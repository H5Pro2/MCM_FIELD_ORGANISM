# S2-FK: Statische Zuordnung des Callerfehlerbelegs

## Status und Grenze

**STATIC_CALLER_FAILURE_CONTAINER_BOUND_AUDIT_PENDING**

Dieser Ergaenzungsvertrag bindet ausschliesslich die Belegzuordnung fuer
FJ-B01 innerhalb von FG-C06/M3: Callerfehler ohne gueltige Observer-Rueckgabe
und ohne vollstaendige Observeridentitaet. Keine Codekorrektur,
Implementierungsabnahme oder Ausfuehrungsfreigabe folgt daraus.

Basis: `5d43b2fcbf8f3329aaafbb9af8feebee0ec9012e`.
Die sechs S2-FG-Regelgruppen, ihre 21 Kriterien und die vorhandenen
FG-Belegformen bleiben unveraendert. Der
[JSON-Vertrag](S2FK_STATISCHE_CALLERFEHLER_BELEGZUORDNUNG_V1.json)
bindet die genaue neue private Huelle und ihre Zuordnungsregeln.
[S2-FJ](S2FJ_STATISCHER_ABGLEICH_S2FI_GEGEN_S2FG_UND_S2FH_V1.json)
wird nicht nachtraeglich als bestanden markiert.

**S2-FC bleibt blockiert:** Die tatsaechliche unabhaengige
Bootstrap-/Owneruebergabe und die weiteren Voraussetzungen sind nicht belegt.

## Ein zustaendiger Fehlercontainer

Der unabhaengige Caller erstellt einen eigenen
`s2fg.terminal-evidence.v1` in der Rolle **Callerfehlercontainer**.
Dieser heisst innerhalb der neuen Huelle `caller_terminal`.
Er ist kein vom Observer zurueckgegebener Terminalbeleg.

Darin liegen die originalen FG-Fehler genau einmal:

- `caller_terminal.primary_failure`: verpflichtender urspruenglicher
  Callerfehler, entsprechend dem bisherigen `identity_failure`.
- `caller_terminal.cleanup_failures`: alle originalen Caller-Cleanupfehler
  in ihrer urspruenglichen Reihenfolge.
- `caller_terminal.missing_evidence`: die allein zustaendige Liste
  fehlender Angaben, einschliesslich der Angaben in beiden Fehlerrollen.

Damit existiert fuer jeden wiederverwendeten `FailureEvidence`
tatsaechlich ein umschliessender `TerminalEvidence`, wie S2-FG verlangt.
Die Fehler werden nicht zusaetzlich in eine danebenliegende
`CallerIdentityFailureEvidence` kopiert. Originalbytes und Digests werden
nicht geaendert, fehlende Angaben nicht nachtraeglich aufgefuellt.

Die neue geschlossene `CallerNoReturnEnvelope` kennzeichnet die Herkunft
durch `CALLER_FAILURE_NO_OBSERVER_RETURN` und `independent_caller`.
Nur fuer diesen Fall ersetzt sie die bisherige alleinstehende
FI-Serialisierung des Zweigs `IDENTITY_UNAVAILABLE`. Dies ist eine explizite
versionierte Vertragskorrektur; kein bestehender V1-Validator wird als
kompatibel behandelt. Andere FI-/FG-Faelle bleiben unveraendert.

## Belegquelle, Owner und Prozessidentitaet

Die Belegquelle ist die unabhaengige aufrufende Instanz mit ihren
urspruenglichen lokalen Beobachtungen. Die Huelle bindet deren
Quell-FileRef, qualifizierte Erzeugungsstelle, abgenommenen Quellenabschluss
und urspruengliche aeussere Zulassung. Ein Hash oder Rollenname schafft
diese Herkunft nicht.

`reporter_identity` bezeichnet den Caller. `caller_terminal.owner_identity`
muss denselben Wert tragen, einschliesslich null bei fehlender Calleridentitaet.
Bekannte Owneridentitaeten in den Originalfehlern muessen diesem Caller
entsprechen; frueher unbekannte Werte bleiben unveraendert null.
Alle hier aufgenommenen Originalfehler stammen von `independent_caller`.
Fremde Fehler oder Owner werden nicht umetikettiert.

Die Observeridentitaet liegt getrennt in `observer_identity_parts`.
PID, Erzeugungszeit und Imagepfad werden nur soweit wirklich beobachtet
angegeben. Calleridentitaet, erwarteter Interpreterpfad, Handlezahl oder
ein frueherer Versuch sind kein Ersatz.

Die vorhandenen FI-Domaenen fuer Prozesserzeugung und Identitaetsstand
bleiben erhalten. Ein nicht zurueckgegebener Handle beweist nicht,
dass kein Prozess erzeugt wurde. Ein erworbener Handle begruendet bereits
vor erfolgreicher Identitaetserhebung die bestehenden Aufraeumpflichten.

`failure_sources` ordnet jedem Originalfehler genau einen Quellbezug zu:
Zielposition im Caller-Terminalbeleg, Originalfehlerdigest, Quell-FileRef
und qualifizierte Fehlerstelle. Die Quelle des Huellenerzeugers ersetzt
nicht die Quelle der fehlgeschlagenen Operation. Unbekannte Herkunft bleibt
null und wird aufgefuehrt; sie gilt nicht als abgenommene Herkunft.

## Wo fehlende Angaben stehen

Alle fehlenden Angaben stehen ausschliesslich in
`caller_terminal.missing_evidence`. Die Eintraege sind eindeutige
Feldlokatoren, beginnend an der Wurzel der `CallerNoReturnEnvelope`.
Sie verwenden Feldnamen und kanonische nullbasierte Listenindizes nach
der JSON-Pointer-Schreibweise.

Damit ist beispielsweise die Position
`/caller_terminal/primary_failure/owner_identity` eindeutig vom Feld
`/observer_identity_parts/pid` getrennt. Das sind statische Feldadressen,
keine erzeugten Versuchsbelege.

Die Liste enthaelt die fehlenden Angaben aller Primaer-/Cleanupfehler,
alle nullwertigen Herkunfts- und Observerangaben sowie stets
`/observer_terminal_evidence_digest` und
`/caller_terminal/live_completion`. Sie ist eindeutig, lexikographisch
sortiert und vorher begrenzt. Bekannte Werte werden nicht als unbekannt markiert.

Nichtanwendbare Angaben bei einem nachweislich nicht erzeugten Prozess
bleiben als abwesend aufgefuehrt. Ihre Anwendbarkeit folgt aus
Erzeugungsstand und tatsaechlicher Phase. Eine fehlende Angabe allein
wird dadurch nicht zu einem erfundenen nativen Closefehler.

Fehlt die eigene Herkunft oder Owneridentitaet des Callers, darf nur
unvollstaendige, ablehnende Fehlerdokumentation verbleiben. Sie ist keine
Berechtigung und kein bestandener unabhaengiger Nachweis.

## Fehlerstatus und Abschlussbezug

`caller_terminal.status` ist der einzige Fehlerstatus. Es gelten die
unveraenderten sechs FG-Raenge; `ISOLATED_RECORDING_COMPLETE` ist fuer
diese Callerfehlerrolle ausgeschlossen. Der Huellenbefund bleibt
ausschliesslich `FAILED` oder `UNKNOWN`.

Vor einem wirklichen oder unklaren Start kann eine fehlende Voraussetzung
bei sonst eindeutiger Lage `BLOCKED_PREREQUISITE` ergeben. Nach
unklarer Prozesserzeugung oder bei fehlendem erforderlichem Abschluss-/
Closebeleg bleibt `COMPLETION_UNCONFIRMED` vorrangig.
Unklarer Verbrauch berechtigt weiterhin nicht zur Wiederholung.

Der Verweis `observer_terminal_evidence_digest` ist zwingend null.
Der wirkliche Digest von `caller_terminal` darf ihn niemals ersetzen.
So bleibt ein vorhandener Callerfehlerbeleg von einer fehlenden
Observer-Rueckgabe unterscheidbar.

`caller_terminal.live_completion` ist ebenfalls zwingend null.
`process_observations`, `closure_evidence` und `original_receipt_refs`
sind in diesem engen Callerfehlercontainer leer. Es werden keine inneren
Prozess-, Recorder- oder Abschlussbelege aus ungueltigen Rueckgaben uebernommen.
Tatsaechliche lokale Observer-Exit-/EOF-/Closebeobachtungen duerfen nur in
den entsprechenden Huellenfeldern nach den bestehenden Originalitaetsregeln
stehen. Sie ersetzen keine erfolgreiche Observerantwort oder Closurekette.

Der Callerbeleg bestaetigt nicht den eigenen zukuenftigen Prozessabschluss
des Callers. Es entsteht kein weiterer Beobachterprozess, Abschlussmarker
oder Dateipfad. Kann auch dieser begrenzte Fehlerbeleg nicht vollstaendig
bereitgestellt werden, bleibt der aeussere Abschluss unbekannt und ablehnend.

## Nichtzirkulaere Bindung und unveraenderte Pflichten

Die Reihenfolge lautet: verfuegbare Originalherkunft und Grenzen ->
Originalfehlerdigests -> Caller-Terminaldigest mit Fehlstellenliste ->
Huellen-Digest mit Herkunfts- und Prozesszuordnung.
Kein innerer Beleg hasht seine spaetere Huelle. Der fehlende
Observerdigest bleibt null.

Alle Groessen, Listen, Kodierung und Validierungsarbeit unterliegen
weiterhin FG-C02/FG-C03. Keine neue Quote, kein Zahlenbeleg und kein
unbegrenzter Fehlerkanal werden eingefuehrt. Ohne vorherige unabhaengige
Grenzen bleibt die Eingabe gesperrt.

Die unveraenderte kanonische Projektion der sechs Regelgruppen und
21 Kriterien lautet:
`d30f91133c4340d919303531ca8e06ab826f28110b563d383ca48a3f28ab4b8a`.
Alle vier FG-Belegformen, ihre Statusrangfolge und die offenen
S2-FC-Voraussetzungen werden unveraendert referenziert.

26 rohe Quellen-/Belegreferenzen und die Dokument-/Selbstdigests der vier
Vorgaenger FG/FH/FI/FJ sind rein statisch geprueft. Keine Codeaenderungen,
Tests, Projektimporte, Plattformaufrufe, Ledger-Erzeugung, Recorderstarts
oder Matrixzellen. Keine neuen Herkunftsbelege und keine Laufnummer.

## Naechster Schritt

Die Zuordnung fuer FJ-B01 ist vertraglich festgelegt, aber noch nicht
separat abgenommen. Als naechster Schritt ist ausschliesslich der gezielte
statische Abgleich dieser Container-, Herkunfts-, Owner-, Fehlstellen- und
Abschlussbindungen sinnvoll. Eine Implementierung oder Ausfuehrung
benoetigt weiterhin eine eigene ausdrueckliche Freigabe.

S2-FC bleibt auch nach einer spaeteren Vertragsabnahme blockiert, bis
insbesondere die unabhaengige Bootstrap-/Owneruebergabe tatsaechlich belegt
und die uebrigen offenen Voraussetzungen abgenommen sind.
