# S2-FI: Statische Praezisierung der Start- und Nachweisbindungen

## Status und Umfang

**STATIC_BINDINGS_SPECIFIED_EXTERNAL_BOOTSTRAP_UNRESOLVED**

S2-FI praezisiert ausschliesslich M1 bis M3 aus S2-FH. Es ist ein
ergaenzender Vertrag, kein bestandener Codeaudit und keine Startfreigabe.
S2-FC bleibt blockiert. Die konkrete unabhaengige Bereitstellung der
Bootstrap-Erwartung ist weiterhin nicht belegt; sie wird hier nicht durch
ein als vertrauenswuerdig bezeichnetes Datenobjekt ersetzt.

Basis: `8e68e29ab2ea7aff141b3d0827ff97321a6a0891`.
[S2-FG](S2FG_STATISCHER_KORREKTURVERTRAG_STARTINFRASTRUKTUR_V1.json)
und [S2-FH](S2FH_STATISCHER_CODEAUDIT_GEGEN_S2FG_V1.json) bleiben unveraendert.
Der [zugehoerige JSON-Vertrag](S2FI_STATISCHE_START_UND_NACHWEISBINDUNGEN_V1.json)
enthaelt die geschlossenen Formen und alle Bindungsregeln.

Die sechs FG-Regelgruppen mit ihren 21 Abnahmekriterien werden unveraendert
referenziert. Ihre kanonische Projektion aus `id`, `rules` und
`static_acceptance` hat SHA-256
`d30f91133c4340d919303531ca8e06ab826f28110b563d383ca48a3f28ab4b8a`.
Keine zusaetzlichen Abnahmekriterien oder Testfaelle werden registriert.
Die folgenden Regeln konkretisieren die vorhandenen Pflichten.

## M1: Bootstrap und Owneruebergabe

### Vertrauensgrenze

Die unabhaengige aufrufende Instanz ist der schon in S2-FD/FG verlangte
Vertrauensanker. Sie muss vor dem Observerstart die Originalfreigaben,
Quellen-/Runtimeherkunft, Budgetherleitung und Bootstrapgrenzen unabhaengig
abgenommen haben. Sie besitzt die reale Observerinstanz und deren Kanaele.
Der Observer besitzt die gemeinsame atomare Rollenvergabe fuer
`starter`, `supervisor` und `worker`.

Eine JSON-Datei, CLI-/Umgebungsangabe, PID, Handlezahl, neue ContextVar,
`START`/`OWNED`-Nachricht oder vorhandene Dispatch-/Seal-Datei schafft
diese Berechtigung nicht. Digests beschreiben Bindungen; sie erteilen keine
Berechtigung. Das gilt auch fuer die neuen rein beschreibenden Formen.

Die Uebergabe bleibt auf die vorhandenen Eltern-Kind-Pipes beschraenkt.
Vor deren erstem Payload muss der Empfaenger bereits eine unabhaengig
bereitgestellte Erwartung fuer Elternidentitaet, gehaltenen Kanal und
endliche Parsergrenzen besitzen. Eine erst ueber denselben ungeprueften
Kanal empfangene Policy kann diese Erwartung nicht begruenden.
Stderr bleibt Diagnose-/Drainkanal.

**Konkrete verbleibende Grenze:** Der aktuelle Code stellt diese
vorherige Erwartung und ihren unabhaengigen Uebergabetraeger noch nicht
bereit. S2-FI benennt die erforderliche Eingabe und ihre Abnahme, behauptet
aber keinen bereits existierenden sicheren Transport. Ohne diesen Beleg
muss vor dem Lesen des Acht-Byte-Headers gestoppt werden. Es wird weder ein
neuer Dienst noch ein Ledgerpfad, Kryptoverfahren oder privilegierter
Launcher eingefuehrt.

### Gebundene Reihenfolge

1. Der Caller bindet die bereits abgenommenen Quellen, Budgets, Policy und
   Paketidentitaet vor dem Start. Policykodierung und ihre eigene
   Uebergabe unterliegen bereits vorher hergeleiteten Grenzen.
2. Nur der lebende Observer besitzt den gemeinsamen Zustand je Kindrolle.
   Vor jedem Popen wird `UNUSED -> CLAIMED` atomar vollzogen.
3. Die bestehende direkte Elternrolle erhaelt genau eine lebende
   Startberechtigung. Parallelaufruf, alte Bytes und ein neuer
   `ChildOwner` koennen keinen weiteren Rollenverbrauch erzeugen.
4. Nach dem einzigen Spawn wird der reale Handle vor fehlerfaehiger
   Identitaetspruefung in die Aufraeumverantwortung uebernommen.
   Der Observer adoptiert das Kind und prueft dessen reale Identitaet.
5. Erst jetzt beschreibt `LiveOwnerHandoff` den Zustand `SPAWNED`,
   die realen Eltern-/Kindidentitaeten und die drei gehaltenen Kanaele.
   Der Empfaenger gleicht dies mit seinen vorher bestehenden Erwartungen ab.
6. Die Policy muss vor Kodierung, Allokation und Headerlesen verfuegbar
   sein. Paket und Originalquellen duerfen sie nur exakt erfuellen,
   niemals vergroessern. Alle Handshake-/Claim-/Belegbytes zaehlen mit.
7. Der Worker benoetigt zusaetzlich `RESERVED` und die FG-C01-Pruefung der
   wirklichen, vom Supervisor gehaltenen Reservierung.
8. `SPAWNED` endet in `TERMINAL` oder `FAILED/UNKNOWN`.
   Fehlgeschlagener oder mehrdeutiger Spawn nach `CLAIMED` verbraucht
   ebenfalls den Versuch. Keine Ruecknahme, Wiederherstellung oder Wiederholung.

Der Caller besitzt weiterhin die Einmaligkeit der Observerinvokation;
der Observer besitzt die gemeinsame Kindrollenvergabe. Lokale ChildOwner
behalten Ressourcenverantwortung, nicht eine neue unabhaengige Startquote.
Die Hierarchie Observer -> Starter -> Supervisor -> Worker bleibt erhalten.

### Geschlossene Formen

`BootstrapPolicy` bindet Paket, Metadatenzulassung, Quellenabschluss,
Budgetzertifikat, Originalgroessen und genau drei `RoleLimits`.
Jede Rolle bindet Header-/Bootstrap-/Frame-/Gesamtgroessen, Framezahlen,
Strukturgrenzen, lebenden Speicher, Phasenfristen und Aufraeumreserve.
Der Header bleibt exakt acht Byte. Alle anderen auszufuehrenden Grenzen
muessen vorher aus FG-C02 hergeleitet werden; hier entstehen keine Zahlen.

`LiveOwnerHandoff` ist ausschliesslich ein Beleg nach Adoption:
Versuch, Paket, Policy, aeussere Zulassung, Quellenabschluss, Owner,
Eltern-/Kindidentitaet, Kindrolle, Claimnummer 1 und drei `ChannelBinding`.
Ein Kanal bindet Stromrichtung, direkte Rollen, beide Prozessidentitaeten
und die vom realen Owner gehaltene Handle-Generation.

Nichtzirkulaere Ordnung: Quellen-/Schema-/Budgetbelege -> Paket und
Policy -> unabhaengige Startzulassung -> lebender Owner/Claim ->
beobachtete Kindidentitaet und Handoff. Weder die Policy noch das Paket
enthaelt den Hash seines spaeteren Handoffs oder seiner spaeteren
Startzulassung. Die Zulassung bindet die bereits fertige Policy.

## M2: Urspruengliche Operationsnachweise

### Original und Herkunft

`OriginalOperationEvidence` beschreibt genau eine urspruengliche Operation
mit Versuch, Paket-/Policybindung, Rolle, wirklichem Owner, Phase,
Aufrufreihenfolge, FileRef, qualifizierter Aufrufstelle, Ressourcenrolle,
Handle-Generation, nativer Subjektidentitaet, Aufruf-/Rueckgabestatus,
Originalfehler und Befund.

Die Aufzeichnung stammt von der besitzenden Aufrufgrenze. Sie darf nicht
nachtraeglich aus Exit-Code, lesbarer Datei oder globalem Erfolg entstehen.
Originalbytes bleiben in begrenztem privatem Speicher; ihre spaetere
Uebertragung benutzt den vorhandenen begrenzten Terminalkanal.
Eine lokale Sequenznummer ist nur Reihenfolge, keine native Identitaet.

File-Subjekte behalten die bestehende NTFS-Volume-/File-ID-Form;
Prozesssubjekte die vollstaendige `CreationIdentity`; Pipe-Subjekte
die reale `ChannelBinding`. Handle-Generation und native Identitaet
muessen denselben durchgehend gehaltenen Besitz bezeichnen. Ein spaeteres
Wiederoeffnen kann die Herkunft einer frueheren Schliessung nicht belegen.

Ein erfasster nativer Fehler bleibt original erhalten. Nicht eingetretene,
unterbrochene oder nicht beobachtete Operationen sind nicht bestaetigt.
Ein erfolgreicher Wrapperreturn belegt eine konkrete Unteroperation nur,
wenn die abgenommene Quelle genau diese Folgerung traegt und keinen
zugehoerigen Fehler verschluckt. Ein pauschaler `publish`-/`finish`-
Erfolg ist kein Einzelbeleg fuer jede Schliessung.

### Kontrollspool und fehlende Belege

`ControlTrace.finish -> _ControlSpool.finish -> flush/verify/close`
ist bereits vorhanden. Die eigene Spoolschliessung steht absichtlich
nicht rekursiv im eigenen Kontrolltranskript. Ihr Operationsnachweis muss
deshalb von der besitzenden privaten Aufrufgrenze getrennt gehalten und
nach Rueckkehr ueber den bestehenden Terminalkanal weitergegeben werden.

Wo unveraenderte Bestandsoperatoren einzelne Closeergebnisse oder
Cleanupfehler nicht herausgeben, darf der Wrapper diese nicht erfinden.
Der Beleg bleibt `UNKNOWN`, FG-C06 bleibt dort offen. Dieser Vertrag
genehmigt keine Aenderung an den acht bestehenden Modulen. Ein neuer Hash
eines zusammengefassten Erfolgs schliesst diese Luecke nicht.

Jeder erworbene Handle behaelt genau einen Closeversuch. Fehlende
Beobachtung berechtigt weder zur erneuten Operation noch zur
Erfolgsergaenzung. Primaer- und alle Cleanupfehler bleiben getrennt.

### Relationale Abnahme

`PrivateTerminalBundle` traegt den unveraenderten FG-`TerminalEvidence`
und die begrenzten Originaloperationsbelege. Vorhandene
`ClosureEvidence.operation_receipt_digest` verweisen eindeutig auf deren
kanonische Digests. Originaldatei-FileRefs bleiben wirkliche Dateibelege;
Inlinebelege werden nicht als Dateien ausgegeben.

Die Abnahme erfolgt in dieser Reihenfolge: vorherige Grenzen und lebender
Kanal -> geschlossene Form/Originalbytes/Digest -> Versuch/Paket/Policy/
Owner/Quelle/Phase/Ressource -> wirklicher Operationsausgang ->
eindeutiger Closurebezug -> uebrige FG-Terminalpruefung -> spaeterer Caller.

Ein bestaetigter Closurebeleg benoetigt uebereinstimmende Ressourcenrolle,
Ressourcenart, Subjektidentitaet, Owner, Quelle und Aufrufstelle sowie
einen bestaetigten Originalausgang. `DIRECT_OS` gilt beim wirklichen
Owner; beim Empfaenger ist dies ein delegierter, zusaetzlich kanal- und
quellengebundener Nachweis. Fehlende oder fremde Belege bleiben ablehnend.

Originaloperation -> Closure -> Terminal -> Bundle -> spaeterer Caller.
Kein frueherer Beleg hasht seinen spaeteren Empfaenger oder Abschluss.
Keine neue Datei, Pfadrolle oder rekursive Abschlussaufzeichnung.

## M3: Fehler vor vollstaendiger Prozessidentitaet

`CallerCompletionEvidence.observer_identity` bleibt unveraendert eine
vollstaendige, nicht-nullbare `CreationIdentity`. S2-FI lockert diese
Erfolgsgrenze nicht.

`CallerAssessment` besitzt genau zwei ausdrueckliche Zweige:

- `COMPLETE_IDENTITY`: unveraenderter FG-Callerbeleg. Auch eine bekannte
  Identitaet ist fuer sich kein Erfolg; saemtliche FG-Abschlussregeln gelten.
- `IDENTITY_UNAVAILABLE`: eigener `CallerIdentityFailureEvidence`.
  Dieser kann ausschliesslich `FAILED` oder `UNKNOWN` liefern.

Der Fehlerbeleg trennt `NOT_ATTEMPTED`, `FAILED_NO_CHILD`, `CREATED`
und `UNKNOWN` der Prozesserzeugung. Kein zurueckgegebener Handle beweist
nicht automatisch, dass kein Prozess entstand. `FAILED_NO_CHILD` verlangt
einen eindeutigen Originalnachweis.

PID, Erzeugungszeit und Imagepfad werden jeweils nur soweit wirklich
bekannt angegeben, sonst null. Alle fehlenden Teile stehen explizit in
`missing_evidence`. `NOT_APPLICABLE` gilt nur ohne entstandenes Kind;
`UNAVAILABLE`, wenn kein Identitaetsteil bekannt ist, und `PARTIAL` bei mindestens einem,
aber nicht allen drei bekannten Teilen. Die genaue Form trennt diese Faelle.

Es werden keine Nullwerte als PID, Ersatzdigests, erwarteten Imagepfade
oder Identitaeten aus anderen Versuchen eingesetzt. Der fehlgeschlagene
Erhebungsschritt, Originalfehler, Cleanupfehler und gegebenenfalls schon
beobachteter Exit bleiben erhalten. Eine bekannte falsche Identitaet ist
ein Bindungsfehler, nicht ein fehlender Identitaetsbeleg.

Der Erwerb eines Handles begruendet Aufraeumpflichten bereits vor der
Identitaetserhebung. Er berechtigt nicht zum Schliessen fremder,
nur als Zahl uebermittelter Handles. Ohne entstandenes Kind werden EOF
und Close nicht als erfolgreich erfunden; Nichtanwendbarkeit wird benannt.

Die sechs FG-Statusklassen und ihre Prioritaet bleiben exakt erhalten.
Vor jedem Kind und ohne Nebenwirkung kann eine fehlende Voraussetzung
`BLOCKED_PREREQUISITE` ergeben. Nach unklarer Erzeugung oder bei fehlendem
erforderlichem Terminal-/Closebeleg gilt die vorrangige
`COMPLETION_UNCONFIRMED`-Grenze. Unklarer Verbrauch sperrt weiterhin Retry.
Noch nicht anstehende Schliessungen werden nicht zu erfundenen Closefehlern.

Ein fehlender oder selbst unvollstaendiger Callerfehlerbeleg bleibt ein
aeusserer fehlender Abschluss. Es wird kein weiterer Beobachterprozess
oder Erfolgsmarker erfunden. Eine spaetere Rekonstruktion macht den
abgeschlossenen Fehlerzweig nicht erfolgreich.

## Unveraenderte Pflichten und Belegstand

FG-C01, FG-C02 und FG-C05 bleiben vollstaendig bestehen; M1 praezisiert
nur FG-C03/FG-C04 und M2/M3 nur FG-C06. Alle sechs Codekorrekturen bleiben
nicht umgesetzt. Die 21 Kriterien werden nicht erneut als bestanden
ausgegeben und nicht zu Tests umgedeutet.

Die JSON-Bindung prueft 24 rohe Quellen-/Belegreferenzen. Die vier privaten
S2-FE-Dateien und die acht bestehenden Implementierungsdateien bleiben
bytegleich. Zusaetzlich wird Git auf ausschliessliche Dokumentaenderungen
geprueft. Das ist eine statische Dateipruefung, keine Plattformmessung.

Unveraendert fehlen die S2-FC-Voraussetzungen: vierter Elternpfad samt
Abnahme, Herkunft/Haltbarkeit, vollstaendige Runtime-/Importmenge,
Originalzulassungen, fertiges Startpaket/Budget/Hostrahmen sowie
unabhaengige Start-/Abschlussverantwortung. Historische Metadaten werden
nicht neu erhoben oder zu aktuellen Plattformbelegen erklaert.

Keine Codeaenderungen, Projektimporte, Zustandsfunktionen, Tests,
Plattformaufrufe, Rechteerhoehung, Ledger-Erzeugung, Zielschreibvorgaenge,
Flushes, Recorderstarts oder Matrixzellen. Nur diese Vertragsdokumentation
wird abgelegt und versioniert. Keine neue Laufnummer oder fachliche
Memory-/Feldinterpretation.

## Weiteres Vorgehen

Ein separater statischer Abgleich muss die drei Praezisierungen gegen
S2-FG und S2-FH pruefen. Er darf die noch nicht vorhandene unabhaengige
Bootstrapbereitstellung nicht als bestanden markieren. Eine Wiederholung
des unveraenderten Codeaudits allein kann diese Voraussetzung nicht liefern.

**RUECKMELDUNG ERFORDERLICH vor Codekorrekturen oder Ausfuehrung.**
Diese benoetigen einen eigenen Auftrag. Insbesondere bleibt vor einem
Start die konkrete, quellengebundene und unabhaengig zugelassene
Bootstrap-/Owneruebergabe erforderlich. S2-FC bleibt blockiert.
