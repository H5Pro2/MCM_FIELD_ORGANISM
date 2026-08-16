# S1-KR: B1/P_IH-Drei-Refinement-Implementierung und Ausfuehrung

## Ergebnis

S1-KR erweitert den privaten Ein-Replik-Runner exakt um die drei in S1-KQ
gebundenen B1/P_IH-IDs r2, r4 und r8. Jede Replik wurde genau einmal
ausgefuehrt. Insgesamt wurden neun Intervalle materialisiert und durch den
vorhandenen festen B1-Adapter verarbeitet.

Die Runnerhulle akzeptiert nun registrierte Profilkardinalitaeten: P_IH
besitzt pro Replik drei Checkpoints, acht signed Komponenten und drei
Adapterdiagnostikrecords. Der Modellkern und die Fixtures wurden nicht
geaendert.

## Technische Ausgaben

Vollstaendige Provenienz-Digests:

- r2: `e8cdab0a89e4880319098003d42ebff948bdcb3653ad85d27df81d5b8ea6b0f1`
- r4: `3738f48bb755cd62513c8619a3c1b5b25d6d2956f83c0c641ff6b982ba1d6145`
- r8: `4e11d5f3bfd9a56d2cdf94920d95e7944a6c25a9ee3dca5365432f30deea81e5`

Gemeinsamer Refinement-Vergleichsdigest:

`bdaecf7e21313961d2a437215bd3278b9723b9d2cdbaec0903c4694ebfd0a300`

Alle Checkpoints tragen die korrekte Eltern-Replik-ID. Die drei
Provenienz-Digests sind verschieden; die identitaetsneutralen
Vergleichsdigests sind bitidentisch.

## Einordnung

Alle acht signed P_IH-Komponenten sind unter B1 fuer r2, r4 und r8 null.
Dies ist nur der technische Kontrollbefund fuer den festen Adapter unter der
registrierten A-A-A-Exposition. Daraus folgt weder eine Kandidatenaussage
noch ein Baselineabschluss.

Entscheidung:

`B1_PIH_R2_R4_R8_IMPLEMENTED_NINE_INTERVALS_COMPARISON_IDENTICAL_SET_ACCEPTED`

Receipt-Digest:

`692d1c959bdc119cceafd9430f86c5727cdbb580a8569a2c5c70765ad1f6782c`

## Grenzen

C02 wurde noch nicht als Falloutput zusammengesetzt. B2/P_IH, weitere
Rollen und Profile, die 24-Fall-Matrix, Baseline- und Kandidatenurteile,
Runtimeintegration sowie Forschungslaeufe bleiben geschlossen.

## Naechster zulaessiger Schritt

S1-KS darf ausschliesslich den technischen C02-Fallrecord aus den drei
bereits gebundenen S1-KR-Ausgaben zusammensetzen. Keine neue Replik oder kein
neues Intervall und noch keine B2/P_IH-Auswahl.
