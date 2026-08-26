# S1-XI: Privater Vollform-Runner, Receipts und Aggregator

## Auftrag und Grenze

S1-XI implementiert die drei in S1-XH abgegrenzten privaten Bausteine:

1. einen Vollform-Runnerkern fuer geordnete Zellplaene;
2. ein Zellreceipt mit allen 19 S1-XE-Rollen einschliesslich
   `CELL_PLAN_DIGEST`;
3. ein Matrixreceipt mit allen 15 S1-XE-Rollen und einer atomaren
   Baselineaggregation.

Die registrierte 60-Zellen-Ausfuehrung bleibt hart gesperrt. Abgenommen wird
ausschliesslich ein Satz aus 24 synthetischen `s1xi-sub`-Ersatzplaenen.

## Harte Ausfuehrungssperre

Der private Einstieg `run_s1xi_registered_matrix` prueft zuerst:

```text
S1XI_REGISTERED_EXECUTION_ENABLED = False
```

Bei `False` stoppt er mit `S1XI_REGISTERED_EXECUTION_LOCKED`. Dieser Stopp
liegt vor Materialisierung, Bildung, Probe und Zellverarbeitung. Eine
Implementierung ist damit nicht zugleich eine Ausfuehrungsfreigabe.

## Wiederverwendete Bildung

Der Ersatzpfad verwendet den abgenommenen S1-XF-Bildungshelfer. Pro Lauf
werden daher zuerst zwei leere PPB-1-Zustaende und sechs echte
Bildungsschritte ausgefuehrt. Beide Endzustaende muessen vollstaendig den
S1-XC-Vorlagen entsprechen, bevor ein Ersatzplan ausgefuehrt wird.

## Ersatzplanabnahme

Die Abnahme verwendet zwei Modalitaeten, sechs Systeme und zwei Probearten:

```text
2 x 6 x 2 = 24 s1xi-sub-Zellen
```

Alle 24 Zellreceipts besitzen eindeutige Plan- und Receiptdigests, erfuellen
ihre gebundene Erwartung und erhalten Vorzustand sowie Identitaetsrollen.
Keine Zell-ID beginnt mit `s1xa.`.

Die reine Baselineaggregation vergleicht fuer jedes System denselben
vollstaendigen Schluesselsatz aus Modalitaet und Probe. Im Ersatzpfad gilt:

```text
no-memory:           false
replay:              true
static-prototype:    true
moving-state:        true
last-vector-distance:true
```

Diese Werte pruefen die Aggregatorform. Sie sind keine registrierte
Baselineentscheidung.

## Entscheidungsgrenze

Das 15-Rollen-Ersatzreceipt bindet ausdruecklich:

```text
technical_function_decision:    null
baseline_explanation_decision:  null
final_decision: SUBSTITUTE_RUNNER_AND_AGGREGATOR_VALID_NO_REGISTERED_DECISION
```

Eine Ersatzregistry darf nicht den S1-XC-Registrydigest tragen. Ein
registriertes Receipt verlangt dagegen exakt 60 Zellreceipts, den
S1-XC-Registrydigest und eine widerspruchsfreie Entscheidungsreihenfolge.

## Technische Digests

```text
Ersatz-Matrixreceipt: c4c937eb4b80455796ef2fe5bbb68295fdc0d7784f67130938734a27c20b88cb
Modulquellhash:       edd81cfb9fa0207d8771a50727cd139092bdb8e089442ab2a430f629043c045d
```

`12 von 12` S1-XI-Abnahmetests bestehen. Der Befund bestaetigt nur
Vollform-Runnerkern, Planbindung, Receiptanatomie, Aggregatorform und harte
Sperre. Er ist kein Ergebnis der registrierten technischen
Memory-Funktionspruefung und kein MCM-spezifischer Memory-Befund.

## Naechster Schritt

S1-XJ ist als statischer Quell-, Sperr-, Receipt-, Aggregator- und
Nichtausfuehrungsaudit vorgesehen. Er darf S1-XI nicht importieren oder
ausfuehren. Die registrierte Matrix bleibt bis nach diesem Audit und einer
gesonderten ausdruecklichen Ausfuehrungsfreigabe gesperrt.

## Grundlagen

- [S1-XH Delta-Preflight](S1XH_PPB1_STATISCHER_REGISTERED_MATRIX_IMPLEMENTIERUNGSDELTA_UND_AUSFUEHRUNGSPREFLIGHT.md)
