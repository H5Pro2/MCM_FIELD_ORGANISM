# Identische spätere Weltprobe: Nullbefund

## Frage

Reagiert die unveränderte Runtime nach zwei verschiedenen Weltgeschichten bei
vollständig angeglichener bekannter Gegenwart gleich?

Der Lauf folgt der
[Vorregistrierung 097](../architektur/097_VORREGISTRIERUNG_IDENTISCHE_SPAETERE_WELTPROBE.md).

## Vorgeschichten

```text
H0: 2 -> 3 -> 4 -> 5 -> 6 -> 7
H1: 2 -> 3 -> 4 -> 3 -> 2 -> 1
```

Danach erhalten beide Zweige ohne Reset:

```text
Probe A: sichtbare Position 8
Probe B: sichtbare Position 8
```

Die Position und die Zahl der Proberahmen standen vor dem Lauf fest.

## Probe A

Nach dem ersten identischen Rahmen sind gleich:

- aktueller Rezeptorkontakt;
- `activation`;
- `afterimage`.

In beiden Zweigen gilt:

```text
Summe activation = 1,0
Summe afterimage = 0,0
```

Der vollständige Snapshot ist noch verschieden. Die Ursache ist vollständig
bekannt: Die lokale MCM-Perzeption von Probe A liest den unmittelbar
vorherigen Feldtakt. Dieser vorherige Takt enthält in H0 Kontakt an Position
`7` und in H1 Kontakt an Position `1`.

Damit trägt Probe A eine reguläre Ein-Schritt-Feldprobe, aber keinen
unerklärten Entwicklungsrest.

## Probe B

Nach dem zweiten identischen Rahmen sind gleich:

- Rezeptorzustand;
- vollständige Rezeptorverteilung;
- `activation`;
- `afterimage`;
- alle lokalen Feldproben;
- vollständige MCM-Neuronenschicht;
- vollständiger `SharedMCMFieldSnapshot`.

Gemeinsamer Layerdigest:

```text
1f6fe51eb66bbb2c5da8dd286ca433466921f111d263c8973c43c07273b5cc8c
```

Gemeinsamer Snapshotdigest:

```text
7f14f2e65ec8818f1bb91e58d811257986a708eb957221fa8a7c092334bf1866
```

Kanonischer Ergebnisdigest:

```text
0158469472914f6c15ad5800b5166b7445047c214e927be0ed2fe7d44311d1b2
```

## Kontrollen

- Keine Runtime-Rolle enthält Zweig-, Ereignis- oder Phasenkennung.
- Es wurde kein Zustand zurückgesetzt.
- `receptor_projection_baseline` blieb unverändert.
- Es wurde kein Rauschen erzeugt.
- Es wurde keine Varianzregel ergänzt.
- Es wurde keine Glättung verwendet.
- Es wurde keine Nullpunkt- oder Ruhepunktdynamik ergänzt.
- Zweigreihenfolge, Wiederholung und passiver Observer verändern das Ergebnis
  nicht.

## Befund

```text
verschiedene Weltgeschichte
-> Probe A gleicht direkte aktuelle Ausgänge an
-> bekannte lokale Ein-Schritt-Probe bleibt noch sichtbar
-> Probe B gleicht den vollständigen bekannten Runtimezustand an
-> kein Rest
```

Die bestehende Runtime reagiert bei vollständig gleicher bekannter Gegenwart
reproduzierbar gleich.

## Nicht gezeigt

Der Lauf zeigt nicht:

- organisches Memory;
- eine gespeicherte Weltkonsequenz;
- semantische Resonanz;
- eine innere Bezeichnung;
- entwickelte Topologie;
- Feldrückwirkung;
- Lernen oder Anpassung;
- Feldintelligenz.

Insbesondere ist die Ein-Schritt-Probe nach Probe A kein Memory-Hinweis. Sie
ist eine bereits bekannte, explizite Rolle der gegenwärtigen lokalen
Feldperzeption.

## Entscheidung

Die Nullkontrolle bestätigt die bekannte Runtimegrenze. Nach vollständiger
Angleichung bleibt kein geschichtsabhängiger Feldunterschied bestehen.

Aus diesem Ergebnis wird keine neue Speichermechanik abgeleitet.

## Wie es am besten weitergeht

Als nächster Schritt muss konzeptionell entschieden werden, ob eine
weltbezogene MCM-Speicherhypothese unabhängig von diesem Nullbefund begründet
werden kann. Sie benötigt eine eigene notwendige Funktion und eine
unabhängige Zustandsrolle. Eine bloße Verlängerung der Probe oder ein weiterer
Leaky-Zustand wäre keine organische Lösung.
