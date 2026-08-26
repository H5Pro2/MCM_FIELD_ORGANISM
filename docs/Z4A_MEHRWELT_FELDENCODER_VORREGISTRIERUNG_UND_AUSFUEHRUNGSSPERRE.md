# Z4-A: Mehrwelt-Feldencoder-Vorregistrierung und Ausfuehrungssperre

Stand: 2026-08-06

Status:

- Forschungsfrage, Weltinventar, Arme, Messungen und Entscheidungen statisch
  gebunden;
- zwei Medienquellen lokal und bytegebunden vorhanden;
- Z4-A1-Audioquelle, unabhaengige Kontrolle und Sequenzadapter implementiert,
  technisch reproduziert und final digestgebunden;
- historischer Browservertrag und Assets vorhanden; Z4-A2 bindet einen neuen
  kamerafreien Browser-zu-Rezeptor-Pfad statisch, dessen Implementierung und
  Digests noch fehlen;
- Z4-A3 bindet den generischen gemeinsamen P0/F3/B3-Trajektorienrunner
  statisch; alle drei Scheiben sind implementiert und synthetisch abgenommen;
- Z4-A4 bindet skalares Ergebnisschema, reine Entscheidung und den
  gesperrten Lauf-197-Einstieg; alle technischen Scheiben sind synthetisch
  abgenommen;
- Implementierung und Forschungslauf gesperrt.

## Forschungsfrage

> Bilden P0, F3 und B3 mehrere kontrollierte Video-, Audio-, audiovisuelle
> und Browserweltverlaeufe als technisch stabile kausale Feldtrajektorien ab,
> sodass frische Wiederholung und verlustlose Zeitteilung innerhalb ihrer
> numerischen Huelle bleiben, waehrend reale kausale Umordnung gegen eine
> unabhaengige Kontrollwelt unterscheidbar bleibt?

Z4-A prueft eine technische Feldencoderfunktion. Es gibt kein Training,
keinen Klassifikator und keinen Memory-, Bedeutungs-, Organisations-,
Feldzeit- oder KI-Claim.

## Quelleninventar

### W-V: kontrollierte reine Videowelt

```text
world_id:              z4a.video.street-traffic.v1
source_id:             public.visual.street-traffic.commons.2013-02-02
path:                  sources/media/Street traffic.webm
size_bytes:            26490572
sha1:                  7f916030f14d84a65aa92077339f472897915fef
sha256:                e5facb24baf755f0c1193999d823e99f6032661ad2bdef5cc28cc1cbbfde03e2
bound_interval:        0..35000 ms
sampling_interval:     125 ms
receptor_states:       280
reduced_digest:        f147109d3ac2c411328b0a514119df8fd18abd0bded487056d4a6502bc70780f
current_status:        source and reduced sequence previously reproduced
```

Nur Pixelwerte und technische Quellzeit duerfen den visuellen Rezeptor
erreichen. Dateiname, Herkunft und Metadaten bleiben observerseitig.

### W-AV: kontrollierte audiovisuelle Welt

```text
world_id:              z4a.av.nasa-earthrise.v1
source_id:             public.audiovisual.nasa-earthrise-realtime.svs.2013-12-20
path:                  sources/media/NASA Earthrise Realtime Apollo 8.mp4
size_bytes:            13547755
sha1:                  c63198a925ad227950cca597c4a8500656bacdfc
sha256:                9a061d639c17849e52ace712c8752b5d377123a9eec99df896728098bd783d74
bound_interval:        0..0.5 s
auditory_frames:       41
visual_frames:         15
auditory_digest:       501476111cdd3d17e9b5249b3774dc7918c8ffb8123264c16ce775ba5f6a175f
visual_digest:         86e9d1a2b1c01959f52d2446f855078dc313341f638bc8e23f43fcf79ea48d93
current_status:        source and both receptor sequences previously reproduced
```

Der kurze bereits auditierte Ausschnitt wird wiederverwendet. Eine andere
Stelle des Containers wird nicht nach einem Ergebnis gesucht.

### W-A: kontrollierte reine Audiowelt

```text
world_id:              z4a.audio.sound-mute-sound.v1
source_factory:        sound_mute_sound_20s_source
module:                mcm_field_organism/controlled_audio_phase_source.py
module_sha256:         f6e77cf2796d231995a461a2ceb908da687a38f4c55b3367d64eb99adf2e5f3c
sample_rate:           48000 Hz
frame_size:            480 samples
frequencies:           250, 1000, 4000 Hz
component_amplitude:   0.2
phases_seconds:        contact 20, mute 20, contact 20
source_frames:         6000
expected_receptor_states: 5991
current_status:        deterministic source and chain tested
```

Der
[Z4-A1-Audiovertrag](Z4A1_REINE_AUDIO_REZEPTORSEQUENZ_UND_KONTROLLVERTRAG.md)
bindet die kanonische `ReceptorTimeSequence`, die frequenzverschobene
unabhaengige Kontrollquelle und das Digestformat. Quelle, Kontrolle und
Wiederholung sind implementiert, jeweils exakt reproduziert und final
digestgebunden. W-A traegt damit `Z4A1_TECHNICALLY_BOUND`, ohne dass eine
Feldmatrix ausgefuehrt wurde.

### W-B: kontrollierte Browserwelt

```text
world_id:              z4a.browser.audiovisual.v1
contract_id:           browser.world.audiovisual.v1
contract_module:       mcm_field_organism/browser_world_contract.py
contract_module_sha256: 460ba77df16c913d7f857d4c3ef976b253b4412c40f3f0be11f1c5fc85db19de
duration_seconds:      35
phases_seconds:        static/silent 7, moving/tone 7, static/silent 21
movement_cycles:       3
tone_frequency_hz:     660
tone_gain:             0.18
```

Gebundene Assets:

```text
index.html:  bd2aa844867963dc6a936c1004b0be6949911c5ea9a0a5aa2fbf24d13a092f21
styles.css:  e1eab611427a6db65a7b14b9f0849acb2d2c1bdb29612a049e6bd48c924961b0
stimulus.js: 1a36ddee3be8a02a44acb4bba46b3a4880059551e8c011ba03a2b2e1c7a3563
```

Der vorhandene Server fuehrt die Welt ueber Kamera und Mikrofon zurueck. Das
ist unter der aktuellen Projektgrenze verboten. Der
[Z4-A2-Browservertrag](Z4A2_KAMERAFREIER_BROWSERWELT_REZEPTORVERTRAG.md)
bindet deshalb eine getrennte v2-Welt: tatsaechlich im Browser
gerasterte Canvas-Pixel werden mit 25 Hz erfasst, browserinternes
`OfflineAudioContext`-Audio mit 48 kHz, beides fluechtig und ohne physischen
Sensor. Eine vertikale 990-Hz-Welt ist als unabhaengige Kontrolle gebunden.
v2-Assets, direkter PNG-/PCM-Rezeptoradapter, Playwright-Capture-Schicht,
Runtime-Bindungsresolver und reale Playwright-/Chromium-Installation sind
technisch gebunden; der visuelle Ein-Tick-Smoke ist bestanden.
Auch der OfflineAudio-Grenzsmoke ist bestanden. Aktiver Quellenkontrast und
echte Rezeptorsequenzdigests fehlen noch. W-B bleibt deshalb gesperrt. Eine
Python-Rekonstruktion nur aus Phasenwerten gilt weiterhin nicht als
Browserweltmessung.

## Weltzulassungsregel

Die Vollmatrix darf nur starten, wenn alle vier Weltfamilien gleichzeitig:

- eine feste technische Quellidentitaet besitzen;
- kanonische Rezeptorsequenzen mit festem Digest liefern;
- denselben neutralen Rezeptorvertrag wie ihre Vergleichsarme verwenden;
- ohne Kamera, Mikrofon als Live-Sensor oder physische Rueckkopplung laufen;
- keine Metadaten, Labels oder Phasen-IDs in den Feldzustand schreiben.

Ein Drei-Welten-Ersatzlauf ist nicht zugelassen. Das Fehlen der Browserquelle
darf nicht durch Verdoppelung einer Medienwelt kaschiert werden.

## Gebundene Feldformen

### P0

- bestehende neutrale S/H-Runtime;
- `response_time_seconds = 1.0`;
- `afterimage_time_constant_seconds = 0.5`;
- keine M-Wirkung.

### F3

- bestehende unveraenderte F3-Form;
- `lambda_sm_per_second = 1.0`;
- `kappa = 0.5`;
- `eta = 1.0`;
- gleiche gleichfoermige Anfangsmasse wie Lauf 188 bis 196;
- keine Nachparametrierung.

### B3

- bestehende lineare gekoppelte Feldbaseline;
- dieselben festen Parameter und dasselbe lokale Zustandsbudget wie im
  Z1-/E3-Vergleich;
- keine Anpassung an eine Weltfamilie.

## Statischer API-Befund

P0 und F3 besitzen mit `run_mcm_f3_causal_comparison` bereits einen
allgemeinen Eingang fuer `ReceptorTimeSequence`. Der aktuelle B3-
Trajektorienpfad und der passive Observer sind dagegen in
`mcm_f3_z1_runner.py` an die Z1-Quellenarme gekoppelt.

Der
[Z4-A3-Runnervertrag](Z4A3_GENERISCHER_P0_F3_B3_TRAJEKTORIENRUNNERVERTRAG.md)
bindet inzwischen die weltneutrale Zielstruktur: rollenvariable
Trajektorien, gemeinsamer Handoff je Arm, echter Completion-Support, P0 ohne
Pseudo-M-State sowie 42 Aufgaben pro Welt. Die notwendigen generischen
Module und der passive P0-Callback sind noch nicht implementiert.

Vor Z4-A ist deshalb genau ein technischer gemeinsamer Runner erforderlich,
der:

- beliebige bereits gebundene Rezeptorsequenzen liest;
- P0, F3 und B3 vom selben Basisfeld und selben Handoff startet;
- dieselben Abschlussgruppen und Observerstuetzpunkte erzwingt;
- S/H fuer alle drei Formen und M beziehungsweise B3-Zustand getrennt
  beobachtet;
- keine Entscheidung, Lauf-ID oder Ergebnisinterpretation enthaelt.

Die bestehenden Module bleiben statisch gebunden:

```text
mcm_f3_causal_runner.py sha256:
d16b742b2319c34614ccfa79a838a2c1003fd6830f11b4a5e8fc4949aaa325de

mcm_f3_baseline_coupling.py sha256:
270eb703ed4d76bbc33bbd510551fdf9374a4c8a437d01cd119ebc5a4c76f11c

mcm_f3_z1_trajectory.py sha256:
f1416f1fda7ca293a0bacaa5145f346d25dc3be03501dc6aa504dbc0f021b121
```

Diese Hashes binden den statisch gelesenen Bestand. Eine spaetere notwendige
Implementierung erhaelt neue eigene Bindungen; sie darf die bestehenden
Feldgleichungen nicht veraendern.

## Gebundene Kausalarme je Welt

Fuer jede Weltfamilie und jede Feldform gelten genau:

1. `reference`: kanonischer Weltverlauf;
2. `reproduction`: frischer byte- und sequenzidentischer Wiederholungsarm;
3. `partitioned`: gleiche Rezeptorereignisse mit halbierten leeren
   Integrationsintervallen;
4. `reversed`: modalitaetsweise Wertfolge auf demselben technischen
   Zeitraster umgekehrt;
5. `permuted`: feste Vierblockfolge `0,3,2,1` auf demselben Inventar;
6. `independent`: vorab gebundene unabhaengige Kontrollfolge derselben
   Weltfamilie und desselben technischen Budgets.

Die unabhaengige Kontrollfolge fuer W-A ist durch Z4-A1 und fuer W-B durch
Z4-A2 statisch gebunden. Beide sind noch nicht implementiert oder
digestgebunden. Diese Quellenluecken sind Teil der Ausfuehrungssperre.

Zeitdehnung und Zeitkompression gehoeren nicht zur Z4-A-Entscheidung. Sie
duerfen spaeter nur deskriptiv ausgegeben werden, weil Weltzeitbindung bereits
belegt ist.

## Gemeinsamer Observer-Support

Die Sachtrajektorie verwendet wie Lauf 196 ausschliesslich:

- den neutralen Startzustand;
- echte Rezeptorabschlussgruppen;
- keine zusaetzlichen leeren technischen Partitionsabschluesse.

Die technische Volltrajektorie bleibt fuer Diagnose vorhanden. Referenz,
Wiederholung und Teilungsarm muessen dasselbe Sachstuetzpunktinventar
besitzen. Andernfalls lautet die Entscheidung sofort
`FIELD_ENCODER_NOT_TECHNICALLY_STABLE`.

## Messungen

Getrennt fuer S, H und den jeweiligen Zusatzstate:

- kumulative euklidische Pfadlaenge;
- Normierung auf `q = 0..1`;
- lineare Abtastung auf 101 Punkten;
- skalierte L-inf-Trajektoriendistanz;
- Endzustands-L2 nur als technische Diagnose;
- n/2n/4n-Konvergenz;
- maximale Massen- und Wertebereichsverletzung;
- Laufzeit, Substepzahl und persistiertes Zustandsbudget.

Die numerische Huelle bleibt:

```text
epsilon_component = max(1e-12, 4 * D_component(2n, 4n))
```

Sie wird je Welt, Feldform und Komponente aus den vorregistrierten
Verfeinerungsarmen bestimmt und nicht nach einem Sachvergleich veraendert.

## Technische Mindestkontrollen

- Quell- und Rezeptordigests stimmen mit den spaeter final gebundenen Werten;
- frische Wiederholung liegt komponentenweise innerhalb der Huelle;
- `partitioned` liegt komponentenweise innerhalb der Huelle;
- n/2n/4n-Endfehler nimmt ab;
- keine NaN-, Inf-, Massen- oder Wertebereichsverletzung;
- Umkehrung und Permutation erhalten das Ereignisinventar;
- Observer an/aus veraendert keinen Snapshotdigest;
- alle Modelle lesen denselben Handoff;
- keine Rohmedien oder Rohtrajektorien im Organismuszustand.

## Entscheidungslogik

### Technischer Stopp

`FIELD_ENCODER_NOT_TECHNICALLY_STABLE`, sobald eine Quellenbindung,
Wiederholung, Teilung, Konvergenz, Invariante oder Supportgleichheit scheitert.
Danach werden keine Sachwerte interpretiert.

### Kausale Feldtrennung

Eine Feldform traegt in einer Welt `stable_causal_separation`, wenn:

- `reversed` in mindestens einer aktiven Komponente oberhalb ihrer Huelle
  liegt;
- `permuted` in mindestens einer aktiven Komponente oberhalb ihrer Huelle
  liegt;
- `independent` in mindestens einer aktiven Komponente oberhalb ihrer Huelle
  liegt;
- Wiederholung und Teilung gleichzeitig innerhalb aller Huellen bleiben.

Eine groessere Distanz ist nicht automatisch besser.

### F3-Vorteil

`F3_TECHNICAL_TRAJECTORY_ADVANTAGE` ist nur zulaessig, wenn:

- F3 in mindestens zwei der vier Weltfamilien
  `stable_causal_separation` traegt;
- in denselben Welten sowohl P0 als auch B3 mindestens eine der drei
  erforderlichen kausalen Trennungen nicht tragen;
- F3 in keiner Welt eine technische Stabilitaetskontrolle verletzt;
- jeder der drei erforderlichen F3-Kausalarme auch in S oder H oberhalb
  seiner Huelle liegt und der Unterschied damit nicht nur in M besteht.

Damit entsteht kein frei optimierter Prozentvorteil. F3 muss eine technische
Funktion tragen, die beide einfacheren Formen im selben Design nicht tragen.

### Gesamtentscheidungen

- `FIELD_ENCODER_CAUSAL_BUT_BASELINE_EQUIVALENT`: P0 oder B3 traegt selbst
  die erforderliche Drei-Welten-Breite oder die Baselines decken gemeinsam
  jede stabile F3-Welt gemaess Z4-A4 ab.
- `F3_TECHNICAL_TRAJECTORY_ADVANTAGE`: nur gemaess der strengen Bedingung
  oben.
- `NO_STABLE_CAUSAL_FIELD_SEPARATION`: keine Feldform traegt in mindestens
  drei Weltfamilien die vollstaendige stabile kausale Trennung.
- `Z4A_DECISION_UNRESOLVED`: technisch gueltiges Mischmuster, das keine der
  drei Sachentscheidungen vollstaendig traegt.

Die exakte, widerspruchsfreie Reihenfolge und die konservative Restklasse
sind im
[Z4-A4-Entscheidungsvertrag](Z4A4_SKALARES_ERGEBNIS_ENTSCHEIDUNG_UND_LAUF197_SPERRE.md)
gebunden. Es wird keine Entscheidung durch freie Interpretation erzwungen.

## Persistenzgrenze

Ein spaeteres Ergebnisartefakt darf nur enthalten:

- Quellen- und Ausfuehrungsdigests;
- Supportzahlen und technische Kontrollen;
- skalare Distanzen und Huellen;
- Entscheidungen pro Welt und Feldform;
- Laufzeit- und Zustandsbudget.

Nicht persistiert werden Rohframes, Audiosamples, vollstaendige
Rezeptorsequenzen oder Feldtrajektorien.

## Aktuelle Ausfuehrungssperre

Z4-A ist nicht ausfuehrbar, solange mindestens einer dieser Punkte offen ist:

1. W-B besitzt Vertrag, v2-Assets, direkten kamerafreien
   Browser-zu-Rezeptor-Adapter, Capture-Schicht, Runtime-Bindungsresolver,
   reale gebundene Playwright-/Browserinstallation, visuellen Ein-Tick-Smoke
   und OfflineAudio-Grenzsmoke, aber noch keinen aktiven Quellenkontrast und
   keine echten Rezeptorsequenzdigests.
2. W-B darf nicht den vorhandenen Kamera-/Mikrofonserver verwenden.
3. W-B besitzt noch keine implementierte und digestgebundene unabhaengige
   Kontrollsequenz.
4. Der reservierte Lauf-197-Zielpfad bleibt bis zur vollstaendigen Z4-A2-
   Bindung und einer ausdruecklichen Ausfuehrungsentscheidung gesperrt.

Es gibt keinen Teil-, Probe- oder Drei-Welten-Lauf. `lauf-197` ist nur fuer
die spaetere Vollmatrix reserviert und noch nicht ausgefuehrt.

## Aussagegrenze

Auch ein spaeter erfolgreicher Z4-A-Lauf belegt nur einen stabilen kausalen
Feldencoder im definierten technischen Sinn. Er belegt kein Erkennen, Lernen,
Memory, inneren Kontext, Organisation, Topologie, Semantik,
Selbstregulation oder KI.

## Bester naechster Schritt

Die vier statischen Vertraege sind abgeschlossen. Der technische Stand ist:

1. Z4-A1: Audio-Rezeptorsequenz und unabhaengige Kontrolle sind implementiert,
   technisch reproduziert und digestgebunden;
2. Z4-A2: Vertrag, v2-Assets, direkter PNG-/PCM-Rezeptoradapter,
   Playwright-Capture-Schicht, Runtime-Bindungsresolver, reale Runtime,
   Browserbinary, visueller Ein-Tick-Smoke und OfflineAudio-Grenzsmoke sind
   technisch gebunden; aktiver Quellenkontrast und echte
   Browsersequenzdigests bleiben gesperrt;
3. Z4-A3: generischer gemeinsamer P0/F3/B3-Trajektorienrunner ist statisch
   spezifiziert; alle drei Scheiben sind implementiert und synthetisch
   abgenommen.
4. Z4-A4: skalares Ergebnisschema, reine Entscheidungsfunktion, Messadapter
   und one-shot Sperre sind technisch implementiert und synthetisch
   abgenommen.

Z4-A bleibt gemaess dem
[aktiven Richtungsentscheid](RICHTUNGSENTSCHEID_SUBSTRAT_VOR_MEMORYBEFUND.md)
am Stand `Z4A2_OFFLINE_AUDIO_SMOKE_BOUND` als technische Wahrnehmungs-,
Quellen- und Baseline-Infrastruktur geparkt. Aktiver Quellenkontrast,
Rezeptorsequenzen, Vollcapture und Lauf 197 werden nicht gestartet, solange
der Substratzweig sie nicht fuer eine vorregistrierte Gegenbaseline benoetigt.
S0, S1-A und S1-B sind inzwischen gebunden. Der projektweite naechste Schritt
ist S2-C16 mit der kanonischen A8/B8-End-to-End-Komposition; Z4-A bleibt geparkt.
