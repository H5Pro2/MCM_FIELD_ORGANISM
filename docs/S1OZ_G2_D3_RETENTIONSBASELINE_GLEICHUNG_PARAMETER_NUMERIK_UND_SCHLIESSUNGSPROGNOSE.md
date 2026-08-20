# S1-OZ G2/D3 Retentionsbaseline: Gleichungs-, Parameter-, Numerik- und Schliessungsvertrag

## Status

S1-OZ bindet ausschliesslich die minimale stationaere Updategleichung, den
einzigen Startwert, die einzige Retentionsfraktion, kanonische
Konfigurations- und Zustandsdigests, exakte Checkpointwerte sowie die atomare
Schliessungsprognose der S1-OY-Gegenbaseline. Es wird nichts implementiert
oder ausgefuehrt.

Entscheidung:

```text
G2_D3_MATCHED_RETENTION_EXACT_EQUATION_PARAMETERS_AND_CLOSURE_PREDICTION_BOUND
```

## Vertragsidentitaeten

```text
g2.d3.matched-retention-update-equation.contract.s1oz.v1
-> 90ed790d33882b8fd7691f75d43ac39530c232712bb3a67766f07771ba82b84a

g2.d3.matched-retention-config.q0-0p5.rho-0p5.s1oz.v1
-> 658d726944639840ed5c6ff0db0f3b8c863567dfa1fbd7aa2bc0fb7ade25ceb8

g2.d3.exact-checkpoint-baseline-closure.contract.s1oz.v1
-> ac13a848fab0e766b4c02568d4c20aa93915cf0f34dce68ac682969f1fcb376c
```

Akzeptierte S1-OY-Vertragsdigests:

```text
baseline contract
= 18ea29690ef7e62ae086c93b43dc3678f8ad5fed81aa1a0fde24983649d6f036

event contract
= d9bfd11f5b1a555bceca419b5f5b6ccfcc1206b692881f0be4b1a29642cfb23a

state anatomy contract
= e886e77d6bec13dbbd462f0454b4758961f499ab28c85608cde068f695d349fb

comparison contract
= 7b3818ca3e9ce2b2b1502399e52d69ca25a02247cca43f06b883633a61d28f0d
```

## Minimale stationaere Gleichung

Der Baselinezustand am Checkpoint `k` ist `q_k`. Bei genau einem gueltigen
modellneutralen Fortsetzungsereignis gilt:

```text
q_(k+1) = rho * q_k
```

Der read-only Checkpointwert ist ohne weitere Abbildung:

```text
y_k = q_k
```

Gebundene Zahlenwerte:

```text
q_0 = 0.5
rho = 0.5
```

Es gibt keinen Bias, Offset, Gain, Clip, Schwellenwert, laufenden Mittelwert,
Zaehler, Zeitparameter oder weiteren Zustand. Die Gleichung wird pro
gueltigem Fortsetzungstoken exakt einmal und insgesamt exakt zweimal
angewendet.

Ein Checkpointreadout und ein fehlendes oder ungueltiges Ereignis fuehren
kein Update aus. Ein ungueltiges Ereignis erzeugt jedoch auch kein
erfolgreiches Teilresultat.

## Parameterauswahl und Informationsgrenze

`q_0` entspricht der bereits vor S1-OX gebundenen gemeinsamen CP0-Referenz.
`rho` entspricht der bereits vor Auswahl dieser Baseline offengelegten
stationaeren Halbierungsstruktur der zwei konservativen D3-Schritte.

Die Baseline ist damit absichtlich eine vor dem Baselinelauf vollstaendig
bestimmte enge Gegenkonstruktion. Sie wird nicht aus einem spaeteren
Baselineergebnis gefittet. Es gibt:

- keinen getrennten Fit fuer XXX und YYY;
- keinen Fit pro Schritt oder Checkpoint;
- keine Suche ueber Parameterwerte;
- keine Anpassung nach einem Test- oder Vergleichsergebnis;
- keinen Zugriff auf D3-Rohbytes oder Kandidatenbelege im Operator.

Die Auswahl prueft gezielt, ob der aktuelle Kandidatenvektor bereits durch
eine minimale zustandsbehaftete Retentionsregel erklaert ist. Sie ist keine
allgemeine Baseline fuer spaetere Konkurrenz- oder Erholungsprofile.

## Kanonischer Konfigurationsrecord

Payload ohne Eigendigest:

```json
{"baseline_class_id":"G2_D3_MATCHED_SINGLE_STATE_RETENTION_BASELINE","configuration_schema_id":"g2_d3_single_state_retention_configuration","configuration_schema_version":"s1oy.v1","initial_retained_capacity":0.5,"retention_fraction_per_fresh_continuation":0.5,"update_rule_id":"ONE_STATIONARY_RETENTION_UPDATE_PER_FRESH_CONTINUATION"}
```

```text
configuration_record_digest
= 68226a0df481c9ae938cc260c386ccbfb0c19444756f6a1d99001fd68602414e
```

Kanonischer vollstaendiger Record:

```json
{"baseline_class_id":"G2_D3_MATCHED_SINGLE_STATE_RETENTION_BASELINE","configuration_record_digest":"68226a0df481c9ae938cc260c386ccbfb0c19444756f6a1d99001fd68602414e","configuration_schema_id":"g2_d3_single_state_retention_configuration","configuration_schema_version":"s1oy.v1","initial_retained_capacity":0.5,"retention_fraction_per_fresh_continuation":0.5,"update_rule_id":"ONE_STATIONARY_RETENTION_UPDATE_PER_FRESH_CONTINUATION"}
```

```text
configuration input digest
= 12e6d381c0dcc0f170c39453bde291152bc55499e0292edacb2d0a09c27e1d93
```

Der Record ist fuer beide Ketten und beide Updates byteidentisch.

## Exakte Zustandsfolge

Aus der vorregistrierten Gleichung folgt ohne Fit:

| Checkpoint | Ereignisse seit Start | `retained_capacity` | State-Recorddigest | State-Inputdigest |
|---|---:|---:|---|---|
| CP0 | `0` | `0.5` | `c51470d4cdf0fc5d24b50a6e7617a7e72346217880a302b0adf5905b0390d0ec` | `f67406ef5f4da6ecd3775ab8c12139dbee607dd33b0c89e14842774c48d0ffd2` |
| CP1 | `1` | `0.25` | `183125e5c5b45acd56314bee5ec3453fd7676f57fb76e965e3f9b6793debce91` | `2eb320f35971b2d29fc5f07adcee5d2e8d05b68398d6655b42086d7ea1a05eb7` |
| CP2 | `2` | `0.125` | `0a65c70bee3b6bb7c6b6a8a4a5f69aae1bca0e00b1b0ca0494ec6a594195cb6b` | `4978a6221f1da66a2959e2661ee335f1c491b127af4a22f18da440f335f3be48` |

Die State-Recorddigests werden jeweils ueber die kanonische Payload ohne
`state_record_digest` berechnet. Die State-Inputdigests binden die
vollstaendigen kanonischen Records einschliesslich ihres Eigendigestfelds.

XXX und YYY muessen dieselben drei Zustandsrecords und Werte erzeugen. Ihre
vollstaendigen Baselinebelegdigests muessen wegen getrennter
Quellprovenienz verschieden sein.

## Exakte Baselineprognose

```text
baseline checkpoint values = (0.5, 0.25, 0.125)

delta CP1-CP0 = -0.25
delta CP2-CP1 = -0.125
delta CP2-CP0 = -0.375
```

Der orientierungsunabhaengige Baselinevergleichsdigest wird ueber dieselbe
kanonische Wert-/Komponentenpayload wie beim Kandidaten gebildet:

```text
baseline comparison digest
= 5c8d3b60bbc205594974f632a878472bf628426dc914af72514cf7b42e8a86a5
```

## Numerische Gueltigkeit

Die Werte `0.5`, `0.25` und `0.125` sind endliche nichtnegative dyadische
Zahlen und in binaerer Gleitkommadarstellung exakt. Beide Multiplikationen
und alle drei gerichteten Differenzen muessen deshalb ohne Rundungsrest die
gebundenen Werte liefern.

Verbindlich gilt:

```text
tolerance = 0.0
NaN or infinity = invalid
negative state = invalid
bool as number = invalid
clipping or renormalization = forbidden
```

Eine numerische Abweichung darf nicht toleriert, gerundet oder als
Kandidatenresiduum interpretiert werden. Sie ist ein technischer Fehler und
liefert `not_computable`.

## Atomare Schliessungsprognose

Nach zwei getrennten vollstaendig gueltigen Ausfuehrungen muss der spaetere
Comparator exakt bilden:

```text
candidate values = (0.5, 0.25, 0.125)
baseline values  = (0.5, 0.25, 0.125)
residual values  = (0.0, 0.0, 0.0)

candidate components = (-0.25, -0.125, -0.375)
baseline components  = (-0.25, -0.125, -0.375)
residual components  = (0.0, 0.0, 0.0)

closure status = BASELINE_CLOSED_CURRENT_CHECKPOINT_VECTOR
```

Kanonische Schliessungspayload:

```json
{"baseline_checkpoint_values":[0.5,0.25,0.125],"baseline_directed_components":[-0.25,-0.125,-0.375],"candidate_checkpoint_values":[0.5,0.25,0.125],"candidate_directed_components":[-0.25,-0.125,-0.375],"residual_checkpoint_values":[0.0,0.0,0.0],"residual_directed_components":[0.0,0.0,0.0]}
```

```text
closure payload digest
= bce12955a3df61976dcf650b9dba93a59c5894d148a07414efd44489d5f2af15
```

Die Entscheidung ist fuer XXX und YYY gemeinsam atomar. Ein fehlender,
ungueltiger oder abweichender Arm liefert keine Schliessungsentscheidung.

## Falsifikations- und STOPP-Regeln

Die technische Baselineabnahme scheitert, wenn:

- ein anderer Startwert oder eine andere Retentionsfraktion verwendet wird;
- mehr oder weniger als zwei Updates stattfinden;
- Readout, Position, Orientierung oder Chainrolle den Zustand aendert;
- XXX und YYY verschiedene Zustandsrecords erzeugen;
- ein Wert nur mit Toleranz, Rundung, Clip oder Nachnormalisierung passt;
- der Operator Kandidatenwerte, Kandidatenbelege oder Fixtureerwartungen
  liest;
- Konfiguration oder Zustand waehrend einer Kette mutiert werden;
- bei einem Fehler ein Teilvektor sichtbar bleibt;
- Kandidat oder Baseline fuer den Vergleich ein zweites Mal ausgefuehrt wird;
- ein technischer Baselinefehler als positives Kandidatenresiduum gilt.

Wenn die spaetere Implementierung alle Bindungen erfuellt, ist der aktuelle
S1-OW-Checkpointvektor methodisch durch diese Gegenbaseline geschlossen.
Dieser Abschluss stoppt nur seine Verwendung als eigene Funktionsevidenz
oder als Evidenz fuer eine hypothetische MCM-Memory-Funktion. Er verwirft
weder die D3-Ressourcenanatomie noch den technischen MCM-Feldkern.

## Aussagegrenze

S1-OZ ist eine statische analytische Prognose. Es gibt noch keinen
Baselineoperator, keinen Comparator, keinen Test und keinen Lauf.

Die erwartete Schliessung ist kein Befund zur hypothetischen MCM-Memory und
keine Aussage ueber Konkurrenz, Interferenz, Erholung oder
Kapazitaetsfreigabe.

## Naechster erlaubter Schritt

S1-PA darf ausschliesslich Produktions- und Testdateigrenzen, kanonische
Konfigurations-/Zustandsfixtures, XXX-/YYY-Provenienz, externe
Fehlermutationen, defensive Gates und ein endliches Einmaltestbudget fuer
Baselineoperator und Comparator statisch binden.

S1-PA darf noch nichts implementieren oder ausfuehren und keine Feld-,
Runtime-, Transfer-, Runner- oder Medienwirkung freigeben.
