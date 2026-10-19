# S2-SFA-Quellenquittungsqualifikation 20260919-02: Befund

## Ergebnis

`QUALIFIED` — der einmalig vorgebundene Aufruf

```powershell
C:\Python314\python.exe -m unittest tests.test_s2sfa_source_receipt_requalification
```

endete mit `Ran 3 tests in 4.224s ... OK`.

## Erreichte Kontrollen

| Kontrolle | Ergebnis |
|---|---|
| 288 Kanalwerte | `channel_values` werden unverändert und in vorhandener Rezeptorreihenfolge als Beobachtung übernommen; ihr Digest ist Teil der Quittung. |
| Vollständiger neutraler Pfad | Eigenständige neutrale RGB-Frames: Lieferung, Hash vor `analyze()`, 32 analysierte Quittungen, Record, atomare Veröffentlichung, read-only Verifikation und getrennte Auswertung. |
| Fehlende Quittung | Vor numerischer Verarbeitung mit `SOURCE_RECEIPTS_REQUIRED` abgewiesen. |
| Manipulierte Quittung | Vor numerischer Verarbeitung mit `SOURCE_BINDING_INVALID` abgewiesen. |

Der Abbruch nach Hashbildung wurde nicht wiederholt. Er bleibt als bestandene
Kontrolle im historischen Fehlbefund
[20260919-01](../s2sfa-source-receipt-qualification-20260919-01/REPORT.md)
erhalten.

## Quellenquittung

Jede Quittung enthält die neutrale Quellen-ID, den Rezeptdigest,
Sequenzposition, Frameindex, RGB-Form, Datentyp, Hash des tatsächlich
erzeugten Eingangs, Status und bei erfolgreicher Analyse den Digest der 288
Beobachtungswerte. `HASHED_NOT_ANALYZED` und `ANALYZED` bleiben getrennt.

Der Eingangshash bindet den tatsächlich erzeugten Frame; er vergleicht keinen
vorversiegelten Sollhash. Damit belegt er keine externe Quellenidentität.
Der Verifikator prüft Struktur, Sequenz, Digest und
Beobachtungsbindung ausschließlich aus dem Record, ohne Frame-Regeneration.

## Grenzen

Die Qualifikation verwendete nur unabhängige neutrale Frames und materialisierte
weder `_plan_sources()` noch `materialize_frame()`. Kein realer
32-Frame-Methodenversuch, Medienlauf, Feld- oder Memorypfad wurde ausgeführt.
Die erfolgreiche Anschlussqualifikation ist keine Ausführungsfreigabe.
