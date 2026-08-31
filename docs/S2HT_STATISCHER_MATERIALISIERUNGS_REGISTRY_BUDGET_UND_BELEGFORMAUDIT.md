# S2-HT: Statischer Materialisierungs-, Registry-, Budget- und Belegformaudit

Status: `STATIC_AUDIT_PASS_PRIVATE_RUN_SHELL_MAY_BE_IMPLEMENTED`

## Auditgrenze

S2-HT prueft den S2-HS-Vertrag gegen die vorhandenen privaten Rezeptor-,
B4-, TSPM-1-, PPB-1-, S2-FS-, S2-GC-, S2-GI- und S2-HQ-Grenzen.

Es wurden keine Projektmodule importiert, keine Bilder durch einen Rezeptor
ausgefuehrt, keine Zustaende gebildet, keine Verbraucher aufgerufen und keine
Tests oder Laeufe gestartet. Die Pruefung beruht ausschliesslich auf
Quelltext, gebundenen Digests, den qualifizierten S2-HQ-Fixtures und
statischer Registry-, Bruch-, Groessen- und Grapharithmetik.

Die bestehende S2-GT-Registry bleibt unveraendert. S2-HT oeffnet weder deren
alten Laufpfad noch einen Kontextfunktionslauf.

## 1. Materialisierung der beiden Geschichten

Beide Geschichten besitzen genau fuenf Formationseingaben, einen
vollstaendigen read-only Probeinput und einen frischen Composite-Anfang.

### Geschichte h0

```text
1 V1/M1 -> FAST_CREATED, Slow-Support 0
2 V1/M1 -> FAST_UPDATED, PPB-Erzeugung, Support 1
3 V1/M1 -> FAST_UPDATED, PPB-Aktualisierung, Support 2
4 V1/M1 -> FAST_UPDATED, PPB-Aktualisierung, Support 3, stabil
5 V0/M0 -> FAST_CREATED mit partiellem visuellen Konflikt, kein PPB-Aufruf
Probe Q0/MQ
```

### Geschichte h1

```text
1 V0/M0 -> FAST_CREATED, Slow-Support 0
2 V0/M0 -> FAST_UPDATED, PPB-Erzeugung, Support 1
3 V0/M0 -> FAST_UPDATED, PPB-Aktualisierung, Support 2
4 V0/M0 -> FAST_UPDATED, PPB-Aktualisierung, Support 3, stabil
5 V1/M1 -> FAST_CREATED mit partiellem visuellen Konflikt, kein PPB-Aufruf
Probe Q1/MQ
```

Die vorhandene TSPM-1-Auswahl verlangt fuer ein gemeinsames Fast-Update,
dass auditive und visuelle Distanz jeweils innerhalb ihrer Schwelle liegen.
Beim fuenften Schritt gilt zwar visuell `1/9 <= 1/5`, aber auditiv
`1/4 > 1/5`. Deshalb kann A den vorhandenen B-Slot nicht gemeinsam matchen.
Der partielle visuelle Match wird als Konfliktbeleg erhalten; der operative
Pfad ist ein neuer Fast-Slot ohne Konsolidierung.

Damit bleibt nach Schritt 5 in beiden Geschichten statisch zwingend:

- B-Slow auditiv und visuell bei Support `3` und `stable=True`;
- der B-Bankdigest gegenueber Schritt 4 unveraendert;
- A als juengster B4-Eintrag mit `formation_index = 5`;
- A als eigener TSPM-Fast-Slot;
- zwei Fast-Slots bei Kapazitaet `3`, also keine Ersetzung;
- B-Alter `1` bei Ablaufgrenze `8`, also kein Ablauf;
- fuenf B4-Eintraege bei Kapazitaet `9`, also keine FIFO-Verdraengung.

Die gleichzeitige Verfuegbarkeit von A und B ist somit aus den vorhandenen
Uebergaengen erreichbar und wird nicht nachtraeglich aus Fallmetadaten
erzeugt.

## 2. Rezeptor- und Probegeometrie

Die 18 visuellen Rezeptorwerte entstehen aus konstanten `uint8`-Bloecken in
einem `80 x 120 x 3`-Bild. Statisch ergeben sich:

```text
V0 = (1,0,0,1,1,0,0,1,1,0,0,1,1,0,0,1,1,0)
V1 = (1,1,0,0,1,0,0,1,1,0,0,1,1,0,0,1,1,0)

Q0 = (1,127/255,0,128/255,1,0,0,1,1,0,0,1,1,0,0,1,1,0)
Q1 = (1,128/255,0,127/255,1,0,0,1,1,0,0,1,1,0,0,1,1,0)
```

Die exakten normalisierten L1-Abstaende ueber 18 Werte lauten:

```text
d(V0,V1) = (1+1)/18 = 1/9 = 255/2295

d(Q0,V0) = d(Q1,V1)
         = (127/255 + 127/255)/18
         = 127/2295

d(Q0,V1) = d(Q1,V0)
         = (128/255 + 128/255)/18
         = 128/2295

tau = 44/765 = 132/2295
```

Beide Vollproben liegen damit zu beiden Kandidaten innerhalb der
Funktionsschwelle. Q0 bevorzugt V0 und Q1 bevorzugt V1 jeweils um exakt
`1/2295`. Die Richtungen sind gespiegelt. Auditiv gilt weiterhin
`d(MQ,M0) = d(MQ,M1) = 1/8 <= 1/5`.

Die gemeinsame maskierte Verbraucherprobe ist davon getrennt. V0 und V1
unterscheiden sich nur an den maskierten Indizes `1` und `3`; alle sichtbaren
Positionen sind gleich. Vollprobe, Speicherabruf und Maskenverbrauch koennen
daher nicht ihre Rollen tauschen.

## 3. Vier symmetrische Rollenfaelle

| Fall | Geschichte | angefordert | gewaehlter Inhalt | nicht gewaehlter Inhalt |
|---|---|---|---|---|
| `c01` | h0 | `A_RECENT` | V0 | V1 |
| `c02` | h0 | `B_STABLE` | V1 | V0 |
| `c03` | h1 | `A_RECENT` | V1 | V0 |
| `c04` | h1 | `B_STABLE` | V0 | V1 |

`c01/c02` referenzieren bytegleich dasselbe h0-Bundle; `c03/c04` dasselbe
h1-Bundle. Kein Fall besitzt einen Bildungs- oder Projektionsaufruf. Der
einzige funktionale Unterschied innerhalb eines Paars ist
`requested_area`.

Verbraucher und Direktbaseline erhalten je Fall dieselbe Probe, dasselbe
Bundle, dieselbe Rollenbindung und denselben 59-Term-Ledger:

```text
18 Maskenpruefungen + 9 Sichtvergleiche + 9 Kopien
+ 1 Bereich + 1 Kandidat + 1 Komponente + 18 Werte + 2 Digests = 59
```

Die Baseline importiert den gemeinsamen unveraenderlichen Bindungstyp und
die Rollenmenge aus S2-HQ. Sie ruft jedoch weder
`complete_from_explicit_area` noch eine interne Auswahl- oder
Ergebnisfunktion des Verbrauchers auf. Ihre Auswahl- und Fuellfunktion ist
eigenstaendig. Gemeinsamer Vertrag ist damit erlaubt; Ergebnis- oder
Aufrufwiederverwendung ist ausgeschlossen.

Jeder der acht Armbelege muss `prestate_digest == poststate_digest` gegen den
vollstaendigen Composite-Zustand seiner Geschichte nachweisen. Der
Historyabschluss nach beiden Faellen muss nochmals denselben B4-, Fast-,
auditiven Slow-, visuellen Slow- und Composite-Digest wie vor `c01/c02`
beziehungsweise `c03/c04` binden. Damit ist Read-only nicht nur pro Aufruf,
sondern ueber den gesamten Rollenvergleich geschlossen.

## 4. Registry und Ereignisse

Die CSV-Registry wurde vollstaendig gelesen und statisch geprueft:

- exakt `60` Datenzeilen;
- Indizes lueckenlos `1..60`;
- Operations-IDs lueckenlos `hs-op-001..hs-op-060`;
- keine doppelte Operations-ID;
- alle internen Eltern existieren und besitzen einen kleineren Index;
- genau eine externe Wurzel, `external-evaluation-plan-seal`, erst bei
  `hs-op-053`;
- `30` unterschiedliche Ownerrollen und `19` Receipt-Typen;
- jede Erfolgsoperation besitzt genau ein START-/RESULT-Paar.

Der Erfolgspfad hat daher exakt `120` Ereignisse. Die Paarung ist
deterministisch:

```text
Operation n -> START 2*n-1 -> RESULT 2*n
```

Die Registry ist topologisch ausfuehrbar und azyklisch. Die lineare
Ausfuehrungsreihenfolge bleibt die numerische Registryreihenfolge, auch wenn
h0 und h1 keine Zustaende teilen.

## 5. Getrennte Vertragswurzeln

Der Gesamtdokument-Digest des S2-HS-Dokuments darf nicht als Elternbeleg des
Ausfuehrungspfads verwendet werden, weil dasselbe Dokument auch die
Evaluationserwartungen enthaelt. S2-HT materialisiert deshalb zwei typisierte
Teilwurzeln:

### `S2HSExecutionContractDigest`

Enthaelt ausschliesslich:

- Quellen- und Konfigurationsbindung;
- h0/h1-Eingabefolgen ohne Sollausgaben;
- Registry und Erfolgs-/Fehlerbudgets;
- Receipt-, Owner-, Zustands- und Read-only-Regeln;
- maskierte Probe und explizit angeforderte Rollen.

### `S2HSEvaluationPlanSealDigest`

Enthaelt ausschliesslich:

- `c01 -> V0`, `c02 -> V1`, `c03 -> V1`, `c04 -> V0`;
- Gleichheit mit der Direktbaseline;
- sichtbare Unveraendertheit und exakt neun Maskenwerte;
- Nulleinfluss des nicht gewaehlten Bereichs;
- Bestaetigungs- und Falsifikationsregeln.

Der Gesamtdokument-Digest bleibt nur Provenienznachweis und ist keine
Ausfuehrungsautoritaet. `EvaluationRunBinding` in Operation 53 ist der erste
und einzige Knoten, der `ExecutionEvidencePackage` und den unabhaengigen
Evaluationseal gemeinsam referenziert. Damit gelangen Zielwerte weder
direkt noch indirekt in Rezeptor-, Speicher-, Projektions-, Rollen- oder
Armoperationen.

## 6. Owneruebergaenge

Die Registryrollen sind mit folgenden endlichen Uebergaengen
materialisierbar:

| Ownerklasse | Anfang | erlaubte Zwischenzustaende | terminal |
|---|---|---|---|
| Lauf | `RESERVED` | `ACTIVE`, `EXECUTION_SEALED`, `EVALUATING`, `COMPLETING` | `CONSUMED` oder `FAILED` |
| Geschichte | `FRESH` | `ACTIVE` | `SEALED` oder `FAILED` |
| Formation | `AUTHORIZED` | `SOURCE_BOUND`, `BUSY` | `CONSUMED` oder `FAILED` |
| Probe | `AUTHORIZED` | `SOURCE_BOUND`, `BUSY` | `CONSUMED` oder `FAILED` |
| Projektion | `AUTHORIZED` | `S2GC_PROJECTED` | `CONSUMED` oder `FAILED` |
| Fall | `AUTHORIZED` | `ROLE_BOUND`, `ARMS_COMPLETE` | `SEALED` oder `FAILED` |
| Arm | `AUTHORIZED` | `BUSY` | `CONSUMED` oder `FAILED` |
| Evaluation | `UNBOUND` | `BOUND`, `EVALUATING`, `AGGREGATED` | `CONSUMED` oder `FAILED` |

Jeder Formation- und Armowner wird genau einmal verbraucht. Ein Fallowner
erteilt zwei getrennte Kindautorisierungen fuer Verbraucher und Baseline;
kein Arm darf den Ergebnisbeleg des anderen als Eingabe verwenden. Ein
Fehler setzt den betroffenen Owner und den Laufowner auf `FAILED`. Nach einem
terminalen Zustand gibt es keine Wiederverwendung.

## 7. Receiptformen und Groessen

Alle neuen S2-HS-Belege werden als kompakte, ASCII-kanonische
Aufzeichnungsprojektionen materialisiert. Vollstaendige In-Memory-Objekte
bleiben Funktionsquellen und werden nicht erneut eingebettet. Bereits
qualifizierte Grenzen werden fuer die vier grossen Rollen unveraendert
uebernommen:

- ReceptorReceipt: maximal `2765` Byte;
- FormationReceipt: maximal `2801` Byte;
- S2-GC-Receipt: maximal `3174` Byte;
- S2-GI-Receipt: maximal `2978` Byte.

Die S2-GC-Sequenzrolle ist `NOT_REQUESTED` mit leerer Referenzmenge. Die
ausgeschlossene 3236-Byte-Form mit unzulaessiger Sequenzevidenz ist daher
kein gueltiger S2-HS-Beleg.

Fuer die uebrigen typisierten Formen ergibt die statische kanonische
Worst-Case-Materialisierung mit 96-Zeichen-Owner, 64-Zeichen-Digests und den
vollstaendigen gebundenen Wertfeldern folgende Huelle:

| Receiptrolle | Voraussichtliche Vollhuelle | bindende Obergrenze |
|---|---:|---:|
| RunPreparation | 1093 | 1536 |
| SourceManifest mit bis zu 24 Quellhashes und 7 Fixture-Digests | 2821 | 3584 |
| MaskedProbe | 1021 | 1280 |
| HistoryInitial | 968 | 1280 |
| Receptor | qualifiziert | 2765 |
| Formation | qualifiziert | 2801 |
| ReadOnly | 1562 | 2048 |
| S2-GC | qualifiziert | 3174 |
| S2-GI | qualifiziert | 2978 |
| HistoryEvidence | 1762 | 2048 |
| RoleBinding | 1352 | 1792 |
| Consumer/Baseline Arm | 2270 | 2560 |
| CaseEvidence | 1182 | 1536 |
| ExecutionEvidence | 1443 | 1792 |
| EvaluationRunBinding | 798 | 1024 |
| EvaluationFinding | 1067 | 1536 |
| AggregateFinding | 1006 | 1280 |
| TerminalFinding | 849 | 1024 |
| CompletionMarker | 792 | 1024 |
| FailureEvidence | maximal 558 | 1024 |
| NotEvaluableMarker | maximal 558 | 1024 |

Ein Ereignis mit sechs Elterndigests benoetigt in derselben statischen Form
`959` Byte und erhaelt die Obergrenze `1536`. Jeder Beleg bleibt unter der
privaten Einzelgrenze `4096` Byte. `ExecutionEvidencePackage` bindet die 120
Ereignisse ueber Anzahl, finalen Journaldigest und typisierte Teilwurzeln; es
dupliziert nicht 120 Ereignisobjekte.

`S2HSFailureEvidenceReceipt` bindet ausschliesslich neutrale Fehlerkennung,
fehlgeschlagene Operation und Phase, Owner, letzten gueltigen Eventdigest und
Teilstandsdigest. `S2HSNotEvaluableMarker` bindet diesen Beleg, den
Fehlerjournalabschluss und `NOT_EVALUABLE`. Beide enthalten weder Fallziel
noch Funktionsbewertung.

Die Obergrenzen ergeben fuer den vollstaendigen Erfolgspfad:

```text
60 Receipt-Huellen: 136726 Byte
120 Ereignisse:     184320 Byte
Gesamtmaximum:      321046 Byte
```

Beim spaetestmoeglichen Fehler entfaellt der CompletionMarker und es kommen
zwei Fehlerabschlussbelege hinzu. Mit maximal `124` Ereignissen gilt:

```text
maximale Fehler-Receipt-Huellen: 137750 Byte
maximale Fehlerereignisse:       190464 Byte
maximales Fehlerpfadbudget:      328214 Byte
```

Diese Grenzen betreffen die spaetere private S2-HS-Huelle. Sie aendern weder
die S2-GT-Registry noch deren historische Gesamtbudgets. Eine spaetere
Implementierung muss die hier gebundenen Huellegrenzen vor jedem Publish
fail-closed pruefen.

## 8. Digestgraph

Der vollstaendige Graph ist vorwaertsgerichtet:

```text
ExecutionContract + Quellen
-> RunPreparation
-> SourceManifest / MaskedProbe
-> HistoryInitial
-> ReceptorReceipt
-> FormationReceipt
-> finaler Composite-Zustand
-> FullProbeReceipt
-> ReadOnlyReceipt
-> S2GCReceipt
-> S2GIReceipt
-> HistoryEvidence
-> RoleBinding
-> ConsumerReceipt / BaselineReceipt
-> CaseEvidence
-> ExecutionEvidencePackage

EvaluationPlanSeal + ExecutionEvidencePackage
-> EvaluationRunBinding
-> EvaluationFindings
-> Aggregate
-> Terminal
-> CompletionMarker
```

Jeder interne Registryelter besitzt einen kleineren Index. Receipt-Digests
werden erst nach ihren Payloads gebildet. Terminal und Marker enthalten
weder ihren eigenen noch einen zukuenftigen Digest. Der Graph ist damit
vollstaendig materialisierbar und azyklisch.

## 9. Exklusive Entscheidungen

Vor erfolgreicher Reservierung ist nur `START_BLOCKED` ohne Laufverzeichnis
zulaessig. Nach Reservierung existiert genau einer der Pfade:

```text
ACTIVE -> EXECUTION_SEALED -> EVALUATING -> COMPLETING -> COMPLETE

ACTIVE / EXECUTION_SEALED / EVALUATING / COMPLETING
-> FAILING -> NOT_EVALUABLE
```

`COMPLETE` verlangt alle 60 Erfolgsoperationen, 120 Ereignisse, vollstaendige
Belege und eine abgeschlossene Evaluation. `COMPLETE` kann einen positiven
oder funktional falsifizierten Befund enthalten.

`NOT_EVALUABLE` ist ausschliesslich fuer technische oder methodische
Vertragsverletzungen zulaessig. Danach entstehen keine Evaluation und kein
CompletionMarker. Funktionsfalsifikation ist kein technischer Fehler und
darf nicht in `NOT_EVALUABLE` umklassifiziert werden.

Die drei Zustaende `START_BLOCKED`, `NOT_EVALUABLE` und `COMPLETE` sind
gegenseitig exklusiv und terminal.

Operation 59 erzeugt nur einen unveroeffentlichten `COMPLETING`-Beleg.
`COMPLETE` entsteht atomar erst mit Operation 60. Scheitert Operation 60,
wird der vorbereitete Beleg nicht als Terminalzustand anerkannt und nur der
registrierte Fehlerabschluss darf `NOT_EVALUABLE` veroeffentlichen.

## 10. Auditentscheidung

| Pruefpunkt | Befund |
|---|---|
| h0 und h1 aus frischen Zustaenden materialisierbar | bestanden |
| B erreicht Support 3 | bestanden |
| A bleibt am Probezeitpunkt aktuell | bestanden |
| abschliessende A-Bildung veraendert B nicht | bestanden |
| Q0/Q1 und Spiegelabstaende exakt | bestanden |
| vier Rollenfaelle symmetrisch und budgetgleich | bestanden |
| Registry 60 lueckenlos, Ereignisse 120 paarweise | bestanden |
| Verbraucher und Baseline aufrufseitig unabhaengig | bestanden |
| Ausfuehrungs- und Evaluationswurzel getrennt | bestanden |
| Owneruebergaenge endlich und einmalig | bestanden |
| Receiptformen unter 4096 Byte materialisierbar | bestanden |
| Digestgraph vollstaendig und azyklisch | bestanden |
| Terminal- und Falsifikationsregeln exklusiv | bestanden |
| S2-GT-Registry unveraendert | bestanden |

S2-HT ist bestanden. Eine kleine private S2-HS-Laufhuelle darf nun in einem
separaten Schritt implementiert werden. Diese Freigabe umfasst noch keine
Tests, Qualifikation oder Funktionsausfuehrung.

Der maximal moegliche spaetere positive Befund bleibt:

```text
S2HS_ROLE_ADDRESSED_TWO_AREA_CONTEXT_VALID_DIRECT_FILL_EXPLAINS
```

Er wuerde nur kontrollierte explizite Adressierbarkeit zweier gleichzeitig
verfuegbarer Memory-Bereiche bestaetigen, nicht automatische Kontextwahl.
