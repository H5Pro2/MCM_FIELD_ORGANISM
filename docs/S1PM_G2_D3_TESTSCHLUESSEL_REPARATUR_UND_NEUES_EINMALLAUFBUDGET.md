# S1-PM G2/D3 Testschluessel-Reparatur und neues Einmallaufbudget

## Status und Zweck

S1-PM behandelt ausschliesslich den im einmaligen S1-PL-Verbundlauf
aufgetretenen Testinfrastrukturfehler. Es korrigiert noch keine Datei und
fuehrt keinen Test aus.

Entscheidung:

```text
S1PL_SINGLE_TEST_KEY_DEFECT_ISOLATED_EXACT_REPAIR_AND_ONE_NEW_63_TEST_BUDGET_BOUND
```

## Gebundener Ausgangsbefund

Die statische S1-PL-Vorpruefung bestaetigte:

- exakt fuenf neue S1-PL-Dateien;
- 13 von 13 unveraenderte Grundlagendigests;
- gueltige Syntax der fuenf Dateien;
- exakt 43 Regressionstestmethoden und 20 neue Testmethoden.

Der danach einmalig ausgefuehrte Verbundlauf meldete:

```text
Ran 63 tests in 0.127s
FAILED (errors=1)
```

62 Methoden waren erfolgreich. Test 19 brach mit
`KeyError: 'contract_digest'` ab. S1-PL ist deshalb nicht als bestanden
abgenommen. Es gab keinen zweiten Lauf.

## Statische Ursachenbindung

Das Comparator-Receipt deklariert in
`mcm_field_organism/g2_d3_binding_offer_comparison.py` ausschliesslich:

```text
comparison_contract_digest
```

Der Receiptproduzent befuellt genau dieselbe Rolle. Test 19 verwendet dagegen
in seiner Liste verschiedener Digestrollen einmalig:

```text
contract_digest
```

Dieser nicht vorhandene Schluessel wird vor der beabsichtigten
Verschiedenheitspruefung gelesen und verursacht den beobachteten `KeyError`.
Im gesamten Testmodul existiert genau ein Vorkommen dieses falschen
Schluessels.

Diese Ursachenbindung ist eine statische Schnittstellenfeststellung. Sie
wertet die noch nicht vollstaendig abgenommene Implementierung nicht als
fehlerfrei und ist keine Aussage ueber Kandidatenwirkung.

## Eingefrorene S1-PL-Dateien

Vor und nach der spaeteren Reparatur muessen unveraendert gelten:

```text
mcm_field_organism/g2_d3_local_binding_offer.py
= 4a1093055f082af944345c39c928db92539876cecffd07fb080a93d8f6b7e6db
mcm_field_organism/g2_d3_binding_offer_baseline_adapter.py
= b65efcb27741ed516676841cc0993cb3f9f4b80bc66871bdd99588ecfa4c9c56
mcm_field_organism/g2_d3_binding_offer_comparison.py
= 9951415cf6e3ba680b16cb4ebe5ba3e1b5154ed0c7eab3a5b7fb7de07f7a5681
tests/g2_d3_s1pl_binding_offer_fixtures.py
= 8b3ce54b18d36f7ea5c788df95fe53f778af2e1b3454c1aab80e4324c688f58d
```

Die 13 in S1-PK gebundenen Grundlagendigests bleiben ebenfalls unveraendert
und muessen vor dem neuen Lauf erneut vollstaendig geprueft werden.

## Exakte Reparaturgrenze

S1-PN darf genau eine bestehende Datei aendern:

```text
tests/test_g2_d3_s1pl_binding_offer_comparison.py
```

Ihr Ausgangsdigest ist:

```text
7049a6b65533a6f567ac9c8b446224c56cec07f6f55c27aef291670e3824968e
```

Erlaubt ist exakt ein textueller Austausch in Test 19:

```text
"contract_digest"
->
"comparison_contract_digest"
```

Der vorab berechnete Digest der reparierten Datei muss danach exakt sein:

```text
3a98acc5876353dda3f19b5283e3b0ec98a138b08fa6706eb68ecef97343d8d8
```

Keine weitere Zeile, kein Produktionsmodul, kein Fixture und kein
Testumfang darf geaendert werden.

## Statische Vorpruefung fuer S1-PN

Vor einer Testausfuehrung muessen gemeinsam gelten:

1. alle 13 S1-PK-Grundlagendigests stimmen;
2. die vier vorstehend eingefrorenen S1-PL-Dateien stimmen;
3. die reparierte Testdatei besitzt den gebundenen Nachher-Digest;
4. die vier Testsuiten enthalten weiterhin exakt 63 Testmethoden;
5. `git diff --check` meldet keinen Fehler;
6. ausser der einen Testdatei bestehen vor der Ergebnisdokumentation keine
   weiteren Aenderungen.

Bei jeder Abweichung endet S1-PN vor dem Lauf fail-closed.

## Neues einmaliges Testbudget

Nach erfolgreicher statischer Vorpruefung darf S1-PN genau einmal ausfuehren:

```powershell
python -m unittest `
  tests.test_g2_d3_s1nr_schema_validator `
  tests.test_g2_d3_s1pg_free_blocked_intervention_validator `
  tests.test_g2_d3_s1pb_retention_baseline_closure `
  tests.test_g2_d3_s1pl_binding_offer_comparison
```

Erwartet werden exakt 63 erfolgreiche Testmethoden. Subtests veraendern die
Methodenzahl nicht. Ein zweiter Lauf ist nicht freigegeben.

## Ergebnis- und Abbruchregel

Nur `Ran 63 tests` zusammen mit `OK` darf die technische S1-PL-Abnahme
schliessen. Jeder Fehler, Fehlschlag, eine andere Methodenzahl oder eine
Digestabweichung stoppt S1-PN ohne Reparatur, Wiederholung oder
Uminterpretation.

Nach dem Lauf duerfen nur `AKTUELLER_FORSCHUNGSWEG.md`, `README.md` und
`docs/AKTUELLE_TECHNISCHE_PROJEKTGRENZE.md` um das tatsaechliche Ergebnis
ergaenzt werden.

## Aussagegrenze

Ein spaeter positives Ergebnis wuerde ausschliesslich die implementierte,
konstruktiv vorgegebene lokale Ressourcenregel, den statischen Adapter und
den passiven Vergleich technisch abnehmen. Es waere kein Nachweis einer
selbst gebildeten Substratgeschichte und kein Nachweis hypothetischer
MCM-Memory. Feld-, Runtime-, O3- und Medienintegration bleiben gesperrt.

## Naechster erlaubter Schritt

S1-PN darf nur den exakt gebundenen Testschluessel austauschen, alle
eingefrorenen Digests statisch pruefen und anschliessend den einen neuen
63-Test-Lauf ausfuehren. Danach wird ausschliesslich das tatsaechliche
Ergebnis dokumentiert.
