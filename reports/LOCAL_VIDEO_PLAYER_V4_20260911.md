# Private Player- und Budgetanbindung v4

## Administrative Prüfung bestanden; konkrete reale Restgrenze

Die neue administrative Bindung wurde genau einmal unabhängig read-only
geprüft und als **QUALIFIED / ADMINISTRATIVE_ADMISSION** abgeschlossen.
Kein Test, Browser, Decoder oder Sitzungsaufruf wurde wiederholt. Der
historische Status von 03 bleibt NOT_QUALIFIED. Die zehn bestandenen
Funktionsgruppen werden weder erneut behauptet noch zum neuen Testlauf.

Die Prüfung kontrollierte alle historischen Dateien über den vollständigen
Dateibaumdigest, sämtliche zehn individuellen Passzeilen, Vorregistrierung,
Code- und Browseridentitäten, transitive Quellenbindungen und die vollständig
unabhängig summierte neue Bilanz. Die zwei administrativen Rückersetzungen
der Sessiondatei ergeben bytegenau ihren tatsächlich getesteten Stand.
Wahrnehmung, Verarbeitung, Memory und CSP sind unverändert.

Administrative Dateien einschließlich kurzem Abschluss: 3.862 / 4.608 Byte;
Rest 746 Byte. Screenshots 68.891 / 98.304, Rest 29.413 Byte. Zusammen
30.159 Byte verbleibende Reserve. Qualifikationsmetadaten 147.160 / 147.456,
Quellen und Zusatzhülle jeweils 257.729, Gesamt 406.229 Byte. Alle neuen
administrativen Grenzen eingehalten. Der kurze 279-Byte-Abschluss steht in
der reservierten Ablage; dieses ausführliche Forschungsdokument ersetzt
keinen Pflichtbeleg und ist keine operative Laufreferenz.

- [Administrative Bindung](s2oe/media-player-admission-20260911-01/binding.json),
  SHA-256 `996e1278994a929e2fd7f7d05140960c3dca178fb18c0c23dc8365512e5f0617`.
- [Unabhängiger administrativer Prüfabschluss](s2oe/media-player-admission-20260911-01/result.json),
  SHA-256 `4dccb25c6577c85c2b26b6f32bd43a4d5d1daa75e05da60a28ac717c227d3ff6`.

### Vollständige reale Laufvorbereitung

Neue Ablage `s2oe/media-player-run-binding-20260911-01`; vorgesehene
unverbrauchte Lauf-ID bleibt `media-memory-video-20260911-01`. Quellenbytes,
24 Ereignisse, 20 Formationen, vier Hinweise, 22 Audio-/NJ- und 22 visuelle
Analysen, 7.392 Feldkontakte und acht Scans unverändert gebunden. Die alte
common-Datei wird mit ihrem bekannten Hash ausschließlich als Quellenherkunft
referenziert; keine MP4 wurde dafür geöffnet.

Ein erster administrativer Leseversuch der alten common-Datei scheiterte an
deren nicht aktueller kanonischer JSON-Kodierung, bevor die neue Ablage erzeugt
wurde. Danach wurde sie als historische, zuvor SHA-256-geprüfte JSON-Referenz
gelesen, nicht als aktueller Runtimebeleg akzeptiert. Die neue native Source-
und Manifestform wurde regulär aufgebaut und gebunden. Kein Validator wurde
gelockert; keine Test- oder Sitzungswiederholung fand statt.

Die aktuelle Quellenbindung einschließlich Starter, Zulassung und ihrer
Prüfskripte sowie sämtliche 25 Fortschrittspositionen und Abschlussalternativen
stehen in der neuen Ablage. Lauf- und Qualifikationsscope werden ausdrücklich
getrennt: 98.304 Byte für reale Sitzungsmetadaten, 147.456 für die abgeschlossene
Qualifikationsablage. Letztere wird nicht aus der gemeinsamen Gesamtbilanz
entfernt: Alle Dateien, Bilder und Reserven sind dort zusätzlich enthalten;
nur identische physische Referenzpfade werden einmal gezählt.

| Reale Vorbindung | Maximum Byte | Grenze Byte |
|---|---:|---:|
| Metadaten | **102.007** | **98.304** |
| Quellen | 257.950 | 262.144 |
| NJ | 22.528 | 22.528 |
| Formationen | 30.720 | 30.720 |
| Generationen | 30.720 | 30.720 |
| Zusatzhülle | 341.918 | 393.216 |
| Verifikation | 262.144 | 262.144 |
| Laufgesamt | 3.818.434 | 4.194.304 |
| Lauf plus vollständige Qualifikation | 3.948.635 | 4.194.304 |

Erste Überschreitung: Fehleralternative bei Fortschritt 18, 98.776 Byte.
Bei Fortschritt 24: Erfolg 101.420, Fehler 102.007 Byte. Das ist eine
Vorabsicherungsgrenze, keine gemessene Größe eines realen Laufs.

Die maximale Fehler-Metadatenrechnung ist vollständig nachvollziehbar:
20.454 Record + 3.453 Session ohne 393.216 Byte separat klassifizierte
Präfixschritte + 10.139 Lauf-common + 512 Bericht + 28.765 aktive
Metadatenreferenzen + 38.684 reservierte Anteile = **102.007 Byte**.
Die reservierten Anteile enthalten ausdrücklich die 10.139-Byte-Originalkopie
von common, die 16.073-Byte-Bilanzdatei selbst, Auswertung, Dispatch,
Abschluss, Playerabschluss, Settings, Autorisierung und Startanleitung.
Gleiche Inhalte in zwei physischen common-Dateien werden zweimal gezählt.
Die Bilanzdatei enthält auch ausgeschriebene verletzte Zeilen; sie wurde nach
Feststellung der Überschreitung nicht nachträglich verkürzt.

- [Konkrete Bilanz](s2oe/media-player-run-binding-20260911-01/budget.json):
  `7961b2b8795e62bf70eb1fa7897384e6ffd0e0e7c946c2e0d73fe8298a010d75`.
- Aktuelle common-Datei:
  `128b78fa2d8f987dcd76bafc683f47f8f2368e630ddd9f520fe4dc76ba4190ec`.
- Settings:
  `50c1220e6edaf6424d82acd2daf23678699915e1a8bf1da9149c93281167b18d`.
- [Startanleitung mit konkretem, noch gesperrtem Befehl](s2oe/media-player-run-binding-20260911-01/START.md).

**NOT_START_READY:** Der Starter verlangt eine leere Verletzungsliste und
darf diese Bindung daher nicht starten. `authorization-template.json` bleibt
ausdrücklich `authorized: false`; keine wirksame Freigabe oder Verbrauchsdatei
erzeugt. Der administrative Nachweis ist abgeschlossen. Offen bleibt allein
die reale Metadatenüberschreitung von 3.703 Byte. Keine erneute Qualifikation,
Quellenverarbeitung, Größenkorrektur oder automatische Folgeausführung.

## Administrative Anschlussbindung nach 03

Ausdrückliche neue Freigabe: Screenshotreserve 98.304 Byte und vollständige
Qualifikationsmetadaten 147.456 Byte ausschließlich für die neue administrative
Bindung. Historischer Gesamtstatus von 03 bleibt NOT_QUALIFIED. Die reale
Sitzungsgrenze bleibt 98.304 Byte; p.SESSION_LIMITS und die historische
Funktionsqualifikationsrechnung werden nicht global geändert.

Neue administrative ID `media-player-admission-20260911-01`, kein neuer
Funktionslauf. `reports/prepare_media_admission.py` bindet den vollständigen
vorhandenen Dateibaum mit Größen und Hashes über einen kanonischen Digest.
Die Inhalte bleiben an ihren vorhandenen Pfaden lesbar. Alle Dateien und
externen Referenzen werden vollständig gezählt. Die separate
`reports/verify_media_admission.py` liest einmal unabhängig und kontrolliert
die zehn individuellen Passzeilen, Vorregistrierung, aktuellen Code,
Browserdateien, ursprüngliche Fehlerklassifikation und vollständige Bilanz.
Sie ruft keinen Testkörper, Browser, Decoder oder Runtimepfad auf.

Die einzige Änderung an vorhandenen Produktdateien ist administrativ:
`_s2oe_media_session.py` verweist auf die neue Zulassung und führt die zwei
neuen administrativen Quelldateien im Inventar. Die Prüfseite rekonstruiert
den historischen Modultext durch genau diese beiden expliziten Rückersetzungen
und prüft Größe und SHA-256 gegen den tatsächlich getesteten Stand. Das ist
ein Nachweis der begrenzten Quelldifferenz, keine Wiederholung historischer
Tests und keine Behauptung, die neue Zulassungsreferenz sei damals getestet.
Alle übrigen getesteten Quelldateien müssen bytegleich bleiben.

Vorbilanz einschließlich vollständiger Reserven: Metadaten 147.160 / 147.456,
Quellen 257.729 / 262.144, Zusatzhülle 257.729 / 393.216, Verifikation
564 / 262.144, Gesamt 406.229 / 4.194.304 Byte. Screenshotreserve vollständig
98.304 Byte, davon unveränderte Dateien 68.891 und Rest 29.413 Byte.
Für die neuen administrativen Bindungs-/Prüfdateien und Bericht sind zusammen
4.608 Byte reserviert. Die bereits abgeschlossenen alten Qualifikationsdateien
zählen vollständig mit ihrer Istgröße, nicht erneut mit einer zusätzlichen
Reserve für eine ausdrücklich ausgeschlossene Funktionswiederholung.

Der unabhängige Prüfabschluss wird als `ADMINISTRATIVE_ADMISSION` ausgewiesen.
Er kann eine aktive Zulassung begründen; er macht aus dem historischen
NOT_QUALIFIED keinen historischen Erfolg. Keine reale MP4 geöffnet.

## Abschluss 03: 10/10, aber Belegbudget nicht eingehalten

`media-player-qualification-20260911-03` wurde genau einmal ausgeführt:
zehn Gruppen in 16,410 Sekunden, Testprozess Exitcode 0. **Alle Prüfgruppen
bestanden; Gesamtstatus bleibt NOT_QUALIFIED wegen Größenüberschreitung.**
Historische 9/10-Belege sind unverändert. Kein Retry und keine weitere
Quellen-, CSP-, Anzeige- oder Budgetänderung nach dem Aufruf.

Erreicht wurden nun auch die zuvor verdeckten Kontrollen: Videowiedergabe
mit fortgeschrittener Zeit, nicht einfarbiger Frame, Desktop- und Mobilansicht
ohne horizontalen Überlauf, Start/Status/Stopp über tatsächliche Browserbuttons,
sichtbarer unveränderlicher Memory-/Enthaltungsstatus sowie Wiederanlaufsperre.
Die Browserbedienung verwendet eine synthetische Sitzung. Der separate native
Sitzungsanschluss bis zum ersten Ereignis, kontrollierter Stopp und einmalige
Verifikation wurden ebenfalls erneut erreicht. Diese getrennten Kontrollen
sind kein vollständiger realer Medienlauf und kein Memory-Lernbefund.

Die gespeicherten Ansichten wurden anschließend ausschließlich lesend gesichtet:
keine erkennbare Überlagerung, Video und Bedienfelder sichtbar. Die Bilder
zeigen den neutralen Zustand vor Autorisierung; die nachfolgenden Klicks sind
über Assertions belegt, nicht als zusätzliche Screenshots gespeichert.

- [Desktopansicht](s2oe/media-player-qualification-20260911-03/desktop.jpg),
  36.872 Byte, 900 Pixel breit.
- [Mobilansicht](s2oe/media-player-qualification-20260911-03/mobile.jpg),
  32.019 Byte, 390 Pixel breit.

| Vollständige Istbilanz mit Restreserven | Byte | Grenze | Überschreitung |
|---|---:|---:|---:|
| Metadaten | **119.147** | **98.304** | **20.843** |
| Quellen | 249.766 | 262.144 | 0 |
| Zusatzhülle | 249.766 | 393.216 | 0 |
| Verifikation | 564 | 262.144 | 0 |
| Gesamt | 370.253 | 4.194.304 | 0 |
| Qualifikationsabschlussdateien | 7.444 | 12.288 | 0 |
| Screenshots | **68.891** | **40.960** | **27.931** |

Verbleibende Reserven: 6.008 Byte. Physische Belege und aktive Referenzen:
364.245 Byte; Metadaten ohne Restreserven 113.139 Byte. Auch diese liegen
14.835 Byte über der Grenze. Clientfixtures 7.540 / 8.192 Byte; vollständiges
Testlog 1.535 Byte. Der Fehler ist damit nicht die lokale Log-/Abschlussreserve,
sondern die unterschätzte vollständige visuelle Beleggröße. Keine Bilder
nachträglich verkleinert, entfernt, ausgelagert oder umklassifiziert.

- [Ergebnis 03](s2oe/media-player-qualification-20260911-03/result.json):
  `cafee3b1f2a9744c7f17a6d9a30cc7eba94f8f30b0d244e2061505ea3d2c3c0c`.
- [Inventar 03](s2oe/media-player-qualification-20260911-03/inventory.json):
  `232903354b8c569858b6c8629b634bb0cdaf24952cff781e3af538f8d828559f`.
- [Istbilanz 03](s2oe/media-player-qualification-20260911-03/final-balance.json):
  `109a514f6489bb11b047ffe7dc3585fb660252ddc1b417b595ba53298004c80b`.
- [Vollständiges Log 03](s2oe/media-player-qualification-20260911-03/stderr.txt):
  `08875af369bb2795d3920ba49885051d487c9c569cd572bd03d2ea24d9db7aef`.

Alle 14 Codebindungen und die Browserumgebung sind unverändert. Der technische
Starter `reports/start_bound_media_player.py` ist vorhanden, aber
`load_binding()` verlangt einen insgesamt qualifizierten Beleg. Deshalb
bleibt der reale Videoeingang gesperrt. Die alte Laufvorbereitung wird nicht
als finale neue Bindung ausgegeben. Kein realer Lernlauf, keine reale MP4
gelesen, keine erneute Workerqualifikation und keine Fokuserweiterung.
Gates False. Notwendig ist ausschließlich eine Entscheidung zum ausgewiesenen
Belegbudgetkonflikt, keine weitere allgemeine Anschlussklärung.

## Vorbindung 03: enge CSP-Testkorrektur

Die neue ausdrückliche Freigabe gilt für genau eine vollständige Suite mit
zehn Gruppen unter `media-player-qualification-20260911-03`. Der fehlerhafte
Stringprädikataufruf in Test 08 wird durch Locator-Assertions ersetzt;
Videozeit wird für höchstens fünf Sekunden durch direkte DOM-Funktionsaufrufe
beobachtet. Keine String-Evaluation und keine CSP-Lockerung. Sicht-/Pixel-
prüfung und Browserbedienung bleiben vollständig bestehen.

Geändert werden nur `tests/test_s2oe_player.py` und die aktive `QUAL_ID` in
`tools/_s2oe_media_session.py`. Die 14 Quellen von 02 wurden zuvor auf ihre
gespeicherten Hashes geprüft und unverändert archiviert. Player, HTML/CSP,
Decoder, Worker und sämtliche Produktregeln bleiben unverändert.

Vor Test: neue Ausgabeablage nicht vorhanden; sämtliche 25 Fortschritts-
positionen und Abschlussalternativen ohne Budgetverletzung. Qualifikations-
metadaten 97.873, Quellen 249.766, Gesamt 626.167 Byte. Laufhüllenmaximum:
Metadaten 94.480, Zusatzhülle 333.734, Gesamt 3.802.823 Byte. Unveränderte
Qualifikationsreserve 12.288 Byte, keine Erhöhung auf die genehmigte lokale
Obergrenze 16.384. Quell- und Browserinventar werden vor dem einen Testprozess
erneut vollständig gespeichert. Keine reale MP4, kein Lernlauf und kein Retry.

## Ergebnis der Neuqualifikation 02

**NOT_QUALIFIED**, neun von zehn Gruppen bestanden, genau ein neuer Aufruf
in 16,302 Sekunden. Historische Tests und Workerqualifikation nicht wiederholt.
Quellinventar und gebundene Browserdateien sind nach dem Aufruf unverändert.

Die Browserumgebung ist jetzt verfügbar: Chromium 151.0.7922.34 startete,
die Seite wurde geladen, `play()` kehrte zurück und `videoWidth===320` wurde
erreicht. Die unmittelbar folgende Abfrage in
`tests/test_s2oe_player.py:203` scheiterte mit:

`Page.wait_for_function: EvalError: Evaluating a string as JavaScript violates ... Content Security Policy ... 'unsafe-eval'`

Damit sind weder laufende Bildänderung noch Pixelprüfung, Desktop-/Mobil-
Screenshots und die danach angeordneten Start-/Status-/Stopp-Klicks bestätigt.
Es ist ein konkreter Fehler an der Test-/CSP-Grenze; kein belegter Memory-
oder Decoderfehler. Die CSP wurde nicht gelockert. Kleinste Korrekturrichtung:
CSP-verträgliche Funktionsprädikate statt aus Zeichenketten evaluierter
Ausdrücke beziehungsweise Locator-Assertions einsetzen, ohne `unsafe-eval`
freizuschalten. Nach dem Fehllauf keine Codeänderung und kein Retry.

Die übrigen neun Gruppen bestanden erneut eigenständig. Der native Fall
erreichte ein Ereignis und den kontrollierten Stopp; seine einmalige lesende
Prüfung meldet `NOT_EVALUABLE`, `evaluation_allowed=False`. Das ist die
erwartete Sperre des unvollständigen neutralen Laufs, keine volle native
Player-/Medienqualifikation. Die vollständige Bedienfolge ist separat
synthetisch geprüft, nicht durch den fehlenden Browsernachweis ersetzt.

| Vollständige Istbilanz mit Restreserven | Byte | Grenze |
|---|---:|---:|
| Metadaten | 91.216 | 98.304 |
| Quellen | 249.581 | 262.144 |
| Zusatzhülle | 249.581 | 393.216 |
| Verifikation | 564 | 262.144 |
| Gesamt | 342.137 | 4.194.304 |
| Qualifikationsabschlussdateien | 9.816 | 12.288 |

Restreserven 45.372 Byte; physische Belege plus aktive Referenzen 296.765 Byte.
Clientfixtures 6.764 / 8.192 Byte; Screenshots 0 / 40.960 Byte. Vollständiges
Fehlerlog 4.132 Byte. Es überschreitet den geplanten Loganteil von 4.096,
aber nicht die vorgebundene gemeinsame 12.288-Byte-Kappe. Keine Kürzung,
Umklassifizierung oder nachträgliche Grenzänderung; keine Budgetverletzung.

- [Ergebnis 02](s2oe/media-player-qualification-20260911-02/result.json):
  `1a4963d3fac078dea58dee618e435c33dec91ed0ded567c2e8f22ece29165da6`.
- [Inventar 02](s2oe/media-player-qualification-20260911-02/inventory.json):
  `68d7fec1afcb0ae5f7be777674be166c7a16120824d9d9bb50e4ca8e657cabe3`.
- [Istbilanz 02](s2oe/media-player-qualification-20260911-02/final-balance.json):
  `56ba77f0743f95e95fadbcb86917955500a4d1af8c184297b85971c64951f7ac`.
- [Vollständiges Log 02](s2oe/media-player-qualification-20260911-02/stderr.txt):
  `b8c87458779b1a6e69162386092008a566e7775234edecb065e3b8514d6cdc84`.

Der reale Einstieg bleibt **nicht startbereit**: Der aktuelle Starter
verlangt eine bestandene Playerqualifikation. Die vorhandene alte
Laufvorbereitung wird nicht umgedeutet; eine neue finale erfolgreiche
Bindung wurde nicht ausgegeben. `media-memory-video-20260911-01` und sein
Autorisierungsverbrauch sind weiterhin unbenutzt. Keine reale MP4 geöffnet,
keine weitere Video-/Rezeptorprüfung und kein Lernlauf. Gates False.

Die Detailblickidee ist ausschließlich im Forschungsweg vorgemerkt. Keine
Fokuserweiterung oder neue Forschungsserie begonnen.

## Prospektive Neuqualifikation 02

Neuer Auftrag: ausschließlich Video-Grundbetrieb fortsetzen. Der alte 9/10-
Beleg bleibt `NOT_QUALIFIED`. Vorhandene Ergebnisse wurden geprüft; ein
zweiter Aufruf lag nicht vor. Die 14 damaligen Quellen wurden vor Änderung
hashgeprüft archiviert; der Archivname verleiht ihnen keine Qualifikation.

Neue ID `media-player-qualification-20260911-02`. Die vollständigen zehn
Playerprüfgruppen werden einmal ausgeführt, keine Worker-Testserie.
Zusätzlich zu Vorschau und Sichtprüfung erfolgen Start/Status/Stopp über die
tatsächlichen Browserbuttons, mit synthetischer Bedienfolge. Der separate
native Einereignis-/Stoppfall bleibt erhalten. Keine reale MP4 wird geöffnet.

Browserumgebung: Playwright 1.62.0, Chromium Headless 151.0.7922.34,
Revision 1234. Die fehlende passende Browserdistribution wurde vom offiziellen
Playwright-CDN installiert, nicht eine vorhandene fremde Revision umetikettiert.
Browser-EXE, Node-EXE und Browserrevisionsdatei werden mit Pfad, Größe und
SHA-256 vorab in der Vorregistrierung gebunden, vor Browserstart und nach
der Suite erneut auf Gleichheit geprüft. Laufzeitinstallation ist getrennt
von erzeugten Belegen; die Bindungsmetadaten zählen vollständig. Die Dateien
werden nicht als zusätzliche Quellenbelege in den Versuch kopiert.

Die genehmigte lokale Qualifikationsreserve wird prospektiv auf **12.288 Byte**
gebunden: 4.096 Byte Vorregistrierung samt Umgebung, 4.096 Byte vollständige
Logs, 2.560 Byte Ergebnis und 1.536 Byte Abschlussbilanz als Plananteile;
die gemeinsame Kappe gilt für deren Summe. Größere reale Fehlerlogs bleiben
ungekürzt. Historische 8.192-Byte-Bindungen werden nicht geändert.

| Vorbilanz | Qualifikation | Laufhüllenmaximum | Grenze |
|---|---:|---:|---:|
| Metadaten | 97.873 | 94.480 | 98.304 |
| Quellen | 249.581 | 249.581 | 262.144 |
| Zusatzhülle | 249.581 | 333.549 | 393.216 |
| Verifikation | 262.144 | 262.144 | 262.144 |
| Gesamt | 625.982 | 3.802.638 | 4.194.304 |

Screenshots zusammen 40.960, Clientfixtures 8.192 und Berichtreserve 512 Byte
bleiben enthalten. Sämtliche 25 Fortschrittspositionen und beide
Abschlussalternativen passen. Der Quellstand wird unmittelbar vor dem einzigen
Aufruf als vollständiges Inventar gespeichert. Keine Ausführung der realen
Sitzung; die konkrete Laufbindung folgt nur nach erfolgreicher Qualifikation.

## Abschluss des einmaligen Aufrufs

**NOT_QUALIFIED**, neun von zehn Gruppen bestanden, ein Aufruf, 16,339 Sekunden.
Alle 14 gebundenen Quelldateien sind unverändert. Kein Retry, keine Installation
oder Korrektur nach dem Fehllauf. Keine reale MP4-Verarbeitung, Gates False.

Konkrete Fehler und Grenzen:

- Browserprüfung `tests/test_s2oe_player.py:192`: `chromium.launch()` verlangt
  `chromium_headless_shell-1234/chrome-headless-shell-win64/chrome-headless-shell.exe`.
  Diese Datei fehlt. Der Fehler liegt vor dem Browserstart; Wiedergabe,
  Desktop-/Mobilansicht und JavaScript-Prüfung wurden nicht erreicht. Daraus
  folgt weder ein bestandener Playernachweis noch ein belegter UI-Codefehler.
- Vollständige lokale Qualifikationsdateien: 9.641 statt 8.192 Byte,
  Überschreitung 1.449 Byte. Das 4.694-Byte-Fehlerlog wurde vollständig erhalten.
  Die passende Vorbilanz war keine Garantie der tatsächlichen Fehlergröße.
- Der native Anschlussfall erreichte ein Ereignis mit je einer Audio-, NJ-
  und Visualverarbeitung sowie je einem Feld-/Memoryformationsversuch. Danach
  regulärer vorzeitiger Abschluss `CLOSE/INCOMPLETE`, Runtime CLOSED und genau
  eine unabhängige Prüfung mit `evaluation_allowed=False`. Er belegt keinen
  vollständigen nativen Medienlauf und keinen fachlichen Lernerfolg. Der
  neutrale Worker lieferte Endpunkte; keine reale Containerdekodierung.

| Istklasse einschließlich verbleibender Reserven | Byte | Grenze |
|---|---:|---:|
| Metadaten | 88.569 | 98.304 |
| Quellen | 246.054 | 262.144 |
| Gemeinsame Zusatzhülle | 246.054 | 393.216 |
| Verifikation | 564 | 262.144 |
| Gesamt | 335.963 | 4.194.304 |
| Lokale Qualifikationsdateien | **9.641** | **8.192** |

Restreserven insgesamt 42.900 Byte; physische Belege plus aktive Referenzen
293.063 Byte. Clientfixtures 6.764 / 8.192 Byte, Screenshots 0 / 40.960 Byte.
Fehlende Screenshots gelten nicht als Prüfleistung. Neutrale Eingangsdateien
liegen getrennt unter `sources/s2oe-player-neutral` und
`sources/s2oe-worker-neutral`; keine Benutzerdatei wurde geöffnet.

Aktuelle Quellen sind im
[Inventar](s2oe/media-player-qualification-20260911-01/inventory.json)
mit Größen und SHA-256 gebunden. Ergebnis, vollständiges Log und Bilanz:

- [Ergebnis](s2oe/media-player-qualification-20260911-01/result.json), SHA-256
  `176263f925fc2b47b7e8534fe44609e0ba471b14aa6438245b42f1d9de36f3ac`.
- [Log](s2oe/media-player-qualification-20260911-01/stderr.txt), SHA-256
  `8ad445192df7e408bbae1c4dfc96b9d2288647caba1ce84fd7f1b39e86de248b`.
- [Istbilanz](s2oe/media-player-qualification-20260911-01/final-balance.json), SHA-256
  `7c6d439e1a6c39c378408bb1bafffeda3f198e2e81c83cd765b04f6b516d3f64`.
- Inventar-SHA-256
  `06e1a4a7c62c6a0cba2b72a05da8c9cf473595de34e486cf0940dcf7513bc83f`.

Kleinste Korrekturrichtung: Browserinstallation und tatsächlich verwendete
Playwright-Version explizit gemeinsam binden; vollständige Fehler- und
Abschlussreserve prospektiv absichern. Keine Memorykorrektur begründet.
Beides wurde nach diesem Fehllauf nicht geändert. Eine finale reale
Startbindung wird nicht als qualifiziert ausgegeben.

Dieses Dokument steht außerhalb der Qualifikationsablage. Es ersetzt keinen
Pflichtbeleg; bei späterer Verwendung als Laufabhängigkeit ist es mitzuzählen.

## Freigabe und Vorbindung

Die synchronisierte Analystenfreigabe bestätigt ausdrücklich 98.304 Byte
Sitzungsmetadaten ausschließlich für `s2oe.sampled-media.v4-local-player`.
Die gemeinsame Ledgerfunktion verwendet diese Grenze bei Start, Fortschritt,
Abschluss und technischer Prüfung. Historische `b.LIMITS` bleiben bei 65.536.
Quellen 262.144, Zusatzhülle 393.216, Gesamt 4.194.304 und Verifikation
262.144 Byte bleiben unverändert. Der Decoderjob bleibt auf 512 MiB begrenzt.

Der vorhandene Workerbeleg `media-worker-qualification-20260911-01` bleibt
14/14; seine Tests werden nicht wiederholt. Decoder und Worker müssen anhand
dieses Belegs weiterhin quellengleich sein. Die damaligen elf Quelldateien
sind hashgeprüft unter `s2oe/qualified-v3-source-archive` archiviert.

Aktive Ergänzungen: `tools/_s2oe_local_player.py`, `tools/s2oe_player.html`,
`reports/start_bound_media_player.py`, `tests/test_s2oe_player.py` und
`reports/qualify_media_player_once.py`. Die neue Inventarliste enthält 14
Dateien. Die ursprünglichen `tests/test_s2oe_media.py` und
`reports/qualify_direct_media_once.py` werden nicht mehr als aktive
Laufabhängigkeiten mitgeführt: Der neue Pfad importiert oder liest sie nicht.
Historische Dateien und Nachweise bleiben vollständig erhalten. Die weiterhin
verwendeten Worker-Hilfsdateien und transitiven OC-Bindungen bleiben gezählt.

Der Player bindet genau die ausgewählte lokale Datei. Browser-Vorschau und
Decoderverarbeitung sind getrennt, nicht synchronisiert. Die Vorschau wird
beim Start angehalten und gesperrt. Keine Tab-, Kamera- oder Mikrofonaufnahme.
Das Laden der Seite öffnet kein Gate. Erst Start mit expliziter, digestgebundener
Einmalautorisierung verbraucht die Freigabe. Ohne sie bleibt Start gesperrt.
Einziger Verifikationsaufrufer ist der Playerabschluss; keine zweite äußere
Verifikation. Eine fachliche Auswertung wird hier nicht ausgeführt.

## Einmalige neutrale Qualifikation

Neue ID: `media-player-qualification-20260911-01`.
Dateigebundener Aufruf aus `workspace`:
`C:/Python314/python.exe -m reports.qualify_media_player_once`.
Der Aufrufer bindet vor dem einzigen Testprozess vollständiges Codeinventar,
Prüfnamen, Pythonumgebung, Reserven und Bilanz. Zehn neue Prüfgruppen:

1. Private Metadatengrenze und unveränderte historische Grenze, Gleichstand/Überlauf.
2. Erforderliche Autorisierung und Einmalverbrauch.
3. Unabhängig erwartete, unveränderliche Anzeigeprojektion.
4. Vollständige synthetische Bedienfolge und einmalige Verifikation.
5. Vorzeitiger Stopp und Primärfehler.
6. HTTP-Herkunft, Token und ausschließlich gebundene Mediendatei.
7. Vorschauhash und tatsächliche Vorschau-Lesemenge.
8. Browseranzeige auf Desktop/Mobilgerät mit neuem neutralem Video.
9. Ein nativer Sitzungsanschluss mit einer Formation und anschließendem Stopp.
10. Bindungshash und Ablehnung einer anderen Quelle.

Der native Fall verwendet den gebundenen neutralen Workerlieferanten,
keine reale MP4. Die synthetische vollständige Bedienfolge ist ausdrücklich
kein neuer nativer 24-Ereignis-Nachweis. Die ursprüngliche Workerqualifikation
bleibt der getrennte Nachweis dafür. Browser-JPEGs sind nur Sichtprüfungen,
keine verlustbehaftete Speicherung nativer Wahrnehmungsbelege.

| Klasse | Qualifikationsvorbindung | Maximum späterer Laufhüllen | Grenze |
|---|---:|---:|---:|
| Metadaten | 93.777 | 90.384 | 98.304 |
| Quellen | 246.054 | 246.054 | 262.144 |
| Zusatzhülle | 246.054 | 330.022 | 393.216 |
| Verifikation | 262.144 | 262.144 | 262.144 |
| Gesamt | 618.359 | 3.795.015 | 4.194.304 |

Qualifikationsreserve 8.192 Byte, Screenshots zusammen 40.960 Byte,
administrative Clientfixtures zusammen 8.192 Byte und Berichtreserve
512 Byte. Laufhüllen umfassen alle 25 Fortschrittspositionen und beide
Abschlussalternativen, zusätzlich 24.576 Byte vollständige Laufvorbereitung,
1.024 Byte Playerabschluss und 512 Byte Autorisierungsverbrauch.
Die konkrete finale reale Bindung wird dadurch nicht ersetzt.

Ein zunächst falsch zitierter administrativer Python-Aufruf scheiterte vor
Import am Syntaxparser. Der korrigierte reine Vorbilanzaufruf bestätigte die
obigen Werte. Das war kein Testaufruf und kein Zugriff auf Medienpayloads.

Status vor Test: vorbereitet, noch nicht qualifiziert. Ergebnisablage war
nicht vorhanden. Bei Fehler kein Retry; vollständige Logs bleiben erhalten.
