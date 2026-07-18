# Befund 004: Kontrollierter auditiver Weltkontakt

## 1. Bezug

Ausgeführt wurde
[Methodik 004](../methodik/004_KONTROLLIERTER_AUDITIVER_WELTKONTAKT.md).

Der Versuch prüfte deterministische Audiosamples, eine transparente lokale
Frequenzprojektion, Schwellenereignisse und unabhängige
Integrate-and-Fire-Baselines.

## 2. Kontrollierte Welt

```text
Abtastrate:      8000 Samples pro Sekunde
Fenster:         80 Samples / 0.01 Sekunden
Frequenzsonden:  200 Hz, 400 Hz, 800 Hz
Samplebereich:   [-1, 1]
```

Die Sondenfrequenzen liegen exakt auf der diskreten Fensterauflösung. Dieser
Aufbau isoliert die Mechanik, bildet aber keine reale Hörwelt ab.

## 3. Implementierte Baselines

- **R0/B0:** kontinuierliche Frequenzamplitude,
- **B1:** vorhandener unabhängiger Leaky-Nachhall als Referenz,
- **B2:** lokale signierte Schwellenereignisse für Beginn und Ende,
- **B3:** unabhängige Integrate-and-Fire-Ladung mit Spikeanzahl pro Fenster.

Nicht implementiert wurden:

- Live-Mikrofon,
- Frequenzträgerverbindungen,
- Netzwerkgewichte,
- Lernen oder Anpassung,
- Sprach-, Musik- oder Ereigniserkennung,
- ein gemeinsamer MCM-Strang.

## 4. Methodische Korrektur vor dem gültigen Lauf

Der erste fokussierte Lauf zeigte, dass die vorregistrierte binäre
Ein-Spike-Formel bei niedriger Schwelle mehr als eine Schwellenladung in einem
Fenster ansammeln kann. Ein einmaliger Schwellenabzug ließ dann einen
Membranrest oberhalb der Schwelle zurück.

Die Baseline wurde deshalb offen korrigiert:

```text
spike_count = floor(v* / theta)
v(t + dt) = v* - theta * spike_count
```

Damit bleibt der Rest immer kleiner als die Schwelle. Die Korrektur führt keine
neue Zustandsrolle und keine Kopplung ein. Sie macht jedoch sichtbar, dass die
genaue Spikezeit innerhalb eines 10-ms-Fensters nicht aufgelöst wird.

Erst danach wurde der vollständige fokussierte Lauf gewertet.

## 5. Ausführung

```text
python -m unittest -v tests.test_controlled_auditory_contact
```

Gültiges Ergebnis:

```text
25 Tests
25 bestanden
0 Fehler
0 Fehlschläge
```

## 6. Rezeptorbefunde

### Stille

Stille erzeugt exakt den Nullvektor. Ohne frühere Ladung entstehen weder
Schwellenereignisse noch Spikes.

### Frequenzlokalität

Jeder kontrollierte Einzelton erscheint mit seiner vorgegebenen Amplitude im
zugehörigen Frequenzkanal. Die beiden anderen Sonden bleiben innerhalb reiner
Gleitkommatoleranz null.

Der Befund ist durch die exakt aufgelösten Prüffrequenzen begünstigt. Er darf
nicht auf beliebige reale Klänge übertragen werden.

### Phase und Amplitude

Eine Phasenverschiebung verändert die gemessene Frequenzamplitude nicht.
Innerhalb der Samplegrenze skaliert R0 linear mit der Tonamplitude.

### Mehrklang

Zwei gleichzeitig eingespeiste Sondenfrequenzen bleiben als zwei getrennte
lokale Energieanteile erhalten. Es findet keine semantische oder globale
Fusion statt.

### Reihenfolgeneutralität

Alle sechs Berechnungsreihenfolgen der drei Frequenzsonden ergeben nach
Rückordnung dieselben Werte.

## 7. Schwellenereignisse B2

B2 trägt:

- positiven Schwellenübertritt bei Tonbeginn,
- negativen Schwellenübertritt bei Tonende,
- Zeitposition regelmäßiger und unregelmäßiger Pulse,
- Unterschied auf- und absteigender Frequenzfolgen.

B2 verliert:

- jede subthreshold Energie,
- genaue überschwellige Amplitude,
- Veränderung innerhalb eines gleichbleibenden Schwellenbandes.

Verschiedene Amplituden erzeugen absichtlich dasselbe Ereignis. Die Schwelle
bestimmt, ob ein Kontakt überhaupt sichtbar wird.

## 8. Integrate-and-Fire B3

B3 trägt:

- lokale Ladungsintegration,
- Relaxation bei Stille,
- wiederholte Spikezahlen bei anhaltender Energie,
- deterministische Wiederholung nach Reset,
- vollständige Unabhängigkeit der Frequenzkanäle.

Die Kombination aus `theta` und `tau` verändert die Spikefolge stark. Über die
geprüften Werte entstanden mehrere verschiedene Folgen aus derselben
Energiegeschichte.

Verschiedene kontinuierliche Energiegeschichten wurden außerdem auf identische
Spikefolgen abgebildet. Die Spikeausgabe enthält somit weniger Information als
die kontinuierliche Frequenzlage.

## 9. B1-Gegenreferenz

Bei identischer aktueller Frequenzlage bewahrt der unabhängige Leaky-Nachhall
unterschiedliche unmittelbare Frequenzvorgeschichten. Dafür ist keine
Spikecodierung erforderlich.

## 10. Zentrale Entscheidung

Spikes besitzen einen engen technischen Nutzen:

```text
kontinuierliche Energie
-> endliche lokale Zeitereignisse
```

Sie erzeugen jedoch keine neue Weltinformation. Alle Spikeunterschiede folgen
aus Frequenzprojektion, Schwelle, Integrationszeit und Fensterung.

Die bindende Aussage lautet:

```text
lokale auditive Spikeereignisse sind möglich
!= MCM-Neuron nachgewiesen
!= spikendes MCM-Feld nachgewiesen
```

## 11. Kritische Grenzen

- Die drei Frequenzkanäle sind fest vorgegeben.
- Das 10-ms-Fenster legt Zeitauflösung und Latenz fest.
- Die kontrollierten Töne passen exakt zur Frequenzauflösung.
- B2 und B3 sind schwellenabhängig.
- B3 löst mehrere Spikes innerhalb eines Fensters nur als Anzahl auf.
- Synthetische Töne enthalten keine Raumakustik, Geräuschbreite oder
  Mikrofoneigenschaften.
- Es gibt keine Wirkung zwischen Frequenzträgern.

## 12. Evidenz

**E1 für die kontrollierte auditive Rezeptor- und Spikebaseline.**

Weiterhin **E0** für:

- reales auditives MCM-Feld,
- MCM-Neuron,
- spikende Trägerkopplung,
- Live-Weltteilnahme,
- gemeinsamen MCM-Strang,
- Lernen und Feldintelligenz.

## 13. Architekturentscheidung

Die kontinuierliche Frequenzlage bleibt die vollständige technische
Gegenreferenz. B2 und B3 bleiben passive Ereignisbaselines und werden noch
nicht als zusätzliche Zustandsrollen in die MCM-Schnittstelle aufgenommen.

Es werden keine Verbindungen zwischen Frequenzträgern freigegeben.

## 14. Bester nächster Schritt

Der nächste sinnvolle Versuch ist ein streng passiver Live-Mikrofonadapter, der
dieselben kontinuierlichen Frequenzzustände erzeugt und B2/B3 nur parallel im
Observer vergleicht.

Vor Mikrofonzugriff müssen Aufnahmegerät, Datenschutzgrenze, Rohdatenhaltung
und technische Audioabhängigkeit ausdrücklich festgelegt werden. Es wird noch
kein dauerhaft mithörendes System und kein spikendes Netzwerk freigegeben.
