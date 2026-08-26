# S1-KM: Versionierter B1-Checkpoint-Identitaetskorrekturvertrag

## Ergebnis

S1-KM bindet die Korrektur fuer die in S1-KL gefundenen acht falschen
Checkpoint-Replikidentitaeten. Jeder Checkpoint muss kuenftig dieselbe
`replica_id` wie sein uebergeordneter vollstaendiger Output tragen. Eine
Abweichung muss den gesamten Output ohne Teilwert verwerfen.

## Versionierung

S1-KM ist ein versionierter semantischer Overlay-Vertrag auf dem vorhandenen
v2-Outputschema. Feldreihenfolge und beide Digestalgorithmen bleiben
unveraendert. Dadurch kann der bestehende identitaetsneutrale
Vergleichsdigest bitidentisch bleiben: Die Checkpoint-Replik-ID ist bereits
eine ausdrueckliche S1-KE-Vergleichsausnahme.

Die historischen B1-r4/r8-v2-Ausgaben und ihre Digests bleiben unveraendert
als Belege des fehlerhaften Zustands erhalten. Korrigierte v2-Ausgaben
muessen neue vollstaendige Provenienz-Digests besitzen.

## Gebundene Neuausfuehrung

- nur B1/P_IE r4 und r8;
- beide Repliken genau einmal;
- vier Intervalle pro Replik, hoechstens acht insgesamt;
- kein Retry und keine Wiederholung;
- B1/r2 und alle B2/P_IE-Ausgaben bleiben unveraendert.

Numerische Checkpoints, Komponenten und Adapterdiagnostik muessen bitidentisch
zum historischen Inhalt bleiben. Beide Vergleichsdigests muessen weiterhin
dem gebundenen B1/r2-Vergleichsdigest entsprechen.

Entscheidung:

`VERSIONED_B1_R4_R8_CHECKPOINT_IDENTITY_CORRECTION_BOUND_EIGHT_CALL_BUDGET_NO_EXECUTION`

Kanonischer Vertragsdigest:

`c54b795f54dae25d76717ad974dd329493f5993ac9613a4922f24c2d930a9af1`

## Grenzen

S1-KM implementiert keine Korrektur und fuehrt keine Replik oder kein
Intervall aus. Historische Daten werden nicht umgeschrieben. C01, C05 und die
24-Fall-Matrix bleiben gesperrt; es wird kein Baseline- oder
Kandidatenurteil gefaellt.

## Naechster zulaessiger Schritt

S1-KN darf ausschliesslich die gebundene Identitaetsregel im Runner und im
vollstaendigen Outputvalidator implementieren und B1/r4 sowie B1/r8 je einmal
innerhalb des Acht-Intervall-Budgets neu ausfuehren.
