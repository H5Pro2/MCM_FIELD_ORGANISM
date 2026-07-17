# Optionale periodische MCM-Sensoranatomie

> **Historischer Forschungsvertrag:** Die periodische Anatomie bleibt als
> geprüfte Baseline erhalten. Sie definiert nicht die Geometrie des aktuellen
> gemeinsamen MCM-Feldes.

## 1. Status

Architekturvertrag mit technisch geprüfter optionaler Runtime-Unterstützung.
Die vorhandene `MCMNeuronLayer` bleibt ohne expliziten Achsenvertrag offen.
Eine periodische lokale Abtastung ist nur unter den hier festgelegten
Bedingungen zulässig.

## 2. Anlass

Die simulierte Referenzwelt aus Architektur 018 besitzt sieben Positionen auf
einem Ring. Befund 034 zeigt:

```text
Weltposition 6 und Weltposition 0 sind lokal benachbart
+ Kontaktwerte erreichen die richtigen MCM-Träger
+ die lineare MCM-Schicht erhält diese Nachbarschaft nicht
```

Der fehlende Randkontakt ist kein Verlust des Aktivierungswertes. Er ist eine
offene Frage der technischen Sensoranatomie.

## 3. Grundsatz

Periodizität darf nur eine bereits offen dokumentierte Rezeptorgeometrie
abbilden. Sie darf keine Beziehung aus Feldaktivität ableiten und keine
entwickelte Topologie vorgeben.

```text
periodische Sensoranatomie = technische Probenadressierung
periodische Sensoranatomie != gespeicherte Kante
periodische Sensoranatomie != gelernte Beziehung
periodische Sensoranatomie != Feldregel
```

Für jede räumliche Achse muss ausdrücklich genau eine Randart gelten:

- `open`: Eine Probe außerhalb der Achse fehlt.
- `periodic`: Eine Probe außerhalb der Achse wird auf derselben Achse
  zyklisch adressiert.

Eine stillschweigende Standardperiodizität ist unzulässig. Ohne expliziten
Vertrag bleibt eine Achse offen.

## 4. Zulässige feste Rollen

Ein späterer technischer Geometrievertrag darf ausschließlich tragen:

- stabile Geometrieidentität,
- endliche Achsengrößen,
- feste technische Neuronenpositionen,
- pro Achse die Randart `open` oder `periodic`,
- symmetrische relative Proben-Offsets,
- eine unveränderliche Zuordnung von Rezeptorträgern zu MCM-Neuronen,
- eine gemeinsame abgeschlossene Feldzeit.

Diese Rollen gehören zur Sensoranatomie. Sie enthalten keine Bedeutung,
Wichtigkeit, Aktivitätsstärke oder Entwicklungsentscheidung.

## 5. Periodische Adressierung

Für eine periodische Achse der endlichen Größe `L` wäre ausschließlich die
technische Quellposition definiert:

```text
source = (target + offset) modulo L
```

Für die sieben Positionen der Referenzwelt folgt daraus:

```text
target 0, offset -1 -> source 6
target 6, offset +1 -> source 0
```

Die Modulo-Abbildung darf nur beim Erzeugen einer lokalen Feldprobe verwendet
werden. Sie verändert weder Aktivierung noch Nachhall und wird nicht im
Neuron als Nachbarliste gespeichert.

## 6. Keine Kanten und keine Verdrahtung

Auch bei periodischer Adressierung entsteht jede lokale Probe erneut aus der
vollständigen abgeschlossenen Schichtlage.

Das Neuron speichert weiterhin nicht:

- welche anderen Neuronen es zuletzt wahrgenommen hat,
- eine Kante zum Randpartner,
- ein Gewicht oder eine Kopplungsstärke,
- Nutzungszahl, Kontinuität oder Beziehungsgeschichte,
- Richtungsvorliebe oder Gewinnerrolle.

Eine Feldprobe bleibt Wahrnehmung und ist keine Beziehung.

## 7. Symmetrie und Mehrdeutigkeit

Jeder relative Offset benötigt weiterhin sein Gegenstück. Die technische
Anatomie darf dadurch keine versteckte Vorzugsrichtung erzeugen.

Wenn verschiedene Offsets an einer kleinen periodischen Achse auf denselben
Quellträger fallen, ist die Geometrie für diesen Probenvertrag mehrdeutig. Sie
muss abgelehnt werden, statt Proben still zusammenzufassen, doppelt zu zählen
oder mit Gewichten zu unterscheiden.

Für den Ring mit sieben Positionen und den Offsets `-1` und `+1` tritt diese
Mehrdeutigkeit nicht auf.

## 8. Trennung von technischer und entwickelter Topologie

Die periodische Randart beantwortet nur:

```text
Welche lokalen Weltkontakte kann ein MCM-Neuron technisch wahrnehmen?
```

Sie beantwortet nicht:

```text
Welche Feldbereiche entwickeln eine Beziehung?
Welche Beziehung stabilisiert oder löst sich?
Welche Feldlage trägt später eine Funktion?
```

Später entstehende Feldbeziehungen müssen deshalb getrennt von der
Sensorgeometrie beobachtet und geprüft werden. Eine Übereinstimmung mit dem
technischen Ring wäre noch kein Entwicklungsbefund.

## 9. Pflichtkontrollen vor einer Implementierung

Eine spätere passive Methodik muss offene und periodische Anatomie aus
demselben eingefrorenen Feldzustand vergleichen.

Sie muss mindestens prüfen:

1. Innere Positionen erhalten in beiden Anatomien exakt dieselben Proben.
2. Nur die Randpositionen erhalten in der periodischen Anatomie zusätzliche
   korrekt adressierte Proben.
3. Jeder periodische Randkontakt besitzt den symmetrischen Gegenkontakt.
4. Zyklische Rotation der Trägeridentitäten rotiert das Probenergebnis mit.
5. Umkehrung der technischen Ringrichtung erzeugt keinen Vorzug.
6. Observer und technische Iterationsreihenfolge bleiben neutral.
7. Rezeptorkontakt, Aktivierung und Nachhall werden nicht verändert.
8. `hold_state_baseline` und `receptor_projection_baseline` erzeugen trotz
   verschiedener Randproben weiterhin ihre exakt erwarteten Ausgaben.
9. Ursache, `delta`, Effort und Provenienz bleiben außerhalb der Feldproben.
10. Reset hinterlässt keine periodische Beziehung oder Restspur.

## 10. Erwartete minimale Differenz

Für den sieben Träger breiten Ring mit den Offsets `-1` und `+1` darf sich der
Vergleich nur hier unterscheiden:

```text
offene Anatomie:
Neuron 0 sieht lokal nur Neuron 1
Neuron 6 sieht lokal nur Neuron 5

periodische Anatomie:
Neuron 0 sieht Neuron 6 und Neuron 1
Neuron 6 sieht Neuron 5 und Neuron 0
```

Jede weitere Differenz wäre ein Implementierungsfehler oder eine zusätzliche,
nicht freigegebene Mechanik.

## 11. Nicht freigegeben

- Periodizität ohne expliziten `PeriodicSamplingAxis`,
- Anwendung lokaler Proben auf Aktivierung oder Nachhall,
- feste oder adaptive Feldkopplung,
- gespeicherte Nachbarn, Kanten oder Beziehungen,
- Verbindung eines Randkontakts mit einem Effektorwert,
- Reward, Ziel, Auswahl oder Handlung,
- Interpretation der Ringanatomie als organische Entwicklung,
- Übertragung periodischer Ränder auf Audio, Video oder spätere Sensoren ohne
  eigenen sensorspezifischen Geometrievertrag.

## 12. Evidenzgrenze

Dieser Vertrag trägt nur:

```text
begründete Zulässigkeit einer optionalen technischen Randart: E1
periodische lokale Probenbildung in der Runtime:              E1
kausale Wirkung periodischer Feldproben:                      E0
entwickelte Topologie:                                        E0
Eigenwirkung und Handlung:                                    E0
Feldintelligenz:                                              E0
```

## 13. Stärkstes Gegenargument

Die periodische Anatomie übernimmt die Ringstruktur vollständig aus einer vom
Entwickler vorgegebenen Simulationswelt. Sie kann deshalb niemals selbst als
Emergenz oder organisch entstandene Feldordnung gelten.

Ihr einziger möglicher Nutzen ist, den sensorischen Weltkontakt lokal
vollständig abzubilden, bevor geprüft wird, ob dem Feld darüber hinaus eine
eigene Funktion fehlt.

## 14. Bester nächster Schritt

Befund 036 bestätigt die optionale technische Schichteigenschaft. Als Nächstes
wird ihre Aktivierung ausschließlich für den expliziten simulierten Ringpfad
vorregistriert.

Eine Wirkung lokaler Proben auf Aktivierung, Nachhall oder Effektor bleibt
weiterhin geschlossen.
