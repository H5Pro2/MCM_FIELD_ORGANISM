# S1-EB26: Kanonische Workerform mit synthetischen Rechenkernen

## Status

S1-EB26 implementiert die in S1-EB25 gebundene Reihenfolge und
Exactly-once-Fehlerpolitik als private Workerform. Sechs Rechen- und
Handoffstufen werden fuer die Abnahme ausschliesslich durch synthetische
Digestkerne ersetzt.

Der kanonische Einstieg validiert seine Eingaben und stoppt danach explizit
mit `canonical worker execution remains locked`. Kein kanonischer Feldlauf
wurde gestartet.

## Implementierung

```text
mcm_field_organism/e1_confirmation_canonical_worker.py
tests/test_e1_confirmation_canonical_worker.py
```

Normalisierter Implementierungsdigest:

```text
08fba35a409368c7c174b687457f2c86df074ef33eb0dc352f1a1c0db4952d75
```

## Synthetisch ersetzte Stufen

```text
formation
probe_handoff
probe_r2_r4_r8
result_handoff
result_composition
report_handoff
```

Jede Stufe erhaelt nur den Digest der vorherigen Stufe und muss genau einen
SHA-256-Digest zurueckgeben. Damit wird die Orchestrierungsreihenfolge
geprueft, ohne kanonische Felder, Zustandsobjekte oder Resultate zu erzeugen.

## Exactly-once-Verhalten

Erfolgsweg:

```text
frischer S1-EB23-Preflight
-> exklusiver Lockmarker
-> exklusiver Attemptmarker
-> sechs synthetische Stufen in fester Reihenfolge
-> temporaerer Bericht
-> atomare same-directory Publikation
-> vollstaendige Ruecklese- und Hashpruefung
-> Attempt entfernen
-> Lock freigeben
```

Fehlerweg nach dem Attemptmarker:

```text
kein Bericht
Attempt bleibt erhalten
Lock wird freigegeben
jeder zweite Versuch wird vor einem neuen Preflight abgelehnt
```

## Geschlossene Grenze

```text
synthetic_only                 = true
canonical_execution_permitted = false
claims_permitted              = false
```

Der synthetische Pfad lehnt das registrierte `reports/`-Verzeichnis ab. Der
kanonische Einstieg enthaelt weder Marker-, Writer- noch kanonische
Rechenkernaufrufe.

## Technische Abnahme

```text
8 fokussierte S1-EB26-Tests
588 Tests im vollstaendigen E1-Verbund
OK
```

Geprueft wurden die exakte Stufenreihenfolge, Preflight vor erstem Marker,
atomare Erfolgspublikation, Attemptentfernung erst nach Verifikation,
Attemptbeibehaltung und No-Retry im Fehlerfall, Manipulationsabwehr,
Ablehnung von `reports/`, geschlossener kanonischer Einstieg, private API und
freie kanonische Zielpfade.

Der S1-EA6-Bericht blieb unter
`adf8b2b6c1b9fdda48062dbb1cd9149fcde462a3dc77a348aa2dfb0cb1fcaa47`
unveraendert. Alle drei S1-EB-Zielpfade bleiben frei.

## Aussagegrenze

S1-EB26 belegt nur Workerreihenfolge, Persistenzordnung und Fehlerpolitik.
Synthetische Digests sind keine Feldresultate. Es folgt kein Memory-,
Feldzeit-, Bedeutungs-, Organisations-, Topologie- oder KI-Nachweis.

## Bester naechster Schritt

S1-EB27 bindet die vorhandenen kanonischen Bildungs-, Handoff-, Probe-,
Kompositions- und Berichtsfunktionen statisch an die sechs Workerrollen. Die
Bindung muss Typen, Digests und `r2/r4/r8`-Reihenfolge vorab pruefen und
weiterhin vor jedem Feldlauf und Marker stoppen. Erst danach kann ein finaler
kanonischer Worker unter dem S1-EB22-Ressourcenwaechter geschlossen werden.
