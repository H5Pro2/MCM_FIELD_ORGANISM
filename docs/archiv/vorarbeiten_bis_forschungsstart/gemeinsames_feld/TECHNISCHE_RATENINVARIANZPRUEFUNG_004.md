# Technische Rateninvarianzprüfung 004

## Status

Passive Baselineprüfung vor `GF_001`.

Diese Prüfung verändert die MCM-Runtime nicht. Sie verwendet ausschließlich
den bereits bekannten unabhängigen exponentiellen B1-Nachhall aus Methodik 002
als mathematische Zeitbaseline.

## Fragestellung

Kann derselbe vollständig beschriebene zeitliche Weltkontakt unabhängig davon
dieselbe passive Endlage erzeugen, ob er durch viele kurze oder wenige lange
technische Segmente dargestellt wird?

Getrennt wird:

```text
verstrichene physikalische Dauer
gegen
bloße Anzahl technischer Ereignisse
```

## Kontrollierter Weltverlauf

Die Gesamtdauer beträgt zwei Sekunden:

```text
0,0 s bis 1,0 s: Kontakt 0,8
1,0 s bis 2,0 s: Kontakt 0,0
```

Beide Darstellungen enthalten exakt dieselben Kontaktgrenzen:

- dicht: 20 Segmente zu 0,1 Sekunden,
- dünn: 4 Segmente zu 0,5 Sekunden.

Geprüft werden die bereits verwendeten Baseline-Zeitkonstanten
`tau = 0,25`, `1,0` und `4,0` Sekunden.

## Baselines

### B0: Verstrichene Zeit

```text
d = exp(-dt / tau)
```

`dt` ist die reale Dauer des jeweiligen Segments.

### B1: Ereigniszähler

Jedes Segment erhält unabhängig von seiner realen Dauer denselben festen
Schritt `dt = 1`. Diese Baseline bildet die problematische Gleichsetzung von
Ereignisanzahl und innerer Zeit ab.

### B2: Ausgelassener Kontakt

Ein kurzer Impuls ist in der dichten Referenz enthalten, in der dünnen
Darstellung aber vollständig ausgelassen. Damit wird geprüft, ob korrekte Zeit
fälschlich als Wiederherstellung fehlender Wahrnehmung ausgegeben wird.

## Ergebnis

| tau | Zeitbaseline: Differenz | Ereigniszähler: Differenz |
|---:|---:|---:|
| 0,25 s | `5,20e-18` | `2,68e-4` |
| 1,00 s | `8,33e-17` | `9,36e-2` |
| 4,00 s | `2,78e-16` | `1,31e-1` |

Die verstrichene Zeit trägt die Rateninvarianz innerhalb reiner
Gleitkommatoleranz. Der Ereigniszähler scheitert bei allen drei
Zeitkonstanten.

Beim ausgelassenen kurzen Kontakt bleibt eine Enddifferenz von
`0,0350083575`. Die Zeitbaseline rekonstruiert keine fehlende Wahrnehmung.

## Befund

Für die bekannte passive B1-Baseline gilt:

```text
vollständig erhaltener Weltverlauf
+ reale Segmentdauer
-> invariant gegen reine Segmentaufteilung
```

Gleichzeitig gilt:

```text
fehlender Weltkontakt
+ korrekte Zeit
-> bleibt fehlender Weltkontakt
```

Der erste Teil folgt mathematisch aus der Exponentialform und ist keine
Entdeckung einer organischen MCM-Zeit. Sein Forschungswert liegt in der
Scheitergrenze: Ein bloßer Ereigniszähler ist keine tragfähige Zeitbasis für
Nachhall oder Relaxation bei unterschiedlich schnellen Rezeptoren.

## Konsequenz für die Architektur

Die aktuelle MCM-Neuronenschicht kennt einen ganzzahligen `tick`, aber keine
verstrichene Organismusdauer innerhalb des Neuronenantriebs. Damit kann eine
spätere zeitabhängige Feldmechanik derzeit nicht zwischen zehn Millisekunden
und einer Sekunde unterscheiden.

Das rechtfertigt noch keine Nachhall-, Kopplungs- oder Memorygleichung. Es
begründet nur den nächsten Vertragskandidaten: Ein atomarer Feldschritt müsste
seine reale Zeitspanne unverändert kennen, ohne dass die Zeitspanne selbst
Aktivität, Bedeutung oder Beziehung erzeugt.

## Konsequenz für GF_001

`GF_001` bleibt geschlossen.

Vor einer Runtimeänderung ist ein passiver Zeitspannenvertrag zu definieren
und gegen folgende Fehler zu prüfen:

- Zeitrücklauf und Überlappung,
- Abhängigkeit von technischer Iterationsreihenfolge,
- Gleichsetzung von Dauer und Aktivität,
- Wiederherstellung ausgelassener Kontakte,
- modality-spezifische Gewichtung,
- versteckte Feldfortschaltung ohne Welt- oder innere Ursache.

Der nachfolgende
[Technische Zeitspannenvertrag 005](TECHNISCHER_ZEITSPANNENVERTRAG_005.md)
setzt ausschließlich diese neutrale Übergaberolle um. Er erzeugt noch keine
Feldschrittfolge und keine zeitabhängige MCM-Mechanik.

Feldkopplung, Topologie, Memory, Semantik, Reflexion und Selbstregulation
bleiben geschlossen.
