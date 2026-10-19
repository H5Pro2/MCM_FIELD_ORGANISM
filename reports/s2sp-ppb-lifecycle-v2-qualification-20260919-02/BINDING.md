# S2-SP: PPB-Lebenszyklus V2 – korrigierte Anschlussqualifikation

Qualifikations-ID: `S2SP-PPB-LIFECYCLE-V2-QUAL-20260919-02`.

Der vorherige Aufruf unter `...-01` bleibt `NOT_QUALIFIED`; diese Bindung
führt ausschließlich die fünf dort nicht erreichten Prüfgruppen aus.

```text
python -B -m unittest tests.test_s2sp_ppb_lifecycle_v2_connection -v
```

## Typgrenze vor dem Aufruf

| Übergabe | Exakter Typ |
|---|---|
| AV-Materialisierung | `S2SPOAMaterializedPairV1` |
| gebundenes AV-Pair | `S2JVBoundAVPairV1` |
| Memory-Vorzustand | `S2JVCompositeStateV1` |
| atomarer Formationsrückgabewert | `S2JVFormationResultV1` |
| visueller PPB-Readout | `PPB1Readout` oder `None` |
| visueller Cue-Payload | `MaskedMemoryCue336V1` direkt, ohne Wrapper |

Die Cuewerte stammen folglich direkt aus `operation.values`; nicht sichtbare
Positionen werden ausschließlich für die neutrale Vergleichsansicht mit
`0.0` repräsentiert. Der produktive Cuevertrag und der Materialisierer bleiben
unverändert.

## Gebundene Dateien

| Datei | SHA-256 |
|---|---|
| `tests/test_s2sp_ppb_lifecycle_v2_connection.py` | `5281b02e343973959d13d99bc8d1194f3215b0d07fcc3396cdd2321c695a08e5` |
| `tools/_s2sp_oa_materialization_adapter.py` | `3f1833e5154bf06b522bb589194d2d7dc076c2fbb6006ef652c5fcfd95859484` |
| `tools/_s2sp_private_memory_compare.py` | `ded375226fe61ca3777d4282b756111c6d1ffb29ae42e10a4cd84d0d61998d51` |
| `mcm_field_organism/_tspm1_private.py` | `014d6e52b82751673d0411aaf603813c2cae14a6a26b4d6d527c3c9e129bf13b` |
| `tools/_s2jw_profiled_memory_coordinator.py` | `0bf4e469321fd780cf71ad2cbfd418e9665af1dfdc618f9d8697fe9f8887b3f8` |

Die Hülle bindet 20 neutrale Ereignisse, 18 Formationen, zwei read-only
Hinweise, beide getrennten Arme, die unabhängige Cue-Exaktbaseline,
Lifecycle-Auswertung und die gemeinsame 262.144-Byte-Bilanz. Die frühere
Adapter-`2/2`- und Readout-`2/2`-Qualifikation werden nur referenziert.
