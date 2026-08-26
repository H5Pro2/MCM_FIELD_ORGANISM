# W2-G: Implementierung der operativen Handoffgrenze

Stand: 2026-08-09

Entscheidung: `OPERATIONAL_HANDOFF_SPLIT_COMPATIBLY`

Implementierung: ja

Formaler Forschungslauf: nein

## Auftrag und Rollentrennung

W2-G trennt die von aktiven Kernruntimes benoetigten Handoff-Rollen aus dem
gemischten Modul `receptor_proposal_handoff_audit`.

Operativ und jetzt in `receptor_proposal_handoff`:

```text
ReceptorProposalHandoffError
ReceptorProposalCompletionGroup
ReceptorProposalBatch
ReceptorProposalHandoff
handoff_receptor_completion_groups
```

Passiv und weiterhin in `receptor_proposal_handoff_audit`:

```text
ProposalSegmentationComparison
synthetische Vergleichssequenzen und Schritte
run_receptor_proposal_handoff_audit
receptor_proposal_handoff_audit_public_roles
```

## Umsetzung

`neutral_asynchronous_field_runtime` und `transient_dock_trajectory`
importieren direkt aus der neuen Grenze. Das alte Auditmodul importiert und
reexportiert dieselben Klassen und dieselbe Funktion. Alte Modul- und
Rootimporte bleiben dadurch objektidentisch.

Die fuenf operativen Namen sind additiv in `current_api` aufgenommen:

```text
122 neutrale Kernexporte
16 getrennte F3-Referenzexporte
138 eindeutige Exporte insgesamt
```

## Architekturwirkung

```text
direkte Kern-Ursprungsmodule: 27
transitiv erreichte Module:    36
lokale Importkanten:          100
receptor_proposal_handoff_audit: nicht erreicht
receptor_proposal_handoff:       erreicht
```

Aktive Kanten:

```text
neutral_asynchronous_field_runtime -> receptor_proposal_handoff
transient_dock_trajectory -> receptor_proposal_handoff
```

## Verifikation

```text
84 passed
316 subtests passed
Python-Kompilierung erfolgreich
Klassen- und Funktionsidentitaet erhalten
passive Auditrollen aus operativer Grenze ausgeschlossen
```

Pytest meldet weiterhin die bestehende Cache-Warnung fuer `.pytest_cache`.
Sie beeinflusst die bestandenen Tests nicht.

## Verwendete Quellen

- bestehendes `receptor_proposal_handoff_audit`;
- aktive Nutzer `neutral_asynchronous_field_runtime` und
  `transient_dock_trajectory`;
- Paket-Root und `current_api`;
- fokussierte Handoff-, Runtime-, Trajektorien- und Manifesttests;
- manifestgenauer statischer Python-AST-Importgraph.

## Aussagegrenze

W2-G ist eine kompatible Architekturtrennung. Es wurden keine Medien oder
Testwelten ausgefuehrt, kein Browser gestartet und keine Kamera, kein
Live-Mikrofon oder andere physische Sensorik aktiviert. Die Umsetzung belegt
kein Memory, Lernen, Feldzeit, Organisation, Semantik, Selbstregulation oder
KI. Lauf 197 bleibt unberuehrt.

## Bester naechster Schritt

W2-H trennt die neutrale AV-Dockgeometrie
`ORTHOGONAL_FIELD_SAMPLE_OFFSETS` und `audio_video_dock_anatomies` aus
`finite_audio_video_field_run` von dessen Capturelauf und Ergebnisrollen.

Verbindlich:

1. Die Geometrie wird ohne Capture-, Runner- oder Ergebnisrollen in ein
   eigenes neutrales Modul verschoben.
2. `finite_audio_video_field_run` reexportiert beide Namen identisch.
3. `audio_video_neutral_field_runtime` importiert direkt aus der neuen Grenze.
4. Geometrie-, Runtime-, Identitaets- und Manifesttests muessen bestehen.
5. Der neutrale Kern darf `finite_audio_video_field_run` danach nicht mehr
   transitiv erreichen.

## Spaeterer Umsetzungsstand W2-H

W2-H ist am 2026-08-09 kompatibel abgeschlossen worden. Die neutrale
AV-Dockgeometrie liegt jetzt in `audio_video_field_geometry`; der neutrale
Kern erreicht `finite_audio_video_field_run` nicht mehr.
