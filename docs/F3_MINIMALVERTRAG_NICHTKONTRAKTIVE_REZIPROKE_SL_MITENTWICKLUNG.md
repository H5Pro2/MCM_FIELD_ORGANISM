# F3-Minimalvertrag: nichtkontraktive reziproke S-L-Mitentwicklung

## Status

```text
Vertragstyp:                       mathematisch-konzeptionelle Zulassungsgrenze
Familie:                           F3
Nichtkontraktivitaet:              nur als Verlaufseigenschaft zulaessig
Reziprozitaet:                     atomar und lokal erforderlich
globale Passivitaet:               nur aus lokalen Bilanzen ableitbar
konkrete Gleichung:                nicht gewaehlt
Implementierung:                   gesperrt
```

## Zweck

Der Vergleich strukturveraendernder K1-Familien behaelt nur F3 bedingt offen.
Dieser Vertrag bestimmt, was eine konkrete F3-Schliessung mindestens leisten
und was sie bereits vor einer Implementierung vermeiden muss.

Der Vertrag beweist weder, dass eine solche Schliessung existiert, noch dass
sie den gesuchten Lebenszyklus traegt.

## 1. Was nichtkontraktiv sein darf

### Verlaufseigenschaft statt Organismusvariable

Nichtkontraktivitaet bezeichnet ausschliesslich einen Vergleich zweier
kontrollierter Verlaeufe:

```text
Geschichte A -> lokaler Gesamtzustand X_A
Geschichte B -> lokaler Gesamtzustand X_B

ab dann identischer lokaler Welt- und Feldverlauf
-> der funktionale Abstand der Fortsetzungen muss nicht sofort kleiner werden
```

Dabei bezeichnet `X` den gemeinsamen lokalen S-L-Zustand. Der Abstand ist
eine spaetere Analysegroesse. Die Runtime darf weder den Parallelverlauf noch
einen Abstand zu ihm lesen.

Damit ist verboten:

- eine Solltrajektorie;
- ein Fehler zwischen aktuellem und gewuenschtem Zustand;
- ein Kontrastivpaar in der Organismusfunktion;
- eine Regel, die bei wachsendem oder fallendem Abstand umschaltet;
- ein gespeicherter Lyapunov-, Gain- oder Neuigkeitswert.

### Zulaessiger Gegenstand

Nichtkontraktiv sein darf nur eine Variation des vollstaendigen lokalen
S-L-Gesamtverlaufs. Nicht ausreichend sind allein:

- groessere Rohamplitude;
- langsamere Relaxation;
- Phasenverschiebung eines festen Oszillators;
- Saettigung an einer Grenze;
- numerische Rundungs- oder Schrittweitenabweichung;
- laengerer Verbleib in einem programmierten Attraktor.

Die Variation muss spaeter eine schnelle lokale Feldfortsetzung veraendern.
Andernfalls liegt nur ein verborgener langsamer Zustand ohne Feldwirkung vor.

### Zeitliche Begrenzung

F3 verlangt keine dauerhafte Expansion. Zulaessig ist, dass Unterschiede in
bestimmten durch Weltgeschichte entstandenen Bereichen zeitweilig erhalten
oder vergroessert werden und unter anderer weiterer Geschichte wieder
vollstaendig funktionslos werden.

Eine fest programmierte Expansionsphase, Expansionsdauer oder Umschaltschwelle
ist verboten.

## 2. Reziprozitaet ohne Fehler- oder Zielbegriff

### Atomare Kreuzwirkung

Eine zulaessige lokale Wechselwirkung muss innerhalb desselben atomaren
Uebergangs sowohl S als auch L veraendern:

```text
(S,L, lokales Vorfeld, Weltkontakt, dt)
-> (S',L')
```

Unzulaessig waere:

```text
S wird zuerst in L geschrieben
L wird spaeter von einem festen Leser auf S angewendet
```

Die konkrete Schliessung muss durch lokale Interventionen zeigen koennen,
dass beide Wirkungsrichtungen zur gemeinsamen Fortsetzung beitragen. Eine
Richtung darf nicht nur diagnostisch korreliert sein.

### Kein Anpassungsziel

Reziprozitaet bedeutet nicht, dass S und L einander angleichen sollen. Ihre
Differenz ist weder Fehler noch Loss. Eine spaetere Gleichung darf daher
nicht aus einem vorgegebenen Abstand mit dem Ziel seiner Minimierung oder
Maximierung hergeleitet werden.

Insbesondere sind ausgeschlossen:

- `L soll S vorhersagen`;
- `S soll einem in L gespeicherten Muster folgen`;
- `Wiederholung soll die Kopplung verstaerken`;
- `Abweichung soll eine Lernrate steuern`.

### Keine getrennte konstitutive Lesestruktur

L darf kein gespeicherter Koeffizient sein, der einen ansonsten unveraenderten
S-Pfad skaliert, rotiert oder routet. Die gemeinsame Naturform darf vom
Gesamtzustand abhaengen; sie darf aber nicht in gespeicherte Struktur plus
festen Wirkungsleser zerfallen.

Ob eine konkrete Form dennoch mathematisch genau auf Gain, Mobilitaet,
adaptive Kante oder feste Rekurrenz reduzierbar ist, bleibt Gegenstand des
naechsten Audits.

## 3. Lokale Bilanz und globale Passivitaet

### Lokale Form

Eine spaetere F3-Schliessung muss eine nichtnegative lokale
Speicher- beziehungsweise Begrenzungsgroesse `B_i` besitzen oder eine
gleichwertige mathematische Schranke nachweisen.

Fuer jeden gleichartigen lokalen Ort muss unterscheidbar sein:

```text
Zufuhr durch Weltkontakt und vorhandenen Feldfluss
interner reziproker S-L-Austausch
Abgabe an lokales Feldumfeld
lokale Dissipation
```

Der interne S-L-Austausch darf in der Gesamtbilanz keine unbegruendete Quelle
sein. Die konkrete Bilanzform wird hier noch nicht festgelegt.

### Global nur als Folgerung

Die globale Grenze muss durch Summation beziehungsweise Integration der
lokalen Bilanzen folgen. Sie darf nicht innerhalb der Organismusfunktion
berechnet oder durchgesetzt werden.

Verboten sind daher:

- globale Normierung aller Orte;
- zentraler Energie- oder Aktivitaetstopf;
- Gewinnerauswahl bei Ueberschreitung eines Budgets;
- globaler Observer, der lokale Updates skaliert;
- Clipping als behauptete Passivitaetsphysik;
- freie oder belegte Slots als Memory-Ressource.

### Warum Passivitaet Nichtkontraktivitaet nicht ausschliesst

Eine begrenzte Gesamtgroesse kann umverteilt werden, waehrend der Abstand
zweier Verlaeufe zeitweilig waechst. Das ist beispielsweise bei nichtnormalen
oder zustandsabhaengigen Flussgeometrien mathematisch moeglich.

Dieser Hinweis ist nur ein Existenzmotiv. Nichtnormale lineare Dynamik,
Oszillation und transienter Energieaustausch bleiben Pflichtbaselines und
duerfen nicht als Entwicklung ausgegeben werden.

## 4. Trennung von Naturform und entstandener Geschichte

| Fest programmiert zulaessig | Muss aus Weltgeschichte folgen |
|---|---|
| endliche lokale S-L-Dimension | konkrete S-L-Belegung |
| identische lokale Updateform | Ort und Richtung einer Abweichung |
| lokaler Wirkungsradius | beteiligte Feldorte |
| Symmetrien und Wertebereiche | konkrete spaetere Feldwirkung |
| lokale Bilanzform | Staerke und Dauer der Wirkung |
| neutrale Passivitaetsgrenze | funktionaler Verlust alter Wirkung |
| technische Integrationsordnung | Form einer spaeteren anderen Wirkung |

Kann aus der linken Spalte bereits abgelesen werden, welche Lage, Richtung,
Episode oder Beziehung spaeter bestehen soll, ist die Schliessung zu stark
vorgegeben.

## 5. Pflichtbaselines fuer jede konkrete Form

Eine F3-Schliessung muss mindestens gegen gleich budgetierte Varianten dieser
Klassen geprueft werden:

1. lineare nichtnormale Rekurrenz mit transienter Verstaerkung;
2. gedaempfter und ungedaempfter gekoppelter Oszillator;
3. feste nichtlineare Rekurrenz mit Saettigung;
4. feste Hysteresekurve oder memristive Kennlinie;
5. adaptiver skalarer beziehungsweise gerichteter Gain;
6. zustandsabhaengige Mobilitaet oder variable Zeitkonstante;
7. Mehrfach-Leaky-Spuren mit demselben Zustandsbudget;
8. feste Attraktorlandschaft mit gleicher lokaler Dimension.

Eine groessere Nachwirkung als bei einer schwachen Baseline genuegt nicht.
Die Baselines muessen Parameter-, Zustands- und Rechenbudget der F3-Form
angemessen abdecken.

## 6. Kausale Mindestbedingungen

Noch vor einem Memory-Lebenszyklus muss eine konkrete F3-Form spaeter zeigen:

1. **Nullpfad:** Neutraler L-Zustand und neutralisierte Kreuzwirkung ergeben
   exakt die heutige schnelle MCM-Runtime.
2. **Weltursache:** Ohne lokale Welt- oder Feldteilnahme entsteht keine
   konkrete Verlaufstrennung.
3. **Gemeinsame Fortsetzung:** Verschiedene Vorgeschichten entwickeln sich
   unter identischer neuer Wirkung bereits vor einer Probe verschieden.
4. **S-Wirkung:** Die langsame Vorgeschichte veraendert die vollstaendige
   schnelle Feldtrajektorie und nicht nur einen Diagnosewert.
5. **L-Tausch:** Die spaetere Wirkung wandert mit dem langsamen
   konstitutiven Anteil.
6. **Reziproke Intervention:** Eingriffe in S und L zeigen beide kausalen
   Richtungen der atomaren Wechselwirkung.
7. **Observerfreiheit:** Keine Analyse oder Probe veraendert die Bildung.
8. **Bilanz:** Nichtkontraktive Abschnitte bleiben lokal und global begrenzt,
   ohne zentrale Korrektur.
9. **Baselinegrenze:** Der Befund ist nicht vollstaendig durch eine
   Pflichtbaseline erklaert.

Diese Bedingungen erlauben nur den Ausdruck `substratvermittelte spaetere
Feldwirkung`. Sie erlauben noch keinen Memory- oder Organisationsbegriff.

## 7. Sofortige Stopplinien vor jeder Gleichungswahl

Eine vorgeschlagene F3-Form erhaelt sofort **STOPP**, wenn mindestens einer
dieser Punkte gilt:

1. Die Runtime muss zwei Verlaeufe, eine Probe oder einen Zielzustand
   vergleichen.
2. Mehrere Ziel-, Ruhe- oder Attraktorzustaende werden absichtlich
   einprogrammiert.
3. L ist funktional ein Gain, eine Kante, Mobilitaet, Zeitkonstante, Spur,
   Vorlage oder Ressource mit festem Leser.
4. Passivitaet wird durch globale Normalisierung, Auswahl, Clipping oder Reset
   erzwungen.
5. Nichtkontraktivitaet besteht nur aus Amplitude, Phase, Saettigung,
   Schrittweitenfehler oder Chaos.
6. Der neutrale Zustand erzeugt ohne Weltzufuhr unbegrenzt Eigenwirkung.
7. Bildung oder Loesung benoetigt Phasenkennung, Schwelle, Zaehler oder feste
   Dauer.
8. Der exakte schnelle Nullpfad ist nicht darstellbar.
9. Eine gleich budgetierte Standardbaseline kann prinzipiell nicht definiert
   werden.
10. Die behauptete Struktur existiert nur als Cluster oder Interpretation des
    Observers.

## 8. Offene mathematische Kernluecke

Der Vertrag zeigt noch nicht, dass F3 ausserhalb fester Rekurrenz existiert.
Jede endliche digitale lokale Dynamik besitzt notwendigerweise eine feste
Updateform. Die entscheidende Frage ist deshalb enger:

> Gibt es innerhalb der zugelassenen Grenzen eine minimale reziproke,
> passive und inkrementell zeitweise nichtkontraktive S-L-Dynamik, deren
> funktionale Klasse nicht vollstaendig auf nichtnormale Rekurrenz,
> Oszillation, Hysterese, Gain oder variable Mobilitaet reduziert werden kann?

Falls diese Frage statisch verneint wird, muss F3 geschlossen werden. Dann
waere ein neuer physikalischer Freiheitsgrad oder eine bewusst weiter
geoeffnete Projektannahme erforderlich; eine Umbenennung bekannter Mechanik
waere kein Fortschritt.

## Zulassungsentscheidung

F3 ist unter diesem Minimalvertrag fuer genau einen statischen Existenz- und
Reduzierbarkeitsaudit zugelassen.

```text
F3 als Suchfamilie:                 bedingt zugelassen
F3 als eigenstaendige Mechanik:     nicht nachgewiesen
konkrete Zustandsvariable:          nicht zugelassen
konkrete Gleichung:                 nicht zugelassen
Implementierung oder Test:          nicht zugelassen
```

## Bester naechster Schritt

Als naechstes wird ein **F3-Existenz- und Reduzierbarkeitsaudit** erstellt.
Er soll rein statisch pruefen:

1. welche minimale lokale Zustandsdimension erforderlich waere;
2. ob Passivitaet und zeitweilige inkrementelle Nichtkontraktivitaet gemeinsam
   moeglich sind;
3. ob jede kleinste Form auf nichtnormale Rekurrenz, Oszillator, Hysterese,
   Gain oder Mobilitaet zurueckfaellt;
4. ob danach ein nichtleerer eigenstaendiger F3-Raum uebrig bleibt.

Nur bei einem positiven nichtreduzierbaren Rest darf anschliessend eine
konkrete konstitutive Schliessung vorgeschlagen werden.
