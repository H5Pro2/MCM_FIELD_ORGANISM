# W1-O: Einmalige reale kanonische Quellenpaar-Diagnose

Stand: 2026-08-08

Entscheidung: `W1O_REAL_CANONICAL_SOURCE_INVARIANTS_MATCH`

Forschungslauf: nein

Reale Diagnosepaare: genau eins

Feldhandoff: nein

## Auftrag

W1-O prueft die in W1-N unter Fakes gebundene kanonische AV-Quelle genau
einmal in der real gebundenen Headless-Browserlaufzeit. Geprueft werden nur
die Quelleninvarianten vor jeder Feldentwicklung.

Der historische W1-M-Runner und seine Assets bleiben unveraendert. Fuer W1-O
wurde ein getrenntes schleifen- und reportfreies Werkzeug gebunden:

```text
tools/run_controlled_av_canonical_source_pair_diagnostic.py
```

## Vorabnahme

Vor dem realen Start bestanden Import-, Bindungs-, Fake- und
Regressionspruefungen mit `30 passed`. Das Werkzeug:

- bindet nur `tools/controlled_av_canonical_audio_world`;
- ruft nur `run_controlled_av_canonical_source_pair_diagnostic()` auf;
- enthaelt keine Schleife und keine Reportpublikation;
- startet beim Import keinen Browser;
- besitzt keinen Feldhandoff und keinen Z4-Bezug.

## Einmaliger realer Befund

Das kanonische Quellenpaar bestand alle gebundenen Invarianten:

```text
diagnostic_decision:                 SOURCE_INVARIANTS_MATCH
failed_invariant_roles:              []
visual_sequence_exact_match:         true
A0 audio_total_energy:               48.00000010990328
C0 audio_total_energy:               48.00000010990328
audio_total_energy_relative_error:   0.0
energy_relative_tolerance:           1e-12
```

Der visuelle Sequenzdigest ist in beiden Bedingungen:

```text
5f55328f68a6fbdee4723ba415fdd679ab5be638cb58d9e539f54bf72cf0eab5
```

Die auditiven Sequenzdigests unterscheiden sich erwartungsgemaess, weil das
identische Tonsegment an verschiedenen Zeitpositionen liegt:

```text
A0: 97568002093fadad566aec024ece75ee41abcf0ac3b4dec00d589ec349519ba6
C0: 095f5511db95a4e1a65a550fc06cd3cd490bff80ad2f64fa01f758f1dc8a6c67
```

Damit ist die beabsichtigte zeitliche Verschiebung vorhanden, ohne die
Gesamtenergie oder die visuelle Rezeptorfolge zu veraendern.

## Inventar und Lifecycle

Beide Bedingungen erreichten jeweils:

```text
visual PNGs:                  36
audio chunks:                120
rendered audio samples:      9600
visual receptor states:      36
auditory receptor states:    111
receptor events:             147
local requests:              3
blocked requests:            0
audio buffer released:       true
page closed:                 true
context closed:              true
browser closed:              true
raw payloads retained:       false
field handoff performed:     false
```

Die gebundene Laufzeit war Playwright `1.62.0`, Chromium
`151.0.7922.34`, Revision `1234`. Nach dem Werkzeugende blieb kein
W1-O-Headless-Prozess zurueck. Es wurden keine Report-, Rohpayload- oder
Forschungslaufdateien angelegt. Lauf 197 blieb unberuehrt.

## Aussagegrenze

W1-O belegt nur, dass das reale kanonische Quellenpaar die vorab gebundenen
visuellen und energetischen Invarianten erfuellt. Es belegt keine
Feldwirkung, Zeitwahrnehmung, Ueberreizung, Regulation, Praegung, Memory,
Organisation, Semantik, Selbstregulation oder KI.

## Bester naechster Schritt

W1-P bindet den vorhandenen A0/C0-Feldpaarweg getrennt an die kanonische
Quelle und prueft ihn zuerst vollstaendig unter Fakes. Historische W1-J- und
W1-K-Pfade bleiben unveraendert. Erst nach dieser technischen Abnahme darf
ein einzelner neuer realer Feldpaar-Smoke vorgesehen werden.
