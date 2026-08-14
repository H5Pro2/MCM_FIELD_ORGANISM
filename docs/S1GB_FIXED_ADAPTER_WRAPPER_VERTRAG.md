# S1-GB: Fixed-Adapter-Wrapper-Vertrag

## Erkannte Eingabegrenze

Der neue 10-Rollen-Pfad besitzt bereits:

- sechs Fixed-Adapter-Slots;
- die exakten Quellzustandsobjekte;
- sechs daraus gebildete Fixed-Adapter-Objekte;
- einen gebundenen gemeinsamen Probequellen-Digest.

Es fehlen im 10-Rollen-Pfad jedoch noch die exakten typisierten
Probe-Sequenzen und Probeplaene. Der alte `Resolved Slot` gehoert zur frueheren
8-Rollen-/Kontaktachsen-Matrix und darf nicht als Ersatz fuer die neue
Slotbindung verwendet werden.

## Wrappergrenze

S1-GB bindet fuer den spaeteren Wrapper:

```text
neuer Fixed-Slot + exakte Probe-Sequenzen + exakter Probeplan
                  + frisches Feld
                  + Quellzustand nur zur Attestierung
                  + Fixed Adapter
                              |
                              v
                  Fixed-Adapter-Feldkern
                              |
                              v
                  typisierte Rohvektor-Ausgabe
```

Das Quellzustandsobjekt darf niemals an den Feldkern gehen. Zustand und Adapter
muessen vor und nach dem Wrapper digestgleich bleiben. Bei jeder unvollstaendigen
oder widerspruechlichen Eingabe erfolgt kein Teilergebnis.

Entscheidung:
`FIXED_ADAPTER_WRAPPER_BOUND_PROBE_CONTEXT_OBJECT_BRIDGE_MISSING`.

## Bester naechster Schritt

S1-GC sollte ausschließlich das neue typisierte 10-Rollen-Probekontextobjekt
implementieren und die bestehenden festen Probe-Sequenzen sowie Plaene gegen
den S1-FP-Digest binden. Noch kein Fixed-Adapter-Wrapper und kein Feldlauf.
