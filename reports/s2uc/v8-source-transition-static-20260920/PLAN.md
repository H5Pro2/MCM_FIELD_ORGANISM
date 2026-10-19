# Statischer Anschlussplan: neutraler V8-Nachweis zum gebundenen S2-UC-Quellenvergleich

**Ergebnis:** Die fuenf Quellen, ihre Payloadhashes, Zeit-/Profilbindungen und sieben Zielherkuenfte sind bereits festgelegt. Neu erforderlich ist ein getrennter, beleggebundener Quellen-Ausfuehrungseinstieg mit Anschluss an den vorhandenen V8-Kern und den vollstaendigen Prozessbegrenzer. Mit dem derzeitigen Bestand ist dieser Zusatz innerhalb 720896 Codebyte **nicht ausgewiesen**: 54 Byte frei stehen einem geschaetzten Nettozusatz von 18300–31400 Byte gegenueber. Keine Grenzaenderung oder automatische Einsparung unterstellt.

Nur statische Datei-, JSON- und AST-Auswertung mit Standardbibliothek; keine Projektmodule importiert, keine Tests, Materialisierung, Quellenproduktion oder Laufbindung ausgefuehrt. Ausschliesslich dieser Plan und sein [statischer Beleg](static-evidence.json) wurden neu geschrieben. Unabhaengige Abnahme bleibt offen.

## Verbindliche Grundlage

Der aktuelle direkte Auftrag betrifft den bestehenden S2-UC-Vergleich. Aeltere V6-/V14-Dateien werden als Quellen-/Erwartungsreferenz gelesen, nicht als heutige Zulassung. Insbesondere bezeichnet der historische Dateiname V14 weiterhin ein `s2uc.run-binding.v1`-Dokument; er ist keine aktuelle V8-Ausfuehrungsbindung.

Quelle: `reports/s2nu/s2nu-source-preseal-20260909-01/execution-plan.json`, tatsaechlich gelesener SHA256 `6e64fbd5b7e86f16156b6d68bd5f7dbda3fefa8f223b2a31114bf3293eaa5f10`; Execution-Digest `1d2787da42fe01e6bb960ad545bcfbf96a3e4abd036ce91033b325c450d7f2c7`. Die gelesene V14-Quellenbindung hat SHA256 `353915dbdb1fe481f76c5dd4bcbc42582998353d7c243b29232e4115629d94ea`.

Alle Quellen sind Mono-PCM_F32LE, 48000 Hz, 4800 Samples / 19200 Byte. Rohprofil `5c6b2b19281a44023497b435a96b1051905af4bbac493cae7e699ea1320392c7`; Halbprofil `4a56de2f630055816533ecb45cdef5662157993bc1192023d01cf29e92247c9f`. Diese Werte bleiben unveraendert.

| Symbol / Quelle | Stream / Fenster | Natives Samplefenster | NJ-Index | Verwendungen | Payload-SHA256 |
|---|---|---|---:|---:|---|
| a / nu-s02-w00 | s02 / 0 | [24000, 28800) | 50 | 11 | `50e67af67fee98adc0ccda22430178e938d4c676072852915fa45e0447031b61` |
| b / nu-s02-w01 | s02 / 1 | [28800, 33600) | 60 | 13 | `6eed63affabbb8c19d00e8a780e851418eb267beff96769108506373251c1c2a` |
| c / nu-s02-w02 | s02 / 2 | [33600, 38400) | 70 | 18 | `17c626793f126ef30b0568cd4a12186da1ed6ffc5da947c0f418916b1eeaafa8` |
| d / nu-s02-w03 | s02 / 3 | [38400, 43200) | 80 | 15 | `29d2e5a3b99945ebb6f9a7c01fa22f42441ea76bd1e0e5898ccbf5bdc2c1a1c8` |
| e / nu-s02-w04 | s02 / 4 | [43200, 48000) | 90 | 1 | `68c73c6cddd0b41cb021af744e172bda7a06b76ff4dc869c2ed2f69b245ac658` |

Rezept- und Quellreihendigest sowie vollstaendige bestehende Metadaten stehen je Quelle in `static-evidence.json`. Die fuenf V14-Quellreihen stimmen in allen dort gebundenen Feldern mit dem versiegelten Plan ueberein. Alle 58 neutralen und realen Endpunktverwendungen stimmen abgesehen vom PCM-Hash feldweise ueberein. Es wurde kein Payloadhash durch Erzeugung von PCM neu bestimmt.

## Konkrete Ersetzungen und Anschluesse

| Stelle | Neutraler V8-Stand | Erforderlicher spaeterer Anschluss |
|---|---|---|
| `tools/_s2uc_binding_v8.py:25`, `manifest()` | Ueberschreibt jeden echten PCM-Hash mit `PCM_HASH` aus 19200 Nullbytes. | Separater Quellenbinder verwendet das unveraenderte Manifest aus `_s2uc_source_binding.py:59` ohne diesen Austausch. Ereignisfolge, Profil, Zeitfelder und Grenzen bleiben gleich. Realer Manifestdigest ist bereits `a357979bf70dd6b90b0db9c7f3098e8b28fbb612e10792dcb588c6fe29062fca`; neutral ist `da506fabb55b87cf8f0063529bb53d08d86723ee9af81bdc532a54b7baa50c27`. Keine neue Reihenfolge erfinden. |
| `_s2uc_binding_v8.py:36`, `sources()` | Fuenf Endpunktreihen tragen denselben Nullhash; Version `s2uc.neutral-sources.v8`. | Genau fuenf echte Quellenbindungen und die vorhandenen 58 Verwendungen in eigenem Ausfuehrungsschema binden. Rohplan mit Rezept-/Quelldigests separat hashreferenzieren. An `SourceAdapter` nur die sieben Endpunktfelder geben; keine vollstaendigen Planzeilen einschieben: dessen Feldvergleich wuerde etwa `recipe`/`stream_id` im Endpunkt suchen. |
| `_s2uc_binding_v8.py:89`, `validate()` und `contract()` | Exakte Autorisierung `ONE_NEUTRAL_EXECUTION`, `ZERO_PCM_F32LE`, `real_sources=False`; neutrale UUID-Lauf-ID; Vergleich gegen fest erzeugte Nullinhalte. | Separater strikter Quellen-Ausfuehrungsbinder: explizite freigegebene Laufidentitaet/Ausgabe, Einmaligkeit, exakt die fuenf Quellen und feste Qualifikationsreferenzen. Keine Lockerung durch einen frei setzbaren `real_sources=True`-Schalter; der neutrale Binder muss reale Bindungen weiter ablehnen. |
| `_s2uc_binding_v8.py:62`, `evidence()` | Erzeugt erwartete neutrale Fixturebelege mit `formal_qualification=False`. | Tatsaechlich ausgefuehrte Qualifikationsprotokolle, genaue Test-IDs, Version, Code-/Werkzeuginventar und Abnahmereferenz pruefen. Die erzeugten Fixture-OK-Felder duerfen nicht in eine reale Freigabe umetikettiert werden. |
| `tests/test_s2uc_execution_v8.py:70` und Begrenzungsskript `child()` | Supplier liefert ausschliesslich `ZERO_PCM`; Fehler werden fuer Tests injiziert. | Nach Zulassung und Besitznahme genau einen Bedarfssupplier anschliessen: vorhandenes `s2uc_run_bound_once.nu_payload_supplier()` / `_s2nu_private_source_binding.pcm_window(WindowSpec(2,0..4))`. Fuenferauswahl vorher strikt pruefen. Generator und Rezept bleiben identisch; keine Vorproduktion, keine Vorversiegelung, kein Fenster-/Wertecache. |
| `_s2uc_execution_v8.py:162`, `run_neutral()` und `_Publication` | Lebenszyklus ist mit neutralem Binder, Scope und Belegversion gekoppelt. | Gemeinsamen privaten Kern nach validiertem Kontext verwenden; neutraler Einstieg behaelt seine Schranken, neuer Quellen-Einstieg liefert nur streng geprueften Quellenkontext. Publikationsscope/-version und Record-Ausfuehrungsreferenz eindeutig trennen. Keine zweite Implementierung von Materialisierung oder Publisher. |
| Korrigiertes `reports/s2uc/v8-process-limit-corrected-20260920/limit.py` | Baut Testfixtures; feste Testfaelle; Nullsupplier oder injizierter Fehler. | Neues begrenztes Prozesseingangsstueck fuer explizite spaetere Laufbindung. Vorimport-Nachweis, Codehashes, Jobmitgliedschaft, Ausgabeidentitaet und Quellenzulassung verbinden. Testfallnamen und Testfixture-Erzeugung sind keine Laufzulassung. Vollstaendigen Parent-/Child-/Messhelferbestand in das fixe Codeinventar aufnehmen; nicht nur eine Behauptung im Bericht. |
| `s2uc_run_bound_once.py:17`, `_s2uc_run_binding.py:499` | Oeffentlicher Einstieg stoppt unbedingt; V8 wird explizit abgewiesen. | Jetzt unveraendert gesperrt lassen. Spaeteren quellenspezifischen Eintritt zunaechst separat und ebenfalls geschlossen vorbereiten. Eine tatsaechliche Oeffnung waere ein gesonderter Schritt nach Qualifikation, unabhaengiger Abnahme und expliziter Einmallaufentscheidung. Der historische Default V14 wird nicht reaktiviert. |

Die historische Kennung `...-02` ist zwar als vorbereitet dokumentiert und die dort genannte Ausgabeablage fehlt aktuell. Das ist keine heutige Freigabe und wird hier weder neu reserviert noch als finale Laufidentitaet festgeschrieben.

## Vorhandene Pruefungen bleiben fachlich unveraendert

- `_s2uc_source_adapter.SourceAdapter`: geordnete 58 Einzelverwendungen, Quellen-/Endpunktvergleich vor Supplier, genau ein Aufruf der bestehenden Materialisierung je Verwendung. Fuenf Quellen bedeuten weiterhin 58 Materialisierungen, nicht fuenf gecachte Ergebnisse.
- `_s2ty_audio_materialization.materialize`: PCM-Hash, 19200 Byte, F32LE-Domaene, bestehender Rezeptor und NJ-Halbprojektion sowie direkte Hash-/Rezeptor-/NJ-Zaehler. Kein neuer Rezeptor, keine andere Skalierung.
- `_s2uc_neutral_connection.execute`: dasselbe 48-Werte-Tupel fuer beide Arme pro Ereignis, drei frische Geschichten, unveraenderte Close-/Hintfolge. Erhaltung der wissenschaftlichen Armregeln.
- `_s2uc_execution_v8._receipt` und `verify_materialized`: verpflichtender Receipt, Rekonstruktion von Werten/Projektionsdigest, Profil, Zeit und Querbindungen, Abgleich mit dem beobachteten Materialisierungsdigest. Die PCM-Pruefung verwendet den gebundenen echten Endpunkthash; sie wird nicht entfernt. Keine nachtraegliche Behauptung einer vollstaendigen Rohrezeptornachrechnung aus nicht gespeicherten Rohwerten.
- `_Source.snapshot`, `_Owners` und gemeinsamer Lebenszyklus: voller/partieller Quellenabschluss, 57 Erfolge beim gescheiterten 58. Versuch, pending Receipt zwischen Armaufrufen, Ownerabschluss, Primaerfehler, Gate-finally und Einmaligkeit durch Lauf-ID/fehlende Ausgabeablage. Keine neue Wiederanlauf- oder Loeschsicherheit behaupten.
- `_s2uc_record_codec`, `_s2uc_publication_v7._finish_record`: verlustfreier Codec, Kandidatengroesse vor Publikation, getrennte erneute Verifikation, Hashanker Record/Verifikation/Terminal, ein Stagingname, vollstaendige Fehler-/Minimal-/Stagingbilanz. Der innere Algorithmus bleibt; lediglich Ausfuehrungskontext und Belegscope werden angebunden.
- Fehlt wegen OOM oder Prozessabbruch ein Produktabschluss, bleibt der Fall nicht auswertbar. Ein externer Beleg ersetzt keinen Produktabschluss. Garantierte Publikation bei echter Erschoepfung ist keine neu einzufuehrende Anforderung.

## Unveraenderte wissenschaftliche Erwartungen

A=abcd, B=dcba, C=abce; drei frische Geschichten, insgesamt 69 Ereignisse, 44 Formationsframes, 14 Hintframes / sieben Entscheidungen, elf Segmentcloses und 58 Endpunkte. G1/G2/G3: 22/14/22 Endpunkte. Je Arm hoechstens zwoelf Traceframes und getrennt zwei Hintframes; NJ-Frame 48 Binary64-Werte. Keine Schwelle, Gleichheitsregel, Quelle oder neue Forschungsfrage hinzufuegen.

| Hintschluessel | Bestehende Zielherkunft | Erwartung S2-TW | Erwartung S2-UA |
|---|---|---|---|
| g1/12 | A: g1-p1, g1-p2 | TRACE_MATCH | TRACE_MATCH |
| g1/24 | A: g1-p1, g1-p2 | ABSTAIN_AMBIGUOUS_RETAINED_TRACE | TRACE_MATCH |
| g1/26 | B: g1-p3 | TRACE_MATCH | ABSTAIN_NO_RETAINED_TRACE |
| g2/38 | A: g2-p1 | TRACE_MATCH | ABSTAIN_NO_RETAINED_TRACE |
| g3/60 | A: g3-p1 | TRACE_MATCH | TRACE_MATCH |
| g3/67 | A: g3-p1 | TRACE_MATCH | ABSTAIN_NO_RETAINED_TRACE |
| g3/69 | B: g3-p3, g3-p4 | TRACE_MATCH | TRACE_MATCH |

**Keine offene Neufestlegung dieser Ziele:** `_s2uc_run_binding.TARGETS` und die V14-Datei binden die sieben Zielherkuenfte bereits. Die aeltere Aussage im Vorbereitungsdokument, diese seien noch ungebunden, beschreibt einen ueberholten Zwischenstand. Die Daten muessen in einer kuenftigen Quellenbindung unveraendert referenziert werden. `_s2uc_evaluation.EXPECTED` bleibt die Prueferwartung, nicht ein in den Arm eingespeistes Ziel.

Der derzeitige Evaluator liefert Entscheidungspaare und Erwartungsverletzungen; `candidate_gains`/`candidate_losses` bleiben leer. Ein reales Quellensignal macht daraus nicht automatisch einen Nachweis von Erinnerungsgewinn. Dieser Anschlussplan fuegt keine neue Gain-/Loss-Regel hinzu. Abweichungen, Mehrdeutigkeit und Enthaltung werden unveraendert berichtet, ohne die Hypothese nach dem Ergebnis umzuschreiben.

## Tatsaechlich offene Voraussetzungen

| Bereich | Was fehlt | Was daraus nicht folgt |
|---|---|---|
| Implementierung | Getrennter strikter Quellenbinder; Wiederverwendung des V8-Lebenszyklus hinter zwei getrennten Zulaessigkeitspruefungen; gebundener Bedarfssupplier; quellenspezifischer Prozesseinstieg; Nachweisleser fuer echte Qualifikation und fixer Inventareintrag aller Prozesswerkzeuge. | Kein neuer NU-Generator, Rezeptor, Memoryarm oder Publisher erforderlich. Fuenf Payloadhashes und Zielherkuenfte fehlen nicht. |
| Qualifikation | Konkreter Anschlussstand samt Parent/Child mit aktuellen Hashes; Zulassungs-/Mischformatgegenproben, Nichtnull-Receipt-/Codecfaelle, Fehlerpraefix und Prozess-Vorimportnachweis im finalen Anschluss; aktuelle vollstaendige Bytebilanz der Bindungs-/Qualifikationsartefakte. | Die 138 bestehenden Tests, Null-PCM-Erfolge und injizierte MemoryError-Abschluesse autorisieren keine echten Quellen. Kein pauschales Wiederholen aller bisherigen Speicherexperimente. |
| Unabhaengige Abnahme | Bisheriger V8-Stand bleibt unabhaengig unabgenommen; spaeter muss der tatsaechliche Anschluss samt Qualifikationsbelegen und Begrenzungsrevision beurteilt werden. | Technische Verifikation im Programm oder erneute Entwicklerselbstpruefung ersetzt diese Abnahme nicht. |
| Spaetere Laufentscheidung | Explizite Quellen-/Einmallauffreigabe fuer genaue Lauf-ID, Ausgabe, Code-/Quellen-/Qualifikationsbelege und verbindlich gewaehlte Begrenzung; erst danach finale Bindung/Eintritt. | 640 MiB Commit und 96 MiB WS bleiben derzeit experimentelle Testparameter, keine bereits genehmigte reale Laufkonfiguration oder V8-Artefaktgrenze. |

Die Nullrecordgroesse ist keine Obergrenze fuer Nichtnullwerte. Laengere `values_hex`, mehrere unterschiedliche Vektoren und numerische Flaglisten sind in gezielten neutralen Codec-/Receiptgegenproben zu beruecksichtigen. Die vorhandene exakte Serialisierung/Grenzpruefung verweigert einen zu grossen Kandidaten bereits sicher; eine pauschale neue Metadatenbegrenzungslogik ist dafuer nicht erforderlich. Ob der fachliche Vergleich erfolgreich publizierbar sein wird, ist mit den Nullbelegen allein noch nicht gezeigt. Keine Recordreserve oder wissenschaftliche Regel anpassen, um ihn passend zu machen.

Die spaetere Quellenzulassung kann vor jedem Payloadaufruf rein dateibasiert gegen den versiegelten Plan geprueft werden. Die tatsaechliche Uebereinstimmung erzeugter Bytes mit den vorhandenen Hashes erfolgt erst bei der separat freigegebenen Materialisierung. Eine neue reale Vorproduktion als versteckte Qualifikation wird nicht vorgeschlagen. Nichtnull-Tests verwenden ausschliesslich gesonderte neutrale Fixtures am gemeinsamen Kern und duerfen den realen Eintritt nicht freischalten.

## Zusaetzlicher Produktions- und Testcode

Planansatz fuer neue Dateien beziehungsweise Nettoerweiterungen; kein Code wurde erstellt. Vorgesehene Rollen sind etwa `tools/_s2uc_source_execution_binding.py`, `tools/_s2uc_source_execution.py`, `tools/s2uc_source_process_once.py` sowie `tests/test_s2uc_source_execution.py` und `tests/test_s2uc_source_process_guard.py`. Diese Namen sind Zuordnungen fuer einen moeglichen Folgeauftrag, keine angelegten Artefakte.

| Arbeitsteil | Produktion zusaetzlich Byte | Tests zusaetzlich Byte | Gezielte Pflichtgegenproben |
|---|---:|---:|---|
| Quellen-/Ausfuehrungsbinder | 3000–5000 | 2500–4000 | Fuenfermenge, Reihenfolge, Payload-/Rezept-/Profil-/Zeitmanipulation; Null-/Real-/Legacy-Mischung; fehlende/stale Zulassung. |
| Gemeinsamer Lebenszyklus und Publikationskontext | 1200–2200 | 1800–3000 | Identische Armwerte und 58 Aufrufe; 57/58-Praefix; Owner-/Codec-/Publikationsfehler; alte Neutralhuelle bleibt gesperrt. |
| Gebundener NU-Supplieranschluss | 400–800 | 1200–2000 | Nur Stream 2 / Fenster 0..4; kein Aufruf vor Zulassung, kein Cache, bytearray ohne zweite Pflichtkopie; Hashabweichung bricht ab. |
| Begrenzter Prozesseinstieg und Eintrittsnachweis | 1500–2800 | 1800–3000 | Grenze und Mitgliedschaft vor Importen, falscher/fehlender Eintrittsnachweis, kein Supplier bei Ablehnung, externer Abbruch ist kein Produktabschluss. |
| Qualifikationsbelegleser und vollstaendiges Inventar | 1600–2800 | 1800–3000 | Test-ID-Vollstaendigkeit, Werkzeug-/Runtimehash, gefaelschte erfolgreiche Fixturebelege, fehlendes Parent/Child im Inventar. |
| Nichtnull-Recordform und Grenzgegenproben | 0–300 | 1500–2500 | Laengere Werte, mehrere Vektoren, Flaglisten; Reservekante/Plus-eins und Fehlerabschluss ohne auswertbaren Record. |
| **Summe** | **7700–13900** | **10600–17500** | **18300–31400 Byte netto** |

Begruendung der Groessenordnung durch gelesene Quellstellen: vorhandener V8-Validator 3379 Byte, Fixture-Belegerzeugung 924 Byte, Eintritt/Lebenszyklus 3317 Byte, Supplier 358 Byte; Begrenzungsrahmen `child` 2646 und `observe` 2456 Byte. Vergleichbare vorhandene Tests: strikte Bindungsabwehr 1183 Byte, vollstaendiger 58er-Erfolg 1764 Byte, Receipt-/Projektionsmanipulationen 3032 Byte; Fixtureaufbau/seal zusammen 1648 Byte. Die zugehoerigen Zeilen und exakten Quellbytebereiche stehen in `static-evidence.json`. Diese Funktionen werden nicht pauschal kopiert oder doppelt als neu gerechnet.

**Unsicherheit:** Die Zusatzwerte sind technische Schaetzintervalle, keine gemessene Implementierung und keine bewiesene minimale/obere Schranke. Die vorherige V8-Grobschaetzung war zu niedrig; deshalb wird hier nicht mit wenigen geaenderten Statusstrings oder kostenloser Qualifikation gerechnet. Alle 138 bisherigen Pruefpflichten bleiben erhalten. Gemeinsamer Kern, Receiptverifier und Publikationskern erhalten keinen zweiten Implementierungsansatz.

Vollstaendige prospektive Rechnung ohne unbelegte Streichgutschrift:

| Bestandteil | Byte |
|---|---:|
| Bestehender V8-Produkt-/Testbestand, 44 Dateien | 699053 |
| Vollstaendiges vorhandenes Messwerkzeug `v8-process-memory-20260920/measure.py` | 10811 |
| Vollstaendiger korrigierter Begrenzungsrahmen `v8-process-limit-corrected-20260920/limit.py` | 10978 |
| **Aktuelle vollstaendige Basis, 46 Dateien** | **720842** |
| Zusatzerfordernis Produktion und Tests inkl. Prozessanschluss | 18300–31400 |
| **Geplanter Gesamtumfang** | **739142–752242** |
| Unveraenderte Codegrenze | 720896 |
| **Geschaetzte Ueberschreitung** | **18246–31346** |

Der ganze Begrenzungs- und Messbestand ist enthalten, auch seine im spaeteren Aufruf nicht benoetigten Funktionsdefinitionen. Keine Einsparung durch Herausrechnen von Funktionen oder Entfernen alter Tests angenommen. Ein moeglicher kuenftiger Austausch durch einen kleineren, vollstaendig qualifizierten Rahmen waere eine ausdrueckliche Architekturentscheidung mit neuer exakter Inventarpruefung; er ist keine bereits gemessene Einsparung dieses Plans. Die erste Begrenzungsrevision mit dem Allokationsnachweis bleibt separat historisch, nicht als identische korrigierte Ausfuehrungsfassung behauptet.

Der NU-Generator und seine Projektabhaengigkeiten sind bereits in der Basis enthalten: `_s2nu_private_source_binding.py` 13635 Byte, `_s2np_private_source_binding.py` 15138 Byte, `_s2ts_temporal_trace_run.py` 10468 Byte sowie der vorhandene Laufbinder 35066 Byte. Sie werden nicht nochmals als neue Produktionsbytes aufgeschlagen. Externe installierte Laufzeiten bleiben wie im bestehenden Vertrag getrennt identifiziert.

## Begrenzte Anschlussfolge und Empfehlung

1. Projektleiter trifft zuerst eine konkrete Architekturentscheidung zum Platzkonflikt: welcher qualifizierbare Bestand stellt den Anschluss unter der unveraenderten Grenze dar? Der vorliegende Aufbau besitzt nur 54 Byte Reserve. Ein Konsolidierungsauftrag muesste die komplette Einsparung nachweisen und alle bisherigen Pruefpflichten erhalten; dieser Plan erteilt ihn nicht.
2. Erst nach tragfaehiger Byteplanung: eng begrenztes Anschlussmodul mit unveraenderten fuenf Quellen und gemeinsamem V8-Kern implementieren; geschlossene Zulaessigkeitsgrenzen und gezielte neutrale Gegenproben belegen.
3. Den konkreten Endstand qualifizieren und unabhaengig abnehmen lassen. Existierende Belege gezielt weiterverwenden; geaenderte Uebergaenge pruefen, keine pauschale Wiederholung aller Messungen.
4. Erst danach gesonderte reale Einmallaufentscheidung und finale Quellen-/Laufbindung. Kein Beginn der Quellenproduktion in den vorangehenden statischen oder neutralen Schritten.

**Empfehlung:** Nicht unmittelbar den Nullsupplier austauschen. Zuerst den konkreten Platzkonflikt dieses Anschlussplans entscheiden; die unabhängige Abnahme bleibt daneben eine offene eigene Voraussetzung. Damit ist die naechste Entscheidung auf Dateien, unveraenderte wissenschaftliche Erwartungen und bezifferten Zusatzbedarf begrenzt.
