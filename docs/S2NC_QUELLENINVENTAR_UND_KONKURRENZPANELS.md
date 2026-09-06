# S2-NC: Neues Quelleninventar und feste Konkurrenzpanels

## Arbeitsgrenze

Diese Ergaenzung materialisiert ausschliesslich das Inventar zum
S2-NC-Vergleich. PCM-Quellbytes duerfen zur Vorversiegelung einmal erzeugt,
auf Formatgueltigkeit geprueft und gehasht werden. Rezeptoren, Distanzregeln,
Memory, Kontext und Feld bleiben unaufgerufen. Eine Vergleichsfunktion
wird hier nicht implementiert oder qualifiziert.

S2-NB bleibt geschlossen. Seine Rezeptorvektoren oder Distanzen werden
nicht eingelesen oder fuer die Quellenwahl verwendet. Die Rezeptorquelle
und S2-KZ werden nur als Code gelesen und gehasht.

## Quellenauswahl vor jedem Rezeptorwert

Gewaehlter kleiner Testbereich: synthetische harmonische Klangfenster.
Die Grundfrequenzen sind eine einfache, vorab feste 55-Hz-Reihe mit drei
Oktavfortsetzungen sowie zwei neuen Zwischentoenen. Sie sind nicht an
Filterbankzentren, gemessene Rezeptorabstaende oder ein gewuenschtes
Matchergebnis angepasst. Der gewaehlte Bereich ist weder offene Welt
noch ein repraesentativer Audiokorpus.

Alle Fenster: Mono `PCM_F32LE`, 48.000 Hz, 4.800 Samples, 19.200 Bytes.
Ein Standardklang besitzt drei Partialfrequenzen `f / 2f / 3f` mit
Amplituden `0.4 / 0.1 / 0.05`. Die Summe ihrer Betragsamplituden ist `0.55`.
Es gibt keine Pegeloptimierung, Kompression, Quelle-Hannung oder Clipping.
Die vorhandene Hannung innerhalb des unveraenderten Rezeptors bleibt bestehen.

| Quellen-ID | Frequenzen in Hz | Amplituden | Phasenseed |
| --- | --- | --- | --- |
| s001 | 220 / 440 / 660 | Standard | s2nc-pcm-001 |
| s002 | 330 / 660 / 990 | Standard | s2nc-pcm-002 |
| s003 | 550 / 1100 / 1650 | Standard | s2nc-pcm-003 |
| s004 | 165 / 330 / 495 | Standard | s2nc-pcm-004 |
| s005 | 275 / 550 / 825 | Standard | s2nc-pcm-005 |
| s006 | 385 / 770 / 1155 | Standard | s2nc-pcm-006 |
| s007 | 770 / 1540 / 2310 | Standard | s2nc-pcm-007 |
| s008 | 1540 / 3080 / 4620 | Standard | s2nc-pcm-008 |
| s009 | 3080 / 6160 / 9240 | Standard | s2nc-pcm-009 |
| s010 | 220 / 440 / 660 | Standard | s2nc-pcm-001 |
| s011 | 220 / 440 / 660 | 0.30 / 0.075 / 0.0375 | s2nc-pcm-001 |
| s012 | 226.6 / 453.2 / 679.8 | Standard | s2nc-pcm-001 |
| s013 | 330 / 660 / 990 | Standard | s2nc-pcm-002 |
| s014 | 330 / 660 / 990 | 0.30 / 0.075 / 0.0375 | s2nc-pcm-002 |
| s015 | 339.9 / 679.8 / 1019.7 | Standard | s2nc-pcm-002 |
| s016 | 550 / 1100 / 1650 | Standard | s2nc-pcm-003 |
| s017 | 550 / 1100 / 1650 | 0.30 / 0.075 / 0.0375 | s2nc-pcm-003 |
| s018 | 566.5 / 1133 / 1699.5 | Standard | s2nc-pcm-003 |
| s019 | 467.5 / 935 / 1402.5 | Standard | s2nc-pcm-010 |
| s020 | 1023 / 2046 / 3069 | Standard | s2nc-pcm-011 |
| s021 | keine | exakt null | kein wirksamer Seed |
| s022 | 220 / 440 / 660 | 0.0125 / 0.003125 / 0.0015625 | s2nc-pcm-001 |
| s023 | Partiale von s001 und s002 | jeweils halbe Standardamplituden | beide Originalseeds |

Die Referenzen sind ausschliesslich s001 bis s009. Die spaeteren Hinweise
s010 bis s023 werden nicht in Referenzpanels eingesetzt. s010/s013/s016
sind bewusste bytegleiche Wiederholungen bei neuen Quellenordinalzahlen.
Die sechs Varianten behalten den Seed und veraendern ausschliesslich
den Pegel um -25 Prozent beziehungsweise alle Frequenzen um +3 Prozent.
Diese Festlegungen erfolgen unabhaengig von der spaeteren Rezeptorausgabe.

## Exakte Erzeugung und Zeitbindung

Frequenzen sind ganzzahlige Millihertz; Amplituden sind ganzzahlige
Zaehler-/Nennerpaare. Fuer jeden Partialindex wird
`SHA256((seed + ':' + str(index)).encode('ascii'))` gebildet. Seine ersten
vier Bytes als unsigned Little-Endian-Integer `u` bestimmen die Phase
`(float(u) / 4294967296.0) * math.tau`.

Pro Sample gilt in Binary64 und in der gespeicherten Gruppen-/Partialfolge:

```text
t = float(sample_index) / 48000.0
f = float(frequency_millihz) / 1000.0
a = float(numerator) / float(denominator)
angle = ((math.tau * f) * t) + phase
value = value + a * math.sin(angle)   # Startwert 0.0; keine Umordnung
payload += struct.pack('<f', value)  # genau eine finale F32-Rundung
```

Python-Version, Skripthash und jeder Payloadhash werden versiegelt.
Eine spaetere libm-/Plattformabweichung rechtfertigt keinen neuen Hash;
die konkrete Regeneration muss den versiegelten Payload exakt treffen.
Alle Rohbytes sind nur fluechtige Testeingaben, kein Memoryinhalt.

Die 23 Quellen stehen in literaler Ordinalfolge s001 bis s023. Ihre
Quelluhr heisst `s2nc-source-sample-clock`; Fenster n umfasst
`[(n-1)*4800, n*4800)`. Vor der ersten Cuequelle sind alle neun Referenzen
vollstaendig abgeschlossen. Ein spaeterer Rezeptorschritt verwendet
`LogSpectralReceptor.analyze` direkt einmal je 4.800er-Fenster in dieser
Folge. Es gibt keine rollenden Zwischenabschluesse oder rueckgesetzte
native Audiouhr. Die Quellzeit wird nicht als gemessener Rezeptorzeitstempel
ausgegeben. Dies ist ein isolierter Referenzvergleich, kein Liveadapter.

Das unveraenderte Profil ist `48000/4800/480/50/18000/48`.
Fuer Anwendbarkeit bleiben nur Baender 0 bis 23 sichtbar; 24 bis 47
sind allein fuer die bestehende interne Kandidatengleichheit verfuegbar.

## Sechs feste Konkurrenzpanels

B4 hat neun Pruefpositionen 0 bis 8, Fast drei Positionen 0 bis 2.
Ein leerer Eintrag bleibt leer und wird nicht durch eine andere Quelle ersetzt.

| Panel | B4-Quellen auf Positionen 0..8 | Fast auf Positionen 0..2 |
| --- | --- | --- |
| p01 | s001,s002,s003,s004,s005,s006,s007,s008,s009 | s001,s008,s009 |
| p02 | leer,s002,s003,s004,s005,s006,s007,s008,s009 | leer,s008,s009 |
| p03 | s001,s002,s003,s004,s005,s006,s007,s008,s009 | s002,s008,s009 |
| p04 | s001,leer,s003,s004,s005,s006,s007,s008,s009 | leer,s008,s009 |
| p05 | s001,s002,s003,s004,s005,s006,s007,s008,s009 | s003,s008,s009 |
| p06 | s001,s002,leer,s004,s005,s006,s007,s008,s009 | leer,s008,s009 |

Die Paare p01/p02, p03/p04 und p05/p06 unterscheiden sich jeweils nur
durch Entfernung der zugeordneten Referenz aus beiden Banken. Andere
Referenzen sind in dem jeweiligen Paar Konkurrenten und bleiben erhalten.
Belegungen mit Luecken sind erlaubte kontrollierte Panels; sie behaupten
keinen durch FIFO oder Fast-LRU erreichbaren Memoryzustand.

Alle Panels erhalten s019 bis s023. Zusaetzlich erhalten p01/p02
s010 bis s012, p03/p04 s013 bis s015 und p05/p06 s016 bis s018.
Die Ausfuehrungsfolge ist panelweise p01 bis p06, darin aufsteigende
Hinweis-ID; die 48 Fall-IDs c001 bis c048 sind damit vollstaendig festgelegt.
Keine Belegung darf spaeter aus einer guenstigen Distanzmatrix ausgewaehlt werden.

Alle Positionen werden je Fall vollstaendig besucht. Mehrfachtreffer in
einer Bank bleiben mehrdeutig. Bei je einem Treffer in beiden Banken
bleibt der bestehende exakte 48-Werte-Vergleich inklusive Digestpruefung
erhalten. Gleiche Quellen in unterschiedlichen Banken werden nicht
vor dem Scan zusammengelegt. Keine Slow-Regel, Fuellung oder Rangfolge.

## Getrennte Auswertungswurzel

Nur die nachgelagerte Bewertung kennt folgende externe Relationen:

- s010/s011/s012 gehoeren zur Referenz s001;
- s013/s014/s015 gehoeren zur Referenz s002;
- s016/s017/s018 gehoeren zur Referenz s003;
- s019/s020 sind unbekannte Quellrezepte;
- s021/s022 sind vorab als informationsarme Testeingaben gebunden;
- s023 ist eine gleichgewichtete Quellmischung, kein Einzelidentitaetsziel.

Diese Relationen sind Aufgabenvorgaben, keine semantischen Tatsachen.
Insbesondere die leise Variante wird normativ als Enthaltungsaufgabe
bewertet, obwohl sie technisch aus s001 entsteht. Ihre Kategorie wird
nicht erst anhand einer gemessenen Rezeptorenergie entschieden. Fuer die
Mischung wird keine tatsaechliche Rezeptormehrdeutigkeit vorausgesetzt.

Bekannte Hinweise bei vorhandener Referenz verlangen genau diese Quelle.
Nach ihrer Entfernung, bei unbekannten, informationsarmen und gemischten
Hinweisen gilt jede Zulassung als Fehlzulassung. Sowohl leere Treffermengen
als auch Ambiguitaet und interner Konflikt sind erlaubte Enthaltungen und
werden getrennt berichtet. Nenner je Arm:

- 3 exakte, 3 Pegel- und 3 Frequenzvarianten mit vorhandener Referenz;
- 9 bekannte Hinweise nach Entfernung;
- 12 unbekannte, 12 informationsarme und 6 gemischte Faelle.

Die Erfolgs-/Zielkonfliktregel des S2-NC-Hauptvertrags bleibt unveraendert.
Keine Erfolgsbedingung wird zum Materialisierungsgate.

## Feste Budgets und nachfolgende Grenze

- Vorversiegelung: 23 PCM-Fenster, 110.400 Samples, 441.600 erzeugte Bytes;
  maximal ein 19.200-Byte-Payload gleichzeitig, keine Rohdateien gespeichert.
- Spaetere Materialisierung: genau 23 Rezeptoranalysen und 1.104 Werte;
  kein Matcher, keine Memory-, Feld- oder Kontextausfuehrung dabei.
- Spaeterer Vergleich je Regel: 48 Faelle, 576 Positionsbesuche,
  528 belegte Beziehungen und 12.672 absolute Banddifferenzen.
- Beide Regeln zusammen: 1.056 Beziehungszeilen, 25.344 Banddifferenzen,
  96 A-Entscheidungen und hoechstens 4.608 exakte Wertevergleiche fuer
  interne A-Kandidatengleichheit. Leere Positionen erzeugen keine Distanzen.
- Die reine direkte Entscheidungstabellen-Baseline prueft weitere
  96 A-Entscheidungen auf denselben vollstaendigen Banktreffermengen;
  sie fuehrt keine weiteren Distanzmessungen aus. Ein separat abgeleiteter
  Digest-/Wertegleichheitsbefund kann maximal weitere 4.608 Wertevergleiche
  benoetigen. Insgesamt hoechstens 9.216 Gleichheitsvergleiche.
- Kanonisches spaeteres Vergleichsergebnis: maximal 4.194.304 Bytes.
  Die zwei Regeln erhalten identische Ressourcenobergrenzen.

Die Source-Siegelung ist kein Funktionslauf und kein positiver Geometriebefund.
Nach Erstellung sind Inventar, Panels, Rollen, Seeds und Payloadhashes
eingefroren. Eine spaetere einmalige Rezeptormaterialisierung und die
Vergleichsimplementierung bleiben getrennte naechste Schritte.
