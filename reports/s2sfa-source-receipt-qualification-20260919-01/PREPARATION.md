# S2-SFA-Quellenquittungsqualifikation 20260919-01: Vorbindung

## Auftrag

Einmaliger neutraler End-to-End-Nachweis für den privaten S2-SFA-
Quellenanschluss: Quellenlieferung, Hashquittung vor Rezeptoranalyse,
Rezeptorwert, Laufrecord, Veröffentlichung, read-only Verifikation und
getrennte Auswertung.

## Gebundene Dateien

| Datei | SHA-256 |
|---|---|
| `AKTUELLER_FORSCHUNGSWEG.md` | `d5705fdef1d74c5009ddf5e5a2682692b40ee7bf62168bd2e726bba52b0e7c0f` |
| `tools/_s2sfa_private_visual_run.py` | `5e5a557abe6af26320bd68d8ac5e7ae778546d3e51dc1fc57650445c81ec0f5f` |
| `tests/test_s2sfa_source_receipt_connection.py` | `2b31c277b1e479eb078d059c4a32f7070b78a5f5d7b6c8d3dc65e65f8fbf87eb` |

## Einmaliger Aufruf

```powershell
C:\Python314\python.exe -m unittest tests.test_s2sfa_source_receipt_connection
```

## Prüfumfang

1. Eigenständige neutrale RGB-Frames werden einzeln geliefert, vor
   `analyze()` gehasht und mit neutraler Quellen-ID, Rezeptdigest,
   Sequenzposition, Form und Datentyp quittiert.
2. Nach erfolgreicher Analyse bindet die Quittung zusätzlich den Digest der
   288 gespeicherten Beobachtungswerte. Der vollständige Record wird
   veröffentlicht, read-only verifiziert und getrennt ausgewertet.
3. Fehlende oder manipulierte Quittungen werden vor der numerischen
   Verarbeitung abgewiesen.
4. Ein neutraler Fehler nach Hashbildung erhält ausschließlich eine
   `HASHED_NOT_ANALYZED`-Quittung, Fortschritt null und einen verifizierbaren
   unvollständigen Record.

## Grenzen

- Der gebundene 32-Frame-Plan wird nicht materialisiert; die Qualifikation
  verwendet nur unabhängige neutrale Framewerte und ruft weder
  `_plan_sources()` noch `materialize_frame()` auf.
- Ein Hash bindet den tatsächlich erzeugten Eingang. Er vergleicht keinen
  vorversiegelten Sollhash und belegt daher keine Quellenidentität außerhalb
  des gespeicherten Records.
- Ledgergrenzen: maximal 2 MiB je Record und 8 MiB gemeinsame Belegablage.
- Keine Feld-/Memoryintegration und kein realer Methodenversuch.
