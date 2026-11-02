"""Validate continuation and affine feedback without rewriting historical reports."""
from collections import Counter
from datetime import datetime,timezone
import hashlib
import json
from pathlib import Path
import re
import subprocess
import sys
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'experiments'))
from attack_support import to_indices,stream_catalog
from external_language import external_model

def load(p):return json.loads((ROOT/p).read_text(encoding='utf-8'))
def sha(p):return hashlib.sha256((ROOT/p).read_bytes()).hexdigest()
def save(p,obj):(ROOT/p).write_text(json.dumps(obj,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')

def main():
    if (ROOT/'checkpoints/phase6_complete.json').exists():
        raise RuntimeError('Historical finalizer: phase6 checkpoint already exists')
    check=subprocess.run([sys.executable,'-m','unittest','discover','-s','tests','-v'],cwd=ROOT,capture_output=True,text=True,encoding='utf-8',timeout=60)
    text=check.stdout+check.stderr;(ROOT/'results/validation_phase5.txt').write_text(text,encoding='utf-8')
    if check.returncode:raise RuntimeError(text)
    tests=int(re.search(r'Ran (\d+) tests',text).group(1));now=datetime.now(timezone.utc).isoformat()
    events=[json.loads(s) for s in (ROOT/'experiment_log.jsonl').read_text(encoding='utf-8').splitlines()]
    completed=[e for e in events if e.get('status')=='completed'];latest={e['experiment']:e for e in completed}
    relevant={k:e for k,e in latest.items() if k.startswith(('E018','E019','E020'))}
    baseline={e['fingerprint'] for e in load('checkpoints/phase4_complete.json')['experiments']}
    phase=[e for e in relevant.values() if e['fingerprint'] not in baseline]
    for e in relevant.values():
        assert sha(e['output'])==e['output_sha256'],e['output']
        for path,digest in e['input_dependencies'].items():assert sha(path)==digest,path
    data={k:load(e['output']) for k,e in relevant.items()}
    model=external_model(4);canonical={p['id']:p for p in load('transcriptions/pages.json')}
    fixtures={f['id']:f for f in load('known_solutions/fixtures.json')};verified=0
    def verify(row,cipher,feedback):
        nonlocal verified
        plain=to_indices(row['plaintext_runes']);r=row['recipe'];assert len(plain)==len(cipher)
        output=[]
        if feedback:
            previous=r['initial_key'];inverse=pow(r['a'],-1,29)
            for p in plain:output.append(inverse*(p-r['b']*previous)%29);previous=p
            assert (r['a'],r['b']) not in ((1,1),(1,28),(28,1),(28,28))
        else:
            key=r.get('key_indices') or stream_catalog(len(cipher)+256)[r['family']]
            cursor=r['start'];skips=set(r['skip_positions'])
            for i,p in enumerate(plain):
                if i in skips:assert p==0;output.append(0)
                else:
                    k=key[cursor%len(key)] if r['family']=='vigenere' else key[cursor]
                    output.append(r['cipher_sign']*(p-r['key_sign']*k)%29);cursor+=1
        assert output==cipher
        assert abs(model.score(plain)-row['score'])<1e-10
        verified+=1
    families={}
    for family in ('E018','E019'):
        control=data[family+'-controls']
        for c in control['controls']:
            cipher=c.get('ciphertext_indices') or to_indices(fixtures[c['fixture']]['ciphertext_runes'])
            for row in c['top']:verify(row,cipher,family=='E019')
            assert c['exact']==(c['top'][0]['plaintext_runes']==fixtures[c['fixture']]['plaintext_runes'])
        if not control['gate_passed']:
            assert family=='E019' and not any(k.startswith('E019-pages') for k in data)
            families[family]={'status':'control_gate_failed','exact_controls':sum(c['exact'] for c in control['controls'])};continue
        pages=[];nulls=[]
        for ident,result in data.items():
            if not ident.startswith(family) or ident.endswith('controls'):continue
            if '-pages-' in ident:pages+=result['pages']
            if 'null_calibration' in result:nulls.append(result)
            for page in result['pages']:
                assert page['ciphertext_runes']==canonical[page['page']]['runes']
                for row in page['top']:verify(row,to_indices(page['ciphertext_runes']),family=='E019')
        assert len(pages)==55 and len({p['page'] for p in pages})==55 and len(nulls)==1
        winner=max(pages,key=lambda p:p['top'][0]['score']);null=nulls[0]
        assert null['pages'][0]['page']==winner['page']
        cal=null['null_calibration'];values=to_indices(winner['ciphertext_runes']);doublets=lambda v:sum(a==b for a,b in zip(v,v[1:]))
        assert len(cal['runs'])==19
        for r in cal['runs']:
            assert Counter(r['ciphertext_indices'])==Counter(values)
            assert doublets(r['ciphertext_indices'])==doublets(values)
        exceed=sum(r['score']>=winner['top'][0]['score'] for r in cal['runs']);p=(1+exceed)/20
        assert p==cal['monte_carlo_p'] and min(1,55*p)==cal['bonferroni_55_pages']
        families[family]={'status':'screen_complete','pages':55,'exact_controls':sum(c['exact'] for c in control['controls']),
            'selected':winner['page'],'top':winner['top'][0],'exceedances':exceed,'replicates':19,
            'raw_p':p,'page_adjusted_p':min(1,55*p),'phase_adjusted_p':min(1,110*p)}
    confirmation=[r for name,r in data.items() if name.startswith('E020-null-batch-')]
    assert len(confirmation)==20 and {r['batch'] for r in confirmation}==set(range(20))
    frozen=families['E019'];observed=frozen['top']['score']
    values=to_indices(canonical[frozen['selected']]['runes']);indices=set();exceedances=0
    for batch in confirmation:
        assert batch['page']==frozen['selected'] and batch['observed_score']==observed
        assert len(batch['runs'])==200
        count=0
        for row in batch['runs']:
            assert row['index'] not in indices;indices.add(row['index'])
            assert Counter(row['ciphertext_indices'])==Counter(values)
            assert sum(a==b for a,b in zip(row['ciphertext_indices'],row['ciphertext_indices'][1:]))==sum(a==b for a,b in zip(values,values[1:]))
            assert row['recipes']==22620
            count+=row['score']>=observed
        assert count==batch['exceedances'];exceedances+=count
    assert indices==set(range(4000))
    p=(1+exceedances)/4001
    frozen.update(initial_raw_p=frozen['raw_p'],initial_exceedances=frozen['exceedances'],initial_replicates=19,
        raw_p=p,page_adjusted_p=min(1,55*p),phase_adjusted_p=min(1,110*p),replicates=4000,exceedances=exceedances,
        calibration='E020 fresh fixed4000-replicate follow-up; initial19 excluded from inference')
    if frozen['phase_adjusted_p']<=0.05:
        raise RuntimeError('Corrected signal: preserve output and perform independent validation before negative-result finalization')
    seconds=sum(e['wall_seconds'] for e in phase);assert seconds<=900
    assert all(e['wall_seconds']<=180 for e in phase)
    summary={'created_at':now,'families':families,'completed_new_processes':len(phase),'new_experiment_seconds':seconds,
        'max_process_seconds':max(e['wall_seconds'] for e in phase),'budget_seconds':900,
        'candidate_records_recomputed':verified,'tests_passed':tests,'new_decryptions':[],
        'resume_note':'Eight E018 completed tasks reused; interrupted LP2-35_39 recomputed; earlier phase4 budget/report remain historical.',
        'orchestration_seconds':{name:load('checkpoints/phase5_'+name+'.json')['seconds'] for name in ('selective','feedback','confirmation')}}
    assert sum(summary['orchestration_seconds'].values())<=900
    save('results/phase5_summary.json',summary)
    state=load('research_state.json')
    state.update(status='fifth_batch_complete_no_new_decryption',updated_at=now,latest_report='reports/attack_phase5_report.md',
        scoring_gate='External4gram passes the three previously seen selective-F controls; no automatic classification of unknown plaintext.',
        completed_experiments=[{'id':e['experiment'],'fingerprint':e['fingerprint'],'output':e['output'],'sha256':e['output_sha256']} for e in latest.values()],
        validation={'tests_passed':tests,'path':'results/validation_phase5.txt','phase5_candidate_records_recomputed':verified},
        session_budget={'phase':'fifth bounded continuation and feedback queue','max_compute_wall_seconds':900,'max_experiment_wall_seconds':180,'workers':1,'background_jobs':False},
        next_experiments=['H021','H018','H023'],new_decryptions=[],promising_candidates=[],
        notes=['Primary decryption objective unresolved.','E018 continuation complete; all55 pages and conditional null evaluated.','External model controls passed, but no new historical decryption.','No running research processes.'])
    state['resources'].update(recorded_successful_experiment_runs=len(completed),recorded_experiment_subprocess_wall_seconds=sum(e['wall_seconds'] for e in completed),phase5_wall_seconds=seconds,phase5_orchestration_seconds=summary['orchestration_seconds'])
    for family,v in families.items():
        if v['status']=='screen_complete':
            note=f"{family}: {v['selected']} selected, raw conditional p={v['raw_p']}, page-adjusted={v['page_adjusted_p']}; no supported candidate."
            if note not in state['failed_approaches']:state['failed_approaches'].append(note)
    save('research_state.json',state)
    h=load('hypotheses.json')
    for item in h['hypotheses']:
        if item['id']=='H019':item.update(status='bounded_screen_no_supported_candidate',result=families['E018'],limits='Changed-score rescan of E007/E008, complete finite grid with exact F-subset optimization; no arbitrary keys or cross-page continuation.')
    if not any(x['id']=='H020' for x in h['hypotheses']):
        h['hypotheses'].append({'id':'H020','claim':'A one-rune plaintext feedback with general invertible multipliers recovers an unknown page.','experiments':['E019','E020'],
            'status':families['E019']['status'],'result':families['E019'],'limits':'Only seed length1, no additive constant or skips; four old sign pairs excluded. No broad family elimination.'})
    h.update(updated_at=now,status='Fifth bounded queue complete; no new decryption.',next_queue=[
        {'id':'H021','priority':1,'task':'Audit source image/layout correspondence, then test a small fixed set of alternate reading orders with known-cipher controls.','gate':'Image hashes/coordinates and line boundaries before scoring; correct across orders; preserve numeric LP2-50.'},
        {'id':'H018','priority':2,'task':'Review concrete manuscript clues for a narrowly justified text-key extension.','gate':'Separate source evidence from thematic speculation; fix text/encoding before searching.'},
        {'id':'H023','priority':3,'task':'Assess whether general feedback of periods2..3 can be searched under a strict new budget.','gate':'Derive equivalences and estimate exact complexity first; synthetic control gate before unknown pages.'}])
    save('hypotheses.json',h)
    save('checkpoints/phase5_complete.json',{'created_at':now,'status':state['status'],'summary':'results/phase5_summary.json','summary_sha256':sha('results/phase5_summary.json'),
        'new_experiments':[{'id':e['experiment'],'fingerprint':e['fingerprint'],'output':e['output'],'sha256':e['output_sha256']} for e in phase],
        'tests':tests,'new_decryptions':[],'resume':'Read current state/hypotheses/report; do not recompute completed fingerprints.'})
    a=families['E018'];b=families['E019']
    b_result=(f"Alle 55 Seiten, 1.244.100 vollständige Koeffizienten-/Schlüsselvarianten. "
        f"Stärkste Seite {b['selected']}: {b['exceedances']}/{b['replicates']} neue Nullwerte mindestens ebenso hoch; "
        f"p={b['raw_p']}, seitenkorrigiert {b['page_adjusted_p']}.") if b['status']=='screen_complete' else (
        f"Kontrollschranke nicht bestanden ({b['exact_controls']}/3 exakt); keine unbekannten Seiten durchsucht.")
    report=f'''# Fünfte Forschungsserie: selektive Schlüsselsuche und affine Rückkopplung

Stand (UTC): {now}. **Keine neue Entschlüsselung bestätigt.**
Die in Serie vier begonnene Wort-/Zahlenstromsuche ist einschließlich Nullvergleich
abgeschlossen. Zusätzlich wurde eine vorher festgelegte Erweiterung der
Klartext-Rückkopplung implementiert, kontrolliert und geprüft.

## E018 abgeschlossen

Alle 55 unbekannten Runenseiten wurden mit 381 kanonischen Wortschlüsselzyklen,
allen Phasen, drei Zahlenstromfamilien, Starts 0–255, vier Vorzeichen und
sämtlichen F-Unterbrechungsteilmengen geprüft. Die Optimierung dieser endlichen
Schlüsselräume ist exakt. Das externe Viergramm-Modell stammt unverändert aus
E016; bekannte Kontrollen DIVINITY, CIRCUMFERENCE und LP2-56 bleiben 3/3 exakt.
Das ist eine erneute Prüfung früherer Familien mit verbessertem Score, keine
unabhängige Entdeckung. Quellen und Normalisierung stehen im
[vorherigen Bericht](attack_phase4_report.md).

Acht bereits fertige Aufgaben wurden über ihre Fingerabdrücke übersprungen:
Kontrollen und sieben Seitengruppen. Die früher abgebrochene Gruppe LP2-35–39
wurde neu gerechnet; sie hatte kein vollständiges Ergebnis. Die historischen
Abbruchdaten, Berichte und Checkpoints wurden nicht umgeschrieben.

Die stärkste Seite ist {a['selected']}, Score {a['top']['score']:.6f}.
{a['exceedances']} von 19 Zufallstexten erreichen mindestens denselben Score:
Plus-eins-p={a['raw_p']}, nach Auswahl aus 55 Seiten p={a['page_adjusted_p']}.
Vollständige Kandidatenausgabe, ausdrücklich **kein bestätigter Klartext**:

```text
{a['top']['transliteration']}
```

## E019: zusätzliche Multiplikatoren bei Klartext-Rückkopplung

Geprüfte Regel: P_i = a C_i + b P_(i−1) modulo 29, mit einem unbekannten
Startwert P_(-1)=K. a und b durchlaufen 1–28; K durchläuft 0–28.
Die vier bereits durch E014/E017 abgedeckten Vorzeichenpaare werden ausgespart.
Es verbleiben 780 Koeffizientenpaare und 22.620 Varianten je Seite.
Diese Erweiterung ist mathematisch motiviert; es gibt keinen Quellenbeleg
für einen bestimmten Multiplikator.

Die endliche Suche verwendet P_0=x, S_0=0 und S_i=C_i+b S_(i−1):
P_i=a S_i+b^i x. Der zugehörige Schlüssel ist K=b^(-1)(x−a C_0).
Damit entspricht jeder getestete Anfangsklartext genau einem Startschlüssel.
Diese Umformung erlaubt eine vollständige Vektorsuche; sie wurde gegen eine
unabhängige skalare Enumeration aller Koeffizienten und Schlüssel geprüft.
Alle 780 Paare wurden außerdem mit mehreren Schlüsseln auf Umkehrbarkeit getestet.

Drei synthetische Kontrollen verwenden bekannte, nicht im externen Training
enthaltene LP-Texte: DIVINITY mit (a,b)=(5,11), CIRCUMFERENCE mit (13,7),
LP2-57 mit (28,3). Die Schlüssel stammen aus Seed 3301019. Die Suche erhält
keinen wahren Schlüssel oder Multiplikator. Ergebnis: {b['exact_controls']}/3 exakt.
Die Texte wurden zuvor betrachtet; dies ist keine neue blinde historische Validierung.

{b_result}

## E020: vorgeschriebene Nachprüfung des ersten auffälligen Scores

Im ersten E019-Vergleich lagen 0 von 19 Nullwerten über dem Score von LP2-55.
Der resultierende Rohwert p=0,05 war wegen der Seitenauswahl kein signifikanter
Befund. Gemäß der vorab festgelegten Eskalationsregel wurden Ciphertext,
Kandidat (a=5, b=20, K=13), Score und vollständige Suchroutine eingefroren.

Vor der Nachprüfung wurden 4.000 neue Nulltexte in 20 festen Chargen zu je 200
registriert (Seed 3301020 plus Chargenindex). Es gab keinen frühen Abbruch
und keine Vermischung mit den ersten 19 Nulltexten. Die größere Kalibrierung
verwendet weiterhin die vollständige unveränderte Optimierung je Nulltext;
sie bewertet nicht nur den einmal gefundenen Schlüssel. Ergebnis:
{b['exceedances']} Überschreitungen, frischer Plus-eins-p={b['raw_p']:.6f},
nach 55 Seiten p={b['page_adjusted_p']:.6f}, nach den beiden Angriffsfamilien
p={b['phase_adjusted_p']:.6f}. Dies liefert keinen korrigiert signifikanten Befund.

Die eingefrorene Ausgabe bleibt unverändert und ist kein verständlicher Klartext:

```text
{b['top']['transliteration']}
```

Die Regel enthält keine additive Konstante, keine F-Unterbrechungen, nur einen
Startwert und keinen über Seitengrenzen fortlaufenden Zustand. Negative Resultate
betreffen ausschließlich diesen vollständig angegebenen Raum. Weitergehende
Autokey-Familien werden dadurch nicht ausgeschlossen.

## Zufallsvergleich und Auswahlkorrektur

Die Nulltexte entstehen durch unabhängige Permutationen mit exakten
Runenhäufigkeiten und exakt derselben Anzahl direkt benachbarter gleicher Runen.
Unpassende Permutationen werden verworfen. Jeder akzeptierte Text durchläuft
denselben vollständigen Suchraum wie die ausgewählte Seite. Bonferroni über
55 Seiten berücksichtigt die Seitenauswahl; zusätzlich wird die Auswahl zwischen
E018 und E019 mit Faktor zwei ausgewiesen. Alle Werte stehen in der
[Ergebnisübersicht](../results/phase5_summary.json).
Das Nullmodell bewahrt keine Wortgrenzen oder sonstige höherstufige Struktur.
Die Korrektur gilt für diese Serie, nicht global für alle früheren explorativen
Hypothesen am wiederholt betrachteten Korpus.

19 Nulltexte erlauben keine korrigierte Signifikanz unter 0,05. Diese erste Stufe
prüft Scheinbefunde; E020 führt die vorgeschriebene größere Folgeprüfung aus.
Eine korrekte Rückverschlüsselung allein ist kein Beleg
für echte Sprache. Es wurde kein Klartext durch freie Nachbearbeitung erzeugt.

## Validierung und Fortsetzung

{tests} Tests bestanden; {verified} Kandidatenaufzeichnungen erneut von den
kanonischen Ciphertexten aus zurückverschlüsselt und skalar nachbewertet.
Quell- und Ergebnishashes stimmen mit den registrierten Abhängigkeiten überein.
LP2-50 bleibt als Zahlenseite im Korpus erhalten und wird in diesen Runensuchen
nicht als Eingabetext verwendet.

{len(phase)} neue erfolgreiche Prozesse, {seconds:.3f} Sekunden gemessene
Experimentzeit; längster Prozess {summary['max_process_seconds']:.3f} Sekunden.
Orchestrierung einschließlich Fingerabdruckprüfung:
{sum(summary['orchestration_seconds'].values()):.3f} Sekunden. Neues Serienbudget
900 Sekunden, Einzelgrenze 180 Sekunden, ein Forschungsprozess gleichzeitig.
E019 hält höchstens 812 Kandidatenzeilen gleichzeitig; Modellarray 29^4 und
begrenzter Cache. Keine Hintergrundaufgaben laufen weiter.

[Checkpoint](../checkpoints/phase5_complete.json),
[Forschungsstand](../research_state.json), [Hypothesen](../hypotheses.json),
[append-only Experimentprotokoll](../experiment_log.jsonl).

Die nächste Priorität ist eine gezielte Prüfung der Quellenbilder und
Zeilenstruktur, bevor eine kleine feste Menge alternativer Leserichtungen
getestet wird. Weitere Textschlüssel brauchen konkrete Quellenhinweise.
Längere allgemeine Rückkopplung wird zunächst auf Aufwand und äquivalente
bereits geprüfte Fälle untersucht.
'''
    (ROOT/'reports/attack_phase5_report.md').write_text(report,encoding='utf-8')
    print(json.dumps({k:v for k,v in summary.items() if k!='families'}))

if __name__=='__main__':main()
