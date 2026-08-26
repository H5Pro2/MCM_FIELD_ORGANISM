# S1-RI: Statischer Auswahl- und exakter Wertableitungsvertrag fuer lokale B1/M4-Kantenwerttreue

## Status und Umfang

S1-RI waehlt die in S1-RH als einzige primaer geeignete Option verbliebene
lokale Kantenwerttreue fuer den gemeinsamen B1/M4-Ausgangsbestand der
Vier-Knoten-Offenlinie aus.

Der Vertrag bindet:

- die gespeicherten M4-Knotenkapazitaeten und Kantenressourcen;
- die daraus abgeleiteten lokalen und globalen M4-Ledgerwerte;
- die korrespondierenden festen B1-Kantenraten;
- die Trennung von primaerem Ausgangsbestand und nicht registrierten
  Vergleichsoptionen.

S1-RI berechnet keine Digests, implementiert keine Payloadfabrik oder
Geometrie, erzeugt keine Fixtures und fuehrt keinen Test oder Feldlauf aus.

Vertragsentscheidung:

```text
LOCAL_EDGE_VALUE_FIDELITY_SELECTED_FOR_PRIMARY_B1_M4_FOUR_NODE_PRESTATE
M4_NODE_CAPACITY_ONE_BOUND_AT_ALL_FOUR_NODES
M4_CONDUCTIVE_ZERO_POINT_TWO_BOUND_ON_ALL_THREE_EDGES
M4_REFRACTORY_ZERO_POINT_ONE_BOUND_ON_ALL_THREE_EDGES
M4_ENDPOINT_FREE_ZERO_POINT_EIGHT_FIVE_DERIVED
M4_INTERIOR_FREE_ZERO_POINT_SEVEN_DERIVED
B1_FIXED_RATE_ONE_POINT_ONE_BOUND_ON_ALL_THREE_EDGES
B1_AND_M4_SHARE_THE_SAME_CONDUCTIVE_SOURCE
ALTERNATIVE_INITIALIZATIONS_ADD_NO_S1RA_MODEL_OR_REPLICA_ROLE
NO_DIGEST_NO_IMPLEMENTATION_NO_EXECUTION
```

## Ausgewaehlte Invariante

Die primaere Geometrieerweiterungsregel lautet:

```text
Jede vorhandene lokale Feldkante derselben technischen Klasse behaelt den
bereits akzeptierten lokalen leitenden und refraktaeren Ausgangswert,
unabhaengig von der Gesamtzahl der Knoten und Kanten.
```

Die Regel ist auf die in S1-RF gebundene offene Vier-Knoten-Linie und den
gemeinsamen B1/M4-Ausgangsbestand begrenzt. Sie ist keine allgemeine
Naturbehauptung fuer beliebige Graphen oder Feldgeometrien.

Die Auswahl folgt aus S1-RH, weil sie gemeinsam:

- die lokale Feldkopplung nicht mit der Knotenzahl normiert;
- die historischen Rand- und Innenledgerrollen erhaelt;
- B1 und M4 auf derselben leitenden Quelle haelt;
- B/C- und A/D-Spiegelung erhaelt;
- lokale und globale Erhaltung schliesst;
- keine neue globale Verteilungsregel einfuehrt.

## Physischer Bestand

Der zugrunde liegende kanonische Kantenbestand bleibt:

```text
E1 = node-a--node-b
E2 = node-b--node-c
E3 = node-c--node-d
```

Die Knotenordnung bleibt `node-a`, `node-b`, `node-c`, `node-d`. Es gibt
keine Zusatzkante, Periodizitaet oder private Rolleninformation im
physischen Bestand.

## M4 gespeicherte Knotenkapazitaeten

Die vier gespeicherten Kapazitaetszeilen lauten:

| Knoten | Kapazitaet |
|---|---:|
| `node-a` | `1.0` |
| `node-b` | `1.0` |
| `node-c` | `1.0` |
| `node-d` | `1.0` |

Damit gilt:

```text
global_capacity = 4.0
```

Die Kapazitaeten stammen aus der unveraenderten rollenfesten DTS-1-
Konfiguration. Sie werden nicht aus der neuen Geometrie nachjustiert.

## M4 gespeicherte Kantenressourcen

Die drei gespeicherten Kantenzeilen lauten exakt:

| erste Knoten-ID | zweite Knoten-ID | `conductive_bound` | `refractory` |
|---|---|---:|---:|
| `node-a` | `node-b` | `0.2` | `0.1` |
| `node-b` | `node-c` | `0.2` | `0.1` |
| `node-c` | `node-d` | `0.2` | `0.1` |

Die beiden Werte werden pro ungerichteter Kante genau einmal gespeichert.
Freie Ressource wird nicht gespeichert.

Die Kantenliste ist unter der S1-RF-Spiegelung invariant. Die aeusseren
Kanten werden ineinander abgebildet; die mittlere Kante bildet sich auf sich
selbst ab.

## M4 lokale Ledgerableitung

Jeder Knoten erhaelt die Haelfte der gespeicherten Werte jeder inzidenten
Kante. Daraus folgen die lokalen Ledger:

| Knoten | Kapazitaet | leitende Halbanteile | refraktaere Halbanteile | frei | Summe |
|---|---:|---:|---:|---:|---:|
| `node-a` | `1.0` | `0.1` | `0.05` | `0.85` | `1.0` |
| `node-b` | `1.0` | `0.2` | `0.1` | `0.70` | `1.0` |
| `node-c` | `1.0` | `0.2` | `0.1` | `0.70` | `1.0` |
| `node-d` | `1.0` | `0.1` | `0.05` | `0.85` | `1.0` |

Die mathematische Ableitung lautet fuer Randknoten:

```text
free = 1.0 - 0.5 * 0.2 - 0.5 * 0.1 = 0.85
```

Und fuer Innenknoten:

```text
free = 1.0 - 2 * 0.5 * 0.2 - 2 * 0.5 * 0.1 = 0.70
```

Die Werte `0.85` und `0.70` sind abgeleitete Prueferwartungen. Sie duerfen
nicht als zusaetzliche gespeicherte M4-Ressourcen in den Payload kopiert
werden.

## M4 globale Erhaltungsableitung

Die globale Bilanz zaehlt jede ungerichtete Kante genau einmal:

```text
free_total        = 0.85 + 0.70 + 0.70 + 0.85 = 3.10
conductive_total  = 0.2 + 0.2 + 0.2          = 0.60
refractory_total  = 0.1 + 0.1 + 0.1          = 0.30
accounted_total   = 3.10 + 0.60 + 0.30        = 4.00
global_capacity   = 4.00
global_residual   = 0.00
```

Die lokale Halbanteilsdarstellung und die globale Einfachzaehlung sind zwei
Ansichten derselben gespeicherten Kantenressourcen. Es entsteht keine
zusaetzliche Ressource.

## M4 unveraenderte Dynamikkonfiguration

Die Auswahl veraendert die bestehenden M4-Dynamikraten nicht:

```text
binding_rate  = 0.4
turnover_rate = 0.3
recovery_rate = 0.2
```

Der Kandidatensidecar bleibt im Pflichtbaselinepaket null. T1 bleibt eine
getrennte eingefrorene Ein-Kanten-Gegenbaseline und wird nicht auf drei
dynamische Kanten kopiert.

## B1 feste Drei-Kanten-Projektion

B1 uebernimmt nur den leitenden Teil desselben ausgewaehlten
M4-Ausgangsbestands. Refraktaere und freie M4-Rollen gelangen nicht in den
B1-Payload.

Der feste B1-Payload muss spaeter folgende drei Kantenzeilen enthalten:

| erste Knoten-ID | zweite Knoten-ID | `rate_per_second` |
|---|---|---:|
| `node-a` | `node-b` | `1.1` |
| `node-b` | `node-c` | `1.1` |
| `node-c` | `node-d` | `1.1` |

Jede Rate folgt ohne weitere Wahl aus:

```text
base_rate = 1.0
capacity = 1.0
fixed_conductive = 0.2
occupancy = 0.5 * 0.2 / 1.0 = 0.1
rate = 1.0 * (1.0 + 0.1) = 1.1
```

Der Backreactionstatus bleibt aktiviert. Der B1-Konfigurationsdigest bleibt
rollenfest unveraendert. Nur der spaetere Geometrie- und Kanteninventardigest
muss die neue Vier-Knoten-Geometrie abbilden.

## B1/M4-Quellenidentitaet

Die spaetere Registrierung muss belegen:

```text
B1.fixed_conductive(E1) = M4.initial_conductive_bound(E1) = 0.2
B1.fixed_conductive(E2) = M4.initial_conductive_bound(E2) = 0.2
B1.fixed_conductive(E3) = M4.initial_conductive_bound(E3) = 0.2
```

B1 darf die Werte nicht aus seinen bereits berechneten Raten
rueckkonstruieren. Beide Rollen muessen auf denselben statischen
Kantenquellbeleg verweisen.

## B3-B6-Konsistenz

Die in S1-RG eindeutig abgeleiteten B3-B6-Frischmassen bleiben:

```text
M(node-a) = M(node-b) = M(node-c) = M(node-d) = 0.25
```

Sie gehoeren zu den F3-basierten Baselines und sind nicht mit den
DTS-1-Kantenressourcen von M4 zu vermischen. Gleichheit einzelner Zahlen
begruendet keine gemeinsame Zustandsrolle.

## Nicht ausgewaehlte Alternativen

### Uniforme globale Budgetteilung

Die in S1-RH untersuchte globale Teilung wird nicht als primaerer
Ausgangsbestand registriert. Sie ist eine moegliche spaetere
Normalisierungsbaseline, aber keine der 14 S1-RA-Modellrollen und keine der
16 Expositionsrepliken.

### Nullinitialisierung

Die Nullinitialisierung bleibt eine moegliche spaetere Negativkontrolle. Sie
ist weder M4-Frischzustand noch B1-Fixed-Adapter-Payload der Pflichtmatrix.

Keine der beiden Alternativen erweitert die 224 Pflichtzellen. Eine spaetere
Ausfuehrung als Zusatzkontrolle benoetigt einen eigenen Vertrag und ein
eigenes Resultat ausserhalb des atomaren Pflichtpakets.

## Auswahlgrenze

Die Auswahl gilt nur fuer:

```text
FOUR_NODE_OPEN_LINE_S1PZ
PRIMARY_M4_FRESH_ANATOMY
PRIMARY_B1_FIXED_ADAPTER_PRESTATE
```

Sie gilt nicht automatisch fuer Ringe, Gitter, Verzweigungen, hoehere
Dimensionen oder andere Knotengrade. Jede solche Geometrie benoetigt einen
eigenen Lokalitaets- und Kapazitaetsaudit.

MINI_DIO bleibt eine historische Methodikquelle. Seine Gewichte,
Rangobserver, serielle Aktualisierung und Rewardpfade sind keine Quelle der
hier ausgewaehlten Werte.

## Paketstatus

Mit S1-RI sind die fuer B1 und M4 offenen primaeren Zahlenwerte geschlossen:

```text
PRIMARY_B1_VALUES_BOUND
PRIMARY_M4_VALUES_BOUND
LOCAL_AND_GLOBAL_LEDGER_EXPECTATIONS_BOUND
B3_B6_FRESH_MASSES_ALREADY_BOUND
CANONICAL_DIGEST_PREIMAGES_NOT_YET_BOUND
GEOMETRY_NOT_REGISTERED
PAYLOAD_FACTORIES_NOT_IMPLEMENTED
MANDATORY_BASELINE_PACKAGE_NOT_EXECUTABLE
```

Der Vertrag ist kein dynamischer Befund und keine Aussage zu einer
hypothetischen MCM-Memory.

## Fail-Closed-Regeln

S1-RI wird verletzt, wenn spaeter:

- eine der drei primaeren M4-Kanten andere Ausgangswerte erhaelt;
- B1 und M4 verschiedene leitende Quellen verwenden;
- B1 refraktaere oder freie M4-Rollen speichert;
- freie M4-Ressource als vierte gespeicherte Rolle erscheint;
- lokale Halbanteile global erneut als Kantenressource addiert werden;
- die mittlere Kante wegen ihrer Lage nachtraeglich anders gewichtet wird;
- M4-Dynamikraten oder B1-Konfiguration retuned werden;
- globale Teilung oder Nullinitialisierung eine Pflichtmatrixrolle erhaelt;
- die Auswahl auf andere Geometrieklassen verallgemeinert wird;
- Digests aus abweichenden Feld- oder Privatpayloads gebildet werden;
- vor einem kanonischen Payloadvertrag implementiert oder ausgefuehrt wird.

## Genau ein naechster Schritt

Als einziger Anschluss ist zulaessig:

```text
S1-RJ - statischer kanonischer Payload- und Digestpraeimagevertrag fuer die
        Vier-Knoten-Geometrie, Rollenabbildung und alle Frischzustaende
```

S1-RJ soll die exakten kanonischen Felder und Ordnungen fuer physischen
Geometriedigest, aeusseren Rollenmappingdigest, oeffentlichen Frischdigest
und 14 private Frischdigests beziehungsweise Leermarkierungen binden. Er
darf noch keine Digests berechnen, keine Geometrie registrieren, nichts
implementieren und nichts ausfuehren.
