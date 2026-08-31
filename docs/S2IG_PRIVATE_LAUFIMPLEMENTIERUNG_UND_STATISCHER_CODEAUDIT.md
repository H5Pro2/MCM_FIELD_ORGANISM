# S2-IG - Private Laufimplementierung und statischer Codeaudit

## Status

`S2IG_PRIVATE_RUNNER_RECORDER_VERIFIER_IMPLEMENTED_STATIC_AUDIT_PASSED_QUALIFICATION_LOCKED`

S2-IG implementiert ausschliesslich die private Lauf- und Beleggrenze des
nach S2-IF bestandenen S2-IE-Plans. Es wurde kein Funktionslauf ausgefuehrt
und kein neuer Memory-Befund erzeugt.

Waehren dieses Schritts wurden:

- keine neuen S2-IG-Module importiert;
- keine Tests ausgefuehrt;
- keine Rezeptor-, Speicher-, Projektions-, Signal- oder Baselinefunktion
  aufgerufen;
- keine Datei- oder Ergebnisaufzeichnung durch den neuen Recorder erzeugt.

## Implementierter Umfang

Neu angelegt wurden genau vier private Module:

1. `tools/_s2ig_private_fixture_registry.py`;
2. `tools/_s2ig_private_runner.py`;
3. `tools/_s2ig_private_append_only_recorder.py`;
4. `tools/_s2ig_private_result_verifier.py`.

Zusaetzlich wurde in
`tools/_s2ic_private_two_area_conflict_contract.py` ausschliesslich die durch
S2-IF verworfene Gleichsetzung

```text
bundle.probe_digest == probe.probe_digest
```

aus der Quellenvalidierung entfernt. Alle uebrigen S2-IC-Pruefungen, die
fuenf Statusregeln, Ledgerformeln, Ownergrenzen und die Direktbaseline sind
unveraendert. S2-ID bleibt damit Logikqualifikation; die neue reale
Zwei-Proben-Integration benoetigt weiterhin ihre eigene Qualifikation.

## Fixtures und Registry

Die private Fixture bindet exakt:

```text
Geschichten:   6
Formationen:  38
Funktionsfaelle: 8
```

Gebunden sind die Geschichten `h-c`, `h-x0`, `h-x1`, `h-sa`, `h-sb` und
`h-n`. Die Ausfuehrungsfixture enthaelt Quellen, Reihenfolge, Zeitfenster und
Budgets, aber keine Sollstatus. Die acht Sollstatus existieren nur in der
unabhaengigen Evaluationswurzel des Verifikators.

Die Erfolgsregistry ist lueckenlos `ie-op-001..183`. Ihre Arithmetik lautet:

```text
Laufvorbereitung und Manifest                  2
Historyinitialisierungen                       6
38 Rezeptor-/Formationpaare                   76
6 Kontextabrufbloecke zu je 5 Operationen     30
8 Fallbloecke zu je 7 Operationen             56
Ausfuehrungsevidenz und Evaluationsbindung      2
Fallevaluationen                               8
Aggregat, Terminal und Completion               3
Gesamt                                        183
START-/RESULT-Ereignisse                      366
maximaler Fehlerpfad                     185 / 370
```

Elternkanten werden nur auf bereits vorhandene Operationen oder die beiden
expliziten externen Wurzeln `ROOT` und `external-evaluation-plan-seal`
gerichtet. Der Registrypfad ist daher statisch azyklisch.

## Getrennte Probenrollen

Der Runner bildet zwei unverwechselbare, unveraenderliche Rollenformen:

- `ContextRetrievalProbe` bindet die vollstaendige audiovisuelle
  S2-FS-Probe, ihren ReceptorReceipt und den nativen Funktionsprobedigest;
- `MaskedSignalProbe` bindet die spaetere visuelle Teilprobe, ihre feste
  Maske, ihr eigenes ReceptorReceipt und den nativen MaskedVisualProbe-
  Digest.

Beide Rollen besitzen eigene IDs, Quellen und Digests. Sie werden nicht
voneinander abgeleitet und nur durch den vorher gebildeten
`case_plan_digest` derselben Ausfuehrungsfixture zugeordnet.

Die zwei nativen Beziehungen bleiben getrennt:

```text
two_area_bundle.probe_digest
    == context_retrieval_probe.function_probe_digest

signal_input.probe_digest
    == masked_signal_probe.masked_visual_probe_digest
```

Eine Gleichheit beider Probedigests ist weder gefordert noch als Autorisierung
verwendet.

## Funktionswiederverwendung

Der Runner ruft ausschliesslich die vorhandenen privaten Komponenten auf:

- S2-FS fuer atomare B4-/TSPM-Formation und read-only Abruf;
- S2-GC fuer das Drei-Rollen-Bundle;
- S2-GI fuer die A/B-Schattenprojektion;
- S2-IC fuer das Fuenf-Status-Signal;
- die unabhaengige S2-IC-Direktbaseline.

Im Runner existiert keine eigene Status-, Matching-, Auswahl-, Rangfolge-,
Verschmelzungs- oder Fallbackregel. `selected_area`, `recommended_area` und
`automatic_selection` bleiben in den Belegen explizit `None`.

## Owner und Atomaritaet

Je Fall bindet ein `DualProbeCaseOwner` vor beiden Armaufrufen:

- Fallplan;
- beide getrennten Probenhuellen und nativen Probedigests;
- A/B-Bundle;
- Signal- und Baselineinput;
- Quellenledger.

Signal und Baseline besitzen weiterhin getrennte S2-IC-Kindowner und werden
getrennt aufgerufen. Ihre Resultate tragen bis zum gemeinsamen Ownercommit
den Status `PRIVATE_CANDIDATE_NOT_CASE_FINDING`. Erst nach Abnahme beider
Resultate entsteht der regulaere Fallbeleg. Wiederverwendung und Teilcommit
sind ausgeschlossen.

## Recorder und Verifikator

Der append-only Recorder erzwingt:

- ein exklusiv neu angelegtes Laufverzeichnis;
- Registryreihenfolge und je ein START-/RESULT-Paar;
- Owner-, Reservierungs-, Eltern- und Artefaktbindung;
- kanonische ASCII-Artefakte mit typbezogenen Groessengrenzen;
- keinen Overwrite, keine Fortsetzung und keinen Retry;
- genau einen terminalen Erfolgs- oder Fehlerpfad;
- `START_BLOCKED` vor erfolgreicher Reservierung;
- zwei registrierte Fehlerabschlussoperationen bis `NOT_EVALUABLE`.

Der stdlib-only Verifikator rekonstruiert die `183` Operationen unabhaengig,
prueft Journal- und Artefaktkette, Quellenhashes, Elternkanten, Receiptgrenzen,
die Ausfuehrungs-/Evaluationswurzeltrennung und die getrennten Probe-
Relationen. Eine gueltige funktionale Abweichung bleibt auswertbar; nur ein
technischer oder methodischer Bruch ergibt `NOT_EVALUABLE`.

## Statische Belege

Alle fuenf geaenderten Python-Dateien wurden nur per ASCII-Lesen und
`ast.parse` geprueft. Es gab keinen Projektimport. Ergebnis:

```text
Fixture/Registry: AST_OK
Runner:           AST_OK
Recorder:         AST_OK
Verifikator:      AST_OK
S2-IC-Korrektur:  AST_OK
Hauptgate:        False
Registryrechnung: 183 / 366
```

Quelldigests:

```text
_s2ig_private_fixture_registry.py
163116cc881830f214a4de3577f6daf7976957c6e883aff8d7bb54338e900633

_s2ig_private_runner.py
6d9da9e0879217c289fa7c0ac8f9c464c102687caa92da9d59aee041fb06cd0a

_s2ig_private_append_only_recorder.py
070317a6ecf8659bfca8072050e275615512645d4e265813aa214e3459762f7c

_s2ig_private_result_verifier.py
62d4b319eabff79f3cb3576668f20d2b6bff509f460a02112e5bffe930406501

_s2ic_private_two_area_conflict_contract.py
e0aa27a1d29704739c23c879dd04fba8e38f31d8435bf35b253f340174251471
```

## Freigabegrenze

S2-IG ist implementiert und statisch freigabereif. Noch gesperrt bleiben:

- Import oder Ausfuehrung der neuen Laufmodule;
- technische Qualifikation und Tests;
- jede der sechs realen Geschichten und alle acht Funktionsfaelle;
- der reale Fuenf-Status-Funktionslauf;
- API-, Snapshot- oder Feldintegration;
- automatische Kontextwahl oder ein neuer Memory-Claim.

Der naechste zulaessige Schritt ist eine getrennt freizugebende neutrale
technische Qualifikation von Fixture, Registry, Runner, Recorder,
Verifikator und insbesondere der ungleichen, aber korrekt gebundenen
Probedigests.
