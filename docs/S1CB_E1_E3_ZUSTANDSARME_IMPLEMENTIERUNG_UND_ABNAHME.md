# S1-CB: E1 E3-Zustandsarme Implementierung und Abnahme

## Status

Die in S1-CA getrennten Zustandsarme `HOLD`, `RELEASE`, `COMPETE` und
`NEUTRAL` sind privat implementiert und technisch abgenommen. Die spaetere
identische Feldprobe ist nicht Bestandteil von S1-CB. Daher liegt noch keine
abschliessende E3-Entscheidung und kein Memory-, Vergessens-, Lern-,
Organismus- oder KI-Befund vor.

## Implementierung

```text
mcm_field_organism/e1_e3_state_arms.py
tests/test_e1_e3_state_arms.py
```

Die Rollen werden weder aus dem Paket noch aus `current_api` exportiert.
E1 bleibt eine opt-in Engineeringmechanik ausserhalb des produktiven
Feldschemas.

## Vier Zustandsarme

```text
HOLD       tiefe unveraenderte Kopie des linken S1-BX-Zustands
RELEASE    uniforme Nullkontaktfreigabe bis t = 4 s
COMPETE    RELEASE plus acht rechte Kontakte bei ablatierter Rueckwirkung
NEUTRAL    neutraler E1-Anfang plus dieselben acht rechten Kontakte
```

COMPETE und NEUTRAL laufen auf getrennten frischen, uniformen
Drei-Knoten-Feldern. Die E1-Rueckwirkung ist ausgeschaltet, sodass beide
Feldverlaeufe nicht bereits durch ihre unterschiedlichen E1-Zustaende
veraendert werden.

## Analytische Freigabekontrolle

Die Checkpoints sind unveraenderlich auf `0`, `1`, `4` und `8` Sekunden
festgelegt. Auf einer uniformen Feldlage verschwindet die neue
Bindungsnachfrage. Jede Kante wird gegen

```text
b_e(t) = b_e(0) * exp(-0.25 * t)
```

geprueft. Ein nichtuniformes Feld wird fuer diesen Arm abgelehnt, weil es die
reine Freigabe mit neuer Bindung vermischen wuerde.

## Rohmetriken

Der private Ergebniscontainer fuehrt ausschliesslich:

```text
release_analytic_linf
resource_budget_linf
release_total_binding_drop
compete_release_binding_linf
compete_total_binding_rebound
compete_neutral_binding_linf
```

Die ersten beiden Werte kontrollieren analytische Freigabe und Bilanz. Die
folgenden Werte beschreiben nur die Zustandsunterschiede und die erneute
Nettobindung nach der konkurrierenden Geschichte.

## Technische Abnahme

Fokussiert:

```text
python -m unittest -v tests.test_e1_e3_state_arms

10 tests
OK
```

Gemeinsam mit dem bisherigen E1-, S/H-, Nachhall- und Consumer-Verbund,
jedoch ohne Wiederholung des S1-BZ-Einmallaufs:

```text
88 tests
OK
```

Geprueft wurden:

- exakte registrierte Freigabezeiten und analytische Exponentialkurve;
- streng monotone Abnahme positiver Bindungen unter uniformer Freigabe;
- erhaltenes endliches Ressourcenbudget;
- erneute Nettobindung und veraenderte Kantenverteilung in COMPETE;
- Trennung von COMPETE und neutraler Neuinitialisierung;
- unveraenderte Eingaben, tiefe Armtrennung und frisches Anfangsfeld;
- Ablehnung eines nichtuniformen Freigabefeldes;
- private API-Grenze.

Die begrenzte interne Bereitschaft lautet:

```text
E3_STATE_ARMS_READY_FOR_PROBE
```

Dies ist absichtlich keine der abschliessenden S1-CA-E3-Entscheidungen.

## Aussagegrenze

S1-CB zeigt, dass die programmierte endliche E1-Ressource technisch
freigegeben und nach einer konkurrierenden Feldgeschichte erneut gebunden
werden kann. Weil Freigabe- und Bindungsgleichung konstruiert wurden, ist
dieser Befund allein kein Nachweis von Vergessen, Memory oder organischer
Entwicklung.

Noch offen ist, ob HOLD, RELEASE und COMPETE bei identischer eingefrorener
Probe kontrolliert verschiedene spaetere S/H-Feldwirkungen erzeugen und ob
alle P0-, Ablations-, Fixed-Gain- und Numerikkontrollen gleichzeitig
bestehen.

## Bester naechster Schritt

S1-CC bindet die genaue Probe- und Ergebniszusammensetzung fuer HOLD,
RELEASE und COMPETE statisch. S1-CD implementiert als naechsten Schritt den
privaten Kompositor und fuehrt erst nach den Vertragspruefungen den
vorregistrierten E3-Probelauf genau einmal aus.
