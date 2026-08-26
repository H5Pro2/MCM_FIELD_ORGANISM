# S1-BH: Maschinenlesbarer aktiver Feldzustandsvertrag

## Status

Additive technische API-Beschreibung. Keine Feldfortschreibung, keine neue
Mechanik, kein Forschungslauf und kein Memory-, Substrat- oder KI-Befund.

## Zweck

`mcm_field_organism.current_api.active_field_state_contract()` liefert den in
S1-BG beschriebenen aktiven Feldzustandsvertrag als JSON-kompatiblen
Python-Wert.

Die Funktion liest keine Testwelt, erzeugt keinen Feldzustand und schreibt
keine Datei. Sie beschreibt nur die aktuell importierte technische
Oberflaeche.

## Ausgabe

Der Rueckgabewert enthaelt:

```text
contract_id
modalities
active_export_names
receptor_sequence_fields
timed_receptor_frame_fields
handoff_fields
field_run_fields
snapshot
reference_manifests
memory_claim
```

`snapshot` bindet das neutrale Schema 1, seine vier Root-Schluessel und die
beiden nur optionalen Referenzzustandsfelder. `reference_manifests` fuehrt
passive Vergleiche, C_i, F3 und S1B getrennt auf. `memory_claim` ist fest
`false`.

## Keine zweite Wahrheit

Die Ausgabe wird bei jedem Aufruf zusammengesetzt aus:

1. `CURRENT_CONTROLLED_FIELD_EXPORTS` und den vier Referenzmanifesten;
2. `dataclasses.fields(...)` der bestehenden Sequenz-, Handoff- und
   Feldlaufvertraege;
3. der gemeinsamen AV-Modalitaetskonstante;
4. denselben Schema-1- und Snapshot-Schluesselkonstanten, die Validierung,
   Serialisierung und Snapshotaufbau verwenden.

Es existiert keine separat gepflegte Kopie der 129 aktiven Exportnamen oder
der Dataclass-Feldlisten.

## Zentralisierte Vertragswerte

Die zuvor mehrfach hart codierte Modalitaetsfolge
`("auditory", "visual")` wird nun durch `AUDIO_VIDEO_MODALITY_IDS` getragen.

Die Snapshotgrenze verwendet nun gemeinsam:

```text
NEUTRAL_SNAPSHOT_SCHEMA_VERSION
F3_SNAPSHOT_SCHEMA_VERSION
S1B_SNAPSHOT_SCHEMA_VERSION
NEUTRAL_SNAPSHOT_ROOT_KEYS
SNAPSHOT_REFERENCE_STATE_FIELDS
```

Diese Konstanten aendern weder Schemabedeutung noch JSON-Format.

## API-Grenze

`active_field_state_contract` und sein in S1-BI ergaenzter technischer Digest
sind Namen in
`CURRENT_CONTROLLED_FIELD_EXPORTS`. Die Funktion beschreibt nur den aktiven
Kern; sie aktiviert keinen der in der Ausgabe aufgelisteten Referenzpfade.

## Verifikation

Der fokussierte Verbund prueft:

```text
JSON-Roundtrip der gesamten Beschreibung
direkte Gleichheit mit allen API-Manifesten
direkte Gleichheit mit den Dataclass-Feldlisten
neutrales Schema 1 sowie F3- und S1B-Schemas
beide aktiven AV-Consumer
gemeinsame neutrale AV-Feldruntime
```

Ergebnis: `67 passed`, `355 subtests passed`. Die bekannte lokale
Pytest-Cachewarnung beeinflusst den Befund nicht.

## Aussagegrenze

Der Vertrag ist technische Selbstauskunft der Software. Er ist keine
Selbstwahrnehmung des Feldes, kein innerer Kontext und kein MCM-Memory.

## Bester naechster Schritt

Der deterministische SHA-256-Digest der kanonisch JSON-kodierten
Vertragsausgabe ist inzwischen in S1-BI umgesetzt. Er zeigt nur Versions- und
Schnittstellendrift an.

