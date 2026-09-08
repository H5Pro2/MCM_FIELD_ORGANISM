# S2-NT: reale diagnostische Vergleichsauswertung

## Technischer Abschluss

Lauf-ID: `s2nt-diagnostic-comparison-20260908-01`.
Genau ein Hauptaufruf, eine unabhaengige read-only Gesamtverifikation und
danach eine getrennte fachliche Auswertung. Exit-Code `0`, kein Retry.

- Gesamtbeleg: `RECORDING_COMPLETE`.
- Verifikation: `S2NT_COMPARISON_VERIFIED`, Direktbaseline bitgleich.
- Fachliche Auswertung: `FUNCTION_EVALUATED`.
- Gesamtbeleg 318.710 Byte bei Grenze 2.097.152 Byte.
- Verifikationsbeleg 894 Byte bei Grenze 262.144 Byte; Auswertung 8.620 Byte.
- Haupt- und Quellgate anschliessend `False`.

Es wurden ausschliesslich die gespeicherten, verifizierten NT-Werte verwendet.
Versiegelung, Qualifikation 18/18, Quellcode, Interpreter/Umgebung, Quellen,
Profile, native Zeiten und Materialisierungsbindungen wurden vor der Rechnung
geprueft. Die qualifizierten Module blieben unveraendert. Der neue Aufrufer
`reports/s2nt/compare_once.py` fuehrt nur die freigegebene Reihenfolge aus.

Keine PCM-Regeneration, Rezeptoranalyse, NJ-Funktionswiederholung, neuen Paare,
Schwellenableitung oder Systemintegration. Historische Belege und Versiegelung,
fremde Aenderungen und Bootstrap bleiben unveraendert.

## Fachliches Ergebnis

**Die vorgebundene gemeinsame L1-Ordnungsseparation ist nicht bestaetigt.**
Dies ist ein gueltiger, fachlich gemischter Vergleich mit negativem primaerem
Trennbefund, kein technischer Abbruch.

| Pruefbereich | Referenz a01 | Referenz a02 | Gesamt strikt bestanden | Umgekehrt | Gleichstand |
| --- | --- | --- | --- | --- | --- |
| Primaer: Varianten vor Addition/Ersetzung | 1/4 | 1/4 | 2/8 | 6/8 | 0/8 |
| Varianten naeher an eigener Referenz | 2/2 | 2/2 | 4/4 | 0/4 | 0/4 |
| Varianten vor unabhaengigen/fremden Kontrollen | 6/6 | 6/6 | 12/12 | 0/12 | 0/12 |

Die insgesamt 18 bestandenen von 24 Bedingungen kompensieren die sechs
primaeren Gegenbefunde nicht. Beide Referenzen verfehlen ihr primaeres
Vierfachkriterium. `complete_strict_order=False`,
`actual_variant_coverage=True`, `bounded_separation_confirmed=False`.

### Belastungsarten und Varianten getrennt

| Primaere Gegenueberstellung | a01 | a02 | Gesamt |
| --- | --- | --- | --- |
| Pegelvariante vor Addition | 0/1 | 0/1 | 0/2 |
| Frequenzvariante vor Addition | 0/1 | 0/1 | 0/2 |
| Pegelvariante vor Ersetzung | 1/1 | 1/1 | 2/2 |
| Frequenzvariante vor Ersetzung | 0/1 | 0/1 | 0/2 |

Additionsbedingungen bestehen somit 0/4, Ersetzungsbedingungen 2/4.
Bei beiden Referenzen liegt die Addition naeher als jede zulaessige Variante.
Die Ersetzung liegt weiter entfernt als die Pegelvariante, aber naeher als
die Frequenzvariante. Es gibt keine Gleichstaende, die nur konservativ als
Nichtbestehen gezaehlt wuerden: Die sechs verletzten Bedingungen sind invers.

Bei den getrennten Kontrollen bestehen Pegel und Frequenz jeweils 2/2
Eigenreferenzbedingungen und 6/6 Abstandskontrollen. Davon entfallen insgesamt
8/8 auf die unabhaengigen Quellen a13/a14 und 4/4 auf die jeweils andere
Referenz. Das ist keine operative Bekanntheitserkennung.

### Vorhandene Distanzen zur jeweiligen Referenz

Die Zahlen sind aus den gespeicherten Distanzzeilen uebernommen; fuer diesen
Bericht wurde keine Differenz oder Distanz erneut berechnet.

| Kategorie | Quelle gegen a01 | L1/48 | Quelle gegen a02 | L1/48 |
| --- | --- | --- | --- | --- |
| Exaktkontrolle | a03 | 0.0 | a08 | 0.0 |
| Pegel | a04 | 0.0011457963034864752 | a09 | 0.0011467677584224877 |
| Frequenz | a05 | 0.00209081175117944 | a10 | 0.0014136106649543015 |
| Addition | a06 | 0.0006383109614130994 | a11 | 0.0006380517440099314 |
| Ersetzung | a07 | 0.0012763628106869519 | a12 | 0.0012763627138177886 |
| Unabhaengige Kontrolle | a13 | 0.009072184057390237 | a13 | 0.009075661230543965 |
| Unabhaengige Kontrolle | a14 | 0.009143163179880705 | a14 | 0.009147291129992402 |

Das einzige vorgebundene Referenz-/Referenzpaar `d01-02` hat den gespeicherten
Abstand `0.009170175006743837`. Alle 25 Paare je Implementierung einschliesslich
Fremdreferenzabstaenden und numerischer Einzelterme stehen in `result.json`.

## Alle 24 Ordnungsbefunde

`LT` bedeutet strikt bestanden, `GT` umgekehrte Ordnung. Die linke und rechte
Kennung referenzieren unveraendert die gespeicherten Distanzzeilen. Es gibt
keinen `EQ`-Befund. Die Bewertung erwartet jeweils `left < right`.

| ID | Gruppe | Links | Rechts | Beobachtung |
| --- | --- | --- | --- | --- |
| o01 | Primaer a01 / Pegel-Addition | d04-01 | d06-01 | GT |
| o02 | Primaer a01 / Pegel-Ersetzung | d04-01 | d07-01 | LT |
| o03 | Primaer a01 / Frequenz-Addition | d05-01 | d06-01 | GT |
| o04 | Primaer a01 / Frequenz-Ersetzung | d05-01 | d07-01 | GT |
| o05 | Primaer a02 / Pegel-Addition | d09-02 | d11-02 | GT |
| o06 | Primaer a02 / Pegel-Ersetzung | d09-02 | d12-02 | LT |
| o07 | Primaer a02 / Frequenz-Addition | d10-02 | d11-02 | GT |
| o08 | Primaer a02 / Frequenz-Ersetzung | d10-02 | d12-02 | GT |
| o09 | Eigenreferenz / Pegel a01 | d04-01 | d04-02 | LT |
| o10 | Eigenreferenz / Frequenz a01 | d05-01 | d05-02 | LT |
| o11 | Eigenreferenz / Pegel a02 | d09-02 | d09-01 | LT |
| o12 | Eigenreferenz / Frequenz a02 | d10-02 | d10-01 | LT |
| o13 | Kontrolle a13 / Pegel a01 | d04-01 | d13-01 | LT |
| o14 | Kontrolle a14 / Pegel a01 | d04-01 | d14-01 | LT |
| o15 | Fremdreferenz / Pegel a01 | d04-01 | d01-02 | LT |
| o16 | Kontrolle a13 / Frequenz a01 | d05-01 | d13-01 | LT |
| o17 | Kontrolle a14 / Frequenz a01 | d05-01 | d14-01 | LT |
| o18 | Fremdreferenz / Frequenz a01 | d05-01 | d01-02 | LT |
| o19 | Kontrolle a13 / Pegel a02 | d09-02 | d13-02 | LT |
| o20 | Kontrolle a14 / Pegel a02 | d09-02 | d14-02 | LT |
| o21 | Fremdreferenz / Pegel a02 | d09-02 | d01-02 | LT |
| o22 | Kontrolle a13 / Frequenz a02 | d10-02 | d13-02 | LT |
| o23 | Kontrolle a14 / Frequenz a02 | d10-02 | d14-02 | LT |
| o24 | Fremdreferenz / Frequenz a02 | d10-02 | d01-02 | LT |

## Rezeptorvariation und Kollisionen

- Pegelvarianten: 2/2 haben geaenderte Rohwerte und geaenderte Halbwerte
  gegenueber ihrer eigenen Referenz (a04/a01 und a09/a02).
- Frequenzvarianten: ebenfalls 2/2 in beiden Skalen (a05/a01 und a10/a02).
- Nominale Varianten ohne tatsaechliche Werteaenderung: 0/4.
- Exaktkontrollen a03/a01 und a08/a02: 2/2 bitgleich, sowohl roh als auch halb.
  Diese beiden Kontrollen zaehlen nicht als Variationsnachweis.
- Weitere bitgleiche Roh- oder Halbvektorpaare: 0/23 der uebrigen gebundenen
  Paare. Nur durch Halbierung entstandene Kollisionen: 0/25.
- Bitgleichheit bei unterschiedlichen vorgegebenen Gesamtzuordnungen: 0/25.

Damit liegt in den untersuchten Paaren keine konkrete Repraesentationskollision
als Erklaerung des negativen Trennbefunds vor. Andere, nicht gebundene
Vektorpaare wurden nicht verglichen. Die Aussage ist keine universelle
Informations- oder Kollisionsgarantie.

## Getrennte Arbeitsbudgets und Integritaet

| Arbeit | Beobachteter Umfang | Grenze |
| --- | --- | --- |
| Primaere Distanzpaare / Banddifferenzen | 25 / 1.200 | 25 / 1.200 |
| Direkte Distanzpaare / Banddifferenzen | 25 / 1.200 | 25 / 1.200 |
| Numerische Differenzen beider Implementierungen | 2.400 | 2.400 |
| Primaere Roh-/Halbgleichheitskomponenten | 2.400 | 2.400 |
| Offline-Vorwaertshalbierungen aus gespeicherten Rohwerten | 672 | 672 |
| Offline-Termpruefungen | 2.400 | 2.400 |
| Offline-Gleichheitspruefungen | 2.400 | 2.400 |
| Offline-Summen | 50 | 50 |
| Nachgelagerte Ordnungspruefungen aus gespeicherten Distanzen | 24 | 24 |

Die Offline-Vorwaertshalbierungen sind numerische Belegpruefungen, keine
erneuten NJ-Projektionen. Die technische Verifikation wertete noch keine
fachliche Ordnung aus; diese folgte genau einmal danach. Keine zusaetzlichen
Banddifferenzen in der fachlichen Auswertung. Der Ergebnisdateihash ist vor
und nach der einmaligen read-only Verifikation identisch.

| Bindung | Digest / SHA-256 |
| --- | --- |
| Ausfuehrungsplan | `512cab06237f98ca0481f6b16764e30bdd99bb18841f0fb204c5e4700ae8673d` |
| Historisches Materialisat | `48a75e2957b1c2e65bc6e63f1a24200b3538fb779406d9abb9f2f2638704647f` |
| Materialisatverifikation | `8fe9e748a841a2b0a63e8e4536cdbc92151e6ff828c60310652926b02afeee59` |
| Vergleichsdigest | `d2134e2c88c8b9e7b1d0d095feff7d3598a028c47ad0de314b53e407b6a6defd` |
| Ergebnisdatei vor/nach Verifikation | `d9721b80d4ea244f708476bb50e37d8ddc88a791533b1845de721493f7c89ac5` |
| Vergleichsverifikation | `cff9e15ac82b673a81d655cba1e49ee63bc06ccd8116e19196d7313fc2c78ffe` |
| Getrennte Auswertung | `dbc09ed53de631b52de9cc71f8d676c3b3cad1b8faec2f59261a8f8c9f8dca56` |

## Interpretation und Nichtnachweise

Beobachtet ist eine Verletzung der vorab geforderten Distanzordnung auf
technisch gueltigen, tatsaechlich unterschiedlichen Rezeptorwerten. Die
einfache vollstaendige L1/48-Bewertung trennt diese zulaessigen Varianten
nicht wie gefordert von den zugehoerigen Additionen und Ersetzungen.

Das widerlegt diese gebundene L1-Ordnungsprognose, nicht jede denkbare Nutzung
der 48 Werte. Numerische Verschiedenheit allein belegt umgekehrt keine
brauchbare Gesamtzuordnung. Es wird keine nachgemessene Annahmeschwelle und
keine neue Zulassungsregel vorgeschlagen oder implementiert.

Die Generatorgruppen bleiben kontrollierte Quellenherkunft. Dass Additionen
reale Referenzbestandteile enthalten, ist kein Nachweis, dass das System diese
Bestandteile erkennt. Bestandteilserkennung, Gesamtzuordnung und operative
Enthaltung sind weiterhin verschiedene Aufgaben. Keine semantische Identitaet,
Memory-/Runtimefunktion oder allgemeine Bekanntheitserkennung wurde hier getestet.

WEITER: Am besten geht es jetzt mit der Analysteneinordnung des negativen
L1-Trennbefunds bei fehlender nachgewiesener Repraesentationskollision weiter.
