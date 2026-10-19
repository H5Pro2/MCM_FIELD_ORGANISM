# Private visuelle Diagnoseanbindung

Prospektive Anschlussversion s2oe.visual-consistency.v1. Kein realer Lauf.
Historischer Medienlauf und dessen Inventar bleiben unverändert.

## Gemeinsamer Code

Der bisherige Videoabschnitt von Decoder.select steht jetzt in
Decoder._select_video. Der AV-Pfad ruft ihn vor _select_audio auf.
VideoDecoder verwendet dieselbe Methode und denselben _frames-Decoder,
CountedFile sowie PyAV-Konverter. Kein kopierter Auswahlalgorithmus.
Nur diagnostisch wird der ausgewählte native Frame bis zur Plane-Bindung
gehalten. Native yuv420p-Planes werden zeilenweise ohne Padding gehasht;
andere Formate scheitern typisiert, ohne Ersatzkonvertierung.

Der bestehende Worker erhält einen geschlossenen video_point-Befehl.
VideoWorker verwendet denselben Prozess-/Jobanschluss mit COMMIT_1024,
einem Slot und einer Anfrage. Sein Kind startet worker_main(VideoDecoder).
Es gibt keinen Audio-Decode-Aufruf; der PCM-Bereich des Transports bleibt
ungenutzt und wird weder als Wahrnehmung gelesen noch analysiert.
Die historischen Defaultlimits bleiben unverändert. Geänderte Decoder-/
Workerhashes benötigen eine neue Profilbindung; alte Qualifikationen werden
nicht als Nachweis dieses neuen Codes ausgegeben. Alte Einmalläufe bleiben zu.

## Konkrete spätere Ausführung

Quelle: C:\Users\TV\Downloads\17138816-uhd_3840_2160_30fps.mp4,
83.498.438 Byte; SHA-256
df0986f384e156c4dfec234e94b6f6baa3d0f8a9cfd7ba81f14aadf0313450aa.
Zeitbasis 1/30000; 30000/1001 fps; 3840x2160. RGB-Ausgang 1920x1080.

Feste Reihenfolge: Punkt 1,0 s Referenz, Punkt 1,0 s Wiederholung,
Punkt 4,0 s Referenz, Punkt 4,0 s Wiederholung. Vier frische Worker,
jeweils ab Anfang und vor dem nächsten geschlossen. Dies präzisiert die
frühere Zwei-Öffnungen-Skizze: zwei unabhängige Dekodierungen je Prüfpunkt.
window=2: Zentrum 21/20 s, historische PTS 31031, Folge-PTS 32032.
window=8: Zentrum 81/20 s, historische PTS 121121, Folge-PTS 122122.
Gültige abweichende Auswahl bleibt ein Diagnoseergebnis; kein Erzwingen
der historischen PTS. Zeiten und Vergleichsbedingungen bleiben sichtbar.

Aufrufanschluss: uhd.bind(source, neue_id), danach open_video nur bei
separater Freigabe; video_point(window), release und close. Keine Wiederholung.
Vollbild und bestehende Okklusion jeweils einmal an LocalChannelGridReceptor
mit VisualGridConfig. Diagnostischer frame_index=0 bei jeder unabhängigen
Analyse, ausdrücklich keine native 30-fps-Medienzeit. Native PTS separat.
Vollständige 288 Binary64-Hexwerte je Analyse; keine Rohbildablage.

## Endliche Bilanz und Qualifikation

Vier native Auswahlbelege, acht spätere Analysen, 2.304 Werte;
576 vollständige und 128 sichtbare Wertevergleiche. Höchstens 400 dekodierte
Videoframes insgesamt, 2.048 Pakete je Worker, insgesamt höchstens 8.192.
Je Worker bestehende Leseschranke 12*Quellgröße, vier Worker nacheinander.
Kein Audio, NJ, Memory oder Feld. Ein Slot, höchstens zwei RGB-Puffer,
ein ausgewählter nativer Frame plus bestehender Lookahead.
1.073.741.824 Byte Prozess-/Joblimit, Anfrage 30 s, Stopp 5 s unverändert.

Gemeinsame Vorbindung: Quellen höchstens 327.680, Metadaten 131.072,
Zusatzhülle 393.216, Gesamt 4.194.304 Byte. Lokal fest reserviert:
16.384 Bindung/Bericht inklusive Vorregistrierung und Abschluss,
32.768 vollständiges Qualifikationslog, 8.192 Ergebnis,
57.344 numerische Tabellen. Summe 114.688 plus vollständig gezählte Quellen.
Kein Rohpayloadarchiv. Größere Fehlerlogs bleiben erhalten und werden als
Budgetfehler gemeldet. Diese Obergrenze ersetzt keine spätere Lauf-Istbilanz.

Zwölf neutrale Prüfgruppen: beide Zeiten, gemeinsamer Code, Zustandsisolation,
Konvertierungsargumente, falsche Zeitbasis, fehlender Frame, Maskierung ohne
Mutation, Gleichheit/Abweichung, ungültige Werte, Gate/UHD-Profilübergabe,
native Plane-Paddingbindung und geschlossener/falscher Punkt.
Keine ausgewählte MP4, PyAV-Dekodierung oder echte Rezeptoranalyse im Test.
Der OS-Prozessanschluss wird hier nicht erneut nativ getestet; seine
bestehende Jobmechanik bleibt bestehen. Diese Grenze offen ausweisen.

Noch keine reale Versuch-ID verbraucht oder Gatefreigabe. Vor einem realen
Aufruf sind aktuelle Code-/Profilhashes und diese Qualifikation zu binden.
Gleichheit und Abweichung sind zulässige Ergebnisse, keine Schwellenableitung.
