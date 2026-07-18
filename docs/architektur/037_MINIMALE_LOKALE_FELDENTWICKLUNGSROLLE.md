# Minimale lokale Feldentwicklungsrolle

## Status

Verbindliche Informations- und Zulässigkeitsgrenze auf `E0 / CONTRACT_ONLY`.

Es wird kein neuer Entwicklungszustand eingeführt. Der bestehende
`MCMNeuronDrive` ist bereits die kleinste lokale Grenze, an der eine spätere
Feldentwicklung untersucht werden kann.

## Vier getrennte lokale Rollen

Ein Feldneuron kann während eines atomaren Vorschlags ausschließlich erhalten:

1. seinen eigenen vollständig abgeschlossenen Vorzustand,
2. seine aktuelle lokale Feldwahrnehmung aus dem gemeinsamen Vorzustand,
3. die real verstrichene Organismusdauer,
4. optional den transienten Verlauf seines eigenen Rezeptordocks.

```text
MCMNeuronDrive
= previous
+ perception
+ step_time
+ transient_receptor_input oder Abwesenheit
```

Die Verfügbarkeit einer Rolle verpflichtet eine spätere Transition nicht,
diese Rolle zu verwenden. Insbesondere ist der eigene Vorzustand noch keine
freigegebene Selbstverstärkung und der transiente Verlauf noch keine
freigegebene Integration.

## Lokalitätsgrenze

Ein Neuron erhält nicht:

- die vollständige gemeinsame Schicht,
- globale Aktivitätssummen oder Modalitätsraten,
- fremde vollständige Dockverläufe,
- einen Gewinner oder eine Rangliste,
- Semantik, Bezeichnung, Reward oder Zielzustand,
- künftige Rezeptorzustände,
- einen schreibenden Observer,
- eine gespeicherte Beziehung oder Topologie.

Lokale Feldproben benachbarter Neuronen bleiben zulässig, weil sie bereits aus
dem vollständig abgeschlossenen gemeinsamen Vorzustand erzeugt werden. Sie
sind Wahrnehmung und keine gespeicherte Kante.

## Ausgangsgrenze

Die heutige technische Transition darf ausschließlich einen neuen begrenzten
Wert für Aktivierung und Nachhall vorschlagen. Identität, Position, Geometrie,
Dockanatomie und Wahrnehmungsbildung bleiben unverändert.

Diese Ausgangsgrenze kann schnelle Feldreaktion untersuchen. Sie kann noch
keine entwickelte Topologie, Beziehung, Semantik oder organisches Memory
erzeugen. Dafür fehlt bewusst jeder zusätzliche persistente Zustand.

## Pflichtmerkmale eines späteren Kandidaten

Ein erster Übergangskandidat muss mindestens:

- dieselbe lokale Funktion an allen Neuronen verwenden,
- unabhängig von technischer Neuronen- und Sampleiteration sein,
- Nullkontakt von Rezeptorabwesenheit trennen,
- keinen Zustand vor dessen Abschluss lesen,
- ohne globale Auswahl oder Modalitätsgewicht auskommen,
- bei gröberer und feinerer Beobachtungsunterteilung denselben kausalen
  Endzustand tragen,
- vollständig durch seine offen gelegten lokalen Eingangsrollen erklärbar
  bleiben.

Zeitteilungsinvarianz ist dabei keine gewünschte Zusatzqualität, sondern eine
notwendige Bedingung. Ohne sie würde der technische Scheduler die Stärke oder
Entwicklung des Feldes bestimmen.

## Baselines und Statikgrenze

`hold_state_baseline` und `receptor_projection_baseline` bleiben reine
Kontrollen. Auch ein weiterer fest programmierter lokaler Leser wäre zunächst
nur eine Baseline.

Die archivierten synthetischen Vorarbeiten zeigen bereits, dass feste
symmetrische Leser lokale Ein-Schritt-Wirkung erzeugen können. Ihre Antwort
folgt jedoch vollständig aus der vorgegebenen Leserform. Das ist keine
entwickelte Feldorganisation.

## Nicht freigegeben

- konkrete Aktivierungs- oder Nachhallgleichung,
- feste Zerfallsrate, Schwelle oder Spikepflicht,
- selbstverstärkende Rückkopplung,
- Lernen, Plastizität oder adaptive Parameter,
- Beziehung, Ressource oder Topologiewachstum,
- semantische Verdichtung oder Resonanz zur Sprache,
- Live-Runtime und Selbstregulation.

## Konsequenz

Die Informationsarchitektur für einen lokalen Kandidaten ist vollständig. Die
verbindliche
[Zulässigkeitsmethodik der ersten lokalen Felddynamik](038_ZULAESSIGKEITSMETHODIK_ERSTE_LOKALE_FELDDYNAMIK.md)
grenzt den ersten Funktionsmangel unter realer Dauer und asynchronem lokalem
Dockverlauf ein. Sie wählt noch keine Feldgleichung aus.
