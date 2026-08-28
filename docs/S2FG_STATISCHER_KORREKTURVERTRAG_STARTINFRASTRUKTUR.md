# S2-FG: Statischer Korrekturvertrag der Startinfrastruktur

## Status und Geltung

**STATIC_CORRECTION_CONTRACT_BOUND_CODE_AUDIT_PENDING**

Dieser Vertrag bindet ausschliesslich die Korrektur- und Nachweispflichten
zu FF-B01 bis FF-B06. Er ist keine Implementierung, keine Codeabnahme und
kein numerisch vollstaendiges Startpaket. Alle sechs Code-/Nachweisblocker
bleiben bis zur gesonderten Abnahme offen. S2-FC bleibt blockiert.

Ausgangscommit: `60be1d43bde8c33fcd4fc572e6474720f803f3bb`.
S2-FD, S2-FE und S2-FF bleiben unveraenderte Originale. S2-FG praezisiert
deren sechs beanstandete Stellen; sonstige Regeln bleiben bestehen.
Die maschinenlesbare Bindung steht in
[S2FG_STATISCHER_KORREKTURVERTRAG_STARTINFRASTRUKTUR_V1.json](S2FG_STATISCHER_KORREKTURVERTRAG_STARTINFRASTRUKTUR_V1.json).

Die vier privaten Quellen sind der einzige betrachtete spaetere
Korrekturbereich. Eine solche Codekorrektur ist heute nicht freigegeben.
Die acht Bestandsmodule, TSPM-1, PPB-1, API, Snapshot und Feldpfad bleiben
unveraendert. Keine neuen Recorderfaelle, Pfadrollen oder Ownerdateien.

## FG-C01: Reservierungszugriff

Bezug: FF-B01; privater Worker und `SourceLease`.

Der Reservierungsleser wird vom normalen unveraenderlichen Quellenleser
getrennt. Sein einzig zulaessiger Zielpfad ist die aus der validierten
RecorderBinding abgeleitete Rolle `platform_reservation`. Er darf keine
freie FileRef, keinen Ersatzpfad und keinen allgemeinen Schreibzugriff
akzeptieren.

Der Supervisor behaelt seinen bestehenden Schreibhandle. Der private Leser
verwendet den vorhandenen Verifikationsmodus `_open(..., verification=True)`:
nur Lesezugriff, vorhandene Datei, keine Erzeugung, kein Rename. Dieser Modus
teilt den vorhandenen Schreibzugriff; der gehaltene Supervisorhandle verhindert
weiterhin fremde Schreib-/Loeschzugriffe. Der allgemeine `read_source`-Pfad
und der Windows-Backendcode werden nicht aufgeweicht.
Grundlage: [Microsoft, CreateFileW-Sharingregeln](https://learn.microsoft.com/en-us/windows/win32/api/fileapi/nf-fileapi-createfilew).

Verbindliche Reihenfolge fuer eine spaetere Implementierung:

1. FG-C04-Owner und Supervisorzustand `RESERVED` abnehmen.
2. Exakten Pfad aus der Binding ableiten und gehaltene Eltern pruefen.
3. Erwartete Reservierungsbytes aus Versuch, Profil, RunBinding, Quellen,
   Originalfreigabe und Review rekonstruieren; Laenge vor dem Lesen binden.
4. Genau diesen Pfad lesend oeffnen. Native Dateiidentitaet muss zum
   gehaltenen Supervisorhandle passen, nicht nur zum Dateinamen.
5. Vollstaendige Bytes, Laenge und SHA-256 sowie unveraenderte Datei- und
   Elternidentitaet nach dem Lesen pruefen. Keine Teilabnahme.
6. Leser in eigener Handleverantwortung halten und genau einmal schliessen;
   Supervisor bleibt fuer seinen Handle verantwortlich. Erst nach gueltiger
   Leseabnahme darf der Worker sein bereits gebundenes Gate erreichen.

Die Supervisoridentitaet muss ueber die abgenommene lebende Ownerkette stammen.
Ein frei eingereichter Identitaetsdatensatz ist kein Ersatz. Fehler fuehren
ohne alternativen Open-Modus, erneutes Lesen oder vorzeitiges Freigeben des
Supervisorhandles zum Abbruch. Die Kosten gehoeren in FG-C02.

## FG-C02: Vollstaendige Budgetherleitung

Bezug: FF-B02; `derive_budget_certificate` und Paketabnahme.

Zwei getrennte Abnahmen sind erforderlich: rechnerische Konsistenz und
inhaltlich gerechtfertigte Quell-/Schleifenannahmen. Nur beide zusammen
duerfen einen numerischen Budgetbeleg ergeben. Nichtleere Annahmetexte,
AST-Ortabdeckung oder grosszuegige Obergrenzen sind keine Abnahme.

Jede Kostenzeile muss auf Rohbyte-FileRef, qualifiziertes Symbol und konkrete
Aufruf-/Schleifenstelle zeigen. Zusaetzlich bindet sie Prozessrolle, Phase,
Erfolgs-/Fehlerzweig, Aufrufkante, Zaehleinheit, Eingabegrenze und deren
Beleg, Wiederholungsobergrenze, primitive Kostenregel und abgeleitete Summe.
Unaufloesbare dynamische Aufrufe oder unbelegte Schleifengrenzen blockieren.
Unerreichbare Stellen benoetigen einen belegten Ausschluss statt einer
unbegruendeten Nullzeile. Die externe Annahmeabnahme referenziert genau
diesen Zeilensatz und die festgeschriebenen Quellen.

Die Rechnung umfasst getrennt:

- explizite native API-Aufrufe, logische Recorder-Aufrufpaare und injizierte
  Proxyoperationen, jeweils mit belegter Abbildung auf S2-FD-Kostenregeln;
- Starter, Supervisor, Worker, Helper, Drain-Threads und Abschlussbeobachter,
  einschliesslich Vorbereitung, Bootstrap, Capture, Publikation und Cleanup;
- alle Quellenlesungen, Elternpruefungen, offenen Handles, Fehlerzweige,
  moegliche zweite Postcondition-Pruefung und jede zulaessige Schliessung;
- JSON-/Base64-Kodierung und Dekodierung, Validierung, Bytekopien,
  Quell-/Paket-/Fehlerhuellen und gleichzeitig lebende Puffer;
- getrennte Rohstream-, Transkript-, Kontrollspool- und Bootstrapgrenzen;
  bei Pipefragmenten wird auch der Ein-Byte-Fall samt kompletter Huelle erfasst;
- Fristen, Polls und Shutdownarbeit ohne Ruecksetzen eines bereits
  verbrauchten Phasenbudgets.

Native Aufrufzahlen sind keine CPU-Zeit oder OS-internen Systemaufrufzahlen.
Payloadbytes sind kein Beleg fuer den gesamten Python-Prozessspeicher.
Die angenommene Runtime muss deshalb auch die verwendeten Bibliothekskosten
und Objekt-/Pufferobergrenzen begruenden. Fehlt diese Grundlage, bleibt der
Host-/Speicherbeleg offen, statt Speicherverbrauch als nachgewiesen auszugeben.

Budgetabhaengigkeiten sind gerichtet: Quellen und Schemata, lokale Faelle,
Rohstream, gerahmtes Transkript, Kontrolltrace und dessen eigener Spool.
Bootstrapgroessen werden aus endlich begrenzten Paketfeldern, Originalbytes
und Huellen berechnet. Selbstbezug auf das fertige Paket ist unzulaessig;
Digestfelder haben feste Laenge, Integerfelder vorab gebundene Breiten.
Der nachfolgend berechnete exakte Paketumfang darf die vorab begruendete
Grenze nur bestaetigen, nicht nachtraeglich vergroessern.

Je Prozess und Richtung gilt ein gemeinsames Byte-/Frameledger vom
Bootstrap bis zum Abschluss. Systemweite Kosten summieren Prozessinstanzen;
gegenseitig ausschliessende Pfade werden nur bei belegter Ausschliesslichkeit
durch ihr Maximum ersetzt. Derselbe Aufwand darf nicht fehlen oder doppelt
als zwei unterschiedliche Leistungen ausgewiesen werden. Cleanup und
Fehlermeldung erhalten vorab mitgezaehlten Restbedarf, keinen Nachschlag.

Alle endgueltigen Grenzen muessen vor Dispatch als exakte positive Integer
aus dem abgenommenen Zeilensatz stammen und in einen unabhaengig abgenommenen
Hostrahmen passen. Interne Nullbeitraege sind nur begruendet zulaessig.
Ueberlauf, unbekannte Werte, falsche Einheit, fehlende Quelle oder Kreisbezug
blockieren. Kein Lauf darf zur nachtraeglichen Festlegung benutzt werden.

Heute bleiben numerische Grenzen **nicht materialisiert**. Bekannt sind nur
13 Faelle, 24 Payloads/528 Bytes, 133 Recorderpfadrollen, 28 Renamekanten und
zwei externe Ownerpfade. 75.623 Bytes/975 AST-Aufrufknoten der vier Quellen
sind Inventar, kein Ausfuehrungsbudget.

## FG-C03: Bootstrap vor Materialisierung begrenzen

Bezug: FF-B03; `_read_bootstrap`, `wire_package`, Pipe- und Paketabnahme.

Eine unabhaengig zugelassene BootstrapPolicy muss bereits vor dem Lesen
vorliegen. Sie bindet Rollen, Bootstrap-/Frame-/Gesamtbytes, Originalanzahl,
Einzeldateigroessen, Struktur-/String-/Integergrenzen, Speicherobergrenze
sowie Start-, Empfangs- und Shutdownfristen. Ihre Werte kommen aus FG-C02
und dem extern zugelassenen Startkontext, niemals aus der noch ungelesenen
Nutzlast. Sie ist selbst Teil der Ressourcen- und Herkunftsabnahme.

Der Sender prueft Umfang und Kosten vor Base64/JSON-Materialisierung.
Der Empfaenger prueft nach hoechstens acht Headerbytes die positive Laenge
gegen die Bootstrapgrenze einschliesslich Header, bevor er Payloadpuffer
anlegt oder liest. Bereits der Headerempfang ist zeitlich begrenzt. Reads
duerfen fragmentiert sein, aber keine unbegrenzten Warte-/Sammelschleifen
erzeugen. JSON-Strukturgrenzen gelten vor beziehungsweise waehrend Parsing;
eine erst nach vollstaendiger Dekodierung gepruefte Grenze reicht nicht.

Nach bounded Parsing und kanonischer Dekodierung muss das Paket exakt zu
Policy, Quellenabschluss und aktueller Ownerzulassung passen. Fuer die
gleiche Budgetgroesse gilt Gleichheit, kein vom Paket gewaehltes Maximum.
Bootstrapbytes und Header werden genau einmal im gesamten Richtungsbudget
gezaehlt. Der Wechsel zu `ParentChannel` darf Zaehler oder Fristen nicht
erneuern. Der Worker-Rohstream bleibt in derselben Kostenbilanz, ohne
seinen bestehenden Recorderframevertrag umzuschreiben.

Fehlende Policy blockiert vor Payloadannahme. Zu lange, abgeschnittene,
mehrdeutige oder fremde Huellen brechen ab. Kein blockierender Fallback,
kein Retry, kein Lesen bis EOF als Ersatz fuer die gebundene Laenge.

## FG-C04: Lebende Einmalstart-Berechtigung

Bezug: FF-B04; aeusserer Owner, Kind-Einstiege und `ChildOwner`.

Persistierte Dispatch-/Sealbytes bleiben notwendige Verbrauchsbelege,
werden aber niemals als erneut verwendbare Startberechtigung akzeptiert.
Die unabhaengige aeussere Vertrauenswurzel muss vor Paketannahme feststehen.
Sie darf nicht durch JSON, `START`, CLI, Umgebungsvariable, PID-Gleichheit,
ein neues Python-Objekt oder vom Kind gelieferte Handlewerte entstehen.

Ein lebender Ownerkontext bindet genau Versuch, Paket, StartAdmission,
BootstrapPolicy, zugelassene Quellmenge, reale Observer-Prozessidentitaet und
seine gehaltenen Kanaele. Prozessidentitaet umfasst PID, Erzeugungszeit und
Imagebindung; Nachweis erfolgt ueber eigene native Handles. Die erwartete
Autoritaet muss aus der unabhaengigen Zulassung stammen, nicht aus demselben
Kanal wie die zu pruefende Behauptung.

Fuer jede der drei Rollen besteht genau ein gemeinsamer Verbrauchseintrag
im lebenden Ownerkontext: `UNUSED -> CLAIMED -> SPAWNED -> TERMINAL` oder
`CLAIMED/SPAWNED -> FAILED/UNKNOWN`. Der Uebergang nach `CLAIMED` erfolgt
atomar vor dem jeweiligen Popen und bleibt auch bei dessen Fehlschlag
verbraucht. Neue `ChildOwner`-Instanzen duerfen diese Eintraege nicht ersetzen.
Jeder Eintrag bindet Elternrolle, reale Elternidentitaet, Kindrolle und nach
Erzeugung die eigene native Kindidentitaet. Es gibt keinen Rueckweg.

Die Hierarchie Observer -> Starter -> Supervisor -> Worker bleibt bestehen.
Vor jeder Erzeugung benoetigt die Elternrolle die aktuelle Zulassung des
aeusseren Owners. Vor Gatefreigabe muss der Owner den erzeugten Kindprozess
selbst uebernommen haben. Der Worker benoetigt zusaetzlich FG-C01 und die
bestehende RESERVED-Abnahme. Ein lokales `OWNED`-Wort ersetzt diese Fakten
nicht. Direkter oder wiederholter Kind-Einstieg ohne diese Kette wird vor
weiterem Kindstart, Reservierung oder Recordergate abgewiesen.

Nach Ownerende, unklarem Dispatch oder verlorener Kanalherkunft ist kein
Wiederaufbau aus alten Dateien erlaubt. Die festen beiden Ownerpfade und
die externe Einmalfreigabe bleiben die dauerhafte Wiederanlaufsperre;
keine weiteren Ledgerdateien und kein neuer Versuchsname.

**Offene Realisierungsgrenze:** S2-FG behauptet keine bereits vorhandene
vertrauenswuerdige Uebertragung dieses Kontexts. Der naechste statische Audit
muss deren konkrete Bootstrap-/Kanalherkunft gegen diese Pflichten pruefen.
Ist sie nur durch eingereichte Bytes oder eine selbst gesetzte ContextVar
begruendet, bleibt FG-C04 nicht abnahmefaehig. Es wird kein kryptografisches
Verfahren, externer Dienst oder neuer privilegierter Launcher stillschweigend
eingefuehrt. Schutz gegen beliebige Codeinjektion oder kompromittiertes OS
wird nicht behauptet; regulaere alternative Aufrufer duerfen die Grenze
gleichwohl nicht umgehen.

## FG-C05: Quellenherkunft und exakte Rollen

Bezug: FF-B05; Paket-, Runtime- und Metadatenabnahme.

`layout_contract_file` muss exakt die bereits gebundene S2-FB-Datei mit
FileRef aus S2-FD sein, nicht eine beliebige historische Referenz.
Alle Prozessplaene muessen denselben abgenommenen Interpreter aus der
beabsichtigten `SourceManifest.runtime_identity` verwenden. Dateipfad,
Rohbytehash, Architektur/ABI und die zugehoerigen Runtime-Dateien muessen
relational zusammenpassen. `sys.executable` allein ist keine Herkunftsabnahme.

Der Quellenabschluss umfasst Entry-Script, vier private Dateien, acht
Bestandsmodule und alle tatsaechlich benoetigten Paketinitialisierungen,
Bootstrap-/Standardbibliotheks-/Extension-/Runtime-Abhaengigkeiten. Die vier
Dateien sind keine abgeschlossene Importwelt. Abhaengigkeiten erhalten
FileRefs und Importkanten oder eine explizit abgenommene Built-in-/Runtime-
Zuordnung. Nicht aufloesbare dynamische Imports blockieren; keine fremden
Projektmodule und keine automatische Abhaengigkeitsbeschaffung.

Der zugelassene Elternpfad muss die benoetigte Quell-/Runtimeidentitaet vor
dem Kindimport sichern und bis zum abgenommenen Abschluss halten. Die
spaetere Kind-Lease prueft diese Bindung erneut, ersetzt aber nicht die
vorherige Absicherung. Fehlende Vorab-Lease verhindert den Start. Externe
Runtimequellen bleiben vom repositorybegrenzten `read_source` getrennt.

Die archivierten nativen Metadaten bleiben Originale; ihre Observer-Runtime
ist nicht automatisch die Recorder-Runtime. Viertes Elternverzeichnis,
Einrichtungsbeleg, Haltbarkeitsgrundlage und unabhaengige Abnahme muessen
gesondert vorliegen. Ein passender Hash oder Reviewername kann fehlende
Beleginhalte nicht ersetzen. Ihre Erhebung ist hier nicht freigegeben.

## FG-C06: Fehler- und Nachweisformen

Bezug: FF-B06; private Ergebnisgrenze und Abschlussbeobachter.

Jeder Fehler behaelt Phase, meldende Rolle, Operation, Ursprungsklasse,
urspruenglichen Code, gegebenenfalls nativen Fehlerwert und bekannten
Paket-/Ownerbezug. Primaerfehler und alle Cleanupfehler werden getrennt
erhalten. Das Rueckgabetupel von `abort()` darf nicht verworfen werden.
Bereits intern abgefangene Cleanupfehler ohne weitergereichten Beleg gelten
als unbekannt, niemals als erfolgreiche Schliessung. Kann der private Wrapper
die bestehende Nachweisluecke nicht ohne Bestandsaenderung schliessen, bleibt
sie fuer den Codeaudit offen; S2-FG autorisiert keine Bestandsaenderung.

Die geschlossenen Vertragsformen im JSON legen Fehler-, Closure- und
Terminalnachweise fest. Es sind Sollformen, keine neuen implementierten
Datentraeger oder vom bestehenden V1-Validator bereits akzeptierte Felder.
Eine spaetere private Umsetzung muss diese Formen explizit validieren;
stilles Erweitern oder Umdeuten bestehender V1-Records ist ausgeschlossen.

Verbindliche Statusprioritaet nach Erfassung aller vorhandenen Belege:

1. Fehlgeschlagener oder unklarer Close/Flush/Seal/terminaler Ownerabschluss:
   `COMPLETION_UNCONFIRMED`, unabhaengig vom Primaerfehler.
2. Bereits verbrauchter oder unklar verbrauchter Einmalanspruch ohne neuen
   Kindstart: `ALREADY_CONSUMED`. UNKNOWN erlaubt niemals Wiederholung.
3. Falsche vorhandene Quellen-, Layout-, Rollen-, Owner- oder Digestbindung:
   `BINDING_REJECTED`; vorhandene Kinder nur kontrolliert abbrechen.
4. Fehlende unabhaengige Voraussetzung vor Dispatch/Kindstart:
   `BLOCKED_PREREQUISITE`. Dazu gehoert fehlende Schreibberechtigung
   (nativer Fehler 5) vor begonnener Reservierung, ohne Rechteerhoehung.
5. Laufender oder bereits dispatchter Versuch mit Timeout, Budget- oder
   sonstigem Laufabbruch: `ABORTED_INCOMPLETE`, sofern keine hoehere
   Unvollstaendigkeitsklasse zutrifft.
6. Nur bei vollstaendiger gueltiger Beweiskette und ohne Fehler:
   `ISOLATED_RECORDING_COMPLETE`.

Die Einordnung richtet sich nach belegter Phase und Ursache, nicht nur nach
Python-Ausnahmetyp. Ein nativer Fehler 5 waehrend unklarer Persistenz ist
kein harmloser Vorbedingungsfehler. Unbekannte Fehler bleiben ablehnend.
Fehlt ein gueltiger Paketdigest bereits am Eingang, wird er als unbekannt
mitgefuehrt, nicht erfunden. Der unabhaengige Aufrufer muss auch Ausfaelle
vor einer regulaeren Observer-Rueckgabe als fehlenden Abschluss erfassen.

Direkte Prozessbeobachtungen stammen aus eigenen Handles. Delegierte
Pipe-/Kontrollabschluesse binden dagegen beobachtende Rolle, reale
Prozessidentitaet, konkrete Operation/Quellstelle, Ressourcenrolle und
Originalnachweis. Ein pauschales `finish(role, True)` oder aus Gesamterfolg
abgeleitetes `control_close_observed` genuegt nicht. Die bestehende
Reihenfolge `control.finish()` vor LiveRecordingCompletion bleibt erhalten.
Ein Prozessende oder eine lesbare Datei ersetzt keinen erfolgreichen Close.

Der Observer darf seinen eigenen terminalen Exit nicht belegen. Sein
Rueckgaberecord und der gesonderte native Abschlussbeleg des unabhaengigen
Aufrufers werden ausserhalb des Observerrecords zusammen abgenommen, ohne
Selbsthash oder rekursive Abschlusskette. Bei fehlender Ausgabe oder
fehlgeschlagener Aufzeichnung gilt unbestaetigter Abschluss, kein Retry.
Fehlerlisten, Closurelisten, Diagnosebytes und Cleanupkosten sind ebenfalls
endlich und aus FG-C02 gebunden; stille Abschneidung ist unzulaessig.

## Separater Codeaudit

Fuer jede Zuordnung FF-B01 -> FG-C01 bis FF-B06 -> FG-C06 sind getrennt
festzuhalten: Vertragskonsistenz, vorhandene Quellumsetzung und vorhandene
Herkunfts-/Budgetbelege. Der Audit darf einen Sollsatz nicht als Codekorrektur
werten und einen Quelldigest nicht als Funktionsbeweis.

Die Abnahmekriterien pro Bindung stehen im JSON. Sie sind statische
Pruefpflichten, keine Testdefinitionen oder Ausfuehrungsfreigaben.
Der unveraenderte Code kann nicht allein wegen dieses Dokuments als
korrigiert gelten. Auch ein spaeter bestandener Codeaudit ersetzt die sechs
weiterhin offenen S2-FC-Voraussetzungen nicht.

Heute: 19 Quell-/Belegbindungen und die drei S2-FD-/FE-/FF-Selbstdigests
geprueft. Nur zwei neue Vertragsdokumente; keine Projektimporte,
Zustandsaufrufe, Tests, nativen Metadaten, Plattformaufrufe, Ledger-Erzeugung,
Zielschreibvorgaenge, Flushes, Recorderstarts oder Matrixzellen. Keine neue
Laufnummer und keine Memory-/Feldinterpretation.

WEITER: Am besten geht es jetzt mit einem separaten statischen Codeaudit
gegen S2-FG weiter. Korrekturimplementierung und Ausfuehrung bleiben gesperrt.
