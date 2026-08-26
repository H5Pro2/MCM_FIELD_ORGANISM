# S1-LG: B2/P_IN-Drei-Refinement-Implementierung und Ausfuehrung

## Ergebnis

S1-LG erweitert den privaten Ein-Replik-Runner exakt um die drei in S1-LF
gebundenen B2/P_IN-IDs r2, r4 und r8. Jede Replik wurde genau einmal
ausgefuehrt. Pro Replik starteten `P_IN_RECOVERY_ON` und
`P_IN_RECOVERY_OFF` unabhaengig aus dem korrigierten B2-Dreiknoten-
Frischzustand mit vollstaendigem Null-L-Zustand. Insgesamt wurden 24
Intervalle materialisiert und durch den vorhandenen linearen Integrator
verarbeitet.

Die Runnerhuelle akzeptiert fuer P_IN zwei terminale Checkpoints, sechs
signed Komponenten und acht Adapterdiagnostikrecords pro Replik. Die
Checkpoint-IDs stimmen mit ihren Eltern-Replik-IDs ueberein. Fixturewerte,
Integratorfunktion und Feldkern wurden nicht geaendert.

## Technische Ausgaben

Vollstaendige Provenienz-Digests:

- r2: `9dd027f4b2c85ce7ca880a803d439f9966f05f673173dde95a4d921793ecf235`
- r4: `4aeede70cf05b60001a898fe8c6fc797c2eac1509813910d9c7d1b6fe6f63c3d`
- r8: `34f563a1ca845377ac0f82a2cf51264bc05e3d019d34ff33b98078a2d5a29602`

Gemeinsamer Refinement-Vergleichsdigest:

`9c584ba209a152b31acd6b3c03392102fe65e98817c6c2fe697ad6d3d5bb86a4`

Alle sechs signed Komponenten sind null und ueber r2/r4/r8 bitidentisch.
Recovery-on und Recovery-off besitzen jeweils dieselben terminalen Digests:

- Feld: `b879ad4b1d0bb0e17980116a0cb29cabf8d78c7b4ca5a12937334f300e5b8c83`
- privater L-Zustand: `69506c49f207cd7fd80a58ccaf083a3291354f28df9b323d256ac51c7962e035`
- Adapteroutput: `399c7c4527374ae5caa3655aa7fe24bd705a548238da018e7c1f7b02288a2a5c`

Damit bildet der lineare Integrator den Recovery-on/off-Unterschied in
diesem Profil technisch nicht ab. Das ist kein Freigabe-,
Wiederverwendungs-, Baseline- oder Kandidatenurteil.

Entscheidung:

`B2_PIN_R2_R4_R8_IMPLEMENTED_TWENTY_FOUR_INTERVALS_COMPARISON_IDENTICAL_SET_ACCEPTED`

Receipt-Digest:

`4afe0ca4c220e04e745d2dee109d31af14d12d63a2363eac03bf9301b0cdbc27`

## Grenzen

C08 wurde noch nicht als Falloutput zusammengesetzt. Weitere Rollen und
Profile, die 24-Fall-Matrix, Baseline- und Kandidatenurteile,
Runtimeintegration sowie Forschungslaeufe bleiben geschlossen.

## Naechster zulaessiger Schritt

S1-LH darf ausschliesslich den technischen C08-Fallrecord aus den drei
bereits gebundenen S1-LG-Ausgaben zusammensetzen. Keine neue Replik und kein
neues Intervall und noch keine weitere Fallauswahl.
