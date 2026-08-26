# S1-NX G2/D3 endlicher F2-Bildungs- und Falsifikationsvertrag

## Status

S1-NX bindet ausschliesslich die endliche Funktions-, Expositions- und
Falsifikationsgrenze fuer eine spaetere endogene Bildung von
`bound_configured`. Der Schritt waehlt keine Bildungsgleichung, keine Rate,
keinen Parameter, keine Runtime und keine Feldrueckwirkung und fuehrt nichts
aus.

Entscheidung:

```text
G2_D3_F2_ORDERED_LOCAL_FORMATION_AND_FALSIFICATION_BOUND
```

## Zweck

Der in S1-NW akzeptierte O3-Operator erzeugt einen direkten C0/C1-Unterschied,
wenn `bound_configured` bereits gesetzt ist. F2 muss vor jeder
Bildungsgleichung klaeren, ob dieselbe D3-Rolle aus einer kontrollierten
lokalen Feldgeschichte hervorgehen koennte.

Die primaere F2-Frage lautet:

```text
Kann dieselbe endliche Menge lokaler Kontakte allein durch ihre Feldordnung
eine unterschiedliche D3-Unterteilung bilden, die nach kontrollierter
Angleichung des schnellen Feldzustands die spaetere identische Probe
unterschiedlich begrenzt?
```

## Gemeinsamer Anfangszustand

Alle Kandidatenarme beginnen bitgleich auf derselben kanonischen Kante mit:

```text
free = 0.5
bound_unconfigured = 0.5
bound_configured = 0.0
blocked = 0.0

aggregate bound = 0.5
capacity = 1.0
```

Geometrie, Feldreferenz, Traegerordnung, Feldzeitgrenze, S/H-Anfangswerte und
alle Nicht-G2-Zustaende sind bitgleich. Der Start ist damit C0; kein Arm darf
C1 oder einen Bildungswert manuell erhalten.

## Zwei lokale Kontaktbausteine

Vor einer Gleichung werden nur zwei gleich lange, gleich starke und lokal
gespiegelte Kontaktrollen gebunden:

```text
X: S_a=-1.0, S_b=+1.0, Handoffkontakt auf edge:a:b
Y: S_a=+1.0, S_b=-1.0, Handoffkontakt auf edge:a:b
```

Beide besitzen im S1-NM-Rahmen dieselbe lokale Beteiligung `p=1.0`. Sie
unterscheiden sich nur in der Orientierung. Jeder Kontakt belegt genau ein
abgeschlossenes lokales Expositionsintervall; zwischen den vier Kontakten
wird kein zusaetzlicher Arm-spezifischer Nullkontakt eingefuegt.

X und Y sind technische Kontaktrollen, keine Labels, Bedeutungen oder
Zielklassen.

## Drei endliche Bildungsgeschichten

Jeder Arm sieht genau vier Kontakte, darunter zweimal X und zweimal Y:

```text
H0_ALTERNATING = X, Y, X, Y
H1_GROUPED     = X, X, Y, Y
H1_MIRRORED    = Y, Y, X, X
```

Damit sind Kontaktzahl, Kontaktstaerke, Gesamtdosis und Orientierungsbilanz
identisch. Primaerer Unterschied ist nur alternierende gegen lokal
fortgesetzte Ordnung. `H1_MIRRORED` kontrolliert, dass eine spaetere Bildung
nicht an ein festes Vorzeichen oder eine Carrierbezeichnung gebunden wird.

Keine Geschichte enthaelt Reward, Ergebniswert, Zielmuster, Sequenzpuffer,
manuelles Konfigurationsbit oder externen Schreibzugriff auf D3.

## Faire Baselineexposition

Kandidat und jede zustandsbehaftete Baseline erhalten pro Arm dieselben
Kontaktbytes, dieselbe Reihenfolge und dieselben Feldzeitgrenzen:

- DTS-1 und geschaltetes T1;
- Fixed Adapter;
- vorregistrierter Leaky-Arm;
- vorregistrierter Integratorarm.

Ein historisches Baselineprofil darf nur wiederverwendet werden, wenn seine
vollstaendige kausale Vorgeschichte bitgleich zur jeweiligen H0-, H1- oder
Spiegelgeschichte ist. Andernfalls muss es spaeter kontrolliert neu erzeugt
werden. Profile werden nicht repariert oder uminterpretiert.

## Kontrollierte Angleichung vor der Probe

Nach jeder Bildungsgeschichte wird fuer Kandidat und Gegenbaselines in
getrennten Interventionskopien derselbe beobachtbare Probenzustand
hergestellt. Angeglichen werden ausschliesslich:

```text
S_a, S_b, H_a, H_b
free, aggregate bound, blocked, capacity
Geometrie, Feldreferenz und Probe
```

Die Angleichung darf nur einen vorregistrierten gemeinsamen F1-Probenzustand
verwenden und weder ein Ergebnis lesen noch einen D3-Sachwert berechnen.
`bound_configured` und `bound_unconfigured` werden dabei ausdruecklich nicht
angeglichen, gesetzt, skaliert oder repariert. Ihre Summe muss weiterhin das
bitgleiche aggregierte `bound=0.5` ergeben.

Leaky- und Integratorbaselines behalten dagegen die aus derselben Geschichte
regelkonform entstandenen eigenen internen Zustaende. Sie duerfen nicht auf
eine Kandidatennull zurueckgesetzt werden. So bleibt pruefbar, ob ihr
Nachhall oder ihre Akkumulation dieselbe Spaetwirkung erklaert.

## Gerichtete Bildungsprognose

Vor jeder Gleichung gilt fuer die D3-Unterteilung:

```text
B_H0 = bound_configured nach H0_ALTERNATING
B_H1 = bound_configured nach H1_GROUPED
B_H1M = bound_configured nach H1_MIRRORED

0.0 <= B_H0 < B_H1 <= 0.5
0.0 <= B_H0 < B_H1M <= 0.5
```

Es wird noch kein Mindestabstand und kein konkreter Bildungsbetrag gebunden.
Die spaetere Bildungsfamilie muss vor Ausfuehrung eine technische
Rundungsgrenze festlegen. Sie darf keine Schwelle aus Ergebnissen ableiten.

Die Spiegelkontrolle verlangt nur dieselbe gerichtete Trennung von H0. Eine
exakte Gleichheit `B_H1=B_H1M` wird vor einer konkreten symmetrischen
Bildungsgleichung noch nicht behauptet.

## Spaetere identische F1-Probe

Nach der Kontrollangleichung wird in allen Armen exakt die S1-NM-Probe
verwendet. Mit dem akzeptierten O3-Operator folgt vorab:

```text
A_H0 = max(0.0, 0.5 - B_H0)
A_H1 = max(0.0, 0.5 - B_H1)
A_H1M = max(0.0, 0.5 - B_H1M)

A_H1 < A_H0
A_H1M < A_H0
```

Der O3-Operator liest nur den nach der Geschichte vorhandenen validierten
D3-Zustand. Er darf keine Kontaktfolge oder Armkennung lesen.

## Bildungsablation

Eine reine Bildungsablation verhindert ausschliesslich die Umordnung
`bound_unconfigured -> bound_configured`. Alle Kontaktfolgen, S/H-Pfade,
aggregierten Ressourcenrollen und Probe bleiben erhalten.

Verbindliche Nullprognose:

```text
B_H0_ablated = B_H1_ablated = B_H1M_ablated = 0.0
A_H0_ablated = A_H1_ablated = A_H1M_ablated = 0.5
```

Eine Ablation, die Kontakte entfernt, S/H veraendert oder das aggregierte
Ledger zuruecksetzt, ist ungueltig.

## Gegenprognosen

### DTS-1 und geschaltetes T1

Beide besitzen keine `bound_configured`-Koordinate. Nach bitgleicher
Aggregation und gemeinsamer Probe lautet ihre D3-F1-Prognose fuer alle drei
Arme null. Erzeugt ein spaeterer Kandidat den Unterschied nur durch
unterschiedliche aggregierte Ressourcen oder Transfers, wird F2 verworfen.

### Fixed Adapter

Ein identischer fester Adapter darf aus der Armreihenfolge keinen
unterschiedlichen Sachwert lesen. Ein armweise verschiedener Adapter oder
eine gespeicherte Sequenzkennung ist unzulaessig.

### Leaky und Integrator

Beide sehen die vollstaendige jeweilige Geschichte. Ihre eigenen spaeteren
Ausgaben duerfen sich deshalb unterscheiden und werden nicht kuenstlich auf
null gesetzt. Reproduziert eine dieser Baselines spaeter neben der
Bildungsrichtung auch die noch zu bindenden Rollen Abschwaechung,
Interferenz, Loesung und Wiederbildung vollstaendig, besitzt G2 keine eigene
Funktionsachse und wird gestoppt.

### Replay und Readout

Keine Folge darf gespeichert, erneut ausgegeben oder ueber eine Arm-ID
rekonstruiert werden. Der Readout ist passiv und darf weder B noch A bilden.

## Verwerfungsbedingungen

Der F2-Zweig wird gestoppt, wenn:

- H0, H1 und Spiegelarm nicht mit identischer Kontaktmenge und Dosis
  realisierbar sind;
- die D3-Unterteilung manuell gesetzt oder aus einer Armkennung gelesen wird;
- `B_H1<=B_H0` oder `B_H1M<=B_H0` gilt;
- der Unterschied nach reiner Bildungsablation bestehen bleibt;
- S/H oder aggregiertes Ledger bei der Probe zwischen Kandidatenarmen
  abweichen;
- Kapazitaet oder Gesamtressource verletzt wird;
- ein Fixed Adapter, Lookup, Replay oder Ergebniswissen den Unterschied
  erzeugt;
- Baselines nicht dieselbe relevante Vorgeschichte erhalten;
- eine Gleichung oder Schwelle erst nach Ergebniskenntnis geaendert werden
  muss;
- Rohdaten, Kontaktfolge oder Ergebniswerte in D3 gespeichert werden muessen.

Ein Fehlschlag ist ein technischer Stopp fuer diese Bildungsfamilie und kein
Befund ueber allgemeine MCM-Moeglichkeiten.

## Aussagegrenze

S1-NX bindet nur eine pruefbare, eingangs- und ordnungsgetragene
Bildungshypothese. Es gibt keine Bildungsgleichung, keinen gebildeten Zustand,
keine Spaetwirkung, Abschwaechung, Interferenz, Loesung oder Feldwirkung,
keine Lernfunktion und keinen Befund zur hypothetischen MCM-Memory.

## Naechster erlaubter Schritt

S1-NY darf ausschliesslich minimale lokale Bildungsmechanismusklassen gegen
diesen F2-Vertrag auditieren. Hoechstens eine Klasse darf weitergefuehrt
werden. Sie muss die konservative Umordnung innerhalb des bestehenden
`bound=0.5` tragen, ordnungssensitiv, gespiegelt kontrollierbar und gegen
Integrator, Leaky, Lookup und Replay abgrenzbar sein.

S1-NY darf noch keine Bildungsgleichung, Parameter, Runtime, Transferbuchung
oder Feldwirkung implementieren oder ausfuehren.
