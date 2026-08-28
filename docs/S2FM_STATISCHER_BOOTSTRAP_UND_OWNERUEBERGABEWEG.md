# S2-FM: Statischer Bootstrap- und Owneruebergabeweg

## Status und Auftrag

**STATIC_BOOTSTRAP_ROUTE_DEFINED_NOT_MATERIALIZED_S2FC_BLOCKED**

Festgelegt wird genau ein privater Weg: ein unabhaengiger Caller mit
vorab quellgebundenem Bootstrap-Anker, bestehende Eltern-Kind-Pipes und
eine durchgehende lebende Ownerkette. Dies ist eine normative Auswahl,
keine Bestaetigung ihrer Implementierung oder Plattformtauglichkeit.
Ein tatsaechlicher Bootstrap-/Ownernachweis liegt damit nicht vor.

Basis: `c737f719437e277bf5631a771ec6d6df6af658fb`.
Massgeblich bleiben S2-FG, S2-FH, S2-FI und die Caller-Belegzuordnung
aus S2-FK/S2-FL. FJ-B01 bleibt auf deren enger Vertragsebene geschlossen.
Der [JSON-Vertrag](S2FM_STATISCHER_BOOTSTRAP_UND_OWNERUEBERGABEWEG_V1.json)
bindet Quellen, Rollen, Nachweisobliegenheiten und offene Voraussetzungen.

**S2-FC bleibt blockiert.** Keine Codeaenderung, Testausfuehrung,
native Metadatenerhebung, Plattformausfuehrung, Ledger-Erzeugung,
Recorderstart, Matrixzelle oder neue Laufnummer ist enthalten.

## 1. Unabhaengige Bootstrap-Quelle

Der initiale Owner ist der bereits vor dem Observerstart unabhaengig
abgenommene Caller. Er ist kein vom Recorder erzeugter Prozess und
erhaelt seine Berechtigung nicht aus dessen Rueckgabe. Seine konkrete
aufrufende Quelle, Runtime und aktuelle CreationIdentity sind im
vorliegenden Bestand noch nicht vollstaendig abgenommen. Weder dieser
Chat noch die benutzte Shell wird ersatzweise zum abgenommenen Caller.

Als ausgewaehlter Vor-Eingabe-Weg wird ein passiver, quellgebundener
Bootstrap-Anker festgelegt. Er gehoert kuenftig zur vor dem Start
abgenommenen privaten Eintrittsquelle; die bestehende Quelle
`tools/run_s2fd_isolated_platform_once.py` ist dafuer die Zielrolle,
besitzt diesen Anker aber derzeit nicht. Es entsteht hier weder eine
Konstante noch ein neues Laufzeitobjekt oder eine neue Dateirolle.

Der Anker bindet vorab:

- die unabhaengig erhobene vollstaendige Caller-CreationIdentity;
- den einzigen zulaessigen Rollenbaum und dessen Elternbeziehungen;
- endliche, aus Quellen hergeleitete Grenzen fuer die Zustellung der
  BootstrapPolicy selbst: Bytes, Header, Struktur, Speicher und Fristen;
- die Herkunft dieser Vorgaben aus der unabhaengigen Vorbereitung,
  nicht aus der ersten Nachricht des zu begrenzenden Kanals.

Die kuenftige Vorbereitung muss vor Observerstart abgeschlossen sein.
Ein bereits laufender Caller darf dabei nicht rueckwirkend durch eine
geaenderte oder von ihm noch nicht abgenommene eigene Quelle legitimiert
werden. Ist eine solche Trennung seiner eigenen Quelle von der
vorbereiteten Eintrittsquelle nicht nachweisbar, ist dieser Weg blockiert.
Waehrend eines gestarteten Versuchs darf der Anker nicht geaendert werden.

Es werden hier keine Caller-PID, Startzeit, Runtimeidentitaet oder
numerischen Grenzen erfunden. Ein fehlender Wert bedeutet fehlende
Startvoraussetzung, nicht einen spaeter aus der Pipe ergaenzbaren Default.

## 2. Vor dem ersten Eingabelesen

Der Elternprozess muss Eintrittsquelle und Runtime vor dem Import des
Kindes schuetzen und ihre Herkunft bis zum Abschluss halten. Erst dann
darf die daraus geladene Ankerbindung als unabhaengige Erwartung gelten.
Ein nachtraeglicher SourceLease oder passender Hash ersetzt das nicht.

Vor dem ersten Acht-Byte-Header muss der Empfaenger die tatsaechliche
Eltern-/Kanalkette bis zu diesem Caller mit unabhaengigen Originalbelegen
abgleichen koennen. Ein erwarteter Rollenname oder eine PID aus der
Nachricht, `os.getppid()`, ein Imagepfad oder eine passende Ahnenfolge
allein genuegen nicht. Erforderlich bleiben die aktuellen gehaltenen
Prozess-/Kanalidentitaeten, ihre Erzeugungszuordnung und die lebende
Ownerbindung. Kann dieser Abgleich erst aus dem zu lesenden Payload
hergestellt werden, darf nicht einmal dessen Header gelesen werden.

Die bestehenden parent-owned stdin/stdout-Pipes sind ausschliesslich
Transport. Auf ihnen wird zuerst die unveraenderte FI-BootstrapPolicy
innerhalb der bereits vorhandenen Ankergrenzen zugestellt und abgenommen;
erst danach folgt das vorhandene Startpaket. Die Policy darf weder ihre
eigenen Zustellgrenzen vergroessern noch Elternidentitaet oder Berechtigung
selbst festlegen. stderr bleibt Diagnosekanal. Kein neuer Kanal, Dienst,
privilegierter Launcher oder kryptographisches Verfahren wird ausgewaehlt.

Sender pruefen vor Kodierung und Allokation; Empfaenger vor Header,
Allokation und Dekodierung. Die Policy-Zustellung und alle folgenden
Kontroll-/Paketbytes gehoeren zu denselben fortlaufenden Budgets und
Fristen. Eine neue Kanalhuelle darf keinen Zaehler zuruecksetzen.

**Offene Materialisierung:** Der vorhandene Code liefert diesen
Vor-Eingabe-Abgleich nicht. Der Folgeaudit muss insbesondere nachweisen,
wie die quellgebundene Erwartung ohne einen unautorisierten ersten
Payload zur genauen lebenden Eltern-/Endpointbindung wird. Die Auswahl
des Ankers allein erfuellt FG-C04.A3 ausdruecklich nicht.

## 3. Initialer Owner und begrenzte Uebergaben

Die Hierarchie bleibt:

```text
independent_caller
  -> completion_observer
       -> starter
            -> supervisor
                 -> worker
```

Der Caller bleibt Root-Owner und haelt die einmalige Observerberechtigung
sowie dessen tatsaechliches Prozesshandle. Der completion_observer ist
von Anfang an dieselbe Instanz, die spaeter den Recorderabschluss
auswertet; es wird kein zweiter Abschlussbeobachter gestartet.

Der Observer besitzt allein die gemeinsame Rollenverbrauchsbilanz fuer
starter, supervisor und worker. Starter und Supervisor erhalten jeweils
nur eine begrenzte Erzeugungsberechtigung fuer ihr direktes Kind. Der
Root-Owner wird nicht durch den Starter, Recorder oder eine Belegdatei
ersetzt. Eine neue ChildOwner-Instanz erzeugt kein neues Rollenbudget.

| Grenze | Verbindliche Voraussetzung und Uebergabe | Verantwortlich danach |
|---|---|---|
| Caller -> Observer | Unabhaengige Quellen-/Runtime-/Policyabnahme; einmalige Inanspruchnahme vor Erzeugung; reale Observeridentitaet und Kanaleigentum abnehmen | Caller haelt Observer-Lebenszyklus; Observer erhaelt nur die drei gebundenen Rollenrechte |
| Observer -> Starter | Starterrolle atomar CLAIMED; reales Kind und Kanaleigentum angenommen | Observer haelt gemeinsame Rollenbilanz und sein direktes Kind |
| Starter -> Supervisor | Aktuelle Observerberechtigung fuer genau dieses Eltern-Kind-Paar; Claim vor Erzeugung; Adoption vor Gate | Starter haelt Original-Kindhandle; Observer haelt eigene Beobachtungsreferenz |
| Supervisor -> Worker | Gleiche Claim-/Adoptionsfolge; zusaetzlich RESERVED und FG-C01-Reservierungsabnahme | Supervisor haelt Worker und Reservierung; Worker erhaelt ausschliesslich den gebundenen Recorderauftrag |
| Recorder -> Observer | Originale E0-E8-, Datei-, Prozess- und Closebelege ueber die vorhandene Kette | Observer bewertet; keine Startberechtigung wird zurueckgegeben |
| Observer -> Caller | Originaler Terminalbeleg, danach separat beobachteter Exit, EOF und eigener Handleabschluss | Caller entscheidet den aeusseren Abschluss; kein eigener zukuenftiger Exit wird behauptet |

Jede Kindrolle wechselt einmalig `UNUSED -> CLAIMED` vor Popen und erst
nach realer Adoption zu `SPAWNED`. Danach nur `TERMINAL`, `FAILED` oder
`UNKNOWN`; auch ein mehrdeutiger Spawn nach CLAIMED erlaubt keinen Retry.
Die Observerberechtigung des Callers wird ebenfalls vor Erzeugung
einmalig verbraucht, bleibt aber von den drei Observer-Rollen getrennt.

Ein Prozesshandle verbleibt im Besitz seines Erzeugers. Eine duplizierte
Beobachtungsreferenz ist ein eigenes zu schliessendes Handle, kein Transfer
der Start- oder Terminierungsberechtigung. Pro Kind gibt es genau eine
vorab zugeordnete Terminierungsinstanz: seinen unmittelbaren Erzeuger.
Ownerverlust erlaubt keine stillschweigende Uebernahme durch den Observer.
Nicht bestaetigbares Aufraeumen bleibt entsprechend unbekannt.

## 4. Prozessidentitaet und Nachweiskette

CreationIdentity muss aus dem tatsaechlich gehaltenen Prozesshandle und
der abgenommenen Runtimequelle stammen. Die bestehende vollstaendige
Identitaetsform bleibt unveraendert. Ein numerisches Handle, eine PID,
ein Digest oder ein erwarteter Imagepfad ersetzt diese Identitaet nicht.
Nach der Erzeugung werden Handlebesitz und Cleanupzustand zuerst gehalten;
eine fehlgeschlagene Identitaetsabnahme darf sie nicht verlieren.

Fuer jeden Uebergang muessen mindestens folgende **tatsaechlichen**
Belegbeziehungen vorhanden sein; hier werden keine Instanzen erzeugt:

1. Urspruengliche unabhaengige Callerabnahme mit Quelle, Runtime und
   CreationIdentity, vor dem Observerstart.
2. Vor-Eingabe-Ankerherkunft und geschuetzte Quellen, dazu die abgenommene
   BootstrapPolicy, Budgetherleitung und Originalfreigaben.
3. Ownerseitiger Rollenclaim fuer Versuch, Elternrolle, Kindrolle und
   Paket-/Policy-/Admission-/Quellenbindung vor dem Spawn.
4. Originaler Erzeugungs- und Adoptionsbeleg mit realem Prozess,
   gehaltenen Endpoints und genau diesem Claim.
5. Erst danach der beschreibende FI-LiveOwnerHandoff mit `SPAWNED`,
   vollstaendigen Identitaeten und ChannelBindings.
6. Originale Operationen und Abschluesse nach FI-M2/FG-C06; anschliessend
   Observerterminal und unabhaengige Caller-Abschlussbeobachtung.

Die bestehenden FI-/FG-Formen werden nicht stillschweigend erweitert.
Belegbytes dokumentieren die Ownerkette, sie erzeugen sie nicht.
`START`, `OWNED`, alte Dispatch-/Sealdateien, CLI, Environment, ContextVar
oder passend serialisierte Handoffs sind keine alternative Berechtigung.

Die Digestreihenfolge bleibt azyklisch: zuerst unabhaengige
Vorbereitung/Anker, dann geschlossene Implementierungsquellen und deren
vollstaendige Budgetherleitung, dann Paket und BootstrapPolicy, danach
aeussere Admission, lebende Claims/Adoptionen und Handoffs, zuletzt
Operations-/Terminalbelege und Callerabschluss. Der Anker darf deshalb
keinen Hash seiner eigenen Quelldatei oder eines erst spaeter daraus
gebildeten Pakets enthalten. Die spaetere Quellenbindung deckt ihn ab.
Ein Selbst-Digest beweist Integritaet seiner Bytes, nicht deren Herkunft.

## 5. Fail-Closed und getrennte Belegrollen

Die sechs FG-Statusraenge bleiben unveraendert. Vor jedem Start fuehrt
eine fehlende unabhaengige Identitaet zu `BLOCKED_PREREQUISITE`, ein
bekannter Widerspruch zu `BINDING_REJECTED`, bereits oder mehrdeutig
verbrauchte Berechtigung zu `ALREADY_CONSUMED`, sofern kein hoeherer
FG-Rang gilt. Es gibt keinen Reparaturstart und keine zweite Erhebung
als verdeckten Retry.

Nach einer versuchten Erzeugung verhindern unbekannte Identitaet,
fehlende Adoption oder fehlender erforderlicher Abschluss jede
Erfolgsannahme. `COMPLETION_UNCONFIRMED` hat bei unbekanntem/gescheitertem
erforderlichem Abschluss Vorrang. Primaer- und Cleanupfehler bleiben
mit ihrer urspruenglichen Quelle erhalten. Ein vor jeglichem Start
noch nicht erforderlicher Close wird nicht als Closefehler erfunden.

- **Caller-Terminalbeleg:** dokumentiert die eigenen Originalfehler.
  Im engen FK-Fall ohne Observerreturn und ohne vollstaendige
  Observeridentitaet bleibt `observer_terminal_evidence_digest` null;
  der Caller-Terminaldigest darf ihn nicht ersetzen. Andere Fehlerfaelle
  werden nicht auf diese enge Huelle umgedeutet.
- **Observer-Rueckgabe:** ist ein innerer Beleg, kein Beweis des eigenen
  spaeteren Exits. Auch ein gueltiger Rueckgabedigest genuegt allein nicht.
- **Plattformnachweis:** benoetigt die vollstaendigen Originaloperationen
  und veroeffentlichten Belege sowie den aeusseren Abschluss. Lesbarkeit,
  Vertragsabnahme oder Callerfehlerbeleg kann ihn nicht ersetzen.

## 6. Bestandsgrenze und naechster Schritt

Die sechs FG-Regelgruppen und 21 FH-Kriterien bleiben unveraendert:
`d30f91133c4340d919303531ca8e06ab826f28110b563d383ca48a3f28ab4b8a`.
Keine historische Implementierungsbewertung wird hier hochgestuft.
28 rohe Quellen-/Belegreferenzen sowie sechs Vorgaenger-Selbstdigests
und deren LF-Textbindungen sind dokumentgebunden geprueft.
Die vier privaten Startdateien und acht bestehenden Module bleiben
bytegleich. Es gibt weiterhin nur die bisherigen zwei Owner-Dateirollen
und 133 Recorder-Pfadrollen; keiner dieser Pfade wurde erzeugt.

Die konkrete Callerquelle, ihre unabhaengige Abnahme, die vor dem ersten
Lesen verfuegbare lebende Eltern-/Kanalbindung, vollstaendige numerische
Budgets und alle offenen FC-P01 bis FC-P06 bleiben nachzuweisen.
Auch die vorhandenen Codekorrektur- und Herkunftsluecken bleiben offen.
S2-FM ist kein bestandener Implementierungs- oder Plattformpreflight.

Naechster sinnvoller Schritt ist ein eng begrenzter statischer
Machbarkeits- und Quellenabgleich dieses einen Uebergabewegs. Entscheidend
ist, ob die Anker-/Callerbindung im vorgesehenen Startpfad vor dem ersten
Eingabelesen ohne Zirkelschluss materialisierbar ist. Falls nicht, muss
dieser konkrete Weg als nicht materialisierbar zurueckgegeben werden,
statt einen weiteren blossen Belegcontainer hinzuzufuegen.
Implementierung, Erhebung und Ausfuehrung brauchen weiterhin getrennte
Freigaben; **S2-FC und die 56-Zellen-Matrix bleiben gesperrt**.
