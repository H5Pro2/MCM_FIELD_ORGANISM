# Dateimedien: Auswahlbindung und Vorabgrenze

## Abschluss: private Budgetversion und 14/14 neutrale Prüfgruppen

`media-oc-qualification-20260911-02` ist **QUALIFIED**: genau ein Testaufruf,
14/14 bestanden, 50,014 Sekunden laut vollständigem Testprotokoll. Der frühere
Vorabstopp `-01` bleibt unverändert ein Vorabstopp mit null Tests. Seine sieben
damaligen Quelldateien sind zusätzlich unter `reports/s2oe/budget-v1-source-archive`
unverändert verfügbar; dieses Archiv ist keine aktive Laufabhängigkeit.

### Genehmigte Änderung und Bindung

Version **`s2oe.sampled-media.v2-private-budget`**, ausdrücklich nur im privaten
Medienanschluss: Quellen maximal **180.224 Byte**, gesamte Qualifikationsmetadaten
maximal **98.304 Byte**. Jede einzelne Sitzung bleibt bei **65.536 Byte**.
Gemeinsame Zusatzhülle **262.144 Byte**, Gesamt **4.194.304 Byte** und
Verifikation **262.144 Byte** bleiben unverändert. Gleiches gilt für die
24-Ereignis-Aufgabe, Halbprofil, Masken, Zeiten und sämtliche Memory-/Operationsgrenzen.

Die Grenze wird im eigenen Ledger in `tools/_s2oe_media_binding.py` sowie in
Fortschritt, Veröffentlichung und Verifikation des Medienanschlusses angewandt.
Die größere Qualifikationsgrenze wird ausschließlich im Qualifikationsaufrufer
verwendet. Das Manifest bindet die neue Schemaversion und die aktuellen
Codehashes; die Vorregistrierung nennt beide vollständigen Grenztabellen.
Historische Validatoren und Defaults wurden nicht geändert.

Innerhalb der neuen Gesamthülle wurden **8.192 Byte** für die vollständigen
Qualifikationsdateien vorgesehen, zusätzlich **512 Byte Berichtreserve**.
Diese prospektive Aufteilung ersetzt hier die vorherige 6.607-Byte-Schätzung;
sie erhöht keine Sitzungsgrenze. Die finale Rechnung zählt die beiden
Abschlussdateien vor ihrer Veröffentlichung einschließlich der Bilanzdatei
selbst. Es wurde keine neue Verpackungsmechanik eingeführt und kein Log gekürzt.

| Klasse | Vorbindung Qualifikation | Ist einschließlich Restreserven | Grenze |
|---|---:|---:|---:|
| Quellen | 178.006 | 178.006 | 180.224 |
| Metadaten | 81.926 | 60.084 | 98.304 |
| Gemeinsame Zusatzhülle | 261.974 | 224.013 | 262.144 |
| Gesamt | 3.751.764 | 1.465.597 | 4.194.304 |
| Verifikation | 262.144 | 30.368 | 262.144 |

Die separat gerechnete Sitzung liegt prospektiv bei maximal **63.622 Byte
Metadaten** (Erfolg: 63.027), damit unter 65.536. Ihr maximales Gesamtvolumen
beträgt 3.700.097 Byte. Beide Abschlussalternativen wurden über alle 25
Fortschrittspositionen geprüft. Die gemeinsame Vorreserve hat nur noch
**170 Byte Abstand** zur Grenze; weitere aktive Pflichtdateien sind deshalb
nicht automatisch mit abgedeckt.

Die tatsächlichen Qualifikationsdateien belegen **5.941 Byte**; davon sind
1.817 Byte vollständiges Testprotokoll in `stderr.txt`, `stdout.txt` ist leer.
Der ausgewiesene Istwert enthält noch **2.251 Byte** ungenutzte Dateireserve
und **512 Byte** ungenutzte Berichtreserve. Physische Belege und gezählte aktive
Referenzen zusammen: **1.462.834 Byte**. Dieser Nachtrag ist Arbeitsdokumentation
außerhalb der unveränderten Qualifikationsablage; dort wurde kein zusätzlicher
Bericht nachträglich in eine bereits abgeschlossene Dateiliste eingefügt.
Die fünf neutralen 32-Byte-Eingangsdateien unter `sources/s2oe-neutral` sind
separater Prüfinputbestand (**160 Byte**), keine Videodateien oder gespeicherten
Rezeptorpayloads. Die ausgewählte reale Videodatei wurde nicht geöffnet.

### Tatsächlich erreichte Prüfung

- Feste Auswahl und Zähler, rationale Zeitgrenzen, Ablehnung einer falschen
  30-fps-Bindung und fortlaufende Runtimezeit bei erneut beginnender Medienzeit.
- Downmix mit vorgebundener Float32-Rundung, unveränderte Eingaben,
  Hashprüfung und Erfassung bereits gelesener Bytes auch bei Hashfehlern.
- Native PyAV-Frameverkleinerung/Farbkonversion und Audioblockauswahl an
  künstlich erzeugten neutralen Frames; letzter Frame vor dem Mittelpunkt.
- Eine **native OC-Sitzung mit 24 Ereignissen, 20 Formationen, vier
  read-only Hinweisen, 7.392 Feldkontakten und acht Scanbelegen**.
  Ein unabhängiger Verifikationsaufruf bestätigt `RECORDING_COMPLETE`,
  `evaluation_allowed: true`, Baselinegleichheit und 480 Generationsslotprüfungen.
- Zwei weitere native Sitzungen: vorzeitiger Stopp und Primärfehler nach
  erfolgter Formation. Zustand und Feldwirkung bleiben beim Schließen erhalten;
  beide Abschlüsse sind `NOT_EVALUABLE`. Die zwei Fehlerbindungsprüfungen
  erfolgten read-only, ohne weitere vollständige native Verifikation.
- Gate-/Reihenfolgefehler, unveränderliche Status-/Schrittrückgaben,
  Decoder-Durchlaufwechsel und wiederholter Stopp. Innerhalb der bestehenden
  Prüfgruppe 12 zusätzlich Gleichstand und Überschreitung bei Quellen- und
  Sitzungsmetadatenlimit; die größere Qualifikationsgrenze verdeckt keine
  unzulässige Sitzung. Es blieb bei **14 Prüfgruppen**, keiner weiteren Serie.

Größte tatsächlich erzeugte native Belege in Byte: Zustand **44.778 / 98.304**,
Eingang **8.516 / 16.384**, Schritt **2.772 / 16.384**, Scan **16.705 / 32.767**,
NJ-Quellenbeleg **573 / 1.024**, Formation **1.102 / 1.536** und
Generation **590 / 1.536**. Die drei neutralen Sitzungen zusammen verarbeiteten
22 Formationen und vier Hinweise; nur die vollständige Sitzung umfasst die
gesamte geplante 24-Ereignis-Folge. Keine dieser Passzahlen ist ein realer
Video- oder Lernbefund.

### Nachweisgrenze und Belege

**Der native Sitzungsnachweis verwendet einen ausdrücklich synthetischen
Endpunktlieferanten.** Die Frame-/Audiokonversion ist separat nativ geprüft;
die Containerzugänge des Durchlauf-/Stopptests sind kontrollierte Testdoubles.
Damit wurde nicht die komplette reale MP4-Demux-/H.264-/AAC-Kette über beide
Durchläufe ausgeführt. Die Offline-Prüfung kontrolliert PTS-, Quellen-,
Payloadhash-, Zeit-, Zustands- und Entscheidungsbindungen, rekonstruiert aber
nicht unabhängig PCM/RGB aus dem Container oder die FFT/NJ-Numerik.
Eine universelle Grenze für interne FFmpeg-Heapbelegung ist ebenfalls nicht
nachgewiesen. Diese Grenzen werden durch 14/14 nicht aufgehoben.

- [Ergebnis](s2oe/media-oc-qualification-20260911-02/result.json), Datei-SHA-256:
  `caa14ac48cf47e2349eb0d7bbcca85043bace6bd6c570714c1cd8f87625c9594`.
- [Vollständige Istbilanz](s2oe/media-oc-qualification-20260911-02/final-balance.json),
  SHA-256 `364705a65142c09d63dad78c4adc69c3c0f1279e3e8a919a90b42be2e79d324e`.
- [Vorregistrierung](s2oe/media-oc-qualification-20260911-02/preregistration.json),
  SHA-256 `2f95230317848b38a0622cb21cf089e69a12df5bd102c07bb264873a234cfd03`.
- Quelleninventar-SHA-256:
  `c1f33ade45232f05b1118c21ed394790e0791f15c3a8339c41e5235a5e72d65c`.
- [Native Gesamtverifikation](s2oe/media-oc-qualification-20260911-02/native-full/verification.json),
  SHA-256 `a0578a4e0dd7bbd55cc2e21f98096e4e4ea81dcb0b2ae223e8657a8827e0a18f`.

Alle sieben aktiven Quelldateien blieben während der Qualifikation unverändert.
Gates anschließend **False**; sämtliche erzeugten nativen Sitzungen geschlossen.
Kein Retry, kein realer Videolernlauf, keine Hypothesenanwendung oder neue
Memorymechanik. HEAD weiterhin `537109994cf777f8d36cda617aafe12226806c25`
zuzüglich des dokumentierten Arbeitsstands.

**RÜCKMELDUNG ERFORDERLICH:** Der Anschluss ist im beschriebenen neutralen
Umfang qualifiziert. Eine konkrete reale Medienlaufbindung und deren separate
Freigabe stehen aus; sie dürfen nicht mit der Qualifikationsfreigabe verwechselt
werden. Es wird nichts automatisch gestartet.

## Nachtrag: direkte OC-Fassung vor Qualifikation gestoppt

Nach der gesonderten Freigabe des direkten OC-Anschlusses wurde die
OD-Bedienhülle nicht übernommen. Die **notwendige OC-Basis bleibt mit
117.707 Byte vollständig enthalten**: Inventar, aktive gemeinsame
Bindungs-/Sitzungs-/Budget-/Verifikationsdateien und deren erforderliche
historische Qualifikationsquellen. Die 142.722 Byte des zuvor verglichenen
Gedächtnislaufs enthielten zusätzlich dessen versuchsspezifische Bindungen.
Diese werden hier nicht verwendet; ihr Archiv bleibt unverändert.

Vorbereitet wurden ein eigenes Medienmanifest mit getrennten PTS-/Runtimezeiten,
der Decoder-/Auswahladapter, eine dünne OC-Sitzungsableitung mit Start,
Status, nächstem Ereignis und Stopp, die ergänzende Herkunftsverifikation sowie
14 neutrale Prüfgruppen. Historische Produktmodule wurden nicht geändert.
Die vorhandenen nativen Feld-/Memory-/Scan- und Zustandsbelegfunktionen werden
weiterverwendet. **Diese neue Fassung ist nicht qualifiziert und nicht zur
Verwendung mit der realen Datei freigegeben.**

Die erste prospektive Rechnung mit Dateireserven passte. Erst die fertig
geschriebenen Dateien und die vollständige gemeinsame neutrale Ergebnishülle
zeigen die folgenden Überschreitungen. Die frühere Reserveprüfung ist deshalb
kein bestandener Anschlussnachweis.

| Klasse | Vollständige Vorbindung | Grenze | Überschreitung |
|---|---:|---:|---:|
| Quellen, auch für die geplante Sitzung | 175.215 | 174.080 | **1.135** |
| Metadaten der gesamten neutralen Qualifikation | 80.251 | 65.536 | **14.715** |
| Gemeinsame Zusatzhülle | 259.183 | 262.144 | keine |
| Gesamt, neutrale Qualifikation | 3.747.298 | 4.194.304 | keine |
| Verifikationsreserve | 262.144 | 262.144 | keine |

Die geplante einzelne Sitzung bleibt in der Metadaten-Vorrechnung bei maximal
62.037 Byte (Fehleralternative) beziehungsweise 61.442 Byte (Erfolg).
Ihr Gesamtmaximum beträgt 3.695.721 Byte. Sie scheitert in dieser Fassung
bereits an der Quellenbeleggrenze; die zusätzliche Qualifikation außerdem
am eigenen gemeinsam gezählten Metadatenumfang. Erfolgs- und Fehlerformen
einer Sitzung wurden als Alternativen über alle 25 Fortschrittspositionen
gerechnet, nicht addiert. Die **drei unterschiedlichen neutralen Prüfablagen**
werden dagegen zusammengezählt: vollständiger Erfolgsfall, früher Stopp und
Primärfehler nach Formation. Ihre tatsächlich getrennt vorgesehenen
Manifest-/Sitzungs-/Fehlerhüllen dürfen nicht aus der Bilanz verschwinden.

Die Quellenaddition ist vollständig:

| Erforderlicher neuer Beitrag | Byte |
|---|---:|
| `tools/_s2oe_media_binding.py` | 4.880 |
| `tools/_s2oe_media_decoder.py` | 9.091 |
| `tools/_s2oe_media_session.py` | 14.600 |
| `tools/_s2oe_media_verification.py` | 4.962 |
| `tests/test_s2oe_media.py` | 11.939 |
| `reports/prepare_direct_media_budget.py` | 3.769 |
| `reports/qualify_direct_media_once.py` | 7.510 |
| Neues Quelleninventar | 757 |
| Neue Beiträge zusammen | 57.508 |
| Weiter erforderliche OC-Basis | 117.707 |
| Insgesamt | **175.215** |

Die Qualifikationsvorrechnung enthält 3.229.688 Byte native Belegobergrenzen,
80.251 Byte Metadaten einschließlich 7.119 Byte Qualifikations-/Berichtreserve,
175.215 Byte Quellen und 262.144 Byte Verifikationsreserve. Es wurden weder
kleinere erwartete Zustände unterstellt noch Pflichtdateien umklassifiziert.
Diese Zahlen sind **keine gemessenen Medien-/Memoryergebnisse**.

### Erreicht und nicht erreicht

Der dateigebundene Vorstart `reports/qualify_direct_media_once.py` wurde
aufgerufen und hat vor `subprocess.run(... unittest ...)` gestoppt.
`precondition-stop.json` hält ausdrücklich **`test_calls: 0`** fest.
Die eine Testausführung in der Vorregistrierung bezeichnet nur den geplanten,
nicht den tatsächlich erreichten Umfang. Keine der 14 Gruppen wurde ausgeführt;
es gibt keinen neuen Passbefund und keine Übernahme alter Passzahlen.
Keine Aufruferdatei erzeugt, kein ausgewähltes Medium geöffnet, keine
Rezeptor-/NJ-Analyse, keine Memory-/Feldfortschreibung oder Sitzung gestartet.
Gates wurden nicht geöffnet. Keine weitere Reserve- oder Kompaktierungsrunde.

Vorbereitet, aber ungeprüft: Auswahl/Grenzzeiten, zweiter Durchlauf, native
RGB-/Audiokonversion an neutralen Frames, Downmix/Rundung, Hash-/Lesekontrolle,
native fortgesetzte Sitzung mit vier read-only Hinweisen, kontrollierter Stopp,
Primärfehler nach Formation, Code-/Profil-/Gatebindung und vollständige Hüllen.
Die vorgesehenen Decoderkontrollen ersetzen außerdem keinen späteren Nachweis
der vollständigen Containerdekodierung der realen Datei oder einer universellen
Obergrenze für interne FFmpeg-Speicherbelegung.

### Unveränderliche Vorabbelege

Verzeichnis: `reports/s2oe/media-oc-qualification-20260911-01`.
Es enthält noch keine `result.json`, Testlogs oder native Prüfgeschichte.

- `inventory.json`, 757 Byte, SHA-256
  `40bd7b458bef35af6793684f619cc546c956eda1e0798b841efb065a0657f19e`.
- `preregistration.json`, 1.936 Byte, SHA-256
  `f1f65af21805454e20eb27ca6e2a180f8b75645e7457894a544fa6f6e055cbaf`.
- `precondition-stop.json`, 944 Byte, SHA-256
  `722b9b950814f28faf7903d5eed2b74a142ab18f35bcb4b565a66ad0c83ced00`.

Der kurze Abschluss in diesem Verzeichnis bleibt innerhalb seiner
512-Byte-Berichtreserve. Dieser ausführliche Nachtrag und der Forschungsweg
sind Archiv-/Arbeitsdokumentation, keine ungezählten Laufabhängigkeiten.
Repository-HEAD weiterhin `537109994cf777f8d36cda617aafe12226806c25` plus
vorhandener Arbeitsstand und die im Inventar gebundenen neuen Dateien.

**RÜCKMELDUNG ERFORDERLICH:** Die konkret fertig gebundene Fassung passt
nicht unter beide bestehenden Grenzen. Kein benötigter Beitrag kann einfach
weggelassen werden, ohne diese Fassung oder ihre Prüfdeckung zu verändern.
Damit ist nicht bewiesen, dass jede denkbare kleinere Implementierung
unmöglich wäre. Keine Grenzerhöhung und keine weitere Optimierungsschleife
automatisch begonnen; der reale Lernlauf bleibt gesperrt.

## Vorheriger Stand: unveränderte OD-Übernahme

Stand: 11.09.2026. Bezug: Benutzerfreigabe für zwei abgetastete Durchläufe,
zehn Formationen je Durchlauf und vier Hinweise vor erneuter Formation.
HEAD: `537109994cf777f8d36cda617aafe12226806c25`, zusätzlich vorhandener
Arbeitsstand. Keine historischen Quellen oder Ergebnisdateien geändert.

**Ergebnis:** Die Operationszahlen passen. Eine unveränderte Übernahme der
aktiven OD-Bedienhülle ist mit den bisherigen vollständigen Belegobergrenzen
nicht vorab abgesichert: Ihre gemeinsame Zusatzhülle überschreitet die Grenze
um mindestens **15.034 Byte**, noch ohne neue Adapterbelege. Das ist eine
strukturelle Vorrechnung, keine gemessene Größe eines Medienlaufs und kein
Memorybefund. Die schlankere OC-Anschlussbasis ist dadurch nicht widerlegt.
Adapterimplementierung und einmalige Qualifikation wurden noch nicht gestartet.

## Unveränderte Quelle

Maßgeblich bleibt die inzwischen ausdrücklich ausgewählte lokale Datei
`C:\Users\TV\Downloads\17138816-uhd_3840_2160_30fps.mp4`, Ausschnitt `[0,5)` s.
Historisch geprüfter SHA-256:
`df0986f384e156c4dfec234e94b6f6baa3d0f8a9cfd7ba81f14aadf0313450aa`.
Quelle in dieser Vorrechnung nicht geöffnet oder erneut dekodiert.
Keine Identität mit der früheren YouTube-Quelle behauptet.
[Vorhandener Quellenbefund](LOCAL_VIDEO_ACCESS_20260911.md).

## Festgelegte Ereignisfolge

`F` bedeutet vollständige AV-Formation, `A` auditiven und `V` visuellen
read-only Hinweis. Administrative IDs: `media-event-01` bis `media-event-24`.
Keine Inhaltsrollen oder erwarteten Treffer im technischen Eingang.

| Ordinal | Durchlauf | Medienfensterstart in Sekunden | Typ |
|---|---|---|---|
| 1 bis 10 | 1 | 0; 0,5; 1; 1,5; 2; 2,5; 3; 3,5; 4; 4,5 | jeweils F |
| 11 | 2 | 0 | F |
| 12 | 2 | 0,5 | F |
| 13 | 2 | 1 | A |
| 14 | 2 | 1 | V |
| 15 | 2 | 1 | F |
| 16 bis 20 | 2 | 1,5; 2; 2,5; 3; 3,5 | jeweils F |
| 21 | 2 | 4 | A |
| 22 | 2 | 4 | V |
| 23 | 2 | 4 | F |
| 24 | 2 | 4,5 | F |

Jedes Audiofenster ist halboffen `[s,s+0,1)` mit 4.800 Samples bei 48 kHz.
Für das Bild gilt ausschließlich `max(PTS * Zeitbasis <= s+0,05)` in
Präsentationsreihenfolge. Die tatsächlichen Frame-PTS müssen später gelesen
werden; aus der nominellen Framerate werden keine beobachteten PTS erfunden.
Fehlende PTS/Zeitbasis, nicht eindeutige Framezuordnung oder fehlende
Audioabdeckung sind typisierte Anschlussfehler, kein Anlass zur Ersatzauswahl.

Die Hinweise verwenden denselben ausgewählten Medienausschnitt wie die
unmittelbar folgende Formation, aber eigene Ereignisbindungen. Audio bleibt
bei Originalbandindizes 0 bis 23; keine neue Maske. Visual bleibt bei den
bestehenden ersten 32 Kanal-/Zellpositionen im 288-Werte-Gitter. Positionen
32 bis 287 werden im RGB-Eingang vor der Hinweisrezeptoranalyse verdeckt,
nicht erst im fertigen Vektor. Das vollständige Formationsbild bleibt davon
unverändert. Audiohinweis, Visualhinweis, Formation ist die feste Reihenfolge.
Hypothesen bleiben getrennt und unangewandt.

## Getrennte Uhren

Vorgesehene neue Adapterkennung: `local-media.sampled-runtime-time.v1`.
Dies bezeichnet eine noch nicht implementierte Anschlussbindung.
Ein Auswahlbeleg muss Datei-/Streambindung, Durchlauf, Auswahlfenster,
Original-PTS mit rationaler Zeitbasis, tatsächlichen Framezeitpunkt,
Audiobereich und Runtimeereignis gemeinsam binden.

Für Ordinal `n` gilt weiterhin die vorhandene Runtimeabbildung mit `g=n-1`:
Audioindex `20*g`, Runtime-Samplefenster `[9600*g,9600*g+4800)`,
Audio-Feldzeit `[200000000*g,200000000*g+100000000)` ns,
virtuelles Runtime-Visualfenster `[6*g+2,6*g+3)`.
Die übrigen Feld-/Visualzeiten bleiben exakt `expected_times(n, kind)`.
Diese virtuellen Indizes dürfen **nicht** als originale Medienindizes gelten.
Die Quelle bleibt `30000/1001 fps` mit Zeitbasis `1/30000`, nicht native 30 fps.
Durchlauf zwei beginnt bei Ordinal 11; nur die Medienzeit springt zurück.
Runtimezeit und Memory werden nicht zurückgesetzt. Nach Ordinal 24 liegt das
gebundene Runtimeende bei 4.700.000.000 ns; es ist nicht die Medienlaufdauer.

## Operationsprüfung

Bezug: `tools/_s2ob_private_caller_binding.py`, `validate_manifest`,
`expected_times`, `bind_input` und `core_sizes`.

| Größe | Vorgesehener Umfang | Bestehende Grenze |
|---|---:|---:|
| Ereignisse | 24 | 28 |
| Formationen | 20 | 20 |
| Audiohinweise / Visualhinweise | 2 / 2 | 2 / 6 |
| Audioanalysen / NJ | 22 / 22 | 22 / 22 |
| Visuelle Analysen | 22 | aus den zulässigen Ereignissen abgeleitet |
| Scanbelege einschließlich Direktbaseline | 8 | 16 |
| Zustandsbelege einschließlich Anfang | 21 | 21 |
| Feldkontakte | 7.392 | innerhalb der gebundenen Ereignisobergrenzen |

Feldkontakte: `20*336 + 2*48 + 2*288`. Die vier Hinweise zählen selbst als
Ereignisse mit unabhängigen Feldkontakten, aber ohne Memoryfortschreibung.
20 ausgewählte AV-Stellen sind nicht gleich 20 Rezeptoraufrufe: Die Hinweise
bringen zwei Audio-/NJ- und zwei visuelle Analysen hinzu.
Decoderpakete, dekodierte Frames/Samples, ausgewählte Fenster und an MCM
übergebene Eingänge benötigen getrennte Zähler. Keine vollständige Verarbeitung
aller Bilder und Audiosamples behaupten.

## Konkrete Beleggrenze

Read-only gegen Dateigröße und SHA-256 geprüft: alle 20 Quellenreferenzen aus
`reports/s2od/terminal-basic-final-binding/common.json`, zusammen **193.210 Byte**.
Common-Datei-SHA-256:
`613a45ae6bb841d716e46d8a77bae442a7371e5d9a292263b25d396c4450a31b`.
Das referenziert den vorhandenen Anschluss, nicht dessen verbrauchte Freigabe
als neue Zulassung. Kein historischer Verifikator aufgerufen.

| Beitrag zur gemeinsamen Zusatzhülle | Maximale Bytezahl |
|---|---:|
| Aktive OD-Quellenreferenzen | 193.210 |
| 22 NJ-Quellenbelege, je 1.024 | 22.528 |
| 20 Formationsbelege, je 1.536 | 30.720 |
| 20 Generationsbelege, je 1.536 | 30.720 |
| Summe ohne neue Adapterabhängigkeiten | **277.178** |
| Unveränderte gemeinsame Grenze | **262.144** |
| Überschreitung der Vorabsicherung | **15.034** |

Das sind unveränderte Obergrenzen aus `core_sizes` und der Formbildung in
`tools/_s2oc_shared_verification.py:synthetic_forms`, keine Annahme kleiner
erwarteter Zustände. Die Klassifikation folgt
`tools/_s2oc_private_session_admission.py:ledger` und
`tools/_s2oc_shared_binding.py:ledger`; OD ändert sie nicht.

Alle 25 Präfixpositionen wurden arithmetisch betrachtet. Die erste
Überschreitung der Erfolgsform liegt nach Ereignis 19: 17 Formationen und
18 Audio-/NJ-Belege ergeben **263.866 Byte**, 1.722 Byte zu viel.
Nach Ereignis 18 sind es 259.770 Byte. Die nachfolgenden Summen lauten:
e20 267.962; e21/e22 268.986; e23 273.082; e24 277.178 Byte.
Eine solche Vorabsicherung würde vor Runtimeöffnung stoppen, nicht erst e19
als realen Fortschritt erreichen.

Erfolgs- und Fehlerabschluss sind Alternativen. Fehlpräfixschritte bleiben
native Schrittbelege, nicht Quellenbelege. Unter Ausschöpfung der bestehenden
Metadaten- und Verifikationsgrenzen ergibt die alte Hülle ohne neue
Adapteranteile insgesamt höchstens **3.717.810 Byte** für Erfolg und
**914.106 Byte** für die synthetische Fehleralternative, jeweils unter
4.194.304 Byte. Das hebt den lokalen Zusatzhüllenkonflikt nicht auf.
Eine vollständige neue Metadaten-, Decoder- und Qualifikationsbilanz liegt
noch nicht vor; diese Gesamtsummen sind daher keine fertige Laufzulassung.

## Kleinste verbleibende Richtung

Nicht die gesamte OD-Sieben-Ereignis-Bedienqualifikation ungeprüft zum neuen
Medieneingang erklären. Der qualifizierte darunterliegende OC-Sitzungspfad
ist separat vorhanden. Seine Quellenreferenzen aus
`reports/s2oc/memory-cycle-run-binding-02/common.json` wurden ebenfalls nur
auf Dateigröße/Hash geprüft: **142.722 Byte**. Mit denselben nativen Reserven
ergäben sich **226.690 Byte** gemeinsame Zusatzhülle vor neuen Abhängigkeiten.
Unter seiner unveränderten Quellenobergrenze 174.080 Byte bleiben höchstens
**31.358 Byte** für sämtliche zusätzlichen Quellen-/Test-/Herkunftsbelege.
Das ist verfügbarer rechnerischer Spielraum, noch kein Vollständigkeitsnachweis.

Ein direkter dünner Medienanschluss an OC statt einer Übernahme des
versuchsspezifischen OD-Starters könnte somit innerhalb der Grenzen liegen.
Notwendige Abhängigkeiten dürfen dabei nicht entfallen; insbesondere Decoder,
Zeitadapter, Start/Status/Stopp, unabhängige Herkunftsprüfung, Qualifikation und
Abschluss müssen vollständig neu gebunden werden. Die bestehende feste
Dateipayload-Zulassung kann nicht stillschweigend für Decoderpayloads gelten.

**Vorabstopp der direkten OD-Übernahme.** Keine Grenzen angehoben, keine
Auswahl verkürzt, keine Decoder-/Rezeptor-/NJ-/Memory-/Feldverarbeitung,
keine Tests und kein Lernlauf. Gates nicht geöffnet. Die Anschlussaufgabe
bleibt unvollständig; eine generelle Unmöglichkeit der 24 Ereignisse ist
aus diesem konkreten OD-Budgetkonflikt ausdrücklich nicht abzuleiten.
