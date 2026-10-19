# UHD-Profil und vollständige Decoderfolge bestätigt

## Technischer Abschluss

Privates Profil `s2oe.file-bound-uhd1024.v1`: Datei, vollständige
Quellenidentität, Decoderkonfiguration, Codehashes und konkrete Lauf-ID
gemeinsam digestgebunden. Prozess- und Job-Commit jeweils 1.024 MiB,
überlappend, nicht addiert. Queue 1, Ausgabeslot 6.240.000 Byte,
Anfragezeit 30 s und kontrollierter Abschluss binnen 5 s unverändert.
Der historische 512-MiB-Default wurde nicht erhöht.

`uhd-profile-neutral-20260911-01`: genau einmal **6/6 bestanden**.
Prüfdeckung: unveränderlicher Profilbeleg, getrennte Ablehnung falscher
Prozess-/Joblimits, abweichende Threads/Queue/Zeitlimits, fremde Quelle/Lauf-ID,
veränderte Code-/Digestbindung sowie Auswahl des festen Workerarms und
Schließen bei falschem aktivem Limit. Die neuen Factorygrenzen wurden
neutral mit kontrollierten Workerrückgaben geprüft; keine Browser- oder
historischen Workerprüfungen wiederholt. Die realen OS-Limits wurden im
anschließenden Decodercheck tatsächlich bestätigt.

`decoder-uhd-sequence-20260911-01`: **DECODER_SEQUENCE_COMPLETE**.
Danach genau eine unabhängige read-only Prüfung: **EVIDENCE_VALID**.

| Umfang | Tatsächlich |
| --- | ---: |
| gebundene Ereignisübergaben / Select-Aufrufe | 24 |
| ausgewählte unterschiedliche AV-Fenster | 20 |
| Durchläufe | 2 |
| Freigaben nach Formationsposition | 20 |
| decodierte Videoframes | 276 |
| decodierte Audioframes | 432 |
| decodierte Audiosamples | 442.368 |
| Pakete | 716 |
| tatsächliche Container-Lesebytes | 401.434.996 |
| Peak Process Commit | 599.674.880 Byte |
| Peak Job Commit | 606.253.056 Byte |

Die vier zusätzlichen Select-Aufrufe entsprechen den gebundenen
Hinweispositionen und verwenden den noch nicht freigegebenen Endpunkt
vor der zugehörigen Formation. Das sind keine vier zusätzlichen ausgewählten
Fenster. Nach jeder Formationsposition wurde der Decoderpuffer freigegeben.
Es fand keine Formation oder Hinweisverarbeitung durch MCM statt.

Native ERROR/FATAL-Meldungen: keine; Prozess-/Joblimitmeldungen: keine.
Der eine Worker wurde nach beiden Durchläufen kontrolliert geschlossen.
Exitcode 1 bezeichnet den bestehenden kontrollierten Jobabschluss.
Vollständige Lesecounter; Gates wurden nicht geöffnet.

## Quellen und Aussagegrenze

Unveränderte Datei `17138816-uhd_3840_2160_30fps.mp4`, 83.498.438 Byte,
SHA-256 `df0986f384e156c4dfec234e94b6f6baa3d0f8a9cfd7ba81f14aadf0313450aa`.
Der bestehende Decoder prüft ihren Hash vor jeder Containeröffnung. Keine
Regeneration oder Rohpayloadablage. PyAV 16.1.0, FFmpeg 8.0.1;
30000/1001 fps, native PTS und Zeitbasen unverändert.

Alle Rückgaben wurden fortlaufend auf Formate, Größen, Endlichkeit und
PCM-Wertebereich sowie PTS-Auswahl geprüft, gehasht und freigegeben.
Gespeichert sind Zeit-/Format-/Digest-/Ressourcenbelege, keine Bilder oder
Audiosamples. Die Offline-Prüfung kontrolliert deren Bindung und vollständige
Folge, nicht die numerischen Ausgaben durch erneutes Decodieren.

**Bestätigt ist die Decoder-Eingangsbereitschaft dieser endlichen Folge.**
Keine Rezeptoren, NJ, Feld, Memory oder Runtime aufgerufen. Weder ein Lern-
noch ein Abrufbefund folgt daraus; auch keine allgemeine Decoderkapazität.

Vor Start verfügbar: 14.048.755.712 Byte Commitspielraum und 7.136.022.528 Byte
RAM, oberhalb der gebundenen Sicherheitsanforderungen. Vorbilanz einschließlich
Reserven 254.397 Byte. Ist vor Verifikationsdatei und Bericht 110.776 Byte;
Verifikation und Bericht zusammen mit 24.576 Byte reserviert.

Beleg-SHA-256:
`2082ac5e521aa984c969806bb7d3b0a7f15e0e51db86127a9230dad96123387c`.
Qualifikations-SHA-256:
`bc788128dece11faa2eb50a2758dbfffd6abaabedba4ca36863548deae5385df`.

## Neue reale Laufbindung: vorbereitet, noch nicht startbereit

Neue ID: `media-memory-video-20260911-02`; Ergebnisverzeichnis und
Verbrauchsdatei fehlen. Keine Autorisierung oder Startausführung erzeugt.
Quelle und alle 24 Ereignisse unverändert in
`../media-player-run-binding-20260911-03/proposed-binding.json` übernommen.
Neuer laufgebundener Profildigest:
`da95487276bcb8f82a1a75bdcdc9005f7e898c7751af9b8af6c5dc62a284b9bf`.

Status ausdrücklich **BLOCKED_NOT_START_READY**. Drei reale Anschlusslücken:

1. `_s2oe_media_session.start()` konstruiert noch `Decoder(manifest.source)`
   ohne das neue Profil; `bind_common()` bindet den Default. Der qualifizierte
   Profilfactoryanschluss ist vorhanden, aber dort noch nicht ausgewählt.
2. `check_common()` und die Playerzulassung verlangen historische exakte
   Worker-/Decoderhashes. Diese Nachweise werden nicht als Zulassung des
   veränderten Codes umgedeutet. Der Sitzungsverifikator muss das neue
   Profil ausdrücklich prüfen; eine globale Lockerung ist nicht zulässig.
3. Die bisherigen aktiven Quellenreferenzen zählen mit aktuellem Code bereits
   **264.699 / 262.144 Byte**. Einschließlich neuer notwendiger Profil-, Prüf-
   und Vorbereitungsdateien sind es **291.129 Byte**, also **28.985 Byte zu viel**,
   bevor weitere Anschlussänderungen hinzukämen. Die einzelnen Dateien und
   Hashes stehen vollständig in der vorgeschlagenen Bindung. Keine Inhalte
   gekürzt oder umklassifiziert; dies ist eine Untergrenze, keine freigegebene
   vollständige Laufbilanz. Die passende Decoder-Prüfablage ersetzt sie nicht.

Die aktualisierte Bindung wird deshalb nicht als ausführbare Einmallauffreigabe
ausgegeben. Historischer Fehlversuch und alle früheren Belege bleiben unverändert.
Keine weitere Decoderoptimierung oder Wiederholung erforderlich.

**RÜCKMELDUNG ERFORDERLICH:** begrenzten Sitzungs-/Zulassungsanschluss an das
geprüfte Profil sowie die konkrete Quellenbudgetzuordnung entscheiden.
Der Decodercheck ist abgeschlossen; kein Lernlauf gestartet.
