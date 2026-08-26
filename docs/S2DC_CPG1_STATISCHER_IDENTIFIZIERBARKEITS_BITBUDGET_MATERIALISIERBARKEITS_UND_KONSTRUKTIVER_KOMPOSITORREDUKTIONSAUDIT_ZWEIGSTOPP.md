# S2-DC: CPG-1 Audit und konstruktiver Zweigstopp

## Auftrag und Grenze

S2-DC auditiert ausschliesslich statisch den S2-DB-Vertrag fuer CPG-1.
Geprueft wurden die vier Leave-one-combination-out-Geschichten, zwei
Relationswelten, die unterbestimmte Negativkontrolle, Budgetgleichheit,
Permutations-, Marginal-, Ablations- und Interferenzrollen sowie die
Reduzierbarkeit auf Standardkompositoren.

Es wurden keine Projektmodule importiert, keine Zustands-, Probe-, Baseline-
oder Runnerfunktion ausgefuehrt und keine Implementierung geaendert.

## Hold-out- und Relationsweltaudit

Die vier Hold-out-Splits sind strukturell eindeutig bezeichnet: `AX`, `AY`,
`BX` und `BY` werden jeweils einmal aus drei Bildungsbeobachtungen
zurueckgehalten. In jedem Split treten beide Einzelkomponenten des Hold-outs
in den verbleibenden Beobachtungen auf. Damit ist die Split-Anatomie
identifizierbar und frei von einem fehlenden Einzelkomponentenfaktor.

Die geforderten zwei Relationswelten sind dagegen noch nicht als konkrete
Fortsetzungstafeln gebunden. Der Vertrag fordert gleiche Komponenten und
Marginalhaeufigkeiten bei verschiedenen Tafeln, legt aber weder die Tafeln
noch eine Regelfamilie fest, die aus drei Zellen genau die vierte bestimmt.
Die Welten sind daher als Rollen getrennt, aber funktional noch nicht
eindeutig materialisierbar.

Die G8-Negativkontrolle ist gueltig. Aus nur `AX` und `BY` folgt keine
eindeutige Fortsetzung fuer `AY` oder `BX`. Der einzig methodisch zulaessige
Befund ist dort `NO_IDENTIFIABLE_COMPOSITION`.

## Identifizierbarkeitsdilemma

Fuer eine frei waehlbare Abbildung der vier Kombinationen auf `R0/R1`
bestimmen drei beobachtete Tabellenzellen den Wert der vierten Zelle nicht.
Es existieren mindestens zwei mit allen Bildungsdaten vereinbare Tafeln, die
sich nur am Hold-out unterscheiden. CPG-1 kann dann keine vorab gerichtete
Hold-out-Prognose liefern.

Wird stattdessen eine additive, lineare, bilineare oder tensorfaktorisierte
Regelfamilie so eingeschraenkt, dass drei Beobachtungen den Hold-out eindeutig
bestimmen, darf die kapazitaetsgleiche `Factorized-Rule-Baseline` exakt
dieselbe Regelfamilie, dieselben Komponenten und dieselben drei
Bildungsbeobachtungen verwenden. Sie berechnet dann dieselbe Fortsetzung.

Auf der endlichen `2 x 2`-Domaene kann zudem jede vollstaendige
Fortsetzungstafel als bilineare Abbildung auf One-hot-Komponenten oder als
Tensor mit vier Zellen dargestellt werden. Haelt CPG-1 genug
Relationsinformation fuer eine beliebige eindeutige vierte Zelle, kann die
faktorisierte Baseline diese Information isomorph und ohne zusaetzlichen
funktionalen Zustand halten.

Damit gilt die vollstaendige Fallunterscheidung:

1. Die Regelfamilie ist nicht ausreichend eingeschraenkt: Der Hold-out ist
   nicht identifizierbar.
2. Die Regelfamilie ist ausreichend eingeschraenkt: Ein gleich budgetierter
   Standardkompositor reproduziert die Prognose.

In keinem Fall verbleibt eine eigene CPG-1-Gegenprognose.

## Budget- und Materialisierbarkeitsaudit

Der Vertrag bindet identische Anzahlen von Komponenten, Bildungstupeln,
Expositionen, Proben und funktionalen Gesamtbits. Diese Fairnessregel ist
methodisch richtig. Eine bitgenaue Materialisierung ist dennoch nicht
moeglich, weil folgende Werte nicht festgelegt sind:

- Kodierung und Bitbreite der Komponenten- und Fortsetzungsvektoren;
- Praezision und Kapazitaet des Relationsregelzustands;
- Aufteilung desselben Gesamtbudgets auf direkte, lineare, bilineare und
  tensorfaktorisierte Baselines;
- konkrete Fortsetzungstafeln und die genau eine vorregistrierte
  Regelfamilie;
- exakte Comparatorgrenzen und Aggregationsreihenfolge.

Diese offenen Rollen wuerden jede Implementierung fail-closed blockieren.
Sie werden nicht nachgebunden, weil die konstruktive Reduktion den Kandidaten
bereits vorher schliesst.

## Prueffamilien

G4 und G5 benennen Permutations-, Marginal- und Reihenfolgekontrollen
korrekt. G6 trennt den Relationsregelzustand durch Ablation. G7 fordert eine
zweite Relationswelt und verbietet Weltlabels als Auswahlhilfe. Fuer eine
eindeutige Fixture fehlen jedoch die konkreten Permutationen, erwarteten
Fortsetzungen, genau eine Interferenzpolitik und die Comparatoraggregation.

Auch bei deren spaeterer Festlegung bleibt die Reduktion erhalten: Derselbe
Standardkompositor kann dieselbe Permutation, dieselben Marginalen, dieselbe
Regelablation und dieselbe begrenzte Interferenzpolitik mit identischen
Eingaben und funktionalen Bits ausfuehren.

## Gegenbaselineaudit

No-Memory, Replay, gemeinsame Prototypbank, BAM-1 und AVPC-1 kontrollieren
wichtige Abkuerzungen, sind aber nicht die entscheidende Grenze. Der feste
direkte Merkmalskompositor kann Komponenten zusammenfuehren, muss daraus
allein jedoch keine Fortsetzungsregel lernen.

Die `Factorized-Rule-Baseline` ist die staerkste und abschliessende
Gegenbaseline. Fuer jede Regelfamilie, die CPG-1 eine eindeutige
Hold-out-Fortsetzung ermoeglicht, kann sie denselben regeltragenden Zustand
und dieselbe Auswertung verwenden. Sie reproduziert damit G1 bis G8, die
Hold-out-Entscheidungen und alle Kontrollrollen ohne mehr Speicher-,
Eingabe-, Bildungs- oder Probebudget.

## Entscheidung

Die Gate-Frage ist negativ beantwortet. CPG-1 liefert bei einer
zurueckgehaltenen Kombination keine eigene vorab gerichtete Prognose, die
ein kapazitaetsgleicher Standardkompositor nicht reproduzieren kann.

`STOP_CPG1_NO_IDENTIFIABLE_NONREDUCIBLE_PROGNOSIS_AGAINST_FACTORIZED_COMPOSITOR`

CPG-1 ist als eigenstaendiger Forschungskandidat terminal geschlossen. Die
kompositionelle Verarbeitung kann weiterhin eine generische
Engineeringfunktion sein. Sie ist jedoch kein eigener MCM-Mechanismus und
kein Nachweis einer MCM-spezifischen Memory-Funktion.

## Naechste Grenze

Es gibt keinen automatisch freigegebenen CPG-1-Folgeschritt. Gleichung,
Implementierung, Tests, Runner und Feldintegration bleiben gesperrt. Eine
neue Forschungsrichtung benoetigt erneut eine ausdrueckliche fachliche
Entscheidung und eine Gegenprognose, die nicht auf eine kapazitaetsgleiche
Standardkomposition reduzierbar ist.
