# Befund 040: Passive Falsifikationsmatrix der Übergangsdisposition

## Ergebnis

Methodik 037 wurde vollständig passiv auf der unveränderten visuellen
MCM-Schnittstelle ausgeführt.

Der kanonische Gesamtdigest lautet:

```text
7928c4d21ed346c6d4bd7b9381983591d43647b68f72d4f9a9a04b0be6babecb
```

Geprüft wurden vier unabhängig aufgebaute Weltzweige mit jeweils 33 Takten
gegen die festen Baselines B0 bis B6. Keine Baseline schrieb in die
MCM-Runtime zurück. Es wurde keine Übergangsdisposition implementiert.

## Primäre Angleichung

Alle Zweige erhielten zuerst vier identische A-Ereignisse `2 → 3`.

Der Konkurrenzzweig B und die angeglichene Nicht-Konkurrenz M besaßen danach
exakt:

```text
P2-Dauer             = 16 Takte
P2-Energie           = 8.0
Gesamtenergie        = 16.0
Positionshäufigkeit  = identisch
kontaktlose Takte    = identisch
```

Sie unterschieden sich ausschließlich in der zeitlichen Nachbarschaft:

```text
B: (4 → 3 → - → -) x 4
M: (4 → - → 3 → -) x 4
```

Nur B erzeugte vier lokale Ereignisse `4 → 3`.

## Übergangsevidenz

Die vorregistrierten Ereignisse entstanden exakt:

```text
A in allen Zweigen       = 4
B im Konkurrenzzweig     = 4
B in der Kontrolle M     = 0
U im unabhängigen Zweig  = 4
```

Für jedes Ereignis galt:

```text
source_tick = target_tick - 1
evidence    = 1.0
```

Nach dem abschließenden kontaktlosen Takt waren Aktivierung und Nachhall in
allen schnellen MCM-Feldern exakt null.

## Baseline-Ergebnisse

### B0: Schnelles Feld

Alle Zweige kollidierten nach dem Abschlusskontakt bei null. Das schnelle Feld
trägt keine gelöste Übergangsgeschichte.

### B1: Positionshäufigkeit

B und M waren exakt identisch. Einzelne Neuronenhäufigkeiten erkennen die
konkurrierende zeitliche Folge nicht.

### B2 und B4: Zähler und permanente Kante

Die alte A-Komponente blieb in B und M jeweils bei:

```text
A-Zähler        = 4.0
A-Kante gesetzt = 1.0
```

Neue B-Evidenz kam nur hinzu. Sie löste A nicht.

### B3: Unabhängige Leaky-Spuren

Für alle festen Zerfallsfaktoren blieb A zwischen B und M bit-identisch:

```text
decay 0.25 → A = 0.0000000000036522453898
decay 0.50 → A = 0.00000203447416425
decay 0.75 → A = 0.00612337988483
decay 0.90 → A = 0.320016332415
```

Die B-Spur entstand zusätzlich, veränderte die A-Spur aber nicht.

### B5: Unabhängige Sättigung

Bei den festen Kapazitäten `1`, `2` und `4` blieb die gesättigte
A-Komponente zwischen B und M gleich. Einzelsättigung begrenzt jede Spur,
bildet aber keine geteilte lokale Beanspruchung.

### B6: Globale Normalisierung

Die A-Anteile lauteten:

```text
Konkurrenz B             = 0.5
Nicht-Konkurrenz M       = 1.0
unabhängige U-Evidenz    = 0.5
Leerlauf                 = 1.0
```

Globale Normalisierung erzeugte die gesuchte Absenkung unter B. Sie senkte A
jedoch ebenso durch das räumlich unabhängige U-Ereignis und verletzte damit
die Lokalitätskontrolle.

## Getragener Negativbefund

Unter den geprüften Bedingungen können unabhängige Zähler, Leaky-Spuren,
permanente lokale Kanten und unabhängige Einzelsättigung keine
konkurrenzgekoppelte Lösung einer alten lokalen A-Einbindung darstellen.

Globale Normalisierung kann eine relative Absenkung erzeugen, unterscheidet
aber lokale Konkurrenz nicht von unabhängiger Weltaktivität.

Damit bleibt ein klarer Repräsentationsrest:

```text
lokal konkurrierende Übergangsevidenz
→ zusätzliche lokale Lösung
```

## Was nicht gezeigt ist

Nicht gezeigt sind:

- die Notwendigkeit einer geteilten lokalen Ressource,
- eine geeignete Zustandsvariable,
- eine Übergangsdisposition,
- entwickelte Topologie,
- Wiederbindung,
- funktionaler Wechsel,
- innere Bezeichnung,
- Semantik oder Feldintelligenz.

Die Matrix zeigt nur, was die geprüften einfachen Baselines nicht leisten.
Sie beweist nicht, dass der offene Funktionsrest biologisch oder
MCM-spezifisch notwendig ist.

## Stärkstes Gegenargument

Die geforderte lokale Ressource ist weiterhin eine Architekturhypothese.
Solange keine spätere identische Feldprobe zeigt, dass die Organisation nach
lokaler Konkurrenz funktional anders wirkt, könnte die gewünschte A-Absenkung
nur eine willkürlich definierte Buchhaltungsgröße sein.

Eine neue Mechanik würde diesen Mangel nicht lösen, wenn sie das erwartete
Ergebnis bereits durch feste Kantenrollen, feste Gewinnerwahl oder eine
eingebaute Leserform erzeugt.

## Evidenz

```text
exakte Baseline-Algebra B0-B6:        E2
Lokalitätsfehler globaler Normierung: E2
Repräsentationsrest der Baselines:    E1
Notwendigkeit lokaler Ressource:      E0
Übergangsdisposition:                 E0
entwickelte Topologie:                E0
Feldintelligenz:                      E0
```

## Stopplinie

Nicht freigegeben sind:

- neue Runtime-Zustände,
- Ressourcen- oder Dispositionsmechanik,
- feste oder adaptive Lernrate,
- Gewinnerregel oder Rangliste,
- Mehrzyklenschleife,
- semantische Klasse,
- Reward, Ziel oder Handlung,
- Rückschreibung in Rezeptoren oder MCM-Felder.

## Bester nächster Schritt

Vor einem Mechanikkandidaten wird eine nicht tautologische spätere Feldprobe
abgegrenzt:

```text
gleiche spätere Weltprobe
+ kontrollierte schnelle Trägerzustände
+ verschieden entstandene lokale Übergangsgeschichte
→ mögliche andere kausale Feldantwort
```

Die Messung darf weder eine gespeicherte Kante direkt auslesen noch eine
vorgegebene Übergangsrolle als Antwort verwenden. Erst wenn eine solche Probe
eine notwendige Leistung benennt, kann geprüft werden, ob überhaupt eine
endliche lokale Zustandsrolle erforderlich ist.
