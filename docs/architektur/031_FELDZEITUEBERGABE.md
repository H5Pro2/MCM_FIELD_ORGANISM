# Feldzeitübergabe des gemeinsamen MCM-Feldes

## Zweck

Dieser Vertrag trennt reale Zeit, Rezeptorabschluss und Feldfortschritt. Er
legt noch keine Feldmechanik fest und gibt keinen fortlaufenden Livebetrieb
frei.

Die Live-Abnahme zeigt, warum diese Trennung notwendig ist: Auditive und
visuelle Rezeptoren schließen innerhalb derselben Organismusdauer verschieden
viele Zustände ab. Würde jeder Abschluss als gleich großer Feldschritt gelten,
prägte die technische Rezeptorrate den Organismuszustand.

## Drei getrennte Zeitrollen

### 1. Lokale Quellenstütze

Die Quellenstütze beschreibt ausschließlich, welcher neue Abschnitt des
lokalen Weltkontakts kausal in einen Rezeptorzustand eingegangen ist.

- Sie gehört zum jeweiligen Rezeptorprozess.
- Ein rollendes Analysefenster darf nicht vollständig als neue Quellenstütze
  ausgegeben werden, wenn nur ein kleiner neuer Abschnitt hinzugekommen ist.
- Überlappende Analysegeschichte darf nicht mehrfach als neuer Weltkontakt
  wirken.
- Eine unbekannte Quellenstütze darf nicht aus Bildrate, Hopgröße oder
  Abschlussabstand erfunden werden.

### 2. Rezeptorabschluss

Der Abschlusszeitpunkt bezeichnet, wann ein unveränderlicher
Rezeptorzustand für seinen Dock verfügbar wird.

- Vor seinem Abschluss darf der Zustand nicht auf das Feld wirken.
- Gleichzeitige Abschlüsse bilden eine ungeordnete atomare Gruppe.
- Die Anzahl der Abschlüsse ist keine Organismusdauer und keine Feldstärke.
- Ein fehlender Abschluss bedeutet weder Nullkontakt noch fortbestehenden
  Kontakt.

### 3. Organismuszeit des Feldes

Die Organismuszeit beschreibt die tatsächlich verstrichene Dauer des
gemeinsamen Feldes.

- Sie schreitet unabhängig von der Anzahl eintreffender Rezeptorzustände fort.
- Rezeptorabschlüsse dürfen diese Zeit nur in technische Auswertungsintervalle
  teilen.
- Eine zusätzliche Auswertungsgrenze ohne neuen Rezeptorkontakt darf den
  physikalisch gleichen Feldverlauf nicht verändern.
- Der ganzzahlige Neuronentick bleibt technische Zustandsidentität und darf
  nicht als Dauer oder Entwicklungsmenge gelesen werden.

## Kausale Übergabe

Der zulässige Ablauf lautet konzeptionell:

```text
abgeschlossener Feldzustand am Zeitpunkt t0
+ verstrichene Organismusdauer t0 -> t1
+ alle bei t1 neu verfügbaren lokalen Rezeptorzustände
-> ein atomarer Feldvorschlag für t1
```

Alle Neuronen lesen denselben abgeschlossenen Vorzustand und dieselbe
verstrichene Organismusdauer. Nur Docks mit einem bei dieser Grenze neu
abgeschlossenen Zustand tragen aktuellen Rezeptorkontakt. Andere Docks bleiben
anatomisch vorhanden, liefern aber weder einen gehaltenen noch einen
eingesetzten Nullwert.

Eine Abschlussgrenze ist damit eine technische Berechnungsgrenze, kein
eigenständiger organischer Zeitschritt. Ob und wie der Feldzustand während der
verstrichenen Dauer reagiert, muss eine später geprüfte lokale Feldmechanik
tragen.

## Verbindliche Invarianten

Vor einer Runtimefreigabe müssen mindestens diese Gegenprüfungen bestehen:

1. **Zeitteilungsinvarianz**  
   Derselbe kontaktfreie Zeitraum erzeugt unabhängig von zusätzlichen leeren
   Auswertungsgrenzen denselben Endzustand.
2. **Quellenstützeninvarianz**  
   Derselbe vollständig belegte Weltkontakt erzeugt bei dichterer oder
   gröberer verlustfreier Unterteilung denselben Endzustand.
3. **Abschlussreihenfolge**  
   Zustände mit identischem Abschlusszeitpunkt wirken unabhängig von
   technischer Iterationsreihenfolge.
4. **Ratenentkopplung**  
   Eine höhere technische Ausgaberate ohne zusätzliche Quellenwirkung darf
   keine stärkere Feldwirkung erzeugen.
5. **Abwesenheit**  
   Eine Modalität ohne neuen abgeschlossenen Zustand erzeugt weder Halten noch
   Nullkontakt und blockiert andere Modalitäten nicht.
6. **Kausalität**  
   Kein Zustand wirkt vor seinem Abschluss; spätere Zustände verändern keinen
   bereits abgeschlossenen Feldzustand rückwirkend.
7. **Wiederaufnahme**  
   Snapshot und Wiederherstellung setzen Organismuszeit und nächste
   Abschlussgrenze ohne Sprung, Doppelwirkung oder verlorenen Kontakt fort.

## Nicht zulässige Abkürzungen

- ein vollständiger gleich großer Feldschritt je Sensorereignis,
- gemeinsame Fenster- oder Hopgrößen,
- Sample-and-Hold oder ein letzter gemeinsamer Kontaktpuffer,
- Interpolation fehlender Rezeptorzustände,
- globale Ratennormalisierung,
- Modalitätsgewichte, Prioritäten oder Gewinner,
- Auswahl eines repräsentativen Frames aus mehreren Zuständen,
- Gleichsetzung von technischem Read, Analysefenster und Quellenstütze,
- neue Memory-, Bedeutungs- oder Topologievariablen zur Lösung des Zeitproblems.

## Konsequenz für die aktuellen Adapter

Der Audioadapter besitzt Analysefenster, Hopfortschritt und Abschlusszeit. Vor
einer Feldübergabe muss ausdrücklich ausgewiesen werden, welcher neu
hinzugekommene Quellenabschnitt kausal getragen wird.

Der Videoadapter besitzt Bildinhalt und gemessene technische Read-Zeit, aber
noch keine hinreichend belegte zeitliche Quellenstütze des Bildes. Aus der
gemeldeten Bildrate oder dem Abstand zweier abgeschlossener Analysen darf sie
nicht abgeleitet werden.

Solange eine Quellenstütze nicht belegt ist, bleibt der jeweilige Livepfad auf
passive Zeit- und Belegungsaudits begrenzt.

## Bereits vorhandene passive Träger

Die Vorarbeiten haben die Transportseite bereits weitgehend geklärt:

- `adapter_timing_capability` trennt exponierte Backendzeiten von tatsächlich
  verwendbarer Quellenzeit;
- `field_time_partition` zerlegt einen Beobachtungshorizont lückenlos an
  Abschlussgrenzen, ohne daraus Feldschritte zu machen;
- `receptor_proposal_handoff_audit` ordnet alle reduzierten Dockzustände
  verlustfrei vorgegebenen Vorschlagsspannen zu;
- grobe und feine Segmentierungen rekonstruieren dieselben vollständigen
  docklokalen Folgen;
- die aktuelle `ReceptorDistribution` und `MCMFieldPerception` können dagegen
  je Dock nur einen gegenwärtigen skalaren Kontakt tragen.

Die offene Grenze lautet daher:

```text
verlustfrei übergebene zeitliche Dockfolge
!= ein skalarer aktueller Dockkontakt
```

Eine Auswahl, Mittelung oder Endpunktprojektion würde Information entfernen.
Ein Feldschritt je Element würde die technische Ereignisdichte zum
Feldfortschritt machen.

## Freigabestatus

```text
Architekturvertrag:          E0 / CONTRACT_ONLY
Feldzeit-Runtime:            nicht freigegeben
Kontakt-Halten:              nicht freigegeben
Ratennormalisierung:         nicht freigegeben
organische Feldentwicklung:  nicht behauptet
```

Der nächste technische Schritt ist keine neue Dynamik. Zuerst wird ein
darstellungsoffener Vertrag für einen **transienten lokalen Dockverlauf**
formuliert. Er muss die bereits verlustfrei übergebene Folge nur während eines
atomaren Feldvorschlags zugänglich machen, ohne sie im Neuron, Feldsnapshot
oder Memory zu speichern und ohne eine Leser- oder Verdichtungsregel
vorzugeben.

Erst wenn dieser Eingangsvertrag gegen Segmentierung, Reihenfolge, Abwesenheit,
Snapshotgrenze und Observer-Rückwirkung abgesichert ist, darf über seine
technische Anbindung an den Neuronenantrieb entschieden werden.
