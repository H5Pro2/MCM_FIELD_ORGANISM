# Lauf 170: Zweiphasige Rezeptor-Feld-Gegenbaseline

## Forschungsfrage und Auftrag

Geprueft wurde, ob die in Lauf 169 beobachteten Audio-Transportverluste
verschwinden, wenn reale Kamera- und Mikrofonerfassung zeitlich von der
unveraenderten Feld- und Gegenbaselineberechnung getrennt werden.

Verglichen wurden zwei aufeinanderfolgende 30-Sekunden-Arme mit einem
Einsekunden-Audiopuffer:

1. bestehende Online-Erfassung mit gleichzeitiger Feldberechnung
2. Erfassung ausschliesslich reduzierter, zeitgestempelter Rezeptorzustaende,
   Schliessen beider Geraete und erst danach Feld- und Gegenbaselineberechnung

Rohbilder und Audiosamples durften nicht behalten werden. Memory, Bedeutung,
Organisation und Topologie waren ausgeschlossen.

## Verwendete Quellen

Tatsaechlich verwendet wurden:

- der aktuelle freigegebene Uebergabeeingang
- `AGENTS.md`
- `docs/forschung/066_AUDIO_OVERFLOW_LOKALISATION_LAUF_168.md`
- `docs/forschung/067_AUDIO_TRANSPORTKAPAZITAET_LAUF_169.md`
- `mcm_field_organism/live_audio_adapter.py`
- `mcm_field_organism/live_audio_video_field.py`
- `mcm_field_organism/receptor_time_alignment.py`
- `mcm_field_organism/audio_video_neutral_field_runtime.py`
- `mcm_field_organism/shared_mcm_field.py`
- `tools/run_live_audio_overflow_localization.py`
- vorhandene Adapter-, Runtime-, Zeit- und Architekturtests

Externe Quellen und projektweite Wissensdatenbanken wurden nicht verwendet.

## Verwendete Dateien und Schnittstellen

Neu erstellt wurden:

- `tools/run_live_two_phase_field_probe.py`
- `tests/test_run_live_two_phase_field_probe.py`
- dieser Bericht

Verwendet wurden die bestehenden Schnittstellen
`_capture_live_receptor_windows`, `_advance_captured_audio_video_sequences`,
`_observe_live_field_window`, `SharedMCMFieldSnapshot` und
`restore_shared_mcm_field`. Projektive Feldmechanik, Rezeptoren,
Transportstandard und Feldparameter wurden nicht veraendert.

Die zweiphasige Ausfuehrung behaelt bis zur Feldfortsetzung ausschliesslich
`ReceptorTimeSequence`-Objekte mit bereits reduzierten Rezeptorkontakten und
Organismuszeit. Es wird keine lokale Rohsensordatei erzeugt.

Verwendet wurden OpenCV-Kameraindex 0 und sounddevice-Audioindex 1.

## Durchgefuehrte Schritte

1. Ein Runner fuer Online- und zweiphasigen Arm wurde auf vorhandenen privaten
   Forschungsfunktionen aufgebaut.
2. Vollstaendigkeit der Modalitaetsfenster und Fortschritt aller Frame- und
   Fensterzeiten wurden explizit ausgewertet.
3. Der bestehende 30-Sekunden-Onlinearm wurde mit einem Einsekundenpuffer
   ausgefuehrt.
4. Kamera und Mikrofon erfassten danach 30 gemeinsame Fenster ohne
   Feldrechnung. Beide Geraetekontexte wurden geschlossen.
5. Dieselben reduzierten Fenster wurden anschliessend durch primaere Feld- und
   exakte Gegenbaselineberechnung fortgesetzt.
6. Gezielte Runner-, Adapter- und Runtimevertraege wurden getestet.

## Messergebnisse und Gegenbaselines

```text
Arm                         Audio  Video  Treiber  Transport  Max. Puffer
Online mit Feld              2990    375        0        348      100/100
Zweiphasig                   2997    548        0          0        5/100
```

```text
Arm                         Fenster  Unvollst.  Zeitfehler  Baselinefehler
Online mit Feld                  30          0           0               0
Zweiphasig                       30          0           0               0
```

```text
Arm                         Primaer Mittel  Baseline Mittel  Gesamt Mittel
Online mit Feld                  0.3924 s          0.3946 s        0.7870 s
Zweiphasige Feldfortsetzung      0.3409 s          0.3376 s        0.6785 s
```

```text
Zweiphasige Gesamterfassung inklusive Kameravorbereitung: 39.9423 s
Zweiphasige nachgelagerte Feldfortsetzung:                 28.7598 s
Checkpoints je Arm:                                              29
Rohsensorpayload gespeichert:                                 nein
```

Die etwa zehn Sekunden oberhalb der 30 Erfassungsfenster enthalten die
Kameravorbereitung und sind keine vergroesserten Rezeptorfenster.

## Einordnung

**Beobachtet:** Der Onlinearm erreichte die volle Transportkapazitaet und
verlor 348 Audioframes. Die zweiphasige Erfassung erreichte maximal 5 von 100
Pufferplaetzen und verlor weder im Treiber noch im Transport Frames. Alle 30
zweiphasigen Fenster enthielten beide Modalitaeten, alle gemessenen Intervalle
und Fenster schritten fort und die exakte Feldgegenbaseline blieb identisch.

**Technische Interpretation:** Die reale Rezeptorerfassung ist unter derselben
begrenzten Transportkapazitaet verlustfrei, wenn waehrenddessen keine Feld- und
Kontrollrechnung konkurriert. Das stuetzt die Lokalisation auf gemeinsame
Rechen- beziehungsweise Scheduling-Last und begruendet eine technische
Entkopplung des Onlinepfads.

**Hypothese:** Eine begrenzte Worker- oder Prozessgrenze, die nur reduzierte
Rezeptorzustaende uebergibt, kann die Onlineerfassung ebenfalls verlustfrei
halten, sofern der Verbraucher den langfristigen Zustrom traegt oder
Rueckstand explizit sichtbar macht.

**Offene Frage:** Die zweiphasige Gegenbaseline weist noch nicht nach, dass
Erfassung und Feldfortsetzung gleichzeitig und dauerhaft verlustfrei in
getrennten Workern laufen.

## Grenzen und nicht gepruefte Annahmen

Die Arme liefen nacheinander. Kameraautomatik, Weltinhalt und Betriebssystemlast
waren nicht kontrolliert; insbesondere die Videozahlen sind keine praezise
Leistungskennlinie. Die nachgelagerte Feldrechnung hat keinen Echtzeitdruck.

Die gespeicherten In-Memory-Rezeptorzustaende sind technische
Versuchsuebergaben und kein MCM-Memory. Es wurden keine Memory-, Bedeutungs-,
Organisations- oder Topologieeigenschaften untersucht. Eine Zielabweichung
liegt nicht vor.

## Konkrete Schlussfolgerung

Die zweiphasige Gegenbaseline erfuellt alle vorab benannten Kriterien: keine
Treiber- oder Transportverluste, vollstaendige Modalitaetsfenster,
fortschreitende Zeit und eine unveraenderte exakte Feldgegenbaseline.

Damit ist nachgewiesen, dass die bestehende reduzierte Erfassung ohne
gleichzeitige Feldlast innerhalb des Einsekundenpuffers funktioniert. Eine
weitere Puffervergroesserung ist nicht erforderlich. Nicht nachgewiesen ist
eine stabile Onlinekopplung; dafuer ist eine begrenzte technische
Worker-Entkopplung erforderlich.

## Vorschlag fuer den naechsten begrenzten Forschungslauf

Lauf 171 sollte ausschliesslich die Erfassung und bestehende Feldfortsetzung
ueber eine begrenzte Worker- oder Prozessgrenze entkoppeln. Uebergeben werden
duerfen nur die vorhandenen reduzierten `ReceptorTimeSequence`-Fenster mit
Organismuszeit; Feldgleichungen, Rezeptoren und Einsekunden-Audiopuffer bleiben
unveraendert.

Ein 30-Sekunden-Onlinearm ist gegen den bestehenden gleichprozessigen Arm zu
vergleichen. Zu messen sind Treiber- und Transportverlust, Eingangs- und
Workerwarteschlangenbelegung, Ende-zu-Ende-Latenz, vollstaendige Fenster,
Zeitfortschritt und exakte Feldgegenbaseline. Bei wachsendem Rueckstand oder
Verlust darf weder der Puffer weiter vergroessert noch eine Memoryvariable
eingefuehrt werden; dann ist die Feldrechnung selbst als Echtzeitgrenze zu
behandeln.
