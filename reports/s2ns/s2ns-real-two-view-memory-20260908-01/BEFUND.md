# S2-NS: realer Zwei-Sichten-Memoryvergleich

## Abschluss und Einmalbindung

Lauf-ID: `s2ns-real-two-view-memory-20260908-01`, Datum: 2026-09-08.
Technik: `RECORDING_COMPLETE`, unabhaengig verifiziert; danach getrennt
`FUNCTION_EVALUATED`. Der autorisierte Aufruf endete mit Exit-Code `0`.
Genau ein Hauptaufruf, eine read-only Gesamtverifikation und eine Auswertung;
kein Retry, kein zusaetzlicher Test- oder Rezeptorvorlauf.

Die Konjunktion ist technisch korrekt, liefert aber keinen belegten sicheren
Zusatznutzen gegen beide Einzelsichten: Gegen LOWER ist sie in allen 15 Faellen
funktionsgleich. Gegen UPPER entstehen sechs richtige Abrufe und fuenf
verhinderte Fehlzulassungen, zugleich aber zwei neue Fehlzulassungen.
Das ist ein gueltiger gemischter Funktionsbefund, kein technischer Abbruch.

Vorab wurden die unveraenderte Versiegelung, die 24/24-Logikqualifikation und
die 20/20-Anschlussqualifikation samt Quellenbindungen geprueft. Die neue
Aufrufbindung steht in `../run_real_once.py`; Vorregistrierung und
Ausfuehrungsabschluss liegen als gleichnamige externe JSON-Belege neben dem
Laufverzeichnis. Die qualifizierten Produktdateien wurden nicht veraendert.

## Umfang und technische Grenzen

| Groesse | Tatsaechlich |
| --- | ---: |
| Frische Geschichten | 3 |
| Ereignisse / Formationen / Hinweise | 31 / 16 / 15 |
| Direkte Audioanalysen / NJ-Projektionen / visuelle Analysen | 31 / 31 / 16 |
| Sichtscans inklusive Direktbaseline | 60 |
| Entscheidungen inklusive Direktbaseline | 90 |
| Vollstaendige Slotzeilen | 1.200 |
| Banddifferenzen im Hauptvergleich | 9.120 |
| Kandidatengleichheitsvergleiche | 1.248 |
| Formations-L1-Terme | 56.832 |
| Atomarer Gesamtbeleg | 1.226.773 Byte |
| Gesamtbeleggrenze | 4.194.304 Byte |

Die unabhaengige Verifikation ist separat budgetiert: 30 Sichtscans,
600 Slotzeilen, 4.560 Banddifferenzen, 624 Gleichheitsvergleiche,
9.408 Fast-Rangterme, 672 PPB-Auswahlterme, 16 Formationspruefungen,
10.752 Updatekomponenten, 31 Quellenbindungen, 1.488 Halbierungsterme,
17 Zustandsdekodierungen und 48 Zustandsvalidierungspassagen. Die einmalige
direkte Nachrechnung prueft beide gespeicherten Implementierungen.
Alle gebundenen Teilbudgets sind eingehalten.

Baselinegleichheit und Read-only-Bindungen sind bestaetigt. Alle 15 Hinweise
lassen ihren jeweiligen Memoryzustand unveraendert. Formationen schreiben
Memory; der gesamte Lauf war deshalb nicht read-only.
Keine Feld-, Runtime- oder Hypothesenanwendung fand statt.

Der historisch versiegelte `endpoint_snapshot_index` bleibt erhalten. Die
versionierte Anschlussbindung verwendet bereits beim Rezeptoraufruf
`nj_snapshot_index = window_start_sample // 480`, nach exakter
Ganzzahligkeits-, Nichtnegativitaets- und Teilbarkeitspruefung. Fenster,
Quellenbytes und Reihenfolge bleiben unveraendert; keine nachtraegliche
Umetikettierung eines Rohzustands.

## Alle 15 Entscheidungen

`A+` / `B+`: richtiger oeffentlicher Abruf aus A_RECENT / B_STABLE.
`A!` / `B!`: Fehlzulassung aus dem jeweiligen Bereich.
`IA`: ABSTAIN_INTERNAL_AMBIGUITY; `NA`: ABSTAIN_NO_APPLICABLE_CONTEXT.
Alle Angaben gelten identisch fuer die jeweilige Direktbaseline.

| Geschichte | Ereignis | Hinweis | LOWER | UPPER | Konjunktion |
| --- | --- | --- | --- | --- | --- |
| h01 | e03 | a03, exakt | A+ | IA | A+ |
| h01 | e04 | a04, Pegelvariante | A+ | IA | A+ |
| h01 | e05 | a05, Frequenzvariante | A+ | IA | A+ |
| h01 | e06 | a06, Mischkontrolle | A! | IA | A! |
| h01 | e07 | a07, unabhaengige Kontrolle | NA | IA | NA |
| h02 | e09 | a03, Ziel fehlt | NA | A! | NA |
| h02 | e10 | a04, Ziel fehlt | NA | A! | NA |
| h02 | e11 | a05, Ziel fehlt | NA | A! | NA |
| h02 | e12 | a06, Mischkontrolle | NA | A! | NA |
| h02 | e13 | a07, unabhaengige Kontrolle | NA | A! | NA |
| h03 | e27 | a03, exakt | B+ | IA | B+ |
| h03 | e28 | a04, Pegelvariante | B+ | IA | B+ |
| h03 | e29 | a05, Frequenzvariante | B+ | IA | B+ |
| h03 | e30 | a06, Mischkontrolle | B! | IA | B! |
| h03 | e31 | a07, unabhaengige Kontrolle | NA | IA | NA |

LOWER und Konjunktion: 6/6 richtige Abrufe bei vorhandenem bekanntem Ziel,
darunter drei A- und drei B-Abrufe; 2/9 Fehlzulassungen in Faellen mit
vorgebundener Enthaltung, 7/9 korrekte Enthaltungen. Insgesamt 2/15
Fehlzulassungen und 7/15 Enthaltungen.

UPPER: 0/6 richtige bekannte Abrufe; 5/9 Fehlzulassungen in den
Enthaltungskontrollen, 4/9 korrekte Enthaltungen. Insgesamt 5/15
Fehlzulassungen und 10/15 interne Mehrdeutigkeiten. Sechs davon betreffen
vorhandene bekannte Ziele, nicht korrekt erkannte Unbekanntheit.

## Erhaltung getrennt von Beziehung und Gewinn

N bezeichnet die auswertbare Fall- beziehungsweise Zielbeziehungsmenge;
D die zuvor richtigen Abrufe beziehungsweise anwendbaren Zielbeziehungen;
R erhaltene, L verlorene Elemente, stets `D = R + L`.
Beziehungszaehlung ist slotbezogen, oeffentliche Erhaltung fallbezogen.
Die drei bekannten Hinweise ohne Zielbildung in h02 gehoeren zu den neun
bekannten Cuefaellen, liefern aber keinen positiven Erhaltungsnenner.

| Oeffentlicher Vergleich | N/D/R/L | Neue richtige Abrufe |
| --- | --- | ---: |
| Konjunktion gegen LOWER, bekannte Hinweise insgesamt | 9/6/6/0 | 0 |
| davon vorhandenes A-Ziel | 3/3/3/0 | 0 |
| davon vorhandenes B-Ziel | 3/3/3/0 | 0 |
| davon Exaktkontrollen mit Ziel | 2/2/2/0 | 0 |
| davon tatsaechlich variierte Hinweise mit Ziel | 4/4/4/0 | 0 |
| Konjunktion gegen UPPER, bekannte Hinweise insgesamt | 9/0/0/0 | 6 |
| davon vorhandenes A-Ziel | 3/0/0/0 | 3 |
| davon vorhandenes B-Ziel | 3/0/0/0 | 3 |
| davon Exaktkontrollen mit Ziel | 2/0/0/0 | 2 |
| davon tatsaechlich variierte Hinweise mit Ziel | 4/0/0/0 | 4 |

Gegen UPPER bedeutet jedes oeffentliche `D=0` ausdruecklich
**Erhaltung nicht geprueft**, nicht verlustfreie Verbesserung.
Pegel und Frequenz liefern jeweils zwei reale Variantenfaelle, je einen
A- und B-Fall. Gegen LOWER jeweils `2/2/2/0`; gegen UPPER jeweils
`2/0/0/0` mit zwei Gewinnen.

Die Zielbeziehungserhaltung betraegt gegen JEDEN Einzelarm `9/9/9/0`:
A `6/6/6/0` (je ein B4- und Fast-Ziel pro Hinweis), B `3/3/3/0`.
Exaktbeziehungen: `3/3/3/0`; Pegel: `3/3/3/0`; Frequenz: `3/3/3/0`.
Keine bekannte Zielbeziehung wurde ausgeschlossen. Diese Erhaltung
anwendbarer Slots ersetzt nicht die Pruefung richtiger Eindeutigkeit.

| Wirkung gegen den Einzelarm | LOWER | UPPER |
| --- | ---: | ---: |
| Neue richtige oeffentliche Abrufe | 0 | 6 |
| Verlorene richtige oeffentliche Abrufe | 0 | 0, D=0 |
| Verlorene bekannte Zielbeziehungen | 0 | 0 |
| Verhinderte Fehlzulassungen | 0 | 5 |
| Neue Fehlzulassungen | 0 | 2 |

Die zwei neuen Fehlzulassungen gegen UPPER sind einzeln `e06` (A) und
`e30` (B). Beide verwenden dieselbe Mischquelle `ns-a06`, sind also keine
zwei unabhaengigen Kontrollquellen. Gegen LOWER bleiben diese Fehler
unveraendert. Die fuenf verhinderten UPPER-Fehlzulassungen sind `e09` bis
`e13` in h02. Keine Verrechnung von Gewinnen und Fehlern.

Rezeptorvariation beruht auf originalen quellengebundenen Formationseingaengen
auf den jeweiligen Originalindizes. `e03/e27` sind in beiden Sichten exakt;
`e04/e05/e28/e29` sind tatsaechlich variiert. Bei `e27` besteht dennoch eine
Cue-/Kandidatenabweichung durch PPB-Rundung: Sie zaehlt nicht als Variation.
Bei fehlender Zielbildung in h02 beziehungsweise fehlender eindeutiger
Sollherkunft der Kontrollen bleibt die entsprechende Referenz `null`.

## Tatsaechliche Bildung und Herkunft

Alle drei Geschichten starten frisch. h01 bildet Ziel `ns-a01` und
Konkurrent `ns-a02` in getrennten B4-/Fast-Slots; Fast-Support jeweils 1,
keine Slow-Prototypen. h02 bildet ausschliesslich `ns-a02` in B4/Fast,
keine Slow-Prototypen. h03 bildet viermal das Ziel, dann neun Druckformationen.

| Ereignisse | Fast / PPB-Verlauf |
| --- | --- |
| e01, e02, e08, e14 | Kein Fast-Match; beide PPB-Banken NO_UPDATE |
| e15 | Fast-Match; beide PPB-Banken CREATED, Slot 000, Support 1 |
| e16 | Fast-Match; beide PPB-Banken MATCHED, Support 2 |
| e17 | Fast-Match; beide PPB-Banken MATCHED, Support 3 |
| e18 bis e26 | Je neuer Fast-Inhalt; beide PPB-Banken NO_UPDATE |

h03 endet mit neun B4- und drei Fast-Slots ausschliesslich aus dem
Druckaudio `ns-a02`; das Ziel ist vollstaendig aus A verdraengt. Die drei
Fast-Slots haben Support 1, letzte Auswahlformationen 13, 11 und 12.
Auditory-Slow-Slot 000 besitzt Support 3 und reine Herkunft `ns-a01`;
Visual-Slow-Slot 000 besitzt Support 3 und reine Herkunft `ns-v01`.
Die uebrigen Slow-Slots sind frei. Keine Druckverdichtung oder Slow-Vermischung.

Generationen und ihre Erhaltung/Ersetzung sind aus den tatsaechlichen
Formationstransaktionen gebunden, nicht als freie Slotangaben eingesetzt.
Die vollstaendigen Inventare, PPB-Transitionen, Formationseingaenge und
Generationsbelege stehen im Gesamtbeleg und seiner Verifikation.

## Sichtbefunde und offene Deckung

Im gespeicherten Scanindex sind 0..8 B4, 9..11 Fast und 12..19 Auditory-Slow.

| Hinweise | LOWER-Treffermenge | UPPER-Treffermenge |
| --- | --- | --- |
| e03 bis e06 | {0,9} | {0,1,9,10} |
| e07 | leer | {0,1,9,10} |
| e09 bis e13 | leer | {0,9} |
| e27 bis e30 | {12} | {0..12} |
| e31 | leer | {0..12} |

LOWER ist in allen 15 Faellen Teilmenge von UPPER. Die Konjunktion behaelt
deshalb exakt die LOWER-Treffermenge und Entscheidung. Es gibt 15/15
einseitige UPPER-Zusatztreffermengen, aber 0/15 Faelle mit zwei nichtleeren,
disjunkten Treffermengen und keinen Fall mit Eindeutigkeit erst nach zwei
einzeln mehrdeutigen Sichten. Die reale Deckung solcher widerspruechlicher
Teilbefunde bleibt offen. Insbesondere erzeugt die Mischquelle a06 keine
gegenseitig ausschliessenden Sichttreffer.

Bei a06 trifft der reine Zielslot in beiden Sichten, obwohl die getrennte
Evaluationswurzel keine eindeutige Zielzuordnung erlaubt. Seine reine
Speicherherkunft macht die Zulassung nicht richtig. Gegen UPPER entfernt
die Konjunktion die schuetzende Mehrdeutigkeit; eine strengere Anwendbarkeit
garantiert deshalb keine kleinere Menge falscher oeffentlicher Zulassungen.

## Aussagegrenze und Bindungsbelege

Beobachtet sind korrekte technische Komposition, reale Stabilisierung und
die oben getrennten Gewinne und Fehler. Ein sicherer Zusatznutzen gegen
beide Einzelsichten ist nicht bestaetigt: Gegen LOWER fehlt der Zusatznutzen;
gegen UPPER verletzt die neue Fehlzulassung die vorgebundene Nutzenbedingung.
Das ist weder ein allgemeiner Gegenbeweis zur Zwei-Sichten-Evidenz noch eine
Begruendung zur Integration oder Quellenoptimierung.

Alle 48 Baender liegen zusammen tatsaechlich vor. Dieser Versuch prueft
Zulassung, nicht Vervollstaendigung fehlender Wahrnehmung, Klangidentitaet
oder Sequenzgedaechtnis. Die bekannte Halbprofil-Subnormalgrenze bleibt
bestehen; eine universelle historische Bedeutungsgleichheit wird nicht
behauptet. Es gab keine nachtraegliche Quellen- oder Maskenwahl.

Die Offline-Pruefung berechnet gespeicherte Roh-/Halbwertbeziehungen,
Formationsrelationen und Scans direkt nach. Sie regeneriert keine PCM-Bytes,
fuehrt keine Rezeptoren/NJ oder Memorytransaktionen erneut aus. Die
Rezeptorherkunft und native interne Receipterzeugung bleiben an die
aufgezeichneten Quellen-, Code- und Digestbindungen gebunden; die Pruefung
ist keine unabhaengige Neumessung der Quellen.

| Datei | SHA-256 | Byte |
| --- | --- | ---: |
| recording.json | 54db28bc86e247326cb55828ddab1af2a910c9f62c36b908df69396cc98d6aa5 | 1226773 |
| verification.json | a9c31d711a73b5588694f8a932b276c526fc7808ffa2f2cd038cf264e0ce72a4 | 164085 |
| evaluation.json | 709c9265660d350e1f3cdab3af3f9798e428a9ab47e2afdd397acf721b70e4e3 | 40348 |

Recorddigest: `c4a4505e35715f808820764759460f9ba0b57212181efb6f4553c4724edd6f8e`.
Verifikationsdigest: `e0748fec43570aa02521b8a4c112d924c16a7604c3b4b3717acd9ed97531622b`.
Auswertungsdigest: `5e2cfefaa6a9f019b13ef2272d46c8c84aa9c26128db98d43afd5b6ab7fa7c46`.

Alle gebundenen Code- und historischen Quelldateihashes sind vor/nach dem
Lauf identisch. Main-, Logik-, Quellen- und Profilgate sind abschliessend
`False`. Versiegelung, historische Belege, fremde Aenderungen und Bootstrap
bleiben unberuehrt; versioniert werden ausschliesslich die neuen Laufartefakte.

STOPP: Der freigegebene Einmallauf ist beendet; keine Wiederholung oder
nachtraegliche Anpassung.

WEITER: Am besten geht es jetzt mit der Analystenbewertung dieses gemischten
Befunds weiter, insbesondere der fehlenden Zusatzwirkung gegen LOWER und
der neuen Fehlzulassung gegen UPPER, ohne bereits eine neue Abrufregel oder
einen weiteren Korpusversuch abzuleiten.
