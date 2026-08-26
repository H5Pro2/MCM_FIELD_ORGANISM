# S1-RA: Statischer Pflichtbaselinepaket-Arm-, Familien- und Checkpointmatrix- sowie Gesamtresultatbuendelvertrag

> **Nachtrag S1-SB:** Die 16-Repliken-Achse ist durch eine 17-Repliken-Achse
> mit `U_FRESH_B_EARLY` und `U_FRESH_B_LATE` ersetzt. Damit gelten 238
> Matrixzellen und 560 passive Pflichtrecords. Die historische Tabelle und
> ihre abgeleiteten Zahlen bleiben als damaliger Stand lesbar, sind aber
> fuer neue Arbeiten durch S1-SB ersetzt.

## Status und Umfang

S1-RA bindet die vollstaendige statische Topologie, unter der die in S1-QZ
registrierten Baseline-Modellrollen spaeter die modellneutralen
S1-PZ-Expositionsrepliken und S1-QA-Beobachtungspunkte abdecken muessen.
Zusaetzlich bindet S1-RA die atomare Form eines gemeinsamen
Baselinepaket-Gesamtresultats.

Der Vertrag bindet keine konkreten Rezeptorinputs, Geometrien, Intervalle,
Dauern, Parameter, Konfigurationswerte, Toleranzen, Fixtures oder Digests. Er
implementiert keine Huelle, Matrix oder Comparatorlogik, fuehrt keinen Test
und keinen Feldlauf aus und trifft keine Ergebnisentscheidung.

Verbindliche Entscheidung:

```text
FOURTEEN_MODEL_ROLES_CROSSED_WITH_SIXTEEN_FRESH_EXPOSURE_REPLICAS
TWO_UNIVERSAL_READOUT_CHECKPOINTS_PLUS_C_FAMILY_COMPETITION_CHECKPOINTS
COMMON_PUBLIC_HISTORY_PROVENANCE_AND_ROLE_PRIVATE_CARRY_BOUND
PACKAGE_OUTPUT_ATOMIC_NO_PARTIAL_MATRIX_PUBLICATION
NO_VALUES_NO_IMPLEMENTATION_NO_COMPARATOR_NO_EXECUTION
```

## Kanonische Modellrollenachse

Die Modellrollenachse uebernimmt S1-QZ unveraendert und in folgender Ordnung:

```text
01 A0_CURRENT_CONTACT
02 A1_FAST_SH
03 A2_B1_FIXED_ADAPTER
04 A2_B2_INTEGRATOR
05 A2_B3_LOCAL_LEAKY
06 A2_B4_LINEAR_COUPLED
07 A2_B5_F3_FULL
08 A2_B6_CONST_V
09 A3_NORM
10 M1_PARALLEL_LEAK
11 M2_DELAY
12 M2_REPLAY
13 M4_DTS1_T1
14 M5_DIRECT
```

Die Ordnungsnummern sind nur kanonische Serialisierungspositionen. Sie sind
keine Prioritaet, Wertung oder Ausfuehrungsreihenfolge. Keine Rolle darf
entfallen, dupliziert oder durch eine andere Rolle ersetzt werden.

## Kanonische Expositionsreplikachse

S1-RA bindet genau die folgenden voneinander unabhaengigen Frischrepliken:

| Position | Replikrolle | Aeussere Ereignisstruktur |
|---|---|---|
| 01 | `F_A` | `HISTORY_A -> ALIGN_READOUT_SH -> PROBE_A` |
| 02 | `F_C` | `HISTORY_C_REMOTE -> ALIGN_READOUT_SH -> PROBE_A` |
| 03 | `F_G` | `GAP_ZERO_CONTACT -> ALIGN_READOUT_SH -> PROBE_A` |
| 04 | `T_EARLY` | kurzer `HISTORY_A`-Praefix -> Align -> `PROBE_A` |
| 05 | `T_LATER` | laengerer `HISTORY_A`-Praefix -> Align -> `PROBE_A` |
| 06 | `I_LOCAL` | `HISTORY_A -> HISTORY_B_LOCAL -> Align -> PROBE_A` |
| 07 | `I_REMOTE` | `HISTORY_A -> HISTORY_C_REMOTE -> Align -> PROBE_A` |
| 08 | `I_GAP` | `HISTORY_A -> GAP_ZERO_CONTACT -> Align -> PROBE_A` |
| 09 | `C_LOCAL` | A-Praefix -> Pre -> B lokal -> Post -> Align -> `PROBE_A` |
| 10 | `C_REMOTE` | A-Praefix -> Pre -> C entfernt -> Post -> Align -> `PROBE_A` |
| 11 | `C_GAP` | A-Praefix -> Pre -> Nullkontakt -> Post -> Align -> `PROBE_A` |
| 12 | `R_EARLY` | `HISTORY_A -> GAP_EARLY -> Align -> PROBE_A` |
| 13 | `R_LATE` | `HISTORY_A -> GAP_LATE -> Align -> PROBE_A` |
| 14 | `U_RELEASED` | A -> `GAP_LATE` -> B lokal -> Align -> `PROBE_B` |
| 15 | `U_EARLY` | A -> `GAP_EARLY` -> B lokal -> Align -> `PROBE_B` |
| 16 | `U_FRESH_B` | zeitangepasster Frisch-Nullpfad -> B lokal -> Align -> `PROBE_B` |

`Pre`, `Post` und `Align` sind aeussere Orchestrierungsoperationen und keine
Modelllabels. `GAP_EARLY`, `GAP_LATE` und der zeitangepasste Frisch-Nullpfad
werden spaeter ausschliesslich als normale `GAP_ZERO_CONTACT`-Intervalle
materialisiert. Ihre konkrete Laenge bleibt offen.

Jede Tabellenzeile startet fuer jede Modellrolle aus einem eigenen
Frischzustand. Keine Zeile ist die Fortsetzung einer anderen Zeile.

## Gebundene Praefix- und Kontrollbeziehungen

Die spaetere Registrierung muss vor jeder Ausfuehrung folgende strukturelle
Identitaeten belegen:

- `T_EARLY` ist ein echter Ereignispraefix von `T_LATER`;
- `I_LOCAL`, `I_REMOTE` und `I_GAP` besitzen denselben A-Praefix;
- `C_LOCAL`, `C_REMOTE` und `C_GAP` besitzen denselben A-Praefix;
- die drei C-Mittelabschnitte entsprechen den jeweiligen I-Rollen, erweitert
  nur um passive C-Checkpoints;
- `R_EARLY` ist ein echter Gap-Praefix von `R_LATE` nach identischer
  A-Geschichte;
- `U_RELEASED` verwendet dieselbe A- und spaete Gap-Geschichte wie
  `R_LATE` vor seiner B-Geschichte;
- `U_EARLY` verwendet dieselbe A- und fruehe Gap-Geschichte wie `R_EARLY`;
- die B-Geschichte und `PROBE_B` sind in allen drei U-Repliken wertidentisch;
- der Frisch-Nullpfad von `U_FRESH_B` ist zeitlich an den entsprechenden
  Vorlauf der beiden anderen U-Repliken angepasst;
- B- und C-Mittelabschnitte innerhalb I und C sind exogen belastungs- und
  zeitangepasst.

Diese Beziehungen werden spaeter durch Plan- und Segmentdigests belegt. Die
Modellkerne erhalten weder die Beziehung noch den Repliknamen.

## Vollstaendige Matrixkreuzung

Die Pflichtmatrix ist das kartesische Produkt aus:

```text
14 Baseline-Modellrollen
x 16 unabhaengigen S1-PZ-Expositionsrepliken
= 224 vollstaendigen Baseline-Lebenszykluszellen
```

Jede Zelle bezeichnet genau eine Frischreplik einer Modellrolle unter genau
einem vorregistrierten Expositionsplan. Die Zahl ist eine abgeleitete
Topologievollstaendigkeit und kein Feldschritt-, Test- oder Laufbudget.

M2-DELAY und M2-REPLAY sind getrennte Modellrollen und erhalten getrennte
Frischpuffer. B1 bis B6 sind ebenfalls sechs getrennte Modellrollen. M3
erhaelt keine Matrixzeile, weil es kein Feldarm ist.

## Pflichtcheckpoints pro Expositionsreplik

Jede der 16 Repliken besitzt zwei universelle Beobachtungspunkte:

1. `ALIGNED_PRE_PROBE`: nach erfolgreichem zeitlosem
   `ALIGN_READOUT_SH`, unmittelbar vor der Probe;
2. `POST_PROBE_READOUT`: nach dem vollstaendig abgeschlossenen Probeintervall.

Jede der drei C-Repliken besitzt zusaetzlich:

1. `PRE_COMPETITION`: nach dem gemeinsamen A-Praefix und vor dem
   Mittelabschnitt;
2. `POST_COMPETITION`: nach dem lokalen, entfernten oder Gap-Mittelabschnitt
   und vor Align.

Damit muss jede Modellrolle liefern:

```text
16 x ALIGNED_PRE_PROBE
16 x POST_PROBE_READOUT
3  x PRE_COMPETITION
3  x POST_COMPETITION
= 38 passive Beobachtungsrecords
```

Das vollstaendige Baselinepaket umfasst damit 532 passive
Beobachtungsrecords. Auch diese Zahl ist nur eine abgeleitete
Vollstaendigkeitspruefung und kein Ausfuehrungsbudget.

Die C-Checkpoints sind reine Feld- und Privatstatusbelege. Eine
Kandidatenbilanz gehoert nicht in das Baselinepaket und wird durch diese
Records nicht simuliert.

## Checkpointinhalt

Jeder passive Baselinecheckpoint muss mindestens enthalten:

- Matrix-, Modellrollen-, Replik- und Checkpointidentitaet;
- Modellregistrierungs- und Konfigurationsdigest;
- Expositionsplan- und bis dahin vollstaendige Ereigniskettendigest;
- oeffentliche Frischprojektions- und Carryprovenienz;
- Geometrie, Knotenordnung, Feldzeit und Rezeptorprovenienz;
- vollstaendigen aktuellen Rezeptorkontakt;
- vollstaendiges signed S und H in kanonischer Knotenordnung;
- vollstaendigen oeffentlichen Felddigest;
- privaten Zustandsdigest oder kanonische Zustandslosmarkierung;
- Alignbeleg, soweit der Checkpoint nach Align liegt;
- technischen Gueltigkeitsstatus und Eigendigest.

`POST_PROBE_READOUT` bindet zusaetzlich die vollstaendige signed
S-Fortsetzung nach der Probe. Ein Skalar, Betrag, eine Norm oder eine
ausgewaehlte Komponente ersetzt diesen Vektor nicht.

Private Rohzustaende werden nicht in den gemeinsamen Checkpoint kopiert. Der
Comparator darf spaeter nur ihre Vollstaendigkeit und Carryidentitaet ueber
den Digest pruefen.

## Gemeinsame oeffentliche Ereignisprovenienz

Fuer dieselbe Expositionsreplik und Ereignisposition muessen alle 14
Modellrollen denselben oeffentlichen Ereignisbeleg tragen:

- denselben Expositionsplandigest;
- denselben Rezeptor- beziehungsweise Nullkontaktinputdigest;
- dieselbe technische Intervallgrenze;
- dieselbe Geometrie- und Knotenordnung;
- bei Align denselben Zielprojektionsdigest;
- am Checkpoint dieselbe aeussere Checkpointidentitaet.

Die vollstaendigen internen Felddigests und privaten Zustandsdigests duerfen
zwischen Modellrollen abweichen. Diese Abweichung ist gerade der technische
Vergleichsgegenstand und darf nicht durch eine erzwungene
Gesamtdigestgleichheit beseitigt werden.

## Frischstart- und Konfigurationsmatrix

Vor der ersten Ereignisposition jeder Zelle gilt gemeinsam:

- alle 224 Zellen besitzen dieselbe oeffentliche Frischprojektion;
- die 16 Zellen derselben Modellrolle besitzen digestgleiche vollstaendige
  Privatfrischzustaende oder dieselbe Leermarkierung;
- jede Modellrolle verwendet in allen 16 Zellen exakt denselben
  Konfigurationsdigest;
- verschiedene Modellrollen duerfen und muessen rollenverschiedene private
  Frischzustaende und Konfigurationen behalten;
- jede Provenienzkette beginnt leer und eindeutig fuer genau diese Zelle.

Eine Konfigurationsgleichheit zwischen unterschiedlichen Modellrollen ist
nicht gefordert. Eine armweise Konfigurationsabweichung innerhalb einer
Modellrolle sperrt dagegen das gesamte Paket.

## Carryketten pro Matrixzelle

Innerhalb einer Zelle muss jede erfolgreiche Operation lueckenlos an die
vorherige anschliessen:

- Folgefelddigest des Intervalls wird Feldvorzustandsdigest des naechsten
  Intervalls;
- Privatfolgezustandsdigest wird Privatvorzustandsdigest des naechsten
  Intervalls;
- Align erhaelt Privatstatus und Feldzeit bitgenau;
- Observe erhaelt Feld, Privatstatus und Feldzeit bitgenau;
- Ereignisreceipts bilden eine kanonische ununterbrochene Digestkette;
- der letzte Checkpoint belegt den terminalen Zellzustand.

Zwischen Matrixzellen existiert kein Carry. Identische Praefixe werden aus
getrennten Frischzustaenden erneut kausal ausgefuehrt und nicht durch
Zustandskopien, Caches oder Replay zwischen Repliken ersetzt.

## Zellresultatvertrag

Eine erfolgreiche Matrixzelle muss atomar binden:

- Matrix- und Zellidentitaet;
- Modellregistrierung, Konfiguration und Expositionsplan;
- Frischfeld- und Privatfrischzustandsprovenienz;
- vollstaendige geordnete Ereignisreceiptkette;
- alle fuer die Replik vorgeschriebenen Checkpointrecords;
- terminalen Feld- und Privatstatusdigest;
- technischen Diagnostikdigest;
- Zellstatus `CELL_COMPLETED` und Eigendigest.

Eine gescheiterte Zelle liefert ausschliesslich einen Fehlerbeleg mit
Zellidentitaet, kanonischer Fehlerklasse und letzter erfolgreicher
Ereignisposition. Feld, Privatstatus, Checkpoints und Teilreceiptkette werden
nicht als Zellresultat veroeffentlicht. Ihr Status lautet
`CELL_NOT_COMPUTABLE`.

## Atomares Baselinepaket-Gesamtresultat

Ein erfolgreiches Gesamtresultat muss enthalten:

- Schema-, S1-QZ- und S1-RA-Vertragsidentitaeten;
- kanonische Modellrollen- und Expositionsreplikordnung;
- alle Modellregistrierungs-, Plan- und gemeinsamen
  Frischprojektionsbelege;
- exakt 224 `CELL_COMPLETED`-Zellresultate;
- exakt 532 vollstaendige passive Checkpointrecords;
- Belege aller Praefix-, Last-, Zeit-, Align- und Carrybeziehungen;
- getrennte technische Diagnostik;
- Paketstatus `BASELINE_PACKAGE_COMPLETED` und Eigendigest.

Sobald eine Modellrolle, Replik, Zelle, Ereignisposition, Carryverknuepfung
oder ein Checkpoint fehlt oder ungueltig ist, wird kein Teil der Matrix als
vergleichbares Paket publiziert. Das einzige zulaessige Fehlerresultat
enthaelt:

- Vertrags- und Matrixidentitaet;
- kanonische Fehlerklasse;
- erste fehlerhafte Koordinate oder Vollstaendigkeitsrolle;
- Paketstatus `BASELINE_PACKAGE_NOT_COMPUTABLE`;
- Eigendigest.

Es enthaelt keine erfolgreichen Zellresultate, Feldreadouts oder
Teilkontraste. Technische Einzelreceipts koennen intern zur Fehlersuche
erhalten bleiben, gehoeren aber nicht zum Comparatorinput.

## Kein Comparator und keine Ergebnisordnung

S1-RA bindet nur die Datenvollstaendigkeit. Insbesondere werden noch nicht
festgelegt:

- Aequivalenzmetriken oder Toleranzen;
- gerichtete F-, T-, I-, C-, R- oder U-Kontraste;
- Baselinefit, Reduktion oder Residualstatus;
- M3-Eingabe und Clampentscheidung;
- Kandidaten-, Bilanz-, Ablations- oder Nullpfadrecords;
- die technische Implementierung der 17 S1-QA-Gates.

Die kanonische Modellrollenordnung ist keine Rangfolge. Es gibt kein erstes
passendes Modell, kein Best-of-Arms und kein vorzeitiges Beenden nach einem
Einzelvergleich.

## Anschlussvoraussetzungen

Die Matrixbindung autorisiert keinen Lauf. Vor jeder Implementierung muss
fuer jede Modellrolle ein S1-QZ-konformer Anschluss feststehen. Besonders
offen bleiben:

- die exakte profilfreie B1-B6-Bruecke fuer A2;
- die normale kontaktfreie M4-Fortsetzung ohne Recovery-Sidecar;
- die gemeinsame technische Kapselung der bereits atomaren A3-, M1-, M2-
  und M5-Kompositorresultate;
- die feldnative A0- und A1-Receiptform.

`NOT_CONNECTABLE` bei nur einer Pflichtrolle stoppt die gesamte Matrix. Ein
fehlender Anschluss reduziert weder die Rollenachse noch die Zellzahl.

## Paketweite Fail-Closed-Regeln

S1-RA wird verletzt, wenn spaeter:

- weniger oder mehr als die registrierten Modellrollen oder Repliken in die
  Matrix gelangen;
- eine Replik aus dem Zustand einer anderen Replik startet;
- identische Praefixe durch geteilten Zustand statt getrennte Ausfuehrung
  erzeugt werden;
- eine Modellrolle armweise Konfigurationen verwendet;
- oeffentliche Ereignisinputs derselben Replik zwischen Modellen abweichen;
- Checkpoints ein Modell fortschreiben oder private Werte interpretieren;
- ein Vor-Probe- oder Nach-Probe-Record fehlt;
- C ohne seine Vor- und Nach-Konkurrenzrecords vorliegt;
- eine fehlgeschlagene Zelle Teilfelder oder Teilcheckpoints publiziert;
- ein unvollstaendiges Paket an einen Comparator uebergeben wird;
- M3 als Feldzeile oder Kandidatenbilanz als Baselineinput erscheint;
- historische 24-Fall-Profile als Ersatz fuer diese Matrix gelten.

## Aussagegrenze

S1-RA bindet nur eine statische Vollstaendigkeits- und Ergebnisstruktur. Es
gibt keine implementierte Matrix, keine registrierten Laufwerte, keine
Ausfuehrung und keinen Funktionsbefund. Eine hypothetische MCM-Memory bleibt
eine offene Entwicklungsrichtung. Der primaere MCM-Wahrnehmungsfeldkern und
alle geschlossenen Zweige bleiben unveraendert.

## Genau ein naechster Schritt

Als einziger Anschluss ist zulaessig:

```text
S1-RB - statischer A2/B1-B6- und M4-Brueckenkompatibilitaetsaudit
        gegen S1-QZ und S1-RA
```

S1-RB soll ausschliesslich am vorhandenen Codebestand pruefen, ob alle sechs
A2-Kerne und der eingefrorene M4-Kern die gemeinsame technische
Intervalluebergabe, getrennte Frischrepliken, normale Kontakt- und
Nullkontaktintervalle sowie atomare Zelloutputs ohne Profilwissen,
Recovery-Sidecars oder Funktionsaenderung tragen koennen. Keine
Brueckenimplementierung, neue Mappingregel, Parameterwahl, Fixture,
Testausfuehrung, Matrixausfuehrung oder Ergebnisentscheidung.
