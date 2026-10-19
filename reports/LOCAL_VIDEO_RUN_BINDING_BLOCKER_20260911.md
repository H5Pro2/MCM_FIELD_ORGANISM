# Reale Medienlaufbindung: konkreter Anschlussblocker

Stand: 2026-09-11. Auftrag: konkrete reale Laufbindung, keine Ausführung.
Bezugscommit: `537109994cf777f8d36cda617aafe12226806c25`; Arbeitsbaum mit
vorhandenen Änderungen. Aktiver Mediencode ist separat im Inventar unter
`s2oe/media-oc-qualification-20260911-02/inventory.json` gebunden.
Dies ist ein statischer Vorbereitungsbefund, kein neuer Lauf und keine
startfähige Freigabe. Keine Tests, Projektimporte oder Medienzugriffe erfolgt.

## Festgelegte Eingänge und Ablauf

- Vorgesehene Lauf-ID: `media-memory-video-20260911-01`.
- Ergebnisziel: `reports/s2oe/media-memory-video-20260911-01`; bei dieser
  Vorbereitung nicht vorhanden und nicht angelegt. Vor Start erneut prüfen.
- Quelle: `C:\Users\TV\Downloads\17138816-uhd_3840_2160_30fps.mp4`.
- Größe laut bestehender Quellenbindung: 83.498.438 Byte.
- SHA-256: `df0986f384e156c4dfec234e94b6f6baa3d0f8a9cfd7ba81f14aadf0313450aa`.
  Hier aus `LOCAL_VIDEO_ACCESS_20260911.md` übernommen, nicht neu gemessen.
  Der Decoder muss die Datei vor Verarbeitung erneut vollständig prüfen.
- Ausschnitt `[00:00,00:05)`, zweimal; dieselbe Runtime und Memory erhalten.
- Pro Durchlauf zehn 100-ms-Fenster ab 0; 0,5; ...; 4,5 Sekunden.
  Letzter Videoframe am oder vor dem Mittelpunkt, mit nächstem Frame als
  Auswahlbeleg. Video-PTS/Zeitbasis 1/30000 und 30000/1001 fps bleiben erhalten.
- e01 bis e10: erster Durchlauf; e11/e12: zweite Fenster 0/1;
  e13 Audiohinweis, e14 Visualhinweis, e15 Formation bei 1 s;
  e16 bis e20: Formationen bei 1,5 bis 3,5 s;
  e21 Audiohinweis, e22 Visualhinweis, e23 Formation bei 4 s;
  e24 Formation bei 4,5 s. Technische IDs `media-event-01` bis `media-event-24`.
- Audiohinweis: erste 24 Bänder. Visualhinweis: erste 32 Positionen;
  übrige RGB-Positionen vor der visuellen Analyse okkludiert.
  Hinweise jeweils read-only vor Formation. Kein erwarteter Treffer als Gate.
- Runtimezeit ausschließlich gemäß `runtime_times()` / `expected_times()`;
  kein Rücksprung bei Medienwiederholung. Profil und Regelbindung unverändert
  gemäß `_s2oe_media_binding.py`, nicht aus der Dateinamensendung abgeleitet.
- 20 Formationen, vier Hinweise, 22 Audio-/NJ- und 22 visuelle Analysen,
  7.392 Feldkontakte, acht Scanbelege. Decoderfortschritt separat zählen.

## Tatsächlich vorhandener Zugang

`tools/_s2oe_media_session.py:251`, `start(manifest, common, inv, directory)`
ist der vorhandene Python-Einstieg. Er prüft Gate, Manifest, aktuelle
Code-/Qualifikationsreferenzen, Ausgabeabwesenheit und beide Hüllenalternativen
an allen 25 Fortschrittspositionen. `Session.next()`, `status()` und
`stop()`/`close()` sind der schrittweise Zugang. Kein Browserplayer, keine
Medien-CLI und kein für diese Lauf-ID gebundener autorisierter Starter existieren
in diesem Anschluss. Den historischen OD-Starter nicht ersatzweise verwenden.

Vorgesehene Aufrufordnung, ausdrücklich nicht ausgeführt: einmal autorisiert
öffnen, gebundene Ereignisse einzeln übergeben, Status bei Bedarf, schließen;
anschließend genau einmal `_s2oe_media_verification.verify_once()` (Zeile 74).
Ein äußerer Aufrufer müsste Freigabe und Gate-Rücksetzung konkret binden.
Die technische Verifikation ersetzt keine fachliche Auswertung; ein fertiger
clipbezogener Auswerter ist hier nicht gebunden. Nur gespeicherte Scans und
Transaktionen dürfen später deskriptiv ausgewertet werden.

## Blocker: native Decoderbelegung nicht begrenzt

Konkrete Grenze: `tools/_s2oe_media_decoder.py:90` ruft `packet.decode()` auf,
bevor die Ergebnisframes gezählt und geprüft werden. Die native Dekodierung
und ihre Rückgabeliste sind zu diesem Zeitpunkt bereits erzeugt.

- Zeile 89 begrenzt Pakete auf 2.048 und einzelne komprimierte Pakete auf
  4.194.304 Byte, nicht den dekomprimierten Speicherbedarf.
- Zeile 125 setzt einen Videothread; das ist keine native Speicherquote.
- Zeile 162 prüft Frameabmessungen erst nach der Dekodierung.
- Zeilen 177 bis 180 prüfen Audioform und Blocklänge erst nach Dekodierung.
- `CountedFile.read()` begrenzt Leseanforderungen und kumulierte Dateibytes;
  das begrenzt weder Referenzframes noch Demux-/Codec-/Konversionspuffer.
- Der Decoder läuft im selben Prozess wie die Sitzung. Der Startpfad richtet
  keine Speicherquote oder isolierte, speicherbegrenzte Decoderinstanz ein.

**Es gibt in diesem Aufrufpfad keine wirksam durchgesetzte numerische
Obergrenze für den gesamten FFmpeg-Arbeitsspeicher.** Die begrenzte Anzahl
gehaltener Python-Auswahlpuffer ist kein Ersatz. Ein RGB-Auswahlarray allein
enthält 6.220.800 Byte; zusätzlich bestehen native Frames, Konversions- und
Rezeptortemporäre. Dies ist keine gemessene Gesamt-RAM-Belegung.

Kleinster notwendiger Anschluss: eine explizite, wirksam durchgesetzte Grenze
um die native Decoderverarbeitung, mit begrenzter Ausgabeübergabe und
typisiertem Ressourcenfehler an die Sitzung. Bei einer Prozessgrenze müssen
Beendigung und Primärfehler ohne zweite Veröffentlichung erhalten bleiben.
Die konkrete Durchsetzung und ihr Grenzwert fehlen; hier nicht implementiert
und keine beliebige RAM-Zahl als Garantie eingesetzt. Memorylimits bleiben
unverändert. Dieser Implementierungsblocker verhindert die Startbereitschaft.

## Artefakte: vorhandene Grenzen, noch keine finale Laufbilanz

Bestehende Sitzungsgrenzen: Metadaten 65.536, Quellen 180.224, gemeinsame
Zusatzhülle 262.144, Verifikation 262.144, Gesamt 4.194.304 Byte.
Die größere Qualifikationsmetadatengrenze gilt nicht für den Medienlauf.

Vorhandene Reserven in `reports/prepare_direct_media_budget.py:26`:
Quellen-/Auswahlbindung 4.096; Qualifikation/Bericht 8.704;
24 Auswahlbelege 12.288; Decoderzähler/Abschluss 2.048;
Auswertung 3.000; Aufrufabschluss 768; Istbilanz 1.536; gemeinsame Referenz 512.
Erfolg und Fehler sind Alternativen, physisch doppelte Inhalte weiterhin
mehrfach zu zählen. Native Zustände, Eingänge, Schritte, Scans, NJ-,
Formations- und Generationsbelege bleiben vollständig enthalten.

Der bisherige generische Vorbeleg nennt 178.006 Byte Quellen und 261.974 Byte
gemeinsame Zusatzhülle: nur 170 Byte gemeinsamer Abstand. Seine maximalen
63.622 Byte Sitzungsmetadaten und 3.700.097 Byte Gesamt sind **keine neue
Istbilanz dieser Laufbindung**. Neuer Starter, Ressourcenbegrenzung,
erneuerte Code-/Qualifikationsbindungen und deren Abschlussdiagnostik sind
noch nicht enthalten. Deshalb wird kein fertig passendes Gesamtbudget
behauptet und kein `common.json` als startbereite Zulassung veröffentlicht.
Auch dieses Dokument muss bei späterer notwendiger Referenzierung mitgezählt
werden; es ist jetzt Arbeitsdokumentation außerhalb einer Laufablage.

## Abschluss

Quelle und unveränderte Aufgabe sind konkret festgehalten. Die fehlende
native Speicherbegrenzung ist ein belegter Implementierungsblocker, nicht
erneut die Frage nach Erlaubnis zur Vorbereitung. Nach dessen Klärung sind
Startdatei, aktive Referenzen und sämtliche Erfolgs-/Fehlerformen gemeinsam
neu zu bilanzieren. Kein Lernlauf, keine Tests, kein Gate geöffnet; historische
Belege unverändert. Keine Aussage über Wiedererkennung oder Stabilisierung.

**RÜCKMELDUNG ERFORDERLICH:** Entscheidung über den eng begrenzten
Decoder-Ressourcenanschluss; der reale Lauf bleibt gesperrt.
