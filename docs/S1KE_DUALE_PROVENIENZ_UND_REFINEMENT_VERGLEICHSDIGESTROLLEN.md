# S1-KE: Duale Provenienz- und Refinement-Vergleichsdigestrollen

## Ergebnis

S1-KE behebt den in S1-KD gefundenen Vertragskonflikt durch eine
korrigierende Overlay-Bindung. Die historischen S1-JX-/S1-JZ-Digests und der
S1-KD-STOPP bleiben unveraendert nachvollziehbar.

## Vollstaendiger Provenienzdigest

`output_digest` bleibt der Digest des vollstaendigen Replikoutputs. Er deckt
Replik-ID, Refinement, Checkpoints, Komponenten, Diagnostik und den neuen
Vergleichsdigest ab. Er dient der Provenienz und dem Manipulationsnachweis.

Da Replik-ID und Refinement verschieden sind, darf und soll dieser Digest
zwischen r2, r4 und r8 verschieden sein.

## Identitaetsneutraler Vergleichsdigest

`refinement_comparison_digest` wird ueber einen separaten, exakt gebundenen
Payload berechnet. Nur folgende Felder fehlen darin:

- oben: `replica_id` und `refinement` als Kontrollidentitaeten;
- oben: `output_digest` und `refinement_comparison_digest` als abgeleitete
  Digestfelder;
- in jedem Checkpoint: `replica_id` als Kontrollidentitaet.

Enthalten bleiben insbesondere:

- Modellrolle, Profilblock und Sequenzdigests;
- Checkpointreihenfolge, Sequenz, Ordinal und Intervalldigest;
- Knotenfolge sowie vollstaendige Aktivierungs- und Nachhallvektoren;
- vollstaendige Feld-, Privatzustands- und Adapteroutputdigests;
- alle signed Komponenten;
- die vollstaendige Adapterdiagnostik.

Die bestehende kanonische S1-JZ-Serialisierung und Digestregel wird
unveraendert wiederverwendet.

## Korrigierte Vergleichsregel

B1 und B2 muessen ueber r2, r4 und r8 denselben
`refinement_comparison_digest` liefern. Ihre vollstaendigen
identitaetstragenden `output_digest`-Werte werden nicht gleichgesetzt.

Eine statische synthetische Drei-Refinement-Projektion liefert wie gefordert
drei verschiedene Provenienz-Digests und genau einen gemeinsamen
Vergleichsdigest. Dabei wurde kein Runner aufgerufen.

Entscheidung:

`DUAL_PROVENANCE_AND_IDENTITY_NEUTRAL_REFINEMENT_DIGEST_ROLES_BOUND_NO_RUNNER_CHANGE_OR_EXECUTION`

Kanonischer Vertragsdigest:

`1d9f500f74d895de52c5635b70aaf710a112f88cca1dc5f0cf8853393e831328`

## Ausfuehrungsgrenze

Der bestehende r2-Runner und sein v1-Output blieben unveraendert. r4 und r8
wurden weder implementiert noch ausgefuehrt. Es gab keinen neuen
Materializer-, Adapter- oder Intervallaufruf, keinen Matrixfall und keine
Runtimeintegration.

## Naechster zulaessiger Schritt

S1-KF darf ausschliesslich den gebundenen Vergleichspayload und das duale
Digestpaar im vorhandenen r2-Runner implementieren. Das r2-Exemplar darf
zweimal mit insgesamt hoechstens acht Intervallaufrufen technisch wiederholt
werden. r4/r8, andere Rollen, vollstaendige Matrixfaelle, Runtime und
Forschungsprobe bleiben geschlossen.
