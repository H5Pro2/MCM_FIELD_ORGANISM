# S2-ML: Statischer Speicher- und Lebensdaueraudit

## Status

`S2MK_DENSE_FULL_FORMAT_FLOW_RESOURCE_INCOMPATIBLE`

Der gebundene dichte Farneback-Pfad fuer `1920 x 1080` ist mit der
unveraenderten Prozesspeakgrenze von `134.217.728` Byte nicht vereinbar.
Diese Entscheidung betrifft ausschliesslich die Vollformatressource. Sie ist
kein Bewegungs-, Korrespondenz-, Wahrnehmungs- oder Memorybefund.

Der Audit hat keine Projektfunktion importiert oder ausgefuehrt, keinen Test
gestartet und keines der acht vorversiegelten Korpuspaare geoeffnet.

## Gebundene Grundlage

| Gegenstand | Bindung |
| --- | --- |
| Produktquelle | `tools/_s2mk_private_motion_measurement.py` |
| Produkt-SHA-256 | `f297ad38877925fb3b6488024507babd9a4617c592c509f3dda615b4eb583759` |
| Testquelle | `tests/test_s2mk_private_motion_measurement.py` |
| Test-SHA-256 | `a54b1d01615f9d8865e35733a7621bde64fcd04e2fb23229e6056f97608949a8` |
| Qualifikationsbefund 03 | `reports/s2mk/S2MK_NEUTRALE_MESSQUALIFIKATION_03_BEFUND.md` |
| Befund-SHA-256 | `f64208917eb743b0d95b45bc85fb5fe2559262455adb7342ed0060cbd29b8913` |
| OpenCV | `4.13.0`, CPU, ein Thread, OpenCL aus |
| Farnebackparameter | `0.5 / 5 / 21 / 5 / 7 / 1.5 / 0` |
| Bildpunkte | `N = 1920 x 1080 = 2.073.600` |
| Prozesspeakgrenze | `134.217.728` Byte (`128 MiB`) |

Fuer die interne CPU-Lebensdauer wurde zusaetzlich die Implementierung von
`FarnebackOpticalFlowImpl::calc` aus dem offiziellen OpenCV-Tag `4.13.0`
statisch herangezogen:

`https://github.com/opencv/opencv/blob/4.13.0/modules/video/src/optflowgf.cpp`

Der qualifizierte lokale Binaer- und Build-Informationsdigest bleibt die
Laufzeitbindung. Der Quellvergleich ersetzt diese Bindung nicht.

## Elementare Vollbildgroessen

| Rolle | Form und Typ | Anzahl | Byte je Objekt | Byte gesamt |
| --- | --- | ---: | ---: | ---: |
| RGB-Frames | `1080 x 1920 x 3`, `uint8` | 2 | `6.220.800` | `12.441.600` |
| Grauprojektionen | `1080 x 1920`, `uint8` | 2 | `2.073.600` | `4.147.200` |
| dichter Flow | `1080 x 1920 x 2`, `float32` | 2 | `16.588.800` | `33.177.600` |
| ein Skalarfeld | `1080 x 1920`, `float32` | 1 | `8.294.400` | `8.294.400` |
| ein Fuenfkanalfeld | `1080 x 1920 x 5`, `float32` | 1 | `41.472.000` | `41.472.000` |
| Bool-Gueltigkeitsfeld | `1080 x 1920`, `bool` | 1 | `2.073.600` | `2.073.600` |

## OpenCV-Untergrenze

Der gebundene Pythonaufruf verwendet
`cv2.calcOpticalFlowFarneback(..., flags=0)`. Der CPU-Pfad erzeugt am
Vollbildlevel gleichzeitig:

- `R[0]`: ein Polynomfeld `CV_32FC5`;
- `R[1]`: ein zweites Polynomfeld `CV_32FC5`;
- `M`: das Aktualisierungsmatrixfeld `CV_32FC5`;
- `flow0`: das Ausgabefeld `CV_32FC2`.

`FarnebackUpdateMatrices(R[0], R[1], flow, M, ...)` benoetigt beide
Polynomfelder und das Flowfeld, waehrend `M` erzeugt und anschliessend fuer
die Iterationen gehalten wird. Diese Rollen koennen daher nicht denselben
Speicher ueberlappend verwenden.

| Gleichzeitig notwendige OpenCV-Matrix | Byte |
| --- | ---: |
| `R[0]` | `41.472.000` |
| `R[1]` | `41.472.000` |
| `M` | `41.472.000` |
| aktueller Vollbildflow | `16.588.800` |
| **harte Teiluntergrenze** | **`141.004.800`** |

Diese Teiluntergrenze liegt bereits `6.787.072` Byte ueber der gesamten
gebundenen Prozessgrenze. Sie laesst beide Eingabegraubilder, beide
RGB-Frames, weitere OpenCV-Matrizen, Pyramidenstufen, Zeilenpuffer,
Pythonobjekte und Allokatoroverhead unberuecksichtigt.

Die regulaere CPU-Lebensdauer enthaelt am Vollbildlevel zusaetzlich:

- `fimg`, das vollformatige `CV_32F`-Arbeitsbild: `8.294.400` Byte;
- `I`, das vollformatige skalierte Arbeitsbild: `8.294.400` Byte;
- `prevFlow` der vorherigen Halbaufloesungsstufe: `4.147.200` Byte.

Zusammen mit den zwei RGB-Frames und zwei Grauprojektionen ergibt das fuer
den ersten Flowaufruf eine statische benannte Belegung von mindestens
`178.329.600` Byte. Beim Rueckwaertsfluss bleibt der bereits erzeugte
Vorwaertsfluss resident; damit steigt die benannte Belegung auf
`194.918.400` Byte.

Der in Qualifikation 03 gemessene Peak von `196.093.952` Byte liegt nur
`1.175.552` Byte ueber dieser statischen Lebensdauerprojektion. Die
Abweichung ist mit nicht einzeln gebundenen OpenCV-Zeilen-, Filter-,
Allokator- und Pythonpuffern vereinbar. Fuer die Entscheidung wird sie nicht
als frei optimierbare Reserve verwendet.

## Phasenbilanz

### 1. Eingabe und Digestpruefung

Zwei RGB-Frames belegen `12.441.600` Byte. `_frame_digest` materialisiert
mit `frame.tobytes(order="C")` zusaetzlich jeweils eine temporaere Kopie von
`6.220.800` Byte. Ein Hash ueber einen zusammenhaengenden Buffer koennte
diese Kopie vermeiden. Der Farneback-Peak wird dadurch nicht veraendert.

### 2. Grauprojektion

Die beiden dauerhaften Grauprojektionen belegen `4.147.200` Byte. Die
zeilenblockweise Integerprojektion besitzt zusaetzliche `uint32`-Puffer fuer
Rot, Gruen, Blau und die gewichtete Summe. Diese Puffer sind begrenzt und
liegen vor dem Flowpeak.

### 3. Vorwaertsfluss

Der erste Farneback-Aufruf haelt RGB, Grau, den aktuellen Flow und die oben
aufgefuehrten OpenCV-Arbeitsmatrizen. Die statische benannte Untergrenze
betraegt `178.329.600` Byte. Interne Gaussian-, Resize-, Polynom- und
Zeilenpuffer sind darin noch nicht enthalten.

Der CPU-Pfad baut keine dauerhaft gespeicherte separate Bildpyramide auf.
Er durchlaeuft die Skalen `1/32, 1/16, 1/8, 1/4, 1/2, 1` und haelt neben der
aktuellen Stufe den vorherigen Flow. Das Vollbildlevel ist wegen der drei
Fuenfkanalfelder dominant.

### 4. Rueckwaertsfluss

Der Rueckwaertsaufruf verwendet dieselben Graubilder, waehrend der
Vorwaertsflow fuer die spaetere Zykluspruefung erhalten bleiben muss. Die
statische benannte Belegung betraegt dadurch `194.918.400` Byte. Dies ist
die peakbestimmende Phase.

### 5. Flowdigests

`_flow_bytes` erzeugt fuer jeden Flow eine vollstaendige temporaere
`bytes`-Kopie von `16.588.800` Byte. Ein direkter SHA-256-Bufferzugriff waere
outputneutral und wuerde diese Kopie entfernen. Die Digestphase liegt aber
nach beiden Farneback-Aufrufen und bestimmt den Prozesspeak nicht.

### 6. Vollbildresiduen und Interpolation

Nach Freigabe der Grauprojektionen bleiben RGB und beide Flows resident.
Hinzu kommen:

- Magnitude: `8.294.400` Byte;
- Gueltigkeit: `2.073.600` Byte;
- Zyklusresiduum: `8.294.400` Byte;
- RGB-Residuum: `8.294.400` Byte;
- begrenzte Koordinaten-, Sample- und Rechenpuffer je Zellzeile.

Der produktseitige Ledger hat fuer diese Phase `89.432.220` Byte als Peak
eigener NumPy-Arrays erfasst. Zellweise Verarbeitung, Pufferwiederverwendung
und fruehere Freigaben koennten diesen Wert reduzieren. Sie liegen jedoch
nach der peakbestimmenden Rueckwaertsflowphase.

### 7. Zellstatistik und Perzentile

Die 96 Zellen werden nacheinander zusammengefasst. Die lokalen Kopien sind
gegenueber den Vollbildmatrizen klein. Die globalen `_summary`-Aufrufe
konvertieren dagegen Vollbildwerte nach `float64`; `np.percentile` darf
weitere Auswahl- oder Sortierpuffer anlegen. Diese Speicheranteile fehlen
im eigenen Arrayledger.

Eine zellweise oder destruktive, erst nach Abschluss aller Zellbefunde
ausgefuehrte Statistikbildung koennte den spaeten Peak reduzieren. Sie kann
die OpenCV-Untergrenze nicht beeinflussen.

### 8. Rezeptor-, Pose- und Formbaseline

Die Baseline wird erst nach Rueckgabe des Bewegungsbefunds ausgefuehrt. Die
Pixel-L1-Berechnung arbeitet bereits zeilenblockweise. Die Rezeptorreduktion
erzeugt 288 Werte; Pose und Form arbeiten anschliessend auf kleinen
`12 x 8 x 3`- beziehungsweise Deskriptorformen.

Diese Phase benoetigt keine dichten Flowfelder mehr. Eine andere Reihenfolge
oder fruehere Freigabe kann den bereits erreichten Prozesspeak nicht
rueckgaengig machen. Eine Prozessaufteilung oder geaenderte Messbasis ist
ausdruecklich nicht zulaessig.

## Bewertung outputneutraler Optionen

| Option | Outputneutral | Peakwirkung | Entscheidung |
| --- | --- | --- | --- |
| Frame- und Flowhash ueber direkten Buffer | ja | entfernt spaete Kopien bis `6.220.800` beziehungsweise `16.588.800` Byte | nicht peakentscheidend |
| Grauarrays direkt nach beiden Flowaufrufen freigeben | bereits umgesetzt | nur nach dem Peak | keine Entscheidungsaenderung |
| Residuenpuffer wiederverwenden | prinzipiell ja | reduziert die Phase mit aktuell `89.432.220` Byte | nicht peakentscheidend |
| Zellweise Residuen- und Statistikbildung | prinzipiell ja | reduziert Vollbild- und Perzentilpuffer nach dem Flow | nicht peakentscheidend |
| Baselines vorziehen oder spaeter ausfuehren | ja | aendert nicht die Farneback-Untergrenze | keine Entscheidungsaenderung |
| OpenCV-`R[0]`, `R[1]`, `M` oder Flow gemeinsam belegen | nein | Rollen sind gleichzeitig benoetigt | unzulaessig |
| Flow tilen oder auf kleinere Aufloesung rechnen | nein | aendert Randbedingungen beziehungsweise Algorithmusergebnis | neuer Forschungsweg |
| Parameter, Level oder Flussverfahren aendern | nein | aendert den gebundenen Algorithmus | neuer Forschungsweg |
| Prozessaufteilung, Vorwaermung oder andere Messbasis | nein | umgeht statt erfuellt die Prozessgrenze | ausgeschlossen |
| temporaeres Auslagern eines Flowfelds | nein | fuehrt eine unbelegte Rohflow-Ablage ein; ein einzelner Aufruf bleibt zu gross | ausgeschlossen |

## Harte Entscheidung

Ein konkreter Lebensdauerplan unter `134.217.728` Byte ist fuer den
unveraenderten dichten Vollformat-Farneback-Pfad nicht belegbar. Bereits die
vier gleichzeitig notwendigen OpenCV-Matrizen `R[0]`, `R[1]`, `M` und
Vollbildflow ueberschreiten die Gesamtgrenze, bevor Projektpuffer oder
Eingaben beruecksichtigt werden.

Der Pfad wird deshalb mit
`S2MK_DENSE_FULL_FORMAT_FLOW_RESOURCE_INCOMPATIBLE` geschlossen. Es erfolgt:

- keine Grenzerhoehung;
- keine Implementierung eines Lebensdauerplans;
- keine Optimierung auf Verdacht;
- keine Wiederholung der S2-MK-Qualifikation;
- keine Oeffnung der acht vorversiegelten Korpuspaare;
- keine Bewegungs- oder Kontinuitaetsinterpretation.

Ein spaeterer kleinerer Korrespondenzpfad muss als neuer Forschungsweg mit
eigener Algorithmus-, Ergebnis-, Ressourcen- und Falsifikationsbindung
beginnen.
