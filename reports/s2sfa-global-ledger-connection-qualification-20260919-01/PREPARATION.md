# S2-SFA Ledger-Anschlussqualifikation 20260919-01: Vorbindung

## Auftrag

Ein einmaliger neutraler Anschlussnachweis für den privaten S2-SFA-Laufweg. Er
verbindet den Ledger vor jeder Beobachtungsverarbeitung mit Lauf,
Veröffentlichung, read-only Verifikation, Auswertung und Fehlerabschluss.

## Gebundene Dateien

| Datei | SHA-256 |
|---|---|
| `tools/_s2sfa_private_visual_run.py` | `48395c38cb2d9bdd06e28ecdc29a285e4d5dff63d7dffdfc569385af62803aff` |
| `tests/test_s2sfa_global_ledger_connection.py` | `0963e74c8fbdb371b87c9a9a98b16c5ebbfd995aa64f4b6049e31bf6e07c74df` |

## Einmaliger Aufruf

```powershell
C:\Python314\python.exe -m unittest tests.test_s2sfa_global_ledger_connection
```

## Umfang und Grenzen

- Ausschließlich neutrale numerische Beobachtungsvektoren mit 288 Werten.
- Keine Planframe-Erzeugung, keine Rezeptoranalyse und keine reale
  S2-SFA-Auswertung.
- Gemeinsames Ledger: Referenzen 512 KiB, Qualifikation 512 KiB, Verifikation
  256 KiB, Auswertung 128 KiB sowie 512 KiB Fehlerreserve.
- Der Pfad zählt den vollständigen Record (maximal 2 MiB), seine temporäre
  Veröffentlichung (maximal 2 MiB), den Fehlerabschluss und alle Ledgerteile
  gegen die globale 8-MiB-Evidenzgrenze.

## Prüfabdeckung

1. Erfolgsrecord vom Eintritt bis zur atomaren Veröffentlichung, read-only
   Verifikation und getrennten Auswertung unter derselben Ledgerbindung.
2. Unvollständiger Record und dessen Veröffentlichung unter derselben
   Ledgerbindung.
3. Fehlendes Ledger an Eintritt und Veröffentlichung vor Nutzdatenverarbeitung.
4. Globale Überschreitung vor Beobachtungsverarbeitung.

Die ältere isolierte Ledger-Qualifikation wird nicht wiederholt.
