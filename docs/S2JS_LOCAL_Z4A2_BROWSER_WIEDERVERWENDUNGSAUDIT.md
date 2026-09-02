# S2-JS - Lokaler Z4-A2-Browser-Wiederverwendungsaudit

## Status und Grenze

`S2JS_LOCAL_Z4A2_PATH_MATERIALIZABLE`

Der fehlgeschlagene Codex-In-App-Browserpfad aus
`s2jr-frame0-browser-preflight-20260902-01` ist terminal geschlossen. Er wird
nicht erneut aufgerufen, umbenannt oder als Herkunft fuer einen lokalen
Browserlauf verwendet.

S2-JS verwendet ausschliesslich die bereits vorhandene lokale Z4-A2-
Playwright-Grundlage. Es entsteht keine neue Browserplattform. Audio,
Rezeptoren, Memory, Kontext und Feld bleiben ausserhalb des Preflights.

## Statisch gebundene Herkunft

| Rolle | Pfad oder Wert | SHA-256 |
| --- | --- | --- |
| Runtimebindung | `mcm_field_organism/z4a_playwright_runtime_binding.py` | `a597a42f0293180f9168f2541087a7cf807ce7ce7ad0619e1f8bcc821b286194` |
| bewiesenes Lifecycle-Muster | `mcm_field_organism/z4a_playwright_smoke.py` | `d7444a46d888724383da00f92ff57bee9fba91ba0dc0c7d1ed48cbca27a5b2b0` |
| bestehende Capture-Grenze | `mcm_field_organism/z4a_playwright_capture.py` | `2c303acbbf09515953f6ab16ec7a4092f54a379586aff41282356a8c5c648dcb` |
| Playwright-Manifest | `.venv/Lib/site-packages/playwright/driver/package/browsers.json` | `f306eed529599b1eaf2f8a85db9de2b23e1a3fe36c2b66434b7c9434fb627a99` |
| Chromium-Binary | `%LOCALAPPDATA%/ms-playwright/chromium_headless_shell-1217/chrome-headless-shell-win64/chrome-headless-shell.exe` | `f7c1ef91a3e287b64509a9733fc8fd43678cf4e2765d67f4d0eceb0e39ecd026` |
| Simulationsreferenz | `tools/_s2jo_private_canonical_av_boundary.py` | `50a39fb3865fbd11b3577f79db2983f9dd3260262dee0f199ae5f884bed4ef71` |

Gebundene Runtimewerte:

- Playwright-Paket `1.62.0`;
- Manifestrolle `chromium-headless-shell`;
- Chromium `151.0.7922.34`, Revision `1234`;
- Binarygroesse `199090176` Byte.

`bind_installed_z4a_playwright_runtime` materialisiert Paket, Manifest,
Manifestrolle und Binary durch statisches Lesen. Vor dem Browserstart wird
der Binarydigest erneut gegen diese Bindung geprueft.

## Wiederverwendete und ausgeschlossene Teile

Unveraendert wiederverwendet werden:

1. die vorhandene `Z4APlaywrightRuntimeBinding`;
2. die Bindung des installierten Playwright-Manifests und Chromium-Binarys;
3. das in `z4a_playwright_smoke.py` bestehende Muster aus Binarypruefung,
   explizitem `executable_path`, Versionsabnahme, frischem Kontext und
   garantiertem Close im `finally`-Pfad.

Nicht als Ganzes wiederverwendbar sind:

- `Z4APlaywrightCapturePreflight`, weil es `480 x 480` fest bindet;
- `run_z4a_playwright_smoke`, weil es lokale Assetnavigation und einen
  Canvas-Locator-Screenshot verwendet;
- `z4a_playwright_capture`, weil es Audio-, Adapter- und Rezeptoraufgaben
  enthaelt.

Der private S2-JS-Preflight beschraenkt sich deshalb auf die bestehenden
Playwright-Primitiven fuer Start, isolierten Kontext, Seite, Screenshot und
geordneten Abschluss. Er fuehrt keine Z4-A2-Welt-, Audio- oder
Rezeptorfunktion aus.

## Einmaliger Preflight

Gebundene Lauf-ID:

`s2jr-local-z4a2-frame0-preflight-20260902-01`

Der Lauf besitzt genau folgende Phasen:

1. `BIND_RUNTIME` - lokale Runtime und Binary statisch binden;
2. `BROWSER_START` - gebundenes Binary einmal headless starten und Version
   abnehmen;
3. `CONTEXT_CREATE` - frischen nicht persistenten Kontext mit
   `1920 x 1080`, Device Scale Factor `1`, ohne Downloads und Service Worker
   erzeugen;
4. `PAGE_CREATE` - genau eine neue Seite erzeugen und jede Netzwerkanfrage
   blockieren;
5. `GEOMETRY_CHECK` - lokales `page.set_content` ohne Server ausfuehren und
   Viewport, Canvas, Scrollflaeche, Rahmen und Textfreiheit pruefen;
6. `RENDER` - Frame 0 ausschliesslich mit neu erzeugter `ImageData` und
   `putImageData` zeichnen;
7. `SCREENSHOT` - genau einen vollstaendigen Viewport-Screenshot erzeugen;
8. `CLOSE` - Seite, Kontext und Browser geordnet schliessen;
9. `PNG_PIXEL_COMPARE` - erst nach Browserabschluss PNG-Form, Alpha,
   RGB8-Bytes und Digest gegen den unabhaengigen S2-JO-Frame 0 pruefen.

Die Browserfixture uebernimmt keine Pixelbytes aus der Simulation. Sie
verwendet nur die vorab gebundenen Literale fuer Hintergrund, Rechteck,
Geometrie und Frameindex.

## Fehler- und Abschlussregeln

Die Browserphasen besitzen getrennte Fehlercodes:

- `BROWSER_START_FAILED`;
- `CONTEXT_CREATE_FAILED`;
- `PAGE_CREATE_FAILED`;
- `GEOMETRY_INVALID`;
- `RENDER_FAILED`;
- `SCREENSHOT_FAILED`;
- `BROWSER_CLOSE_FAILED`.

Nach vorhandenem Screenshot gelten getrennt:

- `PNG_DECODE_FAILED`;
- `PAYLOADS_DIFFER`;
- `BROWSER_SIMULATION_FRAME0_PAYLOAD_EQUAL`.

Genau ein Screenshotaufruf ist erlaubt. Ein Fehler vor dessen erfolgreichem
Abschluss ergibt `NOT_EVALUABLE`. Scheitert dieser vorhandene lokale Pfad
vor dem Screenshot, wird die Browserquelle vorerst terminal geschlossen;
es folgt keine Browserflag-, Runtime- oder Plattformvariation.

Die PNG liegt nur unter `%LOCALAPPDATA%/MCM_FIELD_ORGANISM/s2jr/` und wird
nicht als Repositoryartefakt aufgenommen. Repositorybelege enthalten nur
Plan, Runtimebindung, Lifecycle, Digests, Vergleichsergebnis und Terminal.
