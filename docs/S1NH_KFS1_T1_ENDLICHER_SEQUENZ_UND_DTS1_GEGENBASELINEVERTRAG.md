# S1-NH KFS-1/T1 Sequenz- und DTS-1-Gegenbaselinevertrag

## Status

S1-NH bindet ausschliesslich eine endliche, feldfreie Ereignisfolge fuer
`KFS1-T1_LOCAL_TARGET_REFRACTORY` und die faire DTS-1-Gegenbaseline. Es wird
keine Sequenz ausgefuehrt, kein Parameter gesucht und keine Feldrueckwirkung
aktiviert.

Entscheidung:

```text
KFS1_T1_FINITE_SEQUENCE_AND_DTS1_COUNTERBASELINE_CONTRACT_BOUND
```

## Vergleichsziel

Der Vergleich prueft zwei getrennte Fragen:

1. Erzeugt T1 die in S1-NF festgelegte diskrete Ledgerfolge deterministisch?
2. Ist diese Folge durch das bereits registrierte DTS-1-Profil oder dessen
   statische Nullkontrolle ohne Fit reproduzierbar?

Eine Abweichung von DTS-1 ist nur eine strukturelle Differenz der lokalen
Ressourcenabbildung. Sie ist noch keine Feldwirkung und kein Funktionsvorteil.

## Gemeinsame lokale Ausgangslage

Beide Arme verwenden genau eine kanonische Kante `edge:a:b` und die
Gesamtressource `1.0`.

T1 startet mit:

```text
capacity = 1.0
free = 1.0
bound = 0.0
blocked = 0.0
```

DTS-1 startet mit zwei Knoten der Kapazitaet `0.5` und einer Kante:

```text
q_a = q_b = 0.5
conductive_bound = 0.0
refractory = 0.0
```

Damit betraegt die globale Ressource ebenfalls `1.0`. Die beiden abgeleiteten
freien DTS-1-Knotenressourcen von je `0.5` entsprechen gemeinsam der freien
T1-Kantenressource `1.0`. Keine andere Kante und kein Feldzustand ist Teil des
Vergleichs.

## Gebundene Ereignisfolge

Jedes Ereignis besitzt die synthetische Dauer `1.0`. Die Dauer ist nur die
bereits erforderliche technische DTS-1-Intervalldefinition und keine
physische Zeitschaetzung.

| Ereignis | Kennung | Endwerte `(S_a,S_b)` | Beteiligung `p` |
|---:|---|---|---:|
| 1 | `K1_CONTACT` | `(-1.0,+1.0)` | `1.0` |
| 2 | `K2_REPEAT` | `(-1.0,+1.0)` | `1.0` |
| 3 | `N1_ENTRY` | `(0.0,0.0)` | `0.0` |
| 4 | `K3_BLOCKED_CONTACT` | `(-1.0,+1.0)` | `1.0` |
| 5 | `N2_RELEASE` | `(0.0,0.0)` | `0.0` |
| 6 | `N3_FREE_HOLD` | `(0.0,0.0)` | `0.0` |
| 7 | `K4_REBIND` | `(-1.0,+1.0)` | `1.0` |

Beide Arme erhalten dieselbe geordnete Beteiligungsfolge:

```text
(1.0, 1.0, 0.0, 1.0, 0.0, 0.0, 1.0)
```

Es gibt keinen Reset zwischen den Ereignissen. Jeder Arm traegt nur seinen
eigenen vollstaendigen Ressourcenstand weiter.

## Vorregistrierte T1-Prognose

T1 wird genau einmal je Ereignisgrenze angewendet. Ein Ereignis darf nicht in
mehrere T1-Aufrufe zerlegt werden, weil eine solche Wiederholung insbesondere
den gebundenen Nullkontakt semantisch veraendern wuerde.

| Grenze | `(free,bound,blocked)` | `(bind,block,release)` |
|---|---|---|
| Start | `(1.0,0.0,0.0)` | - |
| nach K1 | `(0.0,1.0,0.0)` | `(1.0,0.0,0.0)` |
| nach K2 | `(0.0,1.0,0.0)` | `(0.0,0.0,0.0)` |
| nach N1 | `(0.0,0.0,1.0)` | `(0.0,1.0,0.0)` |
| nach K3 | `(0.0,0.0,1.0)` | `(0.0,0.0,0.0)` |
| nach N2 | `(1.0,0.0,0.0)` | `(0.0,0.0,1.0)` |
| nach N3 | `(1.0,0.0,0.0)` | `(0.0,0.0,0.0)` |
| nach K4 | `(0.0,1.0,0.0)` | `(1.0,0.0,0.0)` |

Diese Werte muessen fuer T1 bitgenau sein. Eine nachtraegliche Toleranz oder
eine Reparatur ist unzulaessig.

## Gebundene DTS-1-Profile

Die Profilmenge ist vor Ausfuehrung geschlossen:

| Profil | `k_bind` | `k_turn` | `k_rec` | Rolle |
|---|---:|---:|---:|---|
| `DTS1_REGISTERED` | `0.4` | `0.3` | `0.2` | bereits durch S1-JA registriertes technisches Profil |
| `DTS1_STATIC_ZERO` | `0.0` | `0.0` | `0.0` | statische Nullratenkontrolle |

Je Ereignis wird DTS-1 bei konstanter Beteiligung ueber die Dauer `1.0`
fortgeschrieben. Fuer `DTS1_REGISTERED` werden die festen internen
Refinementstufen `r1/r2/r4/r8` verwendet; jedes Refinement deckt dieselbe
Ereignisdauer und dieselben sieben Grenzen ab. `r4` ist der Primaerarm,
`r1/r2/r8` sind technische Kontrollen. Die Nullratenkontrolle benoetigt nur
`r1`, da jeder Subschritt die Identitaet ist.

T1 bleibt eine Ereignisabbildung und wird nicht kuenstlich mit den DTS-1-
Subschritten wiederholt. Verglichen werden die gemeinsamen sieben
Ereignisgrenzen.

Nicht erlaubt sind weitere Ratenprofile, ein Ratenraster, Optimierung,
Interpolation, ein ereignisabhaengiger Ratenwechsel oder eine Auswahl nach
Kenntnis der Ergebnisse.

## Readouts

An jeder Ereignisgrenze werden fuer beide Arme in derselben Reihenfolge
gebunden:

- vollstaendiges Dreirollenledger in der gemeinsamen Ordnung
  `free/bound/blocked` beziehungsweise
  `free_total/conductive_bound/refractory`;
- drei Bruttotransfers;
- lokale und globale Bilanzresiduen;
- kanonischer Zustandsdigest;
- vorzeichenbehaftetes Residuum DTS-1 minus T1 je Ledgerrolle und Transfer.

Feld-, H-, Adapter-, Gain-, Readout-, Label- und Ergebniswerte sind verboten.

## Aequivalenz und Redundanz

Numerische Ereignisgrenzenaequivalenz liegt nur vor, wenn ein vorregistriertes
DTS-1-Profil alle sieben T1-Nachledger und alle sieben Transfertripel innerhalb
der bestehenden reinen Ledger-Rundungsgrenze
`1.1368683772161603e-13` reproduziert. Strukturelle Nullen und die T1-Werte
selbst bleiben bitgenau.

Unabhaengig davon muss berichtet werden, ob T1 nur durch zustands- oder
ereignisabhaengige DTS-1-Ratenanteile in den Grenzfaellen `0` oder `1`
darstellbar waere. Eine solche Darstellung zaehlt nicht als Reproduktion
durch das feste DTS-1-Profil. Sie stuft T1 aber als diskrete, geschaltete
DTS-1-Variante statt als unabhaengige Substratklasse zurueck.

Entscheidungsrollen nach einer spaeteren Ausfuehrung:

- `T1_LEDGER_INVALID`: T1 verletzt Prognose oder Erhaltung; T1 wird gestoppt.
- `T1_REPRODUCED_BY_REGISTERED_DTS1`: das feste DTS-1-Profil reproduziert
  alle Grenzen; T1 ist redundant und wird gestoppt.
- `T1_DTS1_SWITCHED_VARIANT_ONLY`: keine feste Reproduktion, aber vollstaendige
  Darstellung als geschaltete DTS-1-Rollenabbildung; T1 bleibt nur als
  diskrete DTS-1-Variante erhalten.
- `T1_LOCAL_LEDGER_DISTINCT_FIELD_EFFECT_OPEN`: die lokale Folge ist gegen die
  gebundenen DTS-1-Arme getrennt und nicht vollstaendig als geschaltete
  DTS-1-Abbildung reduzierbar; eine Feldgegenprognose bleibt dennoch offen.

Keine dieser Rollen ist in S1-NH entschieden.

## Fail-Closed- und Aufrufgrenze

Eine spaetere Ausfuehrung bricht ohne Teilurteil ab bei abweichender
Ereignisfolge, Anfangsbilanz, Dauer, Rate, Refinementstufe, Aufrufreihenfolge,
fehlendem Readout oder jeder erforderlichen Reparatur.

Maximal erlaubt sind:

```text
T1:                         7 Uebergangsaufrufe
DTS1_REGISTERED r1/r2/r4/r8: 105 reine Subschritte
DTS1_STATIC_ZERO r1:          7 reine Subschritte
MCM-Feldschritte:              0
```

Die 105 registrierten DTS-1-Subschritte folgen aus sieben Ereignissen und
`1+2+4+8=15` Subschritten je Ereignis.

## Aussagegrenze

S1-NH bindet nur einen lokalen Gegenbaselinevergleich. Es gibt keine
Ausfuehrung, keine Feldwirkung, keine Lernfunktion und keinen Befund zur
hypothetischen MCM-Memory.

## Naechster erlaubter Schritt

S1-NI darf ausschliesslich einen reinen, isolierten Sequenzauswerter fuer die
hier gebundenen T1- und DTS-1-Arme implementieren und genau einmal gegen die
geschlossene Matrix ausfuehren. Keine Feldklasse, kein Runner, keine
Parametersuche und keine Feldrueckwirkung.
