# Lauf 140: Reale Aufbauabnahme ohne Entscheidung

## Forschungsfrage und Auftrag

Nach der direkten menschlichen Startbestätigung war einmalig zu prüfen, ob der physische Aufbau im laufenden OpenCV-Vorschaufenster menschlich angenommen oder abgelehnt wird.

## Verwendete Quellen

- direkte Benutzereingabe `AUFBAU BEREIT, KAMERA 0, ENTSCHEIDUNG BEREIT`
- `docs/forschung/046_PHYSISCHER_FELD_WELT_FELD_AUFBAUVERTRAG_LAUF_124.md`
- `docs/forschung/050_REALE_AUFBAUABNAHME_NO_DECISION_LAUF_130.md`
- `tools/run_physical_setup_acceptance.py`

## Verwendete Dateien und Schnittstellen

- Runner: `tools/run_physical_setup_acceptance.py`
- Python: `.venv/Scripts/python.exe`
- Kamera: Gerät `0`
- OpenCV-Vorschaufenster und `cv2.waitKey()` für `A`, `R` oder `Esc`

Effektor, Rezeptor und MCM-Feld wurden nicht ausgeführt.

## Durchgeführte Schritte

1. Die direkte Startbestätigung als außerhalb eines Übergabetextes vorliegend geprüft.
2. Den freigegebenen Runner einmal mit Kamera `0` gestartet.
3. 30 Startframes konsumiert und das Vorschaufenster für 30 Sekunden betrieben.
4. Den Runner-Ausgang ohne Wiederholung ausgewertet.

## Messergebnisse und Gegenbaselines

- Entscheidung: `NO_DECISION`
- Prozess-Exitcode: `1` (Runner signalisiert nicht bestandene Abnahme)
- Startframes: `30`
- Vorschauframes: `564`
- Vorschauzeitlimit: `30.0 s`
- gemeldete Auflösung: `1920 x 1080`
- gemeldete Rate: `30.00003000003 fps`
- beobachtete Startrate: `29.637869186903096 fps`
- `HUMAN_ACCEPTED`: nicht beobachtet
- `HUMAN_REJECTED`: nicht beobachtet
- Bildanalyse: nein
- Bilddatei geschrieben: nein
- Feldsnapshot geladen: nein
- Effektor präsentiert: nein
- Rezeptorzustand erzeugt: nein
- Feldtransition ausgeführt: nein

Gegenbaseline ist Lauf 130, ebenfalls `NO_DECISION`, dort mit 517 Vorschauframes und beobachteten 29.7075 fps. Beide Läufe belegen nur funktionierende Kameravorschau ohne registrierte menschliche Entscheidung.

## Grenzen und nicht geprüfte Annahmen

Nicht technisch geprüft wurden Fensterfokus, Sichttrennung, Reflexionsfreiheit, passive Zielflächen, optisches Übersprechen und die externe Links-Rechts-Provenienz. Aus `NO_DECISION` folgt weder Annahme noch Ablehnung des Aufbaus.

Feld-Welt-Feld-Wirkung, MCM-Feldzeit, Memory, Organisation, Semantik und Topologie wurden nicht untersucht und sind nicht nachgewiesen.

## Konkrete Schlussfolgerung

Die reale Kameraaufnahme und das Vorschaufenster liefen, aber innerhalb des Zeitfensters wurde keine gültige Entscheidung registriert. Die Aufbauabnahme ist nicht bestanden. `E0`, `E1`, `B0` und `B1` bleiben gesperrt. Eine Zielabweichung ist nicht erkennbar.

## Vorschlag für den nächsten begrenzten Forschungslauf

Kein weiterer Versuch soll automatisch erfolgen. Der Forschungsprüfer sollte Lauf 140 zunächst bewerten. Nur bei erneuter ausdrücklicher Freigabe und einer neuen direkten Startbestätigung wäre ein weiterer einzelner Abnahmeversuch vertretbar; dabei muss das OpenCV-Fenster fokussiert sein und die Entscheidung innerhalb von 30 Sekunden dort erfolgen.
