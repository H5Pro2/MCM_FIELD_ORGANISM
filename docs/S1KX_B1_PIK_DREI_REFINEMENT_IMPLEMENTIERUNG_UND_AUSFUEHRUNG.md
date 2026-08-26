# S1-KX: B1/P_IK-Drei-Refinement-Implementierung und Ausfuehrung

## Ergebnis

S1-KX erweitert den privaten Ein-Replik-Runner exakt um die drei in S1-KW
gebundenen B1/P_IK-IDs r2, r4 und r8. Jede Replik wurde genau einmal
ausgefuehrt. Pro Replik starteten `P_IK_A_B_A` und `P_IK_A_GAP_A`
unabhaengig aus dem korrigierten B1-Dreiknoten-Frischzustand. Insgesamt
wurden 24 Intervalle materialisiert und durch den vorhandenen festen
B1-Adapter verarbeitet.

Die Runnerhuelle akzeptiert fuer P_IK zwei terminale Checkpoints, sechs
signed Komponenten und acht Adapterdiagnostikrecords pro Replik. Die
Checkpoint-IDs stimmen mit ihren Eltern-Replik-IDs ueberein. Modellkern,
Fixturewerte und Adaptergleichung wurden nicht geaendert.

## Technische Ausgaben

Vollstaendige Provenienz-Digests:

- r2: `106902d3a4e535f17f3e48142b3bec0fcd7e9f2c653622b5b57deda85cd224e9`
- r4: `6c35c58458bf420cfefc37e995619cf6f9414454d75ef3c22b2567ad0d7ce9e3`
- r8: `965d6cf82736cdeb9a20e7232067b4d151d1addf39a61f43c82f2526c3d46f6f`

Gemeinsamer Refinement-Vergleichsdigest:

`ac5ee2079516a3b336336e2697859b7504ec24dc897d88a1e0bccce0cf07d799`

Die beiden terminalen Feld-, Privat- und Adapteroutput-Digests sind innerhalb
jeder Replik jeweils bitidentisch. Auch die sechs signed Komponenten sind
fuer r2, r4 und r8 null. Dies ist nur der technische Kontrollbefund des
festen B1-Adapters unter den getrennten registrierten A-B-A- und A-Gap-A-
Expositionen. Daraus folgt weder ein Interferenzbefund noch ein
Baselineabschluss oder eine Kandidatenaussage.

Entscheidung:

`B1_PIK_R2_R4_R8_IMPLEMENTED_TWENTY_FOUR_INTERVALS_COMPARISON_IDENTICAL_SET_ACCEPTED`

Receipt-Digest:

`aebf334b2c1113a91e871c6aecb079fa9a8d559d12ee943238a28bee403a38b4`

## Grenzen

C03 wurde noch nicht als Falloutput zusammengesetzt. B2/P_IK, weitere Rollen
und Profile, die 24-Fall-Matrix, Baseline- und Kandidatenurteile,
Runtimeintegration sowie Forschungslaeufe bleiben geschlossen.

## Naechster zulaessiger Schritt

S1-KY darf ausschliesslich den technischen C03-Fallrecord aus den drei
bereits gebundenen S1-KX-Ausgaben zusammensetzen. Keine neue Replik und kein
neues Intervall und noch keine B2/P_IK-Auswahl.
