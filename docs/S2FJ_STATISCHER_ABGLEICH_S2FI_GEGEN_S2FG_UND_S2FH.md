# S2-FJ: Statischer Abgleich S2-FI gegen S2-FG und S2-FH

## Ergebnis

**STATIC_COMPARISON_INCOMPLETE_FAILURE_CONTAINER_BINDING**

Der freigegebene Abgleich ist abgeschlossen, aber eine vollstaendige
Vertragsabnahme ist nicht moeglich. Bei M3 bleibt die Zuordnung fehlender
Angaben aus wiederverwendeten Fehlerbelegen zu ihrem umschliessenden
Terminalbeleg offen. Das ist eine Restluecke innerhalb von FG-C06/M3,
kein zusaetzlicher Forschungszweig und kein beobachteter Laufzeitfehler.

Alle drei Praezisierungen sind enthalten; alle sechs S2-FG-Regelgruppen
und alle 21 in S2-FH geprueften Kriterien sind unveraendert abgedeckt.
**Abdeckung bedeutet nicht Erfuellung.** Die bisherige Code- und
Nachweisbewertung wird nicht hochgestuft. S2-FC bleibt blockiert,
unabhaengig von dieser Vertragsrestluecke auch wegen der weiterhin
fehlenden unabhaengigen Bootstrap-/Owneruebergabe.

Basis: `93c63cd85de0b7c9f756cadf73b07493adbd0723`.
Der [JSON-Auditbeleg](S2FJ_STATISCHER_ABGLEICH_S2FI_GEGEN_S2FG_UND_S2FH_V1.json)
enthaelt den Einzelabgleich aller 21 Kriterien mit Verweisen auf
[S2-FG](S2FG_STATISCHER_KORREKTURVERTRAG_STARTINFRASTRUKTUR_V1.json),
[S2-FH](S2FH_STATISCHER_CODEAUDIT_GEGEN_S2FG_V1.json) und
[S2-FI](S2FI_STATISCHE_START_UND_NACHWEISBINDUNGEN_V1.json).
Keines dieser Dokumente wird durch den Audit geaendert.

## Restpunkt FJ-B01: Fehlerbeleg ohne umschliessenden Terminalbeleg

**Prioritaet P2, FG-C06/M3.**

S2-FI verlangt in `CallerIdentityFailureEvidence.identity_failure`
einen unveraenderten originalen FG-`FailureEvidence`; das gilt auch
fuer Eintraege in `cleanup_failures`. Der FG-Vertrag verlangt fuer
unbekannte Angaben darin ausdruecklich:

> Unavailable facts are listed by field name in enclosing TerminalEvidence.missing_evidence.

Fundstelle: S2-FG-JSON, Zeile 376,
`/evidence_forms/FailureEvidence/rules/0`.

Der neue Callerfehlerzweig soll gerade auch ohne gueltige
Observer-Rueckgabe funktionieren. Sein `terminal_evidence_digest`
darf deshalb null sein. Er besitzt eine eigene `missing_evidence`-Liste,
aber keinen umschliessenden `TerminalEvidence`; `CallerAssessment`
enthaelt nur den gewaehlten Callerbeleg.

Fundstellen: S2-FI-JSON, Zeilen 467 und 472-474 sowie 493-502,
`/forms/CallerIdentityFailureEvidence/fields` und
`/forms/CallerAssessment/fields`.

Rein statischer Grenzfall: Ein Observerhandle wurde erworben, die
Identitaetserhebung scheitert und es liegt kein gueltiger Observerreturn
vor. Der originale Fehler kann eine unbekannte Owneridentitaet enthalten.
S2-FI erlaubt die ablehnende Callerhuelle, bestimmt jedoch nicht
ausdruecklich, welcher umschliessende Terminalbeleg die bestehende
FG-Pflicht fuer diese unbekannte Angabe erfuellt. Eine gleichnamige Liste
in einem anderen Typ ist ohne Bindungsregel kein festgelegter Ersatz.

Es wurde dafuer weder eine Fixture noch ein Belegobjekt erstellt oder
ausgefuehrt. Aus der Textluecke folgt kein falscher Erfolg:
`IDENTITY_UNAVAILABLE` bleibt ausschliesslich ablehnend. Der allgemeine
No-return-Stopp bleibt ebenfalls wirksam. Nicht abnehmbar ist die
vollstaendige, eindeutige Darstellung des Fehlernachweises.

Eine spaetere enge Korrektur muss die zustaendige Beleg-/Containerrolle
und die Weitergabe der unbekannten Angaben explizit festlegen, einschliesslich
verschachtelter Primaer- und Cleanupfehler. Sie darf keinen fehlenden
Observerreturn erfinden oder die sechs FG-Regeln abschwaechen.
Dieser Audit waehlt keine Korrekturform und aendert keine Schnittstelle.

## Abgleich der drei Praezisierungen

### M1: Definiert, unabhaengige Bereitstellung weiterhin nicht belegt

S2-FI bindet `BootstrapPolicy`, `RoleLimits`, `LiveOwnerHandoff`
und `ChannelBinding`. Die vorab erforderlichen Parsergrenzen,
Caller-/Obserververantwortung, gemeinsame Rollenvergabe vor Popen,
Adoption vor Freigabe und Verbrauch ohne Retry sind nachvollziehbar
beschrieben. Ein Handoff nach Adoption wird nicht zur Startberechtigung.

Die fehlende Bereitstellung einer unabhaengigen Erwartung vor dem ersten
Header ist ausdruecklich als Blocker erhalten. Die Policy darf sich
nicht aus ihren eigenen Eingabebytes legitimieren. Es wird kein neuer
Dienst, Pfad oder privilegierter Mechanismus als vorhanden behauptet.

Ergebnis: normative Praezisierung nachvollziehbar; konkrete Uebergabe,
Quellen-/Runtimeherkunft und vollstaendige Budgets weiterhin nicht
materialisiert oder abgenommen. M1 ist nicht vollstaendig geschlossen.

### M2: Originaloperation und Closurebezug auf Vertragsebene gebunden

`OriginalOperationEvidence` erfasst Herkunft, Rolle, Ressource,
native Identitaet, Aufruf und Originalausgang. `PrivateTerminalBundle`
bindet diese Belege an die vorhandenen Closure-Digests. Globale
Erfolgsflags, spaetere Lesbarkeit oder Prozessende ersetzen keine
beobachtete Operation. FileRefs bleiben echte Dateireferenzen.

Die bestehende Kontrollspool-Schliessung wird nicht als fehlend bezeichnet.
Ihr nicht rekursiv im eigenen Trace enthaltener Ausgang muss getrennt
belegt werden. Nicht herausgegebene Einzel- oder Cleanupausgaenge bleiben
UNKNOWN; keine Aenderung am Bestandskern wird daraus abgeleitet.

Ergebnis: fuer den freigegebenen Vertragsabgleich nachvollziehbar
praezisiert. Keine Originaloperation wurde erhoben, kein Validator
abgenommen und keine vollstaendige Implementierbarkeit zertifiziert.

### M3: Ablehnende Ersatzform vorhanden, Kontextpflicht noch offen

Der vollstaendige FG-Callerbeleg und dessen nicht-nullbare
`CreationIdentity` bleiben unveraendert. Die neue Ersatzform trennt
Nichtstart, eindeutigen Erzeugungsfehler, entstandenen Prozess und
unbekannte Erzeugung. Unbekannte Identitaetsteile bleiben null statt
erfundener Werte. Ein erworbener Handle behaelt seine Aufraeumpflichten.

`CallerAssessment` trennt beide Zweige ausdruecklich.
`COMPLETE_IDENTITY` bedeutet noch keinen erfolgreichen Abschluss.
Die unbekannte Identitaet kann ausschliesslich abgelehnt werden.
Die sechs Statusklassen und ihre Rangfolge werden unveraendert uebernommen.

Ergebnis: Ersatzform und Erfolgsgrenze nachvollziehbar; FJ-B01 verhindert
die vollstaendige Abnahme der Wiederverwendung von FG-Fehlerbelegen im
Callerzweig ohne Observerreturn.

## Sechs Regelgruppen und 21 Kriterien

| Regelgruppe | Kriterien | Statischer Abgleich |
| --- | ---: | --- |
| FG-C01 Reservierungszugriff | 3 | Unveraenderte Pflicht; keine umgesetzte Leser-/Sharekorrektur behauptet. |
| FG-C02 Budgetherleitung | 4 | Neue Belegkosten bleiben budgetpflichtig; Zahlen/Hostabnahme fehlen weiterhin. |
| FG-C03 Bootstrapgrenzen | 3 | Vorabgrenzen beschrieben; unabhaengiger Transport bleibt offen. |
| FG-C04 Einmalstart | 4 | Gemeinsame Ownervergabe gefordert; kein Nachweis aus alten Bytes oder neuer ChildOwner-Instanz. |
| FG-C05 Herkunft | 3 | Exakte Layout-/Runtime-/Quellpflichten bleiben erhalten; keine neue Erhebung. |
| FG-C06 Fehlernachweise | 4 | Originaloperation und ablehnender Callerzweig ergaenzt; Kontextrest FJ-B01. |

Der JSON-Beleg uebernimmt fuer jedes Kriterium den genauen Wortlaut,
S2-FG-Pointer und bisherigen S2-FH-Status. Er ergaenzt lediglich die
S2-FI-Fundstellen und die Bewertung dieses Vertragsabgleichs.
Die vier bisherigen Grenzwahrungsbewertungen aus S2-FH werden nicht
zu bestandenen Funktions- oder Codekriterien umgedeutet.

## Belegpruefung und Grenzen

25 rohe Quellen-/Belegreferenzen stimmen mit ihren gebundenen Groessen
und SHA-256-Werten ueberein. Die Selbstdigests und LF-kanonischen
Markdownbindungen von S2-FG, S2-FH und S2-FI sind geprueft.
Die Projektion der sechs Regelgruppen aus `id`, `rules` und
`static_acceptance` bleibt:
`d30f91133c4340d919303531ca8e06ab826f28110b563d383ca48a3f28ab4b8a`.

Die vier privaten Startdateien und acht bestehenden Implementierungsdateien
sind bytegleich. Das ist keine erneute Codeabnahme: Der hier freigegebene
Auftrag prueft Vertragsuebernahme und Dokumentkonsistenz, nicht die
Ausfuehrung oder neue Implementierung der 21 Kriterien.

S2-FC behaelt alle offenen Voraussetzungen aus FG/FH/FI. Ein
Bootstrap-/Ownernachweis allein wuerde die anderen fehlenden Herkunfts-,
Budget-, Elternpfad- und Abschlussbelege nicht automatisch ersetzen.
Der historische Ledgerbefund wurde nicht neu erhoben.

Keine Codeaenderungen, Projektimporte, Tests, Projektfunktionen,
Plattformausfuehrung, Rechteerhoehung, Ledger-Erzeugung, Zielschreibvorgaenge,
Flushes, Recorderstarts oder Matrixzellen. Nur diese Auditdokumentation
wird versioniert. Keine neue Laufnummer oder fachliche Ergebnisinterpretation.

## Konsequenz

**Keine vollstaendige Vertrags-, Code- oder Startabnahme. S2-FC bleibt blockiert.**

**RUECKMELDUNG ERFORDERLICH:** Vorschlag fuer S2-FK ist ausschliesslich die
statische Klaerung der umschliessenden Fehlerbelegrolle fuer den Callerfall
ohne Observerreturn, unter unveraenderten FG-Pflichten. Keine Umsetzung
oder Ausfuehrung. Die unabhaengige Bootstrap-/Owneruebergabe bleibt ein
gesondert tatsaechlich zu belegender Blocker; weitere Wiederholungen eines
unveraenderten Audits ersetzen diesen Nachweis nicht.
