# S2-DS Wiederholung nach S2-DV: Statischer Vergleichspreflight

## Auftrag und Grenze

Dieser S2-DS-Preflight prueft ausschliesslich statisch die letzte
Budgetkorrektur aus S2-DV und ihre Vereinbarkeit mit den bereits gebundenen
S2-DT- und S2-DU-Vertraegen.

Gebundene Artefakte:

- S2-DT: `7b38682c9de21ba02076c4c563280876cb725f11c9cd439d7aa91369f13d8bd1`
- S2-DU: `afefcb8593d6ba74fb98261852e5a18553a5e45e82030f37242179d45f73328c`
- S2-DS nach S2-DU:
  `efb4757c88ae7a4da0d0edf82f9e5002749b4e203ceb516ce8c54e3dbd964949`
- S2-DV: `d5469f35988098020ef5ca413e641f927621dd0adb69b89914b2cbd49e9d7f18`

Es wurden keine Implementierungs- oder Testdateien geaendert, keine
Projektmodule importiert, keine Zustands-, Test- oder Vergleichsfunktion
aufgerufen und keine der 56 Vergleichszellen materialisiert oder
ausgefuehrt.

## Grenzwertquellen

Bestanden.

Der erweiterte `S2DRBudgetReceipt` traegt die Ressourcen-, Formation- und
Probegrenzen als explizite Konstruktorwerte. Fuer jede Rolle besteht genau
eine Herkunftsrelation zum validierten `S2DRArmSpec`. Die Tupelschluessel
stammen aus dem validierten Zellplan und der zugehoerigen Fixture.

Der Konstruktor kann damit die Restidentitaeten ohne globale Registry,
impliziten Default oder externe Ersatz-ID bilden. Die spaetere relationale
Abnahme vergleicht jeden eingebetteten Grenzwert erneut mit demselben
Armvertrag. Fremde oder passend zurechtgelegte Grenzwerte koennen daher
keine Ueberschreitung verdecken.

## T50

Bestanden.

T50 ist vollstaendig und eindeutig gebunden:

```text
arm_id: TSPM1
history_id: H1
operation_role: formation_write_counts
formation_index: 1
bound: 293
used: 294
remaining: -1
```

Der Abgleich mit der gebundenen Fixture bestaetigt, dass H1 genau einen
Formationsschritt besitzt. Der Index `1` ist deshalb vorhanden und eindeutig.
Der Grenzwert `293` entspricht
`max_functional_word_writes_per_formation`; der Verbrauch `294` ist exakt
eine Einheit groesser. Alle anderen Rollen bleiben quellgueltig und innerhalb
ihres Budgets.

## Alleiniger Ablehnungsort

Bestanden.

Der Budgetbelegkonstruktor prueft nur Feldform, Schluessel, Typen,
Eigendigest und die mit seinen eingebetteten Grenzen berechenbaren
Restidentitaeten. Er lehnt weder `used > bound` noch negative Restwerte als
Budgetueberschreitung ab.

Nur

```text
validate_s2dr_cell_result(
  ConfigRecord, FixtureRecord, ArmSpec, CellPlan, CellResult
)
```

verfuegt gleichzeitig ueber Beleg, validierten Armvertrag, Zellplan und
Fixture. Nur diese Funktion darf eine quellgueltige Ueberschreitung mit
`S2DR_RESOURCE_OR_OPERATION_LIMIT_EXCEEDED` ablehnen.

Strukturfehler bleiben Konstruktorfehler. Fremde Grenzwerte oder falsche
Restarithmetik sind relationale Identitaetsfehler. Sie sind keine alternativen
Interpretationen einer Budgetueberschreitung und erzeugen
`S2DR_RESULT_RELATION_MISMATCH` im selben Zellvalidator.

Es existiert keine zweite Budgetentscheidung, keine Mutationsnaht, keine
globale Grenzquelle und kein alternativer Ablehnungsort.

## Gesamtabgleich der Korrekturkette

Alle zuvor offenen Materialisierungsblocker sind geschlossen:

- Fast-, Slow-, Prototyp- und AV-Payloadnachweise sind verlustfrei
  projizierbar;
- T43 und T45 besitzen eindeutige Owner-, Zell-, Plan- und
  Autorisierungswege;
- T49 und T50 besitzen konstruktiv erreichbare, digestkonsistente
  Negativbelege und genau einen relationalen Ablehnungsort.

S2-DT, S2-DU und S2-DV lassen sich ohne weitere fachliche oder technische
Auswahlentscheidung in den vorgesehenen zwei privaten Dateien
materialisieren. Die 56 Vergleichszellen bleiben weiterhin eine getrennt
freizugebende Ausfuehrung.

## Entscheidung

`PASS_TSPM1_PRIVATE_COMPARISON_IMPLEMENTATION_MATERIALIZABLE`

Der S2-DS-Wiederholungs-Preflight ist bestanden. Die private
Vergleichsimplementierung ist damit freigabefaehig. Dieser Audit selbst
implementiert noch nichts und fuehrt weder Tests noch Vergleichszellen aus.

## Naechster Schritt

S2-DW kann die bereits gebundene private TSPM-1-Vergleichsimplementierung in
genau zwei Dateien materialisieren und die 51 gebundenen synthetischen
Vertragstests definieren. Testausfuehrung und die 56 Vergleichszellen bleiben
bis zu einer separaten Freigabe gesperrt.
