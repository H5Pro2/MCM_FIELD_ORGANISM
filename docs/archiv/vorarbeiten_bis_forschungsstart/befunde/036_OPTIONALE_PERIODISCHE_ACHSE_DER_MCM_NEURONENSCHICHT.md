# Befund 036: Optionale periodische Achse der MCM-Neuronenschicht

## Ergebnis

Methodik 033 wurde rückwärtskompatibel in die vorhandene
`MCMNeuronLayer` integriert.

Die einzige neue technische Zustandsrolle lautet:

```text
PeriodicSamplingAxis
  axis_index
  origin
  size
```

Eine Schicht ohne `periodic_axes` bleibt offen. Die periodische Adressierung
wird nur durch einen expliziten Achsenvertrag aktiviert.

Der kanonische Gesamtdigest des Integrationslaufs lautet:

```text
c82fa94f5b007ff06d4129e774246bd9bbdb1feccd57ea9232204a646eef0bf2
```

## Rückwärtskompatibilität

Es galt exakt:

```text
alter Konstruktor ohne periodic_axes
= explizit periodic_axes=()
= bisherige offene Wahrnehmung
= bisheriger Schichtdigest
```

Der vollständige Digest aus Befund 035 blieb unverändert:

```text
1c717cd79cb0a571cfe4e32439c8ba2484b0672da6555765855a5ef811ebbdc5
```

Damit wurden bestehende offene auditive, visuelle und simulierte Feldpfade
nicht still zyklisch umgedeutet.

## Periodische Runtime gegen Referenz

Der positive Runtime-Kandidat verwendete:

```text
Positionen       = (0,) ... (6,)
sample_offsets   = (-1,), (+1,)
periodic_axes    = ((axis_index=0, origin=0, size=7),)
geometry_id      = simulated.field.ring7.v1
```

Die von `MCMNeuronLayer.advance` erzeugten Wahrnehmungen kollidierten exakt mit
der isolierten Referenz aus Methodik 032.

Es kamen ausschließlich hinzu:

```text
Ziel 0, offset -1, Quelle 6
Ziel 6, offset +1, Quelle 0
```

Die Wahrnehmungen der Positionen 1 bis 5 blieben gegenüber der offenen
Runtime exakt gleich.

## Technische Umsetzung

Periodische Achsen werden beim Schichtaufbau geprüft und kanonisch nach
`axis_index` geordnet.

Beim Erzeugen jeder lokalen Probe wird nur die deklarierte Achse abgebildet:

```text
wrapped = origin + ((target + offset - origin) modulo size)
```

Die Abbildung entsteht in jedem Schritt neu aus der vollständigen
abgeschlossenen Schichtlage. Sie wird nicht als Nachbarliste, Kante oder
Beziehung im Neuron gespeichert.

`build_receptor_aligned_mcm_field` reicht einen Achsenvertrag nur weiter, wenn
er ausdrücklich übergeben wurde.

## Mehrdimensionale Kontrolle

Zwei unabhängige periodische Achsen eines vollständigen 3-mal-3-Rasters wurden
in beiden technischen Reihenfolgen aufgebaut.

Nach kanonischer Ordnung waren Schichtzustand und Digest exakt gleich. Die
Reihenfolge unabhängiger Achsenverträge erzeugt damit keine technische
Vorzugsrichtung.

Diese Kontrolle gibt keine periodische visuelle Geometrie frei.

## Baseline-Ablationen

Unter `hold_state_baseline` waren offene und periodische Runtime im schnellen
Zustand exakt gleich:

```text
Aktivierung offen = Aktivierung periodisch
Nachhall offen    = Nachhall periodisch
```

Unter `receptor_projection_baseline` galt ebenfalls:

```text
Aktivierung = identischer Rezeptorkontakt
Nachhall    = 0.0
```

Nur die abgeschlossene Wahrnehmung an Position 0 und 6 enthielt die zwei
zusätzlichen technischen Proben. Es entstand keine Feldwirkung.

## Vollständiger Weltpfad

Alle 42 Zweige wurden erneut vollständig aufgebaut:

```text
Weltintervention
→ abgeschlossener Weltzustand
→ Weltrezeptor
→ allgemeiner Rezeptorrahmen
→ offenes MCM-Feldfenster aus Methodik 031
→ periodischer Runtime-Kandidat
→ isolierte periodische Referenz
```

Für alle Zweige kollidierten Runtime und Referenz exakt.

In allen 21 Ursachenpaaren galt:

```text
external gegen effector
→ Provenienz außen verschieden
→ periodische Runtime-Wahrnehmung innen gleich
```

Ursache, `delta`, Effort und Provenienz gelangten nicht in den Achsenvertrag
oder eine lokale Feldprobe.

## Symmetrie

Die Runtime trug:

```text
7 Rotationen x 2 Ringorientierungen = 14 Transformationen
```

Nach kanonischer Rückabbildung kollidierten alle Wahrnehmungen sowohl
untereinander als auch mit der isolierten Referenz.

## Negativ- und Atomkontrollen

Abgelehnt wurden:

- boolesche und nicht passende Achsenrollen,
- Achsengröße kleiner als zwei,
- Achsenindex außerhalb der Positionsdimension,
- doppelte Verträge derselben Achse,
- Positionen außerhalb des Achsenintervalls,
- unvollständige periodische Achsen,
- mehrere Offsets auf dieselbe Quelle.

Ein kontrollierter Fehler während eines periodischen Schichtschritts ließ die
vollständige vorherige Schicht unverändert.

Nach erfolgreichem Fortschreiben blieben Achsenvertrag, Geometrie, Positionen
und Offsets unverändert erhalten.

## Observer und Wiederholung

Neutral blieben:

- kein Observer,
- leerer Observer,
- sammelnder Observer,
- normale und umgekehrte Neuronenreihenfolge,
- normale und umgekehrte Offsetreihenfolge,
- unabhängige Wiederholung.

Es entstand keine Restspur eines Randkontakts.

## Getragener Befund

Die vorhandene Neuronenschicht kann eine explizite periodische Sensorachse
technisch korrekt und rückwärtskompatibel abbilden.

Dies schließt die Integrationsfrage aus Befund 035:

```text
bekannte periodische Sensoranatomie
→ optionale lokale Runtime-Adressierung
→ keine Veränderung bestehender offener Felder
```

## Stärkstes Gegenargument

Die Runtime führt nur eine gewöhnliche Modulo-Abbildung einer bereits
vorgegebenen Weltgeometrie aus.

Sie zeigt nicht:

- eine selbst entwickelte Topologie,
- kausale Wirkung der zusätzlichen Proben,
- Beziehung, Reorganisation oder Memory,
- Eigenwirkung oder Handlung,
- Feldintelligenz.

## Evidenz

```text
optionale periodische Runtime-Adressierung: E1
Rückwärtskompatibilität offener Felder:     E1
technische Ringtreue der Neuronenschicht:   E1
Ursachenneutralität der Achsenrolle:        E1
Aktivierung im simulierten Weltpfad:        E0
kausale Wirkung periodischer Proben:        E0
entwickelte Beziehung oder Topologie:       E0
Eigenwirkung und Handlung:                  E0
Feldintelligenz:                            E0
```

## Stopplinie

Nicht freigegeben sind:

- stillschweigende Periodizität,
- Aktivierung für Audio oder Video,
- Feldkopplung oder Ausbreitung,
- gespeicherte Nachbarn, Kanten oder Beziehungen,
- eine neue schnelle Zustandsvariable,
- Verbindung einer Probe mit `delta`,
- Effektorwahl, Reward, Ziel oder Handlung.

## Bester nächster Schritt

Methodik 034 registriert die ausdrückliche Aktivierung der bereits geprüften
periodischen Achse ausschließlich im simulierten Welt-MCM-Pfad.

Dabei müssen offene und periodische Varianten aus denselben Welt- und
Rezeptorfolgen entstehen. Unter `receptor_projection_baseline` müssen
Aktivierung, Nachhall, Träger und Zeit exakt kollidieren; nur die
`geometry_id` und die lokalen Wahrnehmungen der beiden Randneuronen dürfen sich
unterscheiden. Vollständige Digests bleiben wegen der offen ausgewiesenen
Geometrieidentität erwartungsgemäß verschieden.
