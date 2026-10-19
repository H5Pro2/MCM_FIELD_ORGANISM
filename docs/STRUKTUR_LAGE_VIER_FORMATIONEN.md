# Getrennter Systemversuch: vier Formationen

Nur statische Vorbereitung. Der abgeschlossene direkte Dreiervergleich und
der Videobefund bleiben unverändert. Keine neue Lauf-ID verbraucht.

## Feste Eingänge und Folge

Eine regulär leere private Halbprofil-Memory mit unveränderter Fast-/PPB-
Mechanik; vorhandener OB/OC-Aufruferpfad, historische Defaults unverändert.
Keine direkte PPB-Ansteuerung und keine Slotvorbelegung.

Audio für alle vier Formationen: vorhandene Datei
`sources/s2ob/caller-av-basic/window.pcm`, 19.200 Byte, 4.800 Float32-
Samples bei 48 kHz. Historisch gebundener SHA-256:
`f1080644e18dac7583d73cd300f9b0dda45ad123c96ba66f4740a5a17a1e6df4`.
Herkunft `reports/s2ob/caller-input-binding/binding.json`; jetzt kein
Payloadzugriff oder erneutes Hashen. Später vor jedem Zugriff Hashprüfung,
je Formation eigene Quellenidentität und eigene Analyse/NJ-Projektion.
Keine Audioauswahl anhand neuer Messungen.

Visuell unveränderte RGB8-Rezepte q04, q05, q06 aus
`structure-location-source-seal-20260912-01`, 1920×1080. Die zweite q04
ist eine ausdrücklich gezählte Wiederholung, keine neue Lagevariante.

| ID | Eingang | Audio-Samplefenster / Index | Video-Ticks |
| --- | --- | --- | --- |
| structure-av-01 | q04 + festes Audio | [0,4800) / 0 | [2,3) |
| structure-av-02 | q04 + festes Audio | [9600,14400) / 20 | [8,9) |
| structure-av-03 | q05 + festes Audio | [19200,24000) / 40 | [14,15) |
| structure-av-04 | q06 + festes Audio | [28800,33600) / 60 | [20,21) |
| structure-vc-05 | okkludiertes q06 | keines | [26,27) |

Zeiten genau nach `tools/_s2ob_private_caller_binding.py::expected_times`:
Audiozeitbasis 48.000, visuell 30; g=Ordinal−1. Gemeinsame Audiofenster
[200.000.000g,200.000.000g+100.000.000) ns; visuelle Fenster beginnen bei
floor((6g+2)×10^9/30) ns und enden gleichzeitig. Feldfenster beginnt beim
ersten Ereignis bei 0, danach bei 200.000.000g−100.000.000 ns.
Historische q-Quellenindizes bleiben Herkunft; neue Präsentationszeiten
werden separat gebunden, nicht rückwirkend als historische Zeiten ausgegeben.

Hinweis: bestehende visuelle Sicht Originalkomponenten 0..31; Komponenten
32..287 verdeckt. RGB-Eingang vor Analyse komponentenweise okkludieren:
nur zu den ersten 32 Grid-/RGB-Komponenten gehörende Zellkanäle aus q06
erhalten, übrige Kanäle schwarz. Keine verdeckten Cuewerte weitergeben.
Das ist ein neues abgeleitetes, noch nicht erzeugtes Cuepayload, nicht q06
mit nachträglich umetikettiertem Hash. Read-only, keine Hypothesenanwendung.

## Statische Erreichbarkeit

`_tspm1_private.py:1458,1488–1531`: erste q04 erstellt Fast mit Support 1,
ohne Konsolidierung. Identische zweite AV-Präsentation soll Fast treffen,
Support 2 erreichen und damit die erste PPB-Erfahrung auslösen.
Die bereits belegten visuellen q04/q05- und q04/q06-Abstände liegen deutlich
unter Fast 0,2. Konvexe Fast-Fortschreibung mit Faktor 0,5 liefert auch für
q06 keine Nähe zur Fast-Grenze; konstantes Audio liefert keine konkurrierende
Audioänderung. Dies ist eine statische Prognose, keine erneute Rechnung
oder Bestätigung der realen zeitgebundenen Rezeptorkette.

Entscheidend: `_tspm1_private.py:2538–2548` übergibt bei Konsolidierung
`exposure.visual.timed_frame.frame` an PPB, nicht `selected.visual_values`
des aktualisierten Fast-Prototyps. Damit können die PPB-Eingänge tatsächlich
q04, q05, q06 sein. Nachgewiesen werden muss dies später durch tatsächliche
Kontaktwerte und Transaktionsbindungen, nicht allein durch Quellenlabels.

## Getrennte Prüfziele

1. Vier reguläre Formationen; Fast-Support 1/2/2/2, Konsolidierungen 0/1/2/3.
2. Visuelle PPB-Eingänge q04/q05/q06; Support 1/2/3, Generation erhalten.
3. Prototypwerte gegen die bereits gespeicherte direkte Kette vergleichen,
   ohne Zeit-/Zustandsdigests verschiedener Präsentationen gleichzusetzen.
4. Abschließenden Scan, interne A-Auflösung, B-Anwendbarkeit und öffentliche
   Entscheidung getrennt erfassen. Keine eindeutige Hypothese voraussetzen:
   die ersten 32 Komponenten liegen außerhalb der gebundenen Vordergrundlagen;
   passende A-Kandidaten können verschiedene vollständige Inhalte tragen.
   Stabilität allein begründet keine eindeutige öffentliche Zuordnung.

## Minimale noch offene Anschlüsse

Der OB-Pfad erwartet Aufruferdateien, die Strukturquellen liegen als Rezepte
und gespeicherte Rezeptorbelege vor. Vor einem Lauf sind die drei RGB-Dateien
rezeptgetreu bereitzustellen, gegen vorhandene Payloadbindungen zu prüfen und
die separate Cueableitung zu binden. Keine Generatoraufrufe im Runtimepfad.
Manifest, technische Quellenzulassung, neue Zeitbindungen und unabhängiger
Prototyp-/Generationsvergleich benötigen eine konkrete Anschlussbindung.
Historische OA-/OB-Zulassung ist keine automatische Freigabe dieser Dateien.

Endlicher geplanter Umfang: fünf Ereignisse, vier Formationen, ein visueller
Hinweis; vier Audioanalysen/NJ-Projektionen, fünf visuelle Analysen,
1.632 Feldkontakte und zwei Scanbelege einschließlich Direktbaseline.
Wiederholte Payloads werden nicht als neue Erfahrung dedupliziert.
Operationsumfang liegt unter dem bestehenden OB-Sieben-Ereignisversuch.
Das ersetzt keine Bytebilanz: tatsächliches Manifest, Quellen-/Codeinventar,
Cuebeleg, Zustände, Verifikation und Abschlussalternativen müssen vor
Qualifikation vollständig innerhalb der unveränderten Grenzen gebunden sein.
Noch kein vollständiger Byteobergrenzennachweis oder ausführbarer Hauptlauf.
