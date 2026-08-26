# S1-NA KFS-1 Validator-Implementierungsvertrag

## Status

S1-NA bindet ausschliesslich die Implementierungsgrenze fuer den isolierten
statischen KFS-1-Schema-Validator aus S1-MY und S1-MZ. Dieser Schritt legt
Dateipfade, reine APIs, Fixturegrenzen, Fehlerverhalten und ein endliches
Testbudget fest. Er implementiert und fuehrt den Validator noch nicht aus.

Kandidatengleichung, Dynamikparameter, MCM-Feldzugriff, Runtimeintegration,
Feldlauf und Funktionsentscheidung bleiben gesperrt.

## Gebundene Dateigrenze

Die spaetere Implementierung darf genau diese neuen Dateien anlegen:

| Datei | Aufgabe |
|---|---|
| `mcm_field_organism/kfs1_schema_validator.py` | reine kanonische Serialisierung, Digestbildung, Schema-/Anatomie-/Ledger-/Kausalpruefung und Validierungsbeleg |
| `tests/kfs1_s1nb_fixtures.py` | ausschliesslich statische positive und mutierte Testbytes samt Erwartungen |
| `tests/test_kfs1_s1nb_schema_validator.py` | fokussierte Abnahme aller S1-MZ-Fixtures und Sperren |

Kein Runner, Toolskript, Report, Audio-/Video-Modul, MCM-Feldmodul oder
bestehender DTS-1-Code darf fuer S1-NA beziehungsweise S1-NB veraendert
werden. Die Fixtures duerfen nicht aus dem Produktionsmodul importiert oder
zur Laufzeit aus Felddaten erzeugt werden.

## Reine oeffentliche API

Das Produktionsmodul darf genau folgende oeffentliche Rollen bereitstellen:

```text
canonical_json_bytes(value) -> bytes
sha256_hex(raw_bytes) -> str
validate_kfs1_record(raw_bytes, registry) -> KFS1ValidationReceipt
build_kfs1_validation_registry() -> KFS1ValidationRegistry
```

Zusaetzlich sind nur unveraenderliche Datentypen fuer Registry und Beleg sowie
Konstanten fuer Schema-IDs, Versionen, Messrollen, Pruefphasen und Fehlercodes
zulaessig. Interne Hilfsfunktionen bleiben privat.

## Schemaversionen

Die Implementierung bindet exakt:

| Rolle | Wert |
|---|---|
| Anatomieschema | `kfs1_anatomy_record` |
| Messrollenschema | `kfs1_measurement_record` |
| Record-Schemaversion | `s1my.v1` |
| Validierungsbeleg | `kfs1_validation_receipt` |
| Beleg-Schemaversion | `s1mz.v1` |
| Digestverfahren | `sha256` mit kleingeschriebenen 64 Hexzeichen |

Die Versionen bezeichnen nur das statische Vertragsformat.

## Kanonische Bytefunktion

`canonical_json_bytes` muss:

- ausschliesslich JSON-Grundtypen und Listen beziehungsweise Mappings mit
  Stringschluesseln akzeptieren;
- Mapping-Schluessel lexikographisch sortieren;
- UTF-8 ohne BOM und ohne ueberfluessige Leerzeichen erzeugen;
- Nichtendlichkeit und negative Null ablehnen;
- unbekannte Python-Objekte ablehnen;
- den Eingabewert nicht veraendern.

Die Funktion ist kein Normalisierer fuer eingehende Records. Sie wird nur
zum Vergleich mit bereits eingelesenen Bytes und zur Digestbildung
vollstaendig gueltiger Teilpayloads verwendet. Nichtkanonische Eingabebytes
bleiben unberuehrt und werden abgelehnt.

## Registrygrenze

`KFS1ValidationRegistry` ist unveraenderlich und enthaelt nur:

- die zwei Record-Schema-IDs und ihre Version;
- die sechs in S1-MX gebundenen passiven Messrollen;
- exakt passive `read_scope`-Werte;
- registrierte Geometrie-, Feldreferenz-, Anatomie- und
  Expositionsidentitaeten der positiven Fixtures;
- die kanonischen S1-MY-Fehlercodes;
- die feste Reihenfolge der sieben S1-MZ-Pruefphasen.

Die Registry enthaelt keine Felddaten, Rohdaten, Labels, Zielwerte,
Sequenzpuffer, Kandidatengleichung oder Dynamikparameter. Sie wird einmal
vollstaendig aufgebaut und waehrend einer Validierung nicht veraendert.

## Validatorverhalten

`validate_kfs1_record` muss:

1. ausschliesslich ein unveraendertes `bytes`-Objekt und eine gueltige
   Registry akzeptieren;
2. zuerst den `input_bytes_digest` ueber die originalen Bytes bilden;
3. die sieben S1-MZ-Pruefphasen in gebundener Reihenfolge auswerten;
4. nur unabhaengig sicher feststellbare Fehler sammeln;
5. Fehlercodes lexikographisch sortieren und duplizierte Codes entfernen;
6. niemals den Eingaberecord reparieren, ergaenzen oder neu serialisieren;
7. genau einen unveraenderlichen `KFS1ValidationReceipt` zurueckgeben.

Ungueltige oder unlesbare Recordbytes sind normale fail-closed Eingaben und
muessen einen `invalid`-Beleg liefern. Nur ein Programmierfehler an der
oeffentlichen Grenze, etwa ein anderer Eingabetyp oder eine ungueltige
Registryinstanz, darf vor der Recordpruefung `TypeError` beziehungsweise
`ValueError` ausloesen. Dabei entsteht kein Teilbeleg.

## Digestgrenze

Ein Record-Digest wird nur berechnet, wenn der dafuer erforderliche
Teilpayload strukturell vollstaendig ist. Selbstbezuegliche Digestfelder
werden aus ihrem eigenen Digestpayload ausgeschlossen:

- `resource_account_digest` bindet `edge_id`, `capacity`, `free`, `bound` und
  `blocked`;
- `anatomy_digest` bindet den Anatomie-Record ohne `anatomy_digest`;
- `measurement_record_digest` bindet den Messrollenrecord ohne
  `measurement_record_digest`;
- `validation_receipt_digest` bindet den Beleg ohne
  `validation_receipt_digest`.

Ein ungueltiger deklarierter Digest wird nicht durch den neu berechneten Wert
ersetzt. Der berechnete Wert darf nur im getrennten Validierungsbeleg stehen.

## Fixturematerialisierung

`tests/kfs1_s1nb_fixtures.py` muss genau diese Klassen materialisieren:

- 2 positive Minimalfixtures;
- 18 Einzeldefekt-Fixtures;
- 3 Mehrfachdefekt-Fixtures;
- 1 unveraenderliche Erwartungstabelle mit Fixture-ID, Eingabebyte-Digest,
  Status, Fehlercodes und erwartetem berechenbaren Record-Digest oder
  `not_computable`.

Jedes negative Fixture muss aus einer positiven Referenz durch die in S1-MZ
gebundene einzelne beziehungsweise mehrfache Mutation nachvollziehbar
abgeleitet werden. Die finalen Testbytes und erwarteten Digests werden als
Konstanten gebunden. Zufall, Zeit, Dateisystemreihenfolge und Netzwerkzugriff
sind verboten.

## Fokussierte Testmatrix

`tests/test_kfs1_s1nb_schema_validator.py` muss mindestens pruefen:

| Test-ID | Abnahme |
|---|---|
| `T01` | beide positiven Fixtures sind gueltig und digeststabil |
| `T02` | alle 18 Einzeldefekte liefern ihren gebundenen primaeren Code |
| `T03` | drei Mehrfachdefekte liefern nur sichere, sortierte Codes |
| `T04` | gleiche Eingabebytes und Registry liefern bitidentische Belege |
| `T05` | Eingabebytes und Registry bleiben unveraendert |
| `T06` | nichtkanonische Bytes werden nicht stillschweigend normalisiert |
| `T07` | fehlende Voraussetzungen erzeugen keine erfundenen Folgedefekte |
| `T08` | Digestrollen sind getrennt und nicht selbstbeziehend |
| `T09` | Kandidat und Baseline mit anderer Expositionshistorie sind nicht vergleichbar |
| `T10` | das Produktionsmodul importiert keine Runner-, Feld-, Audio-/Video- oder DTS-1-Runtime |
| `T11` | der Validator schreibt keine Datei und erzeugt keinen Report |
| `T12` | keine Gleichung, Dynamik, Feldentwicklung oder Ergebniswertung ist erreichbar |

Die Tests verwenden die bestehende Standardbibliothek `unittest`. Es wird
keine neue Abhaengigkeit eingefuehrt.

## Endliches Ausfuehrungsbudget fuer S1-NB

Die spaetere Implementierungsabnahme darf hoechstens umfassen:

- genau einen fokussierten `unittest`-Aufruf fuer die neue Testdatei;
- hoechstens 64 Aufrufe von `validate_kfs1_record` innerhalb dieser Tests;
- genau 0 MCM-Feldschritte;
- genau 0 Runner-, Audio-, Video-, Browser- oder Netzwerkaufrufe;
- genau 0 Reportpublikationen.

Bei einem Testfehler wird kein Fixture angepasst, um den Validator nachtraeglich
zu bestaetigen. Implementierung oder Vertrag werden getrennt geprueft; eine
fachliche Vertragsaenderung erfordert einen neuen statischen Schritt.

## Abnahmekriterien

S1-NA ist erfuellt, wenn die Implementierung ohne offene Entscheidung aus den
gebundenen Dateipfaden, APIs, Versionen, Fixtureklassen, Tests und Sperren
ableitbar ist. S1-NA selbst erzeugt keinen ausfuehrbaren Validatorbefund.

## Naechster erlaubter Schritt

Der naechste Schritt ist S1-NB, ausschliesslich als Implementierung und
einmalige fokussierte Abnahme des statischen KFS-1-Schema-Validators innerhalb
des oben gebundenen Budgets. Kandidatengleichung, Dynamikparameter,
Runtimeintegration, Feldlauf, Baselineurteil und Funktionsentscheidung bleiben
gesperrt.
