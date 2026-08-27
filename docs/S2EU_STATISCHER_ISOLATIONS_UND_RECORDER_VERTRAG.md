# S2-EU: Statischer Isolations- und Recordervertrag

## Status und Umfang

**STATIC_CONTRACT_BOUND_PREFLIGHT_REQUIRED**

S2-EU bindet ausschliesslich die Isolation, Aufzeichnung und spaetere
Abnahme einer dateibezogenen Plattformpruefung. Keine Implementierung,
Projektfunktionsaufrufe, Tests, Plattformaufrufe oder Rechteerhoehung.
S2-EM und die 56-Zellen-Matrix bleiben gesperrt. Keine Laufnummer.

Quellstand: `a5907a195a8994cecdc2881601d32a5ef9510c6f`.
Der JSON-Vertrag bindet den korrigierten S2-ET-Stand, den bestandenen
statischen S2-ES-Wiederholungsaudit und die unveraenderten EO/EQ-Regeln.
Er ist die normative Daten-/Fall-/Recorderbeschreibung dieses Abschnitts.

## 1. Getrennte Voraussetzungen

Vor einem spaeteren Versuch sind unabhaengig zu binden:

- eine ausdrueckliche Einmallauffreigabe fuer genau F, RunBinding und
  Versuch `s2em.002`; der verbrauchte Versuch `s2em.001` bleibt Historie;
- vorhandene, identitaetsgebundene Eltern repository/git_common/ledger/output,
  ein gemeinsames lokales NTFS-Volume und ein vorheriger Einrichtungsbeleg;
- eine Dokumentationsgrundlage fuer Daten-, Namens- und Renamehaltbarkeit,
  einschliesslich der verbleibenden Betriebssystem-/Treiber-/Hardwareannahmen;
- der aktuelle Publisherstand und separat abgenommene Recorder-, Helfer-
  und Supervisorquellen samt vollstaendigem Runtimeinventar;
- ein unabhaengiger einmaliger Aufrufverbrauch, der auch einen Abbruch
  vor dauerhafter Reservierung nicht als Wiederholungsfreigabe behandelt;
- ein vollstaendiger literaler RunBinding mit Pfaden, Originalbytes,
  Fehlerstellen und unabhaengiger Vorregistrierungsabnahme.

Diese Voraussetzungen sind hier nicht als erfuellt markiert. Insbesondere
werden keine Verzeichnisse angelegt, nativen Identitaeten erfunden oder
zukuenftigen Recorderquellen gehasht, die noch gar nicht existieren.

Fuer den isolierten Versuch wird keine positive Q aus seinem eigenen
zukuenftigen Ergebnis verlangt. Q ist erst die nachgelagerte Abnahme.
Fuer eine spaetere Studiennutzung gelten weiterhin alle G1-G5.

## 2. Isolation ohne Studienaktivierung

Der Studienowner FilePublication verlangt echte Matrixbelege. Er darf
deshalb nicht mit erfundenen Zellbefunden aktiviert werden. Beide
Freigabeflags bleiben False; kein AdmissionContext wird installiert.
TSPM-1, PPB-1, Kern, Runner, API, Snapshot und Feldpfad bleiben unveraendert.

Die spaetere Fixture verwendet ausschliesslich den korrigierten
WindowsFiles-Dateibaustein und separat abgenommene Aufzeichnungslogik.
Sie erzeugt kleine, festgelegte ASCII-Pruefbytes, keine Wahrnehmungsdaten,
Vektoren, Zustandsfunktionen, MatrixArtifacts oder echten Receipts.

Die Dateien erhalten den Praefix `s2eu.s2em.002.` in den bereits
gebundenen ledger-/output-Eltern. So bleiben die tatsaechlichen Eltern
vergleichbar, ohne einen Studiennamen oder eine Studienreservierung zu
verwenden. Andere Unterverzeichnisse oder Volumes duerfen nicht still
als gleichwertiger Plattformbeleg dienen. Alle Dateien, auch Spools,
Helferdateien und Aufzeichnungs-Staging, muessen vorab im RunBinding stehen.

Unbekannte oder bereits vorhandene Objekte sperren. Ausnahmen sind nur
die absichtlich vorbereiteten, fallgebundenen Konfliktsentinels und
der read-only Zugriff von p13 auf p01. Keine Loeschung, Migration,
Ueberschreibung, Reparatur oder automatische Wiederholung.

## 3. E0-E8-Aufzeichnung

| Phase | Isolierter Vorgang und erforderlicher Beleg |
| --- | --- |
| E0 | Quellen, Freigabe, Voraussetzungen, native Eltern und Pfadbelegung pruefen. Noch keine Fallreservierung. |
| E1 | Separate Fallreservierung exklusiv erstellen, vollstaendig schreiben, Datei-Flush und Identitaets-/Byteabgleich. |
| E2 | Eigene Zielreservierung mit denselben Pruefungen; kein Platzhalter am Ergebnisziel. |
| E3 | Genau einen inerten Plattformbeleg schreiben und flushen; kein Zellstart und kein Zustandsaufruf. |
| E4 | Feste Pruefbytes im Staging schreiben, flushen und pruefen; danach eigenen SEALED-Beleg schreiben und flushen. |
| E5 | Genau ein No-Replace-Rename am gehaltenen Staging-Handle. |
| E6 | Derselbe Datei-Handle wird geflusht; finaler Name, Identitaet und volle Bytes werden geprueft. |
| E7 | Eigener Fixture-Marker bindet die vorherigen Belege und erhaelt eigenen vollstaendigen Schreib-/Flush-/Pruefabschluss. |
| E8 | Quellen und Belege unveraendert, beide Live-Bestaetigungen vorhanden, alle Handles fehlerfrei geschlossen. |

Die E3/E4/E7-Fixtures bilden die Dateioperationen ab, nicht die fachlichen
Innenrecords des Studienpublishers. Sie sind insbesondere kein Journal
114 und keine 56-Zellen-Beweiskette. Der statische Publisheraudit bleibt
die getrennte Grundlage fuer dessen unveraenderte Logik.

## 4. Endlicher vorregistrierter Umfang

Die folgenden 13 Faelle sind nur vertraglich festgelegt, nicht zur
Implementierung oder Ausfuehrung freigegeben. Ihre Trigger, Rollen,
Reihenfolge, Fehlerherkunft und Sollzustaende stehen im JSON.

| Fall | Gegenstand | Erwarteter isolierter Endzustand |
| --- | --- | --- |
| p01 | Vollstaendiger Dateipfad, Namensbeobachtung vor/nach Rename | COMPLETED |
| p02 | Nicht passende vorab gebundene Elternidentitaet | BLOCKED_PLATFORM_PREREQUISITE |
| p03 | Exklusive Fallreservierung kollidiert | FAILED |
| p04 | Zielreservierung kollidiert nach E1 | FAILED |
| p05 | Synchronisiert erzeugtes Ziel verhindert No-Replace-Rename | ABORTED_INCOMPLETE |
| p06 | Fremder Schreibzugriff kollidiert mit gehaltenem Handle | FAILED |
| p07 | Gezielt verkuerzter Staging-Schreibvorgang | FAILED |
| p08 | Eingespeister Staging-Flushfehler | FAILED |
| p09 | Eingespeister Flushfehler nach Rename | ABORTED_INCOMPLETE |
| p10 | Gezielt verkuerzter Marker-Schreibvorgang | ABORTED_INCOMPLETE |
| p11 | Vollstaendig lesbarer Marker ohne bestaetigten Flush | ABORTED_INCOMPLETE |
| p12 | Eingespeister Handleabschlussfehler | ABORTED_INCOMPLETE |
| p13 | Lesende Einordnung von p01 ohne dessen Live-Kontext | COMPLETE_RECORDS_PRESENT_UNCONFIRMED |

p03-p06 beobachten echte API-Ablehnungen. p07-p12 pruefen gezielt
eingespeiste Fehler; die Rohspur muss Originalaufruf und eingespeiste
Rueckgabe trennen. Ein eingespeister Fehler 5 ist kein beobachteter
Rechtefehler und kein positiver Plattformbeleg. Keine ACL-Aenderung.

p13 ist eine getrennte read-only Kontextpruefung, kein zweiter
Positivlauf, kein realer Prozessabsturz und kein Stromausfallversuch.
Eine erfolgreiche Sollpruefung bedeutet OBSERVED_COMPLETE fuer den Fall,
nicht automatisch COMPLETED fuer seinen Pruefgegenstand.

Nur der genau vorregistrierte Negativausgang erlaubt den Wechsel zum
naechsten eigenstaendigen Fall. Der fehlerhafte Fall selbst bleibt
terminal. Jede andere Abweichung stoppt den Gesamtversuch; nachfolgende
Faelle sind NOT_RUN. Es gibt keinen Ersatzfall und keine Wiederholung.

## 5. Recorder und Rohbeleg

Der JSON-Vertrag legt geschlossene Datenformen fuer Header, Eintraege,
Footer, Plattformquellen, RunBinding, Fixturebelege und Aufzeichnungsabschluss
fest. Die vorhandenen S2-EQ-Formen F/B/Q/C bleiben unveraendert.

Jeder Trace bindet F, RunBinding, Quellen und Erwartungsvertrag. Alle
14 im nativen Baustein deklarierten APIs werden einschliesslich
Identitaets-, Namens-, Lese-, Positions- und Handleabschlussaufrufen
aufgezeichnet. Nur WriteFile/Flush/Rename zu protokollieren genuegt nicht.

CALL_BEGIN und CALL_RETURN erhalten eindeutige Aufruf- und logische
Handlekennungen, Actor, Phase, Pfadrolle, vollstaendige typisierte
Argumente, originale Rueckgabe und Ausgabewerte. Native Fehler werden
unmittelbar vor jedem Logging oder weiteren nativen Aufruf gesichert.
Erfolgreiche Aufrufe uebernehmen keinen veralteten LastError.

Schreib-/Lesebytes und Mengen, API-Flags, Rename-Laenge, Identitaetsbuffer
und alle relevanten Pruefergebnisse bleiben im Rohbeleg erhalten.
Eingespeiste beziehungsweise unterdrueckte Aufrufe werden nicht als
native Aufrufe ausgegeben. Weitergeleitete native Aufrufe behalten einen
eigenen Befund und verweisen auf den umgebenden Proxy-Aufruf.

Ordinal und Digestkette bestimmen die Ordnung; Uhrzeiten sind kein
Kausalitaetsbeleg. Synchronisierte Helfer verwenden benannte Barrieren,
keine Sleeps. Jede Phase hat eine belegte Folge oder NOT_REACHED.
Abgeschnittene Ausgabe, fehlende Rueckgabe, unbekannter Actor,
Digestbruch oder fehlender Footer verhindern COMPLETE.

Der Supervisor erfasst den Worker-Exitcode selbst. Der Worker darf ihn
nicht fuer sich behaupten. Recorder-I/O hat einen getrennten
Kontrollkanal; die Aufzeichnung zeichnet nicht rekursiv sich selbst auf.

## 6. Atomare Ergebnisaufzeichnung

Zuerst werden der vollstaendige Worker-Stream und dessen echtes
Prozessende erfasst. Danach werden alle Originalspuren geprueft und
unveraenderlich eingefroren. Der Supervisor veroeffentlicht die Belege
jeweils durch exklusives Staging, vollstaendiges Schreiben, eigenen
Datei-Flush, No-Replace-Rename und Post-Rename-Flush mit Bytepruefung.

B referenziert Originalspuren und Originaltranskript. Ein anschliessendes
RecordingManifest bindet B und alle Belegdateien. Ein einziger getrennter
RecordingMarker bindet das Manifest und wird selbst geschrieben,
geflusht und geprueft. Erst nach erneuter Quellenpruefung und
fehlerfreiem Schliessen darf eine lebende Abschlussbestaetigung
RECORDING_PUBLICATION_COMPLETE an den unabhaengigen Aufrufer gehen.

Dies ist keine Mehrdateitransaktion: Teildateien koennen sichtbar sein.
Erst vollstaendige Belegmenge, Marker und bestaetigter laufender Abschluss
erlauben die Annahme. Lesbarkeit allein reicht nie. Jeder Schreib-,
Flush-, Rename-, Aufzeichnungs- oder Abschlussfehler sperrt.

Der unabhaengige Aufrufer beobachtet Supervisorabschluss und dessen
tatsaechlichen Exit separat. Der Marker beweist nicht seinen eigenen
Flush. Nach Verlust dieses Vertrauenskontexts darf aus Dateien kein
operativer Abschluss rekonstruiert werden. Kein zweiter Marker, kein
Nachschreiben und kein Wiederanlauf repariert den Beleg.

File-Flush und No-Replace sind Anforderungen an die spaetere Umsetzung,
keine hier gemessenen Garantien.
[Microsoft: FlushFileBuffers](https://learn.microsoft.com/en-us/windows/win32/api/fileapi/nf-fileapi-flushfilebuffers),
[Microsoft: FILE_RENAME_INFO](https://learn.microsoft.com/en-us/windows/win32/api/winbase/ns-winbase-file_rename_info).
Die Exklusiv- und Share-Regeln folgen dem dokumentierten API-Vertrag;
ihre konkrete Anwendung bleibt zu pruefen.
[Microsoft: CreateFileW](https://learn.microsoft.com/en-us/windows/win32/api/fileapi/nf-fileapi-createfilew).

## 7. Herkunft, Abnahme und Statusprioritaet

F und RunBinding werden vor dem Versuch gebunden. Eine externe Freigabe
und Vorregistrierungsabnahme referenzieren beide, nicht umgekehrt:
kein eigener Freigabe-Eigendigestzyklus. Quellenmanifest vor F,
F vor RunBinding, Originalspuren vor B, B vor Q; kein Rueckverweis
des Manifests auf seinen spaeteren Marker.

Fehlende/nicht passende Voraussetzungen vor Reservierung ergeben
BLOCKED_PLATFORM_PREREQUISITE. Fehler nach Reservierung vor Rename
bleiben FAILED, nach Renameversuch ABORTED_INCOMPLETE. Schema- oder
Digestfehler und nativer Fehler 5 werden nicht als Plattformabnahme
umgedeutet. Nach Kontextverlust hoechstens UNCONFIRMED.

Unvollstaendige Aufzeichnung oder gescheiterte Belegveroeffentlichung
haben Vorrang vor positiven Fallbefunden. Ein Worker-Exit 0 ist nur
bei allen vollstaendig passenden Faellen moeglich und ersetzt weder
den Supervisorabschluss noch eine nachgelagerte Abnahme.

Q wird ausschliesslich im unabhaengigen statischen Review gebildet:
Originalspuren gegen Vorregistrierung, echte und eingespeiste Fehler
getrennt, Quellen/Eltern/Runtime identisch, G1-G5 vollstaendig belegt.
Ein anderer Runtimebestand oder ParentSet wird nicht normalisiert.
Ohne dokumentierte G2-Grundlage bleibt Q blockiert, auch nach p01.

Es entstehen nur Plattform- und Aufzeichnungsbefunde. Keine Aussage
ueber TSPM-1-Wirksamkeit, Memory, Repraesentationsqualitaet oder Matrix.
Die spaetere gesamte Publisher-/Matrixintegration bleibt separat.

## 8. Offene Materialisierung und naechster Schritt

Der Begleitbeleg verifiziert 14 direkte Quellen, bestehende Vertrags-
digests, 20 S2-ER-Vorgaengerquellen und 21 S2-EL-Quellen. Paket-, Test-,
Tools- und Reportbaeume bleiben unveraendert. Keine Studienpfade erzeugt.

Recorder und Supervisor existieren fuer diesen Vertrag noch nicht.
Konkrete native Elternwerte, die vollstaendige spaetere Quellclosure,
RunBinding und daraus abgeleitete endliche Aufruf-/Byteobergrenzen
muessen vor Ausfuehrung literal gebunden und statisch abgenommen werden.
Diese ausdruecklichen Voraussetzungen sind keine Ausfuehrungsfreigabe.

**WEITER:** Am besten geht es jetzt mit S2-EV als rein statischem
Materialisierbarkeits- und Isolationsaudit dieses Vertrags weiter.
Er prueft insbesondere E0-E8-Abdeckung ohne Studienaktivierung,
Recorderformen, Fehlerherkunft, Digestzyklen und Abschlussbeobachtung.

Erst danach ist ueber eine separate Implementierung zu entscheiden.
S2-EM benoetigt weiterhin eine ausdrueckliche Freigabe des konkreten
Plattformversuchs. Heute bleiben alle Tests und Ausfuehrungen gesperrt.
