# W1-P: Kanonischer AV-Feldpaarweg unter Fakes

Stand: 2026-08-08

Entscheidung: `W1P_CANONICAL_FIELD_PAIR_IMPLEMENTED_UNDER_FAKES`

Forschungslauf: nein

Realer Browser gestartet: nein

## Auftrag

W1-P bindet die in W1-O real bestaetigte kanonische AV-Quelle an den
vorhandenen A0/C0-Feldpaarweg. Die Bindung wird ausschliesslich unter Fakes
geprueft. W1-O wird nicht wiederholt und es wird kein reales Konsolenwerkzeug
angelegt.

## Getrennte Paaridentitaet

Der historische W1-J-Einstieg bleibt erhalten:

```text
run_browser_payload_timing_pair()
browser.payload.timing-pair.v1
```

W1-P ergaenzt getrennt:

```text
run_browser_payload_canonical_timing_pair()
browser.payload.canonical-timing-pair.v1
```

Beide Einstiege verwenden dieselben bestehenden Vertraege, Rezeptoren,
Feldsubstrate, Inventare, Toleranzen und skalaren Comparatoren. Sie
unterscheiden sich nur in Paaridentitaet und fest gebundenen Assetdigests.

Der kanonische Einstieg akzeptiert ausschliesslich:

```text
index.html: 0ceecd1e9e346ce262e8e0cb41efe52fe2f3e42e00c1d6298fdf23becc451d3b
styles.css: f026fce8f826fb7364a11b1b05ad4acb3dd37aed7dede5453c6f82cbf497b594
world.js:   7e903402e16f3f11423116ab3112d452c3815fb6006ed18537963fd887c956bb
```

Historische Assets werden am kanonischen Einstieg vor jedem Factory-Aufruf
abgelehnt. Dadurch kreuzen W1-J/W1-K und W1-P ihre Quellenidentitaeten nicht.

## Kanonische Fake-Quelle

Der Fake bildet die W1-N/W1-O-Samplelogik nach. In der einzigen aktiven
Phase beginnt die Sinusform am lokalen Index null:

```text
wave_index = sample - active_phase_start
```

Das identische lokale Segment liegt bei A0 in `[2400, 4800)` und bei C0 in
`[4800, 7200)`. Nur seine Zeitposition wechselt.

## Fake-Abnahme

Das kanonische Fake-Paar bestaetigt:

- exakt gleiche visuelle Rezeptorwertfolgen;
- Audioenergiegleichheit innerhalb der unveraenderten Grenze `1e-12`;
- 111 auditive und 36 visuelle Rezeptorzustaende pro Arm;
- 147 Feldzuweisungen pro Arm;
- zwei frische Felder mit identischer Anatomie;
- positive skalare L1- und Linf-Differenz der Feldendzustaende;
- Entscheidung `TECHNICAL_FIELD_INPUT_TIMING_SENSITIVITY_OBSERVED`;
- inaktive Afterimage-Lage;
- vollstaendig geschlossene Fake-Lifecycles;
- keine Rohpayloadhaltung.

Der fokussierte Verbund besteht mit `32 passed`. Die bekannte
Pytest-Cachewarnung `WinError 183` betrifft nur den lokalen Cachepfad.

## Aussagegrenze

W1-P zeigt unter Fakes nur, dass die kanonische Quelle den vorhandenen
technischen Feldcomparator erreicht und eine kontrollierte Zeitverschiebung
in diesem Vertrag skalar unterscheidbar bleibt. Es gibt keinen realen
Feldbefund.

W1-P belegt weder Wahrnehmung noch Nachhall, Feldzeit, Ueberreizung,
Regulation, Praegung, Memory, Organisation, Semantik, Selbstregulation oder
KI.

## Bester naechster Schritt

W1-Q bindet ein getrenntes schleifen- und reportfreies Einmalwerkzeug an
`run_browser_payload_canonical_timing_pair()` und nimmt es zunaechst statisch
ab. Erst danach darf genau ein reales kanonisches Feldpaar ohne Laufnummer
ausgefuehrt werden. Unabhaengig vom Ergebnis gibt es keine automatische
Wiederholung.
