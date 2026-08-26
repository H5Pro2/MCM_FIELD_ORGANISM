# S2-DX: Statischer Implementierungs- und Testaudit

## Auftrag und Grenze

S2-DX prueft ausschliesslich statisch die in S2-DW angelegten privaten
Vergleichs- und Testdateien gegen S2-DR, S2-DT, die bestandene
S2-DS-Korrekturkette sowie S2-DW.

Gebundener Implementierungscommit:
`d6dd21fb1faec5328fd946c8c231eb8a8da40498`.

Es wurden keine Projektmodule importiert, keine Tests ausgefuehrt, keine
Zustandsfunktion aufgerufen und keine Vergleichszelle materialisiert oder
ausgefuehrt.

## Bestandene Pruefbereiche

### Zwei private Dateien und unveraenderter Bestand

Der S2-DW-Commit fuegt genau diese zwei Dateien hinzu:

- `mcm_field_organism/_tspm1_s2dr_private_comparison.py`
- `tests/test_tspm1_s2dr_private_comparison_contract.py`

PPB-1, der TSPM-1-Grundkern, die oeffentliche API, Snapshottypen,
Produktionspfad und Feldpfad wurden nicht geaendert. Das Vergleichsmodul ist
privat und nicht aus dem Paketroot exportiert.

### Gebundene Baugruppen

Die Implementierungsdatei enthaelt:

- statische 7-mal-8-Registry mit 56 unverbrauchten Zellplaenen;
- acht selbst-digestierende private Datentraeger;
- TSPM-1-, B0-, B1-, B2-, B3-, B4- und R0-Operatorrollen;
- Budgetbeleg mit den S2-DV-Grenzfeldern;
- atomaren Einzelzellen-Owner und Owner-Snapshot;
- Zellreceipt, Zellergebnisvalidator und Comparator.

Die Felder der acht Datentraeger stimmen statisch mit S2-DT und S2-DV
ueberein. Die Findingnormalform besitzt die 23 in S2-DU gebundenen Rollen.

### Testinventar und Sperrgrenze

Die Testdatei enthaelt exakt 51 einzeln benannte Definitionen `T01` bis
`T51`. `T40` bis `T51` bilden genau die zwoelf vorgesehenen
Fail-Closed-Rollen.

Es gibt keinen 56-Zellen-Runner, keinen Moduleinstieg und keinen
Matrixausfuehrungsaufruf. Die Comparatorfunktion nimmt nur extern erzeugte
Ergebnisse entgegen und fuehrt selbst keine Zelle aus. Die 56
Vergleichszellen bleiben gesperrt.

## Verbleibende Auditblocker

### DX-B01: R0 ist keine unabhaengige generische Reduktionsbaseline

S2-DR bindet R0 als generische exakte Zwei-Ebenen-Reduktion, deren Zustand
und Operator nicht von TSPM-spezifischen Typen oder Schemanamen abhaengen.
Die Implementierung speichert dagegen unmittelbar einen
`TSPM1CompositeState` in `_R0State`, initialisiert ihn mit
`initial_tspm1_composite_state`, fuehrt ihn mit `TSPM1CoordinatorOwner` fort
und liest ihn mit `probe_tspm1_read_only` aus.

Damit ist R0 nur eine TSPM-1-Huelle und keine unabhaengige generische
Gegenbaseline. Eine Gleichheit zwischen TSPM1 und R0 waere konstruktiv
eingebaut und koennte die geforderte Reduktionskontrolle nicht pruefen.

### DX-B02: Comparator und R0-Exaktheit werden nicht vertragsgemaess geprueft

`compare_s2dr_results` setzt `r0_exact_equivalence` allein aus der Gleichheit
der fuenf Praedikatsbits. S2-DQ/S2-DR verlangen jedoch eine exakte generische
R0-Projektion der positionsgleichen Fast-Slots, modalitaetsgetrennten
PPB-Zustaende, Konsolidierungsereignisse und normalisierten Findings mit
Kontext, auditivem Treffer, visuellem Treffer und Distanzpaar.

Zusaetzlich rufen T35 bis T39 und T51 nicht `compare_s2dr_results` auf. Sie
testen nur `_predicate_vector` oder `_decision_from_vectors`. Dadurch bleiben
die 56-Zell-Vollstaendigkeit, Duplikatfreiheit, R0-Projektionsidentitaet,
Receiptbindung und atomare Comparatorausgabe in genau den dafuer gebundenen
Tests ungeprueft.

### DX-B03: T44 erreicht nicht den erwarteten Autorisierungsfehler

T44 ersetzt nur `authorization_digest`, laesst aber `cell_plan_digest`
unveraendert. Der Owner prueft zuerst den Eigendigest des Plans. Die Mutation
stoppt deshalb bereits mit `S2DR_DIGEST_OR_SOURCE_MISMATCH` und kann den
erwarteten `S2DR_AUTHORIZATION_MISMATCH`-Zweig nicht erreichen.

T44 muss den mutierten Plan mit dem fremden Autorisierungsdigest kanonisch
neu digestieren, ohne dessen Autorisierungsformel zu reparieren. Dann bleibt
der Plandigest gueltig und ausschliesslich die Autorisierungsformel ist
falsch.

### DX-B04: Slow-Prototypnachweise sind nicht an die S1WU-Findings gebunden

Im TSPM-Arm werden Slow-Findingdigests aus `TSPM1ReadOnlyFinding`
uebernommen. Slot, Distanz und Prototypdigest werden danach jedoch separat
durch `_selected_ppb` aus dem Bankzustand rekonstruiert. Es wird nicht
geprueft, dass diese Rekonstruktion genau dem durch den jeweiligen
S1WU-Findingdigest gebundenen Finding entspricht.

In den beiden B1-Armen werden Slow-Status, Slot, Distanz und Prototyp
manuell bestimmt, waehrend `auditory_slow_finding_digest` und
`visual_slow_finding_digest` leer bleiben. Damit ist die in S2-DU geforderte
verlustfreie, digestgebundene Slow-Prototypevidenz nicht vollstaendig
umgesetzt.

Die Korrektur muss pro Modalitaet genau ein validiertes
`S1WUReadOnlyPerceptualFinding` verwenden, seinen Findingdigest gegen die
TSPM-Rolle pruefen und Slot, Distanz sowie `selected_prototype_digest`
ausschliesslich aus diesem Finding uebernehmen.

## Entscheidung

`BLOCK_TSPM1_PRIVATE_COMPARISON_TEST_EXECUTION_FOUR_STATIC_IMPLEMENTATION_GAPS`

S2-DX ist nicht bestanden. Die 51 Tests und alle 56 Vergleichszellen bleiben
gesperrt. Es entsteht kein Vergleichs-, Funktions- oder Memory-Befund.

## Naechster Schritt

S2-DY darf nach separater Freigabe ausschliesslich DX-B01 bis DX-B04 in den
beiden vorhandenen privaten S2-DW-Dateien korrigieren:

- R0 als typ- und schemaneutrale generische Zwei-Ebenen-Reduktion;
- exakte R0-Projektionspruefung im Comparator und echte Comparatorpfade in
  T35 bis T39 sowie T51;
- digestkonsistente T44-Mutation;
- vollstaendige S1WU-Findingbindung der Slow-Prototypnachweise.

Danach ist S2-DX erneut statisch durchzufuehren. Noch keine Test- oder
Vergleichsausfuehrung.
