# Technische Feldeingangs-Kapazitätsfalsifikation 017

## Status

Passive Schnittstellenprüfung vor `GF_001`.

Der Audit prüft, ob die mit Audit 016 verlustfrei bewahrten variablen
Dockfolgen durch die heute vorhandenen Verträge direkt in genau einen atomaren
MCM-Feldvorschlag eintreten können.

Es wird keine neue Repräsentation ergänzt und keine Reduktionsregel ausgewählt.

## Geprüfte Kapazitätsgrenzen

### 1. Einzelner Frame

Ein einzelner abgeschlossener `ReceptorContactFrame` wird vom
`ReceptorDistributor` angenommen. Herkunft, Geometrie, Träger und Werte
bleiben erhalten.

### 2. Mehrere Frames desselben Docks

Zwei auditive Frames innerhalb derselben `ReceptorDistribution` werden mit
der bestehenden Invariante abgewiesen:

```text
duplicate modality frame: auditory
```

Die Verteilung erlaubt damit höchstens einen Frame je Modalität.

### 3. Folge als Neuronenkontakt

`MCMFieldPerception.receptor_contact` akzeptiert einen normalisierten Skalar.
Eine Folge wie `(0,1; 0,9)` wird abgewiesen:

```text
receptor_contact must be numeric
```

Die lokale Wahrnehmung besitzt keinen zeitlich geordneten Kontaktträger.

### 4. Serielle Einzelübergabe

Zwei Frames können als zwei getrennte Verteilungen dargestellt werden. Unter
dem aktuellen `SharedMCMField.advance`-Vertrag entspricht jede Verteilung aber
einem vollständigen atomaren Fortschritt der gemeinsamen Neuronenschicht.

```text
zwei Dockframes
-> zwei vollständige Feldfortschritte
```

Dieser Weg kehrt zur bereits falsifizierten Kopplung von Rezeptorrate und
Feldfortschritt zurück.

## Endpunktkollision

Zwei unterschiedliche Folgen werden bei identischem vorherigem
Neuronenzustand kontrolliert:

```text
Folge A: 0,1 -> 0,9
Folge B: 0,8 -> 0,9
```

Wird nur der aktuelle Endpunkt `0,9` eingesetzt, sind beide
`MCMNeuronDrive`-Eingänge exakt gleich. Der vorherige Aktivierungs- und
Nachhallzustand wurde dabei bewusst identisch gehalten.

Der Befund lautet eng:

```text
gleicher vorheriger Neuronenzustand
+ gleicher gewählter Endpunkt
!= erhaltene innere Dockfolge
```

Er behauptet nicht, dass der vorhandene Neuronenzustand grundsätzlich keine
Geschichte tragen kann. Er zeigt, dass die innerhalb derselben
Vorschlagsspanne neu entstandene Folge durch eine reine Endpunktauswahl
verschwindet.

## Befund

Keine der heutigen direkten Schnittstellen stellt eine variable Folge
mehrerer Zustände desselben Docks in einem atomaren Feldvorschlag dar:

| Gegenmodell | Ergebnis |
|---|---|
| mehrere Frames in einer Verteilung | abgewiesen |
| Kontaktfolge im Skalarfeld | abgewiesen |
| serielle Einzelverteilungen | ein vollständiger Feldfortschritt je Frame |
| nur letzter Endpunkt | unterschiedliche Folgen kollidieren |

Damit ist nicht die verlustfreie Übergabemenge aus Audit 016 widerlegt,
sondern die Kapazität ihrer heutigen Feldschnittstelle.

## Kritische Begrenzung

Der Audit beweist nicht, dass jede denkbare zeitliche Feldrepräsentation
unmöglich ist. Reelle Skalare könnten mit einer künstlichen Kodierung beliebig
komplexe Information verstecken; eine solche Kodierung wäre jedoch keine
vorhandene MCM-Mechanik und würde die organische Entwicklungsfrage nur in
einen Decoder verlagern.

Ebenfalls nicht geprüft sind:

- eine explizit zeittragende lokale Feldwahrnehmung,
- kontinuierliche Rezeptor-Feld-Wirkung,
- asynchrone lokale Wirkung ohne vollständigen Feldfortschritt,
- eine organisch entstehende zeitliche Verdichtung.

## Konsequenz für GF_001

`GF_001` bleibt geschlossen.

Nicht freigegeben sind:

- Auswahl des letzten, stärksten oder mittleren Frames,
- versteckte Sequenzkodierung in einem Skalar,
- ein vollständiger Feldschritt je Sensorzustand,
- eine Sequenzvariable als vorschnelles Memory,
- Feldkopplung, Topologie oder Lernen.

Der nächste Schritt muss vor jeder Implementierung zwei minimale
Architekturträger gegeneinander abgrenzen:

1. eine zeittragende lokale Rezeptorwahrnehmung innerhalb eines atomaren
   Feldvorschlags,
2. lokale asynchrone Rezeptorwirkung bei davon getrennter gemeinsamer
   Feldfortschreibung.

Beide müssen dieselbe reduzierte Dockfolge bewahren, dürfen keine feste
Verdichtung vorgeben und müssen gegen Rezeptorratenabhängigkeit geprüft
werden.

Semantik, Reflexion, Offline-Erholung und Selbstregulation bleiben geschlossen.
