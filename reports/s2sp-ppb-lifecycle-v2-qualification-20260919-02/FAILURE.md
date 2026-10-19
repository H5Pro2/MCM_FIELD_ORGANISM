# S2-SP: PPB-Lebenszyklus V2 – fehlgeschlagene korrigierte Anschlussqualifikation

Qualifikations-ID: `S2SP-PPB-LIFECYCLE-V2-QUAL-20260919-02`.

Der einmalige gebundene Aufruf des ausschließlich neuen Testmoduls endete nach
`9.367 s` mit `Ran 0 tests` und einem Fehler in `setUpClass`. Die korrigierte
direkte Cue-Übergabe wurde erreicht; die fünf Testkörper wurden wegen des
nachfolgenden Verifikationsfehlers nicht ausgeführt.

## Primärfehler

Die neue unabhängige Baseline verglich vollständige 288-Werte-Vektoren. Die
produktive Exaktbaseline prüft dagegen ausschließlich die sichtbaren
Positionen des `MaskedMemoryCue336V1`. Dadurch entstand bei
`_verify(...):124` die Assertion:

```text
AssertionError: independent cue baseline differs
```

Das ist eine fehlerhafte Neutraltestbaseline, kein Befund gegen
Materialisierung, Memoryfortschreibung, PPB-Lifecycle oder die read-only
Hinweisregel. Die vollständige V2-Qualifikation wurde nicht erreicht, da die
unabhängige Vergleichsregel selbst nicht den gebundenen Cuevertrag abbildete.

Der Fehlbefund bleibt erhalten. Kein Retry, kein V2-Hauptlauf und keine
automatische Anpassung der Vergleichsregel folgen aus diesem Aufruf.
