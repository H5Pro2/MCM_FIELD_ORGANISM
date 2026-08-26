# S1-EC49: Synthetische Acht-Rollen-Adapter-Fixture

## Ziel

EC49 implementiert den in EC48 geforderten engen Common-Probe-Adapter mit
injizierbaren Bildung-, Reset- und Probe-Kernschnittstellen. Die Abnahme
verwendet ausschliesslich synthetische typisierte Receipts.

## Datenfluss

Fuer jede Verfeinerung `r2`, `r4` und `r8` werden vier getrennte
Zustandsreferenzen uebergeben:

- aktiver AB-Zustand;
- aktiver BA-Zustand;
- bildungsablatierter AB-Zustand;
- bildungsablatierter BA-Zustand.

Anschliessend erzeugt der Adapter fuer jede der acht EC45-Rollen einen
eigenen Reset-Slot. Alle Slots tragen denselben initialen Felddigest, bleiben
aber logisch getrennte Objekte.

Die Rollen werden wie folgt gebunden:

- P0-reset: neutraler Kernel, kein E1-Zustand;
- E1 aktiv: passender aktiver Zustand, Rueckwirkung an;
- Probe-Rueckwirkungsablation: passender aktiver Zustand, Rueckwirkung aus;
- Bildungsablation: passender bildungsablatierter Zustand, Rueckwirkung an.

## Ergebnis

- drei synthetische Bildungshandoffs;
- 24 getrennte Reset-Slots;
- 24 typisierte Rollenreceipts;
- Zustandsrouten vollstaendig und exakt;
- Rueckwirkungsrouten vollstaendig und exakt;
- null Feldschritte;
- keine Persistenz;
- keine Forschungsentscheidung und kein Claim.

Die konstruierten Samples laufen erneut durch EC47 und EC46. Die dortige
synthetische klare Entscheidung bleibt nur eine Pfadabnahme.

Zwoelf fokussierte gemeinsame Tests bestehen.

Fixture-Digest:
`726a04e6c0e4f285e60962d520fba2cf48942e13e717dde9c591b305c35ee29c`

## Naechster Schritt

Am besten geht es mit S1-EC50 weiter: den injizierbaren Adapter statisch an
die vorhandenen realen Bildung-, Fresh-Field-, P0- und Frozen-E1-
Kernsignaturen binden. Noch keine reale Probeausfuehrung.
