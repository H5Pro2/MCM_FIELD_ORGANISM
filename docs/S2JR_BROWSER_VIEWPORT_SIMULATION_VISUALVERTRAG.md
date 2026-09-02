# S2-JR - Browser-Viewport-zu-Simulation-Visualvertrag

## Status und Zweck

`S2JR_STATIC_VISUAL_CONTRACT_COMPLETE`

Implementierungsstatus:

`BROWSER_VISUAL_IMPLEMENTATION_NOT_AUTHORIZED`

S2-JR bindet ausschliesslich einen spaeteren visuellen Quellenvergleich:

```text
SIMULATION_RENDER
gegen
BROWSER_VIEWPORT
```

Verglichen werden dieselben sechs visuellen S2-JO-Frames. Audio, Memory,
Kontext und MCM-Feld liegen vollstaendig ausserhalb dieses Vertrags. Es wird
kein Browser gestartet, kein Bild erzeugt oder dekodiert und keine
Rezeptorfunktion aufgerufen.

## Terminaler Abschluss von S2-JQ

Der Kandidat

```text
NUT + rawvideo/rgb24 + pcm_f32le
```

bleibt unter dem in S2-JQ gebundenen PyAV-/FFmpeg-Build terminal als
`VIDEO_DECODE_PATH_UNAVAILABLE` geschlossen. S2-JQ wird nicht wiederholt,
umgedeutet oder unter einer anderen Codec- oder Containerbezeichnung
fortgesetzt. S2-JR lockert weder dessen Regeln noch sucht es einen
Ersatzcodec.

Gebundene Abschlussbelege:

| Beleg | SHA-256 |
| --- | --- |
| `reports/s2jq/S2JQ_CODEC_CONTAINER_PREFLIGHT_BEFUND.md` | `3664beb08bc9296ad41245d1ba05db23db31694ca2786de6de7968d419714569` |
| `reports/s2jq/s2jq-video-pcm-preflight-20260901-01/result.json` | `107acbaf751a0ce054d8fb6585dd10870a2d0ca61b444badfccba51af725f282` |
| `reports/s2jq/s2jq-video-pcm-preflight-20260901-01/terminal.json` | `e78517e11e60885477899389b49bde6210501ec75a15b033d5d0679de3ad2183` |

## Gebundener Quellstand

| Quelle | SHA-256 |
| --- | --- |
| `tools/_s2jo_private_canonical_av_boundary.py` | `50a39fb3865fbd11b3577f79db2983f9dd3260262dee0f199ae5f884bed4ef71` |
| `tests/test_s2jo_private_canonical_av_boundary.py` | `c14bd814dfcfa65cfba8e7a54df90cd05ac69f626fa2272280334acb4d005a07` |
| `mcm_field_organism/browser_payload_source.py` | `db4cee84c33e9ccdfc2ddee9a8bbeae5090cccf3370d0db0566af1a8564fa149` |
| `mcm_field_organism/browser_receptor_bridge.py` | `a00654efc655185538570a452302c2bf58e28cfb785e10bd39ca73104752ce20` |
| `mcm_field_organism/finite_video_path.py` | `d09cb6ba35fd061e4a243b7ed2112597a194e75abd026d7cc3ab7aa89922c07a` |
| `tools/controlled_browser_payload_world/index.html` | `74fc372a3eff08ac38e803689e562ce5acbb39d56d3351db475c768457e32af8` |
| `tools/controlled_browser_payload_world/styles.css` | `f026fce8f826fb7364a11b1b05ad4acb3dd37aed7dede5453c6f82cbf497b594` |
| `tools/controlled_browser_payload_world/world.js` | `fda8c774708af883eb97625b7064ec288c06e2819619fb2eb93e281212d32158` |

Die Hashes sind statische Herkunftsbindungen, keine Browser- oder
Funktionsabnahme.

## Visuelle Referenzepisode

Die spaetere Pruefung verwendet unveraendert die visuelle Teilfolge von
`s2jo.digital.av.episode.v1`:

- exakt sechs Frames mit Indizes `0..5`;
- exakt `1920 x 1080 x 3` zusammenhaengende RGB8-Bytes je Frame;
- Hintergrund RGB `(16, 32, 48)`;
- ein Vordergrundrechteck von exakt `160 x 135` Pixeln;
- Vordergrund RGB `(224, 64, 32)`;
- Rechteckzeile `2`, Rechteckspalte gleich Frameindex `0..5`;
- Zeitfenster `floor(i * 1e9 / 30)` bis
  `floor((i + 1) * 1e9 / 30)`;
- gemeinsame Uhr und funktionale Frameform aus S2-JO.

Die Python-Simulation und die Browserdarstellung besitzen getrennte
Implementierungen. Beide werden durch denselben vorab versiegelten literalen
Frameplan gebunden. Weder Browser- noch Simulationsarm darf Pixelbytes oder
Ergebnisse des jeweils anderen Arms als Eingabe uebernehmen.

## Browser-Viewport-Grenze

Der spaetere Browserarm muss vor dem ersten Frame bestaetigen:

- frischer isolierter Browserkontext ohne persistentes Profil und Extensions;
- Seitenviewport exakt `1920 x 1080` CSS-Pixel;
- `deviceScaleFactor` exakt `1`;
- resultierende Screenshotflaeche exakt `1920 x 1080` Device-Pixel;
- genau ein lokales HTML-, CSS- und JavaScript-Assetinventar;
- keine Netzwerk-, Daten-, Blob- oder sonstigen Fremdanfragen;
- keine Scrollflaeche und keine Browserzoomabweichung;
- `html`, `body` und `canvas` fuellen den Viewport pixelgenau;
- Rand, Margin, Padding, Text, Controls, Cursor, Fokusmarkierung und Animation
  sind abwesend;
- der Canvas besitzt eine opake Zeichenflaeche und eine Backing-Store-Groesse
  von exakt `1920 x 1080`.

Die visuelle Nutzlast ist ausschliesslich die PNG-Ausgabe eines vollstaendigen
Viewport-Screenshots. Ein `locator("canvas#world").screenshot(...)` ist nicht
ausreichend, weil es die geforderte Viewportgrenze nicht prueft.

Viewport-, Canvas-, DOM-, Asset-, Browser- und Requestdaten gehoeren nur in
die technische Auditprovenienz. Sie duerfen nicht in den funktionalen Frame-
oder Rezeptordigest eingehen.

## Direkte ImageData-Erzeugung

Fuer jeden Frame erzeugt der Browser eine neue `ImageData(1920, 1080)`-Form.
Ihre RGBA-Bytes werden positionsweise mit den literalen RGB-Werten des
Frameplans und Alpha `255` beschrieben und genau einmal mit
`putImageData(..., 0, 0)` auf den opaken Canvas uebertragen.

Nicht zulaessig sind:

- `fillRect`, Pfade, Text, Bilder, CSS-Hintergruende oder WebGL als Ersatz;
- Antialiasing, Interpolation, Compositing oder Transparenz;
- Lesen der Canvaspixel per `getImageData` als funktionaler Eingang;
- Uebernahme der S2-JO-Pixelbytes aus Python in den Browser;
- DOM-Werte, Canvas-Befehle oder Fixtureparameter hinter der Screenshotgrenze.

Der Frameplan steuert nur die kontrollierte Quellfixture. Der funktionale
Browserinput beginnt erst bei den gerenderten PNG-Bytes des Viewports.

## PNG-zu-RGB8-Grenze

Jeder Viewport-Screenshot muss vor Nutzdatenannahme als PNG validiert werden:

- korrekte PNG-Signatur und vollstaendige Chunkstruktur;
- `IHDR` exakt `1920 x 1080`, Bit-Tiefe `8`, Truecolor;
- weder Palette noch Alpha-, Graustufen- oder Mehrbildform;
- keine eingebettete Farbprofil- oder Gammatransformation;
- genau ein vollstaendig dekodierbares Bild;
- dekodiertes Ergebnis exakt `uint8` mit Form `(1080, 1920, 3)`.

Zulaessig ist ausschliesslich eine verlustfreie PNG-Dekodierung. Gibt der
Decoder BGR-Kanalreihenfolge aus, darf genau eine explizite positionsweise
BGR/RGB-Kanalpermutation erfolgen. Resize, Crop, Farbraumumbau,
Farbkorrektur, Normalisierung, Rundung und Alpha-Compositing sind verboten.

Der vorhandene `BrowserReceptorBridge.push_visual_png` ist fuer S2-JR nicht
unveraendert abgenommen: Er verwendet `IMREAD_COLOR`, prueft die PNG-
Anatomie nicht vollstaendig und ruft den Rezeptor vor einem positionsweisen
Vergleich mit S2-JO auf.

## Vergleichs- und Aufrufreihenfolge

Fuer jeden Index `i = 0..5` gilt verbindlich:

1. unabhaengigen S2-JO-Simulationsframe fuer `i` erzeugen;
2. Browser-`ImageData` fuer `i` aus dem literalen Plan erzeugen;
3. vollstaendigen Viewport als PNG erfassen;
4. PNG strikt und ohne Wertumrechnung nach RGB8 dekodieren;
5. Form, Index, Zeitfenster und Geometrie beider Frames pruefen;
6. SHA-256 der beiden RGB8-Payloads positionsgleich vergleichen;
7. nur bei exakter Digest- und Bytegleichheit beide Frames derselben
   unveraenderten `LocalChannelGridReceptor.analyze`-Funktion anbieten;
8. beide reduzierten visuellen Zustaende kanonisch vergleichen.

Beide Rezeptorinstanzen sind frisch und verwenden exakt:

```text
VisualGridConfig(1920, 1080, 12, 8, 30.0)
```

Jeder reduzierte Zustand besitzt 288 Werte. Quellklasse, PNG-Digest,
Browseridentitaet und DOM-Belege sind aus seiner funktionalen Form
ausgeschlossen.

Eine Payloadabweichung stoppt vor dem zugehoerigen Rezeptoraufruf als
`BROWSER_SIMULATION_PIXELS_DIFFER`. Es gibt keine Toleranz. Erst sechs
bitgleiche Payloadpaare und sechs bitgleiche reduzierte Zustandspaare ergeben
`BROWSER_SIMULATION_VISUAL_PATH_EQUAL`.

## Daten- und Digestrollen

Die Beweiskette ist vorwaertsgerichtet:

```text
S2JRVisualPlan
-> SimulationFrameReceipt[i]
-> BrowserRenderAuditReceipt[i]
-> BrowserViewportPNGReceipt[i]
-> BrowserCanonicalFrameReceipt[i]
-> PixelEqualityReceipt[i]
-> SimulationVisualStateReceipt[i]
-> BrowserVisualStateReceipt[i]
-> VisualStateEqualityReceipt[i]
-> S2JRVisualResult
```

`BrowserRenderAuditReceipt` und `BrowserViewportPNGReceipt` duerfen Browser-
und PNG-Provenienz enthalten. `BrowserCanonicalFrameReceipt` verwendet die
quellenneutrale S2-JO-Form. Kein Ergebnis oder Sollwert darf einen frueheren
Frame, Renderauftrag oder Rezeptorzustand autorisieren.

## Ressourcen- und Operationsgrenze

Je Arm werden exakt sechs RGB8-Payloads mit insgesamt `37.324.800` Byte
verarbeitet. Gleichzeitig duerfen hoechstens ein Simulationsframe, ein PNG
und ein dekodierter Browserframe gehalten werden. PNG-, Browser- und
Decoderpuffer sind als gemessene Laufzeitressourcen getrennt auszuweisen.

Persistente PNG- oder RGB8-Nutzpayloadbytes im Ergebnis: exakt `0`.

Der spaetere Vergleich besitzt maximal 55 Top-Level-Operationen:

- vier vorbereitende Operationen fuer Plan, Browserkontext, lokale Assets und
  Viewportpruefung;
- je Frame acht Operationen fuer Simulation, ImageData-Rendern, Screenshot,
  PNG-Dekodierung, Payloadvergleich, zwei Rezeptoraufrufe und
  Zustandsvergleich: `6 * 8 = 48`;
- je eine Operation fuer Inventarabschluss, Browserabschluss und
  Ledgerpruefung.

Ein frueher Stopp erzeugt nur das gueltige Praefix. Die 55 Operationen sind
keine Implementierungs- oder Ausfuehrungsfreigabe.

## Fail-Closed- und Falsifikationsregeln

Vor dem ersten Rezeptoraufruf stoppt S2-JR bei:

- abweichender Viewport-, Device- oder Canvasgeometrie;
- unvollstaendigem oder fremdem Asset-/Requestinventar;
- Text, Controls, Rahmen, Scrollbereich oder sonstiger sichtbarer Zusatzform;
- anderer Rendertechnik als der gebundenen direkten `ImageData`-Erzeugung;
- ungueltiger PNG-Form oder notwendiger Wert-, Farb- oder Geometrieumrechnung;
- fehlendem, doppeltem oder vertauschtem Frame beziehungsweise Zeitfenster;
- nicht bitgleichem RGB8-Payload;
- Kopplung von Auditprovenienz an funktionale Werte oder Digests.

Sind die kanonischen RGB8-Payloads bitgleich, aber die reduzierten visuellen
Zustaende verschieden, ist die quellenunabhaengige visuelle Rezeptorgrenze
falsifiziert. Unterschiedliche Browser- und Simulationsprovenienz ist dagegen
erwartet.

## Freigabegrenze

S2-JR autorisiert weder Browserassets noch Adapter, Tests oder Ausfuehrung.
Ein spaeterer Implementierungsschritt darf nur eine private visuelle Fixture,
einen Viewport-PNG-Adapter und fokussierte technische Tests umfassen. Erst
danach kann ein einmaliger Sechs-Frame-Vergleich separat freigegeben werden.

Ein positiver Befund waere ausschliesslich ein Nachweis der visuellen
Quellenunabhaengigkeit zwischen Simulation und Browserviewport im
Default-Live-Profil. Er waere keine Audio-, Memory-, Kontext- oder
Feldbestaetigung. Die auditive Quellenpruefung folgt getrennt.
