# S2-EO: Statischer dateibezogener Veroeffentlichungsvertrag

## Status und Geltung

**STATIC_ALTERNATIVE_CONTRACT_BOUND_AUDITS_PENDING**

Dieser Vertrag bindet genau einen privaten dateibezogenen NTFS-Pfad.
Er ist keine Implementierungs-, Plattform- oder Ausfuehrungsabnahme.
S2-EM bleibt blockiert, EL-B01 offen und die 56-Zellen-Matrix gesperrt.
Der historische Versuch `s2em.001` und alle bisherigen Belege bleiben erhalten.

Quellstand: `6d360158a420dfa030ad5cbbd80ca2e9fdba94f9`.
Der JSON-Begleitbeleg bindet Quellen, Pfadrollen, Reihenfolge und Fehlerregeln.
Keine Laufnummer: nur Lektuere, AST-/JSON-/Hash-Abgleich und Dokumentation.

Normative Aussagen bedeuten hier: Eine spaetere Implementierung muss diese
Eigenschaft nachweisen oder geschlossen bleiben. Insbesondere wird die
Metadatenhaltbarkeit nicht durch eine Vertragsformulierung als gemessen ausgegeben.

## 1. Unveraenderliche Grenzen

Keine Volume-Handles, Rechteerhoehung, ACL-Aenderung, Privilegaktivierung,
Produktionsintegration oder Ausfuehrung. Keine Aenderung an TSPM-1, PPB-1,
API, Snapshot, Feldpfad, Vergleichsarmen, Budgets, Comparator oder Quellen.
Die folgenden Dateiformen sind nur fuer einen spaeter separat abgenommenen
Publisher bestimmt, nicht fuer den vorhandenen `_DurableStudyStore`.

Die feste Studien-ID `s2dr.tspm1.h1-h7.56.v1` bleibt dieselbe.
Neuer Quellstand, neuer Owner oder neuer Backendname schaffen keinen zweiten
Matrixversuch. Plattformfixtures muessen weiterhin getrennte Kennungen und
Scratch-Pfade verwenden; dieser Vertrag legt keine solchen Dateien an.

S2-EH bleibt fuer den aktuellen Code verbindlich. Fuer den kuenftigen
Alternativpfad werden seine Volume-Barrieren durch belegte Dateibarrieren
ersetzt. Seine Ausnahme fuer einen fehlgeschlagenen Terminal-Flush wird
**nicht uebernommen**: Jeder solche Fehler verhindert hier den Abschluss.
Die historische Vertragsfassung wird nicht umgeschrieben.

## 2. Vorbedingungen und Namensraum

Zulaessig sind nur vorab gebundene lokale NTFS-Pfade auf demselben Volume.
Die benoetigten Elternverzeichnisse muessen bereits vorhanden, in ihrer
Identitaet gebunden und in ihrer Haltbarkeit abgenommen sein. Der Publisher
erstellt keine Verzeichnisse. Ein blosses `exists` ersetzt diese Vorbedingung
nicht; bei fehlendem Verzeichnis oder Beleg wird vor Reservierung gestoppt.
Die Einrichtung dieser Voraussetzung ist nicht durch S2-EO freigegeben.

Der Plan bindet Repository, gemeinsamen Git-Bereich, Host, Volumeidentitaet,
Elternverzeichnisidentitaeten, kanonische Pfade, Studien-ID, ausdrueckliche
Freigabe, Quellmanifest, Vertragsdigest und die spaetere Plattformabnahme.
Umleitungen, Reparse Points, alternative Datenstroeme, mehrdeutige Namen,
Pfadaliasse und unerwartete Hardlinks sind abzulehnen. Gross-/Kleinschreibung
darf keine zweite Reservierungsidentitaet fuer denselben Zielnamen erzeugen.
Identitaeten muessen am tatsaechlichen Handle geprueft werden, nicht allein
durch Zeichenkettenvergleich vor dem Oeffnen. Elternidentitaeten bleiben
ueber den Ablauf gegen Austausch gebunden.

Die bestehenden Rollen `final`, `staging`, `durable_ledger_root` und
Autorisierung stammen aus dem validierten Plan, nicht aus freien Argumenten.
Fuer den Alternativpfad gilt folgende eindeutige Dateizuordnung:

| Rolle | Gebundener Ort |
| --- | --- |
| Studienreservierung | `durable_ledger_root / study_id`, als Datei statt als neues Verzeichnis |
| Zielreservierung | `final` mit angehaengtem `.reservation.json` |
| Staging | bestehende quellgebundene Staging-Pfadrolle, im selben Verzeichnis wie `final` |
| Ergebnis | bestehende quellgebundene `final`-Pfadrolle |
| Zell-/Journalbelege | flach unter `durable_ledger_root`, Praefix `study_id + '.'`, bestehende Belegnamen |
| Abschlussmarker / Journal 114 | `final` mit angehaengtem `.completed.json`; genau eine Datei fuer diese Rolle |

Die Studienreservierung enthaelt unveraendert den kanonischen
`AttemptReservation`-Datensatz. Ein vorhandenes Objekt an diesem Ort,
insbesondere auch ein altes Verzeichnis, eine leere Datei oder ein
beschaedigter Marker, sperrt. Es gibt keine automatische Migration.
Damit umgeht das alternative Layout nicht die alte Studien-Einmalgrenze.

Die Zielreservierung ist eine permanente Sidecar-Datei. **Am finalen Ziel
wird kein Platzhalter angelegt.** Sonst muesste die spaetere Umbenennung
das eigene Reservierungsobjekt ersetzen. Die Zielreservierung bindet
Studienreservierung, Plan, Autorisierung, Zielpfad und Elternidentitaet.
Sie sperrt denselben Zielnamen auch gegen eine andere Studien-ID.

## 3. Dateioperationen und Rechte

Exklusive Neuerzeugung erfolgt mit `CreateFileW` und `CREATE_NEW`.
Dateien werden synchron, schreibberechtigt und mit `FILE_FLAG_WRITE_THROUGH`
geoeffnet; Lesen fuer die Inhaltspruefung wird ebenfalls gebunden.
Nur der umzubenennende Staging-Handle benoetigt zusaetzliches `DELETE`-Recht.
Fremdes Schreiben und Loeschen waehrend der Bearbeitung sind durch passende
Share-Modi zu verweigern. Es gibt kein `CREATE_ALWAYS`, Truncate,
Delete-on-close, Copy/Delete-Fallback oder Wechsel auf einen anderen Pfad.

Diese Flags und Rechte beschreiben den neuen Vertrag, keine auf diesem
Rechner ausgefuehrten Operationen. Microsoft dokumentiert exklusive
Neuerzeugung und die Behandlung von Write-through samt NTFS-Metadaten;
Hardwaregrenzen bleiben zu beachten.
[Microsoft: CreateFileW](https://learn.microsoft.com/en-us/windows/win32/api/fileapi/nf-fileapi-createfilew).

Jede Datei wird vollstaendig aus ihren vorab festgelegten kanonischen Bytes
geschrieben. Die endliche Aufteilung in Schreibanforderungen und deren
Laengen steht vor dem Schreiben fest. Ein Fehler oder eine kuerzere als
angeforderte Schreibmenge stoppt sofort: kein Nachschreiben zum Reparieren,
kein erneuter Aufruf derselben fehlgeschlagenen Anforderung. Danach folgt
genau die vorgesehene Barriere und ein vollstaendiger Laengen-/Byteabgleich.

Jede Barriere ist ein erfolgreicher `FlushFileBuffers`-Aufruf auf dem Handle
der gerade betroffenen Datei. Rueckgabewert und nativer Fehler sind sofort
zu erfassen. Ein Flush auf einem anderen Handle, Python-Flush, Dateischliessen
oder Lesbarkeit darf diese Barriere nicht ersetzen. Der dokumentierte
Datei-Flush braucht Schreibrecht; kein Volume-Handle ist Bestandteil dieses
Pfads.
[Microsoft: FlushFileBuffers](https://learn.microsoft.com/en-us/windows/win32/api/fileapi/nf-fileapi-flushfilebuffers).

Fuer den Namenwechsel ist genau ein
`SetFileInformationByHandle(..., FileRenameInfo, ...)` am weiterhin geoeffneten
Staging-Handle vorgesehen, mit `ReplaceIfExists=False` und vollstaendig
gebundenem Ziel auf demselben Volume. Kein zweiter Rename bei Ablehnung.
Danach wird derselbe Datei-Handle erneut geflusht und seine Identitaet am
finalen Namen geprueft. Die verlangte atomare Sichtbarkeit und Haltbarkeit
dieser konkreten Kombination sind eigenstaendige Plattform-Abnahmepflichten.
[Microsoft: SetFileInformationByHandle](https://learn.microsoft.com/en-us/windows/win32/api/fileapi/nf-fileapi-setfileinformationbyhandle),
[Microsoft: FILE_RENAME_INFO](https://learn.microsoft.com/en-us/windows/win32/api/winbase/ns-winbase-file_rename_info).

## 4. Verbindliche Reihenfolge

Jeder Schritt setzt alle vorherigen erfolgreichen Schritte voraus.
Ein fehlender Beleg ist ein Fehler, kein unbekanntes positives Ergebnis.

| Schritt | Aktion und Freigabegrenze |
| --- | --- |
| E0 | Quellen, Plan, Autorisierung, Plattformbeleg, Elternidentitaeten und Pfadbelegung pruefen. Keine pauschale Rechteprobe ersetzt die Fehlerpruefung jeder spaeteren Operation. |
| E1 | Studienreservierung exklusiv erstellen, vollstaendig schreiben, Datei-Flush, Identitaets-/Bytepruefung. Ab Erzeugung keine automatische Freigabe oder Loeschung. |
| E2 | Zielreservierung exklusiv erstellen, vollstaendig schreiben, Datei-Flush und pruefen. Scheitert sie, bleibt die Studienreservierung verbraucht; kein Rollback. |
| E3 | Beide Reservierungen und ihre Namenshaltbarkeit bestaetigen. Erst danach duerfte eine separat autorisierte Zelle beginnen. Jeder Startbeleg und jede Journalzeile erhaelt dieselbe vollstaendige Schreib-/Flush-Pruefung. S2-EO fuehrt keine Zelle aus. |
| E4 | Vollstaendigen, gueltigen Vergleichsbeleg im exklusiven Staging schreiben, Datei-Flush, volle Byte-/Quell-/Receiptpruefung. Danach SEALED als Journal 113 dauerhaft schreiben und pruefen. |
| E5 | Genau ein atomarer No-Replace-Rename. Fremdes oder eigenes vorhandenes Ziel fuehrt zum Stopp, nicht zum Ersetzen. |
| E6 | Datei-Flush am weitergehaltenen Ergebnis-Handle nach Rename; finalen Namen, Volume-/Dateiidentitaet, Bytezahl, Bytes und volle Belegkette pruefen. Erst dann intern `final_barrier_confirmed` setzen. |
| E7 | Abschlussmarker als Journal 114 exklusiv schreiben; vollstaendige Bytes, eigener Datei-Flush, anschliessend Inhalts-/Identitaetspruefung. Erst dann intern `marker_barrier_confirmed` setzen. |
| E8 | Quellen und Reservierungen weiterhin unveraendert, beide internen Bestaetigungen wahr, alle Belege gueltig und Handle-Abschluesse ohne Fehler: genau eine operative Rueckgabe `COMPLETED`. |

Die internen Bestaetigungen beginnen falsch. Sie werden weder aus einem
externen Bool, einem Digest noch einem gelesenen `COMPLETED` uebernommen.
Die Rueckgabe vor E8 ist verboten. Die zwei Reservierungen und der Marker
werden nicht in einer behaupteten Mehrdateitransaktion zusammengefasst:
Teilfortschritt ist moeglich und bleibt dann dauerhaft gesperrt.

## 5. Bindungen des Abschlussmarkers

Der private Marker ist eine kanonische Huelle um die bestehende terminale
`AttemptJournalEntry`-Zeile 114. Es gibt keine zweite Journal-114-Datei.
Die Huelle bindet folgende Felder, ohne die inneren Matrixrecords umzubauen:

- Schema- und Backendvertragskennung, Studien-ID und autorisierte Attempt-ID;
- Plan-, Autorisierungs-, Quellen-, Plattformbeleg- und Reservierungsdigest;
- Zielreservierungsdigest, kanonischen Zielpfad und Elternverzeichnisidentitaet;
- Volume-/Dateiidentitaet des nach Rename weitergehaltenen Ergebnis-Handles;
- finale Bytezahl, SHA-256 der vollstaendigen Ergebnisbytes und Artefaktdigest;
- die unveraenderte Terminalzeile mit Reservierungs- und SEALED-Kettenbindung;
- Eigendigest der Huelle nach dem vorhandenen kanonischen Verfahren, ohne Eigendigestfeld.

Alle Werte werden aus validierten Quellen oder tatsaechlichen Handlebefunden
abgeleitet. Die Terminalzeile wird erst nach E6 erzeugt; ihr Inhalt bezeugt
nicht ihren eigenen spaeteren Flush. Deshalb enthaelt die Huelle kein
angeblich selbstbeweisendes `marker_flush_succeeded`-Feld.
Das Ergebnis referenziert den spaeteren Marker nicht: keine Digestzirkularitaet.

## 6. Fehler- und Wiederanlaufregeln

| Beobachtung | Zulaessige Einordnung |
| --- | --- |
| Schreib-/Umbenennungsrecht fehlt, insbesondere Fehler 5 | sofort fail-closed; kein Rechtewechsel oder anderer Backendpfad |
| Verzeichnis oder zugehoeriger Haltbarkeitsbeleg fehlt | `BLOCKED_PLATFORM_PREREQUISITE`, vor Reservierung keine Zelle |
| beliebige Reservierung oder Zieldatei schon vorhanden | Konflikt / bereits verbraucht; keine Ersetzung, Loeschung oder neue Kennung |
| Schreibfehler, Short Write, Flushfehler, Identitaets- oder Inhaltsabweichung vor Rename | `FAILED`, vorhandene Reservierungen bleiben gesperrt |
| Rename-Ausgang unklar oder Ergebnis sichtbar, aber E6 fehlt | `ABORTED_INCOMPLETE`, kein Marker und kein Retry |
| Marker fehlt, ist teilweise, fremd oder hat unbestaetigten Flush | `ABORTED_INCOMPLETE`, auch bei vollstaendig lesbarem Ergebnis |
| Prozessverlust vor bestaetigtem E8 | keine operative Erfolgsmeldung aus Dateien rekonstruieren; kein Resume |
| E0-E8 vollstaendig bestaetigt | `COMPLETED` nur fuer diesen gebundenen Ablauf |

Bei jedem Fehler endet die Aktionskette. Zulaessig bleiben nur Handlefreigabe,
read-only Einordnung und getrennte Diagnose. Diagnosefehler duerfen den
urspruenglichen Fehler nicht verdecken. Keine nachtraegliche Markerbildung,
kein erneuter Flush, kein Nachholen einer Zelle und kein automatischer Retry.
Ein spaeterer unbeteiligter Fehler widerruft keinen bereits belegten Abschluss.

Nach Verlust des vertrauenswuerdigen laufenden Bestaetigungskontexts darf eine
rein lesende Pruefung allenfalls `COMPLETE_RECORDS_PRESENT_UNCONFIRMED`
melden, wenn alle Inhalte passen. Das ist **nicht** `COMPLETED` und gibt keine
Ausfuehrung frei. Ein persistiertes Objekt kann nicht allein belegen, dass
sein letzter Flush erfolgreich zurueckkehrte. Auch ein weiterer Marker wuerde
diese Frage nur verschieben. Hier wird deshalb keine solche Markerrekursion
eingefuehrt. Die strengere Wiederanlaufregel ist bewusst Teil der Alternative.

Lesbarkeit kann aus dem Dateicache stammen und ist kein Persistenznachweis.
[Microsoft: File Caching](https://learn.microsoft.com/en-us/windows/win32/fileio/file-caching).

Fehler vor bestaetigter Reservierung duerfen nicht als sichere dauerhafte
Verbrauchsaufzeichnung ausgegeben werden. Sie erlauben dennoch keinen Retry
der erteilten Einmalausfuehrung. Fehlende Dateien sind niemals selbst eine
Freigabe. Einmaligkeit gegen manuelles Ledgerloeschen oder absichtliche
Belegfaelschung bleibt ausserhalb der bisherigen Vertrauensgrenze.

## 7. Zwingende Abnahmefolge

Die folgenden Gates sind Vertragsforderungen und derzeit **nicht abgenommen**.
Alle muessen vor einer Nutzung durch den Studienpublisher geschlossen sein;
ein isolierter Plattformversuch dient erst der Erhebung der fehlenden Belege:

- G1: vorhandene, identitaetsgebundene, dauerhaft eingerichtete Elternpfade;
  keine Verzeichnisneuerzeugung im Publisher und kein stilles Bootstrap.
- G2: Datei-Flush/Write-through deckt fuer den konkreten NTFS-Pfad auch
  Reservierungsnamen, neue Belegnamen und die Rename-Metadaten ab. Ein
  Dateiflush wird nicht pauschal als Flush aller Elternverzeichnisse behandelt.
- G3: atomare No-Replace-Sichtbarkeit, unveraenderte Handleidentitaet und
  korrekte Share-/Rechtebehandlung bei Konkurrenz und Fehlern.
- G4: genaue Materialisierung der privaten Markerhuelle, Pfadabbildung,
  Fehlerprioritaet und E0-E8-Bestaetigungen; kein ungepruefter Altcodefallback.
- G5: getrennte Quellenbindung und isolierter Plattformbeleg fuer diesen
  Backendstand; alte S2-EM-Fehler und NOT_RUN-Faelle werden nicht uminterpretiert.

Die Kombination aus NTFS, Dateibarrieren und Handle-Rename ist eine fachlich
begruendete Abnahmerichtung, keine Behauptung absoluter Stromausfallsicherheit.
Betriebssystem, Treiber und Datentraeger muessen ihre zugesagten Barrieren
einhalten. Physische Stromausfallversuche sind hier weder erfolgt noch freigegeben.

**WEITER:** S2-EP als separaten statischen Implementierungs- und
Plattform-Voraudit dieses Vertrags durchfuehren. Er muss Materialisierbarkeit
und die Nachweisgrundlage von G1-G5 bewerten. Weil noch kein alternativer
Code existiert, darf er keine Implementierungsabnahme behaupten.

Eine spaetere Implementierung benoetigt eine eigene Freigabe, danach eine
Pruefung des tatsaechlichen Codes. Der separate Implementierungs- und
Plattformaudit muss vor einem neuen Versuch dessen Quellen, Isolation,
Nachweispflichten und Abbruchregeln abnehmen. Er darf die erst zu messenden
Plattformfaehigkeiten nicht bereits als bestanden markieren.

Eine erneute isolierte S2-EM-Ausfuehrung benoetigt danach zusaetzlich eine
ausdrueckliche Einmallauffreigabe mit neuer, getrennt gebundener Belegablage;
`s2em.001` wird nicht wiederverwendet. Sie darf die offenen Plattformbelege
erst erheben, ohne Studienreservierung oder Matrixaufruf. Es wird also kein
bestandener Plattformversuch als Voraussetzung seiner eigenen erstmaligen
Messung verlangt. Erst fuer den Studienpublisher werden G1-G5 gemeinsam
zwingend. S2-EL und die separate Matrixfreigabe bleiben nachgelagerte Grenzen.
