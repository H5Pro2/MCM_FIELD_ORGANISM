# S1-EB22: Native Ressourcen-Abbruchgates

## Status

S1-EB22 implementiert einen privaten Windows-Unterprozesswaechter fuer die
technische Durchsetzung der vorab gebundenen Wandzeit- und Speichergrenzen.
Er verwendet keine neue Drittanbieterabhaengigkeit.

Die Abnahme erfolgte ausschliesslich mit kurzlebigen synthetischen Python-
Prozessen. Der kanonische S1-EB-Lauf wurde nicht gestartet.

## Implementierung

```text
mcm_field_organism/e1_confirmation_resource_guard.py
tests/test_e1_confirmation_resource_guard.py
```

Normalisierter Implementierungsdigest:

```text
df01fef096fb463c5297b3b99b98b9e5b4d8602343c6108f1b7833b7f94a12e4
```

Bindungs-Payloaddigest:

```text
03718c6111e130caebbbc9feadfa0dbe728d8c9234ad87f4133befc6b5b6cffe
```

## Durchsetzungsmechanik

Backend:

```text
Windows Job Object
JOB_OBJECT_LIMIT_JOB_MEMORY
JOB_OBJECT_LIMIT_KILL_ON_JOB_CLOSE
Wandzeitwaechter mit TerminateJobObject
```

Damit werden der gesamte zugeordnete Prozessbaum, ein jobweiter
Speicherdeckel und ein unabhaengiges Wandzeitlimit gebunden. Bei
Grenzverletzung wird nicht nur ein einzelner Worker, sondern das Job Object
beendet.

Die kanonischen Obergrenzen bleiben:

```text
max_wall_seconds    = 1800
max_peak_rss_bytes  = 4294967296
total_field_steps   = 23800
```

## Synthetische Abnahme

```text
Normalprozess:
status = COMPLETED
return = 0

Zeitueberschreitung:
status  = WALL_LIMIT_EXCEEDED
Abbruch nach rund 0.11 Sekunden

Speicherueberschreitung:
status = MEMORY_LIMIT_EXCEEDED
return != 0
```

Die kleinen Testgrenzen dienen nur der schnellen Funktionspruefung. Sie
veraendern die gebundenen kanonischen Obergrenzen nicht.

## Geschlossene Grenze

```text
resource_enforcement_bound = true
canonical_execution_permitted = false
same_session_preflight_complete = false
```

Der Ressourcenwaechter ruft keinen kanonischen Executor auf und kennt keine
Forschungsentscheidung oder Reportsemantik.

## Technische Abnahme

```text
7 fokussierte S1-EB22-Tests
560 Tests im vollstaendigen E1-Verbund
OK
```

Geprueft wurden Normalabschluss, Wandzeitabbruch, Speicherabbruch,
vollstaendige Dreirollenmatrix, Fail-closed bei fehlender Kontrolle, private
API und freie S1-EB-Zielpfade.

Der S1-EA6-Bericht blieb unter
`adf8b2b6c1b9fdda48062dbb1cd9149fcde462a3dc77a348aa2dfb0cb1fcaa47`
unveraendert. Alle drei S1-EB-Zielpfade bleiben frei.

## Bester naechster Schritt

S1-EB23 fuehrt den verpflichtenden Same-session-Preflight aus. Er muss alle
gebundenen Implementierungs-, Vertrags-, Autorisierungs- und
Ressourcendigests erneut pruefen, S1-EA6 bestaetigen und die drei freien
Zielpfade unmittelbar vor einem moeglichen Lauf kontrollieren. Er darf den
Lauf selbst noch nicht starten.
