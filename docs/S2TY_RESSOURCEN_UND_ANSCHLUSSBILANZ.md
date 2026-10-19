# S2-TY: Ressourcen- und Anschlussbilanz

Stand: 2026-09-20. Diese Bilanz bindet die prospektive S2-TY-Quellenform und
neutrale Laufhüllen, aber keinen realen Quellenlauf.

## Abnahme der neutralen Verifikation

Die betroffenen Testmodule wurden mit `python -B -m unittest
tests.test_s2ty_event_control tests.test_s2ty_record_verification -v`
ausgeführt. Die folgenden 14 Test-IDs bestanden mit Exit-Code `0`:

- `Tests.test_complete`
- `Tests.test_primary_error`
- `Tests.test_owner_close_failure_without_primary_error_closes_direct_owner`
- `Tests.test_owner_close_failure_preserves_primary_error_and_closes_direct_owner`
- `Tests.test_full_flow`
- `Tests.test_manipulated_receipts_and_inventory_fail`
- `Tests.test_order_and_status_fail`
- `Tests.test_inner_success_status_mismatch_is_rejected`
- `Tests.test_exact_confirmation_keeps_generation_and_fifo_position`
- `Tests.test_direct_hint_decision_before_eviction_is_verified`
- `Tests.test_eviction_manipulation_fails`
- `Tests.test_duplicate_owner_arm_is_rejected`
- `Tests.test_missing_owner_arm_is_rejected`
- `Tests.test_unknown_owner_arm_is_rejected`

Die Budgettests wurden anschließend im selben Aufruf erreicht:

- `Tests.test_planned_shape_has_bounded_dual_arm_native_peak`
- `Tests.test_success_and_failure_records_are_alternative_envelopes`
- `Tests.test_source_binding_is_required_before_a_run_budget_can_pass`
- `Tests.test_boundary_and_overflow_report_full_failure_contributions`
- `Tests.test_global_limit_is_enforced_when_local_classes_fit`

Code- und Testbindungen dieses Stands:

| Datei | SHA-256 |
| --- | --- |
| `tools/_s2ty_event_control.py` | `df395160eff9978ca992de19d5bd4db8dad8c8a155a4e345c6002e2100d1ada9` |
| `tools/_s2ty_record_verification.py` | `18af82bc9aa36cc23ca50c762ca90e255f514905c1b7c054c7fc5110e3503160` |
| `tools/_s2ty_failure_verification.py` | `563645efda35eec015fb4b53b3f4bf9ad2c5f8e4bcfb25964dddfe3daf705e51` |
| `tools/_s2ty_resource_ledger.py` | `9c39435dd15db76fbb41090e4073cd2e608d911772595ea123b40eba92e731f1` |
| `tools/_s2ty_source_time_binding.py` | `eaa6b4aa18d14c03356a093f496a827d4c087be3a3932965800b5b175d4823ab` |
| `tools/_s2ty_run_envelope.py` | `e57305a5c9626e2f92fba5baa9474eaaa4fc20dc3691801c583abee8d93c13b6` |
| `tools/_s2ty_audio_materialization.py` | `3e2f7e5e0d74585d7e6ac13844406612e55c048b1a8a052294bee9a1e9104174` |
| `tools/_s2nj_private_auditory_output_projection.py` | `e052cc76cf4c9678e11673d95390dea21634bba8082187567a760faaaf4904e5` |
| `mcm_field_organism/log_spectral_receptor.py` | `26a6bd8f2d190db60c75ad29f275b3bd8b09b6d26d4ad54e4396176c4a36d2b0` |
| `mcm_field_organism/broadband_hearing_path.py` | `a20456b24c04d099ba5ee2da6250e3d83dc657392603c41d816b13ca68a37fb7` |
| `tools/_s2ty_perception_trace_adapter.py` | `d15af744f691142befbede6b2e1a28eea93232d2d5d57142caf7611d09ffd47b` |
| `tools/_s2tu_retained_trace.py` | `bf530380f93c8a1bf0eeae5a4169e81bc99aee10050872e3e5ddc7bfdb88f3f6` |
| `tools/_s2tw_exact_confirmation.py` | `90470980a329d0424bec9ba430adbbccaf72bb82145edfefd6e491b6fcec7be9` |
| `tools/_s2tw_source_schedule.py` | `3e8f37ab8675da0a1f34bc14a6bd561fd111d48906728b4df99e5cd429c97cf4` |
| `tools/_s2ts_temporal_trace_run.py` | `e084f2aa6806337587284df6873068b6366e88eea2f02fc11bc981c143f8387a` |
| `tools/_s2ts_temporal_trace.py` | `64d1e7f9ff54d898996974d960bfb58ac7386165846aeec0ea253079e0a8e6d8` |
| `tests/test_s2ty_event_control.py` | `d31459a8eae4a35603f944fc67c374d30661fb906e04d6218db9400766c64259` |
| `tests/test_s2ty_record_verification.py` | `3e80a904b08597b3627c94e560596412a811e4d274510b2057f35bfeff7a69b9` |
| `tests/test_s2ty_resource_ledger.py` | `2cbf774ff8d7ae99114c143a90fdc3e7d68ffe5761570f06acf74ff1a8b036be` |
| `tests/test_s2ty_failure_verification.py` | `9f4409ae8bdfa8c63a469b7af3ca82c1c6515c814a507e6cd0500092bcca4413` |
| `tests/test_s2ty_source_time_binding.py` | `f71f7fce8a96ddd91bf3ed018fb9b57f227d51ad943ae2c2c030320595465f2d` |
| `tests/test_s2ty_run_envelope.py` | `9fd5f130c4777c160d06a738098f3420f0539248dad1d4faf47180196cf7e97d` |
| `tests/test_s2ty_formal_qualification_starter.py` | `4d68dc9f47bc3f57396f91db8d506c699b9f0dcb251432ef5cabd63bbf6303b2` |
| `reports/s2ty/qualify_s2ty_neutral_once.py` | `7c4ab353e0820deb340007202716b1eb0f1602c62c73d70611b0bf678428b4f6` |

Dieser Text ersetzt keine Quellen-, Zeit- oder Fehlerpfadqualifikation.

## Vorgesehene Form

Die bisherige S2-TW-Folge liefert ausschließlich die Form der vorgesehenen
S2-TY-Hülle: 26 Ereignisse, 22 vorverarbeitete NJ-Endpunkte, 16
Formationsframes, sechs Hintframes und vier Segmentabschlüsse. Beide Arme
erhalten denselben Endpunkt: der Adapter und der direkte S2-TW-Store.
Die konkrete Quellen-/Zeitbindung ist weiter unten getrennt beschrieben.

| Native Float64-Nutzlast am Übergabepunkt | Byte |
| --- | ---: |
| Adapter: zwei gehaltene Vierframe-Spuren | 3.072 |
| Direkter Arm: zwei gehaltene Vierframe-Spuren | 3.072 |
| Beide Formationspuffer | 3.072 |
| Beide Hintpuffer | 1.536 |
| NJ-Endpunkt und zwei Übergabereferenzen | 1.152 |
| Ein PCM-Fenster (`4800` Float32-Samples) | 19.200 |
| Ein roher Rezeptorendpunkt | 384 |
| Warteschlange der 22 bereits materialisierten Halbendpunkte | 8.448 |
| Summe Werte-/Materialisierungsnutzlast | 39.936 |
| Bestehende Zustandsgrenze | 98.304 |

Diese Zahl beschreibt die begrenzte MCM-Nutzlast einschließlich eines PCM-Fensters
und sämtlicher bis zum Trace-Bau gehaltener Halbendpunkte. Der Lieferant übergibt
jeweils nur ein Payload; eine 22er-PCM-Liste wird nicht im Runner gehalten.

Die Rezeptorimplementierung hat davon getrennte bekannte NumPy-Anteile:
`979.592` Byte Rezeptorkonfiguration und mindestens `1.939.992` Byte
FFT-Arbeitsarrays. Python-Objektverwaltung und implementierungsspezifische
NumPy-Temporaries sind nicht statisch begrenzt. Diese Untergrenze ist daher
keine Prozessspitzenmessung und keine zusätzliche S2-TY-Kapazitätsfreigabe.

## Serialisierte Alternativen

Die Ledgerrechnung behandelt vollständigen Erfolgs- und Fehlerabschluss als
Alternativen. Der Ergebnisbeleg und der Fehlerbeleg werden nicht addiert.

| Klasse | Bestehende Grenze |
| --- | ---: |
| Metadaten | 65.536 Byte |
| Gemeinsame Zusatzhülle | 262.144 Byte |
| Ergebnisbeleg je Abschlussalternative | 262.144 Byte |
| Unabhängige Verifikation | 262.144 Byte |
| Gesamt | 4.194.304 Byte |

Der neutrale Ledger prüft Gleichstand und Überschreitung einschließlich aller
Teilsummen, Summe, Grenze und Abschlussalternative. Er lehnt außerdem eine
noch ungebundene Quellenklasse ab. Sein Fehlerbeleg enthält in dieser rein
statischen Vorstartphase zusätzlich `phase = PRESTART` und `progress = 0`.
Eine Fehlerhülle nach tatsächlichem Fortschritt ist weiterhin nicht an reale
Quellen gebunden.

## Fehlerabschluss nach Fortschritt

`_s2ty_event_control.py` zeichnet bei einem Fehler jetzt den letzten
vollständig abgeschlossenen Schritt, das versuchte Ereignis, die getrennten
Rückkehrzähler beider Arme und je einen Zustandssnapshot vor Owner-Close auf.
Der Snapshot enthält Generationen sowie Formations- und Hintpuffergrößen. Ein
zwischen den Armen ausgelöster Fehler kann damit einen bereits veränderten Arm
sichtbar machen.

`_s2ty_failure_verification.py` rechnet die erfolgreiche Präfixfolge mit
einem eigenen Modell nach. Ein zusätzlicher zurückgemeldeter Armschritt
erzwingt den berechneten Nachzustand. Ein Nachzustand bei unverändertem Zähler
ist ausschließlich mit `changed_without_return = true` zulässig. Ergebnis-,
Fehler- und Fortschrittszähler werden gegeneinander geprüft; ein Owner-
Schließfehler verlangt mindestens einen fehlgeschlagenen Abschlussbeleg.

Die Prüfung belegt strukturellen Fortschritt: Generationen sowie Formations-
und Hintpufferlängen. Sie enthält keine vollständigen Vektorzustände und ist
daher kein Nachweis unveränderter Speicherinhalte. Die technische
Ausnahmeursache selbst bleibt `cause_confirmed = false`: Sie ist aus dem
gespeicherten Fehlercode nicht unabhängig beweisbar.

Gemessene vollständige neutrale Fehlerhüllen: `829` Byte vor der ersten
Formation, `5.947` Byte nach fünf vollständig abgeschlossenen Schritten,
`1.968` Byte zwischen den Armen und `859` Byte bei erhaltenem Primärfehler
plus Owner-Schließfehler. Alle vier wurden als jeweilige Fehleralternative
durch den Ledger geführt; die neutrale Quellenklasse beträgt dabei `0` Byte
und ist keine Aussage über einen späteren realen Quellenbestand.

## S2-TW-Quellen- und Zeitbindung

`tools/_s2ty_source_time_binding.py` liest ausschließlich den bereits
versiegelten S2-NU-Quellenplan über die bestehende S2-TW-Planwurzel
`6e64fbd5b7e86f16156b6d68bd5f7dbda3fefa8f223b2a31114bf3293eaa5f10`.
Die daraus gebildete, kanonische S2-TY-Bindung umfasst `26` Ereignisse, `22`
Audioendpunkte, `16` Formationen, `6` Hinweise, `4` Segmentabschlüsse und die
beiden abschließenden Owner `adapter` sowie `direct`. Wiederverwendete Quellen
bleiben Ereignisvorkommen mit eigenen Ordinalen; sie werden nicht dedupliziert.
Die Bindungsdarstellung misst `8.062` Byte und bindet zusätzlich eine
prospektive logische Ereignisuhr: `start = 0`, `tick = 1`, Ereigniszeiten
`0` bis `25` sowie Owner-Abschlusszeiten `26` und `27`.
Der Ledger führt diese Darstellung vollständig als Quellenklasse mit `8.061`
Byte; sie ersetzt keine noch ungemessenen Lauf-, Ergebnis- oder Fehlerbelege.

Jeder Audioendpunkt bindet Quellen-ID, erwarteten PCM-SHA-256, Halbprofil,
nativen NJ-Snapshotindex sowie Fenstergrenzen. Die native Zeitform wird
fail-closed geprüft: `window_start_sample == nj_snapshot_index * 480` und
`window_end_sample == window_start_sample + 4800`. Falscher Payloadhash,
falsches Profil, ungültige native Zeit, fehlender Endpunkt und ungültige
Halbwerte werden typisiert abgewiesen. Für den späteren NJ-Übergang gibt der
Handoff dieselbe einmal erzeugte Halbwert-Tupelinstanz an Adapter und direkten
Store weiter; beide Arme erhalten keine zweite Projektion.

Die logische Uhr ist eine neue, versionierte Verarbeitungsreihenfolge für den
prospektiven S2-TY-Versuch. Sie ist weder historische S2-TW-Zeit noch
gemessene Aufnahmezeit und wird nicht in den NJ-, Frame- oder
Vergleichswertepfad übergeben. Die sechs neutralen Tests prüfen einen gültigen
vollständigen Ablauf sowie fehlende, doppelte, rückläufige und manipulierte
Ereigniszeiten. Damit ist die Quellen-/Zeitbindung positiv qualifiziert; eine
reale S2-TY-Quellenverarbeitung oder ein Hauptlauf ist daraus nicht abgeleitet.

## Neutrale Audio-/NJ-Materialisierung

`tools/_s2ty_audio_materialization.py` verwendet den vorhandenen Pfad
`PCM_F32LE → LogSpectralReceptor.analyze() → S2-NJ-Projektion`. Vor `analyze()`
wird der gemessene SHA-256 des einzelnen PCM-Fensters gegen den Manifestwert
geprüft. Der Receipt bewahrt gemessenen Payloadhash, Bytezahl,
Rohzustandsdigest, Projektdigest, Quellwertedigest sowie Unterlaufmarkierungen;
er speichert kein PCM-Rohpayload. Erst die tatsächlich projizierten Halbwerte
werden an beide S2-TY-Arme übergeben.

Die neutrale Materialisierungsfolge nutzt einen getrennten in-memory
Null-PCM-Quellenbestand mit neu dazu passenden Manifesthashes. Sie verarbeitet
`22` Endpunkte mit genau `22` Hashprüfungen, `22` Rezeptoranalysen und `22`
NJ-Projektionen. Die NU-/TW-Payloads wurden nicht gelesen. Fehler an Hash,
Rezeptor oder NJ schließen vor Memoryverarbeitung ab; ihre Hülle enthält Phase
und direkt an den Aufrufstellen erfasste Zähler. Unabhängige Spies prüfen die
Erfolgsfolge `22/22/22`. Der Hashfehlerfall erreicht `1/0/0`; ein
Quellenlieferfehler nach zwei vollständigen Endpunkten hält zwei vollständige
Receipts und `2/2/2` fest.

`reached_step` beschreibt den tatsächlich erreichten Aufruf der gerade
versuchten Quelle (`NONE`, `HASH`, `ANALYZE` oder `NJ`). Er wird getrennt von
der Fehlerphase verifiziert: Ein ungültiger Nicht-`bytes`-Wert erreicht etwa
`NONE`, ein Fehler vor `analyze()` nur `HASH` und ein Fehler beim Zustandsbau
vor NJ nur `ANALYZE`. Ein statisch abgewiesenes Manifest bleibt ohne erneute
Validierungsschleife als eigener Quellenbindungsbeleg prüfbar. Dagegen wird
ein späterer Steuer- oder Ownerfehler mit vorhandenem Record über den
Fehlerverifikator des Records geprüft, auch wenn die Materialisierung bereits
vollständig dokumentiert ist.

Jeder Receipt enthält die Halbwerte als Binary64-Hex, deren Digest sowie die
Projektionsbindung. Der Verifikator prüft daraus Projektdigest, Profil, native
Zeit, Rohzustands- und Quellwertedigest vollständig gegeneinander; manipulierte
Roh-, Projektions-, Wert- und Profilbindungen werden abgewiesen. Das beweist
die Integrität der gespeicherten Bindung, ersetzt jedoch keine erneute
Rezeptorberechnung und belegt deshalb nicht unabhängig die numerische
Richtigkeit des Rohzustandsdigests.

## Neutrale S2-TY-Laufhülle

`tools/_s2ty_run_envelope.py` bindet eine neue Lauf-ID, zwei unterschiedliche
Armowner, das vollständige Quellenmanifest, Profil, Uhr und die siebzehn
aktiven Codehashes. Seine Eingänge sind ausschließlich neutrale Halbwerte;
der Einstieg materialisiert kein PCM und ruft keinen Rezeptor auf. Vor dem
Steuerpfad werden alle `22` Endpunktbindungen geprüft. Erst danach übergibt
er je Endpunkt dasselbe Halbwert-Tupel an Adapter und direkten Store und
erzeugt den bestehenden Record. Die unabhängige Verifikation liest allein
den serialisierten Record.

Vor jeder Receiptprüfung gleicht sie alle `26` inneren Ereignisse mit dem
äußeren Manifest ab: Anzahl, Reihenfolge, Ordinal, Ereignisart und Segment
einschließlich aller Close-Ereignisse. Ein intern konsistenter, aber anders
zugeordneter Verlauf wird damit nicht akzeptiert.

`neutral_inputs()` kopiert dafür die erwarteten Payloadhashes aus dem
Manifest. Diese Hashes sind Fixturebindungen, keine vor Analyse gemessenen
PCM-Hashprüfungen; die neutrale Hülle belegt daher keine reale
Payloadintegrität.

Ein Quellen- oder Zeitfehler beendet die Hülle vor der Ereignissteuerung.
Sein Fehlerbeleg enthält Fehlercode, Phase `SOURCE_BINDING`, letzten
vollständig geprüften Endpunkt, versuchtes Ereignis und beide Armfortschritte
(`0`/`0`). Nach einer abgewiesenen Bindung existiert kein Record und kein
Memory- oder Scanfortschritt. Manipulierte Code- oder Ownerbindungen werden
ebenfalls abgewiesen.

`same_instance = true` ist ausschließlich ein Laufzeitbeleg der Handoff-API.
Nach der Serialisierung bestätigt die unabhängige Prüfung keine
Python-Objektidentität, sondern Wertedigest und vollständige Bindungsgleichheit.

Die sieben neuen Gesamtketten-Tests sind:

- `Tests.test_complete_neutral_chain_has_distinct_owners_and_independent_verification`
- `Tests.test_source_failure_stops_before_event_control_with_endpoint_progress`
- `Tests.test_time_failure_stops_before_event_control`
- `Tests.test_code_binding_and_distinct_owners_are_required`
- `Tests.test_envelope_manipulation_is_rejected`
- `Tests.test_swapped_endpoint_and_invented_source_failure_are_rejected`
- `Tests.test_control_failure_after_direct_arm_progress_uses_failure_verifier`
- `Tests.test_materialized_neutral_chain_records_hash_receptor_and_nj_calls`
- `Tests.test_materialized_hash_receptor_and_nj_failures_stop_before_memory`
- `Tests.test_materialized_source_failure_keeps_prior_receipts_and_direct_counts`
- `Tests.test_materialization_receipt_digest_bindings_reject_manipulation`
- `Tests.test_materialization_failure_counts_follow_direct_call_steps_not_phase`
- `Tests.test_materialized_manifest_failure_is_verified_without_revalidation_escape`
- `Tests.test_materialized_control_failure_uses_record_failure_verifier`

Der vollständige neutrale Aufruf der vierzehn Gesamtketten-Tests plus der
referenzierten S2-TY-Teiltests bestand mit `35/35`. Zusammen mit den zuvor
abgeschlossenen Teilnachweisen umfasst die aktuelle neutrale Testdeckung
`49/49`; sie ist
keine formale Gesamtqualifikation und keine Laufzulassung.

Die tatsächlichen neutralen Hüllen messen `48.373` Byte im Erfolgs- und
`12.820` Byte im Halbwert-Quellenfehlerfall; die materialisierte Erfolgsform
misst nach vollständiger Receiptbindung `105.817` Byte. Die lokale
Recordreserve beträgt deshalb `131.072` Byte; `Ist ≤ Reserve` wird neutral
geprüft. Der
Ledger setzt für die künftige Hülle
alternativ `8.192` Byte Metadaten, `8.192` Byte gemeinsame Zusatzhülle,
`131.072` Byte Record und `32.768` Byte Verifikation an. Beide reservierten
Alternativen ergeben `188.286` Byte und bleiben unter den bestehenden
Klassen- und Gesamtgrenzen. Diese Zahlen umfassen Quellenmanifest und
Abschlussreferenzen, sind aber neutrale Dateigrößen und keine Prognose realer
Laufartefakte.

## Formale neutrale Gesamtqualifikation

Die einmalige Gesamtqualifikation
[`s2ty-neutral-overall-qualification-20260920-03`](../reports/s2ty/s2ty-neutral-overall-qualification-20260920-03/REPORT.md)
ist `QUALIFIED`: `49/49` vorab gebundene Test-IDs, Exit-Code `0`, vollständige
ID-Gleichheit und unveränderte Code-/Testhashes vor und nach dem Aufruf.
Die Ablage enthält Plan, vollständiges `unittest`-Protokoll, beide Hashlisten,
Materialisierungsbeobachtung und Ergebnis. Ihre Dateien belegen zusammen
`35.381` Byte einschließlich Ergebnisdatei.

Die beobachtete neutrale Erfolgsform hält `22/22/22` Hash-/Rezeptor-/NJ-Aufrufe
fest. Ihr Record misst `105.819 / 131.072` Byte; die Erfolgsalternative
einschließlich Quellen- und Verifikationsanteil misst `113.930` Byte. Die
MCM-Nutzlast bleibt `39.936 / 98.304` Byte. Bekannte Rezeptorkonfiguration
und FFT-Arbeitsuntergrenze werden getrennt dokumentiert. Python- und
NumPy-Prozessverwaltung bleibt `NOT_STATICALLY_BOUNDED`; sie ist weder
qualifiziert noch als eingehaltene Prozessspitze behauptet.

Die vorherigen Kennungen `...-01` (Vorstartfehler) und `...-02`
(fehlerhafte ID-Auswertung) bleiben unverändert `NOT_QUALIFIED`. Die formale
Qualifikation verwendet keine NU-/TW-Payloads und ist keine Hauptlauffreigabe.

## Anschlusszuordnung und Lücken

| Laufkomponente | Vorhandene Implementierung | Prüfdeckung | Offene Bindung |
| --- | --- | --- | --- |
| NJ-Halbwerte zu Trace | `tools/_s2ty_perception_trace_adapter.py` | Adaptertests | vollständiger Laufreceipt |
| Quellen- und Zeitbindung | `tools/_s2ty_source_time_binding.py` | sechs neutrale Bindungstests | Laufowner und Ergebnisrecord |
| Neutrale Laufhülle | `tools/_s2ty_run_envelope.py` | vierzehn Gesamtketten-Tests | reale Quellen- und Ergebnisgrößen |
| Audio-/NJ-Materialisierung | `tools/_s2ty_audio_materialization.py` | sieben neutrale Anschluss-Tests | reale Quellenmaterialisierung, Prozessspitze |
| Direkter Vergleichsarm | `tools/_s2tw_exact_confirmation.py` | S2-TY-Recordtests | Laufowner und Armreceipt |
| Ereignissteuerung und Ownerabschluss | `tools/_s2ty_event_control.py` | 14 neutrale Tests | Fehlerabschlussrecord |
| Erfolgsrecord | `tools/_s2ty_record.py` | Roundtrip und unabhängiger Verifikator | Lauf-ID, Ergebnisse, Quellenreferenzen |
| Erfolgsverifikation | `tools/_s2ty_record_verification.py` | Receipt-, Inventar- und Hintmanipulation | keine vollständige Fehlerrecord-Verifikation |
| Fehlerverifikation | `tools/_s2ty_failure_verification.py` | Präfix-, Arm-, Owner- und Manipulationsfälle | Quellen-/Zeitfehler nicht gebunden |
| Ressourcenrechnung | `tools/_s2ty_resource_ledger.py` | Grenz- und Alternativtests | tatsächliche Dateigrößen und Quellenklasse |

Ein späterer Lauf ist deshalb noch nicht statisch budgetgesichert: Es fehlen
reale Quellen- und Ergebnisgrößen. Die Fehlerverifikation prüft die neutrale
Form, aber noch keinen quellen- oder zeitgebundenen Fehlerabschluss mit
tatsächlich verarbeitetem Fortschritt.
