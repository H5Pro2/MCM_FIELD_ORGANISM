# S2-EM: Isolierter Plattform- und Veroeffentlichungspreflight

## Ergebnis

**BLOCKED_PLATFORM_PREREQUISITE**

Der einmalige Plattformversuch `s2em.001` ist vor der ersten
Publikationsfixture gestoppt. Das vorhandene Backend erreicht auf dem
lokalen NTFS-Laufwerk `C:` die Volume-Handle-Anforderung. Windows lehnt
`CreateFileW` mit Fehler **5, Zugriff verweigert**, ab. Der Prozess ist
nicht erhoeht. Der anschliessende Volume-Flush wird nicht erreicht.

Damit ist EL-B01 jetzt durch einen konkreten Plattformblocker belegt,
aber nicht geschlossen. S2-EL bleibt nicht bestanden und die
56-Zellen-Matrix bleibt gesperrt. Das ist kein Funktionsurteil ueber
TSPM-1, PPB-1 oder die Wahrnehmungsrepraesentation.

## Umfang und Quellenbindung

Quellstand: `030bb266507ec6703d51b65e163735a7b3270776`.
Ausfuehrung am 2026-08-27, 09:48:18 UTC; Windows 10.0.19045,
Python 3.14.4. Die Zeitangabe ist ein Ausfuehrungsprotokoll, keine Feldzeit.

Der neue Helfer `tools/run_s2em_platform_preflight_once.py` verwendet nur
die Python-Standardbibliothek. Aus dem gehashten Vergleichsquelltext wird
ausschliesslich die unveraenderte Dateisystemklasse `_DurableStudyStore`
per AST ausgewertet, Zeilen 2783-2885. Das Projektmodul wird nicht importiert.
Die Studie, deren Owner, Registry, Freigabe und Zustandsoperatoren werden
nicht erzeugt oder aufgerufen.

Nur die umgebenden Metadaten- und Fehlerrollen werden isoliert bereitgestellt:
ein inerter Payload, kanonische JSON-Bytes, der private Pruefbereich sowie
eine Ausnahmehuelle, die den nativen Fehlercode unmittelbar festhaelt.
Die Windows-Funktionen im geprueften Konstruktor sind echt, keine Doubles.
Dies prueft den Backendzugriff, nicht den gesamten Matrixpublisher.

Vorgesehen war ausschliesslich `.git/s2em-platform-preflight-001` mit
eigener Kennung `s2em.platform.001`. Wegen des fruehen Abbruchs wurde
auch dieser Scratch-Bereich nicht angelegt. Die reale Studienreservierung,
ihre Autorisierungsdatei, Matrix-Staging und Matrix-Ergebnisdatei fehlen
vor und nach dem Versuch unveraendert.

## Beobachtungen

| Pruefung | Befund |
| --- | --- |
| P0: lokales festes NTFS-Volume, Handle, Flush | BLOCKED: ungueltiger Volume-Handle, nativer Fehler 5 |
| P1: exklusive vollstaendige Dateierzeugung | NOT_RUN |
| P2: No-Replace-Publikation und Abschluss | NOT_RUN |
| P3: bestehendes Ziel unveraenderlich erhalten | NOT_RUN |
| P4: unvollstaendige oder nur lesbare Datei ablehnen | NOT_RUN |
| P5: kein Abschluss nach injiziertem finalem Flush-Fehler | NOT_RUN |

Der Abbruch erfolgt an Quellzeile 2821 mit der technischen Fehlerrolle
`S2DR_ATOMIC_RESULT_REQUIRED`. Der Helfer zeichnet `BackendError`,
`native_error_at_raise: 5`, `filesystem: NTFS` und
`invalid_volume_handle: true` auf. Es wurde keine Rechteerhoehung versucht,
kein anderer Backendpfad eingesetzt und kein Versuch wiederholt.

P1-P5 besitzen ausdruecklich keinen positiven oder negativen Faehigkeitsbefund.
Insbesondere sind Dateiatomaritaet und die Fehlerfaelle des vorgesehenen
Publishers mit diesem Versuch nicht abgenommen. Die Prueffolgen im Helfer
sind nur vorbereitet, nicht erfolgreich erprobt. Ein physischer Stromausfall
oder Prozessabbruch wurde ebenfalls nicht untersucht.

## Ergebnisablage

Die Diagnose hat einen vom untersuchten Publisher getrennten Recorder:
exklusive Erstellung, Datei-fsync, Bytevergleich, Umbenennung im selben
Verzeichnis ohne Ersetzen und erneuter Bytevergleich. Das Diagnoseergebnis
und sein separater Bestaetigungsbeleg wurden vollstaendig gespeichert.
Es blieb keine Diagnose-Stagingdatei zurueck.

Diese erfolgreiche Diagnoseablage ist **kein** Ersatz fuer den fehlenden
Volume-Flush-Nachweis des Matrixpublishers. Lesbarkeit und passende Digests
belegen hier Integritaet, nicht physische Haltbarkeit bei Stromausfall.

| Beleg unter `reports/` | Kanonischer Artefaktdigest |
| --- | --- |
| `s2em_platform_preflight_attempt_v1.json` | `813c305dfbdc3c6ab25b6df99f8627ea29e6a127f5c316156862309cf9861b4a` |
| `s2em_platform_preflight_v1.json` | `469df5d2bede5fa50f998dbc65f4d35b8deaa7b424a6cbbf9d071c5445f3419b` |
| `s2em_platform_preflight_publication_v1.json` | `c110cd3e13073edeeb6e285b2cd74398645692b3ab1ed517bb6023283153f22e` |

Der Helfer protokolliert seinen vorgesehenen Abbruchcode `2` und uebergibt
ihn an `SystemExit`. Das ausfuehrende PowerShell-Werkzeug meldete dagegen
den aeusseren Exit-Code `1`. Ein separat erfasster nativer Prozess-Exit-Code
liegt nicht vor; beide Angaben werden nicht gleichgesetzt. Die Ausgabe war
vollstaendig, die drei gespeicherten Belege sind read-only nachgeprueft.
Es gibt weder einen behaupteten Exit-Code `0` noch einen erfolgreichen
Plattformabschluss. Die konkrete Ablehnung ist unabhaengig von dieser
Unterscheidung durch Fehlercode, Aufrufstelle und Ergebnisdatei belegt.

## Unveraendertheit

Alle 21 in S2-EL gebundenen Dateien stimmen vor und nach dem Versuch in
ihren Rohbytehashes ueberein. Der Helfer stimmt mit seinem vor Ausfuehrung
gespeicherten Hash ueberein. Versuch, Ergebnis und Publikationsbeleg sind
digestgebunden; kanonische Digests und Ergebnis-Rohbytehash wurden erneut
nur lesend geprueft. Es wurden keine Projektmodule geladen.

Paketbaum: `4f914c42e2e70567469d3e6565276b97ee2cd55d`.
Testbaum: `79d9bfbff8fb3fd4430db4c37c4ef713f93e654d`.
Der Git-Abgleich weist keine Aenderung an bestehenden Dateien aus.

Null Tests, null Memory-Zustandsaufrufe, null Vergleichszellen.
TSPM-1, PPB-1, API, Snapshot, Produktiv- und Feldpfad bleiben unveraendert.
Das Ausfuehrungsgate bleibt `False`. Der Versuch wird weder geloescht
noch fuer einen automatischen erneuten Plattformversuch freigegeben.

## Naechster Schritt

**RUECKMELDUNG ERFORDERLICH:** S2-EN als rein statischen Entscheidungs-
und Korrekturvertrag fuer die Veroeffentlichungsgrenze freigeben.
Zu klaeren ist, wie die benoetigten Haltbarkeitsgarantien im vorgesehenen
Ausfuehrungskontext erfuellt werden koennen und welche eng begrenzten
Rechte oder Backendanpassungen dafuer ueberhaupt erforderlich waeren.
Keine automatische Administratorausfuehrung und kein stilles Weglassen
des fehlgeschlagenen Flush-Schritts.

S2-EN waere noch keine Implementierungs- oder Ausfuehrungsfreigabe.
Ein geaenderter Backendpfad benoetigt neue Quellenbindung und gesonderte
Abnahme. Erst nach belegter Plattformunterstuetzung kann S2-EL erneut
statisch abgenommen werden. Die Matrix benoetigt weiterhin eine eigene
ausdrueckliche Einmalausfuehrungsfreigabe.
