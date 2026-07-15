# Befund 013: Sparsamer auditiver Schnellfeld-Kandidat

## 1. Kurzurteil

Der passive Kandidat erfüllt den kleinsten technischen auditiven Feld- und
Dockvertrag:

```text
verteilte aktuelle Rezeptorlage
+ unabhängiger lokaler Nachhall
-> unveränderliches auditives MCMFieldWindow
```

Er bleibt dabei in jedem geprüften Schritt exakt identisch zur unabhängigen
B1-Baseline. Es wurde keine zusätzliche MCM-Feldmechanik gefunden oder
eingeführt.

## 2. Tatsächlich geprüft

Die Projektion wurde mit kontrollierten Drei-Träger-Folgen und drei
Zeitkonfigurationen geprüft:

```text
dt = 0,01; tau = 0,05
dt = 0,02; tau = 0,20
dt = 0,10; tau = 1,00
```

In allen Fällen galt:

- aktuelle Rezeptorenergie wurde trägergetreu als Gegenwart erhalten,
- jeder Nachhallwert war exakt gleich der B1-Ausgabe,
- kein kontaktierter Träger wirkte auf einen anderen Träger,
- gleiche Eingangsfolge erzeugte dieselben Zustandsdigests,
- Geometrie- und Trägerwechsel wurden abgelehnt,
- nicht fortlaufende Schnappschüsse wurden abgelehnt,
- der fertige Zustand konnte am auditiven Dock unverändert verteilt werden.

Keine Zeitkonfiguration wurde als Runtime-Parameter ausgewählt.

## 3. Rezeptorfenster und Feldnachhall

Ein synthetischer Breitbandpfad erhielt zunächst 100 ms eines 1-kHz-Kontakts
und anschließend 100 ms exakte Stille.

Nach dem vollständigen Stillefenster galt:

```text
aktuelle auditive Rezeptorlage = exakt null
lokaler B1-Nachhall           = weiterhin ungleich null
```

Der Nachhall erweitert damit die gegenwärtige lokale Zeitlage über das
technische 100-ms-Rezeptorfenster hinaus.

Dieser Effekt folgt vollständig aus B1. Er belegt weder Lernen noch
Beziehungsgeschichte.

## 4. Was der Kandidat kann

Der Kandidat kann technisch:

- eine verteilte auditive Gegenwart erhalten,
- unmittelbare lokale Geschichte endlich tragen,
- bei gleicher Gegenwart unterschiedliche unmittelbare Vorgeschichte tragen,
- vollständig ohne Trägerkopplung arbeiten,
- einen neutralen Verteilerzustand bereitstellen.

Damit ist er als sparsames schnelles sensorisches Trägergerüst brauchbar.

## 5. Was nicht gezeigt ist

Nicht gezeigt sind:

- eine intern neu gebildete Aktivierung jenseits der Rezeptorenergie,
- lokale Wechselwirkung zwischen Frequenzträgern,
- selbst entwickelte Nachhallzeit,
- adaptive Erregbarkeit,
- Beziehungsgeschichte,
- Topologiewachstum,
- Reflexion, Semantik oder Handlung,
- organische Entwicklung oder Feldintelligenz.

Die Rolle `activation` im ausgegebenen Fenster erhält lediglich die aktuelle
Rezeptorverteilung. Sie ist keine nachgewiesene zusätzliche Feldwirkung.

## 6. Kritischer Einwand

Der Kandidat könnte vollständig so beschrieben werden:

> Ein technischer Rezeptorvektor wird gemeinsam mit einem unabhängigen
> Leaky-Vektor in einen Feldvertrag verpackt.

Dieser Einwand ist zutreffend. Genau deshalb wird der Kandidat nicht als neue
MCM-Mechanik ausgegeben.

Sein Wert liegt in der sparsamen Architektur: Er zeigt, dass für einen ersten
schnellen sensorischen Feldträger keine Kopplung, Spikefunktion oder feste
semantische Verdichtung erforderlich ist.

## 7. Architekturstatus

```text
passiver auditiver Schnellfeld-Kandidat: E1
zusätzliche auditive Feldmechanik:        E0
Runtime-Freigabe:                         nein
```

Der allgemeine Architekturplan bleibt bei `contract_only`, weil der Lauf eine
endliche Forschungsprojektion und keine ausgewählte kontinuierliche Runtime
prüft.

## 8. Bester nächster Schritt

Der Kandidat darf nun in einem endlichen rein auditiven Weltkontakt als
vollständige Kette beobachtet werden:

```text
Audio-In
-> auditive Rezeptoren
-> sparsamer Schnellfeld-Kandidat
-> auditiver Dock
-> unimodale Feldkonstellation
```

Dabei werden mehrere Nachhallzeitkandidaten nur parallel beobachtet. Keine
Variante darf den Weltkontakt beeinflussen oder sich selbst auswählen.
