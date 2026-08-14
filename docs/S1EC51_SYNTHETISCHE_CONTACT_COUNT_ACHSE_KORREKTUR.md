# S1-EC51: Synthetische Contact-Count-Achsen-Korrektur

## Ziel

EC51 behebt die in EC50 gefundene Scope-Luecke, ohne historische EC49-
Artefakte umzudeuten. Die Kontaktzahl wird als eigene typisierte Achse in
Handoffs, Reset-Slots, Rollenreceipts und Auswertung aufgenommen.

## Matrix

Die korrigierte synthetische Matrix umfasst:

```text
2 Kontaktzweige * 3 Verfeinerungen * 8 Rollen = 48 Probe-Slots
```

- Kontaktzweige: `n1`, `n2`;
- Verfeinerungen: `r2`, `r4`, `r8`;
- Rollen: die acht EC45-Common-Probe-Rollen.

Sechs getrennte Bildungshandoffs tragen je vier Zustandsreferenzen. Alle 48
Reset-Slots besitzen denselben initialen Felddigest, aber eindeutige
Slotidentitaeten einschliesslich Kontaktzahl.

## Getrennte synthetische Auswertung

Die Fixture konstruiert zwei getrennte technische Pfadfaelle:

- n1: `NO_MEASURABLE_COMMON_PROBE_DIFFERENCE`;
- n2: `NUMERICALLY_CLEAR_STATE_DEPENDENT_COMMON_PROBE_DIFFERENCE`.

Diese Werte sind synthetisch gewaehlt. Sie pruefen nur, dass n1 und n2
getrennt bis in die EC46-Entscheidungsfunktion gelangen. Sie sind keine
Messung und keine Forschungsevidenz.

## Ergebnis

- sechs kontaktgebundene Bildungshandoffs;
- 48 getrennte Reset-Slots;
- 48 kontaktgebundene Rollenreceipts;
- n1/n2 vollstaendig getrennt;
- null Feldschritte;
- keine Persistenz, Forschungsentscheidung oder Claims.

Zwoelf fokussierte gemeinsame Tests bestehen.

Fixture-Digest:
`913c9ee7bf379a6e2f0a4d9bb8ef1d04e15260bcf80673ebb150a0426d321129`

## Entscheidung

Die EC50-Adaptersperre ist behoben. Erlaubt ist jetzt ausschliesslich die
statische Bindung der kontaktbewussten Schnittstellen an reale Kerne. Eine
reale Bildung oder Probe bleibt gesperrt.

## Naechster Schritt

Am besten geht es mit S1-EC52 weiter: die sechs Bildungs- und 48 Probe-Slots
statisch an die vorhandenen realen Plan-, Fresh-Field-, P0- und Frozen-E1-
Schnittstellen binden. Noch keine Feldschritte.
