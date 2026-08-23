# S1-VT: Private PPB-1-Ergebnishuelle, Compositor und v2-Auswerter

> Anschlussstatus: S1-VU bestaetigt die synthetische Pipeline, stoppt den
> realen Anschluss aber an altem Runnerausgang, fehlender atomarer
> Handoffkette und fehlendem terminalem Einmal-Erfolg-/Fehlerpfad. Siehe
> [S1-VU](S1VU_PPB1_STATISCHER_REALER_HANDOFF_POST_IMPLEMENTIERUNGS_PREFLIGHT.md).

## Auftrag und Grenze

S1-VT implementiert den statischen S1-VS-Vertrag als vollstaendig private
Ergebnispipeline. Der Schritt umfasst:

- eine atomar validierende Huelle fuer genau 528 korrigierte Fallreceipts;
- vollstaendige R0/R1-Abstammungs- und Aufrufbilanzen;
- einen reinen Compositor fuer genau 48 technische Armrecords;
- ein kanonisches Evidenzledger je Arm;
- einen korrigierten reinen v2-Auswerter;
- konstruierte synthetische Vertrags- und Fail-Closed-Tests.

Der registrierte S1-VQ-Matrixrunner wird nicht aufgerufen. Feldkern,
Medienpfade, Snapshot, oeffentliche API und die bestehenden S1-VQ- und
S1-VO-v1-Module bleiben unveraendert.

## Private Implementierung

Das neue Modul
[`_ppb1_s1vt_result_pipeline.py`](../mcm_field_organism/_ppb1_s1vt_result_pipeline.py)
enthaelt drei getrennte reine Stufen:

```text
528 S1-VQ-Fallreceipts
        |
        v
atomar versiegeltes S1-VT-Matrixresultat
        |
        v
48 Armrecords + 48 Evidenzledger
        |
        v
zwei getrennte Modalitaetsentscheidungen
```

Keine Stufe besitzt Zugriff auf den aktiven Feldkern oder eine
Medienruntime. Der S1-VT-Quelltext importiert und ruft keinen registrierten
Matrixausfuehrungseinstieg auf.

## Atomare 528-Receipt-Huelle

`S1VTSealedMatrixResult` akzeptiert nur das vollstaendige korrigierte
Planinventar in kanonischer Reihenfolge. Vor der Versiegelung werden
geprueft:

- Eltern- und Korrekturplandigest;
- exakt 528 planrichtige und schrittausgerichtete Receipts;
- gleiche Laenge von Ereignissen, Basis- und Identitaetsbeobachtungen;
- Schrittindex, Ereignisrolle, endliche Messwerte und Digestrollen;
- gemeinsame Eingangsfolgendigests ueber Familien und R0/R1;
- 144 vollstaendige Vergleichsrecords mit R0- und R1-Pfad-ID;
- Bitgleichheit aller normalisierten R0/R1-Digests;
- exakt 9.476 PPB-, 66.332 Baseline- und 75.808 Gesamtaufrufe;
- kanonischer Receiptlisten-, Vergleichslisten- und Gesamtdigest.

PPB-Slotmatches und Baseline-Matches bleiben anatomisch korrekt getrennt:
PPB-Receipts verwenden ihre vorhandene Slot-ID, besitzen aber im S1-VQ-
Schema keinen getrennten Auswahl-Vorzustandsdigest. B01 bis B06 muessen fuer
eine ausgewaehlte Baselineidentitaet weiterhin den vorhandenen
Vorzustandsdigest tragen. Der Validator erfindet fuer PPB keine fehlende
Baseline-Rolle.

## Reiner 48-Arm-Compositor

Jeder Arm entsteht ausschliesslich aus:

```text
R0: F01 F02 F03 F04 F05 F06 F07 F08
R1:             F04 F05 F06
```

Der Compositor leitet daraus deterministisch ab:

- Vier-Bit-Lebenszyklusmaske fuer F01, F06, F07 und F08;
- Sechs-Bit-Diagnosemaske aus den gebundenen Endproben F02 bis F05;
- F02-Nahzuordnung und F03-Ankertrennung;
- Drei-Bit-Wiederholungsmaske fuer F04 bis F06;
- maximales logisches Werte- und Identitaetsmetadatenbudget;
- getrennte R0-, R1- und Gesamtaufrufe;
- genau ein kanonisches Evidenzledger.

Das Evidenzledger behaelt Quellreceiptdigests, Diagnoseereignisse,
Zuordnungsidentitaeten, Distanzen, F05-Verschiebungen, Fixturemaxima und
Wiederholungsvergleichsdigests. Der Compositor trifft keine Auswahl- oder
Baselineentscheidung.

## Korrigierter v2-Auswerter

Der v2-Auswerter akzeptiert nur das geordnete vollstaendige 48-Arm-
Kreuzprodukt. Eine B01-bis-B06-Baseline darf PPB-1 nur reduzieren, wenn:

- beide Arme alle Zulassungsregeln bestehen;
- Diagnose-, Lebenszyklus- und Wiederholungsmasken gleich sind;
- Nahzuordnung und Ankertrennung gleich bestanden sind;
- logisches Werte-, Identitaetsmetadaten- und Gesamtaufrufbudget nicht
  groesser sind.

Damit genuegt eine nur gleich grosse Matchanzahl nicht mehr. Unterschiedlich
verteilte Diagnosematches gelten als unterschiedliche technische
Ergebnisprofile. B07 bleibt von jeder Reduktion ausgeschlossen.

Unter mehreren nicht reduzierten PPB-Records gilt die gebundene Ordnung aus
logischen Werten, Identitaetsmetadaten, Gesamtaufrufen und erst danach
P0/P1/P2.

## Rein konstruierte Abnahme

Die Testfixture materialisiert alle 528 Planrollen und 75.808 typisierten
Schrittbeobachtungen als konstruierte Daten. Sie ruft weder PPB-Kern noch
Baselineadapter auf. Damit werden nur Resultattransport, Bilanz,
Verdichtung, Fail-Closed-Verhalten und Auswertungslogik geprueft.

Kanonische Digests dieser konstruierten Fixture:

```text
versiegeltes Matrixresultat:
11d3d407bf928fb2c9c93bbbb2f0beefa0e8122740018bb58251bb4159dc0f16

48-Arm-Komposition:
b3045d745eca08f5f600824109165fd23b5979eb925745f45e2525d5d402d387

synthetische Auswertung:
8f21368b94595b5e68db4488f61094e60496c92d59c614e48e6b77943e2e21a5
```

Die konstruierte Fixture enthaelt absichtlich eine gleichwertige kleinere
Baseline. Deshalb lautet ihre rein synthetische Auswahl fuer beide
Modalitaeten `NO_ADMISSIBLE_CONFIGURATION`. Das ist ein erwarteter
Auswertertest und weder ein Ergebnis der registrierten Matrix noch eine
Aussage ueber PPB-1.

## Fail-Closed-Abnahme

Die Tests pruefen insbesondere:

- fehlende Receipts;
- nicht atomar belegte Baselineauswahl;
- exakte 528-/144-/48-Inventare;
- vollstaendige R0-, R1- und Gesamtaufrufbilanzen;
- feste Diagnose-, Lebenszyklus- und Wiederholungsmasken;
- Verknuepfung von Armrecord und Evidenzledger;
- Nichtreduktion bei unterschiedlicher Diagnosemaske;
- Reduktion nur bei gleichem Profil und kleinerem Budget;
- Vorrang des Identitaetsbudgets in der PPB-Auswahl;
- Abwesenheit aus Root-Exports, `current_api` und Feldsnapshot;
- Abwesenheit jedes Feld-, Medien- oder Matrixausfuehrungsaufrufs.

## Testergebnis

Die S1-VT-Abnahme besteht mit `15 von 15` neuen Tests. Zusammen mit
PPB-Kern, Profilbinder, S1-VN, S1-VO, S1-VQ, S1-VR und der aktiven
Engineeringoberflaechen-Grenze bestehen `136 von 136` fokussierte Tests.
Die Paketkompilierung ist erfolgreich.

## Entscheidung

```text
S1_VT_PRIVATE_ATOMIC_528_RECEIPT_ENVELOPE_IMPLEMENTED
S1_VT_144_COMPLETE_REPEAT_COMPARISONS_IMPLEMENTED
S1_VT_EXACT_48_ARM_COMPOSITOR_IMPLEMENTED
S1_VT_CANONICAL_ARM_EVIDENCE_LEDGERS_IMPLEMENTED
S1_VT_DIAGNOSTIC_LIFECYCLE_AND_REPEAT_MASKS_IMPLEMENTED
S1_VT_IDENTITY_METADATA_AND_R0_R1_CALL_BUDGETS_IMPLEMENTED
S1_VT_CORRECTED_BASELINE_EQUIVALENCE_EVALUATOR_IMPLEMENTED
S1_VT_CONSTRUCTED_528_RECEIPT_FIXTURE_ACCEPTED
S1_VT_FULL_MATRIX_EXECUTION_REMAINS_BLOCKED
S1_VT_ZERO_REGISTERED_CALLS_EXECUTED
S1_VT_15_OF_15_NEW_TESTS_PASS
S1_VT_136_OF_136_COMBINED_FOCUSED_TESTS_PASS
```

S1-VT bestaetigt die private Ergebnisverarbeitung mit konstruierten Daten.
Es liegt weiterhin kein reales Parameter-, Baseline- oder PPB-1-
Eignungsergebnis vor.

## Genau ein naechster Schritt

Der einzige Anschluss ist:

```text
S1-VU - abschliessender statischer Post-Implementierungs-Preflight des
        realen korrigierten 528-Pfad-Anschlusses
```

S1-VU muss ohne Ausfuehrung pruefen, ob der bestehende S1-VQ-Runnerausgang
atomar und ohne alte S1-VO-v1-Abkuerzung in S1-VT versiegelt, komponiert und
ausgewertet werden kann. Ausfuehrungsgate, Einmallaufgrenze, Fehlerpfad,
Ergebnisobjekt und null bisherige Aufrufe muessen explizit geprueft werden.

S1-VU darf keinen Matrixfall starten. Auch ein bestandener Preflight waere
noch keine automatische Ausfuehrungsfreigabe.

## Grundlagen

- [S1-VS Ergebnis-Pipeline-Korrekturvertrag](S1VS_PPB1_STATISCHER_ERGEBNIS_PIPELINE_KORREKTURVERTRAG.md)
- [S1-VR abschliessender korrigierter Preflight](S1VR_PPB1_ABSCHLIESSENDER_STATISCHER_KORRIGIERTER_VOLLMATRIX_PREFLIGHT.md)
- [S1-VQ Identitaetsrollen und korrigierter Plan](S1VQ_PPB1_PRIVATE_IDENTITAETSROLLEN_UND_KORRIGIERTER_MATRIXPLANER.md)
