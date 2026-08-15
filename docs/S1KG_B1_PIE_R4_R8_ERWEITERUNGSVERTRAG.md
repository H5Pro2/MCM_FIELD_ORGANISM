# S1-KG: B1/P_IE-r4/r8-Erweiterungsvertrag

## Ergebnis

S1-KG bindet die endliche Erweiterung des dualen S1-KF-Runners auf genau
zwei bereits registrierte Kontrollrepliken:

- `B1:P_IE_CAUSAL_TWO_SUBSTEP:r4`;
- `B1:P_IE_CAUSAL_TWO_SUBSTEP:r8`.

Der Vertrag implementiert und startet diese Repliken noch nicht.

## Eingabe und Frischstarts

Die Runner-Eingabe bleibt auf `schema_id` und `replica_id` begrenzt.
Aufrufer duerfen weder Feldzustand, Privatzustand noch Parameter liefern.

r4 und r8 starten jeweils aus einem eigenen korrigierten B1-Frischzustand.
Innerhalb jeder Replik starten `P_IE_F_HIGH` und `P_IE_R_HIGH` ebenfalls
voneinander unabhaengig frisch. Kein Feld-, Privat- oder Provenienzzustand
darf zwischen r2, r4 und r8 uebertragen werden.

## Endliches Budget

- eine r4-Replik;
- eine r8-Replik;
- vier Intervalle pro Replik;
- hoechstens acht neue Intervallaufrufe insgesamt;
- keine Wiederholung und kein Retry.

## Atomare Abnahme

Jede Zielreplik muss einen vollstaendigen atomaren v2-Output mit beiden
Digestrollen liefern. r4 und r8 muessen jeweils exakt den gebundenen
r2-Vergleichsdigest reproduzieren:

`276f2891e11e2e5a0b22f8dbf65594dc26e217bec28a526a02632bc20334d589`

Die vollstaendigen Provenienz-Digests tragen verschiedene Replik- und
Refinementidentitaeten und werden deshalb nicht auf Gleichheit geprueft.

Nur wenn r4 und r8 beide erfolgreich sind, darf das Drei-Refinement-Set als
technisch angenommen gelten. Ein Fehler verwirft die gemeinsame Annahme ohne
Teilresultat, Reparatur, Wiederholung oder Ersatz.

Entscheidung:

`FINITE_B1_P_IE_R4_R8_DUAL_DIGEST_EXTENSION_BOUND_EIGHT_CALL_BUDGET_NO_EXECUTION`

Kanonischer Vertragsdigest:

`57305167b1d07803ac1d895d729c6b3f6b850561e766ab6e1d8028a0a00c3512`

## Geschlossene Bereiche

Die Runnererweiterung wurde nicht implementiert. r4 und r8 sowie neue
Intervalle wurden nicht ausgefuehrt. Andere Rollen, Schwellen, Rankings,
Baselineabschluss, Kandidatenvergleich, die 24-Fall-Matrixpublikation und
Runtimeintegration bleiben geschlossen.

## Naechster zulaessiger Schritt

S1-KH darf nur die beiden gebundenen IDs implementieren und r4 sowie r8 je
einmal mit insgesamt hoechstens acht neuen Intervallen ausfuehren. Beide
v2-Outputs muessen atomar gegen den r2-Vergleichsdigest geprueft werden.
Keine andere Rolle, keine 24-Fall-Matrixpublikation, keine Runtime und keine
Forschungsprobe.
