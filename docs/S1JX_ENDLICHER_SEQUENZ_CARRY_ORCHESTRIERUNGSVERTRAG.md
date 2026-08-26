# S1-JX: Endlicher Sequenz-Carry-Orchestrierungsvertrag

## Zweck

S1-JX bindet die Orchestrierung zwischen dem reinen S1-JO-Materializer und
den privaten S1-JW-Baselineadaptern. Der Vertrag fuehrt keine Sequenz und
keinen Fall der 24-Fall-Matrix aus.

## Endlicher Umfang

Gebunden sind:

- sechs Baseline-Rollen und vier Profilbloecke;
- die sieben korrigierten S1-JK-Sequenzen mit zusammen 23 Intervallen;
- die Kontrollwerte r2, r4 und r8 mit r4 als Primaerprofil;
- 24 Rollen-/Profilfaelle mit jeweils drei unabhaengigen Repliken;
- 72 eindeutige Replikrecords;
- 414 geplante Baseline-Intervallaufrufe;
- elf Checkpoints je Rolle und Refinement.

Diese Kardinalitaeten beschreiben nur den spaeteren endlichen Arbeitsumfang.
S1-JX hat keinen dieser Aufrufe ausgefuehrt.

## Initialisierung und Carry

Jede Rollen-/Profil-/Refinement-Replik startet mit einem frischen
rolleneigenen Feld und privaten Zustand. Auch jede unabhaengige Sequenz
innerhalb einer Replik startet frisch; ein Geschwisterzweig darf keinen
Zustand liefern.

Nur innerhalb derselben Sequenz und Replik werden gemeinsam weitergereicht:

- das vollstaendige Ausgabefeld;
- der vollstaendige private Folgezustand;
- der aktuelle Intervalldigest;
- der kanonische vollstaendige Outputdigest.

Vor dem naechsten Modellaufruf materialisiert S1-JO exakt das folgende
S1-JK-Intervall. Grenzoperationen ersetzen nur S/H; rolleneigene L-, M- oder
Fixed-Adapter-Zustaende bleiben getragen. Nullkontaktintervalle sind positive
Intervalle und duerfen nicht ausgelassen werden.

Zwischen Sequenzen, Refinements, Rollen, Profilen, Faellen sowie Kandidat und
Baselines ist jeder Carry gesperrt. Insbesondere darf r2 weder r4 noch r8
initialisieren.

## Checkpoints und Komponenten

Erfasst wird nur nach einem registrierten positiven Checkpointflag. P_IE
erfasst beide Ordinale beider Sequenzen, P_IH alle drei Ordinale und P_IK
sowie P_IN nur die beiden terminalen Probeausgaben. Der Readout ist passiv
und darf nicht in einen spaeteren Modellaufruf zurueckwirken.

Die signed Komponenten bleiben in der korrigierten Reihenfolge 8, 8, 6 und
6 gebunden. B1/B2 muessen vollstaendige bitidentische Replikausgaben ueber
r2/r4/r8 liefern. B3 bis B6 geben vollstaendige signed r2-r4- und r4-r8-
Residualvektoren aus. Es gibt keine Schwellenanpassung oder Ergebniswertung.

## Atomare Grenze

Ein ungueltiges Intervall, ein Adapterfehler oder eine Carry-, Checkpoint-
beziehungsweise Digestabweichung verwirft die gesamte Replik. Eine ungueltige
Replik verwirft alle drei Refinements des Falls. Teilsequenzen,
Teilkomponenten, Teilfaelle und Teilmatrizen werden nicht veroeffentlicht.

Entscheidung:

`FINITE_SEQUENCE_CARRY_CHECKPOINT_AND_REFINEMENT_OUTPUT_ORCHESTRATION_BOUND_NO_EXECUTION`

Kanonischer Vertragsdigest:

`4bbf3bfb4997fe7e5ad3364276f127d6a8eb53c6b2452c0b4cac387e097cb5a8`

## Naechster zulaessiger Schritt

S1-JY darf ausschliesslich den privaten reinen Orchestrator fuer genau eine
Rollen-/Profil-/Refinement-Replik implementieren und mit kleinen
synthetischen technischen Sequenztests pruefen. Noch kein vollstaendiger
24-Fall-Matrixfall, keine 72-Replik-Ausfuehrung, kein Baselineurteil, keine
Runtime und keine Forschungsprobe.
