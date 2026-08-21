# S1-SC: Statischer versionierter Frischmanifest-Matrixregistrierungs-, Migrations- und Abnahmebudgetvertrag

## Status und Zweck

S1-SC bindet die technische Migration von der historischen
224-Zellen-Aussage des S1-RK-Frischmanifests zur in S1-SB freigegebenen
17-Repliken-Topologie mit 238 Matrixzellen.

Der Bestandsaudit zeigt, dass sich weder Vier-Knoten-Geometrie noch
Rollenmapping, oeffentliche Frischprojektion oder rollenprivate
Frischzustaende geaendert haben. Veraendert wurde ausschliesslich die
aeussere Expositionsachse. Deshalb wird das abgenommene v1-Frischmanifest
nicht kopiert oder umgeschrieben. Die neue Topologie wird in einer eigenen
versionierten Matrixregistrierung an den unveraenderten v1-Digest gebunden.

S1-SC materialisiert diese Registrierung noch nicht, implementiert keinen
Consumer, aendert keine Fabrik, definiert oder startet keinen Test und bindet
noch kein Expositionsfixture.

Vertragsentscheidung:

```text
S1RK_V1_FRESH_MANIFEST_PRESERVED_BYTE_FOR_BYTE
EXPOSURE_TOPOLOGY_SPLIT_FROM_STABLE_FRESH_STATE_MANIFEST
VERSIONED_17_REPLICA_238_CELL_MATRIX_REGISTRATION_BOUND
BASE_MANIFEST_AND_MATRIX_REGISTRATION_MUST_VALIDATE_TOGETHER
NO_MATERIALIZATION_NO_IMPLEMENTATION_NO_TEST_NO_EXECUTION
```

## Architekturentscheidung

Die bisherige Aussage
`public_fresh_shared_by_all_224_cells` liegt im Feld
`cross_identity_audit` des v1-Frischmanifests. Sie war bei seiner Abnahme
korrekt, koppelt aber einen stabilen Frischzustand an eine spaeter
veraenderbare Versuchstopologie.

S1-SC trennt diese Verantwortungen fuer neue Arbeiten:

```text
S1-RK v1-Frischmanifest
  -> stabile Geometrie-, Rollen- und Frischzustandswerte

S1-SC Matrixregistrierung
  -> kanonische 17-Repliken-Achse
  -> 14 x 17 = 238 Zellen
  -> Frischprojektionsbindung fuer alle 238 Zellen
  -> 560 passive Pflichtrecords
```

Die historische 224-Aussage wird nicht als aktuelle Matrixzahl verwendet.
Sie bleibt Bestandteil der unveraenderten Herkunftsdatei und wird durch die
neue Registrierung explizit supersediert.

## Unveraenderliche Basisidentitaeten

Die Matrixregistrierung muss genau folgende Basisidentitaeten referenzieren:

| Rolle | Gebundener Wert |
|---|---|
| Basisdatei | `reports/s1rk_four_node_fresh_manifest.json` |
| Basisschema | `mcm.s1rk.four-node-fresh-manifest.v1` |
| Basiskanonisierung | `S1-JN/S1-JT-compact-json-sha256-v1` |
| Basismanifestdigest | `ae7a7356a3e06776a000b6e9fafef75b717944f1d75da62d4418be98cc439c68` |
| Kanteninventardigest | `9961eddd8c8a7ad845c9ab43af23f8ae5380c72ffae06c2e0af202cda49c3529` |
| Geometriedigest | `e0c416cc4aa97a66960640a2ff8fbe5d75edcc1f7a603c66b1efbf09ea820884` |
| Rollenmappingdigest | `16ffec39daf424b73b94ed03b0ee4552e29372ba557b37f194c0d9499c49c1dd` |
| oeffentlicher Frischdigest | `ce6912af2bc94458c2ba4243fa6df7b8b05494d956ef96730f4faf7ec5a8a879` |
| Modellrollenanzahl | `14` |
| zustandsbehaftete Privatrollen | `12` |
| Zustandslosmarkierungen | `2` |

Kein privater Payload wird in die neue Registrierung kopiert. Ihre
Integritaet bleibt Aufgabe des bestehenden v1-Consumers.

## Neue Registrierungsidentitaet

Die spaeter zu materialisierende Datei ist:

```text
reports/s1sd_four_node_fresh_matrix_registration.json
```

Sie besitzt:

```text
schema_id            = mcm.s1sc.four-node-fresh-matrix-registration.v1
source_contract_id   = S1-SC
canonicalization_id  = S1-JN/S1-JT-compact-json-sha256-v1
```

Der Registrierungsdigest wird wie beim v1-Manifest als SHA-256 ueber die
kanonische Compact-JSON-Praeimage ohne das eigene Feld
`registration_digest` gebildet. Der konkrete Digest darf erst bei der
einmaligen Materialisierung berechnet und danach statisch dokumentiert
werden.

## Exakte Rootform

Die Registrierung besitzt genau diese Rootfelder:

```text
schema_id
source_contract_id
canonicalization_id
base_fresh_manifest
exposure_replica_axis
matrix_cardinality
public_fresh_projection_binding
registration_digest
```

Unbekannte, fehlende oder doppelte Felder sind unzulaessig. Zahlen sind
JSON-Integer und keine Strings oder Gleitkommazahlen.

### `base_fresh_manifest`

Der Record traegt exakt:

```text
schema_id
manifest_digest
edge_inventory_digest
physical_geometry_digest
outer_exposure_role_mapping_digest
public_fresh_projection_digest
model_role_count
stateful_private_role_count
stateless_marker_count
```

Alle Werte muessen den oben gebundenen Basisidentitaeten entsprechen.

### `exposure_replica_axis`

Die Achse ist ein Array aus genau 17 Records mit den Feldern `position` und
`replica_role`. Positionen sind lueckenlos 1 bis 17. Die Rollenordnung ist:

```text
01 F_A
02 F_C
03 F_G
04 T_EARLY
05 T_LATER
06 I_LOCAL
07 I_REMOTE
08 I_GAP
09 C_LOCAL
10 C_REMOTE
11 C_GAP
12 R_EARLY
13 R_LATE
14 U_RELEASED
15 U_EARLY
16 U_FRESH_B_EARLY
17 U_FRESH_B_LATE
```

Ereignisse, Werte, Dauern und erwartete Kontrastrichtungen gehoeren nicht in
diese Achse.

### `matrix_cardinality`

Der Record traegt exakt:

```text
model_role_count                    = 14
exposure_replica_count              = 17
matrix_cell_count                   = 238
universal_checkpoint_count_per_model = 34
c_family_checkpoint_count_per_model  = 6
checkpoint_count_per_model           = 40
total_checkpoint_count               = 560
```

Der Consumer muss alle Zahlen aus den primitiven Achsen- und Rollenwerten
erneut berechnen. Wertgleichheit ohne korrekte Herleitung reicht nicht.

### `public_fresh_projection_binding`

Der Record traegt exakt:

```text
public_fresh_projection_digest = ce6912af2bc94458c2ba4243fa6df7b8b05494d956ef96730f4faf7ec5a8a879
shared_by_all_matrix_cells      = true
shared_matrix_cell_count        = 238
fresh_object_graph_per_cell     = true
```

Der vollstaendige Digest ist der oben gebundene oeffentliche Frischdigest.
`shared_by_all_matrix_cells` bedeutet Wert- und Digestgleichheit, nicht
gemeinsame veraenderliche Objektidentitaet. Jede spaetere Zelle benoetigt
einen getrennten Frischobjektgraphen.

## Gemeinsame Validierung

Die neue Registrierung ist allein nicht ausfuehrungsfaehig. Ein spaeterer
Validator muss zuerst:

1. das unveraenderte v1-Manifest mit dem technisch abgenommenen bestehenden
   Consumer vollstaendig validieren;
2. die neue Matrixregistrierung unabhaengig validieren;
3. alle Basisidentitaeten der Registrierung gegen die validierte
   v1-Manifestansicht vergleichen;
4. die 17 Rollen und alle abgeleiteten Zahlen reproduzieren;
5. erst danach ein unveraenderliches gemeinsames Registrierungsobjekt
   publizieren.

Eine Registrierung mit passendem Eigendigest, aber anderem Basismanifest,
ist `NOT_CONNECTABLE`. Das v1-Manifest wird weder repariert noch durch die
Registrierung teilweise ersetzt.

## Einfuegepunkte und Dateibudget

Die nachfolgende Implementierungsstufe S1-SD darf genau drei neue Dateien
anlegen:

```text
reports/s1sd_four_node_fresh_matrix_registration.json
mcm_field_organism/four_node_fresh_matrix_registration.py
tests/test_four_node_fresh_matrix_registration.py
```

Zulaessige Begleitveraenderungen sind nur Forschungsstandsdokumentation.
Insbesondere bleiben unveraendert:

- `reports/s1rk_four_node_fresh_manifest.json`;
- `mcm_field_organism/four_node_fresh_manifest.py`;
- `mcm_field_organism/four_node_fresh_factory.py`;
- alle 14 rollenweisen Frischfabriken und Modellaufrufe;
- Paketexporte, `current_api.py`, Orchestratoren und Comparatoren.

## Consumeroberflaeche

Das neue Modul darf genau folgende oeffentliche Rollen bereitstellen:

```python
class FourNodeFreshMatrixRegistrationError(ValueError): ...

@dataclass(frozen=True, slots=True)
class FourNodeFreshMatrixRegistration: ...

def parse_four_node_fresh_matrix_registration(
    raw_bytes: bytes,
) -> FourNodeFreshMatrixRegistration: ...

def load_four_node_fresh_matrix_registration(
    path: Path,
) -> FourNodeFreshMatrixRegistration: ...

def validate_four_node_fresh_matrix_registration_against_manifest(
    registration: FourNodeFreshMatrixRegistration,
    manifest: FourNodeFreshManifest,
) -> None: ...
```

Parser und Loader folgen denselben Grenzen wie der v1-Consumer: striktes
UTF-8/JSON, keine Importzeit-I/O, kein Cache, keine Defaults, keine
Normalisierung und eine rekursiv unveraenderliche Sicht.

## Fail-Closed-Codes

Jeder Fehler beendet den Aufruf ohne Teilobjekt. Zulaessig sind genau:

```text
FRESH_MATRIX_REGISTRATION_BYTES_INVALID
FRESH_MATRIX_REGISTRATION_SCHEMA_INVALID
FRESH_MATRIX_REGISTRATION_SHAPE_INVALID
FRESH_MATRIX_REGISTRATION_DIGEST_INVALID
FRESH_MATRIX_REGISTRATION_REPLICA_AXIS_INVALID
FRESH_MATRIX_REGISTRATION_CARDINALITY_INVALID
FRESH_MATRIX_REGISTRATION_BASE_IDENTITY_INVALID
FRESH_MATRIX_REGISTRATION_MANIFEST_MISMATCH
```

Der Validator darf die historische 224-Zellen-Aussage weder als aktuelle
Zahl akzeptieren noch im v1-Objekt ueberschreiben.

## Fokussiertes Abnahmebudget

S1-SD darf hoechstens 12 Unit-Tests definieren, aber noch nicht ausfuehren:

- gueltige Registrierung und rekursive Unveraenderlichkeit;
- Nicht-Bytes, ungueltiges JSON und doppelte Schluessel;
- fehlende oder unbekannte Felder und falsche Schemaidentitaet;
- falscher Registrierungsdigest;
- abweichende, doppelte oder ungeordnete Replikachse;
- 16- oder 18-Repliken-Achse;
- inkonsistente 238-/560-Ableitungen;
- falsche Basisidentitaet;
- gemeinsamer Erfolg mit dem validierten v1-Manifest;
- Ablehnung eines nicht validierten oder nicht passenden Basismanifests;
- Nachweis, dass v1-Report und bestehende Consumerdatei unveraendert sind.

Die Tests duerfen keinen Frischzustand bauen, keinen Modellkern aufrufen,
keine Matrixzelle erzeugen und kein Expositionsfixture materialisieren.

## Abnahmegrenze

Eine spaetere technische Abnahme belegt nur, dass die unveraenderte
Vier-Knoten-Frischregistrierung eindeutig mit der neuen 17-Repliken-
Topologie verbunden ist. Sie belegt keine Baselinefunktion, keine
Feldentwicklung und keine Faehigkeit einer hypothetischen
MCM-Memory-Entwicklungsrichtung.

## Genau ein naechster Schritt

S1-SD ist ausschliesslich fuer die einmalige Materialisierung der
Matrixregistrierung, die Implementierung ihres strikten Consumers und die
Definition der hoechstens 12 fokussierten, noch nicht ausgefuehrten Tests
zulaessig.

Keine Testausfuehrung, keine Aenderung des v1-Manifests, keine Fabrik- oder
Modellkernanpassung, kein Expositionsfixture und kein Forschungslauf.
