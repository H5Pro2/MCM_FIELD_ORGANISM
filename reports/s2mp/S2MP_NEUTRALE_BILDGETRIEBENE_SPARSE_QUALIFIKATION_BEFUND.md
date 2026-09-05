# S2-MP: Neutrale bildgetriebene Sparse-Qualifikation

## Status

`S2MP_FEATURE_SPARSE_CORRESPONDENCE_VALID`

Die aktuelle private S2-MP-Komponente ist unter der Qualifikations-ID
`s2mp-neutral-feature-sparse-qualification-20260905-02` mit `10/10`,
Exit-Code `0` und terminalem `OK` neutral qualifiziert.

Dies ist noch kein Korpus-, Bewegungs-, Fortsetzungs-, Objektidentitaets-,
Memory-, Kontext- oder Feldbefund.

## Nicht qualifizierender erster Aufruf

Die ID `s2mp-neutral-feature-sparse-qualification-20260905-01` erreichte
keinen Testkoerper. Der Loader konnte den Produktbaustein wegen eines nur
fuer direkten Skriptstart gueltigen privaten Importpfads nicht importieren:

```text
ModuleNotFoundError: No module named '_s2mm_private_sparse_lk_preflight'
```

Danach wurde ausschliesslich dieser Import auf die kanonische Paketform
`tools._s2mm_private_sparse_lk_preflight` korrigiert. Testdefinitionen,
Detectorparameter, LK-Parameter, Grenzen und neutrale Fixtures blieben
unveraendert. Der erste Aufruf bleibt transparent nicht qualifizierend.

## Qualifizierender Aufruf

```text
.venv/Scripts/python.exe -m unittest \
  tests.test_s2mp_private_feature_sparse_correspondence
```

Ausgabe:

```text
..........
----------------------------------------------------------------------
Ran 10 tests in 1.051s

OK
```

## Gepruefte Bindungen

Die zehn vorregistrierten Tests bestaetigen:

1. lokale CPython-, OpenCV-, NumPy-, Binaer-, Einzelthread- und
   OpenCL-Bindung;
2. unveraenderte Detector- und LK-Algorithmusbindung;
3. bitdeterministische Shi-Tomasi-Kandidatenwahl aus dem ersten Frame;
4. maximal `16` Punkte je Zelle und `1.536` Punkte insgesamt;
5. eindeutige, zell- und koordinatengeordnete Kandidaten;
6. gueltige Vorwaerts-/Rueckwaertskorrespondenz auf neutraler Translation;
7. vollstaendige Status- und ausschliesslich gueltige Punkt-, Fehler- und
   Residuenbindungen;
8. konsistente Kandidaten- und Trackabdeckung ueber alle 96 Rasterzellen;
9. regulaeres `INSUFFICIENT_MOTION_EVIDENCE` auf uniformer Eingabe ohne
   technischen Fehler;
10. Fail-Closed bei Zeit-, Digest- und Typfehlern, unveraenderte Eingaben,
    keine Roharrays in der Ausgabe und Prozesspeak unter `134.217.728` Byte.

Der Peaktest hat die gebundene Obergrenze bestanden. Der konkrete
Zwischenwert wurde vom vorregistrierten Test nicht als Ergebnisartefakt
publiziert und wird nicht nachtraeglich durch eine weitere Messung ersetzt.

## Quellen- und Hashbindung

| Artefakt | SHA-256 vor und nach ID `...-02` |
| --- | --- |
| Vertrag | `8f44f0903f9756f4cd760b18d2f0f2e70c1fec4b0dab8530f1f0c3c006027e24` |
| Produktmodul | `4e0e2b7fb19118a958469ee550d0cd90dc5c557b16529ff5c9fa8efa015dccf9` |
| Testdatei | `bce0a5216c78d6f3e7a227c57f299a8adc7dd977956e5d27664cc2e5ebe3e90e` |

Die fachliche Grundlage entspricht der offiziellen OpenCV-Dokumentation:
`goodFeaturesToTrack` waehlt starke Shi-Tomasi-Ecken anhand von
`qualityLevel` und `minDistance`; `calcOpticalFlowPyrLK` verwirft Merkmale
unter `minEigThreshold` ueber seinen Statusbeleg. Siehe
[Shi-Tomasi](https://docs.opencv.org/4.13.0/d8/dd8/tutorial_good_features_to_track.html)
und [Sparse PyrLK](https://docs.opencv.org/4.13.0/dc/d6b/group__video__track.html).

## Grenzen und Folge

- geoeffnete Korpusframes: `0`;
- Korpus-, Memory-, Kontext- oder Feldaufrufe: `0`;
- Schwellen- oder Detectoranpassungen nach einem Ergebnis: `0`;
- erneute S2-MO-Ausfuehrungen: `0`.

S2-MP ist damit als private bildgetriebene Sparse-Messkomponente technisch
qualifiziert. Der naechste zulaessige Forschungsschritt ist die separate
Vorversiegelung genau eines neuen, nicht aus S2-MO angepassten Korpus. Erst
danach darf ein einmaliger ordinaler Vergleich gegen direkte Bild-,
Rezeptor-, Pose- und Formbaselines erfolgen.
