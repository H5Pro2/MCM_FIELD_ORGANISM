# S1-DD: E1 eingefrorener transienter Probeoperator

## Status

Der in S1-DC geforderte private transiente Probeoperator und seine feste
Adapterbaseline sind implementiert und synthetisch abgenommen. Es wurde
keine AB/BA-Historie erzeugt, kein Browser gestartet, kein Forschungsrunner
ausgefuehrt und kein Ergebnisreport geschrieben.

## Implementierte Dateien

```text
mcm_field_organism/e1_frozen_transient_probe.py
tests/test_e1_frozen_transient_probe.py
```

Bestehende synchrone Probe-, neutrale Runtime-, S1-DB- und API-Dateien
bleiben unveraendert. Die neuen Rollen werden weder aus `__init__.py` noch
aus `current_api.py` exportiert.

## Eingefrorener transienter E1-Operator

```text
advance_frozen_e1_fast_shared_field_transient(...)
```

Der Operator:

1. validiert Feld, E1-Geometrie, transienten Handoff und Konfiguration;
2. bildet genau einen Adapter aus dem E1-Zustand vor Probestart;
3. verwendet diesen Adapter unveraendert fuer alle geordneten
   Kontaktabschluesse der Probe;
4. entwickelt ausschliesslich S/H;
5. gibt dasselbe E1-Zustandsobjekt unveraendert zurueck.

Es gibt waehrend der Probe keine E1-Bindung, Freigabe,
Ressourcenwiederverwendung oder zustandsabhaengige Adapteraktualisierung.

## Feste Adapterbaseline

```text
advance_fixed_e1_adapter_fast_shared_field_transient(...)
```

Diese Rolle verwendet denselben transienten Feldpfad ohne E1-Zustandsrolle.
Sie prueft vor der Feldentwicklung, dass die Basisrate des Adapters exakt zu
`1 / response_time_seconds` der Probe passt. Ein unter einer anderen
S/H-Zeitkonfiguration erzeugter Adapter wird abgewiesen.

Sind alle Kantenraten gleich der neutralen Basisrate, delegieren beide
Operatoren direkt an `advance_neutral_fast_shared_field_transient(...)`.
Dadurch bleiben Ablation, neutraler E1-Zustand und Nullgain bitgenau P0.

## Aktiver fester Feldpfad

Bei nichtuniformen aktiven Kantenraten wird der symmetrische gewichtete
E1-Generator genau einmal gebildet. Die vorhandenen geordneten
Punktkontakte, S/H-Nachhallentwicklung und optionale Dissipation werden
unveraendert in diesem festen Generator integriert. Gleichzeitige Audio-
und Videoabschluesse bleiben eine gemeinsame Ereignisgruppe.

## Fokussierte Abnahme

Acht neue S1-DD-Tests bestehen:

1. Der E1-Zustand bleibt objekt- und wertidentisch.
2. Ablation ist bitgenau P0.
3. Ein neutraler aktiver E1-Zustand ist bitgenau P0.
4. Aktiver E1-Probeausgang ist bitgenau die feste Adapterbaseline.
5. Ein nichtuniformer aktiver Adapter veraendert das Feld gegen Ablation.
6. Nullgain ist bitgenau Ablation.
7. Gleichzeitige Modalitaeten sind gegen Deklarationsreihenfolge invariant.
8. Falsche Adapterbasisrate und ungueltiger Schalter brechen ab.
9. Eingaben bleiben unveraendert und alle Rollen bleiben privat.

Der gemeinsame relevante Verbund besteht mit:

```text
92 tests
OK
```

Er umfasst E1-Zustand, gewichteten Adapter, synchrone und transiente
Kopplung, synchrone und transiente eingefrorene Probe, neutral-asynchronen
Feldpfad, schnellen Nachhall, kontrollierte AV-Testwelt und die aktive
API-Grenze.

## Begrenzter Befund

```text
FROZEN_TRANSIENT_E1_PROBE_READY
```

Der Befund zeigt nur, dass ein bereits vorhandener E1-Zustand waehrend einer
asynchronen AV-Probe technisch eingefroren, ablatierbar und exakt gegen
seinen festen Adapter kontrolliert werden kann.

## Aussagegrenze

S1-DD erzeugt keine Geschichte und prueft keine history-spezifische Wirkung.
Es belegt weder Einpraegung noch Vergessen, Rekonstruktion, MCM-Memory,
inneren Kontext, Semantik, Organisation, Topologie, Selbstregulation oder
KI.

## Bester naechster Schritt

S1-DE implementiert ausschliesslich den privaten AB/BA-Sequenz-Permutator
aus S1-DC. Er muss auf bereits reduzierter Rezeptorebene Payload-Multiset,
Carrier, Source-Supports, Ereigniszahl, Organismus-Zeitslots, Eingangsmasse
und Energie exakt erhalten. Zunaechst nur Quellenbildung und synthetische
Vertragspruefung; noch keine E1-Historie und keine Probe.

S1-DE ist inzwischen implementiert und mit 7 fokussierten sowie 107
relevanten `unittest`-Tests abgenommen. Siehe
`S1DE_E1_REDUZIERTE_AV_HISTORY_PERMUTATION.md`.
