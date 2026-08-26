# S1-KD: STOPP Refinementidentitaet im vollstaendigen Outputdigest

## Ergebnis

S1-KD stoppt die geplante Erweiterung des B1/P_IE-Runners auf r4 und r8 vor
jeder Implementierung und Ausfuehrung. Die bestehende Refinement-
Vergleichsregel und das vollstaendige Outputschema sind nicht miteinander
vereinbar.

## Konflikt

S1-JX fordert fuer B1 und B2 bitidentische vollstaendige Replik-
Outputdigests ueber r2, r4 und r8.

Der vollstaendige S1-JZ-Output enthaelt zugleich:

- `replica_id`, die bei r2, r4 und r8 verschieden ist;
- `refinement`, das die Werte 2, 4 und 8 traegt;
- vollstaendige Checkpoints, die jeweils erneut `replica_id` enthalten.

S1-KC berechnet den Outputdigest ueber diesen vollstaendigen Payload. Damit
muessen die drei Provenienz-Digests verschieden sein, selbst wenn alle
Feldwerte, Privatzustaende, Adapterausgaben und signed Komponenten
bitidentisch waeren. Ein Gleichheitskriterium fuer diese vollstaendigen
Digests ist daher unerfuellbar und wuerde eine korrekte Ausfuehrung falsch
verwerfen.

## Ausfuehrungsgrenze

r4 und r8 wurden weder implementiert noch ausgefuehrt. Es gab keinen neuen
Materializer-, Adapter- oder Intervallaufruf, keine weitere technische
Replik, keinen Matrixfall und keine Runtimeintegration. Der gueltige
S1-KC-r2-Stand bleibt unveraendert.

Entscheidung:

`STOPP_B1_REFINEMENT_BIT_IDENTITY_CONFLICTS_WITH_IDENTITY_BEARING_COMPLETE_OUTPUT_DIGEST`

Kanonischer Auditdigest:

`fa51056bfaa3a916a3adec45697cfeb069d4009a557405e55ea299673bf0611f`

## Erforderliche Korrektur

Der naechste Vertrag muss zwei Rollen trennen:

- Der vollstaendige identitaetstragende Outputdigest bleibt fuer Provenienz
  und Manipulationsnachweis erhalten und darf zwischen Refinements
  verschieden sein.
- Ein separater Refinement-Vergleichsdigest muss nur den vorab gebundenen
  vergleichbaren Inhalt erfassen.

Die ausschließlich im Vergleich ausgeschlossenen Replik- und
Refinementidentitaetsfelder muessen exakt aufgelistet werden. Die S1-JX-
Bitidentitaetsregel und das S1-JZ-Outputschema sind entsprechend zu
korrigieren. Numerische Werte, Checkpointinhalt oder Diagnostik duerfen nicht
verdeckt aus dem Vergleich entfernt werden.

## Naechster zulaessiger Schritt

S1-KE darf nur diese dualen Digestrollen, den exakten neutralen
Vergleichspayload, seine Ausschlussliste und die korrigierten S1-JX-/S1-JZ-
Regeln binden. Noch keine r4/r8-Runnerimplementierung oder -Ausfuehrung, kein
vollstaendiger Matrixfall, keine andere Rolle, keine Runtime und keine
Forschungsprobe.
