# S1-OJ G2/D3 konservative Zielprojektion und atomare Commitgrenze

## Status

S1-OJ bindet ausschliesslich Funktionsprognose, Falsifikation und atomare
Grenze fuer eine spaetere konservative D3-Zielprojektion auf Basis der in
S1-OI akzeptierten Halbierungsbetragsermittlung. Der Schritt bindet noch kein
Schema, keine API-Implementierung, keinen Runtimecommit, keine O3-Auswertung
und keinen Feldlauf.

Entscheidung:

```text
G2_D3_CONSERVATIVE_TARGET_PROJECTION_AND_ATOMIC_COMMIT_BOUND
```

## Ausgangspunkt

S1-OI kann aus gueltigen Originalbytes passiv einen Betrag bestimmen:

```text
source D3 U=0.5, C=0.0
+ valid LOCAL_CONTINUATION
+ formation_enabled=true
-> amount m=0.25
```

Der S1-OI-Beleg ist kein D3-Zustand und keine spaetere oeffentliche
Folgeeingabe. S1-OJ bindet nun nur, wie eine getrennte spaetere Komposition
denselben Originalinput innerhalb eines einzigen reinen Aufrufs erneut
validieren, den Betrag transient verwenden und daraus hoechstens einen neuen
D3-Record konstruieren darf.

## Zwei strikt getrennte Stufen

### P: Reine Zielprojektion

Die Projektionsstufe:

- erhaelt originale kanonische Grenz- und D3-Bytes;
- erhaelt den vorregistrierten binaeren Ablationsschalter und exakte
  Registries;
- ruft innerhalb desselben Stacks die akzeptierte S1-OI-Auswertung auf;
- akzeptiert keinen extern gelieferten S1-OI-Beleg;
- konstruiert bei Erfolg hoechstens vollstaendige kanonische D3-Zielbytes;
- mutiert und publiziert nichts.

### C: Atomare Commitgrenze

Die spaetere Commitstufe darf die vollstaendig validierten Zielbytes nur dann
als neuen Kandidatenzustand uebergeben, wenn die aktuell gebundene
Quelldigestidentitaet noch exakt der Projektionsquelle entspricht. Es gibt
keinen partiellen Rollentausch und keine Zwischenveroeffentlichung.

S1-OJ implementiert weder P noch C.

## Zulaessige Zielaenderung

Bezeichnungen:

```text
U = pre.bound_unconfigured
C = pre.bound_configured
m = gueltiger S1-OI-Betrag
```

Nur folgende Rollen duerfen sich bei `m>0` aendern:

```text
target.bound_unconfigured = U - m
target.bound_configured = C + m
```

Alle anderen Sachrollen muessen wertidentisch bleiben:

```text
target.schema_id = pre.schema_id
target.schema_version = pre.schema_version
target.candidate_class_id = pre.candidate_class_id
target.edge_id = pre.edge_id
target.carrier_a_id = pre.carrier_a_id
target.carrier_b_id = pre.carrier_b_id
target.geometry_digest = pre.geometry_digest
target.field_reference_digest = pre.field_reference_digest
target.capacity = pre.capacity
target.free = pre.free
target.blocked = pre.blocked
```

Nur die drei von der Aenderung abhaengigen Digests werden danach kanonisch neu
berechnet:

```text
resource_account_digest
aggregate_projection_digest
anatomy_record_digest
```

Der neu berechnete `aggregate_projection_digest` muss wegen erhaltener
Aggregation wertgleich zum Quelldigest bleiben. Ressourcen- und
Anatomierecorddigest muessen bei `m>0` vom Quelldigest verschieden sein.

## Exakte Erhaltungsidentitaet

Vor jeder Zielserialisierung muessen als exakte rationale Werte gelten:

```text
target.U + target.C = pre.U + pre.C

target.free = pre.free
target.blocked = pre.blocked
target.capacity = pre.capacity

target.capacity
= target.free + target.U + target.C + target.blocked
```

Clipping, Epsilonvergleich, Nachnormalisierung, Restbuchung oder eine
zusaetzliche Ressource sind verboten.

## Nullpfadidentitaet

Bei jedem gueltigen Nullbetrag gilt staerker als nur Wertgleichheit:

```text
m = 0.0
-> target_d3_raw_bytes is source_d3_raw_bytes
-> target_anatomy_record_digest = source_anatomy_record_digest
-> projection_status = NO_CHANGE
```

Die Nullprojektion darf keinen neu serialisierten Ersatzrecord erzeugen. Das
gilt fuer:

- ersten Kontakt;
- lokalen Wechsel;
- `formation_enabled=false`;
- leere `bound_unconfigured`-Restressource.

So kann ein Nullpfad nicht als technische Zustandsaenderung erscheinen.

## Positive C0-Zielprojektion

Fuer die akzeptierte erste F2-Fortsetzung ist vorab gebunden:

```text
pre:
free = 0.5
U = 0.5
C = 0.0
blocked = 0.0
capacity = 1.0

m = 0.25

target:
free = 0.5
U = 0.25
C = 0.25
blocked = 0.0
capacity = 1.0
```

X/X und Y/Y muessen aus demselben D3-Vorzustand bitidentische D3-Zielbytes
erzeugen. Die Orientierungsrollen duerfen im Zielrecord nicht vorkommen.

## Zweite Fortsetzung auf frischem Zielzustand

Eine spaetere sequenzielle F2-Komposition darf die zweite Fortsetzung nur aus
dem vollstaendig abgeschlossenen ersten Zielrecord beginnen:

```text
pre U=0.25, C=0.25
+ m=0.125
-> target U=0.125, C=0.375
```

Die zweite Grenzfigur muss den Anatomierecorddigest dieses neuen Vorzustands
als eigene D3-Quelle binden. Ein alter C0-Quelldigest, ein weitergereichter
S1-OI-Beleg oder ein gespeicherter Fortsetzungszaehler ist unzulaessig.

## Ereignis- und Persistenzsperre

In den D3-Zielbytes bleiben insbesondere verboten:

```text
event_role
prior_orientation
current_orientation
prior_contact_digest
current_contact_digest
interval_ordinal
history_id
arm_id
sequence
continuation_count
formation_enabled
computed_repartition_amount
amount_evaluation_receipt_digest
```

Die Zielprojektion speichert ausschliesslich die geaenderte konservative
D3-Unterteilung. Aus ihr ist keine Kontaktfolge rekonstruierbar.

## Zielvalidierung

Nach kanonischer Serialisierung muss der neue Record durch den unveraenderten
D3-Validator laufen. Nur bei einem gueltigen Beleg duerfen intern gebunden
werden:

```text
source_anatomy_record_digest
amount_evaluation_receipt_digest
target_anatomy_record_digest
target_validation_receipt_digest
```

Diese Provenienzrollen gehoeren in einen passiven Projektionsbeleg, nicht in
den D3-Zielrecord. Ein ungueltiger Zielrecord wird vollstaendig verworfen.

## Atomare Commitreihenfolge

Die spaetere technische Reihenfolge ist verbindlich:

```text
1. Originalgrenze und Original-D3 intern validieren
2. S1-OI-Betrag innerhalb desselben Aufrufs bestimmen
3. bei Nullbetrag Original-D3 bitidentisch zurueckgeben
4. bei positivem Betrag vollstaendigen Zielrecord in-memory konstruieren
5. exakte rationale Erhaltung pruefen
6. alle drei abhaengigen Digests kanonisch berechnen
7. vollstaendige Zielbytes durch D3 validieren
8. Quelldigest gegen den noch aktuellen Kandidatenzustand vergleichen
9. genau einen vollstaendigen Zielzustand atomar uebergeben
10. transiente Grenze, Ereignis, Betrag und Preview vollstaendig verwerfen
```

Vor Schritt 9 ist der Kandidatenzustand unveraendert. Nach Schritt 9 existiert
im Kandidatenpfad nur der validierte D3-Zielzustand. Ein Fehler in einem
beliebigen Schritt erzeugt keinen Commit.

## Stale-Source-Sperre

Zwischen Projektion und spaeterer Uebergabe darf keine andere Aenderung der
D3-Quelle unbemerkt bleiben:

```text
current_anatomy_record_digest != projected_source_anatomy_record_digest
-> STALE_SOURCE
-> target discarded
-> no commit
```

Ein Zielrecord wird nicht auf eine neuere Quelle umgerechnet oder
nachgebessert. Eine erneute Projektion waere ein neuer kontrollierter Aufruf.

## Passive Beleggrenze

Ein spaeterer Projektions-/Commitbeleg darf Provenienz, Status und Digests
dokumentieren. Er ist kein Folgeeingang fuer Grenz-, Betrag-, D3-, O3- oder
Feldlogik.

Ein Commitstatus in einem passiven Beleg ist keine Feldwirkung. S1-OJ gibt
keine Feldintegration frei.

## Gegenbaselinegrenze

Die konservative Zielprojektion ist eine konstruierte Zustandsoperation. Sie
belegt keine eigene Kandidatenfunktion. Ein zustandsbehafteter Adapter oder
Leaky-Arm kann im reinen F2-Bildungsabschnitt weiterhin dieselbe Zahlenfolge
abbilden.

Die angepasste Gegenbaseline bleibt deshalb fuer den spaeteren gemeinsamen
Lebenszyklus zwingend. Digestunterschiede zwischen Quelle und Ziel sind keine
funktionale Abgrenzung.

## Verwerfungsbedingungen

Der Ziel-/Commitzweig wird gestoppt, wenn:

- eine andere Sachrolle als U und C veraendert werden muss;
- aggregiertes `bound`, `free`, `blocked` oder `capacity` abweicht;
- ein Nullbetrag neue D3-Bytes oder einen neuen Recorddigest erzeugt;
- X/X und Y/Y bei gleichem D3-Vorzustand verschiedene Zielbytes erzeugen;
- Zielwerte geclippt, normalisiert oder mit Epsilon akzeptiert werden;
- der Zielrecord ein Ereignis, Kontakt, einen Betrag oder eine Historie
  speichert;
- ein externer S1-OI-Beleg als oeffentliche Eingabe erforderlich ist;
- die Zielbytes nicht kanonisch oder nicht durch D3 validierbar sind;
- ein partieller Record vor vollstaendiger Validierung sichtbar wird;
- ein veralteter Quelldigest committen darf;
- bei Fehler ein Teilcommit oder eine Reparaturbuchung entsteht;
- O3, Feldantwort oder Ergebniswissen zur Zielkonstruktion gelesen werden.

Ein Stopp verwirft diese Projektions-/Commitform und ist kein Befund ueber das
gesamte MCM-Wahrnehmungsfeld.

## Erlaubte spaetere Vertragstests

Vor einer Runtime duerfen spaeter nur reine Tests binden:

- bitidentische Nullpfade;
- C0 plus `m=0.25` zu U/C `0.25/0.25`;
- zweiter Schritt zu U/C `0.125/0.375` aus frischem Zwischenrecord;
- X/X- und Y/Y-Zieldigestgleichheit;
- exakte lokale und aggregierte Erhaltung;
- unveraenderte Identitaets-, freie und blockierte Rollen;
- kanonische Neuberechnung der drei abhaengigen Digests;
- D3-Zielvalidierung;
- Abwesenheit transienter Rollen im Ziel;
- Eingabeimmutabilitaet und Fail-Closed-Verhalten;
- Stale-Source-Abbruch ohne Teilcommit;
- Abwesenheit von O3-, Feld-, Runner-, Medien-, Netzwerk- und I/O-Pfaden.

S1-OJ implementiert und fuehrt keinen solchen Test aus.

## Aussagegrenze

S1-OJ bindet nur die technische Zielprojektion und atomare Commitgrenze. Es
gibt noch keinen implementierten D3-Zielrecord, keinen Commit, keine
sequenzielle F2-Bildung, keine ausgefuehrte O3- oder Feldwirkung, keine
Lernfunktion und keinen Befund zur hypothetischen MCM-Memory.

## Naechster erlaubter Schritt

S1-OK darf ausschliesslich Schema, Digests, Registry, Fehlercodes und passive
Belegrollen fuer reine Zielprojektion und einen getrennten atomaren Commit
binden. Projektions- und Commitstatus muessen unterscheidbar bleiben.

S1-OK darf noch keine Produktions- oder Testimplementierung, keinen
Runtimecommit, keine O3-Auswertung und keinen Feld-, Transfer- oder
Runnerpfad ausfuehren.
