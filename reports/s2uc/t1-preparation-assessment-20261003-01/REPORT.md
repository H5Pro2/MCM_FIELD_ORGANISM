# T1-V2: vollständige Vorbereitungsübergabe

Stand 2026-10-03. T1-Vertrag abgenommen; Vorbereitung V2 technisch qualifiziert.
Die fachliche Vorbereitungsabnahme ist offen. T1-Ausführung ist nicht freigegeben.
Dieser Abschluss wertet ausschließlich gespeicherte Belege aus. Er startet keine
Tests, Replays, Quellenmaterialisierung oder operative Autorisierung.

## Lieferumfang und Bindung

Neue Quellen-/Auswertungshülle: `tools/_s2uc_t1_source.py`,
`tools/_s2uc_t1_evidence_v2.py`, `tools/_s2uc_t1_assessment_v2.py`,
`tools/s2uc_t1_prepare_v2.py`, `tests/test_s2uc_t1_v2.py`.
Hinzu kommen die Präzisierung `docs/S2UC_T1_PRAEZISIERUNG_20261003.txt`
und die V2-Dateien PLAN, BINDUNG, HERKUNFTSINDEX, AUTORISIERUNG_VORLAGE
und AUFRUF unter `docs/S2UC_T1_V2_*_20261003.*`.
Die historische Vertragsfassung bleibt erhalten. Dieser Restauftrag ergänzt
diesen Bericht mit `evidence-inventory.json` und `closure.json` und synchronisiert
die obersten Standangaben von README und AKTUELLER_FORSCHUNGSWEG.

V2-Bindung SHA256:
`78525e2ff688151cc0dfbb9400a40a4a5732df426d52b89e4d6b5067ddc016f3`.
Plan SHA256: `000e3aae92d7966ac8cde82d108197802843b6b71b426f6d98f4996805dc502e`.
Qualifikationsabschluss SHA256:
`6533a4810d0c612fef4c8066c731d94b95898458f004547b5a5cd06e81dbd22f`.
Die Bindung umfasst 90 Codedateien. Das beigefügte Inventar dokumentiert den
Dateiabgleich einschließlich gemeinsamer Codebindungen mit der zuvor
qualifizierten technischen Wiederholung V4. Die bereits gebundenen Dateien
werden für diesen Abschluss nicht verändert.

U/M/E/K/P, Defaults, Auswahl- und Fehlerfortschreibungsregeln bleiben unverändert.
V2 verwendet die eingefrorenen Replayfunktionen, den qualifizierten Sample-
Blattbeobachter und denselben Watchdog-Code. Die separate Quelle importiert nur
hashlib und erhält keine Policyergebnisse. Bibliothek, Modus, Bank und Sollmodalität
bleiben Beobachterdaten; die Policy erhält die Werte und ihr bestehendes Profil.
Float64-LE/Base64 exportiert die Werte verlustfrei innerhalb der Quelldateigrenze.

## Tatsächlich erfolgte neutrale Ausführungen

| Vorbereitung | Gespeicherter Abschluss | Abgeschlossene Policy-Replays | Materialisierte neutrale Fälle |
| --- | --- | ---: | ---: |
| V1, t1-neutral-qualification-20261003-01 | FAILED, WORKER_EXIT:1 | 5: neutral-hold U/M/E/K/P | 2 |
| V2, t1-neutral-qualification-20261003-02 | PASS | 10: neutral-hold und neutral-change, jeweils U/M/E/K/P | 2 |
| Summe dieses T1-Entwicklungspakets | V1 bleibt mitgezählt | 15 | 4 Fallmaterialisierungen, 2 verschiedene Fälle |

Jeder Replay umfasst 80 Positionen: insgesamt 1.200 Arm-Aufnahmen und ebenso
viele Referenzfortschreibungen in diesen Matrizen. V1 materialisierte beide
neutralen Quellen vor dem ersten Replay, erreichte aber nur den ersten Fall.
V2 verwendet dieselben neutralen Fälle erneut; diese Wiederholung wird nicht
als neue unberührte Evidenz ausgegeben. Namespace MCM-QUALIFICATION-ONLY-v1:
neutral-hold Replikat201/QH, 80H/Bank0; neutral-change Replikat202/QC,
24C/Bank0,16R/Bank0,8I/Bank1,32C/Bank1.

V1 bestand neun Vorbereitungstests. V2 bestand elf Vorbereitungstests und vier
anschließende Belegtests. T09 enthält zusätzlich echte Watchdog-Normal- und
Abbruchprozesse; diese sind keine Policy-Replays. Ihre temporären Probeordner
wurden vom Test entfernt; gespeichert sind Testergebnis und gebundener Testcode,
keine eigenständigen dauerhaften Probejournale. Die Unit-/Grenztests verwenden
neutrale synthetische Fixtures; die vier Belegtests lesen die gespeicherte Matrix.
Alle V1-Dateien, Fehlerabschluss und erste Codefassung bleiben erhalten.
Frühere Sample-/Watchdog-/V4-Qualifikationen werden als historische Nachweise
wiederverwendet und wurden im T1-Paket nicht erneut ausgeführt.

T1-Evaluationsquellen: **0**. T1-Evaluationsreplays: **0**.
Keine T1-Digests aus Test- oder Pilotmaterialisierung. Die im Plan gespeicherten
Fallkennungen und Phasendefinitionen sind keine materialisierten T1-Quellen.

## Korrektur V1 → V2 und kausale Belegführung

V1 brach mit `INVALID_CASE_EVIDENCE: ValueError:FROZEN_ERROR_PAIR` ab.
Die neue Prüfung setzte fälschlich den Zellzustand bei der Prognose mit dem
Zustand beim späteren Feedback gleich. Im neutral-hold-Fall für Ziel9 wurde der
Beleg an den Eingängen7/8 noch unter Kandidatenschlüsseln eingefroren. Aufnahme8
promovierte den Bestand. Beim Feedback9 waren diese ursprünglichen Schlüssel
nicht mehr lebend; die promovierten Retained-Schlüssel waren andere Schlüssel.
Dies war ein Fehler der Belegprüfung, kein nachgewiesener Policyfehler.

V2 friert Fehlerzellen und Feedbackhistorie für das nächste Ziel vor der Aufnahme
und einer möglichen Promotion ein. ec/ep im Prognosebeleg werden mit diesem
vorziellichen Snapshot verglichen. Die Live-Markierung beim späteren Feedback
wird gesondert gegen den dann bestehenden Bestand geprüft. Nur noch lebende
Originalschlüssel erhalten die erwartete Fehlerfortschreibung. Promotion nimmt
die bestehende Zelle und Historie mit, schreibt aber eingefrorene Prognosekeys
nicht rückwirkend um. Verlorene Schlüssel werden nicht wiederbelebt; ihr
`live_at_feedback` ist falsch und ihr nachfolgender Zelleintrag fehlt.

T13 belegt genau diesen Fall und weist eine gefälschte Live-Markierung zurück.
T11 prüft manipulierte Zustände, Originalordinalen, Feedbackfehler, Auswahl und
fehlende Zeilen. T12 rekonstruiert die vollständige Matchmenge aus Originalbestand
und Quellwerten; auch gemeinsames Entfernen eines Matches aus U und M fällt auf.
Kein Match ist ein gültiger Verfügbarkeitsbefund und kein fehlender Technikbeleg.
Modaler Nachfolger und tatsächlich realisiertes Ziel bleiben getrennt.

## Gespeicherte Test-IDs: alle bestanden

| ID | Gegenstand |
| --- | --- |
| T01 | Policyblinder Generator, neutrale Domäne und Evaluationssperre |
| T02 | Formel, Byte-Reihenfolge, Zustandsfortsetzung ohne Phasenreset |
| T03 | Vollständige Nenner und negative Kontrollen, leere Zielmengen |
| T04 | Verlustfreier Codec und Provenienz, fehlerhafte Nutzlast |
| T05 | Modales Mechanismuskriterium getrennt von realisiertem Fehler |
| T06 | 52 Übergänge, festes spätes Fenster, Kontrollen, fehlende Belege |
| T07 | Herkunftsüberlappung ohne Fallauswahl oder Ersatz |
| T08 | Autorisierungssperre vor Worker und Quelle |
| T09 | Wiederverwendeter Watchdog, echter Normal- und Abbruchpfad |
| T10 | Zwei gespeicherte Fünfarmfälle, Evidenz und Freigabe aller Slots |
| T11 | Zurückweisung manipulierter Provenienz, Feedbacks und Auswahl |
| T12 | Vollständige Matchmenge und Ressourcenüberschreitung |
| T13 | Promotion zwischen Prognose und Feedback, verlorene Schlüssel |
| T14 | Schwelle26, Gruppenanforderung und voller Kontrollnenner |
| T15 | Exakte Schadensgrenze1/32 und festes Stabilitätsfenster |

Vollständige Python-Testnamen und unveränderte gespeicherte Ergebnisse stehen
im Inventar sowie in `tests.json` und `evidence-tests.json` der V2-Qualifikation.
Die zwei neutralen Matrixfälle decken nicht jeden Maximalbestand ab; insbesondere
ist das kein neuer Sechshypothesen-Stresstest. Frühere gebundene Grenzprüfungen,
Sample S01–S10 und Watchdog-Qualifikation bleiben die ergänzende Grundlage.

## Festgelegte Auswertung und Aussagegrenzen

16 Fälle, je80 Positionen; 80 Arme,1.280 Quellpositionen,
6.400 Arm-Aufnahmen plus6.400 Referenzfortschreibungen. Alle Quellen und
Herkunftsbelege müssen vor dem ersten Policyaufruf vollständig gespeichert sein.
Der Herkunftsindex enthält87 gespeicherte Quellen im dokumentierten Suchumfang;
der versiegelte neutrale Ergänzungsindex wird zusätzlich berücksichtigt.
Überlappungen werden ausgewiesen und lösen keinen Fallersatz aus.

Alle52 Übergänge bleiben im Nenner, einschließlich kurzer Phasen und leerer
Zielmengen. Die20 strukturell negativen Kontrollen werden zusätzlich getrennt
ausgewiesen: I12/H8. Nichtbestehen der Warmwahl bedeutet weder schlechte
Vorhersage noch unangemessene Enthaltung. Reale Fehler bleiben separat sichtbar.
Anpassung verlangt26/52 sowie4/13 je Herkunftsgruppe; die Schwellen bleiben gleich.

G_w bezeichnet ausschließlich Ziele11,13,...,79 der vier S0-Fälle, kein
unterstelltes Warmsein. Wärme erfordert die tatsächlich belegten vorziellichen
Fehlerwerte und die Feedbackhistorie des betreffenden Schlüssels. Wiedererkennung,
Verfügbarkeit, Anpassung, G-Nutzen und Schäden werden getrennt berichtet.
G verlangt strikten Vorteil gegen jede Baseline; das feste späte Fenster darf
gegen keine Baseline schlechter sein. Die G-Fallschadensgrenze bleibt1/32.
Technisch fehlende Evidenz führt zu NOT_EVALUABLE und wird nicht herausgefiltert.

Der Vertrag prüft begrenzten synthetischen Transfer ab der48-Vektor-Grenze.
Exakte Wiederkehr eines künstlichen endlichen Alphabets ist vorausgesetzt.
Keine Aussage zu verrauschter Invarianz oder Audio-/Video-Kettentransfer.
Der ursprüngliche Raster32-Lauf bleibt NOT_EVALUABLE; der spätere technische
Wiederholungslauf bleibt separat abgeschlossene Evidenz innerhalb seines Rasters.

## Ressourcen, Exporte und Zeit

Maximaler gespeicherter Zusatzheap je Arm: U6.033, M4.364, E2.457,
K1.386, P1.386 Byte; Grenze16.384. Gepackter Bestand416/416 Byte.
U: Originalframe-Obergrenze8, kombinierte Obergrenze10, Receipt816 Byte,
UTF8-Obergrenze1.632 Byte. U-Felder mit Peak0 bedeuten hier nicht gemessene
Trace-Peaks, nicht null Speicherverbrauch. Baselines: Framepeak8, kombiniert9,
ein Ausgabeslot, Receipt549 Byte, transienter Receipt-UTF8-Peak1.098 Byte.
Grenzen:18 Originalframes,2 Ausgabeslots,20 kombiniert, Receipt16.384,
UTF8 32.768 Byte. Alle zehn gespeicherten Arme schließen mit freigegebenen Slots.

Die Zusatzheapmessung umfasst die isolierte Aufnahme einschließlich Promotion
und Metadaten; Beobachtertrace ist ausgenommen. Die Baseline-Traces behalten ihre
ursprüngliche Abdeckung mit qualifiziertem Sample-Blattbeobachter. Diese Werte
sind keine Messung des gesamten Prozess-RAM.

V2-Qualifikationsordner:942.725 Byte. Vorbereitung und gebundene Referenzen
einschließlich PENDING-Vorlage:6.539.356/8.388.608 Byte nach der Hüllenbilanz.
Eine später separat autorisierte Datei kommt als eigene Datei hinzu und wird
beim Start mitgerechnet. Dieses ergänzende Übergabedossier wird separat im
Abschlussinventar bilanziert und ist keine nachträgliche Änderung der Bindung.
V1- und V2-Archivgrößen sowie Einzelexporte sind im Inventar ausgewiesen.

Operativer gemeinsamer Exportrahmen67.108.864 Byte, Abschlussreserve1.048.576.
Dateigrenzen: Quelle65.536, Arm196.608, Fallauswertung524.288,
Ressourcen32.768, Start1.024, sonstige Datei524.288 Byte. Die neutralen Quellen
haben je41.026 Byte. Qualifikation:900s/16MiB; die hohe Vorbelastung im neutralen
Ledger ist die technische Reservierung dieses engeren Rahmens, kein Export
von51MiB an Forschungsdaten. Tatsächliche Dateien werden separat bilanziert.

Gespeicherte V2-Gesamtdauer bis vor dem Schreiben ihres Abschlusses115,4300404s;
reine Replayengine111,2685988s, Quellenverarbeitung0,1033935s,
Fallauswertung1,1022767s, Armexport0,0344154s.
Der Worker wurde mit Exit0 und beendetem Prozess bestätigt. Die gespeicherte
Lifecycle-Chronologie meldet den tatsächlichen Abschluss innerhalb der Frist;
die Zeitmarke schließt ihren eigenen letzten Schreibvorgang nicht ein.
V1-Qualifikationsdauer93,4739632s; der fehlgeschlagene Versuch wird nicht versteckt.

Zeitplanung:16 mal die jeweils langsamere neutrale80er-Zeit jeder Baseline,
zuzüglich25 Prozent =1.796,196404s. Dazu180s Administration,30s U und60s
Abschluss: **2.066,196404s**, Reserve **1.533,803596s** zur3.600s-Grenze.
Das ist eine Hochrechnung, keine gemessene T1-Laufzeit und keine Garantie für
die noch ungeprüfte T1-Konkurrenz. Workergrenze3.540s, Abschlussbudget60s.

## Vorbereiteter Aufruf und nächste Entscheidung

Arbeitsverzeichnis: `C:/Users/TV/Documents/MCM_FIELD_ORGANISM/workspace`.
Der vorhandene Aufrufleitfaden ist `docs/S2UC_T1_V2_AUFRUF_20261003.txt`.
Vorbereitung und Qualifikation sind erledigt; deren Befehle nicht wiederholen.
Die Autorisierungsvorlage bleibt `PENDING_SEPARATE_AUTHORIZATION`.
Erst nach fachlicher Vorbereitungsabnahme und separater Einmallauffreigabe
kommt folgender bereits vorbereitete Aufruf infrage:

```powershell
C:/Python314/python.exe -m tools.s2uc_t1_prepare_v2 run --authorization <separate-Datei>
```

Exklusives Ziel: `reports/s2uc/t1-transfer-20261003-01`, derzeit nicht vorhanden.
Keine Wiederaufnahme, keine Zusammenführung mit früheren Läufen. Es wurde keine
operative Autorisierungsdatei erstellt und dieser Aufruf wurde nicht ausgeführt.

Empfehlung an den Projektleiter: dieses vollständige Vorbereitungspaket anhand
der Bindung, Fehlerkorrektur, Ausführungsbilanz und Grenzen fachlich abnehmen.
Bei Abnahme ist der nächste Entwicklungsschritt die separat zu autorisierende,
einmalige T1-Transferprüfung mit unveränderten Kriterien. Vorher besteht kein
Bedarf für weitere Optimierungen, Testwiederholungen oder Policyänderungen.
