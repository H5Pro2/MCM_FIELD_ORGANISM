# S1-NR G2/D3 Validatorimplementierung und fehlgeschlagene Einmalabnahme

## Status

S1-NR implementiert ausschliesslich die drei in S1-NQ gebundenen Dateien.
Bestehender KFS-1-, DTS-1-, Feld-, Runner- und Mediencode blieb unveraendert.

Entscheidung:

```text
G2_D3_VALIDATOR_IMPLEMENTED_BUT_NOT_ACCEPTED
```

## Implementierter Umfang

- reiner unveraenderlicher D3-Registrytyp;
- reiner Fail-Closed-Einzelrecordvalidator;
- reiner F1-Paarvalidator;
- drei positive Primaerfixtures und zwei einzeln gueltige Kontrollrecords;
- 18 gebundene Einzelmutationen und sechs gebundene Paarmutationen;
- fokussierte `unittest`-Abnahme ohne Feld-, I/O-, Medien- oder Netzwerkpfad.

Der Produktionsvalidator importiert neben der Standardbibliothek nur
`canonical_json_bytes` und `sha256_hex` aus dem unveraenderten KFS-1-Validator.

## Einmalige Ausfuehrung

Der in S1-NQ einmal erlaubte Befehl wurde genau einmal ausgefuehrt:

```text
python -m unittest tests.test_g2_d3_s1nr_schema_validator
```

Ergebnis:

```text
Ran 10 tests in 0.021s
FAILED (failures=1)
```

Der einzige gemeldete Defekt betraf `D3_I_MISSING`. Beim absichtlich
fehlenden Feld `candidate_class_id` lieferte die Implementierung neben
`D3_MISSING_OR_UNKNOWN_FIELD` den abgeleiteten Folgefehler
`D3_CLASS_ID_MISMATCH`. Erwartet war ausschliesslich der Strukturfehler.

Die uebrigen Subtests meldeten keinen weiteren Fehler. Daraus wird dennoch
kein bestandener Gesamtbefund abgeleitet.

## Korrektur nach dem Lauf

Die Klassenidentitaetspruefung wurde danach lokal so abhaengigkeitsgebunden,
dass sie nur bei vorhandenem `candidate_class_id` ausgefuehrt wird. Vertrag,
Fixturebytes und erwartete Fehlercodes wurden nicht veraendert. Wegen des
ausgeschoepften Einmalbudgets wurde die korrigierte Fassung nicht erneut
ausgefuehrt.

SHA-256 der gegenwaertigen, nach dem Lauf korrigierten Dateien:

```text
g2_d3_schema_validator.py                  666f38ef49ddfa1538a301f43f265d60e7e0f1f48834e3df0653551d03f18c0d
g2_d3_s1nr_fixtures.py                     76351b57709f2af5a249a76a48a8cd08a7ac51f5b79855e592f69087fd80724d
test_g2_d3_s1nr_schema_validator.py        244aecbe65b057f22080503390e52fc8cdb20e9a4b713c093ca8e990bb8dcb87
```

## Aussagegrenze

S1-NR belegt keinen akzeptierten Validator. Es gibt weiterhin keine
G2-Admissibilitaetsfunktion, Dynamik, Feldwirkung, Lernfunktion oder einen
Befund zur hypothetischen MCM-Memory.

## Naechster erlaubter Schritt

S1-NS darf ausschliesslich einen neuen endlichen Wiederabnahmevertrag fuer
die unveraenderte korrigierte Drei-Dateien-Fassung binden. Vor dieser Bindung
darf kein weiterer Testlauf stattfinden. Admissibilitaet, Transfer, Bildung
und Feldmechanik bleiben gesperrt.
