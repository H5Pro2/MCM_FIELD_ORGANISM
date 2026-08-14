# S1-BM: E1 minimale Ressourcenanatomie und Erhaltungsidentitaet

## Status

Statischer Zustands- und Bilanzvertrag fuer E1. Keine Dynamikgleichung, keine
Runtime, kein Snapshot-Schema, kein Testlauf und kein Memory-, Lern- oder
KI-Befund.

## Verwendete Feldanatomie

E1 verwendet ausschliesslich das vorhandene ungerichtete lokale
MCM-Kanteninventar:

```text
V = vorhandene Feldneuronen
E = mcm_substrate_edge_inventory(layer)
```

`mcm_substrate_edge_inventory` liefert jede bestehende symmetrische lokale
Feldkante genau einmal, lehnt Selbstkanten ab und bindet das Inventar an die
aktuelle Feldgeometrie. E1 erzeugt, loescht oder sortiert keine Kante nach
Inhalt.

## Minimale gespeicherte Rollen

### Feste Knotenkapazitaet

Jeder Knoten `i` besitzt eine unveraenderliche positive Kapazitaet `q_i`.
Sie ist technische Anatomie und kein dynamischer Zustand.

```text
q_i > 0
```

Fuer den ersten Kandidaten gilt eine uniforme Initialanatomie:

```text
q_i = q_0 fuer alle i
```

### Dynamische Kantenbindung

Jede vorhandene ungerichtete Kante `e = {i,j}` traegt genau einen
nichtnegativen gebundenen Anteil `b_e`:

```text
b_e >= 0
```

`b_e` ist der einzige neue dynamische Freiheitsgrad von E1.

## Abgeleitete freie Ressource

Die freie Ressource eines Knotens wird nicht separat gespeichert. Sie ist der
Bilanzrest aus Knotenkapazitaet und der Haelfte jeder inzidenten
Kantenbindung:

```text
f_i = q_i - 0.5 * Summe(b_e fuer alle an i inzidenten Kanten e)
```

Zulaessige Zustaende erfuellen fuer jeden Knoten:

```text
f_i >= 0
```

Damit kann eine Kante nur Ressource binden, die an beiden Endpunkten lokal
verfuegbar ist. Eine globale Nachnormierung ist weder erforderlich noch
zulaessig.

## Lokale Erhaltungsidentitaet

Fuer jeden Knoten bleibt sein Ressourcenanteil exakt:

```text
q_i = f_i + 0.5 * Summe(b_e fuer e inzident an i)
```

Summiert ueber alle Knoten folgt automatisch die globale Identitaet:

```text
Q = Summe(q_i)
  = Summe(f_i) + Summe(b_e)
```

Jede ungerichtete Kante erscheint in zwei lokalen Knotensummen mit Faktor
`0.5` und deshalb global genau einmal.

Diese knotenweise Identitaet ist staerker als eine nur globale Bilanz. Sie
verhindert unsichtbaren Ferntransport und macht Konkurrenz ausschliesslich
zwischen Kanten moeglich, die einen Feldort teilen.

## Zulaessiger elementarer Transfer

Eine spaetere lokale Dynamik darf eine Kantenbindung nur durch einen
bilanzierten Transfer `delta_e` veraendern:

```text
b_e' = b_e + delta_e
f_i' = f_i - 0.5 * delta_e
f_j' = f_j - 0.5 * delta_e
```

Fuer Freigabe ist `delta_e < 0`, fuer Bindung `delta_e > 0`. Nach dem
Transfer muessen `b_e'`, `f_i'` und `f_j'` nichtnegativ bleiben.

Das ist eine Bilanzidentitaet, noch keine Vorschrift dafuer, wann oder wie
gross `delta_e` wird.

## Initialzustand und Nullarm

Der kanonische E1-Initialzustand lautet:

```text
b_e = 0 fuer alle e
f_i = q_i fuer alle i
```

Der E1-Nullarm erzeugt keinen E1-Zustand und verwendet unveraendert die
heutige neutrale S/H-Runtime. Ein angelegter, aber uniformer E1-Zustand ist
nicht mit diesem Nullarm gleichzusetzen und muss spaeter separat kontrolliert
werden.

## Zustandsidentitaet

Ein spaeterer technischer E1-Zustand benoetigt mindestens:

```text
contract_id
neuron_ids und feste q_i
ungerichtete edge_ids und b_e
edge_inventory_digest
```

Freie Ressourcenwerte werden aus dieser Darstellung berechnet. Sie duerfen
nicht redundant serialisiert werden, weil sonst zwei widersprechende
Wahrheiten fuer dieselbe Bilanz entstehen koennten.

## Abgrenzung zu F3

F3 speichert eine erhaltene Masse pro Knoten und transportiert sie auf dem
festen Feldgraphen. E1 speichert dagegen Bindung pro vorhandener Kante bei
fester knotenweiser Kapazitaet.

```text
F3: dynamische Knotenmasse, feste Kopplungsform
E1: feste Knotenkapazitaet, dynamische Kantenbindung
```

Diese strukturelle Differenz ist eine technische Gegenprognose, kein Nachweis
einer neuen Naturklasse.

## Noch nicht festgelegt

- Ursache und Betrag von `delta_e`;
- Freigaberate im Nullkontakt;
- genaue Rueckwirkung von `b_e` auf den Feldgenerator;
- kontinuierliche oder diskrete Integrationsform;
- Parameterskala und Zeiteinheit;
- opt-in Zustandscontainer und moegliches spaeteres Snapshot-Schema.

## Aussagegrenze

Die Bilanz konstruiert nur einen endlichen lokalen Zustandsraum. Sie beweist
weder Praegung noch Vergessen, Wiederverwendung, Rekonstruktion oder
MCM-Memory.

## Bester naechster Schritt

S1-BN hat genau eine kontinuierliche lokale Transferursache fuer `delta_e`
und die dazu konjugierte Rueckwirkung auf denselben Feldtransfer bestimmt.
Vorzeichen, Symmetrie, Nullkontakt und Gegenprognose gegen festen Gain sind
damit statisch gebunden. Als naechstes bindet S1-BO die
dimensionskonsistente Minimalgleichung und eine bereichserhaltende
Integrationsstrategie.
