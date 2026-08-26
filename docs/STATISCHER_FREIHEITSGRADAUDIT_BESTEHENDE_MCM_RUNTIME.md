# Statischer Freiheitsgradaudit der bestehenden MCM-Runtime

## Status

```text
Auditart:                         statisch / codebezogen
produktive lokale Dynamikwerte:   activation, afterimage
rueckwirkender schneller Wert:    activation
afterimage -> activation:         nein
langsamer konstitutiver Zustand:  nicht vorhanden
kleinste Schemaerweiterung:       ein lokaler skalarer Zustand
konkrete Gleichung:               nicht zugelassen
Code- oder Runtime-Aenderung:      nein
```

## Prueffrage

Der Korrekturvertrag erlaubt eine inhaltsfreie feste lokale Naturform. Vor
einer neuen Mechanikhypothese ist daher am ausgefuehrten Code zu klaeren:

1. Welche lokalen Zustaende besitzt die heutige MCM-Runtime tatsaechlich?
2. Welche davon entwickeln die spaetere schnelle Feldtrajektorie kausal mit?
3. Welche gesuchte Feldfunktion ist mit diesem Zustand prinzipiell nicht
   darstellbar?
4. Was ist die kleinste zusaetzliche Zustandsdimension, die diese Luecke
   ueberhaupt adressieren koennte?

Der Audit fuehrt keinen Code und keinen Test aus.

## Untersuchte produktive Kernquellen

- `mcm_field_organism/mcm_neuron.py`
- `mcm_field_organism/mcm_neuron_layer.py`
- `mcm_field_organism/shared_mcm_field.py`
- `mcm_field_organism/neutral_local_field_substrate.py`
- `mcm_field_organism/neutral_asynchronous_field_runtime.py`
- `mcm_field_organism/neutral_field_session.py`
- `mcm_field_organism/field_step_time.py`

Zur Abgrenzung wurden ausserdem statisch gelesen:

- `mcm_field_organism/local_adaptive_receptivity.py`
- `mcm_field_organism/local_synaptic_memory_candidate.py`
- `mcm_field_organism/previous_state_contribution_hook.py`

Diese drei Dateien liefern Vergleichs- oder Interventionsmechaniken, sind aber
keine zusaetzlichen Zustandsrollen der neutralen produktiven Feldruntime.

## 1. Zustandsinventar eines Feldortes

### Dynamische Werte

`MCMNeuron` traegt genau zwei numerische lokale Dynamikwerte:

```text
activation
afterimage
```

Beide liegen im normalisierten Bereich `-1..1` und werden im
`SharedMCMFieldSnapshot` serialisiert. Auch `MCMNeuronOutput` kann nur diese
beiden Werte fuer den Folgezustand liefern.

### Technische und anatomische Rollen

Die folgenden Angaben sind keine freien Entwicklungszustaende:

| Rolle | Einordnung |
|---|---|
| `neuron_id`, `field_id`, `layer_id` | technische Identitaet |
| `modality_id`, `geometry_id` | Herkunfts- und Geometrievertrag |
| `position`, `sample_offsets`, `periodic_axes` | feste Anatomie |
| Dock- und Carrier-Zuordnung | feste Rezeptorgrenze |
| `tick`, Feldfenster, `step_time` | technische Kausal- und Zeitordnung |
| `receptor_contact` | gegenwaertige Weltzufuhr |
| `local_samples` | Kopie des abgeschlossenen lokalen Vorfelds |
| `last_distribution` | rekonstruierbare Eingangsprovenienz |
| Snapshot und Digest | technische Fortsetzung und Integritaet |

`local_samples` enthalten Aktivierung und Nachhall benachbarter Feldorte des
vorherigen Ticks. Sie erzeugen keine weitere lokale Zustandsdimension, weil
ihre Werte bereits im abgeschlossenen Vorfeld liegen und bei jedem Schritt
neu daraus gebildet werden.

## 2. Tatsaechliche aktive Naturform

### Activation

Die neutrale Runtime bildet aus der symmetrischen festen Nachbarschaft einen
linearen Diffusionsgenerator. Rezeptorkontakte gehen als Rand- beziehungsweise
Zufuehrungsterm ein. `activation` wird ueber reale Schrittdauer exakt entlang
dieses festen Generators fortgeschrieben.

Damit haengt die naechste schnelle Aktivierung ab von:

```text
vorheriger activation
+ feste lokale Geometrie
+ gegenwaertiger Rezeptorzufuhr
+ reale Schrittdauer
+ feste Antwort- und optionale Dissipationsparameter
```

Kein lokaler Zustand veraendert Generator, Nachbarschaft, Antwortform oder
Kopplungsbedingung.

### Afterimage

`afterimage` ist eine lineare schnelle Spur. Sie folgt der Activation mit
einer festen Zeitkonstante und optional derselben festen Dissipation.

In der aktiven Gleichung gilt jedoch nur:

```text
activation -> afterimage
```

Es gibt keinen Rueckterm:

```text
afterimage -> activation
```

Ein Eingriff nur in `afterimage` kann deshalb die spaetere
Activation-Trajektorie der neutralen Runtime nicht veraendern. Afterimage ist
ein serialisierter dynamischer Wert, aber kein reziproker Entwicklungszustand
der schnellen Feldwirkung.

### Perception und generische Transitionhuelle

Die allgemeine Layerhuelle stellt einem injizierten Transition-Callable den
vorherigen Neuronenzustand, lokale Vorfeldproben, Rezeptorkontakt und
Schrittzeit bereit. Das ist eine offene technische Kausalgrenze.

Die Offenheit der Huelle ist noch keine vorhandene Naturfunktion. In der
neutralen Runtime werden die Ausgaben aus dem festen Generator berechnet; die
Huelle fuegt keinen weiteren Zustand und keine Entwicklungsregel hinzu.

## 3. Markov-Grenze der heutigen schnellen Runtime

Seien zwei Weltgeschichten A und B zu einer Kausalgrenze in allen
`activation`-Werten gleich. Erhalten beide danach dieselbe Geometrie,
Rezeptorzufuhr, Schrittdauer und Konfiguration, dann sind ihre weiteren
Activation-Trajektorien gleich.

Unterschiedliche `afterimage`-Werte aendern diese schnelle Fortsetzung nicht.

Damit gilt fuer die aktive Runtime:

```text
gleiche aktuelle activation
+ gleiche kuenftige Weltwirkung
-> gleiche kuenftige activation
```

Eine fruehere Geschichte kann keine zusaetzliche spaetere schnelle
Feldwirkung tragen, sobald ihr Unterschied nicht mehr in `activation` liegt.

Das schliesst nicht Nachhall oder Feldzeit aus. Es zeigt nur, dass die heutige
Runtime keine von der schnellen Feldlage verschiedene konstitutive
Vorgeschichte besitzt, die spaeter auf das schnelle Feld zurueckwirkt.

## 4. Was mit dem vorhandenen Zustand nicht darstellbar ist

Nicht darstellbar ist derzeit die geforderte Kausaltrennung:

```text
Geschichte A -> gleiche schnelle Feldlage S, anderer konstitutiver Zustand L_A
Geschichte B -> gleiche schnelle Feldlage S, anderer konstitutiver Zustand L_B

+ identischer weiterer Weltkontakt
-> unterschiedliche schnelle Feldfortsetzung
```

Es fehlt ein Zustand, der zugleich:

1. nicht nur Kopie oder Funktion der aktuellen Activation ist;
2. durch lokale Feldteilnahme veraendert wird;
3. in derselben atomaren Naturform spaetere Activation mitveraendert;
4. ueber Snapshot und Wiederaufnahme vollstaendig fortgesetzt wird;
5. beim neutralen Wert exakt die heutige Runtime ergibt.

Ohne diesen Zustand sind substratvermittelte spaetere Feldwirkung,
funktionaler Tausch und Neutralisierung architektonisch nicht formulierbar.

## 5. Abgrenzung vorhandener Nebenmechaniken

### Lokale adaptive Receptivity

`LocalReceptivityState` besitzt einen skalaren Wert pro Neuron und skaliert
die spaeteren Rezeptorkontakte. Der Zustand lebt ausserhalb des
`SharedMCMFieldSnapshot` und wirkt als fester Eingangs-Gain.

Er ist damit eine enge Pflichtbaseline, aber nicht der fehlende
konstitutive MCM-Freiheitsgrad.

### Lokaler synaptischer Memory-Kandidat

Der passive Kandidat besitzt explizite Quellen-, Ziel- und Relations-IDs,
zwei Werte pro fester Relation und ein lokales Budget. Er schreibt nicht in
die Runtime zurueck und liegt ausserhalb des gemeinsamen Feldsnapshots.

Er ist historische Vergleichsmechanik und wegen fester Kanten-, Leser- und
Budgetstruktur kein zulaessiger neuer Organismuszustand.

### Previous-State-Operator

`None`, `identity` und `zero` sind private Forschungsinterventionen auf
Activation und Afterimage. Sie fuegen keine produktive Zustandsrolle hinzu
und duerfen nicht als Organismusfunktion verwendet werden.

## 6. Kleinste moegliche zusaetzliche Dimension

### Untergrenze

Mit null neuen lokalen Werten bleibt die Markov-Grenze unveraendert. Die
kleinste moegliche Schemaerweiterung ist daher:

```text
ein zusaetzlicher begrenzter skalarer Zustand L_i pro Feldort
```

Seine vorlaeufige physische Rollenbezeichnung lautet:

> lokale konstitutive Feldkonfiguration

Gemeint ist eine inhaltsfreie lokale Materiallage, die durch Feldteilnahme
mitentwickelt wird und innerhalb derselben atomaren Naturform die spaetere
lokale Feldfortsetzung mitbestimmt.

Der Begriff behauptet weder Memory noch Organisation. `L_i` ist kein Name
fuer Receptivity, Gain, Gewicht, Energie, Fehler oder gespeicherten Inhalt.

### Nur eine Dimensionsuntergrenze

Ein Skalar ist noch kein zugelassener Mechanikkandidat. Jede konkrete skalare
Wirkung kann auf bereits bekannte Klassen zurueckfallen:

- zusaetzliche Leaky-Spur;
- Integrator oder Saettigungsintegrator;
- adaptiver Gain;
- variable Zeitkonstante;
- zustandsabhaengige Mobilitaet;
- feste Hysterese;
- einfache nichtlineare Rekurrenz.

Der Audit stellt deshalb nur fest, dass weniger als ein zusaetzlicher Wert
unmoeglich ist. Er stellt nicht fest, dass ein Wert funktional genuegt.

## 7. Verbindliche Architekturbedingungen fuer L

Falls ein skalarer Kandidat spaeter zugelassen wird, muss er mindestens:

- pro bestehendem Feldort und ohne Partner-ID liegen;
- im selben `MCMNeuron`-Gesamtzustand fortgesetzt werden;
- in Snapshot, Restore und Digest enthalten sein;
- mit Activation innerhalb eines atomaren Schritts gemeinsam entstehen;
- nur lokalen abgeschlossenen Vorzustand, Vorfeld, Weltkontakt und `dt` lesen;
- bei neutralem L exakt die heutige Activation- und Afterimage-Runtime lassen;
- ohne besondere Schreib-, Lese-, Probe-, Loesch- oder Phasenfunktion wirken;
- dieselbe unveraenderte Naturform fuer Bildung, Wirkung und Umbildung nutzen.

Diese Punkte sind nur Architekturbedingungen. Sie geben kein Feld in der
Dataclass und keine Updategleichung frei.

## 8. Staerkste enge Pflichtbaselines

Fuer genau einen zusaetzlichen skalaren Zustand sind vor jeder konkreten Form
mindestens zu fuehren:

1. neutrale heutige Runtime ohne L;
2. zusaetzliche lineare Leaky-Spur;
3. L als saturierender Integrator;
4. L als adaptiver Rezeptor- oder Feld-Gain;
5. L als variable Zeitkonstante beziehungsweise Mobilitaet;
6. lineare reziproke S-L-Zweizustandsdynamik;
7. gedaempfter S-L-Oszillator;
8. feste skalare Hysterese;
9. gleich dimensionierte feste nichtlineare Rekurrenz;
10. Ablation `L -> S` und Ablation `S -> L`.

Der Kandidat muss nicht ausserhalb jeder Rekurrenz liegen. Er muss eine vorab
benannte Beobachtung tragen, welche diese engeren Klassen nicht gemeinsam
reproduzieren.

## 9. Auditentscheidung

```text
vorhandene schnelle Feldlage:         activation
vorhandene schnelle Spur:             afterimage
vorhandene konstitutive Rueckwirkung:  nein
fehlende Mindestkapazitaet:            ein lokaler skalarer Zustand
skalare funktionale Eignung:           offen
Schemaaenderung:                       nicht freigegeben
Gleichung oder Implementierung:        nicht freigegeben
```

Der aktuelle Code ist fuer den schnellen Wahrnehmungs- und Nachhallpfad
geeignet. Er besitzt jedoch keinen unabhaengigen langsamen lokalen Zustand,
der seine eigene Vorgeschichte spaeter wieder auf Activation wirken laesst.

## Bester naechster Schritt

Als naechstes wird ein **skalarer L-Suffizienz- und No-Go-Audit** erstellt.
Er muss vor jeder Gleichungswahl statisch entscheiden:

1. ob ein einzelner lokaler Skalar unter der vorhandenen skalaren
   Activation-Geometrie mehr sein kann als Spur, Gain, Mobilitaet, Integrator
   oder Hysterese;
2. welche unabhaengige physische Funktion dann uebrig bleibt;
3. ob eine Dimension funktional genuegt oder eine hoehere lokale
   Zustandsdimension zwingend begruendet werden muss.

Nur bei einem nichtleeren skalaren Rest darf ein konkreter L-Kandidat
formuliert werden.
