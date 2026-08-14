# W1-H: Einmaliger realer Browser-Payload-Smoke

Stand: 2026-08-07

Entscheidung: `W1H_REAL_BROWSER_PAYLOAD_SMOKE_TECHNICALLY_PASSED`

Forschungslauf: nein

Laufnummer: keine

Reale Ausfuehrungen: genau eine erfolgreiche Browserausfuehrung

## Zweck

W1-H prueft ausschliesslich, ob die in W1-F und W1-G gebundene kurze lokale
Browserwelt unter der real installierten Runtime einmal vollstaendig bis in
das gemeinsame S/H-Feld durchlaeuft und danach alle Runtimegrenzen schliesst.

Der erste Werkzeugaufruf brach vor jedem Browserstart am fehlenden
Projektstamm im Python-Importpfad ab. Dieser reine Startskriptfehler wurde
behoben und mit einem Importtest ausserhalb des Workspace abgesichert. Er ist
keine Browserausfuehrung und erzeugte keine Messdaten. Danach wurde der reale
Smoke genau einmal ausgefuehrt.

## Gebundene Runtime

```text
playwright:                       1.62.0
chromium-headless-shell:          151.0.7922.34
browser_revision:                 1234
requirements_sha256:             6d838da3367601bc8911715ee2fd6b102c48e553933093c48904609beacdc5d2
manifest_sha256:                 f306eed529599b1eaf2f8a85db9de2b23e1a3fe36c2b66434b7c9434fb627a99
executable_sha256:               ce4635cd0e5dc0e21494542a701f347e91c1f1d821970578d97ed8df4ced50ef
```

Die beobachtete Engineversion stimmt mit der gebundenen Engineversion
ueberein.

## Technisches Ergebnis

```text
visual_png_count:                3
audio_chunk_count:              30
rendered_audio_sample_count:    2400
visual_state_count:             3
auditory_state_count:           21
assigned_event_count:           24
local_request_count:            3
blocked_request_count:          0
raw_payloads_retained:          false
audio_buffer_released:          true
page_closed:                    true
context_closed:                 true
browser_closed:                 true
```

Die drei lokalen Requests betreffen ausschliesslich `index.html`,
`styles.css` und `world.js`. Das gebundene Payloadinventar, das
Rezeptorinventar und die Ereigniszahl wurden exakt erreicht.

## Digests

```text
world_contract_digest:          8d896d7e55fd56c4193f3f25570a1c560fc5e1035f96f16e3f0640f8a06f7261
source_config_digest:           2671842a8e6cf764dd3f28f2accd075b41797e6f7e0ecd2bc2978af2ab6f1bb2
batch_digest:                   bee976f8db5549e059690097147eac05dd9a4510550ce486d22287ec1cfdcb74
field_snapshot_digest:          1cacc2849dd9b5d4bddba0bbbb2d3706e48f7abbad96e8ad4f8653748d1f1953
```

Die Digests identifizieren diesen technischen Durchgang. Aus einem einzelnen
Durchgang wird keine Wiederholbarkeit und keine Forschungswirkung abgeleitet.

## Nachzustand

Nach Werkzeugende lief kein W1-Headless-Browserprozess mehr. Die reservierten
Lauf-197-Dateien waren weiterhin nicht vorhanden. Das Werkzeug schrieb weder
einen Report noch Rohpayloads oder eine Forschungslaufdatei.

Der korrigierte direkte Werkzeugeinstieg wurde mit `11 passed` in den
fokussierten Runtime- und Smoke-Tests geprueft. Die bekannte
Pytest-Cachewarnung `WinError 183` betrifft nur den lokalen Cachepfad.

## Aussagegrenze

W1-H belegt genau eine technische Durchgaengigkeit:

```text
kontrollierte lokale Browserwelt
-> PNG- und PCM-Payloads
-> allgemeine Rezeptorbruecke
-> gemeinsames S/H-Feld
-> skalarer Receipt
-> vollstaendiger Prozessschluss
```

W1-H belegt keine Wahrnehmungsqualitaet, Praegung, Feldzeit, Memory,
Organisation, Semantik, Selbstregulation oder KI. Insbesondere ist der
erzeugte Feldzustand noch nicht gegen eine kontrollierte Null- oder
Stoerbaseline bewertet.

## W1-H-Entscheidung

```text
Runtimeidentitaet:               bestanden
lokale Requestgrenze:            bestanden
Payloadinventar:                 bestanden
Rezeptor- und Ereignisinventar:  bestanden
Rohpayloadfreiheit:              bestanden
Audiopufferfreigabe:             bestanden
Seiten-, Kontext-, Browserschluss: bestanden
technische S/H-Durchgaengigkeit: bestanden
Forschungsaussage:               nein
```

## Bester naechster Schritt

W1-I bindet statisch einen kleinsten kontrollierten Gegenbaseline-Vertrag
fuer die bestehende Browserwelt. Er muss mindestens identische Runtime,
Dauer, Abtastraten und Rezeptoren festhalten und genau eine unabhaengige
Eingangsvariation gegen eine Null- oder strukturzerstoerte Kontrolle stellen.
W1-I fuehrt noch keinen Browser, keinen Testweltlauf und keinen Forschungslauf
aus.
