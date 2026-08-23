# S1-XM: Statischer Ergebnis-, Receipt- und Grenzwertaudit

## Auftrag und Grenze

S1-XM prueft den vorhandenen S1-XL-Ergebnisdatensatz, die gebundenen Quellen
und die numerische Grenzwertdefinition. Kein Projektmodul wurde importiert,
keine Funktion aufgerufen und keine Matrixzelle erneut ausgefuehrt.

## Formales Ergebnis bleibt bestehen

Das S1-XL-Receipt wird nicht umgeschrieben:

```text
method_valid:                  true
candidate_pass_cell_count:     9 von 10
technical_function_decision:   TECHNICAL_MEMORY_FUNCTION_FAIL
final_decision:                TECHNICAL_MEMORY_FUNCTION_FAIL
matrix_receipt_digest:         c854345e708175ef4473b1044d3ab1cd40f48c39c0676789523fd8a52297e2ce
```

S1-XM aendert weder Erwartung noch Toleranz nach dem Ergebnis.

## Grenzwertbefund

Die einzige abweichende Kandidatenzelle ist
`s1xa.auditory.ppb1.boundary-positive`. Der Vertrag setzt gleichzeitig:

```text
auditive Schwelle:             0.2
boundary-positive Reiz:        0.2
erwartete Erkennung:           true
berechnete L1-Distanz:         0.20000000000000004
Vergleich:                     distance <= threshold
```

Die beobachtete Distanz liegt um `2.7755575615628914e-17` ueber der
Schwelle. Damit ist die vorregistrierte positive Grenzerwartung nicht
numerisch konsistent mit der implementierten Metrik. Das ist ein Fehler der
synthetischen Grenzwertbindung, nicht eine kandidatenexklusive Gegenwirkung.

Der formale Funktions-Fail bleibt trotzdem erhalten. Er darf lediglich nicht
als Evidenz interpretiert werden, dass die PPB-1-Mechanik selbst an ihrer
technischen Funktion scheiterte.

## Baselinebefund

Kandidat und alle zustandsbehafteten Baselines verwenden dieselbe
normalisierte L1-Distanz und denselben Schwellenvergleich. Im beobachteten
60-Zellen-Ergebnis erklaeren vier vollstaendige Baselines das gesamte
Kandidatenverhalten:

```text
no-memory:             false
replay:                true
static-prototype:      true
moving-state:          true
last-vector-distance:  true
```

Damit verbleibt unabhaengig vom Grenzwertfehler keine beobachtete
MCM-spezifische Differenz. Eine korrigierte Wiederholung von S1-XL waere
methodisch nicht zulaessig und wuerde die bereits festgestellte
Baseline-Reduzierbarkeit nicht aufheben.

## Entscheidung

`PASS_BOUNDARY_EXPECTATION_INCONSISTENT_FORMAL_FAIL_PRESERVED_CANDIDATE_CAUSE_NOT_ESTABLISHED_BASELINE_REDUCIBLE`

PPB-1 bleibt als transparente Engineeringkomponente verfuegbar. Der
registrierte Vergleichszweig ist jedoch geschlossen und liefert keinen
Nachweis einer MCM-spezifischen Memory-Mechanik.

## Naechster Schritt

S1-XN darf ausschliesslich einen statischen Engineering- und
Korrekturvertrag erstellen. Er soll die numerische Grenzwertfixture fuer
zukuenftige technische Tests robust definieren und festlegen, welche
PPB-1-Bausteine als reduzible Engineeringinfrastruktur erhalten bleiben.
Keine Runtimeaenderung, kein Matrixlauf und keine neue Forschungsbehauptung
sind Teil dieses Schritts.
