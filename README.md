# MCM_FIELD_ORGANISM

`MCM_FIELD_ORGANISM` entwickelt die Grundmechanik eines digitalen,
MCM-basierten Wahrnehmungs- und Nervensystems. Im Mittelpunkt steht kein
vorprogrammiertes Erkennen, sondern ein gemeinsames Feld, das über
sensorspezifische Rezeptorflächen kontinuierlich an einer Welt teilnimmt.

## Aktueller Entwicklungsstand

Die [Bestandskonsolidierung vom 28.08.2026](docs/BESTANDSKONSOLIDIERUNG_NACH_PLATTFORMSTOPP.md)
trennt den historisch geprueften Feldpfad, PPB-1 und die private technische
Memory-Architektur TSPM-1 von der nicht abgenommenen Plattforminfrastruktur.
Der konkrete Supervisor-/Child-Plattformpfad ist geschlossen. S2-FC und der
alte Matrixeinstieg bleiben gesperrt; bestehender Code und Belege bleiben erhalten.

Der [begrenzte TSPM-1-Funktionspruefplan](docs/TSPM1_VERHAELTNISMAESSIGER_FUNKTIONSPRUEFPLAN.md)
wurde nach acht bestandenen fokussierten Tests einmalig ueber den separat
freigegebenen privaten Einstieg ausgefuehrt: **56 Zellen, 336 Bildungsangebote
und 144 Proben, vollstaendig aufgezeichnet, Exit-Code 0**.
Der [Funktionsvergleich](reports/tspm1_functional/functional-20260828-01/BEFUND.md)
zeigt fuer TSPM-1, die unabhaengige R0-Kontrolle und den einfacheren FIFO-Arm B4
jeweils 18 von 18 korrekt beurteilte Proben. B4 erreicht das gleiche gebundene
Funktionsprofil mit 1218 statt 2089 geschriebenen Woertern und 255 statt 269
logischen Speicherwoertern. Fuer diese Aufgabe genuegt die einfachere Loesung;
TSPM-1 bleibt eine vorhandene technische Zwei-Ebenen-Referenz.

Die Einmalfreigabe ist verbraucht, der neue Einstieg wieder gesperrt.
Speicherkerne, Fixtures, Parameter und Feldpfad wurden nicht geaendert.
Die 26 AV-Traegerwerte variieren in diesen Fixtures nur in zwei unabhaengigen
Werten. Der Vergleich belegt deshalb weder die Qualitaet reichhaltigerer
Wahrnehmungsmerkmale noch eine MCM-spezifische Feldmechanik.

Als naechste Aufgabe ist die [Erhaltung visueller Ortsstruktur](docs/VISUELLE_ORTSSTRUKTUR_AUFGABEN_UND_PRUEFPLAN.md)
gewaehlt: gleich verteilte Helligkeitswerte in unterschiedlichen Bildzellen.
Die separat freigegebene private Umsetzung und Untersuchung sind abgeschlossen:
11/11 fokussierte Tests, danach einmalig 28 Bildanalysen, acht Bildungen und
48 Proben, Exit-Code 0. Der [Ortsstrukturbefund](reports/tspm1_functional/spatial-20260828-01/BEFUND.md)
zeigt: Die 18 ortsgebundenen Werte bleiben im Rezeptor und in B4 erhalten.
Der Abruf unterscheidet den grossen Ortstausch, setzt den kleinen jedoch in
sechs Proben falsch gleich. Das begrenzt die bestehende Abrufbewertung fuer
diese Aufgabe, nicht die Erhaltung der Zellwerte. Eine Aenderung der
Abrufregel ist getrennt zu entscheiden; keine neue Speichermechanik wurde
eingefuehrt. TSPM-1 und PPB-1 bleiben erhalten, der Versuchseinstieg ist wieder gesperrt.

Der anschliessende [Kalibrierungs- und Bestaetigungsplan](docs/VISUELLE_L1_KALIBRIERUNG_UND_BESTAETIGUNGSPLAN.md)
bindet dieselbe L1-Regel mit bisheriger Schwelle 0,2 und einer vorab gebundenen
visuellen Schwelle von 44/765. Globale Intensitaetsverschiebungen um +/-8
sollen toleriert, Zweizellentausche ab Kontrast 64 unterschieden werden.
Drei neue Bildpaare dienen der Bestaetigung, ein schwaecheres Paar separat
der Grenzdiagnose. Bekannte Entwicklungsdaten werden nicht als Bestaetigung
gezaehlt. Die anschliessend freigegebene Umsetzung und einmalige Bestaetigung
sind abgeschlossen: acht bestandene Tests, 56 Bildanalysen, acht Bildungen,
48 Probeinputs und 96 Regelabrufe. Der [Kalibrierungsbefund](reports/tspm1_functional/calibration-20260828-01/BEFUND.md)
zeigt mit 44/765 alle 36 Pflichtentscheidungen korrekt; die alte Schwelle
liefert zwoelf Fehlgleichsetzungen. G1 bleibt separat: Beide Regeln setzen
sechs schwache Tausche gleich. Deren unveraenderter L1-Abstand ist identisch
mit dem einer tolerierten +/-8-Verschiebung. Fuer die definierte Mindestaufgabe
genuegt einfache Kalibrierung; eine Erweiterung auf schwache Tausche waere
gesondert zu entscheiden. Die Schwelle wurde technisch vorgegeben, nicht
erlernt. Speicher und Feldpfad blieben unveraendert, der Einstieg ist gesperrt.

Der naechste [Aufgabenplan zur visuellen Reihenfolge](docs/VISUELLE_REIHENFOLGE_AUFGABEN_UND_PRUEFPLAN.md)
prueft vier gleiche Einzelbilder in zwei Folgen mit vertauschten Mittelpositionen.
B4 besitzt Bildungsindizes, aber bislang keinen geprueften Sequenzabruf.
Geplant sind eine private read-only Folgenpruefung und eine reihenfolgeblinde
Inhaltskontrolle bei unveraenderten Speicherwerten und L1-KAL-Grenzen.
Die zwei privaten Dateien und acht fokussierten Tests wurden freigegeben;
alle Tests bestanden. Die bedingte einmalige Hauptuntersuchung erzeugte zwar
alle 152 Ereignisse fuer den vorgesehenen Umfang, stoppte aber im
Abschlussvalidator wegen eines falschen Modulverweises mit Exit-Code 1.
Der [Fehlabschluss](reports/tspm1_functional/sequence-20260829-01/BEFUND.md)
ist daher ausdruecklich nicht auswertbar und weder positiver noch negativer
Sequenzbefund. Der Validatorverweis ist statisch korrigiert, der Einstieg
gesperrt und die Einmalfreigabe verbraucht. Es gab keine Wiederholung.

Fuer eine methodisch getrennte Bestaetigung liegt ein
[neuer Korrektur- und Bestaetigungsplan](docs/VISUELLE_REIHENFOLGE_UNABHAENGIGE_BESTAETIGUNGSPLAN.md)
vor. Vier neue Bilder werden deterministisch aus gleich hellen 3-von-6-Masken
ausgewaehlt und vorab gebunden. Regeln, B4 und `44/765` bleiben unveraendert.
Vor einem neuen Einmallauf musste genau ein kleiner Abschlussvalidator-Test den
korrigierten Pfad vollstaendig bis `COMPLETE` pruefen. Diese begrenzte
Refaktorierung und [Korrekturpruefung](reports/tspm1_functional/sequence-confirmation-validator-20260829-01/BEFUND.md)
sind abgeschlossen: 1/1 Test, Exit-Code 0, vollstaendiger Mini-Abschluss und
alle fachlichen Guardzaehler null. Das bestaetigt nur die Aufzeichnungstechnik.

Die danach ausdruecklich freigegebene unabhaengige Hauptausfuehrung
`sequence-confirmation-20260829-01` ist inzwischen einmalig und vollstaendig
abgeschlossen. Der [Befund](reports/tspm1_functional/sequence-confirmation-20260829-01/BEFUND.md)
belegt 56 Bildanalysen mit N1-N4, acht tatsaechliche B4-Bildungen aus zwei
frischen Banken, zwoelf Folgeproben, 24 read-only Entscheidungen und 152
verkettete Ereignisse bei Exit-Code 0. GEORDNET lieferte sechs korrekte
Annahmen und sechs korrekte Abweisungen; REIHENFOLGEBLIND nahm erwartungsgemaess
alle zwoelf inhaltsgleichen Folgen an. Eine unabhaengige read-only Pruefung
rechnete alle 192 Paarabstaende aus den Belegen nach. Damit ist ein begrenzter
technischer Abruf kurzer visueller Reihenfolgen ueber tatsaechlich erzeugte
Bildungsindizes bestaetigt. Das ist kein selbststaendiges Sequenzlernen, keine
semantische oder episodische Memory und keine MCM-Feldwirkung. Der Einstieg
ist wieder gesperrt; es gab keine Wiederholung oder nachtraegliche Anpassung.

Als naechste getrennte Aufgabe liegt ein statischer
[Pruefplan fuer Zwischenreize und Kapazitaetsdruck](docs/FOLGENERHALTUNG_ZWISCHENREIZE_KAPAZITAETSDRUCK_PRUEFPLAN.md)
vor. Er trennt Inhaltserhaltung von Folgenordnung. B4 darf seine gespeicherten
Bildungsindizes verwenden; TSPM-1 nimmt mit getrennten Fast-/Slow-Befunden nur
am Inhaltsvergleich teil, weil sein aktueller Zustand keine vollstaendige
beliebige Viererfolge traegt. Der korrigierte Verdichtungsteil vergleicht zwei
gegen vier N1-Expositionen und stabilisiert N1-N4 jeweils durch vier
Expositionen vor dem Slow-Kapazitaetsdruck. Die sechs privaten Fixtures und die
zustandsunveraenderliche B4-/TSPM-1-Inhaltsauswertung sind implementiert und
statisch geprueft. Acht fokussierte synthetische Adaptertests bestanden mit
`8/8`. Der private Runner, die exklusive Ereignisaufzeichnung und ein davon
getrennter read-only Ergebnisverifikator sind jetzt fuer den exakten Umfang
`146/170/16/316/1296` implementiert und statisch geprueft. Der
Ausfuehrungsschalter bleibt geschlossen. Die danach genau einmal ausgefuehrte
[Runnerqualifikation](reports/tspm1_functional/retention-runner-qualification-20260829-01/BEFUND.md)
endete mit sechs bestandenen und zwei technisch blockierten Tests, Exit-Code 1.
Die echten kleinen B4-/TSPM-1-Wege und read-only Proben bestanden; die beiden
Belegwegtests erreichten den Recorder nicht, weil dessen exakte `Path`-Typgrenze
einen Windows-`WindowsPath` abweist. Es gab keine Korrektur oder Wiederholung.
Nach gesonderter Freigabe wurden die zwei `Path`-Pruefungen eng korrigiert.
Die neue einmalige
[Runnerqualifikation](reports/tspm1_functional/retention-runner-qualification-20260829-02/BEFUND.md)
bestand danach denselben unveraenderten Testsatz mit `8/8`, Exit-Code 0. Der
statische Abschlussaudit qualifiziert Runner, Recorder und Verifikator, nicht
die Memory-Funktion.

Der anschliessend separat freigegebene Hauptlauf
`retention-capacity-main-20260829-01` wurde genau einmal ausgefuehrt und
vollstaendig aufgezeichnet: 146 Expositionen, 170 Inhaltsproben, 16
Folgenbefunde, 316 Bildanalysen und 1296 Ereignisse. Der
[Befund](reports/tspm1_functional/retention-capacity-main-20260829-01-evaluation/BEFUND.md)
zeigt fuer die gebundenen synthetischen Geschichten: Zwei N1-Expositionen
reichen nach Fast-Verlust nicht zur Erhaltung; vier Expositionen stabilisieren
den Slow-Prototyp mit Support 3. Fast-Ablauf, Slow-Erhaltung und die spaetere
Slow-Ersetzung von N1 durch D1 sowie N2 durch D2 sind getrennt belegt. B4
rekonstruiert die Folgen S1/S2 bis zum Verlust benoetigter FIFO-Inhalte;
TSPM-1 besitzt weiterhin keine vollstaendige Folgenrepraesentation. Der
read-only Verifikator bestaetigt `RECORDING_COMPLETE` ohne Beanstandung. Das
ist eine begrenzte technische Memory-Funktion, kein allgemeiner oder
langfristiger MCM-Memory-Nachweis. Das Gate ist wieder geschlossen; Kerne,
Parameter, API, Snapshot und Feldpfad blieben unveraendert.

Der darauf aufbauende
[S2-FR-Architektur- und Falsifikationsvertrag](docs/S2FR_STATISCHER_ARCHITEKTUR_UND_FALSIFIKATIONSVERTRAG_ATOMARER_B4_TSPM1_VERBUND.md)
bindet B4 und TSPM-1 als getrennte private Sichten auf genau denselben
perzeptiven Eingang. B4 bleibt fuer juengste Inhalte und explizite
Bildungsreihenfolge zustaendig; TSPM-1 bleibt fuer Fast-Spuren und
wiederholungsabhaengige Slow-Stabilisierung zustaendig. Ein spaeterer
Koordinator darf nur die gemeinsame Quelle, atomare Doppel-Fortschreibung,
getrennte read-only Befunde und das vollstaendige Ressourcenledger
bereitstellen. Er ist kein dritter Speicher und trifft keine automatische
Auswahl einer vermeintlich richtigen Erinnerung. S2-FS hat diesen privaten
Koordinator inzwischen in genau einem neuen Modul umgesetzt. Die einmalig
ausgefuehrte neutrale Testsuite bestand `12/12` mit Exit-Code 0. Geprueft sind
gemeinsame Quellenbindung, atomarer Doppelschritt, kein sichtbarer Teilzustand
nach Armfehlern, Einmalowner, getrennte read-only Befunde und das vollstaendige
Ressourcenledger. Das Ergebnis lautet ausschliesslich
`PRIVATE_ATOMIC_COORDINATOR_CONTRACT_VALID`. Ein funktionaler Verbundlauf,
Runner, Feldintegration und automatische Abrufauswahl sind weiterhin nicht
freigegeben.

Der nachfolgende
[S2-FT-Funktions- und Auswertungsplan](docs/S2FT_STATISCHER_FUNKTIONS_UND_AUSWERTUNGSPLAN_ATOMARER_B4_TSPM1_VERBUND.md)
materialisiert die vorgegebene einzelne 17-Schritt-Geschichte ohne
Ausfuehrung. Dabei wurde ein statischer Blocker gefunden: P1 wird im
dreiplatzigen TSPM-Fast-Speicher bereits bei Schritt 4 verdraengt. Seine drei
spaeteren Auftritte erzeugen deshalb nur zwei PPB-1-Aufrufe und Slow-Support 2,
nicht den geforderten stabilen Support 3. Die Geschichte ist nicht zur
Implementierung freigegeben. Als kleinste Korrektur ist ein fuenfter
P1-Auftritt und damit eine 18-Schritt-Geschichte dokumentiert; diese Aenderung
benoetigt eine ausdrueckliche fachliche Entscheidung.

Diese Entscheidung ist mit
[S2-FU](docs/S2FU_STATISCHER_KORRIGIERTER_FUNKTIONS_UND_AUSWERTUNGSPLAN_ATOMARER_B4_TSPM1_VERBUND.md)
erfolgt. Die korrigierte 18-Schritt-Geschichte aktualisiert P2 zunaechst bis
Support 1 und legt P1 danach neu an; drei weitere P1-Aktualisierungen erreichen
Support 3. Elf paarweise verschiedene auditive 4-von-8-Masken verhindern einen
gemeinsamen auditiven Nullprototyp. Der Plan bindet 24 Rezeptoranalysen, 18
Composite-Formationen und die aktualisierten Grenzen `11106/8424/972`.
Fixtures, Implementierung, Tests und Ausfuehrung bleiben gesperrt.

Die anschliessend eng freigegebene private Fixture- und
Auswertungsimplementierung ist inzwischen in genau zwei neuen Modulen
abgeschlossen. Das Fixture bindet Literale, Zeitfenster, Probequellen und
Budgets; der reine Auswerter verarbeitet ausschliesslich bereits erzeugte
Belege und importiert keine Speicher- oder Rezeptorfunktion. Der getrennte
statische AST-Audit bestaetigt alle Umfaenge, Mindestabstaende und
Importgrenzen. Der Befund lautet
`PASS_S2FU_PRIVATE_FIXTURE_EVALUATOR_STATIC_CODE_AUDIT`. Es gab keinen Import,
Test, Zustandsaufruf oder Lauf. Runner und Ergebnisablage bleiben gesperrt.

Die danach einmalig freigegebene neutrale Fixture-/Auswerterqualifikation
bestand `12/12` mit Exit-Code `0` und terminalem `OK`. Funktionale
Negativfaelle wurden mit konsistent neu berechneten Digests als
`S2FU_FUNCTION_FALSIFIED` erkannt; Methodenbrueche endeten `NOT_EVALUABLE`.
Der Status lautet `S2FU_FIXTURE_EVALUATOR_QUALIFICATION_VALID`. Die
synthetischen Evidence-Bundles sind keine Versuchsergebnisse. Speicher-,
Rezeptor-, Koordinator-, Runner- und Dateifunktionen wurden nicht ausgefuehrt;
der 18-Schritt-Hauptlauf bleibt gesperrt.

S2-FV materialisiert danach die private technische Ausfuehrungsgrenze in
genau drei Modulen: geschlossener Runner, append-only Recorder und
unabhaengiger read-only Ergebnisverifikator. Die festen Budgets lauten
`24/54/18/1/6`, insgesamt 103 Operationen und 206 verkettete
START-/RESULT-Ereignisse. Der statische Codeaudit bestand mit
`PASS_S2FV_PRIVATE_RUNNER_RECORDING_VERIFIER_STATIC_CODE_AUDIT`.

Die getrennte neutrale S2-FW-Qualifikation wurde danach genau einmal
ausgefuehrt. Alle zwoelf Tests bestanden mit Exit-Code `0`. Geprueft wurden
kleine neutrale Komponentenpfade, die vollstaendige synthetische
103/206-Aufzeichnung, ihre unabhaengige Verifikation sowie fail-closed
Manipulations- und Teilstandfaelle. Der technische Abschluss lautet
`PASS_S2FW_NEUTRAL_RUNNER_RECORDING_VERIFIER_QUALIFICATION_AUDIT`. Dies ist
kein Memory-Funktionsbefund. Der 18-Schritt-Hauptlauf wurde nicht ausgefuehrt
und bleibt separat gesperrt.

S2-FX hat diesen Hauptlauf spaeter genau einmal unter der Lauf-ID
`s2fx-main-20260830-01` ausgefuehrt. Die unabhaengige read-only Verifikation
bestaetigt die vollstaendige Aufzeichnung mit 103 Operationen und 206
Ereignissen. Eine positive Funktionswertung wurde dennoch nicht gebildet:
Der zusammenfassende Formationsbeleg meldet den visuellen P1-Support nach
Prototypmittelung als `0`, waehrend der gespeicherte Slow-Zustand und der
finale read-only Befund Support `3` zeigen. Die Auswertung stoppte deshalb
fail-closed mit
`S2FX_FUNCTION_EVALUATION_NOT_EVALUABLE_EVIDENCE_CONTRADICTION`. Der Lauf
bleibt abgeschlossen und wird nicht nachtraeglich repariert oder wiederholt.

S2-FY hat danach ausschliesslich die Ursache in der kuenftigen
Slow-Support-Instrumentierung korrigiert. Die Auslesung verwendet nun die
bestehende normalisierte PPB-1-L1-Distanz und die unveraenderten nativen
Schwellen statt exakter Float-Tupelgleichheit. Eine einmalige neutrale
Qualifikation bestand `8/8` mit Exit-Code `0`; Support `3`, Support `1`,
Modalitaetsbindung, Fail-Closed-Verhalten und Zustandsunveraendertheit sind
abgedeckt. S2-FX bleibt dennoch `NOT_EVALUABLE`. Ein neuer 18-Schritt-Lauf ist
nicht durch S2-FY selbst freigegeben.

S2-FZ hat den unabhaengig freigegebenen Bestaetigungslauf spaeter genau einmal
unter `s2fz-confirmation-20260830-01` ausgefuehrt. Die read-only Verifikation
bestaetigt `RECORDING_COMPLETE`, 103 Operationen, 206 Ereignisse und Issues
`0`. Die kanonische reine Auswertung endet ohne Methodenproblem oder
Funktionsabweichung mit `S2FU_FUNCTION_CONFIRMED`: B4 erhaelt die fruehe
Viererfolge, P1 bleibt nach Verlust aus B4 und Fast mit Slow-Support `3`
abrufbar, P2 bleibt bei Support `1` instabil und wird nach B4-/Fast-Verlust
nicht abgerufen. Der begrenzte Befund ist ein MCM-kompatibler
Memory-Grundbaustein auf Engineeringebene, keine allgemeine Langzeit-Memory
und keine automatische Kontextauswahl.

S2-GA bindet darauf aufbauend ausschliesslich den statischen Vertrag fuer ein
privates `PerceptualContextBundle`. Es darf maximal je einen getrennten
Befund aus `B4_RECENT`, `TSPM_FAST` und `TSPM_SLOW` transparent bereitstellen,
gueltige Abwesenheit von beschaedigter Evidenz trennen und B4-Folgeninformation
nur gesondert ausgeben. Rangfolge, Verschmelzung, automatische Auswahl,
Zustandsaenderung und Feldrueckwirkung bleiben ausgeschlossen. Der Vertrag ist
noch keine Implementierung und noch kein Nachweis funktionaler
Kontextverwendung.

S2-GB hat die private, unveraenderliche Bundleprojektion und genau zwoelf
neutrale Vertragstests angelegt. Der erste einmalige Testlauf endete mit zehn
bestandenen Tests und zwei Fehlern im neutralen Sequenz-Helper, bevor die
beabsichtigten Negativgrenzen erreicht wurden. Der Helper ist statisch eng
korrigiert; dieser erste Lauf bleibt fehlgeschlagen. Die separat freigegebene
S2-GC-Wiederholungsqualifikation bestand danach einmalig mit `12/12`,
Exit-Code `0`, terminalem `OK` und identischen Quellhashes. Damit gilt
`PRIVATE_READ_ONLY_PERCEPTUAL_CONTEXT_BUNDLE_VALID`. Eine funktionale
Kontextverwendung ist daraus noch nicht belegt; Speicherkerne, API, Snapshot
und Feldpfad blieben unveraendert.

S2-GD bindet anschliessend die Zielabbildung auf zwei logische Bereiche.
`A_RECENT` erhaelt B4-Inhalt, B4-Kurzfolge und die weiterhin getrennte interne
Fast-Spur. `B_STABLE` stellt nur stabilisierte auditive und visuelle
Slow-Prototypen ohne Reihenfolge bereit. Das Drei-Rollen-Bundle bleibt
unveraenderte technische Referenz. Der vorhandene TSPM-Receipt erlaubt nur
die engere Aussage einer Fast-ausgeloesten, originalquellgebundenen
Slow-Aktualisierung; eine Uebertragung des gesamten A- oder B4-Zustands ist
nicht belegt. Implementierung und Kontextvergleich sind noch nicht
freigegeben.

Der S2-GE-Materialisierungscheck stoppt die unmittelbar vorgesehene
Schattenprojektion vor Code und Tests. Das qualifizierte S2-GC-Bundle bewahrt
bei `NO_STABLE_SLOW_MATCH` keinen konkreten instabilen Support, waehrend S2-GE
diese Evidenz verlustfrei erhalten soll. Aus einem Abwesenheitscode darf kein
Support rekonstruiert werden. Als kleinste Korrektur ist ein privater,
relational gebundener Eingangsbeleg aus unveraendertem S2-GC-Bundle und genau
seinem vorgelagerten validierten S2-FS-read-only-Befund vorgeschlagen. Diese
erweiterte Eingangsgrenze ist mit S2-GF nun statisch gebunden. Das Bundle
bleibt alleinige Autoritaet fuer oeffentliche Kandidaten; der S2-FS-Befund
darf nur instabile Slow-Slots als interne Pruefevidenz liefern. Da beide
read-only Artefakte keine historische Owner-ID tragen, bindet S2-GF einen
neuen gemeinsamen Einmal-Owner fuer die Belegpaarung und behauptet keine
rueckwirkende Ownergleichheit. Implementierung und Materialisierbarkeitsaudit
bleiben gesperrt.

Die folgenden Architektur- und Hypothesentexte erteilen keine Ausfuehrungs-
oder Integrationsfreigabe und sind von dieser privaten Engineeringrichtung
zu unterscheiden.

## Grundarchitektur

![Schaltplan des gemeinsamen MCM-Feldes](docs/bilder/architektur/mcm_field_organism_gemeinsames_feld_schaltplan.png)

Jede Sinnesmodalität besitzt einen eigenen Rezeptorpfad. Herkunft, lokale
Geometrie und Zeitlage bleiben bis zum jeweiligen MCM-Dock erhalten. Eine
Modalität kann allein Weltkontakt in das gemeinsame Feld einbringen, auch wenn
andere Sinneskanäle fehlen oder gerade keinen Kontakt haben.

Der Rezeptorenverteiler erhält ausschließlich abgeschlossene technische
Rezeptorzustände. Er ordnet sie einer gemeinsamen technischen Feldzeit und offenen
MCM-Docks zu. Er speichert kein Memory, erzeugt keine Bedeutung und fusioniert
die Kanäle nicht zu einem vorgegebenen Muster.

Hinter den Docks existieren keine getrennten auditiven, visuellen oder taktilen
MCM-Felder. Alle Docks wirken auf dieselbe synchrone MCM-Neuronenschicht. Deren
vollständiger Zustand ist die gemeinsame gegenwärtige innere Feldlage.

Eine hypothetische MCM-Memory ist architektonisch keine nachgeschaltete Datenbank.
Entwicklung kann nur im fortlaufend weltberührten gemeinsamen Feld stattfinden.
Falls sich dabei wirksame Beziehungen oder eine beschreibbare Feldtopologie
bilden, sind sie Folgen derselben Feldentwicklung, keine
gesondert programmierte Zielfunktion. Die dafür notwendige Memorymechanik ist
noch in Forschung.

Semantische Resonanz, Reflexion und Offline-Erholung sind Rollen dieses
gemeinsamen Feldsystems, aber noch keine behaupteten Fähigkeiten. Sprache darf
später nur als weitere erfahrene Feldform angebunden werden. Reflexion müsste
das gegenwärtige Feld erneut auf dieselbe Neuronenschicht wirken lassen.
Offline-Erholung bleibt ein Betriebsmodus mit reduziertem Weltkontakt bei
weiterlaufendem Feld, kein Training, kein Replay und kein Ausschalten.

Im Wachzustand ist äußerer Weltkontakt die primäre Ursache der aktuellen
Feldlage. Eine spätere entwickelte Feldorganisation dürfte als innerer Kontext
mitwirken; Reflexion wäre ihre zeitlich getrennte Rückwirkung auf dasselbe
Feld. Verdichtung, Syntax und Sprache bleiben dabei Entwicklungsfolgen und
werden nicht als Speicher- oder Bedeutungsmodule vorgegeben.

## Zielrichtung der Feldentwicklung

Das folgende Schema beschreibt die angestrebte Forschungsrichtung, nicht den
bereits implementierten Funktionsumfang:

```mermaid
flowchart TD
    W["Welt und Erleben<br/>sehen · hören · fühlen · handeln"]
    R["Rezeptorschicht"]
    V["Verteiler"]
    M["Gemeinsames MCM-Feld"]
    F["Aktuelle Feldlage<br/>Streuung · Feldmuster"]
    K["Resonanz und Kohärenz<br/>vor-sprachliche Übereinstimmung"]
    T["Differenzierung der<br/>Verarbeitungstiefe"]

    A["Getragene Feldbereitschaft<br/>implizites Erkennen"]
    D["Innerer Dialog<br/>Reflexion · Selbstklärung"]
    S["Semantische Verdichtung<br/>eigene Bezeichnungen"]
    E["Erfahrung und Verdichtung<br/>gesehen · gefühlt · erlebt · bewegt"]
    P["Stabilere getragene Form<br/>Musterkohärenz"]
    N["Spätere ähnliche Wahrnehmung<br/>Wiederkontakt"]

    W --> R --> V --> M --> F
    F --> K --> T
    T --> A
    T --> D
    D --> S --> E
    A --> E
    E --> P --> N --> M
    P --> K

    X["Nicht gemeint:<br/>Bildspeicher · Rohdatenbank<br/>Wort-Objekt-Mapping<br/>künstliches Rauschen<br/>Selbstbeobachtung per Bildschirm/Kamera"]

    X -. ausgeschlossen .-> M

    classDef world fill:#e7f0f7,stroke:#35627d,stroke-width:2px,color:#102a3a;
    classDef field fill:#dcefe6,stroke:#367a57,stroke-width:2px,color:#173b28;
    classDef process fill:#fff1cf,stroke:#9b7316,stroke-width:2px,color:#49370a;
    classDef memory fill:#eadff2,stroke:#70458a,stroke-width:2px,color:#321c40;
    classDef excluded fill:#f7dddd,stroke:#a54242,stroke-width:2px,color:#4c1d1d;

    class W,R,V world;
    class M,F field;
    class K,T,A,D process;
    class S,E,P,N memory;
    class X excluded;
```

Technisch umgesetzt ist der Pfad von Weltkontakt und Rezeptoren bis zur
aktuellen gemeinsamen Feldlage. Resonanz, Kohärenz, Verarbeitungstiefe,
getragene Feldbereitschaft, innerer Dialog, semantische Verdichtung und eine
später rückwirkende getragene Feldform sind offene Forschungsfunktionen.

Insbesondere darf die Differenzierung der Verarbeitungstiefe nicht als feste
Relevanzschwelle oder Umschalter programmiert werden. Eine getragene Kohärenz
müsste sich daran zeigen, dass unterschiedliche reale Weltgeschichte bei
später angeglichener aktueller Aktivierung und angeglichenem Nachhall die
lokale Feldweiterleitung weiterhin kausal verändert. Diese
Beobachtungsanforderung legt noch keine Speichergröße oder Mechanik fest.

## Forschungsgrenze

Fest vorgegeben werden dürfen nur transparente digitale Naturbedingungen:

- Kausalität und gemeinsame technische Feldzeit
- atomare Berechnung aus demselben vorherigen Zustand
- lokale Wechselwirkung
- endliche lokale Ressourcen
- numerische Schutzgrenzen
- stabile technische Identitäten
- ein vollständig passiver Observer

Nicht als Runtime-Ziel vorgegeben werden Muster, Syntax, Kontext, Semantik,
Rollen, Emotion, Bedeutung, Reward, Zieltopologie oder gewünschte Intelligenz.
Eine langsamere Organisations- oder Memory-Schicht wird erst Teil der Mechanik,
wenn ihre Notwendigkeit, Zustandsrolle, Wirkung, Begrenzung und Lösbarkeit
getrennt nachgewiesen sind.

Die Entwicklungsreihenfolge ist bindend: Zuerst muss die kontinuierliche
Kernmechanik aus Weltkontakt, Rezeptoren, Verteiler, Docks, MCM-Neuronenschicht
und gemeinsamem laufendem Feld stehen. Danach wird eine hypothetische
MCM-kompatible Memory-Architektur untersucht. Natürliche
Lösung und Wiederbindung, semantische Resonanz, Reflexionsrückwirkung,
selbstständige Eingangs- und Feldregulation sowie Resonanz zur Sprache sind
darauf aufbauende Forschungsrichtungen. Keine dieser Fähigkeiten wird als
fertiges Verhalten vorprogrammiert.

## Projektphase

Die technische Weltkontaktstrecke ist jetzt auf die neue Zustandsgrenze
ausgerichtet:

```text
Rezeptoren -> neutraler Rezeptorenverteiler -> offene Docks
-> eine gemeinsame MCM-Neuronenschicht -> gemeinsamer Feldzustand
```

Der implementierte Pfad prüft nur verlustfreie Herkunft, gemeinsame Zeit,
atomare Feldaktualisierung und Reihenfolgeunabhängigkeit. Er behauptet noch
keine MCM-Memory-Funktion, keine natürliche Lösung oder Wiederbindung, keine
semantische Resonanz, keine Reflexionsrückwirkung, keine Selbstregulation,
keine Resonanz zur Sprache und keine Offline-Wirkung.

Ein endlicher realer Audio-Video-Lauf bestätigt inzwischen, dass letzte
vollständige auditive und visuelle Rezeptorzustände aus real überlappenden
Aufnahmefenstern über getrennte Docks in dieselbe MCM-Neuronenschicht gelangen.
Dabei werden keine Bild- oder Audiorohdaten im Feldzustand gespeichert.

Das Projekt befindet sich weiterhin in der technischen Vorarbeit.
Schnittstellen-, Zustands- und Regressionstests sind deshalb keine
Forschungsversuche. Eine neue Versuchsreihe beginnt erst, wenn der vollständige
Grundpfad als zusammenhängendes System freigegeben ist.

Die Überlegung/Idee der Feldintelligenz wird nicht als eigene Evidenzachse verfolgt. 
Frühere Untersuchungen bleiben im Archiv als Komponentenevidenz, Regression,
Gegenbaseline oder historische Architekturevidenz erhalten, werden aber nicht
automatisch auf das gemeinsame MCM-Feld übertragen.

Vorarbeiten aus
[MINI_DIO](https://github.com/H5Pro2/MINI_DIO) und der
[Mental-Core-Matrix](https://github.com/H5Pro2/Mental-Core-Matrix-MCM) dienen
als Forschungsgrundlage. Sie gelten nicht automatisch als Evidenz des neuen
Systems.

## Grunddokumente

- [Priorisierter Umsetzungsplan](PRIO_UMSETZUNGSPLAN.md)
- [Bauplan und Anweisung](BAUPLAN_UND_ANWEISUNG.md)
- [Vorarbeitsstand bis zum Forschungsstart](docs/VORARBEITSSTAND.md)
- [Gründungs- und Architekturvertrag](docs/GRUENDUNGSVERTRAG.md)
- [Gemeinsames MCM-Feld: verbindliche Architekturgrenze](docs/architektur/024_GEMEINSAMES_MCM_FELD_ARCHITEKTUR.md)
- [Rezeptorvertrag und Dockgrenze](docs/architektur/025_REZEPTORVERTRAG_UND_DOCKGRENZE.md)
- [Gemeinsamer Audio-Video-Feldkontakt](docs/architektur/026_GEMEINSAMER_AUDIO_VIDEO_FELDKONTAKT.md)
- [Doppelte Selbstregulation: MCM-Rückführung und Eingänge](docs/architektur/027_DOPPELTE_SELBSTREGULATION_GRENZE.md)
- [Hypothetische MCM-Memory-Entwicklungsrichtung](docs/architektur/028_HYPOTHETISCHE_MCM_MEMORY_ENTWICKLUNGSRICHTUNG.md)
- [Weltkontakt, innerer Kontext und Feldrückwirkung](docs/architektur/030_WELTKONTAKT_INNERER_KONTEXT_UND_FELDRUECKWIRKUNG.md)
- [Feldzeitübergabe des gemeinsamen MCM-Feldes](docs/architektur/031_FELDZEITUEBERGABE.md)
- [Transienter lokaler Dockverlauf](docs/architektur/032_TRANSIENTER_LOKALER_DOCKVERLAUF.md)
- [Transiente lokale Neuroneneingabe](docs/architektur/033_TRANSIENTE_LOKALE_NEURONENEINGABE.md)
- [Transiente Neuronenantriebsrolle](docs/architektur/034_TRANSIENTE_NEURONENANTRIEBSROLLE.md)
- [Atomare transiente Feldübergabe](docs/architektur/035_ATOMARE_TRANSIENTE_FELDUEBERGABE.md)
- [Beobachtungsgrenze statt Feldtakt](docs/architektur/036_BEOBACHTUNGSGRENZE_STATT_FELDTAKT.md)
- [Minimale lokale Feldentwicklungsrolle](docs/architektur/037_MINIMALE_LOKALE_FELDENTWICKLUNGSROLLE.md)
- [Zulässigkeitsmethodik der ersten lokalen Felddynamik](docs/architektur/038_ZULAESSIGKEITSMETHODIK_ERSTE_LOKALE_FELDDYNAMIK.md)
- [Evidenzgrenze und Neustart der Feldforschung](docs/EVIDENZGRENZE_GEMEINSAMES_MCM_FELD.md)
- [Offene Forschungsfragen](docs/FORSCHUNGSFRAGEN.md)
- [Historische Architekturstände](docs/architektur/HISTORISCHE_ARCHITEKTURSTAENDE.md)
- [Archiv der Vorarbeiten](docs/archiv/vorarbeiten_bis_forschungsstart/README.md)
