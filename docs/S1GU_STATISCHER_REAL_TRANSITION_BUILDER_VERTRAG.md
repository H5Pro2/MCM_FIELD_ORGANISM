# S1-GU: Statischer Real-Transition-Builder-Vertrag

Stand: 2026-08-15

Status: `PROVENIENZLUECKE_GEBUNDEN_KEINE_AUSFUEHRUNG`

## Ergebnis

Der spaetere reine Real-Transition-Builder ist statisch eingegrenzt:

```text
Fresh Binding
+ exakter Batch
+ vorheriger Carrier
+ Kernelrueckgabefeld
+ typisiertes Adapteraufruf-Receipt
-> neuer Carrier
-> S1-GQ-Real-Transition
-> gemeinsamer Real-Envelope
```

Ein neues `SharedMCMField` allein ist keine ausreichende Provenienz. Es koennte
aus einer fremden, wiederholten oder manuell konstruierten Quelle stammen. Der
Builder muss deshalb zusaetzlich ein typisiertes Receipt verlangen, das
gemeinsam bindet:

- S1-GS-Gate und externe Autorisierung;
- verbrauchten Einmaltoken;
- Binding, Batch, Zeit und vorherigen Carrier;
- vorherigen und naechsten Felddigest;
- genau einen Adapteraufruf und einen Feldschritt;
- unveraenderte Quellzustands- und Fixed-Adapter-Digests.

## Geschlossene Grenze

Das benoetigte Adapteraufruf-Receipt existiert noch nicht. Deshalb sind weder
der reine Builder noch ein Realadapter freigegeben oder implementiert. S1-GU
ruft keinen Mapper, Projektor, Token oder Feldkernel auf.

Entscheidung:

```text
REAL_TRANSITION_BUILDER_BOUND_TYPED_ADAPTER_CALL_RECEIPT_REQUIRED
```

Dies ist eine technische Provenienzkorrektur, kein wissenschaftlicher STOPP
und kein Feld-, Substrat- oder Memory-Befund.

## Bester naechster Schritt

S1-GV implementiert nur das nicht ausfuehrende Schema des typisierten
Adapteraufruf-Receipts. Es erhaelt keinen Builder und keinen Kernelzugriff;
zunaechst werden nur Vollstaendigkeit, Unveraenderlichkeit und Fail-Closed-
Grenzen geprueft.
