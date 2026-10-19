# PerceptionSample-Blattfall V1 – neutrale Qualifikation (2026-10-03)

Ergebnis: S01–S10 bestanden;alle acht vollständigen Fach- und Metervergleiche gleich. Separater Beobachterstand ergänzt ausschließlich den geprüften Sample-Blattfall. Alle acht JSON-Zeitpaare schneller. Keine Rasterausführung und keine Änderung der bestehenden operativen Hülle.

## Implementierung und Bindung

Neue Dateien: tools/_s2uc_sample_leaf_observer_v1.py,tests/test_s2uc_sample_leaf_observer.py,tools/s2uc_sample_leaf_qualify.py. Plan und Code wurden vor Matrixbeginn gebunden. Alter Frame-Beobachter und historische Bindungen/Exporte unverändert. Keine Wertededuplizierung,kein Cache,keine Stackverkürzung und keine Änderungen an Quelle,Policy oder Traceereignissen.
Der kurze Pfad verlangt exakt PerceptionSample,exakt tuple mit48 echten floats,exakt str für profile/owner/stream und exakt int für index/start_sample/end_sample. seen wird unverändert zuerst gesetzt. Unterklassen,mutable Payloads und ungeklärte Felder bleiben vollständig traversiert. Ein bool-Index wird nicht als exakter int akzeptiert. Es wird strukturelle Skalarität geprüft,keine neue fachliche Eingabevalidierung eingeführt.
Bindung SHA256: 7ad1818a644f381bbcfc503ccd61e324bc8c4389bee1c390c07515a3d3260ead. S01 prüft per AST,dass nur der Sample-Blattfall hinzukommt. Der bereits qualifizierte Frame-Blattfall bleibt erhalten.

## Tests und Ressourcenerkennung

S01–S10:10/10 bestanden,keine Fehler/Skips. Vollständige Test-IDs in tests.json. S02/S03 vergleichen erreichbare Frame-ID-Mengen,Aliase/Zyklen,18/19-Grenze,Outputslots und20er-Kombination;S04 bestehende Frame-Fallbacks;S05 sechs echte Hypothesen einer neutralen Vorbelegung;S06 Promotion/Verdrängung und vier Unterbrechungspunkte samt Cleanup und transienten Maxima;S07 unveränderte Frame-,Fremdvektor- und Metadatenfehler.
S09 prüft acht Sample-Fallbacks mit verborgenen Frames:eine Unterklasse und jedes der sieben Felder. Hinzu kommen eine nachträglich veränderte Liste und bool-Index. S10 prüft sieben Sample-Aliase,einen Zyklus und verborgene18/19-Frame-Grenzen. Alle Frame-ID-Mengen,Ressourcen und Fehler entsprechen dem bisherigen Visitor.
S08:isolierter Observerpeak OLD 7176 Byte/NEW 5592 Byte bei18 Frames plus Sample mit48 getrennten Floats. Kein persistenter Cache;dies ist keine Gesamtprozess-RAM-Messung. Unit-Qualifikation lief vor dem Start eines frischen Matrixprozesses,keine Benchmark-Warmups.

## JSON-Zeitmatrix

Genau16 Replays mit je80 Positionen:1280 Aufnahmen und1280 Referenzfortschreibungen. N1 M/E/K/P jeweils OLD/NEW,N2 M/E/K/P jeweils NEW/OLD. Jeder Replay erhält frisch gelesene gespeicherte JSON-Werte mit48 verschiedenen Float-Identitäten je Vektor. Vorbereitung/Digest und Export außerhalb des Replaytimers. Direkter Aufruf der unveränderten baseline.replay-Funktion;Visitor vorab zugewiesen und anschließend wiederhergestellt. Keine Diagnose-Besuchszähler,kein Mock und kein zusätzlicher Testwrapper im gemessenen Aufruf.

| Quelle/Arm | OLD Wall s | NEW Wall s | OLD CPU s | NEW CPU s | Entlastung | Heap OLD/NEW Byte |
|---|---:|---:|---:|---:|---:|---|
| N1/M | 13.301407 | 10.388890 | 13.281250 | 10.390625 | 21.90% | 4548/2724 |
| N1/E | 13.316360 | 10.463847 | 13.312500 | 10.437500 | 21.42% | 2481/2481 |
| N1/K | 13.012054 | 9.775789 | 12.953125 | 9.781250 | 24.87% | 1498/1498 |
| N1/P | 12.849308 | 9.709620 | 12.859375 | 9.703125 | 24.43% | 1498/1498 |
| N2/M | 18.537466 | 14.732823 | 18.515625 | 14.703125 | 20.52% | 2860/2892 |
| N2/E | 18.171074 | 14.506187 | 18.125000 | 14.515625 | 20.17% | 2481/2481 |
| N2/K | 17.628381 | 13.981143 | 17.625000 | 13.984375 | 20.69% | 1498/1498 |
| N2/P | 17.289312 | 13.894418 | 17.265625 | 13.890625 | 19.64% | 1498/1498 |

Summe OLD 124.1053624 s/NEW 97.4527171 s: 21.48% weniger Replayzeit. Gesamte Matrix bis Ende der Abschlussverwaltung 222.848014 s unter900 s. Quellen-/Exportzeiten pro Replay in measurements.json;kein fsync- oder physischer Datenträgerdurchsatzbeleg.
Alle acht Fachbelege nach Abtrennung ausschließlich resources kanonisch gleich;resources danach vollständig gesondert verglichen. Sämtliche Meterfelder stimmen exakt überein. Alle16 Replays mit vollständiger terminaler,EMA- und Ausgabefreigabe sowie Endziel81. Keine nachträgliche Feldfilterung.
Vollständige resources-Objekte unterscheiden sich in zwei Paaren ausschließlich im additional_python_peak: N1/M4548→2724 Byte,N2/M2860→2892 Byte. Die32 Byte Erhöhung bleibt ausdrücklich dokumentiert. In den übrigen sechs Paaren sind auch vollständige Ressourcenobjekte gleich. Diese isolierten Allokationspeaks sind nicht gleichgesetzt oder bereinigt;Allocator-/Erstaufrufeffekte sind mögliche,nicht gesondert gemessene Ursachen.
Maximaler Zusatzheappeak 4548/16384 Byte. Metermaxima: `{"combined_peak": 13, "frame_peak": 12, "match_metadata_peak": 2, "output_python_bytes_peak": 3645, "output_slots_peak": 2, "receipt_bytes_peak": 454, "receipt_python_bytes_peak": 495, "receipt_transient_utf8_bytes_peak": 908, "samples": 76050, "scalar_pair_comparisons": 0, "temporary_numeric_vectors_peak": 0, "transient_reference_frames_peak": 12}`. Gepackter EMA-Bound416 Byte bleibt eine Obergrenze und bedeutet nicht in jedem Arm tatsächlichen Besitz. Ressourcen- und Fehlererkennung unverändert in den geprüften Fällen.

## Aktualisierte Zeitplanung – ausdrücklich Hochrechnung

Keine weitere Hüllenintegration oder Rastermessung in diesem Auftrag. Für eine spätere Übernahme des neuen Visitors werden folgende Szenarien ausgewiesen. Unverändert bleiben25 Prozent Zuschlag plus180 s Verwaltung/Materialisierung/Belegprüfung/Export,30 s U und60 s Abschluss. Die3600-Sekunden-Grenze wird nicht erhöht.

| Szenario | Hochrechnung s | Reserve zu3600 s |
|---|---:|---:|
| Bisheriger konservativer Plan | 6330.088 | -2730.088 |
| Aktualisierter konservativer Transfer | 5140.141 | -1540.141 |
| Bisheriges48/80-Kontextklassenmodell | 4760.362 | -1160.362 |
| Aktualisierter Klassentransfer | 3878.644 | -278.644 |
| Neue neutrale Kontextmaxima,80er-Preis auch für48er | 2541.872 | 1058.128 |

Die Transfermodelle verwenden durchgängig die schwächste gemessene NEW/OLD-Quote 0.803642057,nicht die günstigste oder den Mittelwert. Formel:(bisherige Baselineplanung)×Quote+270 s. Damit wird ausdrücklich auch ein Anteil skaliert,der nicht sicher durch den Sample-Blattfall beeinflusst wird;der Transfer auf den vollständigen Hüllenstack ist unbewiesen.
Das neutrale Modell verwendet die jeweils langsamste NEW-Zeit von N1 beziehungsweise N2 und16 stabile/112 konkurrierende Baseline-Arme,berechnet auch48er-Arme mit vollem80er-Preis. Es deckt nicht alle Rasterkontexte und Hostschwankungen ab und ist keine obere Schranke. Sein positiver rechnerischer Rest ersetzt keinen Zeitnachweis. Die beiden historisch gestützten aktualisierten Szenarien bleiben über3600 s;ausreichende Reserve für den vollständigen Rasterlauf ist weiterhin nicht belegt.
Pro Paar liegt nur eine Messung vor. Reihenfolge wurde zwischen N1/N2 umgekehrt,aber es gibt keine statistische Streuungsschätzung und kein Hostlastprofil. Daher weder allgemeine Beschleunigungsgarantie noch Garantie einer vollständigen Rasterstunde. Die neue Zeitmatrix enthält keine Diagnosezähler;ihre Ergebnisse werden nicht mit den Zählerzeiten der2×2-Diagnose zu einem gemeinsamen Benchmark vermischt.

## Nächster begrenzter Schritt

Den qualifizierten Sample-Beobachter in einer separat beauftragten Version der bestehenden Hülle übernehmen und neu binden;dabei die unveränderten Ressourcen-/Autorisierungssperren erhalten. Eine Rasterausführung bleibt wegen fehlender belastbarer Zeitreserve unempfohlen und bedarf ohnehin separater Entscheidung. Keine weitere Optimierungsvariante aus diesem Abschluss ableiten.
Raster32 bleibt geschlossen und global NOT_EVALUABLE. Historische Dateien,Bindungen und Rasterautorisierungsvorlagen sind unverändert. Der Sample-Blattfall ist separat implementiert und neutral qualifiziert,noch nicht in den operativen Wiederholungseinstieg übernommen.
