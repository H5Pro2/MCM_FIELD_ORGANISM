# S2-FF: Statischer Codeaudit der Startinfrastruktur

## Entscheidung

**BLOCKED_STATIC_CODE_AUDIT**

S2-FF ist durchgefuehrt, aber nicht bestanden. Die vier privaten S2-FE-Dateien
werden nicht zur Ausfuehrung abgenommen. S2-FC bleibt blockiert; S2-EM,
Recorder und die 56-Zellen-Matrix bleiben gesperrt.

Gepruefter Commit: `cca4af8db342405c79703daf5d76180f32467d1b`.
Vertragsgrundlage sind S2-FD und der unveraenderte S2-FE-Implementierungsbeleg.
Der maschinenlesbare Befund steht in
[S2FF_STATISCHER_CODEAUDIT_STARTINFRASTRUKTUR_V1.json](S2FF_STATISCHER_CODEAUDIT_STARTINFRASTRUKTUR_V1.json).

Die folgenden sechs Blocker sind statische Befunde, keine beobachteten
Plattformfehler. Es wurden weder Fehler injiziert noch Projektmodule importiert
oder Projektfunktionen aufgerufen. Keine Korrekturimplementierung in S2-FF.

## FF-B01: Unvereinbarer Reservierungszugriff

Prioritaet P1. Der Worker liest `platform_reservation` vor `record_worker`
ueber `SourceLease.read_exact`. Dieser Weg benutzt `WindowsFiles.read_source`
und damit `_open(..., verification=False)`. Der Lesehandle teilt nur Lesen.
Der Supervisor haelt zu diesem Zeitpunkt den mit Lese-/Schreibzugriff
erzeugten Reservierungshandle noch offen. Erst nach Capture/Publikation
wird sein Backend geschlossen.

Fundstellen: `tools/run_s2fd_isolated_platform_once.py:81`,
`mcm_field_organism/_s2fd_start_owner.py:67`,
`mcm_field_organism/_s2er_windows_files.py:68` und `:174`,
`mcm_field_organism/_s2ex_recorder_supervisor.py:163` und `:320`.

Nach der dokumentierten bidirektionalen Windows-Sharingpruefung ist dieser
zweite Open nicht mit dem bestehenden Schreibzugriff vereinbar. Daraus folgt
statisch ein `ERROR_SHARING_VIOLATION`, sofern der vorgesehene Ablauf bis zu
diesem Zugriff erreicht wird. Das ist keine vor Ort gemessene Fehlernummer.
[Microsoft: CreateFileW, dwShareMode](https://learn.microsoft.com/en-us/windows/win32/api/fileapi/nf-fileapi-createfilew).

Die Korrektur muss den privaten Leser mit der gehaltenen Reservierung
vereinbaren, ohne Schreibschutz, Quellidentitaet oder bestehendes Backend
pauschal aufzuweichen. Der bestehende Kern wird hier nicht geaendert.

## FF-B02: Numerischer Budgetnachweis nicht hergeleitet

Prioritaet P1. S2-FE liefert ausdruecklich keinen vollstaendigen numerischen
Budgetbeleg. Der Audit kann diesen deshalb nicht bestaetigen.
`derive_budget_certificate` prueft uebergebene Kostenzeilen, Quellorte und
Ganzzahlarithmetik. Die Funktion weist selbst darauf hin, dass die Wahrheit
der eingereichten Schleifen- und Schemaannahmen separat abzunehmen ist.

Fundstellen: `mcm_field_organism/_s2fd_start_contract.py:249`, `:276`,
`:295`, `:303`, `:315`, `:327` und `:329`.

Die Quellortabdeckung beweist weder Ausfuehrungshaeufigkeit noch Kostenklasse.
`iteration_bound`, `input_bounds` und `primitive_cost` werden nicht aus einem
vollstaendigen Aufrufgraphen gewonnen. Abdeckung in einer beliebigen Domaene
belegt nicht, dass native Aufrufe, logische Paare, Validierung und Cleanup
jeweils vollstaendig gezaehlt sind. Nichtleere Annahmetexte ersetzen diesen
Nachweis nicht.

Auch die geordnete Groessenliste ist noch kein abgenommener Bytebeweis:
Konstante Ausdruecke sind moeglich; `transcript >= 4 * worker_raw` allein
deckt die JSON-Huellen fuer Ein-Byte-Fragmente nicht ab. Der Puffer wird nur
als positive Zahl geprueft. Bootstrap, alle Originalbytes samt Base64/JSON,
gleichzeitig gehaltene Kopien, Prozessphasen und Fehlerpfade brauchen eigene
nachvollziehbare Beitraege. Der Hostrahmen ist ebenfalls erst einzureichen
und unabhaengig abzunehmen.

Die bestaetigten 75.623 Quellbytes und 975 AST-Aufrufknoten sind ausschliesslich
Inventar. Sie sind keine numerischen Laufbudgets. Es wurden keine willkuerlichen
Grenzwerte eingesetzt. Die spaetere Abnahme braucht eine vollstaendige,
quellgebundene Kostenrechnung einschliesslich ihrer Annahmen; eine automatische
allgemeine Programmkostenbeweisfunktion wird dadurch nicht verlangt.

## FF-B03: Bootstrap-Grenze greift zu spaet

Prioritaet P1. `_read_bootstrap` akzeptiert eine positive 8-Byte-Laenge,
liest deren gesamten Inhalt blockierend, sammelt Fragmente und dekodiert JSON.
Danach dekodiert `unwire_package` die Originalquellen und validiert das Paket.
Erst anschliessend wird `consumed <= maximum_ipc_bytes` geprueft.

Fundstellen: `tools/run_s2fd_isolated_platform_once.py:30` und `:162`,
`mcm_field_organism/_s2fd_start_owner.py:147`,
`mcm_field_organism/_s2fd_completion_observer.py:118`.

Die Laenge ist mathematisch endlich, aber vor Allokation und Parsing nicht
an das zugelassene Ressourcenbudget gebunden. Auch der Sender materialisiert
die kodierte Huelle vor seiner Schreibbudgetpruefung. Die vorgesehene
Elternfrist begrenzt nicht die zuvor belegte Speichermenge. Eine eigenstaendig
gebundene Bootstrap-Grenze und ihre Kosten muessen vor diesen Arbeiten gelten;
die Grenzen duerfen nicht erst aus dem unbegrenzt eingelesenen Paket stammen.

## FF-B04: Kindstart nicht an lebenden Einmal-Owner gebunden

Prioritaet P1. Der aeussere Observer prueft einen standardmaessig leeren
Vertrauenskontext und verbraucht die lokale Einmalfreigabe. Diese Pruefung
liegt nicht auf dem direkten Kind-Einstiegspfad.

Fundstellen: `mcm_field_organism/_s2fd_start_owner.py:35`, `:128`, `:209`
und `:246`; `tools/run_s2fd_isolated_platform_once.py:14`, `:51` und `:150`.

`validate_handoff` akzeptiert passende bereits vorhandene Dispatch-/Sealbytes.
`_parent_pipe` bestaetigt den tatsaechlichen Elternprozess der Pipe, aber nicht
dessen zugelassene Rolle und einmaligen Startbesitz. Ein neues
`ChildOwner`-Objekt beginnt mit leerer Verbrauchsmenge. Der Starter erzeugt
nach passender Huelle und `START` einen Supervisor, ohne einen neuen lebenden
Owner-Nachweis gegen die aeussere Einmalfreigabe zu pruefen.

Damit laesst sich statisch keine dauerhafte Einmaligkeit der Kindstarts
begruenden: Unter der ausdruecklichen Annahme eines spaeter gueltigen Pakets
und noch vorhandener passender Belege unterscheidet der Kindpfad einen
berechtigten aktuellen Aufruf nicht von der erneuten Vorlage dieser Bytes
durch einen anderen realen Elternprozess. Spaetere Dateikollisionen koennen
den Recorder stoppen, verhindern aber den vorherigen erneuten Prozessstart
nicht. Dies wurde nicht ausgefuehrt; es wird weder ein aktuelles gueltiges
Startpaket noch ein erfolgreicher Recorder-Bypass behauptet.

Erforderlich ist eine vorab definierte Bindung zwischen aktuellem Owner,
Kindrolle, Kanalherkunft und einmaliger Startberechtigung. Ein Digest beweist
die Uebereinstimmung von Daten, nicht allein die Berechtigung zu deren Nutzung.

## FF-B05: Ausfuehrungsherkunft nicht vollstaendig geschlossen

Prioritaet P1. Die Importlisten muessen die vier Infrastrukturdateien enthalten;
deren Vollstaendigkeit als tatsaechliche transitive Bootstrap-/Runtime-Menge
wird dadurch nicht bewiesen. Der Interpreter ist an seine eigene FileRef und
die Runtime-Leseliste gebunden, aber nicht relational an die im SourceManifest
deklarierte Runtime-Identitaet. `sys.executable` wird spaeter nur mit dem
Prozessplan verglichen.

Fundstellen: `mcm_field_organism/_s2fd_start_contract.py:363`, `:419`,
`:441`, `:478` und `:500`; `tools/run_s2fd_isolated_platform_once.py:155`.

`layout_contract_file` muss lediglich irgendeine der historischen Referenzen
sein, nicht genau der gebundene S2-FB-Layoutvertrag. Hashgleichheit eines
referenzierten Belegs und eine nichtleere `reviewer_identity` ersetzen keine
inhaltliche Herkunftsabnahme. Die vier Elternpfade sind relational geprueft;
ihre zukuenftige unabhaengige native Abnahme bleibt davon getrennt.

Der Kind-Einstieg importiert die privaten Module vor der spaeteren
`SourceLease`-Pruefung. Eine gelesene Dateiliste ist daher fuer sich kein
Beleg, welche Bytes beim Bootstrap tatsaechlich ausgefuehrt wurden. Die
Eltern-Lease ist ein vorhandener Schutz im ordentlichen Startpfad; dessen
abgenommene Vollstaendigkeit und die Kindberechtigung aus FF-B04 fehlen noch.

Der Korrekturumfang muss sowohl die konkreten relationalen Luecken als auch
die explizite externe Vertrauensgrenze binden. Hier werden keine neuen
Runtime-Dateien oder nativen Metadaten erhoben.

## FF-B06: Fehler- und Abschlussbeobachtung nicht lueckenlos

Prioritaet P2. `_supervisor` verwirft den Rueckgabewert von `supervisor.abort()`.
Der Bestandsoperator gibt Close-/Cleanupfehler als Tupel zurueck. Ein dabei
gemeldeter Schliessfehler wird somit nicht als solcher weitergebunden.

Fundstellen: `tools/run_s2fd_isolated_platform_once.py:137`,
`mcm_field_organism/_s2ex_recorder_supervisor.py:328`,
`mcm_field_organism/_s2fd_completion_observer.py:390`.

Der aeussere Handler uebernimmt nur `StartError.status`; andere Fehlertypen
werden allgemein `ABORTED_INCOMPLETE`. Damit werden insbesondere native
Voraussetzungsfehler aus der Quellen-Lease nicht phasengerecht uebertragen.
Die Startfreigabe und Kanalpruefung liegen zudem vor dem Ergebnis-try-Block;
dort muss der unabhaengige Aufrufer den fehlenden Abschluss behandeln.
Der Pfad bleibt ablehnend, aber die geforderte Herkunft und Statusklassifikation
der Fehler ist nicht vollstaendig.

Der Abschlussbeobachter besitzt tatsaechlich eigene Prozesshandles und
fragt Identitaet und Exit-Code ab. Das ist im Code vorhanden, nicht ausgefuehrt.
Davon zu trennen sind delegierte Pipe-/Kontrollabschluesse:
`pipe_closures` wird von Kindrollen gemeldet, `finish(role, True)` uebernimmt
die Aussage, und `control_close_observed` wird aus dem Gesamterfolg gesetzt
(`_s2fd_completion_observer.py:200`, `:359`, `:414`). Die bestehende
Supervisorreihenfolge ruft `control.finish()` vor ihrer Erfolgsrueckgabe auf;
es waere falsch, diese Pruefung als nicht vorhanden zu bezeichnen.
Ihre Beweiskette haengt jedoch von der noch offenen Quell-/Ownerabnahme ab.
Direkte OS-Beobachtung und delegierte, quellgebundene Abschlussaussagen
muessen im Korrekturvertrag unterscheidbar bleiben. Ein Prozessende allein
beweist keinen erfolgreichen expliziten Datei-Close.

## Bestaetigter Teilumfang

- Genau vier private neue Python-Dateien; 19 Quell-/Belegbindungen stimmen
  bytegenau mit S2-FE ueberein. S2-FD- und S2-FE-Selbstdigests stimmen.
- AST- und Symboltabellenpruefung der vier Quellen ohne Import: keine
  Syntaxfehler und keine statisch unaufgeloesten globalen Namen.
- Geschlossene Paketformen, kanonische Digests, getrennte feste Ownerpfade
  und kein automatisches Anlegen des Ledger-Verzeichnisses sind vorhanden.
- Der regulaere Observerpfad verbraucht die Freigabe vor Dispatch und startet
  den ersten Kindprozess erst nach Rueckkehr aus `reserve_dispatch`.
- Bestehende Belege oder Teilbelege werden im regulaeren Reservierungspfad
  nicht geloescht oder als neue freie Gelegenheit umgedeutet.
- Urspruengliche Report-/Trace-/Manifest-/Markerbytes werden gegen Receipts
  geprueft. Das behebt nicht die oben genannten Herkunfts- und Abschlussluecken.

Dies ist keine Teilfreigabe zur Ausfuehrung und keine vollstaendige
Funktionskorrektheitsgarantie. Insbesondere sind statische Syntaxabnahme,
Budgetabnahme, nativer Herkunftsbeleg und Plattformabschluss getrennte Dinge.

## Offene S2-FC-Voraussetzungen

Der archivierte Metadatenbeleg bleibt unveraendert. Er dokumentiert drei
Eltern und ein damals fehlendes Ledger. Sein Zustand wurde nicht erneut
nativ erhoben. Es fehlen weiterhin:

1. eingerichteter und unabhaengig abgenommener vierter Elternpfad;
2. Herkunfts-/Haltbarkeitsbeleg fuer diesen Pfad und den vorgesehenen Abschluss;
3. vollstaendig abgenommene tatsaechliche Runtime-/Importabschlussmenge;
4. originale innere Freigabe-/Reviewbytes und unabhaengige aeussere Startabnahme;
5. vollstaendiges Startpaket mit quellabgeleiteten numerischen Budgets und
   abgenommenem Hostrahmen;
6. unabhaengig gebundener Aufrufer, der den terminalen Observerabschluss sieht.

Diese fehlenden Belege duerfen nicht durch angenommene Werte, alte
Metadaten oder diesen Audit ersetzt werden. Auch nach Behebung der Codeblocker
waere S2-FC ohne diese Voraussetzungen weiter blockiert.

## Umfang und Fortsetzung

Nur dieser Audit und sein JSON-Beleg wurden neu angelegt. Keine Aenderung
der vier geprueften Quellen, der acht Bestandsmodule, von TSPM-1, PPB-1,
API, Snapshot, Feldpfad oder Runner. Keine Tests, Plattformaufrufe,
Metadatenerhebung, Ledger-Erzeugung, Zielschreibvorgaenge, Flushes,
Recorderstarts oder Matrixzellen. Keine neue Laufnummer und keine fachliche
Memory- oder Feldinterpretation.

**RUECKMELDUNG ERFORDERLICH:** Als naechsten Schritt S2-FG ausschliesslich als
statischen Korrekturvertrag fuer FF-B01 bis FF-B06 freigeben. Er soll die
Korrekturen und fehlenden Beweisrollen binden, noch keinen Code aendern oder
eine Ausfuehrung erlauben. Anschliessende Implementierung und erneuter Audit
bleiben separat zu entscheiden.
