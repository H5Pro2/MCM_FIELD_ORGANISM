# S2-UC: Finale Laufbindung, Vorbereitung

Stand: 2026-09-20. Dieses Dokument startet keinen Lauf und erzeugt keine
Quellen. Es bindet ausschließlich den zukünftigen Einmalaufruf.

## Neutrale Codec- und Fehlerabschlusskorrektur

Die historische Recorddarstellung bleibt unverändert lesbar. Für künftige
S2-UC-Records existiert zusätzlich der private Codec
`s2uc.record-codec.v2`: Er speichert Werte als exakte Binary64-Bitmuster,
führt gleiche Wertevektoren nur einmal und bindet Frameidentitäten
(`profile`, `owner`, `segment`, `ordinal`) weiterhin getrennt. Diese
Komprimierung verändert weder Wahrnehmungs- noch Memorywerte.

Der Record wird vor jeder Publikation vollständig serialisiert und gegen
Record- und Gesamtbudget geprüft. Überschreitet der Kandidat eine Grenze,
wird kein `record.json` veröffentlicht. Stattdessen entsteht ein separat auf
`16.384` Byte begrenzter `error.json`-Beleg mit Primärfehler, Phase,
Fortschritt sowie Bytezahl und Digest des verworfenen Kandidaten. Er enthält
den Record nicht und kann daher nicht rekursiv an dessen Überschreitung
scheitern. Ein späterer Abschluss darf diesen Primärfehler nicht ersetzen.

Die einmalige neutrale Qualifikation
`S2UC-CODEC-ERROR-NEUTRAL-QUALIFICATION-20260920-01` bestand mit `37/37`.
Sie öffnete keine realen Payloads. Das vollständige Protokoll, die
Ergebnisreferenz und die Größenrechnung stehen in:

- `reports/s2uc/closure-preparation/codec-error-neutral-protocol-v3.json`
- `reports/s2uc/closure-preparation/codec-error-qualification-result-v3.json`
- `reports/s2uc/closure-preparation/codec-error-budget-v3.json`

Die neutrale vollständige Verbindungsform umfasst `104.939` Byte Record,
`64` Frameidentitäten und `40` gespeicherte Vektoren. Die konservative
Abschätzung für `116` unterschiedliche Vektoren bei der gemessenen
Recordmetadatenform beträgt `206.579` Byte. Sie ist keine Laufzulassung,
weil die Metadatenmessung selbst keine strukturelle Obergrenze bildet. Der
Fehlerbeleg für einen absichtlich übergrenzen Kandidaten misst `345` Byte.
Diese Messung ist keine reale Quellen- oder Funktionsauswertung.

Die nachfolgend referenzierte V6-Endbindung ist historisch und enthält die
vorherige Codec-/Publikationsform. Sie ist nach dieser Korrektur keine aktive
Zulassung; eine spätere reale Laufbindung muss die hier gebundenen aktuellen
Dateihashes und Qualifikationsbelege neu referenzieren.

Die vollständige Neubewertung der Metadaten- und Abschlussgrenzen steht im
[`S2UC_ENTSCHEIDUNGSPAKET_NEUER_EINMALLAUF.md`](S2UC_ENTSCHEIDUNGSPAKET_NEUER_EINMALLAUF.md).

## Vorgesehener Lauf

- Lauf-ID: `s2uc-source-comparison-real-20260920-01`
- Ergebnisablage: `reports/s2uc-source-comparison-real-20260920-01`
- Vorstartbedingung: Die Ablage fehlt; der dateigebundene Einstieg legt sie
  selbst an und verweigert jede bestehende Ablage.
- Eingangsform: die unveränderte S2-UC-Manifestfolge mit drei frischen
  Geschichten, 69 Ereignissen, 58 Audio-/NJ-Endpunkten und 14 Hintframes.
- Quellenzulassung: Der Quellenplan `6e64fbd5b7e86f16156b6d68bd5f7dbda3fefa8f223b2a31114bf3293eaa5f10`,
  sein Execution-Digest
  `1d2787da42fe01e6bb960ad545bcfbf96a3e4abd036ce91033b325c450d7f2c7`
  sowie die für jeden Endpunkt noch separat zu bindenden Payloadhashes.

## Aktive Ausführungsbindungen

Die aktuelle vollständige Dateihülle steht in
`reports/s2uc/closure-preparation/dependency-inventory-v6.json`. Ihre
aufgelöste referenzbasierte Endbindung ist
`reports/s2uc/S2UC_RUN_BINDING_20260920_FINAL_V6.json`. Frühere V1- bis
V6-Quellenbindungen und frühere Finalbindungen bleiben
historische Artefakte und sind keine aktive Zulassung.

Die neutralen Anschlussqualifikationen bestehen aus
`tests.test_s2ub_candidate_confirmation`,
`tests.test_s2uc_neutral_connection` und
`tests.test_s2uc_materialization_connection`. Reale Quellen sind daraus nicht
zugelassen.

Die maschinenlesbare Bindung wird durch `_s2uc_run_binding.py` aus der
vorhandenen `source.source_rows()`-Ursprungsdatei gebildet und vor einem
späteren Start gegen sich selbst validiert. Sie enthält die Ursprungsdatei
samt Digest, fünf Quellenbindungen und alle 58 Endpunktverwendungen, ohne PCM
zu öffnen.

## Bilanz und Abschlussalternativen

Der Erfolgspfad umfasst Record, technische Verifikation, getrennte
Entscheidungsauswertung und Terminalbeleg. Der Fehlerpfad umfasst Record,
Fortschritt, Primärfehler und technischen Fehlerbeleg. Falls dessen vollständige
Hülle nicht innerhalb der Grenzen liegt, kann ausschließlich der begrenzte
Ersatzbeleg `terminal-minimal.json` mit Primärfehler, Fortschritt, Grund,
Dateireferenzen und Größen-/Digestwerten entstehen.

Gebunden bleiben Recordreserve `245.760` Byte, absolute Recordgrenze `262.144`
Byte, aktive Bindungsreserve `131.072` Byte, Verifikationsreserve `131.072`
Byte, Terminalreserve `16.384` Byte, Sharedgrenze `262.144` Byte und
Gesamtgrenze `4.194.304` Byte. Die tatsächliche Bilanz wird erst auf den
gespeicherten Bytes des späteren Laufs bestimmt.

## Korrigierte administrative Bilanz

Die frühere Metadatenrechnung addierte eine eingebettete Finalbindung und
eine nicht erzeugte Qualifikationsreserve zu den Sitzungsmetadaten. Das ergab
fälschlich `111.435 / 65.536` Byte. Die aktuelle Bindung speichert den
vollständigen Quellenvertrag genau einmal als referenzierte Datei; Pfad,
Bytezahl und SHA-256 werden beim Laden aufgelöst und geprüft.

Die aktuelle Vorbilanz steht in
`reports/s2uc/closure-preparation/budget-v6.json`:

- Metadaten: `28.073 / 65.536` Byte.
- Gemeinsame Zusatzhülle: `194.116 / 262.144` Byte, einschließlich der
  Terminalreserve von `16.384` Byte.
- Erfolg und Fehler sind Alternativen, jeweils `599.021 / 4.194.304` Byte.
- Der Ersatzabschluss ist der separate Minimalzweig mit
  `467.949 / 4.194.304` Byte und zählt eine bereits veröffentlichte
  Recorddatei konservativ mit.

Der referenzbasierte Finalformat-Test lief neutral mit `21/21` Tests. Sein
kompakter Befund liegt unter
`reports/s2uc/closure-preparation/finalformat-neutral-test-v4.json`; das
vollständige Prüfprotokoll liegt zusätzlich unter
`reports/s2uc/closure-preparation/finalformat-neutral-protocol-v3.json`.
Beide werden samt Codebindungen vor dem Start aufgelöst. Das Verfahren öffnete
keine realen Quellen und ist keine Ausführungsfreigabe.

## Erwartungen und Aussagegrenze

Die sieben Erwartungsschlüssel sind fest an `(Geschichte, globales
Hintordinal)` gebunden: `g1/12`, `g1/24`, `g1/26`, `g2/38`, `g3/60`, `g3/67`
und `g3/69`. Ihre erwarteten Armentscheidungen sind im unveränderten
`_s2uc_evaluation.py` hinterlegt und werden nicht aus Laufergebnissen
abgeleitet.

Eine Zielherkunft für jeden erwarteten Abruf ist noch nicht separat gebunden.
Der spätere Bericht darf deshalb Unterschiede ausschließlich als
Entscheidungswechsel ausweisen, nicht als fachlichen Gewinn oder Verlust.
Eine reale Ausführungsfreigabe erfordert zusätzlich die Payloadhashbindung und
gegebenenfalls diese Zielherkunft.
