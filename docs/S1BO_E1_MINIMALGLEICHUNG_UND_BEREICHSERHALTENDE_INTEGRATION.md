# S1-BO: E1 Minimalgleichung und bereichserhaltende Integration

## Status

Statischer Gleichungs- und Integrationsvertrag fuer E1. Keine Runtime, kein
Snapshot-Schema, kein Testlauf und kein Memory-, Lern-, Organismus- oder
KI-Befund.

## Verbindliche Groessen und Einheiten

Der erste E1-Korridor verwendet die uniforme Knotenkapazitaet aus S1-BM:

```text
q_i = q_0 > 0                              Ressource
b_e >= 0                                   Ressource
f_i = q_0 - 0.5 * Summe_e~i(b_e)           Ressource
p_e = ((S_i - S_j) / 2)^2                  dimensionslos
k_on, k_off                                1 / Sekunde
r_0                                        1 / Sekunde
gamma                                      dimensionslos
```

`e~i` bezeichnet eine vorhandene ungerichtete Kante, die an Knoten `i`
inzident ist. Alle Parameter sind global und inhaltsfrei. Kein Parameter darf
von Modalitaet, Weltkennung, Wiederholungszahl oder Versuchsergebnis
abhaengen.

## Kontinuierliche Minimalgleichung

Fuer jede vorhandene Kante `e = {i,j}` gilt:

```text
d b_e / dt
= k_on * q_0 * p_e * (f_i / q_0) * (f_j / q_0)
- k_off * b_e
```

oder gleichwertig:

```text
d b_e / dt = (k_on / q_0) * p_e * f_i * f_j - k_off * b_e
```

Der erste Term bindet nur lokal verfuegbare Ressource. Der zweite Term gibt
jede vorhandene Bindung kontinuierlich frei.

## Invarianz des zulaessigen Zustandsraums

Der zulaessige Bereich lautet:

```text
b_e >= 0 fuer alle e
f_i >= 0 fuer alle i
```

An seinen Grenzen zeigt der Vektorfluss nach innen:

1. Bei `b_e = 0` verschwindet die Freigabe und der Bindungsterm ist
   nichtnegativ. `b_e` kann deshalb nicht unter null laufen.
2. Bei `f_i = 0` verschwinden die Bindungsterme aller an `i` inzidenten
   Kanten. Vorhandene Freigabe vergroessert `f_i`. Die Knotenkapazitaet kann
   deshalb nicht ueberzogen werden.
3. Da `f_i` immer aus `q_0` und `b_e` abgeleitet wird, bleibt die lokale und
   globale S1-BM-Erhaltungsidentitaet algebraisch exakt.

Diese Aussagen gelten fuer die kontinuierliche Gleichung. Eine numerische
Implementierung darf sie nicht durch nachtraegliches Clipping vortaeuschen.

## Symmetrischer konservativer Zeitschritt

Fuer die erste technische Implementierung wird `S` innerhalb eines explizit
uebergebenen Intervalls `dt > 0` eingefroren. Der E1-Schritt verwendet eine
symmetrische Freigabe-Bindung-Freigabe-Komposition.

### 1. Halbe exakte Freigabe

```text
b_e^(a) = b_e * exp(-k_off * dt / 2)
f_i^(a) = q_0 - 0.5 * Summe_e~i(b_e^(a))
```

### 2. Gleichzeitiges lokales Bindungsangebot

```text
d_e = q_0 * (1 - exp(-k_on * p_e * dt))
      * (f_i^(a) / q_0) * (f_j^(a) / q_0)

D_i = 0.5 * Summe_e~i(d_e)
a_i = 1                         falls D_i = 0
a_i = min(1, f_i^(a) / D_i)     sonst

delta_e = d_e * min(a_i, a_j)
b_e^(b) = b_e^(a) + delta_e
```

`a_i` ist kein nachtraegliches Clipping. Es ist die vor dem Transfer
berechnete lokale Zuteilung derselben endlichen Knotenressource. Sie verwendet
nur die Kante und ihre beiden lokalen Ein-Schritt-Nachbarschaften. Alle
Kantenangebote werden aus demselben Vorzustand berechnet; eine Iteration in
Kantenreihenfolge ist unzulaessig.

Aus `delta_e <= d_e * a_i` folgt fuer jeden Knoten:

```text
0.5 * Summe_e~i(delta_e) <= a_i * D_i <= f_i^(a)
```

Damit ist `f_i^(b) >= 0` konstruktiv garantiert.

### 3. Zweite halbe exakte Freigabe

```text
b_e' = b_e^(b) * exp(-k_off * dt / 2)
f_i' = q_0 - 0.5 * Summe_e~i(b_e')
```

Der Schritt ist fuer jede Kantenreihenfolge identisch, erhaelt die Bilanz und
benoetigt weder globale Nachnormierung noch Zustandsclip. Fuer `dt -> 0`
konvergiert sein Bindungsangebot erster Ordnung gegen die kontinuierliche
Minimalgleichung; die symmetrische Freigabekomposition vermeidet eine
einseitige Bevorzugung neuer oder alter Bindung.

## Rueckwirkung auf den schnellen Feldgenerator

Nach einem abgeschlossenen E1-Schritt wird fuer jede vorhandene Kante
festgelegt:

```text
r_e = r_0 * (1 + gamma * b_e / q_0)
J_e = r_e * (S_j - S_i)
```

Wegen der S1-BM-Knotengrenze gilt im uniformen Korridor:

```text
0 <= b_e / q_0 <= 2
r_0 <= r_e <= r_0 * (1 + 2 * gamma)
```

Fuer den ersten technischen Korridor wird statisch begrenzt:

```text
0 <= gamma <= 1
```

Die symmetrischen nichtnegativen Kantenraten bilden weiterhin einen
gewichteten diffusionsartigen Graphgenerator. E1 aendert damit die lokale
Fortsetzungsrate, nicht die Feldwerte durch additive Speicherung.

## Atomare Reihenfolge

Ein spaeterer isolierter E1-Entwicklungsschritt muss genau diese Grenze
besitzen:

```text
1. abgeschlossene Werte S_t und E1-Zustand b_t lesen
2. p_e ausschliesslich aus S_t bilden
3. E1 fuer das explizite dt konservativ zu b_(t+dt) entwickeln
4. f_(t+dt) nur als Bilanzrest berechnen
5. neuen unveraenderlichen E1-Zustand atomar ausgeben
```

Die Einbindung der neuen Leitfaehigkeiten in den naechsten S/H-Feldschritt
ist eine spaetere, getrennt ablatierbare Integrationsstufe. Innerhalb desselben
Schritts darf keine Aufrufreihenfolge zwischen einzelnen Kanten wirken.

## Exakte Null- und Grenzfaelle

```text
dt = 0
-> kein Schritt zulaessig; Zeit muss positiv und explizit sein

k_on = 0 und k_off = 0
-> b_e bleibt exakt identisch

k_on = 0 und k_off > 0
-> reine exakte exponentielle Freigabe

k_off = 0 und p_e = 0 fuer alle e
-> b_e bleibt exakt identisch

b_e = 0 und p_e = 0 fuer alle e
-> kanonischer E1-Zustand bleibt exakt neutral

E1 opt-in aus
-> kein E1-Zustand und unveraenderter heutiger S/H-Pfad
```

Der angelegte neutrale E1-Zustand ist weiterhin eine Kontrolle und nicht mit
`E1 opt-in aus` gleichzusetzen.

## Pflichtpruefungen vor Feldkopplung

Eine isolierte Zustandsimplementierung muss mindestens nachweisen:

1. exakte kanonische Kantenidentitaet und Geometriebindung;
2. Nichtnegativitaet von `b_e` und allen abgeleiteten `f_i`;
3. lokale und globale Bilanz bis zur vereinbarten Rundungstoleranz;
4. Invarianz gegen Permutation der gespeicherten Kantenreihenfolge;
5. reine Freigabe gegen die analytische Exponentialloesung;
6. Konvergenz bei `dt`, `dt/2` und `dt/4` ohne Ergebnistuning;
7. exakte Trennung von E1-aus und angelegtem neutralem E1-Zustand;
8. keine Aenderung bestehender Snapshot- oder `current_api`-Vertraege.

## Aussagegrenze

Die Gleichung ist eine bewusst konstruierte ressourcenbegrenzte adaptive
Kantenleitfaehigkeit. Bereichserhaltung, Wiederholungsabhaengigkeit oder
Rueckwirkung waeren technische Eigenschaften dieser Gleichung und fuer sich
kein Nachweis von MCM-Memory oder einer neuen MCM-Natur.

## Bester naechster Schritt

S1-BP hat den kleinsten isolierten, opt-in E1-Zustandscontainer und seine
reine Zustandsentwicklung ohne Einbindung in S/H, Snapshot oder `current_api`
spezifiziert. Als naechstes implementiert S1-BQ genau dieses Modul und den
fokussierten Testverbund. Erst nach dessen Abnahme darf die Rueckwirkung auf
den Feldgenerator vorbereitet werden.
