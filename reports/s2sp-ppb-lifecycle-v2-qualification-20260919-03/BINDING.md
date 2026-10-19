# S2-SP: PPB-Lebenszyklus V2 – Sichtumfangsqualifikation

Qualifikations-ID: `S2SP-PPB-LIFECYCLE-V2-QUAL-20260919-03`.

Die früheren Aufrufe `...-01` und `...-02` bleiben als nicht bestandene
Testanbindungsbefunde erhalten. Dieser Aufruf enthält ausschließlich die acht
bislang unerreichten Kontrollen des neuen Moduls:

```text
python -B -m unittest tests.test_s2sp_ppb_lifecycle_v2_connection -v
```

## Vergleichsbindung

Die unabhängige Exaktbaseline berechnet für jeden zulässigen Kandidaten nur

```text
all(candidate[i] == cue[i] for i in range(32))
```

und ruft keinen produktiven Scan- oder Vergleichshelfer auf. Verdeckte
Positionen `32..287` beeinflussen diese Entscheidung nicht. Die drei
zusätzlichen neutralen Kontrollen prüfen verdeckte Abweichung ohne
Entscheidungsänderung, sichtbare Abweichung ohne Exakttreffer sowie die
Abweisung einer ungültigen Sichtbindung.

Vor dem Aufruf wurden Ereignisform, Kandidatenform, sichtbarer Indexumfang,
Materialisierungs-/Cue-/Formations-/Readouttypen und Testauswahl statisch
geprüft. Es gibt keine Änderung an Materialisierer, Cuevertrag, produktiven
Abrufregeln, Quellen oder Memorykern.

## Gebundene Dateien

| Datei | SHA-256 |
|---|---|
| `tests/test_s2sp_ppb_lifecycle_v2_connection.py` | `b646306b4d1f25a30297349b4d9596113cc72f8aaa972678ae40d4809e0049c6` |
| `tools/_s2sp_oa_materialization_adapter.py` | `3f1833e5154bf06b522bb589194d2d7dc076c2fbb6006ef652c5fcfd95859484` |
| `tools/_s2sp_private_memory_compare.py` | `ded375226fe61ca3777d4282b756111c6d1ffb29ae42e10a4cd84d0d61998d51` |
| `mcm_field_organism/_tspm1_private.py` | `014d6e52b82751673d0411aaf603813c2cae14a6a26b4d6d527c3c9e129bf13b` |
| `tools/_s2jw_profiled_memory_coordinator.py` | `0bf4e469321fd780cf71ad2cbfd418e9665af1dfdc618f9d8697fe9f8887b3f8` |

Die neutral materialisierte Hülle bindet 20 Ereignisse, 18 Formationen, zwei
read-only Hinweise, zwei getrennte Arme, native PPB-Readouts, unabhängige
Verifikation und negative Lifecycle-Auswertung. Record, Verifikation und
Auswertung müssen gemeinsam höchstens `262144` Byte belegen.
