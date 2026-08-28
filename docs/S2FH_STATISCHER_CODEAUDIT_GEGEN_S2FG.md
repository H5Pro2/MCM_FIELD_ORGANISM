# S2-FH: Statischer Codeaudit gegen S2-FG

## Entscheidung

**BLOCKED_CONTRACT_OR_MATERIALIZATION**

Der separate Audit ist durchgefuehrt, aber nicht bestanden. Keine der sechs
S2-FG-Regelgruppen ist vollstaendig auf den Code angewendet. Zusaetzlich sind
Teile der Bootstrap-/Owner- und Fehlernachweisbindung noch nicht eindeutig
materialisierbar. S2-FC bleibt blockiert. Keine Implementierungs-, Test-,
Plattform- oder Matrixfreigabe folgt aus diesem Dokument.

Gepruefter Stand: `f57d1162b2969caec01c27717c2119bb42060457`.
Die vier privaten Dateien sind bytegleich mit dem S2-FE-Stand. S2-FG war
ausdruecklich nur ein Korrekturvertrag, keine Korrekturimplementierung.
Der Befund beschreibt daher keine neu beobachtete Laufregression.

Der [JSON-Beleg](S2FH_STATISCHER_CODEAUDIT_GEGEN_S2FG_V1.json) ordnet alle
21 statischen Abnahmekriterien den sechs Regelgruppen zu. Diese Kriterien
wurden gelesen und gegen den Code abgeglichen, nicht als Tests ausgefuehrt.

## Sechs Regelgruppen

### FG-C01: Reservierungszugriff nicht umgestellt

Die Sollregel fuer den getrennten, rollen- und ownergebundenen Leser ist
lokal konsistent. Der Worker benutzt jedoch weiterhin `lease.read_exact`
und damit den normalen `read_source`-Pfad. Der geforderte Verifikationsmodus
wird fuer die Reservierung nicht ausgewaehlt. Die zusaetzliche Bindung an
die native Identitaet des gehaltenen Supervisorhandles fehlt ebenfalls.

Fundstellen: `tools/run_s2fd_isolated_platform_once.py:81`,
`mcm_field_organism/_s2fd_start_owner.py:63`,
`mcm_field_organism/_s2er_windows_files.py:68` und `:174`.
FF-B01 bleibt offen; seine technische Umsetzung haengt auch von FG-C04 ab.

### FG-C02: Budgetbeweis weiterhin unvollstaendig

Die Trennung von Rechnung, Annahmeabnahme und Hostbeleg ist nachvollziehbar.
Vorhanden ist aber weiterhin nur die Pruefung eingereichter Kostenzeilen und
AST-Orte. Rollen-/Phasen-/Aufrufkantenbeweise, vollstaendige Multiplikitaeten,
Runtimekosten, Bootstrap-/Diagnosehuellen und der Hostrahmen sind nicht
vollstaendig gebunden. Es liegt kein numerischer Ausfuehrungsbeleg vor.

Fundstellen: `mcm_field_organism/_s2fd_start_contract.py:249`, `:276`,
`:295`, `:315`, `:329`; S2-FG-JSON `/numerical_status`.
Die bekannte Zahl der Quellbytes oder AST-Knoten wird nicht als Budget
gewertet. Die ehrliche Nichtmaterialisierung ist korrekt, aber keine Abnahme.

### FG-C03: Vorabgrenzen fehlen im Bootstrap

Die Sollreihenfolge ist konsistent: Grenzen vor Lesen, Allokation und
Dekodierung. Im Code wird die positive Headerlaenge noch vor jeder
unabhaengigen Policypruefung eingelesen und verarbeitet. Die Budgetpruefung
folgt erst nach `unwire_package`. Der Sender kodiert ebenfalls vor der
abschliessenden Schreibbudgetpruefung; die neuen gemeinsamen Phasen- und
Framegrenzen sind nicht umgesetzt.

Fundstellen: `tools/run_s2fd_isolated_platform_once.py:30`, `:162`, `:166`,
`mcm_field_organism/_s2fd_start_owner.py:147`, `:179`,
`mcm_field_organism/_s2fd_completion_observer.py:118`.
Hinzu kommt die offene Materialisierung unter M1.

### FG-C04: Keine durchgaengige lebende Rollenberechtigung

Die Forderung, Beleggleichheit nicht als Berechtigung zu behandeln, ist
konsistent. Der aeussere Owner besitzt eine Einmalpruefung. Die Kindpfade
pruefen hingegen weiterhin vorhandene Handoffbytes und den realen
Pipe-Elternprozess; `ChildOwner` beginnt je Instanz mit leeren Mengen.
Die in S2-FG verlangte gemeinsame atomare Rollenvergabe durch den lebenden
Owner ist nicht vorhanden.

Fundstellen: `mcm_field_organism/_s2fd_start_owner.py:35`, `:128`, `:209`,
`:246`; `tools/run_s2fd_isolated_platform_once.py:14`, `:51`.
Unter der bereits in S2-FF genannten Bedingung eines spaeter gueltigen Pakets
sind alte Belegbytes allein weiterhin kein statischer Einmaligkeitsbeweis.
Es wurde weder ein Paket konstruiert noch ein Wiedereintritt ausgefuehrt.

### FG-C05: Herkunftsregeln nicht vollstaendig umgesetzt

Die exakte S2-FB-Rolle, Interpreter-/Runtimegleichheit und vollstaendige
Importmenge sind sachlich vereinbar. Der Code erlaubt fuer den Layoutvertrag
weiterhin irgendeine historische Referenz. Die Importliste muss nur die
vier Infrastrukturquellen enthalten. Interpreterreferenz und deklarierte
Runtimeidentitaet werden nicht vollstaendig miteinander abgeglichen.

Fundstellen: `mcm_field_organism/_s2fd_start_contract.py:389`, `:419`,
`:478`, `:500`; `tools/run_s2fd_isolated_platform_once.py:155`.
Eine Eltern-Lease ist vorhanden, ihre vollstaendige Quellabdeckung vor den
Kindimports ist jedoch nicht abgenommen. Archivierte Metadaten werden
nicht als aktuelle Runtime- oder vierte Elternidentitaet umgedeutet.

### FG-C06: Fehlerkette und Nachweisformen nicht umgesetzt

Der private Wrapper verwirft weiterhin den Rueckgabewert von `abort()`.
Der Observer klassifiziert andere Ausnahmetypen als `StartError` pauschal;
die geforderten getrennten Primaer-/Cleanupbelege fehlen. Die neuen
S2-FG-Nachweisformen haben keine Validatoren oder Callsite-Anbindung im Code.
Der bestehende geschlossene V1-Vertrag ist kein Ersatz dafuer.

Fundstellen: `tools/run_s2fd_isolated_platform_once.py:137`,
`mcm_field_organism/_s2ex_recorder_supervisor.py:328`,
`mcm_field_organism/_s2fd_completion_observer.py:390`,
`mcm_field_organism/_s2fd_start_contract.py:45`.

Eigene native Prozesshandles, Identitaets-/Exitpruefung und
`control.finish()` vor Erfolgsrueckgabe sind im Bestand vorhanden. Sie
werden nicht als fehlend bezeichnet. Die delegierte Pipe-/Kontrollabnahme
bleibt aber ueber `finish(role, True)` und `control_close_observed=success`
zusammengefasst. Die geforderte getrennte Herkunft fehlt.
Fundstellen: `_s2fd_completion_observer.py:200`, `:361`, `:414`;
`_s2ex_recorder_supervisor.py:320`.

## Verbleibende Materialisierungsfragen

Diese Punkte liegen innerhalb der sechs vorhandenen Blocker. Sie sind
keine neuen Funktionen und keine ausgefuehrten Negativtests.

**M1, FG-C03/FG-C04:** `BootstrapPolicy` und `LiveOwnerContext` sind Listen
erforderlicher Inhalte, keine vollstaendig gebundenen Eingabe-/Uebergabeformen.
Der konkrete unabhaengige Vertrauensanker, seine Bereitstellung vor dem
Payloadlesen und der Rollenverbrauch ueber die bestehenden Prozesskanaele
sind nicht festgelegt. Ein bloss als vertrauenswuerdig bezeichnetes Objekt
oder weitere passende Digests wuerden FF-B04 nicht schliessen. S2-FG nennt
diese Grenze selbst offen. Dies ist Unvollstaendigkeit, kein behaupteter
Widerspruch seiner Sicherheitsabsicht. Fundstellen im S2-FG-JSON:
`/proof_shapes/BootstrapPolicy`, `/proof_shapes/LiveOwnerContext` (Zeilen 321, 335).

**M2, FG-C06:** `ClosureEvidence.operation_receipt_digest` soll Original-
Operationsbelege binden. Deren konkrete geschlossene Originalform,
Bereitstellung und Abnahme sind aber nicht festgelegt. Der Digest allein
belegt weder die Operation noch deren Herkunft. Die bestehende
Kontrollspool-Schliessung wird nicht dadurch unabhaengig belegt, dass sie
nachtraeglich einen weiteren Hash erhaelt. Fundstelle:
`/evidence_forms/ClosureEvidence/fields/operation_receipt_digest` (Zeile 396).

**M3, FG-C06:** `CallerCompletionEvidence.observer_identity` ist zwingend
eine vollstaendige `CreationIdentity`; null ist dort nicht zulaessig.
Fuer einen Fehler vor erfolgreicher Identitaetserhebung gibt es damit
keine ausdrueckliche Darstellung in dieser Callerform. Andere Fehlerformen
erlauben unbekannte Identitaeten, ihre Verwendung als aeusserer Ersatzbeleg
ist jedoch nicht gebunden. Benannt werden muessen der zulaessige Beleg und
seine Ablehnungskriterien, ohne eine Identitaet zu erfinden. Fundstellen:
`/evidence_forms/CallerCompletionEvidence` (Zeile 433),
`/closed_form_rules` und `/failure_rules/no_return`.
Das ist eine Luecke fuer fruehe Fehlerfaelle, kein beobachteter falscher Erfolg.

Die sechs Statusklassen und die Trennung zwischen Observer-Rueckgabe und
spaeterem Caller-Exitbeleg lassen sich dagegen ohne Selbsthash anwenden.
Eine noch gar nicht anstehende Schliessung ist nicht automatisch ein
fehlgeschlagener Close. Unbekannte benoetigte Evidenz bleibt ablehnend.
Eine globale Behauptung vollstaendiger Widerspruchsfreiheit ist angesichts
M1 bis M3 nicht gerechtfertigt.

## Belege und Grenzen

- 22 geerbte FileRefs und S2-FG selbst sind bytegebunden geprueft; die vier
  Selbstdigests S2-FD/FE/FF/FG sowie der LF-kanonische S2-FG-Textbeleg stimmen.
- Keine Codeabweichung gegen S2-FE und keine neue Testdatei. Der Vergleich
  mit dem Git-Stand bestaetigt dies zusaetzlich zur Rohbytepruefung.
- Der aktuelle Status der sechs S2-FC-Voraussetzungen bleibt unveraendert:
  vierter Elternpfad, Herkunft/Haltbarkeit, Runtime-/Importmenge, innere und
  aeussere Zulassung, komplettes Paket/Budget/Hostrahmen und unabhaengiger Caller.
- Der alte Befund zum fehlenden Ledger wurde nicht nativ neu erhoben.
  Keine Tests, Projektimporte, Projektfunktionen, Plattformaufrufe,
  Rechteerhoehung, Ledger-Erzeugung, Zielschreibvorgaenge, Flushes,
  Recorderstarts oder Matrixzellen. Keine neue Laufnummer oder fachliche
  Memory-/Feldinterpretation.

## Konsequenz

Ein weiterer Audit desselben unveraenderten Codes kann die offenen
Korrekturen nicht ersetzen. Vor einer vollstaendigen privaten Umsetzung
muss insbesondere M1 bis M3 eine konkrete, pruefbare Bindung erhalten.
Die bestehenden Korrekturpflichten FG-C01 bis FG-C06 bleiben erhalten;
dieser Audit repariert oder erweitert S2-FG nicht.

**RUECKMELDUNG ERFORDERLICH:** Naechster Vorschlag ist S2-FI als eng begrenzte
statische Materialisierungsbindung fuer M1 bis M3. Keine neue Lauf- oder
Codefreigabe. Anschliessende Codekorrekturen benoetigen einen separaten
Auftrag; die Herkunfts- und Budgetbelege bleiben weiterhin erforderlich.
