# Begrenzten OC-Sitzungseinstieg bedienen

Stand: 2026-09-11, Schnittstellen am Arbeitsbaum zu Commit
`537109994cf777f8d36cda617aafe12226806c25` gelesen. Maßgeblich für einen Lauf
ist das qualifizierte Codeinventar, nicht der Commit allein. Diese Anleitung
erteilt keine Laufbefugnis. Gates bleiben `False`.

## 1. Eingaben vorbereiten

Der private Anschluss verarbeitet eine vorab vollständig gebundene Dateifolge,
keinen Liveeingang. Akzeptiert werden:

| Eingabe | Verbindliche Form |
| --- | --- |
| PCM | Rohbytes ohne WAV-Header: 4.800 Mono-Samples, Float32 Little-Endian (`<f4`), 19.200 Byte; 48 kHz, 100 ms; endlich und im Bereich `[-1,1]`. |
| RGB | Rohbytes ohne PNG-/JPEG-Header: `uint8`, Form `(1080,1920,3)`, RGB-Kanalfolge, 6.220.800 Byte. |
| Vollständige AV-Wahrnehmung | Je ein PCM- und RGB-Payload; Ereignistyp `COMPLETE_AV_PERCEPTION`. |
| Auditiver Hinweis | Nur PCM; `PARTIAL_AUDITORY_CUE`; feste auditive Sicht, keine freie Maskenwahl. |
| Visueller Hinweis | Nur RGB; `PARTIAL_VISUAL_CUE`; bereits vor Analyse okkludiert: beobachtet werden visuelle Indizes 0–31. Für Indizes 32–287 müssen die zugehörigen Kanalflächen null sein. Raster: 8×12 Zellen à 135×160 Pixel, je drei Kanäle. |

Dateipfade sind relativ zu `workspace`, müssen darin verbleiben und werden
nicht automatisch konvertiert. Jede Payloadbindung enthält `source_id`, `path`,
`sha256`, `byte_count`. Quellen-IDs sind je Manifestvorkommen eindeutig;
dieselben unveränderten Dateibytes dürfen mit getrennten Bindungen wiederkehren.
Sie werden dann erneut gelesen und analysiert, nicht dedupliziert.
IDs für Lauf, Ereignisse und Quellen erfüllen `[a-z][a-z0-9-]{7,79}`;
Ereignis-IDs sind eindeutig. Kurze Planbezeichnungen wie `e01` allein genügen nicht.

**Zeitbindung ist nicht frei:** Für Ereignisordinal `n` ab 1 gilt `g = n-1`.
Alle Werte sind ganzzahlig; fehlende Modalitäten tragen `None` bzw. JSON `null`.

| Manifestfeld | Exakte Bindung |
| --- | --- |
| `audio_window`, `audio_index` | `(9600*g, 9600*g+4800)` in Samples; nativer Index `20*g` |
| `audio_common` | `(200000000*g, 200000000*g+100000000)` |
| `visual_window` | `(6*g+2, 6*g+3)` in Videoticks bei 30 Hz |
| `visual_common` | `((6*g+2)*1000000000//30, 200000000*g+100000000)` |
| `field_window` | `(0,100000000)` bei `g=0`, sonst `(200000000*g-100000000,200000000*g+100000000)` |

Gemeinsame Zeiten sind Nanosekunden der expliziten Uhr `s2ob-caller-field-clock`.
Wartezeiten zwischen Aufrufen verschieben keine Ereigniszeit.
Quelle: [Payload/Event/Manifest, expected_times, validate_manifest und Materializer](../tools/_s2ob_private_caller_binding.py), Zeilen 59–264.

## 2. Manifest, Zulassung und Budget binden

Vor jeder Analyse werden `Event`-Objekte mit `Payload`-Bindungen zu einem
unveränderlichen `Manifest` zusammengefasst. Vorhandene Schnittstellen sind
`build_manifest(run_id, events, code_digest)` und `decode_manifest(value)`.
Schema ist `s2ob.caller.v2`; Profil ist das bestehende NJ-Halbprofil mit
`ALL_BANDS_24` für A, unveränderten übrigen Regeln und festem
`CONFIG_DIGEST = 55f1de8602c945749728ce17c74cdff8320d1b5fc72c800f239bc86737db1a1e`.
Den Profilhash aus der qualifizierten Bindung übernehmen, nicht frei setzen.
Sollrollen, Treffer und Inventare gehören ausschließlich in eine getrennte Bewertung.

Die gemeinsame Bindung `common.json` enthält Manifest, Regel-/Runtimekonfiguration,
Lesemengenplan, Referenzinventar und Qualifikationsbezug. `qualified_common(manifest,
directory)` verbindet diese mit dem aktuellen Qualifikationsbestand;
`validate_common(..., qualified=True)` prüft verfügbare Referenzinhalte, Hashes,
aktuellen Code samt transitiven Abhängigkeiten und die aktive 30/30-Qualifikation.
Historische Zulassungen sind kein Ersatz für geänderten Code. JSON-Dateien müssen
der vorhandenen kanonischen Darstellung entsprechen; ein Digest ohne Inhalt genügt nicht.
Quelle: [gemeinsame Bindung](../tools/_s2oc_shared_binding.py), Funktionen
`qualified_common`, `validate_common`, `inventory`, `read_json`.

Zulässig sind 1–28 Ereignisse, höchstens 20 Formationen, zwei auditive und sechs
visuelle Hinweise; kürzere Folgen benötigen keine Füllereignisse. Zusätzlich gelten
die Bytegrenzen: Manifest 32.768, Metadaten 65.536, Quellenbelege 174.080,
gemeinsame NJ-/Formations-/Generationshülle 262.144, Verifikation 262.144 und
Gesamtbeleg 4.194.304. Native Zustandsbelege bleiben auf je 98.304 Byte begrenzt.
Einzelgrenzen sind keine gemeinsam garantierte Reservierung.

`preflight(common)` bilanziert alle Fortschrittspositionen sowie Erfolgs- und
Fehlerabschluss als Alternativen. `shared.ledger(...)` zählt auch notwendige
Referenzdateien, Qualifikation, Abschluss und Bewertung. Vorstartprüfung und
tatsächliche Fortschritts-/Abschlussbilanz müssen passen. Eingangsbestand,
geplante Lesemenge und tatsächlich gelesene Bytes werden getrennt ausgewiesen.
Quellen: [Grenzen](../tools/_s2ob_private_caller_binding.py),
[Vorstartprüfung](../tools/_s2oc_shared_verification.py),
[gemeinsames Ledger](../tools/_s2oc_shared_binding.py).

## 3. Öffnen, übergeben, schließen

Aktueller Einstieg ist [tools/_s2oc_bound_session.py](../tools/_s2oc_bound_session.py),
nicht ein historischer OA-Runner. Folgende Signaturen beschreiben die vorhandene
Python-Bedienung; sie sind hier keine Ausführungsanweisung:

```python
session = entry.open_session(common, inv, output_directory,
                             neutral=False, common_path=common_path)
step_bytes = session.process(event)  # exakt das nächste gebundene Event
record_bytes = session.close()
```

Das Ergebnisverzeichnis darf noch nicht existieren; sein Elternverzeichnis muss
existieren. Eine neue, separat freigegebene Lauf-ID ist erforderlich. Der autorisierte
Aufrufer muss die einmalige Gateöffnung im selben Prozess übernehmen;
`open_session` verbraucht sie sofort. Die Sitzung hält genau einen Materialisierer
und eine Runtime. Jedes `process` prüft Reihenfolge und vollständige Ereignisbindung
vor Payloadzugriff. Hashprüfung liegt vor Analyse, NJ genau einmal vor Audiokontaktbildung.
Rohpayloads werden schrittweise freigegeben; Feld und Memory bleiben erhalten.

Doppelte, vertauschte, fremde oder nach Abschluss eingereichte Ereignisse werden
typisiert abgewiesen; paralleler Wiedereintritt scheitert an `SESSION_BUSY`.
Tatsächliche Verarbeitungsfehler führen zum Fehlerabschluss mit Phase und Fortschritt,
ohne gültige Feldwirkungen zurückzunehmen. Keine automatische Wiederholung.
Vorzeitiges `close()` ergibt `NOT_EVALUABLE`/`INCOMPLETE`, keinen vollständigen Erfolg.
Wiederholtes Schließen liefert denselben Abschluss, ohne erneut zu publizieren.
Quelle: [geerbter Prozess-/Abschlussablauf](../tools/_s2oc_private_caller_session.py),
`Session.process/close`, und die aktuellen Überschreibungen im Sitzungseinstieg.

## 4. Rückgaben verstehen

`process` gibt unveränderliche kanonische JSON-Bytes des Schrittergebnisses zurück,
keine veränderlichen Owner oder vollständige Rohwahrnehmung:

- `perception_status`, `field_receipt_digest`: Verarbeitung im unabhängigen Feldzweig.
- `memory_status`, `memory_receipt_digest`: Memoryoperation; Hinweise schreiben Memory nicht fort.
- `context_status`, `hypothesis`: getrennte Kontexthypothese oder Enthaltung;
  `hypothesis = null` ist nicht automatisch ein Fehler. Hypothesen bleiben unangewandt.
- `prestate_digest`, `poststate_digest`, `error_codes`: Zustandsbindung und technische Fehler.

Die vollständigen Belege stehen nach Abschluss unter `execution.inputs`
(gebundene Wahrnehmung), `source_receipts` (Quellen/NJ), `rows`
(Schritte, Formationen und Generationen), `states` und `scans`
(Primärscan/Direktbaseline). Gemeinsam abgelegte Angaben werden über
`load_common` und `unpack` vollständig aufgelöst. Der Schritt allein ist kein
separater Zugriff auf aktuelle Vektoren oder das gesamte Memoryinventar.
Quelle: [Schrittform](../tools/_s2mr_private_minimal_mcm_runtime.py),
`MinimalMCMRuntimeStep336V1`; [Belegzeile](../tools/_s2oa_private_runtime_binding.py),
`SingleRuntime.process_next`.

`close()` veröffentlicht `record.json` und `session.json`, aber führt selbst
keine unabhängige Verifikation oder fachliche Bewertung aus. Dafür besteht
`_s2oc_shared_verification.verify_once(directory, inv, qualified=True)`;
sie liest Belege ohne Rezeptorwiederholung und erzeugt einen einmaligen Prüfbeleg.
Nur `RECORDING_COMPLETE` mit `evaluation_allowed` erlaubt die separat gebundene
Auswertung. Ein fachlich falsifizierter Lauf kann technisch vollständig sein.

## 5. Neue Folge und verbleibende Bediengrenze

Vor einem neuen Versuch sind Dateien, vollständiges Manifest, aktuelles Inventar,
verfügbare Zulassungsbelege, gemeinsamer Hash, neue Ergebnisablage, beide
Abschlussalternativen und getrennte Erwartungen konkret zu binden. Erst danach
folgt eine separate Einmallauffreigabe. Geänderte Software benötigt eine passende
Quellen-/Qualifikationsbindung, nicht gelockerte Hashprüfungen.

Der vorhandene [dateigebundene Aufrufer](../reports/s2oc/run_bound_session_once.py)
bietet `run(common_path, trusted_sha256, inventory_path, output, neutral=False)`
und CLI-Argumente `--common`, `--sha256`, `--inventory`, `--output`.
Er steuert die ganze Folge, verifiziert einmal und schreibt die Bilanz, wertet
aber nicht fachlich aus. **Die CLI öffnet kein Gate und ist deshalb kein
allein startfähiger Benutzerbefehl.**

Für manuelle Einzelübergaben besteht nun der private
[Terminalclient](../tools/_s2od_private_terminal_client.py), neutral mit 16/16
Bedienkontrollen qualifiziert. Ein autorisierter Aufrufer lädt
`TerminalClient(common_path, trusted_sha256, inventory_path, output)` und ruft
`interact()` auf. `open` öffnet nur bei separat freigegebenem Gate; `next`
verarbeitet genau das nächste Ereignis, `status` zeigt den Fortschritt.
`close`, `abort` oder `quit` schließen ohne Neustart. Vorzeitiges Schließen
ist kein vollständiger Erfolg. Anschließend wird die vorhandene read-only
Verifikation einmal aufgerufen, keine fachliche Auswertung. Angezeigt werden
Status, Fehler und die unveränderte Hypothese, ohne zusätzliche Belegkopie.

Auch die Client-CLI (`--common`, `--sha256`, `--inventory`, `--output`) besitzt
keinen Gateöffnungsschalter. Die gemeinsame Bindung muss zusätzlich die drei
Dateien aus `client.OWN` als Quellen sowie `preregistration.json`, `stdout.txt`,
`stderr.txt` und `result.json` der
[Clientqualifikation](../reports/s2od/s2od-terminal-qualification-20260911-01/BEFUND.md)
als verfügbare, hashgebundene Metadaten mitzählen. Alte Bindungen werden nicht
stillschweigend erweitert. Ein tatsächlicher Benutzerlauf bleibt gesperrt.
Die neutralen Bedienprüfungen verwenden Sitzungsdoubles, keine neue native
Memorygeschichte; die bisherigen OC-Mechaniken bleiben unverändert.

Ein allgemeiner Manifestassistent, Medienkonverter und quellenneutraler fachlicher
Auswerter gehören ebenfalls nicht zum vorhandenen Einstieg.

Der [abgeschlossene Gedächtniszyklus](../reports/s2oc/caller-memory-cycle-20260910-02/BEFUND.md)
ist nur ein Lese-Beispiel. Seine Lauf-ID und Freigabe sind verbraucht; Erwartungen
und `FALSIFIED` bleiben unverändert. Diese Anleitung begründet weder Livequellen,
freie Taktung, Semantik, neue Memorymechanik noch allgemeinen Dauerbetrieb.
