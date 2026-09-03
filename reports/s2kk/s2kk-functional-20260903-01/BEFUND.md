# S2-KK Einmallaufbefund

## Status

`NOT_EVALUABLE`

Lauf-ID: `s2kk-functional-20260903-01`

Der einmalige prospektive S2-KK-Lauf wurde nicht wiederholt und nicht
nachtraeglich korrigiert. Er endete waehrend der Fixture-Materialisierung vor
dem ersten Memoryaufruf. Deshalb liegt weder eine Funktionsbestaetigung noch
eine Funktionsfalsifikation vor.

## Abbruch

```text
ERROR_TYPE=ValueError
ERROR_MESSAGE=distractor anchor separation differs
```

Die 19 vorgesehenen AV-Bloecke wurden rezeptorisch materialisiert. Das
vorangestellte Sicherheitsgate verlangte danach fuer jede
Distraktor-/Ankerbeziehung die gebundene Trennung. Mindestens eine Beziehung
erfuellte diese Ausfuehrungsbedingung nicht. Der Lauf stoppte daraufhin vor:

- Initialisierung oder Fortschreibung der Memorygeschichte;
- den 17 Formationen;
- der Vollprobe `H_FULL`;
- der maskierten Probe `H_MASKED`;
- Kontextverbrauch, Baselines und Zielauswertung.

`H_FULL` und `H_MASKED` gelangten nicht in einen Trainingspfad. Zielwerte
gelangten weder zu Memory noch Verbraucher oder Baselines.

## Read-only Belegpruefung

Genau eine nachgelagerte reine Dateipruefung wurde ausgefuehrt. Sie rief
weder Rezeptor-, Memory-, Kontext- noch Auswerterfunktionen auf.

```text
READ_ONLY_VERIFICATION=RECORDING_COMPLETE_NOT_EVALUABLE
schema=True
run_id=True
digest=True
terminal_status=True
no_retry=True
raw_payloads_retained=True
source_hashes_stable=True
not_evaluable_has_error=True
not_evaluable_has_no_functional_status=True
```

Ergebnisdigest:
`51baf93ccee6c1d9b94e4aab7c2c9bc497ce44d5610ed20687d25435c1e52ced`

## Aussagegrenze

Dieser Befund betrifft das prospektive Fixture-Startgate, nicht die bereits
qualifizierten S2-KK-Komponenten und nicht die Memory- oder Kontextfunktion.
Der Status
`S2KK_LEARNED_VISUAL_CONTEXT_UTILITY_CONFIRMED_DIRECT_ADAPTIVE_FILL_EXPLAINS`
wurde nicht gesetzt. Eine erneute Ausfuehrung unter dieser Lauf-ID ist
ausgeschlossen.
