# S2-DT: Statischer TSPM-1-Korrekturvertrag

## Auftrag und Grenze

S2-DT schliesst ausschliesslich DS-B01 bis DS-B06 aus dem S2-DS-Preflight.
Der Vertrag ergaenzt exakte Datentraeger, Aufrufflaechen,
Baselinezustandsformen, Owner- und Fehlerregeln, Comparatorprojektionen und
51 einzelne Testrecords.

Es wurden keine Projektmodule importiert, keine Zustands-, Probe-, Test- oder
Vergleichsfunktion aufgerufen, keine Tests ausgefuehrt und keine
Implementierungsdatei geaendert. Alle 56 Vergleichszellen bleiben gesperrt.
Die Bezeichnung bleibt verbindlich `TSPM-1`; `APM-1` erhaelt keine Rolle.

Gebundener S2-DS-Artefaktdigest:
`d0a78f327f2083855d2223408fe9dfc458cf112b19ff2479a0845fae160ddcf8`.

## Gemeinsame kanonische Form

Jeder private Datentraeger verwendet `schema_version` als erstes und seinen
Eigendigest als letztes Feld. Der Eigendigest ist SHA-256 ueber ASCII-kodiertes
kanonisches JSON mit sortierten Schluesseln und kompakten Trennzeichen. Nur
das eigene Digestfeld wird ausgelassen. Tupel werden als JSON-Listen,
verschachtelte Datentraeger mit ihrem vollstaendigen kanonischen Payload
abgebildet. `NaN`, Unendlich, Sets, Maps mit nichttextuellen Schluesseln und
implizite Defaultfelder sind verboten.

## DS-B01: Acht exakte Datentraeger

Die Konstruktorfelder sind in dieser Reihenfolge gebunden:

1. `S2DRConfigRecord`
   - `schema_version`, `candidate_id`, `parent_artifact_digests`,
     `source_blob_digests`, `auditory_carrier_ids`, `visual_carrier_ids`,
     `fast_parameters`, `auditory_ppb_parameters`, `visual_ppb_parameters`,
     `arm_resource_words`, `operation_limits`, `config_digest`.
2. `S2DRFixtureRecord`
   - `schema_version`, `history_id`, `formation_pair_ids`, `probe_specs`,
     `ppb_budget_indices`, `field_clock_id`, `interval_width`,
     `source_id_format`, `formation_frame_id_format`,
     `probe_frame_id_format`, `fixture_digest`.
3. `S2DRArmSpec`
   - `schema_version`, `arm_id`, `operator_id`, `state_schema_id`,
     `resource_words`, `formation_write_limit`, `formation_distance_limit`,
     `probe_distance_limit`, `probe_write_limit`,
     `initial_state_payload`, `initial_state_digest`, `arm_spec_digest`.
4. `S2DRCellPlan`
   - `schema_version`, `cell_id`, `history_id`, `arm_id`, `config_digest`,
     `fixture_digest`, `arm_spec_digest`, `initial_state_digest`,
     `formation_call_count`, `probe_call_count`, `authorization_digest`,
     `cell_plan_digest`.
5. `S2DRBudgetReceipt`
   - `schema_version`, `cell_id`, `cell_plan_digest`, `resource_words_used`,
     `formation_write_counts`, `formation_distance_counts`,
     `probe_distance_counts`, `probe_write_counts`,
     `remaining_resource_words`, `remaining_formation_write_budget`,
     `remaining_formation_distance_budget`,
     `remaining_probe_distance_budget`, `budget_receipt_digest`.
6. `S2DRCellReceipt`
   - `schema_version`, `cell_id`, `cell_plan_digest`, `config_digest`,
     `fixture_digest`, `arm_spec_digest`, `prestate_digest`, `event_digest`,
     `finding_digest`, `budget_receipt_digest`, `poststate_digest`,
     `owner_id`, `owner_terminal_state`, `internal_error_code`,
     `cell_receipt_digest`.
7. `S2DRCellResult`
   - `schema_version`, `cell_id`, `cell_plan_digest`, `prestate_digest`,
     `event_payloads`, `finding_payloads`, `poststate_payload`,
     `poststate_digest`, `budget_receipt`, `cell_receipt`,
     `cell_result_digest`.
8. `S2DRComparisonResult`
   - `schema_version`, `registry_digest`, `ordered_cell_result_digests`,
     `per_arm_predicate_vectors`, `per_arm_error_counts`,
     `strongest_simple_baseline_id`, `r0_exact_equivalence`, `decision`,
     `comparison_result_digest`.

`parent_artifact_digests`, `source_blob_digests`, `arm_resource_words`,
`operation_limits`, `fast_parameters` und beide PPB-Parameterrollen sind
geordnete Tupel aus `(role, value)`. `probe_specs` ist ein Tupel aus
`(after_formation_index, pair_ids)`. Ereignis- und Findingpayloads sind
kanonische Tupel gemaess den Operatorregeln unten. Alle vier Zaehlerrollen
im Budgetreceipt sind Tupel in Aufrufreihenfolge; die drei
`remaining_*_budget`-Rollen sind gleich lange Tupel der jeweiligen
Restgrenzen nach jedem Aufruf.

Bei erfolgreicher Zelle sind alle Digestfelder 64-stelliges SHA-256-Hex,
`owner_terminal_state=COMMITTED` und `internal_error_code=None`. Bei Fehler
entsteht kein `S2DRCellResult`; nur der terminale Ownersnapshot traegt den
internen Fehlercode. Ein Fehlerreceipt wird nicht als Zellreceipt ausgegeben.

## DS-B02: Vollstaendige private Signaturen

Die spaetere Implementierung darf genau diese sechs Aufrufflaechen besitzen:

```python
build_s2dr_registry() -> tuple[
    S2DRConfigRecord,
    tuple[S2DRFixtureRecord, ...],
    tuple[S2DRArmSpec, ...],
    tuple[S2DRCellPlan, ...],
    str,
]

initial_s2dr_arm_state(
    config: S2DRConfigRecord,
    arm: S2DRArmSpec,
) -> object

advance_s2dr_arm(
    config: S2DRConfigRecord,
    fixture: S2DRFixtureRecord,
    arm: S2DRArmSpec,
    prestate: object,
    pair_id: str,
    formation_index: int,
) -> tuple[object, tuple[object, ...], tuple[int, int]]

probe_s2dr_arm(
    config: S2DRConfigRecord,
    fixture: S2DRFixtureRecord,
    arm: S2DRArmSpec,
    state: object,
    pair_id: str,
    probe_index: int,
) -> tuple[tuple[object, ...], int]

validate_s2dr_cell_result(
    config: S2DRConfigRecord,
    fixture: S2DRFixtureRecord,
    arm: S2DRArmSpec,
    plan: S2DRCellPlan,
    result: S2DRCellResult,
) -> S2DRCellResult

compare_s2dr_results(
    config: S2DRConfigRecord,
    plans: tuple[S2DRCellPlan, ...],
    results: tuple[S2DRCellResult, ...],
    registry_digest: str,
) -> S2DRComparisonResult
```

Das Rueckgabetupel von `advance_s2dr_arm` ist
`(poststate, event_payload, (functional_writes, distance_terms))`. Das
Rueckgabetupel der Probe ist `(finding_payload, distance_terms)` und besitzt
keinen Nachzustand. `build_s2dr_registry` berechnet Initialzustandsdigests
nur aus den in den Armspezifikationen gebundenen leeren Payloads; es ruft
keine Zustandsfunktion auf.

Der Zellowner besitzt exakt:

```python
S2DRCellOwner(
    owner_id: str,
    authorization_id: str,
    consumption_id: str,
    cell_plan_digest: str,
    config_digest: str,
    fixture_digest: str,
    arm_spec_digest: str,
    prestate_digest: str,
)

owner.consume_once(
    config: S2DRConfigRecord,
    fixture: S2DRFixtureRecord,
    arm: S2DRArmSpec,
    plan: S2DRCellPlan,
) -> S2DRCellResult

owner.snapshot() -> tuple[
    str, str, str, str, str | None, str | None
]
```

Der Snapshot lautet `(owner_id, consumption_id, status,
cell_plan_digest, internal_error_code, committed_result_digest)`.

### Initialzustandsbindung ohne Zustandsaufruf der Registry

`build_s2dr_registry()` materialisiert fuer jeden Arm genau einen leeren
kanonischen Payload und dessen Digest:

- TSPM1: der vorhandene `TSPM1CompositeState.payload_without_digest()` fuer
  Generation 0. Der Fast-Digest stammt aus drei freien Slots
  `tspm1.fast.slot.000..002`, Count 0 und vier `None`-Quellzeitrollen; beide
  PPB-Digests stammen aus den unten beschriebenen leeren PPB-Payloads.
- B0: `("s2dr.b0.state.v1",)`.
- B1 Direct und Matched: Tupel aus einem leeren auditiven und einem leeren
  visuellen PPB-Payload.
- B2: `("s2dr.b2.state.v1",0,None,None,<neun freie B2-Slots>)`.
- B3: `("s2dr.b3.state.v1",False,(),None,0)`.
- B4: `("s2dr.b4.state.v1",0,None,None,<neun freie B4-Eintraege>)`.
- R0: `("s2dr.r0.state.v1",<normalisierter leerer TSPM1-Payload>)`.

Ein leerer PPB-Payload lautet exakt `(schema_version, bank_id,
config_digest, 0, None, None, slots)`. Jeder freie PPB-Slot lautet
`(slot_id,False,(),None,None)`; Anzahl und Slot-ID folgen der gebundenen
auditiven beziehungsweise visuellen PPB-Konfiguration. Der jeweilige
`initial_state_digest` ist der kanonische Digest dieses Payloads. Die spaetere
Funktion `initial_s2dr_arm_state` muss einen Zustand erzeugen, dessen
normalisierter Payload bitgleich zum ArmSpec-Payload ist; sie bestimmt den
Zellplandigest nicht rueckwirkend.

## DS-B03: Kanonische B2-, B3- und B4-Zustaende

Alle internen Zustandsformen sind unveraenderliche kanonische Tupel und
zaehlen nicht zu den acht Vergleichsdatentraegern.

### B2

Ein B2-Slot lautet
`(slot_id, occupied, values, support, last_selected_step)`. Die IDs sind
`b2.slot.000` bis `b2.slot.008`.

- frei: `occupied=False`, `values=()`, `support=None`,
  `last_selected_step=None`;
- belegt: `occupied=True`, exakt 26 endliche Werte in `[-1,1]`,
  `support` in `{1,2}` und `1 <= last_selected_step <= accepted_count`.

Der B2-Zustand lautet
`(schema_id, accepted_count, auditory_last_end_tick,
visual_last_end_tick, slots)` mit neun Slots. Initial gilt
`accepted_count=0`, beide Zeiten `None`, alle Slots frei. Sonst sind beide
Zeiten positiv und stammen aus derselben Formation.

Vor Match werden alle Slots mit
`formation_index-last_selected_step >= 8` gleichzeitig freigegeben. Match
verlangt auditive und visuelle mittlere L1-Distanz jeweils `<=0.2`; Rang ist
`(max_distance, distance_sum, slot_id)`. Match erzeugt `B2_UPDATED`, mittelt
mit Faktor `0.5`, saettigt Support bei 2 und aktualisiert die Auswahl. Ohne
Match entsteht im kleinsten freien Slot `B2_CREATED`, sonst ersetzt
`B2_REPLACED` den Rang `(last_selected_step, slot_id)`. Das Ereignispayload
lautet `(primary_event, selected_slot_id, expired_slot_ids,
replaced_prestate_slot_digest_or_none, auditory_distance_or_none,
visual_distance_or_none, poststate_digest)`.

Die B2-Probe ignoriert abgelaufene Slots read-only, verwendet denselben
Matchrang und liefert `(arm_id, pair_id, recognized, slot_id_or_none,
auditory_distance_or_none, visual_distance_or_none, context_source,
state_digest)`, wobei `context_source` `B2_JOINT_PROTOTYPE` oder
`NO_COMPLETE_CONTEXT` ist.

### B3

Der B3-Zustand lautet `(schema_id, occupied, values,
last_formation_step, accepted_count)`.

- initial: `False, (), None, 0`;
- belegt: 26 endliche Werte, positiver letzter Schritt und
  `last_formation_step <= accepted_count`.

Die erste Formation setzt den Eingangsvektor und erzeugt `B3_CREATED`.
Jede weitere erzeugt `B3_UPDATED` mit `0.5*alt + 0.5*eingang`. Die Probe ist
nur positiv, wenn `accepted_count-last_formation_step < 8` und beide
Modalitaetsdistanzen `<=0.2` sind. Findingform und Distanzfelder entsprechen
B2; `context_source` ist `B3_REVERBERATION` oder `NO_COMPLETE_CONTEXT`.

### B4

Ein B4-Eintrag lautet `(slot_id, occupied, values, formation_index)`, mit
IDs `b4.slot.000` bis `b4.slot.008`.

- frei: `False, (), None`;
- belegt: 26 endliche Werte und positiver Bildungsindex.

Der B4-Zustand lautet `(schema_id, accepted_count,
auditory_last_end_tick, visual_last_end_tick, entries)`. Belegte Eintraege
stehen lueckenlos vor freien Eintraegen und aufsteigend nach
Bildungsindex. Bei voller Kapazitaet wird Eintrag 0 entfernt, die acht
verbleibenden Payloads werden nach links verschoben und mit ihren festen
Positions-IDs neu gebunden; der neue Eintrag kommt auf Position 8.
Primaerereignisse sind `B4_APPENDED` und `B4_EVICTED_AND_APPENDED`.

Die Probe rangiert alle Treffer nach `(max_distance, distance_sum,
-formation_index, slot_id)` und liefert die gemeinsame Findingform mit
`B4_FIFO` oder `NO_COMPLETE_CONTEXT`. Keine Probe veraendert einen Zustand.

B0 liefert immer `NO_COMPLETE_CONTEXT`. B1 verwendet PPB-1 unveraendert.
TSPM-1 verwendet den unveraenderten privaten Kern. R0 muss dessen
normalisierte Payloads exakt reproduzieren.

## DS-B04: Owner, Autorisierung und Fehler

IDs werden vor jedem Zustandsbezug gebildet:

```text
authorization_id = SHA256(canonical_json([
  "S2DR_AUTH", cell_id, config_digest, fixture_digest,
  arm_spec_digest, initial_state_digest
]))
owner_id       = "s2dr.owner:" + cell_id
consumption_id = "s2dr.consume:" + cell_id
```

Nur `build_s2dr_registry()` darf die Autorisierungsidentitaet aus diesen
statischen Quellen ableiten. Ergebnis-, Ereignis- oder Findingwerte duerfen
nicht eingehen.

Fehlercodes und Prioritaet:

1. Lock nicht sofort verfuegbar: `S2DR_OWNER_BUSY`, Status bleibt wie zuvor.
2. Status nicht `FRESH`: `S2DR_OWNER_TERMINAL`, keine Aenderung.
3. falscher exakter Typ oder Schema: `S2DR_INVALID_TYPE_OR_SCHEMA`.
4. Config-/Fixture-/Arm-/Plan-/Eigendigest falsch:
   `S2DR_DIGEST_OR_SOURCE_MISMATCH`.
5. Owner- oder Autorisierungsrolle falsch:
   `S2DR_AUTHORIZATION_MISMATCH`.
6. Zell-ID, Vorzustand oder Aufrufzahlen falsch:
   `S2DR_FIXTURE_ARM_OR_PRESTATE_MISMATCH`.
7. Ressourcen- oder Operationsgrenze verletzt:
   `S2DR_RESOURCE_OR_OPERATION_LIMIT_EXCEEDED`.
8. Ereignis-, Finding-, Budget-, R0- oder Ergebnisrelation falsch:
   `S2DR_RESULT_RELATION_MISMATCH`.
9. fehlende Atomaritaet oder Teilresultat:
   `S2DR_ATOMIC_RESULT_REQUIRED`.

Nach bestandenem Lock und `FRESH` wechselt der Owner lokal auf `BUSY`.
Jeder Fehler 3 bis 9 setzt terminal `FAILED`, bindet genau den ersten
internen Fehlercode und gibt nach aussen nur `S2DR_ATTEMPT_FAILED` aus.
Es gibt weder Zellresultat noch Receipt oder Nachzustand. Ein Folgeaufruf
liefert `S2DR_OWNER_TERMINAL`. Nur vollstaendige relationale Validierung setzt
atomar `COMMITTED` und bindet den Ergebnisdigest.

## DS-B05: Projektion der 56 Zellen auf P1 bis P5

Der Comparator verlangt genau 56 einzigartige Resultate in der
Registryreihenfolge H1 bis H7, darin je Arm in der gebundenen Armreihenfolge.
Fehlend, doppelt, fremd, ungeordnet oder digestinkonsistent ergibt
`METHOD_INVALID` ohne Teilvergleich.

Jedes Finding wird normalisiert zu
`(history_id, arm_id, checkpoint, pair_id, recognized, context_source,
slot_or_entry_id, auditory_distance, visual_distance, state_digest)`.

Je Arm gelten:

- `P1_EARLY`: H1/AX ist nach Schritt 1 positiv. Fuer TSPM-1 muss die Quelle
  `FAST_ASSOCIATIVE_CONTEXT` sein.
- `P2_LATE`: H3/AX ist nach Schritt 12 positiv. Fuer TSPM-1 muessen
  `fast_recognized=False` und `slow_recognized=True` gelten. Fuer B2/B3/B4
  genuegt der eigene positive Kontext; B0 kann nicht bestehen. B1 verwendet
  seinen PPB-Kontext.
- `P3_CONFLICT`: H4 erkennt AX, AY und BX. TSPM-1 muss AX langsam sowie AY
  und BX ausschliesslich schnell erkennen; sein langsamer AX-Payloaddigest
  muss dem H2-AX-Payloaddigest nach Schritt 4 entsprechen. Fuer einfache
  Baselines muessen alle drei gebundenen Paare positiv sein und der
  normalisierte AX-Payload muss dem H2-AX-Payload nach Schritt 4 entsprechen.
- `P4_EVICTION`: H5 erkennt AX und P4. TSPM-1 meldet keinen AX-Fast-Slot,
  einen P4-Fast-Slot und einen positiven langsamen AX-Kontext. B2/B4 muessen
  ihre gebundene Ersatz-/FIFO-Regel einhalten; andere Baselines muessen beide
  Proben innerhalb ihres Zustandsvertrags positiv liefern.
- `P5_ERROR`: H7 liefert exakt
  `[true,true,false,false,false]`. TSPM-1 darf in H6 keine langsame Bindung
  fuer D1, D3 oder D8 und in H4 keine langsame Bindung fuer AY oder BX
  besitzen. Jeder Arm muss null ungebundene Paarakzeptanzen, null
  Probe-Schreibungen und null Ledgerverletzungen haben.

Ein Arm besteht nur bei `[P1,P2,P3,P4,P5]=[true,true,true,true,true]`.
`per_arm_error_counts` lautet geordnet
`(false_accepts, false_consolidations, partial_conflict_errors,
eviction_errors, budget_errors)`.

Die staerkste einfache Baseline wird aus B0 bis B4 lexikographisch gewaehlt:
mehr wahre Pflichtpraedikate, weniger Summe der Fehler, kleinere
Capture-Latenz, weniger funktionale Writes, Arm-ID. `B1_DIRECT` und
`B1_BUDGET_MATCHED` bleiben getrennte Arme. R0 nimmt nicht an dieser Wahl
teil und muss vor jeder Funktionsentscheidung alle TSPM-1-Normalformen exakt
reproduzieren.

Entscheidungsprioritaet:

1. Quellen-, Matrix-, Budget- oder R0-Fehler: `METHOD_INVALID`;
2. TSPM-1-Operator-/Atomaritaetsfehler oder fehlendes TSPM-Praedikat:
   `TSPM1_FUNCTION_NOT_VALID`;
3. mindestens eine einfache Baseline besteht alle P1 bis P5:
   `FUNCTION_VALID_SIMPLE_BASELINE_EXPLAINS`;
4. sonst:
   `TSPM1_TWO_TIMESCALE_ENGINEERING_ADVANTAGE_OVER_SIMPLE_BASELINES`.

## DS-B06: 51 einzelne Testrecords

Jeder spaetere Testrecord bindet `(test_id, group, fixture_or_mutation,
call_surface, expected_result, expected_owner_state,
expected_operator_call_budget)`. Die folgende Tabelle ist vollstaendig:

| IDs | gebundener Inhalt |
| --- | --- |
| T01 | Eltern- und Quellblobdigests exakt |
| T02 | genau zwei Dateien, keine Exporte oder Runner |
| T03 | Kandidat exakt TSPM1, keine APM1-Rolle |
| T04 | Dimensionen exakt 8/18/26 |
| T05 | Konfiguration und Traegerreihenfolge exakt |
| T06 | Registry 7*8=56, frisch, geordnet, nicht konsumiert |
| T07-T13 | je ein exakter Fixturetest fuer H1 bis H7 |
| T14-T21 | je ein Operator-/Initialzustandstest fuer TSPM1, B0, B1 Direct, B1 Matched, B2, B3, B4, R0 |
| T22 | gemeinsames Maximum 269/2152 |
| T23 | acht Armwerte exakt |
| T24 | Bildungsschreibgrenze 293 |
| T25 | Bildungs-/Probedistanzgrenze 234 |
| T26 | Probe schreibt null funktionale Woerter |
| T27-T34 | je ein Konstruktor-/Digesttest fuer die acht Datentraeger |
| T35 | P1-bis-P5-Projektion aller gebundenen Zellrollen |
| T36 | METHOD_INVALID besitzt Vorrang |
| T37 | TSPM1_FUNCTION_NOT_VALID besitzt Vorrang vor Baselinewertung |
| T38 | einfache Baseline und lexikographischer Tie-Break |
| T39 | technischer Vorteil nur bei TSPM-Pass, Baseline-Fail und R0-Gleichheit |
| T40-T51 | die zwoelf Fail-Closed-Mutationen in S2-DR-Reihenfolge |

T01 bis T39 verwenden keinen Cell-Owner-Consume und haben
`expected_operator_call_budget=0`; reine B2/B3/B4-Mikrooperatorpruefungen in
T18 bis T20 verwenden direkt genau einen Operatoraufruf, aber keinen Owner
und keine Matrixzelle.

T40 bis T45 laufen ueber einen frischen synthetischen Owner. Sie erwarten
`S2DR_ATTEMPT_FAILED`, terminal `FAILED`, den unten gebundenen internen Code,
kein Resultat und danach `S2DR_OWNER_TERMINAL`. T46 verwirft doppelte Plaene
strukturell vor der Auswertung; T47 verwirft eine stale Probe direkt vor
einem Operatoraufruf. T48 bis T50 verwenden den Resultatvalidator, T51 den
Comparator. In T46 bis T51 wird kein Owner erzeugt. Alle zwoelf Faelle haben
Operatorbudget 0 und koennen deshalb keine Zelle committen.

Die exakte Zuordnung T40 bis T51 lautet:

```text
T40 WRONG_CONFIG_DIGEST
T41 WRONG_FIXTURE_DIGEST
T42 WRONG_ARM_DIGEST
T43 WRONG_PRESTATE_DIGEST
T44 WRONG_AUTHORIZATION
T45 FOREIGN_CELL_ID
T46 DUPLICATE_CELL_ID
T47 STALE_PROBE
T48 SWAPPED_BUDGET_RECEIPT
T49 RESOURCE_LIMIT_EXCEEDED
T50 OPERATION_LIMIT_EXCEEDED
T51 RESULT_OR_R0_RELATION_MISMATCH
```

Die exakten Negativerwartungen lauten:

| ID | Pruefflaeche | erwarteter Befund | Owner |
| --- | --- | --- | --- |
| T40-T42 | `owner.consume_once` | intern `S2DR_DIGEST_OR_SOURCE_MISMATCH`, aussen `S2DR_ATTEMPT_FAILED` | `FAILED` |
| T43 | `owner.consume_once` | intern `S2DR_FIXTURE_ARM_OR_PRESTATE_MISMATCH`, aussen `S2DR_ATTEMPT_FAILED` | `FAILED` |
| T44 | `owner.consume_once` | intern `S2DR_AUTHORIZATION_MISMATCH`, aussen `S2DR_ATTEMPT_FAILED` | `FAILED` |
| T45 | `owner.consume_once` | intern `S2DR_FIXTURE_ARM_OR_PRESTATE_MISMATCH`, aussen `S2DR_ATTEMPT_FAILED` | `FAILED` |
| T46 | `compare_s2dr_results` | `S2DR_RESULT_RELATION_MISMATCH`, kein Vergleichsresultat | `NOT_CREATED` |
| T47 | `probe_s2dr_arm` | `S2DR_FIXTURE_ARM_OR_PRESTATE_MISMATCH`, kein Finding | `NOT_CREATED` |
| T48 | `validate_s2dr_cell_result` | `S2DR_RESULT_RELATION_MISMATCH`, kein Resultat | `NOT_CREATED` |
| T49-T50 | `validate_s2dr_cell_result` | `S2DR_RESOURCE_OR_OPERATION_LIMIT_EXCEEDED`, kein Resultat | `NOT_CREATED` |
| T51 | `compare_s2dr_results` | vollstaendiges atomisches Vergleichsresultat mit `METHOD_INVALID` wegen R0-Abweichung | `NOT_CREATED` |

Damit gilt: strukturell unvollstaendige oder doppelte Eingaben erzeugen kein
Vergleichsresultat. Vollstaendige, digestkonsistente 56er-Eingaben mit
methodischer R0-Abweichung erzeugen genau ein atomar validiertes
`METHOD_INVALID`-Resultat.

Kein Test darf `compare_s2dr_results` mit 56 realen Zellresultaten aufrufen.
T35 bis T39 verwenden ausschliesslich synthetische, digestkonsistente
Comparatorrecords. Damit bleibt die 56-Zellen-Ausfuehrung gesperrt.

## Blockerschluss

| S2-DS-Blocker | S2-DT-Bindung |
| --- | --- |
| DS-B01 | acht Feldlisten und eine kanonische Digestregel |
| DS-B02 | sechs Modulsignaturen plus Ownerkonstruktor, Consume und Snapshot |
| DS-B03 | vollstaendige B2/B3/B4-Tupelzustaende, Ereignisse und Findings |
| DS-B04 | statische Autorisierungsquelle, Fehlercodes und Prioritaet |
| DS-B05 | zellgenaue Normalform, P1-P5, Tie- und Entscheidungsreihenfolge |
| DS-B06 | T01 bis T51 mit Erwartung, Ownerstatus und Aufrufbudget |

## Entscheidung

`PASS_TSPM1_SIX_STATIC_COMPARISON_MATERIALIZATION_BINDINGS_CORRECTED`

S2-DT schliesst die sechs Luecken auf Vertragsniveau. Es belegt noch nicht,
dass der korrigierte Vertrag den Wiederholungspreflight besteht.

## Naechster Schritt

S2-DS muss nach separater Freigabe erneut ausschliesslich statisch pruefen,
ob DS-B01 bis DS-B06 vollstaendig, widerspruchsfrei und ohne neue
Implementierungsentscheidung geschlossen sind. Implementierung, Tests und
alle Vergleichszellen bleiben bis dahin gesperrt.
