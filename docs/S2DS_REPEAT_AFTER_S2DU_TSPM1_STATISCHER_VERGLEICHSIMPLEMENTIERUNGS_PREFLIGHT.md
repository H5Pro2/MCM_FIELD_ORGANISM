# S2-DS Wiederholung nach S2-DU: Statischer Vergleichspreflight

## Auftrag und Grenze

Dieser S2-DS-Wiederholungs-Preflight prueft ausschliesslich statisch, ob die
drei Korrekturen aus S2-DU vollstaendig, widerspruchsfrei und ohne weitere
Implementierungsentscheidung materialisierbar sind.

Gebundene Artefakte:

- S2-DT: `7b38682c9de21ba02076c4c563280876cb725f11c9cd439d7aa91369f13d8bd1`
- vorheriger S2-DS-Wiederholungs-Preflight:
  `e032d0a5a4c813d2874a80d329f98942a8e3e67da93181709aa99a3dd441018e`
- S2-DU: `afefcb8593d6ba74fb98261852e5a18553a5e45e82030f37242179d45f73328c`

Es wurden keine Implementierungs- oder Testdateien geaendert, keine
Projektmodule importiert, keine Zustands- oder Vergleichsfunktion aufgerufen,
keine Tests ausgefuehrt und keine der 56 Vergleichszellen materialisiert oder
ausgefuehrt.

## Bestandene Korrekturen

### Fast-, Slow- und Prototypnachweise

Die erweiterte Normalform erhaelt die fuer P2 und P3 erforderliche Evidenz:

- Fast-Treffer, Slot, Slotdigest und beide Fast-Distanzen;
- getrennte auditive und visuelle Slow-Status- und Findingrollen;
- getrennte ausgewaehlte Slow-Slots, Prototypdigests und Distanzen;
- einen aus den ausgewaehlten Traegerwerten gebildeten, von Zustands- und
  Findingmetadaten unabhaengigen AV-Payloaddigest.

Die Quellen sind an validierte TSPM-1- und S1WU-Findings sowie an den
jeweiligen Fast-Slot oder PPB-1-Prototyp gebunden. Fehlende Rollen bleiben
`null` und werden nicht aus `context_source` erraten. P2 und P3 sind damit
aus einem `S2DRCellResult` eindeutig berechenbar. DS-RB01 ist geschlossen.

### T43 und T45

Owner, Zelle, Plan und Autorisierung besitzen nun literale Gleichheitsketten.
Die Autorisierung ist aus Zell-, Konfigurations-, Fixture-, Arm- und
Initialzustandsidentitaet kanonisch gebildet.

- T43 veraendert nur den Owner-Vorzustandsdigest. Die
  Zell-/Autorisierungsgruppe bleibt gueltig; der Fall erreicht eindeutig
  `S2DR_FIXTURE_ARM_OR_PRESTATE_MISMATCH`.
- T45 uebergibt einem fuer Plan P gebundenen Owner einen intern
  selbstkonsistenten fremden Plan Q. Der Fall stoppt eindeutig an der
  Owner-Zell-/Autorisierungsgruppe mit
  `S2DR_OWNER_AUTHORIZATION_MISMATCH`.

Beide Wege enden ohne Ergebnis, mit null PPB-1-Aufrufen und terminalem Owner.
DS-RB02 ist geschlossen.

## Verbleibender Materialisierungsblocker

### DS2-RB01: Budgetkonstruktion und T50 sind noch nicht voll bestimmt

S2-DU legt den alleinigen fachlichen Ablehnungsort fuer Grenzueberschreitungen
korrekt auf `validate_s2dr_cell_result`. Zwei seiner Materialisierungsregeln
sind jedoch noch nicht mit den vorhandenen Datentraegern vereinbar.

#### Konstruktor kennt den gebundenen Grenzwert nicht

Der `S2DRBudgetReceipt` besitzt verwendete Zaehler und Restwerte, aber weder
Arm-ID noch Ressourcen- oder Operationsmaxima. Sein Konstruktor erhaelt laut
gebundener Signatur auch keinen `S2DRArmSpec` und keinen
`S2DRConfigRecord`. Trotzdem verlangt S2-DU im Konstruktor:

```text
remaining == bound - used
```

`bound` ist an dieser Stelle nicht verfuegbar. Die Identitaet kann deshalb
nicht im Belegkonstruktor geprueft werden. Eine verdeckte Registrysuche oder
globale Konfiguration waere eine neue, nicht gebundene Quelle.

Die eindeutige Korrektur muss lauten:

- Der Konstruktor validiert ausschliesslich Form, Typ, nichtnegative
  Verbrauchszaehler, ganzzahlige Restwerte und Eigendigest.
- `validate_s2dr_cell_result` erhaelt `ArmSpec` und prueft dort erstmals
  sowohl `remaining == bound - used` als auch `used <= bound` und
  `remaining >= 0`.

Damit bleibt der relationale Validator der einzige Ablehnungsort.

#### T50 benennt keinen bestimmten Zaehler

T50 erhoeht laut S2-DU "genau einen" Operationszaehler, legt aber nicht fest,
welche Operationsrolle, welcher Tupelschluessel und welcher Arm betroffen
sind. Die vier moeglichen Rollen besitzen unterschiedliche Formen und
Grenzen. Ausserdem besitzt der Beleg fuer `probe_write_counts` keinen eigenen
`remaining_probe_write_budget`-Datentraeger.

T50 muss daher einen bereits vorhandenen Restbudgettyp literal waehlen. Die
kleinste widerspruchsfreie Bindung ist:

```text
arm_id: TSPM1
history_id: H1
counter: formation_write_counts
counter_key: formation_index 0
used: formation_write_limit + 1
remaining_formation_write_budget: -1
all other resource and operation roles: valid and within bound
```

Budgetreceipt, Zellreceipt und Zellergebnis muessen danach kanonisch neu
digestiert werden. Erst der relationale Validator darf diesen Beleg mit
`S2DR_RESOURCE_OR_OPERATION_LIMIT_EXCEEDED` ablehnen.

## Entscheidung

`BLOCK_TSPM1_PRIVATE_COMPARISON_IMPLEMENTATION_ONE_BUDGET_MATERIALIZATION_BINDING_OPEN`

Der S2-DS-Wiederholungs-Preflight besteht nicht. Die private
Vergleichsimplementierung, Testimplementierung, Testausfuehrung und alle 56
Vergleichszellen bleiben gesperrt.

## Naechster Schritt

S2-DV darf nach separater Freigabe ausschliesslich DS2-RB01 schliessen:

- alle grenzabhaengigen Rechenidentitaeten aus dem Belegkonstruktor in
  `validate_s2dr_cell_result` verschieben;
- T50 literal auf den TSPM-1/H1-`formation_write_counts`-Zaehler am
  `formation_index 0` binden.

Danach ist S2-DS erneut rein statisch durchzufuehren. Noch keine
Implementierung, Testausfuehrung oder Vergleichszelle.
