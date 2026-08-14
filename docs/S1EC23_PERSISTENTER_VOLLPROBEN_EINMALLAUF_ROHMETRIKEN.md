# S1-EC23: Persistenter Vollproben-Einmallauf mit Rohmetriken

## Status

```text
FULL_REGISTERED_PROBE_EXECUTED_ONCE
ALL_NINE_THOUSAND_EIGHT_HUNDRED_FIELD_ARM_STEPS_EXECUTED
PERSISTENT_STATES_CONSUMED_FROZEN
ALL_REGISTERED_CONTROLS_PASSED
RAW_METRICS_PUBLISHED_AND_RELOADED
NUMERICAL_CONVERGENCE_NONINCREASING
NO_RESULT_DECISION
NO_CLAIMS
```

S1-EC23 fuehrte nach der S1-EC22-Freigabe genau eine registrierte
`200/400/800`-Probe gegen die persistenten S1-EC19-Zustaende aus. Je
Verfeinerung liefen sieben Arme. Der Bericht enthaelt Rohvektoren,
Kontrollmetriken und Verfeinerungsreste, aber keine Forschungsentscheidung.

## Implementierung

```text
mcm_field_organism/e1_confirmation_full_published_probe_once.py
tests/test_e1_confirmation_full_published_probe_once.py
```

## Einmallauf

```text
execution_id = e1.full-published-probe.s1ec23.once.v1
field_arm_step_count = 9800
runtime_seconds = 205.23553969990462
report_bytes = 27906
report_sha256 = 85a114b9de5f2152558ca78a03a15f5690607fab98b7f9ddbf10cadf32e8b50e
raw_result_digest = 4c0e74fe291a43d69ca49fa6285ae36eeee2829df4225cf1aba75240b022de81
```

Der Bericht wurde atomar publiziert, erneut gelesen und typisiert
rekonstruiert. Attempt und Lock wurden erst danach entfernt. Die Identitaet
darf nicht wiederholt werden.

## Ressourcen

Unmittelbar vor dem Lauf wurden gemessen:

```text
free_memory_bytes = 8258609152
free_disk_bytes = 236808015872
resource_snapshot_digest = 4e6514efaa25bc786df843338c0c61b2d539c7fe2977aed783b8c913449dddae
release_decision_digest = 899d6ee03ca9481f3bf765d89e5e335332b6341360a3d9ef3af3d515b584c564
```

## Rohwerte

```text
r2 active S/H Linf = 6.185938147662551e-06 / 6.377558586692644e-06
r4 active S/H Linf = 6.24961504122612e-06 / 6.313962658058281e-06
r8 active S/H Linf = 6.28168776978244e-06 / 6.282331414225739e-06

r2 -> r4 probe residual = 8.140854720894986e-07
r4 -> r8 probe residual = 4.0517124277883454e-07
convergence_nonincreasing = true
```

Alle drei Verfeinerungen bestanden:

```text
probe_ablation_residual = 0.0
fixed_adapter_residual = 0.0
frozen_state_change = 0.0
all_registered_controls_passed = true
source_states_unchanged = true
```

## Artefakt

```text
synthetic_runs/s1ec23_full_published_probe_once_v1/
  e1_full_published_probe_s1ec23_once_v1.json
```

Der geschuetzte S1-EC19-Quellbericht blieb unter SHA-256
`93cc94ddb18f80919067ff4e29ccae5aa038bb436d72584acef2d38e57be1fcc`
unveraendert.

## Evidenzgrenze

S1-EC23 liefert erstmals kontrollierte Rohdaten einer spaeteren identischen
Probe auf den persistenten, zeitgeordnet gebildeten E1-Zustaenden. Der
sinkende Verfeinerungsrest und die exakten Gegenkontrollen sind relevante
Evidenz, aber der Lauf selbst trifft absichtlich keine Entscheidung.

```text
result_decision_permitted = false
claims_permitted = false
```

Insbesondere sind Memory, Bedeutung, Organisation, Semantik,
Selbstregulation und KI weiterhin nicht nachgewiesen.

## Bester naechster Schritt

S1-EC24 sollte den unveraenderten S1-EC23-Bericht statisch gegen die bereits
in S1-EC20 gebundene Entscheidungsregel auditieren. Zu pruefen sind
Schutzhash, Kontrollnullen, nichtzunehmender Rest und die strenge Bedingung,
dass jedes feine r8-Aktivsignal groesser als der achtfache feine Rest ist.
Keine neue Probe und keine Nachparametrierung.
