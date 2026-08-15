# S1-KF: Dualer Digest im B1/P_IE/r2-Runner

## Ergebnis

S1-KF implementiert den S1-KE-Vergleichspayload und beide Digestrollen nur
im bestehenden `B1:P_IE_CAUSAL_TWO_SUBSTEP:r2`-Runner.

## Ablauf

Der Runner erzeugt weiterhin dieselben vier Checkpoints, acht signed
Komponenten und vier Adapterdiagnostikrecords. Danach:

1. Der identitaetsneutrale S1-KE-Vergleichspayload wird gebildet und als
   `refinement_comparison_digest` digestiert.
2. Der vollstaendige v2-Replikoutput nimmt diesen Vergleichsdigest auf.
3. Der gesamte identitaetstragende Payload wird als `output_digest`
   digestiert.

Beide Digests muessen vorhanden und gueltig sein, sonst wird kein Output
veroeffentlicht.

## Technische Abnahme

Zwei unabhaengige r2-Wiederholungen wurden mit insgesamt acht Intervallen
ausgefuehrt. Beide vollstaendigen Ausgaben sind bitidentisch.

V2-Provenienzdigest beider Wiederholungen:

`07325bb2d4c739483d7eea2dbe7110e8f5efe315a31946f937988f7dabc2882a`

Refinement-Vergleichsdigest beider Wiederholungen:

`276f2891e11e2e5a0b22f8dbf65594dc26e217bec28a526a02632bc20334d589`

Die acht signed Komponenten bleiben null. Das ist weiterhin nur die
technische Identitaet der beiden gebundenen Expositionen unter B1 und kein
Matrix- oder Kandidatenbefund.

Der historische S1-KC-v1-Outputdigest bleibt in dessen Receipt erhalten und
wird nicht rueckwirkend ersetzt.

Entscheidung:

`R2_RUNNER_DUAL_PROVENANCE_AND_REFINEMENT_COMPARISON_DIGESTS_IMPLEMENTED_TWO_BIT_IDENTICAL_REPEATS`

Kanonischer Receipt-Digest:

`ab0d783e83a6d905428da2b87c5be32090e866191abe30c0cee90835ff80e7ff`

## Ausfuehrungsgrenze

r4 und r8 wurden weder implementiert noch ausgefuehrt. Keine andere Replik,
kein vollstaendiger Matrixfall und keine Runtimeintegration wurden
freigegeben.

## Naechster zulaessiger Schritt

S1-KG darf ausschliesslich die endliche Erweiterung auf die registrierten
B1/P_IE-Repliken r4 und r8 binden. Jede Replik muss separat frisch starten,
einen atomaren v2-Output liefern und ihren Vergleichsdigest gegen den
gebundenen r2-Wert pruefen. Das spaetere Ausfuehrungsbudget betraegt
hoechstens acht neue Intervalle. Noch keine Implementierung oder Ausfuehrung
von r4/r8, keine andere Rolle, kein Matrixfall, keine Runtime und keine
Forschungsprobe.
