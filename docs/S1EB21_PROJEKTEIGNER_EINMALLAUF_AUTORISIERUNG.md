# S1-EB21: Projekteigner-Einmalllauf-Autorisierung

## Status

Der Projekteigner hat auf die ausdrueckliche Frage nach der Autorisierung
genau eines S1-EB-Einmallaufs mit `ok weiter` zugestimmt. Diese Zustimmung
wird als `AUTHORIZED_ONE_SHOT` fuer den unmittelbar zuvor bezeichneten Lauf
und ausschliesslich unter den S1-EB19-Grenzen gebunden.

Die Autorisierung startet den Lauf nicht und oeffnet weder Ausfuehrung noch
Persistenz.

## Implementierung

```text
mcm_field_organism/e1_confirmation_owner_authorization.py
tests/test_e1_confirmation_owner_authorization.py
```

Normalisierter Implementierungsdigest:

```text
1b37c7362844e04693598ed2d0e5f1ca75bdcc6ce3a4c48e61516bb41cda873a
```

Autorisierungs-Payloaddigest:

```text
e9e6eba15ad45534f141e59c17fca52fb29e45c0a9fc4bf77fb66591420be312
```

## Gebundene Entscheidungen

```text
independent_reviewer_decision = FREIGABE
project_owner_authorization   = AUTHORIZED_ONE_SHOT
authorized_run_count          = 1
```

Die unabhaengige Prueferentscheidung bleibt separat unter dem SHA-256
`0cfa8504d39787b1c5d5395dd6bf65947af28b3cca7d851e67c4a9f1819e993a`
gebunden.

## Unveraenderter Laufrahmen

```text
Feldschritte: 23800
Wandzeit:     maximal 1800 Sekunden
Peak RSS:     maximal 4294967296 Byte
Retry:        keiner nach gestartetem Fehler
S1-EA6:       keine Wiederholung
Posthoc:      keine Parametrierung oder weichere Schwelle
Claims:       kein Memory- oder KI-Claim aus der Autorisierung
```

## Noch geschlossene Gates

```text
resource_enforcement_bound      = false
same_session_preflight_complete = false
execution_permitted             = false
persistence_permitted           = false
```

## Technische Abnahme

```text
7 fokussierte S1-EB21-Tests
553 Tests im vollstaendigen E1-Verbund
OK
```

Geprueft wurden getrennte Pruefer- und Projekteignerentscheidung,
Einmallaufanzahl, Ressourcen- und Fehlerrahmen, geschlossene Restgates,
Manipulationsabwehr, Wiederholbarkeit, fehlende Runtime- und Writerpfade,
private API und freie S1-EB-Zielpfade.

Der S1-EA6-Bericht blieb unter
`adf8b2b6c1b9fdda48062dbb1cd9149fcde462a3dc77a348aa2dfb0cb1fcaa47`
unveraendert. Alle drei S1-EB-Zielpfade bleiben frei.

## Bester naechster Schritt

S1-EB22 bindet und testet die technische Durchsetzung der 30-Minuten- und
4-GiB-Abbruchgrenzen ausschliesslich mit kurzlebigen synthetischen
Unterprozessen. Der kanonische Lauf bleibt bis danach und bis zum
Same-session-Preflight gesperrt.
