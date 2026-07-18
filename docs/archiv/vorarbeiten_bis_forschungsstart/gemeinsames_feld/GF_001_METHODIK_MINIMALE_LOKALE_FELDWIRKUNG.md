# GF_001 Methodik: minimale lokale Feldwirkung

## Status

`GF_001` ist vollständig vorregistriert. Ein synthetischer passiver Lauf ist
methodisch freigegeben. Es wird keine Runtime-Mechanik freigegeben.

Die Methodik konkretisiert den
[Zulässigkeitsvertrag 026](ZULAESSIGKEITSVERTRAG_MINIMALE_LOKALE_FELDWIRKUNG_026.md),
ohne eine Übergangsfunktion als MCM-Mechanik auszuwählen.

## Forschungsfrage

```text
Kann eine lokale Feldprobe aus dem vollständig abgeschlossenen Vortakt
die nächste lokale Aktivierung kausal verändern?
```

Zusätzlich wird getrennt:

```text
Welche beobachtete Wirkung stammt aus lokaler Vorfeldinformation?
Welche Wirkung ist nur durch die jeweils eingesetzte feste Baseline definiert?
```

## Synthetische Prüfwelt

Die gemeinsame Feldgeometrie besteht aus zwei Reihen mit je drei Positionen:

```text
auditive Dockreihe:  A0 -- A1 -- A2
                      |     |     |
visuelle Dockreihe:  V0 -- V1 -- V2
```

Die lokalen Offsets sind ausschließlich:

```text
(-1, 0), (1, 0), (0, -1), (0, 1)
```

Damit sind in derselben Geometrie prüfbar:

- horizontale lokale Wirkung innerhalb einer Dockreihe,
- vertikale lokale Wirkung zwischen den Dockreihen,
- horizontale Spiegelung,
- vollständiger Tausch der Dockreihen.

Die Dockbezeichnungen dürfen die Übergangsfunktion nicht verändern.

## Zeitpfad

Jeder Zweig wird unabhängig neu aufgebaut:

```text
vollständiges Feld(t)
+ Weltkontakt(t+1)
-> lokale Perception aus Feld(t)
-> unabhängiger Vorschlag jedes Neurons
-> vollständiges Feld(t+1)
```

Kein Vorschlag darf Feldzustand aus `t+1` lesen. Nachhall bleibt stets null.

## Vergleichsbaselines

### B0: reine Rezeptorprojektion

```text
Aktivierung = aktueller Rezeptorkontakt
```

Bei fehlendem Rezeptorkontakt ist die Aktivierung null. Lokale Feldproben
werden ignoriert.

### B1: Hold-State

Der vorherige schnelle Zustand wird unverändert ausgegeben. Diese Baseline
prüft nur technische Persistenz und ist kein zulässiger Feldwirkungskandidat.

### B2: symmetrischer lokaler Aktivierungsmittelwert

```text
Aktivierung =
arithmetischer Mittelwert aller vorhandenen lokalen Aktivierungsproben
```

Ohne lokale Probe ist die Ausgabe null. Aktueller Rezeptorkontakt und
vorheriger Eigenzustand werden nicht gelesen.

### B3: symmetrischer gemeinsamer Mittelwert

```text
Aktivierung =
arithmetischer Mittelwert aus vorhandenem aktuellem Rezeptorkontakt
und allen vorhandenen lokalen Aktivierungsproben
```

Ein expliziter Nullkontakt nimmt als vorhandener Kontakt am Mittelwert teil.
Rezeptorabwesenheit fügt keinen Wert hinzu. Dadurch bleiben beide Rollen
beobachtbar getrennt.

B2 und B3 sind feste Forschungsbaselines. Ein positiver Befund wählt keine von
beiden als MCM-Mechanik aus.

## Interventionszweige

Für jede Baseline werden mindestens geprüft:

1. unveränderte Eingänge,
2. Ablation sämtlicher lokaler Feldproben,
3. Ablation des aktuellen Rezeptorkontakts,
4. expliziter Nullkontakt,
5. fehlender Rezeptor,
6. umgekehrte Sample-Iteration,
7. umgekehrte Neuronen-Iteration,
8. horizontale Spiegelung der vollständigen Geometrie,
9. vollständiger Tausch der Dockreihen,
10. vollständige Nullquelle,
11. ausschließlich gleiches Dock als lokale Quelle,
12. ausschließlich anderes Dock als lokale Quelle,
13. vollständige Observerentfernung,
14. unabhängiger Neuaufbau aller Zweige.

## Messgrößen

Alle Aktivierungen werden nach kanonischer Feldposition verglichen:

```text
Delta_lokal =
Antwort(originale lokale Proben)
- Antwort(Ablation lokaler Proben)
```

```text
Delta_kontakt =
Antwort(originaler Kontakt)
- Antwort(Ablation aktueller Kontakt)
```

Zusätzlich werden exakt gemessen:

- Fehler bei Sample- und Neuronenpermutation,
- Fehler nach geometrischer Spiegelung,
- Fehler nach Dockreihentausch,
- Aktivität unter vollständiger Nullquelle,
- getrennte Wirkung innerhalb und zwischen Docks,
- Observereinfluss,
- jede Änderung des Nachhalls.

## Entscheidung

Eine kausale lokale Baselinewirkung ist nur getragen, wenn:

- `Delta_lokal` ungleich null ist,
- die Wirkung bei lokaler Sample-Ablation verschwindet,
- Sample- und Neuronenreihenfolge Fehler null erzeugen,
- Spiegelung und Docktausch die Antwort äquivariant mitführen,
- ohne Quelle exakt keine Aktivität entsteht,
- der Observer das Ergebnis nicht verändert,
- keine Nachhalländerung auftritt.

Die Auswertung bleibt für B2 und B3 getrennt. Gemeinsamkeiten dürfen als
Eigenschaft symmetrischer lokaler Baselines beschrieben werden. Unterschiede
sind Folgen der verschiedenen festen Leserformen.

## Stopplinie

Der Lauf wird abgebrochen und nicht erweitert, wenn:

- technische Reihenfolge die Antwort verändert,
- Spiegelung oder Docktausch eine unbegründete Vorzugsrichtung zeigt,
- der Observer die Antwort verändert,
- ohne Quelle Aktivität entsteht,
- Nachhall verändert wird,
- ein Zweig Zustand aus einem anderen Zweig übernimmt,
- Zustand desselben neuen Takts gelesen wird,
- eine nicht registrierte Variable benötigt wird.

Unabhängig vom Ergebnis bleiben geschlossen:

- Runtimeübernahme von B2 oder B3,
- Mehrtakt-Rekurrenz,
- Eigenzustandsrückkopplung,
- Nachhallentwicklung,
- Beziehung, Ressource oder Topologie,
- Memory, Lernen, Semantik oder Reflexion,
- adaptive Parameter und Selbstregulation.

## Evidenzziel

```text
Methodik und Invarianten: E1
kausale Wirkung einer festen lokalen Baseline: höchstens E2
MCM-spezifische Feldmechanik: E0
organische Feldorganisation: E0
```

Der Lauf untersucht lokale Feldwirkung. Er sucht keine vorausgesetzte
übergeordnete Fähigkeit.

## Nächster Schritt

Als Nächstes darf ein passiver synthetischer `GF_001`-Lauf genau nach dieser
Methodik implementiert werden. Erst der Befund entscheidet, ob die lokale
Wirkungsfrage präziser gestellt werden kann. Keine getestete Baseline wird
allein durch ihr Funktionieren zur Runtime.
