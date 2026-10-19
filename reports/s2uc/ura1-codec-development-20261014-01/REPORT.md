# URA1: Abschluss der neutralen Archivkompaktierung

Stand 2026-10-14. MCM-KI-Entwickler an MCM KI Projektleiter.
Bezug: Anschlussauftrag zur verlustfreien Kompaktierung der vorhandenen neutralen URA1-Belege; ursprüngliches Prüfpaket dda37469-3a5d-4448-abcc-45f05509760e.

**PASS_CODEC_ONLY.** Beide vorhandenen Fälle erfüllen höchstens 512 KiB gzip und höchstens 4 MiB dekomprimiertes Archivformat. Vollständige kanonische Rekonstruktion und gezielte Manipulationserkennung sind belegt. Das ist keine Forschungsbereitschaft und keine neue Forschungsfreigabe.

## Dateien und Verfahren

- [tools/_s2uc_ura1_archive_encode.py](C:/Users/TV/Documents/MCM_FIELD_ORGANISM/workspace/tools/_s2uc_ura1_archive_encode.py): Encoder für referenzierte JSON-Teilbäume.
- [tools/_s2uc_ura1_archive_decode.py](C:/Users/TV/Documents/MCM_FIELD_ORGANISM/workspace/tools/_s2uc_ura1_archive_decode.py): Unabhängiger Decoder ohne Encoder- oder Policyimport; fortlaufende kanonische Rekonstruktion.
- [tests/test_s2uc_ura1_archive_codec.py](C:/Users/TV/Documents/MCM_FIELD_ORGANISM/workspace/tests/test_s2uc_ura1_archive_codec.py): Neun ausschließlich archivbezogene Codec-Tests.
- [tools/s2uc_ura1_archive_codec_qualify.py](C:/Users/TV/Documents/MCM_FIELD_ORGANISM/workspace/tools/s2uc_ura1_archive_codec_qualify.py): Fokussierter Codec-Prüfeinstieg, erzeugt neue Belege in separatem Verzeichnis.
- [docs/S2UC_URA1_ARCHIVFORMAT_V1.md](C:/Users/TV/Documents/MCM_FIELD_ORGANISM/workspace/docs/S2UC_URA1_ARCHIVFORMAT_V1.md): Offene Formatspezifikation, Integritäts- und Ressourcenvertrag.

Identische JSON-Teilbäume werden einmal gespeichert; geordnete Arrays und Objekte referenzieren frühere Knoten. Nach genau einer gzip-Dekompression liegt lesbares JSON mit skalaren Werten, Schlüsseln und Referenzen vor. Es gibt keine innere Kompression, Base64-Nutzlast oder versteckte expandierte Daten. Diese echte strukturelle Referenzkodierung ersetzt redundante Wiederholung; es wurden keine Ereignisse ausgelassen. Zahlen und Originalmetadaten bleiben erhalten. Python-Objektadressen waren im ursprünglichen JSON nicht vorhanden und werden nicht als rekonstruierte Identität behauptet.

Die Decoderimplementierung prüft das Schema und rückwärts gerichtete Referenzen eigenständig. Ihre fortlaufende Ausgabe wird gegen den extern gebundenen Originalhash und die Originalbytezahl geprüft. Zusätzlich vergleicht C01 die komplette Ausgabe unmittelbar Byte für Byte mit dem ursprünglichen kanonischen Record. Damit bleiben sämtliche Zustandsfelder, Ereignisse, Reihenfolgen, Tickets, Fehlerzellen und Auswahlunterschiede erhalten. Es wurden keine Policies ausgeführt oder neue Forschungsquellen erzeugt.

## Größenvergleich

Alle Größen in Byte. Die dekomprimierte kodierte Darstellung ist ausdrücklich von der vollständig rekonstruierten Historie getrennt.

| Fall | Original gzip | Neues gzip | Dekodiertes Archivformat (JSON-DAG) | Vollständig rekonstruierte kanonische Historie |
| --- | ---: | ---: | ---: | ---: |
| D_hand_case | 51765 | 24408 | 276323 | 3860092 |
| lifecycle_trace | 124396 | 19732 | 266560 | 13380342 |

Grenzen: gzip 524.288 Byte; dekomprimiertes Archivformat 4.194.304 Byte. Beide Fälle liegen darunter. Die vollständige Lebenszyklushistorie bleibt 13.380.342 Byte groß; sie ist weder gekürzt noch als unter 4 MiB ausgegeben. Der Auftrag erlaubt die getrennte Offenlegung bei echter Referenz-/Differenzkodierung. Der aktuelle Codec löst damit den Formatgrößenblocker für diese zwei Fälle, nicht für unbekannte größere Fälle.

## Ausgeführte Test-IDs und Decoderbelege

Ein fokussierter Codec-Prüfdurchlauf: neun Tests bestanden, 75,690 Sekunden einschließlich Speichermessungen. Keine Wiederholung der ursprünglichen N01–N14-Policyprüfungen. Präfix der folgenden IDs: tests.test_s2uc_ura1_archive_codec.CodecTests.

- `test_C01_full_byte_reconstruction_and_limits`: PASS.
- `test_C02_missing_event`: PASS.
- `test_C03_swapped_events`: PASS.
- `test_C04_invalid_and_cyclic_references`: PASS.
- `test_C05_damaged_state_reference`: PASS.
- `test_C06_manipulated_value_and_binding`: PASS.
- `test_C07_stream_and_materialized_memory`: PASS.
- `test_C08_original_bindings_unchanged`: PASS.
- `test_C09_scalar_types_and_repeated_identity_metadata`: PASS.

C01 prüft beide vollständigen kanonischen Records und beide Größenlimits. C02 entfernt ein Ereignis, C03 vertauscht zwei verschiedene interne Ereignisse. C04 injiziert negative, außerhalb liegende, boolesche und zyklische Referenzen. C05 beschädigt den Zustandsverweis eines Ereignisses: Das ist die passende Negativkontrolle für dieses Referenzformat, das keine Delta-Operationscodes besitzt. C06 verändert einen numerischen Wert und die deklarierte Originalbindung. Die manipulierten Archive werden jeweils neu gzip-kodiert; die Erkennung beruht daher nicht bloß auf einem ungültigen gzip-CRC. C09 prüft skalare Typunterschiede, negatives Null, Unicode, leere Container und verschiedene Originalmetadaten bei gleichem Wert.

Integritätsgrenze: Die vollständige Hashprüfung braucht einen separat vertrauenswürdigen Originalbezug. Ein gemeinsam mit seinem externen Vertrauensanker ersetztes Archiv wird hierdurch nicht authentifiziert. Der Decoder darf Bytes vor Abschluss an einen Sink liefern; diese sind bis zum erfolgreichen Abschluss vorläufig. Die Tests akzeptieren manipulierte Teilresultate nicht als geprüfte Historie.

## Speicherbedarf der Rekonstruktion

Gemessen mit Python 3.14.4 und tracemalloc. Der Tracer startet unmittelbar vor dem Decoderaufruf, einschließlich gzip-Dekompression, JSON-Parsing, Referenzvalidierung und Ausgaberekonstruktion. Vorab geladene Eingabebytes und Referenzoriginale sowie Interpreter-/Importgrundkosten sind nicht Teil dieser zusätzlichen Python-Peaks. Die Peakwerte sind keine Windows-Job- oder native Prozessgesamtmessung.

| Fall | Fortlaufende Prüfung: Python-Peak | Vollständige Bytes plus JSON-Baum: Python-Peak |
| --- | ---: | ---: |
| D_hand_case | 8589858 | 19531679 |
| lifecycle_trace | 8585166 | 61950316 |

Die fortlaufende Variante hält kodiertes JSON und Knotengraphen und prüft die Ausgabe inkrementell; sie sammelt die rekonstruierte Historie nicht. Die Materialisierungsvariante hält zusätzlich einen Bytes-Puffer und den vollständig rekonstruierten Python-JSON-Baum. Der größere Bedarf ist offengelegt, nicht dem Arm zugeschlagen oder als kostenloser Beobachter behandelt. Maximale Knotentiefe ist hier 11; der Decoder begrenzt sie auf 128. Die erwartete Originalbytezahl begrenzt die Expansion. Encoderkosten wurden in diesem Auftrag nicht als vollständige Prozessressource qualifiziert.

## Erhalt der Ursprungsbelege und Bindungen

C08 prüft sämtliche zehn Einträge der bestehenden neutralen Closure, die fünf dort gebundenen Entwicklungsdateien und alle 160 UF1-Vorgängerdateien unverändert. Die alte Closure selbst wird zusätzlich durch ihren SHA-256 in der neuen binding.json gebunden. Originalarchive, ursprünglicher Bericht und ursprüngliche Bindungen wurden nicht verändert. Die neuen Codecdateien und Formatspezifikation erhalten eine eigene Bindung; neue Archive liegen ausschließlich im separaten Codec-Belegverzeichnis.

## Verbleibende Risiken und nächster Schritt

Es wurden ausschließlich die beiden vorhandenen kleinen Fälle verwendet. Die Referenztabelle wächst mit der Zahl unterschiedlicher Teilbäume; veränderte Zustände können die Wiederverwendung reduzieren. Fortlaufende Ausgabe spart die expandierte Historie, hält aber weiterhin das komplette kodierte Dokument. Laufzeit wächst mit dem vollständig rekonstruierten Inhalt. Die Größen- und Speicherwerte lassen sich daher nicht als Garantie für 32 vollständige Geschichten verwenden.

Offen bleiben insbesondere die Gesamtprozess-/Beobachterbilanz, native Allokationen, Konstruktortransienten und spätere vollständige Export-/Laufzeitqualifikation. Es gab keinen Größenablauf, keine Bootstrapmatrix, keinen Forschungsversuch und keine Änderung der U/R-Regeln. Die frühere Forschungsfreigabe wird nicht erneuert.

Empfohlener nächster Schritt an den Projektleiter: den jetzt belegten neutralen Codec abnehmen und einen gesonderten, begrenzten Auftrag zur offenen Prozess-/Beobachter- und Konstruktorressourcenbilanz formulieren. Dabei den fortlaufenden Decoder als Ausgangspunkt verwenden und die noch nicht belegte Skalierung ausdrücklich erhalten. Ein Größenablauf oder neue Quellen folgen nicht automatisch daraus.

## Belege

- [tests.json](C:/Users/TV/Documents/MCM_FIELD_ORGANISM/workspace/reports/s2uc/ura1-codec-development-20261014-01/tests.json)
- [tests.txt](C:/Users/TV/Documents/MCM_FIELD_ORGANISM/workspace/reports/s2uc/ura1-codec-development-20261014-01/tests.txt)
- [evidence.json](C:/Users/TV/Documents/MCM_FIELD_ORGANISM/workspace/reports/s2uc/ura1-codec-development-20261014-01/evidence.json)
- [binding.json](C:/Users/TV/Documents/MCM_FIELD_ORGANISM/workspace/reports/s2uc/ura1-codec-development-20261014-01/binding.json)
- [D_hand_case.dag.json.gz](C:/Users/TV/Documents/MCM_FIELD_ORGANISM/workspace/reports/s2uc/ura1-codec-development-20261014-01/D_hand_case.dag.json.gz)
- [lifecycle_trace.dag.json.gz](C:/Users/TV/Documents/MCM_FIELD_ORGANISM/workspace/reports/s2uc/ura1-codec-development-20261014-01/lifecycle_trace.dag.json.gz)
- [Unveränderter ursprünglicher Entwicklungsbericht](C:/Users/TV/Documents/MCM_FIELD_ORGANISM/workspace/reports/s2uc/ura1-neutral-development-20261014-01/REPORT.md)
