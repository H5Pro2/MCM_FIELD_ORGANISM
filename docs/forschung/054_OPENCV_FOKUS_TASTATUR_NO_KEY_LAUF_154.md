# Lauf 154: Interaktive OpenCV-Tastaturprobe ohne empfangene Taste

## Forschungsfrage und Auftrag

Empfängt das neutrale OpenCV-Prüffenster im realen Desktop-Kontext während einer einmaligen, auf 15 Sekunden begrenzten Ausführung eine der Tasten `A`, `R` oder `Esc`?

Freigegeben war ausschließlich die interaktive Ausführung von `tools/run_opencv_keyboard_focus_probe.py`. Kamera, Effektor, Rezeptor und Feldruntime waren ausgeschlossen.

## Verwendete Quellen

- Prüferfreigabe im aktuellen Übergabeeingang zu Lauf 153
- direkte Benutzerhinweise zur derzeit ungeeigneten Kamerasituation und zur Bevorzugung künstlicher Audio-/Video-Testwelten
- `tools/run_opencv_keyboard_focus_probe.py`
- `docs/forschung/053_OPENCV_FOKUS_TASTATUR_PRUEFWERKZEUG_LAUF_153.md`

Externe Webquellen und Medien wurden nicht verwendet.

## Verwendete Dateien und Schnittstellen

- Runner: `tools/run_opencv_keyboard_focus_probe.py`
- Python: `.venv/Scripts/python.exe`
- OpenCV: `namedWindow`, `imshow`, `waitKey`, `getWindowProperty`, `destroyAllWindows`

Es wurde keine Kamera geöffnet und keine Projektlaufzeit importiert.

## Durchgeführte Schritte

1. Den freigegebenen Runner genau einmal ohne zusätzliche Parameter gestartet.
2. Das neutrale OpenCV-Fenster bis zum festgelegten Zeitlimit betrieben.
3. Den maschinenlesbaren Runner-Ausgang übernommen.
4. Den Versuch nicht wiederholt.

## Messergebnisse und Gegenbaselines

Ausführung:

```powershell
.\.venv\Scripts\python.exe tools\run_opencv_keyboard_focus_probe.py
```

Ergebnis:

- Ereignis: `NO_KEY_RECEIVED`
- Zeitlimit: `15.0 s`
- gemessene Laufzeit: `15.015257699997164 s`
- `waitKey`-Iterationen: `832`
- Kamera geöffnet: nein
- Bildanalyse: nein
- Bilddatei geschrieben: nein
- Aufbauentscheidung erzeugt: nein
- Effektor präsentiert: nein
- Rezeptorzustand erzeugt: nein
- Feldsnapshot geladen: nein
- Feldtransition ausgeführt: nein

Gegenbaseline aus Lauf 153: Das synthetische Mapping aller erlaubten Tasten war korrekt und die fokussierten Vertragsprüfungen bestanden. Lauf 154 zeigt dagegen, dass während dieser konkreten realen Desktop-Ausführung keine erlaubte Taste empfangen wurde.

## Grenzen und nicht geprüfte Annahmen

`NO_KEY_RECEIVED` unterscheidet nicht zwischen fehlender Tasteneingabe, fehlendem Fensterfokus, nicht sichtbarem Fenster oder einem anderen Desktop-Eingabeproblem. Sichtbarkeit und Betriebssystemfokus wurden nicht unabhängig beobachtet. Der Lauf belegt deshalb keinen Defekt von `cv2.waitKey()`.

Die Kameraumgebung war laut direkter Benutzerangabe aktuell dunkel und unbewegt; sie war für Lauf 154 ohne Bedeutung, weil keine Kamera geöffnet wurde. Reale Kamera- und Aufbauversuche wurden nicht ausgeführt. `E0`, `E1`, `B0` und `B1` bleiben gesperrt.

Es folgen keine Aussagen zu Feld-Welt-Feld-Wirkung, MCM-Feldzeit, Memory, Organisation, Semantik oder Topologie. Keine Zielabweichung ist erkennbar.

## Konkrete Schlussfolgerung

Die synthetisch bestätigte Key-Mapping-Logik führte in der einmaligen realen Desktop-Probe zu keinem empfangenen Schlüsselereignis. Die offene Ursache bleibt auf Fensterdarstellung, Fokus, menschliche Eingabe oder Desktop-Ereignisübertragung begrenzt. Daraus darf keine Aufbauentscheidung abgeleitet werden.

## Vorschlag für den nächsten begrenzten Forschungslauf

Bis geeignete reale Bedingungen vorliegen, sollte die Forschung mit vorhandenen kontrollierten künstlichen Audio-/Video-Testwelten fortgesetzt werden. Der nächste Lauf sollte zunächst nur den Bestand der synthetischen Audio-/Video-Runner, ihre Eingangsverträge und die bereits dokumentierte asynchrone Forschungslücke inventarisieren. Erst danach sollte ein einzelner parametrisierter Lauf zu unterschiedlichen Audio-/Videoraten, Zeitteilungen und Ereignisreihenfolgen vorregistriert werden. Es ist keine neue Feld-, Memory- oder Bedeutungsmechanik erforderlich.
