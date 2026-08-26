# S1-TS: Statischer Konsolidierungs- und Driftgrenzenvertrag der Kandidatenhuelle

## Status und Zweck

S1-TS bindet die mit S1-TQ technisch abgenommene Kandidatenhuelle nach der
S1-TR-Zulassungsentscheidung als getrennte inaktive Forschungsinfrastruktur.
Der Vertrag aendert keine Runtime-, API-, Inventar-, Produktions- oder
Testdatei und fuehrt keinen Test oder Feldlauf aus.

```text
S1_TS_INACTIVE_RESEARCH_INFRASTRUCTURE_CONSOLIDATION_AND_DRIFT_BOUNDARY_BOUND
```

## Eingefrorener Infrastrukturstand

```text
mcm_field_organism/four_node_candidate_observation_envelope.py
  e7ef64fbbb8dc22ad123484ac53ab6cdbe1d5d4f17440a47ffd311f3c70ad74d
tests/test_four_node_candidate_observation_envelope.py
  b457cab3e798859cdc1550d98800ca130bcce055341d6b15ebdcc4ef53595d8c
```

Gebundene technische Abnahme:

```text
24 von 24 synthetischen Testmethoden
genau ein erfolgreicher S1-TQ-Lauf
32 priorisierte Fail-Closed-Fehlerklassen
keine reale Kandidatenhuelle
```

Beide Dateien duerfen ohne neuen statischen Aenderungsvertrag nicht
veraendert werden.

## Eingefrorene aktive Oberflaechengrenze

```text
mcm_field_organism/current_api.py
  01daabe43dd52766014926f3ee30d55cd390d9d3ed6651a7bd3664997caa0360
mcm_field_organism/root_lazy_exports.py
  ff6689dfebbe8ba415753c7d509175322229a0c48d8d2670c2f6ec3257bfa016
mcm_field_organism/__init__.py
  bb9d968aafe91b4c909abcf30e59b0cc0695fb0d815f32e2014972270327c9da
```

Keine dieser Oberflaechen bietet Namen aus
`four_node_candidate_observation_envelope` an. Kein anderes Produktionsmodul
und keine andere Testdatei importiert die Huelle. Diese Abwesenheit ist eine
gewollte operative Grenze.

Eine spaetere unabhaengige Aenderung der drei Oberflaechendateien muss nicht
dauerhaft deren heutigen Bytehash erhalten. Sie darf aber ohne ausdrueckliche
Kandidatenfreigabe keinen Namen, Modulpfad oder Lazy-Eintrag der Huelle
aufnehmen.

## Abgrenzung zum bestehenden Root-Inventar

Das vorhandene S1-PT-Inventar klassifiziert angebotene Root-Namen in fuenf
operative Rollen. Die Kandidatenhuelle besitzt absichtlich keinen Root-Namen
und darf deshalb nicht durch eine erfundene Root-Klassifikation in dieses
Inventar eingetragen werden.

Eingefrorene Referenzen:

```text
docs/S1PT_ROOT_EXPORT_INVENTORY_V1.json
  4697f0773445718510d28e42e9bc88bf6aa57cbfe41a9d48d1c6ac035cc90e79
tools/build_s1pt_root_export_inventory.py
  1ad63632dc23c8b11da81aafe594f14ae62ebba768f054e43408a3ad7a177bfc
```

S1-TS erweitert weder die S1-PT-Klassen noch den Builder. Die neue Rolle
`INACTIVE_RESEARCH_INFRASTRUCTURE` gilt nur in einem getrennten
Dokumentationsmanifest fuer nicht angebotene Forschungsdateien.

## Verbindliche Rollenklassifikation

| Datei | Rolle | Operative Bedeutung |
|---|---|---|
| `mcm_field_organism/four_node_candidate_observation_envelope.py` | `INACTIVE_RESEARCH_INFRASTRUCTURE` | direkt importierbarer reiner Strukturvalidator ohne aktiven Anschluss |
| `tests/test_four_node_candidate_observation_envelope.py` | `INACTIVE_RESEARCH_INFRASTRUCTURE_TEST` | synthetische technische Abnahme, kein aktiver Testprozess |

Aus dieser Klassifikation folgt keine Kandidatenzulassung und keine
Funktionsaussage.

## Driftgates

Die Konsolidierungsgrenze ist verletzt, sobald ohne neuen Vertrag mindestens
einer dieser Faelle eintritt:

1. Quell- oder Testdigest driftet;
2. ein Huellenname erscheint in `current_api`, Root-Lazy-Exports oder
   Paket-`__all__`;
3. ein aktives Feld-, Runner-, Fixture-, Producer- oder Comparatormodul
   importiert die Huelle;
4. das Huellenmodul importiert ein anderes Projektmodul;
5. Datei-, Netzwerk-, Prozess-, Thread-, Uhrzeit- oder Geraetezugriff wird
   hinzugefuegt;
6. eine oeffentliche Builder-, Producer-, Runner-, Comparator-, Parse-,
   Repair- oder Serialisierungsfunktion wird angeboten;
7. ein realer Report oder Atlas wird durch den Validator gelesen;
8. synthetische Schemaabnahme wird als Kandidaten- oder Funktionsbefund
   bezeichnet;
9. ein geschlossener Zweig wird ueber die Huelle wieder aktiviert.

Bei Drift bleibt die Huelle fail-closed ausserhalb der aktiven API, bis ein
neuer statischer Vertrag Ursache, Umfang und Abnahme bindet.

## Wiedereroeffnungstor der Kandidatenforschung

Alle neun S1-TR-Voraussetzungen muessen vor einer Reaktivierung gemeinsam und
kandidatenspezifisch vorliegen:

```text
R01 eigene nicht-reduzierbare Funktionsprognose
R02 endogene Erreichbarkeit aus normaler Feldgeschichte
R03 eigenstaendige nicht-DTS- und nicht-G2-reduzierbare Anatomie
R04 konjugierte Feld-Traeger-Kopplung
R05 endliche lokale Bilanz und ungueltige Zustaende
R06 isolierende vorregistrierte Falsifikationsintervention
R07 gemeinsamer Lebenszyklus aus Bildung bis Wiederbeanspruchung
R08 faire kausalhistorisch gleiche Gegenbaselines
R09 getrennte Producer- und passive Comparatorgrenze
```

R01 bis R08 muessen vor R09 feststehen. Eine Analogie, Umbenennung,
Parameterabweichung oder synthetisch gueltige Huelle erfuellt das Tor nicht.

## Gebundenes getrenntes Manifest

Ein spaeterer S1-TU-Schritt darf genau eine neue Datei anlegen:

```text
docs/S1TU_INACTIVE_RESEARCH_INFRASTRUCTURE_V1.json
```

Das kanonische JSON bindet ausschliesslich:

- `contract_id = mcm.s1tu.inactive-research-infrastructure.v1`;
- `contract_digest = d427ce7743ed4c557609ca98a15d09f8beae26580505fa3d853687d37e66d19e`;
- kompakte ASCII-JSON-Kanonisierung mit sortierten Schluesseln;
- genau zwei geordnete Infrastrukturrecords samt Rollen und Bytehashes;
- genau drei geordnete aktive Oberflaechenbelege samt Bytehashes;
- die zwei unveraenderten S1-PT-Referenzen;
- genau neun Driftgates und neun Wiedereroeffnungsanforderungen;
- Status `INACTIVE_RESEARCH_INFRASTRUCTURE_BOUND_NO_ACTIVE_EXPORT`;
- einen atomaren Artefaktdigest ueber alle Nutzfelder.

S1-TU darf kein Werkzeug, keinen Validator, keinen Export, keinen Test und
keine Runtimeaenderung hinzufuegen. Die Manifestpruefung erfolgt nur statisch
mit Standardbibliothek und ohne Projektimport.

## Aussagegrenze und naechster Schritt

S1-TS konsolidiert Infrastruktur. Es ist kein Kandidatenbefund und kein
Befund zur Entwicklungsrichtung einer hypothetischen MCM-Memory.

Der einzige naechste Schritt ist S1-TU fuer genau das eine kanonische
Dokumentationsmanifest und seine statische Abnahme. Es wird kein Test
ausgefuehrt und kein Forschungszweig wieder geoeffnet.
