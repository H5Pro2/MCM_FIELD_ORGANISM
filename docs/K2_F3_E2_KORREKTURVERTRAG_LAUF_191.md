# K2/F3 E2: Korrekturvertrag fuer Lauf 191

Stand: 2026-08-06

## Zweck

Lauf 190 endete nach der Armrechnung beim JSON-Schreiben ohne Artefakt. Lauf
191 uebernimmt den wissenschaftlichen Vertrag aus
`K2_F3_E2_GEOMETRISCHE_M_KAUSALITAET_VORREGISTRIERUNG.md` byteinhaltlich in
allen fachlichen Rollen.

## Einzige Aenderung

```python
tuple((key, bool(value)) for key, value in controls)
```

Die Konvertierung erfolgt erst im passiven Observerergebnis. Sie liest keine
Feldwerte zur Auswahl, veraendert keinen Kontrollwahrheitswert und wird nicht
an die Runtime zurueckgegeben.

Unveraendert bleiben:

- beide Geschichtsdigests und der gemeinsame Probedigest;
- 84 Spiegelpaare und beide 36-Orte-Masken samt Digests;
- S/H-Angleichung;
- `lambda_sm=1.0`, `kappa=0.5`, `eta=1.0`, 4n;
- alle zwoelf Arme;
- alle neun fachlichen Kontrollrollen pro Gesamtvertrag;
- Entscheidungs- und Nichtclaimgrenzen.

## Ausfuehrungsgrenze

Vor Lauf 191 muss ein technischer Test bestaetigen, dass auch ein
`numpy.bool_` als natives JSON-kompatibles Python-`bool` ausgegeben wird.
Danach darf der korrigierte Einmal-Runner genau ein Ergebnisartefakt
`reports/mcm_f3_geometry_lauf_191.json` erzeugen.
