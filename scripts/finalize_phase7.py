"""Verify the glyph overlay, numeric diagnostics and delayed-feedback checkpoint."""
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
from attack_support import to_indices
from external_language import external_model
from liberprimus.numeric import encode_pair
from PIL import Image

def load(path):return json.loads((ROOT/path).read_text(encoding='utf-8'))
def sha(path):return hashlib.sha256((ROOT/path).read_bytes()).hexdigest()
def save(path,data):(ROOT/path).write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')

def main():
    if (ROOT/'checkpoints/phase8_complete.json').exists():
        raise RuntimeError('Newer phase8 checkpoint exists; refuse historical state overwrite')
    if (ROOT/'checkpoints/phase8_complete.json').exists():
        raise RuntimeError('Newer checkpoint exists; refuse historical state overwrite')
    completed=load('checkpoints/phase7_feedback_complete.json')
    selection=load('experiments/periodic_feedback_selection.json')
    assert sha('experiments/periodic_feedback_selection.json')==completed['selection_sha256']
    tests=subprocess.run([sys.executable,'-m','unittest','discover','-s','tests','-v'],
                         cwd=ROOT,capture_output=True,text=True,encoding='utf-8',timeout=60)
    output=tests.stdout+tests.stderr
    (ROOT/'results/validation_phase7.txt').write_text(output,encoding='utf-8')
    if tests.returncode:raise RuntimeError(output)
    count=int(re.search(r'Ran (\d+) tests',output).group(1));now=datetime.now(timezone.utc).isoformat()
    events=[json.loads(line) for line in (ROOT/'experiment_log.jsonl').read_text(encoding='utf-8').splitlines()]
    done=[e for e in events if e.get('status')=='completed']
    latest={e['experiment']:e for e in done}
    phase={k:e for k,e in latest.items() if k.startswith(('E023','E024','E025'))}
    assert len(phase)==77
    for e in phase.values():
        assert sha(e['output'])==e['output_sha256']
        for path,digest in e['input_dependencies'].items():assert sha(path)==digest,path
    data={k:load(e['output']) for k,e in phase.items()}
    glyph=data['E023-glyph-audit'];numeric=data['E024-numeric-structure']
    for crop in load('sources/glyph_crop_manifest.json')['crops']:
        with Image.open(ROOT/crop['image_path']) as source, Image.open(ROOT/crop['crop_path']) as saved:
            expected=source.crop(crop['box'])
            assert expected.size==saved.size and expected.mode==saved.mode
            assert expected.tobytes()==saved.tobytes(),crop['crop_path']
    cells=glyph['cells'];payload=bytes(c['value'] for c in cells)
    assert len(payload)==256 and payload.hex()==glyph['byte_hex']
    assert hashlib.sha256(payload).hexdigest()==glyph['byte_sha256']==numeric['input_byte_sha256']
    for cell in cells:
        assert encode_pair(cell['value'])==cell['token']
    pairs=sum(payload[i]==payload[j] for i in range(256) for j in range(i))
    assert pairs==numeric['descriptive']['equal_unordered_pairs']
    assert numeric['controls_passed']==4
    assert glyph['image_supported_cells']==5 and glyph['canonical_changed'] is False
    canonical={p['id']:p for p in load('transcriptions/pages.json')}
    controls=data['E025-controls'];assert controls['gate_passed'] and len(controls['controls'])==3
    fixtures={f['id']:f for f in load('known_solutions/fixtures.json')}
    model=external_model(4);verified=0
    def verify(row,cipher):
        nonlocal verified
        plain=to_indices(row['plaintext_runes']);r=row['recipe']
        assert r['delay']==2 and len(r['initial_key'])==2
        # Independent algebraic reencryption, no call into the new feedback module.
        for i,(p,c) in enumerate(zip(plain,cipher)):
            previous=plain[i-2] if i>=2 else r['initial_key'][i]
            assert (p-r['b']*previous)*pow(r['a'],-1,29)%29==c
        assert len(plain)==len(cipher)
        scalar=model.score(plain)
        assert abs(scalar-row['score'])<1e-9,(scalar,row['score'])
        verified+=1
    for control in controls['controls']:
        assert control['exact'] and control['top'][0]['plaintext_runes']==fixtures[control['fixture']]['plaintext_runes']
        for row in control['top']:verify(row,control['ciphertext_indices'])
    pages=[p for k,item in data.items() if k.startswith('E025-pages-') for p in item['pages']]
    assert len(pages)==55 and len({p['page'] for p in pages})==55
    for p in pages:
        assert p['ciphertext_runes']==canonical[p['page']]['runes'] and p['recipes']==655980
        for row in p['top']:verify(row,to_indices(p['ciphertext_runes']))
    winner=max(pages,key=lambda p:p['top'][0]['score'])
    assert winner['page']==selection['selected_page']==completed['selected']
    assert winner['top'][0]['score']==selection['observed_score']
    for path,digest in selection['page_outputs'].items():assert sha(path)==digest
    nulls=[p for k,item in data.items() if k.startswith('E025-null-') for p in item['pages']]
    assert len(nulls)==19
    cipher=to_indices(canonical[winner['page']]['runes'])
    equal=lambda a:sum(x==y for x,y in zip(a,a[1:]))
    for row in nulls:
        assert row['page']==winner['page'] and row['recipes']==655980
        assert Counter(row['ciphertext_indices'])==Counter(cipher)
        assert equal(row['ciphertext_indices'])==equal(cipher)
    exceed=sum(row['score']>=winner['top'][0]['score'] for row in nulls);p=(1+exceed)/20
    assert exceed==completed['exceedances'] and p==completed['raw_p']
    elapsed=sum(e['wall_seconds'] for e in phase.values())
    feedback_seconds=sum(e['wall_seconds'] for k,e in phase.items() if k.startswith('E025'))
    assert feedback_seconds<650 and elapsed<900
    assert all(e['wall_seconds']<180 for e in phase.values())
    summary={'created_at':now,'image_supported_cells':5,'inspected_crops':16,
        'numeric_byte_sha256':glyph['byte_sha256'],'numeric_rejected_statistics':numeric['rejected_at_familywise_005'],
        'numeric_controls_passed':4,'feedback_pages':55,'feedback_recipes':55*655980,
        'feedback_exact_controls':3,'selected_page':winner['page'],'top':winner['top'][0],
        'raw_p':p,'page_adjusted_p':min(1,55*p),'null_exceedances':exceed,'null_replicates':19,
        'pending_larger_calibration':exceed==0,'candidate_records_recomputed':verified,
        'tests_passed':count,'new_completed_processes':len(phase),'seconds':elapsed,
        'feedback_seconds':feedback_seconds,'feedback_orchestration_seconds':completed['seconds'],
        'phase_budget_seconds':900,'period3_searched':False,'new_decryptions':[]}
    save('results/phase7_summary.json',summary)
    entries=[{'id':k,'fingerprint':e['fingerprint'],'output':e['output'],'sha256':e['output_sha256']} for k,e in phase.items()]
    save('checkpoints/phase7_complete.json',{'created_at':now,'status':'seventh_batch_complete_no_new_decryption',
        'summary':'results/phase7_summary.json','summary_sha256':sha('results/phase7_summary.json'),'experiments':entries})
    state=load('research_state.json');known={e['fingerprint'] for e in state['completed_experiments']}
    state['completed_experiments'] += [e for e in entries if e['fingerprint'] not in known]
    state.update(status='seventh_batch_complete_no_new_decryption' if exceed else 'seventh_batch_candidate_requires_larger_null',updated_at=now,
        latest_report='reports/attack_phase7_report.md',next_experiments=([] if exceed else ['E025-larger-null'])+['H026','H023','H018'],
        promising_candidates=[] if exceed else [{'page':winner['page'],'status':'uncalibrated_screen_maximum','source':'results/phase7_summary.json'}],
        session_budget={'phase':'seventh bounded glyph/numeric/feedback queue','max_compute_wall_seconds':900,
                        'max_experiment_wall_seconds':180,'workers':1,'background_jobs':False},
        validation={'tests_passed':count,'path':'results/validation_phase7.txt','phase7_candidate_records_recomputed':verified},
        notes=['No previously unknown plaintext confirmed.',
               'Five disputed table cells have image-supported readings in an explicit overlay; old canonical file unchanged.',
               'No full independent transcription of all256 cells or second-reader image review claimed.',
               'Four byte diagnostics are limited tests against IID uniform bytes, not evidence of encryption.',
               'Period2 affine feedback completed; period3 remains unsearched.','No research process remains running.'])
    state['resources'].update(recorded_successful_experiment_runs=len(done),
        recorded_experiment_subprocess_wall_seconds=sum(e['wall_seconds'] for e in done),phase7_wall_seconds=elapsed)
    message=f'E025 full period2 grid on55pages: {winner["page"]} null p={p}, Bonferroni55={min(1,55*p)}; no supported decryption.'
    if message not in state['failed_approaches']:state['failed_approaches'].append(message)
    save('research_state.json',state)
    hypotheses=load('hypotheses.json')
    for h in hypotheses['hypotheses']:
        if h['id']=='H024':h.update(experiments=['E022','E023'],status='five_conflicts_image_supported_overlay_preserved',
            result={'image_supported_cells':5,'unresolved_among_original_five':0,'inspected_crops':16},
            limits='Single visual reader, five disputed cells only. No full independent table transcription or decryption; old source variants retained.')
    for h in [
        {'id':'H025','claim':'The source-aligned256-byte stream departs from IID uniform bytes under four fixed diagnostics.',
         'experiments':['E024'],'status':'limited_diagnostics_complete','result':numeric['calibration']['observed'],
         'limits':'No rejection does not prove randomness or encryption; no cipher or key inferred.'},
        {'id':'H023','claim':'General affine plaintext feedback with delay2 or3 can expose an unknown page.',
         'experiments':['E025'],'status':'period2_complete_period3_deferred','result':summary,
         'limits':'Only period2, no F skips or additive constant; period3 has29 times as many recipes and was not searched.'}]:
        hypotheses['hypotheses']=[old for old in hypotheses['hypotheses'] if old['id']!=h['id']]+[h]
    hypotheses['next_queue']=[
        {'id':'H026','priority':1,'task':'Audit retained word boundaries and benchmark an externally trained boundary-aware score on known solutions and matched controls before any new unknown-key search.','gate':'No fitting to the best unknown candidates; preserve exact source separators.'},
        {'id':'H023','priority':2,'task':'Use measured period2 cost to design a bounded period3 strategy; exact control recovery and a feasible full-null budget required.'},
        {'id':'H018','priority':3,'task':'Use concrete source clues to justify additional text keys or interpretations of numeric data.'}]
    if not exceed:
        hypotheses['next_queue'].insert(0,{'id':'E025-larger-null','priority':0,
            'task':'Freeze the E025 candidate; preregister and budget a larger independent null calibration before any significance claim.'})
    hypotheses['updated_at']=now;save('hypotheses.json',hypotheses)
    statistic_rows='\n'.join(f'| {name} | {row["raw_p"]:.4f} | {row["adjusted_p"]:.4f} |' for name,row in numeric['calibration']['observed'].items())
    report=f'''# Siebte Forschungsserie: Glyphenprüfung, Zahlentabellen und Rückkopplung

Stand (UTC): {now}. **Keine neue Entschlüsselung bestätigt.**

## E023: Fünf Quellenkonflikte am Bild geprüft

16 unvergrößerte Ausschnitte aus den gepinnten Bildern liefern Vergleichszeichen.
Die fünf strittigen Zellen stützen folgende Lesarten:

| Seite | Zeile, Spalte (ab 1) | Bildgestützte Lesart | Base60-Wert |
|---|---|---|---|
| LP2-49 | 6,6 | `1l` | 107 |
| LP2-49 | 7,3 | `0l` | 47 |
| LP2-50 | 11,6 | `0I` | 18 |
| LP2-50 | 12,5 | `2S` | 148 |
| LP2-51 | 8,7 | `3I` | 198 |

Kleines `l` hat in den geprüften Ausschnitten 73–74 Pixel Höhe, großes `I` 67.
Großes `L` besitzt einen Fuß; kleines `i` einen getrennten Punkt. Das strittige
`S` hat 69–71 Pixel Höhe, das Vergleichs-`s` 44–45. Messungen bei drei
Helligkeitsschwellen (32/128/224) stützen den visuellen Vergleich. Die Schwellen
wurden nach der ersten Bildansicht als Empfindlichkeitsprüfung festgelegt;
dies ist kein vorab validierter automatischer Zeichenerkenner.

![Unveränderte Bildausschnitte mit Beschriftungen](../sources/glyph_crops/contact_sheet.png)

[Koordinaten und Prüfsummen](../sources/glyph_crop_manifest.json),
[Beobachtungen](../sources/glyph_observations.json). Die Ausschnitte wurden nicht
resampelt oder nachgeschärft. Quellenbilder und kanonische Transkription bleiben
unverändert. Die separate Korrekturschicht ergibt dieselben Tokens wie die schon
vorhandene iddqd-Transkription; dies ist eine Quellenprüfung, keine neue Entzifferung.
Alle historischen Alternativen bleiben erhalten. Ein einzelner visueller Leser,
keine zweite unabhängige Bildlesung und keine vollständige Neutranskription aller
256 Zellen. Die neun E022-Dezimalinkonsistenzen bleiben als historischer Befund bestehen.

## E024: Begrenzte Strukturprüfung der 256 Werte

Base60 bleibt replizierte Vorarbeit. Die explizite Reihenfolge lautet LP2-49,
LP2-50, LP2-51, jeweils zeilenweise von links nach rechts. Jede Zahl ist mit
Seite, Zeile, Spalte und Token zurückverfolgbar und reversibel kodiert.
Bytefolge SHA-256: `{glyph['byte_sha256']}`.

161 verschiedene Werte, 127 gleiche ungeordnete Wertepaare, keine gleichen
Nachbarwerte. Die empirische Entropie beträgt {numeric['descriptive']['empirical_entropy_bits']:.6f} Bit;
dieser endliche Stichprobenschätzer ist kein Test kryptographischer Zufälligkeit.

Vier vorab festgelegte Statistiken wurden mit 9.999 IID-gleichverteilten Bytefolgen
verglichen (Seed 3301024). Alle vier Statistiken werden in jedem Zufallslauf
berechnet; Bonferroni-Faktor 4, Bitmaximum bereits innerhalb jedes Laufs ausgewählt.

| Statistik | Roh-p | Korrigiertes p |
|---|---|---|
{statistic_rows}

Die vier vorgesehenen positiven Kontrollprüfungen bestehen. Keine auffällige
Abweichung in diesen Tests; daraus folgt weder Verschlüsselung noch Zufälligkeit,
Dateityp oder Schlüssel. Keine Statistik auf den unbekannten Daten nachoptimiert.

## E025: Affine Klartext-Rückkopplung mit Abstand zwei

Regel: `P_i = a*C_i + b*P_(i-2) mod 29`, mit zwei freien Anfangswerten.
Alle a,b von 1 bis 28, ohne vier schon in E014 geprüfte Vorzeichenpaare;
alle 29² Anfangswerte. **655.980 Regeln pro Seite**, zusammen **{55*655980:,}**
auf allen 55 unbekannten Runenseiten. Kein F-Auslassen, kein additiver Offset,
keine Umordnung und kein Schlüsselübergang zwischen Seiten. LP2-50 bleibt
als Zahlenseite erhalten und ist kein Runeninput dieser Hypothese.

Für jede Restklasse r wird mit dem Anfangsklartext x_r statt dem Schlüssel
parametrisiert: `S_r=0`, `q_r=1`, anschließend `S_i=C_i+b*S_(i-2)` und
`q_i=b*q_(i-2)`. Dann `P_i=a*S_i+q_i*x_r`; der eindeutige Anfangsschlüssel
ist `b^-1*(x_r-a*C_r) mod29`. Die Parametrisierung ist bijektiv, kein Heuristikverlust.
Nur 2.048 Kandidaten gleichzeitig; fester externer Viergramm-Score.

Drei synthetisch verschlüsselte bekannte Texte werden unter dem vollständigen
Raster exakt als beste Ergebnisse gefunden. Diese bekannten Kontrolltexte sind
keine blinde historische Validierung. Der stärkste unbekannte Kandidat stammt
von {winner['page']} (Score {winner['top'][0]['score']:.6f}):

```text
{winner['top'][0]['transliteration']}
```

{exceed} von 19 Nulltexten erreichen mindestens diesen Score. Roh-p={p:.3f},
seitenkorrigiert {min(1,55*p):.3f}. Die Nulltexte erhalten Runenhäufigkeiten und
gleiche Nachbarpaare; jeder durchläuft dasselbe vollständige Raster. Alle
Seitenergebnisse wurden vor den Nulltests eingefroren. 19 Replikate könnten
korrigierte Signifikanz nicht auflösen; bei null Überschreitungen wäre eine
größere vorab festgelegte Prüfung erforderlich. Keine neue Lösung bestätigt.

Abstand drei wurde mathematisch vorbereitet, **nicht durchsucht**: 19.023.420
Regeln pro Seite, also 29-mal die Kandidatenzahl. Eine entsprechende Laufzeit
wäre eine Extrapolation; die Bewertung muss vor einem größeren Lauf geprüft werden.

## Validierung und Fortsetzung

{count} Tests bestanden. {verified} gespeicherte Kandidaten wurden unabhängig
mit skalarer Algebra zurückverschlüsselt und mit dem skalaren Sprachmodell
nachbewertet. Hashes sämtlicher neuer Ergebnisse und Abhängigkeiten stimmen.
{len(phase)} abgeschlossene Aufgaben, {elapsed:.3f} Sekunden protokollierte
Experimentzeit; davon {feedback_seconds:.3f} für E025, innerhalb dessen
650-Sekunden-Grenze und der 900-Sekunden-Phasengrenze. Keine Hintergrundaufgabe.

Als Nächstes: Die bisher ungenutzten Wortgrenzen quellengetreu prüfen und einen
extern trainierten Wortgrenzen-Score an Kontrollfällen bewerten. Abstand drei
bleibt eine getrennte, vorab zu budgetierende Suche. Weitere Textschlüssel und
Zahleninterpretationen benötigen konkrete Quellenhinweise.

[Checkpoint](../checkpoints/phase7_complete.json), [Übersicht](../results/phase7_summary.json).
'''
    (ROOT/'reports/attack_phase7_report.md').write_text(report,encoding='utf-8')
    print(json.dumps(summary,ensure_ascii=True))

if __name__=='__main__':main()
