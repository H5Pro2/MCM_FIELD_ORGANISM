# S1-EC21: Synthetische Siebenarm-Probe-Consumer-Abnahme

## Status

```text
FIXTURE_CONSUMER_ACCEPTED
R2_R4_R8_PROCESSED
ALL_TWENTY_ONE_ARMS_EXECUTED
ALL_REGISTERED_CONTROLS_PASSED
FIXTURE_CONVERGENCE_NOT_ACCEPTED
PERSISTENT_STATES_NOT_CONSUMED
REGISTERED_PROBE_NOT_CONSUMED
NO_RESULT_DECISION
NO_CLAIMS
```

S1-EC21 implementiert den privaten typisierten Consumer fuer die in S1-EC20
gebundene siebenarmige Probeform. Die Abnahme verwendet dieselbe
84-Knoten-/145-Kanten-Geometrie und dieselben unteren Feldoperatoren, aber
kleine neu erzeugte Formationszustaende und eine explizit verkuerzte
`2/4/8`-Probe-Fixture.

Der persistierte S1-EC19-Zustandssatz und die vollstaendige registrierte
`200/400/800`-Probe werden nicht verbraucht.

## Implementierung

```text
mcm_field_organism/e1_confirmation_published_probe_fixture_consumer.py
tests/test_e1_confirmation_published_probe_fixture_consumer.py
```

## Gebundene und substituierte Quellen

```text
registered_probe_source_digest = c0a9a59fb93996bdfd95247a1f6feec19723aeb36c84bd8bc8a423e677fbea7d
registered_probe_plan_set_digest = 00b221266aa6bedf86ed24c1aac1f3112e140077141fcef2993edb77401785e0

fixture_probe_source_digest = ae49199713a39aca542b67ffc5f13883211eb52b54a47ce4e29b94ef8a8fad8f
fixture_probe_plan_set_digest = 9fdf3dc48a03f85df78ebbb0aba46762157bf758fe4e73c5e47101dfb2b8e13c
fixture_matrix_digest = 8470dbf10c2537f76940a3c4bee6e3d22a6ce5bfce1fc5c0e314edfa6d2c674c
result_digest = 1b328220ea65562575b608c7ffaa5a7ecce894ce323080f23009ed7358e9e11f
```

Die Fixture behaelt Modalitaeten, Geometrien, sieben Armrollen und
Operatorfolge bei. Sie substituiert Quelle, Schrittzahlen und gebildete
Zustaende und ist deshalb nicht als wissenschaftliche Probe auswertbar.

## Sieben Arme

Je Verfeinerung wurden ausgefuehrt:

```text
p0, ab0, ba0, ab1, ba1, abf, baf
```

Alle drei Verfeinerungen bestanden:

- sieben anfangs wertgleiche und objektgetrennte Felder;
- Supports genau einmal zugeordnet;
- `p0 == ab0 == ba0` bitgenau;
- `ab1 == abf` und `ba1 == baf` bitgenau;
- AB- und BA-Zustandsobjekte waehrend der Probe eingefroren;
- keine Veraenderung persistenter oder terminaler Artefakte.

## Fixture-Rohwerte

```text
r2 active S/H Linf = 1.3589620647437572e-06 / 1.924748341059629e-06
r4 active S/H Linf = 1.3589620647160017e-06 / 1.924748341201876e-06
r8 active S/H Linf = 1.3589391429161268e-06 / 1.924715062585902e-06

r2 -> r4 probe residual = 6.505213034913027e-16
r4 -> r8 probe residual = 1.7828695117461102e-10
convergence_nonincreasing = false

probe_ablation_residual = 0.0
fixed_adapter_residual = 0.0
frozen_state_change = 0.0
```

Der steigende feine Fixture-Rest entsteht nach einem praktisch bei
Rundungsnull liegenden groben Rest. Diese kleine Fixture ist daher keine
Numerikevidenz fuer die spaetere Vollprobe.

## Evidenzgrenze

S1-EC21 bestaetigt, dass der neue Consumer alle drei Verfeinerungen und alle
sieben Arme kontrolliert ausfuehren kann. Es bestaetigt keine Wirkung der
persistierten S1-EC19-Zustaende.

```text
fixture_payload_only = true
persistent_states_consumed = false
registered_probe_consumed = false
probe_execution_permitted = false
result_decision_permitted = false
claims_permitted = false
```

## Bester naechster Schritt

S1-EC22 sollte statisch den Ressourcen- und Exactly-once-Vertrag fuer eine
einmalige persistente `200/400/800`-Probe binden. Die Laufzeitschaetzung
muss die 9.800 Feldarm-Schritte beruecksichtigen. Bericht, Attempt und Lock
benoetigen eine neue Identitaet; Ergebnisentscheidung und Claims bleiben
auch in diesem Lauf getrennt.
