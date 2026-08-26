# S1-GC: Zehn-Rollen-Probekontextbruecke

S1-GC schliesst die in S1-GB gefundene Objektluecke. Die sechs
Fixed-Adapter-Slots werden mit den exakten typisierten Probe-Sequenzen und dem
jeweils passenden r2/r4/r8-Probeplan verbunden:

```text
r2 fixed-adapter-ab/ba -> derselbe r2-Plan + dieselben Probe-Sequenzen
r4 fixed-adapter-ab/ba -> derselbe r4-Plan + dieselben Probe-Sequenzen
r8 fixed-adapter-ab/ba -> derselbe r8-Plan + dieselben Probe-Sequenzen
```

Der Probequellendigest muss dem S1-FP-Vertrag entsprechen. Sequenz- und
Planobjekte werden nicht rekonstruiert oder kopiert; ihre Objektidentitaet wird
ueber alle sechs Kontexte erhalten. Der alte 8-Rollen-`Resolved Slot` wird
nicht verwendet.

Entscheidung:
`TEN_ROLE_PROBE_CONTEXT_OBJECT_BRIDGE_COMPLETE_WRAPPER_CLOSED`.

Es wurde kein Fixed-Adapter-Wrapper oder Feldkernel aufgerufen.

## Bester naechster Schritt

S1-GD sollte die sechs S1-GC-Kontexte synthetisch mit den sechs S1-FW-Handoffs
zusammenfuehren und Binding-, Zustands-, Adapter-, Plan- und Probequellendigests
atomar pruefen. Noch kein Fixed-Adapter-Wrapper und kein Feldlauf.
