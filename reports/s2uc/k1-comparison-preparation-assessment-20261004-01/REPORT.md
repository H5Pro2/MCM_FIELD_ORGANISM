# U/K1-Vergleichshülle: neutral qualifizierter Abschluss

Die ausführbare Vergleichshülle liegt vor. Endgültige Qualifikation V2:15/15
Prüfungen PASS; Vorstartbindung und verlustfreie Belegverpackung geprüft.
Der Forschungsvergleich wurde nicht ausgeführt. Keine F1–F8-Quellen wurden
materialisiert; kein T1-Replay. K1-Verhalten und Bewertungskriterien bleiben
eingefroren. Die technische K1-Abnahme des Projektleiters ist berücksichtigt.

## Implementierte Dateien

- `tools/_s2uc_k1_compare_sources.py`: feste24-Fälle-Beschreibung, T1-Lesen aus
  gebundenen Dateien, ausschließlich später im autorisierten Worker aktive
  F-Formel; separater neutraler Ersatzdatenzweig.
- `tools/_s2uc_k1_compare_engine.py`: zwei frische Varianten mit je eigener
  unabhängiger K1/U-Referenz; Prüfung von Bestand, exakten und skalierten Matches,
  Berechtigung, eingefrorenen Originalen, EMA, Promotion/Pruning und Auswahl.
  Vollständiger Fallauswerter und Aggregator für vier getrennte Urteile.
- `tools/s2uc_k1_compare.py`: Vorbereitung, Code-/Vorstartprüfung, neutraler
  Qualifikator, exklusiver Start, Workerüberwachung, Exportkappen, gesicherter
  Abschluss sowie verlustfreie ZIP-Verpackung der Qualifikationsbelege.
- `tests/test_s2uc_k1_compare.py`:15 neutrale Integrations-, Gegen- und
  Fehlerpfadprüfungen.
- Neue V2-Plan-, Codebindungs-, Vorstartbindungs- und Autorisierungsvorlagendateien
  sowie ausführbare Aufrufanleitung in `docs/`; README/Forschungsweg aktualisiert.

Kein bestehendes K1-Produktionsmodul wurde geändert. Bereits gültige K01–K10-
Verhaltenstests wurden nicht wiederholt. Historische Laufarchive bleiben erhalten.

## Feste Vergleichs- und Bewertungsgrenzen

Die16 T1-Fälle werden in gespeicherter Reihenfolge mit80 Positionen verwendet,
F1–F8 mit jeweils64 Positionen exakt nach Konzeptvertrag. Insgesamt24 Fälle,
48 Arme,1.792 Quellpositionen,3.584 Aufnahmen und3.584 unabhängige
Referenzfortschreibungen.624 T1- und248 F-Ziele werden je Variante bewertet.
Die letzte Prognose ist jeweils zensiert. Kein gemeinsamer U/K1-Speicher.

Je Ziel werden beide lebenden Hypothesenmengen, Originalordinalen/Offset,
vorzielliche Fehlerzellen, Feedbackpositionen, Promotionslinie, gewählte
Hypothese, Kaltheit/Gleichstand/fehlender Vorteil und tatsächlicher Fehler
gespeichert. Gewonnene/verlorene Hypothesen sowie warme Möglichkeiten werden
über Originalidentitäten verglichen; tatsächliche und modale Übereinstimmung
sind getrennt ausgewiesen. Alle Bestandsänderungen sind je Aufnahme verfügbar.
Neue, nicht übernommene Originalblöcke bleiben im Lebenszyklusbericht sichtbar;
eine Bestätigung alter Werte ist dabei keine behauptete neue Lernerfahrung.

Die primäre Mechanismusprüfung bleibt der streng höhere Anteil mit lebendem
modalem Nachfolger und vorziellichem Feedback über624 T1-Ziele.324 Diagnoseziele
werden nur ergänzend berichtet. Gesamtnutzen erfordert zugleich strikt bessere
T1-Fallmittel, nicht schlechtere F-Fallmittel und ein strikt besseres gleich
gewichtetes Mittel aller24 Fälle. Berechnung mit exakten Brüchen der beobachteten
MAE-Werte, ohne gerundete Entscheidung. Schäden bleiben vollständig sichtbar:
kein Fallmittelabstand über1/32, G_w der vier S0-Fälle nicht schlechter.
52 Anpassungsübergänge einschließlich20 Kontrollen und unveränderte Schwellen
26/52 sowie mindestens4/13 je Gruppe werden zusätzlich berichtet.

## Neutrale Qualifikation

Endgültiger Belegordner: `../k1-comparison-neutral-20261004-02/`.
Prüfabschluss PASS,15 Prüfungen, keine Fehler oder Fehlschläge, Gesamtdauer
10,1456894s. Die absichtlich erzeugten Worker-Ausnahmen sind bestandene
Fehlerpfadprüfungen; sie sind keine unerwarteten Qualifikationsfehler.

| Prüfung | Geprüftes Verhalten | Ergebnis |
| --- | --- | --- |
| 01 | Gesamte Pipeline:24 Ersatzfälle,48 Arme,3.584 Aufnahmen/Referenzen,872 Ziele, vollständige Auswertung | PASS |
| 02 | Ungültiger Start: Abschluss vor Workerstart, keine Quellen | PASS |
| 03 | Prozessstartfehler hinterlässt terminalen Abschluss | PASS |
| 04 | Zeitlimit beendet Worker und schließt ab | PASS |
| 05–06 | Harter Workerabsturz und behandelte Worker-Ausnahme | PASS |
| 07 | Exportreserve und Vorbereitungsgrenze | PASS |
| 08 | Bestehende Ausgabe bleibt unverändert, separater Ablehnungsbeleg | PASS |
| 09 | Fehlende Ziele und Ressourcenüberschreitung werden abgelehnt | PASS |
| 10 | Gleichheit ist kein Nutzen/Mechanismusgewinn; Schadensüberschreitung wird erkannt | PASS |
| 11 | Forschungsgate geschlossen, Ersatzdaten ohne Forschungsdecoder | PASS |
| 12 | Fristablauf und Abbruch vor Workerstart | PASS |
| 13 | Abbruch nach Workerstart und Exportfehler im Worker | PASS |
| 14 | Tatsächlicher Autorisierungsprüfpfad: fehlende/falsche Datei | PASS |
| 15 | Vollständige Exportobergrenze und einzelne Dateikappe | PASS |

Neutrale Eingaben verwenden .1875+(Index+1)/512+j/131072 und eigenständige
Muster. Weder T1-Quellwerte noch F-Formel werden in diesen Läufen an die Policy
übergeben. Die24 Fälle behalten die vertraglichen Längen und Maskengeometrien,
damit Auswertung und vollständige Nenner tatsächlich geprüft sind. Neutrale
Ergebnisurteile begründen keinerlei fachliches Urteil über T1/F.

Die erste Hüllenqualifikation01 bestand12 Prüfungen. Beim anschließenden
Budgetabgleich wären unkomprimierte Qualifikationsbelege plus Eingangsbindung
größer als8MiB gewesen. Deshalb wurde vor einem Forschungsstart die Hülle
erweitert: verlustfrei komprimierte Startbelege, explizite Dateikappen und
zusätzliche Fehlerpfadtests. Version01 samt damaligem Quelltext bleibt unter
`../k1-comparison-envelope-repair-20261004-01/` nachvollziehbar. Version02 ist
der allein gültige Startstand. Zwei vollständige neutrale Integrationsläufe
wurden ausgeführt; dazu die gezielten Fehler- und Quellengateprüfungen.

## Ressourcen, Zeit und Verpackung

| Größe | Endgültiger neutraler Befund | Grenze |
| --- | --- | --- |
| Zusatzheap im bestehenden Policy-Messumfang | 8.818 Byte | 16.384 Byte |
| Konservative Originalframe-Obergrenze | 16 | 18 |
| Ausgabeslots | 2 | 2 |
| Konservative kombinierte Obergrenze | 18 | 20 |
| Gepackte Bank | 416 Byte | 416 Byte |
| Receipt | 1.476 Byte | 16.384 Byte |
| UTF8-Obergrenze | 2.952 Byte | 32.768 Byte |
| Vollständiger neutraler Worker | 5,0185012s | später höchstens3.540s |
| Neutraler Supervisor vor terminalem Schreiben | 6,4890005s | neutral300s, später3.600s |
| Vollständiger neutraler Integrationsordner | 7.440.883 Byte | spätere Exportbilanz siehe unten |
| Verlustfreies Qualifikations-ZIP | 380.373 Byte | Teil der Vorbereitung |
| Vorbereitung mit Vorlage als Autorisierungsplatzhalter | 2.340.146 Byte | 8.388.608 Byte |

Für eine echte zusätzliche Autorisierungsdatei kommen deren tatsächliche Bytes
hinzu; die Startprüfung zählt sie verbindlich mit. Der Start benutzt das ZIP
und dessen Abschluss-/Testnachweise. Die unkomprimierten historischen Belege
bleiben erhalten, werden aber nicht nochmals als operative Vorbereitung geladen.
Jede enthaltene Datei wird nach Entpacken gegen Größe und SHA256 des gespeicherten
Prüfabschlusses geprüft; Erweiterung über16MiB wird abgelehnt. Es wird nichts
gelöscht und keine Evidenz durch eine bloße Zusammenfassung ersetzt.

Das statische Exportmaximum einschließlich maximal8MiB Vorbereitung und1MiB
Abschlussreserve beträgt64.749.568 Byte=61,75MiB und liegt unter64MiB.
Es setzt sich aus24×160KiB Quellen,48×512KiB Armergebnissen,24×1MiB
Fallauswertungen und1MiB Verwaltungsdateien zusammen. Dateikappen und die
Gesamtbilanz werden vor jedem regulären Export geprüft. Die Abschlussreserve
bleibt davon getrennt. Keine Grenzerhöhung oder stillschweigende Fallkürzung.

Die neuen Replayläufe nutzen die konservative Originalframe-Bilanz; keine neue
langsame Trace-Messung. Nullwerte der Trace-Felder bedeuten nicht gemessen.
Die ursprüngliche K1-Tracequalifikation bleibt unverändert gültig. Zusatzheap
ist kein Gesamtprozess-RAM. Die neutrale Laufzeit ist keine Vorhersage des
Forschungslaufs; dieser erhält die unveränderten harten Fristen. Der gespeicherte
Abschlusszeitwert endet unmittelbar vor seinem eigenen Schreiben und behauptet
keine exakte Messung der eigenen Schreibdauer. Ein Betriebssystem-/Datenträger-
Totalausfall kann durch diese Software nicht mit einem Schreibnachweis überlebt
werden; die geprüften gewöhnlichen Start-, Worker- und Abbruchfehler sind abgedeckt.

## Bindung, Aufruf und nächste Entscheidung

Vorstartbindung: `docs/S2UC_K1_VERGLEICH_V2_20261004_VORSTARTBINDUNG.json`.
SHA256: `c35c1146ebb6c6884d761a52fb50aa15df39f9d39f821e6b329103a76446f9b9`.
Codebindung SHA256:
`367e70faf40d31861734b4437147648c5282976b0c8e29fc1634957554901b3a`.
Qualifikationsabschluss SHA256:
`29c902aba7cfb3c688754992c1e6d165a91552aa784cc545223bbe992b7d4d30`.

Der ausführbare Befehl und die präzise Autorisierungsgrenze stehen in
`docs/S2UC_K1_VERGLEICH_V2_20261004_AUFRUF.md`. Die operative Autorisierungsdatei
und der Forschungs-Ausgabeordner existieren noch nicht. `check` wurde erfolgreich
ausgeführt; `run` wurde für Forschungsdaten nicht aufgerufen.

Empfehlung an den Projektleiter: Die neutral qualifizierte Hülle abnehmen und
über genau einen begrenzten Vergleich aller24 Vertragsfälle entscheiden. Dieser
soll prüfen, ob zusätzliche nutzbare alte Erfahrung die verworfenen neuen Spuren
insgesamt aufwiegt. Bis zu dieser separaten Einmalbeauftragung bleibt die
Forschungsausführung geschlossen; kein Nachoptimieren der K1-Regel.
