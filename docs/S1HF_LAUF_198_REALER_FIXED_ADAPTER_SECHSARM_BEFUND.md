# S1-HF: Lauf 198 realer Fixed-Adapter-Sechsarm-Befund

Stand: 2026-08-15

Status: `SIX_ARM_REAL_FIXED_ADAPTER_PROBE_COMPLETED_ATOMICALLY`

## Laufgrenze

Der vorbereitete Projektwurzel-Modulstart wurde genau einmal ausgefuehrt.
S1-GU verarbeitete S1-GS als reale Einzelbatch-Transition und S1-HB als
terminalen Outputabschluss.

```text
Ausfuehrungsmodus:                real, in-memory, fixed-adapter
Arme:                             6 (r2/r4/r8, AB/BA)
Transitionen:                     2.800 real-field-advance
ausgefuehrte Feldschritte:        2.800
Supports:                         660
terminale Carrier:                6
S1-GI-Outputs:                    6
Common-Probe-Receipts:            6
atomare Rueckgabe:                ja
Quellzustaende erhalten:          ja
Fixed Adapter erhalten:           ja
Persistenz:                       nein
Claims oder Memoryentscheidung:   nein
Retry:                            nein
Ergebnisdigest:                   1e28219de2439e3cde5278aedb787cad1ffc2e3086b9890769ac875d7df01d91
```

## Messung

AB und BA erhielten je Verfeinerung dieselbe neutrale Probe. Sie
unterschieden sich ausschliesslich durch den aus ihrem jeweiligen E1-
Bildungszustand abgeleiteten festen Adapter.

| Verfeinerung | Schritte je Arm | Supports je Arm | Aktivierung AB/BA Linf | Nachhall AB/BA Linf |
|---|---:|---:|---:|---:|
| r2 | 200 | 110 | 3.145442008349597e-07 | 2.1826650970727807e-07 |
| r4 | 400 | 110 | 3.1155455250050923e-07 | 2.1618997246477395e-07 |
| r8 | 800 | 110 | 3.114299929989073e-07 | 2.1608402354413025e-07 |

Die Differenzen sind in allen drei Aufloesungen groesser als die bisherige
absolute Kontrollgrenze `1e-12`. Die Aenderung von r4 zu r8 ist wesentlich
kleiner als von r2 zu r4; beide Messgroessen naehern sich einem stabilen
nichtnulligen Wert.

Terminale Felddigests:

| Arm | Digest |
|---|---|
| r2 AB | `fce90431b8eec6f3e770d6ec38ec7f3572a1c1e8ecc3660d955ed82e796fce03` |
| r2 BA | `cc9ac0d12c28c4ee6edf1c8775b4d1fba2e4dbee07fe54aaa7cedab200b6200a` |
| r4 AB | `544ee6d72b00b88b290cc82234ca36e34540c740a6bc8b0612e107ad3f474235` |
| r4 BA | `15974d6081d2de8c3625c49f32508e7945037ddf578636f069c828d752b5f34a` |
| r8 AB | `e7911b5b8a4cb215fc7455b426152aedca8a14b8c2902428a12f28544acfd1fb` |
| r8 BA | `f443cd315390011ae4b63831e06ce178cc6652994d43d95e7c9c4dae9f321bae` |

## Technische Interpretation

Der aus unterschiedlichen AB/BA-E1-Endzustaenden abgeleitete feste Adapter
uebertraegt einen kleinen, aber ueber r2/r4/r8 konvergierenden Unterschied
auf die identische spaetere Feldprobe. Damit ist die reale Fixed-Adapter-
Messstrecke fuer diese sechs Arme technisch geschlossen.

Der Befund ist zugleich die erwartete Gegenbaseline: Eine spaetere aktive
E1-Wirkung muss ueber diese feste zustandsabgeleitete Adapterwirkung
hinausgehen, um eine eigenstaendige Dynamik zu zeigen.

## Nichtnachweise

Lauf 198 enthaelt keine aktive Frozen-E1-Probe, P0-Kontrolle oder Ablation.
Er vergleicht die feste Adapterwirkung nicht direkt mit einer gleichzeitig
ausgefuehrten aktiven E1-Wirkung. Nicht nachgewiesen sind daher insbesondere
Memory, Rekonstruktion, Abruf, Abschwaechung, Interferenz, innerer Kontext,
Organisation, Semantik, Selbstregulation oder KI.

## Naechster Schritt

Den Befund zunaechst statisch gegen S1-FO und die vorregistrierte gemeinsame
Probenmatrix einordnen. Erst danach ist zu entscheiden, ob die aktive
Frozen-E1-Probe noch eine unterscheidbare Gegenprognose gegen Lauf 198 besitzt
oder ob der Fixed-Adapter-Zweig die vorhandene Wirkung bereits vollstaendig
erklaert.
