# S1-FZ: Statische Real-Receipt-Grenze

## Ergebnis der Schnittstellenpruefung

Die vorhandenen P0- und Frozen-E1-Ausgaben lassen sich verlustfrei in das
gemeinsame Receipt ueberfuehren, wenn drei bereits gebundene Objekte gemeinsam
an den Konverter gehen:

```text
Resolved Slot     -> Rolle, Verfeinerung, Modus, Probequelle
Fresh Field       -> Anfangsfelddigest, geordnete Neuronen-IDs
Real Probe Output -> Endfelddigest, Rohvektoren, Schritte, Supports,
                     Frozen-State-Evidenz
```

Der vorhandene P0/Frozen-E1-Wrapper muss dafuer nicht geaendert werden. Es
fehlt nur der typisierte Konverter, der die drei Quellen gegen denselben
Binding-Digest prueft und daraus das gemeinsame Receipt bildet.

## Fixed-Adapter-Grenze

Der Fixed-Adapter-Feldkern ist vorhanden. Es fehlt ein realer Wrapper mit
eigener Ausgabegrenze. Er muss insbesondere getrennt attestieren:

- Quellzustandsdigest;
- Fixed-Adapter-Digest;
- unveraenderte Quellzustands- und Adapterdigests;
- frisches Anfangsfeld und geordnete Rohvektoren;
- exakte Schritte und Supports;
- keine Persistenz und keine Claims.

Das lebende E1-Zustandsobjekt darf nicht an den Fixed-Adapter-Feldkern gegeben
werden. Die Wirkung des eingefrorenen Adapters darf nicht als dynamische
E1-Rueckwirkung bezeichnet werden.

Entscheidung:
`EXISTING_BRANCHES_CONVERTIBLE_FIXED_WRAPPER_CONTRACT_MISSING`.

## Bester naechster Schritt

S1-GA sollte den reinen P0/Frozen-E1-Receipt-Konverter implementieren und mit
synthetisch konstruierten typisierten Real-Outputs abnehmen. Der
Fixed-Adapter-Realwrapper und jeder Feldlauf bleiben dabei geschlossen.
