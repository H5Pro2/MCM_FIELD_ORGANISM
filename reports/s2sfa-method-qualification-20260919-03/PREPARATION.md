# S2-SFA: Vorbereitung der fokussierten Ergänzungsqualifikation

**Qualifikations-ID:** `s2sfa-method-qualification-20260919-03`  
**Status vor Aufruf:** gebunden, noch nicht ausgeführt

## Umfang

Dieser Aufruf erreicht nur die zwei fehlenden Kontrollen aus
`20260919-02`; die dort bestandenen sieben Testmethoden werden nicht erneut
ausgeführt.

1. Ein vollrangiger projektierter Zweidimensionalfall mit zwei gleichen
   kleinsten Eigenwerten muss `SFA_TRAINING_DEGENERATE` liefern.
2. Eine private `LinearSFALearner`-Instanz muss nach `freeze()` zwei
   unterschiedliche spätere Prüfwerte unverändert projizieren und eine weitere
   Lernzufuhr mit `SFA_LEARNER_FROZEN` abweisen.

Die neue Lerninstanz kapselt nur die bereits vorhandene reine
`fit_linear_sfa()`-Funktion. Sie berührt Feld, Memory, Rezeptoren und den
gebundenen 32-Frame-Bestand nicht. Die sieben Vorgängerprüfungen bleiben
historische Einzelbefunde; ein zusammengeführter Gesamtstatus folgt erst aus
diesem Befund und den unveränderten Quellenbindungen.

## Einziger Aufruf

- Arbeitsverzeichnis: `C:\Users\TV\Documents\MCM_FIELD_ORGANISM\workspace`
- Interpreter: `C:\Python314\python.exe` (`Python 3.14.4`)

```text
C:\Python314\python.exe -m unittest tests.test_s2sfa_focused_coverage
```

Keine globale `PYTHONPATH`-Änderung oder Installation. Keine Planframes,
Rezeptor-, NJ-, Feld- oder Memoryaufrufe.

## Quellenbindung

| Datei | SHA-256 |
| --- | --- |
| `tools/_s2sfa_private_visual_method.py` | `0fe16352a5a15bc0cc73acde7f71a8bdfe57156c022d2b4f87404e76a333793d` |
| `tests/test_s2sfa_focused_coverage.py` | `58b70d5bb43694807237adad8a040891a81be09cb919c5e4fe3de2680b48f802` |
| `docs/ARCHITEKTURKLAERUNG_ZEITLICHE_ERFAHRUNGSSPUR.md` | `5dbe4e446bab5b4fb26ee342a8920ff4704f28dfb1892113dca8f5959b21960f` |

`20260919-01` und `20260919-02` bleiben unverändert `NOT_QUALIFIED`.
