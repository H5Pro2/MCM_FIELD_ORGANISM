# S2-TS: einmaliger auditiver Teilverlauf

Lauf-ID: `s2ts-temporal-trace-real-20260919-01`  
Technischer Status: `RECORDING_COMPLETE`  
Unabhängige Verifikation: `VERIFIED`, einmal read-only.

## Ressourcen und Bindungen

Der Lauf verarbeitete exakt 20 Ereignisse: 18 vorversiegelte NU-
Audioendpunkte, acht Formationen, zehn read-only Hintframes und zwei
Sitzungsabschlüsse. Für jeden Endpunkt erfolgten genau eine Payloadhashprüfung,
eine Rezeptoranalyse und eine NJ-Projektion. Es gab null Feldkontakte, null
A/B-Scans und keine Hypothesenanwendung. Der Record belegt 54.742 Byte und
liegt unter der gebundenen 262.144-Byte-Grenze.

Die vier wiederverwendeten Quellenrollen erzeugten in ihren jeweiligen
Wiederholungen gleiche gespeicherte Wertedigestformen: 18 Endpunkte, vier
verschiedene Halbvektordigests. Dieser Befund wird als beobachtete
Reproduzierbarkeit dokumentiert; es wurde keine Deduplizierung oder Anpassung
vorgenommen.

## Getrennte Funktionsauswertung

| Hintabschluss | Spurentscheidung | Inhaltliche Einzel-/Multisetbaseline |
| --- | --- | --- |
| e06: `b,c` in S1 | `TRACE_MATCH`, Offset 1 | beide Werte vorhanden |
| e08: `c,b` in S1 | `ABSTAIN_ORDER_MISMATCH` | beide Werte vorhanden |
| e10: `a,c` in S1 | `ABSTAIN_ORDER_MISMATCH` | beide Werte vorhanden |
| e13: `b,c` nach S1-Close | `ABSTAIN_NO_TRACE` | keine aktive Spur |
| e19: `a,b` in S2 | `ABSTAIN_AMBIGUOUS_OFFSET`, Offsets 0 und 2 | beide Werte vorhanden |

Damit findet die private Spur den gebundenen Teilverlauf einmal eindeutig,
weist Umkehr und Nichtnachbarschaft trotz gleicher Inhaltsbaselines zurück,
gibt nach Close keine alte Generation aus und enthält beim mehrfachen
Abschnitt. Der Befund gilt nur für exakte, sitzungsgebundene 48-Wert-
Teilfolgen. Er belegt weder Quellenidentität, Variantenrobustheit noch eine
öffentliche A/B-Hypothese.
