# W6-G: Statischer einmaliger Browser-Ausfuehrungsvertrag

Stand: 2026-08-09

Entscheidung: `W6G_ONE_SHOT_CONTRACT_BOUND_EXECUTION_BLOCKED_PYTHON_PLAYWRIGHT_MISSING`

Arbeitsart: statische Runtime-, Asset-, Lifecycle- und Reportvorabnahme

Runtimeaenderung: ja, additiver statischer S1-B-Referenzvertrag

Browser gestartet: nein

Formaler Forschungslauf: nein

## Ausfuehrungsfrage

Sind Weltvertrag, lokale Assets, Browserruntime, Kontextisolation,
Einmaligkeit, Reportoberflaeche und Abbruchbedingungen fuer genau einen
spaeteren kontrollierten H_A/H_B/P-Browserlauf vollstaendig gebunden?

## Implementierter Vertrag

`mcm_field_organism/s1b_causal_browser_execution_contract.py` stellt bereit:

- `S1BCausalBrowserExecutionContract`;
- `prepare_s1b_causal_browser_execution_contract(...)`;
- eine statische READY-/BLOCKED-Entscheidung ohne Browserimport oder Start.

Der Vertrag liest und prueft ausschliesslich vorhandene Dateien. Er erzeugt
weder Report, Attemptmarker noch Lockdatei.

## Gebundene Browserruntime

Der vorhandene Node-Playwright-Bestand und die lokale Browserbinary tragen
inhaltlich denselben Pin:

```text
Playwright/Playwright Core:  1.62.0
Engine:                      chromium
Engineversion:               151.0.7922.34
Browserrevision:             1234
Requirements SHA-256:        6d838da3367601bc8911715ee2fd6b102c48e553933093c48904609beacdc5d2
Manifest SHA-256:            f306eed529599b1eaf2f8a85db9de2b23e1a3fe36c2b66434b7c9434fb627a99
Binarygroesse:                211223552 Byte
Binary SHA-256:              ce4635cd0e5dc0e21494542a701f347e91c1f1d821970578d97ed8df4ced50ef
Runtimebinding SHA-256:       5022663084b96a50c88a9f4acb9e62b4a1d15c9e06d731527588138163cddc9e
browser_started:              false
```

Manifestquelle ist der gebuendelte read-only Node-Bestand. Die Binary liegt
im lokalen Workspacecache. Beide wurden nur statisch gelesen.

## Gebundene Assets

```text
index.html: 74fc372a3eff08ac38e803689e562ce5acbb39d56d3351db475c768457e32af8
styles.css: f026fce8f826fb7364a11b1b05ad4acb3dd37aed7dede5453c6f82cbf497b594
world.js:   fda8c774708af883eb97625b7064ec288c06e2819619fb2eb93e281212d32158
Weltset:    66168de571819b71e68ce6605781d3d65224cc1663294924fce788ad2a821920
```

Netzwerkrequests, persistente Profile, Erweiterungen, Rohdatenhaltung und
Rueckschreibung bleiben verboten.

## Kontext- und Lifecyclevertrag

Ein spaeterer Lauf muss genau drei frische isolierte Kontexte verwenden:

```text
Kontext 1: H_A
Kontext 2: H_B
Kontext 3: P
```

Alle Kontexte laufen headless. P wird einmal reduziert und danach als
dasselbe immutable Sequenzobjekt auf alle Feldarme angewandt. Attemptmarker
muss vor einem spaeteren Browserstart atomar angelegt werden; ein exklusiver
Lock verhindert Wiederholung. Seiten, Kontexte und Browser muessen auch bei
Fehlern geschlossen werden.

## Reservierter Reportkorridor

```text
reports/s1b_causal_browser_w6i_once_v1.json
reports/s1b_causal_browser_w6i_once_v1.json.attempted
reports/s1b_causal_browser_w6i_once_v1.json.lock
```

Alle drei Pfade sind zum W6-G-Zeitpunkt nicht vorhanden. Sie wurden nur im
Vertrag reserviert und nicht angelegt. Der reservierte Lauf 197 bleibt davon
vollstaendig getrennt.

Der Report darf nur vorregistrierte Skalare, Boolesche Werte und Digests
tragen: Runtime/Welt/Asset/Batchbindungen, Supportzaehler, L-Normen, die fuenf
R/N/X-Differenzen, schnelle Gleichheitskontrollen, Nullarmkontrollen,
technische Entscheidung sowie Rohpuffer- und Closurestatus. S/H/L-Trajektorien
und Medienpayloads werden nicht in den Report geschrieben.

## Aktuelle statische Entscheidung

Die aktuelle System-Python-Runtime `C:\Python314\python.exe` und der
gebuendelte Workspace-Python enthalten keine Python-Paketmetadaten fuer
`playwright`. Der bestehende Python-Ausfuehrungspfad importiert jedoch
`playwright.sync_api`.

Deshalb lautet die reale Vorabnahme:

```text
preflight_decision:       BLOCKED_PYTHON_PLAYWRIGHT_PACKAGE_MISSING
execution_permitted:      false
python_playwright_version: null
Browserbinary passend:    ja
Node-Manifest passend:    ja
Assets passend:           ja
Reportpfade frei:         ja
Browser gestartet:        nein
```

Lokaler Vertragsdigest:

```text
1de02d118b09366b68cd83ecc896b9846deca2da5abd2b58c70a20e53df6bce2
```

Der passende Node-Bestand wird nicht stillschweigend als Python-Paket
umgedeutet. Ebenso wird nicht global in `C:\Python314` installiert.

## Technische Abnahme

Tests bestaetigen:

- READY bei statisch passender Python-Paketversion;
- gebundene BLOCKED-Entscheidung bei fehlendem Python-Paket;
- Einmaligkeitssperre bei vorhandenem Report-/Attempt-/Lockpfad;
- keine Dateierzeugung durch die Vorabnahme;
- unveraenderte S1-B-Referenzexportgrenze.

Zusammen mit den angrenzenden W6-F-, S1-B-, API-, neutralen Runtime- und
AV-Tests bestehen 68 Tests.

## Abbruchbedingungen

Ein spaeterer Browserstart bleibt verboten bei:

- fehlendem oder versionsabweichendem Python-Playwright-Paket;
- veraendertem Runtime-, Binary-, Asset- oder Weltsetdigest;
- vorhandenem Report-, Attempt- oder Lockpfad;
- weniger oder mehr als drei isolierten Kontexten;
- Netzwerkrequest, persistentem Profil oder Erweiterung;
- nicht freigegebenem Audio-Rohpuffer;
- unvollstaendigem Handoff oder nicht identischer Probe;
- fehlender sicherer Schliessung aller Browserressourcen.

## Aussagegrenze

W6-G erzeugt keine Welt- oder Feldevidenz und insbesondere keinen Nachweis
von Praegung, Memory, Feldzeit, Organisation, Semantik oder KI. Die Sperre ist
eine fehlende Python-Laufzeitabhaengigkeit, keine Grenze der MCM-Mechanik.

## Bester naechster Schritt

W6-H richtet einen isolierten, projektlokalen Python-Playwright-1.62.0-
Korridor ein oder bindet einen bereits vorhandenen gleichwertigen Korridor.
Danach wird nur die statische W6-G-Vorabnahme erneut ausgefuehrt. W6-H startet
keinen Browser. Erst ein READY-Ergebnis duerfte W6-I als einmalige
kontrollierte Ausfuehrung freigeben.
