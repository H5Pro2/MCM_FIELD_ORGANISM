# S2-IB - Statischer Korrekturvertrag des Konfliktsignals

## Status

`STATIC_FIVE_STATUS_CONFLICT_SIGNAL_CORRECTION_BOUND`

S2-IB korrigiert ausschliesslich die drei offenen S2-IA-Bindungen:

1. vollstaendige Statusdomain einschliesslich `NO_APPLICABLE_CONTEXT`;
2. genau ein atomarer Einmal-Owner je Signalaufruf;
3. unveraenderliche Daten-, Digest-, Ledger-, Operations- und Groessenformen.

Die Korrektur fuegt keine Memory-Ebene, Auswahlregel, Rangfolge,
Speicherabfrage oder Feldwirkung hinzu. Implementierung, Tests und Ausfuehrung
bleiben gesperrt.

## Fuenf regulaere Statuswerte

Fuer jeden Bereich gilt vorgelagert genau eine der drei gueltigen
Anwendbarkeitslagen:

- `APPLICABLE`: gueltiger Kandidat vorhanden und auf allen sichtbaren
  Probenpositionen passend;
- `ABSENT_VALID`: kanonisch gueltige Abwesenheit ohne Kandidat;
- `VISIBLE_CONFLICT`: gueltiger Kandidat vorhanden, aber mindestens ein
  sichtbarer Probenwert widerspricht ihm.

Seien:

```text
K = Anzahl APPLICABLE           in {0,1,2}
P = Anzahl vorhandener Kandidaten
    = APPLICABLE + VISIBLE_CONFLICT in {0,1,2}
```

Dann ist die Statusfunktion vollstaendig und exklusiv:

| Ergebnisstatus | Exakte Bedingung |
| --- | --- |
| `NO_CONTEXT` | A und B sind beide exakt `ABSENT_VALID`; damit `K=0, P=0`. |
| `NO_APPLICABLE_CONTEXT` | `K=0` und `P>=1`; jeder vorhandene Kandidat ist `VISIBLE_CONFLICT`. |
| `SINGLE_SOURCE` | Exakt `K=1`; der andere Bereich ist `ABSENT_VALID` oder `VISIBLE_CONFLICT`. |
| `CONSISTENT` | `K=2` und alle neun maskierten Ergaenzungswerte sind positionsweise gleich. |
| `CONFLICT` | `K=2` und mindestens ein maskierter Ergaenzungswert unterscheidet sich. |

Keine andere Kombination aus zwei gueltigen Anwendbarkeitslagen existiert.
Typ-, Rollen-, Quellen-, Probe-, Zustands-, Digest- oder Ressourcenbruch ist
keine Anwendbarkeitslage und erzeugt niemals einen regulaeren Status.

## Eingabeform

`TwoAreaConflictSignalInput` ist unveraenderlich und enthaelt exakt:

```text
schema
invocation_id
function_role                 SIGNAL | DIRECT_BASELINE
probe_digest
probe_source_digest
mask_digest
bundle_digest
bundle_source_digest
config_digest
composite_state_digest
bundle_prestate_digest
bundle_poststate_digest
a_area_finding_digest
b_area_finding_digest
input_digest
```

Die vollstaendigen validierten `MaskedVisualProbe`- und
`TwoAreaContextBundle`-Objekte bleiben die In-Memory-Quellen. Die Eingabeform
bindet sie, ersetzt sie aber nicht durch rekonstruierte Daten.

Verbindliche Relationen:

- `invocation_id` ist ASCII und erfuellt
  `[a-z][a-z0-9-]{7,95}`;
- exakt 18 Probenpositionen mit den bestehenden neun sichtbaren und neun
  maskierten Positionen;
- Probe- und Maskendigest stimmen mit dem In-Memory-Probeobjekt ueberein;
- A- und B-Findingdigest stammen aus demselben kanonischen Bundle;
- Bundle-, Konfigurations-, Quellen- und Zustandsdigests stimmen mit dem
  In-Memory-Bundle ueberein;
- `bundle_prestate_digest == bundle_poststate_digest ==
  composite_state_digest`;
- `function_role` wird vor dem Aufruf gebunden und darf nicht aus dem Ergebnis
  abgeleitet werden;
- die Eingabe enthaelt weder Zielwerte noch Sollstatus, Fallklasse,
  `requested_area`, Gewinner oder Evaluationsdigest.

## Atomarer Einmal-Owner

Jeder einzelne Aufruf besitzt genau einen `TwoAreaConflictSignalOwner`. Es
gibt keine Unterowner fuer Probe, A, B, Vergleich oder Ergebnis.

Der unveraenderliche Owner-Vorzustand enthaelt:

```text
schema
owner_id                      ASCII [a-z][a-z0-9-]{7,95}
invocation_id
function_role                 SIGNAL | DIRECT_BASELINE
input_digest
state                         READY
owner_prestate_digest
```

Der Owner wird vor O1 unabhaengig von Probeinhalt, Statusmatrix und Ergebnis
erzeugt. Er bindet denselben Eingabedigest, der anschliessend validiert wird.

Der einzige zulaessige Uebergang lautet:

```text
READY -> CONSUMED   bei vollstaendig gueltigem atomarem Erfolg
READY -> FAILED     bei jedem Fehler
```

`CONSUMED` und `FAILED` sind terminal. Wiederverwendung, Retry, Teilverbrauch
oder ein zweiter Owneruebergang sind verboten.

Der Owner-Nachzustand enthaelt exakt:

```text
schema
owner_id
invocation_id
function_role
input_digest
prior_owner_digest
terminal_binding_digest       result_digest | error_cause_digest
state                         CONSUMED | FAILED
owner_poststate_digest
```

`owner_prestate_digest` ist kein Feld von `TwoAreaConflictSignalInput`.
Zuerst wird die ownerfreie Eingabe gebunden; danach bindet der Owner READY
deren `input_digest`. So entsteht keine zyklische Input-/Ownerbeziehung.

Signalgeber und Direktbaseline sind getrennte Aufrufe und besitzen je eine
eigene Ownerinstanz derselben Form. Kein Aufruf darf Owner, Zwischenbefund oder
Ergebnis des anderen verwenden. Innerhalb eines Aufrufs bleibt es exakt ein
Owner fuer Probe, A-/B-Befunde, Vergleich, Ergebnis und Receipt.

## A-/B-Anwendbarkeitsform

Jeder Aufruf erzeugt lokal genau zwei unveraenderliche
`AreaApplicabilityFinding`-Objekte in kanonischer Reihenfolge A, B.

Exakte Felder:

```text
schema
area                          A_RECENT | B_STABLE
status                        APPLICABLE | ABSENT_VALID | VISIBLE_CONFLICT
input_digest
probe_digest
bundle_digest
area_finding_digest
role_finding_digest
candidate_digest             digest | null
component_digest             digest | null
component_source_digest      digest | null
visible_mismatch_positions   tuple[int]
masked_positions             tuple[int]
masked_values                tuple[float]
masked_values_digest         digest | null
finding_digest
```

Invarianten:

- `APPLICABLE`: Kandidaten- und Komponentendigests vorhanden,
  `visible_mismatch_positions == ()`, exakt neun kanonische
  `masked_positions`, exakt neun `masked_values` und gueltiger
  `masked_values_digest`;
- `VISIBLE_CONFLICT`: Kandidaten- und Komponentendigests vorhanden,
  mindestens eine und hoechstens neun sichtbare Konfliktpositionen,
  `masked_positions == ()`, `masked_values == ()` und
  `masked_values_digest is null`;
- `ABSENT_VALID`: kein Kandidat und keine Komponenten- oder Wertedaten; alle
  entsprechenden Felder sind `null` beziehungsweise leere Tupel;
- A verwendet ausschliesslich `B4_RECENT` aus `A_RECENT.recent_content`;
- B verwendet ausschliesslich die stabile visuelle Komponente aus
  `B_STABLE.stable_content`;
- A-Fast, Kurzfolge und nicht visuelle B-Komponenten sind keine
  Ersatzkandidaten;
- jedes Finding bindet nur Eingabe und eigene Bereichsevidenz, niemals das
  andere Finding oder den erwarteten Endstatus.

Alle gespeicherten Maskenwerte sind exakt `float`, endlich und im bereits
gebundenen visuellen Rezeptorbereich `0.0..1.0`. Bool, String, automatische
Konvertierung und beliebige iterierbare Container sind unzulaessig.

## Vergleichsform

`MaskedSupplementComparison` enthaelt exakt:

```text
schema
input_digest
a_applicability_finding_digest
b_applicability_finding_digest
comparison_status             NOT_PERFORMED | EQUAL | DIFFERENT
a_masked_values_digest        digest | null
b_masked_values_digest        digest | null
differing_masked_positions    tuple[int]
comparison_digest
```

Invarianten:

- `NOT_PERFORMED` genau dann, wenn `K<2`; beide Wertedigestfelder und die
  Differenzpositionen sind leer;
- `EQUAL` genau bei `K=2` und identischen neun Maskenergaenzungen;
- `DIFFERENT` genau bei `K=2` und mindestens einer unterschiedlichen
  Maskenposition;
- sichtbare Werte, Zielwerte und Bereichsnamen duerfen die Gleichheitsprüfung
  nicht beeinflussen;
- A/B-Vertauschung behaelt `comparison_status` und die Menge der
  Differenzpositionen unveraendert.

## Ergebnisform

`TwoAreaConflictSignalResult` enthaelt exakt:

```text
schema
function_role
status                        einer der fuenf regulaeren Statuswerte
input_digest
probe_digest
bundle_digest
a_applicability_finding_digest
b_applicability_finding_digest
comparison_digest
present_areas                 kanonisches Tupel aus A_RECENT, B_STABLE
applicable_areas              kanonisches Tupel aus A_RECENT, B_STABLE
differing_masked_positions
selected_area                 null
recommended_area              null
automatic_selection           null
prestate_digest
poststate_digest
resource_ledger_digest
result_digest
```

`present_areas` wird ausschliesslich aus `status != ABSENT_VALID` der beiden
Anwendbarkeitsbefunde abgeleitet. `applicable_areas` wird ausschliesslich aus
`status == APPLICABLE` abgeleitet. Beide Tupel verwenden nur zur
Deterministik die Reihenfolge A, B; diese Reihenfolge ist keine Rangfolge.

Die Statusentscheidung verwendet nur die beiden Anwendbarkeitsstatus und bei
`K=2` die maskierten Ergaenzungswerte. Sie liest keine sichtbaren Werte erneut.

## Receipt- und Fehlerform

`TwoAreaConflictSignalReceipt` enthaelt exakt:

```text
schema
invocation_id
function_role
owner_prestate_digest
input_digest
a_applicability_finding_digest
b_applicability_finding_digest
comparison_digest
resource_ledger_digest
result_digest
owner_poststate_digest
receipt_digest
```

Ein Erfolgsaufruf gibt atomar genau das Tupel
`(result, receipt, owner_poststate)` frei. Vor O6 ist keines dieser Objekte
ausserhalb des Aufrufs sichtbar.

Bei Fehler entstehen kein A-/B-Teilbefund, kein Vergleich und kein
regulaeres Ergebnis ausserhalb des Aufrufs. Atomar freigegeben werden nur:

```text
TwoAreaConflictSignalErrorCause(
    invocation_id,
    function_role,
    owner_prestate_digest,
    input_digest,
    failed_operation,
    error_code,
    message_id,
    error_cause_digest
)
owner_poststate(state=FAILED)
TwoAreaConflictSignalErrorReceipt(
    invocation_id,
    function_role,
    owner_prestate_digest,
    input_digest,
    failed_operation,
    error_code,
    error_cause_digest,
    owner_poststate_digest,
    error_receipt_digest
)
```

Fehlertexte sind feste neutrale ASCII-Message-IDs. Probe-, Kandidaten- oder
Zielwerte duerfen nicht in dynamische Fehlermeldungen gelangen.

Die Fehlerregistry ist literal und vollstaendig:

| Code | Message-ID | Zulaessige Ursache |
| --- | --- | --- |
| `S2HZ-E001` | `TYPE_OR_SCHEMA_INVALID` | exakter Typ oder Schema verletzt |
| `S2HZ-E002` | `SOURCE_OR_DIGEST_INVALID` | Quelle, Relation oder Digest verletzt |
| `S2HZ-E003` | `OWNER_INVALID` | Ownerbindung, Zustand oder Einmaligkeit verletzt |
| `S2HZ-E004` | `PROBE_OR_MASK_INVALID` | Probe, Dimension oder Maskenform verletzt |
| `S2HZ-E005` | `AREA_EVIDENCE_INVALID` | Rolle, Kandidat oder Komponente verletzt |
| `S2HZ-E006` | `READ_ONLY_VIOLATION` | Vor-/Nachzustand unterscheidet sich |
| `S2HZ-E007` | `RESOURCE_BOUND_EXCEEDED` | Ledger- oder Groessengrenze verletzt |
| `S2HZ-E008` | `ATOMICITY_OR_REUSE_VIOLATION` | Teilveroeffentlichung oder Wiederverwendung erkannt |

Andere Codes und dynamische Message-IDs sind unzulaessig. Jede Fehlerform
bindet genau einen dieser Codes und genau eine der Operationen O1 bis O6.

## Sechs interne Operationen

Jeder Signal- oder Baselineaufruf besitzt exakt dieselben sechs logischen
Operationen:

| ID | Operation | Sichtbarkeit |
| --- | --- | --- |
| O1 | Eingabe, Quellen, Probe, Bundle und Owner-Vorzustand validieren | lokal |
| O2 | A-Anwendbarkeit bilden und validieren | lokal |
| O3 | B-Anwendbarkeit bilden und validieren | lokal |
| O4 | Maskenergaenzungen vergleichen und Status ableiten | lokal |
| O5 | Ledger und Ergebnis kandidatenseitig vollstaendig validieren | lokal |
| O6 | Owner terminal fortschreiben und Ergebnis plus Receipt atomar freigeben | atomar oeffentlich |

O2 und O3 sind logisch unabhaengig und duerfen keine Elternkante zueinander
besitzen. Die kanonische Ausfuehrungsreihenfolge O2 vor O3 dient nur der
Reproduzierbarkeit. Ein Fehler in O1 bis O6 fuehrt direkt zum atomaren
Fehlerabschluss; keine spaetere Erfolgsoperation ist dann zulaessig.

## Exaktes Ressourcenledger

Fuer jeden gueltigen Pfad werden vor O5 exakt folgende abgeleiteten Werte
bestimmt:

```text
P = Anzahl vorhandener Kandidaten       0..2
K = Anzahl anwendbarer Kandidaten       0..2
C = 1 bei K=2, sonst 0
```

`TwoAreaConflictSignalLedger` besitzt exakt:

```text
input_validation_count             = 1
probe_position_validation_count    = 18
bundle_validation_count            = 1
area_lookup_count                   = 2
area_finding_validation_count      = 2
candidate_reference_count          = P
component_reference_count          = P
visible_compare_count              = 9*P
masked_projection_count            = K
masked_value_reference_count       = 9*K
cross_area_compare_count           = 9*C
signal_binding_digest_validation_count = 15 + 3*P
new_digest_operation_count         = 7 + K
logical_operation_count            = 6
published_success_object_count     = 3
storage_or_learning_call_count     = 0
```

Die 15 festen Signalbindungsdigests sind die 12 Digests der ownerfreien
Eingabeform, der anschliessend gebildete Owner-Vorzustandsdigest sowie die
beiden eingebetteten Rollenfindingdigests. Je vorhandenem Kandidaten kommen
Kandidaten-, visuell verwendeter Komponenten- und Komponentenquelldigest
hinzu. Die rekursive Validierung des bereits
qualifizierten S2-GI-Bundles bleibt in dessen gebundenem Quellledger und wird
nicht als neue Signalverarbeitung doppelt gezaehlt.

Die sieben festen neuen Digests sind exakt A-Finding, B-Finding, Vergleich,
Ledger, Ergebnis, Owner-Nachzustand und Receipt. Je `APPLICABLE`-Kandidat
kommt genau ein Digest der neun Maskenwerte hinzu. Eingabe- und
Owner-Vorzustandsdigest sind bereits gebundene Quellen und werden validiert,
nicht neu erzeugt.

Damit gelten folgende maximale Erfolgswerte bei `P=2, K=2`:

```text
Kandidatenreferenzen       = 2
Komponentenreferenzen      = 2
sichtbare Vergleiche       = 18
Maskenprojektionen         = 2
Maskenwertreferenzen       = 18
bereichsuebergreifende Vergleiche = 9
Signalbindungsdigestvalidierungen = 21
neue Digestoperationen     = 9
logische Operationen       = 6
```

Ein Fehlerpfad erzeugt keine Erfolgsobjekte, besitzt
`published_success_object_count = 0` und genau drei Abschlussdigests fuer den
neutralen Fehlerursachenbeleg, den Owner-Fehlernachzustand und das
ErrorReceipt. Bereits lokal geleistete Arbeit wird im Fehlerledger bis zur
gescheiterten Operation vollstaendig ausgewiesen.

Signalgeber und Direktbaseline verwenden dieselben Formeln und Obergrenzen.
Native Laufzeit- und Speicherwerte werden spaeter getrennt berichtet und
duerfen keine funktionale Arbeit ersetzen.

## Maximale kanonische Artefaktgroessen

Alle spaeteren privaten Formen muessen ASCII-kanonisch, ohne eingebettete
Vollobjekte und unter folgenden unveraenderlichen Haltungsgrenzen bleiben:

| Form | Maximale Bytes einschliesslich Zeilenabschluss |
| --- | ---: |
| `TwoAreaConflictSignalOwner` | 768 |
| `TwoAreaConflictSignalInput` | 1792 |
| ein `AreaApplicabilityFinding` | 2048 |
| `MaskedSupplementComparison` | 1280 |
| `TwoAreaConflictSignalLedger` | 1536 |
| `TwoAreaConflictSignalResult` | 2048 |
| `TwoAreaConflictSignalReceipt` | 2048 |
| `TwoAreaConflictSignalErrorCause` | 1024 |
| `TwoAreaConflictSignalErrorReceipt` | 1536 |

Ein Receipt referenziert die anderen Formen ausschliesslich ueber typisierte
Digests; es bettet sie nicht erneut ein. Keine Form darf 4095 Byte erreichen.
Ueberschreitung wird ausschliesslich in O5 vor O6 erkannt und fuehrt
fail-closed zum Fehlerabschluss.

Die spaetere Implementierungspruefung muss jede konkrete Form gegen ihre
kanonische Vollserialisierung nachrechnen. Die hier gebundenen Grenzen duerfen
nicht nach einem Ergebnis erhoeht werden.

## Digestreihenfolge

Der vollstaendige Erfolgsgraph lautet:

```text
validierte Probe + validiertes S2-GI-Bundle
-> TwoAreaConflictSignalInput

unabhaengige Callerquelle + input_digest
-> Owner READY / owner_prestate_digest

input_digest + owner_prestate_digest + A-Quelle
-> A-ApplicabilityFinding

input_digest + owner_prestate_digest + B-Quelle
-> B-ApplicabilityFinding

A-Finding + B-Finding
-> MaskedSupplementComparison

Input + A + B + Comparison + exakte Zaehlwerte
-> Ledger

Input + A + B + Comparison + Ledger + owner_prestate_digest
-> Result

owner_prestate_digest + result_digest
-> Owner CONSUMED / owner_poststate_digest

alle vorstehenden Digests
-> Receipt
```

Der Fehlergraph zweigt an O1 bis O6 vor jeder Erfolgsveroeffentlichung ab:

```text
owner_prestate_digest + input_digest + Operation + Fehlercode
-> ErrorCause / error_cause_digest
-> Owner FAILED
-> ErrorReceipt
```

Kein Digest bindet sich selbst oder einen spaeteren Digest. A und B sind
Geschwister mit denselben Eltern. Sollstatus und Zielwerte sind keine Eltern
des Funktionsgraphen.

## Symmetrie

Bei einer vollstaendigen Vertauschung von A und B muessen gelten:

- regulaerer Status unveraendert;
- `present_areas` und `applicable_areas` nur rollenentsprechend vertauscht;
- `EQUAL`, `DIFFERENT` oder `NOT_PERFORMED` unveraendert;
- Menge der abweichenden Maskenpositionen unveraendert;
- Ressourcenledger identisch;
- kein Feld erhaelt aus der kanonischen A-vor-B-Serialisierung eine
  funktionale Prioritaet.

## Korrigierte Fallmatrix

| Fall | A | B | Status |
| --- | --- | --- | --- |
| C1 | passend X | passend X | `CONSISTENT` |
| C2 | passend X | passend Y | `CONFLICT` |
| C3 | passend X | `ABSENT_VALID` | `SINGLE_SOURCE` |
| C4 | `ABSENT_VALID` | passend X | `SINGLE_SOURCE` |
| C5 | `ABSENT_VALID` | `ABSENT_VALID` | `NO_CONTEXT` |
| C6 | passend X | `VISIBLE_CONFLICT` | `SINGLE_SOURCE` |
| C7 | `VISIBLE_CONFLICT` | passend X | `SINGLE_SOURCE` |
| C8 | `VISIBLE_CONFLICT` | `VISIBLE_CONFLICT` | `NO_APPLICABLE_CONTEXT` |
| C9 | `VISIBLE_CONFLICT` | `ABSENT_VALID` | `NO_APPLICABLE_CONTEXT` |
| C10 | `ABSENT_VALID` | `VISIBLE_CONFLICT` | `NO_APPLICABLE_CONTEXT` |

Alle zehn Faelle muessen spaeter zusaetzlich mit vertauschten A-/B-Rollen
geprueft werden. Fall-IDs und Sollstatus gehoeren ausschliesslich in einen
nachgelagerten Auswerter.

## Falsifikation und Fail-Closed

Bei gueltigen Eingaben ist die Funktion falsifiziert, wenn die fuenfteilige
Statusfunktion, A/B-Symmetrie oder Direktbaselinegleichheit verletzt wird,
eine Auswahl entsteht oder ein Zustand veraendert wird.

Methodisch ungueltig und fail-closed sind dagegen:

- fremde, fehlende oder widerspruechliche Probe-, Bundle-, A-, B-, Quellen-,
  Owner- oder Zustandsbindung;
- ungueltige Typen, Dimensionen, Rollen, Masken oder Digests;
- nicht exakt ein Owner oder Owner-Wiederverwendung;
- Teilveroeffentlichung vor O6;
- Budget- oder Groessenueberschreitung;
- Beschaedigung, die als regulaerer Status oder `ABSENT_VALID` erscheint.

Der maximal zulaessige positive Befund bleibt:

```text
S2HZ_TWO_AREA_CONFLICT_SIGNAL_VALID_DIRECT_COMPARISON_EXPLAINS
```

Er bestaetigt nur eine transparente Zustandsauskunft ueber zwei vorhandene
Kontextbereiche. Er belegt keine automatische Kontextwahl und keine neue
Memory- oder Feldmechanik.

## Freigabegrenze

S2-IB ist statisch gebunden. Als naechster Schritt ist ausschliesslich der
vollstaendige statische S2-IA-Wiederholungsaudit gegen diese Korrektur
zulaessig. Implementierung, Tests und Ausfuehrung bleiben bis zu dessen
Bestehen gesperrt.
