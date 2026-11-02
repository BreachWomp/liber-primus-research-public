"""Validate and checkpoint phase two without replacing historical reports."""
from datetime import datetime,timezone
import hashlib
import json
from pathlib import Path
import re
import subprocess
import sys

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"experiments"))
from attack_support import model_without,to_indices,key_catalog,stream_catalog
from plaintext_autokey_attack import invert


def load(path):return json.loads((ROOT/path).read_text(encoding="utf-8"))
def save(path,value):(ROOT/path).write_text(json.dumps(value,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
def sha(path):return hashlib.sha256((ROOT/path).read_bytes()).hexdigest()


def main():
    if (ROOT/"checkpoints/phase3_complete.json").exists():
        raise RuntimeError("Phase2 finalizer is historical; use scripts/finalize_phase3.py")
    now=datetime.now(timezone.utc).isoformat()
    check=subprocess.run([sys.executable,"-m","unittest","discover","-s","tests","-v"],cwd=ROOT,
                         capture_output=True,text=True,encoding="utf-8",timeout=60)
    validation=check.stdout+check.stderr
    (ROOT/"results/validation_phase2.txt").write_text(validation,encoding="utf-8")
    if check.returncode:raise RuntimeError(validation)
    test_count=int(re.search(r"Ran (\d+) tests",validation).group(1))
    events=[json.loads(line) for line in (ROOT/"experiment_log.jsonl").read_text(encoding="utf-8").splitlines()]
    completed=[e for e in events if e.get("status")=="completed"]
    latest={}
    for event in completed:latest[event["experiment"]]=event
    phase=[e for name,e in latest.items() if int(name[1:4])>=6]
    expected={"E006-selective-control-benchmark","E009-null-LP2-55","E009-null-LP2-49","E010-autokey","E011-autokey"}
    pages={p["id"]:p for p in load("transcriptions/pages.json")}
    eligible=[p for p in pages.values() if p["edition"]=="LP2" and p["page"]<=55 and p["runes"]]
    expected|={f"E007-dictionary-{p['id']}" for p in eligible}|{f"E008-streams-{p['id']}" for p in eligible}
    if {e["experiment"] for e in phase}!=expected:raise RuntimeError("phase task inventory incomplete")
    for e in phase:
        if sha(e["output"])!=e["output_sha256"]:raise RuntimeError("changed output "+e["output"])
        for path,digest in e["input_dependencies"].items():
            if sha(path)!=digest:raise RuntimeError("changed dependency "+path)
    outputs={e["experiment"]:load(e["output"]) for e in phase}
    model=model_without();streams=stream_catalog(1755);verified=0
    for name,data in outputs.items():
        if not name.startswith(("E007","E008","E010","E011")):continue
        for page in data["pages"]:
            values=to_indices(pages[page["page"]]["runes"])
            assert page["ciphertext_runes"]==pages[page["page"]]["runes"]
            if name.startswith("E010"):
                row=page["top_suffix"];p=row["period"]
                assert [(row["cipher_sign"]*values[i]+row["feedback_sign"]*values[i-p])%29 for i in range(p,len(values))]==row["plaintext_indices"]
                assert abs(model.score(row["plaintext_indices"])-row["score"])<1e-10
                verified+=1;continue
            for row in page["top"]:
                plain=to_indices(row["plaintext_runes"]);recipe=row["recipe"]
                if name.startswith("E011"):
                    assert invert(plain,recipe["key_indices"],recipe["cipher_sign"],recipe["feedback_sign"],recipe["skip_positions"])==values
                else:
                    key=recipe.get("key_indices") or streams[recipe["family"]]
                    cursor=recipe["start"];skip=set(recipe["skip_positions"]);cipher=[]
                    for i,symbol in enumerate(plain):
                        if i in skip:
                            assert symbol==0;cipher.append(0)
                        else:
                            cipher.append((recipe["cipher_sign"]*(symbol-recipe["key_sign"]*key[cursor]))%29)
                            cursor+=1
                            if name.startswith("E007"):cursor%=len(key)
                    assert cipher==values
                assert abs(model.score(plain)-row["score"])<1e-10
                verified+=1
    controls=outputs["E006-selective-control-benchmark"]
    autokey=outputs["E010-autokey"];plainauto=outputs["E011-autokey"]
    dictionary_tasks=sum(o.get("evaluated_key_sign_tasks",0) for n,o in outputs.items() if n.startswith("E007"))
    stream_tasks=sum(o.get("evaluated_key_sign_tasks",0) for n,o in outputs.items() if n.startswith("E008"))
    phases=sum(len(k["indices"]) for k in key_catalog())*4*55
    phase_seconds=sum(e["wall_seconds"] for e in phase)
    phase_summary={"updated_at":now,"experiment_groups":["E006","E007","E008","E009","E010","E011"],
                   "completed_runs":len(phase),"dictionary_key_sign_tasks":dictionary_tasks,"dictionary_phase_sign_combinations":phases,
                   "stream_key_sign_tasks":stream_tasks,"stream_start_sign_combinations":stream_tasks*256,
                   "ciphertext_autokey_tasks":autokey["evaluated_page_period_sign_tasks"],
                   "plaintext_autokey_recipes":plainauto["evaluated_recipes"],"verified_saved_candidates":verified,
                   "wall_seconds":phase_seconds,"tests_passed":test_count,"new_decryptions":[]}
    save("results/phase2_summary.json",phase_summary)
    state=load("research_state.json")
    state.update(status="second_attack_batch_complete_no_new_decryption",updated_at=now,
                 latest_report="reports/attack_phase2_report.md",new_decryptions=[],promising_candidates=[],
                 scoring_gate="fails_exact_LP2_56_and_DIVINITY_interruptions; no automatic success classification",
                 validation={"tests_passed":test_count,"path":"results/validation_phase2.txt","saved_candidates_replayed":verified},
                 session_budget={"phase":"second bounded direct-attack queue","max_compute_wall_seconds":900,
                                 "max_experiment_wall_seconds":180,"workers":1,"background_jobs":False},
                 resources={"recorded_successful_experiment_runs":len(completed),
                            "recorded_experiment_subprocess_wall_seconds":sum(e["wall_seconds"] for e in completed),
                            "phase2_wall_seconds":phase_seconds,"scope":"Measured experiment runs only; source retrieval, tests, analysis excluded."},
                 completed_experiments=[{"id":e["experiment"],"fingerprint":e["fingerprint"],"output":e["output"],"sha256":e["output_sha256"]} for e in latest.values()],
                 next_experiments=["H012","H013","H014"],
                 notes=["Primary objective remains a new independently reproducible decryption; not achieved.",
                        "User explicitly prioritized direct unknown-page attacks; expanded image audit deferred.",
                        "All scheduled phase2 attacks and calibration finished; no live background process.",
                        "Skip identical completed fingerprints; do not run the initial finalizer over this checkpoint."])
    state["failed_approaches"]+= [s for s in [
        "E007/E008 selected language maxima are ordinary under matched count/doublet conditional shuffles.",
        "No signal in seed-free ciphertext-autokey suffixes of period1..64 under the specified plug-in null.",
        "390 literal-key plaintext-autokey seeds with none/all-F interruptions yield no supported candidate."] if s not in state["failed_approaches"]]
    save("research_state.json",state)
    hypotheses=load("hypotheses.json")
    entries=[
      {"id":"H007","priority":2,"claim":"A normalized backoff score can rank true text above mutations and choose correct F interruptions.",
       "experiments":["E006"],"status":"partial_control_pass_scoring_gate_failed",
       "result":"1105/1200 corruption comparisons; exact CIRCUMFERENCE known-key recovery; DIVINITY98.835% and LP2-56 not exact.",
       "scope":"Leave-one-section-out controls; mutation comparisons correlated; no significance claim."},
      {"id":"H008","priority":3,"claim":"Uniform rejection shuffles conditional on counts and doublets provide a correct short-page null.",
       "experiments":["E009"],"status":"exact_sampler_used_for_short_pages",
       "result":"Exhaustive12-state multiplicity control passed; independent rejection shuffles avoid accepted-move chain bias.",
       "scope":"No claim of efficient sampling on long pages; original proposal-count MCMC remains unimplemented."},
      {"id":"H009","priority":1,"claim":"Known-word cyclic keys or number streams with arbitrary F interruptions recover unknown pages.",
       "experiments":["E007","E008","E009"],"status":"bounded_screen_no_supported_candidate",
       "result":"381keycycles,allphases,4signs;3numberstreams,256starts,4signs;allFsubsets exact DP; conditional null p0.25/0.95, page-adjusted1.",
       "scope":"Scorer limits preclude eliminating the whole cipher families; section alignment not yet tested."},
      {"id":"H010","priority":2,"claim":"Ciphertext-autokey exposes readable suffixes without knowing the seed.",
       "experiments":["E010"],"status":"bounded_screen_no_supported_candidate",
       "result":f"13516page/period/sign tasks; global plug-in p={autokey['global_p_plugin']}; exact synthetic control recovery.",
       "scope":"Periods1..64,min60suffixrunes,nointerruptions; null does not fix marginal counts."},
      {"id":"H011","priority":2,"claim":"Literal LP1-word seeds decrypt a plaintext-autokey page.",
       "experiments":["E011"],"status":"bounded_screen_no_supported_candidate",
       "result":"390seeds,171600recipes; strongest page null p0.15/0.375, adjusted1; exact synthetic full-grid control.",
       "scope":"Only none/all-F policies, no seed rotations, arbitrary-key search or continuation across pages."}]
    existing={h["id"] for h in hypotheses["hypotheses"]}
    hypotheses["hypotheses"].extend(h for h in entries if h["id"] not in existing)
    hypotheses.update(updated_at=now,status="Second direct-attack queue complete. No new decryption.",next_queue=[
      {"id":"H012","priority":1,"task":"Search section-continuous prime/totient keys across page boundaries with fixed source-defined section partitions.",
       "gate":"Explicit partitions and key consumption, synthetic crossing-page control, complete-search null, no arbitrary boundary tuning."},
      {"id":"H013","priority":2,"task":"Test source-pinned running text keys with explicit Latin-to-rune spelling conventions.",
       "gate":"Public text provenance, fixed title/offset grid, independent full-rule reproduction; no word-snippet success claims."},
      {"id":"H014","priority":3,"task":"Explore arbitrary plaintext-autokey seeds or selective interruptions beyond the dictionary baseline.",
       "gate":"Synthetic hidden-seed recovery, bounded search, unrelated language training if needed, matched selection-corrected null."},
      {"id":"H006","priority":4,"task":"Deferred image audit of the86doublets; required before claims relying on a specific glyph.",
       "gate":"Original-image coordinates and hashes, preserve uncertain variants."}])
    save("hypotheses.json",hypotheses)
    save("checkpoints/attack_phase2_complete.json",{"created_at":now,"summary":phase_summary,
         "research_state_sha256":sha("research_state.json"),"hypotheses_sha256":sha("hypotheses.json"),"records":phase})
    # This report is a new artifact; the first research report remains historical.
    report=f'''# Direkte Entschlüsselungsversuche: zweite Forschungsserie

Stand (UTC): {now}. **Keine neue Entschlüsselung nachgewiesen.**
Alle 55 ungelösten LP2-Runenseiten wurden in vier weiteren Chiffrensuchen geprüft.
LP2-50 bleibt als Zahlenseite im Korpus; diese Runenangriffe sind darauf nicht anwendbar.
Die erste Serie bleibt im [historischen Bericht](research_report.md) erhalten.

## Ergebnisse und Umfang

| Versuch | Tatsächlich untersuchter Suchraum | Ergebnis |
|---|---|---|
| E006 | Sechs getrennte LP1-Trainings-/Testabschnitte; 1.200 lokale Fehlvarianten; bekannte Schlüssel mit sämtlichen F-Teilmengen | Wahrer Text in 1.105 Fällen höher bewertet; ein Unterbrechungskontrollfall exakt, zwei nicht exakt |
| E007 | 381 primitive Schlüsselzyklen aus bekannten Wörtern, beide Wortreihenfolgen, alle Startphasen, vier Vorzeichen; {dictionary_tasks:,} Schlüssel-/Vorzeichenaufgaben, {phases:,} Phasen-/Vorzeichenkombinationen | Kein bestätigter Klartext |
| E008 | Primzahlen, p−1 und φ(n); Startoffset 0–255, vier Vorzeichen; {stream_tasks*256:,} Start-/Vorzeichenkombinationen | Kein bestätigter Klartext |
| E009 | Gleiche vollständige E007/E008-Suche auf jeweils 39 bedingt zufälligen Fassungen der ausgewählten Seiten LP2-55 und LP2-49 | p=0,25 bzw. 0,95; Bonferroni über 55 Seiten jeweils 1 |
| E010 | Ciphertext-Autokey: Perioden 1–64, vier Vorzeichen, mindestens 60 Runen hinter dem unbekannten Präfix; 13.516 Varianten | Globaler Modellvergleich über 999 Simulationen: p=0,464; synthetischer Kontrolltext exakt wiedergefunden |
| E011 | Plaintext-Autokey: 390 unveränderte Wortschlüssel einschließlich Rückwärtsfassungen, vier Vorzeichen, keine oder sämtliche F-Unterbrechungen; 171.600 Varianten | Ausgewählte LP2-49/55: p=0,15/0,375, seitenkorrigiert jeweils 1; synthetischer Kontrolltext exakt wiedergefunden |

E007 und E008 optimieren **sämtliche Teilmengen der F-Unterbrechungen** exakt
unter dem festgelegten Sprachmodell. F wird bei einer Unterbrechung unverändert
kopiert und verbraucht kein Schlüsselelement. Die Suche vereinigt nur Zustände mit
gleichem Schlüsselzeiger und gleichem Sprachkontext; sie benutzt keinen Beam-Cutoff.
Die kombinatorischen F-Masken sind in den oben genannten Zählungen nicht als
einzeln ausgeführte Versuche gezählt. Das Schema gilt nur für diese konkrete Familie.

E010 berechnet für i≥d die Folge P_i=(a·C_i+b·C_(i−d)) mod29. Das unbekannte
Präfix bleibt ausdrücklich offen. E011 hängt dagegen den gewonnenen Klartext
an den Startschlüssel an. Primitive Zyklusverkürzung wäre dort falsch; deshalb
werden die ursprünglichen 390 Wortschlüssel verwendet, nicht die 381 Vigenère-Zyklen.

## Kontrollen und Interpretation

Das Sprachmodell ist ein normalisiertes Trigramm-Backoff-Modell mit α=0,5 und
Stärke 5. Die Parameter wurden vor der Serie gespeichert. Die bekannte
CIRCUMFERENCE-Unterbrechungsregel wird mit separat trainiertem Modell exakt
gewonnen. Beim DIVINITY-Abschnitt stimmen 98,835 % der Runen; sechs sind falsch.
Auf LP2-56 bevorzugt der Score weiter F an Position 51 statt der richtigen 56.
LP2-56 ist ein bekannter Regressionstest und kein neuer Blindtest.

Die 1.105 von 1.200 erfolgreichen Mutationsvergleichen entsprechen 92,08 %,
sind aber korreliert. Das ist eine deskriptive Diagnose und kein Signifikanztest.
Ein hoher Score allein darf folglich keine Entschlüsselung bestätigen.

Die E009/E011-Vergleichstexte erhalten die exakten Runenhäufigkeiten und die
Zahl direkt benachbarter gleicher Runen. Unabhängige gleichverteilte Mischungen
werden verworfen, bis die Wiederholungszahl passt. Für diese kurzen Seiten ist
dies praktikabel und vermeidet das frühere Problem akzeptierter MCMC-Schritte.
Jeder Vergleich wiederholt die vollständige betreffende Schlüsselsuche;
Bonferroni über 55 Seiten berücksichtigt die Seitenauswahl. 39 Wiederholungen
können nach dieser Korrektur keine Signifikanz unter 0,05 auflösen. Hier dienen
sie zur Prüfung offensichtlicher Scheinbefunde, nicht zum Nachweis einer Lösung.

E010 maximiert in jeder Simulation über sämtliche Seiten, Perioden und
Vorzeichen. Sein symmetrisches Markov-Modell berücksichtigt den allgemeinen
Wiederholungsmangel, aber nicht die exakten Runenhäufigkeiten; die Unsicherheit
des geschätzten Parameters q wird nicht fortgepflanzt. Die Zusatzkorrektur über
die fünf neuen diagnostischen p-Werte wäre ebenfalls überall 1. Es wird keine
globale Entdeckung über die aufeinanderfolgenden Forschungsserien behauptet.

Die vollständigen besten Ausgaben enthalten keinen zusammenhängenden
überzeugenden Klartext. Sie bleiben als Kandidaten mit Rechenregel gespeichert.
Die Negativbefunde grenzen diese festen Suchräume und dieses Sprachmodell ein;
sie schließen Vigenère oder Autokey im Allgemeinen nicht aus.

## Reproduktion und Prüfung

```sh
python scripts/run_attack_phase.py --mode all --budget-seconds 900
python experiments/conditional_attack_null.py --page LP2-55 --seed 330100955
python experiments/conditional_attack_null.py --page LP2-49 --seed 330100949
python experiments/ciphertext_autokey_scan.py
python experiments/plaintext_autokey_attack.py
python scripts/finalize_attack_checkpoint.py
```

Die Runner überspringen identische abgeschlossene Fingerabdrücke mit gültiger
Ergebnisprüfsumme. Parameter, Quellen-Hashes, Seeds und Ergebnisse stehen im
[append-only Experimentprotokoll](../experiment_log.jsonl); vollständige Dateien
sind im [Checkpoint](../checkpoints/attack_phase2_complete.json) referenziert.
Die alten Ergebnisse und der erste Bericht wurden nicht umgeschrieben.

{test_count} Tests bestanden. Zusätzlich wurden {verified} gespeicherte Kandidaten
gegen den kanonischen Quelltext unabhängig nachgerechnet, bei vollständigen
Kandidaten auch zurückverschlüsselt. Scores wurden nochmals skalar geprüft.
Das bestätigt die Rechenregeln, **nicht** die sprachliche Richtigkeit der Ausgaben.

Diese Serie umfasst {len(phase)} abgeschlossene Prozesse mit zusammen
{phase_seconds:.3f} Sekunden gemessener Experimentzeit. Jeder Versuch hatte eine
Grenze von 180 Sekunden, die Serie eine Rechengrenze von 900 Sekunden. Simulationen
arbeiten seitenweise bzw. in Blöcken von 128. Die DP hält einen endlichen Zustandsraum
aus Schlüsselzeiger und zwei Runen Kontext; der Sprachcache ist auf 100.000 Einträge
begrenzt. Download-, Test- und Analysezeit sind separat. Keine Hintergrundarbeit läuft.

## Nächste direkte Angriffe

1. Schlüsselverbrauch über vorab quellenbegründete Seitengrenzen hinweg verfolgen,
   insbesondere Primzahl-/Totientfolgen mit F-Unterbrechungen.
2. Laufende Textschlüssel aus eingefrorenen öffentlichen Texten mit festgelegter
   Runenkodierung prüfen; Bücher und Offsetbereiche vor dem Lauf festlegen.
3. Plaintext-Autokey mit unbekannten Startschlüsseln bzw. selektiven F-Masken
   untersuchen, zuerst mit verdeckten synthetischen Schlüsseln kontrollieren.

Die größere Bildprüfung wurde entsprechend der Nutzerpriorität zurückgestellt.
Neue glyphenspezifische Behauptungen erfordern weiterhin die Originalbildprüfung.
'''
    (ROOT/"reports/attack_phase2_report.md").write_text(report,encoding="utf-8")
    print(json.dumps(phase_summary))


if __name__=="__main__":main()
