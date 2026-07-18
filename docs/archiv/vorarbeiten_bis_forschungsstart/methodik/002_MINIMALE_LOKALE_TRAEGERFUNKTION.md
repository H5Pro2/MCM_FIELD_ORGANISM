# Methodik 002: Minimale lokale Trägerfunktion

## 1. Status und Grenze

Diese Methodik prüft, ob die derzeit verlangte Minimalfunktion eines
sensorspezifischen MCM-Trägers bereits durch bekannte unabhängige
Filtermechanik vollständig erklärt wird.

```text
lokaler Rezeptorkontakt
-> lokaler schneller Zustand
-> begrenzter Nachhall
-> ungetriebene Relaxation
```

Der Versuch implementiert keinen MCM-Neuronentyp, keine Nachbarschaft, keine
Feldspannung, keine Überlagerung zwischen Trägern und kein Lernen.

## 2. Forschungsfrage

Benötigt diese Minimalfunktion bereits eine neuronähnliche oder feldartige
Wechselwirkung zwischen Trägern, oder genügt ein unabhängiger lokaler
Leaky-Integrator?

## 3. Prüfbare Funktionen

### F1: Lokale Gegenwartsaufnahme

Ein lokaler Kontakt ist am zugehörigen technischen Träger unmittelbar als
Aktivierung darstellbar. Ein anderer Träger wird dadurch nicht verändert.

### F2: Begrenzter Nachhall

Nach einem endlichen Kontakt bleibt vorübergehend eine lokale Spur erhalten,
ohne dass der Eingang weiter anliegt.

### F3: Ungetriebene Relaxation

Ohne neuen Kontakt nähert sich die Spur monoton dem neutralen Zustand. Sie
wächst nicht selbstständig und springt nicht auf andere Träger über.

### F4: Polarität

Positive und negative Kontakte behalten ihre Richtung. Relaxation darf das
Vorzeichen nicht ohne neuen Gegenkontakt umkehren.

### F5: Endliche Lage

Bei begrenzter Aktivierung und begrenztem Ausgangszustand bleibt der nächste
Zustand innerhalb derselben Grenzen.

### F6: Atomare Lokalität

Alle Träger lesen denselben vorherigen Zustand. Technische
Berechnungsreihenfolge darf das Ergebnis nicht verändern.

### F7: Zeitskalenkonsistenz

Bei derselben stückweise konstanten Kontaktgeschichte und derselben gesamten
physikalischen Dauer darf eine feinere technische Schrittweite nicht allein
eine andere Endlage erzeugen.

### F8: Geschichtsgrenze

Es muss sichtbar werden, welche Geschichte der Zustand unterscheiden kann und
welche verschiedenen Verläufe in derselben lokalen Spur zusammenfallen.

## 4. Baselines

### B0: Zustandsloser Träger

```text
a_i(t) = u_i(t)
h_i(t) = 0
```

`u_i` ist der lokale technische Kontakt, `a_i` die gegenwärtige Aktivierung und
`h_i` der Nachhall.

B0 trägt aktuelle Lokalität, aber voraussichtlich keinen Nachhall.

### B1: Unabhängiger Leaky-Nachhall

```text
a_i(t) = u_i(t)

d = exp(-dt / tau)

h_i(t + dt) = d * h_i(t) + (1 - d) * a_i(t)
```

Jeder Träger verwendet nur:

- seinen eigenen aktuellen Kontakt,
- seinen eigenen vorherigen Nachhall,
- die offen ausgewiesene technische Schrittweite `dt`,
- die geprüfte Zeitkonstante `tau`.

Es gibt keine Wirkung zwischen Trägern.

Die Exponentialform wird als Baseline gewählt, weil wiederholte Teilschritte
bei konstantem Eingang exakt derselben Gesamtdauer entsprechen. Sie ist keine
behauptete MCM-Naturgleichung.

### B2: Mehrere feste Zeitkonstanten

B2 wäre eine parallele Gruppe unabhängiger B1-Spuren. Sie wird nur ausgeführt,
wenn B1 eine konkret benannte notwendige zeitliche Funktion nicht trägt.

### B3: Lokale Nachbarschaftswirkung

B3 wäre die kleinste offen ausgewiesene Wirkung zwischen benachbarten
Trägern. Sie bleibt gesperrt, solange keine notwendige Funktion benannt ist,
die unabhängige Träger nicht erfüllen.

## 5. Parameterfamilie

Die Prüfung sucht keine optimale Zeitkonstante. Sie verwendet eine offene
Familie, um die strukturellen Eigenschaften der Gleichung zu prüfen:

```text
tau in {0.25, 1.0, 4.0}
dt  in {1.0, 0.5, 0.25}
```

Diese Werte sind Baseline-Sonden. Kein Wert wird als biologische oder
MCM-spezifische Konstante übernommen.

## 6. Kontaktgeschichten

Mindestens geprüft werden:

- vollständige Nullgeschichte,
- einzelner positiver Impuls,
- einzelner negativer Impuls,
- konstanter Kontakt,
- Kontakt und Pause,
- Kontakt, Pause und erneuter Kontakt,
- Vorzeichenwechsel,
- alternierende Kontakte,
- gleiche Gegenwart nach verschiedener Vorgeschichte,
- verschiedene Vorgeschichten mit absichtlich gleicher B1-Endspur,
- Mehrträgerkontakt an nur einem Träger,
- verschiedene technische Berechnungsreihenfolgen.

## 7. Messgrößen

- Aktivierungsvektor
- Nachhallvektor
- maximale Betragslage
- monotone Relaxationsverletzungen
- Vorzeichenwechsel ohne Gegenkontakt
- Differenz nicht kontaktierter Träger
- Differenz zwischen Berechnungsreihenfolgen
- Differenz zwischen Zeitauflösungen bei gleicher Dauer
- Abweichung bei linearer Amplitudenskalierung
- Anzahl verschiedener Geschichten mit gleicher Endspur

## 8. Pflichtkontrollen

### C1: Mechanik aus

B0 zeigt, welche Funktion ohne Nachhallzustand fehlt.

### C2: Vollständiger Reset

Nach Reset auf Null muss dieselbe Geschichte exakt dieselbe Spur erzeugen.

### C3: Trägerisolation

Kontakt an Träger `i` darf keinen unabhängigen Träger `j` verändern.

### C4: Permutation der technischen Berechnung

Wird dieselbe Zuordnung aus Trägeridentität, Vorzustand und Kontakt in anderer
technischer Reihenfolge berechnet, muss nach Rückordnung dieselbe Lage
entstehen.

### C5: Amplitudenskalierung

Solange die technische Eingangsgrenze eingehalten wird, muss B1 linear mit der
Eingangsamplitude skalieren.

### C6: Zeitauflösung

Ein Kontaktblock derselben Dauer wird mit mehreren `dt`-Werten ausgeführt. Die
Endlagen müssen innerhalb reiner Gleitkommatoleranz übereinstimmen.

### C7: Gegenhistorie

Ein Kontakt mit umgekehrter Polarität muss eine vorhandene Spur lokal
abschwächen oder umkehren können. Das ist noch keine Reorganisation.

## 9. Erwartung

Erwartet wird:

- B0 trägt F1, aber nicht F2.
- B1 trägt F1 bis F7 vollständig.
- B1 unterscheidet manche unmittelbaren Vorgeschichten.
- Verschiedene Geschichten können dieselbe B1-Endspur erzeugen und sind danach
  funktional ununterscheidbar.
- Kein unabhängiger Träger erzeugt räumliche Überlagerung oder Weiterleitung.

## 10. Entscheidungskriterien

### D1: B1 genügt

Wenn B1 F1 bis F7 über die Parameterfamilie trägt, ist für die aktuelle
Minimalfunktion keine neuronähnliche Nachbarschaft begründet.

Dann gilt:

```text
technischer lokaler Nachhall möglich
!= MCM-Feld nachgewiesen
!= Neuron notwendig
```

Die Forschung stoppt vor B2 und B3.

### D2: B1 scheitert

Ein Scheitern rechtfertigt nicht automatisch eine komplexere Mechanik. Zuerst
wird getrennt, ob Ursache ein Implementierungsfehler, eine widersprüchliche
Funktionsforderung oder ein echter lokaler Funktionsmangel ist.

Nur ein reproduzierbarer Funktionsmangel darf B2 oder B3 öffnen.

## 11. Stoppregeln

Keine Nachbarschafts- oder Neuronenmechanik wird eingeführt, wenn:

- B1 alle aktuell geforderten Funktionen erfüllt,
- eine gewünschte Zusatzleistung nicht operationalisiert ist,
- nur reichere oder lebendiger wirkende Trajektorien gesucht werden,
- ein positiver Effekt direkt aus der Leaky-Gleichung folgt,
- mehrere feste Zeitkonstanten bereits genügen würden,
- räumliche Kopplung nur als MCM-Metapher begründet wird.

## 12. Aussage- und Evidenzgrenze

Ein positiver B1-Lauf kann E1 für die korrekte Baselineimplementierung und eine
belastbare Scheitergrenze tragen.

Er zeigt nicht:

- ein MCM-Feld,
- ein digitales Neuron,
- natürliche Feldbildung,
- Überlagerung zwischen Trägern,
- Lernen oder Organisationsgeschichte,
- Feldintelligenz.

## 13. Bester nächster Schritt

Nach dieser Vorregistrierung werden ausschließlich B0 und B1 als reine
Forschungsbaselines implementiert und gegen F1 bis F8 geprüft. B2 und B3
bleiben bis zur Auswertung gesperrt.
