# S2-NC: Kategorienbindung und numerische Abgrenzung

Qualifikations-ID: `s2nc-category-binding-qualification-20260906-01`.

## Beobachtung

Genau ein vorregistrierter Aufruf aus dem Workspace-Root:

```text
python -m unittest tests.test_s2nc_private_evaluation_categories -v
```

Ergebnis: `5/5`, Exit-Code `0`, `Ran 5 tests in 0.040s`, `OK`.
Status: `S2NC_CATEGORY_BINDING_QUALIFIED`. Kein Retry.
Kommando, Testliste und Vorhashes stehen in `qualification-plan.json`,
die Ausgabe in `test-output.txt`, Nachhashes und Abschluss in `postcheck.json`.
Alle 18 gebundenen Datei-Vor-/Nachhashes sind identisch.

## Enger Produktdiff

Nur der private Auswerter erhaelt eine eigene, exakt begrenzte Kategorienform:

- `KNOWN_EXACT`
- `KNOWN_FREQUENCY_VARIANT`
- `KNOWN_GAIN_VARIANT`
- `LOW_INFORMATION_QUIET`
- `LOW_INFORMATION_SILENCE`
- `MIXED_SOURCE`
- `UNKNOWN`

Akzeptiert wird ausschliesslich der exakte eingebaute Stringtyp mit einem
dieser sieben Werte. Allgemeiner ID-Validator, Quellen-ID-Regeln, beide
Vergleichsregeln, Direktbaseline und Bewertungslogik bleiben unveraendert.
Die bestehenden neutralen Testfixtures verwenden jetzt `KNOWN_EXACT` statt
der bisherigen ungebundenen Literale `neutral` und `known`; Testkoerper und
fachliche Assertions bleiben ansonsten unveraendert. Der historische
`16/16`-Beleg wird nicht geaendert und wurde nicht erneut ausgefuehrt.

## Fuenf Pruefgruppen

1. Alle 48 Kategorien-/Erwartungsuebergaben des bytegebundenen Evaluationsplans
   mit ausschliesslich synthetischen Entscheidungen; sieben Kategorien,
   korrekte Nenner, identische Eingaben vor und nach der Auswertung.
2. Jede Kategorie mit allen fuenf gueltigen Entscheidungsstatus. Eine
   Enthaltung bei erwarteter Zulassung bleibt auswertbar und ergibt
   `FALSIFIED`, nicht einen technischen Kategorienfehler.
3. Ungebundene Kategorien, Schreibvarianten, Leerzeichen, falsche Typen und
   String-Unterklassen stoppen mit `EXPECTATION_INVALID`.
4. Allgemeine ID-Grenze und Quellvalidierung bleiben unveraendert: Kategorien
   sind keine gueltigen Quellen-IDs; Listen und doppelte Quellen bleiben
   ungueltig.
5. Verlorener bekannter Treffer und neue Fehlzulassung bleiben getrennte
   negative Befunde. Ergebnisdigests stimmen; manipulierte Eingangsbelege
   werden abgewiesen.

Die synthetischen CaseResults dienen nur der Auswerterschnittstelle, nicht
als Behauptung vollstaendiger Scanbelege. Der technische Scanverifikator ist
unveraendert und wird durch diese Qualifikation nicht neu qualifiziert.
Aufrufe von Vergleich, Materialisatbindung und Panelbindung waren in den
fokussierten Tests explizit gesperrt. Kein versiegelter Rezeptorwert wurde
geladen oder ausgewertet; der Materialisierungsbeleg wurde nur gehasht.

## Arithmetik und historische Bindung

Der Vergleichsvertrag nennt jetzt ausdruecklich die bereits vor dem
historischen `16/16`-Aufruf gebundene `statistics.mean`-Arithmetik ueber
24 Binary64-Differenzen. Sie ist nicht die historische Rechenfolge
`sum(...)/24`; am inklusiven Grenzwert sind unterschiedliche Entscheidungen
moeglich. Keine Aenderung der Produktarithmetik, keine dritte Regel,
keine weitere Schwelle und kein Anspruch bitidentischer Produktionsreproduktion.

Die historische Versiegelung bindet weiterhin die urspruengliche
Vertragsdatei, verfuegbar unter Commit `1065db1`:

```text
historisch: 1fabeb6a35e8ab6ace4f2f1c8763cfa9c932446ad39c4a3e8f040b5da3cdc6fe
Nachtrag:   c3f6952c640c50da7b8e92a1773936a5277f55d2c746d97d5ebf747eaf733084
```

Der autorisierte Nachtrag wird separat versioniert. `seal.json`,
`execution-plan.json`, `evaluation-plan.json`, Quelleninventar,
Erzeugungsskript und Materialisierungsbeleg sind unveraendert. Keine
Neuversiegelung und keine nachtraegliche Anpassung historischer Hashes.
Ein Abgleich des alten Dokumenthashs mit der aktuellen Vertragsdatei waere
folglich unzulaessig; fuer die historische Bindung gilt die archivierte
Version, fuer die numerische Klarstellung dieser separat gebundene Nachtrag.
Quellen, Erwartungen und Erfolgskriterien bleiben unveraendert.

## Grenze und Rueckmeldung

Keine Korpusauswertung, Rezeptor-, Memory-, Kontext-, Feld- oder Runtimeaufrufe.
Die spaeteren Budgets bleiben `48` Faelle je Regel, `1.056` Beziehungszeilen,
`25.344` Banddifferenzen und maximal `4.194.304` Ausgabebytes. Sie wurden
nicht auf dem Korpus ausgefuehrt. Bessere Selektivitaet ist nicht nachgewiesen.

RUECKMELDUNG ERFORDERLICH: Die einmalige Korpusauswertung bleibt separat
freizugeben. Der Analyst erhaelt ausschliesslich diesen Qualifikationsbefund.

WEITER: Am besten geht es jetzt mit der Analystenpruefung dieser engen
Kategorienkorrektur und des numerischen Nachtrags weiter. Erst danach kann
die einmalige Zwei-Regel-Auswertung zur Freigabe vorgeschlagen werden.
