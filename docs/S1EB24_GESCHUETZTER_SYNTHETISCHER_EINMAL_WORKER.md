# S1-EB24: Geschuetzter synthetischer Einmal-Worker

## Status

S1-EB24 implementiert die Ablaufkoordinationsgrenze fuer einen spaeteren
kanonischen Einmallauf. Ein eigener Unterprozess wird durch den in S1-EB22
gebundenen Windows-Job-Object-Waechter gestartet. Im Child-Prozess wird der
S1-EB23-Preflight neu erzeugt, geprueft und unmittelbar vor genau einem
synthetischen Exactly-once-Marker konsumiert.

Der kanonische S1-EB-Lauf wurde nicht gestartet. Weder Bildung noch Probe,
Ergebniskomposition oder Berichtspersistenz wurden aufgerufen.

## Implementierung

```text
mcm_field_organism/e1_confirmation_one_shot_worker.py
tests/test_e1_confirmation_one_shot_worker.py
```

Normalisierter Implementierungsdigest:

```text
eae200d33ac95ded3f0190e45f01b5dbf4acc2466498cfa043b3f8bf08d8862b
```

## Ablaufkoordinationsfolge

```text
Parent
  -> unveraenderten S1-EB22-Ressourcenwaechter pruefen
  -> Child unter Windows Job Object starten

Child
  -> S1-EB9/S1-EB4/S1-EB19/S1-EB21/S1-EB22 erneut binden
  -> S1-EB23 im selben Prozess erzeugen
  -> S1-EB23 unverzueglich pruefen
  -> Alter und Prozessidentitaet pruefen
  -> genau einen synthetischen Marker ausserhalb reports/ anlegen
  -> claimfreies synthetisches Receipt ausgeben

Parent
  -> Prozessabschluss und Ressourcengate pruefen
  -> Markerpfad, Markerhash, Child-PID und Preflight-Digest pruefen
```

Der synthetische Marker bleibt absichtlich bestehen. Ein zweiter Start im
gleichen synthetischen Verzeichnis wird abgelehnt. Damit wird die
No-Retry-/Exactly-once-Grenze ohne Nutzung der registrierten Projektziele
abgenommen.

## Gebundene Ressourcen

```text
resource_guard_digest = 03718c6111e130caebbbc9feadfa0dbe728d8c9234ad87f4133befc6b5b6cffe
max_wall_seconds       = 1800
max_peak_rss_bytes     = 4294967296
process_tree_kill      = true
```

## Geschlossene Grenze

```text
synthetic_only                  = true
work_invocation_count           = 1
canonical_targets_touched       = false
canonical_execution_permitted   = false
claims_permitted                = false
```

S1-EB24 oeffnet den gesperrten S1-EB16-Einstieg nicht und enthaelt keinen
kanonischen Runtime-, Probe-, Kompositions- oder Publikationsaufruf.

## Technische Abnahme

```text
7 fokussierte S1-EB24-Tests
573 Tests im vollstaendigen E1-Verbund
OK
```

Geprueft wurden Same-session-Reihenfolge, Job-Object-Ausfuehrung,
Child-Prozessidentitaet, Marker-/Receipt-Bindung, Exactly-once-Sperre,
Fail-closed bei veraendertem Ressourcenreceipt, Ablehnung von `reports/`,
private API und freie kanonische Zielpfade.

Der S1-EA6-Bericht blieb unter
`adf8b2b6c1b9fdda48062dbb1cd9149fcde462a3dc77a348aa2dfb0cb1fcaa47`
unveraendert. Alle drei S1-EB-Zielpfade bleiben frei.

## Aussagegrenze

S1-EB24 belegt nur die technische Ablaufkoordination eines geschuetzten,
prozesslokal vorgeprueften Einmalschritts. Es ist kein Memory-, Feldzeit-,
Bedeutungs-, Organisations-, Topologie- oder KI-Nachweis.

## Bester naechster Schritt

S1-EB25 auditiert statisch die nun freigabefaehige Gesamtkette von
S1-EB19 bis S1-EB24 gegen den unveraenderten S1-EB16-Executor. Dabei wird ein
minimaler kanonischer Workervertrag formuliert, der Bildung, Probe,
Komposition und atomare Persistenz genau einmal verbindet. Noch kein
kanonischer Laufstart; jede Abweichung fuehrt vor dem ersten Marker zum
Fail-closed.
