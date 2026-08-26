# W1-Q: Einmaliges reales kanonisches AV-Feldpaar

Stand: 2026-08-08

Entscheidung: `W1Q_REAL_CANONICAL_FIELD_TIMING_SENSITIVITY_OBSERVED`

Forschungslauf: nein

Reale Feldpaare: genau eins

Automatische Wiederholung: nein

## Auftrag

W1-Q bindet ein getrenntes Einmalwerkzeug an den in W1-P unter Fakes
abgenommenen kanonischen Feldpaarweg und fuehrt danach genau ein reales
A0/C0-Paar aus. W1-O und der historische W1-K-Pfad werden nicht wiederholt.

Das Werkzeug lautet:

```text
tools/run_browser_payload_canonical_timing_pair.py
```

Es ist schleifen- und reportfrei, schreibt keine Ergebnisdatei und startet
beim Import keinen Browser.

## Vorabnahme

Vor dem realen Start bestanden:

- feste Bindung an `controlled_av_canonical_audio_world`;
- Bindung an `run_browser_payload_canonical_timing_pair()`;
- Import ohne Browserstart;
- Abwesenheit von Schleifen, Reports und Z4-Bezug;
- kanonischer Fake-Feldvergleich;
- historische W1-J-Regression;
- oeffentlicher API-Export.

Der fokussierte Verbund bestand mit `33 passed`.

## Einmaliger realer Quellenbefund

Alle Quelleninvarianten hielten:

```text
visual_sequence_exact_match:        true
A0 audio_total_energy:              48.00000010990328
C0 audio_total_energy:              48.00000010990328
audio_total_energy_relative_error:  0.0
energy_relative_tolerance:          1e-12
assigned events per arm:            147
```

Beide Arme enthielten je 36 visuelle und 111 auditive Rezeptorzustaende.
Damit erreicht nur die beabsichtigte auditive Zeitverschiebung zwei frische
Felder; visuelle Folge, Gesamtenergie und Inventare bleiben angeglichen.

## Einmaliger realer Feldvergleich

Der reduzierte skalare Vergleich ergab:

```text
activation_final_l1:       0.020399902857823008
activation_final_linf:     0.008203063751618889
field_numerical_tolerance: 1e-12
afterimage_final_linf:     0.0
afterimage_a0_max_abs:     0.0
afterimage_c0_max_abs:     0.0
technical_decision:        TECHNICAL_FIELD_INPUT_TIMING_SENSITIVITY_OBSERVED
```

Die Feldsnapshot-Digests unterscheiden sich:

```text
A0: f22657377ec8f11b0cb5611316e18f9e1db527773b7ef7a9b82a7ecd00b6425d
C0: b79b618265af0a39c682a88925a1c845c785629a99a83d98ca5a4f01718fc20b
```

Dieser Befund zeigt eine reale technische Empfindlichkeit des bestehenden
Feldpfads gegenueber der kontrollierten Zeitlage eines energiegleichen
auditiven Segments. Er beschreibt eine Endzustandsdifferenz in diesem festen
Vertrag und keine weitergehende Funktion.

## Lifecycle und Artefaktgrenze

Beide Arme schlossen Seite, Kontext, Browser und Audiopuffer vollstaendig.
Pro Arm gab es drei lokale und keine blockierten Anfragen. Rohpayloads wurden
nicht gehalten. Nach Werkzeugende blieb kein W1-Q-Headless-Prozess zurueck.

Es entstanden keine Report-, Rohpayload- oder Forschungslaufdateien. Lauf
197 blieb unberuehrt. W1-Q wird nicht automatisch wiederholt.

## Aussagegrenze

Die technische Entscheidung ist kein Nachweis fuer Nachhall, Feldzeit,
Zeitwahrnehmung, Ueberreizung, Regulation, Praegung, Memory, Organisation,
Semantik, Selbstregulation oder KI. Insbesondere ist die in diesem Vertrag
inaktive Afterimage-Lage kein positiver oder negativer Memory-Befund.

## Bester naechster Schritt

W1-R charakterisiert das unveraenderte Feld zuerst unter synthetischen
kontrollierten Rezeptorfolgen hinsichtlich Belastung, Saettigung und Erholung.
Es wird noch keine adaptive Regulation implementiert. Zu binden sind
mindestens Reizstaerke, Reizdauer, Ruhefenster, Maximalaktivierung,
Erholungsrest und feste Gain-/Clipping-/Leaky-Gegenbaselines. Ein realer
Browserlauf gehoert nicht zu W1-R.
