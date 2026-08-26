# W7-BA: Vertrag fuer dimensionslosen CAP-Observer-Profilvergleich

## Entscheidung

`CAP_OBSERVER_DIMENSIONLESS_PROFILE_COMPARISON_PREREGISTERED`

W7-BA bindet wertfrei den einzigen zulaessigen Vergleich zwischen den zwei
CAP-Profilen aus W7-AZ und den sechs LEAK-/SAT-/NORM-Profilen aus W7-AX. Der
Vertrag nimmt keine Profilwerte entgegen und trifft keine Auswahl.

## Vergleichsraum

Absolute CAP-Feldamplituden und Observerausgaben duerfen nicht miteinander
verglichen werden. Zulaessig sind nur die drei bereits dimensionslosen
Kurven `old_b_retention`, `old_g_retention` und `new_b_gain` mit jeweils
fuenf Checkpoints.

Alle verglichenen Profile muessen technisch `RESOLVED` sein. Andernfalls ist
das einzige Ergebnis `NOT_RESOLVED`; es gibt keine Epsilonrettung.

## Distanz und Auswahl

Pro Modell und Richtung wird der Linf-Abstand ueber alle 15 Profilkoordinaten
gebildet. Der Modellabstand ist das Maximum aus AB und BA. Ein Modell passt
nur bei einem Abstand kleiner oder gleich `0.05`.

Bei mehreren Treffern gilt unveraendert die Reihenfolge
`LEAK > SAT > NORM`. Zulaessige spaetere Ergebnisse sind ausschliesslich:

- `NOT_RESOLVED`;
- `PROFILE_NOT_MATCHED`;
- `PROFILE_EXPLAINED_BY_LEAK`;
- `PROFILE_EXPLAINED_BY_SAT`;
- `PROFILE_EXPLAINED_BY_NORM`.

Die neutrale Neu-Kontaktkurve bleibt Quellen-Auditkontrolle und wird nicht
nachtraeglich als vierte Profilkoordinate eingefuehrt.

## Aussagegrenze

Auch eine spaetere Observererklaerung bedeutet nur, dass ein externes
einfaches Modell die Form der CAP-Lebenszyklusprofile innerhalb der
vorregistrierten Grenze reproduziert. Sie ist weder Organismusfunktion noch
Feld-, Ressourcen-, Memory-, Feldzeit-, Organisations-, Semantik- oder
KI-Befund.

## Naechster Schritt

W7-BB darf einen reinen terminalen In-Memory-Auswerter implementieren, der
die vorhandenen W7-AX- und W7-AZ-Profile genau einmal vergleicht und eines
der fuenf Ergebniswoerter liefert. Er darf nichts zur Runtime zurueckschreiben.
