# S1-LD: B1/P_IN-Drei-Refinement-Implementierung und Ausfuehrung

## Ergebnis

S1-LD erweitert den privaten Ein-Replik-Runner exakt um die drei in S1-LC
gebundenen B1/P_IN-IDs r2, r4 und r8. Jede Replik wurde genau einmal
ausgefuehrt. Pro Replik starteten `P_IN_RECOVERY_ON` und
`P_IN_RECOVERY_OFF` unabhaengig aus dem korrigierten B1-Dreiknoten-
Frischzustand. Insgesamt wurden 24 Intervalle materialisiert und durch den
vorhandenen Fixed Adapter verarbeitet.

Die Runnerhuelle akzeptiert fuer P_IN zwei terminale Checkpoints, sechs
signed Komponenten und acht Adapterdiagnostikrecords pro Replik. Die
Checkpoint-IDs stimmen mit ihren Eltern-Replik-IDs ueberein. Fixturewerte,
Fixed-Adapter-Funktion und Feldkern wurden nicht geaendert.

## Technische Ausgaben

Vollstaendige Provenienz-Digests:

- r2: `26aca3dc6449088eecba25939f5e23f8e6605303bcb9adcdb3c6c2b95641a39e`
- r4: `d223066615372b443283babfad5d49e9350e812ceb85280475759e49351c9e7f`
- r8: `96b8189f72f08ea5acde11df3b898ac546b0bb3561c9a8450609b55b63864ea9`

Gemeinsamer Refinement-Vergleichsdigest:

`86262db028725dccebdfea9feed59d44f277fafee2c3bc62ec4d230183542542`

Alle sechs signed Komponenten sind null und ueber r2/r4/r8 bitidentisch.
Recovery-on und Recovery-off besitzen jeweils dieselben terminalen Digests:

- Feld: `96c508e5d2f4f660304772292e175008636fd10dcfa09eab798b15ad3aff0a1d`
- privater Fixed-Adapter-Zustand: `7f9afbe3dccf65514ba8dd5b61d6c24b5113c068655a05861fe1415ade374ee1`
- Adapteroutput: `a44ab12e30bafa9c8e93ad1fe915084972f013b2fff4037639fa19e4062b176e`

Damit bildet der Fixed Adapter den Recovery-on/off-Unterschied in diesem
Profil technisch nicht ab. Das ist kein Freigabe-, Wiederverwendungs-,
Baseline- oder Kandidatenurteil.

Entscheidung:

`B1_PIN_R2_R4_R8_IMPLEMENTED_TWENTY_FOUR_INTERVALS_COMPARISON_IDENTICAL_SET_ACCEPTED`

Receipt-Digest:

`c4eb4fa0b8c1c79979c6a9bf28fc15c765d9a45d155c48665ae69dd6df513169`

## Grenzen

C04 wurde noch nicht als Falloutput zusammengesetzt. Weitere Rollen und
Profile, die 24-Fall-Matrix, Baseline- und Kandidatenurteile,
Runtimeintegration sowie Forschungslaeufe bleiben geschlossen.

## Naechster zulaessiger Schritt

S1-LE darf ausschliesslich den technischen C04-Fallrecord aus den drei
bereits gebundenen S1-LD-Ausgaben zusammensetzen. Keine neue Replik und kein
neues Intervall und noch keine weitere Fallauswahl.
