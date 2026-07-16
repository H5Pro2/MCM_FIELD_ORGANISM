# Befund 028: Reale visuelle Startphasen-Grenze

## Kurzurteil

Zwei Läufe in entgegengesetzter Zweigreihenfolge tragen denselben technischen
Befund:

> Drei Startframes reichen für einen unmittelbar anschließenden realen
> visuellen Feldvergleich nicht aus. Nach 30 Startframes beginnt die lokale
> Rezeptoränderung bereits im späteren Ruhebereich. 90 Startframes erschließen
> unter den geprüften Bedingungen keinen notwendigen zusätzlichen Bereich.

Dieser Befund betrifft ausschließlich die technische Startgrenze des
vorhandenen Kameraadapterpfads. Er ist keine visuelle Feldmechanik.

## Prüfaufbau

Jeder Zweig öffnete den Adapter neu und verbrauchte ausdrücklich entweder 3,
30 oder 90 Startframes. Anschließend wurden 30 reale Frames durch das lokale
12-x-8-x-3-Rezeptorraster und die unveränderte visuelle
Rezeptorprojektions-Baseline geführt.

Der erste MCM-Frame blieb als Initialisierung ausgeschlossen. Aus den übrigen
29 Frames wurden Mittelwerte der ersten, mittleren und letzten fünf Frames
sowie des vollständigen Bereichs gebildet.

Es wurden keine Bilder gespeichert.

## Explorative Reihenfolge: 3 -> 30 -> 90

| Startframes | erste 5 | mittlere 5 | letzte 5 | alle 29 |
|---:|---:|---:|---:|---:|
| 3 | 0,001802938 | 0,001092115 | 0,000517306 | 0,001607905 |
| 30 | 0,000452163 | 0,000449637 | 0,000473937 | 0,000459740 |
| 90 | 0,000430668 | 0,000457538 | 0,000521419 | 0,000488671 |

Bei drei Startframes war das erste Fünferfenster etwa `3,49`-mal so groß wie
das letzte. Bei 30 und 90 Startframes lagen die Fenster bereits von Beginn an
in derselben Größenordnung.

## Bestätigungsreihenfolge: 90 -> 30 -> 3

| Startframes | erste 5 | mittlere 5 | letzte 5 | alle 29 |
|---:|---:|---:|---:|---:|
| 90 | 0,000492747 | 0,000458152 | 0,000475157 | 0,000463993 |
| 30 | 0,000468360 | 0,000488719 | 0,000475363 | 0,000478135 |
| 3 | 0,001473012 | 0,001782672 | 0,000472225 | 0,001404064 |

Auch bei umgekehrter Reihenfolge lag das erste Fünferfenster nach drei
Startframes etwa `3,12`-mal über dem letzten. Nach 30 und 90 Startframes blieb
dieser ausgeprägte Abfall aus.

## Interpretation

Der frühe Unterschied nach drei Startframes gehört zur technischen
Einschwingphase des realen Kameraeingangs. Er darf nicht als natürliche
Feldänderung, visuelle Unruhe oder Reaktion des MCM-Feldes ausgegeben werden.

30 Startframes trennen diese Einschwingwirkung unter den geprüften Bedingungen
ausreichend von der ersten Wahrnehmungsphase. Der 90-Frame-Zweig zeigt keinen
Hinweis, dass für den nächsten eng begrenzten Phasenversuch noch mehr
Startframes erforderlich wären.

## Architekturfolge

Für reale visuelle Feld- und Phasenvergleiche dieses Adapterpfads gilt künftig:

```text
explizite Startphase: mindestens 30 Frames
Startframes:          keine Wahrnehmung
erster MCM-Frame:     sichtbare Initialisierung, nicht auswerten
ab zweitem MCM-Frame: auswertbarer Feldverlauf
```

Die allgemeine Adapterschnittstelle bleibt offen und verlangt weiterhin eine
explizite Anzahl. Es wird kein geräteübergreifender versteckter Standardwert
eingebaut.

## Nicht gezeigt

- Die Grenze gilt nicht automatisch für andere Geräte, Treiber oder
  Lichtverhältnisse.
- 30 Startframes sind keine biologische Konstante.
- Die Startphase normalisiert keine Bilder.
- Es wurde keine Bewegung und keine visuelle Invarianz geprüft.
- Es wurde kein visueller Nachhall oder Memory freigegeben.

## Evidenz

```text
3 Frames als unzureichende unmittelbare Startphase: E2
30 Frames für den nächsten realen Phasenlauf:       E2
Notwendigkeit von mehr als 30 Frames:               nicht gestützt
visuelle Feldfunktion:                              E0
```

## Bester nächster Schritt

Der nächste reale Ruhe-Veränderung-Ruhe-Lauf verwendet ausdrücklich 30
Startframes und wertet aus demselben Lauf sowohl globale Mittel als auch lokale
Phasenprofile aus. Erst dann wird beurteilt, ob eine kontrollierte lokale
Veränderung bereits in der vorhandenen Feldhülle getragen wird.
