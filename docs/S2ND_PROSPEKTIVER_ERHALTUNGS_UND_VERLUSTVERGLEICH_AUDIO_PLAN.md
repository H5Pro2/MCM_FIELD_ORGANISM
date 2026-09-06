# S2-ND: Prospektiver auditiver Erhaltungs- und Verlustvergleich

## Auftrag und Aussagegrenze

S2-NC bleibt unveraendert abgeschlossen: neun bekannte Mehrdeutigkeiten
wurden korrekt aufgeloest, beide Regeln hatten null Fehlzulassungen. Es gab
keinen korrekt eindeutigen Mittelwerttreffer, dessen Erhalt pruefbar war.
Dieser Befund wird weder wiederholt noch umgedeutet.

Neue Gegenfrage: Welche korrekt eindeutigen Treffer von `MEAN_L1_24`
erhaelt oder verliert `ALL_BANDS_24` bei nicht bitidentischen Audiohinweisen?
Exaktkontrollen werden getrennt von Varianten ausgewiesen. Neue falsche
Eindeutigkeit nach Verwerfen anderer Kandidaten wird ebenfalls gezaehlt.

Jetzt ausschliesslich dieser statische Plan. Keine PCM-Erzeugung,
Versiegelung von Payloaddigests, Rezeptoranalyse, Tests, Regelvergleiche oder
Systemintegration. Die folgenden Quellenrezepte, Belegungen und Erwartungen
werden vor jedem Rezeptorwert festgelegt; ihre Byteversiegelung ist ein
spaeterer, separat freizugebender Schritt. Es werden keine noch unberechneten
Payloadhashes oder empirischen Distanzen behauptet.

## Unveraenderte Regeln

Je belegter Position, auf den beobachteten Baendern `0..23`:

```text
delta_i = abs(candidate_i - cue_i)          # Binary64
MEAN_L1_24:   statistics.mean(delta) <= 0.2
ALL_BANDS_24: max(delta)             <= 0.2
```

Keine andere Arithmetik, dritte Regel, Gewichtung, Rundung, Toleranz oder
Schwellenwahl. `statistics.mean` bleibt von der historischen
`sum(...)/24`-Rechenfolge unterschieden; kein Anspruch bitidentischer
Produktionsreproduktion. Die unobservierten Baender `24..47` dienen nur
der bestehenden internen vollstaendigen Kandidatengleichheitspruefung.

Alle neun B4- und drei Fast-Positionen werden immer besucht. Leere Positionen
bleiben leer. Mehrere Treffer innerhalb einer Bank ergeben Mehrdeutigkeit;
je ein B4-/Fast-Treffer wird nach der bestehenden exakten 48-Werte- und
Digestgleichheit aufgeloest. Keine Deduplication, Rangfolge, neue
Konfliktaufloesung oder automatische Bevorzugung eines Bereichs.

## Neue Quellen, feste Rezepte

Alle Fenster: Mono `PCM_F32LE`, 48.000 Hz, 4.800 Samples, 19.200 Bytes.
Rezeptor unveraendert: `LogSpectralReceptor.analyze`, Profil
`48000/4800/480/50/18000/48`. Genau eine direkte Analyse pro Quellenfenster
ist spaeter vorgesehen; keine rollende Audiopipeline.

Quelle: harmonische Summe dreier Sinuspartialtoene. Neue Grundfrequenzen und
Seeds werden literal gebunden; keine Filterbankzentren oder gemessenen
Abstaende bestimmen sie. Der Bereich bleibt eine kleine synthetische
Klangaufgabe, keine allgemeine akustische Identitaet oder offene Welt.

Amplitudenformen, jeweils rationale Zaehler-/Nennerpaare in Partialfolge:

| Form | Partial 0 | Partial 1 | Partial 2 |
| --- | --- | --- | --- |
| a0 | 8/20 | 2/20 | 1/20 |
| a1 | 6/20 | 3/40 | 3/80 |
| a2 | 6/20 | 4/20 | 1/20 |

`a1` ist ein gemeinsamer Eingangspegel von 3/4 gegenueber `a0`.
`a2` verlagert fest 1/10 Amplitude vom ersten zum zweiten Partial, ohne die
Summe der Betragsamplituden zu veraendern. Diese begrenzte spektrale
Umgewichtung ist keine nachtraegliche Rezeptor- oder Pegelnormierung.
Der Faktor 103/100 der Frequenzvarianten wird ebenfalls vorab festgelegt.
Variationsstaerken orientieren sich nicht an gemessenen Schwellenabstaenden.

Frequenzen in der Tabelle sind exakt dezimal notierte Hz; gespeichert
werden ganzzahlige Millihertz, ohne erneute Multiplikation zur Laufzeit.

| Quellen-ID | Frequenzen Hz, Partialfolge 0/1/2 | Amplitudenform | Phasenseed |
| --- | --- | --- | --- |
| s001 | 240 / 480 / 720 | a0 | s2nd-pcm-001 |
| s002 | 360 / 720 / 1080 | a0 | s2nd-pcm-002 |
| s003 | 600 / 1200 / 1800 | a0 | s2nd-pcm-003 |
| s004 | 1440 / 2880 / 4320 | a0 | s2nd-pcm-004 |
| s005 | 2160 / 4320 / 6480 | a0 | s2nd-pcm-005 |
| s006 | 3600 / 7200 / 10800 | a0 | s2nd-pcm-006 |
| s007 | 240 / 480 / 720 | a0 | s2nd-pcm-001 |
| s008 | 240 / 480 / 720 | a1 | s2nd-pcm-001 |
| s009 | 247.2 / 494.4 / 741.6 | a0 | s2nd-pcm-001 |
| s010 | 240 / 480 / 720 | a2 | s2nd-pcm-001 |
| s011 | 360 / 720 / 1080 | a0 | s2nd-pcm-002 |
| s012 | 360 / 720 / 1080 | a1 | s2nd-pcm-002 |
| s013 | 370.8 / 741.6 / 1112.4 | a0 | s2nd-pcm-002 |
| s014 | 360 / 720 / 1080 | a2 | s2nd-pcm-002 |
| s015 | 600 / 1200 / 1800 | a0 | s2nd-pcm-003 |
| s016 | 600 / 1200 / 1800 | a1 | s2nd-pcm-003 |
| s017 | 618 / 1236 / 1854 | a0 | s2nd-pcm-003 |
| s018 | 600 / 1200 / 1800 | a2 | s2nd-pcm-003 |

Die Referenzquellen sind s001 bis s006. Die spaeteren Hinweise s007 bis s018
werden niemals als Referenz eingespeist. Exaktkontrollen s007/s011/s015
reproduzieren ihren Referenzpayload bewusst, aber unter neuer Quellen-ID
und strikt spaeterer Zeit. Keine Rezeptorwerte historischer Korpora werden
uebernommen.

Erzeugungsfolge und Arithmetik entsprechen der bereits dokumentierten
rezeptorfreien harmonischen Quelle: pro Partialindex `i` die ersten vier
Bytes von `SHA256((seed + ':' + str(i)).encode('ascii'))` als unsigned
Little-Endian-Integer `u`; Phase `(float(u)/4294967296.0)*math.tau`.
Samples in aufsteigender Reihenfolge, Partiale 0, 1, 2, Binary64-Summe ab 0.0:

```text
t = float(sample_index) / 48000.0
f = float(frequency_millihz) / 1000.0
a = float(numerator) / float(denominator)
angle = ((math.tau * f) * t) + phase
value = value + a * math.sin(angle)
payload_sample = struct.pack('<f', value)   # eine finale Float32-Rundung
```

Keine quellseitige Hannung; die unveraenderte Rezeptor-Hannung bleibt bestehen.
Die Summe der Betragsamplituden ist hoechstens 0.55 und begrenzt die PCM-Summe.
Dies garantiert nicht die Normalform der resultierenden Spektralwerte.
Technisch ungueltige Rezeptorwerte fuehren deshalb zum Stopp, nicht zu
Clipping, neuem Skalierungsfaktor oder Ersatzquelle.

Ordinale Quelle n=1..18 hat die Uhr `s2nd-source-sample-clock` und das Fenster
`[(n-1)*4800, n*4800)`. Quellzeit und Rezeptor-Profilbindung werden getrennt
aufgezeichnet; keine erfundenen nativen Snapshotzeitstempel.

## Feste Belegungen und Fallfolge

Zwoelf Panels, ausschliesslich die folgenden Positionen belegt; alle anderen
der neun B4- und drei Fast-Positionen sind explizit `None`.

| Panel | B4[0] | B4[1] | Fast[0] | Hinweise, feste Reihenfolge |
| --- | --- | --- | --- | --- |
| p01 | s001 | leer | s001 | s007,s008,s009,s010 |
| p02 | leer | leer | leer | s007,s008,s009,s010 |
| p03 | s001 | s004 | s001 | s007,s008,s009,s010 |
| p04 | leer | s004 | leer | s007,s008,s009,s010 |
| p05 | s002 | leer | s002 | s011,s012,s013,s014 |
| p06 | leer | leer | leer | s011,s012,s013,s014 |
| p07 | s002 | s005 | s002 | s011,s012,s013,s014 |
| p08 | leer | s005 | leer | s011,s012,s013,s014 |
| p09 | s003 | leer | s003 | s015,s016,s017,s018 |
| p10 | leer | leer | leer | s015,s016,s017,s018 |
| p11 | s003 | s006 | s003 | s015,s016,s017,s018 |
| p12 | leer | s006 | leer | s015,s016,s017,s018 |

Fall-IDs c001..c048 entstehen panelweise p01..p12, jeweils mit den vier
literal geordneten Hinweisen. Beide Regeln verwenden genau diese Reihenfolge.
Die Entfernungskontrollen sind p01/p02, p03/p04, p05/p06, p07/p08,
p09/p10 und p11/p12. Ausschliesslich die jeweilige Referenz wird entfernt;
ein verbliebener Konkurrent wird weder ersetzt noch verschoben.

Die referenzreinen Belegungen sollen die bisherige Konkurrenzkonfundierung
sichtbar trennen, nicht per Startgate einen Treffer garantieren. Auch
Konkurrenzpanels, leere Panels und erfolglose Varianten bleiben vollstaendig
im Datensatz. Keine Auswahl von Panels nach Analyse. Dies sind kontrollierte
Referenzbelegungen und kein neuer Lauf mit realer Memorybildung.

## Rollen und technische Vorversiegelung

Der Ausfuehrungsplan enthaelt ausschliesslich Quellenrezepte, neutrale IDs,
Zeit-/Profilbindungen, Panelpositionen, Beobachtungsbaender und Budgets.
Nur die getrennte Evaluationswurzel bindet:

- s007..s010 gehoeren als Aufgabenvorgabe zu s001;
- s011..s014 zu s002;
- s015..s018 zu s003;
- je Gruppe Reihenfolge Exakt, gemeinsamer Pegel, Frequenz, Spektralumgewichtung;
- bei vorhandener Referenz wird ausschliesslich diese als korrekter Treffer
  akzeptiert; bei entfernter Referenz ist Enthaltung vorgegeben.

Zur unveraenderten Kategorienform des vorhandenen Auswerters werden Exakt
als `KNOWN_EXACT`, Frequenz als `KNOWN_FREQUENCY_VARIANT` und beide
Amplitudenvarianten als `KNOWN_GAIN_VARIANT` uebergeben. Ein ausschliesslich
nachgelagerter Subtyp `UNIFORM_GAIN` beziehungsweise `SPECTRAL_REWEIGHT`
haelt gemeinsame Pegelaenderung und partielle Umgewichtung getrennt.
Diese Subtypen beeinflussen weder Anwendbarkeit noch fachliche Korrektheit.
Es wird kein allgemeiner Kategorienvalidator erweitert.

Vor jeder spaeteren Rezeptoranalyse: Quellen einmal rezeptorfrei erzeugen,
alle 18 PCM-Payloadhashes, Rezeptdigests, Python-/Generatoridentitaet,
Quellfenster, Dokumenthash sowie Ausfuehrungs- und Evaluationsplandigest
versiegeln. Quelle und Split werden nicht anhand von Distanzen ausgewaehlt.
Bei der getrennten Materialisierung muss jeder regenerierte Payload vor
seiner Analyse exakt dem Siegel entsprechen. Kein neuer Seed, Retry,
Austausch, Umordnen oder nachgemessener Parameterwechsel.

Die Varianten sollen nicht bitidentische PCM-Eingaben sein. Payload- und
Rezeptorbitgleichheit zur zugeordneten Referenz werden spaeter getrennt
berichtet, nicht vorausgesetzt: Eine im Rezeptor verschwundene Variation
wird als solche ausgewiesen und nicht als bestandene Toleranzprobe verkauft.
Alle gueltigen Quellen bleiben auch in diesem Fall erhalten.

## Erhaltungsnenner und Falsifikation

Jeweils getrennt fuer Exakt, gemeinsamen Pegel, Frequenz,
Spektralumgewichtung und alle Varianten zusammen:

1. N: saemtliche vorgebundenen Faelle mit vorhandener Referenz.
2. D: darunter korrekt eindeutige Treffer des Mittelwertarms.
3. R: darunter weiterhin korrekt eindeutige Treffer von ALL_BANDS_24.
4. L: Mittelwerttreffer, die ALL_BANDS_24 nicht korrekt erhaelt; `D = R + L`.

Verlust in Enthaltung und Verlust in falsche Zulassung werden getrennt
benannt. Die Unterteilung nach referenzreinem und Konkurrenzpanel bleibt
erhalten. Identische Cuequellen in mehreren Panels sind abhaengige
Panelpruefungen, keine unabhaengigen Audioaufnahmen.

Nenner vor der Messung: 24 positive Panelpruefungen, davon sechs Exakt- und
18 Variantenfaelle (je sechs pro Variantentyp); weitere 24 Entfernungskontrollen.
Es gibt nur drei verschiedene Exakt-Cuequellen und neun Variantenquellen.
Fuer echte Rezeptorvariation wird zusaetzlich der Teilnenner der
nicht bitidentischen 48-Werte-Ausgaben berichtet, ohne Fallentfernung.

Die universelle Erhaltungsprognose fuer Varianten lautet vorab:
Jeder korrekt eindeutige Mittelwerttreffer bleibt korrekt eindeutig erhalten.

- `D_varianten > 0` und `L_varianten = 0`: Erhaltung auf dem beobachteten
  Teilnenner bestaetigt; kein allgemeiner Transfer- oder Produktionsnachweis.
- `D_varianten > 0` und `L_varianten > 0`: Erhaltungsprognose falsifiziert.
  Jeder Verlust zaehlt, auch wenn anderswo zusaetzliche Treffer entstehen.
- `D_varianten = 0`: `ERHALTUNG_NICHT_GEPRUEFT`, kein Erfolg. Dasselbe gilt
  separat fuer jeden Variantentyp und den echten Rezeptorvariations-Teilnenner.
- Gute Exaktkontrollen ersetzen niemals einen leeren Varianten-Nenner.

Zusaetzlich alle 48 Faelle je Regel auswerten: korrekte bekannte Treffer,
verfehlte bekannte Treffer, falsche Zulassungen, leere Treffermengen,
Mehrdeutigkeiten, Konflikte und korrekte Enthaltungen mit absoluten Zahlen
und Nennern. Insbesondere jede neue Fehlzulassung nach Referenzentfernung
ist ein regulaerer negativer Befund, kein technischer Fehler.

Der vorhandene S2-NC-Auswerter bleibt fuer die gemeinsame Vergleichstabelle
unveraendert. Dessen moegliche aggregierte Verbesserungsentscheidung hebt
eine falsifizierte Erhaltungsprognose nicht auf. Fuer die neue Frage ist der
explizite D/R/L-Befund massgeblich; kein Saldo darf Verluste verdecken.
Es wird keine Zielgenauigkeit als Annahmegate verwendet.

## Wiederverwendung und endlicher Umfang

Unveraendert wiederverwenden: `compare_case`, bestehende A-Aufloesung,
unabhaengige `decide`-Baseline, `verify_case` und nachgelagerte Fallbewertung
aus den privaten S2-NC-Modulen. Keine Aenderung an Regeln oder produktivem Abruf.

Die historischen S2-NC-Korpushelfer binden dagegen konkret 23 Quellen,
alte Plandigests und exakt 528 Beziehungen je Arm. Sie duerfen nicht mit
S2-ND-Daten aufgerufen oder durch Umetikettierung ueberlistet werden.
Eine spaetere kleine Aufrufbindung muss die folgenden neuen Inventarzaehler
explizit fuehren und dieselben reinen Vergleichsfunktionen verwenden.
Jetzt wird weder dieser Aufrufer noch eine neue Infrastruktur implementiert.

| Groesse | Prospektiver S2-ND-Umfang |
| --- | ---: |
| PCM-Fenster / Rezeptoranalysen bei spaeterer Materialisierung | 18 / 18 |
| Samples / erzeugte PCM-Bytes | 86.400 / 345.600 |
| Gleichzeitig gehaltener PCM-Payload | hoechstens 19.200 Bytes |
| Reduzierte Rezeptorwerte | 864 |
| Feste Panels | 12 |
| Faelle je Regel / insgesamt | 48 / 96 |
| Positionsbesuche je Regel / insgesamt | 576 / 1.152 |
| Belegte Beziehungen je Regel / insgesamt | 72 / 144 |
| Absolute Banddifferenzen je Regel / insgesamt | 1.728 / 3.456 |
| A-Entscheidungen / direkte Baselineentscheidungen | 96 / 96 |
| Exakte interne Wertevergleiche, Vergleich insgesamt maximal | 2.304 |
| Zusaetzliche direkte Baselinevergleiche maximal | 2.304 |
| Zusaetzliche Verifikationsvergleiche maximal | 2.304 |
| Gleichheitsvergleiche einschliesslich Verifikation maximal | 6.912 |

Herleitung: je Referenzgruppe und Regel vier Hinweise auf Panels mit
`2 + 0 + 3 + 1` belegten Positionen: 24 Beziehungen; drei Gruppen: 72.
Nur die beiden referenzhaltigen Panels je Gruppe koennen zugleich einen
B4- und Fast-Treffer liefern: maximal 24 Faelle je Regel mit 48
Gleichheitsvergleichen. Keine versteckten Vollscandistanzen fuer leere Slots.

Die bisherigen Ressourcenobergrenzen werden nicht erhoeht: hoechstens
528 Beziehungen und 12.672 Banddifferenzen pro Regel, hoechstens 9.216
Gleichheitsvergleiche insgesamt und maximal 4.194.304 kanonische
Ergebnisbytes. Der geringere tatsaechliche Arbeitsumfang folgt aus den
vorab sparsam belegten Panels, nicht aus einem vorzeitigen Scanabbruch.

Spaeter genau ein Vergleich, vollstaendige Aufzeichnung, anschliessend genau
eine unabhaengige read-only Verifikation und erst danach fachliche Bewertung.
Technische Quellen-, Typ-, Zeit-, Profil-, Digest-, Ausfuehrungs- oder
Budgetfehler ergeben `NOT_EVALUABLE`; unguenstige gueltige Trefferbilder nicht.
Kein Retry, keine nachtraegliche Auswahl erfolgreicher Faelle.

## Abschluss dieses Auftrags

Nur dieser Plan wird dokumentiert und versioniert. Keine Materialisierung,
Tests, Auswertung, historische Belegaenderung, Memory-, Feld-, Kontext-
oder Runtimeintegration. S2-NC bleibt geschlossen und seine Arithmetikbindung
erhalten. Ein Erhaltungs- oder Verlustbefund fuer S2-ND liegt noch nicht vor.

WEITER: Am besten geht es jetzt mit der Analystenpruefung dieses einzelnen
Plans und danach gegebenenfalls der separaten Freigabe seiner rezeptorfreien
Quellenvorversiegelung weiter; noch keine Rezeptor- oder Vergleichsausfuehrung.
