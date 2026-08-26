# Lauf 169: Audio-Transportkapazitaet unter Feldlast

## Forschungsfrage und Auftrag

Geprueft wurde, ob eine begrenzte Audio-Transportreserve von einer, zwei oder
vier Sekunden ausreicht, um den in Lauf 168 lokalisierten internen Rueckstand
unter unveraenderter Feld- und Gegenbaselineberechnung verlustfrei zu tragen.

Vorab festgelegte Erfolgskriterien waren null Transportverlust, null
Treiberoverflow, fortschreitende Fensterzeit und eine unveraenderte exakte
Feldgegenbaseline. Bei Verlust auch mit vier Sekunden galt die Stopplinie:
keine weitere Puffervergroesserung, sondern technische Entkopplung von
Erfassung und Feldberechnung.

## Verwendete Quellen

Tatsaechlich verwendet wurden:

- der aktuelle freigegebene Uebergabeeingang
- `AGENTS.md`
- `docs/forschung/066_AUDIO_OVERFLOW_LOKALISATION_LAUF_168.md`
- `mcm_field_organism/live_audio_adapter.py`
- `mcm_field_organism/live_audio_video_field.py`
- `tools/run_live_audio_overflow_localization.py`
- vorhandene Adapter-, Runtime-, Zeit- und Architekturtests

Externe Quellen und projektweite Wissensdatenbanken wurden nicht verwendet.

## Verwendete Dateien und Schnittstellen

Erweitert wurden:

- `mcm_field_organism/live_audio_adapter.py`
- `mcm_field_organism/live_audio_video_field.py`
- `mcm_field_organism/__init__.py`
- `tools/run_live_audio_overflow_localization.py`
- `tests/test_finite_audio_adapter.py`
- `tests/test_audio_video_neutral_field_runtime.py`
- `tests/test_run_live_audio_overflow_localization.py`

Neu erstellt wurden:

- `tools/run_live_audio_transport_capacity_probe.py`
- `tests/test_run_live_audio_transport_capacity_probe.py`
- dieser Bericht

Der bestehende Audiotransport erhielt einen expliziten, standardmaessig
weiterhin eine Sekunde grossen Pufferhorizont sowie Kapazitaets- und
Maximalbelegungsmessung. Primaere Feldrechnung und exakte Gegenbaseline wurden
pro Fenster separat mit `time.perf_counter` gemessen. Die Feldgleichungen,
Rezeptoren und Projektionswege wurden nicht veraendert.

Verwendet wurden OpenCV-Kameraindex 0 und sounddevice-Audioindex 1, das
Mikrofon der HD Pro Webcam C920.

## Durchgefuehrte Schritte

1. Begrenzte Transportkapazitaet und maximale Belegung wurden instrumentiert.
2. Primaere und kontrollierende Feldrechenzeit wurden pro Fenster gemessen.
3. Drei aufeinanderfolgende 30-Sekunden-Feldarme mit einer, zwei und vier
   Sekunden Pufferhorizont wurden ausgefuehrt.
4. Treiber- und Transportverlust, Rezeptorzahlen, Fensterzeit und exakte
   Feldgegenbaseline wurden fuer jeden Arm geprueft.
5. Adapter-, Runtime-, Zeit-, Runner- und Architekturvertraege wurden getestet.

## Messergebnisse und Gegenbaselines

```text
Puffer  Kapazitaet  Max. Belegung  Belegung  Treiber  Transport
1 s          100          100       100 %        0       1983
2 s          200          200       100 %        0       1644
4 s          400          400       100 %        0       1320
```

```text
Puffer  Audio  Video  Baselinefehler  Zeitfehler
1 s      2426    332         0              0
2 s      2428    333         0              0
4 s      2594    319         0              0
```

```text
Puffer  Primaer Mittel  Baseline Mittel  Gesamt Mittel  Gesamt Maximum
1 s        0.5014 s        0.4910 s        0.9923 s       1.2431 s
2 s        0.4692 s        0.4657 s        0.9349 s       1.2623 s
4 s        0.4751 s        0.4696 s        0.9447 s       1.2915 s
```

```text
Checkpoints je Arm:             29
Rohsensorpayload gespeichert:   nein
Regressionstests:               49 passed, 9 subtests passed
```

Alle drei Arme verwendeten dieselbe Feldmechanik und dieselbe exakte
Gegenbaseline. Die Kapazitaet war die einzige vorab festgelegte technische
Variation.

## Einordnung

**Beobachtet:** Jeder Puffer erreichte seine volle Kapazitaet. Auch vier
Sekunden verloren 1320 Audioframes. PortAudio meldete in keinem Arm einen
Input-Overflow. Zeitfortschritt und Feldgegenbaseline blieben fehlerfrei.

**Technische Interpretation:** Eine groessere begrenzte Warteschlange reduziert
in diesen Einzelarmen die Verlustzahl, beseitigt den Rueckstand jedoch nicht.
Die kombinierte primaere und kontrollierende Feldrechnung beanspruchte im
Mittel ungefaehr 0.93 bis 0.99 Sekunden je Einsekundenfenster und erreichte
Spitzen ueber 1.24 Sekunden. Damit arbeitet die Verarbeitung zeitweise
langsamer als der reale Zufluss.

**Hypothese:** Solange Erfassung und beide Feldrechnungen im selben
Python-Prozess um Rechenzeit konkurrieren, kann ein endlicher Puffer lediglich
Rueckstand verschieben und nicht verlaesslich abbauen.

**Offene Frage:** Der Lauf misst maximale, aber keine zeitaufgeloeste
Warteschlangenbelegung pro Fenster. Er beweist daher keine streng monotone
Belegungsentwicklung. Die Vollbelegung und der Verlust im Viersekundenarm
reichen jedoch fuer die vorab definierte Stopplinie aus.

## Grenzen und nicht gepruefte Annahmen

Die Arme wurden nacheinander ausgefuehrt. Betriebssystemlast,
Kameraautomatik und Weltinhalt waren nicht kontrolliert. Unterschiede zwischen
den Verlustzahlen duerfen deshalb nicht als exakte Kapazitaetskennlinie
interpretiert werden.

Die exakte Gegenbaseline verdoppelt einen wesentlichen Teil der Feldlast, ist
aber fuer diesen kontrollierten Forschungsarm absichtlich enthalten. Es wurden
keine Rohbilder oder Audiodaten gespeichert. Memory, Bedeutung, Organisation
und Topologie wurden nicht untersucht. Eine Zielabweichung ist nicht
erkennbar.

## Konkrete Schlussfolgerung

Keiner der vorab begrenzten Pufferhorizonte ermoeglichte eine verlustfreie
reale Audio-Video-Feldruntime. Vier Sekunden wurden vollstaendig belegt und
verloren weiterhin Audioframes. Die Stopplinie ist damit erreicht: eine weitere
Puffervergroesserung ist durch diese Befunde nicht gerechtfertigt.

## Vorschlag fuer den naechsten begrenzten Forschungslauf

Als naechster Lauf sollte eine rein technische, zweiphasige 30-Sekunden-
Gegenbaseline aufgebaut werden:

1. Kamera und Mikrofon erfassen zuerst ausschliesslich die bestehenden
   reduzierten, zeitgestempelten Rezeptorzustaende in einem explizit begrenzten
   Lauf; Rohsensorpayload wird nicht behalten.
2. Nach dem Schliessen der Geraete werden dieselben Fenster mit unveraenderter
   Feld- und Gegenbaselineberechnung fortgesetzt.

Verglichen werden diese zweiphasige Ausfuehrung und der bestehende Onlinearm
bei einem Einsekunden-Transportpuffer. Primaere Kriterien sind null Treiber-
und Transportverlust waehrend der Erfassungsphase, vollstaendige
Fensterbelegung, fortschreitende Zeitstempel und unveraenderte exakte
Feldgegenbaseline.

Erst wenn diese Gegenbaseline verlustfrei ist, ist die technische Ursache
ausreichend bestaetigt, um eine begrenzte Prozess- oder Worker-Entkopplung fuer
den Onlinepfad zu entwickeln. Memory-, Bedeutungs- und
Organisationsauswertungen bleiben ausgeschlossen.
