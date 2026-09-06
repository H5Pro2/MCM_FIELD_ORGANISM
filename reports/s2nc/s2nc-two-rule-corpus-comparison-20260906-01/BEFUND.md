# S2-NC: Einmaliger Zwei-Regel-Korpusvergleich

Lauf-ID: `s2nc-two-rule-corpus-comparison-20260906-01`.

## Abschluss

- Genau ein Hauptaufruf: `python -m reports.s2nc.compare_corpus_once`.
- Exit-Code `0`; kein Retry und keine Parameterkorrektur.
- Vollstaendige Aufzeichnung: `RECORDING_COMPLETE`.
- Genau eine anschliessende unabhaengige read-only Verifikation:
  `TECHNICALLY_VALID`, 96 Fallresultate, keine erneute Distanzberechnung.
- Erst danach separate fachliche Bewertung: `IMPROVEMENT_CONFIRMED`.
- Vorhersage fuer `MEAN_L1_24`: `FALSIFIED` (9 fehlende bekannte Treffer).
- Vorhersage fuer `ALL_BANDS_24`: `CONFIRMED` (48/48 korrekte Fallentscheidungen).

Die Auswertung verwendet ausschliesslich die 23 vorhandenen versiegelten
Rezeptorzustaende. Keine Rezeptorwiederholung, Quellenregeneration, Memory-,
Kontext-, Feld- oder Runtimeintegration. Beide Regeln und die unabhaengige
Entscheidungstabellen-Baseline blieben unveraendert. Der archivierte
Einmalaufrufer fuehrt diese vorhandenen Funktionen zusammen; er ist keine
neue Recorder- oder Runnerplattform.

## Ergebnis mit Nennern

| Messung | MEAN_L1_24 | ALL_BANDS_24 |
| --- | ---: | ---: |
| Korrekt eindeutige bekannte Treffer | 0/9 | 9/9 |
| Fehlende bekannte Treffer | 9/9 | 0/9 |
| Fehlzulassungen ueber alle Faelle | 0/48 | 0/48 |
| Korrekte Enthaltungen bei erwarteter Enthaltung | 39/39 | 39/39 |
| Interne A-Mehrdeutigkeit | 48/48 | 18/48 |
| Keine anwendbaren A-Kandidaten | 0/48 | 21/48 |
| Interner A-Konflikt | 0/48 | 0/48 |
| Gueltige vollstaendige A-Abwesenheit | 0/48 | 0/48 |
| Insgesamt korrekte Fallentscheidungen | 39/48 | 48/48 |
| Passende belegte Pruefpositionen | 528/528 | 90/528 |

Die neun bekannten Treffer des strengeren Arms sind `c001..c003`,
`c017..c019` und `c033..c035`. Jeweils genau ein B4- und ein Fast-Treffer
verweisen auf dieselbe Referenz `s001`, `s002` beziehungsweise `s003`.
Beide internen Herkunftspositionen bleiben aufgezeichnet; keine Deduplication.

Die 18 verbleibenden Mehrdeutigkeiten des strengeren Arms verteilen sich auf
sechs Faelle des zweiten unbekannten Hinweises, sechs stille und sechs
leise Hinweise. Die 21 Nichtanwendbarkeiten betreffen neun bekannte Hinweise
nach Referenzentfernung, sechs Faelle des ersten unbekannten Hinweises und
sechs Mischhinweise. Alle 39 sind gemaess unveraendertem Evaluationsplan
korrekte Enthaltungen. Sie sind nicht alle Belege fuer leere Treffermengen.

## Getrennte Aufgabenklassen

| Aufgabe | Nenner | Korrekt MEAN_L1_24 | Korrekt ALL_BANDS_24 |
| --- | ---: | ---: | ---: |
| Bekannte exakte Hinweise, Referenz vorhanden | 3 | 0 | 3 |
| Bekannte Pegelvarianten, Referenz vorhanden | 3 | 0 | 3 |
| Bekannte Frequenzvarianten, Referenz vorhanden | 3 | 0 | 3 |
| Bekannte Hinweise, Referenz entfernt | 9 | 9 | 9 |
| Unbekannte Hinweise | 12 | 12 | 12 |
| Informationsarme Stille | 6 | 6 | 6 |
| Informationsarme leise Hinweise | 6 | 6 | 6 |
| Quellmischung | 6 | 6 | 6 |

Die drei versiegelten KNOWN-Kategorien enthalten jeweils sechs Faelle:
drei mit und drei ohne Referenz. Ihre aggregierten Werte betragen deshalb
je `3/6` gegen `6/6`; die obige Aufteilung vermeidet eine Vermischung von
Treffer- und Enthaltungsaufgaben.

Gemaess gebundener Vergleichsentscheidung:

- verbesserte Faelle: `9/48`;
- unveraenderte fachliche Korrektheit: `39/48`;
- neue Fehlzulassungen: `0/48`;
- verlorene zuvor korrekte bekannte Treffer: `0`, Ausgangsnenner `0`.

Die letzte Bedingung ist auf diesem Korpus leer erfuellt: Der Mittelwertarm
hatte keinen korrekt eindeutigen bekannten Treffer, der haette verloren
gehen koennen. Ein allgemeiner Erhalt bereits funktionierender
Mittelwerttreffer ist damit nicht nachgewiesen.

## Interpretation und Nichtnachweise

Der positive Befund entsteht nicht allein aus weniger passenden Positionen.
Neun zuvor mehrdeutige bekannte Faelle werden korrekt eindeutig, ohne neue
Fehlzulassung oder Verschlechterung der 39 Enthaltungsaufgaben. Das erfuellt
die vorgebundene Alternative einer Verbesserung bekannter Mehrdeutigkeiten.

Eine Verringerung tatsaechlicher Fehlzulassungen wurde nicht gemessen:
Beide Arme lagen bereits bei null. Unbekannte und informationsarme Faelle
koennen weiterhin mehrere Kandidaten treffen; Sicherheit entsteht dort
durch die unveraenderte Enthaltung, nicht durch eine behauptete Erkennung
von Unbekanntheit oder Bedeutung.

Die unabhaengige direkte Entscheidungstabellen-Baseline reproduziert
`96/96` A-Entscheidungen. Der Effekt ist eine transparente Folge der strengeren
Bandregel auf festen Referenzpanels. Keine neue Memorymechanik, keine
automatische B-Bevorzugung, Semantik oder besondere MCM-Physik.
Die Panels sind keine in diesem Lauf real gebildeten Memoryzustaende.
Eine Produktionsintegration oder allgemeine akustische Identitaet ist nicht
qualifiziert. Historische S2-MT-/S2-NB-Befunde werden nicht umgedeutet.

## Arbeits- und Beleggrenzen

| Groesse | Aufgezeichnet | Grenze |
| --- | ---: | ---: |
| Faelle je Regel | 48 | 48 |
| Positionsbesuche insgesamt, einschliesslich leerer Slots | 1.152 | 1.152 |
| Beziehungszeilen | 1.056 | 1.056 |
| Absolute Banddifferenzen | 25.344 | 25.344 |
| A-Entscheidungen / Direktbaselineentscheidungen | 96 / 96 | 96 / 96 |
| Exakte Gleichheitsvergleiche im Vergleich | 432 | 4.608 |
| Exakte Gleichheitsvergleiche der Direktbaseline | 432 | 4.608 |
| Zusaetzliche Gleichheitspruefungen der Verifikation | 432 | im Gesamtbudget |
| Gleichheitsvergleiche einschliesslich Verifikation | 1.296 | 9.216 |
| Aufzeichnung in Bytes | 1.012.236 | 4.194.304 |
| Aufzeichnung + Verifikation + Auswertung in Bytes | 1.036.044 | 4.194.304 |

Alle Scans wurden vollstaendig abgeschlossen. Die Verifikation liest die
gespeicherte Aufzeichnung, prueft Quellen-, Fall-, Digest-, Reihenfolge-,
Status-, Read-only- und Budgetbindungen, Mittelwert-/Maximumreduktionen und
die direkte Entscheidungstabelle. Sie berechnet keine Banddifferenzen erneut
und kennt keine Sollentscheidungen. Die aufgezeichneten Ergebnisse bleiben
dabei unveraendert. Erst nach ihrer erfolgreichen Pruefung wird der
Evaluationsplan an den getrennten Auswerter uebergeben.

## Versionen und Integritaet

Produktstand: Commit `2e9ff8a1dfc27384469391ad6991056bf8528312`.
Der zusaetzliche archivierte Aufrufer ist vor dem Aufruf durch seinen
Dateihash in `run-plan.json` gebunden. Alle 21 gebundenen Vor-/Nachhashes
stimmen ueberein; siehe `completion.json`. Historische Artefakte wurden
nicht geaendert, neu versiegelt oder erneut ausgewertet.

Historischer Vertrag unter Commit `1065db1`:
`1fabeb6a35e8ab6ace4f2f1c8763cfa9c932446ad39c4a3e8f040b5da3cdc6fe`.

Separater Arithmetiknachtrag:
`c3f6952c640c50da7b8e92a1773936a5277f55d2c746d97d5ebf747eaf733084`.

`MEAN_L1_24` verwendet die qualifizierte `statistics.mean`-Arithmetik,
nicht die historische Rechenfolge `sum(...)/24`. Keine bitidentische
Reproduktion des produktiven Abrufs wird behauptet.

Zentrale Belege:

- `recording.json`: vollstaendige Scans, 1.056 Beziehungszeilen mit je 24
  Differenzen, Treffermengen, A-Entscheidungen und Direktbaseline;
- `verification.json`: einmaliger technischer read-only Pruefbeleg;
- `evaluation.json`: alle 48 nachgelagerten Fallbewertungen, Kategorien,
  Verluste, Fehlzulassungen und Vergleichsentscheidung;
- `completion.json`: Abschluss, Dateigroessen, Dateihashes und Nachhashes;
- `run-plan.json`, `invocation.json`, `call-result.json`: vorab gebundener
  Aufruf, Einmalreservierung und unveraenderte Kommandoausgabe.

Aufzeichnungs-SHA-256:
`1d1330bceb46ac0409eab113996911c9ac699101f9184bd90152f5e384bca76d`.

Aufzeichnungsdigest:
`9a48f9f9920baf1cf365fec0c5064d8e63f385ac32f764893666911b37aab4dc`.

Verifikationsdigest:
`64776e5794825d4d6de4f6f6cfa7629e22c11c5994dff35ff1ff3c92ee4a666a`.

Auswertungsdigest:
`338e5294d50fb4118831ee7d13f5eaf8251e7a90b3d6403b32bdd83104b73265`.

## Rueckmeldung an den Analysten

Dieser freigegebene Vergleich ist abgeschlossen. Keine weitere Ausfuehrung
oder Integration ist damit freigegeben.

WEITER: Am besten geht es jetzt mit der Analystenbewertung dieses begrenzten
Selektivitaetsgewinns weiter. Ein moeglicher Folgeauftrag sollte insbesondere
bereits korrekt eindeutige Mittelwerttreffer einschliessen, um deren Erhalt
nicht erneut nur mit Ausgangsnenner null zu pruefen; keine automatische
Produktumstellung und keine nachtraegliche Schwellenanpassung.
