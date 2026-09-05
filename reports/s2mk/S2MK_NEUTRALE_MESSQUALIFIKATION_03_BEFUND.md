# S2-MK: Neutrale Messqualifikation 03

## Status

`S2MK_NEUTRAL_MOTION_MEASUREMENT_NOT_QUALIFIED_MEMORY_BOUND_EXCEEDED`

Die Qualifikation
`s2mk-neutral-motion-measurement-qualification-20260905-03` wurde genau
einmal gestartet und nicht wiederholt. Die historischen Versuche 01 und 02
bleiben unveraendert erhalten.

## Korrektur

`PoseV1` blieb unveraendert. Ausschliesslich die S2-MK-V1-Baselineform wurde
korrigiert:

- `background_channels` wird als `background_r`, `background_g` und
  `background_b` komponentenweise verglichen;
- die uebrigen zwoelf skalaren Posefelder bleiben einzeln;
- `support_cell_count` steht als numerische Differenz an letzter Stelle;
- die kanonische Rollenfolge besitzt exakt 16 Eintraege;
- es gibt keine Mittelwert-, Maximum- oder sonstige Aggregation der drei
  Hintergrundkanaele.

Der bestehende Test 08 variiert die drei neutralen Hintergrundkanaele
unabhaengig um `1/255`, `3/255` und `5/255`.

## Quellhashes vor dem Lauf

| Quelle | SHA-256 |
| --- | --- |
| `tools/_s2mk_private_motion_measurement.py` | `f297ad38877925fb3b6488024507babd9a4617c592c509f3dda615b4eb583759` |
| `tests/test_s2mk_private_motion_measurement.py` | `a54b1d01615f9d8865e35733a7621bde64fcd04e2fb23229e6056f97608949a8` |

## Einmaliger Aufruf

```text
.venv/Scripts/python.exe -m unittest -v tests.test_s2mk_private_motion_measurement
```

- Aufrufe: `1`;
- Exit-Code: `1`;
- ausgefuehrte Testkoerper: `15/15`;
- bestandene Testkoerper: `14/15`;
- terminales unittest-Ergebnis: `FAILED (failures=1)`.

Bestanden sind:

- qualifizierte lokale Runtimebindung;
- exakte ganzzahlige RGB-zu-Y-Projektion;
- kanonischer endlicher `float32`-Vorwaerts-/Rueckwaertsfluss;
- bilineare Abtastung und Randbehandlung;
- geometrische Korrespondenzen, Zyklus- und RGB-Residuen;
- vollstaendige ueberschneidungsfreie `12 x 8`-Zellabdeckung;
- feste Perzentil- und Summationsregeln;
- unabhaengige Pixel-, Rezeptor-, Pose- und Formbaseline;
- Ausschluss von Rohframes und Flussfeldern aus der Ausgabe;
- Quellen-, Zeit-, Algorithmus-, Geometrie- und Datentyp-Fehlergrenzen;
- Import- und Korpusgrenzen.

## Speicherbefund

Test 15 hat die gebundene Vollformatgrenze nicht eingehalten:

| Messung | Byte |
| --- | ---: |
| produktseitig gezaehlter Peak eigener NumPy-Puffer | `89.432.220` |
| gemessener Prozess-Working-Set-Anstieg | `183.652.352` |
| Working-Set-Anstieg einschliesslich bereits residenter Eingabeframes | `196.093.952` |
| gebundene Obergrenze | `134.217.728` |
| Ueberschreitung | `61.876.224` |

Die eigene Arrayprojektion bleibt unter der Grenze. Der gemessene lokale
Prozesspeak einschliesslich der OpenCV-internen Vollformatarbeit
ueberschreitet sie jedoch eindeutig. Die Grenze wird nicht erhoeht und der
Messwert wird nicht auf die sichtbaren Produktarrays reduziert.

Weitere neutrale Messwerte:

```text
forward_flow_digest  = b7726c413f5b8e6417c1e1a013d2ffcd9d7af60c738c33c2cb9a9e37e3c6bd4b
reverse_flow_digest  = aaeac0beead7d6861ca4471c7750b1f0848f0bafb2e142e467f8fc507f2b15f6
valid_correspondences = 2073600 / 2073600
result_canonical_bytes = 75321
```

Diese Werte stammen nur aus der neutralen Qualifikationsfixture. Sie sind
kein fachlicher Korpus- oder Objektidentitaetsbefund.

## Grenzen

- geoeffnete versiegelte Korpuspaare: `0`;
- Memoryaufrufe: `0`;
- Kontextaufrufe: `0`;
- Feldaufrufe: `0`;
- Parameter-, Algorithmus- oder Budgetaenderungen nach dem Lauf: `0`;
- Wiederholungen: `0`.

## Quellhashes nach dem Lauf

| Quelle | SHA-256 |
| --- | --- |
| `tools/_s2mk_private_motion_measurement.py` | `f297ad38877925fb3b6488024507babd9a4617c592c509f3dda615b4eb583759` |
| `tests/test_s2mk_private_motion_measurement.py` | `a54b1d01615f9d8865e35733a7621bde64fcd04e2fb23229e6056f97608949a8` |

## Entscheidung

Die 16-Rollen-Baselinekorrektur ist funktional belegt. S2-MK als Ganzes
bleibt wegen der real gemessenen Speicherueberschreitung technisch nicht
qualifiziert. Der Lauf ueber die acht vorversiegelten S2-MJ-Paare bleibt
gesperrt.

Ein weiterer Schritt benoetigt einen engen statischen Speicher- und
Lebensdaueraudit der Vollformatimplementierung. Er darf weder die Grenze
erhoehen noch Flowparameter, Korpus oder Algorithmus veraendern.
