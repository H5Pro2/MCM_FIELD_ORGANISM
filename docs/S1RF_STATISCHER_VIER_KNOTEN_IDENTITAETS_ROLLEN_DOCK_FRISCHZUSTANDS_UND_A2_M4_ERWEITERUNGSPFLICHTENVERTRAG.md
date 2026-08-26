# S1-RF: Statischer Vier-Knoten-Identitaets-, Rollen-, Dock-, Frischzustands- und A2/M4-Erweiterungspflichtenvertrag

## Status und Umfang

S1-RF bindet die in S1-RE ausgewaehlte offene Vier-Knoten-Linie als
kanonische technische Identitaetsform. Der Vertrag trennt strikt:

- die modellneutrale physische Feldgeometrie;
- die aeussere A/B/C/D-Rollenabbildung des Versuchs;
- die gemeinsame oeffentliche Frischprojektion;
- die rollenprivaten Frischzustandsformen.

S1-RF bindet keine Gleichung, keinen Zahlenparameter, keine Kontakthoehe,
keine Dauer, keine Rate und keine konkrete private Ressourcenmenge. Es wird
nichts implementiert, materialisiert, getestet oder ausgefuehrt.

Vertragsentscheidung:

```text
FOUR_NODE_OPEN_LINE_IDENTITIES_AND_CANONICAL_ORDER_BOUND
PHYSICAL_GEOMETRY_DIGEST_SEPARATED_FROM_OUTER_EXPOSURE_ROLE_DIGEST
FOUR_ONE_TO_ONE_TECHNICAL_CONTROL_CARRIERS_BOUND
B_C_AND_A_D_REFLECTION_ORBITS_BOUND
COMMON_PUBLIC_FRESH_PROJECTION_SHAPE_BOUND_FOR_ALL_FOURTEEN_ROLES
A2_B1_B6_FOUR_NODE_PRIVATE_SHAPES_BOUND_WITH_VALUES_UNBOUND
M4_FOUR_NODE_THREE_EDGE_ANATOMY_SHAPE_BOUND_WITH_VALUES_UNBOUND
UNKNOWN_NODE_COUNT_MUST_FAIL_CLOSED
NO_EQUATION_NO_PARAMETER_NO_IMPLEMENTATION_NO_EXECUTION
```

## Kanonische physische Identitaet

Folgende Identitaeten sind fuer die spaetere Registrierung reserviert:

| Rolle | Gebundene Identitaet |
|---|---|
| Geometrieklasse | `FOUR_NODE_OPEN_LINE_S1PZ` |
| Feld | `mcm.s1rf.field.4n` |
| Layer | `mcm.s1rf.layer.4n` |
| Geometrie | `mcm.s1rf.geometry.4n` |
| technische Modalitaet | `technical-control` |
| Dock | `dock.s1rf.technical-control.4n` |
| Rezeptorgeometrie | `mcm.s1rf.receptor.4n` |

Die technische Modalitaet bezeichnet nur den kontrollierten
Rezeptoreingang dieser Forschungsfixture. Sie behauptet keine auditive,
visuelle oder biologische Sinnesfunktion und erweitert keine
Wahrnehmungsmodalitaet des produktiven Feldes.

## Knoten- und Kantenordnung

Die physische Knotenordnung ist:

| Position | Knotenidentitaet |
|---:|---|
| 0 | `node-a` |
| 1 | `node-b` |
| 2 | `node-c` |
| 3 | `node-d` |

Die eindimensionale offene Linie verwendet die vorhandenen symmetrischen
Sampleoffsets `(-1)` und `(+1)` und keine periodische Achse.

Der kanonische ungerichtete Kantenbestand lautet:

```text
node-a--node-b
node-b--node-c
node-c--node-d
```

Jede Kante muss kanonisch mit lexikografisch geordneten Endpunkten genau
einmal im Inventar erscheinen. Selbstkanten, die Kante `node-a--node-d` und
jede weitere Zusatzkante sind ungueltig.

## Aeussere Expositionsrollen

Die Rollenabbildung wird getrennt von der physischen Geometrie gebunden:

| Aeussere Rolle | Physischer Knoten |
|---|---|
| `B_LOCAL` | `node-a` |
| `A_FOCAL` | `node-b` |
| `D_CONTROL` | `node-c` |
| `C_REMOTE` | `node-d` |

Damit gilt physisch:

```text
node-a -- node-b -- node-c -- node-d
B_LOCAL   A_FOCAL   D_CONTROL  C_REMOTE
```

`D_CONTROL` ist keine vierte S1-PZ-Expositionsfamilie und keine
Modellrolle. Es ist die aeussere Kontrollgegenlage zu A. Seine spaetere
Eingabebelegung muss im oeffentlichen Expositionsplan stehen.

Kein Modellaufruf darf die vier Rollennamen, ihre Ereignisbedeutung oder
einen Rollenmappingdigest erhalten.

## Spiegelungsinvariante

Die kanonische Linienspiegelung lautet:

```text
node-a <-> node-d
node-b <-> node-c
```

Sie erzeugt zwei Knotenorbits:

- Randorbit: `node-a`, `node-d`;
- Innenorbit: `node-b`, `node-c`.

Und zwei Kantenorbits:

- aeusserer Kantenorbit: `node-a--node-b`, `node-c--node-d`;
- mittlere Fixkante: `node-b--node-c`.

Vor jeder Exposition muessen oeffentliche Frischwerte und rollenprivate
Frischwerte diese Orbitgleichheit respektieren. Nach Beginn einer
rollenverschiedenen Exposition duerfen die dynamischen Werte auseinander
laufen.

Die Invariante fordert keine Ergebnisgleichheit und keine nachtraegliche
Symmetrisierung.

## Dock- und Carriervertrag

Das eine technische Dock besitzt genau vier Ein-zu-eins-Zuordnungen:

```text
carrier-a -> node-a
carrier-b -> node-b
carrier-c -> node-c
carrier-d -> node-d
```

Die kanonische Carrierordnung lautet `carrier-a`, `carrier-b`, `carrier-c`,
`carrier-d`. Ein Frame ist nur geometrisch gueltig, wenn er genau diese vier
Carrier in dieser Ordnung und die gebundene Rezeptorgeometrie verwendet.

Der Nullkontaktframe muss spaeter vier positive Nullwerte tragen. Werte fuer
`HISTORY_A`, `HISTORY_B_LOCAL`, `HISTORY_C_REMOTE`, D, Proben und Zeiten
werden in S1-RF nicht festgelegt.

## Getrennte Digestrollen

Spaetere Registrierung muss mindestens vier getrennte Digestrollen bilden:

1. `physical_geometry_digest` ueber Feld-, Layer-, Geometrie-, Modalitaets-,
   Knoten-, Positions-, Offset-, Kanten-, Dock- und Carrieridentitaeten;
2. `outer_exposure_role_mapping_digest` ueber die A/B/C/D-Zuordnung und die
   Spiegelungsorbits;
3. `public_fresh_projection_digest` ueber den vollstaendigen oeffentlichen
   Vier-Knoten-Frischzustand;
4. je Modellrolle einen `private_fresh_state_digest` oder eine kanonische
   Zustandslosmarkierung.

Der Modellkern darf nur den physischen Geometriedigest erhalten. Der
Rollenmappingdigest bleibt im aeusseren Orchestrator. Der oeffentliche
Frischdigest darf keinen rollenprivaten Payload enthalten.

S1-RF berechnet noch keinen dieser Digests.

## Gemeinsame oeffentliche Frischprojektion

Alle 224 spaeteren Lebenszykluszellen muessen dieselbe oeffentliche
Frischform besitzen:

- genau die vier gebundenen Knoten in kanonischer Ordnung;
- dieselbe offene Liniengeometrie und dasselbe Dock;
- S und H an jedem Knoten als bitgenaue positive Null;
- Rezeptorkontakt an jedem Knoten als positive Null;
- Feld- und Perzeptionstakt auf dem gemeinsamen initialen Feldtakt;
- keine lokalen Samples;
- keine letzte Rezeptorverteilung;
- keine Modell-, Replik-, Ereignis- oder Ergebnisrolle im Feldpayload.

Die private Zustandsform darf sich zwischen Modellrollen unterscheiden,
aber nicht zwischen den 16 Frischrepliken derselben Modellrolle.

## Vierzehn private Frischformen

| Modellrolle | Gebundene private Vier-Knoten-Form |
|---|---|
| `A0_CURRENT_CONTACT` | kanonische Zustandslosmarkierung |
| `A1_FAST_SH` | kanonische Zustandslosmarkierung; S/H liegt nur im Feld |
| `A2_B1_FIXED_ADAPTER` | externer Fixed-Adapter-Payload fuer exakt drei Kanten plus unveraenderter B1-Konfigurationsdigest |
| `A2_B2_INTEGRATOR` | vier geordnete L-Eintraege plus unveraenderter B2-Konfigurationsdigest |
| `A2_B3_LOCAL_LEAKY` | eingebetteter Vier-Knoten-M-Zustand plus unveraenderter B3-Konfigurationsdigest |
| `A2_B4_LINEAR_COUPLED` | eingebetteter Vier-Knoten-M-Zustand plus unveraenderter B4-Konfigurationsdigest |
| `A2_B5_F3_FULL` | eingebetteter Vier-Knoten-M-Zustand plus unveraenderter B5-Konfigurationsdigest |
| `A2_B6_CONST_V` | eingebetteter Vier-Knoten-M-Zustand, unveraenderter CONST-V-Spezifikationsdigest und B6-Konfigurationsdigest |
| `A3_NORM` | vollstaendiger geordneter Vier-Knoten-NORM-Zustand |
| `M1_PARALLEL_LEAK` | zwei getrennte vollstaendige Vier-Knoten-Spuren |
| `M2_DELAY` | eigener leerer Frischpuffer; spaetere Records muessen Vier-Knoten-Breite und Geometriedigest tragen |
| `M2_REPLAY` | eigener leerer Frischpuffer; keine Teilung mit M2-DELAY |
| `M4_DTS1_T1` | externe Vier-Knoten-/Drei-Kanten-DTS-1-Anatomie; Kandidatensidecar bleibt null |
| `M5_DIRECT` | vollstaendiger geordneter Vier-Knoten-Retentionszustand |

Die Tabelle bindet Form, Identitaet und Vollstaendigkeit, nicht die
Funktionsqualitaet einer Baseline.

## A2-B1-Erweiterungspflicht

Der Vier-Knoten-B1-Payload muss spaeter exakt enthalten:

- unveraenderte B1-Schemaidentitaet;
- aktivierten festen Backreactionstatus gemaess bestehender B1-Rolle;
- unveraenderten B1-Basiskonfigurationsbezug;
- den neuen Drei-Kanten-Inventardigest;
- genau eine Ratenzeile fuer jede der drei kanonischen Linienkanten;
- den unveraenderten B1-Konfigurationsdigest.

Die drei Ratenwerte bleiben ungebunden. Sie duerfen nur aus einer bereits
akzeptierten B1-Quelle eindeutig abgeleitet werden. Der heutige Codepfad
`zwei Knoten, sonst drei Knoten` muss spaeter durch eine explizite
Geometrieauswahl ersetzt werden. Eine unbekannte Knotenzahl muss fehlschlagen.

## A2-B2-Erweiterungspflicht

Der private L-Payload muss genau einen Eintrag fuer `node-a` bis `node-d` in
kanonischer Reihenfolge enthalten. Der Frischwert ist fuer alle vier
Eintraege positive Null. Der B2-Konfigurationsdigest bleibt unveraendert.

Fehlende, doppelte, zusaetzliche oder anders geordnete Eintraege sind
ungueltig. Ein historischer Drei-Knoten-Payload darf nicht aufgefuellt
werden.

## A2-B3-B6-Erweiterungspflicht

Jeder eingebettete M-Frischzustand muss enthalten:

- die vier gebundenen Knoten in kanonischer Ordnung;
- den Drei-Kanten-Inventardigest;
- genau eine endliche nichtnegative Masse pro Knoten;
- die unveraenderte rollenfeste Arm- und Konfigurationsidentitaet;
- bei B6 zusaetzlich den unveraenderten CONST-V-Spezifikationsdigest.

Die Massenwerte bleiben ungebunden. Sie muessen vor Ausfuehrung die
Spiegelungsinvariante erfuellen:

```text
M(node-a) = M(node-d)
M(node-b) = M(node-c)
```

S1-RF erlaubt keine Aenderung der bestehenden B3-B6-Gleichungen,
Konfigurationen oder Refinementrollen.

## M4-Anatomiepflicht

Die private M4-Frischanatomie muss exakt enthalten:

- vier positive Knotenkapazitaetsrollen fuer `node-a` bis `node-d`;
- drei Kantenressourcen fuer den kanonischen Linienkantenbestand;
- pro Kante genau die gespeicherten Rollen `conductive_bound` und
  `refractory`;
- freie Ressource nur als abgeleiteten Kapazitaetsrest;
- lokale Ledger aus Halbanteilen der inzidenten Kanten;
- eine globale Bilanz mit jeder ungerichteten Kante genau einmal;
- den Drei-Kanten-Inventardigest;
- einen nullgesetzten Kandidatensidecar.

Die Frischanatomie muss strukturell spiegelungssymmetrisch sein:

```text
capacity(node-a) = capacity(node-d)
capacity(node-b) = capacity(node-c)
edge_state(node-a--node-b) = edge_state(node-c--node-d)
edge_state(node-b--node-c) maps to itself
```

Konkrete Kapazitaeten und Kantenressourcen bleiben ungebunden. T1 bleibt die
eingefrorene Ein-Kanten-Gegenbaseline und wird nicht als dreifacher
dynamischer Kantenstatus kopiert.

## D-Kontrollgrenze

`node-c` beziehungsweise `D_CONTROL` darf spaeter nur durch den oeffentlich
registrierten Rezeptorframe und die normale Feldkopplung wirken. Verboten
sind:

- ein privater D-Korrekturwert;
- modellrollenspezifische D-Eingaben;
- eine D-Klemme waehrend normaler Geschichte;
- die Uminterpretation von D als Kandidatenressource;
- das Entfernen von D aus privaten Vollzustaenden;
- ein Rollenflag im Modellkern.

D ist notwendig, damit B und C vor Exposition geometrisch gleichartig sind.
Es ist kein vierter fachlicher Messarm.

## Registrierungs- und Ausfuehrungsstatus

Mit S1-RF sind Namen und Formen gebunden, aber noch keine lauffaehigen
Objekte vorhanden:

```text
STATIC_IDENTITIES_BOUND
STATIC_ROLE_AND_REFLECTION_MAPPING_BOUND
STATIC_PAYLOAD_SHAPES_BOUND
NUMERIC_PRIVATE_VALUE_SOURCES_UNAUDITED
DIGESTS_NOT_COMPUTED
GEOMETRY_NOT_REGISTERED_IN_CODE
FRESH_FACTORY_NOT_IMPLEMENTED
MANDATORY_BASELINE_PACKAGE_NOT_EXECUTABLE
```

Dieser Vertrag misst keine Dynamik und trifft keine Aussage zu einer
hypothetischen MCM-Memory.

## Fail-Closed-Regeln

S1-RF wird verletzt, wenn spaeter:

- physischer Geometriedigest und A/B/C/D-Rollenmappingdigest vermischt
  werden;
- ein Modellkern einen Expositionsrollennamen erhaelt;
- Knotennamen, Reihenfolge, Positionen, Kanten oder Carrier abweichen;
- Periodizitaet oder eine Zusatzkante eingefuehrt wird;
- B/C- oder A/D-Frischsymmetrie ohne vorgelagerten Vertrag gebrochen wird;
- D einen versteckten oder modellabhaengigen Eingang erhaelt;
- oeffentliche Frischprojektionen zwischen Modellrollen abweichen;
- private Frischzustaende zwischen Repliken geteilt werden;
- unbekannte Geometrien auf Zwei- oder Drei-Knoten-Payloads zurueckfallen;
- B1-Raten oder M-/M4-Frischwerte ohne eindeutige Quelle gewaehlt werden;
- M4 freie Ressource gespeichert oder T1 kantweise vervielfacht wird;
- vor abgeschlossener Wertquellenpruefung implementiert oder ausgefuehrt
  wird.

## Genau ein naechster Schritt

Als einziger Anschluss ist zulaessig:

```text
S1-RG - statischer Wertquellen- und eindeutiger Ableitbarkeitsaudit fuer
        B1-, B3-B6- und M4-Vier-Knoten-Frischpayloads
```

S1-RG soll ausschliesslich pruefen, ob die fehlenden privaten Zahlenwerte
aus bereits akzeptierten rollenfesten Konfigurationen und Erhaltungsregeln
eindeutig und ohne Retuning folgen. Es darf keine Werte frei waehlen, keine
Gleichung aendern, keinen Digest berechnen, nichts implementieren und nichts
ausfuehren. Ist eine notwendige Zahl nicht eindeutig ableitbar, bleibt die
Registrierung gesperrt und die offene fachliche Wahl muss benannt werden.
