# S1-QG: Statischer A3-NORM-Zustandsinventar-, Nennerprovenienz- und Feldoutputrollenvertrag

## Status und Umfang

S1-QG bindet fuer die nach S1-QF verbleibende A3-NORM-Gegenbaseline:

- das vollstaendige private Zustandsinventar;
- die kanonische Orts- und Geometrieordnung;
- die Herkunft der globalen Skalierungsgrundlage;
- die Trennung von privatem Zustand, temporaerer Skalierung und Feldoutput;
- die erlaubten S- und H-Rollen;
- die atomare Ausgabe- und Fail-Closed-Grenze.

S1-QG waehlt noch nicht, ob der normalisierte Vektor S ersetzt, S skaliert
oder als Feldquelle einwirkt. Der Vertrag enthaelt keine neue Gleichung,
Parameter, Werte, Toleranzen, Schema-ID, Implementierung, Fixture,
Runtimeaenderung, Testausfuehrung oder Ergebnisentscheidung.

Verbindliche Entscheidung:

```text
NORM_COMPLETE_LOCAL_STATE_INVENTORY_AND_GLOBAL_SCALE_PROVENANCE_BOUND
GLOBAL_SCALE_IS_EPHEMERAL_OUTPUT_DERIVATION_NOT_PRIVATE_CARRY
NORM_MAY_AFFECT_ONLY_S_H_REMAINS_SHARED_FAST_FIELD_ROLE
FIELD_COMPOSITION_FAMILY_REMAINS_UNSELECTED
NO_EQUATIONS_NO_VALUES_NO_IMPLEMENTATION_NO_EXECUTION
```

## Rollenordnung

NORM besitzt genau vier getrennte technische Rollen:

| Rolle | Lebensdauer | Bedeutung |
|---|---|---|
| `NORM_LOCAL_STATE` | ueber Intervalle getragen | genau eine private lokale Koordinate pro Feldknoten |
| `NORM_GLOBAL_SCALE_RECORD` | nur innerhalb eines atomaren Outputs | Beleg der Skalierungsherkunft aus dem vollstaendigen aktuellen Zustand |
| `NORM_SIGNED_OUTPUT_VECTOR` | atomarer Intervalloutput | vollstaendiger vorzeichenbehafteter normalisierter Vektor |
| `NORM_FIELD_OUTPUT` | spaetere gemeinsame Feldoberflaeche | vollstaendiges S/H-Feld nach noch ungebundener Komposition |

Nur `NORM_LOCAL_STATE` darf zwischen Intervallen getragen werden. Die
Skalierungsgrundlage und der normalisierte Output werden an jedem atomaren
Abschluss neu aus dem aktuellen vollstaendigen Zustand abgeleitet.

## Privates Zustandsinventar

Der NORM-Privatzustand enthaelt genau:

- Modell- und Vertragsidentitaet;
- unveraenderte Konfigurationsidentitaet;
- Geometrieidentitaet;
- kanonisch geordnete Feldknotenidentitaeten;
- genau eine endliche lokale Koordinate je Feldknoten;
- Vorzustands- und Frischzustandsprovenienz;
- einen kanonischen Zustandsdigest;
- einen atomaren Gueltigkeitsstatus.

Nicht zum Zustand gehoeren:

- globaler Nenner oder Skalierungswert;
- vorheriger normalisierter Output;
- H, Rezeptorkontakt oder Feldreadout;
- Arm-, Familien-, Checkpoint- oder Ergebnislabel;
- Kandidatenzustand, Kandidatenbilanz oder Ressourcenledger;
- Edge-Inventar, F3-Fluss oder Nachbarschaftsrolle;
- Ereigniszaehler, Puffer, Replayfolge oder globaler Cache.

Ein Zustand mit einer zusaetzlichen Koordinate ist keine NORM-Unterrolle nach
S1-QG.

## Kanonische Ortsordnung

Das Zustandsinventar muss jeden Knoten des gemeinsamen Feldes genau einmal
und in derselben kanonischen Reihenfolge wie das vollstaendige
`SharedMCMField` enthalten. Nur Rezeptordocks, nur A/B/C-Orte oder eine
nachtraeglich ausgewaehlte Teilmenge sind unzulaessig.

Die Geometrieordnung bindet:

- dieselbe Knotenmenge vor und nach jedem Intervall;
- eindeutige Zuordnung zwischen Knoten und lokaler Koordinate;
- identische Reihenfolge fuer Zustand, Evidence, Output und Digest;
- Permutationskovarianz bei gemeinsam permutierter Geometrie und Eingabe;
- keine Bedeutung aus der numerischen Position eines Knotens in der Liste.

Eine Geometrieaenderung erzeugt keinen migrierten NORM-Zustand, sondern einen
atomaren Stopp.

## Frischzustand und Carry

Der NORM-Frischzustand wird fuer jeden Arm unabhaengig durch die vorhandene
W7-N-Frischzustandsrolle fuer `norm` aufgebaut. Er deckt die vollstaendige
registrierte Feldgeometrie ab und besitzt keine Vorgeschichte.

Nach einem gueltigen Intervall wird ausschliesslich der vollstaendige lokale
Folgezustand als naechster Vorzustand getragen. Dabei muessen gemeinsam
uebereinstimmen:

- Modell- und Konfigurationsidentitaet;
- Geometrie und Knotenordnung;
- Vorgaenger- und Folgezustandsdigest;
- Intervall- und Feldzeitprovenienz;
- Frischreplikatidentitaet.

Ein einzelner Ortszustand, ein Skalierungsrecord oder ein Outputvektor darf
nicht separat in den naechsten Schritt uebernommen werden.

## Modellneutrale Eingabegrenze

Der vorhandene NORM-Lokalkern darf pro Intervall nur erhalten:

- den vollstaendigen gueltigen NORM-Vorzustand;
- die vollstaendige aktuelle S-Evidence in kanonischer Knotenordnung;
- die abgeschlossene technische Intervalldauer;
- die unveraenderte NORM-Konfiguration.

H und Rezeptorkontakt duerfen als gemeinsame Feldprovenienz beobachtet, aber
nicht als zusaetzliche NORM-Zustands- oder Nennerquelle gelesen werden.
Expositionsrollen bleiben im Orchestrator.

Die S-Evidence muss aus genau demselben gemeinsamen Feldintervall stammen,
das spaeter im NORM-Feldoutput belegt wird. Ein historischer Observerdriver,
ein gespeicherter W7-P-Trace oder ein Ergebnisvektor ist keine zulaessige
Eingabe.

## Atomare Zustandsfortschreibung

Die vorhandenen Rollen `build_zero_w7n_local_baseline` und
`advance_w7n_local_baseline` bleiben die einzigen zugelassenen Quellen fuer
den lokalen NORM-Zustand und den bestehenden normalisierten Lokalausgang.
S1-QG aendert deren Gleichung und Konfiguration nicht.

Ein spaeterer Intervallschritt muss logisch atomar erfolgen:

1. gemeinsame Eingabe, Geometrie, Konfiguration und Vorzustand validieren;
2. alle lokalen Koordinaten ueber dasselbe abgeschlossene Intervall
   fortschreiben;
3. erst den vollstaendigen lokalen Folgezustand fixieren;
4. daraus die globale Skalierungsprovenienz und den signed Outputvektor
   ableiten;
5. erst danach einen vollstaendigen Feldoutput materialisieren;
6. Zustand, Skalierungsbeleg, Feld und Diagnostik gemeinsam veroeffentlichen.

Kein Ortsoutput darf vor Abschluss aller lokalen Zustandskoordinaten sichtbar
werden.

## Globale Skalierungsprovenienz

Der `NORM_GLOBAL_SCALE_RECORD` muss ohne einen neuen Carryzustand mindestens
binden:

- Modell-, Vertrags- und Konfigurationsidentitaet;
- Geometrie und kanonische Knotenordnung;
- Digest des vollstaendigen lokalen Folgezustands;
- Beleg, dass jede lokale Koordinate genau einmal in die vorhandene
  Skalierungsregel eingegangen ist;
- Bezug auf den fest registrierten numerischen Stabilisator der vorhandenen
  NORM-Konfiguration;
- Endlichkeits- und Definitionsstatus;
- Digest des daraus abgeleiteten signed Outputvektors;
- einen eigenen Recorddigest.

S1-QG bindet weder den konkreten Skalierungswert noch den vorhandenen
Stabilisatorwert neu. Der Record belegt Herkunft und Vollstaendigkeit, nicht
eine neue Formel.

Der Skalierungsrecord darf nicht:

- in den naechsten Privatstatus geschrieben werden;
- zwischen Armen oder Replikaten geteilt werden;
- nur ausgewaehlte Orte enthalten;
- Kandidaten- oder Comparatorwerte lesen;
- eine lokale Nachbarschaft staerker gewichten;
- nach Kenntnis eines Feldfits neu berechnet werden.

## Signed Outputvektor

`NORM_SIGNED_OUTPUT_VECTOR` muss:

- genau einen endlichen Wert pro kanonischem Feldknoten enthalten;
- die Knotenordnung des lokalen Zustands unveraendert uebernehmen;
- das Vorzeichen jeder lokalen Zustandskoordinate erhalten;
- bei einem lokalen Nullzustand an diesem Ort einen Nulloutput tragen;
- aus genau einem vollstaendigen Skalierungsrecord stammen;
- einen eigenen Digest besitzen.

Ein Betrag, eine Norm, ein Maximum, eine ausgewaehlte Region oder die
Skalierungsgroesse allein ist kein NORM-Outputvektor.

Der Vektor ist noch kein S1-QA-Feldresultat. Er ist die vollstaendige
baselineeigene Ausgabe, die ein spaeterer Feldkompositor ohne zusaetzliche
Information konsumieren duerfte.

## Erlaubte S-Rolle

NORM darf spaeter ausschliesslich die S-Komponente des naechsten
vollstaendigen Feldes beeinflussen. Der Feldkompositor darf als
baselineeigene Information nur erhalten:

- `NORM_SIGNED_OUTPUT_VECTOR`;
- dessen Zustands- und Skalierungsprovenienz;
- den gemeinsamen kandidatenfreien Feldvorzustand und Feldinput;
- die unveraenderte gemeinsame Feldkonfiguration.

Noch offen bleibt genau eine Kompositionsentscheidung:

```text
REPLACE_S | SCALE_S | SOURCE_S
```

Diese Bezeichnungen sind Funktionsfamilien, keine Gleichungen. Genau eine
Familie muss vor einer Implementierung statisch gewaehlt und gegen die beiden
anderen abgegrenzt werden. Eine Mischform oder armweise Auswahl ist
unzulaessig.

## Gemeinsame H-Rolle

NORM besitzt keine eigene H-Koordinate, keine H-Konfiguration und keinen
H-Readout. H muss aus derselben kandidatenfreien schnellen Feldrolle wie A1
stammen.

Ein spaeterer Feldkompositor muss deshalb belegen:

- genau eine technische Feldzeitfortschreibung pro Intervall;
- dieselbe schnelle H-Konfiguration wie A1;
- keine zweite oder nachtraegliche H-Aktualisierung;
- keinen Rueckfluss des normalisierten Outputs in einen privaten H-Zustand;
- vollstaendige S/H-Ausgabe in derselben atomaren Feldmaterialisierung.

Wie die gemeinsame H-Fortsetzung mit der noch offenen S-Kompositionsfamilie
nichtzirkulaer verbunden wird, bleibt dem naechsten Audit vorbehalten.

## Vollstaendige NORM-Ausgabe

Ein spaeterer gueltiger NORM-Intervalloutput muss atomar enthalten:

- vollstaendige S1-QD-Eingabe- und Carryprovenienz;
- vollstaendigen NORM-Folgezustand;
- `NORM_GLOBAL_SCALE_RECORD`;
- `NORM_SIGNED_OUTPUT_VECTOR`;
- vollstaendiges gemeinsames Feld mit S und H;
- Beleg der genau einmaligen Feldzeitfortschreibung;
- getrennte technische Diagnostik;
- einen Gesamtdigest;
- genau einen Abschlussstatus.

Fehlt ein Bestandteil, werden weder Feld noch Folgezustand als Teilergebnis
veroeffentlicht.

## Null- und Symmetrierollen

Ohne konkrete Werte bindet S1-QG folgende strukturelle Pflichten:

- Ein vollstaendiger lokaler Nullzustand erzeugt einen definierten
  Nulloutputvektor.
- Gleichwertige lokale Zustaende erhalten unter derselben globalen
  Skalierungsgrundlage gleichwertige Outputs.
- Eine gemeinsame Permutation von Geometrie, Zustand und Evidence permutiert
  den Output entsprechend, aendert aber nicht seine technische Rolle.
- Ein Vorzeichenwechsel aller lokalen Zustandswerte spiegelt sich im signed
  Output wider, ohne die Ortsordnung zu aendern.
- Gleich grosse globale Zustandslasten duerfen nicht aufgrund von A/B/C- oder
  Nah/Fern-Labels verschieden skaliert werden.

Diese Pflichten sind keine numerischen Ergebnisprognosen.

## Fail-Closed-Zustaende

Der NORM-Pfad liefert ausschliesslich `NOT_COMPUTABLE`, wenn:

- ein Feldknoten fehlt, doppelt vorkommt oder anders geordnet ist;
- Zustand, Evidence und Feldgeometrie nicht dieselbe Ortsmenge besitzen;
- ein lokaler Zustand oder Output nicht endlich ist;
- die Konfigurationsidentitaet zwischen Intervallen wechselt;
- die Skalierungsprovenienz nicht alle Orte genau einmal bindet;
- der Skalierungsrecord aus einem anderen Arm oder Zustand stammt;
- ein Nenner oder Output als privater Carry uebernommen wird;
- H in den NORM-Zustand oder die Skalierungsquelle gelangt;
- Kandidaten-, Arm-, Ziel-, Ergebnis- oder Zukunftsinformation gelesen wird;
- mehr als eine S-Kompositionsfamilie verwendet wird;
- die Feldzeit zweimal fortgeschrieben oder ein Feld nachtraeglich repariert
  wird;
- nur Observeroutput statt eines vollstaendigen Feldresultats vorliegt.

Ein technischer NORM-Stopp erzeugt kein Kandidatenresiduum.

## Bestands- und Implementierungsgrenze

Der vorhandene W7-N-NORM-Kern ist fuer lokalen Zustand und normalisierten
Output wiederverwendbar. Nicht vorhanden ist weiterhin ein atomarer
Feldkompositor, der genau eine S-Kompositionsfamilie und die gemeinsame
A1-H-Rolle ohne doppelten Feldschritt verbindet.

Status:

```text
EXISTING_NORM_STATE_AND_OUTPUT_KERNEL_REUSABLE
NEW_ATOMIC_FIELD_COMPOSITOR_STILL_REQUIRED
MANDATORY_BASELINE_PACKAGE_NOT_EXECUTABLE
```

S1-QG implementiert diesen Kompositor nicht.

## Aussagegrenze

S1-QG bindet nur Zustands-, Provenienz- und Ausgaberollen einer technischen
Gegenbaseline. Es gibt keine neue NORM-Feldgleichung, keine Parameter, keine
Implementierung, keinen Feldlauf, keinen Kandidaten und keinen Befund zu
einer hypothetischen MCM-Memory. Der primaere MCM-Wahrnehmungsfeldkern bleibt
unveraendert.

## Genau ein naechster Schritt

Als einziger Anschluss ist zulaessig:

```text
S1-QH - statischer NORM-Feldkompositionsfamilien- und
        Nichtzirkularitaetsaudit
```

S1-QH soll `REPLACE_S`, `SCALE_S` und `SOURCE_S` gegen die bestehende
Feldarchitektur, die A1-H-Rolle und die NORM-Gegenprognose pruefen. Genau eine
Familie darf nur dann weitergefuehrt werden, wenn sie ohne doppelten
Feldschritt, versteckten Parameter oder Funktionsduplikation einen atomaren
Feldoutput erlaubt. Noch keine Gleichung, Parameter, Werte, Implementierung,
Fixture, Runtimeaenderung, Testausfuehrung oder Ergebnisentscheidung.
