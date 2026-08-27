# S2-EZ: Statischer Recorder-Korrekturvertrag

## Status und Grenze

**STATIC_CORRECTION_CONTRACT_BOUND_CODE_AUDIT_REQUIRED**

Ausgangscommit: `42634191f09c4a70fa7bb5e53738965e6e856e13`.
Dieser Vertrag bindet ausschliesslich die Korrekturen EY-B01 bis EY-B04.
Die normative JSON-Ergaenzung konkretisiert Datenformen, Originalbelege,
Abnahme und Fehlerherkunft. Sie implementiert keine dieser Regeln.

Keine Codeaenderung, Projektimporte, Zustandsfunktion, Testausfuehrung,
Plattformaufrufe, Rechteerhoehung oder Matrixzellen. Keine Laufnummer.
S2-EM und der 56-Zellen-Vergleich bleiben gesperrt. Keine Aussage ueber
Memory-Funktion, Repraesentationsqualitaet oder MCM-Feldwirkung.

## Vorrang und Quellenbindung

S2-EU bleibt die Quelle der 13 Faelle, E0-E8, Sollausgaenge, Trigger,
Originalbytes, Einmaligkeit und Abschlussregeln. S2-EW behaelt seine
133 festen Pfadplaetze, Quellen-/Verzeichnisableitung und 28 Renamekanten.
F/B/Q/C, RunBinding, TraceEntry, FixtureRecord und Markerfelder bleiben
unveraendert. Es kommen keine APIs, Pfadrollen, Faelle oder Phasen hinzu.

Nur fuer EY-B03 hebt die ausdrueckliche S2-EZ-Freigabe das pauschale
S2-EW-Verbot einer neuen Kontroll-Datenform fuer genau
`s2ex.control-entry.v1` auf. Deren Felder und erlaubte Ereignisse werden
jetzt geschlossen gebunden. Das ist keine rueckwirkende Codeabnahme und
keine Erlaubnis weiterer Kontrollformen oder Abschlussprotokolle.

Ein kuenftiges F behaelt isolation_contract als exakten FileRef auf
S2-EW; recorder_format_contract muss exakt diesen S2-EZ-JSON-Vertrag
referenzieren. Die Fallreferenzen und expected_contract_digest bleiben
bei S2-EU. S2-EZ bindet EU/EW/EY byte- und artefaktdigestgenau. Damit
bindet der vorhandene Header.profile_digest die neue Recorderregel
ohne zusaetzliches Tracefeld. Der vorhandene private Bindingvalidator
muss diese unterschiedliche Referenzzuordnung spaeter umsetzen.

Der S2-EZ-FileRef gehoert in die vorhandene, unabhaengig abgenommene
Leseliste. Nur deren endliche source-/directory-Ableitung wird fuer
den konkreten spaeteren Aufruf neu bestimmt; kein neuer Schreibpfad.
Quellen/Vertraege -> F -> RunBinding -> externe Freigabe/Review ->
Originalspuren/B -> Q bleibt gerichtet. Heute entstehen weder ein
F/RunBinding noch native Identitaeten oder eine neue Ausfuehrungsfreigabe.

## EY-B01: Pfad und Handle getrennt

CreateFileW, GetFileAttributesW und GetDriveTypeW besitzen an Position 0
einen Pfad. Dieser wird vor dem Aufruf ausschliesslich gegen die
eindeutige S2-EW-Inventarrolle geprueft, unveraendert als UTF16LE_BASE64
aufgezeichnet und niemals an number oder eine Handletabelle uebergeben.

GetDriveTypeW bindet die kanonische directory-Rolle der Laufwerkswurzel.
GetFileAttributesW bindet die konkrete Dateipfadrolle. Beide haben
handle_id null und eine leere outputs-Liste; raw_return traegt das
Originalergebnis. CreateFileW hat im Aufrufpaar ebenfalls handle_id null;
nur sein erfolgreicher Return erzeugt einen neuen logischen Handle in
opened_handle. Fehlgeschlagene Oeffnungen erzeugen keinen Handle.

Alle uebrigen APIs binden einen bereits geoeffneten logischen Handle
mit Actor, Pfadbesitzer und aktueller Rolle. Erfolgreicher Rename wechselt
erst nach dem Return zur eindeutigen Zielrolle. Ein fehlgeschlagener
Rename aendert keine Zuordnung. Die JSON-Tabelle legt die vollstaendigen
Ausgabeslots aller 14 APIs fest; native Signaturen bleiben unveraendert.

## EY-B02: Abnahme aus Originaloperationen

Die lesende Abnahme darf keine Fixture oder Dateifunktion aufrufen.
Sie verarbeitet nur vollstaendige Originalbytes und vorgebundene
Vertrags-/Quellwerte. Ein Marker, Digest, Phasenflag oder Check-True
ersetzt niemals die zugehoerigen Originaloperationen.

Verbindliche Reihenfolge:

1. Endliche Grenzen, kanonische Datenformen, Schemaliterale und Quellbindung.
2. Digestfolge, eindeutige Callpaare und geschlossene Ereignisfelder.
3. Pfad-/Actor-/Handlezuordnung und vollstaendige typisierte API-Slots.
4. Dateiidentitaeten, Bytes, Mengen, Positionen und native Fehlerherkunft.
5. Phasenpflichten, Falltrigger, erlaubte Abbrueche und einmaliger Close.
6. Ausschliesslich daraus abgeleitete Footer-/Fallentscheidung.

Eine Phase ist nur CONFIRMED, wenn ihre im JSON gebundenen Operationen
vollstaendig, in richtiger Reihenfolge und mit passenden Originalwerten
vorliegen. Zusaetzliche Hilfsaufrufe sind nur als durch die vorhandenen
Backendroutinen begruendete Identitaets-/Lese-/Pruefschritte erlaubt und
werden ebenfalls abgenommen. Keine ungeprueften Zusatzwrites oder Renames.

E1/E2/E3/E7 erfordern jeweils Erzeugung, vollstaendiges Schreiben,
Flush und volle Byte-/Identitaetspruefung des richtigen Records.
E4 fordert Payload und Seal, E5 den einmaligen No-Replace-Rename,
E6 Flush und finalen Namen/Bytes, E8 Quellen-/Belegpruefung und Abschluesse.
E0 sowie alle Sonderabbrueche und p13 sind im JSON einzeln gebunden.

Datei- und Quellnachweise werden aus ReadFile-, Groessen-, Positions-,
Namens- und Identitaetsausgaben rekonstruiert. FixtureRecord-Felder,
Vorbelegdigestfolge und Payloads muessen exakt zum Vertrag passen.
Die Abnahme ist kein Replay der Fixture und darf fehlende Aufrufe nicht
aus dem Quelltext ergaenzen. Der aufruflose p01 aus S2-EY wird verworfen.

Bei p09/p11 gehoert die lesende Nachpruefung der vollstaendigen finalen
beziehungsweise Markerbytes in CLEANUP zum bereits beschriebenen
Lesbarkeitsgegenfall. Sie nutzt nur den gebundenen Helferpfad; kein
erneuter Write/Flush, keine Fortsetzung des gescheiterten Subjekts.
Die Lesbarkeit hebt ABORTED_INCOMPLETE nicht auf. Scheitert diese
Nachpruefung, ist der Sollfall nicht vollstaendig belegt.

## EY-B03: Geschlossene Kontroll-Datenform

ControlEntry hat genau schema_version, attempt_id, sequence, phase,
event, actor_id, previous_record_digest, fields und record_digest.
Die JSON-Ergaenzung definiert die exakten Typen und drei fields-Varianten:
CONTROL_HEADER, CALL_BEGIN und CALL_RETURN. Kein offenes fields-Objekt.

Der erste Eintrag bindet F und RunBinding; sein Vorgaengerdigest ist
der vorgebundene SourceManifest-Digest. Alle weiteren Eintraege bilden
eine lueckenlose Digestfolge. Actor ist nur der vorgebundene Supervisor.
phase bleibt das bestehende technische Literal SETUP, keine zusaetzliche
Subjektphase. Kontrollablauf und Reihenfolge folgen den Originalaufrufen,
nicht einer erfundenen E0-E8-Projektion.

Native Kontrollaufrufe unterliegen denselben API-/Pfad-/Handlepruefungen,
aber keiner Fehlerinjektion. Es gibt keine Fall-ID und keinen Beitrag
zur NativeFailure-Zaehlung eines Subjektfalls. Spool, Staging, Rename,
Post-Rename-Flush, Marker und Closereihenfolge bleiben wie in EU/EW.

Vor einem Live-Abschluss wird die vollstaendige Kontrollspur rein lesend
abgenommen. Ihr eigenes I/O bleibt nichtrekursiv: Der anschliessende
eigene Flush, Byteabgleich und Close werden nicht in dieselbe Spur
zurueckgeschrieben. Sie muessen erfolgreich zum unabhaengigen Aufrufer
zurueckkehren. Kein Footer/Flag beweist diese eigene Barriere.

Kontroll-Spool bleibt nichtfinal. Kein neuer Marker, Zeuge, Pfad oder
F/B/Q/C-Feld. Lesbare Dateien nach Fehlern bleiben unbestaetigt;
jeder Kontroll-/Publikations-/Abschlussfehler verhindert Live-Abnahme.

## EY-B04: p12 erst nach erfolgreichem Close injizieren

Der vorgesehene Proxy-CALL_BEGIN bleibt origin INJECTED; genau ein
weitergeleitetes NATIVE-Aufrufpaar referenziert ihn. Das kennzeichnet
den vorgesehenen Proxy, noch keine tatsaechlich angewendete Injektion.

Nur bei erfolgreichem nativen Close folgt INJECTION mit FALSE/5 und
der passende Proxy-CALL_RETURN. Der native Return bleibt erfolgreich;
first_injected_failure verweist auf den Proxy. Der Sollausgang bleibt
ABORTED_INCOMPLETE. Kein zweiter Close.

Bei echtem nativen Closefehler gibt es kein INJECTION-Ereignis und
keinen injected_error. Das Proxy-Aufrufpaar wird mit raw_return 0,
native_error null, injected_error null, outputs [] geschlossen. Der
bereits verknuepfte native Return traegt allein den unmittelbar
gesicherten echten Fehler, auch wenn dieser zufaellig 5 ist.
Das ist kein Erfolg: matched ist False, der Versuch stoppt,
first_injected_failure bleibt null. Der NativeFailure-Verweis wird
nach der unveraenderten Originalaufrufordnung bestimmt. Kein Retry.

Fehlt die native Rueckgabe oder scheitert das Logging, bleiben die
Belege unvollstaendig; es darf kein Return erfunden werden. Der Handle
gilt ab Closeversuch als verbraucht, unabhaengig vom Ausgang.

## Abnahme und naechster Schritt

Die vier Regeln sind jetzt auf Vertragsebene gebunden. Die vier
Implementierungsbefunde bleiben offen, bis korrigierter Code sie erfuellt.
Der angeforderte S2-EY-Wiederholungsaudit folgt rein statisch gegen
den vorhandenen Code. Bei unveraenderten Modulen darf er nicht bestehen.

Eine anschliessend notwendige private Korrekturimplementierung benoetigt
eine eigene Freigabe; Tests und Plattformlauf werden nicht mitfreigegeben.
Auch spaeter bleiben konkrete Quellen/Runtime/Eltern, endliche Limits,
unabhaengige Start-/Abschlussbeobachtung und Einmaligkeit vor Ausfuehrung
separat zu binden. Bestehende Kern-/Feldmodule bleiben unveraendert.

**WEITER:** Am besten geht es jetzt mit dem angeforderten rein statischen
S2-EY-Wiederholungsaudit gegen diesen Vertrag und den vorhandenen Code weiter.
