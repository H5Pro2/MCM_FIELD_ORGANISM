# S1-GD: Fixed-Adapter-Aufrufbindung

S1-GD verbindet die sechs S1-GC-Probekontexte atomar mit den sechs
Fixed-Adapter-Handoffs aus S1-FW.

Jede vorbereitete Aufrufgruppe enthaelt:

```text
exaktes Fixed-Slot-Binding
+ exakte Probe-Sequenzen und passender Plan
+ exaktes Quellzustandsobjekt zur Attestierung
+ exaktes Fixed-Adapter-Objekt
+ alle zugehoerigen Digests
```

Gleiche Werte oder Digests mit unterschiedlichen Binding-Objekten reichen
nicht aus. Kontext und Handoff muessen dasselbe Binding-Objekt teilen. Ebenso
werden Zustand und Adapter ohne Kopie aus dem S1-FW-Handoff uebernommen.

Entscheidung:
`SIX_FIXED_ADAPTER_INVOCATIONS_ATOMICALLY_BOUND_WRAPPER_CLOSED`.

Es wurde kein frisches Feld gebaut, kein Wrapper aufgerufen und kein Feldschritt
ausgefuehrt.

## Bester naechster Schritt

S1-GE sollte den Fixed-Adapter-Wrapper als private Implementierung hinter einem
synthetischen Nullbatch-Gate anlegen. Zuerst sind nur Eingabevalidierung,
Nullbatch-Abbruch und typisierte leere Ausgabe zu testen; noch kein positiver
Probeplan und kein Feldlauf.
