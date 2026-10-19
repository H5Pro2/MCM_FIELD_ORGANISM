# S2-SP-Memoryvergleich: Qualifikationsfehlbefund

Auftragskennung: `S2SP-MEMORY-COMPARE-QUAL-20260919-01`  
Status: `NOT_QUALIFIED`

Der einmalige fokussierte neutrale Aufruf

```powershell
python -B -m unittest tests.test_s2sp_private_memory_compare -v
```

endete mit drei Fehlern. Alle drei Prüfgruppen erreichten die erste neutrale
Formation und brachen anschließend im privaten Quellenanschluss ab:

```text
AttributeError: 'VisualReceptorState' object has no attribute 'frame'
```

Auslöser ist `Sources.formation()` in
`tools/_s2sp_private_memory_compare.py`: Der Rückgabebeleg verwendet
`visual.frame.values`; der direkte visuelle Rezeptorzustand stellt seine Werte
jedoch als `visual.channel_values` bereit. Dadurch wurden weder der read-only
Hinweis, die Innenabweichungsabweisung noch die B4-Ersetzungskontrolle
erreicht.

Dieser Befund betrifft den neuen privaten Anschluss, nicht den bestehenden
Memorykern. Die gebundene reale S2-SP-Folge wurde nicht gestartet. Es erfolgte
keine automatische Korrektur oder Wiederholung.
