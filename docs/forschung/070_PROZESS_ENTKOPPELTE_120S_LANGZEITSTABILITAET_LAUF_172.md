# Lauf 172: Prozess-entkoppelte 120-Sekunden-Langzeitstabilitaet

## Forschungsfrage und Auftrag

Geprueft wurde, ob der in Lauf 171 fuer 30 Sekunden stabilisierte
prozess-entkoppelte Audio-Video-Feldpfad ueber 120 Sekunden ohne Audioverlust,
volle Workerqueue oder wachsenden Rueckstand weiterarbeitet.

Der vorhandene Prozessarm wurde unveraendert verwendet. Ein erneuter
gleichprozessiger Lastarm war nicht Bestandteil des Auftrags. Die
Workerqueue blieb auf vier reduzierte Rezeptorfenster und der Audiotransport
auf eine Sekunde begrenzt.

## Verwendete Quellen

Tatsaechlich verwendet wurden:

- der aktuelle freigegebene Uebergabeeingang
- `AGENTS.md`
- `docs/forschung/068_ZWEIPHASIGE_REZEPTOR_FELD_GEGENBASELINE_LAUF_170.md`
- `docs/forschung/069_PROZESS_ENTKOPPELTE_ONLINE_FELDFORTSETZUNG_LAUF_171.md`
- `tools/run_live_process_decoupling_probe.py`
- `tests/test_run_live_process_decoupling_probe.py`
- `mcm_field_organism/live_audio_adapter.py`
- `mcm_field_organism/live_audio_video_field.py`
- `mcm_field_organism/audio_video_neutral_field_runtime.py`
- vorhandene Adapter-, Runtime- und Architekturtests

Externe Quellen und projektweite Wissensdatenbanken wurden nicht verwendet.

## Verwendete Dateien und Schnittstellen

Erweitert wurden:

- `tools/run_live_process_decoupling_probe.py`
- `tests/test_run_live_process_decoupling_probe.py`

Neu erstellt wurde dieser Bericht.

Der Runner erhielt ausschliesslich eine 120-Sekunden-Prozessarmoption und
Zehn-Fenster-Profile. Verwendet wurden weiterhin die bestehenden reduzierten
`ReceptorTimeSequence`-Fenster, `_capture_live_receptor_windows`,
`_advance_captured_audio_video_sequences` und die exakte Feldgegenbaseline.

Feldmechanik, Rezeptoren, Projektion, Worker- und Audiopufferkapazitaet wurden
nicht veraendert. Rohbilder und Audiosamples wurden weder uebergeben noch
gespeichert. Verwendet wurden Kameraindex 0 und Audioindex 1.

## Durchgefuehrte Schritte

1. Der bestehende Prozessrunner wurde fuer einen reinen 120-Sekunden-Arm
   freigeschaltet.
2. Fuer jeweils zehn Fenster wurden Worker-Rueckstand, Ende-zu-Ende-Latenz,
   Feldrechenzeit, Audiopufferbelegung, Verluste und Baselinefehler
   zusammengefasst.
3. Der Prozessarm wurde fuer 120 gemeinsame reale Rezeptorfenster ausgefuehrt.
4. Rueckstand am Erfassungsende und nach kontrolliertem Leeren wurden getrennt
   erfasst.
5. Betroffene Tests und Diff-Formatvertraege wurden geprueft.

## Messergebnisse und Gegenbaselines

```text
Fenster:                            120
Audioframes:                      11997
Videoframes:                       1885
Treiberueberlaeufe:                   0
Transportverluste:                    0
Maximale Audiopufferbelegung:       6/100
Unvollstaendige Fenster:                0
Nicht fortschreitende Frames/Fenster: 0/0
Baselinefehler:                         0
```

```text
Workerqueue-Kapazitaet:                 4 Fenster
Maximaler Rueckstand gesamt:            1 Fenster
Maximaler Rueckstand in jedem 10er-Block: 1 Fenster
Rueckstand am Erfassungsende:           1 Fenster
Rueckstand nach kontrolliertem Leeren:  0 Fenster
Maximale Queue-Wartezeit:               0.0095483 s
```

```text
Ende-zu-Ende-Latenz Minimum: 0.6255 s
Ende-zu-Ende-Latenz Mittel:  0.7602 s
Ende-zu-Ende-Latenz Maximum: 1.0298 s

Feld plus Baseline Minimum:  0.3961 s
Feld plus Baseline Mittel:   0.4980 s
Feld plus Baseline Maximum:  0.7589 s
```

Die zwoelf Zehn-Fenster-Profile zeigten:

```text
Fenster     Max. Rueckstand  Latenzmittel  Latenzmaximum  Verlust
000-009          1             0.7252 s       0.8188 s       0
010-019          1             0.7763 s       0.8720 s       0
020-029          1             0.7616 s       0.8728 s       0
030-039          1             0.7981 s       0.9570 s       0
040-049          1             0.7323 s       0.8478 s       0
050-059          1             0.7651 s       0.8297 s       0
060-069          1             0.7690 s       1.0298 s       0
070-079          1             0.7447 s       0.8194 s       0
080-089          1             0.7628 s       0.9072 s       0
090-099          1             0.7948 s       0.9444 s       0
100-109          1             0.7406 s       0.8141 s       0
110-119          1             0.7523 s       0.8462 s       0
```

Die kumulative Audiopuffer-Maximalbelegung stieg in den Profilen von drei auf
sechs Frames, blieb danach weit unter der Kapazitaet und erzeugte keinen
Verlust.

## Einordnung

**Beobachtet:** Alle 120 Fenster wurden verarbeitet. In keinem Zehn-Fenster-
Intervall stieg der Worker-Rueckstand ueber ein Fenster. Es gab keine Treiber-
oder Transportverluste, keine volle Queue, keine Zeitfehler und keine
Abweichung von der exakten Feldgegenbaseline.

**Technische Interpretation:** Der Worker verarbeitet die bestehende Feld-
und Kontrollrechnung im geprueften Zweiminutenhorizont schneller als der
Fensterzustrom. Die stabilen Intervallwerte widersprechen einem monoton
wachsenden Rueckstau in diesem Lauf.

**Hypothese:** Das eine ausstehende Fenster am Erfassungsende entspricht der
normalen Verarbeitung des zuletzt uebergebenen Fensters. Die geringe maximale
Queue-Wartezeit und der konstante Intervallrueckstand stuetzen diese Deutung.

**Offene Frage:** Der Lauf belegt keine unbegrenzte Betriebsdauer und keine
Stabilitaet unter absichtlich erhoehter externer Systemlast.

## Grenzen und nicht gepruefte Annahmen

Es wurde ein einzelner 120-Sekunden-Lauf ausgefuehrt. Kameraautomatik,
Weltinhalt und Betriebssystemlast waren nicht kontrolliert. Die Profile sind
daher ein technischer Langzeitbefund dieses Laufs, keine allgemeine
Echtzeitgarantie fuer jede Hardware.

Die Prozessqueue ist technischer Transport und kein MCM-Memory. Es wurden
keine Memory-, Bedeutungs-, Organisations- oder Topologieeigenschaften
untersucht. Eine Zielabweichung liegt nicht vor.

## Konkrete Schlussfolgerung

Die prozess-entkoppelte reale Audio-Video-Feldruntime ist im kontrollierten
120-Sekunden-Horizont technisch stabil. Alle vorab festgelegten
Erfolgskriterien wurden erfuellt, ohne Puffervergroesserung oder Aenderung der
MCM-Feldmechanik.

Damit ist die zuvor offene Runtime-Grundlage ausreichend belastbar, um den
naechsten Grundlagenzweig nicht weiter durch synthetische Persistenz- oder
Memorylaeufe zu verzoegern. Der Befund betrifft ausschliesslich verlaessliche
Weltaufnahme und Feldfortsetzung.

## Vorschlag fuer den naechsten begrenzten Forschungslauf

Lauf 173 sollte den vorhandenen physischen Aufbauvertrag mit der nun
stabilisierten Prozessruntime zusammenfuehren und einen einzelnen technischen
Vorabnahmelauf fuer den getrennten Pfad vorbereiten:

```text
MCM-Feld -> physischer Effektor -> passive Zielflaeche
          -> Kamera -> Rezeptor -> MCM-Feld
```

Die technische Vorbereitung muss pruefen, dass die Kamera den Effektor nicht
sieht, nur die passive Zielflaeche erfasst und Originalwirkung, blockierter
Lichtweg, neutrale Ausgabe sowie unterbrochene Rueckkehr als getrennte Arme
ausfuehrbar sind. Ohne physisch bestaetigten Aufbau darf kein Kausalbefund
behauptet werden. Memory-, Bedeutungs- und Organisationsauswertungen bleiben
ausgeschlossen.
