# S2-LS - Vorab eingefrorenes AV-Train/Holdout-Korpus

## Status und Funktionsfrage

`S2LS_STATIC_PRESEALED_AV_CORPUS_FUNCTION_AND_FALSIFICATION_CONTRACT`

S2-LS ersetzt keine S2-LR-Fixture und setzt den terminal geschlossenen
S2-LR-Versuch nicht fort. Der Vertrag bindet einen neuen, begrenzten
Funktionsvergleich:

> Generalisiert das bestehende rollenfreie Zwei-Bereich-Memory aus mehreren
> vorab feststehenden audiovisuellen Erfahrungen auf ebenfalls vorab
> zurueckgehaltene Varianten, und wie unterscheiden sich adaptive Bank,
> eingefrorener Erstprototyp und Replay dabei tatsaechlich?

Ein adaptiver Sieg ist weder Materialisierungsvoraussetzung noch erwarteter
Pflichtbefund. Treffer, Verwechslungen, Enthaltungen und Fehlschlaege sind
gleichwertig auswertbare Funktionsergebnisse.

## Unveraenderte Grundlage

Unveraendert wiederverwendet werden:

- der qualifizierte rollenfreie S2-LO/S2-LQ-Strompfad;
- 48 auditive und 288 visuelle Default-Live-Rezeptorwerte;
- die bestehenden Rezeptoren, Fast-/Slow-Schwellen, Updatefaktoren,
  Stabilitaets-, LRU- und Ablaufregeln;
- `A_RECENT` und `B_STABLE` als einzige oeffentliche Memorybereiche;
- getrennte auditive und visuelle Auswertung;
- read-only Teilhinweisabruf und die vorhandenen Direktbaselines.

Nicht zulaessig sind neue Memoryschichten, neue Matchingregeln,
Schwellenkalibrierung, Feldrueckwirkung, semantische Labels im Strom oder eine
neue Recorderplattform.

## Korpusursprung

Das endliche Korpus enthaelt mehrere Wahrnehmungsfamilien mit jeweils
mehreren Trainings- und Holdoutvarianten. Eine Variante ist nur zulaessig,
wenn sie vor jeder Rezeptoranalyse auf einem der folgenden Wege feststeht:

1. als unveraenderte endliche RGB8-/PCM_F32LE-Aufnahme; oder
2. als unabhaengig erzeugte Variante aus einer vorab versiegelten
   Quellfixture, einem festen Transformationsrezept und einem festen Seed.

Das Transformationsrezept darf keine Rezeptorwerte, Memoryzustaende,
Schwellen, Prototypen oder Ergebnisse lesen. Nach der Versiegelung sind weder
Variantenersatz noch Parameter- oder Seedwechsel zulaessig.

Alle visuellen Quellen muessen kanonische `1920x1080 RGB8`-Frames liefern.
Alle auditiven Quellen muessen die bereits gebundene mono-
`48000 Hz PCM_F32LE`-Form und deren native Zeitfenster erfuellen. Resize,
Resampling, Normalisierung und Clipping sind ausgeschlossen.

## Vorabversiegelung

Vor dem ersten Rezeptoraufruf entsteht genau ein unveraenderlicher
`PresealedAVCorpusPlanV1`. Er bindet mindestens:

- Korpus-ID, Schemas und Konfigurationsdigests;
- fuer jede Quellvariante eine neutrale Sample-ID, Modalitaetsrollen,
  Geometrie, Zeitform und SHA-256 der kanonischen RGB-/PCM-Bytes;
- einen vollstaendigen, disjunkten Train/Holdout-Split;
- die unveraenderliche Ereignisreihenfolge des Trainingsstroms;
- getrennte Auswertungszuordnungen fuer Wahrnehmungsfamilie und Variante;
- die drei Vergleichsarme und alle Metriken;
- ein Verbot jeder nachtraeglichen Korpus- oder Splitmutation.

Der Plandigest wird gebildet, bevor ein Rezeptorwert existiert. Die
Familien-, Train/Holdout- und Sollzuordnungen gehoeren zu einer getrennten
Auswertungswurzel. Der Laufpfad erhaelt nur neutrale Sample-, Ereignis-,
Quellen- und Zeitbelege.

Die Laufwurzel darf aus dem Auswertungsplan weder Familiennamen noch
Splitrolle, Zielwerte oder erwartete Entscheidungen uebernehmen. Beide
Wurzeln werden erst nach vollstaendig abgeschlossener Laufaufzeichnung durch
eine read-only `EvaluationRunBinding` verbunden.

## Rezeptormaterialisierung

Nach der Versiegelung werden die Quellen genau einmal durch die unveraenderten
Rezeptoren gefuehrt. Die Materialisierung prueft ausschliesslich technische
Gueltigkeit:

- Payloaddigest, Form, Dimension, native Uhr und Reihenfolge stimmen;
- jede Quelle erzeugt exakt 48 auditive und 288 visuelle Werte;
- identische Payloads bleiben deterministisch;
- Rohdaten werden nach der Reduktion verworfen und nicht in Memory,
  Ergebnis oder Receipt gespeichert;
- Rezeptor- und AV-Digests enthalten keine Familien-, Split- oder Sollrolle.

Gemessene Distanzen werden aufgezeichnet, aber nicht als Startgate gegen
`0.02`, `0.01` oder `0.2` verwendet. Keine Variante darf wegen eines
unerwuenschten Distanzwerts ersetzt, skaliert oder erneut erzeugt werden.

Technisch ungueltige Quellen ergeben `NOT_EVALUABLE`. Eine gueltige, aber
schlecht getrennte oder nicht generalisierbare Geometrie bleibt dagegen ein
regulaerer Funktionsbefund.

## Trainingsstrom

Der Trainingsstrom verarbeitet ausschliesslich die versiegelten
Trainingsvarianten in der vorab gebundenen Reihenfolge. Jedes vollstaendige
AV-Ereignis wird ueber den bestehenden S2-LO/S2-LQ-Pfad verarbeitet:

- derselbe reduzierte Rezeptorzustand geht an die unabhaengigen Feld- und
  Memory-Geschwisterprojektionen;
- genau eine atomare B4-/TSPM-Formation findet statt;
- der Laufpfad kennt keine Familie, Holdoutrolle oder Erfolgsprognose;
- Holdoutquellen duerfen weder Formation noch Baselinetraining erreichen.

Nach dem Training werden die gebundenen Verdraengungsereignisse ausgefuehrt,
ohne ihr Ergebnis vorab zu fordern. Der tatsaechliche Bestand von B4, Fast
und beiden Slow-Banken wird vollstaendig und modalitaetsgetrennt
aufgezeichnet.

## Vergleichsarme

Alle versiegelten Holdouts werden erst nach Abschluss des Trainings und unter
strikt spaeteren Quellenzeiten read-only ausgewertet. Audio und Video werden
getrennt berichtet. Fuer jede Modalitaet laufen mit identischen Eingaben:

1. `ADAPTIVE_BANK`: tatsaechlicher finaler Slow-Prototyp;
2. `FROZEN_FIRST_PROTOTYPE`: unveraenderter erster gueltiger
   Familienprototyp;
3. `REPLAY_NEAREST_EXEMPLAR`: naechstes einzelnes Trainingsexemplar.

Frozen und Replay werden unabhaengig aus den versiegelten Trainingsbelegen
gebildet. Sie duerfen weder Codepfade noch Ergebnisse der adaptiven Bank
uebernehmen. Alle drei Arme verwenden dieselben bestehenden Distanzregeln;
es gibt keine armbezogene Toleranz oder Rangkorrektur.

Bei Teilhinweisen bleibt der vollstaendige vorhandene Slotscan die
Engineeringbaseline. Mehrere Treffer fuehren zur bestehenden Enthaltung und
nicht zu Ranking, Verschmelzung oder automatischer Auswahl.

## Messungen

Der nachgelagerte Auswerter berichtet pro Holdout, Familie und Modalitaet:

- Distanzen zu jedem Trainingsexemplar, zum Frozen-Prototyp, zum adaptiven
  Prototyp und zum naechsten Replay-Exemplar;
- Match, Fehlmatch, Mehrdeutigkeit, Enthaltung und Abwesenheit je Arm;
- familienrichtige Treffer und familienfremde Interferenzen;
- Support, Slot- und Uebergangsdigests der tatsaechlichen Memoryspur;
- Vor-/Nachzustandsdigests aller read-only Proben;
- eine Konfusionsmatrix getrennt fuer Audio und Video.

Aggregierte Trefferquoten duerfen nur zusammen mit den vollstaendigen
Einzelfaellen ausgegeben werden. Ein globaler AV-Treffer darf keine
abweichenden Modalitaetsbefunde verdecken.

## Entscheidung

Ein technisch vollstaendiger Lauf ist unabhaengig von seiner fachlichen
Trefferquote auswertbar. Zulaessige terminale Funktionsbefunde sind:

- `S2LS_ADAPTIVE_GENERALISATION_OBSERVED`, falls die adaptive Bank auf dem
  vorab versiegelten Holdoutkorpus einen belegten Nutzen gegenueber beiden
  Baselines zeigt;
- `S2LS_BASELINES_EQUIVALENT`, falls kein belastbarer Unterschied entsteht;
- `S2LS_ADAPTIVE_GENERALISATION_NOT_OBSERVED`, falls Frozen oder Replay
  gleich gut beziehungsweise besser sind oder die adaptive Bank relevante
  Holdouts nicht generalisiert;
- `S2LS_INTERFERENCE_OBSERVED`, falls familienfremde Treffer oder
  Prototypvermischung auftreten.

Mehrere fachliche Befunde duerfen gleichzeitig gelten. Es gibt keinen
vorgegebenen Gewinner und keinen nachtraeglichen Ausschluss unbequemer
Varianten. `NOT_EVALUABLE` ist ausschliesslich technischen Quellen-, Split-,
Zeit-, Digest-, Owner-, Read-only- oder Aufzeichnungsfehlern vorbehalten.

## Aussagegrenze

Ein positiver Befund wuerde begrenzte Generalisation aus einem vorab
eingefrorenen AV-Erfahrungskorpus zeigen. Er belegt weder Semantik,
Objektidentitaet, offene Welt, Langzeitpersistenz noch besondere
MCM-spezifische Physik. Ein negativer oder gemischter Befund bleibt ein
vollwertiges Ergebnis ueber die unveraenderte bestehende Memorymechanik.

S2-LS ist zunaechst nur dieser statische Vertrag. Korpusauswahl,
Materialisierung, Implementierung und Ausfuehrung benoetigen jeweils eine
separate ausdrueckliche Freigabe.
