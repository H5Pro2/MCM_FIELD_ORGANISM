# S1-RC: Statischer M4-T1-Strukturprojektions-, Erhaltungs- und Nichtdoppelzaehlungsvertrag

## Status und Umfang

S1-RC entscheidet vor jeder M4-Brueckenimplementierung, welche passive
Strukturvalidierung fuer eine DTS-1-Anatomie mit mehreren Knoten und Kanten
zulaessig ist und welche technische Rolle der geschlossene T1-Bestand dabei
behaelt.

Der Vertrag:

- vergleicht nur vorhandene DTS-1- und T1-Anatomien;
- bindet keine neue Ressourcenrolle oder Dynamik;
- waehlt keine Geometrie, Kapazitaet, Rate, Feldkonfiguration oder Fixture;
- implementiert keine Projektion, Bruecke oder Runtime;
- fuehrt keinen Test und keinen Feldlauf aus;
- trifft keine Baseline-, Kandidaten- oder Funktionsentscheidung.

Verbindliche Entscheidung:

```text
NO_UNIQUE_CAPACITY_PRESERVING_EDGEWISE_T1_PROJECTION_FOR_SHARED_NODE_GEOMETRY
DTS1_NODE_LOCAL_HALF_SHARE_LEDGER_IS_THE_UNIQUE_EXISTING_NONDUPLICATING_LOCAL_VALIDATOR
GLOBAL_DTS1_LEDGER_REMAINS_THE_PACKAGE_WIDE_CONSERVATION_VALIDATOR
T1_REMAINS_FROZEN_ONE_EDGE_COUNTERBASELINE_AND_TEST_FIXTURE_ONLY
T1_IS_NOT_AN_M4_RUNTIME_STATE_TRANSITION_OR_MATRIX_CHECKPOINT
M4_T1_ROLE_BLOCKER_CLOSED_WITHOUT_NEW_DYNAMICS
NO_IMPLEMENTATION_NO_EXECUTION_NO_RESULT_DECISION
```

## Verbindlicher Bestandsunterschied

### DTS-1-Anatomie

Die vorhandene `DTS1ResourceAnatomy` speichert:

- eine feste positive Kapazitaet pro Knoten;
- einen leitend gebundenen Betrag pro bestehender ungerichteter Kante;
- einen refraktaeren Betrag pro bestehender ungerichteter Kante.

Freie Ressource wird nicht gespeichert. Sie entsteht pro Knoten als Rest
seiner Kapazitaet nach Anrechnung der jeweils halben leitenden und
refraktaeren Anteile aller anliegenden Kanten.

Damit besitzt DTS-1 zwei bereits implementierte Erhaltungsoberflaechen:

- `DTS1NodeResourceLedger` fuer jeden Knoten;
- die globale Anatomieidentitaet ueber alle freien Knotenreste und jede
  ungerichtete Kantenressource genau einmal.

### T1-Anatomie

`KFS1T1Ledger` beschreibt dagegen genau eine lokale Kante mit einer eigenen
festen Ledgerkapazitaet und den drei gespeicherten Rollen
`free`, `bound` und `blocked`. Der T1-Schritt arbeitet auf genau diesem
vollstaendigen Ein-Kanten-Ledger.

T1 besitzt keinen Knotenbestand, keine gemeinsam genutzte Knotenkapazitaet
und keine Regel dafuer, wie eine Kapazitaet zwischen mehreren anliegenden
Kanten aufzuteilen waere.

Diese Formen sind im Ein-Kanten-Fall vergleichbar, aber bei gemeinsam
genutzten Knoten nicht identisch.

## Audit der moeglichen Projektionsklassen

### P1 - Unabhaengiges T1-Ledger pro DTS-1-Kante

Eine direkte Projektion koennte leitend gebundene und refraktaere
DTS-1-Kantenwerte als `bound` und `blocked` uebernehmen. Fuer `free` und die
T1-Kapazitaet fehlt jedoch eine eindeutige Kantenrolle:

- DTS-1 speichert keine Kapazitaet pro Kante;
- freie Ressource gehoert einem Knoten und kann mehreren Kanten angeboten
  werden;
- derselbe freie Knotenrest wuerde bei vollstaendiger Uebernahme in jede
  anliegende Kante mehrfach erscheinen;
- eine Aufteilung nach Knotengrad, Gleichanteil, Minimum, Maximum oder
  Lastprofil waere eine neue Regel.

P1 ist daher verworfen:

```text
EDGEWISE_T1_LEDGER_PROJECTION_INVALID_DOUBLE_COUNT_OR_NEW_ALLOCATION_RULE
```

### P2 - Ein global aggregiertes T1-Ledger

Die vorhandene DTS-1-Globalidentitaet kann freie Knotenreste sowie leitende
und refraktaere Kantenressourcen ohne Doppelzaehlung aggregieren. Ein daraus
gebildetes globales Dreirollenledger waere erhaltend.

Es waere aber keine lokale T1-Kante und koennte weder die lokale
Kantenidentitaet noch die gemeinsame Knotenkonkurrenz pruefen. Eine
Ausfuehrung von `advance_kfs1_t1_edge` auf diesem Aggregat wuerde eine neue
globale Dynamik behaupten.

P2 bleibt deshalb ausschliesslich die bereits vorhandene globale
DTS-1-Erhaltungspruefung. Es wird nicht als T1-Laufzeitprojektion bezeichnet.

### P3 - Knotenlokale DTS-1-Halbankteilsprojektion

Die vorhandene `DTS1ResourceAnatomy.local_ledgers()`-Oberflaeche ordnet jedem
Knoten eindeutig zu:

- seinen freien Kapazitaetsrest;
- die Summe der halben leitenden Anteile aller anliegenden Kanten;
- die Summe der halben refraktaeren Anteile aller anliegenden Kanten.

Jede ungerichtete Kantenressource wird damit ueber ihre beiden Endpunkte
insgesamt genau einmal bilanziert. Ein Knoten wird nur gegen seine eigene
Kapazitaet geprueft. Es gibt keine Gradgewichtung, Profilwahl oder
nachtraegliche Normalisierung.

P3 ist die eindeutige vorhandene lokale Mehrknotenvalidierung. Sie ist aber
ein DTS-1-Knotenledger und kein `KFS1T1Ledger`. Insbesondere darf sie nicht
an `advance_kfs1_t1_edge` uebergeben oder als neue T1-Knotendynamik
umbenannt werden.

## Gebundene M4-Validierungsordnung

Eine spaetere M4-Bruecke muss nach jedem erfolgreichen DTS-1-Intervall genau
die folgenden vorhandenen Validierungsebenen belegen:

1. vollstaendige Knoten-, Kanten- und Geometrieidentitaet;
2. Endlichkeit und Nichtnegativitaet aller gespeicherten Kantenrollen;
3. lokale Kapazitaetsidentitaet jedes DTS-1-Knotens ueber P3;
4. globale Kapazitaetsidentitaet mit jeder Kantenressource genau einmal;
5. vollstaendige Eingangs- und Ausgangsanatomiedigests;
6. vollstaendige Transferledger fuer genau die vorhandenen Kanten;
7. atomare gemeinsame Ausgabe von Feld und Folgeanatomie.

Diese Pruefungen lesen nur das vorhandene DTS-1-Resultat. Sie schreiben
weder Feld noch Anatomie fort und fuegen keinen zweiten Zustand hinzu.

Eine spaetere S1-RA-Beobachtung traegt nur den vollstaendigen privaten
M4-Zustandsdigest und den technischen Erhaltungsbeleg. Die privaten
Knoten- und Kantenrohwerte bleiben innerhalb des M4-Adapters und werden nicht
als allgemeiner Baselinefeldreadout veroeffentlicht.

## Verbleibende T1-Rolle

S1-NI und S1-NJ haben T1 bereits als unabhaengigen Kandidaten geschlossen.
T1 bleibt genau in den dort gebundenen technischen Rollen erhalten:

- reproduzierbare diskrete Ein-Kanten-DTS-1-Gegenbaseline;
- Testfixture fuer atomare Ereignisgrenzen und lokale
  Dreirollenressourcenbilanz.

Fuer M4 bedeutet `T1-Strukturkontrolle` ab S1-RC ausschliesslich:

- die drei Rollen `free/bound/blocked` begruenden keine zusaetzliche
  Kandidatenfunktion jenseits DTS-1;
- eine M4-Bruecke darf keine vierte Ressourcenrolle oder einen zweiten
  T1-Zustand einfuehren;
- der eingefrorene T1-Einkantenbestand bleibt ein externer technischer
  Referenz- und Regressionstest;
- die konkrete Mehrknotenerhaltung wird durch die vorhandenen
  DTS-1-Knoten- und Globalledger validiert.

T1 wird nicht:

- pro M4-Intervall fortgeschrieben;
- aus einer Mehrknoten-Anatomie rekonstruiert;
- als zusaetzlicher Privatcarry gespeichert;
- als eigener S1-RA-Matrixarm oder Checkpoint ausgegeben;
- zur Auswahl oder Veraenderung eines DTS-1-Transfers verwendet.

Damit bleibt T1 strukturelle Kontrolle, ohne eine technisch ungueltige
Mehrkantenprojektion zu behaupten.

## Warum dies keine Entfernung von T1 ist

Der T1-Code, seine historischen Abnahmen und seine Reklassifikation bleiben
unveraendert erhalten. S1-RC schraenkt nur eine zu breite moegliche
Interpretation in M4 ein.

Die M4-Feldbaseline bleibt der eingefrorene gekoppelte DTS-1-Kern. T1 war
nach S1-QC nie als zweiter Feldarm vorgesehen. Die Verwendung der bereits
vorhandenen DTS-1-Ledgerpruefung entspricht daher der gebundenen
Nichtduplizierungsgrenze.

## M4-Zustands- und Receiptgrenze

Der spaetere private M4-Carry umfasst:

- die vollstaendige DTS-1-Anatomie;
- Geometrie- und Konfigurationsidentitaet;
- den kanonischen Anatomiedigest.

Er umfasst keinen T1-Laufzeitzustand. Der technische M4-Receipt muss
zusaetzlich passiv belegen:

- maximale lokale DTS-1-Ledgerabweichung;
- globale DTS-1-Ledgerabweichung;
- vollstaendigen Kantentransferdigest;
- Identitaet des eingefrorenen T1-Referenzvertrags;
- `t1_runtime_transition_count = 0`;
- atomaren Feld-/Anatomieabschlussstatus.

Die T1-Vertragsidentitaet belegt nur die geschlossene Rollen- und
Redundanzgrenze. Sie darf keinen numerischen T1-Vergleich als bestanden
ausgeben, wenn kein Ein-Kanten-Test ausgefuehrt wurde.

## Erhaltungs- und Nichtdoppelzaehlungsgates

Eine M4-Zelle bleibt `NOT_COMPUTABLE`, wenn:

- ein Knoten mehr leitende und refraktaere Halbankteile traegt als seine
  Kapazitaet zulaesst;
- eine ungerichtete Kantenressource lokal nicht je zur Haelfte an beiden
  Endpunkten bilanziert wird;
- eine Kantenressource global fehlt oder mehrfach gezaehlt wird;
- freie Ressource als zusaetzlicher gespeicherter M4-Wert dupliziert wird;
- lokale oder globale Ledgerabweichung nicht den vorhandenen DTS-1-Gates
  entspricht;
- Feld- und Anatomiegeometrie nicht vollstaendig uebereinstimmen;
- ein T1-Ledger pro Kante synthetisiert wird;
- T1 einen M4-Zustand oder Transfer fortschreibt.

Ein fehlgeschlagener Erhaltungsbeleg publiziert weder Folgefeld noch
Folgeanatomie als S1-QZ-Erfolg.

## Abgrenzung zu M3 und spaeteren Kandidaten

Die DTS-1-Erhaltungsledger sind privater M4-Baselinezustand. Sie werden nicht
als M3-Capacity-Clamp-Eingabe und nicht als Ersatz fuer eine spaetere
Kandidatenbilanz verwendet.

Die Tatsache, dass M4 lokal und global erhalten ist, weist keine
Kapazitaets-, Freigabe- oder Wiederverwendungsfunktion nach. Sie stellt nur
sicher, dass diese geschlossene technische Dreirollenbaseline ohne
Doppelzaehlung ausgefuehrt werden koennte.

## M4-Anschlussstatus nach S1-RC

Der in S1-RB offene T1-Rollenblocker ist geschlossen:

```text
M4_DTS1_RUNTIME_STATE_ONLY
M4_DTS1_NODE_AND_GLOBAL_LEDGER_VALIDATION_ONLY
T1_FROZEN_EXTERNAL_ONE_EDGE_REFERENCE_ONLY
NO_T1_MULTI_EDGE_PROJECTION_REQUIRED_OR_PERMITTED
M4_CONDITIONALLY_CONNECTABLE_PENDING_NEUTRAL_FRESH_AND_INTERVAL_BRIDGE
```

M4 ist damit wie A2 prinzipiell durch eine reine neutrale Huelle
anschliessbar. Es ist noch nicht implementiert, registriert oder
ausfuehrbar.

## Fail-Closed-Regeln

S1-RC wird verletzt, wenn spaeter:

- einem DTS-1-Rand eine frei erfundene eigene T1-Kapazitaet zugewiesen wird;
- derselbe freie Knotenrest in mehreren Kantenledgern erscheint;
- eine Grad-, Last-, Minimum-, Maximum- oder Gleichanteilsregel als reine
  Projektion eingefuehrt wird;
- das globale DTS-1-Ledger als lokale T1-Kante bezeichnet wird;
- der DTS-1-Knotenledger an den T1-Uebergangskern uebergeben wird;
- T1 pro M4-Matrixzelle laeuft oder einen zweiten Carry erzeugt;
- die T1-Referenzidentitaet einen nicht ausgefuehrten numerischen Test
  vortaeuscht;
- private M4-Ressourcenwerte in einen allgemeinen Baselinevergleich oder M3
  gelangen;
- ein ungueltiger Ledgerbeleg als positiver Feldunterschied interpretiert
  wird.

## Aussagegrenze

S1-RC ist ein statischer Struktur- und Nichtdoppelzaehlungsvertrag. Er
implementiert und bestaetigt keine M4-Ausfuehrung. Es gibt keine neue
Gleichung, Ressource, Dynamik, Geometrie, Matrixausfuehrung oder Aussage zu
einer hypothetischen MCM-Memory. Der primaere MCM-Wahrnehmungsfeldkern und
alle geschlossenen Zweige bleiben unveraendert.

## Genau ein naechster Schritt

Als einziger Anschluss ist zulaessig:

```text
S1-RD - statischer Drei-Knoten-A/B/C-Geometrie-, Lastanpassungs- und
        modelluebergreifender Frischprojektions-Kompatibilitaetsaudit
```

S1-RD soll ausschliesslich pruefen, ob die vorhandene S1-JV-Drei-Knoten-
Offenlinie die S1-PZ-Rollen `A_FOCAL`, `B_LOCAL` und `C_REMOTE`, eine
kontrollierbare B/C-Lastanpassung sowie dieselbe oeffentliche
Frischprojektion fuer alle 14 Modellrollen tragen kann. Wenn die Geometrie
die lokale/entfernte Trennung nicht eindeutig erfuellt, bleibt die
S1-RA-Matrix gesperrt; eine neue Mappingzeile darf im Audit nicht erfunden
werden. Keine Registrierung, Parameterwahl, Implementierung, Fixture,
Testausfuehrung oder Feldlauf.
