# S1-VW: Private synthetische PPB-1-Einmallauf-, Handoff- und Terminalhuellen-Abnahme

## Auftrag und Grenze

S1-VW implementiert die in S1-VV gebundene H0-bis-H7-Orchestrierung nur
fuer synthetische Integrationspruefungen. Der Producer wird injiziert und
liefert ausschliesslich konstruierte S1-VQ-Resultate. Der private reale
S1-VQ-Ausfuehrungskoerper wird weder importiert noch aufgerufen.

Nicht Bestandteil von S1-VW sind:

- Produktionsintegration oder reale Projekteignerfreigabe;
- Ausfuehrung eines registrierten PPB- oder Baselinepfads;
- Feld-, Rezeptor- oder Medienlauf;
- oeffentliche API oder Snapshotrolle;
- Parameter-, Baseline- oder Eignungsentscheidung.

## Implementierte private Rollen

Das private Modul
[`_ppb1_s1vw_synthetic_one_shot_handoff.py`](../mcm_field_organism/_ppb1_s1vw_synthetic_one_shot_handoff.py)
implementiert:

- einen typisierten synthetischen Autorisierungstoken;
- einen exklusiv erzeugten und dauerhaft erhaltenen Sperrmarker;
- die feste H0-bis-H7-Reihenfolge;
- Vorvalidierung von 528 Receipts, 75.808 konstruierten Beobachtungen und
  144 Wiederholungsvergleichen;
- S1-VT-Versiegelung, 48-Arm-Komposition und v2-Auswertung;
- atomare terminale Erfolgs- oder Fehlerartefakte;
- Fehlerrollen H2 bis H7 ohne Receipt-, Arm- oder Entscheidungsleck;
- einen bedingungslos gesperrten Produktionsentrypoint.

Der synthetische Artefaktpfad muss ein neu angelegtes temporaeres
Testverzeichnis mit dem Namen `s1vw-synthetic-artifacts` sein. Die spaetere
Produktionsgrenze `data/generated/ppb1/one_shot/` wird abgelehnt.

## Einmaligkeit und Atomaritaet

H0 prueft Token, injizierte Rollen und freie Testpfade. H1 legt den
Sperrmarker exklusiv an und verbraucht den Token. Erst danach darf der
synthetische Producer aufgerufen werden. Ein vorhandener Marker, ein
vorhandenes Terminalartefakt oder ein bereits verbrauchter Token stoppt vor
einem weiteren Produceraufruf.

Erfolg und Fehler werden kanonisch in eine Temporaerdatei geschrieben und
atomar auf genau einen Terminalpfad verschoben. Der Sperrmarker bleibt bei
jedem Ausgang erhalten. Fehlerobjekte enthalten keine Teilresultate. Eine
gescheiterte Terminalpublikation liefert nur einen H7-In-Memory-Fehler und
erlaubt keine Wiederholung.

Systemzeit besitzt keine kausale, ordnende oder Digestrolle. Reihenfolge und
Einmaligkeit werden durch Ausfuehrungs-ID, Stufen, Zaehler, Digests und den
persistenten Marker bestimmt.

## Synthetische Abnahme

Die Abnahme konstruiert dieselben 528 typisierten Receiptrollen und 75.808
Schrittbeobachtungen wie S1-VT. Sie fuehrt keinen Kern-, Adapter- oder
Matrixschritt aus. Geprueft werden:

- vollstaendiger Erfolgsweg H0 bis H7;
- dauerhafte Wiederholungssperre vor einem zweiten Produceraufruf;
- getrennte Fail-Closed-Grenzen H2, H3, H4, H5, H6 und H7;
- genau ein terminales Artefakt ohne Temporaerrest im Erfolgsfall;
- Fehlerartefakte ohne Matrix-, Kompositions- oder Auswertungsobjekt;
- Ablehnung fremder und produktiver Artefaktpfade vor Tokenverbrauch;
- unveraenderte Root-Exports, `current_api` und Feldsnapshot;
- Abwesenheit des realen Matrixkoerpers sowie jeder Feld-, Medien- und
  Systemzeitabhaengigkeit.

Die S1-VW-Abnahme besteht mit `11 von 11` neuen Tests. Zusammen mit dem
bisherigen fokussierten PPB- und Engineeringbestand bestehen `155 von 155`
Tests. Die Paketkompilierung ist erfolgreich.

## Entscheidung

```text
S1_VW_PRIVATE_SYNTHETIC_H0_TO_H7_ORCHESTRATOR_IMPLEMENTED
S1_VW_SYNTHETIC_AUTHORIZATION_CONSUMED_BY_DURABLE_LOCK
S1_VW_PROCESS_PERSISTENT_RETRY_BLOCK_TESTED
S1_VW_ATOMIC_SUCCESS_AND_ERROR_ARTIFACTS_TESTED
S1_VW_H2_TO_H7_FAIL_CLOSED_BOUNDARIES_TESTED
S1_VW_NO_PARTIAL_RESULT_EXPOSURE_TESTED
S1_VW_PRODUCTION_ENTRYPOINT_HARD_BLOCKED
S1_VW_PRIVATE_REAL_S1VQ_BODY_NOT_IMPORTED_OR_CALLED
S1_VW_ZERO_REGISTERED_MATRIX_CALLS_EXECUTED
S1_VW_11_OF_11_NEW_TESTS_PASS
S1_VW_155_OF_155_COMBINED_FOCUSED_TESTS_PASS
```

S1-VW schliesst die synthetische Implementierungs- und Abnahmegrenze. Es
liegt weiterhin kein reales PPB-1-, Parameter- oder Baselineergebnis vor.

## Genau ein naechster Schritt

Der einzige Anschluss ist:

```text
S1-VX - statischer Post-Integrations- und Ressourcen-Preflight
```

S1-VX darf keinen Matrixfall ausfuehren. Es muss statisch pruefen, welche
Produktionsbindung, realen Ressourcenuntergrenzen, Quellcodedigests,
Artefaktgrenzen und Projekteigner-Autorisierungsrollen noch fehlen. Nur wenn
alle Vorbedingungen geschlossen sind, darf S1-VX einen exakten Text fuer
eine neue reale Einmallauffreigabe vorschlagen. `ok weiter` bleibt dafuer
unzureichend.

## Grundlagen

- [S1-VV Einmallauf- und Handoffvertrag](S1VV_PPB1_STATISCHER_EINMALLAUF_HANDOFF_ERGEBNIS_UND_FEHLERVERTRAG.md)
- [S1-VU realer Handoff-Preflight](S1VU_PPB1_STATISCHER_REALER_HANDOFF_POST_IMPLEMENTIERUNGS_PREFLIGHT.md)
- [S1-VT private Ergebnispipeline](S1VT_PPB1_PRIVATE_ERGEBNISHUELLE_COMPOSITOR_UND_V2_AUSWERTER_ABNAHME.md)
