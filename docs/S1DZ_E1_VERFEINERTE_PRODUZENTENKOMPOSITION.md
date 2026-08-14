# S1-DZ: E1 verfeinerte Produzentenkomposition

## Status

Die private Komposition zwischen verfeinerter E1-Bildung, siebenarmiger
eingefrorener Probe und S1-DX-Ergebniscontainer ist implementiert und
synthetisch abgenommen. Der kanonische S1-DY-Einstieg bleibt geschlossen.
Es wurde keine kanonische Bildung, Probe oder Persistenz ausgefuehrt.

## Implementierung

```text
mcm_field_organism/e1_refined_chain_producer_composition.py
tests/test_e1_refined_chain_producer_composition.py
```

Normalisierter Implementierungsdigest:

```text
30c41cb3ec049e7fda200cb85dc9bfb7b63f67707eb05d65474c66d1d287ff8f
```

## Kompositionsgrenze

`compose_synthetic_e1_refined_chain_result(...)` verbraucht genau eine
synthetische S1-DV-Produktion mit `r1/r2/r4`. Fuer jedes Bildungsresultat
wird der uebergebene Probe-Runner genau einmal aufgerufen. Sein Ergebnis
muss sieben geordnete Feldendigests, aktive S/H-Vektoren, beide
Nach-Probe-Zustandsdigests und die exakten Ablationsreste tragen.

Seit S1-EA2 delegiert dieser synthetische Einstieg an einen gemeinsamen
privaten Kompositionskern. Der Kern akzeptiert nur eine bereits getrennt
validierte synthetische oder kanonisch-S1-DU-gebundene Produktion.

Die Komposition leitet daraus ab:

- fuenf geordnete Bildungszustandsdigests je Verfeinerung;
- sieben geordnete Probefelddigests je Verfeinerung;
- Zustands-, Gesamtbindungs- und S/H-Probenabstaende;
- R1/R2- und R2/R4-Reste fuer Zustand und Probe;
- Identitaets-, Bildungsablations-, Probeablations-, Fixed-Adapter- und
  Ressourcenreste;
- elf geordnete Pflichtkontrollen;
- genau die vorregistrierte S1-DS-Entscheidung im S1-DX-Container.

Eine veraenderte AB- oder BA-Zustandssignatur nach der Probe laesst die
Frozen-State-Kontrolle fehlschlagen und fuehrt deterministisch zu
`TECHNICALLY_INVALID`.

## Technische Abnahme

```text
5 fokussierte Tests
370 Tests im vollstaendigen E1-Verbund
OK
```

Die drei S1-EA-Pfade bleiben frei. Der bestehende S1-DN-Bericht blieb
unveraendert.

## Aussagegrenze

Die synthetischen Probevektoren sind Testfixtures. S1-DZ weist weder eine
kanonische AV-Zustandsbildung noch Transfer, Memory, Semantik, Organisation,
Topologie, Selbstregulation oder KI nach.

## Anschluss

S1-EA0 implementiert nun den siebenarmigen eingefrorenen Probe-Runner und
weist seine Runtime-Eigenschaften auf synthetischen Zustaenden nach. Der
kanonische 84-Knoten-Anschluss bleibt getrennt offen.
