# Methodik 024: Reale visuelle Startphasen-Reichweite

## 1. Anlass

Ein explorativer Ruhe-Lauf begann nach drei ausdrücklich verbrauchten
Startframes mit einer deutlich stärkeren lokalen Rezeptoränderung als in den
späteren Fenstern desselben Laufs. Nach 30 und 90 Startframes war dieser frühe
Abfall nicht in derselben Form sichtbar.

Bevor reale Feldphasen verglichen werden, muss deshalb geklärt werden, ob die
deklarierte technische Startphase den Kameraeingang ausreichend von der ersten
MCM-Wahrnehmung trennt.

## 2. Forschungsfrage

Reichen drei Startframes für eine stabile anschließende visuelle Ruhefolge aus,
oder trägt der erste Feldabschnitt noch technische Einschwingwirkung, die nach
30 beziehungsweise 90 Startframes wesentlich kleiner ist?

## 3. Unveränderte Kette

Jeder Zweig öffnet den Kameraadapter neu und verwendet:

```text
explizite Startframes
-> 30 reale Wahrnehmungsframes
-> lokales 12-x-8-x-3-Rezeptorraster
-> visuelle MCM-Neuronenschicht
-> unveränderte Rezeptorprojektion
-> passiver Observer
```

Der erste MCM-Frame bleibt als Initialisierungsframe ausgeschlossen. Es werden
keine Bilder gespeichert und keine Werte in das Feld zurückgegeben.

## 4. Vorregistrierte Zweige

```text
S3:  3 Startframes
S30: 30 Startframes
S90: 90 Startframes
```

Die Bestätigungsreihenfolge lautet `S90 -> S30 -> S3` und kehrt damit die
explorative Reihenfolge um.

## 5. Messung

Für jeden Zweig werden aus den 29 Frames nach der Initialisierung vier
observerseitige Größen gebildet:

- Mittel der ersten fünf Frames,
- Mittel von fünf Frames aus der Laufmitte,
- Mittel der letzten fünf Frames,
- Mittel aller 29 Frames.

Grundgröße ist ausschließlich:

```text
mittleres |aktueller Rezeptorkontakt - eigene Voraktivierung|
über alle 288 visuellen Neuronen
```

Es wird keine Stabilitätsschwelle in die Runtime eingebaut.

## 6. Entscheidung

Eine zu kurze Startphase ist gestützt, wenn S3 erneut einen ausgeprägten
Abfall vom ersten zum letzten Fünferfenster zeigt, während S30 und S90 von
Beginn an in der Größenordnung ihrer späteren Fenster liegen.

30 Startframes dürfen nur als technische Konfiguration für diesen Adapterpfad
übernommen werden, wenn S30 gegenüber S3 trägt und S90 keinen notwendigen
zusätzlichen Bereich erschließt.

Der Befund gilt nicht automatisch für andere Kameras, Treiber, Belichtungen
oder Lichtlagen.

## 7. Nicht freigegeben

- Bildnormalisierung,
- Rauschschwelle,
- automatische Belichtungsregel im MCM-Feld,
- visuelle Nachhallmechanik,
- Bewegungserkennung,
- Memory oder Semantik.

## 8. Evidenzgrenze

Maximal E2 für die technische Startphasengrenze des vorhandenen realen
Adapterpfads.

## 9. Bester nächster Schritt

Nach genau einer Wiederholung in umgekehrter Reihenfolge wird entschieden, ob
die reale Phasenmethodik künftig 30 explizite Startframes verlangt. Erst danach
wird ein kontrollierter visueller Veränderungslauf erneut zugelassen.
