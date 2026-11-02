"""Validate image-anchored routes and preserve source uncertainties at checkpoint."""
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
    if (ROOT/'checkpoints/phase7_complete.json').exists():
        raise RuntimeError('Newer phase7 checkpoint exists; refuse historical state overwrite')
    tests=subprocess.run([sys.executable,'-m','unittest','discover','-s','tests','-v'],cwd=ROOT,capture_output=True,text=True,encoding='utf-8',timeout=60)
    output=tests.stdout+tests.stderr;(ROOT/'results/validation_phase6.txt').write_text(output,encoding='utf-8')
    if tests.returncode:raise RuntimeError(output)
    count=int(re.search(r'Ran (\d+) tests',output).group(1));now=datetime.now(timezone.utc).isoformat()
    events=[json.loads(s) for s in (ROOT/'experiment_log.jsonl').read_text(encoding='utf-8').splitlines()]
    done=[e for e in events if e.get('status')=='completed'];latest={e['experiment']:e for e in done}
    phase={k:e for k,e in latest.items() if k.startswith(('E021','E022'))}
    assert len(phase)==25
    for e in phase.values():
        assert sha(e['output'])==e['output_sha256']
        for path,digest in e['input_dependencies'].items():assert sha(path)==digest,path
    data={k:load(e['output']) for k,e in phase.items()}
    canonical={p['id']:p for p in load('transcriptions/pages.json')}
    fixtures={f['id']:f for f in load('known_solutions/fixtures.json')};model=external_model(4);verified=0
    def verify(row,stored):
        nonlocal verified
        r=row['recipe'];plain=to_indices(row['plaintext_runes']);indices=r['route']['indices']
        assert sorted(indices)==list(range(len(stored))) and len(plain)==len(stored)
        if r['family']=='affine':decoded_cipher=[pow(r['a'],-1,29)*(v-r['b'])%29 for v in plain]
        else:
            key=r.get('key_indices') or stream_catalog(len(stored)+256)[r['family']]
            cursor=r['start'];skip=set(r['skip_positions']);decoded_cipher=[]
            for i,v in enumerate(plain):
                if i in skip:assert v==0;decoded_cipher.append(0)
                else:
                    kval=key[cursor%len(key)] if r['family']=='vigenere' else key[cursor]
                    decoded_cipher.append(r['cipher_sign']*(v-r['key_sign']*kval)%29);cursor+=1
        recovered=[None]*len(stored)
        for i,j in enumerate(indices):recovered[j]=decoded_cipher[i]
        assert recovered==stored
        assert abs(model.score(plain)-row['score'])<1e-10
        verified+=1
    controls=data['E021-controls'];assert controls['gate_passed'] and len(controls['controls'])==9
    for c in controls['controls']:
        assert c['exact'] and c['top'][0]['plaintext_runes']==fixtures[c['fixture']]['plaintext_runes']
        for r in c['top']:verify(r,c['stored_ciphertext_indices'])
    pages=[r for k,r in data.items() if k.startswith('E021-page-')]
    assert {r['page'] for r in pages}=={'LP2-00','LP2-49','LP2-51','LP2-55'}
    for p in pages:
        assert p['ciphertext_runes']==canonical[p['page']]['runes']
        assert len(p['route_scores'])==8
        for r in p['top']:verify(r,to_indices(p['ciphertext_runes']))
    winner=max(pages,key=lambda p:p['top'][0]['score']);values=to_indices(winner['ciphertext_runes'])
    plan=load('experiments/reading_order_null_plan.json');assert plan['selected_page']==winner['page']
    for path,digest in plan['source_outputs'].items():assert sha(path)==digest
    null=[r for k,r in data.items() if k.startswith('E021-null-')];assert len(null)==19
    doubles=lambda v:sum(a==b for a,b in zip(v,v[1:]))
    for n in null:
        assert n['page']==winner['page'] and Counter(n['ciphertext_indices'])==Counter(values)
        assert doubles(n['ciphertext_indices'])==doubles(values)
        assert n['score']==max(r['score'] for r in n['route_scores'])
    exceed=sum(n['score']>=winner['top'][0]['score'] for n in null);p=(1+exceed)/20
    numeric=data['E022-numeric-source-audit'];assert numeric['total_cells_per_source']==256
    audit=load('sources/layout_audit.json')
    for page in audit['pages']:
        assert sha(page['image_path'])==page['image_sha256']
        assert ''.join(page['rune_rows'])==canonical[page['page_id']]['runes']
    elapsed=sum(e['wall_seconds'] for e in phase.values());assert elapsed<=900
    assert max(e['wall_seconds'] for e in phase.values())<=180
    summary={'created_at':now,'selected_page':winner['page'],'top':winner['top'][0],'raw_p':p,'null_exceedances':exceed,'null_replicates':19,
        'page_adjusted_p':min(1,55*p),'pending_larger_calibration':exceed==0,'unknown_pages':len(pages),'routes_per_page':8,'exact_controls':9,
        'image_pages_inspected':7,'numeric_cells_per_source':256,'numeric_token_disagreements':len(numeric['source_disagreements']),
        'numeric_decimal_inconsistencies':len(numeric['published_decimal_inconsistencies']),
        'candidate_records_recomputed':verified,'tests_passed':count,'new_completed_processes':len(phase),'seconds':elapsed,
        'orchestration_seconds':load('checkpoints/phase6_routes.json')['seconds'],'budget_seconds':900,'new_decryptions':[]}
    save('results/phase6_summary.json',summary)
    state=load('research_state.json')
    state.update(status='sixth_batch_complete_no_new_decryption' if exceed else 'sixth_batch_candidate_requires_larger_null',updated_at=now,
        latest_report='reports/attack_phase6_report.md',new_decryptions=[],promising_candidates=([{'page':winner['page'],'status':'uncalibrated_screen_maximum','source':phase['E021-page-'+winner['page']]['output']}] if not exceed else []),
        completed_experiments=[{'id':e['experiment'],'fingerprint':e['fingerprint'],'output':e['output'],'sha256':e['output_sha256']} for e in latest.values()],
        validation={'tests_passed':count,'path':'results/validation_phase6.txt','phase6_candidate_records_recomputed':verified},
        session_budget={'phase':'sixth bounded image/layout queue','max_compute_wall_seconds':900,'max_experiment_wall_seconds':180,'workers':1,'background_jobs':False},
        next_experiments=(['E021-larger-null'] if not exceed else [])+['H024','H023','H018'],
        notes=['Primary objective unresolved; no new plaintext confirmed.','Seven images inspected for layout, not all glyphs independently transcribed.','E021 covers four selected rune pages and eight row routes; no whole-book or columnar exclusion.','Numeric grid disagreements preserved explicitly; canonical data unchanged.','No running research processes.'])
    state['resources'].update(recorded_successful_experiment_runs=len(done),recorded_experiment_subprocess_wall_seconds=sum(e['wall_seconds'] for e in done),phase6_wall_seconds=elapsed)
    if exceed:
        note=f"E021 eight row routes with finite cipher union on4pages: {winner['page']} null p={p}, Bonferroni55={min(1,55*p)}; no supported candidate."
        if note not in state['failed_approaches']:state['failed_approaches'].append(note)
    save('research_state.json',state)
    h=load('hypotheses.json');known={v['id'] for v in h['hypotheses']}
    if 'H021' not in known:h['hypotheses'].append({'id':'H021','claim':'Alternate image-anchored row reading order exposes a page under a small known cipher family.','experiments':['E021'],
        'status':'screen_no_supported_candidate' if exceed else 'larger_null_required','result':summary,'limits':'Four selected pages only; eight row orders, no column alignment, no arbitrary key, no numeric-table decryption.'})
    if 'H024' not in known:h['hypotheses'].append({'id':'H024','claim':'The alphanumeric tables require a separate source/glyph audit before treating them as bytes.','experiments':['E022'],
        'status':'source_discrepancies_documented','result':{'token_disagreements':summary['numeric_token_disagreements'],'decimal_inconsistencies':summary['numeric_decimal_inconsistencies']},
        'limits':'Base60 is replicated prior art; conflicting cells unresolved, all alternatives preserved.'})
    h.update(updated_at=now,status=state['status'],next_queue=(
        [{'id':'E021-larger-null','priority':0,'task':'Register a feasible larger conditional null before any significance interpretation.'}] if not exceed else [])+[
        {'id':'H024','priority':1,'task':'Resolve conflicting Base60 glyphs against source-image coordinates, preserving unresolved alternatives; only then define bounded numeric hypotheses.','gate':'No automatic case normalization; reproduce every byte from a cited cell; no infeasible brute force.'},
        {'id':'H023','priority':2,'task':'Derive bounded search for affine feedback periods2..3; check equivalent prior cases and exact synthetic controls.'},
        {'id':'H018','priority':3,'task':'Use actual source clues to justify any additional text key.'}])
    save('hypotheses.json',h)
    save('checkpoints/phase6_complete.json',{'created_at':now,'status':state['status'],'summary':'results/phase6_summary.json','summary_sha256':sha('results/phase6_summary.json'),
        'experiments':[{'id':e['experiment'],'fingerprint':e['fingerprint'],'output':e['output'],'sha256':e['output_sha256']} for e in phase.values()],
        'tests':count,'new_decryptions':[]})
    disputes='\n'.join('| '+str(r['page_id'])+' | '+str(r['row_1based'])+','+str(r['column_1based'])+' | '+
        ' / '.join(r['tokens'][name] for name in ('relikd_canonical','iddqd','scream314'))+' | '+
        ' / '.join(str(r['values'][name]) for name in ('relikd_canonical','iddqd','scream314'))+' |' for r in numeric['source_disagreements'])
    conclusion='Kein korrigiert signifikanter Befund.' if exceed else 'Größere Kalibrierung erforderlich; kein Entschlüsselungsnachweis.'
    report=f'''# Sechste Forschungsserie: Quellenbilder, Leserichtungen und Zahlentabellen

Stand (UTC): {now}. **Keine neue Entschlüsselung bestätigt.**
Die Zeilenstruktur von sieben Seiten wurde am Bild geprüft. Eine begrenzte
Leserichtungssuche auf vier unbekannten Runenseiten wurde mit bekannten Lösungen
und Zufallstexten validiert. Zusätzlich wurden Unterschiede zwischen drei
Transkriptionen der Zahlentabellen dokumentiert.

## Bildprüfung und explizite Grenzen

Geprüft wurden LP2-00, 49, 50, 51, 55, 56 und 57. Drei zusätzliche JPEGs wurden
aus dem schon gepinnten scream314-Commit geladen; übrige Bilder lagen bereits
im Quellenbestand. [Bildmanifest](../sources/layout_images_manifest.json) und
[Layoutprotokoll](../sources/layout_audit.json) enthalten URLs, Commit, Abrufzeit,
SHA-256, native Bildgröße und manuell gewählte Pixelregionen der Zeilen.
Die Regionen sind ungefähre Inspektionsbereiche, keine exakten Glyphensegmente.

Bestätigte Zeilenstruktur: LP2-00 zwölf Runenzeilen; LP2-49 drei Runenzeilen über
einer 10×8-Tabelle; LP2-50 eine 13×8-Tabelle ohne Runentext; LP2-51 neun Tabellenzeilen
zu je acht Zellen und vier Runenzeilen darunter; LP2-55 vier Runenzeilen.
LP2-56 hat drei plus zwei Runenzeilen mit einem Hash dazwischen, LP2-57 fünf.
Große Initialrunen werden ausdrücklich einmal der ersten Textzeile zugeordnet,
wie in der bestehenden Transkription. Das ist eine festgehaltene Zuordnungsregel.

Die Prüfung betrifft Zeilenanzahl, Reihenfolge und Endpunkte, **keine vollständige
unabhängige Transkription jeder Glyphe** und keinen Bildaudit des gesamten Buchs.
Die Schrift ist nicht gleichmäßig in Runenspalten gesetzt. Deshalb werden keine
künstlich aufgefüllten Rechtecke oder angeblich physischen Vertikalspalten erzeugt.
Quellenübereinstimmung beweist keine unabhängig authentifizierte Cicada-Herkunft.

## E021: acht Leserichtungen mit festem Chiffrenraster

LP2-00, 49, 51 und 55 waren vor den neuen Scores festgelegt. Acht bijektive
Permutationen: Zeilen von oben oder unten; innerhalb der Zeilen links nach rechts,
rechts nach links oder abwechselnd, mit beiden Anfangsrichtungen. Ungleiche
Zeilenlängen bleiben erhalten. Die Permutation erfolgt **vor** der Entschlüsselung;
Schlüsselphase und F-Unterbrechungen beziehen sich auf diesen Lesestrom.

Jede Route prüft alle 812 affinen Substitutionen, die beiden bekannten Schlüssel
DIVINITY und FIRFUMFERENFE mit allen Phasen sowie Primzahlen, p−1 und φ(n) mit
Starts 0–255. Bei den Schlüsselströmen werden vier Vorzeichen und sämtliche
F-Teilmengen exakt optimiert. Der externe Viergramm-Score bleibt unverändert.
Die normale Leserichtung dient als Referenz; die Schlüsselmenge ist kleiner
als der volle frühere Wortkatalog. E021 prüft weder beliebige Schlüssel noch
jede denkbare Transposition, Rückkopplung oder seitenübergreifende Kombination.

Die acht synthetisch umgeordneten LP2-56-Kontrollen werden jeweils im vollständigen
Suchraum exakt wiedergewonnen; die Route wird dem Sucher nicht verraten.
Zusammen mit LP2-57 ergibt das **9/9 exakte Kontrollen**. Die erwarteten Texte
sind bereits bekannt; dies validiert die Implementierung, keine neue historische Lösung.

Stärkster Kandidat: {winner['page']}, Route `{winner['top'][0]['recipe']['route']['name']}`,
Score {winner['top'][0]['score']:.6f}. Vollständige unveränderte Ausgabe:

```text
{winner['top'][0]['transliteration']}
```

{exceed} von 19 unabhängigen Nulltexten erreichen mindestens diesen Score.
Plus-eins-p={p:.3f}, nach konservativer Auswahlkorrektur über 55 Seiten
p={min(1,55*p):.3f}. {conclusion}
Die Nulltexte erhalten Runenhäufigkeiten und die Anzahl gleicher Nachbarrunen
in der ursprünglichen Speicherreihenfolge. Jeder durchläuft wieder alle acht
Routen und das gesamte Chiffrenraster. Die vier Seiten wurden auch aufgrund
früherer Scores ausgewählt; sie sind keine frische Zufallsstichprobe. Der Faktor
55 berücksichtigt diese Auswahl konservativ. Das Nullmodell erhält keine
Wortgrenzen oder andere höhere Struktur. 19 Replikate könnten korrigierte
Signifikanz nicht auflösen; null Überschreitungen würden eine größere Prüfung erfordern.

## E022: Zahlentabellen als Quellenproblem

Die Tabellen von LP2-49/50/51 enthalten zusammen **256 Zellen**. Die Base60-Deutung
steht bereits in der gepinnten Community-Quelle und wird hier nur reproduziert:
Alphabet `0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwx`,
Wert eines Paars = 60×Index des ersten Zeichens + Index des zweiten Zeichens.
Alle Werte der drei Transkriptionsvarianten liegen zwischen 0 und 255.
Das beweist weder einen Dateityp noch eine Verschlüsselung oder einen Schlüssel.

Es gibt **{len(numeric['source_disagreements'])} unterschiedliche Zellen** zwischen den Quellen:

| Seite | Zeile,Spalte (ab 1) | relikd / iddqd / scream314 | jeweilige Base60-Werte |
|---|---|---|---|
{disputes}

Zusätzlich enthält die veröffentlichte Dezimaltabelle der scream314-Quelle
**{len(numeric['published_decimal_inconsistencies'])} Abweichungen** von der direkten Umrechnung ihrer eigenen
Base60-Zeichen. Die ursprüngliche Kennzeichnung einer Tabelle als fehlerhaft
wird als Quellenhinweis behandelt, nicht als Entscheidung über richtige Glyphen.
Details und alle drei vollständigen Varianten bleiben im
[E022-Ergebnis]({('../'+phase['E022-numeric-source-audit']['output'])}) erhalten.

Die Konflikte sind **nicht aufgelöst**. Groß-/Kleinschreibung wird nicht automatisch
angeglichen. Bestehende kanonische Daten und historische Ergebnisse wurden nicht
verändert. E021 entschlüsselt ausschließlich den ausgewählten Runenstrom;
Tabellen, Hashes und Bilder bleiben erhalten, ohne sie als Runen oder zusätzlichen
Schlüsselverbrauch zu interpretieren. Das ist eine Begrenzung dieser Hypothese.

## Validierung und Fortsetzung

{count} Tests bestanden; {verified} gespeicherte Kandidaten wurden unabhängig
zurückverschlüsselt und über die inverse Route wieder an die ursprünglichen
Positionen gesetzt. Modellwerte wurden skalar nachgerechnet, Hashes geprüft.
E022 ist ein deterministischer Quellen-/Rechenvergleich; ein Zufallsmodell oder
p-Wert wäre dafür nicht sinnvoll. Es wird keine neu entdeckte Chiffre behauptet.

{len(phase)} erfolgreiche Aufgaben, {elapsed:.3f} Sekunden Experimentzeit innerhalb
des 900-Sekunden-Budgets; maximal 180 Sekunden je Prozess, ein Forschungsprozess.
Keine Hintergrundaufgabe läuft weiter. [Checkpoint](../checkpoints/phase6_complete.json),
[Übersicht](../results/phase6_summary.json), [Forschungsstand](../research_state.json).

Als Nächstes haben die widersprüchlichen Zahlenzeichen Priorität: mit Bildkoordinaten
prüfen, offene Alternativen erhalten und erst dann begrenzte Hypothesen für die
256 Werte festlegen. Längere allgemeine Rückkopplung bleibt eine getrennte Aufgabe.
'''
    (ROOT/'reports/attack_phase6_report.md').write_text(report,encoding='utf-8')
    print(json.dumps(summary,ensure_ascii=True))

if __name__=='__main__':main()
