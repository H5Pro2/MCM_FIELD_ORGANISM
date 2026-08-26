# S1-OR G2/D3 Zweischrittkomposition: Implementierungs-, Fixture- und Testbudgetvertrag

## Status

S1-OR bindet ausschliesslich Dateigrenzen, kanonische Chainfixtures,
gezielte externe Fehlermutationen und ein endliches Einmaltestbudget fuer
die spaetere S1-OQ-Zweischrittkomposition. Der Schritt implementiert nichts
und fuehrt keinen Test aus.

Entscheidung:

```text
G2_D3_TWO_STEP_COMPOSITION_IMPLEMENTATION_FIXTURES_AND_SINGLE_TEST_BUDGET_BOUND
```

## Gebundene Dateigrenze

S1-OS darf genau drei neue Dateien anlegen:

| Datei | Aufgabe |
|---|---|
| `mcm_field_organism/g2_d3_two_step_composition.py` | reine Zweischrittkomposition und Sequenzregistry |
| `tests/g2_d3_s1os_fixtures.py` | zwei kanonische Chains und sieben externe Fehlermutationen |
| `tests/test_g2_d3_s1os_two_step_composition.py` | fokussierte technische Abnahme |

Bestehende Produktions-, Fixture- und Testdateien bleiben unveraendert. Die
akzeptierten Projektions-, Commit-, Betrags-, Grenz- und D3-Module duerfen
nicht erweitert, repariert oder ersetzt werden. Statusdokumente duerfen nach
dem einmaligen Test nur dessen tatsaechliches Ergebnis aufnehmen.

## Erlaubte Produktionsabhaengigkeiten

Das neue Produktionsmodul darf nur importieren:

- Python-Standardbibliothek fuer unveraenderliche Datentypen und reines
  kanonisches JSON-Lesen;
- Registrytypen, Resultattypen, Vertragsdigests sowie die reinen
  Projektions- und Commitfunktionen aus `g2_d3_target_projection`;
- Registrytyp, Receipttyp und reine Validierungsfunktion aus
  `g2_d3_transient_boundary_validator`;
- `G2D3ValidationRegistry` aus `g2_d3_schema_validator`;
- `G2D3HalvingAmountRegistry` aus `g2_d3_halving_amount`;
- `canonical_json_bytes` und `sha256_hex` aus dem unveraenderten
  KFS-1-Validator.

Admissibility-, O3-, Feld-, Transfer-, Runner-, Medien-, Browser-, Netzwerk-,
Speicher- und Dateischreibmodule sind verboten.

## Gebundene oeffentliche Oberflaeche

Das Modul darf genau bereitstellen:

```text
build_g2_d3_two_step_composition_registry()
-> G2D3TwoStepCompositionRegistry

compose_g2_d3_two_step_continuation(
    first_boundary_raw_bytes,
    second_boundary_raw_bytes,
    initial_d3_raw_bytes,
    formation_enabled,
    sequence_registry,
    target_commit_registry,
    amount_registry,
    boundary_registry,
    d3_registry,
) -> G2D3TwoStepCompositionResult
```

Zusaetzlich sind nur die in S1-OQ gebundenen unveraenderlichen Chainrecord-,
Registry-, Resultat- und Belegtypen sowie Schema-, Phasen-, Fehlercode- und
Vertragsdigestkonstanten oeffentlich. Parsing, Gating und Belegaufbau bleiben
privat.

## Feste Vertragswerte

```text
receipt_schema
= g2_d3_two_step_composition_receipt/s1oq.v1

composition_class_id
= G2_D3_TWO_FRESH_CONTINUATION_COMPOSITION

composition_contract_digest
= e68646a2d4a605ecdd36125dcd5f97cd849091d5af1bbcf1f587b1c01e1c2e06

accepted_projector_contract_digest
= c761d3f5b2dc486ca6cb9389d305e9b2ec8d847812bac72e40d89995a66f6e2b

accepted_commit_contract_digest
= 4cae38e9c7986ff6099cfd8c2c742a2c11465bb61a9885441a403fab9b5859b5

accepted_amount_operator_contract_digest
= 396bd7b9fde4b7ee3b268e1d53245fd2a950cf4d8d9464f084d9b498c17de83b

accepted_boundary_validator_contract_digest
= 7a84b6f6dee9ba8f6e7f5cce9ee7655a63104cda669aabe35101072036fdebd0

accepted_d3_validator_contract_digest
= b113a2deb46d3f42e07a110335d6a665a89d8a39686a1e86700e8e971bf6ab9c
```

## Kanonische zweite Grenzen

Die Fixturedatei darf `build_boundary` testseitig fuer Ordinal `2` verwenden,
danach ausschliesslich `source_d3_anatomy_record_digest` auf Mixed setzen,
`boundary_record_digest` neu berechnen und kanonisch serialisieren.

Gebundene X-Grenze:

```text
prior/current ordinal = 1/2
prior/current orientation = X/X
boundary_record_digest
= 7d499f00806f6a7e9afea9119aad09b5a74b736881a7a93bd61142fcce8e8ab0
boundary_input_digest
= 6d4a6a51e8c3fb81734598f23edff930f88b5f85e00b79c5d84d1da2b5b0ad9a
```

Gebundene Y-Grenze:

```text
prior/current ordinal = 1/2
prior/current orientation = Y/Y
boundary_record_digest
= b9756269da497da0c64a0e63e5a64f1c98497118b4ad9f61f74eafcd0786d9c0
boundary_input_digest
= dc772636ed23e9cf9a904fd9943a7a1bcfacafe08aed9e60a65ac93f3d266d32
```

## Zwei gueltige Chainfixtures

Jedes Fixture ist ein Tupel aus erster Grenze, zweiter Grenze, initialem C0
und `formation_enabled=true`.

| Fixture | erste Grenze | zweite Grenze | erwartete Chain | erwartetes Final |
|---|---|---|---|---|
| `OR_V_XXX` | X/X `0/1` | X/X `1/2` | `OP_CHAIN_XXX` | Second |
| `OR_V_YYY` | Y/Y `0/1` | Y/Y `1/2` | `OP_CHAIN_YYY` | Second |

Beide binden:

```text
initial input digest
= d248ddae09d0cbd3874254082ed5675a82792d6e4fb3aa76ecf0ef59cbc546f7

intermediate input digest
= 2a4eaace22145b47e44e3d0c5a98a8b3e289deeee1190db4bb079228bf11aea8

final input digest
= a0e9a2468571ab2a3c437f8d436958b5c0eef886ad1e7f3d2b4ce54d278e7bab
```

Die erwarteten finalen Bytes stammen aus dem bereits statisch gebundenen
`D3_OL_SECOND_TARGET`; sie werden nicht aus der neuen Implementierung
uebernommen.

## Sieben externe Fehlermutationen

### Unbekannte erste Chain

`OR_I_UNKNOWN_FIRST` ersetzt nur die erste X/X-Grenze durch die gueltige
X/Y-Grenze. Initial C0 und zweite X-Grenze bleiben unveraendert.

```text
expected = OQ_UNKNOWN_CHAIN_BINDING
first projection calls = 0
```

### Falscher Initialzustand

`OR_I_UNKNOWN_INITIAL` verwendet die registrierte erste und zweite X-Grenze,
aber Mixed statt C0 als Initial-D3.

```text
expected = OQ_UNKNOWN_CHAIN_BINDING
first projection calls = 0
```

### Formation deaktiviert

`OR_I_FORMATION_DISABLED` ist bytegleich zu `OR_V_XXX`, setzt aber den
Schalter auf `false`.

```text
expected = OQ_FORMATION_DISABLED
first projection calls = 0
```

### Allgemein ungueltige zweite Grenze

`OR_I_SECOND_INVALID` aendert in der kanonischen zweiten X-Grenze nur
`schema_version` auf `s1oa.v2`, ohne den alten Boundary-Recorddigest zu
reparieren.

```text
second boundary input digest
= 5a4f299e8737d118c747fcd4246a2c94f6a610b7a37aeed600241f90e7496b16

expected = OQ_SECOND_BOUNDARY_INVALID
second projection calls = 0
```

### Alte D3-Quellbindung

`OR_I_SECOND_SOURCE_C0` ist eine ansonsten vollstaendig gueltige X-Grenze
mit Ordinalen `1/2`, bindet aber C0 statt Mixed als D3-Quelle und wird danach
kanonisch neu versiegelt.

```text
boundary_record_digest
= db513ad998ed296cecbe8f7da0fe931811860ae87ad7ccc69a0da21bcd29b321

boundary input digest
= b2d417714d168a73291be743752be7586e32e2b0c67a9f7b96c6708a3ae7b82c

expected = OQ_SECOND_SOURCE_BINDING_MISMATCH
second projection calls = 0
```

### Gekreuzter Kontaktlink

`OR_I_SECOND_CONTACT_CROSS` kombiniert die erste X-Grenze mit der gueltigen
zweiten Y-Grenze. Initialzustand und D3-Quellbindung bleiben korrekt.

```text
expected = OQ_SECOND_CONTACT_LINK_MISMATCH
second projection calls = 0
```

### Zurueckgesetzter Kontaktlink

`OR_I_SECOND_CONTACT_RESET` verwendet nach der ersten X-Grenze eine
ansonsten gueltige X/X-Grenze mit erneutem Ordinalpaar `0/1` und korrekter
Mixed-Quellbindung.

```text
boundary_record_digest
= 62003cc5144577d7c793051c01534348bc8be20e756bc1ab14d50199e17da79b

boundary input digest
= 5b1413f8041cb6d7c9552860affa75f2e74958b30b5bb00a6dfc2cc674f83087

expected = OQ_SECOND_CONTACT_LINK_MISMATCH
second projection calls = 0
```

## Defensive interne Codes

Folgende S1-OQ-Codes bleiben registrierte Sicherheitsgrenzen:

```text
OQ_FIRST_PROJECTION_FAILED
OQ_FIRST_COMMIT_FAILED
OQ_INTERMEDIATE_IDENTITY_MISMATCH
OQ_SECOND_PROJECTION_FAILED
OQ_SECOND_COMMIT_FAILED
OQ_FINAL_IDENTITY_MISMATCH
```

Mit exakten Registries, den zwei registrierten ersten Grenzen und den
akzeptierten unveraenderten Abhaengigkeiten sind diese Codes nicht durch
einen zusaetzlichen externen Fixturewert erreichbar. S1-OR verbietet deshalb
Monkeypatching, Dependency-Ersatz, gefaelschte Resultatobjekte und
Produktionshooks nur zur kuenstlichen Codeerzeugung.

Die Abnahme prueft statisch, dass alle sechs Codes registriert und an ihrem
jeweiligen Voraussetzungsgate fail-closed implementiert sind. Ein dort
auftretender Fehler in realer Verwendung darf keine finalen Bytes liefern.

## Fokussierte Testmatrix

| Test-ID | Abnahme |
|---|---|
| `T01` | alle Chain-, Boundary-, Initial-, Zwischen- und Finaldigests sind exakt gebunden |
| `T02` | XXX und YYY liefern exakt ihre Chainrolle und dieselben finalen Second-Bytes |
| `T03` | beide Ketten besitzen bitidentische Zwischen- und Final-D3-Digests |
| `T04` | der passive Beleg enthaelt nur Digests/Status und besitzt einen unabhaengig rekonstruierten Eigendigest |
| `T05` | unbekannte erste Grenze und falscher Initialzustand stoppen vor erster Projektion |
| `T06` | deaktivierte Formation stoppt vor erster Projektion |
| `T07` | allgemein ungueltige zweite Grenze stoppt nach erstem Commit vor zweiter Projektion |
| `T08` | alte C0-Quellbindung liefert nur den gebundenen Quellenfehler |
| `T09` | gekreuzter und zurueckgesetzter Kontakt liefern nur den Kontaktlinkfehler |
| `T10` | Completed-Checks belegen das Voraussetzungsgating aller externen Fehler |
| `T11` | alle elf Codes sind registriert; sechs defensive Codes besitzen keine externen Fake-Fixtures |
| `T12` | gleiche Inputs liefern bitgleiche Resultate; Inputs und Registries bleiben unveraendert |
| `T13` | falsche API-Typen/Registries und Belege als Eingaben scheitern vor Resultat |
| `T14` | Moduloberflaeche erreicht keinen Runtime-, O3-, Feld-, Runner-, I/O-, Medien- oder Netzwerkpfad |

Die Tests verwenden ausschliesslich `unittest` und Python-Standardbibliothek.
Fixtures und Erwartungen werden nach einem Testresultat nicht angepasst.

## Endliches S1-OS-Ausfuehrungsbudget

S1-OS darf genau einmal ausfuehren:

```text
python -m unittest tests.test_g2_d3_s1os_two_step_composition
```

Innerhalb dieser Abnahme gelten maximal:

```text
compose_g2_d3_two_step_continuation:         35 Aufrufe
project_g2_d3_conservative_target:          100 interne Aufrufe
verify_and_commit_g2_d3_projected_target:    50 interne Aufrufe
evaluate_g2_d3_continuation_halving_amount: 100 interne Aufrufe
validate_g2_d3_transient_boundary:          130 interne Aufrufe
validate_g2_d3_anatomy_record:              300 interne Aufrufe
O3-Auswertungen:                               0
MCM-Feldschritte:                               0
Runtime-/Speicherpublikationen:                 0
Transfer-/Runner-/Medien-/Netzwerkaufrufe:      0
Dateischreibzugriffe des Operators:             0
read-only Quelltextzugriffe:           maximal 3
```

Bei einem Fehler wird der S1-OS-Test nicht erneut ausgefuehrt. Die
Implementierung wird gegen den unveraenderten Vertrag korrigiert, ohne
Fixtures, Digests, Erwartungen oder Budgets umzudeuten.

## Aussagegrenze

S1-OR bindet nur die spaetere Implementierung und einmalige technische
Abnahme der begrenzten Zweischrittkomposition. Es gibt noch keine
Sequenzimplementierung, keine Runtimepublikation, keine O3- oder Feldwirkung
und keinen Befund zur hypothetischen MCM-Memory.

## Naechster erlaubter Schritt

S1-OS darf ausschliesslich die drei gebundenen Dateien implementieren, den
fokussierten Test genau einmal innerhalb des Budgets ausfuehren und das
tatsaechliche Ergebnis in den Statusdokumenten festhalten.

Runtimepublikation, O3, Feld, Transfer, Runner und Medienpfade bleiben
unveraendert und gesperrt.
