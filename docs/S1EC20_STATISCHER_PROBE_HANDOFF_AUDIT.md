# S1-EC20: Statischer Probe-Handoff-Audit

## Status

```text
STATIC_HANDOFF_READY
S1_EC19_REPORT_HASH_BOUND
FIFTEEN_STATE_ROLES_INVENTORIED
SIX_ACTIVE_STATES_BOUND
SEVEN_PROBE_ARMS_PREREGISTERED
NO_PROBE_EXECUTION
NO_RESULT_DECISION
NO_CLAIMS
```

S1-EC20 liest den persistenten S1-EC19-Bericht unveraendernd, rekonstruiert
alle Zustaende typisiert und bindet den spaeteren Probe-Handoff. Es werden
keine Probefelder erzeugt, keine Feldschritte ausgefuehrt und keine Dateien
publiziert.

## Implementierung

```text
mcm_field_organism/e1_confirmation_published_probe_handoff_audit.py
tests/test_e1_confirmation_published_probe_handoff_audit.py
```

## Gebundene Quelle

```text
report_sha256 = 93cc94ddb18f80919067ff4e29ccae5aa038bb436d72584acef2d38e57be1fcc
audit_digest = 3524e973ee92e0551d85ea8be561ea0006f61909d3779e1e81cdb2109f596c2a
state_count = 15
edge_binding_count = 2175
unique_state_digest_count = 7
```

Die 15 Rollen besitzen erwartungsgemaess sieben Wertklassen:

- `ab_identity` ist je Verfeinerung bitgleich zu `ab`;
- alle sechs formationsablatierten Rollen tragen denselben neutralen Zustand;
- die sechs aktiven AB/BA-Zustaende aus `r2/r4/r8` sind untereinander
  digestverschieden.

Damit werden Kontrollgleichheit und aktive Zustandsverschiedenheit getrennt
behandelt. Eine Rollenanzahl wird nicht faelschlich als Anzahl verschiedener
Zustandswerte ausgegeben.

## Aktive Zustandsrollen

```text
r2:ab = 1517fdbe0f545b52658c0ae0160c81e4c2b66fbf6c849c0ef29469ffe8b87d10
r2:ba = 9552637705c013acec17dc0a8d94a36ecf7700e059e6434f4341f8c503375ab1
r4:ab = da6871ad5246b7c9127e4b7197eaf5b6a6712590ef5b371c6ff223e4223c3d30
r4:ba = 6ef6aaea3b7dfcf8fe43fbf88912ad99af72bc2db6aafbe3f0f00e2d06dd40e0
r8:ab = 0efddbcb22ae7f5640730692eac593b1321f99274b3ee5e4b6e886de27aebc9d
r8:ba = b985ebdf21e36370f8eb8cecb0f9e49342f6aead625a03c59b7592994cf97b10
```

`r2/r4` sind numerische Kontrollrollen. `r8:ab` und `r8:ba` sind die beiden
spaeteren Entscheidungskandidaten. Die uebrigen drei `r8`-Rollen bleiben
Identitaets- und Ablationskontrollen.

## Vorregistrierte Probe

Die Probe stammt aus demselben bereits vor S1-EC19 vorbereiteten typisierten
Eingangsbundle. Sie wurde nicht anhand der S1-EC19-Ergebnisse ausgewaehlt.

```text
probe_source_digest = c0a9a59fb93996bdfd95247a1f6feec19723aeb36c84bd8bc8a423e677fbea7d
probe_plan_set_digest = 00b221266aa6bedf86ed24c1aac1f3112e140077141fcef2993edb77401785e0

r2 plan = a2b77ea6f688e07586d52bd689bf0b7e281c645f0569112315a41eb1c2ec3e42
r4 plan = 8c2e83617efa7095a3ecd3083f80bad34fb5fb7b8fbb7da846ce225772fbdd8f
r8 plan = 1479ad8b9ccb09727fe3e12f985632f594bed4934e4f2f7e40423f4cd6831e5e
```

Je Verfeinerung sind sieben frische, wertgleiche und objektgetrennte Felder
vorgesehen:

```text
p0, ab0, ba0, ab1, ba1, abf, baf
```

Pflichtkontrollen sind bitgenaue Ablation gegen P0, bitgenaue feste
Adapterbaselines gegen die aktiven Arme, eingefrorene E1-Zustaende,
identische Supports und getrennte `r2/r4`- sowie `r4/r8`-Probereste. Eine
Ergebnisentscheidung bleibt gesperrt, bis das feine aktive Signal streng
groesser als der achtfache feine numerische Rest ist.

## Evidenzgrenze

S1-EC20 bestaetigt nur, dass Quelle, Zustaende, Rollen, Probeplaene,
Kontrollen und Metriken vor einer Ausfuehrung eindeutig gebunden sind. Es
bestaetigt keine spaetere Feldantwort und kein Memory.

```text
probe_execution_permitted = false
result_decision_permitted = false
claims_permitted = false
```

## Bester naechster Schritt

S1-EC21 sollte den privaten typisierten Probe-Consumer fuer genau diesen
Auditvertrag implementieren und mit einer kleinen synthetischen Fixture
abnehmen. Dabei muessen alle sieben Arme und `r2/r4/r8` verarbeitet werden,
aber der persistierte S1-EC19-Bericht darf noch nicht in einer echten Probe
verbraucht werden.
