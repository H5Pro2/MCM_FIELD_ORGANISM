# S1-EC28: Synthetische reale Formation-Consumer-Abnahme

## Status

```text
SMALL_N2_R2_FIXTURE_EXECUTED
THREE_COPIED_INPUT_ARMS_COMPLETE
FORMATION_ABLATION_NEUTRAL
INPUTS_AND_EC27_PLANS_PRESERVED
TYPED_STATE_ROUNDTRIP_EXACT
FAILURE_PATH_ATOMIC
NO_CANONICAL_RUN
NO_RESULT_DECISION_OR_CLAIM
```

S1-EC28 nimmt den kleinsten realen Formation-Consumer auf dem korrigierten
EC27-n2-Paar ab. Die Fixture verwendet je Episode nur den ersten auditiven
und visuellen Abschluss, also vier Supports pro Aktivarm. Wegen der
asynchronen AV-Abschlusszeiten entstehen vier Completion-Gruppen und auf r2
acht Schritte pro Arm.

## Reale Fixture-Arme

```text
repeated_active             -> vorhandener Real-Kernelarm ab
continuous_active           -> vorhandener Real-Kernelarm ba
repeated_formation_ablated  -> vorhandener Ablationsarm
```

Alle Arme starten aus wertidentischen, tief kopierten Feld- und
E1-Zustaenden. Es gibt keine neue E1-Gleichung und keine neue
Organismusfunktion.

## Zweiter korrigierter STOPP

Die erste reale Abnahme stoppte vor der Formation, weil wiederholte Episoden
noch dieselben technischen Quellintervalle trugen. Der Completion-Planner
hatte die Organismusbelegung korrekt getrennt, aber die reale Runtime erkannte
den zweiten Kontakt zu Recht als doppelten Quellsupport.

EC27 verschiebt nun bei jedem Replay gemeinsam:

```text
technisches Quellintervall
+ Organismusintervall
+ technische Snapshot-ID
```

Trager, Werte und Intervalldauer bleiben unveraendert. Danach akzeptiert die
reale Runtime alle vier Supports jedes Aktivarms.

## Ergebnis

```text
corrected EC27 plan-set digest = b53d1e1c94dedaf4d7cd8aac250d8c81bd0ebc0b0e2ea69ecd7e0e3716b365ea
EC28 fixture result digest = 1b36c259202d8e8b27941a91ca508af181b7391afc2ca9f1b9f6e616f1fadff6
supports per active arm = 4
steps per arm = 8
formation ablation = neutral
typed state snapshot/restore = exact
```

Der technische Linf-Abstand zwischen getrenntem und kontinuierlichem
Fixture-Endzustand betraegt `2.3267539430464265e-04`. Dieser Wert ist kein
Forschungsbefund: Die Fixture enthaelt nur n2/r2, vier Supports und keine
vollstaendigen Pflichtbaselines oder Numerikverfeinerung.

Ein absichtlich fehlschlagender Kernel hinterlaesst weder Eingangsobjekte
noch EC27-Plaene veraendert und liefert keinen partiellen Ergebniscontainer.

## Evidenzgrenze

Nachgewiesen ist nur die technische Bereitschaft des realen
Formation-Consumerpfads. Nicht nachgewiesen sind wiederholungsabhaengige
Bildung, Praegung, Abschwaechung, Memory, Feldzeit, Organisation oder KI.

## Bester naechster Schritt

S1-EC29 sollte statisch die Ressourcen- und Ausfuehrungsreihenfolge fuer
eine vollstaendige, aber weiterhin nichtkanonische n1/n2-Pilotmatrix binden.
Sie muss r2/r4/r8, getrennt/kontinuierlich, P0 und Bildungsablation enthalten
und nach der Pilotmatrix jede Forschungsentscheidung gesperrt lassen. Noch
kein n4/n8-Vollversuch und kein Praegungsclaim.
