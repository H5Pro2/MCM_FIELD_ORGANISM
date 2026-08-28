# TSPM-1: einmaliger Funktionsvergleich vom 28.08.2026

## Ergebnis

Der ausdruecklich freigegebene Versuch `functional-20260828-01` ist vollstaendig
ausgefuehrt und auswertbar: **56 Zellen, 336 Bildungsangebote, 144 Proben,
Exit-Code 0, terminales OK**. Keine Wiederholung oder Teilfortsetzung.
Alle acht Arme haben jeweils sieben frische Zellanfangszustaende, 42
Bildungsangebote und 18 Proben durchlaufen. Fachlich falsche Abrufe sind
Ergebnisse; technische Fehler wurden in keinem Arm gemeldet.

TSPM-1 erfuellt alle fuenf gebundenen Aufgaben. Die unabhaengige R0-Kontrolle
reproduziert die vollstaendige vertragliche TSPM-1-Projektion. Der einfachere
FIFO-Arm B4 erfuellt dieselben Aufgaben mit geringerem logischem Speicher-
und Schreibaufwand. Die technische Entscheidung lautet unveraendert
`FUNCTION_VALID_SIMPLE_BASELINE_EXPLAINS`.

Das ist ein positiver Funktionsbefund fuer die untersuchten technischen
Speicherbausteine, keine Begruendung fuer eine neue MCM-Feldmechanik.
Eine bekannte Architektur ist eine zulaessige Engineeringloesung.

## Aufgaben und Abrufe

Die vorab festgelegten P1-P5-Regeln wurden nicht angepasst:

- P1: fruehe Aufnahme, H1 nach dem ersten Angebot.
- P2: spaete Erhaltung, H3 nach zwoelf Angeboten.
- P3: Wiederholung und Teilassoziationskonflikt, H2/H4; AX bleibt erhalten.
- P4: Kapazitaets- und Verdrangungsverhalten, H5/H6.
- P5: aehnliche und ausserhalb liegende Proben, H7.

Je Arm sind 15 positive und drei negative Proben gebunden. Die Quote unten
zaehlt korrekte Abrufe UND korrekte Ablehnungen, nicht nur Treffer.

| Arm | Korrekt / 18 | P1 | P2 | P3 | P4 | P5 | Konkreter Befund |
|---|---:|:---:|:---:|:---:|:---:|:---:|---|
| TSPM1 | 18 | ja | ja | ja | ja | ja | Schnelle Aufnahme plus spaeter PPB-1-Abruf |
| B0, kein Speicher | 3 | nein | nein | nein | nein | nein | Alle 15 positiven Proben verfehlt |
| B1_DIRECT, PPB-1 direkt | 9 | nein | ja | nein | nein | nein | Stabilisiertes AX erhalten; fruehe und neue Zustaende fehlen |
| B1_BUDGET_MATCHED, PPB-1 | 9 | nein | ja | nein | nein | nein | Gleiches Abrufprofil wie B1_DIRECT mit weniger Schreibarbeit |
| B2, adaptive Prototypbank | 17 | ja | nein | ja | ja | ja | Nur spaeter AX-Abruf in H3 verfehlt |
| B3, Nachhall | 8 | ja | nein | nein | nein | ja | Fruehe und nahe Proben moeglich; H3-H6 nicht ausreichend erhalten |
| B4, begrenzter FIFO-Speicher | 18 | ja | ja | ja | ja | ja | Gleiches funktionales Profil wie TSPM1 und R0 |
| R0, unabhaengige Zwei-Ebenen-Kontrolle | 18 | ja | ja | ja | ja | ja | Vollstaendige gebundene R0-Projektion stimmt mit TSPM1 ueberein |

Alle funktionalen Fehler waren ausbleibende positive Abrufe. Es gab keine
falsch positiven Zuordnungen und keine falschen Werte bei einem als erkannt
zurueckgegebenen positiven Abruf. Die normalisierten Zielabweichungen der
erkannten positiven Abrufe betragen auditiv und visuell jeweils 0,0.

Die neun fehlenden Abrufe beider B1-Arme sind H1/1/AX, H2/1/AX,
H4/6/AY, H4/6/BX, H5/8/P4, H6/7/D1, H6/7/D3, H6/7/D8 und H7/4/NEAR.
B2 verfehlt ausschliesslich H3/12/AX. B3 verfehlt H3/12/AX sowie alle
positiven Proben in H4, H5 und H6. B0 verfehlt alle positiven Proben.

## Was die zweite Ebene leistet

Die gespeicherten nativen Findings zeigen bei TSPM1:

- H1/1/AX und H2/1/AX stammen aus `FAST_ASSOCIATIVE_CONTEXT`.
- H2/4/AX wechselt nach der Bildung zu `SLOW_PPB1_CONTEXT`.
- H3/12/AX wird ebenfalls aus beiden stabilisierten PPB-1-Baenken abgerufen.
- H4-H6: AX stammt aus PPB-1; AY/BX, P4 beziehungsweise D1/D3/D8 stammen
  aus dem schnellen Speicher. Beide Ebenen ergaenzen sich in diesen Aufgaben.
- H7: AX kommt aus PPB-1, NEAR aus dem schnellen Speicher. PARTIAL_OUT,
  OUTSIDE und FAR liefern keinen vollstaendigen Kontext.

Damit ist die zweite Ebene im tatsaechlichen TSPM-1-Ablauf wirksam. Gegenueber
B2 hilft sie beim spaeten H3-Abruf; gegenueber PPB-1 allein ergaenzt die
schnelle Ebene fruehe und noch nicht stabilisierte Zustaende. Daraus folgt
aber keine Notwendigkeit zweier Ebenen: B4 loest alle gebundenen Aufgaben ohne
Konsolidierung. Die vorliegenden Geschichten verlangen keinen Vorteil,
den ausschliesslich die zweite Ebene liefern kann.

## Ressourcen und Kosten

Alle Arme bleiben unter demselben Ressourcenmaximum von 269 logischen
Woertern. Bildungsangebote und Proben sind gleich; B1_BUDGET_MATCHED nimmt
gemaess unveraenderter Regel 19 statt 42 Angebote in PPB-1 an. B1_DIRECT
verarbeitet alle 42. Diese unterschiedlichen Annahmeregeln sind keine
nachtraegliche Budgetanpassung.

| Arm | Logische Woerter | Geschriebene Woerter gesamt | Funktionale Distanzterme | Validierungsterme | PPB-1-Bildungsaufrufe |
|---|---:|---:|---:|---:|---:|
| TSPM1 | 269 | 2089 | 3224 | 2886 | 38 |
| B0 | 0 | 0 | 0 | 0 | 0 |
| B1_DIRECT | 176 | 1512 | 1920 | 0 | 84 |
| B1_BUDGET_MATCHED | 176 | 684 | 754 | 0 | 38 |
| B2 | 264 | 1289 | 3120 | 0 | 0 |
| B3 | 29 | 1218 | 468 | 0 | 0 |
| B4 | 255 | 1218 | 2522 | 0 | 0 |
| R0 | 269 | 2089 | 3224 | 0 | 38 |

Die Distanzspalten geben die gebundenen logischen Zaehler aus den
Einzelbelegen wieder, nicht saemtliche Python-Instruktionen oder reale
CPU-Kosten. Bei TSPM1 werden 2886 zusaetzliche Validierungs-Distanzterme
mitgezaehlt. R0-Exaktheit bezeichnet die vertragliche Zustands-/Abrufprojektion,
nicht Identitaet von Validierungsaufwand oder Prozesslaufzeit.

Beobachtete Maxima ueber alle Arme: 70 geschriebene Woerter je Bildungsangebot
(Grenze 293), 182 Distanzterme je Bildung und 234 je Probe (Grenze jeweils
234). Funktionale Schreibarbeit jeder Probe: null. Die separate fachliche
Auswertung der zurueckgegebenen AV-Werte ist kein Zustandsupdate.

Fuer das identische funktionale Profil bevorzugt die vorab gebundene
Engineeringregel B4: **871 weniger geschriebene Woerter als TSPM1/R0
(41,7 Prozent), 14 weniger logische Speicherwoerter und eine statt zwei
Ebenen**. Innerhalb des identischen B1-Profils ist B1_BUDGET_MATCHED sparsamer
als B1_DIRECT. Ein billigerer Arm mit schlechterer Abrufqualitaet wird
dadurch nicht als gleichwertig eingestuft.

Der Runner protokolliert 1919,682 Sekunden; die aeussere Prozessbeobachtung
umfasst 19:39:40,304 bis 20:11:47,537 UTC, also etwa 32 Minuten einschliesslich
Start und Abschluss. Es liegen keine getrennten Laufzeitmessungen je Arm vor.
Der reale Prozessspeicher wurde nicht gemessen (`NOT_MEASURED`); 269 logische
Woerter sind ausdruecklich keine RAM-Angabe. Aus diesem Lauf folgt keine
allgemeine Geschwindigkeitsrangfolge.

## Aufzeichnung und nachtraegliche Pruefung

Der vorab dokumentierte [Ausfuehrungsstand](../functional-20260828-01.prestart.md)
und die [Einmalfreigabe](../functional-20260828-01.authorization.txt) binden
den neuen privaten Einstieg. Im Manifest sind 23 Quellen mit Originalbytes,
Runtimeinformationen, Registry und Konfiguration gespeichert. Der Arbeitsstand
war nicht eingecheckt; HEAD allein bezeichnet daher nicht den ausgefuehrten Code.

Nach Prozessende wurde nur aufgezeichnetes Material gelesen und geprueft:

- `verify_result` bestaetigt `COMPLETE` ohne Modell- oder Zustandsaufrufe.
- Zusaetzlicher Standardbibliothek-Abgleich bestaetigt alle 116 versiegelten
  JSON-Datensaetze, 56 verschiedene Zellen/Owner, 336 Ereignisse und 144 Findings.
- Alle 23 archivierten Quellbytes und SHA-256-Werte stimmen mit den nach dem
  Lauf vorliegenden Quellen ueberein, vor der anschliessenden Gatesperrung.
- Prozessbeleg, Standardausgabe, leere Fehlerausgabe und Autorisierung stimmen
  in ihren Dateihashes ueberein. Exit-Code 0, keine Wiederholung.
- `errors.json` enthaelt keine Fehler; kein Failure-Beleg und keine
  temporaeren Ergebnisdateien sind vorhanden.

Die vollstaendigen Ereignisse, Vor-/Nachzustaende, Receipts, abgerufenen
AV-Werte und Kosten bleiben in `cell-001.json` bis `cell-056.json` erhalten.
Die Auswertung ersetzt diese Einzelbelege nicht.

| Beleg | SHA-256 der unveraenderten Dateibytes |
|---|---|
| [manifest.json](manifest.json) | `57649bda9b81530d58c831675ad0bcd804e41411552e7a9b62ce2cd7159f0a90` |
| [result.json](result.json) | `e03fa5d9d5a17a95c56dd3c0b07c287f7528359df1df928c4fcb4652d991c033` |
| [terminal.json](terminal.json) | `06810a0097aa47a058df7303d063ef45081887e4ade842fb2101027fcf0a360d` |

Der kanonische Ergebnis-Envelope-Digest ist
`4aa72093dec13cbca01e0199551c0d0eeae17cc3caad8b72cb1b5825c7d1d8ee`.
Er ist nicht mit dem rohen Dateihash zu verwechseln.
Der [aeussere Prozessbeleg](../functional-20260828-01.process.json)
enthaelt Start, Ende, Exit-Code und Ausgabehashes.
Die eng begrenzte Git-Regel `reports/tspm1_functional/** -text` erhaelt die
Originalbytes dieses Belegordners beim Commit und Checkout. Sie wurde erst
zur Ablage nach dem Lauf ergaenzt und aendert keine Ausfuehrungsregel.

## Ausfuehrungsgrenze nach Abschluss

Die einmalige Freigabe ist verbraucht. Nach erfolgreicher Quellenpruefung
wurde ausschliesslich `_FUNCTIONAL_STUDY_RELEASE_ENABLED` auf `False`
zurueckgesetzt. Die archivierten Ausfuehrungsbytes bleiben unveraendert;
die aktuelle Runnerdatei unterscheidet sich deshalb bewusst um diese Sperre.
Zusaetzlich bleiben Versuchspfad und Autorisierungsreservierung bestehen.
Ein statischer AST-Abgleich bestaetigt, dass nur diese Gatesperre von den
archivierten Runnerbytes abweicht; die uebrigen 22 Quellen sind unveraendert.
SHA-256 des gesperrten Runners:
`e545f24616b4769bd978fc7a6890f3960bef142ad4b7d5637c8c9ec66cc22258`.

Der alte Einstieg, S2-FC und der geschlossene Plattformpfad bleiben gesperrt.
Keine erneute Test- oder Vergleichsausfuehrung, keine Parameteranpassung,
kein Feldlauf und keine Feldintegration wurden vorgenommen. TSPM-1-Grundkern,
PPB-1, Baselines, Fixtures, API und Snapshot bleiben unveraendert.

## Engineeringempfehlung und offene Frage

Fuer die **hier gepruefte begrenzte Aufgabe** ist B4 die einfachste ausreichende
Loesung. Empfehlung: B4 als bevorzugte Arbeitsreferenz behalten und TSPM-1
einschliesslich PPB-1 als vorhandene Zwei-Zeitskalen-Referenz erhalten. Es wird
in diesem Auftrag nichts ersetzt, geloescht oder integriert. Der Vergleich
rechtfertigt keine weitere Komplexitaet allein fuer dieselben H1-H7-Aufgaben.

Dies ist weder ein allgemeiner Nachweis der Gleichwertigkeit fuer beliebige
Sequenzen noch ein Scheitern der technischen Memory-Entwicklung. Lange
Geschichten, andere Verteilungen und reale Wahrnehmungsqualitaet wurden nicht
geprueft. Die 26 AV-Traegerwerte bestehen in diesen Fixtures aus nur zwei
unabhaengig variierenden Werten, wiederholt in acht auditiven und 18 visuellen
Positionen. Treffer hier belegen deshalb keine reichhaltige raeumliche,
zeitliche oder multimodale Repraesentation.

Naechste getrennte Entscheidung: Welche Merkmalsabstufungen, raeumlichen
Beziehungen oder zeitlichen Uebergaenge soll der Wahrnehmungsspeicher erhalten?
Daraus sollte genau eine konkrete Repraesentationsaufgabe entstehen, bevor
weitere Speichermechanik oder ein neuer Vergleich implementiert wird.
Diese Untersuchung und ein weiterer Lauf sind durch diesen Abschluss nicht
freigegeben. Keine weitere allgemeine Vertragsaudit-Kaskade ist erforderlich.
