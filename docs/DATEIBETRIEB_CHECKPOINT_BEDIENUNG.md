# Dateibetrieb mit geordnetem Checkpoint

## Konkreter Vorabkonflikt: später Voll-Datei-Stopp

Die weitergehende Prüfung am 2026-09-13 ergibt einen konkreten Konflikt für
den bestehenden Voll-Dateimodus mit Wiedereinstieg ab Dateianfang. Dies ist
eine statische Gegenrechnung an einer regulären CFR-Zeitfolge, kein neuer
Decoderlauf und kein nachträglich behaupteter Messwert der realen Datei.

Gebundene Voraussetzungen: 20 Auswahlstellen, Abstand 7/5 Sekunden und
Mittelpunktzugabe 1/20 Sekunde; 30000/1001 fps, Zeitbasis 1/30000. Für eine
zulässige regelmäßige Folge mit PTS(k)=1001*k und Beginn bei null muss
`_select_video` auch den ersten Frame NACH dem Mittelpunkt lesen. Die Anzahl
ausgegebener Decoderframes bis Mittelpunkt t ist damit mindestens
`floor(t*30000/1001)+2`. Zusätzlicher Codecaufwand kann diese Schranke nicht
verkleinern. Die Gegenfolge benötigt keine besonderen Bildinhalte.

| Voll-Datei-Position | Mittelpunkt | Notwendige Videoframes ab Anfang |
| --- | ---: | ---: |
| Ereignis 7, Fensterindex 6 | 8,45 s | floor(253500/1001)+2 = 255 |
| Ereignis 19, Fensterindex 18 | 25,25 s | floor(757500/1001)+2 = 758 |
| Ereignis 20, Fensterindex 19 | 26,65 s | floor(799500/1001)+2 = 800 |

Suspend nach Ereignis 7 und vollständiger Restore ab Anfang erfordern daher
bereits **255 + 800 = 1.055 Videoframes**, gegenüber der unveränderten
kumulativen Grenze **1.024**: mindestens **31 Frames Überschreitung**, noch
OHNE abschließendes EOF-Drain. Bei einer vorgebundenen 801-Frame-CFR-Datei
wären es einschließlich Drain 1.056, also 32 mehr. Nach Ereignis 19 sind es
mindestens **758 + 800 = 1.558**, also 534 mehr ohne Drain.

Das ist eine tatsächlich zulässige Zeitform des vorhandenen Profils, keine
Garantie identischer Abstände allein aus `average_rate` und keine neue
Analyse der realen Datei. Es widerlegt die allgemeine Vorabsicherung aller
Ereignisgrenzen mit dem vorgeschlagenen Anfangs-Replay unter diesem Deckel.
Es beweist NICHT, dass ein früher Schnitt oder der kürzere Zwei-Pass-Modus
unmöglich wäre. Solche Fälle dürfen aber nicht unbemerkt anstelle des
geforderten fortsetzbaren Dateibetriebs qualifiziert werden.

Codebezug: Auswahl `tools/_s2oe_media_binding.py:163`; Reihenfolge
`:76`; Video-Lookahead `tools/_s2oe_media_decoder.py:163`; kumulative
Framegrenze `:101`; Voll-Dateiprofil `tools/_s2oe_full_file.py:10`;
EOF-Anforderung `tools/_s2oe_media_session.py:226` und Ressourcenprüfung
`tools/_s2oe_media_verification.py:52`. Der Start eines neuen Workers darf
die bereits gezählten 255 beziehungsweise 758 Frames nicht löschen.

### Konsequenz für die freigegebene Umsetzung

Kein Testaufruf, keine Medien-/Rezeptorverarbeitung, kein geänderter
Produktcode. Der geplante universelle Anfangs-Replay-Anschluss ist an dieser
konkreten Grenze vorab gestoppt. Bytebilanz und weitere Ressourcen würden
diesen Operationskonflikt nicht beheben. Keine neue Grenzerhöhung.

Kleinste Korrekturrichtung ohne Erhöhung: Fortsetzbarkeit nur für vorab
budgetgedeckte Schnittstellen anbieten und einen späteren Speicherstopp
nicht als vollständig fortsetzbar zusagen. Alternativ wäre ein belegter
Decoderwiedereinstieg an einem früheren geeigneten Zugriffspunkt statt
Dateianfang nötig, einschließlich Audio-Vorlauf und identischer Frameauswahl;
diese zusätzliche Decoderfähigkeit ist bislang nicht vorhanden/qualifiziert.
Keine dieser Varianten wurde stillschweigend als neue Bediensemantik
implementiert. Für eine Fortführung ist konkret zwischen begrenzter
Suspendposition und weitergehendem Decoderwiedereinstieg zu entscheiden.

## Anschlussprüfung nach Implementierungsfreigabe

2026-09-13: Implementierung und einmalige neutrale Qualifikation sind nun
freigegeben, jedoch nur nach vollständiger Erfolgs-/Fehlerbilanz. Diese
Vorbedingung ist noch nicht erfüllt. Null Testaufrufe, keine Medienöffnung,
keine Produktänderung und keine neue Laufbindung. Die folgenden konkreten
Restanschlüsse wurden am vorhandenen Code zusätzlich festgestellt:

1. `tools/_memory_checkpoint.py:419`, `validate_accounting`, verlangt exakt
   die Summe der PCM/RGB-Dateigrößen des Präfixes; `read_operations` ist dort
   Audio plus Visual. `tools/_s2oe_media_session.py:82`, `read_account`,
   liefert dagegen Containerbytes und Paketanzahl. Diese Formen sind nicht
   austauschbar. Ein Medienkonto benötigt eine eigene versionierte Prüfung,
   ohne den historischen Dateikontenvalidator zu lockern.
2. `tools/_s2oe_media_decoder.py:87` initialisiert alle Konten mit null.
   `CountedFile.read` (:44) zählt gelesene Bytes vor der Abweisung;
   `_frames` (:92) prüft Pakete/Frames vor weiterer Ausgabe. Die verbleibenden
   kumulativen Grenzen müssen bereits im neuen Worker vor Hashlesen/Demux
   wirksam sein, nicht erst beim Zurücksenden seiner Antwort. Wiedereinstieg
   und reguläre Arbeit separat aufzeichnen, aber gemeinsam begrenzen.
3. Aktuelle Decoderdeckel: Containerbytes 12 × Dateigröße; im Zwei-Pass-Modus
   2.048 Pakete, 400 Videoframes, 600 Audioframes; im Voll-Dateimodus 4.096,
   1.024 und 2.048 (`_s2oe_media_decoder.py:32,96,101`). Ein ununterbrochener
   Lauf darf diese Deckel bereits ausschöpfen. Dieselben Deckel zusätzlich
   dem Wiedereinstieg zuzugestehen wäre eine Grenzerhöhung. Aus den Deckeln
   allein folgt deshalb keine positive garantierte Wiedereinstiegsreserve.
   Das ist kein Nachweis, dass ein konkreter kurzer neutraler Bestand nicht
   passt; für diesen fehlen noch eine gebundene Dateiform, Schnittposition
   und getrennte konservative Arbeitsobergrenzen. Keine realen Messungen
   wurden zur Auswahl eines günstigen Bestands verwendet.
4. Die Artefaktprofile sind nicht identisch: Medien-v6 bindet in
   `_s2oe_media_binding.py:13` Metadaten 131.072, Quellen 327.680,
   Zusatzhülle 393.216 Byte (Gesamt aus OB); der allgemeine Checkpointledger
   bindet in `_memory_checkpoint_ledger.py:5` 65.536 / 174.080 / 262.144
   und 4.194.304 Byte gesamt. Der abgeschlossene Prozessvergleich verwendet
   wiederum seine eigene private v3-Bindung. Keine dieser Ausnahmen wird
   automatisch auf den Mediencheckpoint übertragen. Eine gemeinsame
   physische Liste samt Checkpoint, Präfix, Restabschluss, temporärer
   Publikation, Referenzen, Tests und Logs liegt noch nicht vor. Daher wird
   weder Budgetkonformität noch eine konkrete Byteüberschreitung behauptet.
5. Der neue Stopp muss im Player zuerst nur weitere Ereignisstarts sperren.
   Der vorhandene `Session.stop` darf dabei nicht aufgerufen werden: Er
   cancelt einen aktiven Decoder. Nach abgeschlossenem Schritt unter derselben
   Verarbeitungssperre exportieren, veröffentlichen und gespeicherten Inhalt
   prüfen; erst dann Speichererfolg anzeigen. Bei Fehlern keine spätere
   INCOMPLETE-Meldung anstelle des Primärfehlers. Am Manifestende normaler
   Abschluss, nicht künstlich ein fortsetzbarer Checkpoint.

Zusammenhängender noch ausstehender Implementierungsumfang: versionierte
Medienkonto-/Manifestprüfung um die unveränderte native Rekonstruktion;
Restoreposition und Restlimits im Workerprotokoll; durchgängiger
Suspend-Abschluss im vorhandenen Player; eine gemeinsame phasenbezogene
Artefaktliste. Aktive Decoder-/Profilhashes müssen danach ausdrücklich neu
gebunden werden. Eine nur administrativ erfolgreiche Testfixture würde diese
Grenzen nicht qualifizieren.

Die einmalige Qualifikation ist **nicht verbraucht**. Sie darf erst nach
Fertigstellung dieser Anschlüsse und vollständiger tragfähiger Vorbilanz
starten; der reale Videolauf bleibt gesperrt. Keine zusätzliche Vertragsserie
ist vorgeschlagen. Dieser Nachtrag behauptet keinen fertigen Anschlussnachweis.

Stand: 2026-09-13. Auftrag: DATEIBETRIEB-CHECKPOINT-BEDIENUNG.
Statische Anschlussplanung auf Commit 537109994cf777f8d36cda617aafe12226806c25
mit vorhandenen lokalen Änderungen. Keine neue Ausführung oder Implementierung.

## Bestätigter Ausgangspunkt

`memory-restart-transfer-20260912-01`: sieben Ereignisse je Arm, Checkpoint
nach vier Formationen, tatsächliches Prozessende, frischer Restoreprozess.
Einmalige Gesamtverifikation RECORDING_COMPLETE und getrennte Auswertung
CONFIRMED. Feld, Memory einschließlich Prototypen, Generationen, Snapshots
und Konten stimmen an allen sieben Positionen überein. Beide Hinweise enden
gleich mit ABSTAIN_INTERNAL_AMBIGUITY. Das ist Fortsetzungsgleichheit, kein
eindeutiger Zielabruf. Quellen wurden wiederverwendet. Feldvergleich anhand
vollständiger Snapshotdigests, keine erneute Feldsimulation; kein allgemeiner
Absturzwiederherstellungsnachweis. Ergebnisdateien bleiben unverändert.

## Vorhandene Anschlüsse und Lücken

| Anschluss | Vorhandener Code | Kleinste fehlende Verbindung |
|---|---|---|
| Leerer Start | `tools/_s2oe_media_session.py:41`, `NativeRuntime`; `:314`, `start` erzeugen frische Zustände und Materialisierer. | Explizite Startart leer oder ausgewählter Checkpoint vor Instanziierung binden. Kein stiller Fallback auf leer. |
| Checkpoint | `tools/_memory_checkpoint.py:179`, `export`; `:202`, `validate`: Feld, Memory, Präfix, Generationen, Konten und Code-/Manifestbindung. | Validator ist an OB-Manifest und PCM/RGB-Dateibelege gebunden, nicht an Medienmanifest. Versionierten Medienanschluss ergänzen, historische Akzeptanz nicht lockern. |
| Wiederladen | `tools/_memory_checkpoint.py:311`, `NeutralCheckpointSessionV1`: neuer Prozess, einmaliger Verbrauch, wiederhergestellte Konten; `RestoredCallerV1` ab :277. | Aktuelle Aufrufermaterialisierung kennt keine Decoderfortsetzung. Bestehende native Wiederherstellung wiederverwenden, Medienherkunft separat vollständig prüfen. |
| Bedienung | `tools/_s2oe_local_player.py:132`, `start`; `:242`, `status`; `:227`, `stop`. | Status um ausgewählten Checkpoint, Quelldigest, abgeschlossene und nächste Position sowie kumulative Konten ergänzen. Keine internen Owner herausgeben. |
| Ereignisgrenze | `tools/_s2oe_local_player.py:158`, `_run` verarbeitet einzelne Ereignisse. | Geordnetes Suspend-Kommando nur vor dem nächsten Ereignis wirksam machen. Derzeit kann `Session.stop` (:239) einen laufenden Decoder abbrechen; das ist kein Checkpointstopp. |
| Abschluss | `tools/_s2oe_media_session.py:216`, `close` bewertet unvollständige Folge als INCOMPLETE. | Suspend als eigener gültiger Zwischenabschluss; genau eine Veröffentlichung, keine vollständige Erfolgsauswertung und kein Überschreiben durch INCOMPLETE. Endgültiger Abschluss nach vollständigem Suffix. |

Der qualifizierte `tools/_checkpoint_transfer_entry.py` ist ein fest gebundener
Referenz-/Save-/Restore-Versuchsaufrufer mit Rollenautorisierung und privatem
Ledger, kein fertiger Benutzerstarter. Seine Zulassung nicht auf beliebige
Dateien übertragen. Native Speicherform und Mechanik bleiben unverändert;
neue Bedien-/Quellenbindungen benötigen eigene aktive Code- und Prüfbelege.

## Medienposition und Decoder

`tools/_s2oe_media_decoder.py:118` öffnet je Durchlauf Container und Iteratoren
von vorn. `select` (:149) verlangt fortlaufende Fenster ab null und hält bei
wiederholter Fensternummer PCM/RGB bereit. Ein beliebiger Restoreindex wird
heute nicht akzeptiert. Ein Dateioffset allein stellt Codec-, Audio- und
Frameauswahlzustand nicht wieder her.

Zusätzlich zum Systemcheckpoint binden: unveränderte Containerdatei/Hash,
Streamindizes und Konversionsprofil, Original-PTS/Zeitbasen, Durchlauf,
zuletzt abgeschlossene Ereignisordinalzahl, nächste Auswahlposition sowie
Runtimezeit. Native 30000/1001 fps bleiben von Runtimefenstern getrennt.
Bei mehreren Hinweisen/Formationen desselben Fensters muss auch die genaue
Unterposition erhalten bleiben, nicht nur die Fensternummer.

Kleinster zunächst prüfbarer Wiedereinstieg: dieselbe Datei im neuen Decoder
ab Durchlaufbeginn bis zur benötigten Auswahlstelle kontrolliert vorlaufen
lassen. Bereits abgeschlossene Ereignisse nicht erneut an Rezeptoren, NJ,
Feld oder Memory übergeben. Kein ungeprüftes Keyframe-Seeking und keine
Serialisierung interner Codecobjekte. Falls noch ein Ereignis zum zuletzt
benutzten Fenster offen ist, dessen Medienfenster erneut decodieren, nicht
den früheren Systemschritt wiederholen. Diese Methode ist nur ein Vorschlag,
noch nicht implementiert oder als ressourcengerecht nachgewiesen.

Decoderwiedereinstieg verursacht zusätzliche physische Lese-/Decodearbeit.
Getrennt zählen: Eingangsbestand, geplante und tatsächliche Lesebytes,
Wiedereinstieg, ausgewählte Fenster, Rezeptor-/NJ-Aufrufe und MCM-Ereignisse.
Verbrauchte Arbeit darf durch Prozessneustart nicht verschwinden. Verbleibende
Ereignis-/Formationsbudgets ergeben sich aus ursprünglichem Manifest minus
abgeschlossenem Präfix; Decoderbudget muss zusätzliche Vorlaufarbeit umfassen.
Prozessbezogene Spitzenwerte und kumulative Arbeitskonten nicht vermischen.
Aktive Worker-/Jobgrenzen aus `tools/_s2oe_decoder_worker.py` bleiben wirksam.

Vor Umsetzung offen: vollständige phasenweise Hülle aus Medienbelegen,
Systemcheckpoint, aktiven Referenzen, Restlauf und alternativen Fehlerformen.
Die passende Sieben-Ereignis-Bilanz beweist keine passende Videobilanz.
Keine Grenzerhöhung oder automatische neue Reserve aus diesem Plan ableiten.

## Minimale spätere Prüfaufgabe

Eine kleine vorgebundene neutrale Datei/Folge in zwei getrennten Instanzen:
ununterbrochen gegen geordnetes Suspend an einer abgeschlossenen Grenze,
Prozessende und Restore. Gleiche Ereignisse, Profile und Quellen; keine neue
Quelle beim Restore. Vor jeder noch offenen Verarbeitung Position prüfen.

Vergleichen: ausgewählte PCM/RGB- und PTS-Bindungen, Runtimeuhren, native
Feld-/Memoryzustände, Prototypen, Generationen, Ablaufkonten, Scans und
Entscheidungen. MCM-Arbeit muss gleich sein; zusätzliche Decoderarbeit muss
gesondert und innerhalb der kumulativen Grenzen belegt sein. Kein erneutes
Systemereignis aus dem Präfix. Eine Grenze innerhalb gemeinsam genutzter
Cue-/Formationsfenster zusätzlich neutral prüfen, sofern der Modus sie zulässt.

Unabhängige Negativkontrollen: fremde Quelle/Profil/Manifest, manipulierte
Position, verbrauchter Checkpoint, fehlender Inhalt hinter Referenz,
erschöpftes Decoderbudget, Suspend während Verarbeitung, Publikationsfehler
und mehrfaches Stoppen. Primärfehler erhalten; fehlgeschlagenes Sichern nicht
als wiederladbar anzeigen. Auf Ende der Folge regulär schließen, keinen
weiteren fortsetzbaren Rest behaupten. Bestehende Prüfung wiederverwenden,
keine historische Testserie pauschal wiederholen.

Noch nicht freigegeben: diese Prüfungen oder ihre Umsetzung. Zunächst muss
der Medienmanifest-/Checkpointanschluss samt Wiedereinstiegs- und Budgetform
konkret gebunden werden. Keine freie Quellenwahl beim Restore, Livequellen,
Crash-Recovery, neue Lernregel oder automatische Aufmerksamkeit.
