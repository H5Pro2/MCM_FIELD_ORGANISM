# S1-OX G2/D3 zustandsbehaftete Retentionsbaseline: Funktions- und Falsifikationsvertrag

## Status

S1-OX bindet ausschliesslich Funktion, faire Kausalexposition,
Gegenprognose und Verwerfungsbedingungen fuer genau eine kleine
zustandsbehaftete Gegenbaseline zum abgenommenen S1-OW-Drei-Checkpointpfad.
Der Schritt bindet noch kein Schema, keine Gleichung, keinen Zahlenparameter,
keine Implementierung und keinen Lauf.

Entscheidung:

```text
G2_D3_ONE_STATE_MATCHED_RETENTION_BASELINE_FUNCTION_AND_FALSIFICATION_BOUND
```

## Methodischer Ausgangspunkt

S1-OW reproduziert fuer XXX und YYY technisch exakt:

```text
CP0 -> CP1 -> CP2
0.5 -> 0.25 -> 0.125
```

Diese Folge ist durch die vorab gesetzte konservative D3-Unterteilung und
den bekannten read-only O3-Operator konstruktiv bestimmt. Sie ist deshalb
allein keine eigene Funktionsprognose des Substratkandidaten. Eine einfache
zustandsbehaftete Baseline darf dieselbe Folge tragen koennen, sofern sie
dieselbe relevante Vorgeschichte sieht und nicht armweise angepasst wird.

## Genau eine Gegenbaseline

Die neue Gegenrolle lautet:

```text
G2_D3_MATCHED_SINGLE_STATE_RETENTION_BASELINE
```

Sie ist die kleinste diskrete Gegenrolle der Leaky-/Retentionsklasse und
kein neuer Feld- oder Substratkandidat.

Sie besitzt genau einen endlichen, nichtnegativen skalaren Eigenzustand. Der
Zustand ist weder D3-Ressource noch Feld-, Nachhall-, Integrator- oder
Checkpointbeleg. Er wird vor CP0 einmal aus dem gemeinsamen registrierten
Startwert initialisiert und danach ueber beide Fortsetzungsereignisse ohne
Reset getragen.

Jedes gueltige frische Fortsetzungsereignis darf den Eigenzustand nach genau
einer unveraenderten Retentionsregel aktualisieren. Dieselbe spaeter zu
bindende Konfiguration gilt fuer:

- ersten und zweiten Schritt;
- XXX und YYY;
- alle Wiederholungen;
- alle spaeter zulaessigen Null- und Fehlerkontrollen.

Schrittnummer, Orientierung und Chainrolle duerfen im Beleg erscheinen,
aber weder Regel noch Sachwert umschalten.

Ein reiner Checkpointreadout oder ein Intervall ohne gueltiges frisches
Fortsetzungsereignis darf kein Zustandsupdate ausloesen.

## Eigene Funktionsprognose der Baseline

Die Baselineprognose lautet:

```text
Ein einziger vor der Ausfuehrung gebundener skalarer Retentionszustand kann
die vollstaendige Folge CP0/CP1/CP2 fuer XXX und YYY gemeinsam erklaeren,
ohne D3-Ressourcenrollen oder Checkpoint-Fixturewerte zu lesen.
```

Wenn diese Prognose spaeter besteht, ist der S1-OW-Vektor durch die
zustandsbehaftete Gegenbaseline geschlossen. Dann darf aus dem Vektor keine
eigene Ressourcen-, Abschwaechungs- oder hypothetische MCM-Memory-Funktion
abgeleitet werden.

Die Kandidatenseite besitzt in der aktuellen Zwei-Schritt-Matrix keine
abweichende Gegenprognose. Ein funktionales Residuum kann erst aus einer
vorregistrierten Erweiterung mit Konkurrenz, kontaktfreier Erholung oder
direkter Ressourcenintervention entstehen. S1-OX bindet eine solche
Erweiterung noch nicht.

## Gemeinsame kausale Exposition

Kandidat und Baseline erhalten dieselbe logische Ereignisfolge:

```text
gemeinsamer Start -> CP0
erstes gueltiges Fortsetzungsereignis -> erstes Zustandsupdate -> CP1
zweites gueltiges Fortsetzungsereignis -> zweites Zustandsupdate -> CP2
```

Die Baseline wird nicht erst am Readout eingesetzt. Sie muss ihren eigenen
Zustand bereits ab dem gemeinsamen Start durch beide Ereignisse tragen.
Checkpointrollen lesen nur den jeweils erreichten Zustand; sie loesen kein
zusaetzliches Update aus.

XXX und YYY bleiben getrennte Expositionsketten. Beide starten aus demselben
Baselinevorzustand und derselben Konfiguration. Es gibt keinen
Zustandsuebertrag zwischen den Ketten.

Bei einem ungueltigen Zweischrittpfad gibt es weder Kandidaten- noch
Baseline-Teilvektor. Ein Fehler vor CP2 beendet den Vergleich atomar.

## Erlaubte Baselineeingaben

Die Baseline darf spaeter nur erhalten:

- den vorregistrierten skalaren Startzustand;
- die geordnete Folge zweier modellneutraler gueltiger
  Fortsetzungsereignisse;
- eine einzige vor der Ausfuehrung gebundene Konfigurationsidentitaet;
- die drei logischen read-only Checkpointrollen;
- die getrennte Kettenidentitaet ausschliesslich fuer Provenienz.

Die Ereignisse duerfen nur bestaetigen, dass jeweils genau eine frische
Fortsetzung stattgefunden hat. Sie enthalten keinen erwarteten Folgewert.

## Gesperrte Informationen

Die Baseline darf nicht erhalten oder ableiten:

- freie, leitend gebundene oder refraktaere D3-Ressource;
- D3-Rohbytes, Anatomyrecords oder deren Sachwerte;
- O3-Werte, O3-Belege oder den S1-OW-Vektor;
- Projektions-, Commit-, Kompositions- oder Checkpointbelege als
  Folgeeingang;
- erwartete Deltas oder den Vergleichsdigest;
- Fixture-, Arm-, Ergebnis- oder Fehlerlabel als Regelinput;
- eine getrennte Konfiguration pro Kette, Schritt oder Checkpoint;
- einen Reset, eine Reparatur oder einen nachtraeglichen Fit innerhalb der
  Exposition.

Digests solcher Objekte duerfen nur im abschliessenden passiven
Vergleichsbeleg zur Provenienz erscheinen. Sie duerfen keinen Baselinewert
erzeugen.

## Gebundene Vergleichsrollen

Ein spaeterer fairer Vergleich muss fuer Kandidat und Baseline getrennt
tragen:

- drei skalare Checkpointwerte;
- zwei benachbarte und eine gesamte gerichtete Differenz;
- einen orientierungsunabhaengigen Vergleichsdigest;
- Startzustands-, Konfigurations-, Ereignis- und Ergebnisdigests;
- einen atomaren Gueltigkeitsstatus ohne Teilprofil.

Es wird nicht checkpointweise gefittet. Genau eine Baselinekonfiguration
muss alle sechs Sachwerte der beiden Ketten gemeinsam erklaeren.

## Schliessungs- und Falsifikationsentscheidung

### Baseline schliesst den aktuellen Befund

Der S1-OW-Befund ist durch die Baseline geschlossen, wenn eine einzige vorab
gebundene Konfiguration fuer XXX und YYY gemeinsam exakt reproduziert:

```text
checkpoint values = (0.5, 0.25, 0.125)
directed components = (-0.25, -0.125, -0.375)
comparison digest
= 5c8d3b60bbc205594974f632a878472bf628426dc914af72514cf7b42e8a86a5
```

Eine geschlossene Baseline ist ein methodisch erwartbarer Negativbefund fuer
eine eigene Kandidatenfunktion, kein technischer Fehler des MCM-Feldkerns.

### Baselinevertrag ist ungueltig

Die Baseline wird als unfair oder ungueltig verworfen, wenn sie:

- nicht dieselben zwei relevanten Ereignisse ab dem gemeinsamen Start sieht;
- zwischen CP0, CP1 und CP2 zurueckgesetzt oder neu initialisiert wird;
- pro Kette, Schritt oder Checkpoint verschieden konfiguriert wird;
- erwartete Werte, D3-Zustaende, Belege oder Ergebnislabels liest;
- einen Checkpoint als Updateereignis verwendet;
- ungueltige Sequenzen teilweise auswertet;
- Werte nach dem Lauf repariert, clippt oder aus Fixtures ersetzt;
- nur Betragswerte vergleicht und dadurch die Richtung der Komponenten
  verliert.

Ein ungueltiger Baselinevertrag darf weder als Schliessung noch als Residuum
gewertet werden.

### Kandidatenresiduum bleibt vorerst gesperrt

Ein Scheitern der spaeteren Baseline auf nur diesen zwei Ketten waere noch
kein positiver Kandidatenbefund. Zuerst muessten Implementierungsfehler,
Konfigurationsbindung und Expositionsgleichheit geschlossen werden. Eine
eigene Funktionsaussage benoetigt danach mindestens eine getrennt
vorregistrierte Konkurrenz-, Erholungs- oder Ressourcenintervention, die
dieser Einzustandsbaseline eine andere Prognose gibt.

## Aussagegrenze

S1-OX bindet nur eine faire technische Gegenprognose zum konstruktiven
S1-OW-Checkpointvektor. Es gibt noch keine Baselinegleichung, keinen
Parameter, keinen Vergleichsoperator und keinen neuen Lauf.

Der Vertrag belegt weder eine eigene Substratfunktion noch Abschwaechung,
Interferenz, Erholung oder eine hypothetische MCM-Memory-Funktion.

## Naechster erlaubter Schritt

S1-OY darf ausschliesslich die diskrete Baselinezustandsanatomie,
modellneutralen Ereignisrecords, Update- und Checkpointreihenfolge,
Schemafelder, Vertragsdigests und Fail-Closed-Codes statisch binden.

S1-OY darf noch keine Zahlenparameter oder Gleichung waehlen, keine
Implementierung anlegen, keinen Test oder Baselinelauf ausfuehren und keine
Feld- oder Runtimewirkung freigeben.
