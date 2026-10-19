# U/A1-Vergleichsvorbereitung – Abschluss 2026-10-04

A1 ist technisch abgenommen. Der beauftragte U/A1-Vergleich ist implementiert,
mit neutralen Ersatzdaten qualifiziert und vorstartgebunden. Die technische
Abnahme der Vergleichshülle und eine separate Einmallauffreigabe liegen als
nächste Entscheidung beim Projektleiter. Kein Forschungsreplay, keine
Forschungsquellenmaterialisierung und keine operative Autorisierungsdatei.

## Implementierung und unveränderte Bindungen

Vier neue Dateien:

- `tools/_s2uc_a1_compare_sources.py`: dieselben 16 T1- und acht F-Fälle,
  Reihenfolge, Längen, Phasen, Zielmasken, Quellenhashes und Bewertungskriterien.
  Neutrale Ersatzwerte entstehen in einem separaten Zweig vor jedem Quellzugriff.
- `tools/_s2uc_a1_compare_engine.py`: eigener A1-Auswerter; ursprüngliches U
  und unabhängige Zustandsreferenzen. Prüft vor Aufnahme jedes Hinweispaars
  Teilzulassung, zusätzliche Revision, Originaltuple-Identität, umgeschlüsselte
  Fehlerzellen, neue Tickets, eingefrorene Originalnachfolger und Auswahl.
- `tools/s2uc_a1_compare.py`: separate Vorbereitung, Qualifikation, Versiegelung,
  reine Bindungsprüfung und einmaliger Vergleichsstart. Die Supervisor-Funktion
  ist textidentisch zum bereits qualifizierten K1-Supervisor. A1 erhält eigene
  Pfade, Autorisierung, Codebindung und die korrekte Arm-Exportkategorie.
- `tests/test_s2uc_a1_compare.py`: 18 Prüfungen der Hülle, kein erneuter Lauf
  des abgenommenen A01–A11-Verhaltenspakets.

Die A1-Regel sowie U/K1-Produktionsdateien wurden nicht verändert. Die
A1-Implementierungsbindung besteht weiterhin mit 164 Dateien; die historische
K1-Vorstartbindung besteht ebenfalls. Beide Prüfungen lesen nur Hashbindungen.
Die neue Codebindung umfasst 152 Dateien einschließlich gebundener Abhängigkeiten,
Plan und bestehender T1-Quellhashes. Hashprüfung ist keine Materialisierung.

## Auswertung und Evidenzgrenze

Teilzulassungen, vollständige Kandidaten-/Retained-Bestätigungen, verarbeitetes
und verworfenes Feedback sowie spätere warme Abrufe sind getrennte Größen.
Vollständige Bestätigungen werden aus tatsächlich beobachteten Viererblöcken
rekonstruiert; Retained-Rolle oder Teilzulassung allein zählen niemals als solche.
Die gespeicherte Feedbackhistorie wird je Originalspur und Offset überprüft.
Eine warme Hypothese benötigt früher verarbeitetes Feedback derselben Linie.
Teilzulassungen und Feedbackzahlen allein erfüllen kein Mechanismuskriterium.

Jede Fallauswertung enthält alle Zielvergleiche, gewonnene/verlorene Original-
Offset-Linien, warme Gewinne/Verluste, Fehlerdifferenzen, Verdrängungszeitpunkte,
verlorene Fehlerzellen und Teilzulassungs-/Feedback-/Wiederabrufketten.
Vorkommenszahlen und eindeutige Originalspuren beziehungsweise Offset-Linien
werden getrennt gezählt. Identitäten sind auf den jeweiligen Fall beschränkt.

Unverändert: Mechanismus verlangt mehr modale warme T1-Möglichkeiten über624
Ziele; Nutzen verlangt strikt besseres T1-Mittel, nicht schlechteres F-Mittel
und strikt besseres Mittel über alle24 Fälle. Schaden: jede Falldifferenz
höchstens1/32 und T1-G_w nicht schlechter. Anpassung:26/52 insgesamt,
mindestens4/13 pro Gruppe;20 Negativkontrollen.324 Diagnoseziele ersetzen
keine Primärmaske. Material bleibt bekanntes Entwicklungsmaterial, kein Transfer.

## Neutrale Qualifikation

`../a1-comparison-neutral-20261004-01/tests.json`:18/18 PASS, keine Fehler.
Gesamtdauer13,479s. Vollablauf COMPLETE:24 Fälle,48 Arme,3.584 Aufnahmen und
Referenzfortschreibungen,872 Zielvergleiche; Worker4,673s,
Supervisor bis vor Abschluss6,289s. Keine formale Wiederholung notwendig.
Vier vorherige neutrale Entwicklungsprüfungen mit acht Armen/640 Aufnahmen
waren ein nicht archivierter Smokecheck; sie sind kein Abnahmebeleg.

| Prüf-IDs | Gegenstand | Ergebnis |
| --- | --- | --- |
| 01 | Vollständiger neutraler Ablauf, Gewinn und Schaden, alle vier Stufen | PASS |
| 02–08 | Autorisierung, Startfehler, Timeout, Prozessabsturz, Workerfehler, Limits, Kollision | PASS |
| 09–10 | Fehlende Ziele/Ressourcenverletzung; Gleichstand reicht nicht, Schaden wird erkannt | PASS |
| 11–15 | Quellsperre, Zeit-/Abbruchpfade, Exportfehler, echter Autorisierungspfad, Dateikappen | PASS |
| 16 | Exakte Fall-, Masken-, Limit- und Kriteriengleichheit mit bisherigem Plan | PASS |
| 17 | Falsche Vollbestätigung, fehlende Revision und falsche Feedbackhistorie abgewiesen | PASS |
| 18 | Fehler nach A1-Revision und Receipt schließen leer; Auswerterfehler schließt NOT_EVALUABLE | PASS |

Fehlerinjektionen erzeugen absichtlich einzelne NOT_EVALUABLE-Abschlüsse und
Tracebacks. Das sind bestandene Negativprüfungen, keine fehlgeschlagene
Qualifikation. Kein Fehlerabschluss enthält ein positives Forschungsurteil.

Nur in den neutralen Ersatzdaten beobachtet:

| Stufe | U | A1 |
| --- | ---: | ---: |
| Teilzulassungen | 0 | 64 |
| Vollständige Bestätigungen | 86 | 120 |
| Verarbeitetes Hypothesenfeedback | 388 | 504 |
| Verworfenes Hypothesenfeedback | 62 | 0 |
| Warme Hypothesenabrufe | 258 | 348 |
| Spätere warme Abrufe nach Teilzulassung | 0 | 148 |

A1 verdrängt40 Spuren durch Teilzulassung. Insgesamt98 Zielverbesserungen,
78 Verschlechterungen,696 Gleichstände; größter Zielmehrfehler0,001953125.
152 gewonnene Vorkommen entsprechen20 Original-Offset-Linien;98 verlorene
Vorkommen entsprechen56 Linien. Diese Zahlen prüfen den Auswerter und sind
**kein A1-Forschungsnutzenbeleg**.

## Budgets und Abschluss

Unverändert3.600s gesamt,3.540s Worker und60s Abschlussreserve;
64MiB Export inklusive8MiB Vorbereitung und1MiB Abschlussreserve.
Die einzelnen Exportkappen summieren sich maximal auf61,75MiB.
Gemessen:9.394Byte Zusatzheap,416Byte Bank,1.550Byte Receipt,
3.100Byte UTF-8-Obergrenze, zwei Ausgabeslots. Konservative Obergrenzen:
16 Originalframes und18 kombiniert. Die Nullwerte der nicht aktivierten
Frame-Tracing-Zähler sind keine gemessenen Nullbelegungen; die vorhandene
A1-Tracequalifikation bleibt unverändert gültig.

Der neutrale Vollablauf exportiert8.083.979Byte vor Abschluss.
Das verlustlos geprüfte Qualifikationsarchiv umfasst873.918Byte;
Vorbereitung vor Eigenbindung/Autorisierung2.858.192Byte. Der Start prüft
zusätzlich deren tatsächliche Dateigrößen gegen8MiB. Die Abschlusszeitmessung
erfolgt wie bisher vor dem finalen Schreiben des Abschlussdokuments.
Betriebssystemausfall/Stromverlust wird dadurch nicht als abgefangener Fehler behauptet.

## Vorstartbindung und vorbereiteter Befehl

`docs/S2UC_A1_VERGLEICH_V1_20261004_VORSTARTBINDUNG.json`

SHA256: `c5478f0a7fce810bda23ee045a02b21317d5178d4ee595c1f064327d08199705`

Die Bindung umfasst Code-/Eingabebindung, Qualifikationsabschluss, Testergebnis
und verlustloses Belegarchiv. `check` hat PASS_PRESTART_BINDING_NO_REPLAY ergeben.

Reine Prüfung im Projektverzeichnis:

```powershell
C:/Python314/python.exe -m tools.s2uc_a1_compare check
```

Vorbereiteter Vergleichsbefehl, **nicht ausgeführt**; erst nach separater
Freigabe und Bereitstellung der exakt gebundenen Autorisierungsdatei:

```powershell
C:/Python314/python.exe -m tools.s2uc_a1_compare run --authorization docs/S2UC_A1_VERGLEICH_V1_20261004_AUTORISIERUNG.json
```

Die Vorlage `docs/S2UC_A1_VERGLEICH_V1_20261004_AUTORISIERUNG_VORLAGE.json`
steht auf PENDING_SEPARATE_AUTHORIZATION und autorisiert keinen Start.
Der vorgesehene Ausgabeordner `reports/s2uc/a1-comparison-20261004-01` existiert
noch nicht. Vorhandene Ausgaben werden niemals überschrieben oder fortgesetzt.

Empfohlener nächster Schritt: Projektleiter prüft diese Vergleichshülle und
ihre Belege. Bei Abnahme kann er die separate, genau auf diese Vorstartbindung
bezogene Einmallaufentscheidung vorbereiten. Keine Regeländerung und kein
weiterer Variantenvergleich sind aus der neutralen Qualifikation abgeleitet.
