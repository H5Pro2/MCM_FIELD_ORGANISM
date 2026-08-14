# S1-EB31: Terminaler Einmallauf-Abbruch

## Status

```text
STOPP
CANONICAL_ONE_SHOT_FAILED_NO_RETRY
```

Der autorisierte kanonische S1-EB-Einmallauf wurde am 12. August 2026 genau
einmal unter dem gebundenen Windows-Job-Object gestartet. Der Prozess
erstellte Lock und Attempt und brach danach vor dem ersten Feldschritt ab.
Es wird kein Wiederholungsversuch gestartet.

## Implementierung

```text
mcm_field_organism/e1_confirmation_final_canonical_worker.py
```

Normalisierter Implementierungsdigest:

```text
0f0a64f8586f337ab0af7d877694895956fdb56cf553a2858efdc102018e24e7
```

## Ausfuehrungszustand

```text
guard_status          = NONZERO_EXIT
return_code           = 1
elapsed_seconds       = 3.9475583999883384
peak_job_memory_bytes = 464633856
field_steps_started   = false
report_created        = false
attempt_retained      = true
lock_released         = true
retry_permitted       = false
```

Attemptpfad und Digest:

```text
reports/e1_refined_confirmation_s1eb_once_v1.attempt.json
695f8170011d3c7afe1a0c8816021fb4814ac409c71fef36253f2ce9ce091782
```

Der Attempt bindet den finalen Auditdigest
`1bd5bdb972a12e3ac114715451381481a4a8d03a477b585d60d82eb33a3974f8`
und den Preflightdigest
`a74b9ff4e42894882cb71d1b219e330a757541aa2633e655cca5852ccfb7a552`.

## Ursache

Nach der vertragsgemaessen Reihenfolge Preflight, Lock und Attempt rief
`produce_e1_confirmation_canonical_formation(...)` intern erneut
`build_e1_refined_confirmation_contract(...)` auf. Dieser alte Konstruktor
verlangt gleichzeitig freie Report-, Attempt- und Lockpfade. Der
Pflicht-Attempt war zu diesem Zeitpunkt bereits vorhanden. Der Abbruch lautet:

```text
E1RefinedConfirmationContractError:
S1-EB one-shot paths are not distinct and free
```

Damit besteht ein Laufzeitwiderspruch zwischen Exactly-once-Reihenfolge und
interner Bildungsvorbedingung. Die statischen und synthetischen Abnahmen
hatten diesen Widerspruch nicht erfasst.

## Evidenzgrenze

Es entstanden keine Formations-, Probe-, Resultat- oder Berichtsdaten. Daher
gibt es keine technische S1-EB-Entscheidung und keinen neuen Memory-,
Feldzeit-, Bedeutungs-, Organisations-, Topologie- oder KI-Befund.

S1-EA6 blieb unter
`adf8b2b6c1b9fdda48062dbb1cd9149fcde462a3dc77a348aa2dfb0cb1fcaa47`
unveraendert.

## Bester naechster Schritt

Nicht weiter ausfuehren. Zuerst muss der Projekteigner ausdruecklich
entscheiden, ob No-Retry terminal bestehen bleibt oder ob nach separater
Ursachenpruefung ein neuer Lauf mit neuer Ausfuehrungsidentitaet autorisiert
werden darf. Der Attempt darf bis dahin weder entfernt noch umgedeutet werden.
