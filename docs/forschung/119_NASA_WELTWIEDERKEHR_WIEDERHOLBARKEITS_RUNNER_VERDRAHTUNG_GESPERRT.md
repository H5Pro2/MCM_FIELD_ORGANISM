# NASA-Weltwiederkehr: Wiederholbarkeits-Runner strukturell verdrahtet und gesperrt

## Prüfentscheidung

Der vorregistrierte Wiederholbarkeitsplan ist strukturell verdrahtbar. Der Vertrag beschreibt drei geordnete, aber nicht ausführbare Wiederholungsslots. Es wurde keine Wiederholung ausgeführt.

## Wiederholungsslots

```text
repeat_index_set: 1, 2, 3
arms_per_repeat:  6
```

Jeder Slot verlangt:

- eine neue Runnerinstanz,
- ein frisches Feld zu Beginn,
- eine separate spätere Startvorabnahme,
- identische Quellen-, Permutations-, Feldparameter- und Armverträge.

Explizit ausgeschlossen sind eine Zustandsübernahme zwischen Wiederholungen und die Wiederverwendung eines bereits verbrauchten One-Shot-Ausführungsbelegs.

## Konstruktive Sperren

```text
automatic_repeat_loop_available: false
executable:                      false
repeatability_run_allowed:       false
media_decode_allowed:            false
receptor_feed_allowed:           false
stability_threshold_defined:     false
memory_threshold_defined:        false
organization_threshold_defined:  false
```

`execute_public_av_return_replication_repeatability_runner` verweigert jede Ausführung. Der Vertrag enthält keinen Schleifenmechanismus und kann keine drei Läufe automatisch starten.

## Aussagegrenze

Die Verdrahtung belegt ausschließlich strukturelle Darstellbarkeit. Sie enthält keine Stabilitätsmessung und keinen Memory-, Bedeutungs-, Organisations-, Kausalmechanismus- oder KI-Claim.
