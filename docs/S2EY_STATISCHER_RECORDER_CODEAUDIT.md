# S2-EY: Statischer Recorder-Codeaudit

## Entscheidung

**STATIC_CODE_AUDIT_BLOCKED**

Gepruefter Commit: `851691596c2d02024280ed31513c82287ba38727`.
Die fuenf privaten S2-EX-Module wurden gegen S2-EU und S2-EW gelesen.
Vier konkrete Korrekturpunkte verhindern die Abnahme. S2-EX bleibt
implementiert, aber nicht ausgefuehrt und nicht als Plattformpfad abgenommen.
Der bestandene S2-EV-Vertragsaudit ersetzt keinen Codeaudit.

Keine Codekorrektur, Projektimporte, Zustandsfunktionen, Tests,
Recorder-/Plattformaufrufe, Rechteerhoehung oder Matrixzellen.
Es entstehen nur diese Auditnotiz und ihr JSON-Quellenbeleg. Keine Laufnummer.

## Blocker

### EY-B01: Pfadargument wird als Handlezahl ausgewertet (P1)

`_s2ex_recorder_native.py:152-161` behandelt nur CreateFileW gesondert.
Danach wertet `_outputs` immer `number(args[0])` aus. Bei GetDriveTypeW
und GetFileAttributesW ist dieses Argument ein kanonischer Pfad, keine
Handlezahl. `number` versucht in Zeile 33 die Konvertierung mittels int.

Der unveraenderte Backendpfad beginnt pin_parents mit GetDriveTypeW
(`_s2er_windows_files.py:126-136`). Bei spaeterer Entsperrung wuerde
deshalb bereits der erste Aufruf mit einer Laufwerkswurzel nach der
nativen Rueckgabe, aber vor CALL_RETURN, an der Konvertierung scheitern.
Supervisor.reserve und jeder Fall sind betroffen. GetFileAttributesW
besitzt denselben Fehler. Das ist eine statische Kontrollflussableitung,
kein ausgefuehrter oder beobachteter Plattformfehler.

Erforderlich ist eine separate, vertragsgetreue Ausgabebehandlung fuer
pfadbasierte APIs ohne Handleargument. Keine Aenderung der 14 APIs oder
des bestehenden WindowsFiles-Kerns.

### EY-B02: Traceabnahme belegt Pflichtoperationen nicht (P1)

`_s2ex_recorder_trace.py:163-262` prueft Digestfolge, Aufrufpaare,
Phasenmarker und einige boolesche Checks. Fuer p01 fordert der Code
aber keine einzige native Pflichtoperation: Leere Aufrufmengen erfuellen
die Bedingungen fuer fehlende Fehler, Cleanupfehler und Injektionen.

Rein symbolisches Gegenbeispiel: korrekt gebundener Header, neun geordnete
PHASE_BEGIN/PHASE_END-Paare mit True, die vier verlangten True-Checks
sources-unchanged, case-postconditions, helper.before-rename und
helper.after-rename, danach TERMINAL/COMPLETED und ein konsistenter Footer.
Diese Beschreibung enthaelt weder Reservierung noch Write/Flush/Rename
oder Close. Die aktuellen Bedingungen in Zeilen 244-248 unterscheiden
sie nicht von einem vollstaendigen p01. Es wurden keine solchen
Tracebytes erzeugt und kein Validator aufgerufen.

Zusaetzlich bindet validate_entry (`:20-59`) nicht das Schemaliteral und
nicht die vollstaendigen ereignisspezifischen Null-/Ausgaberegeln.
Eine neu gehashte unbekannte TraceEntry-Schemakennung wird nicht eigens
abgewiesen. Ein Handle-Lebenszyklus, die Zuordnung typisierter Pfadbytes
zum Inventar und die Vollstaendigkeit der nativen Ausgabeslots werden
bei der lesenden Abnahme ebenfalls nicht relational rekonstruiert.
Die Geberpruefung im NativeRecorder ersetzt diese Abnahme nicht.

`_s2ex_recorder_fixture.py:108-116` setzt case-postconditions nach wenigen
allgemeinen Pruefungen. Insbesondere werden nach dem p09-/p11-Flushfehler
die finalen beziehungsweise Markerbytes nicht noch einmal gelesen.
Der Trace darf eine solche Lesbarkeitsbeobachtung nicht aus der Absicht
oder aus einem allgemeinen True-Flag ableiten.

Der Supervisor verwendet matched in capture und publish
(`_s2ex_recorder_supervisor.py:249-251, 278-286`) zur Belegabnahme.
Deshalb ist die Luecke nicht nur ein fehlender Komfortcheck.
Vor Abnahme sind die bereits gebundenen Fall-/Phasenpflichten,
Fehlerabbrueche, vollstaendigen Datenformen und nativen Identitaeten
gegen die Originaleintraege zu pruefen. Keine neuen Erfolgsregeln oder
zusaetzlichen Faelle, sondern Umsetzung der bestehenden S2-EU-Regeln.

### EY-B03: Zusaetzliche Kontroll-Datenform ohne Vertragsbindung (P2)

`_s2ex_recorder_supervisor.py:65-111` fuehrt
`s2ex.control-entry.v1` mit frei uebergebenem fields-Objekt ein.
Der Header und die Kontrollereignisse erhalten keine geschlossene,
vertraglich gepruefte Ereignis-/Feldform oder eigene lesende Abnahme.

S2-EW global_lifecycle_rules verbietet ausdruecklich eine neue
Kontroll-Payloadform. Die neue Schemaform ist daher nicht durch die reine
Pfadrollenergaenzung gedeckt. Der benoetigte separate Kontrollkanal
selbst bleibt richtig und darf nicht mit Subjekttraces vermischt werden.

Zuerst muss eine enge statische Korrektur festlegen, wie der bereits
geforderte Kontrollkanal mit den bestehenden Daten-/Fehlerregeln
konform materialisiert wird. Kein stillschweigendes Anerkennen der
neuen Form, keine zusaetzliche Marker- oder Zeugenrekursion.

### EY-B04: p12 kennzeichnet auch echten Closefehler als Injektion (P2)

`_s2ex_recorder_native.py:207-218` ruft CloseHandle zwar einmal separat
als NATIVE auf, setzt danach aber auch bei dessen Fehlschlag eine
INJECTION und einen Proxy-CALL_RETURN mit injected_error. Der echte
Fehlercode wird in diesem Zweig als injected_error weitergereicht.

S2-EU p12 erlaubt die eingespeiste Rueckgabe FALSE/5 ausschliesslich
nach erfolgreichem nativen Close. Bei einem echten Closefehler muss
dieser den Versuch als unerwarteten nativen Fehler stoppen, ohne als
ausgefuehrte Fehlerinjektion klassifiziert zu werden.

Die getrennte native Rueckgabe bleibt im aktuellen Code erhalten und
unexpected_native verhindert den Solltreffer. Es wird hier deshalb
kein falsch positiver Gesamtabschluss behauptet. Fehlerherkunft und
first_injected_failure waeren dennoch nicht vertragsgetreu.
Korrekturziel: erfolgreiche Weiterleitung als Voraussetzung der
p12-Injektion, kein zweiter Close und kein Verlust des Originalfehlers.

## Abdeckung der 13 Faelle

Alle Zeilen bezeichnen gelesenen Code, keine ausgefuehrten Faelle.
EY-B01 blockiert den nativen Einstieg fuer alle Faelle. EY-B02 verhindert
zusaetzlich eine vollstaendige Abnahme ihrer Originalspuren.

| Fall | Statisch vorhandener Ablauf | Verbleibende Grenze |
| --- | --- | --- |
| p01 | E0-E8, zwei Reservierungen, Beleg, Staging, Seal, Rename, Flush, Marker, Close | B01/B02; kein positiver Plattformbefund |
| p02 | Nur erstes Hexzeichen der erwarteten output-Identitaet wird geaendert | B01/B02; kein nativer Identitaetstausch |
| p03 | Helfersentinel nach E0 am case_reservation-Pfad | B01/B02; Fehler 80 nicht beobachtet |
| p04 | Helfersentinel nach E1 am target_reservation-Pfad | B01/B02; Fehler 80 nicht beobachtet |
| p05 | Synchronisierter final-Sentinel nach letzter Abwesenheitspruefung | B01/B02; No-Replace-Ablehnung nicht beobachtet |
| p06 | Fremder GENERIC_WRITE/OPEN_EXISTING-Aufruf am selben Reservierungspfad | B01/B02; Sharefehler 32 nicht beobachtet |
| p07 | Weitergeleitetes N-1-Stagingwrite, keine Reparatur im Geberpfad | B01/B02; kein Short-Write-Befund |
| p08 | Unterdrueckter Stagingflush mit eingespeistem Fehler 5 | B01/B02; keine Rechteinterpretation |
| p09 | Unterdrueckter Post-Rename-Flush, kein Marker im Geberpfad | B01/B02; keine bestaetigte Lesbarkeitsbeobachtung |
| p10 | Weitergeleitetes N-1-Markerwrite | B01/B02; kein Markerflush nach Sollfehler |
| p11 | Markerwrite, unterdrueckter Markerflush | B01/B02; keine bestaetigte Lesbarkeitsbeobachtung |
| p12 | Separater nativer Close und vorgesehener Proxyfehler | B01/B02/B04; native Fehlervariante nicht korrekt klassifiziert |
| p13 | Neuer Lesekontext liest p01, liefert nur UNCONFIRMED | B01/B02; keine Wiederaufnahme oder Live-Bestaetigung |

## Erhaltene Grenzen und offene Voraussetzungen

Pfadrollen werden aus den 133 festen Plaetzen sowie den endlichen
Quell-/Verzeichnislisten gebildet. Renamekanten, p06-Triggeralias und
p13-Zugriff auf p01 sind im Geberpfad explizit getrennt. Spools werden
nicht als finale Belege umbenannt; Recorder-Staging besitzt eigene Rollen.

Der Supervisor ordnet capture vor publish an. Er wartet auf den
Worker-Exit, prueft Spools, veroeffentlicht ueber eigene Stagingdateien
und liefert LiveRecordingCompletion erst nach Datei-/Kontrollabschluss.
Abbruchpfade setzen INCOMPLETE, nicht automatisch COMPLETE bei Lesbarkeit.
Dies ist eine gelesene Struktur, keine bestaetigte Flush-/Dauergarantie.

EU/EW-/Header-/Run-/Quelldigests sind explizit gekoppelt. Die konkrete
vollstaendige Quell-/Runtime-/Actor-/Pfadbindung, native Elternidentitaet,
endliche Aufruf-/Bytegrenzen, unabhaengige Freigabe/Abnahme und
vertrauenswuerdige Startbindung bleiben wie in S2-EX separat zu erbringen.
reserve prueft bislang die Mitgliedschaft von Freigabe-/Reviewreferenzen;
capture nimmt einen Popen entgegen. Das ersetzt deren externe Herkunfts-
und Einmaligkeitsabnahme nicht. Diese bereits offengelegten Voraussetzungen
werden hier weder als implementiert noch als erfuellt ausgegeben.

Alle drei Ausfuehrungsflags bleiben False, die neue Abnahmemenge leer.
Die fuenf Module nutzen nur ihre privaten Recorderteile und den bestehenden
Dateibaustein mit reinen Recordhilfen. Die dort vorhandene lazy _core-
Funktion wird von keinem Recorderpfad aufgerufen. Keine neue Einbindung
aus API, Paketexport, Feldpfad, Tests oder Tools wurde gefunden.

30 Quellenbindungen, fuenf Syntaxbaeume, EU/EW/EX-Artefaktdigests und neun
unveraenderte EU-Abschnitte wurden statisch abgeglichen. Paket-, Test-,
Tool- und Reportbaum bleiben unveraendert; die sechs Studienpfade fehlen
weiterhin. Der JSON-Beleg bindet die genauen Quellen und Zeilen.

## Naechster Schritt

S2-EZ als eng begrenzten statischen Korrekturvertrag fuer EY-B01 bis
EY-B04 vorschlagen. Er soll diese vier Punkte schliessen, ohne die
13 Faelle, E0-E8, Erfolgsregeln oder Feldgrenzen zu erweitern.
Danach erst separat freigegebene private Korrektur und erneuter S2-EY.
Es wird heute weder eine Korrektur noch eine Ausfuehrung freigegeben.

S2-EM und die 56-Zellen-Matrix bleiben gesperrt. Kein Memory- oder
MCM-Feldbefund. Auch eine kuenftige Codeabnahme ersetzt die konkrete
Plattformvoraussetzungsbindung und ausdrueckliche Einmallauffreigabe nicht.

**WEITER:** Am besten geht es jetzt mit S2-EZ als rein statischem
Korrekturvertrag fuer die vier Recorder-Blocker weiter.
