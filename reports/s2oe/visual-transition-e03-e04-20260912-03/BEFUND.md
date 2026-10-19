# e03 → e04: visuelle PPB-Zuordnung numerisch erklärt

2026-09-12; Bezugscommit `537109994cf777f8d36cda617aafe12226806c25` plus
die ausdrücklich gebundenen Arbeitsdateien. Diagnose
`visual-transition-e03-e04-20260912-03`: **EVIDENCE_VALID**.

## Umfang und Herkunft

13 neue Anschlusskontrollen genau einmal bestanden unter
`visual-reference-qualification-20260912-02`. Die 12/12 Tabellenprüfungen
wurden nicht wiederholt. Anschließend genau eine Tabellenberechnung und
eine unabhängige read-only Belegprüfung, beide erfolgreich.

e03 und e04 sind direkt benachbarte vollständige Formationen in der
abgetasteten Ereignisfolge, nicht unmittelbar aufeinanderfolgende Videoframes.
Der e03-Nachzustand entspricht dem e04-Vorzustand. Die vollständigen
gespeicherten Werte, nativen Zustandsdigests, Zeit- und Profilbindungen wurden
vor der Rechnung geprüft. Keine Werte wurden aus Digests rekonstruiert.

Die gemeinsame historische Hülle wurde mit dem bestehenden `unpack()`
aufgelöst, erst danach wurden ihre nativen Digests geprüft. 85 statisch
ermittelte aktive Offline-Dateien sind gebunden. Die aktuelle PPB-Regeldatei
stimmt mit der historischen Inventarbindung überein:
`mcm_field_organism/_ppb1_reference.py`, SHA-256
`15f1fabaa45348f067b7bf466f138d275d74f75a6e98afc05867f7b8c35d46f0`.

**Herkunftsgrenze:** Die beiden damals verwendeten Decoder-/Workerdateien
sind weder in der Git-Historie noch in den vorhandenen Quellarchiven mit
ihren exakten Hashes verfügbar. Historische Hashes und Größen bleiben in
`binding.json` und `verification.json` erhalten. Heutige Dateien wurden
nicht als Ersatz verwendet. Die damalige Softwareidentität ist daher nicht
vollständig unabhängig rekonstruiert. Beide Module gehören nicht zum aktiven
Offline-Satz; ihre Imports werden ausdrücklich blockiert und neutral geprüft.
Der gespeicherte Elternrecord ist weiterhin durch seinen ursprünglichen
Datei-SHA gebunden. Keine neue Bestätigung der historischen Medienmessung.

## Alle vier damaligen visuellen Slots

Die ursprüngliche Zuordnungsregel prüft belegte, nicht abgelaufene Prototypen
mit `math.fsum(abs(q[i]-p[i])) / 288 <= 0.01`. Support 1 schließt eine
erneute Formationszuordnung nicht aus; er reicht lediglich noch nicht für
einen stabilen öffentlichen B-Abruf.

| Slot | Generation | Support | Abstand | Abstand minus 0,01 | Match |
| --- | --- | ---: | ---: | ---: | --- |
| 000 | e02 | 1 | 0,034057930258008545 | +0,024057930258008543 | nein |
| 001 | e03 | 1 | 0,030183521569636083 | +0,020183521569636084 | nein |
| 002 | frei | – | nicht berechnet | nicht anwendbar | kein Kandidat |
| 003 | frei | – | nicht berechnet | nicht anwendbar | kein Kandidat |

Binary64-Distanzen: Slot 000 `0x1.1700a81415434p-5`,
Slot 001 `0x1.ee86dd8142b99p-6`. Alle 576 Einzelterme einschließlich
Originalindizes und Hexdarstellung sind in `table.json` gespeichert.

Keiner der belegten Slots war abgelaufen. Der nächste PPB-Schritt ist 3;
die Ablaufgrenze bleibt 64. Beide Distanzen liegen über 0,01. Damit gibt es
keinen Match, und von den freien Slots wird regelkonform die kleinste ID
gewählt: **CREATED in Slot 002, Support 1**.

Dies stimmt mit dem aufgezeichneten Übergang und vollständigen Nachzustand
überein. Slots 000 und 001 bleiben in diesem Übergang unverändert. e04
verstärkt deshalb nicht die e03-Generation, sondern legt eine weitere Spur
an. **Bei e04 findet noch keine Ersetzung statt.** Die späteren Ersetzungen
sind ein getrennter bereits dokumentierter Verlauf, hier nicht nachgerechnet.

## Arbeit und Bilanz

Primär: 576 explizite Differenzen und 576 im bestehenden Distanzhelfer.
Unabhängige Prüfung: separat 576 Differenzen; keine Übernahme primärer
Summen oder Auswahlentscheidung. Insgesamt **1.728**, kein weiterer Übergang.
Keine Medienanalyse, NJ-Projektion, Memoryfortschreibung, Feld- oder Abrufausführung.

Konservative vollständige Abschlussalternative: **3.743.689 / 4.194.304 Byte**,
Metadaten **63.508 / 65.536 Byte**, Tabelle plus Prüfung 200.704 / 262.144 Byte.
Erfolg und Fehler wurden getrennt bilanziert, einschließlich Fehler nach
gespeicherter Prüfung und Abschlussbericht. Die lokale Bindungsreserve
berücksichtigt die vollständigen Quellenrollen mit 28.672 Byte; keine
übergeordnete Grenze wurde erhöht.

Ist: Tabelle 104.075 Byte, Prüfung 616 Byte, Bindung 25.178 Byte,
Qualifikationslog 1.697 Byte. `balance.json` zählt sämtliche gebundenen
Referenzdateien physisch einmal (3.479.477 Byte) und alle technischen Ausgaben.
Bericht und abschließende Istbilanz bleiben innerhalb ihrer mitgebundenen
8.192-Byte-Reserven. Die finale Istbilanz wird separat beigelegt.

## Aussagegrenze

Die fehlende Wiederzuordnung ist für diesen Übergang durch die unveränderte
Distanzregel erklärt, nicht durch fehlende Daten, Ablauf oder einen
Implementierungsfehler. Daraus folgt weder eine Schwellenempfehlung noch
eine Lösung für visuelle Erhaltung. Kein Fokus-, Wiederholungs- oder
Identitätsnachweis. Historische Fehlversuche bleiben unverändert erhalten.
Gates False; keine weitere Ausführung und kein automatischer Folgeversuch.
