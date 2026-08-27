# S2-EV: Statischer Materialisierbarkeits- und Isolationsaudit

## Status und Grenze

**STATIC_AUDIT_BLOCKED_ONE_BINDING**

S2-EV ist abgeschlossen, aber nicht bestanden. Es verbleibt genau eine
gemeinsame Materialisierungsluecke: EV-B01, die unvollstaendige geschlossene
Pfad- und Rollenbindung fuer Recorderdateien und native Hilfsaufrufe.

Geprueft wurde S2-EU auf Quellstand
`e003773d910af52df123d4a21c050768daa4fedd`.
Dies ist ein Dokumentations- und Quelltextaudit, kein Plattformversuch.
Keine Implementierung, Projektimporte, Zustandsfunktionen, Tests,
Plattformpruefaufrufe, Rechteerhoehung oder Matrixzellen. Keine Laufnummer.
TSPM-1, PPB-1, Feldpfad, API, Snapshot und Runner bleiben unveraendert.
S2-EM und die 56-Zellen-Matrix bleiben gesperrt.

Der maschinenlesbare Begleitbeleg bindet die gelesenen Quellen, Digests,
geschuetzten Git-Baeume und die statischen Einzelpruefungen. Keine
nachtraegliche Aenderung von S2-EU oder seiner Vorgaenger.

## 1. EV-B01: Pfadinventar und Aufrufrollen nicht vollstaendig

### Fundstellen

Im normativen S2-EU-JSON stehen:

- Zeilen 163-178: feste Pfadrollen und Pflicht zur Vorbindung aller Spools,
  Aufzeichnungs-Stagings und Supervisor-Publikationspfade;
- Zeilen 546-562: RunBinding mit BoundPath aus case_id, role und path;
- Zeile 668: PathRole ist auf die ausdruecklichen isolation.paths-Rollen,
  vier Parentrollen, foreign_write_handle und deklarierte Quellhandles begrenzt;
- Zeilen 675-679: native Aufrufe muessen mit passender Pfadrolle vollstaendig
  aufgezeichnet werden, einschliesslich Hilfsaufrufen;
- Zeilen 785-788: jede Belegdatei, B und RecordingManifest benoetigen eigenes
  exklusives Same-Parent-Staging vor ihrer finalen Veroeffentlichung.

Der unveraenderte Dateibaustein oeffnet zusaetzlich alle Vorfahren der
gebundenen Eltern in `_s2er_windows_files.py:133` und gegebenenfalls weitere
Quellverzeichnis-Vorfahren in Zeile 169. Das sind nicht nur die vier
ParentSet-Verzeichnisse oder die eigentlichen Quelldateien.

### Konstruktiver statischer Gegenbeleg

Schon die Veroeffentlichung des p01-Trace benoetigt zwei verschiedene
Dateirollen: dessen endgueltigen Trace und sein eigenes Recording-Staging.
Die vorhandene Rolle `staging` bezeichnet jedoch ausdruecklich das
E4-Subjekt-Staging von p01. Dieses ist nach E5 dessen Ergebnisdatei und darf
nicht als neues Trace-Staging wiederverwendet werden.

Auch B und RecordingManifest brauchen getrennte Stagings, der Worker
nichtfinale Spools. Hierfuer gibt es weder eigene geschlossene Rollen noch
eine gebundene Ableitungsregel vom jeweiligen Belegziel. Ein zusaetzlicher
frei benannter role-Wert widerspricht der geschlossenen Rollenliste.
Eine zweite Belegung derselben Rolle mit anderem Pfad waere ohne eindeutige
Zuordnungsregel ebenfalls nicht pruefbar.

Unabhaengig davon oeffnet pin_parents die uebergeordneten Verzeichnisse.
Deren native Aufrufe duerfen nicht aus der Spur verschwinden. Sie sind aber
weder eine der vier ausdruecklichen Parentrollen noch pauschal ein
deklarierter Quelldatei-Handle. Es fehlt die genaue Bindung solcher
abgeleiteten Lesepfade an ihre Aufrufrollen.

Dies ist keine fehlende aktuelle native Messung und kein Verlangen nach
bereits implementiertem Recordercode. Es fehlt die zulaessige Form und
Zuordnung fuer spaeter einzutragende Werte. Die Implementierung muesste
hier eine neue Vertragsregel erfinden.

### Auswirkung und Schliessbedingung

Vollstaendige E0-Aufzeichnung und atomar nachvollziehbare Recorderablage
sind mit der jetzigen geschlossenen Rollenbindung nicht abnehmbar.
Der gemeinsame Blocker betrifft daher alle 13 Faelle; kein einzelner
Fall wurde ausgefuehrt oder als Plattformbefund bestanden gewertet.

Eine spaeter separat freizugebende statische Korrektur muss:

- alle benoetigten Recorder-Spool-, Staging-, Ziel- und Kontrollablagepfade
  mit eindeutiger Beleg-/Fall-/Actor-Zuordnung darstellbar machen;
- die gelesenen Parent- und Quellverzeichnis-Vorfahren sowie die zugehoerigen
  nativen Aufrufrollen eindeutig aus den zugelassenen Quellen ableiten;
- eindeutige Pfad-/Rollenidentitaet, Kollisionsfreiheit und die absichtlichen
  Ausnahmen fuer Sentinels und p13 unverwechselbar festlegen;
- fuer jeden erreichten Datei-/Verzeichnisaufruf genau eine vorgebundene
  Zuordnung erlauben und unbekannte Pfade weiter fail-closed abweisen.

Keine Erweiterung auf beliebige Pfade, keine neue Fallfamilie und keine
Aenderung der Ablauf-, Fehler-, Herkunfts- oder Abschlussregeln.

## 2. Getrennte Voraussetzungen und Herkunft

PR1-PR6 sind voneinander getrennt und nicht als bereits erfuellt markiert.
Die Abhaengigkeitsrichtung Quellenmanifest -> F -> RunBinding -> externe
Freigabe/Vorregistrierungsabnahme -> Rohbelege/B -> Q ist nicht zirkulaer.
Insbesondere wird fuer den isolierten Versuch keine Q aus seinem eigenen
zukuenftigen Ergebnis vorausgesetzt.

Eine spaetere materielle Abnahme benoetigt weiterhin genaue Elternidentitaeten,
Einrichtungs- und Garantiedokumentation, literal gebundene Quellen/Runtime,
ein unabhaengiges Einmallaufrecht und dessen Verbrauch. Fehlende Istwerte
sind die ausdruecklich vorgesehene spaetere Materialisierung, kein zusaetzlicher
hier erfundener Blocker. EV-B01 betrifft dagegen die dafuer benoetigte Form.

Die 14 nativen API-Namen und ihre Parameteranzahlen im Recordervertrag stimmen
mit den Deklarationen im Dateibaustein ueberein. AST-Analyse liest nur Syntax;
kein Modul wurde importiert oder instanziiert. Die genaue Serialisierung,
Actor-/Barrierenbindung, endliche Aufruf-/Bytegrenzen und unabhaengige
Abschlussbeobachtung bleiben im spaeteren Implementierungsaudit zu pruefen.

## 3. E0-E8 und alle 13 Fallbindungen

Die Ablaufabsichten sind konsistent: E0 Voraussetzungen; E1 Fallreservierung;
E2 Zielreservierung; E3 inerter Beleg; E4 Nutzbytes und Seal; E5 No-Replace;
E6 finaler Datei-Flush und Identitaet; E7 eigener Marker; E8 Live-Bestaetigungen
und fehlerfreie Handleabschluesse. E3/E4/E7 sind nur Datei-Fixtures, keine
Matrixbelege oder Studienreceipts.

Die folgende Abnahme betrifft ausschliesslich die statische Fallabsicht.
Jede vollstaendige Materialisierung bleibt gemeinsam durch EV-B01 blockiert.

| Fall | Statisch gepruefte Bindung | Isolierter Sollzustand |
| --- | --- | --- |
| p01 | E0-E8, benannte Beobachtungsbarrieren vor/nach Rename; kein universeller Crashbeweis | COMPLETED |
| p02 | Genau eine erwartete Parent-ID geaendert; echte Verzeichnisse unveraendert; Abbruch vor Fallreservierung | BLOCKED_PLATFORM_PREREQUISITE |
| p03 | Eigener Sentinel an Fallreservierung; echte CREATE_NEW-Ablehnung 80; Sentinel unveraendert | FAILED |
| p04 | E1 verbraucht, Sentinel an Zielreservierung; echte Ablehnung 80, kein Rollback | FAILED |
| p05 | Sentinel erst nach E4 und letzter Abwesenheitspruefung; Rename abgewiesen, nichtnull nativer Fehler, Sentinel unveraendert | ABORTED_INCOMPLETE |
| p06 | Separater Schreibzugriff gegen gehaltenen Handle; echte Share-Ablehnung 32 | FAILED |
| p07 | Genau N-1 weitergeleitete Stagingbytes; originaler nativer Ausgang getrennt; keine Reparatur | FAILED |
| p08 | Ein unterdrueckter E4-Flush mit eingespeistem Fehler 5; kein Seal/Rename | FAILED |
| p09 | Ein unterdrueckter E6-Flush; lesbare Ergebnisdatei reicht nicht; kein Marker | ABORTED_INCOMPLETE |
| p10 | Genau N-1 Markerbytes; kein nachtraeglicher Flush oder Ersatzmarker | ABORTED_INCOMPLETE |
| p11 | Lesbarer vollstaendiger Marker ohne bestaetigten eigenen Flush | ABORTED_INCOMPLETE |
| p12 | Echter Close genau einmal, danach nur bei dessen Erfolg eingespeiste Ablehnung; kein zweiter Close | ABORTED_INCOMPLETE |
| p13 | Read-only Einordnung von p01 ohne dessen Live-Kontext; kein zweiter Positivlauf | COMPLETE_RECORDS_PRESENT_UNCONFIRMED |

Nur ein exakt vorregistrierter Negativausgang erlaubt den naechsten Fall.
Unerwartete Abweichung stoppt den Gesamtversuch; Folgefaelle bleiben NOT_RUN.
OBSERVED_COMPLETE bezeichnet die vollstaendige Uebereinstimmung eines Falls
mit seinem Sollausgang, nicht notwendig eine erfolgreiche Veroeffentlichung.
Es wurden weder 13 Tests noch 13 Plattformversuche ausgefuehrt.

## 4. Fehler, Recorder und Abschluss

Native Rueckgaben, eingespeiste Rueckgaben und reine Pruefentscheidungen
sind getrennte Belegarten. Weitergeleitete native Aufrufe behalten eigene
Aufrufkennungen und originale Rueckgaben. Unterdrueckte Aufrufe erzeugen
keinen erfundenen NativeFailure. Ein eingespeister Fehler 5 ist kein
beobachteter Rechtefehler.

Der erste native Fehler im B-Beleg ist nach der Reihenfolge echter nativer
CALL_BEGIN-Ereignisse zu bestimmen, nicht aus dem ausgewaehlten Fehlerszenario.
Auch ein erwarteter Abwesenheitsbefund aus require_absent ist als originale
API-Rueckgabe zu erhalten; der spaetere Falltrigger wird separat gegen die
volle Spur geprueft. Setup-/Helferfehler werden nicht passend umgedeutet.

Header, Digestkette, gepaarte Aufrufe und Footer binden die volle Spur.
Fehlender Ruecklauf, Footer, Close oder Protokollteil sperrt COMPLETE.
Nach einem unerwarteten Abbruch sind NOT_RUN und unvollstaendige Originalspuren
Diagnostik, kein Ersatz fuer eine positive Q. Dieser Fehlerpfad darf keine
Erfolgsmarker nachschreiben oder eine Wiederholung erlauben.

Die Veroeffentlichungsreihenfolge ist nicht zirkulaer: eingefrorene Originale,
B, Manifest, eigener Marker, Quellen-/Bytepruefung und erfolgreiche Closes,
erst dann die unabhaengig beobachtete Live-Bestaetigung. Ein Marker kann
seinen eigenen spaeteren Flush nicht beweisen. Der getrennte Kontrollkanal
und die externe Abschlussbeobachtung sind verbindlich; keine Rekonstruktion
eines operativen Erfolgs aus lediglich lesbaren Dateien.

Eine Mehrdateitransaktion wird nicht behauptet. Teilweise vorhandene Dateien
bleiben verbraucht. Native Haltbarkeit, Rechte und G1-G5 sind hier nicht
gemessen oder abgenommen. Die alte S2-EM-Aufzeichnung bleibt unveraendert;
sie wird nicht als erfolgreiche dateibezogene Pruefung neu interpretiert.

## 5. Quellen und technische Grenzen

Statisch verifiziert: 17 direkte Quellen, acht Artefaktdigests, die
S2-EU-Begleittextbindung, drei private Syntaxbaeume und 14 API-Deklarationen.
Die vier geschuetzten Paket-/Test-/Tool-/Reportbaeume stimmen weiterhin mit
S2-EU ueberein. Sechs gebundene Studienausgabepfade sind nicht vorhanden.
Beide Freigabeflags stehen weiterhin auf False.

Die Quellpruefung und JSON-/Hash-/AST-Auswertung sind keine Ausfuehrung der
geprueften Projektlogik. Keine Plattformvorbereitung wurde als Nebeneffekt
angelegt; lediglich diese zwei neuen Auditdokumente werden versioniert.

## Naechster Schritt

**RUECKMELDUNG ERFORDERLICH:** Eine separate Freigabe fuer S2-EW als eng
begrenzten statischen Korrekturvertrag zu EV-B01. Danach S2-EV erneut
rein statisch pruefen. Diese Empfehlung erteilt keine Implementierungs-
oder Ausfuehrungsfreigabe.

**WEITER:** Am besten geht es jetzt mit der vollstaendigen statischen
Pfad- und Rollenbindung fuer den isolierten Recorder weiter.
