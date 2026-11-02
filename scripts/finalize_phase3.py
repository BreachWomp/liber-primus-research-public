"""Validate the third attack queue and preserve an independently resumable checkpoint."""
from datetime import datetime,timezone
import hashlib
import json
from pathlib import Path
import re
import subprocess
import sys
import numpy as np

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"experiments"))
from attack_support import model_without,to_indices,stream_catalog
from running_key_attack import source_keys


def load(path):return json.loads((ROOT/path).read_text(encoding="utf-8"))
def sha(path):return hashlib.sha256((ROOT/path).read_bytes()).hexdigest()
def save(path,obj):(ROOT/path).write_text(json.dumps(obj,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")


def main():
    if (ROOT/"checkpoints/phase4_complete.json").exists():
        raise RuntimeError("Historical finalizer: phase4 checkpoint already exists")
    now=datetime.now(timezone.utc).isoformat()
    check=subprocess.run([sys.executable,"-m","unittest","discover","-s","tests","-v"],cwd=ROOT,
                         capture_output=True,text=True,encoding="utf-8",timeout=60)
    validation=check.stdout+check.stderr
    (ROOT/"results/validation_phase3.txt").write_text(validation,encoding="utf-8")
    if check.returncode:raise RuntimeError(validation)
    count=int(re.search(r"Ran (\d+) tests",validation).group(1))
    events=[json.loads(line) for line in (ROOT/"experiment_log.jsonl").read_text(encoding="utf-8").splitlines()]
    completed=[e for e in events if e.get("status")=="completed"]
    phase_runs=[e for e in completed if 12<=int(e["experiment"][1:4])<=15]
    latest={e["experiment"]:e for e in phase_runs}
    expected={"E012-section-control","E013-running-key","E014-short-autokey","E015-differential-affine"}
    expected|={"E012-section-"+s["id"] for s in load("experiments/section_plan.json")["sections"]}
    null_names=[n for n in latest if n.startswith("E012-null-")]
    if len(null_names)!=1:raise RuntimeError("need exactly one registered section-null result")
    expected|=set(null_names)
    if set(latest)!=expected:raise RuntimeError("phase inventory incomplete")
    for event in phase_runs:
        if sha(event["output"])!=event["output_sha256"]:raise RuntimeError("modified output")
        for path,digest in event["input_dependencies"].items():
            if sha(path)!=digest:raise RuntimeError("modified experiment dependency "+path)
    results={name:load(e["output"]) for name,e in latest.items()}
    canonical={p["id"]:p for p in load("transcriptions/pages.json")};model=model_without()
    running,_=source_keys();verified=0
    for name,data in results.items():
        if name=="E012-section-control":continue
        if name.startswith("E012"):
            cipher="".join(canonical[p]["runes"] for p in data["section"]["page_ids"])
            assert cipher==data["ciphertext_runes"]
            rows=[{"ciphertext_runes":cipher,"top":data["top"]}]
        else:rows=data["pages"]
        for page in rows:
            values=to_indices(page["ciphertext_runes"])
            if "page" in page:assert page["ciphertext_runes"]==canonical[page["page"]]["runes"]
            candidates=page.get("top") or [page["top_suffix"]]
            for row in candidates:
                plain=to_indices(row["plaintext_runes"]);r=row["recipe"]
                if name.startswith("E015"):
                    assert len(plain)==len(values)-1
                    assert [(r["a"]*(values[i]-values[i-1])+r["b"])%29 for i in range(1,len(values))]==plain
                    out=[values[0]];inverse=pow(r["a"],-1,29)
                    for p in plain:out.append((out[-1]+inverse*(p-r["b"]))%29)
                else:
                    if name.startswith("E012"):key=stream_catalog(len(values)+256)[r["family"]]
                    elif name.startswith("E013"):key=running[r["key_stream"]]
                    else:key=list(r["key_indices"])
                    cursor=r.get("start",0);skips=set(r["skip_positions"]);out=[]
                    for i,p in enumerate(plain):
                        if i in skips:
                            assert p==0;out.append(0)
                        else:
                            ks=r.get("key_sign",r.get("feedback_sign"))
                            out.append((r["cipher_sign"]*(p-ks*key[cursor]))%29)
                            cursor+=1
                            if name.startswith("E014"):key.append(p)
                assert out==values
                assert abs(model.score(plain)-row["score"])<1e-10
                verified+=1
    section_null=results[null_names[0]]["null_calibration"]
    text=results["E013-running-key"];short=results["E014-short-autokey"];diff=results["E015-differential-affine"]
    section_control=results["E012-section-control"]
    pvalues=[section_null["bonferroni_10_sections"],text["null_calibration"]["bonferroni_55_pages"],
             short["null_calibration"]["bonferroni_55_pages"],diff["null_calibration"]["global_p_plugin"]]
    seconds=sum(e["wall_seconds"] for e in phase_runs)
    summary={"created_at":now,"experiment_groups":["E012","E013","E014","E015"],
             "completed_processes":len(phase_runs),"distinct_current_tasks":len(latest),"seconds":seconds,
             "max_process_seconds":max(e["wall_seconds"] for e in phase_runs),"budget_seconds":900,
             "section_start_sign_combinations":10*3*4*256,"running_key_recipes":text["evaluated_recipes"],
             "short_seed_recipes":short["evaluated_recipes"],"differential_affine_recipes":diff["evaluated_recipes"],
             "candidate_records_recomputed":verified,"tests_passed":count,"numpy":np.__version__,
             "phase_local_bonferroni4_p":[min(1,4*p) for p in pvalues],"new_decryptions":[],
             "duplicate_control_note":"E012control ran twice because default180 and explicit180.0 produced different fingerprints; same scientific parameters, not independent replication. Both immutable events retained and both times counted."}
    save("results/phase3_summary.json",summary)
    state=load("research_state.json")
    all_latest={e["experiment"]:e for e in completed}
    state.update(status="third_attack_batch_complete_no_new_decryption",updated_at=now,latest_report="reports/attack_phase3_report.md",
                 completed_experiments=[{"id":e["experiment"],"fingerprint":e["fingerprint"],"output":e["output"],"sha256":e["output_sha256"]} for e in all_latest.values()],
                 validation={"tests_passed":count,"path":"results/validation_phase3.txt","phase3_candidate_records_recomputed":verified},
                 session_budget={"phase":"third bounded direct-attack queue","max_compute_wall_seconds":900,"max_experiment_wall_seconds":180,"workers":1,"background_jobs":False},
                 resources={"recorded_successful_experiment_runs":len(completed),"recorded_experiment_subprocess_wall_seconds":sum(e["wall_seconds"] for e in completed),
                            "phase3_wall_seconds":seconds,"scope":"All recorded successful runs, including duplicate control, excluding tests/source retrieval/analysis."},
                 next_experiments=["H016","H017","H018"],new_decryptions=[],promising_candidates=[],
                 notes=["Primary decryption objective unresolved; no claimed new solution.",
                        "Three direct families plus structural differential test completed with null models and explicit controls.",
                        "Selective-F exact-language ranking remains unreliable; the synthetic section control misplaces one interruption.",
                        "Current checkpoint complete; no running processes. See phase3 report for source and search limits."])
    state["failed_approaches"]+=[s for s in [
        "E012 source-defined section-continuous streams: selected null p0.10, adjusted1; no supported plaintext.",
        "E013 Self-Reliance under two rune encodings: selected null p0.125, adjusted1; no supported plaintext.",
        "E014 exhaustive plaintext-autokey seeds1..3: selected null p0.375, adjusted1; no supported plaintext.",
        f"E015 differential-affine screen: global plug-in p{diff['null_calibration']['global_p_plugin']}; no new solution."] if s not in state["failed_approaches"]]
    save("research_state.json",state)
    hypotheses=load("hypotheses.json");present={h["id"] for h in hypotheses["hypotheses"]}
    new=[
      {"id":"H012","claim":"Prime/totient streams continue across source-defined LP2 sections.","experiments":["E012"],
       "status":"bounded_screen_no_supported_candidate","result":"10unique sections from2source partitions; allFsubsets and0..255starts; selected Markovnull p0.1, section-adjusted1.",
       "limits":"LP2-50 preserved with zero key consumption by hypothesis; known continuation exact, score-optimal interruption not exact."},
      {"id":"H013","claim":"Emerson Self-Reliance is a forward running key under one of2explicit GP conventions.","experiments":["E013"],
       "status":"bounded_screen_no_supported_candidate","result":f"{text['evaluated_recipes']}recipes; null p0.125,page-adjusted1; exact synthetic recovery.",
       "limits":"One edition/essay; no all-subsetF or backwardkey; no historical key claim."},
      {"id":"H014","claim":"A1..3rune arbitrary seed recovers a plaintext-autokey page.","experiments":["E014"],
       "status":"bounded_screen_no_supported_candidate","result":f"{short['evaluated_recipes']}recipes; null p0.375,page-adjusted1; exact synthetic recovery.",
       "limits":"None/allF only; longerseeds and cross-pagefeedback untested."},
      {"id":"H015","claim":"Affine substitution of first modular differences exposes plaintext and explains low ciphertext repeats.","experiments":["E015"],
       "status":"bounded_screen_no_supported_candidate","result":f"44660recipes; global plug-in p{diff['null_calibration']['global_p_plugin']}; exact synthetic recovery={diff['positive_control']['exact_top_one']}.",
       "limits":"No arbitrary substitution, higher-order difference, skips, or cross-page IV."}]
    hypotheses["hypotheses"].extend(h for h in new if h["id"] not in present)
    hypotheses.update(updated_at=now,status="Third direct-attack queue complete; no new decryption.",next_queue=[
      {"id":"H016","priority":1,"task":"Train a separate language/word-boundary scorer on pinned public English excluding the tested running-key essay; benchmark all known fixtures before new searches.",
       "gate":"Freeze normalization and model candidates, no unknown-page tuning, report full-word errors and exact selective-interruption recovery."},
      {"id":"H017","priority":2,"task":"Develop bounded search for longer plaintext-autokey seeds with hidden synthetic keys before applying to unknown pages.",
       "gate":"Recover keys of lengths4..12 in leave-one-section-out controls; strict runtime/evaluation cap and same optimizer on nulls."},
      {"id":"H018","priority":3,"task":"Revisit source-backed key clues and test only specifically justified text-key extensions or boundary rules.",
       "gate":"Distinguish actual manuscript evidence from thematic association; register title/encoding/offset choices before scans."},
      {"id":"H006","priority":4,"task":"Deferred image audit for any proposed glyph-specific rule.","gate":"Source image hashes and exact coordinates."}])
    save("hypotheses.json",hypotheses)
    save("checkpoints/phase3_complete.json",{"created_at":now,"summary":summary,"records":list(latest.values()),
         "research_state_sha256":sha("research_state.json"),"hypotheses_sha256":sha("hypotheses.json")})
    report=f'''# Dritte Forschungsserie: Abschnittsschlüssel, Textschlüssel und Autokey

Stand (UTC): {now}. **Keine neue Entschlüsselung bestätigt.**
Die vollständigen stärksten Ausgaben wurden geprüft; keine enthält überzeugenden
zusammenhängenden Klartext. Alle Versuche bleiben mitsamt Rechenregel erhalten.
Frühere Berichte: [Serie1](research_report.md), [Serie2](attack_phase2_report.md).

## Tatsächliche Angriffe

| Versuch | Abgedeckter Suchraum | Ergebnis |
|---|---|---|
| E012 | Zehn eindeutige quellenbasierte LP2-Abschnitte; Primzahlen, p−1, φ(n); vier Vorzeichen; Start0–255; sämtliche F-Teilmengen exakt optimiert | Stärkster Abschnitt LP2-00–02: p=0,10; über zehn Abschnitte korrigiert1 |
| E013 | Alle55ungelösten Runenseiten mit allen gültigen Startstellen in41.522Runen von Emersons Self-Reliance; zwei Kodierungen, vier Vorzeichen, keine/alleF | {text['evaluated_recipes']:,} Varianten; stärkste Seite LP2-49: p=0,125, seitenkorrigiert1 |
| E014 | Alle29+841+24.389Startschlüssel von1–3Runen; vier Vorzeichen, keine/alleF; alle55Seiten | {short['evaluated_recipes']:,} Varianten; LP2-55: p=0,375, seitenkorrigiert1 |
| E015 | P_i=a(C_i−C_(i−1))+b mod29, alle812invertierbaren affinen Abbildungen, jede der55Seiten | 44.660Varianten; globaler Modellvergleich p={diff['null_calibration']['global_p_plugin']} |

Die Varianten sind stark verwandt; diese Zahlen sind keine Anzahl unabhängiger
Beweise. Bei E012 kommen zu30.720Start-/Vorzeichenkombinationen die durch dynamische
Programmierung optimierten F-Teilmengen hinzu. E014 enumeriert Anfangsklartexte;
für jedes Vorzeichenpaar entspricht jeder davon genau einem Startschlüssel.
Dies wurde gegen die direkte Autokey-Rechnung geprüft.

## Quellen und Grenzannahmen

Die eingefrorene relikd-Quelle gruppiert LP2-54/55 separat, der iddqd-Index
behandelt54als Unterabschnitt des Kapitels ab40. Beide Einteilungen wurden vor
dem Lauf gespeichert; daraus ergeben sich zehn unterschiedliche Abschnitte.
Es wurde kein Abschnitt nach einem guten Score zugeschnitten.

LP2-50 wird mit ihrem Zahlenlayout und einer Nullbreite im Runenstrom erhalten.
**Null Schlüsselverbrauch ist hier eine Modellannahme**, keine Aussage über die
tatsächliche Funktion der Zahlenseite. Der Schlüssel und Sprachkontext laufen
über die übrigen Seitengrenzen weiter. Die Seitenstücke jeder Ausgabe bleiben
getrennt abrufbar.

Der Textschlüssel stammt aus der offiziellen [Gutenberg-Ausgabe2944](https://www.gutenberg.org/ebooks/2944).
Originaldatei einschließlich Kopf-/Lizenztext, Abrufzeit und SHA-256 stehen in
[Quellenmanifest](../sources/emerson_manifest.json) und `data/raw/gutenberg/pg2944.txt`.
Ausgewählt wurde ausschließlich Self-Reliance einschließlich Epigraph und
wiederholtem Titel. Es handelt sich um eine **thematische Hypothese**, nicht um
einen belegten Cicada-Schlüssel.

Kodiert wurden ASCII-Buchstabenwörter mit der vorhandenen gierigen GP-Regel
innerhalb jedes Worts. Zwei Q-Regeln: Q→C bzw. QU→CW und übrigesQ→C. Die nicht
ASCII-Lateinbuchstaben æ und é werden dabei ausgelassen und ausdrücklich
inventarisiert; die Quelldatei wurde nicht verändert. Andere Schreibweisen,
Rückwärtsrichtung, andere Bücher oder beliebige F-Teilmengen sind nicht abgedeckt.

## Kontrollbefunde und Grenzen der Aussage

E012 verschlüsselt einen bekannten, vom Training ausgeschlossenen LP1-Text
künstlich mit einem fortlaufenden Schlüssel und teilt ihn in drei Seiten.
Die gespeicherte Regel reproduziert die Seiten exakt, einschließlich verbrauchter
Schlüsselstellen. Der Sprachscore wählt jedoch F48stattF49 und erreicht nur
{100*section_control['character_accuracy']:.3f}% Runengenauigkeit. Das automatische
Entschlüsselungskriterium bleibt deshalb gesperrt.

Die synthetischen Kontrollfälle für E013, E014 und E015 werden im gesamten
jeweiligen Suchraum exakt als beste Ausgabe wiedergewonnen. Das zeigt
Erkennungsfähigkeit für diese konkreten Konstruktionen, nicht für jede
historische Chiffre. Bekannte LP2-56-Regressionsfehler bleiben unverändert.

E013/E014 verwenden39unabhängige Vergleichstexte mit exakten Runenhäufigkeiten
und exakter Zahl direkt benachbarter gleicher Runen. Jeder wiederholt die volle
Schlüsselsuche; Bonferroni55berücksichtigt die Auswahl der besten Seite. Diese
kleine Stichprobe dient zum Prüfen von Scheinbefunden und könnte eine korrigierte
Signifikanz unter0,05gar nicht auflösen. Bei null Überschreitungen wäre eine
größere registrierte Folgeprüfung nötig; dazu kam es hier nicht.

E012 nutzt39Simulationen des schon festgelegten symmetrischen Markov-Modells,
mit unabhängigen Kettenstarts an den tatsächlichen Seitengrenzen. E015 nutzt199
Simulationen und maximiert bei jedem Durchlauf über alle55Seiten und812Abbildungen.
Diese Modelltests erhalten die beobachteten Symbolhäufigkeiten nicht exakt;
Schätzunsicherheit von q wird nicht fortgepflanzt. Nach zusätzlicher Bonferroni-
Korrektur über die vier Diagnosen lauten die Werte {summary['phase_local_bonferroni4_p']}.
Es handelt sich weiterhin um explorative Forschung am bereits betrachteten Korpus.

Die negative Differenzprüfung betrifft nur die angegebene affine Abbildung.
Sie widerlegt nicht jede Chiffre mit Rückkopplung. E015 erweitert den früheren
E010-Suchraum um weitere Steigungen und additive Konstanten; es ist keine
unabhängige Replikation einer neuen Entdeckung.

## Validierung, Ressourcen und Fortsetzung

{count} Tests bestanden. {verified} gespeicherte Kandidatenaufzeichnungen wurden
erneut vom kanonischen Ciphertext aus geprüft, zurückverschlüsselt und skalar
nachbewertet. Dazu gehören drei erneut gespeicherte Ausgaben des für E012
ausgewählten Nullvergleichs. Die korrekte Rückrechnung bestätigt die Regel,
nicht die sprachliche Echtheit.

Insgesamt {len(phase_runs)} erfolgreiche Prozesse, {len(latest)} aktuelle Aufgaben,
{seconds:.3f} Sekunden gemessene Experimentzeit innerhalb des900Sekunden-Budgets.
Längster Prozess: {summary['max_process_seconds']:.3f} Sekunden, Grenze180.
NumPy{np.__version__}; kleine feste Arrayblöcke und jeweils nur ein Forschungsprozess.
Downloads, Tests und Analyse sind nicht in dieser Rechenzeit enthalten.

Ein Kontrolllauf wurde versehentlich zweimal gerechnet: `180` und `180.0`
erzeugten unterschiedliche Fingerabdrücke bei wissenschaftlich gleichen Parametern.
Beide historischen Ereignisse bleiben erhalten und beide Laufzeiten werden gezählt;
sie gelten nicht als zwei unabhängige Kontrollen. Die wiederholten Aufrufe der
gespeicherten Kommandos verwenden anschließend den vorhandenen Fingerabdruck.

```sh
python scripts/run_section_phase.py
python experiments/running_key_attack.py
python experiments/short_seed_autokey.py
python experiments/differential_affine.py
python scripts/finalize_phase3.py
```

Vollständige Ergebnisse und Hashes: [Checkpoint](../checkpoints/phase3_complete.json),
[Experimentprotokoll](../experiment_log.jsonl), [Forschungsstand](../research_state.json).
Keine unbeaufsichtigten Prozesse laufen.

Als Nächstes: einen unabhängig trainierten Wort-/Sprachscore gegen die verbleibenden
Unterbrechungsfehler prüfen und damit längere unbekannte Autokey-Startschlüssel
in begrenzten, synthetisch kontrollierten Suchen angehen. Weitere Textschlüssel
sollen durch konkrete Quellenhinweise begründet werden.
'''
    report=re.sub(r"(?<=\d)(?=[A-Za-zÄÖÜäöü])"," ",report)
    for before,after in [("Alle55","Alle 55"),("alle55","alle 55"),("alle812","alle 812"),
                         ("nach55","nach 55"),("über55","über 55"),("zu30","zu 30"),
                         ("von1","von 1"),("genau einem","genau einem"),("Ausgabe2944","Ausgabe 2944"),
                         ("mit39","mit 39"),("nutzt39","nutzt 39"),("nutzt199","nutzt 199"),
                         ("Bonferroni55","Bonferroni 55"),("unter0","unter 0"),("des900","des 900"),
                         ("Grenze180","Grenze 180"),("NumPy2","NumPy 2"),("behandelt54","behandelt 54"),
                         ("ab40","ab 40"),("alle29","alle 29"),("Alle29","Alle 29")]:
        report=report.replace(before,after)
    (ROOT/"reports/attack_phase3_report.md").write_text(report,encoding="utf-8")
    print(json.dumps(summary))


if __name__=="__main__":main()
