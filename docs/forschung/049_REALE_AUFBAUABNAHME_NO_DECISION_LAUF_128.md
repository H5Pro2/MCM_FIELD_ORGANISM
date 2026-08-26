# Forschung 049: Reale Aufbauabnahme NO_DECISION (Lauf 128)

## Forschungsfrage und Auftrag

Kann der in Lauf 124 definierte physische Aufbau nach der direkten menschlichen
Startbestaetigung `AUFBAU BEREIT, KAMERA 0, ENTSCHEIDUNG BEREIT` durch genau
eine reale Rohbildvorschau angenommen oder verworfen werden?

Freigegeben war ausschliesslich die einmalige manuelle Aufbauabnahme. Eine
Bildanalyse, Bildspeicherung, Effektor-Praesentation, Rezeptorzustandserzeugung
oder Feldtransition war ausgeschlossen.

## Verwendete Quellen

- direkte menschliche Startbestaetigung im aktuellen Benutzereingang
- `docs/forschung/046_PHYSISCHER_FELD_WELT_FELD_AUFBAUVERTRAG_LAUF_124.md`
- `docs/forschung/048_REALE_AUFBAUABNAHME_NO_DECISION_LAUF_126.md`
- `tools/run_physical_setup_acceptance.py`

Externe Quellen und MINI_DIO wurden nicht verwendet.

## Verwendete Dateien und Schnittstellen

- `OpenCVVideoFrameSource`
- `CameraAcquisitionControls(True, True, True)`
- `VisualGridConfig()` mit angeforderten 1920 x 1080 und 30 fps
- `tools/run_physical_setup_acceptance.py --camera-device 0`

Es wurde nur Kameraindex `0` aufgerufen. Keine Kameraindexsuche, Effektor-,
Rezeptor- oder Feldschnittstelle wurde verwendet.

## Durchgefuehrte Schritte

1. Die direkte Startbestaetigung ausserhalb eines zitierten Agenten- oder
   Pruefertexts als erfuellt festgestellt.
2. Das freigegebene Werkzeug mit Kameraindex `0` genau einmal gestartet.
3. Genau 30 Startframes konsumiert und die drei angeforderten
   Akquisitionskontrollen gesetzt.
4. Die rohe Kameravorschau bis zur festen Grenze von 30 Sekunden angezeigt.
5. Keine Annahme- oder Ablehnungstaste empfangen.
6. Nach dem Timeout keinen Wiederholungslauf gestartet.

## Messergebnisse und Gegenbaselines

```text
Ausfuehrungen:                         1
Kameraindex:                           0
Startframes:                           30
Vorschauframes:                        579
Vorschaugrenze:                        30.0 s
Gemeldete Geometrie:                   1920 x 1080
Gemeldete Rate:                        30.00003000003 fps
Beobachtete Startrate:                 29.47114937307774 fps
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
- Der Timeout wurde nicht als Annahme oder Ablehnung umgedeutet.
- Es wurde weder ein anderer Kameraindex noch eine Wiederholung verwendet.
- E0, E1, B0 und B1 wurden nicht ausgefuehrt.

## Beobachtetes Ergebnis

Kamera `0` lieferte die angeforderte Geometrie. Die Schnittstelle meldete die
drei angeforderten Automatik-Sperren als akzeptiert. Innerhalb der begrenzten
Vorschau wurden 579 Frames angezeigt, aber weder `A` noch `R` oder `Esc` als
Entscheidung empfangen. Das Ergebnis lautet deshalb:

```text
NO_DECISION
```

## Technische Interpretation

Die direkte Startbedingung war fuer Lauf 128 erfuellt und der reale
Kamerapfad war technisch ausfuehrbar. `NO_DECISION` sagt nicht aus, ob die
zehn manuellen Sichtkriterien erfuellt oder verletzt sind. Der Prozesscode
ungleich null folgt bei diesem Werkzeug aus jeder Entscheidung ausser
`HUMAN_ACCEPTED`; er ist hier kein Kamera- oder Laufabbruch.

Der statische Ausgabewert `run_number: 125` bezeichnet die
Entstehungsprovenienz des Werkzeugs. Der hier dokumentierte reale Lauf ist
Lauf 128.

## Grenzen und nicht gepruefte Annahmen

- Sichttrennung, Reflexionsfreiheit, passive Zielflaechen und optisches
  Uebersprechen wurden nicht menschlich bestaetigt oder verworfen.
- Die gemeldeten Control-Sperren sind keine unabhaengige optische Messung.
- E0, E1, B0 und B1 bleiben durch den Aufbauvertrag gesperrt.
- Es wurde keine Feld-Welt-Feld-Wirkung beobachtet.
- MCM-Feldzeit, Memory, Organisation, Semantik und Topologie wurden weder
  untersucht noch nachgewiesen.
- Eine Zielabweichung ist nicht erkennbar.

## Konkrete Schlussfolgerung

Lauf 128 endet nach genau einer freigegebenen Ausfuehrung mit `NO_DECISION`.
Die Kameraanschlussstelle war verwendbar, aber die manuelle Aufbauabnahme ist
nicht bestanden. Daraus folgt keine Freigabe fuer E0, E1, B0 oder B1.

## Naechster begrenzter Forschungslauf

Der Benutzer sollte entscheiden, ob eine weitere, neu begruendete
einmalige Aufbauabnahme freigegeben wird. Sie darf erst nach erneuter direkter
menschlicher Startbestaetigung erfolgen und nicht als automatische
Ergebnissuche wiederholt werden.

Aus dem jetzigen Stand kann die Forschung erst nach einem separat
beobachteten `HUMAN_ACCEPTED` zur Vorregistrierung der physischen
Kausalkontrollen E0, E1, B0 und B1 weitergehen. Bis dahin bleiben
Feld-Welt-Feld-, Memory- und Organisationsaussagen ausgeschlossen.

## Tatsaechlich verwendete Quellen

- direkter aktueller Benutzereingang
- `docs/forschung/046_PHYSISCHER_FELD_WELT_FELD_AUFBAUVERTRAG_LAUF_124.md`
- `docs/forschung/048_REALE_AUFBAUABNAHME_NO_DECISION_LAUF_126.md`
- `tools/run_physical_setup_acceptance.py`
- Konsolenausgabe der einmaligen Lauf-128-Ausfuehrung
