# S2-FO: Autorisierter Read-only-Bootstrap-Probevertrag

## Status und verbindliche Korrektur

**STATIC_AUTHORIZED_READ_ONLY_PROBE_CONTRACT_BOUND_S2FC_BLOCKED**

Der in S2-FN vorgeschlagene Weg eines noch unberechtigten Einlesens ist
vom Benutzer abgelehnt und wird nicht weiterverfolgt. Die betreffende
Empfehlung im historischen FN-Dokument und dessen JSON `/next_step`
hat keine aktuelle Geltung. Der FN-Auditbefund bleibt unveraendert.
Eine spaetere Pruefung legitimiert keinen zuvor unberechtigten Zugriff.

S2-FO definiert nur einen minimalen, **vor dem ersten Read ausdruecklich
autorisierten** Probeumfang. Die aktuelle Freigabe gilt fuer diesen
statischen Vertrag, nicht fuer seine Implementierung, Vorbereitung oder
Ausfuehrung. S2-FC bleibt blockiert. Es wird kein vorhandener
Bootstrap-/Ownernachweis behauptet.

Basis: `e227c49a9e149b7fda13e83c8491999334385ba9`.
Quellen und offene Voraussetzungen stehen im
[JSON-Vertrag](S2FO_STATISCHER_AUTORISIERTER_READ_ONLY_BOOTSTRAPVERTRAG_V1.json).

## Minimaler Gegenstand

Die gesonderte Probe wird als private Read-only-Routine innerhalb des
bereits unabhaengig abgenommenen Callers festgelegt. Sie erzeugt keinen
Prozess. Der initiale Owner bleibt derselbe Caller; es gibt keinen
Ownerwechsel, keinen neuen Starter und keinen Abschlussbeobachter.
Die Herkunft des bestehenden Callers muss vor Eintritt in die Routine
belegt sein. Die aktuelle Shell oder dieser Chat wird nicht zu ihm erklaert.

Einziger Nutzdaten-Lesepfad:

`C:\Users\TV\Documents\MCM_FIELD_ORGANISM\workspace\docs\S2FB_STATISCHER_NATIVER_LAYOUTVERTRAG_V1.json`

Verbindliches Original: 9.184 Bytes, SHA-256
`3dd1bc35bf8fc8f8242475f3264484878f730a99b43494a67700b09a5c79ad58`.
Es handelt sich um eine bereits gebundene Bootstrap-Quelle, nicht um
einen neuen nativen Layout- oder Plattformbefund.

Der einzige Lesekanal ist ein **bereits vorab autorisiertes, gehaltenes
Read-only-Dateihandle genau dieses Originals**. Kein Pipe-Payload, kein
stdin, Socket, Netzwerkpfad oder frei waehlbarer Pfad ist zugelassen.
Die Routine oeffnet keine Datei selbst und legt keinen Kanal an.
Das ist eine gesonderte Datei-Leseprobe, kein Ersatz fuer die nicht
abgenommene Eltern-Kind-Pipebindung aus FM/FN.

Die Probe vergleicht ausschliesslich Laenge und rohe Bytes bzw. deren
Digest mit dem vorab gebundenen Original. Sie interpretiert dessen
Inhalt nicht als Freigabe, verfolgt keine eingebetteten Verweise und
importiert daraus keinen Code. Die Quellen-/Runtimeclosure der spaeteren
Routine ist eine separate Vorbedingung, keine zusaetzliche Nutzdaten-
Leseliste. Das Original darf keine Erweiterung dieser Liste bestimmen.

## Vorbedingungen vor dem ersten Read

Alle folgenden Bindungen muessen aus unabhaengiger, schon autorisierter
Vorbereitung stammen und dem Caller vorliegen, ohne dazu erst die Probe
oder den zu pruefenden Kanal lesen zu muessen:

1. Konkrete Callerquelle, abgenommene Runtime und vollstaendige aktuelle
   CreationIdentity, mit urspruenglicher Herkunft und gehaltenem Besitz.
2. Gesonderte Freigabe genau dieses Lesepfads, Originals, Kanals und
   Aufrufumfangs. Der vorliegende Vertrag ist keine Laufberechtigung.
3. Tatsaechliche Datei-/Volumeidentitaet, exakter Pfad, Laenge,
   Read-only-Zugriff, Handle-Generation, Ausgangsposition und
   Eigentumszuordnung; keine bloss uebergebene Handlezahl.
4. Originale Nachweise der vorher autorisierten Handleerzeugung und
   Identitaetspruefung, Schutz der Quelle vor Austausch/Aenderung sowie
   eine unabhaengige Zuordnung zum Caller. Pfad oder Hash allein reichen
   nicht. Dateiumleitung oder ein anderer Handle wird nicht nachtraeglich
   als gleichwertig angenommen.
5. Vorab gepruefte Routinequelle und endliche Lese-, Speicher-,
   Operations- und Cleanupgrenzen einschliesslich Fristen. Die 9.184
   Inhaltsbytes sind bekannt; ein vollstaendiges Operationsbudget wird
   nicht erfunden und ist noch nicht abgenommen.
6. Vollstaendige verbindliche Start-/Aufraeumreihenfolge und nachgewiesene
   alleinige Verantwortung fuer genau das dedizierte Lesehandle.

Auch die Bereitstellung dieser Voraussetzungen ist kein freier
Hilfsaufruf: Oeffnen, Metadatenzugriff und Identitaetserhebung benoetigen
eigene vorherige Autorisierung. S2-FO fuehrt sie nicht aus. Ein
unberechtigter Vorlauf darf nicht als Vorbedingung umetikettiert werden.

Fehlt eine Bindung, muss vor dem ersten Inhaltsbyte und vor jedem
Probe-Read abgebrochen werden. Unbekannte Identitaet ist kein Default,
kein Anlass fuer einen Suchlauf und keine Berechtigung zu einem Probezugriff.

## Start- und Aufraeumfolge

| Phase | Bindung und erlaubter Umfang der spaeteren Probe |
|---|---|
| Vorbereitung ausserhalb der Probe | Bereits autorisierter Caller und dediziertes Lesehandle, originale Erzeugungs-/Identitaetsbelege, Quellen- und Budgetabnahme muessen vorliegen. Keine Erhebung durch S2-FO. |
| Eintritt | Lebende Calleridentitaet, Freigabe, Kanalbesitz, Original und Budgets gegen unabhaengige Vorbindungen pruefen; bei fehlender Bindung kein Read. |
| Einmalige Nutzung | Genau einen Probeaufruf im bestehenden Ownerkontext binden, ohne Datei-Ledger. Neue Wrapper oder alte Belegbytes schaffen keine erneute Freigabe. |
| Lesen | Ausschliesslich das gehaltene autorisierte Handle, Position null, insgesamt genau das gebundene Original, keine weitere Datei und kein EOF-Erweiterungsread. Teilstuecke bleiben innerhalb desselben vorab begrenzten Vorgangs. |
| Abgleich | Laenge und Digest gegen die bereits vorhandene Erwartung; keine Rechte, Identitaeten oder Konfiguration aus dem Inhalt rekonstruieren. |
| Aufraeumen | Der Caller schliesst sein dediziertes Lesehandle genau einmal nach Lesen oder Fehler. Ein unbekanntes/fremdes Handle darf nicht uebernommen oder geschlossen werden; bereits unabhaengig belegter eigener Besitz bleibt trotz Inhaltsfehler erhalten. |
| Rueckgabe | Begrenzter In-Memory-Befund erst nach Aufraeumversuch, mit originalen Fehlern und fehlenden Nachweisen. Kein Datei-, Pipe-, stdout-, Marker- oder Logschreiben durch die Probe. |

Das Eigentum verbleibt durchgehend beim Caller. Die Routine begruendet
keine Terminierungsberechtigung und beendet den Caller nicht. Die
Aufraeumzustaendigkeit wird vor Eintritt festgelegt, nicht aus dem
spaeteren Ergebnis abgeleitet. Der Abschluss betrifft den Leseaufruf
und sein Handle, nicht den zukuenftigen Prozessabschluss des Callers.

Diese Tabelle ist eine verbindliche Sollfolge, **noch kein tatsaechlicher
Nachweis ihrer Einhaltung**. Vollstaendige Originalbelege muessen die
vorherige Erzeugung/Abnahme und spaeter jede eigene Lese-/Closeoperation
zu Quelle, Phase, Prozess, Owner und Handle-Generation zuordnen. Eine
Erfolgsboolesche Angabe oder ein spaeter passender Digest ersetzt das nicht.
Es wird kein neuer Belegdatentraeger oder V1-Validator stillschweigend
eingefuehrt; konkrete Materialisierung bleibt separat zu pruefen.

## Ausschluesse und Fail-Closed

Keine Schreib-, Flush-, Reservierungs-, Umbenennungs-, Veroeffentlichungs-,
Recorder-, Matrix-, Feld- oder API-Funktion; keine neuen Prozesse,
keine Rechteerhoehung, kein Ledger und kein Retry nach Fehler oder
unklarem Verbrauch. Insbesondere werden `reserve_dispatch`, `start_once`,
`observe_once`, `ChildOwner` und Recorder-Supervisor nicht als
Probehuellen verwendet. Die vorhandene SourceLease ist ebenfalls keine
stillschweigende Umsetzung der auf genau ein gehaltenes Handle begrenzten
Routine. TSPM-1, PPB-1 und der Feldpfad bleiben unberuehrt.

Fehlende Vorbedingungen stoppen vor Read. Bekannte Identitaets- oder
Quellwidersprueche werden abgewiesen. Lese-/Budgetfehler stoppen den
Vorgang ohne Wiederholung. Unklarer Besitz oder fehlender erforderlicher
Closebeleg verbietet einen bestaetigten Abschluss. Primaer- und
Cleanupfehler behalten ihre Originalherkunft; fehlende Werte bleiben
fehlend. Die bisherigen FG-Statusprioritaeten werden nicht gelockert.

Callerfehlerbeleg, Observer-Rueckgabe und tatsaechlicher Plattformnachweis
bleiben getrennt. Die Probe erzeugt keine Observer-Rueckgabe. Ihr eigener
In-Memory-Lesebefund darf keine fehlende Observeridentitaet und keinen
fehlenden Plattformbeleg ersetzen. Die enge FK-/FL-Belegzuordnung bleibt
unveraendert und wird nicht automatisch auf andere Fehlerfaelle erweitert.

## Offener Stand und naechster Schritt

Die konkreten Vorbindungen fuer Caller, Routine, Handle, Kanalherkunft,
Budget und tatsaechliche Start-/Closebelege sind **nicht bereitgestellt**.
FN-B01 und FN-B02 werden durch diesen Vertrag nicht geschlossen. Die
Leseprobe waere auch bei spaeterem Erfolg nur ein enger autorisierter
Zugriffs-/Abschlussbefund, keine gueltige Plattformpruefung und kein
Nachweis der vollstaendigen Bootstrap-/Owneruebergabe.

30 rohe Quellen-/Belegreferenzen und acht Vorgaenger-Digest-/Textpaare
sind statisch geprueft. Die sechs FG-Regelgruppen, 21 Kriterien,
vier FG-Belegformen und offenen FC-P01 bis FC-P06 bleiben unveraendert.
Nur die beiden neuen Vertragsdokumente werden abgelegt. Kein Code,
Projektimport, Test, nativer Aufruf, Probezugriff, Recorderstart oder
Matrixlauf wird ausgefuehrt; es gibt keine neue Laufnummer.

Naechster Schritt ist ausschliesslich ein gesonderter statischer
Vorbedingungs- und Isolationsaudit dieses minimalen Probevertrags.
Er muss insbesondere zeigen, wo die autorisierte Caller-/Handlebindung
bereits vor Read unabhaengig herkommt. Kann das nicht konkret bereitgestellt
werden, bleibt der Weg eine offene Vertrauensluecke und darf nicht
implementiert oder ausgefuehrt werden. **S2-FC bleibt blockiert.**
