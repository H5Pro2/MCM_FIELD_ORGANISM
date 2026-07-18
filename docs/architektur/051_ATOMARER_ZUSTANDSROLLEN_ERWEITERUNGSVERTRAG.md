# Atomarer Zustandsrollen-Erweiterungsvertrag

## Status

Verbindlicher Architekturvertrag auf `E0 / CONTRACT_ONLY`.

```text
fehlende kausale Rolle:        funktional begründet
atomare Einbindungsstelle:     bestimmt
digitale Darstellung:         offen
Updategleichung:               offen
Runtime-Erweiterung:           gesperrt
```

Dieser Vertrag folgt aus der
[lokalen Ereignisquellgrenze](050_LOKALE_EREIGNISQUELLGRENZE.md)
und dem
[darstellungsoffenen Memory-Substratvertrag](048_DARSTELLUNGSOFFENER_MEMORY_SUBSTRATVERTRAG.md).
Er beschreibt, wie eine spätere Memory-Rolle technisch zum selben
Organismuszustand gehören müsste. Er implementiert diese Rolle nicht.

## Zweck

Die aktuelle Runtime besitzt bereits alle notwendigen lokalen Weltquellen,
aber nur `activation` und `afterimage` als fortgeschriebene dynamische
Zustände.

Eine spätere Memory-Rolle darf deshalb weder als Datenbank neben dem Feld noch
als Observerprodukt hinter dem Feld entstehen. Sie müsste Bestandteil
desselben atomaren Neuronenzustands sein.

Der Vertrag beantwortet ausschließlich:

```text
Wo liegt die Rolle?
Wann wird sie gelesen und veröffentlicht?
Welche Quellen darf sie grundsätzlich erhalten?
Wie bleibt der heutige Nullpfad exakt erhalten?
Wie wird versteckter Zustand ausgeschlossen?
```

Er beantwortet nicht, wie Memory digital gebildet wird.

## 1. Zugehörigkeit zum lokalen Organismuszustand

Eine spätere Memory-Rolle muss logisch jedem technisch gleichartigen
MCM-Neuron als lokale Zustandsmöglichkeit angehören.

Das bedeutet nicht:

- ein unabhängiger Memory-Skalar pro Neuron;
- ein fester Speicherplatz pro Erfahrung;
- ein Memory-Neuron;
- eine vorgegebene Beziehung zu Nachbarn;
- eine modality-spezifische Gedächtnisschicht.

Mehrere lokale Rollenanteile dürfen später gemeinsam eine verteilte
Feldprägung tragen. Ihre konkrete Form und Zusammenarbeit müssen aber aus
derselben lokalen Naturbedingung hervorgehen.

## 2. Vorzustand

Am Beginn eines Feldfortschritts muss der vollständige abgeschlossene lokale
Zustand verfügbar sein:

```text
activation(t)
afterimage(t)
opake Memory-Rolle(t)
```

Die Memory-Rolle darf nicht aus einem Prozesscache, einer Closure, einem
Singleton oder einer externen Datei ergänzt werden.

Ist die Rolle digital nicht vollständig im abgeschlossenen Neuronenzustand
enthalten, gehört sie nicht zum Organismusfeld.

## 3. Zulässige kausale Quellen

Eine spätere Bildungsregel darf grundsätzlich nur Quellen lesen, die bereits
an der atomaren Neuronengrenze vorliegen:

- den eigenen abgeschlossenen Vorzustand;
- lokale Aktivierungs- und Nachhallproben des abgeschlossenen Vorfeldes;
- gegenwärtigen lokalen Rezeptorkontakt;
- den eigenen transienten Dockverlauf innerhalb des Feldschritts;
- die abgeschlossene Organismuszeitspanne;
- den eigenen vorherigen Memory-Rollenanteil.

Technische Identitäten dürfen Adressierung und Validierung ermöglichen. Sie
dürfen nicht als inhaltlicher Zahlenwert, Gewicht, Richtung oder
Erfahrungslabel in die Bildungsregel eingehen.

Unzulässig sind insbesondere:

- Neuronenindex als Gewichtsquelle;
- Modality-ID als Memory-Bedeutung;
- Tickzahl als Erfahrungsstärke;
- Snapshot-ID als Erinnerung;
- Welt-, Objekt-, Episoden- oder Musterlabel;
- Observerausgabe;
- globaler Feldscore oder Gewinner;
- Reward, Zielzustand oder Solltopologie;
- nicht serialisierter Zufallszustand.

## 4. Gemeinsamer atomarer Vorschlag

Eine spätere vollständige Transition müsste logisch gemeinsam vorschlagen:

```text
activation(t+1)
afterimage(t+1)
opake Memory-Rolle(t+1)
```

Alle drei Vorschläge entstehen aus demselben abgeschlossenen Vorzustand und
denselben kausal zulässigen Quellen. Erst wenn alle Neuronen gültige
Vorschläge geliefert haben, wird die vollständige nächste Schicht
veröffentlicht.

Eine neu vorgeschlagene Memory-Rolle darf im selben Feldschritt nicht erneut
als eigene Bildungsursache gelesen werden. Ihre früheste eigenständige
Rückwirkung liegt im folgenden Feldfortschritt.

Damit bleibt ausgeschlossen:

```text
neue Prägung(t+1)
-> sofortige erneute Selbstverstärkung innerhalb desselben Schritts
```

## 5. Fehleratomarität

Scheitert ein Vorschlag, bleibt die gesamte vorherige Schicht unverändert.

Eine spätere Memory-Rolle darf nicht teilweise fortgeschrieben werden, wenn:

- ein anderes Neuron ungültig wird;
- ein Rezeptorvorschlag unvollständig ist;
- eine Zeitspanne nicht passt;
- ein Wert den endlichen Darstellungsbereich verlässt;
- Snapshotvalidierung fehlschlägt.

Teilweise Memory-Updates würden eine technische Reihenfolge als
Erfahrungsgeschichte einschreiben.

## 6. Nullzustand

Die spätere Rolle benötigt einen eindeutig nachgewiesenen Nullzustand.

Im Nullzustand gilt funktional:

```text
gleicher Vorzustand von activation und afterimage
+ gleiche lokale Weltursachen
+ Memory-Rolle im Nullzustand
-> exakt gleiche activation- und afterimage-Fortsetzung
   wie in der heutigen Runtime
```

Der Nullzustand ist nicht:

- fehlender Weltkontakt;
- Nullaktivierung;
- leerer Snapshot;
- gelöschte Erfahrung;
- frei interpretierbarer Standardwert.

Eine spätere Schemaerweiterung kann den Byteinhalt eines Snapshots verändern.
Die kausale Feldfortsetzung im Nullzustand muss dennoch bitgenau der heutigen
Runtime entsprechen.

## 7. Sichtbarkeit im lokalen Feld

Die Memory-Rolle gehört zum Neuronenzustand. Daraus folgt noch nicht, dass ihr
digitaler Inhalt unmittelbar als neue Nachbarprobe verteilt werden darf.

Die heutige lokale Feldprobe trägt ausschließlich:

```text
activation
afterimage
relative technische Position
```

Eine direkte zusätzliche `memory`-Probe würde bereits festlegen:

- dass Memory über dieselbe Anatomie wie Aktivierung koppelt;
- welche Nachbarn den Zustand lesen;
- in welcher Richtung er wirkt;
- dass die digitale Memory-Darstellung feldöffentlich ist.

Diese Festlegungen sind nicht begründet. Bis zu einem eigenen Kausalnachweis
bleibt direkte Memory-Abtastung gesperrt.

Eine spätere Memory-Rolle dürfte zunächst nur über die eigene folgende lokale
Zustandsbildung kausal wirken. Ob und wie daraus verteilte Feldwirkung
entsteht, muss die gemeinsame Feldentwicklung zeigen und separat geprüft
werden.

## 8. Keine rekursive Wahrnehmungsgeschichte

Die vorherige `perception` bleibt technischer Bestandteil des abgeschlossenen
Snapshots. Sie darf nicht pauschal als Memory-Eingabe rekursiv fortgeschrieben
werden.

Sonst entstünde ein wachsendes oder verschachteltes Wahrnehmungsarchiv:

```text
perception(t)
enthält perception(t-1)
enthält perception(t-2)
...
```

Zulässig sind nur die gegenwärtig am Drive offengelegten lokalen
Quellgrößen. Eine spätere Darstellung muss ihre eigene endliche
Zustandsgrenze besitzen.

## 9. Snapshot und technische Fortsetzung

Wenn eine Memory-Rolle später implementiert wird, muss der Snapshot den
vollständigen kausalen Zustand enthalten.

Erforderlich wären:

- eine explizite Snapshot-Schemaversion;
- vollständige kanonische Serialisierung;
- strikte Validierung ohne unbekannte Zusatzfelder;
- identischer Digest nach Serialisieren und Wiederherstellen;
- identische Fortsetzung nach Snapshotgrenze;
- keine Wirkung des Serialisierungsvorgangs selbst.

Eine Migration eines heutigen Schema-v1-Snapshots dürfte eine spätere Rolle
nur ausdrücklich in ihren nachgewiesenen Nullzustand setzen. Sie dürfte keine
Erfahrung erfinden oder aus alten Diagnosefeldern rekonstruieren.

Snapshot-Fortsetzung bleibt technische Rekonstruktion. Sie beweist keine
ununterbrochene Organismuszeit nach einem Ausschalten.

## 10. Observergrenze

Der Observer darf einen vollständig abgeschlossenen Zustand auswerten. Er
darf nicht:

- die Memory-Rolle bilden;
- einen Vorschlag auswählen;
- Relevanz oder Gewinner bestimmen;
- Werte normalisieren oder zurückschreiben;
- eine Weltfinalisierung auslösen;
- versteckte Zustände für den nächsten Takt bereithalten.

Observer an, aus, wiederholt oder in anderer Reihenfolge muss dieselbe
Runtimefortsetzung ergeben.

## 11. Forschungsinterventionen

Eine spätere digitale Darstellung muss kontrollierte Forschungseingriffe
ermöglichen:

1. Memory-Rollenanteil zwischen zwei sonst gleichen lokalen Zweigen tauschen;
2. Memory-Rollenanteile exakt gleichsetzen;
3. den nachgewiesenen Nullzustand einsetzen;
4. schnelle Zustände unabhängig angleichen;
5. Bildungsquelle entfernen, ohne die spätere Probe zu verändern;
6. Wirkpfad unterbrechen, ohne die frühere Bildung zu löschen;
7. Snapshot vor und nach der Intervention vergleichen.

Diese Eingriffe gehören nicht zur Organismus-Runtime. Sie dienen nur der
Kausalprüfung.

## 12. Keine vorweggenommene Kopplung

Der Vertrag gibt nicht vor:

- ob die Rolle skalar, vektoriell, räumlich oder anders dargestellt wird;
- ob mehrere Neuronen gemeinsam eine Prägung tragen;
- ob eine spätere Beschreibung als Beziehung oder Topologie sinnvoll ist;
- wie Stärke, Dauer oder Lösung entstehen;
- welche Erfahrung später semantisch resoniert;
- ob eine Feldfähigkeit oder Entwicklung entsteht.

Insbesondere werden nicht freigegeben:

- feste oder adaptive Kanten;
- `continuity` oder `allocation`;
- lokale Ressourcenwerte;
- Übergangszähler;
- Leaky-Memory als Kandidat;
- Rang- oder Gewinnerregeln;
- Reservoir oder Historienarchiv.

## 13. Erforderliche Nullprüfungen einer späteren Hülle

Noch bevor eine Bildungsregel untersucht werden dürfte, müsste eine reine
technische Hülle mindestens zeigen:

```text
N1  Nullrolle verändert activation und afterimage nie
N2  Nullrolle verändert Reihenfolge- und Geometrieneutralität nicht
N3  fehlgeschlagene Vorschläge hinterlassen keinen Teilzustand
N4  Observer bleibt vollständig neutral
N5  Snapshot-Rundlauf ist vollständig und deterministisch
N6  alte Schema-v1-Zustände migrieren nur in den Nullzustand
N7  transiente Rezeptorverläufe werden nicht persistiert
N8  keine direkte Memory-Nachbarprobe entsteht
```

Diese Prüfungen würden nur die Zustandsanatomie absichern. Sie wären kein
Memory-Befund.

## Freigabegrenze

```text
lokale Zugehörigkeit festgelegt:       ja
atomare Vorschlagsgrenze festgelegt:   ja
Nullverhalten festgelegt:              ja
Snapshotpflicht festgelegt:            ja
Observergrenze festgelegt:              ja
direkte Memory-Nachbarprobe erlaubt:   nein
digitale Darstellung gewählt:          nein
Updategleichung gewählt:                nein
technische Hülle freigegeben:           nein
Runtime-Erweiterung freigegeben:         nein
```

## Nächster Schritt

Der
[Zulässigkeitsaudit der opaken Nullzustandshülle](052_ZULAESSIGKEITSAUDIT_OPAKE_NULLZUSTANDSHUELLE.md)
ist abgeschlossen. Eine digitale Hülle kann nicht zugleich vollständig opak
und darstellungsneutral sein. Selbst ein leerer Platzhalter würde lokalen
Slot, Serialisierung und Migrationspfad vorgeben, ohne eine Memory-Funktion
prüfen zu können.

Die Hülle wird deshalb nicht implementiert. Der anschließende Vertrag der
[kausalen Zustandsäquivalenz](053_KAUSALE_ZUSTANDSAEQUIVALENZ.md)
liegt inzwischen vor. Erst eine nachgewiesene zukünftige Feldunterscheidung
kann den notwendigen Informationsgehalt einer späteren Darstellung begrenzen.

Als Nächstes wird geprüft, wodurch eine solche Unterscheidung aus der
Weltstruktur selbst relevant wird, statt nur durch einen eingebauten Leser.
