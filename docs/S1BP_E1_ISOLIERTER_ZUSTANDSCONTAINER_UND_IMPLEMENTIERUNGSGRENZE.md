# S1-BP: E1 isolierter Zustandscontainer und Implementierungsgrenze

## Status

Statischer Implementierungsvertrag fuer die erste isolierte E1-Scheibe.
Noch keine Implementierung, keine S/H-Rueckwirkung, kein Snapshot-Schema,
kein `current_api`-Export und kein Memory-, Lern-, Organismus- oder KI-Befund.

## Ziel der ersten Scheibe

Die erste Implementierung darf ausschliesslich zeigen, dass der in S1-BO
gebundene E1-Zustand auf der vorhandenen MCM-Geometrie kanonisch angelegt,
validiert und fuer eine explizite Dauer konservativ entwickelt werden kann.

```text
MCMNeuronLayer mit abgeschlossenem S
+ expliziter E1-Vertrag
+ isolierter E1-Vorzustand
+ elapsed_seconds
-> neuer isolierter E1-Zustand
```

Der bestehende Feldzustand wird weder veraendert noch kopiert oder
fortgesetzt.

## Neues explizites Modul

Die Implementierung liegt ausschliesslich in:

```text
mcm_field_organism/e1_local_edge_plasticity.py
```

Tests importieren dieses Modul direkt. In dieser Stufe sind Aenderungen an
folgenden Oberflaechen verboten:

```text
mcm_field_organism/__init__.py
mcm_field_organism/current_api.py
SharedMCMField
NeutralLocalFieldSubstrateConfig
Schema-1-Snapshot und Restore
AV-Consumer und Runner
```

## Fehlergrenze

Das Modul definiert genau einen eigenen technischen Fehler:

```text
E1LocalEdgePlasticityError(ValueError)
```

Fehler werden vor einer Zustandsausgabe ausgeliefert. Numerische Werte,
Endpunktidentitaeten und Kanteninventare werden nicht repariert, geclippt
oder nachnormiert. Nur die bereits gueltigen eindeutigen Kantenobjekte werden
fuer eine deterministische Zustandsdarstellung kanonisch sortiert.

## Unveraenderlicher Vertrag

```text
E1LocalEdgePlasticityContract
    contract_id
    node_capacity
    binding_rate_per_second
    release_rate_per_second
    backreaction_gain
```

Verbindliche Regeln:

```text
contract_id = e1.resource-conserving-local-edge-plasticity.v1
node_capacity > 0
binding_rate_per_second >= 0
release_rate_per_second >= 0
0 <= backreaction_gain <= 1
```

Alle Zahlen muessen endlich und duerfen keine Booleschen Werte sein. Der
Vertrag ist global und darf keine Modalitaets-, Welt-, Objekt-, Label-,
Reward- oder Zielrolle enthalten.

`backreaction_gain` wird in der isolierten Scheibe nur validiert und an die
Vertragsidentitaet gebunden. Er wird noch nicht auf das Feld angewendet.

## Eine Bindung pro vorhandener Kante

```text
E1EdgeBinding
    first_neuron_id
    second_neuron_id
    binding
```

Regeln:

- beide Identitaeten sind nichtleere Strings;
- `first_neuron_id < second_neuron_id`;
- `binding` ist endlich und nichtnegativ;
- jede kanonische Kante kommt im Gesamtzustand genau einmal vor.

Die Kantenidentitaet wird nicht neu konstruiert. Sie muss exakt
`mcm_substrate_edge_inventory(layer)` entsprechen.

## Vollstaendiger E1-Zustand

```text
E1LocalEdgePlasticityState
    contract
    edge_bindings
    edge_inventory_digest
```

Der Zustand validiert:

1. genau einen gueltigen E1-Vertrag;
2. eine nichtleere und eindeutige Bindungsliste, die nach erfolgreicher
   Einzelvalidierung kanonisch sortiert gespeichert wird;
3. einen lowercase SHA-256-Geometriedigest;
4. die lokale Kapazitaetsgrenze
   `0.5 * Summe_e~i(b_e) <= node_capacity` fuer jeden enthaltenen Knoten.

Der Zustand speichert weder `S`, `H`, freie Ressource noch Zeit. Freie
Ressource bleibt der abgeleitete Bilanzrest und darf keine zweite gespeicherte
Wahrheit werden.

## Geometriegebundene Validierung

Die Funktion

```text
validate_e1_state_for_layer(layer, state) -> None
```

prueft vor jeder Entwicklung:

- `layer` ist ein `MCMNeuronLayer`;
- Zustandskanten entsprechen dem vollstaendigen vorhandenen Kanteninventar;
- `edge_inventory_digest` entspricht der aktuellen Geometrie;
- alle Neuronen der verbundenen Geometrie sind durch das Inventar erfasst;
- alle aus dem Zustand abgeleiteten freien Ressourcen sind nichtnegativ.

F3-Zustand und E1-Zustand sind nicht gegenseitig konvertierbar.

## Kanonischer Initialzustand

```text
build_neutral_e1_state(layer, contract)
    -> b_e = 0 fuer jede vorhandene Kante
```

Die Funktion verwendet ausschliesslich
`mcm_substrate_edge_inventory(layer)` und
`mcm_substrate_edge_inventory_digest(layer)`. Sie veraendert den Layer nicht.

Ein angelegter neutraler E1-Zustand ist weiterhin nicht der E1-aus-Arm.

## Abgeleitete freie Ressource

```text
e1_free_node_resources(layer, state)
    -> tuple[(neuron_id, free_resource), ...]
```

Die Ausgabe folgt der kanonischen Neuronenreihenfolge des Layers. Fuer jeden
Knoten gilt:

```text
free_resource
= node_capacity
- 0.5 * Summe(binding aller inzidenten Kanten)
```

Die Funktion ist ein technischer Bilanzobserver. Ihre Werte werden nicht im
Zustand gespeichert.

## Reine Zustandsentwicklung

```text
advance_e1_local_edge_plasticity(
    layer,
    state,
    elapsed_seconds,
) -> E1LocalEdgePlasticityState
```

Verbindliche Grenze:

1. `elapsed_seconds` ist endlich und groesser als null;
2. die Funktion validiert Zustand und Geometrie vor der Rechnung;
3. `S_i` wird aus den abgeschlossenen Aktivierungen des Layers gelesen;
4. `p_e`, halbe Freigabe, gleichzeitige Angebote, lokale Zuteilung und zweite
   halbe Freigabe folgen exakt S1-BO;
5. alle Angebote werden aus demselben Vorzustand berechnet;
6. der Eingabezustand und der Layer bleiben unveraendert;
7. die Funktion gibt genau einen neuen vollstaendigen Zustand zurueck;
8. ein ungueltiges numerisches Ergebnis fuehrt zum Fehler, nicht zum Clip.

Keine andere Zeitquelle, Aufrufzahl oder implizite Standardschrittweite darf
die Entwicklung beeinflussen.

## Keine Serialisierung in dieser Stufe

S1-BP definiert bewusst keine Methoden `canonical_payload`, `from_payload`
oder `digest`. Solche Methoden koennten spaeter eine technische
Zustandsidentitaet bereitstellen, wuerden hier aber bereits eine
Persistenzoberflaeche vortaeuschen. Der Geometriedigest bleibt die einzige
uebernommene Identitaet.

## Fokussierte Abnahme

Die Datei

```text
tests/test_e1_local_edge_plasticity.py
```

muss mindestens pruefen:

1. neutraler Aufbau auf dem vorhandenen Kanteninventar;
2. Ablehnung falscher, fehlender, doppelter oder nichtkanonischer Kanten;
3. Ablehnung nichtendlicher, negativer oder boolescher Zahlen;
4. Ablehnung eines fremden Geometriedigests;
5. exakte reine Freigabe gegen `exp(-k_off * dt)`;
6. Bindung bei Feldspannung und freier Endpunktressource;
7. keine Bindung bei einheitlichem `S`;
8. Nichtnegativitaet und lokale sowie globale Bilanz;
9. Invarianz gegen Kantenreihenfolge in der Eingabekonstruktion;
10. Unveraenderlichkeit von Eingabezustand und Layer;
11. Verfeinerungsvergleich `dt`, `dt/2`, `dt/4`;
12. keine neuen Exporte in `__init__`, `current_api` oder Snapshotrollen.

Tests verwenden kleine synthetische MCM-Layer. Kein Browser, Audio, Video,
Runner oder physischer Weltkontakt ist erforderlich.

## Erfolgsgrenze

Ein bestandener S1-BP-Testverbund belegt nur:

```text
E0: isolierter E1-Zustand ist geometriegebunden,
    endlich, bilanziert und deterministisch entwickelbar
```

Er belegt keine spaetere Feldrueckwirkung, Praegung, Vergessen,
Rekonstruktion oder MCM-Memory.

## Bester naechster Schritt

S1-BQ hat dieses isolierte Modul und den fokussierten Testverbund
implementiert. E0 ist fuer die Bilanzschicht technisch bestanden. Als
naechstes bindet S1-BR statisch den kleinsten ablatierbaren Adapter fuer
symmetrische E1-Kantenraten im schnellen Feldgenerator.
