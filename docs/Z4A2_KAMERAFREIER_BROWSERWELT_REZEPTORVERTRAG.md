# Z4-A2: Kamerafreier Browserwelt-zu-Rezeptor-Vertrag

Stand: 2026-08-06

Status:

- direkte Browserwelt, unabhaengige Kontrollwelt und Rezeptoruebergabe
  statisch gebunden;
- historischer Kamera-/Mikrofonpfad ausdruecklich ausgeschlossen;
- Zielassets und direkter PNG-/PCM-Rezeptoradapter implementiert und
  synthetisch abgenommen;
- Browserautomationsadapter, Browserbinary und reale Rezeptorsequenzdigests
  noch nicht gebunden;
- kein Browser gestartet, keine Quelle erzeugt und kein Lauf ausgefuehrt.

## Zweck

Z4-A2 schliesst ausschliesslich die statische Vertragsluecke der Browserwelt
W-B aus der
[Z4-A-Vorregistrierung](Z4A_MEHRWELT_FELDENCODER_VORREGISTRIERUNG_UND_AUSFUEHRUNGSSPERRE.md).
Der Vertrag legt fest, wie tatsaechlich vom Browser gerasterte Canvas-Pixel
und vom Browser berechnete Web-Audio-Samples spaeter ohne Kamera, Mikrofon,
Lautsprecheraufnahme oder physische Rueckkopplung an die bestehenden
neutralen Rezeptoren uebergeben werden duerfen.

Z4-A2 ist keine Feldmessung. Es wird weder eine Browserausgabe erzeugt noch
eine Feldfunktion bewertet.

## Abgrenzung vom vorhandenen v1-Pfad

Der vorhandene Pfad unter `tools/controlled_browser_world/` bleibt
historischer Bestand:

```text
contract_id:       browser.world.audiovisual.v1
presentation:      Canvas + AudioContext
capture:           Kamera + Mikrofon im Python-Server
status_for_Z4-A:   forbidden
```

Insbesondere duerfen nicht verwendet werden:

- `tools/controlled_browser_world/server.py`;
- dessen `/api/prepare`, `/api/start` oder Live-Koordinatoren;
- `OpenCVVideoFrameSource`;
- `SoundDeviceInputSource`;
- Bildschirmaufnahme ueber eine Kamera;
- Lautsprecherausgabe mit anschliessender Mikrofonaufnahme.

Die v1-Assets duerfen nur als statisch gelesene Herkunft der einfachen
Darstellungsparameter dienen. Ihre bisherigen Hashes werden nicht als
Digests der neuen Browserwelt ausgegeben.

## Neue getrennte Weltidentitaeten

### Referenz

```text
world_id:                 z4a.browser.direct.reference.v2
contract_id:              browser.world.direct.audiovisual.v2
visual_motion_axis:       horizontal
visual_motion_direction:  positive-first
tone_frequency_hz:        660
```

### Unabhaengige Kontrolle

```text
world_id:                 z4a.browser.direct.independent.v2
contract_id:              browser.world.direct.audiovisual.control.v2
visual_motion_axis:       vertical
visual_motion_direction:  positive-first
tone_frequency_hz:        990
```

Die Kontrollfrequenz ist mit dem vorab festen Faktor `1.5` aus der
Referenzfrequenz abgeleitet. Die orthogonale Bewegungsachse veraendert den
visuellen Verlauf, ohne Dauer, Zyklenzahl, Wegamplitude, Form, Farbe oder
Abtastbudget zu veraendern. Achse und Frequenz sind technische
Quellparameter, keine Labels fuer den Feldzustand.

## Gemeinsames Weltprogramm

Beide Welten verwenden exakt:

```text
canvas_css_width:          480 px
canvas_css_height:         480 px
canvas_backing_width:      480 px
canvas_backing_height:     480 px
device_scale_factor:       1
background_rgb:            32, 36, 40
square_rgb:                245, 247, 248
square_width:              86.4 px
square_height:             86.4 px
center_x:                  240 px
center_y:                  240 px
motion_amplitude:          144 px
movement_cycles:           3
oscillator_type:           sine
tone_gain:                 0.18
audio_channels:            1
```

Gebundene Phasen:

```text
0..7 s:    statisches Quadrat, Stille
7..14 s:   sinusfoermige Bewegung, Ton
14..35 s:  statisches Quadrat, Stille
```

In der Bewegungsphase gilt mit lokaler Zeit `u` in Sekunden:

```text
offset(u) = 144 * sin(2 * pi * 3 * u / 7)
```

Die Referenz addiert `offset` auf `center_x`, die Kontrolle auf `center_y`.
Am Anfang und Ende der Bewegungsphase liegt das Quadrat dadurch ohne Sprung
im Mittelpunkt.

## Deterministischer Browsermodus

Die v2-Welt erhaelt spaeter einen eigenen reinen Capture-Einstieg. Dieser
darf keine Benutzeroberflaeche und keinen Echtzeitlauf enthalten. Er muss:

- ausschliesslich lokale, spaeter hashgebundene HTML-, CSS- und
  JavaScript-Assets laden;
- einen frischen isolierten Browserkontext ohne Erweiterungen, Netzwerkzugriff
  oder persistentes Profil verwenden;
- Viewport und Device-Scale auf die gebundenen Werte setzen;
- Animation nicht durch `Date.now`, `requestAnimationFrame`, Bildschirmrate
  oder Fokuszustand fortschalten;
- fuer jeden gebundenen Abtasttick genau `renderVisualAt(tick_ns)` im
  Browserkontext aufrufen;
- erst nach dessen Abschluss das Canvas-Element als PNG durch den
  Browser-Rasterpfad erfassen;
- Audio ausschliesslich mit `OfflineAudioContext` im Browser berechnen;
- weder MediaDevices noch Systemaudio oder eine physische Ausgabe oeffnen.

Die spaetere Python-Seite darf keine Pixel oder Samples aus Phasenparametern
nachbauen. Sie darf nur die tatsaechlich aus dem Browser zurueckgegebenen
PNG-Bytes und PCM-Werte validieren, reduzieren und danach verwerfen.

Der verwendete Automationsadapter, seine Version, die Browserengine-Version
und der SHA-256-Hash des Browserbinaries muessen vor der technischen Abnahme
gebunden werden. Ein automatisches Browserupdate zwischen Referenz und
Wiederholung sperrt die Abnahme.

## Visuelle Browserausgabe

Die visuelle Abtastung ist fest:

```text
visual_rate_hz:            25
visual_interval_ns:        40000000
visual_frame_count:        875
sample_tick_ns(j):         40000000 * j, j = 0..874
field_support(j):          [40000000*j, 40000000*(j+1)]
pixel_format_after_decode: uint8 RGB
```

Die PNG-Erfassung umfasst nur das `canvas#world`, keine Controls, Texte,
Cursor oder Browserrahmen. Die decodierten Pixel muessen exakt die Form
`(480, 480, 3)` besitzen. Nach der Rezeptorreduktion werden PNG-Bytes und
Pixelarray verworfen.

Gebundener Rezeptor:

```text
receptor:             LocalChannelGridReceptor
source_width:         480
source_height:        480
grid_columns:         10
grid_rows:            8
channel_count:        3
carrier_count:        240
frames_per_second:    25
geometry_id:          visual.grid10x8.channels3.source480x480.v1
source_clock:         video.frame
sequence_clock:       z4a.browser.ns
```

`from_visual_receptor_state` erzeugt die inneren Frameintervalle `j..j+1`.
`OrganismTimedReceptorFrame.field_time` traegt den oben gebundenen
Nanosekunden-Support. Phasen-ID, Bewegungsachse, Frequenz und Welt-ID werden
nicht in `ReceptorContactFrame` uebernommen.

## Auditive Browserausgabe

Der Browser rendert je Welt genau einen monoauralen Puffer:

```text
audio_engine:              OfflineAudioContext
sample_rate:               48000 Hz
duration_samples:          1680000
duration_seconds:          35
oscillator_start_sample:   0
oscillator_stop_sample:    1680000
gain_schedule_samples:     0 -> 0.0, 336000 -> 0.18,
                           672000 -> 0.0, 1680000 -> 0.0
source_frame_size:         480 samples
source_frame_count:        3500
```

Der vollstaendige Puffer darf nur fluechtig im isolierten Browserkontext
existieren. Die Uebergabe an Python erfolgt in 480-Sample-Chunks in fester
Reihenfolge. Jeder Chunk wird unmittelbar in einen frischen
`BroadbandHearingPath` gegeben und danach verworfen.

Gebundener Rezeptor:

```text
receptor:             LogSpectralReceptor
sample_rate:          48000 Hz
window_size:          4800 samples
hop_size:             480 samples
min_frequency:        50 Hz
max_frequency:        18000 Hz
band_count:           48
geometry_id:          auditory.log48.50-18000.w4800.h480.v1
receptor_states:      3491
source_clock:         audio.sample
sequence_clock:       z4a.browser.ns
```

Fuer auditiven Rezeptorzustand `i = 0..3490` gilt:

```text
source_end_sample(i)      = 4800 + 480 * i
source_start_sample(i)    = source_end_sample(i) - 4800
field_end_ns(i)           = 100000000 + 10000000 * i
field_start_ns(i)         = field_end_ns(i) - 10000000
```

Damit liegt der erste auditive Abschluss-Support bei `90..100 ms`, der
letzte bei `34.99..35 s`. Das Analysefenster bleibt davon getrennt im
inneren `ReceptorContactFrame` erhalten.

Erwartete Kontaktverteilung fuer beide Frequenzen:

```text
active_zero:    2782
active_energy:   709
total:          3491
```

Die 709 aktiven Zustaende umfassen 700 tontragende Hops und neun
Nachlauf-Hops des ueberlappenden 100-ms-Rezeptorfensters. Diese neun
Uebergangszustaende duerfen nicht entfernt werden.

## Gemeinsame audiovisuelle Sequenz

Beide Modalitaeten verwenden `clock_id = z4a.browser.ns` und
`ticks_per_second = 1000000000`. Der gemeinsame technische Horizont ist
`0..35000000000 ns`.

Die Browserseite liefert keine gekoppelten Audio-Video-Paare. Der Adapter
erzeugt genau zwei eigenstaendige `ReceptorTimeSequence`-Objekte. Ihre realen
Abschlusszeiten werden erst durch den bestehenden selection-free Handoff zu
Abschlussgruppen zusammengefuehrt. Es gibt keine Interpolation, keine
Nachsynchronisierung und keine bevorzugte Modalitaet.

## Kanonische Bindungen

Der Weltvertragsdigest verwendet fuer die Referenz exakt folgende Payload:

```json
{
  "audio": {
    "channel_count": 1,
    "oscillator_type": "sine",
    "sample_rate": 48000,
    "source_frame_size": 480,
    "tone_frequency_hz": 660.0
  },
  "capture": {
    "external_network_allowed": false,
    "media_devices_allowed": false,
    "raw_retention": false,
    "writes_back": false
  },
  "contract_id": "browser.world.direct.audiovisual.v2",
  "phases": [
    {"duration_ns": 7000000000, "phase_id": "rest.before", "tone_gain": 0.0, "visual_mode": "static"},
    {"duration_ns": 7000000000, "phase_id": "change", "tone_gain": 0.18, "visual_mode": "moving"},
    {"duration_ns": 21000000000, "phase_id": "rest.after", "tone_gain": 0.0, "visual_mode": "static"}
  ],
  "visual": {
    "background_rgb": [32, 36, 40],
    "canvas_height": 480,
    "canvas_width": 480,
    "device_scale_factor": 1,
    "motion_amplitude_px": 144.0,
    "motion_axis": "horizontal",
    "motion_direction": "positive-first",
    "movement_cycles": 3,
    "sample_rate_hz": 25,
    "square_height_px": 86.4,
    "square_rgb": [245, 247, 248],
    "square_width_px": 86.4
  },
  "world_id": "z4a.browser.direct.reference.v2"
}
```

Fuer die unabhaengige Kontrolle werden ausschliesslich vier Werte ersetzt:

```text
contract_id:            browser.world.direct.audiovisual.control.v2
world_id:               z4a.browser.direct.independent.v2
audio.tone_frequency_hz: 990.0
visual.motion_axis:      vertical
```

Der Digest ist SHA-256 ueber JSON mit `sort_keys=True`,
`separators=(",", ":")`, `ensure_ascii=True`, `allow_nan=False` und
ASCII-Encoding. Keine Implementierungs-, Browser- oder Ergebnisvariable darf
die Payload ergaenzen oder verdeckt ueberschreiben.

Vor einer technischen Abnahme sind getrennt zu bilden:

1. Weltvertragsdigest fuer Referenz und Kontrolle;
2. SHA-256 jedes v2-Assets;
3. SHA-256 des Adaptermoduls;
4. Browserengine-Version und SHA-256 des Browserbinaries;
5. visueller Rezeptorsequenzdigest je Welt;
6. auditiver Rezeptorsequenzdigest je Welt;
7. gemeinsamer Digest mit
   `mcm_f3_receptor_sequences_digest((auditory, visual))`;
8. dieselben drei Rezeptordigests aus einem vollstaendig frischen
   Wiederholungskontext.

Kanonisches JSON verwendet `sort_keys=True`, `separators=(",", ":")`,
`ensure_ascii=True`, `allow_nan=False` und ASCII-Encoding. Roh-PNGs,
Pixelarrays, PCM-Puffer und vollstaendige Rezeptorsequenzen duerfen nicht in
einem Ergebnisartefakt persistiert werden.

## Abgeleitete Z4-A-Arme

Nach erfolgreicher Bindung gelten je Browserwelt die sechs bereits
vorregistrierten Arme:

- `reference`;
- `reproduction` aus frischem Browserkontext;
- `partitioned` mit identischen Rezeptorereignissen;
- `reversed` modalitaetsweise auf demselben Zeitraster;
- `permuted` modalitaetsweise in fester Vierblockfolge `0,3,2,1`;
- `independent` als vertikale 990-Hz-Kontrollwelt.

Umkehrung und Permutation arbeiten erst auf den gebundenen reduzierten
Wertevektoren. Sie starten keinen weiteren Browser und veraendern weder
Carrierreihenfolge noch Abschluss-Support.

## Technische Abnahmebedingungen

Z4-A2 ist erst technisch abgenommen, wenn ohne Forschungsnummer gilt:

- Referenz und Wiederholung verwenden identische Assets und dasselbe
  Browserbinary;
- je Welt entstehen exakt 875 visuelle und 3491 auditive Zustande;
- alle Werte sind endlich und liegen im jeweiligen Rezeptorbereich;
- alle Abschluss-Supports sind geordnet, nicht ueberlappend und innerhalb des
  35-Sekunden-Horizonts;
- Referenz und frische Wiederholung besitzen identische Modalitaets- und
  Gesamtdigests;
- Referenz und unabhaengige Kontrolle besitzen verschiedene visuelle,
  auditive und gemeinsame Digests;
- Observer an/aus veraendert keinen Zustandsdigest;
- kein Netzwerkrequest verlaesst den lokalen Assetursprung;
- keine Kamera-, Mikrofon-, MediaRecorder-, Systemaudio- oder
  Profilpersistenz wird geoeffnet;
- nach Reduktion bleiben keine Rohpixel- oder PCM-Artefakte bestehen.

Jede Abweichung sperrt W-B mit
`FIELD_ENCODER_NOT_TECHNICALLY_STABLE`. Feldwerte werden dann nicht erzeugt
oder interpretiert.

## Implementierte technische Scheibe 1

Die getrennten Assets unter `tools/z4a_browser_world_v2/` implementieren nur
die gebundenen direkten Browserfunktionen:

- `configureWorld(world_id)` fuer genau die beiden erlaubten Welten;
- `renderVisualAt(tick_ns)` ohne Uhr, Animationsloop oder Fokusabhaengigkeit;
- `renderAudio()` ausschliesslich ueber `OfflineAudioContext`;
- geordnetes Lesen von 480-Sample-Chunks und explizites Freigeben des
  Browserpuffers.

Der Adapter `mcm_field_organism/z4a_browser_receptor_adapter.py` akzeptiert
nur geordnete PNG-Bytes und monoaurale 480-Sample-Bloecke. Er reduziert jedes
Payload unmittelbar in den bestehenden visuellen beziehungsweise auditiven
Rezeptor, bindet die Nanosekunden-Supports und gibt erst nach exakt 875
visuellen Frames und 3500 Audiobloecken zwei getrennte
`ReceptorTimeSequence`-Objekte aus. Rohpixel und PCM werden nicht gespeichert
oder in den skalaren Receipt uebernommen.

Gebundene Dateidigestwerte:

```text
index.html:                         95be6df1af4bc01dafe4206b6f943e8d7ade1058aa6950eb6d67f55ccdb3a5b0
styles.css:                         30ea6308dacbfd35cc4244eb0d885966adafbf4b118ae26809a9aaf7452ec28e
world.js:                           4673545136bd55ee0174a191571e273f216be4593016add57f070032390d96a3
z4a_browser_receptor_adapter.py:    96b10c3ca3b7ebf5d710475669268069a6fd9946f077ba87c85657f071ed952e
```

Die fokussierte synthetische Abnahme bestand mit `4 passed`. Sie pruefte die
beiden exakten Weltvertraege, Assetinventar und verbotene Browser-APIs,
Fehlreihenfolgen sowie ein vollstaendiges synthetisches Inventar mit 875 PNGs,
3500 PCM-Bloecken, 875 visuellen und 3491 auditiven Rezeptorzustaenden. Die
verbundene Z4-A-Regression bestand mit `49 passed` und 6 Subtests. Diese
Abnahme startete keinen Browser und ist kein Forschungslauf.

## Implementierte technische Scheibe 2

`mcm_field_organism/z4a_playwright_capture.py` bindet die Uebergabe einer
bereits erzeugten Playwright-Seite, startet aber selbst keinen Browser. Der
Capture-Adapter erzwingt:

- einen validierten frischen, isolierten Kontext ohne persistentes Profil
  oder Erweiterungen bei exakt 480 x 480 und Device-Scale 1;
- ausschliesslich die drei digestgebundenen lokalen `file:`-Assets;
- technischen Stopp bei jedem versuchten nicht lokalen Request;
- Konfiguration genau einer der beiden gebundenen Weltidentitaeten;
- exakt 875 Aufrufe von `renderVisualAt(tick_ns)` mit anschliessender
  `canvas#world`-PNG-Erfassung;
- genau einen OfflineAudio-Render mit 1680000 Samples und 3500 geordnete
  Chunkuebergaben;
- Freigabe des browserinternen Audiopuffers auch nach Adapterfehler;
- einen ausschliesslich skalaren Receipt ohne PNG-, Pixel- oder PCM-Inhalt.

Gebundener Moduldigest:

```text
z4a_playwright_capture.py:          cdccb956bc873926b552724b96e6edbc4d25745a5c45ec8f77fb3bb6d5f29087
```

Die fokussierte Abnahme mit einer kontrollierten Fake-Seite bestand mit
`4 passed`. Geprueft wurden Preflight-Abweisung, Requeststopp vor Capture,
vollstaendige Aufrufreihenfolge und Audiopufferfreigabe nach Fehler. Die
verbundene Z4-A-Regression bestand mit `53 passed` und 6 Subtests. Playwright
ist in der aktuellen Umgebung nicht installiert; es wurde kein Browser
gestartet und keine echte Browserausgabe reduziert.

## Implementierte technische Scheibe 3

`mcm_field_organism/z4a_playwright_runtime_binding.py` bindet eine
Playwright-Installation ausschliesslich durch statische Dateizugriffe. Die
Bindung:

- liest die installierte Distributionsversion ueber `importlib.metadata`,
  ohne Playwright zu importieren;
- parst `browsers.json` als UTF-8-JSON und verlangt genau einen ausgewaehlten
  `chromium`- oder `chromium-headless-shell`-Eintrag;
- bindet `browserVersion` und numerische Revision aus dem Manifest;
- verweigert Symlinks, fehlende oder leere Dateien und einen Binarypfad
  ausserhalb der vorgegebenen Installationswurzel;
- bildet Manifest- und Binary-SHA-256;
- gibt nur Pfade, Versionen, Groesse und Digests aus und setzt
  `browser_started = false` fest.

Gebundener Moduldigest:

```text
z4a_playwright_runtime_binding.py:  768bda72785e357937f0333cec9fb44a81b1d91b3a5e292f0fbd8b4dc184a49b
```

Die fokussierte Abnahme mit einem synthetischen Installationsbaum bestand mit
`4 passed`. Geprueft wurden exakte Manifest-/Binarybindung, eindeutiger
versionierter Eintrag, Installationswurzel-Sperre, skalare JSON-Projektion und
geschlossenes Verhalten bei fehlender Distribution. Die verbundene
Z4-A-Regression bestand mit `57 passed` und 6 Subtests. Zu diesem
Zwischenstand war noch keine reale Runtime installiert oder gebunden und es
wurde kein Playwright- oder Browserprozess gestartet.

## Technische Scheibe 4: reale statische Runtimebindung

Die projektbezogene Datei `requirements-browser.txt` pinnt
`playwright==1.62.0` und bindet den vorhandenen Video-/OpenCV-Pfad ein. Die
Runtime wurde in `.venv` und die Browserartefakte wurden ausschliesslich in
den durch `.gitignore` ausgeschlossenen lokalen Pfad
`.playwright-browsers/` installiert. Die Installation startete keinen
Browser.

Die reale statische Bindung ergab:

```text
playwright_package_version:         1.62.0
manifest_entry:                     chromium-headless-shell
chromium_engine_version:            151.0.7922.34
browser_revision:                   1234
binary_size_bytes:                  211223552
manifest_sha256:                    f306eed529599b1eaf2f8a85db9de2b23e1a3fe36c2b66434b7c9434fb627a99
binary_sha256:                      ce4635cd0e5dc0e21494542a701f347e91c1f1d821970578d97ed8df4ced50ef
requirements_browser_sha256:        a5891f2a9d63f6dff91defebefb78b3ab5d8a31a441f18bcf1b2825d8ddc45d8
browser_started:                    false
```

Der Realpfad des Binaries liegt unter
`.playwright-browsers/chromium_headless_shell-1234/` und blieb innerhalb der
gebundenen Installationswurzel. Das Manifest wurde aus der gepinnten
Playwright-Distribution unter `.venv` gelesen. Es wurden keine PNGs,
Audiosamples oder Rezeptorsequenzen erzeugt.

## Technische Scheibe 5: realer Ein-Tick-Browser-Smoke

`mcm_field_organism/z4a_playwright_smoke.py` und
`tools/run_z4a_playwright_smoke.py` pruefen vor dem Start erneut Binarygroesse
und -digest, starten genau das gebundene Headless-Shell-Binary, erzeugen einen
isolierten 480-x-480-Kontext und lassen nur die lokalen v2-Assets zu. Der
Smoke konfiguriert die Referenzwelt, rendert ausschliesslich Tick 0, erfasst
ein Canvas-PNG fluechtig, prueft Signatur und dekodierte Dimensionen und
schliesst Kontext und Browser in derselben Playwright-Lebenszeit.

Gebundene Moduldigests:

```text
z4a_playwright_smoke.py:            532d4277998f27aca018f4135f1d8b7795d77e94bdda05bcc0bdcf8e946a3ce4
run_z4a_playwright_smoke.py:        16b729724a3cb81a1abb61c7b2acd068fc7d78b23b62fef11ed7d2ae3f8191b4
```

Der einmal ausgefuehrte reale technische Smoke ergab:

```text
engine_version_bound:               151.0.7922.34
engine_version_observed:            151.0.7922.34
rendered_tick_ns:                   0
canvas_width:                       480
canvas_height:                      480
png_size_bytes:                     1846
png_sha256:                         3950821c52c60e07c88da5cc8e5e264351d1bd797e286f23f10ccf7fc1db9af6
blocked_request_count:              0
raw_png_retained:                   false
browser_started:                    true
browser_closed:                     true
```

Die fokussierte synthetische Abnahme bestand mit `2 passed`; sie pruefte den
vollstaendigen Lifecycle und Binarydrift vor dem Start. Die verbundene
Z4-A-Regression bestand mit `59 passed` und 6 Subtests. Der reale Smoke ist
eine technische Browserabnahme ohne Laufnummer und kein Forschungslauf. Nach
Abschluss lief kein Prozess aus dem lokalen Playwright-Browserpfad.

## Technische Scheibe 6: realer OfflineAudio-Grenzsmoke

`mcm_field_organism/z4a_playwright_audio_smoke.py` und
`tools/run_z4a_playwright_audio_smoke.py` pruefen erneut die gebundene
Binaryidentitaet, starten einen isolierten lokalen Browserkontext und rendern
den 35-Sekunden-Puffer ausschliesslich ueber `OfflineAudioContext`. Aus dem
Browser werden nur Chunk 0 und Chunk 3499 uebertragen. Beide muessen genau
480 endliche Werte im normierten PCM-Bereich enthalten. Der vollstaendige
Puffer verbleibt im Browser und wird im Fehler- wie im Erfolgsfall vor dem
Schliessen freigegeben.

Gebundene Moduldigests:

```text
z4a_playwright_audio_smoke.py:      d0437abac9eb6d95c3122de7c7aefee2b2e0678fdf9f918b841a334ee70d17e0
run_z4a_playwright_audio_smoke.py:  d7536e82c7faa52a83aa09253712e74214bd347b318193f5b59118d6b53adbcf
```

Der einmal ausgefuehrte reale technische Audio-Smoke ergab:

```text
engine_version_bound:               151.0.7922.34
engine_version_observed:            151.0.7922.34
rendered_sample_count:              1680000
first_chunk_index:                  0
last_chunk_index:                   3499
first_chunk_size:                   480
last_chunk_size:                    480
first_chunk_max_abs:                0.0
last_chunk_max_abs:                 0.0
first_chunk_sha256:                 1dc97c1f08e1f166b19a01abdc939995c5003aed51417fc110a92f32e8ece339
last_chunk_sha256:                  6b66e26703a251767e6a6ea1fd2503913657d596852a30e241428309e852de8b
blocked_request_count:              0
audio_buffer_released:              true
raw_samples_retained:               false
browser_started:                    true
browser_closed:                     true
```

Beide Grenzchunks waren betragsmaessig exakt null. Ihre unterschiedlichen
Digests werden nur als technische Serialisierungswerte gefuehrt und nicht
inhaltlich interpretiert. Die fokussierte synthetische Abnahme bestand mit
`2 passed`, die verbundene Z4-A-Regression mit `61 passed` und 6 Subtests.
Der Audio-Smoke besitzt keine Laufnummer und ist kein Forschungslauf. Nach
Abschluss lief kein Prozess aus dem lokalen Playwright-Browserpfad.

## Verwendete Quellen

Lokaler Bestand:

- `mcm_field_organism/browser_world_contract.py`;
- `tools/controlled_browser_world/index.html`;
- `tools/controlled_browser_world/stimulus.js`;
- `tools/controlled_browser_world/server.py`;
- `mcm_field_organism/finite_video_path.py`;
- `mcm_field_organism/log_spectral_receptor.py`;
- `mcm_field_organism/receptor_contract.py`;
- `mcm_field_organism/receptor_time_alignment.py`.

Primaere technische Referenzen:

- Playwright-Dokumentation zur Erfassung von Seiten- und
  Element-Screenshots: https://playwright.dev/python/docs/screenshots
- MDN zu `OfflineAudioContext`:
  https://developer.mozilla.org/en-US/docs/Web/API/OfflineAudioContext
- MDN zu `AudioBuffer.getChannelData()`:
  https://developer.mozilla.org/en-US/docs/Web/API/AudioBuffer/getChannelData

Die Referenzen begruenden nur die technische Verfuegbarkeit der vorgesehenen
Browserbausteine. Ihre Eignung fuer dieses Projekt bleibt bis zur
Implementierung und technischen Abnahme offen.

## Aussagegrenze

Der Vertrag spezifiziert eine kontrollierte audiovisuelle Browserquelle und
ihren direkten technischen Rezeptorpfad. Er belegt keine Wahrnehmung,
Wiedererkennung, Praegung, Semantik, Organisation, relative Feldzeit, Memory
oder KI.

## Aktuelle Entscheidung

`Z4A2_OFFLINE_AUDIO_SMOKE_BOUND`

Statischer Vertrag, v2-Assets, direkter Reduktionsadapter, die getrennte
Playwright-Capture-Schicht, Runtime-Bindungsresolver, reale gepinnte
Playwright-/Chromium-Installation, visueller Ein-Tick-Smoke und
OfflineAudio-Grenzsmoke sind gebunden. Aktive visuelle/auditive
Weltunterscheidung, echte frische Browsersequenzdigests und die unabhaengige
Wiederholung bleiben offen; die Z4-A-Vollmatrix bleibt gesperrt.

## Bester naechster Schritt

Z4-A2 bleibt gemaess dem
[aktiven Richtungsentscheid](RICHTUNGSENTSCHEID_SUBSTRAT_VOR_MEMORYBEFUND.md)
am Stand `Z4A2_OFFLINE_AUDIO_SMOKE_BOUND` geparkt. Kein weiterer Smoke, kein
Vollcapture, keine Rezeptorsequenz und kein Lauf 197 werden gestartet, solange
der Substratzweig sie nicht fuer eine vorregistrierte Gegenbaseline benoetigt.
S0, S1-A und S1-B sind inzwischen gebunden. Der projektweite naechste Schritt
ist S2-C16 mit der kanonischen A8/B8-End-to-End-Komposition; Z4-A2 bleibt geparkt.
