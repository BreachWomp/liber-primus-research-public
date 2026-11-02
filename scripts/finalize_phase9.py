"""Independently verify saved outputs, then checkpoint the actual cipher search."""
from collections import Counter,defaultdict
from datetime import datetime,timezone
from functools import lru_cache
import hashlib
import json
import math
from pathlib import Path
import re
import subprocess
import sys

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'experiments'))
from attack_support import to_indices
from heldout_language import corpus,tokenize
from external_language import external_model

def load(path):return json.loads((ROOT/path).read_text(encoding='utf-8'))
def save(path,data):(ROOT/path).write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def sha(path):return hashlib.sha256((ROOT/path).read_bytes()).hexdigest()


def verify_benchmark(result):
    """Rebuild counts and implement probability equations without score methods."""
    plan=result['parameters'];source=corpus()
    train=[r for r in source if r['chapter'] in plan['training_chapters']]
    counts=[Counter(w for r in train for w in r[key]) for key in ('words','joined')]
    totals=[Counter() for _ in range(2)]
    for k in range(2):
        for word,count in counts[k].items():totals[k][len(word)]+=count
    context_counts=defaultdict(Counter)
    for r in train:
        values=[s for w in r['words'] for s in w]
        for i,symbol in enumerate(values):
            for length in range(min(i,3)+1):
                context_counts[tuple(values[i-length:i])][symbol]+=1
    context_totals={c:sum(v.values()) for c,v in context_counts.items()}
    @lru_cache(maxsize=100000)
    def char_log(word):
        score=0.0
        for i,symbol in enumerate(word):
            p=(context_counts[()].get(symbol,0)+.5)/(context_totals[()]+14.5)
            for length in range(1,min(i,3)+1):
                context=word[i-length:i]
                p=(context_counts.get(context,{}).get(symbol,0)+5*p)/(context_totals.get(context,0)+5)
            score+=math.log(p)
        return score
    @lru_cache(maxsize=100000)
    def word_log(word,k):
        return math.log(counts[k].get(word,0)+20*math.exp(char_log(word)))-math.log(totals[k][len(word)]+20)
    def score(values,ends,k,edges):
        total=0.0;begin=0
        for i,end in enumerate(ends):
            word=tuple(values[begin:end])
            total+=char_log(word) if edges and i in (0,len(ends)-1) else word_log(word,k)
            begin=end
        assert begin==len(values)
        return total/len(values)
    original=(ROOT/'data/raw/gutenberg/pg2944.txt').read_bytes().decode('utf-8-sig')
    fixtures={f['id']:f for f in load('known_solutions/fixtures.json')}
    ranges=[r['source_character_range'] for r in train];scored=0
    aggregates=defaultdict(lambda:{'comparisons':0,'wins':[0,0],'ties':[0,0]})
    for row in result['rows']:
        anchor=row['anchor'];condition=row['condition'];values=row['values'];ends=row['segment_ends']
        if row['origin']=='heldout':
            assert row['chapter'] in plan['heldout_chapters']
            a,b=anchor['source_character_range'];assert all(b<=c or a>=d for c,d in ranges)
            words,joined,joins=tokenize(original[a:b])
            if condition!='apostrophe':
                words=words[anchor['word_start']:anchor['word_start']+20]
            expected=[s for w in words for s in w]
            boundaries=[];cursor=0
            for word in words:cursor+=len(word);boundaries.append(cursor)
            if condition=='apostrophe':
                assert anchor['apostrophe_offsets']==joins
                join_bounds=[];cursor=0
                for word in joined:cursor+=len(word);join_bounds.append(cursor)
                assert row['alternate_ends']==join_bounds
        else:
            expected=to_indices(fixtures[anchor['fixture']]['plaintext_runes'])
            controls=load('results/E026-boundary-audit-314198a84563.json')['controls']
            boundaries=next(r['segment_ends'] for r in controls if r['fixture']==anchor['fixture'])
        if condition!='apostrophe':
            left,right=row['clip']
            if condition=='clipped':
                assert 0<left<boundaries[0] and 0<right<boundaries[-1]-boundaries[-2]
                expected=expected[left:len(expected)-right]
                boundaries=[e-left for e in boundaries[:-1]]+[boundaries[-1]-left-right]
            else:assert left==right==0
        assert expected==values and boundaries==ends
        def check(sample,saved):
            nonlocal scored
            want=[score(sample,ends,0,False),
                  score(sample,row['alternate_ends'],1,False) if condition=='apostrophe' else score(sample,ends,0,True)]
            assert all(abs(a-b)<1e-9 for a,b in zip(want,saved))
            scored+=2
        check(values,row['truth_scores'])
        for mutation in row['mutations']:
            pos=mutation['position'];sample=values[:]
            assert 0<=mutation['replacement']<29 and mutation['replacement']!=sample[pos]
            if mutation['region']=='edge':assert pos<ends[0] or pos>=ends[-2]
            if mutation['region']=='interior':assert ends[0]<=pos<ends[-2]
            sample[pos]=mutation['replacement'];check(sample,mutation['scores'])
            for chapter in ('all',row['chapter']):
                key=(row['origin'],condition,mutation['region'],chapter);aggregate=aggregates[key]
                aggregate['comparisons']+=1
                for k in range(2):
                    delta=row['truth_scores'][k]-mutation['scores'][k]
                    aggregate['wins'][k]+=int(delta>1e-12);aggregate['ties'][k]+=int(abs(delta)<=1e-12)
        assert len(row['nulls'])==19
        for null in row['nulls']:
            assert Counter(null['values'])==Counter(values);check(null['values'],null['scores'])
        assert row['null_strict_wins']==[sum(row['truth_scores'][k]>n['scores'][k]+1e-12 for n in row['nulls']) for k in range(2)]
    for row in result['aggregate']:
        actual=aggregates[(row['origin'],row['condition'],row['region'],row['chapter'])]
        assert all(actual[k]==row[k] for k in ('comparisons','wins','ties'))
    assert not result['edge_gate_passed']
    return scored


def main():
    if (ROOT/'checkpoints/phase10_complete.json').exists():raise RuntimeError('Newer checkpoint exists')
    complete=load('checkpoints/phase9_filter_complete.json')
    tests=subprocess.run([sys.executable,'-m','unittest','discover','-s','tests','-v'],cwd=ROOT,capture_output=True,
                         encoding='utf-8',text=True,timeout=60)
    output=tests.stdout+tests.stderr;(ROOT/'results/validation_phase9.txt').write_text(output,encoding='utf-8')
    if tests.returncode:raise RuntimeError(output)
    test_count=int(re.search(r'Ran (\d+) tests',output)[1]);now=datetime.now(timezone.utc).isoformat()
    events=[json.loads(line) for line in (ROOT/'experiment_log.jsonl').read_text(encoding='utf-8').splitlines()]
    done=[e for e in events if e['status']=='completed'];latest={e['experiment']:e for e in done}
    phase={k:e for k,e in latest.items() if k.startswith(('E030','E031','E032','E033'))};assert len(phase)==78
    for e in phase.values():
        assert sha(e['output'])==e['output_sha256']
        for path,digest in e['input_dependencies'].items():assert sha(path)==digest,path
        assert e['wall_seconds']<180
    data={k:load(e['output']) for k,e in phase.items()}
    benchmark=data['E030-fragment-benchmark'];scored=verify_benchmark(benchmark)
    digest_result=data['E031-numeric-digest-comparison'];provenance=data['E032-claim-provenance']
    for variant in digest_result['variants']:
        assert hashlib.sha256(bytes.fromhex(variant['byte_hex'])).hexdigest()==variant['sha256']
    assert provenance['prior_html_byte_equal'] and not any(provenance['named_files_present'].values())
    controls=data['E033-controls'];assert controls['gate_passed']
    fixtures={f['id']:f for f in load('known_solutions/fixtures.json')}
    model=external_model(4);verified=0
    def verify(cipher,row):
        nonlocal verified
        recipe=row['recipe'];plain=to_indices(row['plaintext_runes'])
        assert len(plain)==len(cipher)-2 and recipe['iv']==cipher[:2]
        assert recipe['unrecovered_prefix_runes']==2
        a,b,c,d=[recipe[k] for k in ('a','b','c','d')]
        assert a and c and not(a in (1,28) and c in (1,28) and b==d==0)
        forward=[(a*cipher[i]+b*cipher[i-1]+c*cipher[i-2]+d)%29 for i in range(2,len(cipher))]
        inverse=cipher[:2];inv=pow(a,-1,29)
        for p in plain:inverse.append(inv*(p-b*inverse[-1]-c*inverse[-2]-d)%29)
        assert forward==plain and inverse==cipher
        assert abs(model.score(plain)-row['score'])<1e-9;verified+=1
    for control in controls['controls']:
        assert control['exact'] and control['top'][0]['plaintext_runes']==fixtures[control['fixture']]['plaintext_runes']
        assert control['recipes']==659340
        for row in control['top']:verify(control['ciphertext_indices'],row)
    pages=[r for k,r in data.items() if k.startswith('E033-page-')];assert len(pages)==55
    canonical={p['id']:p for p in load('transcriptions/pages.json')}
    assert {r['page'] for r in pages}=={f'LP2-{n:02}' for n in range(56) if n!=50}
    for page in pages:
        assert page['ciphertext_indices']==to_indices(canonical[page['page']]['runes']) and page['recipes']==659340
        assert page['score']==page['top'][0]['score']
        for row in page['top']:verify(page['ciphertext_indices'],row)
    winner=max(pages,key=lambda r:r['score']);selection=load('experiments/cipher_filter_selection.json')
    assert sha('experiments/cipher_filter_selection.json')==complete['selection_sha256']
    assert winner['page']==selection['selected_page']==complete['selected_page']
    assert winner['score']==selection['observed_score']
    for path,digest in selection['source_outputs'].items():assert sha(path)==digest
    nulls=[r for k,r in data.items() if k.startswith('E033-null-')];assert len(nulls)==19
    doublets=lambda v:sum(a==b for a,b in zip(v,v[1:]));cipher=winner['ciphertext_indices']
    for null in nulls:
        assert Counter(null['ciphertext_indices'])==Counter(cipher)
        assert doublets(null['ciphertext_indices'])==doublets(cipher) and null['recipes']==659340
        assert null['score']==null['top'][0]['score']
        verify(null['ciphertext_indices'],null['top'][0])
    exceed=sum(r['score']>=winner['score'] for r in nulls);p=(exceed+1)/20
    assert exceed==complete['exceedances'] and p==complete['raw_p']
    attack_seconds=sum(e['wall_seconds'] for k,e in phase.items() if k.startswith('E033'))
    seconds=sum(e['wall_seconds'] for e in phase.values());assert attack_seconds<750 and seconds<900
    stats=[r for r in benchmark['aggregate'] if r['chapter']=='all']
    summary={'created_at':now,'selected_page':winner['page'],'top':winner['top'][0],'unknown_pages':55,
        'rules_per_page':659340,'unknown_rules_evaluated':55*659340,'raw_p':p,'bonferroni55':min(1,55*p),
        'null_exceedances':exceed,'null_replicates':19,'pending_larger_calibration':exceed==0,
        'controls_exact':3,'candidate_records_recomputed':verified,'benchmark_scores_recomputed':scored,
        'edge_gate_passed':benchmark['edge_gate_passed'],'benchmark_aggregates':stats,
        'tests_passed':test_count,'successful_tasks':len(phase),'seconds':seconds,'attack_seconds':attack_seconds,
        'provenance_followup':'Deferred at explicit user request: focus direct cryptanalysis; existing source audit retained.',
        'new_decryptions':[]}
    save('results/phase9_summary.json',summary)
    entries=[{'id':k,'fingerprint':e['fingerprint'],'output':e['output'],'sha256':e['output_sha256']} for k,e in phase.items()]
    status='ninth_batch_complete_no_new_decryption' if exceed else 'ninth_batch_candidate_requires_larger_null'
    state=load('research_state.json');known={r['fingerprint'] for r in state['completed_experiments']}
    state['completed_experiments'] += [e for e in entries if e['fingerprint'] not in known]
    queue=([{'id':'E033-larger-null','priority':0,'task':'Freeze E033 winner and preregister larger fresh matched null calibration before any interpretation.'}] if not exceed else [])+[
        {'id':'H023','priority':1,'task':'Direct cryptanalysis: benchmark a bounded new plaintext-feedback family on synthetic controls; budget identical full-search nulls before unknown pages.'},
        {'id':'H018','priority':2,'task':'Use source-anchored clues from the actual Liber Primus pages to constrain keys or routes; prioritize direct solving.'}]
    state.update(status=status,updated_at=now,latest_report='reports/attack_phase9_report.md',
        next_experiments=[r['id'] for r in queue],
        promising_candidates=[] if exceed else [{'page':winner['page'],'status':'screen_maximum_requires_larger_null'}],
        validation={'tests_passed':test_count,'path':'results/validation_phase9.txt','phase9_candidate_records_recomputed':verified,
                    'phase9_benchmark_scores_recomputed':scored},
        session_budget={'phase':'ninth bounded direct cipher-filter queue','max_compute_wall_seconds':900,
                        'max_experiment_wall_seconds':180,'workers':1,'background_jobs':False},
        scoring_gate='E030 blanket edge fallback rejected. E033 uses frozen E016 external4gram, passes3 exact full-grid synthetic controls.',
        notes=['No previously unknown plaintext confirmed.','User explicitly prioritizes direct solving over unproven community solution claims; no further claim audit planned.',
               'E033 covers a finite reversible two-lag ciphertext filter; first2 source runes are IV, not recovered plaintext.',
               'E030 chapter holdout is training exclusion within this benchmark, not historically unseen material.',
               'No canonical or raw historical source modified.','No research process remains running.'])
    state['resources'].update(recorded_successful_experiment_runs=len(done),
        recorded_experiment_subprocess_wall_seconds=sum(e['wall_seconds'] for e in done),phase9_wall_seconds=seconds)
    message=f'E033 two-lag ciphertext filter on55pages: {winner["page"]}, rawp={p}, adjusted={min(1,55*p)}; no supported plaintext.'
    if exceed and message not in state['failed_approaches']:state['failed_approaches'].append(message)
    save('research_state.json',state)
    hypotheses=load('hypotheses.json')
    new=[
      {'id':'H027','claim':'A fixed edge fallback improves fragment scoring without unacceptable loss on complete words.',
       'experiments':['E030'],'status':'blanket_edge_fallback_rejected','result':{'aggregate':stats,'checks':benchmark['edge_gate_checks']},
       'limits':'Paired descriptive diagnostics on3 previously seen external chapters withheld from current training; no statistical discovery or cipher inference.'},
      {'id':'H029','claim':'A reversible two-lag linear ciphertext filter may reveal plaintext.',
       'experiments':['E033'],'status':'finite_screen_complete' if exceed else 'larger_null_required','result':summary,
       'limits':'Synthetic controls; no historical key clue, first2 positions unrecovered, no F-skip/nonlinear search; no broad family exclusion.'}]
    hypotheses['hypotheses']=[r for r in hypotheses['hypotheses'] if r['id'] not in ('H027','H029')]+new
    for row in hypotheses['hypotheses']:
        if row['id']=='H028':
            row.update(status='deferred_by_user_focus_direct_solving',experiments=['E029','E031','E032'],
                       result={'alternate_digest_matches':False,'historical_binary_provenance':'unverified',
                               'snapshot_commit':provenance['pinned_commit'],'further_claim_review':'not scheduled; explicit user direction'})
    hypotheses.update(status=status,updated_at=now,next_queue=queue);save('hypotheses.json',hypotheses)
    table='\n'.join(f"| {r['condition']} / {r['region']} | {r['wins'][0]}/{r['comparisons']} | {r['wins'][1]}/{r['comparisons']} |"
                    for r in stats if r['origin']=='heldout')
    report=f'''# Neunte Forschungsserie: Direkter Angriff mit Geheimtext-Rückkopplung

Stand (UTC): {now}. **Keine neue Entschlüsselung bestätigt.**

## E033: Zwei vorherige Geheimtextrunen als Rückkopplung

Nach ausdrücklicher Nutzerpräzisierung liegt die Priorität auf dem Lösen der
unbekannten Seiten. Weitere Prüfungen unbelegter Community-Lösungsmeldungen sind
nicht eingeplant. Die bereits abgeschlossenen Quellenprüfungen bleiben erhalten.

Neue endliche Familie: `P_(i-2) = a*C_i + b*C_(i-1) + c*C_(i-2) + d mod 29`.
Dabei sind a,c ungleich null; b,d durchlaufen ganz Z29. Vier bereits in E010
enthaltene reine Vorzeichenfälle sind ausgeschlossen. Das ergibt
**659.340 Regeln je Seite, 36.263.700 Regeln auf allen 55 ungelösten Runenseiten.**
LP2-50 bleibt als Zahlenseite erhalten. Die ersten zwei Geheimtextrunen sind
Initialwerte; für diese Positionen wird kein Klartext behauptet. Die inverse Regel
`C_i = a^-1*(P_(i-2)-b*C_(i-1)-c*C_(i-2)-d)` reproduziert den Originaltext exakt.

Der Wiederholungsmangel motiviert Rückkopplungsmodelle, legt diese Formel aber
nicht historisch fest. Keine F-Unterbrechung, Umordnung oder Seitenfortsetzung.
Alle Koeffizienten werden vollständig geprüft; keine heuristische Vorauswahl.
Score: unverändertes externes Viergramm-Modell von E016. Keine Anpassung an
unbekannte Kandidaten. Drei synthetisch verschlüsselte bekannte Texte werden im
gesamten Suchraum jeweils exakt als bestes Ergebnis zurückgewonnen.

Stärkster Suchtreffer: **{winner['page']}**, Score {winner['score']:.6f}.
Unveränderte Transliteration des Suffixes:

```text
{winner['top'][0]['transliteration']}
```

Regel: `{json.dumps(winner['top'][0]['recipe'])}`.
Diese Ausgabe ist ein gespeicherter Suchtreffer, **keine Entschlüsselung**.

Nach eingefrorener Seitenauswahl durchliefen 19 unabhängige Zufallstexte dieselben
659.340 Regeln. Jeder erhält exakt die Runenhäufigkeiten und die Anzahl gleicher
Nachbarpaare der gewählten Seite; identische Behandlung der zwei Anfangspositionen.
**{exceed}/19** erreichen mindestens den beobachteten Score. Plus-eins-p={p:.3f},
Bonferroni über 55 Seiten={min(1,55*p):.3f}. Diese kleine Kalibrierung kann
korrigierte Signifikanz nicht auflösen. Eine größere Prüfung ist
{'erforderlich und vorgemerkt' if not exceed else 'durch diesen Befund nicht begründet'}.

[Vorab festgelegter Plan](../experiments/cipher_filter_plan.json),
[eingefrorene Auswahl](../experiments/cipher_filter_selection.json).

## E030: Bereits begonnene Score-Prüfung abgeschlossen

Beide Sprachmodelle wurden nur auf Emerson-Kapiteln I und III–IX trainiert,
insgesamt {benchmark['training']['training_runes']} Runen. X–XII wurden für diese
Prüfung ausgeschlossen. Frühere Experimente hatten diese Kapitel bereits verwendet;
es ist kein historisch ungesehener Blindtest. 62 Textfenster jeweils vollständig
und beidseitig gekürzt, 23 Apostroph-Absätze, acht bekannte Kontrolltexte
(sechs zusätzlich gekürzt). Insgesamt 6.440 Ein-Runen-Veränderungen und 3.059
häufigkeitserhaltende Zufallsfolgen; alle Ergebnisse beider festen Alternativen
gespeichert. Abhängige Messungen, deskriptiv, kein Signifikanznachweis.

| Bedingung / veränderte Region | Vollständige Wortwertung / getrennte Apostrophe | Zeichenwertung am Rand / verbundene Apostrophe |
|---|---:|---:|
{table}

Die pauschale Randkorrektur steigert bei echten Fragmenten die Trefferquote um
2,82 Prozentpunkte, verschlechtert sie bei vollständigen Randwörtern aber um
2,10 Punkte. Die bekannte Kontrollrate der Alternative beträgt
{100*benchmark['known_control_alternative_win_rate']:.2f} % statt der verlangten
mindestens 95 %. **Vorab festgelegtes Gate verfehlt; keine Übernahme in E033.**
Das Apostrophverbinden liefert nur vier zusätzliche richtige Entscheidungen bei
460 gezielten Veränderungen. Kein hinreichender Grund für eine neue Gesamtsuche.
Beim Verbinden bleiben die pro Teilwort kodierten Runen unverändert.

## Bereits abgeschlossene Quellenprüfungen E031/E032

Fünf vorhandene Lesarten der 256 Tabellenbytes wurden deterministisch verglichen.
Keine entspricht dem behaupteten alternativen Digest. Die aktuelle öffentliche
Projektstruktur wurde am Commit `{provenance['pinned_commit']}` gepinnt;
sie enthält die behauptete Binärdatei und den benannten Analyzer nicht.
Das ist kein Beweis über frühere Dateistände. Herkunft weiterhin ungeklärt.
Die Byte-Vorschauen widersprechen zudem zwei bereits bildgeprüften `3I`-Lesarten
auf LP2-49 r4c2 und LP2-51 r8c7. Kanonische Daten bleiben unverändert.
Diese Nebenuntersuchung wird auf Nutzerwunsch nicht fortgesetzt.

[Gesicherter Quellenstand](../sources/claim_repository_2026-10-20/manifest.json),
[gesicherte Textdateien](../sources/claim_repository_2026-10-20/files_manifest.json).

## Validierung und nächste direkte Angriffe

**{test_count} Tests bestanden.** {verified} Suchkandidaten unabhängig vorwärts
und rückwärts berechnet und mit dem skalaren Sprachmodell nachbewertet.
{scored} E030-Scores aus unabhängig implementierten Wahrscheinlichkeitsformeln
nachgerechnet; Trainingsausschluss, Quellanker, Veränderungen und Nullhäufigkeiten
geprüft. Alle neuen Ergebnis- und Abhängigkeitshashes stimmen.

{len(phase)} abgeschlossene Aufgaben, {seconds:.3f} Sekunden protokollierte
Experimentzeit, davon E033 {attack_seconds:.3f} Sekunden unter der 750-Sekunden-Grenze.
Ein Forschungsprozess, höchstens 180 Sekunden je Aufgabe, Phasengrenze 900 Sekunden.
Kein Hintergrundprozess bleibt aktiv.

Nächste Priorität: {'zunächst die größere E033-Nullkalibrierung; danach ' if not exceed else ''}weitere begrenzte
Klartext-Rückkopplung mit exakt überprüften Kontrollen und vollständigem
Zufallsvergleich. Schlüssel- oder Leserichtungsbeschränkungen sollen sich auf
die tatsächlichen Liber-Primus-Quellen stützen.

[Checkpoint](../checkpoints/phase9_complete.json), [Messübersicht](../results/phase9_summary.json).
'''
    (ROOT/'reports/attack_phase9_report.md').write_text(report,encoding='utf-8')
    save('checkpoints/phase9_complete.json',{'created_at':now,'status':status,'summary':'results/phase9_summary.json',
         'summary_sha256':sha('results/phase9_summary.json'),'experiments':entries})
    print(json.dumps({k:v for k,v in summary.items() if k not in ('top','benchmark_aggregates')},ensure_ascii=True))


if __name__=='__main__':main()
