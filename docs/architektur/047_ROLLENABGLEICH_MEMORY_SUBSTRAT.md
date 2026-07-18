# Rollenabgleich des vorhandenen Feldes mit dem Memory-Substratvertrag

## Status

Codegestützte technische Zustandsprüfung.

```text
technischer Rollenabgleich: abgeschlossen
organisches Memory:         E0
neue Mechanik:              nicht freigegeben
```

Geprüft wurden die tatsächlich implementierten Rollen:

```text
activation
afterimage
perception
lokale Feldprobe
technische Persistenz
```

Der Abgleich folgt der
[K6-Vorprüfung und offenen Memory-Substratfrage](046_K6_VORPRUEFUNG_UND_MEMORY_SUBSTRATFRAGE.md).

## Prüffrage

> Trägt eine vorhandene Zustandsrolle bereits den vollständigen funktionalen
> Lebenszyklus eines organischen Memory-Substrats, oder fehlt dafür
> nachweislich eine eigene kausal gelesene Zustandsrolle?

Nicht geprüft wird, wie eine fehlende Rolle digital dargestellt oder
aktualisiert werden soll.

## Implementierte Zustandsgrenze

Ein `MCMNeuron` enthält derzeit:

```text
technische Identität und Position
activation
afterimage
perception
```

`MCMNeuronOutput` darf nur `activation` und `afterimage` fortschreiben.

Die nächste `perception` wird von der Neuronenschicht atomar neu gebildet aus:

```text
aktuellem Rezeptorkontakt
+ activation der lokalen Nachbarn aus dem abgeschlossenen Vorfeld
+ afterimage der lokalen Nachbarn aus dem abgeschlossenen Vorfeld
```

Die neutrale Runtime integriert `activation` und `afterimage`. Der vollständige
Snapshot enthält die Neuronenschicht, Docks und die letzte abgeschlossene
Rezeptorverteilung. Ein zusätzlicher verborgener Runtimezustand ist nicht
vorhanden.

## Prüfkriterien

Jede Rolle wird gegen acht notwendige Funktionen geprüft:

1. Entstehung aus realer lokaler Feldwirkung;
2. spätere kausale Mitprägung der Feldentwicklung;
3. Wirkung über den schnellen Gegenwartszustand hinaus;
4. Abschwächung durch dieselbe unveränderte Naturbedingung;
5. vollständige funktionale Lösung ohne Reset;
6. erneute Prägbarkeit durch neue Weltgeschichte;
7. lokale und endliche Zugehörigkeit zum Organismuszustand;
8. technische Fortsetzbarkeit ohne externe Bedeutungswirkung.

## 1. `activation`

### Tatsächliche Rolle

`activation` ist der gegenwärtige schnelle Feldzustand eines MCM-Neurons.

Er:

- entsteht aus realem Rezeptorkontakt und lokaler Felddiffusion;
- wirkt kausal auf die folgende Aktivierung;
- wird von benachbarten Neuronen im nächsten abgeschlossenen Takt lokal
  wahrgenommen;
- gehört zum vollständigen Snapshot;
- bleibt im normierten Feldbereich.

### Grenze

`activation` trägt aktuellen Zustand, aber keine zusätzliche
Geschichtsdisposition. Unterschiedliche Weltgeschichten mit exakt gleicher
aktueller Aktivierung sind für die weitere neutrale Aktivierungsdynamik
gleich.

Bei kontaktfreier reiner Diffusion kann ein räumlich gleichförmiger Anteil
erhalten bleiben. Das ist ein fester Erhaltungsmodus der neutralen
Feldgleichung, keine lösbare geschichtsabhängige Organisation.

### Ergebnis

```text
gegenwärtiger kausaler Feldzustand: ja
langfristiges organisches Memory:   nein
```

## 2. `afterimage`

### Tatsächliche Rolle

`afterimage` ist eine schnelle leaky Zeitlage der Aktivierung.

Er:

- wird lokal aus vorherigem Nachhall und Aktivierungsverlauf gebildet;
- folgt einer festen offengelegten Zeitkonstante;
- gehört zum vollständigen Snapshot;
- wird in lokalen Feldproben sichtbar;
- kann unterschiedliche kurze Geschichten bei gleicher aktueller Aktivierung
  vorübergehend unterscheiden.

### Grenze

In der neutralen Runtime wirkt `afterimage` nicht zurück auf die
Aktivierungsentwicklung. Die Aktivierung wird unabhängig vom Nachhall
integriert; der Nachhall folgt der Aktivierung einseitig.

Seine Lösung ist durch eine feste Leaky-Dynamik erklärt. Damit ist er eine
notwendige schnelle Gegenwartsrolle und zugleich eine gebundene B1-Baseline,
aber kein organisches Memory.

### Ergebnis

```text
kurze geschichtsabhängige Gegenwart: ja
kausale langfristige Feldprägung:    nein
natürliche andere Wiederbindung:     nein
```

## 3. `perception`

### Tatsächliche Rolle

`perception` trennt:

```text
aktuellen lokalen Rezeptorkontakt
von
lokalen Feldproben des abgeschlossenen Vortakts
```

Sie gehört zum serialisierten Neuronenzustand und dokumentiert die
Wahrnehmungsgrundlage des aktuellen abgeschlossenen Takts.

### Grenze

Die nächste Wahrnehmung wird vollständig neu aus aktuellem Rezeptorkontakt und
dem abgeschlossenen lokalen Vorfeld aufgebaut. Die vorherige
`perception` wird von der neutralen Runtime nicht rekursiv als
Geschichtszustand gelesen.

Sie ist deshalb:

- eine kausal saubere gegenwärtige Eingangsrolle;
- kein wachsendes Wahrnehmungsarchiv;
- keine Disposition;
- keine Beziehung;
- kein organisches Memory.

Würde eine spätere Mechanik frühere `perception` rekursiv lesen, wäre dies
bereits eine neue Memory-Zustandsrolle. Diese Änderung darf nicht als bloße
Nutzung eines vorhandenen Feldes ausgegeben werden.

### Ergebnis

```text
gegenwärtige Feldwahrnehmung:          ja
eigenständige fortwirkende Geschichte: nein
```

## 4. Lokale Feldprobe

### Tatsächliche Rolle

Eine lokale Feldprobe ist ein `MCMFieldSample` aus dem abgeschlossenen
Vortakt. Sie enthält:

```text
relative Position
activation
afterimage
technische Quell- und Taktidentität
```

Sie wird für jedes Zielneuron aus der festen lokalen Anatomie neu erzeugt.

### Grenze

Die Probe besitzt keinen eigenen Fortsetzungszustand. Sie bezeichnet keine
gespeicherte Kante und wird nicht unabhängig von den aktuellen
Nachbarzuständen erhalten.

Ein fester Leser kann aus ihr lokale Ein-Takt-Wirkung erzeugen. Diese Wirkung
ist jedoch vollständig durch Leser und gegenwärtiges Vorfeld erklärt.

### Ergebnis

```text
lokale Feldschnittstelle: ja
Memory-Substrat:           nein
```

## 5. Technische Persistenz

### Tatsächliche Rolle

Der `SharedMCMFieldSnapshot` serialisiert den vollständigen bekannten
Runtimezustand. Wiederherstellung erzeugt exakt denselben Snapshot-Digest und
dieselbe technische Fortsetzung.

Persistiert werden:

- vollständige Neuronenschicht;
- `activation`, `afterimage` und aktuelle `perception`;
- feste Docks und Anatomie;
- letzte abgeschlossene Rezeptorverteilung.

### Grenze

Persistenz:

- entwickelt keinen Zustand;
- bewertet keine Information;
- bildet keine Beziehung;
- verändert keine spätere Feldfunktion;
- erzeugt keine Lösung oder Wiederbindung.

Sie kann ein später tatsächlich vorhandenes organisches Memory technisch
mittragen. Sie kann es nicht hervorbringen.

In der harten organischen Lesart beendet ein Ausschalten die kontinuierliche
Feldkausalität. Snapshot-Wiederherstellung ist eine technische Rekonstruktion
des letzten bekannten Zustands, kein Nachweis desselben ununterbrochenen
Lebensprozesses.

### Ergebnis

```text
vollständige technische Zustandserhaltung: ja
organisches Memory:                       nein
```

## Gesamtmatrix

| Rolle | Weltgetrieben | später kausal | über schnelle Lage hinaus | natürliche Lösung | andere Wiederbindung | Organismuszustand |
|---|---:|---:|---:|---:|---:|---:|
| `activation` | ja | ja | nein | nicht als Memory | nein | ja |
| `afterimage` | ja | nur für eigenen Nachhall | nein | feste Leaky-Lösung | nein | ja |
| `perception` | ja | nicht rekursiv | nein | wird ersetzt | nein | ja |
| lokale Feldprobe | ja | nur durch aktuellen Leser | nein | nicht anwendbar | nein | nein, abgeleitet |
| Persistenz | nein | nein | erhält nur Vorhandenes | nein | nein | technische Hülle |

Keine vorhandene Rolle trägt den vollständigen Memory-Lebenszyklus:

```text
Weltgeschichte
-> eigene fortwirkende Zustandsprägung
-> veränderte spätere Bildung
-> Abschwächung
-> vollständige funktionale Lösung
-> erneute andere Prägung
```

## Funktionale Notwendigkeit

Die heutige neutrale Runtime ist für ihre kausale Zukunft vollständig bestimmt
durch:

```text
activation
+ afterimage
+ feste Anatomie und Feldparameter
+ aktuelle abgeschlossene Rezeptorereignisse
+ verstrichene Organismuszeit
```

`perception` und lokale Feldproben werden daraus für den jeweiligen Takt
gebildet. Persistenz kopiert diesen Zustand nur exakt.

Werden die kausal gelesenen schnellen Rollen zweier Zweige angeglichen und
erhalten beide dieselbe spätere Weltgeschichte, kann die heutige Runtime
keinen unterschiedlichen erworbenen Feldweg erzeugen.

Daraus folgt:

> Für organisches Memory ist funktional eine zusätzliche kausal gelesene
> Zustandsrolle notwendig.

Das bedeutet ausdrücklich nicht:

- dass zwingend ein neues skalares Feld ergänzt werden muss;
- dass Kanten oder Gewichte benötigt werden;
- dass Topologie programmiert werden darf;
- dass `continuity`, `allocation` oder eine Ressourcenvariable zurückkehren;
- dass die Darstellung bereits bekannt ist.

Auch eine Erweiterung oder Umwidmung einer vorhandenen Datenstruktur wäre
funktional eine neue Zustandsrolle, sobald sie Geschichte rekursiv trägt und
die weitere Feldbildung verändert.

## Technische Absicherung

Der Rollenabgleich wurde gegen die vorhandenen Zustands- und Runtimeprüfungen
abgesichert:

```text
MCM-Neuron und Neuronenschicht
neutrale lokale Felddynamik
schneller Nachhall
technische Feldsitzung und Snapshot-Fortsetzung
aktuelle Geschichtsnull
verdichtete Feldform-Null
```

Ergebnis:

```text
53 Tests
53 bestanden
0 Fehler
```

Diese Tests belegen technische Rollen und Grenzen, nicht organisches Memory.

## Freigabegrenze

```text
vorhandene Rollen vollständig abgeglichen: ja
vollständiges Memory-Substrat vorhanden:    nein
zusätzliche kausale Zustandsrolle nötig:    funktional ja
Darstellung dieser Rolle festgelegt:        nein
Updategleichung festgelegt:                 nein
Runtime erweitert:                          nein
```

## Nächster Schritt

Der
[darstellungsoffene Memory-Substratvertrag](048_DARSTELLUNGSOFFENER_MEMORY_SUBSTRATVERTRAG.md)
ist inzwischen formuliert.

Dieser Vertrag darf nur festlegen:

- was die Rolle kausal leisten muss;
- was fest vorgegebene digitale Naturbedingung sein darf;
- was ausschließlich durch Weltgeschichte entstehen muss;
- wie vollständige Funktionslosigkeit und erneute Prägbarkeit beobachtbar
  werden;
- wie kontinuierlicher Feldbetrieb und technische Persistenz getrennt bleiben.

Er wählt keine Variable, Gleichung, Kante, Lernrate, Schwelle, Kapazität oder
Zielorganisation aus. Als Nächstes folgt ein enger MINI_DIO-Abgleich zur
Memory-Substratfunktion, nicht zur gewünschten Feldtopologie.
