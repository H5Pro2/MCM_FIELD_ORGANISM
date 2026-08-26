# S1-SF: Statischer gemeinsamer synchroner Vier-Knoten-Expositionssegment-, Ereignisplan- und 17-Repliken-Fixturevertrag

> **Nachtrag S1-SI:** Das ausgerichtete Feld kann bei aktuellen
> Nullkontakten nicht den vorherigen `last_distribution`-Wert behalten, weil
> `SharedMCMField` beide konstruktiv auf Wertgleichheit prueft. S1-SI bindet
> deshalb eine zeitlose Nullframe-Projektionsdistribution im ausgerichteten
> Feld und erhaelt den vorherigen Distributionsdigest im Alignreceipt. Alle
> anderen S1-SF-Werte und Planfolgen bleiben gueltig.

## Status und Umfang

S1-SF bindet erstmals die konkreten gemeinsamen Rezeptorwerte,
Intervallgrenzen, Feldzeiten, Praefixe, Alignziele und 17 Ereignisplaene der
in S1-SB korrigierten Expositionsachse.

Der Vertrag materialisiert noch kein Fixture, implementiert keinen
Orchestrator, aendert keinen Modellkern, berechnet keine Digests und fuehrt
keinen Test, keine Matrixzelle und keinen Forschungslauf aus.

Vertragsentscheidung:

```text
ONE_COMMON_SYNCHRONOUS_FOUR_NODE_SEGMENT_ALPHABET_BOUND
SEVENTEEN_CAUSALLY_ORDERED_EXPOSURE_PLANS_BOUND
EARLY_B_START_TICK_70_AND_LATE_B_START_TICK_100_PAIR_MATCHED
ALL_FOURTEEN_MODEL_ROLES_RECEIVE_THE_SAME_PUBLIC_EVENT_PER_CELL_POSITION
NO_IMPLEMENTATION_NO_TEST_NO_MATRIX_EXECUTION
```

## Gemeinsame technische Identitaeten

Alle modellwirksamen Intervalle verwenden:

| Rolle | Wert |
|---|---|
| Feldclock | `mcm.s1sf.field` |
| Quellclock | `mcm.s1sf.source` |
| Ticks pro Sekunde | `10.0` |
| Intervallbreite | `10` Ticks = `1.0` Sekunde |
| Modality | `technical-control` |
| Rezeptorgeometrie | `mcm.s1rf.receptor.4n` |
| Dock | `dock.s1rf.technical-control.4n` |
| Carrierordnung | `carrier-a, carrier-b, carrier-c, carrier-d` |
| Knotenordnung | `node-a, node-b, node-c, node-d` |

Die Feldzeit beginnt in jeder unabhaengigen Frischreplik bei Tick `0`.
Jedes modellwirksame Intervall besitzt positive Dauer und wird als
`MCMFieldStepTime` mit derselben Grenze wie seine `CommonFieldTime`
materialisiert. Es gibt ausschliesslich synchrone Intervalle.

## Ortsabbildung

Die S1-RJ/S1-RK-Abbildung bleibt unveraendert:

| Expositionsrolle | Carrier | Knoten | Vektorposition |
|---|---|---|---:|
| `B_LOCAL` | `carrier-a` | `node-a` | 1 |
| `A_FOCAL` | `carrier-b` | `node-b` | 2 |
| `D_CONTROL` | `carrier-c` | `node-c` | 3 |
| `C_REMOTE` | `carrier-d` | `node-d` | 4 |

`D_CONTROL` erhaelt in jedem Kontakt- und Probeintervall exakt `0.0`. Es
entsteht keine vierte Expositionsrolle.

## Kanonisches Kontaktalphabet

Alle Vektoren stehen in der Carrier- und Knotenordnung
`(a, b, c, d)`:

| Segmentpayload | Vektor | Dauer je Vorkommen | Zweck |
|---|---|---:|---|
| `A_CONTACT` | `(0.0, 0.5, 0.0, 0.0)` | 1 s | fokale A-Geschichte |
| `B_CONTACT` | `(0.5, 0.0, 0.0, 0.0)` | 1 s | lokale B-Geschichte |
| `C_CONTACT` | `(0.0, 0.0, 0.0, 0.5)` | 1 s | entfernte C-Geschichte |
| `PROBE_A_CONTACT` | `(0.0, 0.25, 0.0, 0.0)` | 1 s | gemeinsamer A-Readoutinput |
| `PROBE_B_CONTACT` | `(0.25, 0.0, 0.0, 0.0)` | 1 s | gemeinsamer B-Readoutinput |
| `ZERO_CONTACT` | keine Frames, `contacts=()` | 1 s | normale kontaktfreie Feldfortsetzung |

Die Bildungs- und Konkurrenzkontakte liegen mit `0.5` im Inneren des
normierten Bereichs `[-1, 1]`. Die Probe verwendet mit `0.25` die halbe
Amplitude, damit sie als gemeinsamer Readoutinput von der staerkeren
Vorgeschichte unterscheidbar bleibt. Diese Werte sind Vorregistrierung und
kein Ergebnisfit.

Ein Nullsegment wird ausschliesslich als leere `ReceptorDistribution`
materialisiert. Ein Frame mit vier Nullwerten ist kein zulaessiger Ersatz.

## Kontaktframe und Snapshotregel

Jedes Nichtnullintervall besitzt genau einen `ReceptorContactFrame` am
registrierten Dock. Der Frame traegt alle vier Carrier und den vollstaendigen
Vierervektor. Seine Quellgrenze entspricht exakt der Feldgrenze.

Die Snapshotidentitaet wird ohne Replik-, Modell-, Familien- oder
Ergebnislabel gebildet:

```text
s1sf.<payload>.<start_tick>.<end_tick>
```

Zulaessige Payloadteile sind:

```text
a-contact
b-contact
c-contact
probe-a-contact
probe-b-contact
```

Beispiel:

```text
s1sf.a-contact.0.10
```

Damit besitzen getrennte Repliken fuer einen gemeinsamen echten Praefix
wertidentische oeffentliche Intervallpayloads und Digests. Die Modellrolle
oder erwartete Kontrastrichtung kann nicht in den Rezeptorinput gelangen.

## Segmentnotation

Die Plannotation expandiert deterministisch:

```text
A<n>@t = n aufeinanderfolgende A_CONTACT-Intervalle ab Tick t
B<n>@t = n aufeinanderfolgende B_CONTACT-Intervalle ab Tick t
C<n>@t = n aufeinanderfolgende C_CONTACT-Intervalle ab Tick t
Z<n>@t = n aufeinanderfolgende ZERO_CONTACT-Intervalle ab Tick t
PA@t   = ein PROBE_A_CONTACT-Intervall [t, t+10)
PB@t   = ein PROBE_B_CONTACT-Intervall [t, t+10)
```

Beispielsweise expandiert `A4@0` zu `[0,10)`, `[10,20)`, `[20,30)` und
`[30,40)`. Segmente duerfen spaeter nicht zusammengefasst, aufgeteilt oder
durch ein laengeres Einzelintervall ersetzt werden.

## Gebundene Geschichtsrollen

| Rolle | Expansion | Dauer | Betragssumme ueber Zeit |
|---|---|---:|---:|
| kurzer A-Praefix | `A2@0` | 2 s | `1.0` |
| voller A-Praefix | `A4@0` | 4 s | `2.0` |
| F-fokale A-Geschichte | `A3@0` | 3 s | `1.5` |
| F-entfernte C-Geschichte | `C3@0` | 3 s | `1.5` |
| F-Nullgeschichte | `Z3@0` | 3 s | `0.0` |
| lokaler Mittelabschnitt | `B2@40` | 2 s | `1.0` |
| entfernter Mittelabschnitt | `C2@40` | 2 s | `1.0` |
| Null-Mittelabschnitt | `Z2@40` | 2 s | `0.0` |
| frueher Gap nach A | `Z3@40` | 3 s | `0.0` |
| spaeter Gap nach A | `Z6@40` | 6 s | `0.0` |
| frischer frueher Nullvorlauf | `Z7@0` | 7 s | `0.0` |
| frischer spaeter Nullvorlauf | `Z10@0` | 10 s | `0.0` |

Die Betragssumme ueber Zeit ist die Summe der absoluten vier Kontaktwerte
multipliziert mit der Dauer in Sekunden. Sie dient nur der exogenen
Lastidentitaet und ist keine Feldmessgroesse.

Die drei F-Intervalle liegen echt zwischen dem kurzen Zwei- und dem vollen
Vier-Intervall-A-Praefix. Der fruehe Drei-Intervall-Gap unterscheidet die
Freigaberolle vom Zwei-Intervall-I-Gap, bleibt aber echter Praefix des
spaeten Sechs-Intervall-Gap.

## Zeitloses Alignziel

Unmittelbar vor jeder Probe wird genau ein `ALIGN_READOUT_SH` ausgefuehrt.
Es verbraucht keine Feldzeit und ruft kein Modell auf. Das gemeinsame Ziel
lautet in kanonischer Knotenordnung:

```text
receptor_contact = (0.0, 0.0, 0.0, 0.0)
S                = (0.0, 0.0, 0.0, 0.0)
H                = (0.0, 0.0, 0.0, 0.0)
```

Nur diese drei oeffentlichen Vektoren werden angeglichen. Feldzeit,
Geometrie, Dock, Substrat- oder Entwicklungsreferenz, Modellrolle,
Konfiguration und vollstaendiger privater Carry bleiben bitgleich. Nach
S1-SI wird `last_distribution` konstruktiv durch die passende zeitlose
Nullframe-Projektionsdistribution ersetzt; sein Vor-Align-Digest bleibt im
aeusseren Alignreceipt. Die Alignprovenienz liegt ausserhalb des
Modellinputs.

Direkt nach Align entsteht passiv `ALIGNED_PRE_PROBE`. Nach dem atomar
abgeschlossenen Probeintervall entsteht passiv `POST_PROBE_READOUT`.

## Kanonische 17 Ereignisplaene

Alle Plaene starten aus einer eigenen validierten Frischprojektion bei Tick
0. `PRE` und `POST` bezeichnen nur die zwei zusaetzlichen passiven
C-Checkpoints.

| Pos. | Plan | Exakte Folge | Probeende |
|---:|---|---|---:|
| 01 | `F_A` | `A3@0 -> ALIGN@30 -> PA@30 -> OBSERVE` | 40 |
| 02 | `F_C` | `C3@0 -> ALIGN@30 -> PA@30 -> OBSERVE` | 40 |
| 03 | `F_G` | `Z3@0 -> ALIGN@30 -> PA@30 -> OBSERVE` | 40 |
| 04 | `T_EARLY` | `A2@0 -> ALIGN@20 -> PA@20 -> OBSERVE` | 30 |
| 05 | `T_LATER` | `A4@0 -> ALIGN@40 -> PA@40 -> OBSERVE` | 50 |
| 06 | `I_LOCAL` | `A4@0 -> B2@40 -> ALIGN@60 -> PA@60 -> OBSERVE` | 70 |
| 07 | `I_REMOTE` | `A4@0 -> C2@40 -> ALIGN@60 -> PA@60 -> OBSERVE` | 70 |
| 08 | `I_GAP` | `A4@0 -> Z2@40 -> ALIGN@60 -> PA@60 -> OBSERVE` | 70 |
| 09 | `C_LOCAL` | `A4@0 -> PRE@40 -> B2@40 -> POST@60 -> ALIGN@60 -> PA@60 -> OBSERVE` | 70 |
| 10 | `C_REMOTE` | `A4@0 -> PRE@40 -> C2@40 -> POST@60 -> ALIGN@60 -> PA@60 -> OBSERVE` | 70 |
| 11 | `C_GAP` | `A4@0 -> PRE@40 -> Z2@40 -> POST@60 -> ALIGN@60 -> PA@60 -> OBSERVE` | 70 |
| 12 | `R_EARLY` | `A4@0 -> Z3@40 -> ALIGN@70 -> PA@70 -> OBSERVE` | 80 |
| 13 | `R_LATE` | `A4@0 -> Z6@40 -> ALIGN@100 -> PA@100 -> OBSERVE` | 110 |
| 14 | `U_RELEASED` | `A4@0 -> Z6@40 -> B2@100 -> ALIGN@120 -> PB@120 -> OBSERVE` | 130 |
| 15 | `U_EARLY` | `A4@0 -> Z3@40 -> B2@70 -> ALIGN@90 -> PB@90 -> OBSERVE` | 100 |
| 16 | `U_FRESH_B_EARLY` | `Z7@0 -> B2@70 -> ALIGN@90 -> PB@90 -> OBSERVE` | 100 |
| 17 | `U_FRESH_B_LATE` | `Z10@0 -> B2@100 -> ALIGN@120 -> PB@120 -> OBSERVE` | 130 |

`ALIGN@t`, `PRE@t`, `POST@t` und `OBSERVE` sind zeitlose aeussere
Operationen. Jede Probe ist ein normales synchrones Modellintervall.

## Gebundene Praefix- und Vergleichsidentitaeten

Die Planexpansion muss spaeter vor Ausfuehrung exakt belegen:

- `T_EARLY.A2@0` ist der echte erste Zwei-Intervall-Praefix von
  `T_LATER.A4@0`;
- alle vollen A-Geschichten sind exakt `A4@0`;
- `F_A.A3@0`, `F_C.C3@0` und `F_G.Z3@0` besitzen dieselbe Dauer; A und C
  besitzen dieselbe Betragssumme ueber Zeit;
- I- und C-Tripletts besitzen denselben A-Praefix und dieselben
  Zwei-Intervall-Mittelgrenzen;
- `B2@40` und `C2@40` sind wert-, last- und zeitangepasst;
- `Z3@40` ist der echte erste Drei-Intervall-Praefix von `Z6@40` nach A;
- `U_EARLY` und `R_EARLY` besitzen vor Tick 70 dieselbe A-/Gap-Geschichte;
- `U_RELEASED` und `R_LATE` besitzen vor Tick 100 dieselbe
  A-/Gap-Geschichte;
- `U_EARLY.B2@70` und `U_FRESH_B_EARLY.B2@70` sind vollstaendig
  wert- und zeitidentisch;
- `U_RELEASED.B2@100` und `U_FRESH_B_LATE.B2@100` sind vollstaendig
  wert- und zeitidentisch;
- die B-Proben sind innerhalb des fruehen Paars `PB@90` und innerhalb des
  spaeten Paars `PB@120` identisch;
- alle A-Proben mit gleicher Startzeit sind payloadidentisch;
- kein Plan enthaelt einen Kandidatenschalter, ein Ergebnislabel oder eine
  erwartete Richtung.

## Gemeinsame Modellsicht

Fuer jede der 238 Matrixzellen gilt:

- die Modellrolle erhaelt nur den aktuellen `ReceptorDistribution`- und
  `MCMFieldStepTime`-Payload;
- fuer dieselbe Replik und Ereignisposition erhalten alle 14 Rollen exakt
  dieselben oeffentlichen Bytes;
- alle Modelle tragen ihren eigenen Feld- und Privatcarry lueckenlos;
- kein Modell erhaelt Planname, Familienrolle, Ordinal, Checkpoint oder
  Vergleichspaar;
- B1, B2 und M4 bleiben durch die ausschliesslich synchrone Form
  anschliessbar;
- Align und Beobachtungen rufen keinen Modellkern auf.

## Abgeleitete Topologie

Die 17 Plaene enthalten pro Modellrolle:

```text
127 synchrone modellwirksame Intervalle
17 zeitlose Alignoperationen
40 passive Pflichtbeobachtungen
```

Ueber alle 14 Modellrollen folgen daraus:

```text
1778 synchrone Modellintervalle
238 zeitlose Alignoperationen
560 passive Pflichtbeobachtungen
```

Diese Zahlen sind Vollstaendigkeitsableitungen und keine
Ausfuehrungsfreigabe oder Laufzeitabschaetzung.

## Fail-Closed-Regeln

Ein spaeteres Fixture ist ungueltig, wenn:

- Clock, Tickrate oder Intervallbreite abweichen;
- ein Intervall transient, nullbreit, ueberlappend oder nicht lueckenlos ist;
- ein Kontaktwert, Carrier, Dock oder Snapshotlabel abweicht;
- ein Nullsegment einen Nullframe statt `contacts=()` verwendet;
- ein Praefix kopiert, gekuerzt, aufgefuellt oder neu segmentiert wird;
- B/C-Last oder Mittelzeit nicht uebereinstimmen;
- eine der beiden U-Frischkontrollen fehlt oder an die falsche B-Zeit bindet;
- Align Feldzeit oder privaten Carry veraendert;
- Plan-, Modell- oder Ergebniswissen in einen Modellinput gelangt;
- ein Digest aus einem historischen Profil wiederverwendet wird;
- eine Teilmenge der 17 Plaene als vollstaendiges Fixture ausgegeben wird.

Es gibt keine Reparatur, Toleranz, Interpolation, Armauffuellung oder
rollenabhaengige Segmentwahl.

## Aussagegrenze

S1-SF bindet nur eine faire endliche technische Exposition. Die Werte und
Plaene bestaetigen keine Baselinefunktion, keine Feldentwicklung und keine
Faehigkeit einer hypothetischen MCM-Memory-Entwicklungsrichtung.

## Genau ein naechster Schritt

S1-SG ist ausschliesslich fuer die Implementierung eines unveraenderlichen
kanonischen Segment-/Planfixtures und eines fail-closed Validators fuer die
17 S1-SF-Plaene sowie fuer noch nicht ausgefuehrte fokussierte Tests
zulaessig.

S1-SG darf keine Modellrolle aufrufen, keinen Alignzustand anwenden, keine
Matrixzelle bauen, keinen Comparator ausfuehren und keinen Forschungslauf
starten.
