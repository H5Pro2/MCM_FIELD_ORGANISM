# S1-VP: PPB-1 statischer Identitaets- und Wiederholungskorrekturvertrag

## Auftrag und Grenze

S1-VP schliesst statisch genau die zwei in S1-VO erkannten methodischen
Luecken vor einer Vollmatrixausfuehrung:

1. Baseline-Readouts benoetigen eine technisch eindeutige ausgewaehlte
   Eintragsidentitaet oder ein explizites `None`;
2. F04, F05 und F06 benoetigen je einen zweiten bitgleich vergleichbaren
   Frischstartpfad.

S1-VP aendert keine Parameter, Fixtures, Distanzregeln, Baselinefunktionen
oder Entscheidungskriterien. Der Schritt implementiert keinen Code und
fuehrt keinen PPB-, Baseline- oder Matrixaufruf aus.

## Identitaetsrollen im Readout

Jeder spaetere Baseline-Readout B01 bis B06 muss getrennt tragen:

- `selected_entry_id`: Identitaet des im Vorzustand passenden Eintrags oder
  `None`, wenn kein Eintrag innerhalb der Matchschwelle lag;
- `written_entry_id`: Identitaet des neu angelegten, ersetzten oder
  aktualisierten Eintrags oder `None`, wenn kein Eintrag geschrieben wurde;
- `selected_prestate_digest`: Digest des Inhalts, auf den sich die
  ausgewaehlte Identitaet im Vorzustand bezieht;
- `poststate_digest`: bereits bestehende atomare Ergebnisbindung.

`selected_entry_id` darf nur zusammen mit einem echten Match gesetzt sein.
Ein `STORED`, `UPDATED`, `FULL_UNMATCHED` oder `OFF` darf nicht nachtraeglich
als Auswahl desselben Eingangs interpretiert werden.

Die Identitaet ist rein technisch. Sie enthaelt keine Klasse, Bedeutung,
Quelle, Medienkennung oder Ergebnisrolle.

## Identitaetsregeln je Baseline

### B01: begrenztes Replay

B01 erhaelt ein festes Inventar von `Kapazitaet` Replay-Slots. Eine
Eintragsidentitaet besteht aus stabiler Slot-ID und monotoner
Belegungsgeneration:

```text
b01.slot.NNN.gMMMMMM
```

Ein freier Slot beginnt ohne Generation. Beim ersten Schreiben entsteht
Generation eins. Wird derselbe Slot nach Fensterfortschritt erneut belegt,
steigt seine Generation genau um eins. Dadurch kann derselbe physische Slot
nicht zwei zeitlich verschiedene Inhalte als dieselbe Zuordnung ausgeben.

Die Matchsuche erfolgt gegen den Vorzustand. Erst danach wird der aktuelle
Vektor in den naechsten Ringplatz geschrieben. `selected_entry_id` und
`written_entry_id` duerfen daher verschieden sein.

### B02: gleitender Fenstermittelwert

B02 besitzt genau eine Readoutidentitaet:

```text
b02.window.000
```

Sie wird nur als `selected_entry_id` ausgegeben, wenn der Vorzustandsmittelwert
innerhalb der Matchschwelle liegt. Die Identitaet bleibt bei Fensterbewegung
gleich, weil B02 absichtlich nur einen gemeinsamen verdichteten Zustand
besitzt. Der Fensterinhalt und sein Digest aendern sich weiterhin.

### B03: feste Prototypliste

B03 besitzt ein festes Slotinventar:

```text
b03.slot.NNN.g000001
```

Ein Slot wird hoechstens einmal belegt und danach weder aktualisiert noch
ersetzt. Seine Generation bleibt deshalb eins. Bei voller Liste und
fehlendem Match sind `selected_entry_id` und `written_entry_id` beide
`None`.

### B04 bis B06: einzelne Spuren

Die drei Einzelspuren besitzen je genau eine feste Identitaet:

```text
b04.trace.000
b05.trace.000
b06.trace.000
```

Vor der ersten Bildung existiert keine auswaehlbare Identitaet. Nach der
Bildung wird die feste Trace-ID nur bei einem spaeteren Match als
`selected_entry_id` ausgegeben. Bei einem Update ohne Match bleibt
`selected_entry_id` `None`; `written_entry_id` ist die jeweilige Trace-ID.

### B07: PPB-OFF

B07 bleibt zustandslos. Beide Identitaetsrollen sind immer `None`. B07 wird
weiterhin nicht als zustandsbehaftete Reduktionsbaseline zugelassen.

## Identitaetslebenszyklus und Bilanz

Die Identitaetsmetadaten muessen der Zustandsanatomie entsprechen:

- kein belegter B01/B03-Eintrag ohne Identitaet;
- kein freier Eintrag mit aktiver Inhaltsidentitaet;
- keine doppelte aktive Identitaet innerhalb eines Baselinezustands;
- jede B01-Ersetzung beendet die alte Generation vor Erzeugung der neuen;
- B02/B04/B05/B06 besitzen hoechstens eine aktive Zustandsidentitaet;
- ein Fehler darf weder Identitaet noch Inhalt teilweise fortschreiben.

Der logische Vektorwertvergleich aus S1-VM bleibt unveraendert. Zusaetzlich
muss der spaetere Ergebnisrecord Anzahl und Digest der aktiven
Identitaetsmetadaten ausweisen. Eine Baseline darf nicht allein deshalb als
kleiner gelten, weil ihre notwendige Identitaetsverwaltung verborgen wird.

## Wiederholungskontrolle R0/R1

Alle bestehenden Pfade bleiben als Primaerpfade `R0` erhalten. Fuer F04,
F05 und F06 wird je Kombination aus Familie, Parameterrecord und Modalitaet
genau ein zweiter Pfad `R1` registriert.

R1 muss:

- aus einem getrennten vollstaendig frischen Zustand starten;
- dieselbe Config und denselben Config-Digest wie R0 verwenden;
- dieselbe geordnete Vektorfolge, Traegerfolge, Quellclock und Schrittgrenze
  erhalten;
- dieselbe Aufrufzahl wie R0 besitzen;
- keinen Zustand, Slotzaehler, Ringindex oder Trace aus R0 uebernehmen;
- unmittelbar nach R0 derselben technischen Kombination ausgewertet werden,
  ohne R0 oder R1 erneut zu starten.

R1 ist eine deterministische Kontrollwiederholung und keine statistische
Replikation. Es gibt weiterhin keine Zufallsziehung, Streuungsschaetzung oder
adaptive Wiederholung.

## Bitgleichheitsvergleich

R0 und R1 besitzen verschiedene Pfad-IDs. Deshalb werden nicht die
vollstaendigen Receiptobjekte einschliesslich `path_id` verglichen.

Bitgleich sein muessen:

- Eingangsfolgendigest;
- Ereignisfolge;
- alle typisierten Schrittbeobachtungen;
- ausgewaehlte und geschriebene Eintragsidentitaeten;
- Endzustandsdigest;
- akzeptierte Aufrufzahl.

Der Vergleichsdigest wird aus genau diesen normalisierten Rollen gebildet.
Eine Abweichung verwirft die betreffende Familie/Parameter/Modalitaets-
Kombination vor jeder Nutzen- oder Baselineentscheidung.

## Korrigierte Fallzahl

Die bestehende Matrix besitzt 384 Primaerpfade. Hinzu kommen:

```text
8 Familien * 3 Parameterrecords * 2 Modalitaeten * 3 Fixtures
= 144 R1-Kontrollpfade
```

Damit gilt fuer den spaeteren korrigierten Plan:

| Rolle | bisher | R1 zusaetzlich | korrigiert |
|---|---:|---:|---:|
| PPB-1 | 48 | 18 | 66 |
| sieben Baselines | 336 | 126 | 462 |
| gesamt | 384 | 144 | 528 |

## Korrigiertes Aufrufbudget

Die zusaetzlichen F04/F05/F06-Aufrufe betragen pro Familie:

| Parameter/Modalitaet | F04 + F05 + F06 |
|---|---:|
| P0 auditiv | 24 |
| P0 visuell | 20 |
| P1 auditiv | 32 |
| P1 visuell | 24 |
| P2 auditiv | 48 |
| P2 visuell | 32 |
| eine Familie gesamt | 180 |

Fuer acht Familien entstehen 1.440 zusaetzliche Aufrufe:

| Rolle | bisher | R1 zusaetzlich | korrigiert |
|---|---:|---:|---:|
| PPB-1 | 9.296 | 180 | 9.476 |
| sieben Baselines | 65.072 | 1.260 | 66.332 |
| gesamt | 74.368 | 1.440 | 75.808 |

Diese Zahlen sind harte Obergrenzen. Fehlgeschlagene Vorvalidierungen duerfen
nicht automatisch wiederholt werden.

## Digest- und Abstammungsgrenze

Der bestehende S1-VN-Plan bleibt unveraendert unter seinem Digest:

```text
35c1e589f749f1c1f1f24900f611fd43f8329d803a4b82ca94584d1925067ba3
```

Ein spaeterer korrigierter Plan muss diesen Digest als `parent_plan_digest`
binden und einen neuen Digest ueber alle 528 Pfade bilden. Der neue Digest
darf erst aus der implementierten kanonischen Pfadstruktur berechnet werden;
S1-VP erfindet keinen vorlaeufigen Wert.

## Stoppbedingungen

Die Korrektur wird nicht zur Ausfuehrung zugelassen, wenn:

- eine Baseline eine mehrdeutige oder inhaltsuebergreifend wiederverwendete
  Identitaet liefert;
- Auswahl- und Schreibidentitaet vermischt werden;
- B07 einen Zustand oder eine Identitaet erhaelt;
- ein R1-Pfad nicht frisch oder kausal identisch zu R0 startet;
- Fallzahl 528 oder Aufrufbudget 75.808 abweichen;
- die bisherigen 384 R0-Pfade in Parameter, Fixture oder Reihenfolge
  uminterpretiert werden;
- ein Ergebnis vor bestandener Identitaets- und R0/R1-Abnahme bewertet wird.

## Claim- und Projektgrenze

S1-VP korrigiert ausschliesslich die Vergleichsmethodik einer privaten
Engineeringkomponente. Der Vertrag behauptet keine endogene Feldursache,
keine Memory-Faehigkeit und keine semantische Wahrnehmung. Feldkern,
Medienpfade, API, Snapshot und Persistenz bleiben unberuehrt.

## Vertragsentscheidung

```text
S1_VP_BASELINE_SELECTED_AND_WRITTEN_ENTRY_IDENTITIES_BOUND
S1_VP_B01_GENERATIONAL_RING_IDENTITIES_BOUND
S1_VP_B02_B04_B05_B06_SINGLE_STATE_IDENTITIES_BOUND
S1_VP_B03_FIXED_SLOT_IDENTITIES_BOUND
S1_VP_B07_IDENTITY_FREE_BOUND
S1_VP_F04_F05_F06_EXACT_R1_FRESH_CONTROLS_BOUND
S1_VP_528_CORRECTED_CASES_BOUND
S1_VP_75808_CORRECTED_CALL_LIMIT_BOUND
S1_VP_PARENT_PLAN_DIGEST_BOUND
S1_VP_NO_IMPLEMENTATION_NO_EXECUTION
```

S1-VP schliesst die beiden Vertragsluecken statisch. Der korrigierte Plan ist
noch nicht implementiert und besitzt deshalb noch keinen neuen Plan-Digest.

## Genau ein naechster Schritt

**Abschlussstand:** S1-VQ hat die nachstehend freigegebenen privaten
Identitaetsrollen und den 528-Pfad-Plan implementiert. Der korrigierte
Plan-Digest lautet `f3073634...dcd1210`; registrierte Aufrufe bleiben null.
Der aktuelle Anschluss ist der statische Abschluss-Preflight S1-VR.

Der einzige Anschluss ist:

```text
S1-VQ - private Implementierung der Baseline-Identitaetsrollen,
        R0/R1-Pfade und des korrigierten 528-Fall-Planers
```

S1-VQ darf die Identitaetszustaende, Readouts, R1-Pfade, normalisierten
Vergleichsdigests und korrigierten Plan implementieren und mit kleinen
konstruierten Fixtures abnehmen. Die 528-Fall-Matrix darf weiterhin nicht
ausgefuehrt werden. Ein anschliessender Preflight muss beide S1-VO-Blocker
nachweislich schliessen, bevor ein Ausfuehrungsschritt zulaessig wird.

## Grundlagen

- [S1-VO reiner Auswerter und Preflight](S1VO_PPB1_REINER_AUSWERTER_UND_STATISCHER_VOLLMATRIX_PREFLIGHT.md)
- [S1-VN private Runner-Abnahme](S1VN_PPB1_PRIVATE_FIXTURE_BASELINE_UND_MATRIXRUNNER_ABNAHME.md)
- [S1-VM statischer Auswahl- und Matrixvertrag](S1VM_PPB1_STATISCHER_PARAMETERWAHL_BASELINE_UND_AUSFUEHRUNGSMATRIXVERTRAG.md)
