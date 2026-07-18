# Befund 029: Erster externer audiovisueller Medienkontakt, Pilot

## Status

Technischer Pilotbefund. Keine Freigabe neuer Feld-, Memory-, Beziehungs- oder
Semantikmechanik.

## Frage

Erreichen Bild und Ton eines sichtbaren externen Browsermediums die vorhandenen
Kamera- und Mikrofonpfade innerhalb eines gemeinsamen, zeitmarkierten Laufs?

## Außenwelt und Phasen

Das Medium wurde ausschließlich über Monitor und Lautsprecher dargeboten.
Kamera und Mikrofon nahmen die physische Außenwirkung auf. Es gab keine direkte
Pixel- oder Audioeinspeisung in Rezeptoren oder MCM-Felder.

Der Lauf verwendete:

```text
10 s  pausiertes Anfangsbild
63 s  audiovisueller Medienkontakt
20 s  beendetes Schlussbild
```

Vor Beginn wurden 30 Kameraframes explizit verworfen. Der Medienstart lag
zwischen 14 und 66 ms hinter der vorgesehenen Phasengrenze. Die automatische
Folgewiedergabe war deaktiviert. Das Medium stand am Ende bei 1:03 von 1:03.

## Technischer Durchlauf

```text
Kameraframes insgesamt:       466
Frames außerhalb des Plans:    0
Grenzframes:                    2
Auditive Rezeptorzustände:   9288
Audioüberläufe:                 0
Visuelle lokale Träger:       288 je Phase
Auditive Frequenzlagen:        48
```

Es wurden keine Rohbilder und keine Rohsamples gespeichert. Die vollständige
technische Statusausgabe bleibt lokal im ignorierten Debugbereich.

## Beobachtete Phasenmittel

### Visuell

| Phase | mittlere absolute Rezeptoränderung | mittlere lokale Aktivierungsdifferenz |
|---|---:|---:|
| Ruhe davor | 0,000138162 | 0,005866368 |
| Medienkontakt | 0,000127664 | 0,005991757 |
| Ruhe danach | 0,000131292 | 0,006136662 |

Die globale visuelle Rezeptoränderung war während des Videos nicht höher als in
den Ruhephasen. Die lokale Aktivierungsdifferenz lag nur rund 2,1 Prozent über
der Anfangsruhe und unter der Schlussruhe.

### Auditiv

| Phase | mittlere gesamte Rezeptorenergie |
|---|---:|
| Ruhe davor | 0,006817026 |
| Medienkontakt | 0,007171463 |
| Ruhe danach | 0,006469072 |

Die auditive Rezeptorenergie lag während des Medienkontakts rund 5,2 Prozent
über der Anfangsruhe und rund 10,9 Prozent über der Schlussruhe. Alle
Rezeptorzustände enthielten messbare Energie.

## Enger Befund

Der reale gemeinsame Kamera- und Mikrofonlauf ist technisch vollständig und
ohne Überlauf durchgelaufen. Der auditive Kontakt ist als schwache
Phasendifferenz sichtbar.

Die vorhandene globale visuelle Zusammenfassung trennt den bewegten
Medienkontakt jedoch nicht von den beiden Ruhefenstern. Damit ist noch nicht
gezeigt, dass das visuelle MCM-Feld das konkrete räumliche Bewegungsmuster in
dieser Anordnung belastbar abbildet.

## Nicht gezeigt

Nicht gezeigt sind:

- ein multimodales gemeinsames Muster,
- eine kausale audiovisuelle Beziehung,
- Wiedererkennung,
- Syntax oder innere Bezeichnung,
- geschichtsabhängige Verdichtung,
- Feldintelligenz,
- ein visueller Nachhall nach dem Video.

## Kritische Grenze

Ohne einen gleich langen Nulllauf mit durchgehend pausiertem Medium kann die
kleine auditive Differenz nicht sicher vom Umgebungsrauschen oder zeitlicher
Drift getrennt werden.

Außerdem ist die globale visuelle Mittelung für räumlich begrenzte Bewegung
möglicherweise zu grob. Vor einer Wiederholung müssen deshalb lokale
Phasenaggregate sichtbar gemacht werden, ohne Bilder, Objektklassen oder
Gewinnerpositionen zu speichern.

## Nächster Schritt

1. Lokale visuelle Phasenaggregate als nicht semantische Verteilung ausgeben.
2. Einen 93-sekündigen Pausen-Nulllauf unter identischer Anordnung ausführen.
3. Erst danach denselben Medienkontakt wiederholen und gegen den Nulllauf
   vergleichen.

Bis dahin bleibt der Befund ein technischer Pilot und keine Aussage über
multimodale Musterbildung.
