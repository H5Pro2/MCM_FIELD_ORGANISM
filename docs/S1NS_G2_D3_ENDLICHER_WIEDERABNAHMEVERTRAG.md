# S1-NS G2/D3 endlicher Wiederabnahmevertrag

## Status

S1-NS bindet ausschliesslich eine einmalige Wiederabnahme der nach dem
fehlgeschlagenen S1-NR-Lauf lokal korrigierten Drei-Dateien-Fassung. Dieser
Schritt fuehrt keinen Test aus und veraendert weder Validator, Fixtures noch
Tests.

Entscheidung:

```text
G2_D3_CORRECTED_VALIDATOR_REACCEPTANCE_BOUND
```

## Anlass und unveraenderter Vertrag

S1-NR meldete genau einen unzulaessigen abgeleiteten Folgefehler fuer das
absichtlich fehlende Feld `candidate_class_id`. Die Implementierung wurde so
korrigiert, dass die Klassenidentitaet nur bei vorhandenem Feld geprueft wird.

Unveraendert bleiben:

- der S1-NP-Schema- und Fail-Closed-Vertrag;
- alle S1-NQ-Fixturebytes und Erwartungsdigests;
- alle 18 Einzel- und sechs Paarmutationen;
- alle erwarteten Fehlercodes;
- die drei oeffentlichen API-Rollen;
- bestehender KFS-1-, DTS-1-, Feld-, Runner- und Mediencode.

## Bitgleicher Preflight

S1-NT muss vor dem einzigen Python-Aufruf die SHA-256-Digests der drei Dateien
read-only pruefen:

```text
mcm_field_organism/g2_d3_schema_validator.py
666f38ef49ddfa1538a301f43f265d60e7e0f1f48834e3df0653551d03f18c0d

tests/g2_d3_s1nr_fixtures.py
76351b57709f2af5a249a76a48a8cd08a7ac51f5b79855e592f69087fd80724d

tests/test_g2_d3_s1nr_schema_validator.py
244aecbe65b057f22080503390e52fc8cdb20e9a4b713c093ca8e990bb8dcb87
```

Bei nur einer Abweichung gilt:

```text
G2_D3_REACCEPTANCE_PREFLIGHT_DIGEST_MISMATCH
```

Dann darf kein Test gestartet und keine Datei fuer den Lauf passend gemacht
werden.

## Einmalige S1-NT-Ausfuehrung

Nach bestandenem Preflight darf genau einmal ausgefuehrt werden:

```text
python -m unittest tests.test_g2_d3_s1nr_schema_validator
```

Erwartete technische Abnahme:

```text
Ran 10 tests
OK
```

Die Laufzeit ist kein Sachkriterium. Warnungen, Fehler, Abbrueche oder weniger
als zehn vollstaendig ausgefuehrte Testgruppen bedeuten eine nicht bestandene
Wiederabnahme.

## Endliches Budget

Innerhalb der Testabnahme bleiben die S1-NQ-Obergrenzen verbindlich:

```text
validate_g2_d3_anatomy_record: 64 Aufrufe
validate_g2_d3_f1_pair:         16 Aufrufe
MCM-Feldschritte:                0
Runner-/Medien-/Netzwerkaufrufe: 0
Report- oder Dateischreibzugriffe: 0
```

Zulaessig sind nur der read-only Digestpreflight und der eine gebundene
`unittest`-Prozess. Kein Gesamt-Testlauf, keine Coverage-Ausfuehrung und kein
zweiter fokussierter Lauf sind erlaubt.

## Entscheidungsregel

Nur bei bitgleichem Preflight und `10 tests, OK` lautet die Entscheidung:

```text
G2_D3_STATIC_VALIDATOR_ACCEPTED
```

Bei jedem anderen Ergebnis lautet sie:

```text
G2_D3_STATIC_VALIDATOR_REACCEPTANCE_FAILED
```

Nach einem Fehlschlag darf S1-NT weder reparieren noch erneut ausfuehren. Der
Befund wird mit unveraendertem Output dokumentiert und der Funktionspfad bleibt
geschlossen.

## Aussagegrenze

Auch eine erfolgreiche Wiederabnahme belegt nur die statische D3-Anatomie-,
Bilanz-, Digest-, Projektions- und Ablationspruefung. Sie belegt keine
G2-Admissibilitaet, Dynamik, Feldwirkung, Musterbildung, Lernfunktion oder
hypothetische MCM-Memory.

## Naechster erlaubter Schritt

S1-NT darf ausschliesslich den Digestpreflight ausfuehren, bei Erfolg den
fokussierten Test genau einmal starten und das Ergebnis dokumentieren. Alle
Admissibilitaets-, Transfer-, Bildungs- und Feldpfade bleiben bis zu einer
erfolgreichen Wiederabnahme gesperrt.
