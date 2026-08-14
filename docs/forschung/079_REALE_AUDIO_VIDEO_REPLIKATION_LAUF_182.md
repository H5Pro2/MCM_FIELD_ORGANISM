# Lauf 182: Begrenzte reale Audio-Video-Replikation

## Forschungsfrage und Auftrag

Geprueft wurde, ob die vorhandene prozessentkoppelte reale Kamera- und
Mikrofonruntime in einem neuen, auf zehn Einsekundenfenster begrenzten Lauf
weiterhin beide Rezeptorwege kontinuierlich und verlustfrei bis zum
`SharedMCMField` traegt.

Gemessen wurden Zeitfortschritt, Paket- und Fensterzahlen, effektive Raten,
Treiber- und Transportverluste, Worker-Rueckstand, Modalitaetsherkunft sowie
die exakte Feldgegenbaseline. Memory-, Bedeutungs- und
Organisationsauswertungen waren ausgeschlossen.

## Verwendete Quellen

Tatsaechlich verwendet wurden:

- aktueller Uebergabeeingang und Lauf 181
- `AGENTS.md`
- `docs/forschung/064_REALE_AUDIO_VIDEO_WAHRNEHMUNGSSTABILITAET_LAUF_166.md`
- `docs/forschung/065_REALE_AUDIO_VIDEO_LANGZEITSTABILITAET_LAUF_167.md`
- `docs/forschung/069_PROZESS_ENTKOPPELTE_ONLINE_FELDFORTSETZUNG_LAUF_171.md`
- `docs/forschung/070_PROZESS_ENTKOPPELTE_120S_LANGZEITSTABILITAET_LAUF_172.md`
- vorhandene reale Runner, Runtime-, Adapter- und Zeittests

Externe Quellen und projektfremde Datenbanken wurden nicht verwendet.

## Verwendete Dateien und Schnittstellen

Ausgefuehrt wurden:

- `tools/run_live_process_decoupling_probe.py`
- `tools/run_live_receptor_time_audit.py`
- die direkt abhaengigen Prozess-, Zeit-, Audio-, Video- und Feldtests

Verwendete Geraete:

- Kamera: expliziter OpenCV-Index `0`
- Audio: expliziter `sounddevice`-Index `1`, aktuell als
  `Mikrofon (HD Pro Webcam C920), MME` inventarisiert

Verwendete Schnittstellen und Komponenten:

- `_capture_live_receptor_windows`
- `_advance_captured_audio_video_sequences`
- `run_process_decoupled`
- `capture_live_audio_video_time_audit`
- `ReceptorTimeSequence`
- `SharedMCMFieldSnapshot`
- exakte unabhaengige Feldgegenbaseline

Neu angelegt wurde nur dieses Forschungsdokument. Feldmechanik, Rezeptoren,
Runner und Adapter wurden nicht geaendert.

## Durchgefuehrte Schritte

1. Vorhandene reale Berichte und aktuelle Runnergrenzen abgeglichen.
2. Die aktuelle Audioeingabegeraeteliste schreibfrei inventarisiert.
3. Einen prozessentkoppelten Lauf ueber zehn Einsekundenfenster mit Kamera `0`
   und Audio `1` ausgefuehrt.
4. Einen getrennten nominal fuenfsekundigen Zeitaudit auf demselben
   Geraetepaar ausgefuehrt.
5. Prozess-, Zeit-, Audioadapter-, Audio-Video-Feld- und finite
   Audio-Video-Tests ausgefuehrt.
6. Es wurden keine Rohbilder oder Audiosamples gespeichert.

## Messergebnisse und Gegenbaselines

### Prozessentkoppelter Feldlauf, 10 Fenster

```text
abgeschlossene Fenster:                  10
Workerresultate:                         10
auditive Rezeptorzustaende:             996
visuelle Rezeptorzustaende:             203
Kamera-Capture-Frames:                  204
nominale effektive Audiozustandsrate:  99.6 Hz
nominale effektive Videozustandsrate:  20.3 Hz
Treiber-Input-Overflow:                   0
Transportverluste:                       0
maximale Audiopufferbelegung:           3 / 100
unvollstaendige Fenster:                  0
nicht fortschreitende Frames:             0
nicht fortschreitende Fenster:            0
Baseline-Abweichungsfenster:              0
```

```text
Workerqueue-Kapazitaet:                   4 Fenster
maximaler Worker-Rueckstand:              2 Fenster
Rueckstand am Erfassungsende:             2 Fenster
Rueckstand nach kontrolliertem Leeren:    0 Fenster
maximale Queue-Wartezeit:                 0.0591111 s
```

```text
Ende-zu-Ende-Latenz Minimum:              0.5541 s
Ende-zu-Ende-Latenz Mittel:               0.8791 s
Ende-zu-Ende-Latenz Maximum:              1.1132 s
Feld plus Baseline Mittel:                0.6035 s
Feld plus Baseline Maximum:               0.7810 s
Rohsensorpayload gespeichert:             nein
Feldmechanik geaendert:                   nein
```

### Getrennter Zeitaudit, nominal 5 Sekunden

```text
Organismustakt:                           organism.monotonic_ns
auditive Zustaende:                       491
auditiver Erfassungsspann:                4.9194695 s
effektive auditive Rate ueber Spann:      ca. 99.8 Hz
visuelle Zustaende:                       145
visueller Erfassungsspann:                6.1488994 s
effektive visuelle Rate ueber Spann:      ca. 23.6 Hz
native Ueberlappungen:                    606
eindeutige Eins-zu-eins-Ueberlappungen:   0
mehrdeutige Snapshots:                    607
unzugeordnete Snapshots:                  29
Auswahl oder Interpolation:               nein
```

Die Modalitaetsherkunft wurde als `auditory` und `visual` auf demselben
Organismustakt ausgewiesen. Der Feldlauf lieferte zehn von zehn exakten
Snapshot-Gegenbaselines.

Verifikation:

```text
47 passed, 9 subtests passed in 1.78s
```

Ein erster Testaufruf enthielt einen nicht vorhandenen Testdateinamen und
wurde vor Ausfuehrung abgewiesen. Er ist kein Forschungsbefund. Der anhand des
tatsaechlichen Inventars korrigierte Testlauf war vollstaendig erfolgreich.

## Einordnung

**Beobachtet:** Beide realen Modalitaeten lieferten in allen zehn Fenstern
reduzierte Rezeptorzustaende. Zeit und Frames schritten fort. Es gab weder
Treiber- noch Transportverlust und keine Abweichung von der exakten
Feldgegenbaseline.

**Beobachtet:** Der Worker-Rueckstand erreichte zwei von vier Fenstern, wurde
nach Erfassungsende aber vollstaendig abgearbeitet. Die mittlere Feld- und
Baselinezeit blieb unter der Fensterdauer.

**Technische Interpretation:** Die vorhandene Prozessentkopplung trug den
realen Kamera-/Mikrofonstrom im geprueften Zehnsekundenhorizont verlustfrei bis
zum Shared-Field-Snapshot. Die exakte Gegenbaseline belegt die unverfaelschte
Weiterrechnung der angekommenen reduzierten Kontakte, nicht die physische
Richtigkeit des Weltinhalts.

**Offene Frage:** Ein kalibrierter Audio-Video-Versatz ist mit dem vorhandenen
Audit nicht bestimmbar. Die unterschiedlichen nativen Raten erzeugten 606
viele-zu-viele Ueberlappungen und kein eindeutiges Zustandspaar. Ohne externen
gemeinsamen Marker waere eine einzelne Versatzzahl eine nicht gepruefte
Annahme.

## Grenzen und nicht gepruefte Annahmen

- Der primaere Feldlauf umfasste nur zehn Sekunden und ist keine neue
  Langzeitgarantie.
- Der Zeitaudit war ein separater Lauf und keine nachtraegliche Rohdatenanalyse
  des Zehnfensterlaufs.
- Kameraautomatik, Weltinhalt und Betriebssystemlast waren unkontrolliert.
- Es gab keinen externen Hardware-Zeitstempel oder kalibrierten
  Audio-Video-Latenzmarker.
- Dock-Herkunft wurde durch vorhandene Modalitaets-, Geometrie- und
  Verteilervertraege sowie Tests kontrolliert, nicht durch einen physischen
  Marker.
- Kamera-Capture-Frames und visuelle Rezeptorzustaende sind wegen Start- und
  Abschlussverarbeitung nicht als identische Zaehler vorausgesetzt.
- Keine Browser- oder Mediendatei wurde verwendet oder erzeugt.
- Memory, Bedeutung, Agency, Organisation und Topologie wurden nicht
  untersucht oder nachgewiesen.
- Bestehende fremde Workspace-Aenderungen blieben unangetastet.

Eine Zielabweichung ist nicht erkennbar.

## Konkrete Schlussfolgerung

Der reale prozessentkoppelte Kamera-/Mikrofonpfad war im neuen begrenzten Lauf
technisch funktionsfaehig: beide Modalitaeten waren vorhanden, Zeiten
schritten fort, Verluste blieben null und alle zehn Feldsnapshots entsprachen
der exakten Gegenbaseline.

Dies bestaetigt reale Wahrnehmungs- und Uebergabestabilitaet fuer den
geprueften Horizont. Es ist kein Nachweis von Memory, eigenstaendiger
Feldorganisation oder physischer Feld-Welt-Feld-Rueckkopplung.

## Vorschlag fuer den naechsten begrenzten Forschungslauf

Als Lauf 183 sollte kein weiterer allgemeiner Stabilitaetslauf folgen. Die
verbleibende technische Synchronisationsfrage sollte mit einem kontrollierten,
gleichzeitig sicht- und hoerbaren physischen Marker vorregistriert werden.

Vor einer Ausfuehrung ist nur zu klaeren, ob ein solcher Marker physisch
bereitgestellt werden kann. Gemessen wuerden die Differenz der ersten
auditiven und visuellen Markerantwort auf dem vorhandenen
`organism.monotonic_ns`-Takt, die Streuung ueber eine kleine feste
Wiederholungszahl und eine Nullaufnahme ohne Marker. Feld-, Memory- und
Effektorregeln bleiben unveraendert.

Kann kein physischer Marker bereitgestellt werden, ist die Versatzfrage als
technische Messgrenze zu schliessen und der naechste Grundlagenzweig bleibt
der getrennte physische Feld-Welt-Feld-Aufbau.
