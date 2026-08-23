# S1-VO: PPB-1 reiner Auswerter und statischer Vollmatrix-Preflight

## Auftrag und Grenze

S1-VO implementiert die in S1-VM gebundene Entscheidungsreihenfolge als
reinen privaten Auswerter und prueft den S1-VN-Matrixstand vor jeder
Ausfuehrung statisch.

Zulaessig sind:

- ein kanonisches 48-Arm-Zusammenfassungsschema;
- reine Stop-, Baseline-Reduktions- und Einfachheitsentscheidungen;
- konstruierte, nicht aus der Matrix stammende Testzusammenfassungen;
- statische Pruefung von Plan, Budget, Resultatschema und Gate.

Nicht zulaessig sind die Ausfuehrung eines registrierten Matrixfalls,
Parameterwahl aus realen Ergebnissen, Feldintegration, Medienruntime,
oeffentliche API oder Snapshotumbau.

## Reiner Auswerter

Das private Modul
[`_ppb1_s1vo_evaluator.py`](../mcm_field_organism/_ppb1_s1vo_evaluator.py)
bindet pro Familie, Parameterrecord und Modalitaet genau eine technische
Zusammenfassung. Der vollstaendige Eingang besitzt damit:

```text
8 Familien * 3 Parameterrecords * 2 Modalitaeten = 48 Armzusammenfassungen
```

Jede Zusammenfassung traegt:

- Lebenszyklusgueltigkeit;
- sechs gebundene Diagnoseproben aus F02 bis F05;
- Anzahl der Matches auf diesen Proben;
- konsistente Nahzuordnung;
- getrennte Zuordnung der beiden Anker;
- bestaetigte Wiederholbarkeit;
- maximale logische Zustandswerte;
- exakte akzeptierte Aufrufzahl.

Der Auswerter akzeptiert nur das vollstaendige 48-Arm-Kreuzprodukt und die
aus P0/P1/P2 rechnerisch folgende Aufrufzahl. Fehlende, doppelte oder
nachtraeglich veraenderte Zusammenfassungen werden fail-closed abgelehnt.

## Gebundene Entscheidungsreihenfolge

Die reine Auswertung erfolgt in der S1-VM-Reihenfolge:

1. Lebenszyklus, Inventar und Aufrufzahl muessen bestehen.
2. Null von sechs Diagnosematches gilt als Nie-Match.
3. Sechs von sechs Diagnosematches gilt als Immer-Match.
4. Nahvarianten muessen konsistent und getrennte Anker verschieden
   zugeordnet sein.
5. Die Wiederholungspruefung muss bestanden sein.
6. Erst danach darf eine einfachere B01-bis-B06-Baseline reduzieren.
7. B07 kann keinen zustandsbehafteten Record reduzieren.
8. Unter nicht reduzierten Records gewinnt die geringste logische
   Zustandsmenge, danach die Reihenfolge P0, P1, P2.

Audio und Video werden getrennt entschieden. Zulaessig sind nur P0, P1, P2
oder `NO_ADMISSIBLE_CONFIGURATION`.

Die konstruierten Tests pruefen Auswahl, getrennte Modalitaetsentscheidungen,
Immer-/Nie-Match-Stopp, fehlende Wiederholung, Baseline-Reduktion,
PPB-OFF-Grenze, unvollstaendige Inventare und kanonische Digests. Sie sind
keine Matrixergebnisse.

## Bestandener technischer Preflightanteil

Der statische Preflight bestaetigt:

- unveraenderten S1-VN-Plan-Digest;
- exakt 384 registrierte Pfade;
- 9.296 PPB-, 65.072 Baseline- und 74.368 Gesamtaufrufe;
- null ausgefuehrte registrierte Aufrufe;
- aktives bedingungsloses Ausfuehrungsgate;
- gemeinsame Config-Digests und Aufrufzahlen je Kausalhistorie;
- vorhandene typisierte Fall- und Matrixresultatrollen.

Plan-Digest:

```text
35c1e589f749f1c1f1f24900f611fd43f8329d803a4b82ca94584d1925067ba3
```

## Zwei zwingende Blocker

Der Preflight stoppt an genau zwei methodischen Luecken.

### 1. Baseline-Eintragsidentitaet fehlt

S1-VM verlangt fuer F02 und F03 eine faire Aussage ueber unnoetige Trennung
und fehlerhafte Verschmelzung. PPB-Receipts tragen dafuer eine Slot-ID. Die
Baseline-Readouts tragen derzeit nur Ereignis, Distanz und Zustandsumfang,
aber keine ausgewaehlte Eintragsidentitaet.

Insbesondere B01 und B03 koennen deshalb zwar `MATCHED` melden, aber nicht
belegen, ob zwei Proben demselben oder verschiedenen Baselineeintraegen
zugeordnet wurden. Eine PPB-gegen-Baseline-Entscheidung waere damit
asymmetrisch.

Blocker:

```text
BASELINE_SELECTED_ENTRY_IDENTITY_NOT_RECORDED
```

### 2. Wiederholungspfade fehlen

S1-VM verlangt fuer F04, F05 und F06 bitgleiche Ergebnisse bei Wiederholung.
Der gleiche Vertrag schliesst jedoch Replikation aus und registriert jede
Kombination nur einmal. Aus einem einzelnen Resultat kann Bitgleichheit bei
Wiederholung nicht bestimmt werden.

Die bestehende Determinismusabnahme des reinen Kerns ist wichtig, ersetzt
aber nicht die im Matrixvertrag ausdruecklich geforderte Wiederholung des
vollstaendigen Pfads mit Fixture, Adapter und Receipt.

Blocker:

```text
F04_F05_F06_REPEATABILITY_PATHS_NOT_REGISTERED
```

## Preflightentscheidung

```text
BLOCKED_CONTRACT_CORRECTION_REQUIRED_NO_EXECUTION
```

Preflight-Digest:

```text
ae85dfb1b7743e2a14480b9b816bd63f9eb98d9a4e1b5bcd1d75eef2ba222851
```

Der Stopp betrifft die Vergleichsidentifizierbarkeit, nicht die bereits
bestandene Funktion des privaten PPB-Kerns oder Profilbinders. Es liegt
weiterhin kein Parameter-, Baseline- oder Eignungsergebnis vor.

## Testergebnis

Der S1-VO-Auswerter und Preflight bestehen mit `15 von 15` neuen Tests.
Zusammen mit S1-VN, Profilbinder, PPB-Kern und aktiven Architekturgrenzen
bestehen `96 von 96` fokussierte Tests. Die Paketkompilierung ist
erfolgreich.

Ein erster konstruierter Immer-/Nie-Match-Test uebergab denselben Zaehler
doppelt ueber seine Testfixture. Nur die Testfixture wurde korrigiert; die
Auswerterlogik und der Projektkern blieben unveraendert. Der abschliessende
Verbund besteht vollstaendig.

## Entscheidung

```text
S1_VO_PURE_48_ARM_EVALUATOR_IMPLEMENTED
S1_VO_STOP_REDUCTION_AND_SIMPLICITY_ORDER_BOUND
S1_VO_STATIC_PLAN_BUDGET_GATE_AND_SCHEMA_CHECKS_PASS
S1_VO_EXACT_TWO_METHOD_BLOCKERS_IDENTIFIED
S1_VO_BASELINE_SELECTED_IDENTITY_MISSING
S1_VO_REPEATABILITY_PATHS_MISSING
S1_VO_FULL_MATRIX_EXECUTION_BLOCKED
S1_VO_ZERO_REGISTERED_CALLS_EXECUTED
S1_VO_15_OF_15_NEW_TESTS_PASS
S1_VO_96_OF_96_COMBINED_FOCUSED_TESTS_PASS
```

## Genau ein naechster Schritt

Der einzige fachlich begruendete Anschluss ist:

```text
S1-VP - statischer Korrekturvertrag fuer Baseline-Eintragsidentitaeten
        und gebundene F04/F05/F06-Wiederholungskontrollen
```

S1-VP darf nur festlegen:

- welche stabile technische Eintragsidentitaet B01 bis B06 im Readout
  liefern oder wann explizit keine Identitaet existiert;
- wie Identitaeten bei Fensterbewegung, Update, Vollbelegung und Ersetzung
  fortgeschrieben oder freigegeben werden;
- genau einen zweiten Frischstartpfad fuer F04, F05 und F06 je bestehender
  Familie/Parameter/Modalitaetskombination;
- korrigierte Fallzahlen, Aufrufbudgets, Digestrollen und
  Bitgleichheitsvergleich;
- unveraenderte Stopp- und Claimgrenzen.

S1-VP darf noch keine Implementierung oder Matrixausfuehrung vornehmen. Die
bestehenden 384 Pfade und ihr Plan-Digest bleiben bis zu einer ausdruecklich
gebundenen Korrektur unveraendert und gesperrt.

## Grundlagen

- [S1-VN private Runner-Abnahme](S1VN_PPB1_PRIVATE_FIXTURE_BASELINE_UND_MATRIXRUNNER_ABNAHME.md)
- [S1-VM statischer Auswahl- und Matrixvertrag](S1VM_PPB1_STATISCHER_PARAMETERWAHL_BASELINE_UND_AUSFUEHRUNGSMATRIXVERTRAG.md)
- [S1-VL privater Rezeptorprofilbinder](S1VL_PPB1_PRIVATER_REZEPTORPROFILBINDER_UND_DIMENSIONSSKALIERTE_SYNTHETISCHE_ABNAHME.md)
