# S2-GQ: Statischer Abnahmeaudit von S2-GP

## Auftrag und Ausfuehrungsgrenze

S2-GQ prueft den S2-GP-Korrekturvertrag rein statisch auf vollstaendige
Materialisierbarkeit, Nichtzirkularitaet, terminale Eindeutigkeit und
Budgetdeckung.

Es wurden keine Projektmodule importiert, keine Tests ausgefuehrt und keine
Rezeptor-, Speicher-, Projektions-, Verbraucher-, Runner- oder Dateifunktion
aufgerufen.

Gepruefter Stand:

- S2-GP-Vertrag:
  `700baf58885ca51a10cb18f1765a0681984e78c2058ddb4ab38ba5046ab33fc8`
- Erfolgsregistry:
  `126bb311b01e3075ae68cf0e017f547103d3e4a1b068021670196d9b4338dcc5`
- Fehlerregistry:
  `23e49213b0ab94654ac4019bb25282c1bec0c47681ad9594e9e8c786a45ac8be`

## Bestandene Teilpruefungen

### Erfolgsregistry ist lueckenlos nummeriert

Die Erfolgsregistry enthaelt exakt 139 Zeilen:

```text
op-0001 bis op-0139
```

Alle IDs und Indizes sind eindeutig. Jeder lineare Erfolgsnachfolger ist
lueckenlos gebunden; `op-0139` endet bei `END`.

Die Klassenverteilung stimmt mit S2-GP ueberein. Damit entstehen bei genau
einem START und einem RESULT je Operation rechnerisch exakt:

```text
139 * 2 = 278 Ereignisse
```

### Vorhandene Operationsreferenzen sind topologisch

Alle in der Registry explizit als `result:op-<nnnn>` referenzierten
Operationseltern besitzen einen kleineren Index als ihre Kinder. Es wurde
keine rueckwaertsgerichtete Operationsreferenz und kein Zyklus im linearen
Erfolgsgraphen gefunden.

Die Ressourcenrollen sind in den 139 Registryzeilen eindeutig. Die neutralen
Operations-, History-, Quellen-, Arm- und Evaluations-IDs enthalten keine
Fallrollen.

### Publikationsformen vermeiden Zukunftsdigests

`FinalEvidencePackage`, `TerminalFinding` und `CompletionMarker`
enthalten nach der S2-GP-Korrektur keinen eigenen oder zukuenftigen
Operationsresultdigest. Das jeweilige RESULT bindet den Digest des bereits
erzeugten Artefakts.

Diese lokale Abschlussreihenfolge ist vorwaertsgerichtet:

```text
FinalEvidence -> RESULT
-> TerminalFinding -> RESULT
-> CompletionMarker -> RESULT
```

### Reine Budgetarithmetik stimmt

Die einzeln aufgefuehrten Erfolgspositionen summieren sich exakt zu:

`2.017.280 Bytes`

Die in S2-GP angegebenen sechs zusaetzlichen Fehlerereignisse und drei
Fehlerartefakte addieren sich rechnerisch auf:

`2.056.192 Bytes`

Diese Bestaetigung betrifft nur die Addition. Ob die Positionen gemeinsam
einen zulaessigen, vollstaendig typisierten Pfad bilden, wird durch die
nachfolgenden Blocker verneint.

## Blocker

### GQ-B01: Pfad- und Ownerrollen sind nicht pro Operation materialisiert

Die Erfolgsregistry besitzt die Spalten:

```text
operation_id
index
history
source_ordinal
operation_class
parent_receipts
successor
resource_role
```

Eine `path_role`-Spalte fehlt. Die globale Pfadtabelle aus S2-GP bestimmt
zwar moegliche Dateipfade, ordnet aber nicht jeder Registryoperation ihre
konkreten Lese-, Schreib- und Abschlussrollen zu.

Ebenso bindet die Registry nicht pro Operation:

- `owner_id`;
- `reservation_digest`;
- den erwarteten Ausgabepfad;
- den erlaubten Journalpfad;
- die zulaessige Schreibart;
- den konkreten Artefakttyp.

Damit kann die allgemeine Aussage, Owner und Reservierung reichten bis zum
letzten Resultat, nicht fuer jede der 139 Operationen mechanisch geprueft
werden. Eine globale Konvention ersetzt die geforderte literale Zuordnung
nicht.

### GQ-B02: Der Fehlerabzweig ist nicht von jedem Fehlerpunkt erreichbar

Die Erfolgsregistry besitzt keine `failure_successor`- oder gleichwertige
Fehlerkante. Die Fehlerregistry beginnt nur abstrakt mit:

```text
last-valid-event + failed-operation + partial-state
-> err-0001
```

Es fehlt eine vollstaendige Zuordnung fuer jede Erfolgsoperation und jede
zulaessige Fehlerphase zu:

- dem letzten gueltigen Event;
- dem erlaubten Teilstand;
- dem ersten Fehlerabschluss;
- der noch verfuegbaren Pfad- und Ownerberechtigung.

Besonders `op-0001 RUN_PREPARE` kann vor erfolgreicher Reservierung
scheitern. In diesem Fall existieren weder das reservierte Laufverzeichnis
noch ein `ReservationReceipt`, auf denen der gebundene Fehlerpfad beruht.
S2-GP definiert dafuer keinen getrennten vorreservierungsgebundenen
Fehlerbeleg.

Damit sind `err-0001..err-0003` nicht aus jedem zulaessigen Fehlerpunkt
eindeutig materialisierbar.

### GQ-B03: Der EvaluationPlanSeal beeinflusst den Ausfuehrungspfad

S2-GP fordert, der vorab versiegelte Evaluationsplan sei keine Elternwurzel
des Ausfuehrungspfads. Die Erfolgsregistry bindet bei `op-0001` jedoch
ausdruecklich:

```text
execution-plan + evaluation-plan-seal + run-authorization
```

Zusaetzlich enthaelt der `ReservationReceipt` den
`evaluation_plan_seal_digest`. Ab `op-0002` bindet jedes Artefakt den
daraus erzeugten `reservation_digest`.

Damit ist der Evaluationsseal transitiv Teil der Ausfuehrungsprovenienz,
bevor das `ExecutionEvidencePackage` existiert. Die spaetere
`EvaluationRunBinding` ist zwar vorwaertsgerichtet, aber nicht der erste
Beruehrungspunkt beider Wurzeln.

Die verlangte Trennung ist daher nicht erfuellt.

### GQ-B04: Erfolgs- und Fehlerabschluss sind nicht terminal exklusiv

Die Erfolgsregistry besitzt nur Erfolgsnachfolger. Die Fehlerregistry besitzt
nur ihre interne Dreierkette. Es fehlt eine kanonische terminale
Zustandsmaschine, beispielsweise:

```text
ACTIVE
-> COMPLETING -> COMPLETE

oder

ACTIVE
-> FAILING -> NOT_EVALUABLE
```

Insbesondere ist nicht literal gebunden:

- dass nach dem ersten Fehler kein weiterer Erfolgsnachfolger zulaessig ist;
- dass nach `NOT_EVALUABLE` weder `EVALUATION_RUN_BIND`,
  `PURE_EVALUATION` noch `COMPLETION_MARKER_PUBLISH` starten darf;
- dass nach Beginn des Erfolgsabschlusses nicht zugleich der
  Fehlerabschluss publiziert werden kann;
- welcher einzelne terminale Marker fuer den Lauf gueltig ist.

Die Prosa `kein Retry` ersetzt diese Zustands- und Autorisierungsgates
nicht.

### GQ-B05: Der maximale Fehlerpfad widerspricht der Abschlussausschliesslichkeit

Das Fehlermaximum von `2.056.192` Bytes wird aus allen
Erfolgsartefakten einschliesslich `CompletionMarker` sowie zusaetzlichen
Fehlerabschlussartefakten einschliesslich `FailureClosureMarker` gebildet.

Damit liegen im budgetierten Maximalpfad sowohl:

```text
COMPLETE
als auch
NOT_EVALUABLE
```

vor. S2-GP erklaert den unbestaetigten COMPLETE-Marker zwar nicht zum
gueltigen Erfolg, bindet aber keinen separaten Stagingpfad und keine Regel,
die den unbestaetigten Marker vor dem Fehlerabschluss entfernt oder
unveroeffentlicht haelt.

Der Wert ist arithmetisch konservativ, aber kein nachgewiesener,
terminal eindeutiger Pfad. Solange GQ-B04 offen ist, kann weder das
Fehlermaximum noch `MAX_RECORDING_BYTES` als vollstaendige Pfadabnahme
gelten.

### GQ-B06: Fehlercodes und neutrale Nachrichtentexte sind nicht registriert

`RunFailureReceipt` bindet die Felder `neutral_error_code` und
`failure_message_id`. S2-GP fordert einen vorregistrierten technischen
Nachrichtentext, legt aber keine literale Fehlercode- und Nachrichtenregistry
vor.

Damit kann der Audit nicht pruefen:

- welche Fehlercodes zulaessig sind;
- welche Nachricht zu welchem Code gehoert;
- welche maximale Nachrichtengroesse gilt;
- ob jeder konkrete Text frei von Fallrolle, Zielwert und Evaluationsinhalt
  bleibt.

Die Datenform ist vorhanden, ihre zulaessigen Inhalte sind noch nicht
materialisiert.

## Auditentscheidung

S2-GP verbessert die Laufanatomie wesentlich. Die 139 Erfolgsoperationen sind
lueckenlos, der lineare Erfolgsgraph ist topologisch, die 278 Ereignisse sind
korrekt hergeleitet und die beiden Zahlenbudgets sind richtig addiert.

Der Gesamtvertrag ist dennoch nicht implementierungsreif. Pfad- und
Ownerrollen, Fehlerkanten, Evaluationstrennung, terminale Exklusivitaet,
pfadgueltiges Fehlerbudget und neutrale Fehlerformen sind noch nicht
vollstaendig materialisiert.

Status:

`BLOCKED_S2GQ_S2GP_NOT_YET_IMPLEMENTATION_READY`

Fixtures, Runner, Recorder, Verifikator, Tests und Ausfuehrung bleiben
gesperrt. S2-GK, Bilder, Schwellen, Speicherkerne und Erfolgskriterien bleiben
unveraendert.

## Naechster enger Schritt

Der naechste fachlich begruendete Schritt ist ein statischer
Korrekturvertrag ausschliesslich fuer `GQ-B01` bis `GQ-B06`:

1. Pfad-, Owner-, Reservierungs- und Artefaktrollen pro Registryoperation;
2. eine explizite Fehlerkante fuer jede zulaessige Erfolgsoperation und
   Fehlerphase, einschliesslich Vorreservierungsfehler;
3. vollstaendige Entfernung des `EvaluationPlanSeal` aus der
   Ausfuehrungsprovenienz vor `EvaluationRunBinding`;
4. eine terminale Zustandsmaschine mit gegenseitig exklusiven Erfolgs- und
   Fehlerpfaden;
5. getrennte exakte Pfadbudgets ohne gleichzeitige Erfolgs- und Fehlermarker;
6. eine literale neutrale Fehlercode- und Nachrichtenregistry.

Diese Korrektur darf den Funktionsvertrag nicht aendern.

