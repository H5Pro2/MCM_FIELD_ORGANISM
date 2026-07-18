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

Noch offen sind die technischen Pflichtachsen Rezeptorrate, Kausalität,
Gleichzeitigkeit, Geometrie und Wiederaufnahme innerhalb desselben Rahmens.
Erst wenn auch diese Gegenprüfungen stehen, kann über einen ersten kleinen
Kandidaten gesprochen werden.
