"""Independent replay and scoring checks for the boundary-aware research phase."""
from collections import Counter
from datetime import datetime,timezone
import hashlib
import json
import math
from pathlib import Path
import re
import subprocess
import sys
from PIL import Image

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'experiments'))
from attack_support import to_indices,stream_catalog
from external_language import paragraphs,external_model
from liberprimus.alphabet import transliterate

def load(path):return json.loads((ROOT/path).read_text(encoding='utf-8'))
def sha(path):return hashlib.sha256((ROOT/path).read_bytes()).hexdigest()
def save(path,data):(ROOT/path).write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')

def main():
    if (ROOT/'checkpoints/phase9_complete.json').exists():raise RuntimeError('Newer checkpoint exists')
    complete=load('checkpoints/phase8_boundary_complete.json')
    tests=subprocess.run([sys.executable,'-m','unittest','discover','-s','tests','-v'],cwd=ROOT,
                         capture_output=True,text=True,encoding='utf-8',timeout=60)
    output=tests.stdout+tests.stderr;(ROOT/'results/validation_phase8.txt').write_text(output,encoding='utf-8')
    if tests.returncode:raise RuntimeError(output)
    test_count=int(re.search(r'Ran (\d+) tests',output).group(1));now=datetime.now(timezone.utc).isoformat()
    events=[json.loads(line) for line in (ROOT/'experiment_log.jsonl').read_text(encoding='utf-8').splitlines()]
    done=[e for e in events if e.get('status')=='completed'];latest={e['experiment']:e for e in done}
    phase={k:e for k,e in latest.items() if k.startswith(('E026','E027','E028','E029'))};assert len(phase)==78
    for e in phase.values():
        assert sha(e['output'])==e['output_sha256']
        for path,digest in e['input_dependencies'].items():assert sha(path)==digest,path
    data={k:load(e['output']) for k,e in phase.items()}
    audit=data['E026-boundary-audit'];benchmark=data['E027-boundary-model'];controls=data['E028-controls']
    triage=data['E029-community-claim-triage']
    assert triage['published_digest_matches_E023']==load('results/E023-glyph-audit-8315f5c684bb.json')['byte_sha256']
    assert triage['order_11_mod29']==28 and triage['pisano_29']==14 and not triage['remote_code_executed']
    assert len(audit['pages'])==75 and len(audit['eligible_unknown_pages'])==54
    assert audit['conflicting_LP2_pages']==['LP2-35']
    decision=load('sources/boundary_layout_decisions.json');image_manifest=load('sources/boundary_image_manifest.json')
    assert sha(decision['image_path'])==decision['image_sha256']==image_manifest['sha256']
    assert sha(decision['crop_path'])==decision['crop_sha256']
    with Image.open(ROOT/decision['image_path']) as source,Image.open(ROOT/decision['crop_path']) as crop:
        expected=source.crop(decision['crop_box']);assert expected.size==crop.size and expected.tobytes()==crop.tobytes()
    record=next(p for p in audit['pages'] if p['page']=='LP2-35')
    assert record['internal_canonical_only']==[80] and 80==decision['rune_offset']
    for p in audit['pages']:
        raw=p['canonical']['raw_text'];offsets=p['canonical']['rune_character_offsets']
        # Explicit aliases are recorded rather than normalized invisibly.
        aliases={r['character_offset']:r['canonical'] for r in p['canonical']['aliases']}
        assert ''.join(aliases.get(i,raw[i]) for i in offsets)==p['canonical']['runes']
    assert benchmark['gate_passed'] and all(c['exact'] for c in benchmark['controls'])
    assert controls['gate_passed'] and len(controls['controls'])==4
    _,counts,source_metadata=paragraphs();length_totals=Counter()
    for word,n in counts.items():length_totals[len(word)]+=n
    char_model=external_model(4);verified=0
    def independent_score(plain,ends):
        total=0.0;begin=0
        for end in ends:
            word=tuple(plain[begin:end]);logq=char_model.score(word)*len(word)
            total+=math.log(counts.get(word,0)+20*math.exp(logq))-math.log(length_totals[len(word)]+20)
            begin=end
        assert begin==len(plain)
        return total/len(plain)
    def verify(row,values,ends):
        nonlocal verified
        r=row['recipe'];plain=to_indices(row['plaintext_runes']);assert len(values)==len(plain)
        if r['family']=='affine':
            decoded=[pow(r['a'],-1,29)*(p-r['b'])%29 for p in plain]
        else:
            key=r.get('key_indices') or stream_catalog(len(values)+256)[r['family']]
            cursor=r['start'];skip=set(r['skip_positions']);decoded=[]
            for i,p in enumerate(plain):
                if i in skip:assert p==0;decoded.append(0)
                else:
                    kval=key[cursor%len(key)] if r['family']=='vigenere' else key[cursor]
                    decoded.append(r['cipher_sign']*(p-r['key_sign']*kval)%29);cursor+=1
        assert decoded==list(values)
        assert abs(independent_score(plain,ends)-row['score'])<1e-9
        verified+=1
    fixtures={f['id']:f for f in load('known_solutions/fixtures.json')}
    for row in benchmark['controls']:
        f=fixtures[row['fixture']];assert row['plaintext_runes']==f['plaintext_runes']
        verify(row,to_indices(f['ciphertext_runes']),row['segment_ends'])
    for c in controls['controls']:
        f=fixtures[c['fixture']];assert c['top'][0]['plaintext_runes']==f['plaintext_runes']
        for row in c['top']:verify(row,to_indices(f['ciphertext_runes']),c['segment_ends'])
    canonical={p['id']:p for p in load('transcriptions/pages.json')}
    audited={p['page']:p for p in audit['pages']}
    pages=[r for k,r in data.items() if k.startswith('E028-page-')]
    assert len(pages)==55 and {r['page'] for r in pages}=={f'LP2-{n:02}' for n in range(56) if n!=50}
    for p in pages:
        assert p['ciphertext_runes']==canonical[p['page']]['runes']
        assert p['segment_ends']==audited[p['page']]['canonical']['segment_ends']
        assert p['key_sign_tasks']==1536
        for row in p['top']:verify(row,to_indices(p['ciphertext_runes']),p['segment_ends'])
    winner=max(pages,key=lambda p:p['top'][0]['score']);selection=load('experiments/boundary_attack_selection.json')
    assert sha('experiments/boundary_attack_selection.json')==complete['selection_sha256']
    assert winner['page']==selection['selected_page']==complete['selected_page']
    assert winner['top'][0]['score']==selection['observed_score']
    for path,digest in selection['source_outputs'].items():assert sha(path)==digest
    nulls=[r for k,r in data.items() if k.startswith('E028-null-')];assert len(nulls)==19
    cipher=to_indices(winner['ciphertext_runes']);doublets=lambda v:sum(a==b for a,b in zip(v,v[1:]))
    for r in nulls:
        assert r['segment_ends']==winner['segment_ends'] and r['key_sign_tasks']==1536
        assert Counter(r['ciphertext_indices'])==Counter(cipher)
        assert doublets(r['ciphertext_indices'])==doublets(cipher)
    exceed=sum(r['score']>=winner['top'][0]['score'] for r in nulls);p=(1+exceed)/20
    assert p==complete['raw_p'] and exceed==complete['exceedances']
    elapsed=sum(e['wall_seconds'] for e in phase.values())
    attack_seconds=sum(e['wall_seconds'] for k,e in phase.items() if k.startswith('E028'))
    assert elapsed<900 and attack_seconds<850 and all(e['wall_seconds']<180 for e in phase.values())
    plain=to_indices(winner['top'][0]['plaintext_runes']);starts=[0]+winner['segment_ends'][:-1]
    rendered=' '.join(transliterate(plain[a:b]) for a,b in zip(starts,winner['segment_ends']))
    summary={'created_at':now,'pages_audited':75,'source_agreeing_unknown_boundaries':54,
        'image_supported_boundary_exception':'LP2-35 rune offset80',
        'word_strict_wins':benchmark['word_strict_wins'],'baseline_strict_wins':benchmark['baseline_strict_wins'],
        'comparisons':1600,'known_key_controls':3,'full_union_controls':4,'unknown_pages':55,
        'selected_page':winner['page'],'top':winner['top'][0],'segmented_transliteration':rendered,
        'raw_p':p,'page_adjusted_p':min(1,55*p),'null_exceedances':exceed,'null_replicates':19,
        'pending_larger_calibration':exceed==0,'candidate_records_recomputed':verified,
        'tests_passed':test_count,'new_completed_processes':len(phase),'seconds':elapsed,
        'attack_seconds':attack_seconds,'attack_orchestration_seconds':complete['seconds'],
        'phase_budget_seconds':900,'new_decryptions':[]}
    summary['community_claim_triage']={'matching_prior_byte_digest':triage['published_digest_matches_E023'],
        'arithmetic_facts_reproduced':2,'new_decryptions_confirmed':0,'alternate_binary_provenance':'unverified'}
    save('results/phase8_summary.json',summary)
    entries=[{'id':k,'fingerprint':e['fingerprint'],'output':e['output'],'sha256':e['output_sha256']} for k,e in phase.items()]
    save('checkpoints/phase8_complete.json',{'created_at':now,'status':'eighth_batch_complete_no_new_decryption',
        'summary':'results/phase8_summary.json','summary_sha256':sha('results/phase8_summary.json'),'experiments':entries})
    state=load('research_state.json');known={r['fingerprint'] for r in state['completed_experiments']}
    state['completed_experiments'] += [e for e in entries if e['fingerprint'] not in known]
    state.update(status='eighth_batch_complete_no_new_decryption' if exceed else 'eighth_batch_candidate_requires_larger_null',
        updated_at=now,latest_report='reports/attack_phase8_report.md',
        next_experiments=([] if exceed else ['E028-larger-null'])+['H027','H028','H023','H018'],
        promising_candidates=[] if exceed else [{'page':winner['page'],'status':'uncalibrated_screen_maximum','source':'results/phase8_summary.json'}],
        validation={'tests_passed':test_count,'path':'results/validation_phase8.txt','phase8_candidate_records_recomputed':verified},
        session_budget={'phase':'eighth bounded boundary-aware queue','max_compute_wall_seconds':900,
                        'max_experiment_wall_seconds':180,'workers':1,'background_jobs':False},
        scoring_gate='Frozen length-conditioned word model passes3 known-key and4 full-union controls; no automatic decryption classification.',
        notes=['No previously unknown plaintext confirmed.',
               '75 layouts retained; 54 unknown pages agree in boundary positions; LP2-35 apostrophe is image-supported.',
               'Single-page scoring treats edge fragments as complete lexical segments; this is a model limitation, not an observed word boundary.',
               'All canonical and raw sources unchanged. Apostrophes split by explicit external-tokenizer convention.',
               'E028 is a changed-score rescan of a finite known-word/number/affine family, not a novel cipher family.',
               'A recent community solution claim was partially checked; matching prior bytes and arithmetic facts do not establish a new decryption. Alternate binary provenance unresolved.',
               'No research process remains running.'])
    state['resources'].update(recorded_successful_experiment_runs=len(done),
        recorded_experiment_subprocess_wall_seconds=sum(e['wall_seconds'] for e in done),phase8_wall_seconds=elapsed)
    message=f'E028 boundary-conditioned finite word/number/affine grid on55pages: {winner["page"]}, rawp={p}, adjusted={min(1,55*p)}; no supported plaintext.'
    if message not in state['failed_approaches']:state['failed_approaches'].append(message)
    save('research_state.json',state)
    h=load('hypotheses.json')
    record={'id':'H026','claim':'Source lexical boundaries and an externally trained word-conditioned model improve finite-key decoding.',
        'experiments':['E026','E027','E028'],'status':'control_gate_passed_unknown_screen_complete',
        'result':summary,'limits':'Previously seen controls; modest descriptive ranking gain; page-edge fragments treated as words, no unknown-key/section search or broad family exclusion.'}
    h['hypotheses']=[r for r in h['hypotheses'] if r['id']!='H026']+[record]
    claim_record={'id':'H028','claim':'A published purported authoritative binary may provide verifiable data beyond the image-derived table.',
        'experiments':['E029'],'status':'claim_partially_checked_provenance_unverified','result':summary['community_claim_triage'],
        'limits':'Only scoped published statements checked; no new plaintext verified, no remote code executed, no historical authentication of the alternate digest.'}
    h['hypotheses']=[r for r in h['hypotheses'] if r['id']!='H028']+[claim_record]
    h['next_queue']=[
        {'id':'H027','priority':1,'task':'Quantify sensitivity to page-edge word fragments and apostrophe treatment using predeclared held-out external segments and known controls; do not tune to unknown candidates.'},
        {'id':'H028','priority':2,'task':'Locate public archival provenance for claimed sexagesimal.bin and compare actual bytes with source images before adopting any corrections; no onion/private-system access or downloaded-code execution.'},
        {'id':'H023','priority':3,'task':'Design a bounded period3 or boundary-aware feedback search only after exact controls and full null budget are feasible.'},
        {'id':'H018','priority':4,'task':'Use concrete source clues before expanding text keys or numeric interpretations.'}]
    if not exceed:h['next_queue'].insert(0,{'id':'E028-larger-null','priority':0,'task':'Freeze candidate and preregister a larger independent null calibration before inference.'})
    h['updated_at']=now;save('hypotheses.json',h)
    report=f'''# Achte Forschungsserie: Quellengetreue Wortgrenzen und Wortscore

Stand (UTC): {now}. **Keine neue Entschlüsselung bestätigt.**

## E026: Trennzeichen und Seitenlayout

Alle 75 kanonischen Seiten wurden mit ursprünglichen Layouttexten, Zeichenoffsets,
Runenpositionen, expliziten Runenaliasen und Nicht-Runenzeichen gespeichert. Die
iddqd-Quelle unterscheidet im eigenen Kopf ausdrücklich Worttrenner, Zeilen und
Seiten. Zeilenschrägstriche und Leerraum erzeugen hier keine Wortgrenze. Bei
zusammengehörigen Kontrollseiten werden Wörter über den Seitenwechsel fortgeführt,
sofern kein explizites Trennzeichen vorliegt. Zahlen und Hashes bleiben erhalten.

54 der 55 unbekannten Runenseiten stimmen zwischen beiden Quellen in Runen und
inneren Segmentgrenzen überein. Auf **LP2-35, Runenoffset 80** enthält relikd
`ᛈᛖ'ᛏ`, iddqd dagegen `ᛈᛖᛏ`. Das nachgeladene Bild aus dem schon gepinnten
scream314-Commit zeigt einen kurzen erhöhten Strich zwischen den letzten beiden
Runen. Die vorhandene relikd-Interpunktion wird dadurch gestützt; beide Lesarten
bleiben im E026-Ergebnis erhalten, die Entscheidung ist separat dokumentiert.

![LP2-35: Quellenausschnitt ohne Resampling](../sources/LP2-35-boundary-crop.png)

[Bildmanifest](../sources/boundary_image_manifest.json),
[Koordinaten und Entscheidung](../sources/boundary_layout_decisions.json).
Ein visueller Leser, kein vollständiger Bildaudit. Der keilschriftähnliche Kopf bleibt
im Originalbild erhalten und wird hier nicht interpretiert.

Apostrophe trennen in dieser Untersuchung **lexikalische Teilstücke**, passend
zum unveränderten externen Text-Tokenizer: etwa `DON T`. Das behauptet keine
gedruckte Wortgrenze. Ebenso werden die Endsegmente einzeln untersuchter Seiten
wie vollständige Teilstücke bewertet, selbst wenn ein Wort über die Seite hinweg
weitergehen könnte. Diese Randfragment-Annahme ist eine ausdrückliche Grenze des
Scores; innere Zeilenumbrüche erzeugen dagegen keine künstlichen Grenzen.

## E027: Festgelegtes externes Wortmodell

Training ausschließlich auf den elf schon gepinnten Emerson-Essays, ohne Kapitel
II und ohne Liber-Primus-Texte: {source_metadata['word_tokens']} Worttokens,
{source_metadata['distinct_rune_words']} verschiedene Runenwörter. Gegebene
Segmentlänge L, Wort w:

`P(w | L) = (count(w) + 20 Q(w)) / (N_L + 20)`.

Q ist die bisherige externe Viergramm-Kette, am Segmentanfang zurückgesetzt.
Der Gesamtscore ist die Summe der Wort-Logwahrscheinlichkeiten pro Rune. Das
Modell ist für jede feste Länge normalisiert; unbekannte Wörter behalten eine
positive Backoff-Wahrscheinlichkeit. Parameter vorab festgelegt, keine Anpassung
an unbekannte Kandidaten.

Auf denselben 1.600 Veränderungen der acht kanonisch konsistenten Kontrolltexte
bevorzugt der Wortscore den Originaltext **{benchmark['word_strict_wins']}**-mal,
der frühere Score **{benchmark['baseline_strict_wins']}**-mal. Dies ist ein
deskriptiver Vergleich korrelierter Veränderungen, kein Signifikanznachweis und
keine blinde historische Validierung. Drei bekannte Schlüsselkontrollen werden
mit allen Phasen beziehungsweise Zahlenstarts und F-Unterbrechungen exakt gefunden.

Die Optimierung speichert innerhalb eines Segments Schlüsselcursor und vollständiges
Teilwort. Erst nach der Wortbewertung werden Pfade mit gleichem Cursor zusammengeführt.
Das deckt sämtliche F-Unterbrechungsteilmengen im angegebenen Suchraum ab, ohne
Beam-Pruning. Kleine vollständige Enumerationen prüfen die DP unabhängig.

## E028: Vollständiger begrenzter Suchraum

812 affine Substitutionen, 381 vorhandene primitive Wortschlüsselzyklen mit allen
Phasen, drei Zahlenströme mit Starts 0–255, vier Vorzeichen und sämtliche
F-Unterbrechungsteilmengen. Im vollständigen Verbund werden vier bekannte Texte
exakt als bestes Ergebnis gefunden. Danach alle 55 unbekannten Runenseiten
untersucht. Die reine Zahlenseite LP2-50 ist erhalten, aber kein Runeninput.
Dies wiederholt bekannte Chiffrenfamilien mit geändertem Score; keine neue Familie.

Stärkster Kandidat: {winner['page']}, Score {winner['top'][0]['score']:.6f}.
Unveränderte Transliteration, durch die festen Quellsegmente getrennt:

```text
{rendered}
```

{exceed} von 19 unabhängigen Nulltexten erreichen mindestens diesen Score;
Plus-eins-p={p:.3f}, Bonferroni über 55 Seiten={min(1,55*p):.3f}. Segmentpositionen
und -längen bleiben fest, ebenso Runenhäufigkeiten und gleiche Nachbarpaare.
Jeder Nulltext durchläuft den gesamten identischen Suchraum. Die Auswahl wurde
vor den Nulltests eingefroren. 19 Replikate reichen nicht zur Auflösung korrigierter
Signifikanz; null Überschreitungen würden eine größere vorab registrierte Prüfung
verlangen. Kein neuer Klartext bestätigt.

## E029: Begrenzte Prüfung einer öffentlichen Lösungsmeldung

Eine [öffentliche Meldung](https://www.reddit.com/r/mystery/comments/1x0432x/proof_5_new_liber_primus_pages_solved/)
behauptet mehrere neue Lösungen. In den untersuchten Abschnitten des verlinkten
[Projekts](https://21skibidiserb37.gitlab.io/xyzsolving333/) steht derselbe Byte-Digest
wie in E023; unsere Bytefolge stimmt damit mit einer öffentlich angegebenen
Folge überein. Eine historische Priorität ist durch den aktuellen Abruf nicht belegt.
Auch die angegebenen arithmetischen Fakten stimmen: 11 hat modulo 29 Ordnung 28,
die Fibonacci-Paarfolge modulo 29 kehrt nach 14 Schritten zurück. Beides wurde
unabhängig nachgerechnet, liefert aber keinen unbekannten Klartext. LP2-56/57
sind bereits bekannte Kontrolllösungen. 256 Byte Länge allein identifizieren
keinen RSA-Block. Die Herkunft der zusätzlich behaupteten Binärdatei und ihres
abweichenden Digests bleibt ungeprüft; diese Daten werden nicht übernommen.

Nur diese Teilbehauptungen wurden geprüft, kein Gesamturteil über die Website.
Zeitgestempelte HTML-Bytes und SHA-256 liegen im
[Quellenmanifest](../sources/community_claim_2026-10-20/manifest.json).
Der direkte Reddit-Abruf liefert nur eine Client-Hülle; der Beitrag wurde über
das Webwerkzeug gelesen. Fremde Skripte und Binärdateien wurden nicht ausgeführt.
Keine neue Entschlüsselung unabhängig bestätigt.

## Validierung und Fortsetzung

{test_count} Tests bestanden; {verified} Kandidaten durch unabhängige Rückverschlüsselung
und direkte Auswertung der Wahrscheinlichkeitsformel geprüft. Alle neuen Ergebnis-
und Abhängigkeitshashes stimmen. Der Bildausschnitt stimmt pixelgenau mit seiner
angegebenen Region im Quellenbild überein. Alte kanonische Daten bleiben unverändert.

{len(phase)} erfolgreiche Aufgaben, {elapsed:.3f} Sekunden protokollierte Experimentzeit;
E028 davon {attack_seconds:.3f} innerhalb der 850-Sekunden-Grenze. Phasengrenze
900 Sekunden, ein Forschungsprozess. Keine Hintergrundaufgabe läuft weiter.

Als Nächstes: Einfluss der Randfragmente und Apostrophkonvention an vorab getrennten
externen Textausschnitten und bekannten Kontrollen messen. Längere Rückkopplung
braucht weiterhin einen tragfähigen Kontroll- und Nullvergleichsaufwand. Weitere
Textschlüssel werden nicht ohne konkrete Quellenhinweise erweitert.

[Checkpoint](../checkpoints/phase8_complete.json), [Übersicht](../results/phase8_summary.json).
'''
    (ROOT/'reports/attack_phase8_report.md').write_text(report,encoding='utf-8')
    print(json.dumps(summary,ensure_ascii=True))

if __name__=='__main__':main()
