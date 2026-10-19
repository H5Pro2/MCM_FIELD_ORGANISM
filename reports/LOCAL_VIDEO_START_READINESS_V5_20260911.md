# Private Medienversion v5: abschließende Startbindung

## Ergebnis und Startbereitschaft

Die fokussierte administrative Versionsprüfung ist bestanden, genau einmal
unter `media-player-admission-20260911-02`. Keine Browser-, Decoder-,
Rezeptor-, Sitzungs- oder sonstige Funktionswiederholung. Drei Grenzgleichstände
und drei +1-Byte-Abweisungen wurden mit den unveränderten Ledger-/Fehlerfunktionen
an vorhandenen Belegformen geprüft. Vollständige historische Prüfdeckung,
Code- und Browserbindungen bleiben erhalten; administrative Quelldifferenzen
sind ausdrücklich geprüft und nicht als historisch ausgeführt ausgegeben.

- Administrative Bindung: SHA-256
  `c6cc169cc121f4fa303be33d60deaac3aaf4d3838d1b8c0ee7c9986849a6cf0c`.
- [Prüfabschluss](s2oe/media-player-admission-20260911-02/result.json):
  `1ff69ac269f6b1e010a442a54f6f84964209d78c33e1c104b4c038364d13b90e`.

### Konkrete Laufbindung

Unverbrauchte Lauf-ID `media-memory-video-20260911-01`; neue Bindungsablage
`s2oe/media-player-run-binding-20260911-02`. Die frühere zu große Bindung 01
bleibt unverändert. Ausgabe- und Autorisierungsverbrauchsdatei fehlen.
Der konkrete `load_binding()`-Aufruf des Starters hat Quellen-/Code-/Profil-
referenzen, Zulassung, Settings und Bilanz akzeptiert. Dies war ausschließlich
Metadatenprüfung, keine weitere Verifikation eines Funktionslaufs oder
Sitzungsinitialisierung. Auf Port 43823 wurde kein Listener gemeldet;
der Port ist dadurch nicht für einen späteren Zeitpunkt reserviert.

| Vollständige Maximalbilanz | Byte | Grenze |
|---|---:|---:|
| Reale Sitzungsmetadaten | 100.017 | 131.072 |
| Quellen | 259.828 | 262.144 |
| NJ-Zusatzbelege | 22.528 | 22.528 |
| Formationszusatz | 30.720 | 30.720 |
| Generationszusatz | 30.720 | 30.720 |
| Gemeinsame Zusatzhülle | 343.796 | 393.216 |
| Verifikation | 262.144 | 262.144 |
| Laufgesamt | 3.818.322 | 4.194.304 |
| Lauf plus vollständige Qualifikationsablage | 3.948.265 | 4.194.304 |

Die gemeinsame Gesamtbilanz enthält die vollständigen historischen Bilder,
Logs, Prüfbelege und alle neuen Reserven. Identische physische Referenzpfade
werden nur einmal gezählt; getrennte common-Kopien bleiben getrennt gezählt.
Die Qualifikationsmetadatengrenze 147.456 und die reale Sitzungsgrenze 131.072
bleiben getrennte Geltungsbereiche. Es gibt keine größere Memorykapazität.

Alle 25 Fortschrittspositionen und beide alternativen Abschlüsse sind gebunden.
Zusätzlich geprüft: unveränderte vorgelagerte abstrakte Startrechnung
(höchstens 63.622 Byte Metadaten) sowie die konkrete interne Startrechnung
(höchstens 82.170 Byte). Keine Verletzung. Die vollständige äußere Bilanz
mit Original-common, sich selbst, Bedienunterlagen und Abschlussreserven
bleibt maßgeblich; die kleinere Startrechnung ersetzt sie nicht.

Die Bilanzdatei belegt 13.785 Byte. Gegenüber der historischen zu großen
Vorbindung fallen keine notwendigen Belege weg: Die neue Verletzungsliste
ist leer, daher gibt es dort keine zusätzlich ausgeschriebenen verletzten
Zeilen. Das ist keine nachträgliche Kürzung der alten Datei. Die neue
Startanleitung belegt 2.756 / 3.072 reservierte Byte; der administrative
Kurzbericht 287 / 512 reservierte Byte.

Gebunden sind außerdem 3.000 Byte Auswertung, 768 Dispatch, 1.536 Abschluss-
bilanz, 512 common-Referenz, 1.024 Playerabschluss, 512 Verbrauchsnachweis,
1.024 Settings, zusammen 1.024 für Vorlage und spätere Autorisierungsdatei,
512 Bericht sowie die vollständig gezählten common-/Inventardateien.
Keine wirksame Autorisierung wurde jetzt erzeugt. Alle aktiven neuen
administrativen Quell- und Ergebnisbindungen sind enthalten.

### Befehl und Bedienung

Der vollständige gebundene Befehl mit Arbeitsverzeichnis steht in
[START.md](s2oe/media-player-run-binding-20260911-02/START.md).
Bedienadresse nach ausdrücklichem Start: `http://127.0.0.1:43823/`.
Start verbraucht beim ersten autorisierten Klick genau die eine Freigabe.
Status zeigt nur vorhandene Rückgaben; Stopp beendet kontrolliert. Der Player
übernimmt die einmalige Verifikation. Kein automatischer Wiederanlauf und
kein äußerer zweiter Verifikator. Hypothesen bleiben unangewandt.

Settings-SHA-256:
`18d6c1799b26a98869bb93d500d0a7779eaa282dde217b317bea6644db2de696`.
common-SHA-256:
`7d306c851a74eeccb00c6aca3b5397372c6d8e450f217cb12a457f08bae5e6d3`.
Budget-SHA-256:
`837a6a39dcf87990bbfe297bb46e4984634e7e2d1c9b0d6b3d92e80845d25650`.

### Verbleibende Voraussetzung und Aussagegrenzen

**Einzige noch fehlende administrative Voraussetzung ist die separate
Einmallauffreigabe.** Erst danach darf `authorization.json` mit dem bereits
festgelegten Inhalt und SHA-256
`830b7141f39a7dc50fa2ef3e0ad4aa57d25718ea1f414c5c639ac2f0ba294624`
bereitgestellt werden. Die vorhandene Vorlage trägt `authorized: false`.
Der Befehl ist vollständig bestimmt, aber jetzt nicht ausgeführt worden.

Die ausgewählte lokale MP4 wurde nicht gelesen. Ihr historisch gebundener
SHA-256 bleibt `df0986f384e156c4dfec234e94b6f6baa3d0f8a9cfd7ba81f14aadf0313450aa`.
Bestand 83.498.438 Byte; Decoder-Leseobergrenze 1.001.981.256 Byte, Vorschau
separat ebenfalls höchstens 1.001.981.256 Byte. Tatsächlich jetzt gelesene
MP4-Bytes: null. Keine Garantie der späteren Container-/Decoderfähigkeit.
Ein technischer Fehler im echten Lauf muss ohne Retry erhalten bleiben.

Unverändert: 24 Ereignisse, 20 Formationen, zwei auditive und zwei visuelle
Hinweise, 22 Audio-/NJ- und 22 visuelle Verarbeitungen, 7.392 Feldkontakte,
acht Scans. Audiofenster beginnen bei 0; 0,5; ...; 4,5 Sekunden pro Durchlauf.
Frameauswahl am oder vor der jeweiligen Mitte, tatsächliche Original-PTS
und Zeitbasis getrennt von Runtimezeit. 30000/1001 fps sind nicht native
30 fps. Zweiter Durchlauf setzt Medienzeit zurück, nicht Runtime oder Memory.

Decoderjob weiterhin 512 MiB Commit, ein 6.240.000-Byte-Übergabeplatz,
4.096 Byte Nachricht und 30 Sekunden Anfragefrist. Keine Gesamt-RAM-Garantie
für Browser/Elternprozess. Browser-Vorschau ist nicht decoder-synchronisiert.
Ein positiver späterer Befund wäre begrenzte Muster-/Abrufevidenz dieses
Ausschnitts, keine Semantik oder allgemeine Quellenidentität. Detailblick,
automatische Fokussierung und neue Memorymechanik bleiben außerhalb.

Historische Qualifikationen und Fehlbefunde unverändert, Gates False.
Dieses Forschungsdokument ist keine zusätzliche operative Laufabhängigkeit;
die vollständige Bedienung steht innerhalb der mitgezählten START.md.

## Prospektive Änderung

Genehmigt sind 131.072 Byte Sitzungsmetadaten ausschließlich für
`s2oe.sampled-media.v5-private-session-budget`. Quellen 262.144,
Zusatzhülle 393.216, Gesamt 4.194.304, Verifikation 262.144 Byte und alle
Wahrnehmungs-, Memory- und Decodergrenzen bleiben unverändert.
Die historische 65.536-Byte-Defaultbindung wird nicht geändert. Alte
Versionen und Fehlbefunde bleiben archiviert; kein Status wird ersetzt.

`tools/_s2oe_media_binding.py` ändert nur VERSION und den expliziten privaten
Metadatenwert in SESSION_LIMITS. Dieselbe bestehende Ledger-/Vergleichslogik
wird bei Start, Fortschritt, Abschluss und Verifikation verwendet.
`_s2oe_media_session.py` erhält nur die neue administrative Zulassungs-ID.
Die beiden administrativen Prüfscripte binden diese Differenz ausdrücklich.
Alle 16 Quellen des vorigen administrativen Stands wurden vor Änderung
hashgeprüft archiviert.

## Fokussierte administrative Prüfung

Neue ID `media-player-admission-20260911-02`. Keine neue Funktionsqualifikation:
vorhandene zehn Prüfgruppen, Bilder und Browserdateien werden gelesen.
Der neue Policytext muss nach genau zwei expliziten Rückersetzungen bytegenau
dem getesteten v4-Code entsprechen. Alle übrigen historischen Produktdateien
bleiben bytegleich, abgesehen von der ausdrücklich gebundenen Zulassungs-ID
und den schon erklärten administrativen Inventarergänzungen der Sessiondatei.

An gespeicherten, nicht erneut erzeugten Belegformen wird die unveränderte
Vergleichslogik für START, PROGRESS und CLOSE geprüft: 131.072 Byte akzeptiert,
131.073 typisiert als MEDIA_ENVELOPE_LIMIT abgewiesen. Phase und neue Grenze
müssen im Fehlerbeleg erhalten bleiben. Keine Runtime oder Wahrnehmung wird
dafür aufgerufen.

Vollständige Vorbilanz: Qualifikationsmetadaten 147.160 / 147.456,
Quellen/Zusatzhülle 259.607, Gesamt 408.107 / 4.194.304 Byte.
Screenshots inklusive Restreserve 98.304 Byte; neue administrative Dateien
inklusive Bericht 4.608 Byte. Keine weitere lokale oder globale Grenzerhöhung.
Die nachfolgende reale Bindung erhält ihre eigene vollständige Bilanz.
