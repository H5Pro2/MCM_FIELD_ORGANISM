# Erfahrener gegenüber frischem Arm

| Kontrolle im zweiten Durchlauf | Erfahren | Frisch | Vorgebundene Zielherkunft | Vergleich |
|---|---|---|---|---|
| Audio, 1,0 s (e13) | Mehrdeutig; 11 Kandidaten | Mehrdeutig; 3 Kandidaten | Erfahren: 2 gemischt, 9 andere; frisch: 3 andere | Kein Abrufgewinn, kein Abrufverlust |
| Video, 1,0 s (e14) | Kein anwendbarer Kandidat | Kein anwendbarer Kandidat | In beiden Armen kein passender Kandidat | Kein Unterschied |
| Audio, 4,0 s (e21) | Mehrdeutig; 11 Kandidaten | Mehrdeutig; 10 Kandidaten | Erfahren: 2 gemischt, 9 andere; frisch: 10 andere | Kein Abrufgewinn, kein Abrufverlust |
| Video, 4,0 s (e22) | Kein anwendbarer Kandidat | Kein anwendbarer Kandidat | In beiden Armen kein passender Kandidat | Kein Unterschied |

**Kein konkreter Abrufvorteil durch die frühere Betrachtung nachgewiesen.**
Alle acht Entscheidungen enthalten sich; keine Hypothese und keine Anwendung.
Die öffentliche Entscheidung ist an allen vier Stellen gleich. Die Kandidaten-
mengen sind es bei Audio nicht. Zusätzliche Spuren sind hier kein Abrufnutzen.

## Technischer Abschluss

`experience-comparison-real-20260919-01` genau einmal ausgeführt, 38,068 Sekunden.
`RECORDING_COMPLETE`; genau eine unabhängige read-only Verifikation,
`evaluation_allowed=True`; anschließend genau eine getrennte Auswertung.
Kein äußerer zweiter Verifikations-/Auswertungsaufruf, kein Retry oder Eingriff.
Die ausgelesenen Ergebnisse stammen aus den gespeicherten Dateien, nicht aus
einer erneuten Memory-/Scanberechnung.

| Tatsächlicher Umfang | Erfahren | Frisch | Gemeinsam |
|---|---:|---:|---:|
| Ereignisse | 24 | 14 | 38 |
| Formationen | 20 | 10 | 30 |
| Read-only-Hinweise | 4 | 4 | 8 |
| Feldkontakte | 7.392 | 4.032 | 11.424 |
| Scans einschließlich Direktbaseline | 8 | 8 | 16 |

22 Audioanalysen, 22 NJ-Projektionen, 22 visuelle Analysen; gemeinsame aktuelle
Materialisate. Die vorherige Betrachtung wurde nicht in den frischen Zustand
übernommen. Kein Abschnittsreset und keine Hypothesenanwendung.
Beide gespeicherten Endzustände sind CLOSED. Der Decoder wurde im qualifizierten
finally-Pfad geschlossen; anschließend kein laufender Decoderworker gefunden.
`dispatch.json` dokumentiert alle beteiligten Gates als False und keinen Fehler.

## Herkunft und Grenze

An beiden Audiokontrollen enthalten die Treffer des erfahrenen Arms neun B4-
Spuren sowie Fast-Slot 000 und auditiven Slow-Slot 000. Die beiden letzteren
haben gemischte, transaktionsgebundene Herkunft einschließlich des jeweils
vorgebundenen Zielfensters. Fast: Support 2; Slow: Support 3. An e13 sind
12 beziehungsweise elf Aktualisierungseinträge belegt, an e21 18 beziehungsweise
17. Gesättigter Support bedeutet daher nicht, dass Aktualisierung ausgeblieben
wäre. Weder Support noch bloße Zielbeteiligung begründen einen richtigen Abruf.

Frisch trifft e13 zwei B4-Spuren und einen Fast-Slot; e21 acht B4-Spuren,
einen Fast- und einen auditiven Slow-Slot. Ihre bis dahin verarbeiteten Fenster
gehören nicht zur jeweils vorgebundenen Zielposition. Es wird keine semantische
Falschheit dieser Klangähnlichkeiten behauptet. Eine gemischte Spur ist ebenso
wenig automatisch eine erkannte Objektidentität oder ein reiner Zielabruf.

Gewinne 0, Verluste 0, ausgegebene Nichtzielhypothesen 0. Das ist kein Nachweis
allgemeiner Erhaltung: In diesem Vergleich gab es keinen richtigen öffentlichen
Abruf, dessen Erhaltung demonstriert werden könnte. Zusätzliche Konkurrenz
erzeugt hier auch keinen neuen öffentlichen Verlust, da schon der frische Arm
an beiden Audiostellen mehrdeutig war.

Original-PTS und 30000/1001 fps bleiben gebunden. Lokale frische Ereignisnummern
1..14 gehören zu globalen Zeitpositionen 11..24. Die explizite leere Vorlaufzeit
im ersten frischen Feldintervall bleibt Teil der freigegebenen Zeitbindung;
keine Alt-/Neu-Feldgleichheit behauptet. Memoryalter basiert weiterhin auf den
tatsächlich erfahrenen Formationen, nicht auf künstlicher Verjüngung.

## Quelle und Ressourcen

Wiederverwendete, bereits untersuchte lokale MP4:
`C:/Users/TV/Downloads/17138816-uhd_3840_2160_30fps.mp4`, 83.498.438 Byte,
SHA-256 `df0986f384e156c4dfec234e94b6f6baa3d0f8a9cfd7ba81f14aadf0313450aa`.
Keine neue unabhängige Quelle und keine behauptete Identität mit der früheren
YouTube-Auswahl. Zwei abgetastete Durchläufe von [0,5) Sekunden; keine
vollständige Verarbeitung aller dekodierten Bilder und Audiosamples.

Decoder: 20 ausgewählte Fenster, zwei Durchläufe, 716 Pakete, 276 Videoframes,
432 Audioframes beziehungsweise 442.368 Audiosamples. Tatsächlich gezählte
Containerlesemenge einschließlich interner Hashlesungen: **401.434.996 Byte**
gegenüber gebunden maximal 1.001.981.256 Byte. Kein weiterer äußerer MP4-Hashlauf.
Gespeicherte Peakwerte: Job 605.782.016, Prozess 599.216.128 Byte, jeweils unter
1.073.741.824; keine Speicherlimitmeldung. Diese Decoderwerte sind nicht der
RAM-Verbrauch des gesamten Entwicklungsprozesses.

Belegdateien vor Bericht/Bilanz: record.json 2.034.144 Byte, verification.json
22.832, evaluation.json 35.602, Bindungskopie 7.350, dispatch.json 289 und
Verifikationsclaim 4 Byte. Die gemeinsame Istbilanz zählt auch Qualifikation,
Vorbindung, Autorisierung, aktive neue Quellen und Abschluss mit. Die
vorab reservierte gemeinsame Spitze bleibt 20.619.300 / 25.165.824 Byte;
eine tatsächlich gemessene temporäre Dateispitze wird nicht behauptet.

## Unveränderte Bindungen

Repository-Bezug `537109994cf777f8d36cda617aafe12226806c25` plus qualifiziertes
Arbeitsbauminventar. Vor Start waren Ausgabe abwesend, aktuelles Inventar und
Qualifikationsdateien passend. Die neue ausdrückliche Chatfreigabe ist separat
als authorization.json gebunden; das historische authorized=False der
Vorbereitungsdatei wurde nicht überschrieben.

- Freigegebene Bindungsdatei: `d1d7e195e65b184f55f03b46ad483171f3abd5a17e2723844182a423e868a7e3`
- Gesamtbeleg: `8587d6d5ac9e5995f66da0246212f33fa98450be4e78caf4485e57c061ba1d78`
- Verifikation: `8b96d22cf3cc6252f5a128c8ed94d86476828aa692131ccf9beb01ad87ccffe3`
- Auswertung: `48229e5399093926c43db6c15eba9c581e922b9959aa27289686107498e14b50`

Lauf-ID verbraucht. Keine Regel-, Masken-, Quellen- oder Schwellenanpassung.
Historische Befunde unverändert. Nächste fachliche Entscheidung beim Analysten;
kein automatischer Anschlussversuch und keine Optimierung aus diesen Ergebnissen.
