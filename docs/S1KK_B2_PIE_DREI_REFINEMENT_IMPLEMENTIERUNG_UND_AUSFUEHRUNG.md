# S1-KK: B2/P_IE-Drei-Refinement-Implementierung und Ausfuehrung

## Ergebnis

S1-KK erweitert den privaten Ein-Replik-Runner exakt um die drei in S1-KJ
gebundenen IDs fuer B2 und `P_IE_CAUSAL_TWO_SUBSTEP`: r2, r4 und r8. Jede
Replik wurde genau einmal ausgefuehrt. Insgesamt wurden zwoelf Intervalle
materialisiert und durch den vorhandenen privaten B2-S2-Adapter verarbeitet.

## Technische Ausgaben

Vollstaendige Provenienz-Digests:

- r2: `881fc449aa7bcad3af2a2a9db3733020514f18842735488eebeb8331be3a71ff`
- r4: `86c612c31fd18015079301828e0255c8d7deca9f6de3432b0a676bdbb8421de0`
- r8: `3e86ef71ae7291d0578952bbc9b8ddcdfda44793b0e1a8d883fe6b1a3ad74648`

Gemeinsamer Refinement-Vergleichsdigest:

`9b0b211b8f6459ec7c4be616c871c882be378af4ae6ea131a469e810dd9c29ae`

Alle drei Outputs besitzen vier Checkpoints, acht signed Komponenten und
vier B2-Adapterdiagnostikrecords. Die Provenienz-Digests sind wegen der
Replikidentitaeten verschieden; die identitaetsneutralen Vergleichsdigests
sind bitidentisch.

## Frischstart und Carry

Die beiden P_IE-Sequenzen beginnen in jeder Replik getrennt aus dem
korrigierten B2-Frischzustand. Ihr jeweils erster Checkpoint reproduziert
denselben privaten L-Digest. Der zweite Checkpoint besitzt nach dem genau
sequenzlokalen Carry einen anderen, zwischen beiden Sequenzen wiederum
identischen L-Digest. Es gibt keinen Carry zwischen Sequenzen oder
Refinements.

## Einordnung

Die acht signed P_IE-Komponenten sind fuer r2, r4 und r8 jeweils null. Das
bestaetigt nur, dass die beiden registrierten P_IE-Expositionen unter B2
technisch identische Readouts liefern und die Refinementkontrolle besteht.
Es ist kein Baselineabschluss und kein Kandidatenvergleich.

Entscheidung:

`B2_PIE_R2_R4_R8_IMPLEMENTED_TWELVE_INTERVALS_COMPARISON_IDENTICAL_SET_ACCEPTED`

Receipt-Digest:

`503a13050c22e4e33e553a4661411868e29b8b2c3e987eee2c3d962daf977e61`

## Grenzen

C05 wurde noch nicht als Falloutput zusammengesetzt. Die 24-Fall-Matrix,
andere Rollen und Profilbloecke, Baseline- und Kandidatenurteile,
Runtimeintegration sowie Forschungslaeufe bleiben geschlossen.

## Naechster zulaessiger Schritt

S1-KL darf ausschliesslich den technischen C05-Fallrecord aus den drei
bereits gebundenen S1-KK-Ausgaben zusammensetzen. Keine neue Replik oder kein
neues Intervall, keine weitere Rolle, keine Matrixpublikation und kein
Urteil.
