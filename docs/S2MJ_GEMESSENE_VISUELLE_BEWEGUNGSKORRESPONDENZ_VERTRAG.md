# S2-MJ: Gemessene visuelle Bewegungskorrespondenz

## Status

`S2MJ_STATIC_MOTION_CORRESPONDENCE_CONTRACT_COMPLETE`

Implementierungsstatus:

`S2MJ_IMPLEMENTATION_AND_MATERIALIZATION_NOT_AUTHORIZED`

S2-MJ bindet eine begrenzte, rein visuelle Messung vor der vorhandenen
Rezeptorreduktion:

```text
zwei aufeinanderfolgende kanonische RGB8-Frames
-> gemessener dichter Vorwaerts-/Rueckwaertsfluss
-> numerische Bewegung, Ueberdeckung und Konsistenz
```

Die Ausgabe behauptet weder Objektidentitaet noch Familienzugehoerigkeit.
Sie bildet keinen Memorykandidaten, nimmt keine Kontextzulassung vor und
veraendert weder Feld noch Memory. S2-MI bleibt unveraendert gueltig: Mit
den dort geprueften statischen Signalen war invariante Erfahrungsbindung
nicht beobachtbar.

Ausgangscommit ist `7599955`.

## Gebundener Quellenstand

| Rolle | Quelle | SHA-256 |
| --- | --- | --- |
| kanonische AV-Grenze | `tools/_s2jo_private_canonical_av_boundary.py` | `50a39fb3865fbd11b3577f79db2983f9dd3260262dee0f199ae5f884bed4ef71` |
| bestehende Pose-/Formprojektion | `tools/_s2lv_private_pose_form_projection.py` | `64125b0ff0e469b792c1969f35b9972ca60723fd2503b1194fc703042eba34e4` |
| unveraenderter visueller Rezeptor | `mcm_field_organism/finite_video_path.py` | `d09cb6ba35fd061e4a243b7ed2112597a194e75abd026d7cc3ab7aa89922c07a` |
| Kernabhaengigkeiten | `requirements.txt` | `5c86bdf12352967045a98cbd6abbcbc6b3440672ddee3f3e9b8f1095fedeeed3` |

`CanonicalVisualFrameV1` bleibt die einzige funktionale Framegrenze. Jeder
Frame hat exakt `1920 x 1080 x 3` zusammenhaengende `uint8`-Werte in
RGB-Reihenfolge, eine native visuelle Uhr, ein halb offenes Zeitfenster,
einen Pixelpayloaddigest und einen quellenneutralen funktionalen Digest.

`SourceAuditProvenanceV1` darf Adapter-, Generator- oder Laufzeitidentitaet
fuehren. Diese Daten bleiben reine Auditprovenienz und sind keine Eltern der
Bewegungsmessung, der Baselines oder einer spaeteren Entscheidung.

## Fehlende lokale Faehigkeitsbindung

Im gebundenen Projektstand existiert kein qualifizierter optischer Fluss
und keine Pixelkorrespondenz. OpenCV wird lokal fuer Aufnahme und
Bilddekodierung verwendet, ist in `requirements.txt` aber nicht als
reproduzierbare Flow-Abhaengigkeit festgeschrieben.

Vor jeder Korpusmaterialisierung ist deshalb genau ein isolierter
Faehigkeitspreflight erforderlich. Er muss eine konkrete lokale
OpenCV-Version, den Digest von `cv2.getBuildInformation()`, die Existenz von
`calcOpticalFlowFarneback`, CPU-Einzelthreadbetrieb und deaktiviertes OpenCL
binden. Er prueft nur Form, Datentyp, Endlichkeit und deterministische
Wiederholbarkeit auf einer neutralen Kleinstfixture. Scheitert eine Bindung,
lautet der Abschluss:

`S2MJ_DENSE_FLOW_PATH_UNAVAILABLE`

Es gibt in diesem Fall keinen Ersatzalgorithmus, keine Parameterwahl und
keinen Korpuslauf unter derselben ID.

## Typisierte Datenformen

### `VisualMotionPairV1`

Ein Paar bindet:

- neutrale `pair_id`;
- `frame_0_functional_digest` und `frame_1_functional_digest`;
- gemeinsame `visual_source_clock_id`;
- beide nativen Framefenster;
- strikt fortschreitende, nicht ueberlappende Zeit;
- Breite `1920`, Hoehe `1080`, Kanalzahl `3`, `RGB8`;
- `motion_algorithm_binding_digest`;
- kanonischen `pair_digest`.

Die Form enthaelt keine Fallrolle, Generatorbewegung, Formklasse,
Sollentscheidung oder erwartete Fortsetzung.

### `DenseFlowAlgorithmBindingV1`

Der erste Implementierungskandidat ist dichter Farneback-Fluss mit exakt:

```text
pyr_scale  = 0.5
levels     = 5
winsize    = 21
iterations = 5
poly_n     = 7
poly_sigma = 1.5
flags      = 0
```

Vorwaerts- und Rueckwaertsfluss verwenden dieselbe Bindung. Die einzige
zulaessige Grauprojektion wird vorab und ohne OpenCV-Farbraumautomatik aus
RGB8 gebildet:

```text
Y = ((77 * R + 150 * G + 29 * B + 128) >> 8)
```

Die Multiplikation und Summe erfolgen in `uint32`, das Ergebnis ist
`uint8`. Es gibt kein Resize, keine Gammakorrektur, Normalisierung,
Histogrammkorrektur oder sonstige Farbumwandlung. Interne Pyramiden sind
ausschliesslich Bestandteil des gebundenen Flow-Algorithmus.

Beide Flussfelder besitzen exakt die Form `1080 x 1920 x 2`, Datentyp
`float32` und nur endliche Werte. Fuer Digests werden sie als
zusammenhaengende Little-Endian-`float32`-Bytes in Zeilenreihenfolge
kanonisiert. Ihre Bytes sind fluechtige Messzwischenwerte und werden nicht
als Laufartefakt gespeichert.

### `MotionCellSummaryV1`

Das vorhandene `12 x 8`-Raster erzeugt genau 96 quellenneutrale
Zellzusammenfassungen. Jede bindet ausschliesslich:

- Zellzeile und Zellspalte;
- Pixelzahl und geometrisch gueltige Korrespondenzzahl;
- Mittelwert von `dx` und `dy`;
- Mittelwert, Median und p95 des Bewegungsbetrags;
- Mittelwert, Median und p95 des Vorwaerts-/Rueckwaertsresiduums;
- Mittelwert, Median und p95 des bewegungskompensierten RGB-Residuums.

Perzentile verwenden die feste lineare NumPy-Definition. NaN, Inf,
abweichende Zellgroesse oder eine unvollstaendige Zelle stoppen fail-closed.

### `MeasuredVisualMotionV1`

Der unveraenderliche Messbefund bindet:

- `pair_digest` und `motion_algorithm_binding_digest`;
- Vorwaerts- und Rueckwaertsflussdigest;
- Gesamtpixelzahl `2.073.600`;
- Anzahl und Anteil geometrisch gueltiger Vorwaertskorrespondenzen;
- globale Betrags-, Zyklusresiduum- und RGB-Residuumstatistiken;
- exakt 96 `MotionCellSummaryV1`-Digests;
- Digest der geordneten Zellzusammenfassungen;
- `measurement_digest`.

Fuer Pixel `p` ist `q = p + F01(p)`. Eine Korrespondenz ist geometrisch
gueltig, wenn `q` innerhalb des zweiten Frames liegt. Nur fuer diese Punkte
wird `F10(q)` bilinear aus dem Rueckwaertsfluss gelesen. Das
Zyklusresiduum ist

```text
norm(F01(p) + bilinear(F10, q), 2)
```

Das bewegungskompensierte RGB-Residuum ist der mittlere absolute
Kanalunterschied zwischen Frame 0 an `p` und dem bilinear gelesenen Frame 1
an `q`, normiert durch `255`. Bilineare Randbehandlung, Summationsreihenfolge
und Perzentildefinition sind Bestandteil der Algorithmusbindung.

Keines dieser Felder ist ein Match-, Identitaets- oder Objektstatus. Ohne
spaetere getrennte Auswertung sind es nur Messwerte.

## Vergleichsbaselines

Nach abgeschlossener Flow-Messung werden dieselben beiden Frames jeweils
genau einmal durch den unveraenderten visuellen Rezeptor reduziert. Erst
danach duerfen die Rohframes verworfen werden. Die Vergleichsform bindet pro
Paar:

1. normierte absolute RGB8-Pixel-L1-Distanz;
2. L1-Distanz der beiden unveraenderten 288-Werte-Rezeptorzustaende;
3. komponentenweise `PoseV1`-Differenzen;
4. L1-Distanz der beiden vorhandenen `FormDescriptorV1`-Vektoren;
5. die Bewegungs-, Ueberdeckungs- und Konsistenzwerte aus
   `MeasuredVisualMotionV1`.

Flow und Baselines erhalten dieselben Frame-Digests, teilen aber keine
Entscheidungshelfer. Rezeptor-, Pose- oder Formwerte duerfen den Flow nicht
parametrisieren. Flowwerte duerfen Rezeptor, Pose oder Form nicht
veraendern.

## Vorversiegelter endlicher Korpus

Vor dem Faehigkeitspreflight und vor jeder Pixel-, Rezeptor- oder
Flowauswertung muss ein `PresealedMotionCorpusPlanV1` materialisiert werden.
Er bindet exakt acht unabhaengige Framepaare und 16 eindeutige Frames:

- zwei fortgesetzte Bewegungen;
- zwei Formwechsel bei vergleichbarer aktueller Bildbelegung;
- zwei fortgesetzte Bewegungen mit Teilverdeckung im zweiten Frame;
- zwei Szenenspruenge.

Die beiden Wiederholungen jeder Evaluationsklasse verwenden verschiedene
Bewegungsrichtungen und getrennte Quellfenster. Generator, Seed, Geometrie,
Farben, Formen, Okkluder, Zeitfenster, RGB8-Payloaddigests und
Framefunktionsdigests werden literal versiegelt. Danach darf kein Wert
gesucht, ersetzt oder anhand eines Messresultats angepasst werden.

Im neutralen Ausfuehrungsplan erscheinen nur `frame-001..frame-016` und
`pair-001..pair-008`. Generatorbewegung, Formfamilie und die vier
Evaluationsklassen stehen ausschliesslich in einer unabhaengig vorab
versiegelten Evaluationswurzel. Diese Wurzel ist kein Elternbeleg von
Framevalidierung, Flow, Rezeptor oder Baseline. Eine
`MotionEvaluationRunBindingV1` verbindet sie erst nach dem vollstaendigen
`MotionExecutionEvidencePackageV1`.

Die Generatorparameter duerfen zur einmaligen Erzeugung und Bindung der
Quellbytes verwendet werden. Sie gelangen weder in `VisualMotionPairV1`
noch in den Algorithmus oder Messbefund. Der Lauf misst die Pixel und liest
keine vorgegebene Bewegung aus dem Generator.

## Ausfuehrungsreihenfolge und Rohdatenlebenszyklus

Fuer jedes Paar gilt strikt:

1. beide kanonischen Frames und ihre vorversiegelten Payloaddigests pruefen;
2. `VisualMotionPairV1` bilden;
3. beide Grauprojektionen erzeugen;
4. Vorwaerts- und Rueckwaertsfluss messen;
5. Bewegung, geometrische Ueberdeckung und Konsistenz zusammenfassen;
6. beide unveraenderten 288-Werte-Rezeptorzustaende bilden;
7. Pixel-, Rezeptor-, Pose- und Formbaselines berechnen;
8. nur Digests, Zusammenfassungen und reduzierte Werte veroeffentlichen;
9. RGB-, Grau-, Flow- und Interpolationspuffer loeschen, bevor das naechste
   Paar geladen wird.

Es duerfen hoechstens zwei RGB-Frames desselben Paares gleichzeitig
resident sein. Kein Rohframe, Graubild, Flussfeld, Warppuffer,
Generatorparameter oder Pixelkorrespondenzarray erscheint im Ergebnis,
Receipt, Feld, Memory oder Kontext.

## Ergebnis- und Falsifikationsregeln

S2-MJ waehlt keine numerische Matchschwelle. Die getrennte Auswertung prueft
ausschliesslich vorab gebundene ordinale Aussagen innerhalb der beiden
gepaarten Fallgruppen:

- fortgesetzte Bewegung muss geringeres Zyklus- und
  bewegungskompensiertes RGB-Residuum als der zugehoerige Formwechsel und
  Szenensprung besitzen;
- Teilverdeckung darf den gemeinsamen Bewegungsanteil erhalten, muss aber
  gegenueber der unbedeckten Fortsetzung groessere obere
  RGB-Residuumquantile ausweisen;
- ein Szenensprung darf nicht als ebenso konsistente Fortsetzung wie sein
  gebundener Fortsetzungsfall erscheinen;
- die Baselines werden nur berichtet; sie autorisieren oder blockieren
  keinen Messbefund.

Die moeglichen fachlichen Abschluesse sind:

- `S2MJ_MOTION_CORRESPONDENCE_OBSERVABLE`: alle vorgebundenen ordinalen
  Relationen gelten in beiden Fallgruppen;
- `S2MJ_MOTION_CORRESPONDENCE_MIXED`: technisch vollstaendig, aber nur ein
  Teil der Relationen gilt;
- `S2MJ_MOTION_CORRESPONDENCE_NOT_SEPARABLE`: die gemessene
  Korrespondenz trennt Fortsetzung und Austausch in den gebundenen
  Kernrelationen nicht;
- `NOT_EVALUABLE`: Quellen-, Zeit-, Form-, Digest-, Algorithmus- oder
  Belegfehler.

Keiner dieser Abschluesse behauptet Objektidentitaet. Nur der erste wuerde
eine spaetere, separat zu vertraglich bindende Nutzung als fluechtige
Kontinuitaetsevidenz in `A_RECENT` rechtfertigen. S2-MJ selbst autorisiert
diese Integration nicht.

## Nichtzirkularitaet und Fail-Closed-Grenzen

Der Digestgraph ist strikt vorwaertsgerichtet:

```text
SourcePlan -> RGB8 payloads -> CanonicalVisualFrameV1
CapabilityReceipt -> DenseFlowAlgorithmBindingV1
CanonicalVisualFrameV1 + DenseFlowAlgorithmBindingV1
-> VisualMotionPairV1
-> flow digests -> cell summaries -> MeasuredVisualMotionV1
-> receptor/pose/form baseline receipts
-> MotionExecutionEvidencePackageV1

EvaluationPlanSeal + MotionExecutionEvidencePackageV1
-> MotionEvaluationRunBindingV1 -> EvaluationResult
```

Verboten sind insbesondere:

- Generatortranslation, Fallrolle oder Sollklasse als Floweingang;
- Ableitung einer Korrespondenz aus Zeitnaehe allein;
- Wahl oder Aenderung von Parametern nach Sichtung eines Ergebnisses;
- Rueckrechnung von Bewegung aus PPB-, Memory-, Kontext- oder Feldzustand;
- Ersetzung fehlender Flowwerte durch Rezeptor-, Pose- oder Formwerte;
- Interpretation kleiner Distanz als Objektidentitaet;
- Speicherung der Rohframes oder dichten Flussfelder als Memoryevidenz;
- Bildung eines Kandidaten, einer Rangfolge oder einer Kontextzulassung.

Falsche Uhr, nicht fortschreitende Fenster, Digestabweichung, falsche
Geometrie, ungueltiger Datentyp, NaN/Inf, unvollstaendiges Flussfeld,
fehlende Zelle, nachtraeglich geaenderter Plan oder Evaluationseinfluss auf
den Lauf stoppen ohne fachliche Interpretation.

## Ressourcen- und Operationsgrenzen

Der spaetere begrenzte Lauf bindet:

- 16 kanonische RGB8-Frames;
- acht unabhaengige Paare;
- 16 dichte Flowaufrufe, je acht vorwaerts und rueckwaerts;
- 16 unveraenderte visuelle Rezeptoraufrufe;
- 16 Rezeptorzustaende zu je 288 Werten;
- 768 Zellzusammenfassungen;
- acht Vergleichsreceipts;
- hoechstens 96 typisierte Top-Level-Arbeitsoperationen.

Die Obergrenze von 96 Operationen besteht lueckenlos aus:

| Klasse | Anzahl |
| --- | ---: |
| Quellenpruefung und kanonische Framebindung | 16 |
| Grauprojektion | 16 |
| unveraenderte visuelle Rezeptorreduktion | 16 |
| Paarbindung | 8 |
| Vorwaertsfluss | 8 |
| Rueckwaertsfluss | 8 |
| Bewegungs- und Zellzusammenfassung | 8 |
| gemeinsamer Baselinevergleich | 8 |
| Quellenplanbindung | 1 |
| Ausfuehrungsplanbindung | 1 |
| unabhaengige Evaluationsplanversiegelung | 1 |
| exklusive Laufreservierung | 1 |
| Ausfuehrungsevidenzpublikation | 1 |
| Evaluation-Run-Bindung | 1 |
| reine Auswertung | 1 |
| atomarer Ergebnis- und Terminalabschluss | 1 |
| **Gesamt** | **96** |

Die gesamte RGB8-Quellmenge betraegt `99.532.800` Byte, wird aber
paarweise gestreamt. Zwei residente RGB-Frames belegen `12.441.600` Byte,
zwei Grauprojektionen `4.147.200` Byte und zwei dichte `float32`-Flussfelder
`33.177.600` Byte. Der spaetere Implementierungsvertrag muss einschliesslich
Interpolations- und Statistikpuffern einen gemessenen Peak unter
`134.217.728` Byte nachweisen.

Persistente kanonische Artefakte bleiben begrenzt auf:

- Korpus- und Ausfuehrungsplan zusammen hoechstens `131.072` Byte;
- jeden Paarbefund hoechstens `98.304` Byte;
- vollstaendiges Ausfuehrungsevidenzpaket hoechstens `1.048.576` Byte;
- Evaluationsbindung, Ergebnis und Terminal zusammen hoechstens
  `131.072` Byte;
- Gesamtartefaktbudget hoechstens `1.310.720` Byte.

Rohpayloads und dichte Flussfelder zaehlen zum fluechtigen Arbeitsbudget und
sind im persistenten Budget ausdruecklich unzulaessig. Die Grenzwerte sind
vor einer Implementierung an den vollstaendigen kanonischen Formen statisch
neu zu materialisieren; sie duerfen nicht still erhoeht werden.

## Architekturgrenze

S2-MJ fuegt dem System keine Memoryebene hinzu. Es misst eine bisher
fehlende Eigenschaft an der Wahrnehmungsgrenze. Die spaetere Architektur
bleibt bis zu einem unabhaengigen positiven Befund gesperrt:

```text
gemessene Pixelbewegung -X-> A_RECENT-Kontinuitaetsevidenz
                         -X-> B_STABLE-Zuordnung
                         -X-> Kontextzulassung
                         -X-> Feldwirkung
```

Memory, Kontext, Feld, PPB, TSPM, Rezeptorschwellen und bestehende
Deskriptoren bleiben unveraendert. Die Untersuchung endet nach Messung,
Baselinevergleich und getrennter Auswertung.

## Vertragsgrenze

- neue Produktionsmodule: `0`;
- neue Runner-, Recorder-, Memory- oder Feldmodule: `0`;
- Rezeptor-, Flow-, Memory-, Kontext- und Feldaufrufe: `0`;
- Tests und Korpusmaterialisierungen: `0`;
- README-Aenderungen: `0`.

Der naechste zulaessige Schritt ist ausschliesslich die Vorversiegelung des
achtpaarigen Korpus und ein isolierter lokaler Flow-Faehigkeitspreflight.
Erst bei bestandenem Preflight darf eine kleine private Mess- und
Vergleichsimplementierung separat freigegeben werden.
