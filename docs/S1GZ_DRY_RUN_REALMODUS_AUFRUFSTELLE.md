# S1-GZ: Dry-Run-Realmodus-Aufrufstelle

S1-GZ bindet die konkrete spaetere Aufrufstelle fuer einen S1-GU-Realmoduslauf,
ohne sie freizugeben oder auszufuehren.

Gebunden ist:

- Runner: `run_e1_formation_s1gu_six_arm_counting_adapter`
- injizierter Transition-Parameter: `carrier_transition`
- Transition: `advance_e1_formation_s1gs_real_single_batch_transition`
- Quelle: typisierter S1-GY-Ausfuehrungsvertrag
- Umfang: sechs Fixed-Adapter-Arme r2/r4/r8 AB/BA
- Budget: 2.800 Transitionen, 2.800 geplante Feldschritte, 660 Supports
- erwartete atomare Ausgabe eines spaeteren Laufs: sechs terminale Carrier,
  sechs S1-GI-Ausgaben und sechs Common-Probe-Receipts

Die Dry-Run-Grenze blockiert vor jedem Runner- oder Callable-Aufruf. S1-GZ ruft
weder S1-GU noch S1-GS auf und beruehrt keinen Mapper, Projektor, Feldkernel,
Writer oder Persistenzpfad.

Geschlossen bleiben:

- Besitzerautorisierung
- reale Feldexecution
- Retry und Parameterkorrektur nach Start
- Teilrueckgabe
- EC46-/Fixed-Adapter-Endentscheidung
- Claims und Memoryentscheidung

Entscheidung:
`DRY_RUN_REAL_MODE_CALL_SITE_BOUND_BEFORE_CALLABLE_EXECUTION`.

Der naechste sinnvolle Schritt ist S1-HA: eine finale statische
Ausfuehrungsvorpruefung der gebundenen Aufrufstelle und Quellen, weiterhin ohne
Besitzerautorisierung und ohne Realmoduslauf.
