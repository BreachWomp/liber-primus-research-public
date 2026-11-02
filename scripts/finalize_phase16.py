"""Independent source replay, schedule optimum checks and joint-search checkpoint."""
from collections import Counter
from datetime import datetime,timezone
import hashlib
import json
import math
from pathlib import Path
import random
import re
import subprocess
import sys

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'experiments'))
from attack_support import to_indices,to_runes
from heldout_language import corpus,tokenize
from liberprimus.decoding import BackoffModel

def load(path):return json.loads((ROOT/path).read_text(encoding='utf-8'))
def save(path,value):(ROOT/path).write_text(json.dumps(value,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def sha(path):return hashlib.sha256((ROOT/path).read_bytes()).hexdigest()


def canonical(key):
    for n in range(1,len(key)+1):
        if len(key)%n==0 and key[:n]*(len(key)//n)==key:
            key=key[:n];break
    return min(key[i:]+key[:i] for i in range(len(key)))


def scalar_replay(cipher,key,sign,skips):
    assert sign in (-1,1) and key and all(type(x) is int and 0<=x<29 for x in key)
    assert skips==sorted(set(skips)) and all(0<=i<len(cipher) and cipher[i]==0 for i in skips)
    plain=[];encoded=[];cursor=0
    for i,c in enumerate(cipher):
        if i in skips:plain.append(0);encoded.append(0)
        else:
            p=(sign*c+key[cursor%len(key)])%29;plain.append(p)
            encoded.append(sign*(p-key[cursor%len(key)])%29);cursor+=1
    assert encoded==cipher
    return plain


def schedule_optimum(cipher,key,sign,model):
    """Independent score-only Viterbi, no stored path and no search-module call."""
    states={(phase,()):0.0 for phase in range(len(key))}
    for c in cipher:
        following={}
        for (phase,h),old in states.items():
            options=[((sign*c+key[phase])%29,(phase+1)%len(key))]
            if c==0:options.append((0,phase))
            for symbol,nxt in options:
                index=(nxt,(h+(symbol,))[-3:]);value=old+model.logp(h,symbol)
                if value>following.get(index,-float('inf')):following[index]=value
        states=following
    return max(states.values())/len(cipher)


def reset_replay(cipher,spans,key,sign,skips,phases):
    assert skips==sorted(set(skips)) and all(0<=i<len(cipher) and cipher[i]==0 for i in skips)
    out=[]
    assert len(phases)==len(spans) and all(type(p) is int and 0<=p<len(key) for p in phases)
    first=next(i for i,s in enumerate(spans) if s['end']>s['start']);assert phases[first]==0
    for span,phase in zip(spans,phases):
        a,b=span['start'],span['end']
        assert a==len(out) and (a!=b or phase==0)
        out+=scalar_replay(cipher[a:b],key[phase:]+key[:phase],sign,[i-a for i in skips if a<=i<b])
    assert len(out)==len(cipher)
    return out


def reset_score(plain,spans,model):
    return sum(model.score(plain[s['start']:s['end']])*(s['end']-s['start']) for s in spans if s['end']>s['start'])/len(plain)


def reset_optimum(cipher,spans,key,sign,model):
    return sum(schedule_optimum(cipher[s['start']:s['end']],key,sign,model)*(s['end']-s['start']) for s in spans if s['end']>s['start'])/len(cipher)


def main():
    if (ROOT/'checkpoints/phase17_complete.json').exists():raise RuntimeError('Newer checkpoint exists')
    complete=load('checkpoints/phase16_phases_complete.json')
    tests=subprocess.run([sys.executable,'-m','unittest','discover','-s','tests','-v'],cwd=ROOT,capture_output=True,text=True,encoding='utf-8',timeout=60)
    output=tests.stdout+tests.stderr;(ROOT/'results/validation_phase16.txt').write_text(output,encoding='utf-8')
    if tests.returncode:raise RuntimeError(output)
    count=int(re.search(r'Ran (\d+) tests',output)[1]);now=datetime.now(timezone.utc).isoformat()
    events=[json.loads(line) for line in (ROOT/'experiment_log.jsonl').read_text(encoding='utf-8').splitlines()]
    done=[e for e in events if e['status']=='completed'];latest={e['experiment']:e for e in done}
    phase={k:e for k,e in latest.items() if k.startswith(('E047-','E048-'))};assert len(phase)==30
    for event in phase.values():
        assert sha(event['output'])==event['output_sha256'] and event['wall_seconds']<180
        for path,digest in event['input_dependencies'].items():assert sha(path)==digest,path
    data={k:load(e['output']) for k,e in phase.items()};control=data['E047-page-phase-controls'];assert control['gate_passed']
    rows=corpus();raw=(ROOT/'data/raw/gutenberg/pg2944.txt').read_bytes().decode('utf-8-sig')
    training=[r for r in rows if r['chapter'] in ('I','III','IV','V','VI','VII','VIII','IX')]
    ranges=[r['source_character_range'] for r in training]
    model=BackoffModel([[x for w in tokenize(raw[a:b])[0] for x in w] for a,b in ranges],order=4,alpha=.5,strength=5)
    assert ranges==control['training']['training_source_ranges']
    verified=0;optima=0;seeds_checked=0;traces_checked=0
    def verify_row(cipher,spans,row):
        nonlocal verified
        key=row['key'];assert 1<=len(key)<=16
        assert len(canonical(key))==len(key)
        plain=reset_replay(cipher,spans,key,row['sign'],row['skip_positions'],row['page_phases'])
        language=reset_score(plain,spans,model)
        assert abs(language-row['language_score'])<1e-9
        phase_cost=(sum(s['end']>s['start'] for s in spans)-1)*math.log(len(key))
        assert abs(phase_cost-row['phase_cost'])<1e-12
        score=language-(len(key)*math.log(29)+cipher.count(0)*math.log(2)+phase_cost)/len(cipher)
        assert abs(score-row['score'])<1e-9
        assert 0<=row['rotation']<row['input_period']<=16
        assert 1<=row['dp_max_states']<=8*row['input_period']
        if 'plaintext_runes' in row:assert to_runes(plain)==row['plaintext_runes']
        verified+=1
    def verify_result(cipher,spans,result):
        nonlocal optima,seeds_checked,traces_checked
        intervals=[]
        for span in spans:
            a,b=span['start'],span['end'];start=a
            for i in range(a,b+1):
                if i==b or cipher[i]==0:
                    if i-start>=32:intervals.append((start,i))
                    start=i+1
        intervals=sorted(intervals,key=lambda ab:(-(ab[1]-ab[0]),ab[0]))[:3]
        pages=sorted([(s['start'],s['end']) for s in spans if s['end']>s['start']],key=lambda ab:(-(ab[1]-ab[0]),ab[0]))[:2]
        expected=[('page',[a,min(b,a+1024)]) for a,b in pages]+[('non_F_run',[a,min(b,a+256)]) for a,b in intervals]
        assert [(r['kind'],r['range']) for r in result['source_stats']]==expected
        assert len(result['restarts'])==min(12,result['unique_seed_keys'])
        keys_seen=set();seed_scores=[];finals=[]
        for restart in result['restarts']:
            initial=restart['initial'];a,b=initial['source_range'];source=cipher[a:b]
            assert (initial['source_kind'],[a,b]) in expected
            key=initial['source_key'];policy=initial['source_policy']
            skips=[i for i,x in enumerate(source) if x==0] if policy=='all_F' else []
            if initial['source_kind']=='non_F_run':assert 0 not in source and policy=='oracle'
            plain=scalar_replay(source,key,initial['sign'],skips)
            assert abs(model.score(plain)-len(key)*math.log(29)/len(source)-initial['seed_score'])<1e-9
            assert canonical(key)==initial['key']
            ident=(initial['sign'],tuple(initial['key']));assert ident not in keys_seen;keys_seen.add(ident)
            seed_scores.append(initial['seed_score']);seeds_checked+=1
            trace=restart['trace'];assert 2<=len(trace)<=4
            assert trace[0]['input_period']==len(initial['key'])
            phase0=trace[0]['rotation'];k0=initial['key']
            assert trace[0]['key']==k0[phase0:]+k0[:phase0]
            for row in trace:verify_row(cipher,spans,row)
            assert all(y['score']>=x['score']-1e-9 for x,y in zip(trace,trace[1:]))
            for field,value in trace[-1].items():assert restart['final'][field]==value
            verify_row(cipher,spans,restart['final']);finals.append(restart['final']);traces_checked+=1
        assert seed_scores==sorted(seed_scores,reverse=True)
        ranked=[];seen=set()
        for row in sorted(finals,key=lambda r:r['score'],reverse=True):
            if row['plaintext_runes'] not in seen:
                ranked.append(row);seen.add(row['plaintext_runes'])
        assert result['top']==ranked[:3]
        winner=result['top'][0]
        assert abs(reset_optimum(cipher,spans,winner['key'],winner['sign'],model)-winner['language_score'])<1e-9
        optima+=1
    catalog={p['id']:p for p in load('transcriptions/pages.json')}
    def source_stream(ids,spans):
        assert [s['page_id'] for s in spans]==ids
        out=[]
        for ident,span in zip(ids,spans):
            piece=to_indices(catalog[ident]['runes'])
            assert span=={'page_id':ident,'start':len(out),'end':len(out)+len(piece),
                'runes':len(piece),'source_refs':catalog[ident]['source_refs'],'zero_rune_page':not bool(piece)}
            out+=piece
        return out
    assert len(control['controls'])==3
    rng=random.Random(3301047)
    for j,record in enumerate(control['controls']):
        chapter=('X','XI','XII')[j];limit=(3316,1200,1200)[j];plain=[];source_ranges=[]
        for src in rows:
            if src['chapter']!=chapter:continue
            a,b=src['source_character_range'];assert all(b<=x or a>=y for x,y in ranges)
            piece=[x for w in tokenize(raw[a:b])[0] for x in w];take=min(limit-len(plain),len(piece))
            if take:
                source_ranges.append({'source_character_range':[a,b],'paragraph':src['paragraph'],'runes_consumed':take})
                plain+=piece[:take]
            if len(plain)==limit:break
        assert source_ranges==record['source_ranges'] and to_runes(plain)==record['truth_runes']
        key=[rng.randrange(1,29) for _ in range((5,8,13)[j])];sign=(1,-1,1)[j]
        skips=[i for i,x in enumerate(plain) if x==0][::2];cipher=[]
        phases=[];first=True
        for span in record['page_spans']:
            phase0=0 if span['start']==span['end'] or first else rng.randrange(len(key));phases.append(phase0)
            if span['start']!=span['end']:first=False
            cursor=phase0
            for i in range(span['start'],span['end']):
                if i in skips:cipher.append(0)
                else:cipher.append(sign*(plain[i]-key[cursor%len(key)])%29);cursor+=1
        assert key==record['injected_key'] and sign==record['injected_sign'] and skips==record['injected_skips']
        assert cipher==record['ciphertext_indices'] and phases==record['injected_phases']
        lengths=([len(to_indices(catalog[f'LP2-{i:02}']['runes'])) for i in range(40,56)] if j==0 else [197,263,311,429])
        offset=0
        for k,(span,length) in enumerate(zip(record['page_spans'],lengths)):
            assert span=={'page_id':f'external-{chapter}-{k:02}','start':offset,'end':offset+length,'runes':length,'zero_rune_page':length==0}
            offset+=length
        assert len(record['page_spans'])==len(lengths) and offset==limit
        verify_result(cipher,record['page_spans'],record['result']);top=record['result']['top'][0]
        assert top['plaintext_runes']==record['truth_runes'] and top['key']==key and top['sign']==sign and top['skip_positions']==skips and top['page_phases']==phases
        assert record['exact'] and all(record['checks'].values())
    doublets=lambda v:sum(a==b for a,b in zip(v,v[1:]))
    def verify_null(source,row,seed):
        out=[];records=[]
        for j,span in enumerate(row['page_spans']):
            assert span['start']==len(out);piece=source[span['start']:span['end']]
            if len(piece)<=2:sample=piece[:];proposal=0
            else:
                rng=random.Random(seed+j)
                for proposal in range(1,100001):
                    interior=piece[1:-1];rng.shuffle(interior);sample=piece[:1]+interior+piece[-1:]
                    if doublets(sample)==doublets(piece):break
                else:raise AssertionError('Null replay exhausted')
            assert Counter(sample)==Counter(piece) and doublets(sample)==doublets(piece)
            assert not piece or (sample[0],sample[-1])==(piece[0],piece[-1])
            out+=sample;records.append({'page_id':span['page_id'],'seed':seed+j,'proposals':proposal})
        assert out==row['ciphertext_indices'] and Counter(out)==Counter(source) and doublets(out)==doublets(source)
        assert records==row['page_proposals'];verify_result(out,row['page_spans'],row['result'])
    assert len(control['nulls'])==1
    assert control['nulls'][0]['page_spans']==control['controls'][1]['page_spans']
    verify_null(control['controls'][1]['ciphertext_indices'],control['nulls'][0],3302047)
    groups=load('experiments/section_plan.json')['sections']
    sections=[r for k,r in data.items() if k.startswith('E048-section-')]
    assert len(sections)==10 and {s['section'] for s in sections}=={g['id'] for g in groups}
    for row in sections:
        group=next(g for g in groups if g['id']==row['section']);assert row['group']==group
        assert row['ciphertext_indices']==source_stream(group['page_ids'],row['page_spans'])
        assert row['training']==control['training'] and row['score']==row['result']['top'][0]['score']
        verify_result(row['ciphertext_indices'],row['page_spans'],row['result'])
    winner=max(sections,key=lambda r:r['score']);selection=load('experiments/phase_key_selection.json')
    assert winner['section']==selection['selected_section']==complete['selected_section']
    assert selection['observed_score']==winner['score'] and len(selection['source_outputs'])==11
    assert selection['search_seed']==3303047 and selection['null_seed']==3301048 and selection['replicates']==19
    for path,digest in selection['source_outputs'].items():assert sha(path)==digest
    assert sha('experiments/phase_key_selection.json')==complete['selection_sha256']
    nulls=[r for k,r in data.items() if k.startswith('E048-null-')];assert len(nulls)==19
    for row in nulls:
        assert row['page_spans']==winner['page_spans'] and row['section']==winner['section']
        verify_null(winner['ciphertext_indices'],row,3301048+100*row['parameters']['replicate'])
        assert row['score']==row['result']['top'][0]['score'] and row['training']==control['training']
    exceed=sum(r['score']>=winner['score'] for r in nulls);p=(exceed+1)/20
    assert exceed==complete['exceedances'] and p==complete['raw_p'] and min(1,10*p)==complete['bonferroni10']
    seconds=sum(e['wall_seconds'] for e in phase.values())
    assert seconds<900 and complete['seconds']+complete['prior_seconds']<650
    s={'created_at':now,'selected_section':winner['section'],'top':winner['result']['top'][0],
       'unknown_groups':10,'controls_exact':3,'new_controls':3,'page_spans':winner['page_spans'],
       'raw_p':p,'bonferroni10':min(1,10*p),'null_exceedances':exceed,'null_replicates':19,
       'pending_larger_calibration':exceed==0,'candidate_records_recomputed':verified,
       'seed_records_recomputed':seeds_checked,'restart_traces_checked':traces_checked,
       'independent_schedule_optima':optima,'tests_passed':count,'successful_tasks':len(phase),
       'seconds':seconds,'family_accounted_seconds':complete['seconds']+complete['prior_seconds'],
       'section_scores':[{'section':r['section'],'runes':len(r['ciphertext_indices']),'score':r['score']} for r in sections],
       'new_decryptions':[]}
    save('results/phase16_summary.json',s);finish(s,phase,done,now)


def finish(s,phase,done,now):
    status='sixteenth_batch_complete_no_new_decryption' if s['null_exceedances'] else 'sixteenth_batch_candidate_requires_larger_null'
    entries=[{'id':k,'fingerprint':e['fingerprint'],'output':e['output'],'sha256':e['output_sha256']} for k,e in phase.items()]
    queue=([{'id':'E048-larger-null','priority':0,'task':'Preserve frozen E048 winner and preregister larger fresh full-optimizer null calibration. No claim from zero of19.'}] if not s['null_exceedances'] else [])+[
        {'id':'H038','priority':1,'task':'Probe longer repeating keys (periods17..32), a range not covered by the completed arbitrary-key solvers. First benchmark source-excluded long controls and F-mask recovery under fixed budgets. Unknown attack only if controls pass; use a separately fixed length penalty and fully reoptimized matched nulls. Do not rerun unchanged periods1..16.'},
        {'id':'H031','priority':2,'task':'General substitution deferred until independently justified scoring repair; no control-specific tuning.'},
        {'id':'H023','priority':3,'task':'Delay3 feedback deferred pending a feasible calibrated reduction.'}]
    state=load('research_state.json');known={e['fingerprint'] for e in state['completed_experiments']}
    state['completed_experiments'] += [e for e in entries if e['fingerprint'] not in known]
    state.update(status=status,updated_at=now,latest_report='reports/attack_phase16_report.md',next_experiments=[q['id'] for q in queue],
        promising_candidates=[] if s['null_exceedances'] else [{'section':s['selected_section'],'status':'screen_maximum_requires_larger_null'}],
        validation={'tests_passed':s['tests_passed'],'path':'results/validation_phase16.txt',
            'phase16_candidate_records_recomputed':s['candidate_records_recomputed'],
            'phase16_seed_records_recomputed':s['seed_records_recomputed'],
            'phase16_independent_schedule_optima':s['independent_schedule_optima']},
        session_budget={'phase':'sixteenth bounded shared-key independent-page-phase queue','max_compute_wall_seconds':900,
            'max_experiment_wall_seconds':180,'workers':1,'background_jobs':False},
        scoring_gate='E047 all3 source-excluded controls recover text,key,all page phases and F masks exactly without oracle inputs.',
        notes=['No previously unknown plaintext confirmed.','Direct solving only; no unsupported claim audits.',
            '10 pinned groups tested with shared keys and independently optimized page phases.',
            'Phase cost fixed at (nonempty_pages-1)*ln(primitive_period); first nonempty phase normalized0.',
            'Key search heuristic; page phases and F masks exact conditional on key.',
            'Numeric spans and all source bytes preserved. No research process remains running.'])
    state['resources'].update(recorded_successful_experiment_runs=len(done),
        recorded_experiment_subprocess_wall_seconds=sum(e['wall_seconds'] for e in done),phase16_wall_seconds=s['seconds'])
    message=f'E048 shared keys with independent page phases on10groups: {s["selected_section"]}, rawp={s["raw_p"]}, adjusted={s["bonferroni10"]}; no supported plaintext.'
    if s['null_exceedances'] and message not in state['failed_approaches']:state['failed_approaches'].append(message)
    save('research_state.json',state)
    hypotheses=load('hypotheses.json');old=next(h for h in hypotheses['hypotheses'] if h['id']=='H037')
    old.update(status='bounded_heuristic_screen_complete' if s['null_exceedances'] else 'larger_null_required',experiments=['E047','E048'],result=s,
        parameters='E045 seeds,12keys,periods1..16,all perpage phases/F masks;3shared-coordinate/DP rounds;phase penalty (G-1)ln(m).',
        limits='All3 controls exact; no unknown plaintext validated. Negative bounded heuristic screen does not exclude all repeating keys or different groups.')
    hypotheses['hypotheses']=[h for h in hypotheses['hypotheses'] if h['id']!='H038']+[
        {'id':'H038','claim':'An unknown repeating key may have primitive period17..32, outside the completed arbitrary-key range.',
         'status':'queued','basis':'E038-E048 arbitrary-key solvers cap period at16; their negative findings do not test longer keys. This identifies an untested range, not positive evidence for it.',
         'mechanism':'Modulo29 repeating key with selective F interruptions, initially bounded to long enough streams for identifiable key recovery.',
         'parameters':'Preregister source-excluded controls, exact periods, stream scope,seed strategy,penalty and budgets before any unknown run.',
         'success_criterion':'Long controls recover exact key,text,F masks; unknown candidates survive fully optimized selection-corrected nulls and independent source replay.',
         'rejection_criterion':'Failed control recovery or infeasible calibration blocks escalation. No brute-force exponential key enumeration.',
         'limits':'More key parameters increase overfitting; a working bounded heuristic and matched calibration are prerequisites.'}]
    hypotheses.update(status=status,updated_at=now,next_queue=queue);save('hypotheses.json',hypotheses)
    top=s['top'];scores='\n'.join(f'| {r["section"]} | {r["runes"]} | {r["score"]:.6f} |' for r in s['section_scores'])
    phases='\n'.join(f'| {span["page_id"]} | {phase} |' for span,phase in zip(s['page_spans'],top['page_phases']))
    report=f'''# Sechzehnte Forschungsserie: Gemeinsamer Schlüssel, verschiedene Seitenanfänge

Stand (UTC): {now}. **Keine neue Entschlüsselung bestätigt.**

## Regel und direkter Angriff

E048 untersucht die zehn gepinnten E012-Seitengruppen mit
`P_i=s*C_i+K[(phase_page+j) mod m] mod29`, s=±1. Jede Seite beginnt bei
einer eigenen unbekannten Schlüsselposition. Ein Chiffren-F kann F kopieren,
ohne j zu erhöhen. Schlüssel gemeinsam, Sprachkontext pro Seite neu.
Gruppen bleiben unbestätigte Chiffregrenzen. Alle Quellrunen, Seitenoffsets
und die leere Runenspanne der Zahlenseite LP2-50 bleiben erhalten.

| Gruppe | Runen | Bester penaliserter Score |
|---|---:|---:|
{scores}

Startschlüssel: zwei längste Seiten (maximal 1.024 Runen) und drei längste
F-freie Abschnitte innerhalb einer Seite (32–256 Runen). E038-Suche mit
Perioden 1–16, beiden Vorzeichen und vier Starts; zwölf zyklisch verschiedene
Schlüssel behalten. Exakte seitenweise Suche über alle Phasen und F-Masken,
danach bis zu drei Runden aus sechs gemeinsamen Koordinatendurchläufen
und erneuter Phasen-/Maskenoptimierung. Schlüsselsuche bleibt heuristisch.

Der Schlüssel wird so gedreht, dass die erste nichtleere Seite Phase 0 hat.
Andere Phasen werden entsprechend angepasst; leere Seiten haben Phase 0.
Das entfernt eine redundante globale Drehung. Vor dem Angriff fester Score:
`[sum(page logp4) - m*ln29 - cipherFcount*ln2 - (G-1)*ln(m)]/N`,
mit primitivem Schlüssellänge m und G nichtleeren Seiten. Der Phasenabzug
berechnet die zusätzlich zugelassenen Anfangspositionen; er ist kein Beweis
gegen Überanpassung und ersetzt den Zufallsvergleich nicht.

## Kontrollfähigkeit und Ergebnis

E047 rekonstruiert drei externe Kontrolltexte mit 3.316, 1.200 und 1.200 Runen exakt:
**Klartext, Schlüssel, sämtliche Seitenphasen und F-Unterbrechungen.**
Zufallsschlüssel mit Längen 5, 8, 13, Vorzeichen +1, −1, +1; Seitenphasen zufällig,
erste nichtleere Phase 0. Keine dieser Vorgaben wird dem Solver mitgegeben.
Kontrolltexte aus Emerson X, XI, XII, Training ausschließlich I, III–IX;
Original-Quellbereiche disjunkt. Diese Kapitel waren historisch bereits
bekannt, daher keine Behauptung einer historisch blinden Prüfung.
Ein weiterer vollständiger Kontroll-Nullversuch dient der Diagnose.

Stärkster unbekannter Abschnitt: **{s['selected_section']}**,
Score {top['score']:.6f}, Sprachwertung {top['language_score']:.6f}.
Vorzeichen {top['sign']}, Schlüssel `{top['key']}`.
F-Skips als nullbasierte Runenoffsets im gesamten Abschnitt:
`{top['skip_positions']}`.

| Seite | Anfangsphase |
|---|---:|
{phases}

Rückverschlüsselung: `C_i=s*(P_i-K[(phase_page+j) mod m]) mod29`,
F-Skips unverändert. Ausgabe nur zur Nachprüfbarkeit verkettet:

```text
{top['transliteration']}
```

**Suchausgabe, kein bestätigter Klartext.** Sieger und alle Ergebnis-Prüfsummen
vor Nullgenerierung eingefroren. Pro Seite erhalten die Nulltexte exakte
Runenhäufigkeiten, Randrunen und gleiche Nachbarpaare. Innenpositionen werden
unabhängig gleichverteilt permutiert und bis zur passenden Nachbarpaarzahl
verworfen (maximal 100.000). Jeder Nulltext durchläuft den vollständigen Solver
mit eigener Auswahl von Startabschnitten, Schlüsseln, Phasen und Masken.

**{s['null_exceedances']}/19** erreichen mindestens den beobachteten Score.
Plus-eins-p={s['raw_p']:.3f}; Bonferroni10={s['bonferroni10']:.3f}.
{'Größere frische Kalibrierung erforderlich; noch keine Signifikanzbehauptung.' if not s['null_exceedances'] else 'Kein durch diesen Vergleich gestützter Lösungskandidat.'}
19 Replikate können korrigierte Signifikanz nicht auflösen. Korrektur nur
für diese zehn Gruppen, nicht projektweit. Kein allgemeiner Ausschluss
beliebiger Schlüssel oder Chiffregrenzen.

## Prüfung und Fortsetzung

{s['tests_passed']} Tests bestanden. {s['candidate_records_recomputed']} Kandidatenaufzeichnungen,
{s['seed_records_recomputed']} Starts und {s['restart_traces_checked']} Suchverläufe unabhängig
skalar nachgerechnet, einschließlich Rückverschlüsselung, Phasen und Kosten.
Separater Score-Viterbi reproduziert die bedingten Phasen-/Maskenmaxima
aller {s['independent_schedule_optima']} Suchausgaben. Kleine Tests enumerieren alle Phasen
und Masken vollständig und prüfen die globale Drehungsinvarianz.
Quellbereiche, Zufallsschlüssel, Phasen und alle 20 neuen Nulltexte aus Seeds
reproduziert; Ergebnis- und Abhängigkeitshashes stimmen.

{s['successful_tasks']} Aufgaben, {s['seconds']:.3f} Sekunden erfolgreiche Experimentzeit;
E048 mit Ablaufaufwand {s['family_accounted_seconds']:.3f} Sekunden unter 650.
Phasenbudget 900, maximal 180 je Prozess, ein Worker, 4.096 Runen/16 Seiten.
Keine neuen Fremdquellen, keine Änderungen an Quellen oder historischen Ergebnissen.

Nächste direkte Hypothese: längere periodische Schlüssel mit 17–32 Runen.
Die bisherigen beliebigen Schlüsselsuchen endeten bei 16. Dieser offene
Bereich ist kein positiver Hinweis; vor unbekannten Texten sind längere
Kontrollen, ein begrenzter Solver und Nullkalibrierung innerhalb des Rechenbudgets erforderlich.

[Plan](../experiments/phase_key_unknown_plan.json),
[Auswahl](../experiments/phase_key_selection.json),
[Messübersicht](../results/phase16_summary.json),
[Checkpoint](../checkpoints/phase16_complete.json).
'''
    (ROOT/'reports/attack_phase16_report.md').write_text(report,encoding='utf-8')
    save('checkpoints/phase16_complete.json',{'created_at':now,'status':status,'summary':'results/phase16_summary.json',
        'summary_sha256':sha('results/phase16_summary.json'),'experiments':entries})
    print(json.dumps({k:v for k,v in s.items() if k not in ('top','section_scores','page_spans')},ensure_ascii=True))


if __name__=='__main__':main()


