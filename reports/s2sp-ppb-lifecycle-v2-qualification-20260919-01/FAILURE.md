# S2-SP: PPB-Lebenszyklus V2 – fehlgeschlagene Anschlussqualifikation

Qualifikations-ID: `S2SP-PPB-LIFECYCLE-V2-QUAL-20260919-01`.

Der einmalige gebundene Aufruf

```text
python -B -m unittest tests.test_s2sp_ppb_lifecycle_v2_connection -v
```

endete nach `6.474 s` mit `Ran 0 tests` und einem Fehler in `setUpClass`.
Keine der fünf vorbereiteten Prüfgruppen wurde erreicht.

## Primärfehler

`tests/test_s2sp_ppb_lifecycle_v2_connection.py:63` behandelte die vom
OA-Materialisierer zurückgegebene visuelle Cue-Operation irrtümlich als
Wrapper mit Attribut `.cue`. Der tatsächliche Payloadtyp ist bereits
`MaskedMemoryCue336V1`; deshalb endete der Aufbau bei:

```text
AttributeError: 'MaskedMemoryCue336V1' object has no attribute 'cue'
```

Die Ursache liegt in der neuen Neutraltestanbindung, nicht in einer
Ausführung der V2-Lebenszykluslogik. Die Materialisierung hatte vor dem
Fehler eine Teilfolge erreicht; sie erzeugt keinen gültigen
Qualifikations- oder Forschungsbefund. Der Record, die unabhängige
Verifikation, die Lifecycle-Auswertung und die fünf Testkörper wurden nicht
erreicht.

Es erfolgt kein Retry und kein V2-Hauptlauf. Die gebundenen früheren
Teilqualifikationen bleiben unverändert; diese Qualifikation ist
`NOT_QUALIFIED`.
