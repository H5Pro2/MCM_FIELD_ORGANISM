# S1-BS: E1 Kantenratenadapter Implementierung und Abnahme

## Status

Reiner E1-Kantenratenadapter und gewichteter interner Generator implementiert
und fokussiert abgenommen. Noch keine gekoppelte S/H-Runtime, kein
Snapshot-Schema, kein `current_api`-Export und kein Memory-, Lern-,
Organismus- oder KI-Befund.

## Implementierte Dateien

```text
mcm_field_organism/e1_weighted_field_adapter.py
tests/test_e1_weighted_field_adapter.py
```

Bestehende Runtime- und API-Dateien wurden nicht veraendert.

## Implementierte Rollen

```text
E1WeightedFieldAdapterError
E1WeightedEdgeRate
E1WeightedFieldAdapterResult
compute_e1_weighted_edge_rates(...)
build_e1_weighted_diffusion_generator(...)
```

## Gebundene Wirkung

Der aktive Adapter uebersetzt jede vorhandene E1-Kantenbindung in:

```text
r_e = r_0 * (1 + gamma * b_e / q_0)
```

Der technische Ablationsarm verwendet bei demselben unveraenderten
E1-Zustand exakt `r_e = r_0`. Der Adapter entwickelt weder E1 noch S/H.

Der Generator wird direkt aus den kanonischen ungerichteten Kantenraten
aufgebaut. Er ist symmetrisch, besitzt Nullzeilensummen und ist
negativ-semidefinit. Rezeptorgrenzen sind nicht Teil des Moduls.

## Fokussierte Abnahme

Ausgefuehrt mit:

```text
python -m unittest -v tests.test_e1_weighted_field_adapter
```

Ergebnis:

```text
9 tests
OK
```

Geprueft wurden aktive Ratenformel, Ablation bei identischem Zustand,
Neutralitaet fuer Nullbindung und Nullgain, maximale Korridorrate,
Geometrie- und Digestfehler, Ratencontainer, Eingabeunveraenderlichkeit,
API-Isolation sowie Symmetrie, Nullzeilensumme und Eigenwertgrenze des
Generators.

## Gemeinsamer Regressionstest

Ausgefuehrt wurden gemeinsam:

```text
tests.test_e1_weighted_field_adapter
tests.test_e1_local_edge_plasticity
tests.test_mcm_substrate_state
tests.test_neutral_local_field_substrate
tests.test_current_api_end_to_end_consumer
tests.test_current_api_browser_payload_consumer
```

Ergebnis:

```text
46 tests
OK
```

## Technisches Urteil

```text
aktive E1-Kantenraten:            bestanden
identische Rueckwirkungsablation: bestanden
Ratenbegrenzung:                  bestanden
gewichtete Generatorsymmetrie:    bestanden
interne Erhaltung:                bestanden
negative Semidefinitheit:         bestanden
Geometriebindung:                 bestanden
E0-Regressionsfreiheit:           bestanden
neutrale S/H-Regressionsfreiheit: bestanden
current_api-Isolation:            bestanden
```

## Aussagegrenze

S1-BS zeigt, dass ein E1-Zustand in einen gueltigen internen Feldgenerator
uebersetzt werden kann. Der Generator wurde noch nicht zur Fortsetzung eines
S/H-Feldes verwendet. Eine spaetere kausale Feldwirkung, Praegung,
Rekonstruktion oder MCM-Memory ist nicht nachgewiesen.

## Bester naechster Schritt

S1-BT hat die atomare Reihenfolge eines neuen isolierten opt-in
E1/S/H-Schritts spezifiziert. Zwei halbe E1-Schritte umschliessen einen
vollstaendigen S/H-Schritt mit dem E1-Mittelzustand. Als naechstes
implementiert S1-BU diesen synchronen Schritt und prueft P0, A0 und A1.
