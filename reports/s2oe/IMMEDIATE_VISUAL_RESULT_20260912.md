# Unmittelbarer visueller Abruf aus dem eingefrorenen e03-Eingang

`immediate-visual-retrieval-20260912-01` wurde genau einmal über den gebundenen
Dateieinstieg ausgeführt. RECORDING_COMPLETE, anschließend genau eine
unabhängige Gesamtverifikation: **EVIDENCE_VALID, evaluation_allowed=true**.
Danach einmal getrennt ausgewertet. Kein Retry oder technischer Abbruch.

## Vier getrennte Befunde

| Kontrolle | Leerabruf | Unmittelbarer Wiederabruf |
| --- | --- | --- |
| Prüffähige Kandidaten B4 / Fast / visuell Slow | 0 / 0 / 0 | 1 / 1 / 0 |
| Sichtbare Wertegleichheit | kein Kandidat, nicht geprüft | je 32/32 Gleichheitsprüfungen erfolgreich |
| Öffentliche Entscheidung | ABSTAIN_NO_CONTEXT | ADMIT_SINGLE_CONTEXT, A_RECENT |
| Primär-/Direktbaseline | übereinstimmend | übereinstimmend |

Die neue reguläre Formation erzeugt `b4.slot.000` und
`tspm1.fast.slot.000`, Memorygeneration 1. Fast-Support ist 1, noch keine
Konsolidierung oder PPB-Fortschreibung. Beide vorhandenen visuellen Kandidaten
besitzen denselben vollständigen Wertedigest und bestehen die interne
288-Werte-Gleichheitsprüfung. Deshalb bilden ihre zwei Bankbelege genau einen
öffentlichen A-Kontext, keine Mehrdeutigkeit. Die Gleichheit wurde nach der
bestehenden Abrufvorschrift geprüft; keine zusätzliche Bitvergleichsserie.

Die 32 beobachteten Positionen liefern je Kandidat einen Treffer. Die übrigen
256 Positionen sind im Cue None und werden nicht als verdeckte Wahrnehmung
übergeben. Die ausgegebene getrennte Hypothese enthält das gespeicherte
Komplement; sie wurde nicht angewandt. Beide Hinweise erhalten ihren jeweiligen
Memoryzustand unverändert. Kein Zwischenereignis zwischen Formation und Abruf.

Der Nachweis `fast_selected=null` in `verification.json` bezeichnet das Ergebnis
der unabhängigen Match-Rangprüfung auf dem leeren Vorzustand, nicht das Fehlen
einer anschließenden Fast-Neubelegung. Diese wird durch die Formation und den
gespeicherten Fast-Slotbeleg bestätigt.

## Herkunft und Umfang

Wiederverwendet wurde der vollständig geprüfte historische e03-Rezeptoreingang,
keine neue Medienquelle: vollständige 48 Halbwerte und 288 visuelle Werte.
Historische Herkunftszeiten blieben erhalten; neue Präsentationszeiten und
Digests sind getrennt gebunden. Keine Decoder-, Medien-, Rezeptor-, NJ- oder
Feldausführung. Eine atomare Formation und vier vollständige öffentliche
Scans einschließlich unabhängiger Baselines, zusammen 64 Slotprüfungen.
Funktionale Scans: insgesamt 704 Wertevergleiche; unabhängige Verifikation
separat ebenfalls 704. Die Verifikation prüfte eine Formationsrelation.

Drei vollständige Elternlesezugriffe: **4.079.334 Byte**. Der Elternrecord
wird als Ablage nur einmal mit 1.359.778 Byte gezählt. Administrative Code- und
Referenzprüfungen sind keine Medienzugriffe.

## Abschluss und Bilanz

Record: 103.238 Byte, SHA-256
`f8766bf6b663cb70d79a025e54d6d38b4543327a2738d0de7c72eda23c27d777`.
Der gespeicherte technische Abschluss zählt vollständig:
**1.625.862 / 4.194.304 Byte**, darunter Metadaten **43.795 / 65.536**,
Quellen 35.678 / 174.080, Verifikation 83.373 / 262.144 und historische
Eingangsdatei 1.359.778 / 2.097.152. Keine Budgetverletzung.
`balance.json`, Record, Verifikation und Auswertung bleiben unverändert.
Dieser nachgelagerte Bericht samt eigener Bilanzergänzung wird zusätzlich
als Metadaten mitgezählt; siehe `immediate-visual-report-balance.json`.

## Aussagegrenze

Der unmittelbare visuelle Abruf einer noch vorhandenen, regulär gebildeten
Spur funktioniert für diesen eingefrorenen Eingang. Das ist kein neuer
Nachweis einer wiederholten Rezeptormessung, langfristiger Stabilisierung,
Abrufbarkeit nach Verdrängung oder Objektidentität. Die vier Enthaltungen des
früheren Videoversuchs bleiben unverändert und werden dadurch nicht widerlegt.

Sitzung abgeschlossen, Gates False. Einmallauffreigabe verbraucht.
Keine automatische Folgeausführung.
