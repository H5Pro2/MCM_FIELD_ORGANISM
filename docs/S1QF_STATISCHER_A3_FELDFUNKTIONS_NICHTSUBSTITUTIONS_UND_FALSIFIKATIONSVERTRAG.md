# S1-QF: Statischer A3-Feldfunktions-, Nichtsubstitutions- und Falsifikationsvertrag

## Status und Umfang

S1-QF prueft vor jeder Feldgleichung, ob die bisherigen A3-Unterrollen
Saettigung und globale Normalisierung jeweils eine eigenstaendige technische
Gegenprognose gegen das bereits gebundene Pflichtbaselinepaket besitzen.

Der Vertrag:

- bindet Funktionsrollen und Falsifikationsbedingungen;
- trennt Feldrollen von reinen Observerdiagnosen;
- entscheidet Redundanz gegen A1, A2, M1 und M5;
- beschreibt nur prinzipielle S- und H-Ausgabegrenzen;
- waehlt keine Gleichung, Parameter, Werte, Toleranzen oder Fixture;
- implementiert und testet nichts;
- fuehrt keinen Feldlauf und keine Ergebnisentscheidung aus.

Verbindliche Entscheidung:

```text
SAT_FIELD_ROLE_REDUCED_TO_M5_SINGLE_STATE_RETENTION_WITH_FIXED_READOUT
NORM_RETAINS_DISTINCT_GLOBAL_OUTPUT_COUPLING_COUNTERPREDICTION
A3_REDUCED_TO_ONE_MANDATORY_FIELD_ROLE_PLUS_OBSERVER_DIAGNOSTICS
NO_EQUATIONS_NO_VALUES_NO_IMPLEMENTATION_NO_EXECUTION
```

## Nichtduplizierungskriterium

Eine A3-Unterrolle bleibt nur als eigener spaeterer Feldarm bestehen, wenn
alle folgenden Bedingungen gelten:

1. Sie besitzt eine Gegenprognose, die nicht nur durch Umbenennung eines
   bereits gebundenen privaten Zustands entsteht.
2. Sie fuegt keine Kandidatenressource, kein Armwissen und keine
   ereignisspezifische Regel hinzu.
3. Ein einziger vorab gebundener Parametersatz muss alle
   F/T/I/C/R/U-Geschichten tragen.
4. Ihr vollstaendiges Feldprofil kann prinzipiell von den vorhandenen
   Baselines abweichen.
5. Die Abweichung folgt aus ihrer eigenen einfachen Erklaerung und nicht aus
   einem unfairen Handoff oder einer anderen H-Dynamik.

Eine vorhandene Observergleichung allein begruendet keinen Feldarm.

## SAT - lokaler Saettigungsintegrator

### Bisherige Funktionsklasse

Der vorhandene W7-N-SAT-Kern besitzt pro Ort genau einen lokalen latenten
Zustand. Dieser Zustand wird durch die normale lokale Feldgeschichte getragen
und ueber einen festen begrenzenden Readout ausgegeben. Die Orte teilen weder
einen Nenner noch eine Ressource.

### Abgleich gegen B3 und M5

B3 ist bereits eine konkrete lokale Leaky-Gegenbaseline. M5 ist als
allgemeine Einzustandsretention pro Ort gebunden und erlaubt einen vorab
festen Readout auf die vollstaendige Feldfortsetzung.

SAT fuegt gegenueber M5 hinzu:

- keine zweite Zustandsrolle;
- keine neue Kausalhistorie;
- keine lokale Konkurrenzressource;
- keine ortsuebergreifende Kopplung;
- keine Sequenz- oder Pufferfunktion;
- nur eine feste lokale Ausgangsbegrenzung.

Damit ist SAT eine konkrete Unterklasse von M5. Ein neuer SAT-Feldarm wuerde
die allgemeine Einzustandsretention absichtlich duplizieren und waere zudem
ohne vorhandenen Feldhandoff nur durch eine neue Ausgabefunktion herstellbar.

### SAT-Entscheidung

```text
NO_DISTINCT_NON_M5_FIELD_COUNTERPREDICTION
SEPARATE_SAT_FIELD_BRANCH_STOPPED
EXISTING_W7N_SAT_KERNEL_RETAINED_AS_OBSERVER_DIAGNOSTIC
```

Der vorhandene SAT-Kern und seine technischen Tests bleiben unveraendert im
Projekt. Er darf spaeter zur Diagnose zeigen, ob ein lokaler Observeroutput
begrenzt ist. Er darf jedoch:

- nicht als zusaetzlicher Pflichtfeldarm zaehlen;
- nicht als Kandidat erscheinen;
- nicht als M5-Ersatz mit schwacherem Vergleichsumfang dienen;
- keinen positiven Feld- oder Kapazitaetsstatus erzeugen.

Sollte M5 spaeter den vollstaendigen Verlauf reproduzieren, ist damit auch
die lokale Einzustands-Saettigungsklasse geschlossen. Sollte M5 scheitern,
folgt daraus keine automatische Wiedereroeffnung von SAT.

## NORM - globale Normalisierung eines lokalen Zustands

### Eigene einfache Erklaerung

NORM traegt wie M5 genau einen lokalen privaten Zustand pro Ort. Seine
eigenstaendige Funktion liegt nicht in einem weiteren Zustand, sondern in
der ortsuebergreifenden Ausgabeordnung:

- alle lokalen Zustandswerte derselben Geometrie bilden gemeinsam genau eine
  aktuelle globale Skalierungsgrundlage;
- jede lokale Ausgabe haengt vom eigenen Zustand und derselben gemeinsamen
  Skalierungsgrundlage ab;
- es gibt keinen Ressourcentransfer, kein Edge-Ledger und keine
  Kandidatenkapazitaet;
- die globale Ausgabekopplung erzeugt keinen zusaetzlichen Carryzustand.

NORM prueft damit die einfachere Erklaerung, dass scheinbare Konkurrenz,
Abschwaechung oder Freigabe nur durch eine geometrieweite Skalierung der
aktuellen baselineeigenen Zustandslage entsteht.

### Praezisierung von M5

Die in S1-QC und S1-QD als `unabhaengig` gebundene M5-Retention wird fuer den
Nichtduplizierungsvergleich ausdruecklich ortsseparabel gelesen:

- jeder lokale Zustand wird ohne Zustand eines anderen Ortes getragen;
- der feste M5-Readout eines Ortes liest nur diesen lokalen Zustand und die
  gemeinsamen modellneutralen Feldinputs dieses Ortes;
- M5 besitzt keinen geometrieweiten Nenner und keine globale
  Outputnormalisierung.

Diese Praezisierung fuegt M5 keine Gleichung hinzu. Sie verhindert nur, dass
M5 nachtraeglich jede beliebige globale Ausgabefunktion aufnehmen und damit
NORM tautologisch verschlucken kann.

### NORM gegen A1

A1 traegt nur das gemeinsame schnelle S/H-Feld. Bei angeglichenem lokalem
Readoutinput besitzt A1 keinen privaten globalen Skalierungszustand.

NORM sagt dagegen voraus, dass eine zusaetzliche entfernte baselineeigene
Zustandslast die Ausgabe am unveraenderten lokalen Ort allein ueber die
gemeinsame Skalierungsgrundlage veraendern kann. Diese Wirkung darf nicht aus
einer veraenderten lokalen Probe oder einem H-Unterschied stammen.

### NORM gegen B2, B3 und M5

B2, B3 und M5 tragen ihre privaten Zustandsrollen ortsseparabel. Eine
entfernte Zustandslast ohne lokalen Feld- oder Geometriepfad darf deren
lokalen Readout nicht allein durch einen globalen Nenner skalieren.

NORM besitzt genau diese ortsuebergreifende Outputabhaengigkeit. Bleibt der
lokale NORM-Output bei veraenderter entfernter Zustandslast unveraendert, ist
die eigenstaendige NORM-Prognose nicht vorhanden.

### NORM gegen B5 und B6

B5 und B6 erzeugen Feldwirkung ueber vorhandene F3-Kopplungs- und
Geometriepfade. Ihre Wirkung kann von Kanten, lokalen Gradienten und dem
getragenen M-Zustand abhaengen.

NORM darf keine dieser Rollen verwenden. Seine Skalierungsgrundlage umfasst
die kanonische Ortsmenge direkt und unabhaengig von Kantenabstand oder
Nachbarschaft. Eine NORM-Ausgabe, die Edge-Inventar, M-Masse, F3-Fluss oder
CONST-V liest, ist keine NORM-Gegenbaseline.

### NORM gegen M1

M1 ueberlagert mehrere unabhaengige passive Spuren. Ohne gemeinsame
Outputnormalisierung kann eine entfernte Spur den lokalen Readout nicht nur
durch geometrieweite Skalierung veraendern.

NORM besitzt dagegen genau einen Zustand pro Ort und genau eine globale
Ausgabekopplung. Werden mehrere Zeitspuren oder armweise ausgewaehlte
Komponenten benoetigt, ist NORM ungueltig und M1 bleibt die passendere
Erklaerung.

## Prinzipielle S- und H-Ausgabegrenze fuer NORM

NORM muss spaeter ein vollstaendiges gemeinsames Feldresultat liefern. Vor
einer Gleichungswahl werden folgende Rollen gebunden:

- Die baselineeigene Normalisierung darf ausschliesslich den Beitrag zur
  naechsten S-Fortsetzung bestimmen.
- H erhaelt keine NORM-spezifische Gleichung und keinen privaten
  Normalisierungszustand.
- Die schnelle H-Fortsetzung muss dieselbe unveraenderte technische Rolle wie
  im kandidatenfreien A1-Feldpfad verwenden.
- Der globale Skalierungswert wird nur aus dem vollstaendigen aktuellen
  NORM-Privatzustand derselben Geometrie gebildet.
- Der Skalierungswert wird nicht in den naechsten Privatstatus
  zurueckgeschrieben.
- `ALIGN_READOUT_SH` bleibt zeitlos und veraendert den NORM-Zustand nicht.

S1-QF entscheidet noch nicht, ob der normalisierte Beitrag S ersetzt,
begrenzt oder ueber eine vorhandene Feldquelle einwirkt. Diese Auswahl waere
Teil eines spaeteren Feldoutputvertrags und darf nicht in einem Adapter
verborgen werden.

## Erforderliche NORM-Gegenprognosen

Eine spaetere NORM-Feldrolle muss mit genau einer Konfiguration gemeinsam
folgende gerichtete technische Aussagen tragen:

### F - Bildung

Eine fokale Geschichte kann ueber ihren lokalen privaten Zustand eine
spaetere Ausgabe veraendern. Eine gleich belastete entfernte Geschichte kann
die fokale Ausgabe nur ueber die globale Skalierungsgrundlage veraendern,
nicht ueber lokale Ressourcenbindung.

### T - Wiederholung und Abschwaechung

Eine scheinbare Abschwaechung darf aus zunehmender globaler Skalierung oder
aus dem ortsseparablen privaten Zustandsverlauf entstehen. Es gibt keine
Beanspruchungs- oder Freigaberolle.

### I und C - Interferenz und Kapazitaet

Lokale B-Last und gleich grosse entfernte C-Last muessen bei gleichem
globalem Zustandsbetrag dieselbe reine Normalisierungstendenz besitzen.
Unterscheidet NORM B und C allein wegen lokaler Nachbarschaft, verwendet es
eine verbotene lokale Ressource oder Feldkopplung.

Damit ist NORM gerade eine Gegenbaseline gegen einen nur scheinbar lokalen
Kapazitaetseffekt: echte lokale Spezifitaet muss gegen die globale
Skalierung bestehen.

### R und U - Funktionsverlust und Wiederverwendung

Ein spaeterer Wirkungsverlust darf nur aus dem normalen Zustandsverlauf und
der aktuellen globalen Skalierung folgen. NORM kann keine direkt freigegebene
lokale Ressource und keine erneute lokale Kapazitaetsbeanspruchung ausweisen.

Kann NORM dennoch das vollstaendige R/U-Feldprofil reproduzieren, bleibt der
Kandidatenverlauf global skalierungsreduziert; die kandidateninterne Bilanz
allein hebt diese Reduktion nicht auf.

## Schliessungsregel

NORM schliesst einen spaeteren Kandidaten nur, wenn ein einziger
vorregistrierter NORM-Parametersatz das vollstaendige gemeinsame
F/T/I/C/R/U-Feldprofil nach S1-QA reproduziert. Einzelne skalierte
Checkpoints, Normen oder Observerprofile reichen nicht.

Ein NORM-Nichtfit ist kein positiver Kandidatenbefund. Alle anderen
Pflichtbaselines und Kandidatengates bleiben erforderlich.

## NORM-Verwerfungsbedingungen

Die NORM-Unterrolle wird verworfen oder bleibt `NOT_COMPUTABLE`, wenn:

- kein vollstaendiges S/H-Feldresultat erzeugt werden kann;
- S- oder H-Wirkung erst nach Kenntnis eines Ergebnisses gewaehlt wird;
- der Nenner nicht aus dem vollstaendigen aktuellen NORM-Zustand entsteht;
- der Nenner Arm-, Ziel-, Kandidaten- oder Zukunftsinformation liest;
- ein verdeckter globaler Carryzustand entsteht;
- lokale Kanten, F3-Fluesse oder Ressourcenledger verwendet werden;
- B und C bei gleicher globaler Zustandslast nur wegen ihrer Rollenlabels
  verschieden behandelt werden;
- verschiedene Arme verschiedene Konfigurationen benoetigen;
- die Feldwirkung vollstaendig durch A1, B2/B3, B5/B6, M1 oder das
  ortsseparable M5 reproduziert wird;
- nur ein Observeroutput statt der vollstaendigen Feldfortsetzung vorliegt.

## Revidierte A3-Paketrolle

Nach S1-QF besteht A3 aus:

| Unterrolle | Status | Paketwirkung |
|---|---|---|
| SAT | auf M5 reduziert | nur bestehende Observerdiagnostik |
| NORM | eigenstaendige globale Outputgegenprognose | ein fehlender Pflichtfeldarm |

Die Zahl der funktional eigenstaendigen M1-M5-Abschlussrollen aus S1-QC
aendert sich nicht. A3 bleibt eine Adaptergruppe, enthaelt aber nur noch eine
nichtredundante spaetere Feldrolle.

## Fail-Closed-Regeln

S1-QF wird verletzt, wenn spaeter:

- SAT ohne neue nicht-M5-reduzierbare Gegenprognose wiedereroeffnet wird;
- ein SAT-Observerprofil als Feldbaseline ausgegeben wird;
- M5 einen globalen Nenner erhaelt und NORM dadurch still verschluckt;
- NORM als Kandidatenmechanik oder lokale Ressource interpretiert wird;
- NORM eine eigene H-Dynamik erhaelt;
- die globale Skalierung nur in ausgewaehlten Armen aktiv ist;
- eine fehlende NORM-Feldrolle als positives Residuum gilt.

## Aussagegrenze

S1-QF reduziert eine redundante Baselineunterrolle und bindet eine
eigenstaendige globale Gegenprognose. Es gibt weiterhin keine
NORM-Feldgleichung, keine Parameter, keine Implementierung, keinen Feldlauf,
keinen Kandidaten und keinen Befund zu einer hypothetischen MCM-Memory. Der
primaere MCM-Wahrnehmungsfeldkern bleibt unveraendert.

## Genau ein naechster Schritt

Als einziger Anschluss ist zulaessig:

```text
S1-QG - statischer A3-NORM-Zustandsinventar-, Nennerprovenienz- und
        Feldoutputrollenvertrag
```

S1-QG soll ausschliesslich die vollstaendige lokale Zustandsordnung, die
kanonische globale Nennerquelle, die erlaubte S-Beitragsgrenze, die gemeinsame
H-Rolle, atomare Outputs und Fail-Closed-Zustaende von NORM binden. Noch keine
Gleichung, Parameter, Werte, Toleranzen, Implementierung, Fixture,
Runtimeaenderung, Testausfuehrung oder Ergebnisentscheidung.
