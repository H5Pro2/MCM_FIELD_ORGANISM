# S1-EC29: Statischer n1/n2-Pilotvertrag

## Status

```text
CORRECTED_EC27_PLANS_BOUND
EC28_REAL_FIXTURE_BOUND
N1_N2_R2_R4_R8_LOAD_EXACT
P0_ABLATION_AND_ACTIVE_ROLES_SEPARATED
RUNNER_IMPLEMENTATION_ONLY
NO_PILOT_EXECUTION
NO_PERSISTENCE_DECISION_OR_CLAIM
```

S1-EC29 bindet Ressourcen, Reihenfolge und Abbruchgrenzen fuer eine spaetere
nichtkanonische n1/n2-Pilotmatrix. Der Vertrag fuehrt keinen Arm aus, misst
keine dynamischen Ressourcen und legt keinen Ergebnis- oder Markerpfad an.

## Matrix

Je Kontaktzahl und Verfeinerung sind sechs Rollen gebunden:

```text
p0_repeated
p0_continuous
repeated_formation_ablated
continuous_formation_ablated
repeated_active
continuous_active
```

P0 besitzt keinen E1-Zustand und keinen Adapter. Die Bildungsablation besitzt
einen neutralen E1-Zustand, dessen Fortschreibung abgeschaltet bleibt. Nur
die beiden Aktivarme verwenden die unveraenderte E1-Mechanik.

## Last und Reihenfolge

```text
n1 r2/r4/r8 steps per arm = 202 / 404 / 808
n1 six-arm load = 8,484 field-arm steps

n2 r2/r4/r8 steps per arm = 402 / 804 / 1,608
n2 six-arm load = 16,884 field-arm steps

total = 25,368 field-arm steps
```

Ausfuehrungsfolge ist fest:

```text
n1: r2 -> r4 -> r8
danach
n2: r2 -> r4 -> r8

je Batch:
P0 -> Bildungsablation -> Aktivarme
```

Bei einem Kontrollfehler wird vor dem naechsten Batch abgebrochen. Es darf
kein partieller Ergebniscontainer entstehen.

## Ressourcenrahmen

```text
minimum free memory = 4 GiB
minimum free disk = 1 GiB
maximum runtime = 900 seconds
persistence = forbidden
```

Die Plattenanforderung bleibt als allgemeine Betriebsreserve gebunden; der
Pilot selbst arbeitet ausschliesslich in Memory.

## Evidenzgrenze

Eine spaetere Pilotmatrix darf nur technische Runnerbereitschaft,
Kontrollidentitaeten und Numerikverhalten liefern. Selbst ein n1/n2-Kontrast
waere keine Entscheidung ueber wiederholungsabhaengige Bildung, weil n4/n8
und die vollstaendige Baselineentscheidung fehlen.

## Bester naechster Schritt

S1-EC30 sollte den sechsarmigen Pilotrunner implementieren und nur mit einer
kleinen injizierten synthetischen Batch-Fixture abnehmen. Geprueft werden
Reihenfolge, Fail-fast-Verhalten, P0-/Ablationsrollentrennung und ein rein
technischer Rohcontainer. Die gebundene 25.368-Schritt-Pilotmatrix bleibt
weiter unausgefuehrt.
