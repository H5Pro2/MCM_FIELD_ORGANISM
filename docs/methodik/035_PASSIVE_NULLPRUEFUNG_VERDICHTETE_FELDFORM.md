# Methodik 035: Passive Nullprüfung verdichteter Feldform

## 1. Status

Vorregistrierte passive Nullprüfung zu Architektur 020.

Es wird ausschließlich die vorhandene visuelle Kette verwendet. Der Versuch
führt keine Persistenz, Formvariable, Ähnlichkeitsfunktion oder neue
Feldtransition ein.

## 2. Forschungsfrage

Trägt der gegenwärtige schnelle visuelle MCM-Zustand nach vollständiger
Feldleerung noch Information aus einer vorausgehenden Folge verschiedener
Ansichten?

Die bindende Nullfrage lautet:

```text
verschiedene vorherige Ansichtsgeschichte
+ exakt gleicher schneller Zustand vor der Probe
+ exakt gleiche neue Holdout-Ansicht
→ identische oder verschiedene Feldantwort?
```

Die aktuelle Architektur sagt eine exakte Kollision voraus.

## 3. Geprüfte fehlende Funktion

Der Versuch prüft noch kein Wiedererkennen.

Er isoliert den Funktionsmangel aus Architektur 020:

> Nach vollständiger Lösung der schnellen Feldlage kann die vorhandene
> visuelle Runtime eine neue Ansicht nicht aufgrund früherer Weltteilnahme
> anders organisieren.

Ein negativer Befund trägt nur diese Grenze.

## 4. Unveränderte Runtime

Der vollständige Pfad lautet:

```text
synthetischer äußerer Frame
→ LocalChannelGridReceptor
→ VisualMCMInterface
→ visuelle MCM-Neuronenschicht
→ receptor_projection_baseline
→ abgeschlossenes visuelles Feldfenster
```

Verwendet werden:

```text
Raster:             5 x 5
Kanäle:             3
lokale Offsets:     oben, unten, links, rechts
Feldtransition:     receptor_projection_baseline
```

Die Runtime erhält keine Familienkennung, Ansichtsklasse, Transformation,
History-ID oder Holdout-Markierung.

## 5. Äußere Formfamilien

Der Testtreiber erzeugt zwei endliche lokale Kontaktanordnungen `A` und `B`.

Beide besitzen:

- dieselbe Rastergröße,
- dieselbe Zahl aktiver lokaler Kontakte,
- dieselbe Kontaktamplitude,
- denselben aktiven technischen Kanal,
- dieselbe gesamte Kontaktenergie,
- dieselbe Anzahl zeitlicher Ansichten.

`A` und `B` sind nicht durch die vorregistrierten räumlichen Transformationen
ineinander überführbar.

Die Namen `A` und `B` existieren ausschließlich im äußeren Forschungsbericht.
Sie gelangen nicht in Rezeptor, Feldzeit, Neuron, Feldfenster oder Verteiler.

Für Rasterkoordinaten `(Zeile, Spalte)` mit Indizes `0 ... 4` werden
vorregistriert:

```text
A0 = {(1,1), (2,1), (3,1), (3,2)}
B0 = {(1,1), (1,2), (1,3), (2,2)}
```

Jede aktive Rasterzelle trägt ausschließlich im technischen Kanal `0` die
Amplitude `1.0`. Alle übrigen Zellen und Kanäle tragen `0.0`.

Bei einer Quellauflösung von `10 x 10` wird jede Rasterzelle durch einen
vollständigen `2 x 2`-Pixelblock abgebildet. Aktive Pixel tragen den
ganzzahligen Kanalwert `255`.

`A0` und `B0` besitzen jeweils vier aktive Kontakte. Sie sind unter Rotation
und Spiegelung nicht ineinander überführbar.

## 6. Ansichten

Eine Ansicht entsteht ausschließlich durch eine vorregistrierte starre
Transformation der lokalen Kontaktanordnung:

```text
Rotation 0 Grad
Rotation 90 Grad
Rotation 180 Grad
Rotation 270 Grad
Spiegelung
```

Es werden keine erkannten Kanten, Ecken, Flächen oder Objektmerkmale
berechnet.

Die Transformationen dienen dem äußeren Weltaufbau. Sie sind keine Fähigkeit
des MCM-Feldes.

Die vier Geschichtsansichten werden in dieser Reihenfolge erzeugt:

```text
R0(r,c)   = (r,c)
R90(r,c)  = (c,4-r)
R180      = R90(R90(r,c))
R270      = R90(R180(r,c))
```

## 7. Holdout

Die Holdout-Probe ist eine transformierte Ansicht von `A`, die in der
zugehörigen vorherigen Geschichte nicht als identischer Frame vorkam.

Sie wird als vertikale Spiegelung von `A0` festgelegt:

```text
M(r,c) = (r,4-c)

Holdout A* = {(1,3), (2,3), (3,3), (3,2)}
```

Sie wird in allen Vergleichszweigen bytegleich, mit derselben Feldzeit und
demselben Frameindex übergeben.

Der Testtreiber kennt ihre Herkunft. Die Runtime erhält nur den aktuellen
Rezeptorkontakt.

## 8. Vorregistrierte Zweige

### H-A: verwandte Ansichtsgeschichte

```text
vier verschiedene transformierte Ansichten von A
→ Feldleerung
→ Holdout von A
```

### H-B: Kontrollgeschichte

```text
dieselben vier äußeren Transformationsrollen von B
→ Feldleerung
→ derselbe Holdout von A
```

### H-P: Reihenfolgekontrolle

```text
dieselben vier Ansichten von A in vorregistriert umgekehrter Reihenfolge
→ Feldleerung
→ derselbe Holdout von A
```

### H-0: keine Formgeschichte

```text
vier kontaktlose Frames
→ Feldleerung
→ derselbe Holdout von A
```

Alle Zweige besitzen dieselbe Anzahl Schritte und dieselbe technische
Zeitstruktur.

## 9. Exakte Feldleerung

Zwischen Geschichte und Holdout liegt mindestens ein vollständig
kontaktloser Frame.

Unter `receptor_projection_baseline` muss sein abgeschlossenes Feldfenster
exakt tragen:

```text
activation = 75-mal 0.0
afterimage = 75-mal 0.0
```

Zusätzlich müssen die lokalen Wahrnehmungen des Holdout-Schritts ausschließlich
den abgeschlossenen Nullzustand dieses Leertakts als vorherige Feldlage lesen.

Der Leertakt ist kein Sleep, keine Konsolidierung und kein Training.

## 10. Primärvergleich

Für jeden Zweig werden vor dem Holdout geprüft:

```text
gleiche Träger
gleiche Geometrie
gleiche Feldzeit
gleicher Frameindex
gleiche Aktivierung
gleicher Nachhall
gleiche lokale vorherige Wahrnehmung
```

Danach werden die vollständigen Holdout-Feldfenster verglichen:

```text
D(H-A, H-B)
D(H-A, H-P)
D(H-A, H-0)
```

Primärmaß ist die L1-Distanz über den vollständigen Aktivierungs- und
Nachhallvektor. Zusätzlich müssen die kanonischen Feldfensterdigests
kollidieren.

Es wird kein Neuron, Kontakt oder Merkmal als Gewinner ausgewählt.

## 11. Erwartung der aktuellen Runtime

Die vorregistrierte Vorhersage lautet:

```text
D(H-A, H-B) = 0
D(H-A, H-P) = 0
D(H-A, H-0) = 0
```

Begründung:

```text
receptor_projection_baseline
→ aktuelle Aktivierung entspricht nur aktuellem Rezeptorkontakt
→ Nachhall ist null
→ vorherige lokale Feldlage ist nach Leertakt null
→ gleiche Holdout-Probe erzeugt gleiche Feldantwort
```

Das ist ein erwarteter Negativbefund, kein Scheitern des Versuchs.

## 12. Pflichtbaselines

### B0: aktuelle Rezeptorprojektion

Die unveränderte Runtime ist die stärkste Nullbaseline. Sie muss jeden
Holdout-Schritt exakt vorhersagen.

### B1: feste unabhängige Leaky-Integratoren

Für jede lokale Kontaktlage werden feste Zeitkonstanten getrennt geprüft:

```text
tau = 1.0, 2.0, 4.0
```

Vor der Holdout-Probe werden zwei Auswertungen geführt:

1. natürliche endliche Relaxation mit exakt ausgewiesener Restspur;
2. exakter Reset ausschließlich der Baseline.

Ein durch Restspur erklärter Unterschied ist keine verdichtete Feldform.

### B2: feste lokale Rekurrenz

Geprüft werden unveränderte Rekurrenzfaktoren:

```text
rho = 0.25, 0.5, 0.75
```

Auch hier werden natürliche Restwirkung und exakter Reset getrennt.

### B3: unveränderliche lokale Kanten

Ein fester symmetrischer Nachbarschaftsschritt darf den aktuellen Holdout
räumlich transformieren. Da seine Kanten nicht aus der Geschichte entstehen,
muss er in allen Zweigen kollidieren.

### B4: äußerer Templatevergleich

Ein Forschungsobserver darf gespeicherte vorherige Frames mit dem Holdout
unter der vollständigen vorregistrierten Rotations- und Spiegelungsfamilie
vergleichen.

Diese Baseline zeigt nur, ob ein Bildarchiv oder eine äußere
Transformationssuche die Aufgabe lösen könnte. Sie schreibt nicht zurück und
ist ausdrücklich kein zulässiges inneres Memory.

## 13. Atomare Zeitkontrolle

Die zeitliche Reihenfolge ist bindend:

```text
abgeschlossene Ansicht t
→ Feldtransition t+1
→ abgeschlossener Leertakt
→ Holdout-Transition
→ Holdout-Beobachtung
```

Der Holdout darf nicht im selben Takt seine eigene historische Evidenz
erzeugen und erneut lesen.

## 14. Weitere Nullkontrollen

1. Jeder Zweig beginnt mit einer frischen visuellen Schnittstelle.
2. Frames werden durch die Schnittstelle nicht verändert oder gehalten.
3. Observer erhalten ausschließlich unveränderliche abgeschlossene Ausgaben.
4. Normale und umgekehrte Auswertungsreihenfolge müssen kollidieren.
5. Unabhängige Wiederholung muss denselben Gesamtdigest erzeugen.
6. Kanalpermutation wird nur außen durchgeführt und kanonisch zurückgeführt.
7. Räumliche Spiegelung des vollständigen Versuchs muss äquivariant sein.
8. Eine absichtlich ungleiche Holdout-Probe muss vom Vergleich erkannt werden.
9. Familiennamen und Transformationsrollen dürfen in keiner Runtime-Rolle
   erscheinen.
10. Der Test hält keine Rohframes nach Abschluss eines Zweigs.

## 15. Entscheidung

### Erwartete vollständige Kollision

Kollidieren alle Holdout-Feldfenster exakt, trägt der Versuch:

> Das gegenwärtige visuelle MCM-Feld bildet aktuelle lokale Wahrnehmung ab,
> besitzt nach vollständiger Feldleerung aber keine ansichtsübergreifende
> Organisationsgeschichte.

Damit ist die fehlende Funktion beobachtbar abgegrenzt.

### Unterschied bei natürlicher B1- oder B2-Restspur

Ein Unterschied, der exakt aus Leaky-Zustand oder fester Rekurrenz vorhergesagt
wird, trägt nur zeitliche Restwirkung.

### Unterschied nach exakter Feldleerung

Bleibt in der unveränderten Runtime ein Unterschied, müssen zuerst geprüft
werden:

- ungleiche Holdout-Frames,
- ungleiche Feldzeit oder Frameindizes,
- unvollständige Feldleerung,
- versteckter Schnittstellenzustand,
- Observer-Rückwirkung,
- technische Reihenfolge,
- Rundungs- oder Digestfehler.

Erst nach Ausschluss dieser Ursachen wäre die aktuelle Zustandsbeschreibung
unvollständig. Ein Lernbefund wäre es noch nicht.

## 16. Stärkstes Gegenargument

Die Nullprüfung bestätigt wahrscheinlich nur eine bereits aus dem Code
erkennbare Tatsache:

```text
eine zustandslose Rezeptorprojektion
speichert keine vorausgehenden Ansichten
```

Der Lauf bleibt dennoch notwendig. Er fixiert erstmals die konkrete
ansichtsübergreifende Weltfunktion, die ein späterer organischer
Verdichtungskandidat tragen müsste, ohne sie bereits durch eine
Speichermechanik zu erzeugen.

## 17. Evidenzgrenze

```text
Grenze des vorhandenen schnellen visuellen Feldes: maximal E2
ansichtsübergreifende Feldform:                    E0
verdichtende Organisationsmechanik:                E0
entwickelte innere Bezeichnung:                    E0
Feldintelligenz:                                   E0
```

## 18. Stopplinie

Nicht freigegeben sind:

- eine langsame Zustandsvariable,
- adaptive Kopplung oder Kante,
- Ähnlichkeitsschwelle,
- Gewinnerauswahl,
- Template- oder Bildspeicher,
- Objekt-, Form- oder Muster-ID,
- externe Cluster,
- Lernrate, Reward oder Ziel,
- Sprache, Syntax oder Handlung.

## 19. Bester nächster Schritt

Methodik 035 wird zuerst exakt als passiver Lauf umgesetzt.

Nur wenn Nullzweige, Feldleerung, Baselines, Symmetrie und Observer-Neutralität
vollständig tragen, darf anschließend der nachgewiesene Funktionsmangel gegen
die vorhandenen lokalen Zustandsrollen abgeglichen werden. Eine neue
Persistenzmechanik wird durch den erwarteten Negativbefund nicht automatisch
freigegeben.
