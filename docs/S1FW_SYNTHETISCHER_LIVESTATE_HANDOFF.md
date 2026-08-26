# S1-FW: Synthetischer Live-State-Handoff

## Umsetzung

S1-FW verwendet die 15 typisierten S1-FJ-Formationsergebnisse. Aus ihnen
werden die zwoelf fuer Proben zulaessigen lebenden `output_state`-Objekte
direkt uebernommen. Kein Digest und kein Capture-Vektor rekonstruiert einen
Zustand.

Die zwoelf Objekte werden auf alle 30 S1-FV-Slots verteilt:

```text
aktive AB/BA-Zustaende              je 3 Verwendungen
formationsablatierte AB/BA-Zustaende je 1 Verwendung
P0                                   kein Zustand
```

Fuer die sechs Fixed-Adapter-Slots berechnet der vorhandene reine
Adaptergenerator aus dem exakten aktiven Zustand ein typisiertes
Kantenratenobjekt. Diese Berechnung fuehrt keinen Feldschritt aus.

## Abnahme

- 12 Quellobjekte und 12 unterschiedliche Objektidentitaeten;
- 30 vollstaendige Slot-Handoffs;
- 24 zustandsgebundene und 6 zustandslose P0-Slots;
- 6 typisierte Fixed-Adapter;
- alle Zustandsdigests vor und nach dem Routing unveraendert;
- exakt null Feldschritte;
- kein realer Probeadapter und keine Persistenz.

Entscheidung:
`SYNTHETIC_LIVE_STATE_TEN_ROLE_HANDOFF_CONFIRMED_REAL_ADAPTER_CLOSED`.

## Bedeutung und Grenze

Der zuvor fehlende Objekt-Handoff und die zehnrollige Verdrahtung sind
synthetisch funktionsfaehig. Damit ist noch keine reale Probe ausgefuehrt und
keine Feldantwort gemessen. Es folgt insbesondere kein E1-, Memory-,
Feldzeit-, Reaktivierungs-, Organisations- oder KI-Nachweis.

## Bester naechster Schritt

S1-FX sollte den fehlenden realen Fixed-Adapter-Probewrapper und ein gemeinsames
typisiertes Receipt-Schema fuer P0, Frozen-E1 und Fixed-Adapter statisch binden.
Danach kann dieser Adapterpfad synthetisch mit zaehlenden Nullschritt-Kernen
abgenommen werden. Noch kein Realrunner oder Feldlauf.
