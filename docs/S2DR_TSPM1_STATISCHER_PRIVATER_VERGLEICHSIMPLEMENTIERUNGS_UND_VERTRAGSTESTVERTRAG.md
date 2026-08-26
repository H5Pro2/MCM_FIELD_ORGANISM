# S2-DR: Statischer privater TSPM-1-Vergleichsimplementierungsvertrag

## Auftrag und Grenze

S2-DR bindet ausschliesslich die spaetere private Implementierung des in
S2-DO bis S2-DP Repeat festgelegten TSPM-1-Vergleichs und die dazugehoerigen
synthetischen Vertragstests. Dieser Schritt implementiert nichts und fuehrt
nichts aus.

Insbesondere bleiben gesperrt:

- jede der 56 Vergleichszellen;
- jeder TSPM-1-, PPB-1- oder Baseline-Zustandsaufruf;
- jede Test- oder Vergleichsausfuehrung;
- API, Snapshot, Feldpfad, Produktion und reale Eingaben;
- Semantik sowie ein Memory- oder MCM-spezifischer Wirksamkeitsbefund.

## Namensbindung

Der aktive Kandidat heisst im gesamten gebundenen Bestand `TSPM-1`. Eine
Projektrolle oder Kandidatenklasse `APM-1` existiert nicht. Die Bezeichnung
`APM-1` aus der Freigabe wird deshalb ausschliesslich als nicht wirksame
Schreibvariante behandelt. Sie darf weder einen neuen Kandidaten noch eine
Umbenennung erzeugen. Die fachliche Grenze lautet weiterhin: TSPM-1 ist bis
zum Vergleich eine private technische Architektur ohne nachgewiesenen
Funktionsvorteil oder eigenstaendigen Memory-Befund.

## Gebundene Elternartefakte

- S2-DO:
  `431fa352d0a32789af72531f34bdd6b2462fcee8f43b026db47bb39fb1ddade2`;
- S2-DQ:
  `ae6fb10da3c016cdd957f5a307115a1f29406ce91606165bec91e86c39b8de08`;
- S2-DP Repeat:
  `029a6f3c70c8adc774111254252f4fd4fd68d05d4d6e20cb6b3167f0a962d505`.

Die in S2-DQ gebundenen Digests von TSPM-1, PPB-1, Rezeptorprofil,
Aktivbatchbinder und S2-DH-Testquelle bleiben unveraendert Voraussetzung.

## Private Dateigrenze

Eine spaetere Implementierung darf genau zwei neue Dateien anlegen:

1. `mcm_field_organism/_tspm1_s2dr_private_comparison.py`;
2. `tests/test_tspm1_s2dr_private_comparison_contract.py`.

Keine vorhandene Datei darf geaendert werden. Das private Modul darf nicht in
`__init__.py`, `current_api.py`, Lazy-Exporttabellen, Snapshotcode,
Paketmetadaten oder Produktionsrunner aufgenommen werden. Es darf keinen
CLI-Einstieg, keinen `run_all`-Aufruf und keine Importnebenwirkung besitzen.

## Konfiguration und Registry

Die Implementierung muss den S2-DQ-Vertrag unveraendert materialisieren:

- acht auditive und 18 visuelle Traegerwerte;
- 26 gemeinsame audiovisuelle Werte;
- `K=3`, `C=2`, `E=8` und die gebundenen Fast-/PPB-Parameter;
- exakt H1 bis H7 mit denselben Folgen, Proben und PPB-Budgetindizes;
- acht Arme in fester Reihenfolge:
  `TSPM1`, `B0`, `B1_DIRECT`, `B1_BUDGET_MATCHED`, `B2`, `B3`, `B4`, `R0`;
- exakt 56 Zellplaene mit IDs `S2DQ:<history_id>:<arm_id>`.

`build_s2dr_registry()` darf ausschliesslich unveraenderliche Config-,
Fixture-, Arm- und Zellplandatentraeger erzeugen. Es darf keine Zustands- oder
Probefunktion aufrufen. Der Registrydigest muss alle 56 geordneten
Zellplandigests binden.

## Acht private Datentraeger

Die spaetere Implementierung verwendet genau diese Rollen:

1. `S2DRConfigRecord`;
2. `S2DRFixtureRecord`;
3. `S2DRArmSpec`;
4. `S2DRCellPlan`;
5. `S2DRBudgetReceipt`;
6. `S2DRCellReceipt`;
7. `S2DRCellResult`;
8. `S2DRComparisonResult`.

Alle Rollen sind frozen, slotgebunden und selbst-digestvalidierend. IDs,
Digests, Quellrollen und geordnete Tupel muessen im Konstruktor validiert
werden. Ein Finding bindet den Vorzustand und darf keinen Nachzustand tragen.
Nur ein vollstaendig validiertes `S2DRComparisonResult` darf spaeter alle 56
Zellergebnisse atomar zusammenfassen.

## Operatorbindung

### TSPM-1 und PPB-1

Der TSPM-1-Arm verwendet den unveraenderten privaten Kern. Beide B1-Arme
verwenden zwei unveraenderte PPB-1-Baenke. `B1_DIRECT` erhaelt jeden
Originalframe genau einmal; `B1_BUDGET_MATCHED` nur die vorregistrierten
Fixtureindizes. Beide besitzen 176 funktionale Woerter, identische
Operationsobergrenzen und getrennte Resultate.

### B2

`S2DRB2State` besitzt neun geordnete gemeinsame Slots und genau die in S2-DQ
gebundene Match-, Update-, Support-, Ablauf-, Freislot-, LRU- und Tie-Regel.
Es gibt keine zweite Ebene und keine Konsolidierung.

### B3

`S2DRB3State` besitzt genau einen gemeinsamen 26-Werte-Nachhallzustand mit
Update `0.5*alt + 0.5*eingang`, Ablauf 8 und read-only Probe bei beiden
mittleren L1-Distanzen `<=0.2`.

### B4

`S2DRB4State` besitzt genau neun FIFO-Eintraege. Ueberschreiben entfernt den
aeltesten Eintrag vollstaendig. Der Probe-Tie-Break lautet unveraendert:
maximale Modalitaetsdistanz, Distanzsumme, juengerer Bildungsindex, feste
Slot-ID.

### R0 und B0

B0 besitzt keinen funktionalen Zustand. R0 bildet TSPM-1 generisch,
positions-, modalitaets- und indexerhaltend ab. R0 darf keine zusaetzliche
Information und keinen TSPM-spezifischen Typnamen in die Gleichheitsprojektion
einbringen.

Alle Operatoren muessen reine private Funktionen sein. Sie duerfen nur ihren
gebundenen Vorzustand und genau eine gebundene Exposition oder Probe lesen.

## Ressourcen- und Operationsledger

Das gemeinsame Maximum bleibt exakt `269 functional_word64` beziehungsweise
`2152` funktionale Bytes. Die Armwerte bleiben in fester Reihenfolge:

```text
TSPM1=269, B0=0, B1_DIRECT=176, B1_BUDGET_MATCHED=176,
B2=264, B3=29, B4=255, R0=269
```

Die festen Operationsgrenzen lauten:

- maximal 293 funktionale Wortschreibungen je Bildung;
- maximal 234 Distanzterme je Bildung;
- maximal 234 Distanzterme je Probe;
- null funktionale Schreibungen je Probe.

Jeder Operator muss vor Rueckgabe seine tatsaechlichen Zaehler gegen diese
Grenzen pruefen. Digest-, Schema- und Provenienzarbeit darf nicht als
funktionale Kapazitaet verwendet werden.

## Zellbesitz und Atomaritaet

Jede spaetere Zelle besitzt einen privaten `S2DRCellOwner` mit genau den
Zustaenden `FRESH`, `BUSY`, `COMMITTED` und `FAILED`. Der Owner bindet
Zellplan-, Config-, Fixture-, Arm-, Vorzustands- und Autorisierungsdigest.

Die Reihenfolge ist verbindlich:

1. Lock einmalig erwerben;
2. `FRESH` und Autorisierung pruefen;
3. Typ, Schema und alle Digests pruefen;
4. Fixture-, Arm- und Vorzustandsbindung pruefen;
5. Ressourcen- und Operationsgrenzen pruefen;
6. erst danach einen privaten Operator aufrufen;
7. Resultat, Budget und Receipt relational validieren;
8. atomar `COMMITTED` oder ohne Teilausgabe terminal `FAILED` setzen.

Retry, Doppelverbrauch, stale Zustand oder fremde Zelltraeger liefern kein
Resultat. Ein fehlgeschlagener Owner darf nicht erneut verwendet werden.

## Comparator und Ergebnisbindung

Der Comparator implementiert exakt P1 bis P5 und die in S2-DQ gebundene
Entscheidungsreihenfolge. Es gibt keine Mehrheitswertung, keine Kompensation
zwischen Geschichten und keine nachtraegliche Schwellenwahl.

Die Endklasse ist genau eine von:

- `METHOD_INVALID`;
- `TSPM1_FUNCTION_NOT_VALID`;
- `FUNCTION_VALID_SIMPLE_BASELINE_EXPLAINS`;
- `TSPM1_TWO_TIMESCALE_ENGINEERING_ADVANTAGE_OVER_SIMPLE_BASELINES`.

R0 muss zuvor die normalisierte TSPM-1-Ausgabe exakt reproduzieren. Auch ein
spaeterer technischer Vorteilsbefund bliebe dadurch generisch erklaert und
waere kein MCM-spezifischer Memory-Befund.

## Gebundenes Vertragstestmanifest

Die spaetere eine Testdatei besitzt exakt 51 Einzeltests:

| Gruppe | Anzahl | Inhalt |
| --- | ---: | --- |
| Quelle und Konfiguration | 6 | Digests, 8/18/26, Parameter, private Grenze |
| H1-bis-H7-Registry | 7 | je Geschichte exakt ein statischer Fixturetest |
| acht Armrollen | 8 | Zustand und Operatorregel je Arm |
| Ressourcen und Operationen | 5 | 269, Armledger, 293, 234, Probe-null-write |
| acht Datentraeger | 8 | Form, Digest und Unveraenderlichkeit je Rolle |
| Comparator | 5 | P1-P5, Reihenfolge, Tie und vier Endklassen |
| Fail-Closed-Mutationen | 12 | fremd, stale, doppelt, vertauscht, ueber Budget |
| **Gesamt** | **51** | keine 56-Zellen-Ausfuehrung |

Die Tests duerfen spaeter reine Konstruktoren, Validatoren und einzelne
synthetische Operator-Mikrofaelle pruefen. Sie duerfen weder die vollstaendige
56-Zellen-Registry konsumieren noch ein `S2DRComparisonResult` aus realen
Zellergebnissen erzeugen. Testimplementierung und Testausfuehrung benoetigen
nach einem statischen Preflight eine separate Freigabe.

## Zwoelf Fail-Closed-Mutationen

1. falscher Configdigest;
2. falscher Fixturedigest;
3. falscher Armdigest;
4. falscher Vorzustandsdigest;
5. falsche Autorisierung;
6. fremde Zell-ID;
7. doppelte Zell-ID;
8. stale Probe;
9. vertauschtes Budgetreceipt;
10. Ressourcenueberschreitung;
11. Operationsueberschreitung;
12. Resultat- oder R0-Relationsabweichung.

Jeder Fall muss terminal fail-closed enden: kein Zellresultat, kein
Vergleichsresultat, keine Teilausgabe und kein Retry.

## Entscheidung

`PASS_TSPM1_STATIC_PRIVATE_COMPARISON_IMPLEMENTATION_AND_CONTRACT_TEST_CONTRACT_BOUND`

S2-DR legt die private Implementierung eindeutig fest, implementiert oder
testet sie aber nicht. Die 56-Zellen-Ausfuehrung bleibt ausdruecklich
gesperrt.

## Naechster Schritt

S2-DS darf nach separater Freigabe ausschliesslich statisch pruefen, ob
Dateigrenze, Registry, acht Typen, Operatoren, Ledger, Ownerreihenfolge,
Comparator und 51-Testmanifest vollstaendig und widerspruchsfrei
implementierbar sind. Noch keine Code- oder Testdatei und keine Ausfuehrung.
