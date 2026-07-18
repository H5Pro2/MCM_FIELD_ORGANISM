# Methodik 029: Passive Wiederaufnahme-Baselineprüfung

## 1. Status

Vorregistrierte passive Baselineprüfung der in Methodik 028 definierten
Weltfunktion. Es wird keine MCM-Runtime erweitert.

## 2. Forschungsfrage

Welche bereits vorhandene Zustandsform oder feste Baseline unterscheidet die
aktuell identischen Wiederaufnahmepaare vollständig?

```text
A gegen D: gleicher aktueller Kontakt an Position 3
B gegen C: gleicher aktueller Kontakt an Position 1
```

Ein Unterschied ist nur dann relevant, wenn er aus der vorangegangenen
Weltgeschichte stammt und nach exaktem Reset verschwindet.

## 3. Vorregistrierte Weltverläufe

Für eine fünf Positionen breite Welt gelten unverändert:

```text
A: 0 -> 1 -> 2 -> - -> 3
B: 4 -> 3 -> 2 -> - -> 1
C: 0 -> 1 -> 2 -> - -> 1
D: 4 -> 3 -> 2 -> - -> 3
```

Die Kontaktamplitude ist an der jeweils aktiven Position positiv und an allen
anderen Positionen null. `-` ist ein vollständiger kontaktloser Schritt.

## 4. Parameterfamilie

```text
Amplitude: 0.25, 0.5, 1.0
dt:        1.0
tau:       1.0, 2.0, 4.0
Pause:     genau 1 kontaktloser Schritt
```

Damit entstehen:

```text
3 Amplituden
x 3 Zeitkonstanten
x 4 Weltverläufe
= 36 Verlaufsbeobachtungen

3 Amplituden
x 3 Zeitkonstanten
x 2 aktuell identische Paarungen
= 18 Paarvergleiche
```

## 5. Gemeinsame Bezeichnungen

`u(t)` ist der vollständige aktuelle Kontaktvektor. Alle passiven Zustände
starten bei null.

Der vorhandene unabhängige Nachhall lautet:

```text
d = exp(-dt / tau)
h(t) = d * h(t-1) + (1-d) * u(t)
```

Die Auswertung verwendet vollständige Vektoren. Sie wählt keine Position als
Gewinner aus.

## 6. Exakte Baselines

### B0: Aktuelle Rezeptorprojektion

```text
z0 = u(t4)
```

Erwartung: A kollidiert mit D und B kollidiert mit C.

### B1: Unabhängiger lokaler Nachhall

```text
z1 = h(t4)
```

Dies ist die unveränderte vorhandene B1-Trägerbaseline.

Erwartung: B1 unterscheidet beide aktuell identischen Paarungen, weil dieselbe
aktuelle Position zuvor verschieden oft oder zu verschiedenen Zeiten
kontaktiert wurde.

### B2: Fester Ein-Schritt-Puffer

```text
z2 = (u(t4), u(t3))
```

Da `u(t3)` in allen Verläufen null ist, muss B2 in beiden Paarungen
kollidieren.

### B3: Feste Rekurrenz

```text
rho = 0.5
r(t) = rho * r(t-1) + u(t)
z3 = r(t4)
```

`rho` wird nicht angepasst. B3 ist eine technische Vergleichsrekurrenz und
keine MCM-Mechanik.

### B4: Ein fester symmetrischer Diffusionsschritt

B4 wird aus dem abgeschlossenen B1-Zustand bei `t4` gebildet:

```text
z4_i = (h_(i-1) + 2*h_i + h_(i+1)) / 4
```

Außerhalb der fünf Positionen gilt der Wert null. Es findet genau ein
Auswertungsschritt statt, keine rekursive Diffusionsruntime.

### B5: Direkte räumliche Asymmetrieabbildung

Für die aktuelle Wiederaufnahmeposition `p` wird aus dem abgeschlossenen
Nachhall vor der Wiederaufnahme gelesen:

```text
z5 = h_(p+1)(t3) - h_(p-1)(t3)
```

Außerhalb der Welt gilt der Wert null. B5 ist ein fester passiver Leser. Das
Vorzeichen wird nicht als Befehl oder Sollrichtung verwendet.

## 7. Paarmessung

Für B0 bis B4 wird die L1-Distanz der vollständigen Baselineausgaben gemessen:

```text
D_b(X,Y) = Summe_i |z_b_i(X) - z_b_i(Y)|
```

Für B5 gilt:

```text
D_5(X,Y) = |z5(X) - z5(Y)|
```

Die Primärwerte sind:

```text
D_b(A,D)
D_b(B,C)
```

Es wird nur Kollision oder Unterschied festgestellt. Es wird keine
Fortsetzungs- oder Rückkehrklasse vorhergesagt.

## 8. Kontrollen

1. A und D besitzen exakt denselben aktuellen Kontaktvektor.
2. B und C besitzen exakt denselben aktuellen Kontaktvektor.
3. Die vorherigen Weltverläufe der Paarpartner sind verschieden.
4. A und B sowie C und D sind vollständige räumliche Spiegel.
5. Exakter Reset lässt alle Baselineausgaben kollidieren.
6. Vertauschte Parameter-, Verlaufs- und Paarauswertungsreihenfolge verändert
   das kanonische Ergebnis nicht.
7. Ein optionaler Observer darf keine Beobachtung verändern.
8. Keine Baseline schreibt in Rezeptor, Neuron oder Feld zurück.
9. Weltbeziehungsnamen sind nicht Teil einer Baselineeingabe.

## 9. Vorhersage

Die stärkste Vorhersage lautet:

```text
B0: Kollision
B1: Unterschied
B2: Kollision
B3: Unterschied
B4: Unterschied
B5: Unterschied
```

B1 dürfte die geforderte Geschichtsabhängigkeit bereits vollständig tragen.
B4 und B5 lesen beziehungsweise transformieren denselben B1-Zustand und sind
deshalb keine unabhängigen Erklärungen.

## 10. Entscheidung

### Erwarteter Baselinebefund

Wenn B1 beide aktuell identischen Paare zuverlässig unterscheidet, trägt der
Versuch:

> Geschichtsabhängige Wiederaufnahme ist in dieser minimalen Welt bereits durch
> unabhängigen lokalen Nachhall darstellbar.

Dann bleibt kein Funktionsrest, der eine neue lokale Feldfolge begründet.

### Unerwartete B1-Kollision

Kollidiert B1 in einem Paar, müssen zuerst Weltaufbau, Zeitindizes und
Paarbildung geprüft werden. Eine neue Mechanik wird dadurch nicht
freigegeben.

### Unterschied nur durch B4 oder B5

Ein ausschließlich abgeleiteter Unterschied zeigt nur, dass eine feste
Auswertung Information aus B1 hervorhebt. Das ist keine selbst entstandene
Feldwirkung.

## 11. Stärkstes Gegenargument

Die Weltfunktion ist möglicherweise zu leicht: Dieselbe Wiederaufnahmeposition
wurde in einem Zweig bereits kurz zuvor kontaktiert und im anderen nicht.

Ein gewöhnlicher unabhängiger Leaky-Zustand kann diesen Unterschied direkt
bewahren. Der Versuch würde dann keine Wechselwirkung zwischen Neuronen
benötigen.

Dieser Gegenbefund ist bindend. Die Welt darf nachträglich nicht verändert
werden, um B1 künstlich scheitern zu lassen.

## 12. Stopplinie

Nicht freigegeben sind:

- eine neue Feldübergangsfunktion,
- Bewegungsfortsetzung,
- Diffusion oder Rekurrenz als Runtime,
- Orientierung als Aktivierungsbefehl,
- adaptive Kopplung,
- Rezeptorrückschreibung,
- Ressourcenmechanik,
- Semantik oder Handlung.

## 13. Evidenzgrenze

Maximal E2 für die Reichweite der festen Baselines in dieser Weltfunktion.

E0 bleiben:

- nichtredundante lokale Feldfolge,
- organische Feldorganisation,
- sensorische Selbstregulation,
- Feldintelligenz.

## 14. Bester nächster Schritt

Methodik 029 wird exakt als passiver Lauf ausgeführt. Falls B1 wie erwartet
genügt, wird diese Weltfunktion geschlossen. Danach muss eine neue
Weltanforderung gesucht werden, bei der unabhängige Trägergeschichte
nachweislich nicht ausreicht, statt dem bestehenden Nachhall zusätzliche
Mechanik aufzusetzen.
