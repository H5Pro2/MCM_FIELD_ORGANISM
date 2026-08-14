# S1-EC57: Synthetische n2/r2-Acht-Rollen-Runner-Fixture

## Ziel

EC57 implementiert ausschliesslich den in EC56 freigegebenen begrenzten
Runner fuer `n2/r2`. Alle Kernstufen bleiben injiziert und liefern
Nullschritt-Receipts.

## Matrix

- ein n2/r2-Planreceipt;
- vier Bildungszustandsreceipts;
- acht getrennte Fresh-Field-Receipts;
- acht Probe-Receipts in der EC45-Rollenreihenfolge.

Die statische Last ist exakt gebunden:

- Bildung: 4 * 402 = 1.608 Schritte;
- Probe: 8 * 200 = 1.600 Schritte;
- Gesamt: 3.208 Schritte.

In EC57 werden davon exakt null ausgefuehrt.

## Kontrollen

- alle vier Zustandsrouten stimmen;
- neutrale und Frozen-E1-Proberouten stimmen;
- Rueckwirkung ist rollengetreu an oder aus;
- alle Ausgangsfelder tragen denselben Digest und acht getrennte
  Objekttokens;
- keine EC46-Entscheidung, da r4/r8 fehlen;
- keine Persistenz, Forschungsentscheidung oder Claims.

Zwoelf fokussierte gemeinsame Tests bestehen.

Fixture-Digest:
`73009f5847200ad8497b454482f8e7e33320c53ecd325b124314ea7720a4758d`

## Naechster Schritt

Am besten geht es mit S1-EC58 weiter: statischer Real-Preflight fuer genau
diese 3.208-Schritt-Fixture. Ressourcen, geschuetzte Artefakte,
Nichtpersistenz und eine separate ausdrueckliche Einmallauffreigabe muessen
vor jeder realen Ausfuehrung gebunden werden.
