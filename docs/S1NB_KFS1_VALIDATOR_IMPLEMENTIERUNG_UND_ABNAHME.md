# S1-NB KFS-1 Validator-Implementierung und Abnahme

## Status

S1-NB implementiert ausschliesslich den in S1-NA gebundenen statischen
KFS-1-Schema-Validator und nimmt ihn einmal fokussiert ab. Der Validator ist
keine KFS-1-Dynamik und besitzt keinen Zugriff auf das MCM-Feld, Runner,
Medienquellen, Browser, Netzwerk oder Reports.

## Implementierte Dateien

| Datei | SHA-256 |
|---|---|
| `mcm_field_organism/kfs1_schema_validator.py` | `8a553409ef12ca1778e92e9b614bcc528f6445d4807ed6b75c93af26220a0a87` |
| `tests/kfs1_s1nb_fixtures.py` | `3779a1a7a53c7f50da5c70f0e049a25cf30a39b1c1761ddff9a263f96ecd5019` |
| `tests/test_kfs1_s1nb_schema_validator.py` | `fe833f0863f9ecfac746b89a6b9aa26ec940a353dc15dc5683dd995184be72a4` |

Das Produktionsmodul enthaelt nur kanonische JSON-Serialisierung,
SHA-256-Digestbildung, eine unveraenderliche Registry, einen unveraenderlichen
Validierungsbeleg und die statischen S1-MY-/S1-MZ-Pruefungen.

## Materialisierte Abnahme

Der testseitige Katalog umfasst exakt:

- 2 positive Minimalfixtures;
- 18 Einzeldefekt-Fixtures;
- 3 Mehrfachdefekt-Fixtures;
- 23 unabhaengig gebildete Erwartungsrecords.

Die einmalige Abnahme wurde mit folgendem fokussierten Aufruf ausgefuehrt:

```text
python -m unittest tests.test_kfs1_s1nb_schema_validator
```

Ergebnis:

```text
Ran 12 tests in 0.015s
OK
```

Dabei wurden 27 Validatoraufrufe ausgefuehrt. Das gebundene Maximum von 64
wurde eingehalten. Es gab genau null MCM-Feldschritte und keine Runner-,
Audio-, Video-, Browser-, Netzwerk- oder Reportaufrufe.

## Technischer Befund

Die Abnahme bestaetigt innerhalb der gebundenen Fixturegrenze:

- beide positiven Minimalrecords werden reproduzierbar akzeptiert;
- jeder Einzeldefekt liefert genau seinen vorregistrierten Fehlercode;
- Mehrfachdefekte liefern nur sicher feststellbare, sortierte Fehlercodes;
- unlesbare und nichtkanonische Bytes werden nicht repariert;
- originale Eingabebytes bleiben ueber ihren Digest identifizierbar;
- Registry und Validierungsbelege sind unveraenderlich;
- Record- und Belegdigest sind getrennt und nicht selbstbeziehend;
- abweichende Expositionshistorien werden fail-closed abgelehnt.

## Aussagegrenze

S1-NB belegt nur die Funktionsfaehigkeit des statischen Validators gegen die
gebundenen Testdaten. Der Schritt belegt keine KFS-1-Wirkung, keine
Kohaerenzaenderung, keine spaetere Aufnahmeaenderung und keinen Befund zur
hypothetischen MCM-Memory.

Es wurden keine Kandidatengleichung, keine Dynamikparameter und keine
Runtimeintegration eingefuehrt.

## Naechster erlaubter Schritt

Der naechste Schritt ist S1-NC, ausschliesslich als statischer Vertrag fuer
das lokale KFS-1-Uebergangsalphabet und seine kausale Eigentuemerschaft. Er
darf festlegen, welche Wechsel zwischen `free`, `bound` und `blocked`
strukturell zulaessig sind, welches lokale Ereignis einen Wechsel ausloesen
duerfte und welche Uebergaenge verboten bleiben. Gleichung, Rate, Parameter,
Runtimeintegration, Feldlauf und Funktionsentscheidung bleiben gesperrt.
