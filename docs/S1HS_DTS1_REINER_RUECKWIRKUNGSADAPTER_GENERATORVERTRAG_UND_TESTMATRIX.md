# S1-HS: DTS-1 Rueckwirkungsadapter- und Generatorvertrag

## Status

S1-HS bindet die spaetere private Implementierung des reinen DTS-1-
Kantenratenadapters und eines getrennten symmetrischen Generatoraufbaus.
Noch keine Implementierung, keine Materialratenwerte, kein gekoppelter
Integrator, keine Runtime und kein Feldlauf.

Entscheidung:

```text
DTS1_PURE_BACKREACTION_CONTRACT_AND_TEST_MATRIX_BOUND
```

## Private Modulgrenze

Die spaetere Implementierung darf ausschliesslich in

```text
mcm_field_organism.dynamic_substrate_dts1_backreaction
```

liegen und definiert einen eigenen `DTS1BackreactionError(ValueError)`.
Paketexport, `current_api`, Snapshot, Restore und Runner bleiben unveraendert.

## Zwei getrennte reine Funktionen

Der Adapter:

```text
compute_dts1_edge_rates(
    layer,
    anatomy,
    substrate_config,
    *,
    backreaction_enabled,
) -> DTS1BackreactionResult
```

Der Generatoraufbau:

```text
build_dts1_diffusion_generator(
    layer,
    adapter_result,
) -> quadratische float64-Matrix
```

Keine der Funktionen darf DTS-1, S oder H fortschreiben. Der Adapter liest
nur einen abgeschlossenen Anatomiezustand. Der Generator liest nur das
fertige Kantenratenledger.

## Geometrie- und Eingabevertrag

`layer` ist ein unveraenderlicher `MCMNeuronLayer` mit vollstaendiger
symmetrischer interner Nachbarschaft. `anatomy` ist eine gueltige
`DTS1ResourceAnatomy`. Beide muessen exakt dasselbe vollstaendige kanonische
Kanteninventar und denselben vorhandenen Kantendigest besitzen.

Es wird keine zweite Geometrieidentitaet eingefuehrt. Fehlende, doppelte,
zusaetzliche oder fremde Kanten brechen vor jeder Ausgabe ab.

`substrate_config` ist die bestehende
`NeutralLocalFieldSubstrateConfig`. Sie liefert ausschliesslich

```text
r_0 = 1 / response_time_seconds
```

`backreaction_enabled` muss ein echter boolescher Wert sein. Es gibt keinen
Default und keinen abgeleiteten Zustandsschalter.

## Adapterausgabe

`DTS1BackreactionResult` enthaelt nur:

- den expliziten Ablationsstatus;
- die bestehende positive Basisrate;
- genau eine kanonische `DTS1BackreactionEdgeRate` je vorhandener Kante;
- den vorhandenen MCM-Kantendigest.

Aktiv gilt exakt:

```text
c_e = b_e / (2 * min(q_i, q_j))
r_e = r_0 * (1 + c_e)
```

Ablatiert gilt exakt `r_e=r_0`. Freie und refraktaere Ressource duerfen in der
Ratenformel nicht gelesen werden. Ein zusaetzlicher Gain, eine Schwelle oder
eine signierte Fallunterscheidung sind verboten.

## Generatoraufbau

Fuer jede Kante `e={i,j}` wird genau einmal gebucht:

```text
G[i,j] += r_e
G[j,i] += r_e
G[i,i] -= r_e
G[j,j] -= r_e
```

Vor Rueckgabe muessen gelten:

```text
G ist endlich, quadratisch und float64
G = transpose(G)
G * 1 = 0
max(eigenvalues(G)) <= gebundene Gleitkommatoleranz
```

Der Generator besitzt keine Randquelle und keine Rezeptor- oder H-Rolle.
Eine solche Grenze gehoert erst zu einem spaeteren gekoppelten Vertrag.

## Verbindliche Testmatrix

| ID | Verpflichtender Nachweis |
|---|---|
| T01 | aktive Formel bei heterogenen Knotenkapazitaeten |
| T02 | Ablation liefert exakt die Basisrate bei identischer Anatomie |
| T03 | `b_e=0` ist exakt neutral |
| T04 | maximale Belegung erreicht, aber ueberschreitet nicht `2*r_0` |
| T05 | gleiche `b_e`, aber andere refraktaere Aufteilung ergibt gleiche momentane Raten |
| T06 | vollstaendiges Layer-/Anatomieinventar und Digest sind zwingend |
| T07 | ungueltige Kontrolle, Konfiguration, Anatomie oder Rate bricht ab |
| T08 | Eingabereihenfolge aendert das Adapterledger nicht |
| T09 | alle Adaptereingaben bleiben unveraendert |
| T10 | Generator ist endlich, quadratisch, float64 und symmetrisch |
| T11 | Nullzeilensumme und konstantes Nullfeld |
| T12 | negative Semidefinitheit |
| T13 | kantenweiser Fluss ist antisymmetrisch und summenerhaltend |
| T14 | unvollstaendiges, doppeltes oder fremdes Ratenledger bricht ab |
| T15 | Adapter ruft keinen Ressourcenschritt auf und liest keine Feldwerte |
| T16 | kein Runtime-, Rand-, I/O-, Snapshot- oder oeffentlicher API-Pfad |

## Aussagegrenze

Ein spaeter bestandener Testverbund zeigt nur korrekte reine Adapter- und
Generatoralgebra. Die momentane Fixed-Adapter-Aequivalenz bleibt bestehen.
Nicht gezeigt sind gekoppelte Stabilitaet, Feldwirkung oder funktionale
Trennung von einer Baseline.

## Bester naechster Schritt

S1-HT darf nach dem naechsten `ok weiter` genau dieses private Adaptermodul
und die 16 technischen Matrixfaelle implementieren. Noch keine
Materialratenwerte, keine gekoppelte Runtime und kein Forschungs- oder
Feldlauf.
