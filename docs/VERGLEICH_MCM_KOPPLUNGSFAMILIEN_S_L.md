# Vergleich der MCM-Kopplungsfamilien S <-> L

## Status

```text
Vergleichsart:                    statisch / darstellungsoffen
gepruefte Kopplungsfamilien:      vier
funktional direkt zugelassen:     keine
offene Oberklasse:               gemeinsame lokale Mitentwicklung
konkrete Naturhypothese:          fehlt
Runtime-Aenderung:                nein
```

## Ausgangspunkt

Der Zwei-MCM-Substratrollen-Vertrag unterscheidet innerhalb desselben
gemeinsamen Feldes:

```text
S = schnelle Wahrnehmungsdynamik
L = langsameres Entwicklungssubstrat
```

Der Vergleich prueft vier moegliche Kopplungslesarten. Eine Familie wird nicht
dadurch neu, dass sie `MCM`, `Substrat`, `organisch` oder `Feldzeit` genannt
wird. Entscheidend ist ihre kleinste technische Zerlegung.

## K1: gemeinsame lokale Zustandsentwicklung

### Funktionsidee

S und L werden atomar aus demselben abgeschlossenen lokalen Gesamtzustand
fortgeschrieben:

```text
(S(t), L(t), Weltkontakt(t))
-> (S(t+1), L(t+1))
```

Es existiert kein nachgeschalteter Memory-Leser. Beide Rollen sind Teil
desselben lokalen Zustandsvorschlags.

### Positiver Architekturwert

- Ein-Feld-Prinzip bleibt erhalten.
- Bildung und Wirkung koennen innerhalb derselben Kausalgrenze liegen.
- Zustandstausch und Neutralisierung sind grundsaetzlich definierbar.
- Relative Feldzeit koennte aus gemeinsamer Trajektorie statt separater Uhr
  beobachtet werden.

### Baselinekollision

Diese Beschreibung legt keine Physik fest. Jede feste gekoppelte Rekurrenz
kann in derselben Form geschrieben werden. Je nach konkreter Funktion entsteht:

- eine Kaskade fester Leaky-Spuren;
- eine zweite langsame Kopie des schnellen Feldes;
- ein fester Attraktor;
- ein nichtlinearer Zustandsautomat;
- ein adaptiver Gain mit internem Zustand.

### Entscheidung

**Als Oberklasse offen, als Kandidat nicht zugelassen.**

K1 beschreibt den richtigen atomaren Ort einer spaeteren Hypothese, aber noch
keine funktionale Nichtredundanz.

## K2: langsame Veraenderung der Feldaufnahme

### Funktionsidee

L veraendert, wie lokaler Rezeptorkontakt in die schnelle Feldentwicklung
eingeht.

```text
Weltkontakt + L
-> veraenderter schneller Eintritt
```

### Baselinekollision

K2 entspricht unmittelbar den bereits geprueften Familien:

- C1 beziehungsweise H1 als lokale Empfaenglichkeit;
- adaptiver Rezeptorgain;
- Ermuedungs-/Erholungsintegrator;
- memristive Eingangskennlinie;
- mehrere feste Leaky-Zeitlagen plus Leser.

Ohne eine unabhaengige gemeinsame Substratphysik entsteht die Wirkung erst
durch die fest programmierte Eingangsmodulation.

### Entscheidung

**Geschlossen als eigenstaendige Familie.**

K2 darf spaeter nur Wirkung einer bereits anderweitig begruendeten
Mitentwicklung sein, nicht deren Begruendung.

## K3: langsame Veraenderung der Feldweiterleitung

### Funktionsidee

L veraendert, wie schnelle Feldwirkung lokal weitergegeben wird.

```text
schnelles Vorfeld + L
-> veraenderte lokale Ausbreitung
```

### Baselinekollision

Je nach Darstellung entsteht:

- adaptive Leitfaehigkeit;
- persistentes Kantengewicht;
- zustandsabhaengige Diffusion;
- H3-Materialantwort;
- feste lokale Rekurrenz mit zusaetzlichem Zustand;
- Hysterese in der Weiterleitungskennlinie.

Eine partnerlose lokale Mediumrolle waere strukturell sauberer als eine
gespeicherte Kante. Ohne konstitutive Materialbegruendung bleibt die
Weiterleitungswirkung dennoch programmiert.

### Entscheidung

**Geschlossen als eigenstaendige Begruendung.**

Wie K2 kann K3 spaeter eine Wirkung einer begruendeten Mitentwicklung sein,
aber nicht selbst den langsamen Zustand rechtfertigen.

## K4: gemeinsame begrenzte Feldkapazitaet

### Funktionsidee

S und L beanspruchen eine endliche lokale Faehigkeit. Veraenderte Beanspruchung
koennte Praegung, Konkurrenz, Loesung und Wiederpraegung verbinden.

### Baselinekollision

K4 entspricht den bereits untersuchten Ressourcenfamilien:

- lokale Kapazitaetsvariable;
- divisive Normalisierung;
- Gewinner- oder Konkurrenzregel;
- konserviertes Zusatzmaterial;
- strukturelles Kontaktmaterial;
- Phasenfeld mit vorgegebener Energielandschaft.

Die Ressource ist nur dann eine unabhaengige Naturbedingung, wenn Stoffrolle,
Erhaltung, Bewegung und Rueckwirkung vor jeder Memory-Funktion begruendet
sind. Der H2-Audit zeigte, dass diese Herleitung derzeit fehlt.

### Entscheidung

**Geschlossen als eigenstaendige Familie.**

Eine spaetere explizite Materialhypothese darf Begrenzung besitzen. Begrenzung
allein erzeugt jedoch keine MCM-Entwicklung.

## Vergleichsmatrix

| Familie | Staerkste positive Rolle | Kleinste Gegenbaseline | Entscheidung |
|---|---|---|---|
| K1 gemeinsame Mitentwicklung | korrekte atomare Ein-Feld-Grenze | feste gekoppelte Rekurrenz | Oberklasse offen |
| K2 Feldaufnahme | direkter innerer Kontext | H1/C1, Gain, Leaky-Leser | als Begruendung geschlossen |
| K3 Feldweiterleitung | lokale Rueckwirkung im Feld | adaptive Kante, Hysterese, B5 | als Begruendung geschlossen |
| K4 Feldkapazitaet | gemeinsamer Lebenszyklus denkbar | Ressource, Norm, Phasenfeld | als Begruendung geschlossen |

## Zentrale Erkenntnis

Aufnahme, Weiterleitung und Kapazitaet sind **Wirkungsorte**, keine
Entstehungsprinzipien.

```text
L veraendert Aufnahme
```

erklaert noch nicht, warum L existiert oder wie L entsteht. Dasselbe gilt fuer
Weiterleitung und Kapazitaet.

Nur K1 setzt die Rollen kausal korrekt zusammen. K1 bleibt jedoch eine leere
Oberklasse, solange keine konkrete lokale Naturhypothese festlegt, wie die
gemeinsame Mitentwicklung verlaeuft und welche Verlaeufe sie ausschliesst.

## Nichtredundanz kann nicht rein strukturell behauptet werden

Keine Datenstruktur garantiert organische Entwicklung:

- ein Skalar kann ausreichend oder trivial sein;
- ein Vektor kann nur mehrere Leaky-Spuren enthalten;
- ein Graph kann vorgegebene Kanten speichern;
- ein Feld kann feste Rekurrenz darstellen;
- eine Ressource kann programmierte Konkurrenz enthalten.

Nichtredundanz ist erst durch den gesamten Lebenszyklus entscheidbar:

```text
Bildung
-> Mitentwicklung unter neuer Evidenz
-> spaetere Feldwirkung
-> Tausch und Neutralisierung
-> vollstaendige funktionale Loesung
-> andere Wiederpraegung
```

## Verhaeltnis zur relativen Feldzeit

Relative Feldzeit darf K1 nicht nachtraeglich legitimieren. Sie ist eine
moegliche beobachtbare Eigenschaft einer gekoppelten Trajektorie, nicht die
Updateursache.

Eine spaetere Hypothese muss deshalb zuerst eine lokale Dynamik besitzen. Erst
danach kann geprueft werden, ob deren kausale Entwicklungsordnung von
Weltsekunden, Ticks und Leaky-Zeitkonstanten abweicht.

## Forschungsentscheidung

Keine der vier Kopplungsfamilien liefert aus sich heraus eine implementierbare
Naturbedingung.

Getragen ist nur die Architekturgrenze:

> Eine spaetere Substrathypothese muss als gemeinsame lokale und atomare
> Mitentwicklung von S und L im selben MCM-Feld formuliert werden. Aufnahme,
> Weiterleitung und Begrenzung duerfen Folgen dieser Mitentwicklung sein,
> aber nicht ihre alleinige Begruendung.

Damit endet die rein darstellungsoffene Kandidatensuche. Der naechste Schritt
muss eine bewusst deklarierte minimale Naturannahme enthalten oder die
Substratentwicklung bleibt geschlossen.

## Anforderungen an die erste konkrete Hypothese

Eine erste Hypothese muss vor Implementierung offenlegen:

1. kleinster lokaler Gesamtzustand `(S,L)`;
2. tatsaechlich gelesene lokale Welt- und Feldrollen;
3. gemeinsame atomare Fortschreibung;
4. Nullgrenze zur heutigen Runtime;
5. lokale Kopplungsrichtung in beiden Kausalrichtungen;
6. Begrenzung ohne Zielzustand;
7. moegliche Loesung ohne Phasenbefehl;
8. moegliche andere Wiederpraegung;
9. staerkste gleich budgetierte Baseline;
10. sofortiges Falsifikationskriterium.

Sie muss zugleich erklaeren, warum ihre Naturannahme fachlich vertretbar ist,
obwohl sie nicht zwingend aus der heutigen schnellen MCM-Gleichung folgt.

## Bester naechster Schritt

Als naechstes wird genau **eine minimale K1-Naturhypothese** auf Papier
formuliert, noch ohne Implementierung.

Die konservativste Richtung ist eine lokale gekoppelte MCM-Zustandsdynamik,
bei der L weder Eingangsgain noch Leitgewicht noch Ressourcenzaehler ist,
sondern als eigener begrenzter Entwicklungsfreiheitsgrad gemeinsam mit S
fortgeschrieben wird.

Vor jeder Gleichung muss jedoch entschieden werden, welche unabhaengige
Naturfunktion dieser Freiheitsgrad besitzt. Kann dafuer nur `er soll Memory
ermoeglichen` angegeben werden, wird keine Hypothese formuliert und die
Runtime bleibt geschlossen.

Die erste solche Annahme ist inzwischen als
[K1-Hypothese der reziproken lokalen Akkommodation](K1_HYPOTHESE_REZIPROKE_LOKALE_AKKOMMODATION.md)
formuliert. Sie ist als Forschungsrahmen zugelassen, aber noch nicht als
Gleichung oder Runtime-Kandidat.
