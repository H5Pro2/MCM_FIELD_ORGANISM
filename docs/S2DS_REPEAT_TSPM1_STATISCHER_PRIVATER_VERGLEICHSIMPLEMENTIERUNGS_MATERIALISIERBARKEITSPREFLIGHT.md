# S2-DS Wiederholung: Statischer TSPM-1-Vergleichspreflight

## Auftrag und Grenze

Der S2-DS-Wiederholungs-Preflight prueft ausschliesslich statisch, ob die
sechs S2-DT-Korrekturen vollstaendig und widerspruchsfrei materialisierbar
sind.

Es wurden keine Projektmodule importiert, keine Zustands-, Probe-, Test- oder
Vergleichsfunktion aufgerufen, keine Tests ausgefuehrt und keine
Implementierungsdatei geaendert. Alle 56 Vergleichszellen bleiben gesperrt.

Gebundener S2-DT-Artefaktdigest:
`7b38682c9de21ba02076c4c563280876cb725f11c9cd439d7aa91369f13d8bd1`.

## Bestandene Korrekturbereiche

### Datentraeger und Digests

Die acht Vergleichsdatentraeger besitzen geordnete Feldlisten, eine
einheitliche kanonische SHA-256-Regel, eindeutige Eigendigestfelder und
gebundene Erfolgsrelationen. Budgetzaehler und Restbudgets sind als geordnete
Aufruftupel festgelegt. Dieser Bereich ist materialisierbar.

### Modulsignaturen und Initialzustaende

Sechs Modulfunktionen sowie Ownerkonstruktor, `consume_once` und Snapshot sind
gebunden. Die acht Arm-Initialformen koennen ohne Zell- oder Zustandsaufruf
aus statischen Payloads und vorhandenen TSPM-1-/PPB-1-Leerformen digestiert
werden. Eine spaetere Runtimeform muss bitgleich normalisieren. Dieser
Bereich ist bis auf die unten genannte Autorisierungsrelation
materialisierbar.

### B2, B3 und B4

Freie und belegte Formen, IDs, Dimensionen, Zeitrollen, Match-, Update-,
Ablauf-, LRU-/FIFO-, Ereignis- und Findingregeln sind eindeutig. Es bleibt
keine Wahl zwischen alternativen Baselineoperatoren. Dieser Bereich ist
materialisierbar.

### Fehlerprioritaet und Testinventar

Ownerzustaende, neun interne Fehlerklassen, aeusserer Fehlschlag und die
Prioritaet sind fest. T01 bis T51 sind lueckenlos und eindeutig gezaehlt;
T40 bis T51 bilden genau die zwoelf vorgesehenen Mutationsrollen. Die
Ausfuehrung der 56 Zellen ist weder in einer Signatur noch in einem Test
freigegeben. Einzelne Erwartungswege bleiben jedoch durch DS-RB02 und
DS-RB03 noch nicht eindeutig erreichbar.

### Kandidatenname

Alle wirksamen Rollen verwenden `TSPM-1` beziehungsweise `TSPM1`. `APM-1`
ist weder Typ, Arm, Datei, Operator, Ergebnis noch Testkandidat. Es wurde
keine neue Kandidatenrolle eingefuehrt.

## Verbleibende Materialisierungsblocker

### DS-RB01: Comparatornormalform verliert erforderliche Evidenz

Die gebundene Normalform eines Findings enthaelt nur:

```text
history_id, arm_id, checkpoint, pair_id, recognized, context_source,
slot_or_entry_id, auditory_distance, visual_distance, state_digest
```

P2 verlangt fuer TSPM-1 getrennt `fast_recognized=False` und
`slow_recognized=True`. P3 verlangt getrennte auditive und visuelle
Slow-Statusrollen sowie einen normalisierten AX-Payloaddigest zum Vergleich
von H2 und H4. Diese Werte sind in der Normalform nicht vorhanden und koennen
aus `context_source` beziehungsweise `state_digest` nicht eindeutig
rekonstruiert werden:

- `SLOW_PPB1_CONTEXT` beweist einen langsamen Treffer, sagt aber nicht, ob
  gleichzeitig auch ein Fast-Slot gepasst hat;
- ein Gesamtzustandsdigest veraendert sich durch Geschichte und Metadaten und
  ist kein Digest des ausgewaehlten Prototyppayloads;
- der vorhandene TSPM-1-Findingtyp besitzt die benoetigten Fast- und
  Slow-Rollen, S2-DT projiziert sie jedoch nicht vollstaendig weiter.

Damit sind P2 und P3 aus dem gebundenen `S2DRCellResult` nicht eindeutig
berechenbar. T35 und die spaetere Ergebnisentscheidung sind blockiert.

### DS-RB02: Autorisierungsidentitaet und T45 sind nicht exakt gekoppelt

`S2DRCellPlan` fuehrt `authorization_digest`, der Ownerkonstruktor dagegen
`authorization_id`. S2-DT gibt eine Formel fuer `authorization_id` an, bindet
aber nicht literal:

```text
owner.authorization_id == plan.authorization_digest
```

Ebenso fehlt eine eigene `owner.cell_id`-Rolle. T45 soll eine fremde Zell-ID
erst als `S2DR_FIXTURE_ARM_OR_PRESTATE_MISMATCH` erkennen. Je nach
Materialisierung kann derselbe Fall aber bereits als falscher Ownername,
Autorisierungsfehler oder Plandigestfehler an einer hoeheren Prioritaet
scheitern.

Vor Implementierung muessen Owner-Zell-ID, Plan-Autorisierungsdigest und die
exakte digestkonsistente T43-/T45-Mutationskonstruktion gebunden werden.

### DS-RB03: T49 und T50 besitzen keinen eindeutigen Ablehnungsort

Alle acht Datentraeger sollen ihre Konstruktorfelder validieren. T49 und T50
fordern dagegen, dass ein ueberzogenes Ressourcen- beziehungsweise
Operationsreceipt bis zu `validate_s2dr_cell_result` gelangt und dort mit
`S2DR_RESOURCE_OR_OPERATION_LIMIT_EXCEEDED` verworfen wird.

Nicht festgelegt ist, ob:

1. `S2DRBudgetReceipt` die Ueberschreitung bereits im Konstruktor ablehnt;
2. der Konstruktor nur Form und Eigendigest prueft und der relationale
   Validator die Grenzen prueft; oder
3. der Test eine interne Mutationsnaht verwenden darf.

Diese Varianten besitzen verschiedene Aufrufflaechen und Fehlerprioritaeten.
T49 und T50 sind deshalb trotz benannter Erwartung noch nicht eindeutig
implementierbar. Dieselbe Korrektur muss klarstellen, dass strukturelle
Konstruktorvalidierung und relationale Budgetabnahme getrennte Ebenen sind.

## Nichtzirkularitaet und bestehende Grenzen

Die Registry, H1 bis H7, die acht Arme, 18 visuellen und 26 gemeinsamen
Werte, das 269-Woerter-Ledger sowie die Operationsgrenzen bleiben
nichtzirkulaer und widerspruchsfrei. Die drei Restblocker aendern keine
Mechanik und keine Vergleichsfrage. Sie verhindern nur, dass Code und Tests
ohne weitere Entscheidung geschrieben werden koennen.

## Entscheidung

`BLOCK_TSPM1_PRIVATE_COMPARISON_IMPLEMENTATION_THREE_REPEAT_PREFLIGHT_BINDINGS_OPEN`

Der S2-DS-Wiederholungs-Preflight besteht nicht. Private Implementierung,
Testimplementierung, Testausfuehrung und alle 56 Vergleichszellen bleiben
gesperrt.

## Naechster Schritt

S2-DU darf nach separater Freigabe ausschliesslich DS-RB01 bis DS-RB03
schliessen:

- verlustfreie Comparatornormalform mit Fast-/Slow- und Prototyppayloadrollen;
- exakte Owner-Zell-/Autorisierungsrelation und erreichbare T43-/T45-Fixtures;
- eindeutige Trennung von Budgetreceipt-Konstruktion und relationaler
  Grenzvalidierung fuer T49/T50.

Danach ist S2-DS erneut rein statisch durchzufuehren. Noch keine
Implementierung oder Ausfuehrung.
