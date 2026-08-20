# S1-PK G2/D3 Bindungsangebot: Implementierungs-, Adapter-, Comparator-, Fehlermutations- und Testbudgetvertrag

## Status und Umfang

S1-PK bindet ausschliesslich die spaetere begrenzte Umsetzung von S1-PJ:
Dateien, APIs, Abhaengigkeiten, atomare Outputs, Fehlerrollen,
Fehlermutationen und genau einen kombinierten Testlauf. S1-PK implementiert
nichts und fuehrt nichts aus. Feld-, Runtime-, Runner-, O3- und Medienpfad
bleiben gesperrt.

Entscheidung:

```text
G2_D3_BINDING_OFFER_IMPLEMENTATION_ADAPTER_COMPARATOR_AND_SINGLE_TEST_BUDGET_BOUND
```

## Gebundene Dateigrenze

S1-PL darf genau fuenf neue Dateien anlegen:

| Datei | Aufgabe |
|---|---|
| `mcm_field_organism/g2_d3_local_binding_offer.py` | atomarer Kandidatenoperator fuer einen Vorzustand und ein Angebot |
| `mcm_field_organism/g2_d3_binding_offer_baseline_adapter.py` | reine Projektion auf den vorhandenen Fortsetzungstoken |
| `mcm_field_organism/g2_d3_binding_offer_comparison.py` | passiver Comparator fertiger Kandidaten- und Baselineergebnisse |
| `tests/g2_d3_s1pl_binding_offer_fixtures.py` | kanonische Gueltig- und Fehlermutationsfixtures |
| `tests/test_g2_d3_s1pl_binding_offer_comparison.py` | fokussierte technische Abnahme |

Bestehende Dateien bleiben unveraendert. Nach dem einzigen Testlauf duerfen
nur `AKTUELLER_FORSCHUNGSWEG.md`, `README.md` und
`docs/AKTUELLE_TECHNISCHE_PROJEKTGRENZE.md` um das tatsaechliche Ergebnis
ergaenzt werden.

## Eingefrorene Grundlage

Vor und nach S1-PL muessen exakt gelten:

```text
mcm_field_organism/kfs1_schema_validator.py
= c0355f6b98f129f2ce3743a409850b2d777f1c4b6ecc02d0971c2a523843162e
mcm_field_organism/g2_d3_schema_validator.py
= 666f38ef49ddfa1538a301f43f265d60e7e0f1f48834e3df0653551d03f18c0d
mcm_field_organism/g2_d3_free_blocked_intervention_validator.py
= d360b8e489dc0fce9440de5d7e496ac9bb10810986d4bd3f6f5c9f4686bffcb6
mcm_field_organism/g2_d3_matched_retention_baseline.py
= 2c9ea49d2fffc386ce5247db2000c9e48554a3eb5e52ce3f949647ef8b25fde8
mcm_field_organism/g2_d3_two_step_composition.py
= b364ae91ff91d45db32edc2081a9782869c46a82495e3cedcf8ffc21d555991f
mcm_field_organism/g2_d3_checkpoint_baseline_comparison.py
= 5f308842c40af6d1afe5c5905be20eedf6fce211c45741d7f5931aa2f604f240
mcm_field_organism/g2_d3_two_step_o3_checkpoints.py
= effc8812845273bacc52eef23a0ba20feefc743b3b630c44f04488e860a10011
tests/g2_d3_s1nr_fixtures.py
= 76351b57709f2af5a249a76a48a8cd08a7ac51f5b79855e592f69087fd80724d
tests/g2_d3_s1pg_free_blocked_intervention_fixtures.py
= 2c8c899812f2be20fdc20a8517c808912af2beb969bd705cc88ed3788083a8b0
tests/g2_d3_s1pb_retention_baseline_fixtures.py
= d02bc49ceb858bcd436586d4ac66fcb08154985e45e04bacd325cc602aaf1fec
tests/test_g2_d3_s1nr_schema_validator.py
= 244aecbe65b057f22080503390e52fc8cdb20e9a4b713c093ca8e990bb8dcb87
tests/test_g2_d3_s1pg_free_blocked_intervention_validator.py
= 129258d61cf6f5f3c1e4632bec56f5d2acdf0ba6d9e187f1584893877f24c24c
tests/test_g2_d3_s1pb_retention_baseline_closure.py
= 44ac066f168c931741a7a337e55ead78a46cd525fbac548f100fc8cfdd9cca5a
```

Die 10 S1-NR-, 15 S1-PG- und 18 S1-PB-Testmethoden bilden 43 unveraenderte
Regressionen im Einmallauf.

## Import- und Verantwortungsgrenzen

### Kandidatenoperator

`g2_d3_local_binding_offer.py` darf nur Standardbibliothek,
`validate_g2_d3_anatomy_record` und kanonische Digesthelfer importieren. Er
darf weder Intervention, Baseline, Comparator, O3, Feld noch Runtime
importieren.

Der Operator nimmt einen D3-Vorrecord, den S1-PI-Payload und den
S1-PJ-Gleichungsvertrag entgegen. Er erzeugt hoechstens einen vollstaendig
validierten Nachrecord, `commit_amount` und einen passiven Receipt. Bei jedem
Fehler entstehen weder Nachrecordbytes noch Teilcommit.

### Baselineadapter

`g2_d3_binding_offer_baseline_adapter.py` validiert nur S1-PI-Payload und
S1-PJ-Adaptervertrag. Sein einziger gueltiger Sachoutput sind die gebundenen
Retentionsereignisbytes mit Digest
`dbffc12bef77155c2271d3990ebe1b8ae4d481ce6155bf8716b1f6e19128b30f`.
Er startet keinen Baselineoperator. Arm-, Kandidatenzustands- und
O3-Information sind verboten.

### Comparator

`g2_d3_binding_offer_comparison.py` nimmt nur zwei fertige
Kandidatenresultate, zwei fertige
`G2D3MatchedRetentionBaselineResult`-Objekte und die kanonische
S1-PJ-Gesamtprognose entgegen. Er startet keinen Operator oder Adapter.

Fuer jede Baseline verwendet er ausschliesslich:

```text
baseline_first_step_response = cp0 - cp1
```

`cp2`, `delta_cp2_cp1` und `delta_cp2_cp0` duerfen weder Messung noch
Kontrast oder Entscheidung beeinflussen.

## Oeffentliche APIs

```text
build_g2_d3_local_binding_offer_registry()
apply_g2_d3_local_binding_offer(
    prestate_raw_bytes,
    event_payload_raw_bytes,
    equation_contract_raw_bytes,
    binding_registry,
    anatomy_registry,
) -> G2D3LocalBindingOfferResult
```

```text
build_g2_d3_binding_offer_baseline_adapter_registry()
adapt_g2_d3_binding_offer_to_retention_event(
    event_payload_raw_bytes,
    adapter_contract_raw_bytes,
    adapter_registry,
) -> G2D3BindingOfferBaselineAdapterResult
```

```text
build_g2_d3_binding_offer_comparison_registry()
compare_g2_d3_binding_offer_results(
    free_available_candidate_result,
    blocked_held_candidate_result,
    free_comparison_baseline_result,
    blocked_comparison_baseline_result,
    prediction_raw_bytes,
    comparison_registry,
) -> G2D3BindingOfferComparisonResult
```

Byteeingaben muessen exakt `bytes`, Registries und Resultate exakt ihre
gebundenen Typen sein. Falsche API-Typen scheitern vor einem Receipt.

## Kandidatenresultat

`G2D3LocalBindingOfferResult` enthaelt exakt:

```text
poststate_raw_bytes: bytes | not_computable
commit_amount: float | not_computable
receipt: G2D3LocalBindingOfferReceipt
```

Nur ein erneut durch den bestehenden D3-Einzelvalidator bestaetigter
Nachrecord darf publiziert werden. Exakt erwartet werden:

```text
FREE_AVAILABLE -> commit 0.375
post input digest = 9195946005008bf034a8625d04ddaf58826254f8a8fbd11f3b3e3433a9483d9f

BLOCKED_HELD -> commit 0.25
post input digest = 1f7d2b8fb9a5d7afebe1fbd60adaa915b3f46c5efe85d98c37d02389cfb64227
```

Der Receipt bindet Eingangs-, Vertrags-, Vorzustands-, Nachzustands- und
Receiptdigests, Commitwert, Phasen, Status und Fehlerrollen.

## Adapter- und Vergleichsresultat

`G2D3BindingOfferBaselineAdapterResult` enthaelt nur
`retention_event_raw_bytes: bytes | not_computable` und einen Receipt. Bei
Fehlern gibt es keine Outputbytes.

Der passive Gesamtvergleich bindet exakt:

```text
candidate_commits = (0.375, 0.25) | not_computable
candidate_binding_contrast = 0.125 | not_computable
baseline_first_step_responses = (0.25, 0.25) | not_computable
baseline_replica_contrast = 0.0 | not_computable
decision = CANDIDATE_DIFFERENT_BASELINE_EQUAL | INVALID_OR_INCOMPLETE
receipt
```

Beide Baselines muessen denselben `OP_CHAIN_XXX`-Ursprung und dieselben
Eingangsbytes besitzen. Absolute Kandidaten- und Baselineantworten werden
nicht als gleiche Messskala interpretiert; klassifiziert werden nur die
gerichteten inneren Kontraste.

## Maschinenlesbare Fehlerrollen

S1-PL bindet exakt 18 Codes:

```text
PL_PRESTATE_INVALID
PL_EVENT_PAYLOAD_INVALID
PL_EQUATION_CONTRACT_INVALID
PL_EVENT_STATE_IDENTITY_MISMATCH
PL_NONFINITE_OR_NEGATIVE_AMOUNT
PL_POSTSTATE_INVALID
PL_ATOMIC_COMMIT_FAILED
PL_ADAPTER_CONTRACT_INVALID
PL_ADAPTER_SOURCE_INVALID
PL_ADAPTER_FORBIDDEN_INPUT
PL_ADAPTER_OUTPUT_MISMATCH
PL_CANDIDATE_RESULT_INVALID
PL_BASELINE_RESULT_INVALID
PL_BASELINE_PROVENANCE_MISMATCH
PL_CP2_EXCLUSION_FAILED
PL_CANDIDATE_CONTRAST_MISMATCH
PL_BASELINE_CONTRAST_MISMATCH
PL_PREDICTION_OR_DECISION_MISMATCH
```

Fehlerrollen sind sortiert, eindeutig und deterministisch. Kein Fehler
erzeugt reparierte Sachwerte.

## Genau 18 kontrollierte Fehlermutationen

Je eine isolierte Mutation gilt fuer:

1. ungueltigen D3-Vorzustandsdigest;
2. negative Ressource im Vorzustand;
3. geaenderten Ereignispayloaddigest;
4. unbekannte Ereignisschemaversion;
5. abweichende Kante im Ereignis;
6. geaenderten Gleichungsvertragsdigest;
7. abweichenden Angebotswert im Gleichungsvertrag;
8. simulierten ungueltigen Nachrecord vor atomarer Publikation;
9. geaenderten Adaptervertragsdigest;
10. falschen Adapter-Quellpayloaddigest;
11. Armkennung im Adapterinput;
12. abweichenden Retentionsereignisoutput;
13. unvollstaendiges Kandidatenresultat;
14. ungueltiges Baselineergebnis;
15. verschiedene Baselineketten zwischen Replikaten;
16. manipulierten `cp1`-Wert;
17. versuchte `cp2`-Einbeziehung;
18. geaenderten Prognosedigest oder Entscheidungswert.

Alle nicht betroffenen Digests werden je Mutation neu berechnet. Jede
Mutation muss genau einen vorregistrierten Code ausloesen; sonst wird vor dem
Lauf abgebrochen.

## Genau 20 neue Testmethoden

Die S1-PL-Abnahme prueft exakt:

1. Registries, Vertragsdigests und Oberflaechen;
2. kanonische positive Fixturebytes und Digests;
3. positiven `FREE_AVAILABLE`-Kandidatenlauf;
4. positiven `BLOCKED_HELD`-Kandidatenlauf;
5. Erhaltung beider Nachrecords;
6. exakte Nachrecord- und Receiptdigests;
7. positiven Adapteroutput;
8. Abwesenheit verbotener Adapterinformation;
9. zwei identische vorhandene Baselineergebnisse;
10. positiven passiven Gesamtvergleich;
11. strikten Ausschluss von `cp2`;
12. Kandidatenfehlermutationen mit Einzelcodes;
13. Adapterfehlermutationen mit Einzelcodes;
14. Comparatorfehlermutationen mit Einzelcodes;
15. Vollstaendigkeit aller 18 Mutationen;
16. deterministische sortierte Fehlerrollen;
17. unveraenderte Eingaben und Registries;
18. falsche API-Typen ohne Teilreceipt;
19. getrennte reproduzierbare Digestrollen;
20. isolierte Imports ohne O3-, Feld-, Runtime-, Runner- oder Medienpfad.

Subtests aendern die Testmethodenzahl nicht.

## Einmaliges S1-PL-Testbudget

Nach Implementierung und statischer Vorpruefung darf genau einmal laufen:

```powershell
python -m unittest `
  tests.test_g2_d3_s1nr_schema_validator `
  tests.test_g2_d3_s1pg_free_blocked_intervention_validator `
  tests.test_g2_d3_s1pb_retention_baseline_closure `
  tests.test_g2_d3_s1pl_binding_offer_comparison
```

Erwartet werden exakt 63 Testmethoden: 43 unveraenderte Regressionen und 20
neue S1-PL-Tests. Kein zweiter Test-, Kandidaten-, Feld- oder Runtimelauf ist
freigegeben.

## Abbruchbedingungen

S1-PL ist vor dem Lauf abzubrechen, wenn eine eingefrorene Datei abweicht,
mehr oder andere Dateien erforderlich werden, Comparator oder Adapter einen
Operator starten muessten, `cp2` nicht sicher ausgeschlossen werden kann,
eine Mutation mehr als einen Code erzeugt oder ein Teilcommit beziehungsweise
eine Reparatur erforderlich wird.

## Aussagegrenze

S1-PK ist nur ein Implementierungs- und Abnahmevertrag. Ein spaeterer
positiver Lauf bestaetigt zunaechst die konstruktiv gebundene lokale
Ressourcenregel, nicht eine selbst gebildete Substratgeschichte. Die
hypothetische MCM-Memory bleibt eine Entwicklungsrichtung.

## Naechster erlaubter Schritt

S1-PL darf ausschliesslich die fuenf neuen Dateien implementieren, die
eingefrorenen Digests vor und nach der Aenderung pruefen und den einen
63-Test-Lauf ausfuehren. Anschliessend darf nur das tatsaechliche Ergebnis
dokumentiert werden. Feldintegration und weitere Funktionsaussagen bleiben
gesperrt.
