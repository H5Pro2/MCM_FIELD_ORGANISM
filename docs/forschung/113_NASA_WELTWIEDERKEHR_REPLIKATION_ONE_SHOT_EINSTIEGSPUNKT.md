# NASA-Weltwiederkehr: vorabnahmegebundener One-Shot-Einstiegspunkt

## Gegenstand

Der sechsarmige Replikationslauf besitzt einen separaten Einstiegspunkt, der ausschließlich eine unveränderte positive Ausführungsvorabnahme akzeptiert. Die Implementierung dieses Gates hat keinen Replikationslauf gestartet.

## Gate-Bedingungen

Vor dem ersten Aufruf einer Ausführungsfunktion werden geprüft:

- positive Freigabe für genau einen begrenzten Lauf,
- unverbrauchte Vorabnahme und Wiederholungszahl `1`,
- identischer Medienpfad und identische Quellenkennung,
- passende Vorregistrierungs-, Kompatibilitäts- und Permutationsverträge,
- vollständige Verdrahtung aller sechs Arme,
- unveränderte Feldparameter,
- weiterhin aktive Sperren der zugrunde liegenden Runner- und Kompatibilitätsverträge.

## Einmaligkeit

Die Freigabe wird unmittelbar vor der Delegation an die injizierte Ausführungsfunktion verbraucht. Auch ein Fehler dieser Funktion gibt keine automatische Wiederholung frei. Ein zweiter Startversuch über denselben Einstiegspunkt wird abgewiesen.

## Testgrenze

Die Tests verwenden ausschließlich injizierte Stubs. Sie decodieren kein Medium, speisen keine Rezeptoren und führen keinen Feldlauf aus.

## Aussagegrenze

Der Einstiegspunkt definiert keine Erfolgsschwelle und erlaubt keine Memory-, Bedeutungs-, Organisations- oder KI-Claims.
