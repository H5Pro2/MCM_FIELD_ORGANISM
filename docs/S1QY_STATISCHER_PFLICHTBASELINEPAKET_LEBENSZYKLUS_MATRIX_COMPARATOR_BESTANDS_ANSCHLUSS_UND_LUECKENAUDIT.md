# S1-QY: Statischer Pflichtbaselinepaket-Lebenszyklus-, Matrix- und Comparator-Bestandsaudit

## Status und Umfang

S1-QY prueft ausschliesslich, welche vorhandenen Projektoberflaechen fuer den
in S1-PZ, S1-QA und S1-QC gebundenen gemeinsamen Pflichtbaselinevergleich
unveraendert oder durch reine Formadapter anschliessbar sind.

Der Audit:

- waehlt keine neue Kandidatenmechanik;
- bindet keine Gleichung, Parameter, Werte, Toleranzen oder Fixture;
- implementiert keinen Adapter, Lebenszyklus, Runner, Matrix oder Comparator;
- fuehrt keinen Test und keinen Feldlauf aus;
- wertet keine historischen Laufresultate neu aus;
- trifft keine Ergebnis- oder Funktionsentscheidung.

Auditentscheidung:

```text
INDIVIDUAL_FIELD_ARMS_PARTLY_COMPLETE_AND_REUSABLE
COMMON_MODELLNEUTRAL_ARM_PROTOCOL_AND_LIFECYCLE_ENVELOPE_ABSENT
COMMON_ATOMIC_MATRIX_BUNDLE_AND_S1QA_GATE_COMPARATOR_ABSENT
HISTORICAL_PROFILE_ORCHESTRATORS_NOT_ADMISSIBLE_AS_COMMON_PACKAGE
MANDATORY_BASELINE_PACKAGE_REMAINS_NOT_EXECUTABLE
NO_IMPLEMENTATION_NO_EXECUTION_NO_RESULT_DECISION
```

## Verbindliche Solloberflaeche

Der spaetere Vergleich muss zwei bereits gebundene Vertragsachsen gemeinsam
erfuellen:

1. S1-PZ liefert fuer Kandidat und alle zustandsbehafteten Baselines dieselbe
   kausale F/T/I/C/R/U-Vorgeschichte mit den Rollen `HISTORY_A`,
   `HISTORY_B_LOCAL`, `HISTORY_C_REMOTE`, `GAP_ZERO_CONTACT`, `PROBE_A`,
   `PROBE_B`, `ALIGN_READOUT_SH` und `OBSERVE`.
2. S1-QA verlangt ein atomar vollstaendiges Beobachtungsbuendel und die
   passive Auswertung in der dort festgelegten 17-Gate-Reihenfolge.

Ein vorhandener Einzelintervallkern ist deshalb noch kein ausfuehrbares
Pflichtbaselinepaket. Zwischen Einzelkern und Comparator werden mindestens
eine gemeinsame Armoberflaeche, ein kausaler Lebenszyklus, vollstaendige
Checkpoints und ein atomarer Matrixabschluss benoetigt.

## Bestandsinventar der Feldarme

| Rolle | Vorhandener technischer Stand | Anschlussstatus |
|---|---|---|
| A0 aktueller Kontakt | feldnativer, zustandsloser Vollfeldpfad vorhanden | nur gemeinsame Lebenszyklus- und Receipt-Huelle fehlt |
| A1 schneller S/H-Nachhall | synchrone und transiente Vollfeldkerne vorhanden | nur gemeinsame Lebenszyklus- und Receipt-Huelle fehlt |
| A2 B1-B6 | vollstaendige private Intervalladapter vorhanden | Kerne wiederverwendbar; alte DTS-1-Profil- und Geometriebindung nicht als gemeinsame Huelle zulaessig |
| A3 NORM | privater atomarer `REPLACE_S`-Kompositor vorhanden | durch reinen Armadapter anschliessbar |
| A3 SAT | als eigener Feldzweig gestoppt | kein Arm; nur Observerdiagnostik bleibt erhalten |
| M1 | privater atomarer Zweispurkompositor vorhanden | durch reinen Armadapter anschliessbar |
| M2 DELAY/REPLAY | private atomare Zwei-Modus-Pufferkompositoren vorhanden | zwei getrennte Armrollen unter derselben M2-Familie anschliessbar |
| M3 Capacity-Clamp | nur zustandsloses Reduktionsgate gebunden | kein Feldarm; passives Schema fehlt weiterhin |
| M4 DTS-1/T1 | geschlossener technischer Dreirollenkern vorhanden | neue neutrale Baselinehuelle fehlt; alte Sidecars bleiben gesperrt |
| M5 DIRECT | privater atomarer Einzustandskompositor vorhanden | durch reinen Armadapter anschliessbar |

Die privaten A3-, M1-, M2- und M5-Resultate besitzen bereits die wesentlichen
atomaren Eigenschaften: vollstaendiges Folgefeld, vollstaendiger privater
Folgezustand, kanonische Provenienz und `NOT_COMPUTABLE` ohne Teiloutput.
Ihre konkreten Typen, Feldnamen und Receipts sind jedoch verschieden. Eine
Matrix darf diese Unterschiede nicht durch typunsichere Fallunterscheidungen
oder Zugriff auf modellinternen Zustand aufloesen.

## Wiederverwendbare gemeinsame Primitive

Folgende Bestandsrollen koennen unter einer neuen, engeren Huelle erhalten
bleiben:

- kanonische Rezeptorverteilungen, synchrone und transiente Feldintervalle;
- vollstaendige `SharedMCMField`-Uebergaben und Feld-, Geometrie- und
  Zeitidentitaeten;
- getrennte Digests fuer Eingabe, Intervall, Konfiguration, Privatstatus,
  Folgefeld und Receipt;
- vorhandene Frischzustandsfabriken der einzelnen Baselinefamilien;
- atomare Erfolgs- beziehungsweise `NOT_COMPUTABLE`-Ausgaben der neuen
  privaten Kompositoren;
- passive Snapshot-Distanzprimitive ohne Feldfortschreibung.

`dynamic_substrate_dts1_common_interval_materializer` und die privaten
B1-B6-Adapter belegen, dass reine Materialisierung und vollstaendige
Intervallausgaben technisch moeglich sind. Ihre DTS-1-spezifischen Rollen,
registrierten Altgeometrien und Profilannahmen duerfen nicht unveraendert zur
allgemeinen S1-PZ-Huelle erklaert werden.

## Fehlende gemeinsame Armoberflaeche

Es existiert noch kein einheitlicher Vertrag, der fuer jeden ausfuehrbaren
Arm gemeinsam und ohne Modellwissen festlegt:

- stabile Arm- und Familienidentitaet;
- unveraenderte Konfigurationsidentitaet ueber alle Geschichten;
- Frischstart und vollstaendigen privaten Carry;
- genau einen gemeinsamen Intervallinput;
- genau ein vollstaendiges Folgefeld und einen vollstaendigen
  Privatfolgezustand;
- passive, typisierte Privatstatus- und Ausgabedigests;
- atomaren Fehlerstatus ohne Feld- oder Zustandsrest;
- ein zeitloses `ALIGN_READOUT_SH`, das keinen privaten Zustand veraendert.

Die gemeinsame Huelle darf keine Baselinegleichung kennen. Sie darf nur die
jeweilige private Adapterfunktion aufrufen, deren vollstaendiges Ergebnis
validieren und es in ein einheitliches Resultatschema ueberfuehren.

## Lebenszyklusbestand und Luecke

S1-PZ bindet die Ereignisrollen und die faire Kausalhistorie vollstaendig auf
Vertragsebene. Es existiert aber kein gemeinsamer ausfuehrbarer Lebenszyklus,
der diese Rollen fuer A0, A1, A2, A3-NORM, M1, beide M2-Modi, M4 und M5 mit
getrennten Frischzustaenden fortschreibt.

Der vorhandene `dynamic_substrate_dts1_one_replica_orchestrator` ist keine
zulaessige Loesung. Er traegt historische Profilnamen, feste Refinements,
spezialisierte Geometrien und alte Ausfuehrungspfade. Seine Wiederverwendung
wuerde S1-PZ an eine geschlossene Versuchshistorie koppeln und die neue
modellneutrale Expositionsbindung verletzen.

Damit gilt:

```text
S1PZ_EVENT_CONTRACT_PRESENT
COMMON_EXECUTABLE_LIFECYCLE_ENVELOPE_ABSENT
HISTORICAL_ORCHESTRATOR_REUSE_PROHIBITED
```

## Matrixbestand und Luecke

Im Projekt existieren mehrere historische Matrizen und profilgebundene
Ausfuehrungstabellen. Keine davon bildet gemeinsam:

- die aktuelle, reduzierte Pflichtarmmenge aus S1-QC und S1-QF;
- alle S1-PZ-Familien mit identischer kausaler Vorgeschichte;
- getrennte Frischstarts und durchgaengigen Carry je Arm;
- dieselben registrierten Beobachtungszeitpunkte;
- atomare Vollstaendigkeit aller Arme und Checkpoints;
- die spaetere S1-QA-Comparatorreihenfolge.

Insbesondere wird keine alte 24-Fall-Matrix fortgesetzt oder umbenannt. Ihre
Profile sind nicht automatisch kausal aequivalent zur aktuellen
F/T/I/C/R/U-Bindung. Eine neue Matrix darf erst nach einem gemeinsamen
Arm- und Lebenszyklusvertrag statisch festgelegt werden.

## Comparatorbestand und Luecke

`controlled_probe_baseline_comparison` ist als passives technisches
Distanzprimitiv wiederverwendbar. Es vergleicht kompatible Feldsnapshots,
schreibt keinen Zustand fort und berechnet Aktivierungs- und
Nachhallabstaende.

Es ist jedoch kein S1-QA-Comparator, weil es nicht prueft:

- Expositionsprovenienz und Konfigurationskonstanz;
- Vollstaendigkeit aller Familien, Arme und Checkpoints;
- private Zustandsprovenienz;
- eine spaetere Kandidatenbilanz und M3-Reduktion;
- die festgelegte 17-Gate-Reihenfolge;
- atomare Paketungueltigkeit bei einem fehlenden Teilresultat.

Historische Evaluatoren mit eingebauten Profilnamen, Schwellen oder
Entscheidungslogik duerfen ebenfalls nicht als allgemeiner Comparator
uebernommen werden. Der spaetere S1-QA-Comparator muss rein passiv bleiben
und darf weder Modelle importieren noch einen Runner ausloesen.

## Anschlussklassen

### Direkt durch reine Formadapter anschliessbar

- A0 und A1 nach Bindung eines gemeinsamen zustandslosen beziehungsweise
  feldgetragenen Carryschemas;
- A3-NORM, M1, M2-DELAY, M2-REPLAY und M5-DIRECT ueber ihre bereits atomaren
  privaten Resultate;
- das vorhandene Snapshot-Distanzprimitiv als untergeordnete Messfunktion.

### Nur nach neutraler Brueckenentscheidung anschliessbar

- A2/B1-B6, weil die Kerne vorhanden, ihre aktuelle gemeinsame
  Adapteroberflaeche aber an alte DTS-1-Registrierungen gebunden ist;
- M4, weil der geschlossene Dreirollenkern erhalten bleibt, aber noch keine
  S1-PZ-neutrale Baselinehuelle besitzt.

### Nicht als Feldarm anschliessbar

- A3-SAT, statische Rekurrenz und G2/D3 als neue Arme;
- M3, das ausschliesslich passives Reduktionsgate bleibt;
- alte Recovery-Sidecars, Frozen-E1 und historische Profilorchestratoren.

## Abhaengigkeitsordnung

Die fehlenden Schichten muessen in folgender Reihenfolge geschlossen werden:

```text
1. gemeinsamer Baselinearm- und Carryvertrag
2. modellneutraler S1-PZ-Lebenszyklusvertrag
3. statische Arm-/Familien-/Checkpointmatrix
4. atomares Gesamtresultatbuendel
5. passiver S1-QA-Gate-Comparator
6. erst danach Implementierungs- und Testvertrag
```

Matrix oder Comparator vor dem Arm- und Lebenszyklusvertrag wuerden
unterschiedliche private APIs nachtraeglich angleichen. Das waere methodisch
nicht pruefbar und bleibt gesperrt.

## Paketweite Fail-Closed-Regeln

Das Pflichtbaselinepaket bleibt `NOT_EXECUTABLE`, wenn:

- ein Arm eine andere relevante Vorgeschichte oder Readoutangleichung sieht;
- eine alte Profil-ID die neue Ereignisrolle bestimmt;
- ein gemeinsamer Adapter Baselinegleichung, Parameter oder Zustand auslegt;
- Konfiguration oder privater Zustand zwischen Armen geteilt wird;
- ein Fehler Feld oder Folgezustand als Teiloutput freigibt;
- ein fehlender Arm, Checkpoint oder Digest uebersprungen wird;
- M3 als Feldarm oder G2/D3 als neuer Kandidat erscheint;
- Comparator oder Matrix selbst Modelle fortschreiben;
- ein inkompatibler Baselineanschluss als positives Residuum gilt.

## Aussagegrenze

S1-QY weist keine Funktion nach und erzeugt keinen Befund zu einer
hypothetischen MCM-Memory. Der Audit bestaetigt nur, dass mehrere benoetigte
Baselinekerne technisch vorhanden sind, waehrend ihre gemeinsame faire
Ausfuehrungs- und Vergleichsoberflaeche noch fehlt. Der primaere
MCM-Wahrnehmungsfeldkern bleibt unveraendert.

## Genau ein naechster Schritt

Als einziger Anschluss ist zulaessig:

```text
S1-QZ - statischer gemeinsamer Baselinearm-, Carry- und
        S1-PZ-Lebenszyklus-Huellenvertrag
```

S1-QZ soll ausschliesslich die einheitliche Armidentitaet, Frischstart- und
Carryrollen, Intervalluebergabe, atomare Resultatform, passive Provenienz und
die modellneutrale Abbildung der S1-PZ-Ereignisrollen binden. Fuer A2 und M4
muss es die Grenze zwischen reiner Bruecke und unzulaessiger
Funktionsaenderung festlegen. Noch keine Matrixwerte, Comparatorentscheidung,
Implementierung, Fixture, Testausfuehrung oder Feldlauf.
