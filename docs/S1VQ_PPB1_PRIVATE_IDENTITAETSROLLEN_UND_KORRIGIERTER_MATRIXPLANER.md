# S1-VQ: PPB-1 private Identitaetsrollen und korrigierter Matrixplaner

## Auftrag und Grenze

S1-VQ implementiert die in S1-VP gebundenen methodischen Korrekturen:

- einen privaten atomaren Identitaetscarry fuer B01 bis B07;
- getrennte Auswahl- und Schreibidentitaeten im Baseline-Readout;
- den korrigierten 528-Pfad-Plan mit R0/R1-Kontrollen;
- normalisierte, von der Pfad-ID unabhaengige Wiederholungsdigests;
- den vollstaendigen internen korrigierten Ausfuehrungskorper;
- ein bedingungsloses Gate vor jeder registrierten Ausfuehrung.

Die Implementierung fuehrt keine der 528 registrierten Pfade aus. Nur
ausdruecklich gekennzeichnete Miniaturfixtures mit hoechstens vier Frames
werden fuer die private Verkabelungsabnahme verwendet.

## Erhalt des Elternplans

S1-VQ veraendert das S1-VN-Modul und seinen 384-Pfad-Plan nicht. Der
Elternplan besteht weiterhin mit:

```text
35c1e589f749f1c1f1f24900f611fd43f8329d803a4b82ca94584d1925067ba3
```

Der neue Plan wird ausschliesslich aus den vorhandenen 384 Parent-Pfaden
abgeleitet. Jeder Parent besitzt genau einen R0-Pfad. Nur Parent-Pfade mit
F04, F05 oder F06 erhalten unmittelbar danach genau einen R1-Pfad.

## Privater Identitaetscarry

Das neue Modul
[`_ppb1_s1vq_corrected_matrix.py`](../mcm_field_organism/_ppb1_s1vq_corrected_matrix.py)
legt den Identitaetszustand als atomaren privaten Carry um den bestehenden
Baselinezustand. Die Baselineberechnung selbst bleibt in S1-VN unveraendert.

Der Carry bindet:

- den vollstaendigen bestehenden Baselinezustand;
- aktive technische Eintragsidentitaeten;
- fuer B01 die endliche Generationsbilanz aller Ring-Slots;
- einen kanonischen gemeinsamen Digest.

Ein Ergebnis ist nur gueltig, wenn Baselinezustand und Identitaetscarry
gemeinsam fortgeschrieben und durch denselben Postcarry-Digest gebunden
werden.

## Implementierte Identitaetsformen

| Baseline | Identitaetsform |
|---|---|
| B01 | generationierte Ring-Slots `b01.slot.NNN.gMMMMMM` |
| B02 | genau `b02.window.000` |
| B03 | feste Slots `b03.slot.NNN.g000001` |
| B04 | genau `b04.trace.000` |
| B05 | genau `b05.trace.000` |
| B06 | genau `b06.trace.000` |
| B07 | keine Identitaet |

B01 sucht zunaechst im Vorzustand und schreibt danach in den naechsten
Ringplatz. Auswahl- und Schreibidentitaet koennen deshalb verschieden sein.
Bei Wiederbelegung eines physischen Slots steigt seine Generation und die
alte Inhaltsidentitaet verschwindet aus dem aktiven Inventar.

B03 schreibt nur bei einem neuen freien festen Slot. Ein Match veraendert
keinen Eintrag und besitzt deshalb eine Auswahl-, aber keine
Schreibidentitaet. Bei voller Liste ohne Match bleiben beide Rollen leer.

B02 und B04 bis B06 schreiben ihre eine Zustandsidentitaet bei jedem
Fortschritt, geben sie aber nur bei einem Match zugleich als
Auswahlidentitaet aus. B07 bleibt vollstaendig identitaetsfrei.

## Readout- und Beobachtungsrollen

Jeder korrigierte Baseline-Schritt traegt:

- bestehendes Baselineereignis und Distanz;
- `selected_entry_id` oder `None`;
- `written_entry_id` oder `None`;
- Digest des ausgewaehlten Vorzustandseintrags oder `None`;
- Anzahl und Digest der aktiven Identitaeten;
- atomaren Postcarry-Digest.

Die korrigierten Fallreceipts fuehren diese Rollen als geordnete
Identitaetsbeobachtungen parallel zu den bestehenden S1-VN-
Schrittbeobachtungen. PPB-Zuordnungen verwenden weiterhin ihre vorhandene
Slot-ID.

## Korrigierter Plan

Der neue Plan besitzt exakt:

```text
384 R0-Pfade + 144 R1-Pfade = 528 Pfade
```

Aufteilung:

```text
66 PPB-Pfade
462 Baselinepfade
```

Jeder R1-Pfad:

- folgt unmittelbar seinem R0-Pfad;
- referenziert dieselbe S1-VN-Parent-ID;
- besitzt gleiche Familie, Parameter, Modalitaet und Fixture;
- bindet denselben Config-Digest und dieselbe Aufrufzahl;
- startet bei einer spaeteren Ausfuehrung aus einem neuen Frischzustand.

Korrigierter Plan-Digest:

```text
f307363400ba66e53a49ec9cd21bc17973f93f240f3946eade2c6a7dbdcd1210
```

## Aufrufbudget

Die Vorbereitung bestaetigt exakt:

```text
PPB-Aufrufe:       9.476
Baselineaufrufe:  66.332
Gesamt:           75.808
ausgefuehrt:            0
```

Die Vollmatrixfunktion bleibt mit `S1VQ_MATRIX_EXECUTION_BLOCKED`
bedingungslos gesperrt. Der interne Ausfuehrungskorper ist implementiert,
aber ueber den vorgesehenen Einstieg nicht erreichbar.

## R0/R1-Vergleich

Der Wiederholungsvergleich schliesst die unterschiedlichen Pfad-IDs aus und
bindet stattdessen:

- Eingangsfolgendigest;
- akzeptierte Aufrufzahl;
- Ereignisfolge;
- bestehende Schrittbeobachtungen;
- neue Identitaetsbeobachtungen;
- Endzustandsdigest.

Die Miniaturabnahme erzeugt fuer PPB und alle sieben Baselines getrennte R0-
und R1-Frischstarts. Alle acht normalisierten Digestpaare sind bitgleich.
Diese Miniaturfixtures sind nicht Bestandteil von F01 bis F08 und keine
Matrixausfuehrung.

## Testergebnis

Die S1-VQ-Abnahme besteht mit `17 von 17` neuen Tests. Zusammen mit S1-VO,
S1-VN, Profilbinder, PPB-Kern und aktiven Architekturgrenzen bestehen
`113 von 113` fokussierte Tests. Die Paketkompilierung ist erfolgreich.

Geprueft werden insbesondere:

- unveraenderter Elternplan und Eltern-Digest;
- 528 eindeutige korrigierte Pfade und exakte R0/R1-Abstammung;
- 75.808-Aufrufbudget bei null Ausfuehrung;
- B01-Auswahl-/Schreibtrennung und Generationserhoehung;
- feste B03- und Einzelspuridentitaeten;
- identitaetsfreies B07;
- Fail-Closed-Verhalten bei inkonsistentem Identitaetsinventar;
- Miniatur-R0/R1-Bitgleichheit fuer alle acht Familien;
- Abwesenheit aus Feldsnapshot, Root-Exports und `current_api`.

## Entscheidung

```text
S1_VQ_PARENT_384_PATH_PLAN_BIT_EQUAL
S1_VQ_PRIVATE_ATOMIC_BASELINE_IDENTITY_CARRY_IMPLEMENTED
S1_VQ_SELECTED_AND_WRITTEN_IDENTITIES_IMPLEMENTED
S1_VQ_B01_GENERATIONAL_REUSE_ACCEPTED
S1_VQ_B07_REMAINS_STATE_AND_IDENTITY_FREE
S1_VQ_CORRECTED_528_PATH_PLAN_IMPLEMENTED
S1_VQ_CORRECTED_PLAN_DIGEST_BOUND
S1_VQ_75808_CALL_BUDGET_ACCEPTED
S1_VQ_MINIATURE_R0_R1_DIGESTS_BIT_EQUAL
S1_VQ_FULL_MATRIX_EXECUTION_BLOCKED
S1_VQ_ZERO_REGISTERED_CALLS_EXECUTED
S1_VQ_17_OF_17_NEW_TESTS_PASS
S1_VQ_113_OF_113_COMBINED_FOCUSED_TESTS_PASS
```

S1-VQ implementiert die beiden Korrekturrollen. Ob der gesamte korrigierte
Pfad technisch ausfuehrungsbereit ist, muss ein eigener Preflight pruefen.
Es liegt noch kein Parameter-, Baseline- oder Eignungsergebnis vor.

## Genau ein naechster Schritt

Der einzige Anschluss ist:

```text
S1-VR - abschliessender statischer Preflight des korrigierten
        528-Fall-Pfads
```

S1-VR muss Eltern- und Korrekturplan, Identitaetsbilanz, R0/R1-
Abstammung, Ergebnisrollen, Aufrufbudget, Frischstartpfad, Ausfuehrungsgate
und Auswerteranschluss vollstaendig pruefen. Der Preflight darf keine
registrierte Ausfuehrung starten.

Nur wenn beide S1-VO-Blocker nachweislich geschlossen sind und kein neuer
Blocker entsteht, darf danach ein eigener endlicher Ausfuehrungsschritt
vorgeschlagen werden.

## Grundlagen

- [S1-VP statischer Korrekturvertrag](S1VP_PPB1_STATISCHER_IDENTITAETS_UND_WIEDERHOLUNGSKORREKTURVERTRAG.md)
- [S1-VO reiner Auswerter und Preflight](S1VO_PPB1_REINER_AUSWERTER_UND_STATISCHER_VOLLMATRIX_PREFLIGHT.md)
- [S1-VN private Runner-Abnahme](S1VN_PPB1_PRIVATE_FIXTURE_BASELINE_UND_MATRIXRUNNER_ABNAHME.md)
