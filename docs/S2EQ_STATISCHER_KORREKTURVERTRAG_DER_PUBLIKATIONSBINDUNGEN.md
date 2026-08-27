# S2-EQ: Statischer Korrekturvertrag der Publikationsbindungen

## Status und Grenze

**STATIC_CORRECTION_CONTRACT_BOUND_EP_REAUDIT_REQUIRED**

S2-EQ konkretisiert ausschliesslich EP-B01 und EP-B02. Es nimmt weder den
Alternativpublisher noch eine Plattformfaehigkeit ab. S2-EP muss erneut
statisch pruefen; Implementierung, S2-EM und die 56-Zellen-Matrix bleiben
gesperrt. Es gibt keinen neuen Versuch und keine Laufnummer.

Quellstand: `15e09ba2dbb144cf53e9dca11ce23d59bb9a439c`. Der JSON-Begleitvertrag
enthaelt die verbindlichen Feldkataloge, Quellenidentitaeten, Digestrollen
und unveraenderten S2-EO-Abschnittsdigests. Die dortigen Typbezeichnungen
sind eine Datenspezifikation, kein implementierter Validator.

## 1. Unveraenderte Regeln

S2-EO bleibt fuer Namensraum, Dateioperationen, E0-E8, Fehlerreihenfolge,
Wiederanlauf und G1-G5 unveraendert. Die sechs entsprechenden JSON-Abschnitte
werden durch ihre kanonischen SHA-256-Digests gebunden. S2-EE-Innenrecords,
Erfolgskriterien, Comparator, Budgets und S2-EH-Altcode bleiben unveraendert.

Keine neue Reservierungsstelle, kein zweiter Abschlussmarker, keine
nachtraegliche Reparatur, kein Volume-Handle und kein Rechtewechsel.
Die neuen Formen sind ausschliesslich private Daten des kuenftigen
S2-EO-Publishers. Der vorhandene `_DurableStudyStore` und seine Reader
sind damit nicht automatisch kompatibel oder freigegeben.

## 2. Gemeinsame Daten- und Digestregeln

Alle Felder der JSON-Feldkataloge sind Pflichtfelder; Zusatzfelder,
doppelte JSON-Schluessel, unbenannte Varianten, NaN und Infinity sind
ungueltig. Null ist ausschliesslich bei explizit optionalen Feldern
erlaubt. Ganzzahlen sind keine Booleans oder Fliesskommazahlen.
Listen werden in der angegebenen Reihenfolge gebunden; Mengenlisten
sind nach dem benannten Schluessel sortiert und duplikatfrei.

Fuer neue private Records gilt das vorhandene kanonische Verfahren:
ASCII-JSON mit `ensure_ascii=True`, `sort_keys=True`,
`separators=(",", ":")`, `allow_nan=False`, ohne abschliessenden
Zeilenumbruch. Der SHA-256-Eigendigest schliesst nur das oberste
`record_digest` aus. Eingebettete Records behalten ihren Eigendigest.
Raw-SHA-256 bezeichnet dagegen die gesamten tatsaechlichen Dateibytes.
Beides darf nicht ausgetauscht werden.

Neue Schemakennungen sind im JSON literal gebunden. Sie sind keine neuen
`S2EFRecord`-Kinds. Die bestehenden Innenrecords werden nach ihrem
unveraenderten eigenen Schema validiert, nicht um neue Felder erweitert.
Alle angenommenen Werte sind unveraenderliche validierte Wertkopien;
spaetere Mutation oder ein erneut aufgeloester freier Pfad ist unzulaessig.

### Native Identitaeten

`VolumeIdentity` bindet NTFS und die 64-Bit-Volumeseriennummer als genau
16 Kleinbuchstaben-Hexziffern. `FileIdentity` ergaenzt die 128-Bit-Datei-ID
als 32 Hexziffern in Reihenfolge der nativen 16 Bytes. Die Seriennummer
wird numerisch mit fuehrenden Nullen dargestellt. Beide Werte stammen
aus `FILE_ID_INFO` des tatsaechlichen Handles, nicht aus Dateinamen,
Dateiinhalten oder dem vorhandenen Repository-Hashhelfer.

Microsoft beschreibt diese Kombination als Dateiidentitaet auf einem
Computer. Daher werden Host und Plattformkontext immer mitgebunden;
die Kombination ist keine globale oder zeitlich unbegrenzte Identitaet.
[Microsoft: FILE_ID_INFO](https://learn.microsoft.com/en-us/windows/win32/api/winbase/ns-winbase-file_id_info).

`DirectoryIdentity` bindet kanonischen absoluten Pfad und native Identitaet.
`ParentSet` hat genau vier Rollen: repository, git_common, ledger, output.
Gleiche physische Verzeichnisse duerfen mehrere Rollen erfuellen; fuer
denselben Pfad muessen die Identitaeten identisch sein. Alle Rollen und
Ergebnisdateien liegen auf dem einen gebundenen Volume.

Kanonische Pfade stammen aus der validierten Quelle und der spaeteren
Handlepruefung. Keine freie Kleinschreibung, Aliasersetzung oder
Normalisierung darf eine abweichende Identitaet verdecken. S2-EO-Regeln
gegen Reparse Points, alternative Datenstroeme, Hardlink- und Namensaliasse
bleiben vollstaendig bestehen. Heute werden keine nativen Identitaeten erhoben.

## 3. EP-B01: Plan, Autorisierung und Reservierungen

Bezeichnungen: P = bestehender ExecutionPlan, A = bestehende
ExecutionAuthorization, R = bestehende AttemptReservation,
W = private PublicationPlan-Huelle, U = private PublicationAuthorization,
T = private TargetReservation, M = privater CompletionMarker.

W bindet P, A, Quellmanifest, S2-EO- und S2-EQ-Vertragsdigest, Backend,
Studie, Attempt, ParentSet, Plattformkontext, komplette Publikationspfade,
Publisherquellen und die abgenommene Plattformidentitaet Q.
P und A werden nicht umgeschrieben. W ist kein Ersatz fuer P.

U bindet genau W, A und die ausserhalb des Publishers erteilte explizite
Freigabe mit Einmalbudget eins. Die Freigabe muss diese exakte W-Identitaet
benennen. Ein beliebiger Hash einer Zustimmung oder eine vom Aufrufer
gelieferte Zustimmung genuegt nicht; die Identitaet muss im unabhaengig
abgenommenen Zulassungskontext hinterlegt sein. Dieser Kontext ist
gegenwaertig leer. W enthaelt U nicht: keine gegenseitige Digestabhaengigkeit.

W.publication_paths werden ausschliesslich aus P und S2-EO abgeleitet.
Die Quelle fuer `final` und `staging` bleibt P. Studienreservierung,
Zielsidecar, flache Belegnamen und Markerpfad folgen exakt S2-EO.
Die private Autorisierung fuehrt keine neue Ledgerdatei oder weitere
Verbrauchsstelle ein; sie ist eine vorab validierte Eingabe an E0.

E0 prueft P, A, W, U und Q vollstaendig, bevor R erzeugt werden duerfte.
R bleibt in Form und Bedeutung unveraendert und wird erst in E1 angelegt.
T entsteht in E2 aus den bereits angenommenen Quellen und bindet
R, P, A, W, U, Studien-/Attempt-ID, finalen Pfad und output-Elternidentitaet.
Kein frei uebergebenes Feld darf diese Ableitung ersetzen.

Der JSON-Teil `relations` legt alle Gleichheiten fest. Insbesondere sind
zwei verschiedene ParentSets oder Plattformabnahmen bei gleichem P nicht
austauschbar: Sie aendern W, damit U und T und schliesslich M. Ohne passende
unabhaengige Autorisierungsbindung ist die geaenderte Kette ungueltig.

## 4. EP-B01: Abschlussmarker und nichtzirkulaere Kette

M behaelt genau die 19 S2-EO-Felder. Die Typen und Literale werden jetzt
festgelegt; kein Flush-Bool und keine zusaetzliche Journaldatei kommen hinzu.

M.execution_plan_digest meint P, nicht W. M.execution_authorization_digest
meint A, nicht U. Der Zugang zu W und U erfolgt eindeutig ueber
M.target_reservation_digest -> T. M.platform_acceptance_digest meint Q.
Die Trennung ist verbindlich und darf nicht kontextabhaengig umgedeutet werden.

Die Ergebnisidentitaet stammt aus dem nach Rename weitergehaltenen Handle.
Volume, finaler Name und output-Elternidentitaet muessen weiterhin mit W
uebereinstimmen. Bytezahl und Raw-Digest werden gegen die vollstaendigen
kanonischen Ergebnisbytes geprueft, der Artefaktdigest gegen den vollstaendig
validierten MatrixArtifact-Innenrecord. Ein blosses Digestfeld im Ergebnis
genuegt nicht.

Die terminale Innenzeile bleibt AttemptJournalEntry 114: COMPLETED,
Vorgaenger SEALED 113, R-Digest, derselbe Ergebnisartefaktdigest,
keine Zellreferenzen und kein Fehler. Ihre Bildung folgt erst auf E6.
Der Marker referenziert das Ergebnis; das Ergebnis referenziert den
spaeteren Marker nicht.

Digestreihenfolge: unabhaengige Vertrags-/Quell-/Plattformbelege und P,
danach A und Q, danach W, danach U, danach R, danach T, danach Ergebnis
und SEALED, danach Terminalzeile und M. Zwischen Q und W gibt es keinen
Rueckverweis; der Plattformversuch darf keine Studienreservierung nutzen.

E6 bestaetigt nur die Ergebnisbarriere. E7 bestaetigt nach eigenem
erfolgreichem Flush und Inhaltsabgleich die Markerbarriere. Erst E8 erlaubt
den operativen Abschluss. Nach Verlust dieses laufenden Vertrauenskontexts
gilt weiterhin hoechstens COMPLETE_RECORDS_PRESENT_UNCONFIRMED.
Keine der neuen Datenformen ersetzt eine tatsaechliche Barriere.

## 5. EP-B02: Herkunft des Plattformbelegs

Die Plattformbeweiskette hat drei getrennte Records:

- F: PlatformProfile, vor einem spaeter separat freigegebenen isolierten
  Versuch festgelegt. Bindet Backend-/Vertragsstand, Publisher- und
  Recorderquellen, Plattformkontext, ParentSet, unabhaengigen
  Isolationsvertrag und die dort vorregistrierte endliche Fallliste.
- B: PlatformReport, vom dort gebundenen Recorder aus genau einem
  autorisierten isolierten Versuch erzeugt. Bindet F, Autorisierung,
  Attempt, Quellen, Kontext, Originalprotokoll und alle Fallbefunde.
- Q: PlatformAcceptance, nachgelagerte statische Abnahme von B gegen F,
  Dokumentationsgrundlage, Parent-Einrichtungsbeleg und Codeaudit.

F registriert kein neues Testbudget durch S2-EQ. Seine Fallliste muss
eins zu eins aus einem spaeter separat abgenommenen Isolationsvertrag
stammen; Nachregistrierung nach Sichtung von B ist verboten. F und B
sind keine Studienplaene. Keine 56-Zellen-ID, keine Studie-R und keine
produktive Ausgabedatei duerfen als Probe benutzt werden.

Die JSON-Formen definieren fuer jeden Fall eindeutige ID, zu pruefende
EO-Gates, vorregistriertes Erwartungsartefakt und genau einen Rohbeleg mit
Status, nativer Fehlerzuordnung und Soll/Ist-Abnahme. Rohbelege enthalten
die vollstaendige geordnete native Aufrufspur mit Handlezuordnung,
Schreibmengen, Rueckgaben, Flushes, Rename-Ausgang und Abschlussfehlern
gemaess gebundenem Recorderformat. Ein freier Text "passed" ersetzt sie nicht.

Die Rohspurform selbst stammt aus dem vorab gehashten Recorder-/Isolations-
vertrag. Das ist keine Erlaubnis fuer nachtraeglich erfundene Felder:
dessen exaktes Format und Quellen muessen im separaten Code-/Plattformaudit
vor dem Versuch abgenommen sein. S2-EQ implementiert keinen Recorder.

### Unabhaengiger Vertrauensanker

Der Publisher darf Q nicht allein aufgrund von Q.status oder eines
passenden Eigendigestfelds akzeptieren. Ein ausserhalb der eingereichten
Belegkette versioniert abgenommener AdmissionContext muss die exakten
F-, B-, Q-, Codeaudit-, Dokumentations- und Parentbeleg-Identitaeten sowie
den jeweiligen Freigabenachweis binden. Seine Identitaet ist vom
gesonderten Implementierungs-/Plattformaudit festgelegt, nicht aus W
oder dem eingereichten Q uebernommen.

Der AdmissionContext ist eine explizite lokale Vertrauensgrenze, keine
Signatur- oder Manipulationssicherheit gegen den Repositoryeigner.
Er wird nicht vom Publisher generiert und hat keinen eigenen
selbstbeweisenden accepted-Schalter. Es wird kein zweiter Publisher
verlangt, der den ersten Publisher abnimmt.

**Aktuell existiert kein zugelassener AdmissionContext und kein Q.**
Der Begleitvertrag hat eine leere Liste zugelassener Kontexte.
Die Typdefinition ist keine Abnahme und keine Ausfuehrungsfreigabe.
Diese Liste dokumentiert nur den heutigen Stand und ist kein spaeter
zu fuellendes Register in diesem Vertrag. Der kuenftige Vertrauensanker
wird separat und unabhaengig gebunden; S2-EQ wird dafuer nicht umgeschrieben.
Die Abnahme darf weder einen Rueckverweis auf den Eigendigest erzeugen
noch den bereits gebundenen Quellstand stillschweigend veraendern.

## 6. EP-B02: Verbindliche Abnahme

Q darf ausschliesslich dann ACCEPTED enthalten, wenn alle folgenden
Bedingungen in der unabhaengigen statischen Abnahme positiv belegt sind:

1. F war vor Ausfuehrung gebunden; Versuch und Recorder waren separat
   autorisiert. Autorisierung, Attempt und Quellhashes stimmen mit dem
   Originalprotokoll ueberein. Der Versuch ist einmalig und isoliert.
2. B ist vollstaendig: unabhaengig erfasster Exit-Code 0, vollstaendige
   Protokolldatei, alle und nur die vorregistrierten Faelle einmal in
   gleicher Reihenfolge. Kein NOT_RUN, fehlender oder unvollstaendiger Fall.
3. Jeder Rohbeleg wird gegen das vorab gebundene Erwartungsartefakt und
   Recorderformat abgenommen. Erwartete Negativfehler muessen genau passen;
   ein erwarteter Fehler 5 ist nur ein Negativbefund und kein positiver
   Nachweis vorhandener Schreibrechte. Ein unerwarteter Fehler sperrt.
4. Backend, Publisher-/Recorderquellen, Betriebssystem-/Runtimeprofil,
   Host, Volume und alle konkreten Elternrollen stimmen exakt ueberein.
   Ein fremder Host, anderes Verzeichnis oder geaenderter Backendstand
   wird nicht durch einen gleichen Dateisystemnamen legitimiert.
5. G1 besitzt einen separat herkunftsgebundenen Einrichtungs-/Haltbarkeits-
   beleg fuer genau diese Eltern, nicht nur exists oder Lesbarkeit.
   Dessen Quellen und Abnahme sind im Vertrauensanker festgelegt.
   Elternidentitaeten muessen bei spaeterer Nutzung erneut stimmen.
6. G2 besitzt eine dokumentierte Garantiegrundlage fuer Daten,
   Reservierungsnamen, neue Belegnamen und Rename-Metadaten, jeweils
   zugeordnet zu den konkreten S2-EO-Operationen und Originalbelegen.
   Der Bericht darf nachlesen und erfolgreiche native Rueckgaben
   feststellen; er darf daraus keine gemessene Stromausfallsicherheit
   oder pauschalen Verzeichnisflush ableiten.
7. G3 ist durch die gebundenen Konkurrenz-/No-Replace-/Identitaets- und
   Fehlerbelege gedeckt. G4 ist durch den separat abgenommenen Codeaudit
   gegen S2-EO und S2-EQ gedeckt. G5 bindet die neue isolierte Belegkette.
   Alle fuenf Gateeintraege muessen ACCEPTED sein.
8. Die Abnahme nennt die konkreten Belege und verbleibenden Hardware-/
   Treiberannahmen. Fehlende Garantiegrundlage wird BLOCKED und fehlende
   oder unvollstaendige Aufzeichnung INCOMPLETE, niemals ACCEPTED.

Jeder Gateeintrag bindet mindestens ein versioniertes Garantie-/Audit-
artefakt. G2, G3 und G5 binden zusaetzlich mindestens einen passenden
Originalfall. Ein Gate wird nicht aus einem pauschalen Gesamturteil abgeleitet.
Die statische Abnahme prueft die inhaltliche Deckung, nicht nur Hashgleichheit.

Der alte S2-EM-Bericht mit Fehler 5 und NOT_RUN-Faellen ist ausschliesslich
historischer Negativbeleg. Sein diagnostisch gespeichertes Ergebnis
belegt nicht den neuen Veroeffentlichungsweg. Er kann Q nicht ersetzen.
Eine Zukunftsfreigabe muss eine neue, getrennte Ablage binden; s2em.001
bleibt verbraucht. S2-EQ erteilt keine solche Freigabe.

Datei-Flush und NTFS-Write-through sind technische Ansaetze unter den
dokumentierten System-/Hardwarevoraussetzungen, keine universelle
Persistenzgarantie.
[Microsoft: FlushFileBuffers](https://learn.microsoft.com/en-us/windows/win32/api/fileapi/nf-fileapi-flushfilebuffers),
[Microsoft: CreateFileW](https://learn.microsoft.com/en-us/windows/win32/api/fileapi/nf-fileapi-createfilew).

## 7. Abnahmestellen ohne neue Ablaufregeln

E0: gesamte Quellen-/Autorisierungs-/Plattform-/Pfadbindung einschliesslich
W, U und zugelassenem Q, bevor irgendeine Studienreservierung entsteht.
Fehlender oder nicht passender Plattformkontext bleibt
BLOCKED_PLATFORM_PREREQUISITE. E2: vollstaendige T-Abnahme gegen
die bereits validierten E0-Quellen und R. E6/E7: vollstaendige
Ergebnis-/Markerabnahme gemaess Abschnitten 3 und 4.
E8 und alle S2-EO-Fehlerprioritaeten bleiben unveraendert.

Es gibt keinen neuen Lauf, keine Probe der Schreibrechte, keine Aenderung
am bestehenden SourceManifest, keine Zustandsfunktion und keine Tests.
Die konkreten nativen Befunde bleiben unerhoben; der Vertrag behauptet
nur, wie ihre spaetere Herkunft und Abnahme gebunden sein muessen.

## 8. Abschluss und naechster Schritt

EP-B01 ist als Korrektur durch exakte private Feldformen, native
Identitaetstypen und eine azyklische Digest-/Autorisierungskette adressiert.
EP-B02 ist als Korrektur durch eine getrennte Profil-/Originalbericht-/
Abnahmekette mit unabhaengigem Vertrauensanker adressiert.
Dies ersetzt den ausstehenden S2-EP-Wiederholungsaudit nicht.

**WEITER:** S2-EP erneut ausschliesslich statisch pruefen. Erst nach
bestandenem Voraudit ist ueber eine separate Implementierungsfreigabe
zu entscheiden. S2-EM und Matrixausfuehrung bleiben gesperrt.
