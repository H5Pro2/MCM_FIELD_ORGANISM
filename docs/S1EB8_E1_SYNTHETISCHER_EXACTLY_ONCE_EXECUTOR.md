# S1-EB8: Synthetischer E1-Exactly-once-Executor

## Status

Der private Exactly-once-Executor fuer die S1-EB4-Berichtsoberflaeche ist
implementiert und ausschliesslich in automatisch geloeschten temporaeren
Testverzeichnissen abgenommen. Er akzeptiert nur ein bereits komponiertes
S1-EB7-Ergebnis. Die registrierten Projektpfade werden explizit abgewiesen.

## Implementierung

```text
mcm_field_organism/e1_confirmation_synthetic_executor.py
tests/test_e1_confirmation_synthetic_executor.py
```

Normalisierter Implementierungsdigest:

```text
d5155dbd0a5fb638b4d3dec092303324b1572b2dbb02cc7a19c990d18f1bb955
```

## Persistenzfolge

```text
freie temporaere Zielpfade pruefen
-> Lock exklusiv anlegen
-> Attempt exklusiv anlegen und fsync
-> bereits komponiertes Ergebnis validieren
-> temporaeren Bericht schreiben und ruecklesen
-> atomar per exklusivem Dateilink publizieren
-> Attempt und Lock nach Erfolg entfernen
```

Ein gestarteter Fehlschlag entfernt den Lock, behaelt aber den
Attempt-Marker. Dadurch ist kein automatischer Wiederholungsversuch
moeglich. Ein bestehender Bericht, Attempt oder Lock blockiert jede weitere
Ausfuehrung in demselben synthetischen Verzeichnis.

## Synthetische Referenz

```text
Bericht-SHA-256
1afb225169041d1d9a4a588aa59c13b7791c310cd55200a5a8414cc7a0ff5fb9

Resultat-SHA-256
ff98c96b2ccecd0a23e1ba02ce1bf8827d672aae72953b9e04d18c9062ad510c

Entscheidung
NUMERICALLY_UNDECIDABLE
```

Diese Werte binden nur die synthetische Persistenzfixture. Sie sind keine
kanonischen Forschungsresultate.

## Kontrollierte Fehlergrenzen

- Nicht aufrufbarer Produzent scheitert vor Attempt und Lock.
- Das registrierte S1-EB-Zielverzeichnis wird vor Attempt abgewiesen.
- Ein ungueltiges gestartetes Resultat behaelt den Attempt-Marker.
- Ein gestarteter Produzentenfehler behaelt den Attempt-Marker.
- Eine zweite Ausfuehrung im selben Verzeichnis wird blockiert.
- Die drei registrierten S1-EB-Pfade bleiben frei.

## Technische Abnahme

```text
6 fokussierte S1-EB8-Tests
477 Tests im vollstaendigen E1-Verbund
OK
```

## Aussagegrenze

S1-EB8 zeigt nur, dass ein bereits vorliegendes Ergebnis atomar und
wiederholungssicher auf die registrierte Berichtsoberflaeche abgebildet
werden kann. Es liefert keinen kanonischen Zustands-, Transfer-, Memory-,
Semantik-, Organisations-, Topologie-, Selbstregulations- oder KI-Befund.

## Anschluss

S1-EB9 hat den kanonischen Produzenten statisch an Quellen, `r2/r4/r8`-
Plaene, Geometrie, neutralen Startzustand und alle neuen Kettenrollen
gebunden. Runtime und Persistenz blieben gesperrt. Siehe
[S1-EB9 kanonische Produzentenbindung](S1EB9_E1_KANONISCHE_PRODUZENTENBINDUNG_UND_PREFLIGHT.md).
