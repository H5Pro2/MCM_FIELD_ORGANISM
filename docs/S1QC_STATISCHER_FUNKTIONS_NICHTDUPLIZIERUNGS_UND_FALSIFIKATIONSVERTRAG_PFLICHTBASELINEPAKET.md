# S1-QC: Statischer Funktions-, Nichtduplizierungs- und Falsifikationsvertrag fuer das Pflichtbaselinepaket

## Status und Umfang

S1-QC bindet die kleinste fachlich eigenstaendige Menge von
Baselinefunktionen, die nach S1-QB fuer einen vollstaendigen S1-PX-Vergleich
noch fehlt oder noch keine zulaessige Lebenszyklusoberflaeche besitzt.

Der Vertrag bindet nur Erklaerungsziele, funktionale Trennung,
Expositionspflichten, Ausgabegrenzen und Verwerfungsbedingungen. Er waehlt
keine Gleichung, Parameter, Zustandsdimension, Pufferlaenge, Zeitkonstante,
Gewichte, Werte, Toleranzen, Digests oder Fixture.

S1-QC implementiert keine Baseline, keinen Adapter und keinen Comparator. Es
gibt keine Runtimeaenderung, keinen Test und keinen Feldlauf.

Entscheidung:

```text
MINIMAL_NON_DUPLICATED_S1PX_BASELINE_FUNCTION_PACKAGE_BOUND
FIVE_DISTINCT_CLOSURE_ROLES_WITH_SEPARATE_ADAPTER_ONLY_PACKAGE
NO_EQUATIONS_NO_PARAMETERS_NO_IMPLEMENTATION_NO_EXECUTION
```

## Nichtduplizierungsentscheidung

Die in S1-PX beschriebenen einfacheren Erklaerungen werden nicht automatisch
zu gleich vielen Laufzeitmodellen. S1-QC fasst nur funktional wirklich
aequivalente Rollen zusammen.

| Urspruengliche Erklaerung | S1-QC-Zuordnung | Begruendung |
|---|---|---|
| aktueller Rezeptorkontakt | Adapterpaket A0 | vorhandener zustandsloser Kern |
| schneller H-Nachhall | Adapterpaket A1 | vorhandener aktiver Feldkern ohne Kandidat |
| einzelne Leaky-/Integratorrolle | Adapterpaket A2 | vorhandene B2/B3-Kerne |
| mehrere feste Zeitskalen | fehlende Funktion M1 | nicht durch armweise Einzel-Leaky-Fits ersetzbar |
| Fixed Adapter | Adapterpaket A2 | vorhandener B1-Kern |
| Frozen-E1 | dieselbe Klasse wie B1 | S1-HG zeigt keine getrennte Prognose |
| permanentes Gewicht | dieselbe statische Kopplungsklasse wie B1 | kein zusaetzlicher privater Zustand |
| statische Rekurrenz mit festen Koeffizienten | B1 plus gemeinsamer Feldintegrator | keine eigene adaptive Zustandsrolle |
| feste Verzoegerung | Spezialfall von M2 | ein begrenzter Puffer mit festem Lag |
| Replay | allgemeinerer Fall von M2 | geordnete fruehere Eingabefolge als private Baselinequelle |
| Saettigung und Normalisierung | Adapterpaket A3 | vorhandene W7-N-Kerne, Feldhandoff fehlt |
| Capacity-Clamp | Reduktionsgate M3 | benoetigt Kandidatenangebot/-kapazitaet, daher kein fairer Feldarm |
| DTS-1/T1 | eingefrorene Baselinefamilie M4 | vorhandener geschlossener Dreirollenkern |
| Einzustandsretention | fehlende Funktion M5 | vorhandener Kern ist G2-spezifisch und zu eng |
| G2/D3 | kein eigener neuer Feldarm | endogene Klasse durch Retention, Free/Blocked durch DTS/Clamp geschlossen |
| Linear/F3 Full/CONST-V | Adapterpaket A2 als Zusatzrollen | vorhandene B4-B6-Kerne |

Damit bleiben fuenf getrennte Abschlussrollen M1 bis M5 und vier
Adaptergruppen A0 bis A3. Diese Zaehlung ist eine Vertragsordnung, keine
Implementierungs- oder Laufanzahl.

## Adapterpaket A0 - Zustandsloser aktueller Kontakt

### Funktionsziel

A0 erklaert jede spaetere Differenz ausschliesslich aus dem aktuellen
Rezeptorkontakt. Es traegt keinen privaten Verlauf und setzt H sowie jeden
anderen privaten Zustand auf seine registrierte Nullrolle.

Vorhandener Kern:

```text
carrier_baselines.stateless_baseline
```

### S1-PZ-Pflicht

A0 sieht alle F/T/I/C/R/U-Ereignisse, darf daraus aber keinen Zustand tragen.
An jeder Probe haengt seine Ausgabe nur von der aktuellen wertidentischen
Probe und Geometrie ab.

### Abschlusswirkung

Sind Kandidatenarme bei angeglichenem Eingang trotzdem verschieden, kann A0
diese Differenz nicht erklaeren. Ein Nichtfit von A0 allein ist kein positives
Kandidatenresiduum.

### Verwerfung des Baselineanschlusses

A0 ist ungueltig, wenn der Handoff fruehere Kontakte, Armrollen oder
Kandidatenzustand liest oder kein vollstaendiges S1-QA-Feldresultat liefert.

## Adapterpaket A1 - Kandidatenfreier schneller S/H-Feldkern

### Funktionsziel

A1 prueft, ob der gesamte Verlauf aus dem vorhandenen schnellen S/H-Feldkern
mit genau einer festen H-Konfiguration folgt.

Vorhandener Kern:

```text
advance_neutral_fast_shared_field
advance_neutral_fast_shared_field_transient
```

### S1-PZ-Pflicht

A1 traegt S und H normal durch alle Geschichten und unterliegt denselben
Readoutangleichungen wie jedes andere Modell. Kein zusaetzlicher privater
Zustand ist zulaessig.

### Abschlusswirkung

Reproduziert A1 das vollstaendige F/T/I/C/R/U-Feldprofil, ist eine zusaetzliche
Kandidatenfunktion nicht erforderlich.

### Verwerfung des Baselineanschlusses

A1 ist ungueltig, wenn der Kandidat nicht vollstaendig deaktiviert ist, H
armweise konfiguriert wird oder die S/H-Angleichung anders als beim Kandidaten
erfolgt.

## Adapterpaket A2 - Bestehende B1-B6-Feldintervallkerne

### Funktionsziel

A2 fuehrt die bereits technisch abgenommenen Gegenrollen unveraendert durch
die neue Lebenszyklusgeschichte:

- B1 Fixed Adapter einschliesslich statischer Kopplungsklasse;
- B2 Integrator;
- B3 Local Leaky;
- B4 Linear Coupled;
- B5 F3 Full;
- B6 CONST-V.

### S1-PZ-Pflicht

Jede Rolle besitzt genau einen privaten Frischzustand und eine
Konfigurationsidentitaet ueber alle Arme. Nur die neue aeussere
Expositionshuelle und reine Formuebersetzung duerfen hinzukommen.

### Abschlusswirkung

Jede A2-Rolle schliesst den Kandidaten fuer sich, wenn sie das vollstaendige
S1-QA-Feldprofil mit einem unveraenderten Parametersatz reproduziert.

### Verwerfung des Baselineanschlusses

Eine A2-Rolle ist ungueltig, wenn Gleichung, Zustand, Refinementbedeutung oder
Zeitinterpretation gegen den vorhandenen Kern veraendert werden.

## Adapterpaket A3 - Saettigung und Normalisierung

### Funktionsziel

A3 prueft zwei einfachere Erklaerungen:

- ein unabhaengiger lokaler Zustand mit fester Saettigung;
- ein unabhaengiger lokaler Zustand mit global normalisiertem Output.

Vorhandene Kerne:

```text
w7n_capacity_function_baselines: sat
w7n_capacity_function_baselines: norm
```

### S1-PZ-Pflicht

Beide Rollen muessen alle Geschichten mit jeweils einer festen
Konfigurationsidentitaet tragen. Der Normalisierungsnenner darf nur aus dem
baselineeigenen aktuellen Zustand derselben Geometrie entstehen.

### Abschlusswirkung

A3 schliesst eine scheinbare Konkurrenz- oder Kapazitaetswirkung, wenn
Saettigung beziehungsweise globale Skalierung das vollstaendige Feldprofil
erklaert.

### Verwerfung des Baselineanschlusses

A3 bleibt gesperrt, wenn fuer den S1-QA-Feldhandoff eine neue
Rueckwirkungsgleichung erforderlich ist. Eine reine Datenformabbildung darf
keine neue Dynamik oder Kopplung erzeugen.

## M1 - Feste Mehrzeitskalenbank

### Erklaerungsziel

M1 prueft, ob der beobachtete Verlauf nur aus mehreren unabhaengigen passiven
Spuren mit fest vorregistrierten Zeitskalen entsteht. Die Spuren interagieren
nicht, teilen keine lokale Ressource und besitzen keine Ereignis- oder
Ortslabels.

### Eigene Funktion

M1 darf unterschiedliche schnelle und langsame Nachwirkungen ueberlagern,
ohne eine neue lokale Organisationsrolle anzunehmen. Alle internen Spuren
werden aus demselben aktuellen lokalen Feldinput fortgeschrieben.

### Abgrenzung

- A1 besitzt genau die vorhandene einzelne schnelle H-Rolle.
- B3 besitzt eine einzelne lokale Leaky-Rolle.
- M1 besitzt mehrere gleichzeitig getragene feste passive Spuren in einem
  Modell und einen vorab festen gemeinsamen Readout.

Mehrere nachtraeglich ausgewaehlte Einzelmodelle sind kein M1.

### S1-PZ- und S1-QA-Pflicht

M1 sieht alle F/T/I/C/R/U-Geschichten, traegt alle Spuren vollstaendig und
liefert eine signed S-Fortsetzung. Eine Konfiguration muss Anzahl,
Zeitrollen und Readoutbindung ueber alle Arme unveraendert halten.

### Schliessungsprognose

Reproduziert M1 Bildung, Abschwaechung, Gap-Verlauf und die scheinbaren
Interferenzkontraste gemeinsam, ist keine eigene lokale Ressourcenfunktion
erforderlich.

### Verwerfung

M1 ist ungueltig, wenn Spuren miteinander interagieren, Armrollen lesen,
lokale Kapazitaet teilen, nach dem Ergebnis gewaehlt oder unterschiedlich
konfiguriert werden.

## M2 - Begrenzter Verlaufspuffer fuer Delay und Replay

### Erklaerungsziel

M2 prueft, ob die spaetere Feldwirkung nur aus einer deterministischen,
begrenzten Wiederverwendung frueherer gemeinsamer Eingaben entsteht.

### Zwei eingefrorene Rollen derselben Familie

```text
M2_DELAY  = feste Ausgabe eines vorregistrierten frueheren Eingabeschritts
M2_REPLAY = feste geordnete Ausgabe aus einem begrenzten Eingabepraefix
```

Ein fester Ein-Schritt-Delay ist damit kein zweiter Kern, sondern der
kleinste M2-Pufferfall.

### Informationsgrenze

M2 darf nur die exakten modellneutralen Eingaben speichern, die es selbst
waehrend derselben S1-PZ-Geschichte erhalten hat. Kandidatenzustand,
Kandidatenbilanz, Armname, erwartete Probe und Ergebniswissen sind gesperrt.

M2 ist ausschliesslich eine private Gegenbaseline. Replay bleibt als
Kandidatenmechanik und als Feldkernfunktion verboten.

### S1-PZ- und S1-QA-Pflicht

M2 muss alle Familien mit einer festen Pufferregel und begrenzter Kapazitaet
tragen. Sein Readout muss als vollstaendige S-Fortsetzung vorliegen. Der
Pufferzustand und jede ausgegebene Quellposition muessen passiv belegbar sein.

### Schliessungsprognose

Reproduziert M2 den gesamten Verlauf, ist die spaetere Wirkung durch
gespeicherte beziehungsweise verzoegerte Eingaben erklaert und der Kandidat
geschlossen.

### Verwerfung

M2 ist ungueltig, wenn Pufferlaenge, Lag, Auswahlordnung oder Ausgaberegel
armweise wechseln, ein Zielmuster gesucht wird oder unbegrenzte Geschichte
gespeichert wird.

## M3 - Lokales Capacity-Clamp-Reduktionsgate

### Erklaerungsziel

M3 prueft, ob ein kandidateninterner Commit oder Readoutkontrast nur aus dem
aktuellen Angebot und der aktuell deklarierten lokal verfuegbaren Kapazitaet
folgt.

### Keine ausfuehrbare Feldbaseline

Ein fairer eigenstaendiger Clamp-Feldarm koennte die kandidateninterne freie
Menge nicht erhalten, ohne Kandidateninformation zu lesen. Eine eigene
Kapazitaetsdynamik wuerde dagegen eine neue Retentions- oder
Dreirollenbaseline einfuehren.

M3 bleibt deshalb ein hartes algebraisches Reduktionsgate innerhalb des
Kandidatenaudits und ist kein F/T/I/C/R/U-Modellarm. Diese Einordnung
praezisiert die S1-QA-Pflichtbaselinegrenze, ohne den Clamp zu entfernen.

### S1-QA-Pflicht

Ein spaeterer Kandidat muss sein eigenes vollstaendiges Angebot und seine
eigene aktuelle Kapazitaet vor jedem relevanten Commit offenlegen. Der
passive M3-Comparator prueft die registrierte minimale Clamp-Erklaerung, ohne
den Kandidaten fortzuschreiben.

### Schliessungsprognose

Stimmt der gesamte relevante Kandidatenkontrast mit M3 ueberein und verbleibt
keine andere kausale Feldprognose, wird die betreffende Kapazitaetsfunktion
als Clamp-reduziert geschlossen.

### Verwerfung des Gates

M3 ist ungueltig, wenn es verdeckte Kandidatenwerte liest, einen Zustand
fortschreibt, Freigabe simuliert oder eine neue Gleichung in den Comparator
einfuehrt.

## M4 - Eingefrorene DTS-1/T1-Dreirollenbaseline

### Erklaerungsziel

M4 prueft, ob der gesamte Verlauf durch die bereits geschlossene technische
Trajektorie `free/bound/blocked` einschliesslich ihrer vorhandenen
Feldrueckwirkung erklaert wird.

### Eingefrorener Bestand

- DTS-1 liefert den vorhandenen gekoppelten Feldpfad.
- T1 liefert die vorhandene parameterfreie lokale Dreirollenprojektion als
  strukturelle Kontrolle.

M4 ist keine neue Kombination und keine Kandidatenwiedereroeffnung. Der
DTS-1-Feldpfad ist die ausfuehrbare Baseline; T1 prueft nur, dass keine
zusaetzliche Rollenfunktion eingeschmuggelt wird.

### S1-PZ- und S1-QA-Pflicht

M4 muss dieselben normalen Geschichten ohne alte Recovery-on/off-Sidecars
sehen. Bestehende Rollen, Gleichungen und lokale Bilanz bleiben
unveraendert. Eine neue private Bruecke darf nur Expositionsform und
Resultatform uebersetzen.

### Schliessungsprognose

Reproduziert der eingefrorene DTS-1-Pfad das vollstaendige Feldprofil und
bleibt seine Ledgertrajektorie T1-rekonstruierbar, ist kein neuer Kandidat
jenseits der Dreirollenbaseline erforderlich.

### Verwerfung

M4 ist ungueltig, wenn alte Sidecars, Kandidatenrollen, neue Recoveryregeln,
geaenderte Raten oder eine umbenannte G2-Unterteilung verwendet werden.

## M5 - Allgemeine Einzustands-Retentionsbaseline

### Erklaerungsziel

M5 prueft, ob alle spaeteren Unterschiede aus genau einem unabhaengigen
zustandsbehafteten Retentionswert pro registriertem Ort folgen.

### Eigene Funktion

Der Zustand wird durch jede normale Exposition nach derselben stationaeren
Regel fortgeschrieben und wirkt ueber einen vorab festen Readout auf die
vollstaendige S-Fortsetzung. Es gibt keine Rollenunterteilung, lokale
Ressourcenkonkurrenz, Sequenzsuche oder Replayfolge.

### Abgrenzung

- B3 ist eine vorhandene konkrete Local-Leaky-Baseline.
- M5 ist die allgemein registrierte Einzustands-Retentionsgegenrolle fuer
  alle Expositionsarten.
- M1 besitzt mehrere passive Zustandsrollen.
- M4 besitzt drei konservativ gekoppelte Ressourcenrollen.

Der vorhandene G2-Retentionskern bleibt Quellreferenz, kann aber wegen seiner
Zwei-Ereignis- und Skalarcheckpointbindung nicht unveraendert als M5 gelten.

### S1-PZ- und S1-QA-Pflicht

M5 sieht alle F/T/I/C/R/U-Geschichten, traegt genau einen Zustand pro Ort und
liefert ein vollstaendiges Feldresultat. Ein Parametersatz muss alle Arme
gemeinsam erklaeren.

### Schliessungsprognose

Reproduziert M5 den gesamten Lebenszyklus, ist die beobachtete Wirkung auf
eine einfache Retention reduzierbar.

### Verwerfung

M5 ist ungueltig, wenn weitere verborgene Zustaende, armweise Regeln,
Kontaktlabels, Ereigniszaehler, Puffer oder kandidatenabhaengige Inputs
benoetigt werden.

## G2/D3 als struktureller Reduktionsaudit

G2/D3 erhaelt keinen neuen Laufzeitarm. Vor einer spaeteren Kandidatenzulassung
wird rein strukturell geprueft:

- Ist eine behauptete neue Unterteilung nur eine gesetzte G2/D3-Koordinate?
- Ist ihre endogene Bildung durch M5-Retention rekonstruierbar?
- Ist ihr Free/Blocked-Anteil durch M3 oder M4 rekonstruierbar?

Trifft eine dieser Bedingungen zu, wird der Kandidat ohne neue G2-Ausfuehrung
geschlossen. Die historischen G2/D3-Operatoren bleiben technische
Referenzobjekte.

## Gemeinsame Schliessungs- und Falsifikationsregel

Fuer A0 bis A3 sowie M1, M2, M4 und M5 gilt spaeter:

- dieselbe S1-PZ-Geschichte;
- derselbe gemeinsame Feld- und Rezeptorinput;
- ein eigener vollstaendiger Frischzustand;
- genau eine Konfiguration pro Modell;
- vollstaendige private Zustandsprovenienz;
- vollstaendige signed S-Fortsetzungen in S1-QA-Reihenfolge;
- keine armweise Passung oder nachtraegliche Modellauswahl.

M3 und G2/D3 bleiben vorgelagerte passive Reduktionsaudits und erhalten keine
eigene Feldarmbewertung.

Eine Baseline schliesst einen Kandidaten nur, wenn sie nach spaeter
vorregistrierter Aequivalenzregel das vollstaendige gemeinsame Feldprofil
reproduziert. Ein einzelner Arm oder Checkpoint reicht nicht.

Erklaert keine Baseline den Verlauf, folgt daraus noch kein
Funktionsnachweis. Erst alle Kandidatengates aus S1-QA und eine getrennte
Evidenzentscheidung koennen einen technischen Residualstatus bewerten.

## Paketweite Verwerfungsbedingungen

Das Pflichtbaselinepaket ist ungueltig, wenn:

- funktional verschiedene Rollen still zusammengelegt werden;
- aequivalente Rollen nur zur Erhoehung der Baselinezahl dupliziert werden;
- eine Baseline eine andere Geschichte oder S/H-Angleichung sieht;
- ein Adapter eine neue Dynamik statt einer Formabbildung einfuehrt;
- M2 als Kandidat oder aktive Feldfunktion erscheint;
- M3 Kandidatenwerte als ausfuehrbarer Baselinezustand uebernimmt;
- M4 geschlossene DTS-/T1-Regeln veraendert;
- M5 mehr als eine private Zustandsrolle benoetigt;
- G2/D3 ohne neue eigene Gegenprognose wieder ausgefuehrt wird;
- eine fehlende oder inkompatible Baseline als positives Residuum gewertet
  wird.

## Aussagegrenze

S1-QC bindet nur das Baselinepaket, gegen das ein spaeterer Kandidat bestehen
muesste. Es gibt weiterhin keinen Kandidaten, keine neue Baselinegleichung,
keine Implementierung und keinen Befund zu einer hypothetischen MCM-Memory.
Der primaere MCM-Wahrnehmungsfeldkern bleibt unveraendert.

## Genau ein naechster Schritt

Als einziger Anschluss ist zulaessig:

```text
S1-QD - statischer Zustands-, Handoff- und Ausgabevertrag fuer
        A0-A3 sowie M1-M5
```

S1-QD soll ausschliesslich die kleinsten privaten Zustandsrollen,
Initialisierungsgrenzen, gemeinsamen Eingaben, vollstaendigen Ausgaben und
Fail-Closed-Schemata der Baselinepaketrollen binden. M3 bleibt zustandsloser
Reduktionsaudit. Noch keine Updategleichung, Parameter, Werte, Toleranzen,
Implementierung, Fixture, Runtimeaenderung, Testausfuehrung oder
Ergebnisentscheidung.
