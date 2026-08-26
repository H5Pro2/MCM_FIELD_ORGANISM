# S1-KO: Korrigierter B1/P_IE-C01-Falloutput

## Ergebnis

S1-KO setzt den technischen Fallrecord C01 erneut zusammen. Verwendet werden
der unveraenderte B1/r2-Provenienzoutput und die in S1-KN korrigierten
B1/r4- und B1/r8-Provenienzoutputs. Es wird keine Replik erneut ausgefuehrt.

Der neue Fallrecord bindet:

- drei getrennte und korrekte Provenienz-Digests;
- den unveraenderten gemeinsamen Refinement-Vergleichsdigest;
- je acht bitidentische signed Komponenten fuer r2, r4 und r8;
- r4 weiterhin als Primaerausgabe;
- die gueltige Checkpoint-Eltern-Identitaet aller drei Repliken.

Alle signed Komponenten sind null. Dies bleibt eine technische
Refinementkontrolle der B1-Gegenbaseline und ist kein Baseline- oder
Kandidatenurteil.

Korrigierter Falloutputdigest:

`2b2fcb698aa8a57ec0c321370fb7f2f587f28847985d7c605d44ca4fbc2e7f41`

Entscheidung:

`C01_CORRECTED_PROVENANCE_CASE_OUTPUT_BOUND_FROM_R2_AND_S1KN_RECEIPT_NO_NEW_EXECUTION`

Kanonischer Vertragsdigest:

`f97b306256c42ab9872f7db71ad5605f18a97a274052ba96430c7b0e2244cfa0`

## Historischer Record

Der bisherige S1-KI-C01-Record und sein Digest bleiben unveraendert als
historischer Record erhalten. Er wird nicht als korrigierte
Provenienzgrundlage verwendet und nicht ueberschrieben.

## Grenzen

S1-KO fuehrt keine Replik und kein Intervall aus. C05 und die 24-Fall-Matrix
bleiben unpubliziert. Baselineabschluss, Kandidatenvergleich,
Runtimeintegration und Forschungslaeufe bleiben geschlossen.

## Naechster zulaessiger Schritt

S1-KP darf ausschliesslich den technischen C05-Fallrecord aus den bereits
gebundenen B2/r2-, r4- und r8-Ausgaben zusammensetzen. Keine neue Ausfuehrung,
keine weitere Rolle, keine Matrixpublikation und kein Urteil.
