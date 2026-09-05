# S2-MM: Ressourcenbegrenzte sparse Bewegungskorrespondenz

## Status und Grenze

S2-MM ist ein neuer, vom terminal geschlossenen dichten S2-MK-Pfad
getrennter Messvertrag. Er prueft ausschliesslich, ob ein festes Punktgitter
mit pyramidalem Lucas-Kanade unter der bestehenden Vollformat- und
Speichergrenze technisch reproduzierbar messbar ist.

Die Ausgabe ist Korrespondenzevidenz. Sie behauptet weder Objektidentitaet
noch Familienzugehoerigkeit und darf keine Memory-, Kontext- oder
Feldentscheidung beeinflussen.

## Eingang

Jeder spaetere Paaraufruf erhaelt genau zwei kanonische RGB8-Frames:

- Geometrie: `1920 x 1080 x 3`;
- Typ: `uint8`;
- C-zusammenhaengende RGB-Reihenfolge;
- gleiche visuelle Quellenuhr;
- strikt fortschreitende, nicht ueberlappende Framefenster;
- vor dem Messaufruf gebundene Payloaddigests.

Die Grauprojektion verwendet unveraendert die ganzzahlige Regel
`(77R + 150G + 29B + 128) >> 8`. Es gibt kein Resize, keine
Farbraumkorrektur und keine Korpus- oder Sollinformation im Messpfad.

## Festes Punktgitter

Das Punktgitter ist allein aus der Vollformatgeometrie abgeleitet:

- `12 x 8` Zellen;
- `4 x 4` Punkte je Zelle;
- exakt `1.536` Punkte;
- X-Positionen je Zelle bei `20, 60, 100, 140` Pixel relativ zur Zellkante;
- Y-Positionen je Zelle bei `16,875`, `50,625`, `84,375`, `118,125`
  Pixel relativ zur Zellkante;
- kanonischer Typ `float32`, Form `(1536, 1, 2)`;
- zeilenweise Ordnung: Zelle, Unterzeile, Unterspalte.

Es gibt keine Keypointwahl aus Pixelwerten, keinen Detektor, keine
Nachbesetzung und keine variable Punktzahl.

## Lucas-Kanade-Bindung

Der einzige zugelassene Kandidat ist
`cv2.calcOpticalFlowPyrLK` aus dem bereits gebundenen lokalen
OpenCV-`4.13.0`-Build mit:

| Parameter | Wert |
| --- | --- |
| Fenster | `21 x 21` |
| `maxLevel` | `3` |
| Ebenen | `0, 1, 2, 3` |
| Terminierung | `COUNT + EPS` |
| maximale Iterationen | `30` |
| Epsilon | `0,01` |
| Flags | `0` |
| `minEigThreshold` | `0,0001` |
| OpenCV-Threads | `1` |
| OpenCL | aus |

Jedes Paar wird vorwaerts und rueckwaerts gerechnet. Ein Track ist nur
geometrisch gueltig, wenn beide OpenCV-Statuswerte gelten, alle Koordinaten
endlich sind und Vorwaerts- sowie Rueckwaertspunkt innerhalb des
Vollformats liegen.

Zyklusresiduum und bewegungskompensiertes RGB-Residuum werden pro gueltigem
Punkt gemessen und nur als feste Verteilungszusammenfassungen ausgegeben.
Es wird noch keine fachliche Matchschwelle gewaehlt.

Weniger als `1.152` gueltige Tracks, also weniger als `75 %` des festen
Gitters, ergeben `INSUFFICIENT_VALID_TRACKS` und damit Enthaltung. Punkte
werden nicht nachgeliefert oder umgeordnet.

## Statischer Ressourcenbeleg

Der OpenCV-4.13-CPU-Pfad baut mit `withDerivatives=false` je Eingabegrau-
bild eine gepolsterte `uint8`-Pyramide. Fuer das vorherige Bild wird ein
einziges gepolstertes `int16 x 2`-Ableitungsfeld auf Maximalgroesse erzeugt
und ueber die Ebenen wiederverwendet.

Bei Fensterbreite `21` gelten pro Pyramide:

| Ebene | Nutzform | gepolsterte Form | Byte |
| ---: | --- | --- | ---: |
| 0 | `1920 x 1080` | `1962 x 1122` | `2.201.364` |
| 1 | `960 x 540` | `1002 x 582` | `583.164` |
| 2 | `480 x 270` | `522 x 312` | `162.864` |
| 3 | `240 x 135` | `282 x 177` | `49.914` |
| **eine Pyramide** |  |  | **`2.997.306`** |
| **zwei Pyramiden** |  |  | **`5.994.612`** |

Das maximale Ableitungsfeld belegt
`1962 x 1122 x 2 x 2 = 8.805.456` Byte. Zusammen mit zwei RGB-Frames,
zwei Grauprojektionen und allen kanonischen Punkt-/Status-/Fehlerarrays
ergibt sich folgende benannte Belegung:

| Rolle | Byte |
| --- | ---: |
| zwei RGB8-Frames | `12.441.600` |
| zwei Grauprojektionen | `4.147.200` |
| zwei gepolsterte Bildpyramiden | `5.994.612` |
| wiederverwendetes Ableitungsfeld | `8.805.456` |
| Punkt-, Status- und Fehlerarrays beider Richtungen | `52.224` |
| **benannte Oberflaeche** | **`31.441.092`** |

Gegenueber `134.217.728` Byte verbleiben `102.776.636` Byte fuer
OpenCV-Zeilenpuffer, `pyrDown`-Arbeit, Pythonobjekte, Allokatorverhalten und
Messinfrastruktur. Anders als bei S2-MK existiert keine strukturelle
Vollbildmatrix-Untergrenze oberhalb des Budgets.

Dieser statische Befund erlaubt nur einen neutralen Vollformat-Preflight.
Die Ressourcengrenze gilt erst dann als technisch eingehalten, wenn dessen
unveraenderte Prozess-Working-Set-Messung einschliesslich beider residenter
RGB-Frames strikt unter `134.217.728` Byte bleibt.

## Neutraler Capability-Preflight

Der Preflight darf genau einmal unter
`s2mm-sparse-lk-capability-preflight-20260905-01` laufen. Er verwendet eine
interne neutrale Vollformatfixture und oeffnet keine Korpusdatei.

Er bindet:

- Python-, OpenCV- und NumPy-Version;
- Pfad, Groesse und SHA-256 des geladenen `cv2`-Binaermoduls;
- Digest von `cv2.getBuildInformation()`;
- vorhandenes `calcOpticalFlowPyrLK`;
- Einzelthread und deaktiviertes OpenCL;
- exakte RGB-, Grau- und Punktgitterdigests;
- Vorwaerts-/Rueckwaertsform, `float32`, Endlichkeit und Statusformen;
- Anzahl geometrisch gueltiger Tracks;
- Track-, Zyklus- und RGB-Residuumdigests;
- zwei bitgleiche Auswertungen derselben neutralen Fixture;
- Prozesspeak ohne Vorwaermung auf der bestehenden Messbasis.

Frames, Graubilder, Pyramiden und Punktarrays duerfen nicht im Ergebnis
erscheinen. Installation, Aktualisierung, Ersatzbibliothek, Prozessaufteilung
und Vorwaermung sind ausgeschlossen.

## Entscheidung

Nur bei vollstaendiger Bindung, bitgleicher Wiederholung, mindestens
`1.152` gueltigen Tracks und einem gemessenen Peak unter `134.217.728` Byte
lautet der Befund:

`S2MM_SPARSE_LK_PATH_AVAILABLE`

Jede Abweichung lautet:

`S2MM_SPARSE_LK_PATH_UNAVAILABLE`

Ein bestandener Preflight ist noch kein Bewegungs- oder
Kontinuitaetsbefund. Erst danach darf ein neuer Korpus vorversiegelt werden.

