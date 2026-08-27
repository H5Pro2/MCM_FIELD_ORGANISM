# S2-EN: Statische Klaerung der Veroeffentlichungsgarantien

## Ergebnis

**STATIC_CLARIFIED_BACKEND_DECISION_REQUIRED**

Der aktuelle Publisher benoetigt administrativen Volume-Zugriff wegen seiner
konkreten Implementierung und der expliziten Bindung in S2-EH. Daraus folgt
nicht, dass jede atomare Ergebnisveroeffentlichung solche Rechte benoetigt.
Ein dateibezogener Weg ist technisch begruendbar. Seine vollstaendige
Gleichwertigkeit zum bestehenden Protokoll ist aber noch nicht belegt.

S2-EM bleibt `BLOCKED_PLATFORM_PREREQUISITE`, EL-B01 bleibt offen.
Keine Rechteaenderung, Codekorrektur, Wiederholung oder neue Ausfuehrung.
Insbesondere wird der fehlgeschlagene Flush nicht nachtraeglich optional.

Quellstand: `cf9b9f64948000362e345524c895fc7139c6c2eb`.
Der JSON-Begleitbeleg bindet Quellen, Vorbelege und die fuenf Antworten.
Dies ist eine statische Klaerung ohne Laufnummer, keine Plattformabnahme.

## 1. Tatsaechlicher Rechtebedarf

Der unveraenderte `_DurableStudyStore` fordert in Quellzeile 2819
`CreateFileW` fuer `\\.\C:` mit `0xC0000000` an:
`GENERIC_READ | GENERIC_WRITE`, Freigabemodus Lesen/Schreiben,
`OPEN_EXISTING`. Er schreibt keine Rohsektoren, verwendet den Handle
aber fuer volumenweite `FlushFileBuffers`-Aufrufe. Der Zugriff reicht
somit ueber die eigenen Ergebnisdateien hinaus.

Microsoft verlangt fuer direkten Volume-Zugriff administrative Rechte.
Ein nur fuer Metadaten geoeffneter Handle ist kein Ersatz fuer einen
schreibberechtigten Flush-Handle.
[Microsoft: CreateFileW, Physical Disks and Volumes](https://learn.microsoft.com/en-us/windows/win32/api/fileapi/nf-fileapi-createfilew#physical-disks-and-volumes).

`FlushFileBuffers` verlangt am Datei-Handle `GENERIC_WRITE`; der besondere
Aufruf fuer alle offenen Dateien eines Volumes verlangt administrative
Rechte. `GENERIC_READ` ist keine zusaetzliche Flush-Voraussetzung.
Nur dessen Weglassen wuerde die administrative Volume-Grenze nicht beseitigen.
[Microsoft: FlushFileBuffers](https://learn.microsoft.com/en-us/windows/win32/api/fileapi/nf-fileapi-flushfilebuffers).

Daneben braucht der konkrete Ablauf normale Rechte zum Erstellen und Lesen
der privaten Dateien und Verzeichnisse. Umbenennen verlangt Loeschrecht an
der Datei oder entsprechendes Recht im Elternverzeichnis. Ein engerer Weg
waere daher nicht rechtefrei, sondern auf die eigenen Dateien begrenzt.
[Microsoft: MoveFileExW](https://learn.microsoft.com/en-us/windows/win32/api/winbase/nf-winbase-movefileexw#remarks).

S2-EM belegt den Fehler 5 beim Volume-Open und einen nicht erhoehten Prozess.
Das ist mit der dokumentierten Rechteanforderung vereinbar. Es ist keine
vollstaendige Diagnose aller ACLs, Tokenrechte oder Sicherheitsfilter.
Weder deren Aenderung noch ein Administratorversuch wird daraus abgeleitet.

## 2. Ist der Volume-Zugriff zwingend?

**Fuer den unveraenderten Ablauf: ja.** Der Konstruktor bricht ohne Handle ab.
`write_new`, `reserve` und `publish` verwenden danach den Volume-Flush.
S2-EH K2 verlangt seine erfolgreiche Rueckkehr vor der Finalpruefung und
dem nachgelagerten terminalen Journal. Ein stiller Austausch verletzt diese
Bindung, auch wenn spaeter eine Datei lesbar waere.

**Fuer die abstrakte Funktion: nicht grundsaetzlich.** Windows bietet
dateibezogenes Flushen sowie Umbenennung am Datei-Handle. Bei
`FileRenameInfo` kann `ReplaceIfExists=False` ein vorhandenes Ziel ablehnen.
Das belegt geeignete engere Bausteine, noch keinen vollstaendigen
Absturzsicherheitsnachweis des MCM-Publikationsprotokolls.
[Microsoft: SetFileInformationByHandle](https://learn.microsoft.com/en-us/windows/win32/api/fileapi/nf-fileapi-setfileinformationbyhandle),
[Microsoft: FILE_RENAME_INFO](https://learn.microsoft.com/en-us/windows/win32/api/winbase/ns-winbase-file_rename_info).

`MOVEFILE_WRITE_THROUGH` wird als Abwarten der Bewegung auf den Datentraeger
beschrieben; seine ausdrueckliche Flush-Zusage nennt insbesondere Copy/Delete.
Daraus wird hier weder abgeleitet, dass eine Umbenennung auf demselben Volume
wirkungslos waere, noch dass dieses Flag allein Reservierung, Journal und
Terminalbeleg dauerhaft absichert.
[Microsoft: MoveFileExW, Flags](https://learn.microsoft.com/en-us/windows/win32/api/winbase/nf-winbase-movefileexw#parameters).

## 3. Unverzichtbare Garantien

Die folgenden Anforderungen stammen aus S2-EE/S2-EH, nicht aus einer
neuen Memory-Funktion. Ein spaeterer Ersatz muss jede einzeln abdecken.

| Grenze | Erforderlicher Nachweis | Was nicht ausreicht |
| --- | --- | --- |
| Exklusivitaet | vorhandene Reservierung und vorhandenes Ziel werden nicht ersetzt | vorangehender Existenztest allein |
| Dauerhafte Einmaligkeit | Reservierung ist vor jeder Zelle dauerhaft; auch leere/beschaedigte Reservierung sperrt | Prozess-ID, Lock allein oder lesbarer Marker im Cache |
| Datenvollstaendigkeit | alle Bytes, Laengen und Quell-/Owner-/Receiptbindungen stimmen | JSON parsebar oder Digest formal gueltig |
| Datenpersistenz | erfolgreiche passende Schreib-/Flush-Barriere vor Freigabe | `write`, `close` oder Ruecklesen allein |
| Metadatenpersistenz | auch Neuerzeugung, Namensbindung und benoetigte Verzeichniseintraege abgesichert | nur die Dateinutzdaten betrachten |
| Publikation | vollstaendiger Befund wird ohne Ersetzen sichtbar; kein Copy/Delete-Fallback | Ergebnisdatei mit internem `COMPLETED` |
| Abschluss | bestaetigte Publikation, Finalpruefung, danach gebundener Terminalbeleg | lesbare finale Datei nach fehlgeschlagenem Flush |
| Wiederanlauf | nur read-only Einordnung; fehlender Beleg bleibt unvollstaendig und verbraucht | nachtraegliches Flushen, Markerergaenzung oder Retry |

Windows kann Lesezugriffe aus dem Dateicache bedienen; Metadaten sind ebenfalls
zu beruecksichtigen. Deshalb prueft Ruecklesen die aktuellen Bytes, nicht
automatisch ihre Haltbarkeit nach Stromverlust.
[Microsoft: File Caching](https://learn.microsoft.com/en-us/windows/win32/fileio/file-caching).

Der untersuchte Dokumentationsstand beschreibt fuer Write-through auch
NTFS-Metadatenbehandlung, einschliesslich Umbenennungen aus der betreffenden
Anforderung. Er nennt zugleich Hardwaregrenzen. Deshalb muessen Handle,
Operation und zugehoerige Barriere zusammenpassen; weder ein beliebiger
spaeterer Dateischreibzugriff noch ein Flagname ersetzt diese Zuordnung.
[Microsoft: CreateFileW, Caching Behavior](https://learn.microsoft.com/en-us/windows/win32/api/fileapi/nf-fileapi-createfilew#caching-behavior).

Die Garantie ist auf einen korrekt arbeitenden Betriebssystem-, Dateisystem-
und Datentraegerpfad zu begrenzen. Ein API-Erfolg ist kein physischer
Stromausfalltest. Auch S2-EM hat keinen solchen Test durchgefuehrt.

### Abschlussmarker und bestehende Fehlerausnahme

S2-EH erlaubt nach einem bereits erfolgreichen Final-Flush und Inhaltsabgleich
die read-only Einordnung einer vollstaendig sichtbaren Terminalzeile, wenn
deren spaeterer Flush scheitert. Das ist kein Beleg fuer die eigene
Haltbarkeit dieser Terminalzeile. Ein spaeterer Verlust kann den Abschluss
unbestaetigt lassen; es entsteht kein Recht auf Wiederholung.

Zu unterscheiden sind damit der bestaetigte vorherige Artefakt-Flush und
die Haltbarkeit des nachgelagerten Abschlussbelegs. S2-EN aendert diese
bestehende Ausnahme nicht. Ein Alternativvertrag darf sie insbesondere
nicht als vollstaendigen Persistenznachweis fuer alle Marker ausgeben.

## 4. Fehler 5 bleibt fail-closed

Im gemessenen Fall scheitert schon der Konstruktor vor Reservierung und
Zellaufruf. Der isolierte Versuch `s2em.001` bleibt dokumentiert und wird
nicht erneut geoeffnet. Daraus wird nicht behauptet, die nie angelegte reale
Matrixreservierung sei bereits verbraucht.

Tritt ein Publikationsfehler erst nach einer realen Reservierung auf, bleibt
diese unabhaengig vom Fehlercode verbraucht. Ohne sichtbare Finaldatei kann
der Versuch `FAILED`, bei sichtbarer aber unbestaetigter Publikation
`ABORTED_INCOMPLETE` sein. Ein Fehler vor bestaetigtem Final-Flush darf
niemals ueber Lesbarkeit in `COMPLETED` umgedeutet werden.

Keine Wiederholung mit anderen Flags, kein ACL-Umschreiben, keine Privileg-
Aktivierung, keine automatische Rechteerhoehung und kein Ausweichen auf den
separaten Diagnoserecorder als angeblich gleichwertigen Publisher.

## 5. Engerer Weg und verbleibende Entscheidung

Als **einziger Vorschlag fuer eine spaetere Vertragsentscheidung** wird eine
dateibezogene NTFS-Publikation festgehalten: begrenzte private Dateirechte,
schreibberechtigte Datei-Handles, gebundene Write-through-/Flush-Barrieren
und No-Replace-Umbenennung ohne Volume-Handle. Das ist eine technische
Ableitung aus den genannten Schnittstellen, keine implementierte oder
abgenommene Alternative. Es wird keine neue konkrete Aufrufsequenz freigegeben.

Fuer Gleichwertigkeit bleiben vier zusammenhaengende Pflichten offen:

1. Dauerhafte Einmaligkeit vor dem ersten Zellstart, einschliesslich der
   Erzeugung der Reservierung und ihrer Elternverzeichnisse. Der bestehende
   `mkdir`-Marker darf nicht ohne Nachweis lediglich durch Dateiflush ersetzt
   werden. Auch vorausgesetzte Verzeichnisse benoetigen eine klare Grundlage.
2. Ein lueckenloser Metadaten- und Datenbeleg fuer die konkrete No-Replace-
   Publikation. Ein enger Datei-Handle darf keine notwendige Wirkung an
   einem anderen Verzeichniseintrag oder einer anderen Datei offenlassen.
3. Dauerhafte, quellgebundene Reihenfolge von Reservierung, Startbelegen,
   SEALED, Artefakt und Abschlussbeleg, mit expliziter Behandlung jedes
   fehlgeschlagenen Flush. Marker-Lesbarkeit ersetzt keine bestaetigte Barriere.
4. Eigene Quellen-/Planbindung und spaeter getrennt freizugebende Abnahme
   auf dem Zielrechner. Die P1-P5-NOT_RUN-Befunde aus S2-EM bleiben unveraendert.

Die Antwort auf die Gleichwertigkeitsfrage lautet daher:
**geeignete engere Plattformbausteine vorhanden; vollstaendige Protokoll-
gleichwertigkeit offen; kein direkt austauschbarer Weg freigegeben.**
Es wurde weder eine Unmoeglichkeit ohne Administratorrechte bewiesen noch
der vorhandene Rechteblocker beseitigt.

**RUECKMELDUNG ERFORDERLICH:** S2-EO als statischen Alternativvertrag fuer
diesen dateibezogenen Weg freigeben, falls er weiterverfolgt werden soll.
Dabei muss insbesondere die bisher ausdrueckliche Volume-Flush-Bindung aus
S2-EH durch nachweisbar gleichwertige, dateibezogene Garantien ersetzt werden.
Bleibt eine der vier Pflichten offen, bleibt auch dieser Weg gesperrt.
Keine Rechteerhoehung, Implementierung oder neue Plattformausfuehrung ist
damit verbunden. S2-EL und die Matrixfreigabe werden nicht vorgezogen.

## Pruefgrenze

Nur Quelllektuere, AST ohne Auswertung, read-only JSON-/Hash-/Git-Abgleich
und Microsoft-Primaerdokumentation, abgerufen am 2026-08-27.
Alle 21 S2-EL-Quellen und die S2-EM-Belegkette stimmen weiterhin.
Paket-, Test- und Helfercode sowie historische Belege werden nicht geaendert.
Keine Projektimporte, Plattformprobe, Tests, Zustandsfunktionen oder Matrixzellen.
