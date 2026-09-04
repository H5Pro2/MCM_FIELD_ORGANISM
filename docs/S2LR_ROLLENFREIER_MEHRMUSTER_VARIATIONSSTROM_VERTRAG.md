# S2-LR - Rollenfreier Mehrmuster-Variationsstrom

## Status und Funktionsfrage

`S2LR_STATIC_FUNCTION_AND_FALSIFICATION_CONTRACT_COMPLETE`

S2-LR bindet genau einen begrenzten prospektiven Versuch fuer die Frage:

> Kann der qualifizierte rollenfreie 336-Werte-Wahrnehmungsstrom zwei
> interleaved erfahrene Familien nicht bitidentischer AV-Wahrnehmungen in
> getrennten stabilen Prototypen verdichten, je eine nie trainierte Variante
> generalisieren und sich bei schwacher Erfahrung, Grenzueberschreitung oder
> Mehrdeutigkeit kontrolliert enthalten?

S2-LR fuehrt keine neue Memory-, Kontext-, Feld- oder Lernmechanik ein. Ein
positiver Befund darf durch die vorhandenen L1-Regeln, adaptiven
Prototypbanken und vollstaendigen Slotscans erklaert werden. Er belegt weder
Semantik noch besondere MCM-spezifische Physik.

## Eingefrorene Grundlage

Grundlage ist der bestaetigte S2-LQ-Lauf
`s2lq-role-free-multipattern-20260904-02`:

- technischer Status `RECORDING_COMPLETE`;
- Funktionsstatus `S2LQ_MULTIPATTERN_STREAM_CONFIRMED`;
- Recorddigest
  `cfd47da364d80f93e0207c30de6504c05256bf1bd02f7cd556bdd2d912dc16b7`;
- Ergebnisdateidigest
  `b1f871135f9a9b1c7d37ac7407fb5731d62410b66ada5c86b918ba8ae59accc3`.

Unveraendert bleiben:

- 48 auditive und 288 visuelle Default-Live-Rezeptorwerte;
- B4-Kapazitaet 9 und TSPM-Fast-Kapazitaet 3;
- auditive Slow-Kapazitaet 8 und visuelle Slow-Kapazitaet 4;
- bestehende Fast- und Slow-Schwellen, Updatefaktoren, Stabilitaetsgrenzen,
  LRU- und Ablaufregeln;
- unabhaengige Geschwisterprojektionen an Feld und atomaren B4-/TSPM-Verbund;
- read-only Slotscans und getrennte Kontext-Hypothesen;
- keine Kontextwirkung auf beobachtete Rezeptorwerte, Feld oder Memory.

Die Schwellen werden nicht neu kalibriert. Die Variationsfamilien werden
prospektiv fuer die bestehenden mechanischen Grenzen konstruiert.

## Rollenfreie Quellen und Auswerterrollen

Alle funktionalen Werte muessen aus echten kanonischen RGB8-Frames und
PCM_F32LE-Fenstern durch die unveraenderten Rezeptoren entstehen. Es duerfen
keine 48er-, 288er- oder 336er-Vektoren hinter den Rezeptoren eingesetzt
werden.

Der Laufpfad kennt ausschliesslich neutrale Quellcodes, Ereigniscodes,
Zeitfenster und Digests. Die folgenden Rollen existieren nur im getrennt
versiegelten Auswertungsplan:

| Auswerterrolle | Zweck | Trainingsexpositionen |
|---|---|---:|
| Familie F, Ausgang `F_PLUS` | erster Familienzustand | 2 |
| Familie F, Variation `F_MINUS` | adaptive Verschiebung | 6 |
| Familie F, Holdout `F_H` | nie trainierte positive Variante | 0 |
| Familie G, Ausgang `G_PLUS` | erster Familienzustand | 2 |
| Familie G, Variation `G_MINUS` | adaptive Verschiebung | 6 |
| Familie G, Holdout `G_H` | nie trainierte positive Variante | 0 |
| schwache Spur W | kontrolliert instabil | 3 |
| Druck `D1...D9` | A-Verdraengung ohne Slow-Bildung | je 1 |

`F_H`, `G_H`, Grenz- und Interferenzfixtures duerfen weder Memoryformation
noch Baselinetraining erreichen. Die Laufwurzel enthaelt nur die direkt aus
okkludierten RGB- beziehungsweise maskierten PCM-Quellen erzeugten
Teilhinweise. Vollstaendige Holdoutwerte liegen ausschliesslich in einer
getrennt versiegelten Evaluationswurzel und werden erst nach Abschluss aller
Laufarme durch eine `EvaluationRunBinding` zugaenglich.

## Einmalige Rezeptormaterialisierung

Vor dem ersten Memoryaufruf werden alle Trainings-, Holdout-, Grenz-,
Interferenz- und Druckfixtures genau einmal durch die realen Rezeptoren
materialisiert. Danach werden unveraenderlich gebunden:

- RGB-/PCM-Payloaddigests, Geometrie, native Uhren und Zeitfenster;
- 48er-, 288er- und AV-Rezeptorwertedigests;
- vollstaendige und auf den Teilhinweispositionen beobachtete L1-Distanzen;
- alle prospektiven PPB-Uebergangswerte in exakter Binary64-Reihenfolge;
- die finalen adaptiven Prototypen beider Familien und Modalitaeten.

Das Materialisierungsgate muss fuer F und G jeweils nachweisen:

1. `PLUS` und `MINUS` aktualisieren in jeder Modalitaet ausschliesslich den
   vorgesehenen Familienprototyp.
2. Jeder Updateeingang liegt innerhalb der jeweils aktiven Fast- und
   Slow-Regel des vorherigen Zustands.
3. Der Holdout liegt ausserhalb der Slow-Schwelle jedes einzelnen
   Trainingsbeispiels und des eingefrorenen Erstprototyps.
4. Der Holdout liegt innerhalb der Slow-Schwelle des prospektiv aus der
   vollstaendigen Updatekette abgeleiteten finalen adaptiven Prototyps.
5. F- und G-Training, Zwischenprototypen und Holdouts bleiben in auditiver
   und visueller Slow-Bank gegenseitig getrennt.
6. Kein F-Ereignis aktualisiert einen G-Slot und kein G-Ereignis einen
   F-Slot.
7. W erzeugt eine eigene homogene Spur, erreicht aber nur Support 2.
8. D1 bis D9 sind nach der echten Fast-AND-Regel von F, G, W und
   untereinander getrennt und erzeugen keinen Slow-Aufruf.

Holdout-Generalisation muss fuer beide Familien in beiden Modalitaeten die
strenge Gegenprognose aus Punkt 3 und 4 erfuellen. Der Auswerter berichtet
Audio und Bild dennoch getrennt; ein Treffer in nur einer Modalitaet darf
nicht als globaler AV-Treffer umgedeutet werden.

Es gibt keine iterative Suche, Normalisierung, nachtraegliche
Schwellenanpassung oder Ersatzfixture. Scheitert eine Bindung, endet der
Versuch vor Memory als
`S2LR_VARIATION_GEOMETRY_NOT_MATERIALIZABLE`.

## Endliche Trainingsfolge

Die 28 vollstaendigen AV-Formationen werden im Laufpfad nur als `e01...e28`
mit neutralen Inhaltscodes gefuehrt. Die versiegelte Auswerterabbildung
lautet:

```text
F_PLUS G_PLUS W
F_PLUS G_PLUS W
F_MINUS G_MINUS W
F_MINUS G_MINUS
F_MINUS G_MINUS
F_MINUS G_MINUS
F_MINUS G_MINUS
F_MINUS G_MINUS
D1 D2 D3 D4 D5 D6 D7 D8 D9
```

Damit gelten exakt:

- acht interleaved Expositionen je starker Familie;
- drei Expositionen der schwachen Spur;
- neun einmalige Druckexpositionen;
- 28 Formationen insgesamt.

Jedes Ereignis besitzt einen eigenen Einmal-Owner. Der Strom bleibt nach
jedem verbrauchten Ereignisowner `OPEN`. Feld- und Memoryzweig erhalten
denselben validierten Rezeptorursprung, bleiben aber voneinander unabhaengig.
Nur der B4-/TSPM-Schritt ist atomar.

## Prospektive Memoryspur

Vor den Druckreizen muessen F und G in beiden Slow-Banken je genau einen
eigenen stabilen Slot besitzen. Ihre Ereignis-, Support-,
Prototypdigest- und Updateketten duerfen ausschliesslich die jeweils eigene
Familie enthalten.

W muss in beiden Slow-Banken einen eigenen Slot mit Support 2 besitzen und
oeffentlich instabil bleiben. Die neun Druckreize duerfen keinen Slow-Slot
erzeugen oder aktualisieren.

Nach e28 muessen gelten:

- B4 enthaelt ausschliesslich D1 bis D9 in realer Bildungsreihenfolge;
- Fast enthaelt ausschliesslich spaete Druckinhalte;
- F, G und W sind vollstaendig aus `A_RECENT` verschwunden;
- F und G bleiben getrennt in `B_STABLE_AUDITORY` und
  `B_STABLE_VISUAL` mit Support 3 erhalten;
- W bleibt intern mit Support 2 vorhanden, erzeugt aber keinen oeffentlichen
  stabilen Kontext;
- kein Druckinhalt ist verdichtet.

Eine gemischte F/G-Prototyplinie, ein falscher Support oder ein unerwarteter
Slow-Druckslot ist bei vollstaendig gueltiger Aufzeichnung eine fachliche
Falsifikation, kein Infrastrukturfehler.

## Zehn spaetere Teilhinweise

Nach e28 folgen unter strikt spaeteren nativen Quellenzeiten zehn reale
Teilhinweise ohne vorbereitende Vollprobe:

| Hinweis | Modalitaet | Auswertungszweck | Gebundene Entscheidung |
|---|---|---|---|
| q01 | visuell | Holdout F | eindeutiges `B_STABLE` F |
| q02 | auditiv | Holdout F | eindeutiges `B_STABLE` F |
| q03 | visuell | Holdout G | eindeutiges `B_STABLE` G |
| q04 | auditiv | Holdout G | eindeutiges `B_STABLE` G |
| q05 | visuell | schwache Spur W | Enthaltung |
| q06 | auditiv | schwache Spur W | Enthaltung |
| q07 | visuell | vorab gebundener innerer Grenzfall F | eindeutiges F |
| q08 | visuell | benachbarter aeusserer Grenzfall | kein anwendbarer Kontext |
| q09 | visuell | beobachtete Positionen passen zu F und G | Mehrdeutigkeit |
| q10 | auditiv | beobachtete Baender passen zu F und G | Mehrdeutigkeit |

q07 und q08 muessen vor Memory mit einer festen positiven Sicherheitsreserve
innerhalb beziehungsweise ausserhalb der bestehenden Grenze materialisiert
werden. Ein exakt auf der Floatgrenze liegender Fall ist unzulaessig.

q09 und q10 muessen technisch echte Interferenzfaelle sein: Die beobachteten
Positionen passen zu beiden stabilen Familienkandidaten, waehrend die
maskierten Ergaenzungen der Kandidaten verschieden sind. Das Ergebnis ist
Enthaltung; es gibt keine Rangfolge, Verschmelzung oder Fallbackregel.

Visuelle Hinweise entstehen aus real okkludierten RGB-Frames. Auditive
Hinweise entstehen aus realen PCM-Fenstern mit einem unabhaengig gebundenen
24/24-Bandplan. Eine Maske darf nie aus Nullwerten oder Zielwerten abgeleitet
werden.

## Scans, Hypothesen und Baselines

Jeder Teilhinweis fuehrt vollstaendig und ohne Short-Circuit aus:

- 9 B4-Slots;
- 3 Fast-Slots;
- 4 visuelle oder 8 auditive Slow-Slots;
- interne Aufloesung von B4/Fast zu hoechstens einem `A_RECENT`-Befund;
- oeffentliche Entscheidung nur zwischen `A_RECENT` und `B_STABLE`.

Nach e28 darf fuer F, G und W kein A-Kandidat vorhanden sein. Eine
zugelassene Hypothese nennt ausschliesslich den Memorybereich und die
maskierten Kandidatenwerte. Beobachtete Werte bleiben unveraendert und die
Hypothese wird weder zum Rezeptorzustand noch zum Feldkontakt.

Vier unabhaengige Vergleichsformen bleiben verbindlich:

1. `FROZEN_FIRST_PROTOTYPE` je Familie;
2. `REPLAY_NEAREST_EXEMPLAR` ueber alle Trainingsvarianten;
3. getrennte `ADAPTIVE_PROTOTYPE_BANK` je Familie;
4. bestehende direkte Slotscan-/Maskenbaseline fuer die aktuelle
   Memorybelegung.

Frozen und Replay muessen die streng gebundenen Holdouts abweisen. Die
adaptive Baseline darf sie annehmen und muss mit den tatsaechlichen
Slow-Prototypen uebereinstimmen. Der Produktionsscan und die direkte
Slotscan-Baseline muessen bei allen zehn Hinweisen dieselbe Entscheidung und
dieselben fachlichen Hypothesenwerte liefern. Keine Baseline darf
Auswerterrollen oder Zielwerte erhalten.

Alle Vergleichsarme erhalten im Lauf nur denselben Teilhinweis. Erst der
nachgelagerte Auswerter vergleicht ihre vorgeschlagenen maskierten Werte mit
dem vollstaendigen Holdoutziel. Eine moegliche Anwendbarkeit eines
Frozen- oder Replaykandidaten auf den beobachteten Teilpositionen darf nicht
als volle Holdout-Generalisation gelten; massgeblich bleiben die getrennten
vollstaendigen Distanzen und Rekonstruktionsfehler nach Oeffnung der
Evaluationswurzel.

## Messungen und Grenzen

Der nachgelagerte Auswerter berichtet mindestens:

- Rezeptordistanzen innerhalb und zwischen beiden Familien;
- Fast-Zuordnung jeder Formation;
- alle modalen Slow-Slots mit Support-, LRU-, Ereignis- und
  Prototypdigestketten;
- Holdoutabstand zu Erstprototyp, jedem Replaybeispiel und adaptivem
  Endprototyp;
- getrennte auditive und visuelle Treffer, Verwechslungen und
  Nichtanwendbarkeit;
- q07/q08-Sicherheitsreserven und q09/q10-Kandidatenmengen;
- identische Memory- und Feldzustandsdigests vor und nach jedem read-only
  Teilhinweis;
- vollstaendige Gleichheit von Produktionsscan und Direktbaseline.

Vor einer Implementierung sind die konkreten Fixtures, alle nativen
Zeitfenster und die exakten Byte- und Ledgergrenzen einmalig zu
materialisieren. Bereits fest gebunden sind:

| Position | Umfang |
|---|---:|
| vollstaendige AV-Formationen | 28 |
| visuelle Teilhinweise | 6 |
| auditive Teilhinweise | 4 |
| Gesamtereignisse | 38 |
| Feldkontakte | `28*336 + 6*288 + 4*48 = 11.328` |
| Memory-L1-Terme | `28*3.552 = 99.456` |
| Scanvergleiche, beide Arme | hoechstens `6*2*800 + 4*2*528 = 13.824` |

Rohpayloads werden einzeln gestreamt und nach Rezeptorreduktion verworfen.
Sie erscheinen weder in Memory, Hypothese, Ergebnisbeleg noch Baseline. Eine
kleine Erweiterung des bestehenden S2-LO/S2-LQ-Pfads, ein atomarer
Ergebnisbeleg und ein read-only Verifikator genuegen. Es entsteht keine neue
Recorder- oder Registryinfrastruktur.

## Entscheidung

`S2LR_ROLE_FREE_MULTIPATTERN_VARIATION_LEARNING_CONFIRMED` ist nur zulaessig,
wenn:

1. alle 28 Formationen und zehn Teilhinweise vollstaendig sind;
2. F und G getrennte, reine Slow-Prototyplinien mit Support 3 besitzen;
3. beide nie trainierten Holdouts nach A-Verdraengung eindeutig der richtigen
   Familie zugeordnet werden und die andere Familie nicht treffen;
4. Frozen und Replay die streng gebundenen Holdouts abweisen, waehrend
   adaptive Bank und realer Slow-Prototyp sie annehmen;
5. W mit Support 2 oeffentlich instabil bleibt und nach A-Verdraengung keine
   Kontextzulassung erhaelt;
6. der innere Grenzfall zugelassen, der aeussere Grenzfall abgewiesen und bei
   beiden Interferenzfaellen enthalten wird;
7. keine Familie, schwache Spur oder Druckfixture einen fremden Slow-Slot
   aktualisiert;
8. alle Scans read-only bleiben und die Direktbaseline exakt uebereinstimmt.

Ein vollstaendig aufgezeichneter Lauf mit anderer Funktion endet als
`S2LR_ROLE_FREE_MULTIPATTERN_VARIATION_LEARNING_FALSIFIED`. Insbesondere sind
Familienvermischung, falsche Holdoutzuordnung oder unkontrollierte Auswahl bei
Interferenz echte Funktionsbefunde.

`NOT_EVALUABLE` bleibt auf Quellen-, Materialisierungs-, Zeit-, Owner-,
Digest-, Ledger-, Read-only- oder Aufzeichnungsbruch beschraenkt. Es gibt
keinen Retry und keine nachtraegliche Fixture- oder Schwellenkorrektur im
selben Lauf.

## Aussagegrenze

Ein positiver Befund bestaetigt begrenztes rollenfreies Lernen zweier stabiler
Wahrnehmungsstrukturen aus variierenden, zeitlich vermischten AV-Erfahrungen.
Er bestaetigt keine gelernte Kategorie, Bedeutung, offene Welt,
Langzeitpersistenz, automatische Maskenerkennung oder autonome Handlung.

Vor einer realen Ausfuehrung ist genau eine kompakte Fixture- und
Geometriematerialisierung erforderlich. Erst deren Bestehen darf eine kleine
private Erweiterung des qualifizierten Strompfads und einen separat
freigegebenen Einmallauf ermoeglichen.
