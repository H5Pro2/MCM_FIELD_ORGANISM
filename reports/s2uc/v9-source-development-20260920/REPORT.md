# S2-UC V9: Quellenanschluss, neutraler Entwicklerabschluss

**161/161 Tests bestanden, Exitcode 0: 138 bisherige und 23 neue Tests.** Keine Fehler, Fehlschlaege oder Skips. Der vollstaendige Testdurchgang dauerte 827,457 Sekunden. Code-/Werkzeuginventar vor und nach dem Durchgang identisch. Der reale Eintritt bleibt bedingungslos gesperrt; keine NU-Payloadproduktion, kein Hauptlauf und keine finale reale Laufbindung. Unabhaengige Abnahme bleibt offen.

## Umsetzung

- Eigener V9-Ressourcenvertrag mit **851968 Codebyte**. Alle sonstigen Kategorien, Grenzen und Record-/Verifikationsreserven sind unveraendert.
- Strikter statischer Quellenkontext: genau die fuenf versiegelten NU-Quellen in vorhandener Reihenfolge, alle 58 Endpunktverwendungen, vollstaendige Planreihen mit Rezept-/Quellinformationen, Roh-/Halbprofil, Zeitfelder, Zielherkuenfte und bestehende Prueferwartungen. Manipulierte, fehlende, umsortierte und gemischte Inhalte werden abgewiesen.
- Separater neutraler V9-Ausfuehrungsbinder mit eigener Version, Einmalidentitaet, kanonischer Ausgabe, exakten Artefaktrollen und vollstaendigem aktuellem Inventar. Positive Tests verwenden ausschliesslich fuenf synthetische `neutral-v9-*`-Nichtnull-Fixtures. Null-/Real-/Legacy-Mischungen und fehlende Autorisierung bleiben gesperrt.
- Ein gemeinsamer Lebenszyklus und Publikationsalgorithmus: Der bisherige V8-Kern stellt privat `_run` bereit; V8 und V9 geben getrennte Validatoren und Publikationskontexte hinein. Derselbe Adapter materialisiert jeden der 58 Endpunkte einmal; beide Arme erhalten dasselbe Wertetupel. Kein zweiter Materialisierungs- oder Publikationsalgorithmus.
- Der vorbereitete NU-Bedarfssupplier prueft den Kontext vor seiner Erstellung, akzeptiert nur Stream 2 / Fenster 0 bis 4 und erzeugt weder vorab Payloads noch einen Cache. Sein Generatoranschluss wurde ausschliesslich mit einem Mock geprueft: zehn Abrufe ergeben zehn Generatoraufrufe; ein bytearray wird identisch weitergereicht. **Kein echter NU-Generatoraufruf im Paket.**
- Begrenzter neutraler Parent-/Child-Einstieg mit `-S`: Das Kind wartet vor Produktimporten auf den Parent, prueft selbst Windows-Jobmitgliedschaft und Prozesslimit, prueft die Codehashes und kontrolliert erneut die Abwesenheit von Produktmodulen/NumPy. Erst danach folgen `site.main()` und Produktimporte. Die Jobgrenze bleibt bis zum Kindprozessende aktiv.
- Belegleser fuer tatsaechlich ausgefuehrte neutrale Entwicklungsevidenz: vollstaendige feste Test-ID-Menge, exaktes PASS-Protokoll, aktuelle Code-/Werkzeug-/Runtimehashes und urspruengliche Einzeldateigrenzen. Fixturebelege bleiben `FIXTURE_ONLY` / `SYNTHETIC_FIXTURE_NOT_EXECUTED`. Konsistenzpruefung ist keine unabhaengige Zertifizierung und erzeugt niemals Realautoritaet.

Dateien, Groessen und vollstaendige SHA256: [FILES.md](FILES.md), [Vorher-/Nachhervergleich](changed-files.json). Alle 55 gebundenen Dateien einschliesslich der vollstaendigen alten Mess- und Begrenzungswerkzeuge stehen im [Endinventar](final-02/dependency-inventory.json). Quellstellen fuer die Abnahme: [review-anchors.json](review-anchors.json).

## Versionen und Standabgleich

Die oberste Standseinordnung im Forschungsweg beschreibt noch den abgeschlossenen V6-Modultrennungszweig. Grundlage dieses Pakets ist der neuere direkte V9-Auftrag samt freigegebener Codegrenze. Die Abweichung und ihre Behandlung stehen in [IMPLEMENTATION.md](IMPLEMENTATION.md); sie wurde nicht als Realfreigabe interpretiert.

**V8-Vertrag und V8-Binder sind bytegleich geblieben.** Die einzige geaenderte vorbestehende Pythondatei ist `tools/_s2uc_execution_v8.py`: +235 Byte fuer den gemeinsamen privaten Kern und die unveraenderte neutrale V8-Fassade. Ihr Hash ist deshalb neu. Alte Inventare, Bindungen und Ergebnisse wurden nicht umgebunden oder nachtraeglich aktualisiert. Alle sieben bisherigen Testdateien und 1852 historische S2-UC-Berichtsdateien sind bytegleich; keine vorbestehende Datei fehlt. [Erhaltungspruefung](final-audit.json).

Der aktuelle V7-Bestand bleibt bei 654949 / 655360 Byte; die aktuelle V8-Produkt-/Testvereinigung liegt bei 699288 / 720896 Byte. Die V9-Vereinigung zaehlt zusaetzlich den gesamten Parent-/Child-/Mess-/Pruefwerkzeugbestand. Historische Belege bleiben Nachweise ihrer damaligen Hashstaende.

## Tests und Befunde

Jede ausgefuehrte ID mit PASS: [TESTS.md](TESTS.md). Maschinenlesbares Ergebnis: [test-result.json](final-02/test-result.json); Originalprotokoll: [unittest.log](final-02/unittest.log). Pflichtzuordnung: [COVERAGE.md](COVERAGE.md).

Die neuen Tests belegen insbesondere Nichtnull-Receipts mit fuenf unterschiedlichen Vektoren, gleiche Armwerte bei allen 58 Materialisierungen, 57 Erfolge bei Fehler im 58. Versuch, ausstehenden Receipt zwischen Armaufrufen, Owner-/Konstruktor-/Codecfehler, Primaerfehlererhalt, Gate-Ruecksetzung, Einmaligkeit, Minimalterminal und verbliebene Stagingbytes. Lange Hexwerte und numerische Flaglisten durchlaufen den verlustfreien Codec; die exakte Recordreserve wird angenommen und Plus-eins abgewiesen. Der alte neutrale Publisher nimmt materialisierte V9-Records weiterhin nicht an.

Im finalen Prozessnachweis sind drei Faelle getrennt archiviert:

| Fall | Ergebnis | Quellenzaehler |
|---|---|---|
| [Falsche Jobzuordnung](final-02/process-1/process-exit.json) | Externer Kindabbruch vor Produktimport; kein Produktabschluss | keine Produktausfuehrung |
| [Injizierter MemoryError](final-02/process-2/process-exit.json) | NOT_EVALUABLE, urspruenglicher MemoryError | 58 Versuche / 57 Erfolge |
| [Neutraler Nichtnull-Erfolg](final-02/process-3/process-exit.json) | CLOSED_NEUTRAL_VERIFIED | 58 / 58 |

Fuer beide Produktausfuehrungen ist `parent-admission < child-admission < after-imports` geprueft. Child: Jobmitgliedschaft wahr, Flags `0x2100`, Commitlimit **671088640 Byte (640 MiB)**, Produkt/NumPy vor Freigabe abwesend. Beide Gates danach falsch; keine reale Quellenproduktion. Das Limit ist weiterhin ein neutraler Testparameter; es wurde keine reale Laufkonfiguration freigegeben. Keine Wiederholung des historischen Allokationsversuchs und keine neue Behauptung eines gemessenen V9-RAM-Peaks. Ein fehlender Abschluss nach echtem OOM/Prozessabbruch bliebe nicht auswertbar.

## Vollstaendige Bytebilanz

| Codebestand | Byte |
|---|---:|
| Historische vollstaendige Ausgangsbasis | 720842 |
| Aenderung am gemeinsamen Kern | 235 |
| Neun neue Pythondateien einschliesslich Tests und Pruefwerkzeug | 54110 |
| **Aktuelle Vereinigung, 55 Dateien** | **775187** |
| Freigegebene Codegrenze | 851968 |
| **Verbleibend** | **76781** |

Der Nettozusatz 54345 Byte liegt 22945 Byte ueber der urspruenglichen oberen Schaetzung von 31400 Byte. Diese Differenz verbraucht einen Teil der ausdruecklich freigegebenen Entwicklungsreserve von 99726 Byte. Keine Einsparung durch Weglassen alter Tests oder nur anteiliges Zaehlen von Werkzeugen. [Codebilanz](code-budget.json).

Jeder V9-Produktabschluss enthaelt zusaetzlich zu Code 26992 Byte Metadaten und 102659 Byte `static_shared`. Die folgende Tabelle nennt tatsaechlich vorhandene Ausgabebytes; Gesamt umfasst auch Code und Eingaben. Es handelt sich um getrennte Gegenproben, nicht um gleichzeitig angesammelte Laufartefakte.

| Abschluss / Primaerfehler | Record | Verifikation | Fehler | Terminal | Minimal | Staging | Gesamt |
|---|---:|---:|---:|---:|---:|---:|---:|
| V9_CODEC_FAIL | 0 | 0 | 1140 | 1140 | 0 | 0 | 907118 |
| V9_CONSTRUCTOR_FAILURE | 0 | 0 | 883 | 883 | 0 | 0 | 906604 |
| MemoryError | 189440 | 385 | 1653 | 1653 | 0 | 0 | 1097969 |
| Neutraler Erfolg | 193150 | 2466 | 0 | 1644 | 0 | 0 | 1102098 |
| NEUTRAL_INVALID_RECORD | 245760 | 0 | 682 | 682 | 0 | 0 | 1151962 |
| SECOND_ARM_FAILURE | 6525 | 382 | 1336 | 1336 | 0 | 0 | 914417 |
| PCM_HASH_INVALID | 2475 | 382 | 1336 | 1336 | 0 | 0 | 910367 |
| ValueError | 2469 | 382 | 1330 | 1330 | 1390 | 0 | 911739 |
| PCM_HASH_INVALID | 0 | 0 | 0 | 0 | 0 | 73 | 904911 |

Der erfolgreiche Nichtnull-Record von 193150 Byte liegt unter der unveraenderten Reserve 245760 Byte. Dies ist keine obere Schranke fuer alle moeglichen realen Payloads. Die technische Groessenabwehr bleibt aktiv; die Wissenschaft wurde nicht passend gemacht.

Alle **51 direkt erfassten Abschluesse** und die **zwei Produktabschluesse der begrenzten Prozesse** sind mit Kategorien, Restdateien und Reserven in [closure-byte-audit.json](closure-byte-audit.json) enthalten. Ein absichtlich unregistriertes V7-Ausgabeartefakt macht die Bilanz erwartungsgemaess unvollstaendig und den Fall NOT_EVALUABLE; seine Zusatzbytes stehen als `unclassified_bytes` und im beobachteten Gesamttotal.

Externe Prozessbelege werden getrennt ausgewiesen: 1500 Byte beim externen Abbruch, 55736 Byte beim MemoryError, 64332 Byte beim Erfolg. Eine konservative Zusatzrechnung zaehlt die Prozesskonfiguration als Metadaten und alle weiteren Supervisor-Dateien als `static_shared`; Gesamt einschliesslich Produkt: **1153705 Byte** bzw. **1166430 Byte**, weiterhin innerhalb saemtlicher unveraenderter Grenzen. Das veraendert weder Produktbelege noch ihre Auswertbarkeit. Archivkopien und der ausfuehrliche Entwicklerbericht sind getrennte Entwicklungsdokumentation mehrerer Faelle.

Der statische Quellen-Vorbereitungsleser prueft und bilanziert separat:

| Eingabe | Byte | Einzelgrenze |
|---|---:|---:|
| Quellenkontext | 50818 | 65536 |
| Qualifikationszusammenfassung | 605 | 16384 |
| Vollstaendiges Testprotokoll | 20707 | 32768 |
| Aktuelles Inventar | 11829 | 16384 |
| Unveraenderter NU-Plan | 44937 | 65536 |

Mit Code ergibt dies **904083 Byte**, Metadaten 50818 und `static_shared` 78078; alle Grenzen eingehalten. [Vorbereitungspruefung](final-02/source-preparation-check.json). Dies ist keine finale Quellen-/Einmallaufbindung. Der ausfuehrliche Entwicklerbericht `test-result.json` wird ausdruecklich nicht anstelle der begrenzten Qualifikationszusammenfassung eingelesen.

## Realsperre und Aussagegrenzen

`start_real` verwirft unpassende Quellenkontexte und endet **auch nach erfolgreicher Strukturpruefung unbedingt mit V9_REAL_EXECUTION_DISABLED**, bevor ein Supplier vorbereitet oder ein Produktlauf begonnen wird. Der oeffentliche CLI-Einstieg besitzt keinen Realmodus; der bisherige Starter bleibt ebenfalls gesperrt. Fehlende/stale Zulassungen sowie scheinbar erfolgreiche synthetische Belege koennen diese Schranke nicht oeffnen.

`candidate_gains` und `candidate_losses` bleiben unveraendert leer und sind in V9 als **NOT_MEASURED** gekennzeichnet: keine Messung von null Gewinnen oder Verlusten. Keine neue Schwelle, Quelle, Armregel, Gain-/Loss-Regel oder wissenschaftliche Bewertungsregel. Nichtnull-Entwicklungstests ersetzen keinen realen Quellenvergleich und keinen Nachweis von Erinnerungsnutzen.

Die Qualifikationslesung meldet NEUTRAL_EVIDENCE_CONSISTENT und weiterhin `real_execution_authorized=false`, `independent_acceptance=OPEN`. [Endpruefung](final-02/final-checks.json). Eigenpruefung wird nicht als unabhaengige Abnahme bezeichnet.

## Integritaet und naechster Schritt

1059 archivierte Dateien und 3113 Referenzvorkommen wurden nachgeprueft; keine Hash-/Byteabweichung. Alle 55 aktuellen Code-Dateien stimmen mit dem Testinventar ueberein. [Abschlussaudit](final-audit.json), [Archivhashes](final-02/evidence-hashes.json).

Vorlaeufige Fehler und Korrekturen bleiben nachvollziehbar: [development-corrections.json](development-corrections.json). Der unterbrochene Ordner `final` ist kein Abschlussnachweis; massgeblich ist ausschliesslich `final-02`.

**Empfohlener naechster Schritt:** unabhaengige Abnahme dieser konkreten Hashfassung, besonders Quellenbindung, gemeinsamer Kern, Eintritt vor Importen, Belegleser und vollstaendige Bilanz. Erst nach dieser getrennten Abnahme waere eine gesonderte Entscheidung ueber reale Begrenzung, genaue Einmallaufidentitaet und finale Bindung sachgerecht. Der Entwickler startet daraus keinen weiteren Lauf.
