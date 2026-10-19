# Videoversuch: vorzeitiger Abschluss und Bedienkorrektur

## Vorhandene Instanz gelesen, kein neuer Start

Port 43824 antwortete bei Übernahme mit `NOT_EVALUABLE`, 8/24 Ereignissen,
`error:null` und bereits erfolgter Verifikation (`evaluation_allowed:false`).
Kein Startkommando, zweiter Starter, Wiederanlauf oder erneuter Verifikatoraufruf.
Kein während einer laufenden Verarbeitung beobachteter Stillstand; die
Sitzung war bei der ersten Statusabfrage bereits geschlossen.

Lauf `media-memory-video-20260911-02` bleibt verbraucht und unverändert.
Der gespeicherte Grund ist **CLOSE / INCOMPLETE**, nach acht Ereignissen;
nächstes Ereignis wäre 9 gewesen. Kein Decoder-, Werte- oder Budgetfehler
ist im Abschluss verzeichnet. Der konkrete Auslöser des Schließens ist nicht
gespeichert. Insbesondere wird ein Benutzerklick auf Stopp nicht nachträglich
als gemessene Ursache behauptet.

## Erreichter Umfang und Grenzen

- Acht Audioanalysen, acht NJ-Projektionen und acht visuelle Analysen.
- Acht verarbeitete Ereignisse; acht Feld- und Memoryformationsversuche im
  geschlossenen Runtime-Snapshot. Letzte angezeigte Rückgabe:
  `FIELD_CONTACT_RECORDED / FORMATION_COMMITTED`, kein Abruf angefordert.
- Acht ausgewählte AV-Fenster im ersten Durchlauf, 108 native Videoframes,
  169 Audioframes und 173.056 decodierte Audiosamples.
- Decoder-Lesemenge 194.356.215 Byte, Zähler vollständig. Vorschau separat
  123.344.326 Byte; sie war kein Decodereingang.
- Keine Prozess-/Joblimitmeldung, keine native ERROR/FATAL-Meldung.
  Peak Process Commit 598.466.560, Peak Job Commit 605.044.736 Byte.
- Worker und Sitzung geschlossen, Gates False. Keine Scans und kein zweiter
  Durchlauf. Die Wiederabruf-/Lernfrage ist deshalb **nicht geprüft**.

Die bestehenden Abschlussbelege zeigen erreichte Verarbeitung, aber keine
vollständig verifizierte Formationsgeschichte: `execution:null` und
`evaluation:null`. Es erfolgt keine nachträgliche fachliche Teilauswertung.

Record-Digest: `47fc047ea992c61f038099ef1c8315abec60272edb0c40daee6f1ceecf9e2e35`.
Bestehender Verifikationsdigest:
`59b096fd6095ecf1ca1d3b44f0a246ca97fcd41566465712f31383daebb9d760`.

## Vorschauverhalten aus dem vorhandenen Code

`tools/s2oe_player.html:32` pausiert das Video beim MCM-Start ausdrücklich.
`:23` pausiert die Vorschau außerdem nach fünf Sekunden und setzt ihre Zeit
auf null; `:24` verhindert Vorschauseeks über fünf Sekunden hinaus.
`tools/_s2oe_local_player.py:274` sperrt neue Vorschauanforderungen nach
Verbrauch der Sitzung mit `PLAYER_PREVIEW_CLOSED`. Bereits gepufferte
Browserbilder sind keine Zustandsanzeige der MCM-Verarbeitung.

Damit ist das stehende Vorschaubild durch die Bedienlogik erklärbar. Eine
Browser-/Decoder-Synchronisierung existiert nicht (`synchronized:false`).
Der genaue historische Klick-/Wiedergabeverlauf wurde nicht aufgezeichnet.
Der finale Playerstatus zeigt `error:null`, obwohl die Sitzung ihren
vorzeitigen Abschluss als `INCOMPLETE` speichert. Das ist eine zusätzliche
Anzeigelücke, kein Nachweis eines verschwundenen Decoderfehlers.

## Kleinste vorgeschlagene Bedienkorrektur

Vorschau und Verarbeitung **eindeutig trennen**, statt eine scheinbare
Echtzeitsynchronität einzuführen:

1. Ein Start löst die gesamte gebundene Verarbeitung aus. Vorschau bleibt
   optional vor Start; während der Verarbeitung keine wiederholt zu
   betätigende Play-Schaltfläche. Das eingefrorene Bild wird ausdrücklich
   als inaktive Vorschau markiert, nicht als aktuelles Rezeptorbild.
2. Fortschritt, Durchlauf, gebundene Medienfenster und abgeschlossene
   Ereignisse bilden die primäre Betriebsanzeige. Browserzeit steuert keine
   Auswahl und keine Runtimeuhr.
3. Vorzeitiger Stopp wird als solcher angezeigt, mit erreichter Ereigniszahl
   und gespeichertem Abschlussgrund. Technischer Fehler, regulärer Abschluss
   und bewusster Stopp dürfen nicht dieselbe leere Fehleranzeige ergeben.
4. Künftigen Stoppauslöser im vorhandenen Abschlussbeleg unterscheiden:
   Bedienkommando, Serverabschluss oder Verarbeitungsfehler. Keine neue
   Recorderplattform oder nachträgliche Umdeutung dieses Laufs.

Nur vorbereitet, nicht implementiert. Dafür wären eng begrenzte Bedien- und
Abschlussprüfungen mit neutralen Rückgaben sinnvoll; keine erneute Decoder-
oder Memorygeschichte. Ein weiterer realer Versuch benötigt eine neue ID
und ausdrückliche Freigabe. **RÜCKMELDUNG ERFORDERLICH:** diese Bedienkorrektur
freigeben; kein automatischer Folgeversuch.
