# Abschlussbericht: begrenzte neutrale URA1-Entwicklung

Stand: 2026-10-14. Ergebnisübergabe des MCM-KI-Entwicklers an MCM KI Projektleiter.
Zuordnung: bestehender neutraler URA1-Entwicklungsauftrag und Rückfrage zum Prüfpaket **dda37469-3a5d-4448-abcc-45f05509760e**.

**PASS_FOCUSED_NEUTRAL_DEVELOPMENT**, ausdrücklich **keine Forschungsbereitschaft**. Die gespeicherte Abschlussdatei führt `neutral_only=true`, `research_ready=false`, `research_runs=0`. Die nachfolgende Übergabe wertet vorhandene Belege aus; bestandene Entwicklungstests wurden hierfür nicht wiederholt. Kein Größenablauf, keine Forschungsquellen, keine Bootstrapmatrix und kein Forschungsversuch wurden für diese Übergabe erzeugt oder gestartet.

Die 14 vorhandenen Tests belegen die Auswahlablation und ihre Kontrollmechanismen auf begrenzten neutralen Fällen. Die vollständigen Kriterien für spätere Forschung sind noch nicht erfüllt: insbesondere ist das ausführliche Ereignisarchiv zu groß, und eine Prozess-/Gesamtlaufqualifikation fehlt.

## Implementierung und Bindung

- [tools/_s2uc_ura1.py](C:/Users/TV/Documents/MCM_FIELD_ORGANISM/workspace/tools/_s2uc_ura1.py): R-Adapter: ersetzt ausschließlich Auswahl und Auswahlgrund innerhalb des Receipt-Pfads. Jüngster berechtigter Originalnachfolger; bei gleichem Originalindex kleinster Schlüssel (role, generation, offset), retained=0/candidate=1. Persistenz nur bei leerer berechtigter Menge. Fehlerzellen bleiben als Kontrollzustand erhalten.
- [tools/_s2uc_ura1_reference.py](C:/Users/TV/Documents/MCM_FIELD_ORGANISM/workspace/tools/_s2uc_ura1_reference.py): Unabhängige Auswahlreferenz mit eigenem Bestand, eigener Paarbildung, eigenen Tickets und Fehlerzellen. Verwendet den vorhandenen unabhängigen Stock-Referenzpfad; importiert keinen R-Produktionsadapter. Sortierung eigener Originaldaten statt Übernahme des Produktionsgewinners.
- [tools/_s2uc_ura1_neutral.py](C:/Users/TV/Documents/MCM_FIELD_ORGANISM/workspace/tools/_s2uc_ura1_neutral.py): Auf 4 bis 128 Frames begrenzte neutrale Prüfhülle, getrennte U/R-Verarbeitung, Ereignisvergleich, Referenzprüfung, Armgraph-/Transientenmessung und verlustfreier Archivexport.
- [tests/test_s2uc_ura1.py](C:/Users/TV/Documents/MCM_FIELD_ORGANISM/workspace/tests/test_s2uc_ura1.py): 14 fokussierte Testmethoden einschließlich Mutation, Kopplungsinjektion und terminaler Fehlerbehandlung.
- [tools/s2uc_ura1_neutral_qualify.py](C:/Users/TV/Documents/MCM_FIELD_ORGANISM/workspace/tools/s2uc_ura1_neutral_qualify.py): Erzeuger des bestehenden neutralen Belegpakets; überschreibt kein vorhandenes Belegverzeichnis und enthält keinen Forschungseinstieg.

Die Entwicklungsbindung enthält die fünf Dateihashes und den unveränderten Konzepthash. N01 bestätigt alle 160 gebundenen UF1-Vorgängerdateien unverändert sowie die identische geerbte Feedback-, Aufnahme- und Promotionsimplementierung. Dies ist eine Entwicklungsbindung, kein Forschungs-Vorstart-SHA.

## Ausgeführte Tests und Ergebnisse

Alle folgenden IDs besitzen im vorhandenen tests.json Status PASS. Vollständiger ID-Präfix: `tests.test_s2uc_ura1.URA1Tests.`.

| Test-ID | Ergebnis / belegter Umfang |
| --- | --- |
| `test_N01_unchanged_U_bindings` | PASS — 160 Vorgängerhashes unverändert; geerbte Kernmethoden identisch. |
| `test_N02_regular_non_equivalence_and_resources` | PASS — Regulärer 64-Frame-Handfall: U/R nicht äquivalent; Ressourcen erfasst. |
| `test_N03_internal_lifecycle_events` | PASS — 48-Frame-Lebenszyklus: interne Aufnahme-, Promotions-, Verdrängungs- und Cleanup-Ereignisse gepaart gleich. |
| `test_N04_error_and_warm_mutation_invariance` | PASS — R-Ausgabe invariant bei COLD, BETTER_THAN_P, WORSE_THAN_P und TIE_P. |
| `test_N05_recent_original_not_confirmation` | PASS — Originalalter statt Bestätigungsalter: jüngeres Original 11 gewinnt gegen Original 3, auch bei schlechterem Fehler. |
| `test_N06_age_and_tie_order` | PASS — Geändertes Originalalter und Schlüsselgleichstand regelgemäß; künstlicher Metadaten-Grenzfall, kein regulärer Nichtäquivalenzbeleg. |
| `test_N07_no_successor_and_factor_rejection` | PASS — Fehlender Nachfolger und unzulässige Faktoren abgewiesen; Persistenz. |
| `test_N08_injected_couplings_rejected` | PASS — Injizierte Bestands-, Feedbackzell- und gepaarte Ereignisabweichungen erkannt. |
| `test_N09_reference_divergence_rejected` | PASS — Mutierte Referenzauswahl terminal als REFERENCE_CHOICE erkannt. |
| `test_N10_error_cleanup_and_resource_paths` | PASS — 24 Fehlerpfade (U/R × zwölf Checkpoints) mit Ressourcenmessung und terminalem Cleanup. |
| `test_N11_bad_input_ticket_and_boundaries` | PASS — Falscher Index, Dimension, nichtendliche Werte, falsches Feedbackziel sowie Überschreitung der neutralen Framegrenze abgefangen. |
| `test_N12_lossless_archive_and_corruption` | PASS — Archiv-Rundreise verlustfrei; Hashkorruption und neu gehashter falscher Fehlerwert erkannt. |
| `test_N13_selected_only_feedback_coupling` | PASS — Feedback nur für Gewinner als injizierte Kopplung bei Ziel 15 erkannt. |
| `test_N14_heap_limit_and_terminal_cleanup` | PASS — Injizierter Zusatzheap 16.385 Byte verletzt Grenze 16.384; terminaler Cleanup bestätigt. |

N10 injiziert: frozen, validated, generation, ec, ep, role, offset, quality, valid, published, promotion_validated und promotion_generation. Nach Fehlern sind Bank, ausstehende Vorhersage, Kandidat und Retained-Bestand bereinigt. N11 verwendet teilweise eine breite Exception-Prüfung; es ist damit kein exakter Fehlerklassennachweis für jeden Eingabefehler verbunden.

## Reguläre Nichtäquivalenz ohne Nutzenbehauptung

Für j=0..47 gilt V(x)[j]=x+j/4096. Jeder reguläre Handblock ist [V(cue), V(0.5), V(target), V(0.0625)]. Der feste Handfall verwendet
[(X,A),(X,A),(Y,B),(Y,B),(X,A),(X,B),(Y,B),(Y,A)] zweimal,
mit X=0.125, Y=0.875, A=0.25 und B=0.75. Das sind 16 Blöcke/64 Frames, keine 1024-Frame-Forschungsgeschichte. Die Handfolge enthält die 3:1-Zuordnungsstruktur und wurde nicht durch Optimierung eines Leistungsabstands gewählt.

Nach dem ersten XA-Block ist Originalnachfolger 3 verfügbar. Für Ziel 7 ist diese Kandidatenhypothese noch kalt: U gibt V(0.5) als Persistenz aus, R gibt V(0.25) aus dem Original 3 aus; R-Schlüssel (1,1,0). Der Unterschied entsteht aus regulärer Aufnahme und Auswahl, ohne künstlich gesetzten Zustand. Beide Ausgaben sind vor dem Ziel eingefroren. Damit ist mögliche Nichtäquivalenz belegt; weder ein mittlerer Nutzen von R noch ein Nutzen von U ist damit nachgewiesen. Der künstliche Gleichstandstest N06 ergänzt ausschließlich die Randfallabdeckung.

## Ereignisweise Gleichheit und Unabhängigkeit

U und R laufen getrennt aus eigenen Zuständen; die Referenz verwaltet ebenfalls eigene Zustände. Es wird kein divergierter Bestand nachträglich synchronisiert. Geprüft werden Bestand samt Originalwerten/-metadaten, Kandidaten/Retained-Spuren, Formierungsframes, Hinweise, Eingangsintervalle, eingefrorene Originale, Persistenzframe, Zähler, vollständige berechtigte Hypothesen, Tickets, EC/EP-Zellen und Feedbackupdates.

Der gemeinsame Bankvergleich maskiert ausschließlich Bytes 202/203 (Auswahl und Auswahlgrund). Entscheidungen und Ausgaben werden separat gegen die jeweilige Referenz geprüft und als Unterschiede archiviert. So wird die beabsichtigte Auswahlabweichung nicht fälschlich als Bestandsabweichung gewertet. Die vollständigen Treffer-/Hypothesen-Receipts werden ebenfalls gepaart verglichen.

Der 64-Frame-Fall enthält je Arm 192 äußere Vorher-/Nachher-Ereignisse. Der 48-Frame-Lebenszyklus enthält je Arm 144 äußere und 552 interne Call/Return-Ereignisse an Aufnahme, Promotion, Pruning, Formierung, Segmentabschluss, Hinweis, Feedback, Freigabe und Owner-Cleanup. Die Gleichheit gilt für diese instrumentierten Grenzen und Fälle, nicht als mathematischer Beweis für sämtliche möglichen Ausführungen. N03 erzwingt Promotion und Verdrängung; die archivierten Promotionsaufrufe können auf ausstehende Tickets geprüft werden. N08/N13 zeigen, dass absichtliche Rückkopplung nicht still akzeptiert wird.

## Ressourcen in den neutralen Fällen

Bytewerte, außer ausdrücklich als Anzahl bezeichnet. Zusammenfassung über normalen 64-Frame-Fall und 24 injizierte Fehlerpfade; Receiptwerte stammen aus dem normalen Fall.

| Messgröße | U | R |
| --- | ---: | ---: |
| Zusatzheap-Peak | 5806 | 5806 |
| Armgraph samt Eingangsrecord: größter Vorher-/Nachherwert | 32632 | 32624 |
| Vorhergraph plus gemessene Transiente / Nachhergraph: Maximum | 36164 | 36156 |
| Gemessene Python-Transiente | 4254 | 4254 |
| Originalframes (Anzahl, obere Zählgrenze) | 16 | 16 |
| Originale plus Ausgaben (Anzahl, obere Zählgrenze) | 18 | 18 |
| Receiptbytes im Normalfall | 702 | 713 |
| Konservative UTF-8-Obergrenze im Normalfall | 1404 | 1426 |
| Eingangsrecord separat ausgewiesen | 1959 | 1959 |
| Gepackte Bank | 416 | 416 |

Die Zusatzheapgrenze von 16.384 Byte ist nicht die Gesamtgraphgrenze. Die gezählten Originale (16) und kombinierten Slots (18) bleiben unter 18 beziehungsweise 20; Ausgabeslots werden auf höchstens zwei geprüft. Receiptgrenzen: 16.384 Byte und konservativ 32.768 Byte UTF-8. Der Eingangsrecord ist im Gesamtgraph enthalten und wird nicht nochmals addiert. Aliase werden im tiefen Graphdurchlauf nur einmal gezählt.

Der interne Ereignistrace läuft separat von der Ressourcenmessung, damit gespeicherte Beobachter-Snapshots nicht als Armzustand verbucht werden. Diese Beobachterkosten müssen in einer späteren Prozessgesamtbilanz trotzdem enthalten sein. Die gemessene konservative Python-Obergrenze ist keine Garantie über native Allokationen, Konstruktortransienten oder alle möglichen Verläufe. Es gibt hier keine Windows-Job-, Laufzeit- oder vollständige Forschungsexportqualifikation.

## Archive, Verlustfreiheit und Abnahmestand

| Archiv | Frames | gzip-Bytes | Expandierte Bytes | Umfang |
| --- | ---: | ---: | ---: | --- |
| D_hand_case.json.gz | 64 | 51765 | 3860092 | reguläre Nichtäquivalenz, äußere Ereignisse, Ressourcen |
| lifecycle_trace.json.gz | 48 | 124396 | 13380342 | zusätzliche interne Ereignisse |

Beide Archive speichern Quellenwerte, Zustände, Hypothesen, Ausgaben, Fehler und Updates. Der vorhandene Erzeuger prüfte nach Komprimierung/Dekomprimierung die kanonische Bytegleichheit mit dem Ausgangsrecord. Der Archivprüfer prüft Hash, Umfang, gepaarte Ereignisse, Zielvollständigkeit und Fehler aus archivierten Ausgaben/Quellen; er ersetzt keine eigenständige vollständige Forschungs-Statistikprüfung und rekonstruiert nicht jedes Update unabhängig neu. Die laufbegleitenden unabhängigen Referenzen liefern den zusätzlichen Zustands-/Updatevergleich.

**Konkreter Exportblocker:** lifecycle_trace expandiert auf 13.380.342 Byte und überschreitet bereits im kleinen Fall die geplante 4-MiB-Grenze (4.194.304 Byte) pro Forschungsfall. Die gzip-Größe allein genügt daher nicht. Diese Grenze wurde weder gelockert noch durch Weglassen von Ereignissen umgangen. Das neutrale Archiv ist als Beleg lesbar, sein derzeitiges Format ist nicht forschungstauglich.

Zu Abschnitt 7 des Konzeptvertrags: Kriterien 1–6 sind im fokussierten neutralen Umfang durch die oben genannten Implementierungs-, Referenz-, Mutations-, Ereignis- und Nichtäquivalenzbelege abgedeckt. Kriterium 7 ist nur hinsichtlich neutraler Archivverlustfreiheit belegt; Quellen-, Bootstrap- und Statistikqualifikation ist nicht beauftragt und nicht erfolgt. Kriterium 8 ist für die gemessenen Armgraphen und Fehlerpfade belegt, jedoch nicht als vollständige Prozess-/Forschungsgrößenbilanz. Deshalb darf der Status nicht als Erfüllung sämtlicher Vorforschungsbedingungen ausgegeben werden.

## Technische Restlücken und begründeter nächster Schritt

Als nächstes empfehle ich dem Projektleiter einen eng begrenzten neutralen Auftrag zur verlustfreien Kompaktierung des Ereignisarchivs mit unabhängigem Decoder. Abnahme: alle bisherigen Zustandsfelder und Ereignisse exakt rekonstruierbar, Manipulationen erkannt, expandierte Darstellung innerhalb der unveränderten vereinbarten Grenze für die freigegebenen neutralen Prüffälle. Keine Beschneidung des Belegumfangs und keine Änderung der U/R-Auswahlregeln.

Danach bleiben die Gesamtprozess-/Beobachterkosten, Konstruktortransienten und die Machbarkeit im später separat beauftragten Umfang zu qualifizieren. Ein kleiner Archivtest allein belegt noch keine Machbarkeit für 32 vollständige Geschichten. Forschungsquellen, Bootstrapmatrix, Größenablauf und Einmallauf benötigen weiterhin einen eigenen passenden Auftrag; sie werden aus dieser Empfehlung nicht gestartet. UFB1 bleibt nicht zur Implementierung beauftragt. Es gibt keinen Nachweis allgemeiner Memory, Semantik, Kognition, eines Effizienzgewinns oder eines Leistungsvorteils aus diesem Entwicklungspaket.

## Belegverweise

- [tests.json](C:/Users/TV/Documents/MCM_FIELD_ORGANISM/workspace/reports/s2uc/ura1-neutral-development-20261014-01/tests.json)
- [tests.txt](C:/Users/TV/Documents/MCM_FIELD_ORGANISM/workspace/reports/s2uc/ura1-neutral-development-20261014-01/tests.txt)
- [evidence.json](C:/Users/TV/Documents/MCM_FIELD_ORGANISM/workspace/reports/s2uc/ura1-neutral-development-20261014-01/evidence.json)
- [resource-summary.json](C:/Users/TV/Documents/MCM_FIELD_ORGANISM/workspace/reports/s2uc/ura1-neutral-development-20261014-01/resource-summary.json)
- [normal-resources.json](C:/Users/TV/Documents/MCM_FIELD_ORGANISM/workspace/reports/s2uc/ura1-neutral-development-20261014-01/normal-resources.json)
- [error-resources.json](C:/Users/TV/Documents/MCM_FIELD_ORGANISM/workspace/reports/s2uc/ura1-neutral-development-20261014-01/error-resources.json)
- [D_hand_case.json.gz](C:/Users/TV/Documents/MCM_FIELD_ORGANISM/workspace/reports/s2uc/ura1-neutral-development-20261014-01/D_hand_case.json.gz)
- [lifecycle_trace.json.gz](C:/Users/TV/Documents/MCM_FIELD_ORGANISM/workspace/reports/s2uc/ura1-neutral-development-20261014-01/lifecycle_trace.json.gz)
- [development-binding.json](C:/Users/TV/Documents/MCM_FIELD_ORGANISM/workspace/reports/s2uc/ura1-neutral-development-20261014-01/development-binding.json)
- [closure.json](C:/Users/TV/Documents/MCM_FIELD_ORGANISM/workspace/reports/s2uc/ura1-neutral-development-20261014-01/closure.json)
- [URA1-Konzeptvertrag](C:/Users/TV/Documents/MCM_FIELD_ORGANISM/workspace/docs/S2UC_URA1_AUSWAHLABLATION_KONZEPT_20261014.md)
