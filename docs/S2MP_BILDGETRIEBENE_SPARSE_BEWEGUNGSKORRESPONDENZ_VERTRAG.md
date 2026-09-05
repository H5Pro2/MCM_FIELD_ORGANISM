# S2-MP: Bildgetriebene sparse Bewegungskorrespondenz

## Zweck

S2-MP ersetzt nicht Sparse-LK, sondern ausschliesslich das fuer S2-MO
ungeeignete feste Vollbildgitter. Kandidatenpunkte werden deterministisch
aus der tatsaechlich sichtbaren Struktur des ersten Frames abgeleitet und
danach mit der unveraenderten S2-MN-LK-Bindung vorwaerts und rueckwaerts
gemessen.

Die Ausgabe ist Korrespondenzevidenz, keine Objektidentitaet. Memory,
Kontext und Feld bleiben ausgeschlossen. Der geschlossene S2-MO-Lauf wird
nicht wiederholt oder nachtraeglich diagnostiziert.

## Kandidatendetektor

Die einzige zugelassene Kandidatenregel ist Shi-Tomasi ueber
`cv2.goodFeaturesToTrack`. OpenCV beschreibt die Funktion als Auswahl
starker Ecken aus einem Graubild; `qualityLevel` verwirft schwache
Eigenwertantworten und `minDistance` unterdrueckt nahe Nachbarn.

Vor jedem spaeteren Korpuszugriff muessen folgende Werte versiegelt sein:

| Bindung | Wert |
| --- | ---: |
| Vollformat | `1920 x 1080 RGB8` |
| Grauprojektion | `(77R + 150G + 29B + 128) >> 8` |
| Zellen | `12 x 8` |
| `maxCorners` je Zelle | `16` |
| Gesamtmaximum | `1.536` |
| `qualityLevel` | `0,01` |
| `minDistance` | `8,0` Pixel |
| `blockSize` | `7` |
| `useHarrisDetector` | `False` |
| `k` | `0,04` |

Der Detektor laeuft fuer jede der 96 nicht ueberlappenden Zellen genau
einmal in Zeilenreihenfolge. Innerhalb einer Zelle werden die ausgegebenen
`float32`-Koordinaten kanonisch nach `(y, x)` sortiert und anschliessend in
Vollbildkoordinaten ueberfuehrt. Es gibt keine Nachbesetzung, Subpixel-
Verfeinerung, ROI aus Sollrollen oder Auswahl anhand eines zweiten Frames.

Kandidatendigest, Kandidatenzahl, Belegung jeder Zelle und belegte Zellzahl
werden gebunden. Uniforme oder strukturarme Bilder duerfen null oder wenige
Kandidaten liefern.

## Sparse-LK und gueltige Projektion

Die LK-Parameter bleiben identisch zu S2-MN:

- Fenster `21 x 21`;
- Ebenen `0...3`;
- maximal `30` Iterationen und Epsilon `0,01`;
- Flags `0` und `minEigThreshold=0,0001`;
- ein OpenCV-Thread, OpenCL aus.

Bei mindestens einem Kandidaten erfolgen genau ein Vorwaerts- und ein
Rueckwaertsaufruf. Beide vollstaendigen Statusmasken werden gebunden.
Punkte, Fehler, Bewegungswerte, Zyklusresiduen und RGB-Residuen werden nur
fuer gemeinsam statusgueltige, endliche und geometrisch innerhalb des
Vollformats liegende Tracks ausgewertet. Ihre Reihenfolge bleibt die
urspruengliche Kandidatenreihenfolge. Ungueltige Punkt- und Fehlerbereiche
werden weder interpretiert noch digestiert.

## Evidenzstatus

S2-MP fuehrt keine Bewegungs-Matchschwelle ein. Eine Messung besitzt fuer
einen spaeteren ordinalen Vergleich lediglich dann ausreichende raeumliche
Grundlage, wenn mindestens `32` gueltige Tracks aus mindestens `4`
verschiedenen Rasterzellen vorliegen.

- Grenze erreicht: `MOTION_EVIDENCE_AVAILABLE`;
- Grenze nicht erreicht: `INSUFFICIENT_MOTION_EVIDENCE`.

Beide Werte sind technisch gueltige Messergebnisse. Insbesondere geringe
Kandidaten- oder Trackzahl ist kein `NOT_EVALUABLE`. `NOT_EVALUABLE` bleibt
auf Quellen-, Zeit-, Typ-, Geometrie-, Digest-, Runtime-, Ressourcen- oder
Ausfuehrungsfehler beschraenkt.

Die absoluten Grenzen `32/4` sind vor jedem Korpus fest und werden nicht aus
an dessen Resultate angepasst. Sie ersetzen keine Objekt- oder
Kontinuitaetsschwelle.

## Raeumliche und numerische Ausgabe

Der unveraenderliche Befund bindet:

- neutrale Paar-, Quellen-, Zeit- und Payloaddigests;
- Detektor- und LK-Bindungsdigest;
- Kandidaten- und gueltige Indexdigests;
- beide vollstaendigen Statusmaskendegests;
- nur gueltige Punkt-, Fehler-, Bewegungs-, Zyklus- und RGB-Digests;
- Kandidaten- und gueltige Anzahl je `12 x 8`-Zelle;
- Kandidatenzahl, gueltige Trackzahl und jeweilige Zellabdeckung;
- feste Mittelwert-, Median-, p95- und Maximum-Zusammenfassungen;
- Evidenzstatus und kanonischen Ergebnisdigest.

Rohframes, Graubilder, Punktlisten und Fehlerarrays erscheinen nicht in der
Ausgabe.

## Neutrale Qualifikation

Vor jedem Korpus darf genau eine korpusfreie Qualifikation laufen. Sie
verwendet nur unabhaengige neutrale Vollformatbilder und prueft:

Die Qualifikations-ID
`s2mp-neutral-feature-sparse-qualification-20260905-01` endete vor jedem
Testkoerper an einer falschen privaten Paketimportform und ist nicht
qualifizierend. Die unveraenderten zehn Tests duerfen nach ausschliesslicher
Korrektur dieses Imports genau einmal unter
`s2mp-neutral-feature-sparse-qualification-20260905-02` laufen.

1. feste Detector-/LK- und Runtimebindung;
2. exakte ganzzahlige RGB-zu-Y-Projektion;
3. deterministische Punktwahl und kanonische Ordnung;
4. Maximum, Eindeutigkeit und Zellzuordnung;
5. einen gueltigen Translationstrack mit Vorwaerts-/Rueckwaertsbindung;
6. komponentenweise Endlichkeit nur im gueltigen Teil;
7. regulaeres `INSUFFICIENT_MOTION_EVIDENCE` auf strukturarmer Eingabe;
8. Fail-Closed bei Payload-, Zeit-, Form- und Typfehlern;
9. unveraenderte Eingabeframes und fehlende Roharrays in der Ausgabe;
10. Prozesspeak strikt unter `134.217.728` Byte.

Die Qualifikation oeffnet keinen S2-MJ- oder anderen Korpus, importiert keine
Memory-, Kontext- oder Feldmodule und fuehrt keine Projektfunktion dieser
Bereiche aus.

## Spaetere Forschungsgrenze

Erst nach bestandener neutraler Qualifikation darf ein neuer Korpus
vorversiegelt werden. Dieser Korpus darf nicht aus S2-MO angepasst werden.
Ein spaeterer Lauf muss gueltige Trackzahl, raeumliche Abdeckung und Residuen
getrennt berichten sowie direkte Pixel-, Rezeptor-, Pose- und Formbaselines
gleichberechtigt ausweisen.

Nur ein vorab gebundener ordinaler Korrespondenzvorteil koennte die offene
Bindungsfrage aus S2-MI erneut begruenden. S2-MP selbst autorisiert keine
Nutzung in `A_RECENT`, `B_STABLE`, Kontext oder Feld.
