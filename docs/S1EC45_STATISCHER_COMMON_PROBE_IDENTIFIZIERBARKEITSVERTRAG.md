# S1-EC45: Statischer Common-Probe-Identifizierbarkeitsvertrag

## Anlass

EC44 wurde genau einmal und nicht persistent mit 25.368 Feldarm-Schritten
ausgefuehrt. Der technische Rohbefund zeigte fuer n1 keine P0- oder
E1-Reihenfolgekontraste. Fuer n2 zeigte bereits P0 einen stabilen terminalen
Reihenfolgekontrast. Deshalb darf der kleinere E1-Zustandskontrast nicht als
eigenstaendige E1-Wirkung interpretiert werden.

Der EC44-Ergebnisdigest lautet
`4de5d99e3a7c477520dffa120a3f74eac07aa8798fa9e9aad14a9af4141393a9`.
EC45 rekonstruiert oder persistiert das fluechtige Rohresultat nicht.

## Identifizierbarkeitsproblem

Die terminalen P0-Groessen sind geordnete Aktivierungs- und
Nachhallkomponenten des Feldes. Der gebildete E1-Zustand besteht aus
geordneten Kantenbindungen. Diese Zustandsraeume sind nicht kommensurabel.
Eine direkte Subtraktion oder ein Groessenvergleich ist unzulaessig.

## Gemeinsamer Beobachtungsraum

Ein spaeterer Vergleich muss alle Arme in denselben Beobachtungsraum bringen:

- identisches zurueckgesetztes Ausgangsfeld;
- identischer Probeimpuls;
- identische Neuronenreihenfolge;
- identische Probe-Schrittzahl;
- eingefrorener, zuvor gebildeter E1-Zustand;
- Messung derselben geordneten Aktivierungs- und Nachhallkomponenten.

Der Vertrag bindet acht Rollen:

1. P0 reset AB und BA;
2. E1 aktiv AB und BA;
3. E1 mit waehrend der Probe deaktivierter Rueckwirkung AB und BA;
4. E1 mit deaktivierter Bildung AB und BA.

P0 nach Feldreset ist die technische Sanity-Baseline. Rueckwirkungsablation
und Bildungsablation sind getrennte Kausalkontrollen. Nur spaetere
Probeantworten im gemeinsamen Beobachtungsraum duerfen verglichen werden.

## Entscheidung

`COMMON_PROBE_IDENTIFIABLE_ACCEPTANCE_BOUND_MISSING`

Der gemeinsame Probevergleich ist strukturell identifizierbar. Eine
Implementierung des kontrollierten Pfads ist erlaubt. Ein Feldlauf bleibt
gesperrt, weil noch keine vom Ergebnis unabhaengige numerische
Akzeptanzgrenze und Verfeinerungsregel vorregistriert wurde.

Es gibt keinen Memory-, Feldzeit-, Organisations- oder KI-Nachweis.

Vertragsdigest:
`6087bc99a8331671c077da4fc7b76959c7608611bbbda8c4815957e89c78ed00`

## Naechster Schritt

Am besten geht es mit S1-EC46 weiter: rein statisch eine numerische
Akzeptanz- und Verfeinerungsregel aus bestehenden Praezisions- und
Nullbaselinegrenzen ableiten. Die Grenze muss vor jeder Common-Probe-
Ausfuehrung feststehen und darf nicht anhand eines spaeteren Ergebnisses
angepasst werden.
