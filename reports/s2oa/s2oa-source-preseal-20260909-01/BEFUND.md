# S2-OA: rezeptorfreie Vorversiegelung

ID `s2oa-source-preseal-20260909-01`. Ein Aufruf
`C:/Python314/python.exe -m reports.s2oa.preseal_once` nach bestandener
[18/18-Quellenqualifikation](../s2oa-source-binding-qualification-20260909-01/BEFUND.md).
Exit 0, kein Retry. **S2OA_SOURCES_PRESEALED / S2OA_PRESEAL_BINDINGS_VALID**.

## Umfang und historische Herkunft

Die feste 28-Ereignisfolge wurde unveraendert gebunden: spaeter 20 Formationen,
zwei auditive und sechs visuelle Hinweise. **48/48 Modalitaetsvorkommen**
wurden einmal separat erzeugt: 22 PCM-Fenster und 26 RGB-Frames. Keine
Deduplizierung; jedes Vorkommen besitzt eine eigene Ereignis-/Quellenzeitbindung.

Der Inhalt stammt aus acht festen Rezept-/Transformationsformen: einem
historischen np-a02-PCM-Rezept, fuenf historischen JX-RGB-Ordinalrezepten
0/2/3/4/5 und zwei daraus okkludierten Cue-Rezepten. Alle 22 PCM-Payloads
stimmen mit dem versiegelten historischen np-a02-Hash ueberein; alle 20
vollstaendigen RGB-Payloads stimmen mit dem JX-Katalog ueberein.
Neue Cuehashes wurden ohne Rezeptoranalyse gebunden. Historische Zeitindizes
werden nicht als neue Indizes ausgegeben; die neue OA-Ereignisbindung bleibt separat.

Native Audio-/Videozeiten, exakte Snapshotindizes, unterschiedliche
Modalitaetsfenster und die Felduhr `s2oa-continuous-field-clock` sind in der
Ausfuehrungswurzel enthalten. Sichtbeobachtung 0..23 auditiv und 0..31 visuell
unveraendert; visuelle Okklusion erfolgte vor jeder spaeteren Rezeptoranalyse
bereits im RGB-Payload. Keine versteckten Cuewerte im geplanten Scan.

## Bytegleichheiten

Alle acht Gleichheitsgruppen stehen mit den vollstaendigen Quellen-ID-Listen
in [seal.json](seal.json). Keine zusaetzliche Kollision zwischen den acht Formen:

| Rezeptform | Getrennte Vorkommen | Payload SHA-256 |
| --- | ---: | --- |
| np-a02 PCM | 22 | 80b97d6323c3890a52c31cfc1866fe26e94961fc1a033ae82f990a0eb1f74595 |
| JX ordinal0, voll | 4 | 68d7b1a28b79359d09b8e283d1edd3ee7bf3a7aa899fad60305c9435a3c3aee6 |
| JX ordinal2, voll | 4 | cd7faff71d59428d6a68a77427d6d9b8d4fc4d26f3b35b24a47760186d4106b8 |
| JX ordinal3, voll | 4 | 0a8ea1fa775d43946c3788d5deffe0b082c91c75bd6489674e572e1e1c448960 |
| JX ordinal4, voll | 4 | 5e2a628ad25ac1f5ae9a36f6c24f91d8daf952048f42a43f25911abf533c6d1f |
| JX ordinal5, voll | 4 | 8846cd7252d493b46f87bf3645ead8b650e8c16ef40817ebf0d8c8861714dd9d |
| JX ordinal0, okkludiert | 4 | 830042ca17af96f000d69cb56deed1c4507454d69c8461301eedb28ec8dc6d38 |
| JX ordinal5, okkludiert | 2 | aa5155bde35cda360624067a6175d29b07c9c230b1b3994fdbff845bdffc8ee9 |

Die technische Ausfuehrungswurzel enthaelt Quellen, Ereignisse, Zeiten,
Profile und Grenzen. Sollziele, q05/q07-Auswertungsbezug, erwartete Supports
und Ersetzungspositionen stehen ausschliesslich in der getrennten
[Evaluationswurzel](evaluation-plan.json). Keine gemessene Distanz oder
erwartete Slotbildung wurde zur Quellenauswahl verwendet.

## Einmalige read-only Bindungspruefung

[verification.json](verification.json) bindet einen Pruefaufruf nach der
Versiegelung. Ausfuehrungs-/Evaluationswurzel, Ereignis-/Zeitformen,
Quellenidentitaeten, historische Rezept-/Payloadbezuege, Quellhashes,
Interpreter-/Generatoridentitaet, Profilmetadaten, Kollisionstabellen und
Nullzaehler der ausgeschlossenen Funktionen wurden gelesen/geprueft.
Dateihashes vor und nach der Pruefung stimmen ueberein.

**Keine Payloadregeneration in der Verifikation.** Sie bestaetigt die
Bindung der aufgezeichneten Payloadhashes, nicht eine unabhaengige
Nachrechnung der Bytes. Keine Rezeptorgueltigkeit, Slotgeneration oder
funktionale Erreichbarkeit aus dieser Vorversiegelung ableiten.

| Bindung | Digest |
| --- | --- |
| execution_digest | bcaf8ad711b4424e5d79184063dc26e84b24a1ec5030f89d1d06ec5bf78a2f6a |
| evaluation_digest | 39f9ada21bfcc1b57648f9ee4aed9cfb7d237a99d9a5babd3b3b9ec597ef848a |
| seal_digest | 28d6d2408f70265c10adf56dacb7f265a231e508e41af484cf9ff5624b7747fc |
| verification_digest | e91cc7edff27df9c2c6b81927e11dc5feb7cfe528b01b9a3fd5618534cd74fe9 |

Quell-/Testhashes stimmen mit der vorherigen Qualifikation ueberein.
Die vollstaendigen Datei-SHA-256 stehen im Pruefbeleg. Unveraenderter
OA-Planhash `bb87f2a89621d2df6ee248d8b917e59db3758ecdeede2a9ac154fdde93a6a69d`.
CPython 3.14.4 / NumPy 2.4.4, math als bestaetigtes Built-in; Interpreter,
Bibliotheksdateien und reine Generator-AST sind gebunden.

Ausfuehrungsplan 78.644 Byte, Evaluationsplan 1.665 Byte, Vorregistrierung
69.553 Byte, Siegel 6.683 Byte, Verifikation 1.421 Byte. Alle innerhalb
der vorab gebundenen Grenzen. Hoechstens ein PCM-Fenster und ein RGB-Frame
gleichzeitig; keine Rohpayloadablage. Kein neuer Prozesspeaknachweis.

## Verbleibende Freigabegrenze

Keine Rezeptor-/NJ-, Distanz-, Memory-, Feld- oder Runtimeaufrufe. Nur das
lokale Quellenfreigabegate war waehrend der Vorversiegelung geoeffnet und
wurde im finally auf False gesetzt; Systemgates blieben geschlossen.
Historische Belege, Quellen, fremde Aenderungen und Bootstrap unveraendert.

Spaeter verbindlich: eine Runtime ohne Reset; visuelle Generationen aus
tatsaechlichen Transaktionen, nicht aus Sollrollen; q05 nur historischer
Beleg, kein aktueller Verfuegbarkeitsersatz bei q07. Gueltige abweichende
Inventare oder Enthaltungen bleiben auswertbar. Auditive Slow-Ersetzung
und allgemeiner Dauerbetrieb sind nicht abgedeckt.

WEITER: Am besten geht es jetzt mit der Analystenpruefung dieser Quellen-
und Ereignisbindungen weiter. Eininstanz-/Generationsanschluss und dessen
neutrale Qualifikation benoetigen die naechste begrenzte Freigabe; kein
Hauptlauf. Prognosezweig ruht, ME/MI bleiben gesperrt.

## Nachtrag 2026-09-10: statische Budgetzuordnung

**Eine Vertragsabweichung liegt vor.** Die oben historische Aussage
"Alle innerhalb der vorab gebundenen Grenzen" gilt nur gegen die spaeter
eingefuehrte Implementierungsgrenze, nicht als Nachweis der Einhaltung des
freigegebenen OA-Plans. Dieser Nachtrag korrigiert diese Einordnung;
18/18-Testprotokoll, Vorregistrierungen, JSON-Wurzeln, Siegel und einmaliger
Pruefbeleg bleiben unveraendert. Keine erneute Verifikation oder Ausfuehrung.

### Urspruengliche Klassen und tatsaechliche Zuordnung

Der [OA-Plan](../../../docs/S2OA_STATISCHER_FUNKTIONSPLAN_FORTGESETZTER_MCM_BETRIEB.md)
im Plancommit `ed7a2e5b` bindet drei unterschiedliche Klassen:

- Metadaten: 65.536 Byte; kein eigener solcher Betrag je Teildatei.
- Quellen-/NJ-/Formations-/Generationszusatzhulle: **insgesamt** 262.144 Byte,
  nicht je Bestandteil; keine nochmalige Vollkopie der Eingangsmaterialisate.
- Getrennte Verifikation und Auswertung: je 262.144 Byte. Ausfuehrungsplan
  und Vorregistrierung sind weder Verifikations- noch Auswertungsergebnisse.

Der vollstaendige spaetere Gesamtbeleg hat daneben den Deckel 4.194.304 Byte.
Dieser hebt keine Klassengrenze auf. Der Plan weist die zwei spaeteren
Quellenplan-Dateien nicht ausdruecklich einer eigenen Vorversiegelungsklasse
zu; insbesondere gibt es keine vorab festgelegte Aufteilung ihrer gemischten
Quellen-, Ereignis-, Umgebungs- und Verwaltungsbestandteile auf die beiden
ersten Klassen. Diese Luecke erlaubt keine nachtraegliche Umetikettierung.

| Datei | Im ausgefuehrten Anschluss deklarierte Klasse | Groesse | Gegenueber 65.536 Byte |
| --- | --- | ---: | ---: |
| execution-plan.json | insgesamt Metadaten, via MAX_METADATA_BYTES | 78.644 | 13.108 darueber |
| preregistration.json | insgesamt Metadaten, via MAX_METADATA_BYTES | 69.553 | 4.017 darueber |

Beide Dateien enthalten auch Quellenbelege, sind aber nicht vorab als Teile
einer gemeinsam bilanzierten Zusatzhulle gebunden worden. Jede ueberschreitet
bereits allein den Metadatendeckel; die Tabelle gewaehrt nicht jeder Datei
einen separaten 65.536-Byte-Freibetrag. Eine verbindliche Zusatzhuellenbelegung
oder verbleibende Reserve fuer NJ, Formationen und Generationen ist deshalb
aus dieser Bindung **nicht ausgewiesen**. Es wird weder ein nachtraeglicher
Restbetrag gutgeschrieben noch eine tatsaechliche Ueberschreitung der gesamten
262.144-Byte-Zusatzhulle behauptet. Belegt ist die abweichende Limitierung.

### Herkunft der groesseren Grenze

Die [spaetere Qualifikationsbindung](../QUALIFIKATIONSBINDUNG.md), versioniert
in `b754c052`, setzt ausdruecklich "Je Plan-/Belegdatei maximal 262.144 Byte".
Ihr SHA-256 `03a801bac287e186f1b8c7126ae2c203c968163a6759ace7450ca5e5f305f2ed`
ist bereits in beiden Vorregistrierungen gebunden; es ist also keine erst
nach dem Lauf eingefuegte Zahl. Eine Freigabe zur Aenderung der Klassen
oder zur Metadatengrenzerhoehung liegt darin jedoch nicht.

Der [Quellenanschluss](../../../tools/_s2oa_private_source_binding.py) setzt
in Zeile 17 `MAX_METADATA_BYTES=262144`, reicht diesen Wert als
`metadata_bytes` in die Budgets weiter und verwendet ihn bei beiden
Dateipublikationen. Der Qualifikationsaufruf bindet denselben Wert als
`metadata_limit`; Test 16 prueft die Huelle gegen genau diesen Wert.
Der [Verifikator](../../../tools/_s2oa_private_preseal_verification.py)
prueft Planwurzeln einzeln gegen diese Grenze und die vier Quelldateien
zusammen nur gegen 4.194.304 Byte. Er fuehrt keine gemeinsame
262.144-Byte-Zusatzhuellenbilanz und keine 65.536-Byte-Metadatenbilanz.

Damit ist die neue per-Datei-Metadatengrenze eine nicht freigegebene
Abweichung der OA-Anbindung. Das Bestehen der Tests und des Pruefaufrufs
gegen diese groessere Grenze beseitigt die Vertragsabweichung nicht.

### Kleinste Korrekturrichtung, noch nicht ausgefuehrt

Nur die administrative Anschluss-/Serialisierungsbindung korrigieren:
Metadaten gemeinsam auf 65.536 Byte begrenzen; Quellenzusatzbelege und
spaetere NJ-/Formations-/Generationsbelege explizit und gemeinsam unter
262.144 Byte bilanzieren. Gemeinsame Rezepte, Umgebungs- und Codebindungen
einmal referenzieren statt in beiden Wurzeln vollstaendig zu duplizieren;
alle 48 Quellenidentitaeten, Zeitbindungen, Payloadhashes und Erwartungen
erhalten. Keine Payload- oder Rezeptoraenderung und keine Grenzerhoehung.

Eine solche neue kompakte Bindung muesste vor ihrer Nutzung separat
freigegeben und qualifiziert werden. Sie darf die historischen Dateien
nicht rueckwirkend budgetkonform nennen oder ueberschreiben. Jetzt wird
keine neue Huelle erstellt, nichts neu versiegelt und kein Test wiederholt.

**Eininstanz-/Generationsimplementierung und Hauptlauf bleiben gesperrt.**
Gates False; Prognosezweig ruht, ME/MI gesperrt. Ausschliesslich dieser
Nachtrag wird versioniert; Code, versiegelte Belege und Bootstrap unveraendert.

RUECKMELDUNG ERFORDERLICH: Analystenentscheidung ueber die eng begrenzte
administrative Budget-/Referenzbindung. Keine automatische Anschlussfreigabe
aus dem bisherigen 18/18- oder Vorversiegelungsstatus.
