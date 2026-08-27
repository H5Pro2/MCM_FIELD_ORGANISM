# S2-ER: Private Implementierung des dateibezogenen Veroeffentlichungswegs

## Status

**PRIVATE_IMPLEMENTATION_PRESENT_STATIC_AUDIT_REQUIRED**

S2-ER implementiert den privaten S2-EO/S2-EQ-Pfad nach bestandenem
S2-EP-Wiederholungsaudit. Der Code wurde ausschliesslich statisch gelesen,
als AST geprueft und ohne Auswertung kompiliert. Es wurde kein Modul
importiert, kein Test ausgefuehrt und keine Windows-Operation aufgerufen.

Ausgangscommit: `eb6ba53d95df1b1cd2152670e4d1499539df6462`.
Keine Laufnummer, keine S2-EM-Wiederholung, keine Matrixzelle und keine
fachliche Ergebnisentscheidung. Implementierung ist nicht Plattformabnahme.

## 1. Geaenderter Umfang

Genau drei neue private Module:

| Datei | Aufgabe |
| --- | --- |
| `mcm_field_organism/_s2er_publication_records.py` | S2-EQ-Feldkatalog, kanonische Records, Digest-/Quell-/Plattformbeleg-Relationen. |
| `mcm_field_organism/_s2er_windows_files.py` | Ausschliesslich dateibezogene native Handles, exklusive Erstellung, Schreiben, Flush, Rename und Abschluss. |
| `mcm_field_organism/_s2er_file_publication.py` | Privater Owner fuer E0-E8, Reservierungen, geordnete Belege und Abschlussmarker. |

Alle bestehenden Implementierungs- und Testdateien bleiben unveraendert.
Insbesondere keine Aenderung an TSPM-1, PPB-1, Vergleichscode, Comparator,
oeffentlichen Exports, API, Snapshot oder Feldpfad. Kein bestehender Runner
wird auf den neuen Publisher umgeleitet. Die zwei weiteren neuen Dateien
sind dieses Dokument und sein JSON-Beleg.

## 2. Daten- und Herkunftsbindung

Die private Recordvalidierung liest ausschliesslich die digestgebundenen
S2-EO/S2-EQ-Vertraege. Sie uebernimmt deren 21 Datenformen, acht privaten
Recordschemas, Literale, Typgrenzen und Eigendigestverfahren. Der vorhandene
S2EFRecord-Katalog wird nicht erweitert.

Der Owner erhaelt eine unveraenderliche kanonische Bytehuelle fuer
S/P/A/W/U/F/B/Q/C. Private Payloads werden als Wertkopien validiert.
P und A bleiben die bestehenden Innenrecords; W/U, T und M binden die
zusaetzlichen Publikationsrollen. Die 19 Markerfelder bleiben unveraendert.

Plattformzulassung verlangt die F/B/Q/C-Relationen, dieselben Quellen,
Host-/Runtime-/Volume-/Elternwerte, vollstaendige Fall- und Gatezuordnung,
Exit-Code 0, vollstaendige Aufzeichnung sowie die unabhaengig abgenommenen
Original- und Reviewdateien. NOT_RUN und fremde Studien-/Zellkennungen
sind nicht als isolierter Plattformbefund zulaessig.

Ein privater ContextVar hat als Vorgabe eine leere unveraenderliche
Zulassungsmenge. Der Publisher nimmt keinen Vertrauensanker als
Payloadfeld oder frei uebergebene Callback-Abnahme an und installiert
keinen Kontext selbst. Es gibt keine Registrierungsschnittstelle.

**Kein AdmissionContext ist installiert.** Ein spaeterer Bootstrap darf
ausschliesslich durch einen separat abgenommenen vertrauenswuerdigen Host
erfolgen, ohne den bereits gebundenen Quellstand umzuschreiben.
Direktes Manipulieren privater Python-Objekte liegt ausserhalb der bereits
benannten Vertrauensgrenze. Die externe inhaltliche Abnahme der konkreten
Rohspurform wird nicht durch Hashgleichheit oder einen neuen Parser fuer
noch ungebundene Formate ersetzt.

## 3. Dateipfad und Atomaritaetsgrenze

Die Windows-Funktionen werden erst bei expliziter spaeterer Konstruktion
gebunden. Import erzeugt keinen Datei- oder Volume-Handle.

Eltern und ihre Vorfahren werden als bestehende Verzeichnisse am Handle
gebunden und gegen Umbenennung/Austausch gehalten. Native Dateitypen,
FILE_ID_INFO, Dateisystem, kanonischer Handlepfad und nicht
case-sensitive Namensraeume werden geprueft. Quellen werden schreib- und
loeschgesperrt gelesen und bis zum Abschluss gehalten.

Die beiden Reservierungen sind exklusive Dateien an den S2-EO-Orten.
Am finalen Ziel entsteht kein Platzhalter. Zusaetzlich verhindert eine
prozesslokale Einmalgrenze den erneuten Versuch mit einem frischen Owner
nach einem fehlgeschlagenen E0/E1. Diese Grenze ersetzt keine dauerhafte
Reservierung und keine unabhaengige Einmallauffreigabe.

Schreibanforderungen werden vor dem ersten WriteFile aus den vollstaendigen
kanonischen Bytes in endliche Abschnitte von maximal 1 MiB zerlegt.
Jede Anforderung muss vollstaendig zurueckkehren; Short Write ist terminal.
Darauf folgen der Datei-Flush und der vollstaendige Byte-/Identitaetsabgleich.
Dies ist eine technische I/O-Aufteilung, keine Aenderung des Vergleichsbudgets.

Staging bleibt bis nach genau einem FileRenameInfo-Aufruf mit
ReplaceIfExists=False am selben Handle. Danach erfolgen erneuter Datei-Flush,
Namens-/Identitaets- und vollstaendiger Ergebnisabgleich. Erst dann wird
die interne Ergebnisbarriere bestaetigt.

Der einzige Abschlussmarker enthaelt Journal 114 nach SEALED 113.
Er bekommt eigene Neuerzeugung, vollstaendiges Schreiben, eigenen Flush
und Inhaltspruefung. Erst E8 nach erneuter Quell-/Belegpruefung und
fehlerfreiem Handleabschluss liefert COMPLETED.

Ein Fehler beendet den Owner. Es gibt keine Loeschung, Reparatur,
Ruecknahme der Reservierung, Nachschreiben, erneuten Rename oder Flush.
Fehler beim Schliessen werden erfasst; sie koennen einen fehlenden
Abschluss nicht in Erfolg umdeuten. Nach Renameversuch bleibt ein
unbestaetigter Ablauf ABORTED_INCOMPLETE. Es existiert kein Restore-
oder Resume-Pfad, der aus lesbaren Dateien einen operativen Abschluss bildet.

## 4. Grenze zur Vergleichsausfuehrung

`begin`, `start_cell`, `record_cell` und `finish` sind private
Integrationspunkte, keine neue Runner-API. Der Publisher erstellt keine
S2DRCellOwner und ruft weder consume_once noch Bildungs-/Probeoperatoren auf.

Ein spaeter separat angebundener Runner muss einen tatsaechlich
abgeschlossenen Owner und dessen Ergebnis liefern. Herkunft, Receipt,
Ergebnis und bereits persistierter Start werden vor Belegschreiben
relational geprueft. Unveraenderliche Bytebelege erkennen auch spaetere
Mutation verschachtelter Resultatwerte.

Die Ergebnisabnahme nutzt vorhandene reine Validierungs- und
Comparatorprojektionen zur Kontrolle eines eingereichten MatrixArtifact.
Sie fuehrt keinen Vergleichslauf aus und fuegt keine Erfolgskriterien hinzu.
Die Auswahl dieser Wiederverwendungsstellen ist Teil des nachfolgenden
statischen Implementierungsaudits; sie ist noch kein abgenommener Anschluss.

Sowohl `_PUBLICATION_RELEASE_ENABLED` als auch das bestehende
`_EXECUTION_RELEASE_ENABLED` bleiben False. Der operative Owner prueft
beide Sperren vor jedem Einstieg. Ein isolierter spaeterer Plattformversuch
muss den nativen Dateibaustein unter eigenem Vertrag pruefen, nicht durch
eine Aktivierung des Studienowners.

## 5. Statische Belege und Grenzen

Die drei neuen Dateien bestehen AST- und Syntaxpruefung ohne exec/import.
Der statische Aufrufabgleich findet keinen Matrix-/Zustandsaufruf,
Volume-Flush, MoveFileEx-Fallback, mkdir, unlink oder Wiederanlauf.

Alle 21 S2-EL-Quelldateien stimmen weiter in Rohbytes und Git-Blobs.
Die 20 direkten Vorgangsquellen und gebundenen Vertragsartefakte sind
unveraendert. Der Testbaum ist unveraendert. Der Paketbaum erhaelt nur
die drei neuen privaten Dateien; er wird nicht als identisch ausgegeben.

Neue Quellbelege binden die Git-Blobbytes unabhaengig von spaeterer
Arbeitsbaum-Zeilenendekonvertierung. Der Beleg vermerkt zusaetzlich die
zum Implementierungszeitpunkt gelesenen Rohbytes. Laufzeit-SourceRef-
Digests behalten unveraendert ihre tatsaechliche Rohbytebedeutung.

Nicht geprueft sind native ABI-Aufrufe, Zugriffsrechte, atomare Sichtbarkeit,
Metadatenhaltbarkeit, Konkurrenzverhalten, Fehler-Injektion oder Tests.
G1-G5, S2-EM und die 56-Zellen-Matrix bleiben gesperrt.
Es gibt keine Aussage zur funktionalen Qualitaet eines Speichers.

Die native Umsetzung orientiert sich an den dokumentierten Handle-,
Pfad- und Rename-Schnittstellen, ohne deren Verhalten hier auszufuehren.
[Microsoft: GetVolumeInformationByHandleW](https://learn.microsoft.com/en-us/windows/win32/api/fileapi/nf-fileapi-getvolumeinformationbyhandlew),
[Microsoft: GetFinalPathNameByHandleW](https://learn.microsoft.com/en-us/windows/win32/api/fileapi/nf-fileapi-getfinalpathnamebyhandlew),
[Microsoft: FileRenameInfo](https://learn.microsoft.com/en-us/windows/win32/api/winbase/ns-winbase-file_rename_info).

## 6. Naechster Schritt

**WEITER:** S2-ES als separaten statischen Implementierungs- und
Plattformaudit durchfuehren: Daten-/Digestbindungen, unabhaengige
Zulassungsgrenze, native Handles und Rechte, E0-E8, Fehlerprioritaet,
einmalige Nutzung und Unveraendertheit der bestehenden Kernpfade.

Der Audit darf keine Tests, Plattformoperationen oder Matrixzellen starten.
Eine spaetere isolierte S2-EM-Ausfuehrung benoetigt weiterhin ihren eigenen
abgenommenen Umfang und eine neue ausdrueckliche Einmallauffreigabe.
