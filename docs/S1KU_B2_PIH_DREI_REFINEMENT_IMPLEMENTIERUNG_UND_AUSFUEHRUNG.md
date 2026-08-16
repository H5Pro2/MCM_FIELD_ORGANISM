# S1-KU: B2/P_IH-Drei-Refinement-Implementierung und Ausfuehrung

## Ergebnis

S1-KU erweitert den privaten Runner exakt um B2/P_IH r2, r4 und r8. Jede
Replik wurde einmal ausgefuehrt; zusammen wurden neun Intervalle durch den
vorhandenen B2-S2-Adapter verarbeitet.

Jeder atomare v2-Output besitzt drei Checkpoints, acht signed Komponenten
und drei Diagnostikrecords. Alle Checkpoint-IDs stimmen mit ihrer
Eltern-Replik-ID ueberein. Die drei privaten L-Digests innerhalb jeder
A-A-A-Sequenz sind verschieden und ihre Folge ist ueber r2/r4/r8
bitidentisch.

## Technische Ausgaben

Provenienz-Digests:

- r2: `e977b20a146f5150c30cb041a5f996cb2cbc394f5fc5e53228922faa42865e61`
- r4: `a12a458e9f8cdf22f5051dda94ad19bc759c39ceef36b45dd52347b2b90e0c7f`
- r8: `64b63aa3bdc34103598ac4dcb8b636169a0a9719003d5215a5a3f605a9f76743`

Gemeinsamer Vergleichsdigest:

`746e8d3954e8894b136a78518c78a6544d9043181c639a811cab4a3aaf059890`

Die acht vorzeichenbehafteten Komponenten sind klein, nicht null und ueber
alle drei Refinements bitidentisch. Dies bestaetigt nur einen reproduzierbaren
technischen B2-Zustandsverlauf unter der registrierten P_IH-Exposition. Ein
Schwellen-, Baseline- oder Kandidatenurteil folgt daraus nicht.

Entscheidung:

`B2_PIH_R2_R4_R8_IMPLEMENTED_NINE_INTERVALS_COMPARISON_IDENTICAL_SET_ACCEPTED`

Receipt-Digest:

`c8568cdad103f2fa86295119e24578e32f9169e354b1e0e981d73aadeb36a9f7`

## Grenzen

C06 wurde noch nicht als Falloutput zusammengesetzt. Weitere Rollen und
Profile, die 24-Fall-Matrix, Baseline- und Kandidatenurteile,
Runtimeintegration sowie Forschungslaeufe bleiben geschlossen.

## Naechster zulaessiger Schritt

S1-KV darf ausschliesslich den technischen C06-Fallrecord aus den drei
bereits gebundenen S1-KU-Ausgaben zusammensetzen. Keine neue Replik oder kein
neues Intervall.
