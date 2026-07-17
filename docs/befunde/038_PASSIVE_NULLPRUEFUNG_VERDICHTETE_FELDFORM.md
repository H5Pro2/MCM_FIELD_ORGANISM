# Befund 038: Passive Nullprüfung verdichteter Feldform

## Ergebnis

Methodik 035 wurde vollständig passiv mit der unveränderten visuellen
MCM-Schnittstelle ausgeführt.

Der kanonische Gesamtdigest lautet:

```text
3cf1021c2f1331a59e2e636d52f21a69e4d19dc21b80fd0b6585dc34a39472ae
```

Geprüft wurden:

```text
4 Ansichtsgeschichten
3 primäre Holdout-Paare
9 Leaky-Baselinevergleiche
9 feste Rekurrenzvergleiche
4 äußere Templatevergleiche
```

## Ansichtsgeschichten

Die vorregistrierten Zweige trugen:

```text
H-A: vier Rotationen der Formfamilie A
H-B: vier Rotationen der nicht kongruenten Formfamilie B
H-P: dieselben vier Ansichten von A in umgekehrter Reihenfolge
H-0: vier kontaktlose Frames
```

Danach folgten in jedem Zweig:

```text
ein vollständig kontaktloser Leertakt
→ derselbe neue gespiegelte Holdout A*
```

Der Holdout war in keiner Geschichte als identischer Frame enthalten.

## Energieangleichung

Die drei aktiven Geschichten trugen exakt dieselbe äußere Kontaktenergie:

```text
H-A = 16.0
H-B = 16.0
H-P = 16.0
```

Der ausdrücklich kontaktlose Nullzweig trug:

```text
H-0 = 0.0
```

Damit kann der Vergleich von H-A, H-B und H-P nicht durch unterschiedliche
Gesamtenergie erklärt werden.

## Exakte Feldleerung

Vor dem Holdout galt in allen vier Zweigen:

```text
maximale Aktivierung = 0.0
maximaler Nachhall   = 0.0
```

Auch alle vorherigen Eigenzustände und lokalen Feldproben, die im
Holdout-Schritt gelesen wurden, trugen exakt null.

Der Holdout konnte dadurch keine schnelle Restlage der vorausgehenden
Ansichten lesen.

## Primärer Nullbefund

Für alle drei Paarvergleiche galt:

```text
D_activation = 0.0
D_afterimage = 0.0
Feldfensterdigest gleich
lokaler Eingabedigest gleich
```

Konkret:

```text
H-A gegen H-B = vollständige Kollision
H-A gegen H-P = vollständige Kollision
H-A gegen H-0 = vollständige Kollision
```

Die identische Holdout-Probe erzeugte nach exakter Feldleerung unabhängig von
der vorherigen Ansichtsgeschichte dieselbe Feldantwort.

## B0: Vorhandene Rezeptorprojektion

Die unveränderte `receptor_projection_baseline` sagte alle
Holdout-Feldfenster exakt voraus:

```text
aktuelle Aktivierung = aktueller Rezeptorkontakt
Nachhall             = 0.0
```

Es blieb kein unerklärter Entwicklungsrest.

## B1: Feste Leaky-Integratoren

Unter natürlicher endlicher Relaxation blieben für alle Zeitkonstanten
messbare Unterschiede:

```text
tau = 1.0:  D = 0.404731 ... 0.607501
tau = 2.0:  D = 0.587984 ... 1.272369
tau = 4.0:  D = 0.375608 ... 1.533602
```

Nach exaktem Reset der jeweiligen Baseline galt in allen neun Vergleichen:

```text
D = 0.0
```

Die natürliche Leaky-Spur unterschied auch H-A von H-P. Beide Zweige
enthielten dieselben vier Ansichten, nur in umgekehrter Reihenfolge.

Damit trägt B1 zeitliche Restgeschichte, aber keine
reihenfolgeübergreifend verdichtete Form.

## B2: Feste Rekurrenz

Auch die unveränderten Rekurrenzfaktoren trugen natürliche Restunterschiede:

```text
rho = 0.25: D = 0.292969 ... 0.427734
rho = 0.50: D = 1.125000 ... 1.875000
rho = 0.75: D = 1.722656 ... 6.152344
```

Nach exaktem Reset kollidierten alle neun Vergleiche:

```text
D = 0.0
```

Auch B2 unterschied H-A von der umgekehrten Reihenfolge H-P. Eine feste
Rekurrenz verlängert Geschichte, verdichtet sie aber nicht automatisch zu
einer Form.

## B3: Unveränderliche lokale Kanten

Ein fester symmetrischer Nachbarschaftsschritt wurde auf den aktuellen
Holdout angewandt.

Da der Holdout in allen Zweigen identisch war und die Kanten keine Geschichte
trugen, kollidierten alle Ausgaben exakt.

Eine unveränderliche lokale Geometrie ergänzt keine ansichtsübergreifende
Information.

## B4: Äußerer Templatevergleich

Der äußere Forschungsobserver durfte frühere Frames speichern und unter der
vollständigen vorregistrierten Rotations- und Spiegelungsfamilie durchsuchen.

Seine minimalen L1-Abstände lauteten:

```text
H-A = 0.0
H-B = 2.0
H-P = 0.0
H-0 = 4.0
```

Damit kann ein Bildarchiv mit äußerer Transformationssuche die verwandte
Formfamilie technisch unterscheiden.

Dieser positive Baselinewert ist keine Fähigkeit des Organismus. Er beruht
gerade auf gespeicherten Vorlagen und einer vorgegebenen
Transformationsfamilie.

## Symmetrie und Kontrollen

Getragen wurden:

- vollständige räumliche Spiegeläquivalenz,
- Äquivalenz nach technischer Kanalpermutation,
- Erkennung einer absichtlich ungleichen Holdout-Probe,
- normale und umgekehrte Zweigreihenfolge,
- leerer und sammelnder Observer,
- unabhängige Wiederholung,
- unveränderte Eingangsframes,
- keine Rohframes im Ergebnis,
- keine Runtime-Rückschreibung.

## Getragener Befund

Das vorhandene schnelle visuelle MCM-Feld trägt die aktuelle lokale
Wahrnehmung und ihre vorherige abgeschlossene Feldlage.

Nach einem exakt feldleeren Takt besitzt es jedoch keine
ansichtsübergreifende Organisationsgeschichte:

```text
verschiedene Ansichtsgeschichte
→ schnelle Feldlage vollständig gelöst
→ identischer neuer Holdout
→ identische Feldantwort
```

Die in Architektur 020 beschriebene verdichtete Feldform ist damit als
fehlende Funktion konkret beobachtbar abgegrenzt.

## Nicht gezeigt

Der Versuch zeigt nicht:

- dass eine neue langsame Variable erforderlich ist,
- welche lokale Organisationsform geeignet wäre,
- dass Ansichten natürlich als zusammengehörig erkannt werden,
- Wiedererkennen, Objektbildung oder Semantik,
- eine entwickelte innere Bezeichnung,
- Reorganisation oder Feldintelligenz.

## Stärkstes Gegenargument

Der Nullbefund folgt direkt aus der vorhandenen zustandslosen
Rezeptorprojektion:

```text
kein fortbestehender Zustand
+ gleiche aktuelle Eingabe
→ gleiche Ausgabe
```

Der wissenschaftliche Wert liegt deshalb nicht in einer überraschenden
Dynamik. Er liegt in der erstmals exakt fixierten Weltfunktion, die ein
späterer Kandidat zusätzlich tragen müsste, ohne auf Bildspeicher,
Transformationssuche oder bloße Zeitreste zurückzufallen.

## Evidenz

```text
Grenze des schnellen visuellen Feldes:       E2
vollständige Holdout-Kollision:               E2
Leaky- und Rekurrenzrest als Baseline:        E2
äußerer Templatevergleich als Gegenmodell:    E2
ansichtsübergreifende Feldform:               E0
verdichtende Organisationsmechanik:           E0
entwickelte innere Bezeichnung:               E0
Feldintelligenz:                              E0
```

## Stopplinie

Nicht freigegeben sind:

- eine neue Persistenzvariable,
- adaptive Kopplung oder Kante,
- feste Formmerkmale,
- Ähnlichkeitsschwelle oder Gewinnerauswahl,
- Bild-, Template- oder Episodenspeicher,
- Objekt-, Form- oder Muster-ID,
- Lernrate, Reward oder Ziel,
- Sprache, Syntax oder Handlung.

## Bester nächster Schritt

Vor jeder neuen Mechanik werden die bereits vorhandenen lokalen Zustandsrollen
gegen den nachgewiesenen Funktionsmangel abgeglichen:

```text
Welche minimale lokale Disposition könnte verschiedene Ansichten durch
gemeinsame Weltteilnahme verbinden, ohne eine Ansicht, eine Formklasse oder
eine Transformationsregel zu speichern?
```

Dieser Abgleich muss zusätzlich festlegen:

- welche lokale Evidenz überhaupt gemeinsame Weltteilnahme trägt,
- welche endliche Ressource beansprucht wird,
- welche spätere Feldfunktion kausal verändert wird,
- wie eine verdichtete Form Wirkung verliert und sich vollständig löst,
- wodurch feste Leaky-Spur, Rekurrenz und unveränderliche Kante scheitern.

Erst danach kann ein neuer passiver Kandidat vorregistriert werden.
