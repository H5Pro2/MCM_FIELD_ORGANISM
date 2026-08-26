# S2-DV: Statischer Korrekturvertrag fuer die Budgetbindung

## Auftrag und Grenze

S2-DV schliesst ausschliesslich den im S2-DS-Preflight nach S2-DU
verbliebenen Blocker `DS2-RB01`. Der Vertrag ergaenzt S2-DT und S2-DU nur
fuer Budgetbeleg, T49 und T50.

Gebundene Elternartefakte:

- S2-DT: `7b38682c9de21ba02076c4c563280876cb725f11c9cd439d7aa91369f13d8bd1`
- S2-DU: `afefcb8593d6ba74fb98261852e5a18553a5e45e82030f37242179d45f73328c`
- S2-DS nach S2-DU:
  `efb4757c88ae7a4da0d0edf82f9e5002749b4e203ceb516ce8c54e3dbd964949`

Es werden keine Implementierungs- oder Testdateien geaendert, keine
Projektmodule importiert, keine Zustandsfunktion oder Vergleichsfunktion
aufgerufen, keine Tests ausgefuehrt und keine Vergleichszelle materialisiert
oder ausgefuehrt.

## Erweiterter Budgetbeleg

`S2DRBudgetReceipt` besitzt kuenftig genau diese geordneten Felder:

```text
schema_version
cell_id
cell_plan_digest
resource_words_bound
resource_words_used
formation_write_bounds
formation_write_counts
formation_distance_bounds
formation_distance_counts
probe_distance_bounds
probe_distance_counts
probe_write_bounds
probe_write_counts
remaining_resource_words
remaining_formation_write_budget
remaining_formation_distance_budget
remaining_probe_distance_budget
remaining_probe_write_budget
budget_receipt_digest
```

Die vier `*_bounds`, vier `*_counts` und vier zugehoerigen Restbudgetrollen
sind geordnete Tupel. Formationsrollen verwenden aufsteigende, einsbasierte
`formation_index`-Schluessel. Proberollen verwenden aufsteigende,
einsbasierte `probe_index`-Schluessel innerhalb der bereits gebundenen
Fixture-Reihenfolge. Schluesselmenge und Tupellaenge muessen je Rolle
bitgleich sein.

## Herkunft der Grenzwerte

Der Belegkonstruktor erhaelt alle Grenzwerte als verbindliche Werte. Ihre
einzige zulaessige Quelle ist der fuer dieselbe Zelle validierte
`S2DRArmSpec`:

```text
resource_words_bound == arm_spec.resource_words
formation_write_bounds[i] == arm_spec.formation_write_limit
formation_distance_bounds[i] == arm_spec.formation_distance_limit
probe_distance_bounds[j] == arm_spec.probe_distance_limit
probe_write_bounds[j] == arm_spec.probe_write_limit
```

Die Tupelschluessel `i` und `j` stammen ausschliesslich aus dem validierten
`S2DRCellPlan` und der gebundenen `S2DRFixtureRecord`. Es gibt keine globale
Registryabfrage, keinen impliziten Default und keine extern ersetzbare
Grenzquelle.

## Konstruktorvalidierung

Der Konstruktor prueft:

- exakte Feldtypen, Tupelschluessel und Tupellaengen;
- nichtnegative ganzzahlige Grenzwerte und Verbrauchszaehler;
- ganzzahlige Restwerte, wobei negative Werte strukturell zulaessig sind;
- fuer Ressourcen `remaining_resource_words == resource_words_bound -
  resource_words_used`;
- fuer jeden Operationsschluessel `remaining[k] == bound[k] - count[k]`;
- Zell-, Plan- und Eigendigestform.

Der Konstruktor prueft ausdruecklich nicht, ob der eingetragene Grenzwert dem
Armvertrag entspricht. Er lehnt auch weder `used > bound` noch negative
Restwerte ab. Dadurch koennen T49 und T50 als strukturell und rechnerisch
konsistente Negativbelege ohne Mutationsnaht konstruiert werden.

## Alleiniger relationaler Ablehnungsort

Nur `validate_s2dr_cell_result(ConfigRecord, FixtureRecord, ArmSpec,
CellPlan, CellResult)` darf den Budgetbeleg gegen seine Quellen und Maxima
abnehmen. Die Pruefreihenfolge innerhalb der Budgetgruppe ist:

1. Belegzelle und Plandigest stimmen mit `CellPlan` ueberein.
2. Grenzwerte und Tupelschluessel stimmen vollstaendig mit `ArmSpec`,
   `CellPlan` und `FixtureRecord` ueberein.
3. Alle Restidentitaeten sind korrekt.
4. Kein Verbrauch ueberschreitet seinen Grenzwert und kein Restwert ist
   negativ.

Jede Abweichung in Schritt 2 oder 3 ist ein
`S2DR_RESULT_RELATION_MISMATCH`. Ausschliesslich eine bei korrekten
Quellgrenzen rechnerisch belegte Ueberschreitung in Schritt 4 erzeugt
`S2DR_RESOURCE_OR_OPERATION_LIMIT_EXCEEDED`. In beiden Faellen entsteht kein
Zellergebnis.

Damit ist `validate_s2dr_cell_result` der einzige relationale Ablehnungsort
fuer Budgetueberschreitungen.

## T49: Ressourcenueberschreitung

T49 bleibt an eine ansonsten gueltige TSPM-1-Zelle gebunden. Der Beleg setzt:

```text
resource_words_bound = arm_spec.resource_words
resource_words_used = resource_words_bound + 1
remaining_resource_words = -1
```

Alle Operationsgrenzen, Zaehler und Restwerte bleiben gueltig und innerhalb
ihres Budgets. Budgetbeleg, Zellreceipt und Zellergebnis werden kanonisch neu
digestiert. Der Konstruktor akzeptiert den strukturell und rechnerisch
konsistenten Beleg. Nur `validate_s2dr_cell_result` verwirft ihn mit
`S2DR_RESOURCE_OR_OPERATION_LIMIT_EXCEEDED`.

## T50: Konkreter Operationszaehler

T50 ist literal an folgende Rolle gebunden:

```text
arm_id = TSPM1
history_id = H1
operation_role = formation_write_counts
formation_index = 1
formation_write_bounds[1] = arm_spec.formation_write_limit = 293
formation_write_counts[1] = 294
remaining_formation_write_budget[1] = -1
```

H1 besitzt genau einen Formationsschritt; `formation_index = 1` ist daher
vorhanden und eindeutig. Alle anderen Grenzen, Zaehler und Restwerte bleiben
quellgueltig und innerhalb ihres Budgets. Budgetbeleg, Zellreceipt und
Zellergebnis werden kanonisch neu digestiert.

Der Konstruktor akzeptiert die strukturell und rechnerisch konsistente Form.
Nur `validate_s2dr_cell_result` verwirft sie mit
`S2DR_RESOURCE_OR_OPERATION_LIMIT_EXCEEDED`.

Fuer T49 und T50 gilt weiterhin:

```text
result: none
owner: NOT_CREATED
PPB-1 calls: 0
```

## Geschlossener Blocker

`DS2-RB01` ist auf Vertragsniveau geschlossen:

- Grenzwerte liegen im Budgetbeleg als verbindliche Konstruktorwerte vor;
- ihre Herkunft und spaetere Relation zum Armvertrag sind eindeutig;
- T50 benennt genau einen vorhandenen und zaehlbaren Operationszaehler;
- Budgetueberschreitungen stoppen ausschliesslich im relationalen Validator.

Dies ist noch kein bestandener Materialisierbarkeitsaudit.

## Entscheidung und naechster Schritt

`S2DV_STATIC_BUDGET_CORRECTION_CONTRACT_COMPLETE_REPEAT_PREFLIGHT_REQUIRED`

S2-DS muss erneut ausschliesslich statisch pruefen, ob die gesamte private
Vergleichsimplementierung nach S2-DT, S2-DU und S2-DV vollstaendig und
widerspruchsfrei materialisierbar ist. Bis zu einem bestandenen Audit bleiben
Implementierung, Tests und alle 56 Vergleichszellen gesperrt.
