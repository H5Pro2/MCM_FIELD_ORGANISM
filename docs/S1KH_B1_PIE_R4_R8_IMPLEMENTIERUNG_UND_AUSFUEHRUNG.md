# S1-KH: B1/P_IE-r4/r8-Implementierung und Ausfuehrung

## Ergebnis

S1-KH implementiert genau die in S1-KG gebundenen Runner-IDs r4 und r8 und
fuehrt beide als ein atomar angenommenes Paar aus.

## Ausfuehrung

- eine r4-Replik mit vier Intervallen;
- eine r8-Replik mit vier Intervallen;
- insgesamt acht neue Intervalle;
- keine Wiederholung, kein Retry und kein Ersatz;
- getrennte Frischstarts pro Replik und pro P_IE-Sequenz.

Jeder Output enthaelt vier Checkpoints, acht signed Komponenten, vier
Diagnostikrecords und beide S1-KE-Digestrollen.

## Digestabnahme

r4-Provenienzdigest:

`fe590916fb6608e91f8f1661859b3ef556ae81c835fa28ecf15484bec291d1f7`

r8-Provenienzdigest:

`047716609ea3aa9289eb376e2cd975bb9b28188eac925b4756b904a293c6f986`

Vergleichsdigest von r2, r4 und r8:

`276f2891e11e2e5a0b22f8dbf65594dc26e217bec28a526a02632bc20334d589`

Die drei vollstaendigen Provenienz-Digests sind verschieden, weil sie ihre
Replik- und Refinementidentitaet tragen. Die identitaetsneutralen
Vergleichsdigests sind bitidentisch. Damit besteht die gebundene technische
B1-Kontrolle ueber alle drei Refinements.

Die acht signed Komponenten bleiben fuer jedes Refinement null. Das ist nur
die erwartete Gleichheit der beiden P_IE-Expositionen unter demselben festen
Adapter. Es ist kein Kandidatenbefund und kein allgemeiner Baselineabschluss.

Entscheidung:

`B1_P_IE_R4_R8_IMPLEMENTED_EIGHT_INTERVALS_COMPARISON_IDENTICAL_THREE_REFINEMENT_SET_ACCEPTED`

Kanonischer Receipt-Digest:

`d9a1216ad04463a633c6d773c37a368eebab0945165fdf3a4dfb438dd8f9d604`

## Publikationsgrenze

Das Drei-Refinement-Vergleichsset ist technisch angenommen. Ein formales
Matrixfall-Output wurde noch nicht zusammengesetzt oder publiziert. Andere
Rollen, die 24-Fall-Matrix, Schwellen, Rankings, Kandidatenvergleich und
Runtimeintegration bleiben geschlossen.

## Naechster zulaessiger Schritt

S1-KI darf ausschliesslich ein atomar zusammengesetztes technisches
B1/P_IE-Falloutputschema aus den bereits gebundenen r2/r4/r8-Receipts
definieren. Es muss Provenienz, gemeinsamen Vergleichsdigest und die acht
Komponenten binden. Keine neue Replika- oder Intervallausfuehrung, keine
weitere Rolle, keine 24-Fall-Matrixpublikation, keine Runtime und keine
Forschungsprobe.
