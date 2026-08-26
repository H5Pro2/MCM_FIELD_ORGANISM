# S1-IY: Endlicher DTS-1-Ereignisgrenzen-Fixturevertrag

## Zweck

S1-IY bindet die endlichen Werte fuer die vier in S1-IX festgelegten
S/H-Grenzrollen. Der Vertrag bleibt statisch: Es existiert noch kein
Grenzoperator, kein ausfuehrbares Fixture und kein Modelllauf.

## Geometrie und Zahlenformat

Die kanonische Geometrie ist die offene ungerichtete Dreiknotenlinie
`node-a -- node-b -- node-c`. Kante A verbindet `node-a` und `node-b`, Kante
B verbindet `node-b` und `node-c`. Alle Werte sind endliche, in IEEE-754
binary64 exakt darstellbare Zweierbrueche innerhalb des normierten
Feldbereichs.

Die S1-HK-Beteiligung einer Kante `(i,j)` bleibt
`((S_i-S_j)/2)^2`. S1-IY fuehrt keine neue Observable ein.

## Gebundene Grenzwerte

In der Reihenfolge `(node-a,node-b,node-c)` gelten:

| Rolle | S | H | Beteiligung `(A,B)` |
|---|---|---|---|
| `A_BOUNDARY` | `(-0.5,0.5,0.5)` | `(0,0,0)` | `(0.25,0)` |
| `B_BOUNDARY` | `(-0.5,-0.5,0.5)` | `(0,0,0)` | `(0,0.25)` |
| `GAP_BOUNDARY` | `(0,0,0)` | `(0,0,0)` | `(0,0)` |
| `PROBE_BOUNDARY` | `(-0.5,0,0.5)` | `(-0.125,0,0.125)` | `(0.0625,0.0625)` |

A und B sind spiegel- und vorzeichensymmetrisch. Ihre aktive Beteiligung ist
gleich gross; die jeweils andere Kante ist strukturell exakt null. Gap ist
vollstaendig null. Die Probe ist von allen Aktivgrenzen verschieden.

Die neue Probe uebernimmt insbesondere weder den alten S-Vektor
`(-1,0,1)` noch den alten H-Vektor `(-0.2,0,0.2)`. Alte P_IK- und
P_IN-Feldresultate bleiben quarantinisiert. Nur die direkten Ressourcenledger
bleiben als vorherige direkte Evidenz erhalten, nicht als Fixturewerte.

## Zeiten und Kontakte

A-, B-, Gap- und Readoutintervall dauern jeweils exakt `0.5` synthetische
Zeiteinheiten. Alle drei Rezeptorkontakte sind in jedem dieser Intervalle
bitgenau `+0.0`. Der S/H-Grenzoperator selbst besitzt Dauer null.

Diese gemeinsame Dauer ist eine technische Fixturewahl und keine physische
Zeitschaetzung. Interne Subschritte oder Baselinekonfigurationen werden in
S1-IY nicht gewaehlt.

## Toleranzen

Kanonische Vektordigests, modelluebergreifende Grenzidentitaet, strukturelle
Nullen und die dyadischen Beteiligungswerte muessen bitgenau sein. Fuer
spaetere reine Bereichs- und Ledger-Rundungspruefungen ist hoechstens
`1.1368683772161603e-13` zugelassen. Eine Ergebnis-, Akzeptanz- oder
Baseline-Fit-Toleranz ist nicht gebunden.

## Endliches Aufrufbudget

P_IK und P_IN besitzen je Modell jeweils acht Grenzanwendungen und acht
Intervallaufrufe. Fuer DTS-1 und B1 bis B6 ergeben sich ueber beide Profile
pro einfacher Gesamtpruefung:

- 112 Grenzanwendungen,
- 112 Intervallaufrufe.

Eine spaetere deterministische Doppelpruefung darf daher hoechstens 224
Grenzanwendungen und 224 Intervallaufrufe besitzen. Das ist ein
Orchestrierungsbudget und noch kein Feldschrittbudget fuer interne
Refinements. Forschungsfeldschritte bleiben null.

## Entscheidung und Sperren

`FINITE_COMMON_EVENT_BOUNDARY_FIXTURE_BOUND_NO_IMPLEMENTATION_OR_EXECUTION`

Kanonischer Vertragsdigest:

`86ce6d3837fce14fa1cf4452ea58f37f17d38ff4da13a7fb8213e6950cccf73d`

S1-IY bindet keine Adapterparameter, Konfigurationsdigests,
Ergebnisschwellen oder Modellanpassung. Es zeigt weder Baselineabschluss noch
Kandidatenvorteil oder eine Speicher-, Lern- oder KI-Faehigkeit.

## Naechster zulaessiger Schritt

S1-IZ darf nur den privaten reinen Grenzoperator und die vier kanonischen
Fixtureobjekte implementieren und technisch gegen S1-IX/S1-IY pruefen. Kein
Baselineadapter, kein Modellintervall, keine Runtime und keine
Forschungsprobe duerfen dabei ausgefuehrt werden.
