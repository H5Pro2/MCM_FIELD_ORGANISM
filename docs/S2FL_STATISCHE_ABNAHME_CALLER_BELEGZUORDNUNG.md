# S2-FL: Gezielte statische Abnahme der Caller-Belegzuordnung

## Ergebnis und Abnahmeumfang

**STATIC_CALLER_EVIDENCE_ASSIGNMENT_ACCEPTED_S2FC_BLOCKED**

Die gezielte statische Abnahme von S2-FK ist bestanden.
FJ-B01 ist **ausschliesslich hinsichtlich der vertraglichen
Callerfehler-Belegzuordnung** geschlossen. Im freigegebenen Pruefumfang
wurde keine weitere Zuordnungsluecke festgestellt.

Dies ist weder eine Codeabnahme noch die Abnahme eines erzeugten
Callerbelegs, eines Plattformlaufs oder einer realen Owneruebergabe.
S2-FC bleibt blockiert. Die alten Auditbefunde werden nicht
nachtraeglich geaendert.

Basis: `62ea08b6ea8967f7169c4a6bf2681f0a6f0ec39e`.
Geprueft wurden [S2-FK](S2FK_STATISCHE_CALLERFEHLER_BELEGZUORDNUNG_V1.json),
der konkrete [Befund FJ-B01](S2FJ_STATISCHER_ABGLEICH_S2FI_GEGEN_S2FG_UND_S2FH_V1.json)
und die unveraenderten FG-/FH-/FI-Bindungen.
Der [JSON-Auditbeleg](S2FL_STATISCHE_ABNAHME_CALLER_BELEGZUORDNUNG_V1.json)
haelt Quellen, Fundstellen, Kriterienerhalt und Abnahmegrenzen fest.

## Zustaendiger Beleg

Die urspruenglichen lokalen Beobachtungen stammen weiterhin vom
unabhaengigen Caller. Dessen `caller_terminal` ist der zustaendige
umschliessende FG-`TerminalEvidence`, nicht die Quelle einer
Observerantwort.

Primaer- und Cleanupfehler liegen jeweils genau einmal unter
`caller_terminal.primary_failure` beziehungsweise
`caller_terminal.cleanup_failures`. Fehlende Angaben werden allein
in `caller_terminal.missing_evidence` gefuehrt.
Damit ist die in FG geforderte umschliessende Belegrolle vorhanden.
Die Fehler werden nicht mehr in einer danebenliegenden FI-Huelle dupliziert.

Die Korrektur ist ausdruecklich versioniert und auf den Fall ohne gueltigen
Observerreturn und ohne vollstaendige Observeridentitaet beschraenkt.
Andere Callerfaelle und bestehende V1-Validatoren werden nicht umgedeutet.

Fundstellen: S2-FK-JSON `/bindings/selection`,
`/bindings/sole_failure_container` und
`/bindings/missing_evidence_owner`; S2-FG-JSON
`/evidence_forms/FailureEvidence/rules/0`.

## Quelle, Owner, Prozess und Fehlerstatus

Die Quelle des Huellenerzeugers ist von der Quelle der fehlgeschlagenen
Operation getrennt. `failure_sources` bindet jede urspruengliche
Fehlerposition an ihren unveraenderten Digest, FileRef und Aufrufort.
Fremde oder unpassende Belege werden nicht repariert.

`reporter_identity` und `caller_terminal.owner_identity` bezeichnen
denselben Caller. Die beobachtete Observeridentitaet steht separat in
`observer_identity_parts`. Unbekannte Werte bleiben null und erhalten
einen eindeutigen Feldlokator in der Fehlstellenliste. Ein Prozesshandle,
erwarteter Imagepfad oder Caller-PID ersetzt keine Observeridentitaet.

Originalfehler behalten Phase, Herkunft, Code und native Fehlerangaben.
Der Containerstatus folgt den unveraenderten FG-Prioritaeten.
`ISOLATED_RECORDING_COMPLETE` ist ausgeschlossen; der Huellenbefund
bleibt `FAILED` oder `UNKNOWN`. Nichtanwendbare Angaben vor einem
nachweislich nicht erfolgten Start werden nicht zu erfundenen Closefehlern.

Eine unbekannte Callerherkunft darf weiterhin nur unvollstaendige,
ablehnende Dokumentation ergeben. Die beschreibenden Datenformen
begruenden keine Start- oder Aufraeumberechtigung fuer fremde Handles.

Fundstellen: S2-FK-JSON `/bindings/source_and_owner`,
`/failure_source_mapping`, `/bindings/status_and_completion`
und `/termination_constraints`.

## Abgrenzung zum Observer und zur Plattform

`observer_terminal_evidence_digest` bleibt zwingend null.
Der Caller-Terminaldigest darf ihn nicht ersetzen.
`caller_terminal.live_completion` bleibt null; die inneren Prozess-,
Closure- und Recorderdateilisten bleiben in diesem Fehlercontainer leer.

Ein vorhandener Callerfehlerbeleg kann deshalb nicht als vorhandene
Observerantwort oder bestaetigte Plattformveroeffentlichung gelten.
Tatsaechliche lokale Exit-/EOF-/Closeangaben bleiben den bestehenden
Originalitaetsregeln unterworfen. Sie liefern hier keinen erfolgreichen
Gesamtabschluss.

Originalfehler -> Caller-Terminalbeleg -> Herkunftshuelle ist
nichtzirkulaer. Feldlokatoren sind Namen und enthalten keinen Hash der
spaeteren Huelle. Der Caller behauptet nicht seinen eigenen zukuenftigen
Prozessabschluss; kein weiterer Beobachter oder Abschlussmarker entsteht.

Fundstellen: S2-FK-JSON `/placement`,
`/bindings/digest_order` und `/bindings/bounds`.

## Unveraenderten Bestand bestaetigt

Die sechs S2-FG-Regelgruppen und alle 21 Kriterien sind unveraendert
referenziert. Ihre kanonische Projektion bleibt:
`d30f91133c4340d919303531ca8e06ab826f28110b563d383ca48a3f28ab4b8a`.

Auch die vier FG-Belegformen und die sechs Statusraenge sind unveraendert.
Der JSON-Audit bewahrt die bisherigen 21 FH-Bewertungen als historische
Code-/Nachweisbewertungen. Keine davon wird durch diese gezielte
Dokumentabnahme zu einem bestandenen Implementierungskriterium.

27 rohe Quellen-/Belegreferenzen stimmen mit den gebundenen Groessen
und SHA-256-Werten ueberein. Die fuenf JSON-Selbstdigests und
LF-kanonischen Textbindungen von FG/FH/FI/FJ/FK sind geprueft.
Die vier privaten Startdateien und acht bestehenden Implementierungsdateien
bleiben bytegleich. Git enthaelt ausschliesslich die neue Auditdokumentation.

Keine Codeaenderungen, Projektimporte, Tests, Zustandsfunktionen,
Plattformaufrufe, Rechteerhoehung, Ledger-Erzeugung, Recorderstarts,
Matrixzellen oder neue Laufnummer. Es wurde kein Belegobjekt materialisiert
und keine historische Metadatenbeobachtung neu erhoben.

## Verbleibende Grenze und naechster Schritt

FJ-B01 braucht auf dieser Vertragsebene keine weitere Wiederholung.
Offen bleibt insbesondere die **tatsaechliche unabhaengige
Bootstrap-/Owneruebergabe vor dem ersten Eingabelesen**.
Auch Herkunfts-, Runtime-, Budget-, Elternpfad- und Abschlussvoraussetzungen
bleiben im bisherigen Status. Ein Fehlerbeleg oder dieser Audit ersetzt
keine davon.

Als naechster gesondert freizugebender Schritt ist eine konkrete statische
Festlegung des Bootstrap-/Owner-Uebergabewegs mit seiner vorhandenen
aufrufenden Instanz, Quellenherkunft und Budgetbindung sinnvoll.
Sie darf die noch nicht vorhandenen Nachweise nicht als gegeben voraussetzen.
Codekorrekturen, Erhebungen und Ausfuehrungen benoetigen eigene Auftraege.
S2-FC bleibt bis zur tatsaechlichen Abnahme der Voraussetzungen blockiert.
