# S1-OY G2/D3 Retentionsbaseline: Anatomie-, Ereignis-, Schema-, Digest- und Fail-Closed-Vertrag

## Status

S1-OY bindet ausschliesslich die diskrete Einzustandsanatomie, einen
modellneutralen Fortsetzungstoken, private Ausfuehrungsreihenfolge,
Schemafelder, Vertragsdigests, passive Belegrollen und Fail-Closed-Codes der
in S1-OX gewaehlten Gegenbaseline. Es werden keine Zahlenparameter oder
Gleichung gewaehlt, nichts implementiert und nichts ausgefuehrt.

Entscheidung:

```text
G2_D3_MATCHED_RETENTION_ANATOMY_EVENT_SCHEMA_DIGEST_FAIL_CLOSED_BOUND
```

## Vertragsidentitaeten

ASCII-Identitaeten und SHA-256-Digests:

```text
g2.d3.matched-single-state-retention-baseline.contract.s1oy.v1
-> 18ea29690ef7e62ae086c93b43dc3678f8ad5fed81aa1a0fde24983649d6f036

g2.d3.model-neutral-fresh-continuation-event.contract.s1oy.v1
-> d9bfd11f5b1a555bceca419b5f5b6ccfcc1206b692881f0be4b1a29642cfb23a

g2.d3.single-state-retention-anatomy.contract.s1oy.v1
-> e886e77d6bec13dbbd462f0454b4758961f499ab28c85608cde068f695d349fb

g2.d3.candidate-baseline-checkpoint-comparison.contract.s1oy.v1
-> 7b3818ca3e9ce2b2b1502399e52d69ca25a02247cca43f06b883633a61d28f0d
```

Akzeptierte bestehende Digests:

```text
two-step composition contract
= e68646a2d4a605ecdd36125dcd5f97cd849091d5af1bbcf1f587b1c01e1c2e06

candidate checkpoint contract
= 582e0fa653c8843cb56e848abc1ea34b1e97b455f8b0a130f22678afb555191f

candidate comparison digest
= 5c8d3b60bbc205594974f632a878472bf628426dc914af72514cf7b42e8a86a5
```

Der letzte Wert ist nur die gebundene Kandidatenreferenz fuer einen spaeteren
Vergleich. Er ist kein Baselineeingang und kein Baselineparameter.

## Diskrete Zustandsanatomie

Die Baseline besitzt genau einen fachlichen Zustand:

```text
retained_capacity
```

Ein spaeterer gueltiger Wert muss ein endlicher, nichtnegativer skalarer
Zahlenwert sein. S1-OY bindet noch keinen Start- oder Folgewert.

Ein kanonischer Zustandsrecord darf genau tragen:

```text
state_schema_id
state_schema_version
baseline_class_id
retained_capacity
state_status
state_record_digest
```

Feste Schemawerte:

```text
state_schema_id = g2_d3_single_state_retention_state
state_schema_version = s1oy.v1
baseline_class_id = G2_D3_MATCHED_SINGLE_STATE_RETENTION_BASELINE
state_status = valid | not_computable
```

Der Record enthaelt keine D3-Ressourcenrolle, Kante, Orientierung,
Chainrolle, Schrittnummer, Zeitdauer, Feldkomponente, Nachhallspur oder
Kandidatenbelegdigest.

Ungueltig sind insbesondere NaN, Unendlich, negative Werte, Boolwerte,
zusaetzliche Felder, fehlende Felder, nichtkanonische Darstellung und ein
falscher Eigendigest. Ungueltige Zustandsrecords werden weder repariert noch
geclippt.

## Noch ungebundene Konfigurationsanatomie

Der spaetere Konfigurationsrecord darf strukturell genau tragen:

```text
configuration_schema_id
configuration_schema_version
baseline_class_id
initial_retained_capacity
retention_fraction_per_fresh_continuation
update_rule_id
configuration_record_digest
```

Feste Schemawerte:

```text
configuration_schema_id = g2_d3_single_state_retention_configuration
configuration_schema_version = s1oy.v1
update_rule_id = ONE_STATIONARY_RETENTION_UPDATE_PER_FRESH_CONTINUATION
```

`initial_retained_capacity` und
`retention_fraction_per_fresh_continuation` bleiben in S1-OY ausdruecklich
ohne Wert. Eine Implementierung darf deshalb noch keinen gueltigen
Konfigurationsrecord erzeugen.

Die spaeteren Werte muessen einmal vor der ersten Kette gebunden werden und
fuer beide Schritte, XXX, YYY und jede Wiederholung identisch bleiben.

## Modellneutraler Ereignistoken

Der Baselinekern darf genau einen Ereignistyp sehen:

```text
G2_D3_FRESH_CONTINUATION
```

Seine kanonische Payload lautet exakt:

```json
{"event_class_id":"G2_D3_FRESH_CONTINUATION","event_schema_id":"g2_d3_model_neutral_continuation_event","event_schema_version":"s1oy.v1"}
```

```text
event input digest
= dbffc12bef77155c2271d3990ebe1b8ae4d481ce6155bf8716b1f6e19128b30f
```

Beide Updates erhalten byteidentisch denselben Token. Der Token enthaelt
keine Position, Orientierung, Chainrolle, Grenze, Quelle, Dauer, D3-Rolle,
Erwartung oder Ergebnisreferenz.

Die Reihenfolge entsteht ausschliesslich dadurch, dass der private Executor
den Token zweimal nacheinander an denselben getragenen Eigenzustand
uebergibt. Der Kern kann den ersten nicht vom zweiten Token unterscheiden.

## Getrennte Provenienz

Die vier bereits gebundenen Quellgrenzdigests bleiben ausserhalb des
Baselinekerns:

| Kette | erstes Ereignis | zweites Ereignis |
|---|---|---|
| XXX | `c3999c31317b4e79dbc42323904a82fcf0bb1ec4b6089d7dded51415d249f42c` | `6d4a6a51e8c3fb81734598f23edff930f88b5f85e00b79c5d84d1da2b5b0ad9a` |
| YYY | `2b128b63e23ede98397b080515768e012ec7fe87fa1734874de790f35456a34b` | `dc772636ed23e9cf9a904fd9943a7a1bcfacafe08aed9e60a65ac93f3d266d32` |

Sie duerfen nur der aeussere Sequenzvalidator und der abschliessende passive
Beleg lesen. Weder Updatekern noch Checkpointreadout erhalten diese Digests.

## Private Ausfuehrungsanatomie

Eine spaetere private Trace darf innerhalb genau eines Aufrufs tragen:

```text
validated initial baseline state
first updated baseline state
second updated baseline state
```

Sie wird weder serialisiert noch oeffentlich zurueckgegeben. Die logische
Reihenfolge ist fest:

```text
1. Eingaben, Registry und Konfiguration pruefen
2. Quellsequenz als vollstaendig gueltige XXX- oder YYY-Kette bestaetigen
3. initialen Baselinezustand pruefen und CP0 read-only lesen
4. identischen Fortsetzungstoken einmal validieren und Update 1 ausfuehren
5. ersten Folgezustand pruefen und CP1 read-only lesen
6. denselben Fortsetzungstoken validieren und Update 2 ausfuehren
7. zweiten Folgezustand pruefen und CP2 read-only lesen
8. gerichtete Komponenten bilden
9. private Zustandsrecords verwerfen
10. passiven Baselinebeleg bilden
```

Kein Checkpointreadout aktualisiert den Zustand. Bei einem Fehler gibt es
keinen oeffentlichen CP0- oder CP1-Teilwert.

## Vorgesehene Oberflaechen

Eine spaetere Implementierung darf hoechstens bereitstellen:

```text
build_g2_d3_matched_retention_baseline_registry()
-> G2D3MatchedRetentionBaselineRegistry

evaluate_g2_d3_matched_retention_baseline(
    first_boundary_input_digest,
    second_boundary_input_digest,
    initial_state_raw_bytes,
    continuation_event_raw_bytes,
    configuration,
    baseline_registry,
    sequence_registry,
) -> G2D3MatchedRetentionBaselineResult
```

Der einzelne Ereignistoken wird intern zweimal verwendet. Es gibt keine
Liste unterschiedlicher Ereigniswerte, keinen externen Zwischenzustand und
keinen Checkpointwert als Eingabe.

Der spaetere Vergleich bleibt eine getrennte reine Oberflaeche. Erst nachdem
Kandidat und Baseline unabhaengig vollstaendige gueltige Resultate erzeugt
haben, darf ein Comparator beide passiven Belege lesen. Der Baselineexecutor
darf den Kandidatenbeleg nicht importieren oder entgegennehmen.

## Registryform

`G2D3MatchedRetentionBaselineRegistry` ist unveraenderlich und bindet genau:

```text
state_schema_id
state_schema_version
configuration_schema_id
configuration_schema_version
event_schema_id
event_schema_version
baseline_receipt_schema_id
baseline_receipt_schema_version
baseline_class_id
event_class_id
update_rule_id
baseline_statuses
baseline_phases
failure_codes
accepted_composition_contract_digest
accepted_candidate_checkpoint_contract_digest
event_contract_digest
state_anatomy_contract_digest
comparison_contract_digest
baseline_contract_digest
```

Weitere feste Werte:

```text
event_schema_id = g2_d3_model_neutral_continuation_event
event_schema_version = s1oy.v1
baseline_receipt_schema_id = g2_d3_matched_retention_baseline_receipt
baseline_receipt_schema_version = s1oy.v1
baseline_statuses = THREE_CHECKPOINTS_EVALUATED | not_computable
```

## Passiver Baselinebeleg

Der unveraenderliche Beleg darf nur tragen:

```text
receipt schema and baseline class identities
first and second source-boundary provenance digests
initial configuration and state input digests
event token digest
CP0, CP1 and CP2 state-record digests
CP0, CP1 and CP2 scalar values
three directed components
baseline comparison digest
baseline and validation status
completed checks and one failure code
accepted and own contract digests
baseline receipt digest
```

Er enthaelt keine Zustandsrohbytes, private Trace, Kandidatenwerte,
Kandidatenbelege oder verschachtelte Resultatobjekte. Sein Eigendigest wird
ueber die kanonische Payload ohne `baseline_receipt_digest` gebildet. Der
Beleg ist kein Folgeeingang.

## Gebundene Phasen

```text
api_intake
sequence_provenance_validation
configuration_validation
initial_state_validation
cp0_readout
event1_validation
update1
cp1_readout
event2_validation
update2
cp2_readout
component_evaluation
persistence_guard
baseline_receipt
```

Der erste Fehler stoppt alle nachgelagerten Phasen.

## Fail-Closed-Codes

Die Registry bindet exakt:

```text
OY_SEQUENCE_PROVENANCE_INVALID
OY_CONFIGURATION_INVALID
OY_INITIAL_STATE_INVALID
OY_CP0_READOUT_FAILED
OY_EVENT1_INVALID
OY_UPDATE1_FAILED
OY_CP1_READOUT_FAILED
OY_EVENT2_INVALID
OY_UPDATE2_FAILED
OY_CP2_READOUT_FAILED
OY_COMPONENT_EVALUATION_FAILED
```

Pro ungueltigem Resultat ist genau ein Code erlaubt. Baselinewerte,
Komponenten und Vergleichsdigest stehen bei jedem Fehler vollstaendig auf
`not_computable`. Bereits intern erreichte Vorzustaende oder Teilwerte werden
nicht publiziert.

Falsche API-Typen, fremde Registries, Kandidatenbelege oder Zustandsbelege
als fachliche Folgeeingaben scheitern vor einem Resultat.

## Getrennter Vergleichsvertrag

Ein spaeterer Comparator darf nur zwei bereits vollstaendige passive
Resultate annehmen:

```text
candidate checkpoint result
baseline checkpoint result
```

Er prueft zuerst jeweils Schema, Vertragsdigest, Gueltigkeit, Vollstaendigkeit
und Eigendigest. Erst danach darf er korrespondierende Werte, gerichtete
Komponenten und Vergleichsdigests gegenueberstellen.

Der Comparator veraendert weder Kandidat noch Baseline und startet keinen
zweiten Aufruf. Ein ungueltiger Eingang liefert kein Residuum und keine
Schliessungsentscheidung.

## Aussagegrenze

S1-OY bindet nur Anatomie und technische Beleggrenzen. Der Zahlenwert des
Startzustands, die Retentionsfraktion und die Updategleichung bleiben offen.
Es gibt keinen Baselineoperator, keinen Comparator und keinen Lauf.

Der Schritt belegt weder Baselineschliessung noch eine eigene
Substratfunktion oder eine hypothetische MCM-Memory-Funktion.

## Naechster erlaubter Schritt

S1-OZ darf ausschliesslich die minimale stationaere Updategleichung, den
einzigen Startwert, die einzige Retentionsfraktion, exakte
Zwischen-/Finalwerte, numerische Gueltigkeitsbedingungen und die atomare
Schliessungsprognose statisch binden.

S1-OZ darf noch nichts implementieren oder ausfuehren und keine Feld-,
Runtime-, Transfer-, Runner- oder Medienwirkung freigeben.
