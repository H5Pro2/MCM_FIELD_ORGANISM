# S2-JP - Video-/PCM-Quellenauswahl und Materialisierungsvertrag

## Status und Grenze

`S2JP_STATIC_CONTRACT_COMPLETE`

Ausfuehrungsstatus:

`VIDEO_DECODE_PATH_BLOCKED_PENDING_CAPABILITY_AND_CONTAINER_EVIDENCE`

Dieser Vertrag waehlt genau eine zweite digitale Quellklasse fuer den spaeteren
Vergleich mit der qualifizierten S2-JO-Simulation:

```text
VIDEO_DECODE + VIDEO_AUDIO
```

Er definiert Auswahl, Materialisierung, Gleichheitspruefung und Stopplogik. Er
implementiert keinen Adapter, erzeugt oder oeffnet keinen Container und ruft
weder Decoder noch Rezeptor, Memory, Kontext oder Feld auf.

Desktop, Browser, Kamera, Mikrofon und Systemaudio bleiben gesperrt. S2-JP
schliesst `JN-B03` noch nicht. Die Schliessung setzt einen spaeteren positiven
Faehigkeitsbeleg und einen konkret gebundenen verlustfreien Container voraus.

## Gebundene Quellen

| Quelle | SHA-256 |
| --- | --- |
| `docs/S2JM_QUELLENUNABHAENGIGE_AUDIOVISUELLE_WAHRNEHMUNGSGRENZE.md` | `6d47d65ff0316202bac01dcc3aa75c909916e5eb7a72e0ce6549239e96ae2575` |
| `docs/S2JN_MATERIALISIERBARKEITS_UND_PROFILGRENZENAUDIT.md` | `f1ea13b45fb71d6af011d411ca30e3a6c6388bff8217b90a45f9ff76876e935a` |
| `reports/s2jo/S2JO_SIMULATION_REFERENZ_QUALIFIKATION.md` | `1b7f7f0c18d92bddbc588cd4f87deb02a8191ec719de3ba1177153ba3ec37674` |
| `tools/_s2jo_private_canonical_av_boundary.py` | `50a39fb3865fbd11b3577f79db2983f9dd3260262dee0f199ae5f884bed4ef71` |
| `mcm_field_organism/public_av_container_source.py` | `78ff998d5bb0cb0bb13321a45b9ee7e24002a77bd4b9896a8c48c29c84bdf31b` |
| `mcm_field_organism/public_media_source_contract.py` | `57b9c1c69f99032db892389a85a9d839130ff9409d492066660b373d67dfc5e8` |
| `requirements-public-av.txt` | `0858f45460e62e149fe7e2c8e3ff587c188e92ccbc3df5bef23e96a397834a12` |
| `.venv/Lib/site-packages/av-16.1.0.dist-info/METADATA` | `2afaca0789ddf1c3b225d722aea306281435489e5ef4cfd7b66d09ac9d4d5a8c` |
| `.venv/Lib/site-packages/av-16.1.0.dist-info/RECORD` | `cb43f848d1f0bddb0683ec30586c646933883205ad7d7853e9c1c04ae2bbba35` |

Die Umgebungsmetadaten belegen PyAV `16.1.0` und dessen Bindung an
FFmpeg-Bibliotheken. Sie belegen statisch nicht, dass die konkrete
NUT-/rawvideo-/PCM-Kombination in diesem Build als Muxer, Demuxer, Encoder und
Decoder verfuegbar ist. Ein Paketversionshash ersetzt keinen Faehigkeitsbeleg.

## Ausgewaehlter Containerpfad

Einziger zulaessiger Kandidat ist:

| Rolle | Verbindliche Form |
| --- | --- |
| Container | endliche NUT-Datei |
| Videocodec | `rawvideo` |
| Videopixelformat | `rgb24` |
| Bildform | `1920 x 1080`, drei Kanaele, zusammenhaengendes RGB8 |
| Bildrate | exakt `30/1` |
| Bildanzahl | exakt `6` |
| Audiocodec | `pcm_f32le` |
| Audiosampleformat | gepacktes Float32, Little Endian |
| Audiokanaele | exakt `1` |
| Samplerate | exakt `48000 Hz` |
| Sampleanzahl | exakt `9600`, aufgeteilt in `20 x 480` |
| Episodendauer | exakt `200 ms` |

NUT ist nur die ausgewaehlte Transporthuelle. Funktional relevant bleiben
ausschliesslich die kanonischen RGB8- und PCM_F32LE-Payloads mit ihrer Zeit-
und Geometriebindung. Containername, Decodername, Bibliotheksversion,
Dateipfad und Dateidigest gehoeren nur in `SourceAuditProvenanceV1`.

Der Kandidat wurde gewaehlt, weil `rawvideo/rgb24` und `pcm_f32le` keine
verlustbehaftete Kodierung benoetigen. FFV1, YUV-Formate, H.26x, VPx, AV1,
AAC, Opus und andere komprimierte oder farbraumwandelnde Pfade sind fuer
diesen Bitgleichheitsversuch ausgeschlossen.

## Referenzepisode

Die Nutzdaten muessen positionsgleich der bereits qualifizierten S2-JO-
Episode entsprechen:

- sechs `CanonicalVisualFrameV1`-Frames mit je `6.220.800` RGB8-Bytes;
- 20 `CanonicalPCMAudioHopV1`-Hops mit je `480` mono Float32-Samples und
  `1.920` kanonischen Little-Endian-Bytes;
- sechs visuelle und elf auditive reduzierte Rezeptorzustaende;
- identische Frame-, Hop-, Uhr-, Geometrie- und Episodenbindungen;
- gesamtes kanonisches Rohpayloadvolumen `37.363.200` Byte.

Die S2-JO-Payloaddigests sind die spaetere Vergleichsreferenz. Ein Container
darf erst als Fixture gebunden werden, wenn sein Erzeugungsplan, Dateidigest,
Dateigroesse, Streaminventar und alle 26 dekodierten Payloaddigests vor der
Vergleichsausfuehrung feststehen. Die Containererzeugung ist nicht Teil des
spaeteren Vergleichslaufs und wird durch S2-JP nicht freigegeben.

## Transformationsgrenze

Der spaetere Video-/PCM-Adapter darf ausschliesslich:

1. den gebundenen NUT-Container lesen;
2. `rawvideo` ohne Skalierung oder Farbraumumrechnung dekodieren;
3. bereits vorliegendes `rgb24` unveraendert uebernehmen;
4. falls der Decoder dieselben Bytes lediglich als `bgr24` ausweist, genau
   eine explizite BGR/RGB-Kanalpermutation ausfuehren;
5. gepacktes mono `pcm_f32le` ohne Wertumrechnung lesen;
6. die 9600 Samples positionsgleich in 20 Hops zu je 480 Samples teilen;
7. die kanonischen S2-JO-Huellen und getrennte Auditprovenienz bilden.

Verboten sind insbesondere:

- Resize, Crop, Padding, Interpolation oder Frameersatz;
- YUV/RGB-, Gamma-, Profil- oder sonstige Farbwertumrechnung;
- Alphaentfernung, wenn der Stream nicht bereits exakt drei Kanaele besitzt;
- Downmix, Kanalwahl, Resampling, Dithering, Normalisierung oder Clipping;
- Float64-Zwischenwerte mit anschliessender Rueckkonvertierung;
- Zeitinterpolation, Frameverdopplung oder Auslassen von Frames/Samples;
- toleranter Vergleich, Rundung oder Schwellennachbesserung.

Jede Bibliotheksfunktion, die `swscale` oder `swresample` fuer die funktionale
Nutzlast einsetzen wuerde, ist in diesem Versuch unzulaessig. Die reine
Kanalpermutation muss als eigener werttreuer Schritt sichtbar bleiben.

## Bestandsaudit des vorhandenen Decoders

`public_av_container_source.py` ist nicht S2-JP-konform und darf fuer den
spaeteren Vergleich nicht unveraendert verwendet werden:

- Video wird durch `to_ndarray(format="bgr24")` auf eine angeforderte
  Ausgabeform gebracht; eine nachweislich reine Kanalpermutation zur
  kanonischen RGB8-Form fehlt.
- Geometrie, Bildrate, Bildanzahl und exakte Streamform des S2-JP-Plans werden
  nicht vollstaendig erzwungen.
- Audio wird in `float64` ueberfuehrt.
- Zweidimensionales Audio wird per Mittelwert zu mono gemischt.
- `PCM_F32LE`, exakt ein Kanal, exakt 48000 Hz und die gebundene Hopteilung
  werden nicht als unveraenderliche Eingangsgrenze belegt.

Damit existiert im Projekt derzeit kein bereits abgenommener Adapter, der den
ausgewaehlten Pfad ohne verbotene Umwandlung bis zur S2-JO-Grenze fuehrt.

## Erforderlicher Faehigkeitsbeleg

Vor jeder Implementierung muss ein separat freigegebener, enger Preflight
fail-closed bestaetigen:

- NUT-Muxer und -Demuxer sind im konkret gebundenen Build vorhanden;
- `rawvideo` kann exakt als `rgb24` geschrieben und gelesen werden;
- `pcm_f32le` kann gepackt, mono und mit 48000 Hz geschrieben und gelesen
  werden;
- Streamparameter sind vor dem ersten funktionalen Decode pruefbar;
- der Decodepfad benoetigt weder `swscale` noch `swresample`;
- genau ein Video- und ein Audiostrom liegen vor; Untertitel-, Daten-,
  Attachment- und weitere AV-Stroeme fehlen;
- die endliche Containerdatei bleibt unter `67.108.864` Byte;
- alle sechs Frames und 9600 Samples werden vollstaendig und in Reihenfolge
  dekodiert.

Fehlt bereits eine dieser Eigenschaften, lautet der Befund
`VIDEO_DECODE_PATH_UNAVAILABLE`. Dann endet S2-JP ohne Adapterimplementierung,
ohne Toleranzregel und ohne Auswahl eines Ersatzcodecs im selben Schritt.

## Positionsweiser Gleichheitsnachweis

Ein spaeterer Vergleich ist nur in dieser Reihenfolge auswertbar:

1. Container- und Streamplan gegen den vorab gebundenen Auditbeleg pruefen.
2. Sechs dekodierte RGB8-Payloaddigests positionsweise gegen S2-JO pruefen.
3. Zwanzig dekodierte PCM_F32LE-Payloaddigests positionsweise gegen S2-JO
   pruefen.
4. Quellneutralen funktionalen AV-Episodendigest vergleichen.
5. Dieselben unveraenderten visuellen und auditiven Rezeptoren aufrufen.
6. Sechs visuelle und elf auditive Zustandsdigests positionsweise vergleichen.
7. Quellenneutralen reduzierten Rezeptorsequenzdigest vergleichen.

Schon ein abweichendes Pixel oder Sample ergibt `PAYLOADS_DIFFER` und stoppt
vor einer Rezeptorgleichheitsaussage. Es gibt keine Toleranz. Sind alle
Payloads bitgleich, aber reduzierte Zustaende verschieden, ist die
quellenneutrale Rezeptorgrenze falsifiziert.

Unterschiedliche gueltige Auditprovenienzdigests sind erwartet und duerfen
weder funktionalen Episodendigest noch Rezeptorzustaende beeinflussen.

## Lauf- und Ressourcenrahmen

Der spaetere zweite Quellenarm besitzt hoechstens 57 Top-Level-Operationen:

- eine Dateiintegritaetspruefung;
- eine Containeroeffnung;
- eine Stream- und Profilpruefung;
- sechs Video-Decode-/Kanonisierungsschritte;
- 20 Audio-Decode-/Kanonisierungsschritte;
- sechs visuelle Rezeptoraufrufe;
- 20 auditive Rezeptor-Pushes;
- eine Inventarversiegelung;
- einen Quellenabschluss.

Der Vergleich mit dem qualifizierten S2-JO-Arm bindet zusaetzlich:

- 26 positionsweise Payloadvergleiche;
- 17 positionsweise Rezeptorzustandsvergleiche;
- eine abschliessende Ledgerpruefung.

Damit gilt fuer eine spaetere Zwei-Quellen-Pruefung das feste Maximum:

```text
55 S2-JO-Operationen + 57 Video-/PCM-Operationen + 44 Vergleiche = 156
```

Es duerfen gleichzeitig hoechstens ein kanonischer Frame und ein kanonischer
Hop als funktionale Nutzlast gehalten werden: `6.222.720` Byte. Decoder- und
Containerpuffer sind getrennt als tatsaechliche Laufzeitressourcen zu messen.
Sie sind nicht Teil des funktionalen Payloadbudgets und nicht kostenlos.

Persistente Pixel-, PCM- und Decoderpufferbytes im Ergebnis: exakt `0`.
Ergebnisse duerfen nur Plaene, Digests, Streamparameter, reduzierte Werte,
Auditprovenienz, Ledger und Fehlerbelege enthalten.

## Digest- und Rollenfolge

Die spaetere Beweiskette bleibt vorwaertsgerichtet:

```text
S2JOReferenceBinding
-> VideoContainerPlan
-> ContainerCapabilityReceipt
-> BoundContainerReceipt
-> StreamInventoryReceipt
-> CanonicalPayloadReceipts[26]
-> CanonicalAVEpisodeReceipt
-> ReducedReceptorReceipts[17]
-> ReducedSequenceReceipt
-> CrossSourceComparisonReceipt
```

`SourceAuditProvenanceV1` bindet Container-, Decoder- und Adapteridentitaet an
die jeweiligen Quellenreceipts, ist aber kein Elternteil der funktionalen
Payload- oder Rezeptordigests. Kein spaeteres Vergleichsergebnis darf eine
fruehere Quelle, Fixture oder Faehigkeit autorisieren.

## Stopplogik und Schlussbefund

S2-JP stoppt statisch vor der Implementierung, weil aktuell zwei notwendige
Belege fehlen:

1. ein konkreter Faehigkeitsbeleg des installierten PyAV-/FFmpeg-Builds fuer
   NUT, `rawvideo/rgb24` und `pcm_f32le` ohne Konvertierung;
2. ein vorab erzeugter und digestgebundener endlicher Container, dessen 26
   dekodierte Payloadpositionen bitgleich zur S2-JO-Referenz sind.

Die Auswahl ist materialisiert, der reale zweite Quellenpfad jedoch noch nicht
abgenommen. Es werden weder Toleranzen eingefuehrt noch Desktop, Browser,
Kamera, Mikrofon oder ein anderer Codec als Ausweichweg geoeffnet.

Dieser Befund betrifft ausschliesslich die Wahrnehmungsschnittstelle im
Default-Live-Profil mit 336 reduzierten Werten. Er ist keine Memoryskalierung,
kein Kontextbefund und keine MCM-Feldwirkung.
