# S1-DU: E1 kanonischer AB/BA-Verfeinerungspreflight

## Status

Der S1-DT-Planer ist nichtausfuehrend auf die kanonischen kontrollierten
AB- und BA-Rezeptorfolgen angewendet worden. Dabei wurden nur Quellenrollen,
Zeitplaene, Handoffs und Integrale gebildet. Kein E1-Zustand und kein S/H-
Feld wurde erzeugt oder fortgeschrieben; keine Probe wurde ausgefuehrt.

## Implementierung

```text
mcm_field_organism/e1_canonical_refinement_preflight.py
tests/test_e1_canonical_refinement_preflight.py
```

Normalisierter Implementierungsdigest:

```text
19d4c2087f93bb95829288da0d48ddc95bc99aa750bc4a486de3e919dec4199b
```

Preflight-Digest:

```text
00b7df0cf1d98286e0f5f75d8a0b27b7176f152bc7065e0320421d521e29a032
```

## Kanonisches Inventar

AB und BA besitzen jeweils:

```text
220 Rezeptorframesupports
200 eindeutige Abschlusszeiten
Horizont 0 bis 2_000_000 Ticks
r1 = 200 Schritte
r2 = 400 Schritte
r4 = 800 Schritte
```

Die Abschlusszeiten beginnen bei Tick `10_000`, enden bei Tick `2_000_000`
und sind fuer AB und BA identisch. Jeder Support wird in jeder Verfeinerung
genau einmal zugeordnet.

## Gleiche Weltmenge

Die bereits gebundenen Modalaudits bestaetigen fuer AB und BA identische:

- Payloadinventare;
- Quellsupportinventare;
- Organismus-Zeitplatzinventare;
- Gesamtmasse und quadratische Energie.

Der neue Preflight bestaetigt zusaetzlich fuer `r1/r2/r4` identische
Schrittgitter, Abschlusszeiten und Kontaktintegrale:

```text
signiert    = 14.328373475671894
absolut     = 14.328373475671894
quadratisch =  3.293282702508704
```

## Erhaltene Zeitordnungsdifferenz

AB und BA duerfen nicht denselben geordneten Pfad besitzen. Das ist im
Preflight sichtbar:

```text
AB-Plandigest = 5657cb57c136a6093275f41278a1fe261ccb6b806803bdf33086e14a697adb9b
BA-Plandigest = 2c0406398d6bc38b508844ae8d1face022630ea2d85297f0dab994e87d2d761c
```

Auch die geordneten Kontaktdigests und Handoffdigests unterscheiden sich.
Damit bleibt nur die vorgesehene AB-/BA-Zeitordnung verschieden, waehrend
die fuer den neuen Numerikvergleich erforderlichen Mengenrollen gleich
bleiben.

## Freigabegrenze

Der Preflight erlaubt nur die naechste Implementierung. Er erlaubt nicht:

- einen kanonischen E1-, History- oder Probelauf;
- eine Wiederholung von S1-DI oder S1-DQ;
- einen Befund zur Zustandsbildung;
- Memory- oder staerkere Claims.

## Technische Abnahme

```text
7 fokussierte Tests
335 Tests im vollstaendigen E1-Verbund
OK
```

## Bester naechster Schritt

S1-DV implementiert einen privaten verfeinerten E1-Bildungsrunner und nimmt
ihn ausschliesslich mit kleinen synthetischen Quellen, Feldern und neutralen
E1-Zustaenden ab. Er muss `r1/r2/r4`, Identitaetswiederholung,
Bildungsablation, Frische, Ressourcenbilanz und reine E1-Ausgabe beherrschen.
Die kanonischen AB-/BA-Plaene bleiben weiterhin unausgefuehrt.

## Anschlussstatus nach S1-DV

S1-DV hat den privaten Bildungsrunner inzwischen ausschliesslich synthetisch
implementiert und abgenommen. Die kanonischen Plaene blieben unausgefuehrt.
Der aktuelle Anschluss steht in
`S1DV_E1_VERFEINERTER_SYNTHETISCHER_BILDUNGSRUNNER.md`.
