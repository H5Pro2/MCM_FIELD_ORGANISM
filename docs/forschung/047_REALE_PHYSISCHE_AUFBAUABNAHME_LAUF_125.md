# Forschung 047: Reale physische Aufbauabnahme (Lauf 125)

## Forschungsfrage und Auftrag

Kann der in Lauf 124 vorregistrierte physische Aufbau mit zwei getrennten
Lichtkanaelen, zwei passiven matten Zielflaechen und einer Kamera, die nur
diese Zielflaechen sieht, real und menschlich abgenommen werden?

Freigegeben sind nur eine rohe Kameravorschau und menschliche Sichtpruefung.
Feldsnapshot, Effektor-Praesentation, Rezeptorauswertung, automatische
Bildanalyse und geschlossener Feldlauf bleiben ausgeschlossen.

## Verwendete Dateien und Schnittstellen

- `docs/forschung/046_PHYSISCHER_FELD_WELT_FELD_AUFBAUVERTRAG_LAUF_124.md`
- `docs/architektur/104_TECHNISCHER_VERTRAG_VISUELLE_MCM_EFFEKTORFLAECHE.md`
- `docs/architektur/105_KAUSALVERTRAG_GETRENNTE_VISUELLE_WELTWIRKUNG.md`
- `mcm_field_organism/live_video_adapter.py`
- `mcm_field_organism/finite_video_path.py` (`VisualGridConfig` nur als Geometrievertrag)
- `tools/run_physical_setup_acceptance.py`
- `tests/test_physical_setup_acceptance_tool.py`

## Durchgefuehrte Schritte

1. Den Bestand auf ein reines Kamera-Vorschauwerkzeug geprueft. Ein solches
   Werkzeug war nicht vorhanden.
2. Ein isoliertes, auf 30 Sekunden und einen expliziten Kameraindex begrenztes
   Vorschauwerkzeug ergaenzt.
3. Das Werkzeug nutzt `OpenCVVideoFrameSource`, konsumiert exakt 30
   Startframes und verlangt danach Sperren fuer Belichtung, Weissabgleich und
   Fokus.
4. Es zeigt ausschliesslich rohe Kameraframes. Es speichert und analysiert
   kein Bild und erzeugt weder Rezeptor- noch Feldzustand.
5. Die Entscheidung ist nur durch `A` (menschlich angenommen) oder `R`/Esc
   (menschlich verworfen) moeglich. Zeitablauf ist keine Annahme.
6. Werkzeuggrenzen und Entscheidungstasten synthetisch getestet.

## Messergebnisse und Gegenbaselines

Synthetische Werkzeugpruefung:

```text
Neue Werkzeug-Vertragstests:      4
Kameragrenztests:                 10
Fokussierte Tests insgesamt:      14 bestanden
Automatische Bildanalyse:          0
Bilddateien geschrieben:           0
Feldsnapshots geladen:             0
Effektor-Praesentationen:          0
Rezeptorzustaende:                 0
Feldtransitionen:                  0
```

Reale Aufbauabnahme:

```text
Physischer Aufbau bestaetigt:      NEIN
Kameravorschau real ausgefuehrt:   NEIN
Menschliche Entscheidung:          AUSSTEHEND
```

Die Nichtausfuehrung ist die Gegenbaseline gegen eine aus Code oder
Dokumentation erfundene physische Abnahme.

## Beobachtetes Ergebnis

Die technische Anschlussstelle fuer eine menschliche Rohbildpruefung ist nun
vorhanden und synthetisch begrenzt. Es wurde kein physischer Aufbau gezeigt
oder bestaetigt. Deshalb ist Lauf 125 nicht bestanden und auch nicht negativ;
die reale Beobachtung steht aus.

## Technische Interpretation

Code kann die Kamera geometrisch konfigurieren, die Startphase begrenzen und
Automatiken zu sperren versuchen. Er kann nicht beweisen, dass Abschirmungen,
matte Zielflaechen und Reflexionsfreiheit real vorliegen. Diese Entscheidung
bleibt beim Menschen und darf nicht automatisch ersetzt werden.

## Grenzen und nicht gepruefte Annahmen

- Der reale Aufbau und die verfuegbaren Materialien wurden nicht gesehen.
- Der korrekte Kameraindex wurde nicht bestaetigt.
- Kameraoeffnung und Sperren der drei Automatiken wurden nicht an Hardware
  ausgefuehrt.
- Sichttrennung, Uebersprechen, Reflexionen und Umgebungslichtstabilitaet
  wurden nicht real beurteilt.
- E0, E1, B0 und B1 wurden nicht ausgefuehrt.
- Keine Feld-Welt-Feld-Wirkung wurde beobachtet.
- Quellenstuetze, Organismuszeit, MCM-Feldzeit, Memory, Organisation,
  Semantik und Topologie sind nicht nachgewiesen.
- Eine Zielabweichung ist nicht erkennbar.

## Konkrete Schlussfolgerung

Die fehlende Vorschau-Anschlussstelle ist eng geschlossen. Eine reale
Aufbauabnahme kann jedoch ohne aufgebauten optischen Pfad und menschliche
Sichtentscheidung nicht behauptet werden. Der Kausalkontrolllauf bleibt
gesperrt.

## Naechster begrenzter Forschungslauf

Lauf 126 sollte nur die einmalige reale Ausfuehrung des jetzt vorhandenen
Abnahmewerkzeugs an einem fertig aufgebauten Pfad enthalten. Vor dem Start
muss der Kameraindex explizit feststehen. Das Ergebnis darf nur
`HUMAN_ACCEPTED`, `HUMAN_REJECTED` oder `NO_DECISION` sein.

Nur `HUMAN_ACCEPTED` darf danach eine getrennte Vorregistrierung fuer einen
Kausalkontrolllauf mit E0, E1, B0 und B1 begruenden. Bei Ablehnung oder
fehlender Entscheidung darf kein Kausallauf folgen.

## Tatsaechlich verwendete Quellen

- `docs/forschung/046_PHYSISCHER_FELD_WELT_FELD_AUFBAUVERTRAG_LAUF_124.md`
- `docs/architektur/104_TECHNISCHER_VERTRAG_VISUELLE_MCM_EFFEKTORFLAECHE.md`
- `docs/architektur/105_KAUSALVERTRAG_GETRENNTE_VISUELLE_WELTWIRKUNG.md`
- `mcm_field_organism/live_video_adapter.py`
- `mcm_field_organism/finite_video_path.py`
- `tests/test_live_video_adapter.py`

MINI_DIO und externe MCM-Quellen wurden nicht verwendet.
