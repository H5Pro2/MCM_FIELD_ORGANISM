# S1-EA6: E1 kanonischer verfeinerter Einmallauf

## Status

Der kanonische verfeinerte Bildungs- und Transferlauf wurde nach dem
S1-EA5-Gate genau einmal ausgefuehrt und atomar veroeffentlicht. Die
vorregistrierte technische Entscheidung lautet:

```text
NUMERICALLY_UNDECIDABLE
```

Das ist weder ein positiver Nachweis noch ein technischer Fehler. Eine
Wiederholung oder Nachparametrierung dieses Laufs ist nicht gestattet.

## Ergebnisartefakt

```text
reports/e1_refined_formation_transfer_s1ea_once_v1.json
```

```text
Release-Digest:
2a4da932e35c518fc15507eb1461f4e6e916e7d4d5922e58e3df02305a916386

Bericht-SHA-256:
adf8b2b6c1b9fdda48062dbb1cd9149fcde462a3dc77a348aa2dfb0cb1fcaa47

Ergebnis-SHA-256:
321b83ca3a99df0474b09d8d9131f031c734dcc2ae67ea32993ed604802678bc
```

Nach erfolgreicher Veroeffentlichung wurden Versuchs- und Sperrmarker
entfernt. Der Ergebnisbericht belegt den Exactly-once-Pfad dauerhaft.

## Kanonische Rohwerte

| Rolle | r1 | r2 | r4 |
|---|---:|---:|---:|
| `d_state` | 0.0008301610449153929 | 0.0008453023645430579 | 0.000852954804258883 |
| `d_total_binding` | 0.00037698677602990976 | 0.0003860800896616501 | 0.0003906361491561733 |
| `d_probe_s` | 0.000006060458470791286 | 0.000006185938147662551 | 0.00000624961504122612 |
| `d_probe_h` | 0.000006506083697885301 | 0.000006377558586692644 | 0.000006313962658058281 |

Verfeinerungsreste:

```text
state r1/r2 = 7.040697694337024e-05
state r2/r4 = 3.4885390053043374e-05
probe r1/r2 = 1.6431350245149634e-06
probe r2/r4 = 8.140854720894986e-07
```

Alle elf Pflichtkontrollen sind wahr. Identitaets-, Bildungsablations-,
Probeablations-, Fixed-Adapter- und Ressourcenrest sind exakt `0.0`.

## Warum unentscheidbar

Zustands- und Probenreste werden bei der Verfeinerung kleiner. Der feine
Zustandsabstand liegt deutlich ueber seinem vorregistrierten Achtfachboden.
Beide feinen Probensignale verfehlen ihren gemeinsamen Achtfachboden jedoch
knapp:

```text
8 * probe r2/r4 = 6.512683776715989e-06
d_probe_s        = 6.24961504122612e-06
d_probe_h        = 6.313962658058281e-06
```

Verhaeltnis Signal zu feinem Rest:

```text
state   > 8
probe S ~= 7.68
probe H ~= 7.76
```

Nach der vor dem Lauf gebundenen Regel darf deshalb nicht
`REFINED_WORLD_FORMATION_AND_TRANSFER_EFFECT` entschieden werden. Da die
Signale nicht null sind und alle Kontrollen bestehen, ist auch
`NO_REFINED_WORLD_FORMATION_EFFECT` unzulaessig. Es bleibt ausschliesslich
`NUMERICALLY_UNDECIDABLE`.

## Implementierung und Audit

```text
mcm_field_organism/e1_canonical_refined_chain_one_shot_execution.py
mcm_field_organism/e1_canonical_refined_chain_result_audit.py
tests/test_e1_canonical_refined_chain_one_shot_execution.py
tests/test_e1_canonical_refined_chain_result_audit.py
```

Normalisierte Implementierungsdigests:

```text
Ausfuehrung:
20bc6abee9c7c800eceba07a5a2eaadf41431ea75a16255217d30a5bb4c4fc57

Ergebnisaudit:
912ff0f98047f0e5ccbfd01ad4894847a71060bb6d482cc794e1ab99f9247f31
```

Historische Vorbereitungstests verwenden nach dem Lauf nur noch temporaere
freie Pfade. Der echte Projektordner wird ausschliesslich vom unveraenderlichen
Ergebnisaudit gelesen.

```text
411 Tests im vollstaendigen post-run E1-Verbund
OK
```

## Aussagegrenze

Nachgewiesen ist eine kontrollierte, reihenfolgeabhaengige E1-Zustandsbildung
und eine spaetere zustandsabhaengige Feldantwort mit exakten Ablationen und
Fixed-Adapter-Kontrollen. Nicht nachgewiesen ist, dass der feine
Probeunterschied ausreichend vom numerischen Verfeinerungsrest getrennt ist.

Der Lauf begruendet daher keinen MCM-Memory-, Semantik-, Organisations-,
Topologie-, Selbstregulations- oder KI-Claim.

## STOPP fuer diesen Lauf

S1-EA6 darf nicht wiederholt, nachparametriert oder durch eine nachtraeglich
weichere Schwelle positiv umgedeutet werden. Sein Ergebnis ist terminal.

## Bester naechster Schritt

Ein neuer S1-EB-Korridor kann statisch als unabhaengige
Verfeinerungsbestaetigung entworfen werden. Er muss vor jeder Ausfuehrung
Quellen, `r2/r4/r8`, unveraenderte Mechanik, denselben Achtfachfaktor,
Exactly-once-Pfade und die Gegenentscheidung binden. S1-EA6 bleibt dabei nur
Upstreambefund und wird weder wiederholt noch mit neuen Werten ueberschrieben.

## Anschluss

S1-EB registriert diesen neuen `r2/r4/r8`-Korridor nun statisch. Nur die
Plannerimplementierung ist als naechster Schritt freigegeben.
