# Forschung 050: Reale Aufbauabnahme NO_DECISION (Lauf 130)

## Forschungsfrage und Auftrag

Kann der physische Aufbau nach der direkten menschlichen Startbestaetigung
`AUFBAU BEREIT, KAMERA 0, ENTSCHEIDUNG BEREIT` durch genau eine begrenzte
Rohbildvorschau angenommen oder verworfen werden?

Freigegeben war ausschliesslich die einmalige manuelle Aufbauabnahme. Eine
Bildanalyse, Bildspeicherung, Effektor-Praesentation, Rezeptorzustandserzeugung
oder Feldtransition war ausgeschlossen.

## Verwendete Quellen

- direkte menschliche Startbestaetigung im aktuellen Benutzereingang
- `docs/forschung/046_PHYSISCHER_FELD_WELT_FELD_AUFBAUVERTRAG_LAUF_124.md`
- `docs/forschung/049_REALE_AUFBAUABNAHME_NO_DECISION_LAUF_128.md`
- `tools/run_physical_setup_acceptance.py`

Externe Quellen und MINI_DIO wurden nicht verwendet.

## Verwendete Dateien und Schnittstellen

- `OpenCVVideoFrameSource`
- `CameraAcquisitionControls(True, True, True)`
- `VisualGridConfig()` mit angeforderten 1920 x 1080 und 30 fps
- `tools/run_physical_setup_acceptance.py --camera-device 0`

Nur Kameraindex `0` wurde aufgerufen. Keine Effektor-, Rezeptor- oder
Feldschnittstelle wurde verwendet.

## Durchgefuehrte Schritte

1. Die direkte menschliche Startbestaetigung als erfuellt festgestellt.
2. Das vorhandene Werkzeug mit Kameraindex `0` genau einmal gestartet.
3. Genau 30 Startframes konsumiert und Belichtung, Weissabgleich und Fokus
   ueber die vorhandene Schnittstelle gesperrt.
4. Die rohe Kameravorschau bis zur festen Grenze von 30 Sekunden angezeigt.
5. Keine Annahme- oder Ablehnungstaste empfangen.
6. Nach dem Timeout keinen Wiederholungslauf gestartet.

## Messergebnisse und Gegenbaselines

```text
Ausfuehrungen:                         1
Kameraindex:                           0
Startframes:                           30
Vorschauframes:                        517
Vorschaugrenze:                        30.0 s
Gemeldete Geometrie:                   1920 x 1080
Gemeldete Rate:                        30.00003000003 fps
Beobachtete Startrate:                 29.70749589680439 fps
Akzeptierte manuelle Controls:         exposure, white_balance, focus
Menschliche Entscheidung:              NO_DECISION
Bildanalyse ausgefuehrt:               False
Bilddatei geschrieben:                 False
Feldsnapshot geladen:                  False
Effektor praesentiert:                 False
Rezeptorzustand erzeugt:               False
Feldtransition ausgefuehrt:            False
```

Gegenbaselines:

- `HUMAN_ACCEPTED` wurde nicht beobachtet.
- `HUMAN_REJECTED` wurde nicht beobachtet.
- Der Timeout wurde nicht als Entscheidung umgedeutet.
- Kein anderer Kameraindex und keine Wiederholung wurden verwendet.
- E0, E1, B0 und B1 wurden nicht ausgefuehrt.

## Beobachtetes Ergebnis

Kamera `0` lieferte die angeforderte Geometrie. Die Schnittstelle meldete die
drei angeforderten Kontrollsperren als akzeptiert. In der Vorschau wurden 517
Frames angezeigt, aber weder `A` noch `R` oder `Esc` registriert. Das Ergebnis
lautet daher:

```text
NO_DECISION
```

## Technische Interpretation

Der reale Kamerapfad war technisch ausfuehrbar. `NO_DECISION` belegt weder die
Erfuellung noch die Verletzung der zehn manuellen Sichtkriterien. Der
nicht-null Rueckgabecode ist bei diesem Werkzeug die vorgesehene Folge jeder
Entscheidung ausser `HUMAN_ACCEPTED` und kein Kameraabbruch.

Der statische Ausgabewert `workflow_run: 125` bezeichnet die
Entstehungsprovenienz des Werkzeugs. Der hier dokumentierte reale Lauf ist
Lauf 130.

## Grenzen und nicht gepruefte Annahmen

- Sichttrennung, Reflexionsfreiheit, passive Zielflaechen und optisches
  Uebersprechen wurden nicht menschlich bestaetigt oder verworfen.
- Die gemeldeten Control-Sperren ersetzen keine optische Stabilitaetsmessung.
- E0, E1, B0 und B1 bleiben gesperrt.
- Es wurde keine Feld-Welt-Feld-Wirkung beobachtet.
- MCM-Feldzeit, Memory, Organisation, Semantik und Topologie wurden weder
  untersucht noch nachgewiesen.
- Eine Zielabweichung ist nicht erkennbar.

## Konkrete Schlussfolgerung

Lauf 130 endet nach genau einer freigegebenen Ausfuehrung mit `NO_DECISION`.
Die Kameraanschlussstelle war verwendbar, die manuelle Aufbauabnahme ist aber
nicht bestanden. Es folgt keine Freigabe fuer E0, E1, B0 oder B1.

## Naechster begrenzter Forschungslauf

Der Forschungspruefer sollte entscheiden, ob eine weitere neu begruendete
einmalige Aufbauabnahme erforderlich ist oder der physische Zweig bis zur
sicheren Bedienbarkeit des Vorschaufensters ruht. Eine weitere Ausfuehrung
bedarf erneut einer direkten menschlichen Startbestaetigung und darf nicht
automatisch zur Ergebnissuche wiederholt werden.

Erst ein separat beobachtetes `HUMAN_ACCEPTED` darf die Vorregistrierung der
physischen Kausalkontrollen E0, E1, B0 und B1 begruenden. Bis dahin bleiben
Feld-Welt-Feld-, Memory- und Organisationsaussagen ausgeschlossen.

## Tatsaechlich verwendete Quellen

- direkter aktueller Benutzereingang
- `docs/forschung/046_PHYSISCHER_FELD_WELT_FELD_AUFBAUVERTRAG_LAUF_124.md`
- `docs/forschung/049_REALE_AUFBAUABNAHME_NO_DECISION_LAUF_128.md`
- `tools/run_physical_setup_acceptance.py`
- Konsolenausgabe der einmaligen Lauf-130-Ausfuehrung
