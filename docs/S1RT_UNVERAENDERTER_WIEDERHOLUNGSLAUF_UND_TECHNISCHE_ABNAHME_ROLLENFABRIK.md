# S1-RT: Unveraenderter Wiederholungslauf und technische Abnahme der Rollenfabrik

## Status und Umfang

S1-RT wiederholt nach der begrenzten S1-RS-Korrektur exakt den unveraenderten
S1-RQ-Fabriktestlauf. Es wurden keine Tests oder Produktionsquellen zwischen
Korrekturcommit und Wiederholung veraendert.

Abnahmeentscheidung:

```text
SIXTEEN_OF_SIXTEEN_FACTORY_TESTS_PASSED
B3_B4_B5_B6_MASS_KEY_TRANSLATION_ACCEPTED
FOURTEEN_ROLE_FRESH_FACTORY_TECHNICALLY_ACCEPTED
EDGE_AND_M2_GEOMETRY_DIGEST_BRIDGES_ACCEPTED
PRIVATE_PAYLOAD_AND_DIGEST_ROUNDTRIPS_ACCEPTED
NO_ADAPTER_NO_MATRIX_NO_FIELD_ADVANCE
```

## Ausgefuehrter Befehl

```text
python -m unittest discover -s tests -p "test_four_node_fresh_factory.py" -v
```

Ergebnis:

```text
Ran 16 tests in 2.863s
OK
```

Der Prozess endete mit Exitcode `0`.

## Abgenommene Korrektur

Die zuvor gescheiterten Oberflaechen bestanden jetzt:

```text
test_all_fourteen_roles_build_in_registered_order
test_b3_through_b6_use_native_substrate_with_explicit_edge_bridge
test_repeated_role_builds_have_separate_public_and_private_objects
```

Damit ist innerhalb der gebundenen Testoberflaeche bestaetigt:

- B3-B6 registrierte `node_id`-Massen werden nativ als `neuron_id`
  konstruiert;
- alle vier Knotenidentitaeten und Einzelmassen bleiben erhalten;
- die native Gesamtmasse bleibt `1.0`;
- die registrierte Rueckprojektion verwendet wieder `node_id`;
- alle vier rollenprivaten Digests werden nach dem Roundtrip reproduziert;
- wiederholte B3-Erzeugung liefert getrennte oeffentliche und private
  Objektgraphen.

## Technisch abgenommene Gesamtoberflaeche

Alle 16 Tests bestaetigen gemeinsam:

- Aufbau aller 14 Rollen in registrierter Reihenfolge;
- strikte Zustandslosigkeit von A0 und A1;
- exakte B1- und B2-Frischwerte;
- native B3-B6-Substratzustaende samt Kanten-Digestbruecke;
- getrennte registrierte A3- und M5-W7-N-Zustaende;
- getrennte M1-FAST/SLOW-Spuren;
- M2-DELAY und M2-REPLAY samt getrennter Geometriedigestbruecke;
- M4-Anatomie mit geschlossenen lokalen und globalen Ledgers;
- gemeinsame Vier-Knoten-Nullfeldgeometrie und Dockabbildung;
- Fail-Closed-Ablehnung unbekannter Rollen und unvalidierter Manifeste;
- getrennte Objektgraphen bei wiederholter Erzeugung.

## Vergleich mit S1-RQ

S1-RQ endete mit sechs Fehlerrecords aus einer gemeinsamen Ursache. S1-RT
verwendete dieselbe Testdatei und denselben Befehl. Nach ausschliesslicher
Korrektur der reversiblen Feldnamenabbildung bestehen alle betroffenen
Tests.

Damit ist die S1-RQ-Ursache technisch geschlossen. Es wurde kein Test an die
Implementierung angepasst.

## Nicht geprueft

S1-RT prueft nicht:

- Montage eines Rollenbundles zu einem vollstaendigen Modelleingang;
- private Adapter oder Baselineaufrufe;
- Carry-Regeln nach dem Frischzustand;
- Ereignis-, Profil-, Refinement- oder Replikzuordnung;
- Matrixzellen oder Ergebnisvergleiche;
- Feldentwicklung oder hypothetische MCM-Memory.

## Technische Bewertung

Die Frischzustandsgrundlage ist nun fuer alle 14 Rollen reproduzierbar,
objektgetrennt und fail-closed. Es liegt kein aktueller Befund vor, der eine
Aenderung der Feld- oder Frischfabrikarchitektur erfordert.

Der naechste technische Engpass ist die Montagegrenze zwischen einem
Rollenbundle und der jeweils vorhandenen Modell- oder Baselineoberflaeche.
Diese Grenze muss vor Implementierung pro Rolle statisch binden, ob der
private Zustand separat bleibt oder kontrolliert in eine native
`SharedMCMField`-Eingabe eingebettet werden muss.

## Paketstatus

```text
S1RT_ROLE_FACTORY_TECHNICALLY_ACCEPTED
FOURTEEN_FRESH_ROLES_AVAILABLE
MODEL_INPUT_ASSEMBLY_NOT_BOUND
BASELINE_ADAPTERS_NOT_CONNECTED
MANDATORY_224_CELL_PACKAGE_NOT_EXECUTABLE
```

## Genau ein naechster Schritt

Als einziger Anschluss ist zulaessig:

```text
S1-RU - statischer rollenweiser Adapteranschluss-, Modelleingangsmontage-
        und Integritaetsvertrag fuer die 14 abgenommenen Frischbundle
```

S1-RU muss pro Rolle binden, welche vorhandene Modelloberflaeche den
oeffentlichen Feldzustand und den privaten Frischzustand erhaelt, welche
Einbettung zulaessig ist und welche Identitaeten davor und danach gleich
bleiben muessen. Keine Implementierung, keine Testausfuehrung, keine
Matrixzelle und kein Feldlauf.
