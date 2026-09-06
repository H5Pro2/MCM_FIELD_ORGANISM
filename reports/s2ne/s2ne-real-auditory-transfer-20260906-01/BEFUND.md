# S2-NE: Einmaliger realer auditiver Memory-Transfer

Lauf-ID: `s2ne-real-auditory-transfer-20260906-01`.
Quellenstand: Commit `e5976d0`.
Technischer Abschluss und unabhaengige Verifikation: **RECORDING_COMPLETE**.
Getrennte Funktionsauswertung: **CONFIRMED**, alle **13/13** gebundenen
Fallvorhersagen einschliesslich beider Direktbaselines erfuellt.

## Ausfuehrungsbindung

Genau ein `run_main_once`, danach genau ein `verify_main_once`, erst danach
genau ein `evaluate_main_once`. Aufruf und Ablaufbindung liegen unveraendert
in `../run_real_transfer_once.py`, Vorregistrierung und Abschluss in
`../s2ne-real-auditory-transfer-20260906-01-preregistration.json` sowie
`../s2ne-real-auditory-transfer-20260906-01-outcome.json`.

```text
C:\Python314\python.exe -B -m reports.s2ne.run_real_transfer_once
```

Exit-Code `0`. Keine Tests, Rezeptorvorlaeufe, Wiederholung oder
Parameterwechsel. Neues Ergebnisverzeichnis war vor dem Aufruf nicht
vorhanden. Das Gate wurde ausschliesslich im Arbeitsspeicher fuer den
Hauptaufruf geoeffnet und anschliessend in `finally` auf `False` gesetzt.
Auch das unveraenderte Gate des qualifizierten Vergleichsmoduls bleibt
`False`. Die qualifizierten Quelldateien wurden nicht veraendert.

Unveraenderte Quellen: Audio s001/s004/s007..s010 aus S2-ND sowie visuell
X und D1..D9 aus S2-JX. Jedes Ereignis erhielt ein neues natives Zeitfenster;
Payloadhash vor jeder Analyse geprueft. Keine Rohpayloadablage, keine
historischen Memoryzustaende geladen. Referenz bleibt historisches
`sum(...)/24`, nicht `statistics.mean`. Alternative veraendert nur die
A-Anwendbarkeit zu `max(...) <= 0.2`; Slow und alle Aufloesungen bleiben gleich.

## Tatsaechlicher Umfang

| Groesse | Beobachtet | Grenze |
| --- | ---: | ---: |
| Frische Bildungsgeschichten plus Nullzustand | 5 + 1 | 5 + 1 |
| Ereignisse / Formationen / Teilhinweise | 33 / 20 / 13 | 33 / 20 / 13 |
| Audio- / visuelle Analysen | 33 / 20 | 33 / 20 |
| Erzeugte Rezeptorwerte | 7.344 | 7.344 |
| Abrufbelege einschliesslich Baselines | 52 | 52 |
| Slotbesuche | 1.040 | 1.040 |
| Banddifferenzen | 5.280 | 24.960 |
| Interne 48-Werte-Gleichheitsvergleiche | 1.344 | 2.496 |
| Abruf-Wertvergleiche insgesamt | 6.624 | 27.456 |
| Logische Abrufoperationen | 728 | 728 |
| Profilabgeleitetes Formations-L1-Limit | 71.040 | 71.040 |
| Atomarer kanonischer Gesamtbeleg | 1.546.079 Byte | 4.194.304 Byte |

Die Verifikation besitzt die gesonderte Reserve von maximal 27.456
Wertvergleichen und fuehrte keinen Memory- oder Abrufaufruf aus. Ihre
Zaehler bestaetigen die 52 vollstaendigen Abrufbelege. Die bestehende
Einzelbeleggrenze von weniger als 32.768 Byte wurde eingehalten.
Das Formations-L1-Limit ist eine profilabgeleitete Obergrenze, keine
Behauptung, dass saemtliche 71.040 Terme ausgefuehrt wurden.

## Alle 13 Entscheidungen

T/E sind ausschliesslich nachgelagerte Auswertungsnotation fuer die
gebundenen Quellen. `A(T)` und `B(T)` bezeichnen `ADMIT_SINGLE_CONTEXT`
aus `A_RECENT` beziehungsweise `B_STABLE_AUDITORY`. `A(E1)` ist hier
eine falsche Zulassung des Konkurrenzinhalts.

| Fall | Geschichte / Cue | Referenz | Alternative | Vorhersage |
| --- | --- | --- | --- | --- |
| q01 | h01 / exakt | A(T) | A(T) | erfuellt |
| q02 | h01 / Pegel | A(T) | A(T) | erfuellt |
| q03 | h01 / Frequenz | A(T) | A(T) | erfuellt |
| q04 | h01 / Spektral | A(T) | A(T) | erfuellt |
| q05 | h02 / exakt | interne Mehrdeutigkeit | A(T) | erfuellt |
| q06 | h02 / Pegel | interne Mehrdeutigkeit | A(T) | erfuellt |
| q07 | h02 / Frequenz | interne Mehrdeutigkeit | A(T) | erfuellt |
| q08 | h02 / Spektral | interne Mehrdeutigkeit | A(T) | erfuellt |
| q09 | h03 / Ziel entfernt | A(E1), falsch | keine Anwendbarkeit | erfuellt |
| q10 | h04 nach 13 / exakt | interne Mehrdeutigkeit | B(T) | erfuellt |
| q11 | h04 nach 14 / exakt | interne Mehrdeutigkeit | oeffentliche A/B-Mehrdeutigkeit | erfuellt |
| q12 | h05 / exakt | interne Mehrdeutigkeit | interne Mehrdeutigkeit | erfuellt |
| q13 | h06 / Nullzustand | kein Kontext | kein Kontext | erfuellt |

Die maschinenlesbaren Originalstatus, Kandidatendigests und Vorhersagen
stehen in `evaluation.json`; die vollstaendigen Treffermengen aller drei
Banken in `recording.json`. Beide Regeln stimmen bei **13/13** Faellen mit
ihrer jeweiligen unabhaengigen Direktbaseline ueberein, insgesamt **26/26**
Arm-/Baselinevergleiche.

Fachlich richtige eindeutige Hypothesen in den neun positiven Abruffaellen
q01..q08/q10: Referenz **4/9**, Alternative **9/9**. Davon sind vier Gewinne
eindeutige A-Treffer unter Konkurrenz und einer ein B-Treffer nach A-Verlust.
Fehlzulassungen ueber alle Faelle: **1/13 -> 0/13**. In der einzigen
Zielentfernungskontrolle q09: **1/1 -> 0/1**. Das ist keine allgemeine
Unbekanntheitserkennung.

Enthaltungen insgesamt: Referenz **8/13**, Alternative **4/13**.
Die Alternative enthaelt in allen vier gebundenen Kontrollen q09/q11/q12/q13.
Oeffentliche A/B-Mehrdeutigkeit in q11 wird trotz gueltigem B-Inhalt nicht
durch einen B-Vorrang aufgeloest. Keine Hypothese wird angewendet.

## Erhaltung und Verlust

N: alle betreffenden q01..q08; D: davon zuvor korrekt eindeutige
Referenz-A-Treffer; R: erhaltene Treffer; L: Verluste. Immer `D = R + L`.
Diese Zahlen sind getrennt von den fuenf neuen Treffern; keine Verrechnung.

| Hinweis / Belegung | Tatsaechliche Rezeptorvariation | N | D | R | L |
| --- | --- | ---: | ---: | ---: | ---: |
| Exakt / ohne Konkurrenz | bitidentisch | 1 | 1 | 1 | 0 |
| Pegel / ohne Konkurrenz | nicht bitidentisch | 1 | 1 | 1 | 0 |
| Frequenz / ohne Konkurrenz | nicht bitidentisch | 1 | 1 | 1 | 0 |
| Spektral / ohne Konkurrenz | nicht bitidentisch | 1 | 1 | 1 | 0 |
| Exakt / Konkurrenz | bitidentisch | 1 | 0 | 0 | 0 |
| Pegel / Konkurrenz | nicht bitidentisch | 1 | 0 | 0 | 0 |
| Frequenz / Konkurrenz | nicht bitidentisch | 1 | 0 | 0 | 0 |
| Spektral / Konkurrenz | nicht bitidentisch | 1 | 0 | 0 | 0 |

Ohne Konkurrenz insgesamt **4/4/4/0**, davon variierte Hinweise **3/3/3/0**.
Mit Konkurrenz **4/0/0/0**: ausdruecklich **ERHALTUNG_NICHT_GEPRUEFT**.
Der Gewinn unter Konkurrenz ersetzt keinen Erhaltungsnachweis mit positivem
Ausgangsnenner. q10 ist ein B-Zugriff, kein erhaltener A-Treffer.

## Tatsaechliche Inventare und Uebergaenge

Alle **25/25** getrennten Inventarpruefungen sind erfuellt: B4, Fast, Audio-
und Visual-Slow fuer h01..h06 sowie Zielverlust aus A vor q10.
Nicht genannte Slots sind frei. Reihenfolgen sind physische Slotreihenfolgen.

| Zustand | B4 | Fast | Slow je Modalitaet |
| --- | --- | --- | --- |
| h01 nach 1 | T | T, Support 1 | leer |
| h02 nach 2 | T,E1 | T/1,E1/1 | leer |
| h03 nach 1 | E1 | E1/1 | leer |
| h04 nach 13, vor q10 | E6,E7,E8,E9,E1,E2,E3,E4,E5 | E9/1,E7/1,E8/1 | S0, Support 3 |
| h04 nach 14, vor q11 | E6,E7,E8,E9,T,E2,E3,E4,E5 | E9/1,T/1,E8/1 | S0, Support 3 |
| h05 nach 2 | T,T | T, Support 2, eine Konsolidierung | S0, Support 1, instabil |
| h06 | leer | leer | leer |

Pro Modalitaet genau vier PPB-Uebergaenge, jeweils Slot `.000`:

| Ereignis | Audio | Video |
| --- | --- | --- |
| h04-e02 | CREATED, Support 1 | CREATED, Support 1 |
| h04-e03 | MATCHED, Support 2 | MATCHED, Support 2 |
| h04-e04 | MATCHED, Support 3 | MATCHED, Support 3 |
| h05-e02 | CREATED, Support 1 | CREATED, Support 1 |

Alle anderen 16 Formationen haben in beiden PPB-Banken `NO_UPDATE`.
Insbesondere keine Druckverdichtung und kein weiterer Slow-Update bei
h04-e15. Alle 40 modalitaetsgetrennten Uebergangsbelege samt Pre-/Postdigests
stehen in `verification.json`.

Audio-Vollvektor-Digests der h04-Uebergangskette:

```text
CREATED/s1  59b59d9b6c5b86472ee39b289ef52696c6fe20c8eb7ae996f1a00094621642ce
MATCHED/s2  20de5c5ca3d1ffc527cb8c3a2ab301126ad93cfbd35acb577e091e1392fd7e0a
MATCHED/s3  73acc50c713e33be33c78ac7f2c85f021f9885ef541e021558ff4ef6f07bf82a
```

Audio-Enddigest der 24 Hypothesenwerte:
`1435c1b16229b8e17f412e7ea73b2e29e0cf1f67037decb45a6e869f0b13ba29`.
Visueller Vollvektordigest nach allen drei Uebergaengen:
`46ee578128cfde13f300b2d03bcbd2df7a57d278174abb2d3a2a22c2c6d5855b`.
Visueller Maskenprojektionsdigest:
`bafd0a9a31ea5eacbfbe484f96288c28ebb60de330c145acf59f8450106d949a`.
Die unveraenderte Binary64-Uebergangskette ist damit gebunden; gerade der
auditive Endprototyp ist nicht faelschlich auf den Ursprungsdigest gesetzt.

h04 wird ueber q10 hinweg fortgesetzt: q10 Pre-/Postdigest und Prestate von
h04-e15 sind identisch:
`246a0c9340e242059848efc7b2e6c478df4ad3d47c6e4d109f02d401d80634b3`.
Nach Formation 14 bleibt q11 read-only auf
`f94e15f557166f6c67eb6f996756302ca9e0aacf45d578a738736b3b09416f6e`.
Alle **13/13** Cue-Zustaende und **52/52** Arm-Pre-/Postbindungen sind
unveraendert. Die 20 Formationen waren dagegen bestimmungsgemaess schreibend.

## Integritaet und Aussagegrenze

Alle 39 vorgebundenen Quell-/Qualifikations-/Test-/Aufruferdateien sind vor
und nach dem Lauf hashgleich. Der Gesamtbeleg blieb waehrend der einmaligen
Verifikation bytegleich. Historische Belege und Bootstrap blieben unberuehrt.

| Datei | SHA-256 |
| --- | --- |
| recording.json | c95b1dd04d61a1153fa7a8d89bfea5f297b5305b8551ef17fcd2304160b11f6d |
| verification.json | 7d38c2f6eb41e8318cd55c46c1b896e6fa23378b7eca6eda76b3b3bb438b7714 |
| evaluation.json | 9c92c37bdafc1d37d7105ebc1212dbf9cc0732b33c533a3cdb3d1a1301941f65 |

Beobachtet ist ein begrenzter Transfer der strengeren auditiven
A-Anwendbarkeit auf echte Memoryzustaende mit Erhaltung ohne Konkurrenz,
korrekten neuen Treffern und einer verhinderten Fehlzulassung.
Die direkte Baseline erklaert den Effekt vollstaendig. Bereits untersuchte
Quellen wurden wiederverwendet: keine unabhaengige Generalisierung, keine
allgemeine Robustheit und weiterhin kein Erhaltungsnachweis unter Konkurrenz.
Keine Produktumstellung, Feld-/Runtimeintegration oder Hypothesenanwendung.

WEITER: Am besten geht es jetzt mit der Analystenbewertung dieses
abgeschlossenen Transferbefunds und der verbleibenden Erhaltungsgrenze
unter Konkurrenz weiter; eine Produktumstellung bleibt separat zu entscheiden.
