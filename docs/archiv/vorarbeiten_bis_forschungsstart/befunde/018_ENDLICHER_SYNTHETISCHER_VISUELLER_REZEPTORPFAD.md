# Befund 018: Endlicher synthetischer visueller Rezeptorpfad

## 1. Kurzurteil

Der erste visuelle Pfad trägt E1 für eine endliche lokale Rezeptorfläche:

```text
synthetischer Drei-Kanal-Frame
-> lokales Kanalraster V2
-> unveränderliche visuelle Rezeptorlage
-> gesperrte visuelle MCM-Feldgrenze
```

Ort und technischer Quellkanal bleiben erhalten. Rohpixel, Bewegung,
Objektrollen und Zeitgeschichte überschreiten die Grenze nicht.

## 2. Implementierte Referenz

Jede Rasterzelle trägt unabhängig den Mittelwert ihrer drei technischen
Quellkanäle, skaliert auf `0..1`.

Die Pflichtprüfungen verwenden kleine 8-x-6-Frames mit einem 4-x-3-Raster.
Dadurch besitzt die Fläche 36 lokale Träger und jede erwartete Wirkung kann
exakt von Hand lokalisiert werden.

Zusätzlich wurde der offene 1.920-x-1.080-Kandidat geprüft:

```text
Raster:       12 x 8
Quellkanäle:  3
Träger:       288
```

Diese Geometrie ist noch keine ausgewählte visuelle Anatomie.

## 3. Null- und Lokalitätsbefunde

- Ein vollständig schwarzer gültiger Frame erzeugt 36 exakte Nullwerte und
  `active_zero`.
- Ein einzelner aktiver Quellkanal in einer Zelle verändert genau einen lokalen
  Träger.
- Keine Wirkung breitet sich auf Nachbarzellen oder andere Quellkanäle aus.
- Vertauschte technische Quellkanäle bleiben verschiedene Rezeptorlagen.

## 4. Gegen globale Bildbaselines

Zwei Frames mit derselben globalen Kanalmenge, aber Kontakt an verschiedenen
Orten, kollidieren in der globalen Kanalmittelwert-Baseline V1.

V2 erhält die räumliche Lage und unterscheidet beide Zustände ohne
Objekterkennung oder Musterklasse.

Damit ist die lokale Verteilung funktional begründet. Eine zusätzliche
visuelle Feldkopplung ist dadurch nicht begründet.

## 5. Endlicher Pfad

Der Adapter:

- liest exakt die angeforderte Framezahl,
- erzeugt genau einen unveränderlichen Rezeptorzustand je Frame,
- erstellt nur Minima, Maxima, Mittelwerte, Zähler und Sequenzdigest,
- fordert nach Laufende keinen weiteren Frame an,
- verwirft einen zu kurzen Quelllauf ohne gültige Teilzusammenfassung,
- liefert mit und ohne Observer dieselbe Zusammenfassung.

Synthetische Testframes liegen ausschließlich in der kontrollierten
Testquelle. Rezeptorzustand und Zusammenfassung enthalten keine Rohbilder.

## 6. Tatsächlich gezeigt

- technische Frameform und Rastergeometrie sind explizit,
- lokale räumliche Verteilung bleibt erhalten,
- drei Quellkanäle bleiben getrennt,
- globale Bildmittelwerte sind als alleinige Repräsentation unzureichend,
- Nullkontakt und aktive lokale Kanalwirkung sind exakt unterscheidbar,
- Sequenzreihenfolge bleibt im technischen Digest unterscheidbar,
- die Grenze ist reproduzierbar und observerneutral.

## 7. Nicht gezeigt

- reale Kameraaufnahme,
- Bewegung, Richtung oder Kontrastgeschichte,
- visueller Nachhall,
- ein visuelles MCM-Feld,
- Kanten, Formen, Objekte, Personen oder Szenen,
- multimodale reale Feldkonstellation,
- organische Entwicklung oder Feldintelligenz.

## 8. Kritischer Einwand

V2 ist lediglich eine feste räumliche Mittelwertreduktion. Dieser Einwand ist
zutreffend. Die Fläche dient als transparente technische Rezeptorbaseline und
nicht als Wahrnehmungs- oder MCM-Mechanik.

## 9. Evidenz und Status

```text
endlicher synthetischer Videovertrag: E1
lokale Drei-Kanal-Rezeptorfläche:      E1
reale Kameraquelle:                    E0
visuelles MCM-Feld:                    E0
```

## 10. Bester nächster Schritt

Nach Verfügbarkeit der Kamera wird ein optionaler, explizit adressierter
Hardwareadapter gebaut. Sein erster Lauf bleibt kurz und passiv und endet an
dieser Rezeptorgrenze. Vorher wird weder Bewegung noch visueller Nachhall
ergänzt.
