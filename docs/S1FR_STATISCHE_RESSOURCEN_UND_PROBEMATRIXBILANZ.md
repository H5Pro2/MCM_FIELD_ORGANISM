# S1-FR: Statische Ressourcen- und Probematrixbilanz

## Frage

Wie gross ist die vollstaendige frische Formation-Common-Probe-Kette, und
kann sie verkleinert werden, ohne eine gebundene Kausalkontrolle oder die
numerische EC46-Pruefung zu verlieren?

## Bilanz

```text
                 Formation       Probe       Gesamt
r2               2.000           2.000        4.000 Feldschritte
r4               4.000           4.000        8.000 Feldschritte
r8               8.000           8.000       16.000 Feldschritte
gesamt           14.000          14.000       28.000 Feldschritte

Aufrufe          15              30           45
```

Bei 84 Feldknoten und 145 E1-Kanten betragen die konservativen statischen
Obergrenzen 2.352.000 Knoten-Schritt-Einheiten und 4.060.000
Kanten-Schritt-Einheiten. Die 15 gehaltenen Formationsergebnisse umfassen
maximal 2.175 Bindungswerte. Der bestehende Mindestwert von 4 GiB freiem RAM
bleibt gebunden. Eine exakte Python-Peak-RAM-Angabe wird nicht behauptet.

## Matrixentscheidung

Alle zehn Probe-Rollen werden benoetigt:

- P0 AB/BA fuer die Reset- und Ordnungsnullkontrolle;
- aktive E1-Zustaende AB/BA fuer den eigentlichen Ordnungskontrast;
- Rueckwirkungsablation AB/BA fuer die direkte Kausalitaetskontrolle;
- Formationsablation AB/BA fuer die Bildungskausalitaet;
- feste Adapter AB/BA fuer die bereits notwendige Alternativerklaerung.

Auch r2, r4 und r8 sind gemeinsam notwendig. EC46 verwendet r2->r4 als
groben und r4->r8 als feinen numerischen Rest. r8 ist zugleich der
Signalmesspunkt. Eine Entfernung einer Verfeinerung wuerde die bestehende
Konvergenzentscheidung veraendern.

Damit existiert innerhalb des unveraenderten S1-FP/EC46-Vertrags keine
kausal gleichwertige kleinere Matrix. Entscheidung:
`FULL_45_ARM_MATRIX_REQUIRED_STATIC_BUDGET_BOUND`.

## Grenze

S1-FR hat keinen Feldschritt ausgefuehrt, keine Besitzerautorisierung erzeugt
und keine Persistenz vorgenommen. Die Bilanz ist kein E1-, Memory-, Feldzeit-,
Reaktivierungs-, Organisations- oder KI-Nachweis.

## Bester naechster Schritt

S1-FS sollte einen statischen Einmallaufvertrag fuer exakt diese 45 Aufrufe
und maximal 28.000 Feldschritte formulieren. Er muss Same-session-Frische,
unmittelbaren Ressourcenpreflight, atomare Ergebnisrueckgabe, keinen Retry
und die getrennte Fixed-Adapter-Auswertung binden. Noch keine Ausfuehrung und
keine Besitzerautorisierung.
