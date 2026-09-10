# S2-OC: Vollständige neutrale Qualifikation mit verlustfreier Belegverpackung

Neue Qualifikations-ID: s2oc-session-qualification-20260910-02.
Genau ein vollständiger Aufruf, keine Übernahme alter Passzahlen. Kein realer
Aufruferlauf, keine historischen Payloads oder Wiederholung einer Geschichte.
Die bisherigen Fehler- und Vorbereitungsbelege bleiben unverändert erhalten.

## Aktuelle Korrekturen und Prüfinventar

Die Materialisierungsphase kann nicht mehr durch alte Runtimephasen überschrieben
werden. Vor dem aktuellen Runtimeaufruf beginnt auch dessen administrative Phase
neu mit EVENT. Memory-/Feldwerte bleiben davon unberührt. Verglichen werden
dieselben kanonischen Ausgabeformen, nicht Python-Tupel gegen JSON-Listen.
Quellen-, Phasen-, Fortschritts- und Erhaltungsassertionen laufen in unabhängigen
Unterkontrollen; die Scanfixture besitzt die gültige ID oc-scan-error.

Alle **29 Prüfgruppen** werden neu ausgeführt. 01–24: identische Eingänge und
Quellen, Zustände, Generationen, kompletter Stapel-/Sitzungsbeleg, unveränderliche
Rückgaben, aktuelle Payloads und wertneutrale Pausen, doppelte/vertauschte/geänderte
Ereignisse, Manifestkopie, CLOSED und Manifestende, Enthaltung, vorzeitiges und
wiederholtes close, Wiedereintritt, Payloadfehler mit erhaltenem Fortschritt,
unabhängige Memory-/Feld-/Scanfehler, Budgets, Manipulationen und Gesamtverifikation.
Keine Änderung der bisherigen fachlichen Assertions oder Memoryregeln.

25: vollständige aktuelle neutrale Sitzung verpacken und bytegenau herstellen.
26: davon unabhängige direkte ZIP-Rekonstruktion einschließlich identischer
Mehrfachdateien, -0.0 und Subnormaldarstellung. 27: fehlenden Inhalt abweisen.
28: falschen Hash und veränderte Belegklasse unabhängig abweisen. 29: übergroße
Entpackdeklaration vor Dekompression abweisen. Nur neutrale administrative Dateien;
keine erneute Verarbeitung gespeicherter Wahrnehmungen.

Unverändert vorgesehen: ein Stapel und zwölf Sitzungen, 16 Runtimeereignisse,
zehn Formationsversuche, **13 Audioanalysen, 13 NJ-Projektionen, 13 visuelle
Analysen** und 13 unabhängige OB-Verifikationen. Zusätzliche Verpackungsarbeit ist
bytebezogen, keine weitere Rezeptor-, Feld-, Memory- oder Scanprüfung.

## Eine Standardverpackung, vollständige Originalbytes

`s2oc.evidence-zip.v3` verwendet ausschließlich zipfile/DEFLATE, feste ZIP-Zeiten
und Kompressionsstufe 9. Kein Recorder, keine Datenbank oder neue Memorytechnik.
Identische Inhalte derselben Belegklasse stehen einmal im ZIP; logische Dateien
behalten eigene Namen, Klasse, ursprüngliche Länge und SHA-256. Der Index bindet
ihre geordnete Zusammensetzung aus ebenfalls längen- und hashgebundenen Inhalten.

Gemischte Runtime-/Sitzungsdateien werden nur an bestehenden JSON-Bytebereichen
in ihre bisherigen Belegklassen zerlegt. Kein JSON-Zahlenwert wird umgeschrieben,
keine Herkunft ersetzt. Der Leser rekonstruiert die originalen Bytes, prüft SHA,
Dateizuordnung, vollständige Bereiche und die normative Klassenzuordnung erneut.
Die direkte neutrale Kontrollrechnung verwendet nur ZIP, Index und Originalbytes.
Die ursprüngliche 77.940-Byte-Metadatenklasse bleibt vollständig erhalten.

ZIP-Dateidaten, lokale Header und zentrale Einträge werden je Inhaltsklasse
gezählt; der gesamte komprimierte Index, dessen Header und ZIP-Abschluss zählen
als Metadaten. Es gibt keine ungezählten Verzeichnisse oder Nebenindizes.
Die numerischen Arrays des Abschlussbelegs verwenden in dieser Reihenfolge:
states, inputs, steps, scans, nj, formations, generations, metadata, sources,
verification, qualification, report. Die Klassen sind nicht frei umschaltbar.

## Gemessene Probe und Vorbindung

Die rein administrative Probe umfasst alle **77 vorhandenen Dateien**, nicht
nur einen kurzen Erfolgslog. 554.595 ursprüngliche Byte werden vollständig
wiederhergestellt; 118.822 Byte sind gespeichert, einschließlich Index und
ZIP-Overhead. 84 Inhaltsblöcke binden getrennte Dateien und geteilte Inhalte.
Alle historischen Originale blieben bytegleich; die Probe ist eine zusätzliche
Kopie und keine rückwirkende Budgetkorrektur. Ihre früheren Darstellungsstufen
sind erhalten, aber keine zusätzlichen Forschungs- oder Qualifikationsläufe.

Gespeichert: Metadaten 42.878, Qualifikationsdateien einschließlich des vollständigen
4.643-Byte-Fehlerlogs 3.319 Byte. Hinzu kommen der neue abschließende Paketbeleg,
die unverändert benötigten OB-Qualifikationsdateien (3.131 Byte), das erforderliche
OB-Codeinventar (10.114 Byte) und die bestehende Berichtreserve (512 Byte).
Die exakte Größe des Paketbelegs wird vor dem Test durch stabile Serialisierung
gebunden; nur wenn auch damit alle Grenzen passen, startet unittest.

Zusätzlich wird vor dem Start die gesamte bisherige neutrale Belegmenge mit
dem aktuellen Quellenmanifest und den aktuellen administrativen Ausgabeformen
als reine Bytehülle verpackt. Der vollständige frühere Fehlerlog bleibt dabei
enthalten. Dieser Beleg heißt ausdrücklich ENVELOPE_SHAPE_ONLY und enthält
keinen neuen Test- oder Runtimebefund. Seine gemessene Bilanz muss ebenfalls
passen; eine passende alte Hülle allein reicht nicht als aktuelle Vorbindung.

Unverändert: Metadaten 65.536, Quellen 174.080, gemeinsame Zusatzhülle 262.144,
Verifikation 262.144, global 4.194.304 Byte. Qualifikationsreserve 4.096 Byte
einschließlich des äußeren Paketbelegs; keine neue Reserve. Für gespeicherte
Laufmetadaten bleiben 57.344, für Quellenbeilagen 65.536 Byte vorgebunden.
Die Entpackgrößen werden separat ausgewiesen; native Einzelgrenzen, insbesondere
98.304 Byte je rekonstruiertem Zustandsbeleg, bleiben unverändert.

Maximal 160 Dateien/Inhaltsblöcke, 65.536 Byte Index, 4.194.304 Byte je
rekonstruierter Datei und 16.777.216 Byte logische Entpackmenge beziehungsweise
Dekompressionsarbeit. Je Dateischritt höchstens 4 MiB Inhaltscache plus 4 MiB
Rekonstruktionspuffer; 10 MiB für diese Nutzbytepuffer einschließlich Index und
Vergleichspuffer gebunden. Keine Aussage über den gesamten Python-Prozess-RSS.
Wiederholte Aliasdateien werden als logische Entpackarbeit mitgezählt.

## Abschluss und aktive Abhängigkeiten

Nach dem einen Test bleiben Logs vollständig. Der Testabschluss und die nativen
Einzelgrößen liegen als logische Dateien im gemeinsamen ZIP. `package.json`
bindet das gesamte ZIP per SHA-256 und berichtet gespeicherte sowie entpackte
Klassengrößen, externe Referenzbytes, Ist-/Reservebedarf und endgültigen Status.
Ein innerer Testpass ohne bestandene Paketbilanz ist keine Gesamtqualifikation.

Nur nach unabhängiger byteweiser Wiederherstellung und passender Bilanz werden
die neuen unkomprimierten Arbeitskopien entfernt, ausschließlich innerhalb der
neuen Qualifikationsablage. Bei Überlauf bleiben sie samt vollständigem Log und
Fehlerbeleg erhalten und werden zusätzlich gezählt. Keine Wiederholung.
Beliebig große künftige Fehlerlogs werden nicht als vorab garantiert passend
behauptet; tatsächlicher Überlauf bedeutet NOT_QUALIFIED, nicht Kürzung.

Der spätere CALLER-Einstieg liest den gepackten Nachweis. Seine vollständige
physische Paketdatei und der äußere Beleg werden als aktive Abhängigkeiten
mitgezählt; innere Metadaten verschwinden dabei nicht aus der Metadatengrenze.
Das Gesamtpaket wird zusätzlich konservativ gegen das Quellenlimit gerechnet.
Damit ist noch nicht jede denkbare kurze Aufruferfolge budgetiert: Deren eigene
vollständige Bilanz bleibt vor einem separat freizugebenden Funktionslauf nötig.
Historisches OB-run_once und dessen Verifikationsregeln bleiben unverändert.
Gates außerhalb neutraler Öffnungen False, ME/MI gesperrt, Prognosezweig ruhend.
