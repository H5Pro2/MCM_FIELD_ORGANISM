# K2/F3 P2: Vorregistrierung des ersten Geschichtstraeger-Versuchs

Stand: 2026-08-06

Status:

- kontrollierte synthetische Audio-Video-Testwelt gebunden;
- zwei getrennte Vorgeschichten und eine einmal frisch reduzierte Probe;
- Parameter aus Lauf 188 unveraendert;
- M-Interventionen vor dem Ergebnis festgelegt;
- kein Memory-, Organisations-, Topologie-, Semantik- oder KI-Claim.

## 1. Forschungsfrage

Kann eine aus normalem kontrolliertem AV-Weltkontakt entstandene
M-Konfiguration nach exakter Angleichung von S und H die Aufnahme einer fuer
beide Geschichtsarme byteidentischen reduzierten Probe kausal veraendern?

Der Versuch prueft nur die Evidenzstufe eines langsamen kausalen
Geschichtstraegers. Er prueft noch keine Praegung, Loesung, Wiederpraegung
oder verteilte Nichtseparierbarkeit.

## 2. Gebundene Testwelt

Verwendet wird unveraendert
`controlled_history_holdout_world_family()`:

```text
same world digest:    3b410299a1f0e23a4bbb45578a538878a481ec31e5ae025f0b0311074a1c0b06
changed world digest: a4009b3e1845b46169d07bd1bb1b088d3a5dbf48107776e290cd4543d1b85d3c
clock:                 organism.mcm_f3_history
ticks_per_second:      1000000
history interval:      [0, 3000000)
probe interval:        [3000000, 4000000)
```

Reduzierte Eingangsfolgen:

```text
same history digest:    997f318cf5f43f84a9747fcd5b95e3fe4cbfce68d3d5f851f22895d70504002d
changed history digest: a263b21d6fefa93389d494cb7d298910caa6f5cfea882aacc74cfb4da4cfba53
shared probe digest:     dba4ae9b51af783ec4abe195eacaac98be94380f1e7125d6cf56f154a15cc927
history frames:          Audio 291, Video 30
probe frames:            Audio 91, Video 10
```

Die Probe wird mit einem frischen Audio- und Videorezeptor genau einmal
reduziert. Dasselbe unveraenderliche `ReceptorTimeSequence`-Objekt wird an
alle Probe-Arme uebergeben. Damit wird die Rezeptorvorgeschichte aus Lauf 187
nicht wiederholt.

## 3. Feld- und F3-Parameter

Unveraendert aus Lauf 188:

```text
S response_time_seconds: 1.0
H time_constant_seconds: 0.5
Dissipation: keine
M initial_total_mass: 1.0
lambda_sm_per_second: 1.0
kappa: 0.5
eta: 1.0
aktive Integration: 4n
Proposal-Rahmen: je ein begrenzter Rahmen fuer Geschichte und Probe
interne Ereignisausrichtung: jeder reale Rezeptorabschluss
```

Der groessere Proposal-Rahmen veraendert keine Ereigniszeit. Die transiente
F3-Runtime integriert weiterhin einzeln bis zu jedem enthaltenen
Rezeptorabschluss. Er verhindert nur einen erneuten Geometrieaufbau nach
jedem Abschluss.

## 4. Phasenordnung

```text
frisches Feld mit gleichfoermigem M
-> drei Sekunden kontrollierte Geschichte
-> Messung von S, H und M
-> externe exakte S/H-Angleichung auf Null
-> vorregistrierte M-Intervention
-> dieselbe einmal reduzierte Probe
-> Messung des vollstaendigen S/H/M-Endzustands
```

Die S/H-Angleichung und M-Interventionen sind Observerwerkzeuge. Sie werden
nicht als Organismusfunktion in die Runtime eingebaut.

## 5. Vorregistrierte Arme

Fuer `same` und `changed` werden gebildet:

```text
natural:       historisches M unveraendert
m-neutral:     M vor der Probe auf die gleichfoermige Referenz gesetzt
eta-null:      historisches M erhalten, eta nur fuer die Probe auf 0 gesetzt
m-swapped:     vollstaendige M-Konfiguration zwischen same und changed getauscht
p0:            lambda_sm = 0 waehrend Geschichte und Probe
```

Bei allen Armen sind S und H unmittelbar vor der Probe exakt Null. Der
M-Tausch veraendert keine Werte, Gesamtmenge, Geometrie oder Feldparameter.

## 6. Vorregistrierte Kontrollen

Ein enger Befund `CAUSAL_M_HISTORY_CARRIER` erfordert gleichzeitig:

1. `same` und `changed` erzeugen vor der Probe unterschiedliche M-Vektoren.
2. S und H sind vor der Probe in allen Vergleichsarmen exakt gleich.
3. Die gemeinsame Probe besitzt in allen Armen denselben Digest.
4. `natural.same` und `natural.changed` unterscheiden sich nach der Probe in
   S oder H.
5. Nach M-Neutralisierung fallen die beiden Probe-Endzustaende in S und H
   exakt zusammen.
6. Bei `eta = 0` fallen die beiden Probe-Endzustaende in S und H exakt
   zusammen.
7. Beim vollstaendigen M-Tausch wandert der jeweilige S/H-Endzustand mit der
   getauschten M-Konfiguration.
8. P0 faellt fuer beide Geschichten nach der Probe exakt zusammen.
9. M-Gesamtmenge, Nichtnegativitaet und S/H-Bereich bleiben invariant.

Scheitert eine Kontrolle, lautet die Entscheidung `TECHNICALLY_UNDECIDABLE`
oder `NO_CAUSAL_M_HISTORY_EFFECT`. Parameter, Welt und Probe werden danach
nicht angepasst und der Lauf wird nicht automatisch wiederholt.

## 7. Messungen

- S-, H- und M-Linf/L2 zwischen `same` und `changed`;
- S/H-Kontraste nach M-Neutralisierung und eta-null;
- komponentengenaue Gleichheit der beiden M-Tauschrichtungen;
- P0-Gleichheit;
- M-Gesamtmassenfehler und kleinstes M;
- Sequenz-, Feld- und Snapshotdigests.

## 8. Nichtnachweis

Auch ein vollstaendig positiver Kausalbefund belegt nur, dass M unter dieser
Kandidatenform ein aus Weltgeschichte erreichbarer, spaeter auf S/H
rueckwirkender Traeger ist. Nicht belegt sind funktionale Speicherung,
relative Feldzeitverdichtung, Praegung, Loesung, Wiederpraegung, verteilte
Nichtseparierbarkeit, Memory, Organisation, Topologie, Semantik oder KI.

## 9. Laufnummer

Der letzte nachweislich ausgefuehrte Forschungsdurchlauf ist Lauf 188. Nur
bei tatsaechlicher Ausfuehrung dieses unveraenderten Vertrags entsteht Lauf
189.
