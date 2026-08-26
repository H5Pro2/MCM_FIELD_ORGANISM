# S1-AK: Passiver `C_i`-Substratpfad ueber synthetische AV-Testwelten

Stand: 2026-08-11

Status: `TECHNISCHER_PASSIVER_SUBSTRATBEFUND_KEINE_RUECKWIRKUNG`

## Umfang

Die gebundene synthetische Weltfamilie
`controlled_history_holdout_world_family()` wurde phasenweise durch den
isolierten `C_i`-Baselinepfad gefuehrt:

```text
contact.0 -> gap.0 -> contact.1 -> probe.0
```

Als technische Feldteilnahme `E_i` wurden ausschliesslich die Aktivierungen
der erzeugten Feldsnapshots verwendet. Die `C_i`-Disposition startete in
beiden Welten identisch bei null.

Konfiguration:

```text
alpha = 0.5
beta  = 1.0
dt    = 0.1
```

## Ergebnis

```text
world.history.same
ci_digest = 1fc523b07d89115a93b95c7fece169870061c94c996679ee5a5496334bc26c9e
min(C_i) = 0.004055861866867495
max(C_i) = 0.028337044952538522

world.history.changed
ci_digest = 53e07df4be07dd9ea7c6b1409df39e20769f49c6723444796031a4ae8b4c82e9
min(C_i) = 0.0037549618768521215
max(C_i) = 0.027445316585201402

history_ci_linf = 0.010146198428510209
history_ci_digest_equal = false
```

## Einordnung

Der passive Pfad zeigt, dass die gebundene `C_i`-Baseline unterschiedliche
technische Dispositionszustaende aus unterschiedlichen synthetischen
Feldvorgeschichten berechnet.

Der Pfad besitzt noch keine Rueckwirkung auf `S`. Deshalb belegt er nur:

```text
Feldsnapshotfolge -> unterschiedliche C_i-Zustaende
```

Er belegt nicht:

- spaetere veraenderte Feldaufnahme;
- Memory, Lernen oder Vergessen;
- inneren Kontext, Organisation, Semantik oder KI;
- eine neue MCM-Natur.

## Aussagegrenze

Die beobachtete Differenz ist mit der gewaehlten lokalen Akkommodations-
Baseline vereinbar. Sie muss noch gegen leaky Spur, Integrator, Gain,
Hysterese und F3 in einem gemeinsamen Rueckwirkungsversuch abgegrenzt
werden.

## Bester naechster Schritt

Den konjugierten `C_i -> S`-Rueckwirkungspfad als getrennte technische
Ablation vorbereiten: Rueckwirkung aus, Rueckwirkung an, identische
synthetische Eingabe und dieselben Snapshotpunkte.
