# Methodik 026: Feldfolgen-Gate vor sensorischer Selbstregulation

## 1. Anlass

Befund 030 zeigt, dass die vorhandenen Rezeptoren nach verschiedenen
Belastungs- und Erholungsgeschichten bei identischer Abschlussprobe exakt
kollidieren. Die Rezeptorabbildungen sind geschichtslos.

Aus diesem Funktionsmangel folgt jedoch nicht, dass eine automatische
Gain-Regel, ein Ermüdungsintegrator oder eine neue Rezeptorspur gebaut werden
sollte.

## 2. Kritische Abhängigkeit

Der Grenzvertrag für sensorische Selbstregulation nennt vier mögliche lokale
Ursachen:

```text
lokale Rezeptorgeschichte
+ lokale Feldfolge
+ lokal verfügbare Ressource
+ reduzierter Weltkontakt
→ möglicher späterer lokaler Aufnahmeunterschied
```

Davon sind gegenwärtig nur Rezeptorgeschichte und reduzierter Weltkontakt
technisch darstellbar. Eine kausale lokale Feldfolge und eine wirksame lokale
Ressourcenordnung sind noch nicht implementiert.

## 3. Tatsächlicher Architekturstand

Vorhanden sind:

- feste passive Rezeptorabbildungen,
- lokale Aktivierung und lokaler Nachhall,
- eine unveränderliche MCM-Neuronenhülle,
- passive Beobachtung lokaler Aktivierungs- und Nachhallunterschiede,
- ein E0-Vertrag für gemeinsame lokale Ressourcen.

Nicht vorhanden sind:

- eine begründete lokale MCM-Übergangsfunktion,
- eine kausal wirksame Feldfolge,
- eine gemessene lokale Wirkungskapazität,
- eine spätere Rückwirkung vom Feld auf die Rezeptoraufnahme.

## 4. Warum B3 bis B5 jetzt nicht genügen

Folgende Modelle könnten bereits heute als isolierte Filter programmiert
werden:

```text
B3: automatische Gain-Regel
B4: lokaler Ermüdungs-/Erholungsintegrator
B5: mehrere feste Leaky-Zeitskalen
```

Jedes dieser Modelle würde seine Geschichte aus dem Rezeptoreingang selbst
erzeugen. Ein späterer Unterschied wäre damit konstruktiv eingebaut:

```text
andere Eingangsgeschichte
→ anderer Filterzustand
→ andere Abschlussausgabe
```

Das wäre ein gültiger Filterbefund, aber keine Teilnahme des Rezeptors an einem
MCM-Feldorganismus.

Ein solcher Lauf würde den Forschungsfokus von der Feldwirkung auf
Eingangsnachregelung verschieben.

## 5. Feldfolgen-Gate

Sensorische Selbstregulation darf erst erneut geöffnet werden, wenn alle
folgenden Voraussetzungen unabhängig getragen sind:

### G1: Kausal entstandene lokale Feldfolge

Eine lokale Feldlage muss aus früherem Weltkontakt und der unveränderten
MCM-Zeitfolge entstanden sein. Sie darf nicht als Klasse, Zielwert oder
Versuchslabel eingesetzt werden.

### G2: Nichtredundanz zum Rezeptoreingang

Zwei Zweige müssen dieselbe lokale Rezeptorgeschichte besitzen, aber
unterschiedliche lokale Feldfolgen tragen.

```text
gleiche lokale Rezeptorgeschichte
+ unterschiedliche kausal entstandene Feldumgebung
→ unterschiedliche lokale Feldfolge
```

### G3: Spätere kausale Feldwirkung

Die unterschiedliche Feldfolge muss unter einer identischen späteren Probe
eine unterschiedliche lokale Feldantwort verursachen. Passive Lesbarkeit
allein genügt nicht.

### G4: Trennung von einfachen Feldbaselines

Die Wirkung darf nicht vollständig erklärt werden durch:

- unabhängigen Leaky-Nachhall,
- festen Ein-Schritt-Puffer,
- feste Rekurrenz,
- Diffusion oder Nachbarmittelung,
- statisches Clipping,
- technische Iterationsreihenfolge.

### G5: Erst danach Rezeptorfrage

Erst wenn G1 bis G4 tragen, darf geprüft werden, ob diese Feldfolge eine spätere
Rezeptoraufnahme lokal mitprägt und ob dadurch eine konkrete Feldfunktion
erhalten wird.

## 6. Stärkstes Gegenargument

Auch eine feste Rückkopplung von einem Feldwert auf einen Rezeptorgain könnte
G1 bis G3 formal erfüllen.

Deshalb wären selbst nach geöffnetem Gate zusätzliche Baselines notwendig:

```text
B6: feste lokale Feldwert-zu-Gain-Abbildung
B7: lokale Ressourcen-Normalisierung
```

Eine Feldrückkopplung wäre nicht allein deshalb organisch, weil ihre Eingabe
aus dem MCM-Feld stammt.

## 7. Stopplinie

Der sensorische Selbstregulationszweig bleibt geschlossen.

Nicht freigegeben sind:

- B3 bis B7 als Organismus-Runtime,
- Empfindlichkeitszustand,
- Feldwert-zu-Gain-Regel,
- Rezeptorrückschreibung,
- lokale oder globale Zielpegel,
- adaptive Schwellen,
- Geräte- oder Betriebssystemsteuerung.

## 8. Entscheidung

Der nächste Forschungsschritt liegt nicht am Rezeptor, sondern im
sensorspezifischen MCM-Feld:

> Kann eine bereits passiv lesbare lokale Feldasymmetrie eine spätere lokale
> Feldwirkung tragen, die über Projektion, Nachhall, festen Puffer, Rekurrenz
> und Diffusion hinausgeht?

Die räumliche Nachhallorientierung aus Befund 020 bietet dafür eine vorhandene
kontrollierte Ausgangslage. Noch fehlt ihre kausale Folgewirkung.

## 9. Evidenzstatus

```text
Geschichtslosigkeit der festen Rezeptoren: E1
passive Lesbarkeit lokaler Feldasymmetrie: E2
kausale lokale Feldfolge:                  E0
sensorische Selbstregulation:              E0
Feldintelligenz:                           E0
```

## 10. Bester nächster Schritt

Vorregistriert werden muss eine minimale lokale Feldfolgen-Kollisionsprüfung.
Sie setzt an der bereits lesbaren räumlichen Nachhallorientierung an und prüft
jede mögliche Folgewirkung gegen Projektion, unabhängigen Nachhall, festen
Puffer, feste Rekurrenz und Diffusion.

Bis diese Prüfung eine nichtredundante Feldfunktion trägt, bleibt die
Rezeptorseite unverändert.
