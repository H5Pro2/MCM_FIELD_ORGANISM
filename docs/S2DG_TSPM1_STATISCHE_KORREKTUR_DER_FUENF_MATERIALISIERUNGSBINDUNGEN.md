# S2-DG: TSPM-1 Korrektur der fuenf Materialisierungsbindungen

## Auftrag und Vorrang

S2-DG ergaenzt den S2-DE-Vertrag ausschliesslich statisch. Bei einer
Abweichung hat diese Korrektur fuer Typen, Signaturen, Zustandsformen,
Receipts, Quellenidentitaet und Fehlerreihenfolge Vorrang.

Es wurden keine Projektmodule importiert, keine Zustands- oder Probefunktion
aufgerufen, keine Tests ausgefuehrt und keine Implementierung geaendert.
Private Implementierung, Replay, API, Snapshot und Feldpfad bleiben gesperrt.

## K1: Vollstaendige private Typenanatomie

Die spaetere private Implementierung darf genau diese dreizehn Typen enthalten:

1. `TSPM1FastConfig`
2. `TSPM1ConfigBinding`
3. `TSPM1BoundExposure`
4. `TSPM1BoundProbe`
5. `TSPM1FastSlot`
6. `TSPM1FastState`
7. `TSPM1FastTransitionCandidate`
8. `TSPM1CompositeState`
9. `TSPM1TransitionReceipt`
10. `TSPM1StepResult`
11. `TSPM1ReadOnlyFinding`
12. `TSPM1CoordinatorOwnerSnapshot`
13. `TSPM1CoordinatorOwner`

Alle Datentraeger ausser dem zustandsbehafteten Owner sind eingefrorene
Dataclasses mit Slots. Jeder digesttragende Typ besitzt
`payload_without_digest()`, `canonical_payload()` und eine kanonische
SHA-256-Bindung ueber ASCII-JSON mit sortierten Schluesseln, kompakten
Separatoren und verbotenen NaN-Werten.

## K2: Gemeinsame Konfigurationsbindung

`TSPM1FastConfig` enthaelt exakt:

- `fast_bank_id`;
- `capacity`;
- `auditory_match_threshold`;
- `visual_match_threshold`;
- `update_factor`;
- `consolidate_after`;
- `expire_after_exposures`;
- `schema_version`.

Die Werte folgen den S2-DE-Grenzen. Der Konfigurationsdigest umfasst alle
diese Felder.

`TSPM1ConfigBinding` enthaelt exakt:

- ein `TSPM1FastConfig`-Objekt;
- ein exaktes `PPB1ReceptorProfileBinding`-Objekt;
- S2-DE- und S2-DG-Vertragsdigest;
- Fast-, Profil-, auditive PPB-1- und visuelle PPB-1-Konfigurationsdigests;
- `config_binding_digest`.

Das Profil muss genau eine auditive und eine visuelle `PPB1BankConfig`
tragen. Deren Modalitaet, Geometrie und Traegerinventare sind die einzige
Dimensionsquelle fuer Fast-Slots, Expositionen und Proben. Redundante Digests
muessen den eingebetteten Objekten entsprechen. Ein Austausch nur einer
PPB-1-Konfiguration invalidiert die gesamte Bindung.

## K3: Expositions- und Probehuellen

### TSPM1BoundExposure

Die Bildungshuelle enthaelt exakt:

- `config_binding_digest`;
- das exakte `PPB1ActiveReceptorBatchEnvelope`-Objekt;
- genau ein auditives und ein visuelles
  `PPB1ActiveReceptorTimedFrameBinding`-Objekt;
- Envelope-, Quellbatch-, Profil- und beide Timed-Frame-Digests;
- beide PPB-1-Eingabeprojektionsdigests;
- gemeinsame Feldclock sowie Schnittfensterstart und -ende;
- `exposure_digest`.

Jedes Timed-Frame-Binding muss per Objektidentitaet genau einmal im passenden
Stream des eingebetteten Envelopes vorkommen. Das im Binding enthaltene
`timed_frame.frame`-Objekt ist die einzige Originalframequelle. Die
Feldclock muss in beiden Bindings gleich sein und

```text
overlap_start = max(auditory_field_start, visual_field_start)
overlap_end   = min(auditory_field_end, visual_field_end)
overlap_start < overlap_end
```

gelten. Der Expositionsdigest wird nur aus Konfigurations-, Envelope-,
Timed-Frame-, Eingabeprojektions- und Schnittfensterrollen berechnet. Es gibt
keine extern uebergebene Expositions-ID.

### TSPM1BoundProbe

Die Probehuille besitzt dieselben Quell- und Identitaetsfelder, aber einen
eigenen `probe_digest` und einen anderen Schematyp. Sie wird niemals in einen
Bildungsaufruf akzeptiert; eine Expositionshuelle wird niemals als Probe
akzeptiert. Die kausale Spaetergrenze wird gegen alle drei Bankzustaende erst
im read-only Abruf geprueft.

Die beiden S1-WU-IDs werden ohne externe Eingabe berechnet:

```text
tspm1.probe.auditory.<probe_digest>
tspm1.probe.visual.<probe_digest>
```

Sie tragen keine Auswahl- oder Ergebnisinformation.

## K4: Exakte Slot- und Zustandsformen

### Freier Slot

Ein freier `TSPM1FastSlot` hat zwingend:

```text
occupied = false
auditory_values = ()
visual_values = ()
support_count = None
last_selected_step = None
consolidation_count = 0
last_consolidation_exposure_digest = None
```

### Belegter Slot

Ein belegter Slot hat nichtleere, dimensionsrichtige Werte in `[-1, 1]`,
Support in `1..consolidate_after`, einen letzten Auswahlschritt in
`1..accepted_exposure_count` und eine nichtnegative Konsolidierungszahl
hoechstens gleich der akzeptierten Expositionszahl.

Bei Konsolidierungszahl `0` ist der letzte Konsolidierungsexpositionsdigest
`None`. Bei positiver Zahl ist er ein gueltiger Digest. Erzeugung und Ersatz
setzen Support auf `1`, Konsolidierungszahl auf `0` und den Digest auf
`None`. Nicht bereites Match erhoeht nur Support und Auswahlzeit. Commit
erhoeht die Konsolidierungszahl genau um eins und bindet den aktuellen
Expositionsdigest. Ablauf setzt den vollstaendigen freien Zustand wieder her.

### Fast- und Composite-Zustand

`TSPM1FastState` enthaelt Fast-Bank- und Konfigurationsdigest,
`accepted_exposure_count`, beide Quellclock-IDs, beide letzten
Quellfensterendticks, die feste Slotmenge und `fast_state_digest`.
Initial sind Zaehler `0`, Clock- und Tickrollen `None` und alle Slots frei.
Nach dem ersten Schritt sind beide Clock- und Tickrollen vollstaendig.

`TSPM1CompositeState` enthaelt Architektur-ID,
`config_binding_digest`, `generation`, `parent_composite_state_digest`,
`last_exposure_digest`, Fast-Zustand, auditive PPB-1-Bank, visuelle PPB-1-
Bank und `composite_state_digest`.

Der Initialzustand hat Generation `0`, keine Parent- oder Expositionsrolle
und exakt drei frische Bankzustaende. Ein Nachzustand hat Generation
`pre.generation + 1`, den Digest des exakten Vorzustands als Parent und den
aktuellen Expositionsdigest. Alle Folgezustaende entstehen ausschliesslich
aus einem erfolgreichen Owner-Commit.

## K5: Eindeutiges Receiptmodell

`TSPM1FastTransitionCandidate` enthaelt den lokalen Fast-Nachzustand, genau
ein Primaerereignis, das Konfliktflag, geordnete Ablaufslotdigests, den
optionalen Ersatzslotdigest, ausgewaehlte Slot-ID und beide optionalen
Matchdistanzen, Konsolidierungsberechtigung und `candidate_digest`. Er ist
noch kein veroeffentlichtes Ergebnis und enthaelt keinen PPB-1-Nachzustand.

`TSPM1TransitionReceipt` trennt orthogonal:

- `primary_event`: genau eines aus `FAST_CREATED`, `FAST_UPDATED`,
  `FAST_REPLACED`;
- `partial_association_conflict`: Boolean, nur ohne gemeinsamen Match;
- `expired_slot_digests`: nach Slot-ID geordnetes, gegebenenfalls leeres
  Tupel;
- `replaced_slot_digest`: nur bei `FAST_REPLACED`, sonst `None`;
- `consolidation_status`: `NOT_ELIGIBLE` oder `COMMITTED`;
- auditive und visuelle PPB-Readoutdigests: genau bei `COMMITTED`, sonst
  beide `None`;
- getrennte auditive und visuelle `stabilized`-Booleans: genau bei
  `COMMITTED`, sonst beide `None`;
- alle Quellen-, Konfigurations-, Fast-, Composite-, Owner- und
  Entscheidungsdigests, wobei nur der Owner-Autorisierungsvorzustandsdigest
  im Receipt liegt;
- `receipt_digest`.

Abgelaufene Slots sind Nebenwirkungen der Vorbereinigung und niemals ein
Primaerereignis. Ein Teilassoziationskonflikt ist ein Flag und niemals ein
zweites Primaerereignis. Scheitert ein berechtigter PPB-Schritt, entsteht
kein Receipt und kein Nachzustand; deshalb gibt es keinen
`CONSOLIDATION_FAILED`-Receiptstatus.

Der Konsolidierungsentscheidungsdigest bindet mindestens
Konfigurationsdigest, Composite-Vorzustandsdigest, lokalen Fast-
Kandidatenzustandsdigest, Expositionsdigest, Berechtigung, beide
Originalinputdigests und bei Commit beide PPB-Readoutdigests.

`TSPM1StepResult` enthaelt Composite-Nachzustand, Receipt, terminalen Owner-
Snapshot und `result_digest`. Zur Vermeidung einer Digestzirkularitaet wird
der Resultdigest ueber die Owner-Nachzustandsprojektion ohne
`committed_result_digest` berechnet. Danach muss der vollstaendige Owner-
Snapshot `committed_result_digest == result_digest` binden. Das Receipt
enthaelt keinen Owner-Nachzustandsdigest.

## K6: Owner, Signaturen und Fehlerreihenfolge

### Ownerbindung

`TSPM1CoordinatorOwner` wird fuer genau einen Versuch konstruiert mit:

- `owner_id`, `authorization_id`, `consumption_id`;
- autorisiertem TSPM-1-Konfigurationsdigest;
- autorisiertem Composite-Vorzustandsdigest;
- autorisiertem Expositionsdigest.

`TSPM1CoordinatorOwnerSnapshot` bindet diese Rollen sowie Status,
Versuchs-, Nutzungs- und Generationszaehler, committed Resultdigest oder
Fehlercode und Fehlerdigest. Gueltige stabile Formen sind:

```text
AUTHORIZED: attempt=0, use=0, generation=0, kein Ergebnis, kein Fehler
CONSUMED:   attempt=1, use=1, generation=1, Ergebnisdigest, kein Fehler
FAILED:     attempt=1, use=0, generation=1, kein Ergebnis, Fehler gebunden
```

Der Owner verwendet einen nicht wiedereintretenden Lock. Lockfehler erzeugt
`TSPM1_OWNER_BUSY` ohne Statusaenderung. Nach Lockgewinn wird zuerst der
terminale Status geprueft. Danach wird der Owner intern `IN_PROGRESS` und
`attempt=1`; jeder folgende Fehler, einschliesslich Preflight, endet terminal
`FAILED`. Ein zweiter Aufruf endet `TSPM1_OWNER_TERMINAL`.

### Gebundene spaetere Signaturen

```text
bind_tspm1_exposure(
    config: TSPM1ConfigBinding,
    envelope: PPB1ActiveReceptorBatchEnvelope,
    auditory: PPB1ActiveReceptorTimedFrameBinding,
    visual: PPB1ActiveReceptorTimedFrameBinding,
) -> TSPM1BoundExposure

bind_tspm1_probe(
    config: TSPM1ConfigBinding,
    envelope: PPB1ActiveReceptorBatchEnvelope,
    auditory: PPB1ActiveReceptorTimedFrameBinding,
    visual: PPB1ActiveReceptorTimedFrameBinding,
) -> TSPM1BoundProbe

initial_tspm1_composite_state(
    config: TSPM1ConfigBinding,
) -> TSPM1CompositeState

advance_tspm1_fast(
    config: TSPM1ConfigBinding,
    prestate: TSPM1FastState,
    exposure: TSPM1BoundExposure,
) -> TSPM1FastTransitionCandidate

TSPM1CoordinatorOwner.consume_once(
    config: TSPM1ConfigBinding,
    prestate: TSPM1CompositeState,
    exposure: TSPM1BoundExposure,
) -> TSPM1StepResult

probe_tspm1_read_only(
    config: TSPM1ConfigBinding,
    state: TSPM1CompositeState,
    probe: TSPM1BoundProbe,
) -> TSPM1ReadOnlyFinding
```

Der lokale Fast-Kandidat ist ein privater Datentraeger, darf aber die
Ownergrenze nicht als eigenstaendiges Ergebnis verlassen.

Die Fehlerprioritaet lautet:

1. `TSPM1_OWNER_BUSY`;
2. `TSPM1_OWNER_TERMINAL`;
3. `TSPM1_INVALID_TYPE_OR_SCHEMA`;
4. `TSPM1_CONFIG_OR_CONTRACT_MISMATCH`;
5. `TSPM1_OWNER_AUTHORIZATION_MISMATCH`;
6. `TSPM1_COMPOSITE_OR_FAST_STATE_INVALID`;
7. `TSPM1_SOURCE_PROVENANCE_MISMATCH`;
8. `TSPM1_MODALITY_GEOMETRY_OR_CARRIER_MISMATCH`;
9. `TSPM1_CLOCK_ORDER_OR_FIELD_OVERLAP_INVALID`;
10. `TSPM1_ATOMIC_RESULT_REQUIRED`;
11. aeusserer Abschluss `TSPM1_ATTEMPT_FAILED` mit gebundenem inneren Code.

Read-only Fehler verwenden dieselbe fachliche Reihenfolge ohne Ownerrollen
und enden mit `TSPM1_READ_ONLY_REJECTED`.

## K7: Direkte Originalobjekt- und Atomaritaetsbindung

Der Koordinator muss vor jedem PPB-1-Aufruf per Objektidentitaet pruefen:

```text
exposure.auditory is genau ein Objekt im auditiven Envelope-Stream
exposure.visual   is genau ein Objekt im visuellen Envelope-Stream
```

Die Aufrufargumente sind danach ohne Kopie exakt:

```text
exposure.auditory.timed_frame.frame
exposure.visual.timed_frame.frame
```

Ein spaeterer statischer AST-Test muss genau diese beiden direkten
Quellketten und insgesamt hoechstens zwei `advance_ppb1_bank`-Aufrufe im
Koordinator nachweisen. Kein Konstruktor fuer `ReceptorContactFrame` und
keine Schleife ueber Fast-Slots darf im Konsolidierungsblock vorkommen.

Der lokale Fast-Kandidat, beide lokalen PPB-1-Ergebnisse, das Receipt und der
Composite-Nachzustand werden vollstaendig validiert, bevor der Owner auf
`CONSUMED` wechselt. Bei jeder Ausnahme bleibt kein Ergebnis erreichbar und
der Owner wird `FAILED`.

## K8: Eindeutiger read-only Befund

`TSPM1ReadOnlyFinding` enthaelt Probe-, Konfigurations- und beobachteten
Composite-Digest, Fast-Erkennung, Fast-Slotdigest und beide Fast-Distanzen,
je Modalitaet `SLOW_UNAVAILABLE`, `SLOW_NOT_RECOGNIZED` oder
`SLOW_RECOGNIZED`, optionale S1-WU-Findingdigests, genau eine Kontextquelle
und `finding_digest`.

Ein frischer PPB-Zustand erzeugt `SLOW_UNAVAILABLE` ohne S1-WU-Aufruf. Ein
nicht frischer Zustand erzeugt genau einen S1-WU-Aufruf mit der aus dem
Probe-Digest abgeleiteten Modalitaets-ID. Vor und nach allen Distanzen und
S1-WU-Aufrufen muessen Fast-, auditive PPB-1- und visuelle PPB-1-
Zustandsdigests identisch sein.

Sind im Composite-Zustand Quellclocks vorhanden, muessen die zwei Probeclocks
modalitaetsspezifisch uebereinstimmen und beide Probe-Endticks groesser als
die jeweiligen Fast- und PPB-1-Endticks sein. Im vollstaendig frischen
Initialzustand sind Fast und beide Slow-Befunde leer beziehungsweise
`SLOW_UNAVAILABLE`; die gueltige Probe liefert zwingend
`NO_COMPLETE_CONTEXT`.

Die Kontextprioritaet aus S2-DE bleibt unveraendert. Ein einzelner positiver
PPB-Befund wird berichtet, erzeugt aber `NO_COMPLETE_CONTEXT`.

## Blockerschluss und naechster Schritt

Die fuenf S2-DF-Blocker sind auf Vertragsniveau geschlossen:

`PASS_TSPM1_FIVE_STATIC_MATERIALIZATION_BINDINGS_CORRECTED_PENDING_REPEAT_S2DF`

Dies ist noch keine Implementierungsfreigabe. Der naechste Schritt ist die
erneute rein statische Durchfuehrung von S2-DF gegen S2-DE plus S2-DG. Erst
ein bestandener Wiederholungsaudit darf den privaten Fast-Kern und seine
synthetischen Vertragstests freigeben.
