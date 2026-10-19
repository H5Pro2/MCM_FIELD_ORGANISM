# S2-SFA-Quellenquittungsqualifikation 20260919-02: Vorbindung

## Anlass

Gezielte Neuqualifikation der lokalen Adapterkorrektur von `state.values` auf
den vorhandenen Vertrag `VisualReceptorState.channel_values`. Der historische
Fehlbefund `20260919-01` bleibt unverändert `NOT_QUALIFIED`.

## Statische Typprüfung

`LocalChannelGridReceptor.analyze()` liefert `VisualReceptorState` mit
`channel_values: tuple[float, ...]`. Der Rezeptor erzwingt Gleichheit von
Kanal- und Trägeranzahl, endliche Werte im Bereich `0..1` und die feste
Trägerreihenfolge. Der Adapter liest ausschließlich dieses Feld und prüft
weiterhin exakt 288 endliche Werte. `frame_index`, `geometry_id`,
`carrier_ids` und `contact` werden nicht als Ersatzwerte verwendet.

## Gebundene Dateien

| Datei | SHA-256 |
|---|---|
| `AKTUELLER_FORSCHUNGSWEG.md` | `d5705fdef1d74c5009ddf5e5a2682692b40ee7bf62168bd2e726bba52b0e7c0f` |
| `tools/_s2sfa_private_visual_run.py` | `9c771ae1a340d88ddaa3431b8148017c3428ce73d3df78964c4ddfe6a506b709` |
| `tests/test_s2sfa_source_receipt_requalification.py` | `19c573fea6a55b58743d133caf87babe775780c8a5b385f2b4b6ed1d77089100` |

## Einmaliger Aufruf

```powershell
C:\Python314\python.exe -m unittest tests.test_s2sfa_source_receipt_requalification
```

## Prüfumfang

1. Alle 288 `channel_values` werden unverändert in Rezeptorreihenfolge
   übernommen und als Beobachtungsdigest gebunden.
2. Quellenlieferung, Hashquittung vor Analyse, Record, Veröffentlichung,
   read-only Verifikation und getrennte Auswertung werden mit neutralen
   Frames vollständig erreicht.
3. Fehlende und manipulierte Quittungen werden vor numerischer SFA-
   Verarbeitung abgewiesen.

Der bereits bestandene Abbruch nach Hashbildung aus `20260919-01` wird nicht
wiederholt. Weder `_plan_sources()` noch `materialize_frame()` werden durch
diese neutrale Suite verwendet; der reale 32-Frame-Methodenversuch bleibt
gesperrt.
