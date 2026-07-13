# Methodik 004: Kontrollierter auditiver Weltkontakt

## 1. Status und Grenze

Diese Methodik eröffnet den ersten kontrollierten auditiven Weltkontakt. Sie
prüft, wie rohe Audiosamples in transparente lokale Frequenzzustände und
anschließend in lokale Ereignisse oder Spikes überführt werden können.

```text
kontrollierte Audiosamples
-> transparente auditive Rezeptorbank
-> kontinuierliche lokale Frequenzenergie
-> optionale lokale Ereignis- oder Spike-Baseline
```

Es werden keine Sprache, Wörter, Sprecher, Musikklassen, Emotionen oder
Bedeutungen erkannt. Zwischen Frequenzträgern existiert keine Verbindung.

## 2. Warum zunächst kontrolliertes Audio

Live-Mikrofonkontakt enthält Hardwareverstärkung, Raumakustik, Hintergrundlärm
und nicht exakt wiederholbare Ereignisse. Diese Faktoren würden Rezeptor- und
Spikeeffekte vermischen.

Der erste Lauf verwendet deshalb deterministisch erzeugte Audiosamples. Ein
Live-Mikrofonadapter wird erst nach bestandener Kausalitäts- und
Informationsprüfung separat untersucht.

## 3. Forschungsfragen

1. Erhält eine transparente lokale Frequenzprojektion Stille, Einzelton,
   Mehrklang, Amplitude und zeitliche Folge reproduzierbar?
2. Welche Information verlieren lokale Schwellenereignisse?
3. Trägt ein unabhängiger Integrate-and-Fire-Zustand eine notwendige Funktion,
   die kontinuierliche Energie und einfache Schwellenereignisse nicht tragen?
4. Rechtfertigt ein positiver Spikebefund bereits ein MCM-Neuron oder nur eine
   technische Ereigniscodierung?

## 4. Kontrollierte technische Welt

Der erste Proberaum verwendet:

```text
Abtastrate:        8000 Samples pro Sekunde
Fensterlänge:      80 Samples
Fensterdauer:      0.01 Sekunden
Frequenzsonden:    200 Hz, 400 Hz, 800 Hz
Samplebereich:     [-1, 1]
```

Die Frequenzen liegen exakt auf der diskreten Fensterauflösung. Dadurch kann
die technische Projektion ohne Fensterfunktions- oder Leakageoptimierung
isoliert geprüft werden.

Diese drei Kanäle sind keine endgültige Hörarchitektur. Sie sind transparente
Messsonden.

## 5. Rezeptorbaseline R0

Für jeden Frequenzkanal wird die Projektion auf Sinus und Kosinus berechnet:

```text
c_f = sum(x_n * cos(2*pi*f*n/fs))
s_f = sum(x_n * sin(2*pi*f*n/fs))

e_f = 2/N * sqrt(c_f^2 + s_f^2)
```

`e_f` ist eine nichtnegative lokale Amplitudensonde. Sie ist kein Lautheits-,
Tonhöhen- oder Bedeutungsurteil.

Die Transformation verwendet immer nur ein abgeschlossenes aktuelles Fenster.
Ihre unvermeidbare Latenz beträgt eine Fensterdauer.

## 6. Vergleichsbaselines

### B0: Kontinuierliche Frequenzlage

Der vollständige Vektor `e_f` bleibt erhalten. B0 besitzt die höchste
Information der hier geprüften Rezeptorausgänge.

### B1: Frequenzlage mit unabhängigem Leaky-Nachhall

Jeder Frequenzkanal verwendet ausschließlich den bereits geprüften B1-Nachhall
aus Methodik 002. B1 dient als zeitliche Vergleichsbasis.

### B2: Lokales Schwellenereignis

Für jeden Kanal und eine offene Schwelle `theta` gilt:

```text
+1: vorher unter theta, aktuell auf oder über theta
-1: vorher auf oder über theta, aktuell unter theta
 0: kein Schwellenwechsel
```

B2 markiert Beginn und Ende relativ zu einer Schwelle. Es speichert weder die
genaue Amplitude noch einen semantischen Ereignistyp.

### B3: Unabhängiger Integrate-and-Fire-Träger

Für jeden Kanal separat:

```text
d = exp(-dt / tau)
v* = d * v(t) + (1 - d) * e_f(t)

spike_count = floor(v* / theta)

v(t + dt) = v* - theta * spike_count
```

Es gibt:

- keine Verbindung zu anderen Kanälen,
- keine Gewichte,
- kein Lernen,
- keine Refraktärzeit,
- keine Hemmung,
- keine semantische Spikebedeutung.

Die Spikeanzahl statt eines binären Einzelspikes verhindert, dass bei kleiner
Schwelle mehrere innerhalb eines Fensters angesammelte Schwellenladungen
stillschweigend als Membranrest stehen bleiben. Die genaue zeitliche Lage
innerhalb des Fensters ist dennoch verloren.

B3 ist eine technische Baseline, kein freigegebenes MCM-Neuron.

## 7. Offene Parameterfamilien

```text
Ereignis- und Feuerschwelle theta in {0.2, 0.5, 0.8}
Integrationszeit tau             in {0.01, 0.05, 0.2}
dt                               = 0.01
```

Kein Wert wird optimiert oder als endgültige Konstante übernommen.

## 8. Auditive Kontaktfamilien

Geprüft werden:

- Stille,
- Einzelton je Frequenzsonde,
- gleicher Ton mit mehreren Amplituden,
- zwei gleichzeitige Töne,
- Tonbeginn, anhaltender Ton und Tonende,
- Impulsfolge mit Pause,
- regelmäßige und unregelmäßige Pulsabstände,
- aufsteigende und absteigende Frequenzfolge,
- gleiche aktuelle Frequenzlage nach verschiedener Vorgeschichte,
- verschiedene Amplituden mit identischem B2-Ereignis,
- verschiedene Energieverläufe mit identischer B3-Spikefolge.

## 9. Prüfbare Funktionen

### F1: Stille und Nullstabilität

Stille erzeugt in R0 und B0 exakt null. B2 und B3 dürfen ohne frühere Ladung
keine Ereignisse erzeugen.

### F2: Frequenzlokalität

Ein Ton auf einer Sondenfrequenz erscheint primär in genau diesem Kanal. Andere
Kanäle dürfen nicht durch technische Berechnungsreihenfolge beeinflusst werden.

### F3: Mehrklangerhalt

Zwei gleichzeitig vorhandene Sondenfrequenzen bleiben als zwei lokale
Energieanteile sichtbar.

### F4: Amplitudenskalierung

R0/B0 skalieren innerhalb der Samplegrenze linear mit der Eingangsamplitude.

### F5: Beginn und Ende

B2 erzeugt bei Schwellenübertritt ein positives und beim Unterschreiten ein
negatives lokales Ereignis.

### F6: Anhaltender Kontakt

B2 erzeugt während unveränderter Überschwelligkeit kein neues Ereignis. B3
darf durch Integration wiederholt feuern.

### F7: Lokale Unabhängigkeit

Energie oder Spike in einem Frequenzkanal verändert keinen anderen Kanal.

### F8: Informationsgrenze

Es werden gezielt verschiedene kontinuierliche Energieverläufe gesucht, die
dieselbe B2- oder B3-Ausgabe erzeugen. Deterministische Spikecodierung darf
nicht als Informationsgewinn ausgegeben werden.

## 10. Pflichtkontrollen

- Phasenverschiebung desselben Tons,
- Umkehr der Kanalberechnungsreihenfolge,
- vollständiger Reset,
- mehrere Amplituden,
- alle Schwellen und Integrationszeiten,
- Stille vor und nach Kontakt,
- identische Wiederholung,
- ungültige Samples und Parameter,
- Observer an und aus durch exakten Ergebnisvergleich.

## 11. Erwartung

Erwartet wird:

- R0 trennt die drei kontrollierten Frequenzsonden.
- B0 erhält mehr Amplitudeninformation als B2 und B3.
- B2 trägt Beginn und Ende, verliert aber subthreshold und genaue Amplitude.
- B3 trägt wiederholbare lokale Spikezeiten bei anhaltender Energie.
- Schwelle und Integrationszeit bestimmen die Spikefolge stark.
- Verschiedene Audiosignale können in B2 und B3 kollidieren.
- Kein Spike erzeugt eine Wirkung in einem anderen Frequenzkanal.

## 12. Entscheidungskriterien

### D1: Spikecodierung ist nur technische Umformung

Wenn B2/B3 keine Information hinzufügen und ihre Unterschiede vollständig aus
Schwelle und Integrationsgleichung folgen, werden sie nur als optionale
Ereignisbaselines geführt.

Dann sind weder MCM-Neuron noch spikendes Feld nachgewiesen.

### D2: Enger funktionaler Nutzen

Ein enger Nutzen kann vorliegen, wenn Spikes zeitliche Ereignisse bei endlicher
lokaler Aktivität reproduzierbar darstellen. Auch dann bleibt die
Netzwerkfreigabe geschlossen.

### D3: Scheitern

Wenn Frequenzlokalität, Zeitkausalität, Reset oder Parameteroffenheit nicht
tragen, wird zuerst die Rezeptor- oder Spikebaseline korrigiert. Es wird keine
komplexere Neuronenmechanik ergänzt.

## 13. Stoppregeln

Keine Verbindung zwischen Spike-Trägern wird eingeführt, wenn:

- Spikes lediglich kontinuierliche Energie quantisieren,
- eine gewünschte Rhythmus- oder Klangklasse extern benannt werden müsste,
- Schwellen auf bestimmte Testtöne optimiert werden,
- reichere Aktivitätsbilder der einzige Vorteil sind,
- analoge Energie und einfacher Nachhall dieselbe Funktion tragen.

## 14. Evidenzgrenze

Ein positiver Lauf kann E1 für die kontrollierte auditive Rezeptor- und
Spikebaseline tragen.

Er zeigt kein Hören im semantischen Sinn, kein MCM-Neuron, kein spikendes
MCM-Feld, keine Syntax und keine Feldintelligenz.

## 15. Bester nächster Schritt

Nach dieser Vorregistrierung werden R0 und B0 bis B3 rein passiv implementiert.
Erst die Auswertung entscheidet, ob lokale Spikeereignisse zusätzlich zur
kontinuierlichen Feldlage technisch sinnvoll bleiben. Ein Live-Mikrofon und
Trägerverbindungen bleiben gesperrt.
