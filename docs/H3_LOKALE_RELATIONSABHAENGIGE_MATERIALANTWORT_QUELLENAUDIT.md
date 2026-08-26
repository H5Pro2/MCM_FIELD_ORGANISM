# H3: lokale relationsabhaengige Materialantwort - Quellenaudit

## Status

```text
Auditart:                              statisch / codegestuetzt
lokale relationale Feldwirkung:        vorhanden
observerfreie zusaetzliche Ereignisrolle: nein
eigenstaendiger Informationsgehalt:    nein
geschichtliche Fortwirkung:            nein
H3-Materialantwort zugelassen:         nein
Runtime-Aenderung:                     nein
```

## Forschungsfrage

H3 fragt, ob eine lokale relationale Feldbewegung als Schreibursache eines
Substrats dienen kann, ohne globale MINI_DIO-Raenge, gespeicherte Zyklen,
Partneridentitaeten oder einfache Produktintegratoren einzufuehren.

Vor jeder Materialantwort muss deshalb geklaert werden:

> Besitzt die heutige atomare MCM-Runtime bereits eine lokale observerfreie
> relationale Ereignisquelle, die mehr Information traegt als Aktivierung,
> Nachhall, feste Anatomie und momentaner Feldfluss?

## Lokal kausal vorhandene Quellen

Ein heutiger lokaler `MCMNeuronDrive` besitzt:

- eigenen abgeschlossenen Vorzustand;
- aktuellen Rezeptorkontakt oder Kontaktabwesenheit;
- lokale Aktivierungs- und Nachhallproben aus dem abgeschlossenen Vortakt;
- relative technische Probenpositionen;
- gemeinsame Organismusdauer;
- gegebenenfalls geordnete transiente Rezeptorabschluesse.

Die atomare Transition erzeugt daraus nur die naechste Aktivierung und den
naechsten schnellen Nachhall. Es existiert kein weiterer Runtimezustand fuer
Relation, Gradient, Fluss, Uebergang, Rangwechsel oder Feldarbeit.

## Gepruefte relationale Quellen

### Lokale Aktivitaetsdifferenz

```text
activation(j,t) - activation(i,t)
```

Sie ist lokal, gerichtet und observerfrei in den Feldproben darstellbar. Sie
ist aber vollstaendig Teil des gegenwaertigen schnellen Feldzustands.

### Gerichteter momentaner Feldfluss

```text
J(j -> i,t) = r * (activation(j,t) - activation(i,t))
```

Der Fluss wirkt real in der neutralen Diffusion. Der Redundanzbefund zeigt
jedoch exakte Rekonstruktion aus Aktivierung, fester Nachbarschaft und
Reaktionsrate. Nach Angleichung des schnellen Feldes sind alle Fluesse gleich.

### Lokale Divergenz oder Gradient

Gradient, Kantenfluss und Knotendivergenz sind Umformulierungen derselben
momentanen Diffusionsinformation. Sie erzeugen keine weitere kausale Rolle.

### Zeitliche Zustandsdifferenz

```text
activation(i,t) - activation(i,t-1)
```

Diese Differenz kann aus zwei abgeschlossenen Feldlagen rekonstruiert werden.
Sie ist jedoch Transitionsergebnis, keine vor der Transition unabhaengig
vorhandene Ursache. Eine Speicherung waere eine weitere Zeitspur.

### Gerichtetes zeitliches Produkt

Der vorhandene Zeitrichtungsaudit verwendete:

```text
activation(i,t-1) * activation(j,t)
- activation(j,t-1) * activation(i,t)
```

Damit ist zeitliche Richtung beobachtbar. Der Wert wurde aber fuer alle
lokalen Beziehungen ungleich null und ist vollstaendig durch zwei
aufeinanderfolgende Feldzustaende sowie den festen Leser bestimmt. Er erzeugt
keine selektive lokale Ereignisquelle.

### MINI_DIO-Rangwechsel und Rangzyklus

MINI_DIO zeigte eine resetfrei rekonstruierbare relative Eigenform aus
aufeinanderfolgenden globalen Rangordnungen und eine variable Schliessung bei
erster exakter Rangwiederkehr.

Diese Funktion ist fuer Feldzeit wichtig, aber nicht direkt uebertragbar:

- globale Paarraenge sind keine lokale Runtimeursache;
- feste Neuronenmitglieder und alte Indexrichtung belasten die Form;
- exakte Wiederkehr benoetigt observerseitigen Zustandsvergleich;
- das Uebergangsprofil wirkte nicht ins Feld zurueck;
- die starke Quellform war kurzlebig und noch keine Relevanzauswahl.

## Informationsentscheidung

Alle heute observerfrei vorhandenen lokalen relationalen Groessen sind
Funktionen von:

```text
abgeschlossenem schnellem Feldzustand
+ fester lokaler Anatomie
+ gegenwaertigem Weltkontakt
+ Organismusdauer
```

Sie enthalten keine unabhaengige Geschichte, sobald Aktivierung und Nachhall
angeglichen wurden.

Eine H3-Materialantwort muesste deshalb selbst festlegen:

1. welche relationale Form gelesen wird;
2. wie diese Form zeitlich akkumuliert oder umgebildet wird;
3. wie sie begrenzt und geloest wird;
4. wie sie spaetere Feldwirkung veraendert.

Diese vier Festlegungen waeren bereits die gesuchte Materialphysik. Sie folgen
nicht aus einer vorhandenen eigenstaendigen Ereignisquelle.

## Kollision mit Pflichtbaselines

| H3-Lesart | Naechste einfachere Erklaerung |
|---|---|
| zeitliche Aktivitaetsdifferenz | zusaetzliche Leaky- oder Differenzspur |
| Kontakt mal Feldabweichung | C1-Produktintegrator |
| gerichtetes Zwei-Zeitlagen-Produkt | fester antisymmetrischer Leser |
| Flussbetrag oder Flussquadrat | lokaler Momentenintegrator |
| wiederkehrende lokale Form | feste Rekurrenz oder Attraktor |
| verstaerkte spaetere Leitung | adaptiver Gain oder Kantengewicht |
| exakte Wiederkehr als Abschluss | Schwellen- oder Zustandsautomat |

H3 besitzt damit keine vorab erkennbare funktionale Nichtredundanz.

## Entscheidung

H3 wird als eigenstaendige Materialfamilie geschlossen. Das Feld besitzt
reale lokale relationale Bewegung und zeitliche Richtung, aber keine
zusaetzliche observerfreie relationale Ereignisrolle mit eigenstaendigem
Informationsgehalt.

Diese Entscheidung bedeutet nicht, dass zeitliche Relationen unwichtig sind.
Sie bleiben:

- Teil des schnellen MCM-Wahrnehmungsfeldes;
- Grundlage der bekannten MINI_DIO-Eigenzeit;
- moegliche lokale Anregung einer spaeter bewusst gesetzten Substratphysik;
- Pflichtdimension fuer spaetere Feldzeit- und Memory-Pruefungen.

Sie begruenden allein jedoch keine Materialantwort.

## Gemeinsames Ergebnis H1 bis H3

```text
H1 lokale Empfaenglichkeit
-> technisch moeglich, aber C1-Produktintegrator plus Leser

H2 umverteilbares Medium
-> Bilanz moeglich, aber Bewegungsphysik nicht aus MCM herleitbar

H3 relationale Materialantwort
-> relationale Quellen vorhanden, aber schnellzustandsredundant
```

Die Suche nach einem Substrat, das sich zwingend aus der heutigen schnellen
MCM-Gleichung ergibt, ist damit ausgeschoepft.

## Neue Richtungsfolgerung

Der naechste sinnvolle Architekturweg ist keine vierte beliebige
Materialformel. Er sollte direkt an der Projektidee zweier gekoppelter
MCM-Dynamikrollen innerhalb desselben gemeinsamen Feldes ansetzen:

```text
schnelle MCM-Wahrnehmungsdynamik
<-> langsameres MCM-Entwicklungssubstrat
-> ein gemeinsames MCM-Feld
```

Dabei waere die langsame Rolle nicht als Datenbank, Kante, separates
Organismusfeld oder externes Material zu verstehen, sondern als zweite
MCM-Substratdynamik mit eigener Entwicklungsskala innerhalb derselben lokalen,
atomaren und bedeutungsfreien Feldordnung.

Auch dieser Weg ist noch nicht freigegeben. Ein bloss langsameres identisches
Feld koennte vollstaendig auf mehrere Leaky-Spuren oder feste Rekurrenz
zurueckfallen.

## Bester naechster Schritt

Als naechstes wird ein darstellungsoffener
**Zwei-MCM-Substratrollen-Vertrag** erstellt. Er soll pruefen:

1. welche Funktion das langsame Substrat gegenueber langsamem Nachhall oder einer
   zweiten identischen Runtime zusaetzlich leisten muesste;
2. wie beide Felder lokal gekoppelt werden koennen, ohne Lernregel, Label,
   Reward oder Zieltopologie;
3. wie relative Feldzeit aus der Kopplung beider Dynamikrollen operational
   entsteht, ohne zwei getrennte Felder einzufuehren;
4. wie ein Zustandstausch oder eine Neutralisierung die spaetere schnelle
   Feldwirkung kausal isolieren koennte;
5. wie Loesung und andere Wiederpraegung ohne feste Ablaufzeit definiert
   bleiben.

Noch werden weder zweite Runtime, Zustandsvariable, Kopplungsgleichung noch
Testlauf implementiert.
