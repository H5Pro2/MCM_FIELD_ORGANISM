# Historische Abrufanzeige

Auftrag: read-only Anzeigeprojektion zu `ABRUF-ANZEIGE-AUSSAGEUMFANG`.
Bezugscommit: `537109994cf777f8d36cda617aafe12226806c25`, bestehender
schmutziger Arbeitsbaum erhalten. Genau ein neuer Testaufruf: **15/15**.

## Bereitgestellte Ansicht

[Historische Ansicht öffnen](view.html). Keine laufende Sitzung, kein Start,
keine Medienwiedergabe. Ereignisauswahl liest ausschließlich abgeschlossene
Belege von `media-memory-video-20260912-01`. Die vorhandene Playeroberfläche
zeigt Zeit, Wahrnehmungs-/Memorystatus, beobachtete Originalindizes und Werte,
bankbezogene Regeln, damals passende Kandidaten mit Generation sowie Ausgang.
Alle Spuren sind historisch; keine aktuelle Verfügbarkeit wird behauptet.
Fehlende Angaben bleiben nicht belegt, Hypothesen sind keine Szenenidentität.

## Tatsächlich geprüft

Zuordnung, Mehrdeutigkeit, fehlende Positionen, Ersetzung bei gleicher Slot-ID,
fremder Lauf, falsches Ereignis, fremder Scanzustand, manipulierte Generation,
unveränderte Eingangscontainer und abgetrennte Rückgaben, fehlende/veränderte
Dateireferenzen, fehlender Scan, Audio-Regelbindung, HTML-Größe und Hypothese.

Ein echter headless Edge-Browser prüfte die neutrale Anzeige bei 1280×900 und
390×844. Erwartungsdaten stammen separat aus den Quellfixtures, nicht aus
dem produktiven Renderer. Alle vier neutralen Ereignisse und beide
Generationen wurden angezeigt. Keine HTTP-Anfrage, kein Videoelement und
kein Startkommando; keine Browserfehler oder horizontale Überbreite.
Die vollständigen Logs sind in `qualification.log` unverändert erhalten.

## Bindung und Bilanz

`binding.json` wurde vor dem Test erstellt: fünf vollständige Code-/Test-/
Aufrufdateien, vier historische Eingangsdateien, historischer Gesamtansatz,
Prüfinventar, Umgebung und Abschlussreserven. Keine historischen Passzahlen.

| Beitrag | Byte |
| --- | ---: |
| Historischer vollständiger gemeinsamer Ansatz inklusive Reserven | 1.816.345 |
| Neue Quellen, HTML-Vorlage, Tests und Aufrufcode | 37.498 |
| Neue Metadatenreserve vor Test | 32.772 |
| HTML-Ausgabereserve | 65.536 |
| Vollständige Vorbilanz | 1.952.151 |
| Tatsächliche Anzeige | 37.187 |
| Tatsächliche Bindung / vollständiges Log / Einmalmarker | 3.144 / 1.614 / 4 |
| Gemeinsamer Ansatz nach Test, inklusive voller Ergebnis-/Berichtreserve | 1.903.984 |
| Übergeordnete Gesamtgrenze | 4.194.304 |

Die vier gelesenen historischen Dateien sind im historischen Gesamtansatz
enthalten, nicht erneut addiert. Dieser Ansatz bewahrt auch die alten
Referenzinhalte. Neue Anzeige-/Qualifikationsmetadaten werden getrennt vom
unveränderten historischen Runtimeledger ausgewiesen; keine Umklassifizierung
von Zuständen. Neue gemeinsame Anzeigehülle vorab 103.034 / 262.144 Byte,
Metadaten 32.772 / 65.536 und Quellen 37.498 / 196.608 Byte.

SHA-256 der Vorbindung:
`14c5d455c85a74cb3b2c0e8252c4214cb5d72d0e4fc0939ba62e96dfbb532089`.
Anzeige:
`774cb7893af5e752bf36e7ea9768cef61e10d20affd414298fa61b99592c283d`.
Weitere Codehashes vollständig in der Vorbindung. Nach Test unverändert.

## Prüfgrenzen

Die Anzeige prüft gepinnte Dateien und ihre Lauf-/Ereignis-/Zustands-/
Generationsverknüpfungen. Sie stützt sich auf den vorhandenen historischen
Prüfbeleg; keine erneute numerische Verifikation, Zustandsdekodierung,
Distanzrechnung oder Scanausführung. Der Browserabgleich war neutral, nicht
eine neue funktionale Prüfung des Videolaufs. Fehlende Hypothesen werden
nicht ergänzt. Die historische Auswertung bleibt unverändert.

Die geänderte HTML-Datei ist neu gebunden; alte ausführbare Zulassungen
werden damit nicht als Zulassungen für diesen Quellenstand ausgegeben.
Kein neuer Live-Anschluss oder Lernlauf. Keine Runtime-/Rezeptor-/Feldaufrufe,
keine Gateöffnung. Gates False; keine neue Memorymechanik.
