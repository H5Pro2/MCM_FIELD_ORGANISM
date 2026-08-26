# S1-FY: Synthetische Common-Probe-Receipts

S1-FY setzt den S1-FX-Vertrag ohne Feldlauf um. Drei getrennte zaehlende
Adapter erzeugen atomar 30 typisierte Nullschritt-Receipts:

```text
P0                6 Receipts   kein Zustand, kein Adapter
Frozen-E1        18 Receipts   Zustand vor/nach identisch
Fixed-Adapter     6 Receipts   Quellzustand + Adapter getrennt
```

Alle Receipts verwenden denselben attestierten Anfangsfelddigest und die
unveraenderten Rohvektoren seiner Neuronenschicht. Anfangs- und Endfelddigest
sind identisch, die Schritt- und Supportzahlen sind null. Sie sind daher keine
Probemessungen und enthalten keine Forschungsentscheidung.

Der Koordinator gibt nur dann ein Ergebnis zurueck, wenn alle 30 Slots
vollstaendig, eindeutig, geordnet und kausal korrekt belegt sind. Ein falscher
Adapter oder ein ungueltiges Receipt bricht vor der Ergebnisbildung ab.

Entscheidung:
`SYNTHETIC_COMMON_RECEIPTS_COMPLETE_REAL_PROBE_CLOSED`.

## Bester naechster Schritt

S1-FZ sollte statisch pruefen, welche vorhandenen realen P0-/Frozen-E1-Ausgaben
verlustfrei in das gemeinsame Receipt konvertiert werden koennen und welche
Felder der neue Fixed-Adapter-Probewrapper liefern muss. Noch keine
Implementierung des Realwrappers und kein Feldlauf.
