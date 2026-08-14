# Lauf 152: Reale Aufbauabnahme ohne Entscheidung

## Forschungsfrage und Auftrag

Nach der direkten menschlichen Startbestätigung war einmalig zu prüfen, ob der physische Aufbau im laufenden OpenCV-Vorschaufenster menschlich angenommen oder abgelehnt wird. Der übergebene Abschlussdatensatz des ausgeführten Einzelversuchs war gegen den bestehenden Aufbauvertrag und die Runner-Schnittstelle abzugleichen und zu dokumentieren.

## Verwendete Quellen

- aktueller Übergabeeingang mit Abschlussdatensatz
- `docs/forschung/046_PHYSISCHER_FELD_WELT_FELD_AUFBAUVERTRAG_LAUF_124.md`
- `docs/forschung/050_REALE_AUFBAUABNAHME_NO_DECISION_LAUF_130.md`
- `docs/forschung/051_REALE_AUFBAUABNAHME_NO_DECISION_LAUF_140.md`
- `tools/run_physical_setup_acceptance.py`

## Verwendete Dateien und Schnittstellen

- Runner: `tools/run_physical_setup_acceptance.py`
- Python: `.venv/Scripts/python.exe`
- Kamera: Gerät `0`
- OpenCV-Vorschaufenster und `cv2.waitKey()` für `A`, `R` oder `Esc`

Effektor, Rezeptor und MCM-Feld wurden nicht ausgeführt. Im Dokumentationsschritt wurde kein weiterer Kamera- oder Runnerlauf gestartet.

## Durchgeführte Schritte

1. Die übergebene direkte Startbestätigung und den Abschlussdatensatz übernommen.
2. Den gemeldeten parameterlosen Vorabbruch als Abbruch vor Kamerazugriff eingeordnet; er zählt nicht als realer Abnahmeversuch.
3. Den genau einmal mit `--camera-device 0` ausgeführten Abnahmeversuch gegen die Runner-Vertragslogik geprüft.
4. Das Ergebnis ohne Wiederholung dokumentiert.

## Messergebnisse und Gegenbaselines

- Entscheidung: `NO_DECISION`
- Startframes: `30`
- Vorschauframes: `293`
- Vorschauzeitlimit: `30.0 s`
- gemeldete Auflösung: `1920 x 1080`
- gemeldete Rate: `30.00003000003 fps`
- beobachtete Startrate: `15.886788771250458 fps`
- akzeptierte manuelle Steuerungen: `exposure`, `white_balance`, `focus`
- `HUMAN_ACCEPTED`: nicht beobachtet
- `HUMAN_REJECTED`: nicht beobachtet
- Bildanalyse: nein
- Bilddatei geschrieben: nein
- Feldsnapshot geladen: nein
- Effektor präsentiert: nein
- Rezeptorzustand erzeugt: nein
- Feldtransition ausgeführt: nein

Gegenbaselines:

- Lauf 130: `NO_DECISION`, 517 Vorschauframes, beobachtete Startrate etwa `29.7075 fps`.
- Lauf 140: `NO_DECISION`, 564 Vorschauframes, beobachtete Startrate `29.637869186903096 fps`.

Lauf 152 liefert erneut keine menschliche Entscheidung. Die deutlich niedrigere beobachtete Startrate und geringere Vorschauframezahl sind technische Unterschiede, belegen für sich aber weder deren Ursache noch eine Änderung der Aufbauqualität.

## Grenzen und nicht geprüfte Annahmen

Der Abschlussdatensatz wurde aus dem aktuellen Übergabeeingang übernommen; der reale Lauf wurde im Dokumentationsschritt nicht wiederholt. Nicht technisch nachgewiesen wurden Fensterfokus, Tastaturempfang, Sichttrennung, Reflexionsfreiheit, passive Zielflächen, optisches Übersprechen und externe Links-Rechts-Provenienz. Aus `NO_DECISION` folgt weder Annahme noch Ablehnung des Aufbaus.

Feld-Welt-Feld-Wirkung, MCM-Feldzeit, Memory, Organisation, Semantik und Topologie wurden nicht untersucht und sind nicht nachgewiesen. Es gab keine Browser- oder Medienverarbeitung. Eine Zielabweichung ist nicht erkennbar.

## Konkrete Schlussfolgerung

Die Kamera-Vorschau wurde laut übergebenem Messdatensatz ausgeführt, aber innerhalb des Zeitfensters wurde keine gültige Entscheidung registriert. Die Aufbauabnahme ist nicht bestanden. `E0`, `E1`, `B0` und `B1` bleiben gesperrt.

## Vorschlag für den nächsten begrenzten Forschungslauf

Kein automatischer Wiederholungsversuch. Der Forschungsprüfer sollte Lauf 152 zunächst bewerten. Falls ein weiterer Einzelversuch fachlich freigegeben wird, sollte vor dessen Start die Bedienbarkeit des fokussierten OpenCV-Fensters außerhalb eines Kameralaufs kontrolliert werden, ohne Bildanalyse, Bildspeicherung oder Feldkomponenten zu ergänzen. Ein realer Wiederholungsversuch benötigt anschließend erneut eine eigenständige direkte menschliche Startbestätigung.
