# S1-EC56: Statischer EC55-Ergebnisaudit

## Gepruefter Befund

EC56 verwendet nur den berichteten, fluechtigen EC55-Rohbefund und fuehrt
EC55 nicht erneut aus.

Alle EC55-Grenzen bestehen:

- exakt n2/r2;
- exakt drei Rollen;
- exakt 1.002 Feldschritte;
- identische, objektgetrennte Ausgangsfelder;
- eingefrorener Zustand erhalten;
- Eingaben erhalten;
- positive Aktiv/Rueckwirkungsablationsdifferenz in Aktivierung und Nachhall;
- keine Vollmatrix, Persistenz, Entscheidung oder Claims.

Der begrenzte Befund lautet:

`real-wrapper-backreaction-route-technically-observable`

Dies ist weiterhin nur ein technischer Wrapperbefund.

## Kleinster naechster Kontrollumfang

Ein fairer AB/BA-Vergleich kann nicht durch einen einzelnen zusaetzlichen
BA-Slot entstehen. Alle Vergleichs- und Kontrollarme muessen im selben Lauf
aus frischen identischen Feldern gebildet werden.

Der kleinste vollstaendige Satz ist daher n2/r2 mit allen acht EC45-Rollen:

- vier Bildungszustaende zu je 402 Schritten: 1.608;
- acht Probe-Slots zu je 200 Schritten: 1.600;
- Gesamt: 3.208 Feldschritte.

Dieser Lauf kann nur eine grobe r2-Kontroll- und Vergleichsfixture sein. Ohne
r4/r8 besitzt er keine Verfeinerungsentscheidung und darf die EC46-
Akzeptanzregel nicht anwenden.

## Entscheidung

`WRAPPER_CONFIRMED_NEXT_MINIMUM_N2_R2_EIGHT_ROLE_FIXTURE`

Erlaubt ist nur die Implementierung dieses begrenzten Runners. Seine reale
Ausfuehrung, die Vollmatrix, Persistenz, Forschungsentscheidungen und Claims
bleiben gesperrt.

Neun fokussierte gemeinsame Tests bestehen.

Audit-Digest:
`959703db814d753744de67de65c216365ced4761fdfeb5f874916c94cba0340d`

## Naechster Schritt

Am besten geht es mit S1-EC57 weiter: den n2/r2-Acht-Rollen-Runner
implementieren und zuerst nur durch injizierte Nullschritt-Receipts sowie
einen statischen Schrittzaehler abnehmen.
