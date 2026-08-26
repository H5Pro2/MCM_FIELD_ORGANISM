# S1-QO: Statischer M1-Mehrzeitskalenbank-Bestands-, Nichtduplizierungs- und Falsifikationsaudit

## Status und Umfang

S1-QO prueft ausschliesslich, ob fuer die in S1-QC und S1-QD gebundene feste
Mehrzeitskalenbank M1 eine eigenstaendige technische Gegenprognose verbleibt
und welche vorhandenen Projektkerne dafuer unveraendert wiederverwendbar
waeren.

Geprueft werden:

- der kandidatenfreie A1-Fast-Feldpfad;
- die vorhandenen Carrier-, B3- und W7-N-`LEAK`-Einzelspuren;
- M5_DIRECT als lokale Einzustandsretention;
- der geschlossene lokale Zwei-Zeitskalen-Kandidat und seine historische
  Zwei-Stufen-Gegenbaseline;
- die Abgrenzung gegen Fixed Adapter, Integrator, NORM, M2 und M4;
- die noch fehlende Zustands-, Readout- und Feldkomposition.

Der Audit bindet keine Gleichung, Komponentenanzahl, Zeitkonstante,
Gewichtung, Konfiguration, Implementierung, Fixture oder Ausfuehrung. Es wird
kein Test und kein Feldlauf ausgefuehrt.

Auditentscheidung:

```text
INDEPENDENT_PARALLEL_FIXED_TIMESCALE_COUNTERPREDICTION_REMAINS_DISTINCT
EXISTING_SINGLE_TRACE_KERNELS_ARE_REUSABLE_PRIMITIVES_NOT_AN_M1_BANK
CLOSED_TWO_TIMESCALE_CANDIDATE_AND_CASCADED_HELPER_ARE_NOT_ADMISSIBLE_M1
M1_FIELD_EXECUTION_REMAINS_UNBOUND_PENDING_FINITE_BANK_AND_READOUT_CONTRACT
NO_EQUATIONS_NO_VALUES_NO_IMPLEMENTATION_NO_EXECUTION
```

## Verbindliche M1-Mindestrolle

M1 prueft die einfache Gegenhypothese, dass ein spaeterer Feldverlauf aus
mehreren gleichzeitig getragenen passiven Nachwirkungsspuren mit festen,
unterschiedlichen Zeitrollen erklaert werden kann.

Ein zulaessiger M1-Pfad muss gemeinsam besitzen:

- eine endliche und kanonisch geordnete Spurmenge pro Feldort;
- einen gemeinsamen registrierten Frischstart aller Spuren;
- dieselbe aktuelle lokale Evidence fuer jede Spur;
- eine feste Konfigurationsidentitaet pro Spur und fuer den Readout;
- keine Wechselwirkung zwischen den Spuren;
- keine lokale gemeinsame Ressource und kein Kapazitaetsledger;
- keine Arm-, Ereignis-, Kandidaten- oder Ergebnisinformation;
- einen vorab festen gemeinsamen lokalen signed Readout;
- ein vollstaendiges S/H-Feld mit genau einer Feldzeitfortschreibung;
- dieselbe Bank und denselben Readout fuer alle F/T/I/C/R/U-Geschichten.

Mehrere getrennt ausgewertete Einzel-Leaky-Arme sind kein M1. Ebenso ist eine
erst nach Ergebnissicht zusammengestellte Spurmenge ungueltig.

## Bestandsinventar

| Bestand | Mehrere parallele unabhaengige Spuren | Vollstaendiger M1-Feldpfad | Einordnung |
|---|---|---|---|
| A1 Fast-H | nein | ja | eine feste schnelle Feldrolle, Gegenbaseline |
| `carrier_baselines.independent_leaky_step` | nein, je Aufruf eine Spur | nein | wiederverwendbare mathematische Einzelspur |
| W7-N `LEAK` | nein, je Zustand eine Spur | ueber M5_DIRECT nur als Einzustand | wiederverwendbarer typisierter Einzelspurkern |
| A2/B3 | nein, konkrete einzelne Leaky-Rollen | ja | bestehende Einspur-Gegenbaselines |
| M5_DIRECT | nein, genau ein lokaler Zustand | privat vorhanden | direkte Einzustandsretention |
| historischer Zwei-Stufen-Leaky-Helfer | zwei gekoppelte Stufen | nein | Kaskade, nicht M1 |
| geschlossener lokaler Zwei-Zeitskalen-Kandidat | nein, gekoppelte Rollen | nein | Stabilisierung und Budget; gesperrt |
| M2 | Puffer statt passiver Spurbank | nein | getrennte Delay-/Replayfamilie |
| M4 | konservatives Dreirollenledger | technisch vorhanden | Ressourcenbaseline, nicht M1 |

Kein vorhandenes Modul liefert unveraendert eine vollstaendige M1-Bank mit
atomarem Zustand, festem Readout und gemeinsamem Feldoutput.

## Wiederverwendbare Einzelspuren

### Carrier-Leaky

`carrier_baselines.independent_leaky_step` ist eine reine passive
Einzelspurfortschreibung. Sie liest Vorzustand, aktuellen Kontakt, Intervall
und eine feste Zeitrolle. Zwischen verschiedenen Aufrufen existiert keine
Interaktion.

Der Kern besitzt jedoch nur `CarrierFrame`-Ausgabe. Ihm fehlen:

- ein typisierter Mehrspurzustand;
- eine gemeinsame Konfigurations- und Ordnungsbindung;
- ein gemeinsamer Readout;
- transiente Intervallbindung;
- A1-H-, Feldzeit- und atomare Feldprovenienz.

Er ist deshalb nur ein moeglicher Einzelspurbaustein, kein vorhandener
M1-Kern.

### W7-N-LEAK und M5_DIRECT

W7-N `LEAK` bietet einen typisierten lokalen Zustand und eine
intervallabhaengige Fortschreibung. S1-QN stellt dafuer einen atomaren
Einzustands-Feldpfad bereit.

M1 darf M5_DIRECT nicht mehrfach als getrennte Feldarme ausfuehren und deren
Ergebnisse nachtraeglich kombinieren. Eine zulaessige Wiederverwendung waere
nur eine neue private Bankhuelle, die:

- mehrere unabhaengige W7-N-`LEAK`-Zustaende gemeinsam traegt;
- jeden Zustand aus derselben A1-S-Evidence fortschreibt;
- erst nach vollstaendiger Fortschreibung genau einen festen Readout bildet;
- nur einmal finales S materialisiert und A1-H unveraendert uebernimmt.

Diese Huelle und ihr Readout existieren noch nicht. M5_DIRECT bleibt als
Einzustandsbaseline unveraendert und wird nicht zu M1 erweitert.

## Ausschluss des geschlossenen Zwei-Zeitskalen-Zweigs

`local_synaptic_memory_candidate.py` ist kein zulaessiger M1-Baustein. Seine
Rollen `flexible` und `stabilized` sind nicht unabhaengig:

- die stabilisierte Rolle liest die flexible Rolle;
- die Fortschreibung enthaelt Stabilisierung und zustandsabhaengige
  Freigabe;
- mehrere Relationen teilen ein lokales Budget;
- der Zustand liegt auf gerichteten Relationen statt als anonyme passive
  Spurmenge pro Feldort vor.

Damit traegt der Kern genau die Interaktions- und Kapazitaetsrollen, die M1
nicht besitzen darf. Seine Root-Klassifikation `CLOSED_CANDIDATE` bleibt
verbindlich.

Auch `_advance_two_stage_leaky` aus der historischen passiven
Vergleichskomponente ist kein M1. Die langsame Stufe wird dort aus der
schnellen Stufe gespeist. M1 verlangt dagegen, dass jede Spur denselben
aktuellen lokalen Eingang sieht und keine andere Spur liest.

Weder Modulnamen noch Teile dieser geschlossenen Implementierung duerfen fuer
M1 umbenannt, exportiert oder reaktiviert werden.

## Verbleibende eigenstaendige Gegenprognose

M1 bleibt funktional eigenstaendig, wenn mindestens zwei nicht identische
passive Zeitrollen gleichzeitig mit nicht verschwindendem, vorab festem
Readoutbeitrag getragen werden.

Strukturelle Gegenprognose:

```text
Nach derselben endlichen Exposition und bei anschliessend identischem lokalen
Gap-Input kann M1 gleichzeitig eine schnelle und eine langsamere lokale
Nachwirkung tragen. Der gemeinsame Gap-Verlauf besitzt dann zwei getrennte
feste Zeitanteile. Ein einzelner A1-, B3- oder M5-Zustand mit einer festen
Zeitrolle kann diese allgemeine Zweikomponentenform nicht erzeugen.
```

Diese Prognose behauptet noch keinen Effekt im Projekt. Sie definiert nur,
welcher spaetere Verlauf M1 von Einspurbaselines unterscheiden wuerde.

M1 wird verworfen, wenn eine einzelne vorhandene Zeitrolle das vollstaendige
vorregistrierte Profil unter derselben Geschichte und derselben
Konfiguration reproduziert. Ein Unterschied an nur einem Checkpoint reicht
nicht fuer eine M1-Abgrenzung.

## Nichtduplizierung gegen Pflichtbaselines

### Gegen A1 Fast-H

A1 besitzt genau die vorhandene schnelle H-Nachwirkung. M1 besitzt mehrere
private S-Spuren und darf H nicht veraendern. Wird fuer den Verlauf nur die
A1-H-Rolle benoetigt, ist M1 redundant.

### Gegen B3 und M5_DIRECT

B3 und M5_DIRECT tragen jeweils eine konkrete lokale Retentionsrolle. M1 ist
nur dann eigenstaendig, wenn eine gemeinsam vorregistrierte Mehrspurform das
vollstaendige Profil erklaert und keine Einspurkonfiguration dies leistet.
Mehrere nachtraeglich ausgewaehlte B3- oder M5-Laeufe sind kein fairer Ersatz
fuer eine gleichzeitig getragene Bank.

### Gegen Fixed Adapter und Integrator

Ein Fixed Adapter besitzt keine fortschreitende passive Mehrspur. Ein reiner
Integrator besitzt keine getrennten festen Abschwaechungsrollen. M1 bleibt
nur getrennt, solange keine Spur statisch oder nicht abschwaechend wird.

### Gegen NORM

NORM besitzt genau einen Zustand pro Ort und eine geometrieweite aktuelle
Outputskalierung. M1 muss ortsseparabel bleiben und darf keinen globalen
Nenner lesen. Eine entfernte private Zustandsaenderung darf daher bei
konstanter lokaler Evidence den lokalen M1-Readout nicht direkt veraendern.

### Gegen M2

M2 speichert eine endliche geordnete Eingabefolge und gibt feste fruehere
Positionen wieder. M1 speichert keine Eingaberecords und besitzt keine
Auswahlposition. Entsteht die Prognose nur durch exakten Delay oder Replay,
ist M1 ungueltig.

### Gegen M4

M4 besitzt ein konservatives `free/bound/blocked`-Ledger. M1-Spuren sind
unabhaengig und teilen keine Kapazitaet. Abschwaechung einer Spur darf daher
keine andere Spur freigeben, blockieren oder verstaerken.

## Noch offene Bindungen

Vor einer M1-Implementierung fehlen weiterhin:

- die kleinste endliche Zahl gleichzeitig erforderlicher Spuren;
- die Auswahl genau eines vorhandenen Einzelspurkerns;
- die kanonische Bank-, Frischstart- und Carryanatomie;
- die Bedingung fuer wirklich unterschiedliche feste Zeitrollen;
- eine kleinste endliche signed Readoutfamilie;
- die S/H-Komposition ohne doppelten A1- oder Feldzeitschritt;
- deterministische Fehler- und atomare Ausgabegrenzen;
- eine endliche Testmatrix fuer die Nichtduplizierungsprognose.

`Beliebig viele Spuren`, `beliebige Zeitrollen` oder `beliebiger Readout`
sind nicht falsifizierbar und bleiben gesperrt.

## Paketstatus

Nach S1-QO gilt:

```text
M1_COUNTERPREDICTION_STRUCTURALLY_DISTINCT
NO_ADMISSIBLE_COMPLETE_M1_CORE_PRESENT
SINGLE_TRACE_PRIMITIVES_PRESENT
M1_IMPLEMENTATION_AND_EXECUTION_NOT_AUTHORIZED
MANDATORY_BASELINE_PACKAGE_NOT_EXECUTABLE
```

Eine offene M1-Implementierungsluecke ist kein Kandidatenresiduum und keine
positive Evidenz. Sie sperrt weiterhin den Gesamtvergleich.

## Fail-Closed-Regeln

M1 wird gestoppt oder bleibt gesperrt, wenn:

- eine Spur eine andere Spur als Eingang liest;
- Komponenten Kapazitaet, Normierung oder Ressourcen teilen;
- Zahl, Zeitrolle oder Readout nach Ergebnis oder pro Arm gewechselt werden;
- geschlossene Kandidatenmechanik als Mehrzeitskalenbaseline zurueckkehrt;
- mehrere getrennte Einzelmodelle nachtraeglich als eine Bank gelten;
- H eine M1-spezifische Dynamik erhaelt;
- Delay, Replay, Ereignislabels oder gespeicherte Rohinputs hinzukommen;
- nur Observerwerte statt eines vollstaendigen Feldoutputs verglichen werden;
- das Fehlen eines zulassungsfaehigen M1-Pfads positiv interpretiert wird.

## Aussagegrenze

S1-QO ist ein statischer Baselineaudit. Er bestaetigt keine M1-Wirkung,
keinen Kandidaten und keinen Befund zu einer hypothetischen MCM-Memory. Der
primaere MCM-Wahrnehmungsfeldkern und alle geschlossenen Zweige bleiben
unveraendert.

## Genau ein naechster Schritt

Als einziger Anschluss ist zulaessig:

```text
S1-QP - statischer M1-Minimalfamilien-, Spuranatomie-, Readout- und
        Falsifikationsvertrag
```

S1-QP soll genau eine kleinste endliche parallele Spurfamilie, genau einen
vorhandenen Einzelspurkern, einen vorab festen lokalen Readout und die
Verwerfungsprognose gegen A1, B3 und M5_DIRECT binden. Bleibt keine endliche
nichtduplizierte Familie uebrig, wird M1 als separater Ausfuehrungsarm
gestoppt. Keine Implementierung, Fixture, Testausfuehrung oder
Ergebnisentscheidung.
