# Forschung 048: Reale Aufbauabnahme NO_DECISION (Lauf 126)

## Forschungsfrage und Auftrag

Kann der in Lauf 124 definierte physische Aufbau durch die einmalige reale
Ausfuehrung des in Lauf 125 vorbereiteten Rohbildwerkzeugs menschlich
angenommen oder verworfen werden?

Freigegeben war genau eine Ausfuehrung. Bildspeicherung, automatische
Bildanalyse, Feldsnapshot, Effektor-Praesentation, Rezeptorauswertung,
Feldtransition und Wiederholung zur Ergebnissuche waren ausgeschlossen.

## Verwendete Quellen

- `docs/forschung/046_PHYSISCHER_FELD_WELT_FELD_AUFBAUVERTRAG_LAUF_124.md`
- `docs/forschung/047_REALE_PHYSISCHE_AUFBAUABNAHME_LAUF_125.md`
- `docs/architektur/026_GEMEINSAMER_AUDIO_VIDEO_FELDKONTAKT.md`
- `tools/run_physical_setup_acceptance.py`
- `mcm_field_organism/live_video_adapter.py`

Externe Quellen und MINI_DIO wurden nicht verwendet.

## Verwendete Dateien und Schnittstellen

- `OpenCVVideoFrameSource`
- `CameraAcquisitionControls(True, True, True)`
- `VisualGridConfig()` mit 1920 x 1080 und angeforderten 30 fps
- `tools/run_physical_setup_acceptance.py --camera-device 0`

Kameraindex `0` war der einzige im Projektbestand konkret dokumentierte
operative Kameraaufruf. Es wurde keine Indexsuche ausgefuehrt.

## Durchgefuehrte Schritte

1. Kameraindex `0` explizit festgelegt.
2. Das vorhandene Werkzeug genau einmal gestartet.
3. Genau 30 Startframes konsumiert.
4. Automatische Belichtung, Weissabgleich und Fokus gesperrt.
5. Die rohe Kameravorschau bis zum festen Zeitlimit angezeigt.
6. Keine menschliche Annahme- oder Ablehnungstaste empfangen.
7. Nach dem Timeout keine Wiederholung gestartet.

## Messergebnisse und Gegenbaselines

```text
Ausfuehrungen:                         1
Kameraindex:                           0
Startframes:                           30
Vorschauframes:                        361
Vorschaugrenze:                        30.0 s
Gemeldete Geometrie:                   1920 x 1080
Gemeldete Rate:                        30.00003000003 fps
Beobachtete Startrate:                 15.162385488550932 fps
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
- Timeout wurde nicht als Annahme umgedeutet.
- Es wurde kein zweiter Kameraindex und kein Wiederholungslauf verwendet.

## Beobachtetes Ergebnis

Die Kamera `0` konnte mit der geforderten Geometrie geoeffnet werden. Alle
drei angeforderten Automatik-Sperren wurden von der Schnittstelle akzeptiert.
Das Werkzeug zeigte 361 rohe Vorschauframes. Bis zum festen Zeitlimit wurde
weder `A` noch `R` oder `Esc` als Entscheidung empfangen.

Das zulaessige Ergebnis ist daher:

```text
NO_DECISION
```

## Technische Interpretation

Der reale Kamerapfad und die drei angeforderten Kontrollsperren waren fuer
diese einmalige Vorschau technisch ausfuehrbar. `NO_DECISION` enthaelt keine
Aussage darueber, ob der physische Aufbau die zehn Sichtkriterien erfuellt.
Insbesondere darf die geoeffnete Kamera nicht als bestandene Aufbauabnahme
interpretiert werden.

Das Werkzeug gibt statisch `workflow_run: 125` aus. Dieser Wert bezeichnet
die Entstehungsprovenienz des Werkzeugs und ist kein Messbeleg fuer die
Laufnummer. Der hier dokumentierte freigegebene Hardwarelauf ist Lauf 126.

## Grenzen und nicht gepruefte Annahmen

- Sichttrennung, Reflexionsfreiheit, passive Zielflaechen und optisches
  Uebersprechen wurden nicht menschlich bestaetigt oder verworfen.
- Die Differenz zwischen gemeldeter Rate und beobachteter Startrate wurde
  nicht weiter untersucht.
- Die Rueckgabewerte der Control-Sperren belegen keine unabhaengige optische
  Stabilitaetsmessung.
- E0, E1, B0 und B1 wurden nicht ausgefuehrt.
- Es wurde keine Feld-Welt-Feld-Wirkung beobachtet.
- Quellenstuetze, Organismuszeit, MCM-Feldzeit, Memory, Organisation,
  Semantik und Topologie sind nicht nachgewiesen.
- Eine Zielabweichung ist nicht erkennbar.

## Konkrete Schlussfolgerung

Lauf 126 endet mit `NO_DECISION`. Die Kameraanschlussstelle war technisch
ausfuehrbar, aber der physische Aufbau ist nicht angenommen. Der
Kausalkontrolllauf mit E0, E1, B0 und B1 bleibt gesperrt.

## Naechster begrenzter Forschungslauf

Ein weiterer Hardwarelauf darf nicht aus Lauf 126 selbst abgeleitet werden,
weil Wiederholung zur Ergebnissuche ausgeschlossen war. Zunaechst sollte der
Forschungspruefer entscheiden, ob eine neue, separat begruendete einmalige
menschliche Aufbauabnahme freigegeben wird oder der physische Zweig bis zu
einer ausdruecklichen menschlichen Aufbauvorbereitung ruht.

Erst ein spaeteres, separat freigegebenes `HUMAN_ACCEPTED` darf eine
Vorregistrierung fuer E0, E1, B0 und B1 begruenden.

## Tatsaechlich verwendete Quellen

- `docs/forschung/046_PHYSISCHER_FELD_WELT_FELD_AUFBAUVERTRAG_LAUF_124.md`
- `docs/forschung/047_REALE_PHYSISCHE_AUFBAUABNAHME_LAUF_125.md`
- `docs/architektur/026_GEMEINSAMER_AUDIO_VIDEO_FELDKONTAKT.md`
- `tools/run_physical_setup_acceptance.py`
- `mcm_field_organism/live_video_adapter.py`
- Konsolenausgabe der einmaligen Lauf-126-Ausfuehrung
