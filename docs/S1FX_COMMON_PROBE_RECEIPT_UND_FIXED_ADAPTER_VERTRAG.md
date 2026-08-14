# S1-FX: Common-Probe-Receipt und Fixed-Adapter-Vertrag

## Drei Probearten

S1-FX bindet ein gemeinsames Receipt fuer:

```text
P0                         6 Slots
Frozen-E1                 18 Slots
Fixed-Adapter              6 Slots
gesamt                    30 Slots
```

Der bestehende reale Probe-Wrapper deckt P0 und Frozen-E1 technisch ab. Fuer
Fixed-Adapter existiert der Feldkern, aber noch kein realer Probewrapper.

## Gemeinsames Receipt

Jedes Receipt muss Rolle, Verfeinerung, Probequelle, Anfangs- und Endfelddigest,
geordnete Neuronen-IDs, rohe Aktivierungs- und Nachhallvektoren, Schrittzahl,
Supportzahl und den verwendeten Kernel enthalten.

Die Kausalevidenz bleibt getrennt:

- P0: kein Zustand und kein Adapter;
- Frozen-E1: Quellzustand sowie Zustandsdigest vor und nach der Probe, aber
  kein Fixed-Adapter-Digest;
- Fixed-Adapter: Quellzustands- und Adapterdigest, aber keine lebende
  Zustandsrolle waehrend der Probe.

Eine Fixed-Adapter-Wirkung darf nicht als dynamische E1-Rueckwirkung berichtet
werden.

## Status

Entscheidung:
`COMMON_RECEIPT_AND_FIXED_ADAPTER_WRAPPER_BOUND_IMPLEMENTATION_MISSING`.

Der gemeinsame Receipt-Konverter und der reale Fixed-Adapter-Probewrapper sind
noch nicht implementiert. Nur eine synthetische zaehlende Implementierung ist
als naechster Schritt offen. Feldlauf, Besitzerautorisierung, Persistenz und
Claims bleiben geschlossen.

## Bester naechster Schritt

S1-FY sollte die drei Zweige mit zaehlenden Nullschritt-Adaptern in das
gemeinsame Receipt ueberfuehren. Dabei sind Nullbarkeit, rohe Vektorreihenfolge,
Schrittbilanz und atomarer Abbruch bei einem fehlerhaften Receipt zu pruefen.
Noch kein realer Probeadapter oder Feldlauf.
