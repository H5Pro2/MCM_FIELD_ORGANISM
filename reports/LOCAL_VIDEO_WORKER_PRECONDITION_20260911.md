# Decoderworker: Vorbereitung und konkrete Vorabüberschreitung

Auftrag: separater, OS-begrenzter Decoderworker; kein realer Medienlauf.
Stand 2026-09-11, Bezugscommit `537109994cf777f8d36cda617aafe12226806c25`.
Vorhandene Arbeitsbaumänderungen und historische Belege unverändert.

**Status: PRECONDITION_BLOCKED. Null Tests, null Workerstarts, null
Medienzugriffe. Kein Anschlussnachweis und keine neue Qualifikation.**

## Vorbereiteter Code

`tools/_s2oe_decoder_worker.py`: 16.323 Byte, SHA-256
`5b4138e6dc4cd04c40d38ba6fd657c79bd0ec3e0a63f76ac4629442cf2b33329`.
Neue, ausdrücklich unqualifizierte Vorbereitung. Die aktive Sitzung importiert
weiterhin den bisherigen Decoder; sie wurde nicht stillschweigend umgestellt.
Der bisherige reale Medienpfad bleibt gesperrt, kein Fallback auf ihn.

Der vorbereitete Anschluss verwendet einen Windows-Job und einen separaten
Pythonprozess. Der Kindprozess wartet vor Medienimport und Dateizugriff.
Der Elternprozess setzt und liest die Jobgrenzen, ordnet den Kindprozess zu
und sendet erst danach die Quellenbindung. Das Kind prüft zusätzlich seine
Zugehörigkeit zum benannten Job und dessen Grenzen. Fehler schließen den
Zugang. Der Worker erzeugt keine Feld-, Memory- oder Rezeptorzustände; die
vorhandenen Decoderimporte laden allerdings transitive Projektmodule.

Ein Shared-Memory-Platz transportiert nur das ausgewählte 4.800-Sample-
PCM-Fenster und den konvertierten RGB-Frame. Genau eine Anfrage ist offen;
Antwortnachrichten sind auf 4.096 Byte begrenzt, Antwortwarteschlange eins.
Es gibt keine vorauslaufende Medienproduktion. `cancel()` terminiert den
Job unabhängig von der Anfragesperre. Dies ist Codeabsicht, noch kein
beobachteter Nachweis korrekter Windows-Durchsetzung.

## Neues privates Ressourcenbudget

Version `s2oe.decoder-job.v1`, fest vor einer möglichen Ausführung:

| Ressource | Grenze | Bedeutung |
|---|---:|---|
| Prozess-Commit | 536.870.912 Byte | 512 MiB, Job-Process-Memory-Limit |
| Job-Commit | 536.870.912 Byte | 512 MiB, gesamter Einprozessjob |
| Aktive Prozesse im Job | 1 | Kein Decoder-Kindprozess außerhalb des Budgets |
| Gemeinsamer Übergabeplatz | 6.240.000 Byte | 19.200 PCM + 6.220.800 RGB |
| Offene Anfrage / Antwortplätze | 1 / 1 | Kein vollständiges Videopuffern |
| Steuer-/Antwortnachricht | 4.096 Byte | Keine nativen Payloads im JSON-Kanal |
| Initialisierung oder Auswahl | 30 Sekunden | Danach Abbruch, kein Retry |
| Prozessbeendigung | 5 Sekunden | Kein unbegrenztes Warten auf FFmpeg |

Begründung des neuen Commitbudgets, nicht aus Medienmessungen abgeleitet:
Ein 3.840×2.160-YUV420-Bild enthält nominal 12.441.600 Byte Bilddaten.
256 MiB werden konzeptionell für Codec-/Referenzbilder und Arbeitspuffer,
128 MiB für Interpreter, Bibliotheken und transitive Imports, 64 MiB für
Konversion und 64 MiB als sonstige Prozessreserve vorgesehen. Diese Aufteilung
ist eine Ressourcenpolitik, keine Herleitung, dass jedes zulässige MP4 damit
dekodierbar ist. Entscheidend ist die gemeinsame durchgesetzte 512-MiB-Grenze;
bei Nichtausreichen muss der Versuch ohne Anpassung enden.

Windows begrenzt damit committierten virtuellen Speicher, nicht gleichbedeutend
den Working Set, GPU-Speicher, Dateicache oder den Speicher des MCM-Elternprozesses.
Der Shared-Memory-Platz und Elternkopien sind separat benannt; daraus folgt
keine harte Gesamt-RAM-Garantie für MCM. Ein Eltern-RGB-Hinweis kann zusätzlich
eine okkludierte Framekopie benötigen. Artefaktgrenzen bleiben Beleggrenzen.

Referenz zur Betriebssystemsemantik:
[Microsoft: Extended Job Limits](https://learn.microsoft.com/en-us/windows/win32/api/winnt/ns-winnt-jobobject_extended_limit_information)
und [Basic Job Limits](https://learn.microsoft.com/en-us/windows/win32/api/winnt/ns-winnt-jobobject_basic_limit_information).
Allocation-Denial und Jobbenachrichtigung werden von einem unspezifischen
Workerfehler getrennt behandelt; ein unerwarteter Exit darf nicht allein
wegen zeitlicher Nähe als Speicherüberschreitung ausgegeben werden.

## Vorabbilanz: bereits zwingende Untergrenze überschritten

Ausgangsbasis ist die dokumentierte vollständige native Vorreserve des
qualifizierten Medienanschlusses, nicht dessen kleinere tatsächliche Fixtures.
Die folgende Addition zählt die neue Pflichtquelldatei genau einmal.

| Klasse | Bisherige Vorreserve | Neuer Worker | Mindestens | Grenze | Überschreitung |
|---|---:|---:|---:|---:|---:|
| Quellen | 178.006 | 16.323 | 194.329 | 180.224 | 14.105 |
| Gemeinsame Zusatzhülle | 261.974 | 16.323 | 278.297 | 262.144 | 16.153 |
| Gesamt | 3.700.097 | 16.323 | 3.716.420 | 4.194.304 | keine allein aus dieser Addition |

Die gemeinsame Zusatzhülle enthält unverändert 22.528 Byte NJ-, 30.720 Byte
Formations- und 30.720 Byte Generationsreserve. Keine Umklassifizierung,
Kürzung oder ungefragte Erweiterung. Der übergeordnete Gesamtspielraum
kompensiert die eigenständige Zusatzhüllengrenze nicht.

**Noch nicht in dieser Untergrenze:** geänderter Sitzungscode und dessen
Inventar, neue Prüf-/Aufrufdateien, Qualifikations- und Quellenzulassung,
Ressourcenprotokolle, neue gemeinsame Laufbindung, dieser gegebenenfalls
referenzierte Befund und zusätzliche Abschlussdiagnostik. Daher keine
vollständige passfähige Laufbilanz behauptet. Die bisherigen 63.027 Byte
Erfolgsmetadaten beziehungsweise 63.622 Byte Fehlermetadaten können nicht
unverändert als Obergrenze des erweiterten Anschlusses verwendet werden.
Erfolgs- und Fehlerabschluss bleiben Alternativen, nicht eine Summierung.

## Noch erforderliche Integration und Prüfdeckung

Nach einer tragfähigen administrativen Bindung sind mindestens erforderlich:

- `Session.stop()` in `_s2oe_media_session.py` muss zuerst den Worker
  abbrechen können, obwohl `process()` die Sitzungssperre hält. Ein bloßer
  Importtausch genügt nicht. Genau ein Primärfehlerabschluss, Feld und Memory
  ohne Rollback, danach kein zweiter Abschluss durch Stop/Close.
- Workerfehler, Jobbenachrichtigung, Zeitüberschreitung und Kanalabbruch
  unterscheiden; Jobspitzen und Cleanupbefunde in die vorhandene Medienhülle
  und unabhängige Verifikation aufnehmen.
- Nach abruptem Kill sind die zuletzt übertragenen Lesezähler nur ein
  bestätigter Präfix, nicht zwingend die tatsächlich insgesamt gelesenen
  Bytes. Dieser Unterschied ist im Entwurf markiert. Für eine vollständige
  reale Ist-Lesebilanz fehlt noch ein ausfallsicherer Zähleranschluss.
- Neutrale Tests: Jobmitgliedschaft und aktive Grenzen vor Dateizugriff;
  verweigerte Einrichtung; kontrollierte Überlast mit OS-Beleg; blockierter
  Worker und Timeout; ein Übergabeplatz und ungültige Antwortgrößen;
  Stop während Auswahl; Primärfehler nach Formation und einmaliger Abschluss.
  Diese Tests wurden weder implementiert noch ausgeführt; keine historischen
  Passzahlen hierfür übernommen.

Wegen der bereits belegten Überschreitung wurde die qualifizierte aktive
Sitzung nicht geändert und keine Testfreigabe verbraucht. Die neue Datei
bleibt Vorbereitung; sie ist kein nutzbarer oder zugelassener Decoderpfad.

## Reale Laufbindung bleibt gesperrt

Die Quelle, zwei Durchläufe, 24 Ereignisse und vorgesehene unbenutzte ID aus
`LOCAL_VIDEO_RUN_BINDING_BLOCKER_20260911.md` bleiben unverändert. Kein
Ergebnisverzeichnis und kein startfähiges `common.json` veröffentlicht.
Browserplayer und versuchsspezifischer autorisierter Starter fehlen weiterhin.
Die Python-API ist kein fertiger Benutzerzugang.

**RÜCKMELDUNG ERFORDERLICH:** Der Ressourcenanschluss ist fachlich freigegeben,
passt mit seinem vorbereiteten Code aber bereits ohne neue Prüfbelege nicht
in die unveränderten administrativen Grenzen. Erforderlich ist eine konkrete
Budget-/Abhängigkeitsentscheidung für den vollständigen Anschluss, keine
weitere Decoder-RAM-Erhöhung oder Wiederholung vorhandener Qualifikationen.
