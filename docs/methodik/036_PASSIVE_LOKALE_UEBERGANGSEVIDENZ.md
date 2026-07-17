# Methodik 036: Passive lokale Übergangsevidenz

## 1. Status

Vorregistrierte passive Prüfung der in Architektur 021 bestimmten
Voraussetzung für spätere Verdichtung.

Es wird keine neue Feldtransition, Disposition, Beziehung oder Persistenz
eingeführt.

## 2. Forschungsfrage

Trägt die vorhandene lokale MCM-Feldwahrnehmung einen kontinuierlichen
Weltkontakt als zeitlich und räumlich zusammenhängende Übergangsevidenz?

Die bindende Frage lautet:

> Unterscheiden sich kontinuierliche und stark permutierte Folgen derselben
> lokalen Kontakte in den bereits vorhandenen kausal getrennten
> Neuroneneingängen, obwohl Energie, Positionshäufigkeit, Frameanzahl und
> unmittelbare Eigenüberlappung angeglichen sind?

## 3. Warum noch keine ganze Form verwendet wird

Eine mehrteilige Form kann zwischen aufeinanderfolgenden Ansichten an
denselben Positionen überlappen.

Dann könnten Unterschiede bereits durch stehen gebliebene aktive Zellen
erklärt werden:

```text
aktueller Kontakt an Position p
+ vorherige Eigenaktivierung an Position p
```

Methodik 036 verwendet deshalb zunächst genau einen aktiven lokalen Kontakt.
So wird die kleinste Anschlussfrage isoliert:

```text
vorherige Aktivität an benachbarter Position
→ aktueller Kontakt an neuer Position
```

Erst nach dieser Nullgrenze darf eine mehrteilige Feldform geprüft werden.

## 4. Unveränderte visuelle Runtime

Der Pfad lautet:

```text
synthetischer äußerer Frame
→ LocalChannelGridReceptor
→ VisualMCMInterface
→ visuelle MCM-Neuronenschicht
→ receptor_projection_baseline
→ passiver lokaler Observer
```

Vorregistrierte Geometrie:

```text
Quellauflösung:      14 x 6 Pixel
Rezeptorraster:      7 Spalten x 3 Zeilen
technische Kanäle:   3
aktive Zeile:        1
aktiver Kanal:       0
aktive Amplitude:    1.0
Feldzeit pro Frame:  genau 1 Tick
```

Jede Rasterzelle wird durch einen vollständigen `2 x 2`-Pixelblock
repräsentiert. Ein aktiver Pixelblock trägt im technischen Kanal `0` den Wert
`255`; alle übrigen Werte sind null.

## 5. Lokale Wahrnehmungsgeometrie

Unverändert verwendet werden:

```text
(-1, 0, 0)  obere lokale Probe
(+1, 0, 0)  untere lokale Probe
(0, -1, 0)  linke lokale Probe
(0, +1, 0)  rechte lokale Probe
```

Die Offsets sind feste Sensoranatomie. Sie sind keine gespeicherten Kanten und
keine entwickelte Beziehung.

## 6. Gemeinsame Kontaktmenge

Alle drei primären Folgen enthalten exakt einmal:

```text
(Zeile 1, Spalte 1, Kanal 0)
(Zeile 1, Spalte 2, Kanal 0)
(Zeile 1, Spalte 3, Kanal 0)
(Zeile 1, Spalte 4, Kanal 0)
(Zeile 1, Spalte 5, Kanal 0)
```

Damit sind zwischen den primären Folgen exakt gleich:

- fünf Frames,
- ein aktiver Kontakt pro Frame,
- Gesamtenergie `5.0`,
- Aktivitätshäufigkeit jeder Position,
- Kanalbelegung,
- räumliche Kontaktmenge.

Keine Sequenzkennung gelangt in die Runtime.

## 7. Primäre Folge C+

Die kontinuierliche Vorwärtsfolge lautet:

```text
1 → 2 → 3 → 4 → 5
```

Jeder neue Kontakt liegt genau eine lokale Spalte rechts vom vorherigen
Kontakt.

Vorregistrierte Erwartung:

```text
4 lokale Übergangsereignisse mit relativer Quelle (0, -1, 0)
0 lokale Übergangsereignisse mit relativer Quelle (0, +1, 0)
```

## 8. Zeitumkehr C-

Die vollständige zeitliche Umkehr lautet:

```text
5 → 4 → 3 → 2 → 1
```

Vorregistrierte Erwartung:

```text
0 lokale Übergangsereignisse mit relativer Quelle (0, -1, 0)
4 lokale Übergangsereignisse mit relativer Quelle (0, +1, 0)
```

Die ungerichtete Gesamtzahl lokaler Übergänge muss mit C+ kollidieren.

## 9. Permutierte Folge P

Die stark permutierte Folge lautet:

```text
1 → 4 → 2 → 5 → 3
```

Jeder aufeinanderfolgende Kontakt ist mindestens zwei Spalten vom vorherigen
Kontakt entfernt.

Vorregistrierte Erwartung:

```text
0 lokale Übergangsereignisse
```

P enthält dennoch dieselben fünf Kontakte wie C+ und C-.

## 10. Unterbrechungsablation C0

Zwischen jeden Kontakt von C+ wird ein vollständig kontaktloser Frame
eingefügt:

```text
1 → - → 2 → - → 3 → - → 4 → - → 5
```

Die Kontaktenergie bleibt `5.0`, die Folge besitzt jedoch neun Frames.

Da die Rezeptorprojektion jeden Leertakt exakt auf null setzt, wird erwartet:

```text
0 lokale Übergangsereignisse
```

Diese Ablation prüft, dass der Observer keine nicht vorhandene
Mehrschrittgeschichte ergänzt.

## 11. Stationäre Gegenkontrolle S

Die stationäre Folge lautet:

```text
3 → 3 → 3 → 3 → 3
```

Sie besitzt ebenfalls:

```text
5 Frames
Gesamtenergie 5.0
```

Erwartet werden:

```text
4 Eigenüberlappungen
0 lokale Nachbarübergänge
```

Damit bleiben Eigenfortsetzung und räumlicher Übergang getrennt.

## 12. Beobachtungsgrößen

Für jedes Neuron und jeden Takt darf der äußere Observer ausschließlich lesen:

- aktuellen `receptor_contact`,
- vorherige eigene `activation`,
- vorherige eigene `afterimage`,
- einzelne lokale Feldproben mit relativer Position,
- deren vorherige Aktivierung und Nachhall.

### Eigenüberlappung

```text
self(t,i) = current_contact(t,i) * prior_activation(t-1,i)
```

### Lokale Übergangsevidenz

Für jede vorhandene lokale Probe `j → i`:

```text
local(t,j→i)
= current_contact(t,i) * prior_activation(t-1,j)
```

Die Produkte sind ausschließlich äußere Messgrößen. Sie werden nicht in das
Neuron oder Feld zurückgegeben.

## 13. Vollständige Ereignisausgabe

Der Bericht hält keine Frames.

Für jedes positive lokale Übergangsereignis werden ausschließlich
festgehalten:

- Takt,
- technische Zielposition,
- relative Quellposition,
- aktueller Kontaktwert,
- vorheriger lokaler Aktivierungswert.

Es werden keine Richtungsklasse, Bewegung, Geschwindigkeit, Objektkennung oder
Formzugehörigkeit erzeugt.

## 14. Pflichtbaseline B0: Energie

Gemessen werden:

```text
Gesamtenergie
Energie pro Frame
Zahl aktiver Kontakte pro Frame
```

C+, C- und P müssen in B0 exakt kollidieren.

S kollidiert ebenfalls in Gesamtenergie und Energie pro Frame, besitzt aber
eine andere Positionshäufigkeit.

## 15. Pflichtbaseline B1: Positionshäufigkeit

Für jede technische Feldposition wird gezählt, in wie vielen Frames sie
aktuellen Kontakt trug.

C+, C- und P müssen als vollständige Häufigkeitsvektoren exakt kollidieren.

Der Vektor wird nur im Forschungsobserver gebildet und nicht zurückgeschrieben.

## 16. Pflichtbaseline B2: Eigenüberlappung

Gezählt wird die in Abschnitt 12 definierte unmittelbare
Eigenüberlappung.

Vorregistriert:

```text
C+ = 0
C- = 0
P  = 0
C0 = 0
S  = 4
```

Damit darf der Unterschied zwischen C+ und P nicht durch stehen gebliebene
Eigenaktivierung erklärt werden.

## 17. Pflichtbaseline B3: Feste lokale Nachbarschaft

B3 ist exakt die Summe der lokalen Übergangsprodukte über die vier
vorgegebenen räumlichen Offsets.

Vorregistriert:

```text
C+ = 4
C- = 4
P  = 0
C0 = 0
S  = 0
```

B3 ist eine feste Ein-Schritt-Überlappungsbaseline.

Wenn der passive MCM-Observer vollständig mit B3 kollidiert, ist nur gezeigt:

> Die vorhandene lokale Feldwahrnehmung stellt kausal getrennte
> Ein-Schritt-Nachbarschaftsevidenz verlustfrei bereit.

Das wäre noch keine MCM-spezifische Organisation.

## 18. Richtungsumkehr

Die gerichteten Ereigniszahlen von C+ und C- müssen unter

```text
(0, -1, 0) ↔ (0, +1, 0)
```

exakt ineinander übergehen.

Eine andere Asymmetrie wäre ein technischer Richtungs- oder
Reihenfolgefehler.

Die Richtung wird gemessen, aber nicht als Ziel, Befehl oder erwartete
Fortsetzung verwendet.

## 19. Räumliche Spiegelung

Der vollständige Versuch wird an der mittleren Spalte gespiegelt.

Nach kanonischer Rückabbildung müssen:

- aktuelle Kontakte,
- Eigenüberlappungen,
- lokale Ereignisse,
- relative horizontale Offsets

exakt kollidieren.

## 20. Kanalpermutation

Der aktive technische Kanal wird von `0` nach `2` verschoben.

Nach kanonischer Rückabbildung müssen alle Messungen exakt kollidieren.
Zwischen Kanälen existieren keine lokalen Proben.

## 21. Atomare Zeit

Ein Übergangsereignis darf ausschließlich verbinden:

```text
abgeschlossene Feldlage aus t-1
→ aktuellen Rezeptorkontakt in t
```

Unzulässig sind:

- aktuelle Kontakte desselben Takts als eigene Vergangenheit,
- Lesen eines noch nicht abgeschlossenen Nachbarzustands,
- mehr als ein Takt Rückgriff,
- Observerzustand als Eingabe.

## 22. Observer- und Ablaufkontrollen

Pflichtkontrollen:

1. Jeder Zweig beginnt mit einer frischen visuellen Schnittstelle.
2. Normale und umgekehrte Neuronenreihenfolge kollidieren.
3. Normale und umgekehrte Offsetreihenfolge kollidieren.
4. Normale und umgekehrte Zweigauswertung kollidieren.
5. Leerer und sammelnder Observer kollidieren.
6. Unabhängige Wiederholung erzeugt denselben Gesamtdigest.
7. Eingangsframes werden nicht verändert.
8. Der Ergebniszustand enthält keine Frames oder Pixel.
9. Ein absichtlich nicht benachbarter Kontakt erzeugt kein Ereignis.
10. Ein absichtlich benachbarter Kontakt erzeugt genau ein passendes Ereignis.

## 23. Vorhersage

Die stärkste Vorhersage lautet:

```text
Energie:
  C+ = C- = P = S = 5.0

Positionshäufigkeit:
  C+ = C- = P

Eigenüberlappung:
  C+ = C- = P = C0 = 0
  S = 4

lokale Übergangsevidenz:
  C+ = 4
  C- = 4
  P  = 0
  C0 = 0
  S  = 0
```

Der gesamte Unterschied zwischen C+ und P wird voraussichtlich exakt durch
die feste lokale B3-Ein-Schritt-Baseline erklärt.

## 24. Entscheidung

### Erwarteter positiver Verfügbarkeitsbefund

Wenn C+ und C- jeweils vier spiegelgerichtete Ereignisse tragen und P sowie C0
null bleiben, ist gezeigt:

> Die vorhandene lokale MCM-Wahrnehmung enthält die minimale kausale Evidenz
> kontinuierlicher benachbarter Weltteilnahme.

### Bindender Baseline-Gegenbefund

Wenn B3 alle Ereignisse exakt vorhersagt, ist nicht gezeigt:

- dass das Feld Übergänge verdichtet,
- dass Beziehungen entstehen,
- dass eine Disposition benötigt oder freigegeben ist,
- dass eine Form wiedererkannt wird.

### Unerwarteter Unterschied über B3 hinaus

Ein nicht durch B0 bis B3 erklärter Unterschied muss zuerst als möglicher
Observer-, Zeit-, Geometrie- oder Reihenfolgefehler behandelt werden.

## 25. Stärkstes Gegenargument

Der Versuch misst wahrscheinlich nur:

```text
aktueller Kontakt
x aktive feste Nachbarprobe aus dem vorherigen Takt
```

Das ist eine einfache lokale Koinzidenz und noch keine organische
Feldentwicklung.

Der Befund bleibt dennoch notwendig: Ohne diese lokal verfügbare
Kausalverbindung hätte eine spätere Disposition keine natürliche Evidenz,
verschiedene Weltkontakte miteinander zu verbinden.

## 26. Evidenzgrenze

```text
lokale Ein-Schritt-Übergangsevidenz: maximal E2
Verfügbarkeit im MCM-Neuroneneingang: maximal E2
Verdichtung über mehrere Übergänge:  E0
lokale Disposition:                  E0
entwickelte Feldform:                E0
Feldintelligenz:                     E0
```

## 27. Stopplinie

Nicht freigegeben sind:

- eine neue Zustandsrolle,
- Übergangszähler in der Runtime,
- adaptive Kante oder Gewicht,
- langsamere Spur,
- Ähnlichkeits- oder Fortsetzungsregel,
- Bewegungs- oder Richtungsklasse,
- Form-, Objekt- oder Ansichtskennung,
- Reward, Ziel oder Handlung,
- Rezeptorrückschreibung.

## 28. Bester nächster Schritt

Methodik 036 wird exakt passiv umgesetzt.

Nur wenn die vorregistrierten lokalen Ereignisse, Baselines, Ablationen und
Symmetrien vollständig tragen, darf anschließend gefragt werden, ob eine
endliche lokale Disposition mehrere solcher Übergänge integrieren könnte.
Auch ein positiver Lauf gibt diese Disposition nicht automatisch frei.
