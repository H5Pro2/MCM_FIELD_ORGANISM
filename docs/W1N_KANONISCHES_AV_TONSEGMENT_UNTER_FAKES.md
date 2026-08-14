# W1-N: Kanonisches AV-Tonsegment unter Fakes

Stand: 2026-08-07

Entscheidung: `W1N_CANONICAL_AUDIO_SEGMENT_IMPLEMENTED_UNDER_FAKES`

Forschungslauf: nein

Realer Browser gestartet: nein

## Auftrag

W1-N korrigiert die in W1-M nachgewiesene Energieabweichung konstruktiv.
Die Toleranz wird nicht nachtraeglich gelockert. Statt zwei unabhaengig
phasengesteuerte Oszillatorsignale zu rendern, verwenden A0 und C0 exakt
dieselbe lokale Sampleform und unterscheiden nur deren Position im
9600-Sample-Puffer.

## Getrennte neue Testquelle

Die bereits real belegten W1-H- und W1-M-Assets bleiben unveraendert. W1-N
legt eine neue Quelle an:

```text
tools/controlled_av_canonical_audio_world/index.html
tools/controlled_av_canonical_audio_world/styles.css
tools/controlled_av_canonical_audio_world/world.js
```

Gebundene Digests:

```text
index.html: 0ceecd1e9e346ce262e8e0cb41efe52fe2f3e42e00c1d6298fdf23becc451d3b
styles.css: f026fce8f826fb7364a11b1b05ad4acb3dd37aed7dede5453c6f82cbf497b594
world.js:   7e903402e16f3f11423116ab3112d452c3815fb6006ed18537963fd887c956bb
```

## Kanonische Samplebildung

Die Quelle berechnet fuer die einzige aktive 300-ms-Phase genau 2400 lokale
Samples:

```text
sample(local_index)
= tone_gain
* sin(2 * pi * tone_frequency_hz * local_index / sample_rate)
```

Entscheidend ist `local_index`: A0 und C0 beginnen die Sinusform jeweils bei
lokalem Index null. Danach werden dieselben Werte eingesetzt:

```text
A0: canonical_segment -> [2400, 4800)
C0: canonical_segment -> [4800, 7200)
```

Der gesamte Float32-Puffer wird weiterhin ueber einen lokalen
`OfflineAudioContext` und `AudioBufferSourceNode` gerendert. Es gibt keinen
`OscillatorNode` und keine zweite phasenabhaengige Tonberechnung.

## Unveraenderte Grenzen

- 120 x 80 Canvas;
- 30 visuelle Frames/s;
- 8000 Audio-Samples/s;
- 80 Samples pro PCM-Hops;
- 36 visuelle PNGs;
- 120 PCM-Hops und 9600 Samples;
- 36 visuelle und 111 auditive Rezeptorzustaende;
- keine Kamera, kein Mikrofon und kein Netzwerk;
- keine Rohpayloadhaltung;
- kein Feldhandoff in der Quellenabnahme;
- Energiegrenze weiterhin `1e-12`.

## Diagnosebindung

`controlled_av_source_pair_diagnostic.py` behaelt den historischen W1-M-Pfad
mit seinen alten Assetdigests. Zusaetzlich bindet
`run_controlled_av_canonical_source_pair_diagnostic()` die neue Quelle unter
der eigenen Identitaet:

```text
controlled.av.canonical-source-pair.diagnostic.v1
```

Damit werden historische Diagnose und korrigierte Quelle nicht vermischt.

## Fake-Abnahme

Die W1-N-Tests bestaetigen:

- exakte neue Assetdigests;
- ASCII-only Assets;
- lokale Sampleerzeugung ueber `localIndex`;
- Verwendung von `OfflineAudioContext` und `createBufferSource`;
- Abwesenheit von `createOscillator`, Kamera, Netzwerk und externem Zustand;
- gleiche visuelle Sequenz;
- Audioenergiegleichheit innerhalb der unveraenderten `1e-12`-Grenze;
- `SOURCE_INVARIANTS_MATCH` fuer das kanonische Fake-Paar;
- kein Feldhandoff und keine Rohpayloadhaltung;
- unveraenderten historischen W1-M-Diagnosepfad als Regression.

Der fokussierte Verbund besteht mit `29 passed`. Die bekannte
Pytest-Cachewarnung `WinError 183` betrifft nur den lokalen Cachepfad.

## Regulatorische Einordnung

W1-N implementiert keine sensorische Selbstregulation. Die bestehende
Regulationsarchitektur bleibt auf E0 und ohne Rueckschreibung.

Die weitere Reihenfolge wird jedoch praezisiert:

```text
kanonische Quellenangleichung
-> reale Quellenabnahme
-> gueltiger Zeitkopplungs-Feldvergleich
-> kontrollierte Ueberlastungs- und Erholungscharakterisierung
-> erst danach Regulationskandidat und Memory-Nachweise
```

Damit kann spaetere Sattigung nicht als Praegung fehlinterpretiert werden.
Ein Regulationskandidat muss lokal, spaeter wirksam, begrenzt und reversibel
sein und gegen feste Gain-, Clipping-, AGC- und Leaky-Baselines bestehen.

## Aussagegrenze

W1-N belegt die neue Quelle nur unter Fakes und statischer Assetpruefung. Es
gibt noch keinen realen Nachweis, dass `OfflineAudioContext` die kanonisch
eingesetzten Puffer an beiden Positionen bit- oder energiegleich ausgibt.

W1-N belegt weder Feldwirkung noch Ueberreizung, Regulation, Nachhall,
Feldzeit, Praegung, Memory, Organisation, Semantik, Selbstregulation oder KI.

## W1-N-Entscheidung

```text
neue getrennte AV-Quelle:          implementiert
kanonisches Tonsegment:            implementiert
nur Sampleposition variiert:       ja
Energietoleranz gelockert:         nein
alte Assets veraendert:            nein
Fake-Quellenpaar:                  bestanden
relevanter Verbund:                29 passed
realer Browserstart:               nein
Forschungslauf:                    nein
```

## Bester naechster Schritt

W1-O bindet ein schleifenfreies Einmalwerkzeug an die neue kanonische Quelle
und fuehrt genau eine reale Quellenpaardiagnose ohne Feldhandoff aus. Nur wenn
visuelle Sequenz und Audioenergie die unveraenderten Grenzen bestehen, darf
spaeter ein neuer Feldpaar-Smoke vorregistriert werden.
