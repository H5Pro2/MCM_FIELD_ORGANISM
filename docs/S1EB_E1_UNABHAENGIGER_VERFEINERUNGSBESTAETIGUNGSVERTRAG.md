# S1-EB: E1 unabhaengiger Verfeinerungsbestaetigungsvertrag

## Status

Ein neuer numerischer Bestaetigungskorridor ist vor jeder Planner-, Runner-
oder Feldausfuehrung statisch registriert. Er ist ein neues Exactly-once-
Artefakt und keine Wiederholung oder Nachparametrierung von S1-EA6.

```text
PREREGISTERED_NOT_IMPLEMENTED
```

## Implementierung

```text
mcm_field_organism/e1_refined_confirmation_contract.py
tests/test_e1_refined_confirmation_contract.py
```

Normalisierter Implementierungsdigest:

```text
d6e7501b7791c489398a12171eb9ae530f210427935a039bea8f12d9423ed5dd
```

Vertragsdigest:

```text
bccf552b7ea69cc083cf65ac0a7d3faacfe7939ff8c7d13c4614f1cf42d06fb4
```

## Forschungsfrage

```text
Trennt r8 beide feinen Probensignale vom vorregistrierten numerischen Rest?
```

Der Korridor verwendet dieselbe gebundene kanonische AV-Quelle, erzeugt aber
ein neues unabhaengiges Einmallaufartefakt. Mechanik, Probe, Ablationen,
Fixed-Adapter-Kontrolle und strikter Achtfachfaktor duerfen nicht veraendert
werden.

## Vorregistrierte Verfeinerung

```text
Bildung:
r2 = 400 Schritte
r4 = 800 Schritte
r8 = 1600 Schritte

Probe:
r2 = 200 Schritte
r4 = 400 Schritte
r8 = 800 Schritte
```

Der physische Bildungs- und Probenhorizont, alle Rezeptorsupports und ihre
integrierten Eingaben muessen identisch bleiben. Nur die kontaktfreien
Intervalle duerfen weiter unterteilt werden.

## Entscheidungsregel

1. Eine fehlgeschlagene Pflichtkontrolle ergibt `TECHNICALLY_INVALID`.
2. Exakt null fuer Zustand und beide Probensignale in `r2/r4/r8` ergibt
   `NO_CONFIRMED_REFINED_EFFECT`.
3. Nur wenn `r8`-Zustand und beide `r8`-Probensignale strikt groesser als das
   Achtfache ihres passenden `r4/r8`-Restes sind und der `r4/r8`-Rest nicht
   groesser als der `r2/r4`-Rest ist, ergibt sich
   `CONFIRMED_REFINED_WORLD_FORMATION_AND_TRANSFER_EFFECT`.
4. Jeder andere technisch gueltige Ausgang ergibt
   `NUMERICALLY_UNDECIDABLE`.

Eine weichere Schwelle nach Kenntnis von S1-EA6 ist ausdruecklich verboten.

## Neue Exactly-once-Pfade

```text
reports/e1_refined_confirmation_s1eb_once_v1.json
reports/e1_refined_confirmation_s1eb_once_v1.attempt.json
reports/e1_refined_confirmation_s1eb_once_v1.lock
```

Alle drei Pfade sind frei. Ausfuehrung und Runnerimplementierung bleiben
gesperrt. Nur die Plannerimplementierung ist als naechster Schritt erlaubt.

## Abnahme

```text
6 fokussierte Tests
417 Tests im vollstaendigen E1-Verbund
OK
```

Es wurde kein Plan gebaut, kein Feld entwickelt, kein Zustand veraendert und
keine Probe ausgefuehrt.

## Aussagegrenze

S1-EB ist nur eine Vorregistrierung. Sie bestaetigt weder den S1-EA6-Effekt
noch Memory, Semantik, Organisation, Topologie, Selbstregulation oder KI.

## Anschluss

S1-EB1 implementiert nun den getrennten `r2/r4/r8`-Planer und nimmt ihn
synthetisch ab. Der kanonische Quellenpreflight bleibt der naechste Schritt.
