# S1-RG: Statischer Wertquellen- und eindeutiger Ableitbarkeitsaudit der Vier-Knoten-Frischpayloads

## Status und Umfang

S1-RG prueft ausschliesslich, ob die in S1-RF noch offenen Zahlenwerte fuer
die Vier-Knoten-Frischformen aus bereits akzeptierten rollenfesten Quellen
eindeutig folgen.

Geprueft werden:

- B1-Fixed-Adapter-Raten auf drei Linienkanten;
- B3-B6-M-Frischmassen auf vier Knoten;
- M4-Knotenkapazitaeten und initiale leitende beziehungsweise refraktaere
  Kantenressourcen.

Der Audit waehlt keine neue Invariante, veraendert keine Gleichung oder
Konfiguration, berechnet keine Digests, implementiert nichts und fuehrt
keinen Test oder Feldlauf aus.

Auditentscheidung:

```text
B3_B6_FOUR_NODE_FRESH_MASSES_UNIQUELY_DERIVE_TO_EXACT_QUARTERS
M4_FOUR_NODE_CAPACITIES_UNIQUELY_DERIVE_TO_ONE_PER_NODE
M4_RATES_REMAIN_UNCHANGED_AND_UNIQUELY_SOURCED
M4_THREE_EDGE_INITIAL_CONDUCTIVE_AND_REFRACTORY_VALUES_NOT_UNIQUELY_DERIVABLE
B1_BASE_RATE_GAIN_CAPACITY_AND_FORMULA_UNIQUELY_SOURCED
B1_THREE_EDGE_FIXED_CONDUCTIVE_SOURCE_NOT_UNIQUELY_DERIVABLE
B1_THREE_EDGE_RATES_THEREFORE_NOT_YET_DERIVABLE
REGISTRATION_AND_IMPLEMENTATION_REMAIN_BLOCKED
NO_RETUNING_NO_EXTRAPOLATION_NO_EXECUTION
```

## Ableitbarkeitskriterium

Ein Zahlenwert gilt nur dann als eindeutig ableitbar, wenn eine bereits
akzeptierte Quelle gemeinsam bindet:

1. die Modellrolle;
2. die betroffene physische Groesse;
3. eine geometrierelevante Regel fuer beliebige zulaessige Knotenzahl oder
   exakt die neue Vier-Knoten-Geometrie;
4. die kanonische Verteilung auf Knoten oder Kanten;
5. keine Profil-, Replik-, Ergebnis- oder Kandidatenabhaengigkeit.

Ein Zahlenmuster aus zwei historischen Geometrien ist keine Regel. Eine
Interpolation, Extrapolation, Mittelung oder Wahl der bequemsten alten
Fixture ist ohne expliziten Quellvertrag unzulaessig.

## Quellenbestand B3 bis B6

S1-JA bindet fuer jede Rolle B3 bis B6 gemeinsam:

```text
initial_total_mass = 1.0
initial_M = uniform-by-node-count
```

S1-JZ materialisiert diese bereits akzeptierte Regel fuer vorhandene
Geometrien als `1.0 / len(node_ids)`. Die Regel ist geometrierelevant und
enthaelt keine Profil- oder Ergebnisrolle.

Fuer vier Knoten folgt deshalb eindeutig:

```text
M(node-a) = 0.25
M(node-b) = 0.25
M(node-c) = 0.25
M(node-d) = 0.25
sum(M)    = 1.0
```

`0.25` ist in Binaer64 exakt darstellbar. Die Verteilung erfuellt die
S1-RF-Spiegelungsinvariante sowohl fuer den Rand- als auch den Innenorbit.

Diese Ableitung gilt getrennt fuer B3, B4, B5 und B6. Ihre Arm-,
Konfigurations- und bei B6 Spezifikationsdigests bleiben unveraendert.

Ergebnis:

```text
B3_B6_VALUE_SOURCE_COMPLETE
NO_NEW_PARAMETER_CHOICE_REQUIRED
```

## B1 eindeutig gebundene Quellen

Der vorhandene B1-Vertrag bindet bereits:

- `response_time = 1.0`;
- `base_rate_per_second = 1.0`;
- `capacity_per_node = 1.0`;
- den festen Multiplikator `0.5` der akzeptierten Adapterableitung;
- den aktivierten Fixed-Adapter-Status;
- die Formel
  `rate = base_rate * (1 + 0.5 * fixed_conductive / capacity_per_node)`.

Sobald fuer jede neue Kante ein eindeutiges `fixed_conductive` vorliegt,
ist ihre B1-Rate ohne weitere Wahl bestimmt.

## B1 fehlende Drei-Kanten-Quelle

S1-JA bindet die historischen leitenden Werte nur profilspezifisch:

| Historischer Bezug | Geometrie | Gebundene leitende Kantenwerte |
|---|---|---|
| P_IE | eine Kante | `0.4` |
| P_IH | eine Kante | `0.4` |
| P_IK | zwei Kanten | `0.2`, `0.2` |
| P_IN | zwei Kanten | `0.2`, `0.2` |

S1-JT bindet daraus fuer die alten Payloads `1.2` auf einer Kante und `1.1`
auf zwei Kanten. Weder S1-JA noch S1-JT formuliert jedoch eine allgemeine
Regel wie:

- gleichbleibender Wert pro Kante;
- gleichbleibendes globales Leitbudget;
- gradabhaengige Verteilung;
- orbitabhaengige Verteilung.

Der heutige S1-JZ-Code setzt nur fuer zwei Knoten `1.2` und fuer jeden
anderen vorhandenen Fall `1.1`. Das ist eine historische Zwei-/Drei-Knoten-
Verzweigung, keine autorisierte Vier-Knoten-Regel.

Fuer die drei neuen Kanten bleiben daher mindestens zwei
spiegelungskonforme Freiheitsgrade:

```text
fixed_conductive(node-a--node-b)
  = fixed_conductive(node-c--node-d) = x
fixed_conductive(node-b--node-c)     = y
```

Die Spiegelung erzwingt `x` auf den beiden aeusseren Kanten, aber nicht
`x = y` und auch keinen konkreten Wert.

Ergebnis:

```text
B1_FIXED_CONDUCTIVE_SOURCE_INCOMPLETE
B1_EDGE_RATES_NOT_YET_BINDABLE
```

## M4 eindeutig gebundene Quellen

Der akzeptierte DTS-1-Konfigurationsbestand bindet rollenfest:

```text
node_capacity = 1.0
binding_rate  = 0.4
turnover_rate = 0.3
recovery_rate = 0.2
```

Die Knotenkapazitaet ist nicht profilabhaengig. Fuer die Vier-Knoten-
Geometrie folgt deshalb eindeutig:

```text
capacity(node-a) = 1.0
capacity(node-b) = 1.0
capacity(node-c) = 1.0
capacity(node-d) = 1.0
global_capacity = 4.0
```

Die drei Dynamikraten bleiben unveraendert. Dies ist keine neue Gleichung
oder Parameterauswahl.

## M4 fehlende Kanteninitialisierung

Die historischen DTS-1-Quellen binden unterschiedliche initiale
Kantenressourcen fuer unterschiedliche Auditzwecke:

| Historischer Bezug | leitend | refraktaer |
|---|---:|---:|
| Ein-Kanten-P_IE/P_IH | `0.4` | `0.2` beziehungsweise armweise `0.8` |
| Zwei-Kanten-P_IK/P_IN | je `0.2` | je `0.1` |
| einzelne Nullquellenkontrollen | `0.0` | `0.0` |

Die Nullquellen waren Gegenkontrollen und duerfen nicht als allgemeiner
M4-Frischzustand umgedeutet werden. Die Ein- und Zwei-Kanten-Werte stammen
aus profilspezifischen Fixtures. S1-RB hat deren private Fabriken
ausdruecklich nicht als allgemeine M4-Frischquelle akzeptiert.

S1-HI bindet Anatomie, Nichtnegativitaet und Erhaltung, aber keine
Initialwerte. Erhaltung kann aus Kapazitaet und zwei unbekannten
Kantenkompartimenten nur den freien Rest ableiten; sie bestimmt die
gespeicherten leitenden und refraktaeren Werte nicht.

Unter der S1-RF-Spiegelung verbleiben vier unbekannte Werte:

```text
conductive(outer-left) = conductive(outer-right) = c_outer
conductive(middle)                              = c_middle
refractory(outer-left) = refractory(outer-right) = r_outer
refractory(middle)                              = r_middle
```

Lokale und globale Erhaltung begrenzen diese Werte, waehlen sie aber nicht.

Ergebnis:

```text
M4_CAPACITY_AND_RATE_SOURCES_COMPLETE
M4_INITIAL_EDGE_RESOURCE_SOURCE_INCOMPLETE
M4_FRESH_ANATOMY_NOT_YET_BINDABLE
```

## Gemeinsame Ursachenwurzel von B1 und M4

B1 ist als Fixed-Adapter-Gegenbaseline aus einem leitenden Vorzustand
abgeleitet. M4 traegt diesen leitenden Anteil als dynamische
Kantenressource. Fuer einen fairen Gegenvergleich duerfen ihre
Vier-Knoten-Initialisierungen nicht unabhaengig voneinander gewaehlt werden.

Die offene Frage lautet deshalb nicht getrennt "welche B1-Rate?" und
"welche M4-Anatomie?", sondern:

```text
Welche bereits begruendbare Geometrieerweiterungsinvariante uebertraegt den
gemeinsamen leitenden und refraktaeren Ausgangsbestand auf drei Kanten?
```

Erst eine solche Invariante kann:

- M4-Kantenressourcen festlegen;
- den entsprechenden B1-Fixed-Conductive-Bestand bestimmen;
- daraus die B1-Raten eindeutig ableiten;
- B1 und M4 geometrisch fair gekoppelt halten.

## Nicht zulaessige Scheinableitungen

S1-RG verwirft insbesondere:

- `1.1` fuer alle drei B1-Kanten nur deshalb, weil vier Knoten nicht zwei
  Knoten sind;
- `0.2/0.1` auf jeder M4-Kante nur durch Kopieren der Zwei-Kanten-Fixture;
- globale Drittelung allein aufgrund optischer Gleichmaessigkeit;
- Nullinitialisierung als angeblich neutralen Default;
- getrennte Auswahl von B1 und M4;
- unterschiedliche Initialwerte zwischen den 16 Repliken;
- eine nachtraegliche Anpassung anhand spaeterer Resultate.

Diese Varianten koennen Gegenstand eines spaeteren Invariantenaudits sein,
sind aber in S1-RG nicht ausgewaehlt.

## Paketstatus

Der Wertquellenaudit schliesst B3 bis B6 numerisch auf Frischzustandsebene.
Er schliesst B1 und M4 noch nicht:

```text
B3_B6_FOUR_NODE_FRESH_VALUES_READY_FOR_LATER_DIGEST_BINDING
B1_FOUR_NODE_PAYLOAD_BLOCKED
M4_FOUR_NODE_FRESH_ANATOMY_BLOCKED
PHYSICAL_GEOMETRY_REGISTRATION_BLOCKED
MANDATORY_BASELINE_PACKAGE_NOT_EXECUTABLE
```

Ein nicht eindeutig ableitbarer Initialwert ist kein dynamischer Befund und
keine Aussage zu einer hypothetischen MCM-Memory.

## Fail-Closed-Regeln

S1-RG wird verletzt, wenn spaeter:

- B3-B6 andere als gleichmaessige Viertelmassen erhalten;
- B3-B6-Gesamtmasse oder Konfiguration geaendert wird;
- M4-Knotenkapazitaeten oder Raten ohne neuen Vertrag geaendert werden;
- historische Profilwerte als allgemeine Vier-Knoten-Regel ausgegeben
  werden;
- B1-Raten vor der leitenden Kantenquelle gebunden werden;
- B1 und M4 verschiedene leitende Ausgangsquellen verwenden;
- Spiegelung allein als Beweis fuer Gleichheit von mittlerer und aeusserer
  Kante behandelt wird;
- eine Erhaltungsidentitaet als Initialwertgleichung umgedeutet wird;
- ein Resultat zur nachtraeglichen Parameterwahl verwendet wird;
- Digests, Implementierung oder Ausfuehrung vor Abschluss der offenen
  Invariantenentscheidung beginnen.

## Genau ein naechster Schritt

Als einziger Anschluss ist zulaessig:

```text
S1-RH - statischer Geometrieerweiterungsinvariantenvergleich fuer den
        gemeinsamen B1/M4-Drei-Kanten-Ausgangsbestand
```

S1-RH soll die mindestens notwendigen Alternativen getrennt vergleichen:
lokal kantenwerttreu, global budgettreu und vollstaendig freie
Nullinitialisierung. Jede Alternative muss gegen B1-Funktionsidentitaet,
M4-Erhaltung, B/C-Spiegelung, Gradunterschiede, Baselinefairness und
historische Quellen abgegrenzt werden. Noch keine Auswahl, keine neuen
Werte, keine Digests, keine Implementierung und keine Ausfuehrung.
