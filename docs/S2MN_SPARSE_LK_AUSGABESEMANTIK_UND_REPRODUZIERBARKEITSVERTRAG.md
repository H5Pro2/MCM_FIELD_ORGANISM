# S2-MN: Sparse-LK-Ausgabesemantik und Reproduzierbarkeit

## Status und Gegenstand

S2-MN korrigiert ausschliesslich die neutrale Auswertung des unter S2-MM
gebundenen pyramidal-sparsamen Lucas-Kanade-Pfads. Der S2-MM-Abbruch bleibt
unveraendert gueltig. Weder Bewegungskorrespondenz noch Sparse-LK sind durch
ihn fachlich bewertet.

Der Algorithmus, die neutrale Vollformatfixture, das feste Punktgitter, die
OpenCV-Parameter, die ABI-Bindung und die Prozess-Working-Set-Messbasis bleiben
unveraendert. Korpus, Memory, Kontext und Feld bleiben gesperrt.

## Statischer OpenCV-Befund

Der gebundene OpenCV-`4.13.0`-CPU-Pfad erzeugt fuer jeden LK-Aufruf eine
vollstaendige `uint8`-Statusmaske und initialisiert jeden Status zunaechst mit
`true`. Das optionale `float32`-Fehlerarray wird dagegen nur erzeugt; eine
vollstaendige Initialisierung aller Eintraege ist nicht gebunden.

Im LK-Invoker existieren Abbruchpfade, die auf Ebene `0` den Status auf
`false` setzen. Beim Unterschreiten von `minEigThreshold` oder bei einer
degenerierten Matrix wird bei den hier gebundenen Flags `0` kein Fehlerwert
geschrieben. Auch die abschliessende Fehlerberechnung wird nur fuer weiterhin
gueltige Tracks ausgefuehrt. Grundlage ist die unveraenderte
[OpenCV-4.13.0-Quelle](https://raw.githubusercontent.com/opencv/opencv/refs/tags/4.13.0/modules/video/src/lkpyramid.cpp),
insbesondere die Status-/Fehleranlage um Zeilen `1180...1194`, der
Eigenwertabbruch um `452...462` und die gueltigkeitsbedingte Fehlerberechnung
um `642...674`.

Damit besitzen Fehlerwerte und nachgelagerte Punktwerte eines ungueltigen
Tracks keine gebundene fachliche Semantik. Sie duerfen weder interpretiert
noch in einen Reproduzierbarkeitsdigest aufgenommen werden.

## Kanonische Gueltigkeitsprojektion

Jede der beiden identischen neutralen Auswertungen umfasst je einen
Vorwaerts- und Rueckwaertsaufruf. Fuer jeden Auswertungsdurchgang gilt:

1. Vorwaerts- und Rueckwaertsstatus muessen jeweils Form `(1536, 1)`, Typ
   `uint8` und ausschliesslich Werte aus `{0, 1}` besitzen.
2. Beide vollstaendigen Statusmasken werden in urspruenglicher Gitterordnung
   separat kanonisiert und digestiert.
3. Ein Gitterindex ist gemeinsam gueltig, wenn beide Statuswerte `1` sind,
   beide Punktpaare endlich sind und Vorwaerts- sowie Rueckwaertspunkt im
   Vollformat liegen.
4. Die gemeinsam gueltigen Indizes werden als streng aufsteigendes
   Little-Endian-`int32`-Array gebunden. Es gibt keine Nachbesetzung,
   Umordnung oder vorzeitige Beendigung.
5. Erst ueber diese Indexfolge werden Vorwaertspunkte, Rueckwaertspunkte,
   Vorwaertsfehler und Rueckwaertsfehler ausgewaehlt. Nur diese ausgewaehlten
   Werte muessen endlich sein und duerfen digestiert oder statistisch
   ausgewertet werden.
6. Bewegung, Zyklusresiduum und bewegungskompensiertes RGB-Residuum werden
   ausschliesslich fuer dieselbe geordnete Indexfolge gebildet.

Punkt- und Fehlerbereiche ausserhalb dieser Projektion werden weder auf
Endlichkeit geprueft noch digestiert, zusammengefasst oder anderweitig
interpretiert. Die vollstaendigen Statusmasken bleiben dennoch beweiskraeftig
gebunden.

Mindestens `1.152` gemeinsam gueltige Tracks bleiben erforderlich.

## Komponentengenaue Reproduzierbarkeit

Die beiden neutralen Auswertungen werden nicht ueber einen einzigen
Gesamtdictvergleich entschieden. Fuer jede folgende Komponente werden
Erstdurchgangsdigest, Zweitdurchgangsdigest und exakte Digestgleichheit
einzeln aufgezeichnet:

- vollstaendiger Vorwaertsstatus;
- vollstaendiger Rueckwaertsstatus;
- geordnete gemeinsam gueltige Gitterindizes;
- gueltige Vorwaertspunkte;
- gueltige Rueckwaertspunkte;
- gueltige Vorwaertsfehler;
- gueltige Rueckwaertsfehler;
- Verschiebungswerte;
- Zyklusresiduen;
- RGB-Residuen.

Es gilt weiterhin exakte Bitgleichheit. Es gibt keine Toleranz, Rundung,
Sortierung nach Ergebniswerten oder Normalisierung. Zusammenfassungen werden
aus dem Erstdurchgang nur dann fachlich publiziert, wenn alle zehn
Komponenten bitgleich sind; die komponentengenauen Abweichungsbelege bleiben
auch bei einem negativen Ergebnis erhalten.

## Ressourcen- und Ablaufbindung

Die Prozessmessung verwendet unveraendert:

- dieselbe Windows-`PROCESS_MEMORY_COUNTERS`-ABI;
- denselben Baselinezeitpunkt nach Anlage der zwei RGB-Frames und des Gitters;
- denselben 1-ms-Samplingthread;
- `process_peak_delta + 12.441.600` residente RGB-Eingabebytes;
- die strikte Grenze `measured_peak_with_inputs < 134.217.728` Byte.

Die Peakmessung wird nach beiden LK-Auswertungen abgeschlossen und
aufgezeichnet, auch wenn eine gueltige Ergebniskomponente abweicht. Es gibt
keine Vorwaermung, Prozessaufteilung, Installation, Aktualisierung oder
Ersatzbibliothek.

Der neue neutrale Preflight darf genau einmal unter
`s2mn-sparse-lk-output-semantics-preflight-20260905-01` laufen. Er oeffnet
keine Korpusdatei und ruft keine Projekt-, Memory-, Kontext- oder Feldfunktion
auf.

## Entscheidung

Nur wenn

- alle Laufzeit-, Binaer- und Ausfuehrungsbindungen gelten;
- mindestens `1.152` gemeinsam gueltige Tracks vorliegen;
- alle zehn gueltigen Ergebniskomponenten bitgleich sind; und
- der gemessene Peak strikt unter `134.217.728` Byte liegt,

lautet der terminale Befund:

`S2MN_SPARSE_LK_PATH_AVAILABLE`

Weicht eine gueltige Komponente ab, wird ihr Befund einzeln ausgewiesen und
der Pfad lautet `S2MN_SPARSE_LK_PATH_UNAVAILABLE`. Eine
Ressourcenueberschreitung fuehrt zum selben terminalen Status mit eigener
Fehlerklassifikation.

Ein positiver S2-MN-Befund bestaetigt nur die lokale technische
Verfuegbarkeit des exakt gebundenen Sparse-LK-Pfads. Er ist noch kein
Bewegungs-, Fortsetzungs-, Objektidentitaets-, Memory-, Kontext- oder
Feldbefund.
