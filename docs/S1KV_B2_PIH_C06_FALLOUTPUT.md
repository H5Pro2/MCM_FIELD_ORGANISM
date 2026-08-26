# S1-KV: B2/P_IH-C06-Falloutput

## Ergebnis

S1-KV setzt den technischen Fallrecord C06 fuer B2 unter
`P_IH_ATTENUATION` ausschliesslich aus den S1-KU-Ausgaben zusammen. Es wird
keine Replik erneut ausgefuehrt.

Der Record bindet drei Provenienz-Digests, einen gemeinsamen
Refinement-Vergleichsdigest, je acht bitidentische signed Komponenten, drei
aufeinanderfolgende private L-Digests und korrekte Checkpoint-
Elternidentitaeten. r4 ist die Primaerausgabe.

Alle acht Komponenten sind klein und nicht null. Die L-Digestfolge sowie die
Komponenten sind ueber r2/r4/r8 bitidentisch. Dies ist ein reproduzierbarer
technischer B2-Zustandsbefund, aber kein Schwellen-, Baseline- oder
Kandidatenurteil.

Falloutputdigest:

`e12db2e8678108f56414868782d92e999d56de90cd1668c5dae334f95e5ef3bf`

Entscheidung:

`C06_B2_PIH_THREE_REFINEMENT_CASE_OUTPUT_BOUND_FROM_S1KU_RECEIPT_NO_NEW_EXECUTION`

Kanonischer Vertragsdigest:

`495139baff29222708e261d0be4c949cf403b6dd6af267670da8774d84cfaf41`

## Grenzen

S1-KV fuehrt keine Replik und kein Intervall aus. Die 24-Fall-Matrix,
weitere Rollen und Profile, Baseline- und Kandidatenurteile,
Runtimeintegration und Forschungslaeufe bleiben geschlossen.

## Naechster zulaessiger Schritt

S1-KW darf ausschliesslich den naechsten einzelnen registrierten Fall samt
Frischstarts, Carry-Regeln, Digestrollen und endlichem Budget auswaehlen.
Methodisch folgt B1/P_IK. Noch keine Implementierung oder Ausfuehrung.
