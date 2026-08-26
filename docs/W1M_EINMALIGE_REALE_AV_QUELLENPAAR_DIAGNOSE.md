# W1-M: Einmalige reale AV-Quellenpaar-Diagnose

Stand: 2026-08-07

Entscheidung: `W1M_REAL_SOURCE_DIAGNOSTIC_IDENTIFIED_AUDIO_ENERGY`

Forschungslauf: nein

Laufnummer: keine

Reale Diagnosepaare: genau eins

Feldhandoff: nein

## Auftrag

W1-M lokalisiert die in W1-K offen gebliebene reale Quellenabweichung mit
genau einem diagnostischen A0/C0-Paar vor jeder Feldentwicklung. Die
Diagnose darf nur reduzierte Sequenzdigests, Audioenergien, Inventare und
Lifecyclewerte ausgeben.

Sie ist keine Wiederholung des W1-K-Feldpaars, weil sie keinen Feldzustand
aufbaut, keinen Feldvergleich berechnet und keine Wirkung bewertet.

## Neutrale Quellenrolle

Der neue Implementierungsname lautet:

```text
mcm_field_organism/controlled_av_source_pair_diagnostic.py
```

Damit bezeichnet `Browser` weiterhin nur die aktuelle technische Laufzeit
der kontrollierten Welt. Die fachlichen Rezeptoridentitaeten bleiben
`visual` und `auditory`.

`ControlledAVSourcePairDiagnosticReceipt` enthaelt:

- zwei skalare Arm-Receipts;
- reduzierte visuelle und auditive Sequenzdigests;
- beide Audioenergien und ihren relativen Fehler;
- Inventare und Lifecycleflags;
- exakt fehlgeschlagene Quelleninvarianten;
- unveraenderlich `field_handoff_performed=False`;
- unveraenderlich `raw_payloads_retained=False`.

## Fake- und Startabnahme

Vor dem realen Start bestanden:

- faire Fake-Quelle mit `SOURCE_INVARIANTS_MATCH`;
- unfaire Fake-Energie mit Fehlerrolle `audio_total_energy`;
- Fehlerbereinigung im zweiten Arm;
- Runtime-Driftstopp vor der Factory;
- Abwesenheit jedes Feldhandoff-Imports;
- importierbares Einmalwerkzeug ausserhalb des Workspace;
- schleifen- und reportfreies Werkzeug;
- statische reale Runtimeidentitaet bei `browser_started=False`.

Der fokussierte Verbund bestand mit `27 passed`.

## Einmalige reale Diagnose

Das Werkzeug
`tools/run_controlled_av_source_pair_diagnostic.py` fuehrte genau ein reales
Quellenpaar aus.

Visueller Befund:

```text
visual_sequence_exact_match: true
A0 visual_sequence_digest:   5f55328f68a6fbdee4723ba415fdd679ab5be638cb58d9e539f54bf72cf0eab5
C0 visual_sequence_digest:   5f55328f68a6fbdee4723ba415fdd679ab5be638cb58d9e539f54bf72cf0eab5
```

Die real reduzierten visuellen Rezeptorwertfolgen sind exakt gleich. Die
visuelle Quelle ist damit als Ursache des W1-K-Sammelfehlers ausgeschlossen.

Auditiver Quellenbefund:

```text
A0 audio_total_energy:              47.99991911465793
C0 audio_total_energy:              47.999918896666436
absolute difference:                2.1799149385606245e-07
audio_total_energy_relative_error:  4.541497059689895e-09
bound tolerance:                    1e-12
failed_invariant_roles:             audio_total_energy
diagnostic_decision:                SOURCE_INVARIANTS_DIFFER
```

Die Ursache ist damit eindeutig als minimale Energieabweichung der zwei
unabhaengig gerenderten Web-Audio-Signale lokalisiert. Der relative Fehler ist
klein, aber etwa 4541-mal groesser als die vorab gebundene Toleranz.

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

Nach Werkzeugende lief kein W1-Headless-Prozess. Es entstanden keine
Report-, Rohpayload- oder Forschungslaufdateien. Lauf 197 blieb unberuehrt.

## Technische Folgerung

Die W1-K-Kontrolle war methodisch richtig, das Paar bei dieser Abweichung zu
verwerfen. Die Grenze darf jetzt nicht nachtraeglich von `1e-12` auf einen
zum beobachteten Wert passenden Schwellwert angehoben werden.

Die robustere Korrektur lautet:

```text
ein kanonisches Tonsegment erzeugen
-> exakt dieselben Samplewerte fuer A0 und C0 verwenden
-> nur die Position des Segments im gemeinsamen 9600-Sample-Puffer aendern
```

Damit bleibt die unabhaengige Variation die Zeitlage. Signalform,
Samplewerte, Energie und aktive Laenge werden konstruktiv identisch, statt
nur ueber eine nachtraegliche Toleranz als aehnlich behandelt zu werden.

## Aussagegrenze

W1-M ist eine Quellen- und Kontrollweltdiagnose. Sie belegt keine
Feldzeitkopplungswirkung und keine Wahrnehmung, Nachhall, Feldzeit, Praegung,
Memory, Organisation, Semantik, Selbstregulation oder KI.

Der auditive Sequenzdigest muss zwischen A0 und C0 verschieden sein, weil
dieselbe Aktivitaet an unterschiedlichen Zeitfenstern liegt. Diese
beabsichtigte zeitliche Differenz ist kein Fehler. Der Fehler war
ausschliesslich die ungleiche Gesamtenergie.

## W1-M-Entscheidung

```text
reales Quellenpaar:                genau eins
visuelle Sequenzgleichheit:        exakt bestanden
Audioenergiegleichheit:            nicht bestanden
historische W1-K-Ursache:          audio_total_energy
Ursache eindeutig lokalisiert:     ja
Feldhandoff:                       nein
Prozessschluss:                    bestanden
Artefaktfreiheit:                  bestanden
Forschungslauf:                    nein
```

## Bester naechster Schritt

W1-N implementiert unter Fakes ein kanonisches wiederverwendetes Tonsegment
fuer die kontrollierte AV-Testquelle. A0 und C0 duerfen nur dessen
Sampleposition unterscheiden. Die Energiegrenze bleibt unveraendert bei
`1e-12`. W1-N startet keinen realen Browser; eine neue reale Quellenabnahme
benoetigt danach eine eigene Entscheidung.
