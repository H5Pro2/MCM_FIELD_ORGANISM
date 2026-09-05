# S2-MM: Sparse-LK-Capability-Preflight

## Status

`S2MM_SPARSE_LK_PATH_UNAVAILABLE`

Der neutrale Preflight
`s2mm-sparse-lk-capability-preflight-20260905-01` wurde genau einmal
ausgefuehrt und nicht wiederholt. Er endete mit Exit-Code `3`.

Dies ist kein Bewegungs-, Korrespondenz-, Objektidentitaets-, Memory-,
Kontext- oder Feldbefund. Keines der acht vorversiegelten S2-MJ-Korpuspaare
wurde geoeffnet.

## Statischer Ressourcenbefund

Vor dem Preflight wurde fuer den fest gebundenen Pfad mit `1.536` Punkten,
Fenster `21 x 21` und den vier Ebenen `0...3` folgende benannte
Vollformatbelegung hergeleitet:

| Rolle | Byte |
| --- | ---: |
| zwei RGB8-Frames | `12.441.600` |
| zwei Grauprojektionen | `4.147.200` |
| zwei gepolsterte Bildpyramiden | `5.994.612` |
| wiederverwendetes maximales Ableitungsfeld | `8.805.456` |
| Punkt-, Status- und Fehlerarrays beider Richtungen | `52.224` |
| **benannte Belegung** | **`31.441.092`** |
| Abstand zur Grenze `134.217.728` | **`102.776.636`** |

Damit besteht fuer Sparse-LK keine dem dichten S2-MK-Pfad entsprechende
strukturelle Vollbildmatrix-Untergrenze oberhalb von 128 MiB. Dieser
statische Befund erlaubte den neutralen Preflight, ersetzte dessen reale
Prozessmessung aber nicht.

## Einmaliger Aufruf

```text
.venv/Scripts/python.exe tools/_s2mm_private_sparse_lk_preflight.py \
  --output-root C:/Users/TV/Documents/MCM_FIELD_ORGANISM/workspace/reports/s2mm \
  --contract-file-sha256 c39d3deec31c5e04c9b08cc31287926b9277a4b8bab969a94ae7b000ca2458f2
```

Der Lauf verwendete:

- eine interne neutrale Vollformat-RGB8-Fixture;
- das feste `12 x 8 x 4 x 4`-Punktgitter;
- zweimal dieselbe vollstaendige Vorwaerts-/Rueckwaertsauswertung;
- OpenCV-Einzelthreadbetrieb und deaktiviertes OpenCL;
- keine Vorwaermung;
- keine Projektmodule oder Projektfunktionen.

## Abbruch

Der terminale Fehler lautet:

```text
RuntimeError: repeated sparse LK output is not bit-identical
```

Beide Auswertungen hatten `_track_pass` vollstaendig verlassen. Damit war
jeweils insbesondere die Mindestzahl von `1.152` geometrisch gueltigen
Tracks erreicht. Mindestens ein Bestandteil der vollstaendig gebundenen
Ergebnisform unterschied sich danach jedoch zwischen den beiden
Auswertungen.

Der Preflight publiziert bei dieser Abweichung absichtlich keine
Einzelresultate. Aus den vorhandenen Artefakten darf daher nicht
nachtraeglich behauptet werden, ob Punktkoordinaten, Status, Fehlerwerte,
Zyklusresiduen, RGB-Residuen oder deren Zusammenfassungen abwichen.

Die Prozesspeakpruefung lag nach der Reproduzierbarkeitspruefung und wurde
nicht erreicht. Es existiert deshalb kein gueltiger gemessener S2-MM-Peak.
Der statische Wert darf nicht als Ersatz fuer diese fehlende Messung
umgedeutet werden.

## Artefakte

| Artefakt | Bindung |
| --- | --- |
| Vertrag | `docs/S2MM_RESSOURCENBEGRENZTE_SPARSE_BEWEGUNGSKORRESPONDENZ_VERTRAG.md` |
| Vertrags-SHA-256 | `c39d3deec31c5e04c9b08cc31287926b9277a4b8bab969a94ae7b000ca2458f2` |
| Capability-Digest | `a5d69e7dbab50b2ddf3a7929b9a8ad34a36023b1f3194f63c55a1d2fdb565b60` |
| Resultatdatei-SHA-256 | `c634cb5f231d5023b120930eebcf1e7727f342e6d0a73eb01b7ada2e95159c76` |

Die maschinenlesbaren Artefakte liegen unveraendert unter:

`reports/s2mm/s2mm-sparse-lk-capability-preflight-20260905-01/`

## Grenzen

- Korpusframes geoeffnet: `0`;
- Projektmodule importiert: `0`;
- Projektfunktionen aufgerufen: `0`;
- Memory-, Kontext- und Feldaufrufe: `0`;
- Installations-, Aktualisierungs- oder Fallbackaufrufe: `0`;
- Wiederholungen des Preflights: `0`.

## Entscheidung

Der gebundene S2-MM-Pfad ist unter dieser Qualifikations-ID nicht
reproduzierbar qualifiziert. Es wird kein Korpus vorversiegelt oder
ausgefuehrt und kein Bewegungs- oder Kontinuitaetssignal behauptet.

Der statische Ressourcenbefund bleibt gueltig, reicht allein aber nicht zur
Freigabe. Eine erneute Ausfuehrung, Parameterkorrektur oder diagnostische
Nachmessung erfolgt in diesem Schritt nicht.
