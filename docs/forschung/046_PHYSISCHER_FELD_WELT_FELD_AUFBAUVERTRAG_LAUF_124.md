# Forschung 046: Physischer Feld-Welt-Feld-Aufbauvertrag (Lauf 124)

## Forschungsfrage und Auftrag

Reichen die vorhandenen Projektmechanismen aus, um einen spaeteren physischen
Pfad

```text
MCM-Feld
-> visueller Effektor
-> zwei getrennte optische Kanaele
-> zwei passive Zielflaechen
-> reale Kamera
-> visueller Rezeptor
-> MCM-Feld
```

ohne interne Frame-Weitergabe und ohne Vorprogrammierung einer Feldwirkung
aufzubauen?

Freigegeben war ausschliesslich eine Schnittstellen- und Aufbaupruefung. Ein
reales Praesentationsfenster, eine Kameraaufnahme, ein Rezeptorlauf oder ein
geschlossener Feldlauf waren nicht freigegeben.

## Verwendete Dateien und Schnittstellen

- `docs/architektur/104_TECHNISCHER_VERTRAG_VISUELLE_MCM_EFFEKTORFLAECHE.md`
- `docs/architektur/105_KAUSALVERTRAG_GETRENNTE_VISUELLE_WELTWIRKUNG.md`
- `mcm_field_organism/visual_mcm_effector_surface.py`
- `mcm_field_organism/visual_mcm_effector_presenter.py`
- `mcm_field_organism/independent_visual_target_presenter.py`
- `mcm_field_organism/live_video_adapter.py`
- `mcm_field_organism/finite_video_path.py`
- `tools/present_visual_mcm_effector_frame.py`
- `tools/present_independent_visual_targets.py`
- `tests/test_visual_mcm_effector_surface.py`
- `tests/test_visual_mcm_effector_presenter.py`
- `tests/test_independent_visual_target_presenter.py`
- `tests/test_live_video_adapter.py`

## Durchgefuehrte Schritte

1. Die zulaessige Feldquelle und affine Effektorabbildung aus Architektur 104
   gegen den vorhandenen Code geprueft.
2. Die digitale Auftrennung jedes Graupaares in ein linkes und rechtes
   Zielraster untersucht.
3. Die manuellen Praesentationswerkzeuge auf Kamera-, Rezeptor- und
   Feldanbindung geprueft.
4. Den realen OpenCV-Kamerapfad auf explizite Geraetewahl, Startphase,
   Aufnahmeparameter und fehlende interne Effektorverbindung untersucht.
5. Die vorhandenen digitalen Effektor-, Zielpraesentations- und
   Kameragrenztests reproduziert.
6. Die noch ausschliesslich physisch und menschlich pruefbaren
   Aufbaubedingungen und Stopplinien vorregistriert.

Es wurde keine Projektmechanik geaendert. Kein Bildschirmfenster und keine
Kamera wurden geoeffnet.

## Beobachteter technischer Bestand

### Digitale Effektorquelle

`project_visual_mcm_effector_surface` akzeptiert genau einen abgeschlossenen
`SharedMCMFieldSnapshot`. Pro Feldort wird unveraendert abgebildet:

```text
I_left  = 0.50 + 0.25 * activation
I_right = 0.50 - 0.25 * activation
```

Die Intensitaeten bleiben in `0.25..0.75`. Es gibt keine Schwelle, Auswahl,
Semantik, Zufallsquelle oder Rueckschreibung.

### Getrennte digitale Zielkanaele

`prepare_independent_visual_target_plan` ordnet alle geraden Spalten dem
linken und alle ungeraden Spalten dem rechten Raster zu. Geometrie und
Grauintensitaeten bleiben erhalten. Der Plan erzwingt:

```text
camera_connected = False
writes_back      = False
stateful         = False
adaptive         = False
random_source    = False
```

`present_independent_visual_target_plan` zeigt beide Raster statisch mit einem
festen Zwischenraum. Die physische optische Fuehrung bleibt ausdruecklich
ausserhalb der Software.

### Reale Kameragrenze

`OpenCVVideoFrameSource` verlangt einen expliziten Kameraindex und eine
explizite `VisualGridConfig`. Die Kamera besitzt eine sichtbare Startphase und
separate Akquisitionskontrollen. Der Kamerapfad importiert keinen
Effektorrahmen und erhaelt keine Feldaktivierung oder Effektorprovenienz.

Der nachgelagerte `LocalChannelGridReceptor` verarbeitet Kamera-Pixel. Die
vorhandene Schnittstelle beweist jedoch nicht, was physisch vor der Kamera
steht.

## Messergebnisse und Gegenbaselines

Fokussierte synthetische Vertragssuite:

```text
Effektoroberflaeche
+ Effektor-Praesentation
+ getrennte Zielpraesentation
+ Live-Kameragrenze
= 35 Tests bestanden
```

Hardware- und Aussenweltmessungen:

```text
Praesentationsfenster gestartet: 0
Kamera geoeffnet:                0
Kameraframes erfasst:            0
Rezeptorzustaende erzeugt:       0
Feldtransitionen ausgefuehrt:    0
```

Vorhandene Gegenbaselines fuer einen spaeteren realen Lauf:

- **E0:** neutraler Feldsnapshot erzeugt zwei identische Mittelgrauraster.
- **E1:** nichtneutraler Snapshot erzeugt die feste affine Kanalpaarung.
- **B0:** beide realen Lichtwege werden physisch blockiert.
- **B1:** beide Effektorkanaele bleiben technisch neutral.
- **R0:** identische Wiederholung bei unveraendertem Aufbau.
- **P0/O0:** Provenienz und Observer duerfen die optische Wirkung nicht
  veraendern.

Diese Baselines sind in Lauf 124 nur spezifiziert, nicht physisch ausgefuehrt.

## Vorregistrierter physischer Aufbau

Ein spaeterer Aufbau ist nur zulaessig, wenn ein Mensch vor jedem Lauf alle
folgenden Punkte bestaetigt:

1. Der Bildschirm oder eine andere Effektorlichtquelle liegt vollstaendig
   ausserhalb des Kamerabildes.
2. Linker und rechter Kanal sind durch lichtundurchlaessige Trennwaende
   gegeneinander abgeschirmt.
3. Jeder Kanal beleuchtet genau eine matte, passive und unbewegte Zielflaeche.
4. Zwischen beiden Zielflaechen besteht ein sichtbarer raeumlicher Abstand.
5. Die Kamera sieht beide Zielflaechen vollstaendig.
6. Die Kamera sieht weder Bildschirm, Kanaloeffnung noch direkte oder
   spiegelnde Effektorreflexion.
7. Kameraposition, Fokus, Belichtung und Weissabgleich bleiben nach der
   Startphase fest.
8. Umgebungslicht, Zielflaechenposition und Kanalgeometrie bleiben innerhalb
   eines Vergleichs unveraendert.
9. Die Zuordnung linker Kanal zu linker Zielflaeche und rechter Kanal zu
   rechter Zielflaeche ist ausserhalb des Organismus eindeutig dokumentiert.
10. Ein aeusserer Sofort-Stopp und die anschliessende neutrale
    Mittelgrauausgabe sind erreichbar.

Die menschliche Aufbauentscheidung bleibt Observerprovenienz. Sie darf weder
in Kamera-Pixel noch in Rezeptor- oder Feldzustand codiert werden.

## Harte Stopplinien

Der spaetere Aufbau wird nicht fuer einen Feldlauf freigegeben, wenn:

- Bildschirm, Lichtquelle, Kanaloeffnung oder Spiegelung im Kamerabild liegt;
- beide Lichtkanaele sich sichtbar auf derselben Zielflaeche vermischen;
- eine Zielflaeche aktiv, berechnend, leuchtend oder zustandsspeichernd ist;
- Kameraautomatik nach der Startphase nicht festgesetzt werden kann;
- direkte Bildschirmaufnahme, Screenshot, virtuelle Kamera oder internes
  Frame-Sharing verwendet wird;
- eine automatische Bildanalyse die Aufbauentscheidung ersetzt;
- adaptive Helligkeit, adaptives Warten oder Ergebniswiederholung benoetigt
  wird;
- die physische Herkunft eines Kameraframes nicht eindeutig ist.

## Technische Interpretation

Die vorhandene Software reicht fuer die digitale Effektorprojektion, die
statische Trennung in zwei Zielkanaele und eine spaetere regulare
Kamera-Rezeptoraufnahme aus. Es fehlt keine neue Feld- oder Rezeptormechanik.

Die entscheidende Anschlussstelle ist physisch, nicht digital: Abschirmung,
passive Zielflaechen, Sichttrennung und Reflexionsfreiheit koennen im Workspace
nicht behauptet oder synthetisch ersetzt werden. Sie benoetigen einen realen
Aufbau und menschliche Sichtpruefung.

## Grenzen und nicht gepruefte Annahmen

- Es wurde nicht geprueft, ob Bildschirm, Abschirmmaterial und zwei matte
  Zielflaechen physisch vorhanden sind.
- Die reale Kameraposition und ihr Sichtfeld wurden nicht geprueft.
- Fokus-, Belichtungs- und Weissabgleichs-Lock wurden nicht an Hardware
  bestaetigt.
- Optisches Uebersprechen, Reflexionen und Umgebungslichtstabilitaet wurden
  nicht gemessen.
- Es wurde keine Feld-Welt-Feld-Wirkung beobachtet.
- Eine spaetere Kameradifferenz waere zunaechst nur optische Kausalwirkung,
  nicht Memory oder Feldorganisation.
- Quellenstuetze, Organismuszeit und MCM-Feldzeit sind nicht nachgewiesen.
- Memory, Organisation, Semantik und Topologie wurden nicht untersucht oder
  nachgewiesen.
- Eine Zielabweichung ist nicht erkennbar.

## Konkrete Schlussfolgerung

Lauf 124 bestaetigt, dass die vorhandene Projektmechanik den digitalen Teil
des getrennten Feld-Welt-Feld-Pfads bereits traegt. Keine technische
Erweiterung ist fuer die reine Aufbauphase erforderlich.

Der reale Kausalpfad ist noch nicht hergestellt. Die verbleibende Grenze ist
ein physischer, menschlich zu bestaetigender Aufbau mit zwei abgeschirmten
Lichtkanaelen, zwei passiven matten Zielflaechen und einer Kamera, die nur
diese Zielflaechen sieht.

## Naechster begrenzter Forschungslauf

Lauf 125 sollte ausschliesslich die reale physische Aufbauabnahme ausfuehren:

- Effektor ausserhalb des Kamerabilds platzieren;
- zwei abgeschirmte Lichtkanaele und zwei passive matte Zielflaechen
  herstellen;
- Kamera auf beide Zielflaechen ausrichten und Automatik nach der Startphase
  sperren;
- ein reines Kamera-Vorschaubild menschlich auf Sichttrennung, Reflexion und
  vollstaendige Zielabdeckung pruefen;
- noch keinen Feldsnapshot praesentieren, keinen Rezeptor auswerten und keinen
  geschlossenen Feldlauf starten.

Nur eine bestandene manuelle Aufbauabnahme darf einen spaeteren separaten
Kausalkontrolllauf mit E0, E1, B0 und B1 begruenden.

## Tatsaechlich verwendete Quellen

- `docs/architektur/104_TECHNISCHER_VERTRAG_VISUELLE_MCM_EFFEKTORFLAECHE.md`
- `docs/architektur/105_KAUSALVERTRAG_GETRENNTE_VISUELLE_WELTWIRKUNG.md`
- `mcm_field_organism/visual_mcm_effector_surface.py`
- `mcm_field_organism/visual_mcm_effector_presenter.py`
- `mcm_field_organism/independent_visual_target_presenter.py`
- `mcm_field_organism/live_video_adapter.py`
- `mcm_field_organism/finite_video_path.py`
- `tools/present_visual_mcm_effector_frame.py`
- `tools/present_independent_visual_targets.py`
- die vier fokussierten Testmodule des Effektor-, Presenter- und Kamerapfads

MINI_DIO und externe MCM-Mechaniken wurden nicht verwendet.
