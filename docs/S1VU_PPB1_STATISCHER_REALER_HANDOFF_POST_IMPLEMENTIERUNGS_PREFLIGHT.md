# S1-VU: Statischer realer PPB-1-Handoff-Post-Implementierungs-Preflight

## Auftrag und Grenze

S1-VU prueft nach der synthetischen S1-VT-Abnahme statisch, ob der private
korrigierte S1-VQ-Ausfuehrungskoerper bereits atomar an die neue
Ergebnispipeline angeschlossen ist.

Geprueft werden Plan, Budget, Nullstand, Ausfuehrungsgate, Runnerausgang,
S1-VT-Stufen, v1-Umgehung, atomare Handoffkette und terminaler Erfolgs- oder
Fehlerpfad. Kein registrierter Matrixfall wird ausgefuehrt.

## Bestandener technischer Bestand

Der Preflight bestaetigt:

- unveraenderten 384-Pfad-Elternplandigest;
- unveraenderten 528-Pfad-Korrekturplandigest;
- exakt 528 Faelle und maximal 75.808 Aufrufe;
- null ausgefuehrte registrierte Aufrufe;
- aktives oeffentliches S1-VQ-Ausfuehrungsgate;
- vorhandenen privaten registrierten Runnerkoerper;
- vorhandene alte S1-VQ-Resultatrollen;
- vorhandene S1-VT-Versiegelungs-, Compositor- und v2-Auswerterstufen;
- keine Umgehung ueber den alten S1-VO-v1-Auswerter.

Plan-Digests:

```text
Elternplan:
35c1e589f749f1c1f1f24900f611fd43f8329d803a4b82ca94584d1925067ba3

Korrekturplan:
f307363400ba66e53a49ec9cd21bc17973f93f240f3946eade2c6a7dbdcd1210
```

## Drei Anschlussblocker

### 1. Runnerausgang endet beim alten Resultat

Der interne S1-VQ-Koerper gibt weiterhin `S1VQMatrixResult` zurueck. Dieses
Objekt traegt Receipts, Aufrufzahl und verkleinerte Wiederholungsdigests,
ist aber nicht selbst die atomar validierte `S1VTSealedMatrixResult`-Huelle.

Blocker:

```text
S1VQ_RUNNER_OUTPUT_NOT_SEALED_AS_S1VT_MATRIX_RESULT
```

### 2. Atomare Handoffkette fehlt

Es existiert noch keine einzige private Funktion, die in fest gebundener
Reihenfolge genau einmal:

```text
S1-VQ-Ausfuehrungskoerper
-> S1-VT-Versiegelung
-> 48-Arm-Compositor
-> v2-Auswerter
```

aufruft. Die drei S1-VT-Stufen sind vorhanden, aber nicht mit dem realen
Runnerausgang verbunden.

Blocker:

```text
S1VQ_TO_S1VT_ATOMIC_HANDOFF_CHAIN_MISSING
```

### 3. Terminaler Einmal-Erfolg-/Fehlerausgang fehlt

Es fehlt eine typisierte atomare Endrolle, die entweder das versiegelte
Matrixresultat, die Komposition und die v2-Auswertung gemeinsam traegt oder
genau einen Fehler ohne Teilresultat. Ebenso ist noch keine private
Einmallaufhuelle mit verbrauchbarer Freigabe, Wiederholungssperre und
Fail-Closed-Abbruch gebunden.

Blocker:

```text
ONE_SHOT_TERMINAL_SUCCESS_OR_ERROR_OUTCOME_MISSING
```

## Implementierter statischer Preflight

Das private Modul
[`_ppb1_s1vu_real_handoff_preflight.py`](../mcm_field_organism/_ppb1_s1vu_real_handoff_preflight.py)
analysiert die Funktionsaufrufe der privaten S1-VQ- und S1-VT-Module ueber
den Python-AST. Damit wird die fehlende Handoffkette erkannt, ohne den
privaten Ausfuehrungskoerper aufzurufen.

Von 13 Checks bestehen zehn. Nur die drei vorstehend benannten
Anschlussrollen bleiben gezielt falsch.

Entscheidung:

```text
BLOCKED_PRIVATE_REAL_HANDOFF_REQUIRED_NO_EXECUTION
```

Preflight-Digest:

```text
31147b026d7f7faacba93f15e607e077fa55ace537500bf4c450f8c7d278258c
```

## Testergebnis

Die S1-VU-Abnahme besteht mit `8 von 8` neuen Tests. Zusammen mit PPB-Kern,
Profilbinder, S1-VN, S1-VO, S1-VQ, S1-VR, S1-VT und der aktiven
Engineeringoberflaechen-Grenze bestehen `144 von 144` fokussierte Tests.
Die Paketkompilierung ist erfolgreich.

Die Tests pruefen insbesondere:

- exakte Plan- und Budgetrollen;
- aktives Gate und null ausgefuehrte Aufrufe;
- vorhandenen Runnerkoerper und vorhandene S1-VT-Stufen;
- Abwesenheit einer S1-VO-v1-Abkuerzung;
- exakt drei neue Handoffblocker;
- kanonische und deterministische Preflightausgabe;
- per AST die Abwesenheit jedes privaten Matrixkoerperaufrufs im Preflight;
- Abwesenheit aus Feldsnapshot, Root-Exports und `current_api`.

## Entscheidung

```text
S1_VU_PARENT_AND_CORRECTED_PLANS_ACCEPTED
S1_VU_528_CASE_AND_75808_CALL_BUDGET_ACCEPTED
S1_VU_PUBLIC_EXECUTION_GATE_ACTIVE
S1_VU_PRIVATE_RUNNER_BODY_PRESENT
S1_VU_S1VT_PIPELINE_STAGES_PRESENT
S1_VU_S1VO_V1_BYPASS_ABSENT
S1_VU_EXACT_THREE_REAL_HANDOFF_BLOCKERS_IDENTIFIED
S1_VU_FULL_MATRIX_EXECUTION_BLOCKED
S1_VU_ZERO_REGISTERED_CALLS_EXECUTED
S1_VU_8_OF_8_NEW_TESTS_PASS
S1_VU_144_OF_144_COMBINED_FOCUSED_TESTS_PASS
```

S1-VU bestaetigt keinen realen Matrixlauf und kein PPB-1-Ergebnis. Der Stopp
betrifft ausschliesslich den noch fehlenden atomaren Anschluss zwischen zwei
bereits vorhandenen privaten technischen Stufen.

## Genau ein naechster Schritt

Der einzige Anschluss ist:

```text
S1-VV - statischer Einmallauf-, Handoff-, Ergebnis- und Fehlervertrag
```

S1-VV muss vor jeder Integration festlegen:

- genau eine private Handofffunktion und ihre feste Aufrufreihenfolge;
- eine verbrauchbare Einmallauffreigabe und Wiederholungssperre;
- das vollstaendige terminale Erfolgsobjekt;
- einen typisierten Fehlerausgang ohne Teilresultat;
- welche Digests und Aufrufzaehler vor und nach jeder Stufe gebunden werden;
- dass S1-VO-v1, oeffentliche API, Snapshot und Feldkern unberuehrt bleiben;
- dass Implementierungstests nur einen injizierten synthetischen Producer
  verwenden duerfen.

S1-VV darf noch keine Integration implementieren und keinen Matrixfall
ausfuehren. Eine spaetere reale Einmalausfuehrung benoetigt weiterhin eine
eigene ausdrueckliche Freigabe nach bestandenem Post-Integrations-Preflight.

## Grundlagen

- [S1-VT private Ergebnispipeline](S1VT_PPB1_PRIVATE_ERGEBNISHUELLE_COMPOSITOR_UND_V2_AUSWERTER_ABNAHME.md)
- [S1-VS Ergebnis-Pipeline-Vertrag](S1VS_PPB1_STATISCHER_ERGEBNIS_PIPELINE_KORREKTURVERTRAG.md)
- [S1-VQ korrigierter Matrixplaner](S1VQ_PPB1_PRIVATE_IDENTITAETSROLLEN_UND_KORRIGIERTER_MATRIXPLANER.md)
