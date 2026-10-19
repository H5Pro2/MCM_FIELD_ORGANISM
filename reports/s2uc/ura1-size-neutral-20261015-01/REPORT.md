# URA1: einmaliger neutraler 1024-Frame-Grenztest

Stand 2026-10-15. MCM-KI-Entwickler an MCM KI Projektleiter.

**TECHNICAL_ABORT – DICTIONARY_LIMIT. Der Größenlauf ist nicht bestanden.** Die beauftragte Vorbereitung und genau eine Ausführung sind erfolgt. Der exklusive Marker ist verbraucht; kein Retry, Resume oder Ersatzfall wurde gestartet. Es gibt keine Forschungsbereitschaft und keine wissenschaftliche Leistungsbewertung.

## Vorstartbindung und Material

Vorstart-SHA-256: `936327936082a351cbc7056e03f340ee0f1f4e0df269deebad3c57161dbf56fd`.

202 Dateien einschließlich der maßgeblichen Vorgängercodes, neuen Prüfhülle, Integritätsimplementierung, Vertrag und finalen Vorabbelegen sind gebunden. Materialrezept, Materialhash, Interpreterdatei, Python-DLLs, Version/Plattform, Grenzen und exakter Aufruf stehen in prestart.json. Vor Markerreservierung und im Worker wurden sie geprüft.

Material ausschließlich die vorhandenen 16 D_ITEMS-Blöcke exakt 16-mal: 256 Blöcke, 1024 Frames, geplant genau U und R nacheinander mit eigenen unabhängigen Referenzen. Keine Materialsuche, ergebnisabhängige Anpassung oder Forschungsquelle. Der Materialhash bezieht sich auf alle kanonischen Framewerte; das kleine Rezept bleibt unter der 32-KiB-Fallquellengrenze.

Material-SHA-256: `c36aaf13ba21830b628ffb98e97400bc4f79090f2415b401429100eb433e11f4`.

Exakter gebundener Aufruf (Argumentliste):

```text
C:\Python314\python.exe
-m
tools.s2uc_ura1_size_once
run
C:\Users\TV\Documents\MCM_FIELD_ORGANISM\workspace\reports\s2uc\ura1-size-preparation-20261015-01\prestart.json
```

Der Supervisor reservierte START.json mit exklusivem create-new. Der Marker bindet den Vorstart-SHA und `consumed=true`; er wurde nicht überschrieben. Der Worker durfte erst nach bestätigter Zugehörigkeit zum selben Windows-Job arbeiten. Der bestehende 128-Frame-Kleinfallpfad blieb unverändert; der neue Einstieg akzeptiert ausschließlich die gebundene Geschichte.

## Neue Dateien

- [tools/_s2uc_ura1_capture_integrity.py](C:/Users/TV/Documents/MCM_FIELD_ORGANISM/workspace/tools/_s2uc_ura1_capture_integrity.py): Während der Erfassung gebildete unabhängige kanonische Anker, Strukturmanifest und zusätzlicher Envelopechecksum.
- [tools/_s2uc_ura1_integrity_decode.py](C:/Users/TV/Documents/MCM_FIELD_ORGANISM/workspace/tools/_s2uc_ura1_integrity_decode.py): Unabhängiger Decodervergleich gegen Erfassungsanker und übrige Recordstruktur.
- [tools/_s2uc_ura1_size_engine.py](C:/Users/TV/Documents/MCM_FIELD_ORGANISM/workspace/tools/_s2uc_ura1_size_engine.py): Separater fester Größeneinstieg mit unveränderten fachlichen Referenz-/Ereignisprüfungen und Fortschrittsmarken.
- [tools/s2uc_ura1_size_once.py](C:/Users/TV/Documents/MCM_FIELD_ORGANISM/workspace/tools/s2uc_ura1_size_once.py): Vorstartprüfung, exklusiver Marker, Supervisor/Worker, Fristen, Budgets, Abbruch- und Abschlussbehandlung.
- [tests/test_s2uc_ura1_size_once.py](C:/Users/TV/Documents/MCM_FIELD_ORGANISM/workspace/tests/test_s2uc_ura1_size_once.py): S01–S07, ausschließlich kleine Policyfälle bis acht Frames.
- [docs/S2UC_URA1_1024_GRENZTEST_VERTRAG_20261015.md](C:/Users/TV/Documents/MCM_FIELD_ORGANISM/workspace/docs/S2UC_URA1_1024_GRENZTEST_VERTRAG_20261015.md): Vor Start gebundener Vertrag für genau diese eine Ausführung.

## Vorbereitung und Test-IDs

Finale Vorbereitung: sieben Testmethoden bestanden, 5,682 s im Testworker. Zusätzliche Supervisorproben liefen im selben harten 512-MiB-Rahmen mit maximal einem Worker gleichzeitig. Der erste vorbereitende Durchgang bleibt erhalten; nach Ergänzung der Export-/Verwaltungsgrenzprüfung wurde die finale Vorbereitung erneut geprüft. Keine dieser Proben reservierte den eigentlichen Größenmarker.

| ID | Beleg | Ergebnis |
| --- | --- | --- |
| S01 | Exakte Material-, Code-, Runtime-, Grenzen- und Aufrufbindung; manipulierte Bindungen werden abgewiesen | PASS |
| S02 | Exklusiver Marker; erneute Reservierung abgewiesen, bestehender Inhalt unverändert | PASS |
| S03 | Vollständiger kleiner U/R-Fall mit Referenzen, acht Erfassungsankern und unabhängiger Decoderprüfung | PASS |
| S04 | Manipulierter Wert sowie fehlende/vertauschte Records trotz neu berechnetem Encoder-Envelopehash erkannt | PASS |
| S05 | Dictionaryabbruch im kleinen Fall; Framefortschritt, Teilanker und Cleanup belegt | PASS |
| S06 | Alte 128-Frame-Grenze bleibt aktiv; Größeneinstieg weist anderes Material zurück; Vorgängerclosures unverändert | PASS |
| S07 | Gesamtexport-, Vorbereitungs- und Verwaltungsgrenzen werden abgewiesen | PASS |
| P-START | Prozessstartfehler nach reserviertem separatem Testmarker; Marker bleibt verbraucht | PASS |
| P-WORKER-TIME | Workerfrist überschritten; Prozess beendet und Ende bestätigt | PASS |
| P-TOTAL-TIME | Gesamtfrist überschritten; Prozess beendet und Ende bestätigt | PASS |
| G01 | Der eine gebundene 1024-Frame-Grenztest | TECHNICAL_ABORT: DICTIONARY_LIMIT |

Die S01–S07-IDs tragen den Präfix `tests.test_s2uc_ura1_size_once.SizeTests.`; vollständige Namen und Ausgabe stehen im gebundenen tests.txt. Diese Vorbereitung ist kein Ersatz für eine vollständige Größenqualifikation.

## Erste verletzte Grenze und erreichter Stand

Abbruch während `capture_references_events_and_anchors` durch `ValueError:DICTIONARY_LIMIT`. Das Dictionary enthielt 4.194.282 serialisierte Byte; nur 22 Byte der unveränderten Grenze 4.194.304 waren frei. Der nächste neue Knoten hätte diese Grenze überschritten und wurde abgewiesen. Seine genaue Größe wurde nicht als separates Messfeld aufgezeichnet; aus der geprüften Guardbedingung folgt lediglich, dass er größer als der verbleibende Raum war.

U hatte Frame 844 begonnen; bis einschließlich Frame 843 waren die frameweisen Referenzprüfungen vollständig erfolgreich. Frame 844 ist ein partiell bearbeiteter Frame, kein vollständig geprüfter Zielpunkt. R wurde nicht gestartet. Daher sind weder zwei vollständige Armläufe noch die abschließende gepaarte Bestands-/Hypothesen-/Ticket-/Zellgleichheit erreicht. Es gibt keine Teilmengenwertung und keine Aussage über einen U/R-Leistungsabstand.

| Erfasste U-Folge | Erfolgreich aufgenommene Records | Kanonische Präfixbytes |
| --- | ---: | ---: |
| Äußere Vorher-/Nachherereignisse | 2529 | 27423038 |
| Interne Call-/Returnereignisse | 9278 | 119062112 |
| Prognosen einschließlich Hypothesen/Tickets | 421 | 555278 |
| Feedback einschließlich Fehlerzellenupdates | 421 | 33110 |

Insgesamt 12.649 Recordindizes. Der Store enthielt beim Abbruch 29.978 Knoten, 158.992 Referenzkanten und vier Collections. Ein begonnenes, nicht vollständig aufgenommenes Record kann bereits neue Teilknoten erzeugt haben; die Dictionaryzählung darf daher nicht als vollständiger Archivrecord interpretiert werden. Die Anker zählen nur erfolgreich aufgenommene Records. Größter aufgenommener beziehungsweise zur Aufnahme geprüfter Record: 15.178 Byte, unter 262.144 Byte. Knoten-, Kanten-, Index- und Collectiongrenzen wurden nicht zuerst erreicht.

## Unabhängiger Integritätsnachweis und seine Grenze

Vor jedem Zugriff auf den Referenzencoder wird der Originalrecord mit einer unabhängigen JSON-Normalisierung kanonisiert. Jede Folge erhält inkrementell SHA-256, Bytezahl und Anzahl. Der Digest wird erst nach erfolgreicher Recordaufnahme fortgeschrieben. Bei vollständig erfasstem Record würden diese acht Anker zusammen mit dem Hash der übrigen Struktur vor Archivkodierung gespeichert und durch den unabhängigen Decoder geprüft. Ein aus dem fertigen Encoderoutput abgeleiteter voller Hash ist nur eine zusätzliche Prüfsumme.

Im tatsächlichen Größenlauf existieren ausschließlich die vier U-Präfixanker in partial-capture-integrity.json. Sie wurden während der Erfassung gebildet, nicht nachträglich aus einem Archiv. Wegen des vorherigen Dictionaryabbruchs wurden kein vollständiges Strukturmanifest, kein gültiges Fallarchiv und kein vollständiger Decodervergleich dieses 1024-Frame-Falls erzeugt. Die unabhängige Rekonstruktion ist im kleinen Vorabtest S03 belegt; S04 zeigt die Erkennung neu gehashter Encoder-Manipulationen. Diese Vorabbelege werden ausdrücklich nicht als erfolgreicher Decodernachweis für den abgebrochenen Größenlauf ausgegeben.

## Ressourcen und Laufzeiten

Supervisor und höchstens ein Worker liefen im selben harten Windows-Job. Gemeinsame Commitgrenze 536.870.912 Byte; ActiveProcessLimit=2. Workerzugehörigkeit bestätigt, keine Breakaway-Ausnahme. Der Worker endete nach der behandelten technischen Abweichung mit Prozesscode 0; das bedeutet kontrollierte Fehlerbehandlung, nicht einen bestandenen Größenlauf.

| Messgröße | Beobachtet | Grenze / Einordnung |
| --- | ---: | --- |
| Gemeinsamer Kernel-Job-Peak | 121.827.328 Byte | 536.870.912 Byte |
| Höchster einzelner Prozess-Commit im Job | 91.901.952 Byte | im gemeinsamen Budget enthalten |
| Gemeinsamer gesampelter Peak | 117.563.392 Byte | Sampling, nicht Kernelmaximum |
| Supervisor-Grundbelegung | 24.997.888 Byte | nach Vorstartprüfung |
| Worker-Private-Bytes zu Beginn der Erfassungsphase | 28.004.352 Byte | Material/Imports bereits vorhanden |
| Python-Peak der Erfassung | 22.433.221 Byte | ergänzend, kein Prozessgesamtwert |
| Erfassung einschließlich Referenzen/Anker | 235,020 s | abgebrochene Phase |
| Cleanup | 0,120 s | bestätigt |
| Workerablauf | 235,144 s | 3540 s |
| Gesamtzeit Supervisor | 236,994 s | 3600 s |
| Temporäre Ereignis-/Archivdateien | 0 Byte | 67.108.864 Byte |
| Dictionary vor Abbruch | 4.194.282 Byte | nächster Eintrag hätte 4.194.304 überschritten |
| Finale Kodierung / gzip / Decoder | nicht erreicht | keine erfolgreichen Größenwerte |

Alle Referenzen, Beobachter, Anker und Codecverwaltungsobjekte zählen zum Prozessbudget. Die 20-ms-Prozesssamples können kurze Transienten verpassen; der gemeinsame Windows-Job-Peak stammt vom Kernel. Native Allokationen sind im Commit enthalten, nicht aber globaler Dateisystemcache oder externe Codex-Prozesse. Der Python-Tracer beginnt nach Erzeugung der festen Materialliste; deren Belegung ist im Prozessbudget enthalten, nicht vollständig im Tracer. Interpreterstart vor Installation des Jobs ist nicht separat zeitaufgelöst.

Cleanup bestätigt: U geschlossen, Bank null, Kandidat und Retained-Originale freigegeben; Storeknoten/-indizes freigegeben; keine Partialdatei und kein gültiges Fallarchiv verblieben; Workerende bestätigt. Die übrigen Interpreterobjekte werden spätestens mit dem bestätigten Prozessende freigegeben. R hatte keine anzuräumenden Armobjekte, da es nicht gestartet wurde.

## Aussage und begründeter nächster Schritt

Der technische Befund ist konkret: Das unveränderte 4-MiB-Dictionary reicht für diese vollständige Ereigniserfassung nicht einmal bis zum Abschluss des ersten Arms der periodischen 1024-Frame-Geschichte. Weder RAM, temporärer Plattenbedarf noch Fristen waren die zuerst erreichte Grenze. Die frühere lineare Größenabschätzung ist durch einen tatsächlichen Dictionaryabbruch ergänzt, nicht durch einen erfolgreichen Größenlauf ersetzt.

Empfehlung an den Projektleiter: ausschließlich einen neuen begrenzten Codecauftrag zur weiteren verlustfreien Kompaktierung der Zustands-/Metadatenänderungen prüfen, etwa explizite Zustandsdifferenzen mit unabhängigem Decoder und fortbestehenden Erfassungsankern. Zunächst an den vorhandenen kleinen Belegen abnehmen. Grenzen und Ereignisumfang bleiben unverändert; U/R- oder Lernregeln sollen dafür nicht geändert werden.

Die jetzt verbrauchte Einmalfreigabe darf dafür nicht wiederverwendet werden. Ein weiterer Größenlauf braucht eine neue ausdrückliche Beauftragung und neue Vorstartbindung. Kein automatischer Retry, keine Ersatzgeschichte, keine 32-Geschichten-Serie, keine Forschungsquellen oder Bootstrapmatrix. Eine technische Weiterentwicklung des Codecs wäre noch keine Forschungsbereitschaft.

## Belege

- [Vorstartbindung](C:/Users/TV/Documents/MCM_FIELD_ORGANISM/workspace/reports/s2uc/ura1-size-preparation-20261015-01/prestart.json)
- [Vorstart-SHA](C:/Users/TV/Documents/MCM_FIELD_ORGANISM/workspace/reports/s2uc/ura1-size-preparation-20261015-01/prestart.sha256)
- [Festes Materialrezept](C:/Users/TV/Documents/MCM_FIELD_ORGANISM/workspace/reports/s2uc/ura1-size-preparation-20261015-01/material-recipe.json)
- [Vorbereitungsbericht](C:/Users/TV/Documents/MCM_FIELD_ORGANISM/workspace/reports/s2uc/ura1-size-preparation-20261015-01/REPORT.md)
- [Finale Vorabtests](C:/Users/TV/Documents/MCM_FIELD_ORGANISM/workspace/reports/s2uc/ura1-size-preparation-20261015-01/qualification-final/tests/tests.txt)
- [Verbrauchter exklusiver Marker](C:/Users/TV/Documents/MCM_FIELD_ORGANISM/workspace/reports/s2uc/ura1-size-neutral-20261015-01/START.json)
- [Technischer Abschluss](C:/Users/TV/Documents/MCM_FIELD_ORGANISM/workspace/reports/s2uc/ura1-size-neutral-20261015-01/result.json)
- [Workerphasen, Fortschritt und Cleanup](C:/Users/TV/Documents/MCM_FIELD_ORGANISM/workspace/reports/s2uc/ura1-size-neutral-20261015-01/worker.json)
- [Windows-Job- und Prozessnachweis](C:/Users/TV/Documents/MCM_FIELD_ORGANISM/workspace/reports/s2uc/ura1-size-neutral-20261015-01/supervisor.json)
- [Unabhängige Präfixanker](C:/Users/TV/Documents/MCM_FIELD_ORGANISM/workspace/reports/s2uc/ura1-size-neutral-20261015-01/partial-capture-integrity.json)
