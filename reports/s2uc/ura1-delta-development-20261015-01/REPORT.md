# URA1: verlustfreie Zustandsdifferenzen, begrenzte Codec-Abnahme

Stand 2026-10-15. MCM-KI-Entwickler an MCM KI Projektleiter.

**PASS_SMALL_STATE_DELTA.** Genau eine gezielte Formatänderung wurde umgesetzt und an den vorhandenen vollständigen Kleinfallbelegen sowie ihren unveränderten 64-/48-Frame-Handfolgen geprüft. Beide kanonischen Originalrecords werden vollständig rekonstruiert. Dictionary und dekomprimiertes Format sind deutlich kleiner; der Laufzeitgewinn ist gering. Keine zusätzliche Codecvariante wurde angehängt.

Kein weiterer Größenlauf, keine Rekonstruktion fehlender Daten des abgebrochenen Laufs aus Hashankern, keine Forschungsquelle, Bootstrapmatrix oder Forschungsausführung. Die verbrauchte Größenfreigabe bleibt verbraucht; keine Forschungsbereitschaft.

## Analyse und genau eine abgeleitete Änderung

Die Analyse liest ausschließlich die vollständigen vorherigen Kleinfallarchive aus ura1-direct-development-20261015-01/normal-corrected. Dictionaryanteile werden anhand der tatsächlich serialisierten Knoten gezählt; Schlüsselbytes sind unten nur ein überlappender Teil davon und werden nicht nochmals zur Summe addiert.

| Größenanteil | D-Handfall (Byte) | Lebenszyklus (Byte) |
| --- | ---: | ---: |
| Vollständige Bankstrings | 98865 | 81120 |
| Zustandsobjekte | 131125 | 98515 |
| Ereignishüllen | 45496 | 34440 |
| Bestandsobjekte | 11574 | 9059 |
| Frameobjekte | 5638 | 4217 |
| Arrayknoten | 13580 | 11055 |
| Andere Objekte | 20431 | 16516 |
| Andere Skalare | 10419 | 9802 |
| Dictionary gesamt | 337128 | 264724 |

Bankstrings, Zustandsobjekte und Ereignishüllen bilden rund 82 % beziehungsweise 81 % dieser Dictionarybytes. Die darin bereits enthaltenen Objektschlüssel benötigen 112.765 / 85.935 Byte. Hohe Änderungsfrequenzen betreffen unter anderem Bank, Paar-/Hinweisintervalle, Bestandsmetadaten und Fortschrittszähler.

Im D-Handfall ändern sich über 582 Bankübergänge lediglich 2.508 Zeichen; vollständige Ersetzungen würden 484.224 Zeichen betreffen. Im Lebenszyklus sind es 2.064 geänderte gegenüber 367.744 vollständig ersetzten Zeichen bei 442 Übergängen. Diese Übergangszählung erfolgt über die äußeren und inneren Folgen beider Arme; sie ist keine zusätzliche Policybewertung.

Daraus folgt genau die Änderung **URA1_STATE_DELTA_V1**: je Folge ein vollständig definierter Anfangsrecord, danach eine geordnete Liste expliziter struktureller Änderungen. Pfade werden referenziert; Setzen, Entfernen von Objektschlüsseln und Ersetzen geänderter Zeichenbereiche sind die drei definierten Operationen dieses einen Formats. Es gibt keine implizite Historie außerhalb des Formats.

## Implementierung und Format

- [tools/_s2uc_ura1_delta_encode.py](C:/Users/TV/Documents/MCM_FIELD_ORGANISM/workspace/tools/_s2uc_ura1_delta_encode.py): Begrenzte fortlaufende Differenzbildung, Referenztabellen, unabhängige Erfassungsanker und Dateiausgabe.
- [tools/_s2uc_ura1_delta_decode.py](C:/Users/TV/Documents/MCM_FIELD_ORGANISM/workspace/tools/_s2uc_ura1_delta_decode.py): Separater Decoder ohne Encoder- oder Policyimport; eigenständige Referenz-/Pfadprüfung und Anwendung der Änderungen.
- [tools/_s2uc_ura1_delta_neutral.py](C:/Users/TV/Documents/MCM_FIELD_ORGANISM/workspace/tools/_s2uc_ura1_delta_neutral.py): Unveränderte fachliche Prüfhülle mit ausschließlich anderem Collectionimport und Docstring.
- [tools/s2uc_ura1_delta_qualify.py](C:/Users/TV/Documents/MCM_FIELD_ORGANISM/workspace/tools/s2uc_ura1_delta_qualify.py): Archivkonvertierung, gezielte Kleinfallintegration und Fehlerprüfungen mit Prozessmessung.
- [tests/test_s2uc_ura1_delta.py](C:/Users/TV/Documents/MCM_FIELD_ORGANISM/workspace/tests/test_s2uc_ura1_delta.py): T01–T06 einschließlich Negativkontrollen und unveränderter Bindungen.
- [docs/S2UC_URA1_ZUSTANDSDELTA_FORMAT_20261015.md](C:/Users/TV/Documents/MCM_FIELD_ORGANISM/workspace/docs/S2UC_URA1_ZUSTANDSDELTA_FORMAT_20261015.md): Vollständige Format-, Anfangszustands-, Reihenfolge-, Operationen- und Grenzbeschreibung.

Werteknoten verwenden das bewährte rückwärts referenzierende JSON-DAG-Prinzip. Die neue Darstellung speichert jedoch keine vollständige neue Ereignis-/Zustandshülle für jeden Schritt. Eine leere Änderungsliste bleibt ein eigener Record. Zahlenrepräsentation, negatives Null, Originalmetadaten, Tickets und Fehlerzellen werden nicht gerundet oder semantisch verändert. T01 prüft zusätzlich einen direkten vollständigen Bytevergleich mit negativen Nullwerten, Typen und Originalidentitäten.

Nach genau einer gzip-Dekompression liegt lesbares JSON vor. Keine innere Kompression und keine Base64-Nutzlast. Vollständige ursprüngliche Historien bleiben größer als das kodierte Format und werden unten ausdrücklich ausgewiesen.

## Verlustfreie Belege und Erfassungsanker

Bei der Archivkonvertierung wird aus dem bestehenden kompakten Quellgraphen jeweils nur der aktuelle Record gelesen. Es wird keine vollständige expandierte Historie geladen. Bei der Integration entstehen dieselben Records regulär aus den bestehenden Handfolgen. Vor Differenzbildung wird der Originalrecord mit der bereits gebundenen unabhängigen Normalisierung kanonisiert und gehasht. Acht geordnete Folgen erhalten Anzahl, Bytezahl und SHA-256; die übrige Recordstruktur wird separat gebunden.

Der Decoder rekonstruiert den Anfangszustand und jeden Folgerecord selbst. Er prüft alle Anker und die übrige Struktur und vergleicht zusätzlich vollständige Bytezahl und kanonischen SHA-256 gegen die vorhandenen extern gebundenen Kleinfallrecords. Die Encoder-Prüfsumme allein genügt nicht. Die vollständigen Erfassungsanker sind je Fall als *-capture.json archiviert.

| Fall | Frames je Arm | Äußere / interne Ereignisse je Arm | Rekonstruierte kanonische Bytezahl | Unveränderter kanonischer SHA-256 |
| --- | ---: | --- | ---: | --- |
| D_hand_case | 64 | 192 / 716 | 19728363 | `abc86c2b96fddd529aa1101f7d7364063ca515be174e7b9dae97a77b426a7d78` |
| lifecycle_trace | 48 | 144 / 552 | 13380342 | `940b29d1f24deac9e1dfcf575234089ff6c78d29415aefce7972598fe66996cd` |

Beide Arme, Prognosen und Feedbackfolgen sind enthalten. U/R-Auswahl, Lernen, Referenzen und Umfang der Ereignisprüfungen bleiben unverändert. T06 prüft den vollständigen Hüllenquelltext nach Rücknahme nur des Imports/Docstrings sowie alle 202 Dateien der früheren Größen-Vorstartbindung. Die alte 128-Frame-Hülle wurde nicht erweitert.

## Vorher/Nachher: Format und Verwaltung

Die Hauptvergleichswerte stammen aus der fortlaufenden Integration. Die Archivkonvertierung benötigt 79.523 / 65.050 Byte dekomprimiert und 13.920 / 11.978 Byte gzip. Unterschiede zur Integration entstehen durch die Reihenfolge der Erfassung und Vergabe von Referenznummern, nicht durch unterschiedliche rekonstruierte Daten oder eine zweite Formatvariante.

| Fall | Dictionary vorher | Dictionary nachher | Format vorher | Format nachher | gzip vorher | gzip nachher |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| D_hand_case | 337128 | 70451 | 339990 | 78258 | 23491 | 13941 |
| lifecycle_trace | 264724 | 58471 | 267066 | 64582 | 19210 | 12170 |

Das Dictionary sinkt um rund 79 % / 78 %, das dekomprimierte Format um rund 77 % / 76 %. Das ist eine belegte technische Größenreduktion. Die Verringerung ist nicht bloß gzip-Wirkung.

| Neuer Dictionaryanteil | D-Handfall | Lebenszyklus |
| --- | ---: | ---: |
| Werteknoten (Byte) | 29954 | 27557 |
| Pfadtabelle (Byte) | 2645 | 2198 |
| Änderungslisten (Byte) | 37852 | 28716 |
| Geordnete Folgenreferenzen (Byte, zusätzlich zum Dictionary) | 6047 | 4579 |
| Vollständige Bankstrings (Anzahl) | 1 | 1 |

| Verwaltung, beide Arme zusammen | D-Handfall | Lebenszyklus | Grenze je Fall |
| --- | ---: | ---: | ---: |
| Tabelleneinträge insgesamt | 1559 | 1332 | 65536 |
| Referenzkanten | 10111 | 7834 | 262144 |
| Recordindizes | 1942 | 1486 | 65536 |
| Collections | 8 | 8 | 16 |
| Vorherige Records: kanonischer Byte-Peak | 33865 | 33996 | 4194304 |
| Größter Record | 15142 | 15147 | 262144 |
| Maximal gleichzeitig temporäre Dateibytes | 13941 | 12170 | 67108864 |

Tabelleneinträge zählen Werte, Pfade und Änderungen gemeinsam. Kanten umfassen Wert-, Pfad-, Anfangszustands-, Delta- und Wurzelreferenzen. Dictionarywerte, Pfade und Änderungslisten teilen sich die unveränderte 4-MiB-Grenze; zusätzlich gilt 4 MiB für das vollständige dekomprimierte Format und 512 KiB für gzip.

Je Collection wird nur ein vorheriger Record gehalten, maximal 16 × 262.144 kanonische Byte insgesamt. Dessen tatsächlicher Python-Heap ist größer und vollständig im Jobbudget enthalten. Decoder und Iteratoren halten aktuelle Records und gegebenenfalls einzelne Kopien, keine ungezählte vollständige Historie. Die Verwaltungs- und Recordgrenzen wurden nicht erhöht.

Temporär entsteht ausschließlich die gzip-Partialdatei. Nach vollständigem Schreiben wird sie im selben Verzeichnis umbenannt, nicht kopiert. Ihre maximale gleichzeitig vorhandene logische Größe beträgt in der Integration 13.941 / 12.170 Byte. Dateisystemblockbelegung wurde nicht separat gemessen. Bestehende Eingabearchive werden gelesen, nicht als temporäre Kopien dupliziert. Cleanup entfernt Partialdateien und gibt Tabellen, Indizes und vorherige Records frei.

## Prozessspeicher und Laufzeiten

Jedes Szenario lief mit Supervisor und höchstens einem Worker im gemeinsamen harten Windows-Job: 536.870.912 Byte Commit, ActiveProcessLimit=2, bestätigte Mitgliedschaft des Workers. Alle Worker endeten mit Code 0. Die Prozessmessung enthält Eingangsdictionary, Referenzen, Anker, frühere Records, temporäre Kopien, Encoder und Decoder.

| Szenario | Gemeinsamer Kernel-Job-Peak | Gesamtzeit |
| --- | ---: | ---: |
| Fokussierte Fehler-/Grenztests | 60280832 Byte | 6.678 s |
| Beide bestehende Archive konvertieren und prüfen | 75427840 Byte | 77.888 s |
| Beide Handfolgen fortlaufend integrieren und prüfen | 64729088 Byte | 90.645 s |

Vorherige direkte Integration: 69181440 Byte Kernel-Peak und 94.934 s. Der neue Integrationserfolg zeigt nur einen kleinen Laufzeitgewinn; einzelne Phasen werden langsamer. Es wird kein allgemeiner Geschwindigkeitsvorteil behauptet.

| Fall / Integrationsphase | Vorher Sekunden | Nachher Sekunden | Nachher Python-Peak |
| --- | ---: | ---: | ---: |
| D_hand_case: Erfassung und Prüfungen | 23.551 | 35.400 | 11592468 Byte |
| D_hand_case: Finale Kodierung und Datei | 0.114 | 0.092 | 11809415 Byte |
| D_hand_case: Unabhängiger Decoder | 31.738 | 17.613 | 19952415 Byte |
| lifecycle_trace: Erfassung und Prüfungen | 15.674 | 23.710 | 12103593 Byte |
| lifecycle_trace: Finale Kodierung und Datei | 0.105 | 0.079 | 12348666 Byte |
| lifecycle_trace: Unabhängiger Decoder | 21.794 | 11.475 | 20498908 Byte |

Die Erfassung wird durch Differenzbildung langsamer, der Decoder schneller; die Gesamtlaufzeit verbessert sich nur gering. Tracemalloc lief während der gemessenen Phasen. Seine Peaks sind absolute lebende Pythonallokationen mit pro Phase zurückgesetzter Peakmarke, keine isolierten Nettowerte. Die Private-Bytes-Samples in supervisor.json können kurze Transienten verpassen; der gemeinsame Job-Peak ist kernelgemessen und enthält native Allokationen. Globaler Dateisystemcache und Interpreterstart vor Jobinstallation sind nicht separat zeitaufgelöst.

## Test-IDs und Ergebnisse

- `tests.test_s2uc_ura1_delta.DeltaTests.test_T01_full_bytes_numbers_metadata_and_anchors`: PASS.
- `tests.test_s2uc_ura1_delta.DeltaTests.test_T02_missing_and_swapped_deltas`: PASS.
- `tests.test_s2uc_ura1_delta.DeltaTests.test_T03_changed_span_and_wrong_initial_state`: PASS.
- `tests.test_s2uc_ura1_delta.DeltaTests.test_T04_invalid_delta_path_and_value_references`: PASS.
- `tests.test_s2uc_ura1_delta.DeltaTests.test_T05_management_record_and_write_failure_cleanup`: PASS.
- `tests.test_s2uc_ura1_delta.DeltaTests.test_T06_live_small_scope_and_original_bindings`: PASS.

T01 prüft vollständige kanonische Bytes, Zahlenrepräsentation einschließlich negativem Null, Metadaten, Zellen, Tickets und Anker. T02 entfernt beziehungsweise vertauscht Änderungen. T03 manipuliert Zeichenbereiche und den Anfangszustand. T04 verwendet ungültige Delta-, Pfad- und Wertreferenzen. T05 prüft Tabellen-/Dictionary-/Kanten-/Index-/Collectiongrenzen, einen übergroßen Record und Schreibfehler nach begonnener Partialausgabe mit Cleanup. T06 prüft einen regulären kleinen U/R-Fall und unveränderte Vorgängerbindungen.

Zusätzliche vollständige Abnahmen:

- A01: bestehendes vollständiges D-Handfallarchiv konvertiert, Anker und ursprünglicher kanonischer Hash bestätigt: PASS.
- A02: bestehendes vollständiges Lebenszyklusarchiv entsprechend geprüft: PASS.
- I01: reguläre 64-Frame-Handfolge mit beiden Armen, ursprünglichen Referenz-/Ereignisprüfungen und unabhängigem Decoder: PASS.
- I02: reguläre 48-Frame-Handfolge entsprechend geprüft: PASS.

Die sechs fokussierten Tests wurden zunächst zur Implementierungsprüfung und anschließend für den Ressourcenbeleg im gemeinsamen Job ausgeführt. Kein Größenlauf war Bestandteil dieser Prüfungen. Es gab keine Rekonstruktion der beim früheren Größenabbruch fehlenden Daten aus bloßen Ankern.

## Skalierungseinschätzung für beide Arme zusammen

Die folgenden linearen Abschätzungen verwenden die vollständigen U/R-Gesamtwerte des neuen 64-Frame-Falls und den Faktor 16. Es wird nicht nochmals mit zwei multipliziert, weil beide Arme bereits enthalten sind. Dies sind keine Messungen eines 1024-Frame-Falls.

- Dictionarybytezahl: 1127216.
- Dekomprimiertes Format: 1252128.
- gzip-Bytezahl: 223056.
- Tabelleneinträge: 24944.
- Referenzkanten: 161776.
- Recordindizes: 31072.
- Falllaufzeit in Sekunden: 850.3.
- Vollständig rekonstruierte Historienbytes (nicht gleichzeitig gehalten): 315653808.

Die Abschätzungen für Dictionary und Format liegen nun unter 4 MiB; Tabellen, Referenzen und gzip ebenfalls unter ihren Grenzen. Die geschätzte Laufzeit liegt unter 3540/3600 s. Das ist ein begründeter technischer Fortschritt gegenüber der vorherigen Darstellung, aber keine Garantie. Größere Generationen, längere Metadaten, mehr unterschiedliche Änderungslisten, geringere U/R-Wiederverwendung und Verwaltungsüberhang können das Wachstum verändern. Die Vorzustandspuffer werden nicht mit der gesamten Historienlänge multipliziert; sie bleiben auf aktuelle Records begrenzt. Der Prozesspeak wird wegen fixer und variabler Anteile nicht blind linear hochgerechnet.

Empfehlung an den Projektleiter: diesen begrenzten Codecstand abnehmen. Ein weiterer einmaliger neutraler Größenlauf wäre jetzt technisch besser begründet, benötigt aber eine neue ausdrückliche Beauftragung, einen angepassten separaten Einstieg und eine neue Vorstartbindung für dieses Format und seinen Decoder. Die alte Einmalfreigabe bleibt verbraucht. Hier wurde kein weiterer Größenlauf ausgeführt.

Die kleine erfolgreiche Abnahme belegt weder 1024-Frame-Machbarkeit noch eine Forschungsserie, einen U/R-Leistungsvorteil oder Forschungsbereitschaft. Es wird keine weitere Codecvariante an diesen Auftrag angehängt.

## Belege

- [analysis.json](C:/Users/TV/Documents/MCM_FIELD_ORGANISM/workspace/reports/s2uc/ura1-delta-development-20261015-01/analysis.json)
- [delta-components.json](C:/Users/TV/Documents/MCM_FIELD_ORGANISM/workspace/reports/s2uc/ura1-delta-development-20261015-01/delta-components.json)
- [scaling-estimates.json](C:/Users/TV/Documents/MCM_FIELD_ORGANISM/workspace/reports/s2uc/ura1-delta-development-20261015-01/scaling-estimates.json)
- [binding.json](C:/Users/TV/Documents/MCM_FIELD_ORGANISM/workspace/reports/s2uc/ura1-delta-development-20261015-01/binding.json)
- [faults/worker.json](C:/Users/TV/Documents/MCM_FIELD_ORGANISM/workspace/reports/s2uc/ura1-delta-development-20261015-01/faults/worker.json)
- [faults/supervisor.json](C:/Users/TV/Documents/MCM_FIELD_ORGANISM/workspace/reports/s2uc/ura1-delta-development-20261015-01/faults/supervisor.json)
- [archive/worker.json](C:/Users/TV/Documents/MCM_FIELD_ORGANISM/workspace/reports/s2uc/ura1-delta-development-20261015-01/archive/worker.json)
- [archive/supervisor.json](C:/Users/TV/Documents/MCM_FIELD_ORGANISM/workspace/reports/s2uc/ura1-delta-development-20261015-01/archive/supervisor.json)
- [integration/worker.json](C:/Users/TV/Documents/MCM_FIELD_ORGANISM/workspace/reports/s2uc/ura1-delta-development-20261015-01/integration/worker.json)
- [integration/supervisor.json](C:/Users/TV/Documents/MCM_FIELD_ORGANISM/workspace/reports/s2uc/ura1-delta-development-20261015-01/integration/supervisor.json)
- [Testausgabe](C:/Users/TV/Documents/MCM_FIELD_ORGANISM/workspace/reports/s2uc/ura1-delta-development-20261015-01/faults/tests.txt)
- [D_hand_case.delta.json.gz](C:/Users/TV/Documents/MCM_FIELD_ORGANISM/workspace/reports/s2uc/ura1-delta-development-20261015-01/integration/D_hand_case.delta.json.gz)
- [D_hand_case-capture.json](C:/Users/TV/Documents/MCM_FIELD_ORGANISM/workspace/reports/s2uc/ura1-delta-development-20261015-01/integration/D_hand_case-capture.json)
- [lifecycle_trace.delta.json.gz](C:/Users/TV/Documents/MCM_FIELD_ORGANISM/workspace/reports/s2uc/ura1-delta-development-20261015-01/integration/lifecycle_trace.delta.json.gz)
- [lifecycle_trace-capture.json](C:/Users/TV/Documents/MCM_FIELD_ORGANISM/workspace/reports/s2uc/ura1-delta-development-20261015-01/integration/lifecycle_trace-capture.json)
