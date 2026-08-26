# Forschung 072: Reale physische Aufbauabnahme ohne Entscheidung (Lauf 174)

## Forschungsfrage und Auftrag

Geprueft wurde, ob der reale optische Aufbau ueber die vorhandene rohe
Kameravorschau menschlich angenommen oder verworfen wird. Nur die bewusste
Taste `A`, `R` oder Esc durfte eine Entscheidung erzeugen.

## Verwendete Quellen

- aktueller Uebergabeeingang
- `tools/run_physical_setup_acceptance.py`
- `docs/forschung/047_REALE_PHYSISCHE_AUFBAUABNAHME_LAUF_125.md`
- `docs/forschung/071_PHYSISCHER_PROZESSPFAD_TECHNISCHE_VORABNAHME_LAUF_173.md`

Externe Quellen und Projektdatenbanken wurden nicht verwendet.

## Verwendete Dateien und Schnittstellen

- `tools/run_physical_setup_acceptance.py`
- `OpenCVVideoFrameSource`
- `CameraAcquisitionControls`
- Kameraindex `0`

## Durchgefuehrte Schritte

1. Den unveraenderten Abnahmerunner direkt gestartet.
2. 30 Startframes zur Kameravorbereitung konsumiert.
3. Belichtung, Weissabgleich und Fokus ueber den vorhandenen Adapter gesperrt.
4. Die rohe Vorschau fuer maximal 30 Sekunden angezeigt.
5. Das vom Runner ausgegebene Ergebnis unmittelbar ausgewertet.

## Messergebnisse und Gegenbaseline

```text
Entscheidung:                     NO_DECISION
Vorschauframes:                           573
Vorschaugrenze:                        30.0 s
Beobachtete Kamerarate:          29.7280 Hz
Gemeldete Kamerarate:            30.0000 Hz
Aufloesung:                     1920 x 1080
Akzeptierte Sperren: exposure, white_balance, focus
Automatische Bildanalyse:             nein
Bilddatei geschrieben:                nein
Feldsnapshot geladen:                 nein
Effektor praesentiert:                nein
Rezeptorzustand erzeugt:              nein
Feldfortsetzung ausgefuehrt:           nein
```

Die Gegenbaseline ist die fehlende menschliche Entscheidung. Zeitablauf darf
nicht als Annahme oder Ablehnung interpretiert werden.

## Einordnung

**Beobachtet:** Kamera `0` lieferte waehrend der begrenzten Vorschau rohe
Frames. Der Runner registrierte weder `A` noch `R` oder Esc.

**Technische Interpretation:** Kameraoeffnung und Vorschaupfad funktionieren.
Der physische Aufbauvertrag wurde jedoch nicht menschlich bestaetigt.

**Hypothese:** Keine. Aus `NO_DECISION` wird keine Aussage ueber die reale
Geometrie abgeleitet.

**Offene Frage:** Werden alle zehn sichtbaren Aufbaukriterien vom Menschen
bewusst angenommen oder wird mindestens eines verworfen?

## Grenzen und nicht gepruefte Annahmen

Der Agent hat das Rohbild nicht analysiert. Sichttrennung, Reflexionsfreiheit,
passive Zielflaechen und Ausschluss des Effektors bleiben unbestaetigt. Es
wurde kein physischer Kausalarm ausgefuehrt. Memory, Bedeutung, Organisation
und Topologie wurden nicht untersucht. Eine Zielabweichung liegt nicht vor.

## Konkrete Schlussfolgerung

Lauf 174 endet mit `NO_DECISION`. Die Kameraanschlussstelle ist real
funktionsfaehig, aber der physische Aufbau ist nicht abgenommen. Ein
Closed-Loop-Ablaufkoordinator und jeder Feld-Welt-Feld-Kausallauf bleiben gesperrt.

## Naechster begrenzter Forschungslauf

Der naechste Lauf darf nur dieselbe menschliche Abnahme wiederholen, wenn eine
Person innerhalb des 30-Sekunden-Fensters bewusst entscheidet. `A` ist nur
bei Erfuellung aller zehn Kriterien zulaessig; andernfalls ist `R` oder Esc zu
verwenden. Erst ein auslesbares `HUMAN_ACCEPTED` darf die eng begrenzte
Ablaufkoordinatorentwicklung freigeben.
