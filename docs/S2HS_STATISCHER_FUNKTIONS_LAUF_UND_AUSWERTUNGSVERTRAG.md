# S2-HS: Statischer Funktions-, Lauf- und Auswertungsvertrag

Status: `STATIC_CONTRACT_BOUND_IMPLEMENTATION_AND_EXECUTION_LOCKED`

## Ziel und Grenze

S2-HS bindet genau einen spaeteren privaten Konfliktvergleich mit gleichzeitig
erzeugtem `A_RECENT` und `B_STABLE`. Geprueft wird ausschliesslich, ob ein
bereits qualifizierter S2-HQ-Verbraucher die ausdruecklich angeforderte Rolle
verwendet und den nicht angeforderten Bereich ohne Einfluss laesst.

Dieser Schritt implementiert und importiert nichts. Er fuehrt keine Bilder,
Speicher-, Projektions-, Verbraucher- oder Testfunktion aus. B4, TSPM-1,
PPB-1, S2-FS, S2-GC, S2-GI, S2-HQ, Rezeptoren, API, Snapshot und Feldpfad
bleiben unveraendert. Die binaere S2-GT-Registry wird weder erweitert noch
als Q0/Q1-Quelle verwendet.

## Gebundene Quellen

Die spaetere Materialisierung darf ausschliesslich die qualifizierten
privaten Komponenten verwenden:

- die S2-HQ-Byte-Block-Fixture fuer `V0`, `V1`, `Q0` und `Q1`;
- die synthetischen auditiven Rezeptorzustaende `M0`, `M1` und `MQ`;
- den atomaren privaten S2-FS-B4-/TSPM-1-Koordinator;
- die read-only S2-GC- und S2-GI-Projektionen;
- den S2-HQ-Rollenverbraucher und seine unabhaengige Direktbaseline.

Die Schwellen bleiben unveraendert:

```text
visuell: 44/765 = 132/2295
auditiv: 1/5

d(V0,V1) = 255/2295
d(Q0,V0) = d(Q1,V1) = 127/2295
d(Q0,V1) = d(Q1,V0) = 128/2295

d(M0,M1) = 1/4
d(MQ,M0) = d(MQ,M1) = 1/8
```

V0 und V1 unterscheiden sich ausschliesslich an den maskierten visuellen
Indizes `1` und `3`. Q0 und Q1 sind reale `uint8`-Blockbilder aus der eigenen
S2-HQ-Fixture. Die gemeinsame Verbraucherprobe ist dagegen die bereits
qualifizierte maskierte Probe mit neun sichtbaren und neun maskierten
Positionen. Vollprobe und Verbraucherprobe sind verschiedene Rollen.

## Zwei reale Bildungsgeschichten

Beide Geschichten beginnen mit getrennten frischen Composite-Zustaenden und
eigenen Ownerketten. Jeder Schritt verwendet eine real materialisierte
visuelle Rezeptorquelle und den gebundenen synthetischen auditiven Zustand.

| Geschichte | Schritte 1-4 | Schritt 5 | Vollprobe | erwartetes A | erwartetes B |
|---|---|---|---|---|---|
| `h0` | `V1/M1` viermal | `V0/M0` | `Q0/MQ` | `V0/M0` | `V1/M1` |
| `h1` | `V0/M0` viermal | `V1/M1` | `Q1/MQ` | `V1/M1` | `V0/M0` |

Die vier B-Expositionen muessen folgende native Folge belegen:

```text
1: FAST_CREATED, kein PPB-Aufruf, Slow-Support 0
2: FAST_UPDATED, PPB-Erzeugung, Slow-Support 1
3: FAST_UPDATED, PPB-Aktualisierung, Slow-Support 2
4: FAST_UPDATED, PPB-Aktualisierung, Slow-Support 3 und stabil
```

Schritt 5 muss wegen `d(M0,M1) = 1/4 > 1/5` einen getrennten A-Fast-Slot
erzeugen. Er darf keinen PPB-Aufruf ausloesen und weder den B-Prototyp noch
dessen Support oder Bankdigest veraendern. Danach muessen gleichzeitig
gelten:

- B4 enthaelt alle fuenf Bildungen; A besitzt den hoechsten
  `formation_index`;
- TSPM-Fast enthaelt A und B in getrennten Slots;
- B ist weder abgelaufen noch verdraengt;
- auditive und visuelle B-Prototypen besitzen Support `3` und `stable=True`;
- die Vollprobe erzeugt A als `B4_RECENT` und `TSPM_FAST` sowie B als
  `TSPM_SLOW`;
- S2-GI gibt exakt die zwei Bereiche `A_RECENT` und `B_STABLE` aus.

Die S2-GC-Sequenzrolle ist fuer diesen Versuch `NOT_REQUESTED` und besitzt
keine Referenzen. Die gespeicherten B4-Bildungsindizes bleiben im Zustand
erhalten, werden aber weder projiziert noch als Entscheidungshilfe benutzt.

Jede Abweichung in dieser Erreichbarkeitskette ist ein methodischer Bruch und
kein funktionaler Negativbefund.

## Vier gerichtete Rollenfaelle

Die Faelle verwenden keine zweite Bildung. `c01` und `c02` teilen dasselbe
fertige h0-Bundle; `c03` und `c04` teilen dasselbe fertige h1-Bundle. Jeder
Fall erhaelt dieselbe maskierte Probe und genau eine ausdrueckliche
`requested_area`.

| Fall | Bundle | A-Belegung | B-Belegung | angefordert | vorab gebundene Ausgabe |
|---|---|---|---|---|---|
| `c01` | `h0` | `V0` | `V1` | `A_RECENT` | neun Maskenwerte aus `V0` |
| `c02` | `h0` | `V0` | `V1` | `B_STABLE` | neun Maskenwerte aus `V1` |
| `c03` | `h1` | `V1` | `V0` | `A_RECENT` | neun Maskenwerte aus `V1` |
| `c04` | `h1` | `V1` | `V0` | `B_STABLE` | neun Maskenwerte aus `V0` |

Die Solltabelle ist Bestandteil eines vor Ausfuehrung unveraenderlich
versiegelten `EvaluationPlanSeal`. Dessen Digest darf weder im
`ExecutionPlan` noch in einer Quellen-, Speicher-, Projektions-, Rollen- oder
Armoperation vorkommen. Erst nach einem vollstaendigen
`ExecutionEvidencePackage` verbindet `EvaluationRunBinding` beide unabhaengige
Wurzeln.

## Rollenisolierung und Baseline

Verbraucher und Direktbaseline erhalten pro Fall bytegleich:

- dieselbe maskierte Probe und denselben Probequellendigest;
- dasselbe unveraenderliche S2-GI-Bundle;
- dieselbe explizite Rollenbindung;
- denselben ausgewaehlten Kandidatenzugriff;
- dieselben Funktionsgrenzen.

Die Direktbaseline muss unabhaengig implementiert bleiben und darf weder den
Verbraucher aufrufen noch dessen Ergebnis uebernehmen. Fuer beide Arme gilt
bei erfolgreicher Vervollstaendigung exakt:

```text
mask_validation_count      = 18
visible_compare_count      = 9
masked_copy_count          = 9
area_lookup_count          = 1
candidate_reference_count  = 1
component_reference_count  = 1
value_reference_count      = 18
digest_operation_count     = 2
```

Der nicht gewaehlte Bereich darf weder Ergebniswert, Status,
`completed_positions`, Ressourcenledger noch Quellenauswahl beeinflussen.
Dies wird spiegelbildlich geprueft: Ein Rollenwechsel bei identischem Bundle
muss die Ausgabe wechseln; ein Kandidatentausch bei gleicher Rollenwahl muss
der gewaehlten Rolle folgen.

Es gibt keine automatische Auswahl, Rangfolge, Verschmelzung, Ersatzquelle
oder Rueckfallregel. `A_RECENT.fast_internal` darf insbesondere nicht als
Ersatz fuer den oeffentlichen B4-Recent-Kandidaten verwendet werden.

## Exakter Erfolgsumfang

Die literale Registry steht in `docs/S2HS_OPERATION_REGISTRY.csv`. Sie bindet
genau:

| Klasse | Anzahl |
|---|---:|
| Vorbereitung und Quellenbindung | 3 |
| History-Initialisierungen | 2 |
| reale Rezeptoranalysen | 12 |
| atomare Composite-Bildungen | 10 |
| Composite-read-only-Proben | 2 |
| S2-GC-Projektionen | 2 |
| S2-GI-Projektionen | 2 |
| History-Invariantenabschluesse | 2 |
| Rollenbindungen | 4 |
| Rollenverbraucher | 4 |
| Direktbaselines | 4 |
| Fallbelegabschluesse | 4 |
| Ausfuehrungsevidenzabschluss | 1 |
| Evaluationsbindung | 1 |
| Fallevaluationen | 4 |
| Aggregatentscheidung | 1 |
| Terminalvorbereitung und Abschlussmarker | 2 |
| **Gesamt** | **60** |

Jede Operation erzeugt genau ein hashverkettetes `START`- und ein
`RESULT`-Ereignis. Der vollstaendige Erfolgspfad besitzt daher exakt
`120` Ereignisse. `START` hat Index `2*n-1`, `RESULT` Index `2*n`; jedes
Ereignis bindet Lauf-ID, Operations-ID, Phase, Owner, Elternresultate,
Payloaddigest, vorherigen Eventdigest und eigenen Eventdigest.

Ein technischer Fehler ersetzt das RESULT der betroffenen Operation durch
ein typisiertes Fehlerresultat. Danach sind ausschliesslich die zwei
registrierten Fehlerabschlussoperationen `FAILURE_EVIDENCE_SEAL` und
`NOT_EVALUABLE_PUBLISH` erlaubt. Bei Fehler in Erfolgsoperation `n` umfasst
der Fehlerpfad `n+2` Operationen und `2*n+4` Ereignisse, maximal `62/124`.
Vor erfolgreicher Laufreservierung entsteht nur `START_BLOCKED` ohne
Laufartefakt. Es gibt keinen Retry, keine Teilfortsetzung und keine
gleichzeitige Erfolgs- und Fehlerterminalisierung.

## Ressourcenbindung

Die beiden Geschichten und die vier Rollenfaelle sind strukturell
budgetgleich. Gebunden sind:

- `10` Formationseingaben mit je `26` AV-Werten, insgesamt `260` Werte;
- `2` Vollproben mit je `26` AV-Werten, insgesamt `52` Werte;
- `12` reale visuelle Analysen mit je `18` Ausgabewerten;
- B4-Kapazitaet `9`, TSPM-Fast-Kapazitaet `3` und unveraenderte
  PPB-1-Konfiguration;
- `10` S2-FS-Formationsledger mit je `617` Schreibwoertern, `468`
  Distanztermen und `54` Kontrolltermen;
- `2` S2-FS-read-only-Ledger mit je `14` Schreibwoertern, `468`
  Distanztermen und `48` Kontrolltermen.

Damit betraegt der gebundene S2-FS-Gesamtumfang:

```text
Schreibwoerter:  10*617 + 2*14  = 6198
Distanzterme:    10*468 + 2*468 = 5616
Kontrollterme:   10*54  + 2*48  = 636
```

Fuer beide S2-GC-Bundles werden aufgrund der fuenf B4-Eintraege, zwei
Fast-Slots und je eines auditiven und visuellen Slow-Slots maximal gebunden:

```text
validated_evidence_records = 10
validated_digest_count     = 12
role_projection_count      = 3
candidate_count            = 3
component_count            = 4
value_count                = 78
sequence_reference_count   = 0
digest_operation_count     = 13
```

Jedes S2-GI-Ledger bindet `1/3/3/4/78/0/2/4` fuer validierte Bundles,
Rollen, Kandidaten-, Komponenten-, Wert- und Sequenzreferenzen,
Bereichsprojektionen und Digestoperationen. Vier Verbraucher und vier
Baselines erhalten jeweils exakt den oben gebundenen 59-Term-Ledgerumfang.

Recorder-, Serialisierungs- und Laufzeitkosten werden getrennt von diesen
Funktionsbudgets berichtet. Sie duerfen keinen Arm bevorzugen und keine
fehlende Funktionsarbeit verdecken. Eine unvollstaendige Aufzeichnung macht
den Lauf `NOT_EVALUABLE`; sie ist kein negativer Memory-Befund.

## Owner- und Einmaligkeitsvertrag

- Ein `run_owner` reserviert genau eine neutrale Lauf-ID und endet in
  `CONSUMED` oder `FAILED`.
- `h0_history_owner` und `h1_history_owner` besitzen getrennte frische
  Anfangszustaende und duerfen nie gegenseitig als Quelle dienen.
- Jeder der zehn Formation-Schritte besitzt einen eigenen Owner, der vor dem
  Aufruf an Konfiguration, Vorzustand und Eingang gebunden und genau einmal
  verbraucht wird.
- Jeder Probe- und Projektionsowner ist an genau den finalen Zustand seiner
  Geschichte gebunden und darf diesen nicht veraendern.
- Jeder Fallowner erzeugt zwei getrennte Einmaltoken fuer Verbraucher und
  Baseline. Beide Token referenzieren dieselbe Rollenbindung, erlauben aber
  keine Ergebnisweitergabe zwischen den Armen.
- Der `evaluation_owner` entsteht erst aus dem vollstaendigen
  `EvaluationRunBinding` und darf keine Ausfuehrungsoperation autorisieren.
- Nach `COMPLETE`, `NOT_EVALUABLE` oder `START_BLOCKED` ist jede weitere
  Operation verboten.

## Verbindliche Belegformen

Alle Formen sind unveraenderlich, ASCII-kanonisch und SHA-256-gebunden.

### `S2HSExecutionPlan`

Bindet neutrale Lauf-ID, Vertragsdigest, Quellenhashes, Konfiguration,
Fixture-Digests, Registrydigest, Operations- und Ressourcenbudgets sowie den
Plandigest. Er enthaelt keinen Evaluationsplandigest und keine Sollausgabe.

### `S2HSReceptorReceipt`

Bindet Operation, Geschichte, Quellordinalzahl, Bildbytesdigest, auditiven
Wertedigest, visuellen Wertedigest, AV-Wertedigest, Envelope-, Quellen- und
START-Eventdigest. Vollobjekte bleiben In-Memory-Quellen und werden nicht als
Auswertungserwartung umgedeutet.

### `S2HSFormationReceipt`

Bindet Formation-Owner-Vorzustand, ReceptorReceipt, Eingang, Composite-
Vorzustand, B4-Ereignis und Bildungsindex, TSPM-Fast-Ereignis,
Konsolidierungsbefund, auditive und visuelle Slow-Supports, B4-/Fast-/Slow-
und Composite-Nachzustandsdigests sowie das native S2-FS-Ledger.

### `S2HSReadOnlyReceipt`

Bindet Vollprobe, finalen Composite-Zustand, getrennte B4-, Fast-, auditive
Slow- und visuelle Slow-Befunde, Support und Stabilitaet, Findingdigest,
Ledger sowie identische Vor-/Nachzustandsdigests.

### Projektionsbelege

`S2HSS2GCProjectionReceipt` und `S2HSS2GIProjectionReceipt` binden jeweils
Quellfinding beziehungsweise Quellbundle, Kandidaten- und Bereichsrollen,
Ressourcenledger, Ausgabe- und Zustandsdigests. Sie duerfen keine Zielwerte
oder angeforderte Rolle enthalten.

### Rollen- und Armbelege

`S2HSRoleBindingReceipt` bindet Fall, maskierte Probe, Bundle, Zustand,
`requested_area` und den ausgewaehlten Bereichsfindingdigest. Der
nicht ausgewaehlte Bereich wird nur ueber den unveraenderten Bundledigest
belegt, nicht als Wertquelle uebergeben.

`S2HSArmReceipt` bindet Armtyp, Rollenbindung, Status, Ausgabewerte,
Maskenpositionen, verwendete Rollen-, Kandidaten-, Komponenten- und
Quelldigests, Ledger sowie identische Vor-/Nachzustandsdigests.

### Ausfuehrung und Evaluation

`S2HSExecutionEvidencePackage` bindet Registry, alle 120 Erfolgsereignisse,
History-, Fall- und Quelldigests sowie den finalen Journaldigest, aber keine
Sollwerte. `S2HSEvaluationRunBinding` ist der erste Beruehrungspunkt zwischen
diesem Paket und dem unabhaengigen `EvaluationPlanSeal`.

Jedes `S2HSEvaluationFinding` bindet den beobachteten Fallbeleg, die
vorversiegelte Zielprojektion, sichtbare Unveraendertheit, Maskenfehler,
Baselinegleichheit, Rollentreue, Nulleinfluss des nicht gewaehlten Bereichs
und read-only Status. `S2HSTerminalFinding` fasst die vier Findings zusammen.
`S2HSCompletionMarker` bindet Terminal- und Evidenzdigest, aber niemals den
eigenen zukuenftigen Digest.

## Digestgraph und Nichtzirkularitaet

```text
Quellen + ExecutionPlan
-> START
-> Rezeptorbeleg
-> Formation und Zustand
-> Vollprobe und read-only Finding
-> S2-GC
-> S2-GI
-> Rollenbindung
-> Verbraucher / unabhaengige Baseline
-> CaseEvidence
-> ExecutionEvidencePackage

unabhaengiger EvaluationPlanSeal
        + ExecutionEvidencePackage
-> EvaluationRunBinding
-> vier Findings
-> Aggregat
-> Terminal
-> CompletionMarker
```

Keine fruehe Kante darf auf Fallziel, Sollausgabe, spaeteres Ergebnis oder
eigenen Digest zeigen. Der Rollenname ist ein expliziter Funktionsinput; die
Bewertung, welcher Bildinhalt dadurch erwartet wird, bleibt Evaluation.

## `NOT_EVALUABLE` und funktionale Falsifikation

`NOT_EVALUABLE` gilt bei Quellen-, Fixture-, Konfigurations-, Owner-,
Digest-, Reihenfolge-, Ereignis-, Ressourcen-, Read-only-, Aufzeichnungs-
oder Terminalbruch sowie wenn A und B nicht gleichzeitig wie gebunden
erreichbar sind. Es erfolgt dann keine Funktionsinterpretation.

Bei vollstaendig gueltiger Beweiskette ist die Funktion falsifiziert, wenn
mindestens eines gilt:

- die Ausgabe folgt nicht der explizit angeforderten Rolle;
- der nicht gewaehlte Kandidat beeinflusst Ausgabe, Status oder Kosten;
- Verbraucher und Direktbaseline unterscheiden sich;
- sichtbare Werte werden veraendert oder nicht exakt neun Maskenwerte
  ergaenzt;
- eine der beiden Spiegelrichtungen zeigt eine andere Rollenregel.

Ein vollstaendiger Lauf darf daher `COMPLETE` sowohl mit bestaetigter als auch
mit falsifizierter Funktion erreichen. Nur ein methodischer oder technischer
Bruch fuehrt zu `NOT_EVALUABLE`.

Der maximal zulaessige positive Befund lautet:

```text
S2HS_ROLE_ADDRESSED_TWO_AREA_CONTEXT_VALID_DIRECT_FILL_EXPLAINS
```

Er bestaetigt ausschliesslich, dass gleichzeitig vorhandene A- und B-Bereiche
kontrolliert und explizit adressierbar sind. Er belegt keine automatische
Kontextwahl, keine intelligente Relevanzentscheidung, keine neue Memory-
Mechanik und keine MCM-Feldwirkung.

## Freigabegrenze

S2-HS ist mit diesem Dokument statisch gebunden. Noch gesperrt bleiben:

- Fixture-, Runner-, Recorder- und Verifikatorimplementierung;
- Tests, Imports und jede Zustands- oder Rezeptorausfuehrung;
- der reale Konfliktfunktionslauf;
- automatische Auswahl, Feldintegration, API und Snapshot.

Der naechste zulassige Schritt ist ein rein statischer Materialisierungs-,
Registry-, Budget- und Belegformaudit dieses Vertrags. Erst dessen Bestehen
darf eine eng begrenzte private Laufimplementierung begruenden.
