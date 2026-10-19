# S2-TY: Auswerternormalisierung

Kennung: `s2ty-evaluation-normalization-qualification-20260920-01`.
Der einmalige neutrale Aufruf umfasst sechs Tests aus
`tests.test_s2ty_evaluation`.

Geprüft werden native Trefferpaare als Tupel, JSON-Listen nach Roundtrip,
abweichende Generation, abweichender Offset, abweichende Reihenfolge,
Mehrfachtreffer sowie ungültige Paarformen. Die Normalisierung ist ausschließlich
eine strukturelle Darstellungskorrektur: Sie sortiert, dedupliziert und wandelt
keine numerischen Werte um.

Gebunden: `tools/_s2ty_evaluation.py`
`272af6a37783cf0250b3ae169fb77dbf4fc8b218b656d42fd773f014684055b3`;
`tests/test_s2ty_evaluation.py`
`dc34c1a8b2e1c04920abf772693304723d1779b0779f1f2227d4552e0f021c1a`.
Keine reale Laufdatei wird durch diese Qualifikation gelesen.
