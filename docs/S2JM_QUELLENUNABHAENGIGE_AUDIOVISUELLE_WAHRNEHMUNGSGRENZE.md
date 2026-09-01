# S2-JM - Quellenunabhaengige audiovisuelle Wahrnehmungsgrenze

## Status und Zweck

`STATIC_CONTRACT_ONLY`

Dieser Vertrag bindet genau die technische Grenze zwischen austauschbaren
audiovisuellen Quellen und den vorhandenen Rezeptorfunktionen:

```text
Quellenadapter
-> kanonische fluechtige Bildframes und PCM-Hops
-> unveraenderte visuelle und auditive Rezeptoren
-> reduzierte zeitgebundene Rezeptorzustaende
```

Er implementiert und prueft nichts. Memory, Kontext, MCM-Feld, Lernen und
Effektoren liegen ausserhalb dieses Vertrags.

Der Lauf `s2jl-end-to-end-context-use-20260901-01` bleibt unveraendert
`NOT_EVALUABLE`. Die Integrationsschuld an `ie-op-171` wird nicht repariert,
umbenannt oder in diesen Wahrnehmungszweig uebernommen. Belastbare getrennte
Memory-, Kontextbeurteilungs-, Zulassungs- und Verbrauchsbefunde bleiben davon
unberuehrt. Eine vollstaendig verkettete reale Memory-zu-Verbrauch-Kette wird
nicht behauptet.

## Quellenrollen

Zulaessige visuelle Quellklassen sind ausschliesslich:

1. `BROWSER_VIEWPORT` - gerenderte Pixel des fest gebundenen Viewports;
2. `DESKTOP_CAPTURE` - Pixel eines fest gebundenen Desktopbereichs;
3. `VIDEO_DECODE` - dekodierte Frames eines endlichen Videos;
4. `SIMULATION_RENDER` - gerenderte Pixel einer kontrollierten Simulation;
5. `CAMERA_CAPTURE` - Frames eines ausdruecklich gewaehlten Kamerageraets.

Zulaessige auditive Quellklassen sind ausschliesslich:

1. `VIDEO_AUDIO` - dekodierte PCM-Spur eines endlichen Videos;
2. `SYSTEM_AUDIO` - PCM-Ausgabe eines ausdruecklich gebundenen Systemkanals;
3. `SIMULATION_AUDIO` - PCM-Ausgabe einer kontrollierten Simulation;
4. `MICROPHONE_CAPTURE` - PCM eines ausdruecklich gewaehlten Mikrofons.

Kamera und Mikrofon sind physische Quellen und bleiben fuer die erste
digitale Gleichheitspruefung gesperrt. Sie muessen spaeter dieselben
kanonischen Eingangsformen ohne eine eigene Rezeptorvariante verwenden.

## Kanonischer visueller Eingang

`CanonicalVisualFrameV1` besitzt genau diese funktionalen Felder:

| Feld | Verbindliche Form |
| --- | --- |
| `schema` | `s2jm.canonical-visual-frame.v1` |
| `episode_id` | neutrale technische Episodenidentitaet |
| `frame_index` | lueckenloser nichtnegativer Integer |
| `pixel_format` | `RGB8` |
| `dtype` | `uint8` |
| `shape` | `(1080, 1920, 3)` |
| `geometry_id` | `visual.grid12x8.channels3.source1920x1080.v1` |
| `clock_id` | gemeinsame technische Episodenuhr |
| `window_start_tick` | eingeschlossen, nichtnegativ |
| `window_end_tick` | ausgeschlossen und groesser als Start |
| `pixel_digest` | SHA-256 der kanonischen zusammenhaengenden RGB-Bytes |
| `functional_input_digest` | Digest aller vorstehenden funktionalen Rollen |

Die Framefolge verwendet unveraendert `30 Hz`. Ein Adapter muss sein natives
Format vor der Grenze exakt nach `RGB8` ueberfuehren. Alpha wird ausschliesslich
vor der Grenze nach einer vorab gebundenen Regel entfernt. BGR-, BGRA-, YUV-,
komprimierte Bild- oder Browser-PNG-Nutzlasten sind keine funktionalen
Rezeptoreingaenge.

Es gibt in dieser Stufe kein implizites Cropping, Resizing, Upscaling,
Downscaling, Farbmanagement oder Interpolieren. Weicht die Quelle von
`1920x1080` ab oder ist die Kanalreihenfolge nicht eindeutig, stoppt der
Adapter fail-closed vor dem Rezeptor.

Jeder gueltige Frame wird unveraendert genau derselben vorhandenen
`LocalChannelGridReceptor.analyze`-Funktion mit der unveraenderten
`VisualGridConfig(1920, 1080, 12, 8, 30.0)` angeboten.

## Kanonischer auditiver Eingang

`CanonicalPCMAudioHopV1` besitzt genau diese funktionalen Felder:

| Feld | Verbindliche Form |
| --- | --- |
| `schema` | `s2jm.canonical-pcm-audio-hop.v1` |
| `episode_id` | dieselbe neutrale technische Episodenidentitaet |
| `hop_index` | lueckenloser nichtnegativer Integer |
| `encoding` | `PCM_F32LE` |
| `channels` | `1` |
| `sample_rate_hz` | `48000` |
| `sample_count` | `480` |
| `sample_domain` | endliche Werte in `[-1.0, 1.0]` |
| `clock_id` | dieselbe technische Episodenuhr |
| `window_start_tick` | eingeschlossen, nichtnegativ |
| `window_end_tick` | ausgeschlossen und groesser als Start |
| `pcm_digest` | SHA-256 der kanonischen 1.920 PCM-Bytes |
| `functional_input_digest` | Digest aller vorstehenden funktionalen Rollen |

Mehrkanalton, andere Sampleraten, Integer-PCM und komprimiertes Audio muessen
vor dieser Grenze durch eine ausdruecklich gebundene technische
Quellenabbildung in diese Form gebracht werden. Fuer die erste Pruefung sind
keine implizite Kanalwahl, Pegelnormalisierung, automatische
Lautstaerkeanpassung, Resampling-Alternative oder fehlertolerante Reparatur
zulaessig. Eine nicht exakt gebundene Abbildung stoppt fail-closed.

Die PCM-Hops werden unveraendert dem vorhandenen `BroadbandHearingPath` mit
`LogSpectralConfig(sample_rate=48000, window_size=4800, hop_size=480,
min_frequency=50.0, max_frequency=18000.0, band_count=48)` angeboten. Der
erste reduzierte Zustand entsteht weiterhin nach 100 ms, danach einer pro
10-ms-Hop. Es gibt keine quellspezifische Filterbank oder Schwelle.

`CanonicalPCMAudioHopV1` ist dabei das atomare PCM-Fenster der Quellgrenze.
Die vorhandene Rolling-Rezeptorfunktion bildet ihr Analysefenster weiterhin
ausschliesslich aus zehn aufeinanderfolgenden Hops. Die Dekodierung der
kanonischen Little-Endian-Bytes in die 480 endlichen Floatwerte veraendert
weder Reihenfolge noch Werte und ist keine eigene Rezeptorfunktion.

## Bestandszuordnung und Nichtabnahme

Wiederverwendet und durch diesen Vertrag festgeschrieben sind ausschliesslich:

- `LocalChannelGridReceptor` mit dem oben gebundenen `VisualGridConfig`;
- `BroadbandHearingPath` und `LogSpectralReceptor` mit dem oben gebundenen
  `LogSpectralConfig`;
- die vorhandenen reduzierten Rezeptorzustands- und Zeitformen hinter diesen
  Funktionen.

PNG-Decoding, BGR-zu-RGB-Konvertierung, Video-Decoding, Desktop- oder
Browseraufnahme, Kamera-Capture, Audiodecoding, Kanalabbildung und Resampling
liegen vor der kanonischen Grenze. Vorhandene Adapter gelten durch diesen
statischen Vertrag nicht automatisch als konform oder abgenommen. Ihre
Konformitaet muss spaeter pro Quellklasse gegen exakt dieselben kanonischen
Eingangsformen geprueft werden. Dieser Vertrag aendert keinen bestehenden
Adapter und behauptet keinen bereits funktionierenden Livepfad.

## Zeit- und Episodenbindung

Visuelle Frames und auditive Hops bilden zwei geordnete Folgen auf derselben
technischen Episodenuhr. Die unterschiedlichen Raten werden nicht durch
Duplikation, Auswahl oder erzwungene 1:1-Paare verborgen.

Verbindlich sind:

- monotone, lueckenlose Indizes je Modalitaet;
- positive, nicht rueckwaerts laufende Zeitfenster;
- identische `episode_id`, `clock_id` und vorab gebundene Episodengrenzen;
- vollstaendige Inventare der erwarteten Frames und Hops;
- keine Behauptung physischer Gleichzeitigkeit allein aus ueberlappenden
  technischen Zeitfenstern.

Nach der Reduktion duerfen ausschliesslich `ReceptorContactFrame`,
`OrganismTimedReceptorFrame`, `ReceptorTimeSequence` und ihre technischen
Digests in den weiteren Wahrnehmungspfad gelangen. Die vorhandenen
Rezeptorfunktionen erhalten keine Quellklasse.

## Strikte Informationsgrenze

Folgende Inhalte sind weder funktionaler Eingang noch zulaessige Hilfsmerkmale:

- DOM, HTML, CSS, Canvas-Befehle oder Browserzustand;
- URL, Seitentitel, Seitentext oder Netzwerkantworten;
- Accessibility-Baum, ARIA-Rollen oder Steuerelementnamen;
- Datei-, Objekt-, Personen-, Sprecher-, Szenen- oder Klassenlabels;
- Objektboxen, Tracking-IDs, Untertitel oder Transkripte;
- Rewards, Zielwerte, Sollentscheidungen oder Evaluationsrollen;
- Kamera-, Mikrofon-, Fenster-, Prozess- oder Dateinamen als
  Wahrnehmungsmerkmal.

Ein Browser-Viewport ist nur seine kanonische Pixelmatrix. Ein Video ist nur
seine kanonischen Frame- und PCM-Folgen. Desktop, Simulation, Kamera und
Mikrofon gelten entsprechend.

## Technische Provenienz

`SourceAuditProvenanceV1` darf getrennt vom funktionalen Eingang enthalten:

- Quellklasse;
- opaque Quellinstanz- und Adapterdigests;
- Adapterversion und gebundene Konfiguration;
- Digest des nativen, fluechtig gelesenen Payloads;
- Aufnahme-, Decode- und Validierungsstatus;
- Fehler-, Vollstaendigkeits- und Verwerfungsbelege.

DOM, URL, Text, Labels und Objektmetadaten bleiben auch in dieser Form
ausgeschlossen. Provenienz darf nur Quellenannahme, Audit und Reproduktion
pruefen. Sie darf nicht:

- in `functional_input_digest` eingehen;
- Rezeptorwerte, Memorybildung, Lernen oder Entscheidungen beeinflussen;
- einen Kandidaten priorisieren oder einen fehlenden Payload ersetzen;
- als versteckte dritte Wahrnehmungs- oder Memoryebene fortbestehen.

Bei bitidentischen kanonischen AV-Eingaengen muessen unterschiedliche gueltige
Quellprovenienzen deshalb dieselben reduzierten funktionalen Rezeptorfolgen
erzeugen. Auditdigests duerfen erwartungsgemaess verschieden bleiben.

## Fluechtigkeit und Besitz

Rohpixel und PCM besitzen genau einen kurzfristigen Adapter-/Rezeptor-Owner.
Sie duerfen bis zum Abschluss ihrer jeweiligen Rezeptorreduktion im Speicher
liegen. Danach gilt verbindlich:

- keine Aufnahme in Memory, Kontext, Feldsnapshot oder oeffentliche API;
- keine Ablage in Ergebnis-, Receipt-, Journal- oder Debugdateien;
- keine Replaywarteschlange und kein spaeteres synthetisches Wiederangebot;
- keine weiter erreichbare Rohpayload-Referenz im Funktionspfad;
- nur kanonische Nutzlastdigests, reduzierte Werte und technische
  Zeit-/Geometriebelege duerfen fortbestehen.

`Verwerfen` bedeutet hier Beenden der programmatischen Aufbewahrung, nicht die
unbelegbare Zusage einer sicheren physikalischen Speicherloeschung.

## Fail-Closed-Regeln

Vor dem ersten Rezeptoraufruf muss die gesamte kanonische Eingangsform gueltig
sein. Der Vorgang stoppt ohne Rezeptorzustand bei:

1. falschem Datentyp, Format, Kanalzahl, Form oder Dimension;
2. NaN, Infinity oder Audio ausserhalb `[-1, 1]`;
3. fehlender, doppelter, vertauschter oder rueckwaerts laufender Position;
4. ungebundener Geometrie, Zeitbasis oder Episodenzugehoerigkeit;
5. unvollstaendig verworfenem Rohpayload oder unzulaessiger Metadatenkopplung;
6. quellspezifischer Rezeptorfunktion oder unterschiedlichem Rezeptorprofil;
7. fehlender Trennung von funktionalem Digest und Auditprovenienz;
8. unvollstaendig abgeschlossenem Audiofenster oder Quelleninventar.

Ein Quellenfehler ist kein aktiver Nullkontakt. Er erzeugt keinen regulaeren
Rezeptorzustand und darf nicht durch Nullen ersetzt werden.

## Naechste digitale Funktionspruefung

Der naechste, separat freizugebende Schritt verwendet eine einzige endliche,
vorab gebundene audiovisuelle Episode. Sie wird ueber die digitalen
Quellklassen Browser-Viewport/Systemaudio, Desktopaufnahme/Systemaudio,
Video-Decode und Simulation bereitgestellt.

Die Pruefung muss zweistufig auswerten:

1. **Adaptergleichheit:** Die kanonischen Frame-, PCM- und
   `functional_input_digest`-Folgen sind positionsweise identisch. Sind sie es
   nicht, ist die Quellenvergleichszelle nicht auswertbar.
2. **Rezeptorgleichheit:** Bei identischen kanonischen Folgen muessen dieselben
   unveraenderten Rezeptoren identische reduzierte Werte, Geometrien,
   Zeitfolgen und funktionale Digests erzeugen. Unterschiedliche
   Auditprovenienz darf daran nichts aendern.

Pflichtkontrollen sind eine einzelne geaenderte Pixelposition, ein einzelner
geaenderter PCM-Samplewert, falsche Kanalreihenfolge, unvollstaendige Folgen
und eingespeiste Metadaten. Reale Unterschiede bleiben Unterschiede; der
Vertrag verlangt keine Wahrnehmungsinvarianz gegen unterschiedliche Pixel oder
Samples.

Kamera und Mikrofon folgen erst nach der digitalen Pruefung als
Schnittstellenkonformitaet physischer Quellen. Wegen unvermeidbarer
Aufnahmeunterschiede wird dort keine Bitgleichheit zur digitalen Episode
behauptet.

## Falsifikation und Freigabegrenze

Der Vertrag ist verletzt, wenn:

- dieselben kanonischen Payloads je nach Quellklasse andere Rezeptorwerte
  erzeugen;
- Metadaten eine funktionale Entscheidung oder einen reduzierten Wert aendern;
- Rohpayloads hinter der Rezeptorgrenze fortbestehen;
- ein Adapter still skaliert, resampelt, repariert oder fehlende Daten ersetzt;
- eine physische oder digitale Quelle eine eigene Rezeptorregel erhaelt.

Eine bestaetigte Quellenunabhaengigkeit waere ausschliesslich ein technischer
Wahrnehmungsschnittstellenbefund. Sie waere kein Nachweis von Objekterkennung,
Semantik, Memory, Lernen, innerem Kontext oder MCM-Feldwirkung.

Bis zu einer separaten Freigabe bleiben Implementierung, Tests,
Quellenaufnahme, Memory-, Kontext- und Feldaufrufe vollstaendig gesperrt.
