# S1-RO: Statischer rollenweiser Realisierungs-, Typbindungs- und Digestbrueckenvertrag

## Status und Zweck

S1-RO bindet fuer alle 14 S1-RK-Modellrollen die exakte Uebersetzung vom
registrierten Frischpayload in einen vorhandenen nativen Zustand oder ein
kleines unveraenderliches technisches Wertobjekt.

Der Audit implementiert keine Fabrik, veraendert kein Manifest und fuehrt
keinen Test, Adapter, Baselineadvance, Feldschritt oder Matrixfall aus.

Vertragsentscheidung:

```text
FOURTEEN_ROLE_REALIZATION_MAP_COMPLETE
TWO_STATELESS_AND_TWELVE_STATEFUL_ROLES_PRESERVED
NATIVE_TYPES_REUSED_WHERE_PAYLOAD_COMPATIBLE
LOCAL_VALUE_WRAPPERS_BOUND_WHERE_NO_NATIVE_TYPE_EXISTS
EDGE_AND_M2_GEOMETRY_DIGEST_BRIDGES_REQUIRED
LEGACY_S1JZ_PRIVATE_STATE_REUSE_FORBIDDEN
NO_IMPLEMENTATION_NO_TEST_EXECUTION_NO_FIELD_RUN
```

## Verbindliche Eingaben

Jeder spaetere Rollenbau erhaelt ausschliesslich:

```text
FourNodeFreshManifest
model_role
```

Das oeffentliche Feld wird bei jedem Aufruf neu durch
`build_four_node_public_fresh_field` erzeugt. Ereignis, Profil, Refinement,
Replik, A/B/C/D-Expositionsrolle oder Ergebnis duerfen keine Eingabe der
Frischfabrik sein.

Die Rollenpositionen bleiben exakt `01` bis `14`. Die zwoelf privaten
Payloads und zwei Zustandslosmarkierungen kommen nur aus der bereits
validierten Manifestansicht.

## Ziel-API im bestehenden Dateibudget

Die spaetere Implementierung darf ausschliesslich
`mcm_field_organism/four_node_fresh_factory.py` erweitern. Folgende bereits
in S1-RL gebundene Rollen werden vervollstaendigt:

```python
@dataclass(frozen=True, slots=True)
class FourNodeFreshBundle:
    public_field: SharedMCMField
    model_role: str
    private_state_or_none: object | None
    stateless_marker_or_none: str | None
    registered_private_digest_or_none: str | None

def build_four_node_role_fresh_bundle(
    manifest: FourNodeFreshManifest,
    model_role: str,
) -> FourNodeFreshBundle: ...
```

Fuer die typisierte Uebersetzung duerfen in derselben Datei diese lokalen
unveraenderlichen Wertobjekte hinzukommen:

```text
FourNodePrivateFreshState
FourNodeFixedAdapterEdgeRate
FourNodeFixedAdapterState
FourNodeIntegratorEntry
FourNodeIntegratorState
FourNodeSubstrateFreshState
FourNodeM4Rates
FourNodeM4FreshState
```

`FourNodePrivateFreshState` ist die gemeinsame technische Huelle. Sie bindet
Modellrolle, Konfigurationsdigest, nativen Zustand, den unveraenderten
registrierten State-Payload sowie gegebenenfalls beide Seiten einer
Digestbruecke. Sie ist kein Adapter und besitzt keine Updatefunktion.

## Rollenweise Zielbindung

| Pos. | Modellrolle | Zielzustand | Uebersetzung |
|---:|---|---|---|
| 01 | `A0_CURRENT_CONTACT` | `None` | nur exakte Zustandslosmarkierung |
| 02 | `A1_FAST_SH` | `None` | nur exakte Feldzustandsmarkierung |
| 03 | `A2_B1_FIXED_ADAPTER` | `FourNodeFixedAdapterState` | drei typisierte Kantenraten plus Basisrate und Backreaction-Flag |
| 04 | `A2_B2_INTEGRATOR` | `FourNodeIntegratorState` | vier typisierte Nullwerte in Knotenreihenfolge |
| 05 | `A2_B3_LOCAL_LEAKY` | `FourNodeSubstrateFreshState` | nativer M-Zustand mit B3-Arm |
| 06 | `A2_B4_LINEAR_COUPLED` | `FourNodeSubstrateFreshState` | nativer M-Zustand mit B4-Arm |
| 07 | `A2_B5_F3_FULL` | `FourNodeSubstrateFreshState` | nativer M-Zustand mit B5-Arm |
| 08 | `A2_B6_CONST_V` | `FourNodeSubstrateFreshState` | nativer M-Zustand mit B6-Arm und gebundenem CONST-V-Spezifikationsdigest |
| 09 | `A3_NORM` | `W7NLocalBaselineState` | registrierter NORM-Spec, vier Nullwerte |
| 10 | `M1_PARALLEL_LEAK` | `M1ParallelLeakBankState` | registrierte FAST/SLOW-Konfiguration, zwei getrennte Nullspuren |
| 11 | `M2_DELAY` | `M2BoundedBufferState` | registrierter DELAY-Modus, leerer Puffer, native Geometriebruecke |
| 12 | `M2_REPLAY` | `M2BoundedBufferState` | registrierter REPLAY-Modus, leerer Puffer, native Geometriebruecke |
| 13 | `M4_DTS1_T1` | `FourNodeM4FreshState` | native DTS-1-Anatomie plus typisierte registrierte Raten |
| 14 | `M5_DIRECT` | `W7NLocalBaselineState` | registrierter LEAK-Spec, vier Nullwerte |

## A0 und A1

A0 erhaelt exakt:

```text
STATELESS_MARKER:A0_CURRENT_CONTACT:S1RJ
```

A1 erhaelt exakt:

```text
FIELD_ONLY:A1_FAST_SH:S1RJ
```

Fuer beide Rollen gelten:

```text
private_state_or_none = None
registered_private_digest_or_none = None
```

Keine leere Mappinghuelle, kein Nulldigest und kein synthetischer Zustand
duerfen diese Abwesenheit ersetzen.

## B1 und B2

Fuer B1 existiert kein geeigneter allgemeiner nativer Frischzustand. Die
lokale Huelle muss exakt binden:

- `base_rate_per_second=1.0`;
- `backreaction_enabled=True`;
- die drei sortierten Kanten a-b, b-c und c-d;
- `rate_per_second=1.1` je Kante;
- den registrierten S1-RK-Kanteninventardigest.

Fuer B2 bindet die lokale Huelle vier Eintraege node-a bis node-d mit
jeweils `value=0.0`. Sie besitzt keine Feld-, Zeit- oder Historienrolle.

`DTS1CommonIntervalPrivateState` ist fuer beide Rollen kein Zieltyp. Diese
Klasse akzeptiert nur die historischen S1-JN-Kurznamen `DTS1` und `B1` bis
`B6` mit profilgebundenen Payloadschluesseln. Eine Erweiterung wuerde den
neuen Vier-Knoten-Bestand mit der alten Orchestratorregistrierung vermischen.

## B3 bis B6

Jede Rolle erzeugt einen neuen `MCMSubstrateArmContract`, vier neue
`MCMSubstrateMass`-Objekte und einen neuen `MCMSubstrateState`.

Gemeinsam gelten:

```text
eta = 1.0
kappa = 0.5
initial_total_mass = 1.0
masses = 0.25 / 0.25 / 0.25 / 0.25
```

Rollenfest gelten:

| Rolle | `arm_id` | `lambda_sm_per_second` | Zusatzdigest |
|---|---|---:|---|
| B3 | `mcm.s1jt.b3.local-leaky` | 1.0 | `None` |
| B4 | `mcm.s1jt.b4.linear-coupled` | 1.0 | `None` |
| B5 | `mcm.s1jt.b5.full` | 1.0 | `None` |
| B6 | `mcm.s1jt.b6.const-v` | 0.5 | `bd30dd584dd81d447aab6c55f24a99fbbdb89ad116b07ef0b831f65a41443172` |

Der B6-Spezifikationsdigest bleibt in `FourNodeSubstrateFreshState`
ausserhalb des nativen `MCMSubstrateState` erhalten. B3-B5 muessen an dieser
Stelle exakt `None` tragen.

## A3, M1 und M5

A3 waehlt aus `build_w7m_capacity_function_matrix_adapter()` exakt den
registrierten NORM-Spec und erzeugt ueber
`build_zero_w7n_local_baseline(spec, 4)` einen neuen NORM-Zustand.

M5 waehlt aus demselben Adapter exakt den registrierten LEAK-Spec und erzeugt
einen neuen LEAK-Zustand mit vier Nullwerten.

M1 verwendet ausschliesslich:

```text
build_registered_m1_parallel_leak_configuration()
build_zero_m1_parallel_leak_bank(configuration, 4)
```

FAST und SLOW muessen getrennte `W7NLocalBaselineState`-Objekte sein. Die
Konfigurationsdigests muessen den jeweiligen Manifestbindungen entsprechen;
ein Spec darf nicht aus A3, M1 oder M5 in eine andere Rolle uebernommen
werden, auch wenn Modellnamen oder Nullwerte gleich sind.

## M2

M2 verwendet pro Rolle eine neue registrierte Konfiguration und einen neuen
leeren Puffer:

```text
M2_DELAY  -> build_registered_m2_configuration("DELAY")
M2_REPLAY -> build_registered_m2_configuration("REPLAY")
```

Die Modi bleiben getrennt. DELAY startet mit Phase `NOT_APPLICABLE`, REPLAY
mit Phase `CAPTURE`; beide besitzen Cursor null und keine Records.

`build_empty_m2_buffer` berechnet seinen Geometriedigest mit dem bestehenden
REPLACE_S-Compositor-Praeimage. Das S1-RK-Manifest registriert dagegen den
Digest des physischen Geometriepayloads. Beide Werte duerfen nicht
gleichgesetzt werden.

Die M2-Bruecke muss deshalb getrennt erhalten:

```text
registered_physical_geometry_digest
native_m2_geometry_digest
```

Vor der Uebersetzung muessen Feld-ID, Geometrie-ID, Layer-ID,
Knotenidentitaeten, Positionen, Modalitaet, Offsets und Periodizitaet exakt
dem Manifest entsprechen. Die Rueckprojektion in den registrierten
Frischpayload setzt ausschliesslich den registrierten Geometriedigest ein.
Ein Unterschied der beiden Hashwerte ist kein Geometrieunterschied.

## M4

M4 erzeugt neue Instanzen von:

```text
DTS1NodeCapacity
DTS1EdgeResource
DTS1ResourceAnatomy
FourNodeM4Rates
FourNodeM4FreshState
```

Gebunden bleiben vier Kapazitaeten `1.0`, drei Kanten mit jeweils
`conductive_bound=0.2` und `refractory=0.1` sowie die Raten
`binding_rate=0.4`, `recovery_rate=0.2` und `turnover_rate=0.3`.

Die abgeleiteten lokalen freien Werte muessen
`0.85/0.70/0.70/0.85` ergeben. Global muessen Kapazitaet `4.0`, freie
Ressource `3.1`, leitend gebundene Ressource `0.6`, refraktaere Ressource
`0.3` und Residuum null vorliegen.

`candidate_sidecar_digest_or_null` bleibt exakt `None`. Es darf kein
zusatzlicher Kandidatenstatus entstehen.

## Kanten-Digestbruecke

Fuer B3-B6 und M4 werden drei technische Digestrollen unterschieden:

1. S1-RK-Kanteninventardigest ueber den registrierten Payload;
2. nativer M-Substrat-Layerdigest aus
   `mcm_substrate_edge_inventory_digest(layer)`;
3. bei M4 der anatomieeigene Digest aus
   `DTS1ResourceAnatomy.edge_inventory_digest`.

Vor jeder Bruecke muessen alle drei Kanteninventare als sortierte
Endpunktpaare exakt gleich sein. Erst danach darf:

- B3-B6 den nativen Layerdigest in `MCMSubstrateState` tragen;
- M4 seinen anatomieeigenen Digest behalten;
- die registrierte Rueckprojektion den S1-RK-Digest einsetzen.

Keiner der drei Digests darf den anderen ueberschreiben oder als dessen
direkte Reproduktion ausgegeben werden.

## Rueckprojektionspflicht

Jeder zustandsbehaftete Rollenbau muss nach der nativen Konstruktion den
registrierten `state_payload` erneut erzeugen. Bei einer Digestbruecke wird
nur der registrierte Digest an seiner registrierten Payloadposition
eingesetzt. Danach werden der vollstaendige private Payload und sein bereits
gebundener Privatdigest reproduziert.

Die Rueckprojektion ist nur eine technische Gleichheitspruefung. Sie ist
keine Serialisierung eines spaeter fortgeschrittenen Zustands und keine
Adapterfunktion.

## Objekttrennung

Jeder Aufruf erzeugt neu:

- oeffentliches Feld, Layer, Dock, Knoten und Wahrnehmungen;
- private Huelle und alle rollenprivaten Wertobjekte;
- M-Arme und Massen;
- W7-N-Zustaende und M1-Spuren;
- M2-Konfiguration und Puffer;
- M4-Kapazitaeten, Kantenressourcen, Anatomie und Raten.

Nur rekursiv unveraenderliche Manifestwerte duerfen geteilt werden. A0 und
A1 teilen keinen synthetischen Privatstatus. Replikanzahl und
Matrixmaterialisierung bleiben ausserhalb dieses Vertrags.

## Fail-Closed-Bindung

Die in S1-RL registrierten Fehlercodes bleiben unveraendert. Sie werden
rollenweise so verwendet:

| Fehlerklasse | Code |
|---|---|
| unbekannte oder doppelte Modellrolle | `FRESH_FACTORY_MODEL_ROLE_INVALID` |
| oeffentliches Feld oder Manifestbezug ungueltig | `FRESH_FACTORY_PUBLIC_FIELD_INVALID` |
| oeffentliche Projektion abweichend | `FRESH_FACTORY_PUBLIC_PROJECTION_MISMATCH` |
| Zieltyp, Konfiguration oder Rueckprojektion ungueltig | `FRESH_FACTORY_PRIVATE_STATE_INVALID` |
| privater Payload- oder Digest-Roundtrip abweichend | `FRESH_FACTORY_PRIVATE_DIGEST_MISMATCH` |
| Kantenpaare oder einer der Kanten-Digestpfade ungueltig | `FRESH_FACTORY_EDGE_BRIDGE_INVALID` |
| M2-Geometrieinventar oder Geometrie-Digestpfad ungueltig | `FRESH_FACTORY_PRIVATE_STATE_INVALID` |
| Objektidentitaet zwischen getrennten Bauten geteilt | `FRESH_FACTORY_OBJECT_SEPARATION_INVALID` |

Es gibt keine Teilrueckgabe, Reparatur, Defaultkonfiguration, Rollenfallback
oder Warnungsfortsetzung.

## Verbleibendes Testbudget

Im bestehenden `tests/test_four_node_fresh_factory.py` duerfen hoechstens
zehn weitere Testmethoden hinzukommen. Damit wird das S1-RL-Limit von 16
Fabriktests vollstaendig, aber nicht ueberschritten.

Die zehn Testrollen muessen gemeinsam abdecken:

- alle 14 Modellrollen und ihre Positionsordnung;
- A0/A1-Zustandslosigkeit;
- B1/B2-Zielwerte;
- B3-B6-Arme, Massen und Kantenbruecke;
- A3/M1/M5-Zustandstypen und getrennte Nullwerte;
- beide M2-Modi und die Geometriebruecke;
- M4-Anatomie, lokale und globale Bilanz;
- Privatdigest-Roundtrip aller zwoelf Rollen;
- unbekannte Rolle und manipulierte Brueckenwerte;
- getrennte Objektgraphen bei wiederholter Erzeugung.

S1-RO definiert diese Tests nicht und fuehrt nichts aus.

## Technische Aussagegrenze

S1-RO bindet nur Frischzustandsmaterialisierung. Die native Konstruktion
eines Nullzustands bestaetigt weder die spaetere Adapteranschlussfaehigkeit
noch eine Baselinefunktion, Felddynamik oder hypothetische MCM-Memory.

## Paketstatus

```text
S1RO_FOURTEEN_ROLE_TYPE_MAP_BOUND
EDGE_AND_M2_GEOMETRY_BRIDGES_BOUND
PRIVATE_ROLE_FACTORY_NOT_IMPLEMENTED
PRIVATE_ROLE_TESTS_NOT_DEFINED_OR_EXECUTED
BASELINE_ADAPTERS_NOT_CONNECTED
MANDATORY_224_CELL_PACKAGE_NOT_EXECUTABLE
```

## Genau ein naechster Schritt

Als einziger Anschluss ist zulaessig:

```text
S1-RP - Implementierung der 14 Rollenbundle, beider Digestbruecken und der
        hoechstens zehn verbleibenden fokussierten Fabriktests
```

S1-RP darf nur `four_node_fresh_factory.py` und
`test_four_node_fresh_factory.py` aendern. Testausfuehrung,
Adapteranschluss, Matrixzellen und Feldlauf bleiben gesperrt.
