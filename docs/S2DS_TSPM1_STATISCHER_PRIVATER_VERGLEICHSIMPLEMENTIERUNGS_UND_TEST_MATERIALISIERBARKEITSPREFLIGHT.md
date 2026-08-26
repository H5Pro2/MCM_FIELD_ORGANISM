# S2-DS: Statischer TSPM-1-Vergleichsimplementierungspreflight

## Auftrag und Grenze

S2-DS prueft ausschliesslich statisch, ob der S2-DR-Vertrag ohne neue
Entscheidung in genau ein privates Vergleichsmodul und genau eine private
Vertragstestdatei ueberfuehrt werden kann.

Es wurden keine Projektmodule importiert, keine Zustands-, Probe-, Test- oder
Vergleichsfunktion aufgerufen, keine Tests ausgefuehrt und keine
Implementierungsdatei geaendert. Die 56 Vergleichszellen bleiben gesperrt.

Gebundener S2-DR-Artefaktdigest:
`ace48bfd28e685e706d5ddf1d6647fe8e36190aa87c8fa6d80b2412c8317afed`.

## Bestandene Bereiche

### Dateigrenze und private Isolation

Die spaetere Dateigrenze ist eindeutig auf
`mcm_field_organism/_tspm1_s2dr_private_comparison.py` und
`tests/test_tspm1_s2dr_private_comparison_contract.py` beschraenkt.
Vorhandene Dateien, API, Paketexporte, Snapshot, Feldpfad und Produktion
duerfen nicht geaendert werden. Ein Runner-Einstieg und Importnebenwirkungen
sind ausgeschlossen.

### Feste Vergleichsform

Folgende Bindungen sind widerspruchsfrei und endlich:

- acht auditive und 18 visuelle Traegerwerte;
- 26 gemeinsame audiovisuelle Werte;
- Ressourcenmaximum 269 Woerter beziehungsweise 2152 Bytes;
- feste Armwerte `269, 0, 176, 176, 264, 29, 255, 269`;
- feste Operationsgrenzen `293`, `234`, `234`, `0`;
- H1 bis H7 und acht geordnete Arme;
- exakt 56 statische Zellplaene;
- exakt 51 vorgesehene Tests, darunter 12 benannte Fail-Closed-Mutationen.

### Kandidatenname

Der aktive Name bleibt `TSPM-1`. Im Projektbestand existiert weder ein
Symbol noch ein Modul oder Kandidatenvertrag `APM-1`. S2-DR weist die
abweichende Schreibweise ausdruecklich als nicht wirksam zurueck. Es entsteht
keine neue Kandidatenklasse.

## Materialisierungsblocker

### DS-B01: Exakte Felder und Digestpayloads der acht Datentraeger fehlen

S2-DR benennt acht frozen Datentraeger und beschreibt ihre Rollen. Nicht
literal festgelegt sind jedoch ihre geordneten Konstruktorfelder,
Optionalitaeten, Typgrenzen, kanonischen Payloads und Eigendigestformeln.
Insbesondere bleibt offen, welche Quell-, Vorzustands-, Ereignis-, Finding-,
Budget-, Nachzustands- und Ownerdigests in `S2DRCellReceipt` und
`S2DRCellResult` zwingend vorkommen.

Damit koennten mehrere strukturell verschiedene, aber vertragsnah wirkende
Typformen implementiert werden.

### DS-B02: Private Funktionssignaturen fehlen

Nur `build_s2dr_registry()` ist namentlich gebunden. Es fehlen exakte
Signaturen und Rueckgabetypen fuer:

- Initialzustand je Arm;
- eine Bildungsexposition je Arm;
- eine read-only Probe je Arm;
- Zellverbrauch durch den Owner;
- Budgetzaehlung und Receiptvalidierung;
- Comparator und atomare Ergebniszusammenfassung.

Ohne diese Aufrufflaechen ist nicht eindeutig, wo Typ-, Quellen- und
Budgetpruefungen liegen und ob ein Operator ein Teilresultat veroeffentlichen
koennte.

### DS-B03: B2-, B3- und B4-Zustandsinvarianten sind nicht vollstaendig

Die Operatorregeln sind fachlich eindeutig, ihre spaeteren privaten
Zustandsformen jedoch nicht. Es fehlen insbesondere:

- exakte freie und belegte Slot-/Eintragsformen;
- kanonische Slot-IDs und Reihenfolgen;
- `None`-, Null- und Positivbedingungen fuer Support, Auswahl und Zeit;
- Primaerereignisse fuer Create, Match, Update, Ablauf und Ersatz;
- Vor-/Nachzustandsdigestbeziehungen;
- eindeutige Formen fuer positive und negative read-only Findings.

Diese Luecke betrifft nur die Materialisierung, nicht die bereits gebundene
Mechanik der drei Baselines.

### DS-B04: Owner-, Autorisierungs- und Fehlervertrag ist unvollstaendig

Die vier Ownerzustaende und die Pruefreihenfolge sind gebunden. Es fehlen
aber Ownerkonstruktor, Snapshotform, `consume_once`-Signatur, Herkunft und
Einmaligkeit der Autorisierungsidentitaet sowie eindeutige Fehlercodes fuer
Busy, Terminal, Autorisierung, Typ/Schema, Quelle, Budget, Relation und
atomaren Fehlschlag.

Auch ist nicht literal festgelegt, welcher interne Fehler im terminalen
`FAILED`-Snapshot gebunden wird und welcher aeussere Fehler ohne Teilausgabe
sichtbar sein darf. Dadurch sind Retry- und Mehrfachfehlerfaelle nicht
eindeutig testbar.

### DS-B05: Comparatorprojektion von 56 Zellen auf P1 bis P5 fehlt

P1 bis P5 und die Endentscheidungsreihenfolge sind gebunden. Nicht
materialisiert ist die exakte Zuordnung der Zellfindings zu jedem
Praedikat, insbesondere:

- welche H1-, H3-, H4-, H5-, H6- und H7-Felder je Arm gelesen werden;
- wie fehlende, doppelte oder widerspruechliche Findings behandelt werden;
- wie Fast- und Slow-Befund getrennt in P2 bis P5 eingehen;
- welche normalisierte R0-Projektion je Zelle bitgleich sein muss;
- welche geordnete Ergebnisform die staerkste einfache Baseline bindet.

Die Reihenfolge allein reicht nicht aus, um einen eindeutigen Comparator zu
implementieren.

### DS-B06: 51 Tests sind nicht einzeln materialisiert

Die Gruppensumme ist korrekt:

```text
6 + 7 + 8 + 5 + 8 + 5 + 12 = 51
```

Nur die sieben H-Fixtures, acht Armrollen und zwoelf Mutationsrollen sind
einzeln benannt. Fuer die uebrigen Gruppen fehlen eindeutige Test-IDs,
Fixtures, Aufrufflaechen, erwartete Ergebnisse und Negativfallprioritaeten.
Auch fuer die zwoelf Mutationen fehlen noch erwarteter Fehlercode,
Owner-Endzustand, Null-Teilausgabe und erlaubtes Operator-Aufrufbudget je
Fall.

Damit kann weder nachgewiesen werden, dass genau 51 verschiedene Tests
entstehen, noch dass keiner davon versehentlich die 56-Zellen-Ausfuehrung
startet.

## Nichtzirkularitaet und Namensbefund

Die geplante Informationsrichtung bleibt nichtzirkulaer: Config, Fixture,
Arm und Vorzustand bestimmen einen Zellplan; ein spaeteres Zellresultat darf
keine dieser Quellen rueckwirkend bestimmen. Die PPB-Budgetindizes bleiben
vorregistriert. `APM-1` erzeugt keine ID, Typ-, Datei- oder Ergebnisrolle.

Die sechs Blocker betreffen ausschliesslich die fehlende exakte
Materialisierungsform.

## Entscheidung

`BLOCK_TSPM1_PRIVATE_COMPARISON_IMPLEMENTATION_SIX_MATERIALIZATION_BINDINGS_OPEN`

S2-DR ist fachlich konsistent, aber noch nicht eindeutig implementierbar.
Private Implementierung, Testimplementierung, Testausfuehrung und alle 56
Vergleichszellen bleiben gesperrt.

## Naechster Schritt

S2-DT darf nach separater Freigabe ausschliesslich als statischer
Korrekturvertrag DS-B01 bis DS-B06 schliessen: exakte Typfelder,
Funktionssignaturen, Baselinezustandsformen, Owner-/Fehlervertrag,
Comparatorprojektion und 51 vollstaendige Testfallrecords. Danach ist S2-DS
erneut statisch durchzufuehren. Noch keine Implementierung oder Ausfuehrung.
