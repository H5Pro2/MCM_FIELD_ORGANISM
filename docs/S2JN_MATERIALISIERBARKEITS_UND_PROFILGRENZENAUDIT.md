# S2-JN - Materialisierbarkeits- und Profilgrenzenaudit

## Status und Auftrag

`S2JN_STATIC_AUDIT_COMPLETE`

Gesamtbefund:

`S2JM_NOT_YET_MATERIALIZABLE_WITH_EXISTING_DIGITAL_ADAPTER_SET`

Dieser Audit prueft ausschliesslich statisch, ob die in S2-JM gebundene
quellenunabhaengige audiovisuelle Wahrnehmungsgrenze mit dem vorhandenen Code
ehrlich ausgefuehrt werden kann. Es wurden keine Module importiert, keine
Quellen geoeffnet und keine Rezeptor-, Memory-, Kontext- oder Feldfunktion
aufgerufen.

S2-JM bleibt als Schnittstellenvertrag fachlich konsistent. Der Befund sperrt
nur die Ausfuehrung mit dem gegenwaertigen Adapterbestand.

## Gebundene Quellen

| Quelle | SHA-256 |
| --- | --- |
| `docs/S2JM_QUELLENUNABHAENGIGE_AUDIOVISUELLE_WAHRNEHMUNGSGRENZE.md` | `6d47d65ff0316202bac01dcc3aa75c909916e5eb7a72e0ce6549239e96ae2575` |
| `mcm_field_organism/finite_video_path.py` | `d09cb6ba35fd061e4a243b7ed2112597a194e75abd026d7cc3ab7aa89922c07a` |
| `mcm_field_organism/log_spectral_receptor.py` | `26a6bd8f2d190db60c75ad29f275b3bd8b09b6d26d4ad54e4396176c4a36d2b0` |
| `mcm_field_organism/broadband_hearing_path.py` | `a20456b24c04d099ba5ee2da6250e3d83dc657392603c41d816b13ca68a37fb7` |
| `mcm_field_organism/receptor_contract.py` | `af565ce442aa56ade4b3b5d028692cccc93b481c299f1ff2d87ba840fdb6ee71` |
| `mcm_field_organism/receptor_time_model.py` | `268eaab0505c78f5053aa1f1671ec3a503fa080774a3fb71c4719c2239c596aa` |
| `mcm_field_organism/browser_payload_source.py` | `db4cee84c33e9ccdfc2ddee9a8bbeae5090cccf3370d0db0566af1a8564fa149` |
| `mcm_field_organism/browser_receptor_bridge.py` | `a00654efc655185538570a452302c2bf58e28cfb785e10bd39ca73104752ce20` |
| `mcm_field_organism/public_av_container_source.py` | `78ff998d5bb0cb0bb13321a45b9ee7e24002a77bd4b9896a8c48c29c84bdf31b` |
| `mcm_field_organism/controlled_audio_video_test_world.py` | `af677b52130f355dc24eb6b6ed0bcc9cfc204db94f2f7326ddebf5d6dcb85f5c` |
| `mcm_field_organism/live_video_adapter.py` | `0cfb4dcc4ffffe6b264746183a63f66c4fb99017791e24e47ce4b70359feaaee` |
| `mcm_field_organism/live_audio_adapter.py` | `92f2709b9b5fc7ac87bffce2c1e7e1422042f5b913b4e019981175f1660b876d` |
| `mcm_field_organism/_ppb1_receptor_profiles.py` | `28f3ce1de5b0ade465fffaa7dd3064eb51688cfea39ebb6c853cb4328bc0e5e0` |

Die Hashes binden nur den statisch gelesenen Stand. Sie sind keine
Funktionsabnahme.

## Profilgrenze

Das S2-JM-Profil ist das vorhandene `default-live`-Rezeptorprofil:

| Rolle | Default-Live |
| --- | --- |
| Bild | `1920 x 1080`, `RGB8`, `30 Hz` |
| visuelles Gitter | `12 x 8 x 3 = 288` Werte |
| Audio | `48000 Hz`, mono, Hop `480`, Fenster `4800` |
| auditive Filterbank | `48` Werte |
| gemeinsamer reduzierter Zustand | `288 + 48 = 336` Werte |

Die bisherige private Memorylinie verwendete das PPB-1-Profil `browser`:

| Rolle | Bisherige Memorylinie |
| --- | --- |
| Bild | `120 x 80`, `RGB8`, `30 Hz` |
| visuelles Gitter | `3 x 2 x 3 = 18` Werte |
| Audio | `8000 Hz`, mono, Hop `80`, Fenster `800` |
| auditive Filterbank | `8` Werte |
| gemeinsamer reduzierter Zustand | `18 + 8 = 26` Werte |

Die Rezeptorfunktion ist in beiden Profilen dieselbe, ihre Geometrie und ihr
Ressourcenbedarf sind es nicht. Insbesondere gilt:

- visuelle Wertzahl: Faktor `288 / 18 = 16`;
- gesamte AV-Wertzahl: Faktor `336 / 26`;
- bestehende B4-, TSPM-1- und PPB-1-Budgets der 26-Werte-Linie werden nicht
  auf das Default-Live-Profil uebertragen;
- kein S2-JM- oder S2-JN-Befund ist ein Nachweis, dass Memorybildung,
  Distanzen, Kapazitaet, Konsolidierung oder Abruf mit 336 Werten gueltig
  skaliert sind.

S2-JM bleibt deshalb eine Wahrnehmungsschnittstellenpruefung. Eine spaetere
Memoryskalierung benoetigt eine eigene Freigabe, eigene Ressourcenbudgets und
eigene funktionale Tests.

## Adapterinventar

### `BROWSER_VIEWPORT` und Browseraudio

Vorhanden sind `BrowserPayloadSourceConfig`, `capture_browser_payload_page`
und `BrowserReceptorBridge`.

Statisch belegt ist:

- der vorhandene Pfad erfasst `canvas#world`, nicht allgemein den gesamten
  Browser-Viewport;
- visuell wird PNG gelesen, mit OpenCV als BGR dekodiert und danach explizit
  nach RGB kanalvertauscht;
- die RGB-Matrix geht unmittelbar in `LocalChannelGridReceptor.analyze`;
- Audio wird als JavaScript-Zahlenfolge gelesen und unmittelbar als
  Float-Tupel an den Rolling-Rezeptor gegeben;
- die vorhandenen gebundenen Browserprofile verwenden `120 x 80`, acht
  auditive Werte und Hops zu 80 Samples;
- `BrowserReceptorSequenceBatch.digest()` bindet `contract_id` und
  `contract_digest` und ist daher kein quellenneutraler funktionaler Digest.

Befund: `PARTIAL_NOT_S2JM_CONFORMANT`.

Die Typen sind parametrisiert, aber es existiert kein gebundener Adapter, der
einen vollstaendigen Browser-Viewport als `CanonicalVisualFrameV1` und Audio
als `CanonicalPCMAudioHopV1` im Default-Live-Profil ausgibt. PNG-Decoding und
die reine BGR/RGB-Kanalpermutation koennen spaeter explizit vor der Grenze
gebunden werden; sie duerfen nicht im Rezeptor verborgen bleiben.

### `DESKTOP_CAPTURE` und `SYSTEM_AUDIO`

Im gebundenen Quellbestand existiert kein Eingangadapter fuer eine
Desktop-Pixelaufnahme und kein Loopback-/Systemaudioadapter.

`live_video_adapter.py` ist ein Kameraadapter. `live_audio_adapter.py` oeffnet
ein ausdrueckliches Eingabegeraet und ist damit ein Mikrofonpfad, kein
Systemaudio-Loopback.

Befund: `ABSENT`.

### `VIDEO_DECODE` und `VIDEO_AUDIO`

`decode_audited_public_av_sources` dekodiert eine begrenzte AV-Datei und
ignoriert Metadatenstroeme. Der aktuelle Rohpfad ist dennoch nicht
S2-JM-konform:

- Videoframes werden explizit als `bgr24` ausgegeben;
- es gibt keine gebundene verlustfreie BGR/RGB-Kanalpermutation zur
  kanonischen Grenze;
- exakte Geometrie `1920 x 1080` und `30 Hz` werden nicht erzwungen;
- Audio verwendet die native Samplerate des ersten Audiostroms;
- Mehrkanalaudio wird durch Mittelwertbildung reduziert;
- es gibt keine gebundene `PCM_F32LE`-Serialisierung und keine vollstaendige
  Bereichsbindung `[-1, 1]` vor der Rueckgabe;
- Resampling auf `48000 Hz` findet nicht statt und darf auch nicht implizit
  ergaenzt werden.

Befund: `NOT_S2JM_CONFORMANT`.

Ein spaeterer erster Gleichheitsversuch darf nur einen bereits passenden
verlustfreien AV-Container verwenden: `1920 x 1080 RGB8` nach reiner
Kanalpermutation, exakt 30 Frames/s sowie mono `48000 Hz` mit exakt gebundenem
Floatbereich. Jede andere Geometrie, Framerate, Kanalzahl oder Samplerate
stoppt fuer diesen Versuch fail-closed; es gibt dabei kein Resize, Downmix
oder Resampling.

### `SIMULATION_RENDER` und `SIMULATION_AUDIO`

`ControlledAudioVideoTestWorld` kann deterministisch `uint8`-RGB-Matrizen und
endliche Audio-Floatfolgen erzeugen. Seine Konfiguration ist typisiert und
grundsaetzlich parametrierbar. Das vorhandene gebundene Basisprofil verwendet
jedoch `24 x 16`, `6 x 4`, `10 Hz` und `4000 Hz` Audio.

Es fehlen die S2-JM-Huellen, die kanonische `PCM_F32LE`-Byteform, die
quellenneutrale funktionale Digestbildung und eine gebundene
Default-Live-Episode.

Befund: `MATERIALIZABLE_AFTER_CANONICAL_ADAPTER`.

Simulation ist die geeignete Referenzquelle fuer die spaetere digitale
Pruefung, ist im gegenwaertigen Stand aber noch kein fertiger S2-JM-Adapter.

### `CAMERA_CAPTURE` und `MICROPHONE_CAPTURE`

Kamera und Mikrofon bleiben wie in S2-JM vorgesehen ausserhalb der ersten
digitalen Pruefung. Der Kameraadapter liefert OpenCV-BGR, obwohl seine Form und
sein Typ zum Default-Live-Profil passen koennen. Der Mikrofonadapter kann mono
`float32` mit gebundener Samplerate und Blockgroesse anfordern. Beide benoetigen
spaeter trotzdem dieselben kanonischen Huellen wie digitale Quellen. Dieser
Audit nimmt sie nicht ab.

## Transformationsgrenze

Fuer die erste digitale Episode sind nur folgende verlustfreien technischen
Schritte vor der kanonischen Grenze zulaessig:

1. verlustfreies PNG-Decoding zu drei `uint8`-Kanaelen;
2. reine BGR/RGB-Kanalpermutation ohne Farbprofil- oder Werteumrechnung;
3. Serialisierung bereits gebundener mono Float32-Samples als
   Little-Endian-Bytes ohne Wertumrechnung.

Gesperrt sind:

- Resize, Crop, Letterbox, Padding und jede Interpolation;
- YUV/RGB- oder profilbasierte Farbumrechnung;
- Gamma-, Pegel-, Kontrast- oder Helligkeitskorrektur;
- Downmix, Resampling, Dithering, Normalisierung und Sample-Reparatur;
- Frameverdopplung, Frameauslassung oder Zeitinterpolation;
- Ersatz fehlender Daten durch Nullen oder den letzten gueltigen Wert.

Eine Quelle, die nicht bereits bis auf die drei erlaubten verlustfreien
Schritte dem Zielprofil entspricht, ist fuer diese erste Pruefung unzulaessig.

## Quellenneutrale Funktionsformen

Die vorhandenen reduzierten Typen `VisualReceptorState`,
`AuditoryReceptorState`, `ReceptorContactFrame`,
`OrganismTimedReceptorFrame` und `ReceptorTimeSequence` enthalten keine
Quellklasse. Geometrie, Modalitaet, Position, Zeit, Carrier und Werte sind
funktionale Rollen.

Nicht als quellenneutral verwendbar ist der vorhandene
`BrowserReceptorSequenceBatch`-Digest, weil dessen kanonische Form den
Browservertrag bindet.

Vor einer Ausfuehrung werden deshalb zwei noch nicht implementierte,
quellenneutrale Digestrollen benoetigt:

- `CanonicalAVInputSequenceDigestV1`: nur Episode, gemeinsame Uhr,
  kanonische Payloaddigests, Indizes, Geometrie und Zeitfenster;
- `CanonicalReducedReceptorSequenceDigestV1`: nur Modalitaet, Rezeptorprofil,
  Geometrie, Zeit, Carrier und reduzierte Werte.

Quellklasse, Adapterdigest und native Payloadprovenienz muessen ausserhalb
dieser beiden Formen bleiben. Sie duerfen nur in `SourceAuditProvenanceV1`
stehen. Damit ist die Digesttrennung konzeptionell materialisierbar, im
aktuellen Code aber noch nicht vorhanden.

## Gebundene digitale Referenzepisode

Die spaetere, separat freizugebende Episode `s2jn.digital.av.episode.v1` dauert
exakt `200 ms` auf einer Uhr mit `1.000.000.000` Ticks/s.

### Visuelle Folge

- sechs Frames bei `30 Hz`;
- jeder Frame besitzt exakt `1920 x 1080 x 3` zusammenhaengende RGB8-Bytes;
- Hintergrund jedes Frames: RGB `(16, 32, 48)`;
- ein Vordergrundrechteck belegt exakt eine Rezeptorzelle von `160 x 135`
  Pixeln und besitzt RGB `(224, 64, 32)`;
- in Frame `i` fuer `i = 0..5` liegt das Rechteck in Zeile `2`, Spalte `i`;
- Zeitfenster: `floor(i * 1e9 / 30)` bis
  `floor((i + 1) * 1e9 / 30)`.

Die Pixelbytes sind die Fixture. Positionen, Farben und Frameindex sind keine
Labels fuer den Rezeptor.

### Auditive Folge

- 20 Hops zu je 480 mono Float32-Samples bei `48000 Hz`;
- jeder Hop besteht aus 120 Wiederholungen der exakt darstellbaren Folge
  `(0.0, 0.5, 0.0, -0.5)`;
- kanonische Serialisierung ausschliesslich `PCM_F32LE`;
- Zeitfenster fuer Hop `i`: `i * 10.000.000` bis
  `(i + 1) * 10.000.000` Ticks.

Der Rolling-Rezeptor erzeugt nach dem zehnten Hop seinen ersten Zustand und
danach je Hop einen weiteren: insgesamt elf auditive Zustande. Zusammen mit
sechs visuellen Zustaenden entstehen je Quellenarm exakt 17 reduzierte
Zustaende.

## Ressourcenbudget

### Payload- und Speichergrenzen

| Rolle | Je Quellenarm | Vier Quellenarme |
| --- | ---: | ---: |
| ein RGB8-Frame | `6.220.800` Byte | nicht gleichzeitig gehalten |
| sechs RGB8-Frames verarbeitet | `37.324.800` Byte | `149.299.200` Byte |
| ein PCM-Hop | `1.920` Byte | nicht gleichzeitig gehalten |
| 20 PCM-Hops verarbeitet | `38.400` Byte | `153.600` Byte |
| gesamtes Rohpayloadvolumen | `37.363.200` Byte | `149.452.800` Byte |
| gepackte reduzierte Float64-Werte | `18.048` Byte | `72.192` Byte |

Die vier Quellenarme werden nacheinander verarbeitet. Der funktionale
Rohpayload-Owner darf gleichzeitig hoechstens einen RGB-Frame und einen
PCM-Hop halten, also `6.222.720` Byte. Decoder-, Treiber- und
Bibliothekspuffer sind getrennte tatsaechliche Laufzeitressourcen und muessen
spaeter gemessen werden; sie werden nicht als kostenlos behauptet.

Persistente Rohpayloadbytes: exakt `0`.

Kanonische Plaene, Payloaddigests, reduzierte Werte, Zeitformen,
Auditprovenienz und Fehlerbelege erhalten eine harte Obergrenze von `524.288`
Byte je Arm und `2.097.152` Byte fuer alle vier Arme. Eine Ueberschreitung
macht den spaeteren Versuch `NOT_EVALUABLE`; die Grenze darf Rohdaten nicht
durch Kompression oder Einbettung verstecken.

### Operationsbudget

Jeder der vier Quellenarme besitzt exakt 55 Top-Level-Operationen:

- eine Quellenoeffnung;
- sechs visuelle Kanonisierungsschritte;
- 20 auditive Kanonisierungsschritte;
- sechs visuelle Rezeptoraufrufe;
- 20 auditive Rezeptor-Pushes;
- eine vollstaendige Inventarpruefung;
- einen Quellenabschluss.

Das ergibt `4 * 55 = 220` Quellenoperationen.

Die quellenuebergreifende Pruefung verwendet Simulation als technische
Referenz und bindet zusaetzlich:

- `3 * 26 = 78` positionsgleiche kanonische Payloadvergleiche;
- `3 * 17 = 51` positionsgleiche reduzierte Zustandsvergleiche;
- eine abschliessende Ledgerpruefung.

Vollstaendiges Maximalbudget: exakt `220 + 78 + 51 + 1 = 350`
Top-Level-Operationen. Ein frueher Fail-Closed-Stopp erzeugt nur das gueltige
Praefix; er darf nicht auf 350 aufgefuellt oder fortgesetzt werden.

Dieses Budget autorisiert keinen Runner, Recorder oder Test.

## Gleichheits- und Entscheidungsregel

Browser, Desktop, Video und Simulation duerfen nur fuer eine konkrete
Position als bitgleiche Quellen verglichen werden, wenn folgende funktionale
Rollen uebereinstimmen:

- RGB- beziehungsweise PCM-Payloaddigest;
- Index und Zeitfenster;
- Episode, Uhr und Geometrie;
- vollstaendiges positionsgleiches Inventar.

Unterschiedliche Auditprovenienz ist zulaessig und erwartet. Bereits eine
abweichende kanonische Payloadposition beendet die betreffende
Quellengleichheitsaussage als `PAYLOADS_DIFFER`; sie ist weder ein
Rezeptorfehler noch ein negativer Quellenunabhaengigkeitsbefund.

Nur bei bitgleichen kanonischen Folgen wird geprueft, ob die identischen
Rezeptorfunktionen bitgleiche reduzierte Zustandsfolgen liefern. Ein
Unterschied dann waere eine echte Falsifikation der S2-JM-Grenze.

## Materialisierungsblocker

`JN-B01 - CANONICAL_BOUNDARY_TYPES_ABSENT`

Die beiden kanonischen Eingangsformen und ihre quellenneutralen Digests sind
noch nicht implementiert.

`JN-B02 - DIGITAL_SOURCE_COVERAGE_INCOMPLETE`

Desktopaufnahme und Systemaudio besitzen keinen Adapter im gebundenen
Quellbestand.

`JN-B03 - EXISTING_ADAPTER_PROFILES_OR_TRANSFORMS_DIFFER`

Browser, Public-AV und Simulation verwenden aktuell andere gebundene Profile
oder geben PNG, BGR, JavaScript-Floats beziehungsweise native Containerwerte
statt der exakten S2-JM-Form aus.

`JN-B04 - FUNCTIONAL_DIGEST_NOT_SOURCE_NEUTRAL_END_TO_END`

Die reduzierten Rezeptortypen sind quellenneutral, der vorhandene
Browser-Batchdigest ist es nicht. Ein gemeinsamer quellenneutraler
Episodendigest fehlt.

Alle vier Blocker muessen vor einer digitalen Ausfuehrungsfreigabe geschlossen
sein. Keiner wird durch Hashgleichheit von Quellcode oder durch theoretische
Parametrierbarkeit ersetzt.

## Schlussbefund

S2-JM ist technisch plausibel, aber mit dem bestehenden digitalen
Adapterbestand nicht vollstaendig materialisiert. Der kleinste ehrliche
naechste Implementierungsschritt waere eine gemeinsame private kanonische
Grenze samt Simulationreferenz sowie getrennte Browser-, Desktop-, Video- und
Systemaudioadapter. Diese Arbeit ist durch S2-JN nicht freigegeben.

Das Default-Live-Profil bleibt strikt von der bestaetigten 26-Werte-
Memorylinie getrennt. Es wurden keine Memoryskalierung, kein Feldpfad und keine
Livequelle geprueft oder freigegeben.
