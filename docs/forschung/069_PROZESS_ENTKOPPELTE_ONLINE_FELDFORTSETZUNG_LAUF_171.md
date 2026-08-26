# Lauf 171: Prozess-entkoppelte Online-Feldfortsetzung

## Forschungsfrage und Auftrag

Geprueft wurde, ob eine begrenzte Prozessgrenze zwischen realer
Audio-Video-Rezeptorerfassung und unveraenderter Feldfortsetzung die in den
Laeufen 167 bis 170 lokalisierten Audio-Transportverluste im 30-Sekunden-
Onlinebetrieb beseitigt.

Verglichen wurden:

1. bestehende gleichprozessige Online-Erfassung mit Feld und exakter Baseline
2. Online-Erfassung im Hauptprozess und Feld plus exakte Baseline in einem
   separaten `spawn`-Prozess

Die Workerqueue war auf vier vollstaendige reduzierte Rezeptorfenster begrenzt.
Der Einsekunden-Audiopuffer blieb unveraendert.

## Verwendete Quellen

Tatsaechlich verwendet wurden:

- der aktuelle freigegebene Uebergabeeingang
- `AGENTS.md`
- `docs/forschung/067_AUDIO_TRANSPORTKAPAZITAET_LAUF_169.md`
- `docs/forschung/068_ZWEIPHASIGE_REZEPTOR_FELD_GEGENBASELINE_LAUF_170.md`
- `mcm_field_organism/live_audio_adapter.py`
- `mcm_field_organism/live_audio_video_field.py`
- `mcm_field_organism/receptor_time_alignment.py`
- `mcm_field_organism/audio_video_neutral_field_runtime.py`
- `mcm_field_organism/shared_mcm_field.py`
- `tools/run_live_audio_overflow_localization.py`
- `tools/run_live_two_phase_field_probe.py`
- vorhandene Runner-, Adapter-, Runtime- und Architekturtests

Externe Quellen und projektweite Wissensdatenbanken wurden nicht verwendet.

## Verwendete Dateien und Schnittstellen

Neu erstellt wurden:

- `tools/run_live_process_decoupling_probe.py`
- `tests/test_run_live_process_decoupling_probe.py`
- dieser Bericht

Verwendet wurden unveraendert `_capture_live_receptor_windows`,
`_advance_captured_audio_video_sequences`, `_observe_live_field_window`,
`SharedMCMFieldSnapshot` und `restore_shared_mcm_field`.

Die technische Erweiterung ist auf den Forschungsrunner begrenzt. Der
Hauptprozess uebergibt nur bestehende `ReceptorTimeSequence`-Fenster mit
reduzierten Kontakten und Organismuszeit. Rohbilder und Audiosamples werden
weder uebergeben noch gespeichert. Feldgleichungen, Rezeptoren, Projektion,
Checkpointmechanik und Feldparameter wurden nicht geaendert.

Verwendet wurden OpenCV-Kameraindex 0 und sounddevice-Audioindex 1.

## Durchgefuehrte Schritte

1. Ein separater, mit Windows-`spawn` gestarteter Feldprozess wurde im Runner
   eingerichtet.
2. Die Uebergabequeue wurde fest auf vier Rezeptorfenster begrenzt.
3. Pro Fenster wurden Rueckstand, Queue-Wartezeit, Ende-zu-Ende-Latenz,
   Feldrechenzeit und Baselineidentitaet gemessen.
4. Ein Drei-Fenster-Techniklauf pruefte Spawn, Serialisierbarkeit und sauberen
   Prozessabschluss; er wurde nicht als Forschungsarm gewertet.
5. Danach wurden gleichprozessiger und prozess-entkoppelter 30-Sekunden-Arm
   nacheinander ausgefuehrt.
6. Der Rueckstand am Erfassungsende wurde vor dem anschliessenden Leerarbeiten
   separat festgehalten.
7. Betroffene Tests und Architekturvertraege wurden ausgefuehrt.

## Messergebnisse und Gegenbaselines

```text
Arm                         Audio  Video  Treiber  Transport  Max. Audiopuffer
Gleichprozessig              2974    395        0        576          100/100
Prozess-entkoppelt           2997    465        0          0            7/100
```

```text
Workerqueue-Kapazitaet:                 4 Fenster
Maximaler Worker-Rueckstand:            2 Fenster
Rueckstand am Erfassungsende:           1 Fenster
Rueckstand nach kontrolliertem Leeren:  0 Fenster
Gelieferte Workerresultate:            30 Fenster
```

```text
Ende-zu-Ende-Latenz Minimum:  0.5884 s
Ende-zu-Ende-Latenz Mittel:   1.0611 s
Ende-zu-Ende-Latenz Maximum:  1.5098 s
Maximale Worker-Queue-Wartezeit: 0.4700 s
```

```text
Arm                         Primaer Mittel  Baseline Mittel  Gesamt Mittel
Gleichprozessig                  0.4309 s          0.4103 s        0.8412 s
Prozess-entkoppelt               0.3290 s          0.3328 s        0.6618 s
```

```text
Unvollstaendige Prozessfenster: 0
Nicht fortschreitende Frames:   0
Nicht fortschreitende Fenster:  0
Baselinefehler:                 0
Rohsensorpayload gespeichert: nein
```

## Einordnung

**Beobachtet:** Der gleichprozessige Arm fuellte den Audiopuffer und verlor
576 Frames. Der Prozessarm verlor keine Audioframes, belegte maximal sieben
von 100 Audiopufferplaetzen und lieferte alle 30 Feldresultate mit exakter
Gegenbaseline. Der Worker-Rueckstand blieb unter der festen Kapazitaet, lag am
Erfassungsende aber noch bei einem Fenster.

**Technische Interpretation:** Die Prozessgrenze beseitigt im geprueften
30-Sekunden-Horizont die Konkurrenz, die zuvor den internen Audiotransport
ueberlastete. Der Feldworker verarbeitete den Strom im Mittel schneller als
ein Einsekundenfenster, erzeugte jedoch messbare zeitweise Latenz und war am
Erfassungsende noch mit dem letzten Fenster beschaeftigt.

**Hypothese:** Der Rueckstand von einem Fenster am Erfassungsende ist die
aktuell bearbeitete letzte Einheit und kein monoton wachsender Stau. Das ist
mit den vorliegenden Maximal- und Endwerten vereinbar, aber noch nicht ueber
einen laengeren Horizont nachgewiesen.

**Offene Frage:** Bleiben Rueckstand, Latenz und Audiotransport ueber mehrere
Minuten begrenzt, oder treten unter laengerer Betriebssystem- und Kameralast
erneut Spitzen bis zur Queuegrenze auf?

## Grenzen und nicht gepruefte Annahmen

Die beiden Arme liefen nacheinander; Weltinhalt, Kameraautomatik und
Betriebssystemlast waren nicht kontrolliert. Daher belegt der Lauf eine
technische Faehigkeit, keine genaue Leistungssteigerung um einen festen Faktor.

Der Horizont betrug nur 30 Sekunden. Maximaler und abschliessender Rueckstand
beweisen keinen stationaeren Langzeitverlauf. Eine Workerqueue ist technischer
Transport und kein MCM-Memory. Memory, Bedeutung, Organisation und Topologie
wurden nicht untersucht. Eine Zielabweichung liegt nicht vor.

## Konkrete Schlussfolgerung

Die begrenzte Prozessentkopplung stabilisiert den realen Onlinepfad im
geprueften 30-Sekunden-Lauf: null Treiber- und Transportverlust, vollstaendige
Fenster, fortschreitende Zeit und exakte Feldgegenbaseline. Das Ergebnis wurde
nicht durch groessere Audiopuffer oder geaenderte Feldmechanik erzeugt.

Der Onlinepfad ist damit fuer 30 Sekunden technisch funktionsfaehig, aber noch
nicht als langfristig stabil nachgewiesen. Der zeitweise Worker-Rueckstand und
die Latenz muessen vor realer Weltwirkung ueber einen laengeren Horizont
kontrolliert werden.

## Vorschlag fuer den naechsten begrenzten Forschungslauf

Lauf 172 sollte denselben Prozessarm unveraendert 120 Sekunden betreiben, ohne
erneuten gleichprozessigen Lastarm. Alle zehn Fenster sind Rueckstand und
Ende-zu-Ende-Latenz zeitaufgeloest zusammenzufassen.

Erfolgskriterien sind null Treiber- und Transportverlust, keine volle
Workerqueue, kein ueber die Zeit wachsender Rueckstand, vollstaendige Fenster,
fortschreitende Zeit und exakte Feldgegenbaseline. Erreicht der Rueckstand die
Kapazitaet oder zeigt er einen anhaltenden Anstieg, wird weder Queue noch
Audiopuffer vergroessert; dann gilt die bestehende Feldrechnung als noch nicht
langzeit-echtzeitfaehig. Memory-, Bedeutungs- und Organisationsauswertungen
bleiben ausgeschlossen.
