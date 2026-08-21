# S1-PX: Statischer Funktions- und Falsifikationsvertrag fuer die hypothetische MCM-Memory-Entwicklungsrichtung

## Status und Umfang

S1-PX oeffnet nach der abgeschlossenen Konsolidierung S1-PQ bis S1-PW genau
eine neue Forschungsrichtung. Der Vertrag beschreibt die gesuchte technische
Funktion, ohne bereits einen Traeger oder Mechanismus auszuwaehlen.

S1-PX enthaelt:

- keine Gleichung und keine Parameter;
- keine neue Zustandsvariable und keine Kandidatenanatomie;
- keine Runtimeaenderung;
- keine Fixture, keinen Test und keinen Feldlauf;
- keinen Funktionsbefund.

Verbindliche Entscheidung:

```text
HYPOTHETICAL_MCM_MEMORY_FUNCTION_DIRECTION_REOPENED
JOINT_LIFECYCLE_COUNTERPREDICTION_BOUND
NO_CANDIDATE_NO_EQUATION_NO_RUNTIME_NO_RUN
```

Der Ausdruck `hypothetische MCM-Memory` bezeichnet ausschliesslich die hier
festgelegte Entwicklungsrichtung. Er bezeichnet keine vorhandene Faehigkeit.

## Technisches Funktionsziel

Gesucht wird eine spaetere lokale Feldwirkung mit folgender gemeinsamer
Kausalstruktur:

```text
zwei zulaessige lokale Weltgeschichten
-> unterschiedliche, endogen erreichte innere Disposition
-> Angleichung des aktuellen Rezeptorkontakts sowie der schnellen S/H-Lage
-> dieselbe spaetere lokale Probe
-> unterschiedliche weitere S-Fortsetzung
```

Der Unterschied muss durch normale Rezeptor- und Feldgeschichte entstehen.
Er darf nicht durch ein gesetztes Label, einen Ergebniszaehler, Reward,
Replay, einen externen Reset oder eine armweise gewaehlte Konfiguration
erzeugt werden.

Eine blosse Zustandsverschiedenheit reicht nicht. Die Disposition muss im
aktiven MCM-Wahrnehmungsfeld eine spaetere kausale Wirkung besitzen.

## Gemeinsame Mindestprognose

Ein spaeterer Kandidat ist nur zulaessig, wenn er vor seiner Gleichung alle
folgenden Teile als eine gemeinsame Prognose tragen kann:

1. **Endogene Bildung:** Zwei kontrollierte Geschichten erzeugen ueber
   denselben normalen Feldpfad unterschiedliche lokale Dispositionen.
2. **Verbleibende Wirkung:** Nach konstruktiver Angleichung von aktuellem
   Eingang, S und H bleibt bei derselben Probe eine unterschiedliche
   S-Fortsetzung erhalten.
3. **Abschwaechung:** Weitere relevante Geschichte kann die spaetere Wirkung
   verringern; ein fest vorgegebener Zerfall allein erfuellt dies nicht.
4. **Spezifische Interferenz:** Eine konkurrierende lokale Geschichte
   veraendert die spaetere A-Wirkung gegenueber einer belastungs- und
   zeitkontrollierten A-Pause-A-Geschichte.
5. **Endliche lokale Kapazitaet:** Gleichzeitige oder aufeinanderfolgende
   lokale Beanspruchung erzeugt eine direkt pruefbare Konkurrenz. Eine globale
   Normalisierung oder ein nachtraegliches Clipping gilt nicht als Kapazitaet.
6. **Funktionale Freigabe:** Die fruehere Wirkung kann vollstaendig
   funktionslos werden, und derselbe lokale Zustandsraum wird danach fuer eine
   andere zulaessige Geschichte erneut nutzbar.
7. **Nichtreduzierbarkeit:** Ein einziger fair exponierter Parametersatz jeder
   Pflichtbaseline darf den gesamten Bildungs-, Wirkungs-, Interferenz-,
   Abschwaechungs-, Freigabe- und Wiederverwendungsverlauf nicht gemeinsam
   reproduzieren.

Ein Kandidat, der nur einen Teil dieser Folge erfuellt, erfuellt die
S1-PX-Gegenprognose nicht.

## Modellneutrale Vergleichsbindung

Kandidat und alle zustandsbehafteten Baselines muessen dieselbe kausale
Vorgeschichte sehen. Dazu gehoeren A-, B-, Gap-, Pausen-, Konkurrenz- und
Freigabeabschnitte sowie derselbe spaetere Readout.

Verbindlich sind:

- identische Ausgangsbedingungen und Eingangsfolgen;
- identische lokale Geometrie und Feldtakte;
- identische Eingangs-, Zeit- und Ressourcenbudgets;
- ein gemeinsamer Parametersatz pro Modell ueber alle Arme;
- keine Reparatur oder Uminterpretation bestehender Profile;
- kontrollierte Neuregistrierung, falls alte Profile keine formal
  aequivalente Kausalgeschichte besitzen;
- passive Messung ohne Kandidatenwissen im Comparator.

Noch werden keine konkreten Folgen, Werte, Toleranzen oder Digests gebunden.

## Pflichtgegenbaselines

Jeder spaetere Kandidat muss gegen die folgenden einfacheren Erklaerungen
gemeinsam bestehen:

| Baseline oder geschlossener Bestand | Zu widerlegende einfachere Erklaerung |
|---|---|
| aktueller Rezeptorkontakt | Die spaetere Differenz stammt nur aus einem noch unterschiedlichen Eingang. |
| schneller Nachhall H und mehrere feste Zeitskalen | Die Differenz ist nur eine passive, exponentielle oder mehrstufige Restspur. |
| Fixed Adapter und Frozen-E1 | Ein vor der Probe festgelegter Adapter erklaert alle spaeteren Readouts. |
| Leaky und Integrator | Ein unabhaengiger Skalar mit Zerfall oder Akkumulation erklaert den Gesamtverlauf. |
| feste Verzoegerung, statische Rekurrenz und permanentes Gewicht | Die Geschichte wird nur zeitversetzt oder durch eine unveraenderliche Kopplung weitergegeben. |
| Replay oder gespeicherte Eingabefolge | Die spaetere Wirkung entsteht durch erneutes Einspeisen frueherer Daten. |
| globale Normalisierung und Saettigungsintegrator | Konkurrenz und Freigabe sind nur globale Skalierung oder Saettigung. |
| Capacity-Clamp | Der Readout folgt ausschliesslich der momentan freien Kapazitaet. |
| DTS-1/T1 | Die Wirkung ist vollstaendig aus `free/bound/blocked` und dessen geschlossener Trajektorie rekonstruierbar. |
| Retentionsbaseline | Ein einzelner zustandsbehafteter Retentionswert reproduziert alle Checkpoints. |
| G2/D3 | Eine gesetzte oder leaky gebildete Unterteilung wird nur unter neuem Namen erneut verwendet. |

Die Baselines duerfen nicht absichtlich geschwaecht werden. Kann eine davon
die gemeinsame Mindestprognose mit fairer Exposition vollstaendig erklaeren,
wird der Kandidat verworfen oder als Baseline eingeordnet.

## Mess- und Interventionsrollen vor jeder Gleichung

Ein spaeterer Kandidatenvertrag muss mindestens folgende Rollen direkt
operationalisieren:

- aktuelle lokale Rezeptor-, S- und H-Lage;
- vollstaendiger kandidateninterner Zustand und seine lokale Bilanz;
- spaetere S-Fortsetzung unter identischer Probe;
- A-Pause-A- und A-B-A-Differenz bei kontrollierter Gesamtbelastung;
- lokale Konkurrenz gegen eine nicht konkurrierende Ortskontrolle;
- Verlust der alten Funktionswirkung;
- direkte Wiederverwendbarkeit der freigegebenen lokalen Kapazitaet;
- Kandidatenablation bei ansonsten identischem Zustand;
- bitgenauer Nullpfad bei ausgeschaltetem Kandidaten;
- Baseline-Residuen ueber die vollstaendige gemeinsame Folge.

Eine Observervariable ohne Rueckwirkung, ein Snapshot oder ein gespeicherter
Record erfuellt keine dieser Funktionsrollen.

## Verwerfungsbedingungen

Ein spaeterer Kandidat wird fail-closed gestoppt, wenn mindestens eine der
folgenden Bedingungen eintritt:

- seine relevante Disposition entsteht nicht endogen aus normaler
  Feldgeschichte;
- nach Angleichung von Eingang, S und H verbleibt keine spaetere Feldwirkung;
- die Wirkung benoetigt Labels, Reward, Replay, Ergebniszaehler, Phasencodes
  oder einen externen Reset;
- Interferenz ist nicht von Pause, Belastung, Sattigung oder Ortsunspezifitaet
  getrennt;
- Kapazitaet ist nicht lokal, nicht endlich oder nicht direkt bilanzierbar;
- Freigabe bedeutet nur Ablauf, Clipping, Nullsetzen oder Neustart;
- die freigegebene Kapazitaet ist nicht fuer eine andere Geschichte erneut
  nutzbar;
- der Gesamtverlauf ist aus S/H, `free/bound/blocked`, einem Clamp, einem
  Retentionsskalar oder einer anderen Pflichtbaseline rekonstruierbar;
- verschiedene Arme benoetigen nachtraeglich verschiedene Modellparameter;
- der Kandidat verletzt Nullpfad, lokale Bilanz, Determinismus oder die
  bestehende Feldkernschnittstelle.

Ein Negativbefund wird nicht innerhalb desselben registrierten Schritts durch
neue Parameter, neue Messgroessen oder eine neue Funktionsdefinition repariert.

## Geschlossene Zweige und Claimsperren

S1-PX oeffnet Frozen-E1, E1, F3, DTS-1/T1 oder G2/D3 nicht erneut. Ihre
Schemata, Validatoren, Operatoren, Ledger und Comparatoren bleiben technische
Infrastruktur oder Baselinebestand.

Gesperrt bleiben Aussagen zu vorhandener Memory-Faehigkeit, Lernen,
Rekonstruktion, Semantik, Verstehen, Bewusstsein, Gefuehl, Erleben, KI oder
biologischer Organik. Auch ein spaeter bestandener Teiltest wuerde nur die
jeweils vorregistrierte technische Feldwirkung belegen.

## Abschluss und genau ein naechster Schritt

S1-PX bindet erstmals nach S1-PQ eine neue, gemeinsame und falsifizierbare
Funktionsrichtung. Es waehlt bewusst noch keinen Kandidaten aus. Die
technische Konsolidierung S1-PQ bis S1-PW bleibt abgeschlossen.

Als genau ein Anschluss ist zulaessig:

```text
S1-PY - statischer Wiederverwendbarkeits- und Lueckenaudit des
        modellneutralen Expositions-, Baseline- und Comparatorgeruests
```

S1-PY soll nur feststellen, welche vorhandenen A/B/Gap-, Baseline- und
Comparatorvertraege die S1-PX-Vorgaben bereits formal erfuellen und welche
Rollen fehlen. Es darf keine Kandidatenmechanik, Gleichung, Parameter,
Runtimeaenderung, Fixture, Testausfuehrung oder Ergebnisentscheidung
enthalten.
