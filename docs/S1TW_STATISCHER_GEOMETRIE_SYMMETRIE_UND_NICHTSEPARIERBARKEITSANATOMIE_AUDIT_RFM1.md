# S1-TW: Statischer Geometrie-, Symmetrie- und Nichtseparierbarkeitsanatomie-Audit RFM-1

## Auftrag und Grenze

S1-TW prueft, ob fuer die in S1-TV gebundene relationale Feldmotivwirkung eine
minimale strukturell nichtseparierbare Zustandsrolle existiert. Der Audit
bindet keine Dynamikgleichung, Rate, Parameter, Runtime, Implementierung,
Testausfuehrung oder Ergebnisentscheidung.

## Eingefrorene Geometrie

```text
node-a -- node-b -- node-c -- node-d

e_ab = {node-a,node-b}
e_bc = {node-b,node-c}
e_cd = {node-c,node-d}

M_left  = (e_ab,e_bc), Zentrum node-b
M_right = (e_bc,e_cd), Zentrum node-c
```

Herkunftsbeleg:

```text
reports/s1rk_four_node_fresh_manifest.json
  19cc753c110b64d1d48cabe46be190a01247995053da442dd4cefcd344ea8bfc
edge_inventory.digest
  9961eddd8c8a7ad845c9ab43af23f8ae5380c72ffae06c2e0af202cda49c3529
geometry_class
  FOUR_NODE_OPEN_LINE_S1PZ
```

Andere Knoten, Kanten, Diagonalen, Selbstkanten oder Zyklen sind ungueltig.

## Verwerfene triviale Anatomie

Folgende Darstellungen besitzen keine eigene relationale Struktur:

- ein einzelner Skalar je Knoten;
- ein einzelner Skalar je Kante;
- zwei unabhaengige Kantenrecords je Motiv;
- Summe, Differenz, Produkt oder feste Funktion aktueller Kantenmarginalen;
- ein frei fortgeschriebener Motivskalar ohne Projektionsidentitaet;
- ein Sequenz-, Phasen- oder Ereigniszaehler.

Ein frei fortgeschriebener Motivskalar waere strukturell nicht von einer
lokalen Retentions- oder Integratorbaseline getrennt. Er wird fuer RFM-1
nicht zugelassen.

## Kleinste verbleibende relationale Rolle

Jedes kanonische Motiv darf genau eine gemeinsame Zwei-Kanten-Tafel besitzen.
Die beiden Kanten erhalten dafuer je zwei rein technische signed
Teilnahmerollen relativ zu ihrer kanonischen Orientierung:

```text
positive Teilnahme
negative Teilnahme
```

Die gemeinsame Tafel besitzt damit genau vier geordnete Zellen:

```text
J_pp  linke Kante positiv, rechte Kante positiv
J_pn  linke Kante positiv, rechte Kante negativ
J_np  linke Kante negativ, rechte Kante positiv
J_nn  linke Kante negativ, rechte Kante negativ
```

Alle vier Zellen muessen endlich und nichtnegativ sein. Die Tafel speichert
keinen Rezeptorwert, kein Eingangsbild, kein Audiosignal, kein Ereignislabel
und keine historische Sequenz.

Diese vier Zellen sind zunaechst nur eine diskrete Anatomierolle. S1-TW legt
nicht fest, ob oder wie sie sich spaeter veraendern oder auf das Feld wirken.

## Abgeleitete Einzelkantenprojektionen

Aus jeder Tafel werden ausschliesslich als Summenprojektionen abgeleitet:

```text
linke Kante positiv = J_pp + J_pn
linke Kante negativ = J_np + J_nn
rechte Kante positiv = J_pp + J_np
rechte Kante negativ = J_pn + J_nn
```

Die vier Projektionen duerfen nicht zusaetzlich als unabhaengige
Kandidatenwerte gespeichert werden. Abweichende gespeicherte und abgeleitete
Marginalen waeren zwei widerspruechliche Zustandsquellen.

## Konstruktiver Nichtseparierbarkeitsbeleg

Zwei verschiedene nichtnegative Zwei-Kanten-Tafeln koennen dieselben
Zeilen- und Spaltensummen besitzen, waehrend ihre vier gemeinsamen Zellen
anders zugeordnet sind. Damit existiert strukturell mindestens ein
relationaler Freiheitsgrad, der nicht aus den Einzelkantenprojektionen
rekonstruiert werden kann.

Verbindlich ist daher:

```text
gleiche vier Einzelkantenprojektionen
+ unterschiedliche kanonische gemeinsame Tafel
= strukturell verschiedene relationale Motivlage
```

Das ist noch kein Wirkungsbeleg. Es zeigt nur, dass die S1-TV-Intervention
anatomisch formulierbar ist, ohne Knoten- oder Einzelkantenmarginalen zu
veraendern.

## Nullrelation

Eine relationale Nullrolle muss aus den Einzelkantenprojektionen eindeutig
und ohne Geschichte bestimmt sein. Sie enthaelt keine zusaetzliche
Kopplungsinformation. Eine spaetere konkrete Anatomie muss vor jeder Dynamik
genau eine Faktorisierungsregel fuer diese Nulltafel binden.

S1-TW waehlt noch keine numerische Faktorisierung. Nicht zulaessig sind:

- mehrere Nulltafeln fuer dieselben Marginalen;
- armweise ausgewaehlte Nulltafeln;
- eine Nulltafel mit verstecktem Carry;
- ein Reset, der eine nichtneutrale Tafel als Null bezeichnet.

## Ueberlappung am mittleren Rand

`M_left` und `M_right` teilen die Kante `e_bc`. Deshalb muessen die aus beiden
Tafeln abgeleiteten positiven und negativen Projektionen fuer `e_bc`
wertidentisch sein.

```text
rechte Projektion von M_left
=
linke Projektion von M_right
```

Die geteilte Projektion darf weder doppelt bilanziert noch durch
Nachnormierung angeglichen werden. Ein Zustand mit widerspruechlichen
`e_bc`-Projektionen ist ungueltig und wird nicht repariert.

S1-TW bindet noch keine globale Ressourcenbilanz. Die
Ueberlappungsidentitaet verhindert lediglich zwei widerspruechliche lokale
Darstellungen derselben Kante.

## Spiegelung und Orientierungsregeln

Unter der vorhandenen Linienspiegelung gilt:

```text
node-a <-> node-d
node-b <-> node-c
e_ab <-> e_cd
e_bc <-> e_bc
M_left <-> M_right
```

Beim Tausch der beiden Motivkanten wird die gemeinsame Tafel transponiert.
Bei Umkehr einer kanonischen Kantenorientierung werden die positiven und
negativen Rollen dieser Kante vertauscht. Die Kombination beider Operationen
muss eindeutig sein und zweimalige Anwendung muss exakt zum Ausgangszustand
zurueckkehren.

Knotennamen duerfen keine eigene Wirkung tragen. Zwei spiegelbezogene
gueltige Zustaende muessen dieselbe Anatomieklasse besitzen.

## Vollstaendiger anatomischer Recordbedarf

Ein spaeterer RFM-1-Anatomierecord muesste mindestens binden:

- unveraenderte Geometrie- und Kanteninventaridentitaet;
- Motivrolle `M_left` oder `M_right`;
- geordnetes linkes und rechtes Kantenpaar;
- kanonische Orientierungsidentitaeten;
- genau vier gemeinsame Tafeleintraege;
- vier daraus abgeleitete Einzelkantenprojektionen;
- gemeinsame `e_bc`-Ueberlappungsidentitaet;
- Nullrelationsreferenz;
- Spiegel- und Transpositionsbeleg;
- atomaren Eigendigest.

Der Record darf keine Feldantwort, Baselineausgabe, Armrolle oder spaetere
Ergebnisentscheidung enthalten.

## Ungueltige Zustaende

Fail-closed ungueltig sind:

- fehlende, zusaetzliche oder umgeordnete Motive;
- unbekannte, doppelte oder nicht angrenzende Kanten;
- negative oder nichtendliche Tafeleintraege;
- fehlende oder widerspruechliche Projektionen;
- unterschiedliche `e_bc`-Projektionen beider Motive;
- redundant gespeicherte unabhaengige Marginalen;
- mehrere Nulltafeln fuer dieselbe Projektionslage;
- verletzte Spiegel-, Transpositions- oder Doppelinversionsidentitaet;
- Knoten-, Arm-, Ereignis- oder Ergebnislabels im relationalen Zustand;
- Sequenzpuffer, Replayinhalt oder globaler versteckter Selector;
- stille Reparatur, Clipping oder Nachnormalisierung;
- eine Tafel, die deterministisch nur aus aktuellen Marginalen erzeugt wird
  und deshalb keine zwei matched relationale Lagen zulaesst.

## Abgrenzung gegen Pflichtbaselines

| Vergleich | Anatomischer Befund |
|---|---|
| unabhaengige Einzelkantenbank | besitzt nur die vier Projektionen, nicht ihre gemeinsame Zuordnung |
| statischer Zweikantenoperator | erzeugt fuer gleiche Marginalen immer dieselbe Ausgabe und kann kein matched Tafel-Paar tragen |
| einzelner Retentionsskalar | besitzt keine Projektionen, Ueberlappungs- oder Symmetrieidentitaet |
| multivariater Integrator | kann prinzipiell vier Tafeleintraege tragen und bleibt deshalb eine offene Reduktionsbaseline |
| DTS-1/T1 | bilanziert Einzelkantenrollen, nicht eine gemeinsame Tafel bei gleichen Kantenmarginalen |
| G2/D3 | bekannte Zustandsunterteilung ohne gemeinsame Zwei-Kanten-Projektionsidentitaet |

Die Anatomie grenzt RFM-1 strukturell von Einzelkantenbank und statischem
Operator ab. Sie grenzt RFM-1 noch nicht funktional von einem passend
dimensionierten multivariaten Integrator ab. Diese Reduktionsgefahr bleibt
ausdruecklich offen.

## Auditentscheidung

Eine minimale nichtseparierbare Anatomierolle bleibt uebrig: die gemeinsame
Vier-Zellen-Tafel zweier angrenzender Kanten bei festen
Einzelkantenprojektionen. Sie kann die S1-TV-matched Intervention strukturell
darstellen und respektiert die vorhandene offene Geometrie.

Damit ist RFM-1 nicht bereits auf eine Einzelkantenbank oder einen statischen
Zweikantenoperator reduziert. Eine Funktionszulassung folgt daraus nicht,
weil endogene Bildung, Feldrueckwirkung und die Abgrenzung zum multivariaten
Integrator noch fehlen.

## Aussagegrenze

S1-TW ist ein Anatomieaudit. Die gemeinsame Tafel ist eine bewusst definierte
technische Zustandsdarstellung und noch keine festgestellte Feldstruktur.
Weitergehende Funktions- oder Faehigkeitsaussagen folgen daraus nicht.

## Verbindliche Entscheidung

```text
S1_TW_RFM1_MINIMAL_JOINT_TWO_EDGE_TABLE_ANATOMY_REMAINS_NONSEPARABLE
EDGE_MARGINAL_AND_OVERLAP_IDENTITIES_BOUND
MULTIVARIATE_INTEGRATOR_REDUCTION_REMAINS_OPEN
NO_DYNAMICS_NO_PARAMETERS_NO_IMPLEMENTATION_NO_RUN
```

## Naechster Schritt

Der einzige naechste Schritt ist S1-TX als statischer Projektions-,
Ueberlappungs- und Integratorreduktionsaudit. Er muss vor jeder Dynamik
klaeren:

- welche exakte Nullfaktorisierung ohne freien Parameter zulaessig ist;
- wie die gemeinsame `e_bc`-Projektion ohne Doppelzaehlung gebunden wird;
- welche matched Tafelpaar-Intervention alle Marginalen erhaelt;
- welche zusaetzliche Gegenprognose RFM-1 von einem fairen multivariaten
  Integrator unterscheidet.

Falls keine solche Integrator-Gegenprognose formulierbar ist, wird RFM-1 als
Retentionsbaseline eingeordnet und gestoppt. S1-TX darf keine
Dynamikgleichung, Parameter, Runtime, Implementierung oder Testausfuehrung
enthalten.
