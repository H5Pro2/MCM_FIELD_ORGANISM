# Forschung 073: Reale physische Aufbauabnahme ohne Entscheidung (Lauf 175)

## Forschungsfrage und Auftrag

Nach direkter Bereitschaft des Benutzers wurde geprueft, ob der reale
optische Aufbau innerhalb der begrenzten Rohkamera-Vorschau bewusst mit `A`
angenommen oder mit `R` beziehungsweise Esc verworfen wird.

## Verwendete Quellen

- direkte Benutzernachricht `ich bin vor der kamera`
- aktueller Uebergabeeingang
- `tools/run_physical_setup_acceptance.py`
- `docs/forschung/072_REALE_PHYSISCHE_AUFBAUABNAHME_NO_DECISION_LAUF_174.md`

Externe Quellen und Projektdatenbanken wurden nicht verwendet.

## Verwendete Dateien und Schnittstellen

- `tools/run_physical_setup_acceptance.py`
- `OpenCVVideoFrameSource`
- `CameraAcquisitionControls`
- Kameraindex `0`

## Durchgefuehrte Schritte

1. Die direkte menschliche Bereitschaft entgegengenommen.
2. Den unveraenderten Abnahmerunner direkt gestartet.
3. 30 Startframes konsumiert und die vorhandenen Kamerasperren angewendet.
4. Die rohe Vorschau fuer maximal 30 Sekunden angezeigt.
5. Die maschinenlesbare Runnerentscheidung ausgewertet.

## Messergebnisse und Gegenbaseline

```text
Entscheidung:                     NO_DECISION
Vorschauframes:                           566
Vorschaugrenze:                        30.0 s
Beobachtete Kamerarate:          29.3348 Hz
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

Die Gegenbaseline bleibt der Zeitablauf ohne gueltige Taste. Er ist weder
Annahme noch Ablehnung.

## Einordnung

**Beobachtet:** Kamera `0` lieferte reale Rohframes. Innerhalb der Vorschau
wurde weder `A` noch `R` oder Esc registriert.

**Technische Interpretation:** Die reale Kameraanschlussstelle funktioniert,
aber die geforderte menschliche Aufbauentscheidung wurde nicht erfasst.

**Hypothese:** Keine. Aus Anwesenheit vor der Kamera oder aus dem Bildinhalt
wird keine Aufbauentscheidung abgeleitet.

**Offene Frage:** Kann der Benutzer das OpenCV-Bildfenster fokussieren und
dort innerhalb der Laufzeit eine gueltige Entscheidungstaste ausloesen?

## Grenzen und nicht gepruefte Annahmen

Das Rohbild wurde nicht analysiert oder gespeichert. Sichttrennung,
Reflexionsfreiheit, passive Zielflaechen und der Ausschluss des Effektors sind
nicht bestaetigt. Kein Effektor- oder Feldlauf wurde ausgefuehrt. Memory,
Bedeutung, Organisation und Topologie wurden nicht untersucht. Eine
Zielabweichung liegt nicht vor.

## Konkrete Schlussfolgerung

Lauf 175 endet mit `NO_DECISION`. Die direkte Bereitschaft des Benutzers ist
keine Ersatzentscheidung. Orchestratorentwicklung und Kausalarme bleiben
gesperrt.

## Naechster begrenzter Forschungslauf

Vor einer weiteren Wiederholung sollte nur die Bedienbarkeit geklaert werden:
Das OpenCV-Bildfenster muss sichtbar und fokussierbar sein, und die Taste muss
dort waehrend der 30 Sekunden gedrueckt werden. Danach darf derselbe Runner
einmal erneut ausgefuehrt werden. Nur ein maschinenlesbares `HUMAN_ACCEPTED`
gibt die eng begrenzte Orchestratorentwicklung frei.
