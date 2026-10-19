# S2-SP: PPB-Lebenszyklus V2 – Anschlussqualifikation

Qualifikations-ID: `S2SP-PPB-LIFECYCLE-V2-QUAL-20260919-01`.

## Einmaliger Aufruf

```text
python -B -m unittest tests.test_s2sp_ppb_lifecycle_v2_connection -v
```

Das Modul enthält ausschließlich fünf neue Kontrollen. Es ruft weder
`tests.test_s2sp_oa_materialization_adapter` noch die historische
Readout-Qualifikation auf. Die gebuchten Teilnachweise `2/2` (Adapter) und
`2/2` (Readout) werden nur als Voraussetzungen referenziert.

## Gebundene Dateien

| Datei | SHA-256 |
|---|---|
| `tests/test_s2sp_ppb_lifecycle_v2_connection.py` | `199a059b52bc5d4519b7e1e1767498b7a6bff33539c1461b55f5976bf981616b` |
| `tools/_s2sp_oa_materialization_adapter.py` | `3f1833e5154bf06b522bb589194d2d7dc076c2fbb6006ef652c5fcfd95859484` |
| `tools/_s2sp_private_memory_compare.py` | `ded375226fe61ca3777d4282b756111c6d1ffb29ae42e10a4cd84d0d61998d51` |
| `mcm_field_organism/_tspm1_private.py` | `014d6e52b82751673d0411aaf603813c2cae14a6a26b4d6d527c3c9e129bf13b` |
| `tools/_s2jw_profiled_memory_coordinator.py` | `0bf4e469321fd780cf71ad2cbfd418e9665af1dfdc618f9d8697fe9f8887b3f8` |

## Prüfbestand und Grenzen

Die neutrale Hülle enthält genau 20 Ereignisse: 18 vollständige AV-
Formationen und zwei visuelle, read-only Hinweise bei Ordinalen 14 und 20.
Die 18 Paare werden einmal materialisiert und an zwei getrennte frische
Memoryzustände übergeben. Das Modul bindet pro Arm alle Übergangsbelege und
native visuelle PPB-Readouts, prüft Hinweise gegen eine unabhängige direkte
Exaktbaseline und wertet fehlende Lifecycle-Voraussetzungen ausschließlich als
`PRÜFBEDINGUNG_NICHT_ERREICHT` aus.

Der kanonische Neutralrecord, Verifikation und Auswertung werden gemeinsam
gegen `262144` Byte geprüft. Rohpayloads liegen nur temporär während des
Testaufrufs vor; OA-Quellen und der reale V2-Korpus werden nicht gelesen.
