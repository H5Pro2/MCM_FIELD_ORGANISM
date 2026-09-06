# S2-ND: Einmaliger Erhaltungs- und Verlustvergleich

## Abschluss

Lauf-ID: `s2nd-retention-loss-corpus-comparison-20260906-01`.
Genau ein Hauptaufruf, Exit-Code **0**, kein Retry.

```text
C:/Python314/python.exe -m reports.s2nd.compare_corpus_once
```

Ausgefuehrt aus dem workspace-Root auf dem qualifizierten Quellenstand
von Commit `20a7fda`; hinzu kam ausschliesslich der archivierte, einmalige
S2-ND-Aufrufer. Keine Aenderung an den qualifizierten Vergleichsmodulen.

Die Aufzeichnung erreichte `RECORDING_COMPLETE`. Danach erfolgte genau eine
unabhaengige read-only Verifikation: `TECHNICALLY_VALID`, 96 Fallresultate,
null Distanz-Neuberechnungen, unveraenderte Aufzeichnung. Erst danach wurden
Evaluationsplan und nachgelagerter Auswerter verwendet.

- Erhaltungsbefund: `RETENTION_CONFIRMED_ON_OBSERVED_SUBSET`.
- Gemeinsamer Vergleich: `IMPROVEMENT_CONFIRMED`.
- Kein technischer Abbruch und kein Ausschluss unguenstiger Faelle.

## Bindungen und Arbeitsumfang

Verwendet wurden ausschliesslich die 18 bereits versiegelten und
materialisierten Quellen mit 864 gueltigen Rezeptorwerten. Vor dem Vergleich
wurden Plan-, Siegel-, Quellen-, Profil-, Materialisierungs- und vorhandene
Pruefbelegbindungen validiert. Interpreter und qualifizierte Quellhashes
waren gebunden; alle Vor-/Nachhashes blieben gleich.

Die Ausfuehrung uebernahm `compare_case`, interne A-Aufloesung, direkte
Entscheidungstabellen-Baseline und `verify_case` unveraendert. Historische
S2-NC-Korpushelfer wurden nicht auf S2-ND umetikettiert. Beide Regeln nutzten
dieselben Baender `0..23`, dieselben Panels und `<= 0.2`:
`statistics.mean` beziehungsweise `max`. Der Mittelwertarm ist weiterhin
keine Behauptung bitidentischer historischer `sum(...)/24`-Reproduktion.

| Zaehler | Beobachtet |
| --- | ---: |
| Panels | 12 |
| Faelle je Regel | 48 |
| A-Entscheidungen / direkte Baselineentscheidungen | 96 / 96 |
| Uebereinstimmende Direktbaselineentscheidungen | 96/96 |
| Vollstaendige Positionsbesuche | 1.152 |
| Beziehungszeilen | 144 |
| Absolute Banddifferenzen | 3.456 |
| Gleichheitsvergleiche, Vergleich / direkte Baseline / Verifikation | 1.728 / 1.728 / 1.728 |
| Gleichheitsvergleiche insgesamt | 5.184 von maximal 6.912 |
| Rezeptor-, Memory-, Kontext-, Feld- und Runtimeaufrufe | jeweils 0 |

Alle neun B4- und drei Fast-Positionen wurden fuer jeden Fall und Arm
vollstaendig besucht, auch bei leeren Panels. Keine Deduplication oder
Rangfolge. Rohpayloads wurden weder regeneriert noch gespeichert.

## Erhaltung und Verlust

N: vorgebundene referenzhaltige Faelle; D: darunter korrekt eindeutige
Mittelwerttreffer; R: durch ALL_BANDS erhalten; L: verloren. Es gilt in
allen Gruppen `D = R + L`. Gewinne werden nicht mit Verlusten verrechnet.

| Hinweisart, beide Konkurrenzbelegungen | N | D | R | L |
| --- | ---: | ---: | ---: | ---: |
| Exaktkontrollen | 6 | 3 | 3 | 0 |
| Gemeinsame Pegelvariation | 6 | 3 | 3 | 0 |
| Frequenzvariation | 6 | 3 | 3 | 0 |
| Spektrale Umgewichtung | 6 | 3 | 3 | 0 |
| Alle Varianten, ohne Exaktkontrollen | 18 | 9 | 9 | 0 |

Alle neun Variantenquellen erzeugten tatsaechlich nicht bitidentische
48-Werte-Rezeptorausgaben gegenueber ihrer Referenz. Die drei Exaktquellen
blieben bitidentisch. Der nicht bitidentische Varianten-Teilnenner lautet
deshalb ebenfalls **N/D/R/L = 18/9/9/0**. Gute Exaktkontrollen ersetzen hier
keinen leeren Varianten-Nenner. Verlust in Enthaltung: 0/9; Verlust in
falsche Zulassung: 0/9 der bisher richtigen variierten Treffer.

| Belegung | Exakt N/D/R/L | Pegel N/D/R/L | Frequenz N/D/R/L | Spektral N/D/R/L | Alle Varianten N/D/R/L |
| --- | --- | --- | --- | --- | --- |
| Referenzrein, ohne Konkurrent | 3/3/3/0 | 3/3/3/0 | 3/3/3/0 | 3/3/3/0 | 9/9/9/0 |
| Referenz und Konkurrent | 3/0/0/0 | 3/0/0/0 | 3/0/0/0 | 3/0/0/0 | 9/0/0/0 |

**Unter Konkurrenz ist Erhaltung weiterhin nicht geprueft:** D=0 bedeutet
ausdruecklich `ERHALTUNG_NICHT_GEPRUEFT`, nicht einen weiteren Erfolg.
Der Mittelwertarm war dort bereits mehrdeutig. Die zusaetzlichen korrekten
Treffer des ALL_BANDS-Arms sind Gewinne, keine erhaltenen Ausgangstreffer.
Alle 45 Kombinationen aus Subtyp, Konkurrenz und Rezeptorbitvariation,
einschliesslich der leeren Gruppen, stehen in `TABELLEN.md` und
`evaluation.json`.

## Gesamte Treffermengen und Entfernungskontrollen

| Messung | MEAN_L1_24 | ALL_BANDS_24 |
| --- | ---: | ---: |
| Korrekte bekannte Treffer, Referenz vorhanden | 12/24 | 24/24 |
| Verfehlte bekannte Treffer | 12/24 | 0/24 |
| Fehlzulassungen, alle Faelle | 12/48 | 0/48 |
| Interne Mehrdeutigkeiten, alle Faelle | 12/48 | 0/48 |
| Interne Konflikte, alle Faelle | 0/48 | 0/48 |
| Leere Treffermenge, alle Faelle | 12/48 | 24/48 |
| Gueltige Abwesenheit bei leerem Panel | 12/48 | 12/48 |
| Nicht anwendbar bei belegtem Panel | 0/48 | 12/48 |
| Korrekte Enthaltungen, Ziel entfernt | 12/24 | 24/24 |
| Fehlzulassungen, Ziel entfernt | 12/24 | 0/24 |
| Passende belegte Positionen | 72/72 | 48/72 |

Bei vorhandener Referenz und Konkurrent werden 12/12 vorher mehrdeutige
Panelpruefungen korrekt aufgeloest: drei Exakt- und neun Variantenfaelle.
Nach Zielentfernung mit verbliebenem Konkurrenten werden 12/12 falsche
Mittelwertzulassungen zu korrekter Enthaltung. Bei vollstaendig leeren
Panels enthalten sich beide Regeln in 12/12 Faellen.

Somit meldet die gemeinsame Bewertung 24/48 Verbesserungen, null neue
Fehlzulassungen und null verlorene bekannte Treffer. Entscheidend ist nicht
allein die Reduktion passender Positionen von 72 auf 48, sondern die belegte
Kombination aus erhaltenen richtigen Treffern, aufgeloester Mehrdeutigkeit
und vermiedenen Fehlzulassungen.

## Belege

`run-plan.json` bindet Aufruf, Hashes und Grenzen; `invocation.json`
reserviert den Einmallauf. `recording.json` enthaelt alle 96 Resultate,
144 Beziehungszeilen, Treffermengen und direkten Baselineentscheidungen,
ohne Evaluationsrollen. `verification.json` bindet die einmalige lesende
Pruefung; `evaluation.json` die erst danach erfolgte fachliche Bewertung.
`completion.json` bindet Abschluss, Artefaktgroessen und Nachhashes;
`call-result.json` bewahrt die unveraenderte Prozessausgabe.

| Artefakt | Bytes | SHA-256 |
| --- | ---: | --- |
| recording.json | 198.365 | `42478137e99159769da0bc09418e75609ab85a15346c5a07cbd0cebbc8800ce9` |
| verification.json | 698 | `f9330b06faa39a75865a713fcf8ed2bd731b9301d8139eefd4bbef01675f50cd` |
| evaluation.json | 69.764 | `5c54e8d3336d1f077cc0e689e4e872c5b3d6a0d68076bfefa17e6b1acd124cdd` |

Diese drei Kernbelege umfassen 268.827 Bytes. Auch der im Aufrufer
begrenzte gesamte JSON-Belegumfang blieb unter 4.194.304 Bytes.
Recording-Digest: `1420b7ea39a5b98a60b3d72b0559cd7bb5885f36629e860aee28b063e200c038`.
Verifikationsdigest: `c1ca8c071712f836099ca8507488cb6b45af72af6946b68e18c734ce5b694b0c`.
Abschlussdigest: `ae86d8cd3c1f0c141921efc16038f1dba0fe0cd641c32604d038a0626b72e843`.

## Aussagegrenze und Rueckmeldung

Beobachtet ist begrenzte Erhaltung fuer neun nicht bitidentische
Variantenhinweise ohne Konkurrent sowie eine Verbesserung auf diesen festen
Konkurrenz- und Zielentfernungspanels. Das ist erstmals ein nichtleerer
Erhaltungsbefund dieses Zwei-Regel-Vergleichs, nicht nur ein Rueckgang der
Treffermenge. Die direkte generische Vergleichsmechanik erklaert ihn.

Dies sind drei harmonische Referenzquellen mit je drei festgelegten
Varianten und einer Exaktkontrolle. Dieselben Hinweise wurden in vier
Panels wiederverwendet; 48 Panelpruefungen sind keine 48 unabhaengigen
Audioaufnahmen. Zielentfernung ist keine allgemeine Open-Set-Aufgabe und
belegt keine Erkennung natuerlicher Unbekanntheit. Keine allgemeine
Klangidentitaet, Robustheit gegen beliebige Stoerung oder Produktumstellung
ist nachgewiesen. Das Regelpaar wurde nicht in den produktiven Abruf,
Memory, Feld oder Runtime integriert.

S2-NC, saemtliche S2-ND-Vorarbeiten und historische Laeufe bleiben
unveraendert; Bootstrap bleibt ausgeschlossen. Kein Retry, keine
Rezeptorwiederholung, neue Schwelle oder nachtraegliche Auswahl.

WEITER: Am besten geht es jetzt mit der Analystenbewertung des gemeinsamen
S2-NC-/S2-ND-Befunds und einer getrennten Entscheidung ueber einen begrenzten
Transfernachweis weiter; keine automatische Produktumstellung.
