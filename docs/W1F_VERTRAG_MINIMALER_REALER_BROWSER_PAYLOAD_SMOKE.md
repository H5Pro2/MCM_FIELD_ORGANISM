# W1-F: Vertrag des minimalen realen Browser-Payload-Smokes

Stand: 2026-08-07

Entscheidung: `W1F_REAL_BROWSER_PAYLOAD_SMOKE_CONTRACT_BOUND_NOT_EXECUTED`

Forschungslauf: nein

Browser gestartet: nein

## Auftrag

W1-F bindet vor jeder realen Browserausfuehrung genau einen minimalen
technischen Smoke fuer den allgemeinen W1-Pfad. Er prueft Browserengine,
lokale Assets, JavaScriptquelle, W1-E-Capture, W1-C-Rezeptorbruecke und den
vorhandenen S/H-Feldhandoff in einer kurzen kontrollierten Welt.

W1-F ist nur Vertrag. Runtimecode, Runner und Browserausfuehrung bleiben bis
zur naechsten technischen Scheibe getrennt.

## Statisch vorhandene lokale Runtime

Der lokale Bestand wurde ohne Playwrightimport und ohne Browserstart gelesen:

```text
playwright_package_version:       1.62.0
manifest_entry:                   chromium-headless-shell
chromium_engine_version:          151.0.7922.34
browser_revision:                 1234
manifest_sha256:                  f306eed529599b1eaf2f8a85db9de2b23e1a3fe36c2b66434b7c9434fb627a99
requirements_browser_sha256:      6d838da3367601bc8911715ee2fd6b102c48e553933093c48904609beacdc5d2
executable_size_bytes:            211223552
executable_sha256:                ce4635cd0e5dc0e21494542a701f347e91c1f1d821970578d97ed8df4ced50ef
browser_started:                  false
```

Die Digestzeilen sind jeweils ein 64-stelliger SHA-256-Wert. Das Binary liegt lokal unter
`.playwright-browsers/chromium_headless_shell-1234/` und ist durch
`.gitignore` ausgeschlossen.

Diese Werte sind nur aktueller technischer Bindungsbestand. W1-G muss sie vor
jeder spaeteren Ausfuehrung erneut aus Dateien und Metadaten ableiten und darf
sie nicht blind als Erfolg voraussetzen.

## Frische allgemeine Runtimebindung

W1-G implementiert `mcm_field_organism/browser_payload_runtime.py` mit:

```text
BrowserPayloadRuntimeBinding
BrowserPayloadRuntimeBindingError
bind_browser_payload_runtime(...)
bind_installed_browser_payload_runtime(...)
browser_payload_runtime_binding_json_value(...)
```

Die Bindung liest ausschliesslich Distribution, Manifest und Binary. Sie:

- verlangt die gepinnte Playwrightversion aus `requirements-browser.txt`;
- waehlt genau `chromium-headless-shell`;
- bindet Engineversion und Revision aus genau einem Manifesteintrag;
- verweigert Symlinks, leere Dateien und Pfade ausserhalb des lokalen
  Installationswurzelverzeichnisses;
- bildet Manifest-, Requirements- und Binarydigest;
- setzt `browser_started=False` unveraenderlich;
- importiert oder verwendet kein `z4a_*`-Modul.

Die vorhandene Z4-Runtimebindung wird weder importiert noch umbenannt. Der
W1-Vertrag ist ein frischer allgemeiner Namensraum.

## Gebundene kurze Welt

Der Smoke verwendet genau einen neuen allgemeinen technischen Weltvertrag:

```text
contract_id:                     browser.world.payload.smoke.v1
phases:
  rest.before:                   100 ms, static, tone_gain 0
  change:                        100 ms, moving, tone_gain 0.2
  rest.after:                    100 ms, static, tone_gain 0
movement_cycles:                 1
tone_frequency_hz:               440
total_duration:                  300 ms
```

Quellenkonfiguration:

```text
source_id:                       browser.payload.smoke.v1
canvas:                          120 x 80, device_scale_factor 1
visual_rate:                     10 fps
visual_inventory:                3 PNGs
motion_axis:                     horizontal
motion_amplitude_fraction:       0.2
foreground_size_fraction:        0.2
background_rgb:                  16, 24, 32
foreground_rgb:                  224, 232, 240
audio:                           mono sine, 8000 samples/s
audio_hop_size:                  80
audio_inventory:                 30 PCM-Hops / 2400 Samples
```

Rezeptorkonfiguration:

```text
visual_grid:                     3 x 2 x 3 Kanaele
auditory_window_size:            800 Samples
auditory_hop_size:               80 Samples
auditory_band_count:             8
auditory_frequency_range:        50 bis 3000 Hz
expected_visual_states:          3
expected_auditory_states:        21
expected_total_events:           24
```

Die kurze Welt ist keine Forschungswelt und keine inhaltliche Baseline. Sie
prueft nur technische Ausfuehrbarkeit und Durchgaengigkeit.

## W1-G-Implementierung ohne realen Start

W1-G implementiert:

```text
mcm_field_organism/browser_payload_runtime.py
mcm_field_organism/browser_payload_smoke.py
tools/run_browser_payload_smoke.py
tests/test_browser_payload_runtime.py
tests/test_browser_payload_smoke.py
```

Der Smokecode stellt eine injizierbare `playwright_factory` bereit. Seine
erste Abnahme verwendet nur synthetische Installationsbaeume und einen
vollstaendigen Fake-Playwright-Lifecycle. W1-G startet noch keinen realen
Browser.

## Reale W1-H-Ausfuehrungsgrenze

Erst nach bestandener W1-G-Abnahme darf W1-H den Smoke genau einmal real
ausfuehren:

```text
statische Runtimebindung erneut pruefen
-> Playwright-Kontextmanager oeffnen
-> exakt ein gebundenes Headless-Shell-Binary starten
-> exakt einen frischen nicht persistenten Kontext erzeugen
-> exakt eine Seite erzeugen
-> capture_browser_payload_page vollstaendig ausfuehren
-> reduzierten Batch in das vorhandene neutrale S/H-Feld uebergeben
-> Seite schliessen
-> Kontext schliessen
-> Browser schliessen
-> Playwright-Kontextmanager verlassen
```

Verbindliche Browseroptionen:

- `headless=True`;
- gebundener `executable_path`;
- Viewport 120 x 80 und Device-Scale 1;
- JavaScript aktiv;
- Downloads deaktiviert;
- Service Worker blockiert;
- kein persistentes Profil und keine Erweiterungen;
- Hintergrundnetzwerk, Komponentenupdate, Sync, Default-Apps und First-Run
  deaktiviert;
- kein Kamera- oder Mikrofonrecht.

## Lokale Requestgrenze

Die W1-E-Capture-Schicht laesst weiterhin nur folgende lokale Dateien zu:

```text
index.html
styles.css
world.js
```

Jeder andere `file:`, `http:`, `https:`, WebSocket- oder sonstige Request
bricht den Smoke vor einem gueltigen Receipt ab. Eine geblockte Anfrage darf
nicht als erfolgreicher Smoke mitgezaehlt werden.

## Garantierter Prozessschluss

Seite, Kontext und Browser werden in getrennten `finally`-Grenzen geschlossen.
Der Receipt darf nur entstehen, wenn gilt:

```text
page_created:                     true
page_closed:                      true
context_created:                  true
context_closed:                   true
browser_started:                  true
browser_closed:                   true
audio_buffer_released:            true
blocked_request_count:            0
raw_payloads_retained:            false
```

Auch bei Asset-, JavaScript-, PNG-, PCM-, Rezeptor-, Feld- oder
Serialisierungsfehler muessen alle bereits erzeugten Browserressourcen
geschlossen werden. Ein Fehler erzeugt keinen positiven Receipt.

## Skalare Smoke-Ausgabe

`BrowserPayloadSmokeReceipt` darf nur technische skalare Rollen enthalten:

- Smoke-, Runtime-, Welt- und Quellenidentitaet;
- Paket-, Engine- und Revisionswerte;
- Requirements-, Manifest-, Binary- und Assetdigests;
- W1-E-Capture-Receipt;
- Rezeptorzustands- und Ereignisanzahlen;
- Batchdigest und finaler technischer Feldsnapshotdigest;
- Request-, Audiofreigabe- und Lifecycleflags;
- `raw_payloads_retained=False`.

PNG-, Pixel-, PCM-, Rezeptorwert-, Feldwert- oder Trajektorienpayloads werden
nicht serialisiert. Das Werkzeug schreibt keine Reportdatei und keine
Forschungslaufdatei; es darf spaeter nur eine ASCII-JSON-Projektion auf
Standardausgabe geben.

## Pflichtabbrueche

W1-H gilt als technisch fehlgeschlagen bei:

- Runtime-, Manifest-, Requirements-, Binary- oder Assetdrift;
- beobachteter Engineversion ungleich gebundener Engineversion;
- nicht lokaler Anfrage oder Navigation;
- abweichendem Bild-, Audio-, Rezeptor- oder Ereignisinventar;
- nicht endlichen oder nicht normierten PCM-Werten;
- fehlerhafter PNG-Geometrie;
- abweichendem W1-E-Batchdigest innerhalb derselben Ausfuehrung;
- nicht erreichtem S/H-Handoff;
- nicht freigegebenem Audiopuffer;
- unvollstaendig geschlossenem Browserlebenszyklus;
- Rohdaten- oder Ergebnisdateierzeugung.

Es gibt keine automatische Wiederholung. Eine Korrektur waere eine neue
technische Entscheidung und kein Fortsetzen desselben Smokes.

## Aussagegrenze

Ein bestandener Smoke belegt nur, dass die kontrollierte lokale Browserquelle
unter der gebundenen Runtime technisch PNG und PCM bis in den vorhandenen
S/H-Feldpfad liefern kann. Er belegt keine Wahrnehmung im psychologischen
Sinn, kein Lernen, keine Praegung, keine Feldzeit, kein Memory, keine
Organisation, keine Semantik und keine KI.

Z4-A, Lauf 197, Kamera, Live-Mikrofon und physische Sensorik bleiben
ausgeschlossen.

## W1-F-Entscheidung

```text
lokale Runtime statisch vorhanden:       ja
allgemeine Runtimebindung implementiert: nein
allgemeiner Smokecode implementiert:     nein
Fake-Lifecycle-Abnahme:                  nein
realer Browserstart:                     nein
W1-H-Ausfuehrung freigegeben:            nein
Forschungslauf:                          nein
naechste technische Scheibe:             W1-G
```

## Bester naechster Schritt

W1-G ist gemaess
`W1G_IMPLEMENTIERUNG_RUNTIMEBINDUNG_UND_BROWSER_SMOKE_LIFECYCLE.md`
technisch geschlossen. Allgemeine Runtimebindung, injizierbarer Smokecode,
Konsolenwerkzeug und Fake-Lifecycle-Tests sind implementiert. W1-H darf das
Werkzeug genau einmal real ausfuehren; keine automatische Wiederholung und
kein Forschungslauf.
