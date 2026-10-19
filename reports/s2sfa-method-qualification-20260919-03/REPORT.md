# S2-SFA: Fokussierte Ergänzungsqualifikation

**Qualifikations-ID:** `s2sfa-method-qualification-20260919-03`  
**Status:** `2/2 QUALIFIED`  
**Aufruf:** einmal

```text
C:\Python314\python.exe -m unittest tests.test_s2sfa_focused_coverage
```

Der Aufruf lief aus
`C:\Users\TV\Documents\MCM_FIELD_ORGANISM\workspace` mit
`C:\Python314\python.exe` (`Python 3.14.4`) und endete mit Exitcode 0:

```text
Ran 2 tests in 0.002s
OK
```

## Neue Prüfdeckung

| Kontrolle | Ergebnis |
| --- | --- |
| Vollrangiger projektierter Fall mit gleichem kleinstem SFA-Eigenwert | `SFA_TRAINING_DEGENERATE` bestätigt |
| Zwei spätere unterschiedliche Prüffolgen nach `freeze()` | eingefrorener Digest unverändert |
| Lernzufuhr nach `freeze()` | `SFA_LEARNER_FROZEN` bestätigt |

Die Ergänzung fügt nur `LinearSFALearner` als private Zukunftssperre um die
unveränderte reine Funktion `fit_linear_sfa()` hinzu. Die sieben früheren
Einzelbefunde für Planbindung, Einfrieren, konstante Eingänge, Rangmangel,
wiederholte Kovarianzeigenwerte, Basisinvarianz, Residuen, Rohbaseline und
Rang-/Auswertungsregeln blieben unverändert und wurden gemäß Auftrag nicht
wiederholt.

## Zusammengeführte Deckung

`20260919-01` bleibt wegen des Importfehlers `NOT_QUALIFIED`.
`20260919-02` bleibt wegen der damals fehlenden zwei Kontrollen
`NOT_QUALIFIED`. Zusammen mit den dort tatsächlich bestandenen sieben
Einzeltests belegt dieser neue fokussierte Aufruf die neun vorab geforderten
neutralen Kontrollen. Dies ist eine technische Methodenqualifikation, kein
Funktionsbefund zum 32-Frame-Planbestand.

Keine Planframes, Rezeptor-, NJ-, Feld- oder Memoryaufrufe wurden ausgeführt.
Der reale Methodenvergleich bleibt gesperrt.

## Aktive Bindungen

| Datei | SHA-256 |
| --- | --- |
| `tools/_s2sfa_private_visual_method.py` | `0fe16352a5a15bc0cc73acde7f71a8bdfe57156c022d2b4f87404e76a333793d` |
| `tests/test_s2sfa_private_visual_method.py` | `4e03a89ef43f08e05a578b8ed6c2990b03cb134263d10f147c8616b066767e6b` |
| `tests/test_s2sfa_focused_coverage.py` | `58b70d5bb43694807237adad8a040891a81be09cb919c5e4fe3de2680b48f802` |
| `docs/ARCHITEKTURKLAERUNG_ZEITLICHE_ERFAHRUNGSSPUR.md` | `5dbe4e446bab5b4fb26ee342a8920ff4704f28dfb1892113dca8f5959b21960f` |
| `PREPARATION.md` | `33ad0550c6768a5838579117c08961f99f070ecbf51676effd6b27403a5a7d5b` |
