# W6-H: Isolierter Python-Playwright-Runtimekorridor

Stand: 2026-08-09

Entscheidung: `W6H_ISOLATED_PYTHON_PLAYWRIGHT_CORRIDOR_READY`

Arbeitsart: technische lokale Runtimeherstellung und statische Vorabnahme

Browser gestartet: nein

Formaler Forschungslauf: nein

## Technische Frage

Kann die in W6-G fehlende Python-Playwright-Abhaengigkeit in einem
projektlokalen, vom System-Python getrennten Korridor exakt passend
bereitgestellt werden, ohne einen Browser zu installieren oder zu starten?

## Umsetzung

Unter `.w6-browser-python` wurde mit dem gebuendelten Python 3.12 eine eigene
virtuelle Umgebung angelegt. Die Installation folgt dem bestehenden
`requirements-browser.txt`-Pfad. Es wurde kein `playwright install`
ausgefuehrt.

Gebundener Paketbestand:

```text
Python:          3.12.13
playwright:      1.62.0
numpy:           2.5.1
opencv-python:   4.14.0.94
```

Die Umgebung ist durch `.gitignore` von Projektartefakten getrennt. Globale
Python-Installationen wurden nicht veraendert.

## Statisches Vorpruefwerkzeug

`tools/print_s1b_causal_browser_preflight.py` bindet ueber
`mcm_field_organism.current_api` ausschliesslich:

- `requirements-browser.txt`;
- das Python-Playwright-Paketmanifest;
- die bereits vorhandene lokale Chromium-Headless-Shell;
- die kontrollierten Browserweltassets;
- die freien W6-I-Report-, Attempt- und Lockpfade.

Das Werkzeug importiert keine `playwright.sync_api`, startet keinen Browser
und erzeugt keine Report- oder Reservierungsdatei.

## Ergebnis

```text
preflight_decision:       READY_FOR_EXPLICIT_ONE_SHOT_BROWSER_EXECUTION
execution_permitted:      true
python_playwright_version: 1.62.0
browser_started:          false
runtime_binding_digest:   13642e9484a319b3f16237bfd39abf49cdbae0b333ecf94076190e205117f002
contract_digest:          094558b988103ad1ed75e708b3a0961b62963f74896411dd1e381afeac81387d
```

Die drei W6-I-Pfade und die drei reservierten Lauf-197-Pfade waren nach der
Vorabnahme weiterhin nicht vorhanden.

## Abnahme

Die direkten `current_api`- und W6-G-Vertragstests bestehen. Der bestehende
Runtimebinder ist jetzt additiv ueber `current_api` exportiert, damit das
Vorpruefwerkzeug keine interne Projektimportgrenze umgeht.

## Aussagegrenze

W6-H beseitigt ausschliesslich eine lokale Paket- und Importblockade. Es
liefert keine Welt- oder Feldevidenz und keinen Nachweis von Praegung, Memory,
Feldzeit, Organisation, Semantik, Selbstregulation oder KI.

## Bester naechster Schritt

W6-I fuehrt genau einmal den in W6-G gebundenen kontrollierten H_A/H_B/P-
Browserlauf aus. Vor dem Start muessen alle Digests und freien Pfade erneut
stimmen; der Attemptmarker muss vor dem Browserstart angelegt werden. Der
Lauf schreibt nur den vorregistrierten Skalarreport und muss Seiten, Kontexte
und Browser vollstaendig schliessen.
