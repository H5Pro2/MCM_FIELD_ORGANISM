# S2-EE: Korrektur- und Ausfuehrungsbindungsvertrag

## Geltung und Grenze

Quellstand: `d734d066991137381c434ebbf08aa76fb209b13d`.
Dieser rein statische Vertrag bearbeitet ausschliesslich ED-B01 bis ED-B05.
Die maschinenlesbare Begleitdatei
`S2EE_TSPM1_STATISCHER_KORREKTUR_UND_AUSFUEHRUNGSBINDUNGSVERTRAG_V1.json`
bindet die Einzelrollen, die 18 Sollproben und die Abbruchreihenfolge.

Nur in diesen fuenf Bereichen ersetzt S2-EE widersprechende Regeln aus
S2-DQ/DR/DT/DU/DV. Historische Vertraege und Ergebnisse bleiben unveraendert.
Die neue Auswertungsrolle heisst `S2EE_FUNCTIONAL_EVALUATION_V1`; sie darf
nicht unter einem alten Registry- oder Comparator-Digest ausgefuehrt werden.
S2-EC bleibt ein Abschluss der alten 51 Vertragstests, keine Abnahme dieses
neuen Vertrags oder einer noch nicht korrigierten Implementierung.

Keine neue Speichermechanik, keine Aenderung an TSPM-1-Grundkern oder PPB-1.
H1-H7, acht Arme, 56 Zellen, Quellenwerte, Zeiten, Kapazitaeten, Match- und
Aktualisierungsparameter sowie PPB-Direktindizes bleiben erhalten. Es werden
keine Tests, Zustandsfunktionen, Registrybuilder oder Vergleiche aufgerufen.
Nur diese zwei Vertragsdokumente werden angelegt. Keine Laufnummer.

## 1. Architekturunabhaengige Funktion

Jeder Arm erhaelt dieselben 42 Bildungseingaben und 18 Probemoeglichkeiten.
B0 ignoriert Eingaben; B1_BUDGET_MATCHED schreibt nur an den 19 gebundenen
Indizes je Modalitaet. B1_DIRECT nutzt alle 42. Diese unterschiedliche
Nutzung des gleichen angebotenen Eingabebudgets bleibt sichtbar und wird
nicht durch zusaetzliche Proben oder nachtraegliche Indizes ausgeglichen.

Die Beobachtung einer Probe besteht aus dem nativen booleschen Abrufresultat
und, bei positivem Abruf, den tatsaechlich ausgewaehlten acht auditiven und
18 visuellen Werten. Diese muessen aus dem beobachteten Armzustand stammen.
Ein Wrapper darf weder einen nicht erkannten Slot zum Abruf erklaeren noch
die Werte aus Probeinput oder Sollvorlage ergaenzen. Fehlende, falsch
dimensionierte oder nicht quellgebundene Werte sind methodisch ungueltig.
Bei negativem Abruf bleibt das ausgewaehlte AV-Payload null; diagnostische
Kandidatenslots duerfen getrennt vorhanden sein, werden aber nicht abgerufen.

Die Sollwerte stammen ausschliesslich aus der statischen Paarliste des
Evaluators. Sie erreichen weder Speicheroperator noch Abrufauswahl. Alle
positiven Proben erwarten ihren gleichnamigen Bildungstraeger; nur NEAR
erwartet AX. PARTIAL_OUT, OUTSIDE und FAR in H7 erwarten negative Abrufe.
Die 18 Einzelfaelle stehen vollstaendig im JSON.

Ein positiver Sollfall ist funktional korrekt, wenn der native Abruf
positiv ist und die vorhandene normalisierte mittlere L1-Abweichung zum
Sollpayload fuer jede Modalitaet hoechstens 0.2 betraegt. Dieser fuer alle
Arme gleiche Auswertungsschwellenwert verwendet die bereits gebundene
0.2-Groesse; er aendert keine native Matchschwelle. Beide Abweichungen
werden getrennt berichtet. Ein negativer Sollfall ist nur bei negativem
nativem Abruf korrekt. Ein korrekt verweigerter Abruf ist kein technischer
Fehler; ein verfehlter positiver Abruf ist ein Funktionsfehler, kein Abbruch.

| Praedikat | Ausschliesslich funktionale Bedingung |
| --- | --- |
| P1_EARLY | H1/1/AX ist korrekt. |
| P2_LATE | H3/12/AX ist korrekt. |
| P3_CONFLICT | H2/4/AX und H4/6/AX, AY, BX sind korrekt; die ausgewaehlten numerischen AX-Werte von H2 und H4 sind exakt gleich. |
| P4_CAPACITY | H5/8/AX, P4 und H6/7/AX, D1, D3, D8 sind korrekt. |
| P5_SELECTIVITY | Alle fuenf H7/4-Proben sind korrekt. |

P4_CAPACITY ersetzt die fruehere unvollstaendige P4_EVICTION-Auswertung.
Es wird kein Verdrangen eines bestimmten internen Slots gefordert. Hat ein
Arm genug Kapazitaet, darf er die Aufgabe ohne Verdrangung loesen. Ablauf,
LRU und Freigabe werden getrennt gegen seine eigenen Operatorregeln auf
technische Gueltigkeit geprueft und bringen keine Funktionspunkte.

H2/1/AX ist eine voll berichtete Latenzbeobachtung, kein sechstes Praedikat.
H6 ist nun explizit Teil von P4. Alle 18 Proben werden bei der Fehlersumme
beruecksichtigt. Fast-/Slow-Rollen, Stabilitaetsflags, Slotzahlen,
Konsolidierungsereignisse, Digestwechsel und interne Komplexitaet sind
Diagnostik, niemals Ersatz fuer diese Aufgaben. Ein fehlendes internes
Merkmal bleibt null und wird nicht in eine erfundene Eigenschaft umkodiert.

## 2. Einheitliche Operationszaehlung

Das Kostenmodell bleibt ein logisches 64-Bit-Ressourcenmodell, keine
CPU-, Laufzeit- oder Python-Heap-Messung. Obergrenzen bleiben unveraendert:
269 Speicherwoerter gemeinsam; 293 funktionale Schreibwoerter je Bildung;
234 Distanzterme je Bildung oder Probe; null funktionale Probeschreibwerte.
Kleinere Armkapazitaeten bleiben gebunden. Grenzwerte werden getrennt von
Verbrauch und Rest gefuehrt; es gibt keine Saldierung zwischen Schritten.

Ein Distanzterm ist die Bearbeitung einer Koordinate einer L1-Distanz.
Jede tatsaechliche Auswertung zaehlt ihre volle Dimension, auch bei gleichen
Werten. Alle Aufrufe innerhalb des privaten Bildungs-/Probeaufrufs samt
Rueckgabevalidierung werden erfasst. Wiederholte Fast-Validierung, PPB-
Vergleiche und erneute S1WU-Belegproben werden nicht rabattiert. Der
Distanzbeleg trennt `functional_terms` und `validation_terms`; deren Summe
steht im gebundenen Verbrauchszaehler und wird gegen 234 geprueft.

Die ausserhalb des Arms liegende Sollauswertung zaehlt ihre zwei
L1-Berechnungen je positiv abgerufenem positiven Sollfall gesondert als
`evaluation_terms`. Sie veraendert keine Auswahl und ist kein weiterer
Armabruf. Ihr identisches Maximum ist 26 je Probe. Hashing, Serialisierung,
Skalarvergleiche, Sortierung und Interpolation sind keine L1-Terme. Sie
werden nicht faelschlich als kostenlose Gesamtberechnung interpretiert.
Insbesondere erzeugt die B3-Bildungsinterpolation allein keine Distanzterme.

Schreibwerte sind logische Zustandsaktionen, nicht die Anzahl geaenderter
Bits und nicht alle Kopien eines unveraenderlichen Python-Objekts. Ein
geschriebener oder geleerter Slot wird mit seiner festen Nutzbreite belastet,
auch wenn einzelne Werte gleich bleiben. Ablauf und anschliessende
Neubelegung desselben Slots sind zwei Aktionen. Unveraenderte Slots werden
nicht belastet; Probezustand und funktionale Schreibmenge bleiben unveraendert.

| Aktion | Logische Schreibwoerter |
| --- | --- |
| Fast-Slot leeren oder schreiben | 30: Belegung, 26 Werte, Support, letzte Auswahl, Konsolidierungszaehler |
| Fast-Bildung globale Fortschreibung | 3: Expositionszaehler und zwei Quellendzeiten |
| Fast-Konsolidierungszaehler nach Uebergabe | 1 zusaetzlich |
| PPB-Slot leeren oder schreiben | Dimension + 3: Belegung, Werte, Support, letzte Auswahl |
| PPB-Bildung globale Fortschreibung | 2 je aufgerufener Bank: Schritt und Quellendzeit |
| B2-Slot leeren oder schreiben | 29; dazu 1 globaler Schritt je Bildung |
| B3-Bildung | 29 einschliesslich Belegung, Werten, letzter Bildung und Schritt |
| B4-Eintrag schreiben/ersetzen | 28; dazu 1 globaler Schritt je Bildung |
| B0 oder uebersprungene PPB-Bildung | 0 |

Composite-Generation ist ein gepruefter Alias der Fast-Schrittzahl, keine
zusaetzliche freie Speicherressource. Statische IDs/Konfigurationen und
Belegobjekte zaehlen nicht als funktionaler Zustand. Die reservierten
Armressourcen bleiben auch bei abgeleiteten oder freien Feldern unverkuerzt.
Die JSON-Regeln binden die Zaehler an Ablauf-, Auswahl- und Aufrufbelege.
Ein bloesser Nachzustandsdiff reicht nicht: Schreiben desselben Wertes muss
erfasst werden. Validierungsberechnungen ohne funktionale Fortschreibung
erzeugen keine funktionalen Schreibaktionen, ihre Distanzen zaehlen aber mit.

Bei der spaeteren Umsetzung muss jeder Aufrufort an einen eindeutigen
Kostenbeleg gebunden sein. Eine unbelegte, fehlende oder doppelte Zaehler-
Zuordnung ist methodisch ungueltig. Der relationale Budgetvalidator bleibt
der einzige semantische Ablehnungsort fuer authentische Ueberschreitungen.
Der Matrixowner faengt diese Ablehnung nur ab und beendet den Versuch.
Nach dem Versiegeln des Operationsbelegs darf der Comparator keine nativen
Distanzberechnungen wiederholen. Er prueft Belegrelationen und Summen;
die gesondert gezaehlte Sollauswertung ist davon getrennt. So werden Kosten
nicht erst nachtraeglich in einen bereits abgeschlossenen Receipt eingefuegt.
S2-EE behauptet nicht, dass unveraenderter Code diese Zaehler schon liefert
oder jede Geschichte unter den Grenzen bleibt. Das muss S2-ED statisch
pruefen; bei einem Widerspruch bleibt die Ausfuehrung geschlossen.

## 3. Vollstaendige Rang- und Entscheidungsordnung

Methodische Gueltigkeit hat immer Vorrang, fuer jeden Arm gleich.
Quell-, Budget-, Owner-, Operator-, Probe-, R0- oder Belegfehler duerfen
nicht als schlechte Speicherleistung eines Konkurrenten gewertet werden.
Sie machen den gesamten Vergleich ungueltig. Ein vollstaendiger gueltiger
Vergleich hat null technische Fehler in jedem Arm.

Die Rangfolge ist lexikographisch: negative Anzahl erfuellter P1-P5,
funktionale Fehlersumme, beobachtete Aufnahmelatenz, gesamte funktionale
Schreibwoerter, ASCII-Arm-ID. Die funktionale Fehlersumme zaehlt jeden
unkorrekten der 18 Sollfaelle einmal; eine verfehlte AX-Erhaltung zaehlt
einen weiteren Fehler nur, wenn beide beteiligten Abrufe bereits korrekt
sind. Technische Fehler bleiben hiervon getrennt.

Aufnahmelatenz ist nur die erste erfolgreiche H2-AX-Probe bei Checkpoint
1 oder 4; ohne Erfolg gilt der endliche Rangwert 5 mit Flag
`NOT_OBSERVED`. Daraus folgt keine Messung an den ungeprobten Schritten
2 oder 3. Die Schreibsumme umfasst alle 42 Bildungsangebote des Arms,
einschliesslich der nulllastigen Angebote. Keine neue Probe zur Tie-Aufloesung.

Alle acht Arme erhalten dieselben Metriken und denselben Rangschluessel.
Die staerkste einfache Baseline wird aus B0, B1_DIRECT, B1_BUDGET_MATCHED,
B2, B3 und B4 bestimmt. R0 wird zusaetzlich gleichwertig berichtet und bleibt
die obligatorische unabhaengige Exaktheitskontrolle, nicht ein ausblendbarer
Konkurrent. ASCII-Aufloesung ist nur eine reproduzierbare Berichtswahl,
kein fachlicher Vorteil bei ansonsten gleichen Werten.

Die Entscheidungsreihenfolge ist verbindlich:

1. Methodische Verletzung oder unvollstaendiger Versuch: `METHOD_INVALID`.
2. Gueltige Belege, aber nicht alle fuenf TSPM-Praedikate erfuellt:
   `TSPM1_FUNCTION_NOT_VALID`, auch wenn Baselines dieselben Fehler zeigen.
3. TSPM erfuellt alle fuenf Aufgaben und mindestens eine einfache Baseline
   ebenfalls: `FUNCTION_VALID_SIMPLE_BASELINE_EXPLAINS`.
4. TSPM erfuellt alle fuenf Aufgaben und keine einfache Baseline ebenfalls:
   `TSPM1_TWO_TIMESCALE_ENGINEERING_ADVANTAGE_OVER_SIMPLE_BASELINES`.

Die letzte Aussage ist strikt auf diese Aufgaben/Fixtures beschraenkt.
Eine exakte R0-Erklaerung bleibt auch dann bestehen; daraus wird niemals
ein Vorteil gegenueber R0 oder ein eigenstaendiger MCM-Mechanismus.
Ein Kostentie oder eine andere Digestidentitaet erzeugt keinen funktionalen
Vorteil. Einfache Erklaerung bedeutet Aufgabenerfuellung, nicht identische
interne Zustaende. Numerische Abruffehler werden zusaetzlich berichtet.

## 4. Durchgaengige Quell- und Ergebnisbindung

Der spaetere Ausfuehrungsplan bindet Vertragsversion, vollstaendige Registry,
Quellmanifest, Laufumgebung, Kostenregeln und Sollauswertung. Das Manifest
enthaelt fuer alle transitiv verwendeten Projektmodule Pfad, Git-Blob und
Rohbyte-SHA256. Eingabedefinitionen und Codequellen sind getrennte Rollen.
Ein Hash der Traegerliste ersetzt keinen Quellcodehash. Dynamisch nicht
statisch aufloesbare Projektimporte stoppen den Preflight. Pythonversion,
Interpreterpfad/-hash und relevante Abhaengigkeiten werden ebenfalls gebunden.

Der Einmalversuch braucht eine spaetere explizite Ausfuehrungsfreigabe fuer
genau diesen Plandigest. Eine Formel allein ist keine Benutzerfreigabe.
Owner- und Verbrauchs-IDs werden aus der dauerhaften Reservierung und der
festen Zellposition abgeleitet, nicht frei vom Aufrufer gewaehlt.

Der JSON-Vertrag definiert eine gerichtete, nichtzirkulaere Belegkette:
Vertrag -> Quellen/Registry -> Ausfuehrungsplan -> Freigabe -> Reservierung
-> Zellstart -> Ergebnis/Ownerabschluss -> Zellbeleg -> Gesamtbefund.
Jeder Digest bindet nur bereits abgeschlossene Vorgaenger und den eigenen
Payload ohne seinen Eigendigest. Das bestehende innere Zellresultat bleibt
vom neuen aeusseren Herkunftsbeleg getrennt; dessen Ergebnisdigest ist keine
Rueckreferenz innerhalb des inneren Receipts.

Die Comparatorgrenze nimmt ausschliesslich vollstaendige quellgebundene
Belege in H1-H7-/Armreihenfolge an. Sie prueft erneut Typen, Eigendigests,
Registry, exakte Rollenmengen, Quellen, Sollproben, Zaehler, Zustandsbelege,
Owner- und Verbrauchsrelationen. Payloads werden kanonisch versiegelt;
ein nachtraeglich veraendertes Dictionary ist keine gueltige Eingabe.
Der volle bestehende R0-Vergleich bleibt zusaetzlich zu den neutralen
Funktionsmetriken erhalten. Kein Nachrechnen einer Zustandsfunktion zur
Belegreparatur, kein synthetisch erzeugter Ersatz fuer einen Zelllauf.

## 5. Dauerhafte Einmaligkeit und atomare Veroeffentlichung

Der unveraenderliche Studienbezeichner ist `s2dr.tspm1.h1-h7.56.v1`.
Alle Vertrags-/Codekorrekturen bleiben innerhalb derselben Einmalgrenze.
Ein neuer Digest, Owner, Prozess oder Branch erzeugt keine neue Erlaubnis.
Die Reservierung bleibt als unveraenderlicher Datensatz mit Status RESERVED
erhalten. Weitere Zustaende werden in einem verketteten Journal angehaengt,
nicht in die bereits digestierte Reservierung zurueckgeschrieben.

Die Freigabe bindet einen kanonischen lokalen Ausfuehrungsbereich aus
Repositorypfad, gemeinsamem Git-Verzeichnis und Hostidentitaet. Dort liegt
die exklusive Reservierung ausserhalb des versionierten Arbeitsbaums.
Ein bereits vorhandener Marker, auch leer oder beschaedigt, sperrt den
Versuch. Es gibt keine Lease, automatische Bereinigung oder Freigabe anhand
einer nicht mehr laufenden Prozess-ID. Weitere Klone/Hosts sind nicht von
derselben Freigabe gedeckt. Manuelles Loeschen oder Ruecksetzen des Ledgers
ist kein unterstuetzter Wiederanlauf und liegt ausserhalb der Zusicherung.

Vor dem ersten Zustandsaufruf muss die Reservierung exklusiv erstellt,
vollstaendig geschrieben und dauerhaft bestaetigt sein. Jeder Zellstart
wird vor seiner einzigen Ausfuehrung ebenso protokolliert. Es gibt genau
eine sequentielle H1-H7-mal-acht-Reihenfolge, keine Parallelisierung,
kein Retry, keine Fortsetzung aus Teilresultaten. Auch ein Absturz vor der
ersten Zelle verbraucht den reservierten Versuch.

Alle erwarteten und unerwarteten Ausnahmen fuehren zu einem terminalen
Fehlversuch. Bei hartem Prozessverlust ohne Endbeleg lautet der abgeleitete
Status `ABORTED_INCOMPLETE`; der persistente Marker bleibt die Sperre.
Das laesst sich read-only feststellen, nicht durch erneute Zellaufrufe
reparieren. Ein vollstaendiger fachlich negativer Vergleich dagegen ist
kein technischer Fehlversuch und darf mit seiner negativen Entscheidung
veroeffentlicht werden.

Erst nach 56 gueltigen Zellbelegen, Quellunveraendertheit und vollstaendiger
Comparatorabnahme wird ein Gesamtartefakt in einem privaten temporaeren
Pfad desselben Dateisystems geschrieben, geschlossen, dauerhaft gesichert
und aus den gespeicherten Bytes nachgeprueft. Ein atomarer No-Replace-
Publikationsschritt macht genau dieses Artefakt sichtbar. Keine existierende
Zieldatei darf ersetzt werden. Ein bereits vollstaendig publiziertes und
valides Artefakt ist terminal, auch wenn der Prozess danach abstuerzt.
Fehlt es oder ist es ungueltig, entsteht kein erfolgreicher Abschluss.

Die konkrete Plattform muss Exklusivitaet, Haltbarkeit und atomare
No-Replace-Publikation vorab nachweisbar unterstuetzen. Ist dies unklar,
bleibt der Ausfuehrungspreflight geschlossen; eine gewoehnliche Datei-
Umbenennung allein ist kein Nachweis von Absturzsicherheit. Die spaetere
Dateiaufzeichnung betrifft Versuchsbelege, nicht Memory-Persistenz oder
den MCM-Feldsnapshot. Vorhandene historische Publisher sind nicht automatisch
fuer diesen Plan freigegeben.

## Abschluss und weiterer Weg

S2-EE bindet die fuenf Korrekturen auf Vertragsebene. Das ist keine
Implementierungsabnahme und kein bestandener S2-ED-Wiederholungsaudit.
Die strukturelle Repraesentationsfrage bleibt ausdruecklich
`NOT_ASSESSED_BY_BOUND_FIXTURES`: zwei variierte Modalitaetsskalare auf
26 Traegern beantworten nicht, ob TSPM-1 ueber einfache Prototypbildung
hinaus strukturierte Wahrnehmungsrepraesentationen ermoeglicht.

Naechster Schritt ist ausschliesslich der erneute statische S2-ED-Audit
dieser Vertragsbindung, einschliesslich Kostenmaterialisierbarkeit und
Publikationsgrenze. Bei einem Restwiderspruch bleibt die Matrix gesperrt.
Auch ein bestandener Vertragsaudit autorisiert weder Codeaenderungen noch
Tests oder den spaeteren Einmallauf.
