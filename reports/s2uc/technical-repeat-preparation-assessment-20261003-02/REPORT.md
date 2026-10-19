# Sample-Beobachter: abgeschlossene Hüllenintegration und Machbarkeit (2026-10-03)

**Ergebnis: PASS.** Die qualifizierte Sample-Blattbehandlung ist separat integriert und neu gebunden. Genau zehn neutrale JSON-Replays N1/N2 × U/M/E/K/P mit je80 Positionen wurden einmalig ausgeführt:800 Aufnahmen und800 Referenzfortschreibungen. Fachbelege10/10 gleich, strukturelle Ressourcenvergleiche10/10 gleich, vollständiges Cleanup in allen Armen. Keine Rasterausführung.

## Lieferstand und nachvollziehbare Vergleichsreparatur

Ausführbarer, gesperrter Endstand: tools/s2uc_repeat_prepare_v4.py; Bindung docs/S2UC_TECHNISCHE_WIEDERHOLUNG_V4_BINDUNG_20261003.json, SHA256 121cb259d4747949722a332c8f4f9f04e8fdfee05a8c7eb235da7de48513cae2.
V3 enthält die einzige neue Matrix in reports/s2uc/technical-repeat-preparation-20261003-03/integration. Worker und Matrix endeten COMPLETE, Prozesscode0. Die nachgelagerte V3-Abnahme endete dagegen FAILED: Sie verlangte auch für U-Einzelmesswerte transient/total exakte Gleichheit. Das war ein Fehler der Vergleichsprüfung, kein fachlicher Replayfehler. Der Fehlerstand und alle Rohdaten bleiben unverändert erhalten.

V4 repariert ausschließlich diese nachgelagerte Prüfung und übernimmt die abgeschlossene Matrix anhand ihrer Hashes. J05 bestätigt AST-Gleichheit von Worker, execute, integriertem Baselineaufruf, Watchdog, Aufruf-/Autorisierungsgates und Zeitplan zu V3. Keine neue Optimierung und keine Replaywiederholung. Jeder U-Messdatensatz muss total=retained+transient und0≤total≤16384 erfüllen; alle übrigen Strukturfelder einschließlich retained und Operationsfolge werden exakt verglichen. Alle Heapabweichungen sind vollständig in comparisons.json erhalten. J06 prüft, dass falsche Operations-/Framefelder, inkonsistente Heapzeilen und Budgetüberschreitungen weiterhin abgewiesen werden.

## Abnahme und unveränderte Grenzen

Neue Prüfungen J01–J04:4/4 PASS vor der Matrix; J05–J07:3/3 PASS für die Reparatur und Wiederverwendung, keine Fehler/Skips. Vorhandene V01–V08, S01–S10, V2 I01–I07 sowie Raster32 R01–R25 werden anhand unveränderter Bindungen übernommen. Keine erneuten Watchdog-Probeläufe und keine Diagnosematrix.

Die komplette JSON-Fachausgabe nach Abtrennung ausschließlich des resources-Objekts stimmt bei allen zehn Armen mit vorhandenen Referenzen überein. Referenz für M/E/K/P ist die qualifizierte Sample-Matrix NEW, für U die frühere integrierte U-Ausgabe. resources wird separat vollständig dokumentiert; 5/10 vollständige Ressourcenobjekte sind exakt gleich. Acht Baseline-Meterobjekte sind exakt gleich, beide U-Strukturen ebenfalls. Alle zehn Ergebnisse erfüllen die originalen resource_check-Prüfungen, terminal_cleanup, slots_released, states_identical und Endziel81; Baselines zusätzlich ema_cleared. Keine fachlichen Kriterien wurden verändert.

Maximaler Zusatzheap 5184/16384 Byte. Baseline-Maxima: {"combined_peak": 13, "frame_peak": 12, "output_slots_peak": 2, "receipt_bytes_peak": 454, "receipt_transient_utf8_bytes_peak": 908, "transient_reference_frames_peak": 12}. U-Maxima: {"combined_upper_bound": 14, "original_frames_upper_bound": 12, "packed": 416, "receipt_bytes_peak": 752, "utf8_upper": 1504}. Alle ursprünglichen Grenzen18 Frames,2 Ausgabeslots,20 kombiniert,416 Byte gepackter Bound und Receipt-/UTF8-Limits bleiben erhalten.

## Tatsächlicher Aufruf und Trace

Frischer spawn-Worker → worker → execute → eingefrorene Engine → produktiver Zeitwrapper → integrated_baseline → eingefrorener Replay. U läuft über den entsprechenden produktiven U-Zeitwrapper. Die spätere operative Hülle verwendet dieselbe Kette; nur neutrale Quellen/Validierung und der Zwei-Fall-Aggregator werden durch die eingefrorenen Rasterlieferanten und den32-Fall-Aggregator ersetzt. Einzelbelegprüfung bleibt dieselbe. Die Messung enthält keine Test-/Mock-Dispatchrahmen. patch.object ersetzt nur die Methode vor dem Aufruf; der Replay wird nicht über einen Mock weitergeleitet.

JSON-Quellen werden vor den Policies exportiert und manifestiert, anschließend neu gelesen, gehasht und validiert;48 getrennte Float-Identitäten pro Vektor werden geprüft. Vollständige bisherige Traceabdeckung bleibt aktiv. Die bereits eingefrorene Ausnahme für isolierte Heapmessung wird nicht verändert; U behält seinen bisherigen Ressourcen-Meter. Der Trace und die Observermethode sind am Workerende freigegeben.

## Direkte Zeiten

| Quelle/Arm | Wall s | Prozess-CPU s |
|---|---:|---:|
| N1/U | 0.091122 | 0.093750 |
| N1/M | 11.112459 | 11.125000 |
| N1/E | 11.289281 | 11.281250 |
| N1/K | 10.613698 | 10.609375 |
| N1/P | 10.649282 | 10.640625 |
| N2/U | 0.114385 | 0.125000 |
| N2/M | 15.822380 | 15.812500 |
| N2/E | 15.464564 | 15.468750 |
| N2/K | 14.777681 | 14.781250 |
| N2/P | 14.912562 | 14.875000 |

| Exklusive Enginephase | Wall s |
|---|---:|
| U_replay | 0.205507 |
| aggregation | 0.000011 |
| baseline_replay | 104.641908 |
| case_assessment | 0.629229 |
| export | 0.064648 |
| manifest | 0.006154 |
| materialization | 0.002283 |
| resource_check | 0.000050 |
| source_hash | 0.029291 |
| source_read | 0.002299 |
| source_validation | 0.008250 |

Quellenverarbeitung insgesamt 0.048277s; Belegprüfung 0.629229s, Aggregation 0.000011s, Export 0.064648s. Gesamte Engine 105.596845s. Die Differenz zu den exklusiven Phasen ist 0.007215s Engineverwaltung. phase-times.json selbst wird danach geschrieben und ist in der Workerzeit enthalten. Vorbereitung außerhalb der Engine steht separat in worker-path.json.

Von festgelegter Prozessdeadline bis bestätigtem Workerende 106.307866s. Tatsächliche Abschlussverwaltung einschließlich Inventar, Abschlussdatei und deren Hash 0.242154s. Matrix bis Ende dieser Verwaltung 106.550709s. Der letzte Journalmarker kann seinen eigenen Schreibvorgang nicht enthalten; keine vorweggenommene Zeitmessung vor dem eigentlichen Abschluss. Vollständige korrigierte Qualifikation einschließlich Reparatur 324.373886s ab ursprünglichem V3-Start; die abschließende Berichtversiegelung erhält zusätzlich einen terminalen Zeitnachweis.

## Einziger Laufzeitplan für3600s

Pro Baselinearm wird der langsamere der direkt integrierten N1/N2-80er-Werte für alle32 Fälle angesetzt, auch für die16 tatsächlich nur48 Positionen langen Fälle. Darauf kommen unverändert25 Prozent Zuschlag. Keine Verkettung alter Beschleunigungsquoten und keine Auswahl des günstigsten Modells.

Baseline:32 × (15,8223801 +15,4645643 +14,7776805 +14,9125623) ×1,25 = **2439.087488s**.
Dazu unverändert180s Administration,30s U,60s Abschluss. **Gesamt 2709.087488s; Reserve 890.912512s zu3600s.** U direkt mit32×größerem80er-Wert hochgerechnet benötigt3,660314s und bleibt deutlich unter seinem30s-Ansatz. Quellen-, Prüf-, Export- und Bindungsverwaltung liegen in den180s; diese Reserve ist nicht zur Baselinebeschleunigung verrechnet. Der Abschlussblock60s bleibt vollständig erhalten.

Der alte Lauf mit3602,419874s und der frühere Plan mit6330,087716s bleiben historische Vergleiche. Sie enthielten den früheren Sample-Durchlauf bzw. andere Aufrufrahmen; deshalb werden diese Gesamtzeiten nicht mit neutralen Geschwindigkeitsquoten skaliert. Die neue Planung misst den zukünftigen Workerpfad direkt und behandelt alle Fälle mit dem vollen80er-Preis.

**Empfehlung: Eine separat autorisierte technische Wiederholung innerhalb3600s ist mit dieser Reserve vertretbar.** N1/N2 beweisen keine absolute Laufzeitobergrenze für jede Kontextkonkurrenz oder Hostlast. Die25-Prozent-Zugabe, der volle80er-Ansatz und die verbleibenden rund891s tragen diese Planungsunsicherheit. Bei einer stärkeren Überschreitung beendet der unveränderte Watchdog den Worker nach3540s;60s bleiben für den Abschluss. Eine Betriebssystemstörung kann auch Abschlusszeiten überschreiten und wird als Fehler ausgewiesen; eine physische Echtzeitgarantie wird nicht behauptet. Ein Abbruch ergibt unvollständige technische Evidenz und keine positive Gesamtauswertung.

## Bindung, Budget und nächste Entscheidung

V4 preparation_check bestanden; Aufruf mit der echten PENDING-Vorlage wurde durch EXPLICIT_SEPARATE_AUTHORIZATION_REQUIRED vor jedem Start abgewiesen. Vorbereitung und gebundene Referenzen 5461852/8388608 Byte. Neuer Belegumfang V3+V4 und Bericht wird in closure.json gemeinsam bilanziert;16MiB und900s bleiben Obergrenzen. Alte Dateien/Bindungen/Exporte wurden nicht geändert.

Nächster Schritt ist die Entscheidung des Projektleiters über eine separate technische Einmallauf-Freigabe auf Basis des gebundenen V4-Stands. Keine weitere Vorbereitungs-/Optimierungsserie. Es liegt nur eine PENDING-Vorlage vor, keine operative Freigabe. Der ursprüngliche Raster32-Lauf bleibt geschlossen und global NOT_EVALUABLE; neue Daten dürfen nicht zu seinem Abschluss ergänzt werden. Kommunikation ausschließlich als Ergebnis hier, Weitergabe durch den Workflow.
