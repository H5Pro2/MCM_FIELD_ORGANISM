# S1-HB: Realer terminaler Outputabschluss

S1-HB schliesst die letzte Implementierungsluecke vor dem autorisierten
S1-GU-Sechsarmlauf. Der Builder akzeptiert ausschliesslich einen vollstaendig
abgearbeiteten realen Live-Field-Carrier. Er liest Aktivierung und Nachhall
aus dem getragenen terminalen Feld und erzeugt einen typisierten S1-GI-Output
der Art `real-in-memory-fixed-adapter-probe`.

Der Builder fuehrt selbst keinen Feldschritt aus. Er verlangt fuer jeden Arm
die exakte Batch-, Schritt- und Supportbilanz, ein vom neutralen Anfangsfeld
getrenntes terminales Feldobjekt sowie unveraenderte Quellzustands- und
Fixed-Adapter-Digests. Persistenz und Claims bleiben ausgeschlossen.

S1-GU unterscheidet nun streng zwischen 2.800 synthetischen Nullschritt-
Transitionen und 2.800 realen Einzelschritt-Transitionen. Gemischte oder
teilweise Ausfuehrung wird verworfen. Ein vollstaendiger Realmodus darf nur
die Entscheidung `SIX_ARM_REAL_FIXED_ADAPTER_PROBE_COMPLETED_ATOMICALLY`
erzeugen.

S1-HB startet den autorisierten Lauf noch nicht.
