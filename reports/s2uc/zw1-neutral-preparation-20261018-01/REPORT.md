# ZW1: getrennte Implementierung und neutrale Qualifikation

2026-10-18 · Workflow 1fd2d773-77de-4aa3-b007-bceafa588386.
Status: Implementierungs-/Neutralpaket abgeschlossen, zur Abnahme. Keine Forschungsvorbereitung oder Forschungsfreigabe daraus ableiten.

## Umsetzung und Grenzen

Neue Dateien ausschließlich unter experiments/zw1: sources.py, statistics.py, matrix.py, integration.py, test_package.py, qualify.py und MATRIX_RECIPE.md. Historische E/F-Implementierungen, U-Auswahl, Feedback, Budgets, Decoder und Referenzen wurden nicht geändert. Die neutrale Integration verwendet den bestehenden policy_case mit neutral=True und höchstens 128 Frames; sie hat keinen Forschungsstartpfad.

sources.py implementiert beide gekoppelten Hinweisfolgen und eine getrennte SHA-/Cursor-/Übergangsrekonstruktion. Die neutrale Quelle heißt MCM-ZW1/neutral/v1. Forschungsanforderungen werden vor Erzeugung abgewiesen. Material an die Policy enthält nur catalog und ids; Paar, Bedingung, Orientierung, Phase und Generatorzustand bleiben außerhalb der Policy. Der bestehende Arm erhält lediglich seine unveränderten Scope-/Ordinaldaten und Wahrnehmungsframes.

Die Typo-Verbindung zweier Sätze in Punkt 3 des angenommenen Konzeptvertrags wurde nicht stillschweigend verändert: implementiert ist das dort mathematisch eindeutig festgelegte B_b=U_b mod 4. Quotient und Rest sind unabhängig; die reale Paarung beruht insbesondere auf gemeinsamem Anfangshinweis und Flipstrom. Ein gemeinsamer Zufallsstrom garantiert keine geringere Varianz.

## Quellen- und Matrixqualifikation

20/20 fokussierte Unitprüfungen bestanden (vollständige IDs und Ausgabe in tests.json/tests.log). Quellenprüfungen umfassen alle vier Vorgänger × sämtliche 24 Ziehungswerte: A jeweils 12/24 Selbstübergänge und 4/24 zu jedem anderen Hinweis, B jeweils 6/24 pro Hinweis; die gemeinsame Übergangstabelle wird exakt geprüft. Gemeinsamer Anfangshinweis, unabhängige Rekonstruktion, Flipkopplung beider Orientierungen, Phasengrenze 128/129, Materialisierung und Abbruch nach 4096 verworfenen Ziehungen sind geprüft. Forschungsanforderungen schlagen fehl.

Für diese reinen Quellentests wurden zwei neutrale 256-Block-Quellenpaare generiert und rekonstruiert; ihre vollen Framefolgen wurden keiner Policy übergeben. Das sind keine Forschungsquellen. Die Integration nutzt ausschließlich 24 Blöcke/96 Frames je Arm.

MATRIX_RECIPE.md wurde vor Matrixerzeugung geschrieben. Fester Namensraum MCM-ZW1/bootstrap/v1; SHA-Schlüssel pro Zeile/Spalte, ohne wählbaren Seed oder Outcome-Eingabe. Genau eine 160000-Byte-Matrix mit 10000 Zeilen ×16 Paarindizes erzeugt, acht Indizes je Orientierung. Eine zweite Implementierung bestätigt alle Bytes, Größe und Schichtzuordnung. Mutation und falsche Schicht werden abgewiesen. Keine Matrixauswahl nach Ergebnissen.

Matrix-SHA256: `cd452bee76ea2b1b64c920afdd9c70211e5ba7abc7207049f4e7e280e5703f6c`.
Rezept-SHA256: `bc4cc1bf0f2ea451da18060eea4548e8b1386d3a5a2e27c63a831fc661030ba6`.
Bindung und zeitliche Reihenfolge stehen in matrix-binding.json.

## Einziger Primärkontrast und unabhängige Referenz

statistics.py verwendet ausschließlich I=Mittel_r[(E−F)_A−(E−F)_B], 16 vollständige Paare, je Bedingung sämtliche Ziele 3,5,…,1023. Vollnenner: 511 je Geschichte, 8176 E/F-Zielpaare je Bedingung, 16352 zusammen, 32704 einzelne Fehlerwerte. Keine warme oder günstige Teilgruppe ersetzt diesen Nenner.

Die Hauptrechnung bildet zuerst die 16 Paardifferenzen. Die getrennte Referenz summiert die vier Armreihen separat und rekonstruiert die Bootstrapstichproben über ganzzahlige Paargewichte. Beide kontrollieren Paar-/Bedingungsidentität, vollständige Zielmengen und Quittungen. Alle vier Ausführungen bleiben beim Resampling zusammen. Das 95%-Perzentilintervall nutzt rationale Summen und die vorgegebene Interpolation. Negative/positive Interaktion sowie Nullberührung sind getestet, ebenso heterogene Paare, fehlende Paare/Ziele/Armwerte, vertauschte Bedingungen, überkreuzte Paarzuordnung und unvollständige Quittungen.

Acht vollständige künstliche Bootstrapauswertungen (Haupt-/Referenzrechnungen) verwendeten dieselbe gebundene Matrix; keine Forschungsfehler wurden eingelesen, keine neue Matrix nach Ergebnissen erzeugt. Bei gemeinsam variierenden Armwerten und exakt verschwindender Interaktion liefern beide Verfahren [0,0]; getrenntes Resampling der Bedingungen wäre hier falsch.

## Tatsächliche neutrale Integration

Drei gezielte Abläufe, alle unter hartem 512-MiB-Windows-Job:

| Ablauf | Policy-Arme | bestandene Live-Referenzen | bestandene Arm-Archivreferenzen | Paarquittungen |
|---|---:|---:|---:|---|
| complete: zwei kurze Paare | 8 | 8 | 8 | 1,2 |
| archive_failure: ungültiger Anker in Paar 2/B | 8 | 8 | 6 | nur 1 |
| source_failure: Quelle nach Versiegelung verändert | 0 | 0 | 0 | keine |
| Gesamt | 16 | 16 | 14 | drei vollständige neutrale Paarquittungen |

Alle 16 Arme bearbeiteten jeweils genau 96 Frames, ohne zusätzliche Messarme. Es gab acht Archivverifier-Aufrufe für je E/F: sieben vollständig bestanden; der achte wurde durch den echten Prüfer mit PRIOR_RECORD_HASH vor erfolgreicher semantischer Rekonstruktion abgewiesen. Der Zähler archive_reference_started=16 bezeichnet Arm-Prüfplätze dieser acht Aufrufe, nicht 16 erfolgreich durchgeführte Rekonstruktionen.

Vor dem ersten Arm liegen pro Ablauf alle vier neutralen Bedingungsquellen geprüft und versiegelt vor. Vor jeder Bedingung und jeder Armerzeugung werden die Quellenbindungen kontrolliert. Der Frischewächter prüft leeren Startbestand, fehlenden Kandidaten, akzeptierte Framezahl 0 und unterschiedliche Objektidentitäten. Jede Bedingung erzeugt genau zwei neue Arme; eine vollständige Paarquittung benötigt beide unabhängigen Archivprüfungen und Cleanup, also vier frische Arme je Paar.

Der Archivfehler lässt Paar 2 unquittiert, obwohl seine Policy-Arme beendet sind. Quellenveränderung stoppt vor jeder Policy-Ausführung mit SOURCE_CHANGED. Alle erzeugten Arme sind geschlossen und ihre Bank geleert; Codec freigegeben, keine Partialdateien. Die reservierten Terminalslots sichern erste Ursache und Fortschritt. Beide unvollständigen Verläufe sowie die kurzen vollständigen Paare werden von der Forschungsstatistik abgewiesen; kein vollständiges Forschungsurteil aus Teilpaaren.

Qualifikation lief in einem einzigen Prozess, Exitcode 0. Die generischen Terminalfelder worker_ended/worker_started sind hier kein Nachweis einer separaten Workerüberwachung: es wurde kein Forschungs-Supervisor/Worker-Paar gestartet. Eine solche Start-/Deadline-/Berechtigungsintegration bleibt dem gesonderten Forschungsvorbereitungspaket vorbehalten. Kein falscher Erfolgsstatus aus den absichtlich abgebrochenen Negativfällen.

## Ressourcen: gemessen, geplant, offen

Gemessen für das vollständige Paket: 49,275 s, Jobpeak 50348032 Bytes (rund 48,02 MiB). Kurze Integration: maximal 15974 Bytes gzip, 83044 encoded, 78162 dictionary, 1686 nodes, 8890 edges, 955 indices, 14 Collections und 16781 Bytes Record. Die harten bestehenden Ledger-/Codec-/Jobgrenzen gelten unverändert; Grenzwerte stehen vollständig in resource-plan.json.

Lineare Kurzfallprojektion je 1024-Frame-Geschichte: gzip 170390 Bytes, encoded 885803, dictionary 833728, nodes 17984, edges 94827, indices 10187, Observer etwa 4,86 MB. Lineare Zeit für 32 Geschichten etwa 2000,72 s; vorsichtiger Ansatz Faktor acht plus 600 s = 16606 s, zuzüglich 3600 s Reserve. Dies sind Planwerte, keine Vollgrößenqualifikation. Insbesondere enthalten die kurzen Paare keine langen Erhaltungszeugen; die winzige lineare Mechanismenprojektion ist keine tragfähige Speicherzusage.

Der tatsächliche ER1-Peak von 432316416 Bytes (412,29 MiB) ist der relevante Vergleichspunkt. Bis zur 512-MiB-Grenze verbleiben nur 104554496 Bytes (99,71 MiB), nicht eine frei verfügbare garantierte Reserve. Historisch wurden Observer bis 4947590 Bytes und Mechanismen bis 64087 Bytes beobachtet. Neue B-Folgen können Kompression, Kandidatenwechsel und Herkunftsketten verändern. Der Speicherpeak darf nicht proportional aus 96 Frames extrapoliert oder allein aus 64 Armen abgeleitet werden.

Plan: Bedingungen seriell, Archivprüfung und Codec-Cleanup vor nächster Bedingung; nur kompakte Fehlerreihen für den späteren Interaktionsvergleich behalten. Keine parallelen vier Armarchive. Die neue Paarhülle verwirft den umfangreichen Fallreport nach Extraktion der Fehlerreihen und ruft GC auf. Ob das in voller Größe im gemeinsamen 512-MiB-Job genügt, bleibt offen. Grenzen nicht erhöhen; eine Grenzverletzung müsste technisch abbrechen und dürfte kein Teilurteil liefern.

## Passende Übernahmen und verbleibender Freigabeschritt

Übernommen werden unveränderte E/F-/U-/Feedbackimplementierung, Live-Referenzen, struktureller Archivvergleich und dessen Größen-/Integritätsprüfungen. Die neuen neutralen A/B-Quellen durchlaufen diese Referenzen tatsächlich. Historische Zeugen- und Fehlerabschlussnachweise gelten nur für ihre bestehenden Komponenten; sie ersetzen nicht die neuen Quellen-, Paar-, Matrix- und Interaktionsprüfungen. Alte Forschungsdaten wurden nicht erneut ausgewertet.

preservation.json bestätigt den bisherigen v2-Validator mit 2979 Code-/Vertragsdateien und 72 Qualifikationsbelegen sowie unveränderte Forschungs- und unabhängige Zeugenlieferungen. Neue Dateien liegen außerhalb der historischen Bindungsverzeichnisse.

Forschungsumfang bleibt exakt 16 Paare, 32 Geschichten, 64 Policy-Arme, 64 Live-Referenzen, 64 Archivrekonstruktionen, 32 Quellenrekonstruktionen und eine unabhängige Statistikreferenz; keine zusätzlichen Messarme. Keine Erweiterung auf 32 Paare.

Keine Forschungsquellen, vollständigen 1024-Frame-Policyfälle, Forschungsberechtigung, Forschungsserie oder neue Vorstartfreigabe erzeugt. Das vorliegende Paket ist neutral qualifiziert; Forschungsquellenzugang und der vollständig gebundene Forschungseinstieg sind ausdrücklich noch nicht zugelassen. Nach Paketabnahme ist der nächste begrenzte Schritt eine gesonderte Forschungsvorbereitung mit Quellenfreigabesperre, Paarvollständigkeit, gemeinsamem Ressourcenrahmen und endgültiger Vorstartbindung. Der Projektleiter entscheidet darüber separat. ER1 bleibt abgeschlossen mit INCONCLUSIVE.
