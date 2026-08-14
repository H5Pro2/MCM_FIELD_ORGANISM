# S1-EC88: Statische r4/r8-Budget- und Objektinventur

## Quellen

EC88 liest ausschliesslich die bestehenden EC52-Slotbindungen, den
EC27-n2-Bildungsplansatz, den EB1-Probeplansatz und den geschlossenen
EC87-Ergaenzungsvertrag. Kein Slot wird ausgefuehrt und kein Feldzustand
veraendert.

## Exakte Schrittbudgets

`r4`:

- 804 Schritte je Bildung, vier Bildungen: 3.216;
- 400 Schritte je Probe, acht Proben: 3.200;
- insgesamt: 6.416 Feldschritte.

`r8`:

- 1.608 Schritte je Bildung, vier Bildungen: 6.432;
- 800 Schritte je Probe, acht Proben: 6.400;
- insgesamt: 12.832 Feldschritte.

Gemeinsam:

- 9.648 Bildungsschritte;
- 9.600 Probeschritte;
- 19.248 Feldschritte.

Beide Verfeinerungen binden dieselben acht Rollen und vier Zustandsrollen.
Die Bildung umfasst jeweils 220 Quellsupports, die Probe 110; alle Supports
sind genau einmal zugewiesen.

## Ressourcen und offene technische Grenzen

Die bisherigen Mindestgates von 4 GiB freiem Arbeitsspeicher und 1 GiB
freiem Datentraeger bleiben als Untergrenze gebunden. Aus den Plaenen kann
jedoch keine belastbare Laufzeitgrenze abgeleitet werden.

EC52 enthaelt abstrakte `r4/r8`-Slots und die Plaene sind konkret vorhanden.
EC59, EC67 und EC84 sind derzeit aber fest auf `n2/r2` typisiert. Konkrete
Objekt-Handoffs und getrennte Laufzeit-Preflights fuer `r4` und `r8` fehlen.

Entscheidung:
`R4_R8_BUDGETS_BOUND_HANDOFFS_AND_RUNTIME_CAPS_MISSING`

## Aussagegrenze

EC88 ist eine Last- und Objektinventur. Es autorisiert keine Ausfuehrung und
liefert keine neuen Messwerte. EC46 bleibt gesperrt. Es besteht kein
Memory-, Feldzeit-, Organisations-, Topologie-, Semantik-,
Selbstregulations- oder KI-Nachweis.

Am besten geht es mit S1-EC89 weiter: zuerst getrennte, nicht ausfuehrende
`n2/r4`- und `n2/r8`-Objekt-Handoffs aus den vorhandenen EC52-/EC27-/EB1-
Objekten bilden und synthetisch pruefen. Laufzeitgrenzen und Freigaben erst
danach festlegen.
