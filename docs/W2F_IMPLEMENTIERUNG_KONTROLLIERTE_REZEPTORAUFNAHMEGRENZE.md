# W2-F: Implementierung der kontrollierten Rezeptoraufnahmegrenze

Stand: 2026-08-09

Entscheidung: `CONTROLLED_RECEPTOR_CAPTURE_SPLIT_COMPATIBLY`

Implementierung: ja

Formaler Forschungslauf: nein

## Auftrag

W2-F trennt die kontrollierte Funktion
`capture_timed_audio_video_receptor_sequences` aus dem gemischten Capture-
und Alignment-Auditmodul `receptor_time_alignment`.

## Umsetzung

Das neue Modul `mcm_field_organism.controlled_receptor_capture` besitzt jetzt:

```text
Clock
capture_timed_audio_video_receptor_sequences
privater Sequenzordnungshelfer
```

Es besitzt die fuer die kontrollierte Aufnahme erforderlichen
Quellenprotokolle, Rezeptoren, Parallelisierung und Umwandlung in reduzierte
Zeitframes. Es besitzt keine Alignment-Auditklasse und keine Auditfunktion.

`receptor_time_alignment` importiert und reexportiert die Capturefunktion
weiterhin. Paket-Root, alter Modulpfad, neue Modulgrenze und
`audio_video_neutral_field_runtime` verweisen dadurch auf dasselbe
Funktionsobjekt.

## Architekturwirkung

`audio_video_neutral_field_runtime` importiert die Capturefunktion jetzt
direkt aus `controlled_receptor_capture`. Der neutrale `current_api`-Kern
erreicht das gemischte Modul `receptor_time_alignment` damit nicht mehr.

Der manifestgenau aktualisierte statische Kernimportgraph umfasst:

```text
neutrale Manifestrollen:       117
direkte Kern-Ursprungsmodule:   26
transitiv erreichte Module:     36
lokale Importkanten:           100
receptor_time_alignment:     nicht erreicht
```

Die kontrollierte Restkante lautet jetzt ausschliesslich:

```text
audio_video_neutral_field_runtime -> controlled_receptor_capture
```

## Verifikation

```text
82 passed
301 subtests passed
Python-Kompilierung erfolgreich
Capturefunktionsidentitaet erhalten
Alignment-Audit aus neuer Capturegrenze ausgeschlossen
```

Pytest meldet weiterhin eine bestehende Cache-Warnung fuer `.pytest_cache`.
Sie beeinflusst die bestandenen Tests nicht.

## Verwendete Quellen

- bestehende Capturefunktion in `receptor_time_alignment`;
- direkte Importstelle in `audio_video_neutral_field_runtime`;
- Paket-Root-Reexport;
- fokussierte Capture-, Alignment-, Zeitmodell-, Runtime- und Manifesttests;
- manifestgenauer statischer Python-AST-Importgraph.

## Aussagegrenze

W2-F ist eine kompatible Architekturtrennung. Die technischen Tests verwenden
synthetische kontrollierte Quellen; es wurde kein Browser gestartet und keine
Kamera, kein Live-Mikrofon oder andere physische Sensorik aktiviert. Die
Umsetzung belegt kein Memory, Lernen, Feldzeit, Organisation, Semantik,
Selbstregulation oder KI. Lauf 197 bleibt unberuehrt.

## Bester naechster Schritt

W2-G trennt die operativen Handoff-Datenrollen und die reine
Gruppenuebergabefunktion aus `receptor_proposal_handoff_audit` von dessen
passiver Vergleichs- und Segmentierungsauswertung.

Verbindlich:

1. Zuerst werden operative Rollen und reine Auditrollen statisch benannt.
2. Nur die von aktiven Kernruntimes benoetigten Handoff-Rollen werden in eine
   eigene neutrale Modulgrenze verschoben.
3. Der bisherige Modulpfad reexportiert alle verschobenen Namen identisch.
4. Auditlogik, Segmentierung und Forschungsinterpretation bleiben ausserhalb
   der operativen Grenze.
5. Identitaets-, Handoff-, Runtime- und Manifesttests muessen bestehen.

## Spaeterer Umsetzungsstand W2-G

W2-G ist am 2026-08-09 kompatibel abgeschlossen worden. Operative
Handoff-Rollen liegen jetzt in `receptor_proposal_handoff`; passive
Segmentierungsvergleiche bleiben im Auditmodul. Der neutrale Kern erreicht
`receptor_proposal_handoff_audit` nicht mehr.
