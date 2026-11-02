"""Validate immutable phase-four outputs and publish the resumable research state."""
from collections import Counter
from datetime import datetime,timezone
import hashlib
import json
from pathlib import Path
import re
import subprocess
import sys

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"experiments"))
from attack_support import to_indices,stream_catalog
from external_language import external_model

def load(path):return json.loads((ROOT/path).read_text(encoding="utf-8"))
def sha(path):return hashlib.sha256((ROOT/path).read_bytes()).hexdigest()
def save(path,data):(ROOT/path).write_text(json.dumps(data,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")

def main():
    if (ROOT/"checkpoints/phase5_complete.json").exists():
        raise RuntimeError("Historical finalizer: use the latest phase checkpoint")
    check=subprocess.run([sys.executable,"-m","unittest","discover","-s","tests","-v"],cwd=ROOT,
                         capture_output=True,text=True,encoding="utf-8",timeout=60)
    validation=check.stdout+check.stderr
    (ROOT/"results/validation_phase4.txt").write_text(validation,encoding="utf-8")
    if check.returncode:raise RuntimeError(validation)
    count=int(re.search(r"Ran (\d+) tests",validation).group(1))
    events=[json.loads(s) for s in (ROOT/"experiment_log.jsonl").read_text(encoding="utf-8").splitlines()]
    completed=[e for e in events if e.get("status")=="completed"]
    phase=[e for e in completed if 16<=int(e["experiment"][1:4])<=18]
    latest={e["experiment"]:e for e in phase}
    for event in phase:
        assert sha(event["output"])==event["output_sha256"]
        for path,digest in event["input_dependencies"].items():assert sha(path)==digest,path
    data={k:load(e["output"]) for k,e in latest.items()}
    canonical={p["id"]:p for p in load("transcriptions/pages.json")}
    fixtures={f["id"]:f for f in load("known_solutions/fixtures.json")}
    models={order:external_model(order) for order in (3,4)};verified=0
    def verify(row,values,order=4,autokey=False):
        nonlocal verified
        plain=to_indices(row["plaintext_runes"]);r=row["recipe"]
        assert len(plain)==len(values)
        key=list(r["key_indices"]) if r.get("key_indices") is not None else stream_catalog(len(values)+256)[r["family"]]
        cursor=r.get("start",0);skips=set(r["skip_positions"]);out=[]
        for i,p in enumerate(plain):
            if i in skips:assert p==0;out.append(0)
            else:
                k=key[cursor%len(key)] if r.get("family")=="vigenere" else key[cursor]
                out.append((r["cipher_sign"]*(p-r.get("key_sign",r.get("feedback_sign"))*k))%29)
                cursor+=1
                if autokey:key.append(p)
        assert out==values
        assert abs(models[order].score(plain)-row["score"])<1e-10
        if autokey:assert abs(models[3].score(plain)-row["trigram_score"])<1e-10
        verified+=1
    benchmark=data["E016-external-language"]
    for result in benchmark["results"]:
        assert len(result["known_key_decodings"])==3
        for row in result["known_key_decodings"]:
            fixture=fixtures[row["fixture"]]
            verify(row,to_indices(fixture["ciphertext_runes"]),result["order"])
            assert row["plaintext_runes"]==fixture["plaintext_runes"] and row["exact"]
    families={}
    for prefix in ("E017","E018"):
        control=data[prefix+"-controls"]
        assert control["gate_passed"]
        for c in control["controls"]:
            values=c.get("ciphertext_indices") or to_indices(fixtures[c["fixture"]]["ciphertext_runes"])
            assert c["exact"] and c["top"][0]["plaintext_runes"]==fixtures[c["fixture"]]["plaintext_runes"]
            for row in c["top"]:verify(row,values,autokey=prefix=="E017")
        pages=[];nulls=[]
        for ident,result in data.items():
            if not ident.startswith(prefix) or ident.endswith("controls"):continue
            if "-pages-" in ident:pages+=result["pages"]
            if "null_calibration" in result:nulls.append(result)
            for page in result["pages"]:
                assert page["ciphertext_runes"]==canonical[page["page"]]["runes"]
                for row in page["top"]:verify(row,to_indices(page["ciphertext_runes"]),autokey=prefix=="E017")
        assert len(pages)==len({p["page"] for p in pages})
        if prefix=="E018" and not nulls:
            families[prefix]={"pages":len(pages),"exact_controls":len(control["controls"]),
                "status":"partial_budget_checkpoint","p":None,"page_adjusted_p":None,
                "remaining_pages":sorted(p["id"] for p in canonical.values() if p["edition"]=="LP2" and p["page"]<=55 and p["runes"] and p["id"] not in {q["page"] for q in pages}),
                "null_pending":True}
            continue
        assert len(pages)==55 and len(nulls)==1
        winner=max(pages,key=lambda p:p["top"][0]["score"])
        null=nulls[0];assert null["pages"][0]["page"]==winner["page"]
        values=to_indices(winner["ciphertext_runes"]);cal=null["null_calibration"]
        doubles=lambda x:sum(a==b for a,b in zip(x,x[1:]))
        for r in cal["runs"]:
            assert Counter(r["ciphertext_indices"])==Counter(values)
            assert doubles(r["ciphertext_indices"])==doubles(values)
        p=(1+sum(r["score"]>=winner["top"][0]["score"] for r in cal["runs"]))/20
        assert len(cal["runs"])==19 and p==cal["monte_carlo_p"]
        assert min(1,55*p)==cal["bonferroni_55_pages"]
        families[prefix]={"pages":55,"exact_controls":len(control["controls"]),"selected":winner["page"],
            "score":winner["top"][0]["score"],"transliteration":winner["top"][0]["transliteration"],
            "p":p,"page_adjusted_p":min(1,55*p),"phase_adjusted_p":min(1,110*p)}
    seconds=sum(e["wall_seconds"] for e in phase)
    budget_record=load("checkpoints/phase4_budget.json") if (ROOT/"checkpoints/phase4_budget.json").exists() else {}
    if budget_record:assert budget_record["combined_conservative_seconds"]<=900
    assert seconds<=900 and max(e["wall_seconds"] for e in phase)<=180
    now=datetime.now(timezone.utc).isoformat()
    summary={"created_at":now,"experiment_groups":["E016","E017","E018"],"completed_processes":len(phase),
        "seconds":seconds,"max_process_seconds":max(e["wall_seconds"] for e in phase),"budget_seconds":900,
        "candidate_records_recomputed":verified,"tests_passed":count,"source":benchmark["source"],
        "mutation_comparisons":{str(r["order"]):[r["correct_strictly_better"],r["comparisons"]] for r in benchmark["results"]},
        "families":families,"budget_audit":budget_record,"new_decryptions":[]}
    save("results/phase4_summary.json",summary)
    state=load("research_state.json");all_latest={e["experiment"]:e for e in completed}
    partial=families["E018"].get("null_pending",False)
    status="fourth_batch_budget_checkpoint_E018_pending" if partial else "fourth_attack_batch_complete_no_new_decryption"
    state.update(status=status,updated_at=now,latest_report="reports/attack_phase4_report.md",
        completed_experiments=[{"id":e["experiment"],"fingerprint":e["fingerprint"],"output":e["output"],"sha256":e["output_sha256"]} for e in all_latest.values()],
        validation={"tests_passed":count,"path":"results/validation_phase4.txt","phase4_candidate_records_recomputed":verified},
        session_budget={"phase":"fourth bounded research queue","max_compute_wall_seconds":900,"max_experiment_wall_seconds":180,"workers":1,"background_jobs":False},
        resources={"recorded_successful_experiment_runs":len(completed),"recorded_experiment_subprocess_wall_seconds":sum(e["wall_seconds"] for e in completed),"phase4_wall_seconds":seconds,"phase4_budget_audit":budget_record},
        new_decryptions=[],promising_candidates=[],next_experiments=(["E018-resume"] if partial else [])+["H020","H021","H018"],
        notes=["Primary objective unresolved; no new decryption.","External-only language model passes three exact selective-F known controls; previously seen controls, not blind validation.","E017 complete with conditional null; see E018 coverage and pending calibration in phase4 summary.","No running processes at checkpoint."])
    for k,v in families.items():
        if v.get("null_pending"):continue
        note=f"{k}: selected {v['selected']} null p={v['p']}, page-adjusted={v['page_adjusted_p']}; no supported plaintext."
        if note not in state["failed_approaches"]:state["failed_approaches"].append(note)
    save("research_state.json",state)
    hypotheses=load("hypotheses.json")
    additions=[{"id":"H016","claim":"External-only language training resolves previously ambiguous F interruptions.","experiments":["E016"],"status":"known_control_gate_passed","result":"Both fixed models exactly recover all three known-key controls; order3 1542/1600, order4 1563/1600 mutation rankings.","limits":"Previously seen fixtures, correlated mutations; data-independent training is not blind validation. No word-boundary scorer implemented."},
        {"id":"H017","claim":"Bounded search can recover unknown plaintext-autokey seeds of length4..12.","experiments":["E017"],"status":"controls_passed_no_supported_unknown_candidate","result":families["E017"],"limits":"Six unskipped synthetic controls; beam heuristic with none/allF only. No exhaustive family exclusion."},
        {"id":"H019","claim":"External4gram scoring finds a supported unknown result in the prior selective-F word/number grids.","experiments":["E018"],"status":"partial_budget_checkpoint" if partial else "controls_passed_no_supported_unknown_candidate","result":families["E018"],"limits":"Changed-score rescan, not independent replication or new cipher family. Pending pages/null are not negative results."}]
    present={h["id"] for h in hypotheses["hypotheses"]}
    hypotheses["hypotheses"].extend(h for h in additions if h["id"] not in present)
    hypotheses.update(updated_at=now,status=status,next_queue=([{"id":"E018-resume","priority":0,"task":"Resume selective driver, skip completed fingerprints and finish remaining pages plus full-grid null calibration.","gate":"Keep all registered dependencies and scientific parameters unchanged; new bounded runtime allocation required."}] if partial else [])+[
        {"id":"H020","priority":1,"task":"Test affine plaintext-feedback recurrences beyond the four sign choices, first with hidden synthetic keys and a fixed computational gate.","gate":"Preregister coefficients and short seed lengths; full optimizer on conditional nulls; derive which cases duplicate E014/E017 before computing."},
        {"id":"H021","priority":2,"task":"Test a small source-defined set of reading orders using verified page layouts before combining with cipher scans.","gate":"Audit line/column boundaries against preserved images, include non-rune pages, fix permutations before language scoring and correct over orders."},
        {"id":"H018","priority":3,"task":"Revisit source-backed key clues; test only specifically justified text-key extensions.","gate":"Manuscript evidence distinguished from thematic association; register text and encoding choices."}])
    save("hypotheses.json",hypotheses)
    checkpoint={"created_at":now,"status":state["status"],"summary":"results/phase4_summary.json","summary_sha256":sha("results/phase4_summary.json"),
        "experiments":[{"id":e["experiment"],"fingerprint":e["fingerprint"],"output":e["output"],"sha256":e["output_sha256"]} for e in phase],
        "tests":count,"new_decryptions":[],"resume":"Read research_state.json and hypotheses.json; completed fingerprints must be skipped."}
    save("checkpoints/phase4_complete.json",checkpoint)
    e18=families["E018"]
    coverage=(f"{e18['pages']}/55 Seiten abgeschlossen; übrige Seiten und Nullvergleich ausstehend. "
              "Das Budget beendet die Serie, nicht die wissenschaftliche Prüfung dieser Familie.") if partial else (
              f"55/55 Seiten und Nullvergleich abgeschlossen; p={e18['p']}, seitenkorrigiert {e18['page_adjusted_p']}.")
    report=f'''# Vierte Forschungsserie: Sprachmodell und längere Autokey-Schlüssel

Stand (UTC): {now}. **Keine neue Entschlüsselung bestätigt.**
Der Fortschritt ist methodisch: Die bisherigen Fehler bei bekannten
F-Unterbrechungen werden mit einem unabhängig trainierten Sprachmodell behoben.
Der abgeschlossene Angriff auf unbekannte Autokey-Schlüssel liefert keinen
belastbaren Klartext. Die erneute selektive Schlüsselsuche ist separat ausgewiesen.

## Sprachmodell und Kontrollen (E016)

Die unveränderte, bereits gepinnte [Gutenberg-Ausgabe 2944](https://www.gutenberg.org/ebooks/2944)
liefert 265.129 Runen in 393 Absätzen aus elf Emerson-Essays.
Self-Reliance ist vollständig ausgeschlossen, weil dieser Text in E013 als
Schlüssel getestet wurde. Kein Liber-Primus-Klartext oder -Ciphertext wird zum
Training verwendet. Das [Quellenmanifest](../sources/emerson_manifest.json)
enthält Abrufzeit und SHA-256; Abschnittsgrenzen stehen in den Ergebnissen.

Die explizite Verarbeitung erweitert ae/oe-Ligaturen, entfernt kombinierende
Akzente nach NFKD, liest ASCII-Wörter, ersetzt QU durch CW und übriges Q durch C
und verwendet die vorhandene gierige GP-Kodierung innerhalb jedes Worts.
Nichtlateinische Buchstaben sind inventarisiert und werden nicht kodiert.
Absatzgrenzen werden beim N-Gramm-Training nicht überschritten. Die Quelldatei
selbst bleibt unverändert. Ein eigener Wortgrenzen-Score wurde nicht implementiert.

Zwei vorab festgelegte Backoff-Modelle (Ordnung 3 und 4, alpha=0,5, Stärke=5)
gewinnen **alle drei bekannten selektiven Kontrollfälle exakt** zurück:
DIVINITY, CIRCUMFERENCE und LP2-56. Einschließlich der richtigen F-Unterbrechungen;
LP2-56 verwendet ausschließlich die Unterbrechung an Runenoffset 56 (nullbasiert).
Mit bekannten Schlüsseln werden alle Phasen beziehungsweise Starts 0–255 durchsucht.

Bei je 200 Mutationen an acht unstrittigen Kontrolltexten wird der echte Text
1542/1600-mal (Ordnung 3) beziehungsweise 1563/1600-mal (Ordnung 4) höher bewertet.
Die Mutationen sind korreliert; dies sind deskriptive Werte, keine p-Werte.
Die früheren 1105/1200 Vergleiche betrafen einen anderen Kontrollumfang und sind
kein direkt vergleichbarer Ausgangswert. Alle LP-Kontrollen waren bereits bekannt:
unabhängige Trainingsdaten bedeuten **keine neue blinde Validierung**.

## Unbekannte Autokey-Startschlüssel (E017)

Alle 55 unbekannten LP2-Runenseiten wurden mit Schlüssellängen 4–12, vier
Vorzeichenkombinationen und den Regeln keine/alle F-Unterbrechungen geprüft.
Die Suche zerlegt die Klartextrückkopplung in zyklische Trigramm-Faktoren.
Pro Erweiterung bleiben höchstens 512 Pfade; alle zyklischen Schnitte werden
versucht, die besten 16 Kandidaten je Schnitt anschließend mit dem Viergramm-
Modell bewertet. **Dies ist eine begrenzte Heuristik, keine vollständige Suche
über alle 29^12 Schlüssel.**

Sechs synthetische Kontrollen (zwei bekannte LP1-Texte, jeweils zufällige Schlüssel
der Längen 4, 8 und 12; Seed 3301017) wurden im vollständigen Suchraster exakt
als beste Ausgabe gefunden. Der Suche wurden weder Schlüssel noch wahre Länge
übergeben. Die injizierten Kontrollen haben keine Unterbrechungen; sie validieren
nicht jede mögliche Unterbrechungsregel oder Textverteilung.

Stärkster unbekannter Kandidat: LP2-49, Score {families['E017']['score']:.6f}.
Seine vollständige Ausgabe lautet:

```text
{families['E017']['transliteration']}
```

Das ist kein zusammenhängender Klartext. Drei von 19 unabhängigen Zufallstexten
mit genau denselben Runenhäufigkeiten und derselben Anzahl benachbarter gleicher
Runen erreichen mindestens diesen Score. Jeder Zufallstext durchläuft dieselbe
vollständige Optimierung und Nachbewertung. Plus-eins-p=0,20, nach Bonferroni über
55 Seiten p=1. Die Auswahl zwischen den zwei Angriffsfamilien ändert das Ergebnis
nicht. Die geringe Zahl von Nullreplikaten könnte korrigierte Signifikanz ohnehin
nicht auflösen; bei null Überschreitungen wäre eine größere registrierte Prüfung nötig.
Seedlängen außerhalb 4–12, beliebige F-Teilmengen und Seitenfortsetzung bleiben offen.

## Erneute selektive Wort-/Zahlenstromsuche (E018)

381 kanonische Wortschlüsselzyklen mit allen Phasen, drei Zahlenströme
(Primzahlen, Primzahlen minus eins, ganzzahlige Totienten), Starts 0–255,
vier Vorzeichen und sämtliche F-Teilmengen werden mit dem neuen Viergramm-Score
geprüft. Die dynamische Programmierung optimiert die Unterbrechungen exakt
innerhalb dieses endlichen Rasters. Anders als E016 umfasst die Kontrolle den
gesamten Wort-/Zahlenstromkatalog: erneut **3/3 exakt**.

**Abdeckung: {coverage}**
Dies ist eine Wiederaufnahme von E007/E008 mit verändertem Trainingsmaterial
und Score, keine neue Chiffrenfamilie oder unabhängige Entdeckung.
Nicht kalibrierte Teilresultate gelten nicht als statistisch negativer Befund.
LP2-50 bleibt als Zahlenseite mit Layout im Korpus erhalten und wird hier nicht
als Runenseite analysiert.

## Validierung und Ressourcen

{count} Tests bestanden. {verified} gespeicherte Kandidatenaufzeichnungen wurden
mit einer separaten Rückrechnung erneut gegen ihren kanonischen Ciphertext
geprüft und skalar nachbewertet; bekannte Kontrollen wurden ebenfalls geprüft.
Die Rückrechnung beweist die angegebene Transformation, nicht die Echtheit des Klartexts.
Ausgabedateien und registrierte Abhängigkeiten stimmen mit ihren SHA-256 überein.

{len(phase)} erfolgreiche Experimentprozesse, {seconds:.3f} Sekunden darin;
längster erfolgreicher Prozess {summary['max_process_seconds']:.3f} Sekunden.
Das Serienbudget beträgt 900 Sekunden, die Einzelgrenze 180 Sekunden.
Der 400-Sekunden-Rahmen für E018 endete während LP2-35–39 nach weiteren
8,646 Sekunden; diese unvollständige Gruppe wurde beendet und als abgebrochen
protokolliert. Sie wird bei der Fortsetzung erneut berechnet. Einschließlich
Orchestrierung, Abbruch und zwei Sekunden konservativer Beendigungsreserve
liegt die Serienabrechnung bei 891,052 Sekunden. Details im
[Budgetprotokoll](../checkpoints/phase4_budget.json); erfolgreiche Laufzeiten
werden darin nicht doppelt gezählt. Ein Forschungsprozess gleichzeitig; feste Beam-/Array-
Größen und begrenzter Modellcache. Tests, Datenlektüre und Dokumentation sind
nicht in der Experimentzeit enthalten. Keine Hintergrundaufgabe läuft weiter.

[Ergebnisübersicht](../results/phase4_summary.json),
[Checkpoint](../checkpoints/phase4_complete.json),
[Forschungsstand](../research_state.json),
[Experimentprotokoll](../experiment_log.jsonl).
Der Dateiname des Checkpoints bezeichnet die gespeicherte Serie; der Status
im Inhalt unterscheidet fertige Experimente von ausstehender Arbeit.

Zur Fortsetzung zuerst E018 mit unveränderten Parametern abschließen; der Runner
überspringt nachgewiesen fertige Fingerabdrücke. Danach: allgemeinere affine
Rückkopplung mit synthetischer Kontrollschranke und eine kleine, anhand der
Quellenbilder begründete Menge alternativer Leserichtungen prüfen.
Historische Berichte und erfolglose Ergebnisse bleiben erhalten.
'''
    (ROOT/"reports/attack_phase4_report.md").write_text(report,encoding="utf-8")
    print(json.dumps({k:v for k,v in summary.items() if k!="source"},ensure_ascii=True))

if __name__=="__main__":main()
