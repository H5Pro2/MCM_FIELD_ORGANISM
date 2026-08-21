# S1-RP: Implementierung der Rollenbundle und Digestbruecken

## Status und Umfang

S1-RP erweitert die bestehende Vier-Knoten-Frischfabrik um alle 14
registrierten Rollenbundle, die Kanten-Digestbruecke fuer B3-B6/M4 und die
M2-Geometrie-Digestbruecke. Im bestehenden Fabriktestmodul sind zehn
zusaetzliche Testmethoden definiert.

Es wurde kein Test ausgefuehrt. Es gibt keinen Adapteranschluss, keine
Matrixzelle und keinen Feldschritt.

Implementierungsstatus:

```text
FOURTEEN_ROLE_FRESH_BUNDLES_IMPLEMENTED
TWO_STATELESS_MARKERS_PRESERVED
TWELVE_PRIVATE_FRESH_STATES_IMPLEMENTED
EDGE_DIGEST_BRIDGE_IMPLEMENTED
M2_GEOMETRY_DIGEST_BRIDGE_IMPLEMENTED
PRIVATE_PAYLOAD_ROUNDTRIP_IMPLEMENTED
SIXTEEN_FACTORY_TESTS_DEFINED_NOT_EXECUTED
NO_ADAPTER_NO_MATRIX_NO_FIELD_ADVANCE
```

## Geaenderte Codedateien

S1-RP aendert ausschliesslich:

```text
mcm_field_organism/four_node_fresh_factory.py
tests/test_four_node_fresh_factory.py
```

Die Manifestdatei, der Consumer, Altmodule, `current_api.py`, Paketexporte,
Runner und Gleichungen bleiben unveraendert.

## Rollenbundle

`build_four_node_role_fresh_bundle` erzeugt pro Aufruf:

- ein neues technisch abgenommenes oeffentliches Vier-Knoten-Nullfeld;
- exakt eine der 14 registrierten Modellrollen;
- fuer A0/A1 nur die jeweilige Zustandslosmarkierung;
- fuer die anderen zwoelf Rollen einen typisierten privaten Frischzustand;
- den registrierten Privatdigest oder bei A0/A1 exakt `None`.

Unbekannte Rollen werden vor einer Teilrueckgabe mit
`FRESH_FACTORY_MODEL_ROLE_INVALID` abgelehnt.

## Implementierte Zieltypen

Neu in der bestehenden Fabrikdatei sind unveraenderliche technische
Wertobjekte fuer:

- B1-Kantenraten und Fixed-Adapter-Frischstatus;
- B2-Knoteneintraege und Integrator-Frischstatus;
- B3-B6 als Huelle um einen nativen `MCMSubstrateState`;
- M4-Raten und Huelle um eine native `DTS1ResourceAnatomy`;
- den gemeinsamen privaten Frischstatus und das vollstaendige Rollenbundle.

Vorhandene native Zustandsklassen werden fuer A3, M1, M2 und M5 direkt
verwendet. Der historische `DTS1CommonIntervalPrivateState` wird nicht
importiert oder erweitert.

## Kanten-Digestbruecke

Vor B3-B6 und M4 vergleicht die Fabrik das registrierte S1-RK-
Kanteninventar mit `mcm_substrate_edge_inventory(field.layer)`. Nur bei
exakter Gleichheit der drei sortierten Kanten wird weitergebaut.

B3-B6 tragen im nativen `MCMSubstrateState` den von
`mcm_substrate_edge_inventory_digest` geforderten Layerdigest. M4 behaelt
seinen anatomieeigenen Digest. In der registrierten Rueckprojektion wird nur
der S1-RK-Kanteninventardigest eingesetzt.

Alle Digestrollen bleiben getrennt abrufbar. Sie werden nicht als
bitidentisch vorausgesetzt.

## M2-Geometrie-Digestbruecke

M2 DELAY und REPLAY werden mit ihren vorhandenen registrierten
Konfigurationsbuildern und `build_empty_m2_buffer` erzeugt. Der native
Puffer traegt den REPLACE_S-Compositordigest der vollstaendigen Feldgeometrie.

Die private Frischhuelle behaelt getrennt:

```text
registered_geometry_digest_or_none
native_geometry_digest_or_none
```

Der native Digest wird erneut direkt aus dem erzeugten Feld berechnet und
gegen den Puffer geprueft. Die registrierte Rueckprojektion verwendet den
S1-RK-Geometriedigest. Damit bleibt nachvollziehbar, welcher Digest welches
Praeimage bezeichnet.

## Privater Roundtrip

Nach jeder nativen Konstruktion erzeugt `_state_projection` den
registrierten `state_payload` erneut. Danach wird der vollstaendige private
Payload mit Modellrolle, Carry-Klasse, Schema, nativer Schemaidentitaet und
Konfigurationsbindung rekonstruiert.

Nur wenn dieser Payload den in S1-RK gebundenen Privatdigest reproduziert,
wird das Rollenbundle zurueckgegeben. Abweichungen enden ohne Teilobjekt mit
`FRESH_FACTORY_PRIVATE_STATE_INVALID` oder
`FRESH_FACTORY_PRIVATE_DIGEST_MISMATCH`.

## Rollenbestand

| Rollen | Implementierter Frischstatus |
|---|---|
| A0/A1 | kein Privatobjekt, exakte Markierung |
| B1 | Basisrate 1.0, drei Kantenraten 1.1, Backreaction aktiv |
| B2 | vier Nullwerte |
| B3-B5 | vier Viertelmassen, rollenfester Arm, kein Zusatzdigest |
| B6 | vier Viertelmassen, CONST-V-Arm, gebundener Spezifikationsdigest |
| A3 | registrierter NORM-Zustand mit vier Nullwerten |
| M1 | getrennte FAST- und SLOW-Nullspur |
| M2 DELAY | leerer Puffer, Phase `NOT_APPLICABLE`, Cursor null |
| M2 REPLAY | leerer Puffer, Phase `CAPTURE`, Cursor null |
| M4 | vier Kapazitaeten, drei Ressourcenkanten, drei registrierte Raten |
| M5 | registrierter LEAK-Zustand mit vier Nullwerten |

## Definierte neue Tests

Zehn neue Testmethoden decken gemeinsam ab:

- Aufbau aller 14 Rollen in registrierter Reihenfolge;
- strikte A0/A1-Zustandslosigkeit;
- B1- und B2-Wertobjekte;
- B3-B6-Massen, Arme und Kantenbruecke;
- getrennte A3- und M5-W7-N-Zustaende;
- die zwei getrennten M1-Spuren;
- beide M2-Modi und die Geometriebruecke;
- M4-Lokal- und Globalbilanz;
- unbekannte Rollen;
- getrennte oeffentliche und private Objektgraphen bei Wiederholung.

Zusammen mit den sechs bereits bestehenden Nullfeldtests enthaelt
`test_four_node_fresh_factory.py` jetzt exakt 16 Testmethoden. Das
S1-RL-Testbudget ist damit ausgeschöpft. Die zehn Consumer-Tests bleiben
unveraendert.

## Statischer Audit

Der reine Quellenaudit bestaetigt:

- genau zwei geaenderte Codedateien;
- syntaktisch gueltige Produktions- und Testquelle;
- exakt 16 Fabriktestmethoden;
- keinen Aufruf von `SharedMCMField.advance` oder einer Baseline-
  Advancefunktion;
- keinen Import des alten S1-JZ-Orchestrators oder seines Privatzustands;
- keine neue Datei, Gleichung, Konfiguration oder Runtime.

Dieser Audit ist keine Testausfuehrung.

## Technische Aussagegrenze

S1-RP implementiert ausschliesslich Frischzustandskonstruktion und
Roundtrippruefung. Die Implementierung ist noch nicht technisch abgenommen.
Sie belegt keine Adapteranschlussfaehigkeit, Baselinefunktion,
Felddynamik oder hypothetische MCM-Memory.

## Paketstatus

```text
S1RP_ROLE_FACTORY_SOURCE_COMPLETE
FOURTEEN_ROLE_BUNDLES_IMPLEMENTED_NOT_TEST_ACCEPTED
SIXTEEN_FACTORY_TESTS_DEFINED_NOT_EXECUTED
BASELINE_ADAPTERS_NOT_CONNECTED
MANDATORY_224_CELL_PACKAGE_NOT_EXECUTABLE
```

## Genau ein naechster Schritt

Als einziger Anschluss ist zulaessig:

```text
S1-RQ - fokussierte Ausfuehrung und technische Abnahme der exakt 16
        Vier-Knoten-Fabriktests
```

S1-RQ darf nur `tests/test_four_node_fresh_factory.py` ausfuehren und das
Ergebnis protokollieren. Kein Consumer-Gesamtlauf, kein allgemeiner
Testbestand, kein Adapteranschluss, keine Matrixzelle und kein Feldlauf.
