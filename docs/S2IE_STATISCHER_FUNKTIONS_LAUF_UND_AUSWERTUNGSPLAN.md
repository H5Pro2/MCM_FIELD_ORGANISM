# S2-IE - Statischer Funktions-, Lauf- und Auswertungsplan

## Status

`S2IE_STATIC_REAL_MEMORY_STATUS_PLAN_BOUND_ONE_SOURCE_OVERBINDING_TO_CORRECT`

S2-IE bindet einen endlichen spaeteren Funktionslauf fuer alle fuenf
qualifizierten S2-IC-Statuswerte aus tatsaechlich fortgeschriebenen privaten
Memory-Zustaenden. Dieser Schritt implementiert und importiert nichts. Es
wurden keine Rezeptor-, Speicher-, Projektions-, Signal-, Baseline- oder
Testfunktionen ausgefuehrt.

Geprueft werden ausschliesslich:

```text
CONSISTENT
CONFLICT
SINGLE_SOURCE
NO_CONTEXT
NO_APPLICABLE_CONTEXT
```

Es gibt keine Auswahl, Rangfolge, Verschmelzung, Maskenfuellung oder Nutzung
eines Gewinners. S2-IC und die unabhaengige Direktbaseline beschreiben nur den
gleichzeitig vorliegenden Zustand von `A_RECENT` und `B_STABLE`.

## Notwendige Quellenkorrektur vor Implementierung

S2-ID qualifiziert die Signallogik. Der statische Abgleich mit dem realen
S2-HY-Pfad zeigt jedoch eine zu enge Integrationspruefung in O1:

```text
bundle.probe_digest == masked_signal_probe.probe_digest
```

Diese Gleichheit ist fuer den realen Kontextpfad falsch. S2-HY bindet
nachweislich zwei getrennte Rollen:

- eine vollstaendige audiovisuelle Kontextabrufprobe, aus der S2-FS, S2-GC
  und S2-GI ihre Befunde bilden;
- eine spaetere maskierte visuelle Signalprobe, gegen die S2-IC die bereits
  vorhandenen A/B-Kandidaten auf sichtbare Anwendbarkeit prueft.

Die gespeicherten S2-HY-Belege zeigen unterschiedliche Digests fuer beide
Rollen. Das ist beabsichtigt und kein Quellenbruch.

Vor einer S2-IE-Implementierung ist deshalb eng zu korrigieren:

```text
entfernen:
bundle.probe_digest == masked_signal_probe.probe_digest

beibehalten:
signal_input.probe_digest == masked_signal_probe.probe_digest
signal_input.bundle_digest == two_area_bundle.bundle_digest
two_area_bundle.probe_digest == context_retrieval_probe_digest
```

`context_retrieval_probe_digest` wird im Lauf- und Fallbeleg separat
ausgewiesen. Der S2-IC-Eingabedigest bindet weiterhin die maskierte Probe und
das vollstaendige Bundle; der Bundledigest bindet transitiv dessen
Kontextabrufprobe. Es wird kein Digest nachtraeglich gleichgesetzt und kein
neues Funktionsfeld benoetigt.

S2-ID bleibt als Logikqualifikation gueltig. Vor einem realen Lauf ist fuer
diese einzelne Quellenkorrektur eine fokussierte Qualifikation mit
ungleichen, aber jeweils korrekt gebundenen Probe-Digests erforderlich.

## Gebundene Rezeptorquellen

### Konfliktgeometrie

S2-IE verwendet die bestaetigte S2-HY-Geometrie erneut als Fixturequelle,
nicht deren Ergebnisdateien:

```text
V0 = (1,0,0,1,1,0,0,1,1,0,0,1,1,0,0,1,1,0)
V1 = (1,1,0,0,1,0,0,1,1,0,0,1,1,0,0,1,1,0)

Q0 = (1,127/255,0,128/255,1,0,0,1,1,0,0,1,1,0,0,1,1,0)
Q1 = (1,128/255,0,127/255,1,0,0,1,1,0,0,1,1,0,0,1,1,0)
```

Alle vier Wertefolgen entstehen aus real erzeugbaren `uint8`-Blockbildern.
V0 und V1 unterscheiden sich nur an den spaeter maskierten Positionen 1 und
3. Die bestaetigten Abstaende und Schwellen bleiben unveraendert:

```text
d(V0,V1) = 255/2295
d(Q0,V0) = d(Q1,V1) = 127/2295
d(Q0,V1) = d(Q1,V0) = 128/2295
tau_visuell = 132/2295 = 44/765
```

Die auditiven Zustaende `M0`, `M1` und `MQ` bleiben die gebundenen
synthetischen auditiven Rezeptorzustaende aus S2-HS:

```text
d(M0,M1) = 1/4
d(MQ,M0) = d(MQ,M1) = 1/8
tau_auditiv = 1/5
```

### Erhaltungs- und Vergessensgeometrie

Fuer `CONSISTENT`, `SINGLE_SOURCE` und `NO_CONTEXT` werden ausschliesslich
die elf bereits statisch gebundenen S2-FU-P1-bis-P11-Fixtures verwendet:

- auditive 4-von-8-Masken, paarweise Mindestdistanz `2/8 = 0.25`;
- visuelle `uint8`-Blockbilder mit drei Werten 210 und drei Werten 30;
- visuelle Mindestdistanz `180/765`;
- alle paarweisen Distanzen liegen oberhalb der nativen Schwellen `1/5`.

IDs und Fallnamen bleiben Evaluationsmetadaten. Speicher und Signal erhalten
nur die real erzeugten Rezeptorwerte und die gebundenen Quellenbelege.

### Sichtkonfliktproben

Fuer `NO_APPLICABLE_CONTEXT` werden zwei spiegelbildliche reale
Signalproben `Z0` und `Z1` gebunden:

- `Z0` entspricht der gemeinsamen sichtbaren V0/V1-Geometrie, aber der erste
  sichtbare `uint8`-Block besitzt 254 statt 255;
- `Z1` entspricht derselben Geometrie, aber der sichtbare Nullblock an
  Position 2 besitzt 1 statt 0;
- alle maskierten Positionen werden anschliessend kanonisch durch `None`
  ersetzt;
- beide Proben widersprechen V0 und V1 an exakt einer sichtbaren Position;
- Zielwerte und erwartete Status gelangen weder in Probe noch Signal.

Die exakte Gleichheitspruefung der sichtbaren Positionen macht beide
Kandidaten gueltig vorhanden, aber nicht anwendbar. Z0 und Z1 werden nicht als
Kontextabrufprobe verwendet.

## Sechs reale Memory-Geschichten

Jede Geschichte beginnt mit einem getrennten frischen S2-FS-Composite-
Zustand, eigener Ownerkette und eigenen Zeitfenstern. Eine Formation erhaelt
denselben rezeptorisch erzeugten AV-Zustand in B4 und TSPM-1.

| Geschichte | Expositionsfolge | Schritte | Zweck |
| --- | --- | ---: | --- |
| `h-c` | P1, P1, P1, P1 | 4 | gleicher aktueller und stabiler Inhalt |
| `h-x0` | V1/M1 viermal, danach V0/M0 | 5 | A=V0, B=V1 |
| `h-x1` | V0/M0 viermal, danach V1/M1 | 5 | A=V1, B=V0 |
| `h-sa` | P11 einmal | 1 | nur A vorhanden |
| `h-sb` | P1 viermal, danach P2 bis P10 je einmal | 13 | nur B fuer P1 vorhanden |
| `h-n` | P11 einmal, danach P2 bis P10 je einmal | 10 | P11 vollstaendig vergessen |

Gesamt: exakt `38` atomare Composite-Formationen.

### Erreichbarkeitsinvarianten

`h-c`:

- vier P1-Expositionen erzeugen drei PPB-Aufrufe und Slow-Support 3;
- der vierte B4-Eintrag und der stabile Slow-Prototyp tragen denselben
  visuellen Inhalt;
- eine P1-Vollprobe liefert A und B gleichzeitig als anwendbare Kandidaten.

`h-x0` und `h-x1`:

- die ersten vier Expositionen stabilisieren B bei Support 3;
- die fuenfte audiovisuelle Exposition erzeugt wegen der auditiven Distanz
  `1/4 > 1/5` einen getrennten aktuellen A-Inhalt;
- B bleibt unveraendert stabil;
- Q0 beziehungsweise Q1 ruft beide Rollen innerhalb der nativen Schwellen ab.

`h-sa`:

- eine P11-Exposition erzeugt B4-Recent und Fast, aber keinen PPB-Aufruf;
- P11 ist in A anwendbar; B ist exakt `ABSENT_VALID`.

`h-sb`:

- vier P1-Expositionen stabilisieren P1 bei Slow-Support 3;
- neun einmalige, paarweise getrennte P2-bis-P10-Distraktoren verdraengen P1
  vollstaendig aus B4 und lassen die P1-Fast-Spur nach der gebundenen
  Acht-Expositionsgrenze ablaufen;
- keiner der Distraktoren wird konsolidiert;
- eine P1-Vollprobe liefert A als `ABSENT_VALID` und B als stabilen Treffer.

`h-n`:

- P11 wird nur einmal aufgenommen und daher nicht konsolidiert;
- neun einmalige P2-bis-P10-Distraktoren entfernen P11 aus B4 und Fast;
- eine P11-Vollprobe liefert fuer A und B jeweils `ABSENT_VALID`.

Fehlt eine dieser Erreichbarkeitsinvarianten, ist der Lauf methodisch
`NOT_EVALUABLE`; daraus folgt kein negativer Signal- oder Memory-Befund.

## Acht Funktionsfaelle

Jeder Fall verwendet genau eine vollstaendige Kontextabrufprobe, ein daraus
erzeugtes S2-GC-/S2-GI-Bundle und eine getrennte maskierte Signalprobe.
Signalgeber und Direktbaseline erhalten bytegleich dieselbe maskierte Probe
und dasselbe Bundle, aber getrennte Input- und Ownerformen.

| Fall | Geschichte | Kontextabruf | Signalprobe | A-Lage | B-Lage | Sollstatus |
| --- | --- | --- | --- | --- | --- | --- |
| `c01` | h-c | P1 voll | P1 maskiert | anwendbar P1 | anwendbar P1 | `CONSISTENT` |
| `c02` | h-x0 | Q0/MQ voll | Q0 maskiert | anwendbar V0 | anwendbar V1 | `CONFLICT` |
| `c03` | h-x1 | Q1/MQ voll | Q1 maskiert | anwendbar V1 | anwendbar V0 | `CONFLICT` |
| `c04` | h-sa | P11 voll | P11 maskiert | anwendbar P11 | abwesend | `SINGLE_SOURCE` |
| `c05` | h-sb | P1 voll | P1 maskiert | abwesend | anwendbar P1 | `SINGLE_SOURCE` |
| `c06` | h-n | P11 voll | P11 maskiert | abwesend | abwesend | `NO_CONTEXT` |
| `c07` | h-x0 | Q0/MQ voll | Z0 maskiert | Sichtkonflikt V0 | Sichtkonflikt V1 | `NO_APPLICABLE_CONTEXT` |
| `c08` | h-x1 | Q1/MQ voll | Z1 maskiert | Sichtkonflikt V1 | Sichtkonflikt V0 | `NO_APPLICABLE_CONTEXT` |

Damit werden alle asymmetrischen Konstellationen gespiegelt:

- `CONFLICT`: A=V0/B=V1 und A=V1/B=V0;
- `SINGLE_SOURCE`: nur A und nur B;
- `NO_APPLICABLE_CONTEXT`: beide Kandidatenbelegungen gespiegelt.

`CONSISTENT` und `NO_CONTEXT` sind bereits rollensymmetrisch. Keine Fall-ID,
Sollklasse oder erwartete Ausgabe ist Elternteil einer Ausfuehrungsoperation.

## Exakter Operations- und Ereignisumfang

Der spaetere Erfolgspfad besitzt exakt `183` Operationen. Jede Operation
erzeugt genau ein START-/RESULT-Paar; damit entstehen exakt `366` Ereignisse.

| Operationsbereich | IDs | Anzahl |
| --- | --- | ---: |
| Laufvorbereitung und Quellenmanifest | `ie-op-001..002` | 2 |
| sechs frische Historyinitialisierungen | `ie-op-003..008` | 6 |
| h-c: vier Rezeptor-/Formationpaare | `ie-op-009..016` | 8 |
| h-x0: fuenf Rezeptor-/Formationpaare | `ie-op-017..026` | 10 |
| h-x1: fuenf Rezeptor-/Formationpaare | `ie-op-027..036` | 10 |
| h-sa: ein Rezeptor-/Formationpaar | `ie-op-037..038` | 2 |
| h-sb: dreizehn Rezeptor-/Formationpaare | `ie-op-039..064` | 26 |
| h-n: zehn Rezeptor-/Formationpaare | `ie-op-065..084` | 20 |
| sechs Bloecke aus Vollprobenrezeptor, S2-FS-read-only, S2-GC, S2-GI und Historyseal | `ie-op-085..114` | 30 |
| c01: Signalprobenrezeptor bis Fallbeleg | `ie-op-115..121` | 7 |
| c02 | `ie-op-122..128` | 7 |
| c03 | `ie-op-129..135` | 7 |
| c04 | `ie-op-136..142` | 7 |
| c05 | `ie-op-143..149` | 7 |
| c06 | `ie-op-150..156` | 7 |
| c07 | `ie-op-157..163` | 7 |
| c08 | `ie-op-164..170` | 7 |
| Ausfuehrungsevidenz und Evaluationsbindung | `ie-op-171..172` | 2 |
| acht Fallevaluationen | `ie-op-173..180` | 8 |
| Aggregat, Terminalvorbereitung, Completion | `ie-op-181..183` | 3 |
| **Gesamt** |  | **183** |

Jeder siebenstufige Fallblock besitzt exakt:

```text
1 SIGNAL_PROBE_RECEPTOR
1 MASKED_SIGNAL_PROBE_PROJECT
1 SIGNAL_INPUT_BIND
1 SIGNAL_INVOKE
1 BASELINE_INPUT_BIND
1 BASELINE_INVOKE
1 CASE_EVIDENCE_SEAL
```

Die Ereignisindizes sind deterministisch:

```text
Operation n -> START 2*n-1 -> RESULT 2*n
```

Scheitert Erfolgsoperation n nach Laufreservierung, folgen ausschliesslich
`FAILURE_EVIDENCE_SEAL` und `NOT_EVALUABLE_PUBLISH`. Der maximale Fehlerpfad
enthaelt damit `185` Operationen und `370` Ereignisse. Vor Reservierung ist
nur `START_BLOCKED` ohne Laufverzeichnis zulaessig.

## Funktions- und Ressourcenbudgets

Gebunden sind:

```text
reale visuelle Rezeptoranalysen: 38 Bildung + 6 Vollprobe + 8 Signalprobe = 52
Composite-Formationen: 38
S2-FS-read-only-Proben: 6
S2-GC-Projektionen: 6
S2-GI-Projektionen: 6
maskierte Probeprojektionen: 8
S2-IC-Signalaufrufe: 8
Direktbaselineaufrufe: 8
```

Unter den unveraenderten S2-FS-Grenzen ergibt sich:

```text
Formations-Schreibwoerter: 38 * 617 = 23446
Formations-Distanzterme:   38 * 468 = 17784
Formations-Kontrollterme:  38 * 54  = 2052

Probe-Schreibwoerter:       6 * 14  = 84
Probe-Distanzterme:         6 * 468 = 2808
Probe-Kontrollterme:         6 * 48  = 288

S2-FS gesamt: 23530 Schreibwoerter, 20592 Distanzterme, 2340 Kontrollterme
```

Die acht Statuspfade besitzen in Reihenfolge c01 bis c08 die `(P,K)`-Paare:

```text
(2,2), (2,2), (2,2), (1,1), (1,1), (0,0), (2,0), (2,0)
```

Damit gelten je Arm ueber alle acht Aufrufe exakt:

```text
Eingabevalidierungen                 8
Probenpositionsvalidierungen       144
Bundlevalidierungen                  8
Bereichslookups                     16
Bereichsfindingvalidierungen        16
Kandidatenreferenzen                12
Komponentenreferenzen               12
sichtbare Vergleiche               108
Maskenprojektionen                   8
Maskenwertreferenzen                72
bereichsuebergreifende Vergleiche   27
Signalbindungsdigestpruefungen     156
neue Digestoperationen              64
logische Operationen                48
veroeffentlichte Erfolgsobjekte     24
Speicher-/Lernaufrufe                0
```

Signal und Direktbaseline erhalten dieselben Grenzen. Fuer beide Arme
zusammen werden diese Werte exakt verdoppelt. Native Laufzeit und realer
Prozessspeicher werden getrennt berichtet und duerfen keine funktionale
Arbeit ersetzen.

## Owner- und Receiptformen

### Owner

- ein Runowner: `RESERVED -> ACTIVE -> EXECUTION_SEALED -> EVALUATING ->
  COMPLETING -> CONSUMED|FAILED`;
- sechs getrennte Historyowner: `FRESH -> ACTIVE -> SEALED|FAILED`;
- 38 Formationowner und sechs Probeowner gemaess S2-FS;
- sechs S2-GC- und sechs S2-GI-Projektionsowner;
- je Fall ein Fallowner sowie getrennte S2-IC-Owner fuer Signal und
  Direktbaseline;
- ein Evaluationowner, der erst aus `EvaluationRunBinding` entsteht.

Kein Owner ist wiederverwendbar. Signal und Baseline teilen weder Owner noch
Ergebnis, obwohl sie dieselben Funktionsquellen erhalten.

### Wiederverwendete kompakte Belege

- `ReceptorReceipt`: maximal 2765 Byte;
- `FormationReceipt`: maximal 2801 Byte;
- `S2FSReadOnlyReceipt`: maximal 2048 Byte;
- `S2GCProjectionReceipt`: maximal 3174 Byte bei `NOT_REQUESTED`;
- `S2GIProjectionReceipt`: maximal 2978 Byte;
- S2-IC-Eingabe, Anwendbarkeitsbefunde, Vergleich, Ledger, Ergebnis, Owner und
  Receipts exakt unter den in S2-IB gebundenen Grenzen.

### Neue S2-IE-Belege

`S2IEExecutionPlan` bindet Lauf-ID, Quellenhashes, sechs Historien, acht
Fallquellen, Registry, Operations-/Ereignisbudgets, Funktionsbudgets und
Plandigest. Es enthaelt keine Sollstatus.

`S2IESignalProbeReceipt` bindet Fall, reales Bildbytesdigest, Rezeptorreceipt,
18 vollstaendige visuelle Werte, feste sichtbare/maskierte Positionen,
maskierten Probedigest und Quellendigest. Grenze: 1536 Byte.

`S2IECaseEvidence` bindet Kontextabrufprobedigest, S2-GI-Bundledigest,
maskierten Signalprobedigest, Signal- und Baselineinput, beide Owner,
Anwendbarkeits-, Vergleichs-, Ledger-, Ergebnis- und Receiptdigests sowie
identische Memory-Vor-/Nachzustandsdigests. Grenze: 3584 Byte.

`S2IEExecutionEvidencePackage` bindet Registrydigest, 366 Ereignisse ueber
Anzahl und finalen Journaldigest, sechs Historyseals, acht Fallbelege und den
Ausfuehrungswurzel-Digest, aber keine Sollwerte. Grenze: 3072 Byte.

`S2IEEvaluationRunBinding` ist der erste Beruehrungspunkt von vollstaendiger
Ausfuehrungsevidenz und unabhaengigem `EvaluationPlanSeal`. Grenze: 1024 Byte.

`S2IEEvaluationFinding` bindet beobachteten und erwarteten Status,
Signal-/Baselinegleichheit, Symmetrie, Read-only-Befund und methodische
Gueltigkeit. Grenze: 1536 Byte.

`S2IEAggregateFinding`, `S2IETerminalFinding` und
`S2IECompletionMarker` besitzen Grenzen 1280, 1024 und 1024 Byte.
START-/RESULT-Ereignisse bleiben unter 1536 Byte. Fehlerbeleg und
`NOT_EVALUABLE`-Marker bleiben jeweils unter 1024 Byte. Keine Form darf 4095
Byte erreichen oder vollstaendige In-Memory-Zustaende erneut einbetten.

## Digestgraph und Wurzeltrennung

```text
ExecutionPlan + Quellen
-> Historyinitialisierung
-> ReceptorReceipt
-> FormationReceipt
-> finaler Composite-Zustand
-> Kontextabrufprobe / S2-FS-read-only
-> S2-GC
-> S2-GI
-> Historyseal

reale Signalprobe
-> MaskedSignalProbeReceipt

Historyseal + S2-GI-Bundle + MaskedSignalProbe
-> S2-IC-Signalinput + eigener Owner
-> Signalresultat

dieselben Funktionsquellen
-> Baselineinput + getrennter Owner
-> Baselineresultat

beide Resultate
-> CaseEvidence
-> ExecutionEvidencePackage

unabhaengiger EvaluationPlanSeal + ExecutionEvidencePackage
-> EvaluationRunBinding
-> acht Findings
-> Aggregat
-> Terminal
-> CompletionMarker
```

Der Evaluationsplan ist vor dem Lauf versiegelt, aber kein Elternknoten des
Ausfuehrungspfads. Fallnamen und Sollstatus existieren ausschliesslich in der
Evaluationswurzel. Kein Digest bindet sich selbst oder einen spaeteren
Digest.

## Auswertung und Entscheidungen

`NOT_EVALUABLE` gilt bei:

- nicht erreichbarer gebundener Memory-Lage;
- Quellen-, Probe-, Owner-, Digest-, Reihenfolge-, Registry-, Ledger-,
  Read-only-, Ereignis-, Aufzeichnungs- oder Terminalbruch;
- Vermischung von Kontextabrufprobe und maskierter Signalprobe;
- Teilausgabe, Wiederverwendung oder unvollstaendiger Beweiskette.

Bei vollstaendig gueltiger Beweiskette ist die Funktion falsifiziert, wenn:

- einer der fuenf Statuswerte nicht nach seiner exakten S2-IB-Regel entsteht;
- Signal und Direktbaseline voneinander abweichen;
- eine A/B-Spiegelung den Status statt nur die Rollenbelege aendert;
- ein gueltiger Fehlerzustand als regulaerer Status erscheint;
- eine Auswahl, Rangfolge, Verschmelzung oder Zustandsaenderung entsteht.

Ein vollstaendiger, aber funktional abweichender Lauf bleibt `COMPLETE` mit
Falsifikationsbefund. Nur technische oder methodische Verletzungen ergeben
`NOT_EVALUABLE`.

Der maximal zulaessige positive Befund lautet:

```text
S2IE_REAL_TWO_AREA_STATUS_FUNCTION_VALID_DIRECT_COMPARISON_EXPLAINS
```

Er bestaetigt nur, dass real gebildete A/B-Memory-Zustaende transparent als
Konsistenz, Konflikt, Einzelquelle, Abwesenheit oder Nichtanwendbarkeit
beschrieben werden koennen. Er belegt keine automatische Kontextwahl, keine
neue Memory-Mechanik und keine Feldwirkung.

## Freigabegrenze

S2-IE ist als statischer Funktions-, Lauf- und Auswertungsplan gebunden.
Noch gesperrt bleiben:

- die enge S2-IC-Quellenkorrektur;
- Fixture-, Runner-, Recorder- und Verifikatorimplementierung;
- Tests, Qualifikation und jeder reale Lauf;
- automatische Auswahl, API-, Snapshot- und Feldintegration.

Der naechste konkrete Schritt ist kein weiterer allgemeiner Vertragsaudit,
sondern die ausdrueckliche Freigabe der einen Quellenkorrektur und der
begrenzten privaten S2-IE-Fixture-/Laufimplementierung. Vor einem Hauptlauf
muss die korrigierte Zwei-Proben-Bindung fokussiert neutral qualifiziert sein.
