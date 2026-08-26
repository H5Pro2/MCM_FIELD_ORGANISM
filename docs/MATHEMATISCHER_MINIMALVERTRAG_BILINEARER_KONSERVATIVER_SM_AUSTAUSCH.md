# Mathematischer Minimalvertrag fuer bilinearen konservativen S-M-Austausch

## Status

```text
Pruefart:                           statischer Existenz- und Invariantenaudit
exakte M-Erhaltung:                 konstruktiv moeglich
M-Nichtnegativitaet und Begrenzung: konstruktiv moeglich
gleichfoermiges M funktional neutral: gefordert
weltbedingter Fluss aus Gleichzustand: gefordert
sofort gebundene S-Rueckarbeit:     gefordert
alle drei letzten Bedingungen:     nicht gleichzeitig erfuellbar
Form 3 unter aktuellem Vertrag:     geschlossen
Code, Runtime oder Versuch:         nicht zugelassen
```

## Forschungsfrage

Existiert eine nichttriviale lokale Kantenform, die M konserviert und
begrenzt, aus gleichfoermigem M durch normale S-Feldgeschichte eine
Verteilung bildet, denselben Austausch sofort auf S zurueckwirken laesst und
bei gleichfoermigem M dennoch fuer jede S-Lage exakt die heutige S-H-Runtime
reproduziert?

Die Antwort ist unter diesen Anforderungen **nein**. Der Widerspruch liegt
nicht in einer Parametrisierung, sondern in den Kausalbedingungen.

## 1. Kleinste Kantenrollen

Fuer eine vorhandene ungerichtete Kante zwischen i und j sei:

```text
dS_ij = S_j - S_i
J_ij  = realisierter M-Nettofluss von i nach j
```

Konservation verlangt:

```text
J_ji = -J_ij
dM_i/dt enthaelt -J_ij
dM_j/dt enthaelt +J_ij
```

Ein gebundener S-Gegenbeitrag derselben Wechselwirkung sei abstrakt R. Seine
konkrete Form ist fuer den No-Go-Beweis nicht notwendig.

## 2. Erhaltung und Zustandsgrenzen sind nicht das Problem

Eine kontinuierliche Austauschfamilie kann konstruktiv nichtnegative
gerichtete Raten verwenden:

```text
q_i_to_j >= 0
q_j_to_i >= 0
J_ij = q_i_to_j - q_j_to_i
```

Traegt jede Abgaberate einen Faktor der vorhandenen Quellmenge M_i, kann ein
leerer Ort nichts abgeben, aber von Nachbarn empfangen. Bei endlicher
Gesamtmenge sind damit prinzipiell invariant:

```text
M_i >= 0
M_i <= M_total
Summe_i M_i = M_total
```

Da S im Bereich `-1..1` liegt, kann beispielsweise eine gerichtete Rate
abstrakt lauten:

```text
q_i_to_j = k * w_ij * M_i * (d + c * dS_ij)
```

mit `d >= 2 * abs(c)`. Die Gegenrichtung verwendet dieselbe Form an der
umgekehrten Kante. Dies ist keine zugelassene MCM-Gleichung, sondern nur ein
Existenzzeuge fuer nichtnegative konservative S-beeinflusste Raten.

## 3. Die drei kollidierenden Bedingungen

### N1: funktionale Neutralitaet

Der bisherige M-Vertrag fordert fuer die gleichfoermige Verteilung `M_i = m0`:

```text
R = 0 fuer jede zulaessige gegenwaertige S-Lage
```

Damit soll der aktive neutrale Materialzustand exakt die heutige S-H-Runtime
reproduzieren.

### N2: weltbedingte Schreibfaehigkeit

Normale S-Feldgeschichte muss M aus demselben gleichfoermigen Zustand
umverteilen koennen. Es muss also mindestens eine S-Lage und Kante geben mit:

```text
M_i = M_j = m0
aber J_ij != 0
```

Andernfalls bleibt M aus seinem neutralen Startzustand fuer immer
gleichfoermig.

### N3: sofort unteilbare Rueckarbeit

Der F3-Vertrag fordert, dass der tatsaechliche weltbedingte M-Austausch und
die S-Rueckwirkung zwei Seiten derselben Wechselwirkung sind. Fuer einen
isolierten nichtkompensierten Kantenfluss gilt daher:

```text
J_ij != 0
-> mindestens ein gebundener S-Gegenbeitrag R ist nicht null
```

Andernfalls schreibt der Austausch M ohne dieselbe sofortige Rueckwirkung und
benoetigt spaeter eine weitere Leser- oder Aktivierungsbedingung.

## 4. No-Go-Beweis

Waehle gemaess N2 eine S-Lage, die aus gleichfoermigem M einen
nichtverschwindenden Kantenfluss erzeugt.

Nach N3 erzeugt derselbe Austausch einen nichtverschwindenden
S-Gegenbeitrag: `R != 0`.

Nach N1 muss bei gleichfoermigem M fuer dieselbe S-Lage jeder M-vermittelte
S-Gegenbeitrag null sein: `R = 0`.

Damit gelten an derselben Kausalgrenze zugleich `R != 0` und `R = 0`.

Der Widerspruch verschwindet nur, wenn mindestens eine Bedingung aufgegeben
wird:

- ohne S-getriebenen Fluss entfaellt N2;
- ohne Rueckarbeit beim ersten Fluss entfaellt N3;
- mit Rueckarbeit aus neutralem M entfaellt N1.

## 5. Scheinloesungen

### Rueckarbeit erst nach Abweichung von m0

Ein Faktor `M_i - m0` kann die erste Rueckwirkung unterdruecken. Danach liest
er jedoch die entstandene Abweichung als Aktivierungsbedingung. Das ist ein
Pattern-Leser beziehungsweise zustandsabhaengiger Gain.

### Rueckarbeit um einen Schritt verzoegern

Dann muss der Austausch gespeichert werden. Es entsteht eine weitere
Flussspur oder ein Readerzustand; Schreiben und Wirkung sind getrennt.

### Rueckarbeit nur bei einer Probe

Eine Probe-, Abruf- oder Phasenbedingung ist als Organismusfunktion verboten.

### Globale Kompensation oder Clipping

Globale Normierung entfernt keine lokalen Gegenbeitraege. Clipping verbirgt
eine Wirkung numerisch, ist aber keine Neutralitaet und keine konservative
Naturform.

## 6. Zusaetzliche S-Bereichsgrenze

Selbst nach einer Nullpfadkorrektur muss die additive S-Rueckarbeit den
Bereich `-1..1` invariant halten. Eine ungehemmte Flussdivergenz garantiert
dies nicht.

Eine spaetere Form benoetigt daher eine analytisch nach innen gerichtete
Wirkung an den S-Grenzen oder eine beschraenkte interne Zielgroesse innerhalb
der bestehenden S-Integration. Nachtraegliches Clipping bleibt unzulaessig.

## 7. Drei moegliche Vertragskorrekturen

### K1: Zustandsneutralitaet behalten

Gleichfoermiges M bleibt fuer jede S-Lage funktional neutral. Dann muss die
sofort unteilbare Rueckarbeit aufgegeben werden und Form 3 bleibt geschlossen.

### K2: Parameterneutralitaet statt Zustandsneutralitaet

Der exakte heutige Nullpfad wird durch einen auf null gesetzten
S-M-Kopplungsparameter definiert. Bei aktiver Kopplung darf bereits der erste
weltbedingte M-Austausch auf S zurueckwirken.

Damit bleiben N2 und N3 vereinbar. Die aktive gekoppelte Runtime unterscheidet
sich ab dem ersten Weltkontakt bewusst von der heutigen neutralen Runtime;
der heutige Pfad bleibt als exakte Parameterablation erhalten.

K2 ist die kleinste mathematisch konsistente Korrektur fuer F3.

### K3: Unteilbarkeit aufgeben

M wird durch S-Drift gebildet und spaeter durch eine getrennte Funktion auf S
abgebildet. Das faellt auf die geschlossene Drift-plus-Pattern-Leser-Familie
zurueck.

## 8. Forschungsentscheidung

```text
konservative positive M-Kantenform:       prinzipiell moeglich
weltbedingte Umverteilung:                prinzipiell moeglich
sofort gebundene S-Rueckarbeit:           prinzipiell moeglich
M-Gleichzustand zugleich immer neutral:   unvereinbar
Form 3 unter aktuellem Vertrag:           geschlossen
```

Es wird keine Gleichung und keine Runtime implementiert. Der naechste Schritt
ist eine explizite Projektentscheidung ueber den Nullpfad.

## Bester naechster Schritt

Als naechstes wird ein **Nullpfad-Korrekturvertrag fuer gekoppelte
Substratphysik** formuliert. Er vergleicht K1 bis K3 und entscheidet, ob der
aktive Materialzustand die schnelle Feldphysik ab dem ersten Kontakt
mitveraendern darf und der exakte heutige S-H-Pfad als Parameterablation
statt als aktiver Materialgleichzustand gefuehrt wird.

Die mathematisch konsistente Empfehlung lautet K2. Sie ist jedoch eine
methodische Vertragskorrektur und darf nicht stillschweigend in einer
Gleichung versteckt werden.

Der
[Nullpfad-Korrekturvertrag](NULLPFAD_KORREKTURVERTRAG_GEKOPPELTE_SUBSTRATPHYSIK.md)
hat K2 inzwischen verbindlich gewaehlt. Form 3 darf nur unter dieser
Parameterneutralitaet erneut mathematisch geprueft werden.
