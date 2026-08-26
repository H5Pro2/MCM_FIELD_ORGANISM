# S1-GA: P0/Frozen-E1-Receipt-Konverter

S1-GA implementiert den reinen Konverter fuer die beiden bereits vorhandenen
Real-Output-Zweige:

```text
Resolved Slot + Fresh Field + Real Probe Output
                         |
                         v
              gemeinsames 22-Feld-Receipt
```

Der Konverter prueft, dass Binding-Digest, Probequelle, Anfangsfeld,
Schrittzahl, Supportzahl und Frozen-State-Evidenz zu demselben gebundenen Slot
gehoeren. Rohvektoren werden unveraendert und in der Neuronenreihenfolge des
frischen Feldes uebernommen.

Die Herkunft muss ausdruecklich angegeben werden:

- `synthetic-typed-real-output` fuer konstruierte Abnahmeobjekte;
- `real-in-memory-common-probe` nur fuer einen zuvor tatsaechlich ausgefuehrten
  Wrapper-Output.

Die aktuelle Abnahme verwendet ausschliesslich die erste Herkunft. Es wurde
kein Probe- oder Feldkernel aufgerufen.

## Bester naechster Schritt

S1-GB sollte den Fixed-Adapter-Wrapper zunaechst als nicht ausfuehrenden
Implementierungsvertrag binden: Eingabetypen, Digest-Gates, Schleifenstruktur,
Ausgabeobjekt und Abbruchbedingungen. Noch keine Wrapperimplementierung und
kein Feldlauf.
