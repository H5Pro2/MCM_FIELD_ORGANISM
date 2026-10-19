# S2-SFA: finale, nicht autorisierte Methodenlaufbindung

**Status:** `BOUND_NOT_AUTHORIZED`  
**Zweck:** private 32-Frame-SFA-Methode; keine Feld-/Memoryintegration und kein
realer Medienlauf.

## Ausführbarer Einstieg

Der einzige vorgesehene Eintritt ist
`tools._s2sfa_private_visual_run.run_plan_once()`. Er prüft vor der ersten
Frameerzeugung Autorisierung und Ledger. Bei einer späteren, separaten
Freigabe muss ein neuer, unbenutzter `run_id` sowie exakt die unten gebundene
Ledgerfolge übergeben werden. Diese Datei setzt `authorized=False` und enthält
keine Lauf-ID-Freigabe.

`run_plan_once()` materialisiert höchstens einen Frame, hasht ihn vor
`LocalChannelGridReceptor.analyze()`, verwirft den Rohframe anschließend und
übergibt nur die 288 Rezeptorwerte samt Quittung an den numerischen SFA-Pfad.
Der zweite Schritt wird erst nach vollständiger Quellenlieferung erreicht.

## Aktive Abhängigkeiten

| Klasse | Datei(en) | Bytes | SHA-256 |
|---|---|---:|---|
| Quellen- und Laufcode | `tools/_s2sfa_private_visual_run.py` | 21.939 | `9c771ae1a340d88ddaa3431b8148017c3428ce73d3df78964c4ddfe6a506b709` |
| SFA-Methode | `tools/_s2sfa_private_visual_method.py` | 10.889 | `0fe16352a5a15bc0cc73acde7f71a8bdfe57156c022d2b4f87404e76a333793d` |
| visueller Rezeptor | `mcm_field_organism/finite_video_path.py` | 10.943 | `d09cb6ba35fd061e4a243b7ed2112597a194e75abd026d7cc3ab7aa89922c07a` |
| Plan- und Methodenbindung | `docs/ARCHITEKTURKLAERUNG_ZEITLICHE_ERFAHRUNGSSPUR.md` | 23.617 | `5dbe4e446bab5b4fb26ee342a8920ff4704f28dfb1892113dca8f5959b21960f` |
| Quellenquittungsqualifikation | `tests/test_s2sfa_source_receipt_requalification.py`, Vorbindung und Befund `20260919-02` | 8.854 | siehe Qualifikationsbeleg |
| frühere aktive Qualifikationsbelege | Methodenbefunde `20260919-02`, `20260919-03` und Ledgeranschluss `20260919-01` | 6.312 | siehe jeweilige Befunde |

Die Dateien der historischen fehlgeschlagenen Quittungsqualifikation bleiben
Archiv. Sie sind kein aktiver Zulassungsbeleg.

## Quellenquittung und Fehlerform

Für jeden Frame bleiben im Record Quellen-ID, Rezeptdigest,
Sequenzposition, Frameindex, RGB-Form, Datentyp, Eingangs-Hash, Status und
bei Analyseerfolg der Beobachtungsdigest. `HASHED_NOT_ANALYZED` bezeichnet
einen Hash vor fehlgeschlagener Analyse; `ANALYZED` bindet die 288
Kanalwerte. Der Hash belegt den tatsächlich erzeugten Eingang, nicht einen
vorversiegelten Sollwert.

Bei Quellenfehlern wird ein einzelner `INCOMPLETE`-Record mit bisheriger
Quittungsfolge und analysiertem Fortschritt erzeugt. Der read-only Verifikator
prüft diesen Fehlerrecord ohne Frame-Regeneration. Eine Auswertung bleibt
gesperrt.

## Gemeinsame Obergrenzenbilanz

| Beitrag | Byte |
|---|---:|
| aktive Code- und Planabhängigkeiten | 67.388 |
| aktive Qualifikationsbelege einschließlich Testquelle | 15.166 |
| Verifikationsreserve | 262.144 |
| Auswertungsreserve | 131.072 |
| Fehlerreserve | 262.144 |
| Recordobergrenze | 2.097.152 |
| temporäre Veröffentlichungsobergrenze | 2.097.152 |
| **Gesamtobergrenze** | **4.932.218** |
| globale Evidenzgrenze | 8.388.608 |
| verbleibende Reserve | 3.456.390 |

Die 6.220.800 Byte eines einzelnen RGB-Frames sind begrenzter
Arbeitspeicher, keine Belegablage. Es wird kein Rohframe im Record gespeichert.
Die Tabelle ist eine vorab gebundene Obergrenzenbilanz, keine gemessene
Laufgröße.

## Freigabegrenze

Der Methodenversuch bleibt bis zu einer neuen ausdrücklichen
Einmallaufentscheidung gesperrt. Eine solche Entscheidung muss neue Lauf-ID,
Ausgabeabwesenheit, diese Dateibindungen und die Ledgerwerte vor der ersten
Materialisierung prüfen.
