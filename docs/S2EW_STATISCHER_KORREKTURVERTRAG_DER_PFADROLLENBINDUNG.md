# S2-EW: Statischer Korrekturvertrag der Pfadrollenbindung

## Umfang

**STATIC_PATH_BINDING_CORRECTION_BOUND**

S2-EW korrigiert ausschliesslich EV-B01 auf Vertragsebene. Quellstand:
`5622405350776b7a98e5fd978a2e7a2a86722bbb`.
Keine Implementierung, Tests, Projektimporte, Plattformaufrufe oder
Matrixzellen. Keine Laufnummer. Bestehender Code und alte Vertraege
bleiben unveraendert.

Die normative JSON-Ergaenzung hat nur fuer die Pfadrollenbindung Vorrang.
Die 13 Faelle, E0-E8, Trigger, Fehlerherkunft, Statusprioritaeten,
Einmaligkeit und Abschlussregeln aus S2-EU bleiben unveraendert.

Das spaetere F referenziert fuer isolation_contract und
recorder_format_contract diesen JSON-Nachtrag. Dieser bindet S2-EU
byte- und artefaktdigestgenau. Fallreferenzen und
TraceHeader.expected_contract_digest bleiben an S2-EU gebunden.
F/B/Q/C und alle Tracefelder behalten ihre Formen. Die private
RunBinding-Form behaelt ihre Felder, verwendet fuer die erweiterte
Rollenmenge aber das Schemaliteral `s2ew.run-binding.v1`.
Es wird heute kein F, RunBinding oder Plattformbeleg erzeugt.

## 1. Inventar und Recorder-Rollen

BoundPath besteht weiterhin genau aus case_id, role und path.
(case_id, role) ist eindeutig. Jeder kanonische Pfad hat genau einen
Inventareintrag. Zugriffsaliase sind keine weiteren Inventareintraege.

Die 13 vorhandenen Pfadschablonen bleiben bytegleich. Subjektdateien
gelten nur fuer p01-p12, Trace-Dateien fuer p01-p13. Globale Rollen haben
case_id null. p13 besitzt keine eigenen Subjektdateien.

Genau sieben Recorder-Rollen kommen hinzu:

| Rolle | Fall | Pfad unter dem gebundenen output-Elternpfad |
| --- | --- | --- |
| recorder.trace.spool | p01-p13 | s2eu.s2em.002.<case_id>.trace.ndjson.spool |
| recorder.trace.stage | p01-p13 | s2eu.s2em.002.<case_id>.trace.ndjson.stage |
| recorder.transcript.spool | null | s2eu.s2em.002.worker-transcript.bin.spool |
| recorder.transcript.stage | null | s2eu.s2em.002.worker-transcript.bin.stage |
| recorder.report.stage | null | s2eu.s2em.002.platform-report.json.stage |
| recorder.manifest.stage | null | s2eu.s2em.002.recording.json.stage |
| recorder.control.spool | null | s2eu.s2em.002.control.ndjson.spool |

Das ergibt 31 zusaetzliche, insgesamt 133 Schreib-/Zielpfadplaetze.
Dies zaehlt nur Namen, keine erzeugten Dateien oder Prueffaelle.
Nicht erreichte Schritte erzeugen ihre Dateien nicht automatisch.
Ein Inventareintrag ist keine dauerhafte Reservierung.

Alle Schreibpfade sind flache, feste Namen unter den bestehenden
ledger-/output-Eltern. Keine beliebigen tempfile-Pfade, Unterverzeichnisse,
alternativen Volumes, Dateiloeschungen oder Fallbacknamen.

## 2. Lesepfade und Verzeichnisse

Die endliche Menge der absichtlich gelesenen Eingabedateien muss genau aus
den zugelassenen SourceRefs und FileRefs stammen: Publisher-/Recorder-
Quellen, benoetigte Vertraege/Voraussetzungen sowie externe Freigabe und
Vorregistrierungsabnahme. Bereits zugelassene Runtime-Quellpruefungen
duerfen ihre ausdruecklich gebundenen Lesepfade beitragen. Es entsteht
dadurch keine zusaetzliche Leseberechtigung oder Backend-Domaene.

Gleiche kanonische Pfade werden zusammengefasst und nach ihren originalen
UTF-16-Codeeinheiten aufsteigend sortiert. Die Rollen source.0 bis
source.(n-1) bezeichnen genau diese endliche Liste. Keine Luecken,
fuehrenden Nullen oder zusaetzlichen freien Quellpfade.

Die Verzeichnismenge ist genau die Vereinigung der vier ParentSet-Pfade
und ihrer Vorfahren bis zur Laufwerkswurzel sowie der Eltern/Vorfahren
aller absichtlich geoeffneten Lesedateien. Gleich sortiert und dedupliziert
erhalten sie die Rollen directory.0 bis directory.(m-1).
Die vier bisherigen Parentrollen verweisen auf diese kanonischen Eintraege.

Die lexikalische Ableitung behauptet keine nativen Identitaeten.
Bei einer spaeteren Ausfuehrung gelten die unveraenderten Backendpruefungen:
ParentSet-Endpunkte muessen die vorgebundene Identitaet aufweisen,
weitere Verzeichnisse werden am ersten gueltigen Handle identifiziert,
gehalten und erneut gegen ihre erfasste Identitaet geprueft.
Keine Verzeichnisse erstellen, schreiben, flushen oder umbenennen.
Kein Volume-Handle und keine Rechteaenderung.

Die Pfadnamen von Freigabe und Review werden vor RunBinding festgelegt.
Ihre Inhalte und FileRef-Digests entstehen erst nach dessen Bindung und
gelangen nicht rueckwaerts in RunBinding. Kein Eigendigestzyklus.
Konkrete Pfade, Quellen und native Istwerte bleiben spaeter separat
zu materialisieren; der Vertrag erfindet heute keine solchen Werte.

## 3. Native Aufrufzuordnung

Dateiargumente und gehaltene Handles identifizieren genau einen
Inventareintrag. Der Pfadbesitzer wird aus diesem Eintrag ermittelt,
nicht pauschal aus TraceEntry.case_id. So kann ein p13-Ereignis einen
p01-Pfad lesen, ohne eine zweite Pfadidentitaet zu erzeugen.

CreateFileW bindet den neuen logischen Handle erst nach Erfolg.
Alle folgenden Handle-Aufrufe referenzieren dessen aktuelle Pfadrolle.
GetDriveTypeW verwendet die kanonische Rolle des abgeleiteten
Laufwerkswurzelverzeichnisses. Quell-/Verzeichnis-Hilfsaufrufe bleiben
vollstaendig aufgezeichnet. Es kommen keine Tracefelder oder nativen
API-Parameter hinzu.

Die vorhandenen Ausnahmen bleiben eng begrenzt:

- p03 und p04: Helfer und Subjekt verwenden denselben Reservierungspfad.
- p05: der Helfersentinel liegt genau am bereits gebundenen final-Pfad.
- p06: foreign_write_handle ist nur der Triggeralias fuer den fremden
  Oeffnungsversuch auf p06.case_reservation, kein eigener Dateipfad.
- p13: nur read-only Zugriff auf die gebundenen p01-Subjektdateien.

Actor und logischer Handle trennen diese Zugriffe. Parentrollen sind
ebenfalls nur Aliase, keine zusaetzlichen Verzeichnisidentitaeten.
Unbekannte oder mehrdeutige Zuordnungen sperren vor der Dateioperation.

Bei Rename behalten CALL_BEGIN und CALL_RETURN die Stagingrolle.
Ziel und Zielrolle sind durch genau eine vorgebundene Renamekante bestimmt.
Erst nach Erfolg wechselt die aktuelle Rolle desselben Handles zum Ziel;
seine native FileIdentity bleibt gleich. Bei Fehler oder Unterdrueckung
findet kein Rollenwechsel statt. Kein zweiter Renameversuch.

## 4. Lebenszyklus je Rolle

| Rollenklasse | Erzeugung und Nutzung | Flush und Abschluss |
| --- | --- | --- |
| Plattformreservierung | Supervisor, CREATE_NEW, einmal gebundene Reservierung | Vollschreiben, eigener Flush, Pruefung, einmal Close, kein Rename |
| Fall-/Zielreservierung | Worker, E1/E2; nur gebundene Sentinel-Ausnahmen | Bestehende E1/E2-Regeln; kein Rollback |
| Evidence / Seal / Fixture-Marker | Worker an E3/E4/E7 | Vollschreiben, eigener Flush, Pruefung, Close; Fehler terminal |
| Subjekt-Staging | Worker an E4, eine E5-Kante zu seinem final-Pfad | E4-Flush, nach Rename E6-Flush und Identitaets-/Bytepruefung |
| Subjekt-final | Nur Renameziel, ausser p05-Sentinel | Kein erneuter Nutzdatenschreibvorgang; E6/E8 bleiben verbindlich |
| Trace-/Transkript-Spool | Supervisor, exklusiv, geordnete Originaldaten | Vollstaendige endliche Schreibauftraege, Freeze, Flush, Bytepruefung, Close |
| Recording-Staging | Supervisor, frisches CREATE_NEW, eingefrorene Bytes | Vollschreiben, eigener Flush, Pruefung, ein No-Replace-Rename |
| Recording-final | Nur zugeordnetes Renameziel | Post-Rename-Flush, Native-/Bytepruefung, Close vor Live-Abschluss |
| Recording-Marker | Supervisor, direktes CREATE_NEW nach Manifest | Vollschreiben, eigener Flush, Pruefung, Close; keine Markerrekursion |
| Kontroll-Spool | Supervisor, exklusiver getrennter Kontrollkanal | Nach den anderen Datenpfaden eigener letzter Flush/Close; Ausgang extern beobachtet |
| Lesedatei / Verzeichnis | Bestehenden zugelassenen Pfad oeffnen | Kein Schreiben, Flush oder Rename; jeder eigene Handle einmal Close |

Streaming-Spools benutzen nicht wiederholt WindowsFiles.write_complete
auf demselben Handle. Ihre bereits in S2-EU separat vorgesehene
Recorder-I/O bleibt spaeter gesondert zu implementieren und abzunehmen.
Jeder Schreibauftrag muss vollstaendig sein; kein Short-Write-Retry.
Nach Freeze sind nur identitaetsgebundene Lesepruefungen zulaessig.

Spools werden nie in finale Belegpfade umbenannt. Recording-Staging
erhaelt die eingefrorenen Originalbytes, beziehungsweise die fertig
serialisierten B-/Manifestbytes. Die Recording-Kanten sind genau:

- recorder.trace.stage -> trace desselben Falls;
- recorder.transcript.stage -> transcript;
- recorder.report.stage -> report;
- recorder.manifest.stage -> recording_manifest.

Kein Cross-Parent-Rename und keine Ueberschreibung. Direkt geschriebene
Reservierungen und Marker sind keine umbenannten Spools.

Der Kontroll-Spool ist kein finaler Erfolgsbeleg. Er protokolliert die
anderen Recorder-Schritte, nicht rekursiv seine eigenen Schreib-/Flush-/
Close-Aufrufe. Sein eigener Abschluss und der Live-Abschluss bleiben
unabhaengig beobachtet. Keine weitere Erfolgsdatei, kein zusaetzlicher
Marker und keine Q allein aus lesbaren Kontrollbytes.

## 5. Abnahme und Fehlergrenzen

Die spaetere Inventarmenge muss exakt den Rollenfamilien, zugelassenen
Quellpfaden und abgeleiteten Verzeichnissen entsprechen. Sortierung:
case_id null zuerst, dann p01-p13, darin role nach UTF-16-Codeeinheiten.
Keine Extrafelder, doppelten Schluessel, unbekannten Rollen, kollidierenden
Schreibpfade oder Eingabe-/Ausgabeueberschneidungen. Native
Alias-/Identitaetspruefungen bleiben zusaetzlich erforderlich.

Die Sentinel-Ausnahmen gelten erst an ihren vorregistrierten Stellen.
Eine allgemeine Vorpruefung darf p03-p06 nicht vorzeitig in einen anderen
Fehlerpfad verschieben. p02 aendert weiterhin nur seine eine erwartete
Elternidentitaet, nicht Pfadrollen oder echte Eltern. p07-p12 duerfen
keine Recorder- oder Kontrollpfade treffen.

Temporare, reservierte und finale Rollen bleiben unterscheidbar.
Dateiexistenz, Rollenwechsel oder Lesbarkeit sind allein kein Abschluss.
Teilbelege bleiben verbraucht; keine Reparatur oder Wiederholung.
Statusprioritaeten, Einmaligkeit und Fehlerherkunft aus S2-EU bleiben
unveraendert. Kein neuer Plattform- oder Memory-Befund.

## Weitere Reihenfolge

Der JSON-Nachtrag bindet die geschuetzten S2-EU-Abschnitte per Digest.
Anschliessend ist S2-EV wie beauftragt erneut statisch durchzufuehren.
Erst nach bestandenem Audit kann ueber eine separate private
Implementierungsfreigabe entschieden werden. S2-EM und Matrix bleiben
gesperrt.

**WEITER:** Am besten geht es jetzt mit dem statischen
S2-EV-Wiederholungsaudit des ergaenzten Pfadrollenvertrags weiter.
