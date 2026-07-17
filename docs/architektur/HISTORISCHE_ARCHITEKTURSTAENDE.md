# Historische Architekturstände

## Zweck

Die Dokumente in diesem Abschnitt beschreiben frühere Forschungsstände mit
getrennten auditiven, visuellen oder taktilen MCM-Feldern, einem
`MCMDistributor` und einer nachgeschalteten multimodalen Feldkonstellation.

Diese Architektur ist durch das
[gemeinsame MCM-Feld](024_GEMEINSAMES_MCM_FELD_ARCHITEKTUR.md) ersetzt.
Die alten Texte bleiben nur erhalten, damit frühere Methodiken und Befunde
inhaltlich nachvollziehbar und ausführbar bleiben.

## Nicht mehr aktuelle Architekturverträge

- [001: Sensorspezifischer MCM-Schnittstellenvertrag](001_SENSORSPEZIFISCHER_MCM_SCHNITTSTELLENVERTRAG.md)
- [002: Gemeinsamer MCM-Strang](002_GEMEINSAMER_MCM_STRANG_VERTRAG.md)
- [003: Auditive Rezeptor-zu-Feld-Grenze](003_AUDITIVE_REZEPTOR_ZU_FELD_GRENZE.md)
- [004: MCM-Verteiler](004_MCM_VERTEILER_VERTRAG.md)
- [005: Multimodaler Musterprüfer](005_MULTIMODALER_MUSTERPRUEFER_VERTRAG.md)
- [006: Früherer technischer Entwicklungsplan](006_TECHNISCHER_ENTWICKLUNGSPLAN.md)
- [007 bis 010: frühere Mehrfeld-Grenzen](007_REFLEXIONS_UND_OFFLINE_GRENZE.md)
- [013: Verbundene Mehrfeld-Architektur](013_VERBUNDENE_MCM_FELDARCHITEKTUR.md)
- [018 bis 023: Forschungsgrenzen auf Basis der früheren Feldanatomie](018_MINIMALER_SIMULIERTER_EFFEKTORVERTRAG.md)

## Historische Runtime

Die Module `sensor_mcm_field.py`, `mcm_distributor.py`,
`multimodal_pattern_checker.py`, `multimodal_constellation_trace.py` und
`visual_mcm_interface.py` sind historische Versuchsbaselines. Sie werden von
älteren Tests direkt importiert, aber nicht vom aktuellen Paket-API angeboten.

Neue Runtime-Arbeit darf nur über `receptor_contract.py`,
`receptor_distributor.py`, `shared_mcm_field.py` und
`finite_multimodal_field_run.py` in das gemeinsame Feld gelangen.
