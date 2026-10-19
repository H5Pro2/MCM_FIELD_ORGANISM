# Ergänzender Anschlussnachweis: 17/17

Genau ein fokussierter Aufruf: **17/17 bestanden**, Exitcode 0.
Vollständige Logs: 2.031 Byte. Alle vorgebundenen Quellenhashes danach
unverändert; siehe `preregistration.json` und `result.json`.
Keine Wiederholung der historischen 24 Prüfungen und kein Hauptlauf.

## Tatsächlich geprüft

Autorisierung aller drei Rollen und Abschnitte, fehlende und fremde Zulassung,
veränderte Codebindung, falscher Abschnitt und falsche Rolle, verbrauchte
Rollenmarke, fehlender Hauptverbrauch sowie fremdes Ergebnisverzeichnis.
Beim direkten unautorisierten Workeraufruf wird die Sitzungsfabrik nicht
erreicht. Mit gültiger neutraler Autorisierung wird sie bei geöffnetem Gate
erreicht; ihr absichtlicher Stopp schließt das Gate wieder.

Zusätzlich: formatbezogene Metadatenbeiträge, private Grenzbindung,
gemeinschaftliche Ausschöpfung der Klassen, tatsächliche administrative
Publikation oberhalb der historischen Metadatengrenze sowie Abweisung einer
Übergröße vor dem Schreiben. Der neue Checkpointabschluss benutzt den privaten
Publikationsanschluss, nicht den historischen Publisher.

Die Sitzungsfabrik und der native Checkpointinhalt sind in diesen fokussierten
Kontrollen Testdoubles. **Kein neuer nativer Memory-/Feld- oder Prozess-Restore-
Nachweis wird behauptet.** Dafür bleiben die unveränderten früheren Belege
zuständig. 24/24 plus 17/17 sind getrennte Teilnachweise, kein neuer 41-Test-Lauf.
Die frühere 21/22-Fehlqualifikation bleibt unverändert NOT_QUALIFIED; ihre
separaten vier Ergänzungskontrollen bleiben ebenfalls eigenständige Belege.

## Prospektive Budgetversion

`checkpoint.transfer-entry.v3` / `checkpoint.transfer-budget.v3`:
Metadaten und Quellen jeweils 196.608 Byte, Gesamt einschließlich temporärer
Dateien 5.242.880 Byte. Ausschließlich der private Neustartanschluss verwendet
diese Grenzen. Historische Ledger/Defaults unverändert; kein Monkeypatching.
Feldcheckpointdeckel 524.288 Byte, gemeinsame Zusatzhülle 262.144 Byte und
Verifikationsgrenze 262.144 Byte bleiben erhalten. Keine größere Memory,
kein zusätzlicher Feldraum und keine Prozess-RAM-Freigabe.

Vollständige vorgebundene Laufrechnung:

| Klasse | Schutzobergrenze | Grenze |
|---|---:|---:|
| Metadaten | 138.913 | 196.608 |
| Quellen | 175.789 | 196.608 |
| Gemeinsame Zusatzhülle | 256.685 | 262.144 |
| Gesamt, phasengerecht | 4.293.977 | 5.242.880 |

Die unterschiedlichen Klassenspitzen werden nicht zu einem fiktiven
gleichzeitigen Zustand addiert. Gesamtspitze: `restore-prefix-7` mit
137.316 Byte Metadaten. Alle übrigen Prozess-/Fehleralternativen sind in der
Vorregistrierung enthalten. Qualifikationsdateien, historische aktive
Referenzen und vorbereitete Laufbindung stehen zusätzlich mit ihren
tatsächlichen Beiträgen in `final-balance.json`. Eingangsdateien wurden hier
nicht gelesen oder verarbeitet. Vorrechnung ist keine Laufmessung.

Die Vorbereitungen `...-01`, `...-02` und `...-03` starteten keine Tests.
`...-04` bindet den tatsächlichen einzigen Aufruf einschließlich korrigierter
neutraler Fabrikattribute und gemeinsamer Klassengrenzkontrolle.

## Endgültige Bindung, noch ohne Autorisierung

`reports/memory-restart-transfer-final/settings.json` bindet die unveränderten
sieben Ereignisse je Arm und die aktuelle Quellen-/Qualifikationsdeckung.
SHA-256:
`f089d57448c0a762ed13cc10d9460e5cc53d9ab81b2008dcd9b2f39376e1a8c3`.
Die administrative Bindungsprüfung wurde ausgeführt, nicht der Vergleich.

Lauf-ID `memory-restart-transfer-20260912-01` und Ergebnisablage sind unbenutzt.
Die separate Autorisierung fehlt absichtlich. Erst nach einer Hauptfreigabe
darf sie erstellt und der gebundene Dateieinstieg benutzt werden. Gates False.
