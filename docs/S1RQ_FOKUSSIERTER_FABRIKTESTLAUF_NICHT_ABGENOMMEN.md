# S1-RQ: Fokussierter Fabriktestlauf nicht abgenommen

## Status und Umfang

S1-RQ fuehrte ausschliesslich die 16 Tests aus
`tests/test_four_node_fresh_factory.py` aus. Consumer-Gesamtlauf,
allgemeiner Testbestand, Adapter, Matrixzellen und Feldschritte wurden nicht
ausgefuehrt.

Abnahmeentscheidung:

```text
S1RQ_NOT_ACCEPTED
SIXTEEN_FACTORY_TESTS_EXECUTED
THIRTEEN_TEST_METHODS_PASSED
THREE_TEST_METHODS_REPORTED_SIX_ERROR_RECORDS
ONE_B3_TO_B6_KEY_TRANSLATION_DEFECT_IDENTIFIED
NO_CODE_CORRECTION_IN_EXECUTION_STAGE
```

## Ausgefuehrter Befehl

```text
python -m unittest discover -s tests -p "test_four_node_fresh_factory.py" -v
```

Ergebnis:

```text
Ran 16 tests in 2.430s
FAILED (errors=6)
```

Der Prozess endete mit Exitcode `1`.

## Bestandene Oberflaechen

13 Testmethoden bestanden. Damit blieben in diesem Lauf technisch
unauffaellig:

- A0- und A1-Zustandslosigkeit;
- A3- und M5-W7-N-Frischzustaende;
- B1- und B2-Wertobjekte;
- M1 FAST/SLOW-Nullspuren;
- beide M2-Modi und ihre getrennten Geometriedigests;
- M4-Anatomie sowie lokale und globale Ressourcenbilanz;
- gemeinsame Nullfeldidentitaeten, Nullwerte, offene Liniengeometrie und
  Dockabbildung;
- wiederholte Trennung des rein oeffentlichen Nullfeldobjektgraphen;
- Fail-Closed-Ablehnung unbekannter Rollen und nicht validierter Manifeste.

Diese Teilergebnisse ersetzen nicht die fehlende Gesamtannahme von S1-RQ.

## Fehlerbild

Betroffen sind drei Testmethoden:

```text
test_all_fourteen_roles_build_in_registered_order
test_b3_through_b6_use_native_substrate_with_explicit_edge_bridge
test_repeated_role_builds_have_separate_public_and_private_objects
```

Die parametrisierte B3-B6-Pruefung erzeugte je einen Fehler fuer B3, B4, B5
und B6. Zusammen mit den beiden weiteren betroffenen Methoden ergeben sich
sechs Fehlerrecords.

Alle Fehler besitzen dieselbe Ursache:

```text
FRESH_FACTORY_PRIVATE_STATE_INVALID:
substrate mass fields mismatch;
missing=['neuron_id'], unknown=['node_id']
```

## Ursachenanalyse

Der registrierte S1-RK-Payload bezeichnet die Knotenidentitaet einer Masse
mit:

```text
node_id
```

Der vorhandene native `MCMSubstrateMass.from_payload` erwartet dagegen:

```text
neuron_id
```

S1-RP reichte den registrierten Massenpayload unveraendert an den nativen
Konstruktor weiter. Damit fehlte genau die in S1-RO geforderte kontrollierte
Typuebersetzung fuer diesen Feldnamen.

Werte, Reihenfolge, Massenbilanz, Armparameter und Kanten-Digestbruecke sind
nicht als Fehlerursache identifiziert. Der Fehler tritt vor Erzeugung eines
nativen B3-B6-Substratzustands auf.

## Korrekturgrenze

Die zulaessige Korrektur ist auf eine reversible Schluesselabbildung
begrenzt:

```text
Manifest -> nativer Zustand: node_id -> neuron_id
nativer Zustand -> Manifest: neuron_id -> node_id
```

Dabei muessen unveraendert bleiben:

- alle vier Knotenidentitaeten und ihre Reihenfolge;
- jede Masse `0.25` und Gesamtmasse `1.0`;
- alle vier Armvertraege;
- registrierter und nativer Kanten-Digestpfad;
- B6-Spezifikationsdigest;
- alle zwoelf registrierten Privatdigests;
- alle anderen Rollenimplementierungen und Tests.

Es ist keine Manifestreparatur und keine Aenderung von
`MCMSubstrateMass`. Die Uebersetzung gehoert ausschliesslich an die lokale
B3-B6-Fabrikgrenze.

## Technische Bewertung

Der Befund erfordert keinen Architekturwechsel und keine fachliche
Neuausrichtung. Er zeigt, dass Manifest- und native Schemaidentitaeten nicht
nur bei Digests, sondern auch bei semantisch gleichbedeutenden Feldnamen
explizit getrennt werden muessen.

Die Fail-Closed-Grenze funktionierte korrekt: Es wurde kein unvollstaendiges
Rollenbundle ausgegeben.

## Paketstatus

```text
S1RQ_FOCUSED_RUN_COMPLETE_NOT_ACCEPTED
B3_B4_B5_B6_NATIVE_MASS_CONSTRUCTION_BLOCKED
OTHER_THIRTEEN_TEST_METHODS_PASSED
ROLE_FACTORY_TECHNICAL_ACCEPTANCE_WITHHELD
BASELINE_ADAPTERS_NOT_CONNECTED
MANDATORY_224_CELL_PACKAGE_NOT_EXECUTABLE
```

## Genau ein naechster Schritt

Als einziger Anschluss ist zulaessig:

```text
S1-RR - statischer Korrekturvertrag fuer die reversible B3-B6-
        Massenidentitaetsabbildung node_id <-> neuron_id
```

S1-RR darf nur Einfuegepunkt, Vorwaerts- und Rueckabbildung,
Unveraendertheitsbedingungen und erneutes Testbudget binden. Keine
Implementierung, keine Testausfuehrung, kein Adapteranschluss, keine
Matrixzelle und kein Feldlauf.
