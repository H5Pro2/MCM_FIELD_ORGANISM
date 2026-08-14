# S1-FC: Statischer E1-Bildungszustands-Konvergenzvertrag

## Forschungsfrage

Konvergiert bereits der durch AV-Geschichte gebildete E1-Endzustand ueber
r2/r4/r8, bevor eine spaetere Probe und deren Feldantwort hinzukommen?

## Gebundene Zustandsdaten

Der Vertrag verlangt fuer r2, r4 und r8 jeweils fuenf vollstaendige,
kanonisch kantenweise geordnete Belegungsvektoren:

- aktives AB;
- aktives BA;
- identisches wiederholtes AB;
- bildungsablatiertes AB;
- bildungsablatiertes BA.

Damit sind 15 Zustandsvektoren erforderlich. Jeder Vektor bindet
Kanteninventar, Kantenreihenfolge, Zustands- und Quellergebnisdigest sowie den
Ressourcenbilanzfehler. Die Rueckgabe muss atomar erfolgen.

## Getrennte Auswertung

Aus aktivem AB und BA wird fuer jede Verfeinerung ein eigener
AB-minus-BA-Ordnungsvektor gebildet. Grob-/Feinabstaende und relative
Feinabstaende werden getrennt berechnet fuer:

- den AB-Zustand;
- den BA-Zustand;
- den AB-minus-BA-Ordnungsvektor.

Zusaetzlich muessen Identitaetswiederholung, beide Bildungsablationen und jede
Ressourcenbilanz innerhalb `1e-12` bleiben. Fuer die drei
Konvergenzfamilien gilt die bereits vor S1-FC bestehende relative
Verfeinerungsgrenze `0.01`; sie wird nicht aus spaeteren Zustandsdaten
abgeleitet.

## Projektgrenze

S1-FC untersucht Bildung vor der Probe. Der Vertrag ersetzt EC46 nicht und
aendert keine EC46-Schwelle. Selbst ein konvergenter E1-Bildungszustand waere
nur ein numerischer Substratbefund, kein Nachweis von Memory, Feldzeit,
Organisation, Semantik, Selbstregulation oder KI.

Es wurden keine Zustandsvektoren erzeugt, kein Feld ausgefuehrt und kein
historischer Lauf rekonstruiert. Entscheidung:
`FORMATION_STATE_CONVERGENCE_BOUND_IMPLEMENTATION_MISSING`.

## Bester naechster Schritt

Am besten geht es mit S1-FD weiter: einen rein synthetischen Evaluator fuer
die 15 Zustandsvektoren implementieren und mit konvergenten, nicht
konvergenten sowie kontrollverletzenden Fixtures abnehmen. Keine reale
Bildung und keine Laufautorisierung.
