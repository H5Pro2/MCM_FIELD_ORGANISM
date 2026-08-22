# S1-TZ: RFM-1 statischer Transaktions-, Aktualisierungs- und Ablationsanatomie-Audit

## Auftrag und Grenze

S1-TZ prueft, ob die in S1-TY gebundene gemeinsame lokale Transaktion ohne
zweiten Kausalpfad, versteckten Zustand oder aktuellen Write-then-read-Kreis
darstellbar ist. Der Audit bindet Vorzustand, Vorschlagsrollen, Validierung,
Commit, Ablationen und spaetere Nachweisrecords.

S1-TZ enthaelt keine Dynamikgleichung, Rate, numerischen Parameter,
Runtimeaenderung, Implementierung, Testausfuehrung oder Ergebnisentscheidung.

## Anschluss an den vorhandenen Feldkern

Der primaere Feldkern besitzt bereits eine synchrone Vorschlagsgrenze:

- jeder Knoten liest den abgeschlossenen Layer-Vorzustand;
- alle Knotenvorschlaege werden ohne Teilcommit erzeugt;
- erst nach erfolgreichen Vorschlaegen entsteht ein vollstaendiger neuer
  Layer;
- ein fehlgeschlagener Vorschlag erzeugt keinen teilweise neuen Feldzustand.

Statische Referenzen sind `SharedMCMField.advance` und
`MCMNeuronLayer.advance`. S1-TZ veraendert diese Implementierung nicht.

RFM-1 darf diese Ordnung spaeter nur erweitern, nicht umgehen. Feld- und
Tafelfolgezustand muessen aus demselben abgeschlossenen Vorzustand entstehen
und als ein gemeinsames Paar uebernommen werden.

## Unveraenderlicher Transaktionsvorzustand

Jede RFM-1-Transaktion liest genau einen eingefrorenen Vorzustand `TX_PRE`. Er
enthaelt:

- Feld-, Geometrie- und Kanteninventaridentitaet;
- abgeschlossenen Feldtick und zugehoeriges Feldintervall;
- vollstaendige aktuelle S/H-Werte aller Feldknoten;
- aktuelle Rezeptorbeitraege des Intervalls;
- vorhandene gerichtete Feldbeitraege auf den drei kanonischen Kanten;
- beide gueltigen RFM-1-Tafeln mit ihren abgeleiteten Projektionen;
- die gemeinsame `e_bc`-Projektionsidentitaet;
- Digests von Feld-, Tafel- und Eingabevorzustand.

Nach Beginn der Vorschlagsbildung ist `TX_PRE` unveraenderlich. Kein
Motivvorschlag darf einen bereits erzeugten Vorschlag eines anderen Motivs
lesen. Der gemeinsame Record darf den vollstaendigen Feldzustand fuer
Identitaet und spaetere Bilanzpruefung tragen; ein einzelner Motivvorschlag
darf daraus ausschliesslich seine drei Motivknoten und zwei Motivkanten
lesen.

## Per-Motiv-Vorschlagsanatomie

Fuer `M_left` und `M_right` wird aus demselben `TX_PRE` je genau ein
vollstaendiger Motivvorschlag erzeugt. Er besitzt ausschliesslich:

- kanonische Motiv-, Kanten- und Orientierungsidentitaet;
- Referenz auf denselben `TX_PRE`-Digest;
- einen ephemeren lokalen Wechselwirkungsbeleg;
- die vorgeschlagene marginalenerhaltende Tafelumlagerung;
- die vollstaendige vorgeschlagene Folgetafel;
- gerichtete signed Feldtransferbeitraege auf den zwei Motivkanten;
- den daraus abgeleiteten bilanzierten Beitrag an den drei Motivknoten;
- Projektions-, Spiegel- und Lokalitaetsbelege;
- einen Eigendigest des vollstaendigen Vorschlags.

Der Wechselwirkungsbeleg ist kein fortbestehender Zustand. Er darf nach der
Transaktionsentscheidung nicht in Feld, Tafel, Snapshot oder Folgeschritt
getragen werden.

## Geschwistervorschlaege statt Write-then-read

Die gemeinsame Kopplung aus S1-TY wird kausal wie folgt gebunden:

```text
eingefrorener Vorzustand TX_PRE
        |
        +--> Tafelvorschlag
        |
        +--> Feldtransfervorschlag
```

Beide Vorschlaege stammen aus demselben lokalen Wechselwirkungsbeleg. Die
vorgeschlagene Folgetafel wird jedoch nicht erneut gelesen, um den
Feldtransfervorschlag desselben Schritts zu erzeugen. Ebenso wird der
vorgeschlagene Feldfolgezustand nicht zurueckgelesen, um die Folgetafel zu
bestimmen.

Damit bedeutet `atomar gekoppelt` nicht `erst schreiben, dann sofort lesen`.
Es bedeutet: zwei kausal zusammengehoerige Vorschlaege aus einem
gemeinsamen, abgeschlossenen Vorzustand und genau ein gemeinsamer Commit.

## Ueberlappende Motive

`M_left` und `M_right` teilen `e_bc`. Beide Motive lesen dieselbe
Vorzustandskante, aber nicht den Vorschlag des jeweils anderen Motivs.

Die beiden Tafelumlagerungen duerfen ihre Projektionen nicht veraendern.
Dadurch bleibt die gemeinsame `e_bc`-Projektionsidentitaet ohne
Nachnormalisierung erhalten.

Signed Feldtransferbeitraege beider Motive auf `e_bc` bleiben als zwei
proveniente lokale Beitraege unterscheidbar. Erst der globale
Feldvorschlagskompositor fasst sie deterministisch zu genau einem
Kantenbeitrag zusammen. Die gemeinsame Kante wird einmal fortgeschrieben;
kein Motiv darf sie separat committen.

## Vollstaendige Aktualisierungsordnung

Die einzig zulaessige kausale Ordnung ist:

1. `TX_PRE` vollstaendig erfassen und validieren.
2. Den unveraenderten primaeren Feldkernvorschlag aus `TX_PRE` bilden.
3. Alle lokalen RFM-1-Motivvorschlaege ausschliesslich aus `TX_PRE` bilden.
4. Alle Tafel-, Projektions-, Lokalitaets-, Bilanz- und Provenienzregeln
   pruefen.
5. Die validierten relationalen Kantenbeitraege deterministisch mit dem
   primaeren Feldvorschlag komponieren.
6. Den vollstaendigen Feldfolgezustand und beide Folgetafeln gemeinsam
   validieren.
7. Genau das vollstaendige Paar gemeinsam committen oder ohne Ausgabe
   abbrechen.

Kanonische Iterationsreihenfolge darf reproduzierbare Serialisierung
bestimmen, aber nicht das numerische Ergebnis. Eine Umkehr der
Motiviterationsreihenfolge muss denselben finalen Digest ergeben.

## Gemeinsame Validierung

Vor einem Commit muessen gemeinsam gelten:

- alle Records sind vollstaendig, endlich und demselben `TX_PRE` zugeordnet;
- Geometrie, Kanteninventar, Orientierung und Motivkardinalitaet stimmen;
- jede Folgetafel ist nichtnegativ und entweder normalisiert oder die
  zulaessige atomare Nulltafel;
- jede Tafelumlagerung erhaelt ihre Zeilen- und Spaltenprojektionen;
- die `e_bc`-Projektionen beider Motive bleiben wertidentisch;
- jeder relationale Feldbeitrag liegt nur auf vorhandenen Motivkanten;
- jeder Kantenbeitrag ist an seinen beiden Enden gegensinnig bilanziert;
- kein globaler Feldquellrest entsteht;
- Feld- und Tafelvorschlag jedes Motivs tragen denselben
  Wechselwirkungsbeleg;
- der primaere Feldkern bleibt im deaktivierten Pfad wertidentisch;
- Spiegelung und Motiviterationsumkehr erhalten die kanonische Entscheidung.

Clipping, Nachnormalisierung, fehlende Werte, Reparatur oder Teilcommit sind
keine Validierung.

## Atomarer Folgezustand

Ein gueltiger Commit besitzt genau zwei gemeinsam versionierte Teile:

- den vollstaendigen Feldfolgezustand;
- den vollstaendigen RFM-1-Tafelfolgezustand beider Motive.

Beide Teile referenzieren denselben Vorzustands-, Eingabe- und
Transaktionsdigest. Es gibt keinen zulaessigen Zustand, in dem nur einer der
beiden Teile fortgeschrieben wurde.

S1-TZ weist noch keinen produktiven Speicherort im `SharedMCMField`-Schema
zu. Diese Anatomie ist eine Voraussetzung fuer einen spaeteren isolierten
Kandidatencontainer, keine Runtimefreigabe.

## Drei getrennte Ablationsanatomien

### RFM-OFF: RFM-1 vollstaendig aus

- `TX_PRE` enthaelt keinen aktiven RFM-1-Zustand.
- Es werden keine Motiv- oder Tafelvorschlaege erzeugt.
- Der primaere Feldkernvorschlag wird unveraendert uebernommen.
- Sein kanonischer Feldfolgedigest muss dem heutigen Feldkern entsprechen.

### RFM-NULL: Relationale Kopplung neutralisiert

- Die Projektionen bleiben wertidentisch.
- Fuer die Auditbewertung wird ausschliesslich die relationsfreie
  Nullfaktorisierung aus S1-TX verwendet.
- Es entsteht kein relationaler Zusatztransfer.
- Der Eingriff ist nur eine instrumentierte Auditablation und kein
  produktiver Betriebsmodus.

### RFM-MATCHED-J: Matched Tafelintervention

- Zwei gueltige `TX_PRE`-Records unterscheiden sich ausschliesslich entlang der
  S1-TX-Interventionsrichtung.
- Feld, S/H, Eingabe, Projektionen, Kantenmarginalen, Geometrie und Dauer
  bleiben wertidentisch.
- Beide Arme durchlaufen dieselbe Vorschlags-, Validierungs- und
  Commitordnung.
- Tafel- und Feldantwort muessen gemeinsam mit der Intervention wechseln;
  andernfalls bleibt keine RFM-1-Gegenprognose.

`RFM-OFF`, `RFM-NULL` und `RFM-MATCHED-J` sind unterschiedliche Eingriffe.
Sie duerfen nicht durch
einen einzigen Modusschalter oder unterschiedliche Parameterwerte
vorgetaeuscht werden.

## Minimale spaetere Nachweisrecords

Eine spaetere isolierte technische Pruefung benoetigt mindestens:

1. **PrestateRecord:** Identitaeten, lokale Werte, beide Tafeln,
   Projektionen und vollstaendiger `TX_PRE`-Digest.
2. **MotifProposalRecord:** Motivrolle, Wechselwirkungsbeleg,
   Tafelumlagerung, Folgetafel, Kanten- und Knotenbeitraege sowie Eigendigest.
3. **TransactionDecisionRecord:** Validierungsergebnisse, gemeinsamer
   Commitstatus, Feld- und Tafelfolgedigests oder genau ein Fehlercode ohne
   Teilausgabe.
4. **AblationPairRecord:** Rolle `RFM-OFF`, `RFM-NULL` oder
   `RFM-MATCHED-J`, gemeinsame Matchidentitaeten und ausschliesslich
   abgeleitete Vergleichswerte.
5. **BaselinePairRecord:** identische Exposition und Parameteridentitaet von
   RFM-1, MVI-0 und JLR-1 sowie getrennte Modelloutputs.

Keiner dieser Records darf Ergebnislabels, Comparatorentscheidungen,
Eingangsrohdaten, Sequenzpuffer oder einen fortgeschriebenen
Wechselwirkungsbeleg enthalten.

## Fail-closed-Zustaende

Die Transaktion ist ungueltig und erzeugt keinen Folgezustand, wenn:

- ein Vorschlag einen veraenderten oder fremden Vorzustand liest;
- `Tafel_next` oder `Feld_next` innerhalb desselben Schritts zurueckgelesen
  wird;
- ein Motiv den Vorschlag des anderen Motivs als Kausalquelle verwendet;
- die gemeinsame Kante zweimal committed wird;
- Tafel- und Feldvorschlag unterschiedliche Wechselwirkungsbelege tragen;
- eine Tafelprojektion, Bilanz- oder Spiegelidentitaet verletzt ist;
- der globale Kompositor von der Motiviterationsreihenfolge abhaengt;
- nur Feld oder nur Tafel erfolgreich materialisiert wird;
- ein Fehler nachtraeglich repariert, geclippt oder normalisiert wird;
- ein ephemerer Beleg in einen Folgezustand oder Snapshot gelangt.

## Auditentscheidung

Die RFM-1-Transaktion ist ohne algebraischen Kreis und ohne versteckten
Zwischenzustand anatomisch darstellbar. Tafel- und Feldvorschlag sind
Geschwister desselben abgeschlossenen Vorzustands. Der bestehende synchrone
Feldkern liefert dafuer eine passende Vorschlags- und Commitgrenze, wird in
S1-TZ aber nicht veraendert.

RFM-1 bleibt damit offen, ist jedoch weiterhin nicht mathematisch oder
funktional zugelassen. Insbesondere ist noch nicht bestimmt, welche
Vorzeichen- und Bilanzwirkung der gemeinsame lokale Wechselwirkungsbeleg
haben darf.

## Verbindliche Entscheidung

```text
S1_TZ_RFM1_CLOSED_PRESTATE_SIBLING_PROPOSAL_ANATOMY_BOUND
ATOMIC_FIELD_TABLE_PAIR_COMMIT_WITHOUT_WRITE_THEN_READ_BOUND
RFM_OFF_NULL_MATCHED_J_AND_MINIMAL_EVIDENCE_RECORDS_BOUND
NO_EQUATION_NO_PARAMETERS_NO_IMPLEMENTATION_NO_RUN
```

## Naechster Schritt

Der einzige naechste Schritt ist S1-UA als statischer Vorzeichen-, Null-,
Bilanz- und Passivitaetsvertrag fuer die gemeinsame lokale Transaktion. Er
muss vor jeder Gleichung festlegen:

- welche signed Zwei-Kanten-Lagen einen positiven, negativen oder neutralen
  relationalen Austausch erlauben;
- wie Spiegelung und gemeinsamer Vorzeichenwechsel den Austausch
  transportieren;
- wie der Feldtransfer lokal quellenfrei bleibt;
- welche Nullfeld-, Einzelkanten- und Nulltafelgrenzen exakt gelten;
- welche Passivitaetsverletzungen RFM-1 sofort stoppen.

Kann keine eindeutige Vorzeichen- und Bilanzordnung ohne Ziel-, Fehler- oder
Ergebnisbegriff gebunden werden, wird RFM-1 gestoppt. S1-UA enthaelt noch
keine Dynamikgleichung, Parameter, Runtime, Implementierung oder
Testausfuehrung.
