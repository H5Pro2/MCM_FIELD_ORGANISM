# S1-EC91: Separate r4/r8-Receipts und reine Konverter

## Korrektur

S1-EC91 behebt die in EC90 lokalisierte Schrittsperre durch eine neue,
parallele Schicht. Die real bestaetigten EC63-/EC64-r2-Dateien bleiben
unveraendert.

Neue Bildungs- und Probequittungen binden die Refinement-ID und akzeptieren
ausschliesslich:

- `r4`: 804 Schritte je Bildung und 400 je Probe;
- `r8`: 1.608 Schritte je Bildung und 800 je Probe.

Die reinen Konverter pruefen weiterhin Arm, Refinement, Assignment- und
Envelope-Digest, Quellsupportzahl, Zustandsroute, Binding-Digest,
Backreaction-Modus und den eingefrorenen Zustandsdigest.

## Synthetische Abnahme

Aus typisierten synthetischen EC8-/EC54-Ausgabeobjekten werden fuer jede
Verfeinerung vier Bildungs- und acht Probequittungen erzeugt. Die
abgerechneten Budgets sind exakt 6.416 fuer `r4` und 12.832 fuer `r8`.
Alle Rollen- und Zustandsrouten stimmen; tatsaechlich ausgefuehrte
Feldschritte: null.

## Grenzen

S1-EC91 ruft keine Wrapper oder Feldkerne auf, persistiert nichts und
autorisiert keine Ausfuehrung. Ein synthetischer Konvertererfolg belegt keine
reale Laufzeitfaehigkeit und erlaubt keine EC46-Entscheidung. Es besteht kein
Memory-, Feldzeit-, Organisations-, Topologie-, Semantik-,
Selbstregulations- oder KI-Nachweis.

Am besten geht es mit S1-EC92 weiter: einen separaten synthetischen
`r4/r8`-Koordinator ueber EC89 und EC91 bauen, der frische Felder,
Zustandsrouten, Budgets und eine atomare Skalarreduktion vollstaendig
abnimmt. Keine reale Ausfuehrung.
