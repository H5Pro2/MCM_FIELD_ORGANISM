# S1-EB2: Kanonischer E1-r2/r4/r8-Preflight

## Status

Der nichtausfuehrende kanonische Preflight fuer den getrennten
S1-EB-Bestaetigungskorridor ist implementiert und abgenommen. Er plant die
gebundenen AB-, BA- und Probesequenzen mit `r2/r4/r8`, ohne ein Feld oder
einen E1-Zustand zu erzeugen und ohne einen Einmallaufpfad zu belegen.

## Implementierung

```text
mcm_field_organism/e1_canonical_confirmation_preflight.py
tests/test_e1_canonical_confirmation_preflight.py
```

Normalisierter Implementierungsdigest:

```text
ac7d0521c79eb0c2154cca4d62c2c88783cd57624d922e7835e1d76c9d2082eb
```

## Gebundene Plaene

```text
AB    1137a456cfceef385112deb26de662294dea2a4b95a2df0d9dc73ff8620a24e5
BA    071b4504dc11eadadeb5d5895775dd6bc076d00d937a3d62372fb958b929fc8d
Probe f78b5866d2629cb781f47ad8d622bf4260a67dacc43cfb52366a33d5790ca6b4
```

AB und BA enthalten jeweils 220 Quellsupports und 200 gemeinsame
Abschlusszeiten. Die Probe enthaelt 110 Quellsupports und 100
Abschlusszeiten. Daraus entstehen exakt:

```text
Geschichte: r2 = 400, r4 = 800, r8 = 1600 Schritte
Probe:       r2 = 200, r4 = 400, r8 = 800 Schritte
```

## Kontrollierte Gleichheit

AB und BA besitzen dieselben Supportinventare, Abschlusszeiten und
Kontaktintegrale. Nur ihre geordnete Kontaktfolge ist verschieden. Die
Handoff-Digests bleiben innerhalb jeder Quelle ueber `r2/r4/r8` invariant.

```text
Geschichte signiert    = 14.328373475671894
Geschichte absolut     = 14.328373475671894
Geschichte quadratisch = 3.293282702508704

Probe signiert         = 6.941865469153374
Probe absolut          = 6.941865469153374
Probe quadratisch      = 1.512406472248469
```

## Unveraenderte Grenzen

- Der abgeschlossene S1-EA6-Einmallauf wurde nicht wiederholt.
- Die S1-EB-Ausfuehrung ist weiterhin nicht freigegeben und nicht gestartet.
- Bericht, Attempt-Datei und Lock des S1-EB-Einmallaufs bleiben unangelegt.
- S1-EB2 erlaubt nur die Implementierung eines getrennten synthetischen
  Bildungsrunners.
- Es folgt kein Memory-, Semantik-, Organisations-, Topologie-,
  Selbstregulations- oder KI-Befund.

## Technische Abnahme

```text
6 fokussierte S1-EB2-Tests
430 Tests im vollstaendigen E1-Verbund
OK
```

## Anschluss

S1-EB3 hat den privaten Bildungsrunner fuer `r2/r4/r8` implementiert und
synthetisch abgenommen. Kanonische Bildung, Probe und Einmallaufpfade blieben
gesperrt. Siehe
[S1-EB3 synthetischer r2/r4/r8-Bildungsrunner](S1EB3_E1_SYNTHETISCHER_R2_R4_R8_BILDUNGSRUNNER.md).
