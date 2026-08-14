# S1-AM: Gekoppelte `C_i -> S`-End-to-End-Ablation

Stand: 2026-08-11

Status: `TECHNISCHE_BASELINE_RUECKWIRKUNG_NACHGEWIESEN`

## Umfang

Die synthetische Weltfamilie wurde phasenweise zweimal verarbeitet:

```text
Rueckwirkung aus:
S/H-Feld -> naechste Phase

Rueckwirkung an:
S/H-Feld -> C_i-Akkommodation -> technische S-Projektion -> naechste Phase
```

Beide Pfade erhielten dieselben vier Phasen und dieselben Rezeptorsequenzen.
Die `C_i`-Rueckwirkung wurde nach jeder Phase auf die Aktivierung des
naechsten Feldzustands projiziert.

## Ergebnisse

```text
world.history.same
off_digest = 1c81971799fbeabfc731be22353c8a1037d046a7174d8b8dc6418d8b64fd6947
on_digest  = e657cb03f900a6fef87f91520da17954c83d9c6f6e873f2ccb4e7785bab1f46d
activation_linf = 0.012764141138514096
digest_equal = false

world.history.changed
off_digest = 8e4fcab5fac0246bb7157409944db6e08a8d022c132964c5dfd42528c13543e9
on_digest  = 5c84edb93b24b5f74943cdf709f799eb969d6971e1f40c7208735d076d9cfca7
activation_linf = 0.013640942718938842
digest_equal = false
```

## Einordnung

Der Rueckwirkungs-an-Pfad erzeugt andere spaetere technische Feldsnapshots
als der Rueckwirkungs-aus-Pfad. Damit ist die technische Kausalrolle der
implementierten `C_i`-Baseline in diesem begrenzten Adapterpfad sichtbar.

Der Befund zeigt nicht:

- Memory, Lernen oder Vergessen;
- autonome Organisation oder inneren Kontext;
- eine neue MCM-Natur;
- eine feldbasierte KI.

Die implementierte Rueckwirkung ist weiterhin eine bewusst entworfene
Engineering-Baseline und muss gegen leaky, Integrator, Gain, Hysterese und
F3 abgegrenzt werden.

## Laufgrenze

Die Projektion wird zwischen den Phasen in den technischen Feldzustand
uebernommen. Sie ist noch keine vollstaendige neue MCM-Gleichung und keine
Freigabe fuer reale Sensorik oder physische Weltkontakte.

## Bester naechster Schritt

Dieselbe End-to-End-Ablation gegen die leaky- und F3-Referenzen ausfuehren
und pruefen, ob `C_i` ueber die bekannten Baselinewirkungen hinaus eine
eigene technische Vorhersage liefert.
