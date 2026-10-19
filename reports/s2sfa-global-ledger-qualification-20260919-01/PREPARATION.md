# S2-SFA: Gemeinsame Ledger-Qualifikation

**Profil:** `SFA_EVIDENCE_2M_8M_V1`  
**Grenzen:** Record `2.097.152`, Gesamtpeak `8.388.608` Byte

Der einzige Aufruf aus dem Repository-Stamm lautet:

```text
C:\Python314\python.exe -m unittest tests.test_s2sfa_global_ledger
```

Er prüft ausschließlich: gemeinsame Überschreitung bei lokal passenden
Einträgen sowie Referenzen, Qualifikation, Record, temporäre Kopie,
Verifikation, Auswertung und Fehlerreserve in einem Peak. Methoden- und lokale
Budgettests werden nicht wiederholt; keine Planframes oder Rezeptoren werden
aufgerufen.

| Datei | SHA-256 |
| --- | --- |
| `tools/_s2sfa_private_visual_run.py` | `81b75b34ef56aab0951215bcdc67a464e99c0142c00b477312c6d76ce736f387` |
| `tests/test_s2sfa_global_ledger.py` | `e077a1bde65417eb4ef8accc88d5a0ce6642124d0863a7bafc4d751033042397` |
