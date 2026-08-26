# S1-KC: B1/P_IE/r2-Ein-Replik-Runner

## Ergebnis

S1-KC implementiert ausschliesslich die in S1-JZ gebundene technische
Beispielreplik `B1:P_IE_CAUSAL_TWO_SUBSTEP:r2`. Die in S1-KB korrigierte
Frischzustandsregistry wird dabei ohne weitere Parameterwahl verwendet.

## Implementierte Grenze

Der private Runner akzeptiert nur eine versionierte Eingabe aus `schema_id`
und der exakten Beispiel-Replik-ID. Alle anderen IDs und alle zusaetzlichen
Aufrufdaten werden fail-closed abgelehnt.

Die Frischzustandsfactory rekonstruiert den registrierten Zweiknoten-B1-
Feldzustand und den festen Adapterzustand. Feldpayload und Privatzustand
muessen ihre gebundenen Digests exakt reproduzieren.

Die beiden Sequenzen `P_IE_F_HIGH` und `P_IE_R_HIGH` starten voneinander
isoliert aus diesem Frischzustand. Innerhalb jeder Sequenz werden nur das
vollstaendige Feld, der private B1-Zustand sowie vorheriger Envelope- und
Outputdigest in Ordinalreihenfolge weitergegeben.

## Technische Ausfuehrung

Zwei deterministische Wiederholungen wurden ausgefuehrt:

- vier Intervalle pro Wiederholung;
- insgesamt acht Intervallaufrufe;
- vier vollstaendige Checkpoints pro Wiederholung;
- acht signed Komponenten in der S1-JZ-Reihenfolge;
- bitidentische vollstaendige Outputs.

Outputdigest beider Wiederholungen:

`bb098fbc3ce5d5da4c72b6b3da69ca789960e81e8299ca2a93621a66e4eea201`

Alle acht signed Komponenten sind null. Das folgt hier daraus, dass beide
Sequenzen dieselbe kausale Exposition unter demselben festen B1-Adapter
erhalten. Es ist kein abgeschlossener Matrixfall, kein allgemeines
Baselineurteil und keine Aussage ueber den DTS-1-Kandidaten.

Entscheidung:

`ONE_B1_P_IE_R2_REPLICA_RUNNER_IMPLEMENTED_TWO_BIT_IDENTICAL_TECHNICAL_REPEATS`

Kanonischer Receipt-Digest:

`59b721a33fddf278c2cc858db40aafdca270e33006ec0cc0cbca82cbfedf177c`

## Geschlossene Bereiche

Keine andere Replik oder Rolle wurde ausgefuehrt. r4 und r8 bleiben
geschlossen. Es gab keinen vollstaendigen Matrixfall, keine
Runtimeintegration und keine Forschungsprobe.

## Naechster zulaessiger Schritt

S1-KD darf ausschliesslich die endliche Runnererweiterung fuer die bereits
registrierten B1/P_IE-Repliken r4 und r8 binden. Zu binden sind getrennte
Frischstarts, erwartete B1-Bitidentitaet, atomare Outputs und ein festes
Aufrufbudget. Noch keine Implementierung oder Ausfuehrung von r4/r8, keine
andere Rolle, kein vollstaendiger Matrixfall, keine Runtime und keine
Forschungsprobe.
