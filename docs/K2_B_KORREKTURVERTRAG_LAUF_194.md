# K2-B: Korrekturvertrag fuer Lauf 194

Stand: 2026-08-06

Lauf 193 brach vor jeder Messung wegen einer fest codierten alten
Organismus-Clock im passiven Trajektorienhelfer ab.

Die einzige zulaessige Korrektur lautet:

```text
step clock = clock_id der gebundenen ReceptorTimeSequence
```

Diese Ableitung ist technische Handoff-Metadatenweitergabe. Sie veraendert
weder Organismuszustand noch Dynamik oder Beobachtungsentscheidung.

Der vollstaendige Forschungsvertrag bleibt:

- `docs/K2_B_F3_FUNKTIONSVERLUST_UND_WIEDERVERWENDUNG_VORREGISTRIERUNG.md`

Erst eine technisch erfolgreiche Ausfuehrung nach diesem Korrekturvertrag
erzeugt Lauf 194.
