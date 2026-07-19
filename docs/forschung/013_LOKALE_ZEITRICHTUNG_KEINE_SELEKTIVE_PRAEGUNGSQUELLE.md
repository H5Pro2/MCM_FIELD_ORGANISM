# Lokale Zeitrichtung: keine selektive Prägungsquelle

## Frage

Kann die zeitliche Reihenfolge realitätsnäherer Audio- und Videokontakte eine
lokale Beziehung selektiver kennzeichnen als die zuvor verworfene
Amplitudenkoaktivität?

## Aufbau

Dieselben zwei kontrollierten Weltphasen werden in umgekehrter Reihenfolge
durchlaufen:

```text
Zweig 1: A -> B
Zweig 2: B -> A
```

Beide Phasen verwenden die vorhandenen auditiven und visuellen Rezeptoren und
das unveränderte gemeinsame MCM-Feld. Nach jeder vollständig abgeschlossenen
Phase liest ein passiver Observer für jede gerichtete lokale Nachbarschaft:

```text
d(i,j) =
    Aktivität_i(t-1) * Aktivität_j(t)
  - Aktivität_j(t-1) * Aktivität_i(t)
```

Die Formel speichert nichts. Sie ist ein fester Ein-Schritt-Leser und wirkt
nicht auf das Feld zurück.

## Ergebnis

```text
gerichtete lokale Beziehungen                 290
unabhängige reziproke Paare                    145

nicht null bei A -> B                          290
nicht null bei B -> A                          290
Vorzeichen zwischen beiden Zweigen getauscht   250
Vorzeichen nicht getauscht                      40

mittlerer Betrag A -> B                   0,001868
mittlerer Betrag B -> A                   0,001944
mittlerer Rest gegen exakte Umkehr         0,000625
relativer Umkehrrest                         32,81 %
```

Die reziproken Leserwerte innerhalb desselben Feldverlaufs sind exakt
antisymmetrisch. Die beiden zeitlich umgekehrten Weltverläufe sind es jedoch
nicht. Felddiffusion, Nachhall und die unterschiedliche erste Phase verändern
den Ausgangszustand der jeweils zweiten Phase.

## Befund

Zeitliche Richtung ist im gemeinsamen Feld beobachtbar. Das ist mehr als
reine gleichzeitige Amplitudenkoaktivität.

Sie liefert unter dieser Prüfung aber keine selektive Prägungsquelle:

- Alle 290 lokalen gerichteten Beziehungen erhalten einen von null
  verschiedenen Wert.
- Der Wert ist vollständig durch zwei aufeinanderfolgende abgeschlossene
  Feldzustände und eine feste Leserform bestimmt.
- Es entsteht kein neuer lokaler Zustand.
- Es wird keine Beziehung stabilisiert, gelöst oder neu gebunden.
- Es tritt keine Wirkung auf eine spätere identische Probe auf.

Damit ist eine beobachtbare zeitliche Feldrichtung gezeigt, aber weder
organisches Memory noch eine entwickelbare Feldtopologie.

## Biologische Einordnung

Biologische zeitabhängige Plastizität stützt die allgemeine Relevanz lokaler
Reihenfolge. Sie ist jedoch keine Freigabe, eine feste STDP-Regel zu kopieren.
Die experimentellen Befunde hängen neben dem relativen Timing auch von
Synapsenstärke, Zelltyp und komplexeren Aktivitätsmustern ab. Diese Grenze
folgt bereits aus den Primärbefunden von
[Bi und Poo (1998)](https://pmc.ncbi.nlm.nih.gov/articles/PMC6793365/) sowie
[Froemke und Dan (2002)](https://www.nature.com/articles/416433a).

Für dieses Projekt folgt daraus nur:

> Zeitliche Ursache darf eine spätere Materialhypothese mitbestimmen. Ein
> gerichteter Ein-Schritt-Wert ist selbst noch kein Memory-Substrat.

## Entscheidung

Keine neue Memory-Mechanik wird freigegeben.

Nicht eingeführt werden:

- STDP-Gewichte,
- Zeitfensterschwellen,
- Gewinnerregeln,
- adaptive Kanten,
- Runtime-Rückwirkung,
- Zieltopologien.

Der feste zeitliche Observer bleibt eine passive Baseline. Der nächste
sinnvolle Schritt ist keine weitere Leserform, sondern die Prüfung, welche
lokale physische Zustandsänderung überhaupt eine zeitliche Ursache tragen,
begrenzen und später wieder lösen könnte.
