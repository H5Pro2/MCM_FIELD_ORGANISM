# S2-FN: Statischer Machbarkeitsabgleich des Bootstrapwegs

## Ergebnis

**STATIC_FEASIBILITY_NOT_ESTABLISHED_S2FC_BLOCKED**

Der Abgleich ist abgeschlossen; die Machbarkeitsabnahme ist **nicht
bestanden**. S2-FM ist in seiner derzeitigen Bindung nicht vollstaendig
materialisierbar beschrieben. Insbesondere fehlt der unabhaengige Weg
von der vorab gebundenen Calleridentitaet zur genauen lebenden
Eltern-/Kanal-/Ownerbindung vor dem ersten Eingabelesen.

Dies ist kein Beweis, dass ein sicherer Bootstrap generell unmoeglich
ist. Es ist auch kein negativer Feld- oder Memorybefund. Abgelehnt wird
nur die Abnahme dieses konkreten privaten Startwegs als umsetzbar.
S2-FC bleibt blockiert; kein tatsaechlicher Owner- oder Plattformnachweis
wurde erhoben oder ersetzt.

Basis: `a4a8b7b294860d38fb277da3d0349b59379a77fa`.
Geprueft wurden [S2-FM](S2FM_STATISCHER_BOOTSTRAP_UND_OWNERUEBERGABEWEG.md),
die unveraenderten FG-/FI-Regeln und der vorhandene private Startcode.
Der [JSON-Audit](S2FN_STATISCHER_MACHBARKEITSABGLEICH_BOOTSTRAP_V1.json)
enthaelt Quellen, sechs Auftragspruefpunkte und die Abnahmegrenzen.

## FN-B01: Vor-Eingabe-Vertrauensweg nicht geschlossen

FM sieht einen vor dem Observerstart eingefrorenen Anker mit
Caller-CreationIdentity, Rollenbaum und endlichen Zustellgrenzen vor.
Diese statischen Angaben koennten prinzipiell vor einem Read geladen
werden. Ihre konkrete Quelle, Vorbereitung, Runtimeabnahme und
numerische Budgetherleitung sind jedoch noch nicht vorhanden bzw.
abgenommen. Die Eintrittsquelle enthaelt den Anker nicht.

Entscheidender ist die verbleibende logische Luecke auch unter der
Annahme, dieser Anker sei bereits vorhanden:

1. FM verlangt vor dem ersten Header genaue aktuelle Eltern-, Endpoint-
   und lebende Ownerbindungen. Rootidentitaet und Rollenbaum allein
   gelten laut demselben Vertrag ausdruecklich nicht als ausreichend.
2. Die Kindprozesse und ihre konkreten Endpoints entstehen erst nach der
   Ankerfestschreibung. Die Eltern-/Observerseite kann danach originale
   Erzeugungs- und Adoptionsbelege besitzen. Daraus folgt noch nicht,
   dass das Kind diese Bindung bereits unabhaengig vor seinem Read hat.
3. Der einzige ausgewaehlte Nachrichtentransport sind die bestehenden
   Eltern-Kind-Pipes. FM benennt keine zusaetzliche konkrete Abbildung,
   die die erforderliche lebende Bindung ohne Lesen dieser Nachrichten
   im Empfaenger verfuegbar macht.
4. Wuerde der erste Payload oder die zuerst gesendete BootstrapPolicy
   diese eigene Berechtigung erst begruenden, muesste zum Pruefen bereits
   gelesen werden. Genau das verbieten FM und FI-M1.

Es handelt sich somit um eine **offene Vorbedingung mit zirkulaerem
Nachrichtenersatz**, nicht um den Beweis eines tatsaechlichen Deadlocks
in einem ausgefuehrten Programm. Die Grundfolge Spawn -> Adoption ->
Sendung ist nicht fuer sich widerspruechlich. Nicht geschlossen ist
die unabhaengige Empfaengerbindung vor dem ersten Empfang.

Fundstellen: FM Abschnitte 1/2 und JSON `/route/source_anchor`,
`/route/pre_input_acceptance`; FI `/clarifications/M1/trust_root`;
FG-C03.A1/A3 und FG-C04.A3/A4.
Im Code prueft `_parent_pipe` lediglich Pipeart und Eltern-PID
(`tools/run_s2fd_isolated_platform_once.py:14`). Danach liest
`_read_bootstrap` Header und Payload (`:30`); erst `main` leitet den
Plan aus dem dekodierten Paket ab und prueft dessen Budget (`:162`).
Es gibt dort weder den FM-Anker noch den erforderlichen Vor-Read-Abgleich.

Die eng begrenzte Quellensuche in `mcm_field_organism` und `tools` findet
fuer `observe_once` nur die Definition und fuer `_TRUSTED_STARTS` nur
Definition und Abfrage. Sie identifiziert keinen separat abgenommenen
Caller-Einstieg. Das ist eine Aussage ueber den geprueften Bestand,
keine Behauptung ueber beliebige externe Aufrufer. Ein gesetzter
ContextVar waere ohnehin kein Ersatz fuer die geforderte Herkunft.

## FN-B02: Bestehende Ownerfolge erfuellt FM nicht

`ChildOwner` legt pro Instanz ein neues `attempted`-Set an und konsumiert
es lokal vor Popen (`_s2fd_start_owner.py:209`). Starter und Supervisor
erzeugen ihr Kind, senden erst dann `CHILD` und warten auf `OWNED`
(`_s2fd_start_owner.py:255`; Eintrittsquelle `:108`). Der Observer
adoptiert daraufhin die tatsaechlichen Handles (`_s2fd_completion_observer.py:350`).
Das ist keine gemeinsame, vom Observer vergebene Rollenberechtigung
vor dem jeweiligen Spawn. Der fehlende FM-Claim laesst sich nicht
rueckwirkend aus einer erfolgreichen Adoption ableiten.

Auch die Cleanupzustaendigkeit weicht ab: Sowohl `ChildOwner.close`
(`_s2fd_start_owner.py:223`) als auch `ProcessEvidence.close`
(`_s2fd_completion_observer.py:218`) koennen noch laufende Kinder
terminieren. FM weist diese Berechtigung ausschliesslich dem jeweiligen
unmittelbaren Erzeuger zu. Eine Beobachtungsreferenz allein legitimiert
keine zweite Terminierungsinstanz. Dies sind statische Codeabweichungen,
keine beobachteten Doppelterminierungen.

Diese Abweichungen widerlegen nicht die grundsaetzliche Programmierbarkeit
einer einmaligen Rollenbilanz. Sie verhindern aber die Abnahme des
vorliegenden Codes als Realisierung der vorgesehenen Uebergabefolge.
Eine Codekorrektur wurde weder ausgewaehlt noch vorgenommen.

## Sechs Auftragspruefpunkte

| Pruefpunkt | Statischer Befund |
|---|---|
| Bootstrap-Quelle vor erstem Read | Nicht belegt. Der Anker ist nur vorgesehen; FN-B01 bleibt auch bei unterstelltem Anker als fehlende Live-Zuordnung offen. |
| Initialer Owner und Prozessidentitaet | Rollenname eindeutig, konkrete Callerquelle/Abnahme nicht belegt. Vollstaendige Kindidentitaeten entstehen aus echten gehaltenen Handles, ersetzen aber keinen Root-Owner. |
| Starter, Recorder, Abschlussbeobachter in Reihenfolge | Hierarchie nachvollziehbar; Vor-Read-Uebergabe und gemeinsame Vor-Spawn-Claims fehlen. Cleanup entspricht nicht der FM-Zuordnung. |
| Keine nachtraeglich erfundene Identitaet | Vertraglich eingehalten. `ProcessEvidence.adopt` liest Kindidentitaeten vor `RESULT` aus Handles. Ein spaeterer Handoff/Result darf die fehlende fruehe Ownerbindung nicht nachtraeglich abnehmen. |
| Callerfehler, Observerreturn, Plattformnachweis getrennt | Auf Vertragsebene erhalten. FK/FL bleiben unveraendert; daraus folgt keine implementierte Caller-Abschlusskette und kein Plattformnachweis. |
| Fehlende/widerspruechliche Uebergaben fail-closed | FM/FG verlangen den Stopp; aktueller Gesamtpfad ist dafuer nicht abgenommen. Der spate Budgetcheck nach dem ersten Read belegt gerade keinen fruehen Ablehnungsort. |

Positive Teilbeobachtung: `ProcessEvidence.adopt` registriert das
gehaltene Handle vor der Identitaetsvalidierung und ermittelt PID,
Erstellungszeit und Image am Prozess (`:173`, `:184`). Der Observer
adoptiert vor der nachfolgenden Bootstrap-Sendung bzw. `OWNED`-Antwort.
Das wird nicht als aus `RESULT` erfundene Identitaet fehlklassifiziert.
Es schliesst aber weder FN-B01 noch FN-B02.

Die sechs FG-Statusraenge und die Caller-Belegzuordnung bleiben
unveraendert. Fehlende Herkunft vor Start bedeutet weiterhin eine
fehlende Voraussetzung; bekannte Widersprueche werden nicht zu
Unbekanntheit umgedeutet. Unbekannter Verbrauch erlaubt keinen Retry.
Erforderlicher, unbestaetigter Abschluss verhindert Erfolg. Hier wurde
keiner dieser Runtimepfade aufgerufen und kein Terminalbeleg erzeugt.

## Nachweisgrenze

29 rohe Quellen-/Belegreferenzen, sieben Vorgaenger-Selbstdigests und
deren LF-Textbindungen sind geprueft. Die sechs FG-Regelgruppen mit
21 Kriterien und die vier FG-Belegformen bleiben unveraendert.
Die vier privaten Startdateien und acht bestehenden Module sind bytegleich.
Historische Abnahmen werden nicht hochgestuft; FJ-B01 wird nicht erneut
geoeffnet. FC-P01 bis FC-P06 behalten ihren offenen Status.

Nur die beiden neuen Auditdokumente wurden hinzugefuegt. Keine
Projektimporte, Codeaenderungen, Tests, native Metadatenerhebung,
Plattformaufrufe, Rechteerhoehung, Ledger-Erzeugung, Zielverzeichnis-
Schreiboperationen, Flushes, Recorderstarts, Matrixzellen oder Laufnummer.

## Konsequenz

Der S2-FM-Weg wird **nicht zur Implementierung oder Ausfuehrung
weitergereicht**. Ein weiterer Belegcontainer loest FN-B01 nicht.

Sinnvoll ist erst eine ausdruecklich freizugebende statische Entscheidung
ueber die Vertrauensgrenze: Muss die gesamte lebende Ownerkette wirklich
vor jedem ersten Read feststehen, oder darf eine unabhaengig vorab
begrenzte, noch unberechtigte Eingabe erfolgen, waehrend jede weitere
Prozesserzeugung, Reservierung und Recorderfreigabe bis zur vollstaendigen
Abnahme gesperrt bleibt? Dabei waere die Erzeugung eines etwaigen
Empfaengerprozesses weiterhin ausschliesslich Sache seines bereits
abgenommenen Eltern-Owners; der Payload duerfte sich nicht selbst zulassen.

Diese Frage waere eine ausdrueckliche Aenderungspruefung von FG/FI/FM,
keine bestehende Freigabe und keine hier ausgewaehlte Alternative.
Auch eine solche Grenze benoetigte reale Caller-, Quellen- und
Plattformnachweise. Ohne neue Entscheidung bleiben nur der dokumentierte
Stopp dieses Abnahmewegs und die bestehenden Sperren bestehen.
