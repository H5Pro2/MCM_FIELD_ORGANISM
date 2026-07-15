# Befund 015: Kontrollierte 20/20/20-Feldkette

## 1. Kurzurteil

Der externe Regler erzeugt exakt:

```text
20 Sekunden Mehrtonkontakt
-> 20 Sekunden numerische Stille
-> 20 Sekunden denselben Mehrtonkontakt
```

Die vollständige auditive Kandidatenkette folgt allen drei Weltphasen. Die
Rezeptorlage wird nach dem vollständigen 100-ms-Nullfenster exakt null, die
drei lokalen Nachhallkandidaten relaxieren gemäß B1 und dieselbe Weltwirkung
stellt anschließend dieselbe Rezeptorlandschaft wieder her.

Der Lauf trägt E2 für die kausale technische Phasenantwort. Er trägt keine
zusätzliche MCM-Feldmechanik.

## 2. Regler

```text
Signal:             250 Hz + 1.000 Hz + 4.000 Hz
Komponentenpegel:   jeweils 0,2
Abtastrate:         48.000 Hz
Chunk:              480 Samples / 10 ms
Phase 1:            2.000 Signalchunks
Phase 2:            2.000 exakte Nullchunks
Phase 3:            2.000 wiederholte Signalchunks
Gesamt:             6.000 Chunks / 60 Sekunden Feldzeit
```

Die dritte Phase startet dieselbe lokale Wellenform erneut. Der Regler erzeugt
jeden Chunk erst beim Lesen und speichert keine Audiofolge.

## 3. Rezeptorantwort

```text
vollständige Rezeptorlagen: 5.991
Phasenlagen:                1.991 / 2.000 / 2.000
active_zero je Phase:       0 / 1.991 / 0
```

| Signalphase | mittlere Summe der aktuellen Rezeptorenergie |
|---|---:|
| Signal 1 | 0,764004 |
| Signal 2 | 0,763190 |

Die Mute-Phase wird getrennt ausgewiesen:

| Schicht | Umfang | aktuelle Rezeptorwirkung |
|---|---:|---:|
| Gate-Ausgabe | 2.000 Chunks | exakt null |
| Übergang des 100-ms-Rezeptorfensters | 9 Lagen | Mittelwert 0,583238 |
| stabile Rezeptorlage | 1.991 Lagen | exakt null |

Die neun Übergangslagen enthalten noch abnehmende Anteile der ersten
Signalphase. Sie sind keine fortlaufende Weltwirkung während Mute.

Die erste vollständig aufgebaute Rezeptorlage von Phase 1 und Phase 3 ist
exakt gleich. Auch die jeweilige letzte Lage ist exakt gleich.

## 4. Nachhallantwort

Mittlere Summe des lokalen Nachhalls in den beiden Signalphasen:

| `tau` | Signal 1 | Signal 2 |
|---:|---:|---:|
| 0,05 s | 0,762271 | 0,761464 |
| 0,20 s | 0,756520 | 0,755739 |
| 1,00 s | 0,725823 | 0,725180 |

Während der stabilen Mute-Rezeptorlage ist die aktuelle Rezeptorwirkung null.
Nur der davon getrennte B1-Feldnachhall relaxiert weiter.

Am Ende der 20-sekündigen Mute-Phase verblieb:

| `tau` | gesamte Restspur |
|---:|---:|
| 0,05 s | `5,69e-174` |
| 0,20 s | `4,00e-44` |
| 1,00 s | `1,69e-9` |

Die Werte sind exakt aus B1 vorhergesagt. Sie entstehen weder durch
Beziehungsgeschichte noch durch Offline-Erholung.

Nach der zweiten vollständigen Signalphase entsprach der Nachhall für
`tau = 0,05 s` und `tau = 0,20 s` wieder exakt dem Ende der ersten Signalphase.
Bei `tau = 1,00 s` betrug die maximale lokale Differenz nur `2,84e-11` und
entspricht der noch endlich relaxierenden Restspur.

## 5. Tatsächlich gezeigt

- Der Regler schaltet chunkgenau und reproduzierbar.
- Die Mute-Phase ist auf Quellenebene bitgenau null.
- Das 100-ms-Rezeptorfenster erklärt die neun Übergangslagen vollständig.
- Danach ist die aktuelle verteilte Rezeptorlage exakt null.
- Lokaler Feldnachhall kann trotz aktueller Nullage zunächst fortbestehen.
- Seine Reichweite bleibt für alle drei Kandidaten vollständig B1-erklärbar.
- Derselbe spätere Weltkontakt erzeugt dieselbe verteilte Rezeptorlage.
- Keine Nachhallvariante verändert Quelle, Rezeptor oder andere Varianten.

## 6. Nicht gezeigt

- reale Mikrofonstille,
- natürliche Wahl einer Nachhallzeit,
- adaptive Erregbarkeit,
- Trägerkopplung,
- Beziehungsgeschichte oder entwickelte Topologie,
- Reflexion oder Offline-Erholung,
- Semantik, Handlung oder Feldintelligenz.

## 7. Kritischer Einwand

Der gesamte Verlauf ist durch bekannte technische Komponenten bestimmt:

```text
deterministischer Pegelregler
-> gleitendes Rezeptorfenster
-> unabhängiger Leaky-Nachhall
```

Dieser Einwand erklärt den Befund vollständig. Das Ergebnis rechtfertigt keine
neue Feldmechanik.

## 8. Evidenz und Status

```text
Regler und Phaseninvarianten:      E1
kausale technische Phasenantwort: E2
zusätzliche MCM-Feldmechanik:      E0
organische Entwicklung:           E0
Runtime-Freigabe:                  nein
```

## 9. Bester nächster Schritt

Der Regler bleibt als kontrollierte Nullwelt erhalten. Weitere reine
Nachhallzeiten würden nur die bekannte B1-Gleichung erneut bestätigen.

Als nächstes sollte geprüft werden, ob dieselbe sparsame Zustandsgrenze auch
für den visuellen Sensorast trägt, sobald die Kamera verfügbar ist. Erst die
zeitgleiche, getrennt erhaltene auditive und visuelle Feldlage eröffnet eine
nicht bereits durch mehr auditive Glättung beantwortete Forschungsfrage.
