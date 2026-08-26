# S1-RB: Statischer A2/B1-B6- und M4-Brueckenkompatibilitaetsaudit gegen S1-QZ und S1-RA

## Status und Umfang

S1-RB prueft ausschliesslich am vorhandenen Codebestand, ob die sechs
A2-Baselinekerne und der geschlossene M4-DTS-1/T1-Bestand ohne
Funktionsaenderung an die gemeinsame S1-QZ-Huelle und die S1-RA-Matrix
angeschlossen werden koennen.

Der Audit:

- liest vorhandene Kern-, Adapter-, Materialisierungs-, Orchestrator- und
  Validierungsoberflaechen;
- fuehrt keinen Test und keinen Feldlauf aus;
- implementiert keine Bruecke, Frischzustandsfabrik oder Resultathuelle;
- bindet keine Geometrie, Parameter, Konfiguration, Refinementstufe oder
  Fixture;
- veraendert keine Gleichung, Mappingregel oder geschlossene Baseline;
- trifft keine Baseline-, Kandidaten- oder Funktionsentscheidung.

Auditentscheidung:

```text
A2_B1_B6_INTERVAL_KERNELS_PROFILE_BLIND_AND_FUNCTION_PRESERVING_BRIDGEABLE
A2_CURRENT_MATERIALIZER_FRESH_FACTORY_AND_ORCHESTRATOR_NOT_S1QZ_ADMISSIBLE
A2_REMAINS_CONDITIONALLY_CONNECTABLE_PENDING_NEUTRAL_BRIDGE
M4_DTS1_CORE_ACCEPTS_NORMAL_CONTACT_AND_ZERO_CONTACT_WITHOUT_RECOVERY_SIDECAR
M4_FRESH_CONFIGURATION_ATOMIC_WRAPPER_AND_GENERAL_T1_VALIDATION_UNBOUND
M4_REMAINS_NOT_CONNECTABLE_PENDING_T1_ROLE_CLARIFICATION
MANDATORY_BASELINE_PACKAGE_REMAINS_NOT_EXECUTABLE
NO_IMPLEMENTATION_NO_EXECUTION_NO_RESULT_DECISION
```

## Auditkriterien

Ein vorhandener Kern gilt nur dann als prinzipiell brueckbar, wenn gemeinsam
gilt:

- der eigentliche Intervallaufruf liest keine S1-PZ-Familie, Replik,
  Ereignisrolle, Zielrichtung oder Ergebnisreferenz;
- normaler Kontakt und normaler Nullkontakt gelangen ueber denselben
  technischen Eingabekanal in den Kern;
- Modellkonfiguration und privater Carry bleiben rollenfest;
- Feld und privater Folgezustand entstehen gemeinsam aus genau einem
  Vorzustand;
- eine neue Huelle muesste nur Typ, Provenienz und Fehlerstatus abbilden;
- keine alte Profilfolge, Recovery-Intervention oder neue Gleichung ist fuer
  die Funktion erforderlich.

Eine vorhandene historische Ausfuehrung ist kein Anschlussnachweis. Eine
technisch moegliche neue Bruecke ist ebenfalls noch keine implementierte
S1-QZ-Oberflaeche.

## A2-Bestandsoberflaechen

### Profilblinder Intervallkern

`dynamic_substrate_dts1_private_baseline_adapters.py` stellt mit
`advance_dts1_private_baseline` einen gemeinsamen Intervallaufruf fuer B1 bis
B6 bereit. Dessen Modelleingabe besteht technisch aus:

- vollstaendigem materialisiertem Feld;
- einer Rezeptorverteilung;
- einem abgeschlossenen Feldintervall;
- einem aeusseren Geometriedigest;
- rollengetrenntem Privatstatus, Konfigurationsdigest und Refinement.

Der Aufruf erhaelt keinen Profilnamen, keine Expositionsfamilie, keinen
Checkpoint, kein erwartetes Vorzeichen und kein Ergebnis. Die Auswahl B1 bis
B6 folgt ausschliesslich aus der festen Modellrolle im privaten Kontext.

Damit ist die eigentliche Kernoberflaeche mit der S1-QZ-Trennung von
`MODEL_ROLE` und `REPLICA_ROLE` vereinbar.

### Rollengetrennte A2-Funktionen

| Rolle | Vorhandener Kernpfad | Statischer Brueckenbefund |
|---|---|---|
| B1 Fixed Adapter | fester Backreaction-Payload und vollstaendiger Feldschritt | profilblind, rollenfeste Konfiguration, privater Zustand unveraendert |
| B2 Integrator | vollstaendiger lokaler L-Zustand und Referenzmodellschritt | profilblind, vollstaendiger Privatfolgezustand vorhanden |
| B3 Local Leaky | F3-Feldpfad mit lokalem Leaky-Calculator | profilblind, eingebetteter M-Zustand bleibt rollenprivat |
| B4 Linear Coupled | F3-Feldpfad mit linearem Calculator | profilblind, eingebetteter M-Zustand bleibt rollenprivat |
| B5 F3 Full | unveraenderter voller F3-Calculator | profilblind, eingebetteter M-Zustand bleibt rollenprivat |
| B6 CONST-V | eingefrorene CONST-V-Spezifikation im F3-Feldpfad | profilblind, Spezifikationsdigest und M-Zustand vollstaendig belegt |

Alle sechs Pfade liefern ein `DTS1PrivateBaselineAdapterOutput` aus
vollstaendigem Feld, vollstaendigem Privatfolgezustand, technischer Diagnostik
und Eigendigest. Der Adapter veroeffentlicht bei intern abgefangenen
Kernfehlern kein teilweises Erfolgsobjekt.

Die aktuelle Fehleroberflaeche wirft jedoch eine Ausnahme und liefert noch
kein gemeinsames S1-QZ-`NOT_COMPUTABLE`-Resultat. Das kann nur durch eine
neue atomare Formhuelle geschlossen werden.

## A2-Kontakt- und Gap-Kompatibilitaet

Der eigentliche A2-Aufruf liest eine normale `ReceptorDistribution` und ein
positives `MCMFieldStepTime`. Ein Gap benoetigt kein Rollenflag: Eine
registrierte Nullkontaktverteilung kann ueber denselben Aufruf verarbeitet
werden wie eine Kontaktverteilung.

B1 und B2 tragen dabei ihre jeweiligen normalen Feld- beziehungsweise
Integratorzustaende fort. B3 bis B6 tragen ihr eingebettetes M und den
vollstaendigen Feldzustand weiter. Es gibt im Kern keinen Recovery-on/off-
Schalter und keine Profilverzweigung.

Die vorhandene A2-Oberflaeche akzeptiert nur einen synchronen
Verteilungsabschluss pro Aufruf. S1-PZ schreibt keine transiente
Intervallform vor. Eine spaetere gemeinsame Registrierung ist deshalb nur
dann ohne Kernwechsel anschliessbar, wenn ihre Geschichten in zulaessige
synchrone technische Intervalle zerlegt werden. Eine transiente Eingabe darf
nicht durch eine angeblich reine Bruecke nachgebildet werden.

## A2-Geometrie- und Konfigurationsgrenze

Die Funktion `_mapping` akzeptiert ausschliesslich die zwei vorhandenen
S1-JV-Geometriezeilen:

- Zwei-Knoten-Offenlinie;
- Drei-Knoten-Offenlinie.

Sie validiert Feld-, Layer-, Geometrie-, Knoten- und interne
Kantendigestrollen exakt. Die Drei-Knoten-Offenlinie stellt prinzipiell drei
unterscheidbare Orte bereit; S1-RB registriert sie aber noch nicht als
A/B/C-Geometrie und bewertet keine Lastanpassung.

Eine A2-Bruecke darf keine neue Mappingzeile anlegen. Deshalb gilt:

```text
EXISTING_THREE_NODE_GEOMETRY_MAY_BE_TESTED_FOR_LATER_S1PZ_REGISTRATION
ANY_OTHER_GEOMETRY_REQUIRES_A_NEW_CORE_CONTRACT_AND_IS_NOT_A_PURE_BRIDGE
```

Auch die B1-B6-Konfigurationsdigests, B1-Payloads, B3-B6-Laufzeitrecords und
die fuer B3-B6 akzeptierten Refinementrollen sind im Bestand fest gebunden.
Sie koennen als ein unveraenderter Modellregistrierungsbeleg weiterverwendet
werden. Die Huelle darf sie nicht neu waehlen, erweitern oder
replikabhaengig variieren.

## Nicht zulaessige A2-Aussenhuellen

Folgende vorhandene Schichten sind nicht als S1-QZ-Huelle wiederverwendbar:

### S1-JO-Materializer

`dynamic_substrate_dts1_common_interval_materializer.py` akzeptiert nur 23
kanonische historische Fixtures. Es validiert Sequenzdigest, Ordinal,
Checkpointrolle und registrierte Vorzustandsdirektive gegen diesen endlichen
Bestand. Damit ist es eine korrekte historische Materialisierung, aber keine
modellneutrale F/T/I/C/R/U-Intervallhuelle.

### S1-JZ-/S1-K*-Frischzustandsweg

Die vorhandene Frischzustandsfunktion liegt privat im historischen
Ein-Replik-Orchestrator. Sie liest S1-JZ-Exemplarrecords und ist an dessen
Geometrie- und Ausfuehrungsvertraege gekoppelt. Obwohl die Auswahl intern
nur Modellrolle und Geometrie verwendet, darf diese private
Orchestratorfunktion nicht zur neuen allgemeinen Frischfabrik hochgestuft
werden.

### Historischer Ein-Replik-Orchestrator

`dynamic_substrate_dts1_one_replica_orchestrator.py` steuert Profilblock,
Sequenzschluessel, Refinementvergleich, Checkpoints und signed
Vergleichskomponenten. Diese Informationen gehoeren nach S1-QZ
ausschliesslich in die neue aeussere Huelle und duerfen nicht als
Modellinput oder Resultatordnung uebernommen werden.

## A2-Anschlussentscheidung

Fuer alle sechs Rollen gilt gemeinsam:

```text
PRIVATE_INTERVAL_KERNEL_PRESENT
NORMAL_CONTACT_AND_ZERO_CONTACT_CHANNEL_PRESENT
COMPLETE_FIELD_AND_PRIVATE_NEXT_STATE_PRESENT
NO_KERNEL_EQUATION_CHANGE_REQUIRED
NEUTRAL_FRESH_FACTORY_INVOCATION_BRIDGE_AND_ATOMIC_S1QZ_RECEIPT_ABSENT
CONDITIONALLY_CONNECTABLE_NOT_YET_CONNECTED
```

Eine spaetere reine Bruecke waere nur zulaessig, wenn sie eine bereits
vorhandene S1-JV-Geometrie und exakt die vorhandene Rollenregistrierung
verwendet. Scheitert die spaetere A/B/C-Geometriepruefung, werden A2 oder die
Matrix nicht durch eine neue Mappingregel repariert.

## M4-DTS-1-Kernbestand

`advance_dts1_coupled_fast_shared_field` ist ein privater atomarer
Intervallkern aus:

- vollstaendigem gemeinsamen Feld;
- vollstaendiger DTS-1-Ressourcenanatomie;
- normaler Rezeptorverteilung und Feldzeit;
- festen Feld- und DTS-1-Konfigurationen;
- einem festen Backreactionstatus.

Der Kern liefert gemeinsam:

- vollstaendiges Folgefeld;
- vollstaendige Folgeanatomie;
- Beteiligungs- und Transferledger;
- den angewendeten Backreactionbeleg;
- abgeschlossene Intervallzeit.

Er liest keinen Profilnamen, keine S1-PZ-Rolle, keinen Checkpoint und kein
Ergebnis. Seine Geometrie folgt dem vollstaendigen Feld- und
Anatomieinventar und ist nicht auf die historischen S1-JV-Zeilen begrenzt.

## M4-Normalgap ohne Recovery-Sidecar

Der DTS-1-Kern berechnet Beteiligung aus dem normalen schnellen
Feldvorzustand und schreibt die drei Rollen mit demselben festen
`DTS1StepRates`-Objekt fort. Eine Nullkontaktverteilung wird ueber denselben
Feldschritt wie ein Kontaktintervall verarbeitet.

Die in historischen Audits verwendeten Recovery-on/off-Dateien sind fuer
diesen normalen Kernaufruf nicht erforderlich. Der feste interne
Recoverykanal ist Bestandteil der eingefrorenen Dreirollendynamik und wirkt
in jedem Intervall nach derselben Regel. Er ist kein aeusserer
Recoveryschalter.

Damit ist folgende S1-QZ-Anforderung prinzipiell erfuellt:

```text
NORMAL_ZERO_CONTACT_CONTINUATION_WITHOUT_RECOVERY_SIDECAR_PRESENT
```

Eine M4-Bruecke muss den Backreactionstatus und alle DTS-1-/Feldkonfigurationen
einmal rollenfest registrieren. Sie darf sie waehrend Gap, Probe oder
Expositionsfamilie nicht umschalten.

Wie A2 akzeptiert der Kern pro Aufruf eine synchrone Rezeptorverteilung.
Eine spaetere transiente M4-Huelle waere keine reine Bestandsbruecke.

## Offene M4-Frisch- und Resultatoberflaeche

Im Bestand existiert keine allgemeine profilfreie M4-Frischzustandsfabrik,
die fuer eine beliebige spaeter registrierte gemeinsame Geometrie gemeinsam
liefert:

- das oeffentliche Frischfeld;
- die vollstaendige eingefrorene DTS-1-Anatomie;
- den Konfigurationsdigest;
- den T1-Validierungsbezug;
- einen S1-QZ-Frischzustandsdigest.

Die historischen Auditmodule bauen ihre Anatomien jeweils privat und mit
profilspezifischen Werten. Diese Fabriken duerfen nicht wiederverwendet oder
zu einer allgemeinen M4-Quelle erklaert werden.

Auch der gekoppelte Kernoutput besitzt noch kein gemeinsames
`COMPLETED`/`NOT_COMPUTABLE`-Receipt, keinen S1-QZ-Carrydigest und keine
Trennung zwischen oeffentlicher Feldprojektion und privatem M4-Ledger. Das
sind reine, aber noch unimplementierte Brueckenaufgaben.

## T1-Validierungsluecke

`kfs1_t1_transition.py` stellt einen vollstaendigen parameterfreien lokalen
Ein-Kanten-Schritt fuer `free/bound/blocked` bereit. Dieser Kern ist
profilblind und fail-closed.

Der vorhandene Vergleich in `kfs1_s1ni_sequence_comparison.py` bildet jedoch
nur eine eigene Zwei-Knoten-/Ein-Kanten-Sequenz. Seine DTS-1-Projektion
verwendet die Summe der freien Endpunktressourcen zusammen mit genau einem
gebundenen und einem blockierten Kantenwert.

Fuer eine Drei- oder Mehrknotengeometrie ist nicht gebunden:

- wie gemeinsam genutzte freie Knotenkapazitaet auf mehrere lokale
  T1-Kantenledger projiziert wird;
- wie Doppelzaehlung an einem Knoten verhindert wird;
- ob T1 nur Anatomie und Erhaltung oder auch jeden DTS-1-Transfer validiert;
- welcher T1-Beleg an einem S1-RA-Checkpoint auszugeben ist;
- ob eine solche Projektion parameterfrei und eindeutig bleibt.

Eine direkte kantweise Wiederholung der Ein-Kanten-Projektion koennte freie
Knotenkapazitaet mehrfach zaehlen. Sie ist deshalb keine zulaessige reine
Formabbildung.

S1-QC und S1-QD binden T1 als strukturelle lokale Validierung von M4, nicht
als zweiten Feldzustand. Diese Rolle ist im allgemeinen Geometriefall noch
nicht technisch abgeschlossen.

M4 erhaelt daher den Status:

```text
DTS1_COUPLED_CORE_CONDITIONALLY_BRIDGEABLE
GENERAL_T1_STRUCTURAL_VALIDATION_PROJECTION_UNBOUND
M4_NOT_YET_S1QZ_CONNECTABLE
```

## S1-QZ-/S1-RA-Kompatibilitaetsmatrix

| Pflicht | A2/B1-B6 | M4 |
|---|---|---|
| profilblinder Kern | ja | ja |
| normaler Kontaktkanal | ja | ja |
| normaler Nullkontaktkanal | ja | ja |
| vollstaendiges Folgefeld | ja | ja |
| vollstaendiger Privatcarry | ja | ja, DTS-1-Anatomie |
| atomarer privater Kernoutput | ja | ja |
| neutrale Frischfabrik | nein | nein |
| allgemeine S1-QZ-Intervallhuelle | nein | nein |
| S1-QZ-Fehlerresultat statt Ausnahme | nein | nein |
| zeitloses Align mit privater Identitaet belegt | noch nicht | noch nicht |
| S1-RA-Geometrie registriert | nein | nein |
| T1-Strukturbeleg | nicht anwendbar | nur Ein-Kanten-Bestand |
| heutiger Paketstatus | bedingt anschliessbar | nicht anschliessbar |

Die Tabelle bewertet technische Anschlussreife, nicht die Qualitaet oder
Erklaerungsleistung einer Baseline.

## Paketweite Auswirkung

S1-RB schliesst keine Baseline aus und veraendert die 14 x 16-Matrix nicht.
Die vorhandenen Kerne muessen nicht neu entwickelt werden. Das Paket bleibt
aber:

```text
MANDATORY_BASELINE_PACKAGE_NOT_EXECUTABLE
```

Ein fehlender A2- oder M4-Anschluss ist kein Feldresiduum und keine Evidenz
fuer eine neue Funktion. Matrix, Comparator und Kandidat bleiben gesperrt.

## Fail-Closed-Regeln

S1-RB wird verletzt, wenn spaeter:

- S1-JO-Fixtures oder S1-JZ-/S1-K*-Profile als neue S1-PZ-Huelle erscheinen;
- eine neue A2-Geometriezeile in einem Formadapter erfunden wird;
- B1-B6-Konfiguration oder Refinement zwischen Repliken wechselt;
- A2 oder M4 eine transiente Geschichte verdeckt durch synchrone
  Nachbildung ersetzt;
- eine historische M4-Recovery-on/off-Intervention in den normalen Gap
  gelangt;
- der M4-Backreactionstatus armweise umgeschaltet wird;
- eine private Audit-Anatomie als allgemeine Frischfabrik gilt;
- T1 freie Knotenkapazitaet auf mehreren Kanten doppelt zaehlt;
- T1 als zweiter dynamischer Feldzustand statt passiver Strukturvalidierung
  ausgefuehrt wird;
- eine Ausnahme Teilfeld oder Teilcarry als gueltiges Zellresultat freigibt;
- ein bedingt anschliessbarer Kern als bereits paketfaehig bezeichnet wird.

## Aussagegrenze

S1-RB ist ein statischer Anschlussaudit. Er bestaetigt keine
Baselineausfuehrung und keinen Funktionsbefund. Es gibt keine neue Gleichung,
Konfiguration, Implementierung, Matrixausfuehrung oder Aussage zu einer
hypothetischen MCM-Memory. Der primaere MCM-Wahrnehmungsfeldkern und alle
geschlossenen Zweige bleiben unveraendert.

## Genau ein naechster Schritt

Als einziger Anschluss ist zulaessig:

```text
S1-RC - statischer M4-T1-Strukturprojektions-, Erhaltungs- und
        Nichtdoppelzaehlungsvertrag fuer gemeinsame Geometrien
```

S1-RC soll vor jeder Brueckenimplementierung entscheiden, ob und wie eine
vollstaendige DTS-1-Anatomie auf passive lokale T1-Strukturbelege abgebildet
werden kann, ohne freie Knotenkapazitaet mehrfach zu verbuchen. Es muss die
Grenze zwischen Anatomievalidierung und verbotener zweiter M4-Dynamik
festlegen und M4 stoppen, falls keine eindeutige parameterfreie Projektion
verbleibt. Keine Gleichungsaenderung, Parameterwahl, Geometrieregistrierung,
Implementierung, Fixture, Testausfuehrung oder Feldlauf.
