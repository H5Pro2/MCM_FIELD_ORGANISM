# Z1: Lauf-196-Einstieg und Ausfuehrungssperre

Stand: 2026-08-06

## Status

Der separate one-shot Einstieg fuer Lauf 196 ist implementiert und
ausschliesslich mit einem synthetischen technischen Vollpaket vorgeprueft. Die
reale F3/B3-Matrix wurde inzwischen genau einmal als
[Lauf 196](forschung/LAUF_196_Z1_GEMEINSAMER_SUPPORT_FELDTRAJEKTORIEN.md)
ausgefuehrt.

## Fester Laufweg

`mcm_field_organism/mcm_f3_z1_run196.py` bindet unveraendert:

```text
vollstaendige reale Z1-Technikmatrix
-> vollstaendige Reproduktions- und Invariantenkontrollen
-> deterministische Abschlussgruppen-Supportprojektion
-> alle fuenf Supportkontrollen muessen bestehen
-> unveraenderte Z1-Auswertung
-> Lauf-ID lauf-196
-> skalares JSON ohne Trajektorien
```

Der Lauf bricht vor der Sachauswertung ab, falls eine Supportkontrolle
scheitert. Es gibt keinen Rueckfall auf die Lauf-195-Abtastung und keine
Interpolation fehlender Abschlusspunkte.

## Persistierte Supportmessungen

Fuer jeden der sieben Arme werden nur folgende technischen Werte ausgegeben:

- Arm-ID;
- Zahl der vollstaendigen technischen Samples;
- Zahl der Entscheidungssamples;
- Kennzeichen, ob beide Supports identisch waren.

Vollstaendige technische und gefilterte S/H/M-Trajektorien bleiben
nichtpersistente Laufdaten.

## Ergebnisvertrag

```text
run_id:        lauf-196
correction_id: mcm.f3.z1.completion-support.v1
schema_id:     mcm.f3.z1.run196.v1
```

Die wissenschaftliche Auswertung verwendet exakt dieselben Distanzfunktionen,
Huellen, 5-Prozent-Grenzen, Teilungsstopplinien und B3-Regeln wie Lauf 195.

## One-shot Werkzeug

`tools/run_mcm_f3_z1_196.py` schreibt ausschliesslich:

```text
reports/mcm_f3_z1_lauf_196.json
```

Ist diese Datei bereits vorhanden, wird vor jeder Ausfuehrung abgebrochen.
Der historische Lauf-195-Einstieg und sein Artefakt werden weder gelesen noch
veraendert.

## Technische Pruefung

Mit einem synthetischen Vollpaket sind bestaetigt:

- Supportprojektion erfolgt vor der unveraenderten Auswertung;
- alle fuenf Supportkontrollen werden gefordert;
- der partitionierte Arm berichtet 183 Voll- und 92 Entscheidungssamples;
- das Ergebnis besitzt die feste Lauf-ID und das feste Schema;
- das JSON enthaelt keinen Schluessel `trajectories`;
- die reale technische Matrix wird im Test ersetzt und nicht aufgerufen.

Zusammen mit den bestehenden Z1/F3-Tests bestehen 52 fokussierte Tests.

## Aussagegrenze

Die fertige Laufsteuerung war vor ihrer Ausfuehrung kein Sachbefund. Lauf 196
hat inzwischen Teilungsinvarianz, Weltzeitbindung und Ordnungssensitivitaet
fuer den festen Korridor klassifiziert. Relative Feldzeit, Memory,
Organisation, Topologie, Semantik, Selbstregulation oder KI sind weiterhin
nicht nachgewiesen.

## Bester naechster Schritt

Den unveraenderten one-shot Einstieg `tools/run_mcm_f3_z1_196.py` genau
einmal ausfuehren. Bei einem technischen Abbruch keine Schwellen-, Quellen-
oder Metrikaenderung vornehmen. Bei erfolgreichem Abschluss das skalare
Artefakt unveraendert als Lauf 196 dokumentieren.
