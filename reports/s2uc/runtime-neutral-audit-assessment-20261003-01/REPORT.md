# Neutraler Laufzeitaudit – fachlicher Abschluss (2026-10-03)

Ergebnis: Die acht gepaarten Diagnosen sind abgeschlossen. Hauptkostenquelle ist der zeilenweise Ressourcenbeobachter, insbesondere `BudgetObserver.trace`. Keine operative Reparatur und kein Raster32-Replay.

## Ausführung und Bindung

18 Replays × 80 Positionen: 1.440 experimentelle Aufnahmen und 1.440 Referenzfortschreibungen. Zwei feste neutrale Quellen N1/N2, M/E/K/P je ON/OFF sowie zwei unveränderte M-Originalanker. Matrix bis bestätigtem Workerende: 206.579 s bei 900 s Grenze. Diagnoseexport einschließlich Abschluss: 1,747,707 Byte.
Vor Beginn und nach Abschluss geprüft: Auditplan, zwei Diagnosedateien, 71 Altdateien und 376 historische Dateien. Originalexporte und Bindungen unverändert. D01–D05: 5/5 bestanden, keine Fehler oder Skips; D01–D04 zuvor als Vorbereitung geprüft, ohne Replay. D05 enthält genau zwei Prozessproben.

## Gemessene Kosten

| Quelle/Arm | ON Replay s | OFF Replay s | ON/OFF |
|---|---:|---:|---:|
| N1/M | 17.329186 | 0.182140 | 95.14 |
| N1/E | 17.228068 | 0.201456 | 85.52 |
| N1/K | 16.560831 | 0.237454 | 69.74 |
| N1/P | 16.329164 | 0.266139 | 61.36 |
| N2/M | 25.120011 | 0.346742 | 72.45 |
| N2/E | 25.506744 | 0.378677 | 67.36 |
| N2/K | 24.250985 | 0.423766 | 57.23 |
| N2/P | 24.481339 | 0.444598 | 55.06 |

Exklusive Kategorien, summiert über acht Replays je Modus. Diese Partition enthält auch Diagnoseaufbau und Ergebnisexport; die Replayzeiten oben schließen beides aus.

| Kategorie | ON Wall s | OFF Wall s | ON CPU s | OFF CPU s |
|---|---:|---:|---:|---:|
| evidence_observation | 3.688529 | 0.456263 | 3.703125 | 0.437500 |
| export_serialization | 0.015119 | 0.014359 | 0.000000 | 0.000000 |
| file_output | 0.006338 | 0.005881 | 0.000000 | 0.000000 |
| json_internal | 1.150441 | 0.280137 | 1.093750 | 0.296875 |
| policy | 2.770071 | 0.092491 | 2.875000 | 0.156250 |
| reference | 0.098405 | 0.048280 | 0.062500 | 0.078125 |
| replay_other | 1.985476 | 1.658242 | 1.734375 | 1.562500 |
| resource_other | 0.227353 | 0.031735 | 0.109375 | 0.062500 |
| resource_trace_approx | 10.036265 | 0.000000 | 10.500000 | 0.000000 |
| resource_trace_base | 141.992183 | 0.000000 | 141.671875 | 0.000000 |
| resource_trace_promotion | 4.936757 | 0.000000 | 4.890625 | 0.000000 |
| source_gate | 0.014524 | 0.011528 | 0.031250 | 0.015625 |

Die drei Traceebenen beanspruchen 94.04% der ON-Wall-Partition; allein der Basisbeobachter 85.07%. Die Kategorien summieren sich exakt zur jeweiligen gemessenen Wall-/CPU-Partition.

Codebefund: Der Basisbeobachter durchsucht bei relevanten Traceereignissen aktive Stackframes und rekursiv deren Objektgraphen. Auch bereits als Frame erkannte Objekte werden anschließend als Dataclasses bis in ihre 48 Skalarwerte durchlaufen. Die abgeleiteten Beobachter dispatchen zusätzlich bei weiteren Python-Ereignissen. Die Messung belegt die dominierende Traceebene; sie isoliert nicht den Anteil einzelner Visitor-Zweige oder einzelner Path-Aufrufe.

Die OFF-Messung unterdrückt ausschließlich sys.settrace in der isolierten Replaykopie. Die unveränderten Adapteroperationen, sonstigen Ressourcenprüfungen, Heapbeobachtung und Referenzfortschreibung bleiben. Der ON/OFF-Unterschied zeigt Beobachtungskosten in diesen Fixtures, keine bewiesene Geschwindigkeit einer noch nicht implementierten Reparatur.

## Timerperturbation und Messgrenzen

| Quelle | Original M s | Diagnose M ON s | Diagnose/Original |
|---|---:|---:|---:|
| N1 | 14.377008 | 17.329186 | 1.205 |
| N2 | 21.908608 | 25.120011 | 1.147 |

Hooks verändern Stacktiefe, Traceereignisse und Allokationen. Policy-/Belegzeiten enthalten verbleibende Dispatch-/Hookkosten; sie sind keine exakt bereinigten Algorithmuszeiten. Der Rest `replay_other` enthält Aufbau, Schleifen-/Prüfverwaltung und nicht separat erfasste Arbeit. `outside_partition_ns` steht pro Messung in den Rohdaten. Prozess-CPU-Zeit ist grob quantisiert; Nullwerte kleiner Kategorien bedeuten nicht kostenlosen Betrieb. Keine Statistik aus Wiederholungen, keine Warmups. Dateiausgabe misst open/write/close ohne fsync; sie belegt keinen physischen Datenträgerdurchsatz.

## Fachliche Gleichheit

8/8 ON/OFF-Paare sind nach Entfernung ausschließlich des Feldes `resources` kanonisch byteidentisch. Beide M-Paare stimmen außerdem mit dem jeweils unveränderten Original-M überein. E/K/P werden nicht mit einer anderen Policy verglichen. Enthalten sind Entscheidungen/Receipts, Fehlerupdates, Aufnahmen und Originalbestände, Zustandshashes, Endziel 81, Ausgabefreigabe, EMA-Löschung und terminales Cleanup. Alle 18 Replays haben ihre terminalen Zustände freigegeben.
N2 konkurrierende Prognosen pro Arm: M=14, E=14, K=14, P=14. Die Aussagen gelten für diese zwei Fixtures; keine allgemeine Gleichheit oder Ressourcenqualifikation daraus ableiten. OFF und zeitinstrumentiertes ON sind ausdrücklich keine operativen Ressourcenbelege.

## Zeitwächter

Normalprobe und Abbruchprobe bestanden. Bei der Abbruchprobe: Anforderung 1.801 ms nach Deadline; bestätigtes Workerende weitere 12.260 ms später. Protokollierte Beispiel-Abschlussserialisierung: 0.143 ms. UTC und monotone Zeit sind für Deadlinefestlegung, Abbruchanforderung, bestätigtes Workerende und Beginn/Ende dieser Verwaltung getrennt gespeichert.
Die Bestätigung nach join ist kein exakt gemessener Todeszeitpunkt. Der historische Raster32-Workerstop bleibt UNKNOWN_NOT_RECONSTRUCTED. Die prototypische Verwaltungsphase misst nur ihre eigene Serialisierung, nicht die spätere gesamte Dateiversiegelung. Die operative supervise-Funktion wurde nicht geändert.

## Genau ein minimaler Reparaturvorschlag – noch nicht umgesetzt

Den rekursiven Ressourcenvisitor um einen sicheren Frame-Blattfall ergänzen: Frame-Identität weiterhin zählen, aber nachgewiesen unveränderliche reine Skalarfelder nicht erneut rekursiv besuchen. Nur exakt typisierte Frames mit unveränderlichem tuple aus echten floats und skalaren Bindungsfeldern dürfen den kurzen Pfad verwenden. Für mutable/custom Payloads, Unterklassen oder ungeklärte Typinvarianten bleibt der bisherige vollständige Visitor. Die derzeitige Frame-Validierung prüft Werte, erzwingt aber keinen tuple-Typ; ein bedingungsloses return nach isinstance(Frame) wäre daher unzureichend. Kein Abschalten von Traceereignissen, kein Caching fachlicher Entscheidungen, keine Policyänderung.

Notwendige Abnahme dieses einen eng begrenzten Hüllenpatches: alter/neuer Visitor mit identischen erreichbaren Frame-IDs, Outputslots, transienten Maxima und Budgetfehlern; Grenz-/Überschreitungsfälle, Aliasfälle, sechs Hypothesen, Eviction/Promotion und Fehlercleanup sowie mutable/custom-Payload-Fallback prüfen. Fachbelege vor/nachher pro gleicher Policy vollständig vergleichen. Anschließend separat freigegebene neutrale ON-Messung bei voller Ressourcenbeobachtung; tatsächliche Zeitersparnis und Zusatzspeicher messen. Erst diese Abnahme könnte eine operative Ressourcenqualifikation begründen. Vor einem späteren bewachten Evaluationslauf sind die hier geprüften getrennten Lebenszyklusereignisse als Protokollanforderung zu übernehmen; dies ist keine zweite Optimierungsalternative und keine jetzige Ausführungsfreigabe.

Raster32 bleibt geschlossen: TIME_LIMIT, globale Kriterien NOT_EVALUABLE, keine Fortsetzung oder fehlenden Arme. Zuständig für die nächste Entscheidung ist der Projektleiter: begrenzten Visitor-Patch mit den genannten Abnahmekriterien freigeben oder ändern.

## Belege

- `analysis.json`: vollständige Summen, Paare, Anker und Zeitwächterdifferenzen.
- `verification.json`: Hashprüfung, Umfang und vollständige Test-IDs.
- `../runtime-neutral-audit-20261003-01/`: versiegelte Rohbelege, 16 Timingdateien, acht Gleichheitsprüfungen, zwei Quellen, Prozessproben und Abschluss.
- Diagnosecode: `tools/s2uc_runtime_audit.py`; Tests: `tests/test_s2uc_runtime_audit.py`; Plan/Bindung unter `docs/S2UC_NEUTRALER_LAUFZEITAUDIT_*_20261003.*`.
