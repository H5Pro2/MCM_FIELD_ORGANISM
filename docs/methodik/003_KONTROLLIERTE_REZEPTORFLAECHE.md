# Methodik 003: Kontrollierte lokale Rezeptorfläche

## 1. Status und Grenze

Diese Methodik prüft die Informationsgrenze unabhängiger lokaler Träger auf
einer kontrollierten zweidimensionalen Rezeptorfläche.

```text
lokaler Kontakt auf einer 3x3-Fläche
-> direkte lokale Trägerzuordnung
-> unabhängiger B0- oder B1-Zustand
-> passiver exakter Zustandsvergleich
```

Es werden keine Nachbarschaft, Diffusion, räumliche Faltung,
Musterklassifikation, globale Auslese oder Handlung implementiert.

## 2. Forschungsfrage

Welche räumlich-zeitliche Information erhält eine Fläche unabhängiger lokaler
Träger bereits vollständig, und welcher konkrete Weltkontakt geht ohne
Trägerwechselwirkung tatsächlich verloren?

## 3. Kontrollierte Fläche

Die erste Fläche besitzt neun technische Positionen:

```text
p00 p01 p02
p10 p11 p12
p20 p21 p22
```

Jede Position ist genau einem unabhängigen Träger zugeordnet. Die Zuordnung ist
eine technische Kontrollbedingung, keine entstandene Topologie.

Ein Kontaktframe enthält pro Position einen Wert im normalisierten Bereich
`[-1, 1]`. Es gibt keine Vorverarbeitung außer der direkten positionsgleichen
Zuordnung.

## 4. Baselines

### B0: Zustandslose Fläche

Jeder Träger übernimmt nur seinen aktuellen lokalen Kontakt. Frühere Kontakte
bleiben nicht erhalten.

### B1: Unabhängige Leaky-Fläche

Jede Position verwendet ausschließlich den in Methodik 002 geprüften lokalen
Leaky-Nachhall. Zwischen Positionen existiert keine Wirkung.

### B2: Globale Summation

Die Summe aller Positionswerte dient nur als Verlustbaseline. Räumlich
verschiedene Kontakte mit gleicher Summe müssen kollidieren.

### B3: Lokale Wechselwirkung

B3 bleibt gesperrt. Es darf nur geöffnet werden, wenn eine notwendige
Weltinformation benannt wird, die B0 und B1 nicht tragen und die nicht erst
durch einen externen Klassifikator zur Funktion erklärt wird.

## 5. Kontaktfamilien

Geprüft werden:

- einzelner Kontakt an jeder Position,
- zwei gleichzeitige Kontakte mit gleicher Gesamtsumme,
- benachbarte und getrennte gleichzeitige Kontakte,
- horizontale Vorwärts- und Rückwärtsfolge,
- vertikale Vorwärts- und Rückwärtsfolge,
- gleiche Endposition nach verschiedener Richtung,
- Kontaktfolge mit und ohne Pause,
- gleiche geometrische Folge an verschobener Position,
- Mehrkontakt mit positiver und negativer Polarität,
- vollständige Nullgeschichte,
- absichtlich konstruierte verschiedene Geschichten mit gleicher B1-Endlage.

## 6. Prüfbare Funktionen

### F1: Positionsidentität

Ein lokaler Kontakt verändert nur den zugeordneten Träger. Kontakte an
verschiedenen Positionen bleiben verschieden.

### F2: Verteilungserhalt

Verschiedene räumliche Kontaktverteilungen mit gleicher Gesamtenergie bleiben
im vollständigen Flächenzustand unterscheidbar.

### F3: Richtungsunterscheidung im Nachhallfeld

Vorwärts- und Rückwärtsfolgen dürfen bei identischer aktueller Nullaktivierung
verschiedene verteilte B1-Nachhalllagen erzeugen.

Das ist nur eine Zustandsdifferenz. Es wird keine Richtung erkannt oder
benannt.

### F4: Lokaler Geschichtskontext

Bei identischem aktuellen Kontakt an derselben Position darf eine andere
Vorgeschichte an anderen Positionen im gesamten Flächenzustand sichtbar
bleiben.

### F5: Translationsentsprechung

Dieselbe Kontaktgeometrie an verschobener Lage soll nach entsprechender
Rückverschiebung dieselben lokalen Werte erzeugen. Die Fläche darf keine
inhaltliche Vorzugsposition besitzen.

### F6: Keine unbegründete Ausbreitung

Ohne Kontakt an einer Position und ohne eigene frühere Spur bleibt ihr Zustand
null. Benachbartsein allein erzeugt keine Wirkung.

### F7: Geschichtskollision

Es muss explizit geprüft werden, ob verschiedene Kontaktgeschichten in
derselben vollständigen B1-Endlage kollabieren. Eine solche Kollision markiert
die Grenze des unabhängigen Einspurmodells.

## 7. Messgrößen

- vollständiger Aktivierungsvektor
- vollständiger Nachhallvektor
- exakte Positionsdifferenz
- Differenz bei gleicher Gesamtsumme
- Vorwärts-/Rückwärtsdifferenz
- Differenz bei gleicher Endposition
- Differenz nach räumlicher Rückverschiebung
- Aktivität nie kontaktierter Positionen
- Anzahl absichtlich verschiedener Geschichten mit identischer Endlage

Es werden keine Musterklassen, Bewegungslabels oder Bedeutungswerte erzeugt.

## 8. Pflichtkontrollen

### C1: Direkte Zuordnung

Jeder einzelne Kontakt muss exakt an der zugeordneten Position erscheinen.

### C2: B2-Kollision

Mindestens zwei räumlich verschiedene Kontaktverteilungen mit gleicher Summe
müssen in B2 kollidieren, im vollständigen Zustand aber verschieden bleiben.

### C3: Reihenfolgeneutralität der Berechnung

Eine Permutation der technischen Trägerberechnung muss nach Rückordnung
denselben Flächenzustand ergeben.

### C4: Reset

Nach vollständigem Nullreset erzeugt dieselbe Geschichte exakt dieselbe
Endlage.

### C5: Parameterfamilie

Richtungs-, Pausen- und Kollisionsprüfungen werden über dieselbe offene
`tau`/`dt`-Familie aus Methodik 002 geführt.

### C6: Observerfreiheit

Alle Aussagen beruhen auf exakten Zustandsvergleichen. Eine
Observerklassifikation darf für keinen Unterschied notwendig sein.

## 9. Erwartung

Erwartet wird:

- B0 erhält die vollständige aktuelle räumliche Verteilung.
- B1 erhält zusätzlich einen begrenzten verteilten Nachhall.
- Vorwärts und rückwärts erzeugen verschiedene Nachhallgradienten.
- Gleiche Endkontakte nach anderer lokaler Vorgeschichte bleiben als gesamter
  Vektor häufig unterscheidbar.
- B2 verliert räumliche Verteilung.
- Verschiedene Geschichten können trotzdem exakt auf dieselbe B1-Endlage
  kollabieren.
- Keine Position wirkt auf eine andere.

## 10. Entscheidungskriterien

### D1: Kein notwendiger Informationsverlust

Wenn B0 und B1 Position, aktuelle Verteilung, Richtungsspur, Pause und
Translation im vollständigen Zustand tragen, ist für diese Funktionen keine
lokale Kopplung begründet.

Eine bloß fehlende interne Weiterleitung ist dann noch kein Funktionsmangel,
solange keine Weltfunktion benannt ist, die diese Weiterleitung benötigt.

### D2: Reale Informationslücke

Eine Kopplungsprüfung darf nur erwogen werden, wenn zwei Weltgeschichten:

1. für eine konkret benannte spätere Weltfunktion verschieden sein müssen,
2. in B0 und B1 vollständig kollidieren,
3. nicht durch eine einfache zusätzliche feste Zeitspur getrennt werden,
4. ohne Observerlabel lokal verfügbar sein müssten.

Auch dann ist B3 noch nicht automatisch freigegeben.

## 11. Stoppregeln

Keine Trägerkopplung wird ergänzt, wenn:

- nur die globale Summe Information verliert, der vollständige Vektor aber
  nicht,
- eine gewünschte Richtung bereits aus dem Nachhallgradienten sichtbar ist,
- die Forderung lediglich „Feld soll sich ausbreiten“ lautet,
- eine Kopplung nur interessantere Bilder erzeugen würde,
- der behauptete Mangel erst durch externe Klassifikation entsteht,
- keine spätere Weltwirkung von der fehlenden Information abhängt.

## 12. Evidenzgrenze

Ein positiver Lauf kann E1 für die Informationskarte der kontrollierten
Baselines tragen.

Er zeigt weder ein MCM-Feld noch Wahrnehmung, Bewegungserkennung, Semantik,
Lernen oder Feldintelligenz.

## 13. Bester nächster Schritt

Nach dieser Vorregistrierung wird nur die kontrollierte 3x3-Fläche mit B0 und
B1 implementiert. B3 bleibt unabhängig vom visuellen Eindruck der Ergebnisse
geschlossen, bis die Entscheidungskriterien erfüllt sind.
