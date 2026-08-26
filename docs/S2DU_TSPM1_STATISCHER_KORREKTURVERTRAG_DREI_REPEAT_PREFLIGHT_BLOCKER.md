# S2-DU: Statischer Korrekturvertrag fuer drei Restblocker

## Auftrag und Grenze

S2-DU schliesst ausschliesslich die drei im S2-DS-Wiederholungs-Preflight
festgestellten Materialisierungsblocker. Dieser Vertrag ergaenzt und
korrigiert S2-DT nur an den nachfolgend ausdruecklich bezeichneten Stellen.
Alle anderen S2-DT-Bindungen bleiben unveraendert.

Gebundene Elternartefakte:

- S2-DT: `7b38682c9de21ba02076c4c563280876cb725f11c9cd439d7aa91369f13d8bd1`
- S2-DS Wiederholung:
  `e032d0a5a4c813d2874a80d329f98942a8e3e67da93181709aa99a3dd441018e`

Es werden keine Implementierungs- oder Testdateien angelegt oder geaendert,
keine Projektmodule importiert, keine Zustandsfunktion aufgerufen, keine
Tests ausgefuehrt und keine Vergleichszelle materialisiert oder ausgefuehrt.

## DS-RB01: Verlustfreie Comparatornormalform

### Vollstaendige Findingprojektion

Jedes normalisierte Finding besitzt genau diese geordneten Rollen:

```text
history_id, arm_id, checkpoint, pair_id, recognized, context_source,
fast_recognized, fast_slot_id, fast_slot_digest,
auditory_fast_distance, visual_fast_distance,
auditory_slow_status, visual_slow_status,
auditory_slow_finding_digest, visual_slow_finding_digest,
auditory_selected_slot_id, visual_selected_slot_id,
auditory_selected_prototype_digest, visual_selected_prototype_digest,
auditory_slow_distance, visual_slow_distance,
selected_av_payload_digest, observed_state_digest
```

Die Projektion ist verlustfrei fuer die von P1 bis P5 benoetigte Evidenz.
Nicht verfuegbare Rollen sind `null`; sie duerfen nicht durch Ersatzwerte
oder aus `context_source` abgeleitete Annahmen aufgefuellt werden.

### Quellenregeln

- Fuer TSPM-1 stammen Fast-Rollen direkt aus dem validierten
  `TSPM1ReadOnlyFinding`.
- Slow-Status und Slow-Findingdigest stammen getrennt fuer auditiv und
  visuell aus demselben validierten TSPM-1-Finding.
- Slot-ID, Distanz und `selected_prototype_digest` einer Slow-Rolle werden
  aus genau dem durch ihren Findingdigest gebundenen validierten
  `S1WUReadOnlyPerceptualFinding` uebernommen.
- Ein Slow-Prototypnachweis ist nur bei `SLOW_RECOGNIZED` vollstaendig. Bei
  `SLOW_NOT_RECOGNIZED` oder `SLOW_UNAVAILABLE` bleiben ausgewaehlte
  Slot-, Prototyp- und Distanzrollen `null`.
- Baselinearme fuellen nur Rollen, die ihr gebundener Operator tatsaechlich
  erzeugt. Fehlende Fast- oder Slow-Ebenen bleiben `null`.

### Payloadidentitaet

`selected_av_payload_digest` ist kein Zustands-, Slot- oder Findingdigest.
Er wird ausschliesslich aus den normalisierten ausgewaehlten auditiven und
visuellen Traegerwerten gebildet:

```text
SHA256(canonical_json([
  "S2DR_SELECTED_AV_PAYLOAD_V1",
  normalized_selected_auditory_values,
  normalized_selected_visual_values
]))
```

Bei `FAST_ASSOCIATIVE_CONTEXT` stammen beide Wertfolgen aus demselben
validierten Fast-Slot. Bei `SLOW_PPB1_CONTEXT` stammen sie aus den beiden
durch die Slow-Findings ausgewaehlten PPB-1-Prototypen. Liegt kein
vollstaendiger Kontext vor, ist der Wert `null`.

Damit wird die AX-Payloadidentitaet zwischen H2 und H4 anhand des
Payloadinhalts und nicht anhand eines geschichtsabhaengigen Zustandsdigests
verglichen.

### P2- und P3-Projektion

P2 ist fuer TSPM-1 genau dann positiv, wenn das gebundene H3/AX-Finding
`recognized=True`, `fast_recognized=False`, beide Slow-Statuswerte
`SLOW_RECOGNIZED` und einen vollstaendigen Slow-Prototypnachweis besitzt.

P3 ist fuer TSPM-1 genau dann positiv, wenn:

- H4/AX erkannt wird, beide Slow-Rollen erkannt sind und der Fast-Treffer
  falsch ist;
- H4/AY und H4/BX erkannt werden, ihr Fast-Treffer wahr ist und nicht beide
  Slow-Rollen gleichzeitig erkannt sind;
- der nichtleere `selected_av_payload_digest` fuer AX in H2 und H4 bitgleich
  ist.

Kein Gesamtzustandsdigest darf die letzte Relation ersetzen.

## DS-RB02: Owner-, Zell- und Autorisierungsidentitaet

### Kanonische Relationen

Der Ownerkonstruktor wird fuer die spaetere private Implementierung wie folgt
gebunden:

```text
(owner_id, cell_id, authorization_digest, consumption_id,
 cell_plan_digest, config_digest, fixture_digest, arm_spec_digest,
 prestate_digest)
```

Vor jedem Verbrauch gelten gleichzeitig:

```text
owner.cell_id == plan.cell_id
owner.authorization_digest == plan.authorization_digest
owner.cell_plan_digest == plan.cell_plan_digest
owner.config_digest == plan.config_digest == config.config_digest
owner.fixture_digest == plan.fixture_digest == fixture.fixture_digest
owner.arm_spec_digest == plan.arm_spec_digest == arm_spec.arm_spec_digest
```

`plan.authorization_digest` bleibt exakt:

```text
SHA256(canonical_json([
  "S2DR_AUTH", plan.cell_id, plan.config_digest, plan.fixture_digest,
  plan.arm_spec_digest, plan.initial_state_digest
]))
```

Eine extern gewaehlte ID darf keine dieser Relationen ersetzen. Der Owner
prueft Ownerterminalitaet, danach die vollstaendige Zell-/Autorisierungsgruppe
und erst danach Fixture-, Arm- und Vorzustandsrelationen.

### T43

T43 verwendet einen unveraenderten gueltigen Plan und einen dazu passenden
Owner. Ausschliesslich `owner.prestate_digest` wird vor Konstruktion auf
einen anderen syntaktisch gueltigen Digest gesetzt. Alle Zell-, Plan- und
Autorisierungsrelationen bleiben gueltig. Der Verbrauch erreicht deshalb
deterministisch die Vorzustandspruefung und endet mit:

```text
internal: S2DR_FIXTURE_ARM_OR_PRESTATE_MISMATCH
outer: S2DR_ATTEMPT_FAILED
owner: FAILED
result: none
PPB-1 calls: 0
```

### T45

T45 verwendet einen gueltigen Owner fuer Plan P und uebergibt beim
Verbrauch einen separat kanonisch digestierten Plan Q mit fremder
`cell_id`. Q ist intern selbstkonsistent; sein Autorisierungsdigest und
Plandigest wurden aus Q neu gebildet. Config, Fixture und Arm bleiben
ansonsten identisch. Die erste abweichende Gruppe ist damit zwingend die
Owner-Zell-/Autorisierungsgruppe. Der Befund lautet:

```text
internal: S2DR_OWNER_AUTHORIZATION_MISMATCH
outer: S2DR_ATTEMPT_FAILED
owner: FAILED
result: none
PPB-1 calls: 0
```

T45 wird damit gegenueber der alten S2-DT-Erwartung praezisiert. Eine
fremde Zellidentitaet darf nicht erst als Fixturefehler weiterlaufen.

## DS-RB03: Ablehnungsort fuer T49 und T50

### Zwei Validierungsebenen

Der Konstruktor von `S2DRBudgetReceipt` prueft ausschliesslich:

- exakte Feldtypen und geordnete Schluessel;
- nichtnegative verwendete Ressourcen- und Aufrufzaehler;
- ganzzahlige Restbudgetwerte, wobei negative Werte strukturell zulaessig
  sind;
- arithmetische Identitaet `remaining == bound - used` fuer jede Rolle;
- Zell-, Plan- und Eigendigestform.

Der Konstruktor vergleicht weder `used` mit einem Maximum noch lehnt er ein
negatives Restbudget ab. Es existiert keine Mutationsnaht zur Umgehung des
Konstruktors.

Nur `validate_s2dr_cell_result` nimmt den strukturell und digestkonsistenten
Beleg relational gegen `S2DRArmSpec` und `S2DRConfigRecord` ab. Sobald ein
Ressourcen- oder Operationswert sein gebundenes Maximum ueberschreitet oder
ein Restbudget negativ ist, endet die Validierung mit
`S2DR_RESOURCE_OR_OPERATION_LIMIT_EXCEEDED` und ohne Ergebnis.

### T49

T49 bildet einen vollstaendig neu digestierten Beleg mit
`resource_words_used = arm_resource_words + 1` und
`remaining_resource_words = -1`. Alle Operationszaehler bleiben innerhalb
ihres Budgets. Budgetbeleg, Zellreceipt und Zellergebnis werden mit den
geaenderten Werten kanonisch neu digestiert. Der Konstruktor akzeptiert die
strukturell gueltige Form; ausschliesslich `validate_s2dr_cell_result` lehnt
sie relational ab.

### T50

T50 erhoeht genau einen fuer den Arm gueltigen Operationszaehler um eins
ueber sein gebundenes Maximum und setzt nur dessen Restbudget auf `-1`.
Ressourcen und alle anderen Operationsrollen bleiben innerhalb des Budgets.
Alle umschliessenden Digests werden kanonisch neu gebildet. Wieder lehnt
ausschliesslich `validate_s2dr_cell_result` relational ab.

Fuer T49 und T50 gilt:

```text
error: S2DR_RESOURCE_OR_OPERATION_LIMIT_EXCEEDED
result: none
owner: NOT_CREATED
PPB-1 calls: 0
```

## Geschlossene Restblocker

- `DS-RB01`: geschlossen durch verlustfreie Finding- und Payloadprojektion.
- `DS-RB02`: geschlossen durch kanonische Zell-/Autorisierungsrelation und
  eindeutige T43-/T45-Konstruktion.
- `DS-RB03`: geschlossen durch getrennte strukturelle Konstruktor- und
  relationale Grenzvalidierung.

Diese Aussage ist eine Vertragskorrektur, kein bestandener
Materialisierbarkeitsaudit.

## Entscheidung und naechster Schritt

`S2DU_STATIC_CORRECTION_CONTRACT_COMPLETE_REPEAT_PREFLIGHT_REQUIRED`

S2-DS muss erneut ausschliesslich statisch pruefen, ob S2-DT zusammen mit
diesem Vertrag vollstaendig und widerspruchsfrei materialisierbar ist. Bis zu
einem bestandenen Audit bleiben private Implementierung, Testimplementierung,
Testausfuehrung und alle 56 Vergleichszellen gesperrt.
