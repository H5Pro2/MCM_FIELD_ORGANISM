# Lauf 194

## Forschungsfrage

Geprueft wurde, ob normale B-Weltgeschichte eine zuvor durch A erzeugte
F3-Zusatzwirkung spezifisch verdraengt und gleichzeitig im selben endlichen
M-Zustandsraum eine andere B-Wirkung erzeugt.

Vertraege:

- `docs/K2_B_F3_FUNKTIONSVERLUST_UND_WIEDERVERWENDUNG_VORREGISTRIERUNG.md`
- `docs/K2_B_KORREKTURVERTRAG_LAUF_194.md`

Lauf 193 war vor jeder Messung an einer falschen technischen Clock im
passiven Trajektorienhelfer abgebrochen. Lauf 194 aenderte ausschliesslich
diese Clock-Weitergabe.

## F3-Messungen

```text
Checkpoint     0          1          2          3          4

A-Rest unter B
Kontrast    4.3903e-4  5.6269e-5  2.4147e-5  1.6080e-5  1.1259e-5
Retention   1.000000   0.128168   0.055001   0.036627   0.025646

A-Rest unter Unterbrechung
Kontrast    4.3903e-4  5.6647e-5  2.4170e-5  1.6122e-5  1.1311e-5
Retention   1.000000   0.129029   0.055053   0.036722   0.025764

neue B-Wirkung
Kontrast    0.0         3.2637e-4  3.7884e-4  3.9236e-4  4.0009e-4
```

Nach vier B-Schritten lag die alte A-Wirkung bei `0.025646` ihres
Ausgangskontrasts und damit unter der vorregistrierten Funktionsverlustgrenze
von `0.05`. Unter der zeitgleichen Unterbrechung lag sie jedoch nahezu gleich
bei `0.025764`.

B besass daher keinen vorregistrierten zweifachen Verdraengungsvorteil gegen
passive Entwicklung. Gleichzeitig lag die neue B-Wirkung mit
`0.00040008693012472986` deutlich ueber der numerischen Effektgrenze.

## Lineare Feldbaseline

Die lineare gekoppelte Feldbaseline zeigte denselben Grundverlauf:

```text
finale A-Retention unter B:             0.02774966341208814
finale A-Retention unter Unterbrechung: 0.02774966341209655
finale neue B-Wirkung:                  0.0003745778800386349
```

In der linearen Form waren B- und Unterbrechungsretention bis auf
Fließkommaarithmetik gleich. Das maximale relative Residuum der gesamten
F3-Kontrastkurve zur linearen Feldbaseline betrug `0.0604342612223017`.

## Kontrollen

Alle gebundenen Quellendigests, Beobachtungstakte und Zustandsinvarianten
blieben gueltig. Der anfaengliche A-Effekt und der finale B-Effekt lagen
oberhalb der vorregistrierten numerischen Grenze.

## Entscheidung

```text
decision: PASSIVE_LOSS_AND_REUSE
```

Die bekannte F3-Baseline kann im selben endlichen M-Zustandsraum nacheinander
unterschiedliche weltbedingte Wirkungsanteile tragen. Der alte Anteil wird im
geprueften Korridor jedoch nicht durch B spezifisch verdraengt. Er verliert
seine Probe-Wirkung nahezu identisch unter B und unter einer gleich langen
Unterbrechung. Der Funktionsverlust ist damit passive Feldrelaxation, keine
konkurrierende Reorganisation.

## Aussagegrenze

- Kein Nachweis von organischem Vergessen oder funktionaler Loesung durch
  Konkurrenz.
- Kein E4- oder Rekonfigurationsbefund.
- Kein Nachweis von Ressourcenfreigabe; die Gesamtmasse ist nur technisch
  erhalten.
- Kein Memory-, Feldzeitverdichtungs-, Organisations-, Topologie-, Semantik-
  oder KI-Claim.
- Positiv belegt ist nur technische passive Verlust- und
  Wiederverwendungsfaehigkeit der bekannten Feldbaseline.

## Ergebnisartefakt

```text
reports/mcm_f3_k2b_lauf_194.json
```

## Bester naechster Schritt

K2-B wird nicht durch weitere B-Dauern oder staerkere Anregung optimiert.
Als naechstes wird der bereits im Projekt angelegte MINI_DIO-Zeitkontext
statisch auf die heutige gemeinsame Feldruntime uebertragen: Welche
operationale innere Entwicklungsordnung blieb dort nach Trennung von Ticks,
Kontakthaeufigkeit, Leaky-Zeit und festen Feldmoden tatsaechlich uebrig?
