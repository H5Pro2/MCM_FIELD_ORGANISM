# S1-BG: Geraeteneutrale Zustandsbeschreibung des aktiven AV-Feldpfads

## Status

Verbindliche technische Zustandsbeschreibung aus vorhandenen API-, Zeit-,
Handoff- und Snapshotvertraegen. Keine neue Runtime, keine neue Mechanik,
kein Forschungslauf und kein Memory-, Substrat- oder KI-Befund.

## Zweck

Ein externer technischer Verbraucher soll den aktuellen Feldpfad verstehen,
ohne historische Forschungszweige, Kamera- oder Mikrofonadapter und interne
Runner kennen zu muessen.

Die Beschreibung beginnt nach der Quellenerfassung bei reduzierten
Rezeptorzustaenden. Ob diese aus kontrollierten synthetischen AV-Frames oder
aus kontrollierten PNG-/PCM-Payloads stammen, ist fuer den nachfolgenden
Feldpfad unerheblich.

## Kanonischer aktiver Pfad

```text
kontrollierte audiovisuelle Quelle
-> modalitaetseigene Rezeptorreduktion
-> ReceptorTimeSequence (auditory, visual)
-> gemeinsamer Organismusuhr-Horizont
-> ReceptorProposalHandoff
-> transiente Docks und Neuroneneingaben
-> neutrales gemeinsames S/H-Feld
-> SharedMCMFieldSnapshot Schema 1
```

## 1. Eingangsvertrag

Jede Modalitaet liefert genau eine `ReceptorTimeSequence`:

| Feld | Bedeutung |
|---|---|
| `modality_id` | technische Herkunft `auditory` oder `visual` |
| `geometry_id` | Identitaet der Rezeptorgeometrie |
| `clock_id` | gemeinsame technische Organismusuhr |
| `frames` | geordnete reduzierte Rezeptorzustaende |

Jeder `OrganismTimedReceptorFrame` enthaelt genau:

```text
frame       = reduzierter ReceptorContactFrame
field_time  = abgeschlossenes CommonFieldTime-Intervall
```

Rohbilder, PCM-Chunks, Dateipfade, Browserobjekte und Geraetehandles gehoeren
nicht zu diesem Vertrag.

## 2. Geometriegrenze

Geraeteneutral bedeutet nicht geometriefrei. Beim Aufbau eines neuen Feldes
muss die deklarierte visuelle Gittergeometrie vorliegen, damit Docks und
lokale Feldorte eindeutig erzeugt werden koennen. Die aktuelle API erhaelt
diese Geometrie ueber einen `LocalChannelGridReceptor`.

Das ist keine Quellensonderbehandlung: Synthetische und Browser-Testwelt-
Zufuhr verwenden denselben Rezeptortyp und dieselbe
`audio_video_dock_anatomies`-Funktion. Nach dem Feldaufbau bleibt die
Geometrie im Feld und Snapshot erhalten.

## 3. Zeit- und Handoffvertrag

Alle Sequenzen und Feldschritte muessen dieselbe `clock_id` verwenden.
Rezeptorintervalle duerfen innerhalb einer Sequenz nicht ueberlappen oder
rueckwaerts laufen.

`ReceptorProposalHandoff` dokumentiert:

| Feld | Invariante |
|---|---|
| `clock_id` | eine gemeinsame Organismusuhr |
| `modality_ids` | erhaltene technische Modalitaeten |
| `batches` | geordnete Abschlussgruppen je Feldschritt |
| `source_event_count` | Anzahl eindeutiger Quellsupports |
| `assigned_event_count` | genau einmal zugewiesene Supports |
| `every_in_horizon_event_assigned_once` | muss wahr sein |
| Vor-/Nachhorizont-IDs | muessen im gebundenen Lauf leer sein |

Der Handoff reduziert, fusioniert oder interpretiert keine Inhalte.

## 4. Aktiver Feldzustand

`NeutralAsynchronousFieldRun` enthaelt:

```text
field                 = ein SharedMCMField
handoff               = vollstaendiger technischer Uebergabebeleg
source_support_count  = Anzahl eindeutiger Weltkontakte
```

Der neutrale Feldzustand traegt:

```text
S = aktuelle schnelle Aktivierung
H = optionale schnelle passive Nachhallspur
```

H folgt der Aktivierung einseitig und ist keine Praegung, kein Lernen und
kein Memorysubstrat.

## 5. Snapshotvertrag

Ohne expliziten Referenzarm gilt ausschliesslich
`SharedMCMFieldSnapshot` Schema 1:

```text
schema_version
layer
docks
last_distribution
```

`layer` enthaelt die aktuelle S/H-Neuronenschicht. `docks` erhaelt die
Rezeptorgeometrie. `last_distribution` erhaelt die letzte abgeschlossene
technische Zeit- und Kontaktgrenze.

Nicht enthalten sind:

```text
Rohpayloads oder Quelldateien
Labels, Bedeutung oder Reward
C_i-Zustand
F3-substrate
S1B-development
Memory- oder Episodenobjekte
```

Restore erzeugt eine unabhaengige technische Feldinstanz mit identischem
Snapshotdigest und identischer Fortsetzung bei gleichem spaeterem Eingang.

## 6. Oeffentliche API-Grenze

Der aktive Kern wird durch 129 Namen in
`CURRENT_CONTROLLED_FIELD_EXPORTS` beschrieben. Passive Auswertung und die
Referenzpfade bleiben getrennt:

```text
PASSIVE_COMPARISON_EXPORTS
CI_REFERENCE_EXPORTS
F3_REFERENCE_EXPORTS
S1B_REFERENCE_EXPORTS
```

Ihre Importierbarkeit ueber `current_api` macht sie nicht zu Bestandteilen
des neutralen aktiven Zustands.

## 7. Kompakte Maschinenlesart

```text
contract_id: mcm.active_av_field_state.v1
modalities: auditory, visual
source_boundary: reduced_receptor_sequences
clock: one_explicit_organism_clock
handoff: every_unique_in_horizon_support_exactly_once
field: one_shared_neutral_s_h_layer
snapshot_schema: 1
raw_payload_retention: false
reference_state_attachment: false
memory_claim: false
```

## Aussagegrenze

Der Vertrag beschreibt technische Feldaufnahme und Zustandsfortsetzung. Er
belegt keine Feldwahrnehmung im psychologischen Sinn, keine relative
Feldzeit, keinen inneren Kontext, keine Semantik und kein MCM-Memory.

## Bester naechster Schritt

Die Zustandsgrenze ist nun kompakt dokumentiert. Der kleine
maschinenlesbare Beschreibungswert ist inzwischen in S1-BH direkt aus
Manifesten, Dataclass-Feldern und gemeinsam verwendeten Vertragskonstanten
umgesetzt.
