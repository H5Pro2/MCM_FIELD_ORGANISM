# S2-JR - Lokaler Z4-A2-Ein-Frame-Preflight

## Status

`NOT_EVALUABLE`

Lauf-ID:

`s2jr-local-z4a2-frame0-preflight-20260902-01`

Der genau einmal ausgefuehrte lokale Playwright-Preflight stoppte in der
Phase `BROWSER_START` mit `BROWSER_START_FAILED`. Er wurde nicht wiederholt,
nicht korrigiert und nicht mit einem anderen Binary oder Browserflag
fortgesetzt.

Der Codex-In-App-Browserpfad bleibt terminal geschlossen. Der vorhandene
lokale Z4-A2-Pfad wird nach diesem zweiten Abbruch ebenfalls vorerst
geschlossen. Es folgt keine weitere Browserinfrastruktur in diesem
Pruefzweig.

## Statische Wiederverwendung

Vor dem Lauf wurde ausschliesslich folgende vorhandene Z4-A2-Grundlage als
materialisierbar abgenommen:

- `Z4APlaywrightRuntimeBinding` fuer die statische Manifest- und
  Binarybindung;
- Binarydigestpruefung und beobachtete Versionsabnahme vor dem Kontext;
- expliziter lokaler `executable_path`;
- frischer, nicht persistenter Kontext als vorgesehener Nachfolger;
- geordneter Seite-, Kontext- und Browserabschluss im `finally`-Pfad.

Die vorhandenen Capture- und Smoke-Funktionen wurden nicht als Ganzes
aufgerufen. Ihre festen `480 x 480`-, Asset-, Audio- und Rezeptoranteile
liegen ausserhalb des freigegebenen S2-JR-Preflights.

Statischer Vertrag:

`docs/S2JS_LOCAL_Z4A2_BROWSER_WIEDERVERWENDUNGSAUDIT.md`

## Gebundene Runtime und Ursache

| Rolle | Gebundener oder beobachteter Wert |
| --- | --- |
| Playwright-Paket | `1.62.0` |
| Manifestrolle | `chromium-headless-shell` |
| Manifestrevision | `1234` |
| gebundene Chromium-Version | `151.0.7922.34` |
| installiertes Browserverzeichnis | `chromium_headless_shell-1217` |
| beobachtete Chromium-Version | `147.0.7727.15` |
| Binary-SHA-256 | `f7c1ef91a3e287b64509a9733fc8fd43678cf4e2765d67f4d0eceb0e39ecd026` |

Das Browserbinary konnte gestartet werden, meldete aber nicht die durch das
aktuelle Playwright-Manifest gebundene Engineversion. Die Abweichung wurde
vor Kontextanlage fail-closed abgewiesen. Der Browser wurde danach ohne
Closefehler geschlossen.

Dies ist eine konkrete lokale Runtime-/Binary-Diskrepanz. Sie ist kein
Pixel-, PNG-, Rezeptor- oder Funktionsfehler.

## Nicht erreichte Phasen

Maschinenlesbar belegt sind:

- Browserstarts: `1`;
- erfolgreich geschlossene Browserprozesse: `1`;
- Kontextanlagen: `0`;
- Seitenanlagen: `0`;
- Geometriepruefungen: `0`;
- Renderaufrufe: `0`;
- Screenshots: `0`;
- PNG-Decoderaufrufe: `0`;
- Pixelvergleiche: `0`;
- Rezeptor-, Audio-, Memory-, Kontext- und Feldaufrufe: jeweils `0`.

Mangels Screenshot existiert keine PNG-Datei und kein
`PAYLOADS_DIFFER`-Befund. Ueber die Gleichheit von Browser- und
Simulationspixeln wurde nichts festgestellt.

## Read-only Abschlusspruefung

Nach dem Lauf wurden ohne Browser-, PNG- oder Projektfunktionsaufruf
erfolgreich geprueft:

- identische Lauf-IDs in Plan, Browserbeleg, Ergebnis und Terminal;
- Runtime-, Browserbeleg- und Ergebnisdigestverkettung;
- aktueller Quellstand gegen die vor dem Lauf gebundenen Quellhashes;
- terminaler `NOT_EVALUABLE`-Marker;
- `BROWSER_START_FAILED` und terminaler Runner-Code `3`;
- Versionsabweichung `151.0.7922.34` gegen `147.0.7727.15`;
- erfolgreicher Browserabschluss ohne Closefehler;
- Abwesenheit von Kontext, Screenshot und jeder Nutzdatenverarbeitung.

Gesamtergebnis der read-only Pruefung:

`READ_ONLY_EVIDENCE_VALID=true`

## Maschinenlesbare Belege

Verzeichnis:

`reports/s2jr/s2jr-local-z4a2-frame0-preflight-20260902-01`

| Datei | Byte | SHA-256 |
| --- | ---: | --- |
| `plan.json` | 1981 | `30101e8739328e22b308a58c40079ad33878092d9d6b2dedc7a1952d0617dfef` |
| `browser-audit.json` | 658 | `01c7d77a25e3f6f348eca7524cb6d9c45f12ec583b4ba35b43d956722a373f2f` |
| `result.json` | 495 | `ec50db90fc48e84eefbc76b90c1eef8e4e0108bf91127f0895498152a95f563a` |
| `terminal.json` | 318 | `dfe48fe34ebbd83212b517944e1e9a7ce7cd05922c4ff7b5ddbabc99af74cd2e` |
| `NOT_EVALUABLE` | 65 | `31a80a165650b1260f04cd9d09867cc3a55cf281655b57d1438376c9d9e5a929` |

Quellbindung des ausgefuehrten privaten Preflights:

`6529ef4dd47535f44fb5f47bd1f7c184347514f5b1b27d9a111ba8fa983f2d94`

## Entscheidung

Die kleine private Sechs-Frame-Adapterimplementierung und jede
Rezeptorqualifikation werden nicht freigegeben. Die Browserquelle ist fuer
diesen Abschnitt vorerst geschlossen. Eine spaetere Wiederaufnahme benoetigt
eine neue fachliche Entscheidung und eine nachweislich konsistente lokale
Playwright-/Chromium-Installation; dieser Lauf wird dabei nicht wiederholt
oder umgedeutet.
