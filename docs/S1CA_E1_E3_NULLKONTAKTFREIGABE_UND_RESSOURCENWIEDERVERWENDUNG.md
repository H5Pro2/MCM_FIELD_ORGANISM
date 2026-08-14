# S1-CA: E1 E3-Nullkontaktfreigabe und Ressourcenwiederverwendung

## Status

Statische Vorregistrierung des naechsten E1-Korridors. Die vier Zustandsarme
sind spaeter in S1-CB implementiert und technisch abgenommen worden. Die
identische Probe wurde noch nicht zusammengesetzt oder ausgefuehrt. Kein
Memory-, Vergessens-, Lern-, Organismus- oder KI-Befund.

## Forschungsfrage

Kann die in S1-BZ technisch kausal wirksame, endliche E1-Kantenressource

1. unter feldspannungsfreiem Nullkontakt bilanziert freigegeben und
2. unter einer spaeteren, raeumlich konkurrierenden Geschichte auf einer
   anderen vorhandenen Kante erneut gebunden werden,

ohne Reset, Speicherkommando, Labels, Reward oder Zielmuster?

## Trennung der Teilfragen

Freigabe und Wiederverwendung werden nicht in einem einzigen Effektwert
vermischt.

```text
E3-A: reine analytisch kontrollierte Freigabe
E3-B: konkurrierende Wiederbindung derselben endlichen Ressource
E3-C: eingefrorene identische Probe vor und nach E3-B
```

## Fester Ausgangspunkt

Ausgangspunkt ist ausschliesslich der linke S1-BX-E1-Endzustand auf der
kanonischen Drei-Knoten-Linie. Seine historischen S/H-Endfelder werden nicht
weiterverwendet. Alle diagnostischen Felder werden frisch und wertidentisch
erzeugt.

Der E1-Vertrag bleibt unveraendert:

```text
node_capacity             = 1.0
binding_rate_per_second   = 1.5
release_rate_per_second   = 0.25
backreaction_gain         = 0.5
```

## E3-A: reine Nullkontaktfreigabe

Die E1-Bilanz wird auf einer geometrieidentischen uniformen Feldlage
fortgesetzt. Alle drei Aktivierungen sind gleich; es gibt keinen
Rezeptorkontakt und damit keine Feldspannung als Bindungsursache.

Vorregistrierte Dauern:

```text
t = 0 s, 1 s, 4 s, 8 s
```

Fuer jede Kante muss wegen verschwindender neuer Bindungsnachfrage gelten:

```text
b_e(t) = b_e(0) * exp(-0.25 * t)
```

Pflichtkontrollen:

```text
keine neue Bindung
monotone Abnahme jeder anfangs positiven Kantenbindung
Zunahme der abgeleiteten freien Knotenressource
Erhaltung der lokalen Ressourcenbilanz
Uebereinstimmung mit der analytischen Kurve bis absolute_tolerance = 1e-12
```

Ein unveraenderter Snapshot-Hold dient als Gegenbaseline und darf nicht als
Nullkontaktentwicklung ausgegeben werden.

## E3-B: konkurrierende Wiederverwendung

Nach der fest vorgegebenen Freigabezeit von 4 Sekunden wird der E1-Zustand
auf einem frischen neutralen Feld achtmal mit dem gespiegelten rechten
Kontakt aus S1-BX fortgesetzt:

```text
Kontakt                 = (0.0, 0.0, 1.0)
Intervalle              = 8
Dauer pro Intervall     = 1.0 s
E1-Rueckwirkung         = aus
```

Die Ablation der Rueckwirkung ist hier eine Identifikationskontrolle: Alle
Wiederverwendungsarme erhalten denselben neutralen S/H-Verlauf. Nur die
lokale E1-Bilanz darf sich entwickeln. Dadurch kann eine Veraenderung der
Ressourcenverteilung nicht durch einen E1-veraenderten Eingangsverlauf
erklaert werden.

Gegenarme:

```text
HOLD       unveraenderter E1-Ausgangszustand
RELEASE    nur 4 s uniforme Nullkontaktfreigabe
COMPETE    RELEASE plus acht rechte Kontakte
NEUTRAL    neutraler E1-Anfang plus dieselben acht rechten Kontakte
```

Alle Arme bleiben getrennte tiefe Kopien. Es gibt keine Serialisierung und
keinen Export in die produktive API.

## E3-C: identische technische Probe

HOLD, RELEASE und COMPETE werden nach ihrer Zustandsbildung eingefroren und
jeweils auf wertidentische Kopien des frischen S1-BY-Probefeldes angewendet.
Probe, Dauer, Zeitaufloesung und Toleranz bleiben exakt aus S1-BY erhalten.

Gemessen werden ausschliesslich rohe Distanzen:

```text
Kantenbindungsvektor gegen HOLD
freie Knotenressource gegen HOLD
S/H-Probeausgang gegen P0
S/H-Probeausgang RELEASE gegen HOLD
S/H-Probeausgang COMPETE gegen RELEASE
```

Feste Gainarme fuer HOLD, RELEASE und COMPETE muessen die jeweiligen
eingefrorenen aktiven Probeausgaenge bis `1e-12` erklaeren. Ablatierte Arme
muessen P0 exakt reproduzieren.

## Vorregistrierte technische Entscheidung

```text
INVALID_RUN
E3_RELEASE_ONLY
E3_RELEASE_AND_RESOURCE_REUSE
NO_E3_EFFECT_IN_FIRST_CORRIDOR
```

`E3_RELEASE_AND_RESOURCE_REUSE` ist nur zulaessig, wenn:

1. alle E3-A-Kontrollen bestehen;
2. COMPETE gegen RELEASE eine Kantenbindung oberhalb `1e-12` veraendert;
3. das Gesamtbudget in jedem Zustand erhalten bleibt;
4. mindestens eine zuvor freigewordene lokale Ressourcenmenge im COMPETE-
   Verlauf wieder in Kantenbindung uebergeht;
5. COMPETE und RELEASE unter identischer eingefrorener Probe einen S- oder
   H-Unterschied oberhalb des Numerikrests erzeugen;
6. Ablations- und Fixed-Gain-Kontrollen bestehen.

Die Richtung eines einzelnen Probewerts wird nicht als Erfolg erzwungen.
Insbesondere ist eine behauptete "alte Erinnerung wird durch eine neue
ersetzt" keine zulaessige Auswertung dieses ersten Korridors.

## Gegenbaselines und Grenzen

Die analytische Exponentialkurve ist Pflichtbaseline fuer Freigabe. HOLD
trennt Zeitfortschritt von Snapshot-Aufbewahrung. NEUTRAL trennt
Wiederverwendung von einer Neuinitialisierung. P0, Ablation und Fixed Gain
trennen E1-Zustandsentwicklung von ihrer spaeteren Feldwirkung.

Der Korridor kann die programmierte E1-Ressourcenmechanik technisch
falsifizieren oder bestaetigen. Er kann weder ein Naturprinzip noch Memory,
Vergessen, Rekonstruktion, Bedeutung oder Selbstwahrnehmung nachweisen.

## Bester naechster Schritt

S1-CB implementiert und prueft den privaten Zustandscontainer und die vier
vorregistrierten Arme. S1-CC bindet als naechsten Schritt die identische
Probe, P0-, Ablations-, Fixed-Gain- und Numerikkontrollen vor ihrer
Ausfuehrung.
