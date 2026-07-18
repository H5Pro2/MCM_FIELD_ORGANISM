# Zulässigkeitsmethodik der ersten lokalen Felddynamik

## Status

Verbindliche Vorregistrierung auf `E0 / CONTRACT_ONLY`.

Diese Methodik wählt keine Feldgleichung aus. Sie bestimmt, welchen
Funktionsmangel ein späterer passiver Kandidat überhaupt bearbeiten darf und
an welchen Gegenprüfungen er vor jeder Runtimefreigabe scheitern muss.

## Konkreter Funktionsmangel

Die technische Feldhülle stellt vier lokale Rollen bereit:

```text
eigener Vorzustand
+ lokale Vorfeldwahrnehmung
+ reale verstrichene Dauer
+ optionaler asynchroner lokaler Dockverlauf
```

Keine vorhandene Transition verbindet diese Rollen zu einer lokalen
Feldentwicklung, die unter gröberer und feinerer Beobachtungsunterteilung
denselben kausalen Endzustand trägt.

- `hold_state_baseline` bewahrt Zustand, ignoriert aber Weltkontakt und Feld.
- `receptor_projection_baseline` zeigt Weltkontakt, ignoriert aber Vorfeld,
  Verlauf und eigene Geschichte.
- feste symmetrische Leser können lokale Wirkung erzeugen, ihre Antwort folgt
  jedoch vollständig aus der programmierten Leserform.

Der Funktionsmangel lautet daher nicht „dem System fehlt Intelligenz“ oder
„das Feld muss lernen“. Er lautet:

> Es fehlt eine lokal-kausale, zeitteilungsinvariante Feldentwicklung, in der
> Weltkontakt und vorhandene Feldlage gemeinsam wirksam sein können, ohne dass
> Sensorfrequenz, Scheduler oder eine feste Bedeutungsregel die Wirkung
> bestimmen.

## Zulässige erste Frage

Ein erster passiver Vergleich darf ausschließlich fragen:

```text
Kann ein expliziter lokaler Übergangskandidat
denselben asynchronen Weltverlauf
unter grober und feiner Beobachtung
zum selben lokalen Endzustand führen,
während Weltkontakt und lokale Vorfeldlage kausal notwendig bleiben?
```

Die Frage verlangt weder Memory noch Topologie, Semantik, Handlung oder
Selbstregulation.

## Pflichtachsen

Jeder Kandidat muss mindestens auf diesen Achsen geprüft werden:

1. **Zeitteilung**: grobe und feine Segmentierung desselben Verlaufs.
2. **Rezeptorrate**: zusätzliche technische Abschlüsse ohne zusätzliche
   Quellenstütze dürfen keine stärkere Wirkung erzeugen.
3. **Abwesenheit**: kein Abschluss ist weder Nullkontakt noch Halten.
4. **Lokalität**: nur eigener Dockverlauf und lokale Vorfeldproben wirken.
5. **Kausalität**: kein Zustand wirkt vor seinem Abschluss.
6. **Gleichzeitigkeit**: technische Reihenfolge gleichzeitig abgeschlossener
   Zustände bleibt wirkungslos.
7. **Geometrie**: Spiegelung und Samplepermutation erzeugen keine versteckte
   Vorzugsrichtung.
8. **Wiederaufnahme**: Unterbrechung durch Snapshot erzeugt keine Doppel- oder
   Fehlwirkung.

## Rollenablationen

Der passive Rahmen muss jeden Eingangsanteil getrennt entfernen oder
kontrollieren können:

- aktuellen skalaren Rezeptorkontakt,
- transiente lokale Rezeptorfolge,
- lokale Vorfeldproben,
- eigenen Vorzustand,
- verstrichene Dauer.

Eine behauptete gemeinsame Feldwirkung ist nur dann kausal gestützt, wenn sie
mit der betreffenden lokalen Rolle mitwandert und bei deren Ablation
verschwindet. Das rechtfertigt noch keine organische Entwicklung.

## Verbindliche Baselines

Mindestens zu führen sind:

- B0: Hold-State,
- B1: reine Rezeptorprojektion,
- B2: fester symmetrischer zustandsloser lokaler Leser,
- B3: einfacher fester zeitlicher Integrator beziehungsweise Nachhallträger.

B2 grenzt bloße lokale Algebra ab. B3 grenzt Geschichtsabhängigkeit ab, die
vollständig aus einer festen Zeitkonstante oder einem Leaky Integrator folgt.

## Zulässigkeit eines Kandidaten

Ein Kandidat darf nur in einen passiven Lauf aufgenommen werden, wenn:

- dieselbe Funktion an jedem Neuron und jeder Modalität verwendet wird,
- alle gelesenen Zustände offen im `MCMNeuronDrive` liegen,
- keine globale Statistik, Rangliste oder Normalisierung gelesen wird,
- keine Bedeutung, Klasse, Zielantwort oder Reward enthalten ist,
- keine versteckte mutable Variable außerhalb des Feldzustands existiert,
- seine Parameter und Begrenzungen vollständig offengelegt sind,
- er weder Topologie noch Memory oder Selbstregulation behauptet.

## Stopplinien

Der Kandidatenzweig wird gestoppt, wenn:

- grobe und feine Segmentierung verschiedene Endzustände erzeugen,
- technische Rezeptorrate die Wirkung bestimmt,
- fehlender Kontakt als Null oder letzter Kontakt behandelt wird,
- technische Iterationsreihenfolge das Ergebnis verändert,
- die Wirkung vollständig durch B2 oder B3 erklärt wird,
- eine neue Speichervariable, Schwelle, Lernrate oder Zielstruktur nötig wird,
- nur gewünschte Muster statt einer offenen lokalen Funktion entstehen.

Ein negativer Befund gibt keine komplexere Mechanik automatisch frei.

## Evidenz- und Interpretationsgrenze

Ein positiver passiver Befund dürfte höchstens tragen:

```text
lokale zeitteilungsinvariante Feldwirkung: Kandidat gestützt
```

Nicht getragen wären:

- entwickelte Feldtopologie,
- organisches Memory,
- Syntax oder semantische Resonanz,
- Reflexion oder Handlung,
- Feldintelligenz.

Feldintelligenz bleibt ausschließlich eine mögliche spätere rückblickende
Interpretation und ist weder Ziel noch Bewertungsachse dieser Methodik.

## Passiver Vergleichsrahmen

Der darstellungsoffene passive Vergleichsrahmen ist technisch umgesetzt. Er
erhält eine explizit übergebene Transition und denselben kontrollierten
asynchronen Verlauf in mehreren Segmentierungen. Der Rahmen selbst:

- darf keinen Standardkandidaten auswählen,
- darf keine Transition in die Runtime einbauen,
- darf keine Live-Quelle anschließen,
- darf keinen Befundtext automatisch erzeugen.

Kontaktfreie Beobachtungsgrenzen gelangen ohne Ersatzwert als leere
`ReceptorDistribution` bis in das gemeinsame Feld. Der vollständige lokale
Dockverlauf bleibt davon getrennt erhalten. Der Rahmen wählt keinen
Endpunktkontakt aus einer transienten Folge aus.

Jeder Zweig wird aus einem frischen Feld mit identischer Neuronenschicht und
identischer Dockanatomie aufgebaut. Grobe und feine Segmentierung werden
jeweils unabhängig wiederholt. Verglichen wird der physische lokale Endpunkt
aus `activation` und `afterimage`; technische Takt- und Beobachtungszähler
bleiben nur im Ablaufprotokoll. Damit wird eine feinere technische Beobachtung
nicht bereits als andere Feldentwicklung ausgegeben.

Die technische Nullkontrolle trägt: `hold_state_baseline` bleibt am physischen
Endpunkt zeitteilungsinvariant. Eine ausdrücklich nur für den Test eingesetzte
taktgebundene Gegenmechanik wird dagegen als segmentierungsabhängig erkannt.
Das wählt keine Feldgleichung aus und ist kein Forschungsbefund.

Die passive Rollenansicht ist inzwischen umgesetzt. Sie entfernt technische
Neuron-, Modalitäts-, Dock- und Clock-Identitäten und stellt ausschließlich
bereit:

```text
eigener schneller Vorzustand
aktueller skalarer Rezeptorkontakt oder Abwesenheit
lokale Vorfeldproben
verstrichene reale Dauer
transiente lokale Rezeptorfolge mit relativen Lesezeiten
```

Jede dieser Rollen kann einzeln entfernt werden. Vollansicht und alle fünf
Ablationen werden aus unabhängigen frischen Feldern aufgebaut. Der Rahmen
meldet lediglich, ob sich der grobe oder feine Endpunkt verändert; er deutet
diesen Unterschied nicht als Entwicklung.

Auch B0 bis B3 sind als explizite passive Gegenfunktionen angeschlossen:

- B0 bewahrt nur den schnellen Vorzustand.
- B1 projiziert nur einen tatsächlich vorhandenen aktuellen skalaren Kontakt.
  Sie wählt ausdrücklich keinen Kontakt aus der transienten Folge.
- B2 liest zustandslos den symmetrischen Mittelwert lokaler Aktivierungsproben.
- B3 trägt lokalen Nachhall mit einer beim Aufruf zwingend angegebenen festen
  Zeitkonstante. Sie besitzt keine Anpassung.

Keine Baseline wird automatisch gewählt oder in die Runtime eingebaut. Fehlt
eine von einer Baseline benötigte Rolle, bricht sie geschlossen ab, statt einen
Ersatzwert zu erfinden.

Rezeptorrate und Kausalität sind inzwischen als weitere passive
Kontrollachsen umgesetzt.

Die Ratenskontrolle akzeptiert nur zwei Verläufe mit identischer
Rezeptoranatomie und identischer reduzierter Quellenstütze. Der zweite Verlauf
darf ausschließlich zusätzliche technische Abschlüsse bereits vorhandener
Quellenzustände enthalten. Neue Werte, Geometrien oder Quellenspannen werden
abgewiesen. Verglichen werden grobe und feine Feldendpunkte. Hold bleibt in
dieser Kontrolle neutral; eine ausdrücklich technische Ereigniszählfunktion
wird als ratenabhängig erkannt.

Die Kausalitätskontrolle verlangt einen exakt identischen abgeschlossenen
Verlauf bis zu einer gemeinsamen groben und feinen Feldgrenze. Nur ein Zweig
enthält einen Kontakt, dessen Abschluss nach dieser Grenze liegt. Die
Feldpräfixe vor der Grenze müssen identisch bleiben. In der technischen
Gegenprobe bleiben sie identisch, während der spätere Endpunkt auf den danach
abgeschlossenen Kontakt reagieren kann.

Die Gleichzeitigkeit ist ebenfalls als passive Kontrollachse angeschlossen.
Sie verlangt mindestens zwei Modalitäten mit tatsächlich gemeinsamen
Abschlusszeiten. Derselbe Verlauf wird mit umgekehrter
Sequenzdeklarationsreihenfolge vollständig neu aufgebaut. Die bereits
vorhandene ungeordnete Abschlussgruppe und die atomare Neuronenschicht müssen
dann dieselben vollständigen groben und feinen Feldspuren erzeugen.

Diese Kontrolle fügt keine Modalitätspriorität und keine neue Sortierregel
hinzu. In der technischen Gegenprobe bleiben die Feldspuren bei zwei
gemeinsamen Abschlusszeiten exakt gleich. Verläufe ohne gemeinsamen
Abschlusszeitpunkt werden als ungeeignete Kontrolle abgewiesen.

Alle drei Ergebnisse sichern nur die Prüffähigkeit des Rahmens. Sie tragen
keinen Feldkandidaten und keine Aussage über organische Entwicklung.

Die Geometrie ist inzwischen als strenge passive Spiegelkontrolle umgesetzt.
Sie verlangt:

- gleiche Modalitäten, Ereigniszahlen sowie Quell- und Organismuszeiten,
- eine vollständige bijektive Spiegelzuordnung aller Rezeptorträger,
- dieselbe Zuordnung an den entsprechenden Dock-Neuronen,
- eine nichtidentische räumliche Spiegelung entlang genau einer Feldachse,
- gespiegelte lokale Sample-Offsets,
- gleiche korrespondierende Anfangszustände.

Erst danach werden grobe und feine Feldspuren positionsentsprechend
verglichen. Eine symmetrische lokale technische Gegenfunktion spiegelt in
beiden Segmentierungen vollständig mit. Eine absichtlich vorzeichenabhängige
Richtungsfunktion wird als nicht äquivariant erkannt. Auch daraus wird keine
Feldfunktion ausgewählt.

Die technische Pflichtachse Wiederaufnahme ist inzwischen ebenfalls
angeschlossen. Derselbe passive Verlauf wird einmal ohne Unterbrechung und
einmal über einen vollständigen Snapshot mit anschließender Wiederherstellung
geführt. Die Transition wird nach der Wiederherstellung bewusst frisch
erzeugt; nicht serialisierter Closure-, Cache- oder Leserzustand kann dadurch
nicht unbemerkt über die Grenze getragen werden.

Für eine zustandslose lokale Gegenfunktion bleiben grobe und feine Feldspuren
exakt gleich. Snapshot und wiederhergestellter Snapshot besitzen denselben
Digest, und alle Rezeptorabschlüsse werden in beiden Pfaden genau einmal
übergeben. Eine absichtlich zustandsbehaftete Closure-Gegenfunktion verletzt
die exakte Wiederaufnahme, obwohl ihre beiden jeweils unabhängig neu
aufgebauten Pfade reproduzierbar bleiben.

Damit sind die vorgesehenen technischen Kontrollachsen des passiven
Vergleichsrahmens vorhanden. Das gibt weder eine Feldgleichung noch eine
Runtimewirkung frei. Vor einem ersten Kandidaten ist nun gemeinsam zu prüfen,
ob der Rahmen den kleinsten offenen Funktionsmangel vollständig und ohne
Verschiebung des Untersuchungsziels abbildet.

## Freigabeabgleich vor einem Kandidaten

Der Funktionsmangel ist als fehlende Runtimeleistung beobachtbar, ohne eine
gewünschte Feldform vorzugeben:

```text
gleicher aktueller Weltkontakt
+ unterschiedliche lokale Vorfeldlage
-> heutige Rezeptorprojektion antwortet gleich

gleiche lokale Vorfeldlage
+ neuer Weltkontakt
-> heutiges Hold antwortet gleich
```

Damit fehlt der vorhandenen Runtime eine lokale Wirkung, bei der Weltkontakt
und bereits vorhandene Feldlage gleichzeitig kausal notwendig sind. Der
passive Rahmen kann diese beiden Notwendigkeiten durch getrennte Ablationen
prüfen und zugleich Zeitteilung, Rezeptorrate, Kausalität, Gleichzeitigkeit,
Geometrie und Wiederaufnahme kontrollieren.

Der Rahmen kann jedoch noch nicht entscheiden, ob ein positiver Kandidat eine
offene Feldfunktion oder nur eine anders formulierte feste Leser-, Diffusions-
oder Rekurrenzgleichung ist. B2 und B3 decken einen festen zustandslosen Leser
und einen festen Leaky-Nachhall ab. Eine allgemeine feste lokale Diffusion und
statische Rekurrenz sind noch keine gleichberechtigt formulierten
Zulassungsbaselines dieses ersten Vergleichs.

Der Rahmen ist daher **prüftechnisch bereit**, aber ein erster Kandidat ist
noch **nicht methodisch freigegeben**. Vor seiner Vorregistrierung fehlt eine
nicht-tautologische Zulassungsbedingung:

> Welche beobachtbare Leistung muss ein lokaler Übergang zusätzlich tragen,
> damit seine Verbindung von Weltkontakt und Vorfeldlage nicht vollständig
> als fester lokaler Filter, feste Diffusion oder statische Rekurrenz erklärt
> ist?

Bis diese Frage beantwortet ist, bleibt die Kandidatenwahl geschlossen. Es
wird weder nach Feldintelligenz gesucht noch eine organische Wirkung aus dem
bloßen Bestehen technischer Invarianzen abgeleitet.
