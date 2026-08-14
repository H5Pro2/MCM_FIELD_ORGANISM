# W1-G: Implementierung von Runtimebindung und Browser-Smoke-Lifecycle

Stand: 2026-08-07

Entscheidung: `W1G_BROWSER_PAYLOAD_SMOKE_IMPLEMENTED_NOT_EXECUTED`

Forschungslauf: nein

Realer Browser gestartet: nein

## Ergebnis

Der in W1-F gebundene allgemeine Browser-Smoke ist implementiert und mit
synthetischen Runtimebaeumen sowie einem vollstaendigen Fake-Playwright-
Lifecycle technisch abgenommen. Die reale lokale Runtime wurde zusaetzlich
mit dem neuen allgemeinen Binder statisch erkannt. Es wurde kein realer
Browserprozess gestartet.

## Allgemeine Runtimebindung

`mcm_field_organism/browser_payload_runtime.py` implementiert:

- `BrowserPayloadRuntimeBinding`;
- `bind_browser_payload_runtime()` fuer explizite Pfade;
- `bind_installed_browser_payload_runtime()` ohne Playwrightimport;
- skalare JSON- und Rollenprojektionen.

Die Bindung prueft vor einem moeglichen Start:

- exakten `playwright==...`-Pin in `requirements-browser.txt`;
- genau einen `chromium-headless-shell`-Manifesteintrag;
- Engineversion und numerische Revision;
- reale regulaere Dateien ohne Symlink;
- Binary innerhalb der gebundenen Installationswurzel;
- positive Binarygroesse;
- Requirements-, Manifest- und Binary-SHA-256;
- unveraenderlich `browser_started=False`.

Die reale statische W1-Bindung ergab:

```text
package_version:                  1.62.0
engine_version:                   151.0.7922.34
browser_revision:                 1234
requirements_sha256:             6d838da3367601bc8911715ee2fd6b102c48e553933093c48904609beacdc5d2
manifest_sha256:                 f306eed529599b1eaf2f8a85db9de2b23e1a3fe36c2b66434b7c9434fb627a99
executable_sha256:               ce4635cd0e5dc0e21494542a701f347e91c1f1d821970578d97ed8df4ced50ef
browser_started:                 false
```

Der Requirements-Digest unterscheidet sich vom W1-F-Zwischenwert nur, weil
der Kommentar von einer Z4-spezifischen auf die allgemeine kamerafreie
Browser-Testweltrolle korrigiert wurde. Der Pin `playwright==1.62.0` blieb
unveraendert. W1-F ist auf den neuen exakten Digest aktualisiert.

## Injizierbarer Smokecode

`mcm_field_organism/browser_payload_smoke.py` implementiert:

- die feste kurze W1-F-Welt und Quellenkonfiguration;
- den passenden visuellen und auditiven Rezeptoraufbau;
- `run_browser_payload_smoke()` mit injizierbarer `playwright_factory`;
- `BrowserPayloadSmokeReceipt` ohne Rohpayload;
- skalare JSON- und Rollenprojektionen.

Vor jedem Factory-Aufruf werden Requirements, Manifest und Binary erneut
gegen Groesse und Digests geprueft. Drift stoppt deshalb vor Playwright und
vor jedem Browserprozess. Zusaetzlich vergleicht der W1-F-Validator
Paketversion, Engineversion, Revision sowie Requirements-, Manifest-, Binary-
und Assetdigests mit den vorab gebundenen W1-F-Werten. Die reale statische
Bindung besteht diese Identitaetspruefung bei `browser_started=False`.

## Browserlebenszyklus

Der implementierte Lifecycle ist:

```text
Runtime erneut pruefen
-> Browser starten
-> isolierten Kontext erzeugen
-> Seite erzeugen
-> W1-E-Capture vollstaendig ausfuehren
-> W1-C-Batch in das S/H-Feld uebergeben
-> Seite schliessen
-> Kontext schliessen
-> Browser schliessen
-> Playwright-Kontext verlassen
```

Seite, Kontext und Browser besitzen getrennte Schliessungsgrenzen. Die
Browsergrenze liegt in einem aeusseren `finally`: Selbst ein kontrollierter
Fehler von `context.close()` verhindert den Aufruf von `browser.close()`
nicht. Bei einem Fehler entsteht kein positiver Receipt.

## Konsolenwerkzeug

`tools/run_browser_payload_smoke.py`:

- bindet die lokale allgemeine Runtime;
- verwendet ausschliesslich die neuen W1-Assets;
- ruft genau einen Smoke auf;
- gibt ausschliesslich eine sortierte ASCII-JSON-Projektion auf Standardausgabe;
- schreibt keine Report-, Payload- oder Forschungslaufdatei.

Das Werkzeug wurde in W1-G nicht ausgefuehrt.

## Gebundene Assetdigests

```text
index.html:                       74fc372a3eff08ac38e803689e562ce5acbb39d56d3351db475c768457e32af8
styles.css:                       f026fce8f826fb7364a11b1b05ad4acb3dd37aed7dede5453c6f82cbf497b594
world.js:                         fda8c774708af883eb97625b7064ec288c06e2819619fb2eb93e281212d32158
```

W1-H muss diese Werte ueber den bestehenden Assetbinder neu lesen. Eine
Abweichung stoppt den Smoke.

## Synthetische Abnahme

Die W1-G-Tests pruefen:

- deterministische Runtimebindung in einem synthetischen Installationsbaum;
- exakten Requirements-Pin und Installationswurzel;
- eindeutigen Headless-Shell-Manifesteintrag;
- feste W1-F-Inventare mit 3 Bildern und 30 Audiohops;
- vollstaendigen Fake-Playwright-Lifecycle bis zum S/H-Feld;
- `21` auditive, `3` visuelle und `24` zugewiesene Ereignisse;
- skalaren Receipt und identische Capture-/Smokedigests;
- Schliessen nach einem Fehler waehrend der PCM-Uebergabe;
- Browser-Schliessen trotz kontrolliert fehlschlagendem Kontextschluss;
- Runtime-Driftstopp vor Aufruf der Playwright-Factory;
- W1-F-Identitaetsstopp fuer eine abweichende synthetische Runtime vor der
  Playwright-Factory;
- Abwesenheit von Z4- und Reportpfaden im neuen W1-Code.

Die isolierte W1-G-/W1-E-/W1-C-/API-Suite bestand mit `24 passed`.

Der relevante Gesamtverbund bestand mit `136 passed` und 9 Subtests. Die
bekannte Pytest-Cachewarnung `WinError 183` betrifft nur den lokalen
Cachepfad.

## Aussage- und Ausfuehrungsgrenze

W1-G belegt die technische Struktur und Fehlerbereinigung nur unter
kontrollierten Fakes. JavaScript, Canvas, `OfflineAudioContext` und die reale
Chromiumausfuehrung sind noch nicht gemeinsam abgenommen.

Ein spaeter bestandener W1-H-Smoke waere ebenfalls nur ein technischer
Durchgaengigkeitsnachweis. Er waere kein Befund zu Wahrnehmung, Lernen,
Praegung, Feldzeit, Memory, Organisation, Semantik oder KI.

Z4-A, Lauf 197, Kamera, Live-Mikrofon und physische Sensorik bleiben
ausgeschlossen.

## W1-G-Entscheidung

```text
allgemeine Runtimebindung:              implementiert
reale Runtime statisch gebunden:        ja
injizierbarer Smokecode:                implementiert
Konsolenwerkzeug:                       implementiert, nicht ausgefuehrt
Fake-Lifecycle bis S/H-Feld:            bestanden
Fehler- und Driftgrenzen:               bestanden
reale W1-F-Runtimeidentitaet:           statisch bestanden
realer Browserstart:                    nein
W1-H einmalig technisch freigabereif:   ja
Forschungslauf:                         nein
```

## Bester naechster Schritt

W1-H fuehrt `tools/run_browser_payload_smoke.py` genau einmal aus. Es ist ein
technischer Smoke ohne Laufnummer. Danach werden ausschliesslich die skalare
Konsolenausgabe, die erwarteten Inventare, lokale Requestfreiheit,
Audiopufferfreigabe und der vollstaendige Prozessschluss dokumentiert. Keine
automatische Wiederholung bei Fehlern.
