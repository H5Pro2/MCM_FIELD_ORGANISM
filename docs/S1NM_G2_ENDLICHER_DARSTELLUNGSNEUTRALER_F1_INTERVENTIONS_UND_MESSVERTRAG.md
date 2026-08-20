# S1-NM G2 endlicher darstellungsneutraler F1-Interventionsvertrag

## Status

S1-NM bindet genau zwei direkte G2-Interventionsarme, einen vollstaendigen
gemeinsamen Kontrollvorzustand und eine primaere lokale Messkomponente. Der
Schritt implementiert und berechnet nichts. G2-Zustandsdarstellung,
Bildungsgleichung, Parameter, Runtime und Feldrueckwirkung bleiben offen.

Entscheidung:

```text
G2_F1_TWO_ARM_LOCAL_ADMISSIBLE_ENGAGEMENT_CONTRACT_BOUND
```

## Zweck

S1-NL verlangt vor jeder G2-Anatomie eine gerichtete direkte
Zustandsintervention. S1-NM schliesst dafuer die Testoberflaeche:

```text
identischer vollstaendiger technischer Vorzustand
+ identische lokale Probe
+ einziger Unterschied G2_C0 oder G2_C1
-> gerichteter Unterschied genau einer lokalen Admissibilitaetskomponente
```

Der Vertrag prueft spaeter nur, ob eine zusaetzliche Konfigurationsrolle
prinzipiell eine eigene lokale Kausalprognose tragen kann. Er zeigt noch
nicht, wie C0 oder C1 entstehen oder ob eine solche Rolle im MCM-Feld
begruendet ist.

## Interventionseinheit

Die direkte Intervention verwendet genau eine kanonische lokale Kante:

```text
edge_id = edge:a:b
first_carrier = a
second_carrier = b
capacity = 1.0
```

Es gibt keine weitere Kante, Nachbarschaft, globale Groesse oder
Rezeptorsequenz.

## Gemeinsamer Ressourcen- und Feldvorzustand

Beide Arme besitzen bitgleich:

```text
KFS-Ledger:
    free = 0.5
    bound = 0.5
    blocked = 0.0

schneller lokaler Feldzustand:
    S_a = -1.0
    S_b = +1.0
    H_a = 0.0
    H_b = 0.0

lokale Beteiligung:
    p = ((S_a - S_b) / 2)^2 = 1.0
```

Die DTS-1-Gegenbaseline verwendet denselben globalen Ressourcenbetrag:

```text
q_a = q_b = 0.5
conductive_bound(edge:a:b) = 0.5
refractory(edge:a:b) = 0.0
derived_free_total = 0.5
```

Fixed Adapter, Leaky und Integrator erhalten in beiden Armen dieselben
vollstaendigen, vorab registrierten Zustandsobjekte. Fuer den direkten
Interventionsvertrag sind Leaky- und Integratorzustand neutral und bitgleich.

## Zwei geschlossene Arme

| Arm | G2-Rolle | Alle anderen Eingaben |
|---|---|---|
| `F1_G2_C0` | `G2_C0` | gemeinsamer Kontrollvorzustand |
| `F1_G2_C1` | `G2_C1` | bitgleich zu `F1_G2_C0` |

`G2_C0` und `G2_C1` sind nur verschiedene gueltige
Konfigurationsrollen. Sie besitzen in S1-NM weder Zahlenwert noch Einheit,
Richtung, Polaritaet, Alter, Ereignisinhalt oder physische Interpretation.

Ein spaeteres Zustandsmodell ist ungueltig, wenn C0 und C1 nicht gleichzeitig
mit dem gemeinsamen Feld- und Ressourcenledger gueltig sein koennen.

## Primaere lokale Messkomponente

Die einzige primaere F1-Komponente lautet:

```text
local_admissible_engagement
```

Sie bezeichnet die endliche obere Ressourcengrenze, die die aktuelle lokale
Probe in genau diesem Vorzustand fuer einen atomaren Transfer von `free` nach
`bound` beanspruchen duerfte, bevor irgendein Transfer oder Feldschritt
ausgefuehrt wird.

Gebundene Einheit und Grenze:

```text
Einheit: lokale Ressource
0.0 <= local_admissible_engagement <= free = 0.5
```

Die Komponente ist kein Gain, Adapterkoeffizient, Readoutscore oder
Ergebnislabel. Sie darf den Zustand nicht veraendern und keine andere
Messkomponente hinzunehmen.

## Gerichtete G2-Prognose

Vor jeder Darstellung wird fest gebunden:

```text
A_C0 = local_admissible_engagement(F1_G2_C0)
A_C1 = local_admissible_engagement(F1_G2_C1)

Delta_G2 = A_C1 - A_C0

G2-Prognose: Delta_G2 < 0.0
```

C1 bezeichnet damit im F1-Vertrag die Konfigurationsrolle mit geringerer
lokaler Zulassung unter genau dieser Probe. Daraus folgt noch keine Aussage
ueber eine spaetere Bildungsgeschichte oder einen allgemeinen
Konfigurationswert.

Es wird keine Mindestgroesse fuer `Delta_G2` gebunden. Eine spaetere
Darstellung muss vor Ausfuehrung eine technische Rundungsgrenze festlegen;
sie darf keine Akzeptanzschwelle nach Ergebniskenntnis einfuehren.

## Nullgrenze und Gegenprognosen

Fuer jeden Gegenarm gilt:

```text
Delta_baseline = 0.0
```

### DTS-1

DTS-1 besitzt in beiden Armen identische Beteiligung, freie Ressource,
leitende Bindung und refraktaere Ressource. Seine Bindungszulassung ist daher
bitgleich. C0 und C1 sind keine DTS-1-Eingaben.

### Geschaltetes T1

T1 liest nur Beteiligung und `free/bound/blocked`. Beide sind bitgleich;
deshalb ist seine Transferprognose in beiden Armen identisch.

### Fixed Adapter

Adapterdigest, Feldvorzustand und Probe sind bitgleich. Ein armweise
verschiedener Adapter ist verboten.

### Leaky und Integrator

Im direkten F1-Eingriff sind ihre vollstaendigen internen Vorzustaende
bitgleich. Daher duerfen sie keinen C0/C1-Unterschied erzeugen. Faire
Bildungsgeschichten fuer diese Baselines werden erst in F2 gebunden.

### G2-Ablation

Die Ablation ersetzt C0 und C1 durch dieselbe neutrale G2-Rolle, ohne einen
anderen Wert zu veraendern. Verbindliche Prognose:

```text
Delta_G2_ablated = 0.0
```

## Erlaubte spaetere Auswertung

Ein spaeterer reiner F1-Auswerter darf ausschliesslich berichten:

- die zwei vollstaendigen Eingabedigests;
- Nachweis der Bitgleichheit aller Nicht-G2-Eingaben;
- `A_C0`, `A_C1` und `Delta_G2`;
- Wertebereichs- und Endlichkeitspruefung;
- Baseline- und Ablationsnullen;
- genau eine Vertragsentscheidung.

Er darf keinen Feldzustand fortschreiben, keinen Transfer buchen, keine
weitere Messkomponente suchen und keine C0/C1-Rolle nach dem Ergebnis
vertauschen.

## Entscheidungsrollen

```text
PASS_G2_F1_DIRECT_CAUSAL_ADMISSIBILITY
STOP_G2_F1_NO_DIRECT_DIFFERENCE
STOP_G2_F1_WRONG_DIRECTION
STOP_G2_F1_BASELINE_NONZERO
STOP_G2_F1_ABLATION_NONZERO
STOP_G2_F1_CONTROL_PRESTATE_MISMATCH
STOP_G2_F1_INVALID_OR_UNBOUNDED_OUTPUT
```

Ein spaeteres `PASS` zeigt nur, dass eine gewaehlte G2-Darstellung die direkte
Interventionsprognose technisch traegt. Es ist noch kein Nachweis endogener
Bildung, Abschwaechung, Interferenz, Loesung oder Feldwirkung.

## Fail-Closed-Grenze

Vor jeder Ausgabe wird abgebrochen bei:

- mehr oder weniger als zwei G2-Armen;
- abweichender Kante, Kapazitaet, S/H, Beteiligung oder Ressourcenbilanz;
- abweichendem DTS-1-, Adapter-, Leaky- oder Integratorvorzustand;
- nicht gleichzeitig gueltigem C0/C1-Zustand;
- negativer, nicht endlicher oder ueber `0.5` liegender Primaerkomponente;
- zusaetzlicher Messkomponente oder Zustandsmutation;
- Transfer-, Feld-, Runtime-, Datei- oder Netzwerkzugriff;
- Reparatur, Fit, Optimierung oder nachtraeglichem Rollentausch.

Eine Abbruchdiagnose ist kein Kandidatenbefund.

## Aussagegrenze

S1-NM bindet nur eine direkte lokale Interventionsmessung. Es gibt keine
G2-Zustandsdarstellung, keine Ausfuehrung, keine Feldwirkung, keine
Lernfunktion und keinen Befund zur hypothetischen MCM-Memory.

## Naechster erlaubter Schritt

S1-NN darf ausschliesslich einen statischen Audit minimaler
G2-Zustandsdarstellungsklassen gegen diesen F1-Vertrag durchfuehren. Es darf
hoechstens eine Darstellungsklasse ausgewaehlt werden, die C0 und C1 endlich,
lokal und nicht aus dem bestehenden Feld- oder Ressourcenledger
rekonstruierbar traegt.

S1-NN bindet noch keine Bildungsgleichung, Parameter, Runtime,
Feldrueckwirkung oder Ausfuehrung.
