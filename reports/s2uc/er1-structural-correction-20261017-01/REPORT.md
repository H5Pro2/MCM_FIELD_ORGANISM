# ER1: neutral geprüfte Korrektur des strukturellen Bestandsvergleichs

2026-10-17. Workflow `3d0c238b-1428-4946-b3f0-8631eccfc978`.
Status **KORREKTUR_NEUTRAL_GEPRUEFT_ZUR_ABNAHME**.

Ein getrennter Prüfpfad behebt den darstellungsbedingten Vergleichsfehler.
10/10 gezielte Strukturtests, ein kurzer neutraler Archivdurchlauf mit eigener
unabhängiger E/F-Referenz und ein gezielt manipuliertes Negativarchiv bestehen
die jeweiligen Erwartungen. Keine Integration in den gebundenen Forschungseinstieg,
keine neue Berechtigung, kein Retry oder Resume.

## Zulässige Darstellung und vollständig erhaltene Prüfung

`_s2uc_er1_stock_structural.py` vergleicht vollständige typisierte Strukturen.
Einzig die Schlüssel in observation_end werden auf Integer vereinheitlicht.
Zulässig: positive Integer 1 bis 2^64−1 oder exakt deren kanonische
ASCII-Dezimaldarstellung als String. Beide Enden 9/10 und 99/100 sind geprüft.

Unzulässig sind Bool, Float, Null, negative/Nullschlüssel, führende Nullen,
Vorzeichen, Leerzeichen, Exponential-/Dezimalschreibweise, Unicodeziffern,
Überlauf und falscher Maptyp. Mehrfachbelegung derselben normalisierten
Generation, etwa 9 und "9", wird auch bei gleichen Endmarken verworfen.
Jeder Eintrag wird geprüft, bevor er in die normalisierte Abbildung gelangt;
es gibt kein stilles Überschreiben, Weglassen oder Zusammenführen.

Objekte sind ungeordnete Abbildungen, Arrays bleiben strikt geordnet.
JSON-Arrays dürfen auf der Pythonseite als Liste oder Tupel vorliegen, wie
bereits beim bisherigen JSON-Vergleich. Das führt keine neue fachliche
Gleichsetzung ein. **Retained-Reihenfolge wird niemals sortiert.**
Integer-, Bool-, Float- und Stringwerte werden nicht ineinander umgewandelt.
Gleitkommawerte werden bitgenau einschließlich des Vorzeichens von Null
verglichen; nichtendliche Werte werden abgelehnt. Eingaben werden nicht verändert.

Vollständig prüfpflichtig bleiben alle vorhandenen Felder, insbesondere:
Retained-/Candidate-Spuren, Reihenfolge, Generationswerte, Originalordinale,
Framewerte, Bildungsordinale, Seriennummern sowie jede Endmarke. Fehlende oder
zusätzliche Einträge/Felder, falsche Endmarken, veränderte Originale und
vertauschte Retained-Reihenfolgen bleiben Fehler. Auch Felder außerhalb der
explizit aufgezählten Beispiele werden nicht aus dem Vergleich herausgefiltert.

Doppelte identische Schlüssel im Archivdrahtformat werden weiterhin vom
unveränderten strikten Reader zurückgewiesen. Ein Python-Dictionary kann einen
bereits vor Funktionsaufruf überschriebenen identischen Schlüssel nicht mehr
sichtbar machen; der Archivdecoder verhindert diesen Informationsverlust am Eingang.
Unterschiedlich typisierte Kollisionsschlüssel werden zusätzlich im neuen Vergleich
zurückgewiesen.

## Getrennter Archivpfad und statischer Vergleichsaudit

`_s2uc_er1_structural_archive.py` ist eine separate Kopie des fachlichen
Prüfpfads mit gezielter Änderung der Vergleiche. Er akzeptiert ausschließlich
als neutral markierte Archive mit höchstens 128 Frames; keine Forschungsintegration.
Die Prüfung des neutralen Umfangs erfolgt vor Integritätsrekonstruktion und
Armreferenzfortschreibung. Der vorhandene Forschungsdatensatz wurde nicht eingelesen
oder neu referenziert. Für dessen Erhaltung wurden nur Dateihashes gelesen.

| Vergleich im bisherigen ER1-Archivpfad | Schlüsselstruktur | Behandlung |
|---|---|---|
| ARCHIVE_STOCK | observation_end mit Integer-/String-Generationsschlüsseln | Vollständiger neuer Strukturvergleich |
| ARCHIVE_OBSERVER | verschachtelte before-/after-Bestände mit denselben Maps | Vollständiger neuer Strukturvergleich, dieselbe begrenzte Schlüsselnormalisierung |
| ARCHIVE_FEEDBACK | feste Stringfeldnamen, Schlüssel als Arraywerte | Unverändert; kein Generationsschlüssel als Objektkey |
| ARCHIVE_CHOICE | Null oder Schlüsselarray | Unverändert |
| ARCHIVE_MATCHES | feste Stringfeldnamen; Generation in Arraywerten | Unverändert |
| ARCHIVE_MECHANISMS | feste Stringfeldnamen; Generation/Originale als Werte | Unverändert |
| ARCHIVE_CELLS | direkte Python-Tupelschlüssel beider Seiten | Unverändert; kein JSON-Objektschlüsselvergleich |

Die ältere neutrale Archivvariante weist denselben Bestandsvergleich auf;
sie bleibt als historisch gebundener Code unverändert. Capture-Anker normalisieren
JSON bereits vor dem Hashen; der Delta-Reader verlangt eindeutige Stringschlüssel
im Drahtformat. Diese unabhängigen Integritätsprüfungen wurden nicht ersetzt.

Erhalten sind Capture-Anker, vollständiger kanonischer Hash, Daten-/Größengrenzen,
eigene Referenzbestände je Arm, Fehlerzellen, Matches, Berechtigungen, vorherige
Fehlerwerte, gewählte Herkunft, Ausgaben, Feedback, Anzahlprüfungen, Beobachter-
und Mechanismenbelege sowie Cleanup. Es werden keine Bankbytes, Stockfelder,
Originale oder Endmarken ausgeblendet.

## Konkrete Tests und kurzer Archivdurchlauf

[Testprotokoll](tests.log), [Ergebnis und Ressourcen](result.json):

- `tests.test_s2uc_er1_stock_structural.Structural.test_01_generation_boundaries_and_json_roundtrip`
- `tests.test_s2uc_er1_stock_structural.Structural.test_02_insertion_order_and_mixed_unique_types`
- `tests.test_s2uc_er1_stock_structural.Structural.test_03_invalid_generation_keys`
- `tests.test_s2uc_er1_stock_structural.Structural.test_04_collision_and_invalid_map_rejected`
- `tests.test_s2uc_er1_stock_structural.Structural.test_05_missing_extra_and_changed_endmarks`
- `tests.test_s2uc_er1_stock_structural.Structural.test_06_originals_order_and_values_still_checked`
- `tests.test_s2uc_er1_stock_structural.Structural.test_07_numeric_values_not_coerced_or_rounded`
- `tests.test_s2uc_er1_stock_structural.Structural.test_08_nested_observer_stock_and_no_input_mutation`
- `tests.test_s2uc_er1_stock_structural.Structural.test_09_upper_bound_and_nonfinite`
- `tests.test_s2uc_er1_stock_structural.Structural.test_10_wire_duplicate_keys_rejected`

Der eigenständige neutrale Eingang enthält zehn unterschiedliche Viererspuren,
je zweimal beobachtet: 80 Frames je Arm, zwei frische Arme. Es wurden keine
historischen Spuren oder Forschungsquellen übernommen und keine Generationen
in einem Forschungsbestand künstlich hochgesetzt. Die abschließenden Endmarken
sind in beiden Armen {9:72, 10:80}. 99/100 wird gezielt mit synthetischen
vollständigen Bestandsstrukturen geprüft, nicht mit einem großen Policyfall.

[neutral-80.gz](neutral-80.gz) besteht Capture-Integrität und beide unabhängigen
Armreferenzen mit dem korrigierten Prüfpfad. [capture.json](capture.json) hält
seine vor der Kodierung erfassten Anker fest. Keine fachliche Neubewertung des
vorhandenen Forschungsarchivs ist damit verbunden.

Im zusätzlichen neutralen Negativarchiv [negative-endmark.gz](negative-endmark.gz)
wurde eine Endmarke im Zustand nach Frame 80 verändert. Capture-Anker und
Archivhash wurden für dieses absichtlich falsche Testmaterial neu berechnet.
Die Integritätsprüfung reicht deshalb allein nicht zur Abwehr; der neue
fachliche Vergleich weist es erwartungsgemäß mit ARCHIVE_STOCK zurück.
Die Testfunktion in s2uc_er1_structural_qualify.py hält den konkreten Aufbau fest.

Eine erste Entwicklungsfassung des Negativarchivs referenzierte nicht mehr alle
Codecsequenzen und wurde bereits mit COLLECTION_COMPLETENESS zurückgewiesen.
Der Testaufbau wurde korrigiert; die Korrekturlogik wurde dafür nicht gelockert.
Dieser Entwicklungsstand bleibt unter ../er1-structural-development-01 erhalten.
Die oben ausgewiesene endgültige Prüfung testet tatsächlich den falschen Bestand.

## Ressourcen und Cleanup

| Größe der endgültigen neutralen Qualifikation | Messwert |
|---|---:|
| Gesamtdauer | 10.596401 s |
| Archivprüfung, instrumentiert | 5.040376 s |
| Pythonpeak der Archivprüfung | 17608227 Bytes |
| Windows-Jobpeak | 89079808 Bytes |
| Positives Archiv gzip | 26127 Bytes |
| Encoded | 201913 Bytes |
| Dictionary | 196256 Bytes |
| Größter Record | 14134 Bytes |
| Collections im positiven Archiv | 14 |
| Zusätzliche Collection im negativen Testmaterial | 1 |

Ein Qualifikationsprozess, 512-MiB-Jobgrenze; die vom Jobwerkzeug verwendete
allgemeine Mitgliederbeschreibung ist keine Behauptung eines zusätzlichen Workers.
Beide Arme geschlossen und Banken geleert, Codec inaktiv, keine Partialdateien.
Der strukturelle Vergleich gehört zum externen Prüfer und verändert weder Policy
noch deren Informationszugang. Keine Hochrechnung auf vollständige Forschungsfälle
und keine neue Laufzeitfreigabe aus diesen Messungen.

## Unveränderte historische Belege und Lieferung

[preservation.json](preservation.json) bestätigt unveränderte Prüfsummen für
2967 historisch gebundene Dateien, 43 Qualifikationsartefakte sowie alle 43 Dateien
der Forschungs-Abbruchübergabe. Vorstartbindung, bestehende Berechtigung,
Verbrauchsmarker, Quellen, Forschungsarchiv und Abbruchbelege bleiben unverändert.
Die Hinzufügung des separaten Prüfpfads ist keine neue Vorstartbindung.

Neu angelegt:

- `tools/_s2uc_er1_stock_structural.py`
- `tools/_s2uc_er1_structural_archive.py`
- `tools/s2uc_er1_structural_qualify.py`
- `tests/test_s2uc_er1_stock_structural.py`

Die drei Projektübersichten werden auf diesen Korrekturstand aktualisiert.
Empfohlener nächster Schritt: Projektleiter nimmt die begrenzte Korrektur anhand
dieser Nachweise ab und entscheidet anschließend über eine gesonderte Integration.
Ein gegebenenfalls neu gebundener Einstieg wäre ein eigener Auftrag. Die alte
Einmalfreigabe bleibt verbraucht; das alte Forschungsarchiv bleibt ungeprüft und
wird durch diese Korrektur nicht nachträglich freigegeben.
