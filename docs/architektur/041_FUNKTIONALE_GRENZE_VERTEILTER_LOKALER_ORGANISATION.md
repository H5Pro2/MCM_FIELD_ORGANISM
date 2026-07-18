# Funktionale Grenze verteilter lokaler Organisation

## Status

Verbindlicher Vergleichs- und Funktionsvertrag auf `E0 / CONTRACT_ONLY`.

Dieses Dokument führt keine Zustandsvariable, Beziehung, Ressourcengleichung
oder Runtime-Wirkung ein. Es präzisiert ausschließlich, welche zusätzliche
beobachtbare Funktion nach dem geschlossenen Kandidaten C1 untersucht werden
darf.

## Ausgangspunkt

C1 hat zwei Punkte getrennt:

```text
lokaler zusätzlicher Zustand
-> kann frühere Feldgeschichte später kausal wirksam machen

fester Produktintegrator + fester Leser
-> erklärt diese Wirkung vollständig
```

Der Fehler von C1 war nicht, dass sein digitaler Zustand eine Zahl war. Der
Fehler war seine vollständige funktionale Zerlegung in einen unabhängig
haltenden Integrator und eine vorgegebene Leserfunktion.

## Mathematische Darstellungsgrenze

Die Forderung:

```text
Organisation darf durch keine Sammlung von Skalaren darstellbar sein
```

ist nicht prüfbar. Ein endlicher digitaler Zustand kann bei unbegrenzter
Präzision und beliebig komplexer Codierung in sehr unterschiedlichen
Datenformen dargestellt werden. Auch Vektoren, Matrizen und Graphen bestehen
technisch aus Zahlen.

Darum wird nicht die Datenform bewertet, sondern:

- welche lokalen Ursachen einen Zustand verändern,
- welche anderen lokalen Möglichkeiten dadurch kausal beeinflusst werden,
- ob dieser Einfluss nur über zulässige Feldwege entsteht,
- ob Wirkung vollständig lösbar ist,
- ob freigewordene Möglichkeit anders beansprucht werden kann.

Ein Skalar ist nicht automatisch statisch. Eine Matrix ist nicht automatisch
organisch.

## Faktorisiertes Gegenmodell

Die stärkste faire Nullklasse besteht aus unabhängigen lokalen Zuständen:

```text
q_i(t2) = F(q_i(t1), lokale Geschichte_i[t1, t2])
```

Dabei gilt:

- jeder Zustand wird unabhängig fortgeschrieben,
- es gibt keine gemeinsam beanspruchte Zustandsgröße,
- die Belegung bei `i` verändert nicht die Änderungsmöglichkeit bei `j`,
- ein fester lokaler Leser darf benachbarte Werte lesen,
- Nichtlinearität, Sättigung und mehrere feste Zeitskalen sind erlaubt.

Diese Klasse ist stärker als C1. Sie darf mehrere lokale Skalare pro Träger
und feste nichtlineare Leser verwenden.

## Faire Vergleichsgrenze

Ein späterer Kandidat und seine faktorisierten Baselines müssen vor dem Lauf
angeglichen werden in:

- gesamter Zahl persistenter reeller Zustandswerte,
- numerischem Wertebereich und Präzision,
- lokalem Leseradius,
- kausal verfügbarem Zeitpräfix,
- Zahl und Dauer der Feldfortschreibungen,
- Snapshotvollständigkeit,
- Zugriff auf Rezeptorkontakt, Aktivierung und Nachhall.

Ein Kandidat darf nicht nur deshalb gewinnen, weil er mehr Zustand, globale
Sicht oder einen längeren Zeitpräfix erhält.

Beliebig große oder beliebig präzise Baselines sind ebenfalls unzulässig,
weil sie jede endliche Versuchstabelle nachträglich codieren könnten.

## Verteilte lokale Organisation als Funktion

Eine verteilte Organisation ist vorläufig nur dann beobachtbar, wenn die
Geschichte einer lokalen Möglichkeit die spätere Änderbarkeit einer anderen
überlappenden lokalen Möglichkeit kausal mitprägt.

```text
Geschichte A beansprucht lokale Feldmöglichkeit
+ identische neue lokale Evidenz B
-> B wirkt anders als ohne Geschichte A
```

Dabei muss gelten:

- A und B überlappen nur über real lokale Feldwirkung,
- eine räumlich getrennte Kontrolle U bleibt unverändert,
- die Wirkung tritt nicht augenblicklich außerhalb des lokalen Kausalwegs auf,
- Lösung von A stellt die frühere Änderbarkeit für B wieder her,
- neue Geschichte B kann danach eine andere spätere Feldfunktion tragen.

Die Begriffe Beanspruchung und Möglichkeit sind Beobachtungsbegriffe. Sie
schreiben weder Kapazitätswert noch Slot oder Kante vor.

## Minimaler Interaktionsrest

Vier kontrollierte Zweige bilden die kleinste erste Abgrenzung:

```text
Y00  keine Geschichte A, keine neue Evidenz B
Y10  Geschichte A, keine neue Evidenz B
Y01  keine Geschichte A, neue Evidenz B
Y11  Geschichte A, neue Evidenz B
```

Für eine fest vorregistrierte spätere Feldmessung wird der Interaktionsrest
gebildet:

```text
I_AB = (Y11 - Y10) - (Y01 - Y00)
```

`I_AB = 0` bedeutet, dass die Wirkung von B unter den geprüften Bedingungen
additiv unabhängig von A ist.

`I_AB != 0` zeigt zunächst nur Wechselwirkung. Auch feste Sättigung,
multiplikative Leser oder globale Normalisierung können einen solchen Rest
erzeugen. Der Wert ist daher ein Screeningmaß und kein Organisationsbeweis.

## Notwendige Kausalinterventionen

Ein belastbarer Funktionsbefund benötigt gemeinsam:

1. Geschichte A vorhanden und entfernt.
2. Neue Evidenz B in beiden Zweigen identisch.
3. Schnelle Feldzustände vor B angeglichen.
4. Mögliche Organisationswirkung von A neutralisiert und getauscht.
5. Lokaler Überlappungsweg A-B geöffnet und blockiert.
6. Gleich starke, aber räumlich getrennte Geschichte U als Kontrolle.
7. Alte Wirkung A vollständig gelöst.
8. B vor und nach dieser Lösung erneut identisch angeboten.
9. Spätere identische Feldprobe nach möglicher B-Bindung.

Nur ein Interaktionsrest, der mit der Organisationsintervention mitwandert,
bei Wegblockade verschwindet und nach Lösung seine alte Wirkung verliert, ist
kausal der untersuchten Organisation zuzuordnen.

## Funktionale Ressourcenfreigabe

Eine Ressource gilt nicht schon deshalb als belegt, weil ein Wert sättigt.

Funktionale Beanspruchung verlangt:

```text
A vorhanden
-> identische Evidenz B kann lokal weniger oder anders organisieren

A vollständig gelöst
-> dieselbe Evidenz B erhält diese Möglichkeit zurück
```

Zusätzlich darf die getrennte Kontrolle U nicht entsprechend beeinflusst
werden. Andernfalls liegt globale Normalisierung oder globale Erschöpfung vor.

## Wiederbindung

Wiederbindung ist erst beobachtbar, wenn:

```text
alte Wirkung A vollständig funktionslos
-> identische neue lokale Geschichte B
-> neue spätere Feldwirkung
-> diese Wirkung wandert mit B-spezifischer lokaler Geschichte mit
```

Rückkehr zu A ist zulässig, sofern A zuvor kausal gelöst war und nur durch
neue lokale Evidenz wieder entstand. Verboten bleibt passive Rückkehr aus
einer Restspur.

## Warum ein lokaler Skalar weiterhin möglich bleibt

Ein späterer digitaler Kandidat darf lokale Zahlen enthalten. Entscheidend
ist, ob ihre Fortschreibung gemeinsam gekoppelt ist und den vollständigen
Lebenszyklus trägt.

Nicht ausreichend ist:

```text
jeder Wert integriert unabhängig seine eigene Evidenz
-> fester Leser kombiniert die Werte später
```

Prüfbar interessanter wäre:

```text
lokale Zustandsänderung A
-> verändert über denselben lokalen Feldprozess die Änderbarkeit B
-> Lösung von A hebt diese Kopplung vollständig auf
```

Auch das wäre zunächst nur funktionale Kopplung. Organisches Memory verlangt
zusätzlich Entstehung aus Weltgeschichte, Stabilisierung, Lösung und andere
Wiederbindung.

## Pflichtbaselines

Mindestens erforderlich sind:

```text
B0  heutige neutrale Feldruntime
B1  mehrere unabhängige leaky Zustände pro Neuron
B2  unabhängige begrenzte Produktintegratoren
B3  unabhängige lokale Sättigung
B4  fester multiplikativer lokaler Leser
B5  statische lokale Rekurrenz
B6  lokale Summennormalisierung mit festem Radius
B7  globale Normalisierung als unzulässige Gegenkontrolle
B8  permanentes lokales Kantengewicht
B9  passive Relaxation und Rückkehr
```

Die Zustands- und Leserbudgets von B1 bis B6 müssen dem Kandidaten fair
entsprechen.

## Stopplinien

Kein weiterer Kandidat wird freigegeben, wenn seine gewünschte Wirkung nur
dadurch entsteht, dass:

- eine Kapazitätsvariable direkt programmiert wird,
- eine Kante oder Partneridentität vorgegeben wird,
- ein `argmax`, Gewinner oder Ranking auswählt,
- globale Normalisierung lokale Konkurrenz vortäuscht,
- eine feste Schwelle Lösung erklärt,
- ein Löschbefehl Ressource freigibt,
- ein Phasenlabel Bildung und Probe technisch umschaltet,
- mehr Zustand oder größerer Leseradius als in den Baselines verwendet wird.

Ein von null verschiedener Interaktionsrest allein gibt keine Mechanik frei.

## Ergebnis der Formalisierung

```text
Darstellungsform vorgeschrieben:          nein
Skalare grundsätzlich ausgeschlossen:    nein
funktionale Kopplung abgegrenzt:          ja
faire faktorisierte Nullklasse definiert: ja
Ressource als Variable eingeführt:        nein
weiterer Kandidat freigegeben:            nein
Runtime-Erweiterung:                      nein
```

## Nächster Schritt

Vor jeder neuen Gleichung wird eine rein passive Versuchsmatrix
vorregistriert. Sie muss A, B und U so anordnen, dass lokale Überlappung,
getrennte Kontrolle, Interaktionsrest, Lösung und erneute B-Evidenz beobachtbar
sind, ohne bereits Kapazität, Kante oder Gewinnerregel zu programmieren.
