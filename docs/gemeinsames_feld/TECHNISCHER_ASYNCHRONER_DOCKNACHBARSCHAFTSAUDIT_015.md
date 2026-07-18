# Technischer asynchroner Docknachbarschaftsaudit 015

## Status

Passive Strukturprüfung vor `GF_001`.

Der Audit prüft, wann zwei aufeinanderfolgende Kontakte desselben Docks auch
in der globalen asynchronen Abschlussfolge unmittelbar benachbart bleiben.
Abschlussgruppen werden dabei ausdrücklich nicht zu MCM-Feldticks erklärt.

Es werden keine Kontakte gehalten, keine Zwischenwerte rekonstruiert und keine
Neuronenübergänge ausgeführt.

## Unterscheidung der Nachbarschaften

Für jedes Dock werden zwei Ordnungen getrennt:

```text
lokale Dockfolge:
aufeinanderfolgende Zustände desselben Rezeptorprozesses

globale Abschlussfolge:
zeitlich geordnete Abschlussgruppen aller Rezeptorprozesse
```

Ein lokales Kontaktpaar bleibt global unmittelbar benachbart, wenn zwischen
seinen beiden Abschlussgruppen keine andere Abschlussgruppe liegt. Eine
gleichzeitige gemischte Gruppe bleibt ungeordnet und gilt nicht als
gegenseitige Unterbrechung.

## Kontrollierte Folgen

### 1. Abwechselnde Modalitäten

```text
A1 -> V1 -> A2 -> V2 -> A3 -> V3
```

Jedes Dock besitzt lokal zwei aufeinanderfolgende Paare. Global bleibt davon
kein Paar unmittelbar benachbart.

| Dock | lokale Paare | global benachbart | unterbrochen |
|---|---:|---:|---:|
| auditiv | 2 | 0 | 2 |
| visuell | 2 | 0 | 2 |

### 2. Kontrollierte Ratenschiefe `310:16`

Die Ereigniszahlen entsprechen dem früher real gemessenen Verhältnis aus
Audit 003. Ihre Zeitpositionen sind eine synthetische Kontrolle und keine neue
Gerätemessung.

| Dock | Ereignisse | lokale Paare | global benachbart | unterbrochen |
|---|---:|---:|---:|---:|
| auditiv | 310 | 309 | 293 | 16 |
| visuell | 16 | 15 | 0 | 15 |

Damit wären bei einer ungeprüften Fortschaltung des gesamten Feldes an jeder
Abschlussgruppe rund `94,82 %` der auditiven Kontaktpaare, aber `0 %` der
visuellen Kontaktpaare als unmittelbare Endpunktpaare verfügbar.

### 3. Gemeinsame Abschlussgruppen

Bei drei gemeinsamen Audio-Video-Abschlussgruppen bleiben für beide Docks je
zwei von zwei lokalen Paaren unmittelbar benachbart. Der Unterschied entsteht
somit nicht aus der Dockanatomie, sondern aus der globalen Zeitordnung.

## Aktueller realer Lauf

Am 18. Juli 2026 wurde dieselbe passive Auswertung über drei vorab deklarierte
Ein-Sekunden-Fenster mit den verfügbaren Audio- und Videoeingängen wiederholt.
Ausgewertet wurden nur reduzierte Zustände und ihre Abschlusszeiten; Rohbild
und Roh-Audio wurden nicht gespeichert.

| Dock | Ereignisse | lokale Paare | global benachbart | unterbrochen |
|---|---:|---:|---:|---:|
| auditiv | 310 | 309 | 294 | 15 |
| visuell | 16 | 15 | 0 | 15 |

Es entstanden `326` Abschlussgruppen. Der auditive Anteil unmittelbarer Paare
betrug `95,15 %`, der visuelle Anteil `0 %`.

Die Abweichung von `293` zu `294` auditiven Paaren gegenüber der synthetischen
Kontrolle folgt aus der konkreten Ereignisreihenfolge. Die Richtungsdiagnose
bleibt gleich: Die langsamere visuelle Folge verliert unter dem Gegenmodell
jedes unmittelbare Endpunktpaar.

## Bezug zur aktuellen Runtime

Die gemeinsame MCM-Neuronenschicht wird atomar als Ganzes fortgeschrieben.
Wenn ein Dock in einem solchen Schritt keinen Kontakt liefert, erhält sein
Neuron `receptor_contact=None`. Würde jede Abschlussgruppe unmittelbar als
vollständiger Feldschritt verwendet, verdrängt daher ein dazwischenliegendes
Ereignis den vorherigen Rezeptorendpunkt aus der nächsten
`MCMNeuronDrive`-Wahrnehmung.

Der Audit führt dieses Gegenmodell nicht aus. Er misst nur dessen notwendige
Informationsvoraussetzung.

## Befund

```text
Nachbarschaft im Rezeptorprozess
!= Nachbarschaft in der globalen Abschlussfolge
```

Die Verfügbarkeit zweier unmittelbarer Endpunkte desselben Docks würde bei
einem Feldschritt je Abschlussgruppe von der relativen Rezeptorrate abhängen.
Die schnellere Modalität behält in der kontrollierten Ratenschiefe fast alle
Paare, während die langsamere Modalität alle verliert.

Damit ist die globale Abschlussgruppe als ungeprüfter vollständiger MCM-Takt
weiter falsifiziert. Gleichzeitig ist die lokale Dockfolge technisch
vorhanden; sie darf aber nicht durch einen neuen Dockpuffer, Sample-and-Hold
oder eine feste Gültigkeitsdauer in das Feld übertragen werden.

## Konsequenz für GF_001

`GF_001` bleibt geschlossen.

Nicht begründet sind:

- ein Feldschritt pro Rezeptorabschluss,
- modalitätseigenes Halten,
- Auswahl des jeweils neuesten Zustands,
- Interpolation oder Ratenangleichung,
- ein zusätzlicher Kontakt- oder Beziehungsspeicher.

Als nächste Informationsfrage bleibt, ob ein atomarer Feldvorschlag die seit
dem letzten Vorschlag neu abgeschlossenen Kontakte je Dock als begrenzte
Ereignismenge lesen kann, ohne sie zu fusionieren, zu gewichten oder als
dauerhaft gültig zu behandeln. Zuerst muss diese reine Übergabeform gegen
Reihenfolge-, Raten- und Auslassungsartefakte geprüft werden.

Feldkopplung, Topologie, Memory, Semantik, Reflexion und Selbstregulation
bleiben geschlossen.
