# Methodik 014: Endlicher visueller Rezeptorpfad

## 1. Zweck

Vor einem visuellen MCM-Feld wird ein streng endlicher Video-In mit einer
lokalen, nichtsemantischen Rezeptorfläche geprüft:

```text
endliche technische Bildquelle
-> lokales Kanalraster
-> unveränderliche visuelle Rezeptorlage
-> gesperrte visuelle MCM-Feldgrenze
```

Die Prüfung verwendet zunächst synthetische Frames. Eine reale Kamera wird
erst später als explizite Quelle an denselben Vertrag angeschlossen.

## 2. Technischer Eingangsvertrag

Ein gültiger Frame besitzt:

- explizite Breite und Höhe,
- genau drei technische Quellkanäle,
- ganzzahlige Kanalwerte von 0 bis 255,
- einen fortlaufenden Frameindex,
- eine explizite Bildrate.

Farbbedeutung, Objektinhalt und Kameradiagnosen werden nicht übernommen.

## 3. Lokale Kanalfläche

Der Frame wird ohne Objekterkennung in rechteckige Zellen zerlegt. Pro Zelle
bleibt der Mittelwert jedes der drei technischen Quellkanäle erhalten.

```text
Frame H x W x 3
-> Raster R x C
-> R * C * 3 lokale technische Träger
```

Die Ausgabe wird auf `0..1` skaliert. Eine Zelle beeinflusst keine andere
Zelle. Die drei Kanäle werden nicht zu Helligkeit, Farbe oder Bedeutung
zusammengefasst.

## 4. Geometrie

Die Implementierung unterstützt jede Rastergeometrie, welche die explizite
Quellbreite und -höhe vollständig teilt. `12 x 8` ist ein erster Kandidat für
spätere 1.920-x-1.080-Frames, keine festgeschriebene visuelle Anatomie.

Die Rasterreduktion ist ein dokumentierter technischer Informationsverlust.
Rohpixel dürfen die Rezeptorgrenze nicht überschreiten.

## 5. Kontaktstatus

```text
active_zero:  alle lokalen Kanalwerte sind exakt null
active_light: mindestens ein lokaler Kanalwert ist ungleich null
```

Es wird keine Helligkeits-, Bewegungs- oder Ereignisschwelle angepasst.

## 6. Noch nicht enthalten

- Bewegung und Richtung,
- zeitlicher Kontrast,
- visueller Nachhall,
- Kanten- oder Formdetektion,
- Gesichter, Personen, Objekte oder Szenen,
- Aufmerksamkeit und Salienz,
- visuelle Beziehungen oder Musterklassen,
- ein visuelles MCM-Feld.

Diese Rollen dürfen erst nach einer konkret fehlenden Weltfunktion untersucht
werden.

## 7. Pflichtprüfungen

1. Schwarzer gültiger Frame ergibt exakte aktive Nulllage.
2. Lokale Kanalwirkung bleibt in ihrer Zelle und ihrem Quellkanal.
3. Gleiche globale Kanalsummen an verschiedenen Orten bleiben unterscheidbar.
4. Vertauschte Quellkanäle bleiben unterscheidbar.
5. Frame-Reihenfolge verändert nur den Sequenzdigest, nicht einzelne Frames.
6. Gleiche Folge erzeugt nach Neustart denselben Digest.
7. Ungültige Form, Datentypen und Werte werden abgelehnt.
8. Der Lauf liest exakt die vorgegebene Framezahl.
9. Ein zu kurzer Quelllauf liefert keine gültige Teilzusammenfassung.
10. Observer an oder aus verändert keinen Rezeptorzustand.
11. Rezeptorzustände enthalten keine Rohpixel und keine semantischen Rollen.
12. Nach Laufende wird kein weiterer Frame gelesen.

## 8. Baselines

- **V0:** globale Summe der drei Quellkanäle.
- **V1:** globaler Mittelwert jedes Quellkanals.
- **V2:** lokales Kanalraster ohne Zeitgeschichte.

V2 ist der implementierte Referenzkandidat. Er ist noch kein visuelles
MCM-Feld.

## 9. Evidenzziel

Maximal **E1** für endlichen Videovertrag, lokale Rezeptorfläche und
Rohdatengrenze. Visuelle Feldwirkung, Nachhall und multimodale reale
Konstellation bleiben **E0**.
