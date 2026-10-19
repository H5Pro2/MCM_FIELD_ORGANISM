# S2-UC: Entscheidungspaket für einen neuen Einmallauf

Stand: 2026-09-20. Dieses Paket ist statisch. Es öffnet keine PCM-Quelle,
wertet keinen historischen Record erneut aus und autorisiert keinen Lauf.

## Vorbereitete Bindung

Der mögliche neue Lauf hat die reservierte, unbenutzte Kennung
`s2uc-source-comparison-real-20260920-02` und die Ergebnisablage
`reports/s2uc-source-comparison-real-20260920-02`. Quellenplan,
Geschichten, Zielerwartungen und Regeln sind gegenüber dem historischen Lauf
unverändert. Nur Recordcodec und technischer Fehlerabschluss unterscheiden
sich.

Die vorbereitete, aber absichtlich nicht ausführbare Quellenbindung ist
[`S2UC_RUN_BINDING_20260920_V8_PREPARED.json`](../reports/s2uc/S2UC_RUN_BINDING_20260920_V8_PREPARED.json)
mit SHA-256
`262fd389a585bd9ef3c8b5e3b1e7279bbd89e78d96a08097e43c5a415068607c`.
Die dazugehörige vollständige Entwurfsbindung ist
[`S2UC_RUN_BINDING_20260920_FINAL_V8_PREPARED.json`](../reports/s2uc/closure-preparation/S2UC_RUN_BINDING_20260920_FINAL_V8_PREPARED.json),
SHA-256
`2415ee10988e09ca1eae59b68c096416854e2ddcc82a0656fcfe6c129558bb55`.

Sie sind keine gültigen Eingaben für den gegenwärtigen Starter: Dieser prüft
noch die historische feste Laufkennung. Ein ausführbarer Startbefehl wird
bewusst nicht ausgegeben. Er wäre ohne eine neue, neutral geprüfte
Identitätsbindung irreführend.

## Größenbefund

Die gemessenen `58.378` Byte Recordmetadaten stammen aus einer neutralen
Messung mit Nullwerten. Sie sind **keine strukturelle Obergrenze**. Der
Record enthält für alle 58 materialisierten Ereignisse jeweils 48
`values_hex`-Werte. Ein neutraler Nullwert benötigt acht Zeichen,
ein zulässiger endlicher Halbwert kann 23 Zeichen benötigen. Allein diese
Wertdarstellung kann gegenüber der Messung um `41.760` Byte wachsen.

Der V2-Codec begrenzt seine Vektortabelle dagegen wertunabhängig durch
Binary64-Bitmuster. Die frühere Abschätzung von `206.579` Byte für 116
verschiedene Vektoren setzt jedoch die gemessenen `58.378` Metadatenbyte
voraus und ist deshalb keine Zulassungsobergrenze.

Für eine echte Obergrenze fehlen noch eine explizite Bytegrenze für die 58
Materialisierungsreceipts einschließlich `projection_binding`, die 69
Ereigniszeilen, Übergänge, Hintreceipts sowie Arm-Snapshots. Der reale
Adapter verwendet zwar ein NJ-Ausgabeprofil mit eigener Ausgabegrenze; die
S2-UC-Recordform leitet daraus bislang keine zusammenhängende
Metadatenobergrenze ab.

## Vollständige Reservebilanz

Die neue Bilanz zählt aktuelle Runtime- und Testabhängigkeiten, vorbereitete
Bindungen, Qualifikationssummary/-protokoll/-ergebnis/-budget sowie
Abschlussreserven vollständig. Erfolg, Vorpublikationsfehler und
Nachpublikationsfehler sind Alternativen.

| Alternative | Metadaten | Gemeinsame Hülle | Record | Verifikation | Gesamt |
| --- | ---: | ---: | ---: | ---: | ---: |
| Erfolg, reserviert | 28.374 | 221.319 | 245.760 | 131.072 | 626.525 |
| Recordfehler vor Publikation | 28.374 | 221.319 | 0 | 0 | 249.693 |
| Fehler nach Publikation | 28.374 | 237.703 | 245.760 | 131.072 | 642.909 |

Alle drei Alternativen liegen innerhalb der globalen Klassen- und
Gesamtgrenzen. Die Nachpublikationsalternative reserviert zwei getrennte
Terminalgrößen: Fehlerbeleg und Abschlussbeleg. Der bestehende Runtime-Ledger
zählt jedoch derzeit nur einen `terminal_bytes`-Beitrag. Diese Differenz muss
vor einer Laufzulassung technisch vereinheitlicht und neutral geprüft werden.

Die vollständigen maschinenlesbaren Werte, Referenzen und SHA-256-Bindungen
stehen im
[`s2uc-relaunch-decision-package-v1.json`](../reports/s2uc/closure-preparation/s2uc-relaunch-decision-package-v1.json).

## Vorstartstatus

`BLOCKED_PENDING_STRUCTURAL_METADATA_BOUND`.

Eine neue Vorstartqualifikation wurde nicht ausgeführt, weil weder eine
ausführbare neue Laufidentitätsannahme noch eine Recordmetadatenobergrenze
gebunden ist. Die vorhandene Codec-/Fehlerqualifikation `37/37` bleibt
gültig für ihre eigene Form, ersetzt diese beiden neuen Prüfungen aber nicht.

Der historische Lauf `s2uc-source-comparison-real-20260920-01` bleibt
`NOT_EVALUABLE` und unverändert.

## Aktive Abschlussbindung V14

Die aktuelle, nur für den vorbereiteten neuen Lauf geltende Quellenbindung ist
[`S2UC_RUN_BINDING_20260920_V14.json`](../reports/s2uc/S2UC_RUN_BINDING_20260920_V14.json),
SHA-256 `353915dbdb1fe481f76c5dd4bcbc42582998353d7c243b29232e4115629d94ea`.
Die ausdrücklich zu übergebende finale Bindung liegt unter
[`closure-preparation/S2UC_RUN_BINDING_20260920_FINAL_V14.json`](../reports/s2uc/closure-preparation/S2UC_RUN_BINDING_20260920_FINAL_V14.json),
SHA-256 `7b03764a183e6d571b067a473b420e6ce1d74b51297042f93725de5e6c7a7c84`.

Die Bilanz führt Manifest, finale Bindung, alle aktiven Quell- und Testdateien,
Inventar, Quellenbindung, Qualifikationssummary/-protokoll/-ergebnis, Ledger
und Abschlussreserve als getrennte Beiträge. Erfolg und Fehlerabschluss sind
Alternativen; beim Fehler nach Publikation werden Fehlerbeleg und Abschluss
gleichzeitig gezählt. Ein unterschätzter Einzelbetrag ändert den kanonischen
Ledgerdigest und wird vor jedem Payloadzugriff abgewiesen.

Ein möglicher, weiterhin nicht ausgeführter Start verwendet den expliziten
Pfad: `python -c "from pathlib import Path; from tools import s2uc_run_bound_once as s; s.start(Path('reports/s2uc-source-comparison-real-20260920-02'), authorize=True, binding_file=Path('reports/s2uc/closure-preparation/S2UC_RUN_BINDING_20260920_FINAL_V14.json'))"`.
