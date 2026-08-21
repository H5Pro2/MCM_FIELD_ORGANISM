# S1-TB: Gestoppter realer Baseline-Referenzatlas-Einmallauf und Nullabilitaetsbefund

## Einmalige Ausfuehrung

S1-TB wurde genau einmal mit dem in S1-TA gebundenen Befehl gestartet:

```text
python -B -m mcm_field_organism.four_node_baseline_reference_single_run --authorization S1-TB_REAL_BASELINE_REFERENCE_ATLAS_ONCE
```

Der Prozess endete kontrolliert:

```text
error_code=ATLAS_ONE_SHOT_NOT_COMPUTABLE
attempt_path=reports/s1tb_baseline_reference_atlas_once_v1.attempt.json
exit_code=1
```

Es gab keinen Retry. Kein Modellproducer und kein Feldschritt wurden
aufgerufen.

## Persistente Start- und Sperrbelege

Wie vorregistriert bleiben nach einem gestarteten Fehler Versuchsnachweis
und Sperre unveraendert bestehen:

```text
reports/s1tb_baseline_reference_atlas_once_v1.attempt.json
  file_sha256 = e746f02cb0cfaa219a59ae2a1d7a8768925a52710ba0316aacd8bddd7eb795e5
  attempt_digest = 6d2d3d4da44c169bf5b2d72bc03d13744d00ec21c30aa75fcfba9f4e7add399c

reports/s1tb_baseline_reference_atlas_once_v1.lock
  file_sha256 = 42a66cbd8e32bfba04655617cb56f53220029f155a7b320c57239261b409600e
  lock_digest = 47317cae6b74b087299441787eaf19ee22b0d0434e903d1dfc322a9634af54b7
```

Diese Dateien werden nicht geloescht, repariert oder fuer einen zweiten
S1-TB-Start wiederverwendet. Ergebnis und Staging fehlen:

```text
reports/s1tb_baseline_reference_atlas_once_v1.json = absent
reports/.s1tb_baseline_reference_atlas_once_v1.json.staging = absent
```

## Passiv isolierter Stopgrund

Nach dem gestoppten Lauf wurde der Comparator nicht erneut aufgerufen. Die
bereits gebundene Eingabe wurde nur stufenweise gegen die
Validatorbedingungen geprueft.

Die vollstaendige oeffentliche Provenienz und alle
`ALIGNED_PRE_PROBE`-Kontrollen waren ohne Abweichung. Der erste technische
Ausnahmeort lag in der Typpruefung des Rezeptorkontaktvektors:

```text
TypeError: must be real number, not NoneType
```

Exakt 14 Checkpointrecords sind betroffen, jeweils derselbe
Plan-/Checkpointort in jeder Modellrolle:

```text
plan_role       = C_GAP
checkpoint_role = POST_COMPETITION
channel         = signed_receptor_contact_vector R
value           = (None, None, None, None)
affected_models = 14 von 14
```

In keinem signed Aktivierungsvektor `S` und keinem signed
Nachbildvektor `H` wurde `None` gefunden. Die 320 numerisch zu
vergleichenden S/H-Profilkomponenten sind daher nicht Ursache des Stops.

## Technische Einordnung

`None` bezeichnet an dieser Stelle einen nicht vorhandenen aktuellen
Rezeptorkontakt nach der Gap-Exposition. Es ist ein Provenienzmarker und
keine numerische Feldkomponente. Der aktuelle Comparatorvalidator hat
Rezeptorprovenienz, S und H faelschlich derselben
`math.isfinite`-Typregel unterworfen.

Eine stille Ersetzung von `None` durch `0.0` ist unzulaessig, weil dadurch
`kein Kontaktrecord` und `expliziter Nullkontakt` gleichgesetzt wuerden.
Die korrekte technische Richtung ist:

- `R` bleibt explizit nullable und wird nur auf zulässige
  Provenienzformen sowie modelluebergreifende Gleichheit geprueft;
- `S` und `H` bleiben strikt vier endliche Zahlen und alleinige numerische
  Profilkomponenten;
- die kanonische Serialisierung behaelt `null` fuer die betroffenen
  R-Komponenten;
- ein spaeterer Neulauf erhaelt neue Identitaet, Pfade und Autorisierung;
  die S1-TB-Belege bleiben dauerhaft erhalten.

Dies ist kein negativer Baseline- oder Feldbefund, sondern eine
falsifizierte technische Typannahme an der passiven Provenienzgrenze.

## Entscheidung und naechster Schritt

```text
S1_TB_STARTED_ONCE_AND_STOPPED_FAIL_CLOSED
NO_RESULT_ARTIFACT_ATTEMPT_AND_LOCK_PRESERVED
NULLABLE_RECEPTOR_PROVENANCE_TYPE_ASSUMPTION_FALSIFIED
S_H_NUMERICAL_PROFILE_NOT_EVALUATED_TO_COMPLETION
```

Der einzige naechste Schritt ist S1-TC als statischer
Nullabilitaets-, Serialisierungs-, Test- und getrenntes
Neulaufidentitaetsvertrag. S1-TC darf noch keinen Code aendern, keinen Test
ausfuehren, keinen Comparator aufrufen und keinen S1-TB-Beleg entfernen.
