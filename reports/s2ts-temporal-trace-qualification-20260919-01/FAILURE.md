# S2-TS: neutrale Spurzustands-Qualifikation

Qualifikations-ID: `S2TS-TEMPORAL-TRACE-QUAL-20260919-01`  
Status: `NOT_QUALIFIED`

Der gebundene Einzelaufruf lief einmal und erreichte `2/3` Kontrollen. Kein
Retry erfolgte.

Die Produktlogik verarbeitet Hintframes paarweise. In
`test_order_and_fair_baselines` wird nach dem erfolgreichen Hint `b,c` nur der
erste Frame des Umkehrhints `c` übergeben; der Rückgabewert `None` ist dafür
vorgesehen. Der Test greift dennoch unmittelbar auf `['decision']` zu und
endet vor der beabsichtigten Reihenfolgenassertion mit:

```text
TypeError: 'NoneType' object is not subscriptable
```

Der Fehler ist eine unvollständige Testsequenz. Die Kontrolle hat die
Umkehrordnung noch nicht geprüft. Der Produktzustand, Quellen, NJ, Rezeptor,
Feld und A/B-Memory wurden nicht verändert beziehungsweise aufgerufen.

Eine weitere Qualifikation benötigt eine neue Freigabe und muss den zweiten
Hintframe `b` tatsächlich übergeben, bevor sie die Entscheidung prüft.
