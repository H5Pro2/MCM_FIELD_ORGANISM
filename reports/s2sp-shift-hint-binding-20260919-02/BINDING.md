# S2-SP Start- und Ausgabebindung

Auftragskennung: `S2SP-SHIFT-HINT-START-20260919-02`  
Geplante Lauf-ID: `s2sp-shift-hint-real-20260919-02`

Der vorherige Lauf `s2sp-shift-hint-real-20260919-01` bleibt
`NOT_EVALUABLE`. Er endete vor Quellenmaterialisierung, weil der direkte
Dateistart den Workspace-Importpfad nicht enthielt.

## Verbindlicher Start

Der neue Einmallauf darf ausschließlich aus der Workspacewurzel mit dem
festen Interpreteraufruf erfolgen:

```powershell
python -B -m reports.run_s2sp_shift_hint_once
```

Es gibt keine globale `PYTHONPATH`-Änderung, Installation oder
Validatorlockerung. Der Modulimport selbst ruft `run_once()` nicht auf und
materialisiert daher keine Quelle.

## Ergebnisdarstellung

`render_report()` bildet Exaktbaseline, eindeutige Teilstrukturhinweise,
Kandidatenmehrdeutigkeiten, Offsetmehrdeutigkeiten und Enthaltungen direkt aus
den gespeicherten Evaluationszeilen. Sie enthält keine vorformulierte positive
Aussage zu einem konkreten Vergleichsfall. Die separate Evaluationswurzel
ordnet Sollrollen erst nach der technischen Verifikation zu und markiert jede
Abweichung als `DEVIATION`.

## Unveränderte Versuchsbindung

Quellenrezepte, sechs direkte Rasteranalysen, fünf Vergleichsbedingungen,
Offets `-1`, `0`, `+1`, die Exaktbaseline der ersten 32 Werte und die
Artefaktgrenzen bleiben gegenüber der Bindung `…-01` unverändert. Memory- und
Feldkontakte bleiben bei null.

## Aktive Dateien

| Datei | SHA-256 |
| --- | --- |
| `reports/run_s2sp_shift_hint_once.py` | `d0f65e15fff1189f1a5c96c8dad7e7dc1629897330d36736fe63405060d8b4b9` |
| `tests/test_s2sp_shift_hint_runner_binding.py` | `92fbf0772387c571057335eb763c439a12ed7594afc64a4992f3ccec4949b2c7` |
| `tools/_s2sp_private_shift_hint.py` | `cc16661dc16f75e5e59e077a739c7b7a608168d68aafe1cdb31071f04532ed36` |

Die sechs früheren reinen Logiktests werden nicht wiederholt. Der neue
fokussierte Testumfang besteht aus dem frischen Modulimport ohne
Materialisierung und der synthetischen positiven sowie negativen
Ergebnisdarstellung.
