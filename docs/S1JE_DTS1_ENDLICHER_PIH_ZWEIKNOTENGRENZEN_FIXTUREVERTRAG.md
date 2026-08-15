# S1-JE: Endlicher P_IH-Zweiknotengrenzen-Fixturevertrag

## Zweck

S1-JE bindet die endlichen Werte fuer die in S1-JD festgelegte gemeinsame
P_IH-Zweiknoten-A-Grenze. Der Zustand bleibt statisch: Ein entsprechender
Grenzoperator, die gemeinsame Intervallhuelle und Baselineadapter sind noch
nicht implementiert.

## Geometrie und Grenze

Die kanonische Geometrie ist die offene ungerichtete Zweiknotenlinie
`node-a -- node-b` mit genau einer Kante A. Alle Werte sind in IEEE-754
binary64 exakt darstellbar und liegen im normierten Feldbereich.

Gebunden sind:

- Rolle: `A_BOUNDARY_2N`
- S: `(-0.5,0.5)`
- H: `(0,0)`
- S1-HK-Beteiligung A: `0.25`

Die Beteiligung folgt unveraendert aus `((S_a-S_b)/2)^2`. S ist
antisymmetrisch, H ist bitgenau `+0.0`. Die Grenze uebernimmt weder den alten
P_IH-S-Vektor `(-1,1)` noch den alten H-Vektor `(-0.2,0.2)`.

## Intervallwerte

Jedes der drei P_IH-Aktivintervalle dauert exakt `0.5` synthetische
Zeiteinheiten. Der Rezeptorkontakt ist an beiden Knoten bitgenau `+0.0`. Der
Grenzoperator selbst verbraucht keine Zeit.

Alle drei Ereignisse verwenden bitidentische Grenzwerte, Dauer und Kontakt.
Diese Werte sind technische Fixturewerte und keine physische Zeitschaetzung.

## Toleranzen

Fixture-Digest, modelluebergreifende Grenzidentitaet, strukturelle Nullen,
Antisymmetrie und dyadische Beteiligung muessen bitgenau sein. Fuer spaetere
reine Bereichs- und Ledger-Rundungspruefungen gilt hoechstens
`1.1368683772161603e-13`. Eine Ergebnis-, Akzeptanz- oder Fit-Toleranz ist
nicht gebunden.

## Aufrufbudget

Die spaetere technische Pruefung umfasst sieben Modelle, drei Intervalle und
die drei bereits gebundenen Refinementstufen 2, 4 und 8. Daraus folgen pro
vollstaendiger einfacher Pruefung:

- 63 Grenzanwendungen,
- 63 Intervallaufrufe.

Die deterministische Doppelpruefung ist auf 126 Grenzanwendungen und 126
Intervallaufrufe begrenzt. Private interne Subschritte sind keine
zusaetzlichen Grenzanwendungen oder High-Level-Intervallaufrufe.
Forschungsfeldschritte bleiben null.

## Quarantaene und Entscheidung

Alte P_IH-Feldresultate duerfen nicht importiert, skaliert, angepasst oder
uminterpretiert werden. Direkte Ressourcenledger bleiben getrennte direkte
Evidenz. Das neue Feldprofil muss spaeter aus der korrigierten gemeinsamen
Exposition neu registriert werden.

Entscheidung:

`FINITE_P_IH_TWO_NODE_BOUNDARY_FIXTURE_BOUND_NO_IMPLEMENTATION_OR_EXECUTION`

Kanonischer Vertragsdigest:

`b1da58d2e2e1d6e6e7df1275a5fb6d51221f10866f746f18a7224ecccb745aae`

S1-JE zeigt keine numerische Zulaessigkeit, Baselinepassung oder
Kandidatenueberlegenheit. Speicher-, Lern- und KI-Claims bleiben gesperrt.

## Naechster zulaessiger Schritt

S1-JF darf ausschliesslich den privaten reinen Grenzoperator um die
Zweiknotenrolle erweitern und technisch pruefen. Noch keine gemeinsame
Intervallhuelle, kein Adapter- oder Modellaufruf, keine Runtime und keine
Forschungsprobe.
