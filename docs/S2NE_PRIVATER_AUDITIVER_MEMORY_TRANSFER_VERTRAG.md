# S2-NE: Privater auditiver Memory-Transfervertrag

## Status und Grenze

Ausschliesslich statischer Vertrag. Keine Implementierung, Rezeptor- oder
Memoryausfuehrung, Tests oder neue Auswertung. S2-NC/S2-ND bleiben mit ihren
unveraenderten Panelbefunden abgeschlossen. Dieser Vertrag autorisiert
keinen Hauptlauf und keine Produktumstellung.

Frage: Uebertraegt sich der begrenzte Vorteil von ALL_BANDS_24 auf
tatsaechlich gebildete B4-/Fast-/Slow-Zustaende, ohne richtige A-Treffer zu
verlieren oder durch automatischen B-Vorrang Mehrdeutigkeit zu uebergehen?
Dies ist gezielte technische Uebertragung bereits untersuchter Quellen,
keine unabhaengige Generalisierung.

## Genau eine experimentelle Aenderung

Referenz: unveraenderter
`form_auditory_partial_cue_retrieval_336` aus S2-KZ. Alternative:
private Anbindung mit identischem validiertem Zustand, Cue und Bandplan.

```text
delta_i = abs(candidate[i] - float(cue.values[i])), i = 0..23
Referenz A, B4 und Fast: sum(delta_i in Bandreihenfolge) / 24 <= 0.2
Alternative A:          max(delta_i in Bandreihenfolge)      <= 0.2
Beide B-Auditory-Slow:  sum(delta_i in Bandreihenfolge) / 24 <= 0.02
```

Die Referenz ist NICHT bitidentisch mit dem S2-NC-/S2-ND-Arm
`statistics.mean`. Keine Arithmetikkorrektur des historischen Abrufs,
keine Rundung, Toleranz, neue Schwelle oder dritte Regel.
Alle 24 Differenzen werden auch im Max-Arm vollstaendig gebildet.

Formation unveraendert: Fast-Match benoetigt Audio UND Video im vollen
Profil innerhalb jeweils 0.2; Trennung benoetigt Audio ODER Video ausserhalb.
Fast-Kapazitaet 3, Updatefaktor 0.5, Konsolidierung ab Support 2, Ablauf 8.
B4 bleibt FIFO mit 9 Slots. PPB bleibt auditiv 8 Slots / 0.02, visuell
4 Slots / 0.01, jeweils Updaterate 0.05 und stabile Grenze 3.

Unveraendert bleiben Eignung der Slots, vollstaendiger 9/3/8-Scan,
B4-/Fast-Aufloesung, exakte Gleichheit ihrer vollen 48 Kandidatenwerte,
Slow-Regel und oeffentliche A/B-Entscheidung. Mehrere Treffer innerhalb
einer Bank bleiben Mehrdeutigkeit, selbst bei wertgleichen B4-Eintraegen.
Ein A- und ein B-Kandidat bedeuten Enthaltung, auch bei gleichem Inhalt.
Keine Deduplication, Rangfolge, Bevorzugung von B, Kontextanwendung oder
Feldrueckwirkung. Hypothesen enthalten nur getrennte 24 Maskenwerte.

Die private Alternative darf S2-KZ nicht monkeypatchen. Eine technische
Armhuelle bindet Regel-ID und Quellhash; ein Max-Statistikwert wird nicht
als Mittelwert bezeichnet. Bestehende produktive Module bleiben unveraendert.

## Konkrete Quellen und prospektive Zeit

Aus S2-ND unveraendert: s001, s004 und s007..s010 aus dem versiegelten
`execution-plan.json`. s001 ist die erste Referenz, s004 ihr festgelegter
Konkurrent; s007 ist Exaktkontrolle, s008 Pegel-, s009 Frequenz- und s010
Spektralvariante. Alle sechs bleiben enthalten. Keine Wahl anhand neuer
Messungen, anderer Seed, Skalierung oder Clipping.

Visuell ausschliesslich S2-JX: X und D1..D9, mit den dort literal gebundenen
RGB-Payload- und 288-Werte-Digests. Generator `_visual_image` unveraendert:
1920x1080 RGB8, 12x8 Zellen; fuer flachen Kanalindex i und Ordinal o
255 genau dann, wenn `(i+o)%11 in {1,3,4,5,9}`, sonst 0.
X hat o=0, D1..D9 haben o=2..10. Keine neuen visuellen Fixtures.

Nur folgende Auswertungsnotation wird im Vertrag verwendet:

- T = Audio s001 + Bild X.
- E1..E9 = Audio s004 + jeweiliges Bild D1..D9.
- Q0/Qg/Qf/Qs = spaetere Audioquellen s007/s008/s009/s010.

Im technischen Lauf werden ausschliesslich neutrale History-, Ereignis-,
Rezept- und Quellen-IDs uebergeben, niemals T-/E-/Q-Rollen oder Sollwerte.
Kandidaten kommen allein aus dem atomaren S2-JW-B4-/TSPM-Koordinator.
Kein Einsetzen von Vektoren in Slots, kein Laden historischer Memoryzustaende.

Jedes Quellenereignis wird spaeter neu aus den unveraenderten Rezepten
erzeugt. PCM-Payloadhash vor `LogSpectralReceptor.analyze` gegen S2-ND,
RGB-Hash vor `LocalChannelGridReceptor.analyze` gegen S2-JX pruefen.
Direkter Audiorezeptor: unveraendertes Profil 48000/4800/480/50/18000/48,
genau ein analyze je Fenster, keine rollende Pipeline. Die resultierenden
Wertedigests muessen die vorhandenen Quellenbindungen reproduzieren.

Ein `ReceptorContactFrame` darf die direkt erzeugten Werte mit expliziter
Quellzeit binden; kein erfundener Broadband-Snapshot oder rekonstruierter
historischer Zeitstempel. Geometrie und Carrierfolge muessen mit dem
qualifizierten Default-Live-Profil uebereinstimmen. Es werden keine
handgeschriebenen 48-/288-Werte als Rezeptorausgabe verwendet.

Pro frischer Geschichte j=0,1,... in der unten gebundenen Ereignisfolge:
Audiofenster [9600*j,9600*j+4800) bei 48000 Hz, native Uhr
`s2ne-hXX-audio-sample`. Visueller Frameindex 6*j+2 bei 30 Hz.
Gemeinsame Paarzeit in ns: Audio [200000000*j,200000000*j+100000000),
Video [floor((6*j+2)*1000000000/30),200000000*j+100000000).
Beide ueberlappen real im letzten Drittel des Audiofensters.
Die gemeinsame Uhr `s2ne-hXX-pair-clock` erzeugt keinen Feldaufruf.
Ein Cue verwendet nur seine native Audiozeit, keine visuelle Uhr.

Neue Ereignis-ID `s2ne-hXX-eYY`; Payloadgleichheit bedeutet keine Wiederverwendung
derselben zeitlichen Quelle. Die alten S2-ND-Quellfenster bleiben historisch
unveraendert; ein neuer Elternbeleg verbindet Rezept-ID/Payloadhash mit dem
neuen Ereignisfenster. Jeder Formationowner ist neu und einmalig.
Bei Teilhinweisen werden nur Baender 0..23 freigegeben, 24..47 sind None.
Kein vorbereitender Memory-Vollabruf; verborgene Cuewerte beeinflussen
weder Treffer noch Auswahl. Rohdaten nach Reduktion freigeben.

## Literale Geschichten und Fallmatrix

Fuenf frische, voneinander getrennte Memoryzustaende plus ein Nullzustand.
Pfeile bezeichnen read-only Cues, keine Formationen.

```text
h01: T -> Q0 Qg Qf Qs
h02: T E1 -> Q0 Qg Qf Qs
h03: E1 -> Q0
h04: T T T T E1 E2 E3 E4 E5 E6 E7 E8 E9 -> Q0; T -> Q0
h05: T T -> Q0
h06: Nullzustand -> Q0
```

h04 ist eine fortgesetzte Geschichte, keine Zustandskopie: nach Formation 13
folgt Cue q10, danach Formation 14 und Cue q11. Die Cuezeit wird beim
spaeteren Quellenereigniszaehler mitgezaehlt, nicht als Memoryformation.
Geschichten werden in der Reihenfolge h01..h06 abgearbeitet.

| Faelle | Zustand | Audio-Cue | Fachliche Referenzprognose | Alternative |
| --- | --- | --- | --- | --- |
| q01..q04 | h01 nach 1 | s007,s008,s009,s010 | korrekt A | korrekt A, Erhaltung |
| q05..q08 | h02 nach 2 | s007,s008,s009,s010 | A-interne Mehrdeutigkeit | korrekt A |
| q09 | h03 nach 1 | s007 | falsche A-Zulassung von s004 | keine Anwendbarkeit |
| q10 | h04 nach 13 | s007 | A-interne Mehrdeutigkeit trotz stabilem B | korrekt B |
| q11 | h04 nach 14 | s007 | A-interne Mehrdeutigkeit | oeffentliche A/B-Mehrdeutigkeit |
| q12 | h05 nach 2 | s007 | A-Bankmehrdeutigkeit | A-Bankmehrdeutigkeit |
| q13 | h06 | s007 | kein Kontext | kein Kontext |

Erwartungen gehoeren ausschliesslich in die getrennte Evaluationswurzel.
Keine Vorhersage ist technisches Erfolgsgate. Eine regulaere Abweichung
wird nach vollstaendiger Aufzeichnung als Funktionsbefund ausgewertet.

## Statische Erreichbarkeit

h01: B4[0]=T und Fast[0]=T/Support1, sonst leer, kein PPB-Aufruf.
Die Kandidaten sind exakt gleich, weil beide aus derselben Formation stammen.

h02: E1 ist wegen X/D1-Trennung ein neuer Fast-Slot, kein Update von T.
B4 enthaelt T,E1; Fast[0]=T/1, Fast[1]=E1/1; Slow leer.
h03: nur E1 in B4[0] und Fast[0]/1, Slow leer. Damit ist Zielentfernung
eine echte neue Bildungsgeschichte, kein manuelles Loeschen eines Slots.

h04, jede Zeile bezeichnet einen wirklichen Formationsschritt:
```text
1:  Fast F0=T/s1; Slow leer
2:  F0=T/s2/c1; beide PPB-S0 CREATED/s1
3:  F0=T/s2/c2; beide PPB-S0 MATCHED/s2
4:  F0=T/s2/c3; beide PPB-S0 MATCHED/s3
5:  F1=E1/s1
6:  F2=E2/s1
7:  F0=E3/s1 ersetzt T
8:  F1=E4/s1 ersetzt E1
9:  F2=E5/s1 ersetzt E2
10: F0=E6/s1 ersetzt E3
11: F1=E7/s1 ersetzt E4
12: F2=E8/s1 ersetzt E5
13: F0=E9/s1 ersetzt E6
14: F1=T/s1 ersetzt E7; kein neuer PPB-Aufruf
```

B4 ist nach Schritt k exakt die letzten min(k,9) Formationen in seinem
unveraenderten Ring. Nach 13: chronologisch E1..E9; physisch
[ E6,E7,E8,E9,E1,E2,E3,E4,E5 ]. Nach 14:
[ E6,E7,E8,E9,T,E2,E3,E4,E5 ].
Fast nach 13: [E9,E7,E8], nach 14: [E9,T,E8].
LRU folgt den letzten Auswahlschritten; vor jeder Ersetzung ist das Alter
kleiner 8. Kein Druckinhalt wird wiederholt, keiner erreicht Fast-Support 2.

X/Di und unterschiedliche Di/Dj besitzen die bereits in S2-LC/S2-JV
abgeleitete visuelle Distanz mindestens 13/24 > 0.2. Somit trennen sich
alle E-Formationen gemeinsam in Fast unabhaengig von ihrer gleichen
Audioquelle. Die Druckphase erzeugt keine weiteren PPB-Aufrufe.
Beide Slow-Banken behalten nur S0 mit Support 3; die anderen Slots bleiben
leer. q10 trifft somit real vorhandene B-Inhalte nach vollstaendigem
Zielverlust aus B4 und Fast.

PPB-Endwerte fuer Audio UND Video werden gemaess S2-LF aus
CREATED -> MATCHED -> MATCHED abgeleitet:
`p0=x; p1=(1.0-0.05)*p0+0.05*x; p2=(1.0-0.05)*p1+0.05*x`,
komponentenweise in exakt der Binary64-Operationsfolge des Kerns.
Kein Runden, kein Digest des Ausgangsvektors als Endprototypdigest.
Die Formations-/Supportkette bindet Reihenfolge, obwohl x wiederholt gleich
ist. Unter 0..1 ist das Rundungsresiduum dieser zwei Updates konservativ
kleiner als 2^-48 und damit klar innerhalb der unveraenderten Slow-Grenze
0.02 gegen die exakte Q0-Quelle. Integritaet und funktionaler Treffer bleiben
getrennte Pruefungen.

h05: zwei T-Eintraege in B4, ein aktualisierter T-Fast-Slot/s2/c1; je
PPB-Bank ein CREATED-Slot mit Support1, nicht stabil. Zwei B4-Treffer
erzwingen Enthaltung, auch bei identischen Kandidatenwerten.
h06: alle Slots frei.

Bereits aufgezeichnete S2-ND-Werte, keine neue Distanzberechnung:
| Cue | T-Mittelwert / T-Maximum | E-Audio-Mittelwert / E-Audio-Maximum |
| --- | --- | --- |
| s007 | 0 / 0 | 0.029838435371604115 / 0.26692969544099204 |
| s008 | 0.007459612453191895 / 0.06673242522731035 | 0.02237882291841222 / 0.2001972702136817 |
| s009 | 0.012815233259653691 / 0.10512390324962623 | 0.030363397848509378 / 0.36591889487245943 |
| s010 | 0.010853533305731026 / 0.11140202404082614 | 0.029752733828803692 / 0.22280402880490205 |

Die Tabellenmittelwerte verwenden statistics.mean und ersetzen NICHT die
spaetere historische Rechenfolge. Alle liegen jedoch mehr als 0.16 unter
0.2; die konservative Binary64-Summationsabweichung fuer 24 nichtnegative
Terme aus 0..1 bleibt unter 1e-13. Die hier benutzte statische Seite der
Referenzgrenze haengt deshalb nicht von der Arithmetikdifferenz ab.
S008/E hat nur etwa 0.000197 Max-Reserve; dieser bekannte Grenzabstand bleibt
unveraendert, ohne nachtraegliche Quellenkorrektur.

## Vergleich, Baseline und falsifizierbare Auswertung

Je Cue dasselbe echte Zustand/Cue/Bandplan-Tupel an Referenz, Alternative
und je eine unabhaengige Direktbaseline. Baselines scannen selbst und
verwenden keine Trefferlisten oder Entscheidungshelfer des jeweiligen Arms.
Der qualifizierte S2-KZ-Direktarm bleibt Referenzbaseline; fuer ALL_BANDS
nur dieselbe eine A-Statistikaenderung in einer privaten direkten Umsetzung.
Read-only gilt fuer alle vier Abrufe, nicht fuer die 20 Formationen.

Zunaechst vollstaendig aufzeichnen, dann einmal unabhaengig read-only
verifizieren, erst danach auswerten. Kandidatenintegritaet aus
Formationsquelle, Slot, Pre-/Postzustand, Konfiguration und PPB-Uebergang
nachweisen. Verifikation akzeptiert jede gueltige Enthaltung; Rollen,
Zielwerte und Erwartungen entscheiden niemals technische Gueltigkeit.

N/D/R/L getrennt fuer exakte A- und variierte A-Hinweise sowie Konkurrenz:
N sind q01..q08; D korrekt eindeutige Referenz-A-Treffer, R deren Erhalt,
L Verlust in Enthaltung oder falsche Zulassung, D=R+L.
Prospektiv ohne Konkurrenz: exakt 1/1/1/0, Varianten 3/3/3/0.
Mit Konkurrenz: exakt 1/0/0/0, Varianten 3/0/0/0; D=0 bleibt
ERHALTUNG_NICHT_GEPRUEFT. Tatsaechliche Rezeptorbitvariation separat berichten.
q10 ist B-Zugriff nach A-Verlust, kein erhaltener A-Ausgangstreffer.

Alle 13 Faelle erhalten zusaetzlich Treffer-/Fehlzulassungs-/Enthaltungsstatus.
q09 ist Zielentfernung, nicht allgemeine Unbekanntheit. q11/q12/q13 sind
harte Enthaltungskontrollen. Hypothesen muessen genau die belegten
Kandidatenwerte tragen; keine Wunschrolle darf den Inhalt ersetzen.

Begrenzter Transfer bestaetigt nur, wenn alle Matrixvorhersagen,
Baselinegleichheit, tatsaechliche Inventare und Read-only-Bindungen stimmen,
kein bisher korrekter A-Treffer verloren geht und keine neue Fehlzulassung
entsteht. Jeder Verlust, falscher Kandidat oder verfehlte Kontrollfall
falsifiziert den entsprechenden Claim, auch bei anderen Gewinnen.
Technische Quellen-/Typ-/Digest-/Zeit-/Budgetfehler ergeben NOT_EVALUABLE.
Keine Reparatur, Nachselektion oder Parameteraenderung nach einem Lauf.

## Exakter Umfang und harte Grenzen

| Groesse | Gebunden |
| --- | ---: |
| Frische Geschichten / zusaetzlicher Nullzustand | 5 / 1 |
| Formationen je h01..h05 | 1 / 2 / 1 / 14 / 2 |
| Atomare Formationsaufrufe / B4-Schreibschritte / TSPM-Schritte | 20 / 20 / 20 |
| Teilhinweisereignisse | 13 |
| Direkte Audioanalysen / visuelle Analysen bei spaeterer Bildung | 33 / 20 |
| Erzeugte Endpunkt-Rezeptorwerte | 33*48 + 20*288 = 7.344 |
| Abrufaufrufe Referenz / Alternative / ihre Baselines | 13 / 13 / 26 |
| Slotscanpositionen einschliesslich Baselines | 52*20 = 1.040 |
| Banddifferenzen maximal | 52*480 = 24.960 |
| Interne 48-Werte-Vergleiche maximal | 52*48 = 2.496 |
| Alle Abruf-Wertvergleiche maximal | 52*528 = 27.456 |
| Zusaetzliche unabhaengige Verifikations-Wertvergleiche maximal | 52*528 = 27.456 |
| Abruf plus Verifikations-Wertvergleiche maximal | 54.912 |
| Logische S2-KZ-Operationen einschliesslich Baselines | 52*14 = 728 |
| Formations-L1-Terme, profilabgeleitete Obergrenze | 20*3.552 = 71.040 |
| Numerischer Zustand je aktueller Geschichte | maximal 44.544 Bytes |
| Gleichzeitiger RGB-/PCM-Rohpayload | maximal 6.220.800 / 19.200 Bytes |
| Vollstaendige kanonische Ausgabe je Abruf | kleiner 32.768 Bytes |
| Gesamter atomarer Ergebnisbeleg | maximal 4.194.304 Bytes |
| Feld-, Runtime-, Vollprobe- und Fuellaufrufe | 0 |

Die Zustandsableitung prognostiziert vier PPB-Aufrufe je Modalitaet:
drei in h04 und einen in h05. Ebenso ergeben die geplanten Probeinventare
55 geeignete Slotbeziehungen pro Arm, mithin 5.280 Banddifferenzen ueber
alle vier Arme. Diese abhaengigen Zaehler sind Vorhersagen, keine Gates,
die eine echte Inventarabweichung zum technischen Fehler umdeuten.
Harte Scanobergrenzen gelten unabhaengig vom funktionalen Ergebnis.
Keine Umdeutung der alten S2-JW-Planmetadaten 15/3/72 als neue Laufzaehler.

Ein Ergebnisbeleg genuegt: begrenzte Formationsreceipts, relevante echte
Zustandsbelege und 52 Abrufbelege samt Baselinevergleich; einmalige
Verifikation und getrennte Auswertung. Die Verifikation darf aus den
aufgezeichneten Zustands-/Cuewerten einmal dieselben Banddifferenzen und
internen Gleichheitsbedingungen pruefen; dafuer ist die eigene Reserve
oben gebunden. Sie ruft weder Memoryformation noch einen der Abrufarme
erneut auf. Hash-/Typpruefungen sind keine funktionalen L1-Terme.
Keine Operationsregistry,
append-only Recorderplattform oder neue Memoryebene. Die konkreten
kanonischen Groessen werden in der spaeteren neutralen Qualifikation
gegen obige unveraenderliche Obergrenzen geprueft, nicht hier behauptet.

## Gebundene Ausgangsdateien

Die folgenden SHA-256 wurden ausschliesslich lesend erfasst. Sie binden
Quellen/Mechanik und die vorhandenen Distanzbelege; keine neue Messung.

- `tools/_s2kz_private_auditory_partial_cue_retrieval_336.py`: `58bb0f7e9265278ced70d38bfe2858081b2e2eb134753c3457e4e03ba01eb04b`.

- `tools/_s2kz_private_direct_auditory_slot_scan_baseline.py`: `8d49715c3d59fa5d5b61855a198fb472cbbf3f34a82819e026714f9933084618`.

- `tools/_s2jw_profiled_memory_coordinator.py`: `c9676ea9a740bfb82d66a91c00c559d1ff4d3759bd7bfed12c55afb9820dea81`.

- `tools/_s2jw_default_live_profile.py`: `ad5c8f607bc375daa8a6ed70134f6ed716780658a2a5e88bddb77a980da1af6f`.

- `tools/_s2jw_default_live_av_pairing.py`: `4ec7d8660bb2269f858db8a025749764b193cd3511934b9ae143bb07359958db`.

- `tools/_s2jw_profiled_memory_ledger.py`: `995c064e32dba313d6d8329ed9c661402ce77185143f2d62b95380b777da2f80`.

- `mcm_field_organism/_tspm1_private.py`: `321ce786c42edd217dc6dbf2210c495016b2babaa78d53449a13b0039965d516`.

- `mcm_field_organism/_ppb1_reference.py`: `15f1fabaa45348f067b7bf466f138d275d74f75a6e98afc05867f7b8c35d46f0`.

- `tools/_s2jx_default_live_memory_fixtures.py`: `5313888d81b946c7ca87f6cf140a04d7810fdb0ecd1eaa0650e9fc1bb1854936`.

- `reports/s2nd/seal_inventory.py`: `9f72d2a9fc9676235cf69b23ea690d25f0a782222c54393ecf5b44107f0ce91c`.

- `reports/s2nd/s2nd-source-panel-preseal-20260906-02/execution-plan.json`: `0db1fc0f64a5af76616e7652fcf9b8da3bfb6fef8c9e60fa0870a4e49425df4e`.

- `reports/s2nd/s2nd-receptor-materialization-20260906-01/result.json`: `05981df7575b2833af35f62b8e194a33851ed855fe134fc39fc79a85aa1729f0`.

- `reports/s2nd/s2nd-retention-loss-corpus-comparison-20260906-01/recording.json`: `42478137e99159769da0bc09418e75609ab85a15346c5a07cbd0cebbc8800ce9`.

## Naechster freizugebender Schritt

Nur dieser Vertrag wird versioniert. Danach gegebenenfalls kleine private
Anbindung und neutrale Qualifikation, noch keine Hauptgeschichten.
Ein einmaliger realer Transferlauf benoetigt anschliessend eigene Freigabe.
S2-NC und S2-ND werden weder wiederholt noch neu bewertet.

WEITER: Am besten geht es jetzt mit der Analystenpruefung dieses einzelnen
Memory-Transfervertrags und danach gegebenenfalls der begrenzten privaten
Implementierungsfreigabe weiter; keine Produktumstellung.
