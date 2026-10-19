# DATEIBETRIEB-CHECKPOINT-BEDIENUNG: Abschluss

`media-restart-qualification-20260913-02`: genau ein Aufruf, **8/11**,
`NOT_QUALIFIED` (ein Fehlschlag, zwei Fehler), 92,751 s. Kein Retry.
Bezugscommit `537109994cf777f8d36cda617aafe12226806c25`; vorhandener
uncommitteter Arbeitsstand. Codehashes vor/nach dem Aufruf unverändert.
[Quellen und Prüfbestand](preregistration.json), [Ergebnis](result.json),
[vollständiges Testlog](stderr.log). Vorbindung SHA-256:
`8c69477af4608fa15a7e72a01fa4c6ef2c3d8089295b42cee1ea08f546d79171`.

## Erreichte Prüfdeckung

Bestanden: unabhängige Referenzauflösung und Manipulationsabwehr;
Budgetgleichstand/Überschreitung an allen 21 synthetischen Positionen;
Primärfehler nach einer nativen Formation mit unveränderter Feldwirkung
und Memorybindung; Positions-, Quellen- und Verbrauchsabwehr beider
Checkpoints; Player erhält den Primärfehler ohne zweite Publikation.

Referenz, frühes Speichern/Fortsetzen und spätes Speichern abgeschlossen.
Später Restore verarbeitet 20 Ereignisse und publiziert `record.json`,
scheitert aber beim Playerabschluss. Dieser Teilbeleg ist kein gültiger
Gesamtabschluss. Die getrennten frühen/späten Vergleichsgruppen scheitern
bereits beim Publizieren ihres Prüfclaims. Keine native Gesamtverifikation,
keine bestätigte Gesamtgleichheit oder Funktionsauswertung daraus ableiten.

## Gespeicherter Primärfehler

[failure.json](late-restore/failure.json): `MEDIA_STORE_BUDGET`,
`PLAYER_CLOSE`, Ereignis/Fortschritt 20, Belegklasse Metadaten:

| Beitrag | Byte |
|---|---:|
| Tatsächliche aktuelle Metadaten | 108.463 |
| Beantragte Datei | 1.348 |
| Veröffentlichung mit temporärer Kopie | 2.696 |
| Primärfehlerreserve | 8.192 |
| Administrative Abschlussreserve | 12.288 |
| Prospektive Summe | 131.639 |
| Grenze / Überschreitung | 131.072 / 567 |

Der vollständige Fehlerbeleg umfasst 2.394 Byte. Kein `INCOMPLETE` ersetzt
den Primärfehler. Decoder geschlossen, Gates False. Die fehlende historische
Auslösesumme des alten 11/12-Laufs bleibt weiterhin unbekannt.

## Bilanz und offene Korrekturgrenze

Vorreserviert: 128.266 Byte Metadaten, 3.803.236 Byte gesamt. Die gemeinsame
Metadatenobjekt-Reserve von 40.960 Byte war keine tragfähige Obergrenze:
Ist 47.748 Byte, Differenz 6.788 Byte. Physische Belegung und zusätzlich
festgehaltene Reserven sind zu unterscheiden. Vollständige Logs bleiben
erhalten. Die finale Istbilanz einschließlich dieses Berichts und eigener
Bilanzdatei steht in `closure-balance.json`; keine Grenzen erhöht.

Nötig wäre eine belastbare Index-/Abschlusshüllenbindung mit eindeutigem
Reserveverbrauch statt mehrfacher Belegung bereits beanspruchter Reserven.
Hier nicht umgesetzt. Keine Memory-, Rezeptor- oder Decoderkorrektur.

Alte Prüfgruppen wurden nicht pauschal wiederholt; unveränderte Abhängigkeiten
und alte Teildeckung sind vorgebunden, kein historischer Passzahlübertrag.
Alter 11/12-Lauf bleibt NOT_QUALIFIED. Nur synthetischer Codec mit nativen
Rezeptoren/Runtime; kein realer Videolauf. Weitere Ausführung gesperrt.
