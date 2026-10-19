# S2-TY: Ausführungsbindung des begrenzten Quellenanschlussversuchs

Stand: 2026-09-20. Dokumentkennung: `S2TY-REAL-CONNECTION-BINDING-20260920-01`.
Dies ist eine statische Ausführungsbindung, keine Lauf-ID und keine Hauptlauffreigabe. Es wurden keine NU-/TW-PCM-Payloads erzeugt, gelesen oder analysiert.

## Gebundener Einstieg

Der spätere Einmalaufruf hat genau diese Reihenfolge:

1. `tools._s2ty_source_time_binding.source_manifest()` erstellt das gebundene Manifest mit 26 Ereignissen.
2. `tools._s2ty_real_source_supplier.create_payload_supplier(manifest)` löst ausschließlich die im Manifest referenzierten NU-Quellen auf. Es öffnet beim Binden keine Payload.
3. `tools._s2ty_run_envelope.run_materialized_once(...)` fordert je Endpoint genau ein Fenster an, prüft den Payloadhash vor `analyze`, führt genau einen Rezeptoraufruf und eine NJ-Projektion aus und gibt dasselbe Halbprofil an die getrennten Arme `adapter` und `direct` weiter.
4. `tools._s2ty_real_run_entry.run_bound_once(...)` prüft die externe, eingefrorene `run-binding.json`, die Ausgabeabwesenheit und alle aktiven Referenzen. Es publiziert genau einmal `envelope.json`, führt danach die äußere read-only Gesamtverifikation aus und publiziert deren Ergebnis getrennt.
5. Erst bei erfolgreicher äußerer Verifikation liest `tools._s2ty_evaluation.evaluate_verified(...)` die Entscheidungen und publiziert `evaluation.json`. `closure.json` hält den technischen Abschluss fest.

Der Supplier akzeptiert nur die im Quellenplan enthaltene Kombination aus Ereignisordinal, Endpoint, Profil, Hash und nativer Zeit. Eine vertauschte oder erfundene Endpointbindung scheitert vor der Fenstererzeugung. Das native `bytearray` des NU-Generators wird ohne zusätzliche vollständige PCM-Kopie an die bestehende Materialisierung übergeben und anschließend im Hüllenpfad freigegeben.

## Ereignis- und Zeitbindung

| Größe | Bindung |
|---|---:|
| Ereignisse | 26 |
| Audio-/NJ-Endpunkte | 22 |
| Formationen | 16 |
| Hinteilfenster | 6 |
| Hinweise pro Arm | 3 |
| Segmentabschlüsse pro Arm | 4 |
| Owners | `adapter`, `direct`, getrennt |
| Logische Runtimezeit | Ordinal `1..26` auf Zeit `0..25`; Owner-Close auf `26`, `27` |
| Native Audiotime | unverändert aus `nu-s02-w00..w04`, jeweils `start = snapshot_index * 480` |

Die Quelle wird in der vorgebundenen Reihenfolge `p1`, `p2`, `h1`, `p3`, `h2`, `p4`, `h3` verwendet. Wiederkehrende Quell-IDs werden nicht dedupliziert: jede der 22 Endpointforderungen erzeugt und verarbeitet ihr eigenes PCM-Fenster. Die Runtimezeit läuft nur logisch vorwärts; die native Quellenzeit bleibt die im NU-Plan gebundene Zeit und wird nicht umgerechnet.

## Vorab gebundene fachliche Kriterien

Die technische Prüfung verlangt Adapter-/Direktgleichheit nach jedem Ereignis, getrennte Owner-Abschlüsse, vollständige Receipts und die unabhängige Direktnachrechnung. Die spätere fachliche Auswertung berichtet diese Befunde getrennt; sie darf keinen neuen Scan oder eine erneute Materialisierung auslösen:

| Hinweis | Zu prüfender Befund |
|---|---|
| `h1` mit `b,c` | eindeutiger Treffer der Generation 1 nach `p1` und exakter Bestätigung durch `p2` |
| `h2` mit `d,c` | eindeutiger Treffer der Generation 2 nach `p3` |
| `h3` mit `d,a` | negative Hinweiskontrolle: `ABSTAIN_NO_RETAINED_TRACE` |

`p2` muss `TRACE_CONFIRMED` für Generation 1 liefern: keine zusätzliche Belegung und keine Verjüngung der FIFO-Position. `p3` bildet Generation 2; `p4` bildet Generation 3 und verdrängt Generation 1. Die Verdrängung wird durch diese Übergangs- und Inventarbelege nachgewiesen, nicht durch die Enthaltung bei `h3` allein. Diese Kriterien sind keine Behauptung über Quellenidentität, Lernen, biologische Aufbewahrung oder Variantenbindung.

## Aktive Bindungen

| Datei | SHA-256 |
|---|---|
| `reports/s2nu/s2nu-source-preseal-20260909-01/execution-plan.json` | `6e64fbd5b7e86f16156b6d68bd5f7dbda3fefa8f223b2a31114bf3293eaa5f10` |
| `tools/_s2nu_private_source_binding.py` | `8e0fa79f3ce66ce4228f46a52252de5d207c6cee29fefc42f957aa41dc56bce6` |
| `tools/_s2ts_temporal_trace_run.py` | `e084f2aa6806337587284df6873068b6366e88eea2f02fc11bc981c143f8387a` |
| `tools/_s2tw_source_schedule.py` | `3e8f37ab8675da0a1f34bc14a6bd561fd111d48906728b4df99e5cd429c97cf4` |
| `tools/_s2ty_source_time_binding.py` | `eaa6b4aa18d14c03356a093f496a827d4c087be3a3932965800b5b175d4823ab` |
| `tools/_s2ty_real_source_supplier.py` | `64cc1be4ab211787c1ace93de7520fed38d39f5ddc247a3fe783d682be2c9cdc` |
| `tools/_s2ty_audio_materialization.py` | `c332b1eccff35aefc0dbea27c4db78e5b97524ed2f46ab7a6461e3bcc522db72` |
| `tools/_s2ty_run_envelope.py` | `151f4f08c2141bd0ffb3b69e183a3a8bb20bbd32acc863b48cc0da016347866b` |
| `tools/_s2ty_evaluation.py` | `905507dd22f883f822546e95103cdd8063d0b9c85ca2ff9125c07edfd348357d` |
| `tools/_s2ty_real_run_entry.py` | `905f272a466b27c4e75fa5e69bca9cb60aa97ed5f378b875b103345e1863fe11` |
| `tools/_s2ty_record_verification.py` | `18af82bc9aa36cc23ca50c762ca90e255f514905c1b7c054c7fc5110e3503160` |
| `tools/_s2ty_resource_ledger.py` | `9c39435dd15db76fbb41090e4073cd2e608d911772595ea123b40eba92e731f1` |
| `reports/s2ty/s2ty-neutral-overall-qualification-20260920-03/qualification-result.json` | `dce17b722f70ab1cb9cb80891cb79d55058eec21144026338bde13826d7c4066` |

Die vollständige Laufhülle bindet zusätzlich die von `tools._s2ty_run_envelope.code_hashes()` erfassten Core-, Rezeptor- und Hearing-Path-Dateien. Der spätere Start muss deren aktuelle Hashmap exakt gegen die vor dem Start erzeugte Bindung prüfen.

## Bilanz und Grenze

Die S2-TY-Ledgerform zählt Erfolgs- und Fehlerabschluss als Alternativen:

| Beitrag | Gebundener Wert |
|---|---:|
| Quellenmanifest | 8.061 Byte |
| aktive Code-, Test-, Quellen- und Qualifikationsreferenzen | 210.114 Byte, vollständig als gemeinsame Zusatzhülle gezählt |
| Metadatenreserve | 8.192 Byte von 65.536 |
| gemeinsame Zusatzhülle | 210.114 Byte von 262.144 |
| Erfolg **oder** Fehlerpublikation | 196.608 Byte von 262.144 |
| terminaler Fehlerbeleg | 8.192 Byte, zusätzlich zur Fehlerpublikation innerhalb der 262.144-Byte-Recordgrenze reserviert |
| Verifikationsreserve | 32.768 Byte von 262.144 |
| Erfolgsalternative | 455.743 Byte von 4.194.304 |
| Fehleralternative einschließlich Terminalreserve | 463.935 Byte von 4.194.304 |
| gebundener nativer MCM-Payload | 39.936 Byte von 98.304 |

Die neutrale Erfolgsbeobachtung von `105.819` Record-Byte ist keine Obergrenze für die reale Hülle. Der Starter serialisiert daher vor jeder Veröffentlichung `envelope.json`, `outer-verification.json`, gegebenenfalls `evaluation.json` und `closure.json` und bilanziert deren tatsächliche Bytes. Bei Überschreitung entsteht eine typisierte Fehlerhülle mit Artefaktteilbeträgen, Summe, Grenze, Phase `CLOSURE_BUDGET` und Materialisierungsfortschritt. Passt auch diese vollständige Fehlerhülle nicht, wird ausschließlich `terminal-error.json` aus der separaten Reserve veröffentlicht. Dieser Beleg nennt Größe und Digest aller nicht publizierten Artefakte und markiert `evidence_complete=false`; er behauptet keine vollständige Sicherung. Bereits veröffentlichte Belege werden nie überschrieben. Beide Abschlussformen werden nicht addiert.

Eine formale Prozessspeicherobergrenze besteht im aktiven S2-TY-Vertrag nicht. Der Ledger weist nur die native MCM-Nutzlast sowie bekannte Materialisierer-Untergrenzen aus (`979.592` Byte Rezeptorkonfiguration und `1.939.992` Byte FFT-Arbeitsraum). Python-Administration und NumPy-Temporäre sind dort ausdrücklich `NOT_STATICALLY_BOUNDED`. Das ist keine Neuinterpretation von Payload- oder Artefaktgrenzen und keine universelle RAM-Garantie.

## Neutrale Anschlussprüfung und verbleibende Sperre

Die neue fokussierte Prüfung `s2ty-real-entry-qualification-20260920-04` führte einmal `30/30` Tests mit Exit-Code `0` aus: `tests.test_s2ty_real_source_supplier`, `tests.test_s2ty_evaluation`, `tests.test_s2ty_run_envelope` und `tests.test_s2ty_real_run_entry`. Sie nutzte ausschließlich neutrale In-Memory-Fenster. Sie prüfte die Lazy-Bindung, vertauschte Endpoints vor Payloadzugriff, die native `bytearray`-Übergabe durch den neutralen Rezeptor-/NJ-Pfad, die Vorbilanz, vorhandene Ausgabe, Materialisierungsabbruch, Lieferanteninitialisierung nach Ausgabeanlage, getrennte Ausführungsfehler mit unbekanntem Fortschritt, äußere Verifikationssperre, Auswertungsfehler, Istüberschreitung beider vollständigen Reserven, terminalen Fehlerabschluss, Auswertungssperre und Gate-Rücksetzung. Die historische 49er-Gesamtqualifikation bleibt an ihren damaligen Hashes gebunden; sie wird nicht als neue Prüfung der geänderten Dateien ausgegeben.

Die aktive, unverbrauchte Bindung liegt in [run-binding.json](../reports/s2ty/s2ty-temporal-confirmation-retention-real-20260920-01-binding-03/run-binding.json): Laufname `s2ty-temporal-confirmation-retention-real-20260920-01`, Bindungsdigest `f60010d915fbed11ac2e43d4d9e3da9304f04b2002b33af78bd4cf2d2a928d1d`, Dateihash `8c0443755d11f1b441aee7fd47406fc3d09b1809e1cc14b972f0173c3ec1d8a2`. Der Startbefehl ist erst nach expliziter Einmallaufautorisierung zulässig:

```powershell
Set-Location C:\Users\TV\Documents\MCM_FIELD_ORGANISM\workspace
# Autorisierter Aufrufer setzt tools._s2ty_real_run_entry.MAIN_GATE nur für diesen Prozess auf True.
python -c "from pathlib import Path; from tools import _s2ty_real_run_entry as e; e.MAIN_GATE=True; print(e.run_bound_once(Path('reports/s2ty/s2ty-temporal-confirmation-retention-real-20260920-01-binding-03/run-binding.json'), Path('reports/s2ty/s2ty-temporal-confirmation-retention-real-20260920-01')))"
```

Diese Vorstartaussage galt vor der nachfolgenden Einmallauffreigabe. Der
gebundene Befehl wurde danach genau einmal ausgeführt; Ergebnis und Istbilanz
sind im folgenden Abschnitt festgehalten.

## Reeller Anschlussversuch und read-only Nachtrag

Der einmalige Lauf `s2ty-temporal-confirmation-retention-real-20260920-01`
ist technisch abgeschlossen: `26/26` Ereignisse, `22/22/22`
Hash-/Rezeptor-/NJ-Aufrufe, getrennte Owner und äußere Verifikation
`VERIFIED`. Die Ergebnisablage bleibt unverändert. Ihre Istbilanz beträgt
`360.406` Byte; die wiederverwendeten Quellen umfassten tatsächlich
`422.400` gelesene PCM-Byte. Eine allgemeine Prozessspeicherobergrenze bleibt
weiterhin ausdrücklich offen.

Die gespeicherte `evaluation.json` enthält für `h1` und `h2` gleiche
Entscheidungsinhalte wie die Sollwerte, aber `matches_expected=false`. Das
war ein Liste-/Tupel-Darstellungsfehler des Auswerters, kein abweichender
Hintreceipt. Die fokussierte Normalisierungsqualifikation
[`6/6`](../reports/s2ty/s2ty-evaluation-normalization-qualification-20260920-01/qualification-result.json)
bindet die strukturtreue Vergleichskorrektur. Der separate
[read-only Nachtrag](../reports/s2ty/s2ty-temporal-confirmation-retention-real-20260920-01-evaluation-addendum/addendum.json)
referenziert die Originaldateien per Digest, ruft keine technische
Verifikation erneut auf und ergibt `all_expected=true`.

Damit sind technische Hülle, exakte Wiederholungsbestätigung, FIFO-Übergänge
und die drei Hinweisentscheidungen für diese angeschlossene Sequenz getrennt
belegt. Der Umfang bleibt begrenzt: keine Aussage über Variantenlernen,
Quellenidentität, allgemeine Prozessspeichergrenzen oder Video-Erinnerungsnutzen.
