# S2-SFA-Quellenquittungsqualifikation 20260919-01: Fehlbefund

## Ergebnis

`NOT_QUALIFIED` — der einmalig vorgebundene Aufruf

```powershell
C:\Python314\python.exe -m unittest tests.test_s2sfa_source_receipt_connection
```

endete mit `Ran 3 tests ... FAILED (errors=2)`. Es erfolgt kein Retry.

## Tatsächlich erreichte Kontrolle

`test_failure_after_hash_retains_only_hashed_receipt` wurde erreicht. Der
neutrale Fehleradapter brach nach Hashbildung ab; der resultierende
unvollständige Record enthielt eine `HASHED_NOT_ANALYZED`-Quittung, Fortschritt
null und wurde read-only als `INCOMPLETE_ACCEPTED` verifiziert.

## Fehlerursache

Die zwei Erfolgspfadkontrollen scheiterten in
`tools/_s2sfa_private_visual_run.py:213` vor der Aufnahme einer
Beobachtungsquittung:

```text
AttributeError: 'VisualReceptorState' object has no attribute 'values'
```

Der vorhandene Rezeptor liefert seine 288 Werte unter
`VisualReceptorState.channel_values`
([`finite_video_path.py:74`](../../mcm_field_organism/finite_video_path.py:74),
[`finite_video_path.py:210`](../../mcm_field_organism/finite_video_path.py:210)),
nicht unter `values`. Dadurch wurde die neue Quellenlieferung nach ihrem Hash,
aber vor erfolgreicher Analyse als `SOURCE_ANALYSIS_FAILED` abgeschlossen.

Dies ist ein lokaler Adapterfehler. Er belegt weder eine Einschränkung der
Rezeptorwerte noch einen SFA-, Feld- oder Memorybefund.

## Grenzen

Es wurden ausschließlich unabhängige neutrale RGB-Frames verarbeitet. Der
gebundene 32-Frame-Methodenbestand wurde nicht materialisiert; kein realer
Methoden- oder Medienlauf wurde gestartet. Die Erfolgskette bis Record,
Verifikation und Auswertung ist wegen der beiden Fehler nicht qualifiziert.

## Kleinste Korrekturrichtung

Der Quellenadapter muss ausschließlich die vorhandene technische Ausgabe
`channel_values` lesen und deren bestehende 288-Wert-/Endlichkeitsprüfung
beibehalten. Danach erfordert die unveränderte vollständige
Quellenquittungsqualifikation eine neue ausdrückliche Freigabe.
