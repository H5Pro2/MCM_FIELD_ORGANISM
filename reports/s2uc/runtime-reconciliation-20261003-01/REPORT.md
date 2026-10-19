# Statischer Laufzeitabgleich – 2026-10-03

Ergebnis: gleiche Fach-/Ressourcenbelege und derselbe aktive Frame-Blattfall,aber unterschiedliche Objektidentitäten und Aufrufstapel. Die zusätzlichen42,0623245 Sekunden lassen sich aus den gespeicherten Messungen nicht kausal aufteilen. Kein neuer Replay,keine operative Codeänderung und keine neue Autorisierung.

## Paarvergleich und Messgrenzen

| Fixture/Arm | Visitorqualifikation Replay s | Integration Startintervall s | Differenz s | Basistrace-Stichproben |
|---|---:|---:|---:|---:|
| N1/M | 10.897546 | 15.318321 | 4.420775 | 60872 |
| N1/E | 10.683822 | 15.269207 | 4.585385 | 60872 |
| N1/K | 9.969323 | 14.767199 | 4.797876 | 60872 |
| N1/P | 10.111891 | 15.186732 | 5.074841 | 60872 |
| N2/M | 14.628340 | 20.700047 | 6.071707 | 76050 |
| N2/E | 14.967013 | 20.432267 | 5.465254 | 76050 |
| N2/K | 14.159261 | 20.184933 | 6.025672 | 76050 |
| N2/P | 13.840664 | 20.213212 | 6.372548 | 76050 |

Exakt gespeicherte Summen: Visitorqualifikation 99.2578592 s,integrierte Baseline-Kategorie 141.3201837 s,Mehrzeit 42.0623245 s (42.38%). Je Arm fehlen der Integration monotone Start-/Endzeiten und CPU-Zeiten. Deshalb sind die zweiten Tabellenwerte ausdrücklich UTC-Startintervalle,keine isolierten Replayzeiten. Beim letzten P endet das Intervall am worker-complete-Zeitstempel;P enthält außerdem nachfolgende Fallprüfung.
Die acht Intervalle summieren sich zu 142.071918 s und liegen zusammen 0.751734 s über der exakten Baseline-Kategorie. Diese Differenz erlaubt keine genaue Aufteilung auf einzelne Arme und setzt vergleichbare UTC-/Monotonuhren voraus. Die gesamte Engineverwaltung außerhalb der Baseline-Kategorie beträgt nur 1.047881 s;externes Materialisieren,Exportieren und Fallprüfen können daher die42,06 s innerhalb der Baseline-Kategorie nicht erklären.
Die Qualifikationsuhr startet nach Installation des Visitorpatches und umfasst Profil-Digest,Replay und Deadlineprüfungen;Export liegt außerhalb. Die integrierte Kategorie umfasst zusätzlich checked/MagicMock/active,acht Manifestleseprüfungen,Patchaufbau/-abbau und die gesamte Replayarbeit. Die eigentliche Quellenmaterialisierung,Quelleneinlesung/-validierung,äußere Exporte,Ressourcenprüfung und Fallauswertung liegen außerhalb dieser Kategorie. Beide Replays enthalten dieselbe interne Belegerzeugung und Referenzfortschreibung.

## Ist der kurze Frame-Pfad wirksam?

Ja,statisch und durch die gespeicherte Aktivierungsprüfung gestützt: beide Pfade ersetzen BudgetObserver.trace durch dieselbe FrameLeafBudgetObserver.trace. Die Integration prüfte die aktive Methode unmittelbar vor original_replay. Gleiche gespeicherte samples-Werte und alle übrigen Meterfelder sind zusätzlich belegt,aber kein Beweis gleicher Besucherarbeit.
JSON erzeugt zunächst Listen;GatedReplay.take normalisiert jede Wertefolge mit tuple(values),bevor PairContextAdapter.accept_perception einen exakten Frame konstruiert. Alle48 Werte sind echte floats und die Bindungsfelder skalare Strings/Integer. Damit bleibt der kurze Frame-Pfad an denselben Frame-Objekten anwendbar. Die JSON-Listen sind kein Fallback-Auslöser im fertigen Frame. Weder Leaf-Hit-Zähler noch pro-Objekt-Visit-Zähler wurden gespeichert;ihre historische Zahl wird nicht erfunden.

## Belegte Unterschiede im Beobachtungsaufwand

1. Identität der Skalarwerte: Die direkte Fixture konstruiert jeden Vektor mit (x,)*48,einem Float-Objekt in48 Slots. Der integrierte Pfad liest die Quelle aus JSON und erzeugt48 getrennte Float-Objekte mit gleichen Werten. Read-only-Dekodierung beider gespeicherter Quellen bestätigt48 verschiedene IDs je Vektor;die ursprünglichen Laufobjekte sind nicht archiviert. tuple(values) bewahrt diese Referenzen. Die Quellen sind numerisch vollständig gleich.
   Der neue Blattfall überspringt ausschließlich Frame-Payloads. PerceptionSample ist ebenfalls eine Dataclass,erhält aber keinen Blattfall. In relevanten Adapterstackframes ist sample als lokale Variable erreichbar. Dessen values wird weiterhin durchlaufen. Beim direkten Vektor endet visit für47 wiederholte IDs sofort an seen;beim JSON-Vektor erreichen diese47 Floats jeweils Typprüfungen bis dataclasses.is_dataclass. Das ist ein konkreter zusätzlicher Codepfad pro entsprechendem Samplebesuch,kein Nachweis seiner summierten Sekunden.
2. Aufrufstapel: In der Qualifikation steht matrix direkt unter replay. In der gemessenen Integration stehen dort active,unittest.mock._execute_mock_call,_mock_call,__call__,integrated_baseline,checked,timed.call,execute und die äußere execute-Hülle. Der Visitor läuft mit cursor.f_back bis zum Stackende und wertet Path(cursor.f_code.co_filename).name auch für später ausgeschlossene Rahmen aus. Mindestens die fünf Test-/Mock-Rahmen active,checked und die drei Mock-Dispatcher fehlen im späteren operativen Pfad. Gleiche Ressourcenpeaks oder samples zählen diese zusätzliche Arbeit nicht.
Hostschwankung bleibt möglich,aber ungemessen: Für die Integration fehlen Prozess-CPU-Zeit,Lastprofil und Wiederholungen. Die höhere integrierte Laufzeit darf weder ausschließlich dem Host noch ausschließlich den beiden Codeunterschieden zugeschrieben werden. Der gespeicherte frühere Laufzeitaudit weist den Basisvisitor als Hauptkostenebene aus;er misst nicht die Anteile dieser beiden Unterschiede im aktuellen Vergleich.

## Nach Länge und Kontext gegliederter Zeitplan

Für stabile Fälle dient N1,für Konkurrenzfälle N2 als neutraler Bezug. N2 enthält14 konkurrierende Prognosen pro Baseline. Die historischen abgeschlossenen wechselnden Fälle zeigen tatsächlich konkurrierende Kontexte. Nicht ausgeführte Fälle werden nur anhand ihres vorab festgelegten Blockwechsels zugeordnet;ihre Laufzeiten oder Konkurrenzbelege werden nicht ergänzt.

| Länge | Kontextklasse | geplante Arme | historisch beobachtet | historischer Maximalabstand s | beobachtete Konkurrenzprognosen |
|---|---|---:|---:|---:|---|
| 48 | stable | 8 | 8 | 17.421689 | [0, 0] |
| 48 | competing | 56 | 56 | 26.864836 | [2, 8] |
| 80 | stable | 8 | 4 | 29.819829 | [0, 0] |
| 80 | competing | 56 | 43 | 48.458863 | [4, 14] |

Alle Szenarien behalten25 Prozent Zuschlag plus180 s Verwaltung,30 s U und60 s Abschluss. Keine Werteauswahl innerhalb einer Klasse:verwendet wird jeweils das Maximum;alle Messpaare bleiben im JSON enthalten.

| Modell | Gesamthochrechnung s | Reserve zu3600 s |
|---|---:|---:|
| Bisheriger konservativer Plan unverändert | 6330.088 | -2730.088 |
| Historische vier Klassen × schwächste neutrale Entlastung | 4760.362 | -1160.362 |
| Historische vier Klassen ohne unbewiesenen Entlastungstransfer | 6015.074 | -2415.074 |
| Integrierte N1/N2-Maxima;80er-Zeit auch für48er | 3474.373 | 125.627 |

Das historische Klassenmodell mit Entlastung verwendet einheitlich die ungünstigste NEW/OLD-Quote 0.781602082;keine günstigere N2-Quote. Die Übertragbarkeit dieser Quote auf JSON-Quellen und andere Aufrufstapel ist gerade ungeklärt. Das Modell ohne Transfer zeigt diese Unsicherheit ausdrücklich.
Das neutrale Kontextmodell reduziert48er-Zeiten NICHT linear auf60 Prozent,sondern berechnet auch dafür den vollen beobachteten80er-Maximalabstand. Dennoch ist es keine obere Schranke: N1/N2 decken nicht alle Rasterkontexte ab,Test-Mocks unterscheiden sich vom operativen Pfad,und eine Messung kann Host-/Pfadschwankung nicht begrenzen. Ein rechnerisch positiver Rest dieses Modells ist deshalb kein Reservebeleg. Historische48er-Messungen bleiben im Klassenmodell erhalten;fehlende neue48er-Messungen werden nicht ersetzt oder behauptet.

## Genau eine Anschlussentscheidung

Kein weiterer Patch ist durch die bisherigen Zeitdaten ausreichend begründet. Der eng eingegrenzte offene Befund lautet: Mehrkosten des Basisvisitors durch Float-Identitäten und äußere Stackrahmen sind statisch belegt,ihre Zeitanteile und möglicher Hostanteil nicht gemessen.
Vorschlag zur separaten Beauftragung: genau eine neutrale2×2-Diagnose mit N2/M,je80 Positionen,vier Replays ohne Wiederholung. Faktoren: direkte Fixture mit geteilten Float-Referenzen versus aus gespeichertem JSON gelesene Werte;direkter Qualifikationsaufruf versus exakt die integrierte Testhülle. Feste Reihenfolge:direkt/geteilt,direkt/JSON,Testhülle/JSON,Testhülle/geteilt. Derselbe neue Visitor,aktiver Trace,gleiche Quelle nach kanonischen Werten,gleiche Deadlineprüfung und Exportgrenzen.
Notwendige Messgrößen: monotone Replayzeit und Prozess-CPU je Arm;Zahl relevanter Traceereignisse,Stackrahmen-/Dateinamenprüfungen,PerceptionSample-Besuche,unterschiedliche Float-IDs und Frame-Blattfalltreffer. Diagnosezähler müssen identisch in allen vier Armen aktiv sein;ihre Kosten sind offenzulegen. Vollständige Fach-/Meterbelege vergleichen. Vier Faktor-Kombinationen sind das kleinste Design,das beide geänderten Faktoren und ihre Wechselwirkung trennt;ein einzelnes Paar würde sie vermischen. Kein allgemeiner statistischer Hostnachweis aus einem Durchgang.
Abnahme dieser vorgeschlagenen Diagnose: Mehrarbeit den beiden Faktoren anhand der Zähler zuordnen und CPU-/Wall-Unterschiede beziffern;erst danach genau einen nötigen Eingriff auswählen. Dieser Vorschlag ist weder implementiert noch ausgeführt oder autorisiert. Keine weitere Optimierungsvariante in diesem Auftrag.

Raster32 bleibt geschlossen/global NOT_EVALUABLE;keine neue Autorisierung. Ein späterer Lauf bleibt eine technische Wiederholungsprüfung bekannter Daten,keine unberührte Evaluation.
