# Technische Snapshotänderungs-Falsifikation 013

## Status

Passive Baselineprüfung vor `GF_001`.

Diese Prüfung fragt, ob Änderungen zwischen aufeinanderfolgenden
Rezeptorsnapshots eine rateninvariante Eingangsform bilden können. Sie ergänzt
keinen vorherigen Snapshotpuffer und führt keinen Feldschritt aus.

## Baselines

Für eine geordnete Snapshotfolge `x(0) ... x(n)` werden zwei Maße verglichen:

### B0 - Gerichtete Änderung

```text
M_signed = Summe (x(k) - x(k-1))
```

Die Summe teleskopiert immer zu:

```text
M_signed = x(n) - x(0)
```

### B1 - Absolute Gesamtänderung

```text
M_absolute = Summe |x(k) - x(k-1)|
```

Dieses Maß bewahrt die gesamte tatsächlich beobachtete Weglänge der
Snapshotwerte, aber keine unbeobachteten Zwischenzustände.

## Kontrollgeschichten

Fünf Paare trennen unterschiedliche Fehlerquellen:

1. monotone Rampe, dicht gegen dünn,
2. Rückkehr zum Ausgangswert mit allen Umkehrpunkten,
3. zusätzliche identische Snapshots bei gleichem Horizont,
4. dichte Oszillation gegen ausgelassene Zwischenbewegung,
5. identische Wertfolge mit kurzer gegen lange Verweildauer.

## Ergebnis

| Prüfung | gerichtete Differenz | absolute Differenz | weitere Grenze |
|---|---:|---:|---|
| monotone Ratenteilung | `0` | `0` | vollständiger Pfad erhalten |
| Rückkehrpfad | `0` | `0` | gerichtete Summe ist trotz Weg `0` |
| zusätzliche Duplikate | `0` | `0` | Ereignisanzahl neutral |
| ausgelassene Oszillation | `0` | `4` | fehlende Übergänge bleiben unsichtbar |
| Verweildauer `0,2 s` gegen `1,0 s` | `0` | `0` | `0,8 s` Dauerunterschied geht verloren |

Sieben synthetische Kontrollen sichern geordnete Kausalität,
Horizontgleichheit, Reproduzierbarkeit der Maße und das Fehlen eines
ausgewählten Puffers oder einer Feldwirkung.

## Befund

Snapshotänderung löst einen Teil des Ratenproblems, aber nicht die
Eingangszeitfrage:

```text
zusätzliche identische Snapshots
-> keine zusätzliche Änderung
```

Gleichzeitig gilt:

```text
gerichtete Änderung
-> nur Endpunktdifferenz, keine Geschichte

absolute Änderung
-> nur beobachteter Weg, keine ausgelassene Bewegung

beide Änderungsmaße
-> keine Kontaktdauer
```

Für eine Online-Berechnung wäre außerdem mindestens der unmittelbar vorherige
Snapshot derselben Rezeptorgeometrie nötig. Ein solcher lokaler Puffer ist
beim visuellen Rezeptor derzeit nicht vorhanden. Ihn einzuführen wäre eine
neue Rezeptormechanik und folgt nicht allein aus diesem Baselinebefund.

## Konsequenz für GF_001

`GF_001` bleibt geschlossen.

Änderungsinformation darf nicht als alleiniger Feldinput freigegeben werden.
Sie verliert entweder den zurückgelegten Weg oder Dauer und unbeobachtete
Zwischenbewegung. Sie rechtfertigt auch keinen versteckten letzten
Snapshotpuffer.

Vor einem neuen Kandidaten muss geklärt werden, welche minimale Funktion an
der Rezeptorgrenze tatsächlich fehlt: Erkennung lokaler Veränderung,
Fortbestehen aktuellen Kontakts oder zeitliche Kontaktmenge. Diese Funktionen
dürfen nicht unter einem einzigen Begriff „Änderung“ vermischt werden.

Feldkopplung, Topologie, Memory, Semantik, Reflexion und Selbstregulation
bleiben geschlossen.
