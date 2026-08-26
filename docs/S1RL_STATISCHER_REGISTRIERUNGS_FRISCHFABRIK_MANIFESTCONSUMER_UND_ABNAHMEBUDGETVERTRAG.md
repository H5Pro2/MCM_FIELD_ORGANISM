# S1-RL: Statischer Registrierungs-, Frischfabrik-, Manifestconsumer- und Abnahmebudgetvertrag

## Status und Zweck

S1-RL bindet ausschliesslich die technischen Einfuegepunkte fuer das in
S1-RK materialisierte Vier-Knoten-Frischmanifest. Der Vertrag legt fest, wie
ein spaeterer Consumer das Manifest unveraendert pruefen und wie daraus ein
gemeinsamer oeffentlicher Nullfeldzustand sowie 14 getrennte rollenprivate
Frischformen erzeugt werden duerfen.

S1-RL implementiert nichts. Es registriert keine Geometrie, importiert kein
Manifest zur Laufzeit, erzeugt keinen Feldzustand und fuehrt weder Tests noch
Matrixzellen oder Feldschritte aus.

Vertragsentscheidung:

```text
TWO_PRODUCTION_FILES_AND_TWO_TEST_FILES_BOUND
S1RK_MANIFEST_IS_THE_ONLY_VALUE_SOURCE
COMMON_PUBLIC_FIELD_AND_PRIVATE_ROLE_STATE_SEPARATED
NATIVE_EDGE_DIGEST_BRIDGE_REQUIRED_AND_EXPLICIT
LEGACY_PROFILE_ORCHESTRATOR_REUSE_FORBIDDEN
NO_IMPLEMENTATION_NO_REGISTRATION_NO_TEST_EXECUTION_NO_FIELD_RUN
```

## Verbindliche Quelle

Einzige Wertquelle ist:

```text
reports/s1rk_four_node_fresh_manifest.json
```

Erwartete Identitaeten:

| Rolle | Wert |
|---|---|
| Schema | `mcm.s1rk.four-node-fresh-manifest.v1` |
| Manifestdigest | `ae7a7356a3e06776a000b6e9fafef75b717944f1d75da62d4418be98cc439c68` |
| Kanteninventardigest | `9961eddd8c8a7ad845c9ab43af23f8ae5380c72ffae06c2e0af202cda49c3529` |
| Geometriedigest | `e0c416cc4aa97a66960640a2ff8fbe5d75edcc1f7a603c66b1efbf09ea820884` |
| Rollenmappingdigest | `16ffec39daf424b73b94ed03b0ee4552e29372ba557b37f194c0d9499c49c1dd` |
| oeffentlicher Frischdigest | `ce6912af2bc94458c2ba4243fa6df7b8b05494d956ef96730f4faf7ec5a8a879` |

Kein Wert darf aus einem historischen Profil, einem Runneroutput oder einem
Default rekonstruiert werden. Fehlende, unbekannte oder abweichende Werte
werden nicht repariert.

## Bestandsaudit der Einfuegepunkte

Fuer das gemeinsame Feld werden unveraendert wiederverwendet:

- `MCMFieldPerception` und `MCMNeuron` aus `mcm_neuron.py`;
- `MCMNeuronLayer` aus `mcm_neuron_layer.py`;
- `ReceptorNeuronDockMap` aus `receptor_contract.py`;
- `SharedFieldDock` und `SharedMCMField` aus `shared_mcm_field.py`.

Fuer rollenprivate native Frischzustaende duerfen unveraendert verwendet
werden:

- `MCMSubstrateArmContract`, `MCMSubstrateMass` und `MCMSubstrateState`;
- `DTS1NodeCapacity`, `DTS1EdgeResource` und `DTS1ResourceAnatomy`;
- `build_zero_w7n_local_baseline`;
- `build_registered_m1_parallel_leak_configuration` und
  `build_zero_m1_parallel_leak_bank`;
- `build_registered_m2_configuration` und `build_empty_m2_buffer`.

Der private `_build_fresh_state` in
`dynamic_substrate_dts1_one_replica_orchestrator.py` ist kein zulaessiger
Einfuegepunkt. Er ist an historische S1-JZ-Profile, Zwei-/Drei-Knoten-
Geometrien und alte Rollen gebunden. Seine Erweiterung wuerde zwei
Registrierungswelten vermischen.

`current_api.py`, Paketexporte, bestehende Adapter, Gleichungsmodule und
Runner bleiben in der naechsten Stufe unveraendert.

## Exaktes Dateibudget

Die nachfolgende Implementierungsstufe darf genau diese vier neuen Dateien
anlegen:

```text
mcm_field_organism/four_node_fresh_manifest.py
mcm_field_organism/four_node_fresh_factory.py
tests/test_four_node_fresh_manifest.py
tests/test_four_node_fresh_factory.py
```

Zulaessige Begleitveraenderungen sind nur Forschungsstandsdokumentation und
Formatkorrekturen innerhalb dieser vier Dateien. Weitere Produktions-,
Konfigurations-, Report- oder Fixturedateien sind gesperrt. Insbesondere
darf das S1-RK-Manifest weder kopiert noch neu geschrieben werden.

## Manifestconsumer-API

`four_node_fresh_manifest.py` erhaelt genau diese oeffentlichen Rollen:

```python
class FourNodeFreshManifestError(ValueError): ...

@dataclass(frozen=True, slots=True)
class FourNodeFreshManifest: ...

def parse_four_node_fresh_manifest(raw_bytes: bytes) -> FourNodeFreshManifest: ...

def load_four_node_fresh_manifest(path: Path) -> FourNodeFreshManifest: ...
```

Der Parser muss:

1. UTF-8 und JSON strikt lesen;
2. alle Schemata, Schluessel, Typen, Listenordnungen und Rollenpositionen
   exakt pruefen;
3. unbekannte Felder ablehnen;
4. alle vier gemeinsamen und alle zwoelf privaten Payloads kanonisch
   re-hashen;
5. die zwei Zustandslosmarkierungen exakt pruefen;
6. den Manifestdigest nach Entfernen nur seines eigenen Feldes reproduzieren;
7. alle in S1-RK gebundenen Queridentitaeten erneut pruefen;
8. eine rekursiv unveraenderliche Sicht liefern.

`load_four_node_fresh_manifest` darf nur Bytes lesen und an den Parser
uebergeben. Es gibt keine Modulimport-Dateioperation, keinen Cache und keinen
prozessglobalen Manifestzustand.

## Frischfabrik-API

`four_node_fresh_factory.py` erhaelt genau diese oeffentlichen Rollen:

```python
class FourNodeFreshFactoryError(ValueError): ...

@dataclass(frozen=True, slots=True)
class FourNodeFreshBundle:
    public_field: SharedMCMField
    model_role: str
    private_state_or_none: object | None
    stateless_marker_or_none: str | None
    registered_private_digest_or_none: str | None

def build_four_node_public_fresh_field(
    manifest: FourNodeFreshManifest,
) -> SharedMCMField: ...

def build_four_node_role_fresh_bundle(
    manifest: FourNodeFreshManifest,
    model_role: str,
) -> FourNodeFreshBundle: ...
```

Die Feldfabrik baut genau vier Knoten in der Manifestreihenfolge mit
`S=0.0`, `H=0.0`, Wahrnehmungstakt `0`, Rezeptorkontakt `0.0`, leeren lokalen
Samples und `last_distribution=None`. Dock, Carrierzuordnung,
Nachbarschaftsoffsets und Identitaeten kommen ausschliesslich aus dem
Manifest. Sie ruft `SharedMCMField.advance` nicht auf.

Jeder Rollenaufruf baut ein neues oeffentliches Feldobjekt und einen neuen
rollenprivaten Zustand. A0 und A1 besitzen ausschliesslich ihre jeweilige
Zustandslosmarkierung. Fuer sie darf kein kuenstlicher Privatstatus entstehen.
Die verbleibenden zwoelf Rollen erhalten genau den registrierten
Privatdigest und eine native oder streng typisierte unveraenderliche
Realisierung ihres Payloads.

Die Fabrik erhaelt weder Ereignis-, Profil-, Refinement-, Replik- noch
A/B/C/D-Expositionsrollen als Eingabe. Das aeussere Rollenmapping darf
niemals in Feld oder Privatstatus eingebettet werden.

## Digestbruecke

Das S1-RK-Kanteninventar und die bestehende native M-Substratklasse verwenden
verschiedene kanonische Praeimages. Deshalb sind zwei Digestrollen zu
unterscheiden:

- der registrierte S1-RK-Kanteninventardigest identifiziert das Manifest;
- `mcm_substrate_edge_inventory_digest(layer)` identifiziert die native
  Layerableitung fuer `MCMSubstrateState`.

Die Fabrik muss zuerst die drei sortierten Kantenpaare semantisch exakt
vergleichen. Erst danach darf sie fuer B3-B6 den nativen Layerdigest in das
native `MCMSubstrateState` einsetzen. Beide Digests muessen getrennt im
Pruefpfad erhalten bleiben. Gleichsetzung, Ersetzung ohne Kantenvergleich
oder Verwendung des `DTS1ResourceAnatomy.edge_inventory_digest` als S1-RK-
Digest ist unzulaessig.

Der registrierte Privatdigest wird weiterhin ueber den unveraenderten
Manifestpayload reproduziert. Er ist nicht der Digest des daraus erzeugten
Python-Objekts.

## Rollenbindung

| Modellrollen | Frischrealisierung |
|---|---|
| A0, A1 | kein Privatstatus; exakte Markierung |
| B1 | unveraenderliche Fixed-Adapter-Kantenhuelle aus dem Manifestpayload |
| B2 | streng typisierte Integrator-Nullwertehuelle |
| B3-B6 | native M-Substratwerte plus explizite Digestbruecke |
| A3, M5 | native W7-N-Nullzustaende mit registrierter Spezifikation |
| M1 | zwei getrennte native W7-N-Nullspuren |
| M2 DELAY, M2 REPLAY | zwei getrennte native leere M2-Puffer |
| M4 | native DTS-1-Ressourcenanatomie plus getrennte registrierte Ratenhuelle |

Die in der Tabelle genannten Hüllen sind lokale unveraenderliche
Wertobjekte in `four_node_fresh_factory.py`; sie sind keine neuen
Gleichungen, Adapter oder Runtimezustandsmaschinen.

## Objekttrennung

Bei zwei Fabrikaufrufen darf kein veraenderliches Objekt gemeinsam benutzt
werden. Das gilt insbesondere fuer Felder, Layer, Knoten, Dockmaps,
Substratmassen, Ressourcenledgers, W7-N-Zustaende, M1-Spuren und M2-Puffer.

Unveraenderliche skalare Werte und Konfigurationswertobjekte duerfen
wertgleich sein. Objektidentitaet darf jedoch nie als Ersatz fuer die
geforderte Repliktrennung dienen. Die Erzeugung von 16 Repliken pro Rolle
gehoert noch nicht zu S1-RL und wird spaeter durch wiederholte Einzelaufrufe
gebunden.

## Fail-Closed-Fehler

Jeder Fehler beendet den Aufruf ohne Teilobjekt. Die Exceptiontexte muessen
genau einen dieser stabilen Codes enthalten:

```text
FRESH_MANIFEST_BYTES_INVALID
FRESH_MANIFEST_SCHEMA_INVALID
FRESH_MANIFEST_SHAPE_INVALID
FRESH_MANIFEST_DIGEST_INVALID
FRESH_MANIFEST_DEPENDENCY_INVALID
FRESH_MANIFEST_ROLE_AXIS_INVALID
FRESH_FACTORY_MODEL_ROLE_INVALID
FRESH_FACTORY_PUBLIC_FIELD_INVALID
FRESH_FACTORY_PUBLIC_PROJECTION_MISMATCH
FRESH_FACTORY_PRIVATE_STATE_INVALID
FRESH_FACTORY_PRIVATE_DIGEST_MISMATCH
FRESH_FACTORY_EDGE_BRIDGE_INVALID
FRESH_FACTORY_OBJECT_SEPARATION_INVALID
```

Es gibt keine Warnungsfortsetzung, Toleranz, Normalisierung unbekannter Werte,
Fallbackrolle oder teilweise Rueckgabe.

## Technisches Testbudget

Die naechste Stufe darf hoechstens 28 fokussierte Unit-Tests definieren:

- hoechstens 12 Consumer-Tests fuer gueltiges Manifest, UTF-8/JSON,
  Schemata, exakte Shapes, unbekannte Felder, Payloaddigests,
  Zustandslosmarkierungen, Rollenachse, Querreferenzen und Manifestdigest;
- hoechstens 16 Fabriktests fuer Nullfeldprojektion, alle 14 Rollen,
  native Zustandsformen, Digestbruecke, unbekannte Rollen,
  A0/A1-Zustandslosigkeit und wiederholte Objekttrennung.

Zulaessige Tests verwenden das vorhandene Manifest nur lesend. Sie fuehren
keinen Feldschritt, keine Gleichung, keinen Baselineadvance, keine
Matrixzelle und keinen Ergebnisvergleich aus. Der allgemeine Bestand darf
erst nach erfolgreichem fokussiertem Testlauf in einer spaeteren eigenen
Stufe ausgefuehrt werden.

## Abnahmekriterien der Implementierungsstufe

Eine spaetere Implementierung ist technisch abnehmbar, wenn und nur wenn:

- das unveraenderte S1-RK-Manifest vollstaendig akzeptiert wird;
- jede Einzelveraenderung am Manifest fail-closed erkannt wird;
- alle 14 Rollen genau einmal adressierbar sind;
- alle Rollen dieselbe oeffentliche Frischprojektion reproduzieren;
- alle zwoelf Privatdigests und zwei Markierungen reproduziert werden;
- native Zustandsobjekte die registrierten Werte ohne neue Parameter tragen;
- beide Kanten-Digestrollen getrennt und durch exakte Kantenidentitaet
  verbunden sind;
- wiederholte Fabrikaufrufe voneinander unabhaengige Objektgraphen liefern;
- kein gesperrtes Modul veraendert und keine Runtime ausgefuehrt wurde.

Diese Kriterien pruefen nur Registrierung, Materialisierung und technische
Isolation. Sie sind kein Baseline-, Funktions- oder Memory-Befund.

## Paketstatus

```text
S1RL_INSERTION_POINTS_BOUND
S1RL_FILE_API_ERROR_AND_TEST_BUDGET_BOUND
FOUR_NODE_GEOMETRY_NOT_REGISTERED
MANIFEST_CONSUMER_NOT_IMPLEMENTED
FRESH_FACTORIES_NOT_IMPLEMENTED
BASELINE_ADAPTERS_NOT_CONNECTED
MANDATORY_224_CELL_PACKAGE_NOT_EXECUTABLE
```

## Genau ein naechster Schritt

Als einziger Anschluss ist zulaessig:

```text
S1-RM - Implementierung des unveraenderlichen S1-RK-Manifestconsumers und
        der gemeinsamen Vier-Knoten-Nullfeldfabrik im S1-RL-Dateibudget
```

S1-RM darf zunaechst nur die beiden Produktionsmodule anlegen und die
Consumer- sowie Nullfeldtests definieren. Rollenprivate Fabriken,
Testausfuehrung, Adapteranschluss, Matrixzellen und Feldlauf bleiben bis zu
einer weiteren Abnahmestufe geschlossen.
