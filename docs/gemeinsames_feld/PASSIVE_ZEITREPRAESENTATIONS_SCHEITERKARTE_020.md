# Passive Zeitrepräsentations-Scheiterkarte 020

## Status

Diese Untersuchung ist ein passiver Observerlauf vor `GF_001`. Sie verwendet
unverändert die vier synthetischen Kontaktwelten aus dem
[Funktionalen Zeitwirkungsvertrag 019](FUNKTIONALER_ZEITWIRKUNGSVERTRAG_019.md).
Sie führt keine Feldwirkung aus und ändert weder Runtime noch Memory.

## Frage

Welche einfachen Darstellungen bewahren gleichzeitig:

```text
F1: dieselbe gestützte Kontaktbahn trotz anderer Segmentdichte
F2: unterschiedliche zeitliche Ordnung trotz gleichem Endpunkt und Mittelwert
```

Geprüft werden nur vier Nullrepräsentationen:

- Segmentanzahl,
- letzter Endpunkt,
- zeitgewichteter Mittelwert,
- vollständige bekannte Stützbahn.

## Kontrollwelten

Für F1 tragen eine dichte Folge mit zehn Segmenten und eine grobe Folge mit
zwei Segmenten denselben konstanten Kontakt `0,5` über zehn Takte.

Für F2 werden zwei gleich lange Wege verglichen:

```text
A: 0,2 -> 0,8 -> 0,5
B: 0,8 -> 0,2 -> 0,5
```

Beide besitzen den Endpunkt `0,5` und den zeitgewichteten Mittelwert `0,5`.
Nur ihre Reihenfolge unterscheidet sich.

## Ergebnis

| Nullrepräsentation | F1 invariant | F2 zugänglich | feste Breite in den Kontrollen |
|---|---:|---:|---:|
| Segmentanzahl | nein | nein | ja |
| letzter Endpunkt | ja | nein | ja |
| zeitgewichteter Mittelwert | ja | nein | ja |
| vollständige bekannte Stützbahn | ja | ja | nein |

Die Segmentanzahl verwechselt Darstellungsdichte mit Kontakt. Endpunkt und
Mittelwert beseitigen diesen Fehler in der konstanten Welt, lassen aber die
beiden geordneten Wege kollidieren. Nur die vollständige bekannte Stützbahn
trägt in diesen Kontrollen beide Vertragsachsen. Ihre Nutzlast wächst jedoch
mit den tatsächlichen Kontaktwechseln: ein Element in den konstanten Welten,
drei Elemente in den geordneten Welten.

## Tragfähiger Befund

Die drei einfachen festen Nullzusammenfassungen genügen dem Vertrag 019 nicht.
Die vollständige bekannte Stützbahn zeigt lediglich, welche Sollinformation
in den geprüften Welten vorhanden sein muss.

Nicht gezeigt ist:

- dass die vollständige Bahn minimal ist,
- dass keine kompakte ordnungssensitive Darstellung existiert,
- dass jede zeitliche Unterscheidung für das Feld relevant werden muss,
- wie reale visuelle Weltstütze bestimmt wird,
- wie zeitliche Information auf Neuronen oder Feld wirkt.

Ein Bestehen an nur einem geordneten Kontrollpaar wäre kein allgemeiner
Nachweis. Die Scheiterkarte wählt daher keinen Gewinner aus.

## Stopplinie

`GF_001` bleibt geschlossen. Nicht freigegeben sind:

- eine Sequenz- oder Zusammenfassungsschnittstelle der Runtime,
- ein Zeitintegrator oder lokaler Zeitwirkzustand,
- Speicherung vollständiger Rezeptorfolgen,
- Zeitkonstanten, Schwellen oder Toleranzen,
- Feldkopplung, Memory, Topologie oder Lernen.

## Nächster Prüfpunkt

Vor einer Mechanik muss geprüft werden, ob breitere, aber weiterhin feste
zeitliche Zusammenfassungen unter kontrollierten Verlaufspaaren kollidieren.
Der nächste Lauf darf deshalb nur adversarielle Kollisionsfamilien für
kompakte Nullzusammenfassungen konstruieren. Er darf weder eine bevorzugte
Repräsentation noch eine Feldgleichung vorwegnehmen.

Die [Passive Kompaktzusammenfassungs-Kollision 021](PASSIVE_KOMPAKTZUSAMMENFASSUNGS_KOLLISION_021.md)
führt diese Kontrolle mit zwei exakten Zeitumkehrungen aus. Ein festes Bündel
aus 13 Lage-, Moment-, Änderungs- und Nachbarschaftskennwerten kollidiert
vollständig. Damit ist Zeitrichtung als fehlende Information isoliert, nicht
die Unmöglichkeit jeder kompakten Darstellung bewiesen.
