# MINI_DIO-Zeitkontext: funktionale Reduktion und Substratwege

> **Aktuelle Einordnung:** Die Rekonstruktion bleibt als Quellenarbeit
> erhalten. Der
> [Reaudit nach Lauf 194](MINI_DIO_ZEITKONTEXT_REAUDIT_NACH_LAUF_194.md)
> begrenzt ihren Befund auf passive relationale Trajektorienwiederkehr mit
> variabler Beobachtungsdauer. Eine relative Feldzeit ist damit noch nicht
> nachgewiesen.

## Zweck

Dieses Dokument reduziert die vorhandenen MINI_DIO-Befunde 2110, 2111, 2114
und 2126 auf die kleinsten fuer `MCM_FIELD_ORGANISM` nutzbaren Funktionen. Es
waehlt noch keine Gleichung und erweitert keine Runtime.

## Rekonstruierte MINI_DIO-Funktion

Der staerkste innere Zeitkontext bestand nicht aus `MiniTemporalTracker`,
Weltzeit oder gespeicherten Episoden. Er entstand in der passiven Auswertung
des kontinuierlichen Feldes aus:

```text
eigene Feldordnung im vorherigen Zustand
gegen
eigene Feldordnung im aktuellen Zustand
-> gerichtete relationale Formaenderung
-> erste exakte Wiederkehr einer bereits durchlaufenen Ordnung
-> variable Zyklusdauer
```

Konkret wurden bei zwoelf Neuronen 66 paarweise Aktivierungsrangrelationen
verglichen. Aenderungen zwischen `kleiner`, `gleich` und `groesser` bildeten
ein staerkenormiertes Uebergangsprofil. Die erste exakte Rangwiederkehr schloss
den Zyklus ohne feste Tickzahl.

Damit waren drei getrennte Funktionen getragen:

1. **Feldspur:** Vergangenheit wirkte kurz ueber den Nachhall weiter.
2. **Intrinsische Eigenform:** Aufeinanderfolgende eigene Feldzustaende
   enthielten eine resetfrei rekonstruierbare relative Bewegungsform.
3. **Variable Eigenzeit:** Eine tatsaechliche Formwiederkehr statt einer festen
   Dauer bestimmte den Abschluss eines Zyklus.

Nicht getragen waren eine feldinterne Nutzung dieser Form, Memory,
Relevanzauswahl, Semantik oder eine spaetere Rueckwirkung.

## Was funktional uebertragbar ist

Die folgenden Funktionen sind fuer die neue Architektur richtungsweisend:

- Zeitkontext wird aus Zustandsbeziehungen, nicht aus Sekunden abgeleitet.
- Die eigene Feldbewegung ist die Quelle; eine parallele Nullwelt ist nicht
  Teil des Organismus.
- Ein innerer Abschnitt kann durch ein Feldereignis statt durch feste Dauer
  begrenzt werden.
- Die relative Form ist wichtiger als die absolute Bewegungsmenge.
- Neue Erfahrung kann die kurze Quellform abschwaechen oder ueberformen.
- Form, zeitlicher Abschluss und spaetere Relevanz sind getrennte Funktionen.

## Was nicht uebertragen werden darf

Die konkrete Rangmechanik ist kein neutraler Runtime-Kandidat:

- globale Paarvergleiche aller Neuronen waeren ein zentraler Observer;
- die verglichenen Mitglieder waren durch feste Neuronenindizes bestimmt;
- die alte serielle Indexrichtung beeinflusste die Feldbewegung;
- exakte Rangwiederkehr setzt eine observerseitig bewahrte Zustandsmenge
  voraus;
- das Uebergangsprofil war eine Diagnose und wirkte nicht ins Feld zurueck;
- Welt- und Kontaktgrenzen waren teilweise von aussen bereitgestellt.

Die Aufgabe lautet daher nicht, Rangprofile oder Rangzyklen in die Runtime zu
kopieren. Gesucht wird ein lokales physisches Gegenstueck ihrer Funktion.

## Abgleich mit der heutigen MCM-Architektur

### Bereits vorhanden

- eine atomare, reihenfolgeneutrale Schichtfortschreibung;
- eigener lokaler Vorzustand aus `activation` und `afterimage`;
- lokale Feldproben aus dem vollstaendig abgeschlossenen Vortakt;
- relative Probenpositionen in gemeinsamer Geometrie;
- reale Organismusdauer und kausale Reihenfolge;
- lokale Diffusionswirkung und schneller Nachhall;
- Snapshot und exakte technische Fortsetzung.

### Noch nicht vorhanden

- eine langsame lokale Zustandsrolle jenseits von Aktivierung und Nachhall;
- eine feldinterne Form, die nach Angleichung schneller Rollen fortwirkt;
- eine durch Geschichte veraenderliche Aufnahme- oder Leitbedingung;
- eine lokale, nicht indexgebundene Ereignisgrenze;
- funktionale Loesung und erneute Praegbarkeit derselben Kapazitaet.

Der bestehende momentane Feldfluss ist eine reale Schreibursache, aber kein
Memory-Zustand: Er ist vollstaendig aus aktueller Aktivierung, fester
Nachbarschaft und Reaktionszeit ableitbar.

## Drei konkurrierende Substratwege

Die Kandidaten sind Naturhypothesen, keine freigegebenen Implementierungen.
Sie muessen mit derselben Testfamilie und gegen einfachere Baselines antreten.

### H1: lokal deformierbare Feldaufnahme

**Funktionsannahme:** Wiederholte lokale Feldbeanspruchung kann die spaetere
Aufnahme derselben Feldregion veraendern. Die Veraenderung liegt weder im
aktuellen Eingang noch im schnellen Nachhall.

**Anschluss an MINI_DIO:** Die wiederkehrende relationale Feldbewegung wuerde
nicht als Profil gespeichert, sondern hinterliesse eine veraenderte lokale
Antwortbedingung.

**Staerke:** Direkter Anschluss an den gesuchten inneren Kontext bei
identischer spaeterer Probe.

**Hauptgefahr:** Ein deformierbarer Zustand kann lediglich ein Produkt-,
Energie- oder Leaky-Integrator mit festem Leser sein.

**Pflichtgegenbaseline:** lokale exponentielle Spur mit gleicher Kapazitaet,
Relaxation und Leserwirkung.

### H2: begrenztes lokal umverteilbares Feldmedium

**Funktionsannahme:** Eine endliche lokale Traegerressource kann durch reale
Feldwirkung raeumlich umverteilt werden und dadurch spaetere Aufnahme oder
Weiterleitung veraendern. Neue Beanspruchung kann alte Verteilung verdraengen,
ohne Loeschbefehl.

**Anschluss an MINI_DIO:** Bewegliche Relationsordnung und selbstbegrenzende
Erneuerung erhalten ein feldlokales Gegenstueck, ohne feste Partnerlisten zu
speichern.

**Staerke:** Begrenzung, Vergessen und Wiederpraegung koennen aus derselben
Ressourcenbilanz folgen.

**Hauptgefahr:** Richtung, Skala und Mobilitaet koennten willkuerlich
programmiert werden; eine bloss diffundierende Zusatzmasse kann redundant
oder bedeutungslos bleiben.

**Pflichtgegenbaseline:** passive Diffusion einer konservierten Zusatzgroesse
ohne feldabhaengige Leitwirkung.

### H3: lokale relationsabhaengige Materialantwort

**Funktionsannahme:** Nicht einzelne Aktivitaet, sondern die zeitliche
Koexistenz lokaler Feldunterschiede veraendert eine begrenzte Materialantwort.
Die spaetere Feldwirkung haengt von der entstandenen lokalen Materiallage ab.

**Anschluss an MINI_DIO:** Dieser Weg uebertraegt den Kern der relativen
Rangwechselform, ohne globale Raenge, feste Neuronenpaare oder gespeicherte
Zyklen einzufuehren.

**Staerke:** Zeitkontext entsteht aus lokaler relationaler Bewegung statt aus
Aktivitaetsmenge oder Weltzeit.

**Hauptgefahr:** Jede konkrete Wahl wie Vorzeichen, Betrag, Produkt oder
Quadrat kann wieder nur ein handgebauter Integrator sein. Eine feste
Paaranatomie wuerde MINI_DIOs Indexproblem wiederholen.

**Pflichtgegenbaseline:** alle einfachen lokalen Moment- und
Produktintegratoren mit identischem Zustandsbudget.

## Vorlaeufige Bewertung

| Kriterium | H1 Feldaufnahme | H2 Medium | H3 Materialantwort |
|---|---:|---:|---:|
| direkter Anschluss an spaetere Feldwirkung | hoch | mittel | hoch |
| natuerliche Ressourcenbegrenzung | offen | hoch | offen |
| natuerliche Loesung und Wiederpraegung | offen | hoch | offen |
| Anschluss an MINI_DIO-Eigenform | mittel | mittel | hoch |
| Gefahr eines trivialen Integrators | hoch | mittel | sehr hoch |
| Gefahr vorgegebener Richtung oder Topologie | niedrig | hoch | hoch |

Der
[H1-Kausalvertrag](H1_LOKAL_DEFORMIERBARE_FELDAUFNAHME_KAUSALVERTRAG.md)
zeigt inzwischen, dass H1 als Einzelspur bereits mit dem verworfenen
C1-Kandidaten kollidiert und geschlossen ist. Der
[H2-Bestandsaudit](H2_BEGRenztes_UMVERTEILBARES_FELDMEDIUM_BESTANDSAUDIT.md)
zeigt inzwischen: H2 ist fuer einen vollstaendigen Memory-Lebenszyklus
funktional stark, laesst sich aber nicht automatisch aus der heutigen
MCM-Gleichung herleiten. Offen bleibt nur eine ausdruecklich deklarierte,
unabhaengig pruefbare Materialhypothese. H3
liegt MINI_DIOs relationaler Eigenform am naechsten, ist jedoch am schwersten
von einem programmierten Integrator abzugrenzen.

## Falsifikationsmatrix

Jeder spaetere Kandidat muss mindestens folgende Vergleiche ueberstehen:

| Vergleich | Muss kollidieren oder entsprechen | Darf sich unterscheiden |
|---|---|---|
| gleicher Quellenpfad, andere Segmentdichte | funktional entsprechen | nicht allein wegen Aufrufzahl |
| gleicher kausaler Verlauf, Zeitdehnung | nach Zeitabbildung entsprechen | nicht allein wegen Sekunden |
| gleiche Dauer und Energie, andere Reihenfolge | offen | wenn die Feldbewegung kausal verschieden ist |
| gleiche Wiederholungszahl, budgetgleicher neuer Verlauf | nicht durch Zaehler erklaerbar | nur substratvermittelt |
| angeglichene schnelle Feldrollen, identische Probe | Baseline identisch | Kandidat nur bei getragener Substratgeschichte |
| Substrattausch zwischen A und B | schnelle Rollen unveraendert | Wirkung muss mit dem Substrat wandern |
| Substratneutralisierung | keine Zusatzwirkung | keine versteckte Sequenzwirkung |
| konkurrierende Geschichte und Ruhe | getrennt auswerten | Loesung darf nicht nur feste Ablaufzeit sein |
| neue Geschichte nach Funktionslosigkeit | gleiche Kapazitaet nutzbar | neue statt alte Wirkung |

## Forschungsentscheidung

Die MINI_DIO-Eigenzeitforschung ist ausreichend, um die Suche nach einer Uhr,
einem Tickzaehler oder einer externen Episodensegmentierung zu beenden. Sie
liefert aber keine fertige Memory-Mechanik.

Der neue Schwerpunkt ist:

> lokale relative Feldbewegung als Schreibursache eines begrenzten Substrats,
> das spaetere Feldwirkung veraendert und durch weitere Feldgeschichte wieder
> vollstaendig funktionslos sowie neu praegbar werden kann.

## Bester naechster Schritt

Der H1-Vertrag ist abgeschlossen: Die einfache lokale Feldempfaenglichkeit
kollidiert vollstaendig mit C1 und wird nicht erneut implementiert.

Der H2-Bestandsaudit ist abgeschlossen. Als naechstes werden hoechstens drei
etablierte passive Materialklassen statisch gegen die H2-B-Grenzen verglichen.
Noch wird keine Zustandsvariable oder Gleichung implementiert.
