# S1-RH: Statischer Geometrieerweiterungsinvariantenvergleich fuer den B1/M4-Drei-Kanten-Ausgangsbestand

## Status und Umfang

S1-RH vergleicht drei moegliche Regeln fuer die Uebertragung des
historischen B1/M4-Ausgangsbestands auf die in S1-RF gebundene offene
Vier-Knoten-Linie:

1. lokale Kantenwerttreue;
2. globales Budget mit gleichmaessiger Neuverteilung;
3. vollstaendig freie Nullinitialisierung.

Der Vergleich verwendet MINI_DIO nur als historische Methodikquelle fuer
die Sensitivitaet lokaler Felddynamik gegen Architektur und Kopplung. Er
uebernimmt keine MINI_DIO-Gewichte, Muster, Observer oder Evidenz.

S1-RH waehlt noch keine Hauptinvariante, bindet keinen neuen Wert oder
Digest, implementiert nichts und fuehrt keinen Test oder Feldlauf aus.

Auditentscheidung:

```text
LOCAL_EDGE_VALUE_FIDELITY_IS_THE_ONLY_PRIMARY_ELIGIBLE_OPTION_NOT_YET_SELECTED
LOCAL_OPTION_PRESERVES_HISTORICAL_ENDPOINT_AND_INTERIOR_LEDGER_ROLES
LOCAL_OPTION_PRESERVES_B1_EDGE_RATE_AT_ONE_POINT_ONE
GLOBAL_BUDGET_ALONE_IS_UNDERDETERMINED_UNDER_REFLECTION
UNIFORM_GLOBAL_BUDGET_ADDS_A_NEW_GLOBAL_NORMALIZATION_AND_CHANGES_LOCAL_RATES
ZERO_INITIALIZATION_IS_A_NEGATIVE_CONTROL_NOT_A_PRIMARY_FIXED_ADAPTER_SOURCE
MINI_DIO_SUPPORTS_LOCALITY_CAUTION_BUT_SUPPLIES_NO_TRANSFERABLE_VALUES
NO_SELECTION_NO_REGISTRATION_NO_IMPLEMENTATION_NO_EXECUTION
```

## Gemeinsame Vergleichsbasis

Die gebundene Vier-Knoten-Linie lautet physisch:

```text
node-a -- node-b -- node-c -- node-d
```

Die Spiegelung fordert:

```text
edge(node-a,node-b) = edge(node-c,node-d)
```

Die mittlere Kante `node-b--node-c` bildet einen eigenen Fixorbit. Reine
Spiegelung erzwingt daher nicht, dass mittlere und aeussere Kanten denselben
Wert tragen.

Gemeinsam unveraendert bleiben:

- M4-Knotenkapazitaet `1.0` an jedem Knoten;
- M4-Bindungs-, Turnover- und Recoveryraten;
- B1-Basisrate `1.0`;
- B1-Ableitung `rate = 1.0 * (1 + 0.5 * conductive / 1.0)`;
- drei kanonische Linienkanten;
- B/C- und A/D-Spiegelung;
- getrennte Modellrollen und Frischrepliken.

## Historische Quellennaehe

Fuer die heutige lokale Konkurrenz-, Freigabe- und Wiederverwendungsfrage
sind die Zwei-Kanten-Fixtures P_IK und P_IN die naechsten historischen
Geometriequellen. Sie binden auf jeder vorhandenen Kante:

```text
conductive = 0.2
refractory = 0.1
```

Bei Knotenkapazitaet `1.0` folgt daraus in der Drei-Knoten-Linie:

```text
freier Randknoten   = 0.85
freier Innenknoten  = 0.70
B1-Rate pro Kante   = 1.10
```

Die Ein-Kanten-Werte `0.4/0.2` gehoeren zu anderen historischen
Profilformen. Nullwerte stammen aus ausdruecklichen Nullquellenkontrollen.

S1-RH bewertet, welche Eigenschaft beim Hinzufuegen eines weiteren lokalen
Feldorts erhalten werden soll. Historische Naehe allein ist noch keine
Auswahl.

## Alternative L: lokale Kantenwerttreue

Die lokale Alternative setzt auf jeder neuen Linienkante dieselbe bereits
gebundene lokale Zwei-Kanten-Fixture fort:

```text
conductive = 0.2 je Kante
refractory = 0.1 je Kante
```

### M4-Ledgerfolge

Fuer Endpunkte mit einer inzidenten Kante folgt:

```text
free = 1.0 - 0.5 * 0.2 - 0.5 * 0.1 = 0.85
```

Fuer Innenpunkte mit zwei inzidenten Kanten folgt:

```text
free = 1.0 - 2 * 0.5 * 0.2 - 2 * 0.5 * 0.1 = 0.70
```

Damit besitzt die Vier-Knoten-Linie exakt zwei gespiegelte Randledger mit
`0.85` und zwei gespiegelte Innenledger mit `0.70`. Die lokalen Rollen der
historischen Zwei-Kanten-Linie bleiben erhalten.

Die globale Kapazitaet steigt mit dem neuen Knoten von `3.0` auf `4.0`.
Auch der gespeicherte Gesamtbestand steigt entsprechend der neuen lokalen
Kante:

```text
conductive_total = 0.6
refractory_total = 0.3
free_total       = 3.1
accounted_total  = 4.0
```

Die globale Erhaltung bleibt exakt geschlossen.

### B1-Folge

Der feste leitende Wert `0.2` ergibt auf jeder Kante:

```text
B1 rate = 1.0 * (1 + 0.5 * 0.2 / 1.0) = 1.1
```

B1 bleibt damit die unveraenderte feste Projektion desselben lokalen
leitenden Ausgangsbestands, den M4 dynamisch traegt.

### Bewertung

| Kriterium | Urteil |
|---|---|
| lokale Kantenfunktion | erhalten |
| B/C- und A/D-Spiegelung | erhalten |
| lokale Kapazitaetsledger | erhalten |
| globale Erhaltung | geschlossen |
| B1/M4-Leitquellenkopplung | erhalten |
| neuer globaler Normalisierer | keiner |
| globaler Gesamtbestand | waechst mit lokaler Geometrie |

Die Alternative ist vollstaendig, lokal begruendbar und als primaere
Auswahl geeignet. S1-RH waehlt sie noch nicht aus.

## Alternative G: globales Budget mit Gleichverteilung

Globales Budget allein ist nicht eindeutig. Bei Spiegelung gelten nur:

```text
2 * c_outer + c_middle = 0.4
2 * r_outer + r_middle = 0.2
```

Diese Gleichungen besitzen unendlich viele zulaessige Verteilungen. Um eine
konkrete Alternative zu erhalten, muss zusaetzlich Gleichheit aller drei
Kanten angenommen werden. Dann folgt:

```text
conductive = 0.4 / 3 = 2/15 je Kante
refractory = 0.2 / 3 = 1/15 je Kante
```

### M4-Ledgerfolge

Unter dieser Zusatzannahme folgt:

```text
freier Endpunkt  = 0.90
freier Innenpunkt = 0.80
```

Die Bilanz bleibt global geschlossen, aber die lokalen Rollen aendern sich
gegenueber der historischen Zwei-Kanten-Geometrie von `0.85/0.70` auf
`0.90/0.80`.

### B1-Folge

Die feste Rate wird:

```text
B1 rate = 1.0 * (1 + 0.5 * (2/15)) = 16/15
```

Das ist ungefaehr `1.0666666667` statt `1.1`. Die lokale Kopplung wird allein
deshalb schwaecher, weil ein weiterer Feldort hinzugekommen ist.

### Bewertung

| Kriterium | Urteil |
|---|---|
| lokale Kantenfunktion | veraendert |
| B/C- und A/D-Spiegelung | erhalten |
| lokale Kapazitaetsledger | veraendert |
| globale Erhaltung | geschlossen |
| B1/M4-Leitquellenkopplung | nur bei gemeinsamer Teilung erhalten |
| neuer globaler Normalisierer | erforderlich |
| globaler Gesamtbestand | gegen Knotenzahl fixiert |

Die Alternative behandelt M4 als einen global festen Gesamtvorrat. Der
bestehende Vertrag bindet jedoch positive Kapazitaet pro Knoten und lokale
Kantenressourcen, keinen knotenzahlunabhaengigen Gesamtvorrat. Sie ist daher
keine reine Fortsetzung der heutigen lokalen Anatomie.

## Alternative Z: vollstaendig freie Nullinitialisierung

Die Nullalternative setzt auf jeder Kante:

```text
conductive = 0.0
refractory = 0.0
free per node = 1.0
```

M4 kann aus diesem Zustand spaeter durch normale Beteiligung leitende
Ressource binden. Als Frischzustand ist er anatomisch gueltig und vollstaendig
spiegelungssymmetrisch.

Fuer B1 folgt jedoch auf jeder Kante nur die Basisrate:

```text
B1 rate = 1.0
```

Damit besitzt der feste Adapter keinen leitenden Aufschlag. Seine Rate ist
dieselbe wie bei ablatierter Rueckwirkung. Die historische B1-Funktion als
Fixed-Adapter-Gegenbaseline eines vorhandenen leitenden Vorzustands geht
verloren.

Nullanatomien existieren im Projekt als ausdrueckliche Nullquellen- und
Ablationskontrollen. Diese Rolle ist methodisch wertvoll, aber nicht mit dem
primaeren M4-Frischzustand oder B1-Fixed-Adapter gleichzusetzen.

### Bewertung

| Kriterium | Urteil |
|---|---|
| lokale Kantenfunktion | leitender Ausgangsbestand entfernt |
| B/C- und A/D-Spiegelung | erhalten |
| lokale Kapazitaetsledger | vollstaendig frei |
| globale Erhaltung | geschlossen |
| B1/M4-Leitquellenkopplung | formal nullgleich |
| Fixed-Adapter-Gegenfunktion | kollabiert auf Basisrate |
| geeignete Rolle | Negativkontrolle |

## MINI_DIO-Abgleich

MINI_DIO zeigte, dass lokale Nachbarweitergabe, feste Startgewichte,
Aktualisierungsreihenfolge und Rueckfuehrung die beobachtete Feldtrajektorie
stark bestimmen. Wiederkehrende Rangformen wurden dort global und passiv
durch einen Observer beschrieben.

Daraus sind fuer S1-RH folgende methodische Hinweise zulaessig:

- lokale Kopplungsstaerke darf nicht unbemerkt mit der Gesamtfeldgroesse
  wechseln;
- Geometrie- und Kopplungsaenderung muessen als getrennte Ursachen behandelt
  werden;
- Musterbeobachtung darf keine Werte zurueck in das Feld schreiben;
- Aktualisierung muss aus einem gemeinsamen Vorzustand statt seriell
  in-place erfolgen;
- globale Normalisierung ist eine eigene Mechanik und kein neutraler Default.

MINI_DIO hat jedoch weder DTS-1-Ressourcen noch B1-Fixed-Adapter, lokale
Erhaltungsledger oder einen Skalierungstest zwischen Kantenanzahlen
untersucht. Es liefert deshalb keine Zahlenwerte und beweist keine der drei
Alternativen.

Der Abgleich stuetzt nur die Vorsicht, lokale Dynamik nicht durch eine
verdeckte knotenzahlabhaengige Normierung umzuschreiben.

## Vergleichsmatrix

| Kriterium | Lokal L | Global G | Null Z |
|---|---|---|---|
| ohne zusaetzliche Verteilungsannahme eindeutig | ja | nein | ja |
| historische lokale Ledgerrollen erhalten | ja | nein | nein |
| B1-Rate `1.1` erhalten | ja | nein | nein |
| B1/M4 gemeinsam ableitbar | ja | bedingt | formal null |
| globale Erhaltung | ja | ja | ja |
| neue globale Normalisierung | nein | ja | nein |
| primaere Baselinefunktion erhalten | ja | veraendert | kollabiert |
| geeignete Rolle | primaer geeignet, ungebunden | alternative Normalisierungsbaseline | Negativkontrolle |

## Forschungsentscheidung

S1-RH trifft noch keine numerische Auswahl. Der Vergleich reduziert den
primaeren Entscheidungsraum jedoch auf genau eine noch ungebundene Option:

```text
LOCAL_EDGE_VALUE_FIDELITY
```

Die uniforme globale Budgetteilung bleibt als moegliche
Normalisierungsbaseline ein anderer Mechanismus. Nullinitialisierung bleibt
eine Negativkontrolle. Keine der beiden darf den primaeren B1/M4-
Ausgangsbestand ersetzen, ohne die Baselinefunktion zu aendern.

Dieser Vergleich ist kein dynamischer Befund und keine Aussage zu einer
hypothetischen MCM-Memory.

## Fail-Closed-Regeln

S1-RH wird verletzt, wenn spaeter:

- MINI_DIO als Zahlen- oder Evidenzquelle fuer M4 dargestellt wird;
- lokale Kantenwerttreue und globales Budget gleichzeitig behauptet werden;
- globales Budget ohne zusaetzliche Verteilungsregel als eindeutig gilt;
- eine knotenzahlabhaengige Rate als unveraenderte lokale Funktion gilt;
- Nullinitialisierung als historischer B1-Fixed-Adapter ausgegeben wird;
- B1 einen anderen leitenden Bestand als M4 projiziert;
- refraktaere M4-Werte in den B1-Payload gelangen;
- lokale und globale Bilanz verwechselt werden;
- eine der Alternativen anhand spaeterer Resultate gewaehlt wird;
- vor einem eigenen Auswahlvertrag registriert oder implementiert wird.

## Genau ein naechster Schritt

Als einziger Anschluss ist zulaessig:

```text
S1-RI - statischer Auswahl- und exakter Wertableitungsvertrag fuer lokale
        B1/M4-Kantenwerttreue auf der Vier-Knoten-Offenlinie
```

S1-RI darf die lokal kantenwerttreue Option als primaeren Ausgangsbestand
auswaehlen und alle daraus bereits arithmetisch folgenden B1-, M4- und
Ledgerwerte exakt binden. Globale Budgetteilung und Nullinitialisierung
muessen als getrennte Baseline- beziehungsweise Negativkontrollrollen
markiert bleiben. Noch keine Digests, keine Implementierung, keine Fixtures,
keine Tests und kein Feldlauf.
