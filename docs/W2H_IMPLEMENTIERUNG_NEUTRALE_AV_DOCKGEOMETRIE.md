# W2-H: Implementierung der neutralen AV-Dockgeometrie

Stand: 2026-08-09

Entscheidung: `NEUTRAL_AV_DOCK_GEOMETRY_SPLIT_COMPATIBLY`

Implementierung: ja

Formaler Forschungslauf: nein

## Auftrag

W2-H trennt die von der aktiven AV-Runtime benoetigte Dockgeometrie aus dem
gemischten Capturemodul `finite_audio_video_field_run`:

```text
ORTHOGONAL_FIELD_SAMPLE_OFFSETS
audio_video_dock_anatomies
```

## Umsetzung

Das neue Modul `audio_video_field_geometry` besitzt die Geometriekonstante,
den Dockaufbau und technisch den bisherigen `FiniteAudioVideoFieldError`.
Der Fehlervertrag musste mitverschoben werden, damit die Geometriefunktion
keinen Kreisimport erzeugt und bestehende Ausnahmeidentitaet behaelt.

`finite_audio_video_field_run` reexportiert alle drei Namen identisch. Die
aktive `audio_video_neutral_field_runtime` importiert Konstante und Funktion
direkt aus der neuen Grenze. Capturefunktion, Capture-Ergebnis und
Captureabhaengigkeiten verbleiben im bisherigen Modul.

Konstante und Geometriefunktion sind additiv in `current_api` aufgenommen:

```text
124 neutrale Kernexporte
16 getrennte F3-Referenzexporte
140 eindeutige Exporte insgesamt
```

## Architekturwirkung

Der manifestgenaue statische Kernimportgraph umfasst:

```text
direkte Kern-Ursprungsmodule: 28
transitiv erreichte Module:    36
lokale Importkanten:           95
finite_audio_video_field_run: nicht erreicht
audio_video_field_geometry:   erreicht
```

Die aktive Geometriekante lautet:

```text
audio_video_neutral_field_runtime -> audio_video_field_geometry
```

## Verifikation

```text
92 passed
322 subtests passed
Python-Kompilierung erfolgreich
Konstanten-, Funktions- und Fehleridentitaet erhalten
Capture- und Ergebnisrollen aus Geometriegrenze ausgeschlossen
```

Pytest meldet weiterhin die bestehende Cache-Warnung fuer `.pytest_cache`.
Sie beeinflusst die bestandenen Tests nicht.

## Verwendete Quellen

- bestehendes `finite_audio_video_field_run`;
- aktive Importstelle in `audio_video_neutral_field_runtime`;
- Paket-Root und `current_api`;
- fokussierte Geometrie-, Capture-, Runtime- und Manifesttests;
- manifestgenauer statischer Python-AST-Importgraph.

## Aussagegrenze

W2-H ist eine kompatible Architekturtrennung. Die technischen Tests verwenden
synthetische kontrollierte Quellen; es wurde kein Browser gestartet und keine
Kamera, kein Live-Mikrofon oder andere physische Sensorik aktiviert. Die
Umsetzung belegt kein Memory, Lernen, Feldzeit, Organisation, Semantik,
Selbstregulation oder KI. Lauf 197 bleibt unberuehrt.

## Bester naechster Schritt

W2-I trennt die neutralen Vertragsenums `EvidenceLevel` und
`RuntimePermission` aus `architecture_readiness` von dessen passivem
Architekturplan.

Verbindlich:

1. Die beiden Enums werden in eine eigene neutrale Vertragsgrenze verschoben.
2. `architecture_readiness` reexportiert beide Klassen identisch.
3. `receptor_process_contract` importiert direkt aus der neuen Grenze.
4. Planungsdaten und Architekturbewertung bleiben ausserhalb des neutralen
   Vertragsmoduls.
5. Identitaets-, Vertrags-, Manifest- und Importgraphtests muessen bestehen.

## Spaeterer Umsetzungsstand W2-I

W2-I ist am 2026-08-09 kompatibel abgeschlossen worden. `EvidenceLevel` und
`RuntimePermission` liegen jetzt in `architecture_contract`; der neutrale
Kern erreicht `architecture_readiness` nicht mehr. Damit sind alle vier in
W2-D lokalisierten gemischten Modulgrenzen getrennt.
