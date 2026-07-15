# Lokale MCM-Neuronenfunktion: erste Wirkungsgrenze

## 1. Offene Funktion

Die technische Neuronenhülle trennt bereits drei lokale Eingänge:

```text
aktueller Rezeptorkontakt
+ eigener Zustand aus t
+ lokale Feldproben aus t
-> noch offene Zustandsbildung für t+1
```

Eine konkrete Übergangsregel ist weiterhin nicht festgelegt. Insbesondere wird
keine Nachbarmittelung als MCM-Mechanik vorausgesetzt.

## 2. Passive Wirkungszerlegung

Für jede lokale Feldprobe `j` am Neuron `i` werden zunächst nur die
vorzeichenbehafteten Unterschiede beobachtet:

```text
delta_activation(i,j) = activation(j,t) - activation(i,t)
delta_afterimage(i,j) = afterimage(j,t) - afterimage(i,t)
```

Rezeptorkontakt, Eigenzustand, Aktivierungsunterschiede und
Nachhallunterschiede bleiben getrennte Messrollen. Der Prüfer setzt sie weder
zu einer neuen Aktivierung zusammen noch versieht er sie mit Gewichten.

## 3. Getragene Invarianten

Die passive Zerlegung erfüllt:

- Ein räumlich gleichförmiges Feld erzeugt keinen lokalen Paarunterschied.
- Eine vollständige Vorzeichenumkehr kehrt auch die Unterschiede um.
- Rezeptorkontakt verändert die vorherige lokale Feldlage nicht rückwirkend.
- Aktivierung und Nachhall bleiben unterscheidbare Zustandsrollen.
- In einer geschlossenen symmetrisch abgetasteten Schicht summieren sich die
  rohen Paarunterschiede zu null.
- Die technische Iterationsreihenfolge bleibt ohne Wirkung.

## 4. Wichtiger Negativbefund

Die häufig naheliegende Größe

```text
Mittelwert der Nachbaraktivierung - eigene Aktivierung
```

ist an Feldrändern nicht global erhaltend, weil Randneuronen und innere
Neuronen unterschiedlich viele lokale Partner besitzen. Eine rohe Summe der
gegenseitigen Paarunterschiede ist bei symmetrischen Paaren erhaltend, wirkt
aber abhängig von der lokalen Partnerzahl.

Beide Varianten beschreiben zudem zunächst nur Ausgleich oder Glättung. Keine
von ihnen belegt Entwicklung, Feldintelligenz oder organische Organisation.

## 5. Stopplinie

Der neue Prüfer ist ein passiver Observer und keine Runtime-Freigabe. Noch
nicht zulässig sind:

- Anwendung der Paardifferenz als Aktivierungsänderung,
- feste Kopplungsstärke oder feste Nachhallrate,
- Clipping als Ersatz für eine begründete Dynamik,
- adaptive Gewichte oder gespeicherte Kanten,
- Interpretation von Glättung als Feldorganisation.

## 6. Ergebnis

Die lokale Wahrnehmung ist nun mathematisch prüfbar, ohne die gesuchte Funktion
vorwegzunehmen. Zugleich zeigt die Prüfung, dass die vorhandenen Zustände
`activation` und `afterimage` noch keine nichttriviale organische Feldfunktion
begründen. Vor einer Runtime-Regel muss geklärt werden, welche beobachtbare
Funktion über reine Projektion, Relaxation und Diffusion hinaus fehlt.

## 7. Bester nächster Schritt

Als nächstes werden ausschließlich minimale Zustandskandidaten gegeneinander
geprüft: Kann der vorhandene Nachhall eine eigenständige lokale Feldbewegung
tragen, oder benötigt das Neuron eine getrennte reversible Feldgröße wie
lokale Spannung beziehungsweise Bewegungsrichtung? Erst ein abgegrenzter
Funktionsgewinn darf die Neuronenhülle erweitern.
