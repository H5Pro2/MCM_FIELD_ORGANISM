# S1-GG: Statische Fixed-Adapter-Realkern-Bindung

Stand: 2026-08-15

Status: `STATISCHE_SCHNITTSTELLENPRUEFUNG_KEINE_AUSFUEHRUNG`

## Ergebnis

Die kleinste reale Fixed-Adapter-Aufrufkette ist mit den vorhandenen Typen und
Signaturen kompatibel:

```text
objektgetrenntes frisches SharedMCMField
-> ReceptorProposalBatch
-> map_proposal_batch_to_transient_docks
-> project_transient_docks_to_neuron_inputs
-> leerer ReceptorDistribution-Zeittraeger
-> advance_fixed_e1_adapter_fast_shared_field_transient
-> terminaler Snapshot mit geordneten Rohvektoren
-> gemeinsames S1-FX-Receipt
```

Der Fixed-Adapter-Kern nimmt keinen lebenden E1-Zustand entgegen. Das
Quellzustandsobjekt bleibt ausschliesslich fuer die getrennte Attestierung vor
und nach dem spaeteren Wrapper gebunden.

## Gebundene Konfiguration

Die bestehende Probeimplementierung verwendet:

- `NeutralLocalFieldSubstrateConfig(1.0)`;
- `NeutralFastAfterimageConfig(0.5)`;
- keine zusaetzliche Dissipationskonfiguration;
- einen leeren `ReceptorDistribution`-Randtraeger fuer die Batch-Zeitspanne.

S1-GG aendert diese Werte nicht und fuehrt keine Nachparametrierung ein.

## Verbleibende Objektluecke

S1-GD traegt bereits den exakten Probekontext, den Quellzustand zur
Attestierung und den Fixed Adapter. Das neutrale Anfangsfeld existiert in den
S1-FI-Eingaben, wird aber nicht als frisches objektgetrenntes Feld an die sechs
S1-GD-Aufrufe weitergegeben.

Damit fehlt genau:

```text
S1-FI initial_field
-> sechs tiefe, digestgleiche und objektgetrennte Fresh-Field-Objekte
-> je eines an genau einen S1-GD-Aufruf gebunden
```

Ein alter Acht-Rollen-`Fresh Field`-Slot darf diese Bruecke nicht ersetzen,
weil sein Binding nicht dem neuen Zehn-Rollen-Objekt entspricht.

## Aussagegrenze

Es wurde kein Feld konstruiert, kopiert oder fortgeschrieben. Kein Batch,
Kernel, Snapshot oder Receipt wurde ausgefuehrt beziehungsweise erzeugt.
S1-GG ist nur eine statische Anschlusskartierung und kein Mess- oder
Memory-Befund.

Entscheidung:

```text
REAL_FIXED_ADAPTER_KERNEL_CHAIN_BOUND_FRESH_FIELD_BRIDGE_MISSING
```

## Bester naechster Schritt

S1-GH implementiert nur die typisierte Fresh-Field-Bruecke: sechs tiefe,
digestgleiche, objektgetrennte Kopien des gebundenen S1-FI-Anfangsfelds werden
atomar den sechs S1-GD-Aufrufen zugeordnet. Kein Probeplan, Batch oder
Feldkernel wird dabei ausgefuehrt.
