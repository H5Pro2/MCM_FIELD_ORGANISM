# S2-SP-Abbruchbeleg

Auftragskennung: `S2SP-SHIFT-HINT-20260919-01`  
Lauf-ID: `s2sp-shift-hint-real-20260919-01`  
Status: `NOT_EVALUABLE`

Der einmalige gebundene Aufruf `python reports/run_s2sp_shift_hint_once.py`
brach in der Importphase ab, bevor `LocalChannelGridReceptor` instanziiert
oder eine Quelle erzeugt wurde.

```text
ModuleNotFoundError: No module named 'mcm_field_organism'
```

Der unmittelbare technische Grund ist der dateidirekte Start: Python setzt
`reports/` als ersten Suchpfad; der Projektwurzelpfad war nicht an den
Skriptprozess gebunden. Es wurden deshalb keine RGB-Frames erzeugt, keine
Rezeptoranalysen ausgeführt, keine Memory- oder Feldkontakte ausgelöst und
kein Ergebnisartefakt publiziert.

Dieser Befund ist kein negativer Vergleichsbefund. Ein Ersatzlauf wurde nicht
gestartet. Eine mögliche spätere Korrektur müsste ausschließlich die
dateigebundene Import-/Aufrufumgebung vor der Quellenmaterialisierung
qualifizieren und separat freigegeben werden.
