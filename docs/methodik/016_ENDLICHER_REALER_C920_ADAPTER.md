# Methodik 016: Endlicher realer C920-Adapter

## 1. Zweck

Die reale Kamera wird als ausdrücklich adressierte, endliche Quelle an die
bereits geprüfte visuelle Rezeptorfläche angeschlossen:

```text
explizites Kameragerät
-> deklarierte technische Startphase
-> endliche Rohframefolge
-> lokale visuelle Rezeptorfläche
-> unveränderliche Rezeptorzustände
-> Stopp vor dem visuellen MCM-Feld
```

## 2. Explizite Gerätewahl

Der Adapter akzeptiert ausschließlich einen angegebenen nichtnegativen
Geräteindex. Er sucht keine Kamera und wählt kein Windows-Standardgerät.

Breite, Höhe und Bildrate stammen aus `VisualGridConfig`. Beim Öffnen werden
diese Werte angefordert und nach der Startphase als tatsächlich gemeldete
Geräteeinstellungen ausgewiesen.

## 3. Sichtbare Startphase

Die Anzahl technischer Startframes muss beim Erzeugen der Quelle ausdrücklich
angegeben werden. Vor `prepare()` kann kein Rezeptorframe gelesen werden.

`prepare()`:

- liest exakt die deklarierte Anzahl,
- prüft Form und Datentyp jedes Startframes,
- zählt exakte Nullframes und aktive Frames getrennt,
- gibt keine Startframes an die Rezeptorfläche weiter,
- speichert oder veröffentlicht keine Rohbilder.

Die Startphase ist damit weder verstecktes Verwerfen noch Wahrnehmung.

## 4. Endliche Aufnahme

Nach erfolgreicher Startphase liefert jeder Aufruf genau einen vollständigen
Frame. `capture_finite_video()` begrenzt die Anzahl und erzeugt je Frame genau
einen lokalen Rezeptorzustand.

Der Kamerakontext gibt das Gerät auch bei Fehlern wieder frei. Eine erneute
Startphase innerhalb desselben Kontexts ist verboten.

## 5. Rohdatengrenze

Rohframes existieren nur während des Lesens und der lokalen Rasterreduktion.
Startzusammenfassung, Rezeptorzustand und Laufzusammenfassung enthalten keine:

- Bilder oder Pixel,
- Frameausschnitte,
- Dateipfade,
- Objekte, Personen oder Szenen,
- Bedeutung oder Bezeichnung.

## 6. Pflichtkontrollen

1. Fehlende OpenCV-Abhängigkeit blockiert vor Geräteöffnung.
2. Ungültiger Geräteindex oder Startumfang wird abgelehnt.
3. Angeforderte Geometrie und Bildrate werden explizit gesetzt.
4. Lesen vor `prepare()` ist unmöglich.
5. Startframes und Aufnahmeframes besitzen getrennte Zähler.
6. Exakter Nullframe bleibt als technischer Startbefund sichtbar.
7. Ungültige Frameform scheitert an ihrer genauen Position.
8. Endliche Rezeptoraufnahme beginnt erst nach der Startphase.
9. Zusammenfassungen enthalten keine Rohbildrollen.
10. Das Gerät wird bei normalem Ende und bei Fehler freigegeben.

## 7. Evidenzgrenze

Maximal E1 für Hardwarezugriff und Startvertrag sowie E2 für den kontrollierten
realen Pfad bis zur bereits unabhängig geprüften Rezeptorgrenze.

Nicht freigegeben sind visuelle Felddynamik, Bewegung, Objekte, Semantik oder
multimodale reale Musterbildung.
