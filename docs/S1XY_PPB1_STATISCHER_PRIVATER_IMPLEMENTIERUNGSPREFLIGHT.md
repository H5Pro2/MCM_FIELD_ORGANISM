# S1-XY: Statischer privater PPB-1-Implementierungspreflight

## Auftrag und Grenze

S1-XY bindet ausschliesslich die spaetere private Implementierungsanatomie
fuer den in S1-XW und S1-XX abgeschlossenen Materialisierungsstand. Es wird
nichts implementiert oder ausgefuehrt. Projektmodule, Fixtures,
Zustandsfunktionen, Proben, Tests und Runner bleiben unaufgerufen.

## Vier getrennte Bausteine

### 1. Private Fixture

Ein neues privates S1-XZ-Modul soll die zwei Modalitaetsbindungen und zehn
geordneten Modalitaets-/Geschichtsplaene unveraenderlich materialisieren.
Es darf Werte, Fensterrollen, Sollereignisse, Probeordnungen und erwartete
Verhaltenswerte validieren, aber keinen Zustand bilden oder ausfuehren.

### 2. Statische Prototypbaseline

Ein spaeteres privates S1-YA-Modul soll eine mit derselben PPB-1-Regel
gebildete Bank nach der Bildungsphase einfrieren. Jede spaetere Exposition
wird durch ein Receipt als empfangen gebunden; Vor- und Nachzustandsdigest
muessen dabei identisch bleiben. Die Baseline darf weder Aktualisierung noch
Ablauf oder Verdraengung ausfuehren.

### 3. Receipts und Vergleich

Ein spaeterer privater Runner soll vorhandene S1-WQ-Uebergangsrecords und
S1-WU-Probenbefunde wiederverwenden. Neue Receipts sind nur fuer
eingefrorene Baselineexpositionen, gepaarte Probevergleiche, zehn
Geschichtsabschluesse und einen Gesamtabschluss zulaessig. Verhaltensvergleich
und Metadaten bleiben getrennt.

### 4. Endlicher Runner

Der Runner darf spaeter genau eine Fixture bilden und die Reihenfolge
`auditory/H1..H5`, danach `visual/H1..H5` abarbeiten. Jede Geschichte startet
mit getrennten frischen Kandidaten- und Baselinezustaenden. Erst werden beide
gleich gebildet und auf Verhaltensgleichheit geprueft; danach erhaelt nur der
Kandidat Zustandsuebergaenge, waehrend die Baseline dieselben Expositionen
unveraendert quittiert. Abschliessend folgen die gepaarten read-only Proben.

## Exakte spaetere Aufrufbudgets

| Rolle | Anzahl |
|---|---:|
| Fixturebildung | 1 |
| Modalitaets-/Geschichtsplaene | 10 |
| Konfigurationen | 20 |
| Frischzustaende | 20 |
| Kandidaten-Uebergangsaufrufe | 64 |
| Baseline-Bildungsuebergaenge | 36 |
| eingefrorene Baseline-Aktualisierungsreceipts | 28 |
| Kandidatenproben | 32 |
| Baselineproben | 32 |
| gepaarte Vergleichsreceipts | 32 |
| Geschichtsreceipts | 10 |
| Gesamtreceipt | 1 |
| Retries | 0 |

Die `64 + 36 + 28` Kandidaten-, Bildungs- und eingefrorenen
Baselineuebergaben ergeben exakt `128` Expositionsuebergaben. Die beiden
Probegruppen ergeben exakt `64` Proben.

## Atomare Ergebnisanatomie

Jedes der zehn Geschichtsergebnisse muss gemeinsam enthalten:

- Fixture- und Konfigurationsdigests;
- Kandidaten- und Baseline-Frischbindung;
- geordnete Kandidaten-Uebergangsrecords;
- geordnete Baseline-Bildungsrecords;
- geordnete eingefrorene Baseline-Expositionsreceipts;
- geordnete gepaarte Probevergleiche;
- Vorvergleichsgleichheit;
- erwartete und beobachtete Konflikt- oder Verdraengungsrolle;
- Methodenstatus und Geschichtsentscheidung.

Ein Gesamtresultat ist nur atomar, wenn alle zehn Ergebnisse in der
gebundenen Reihenfolge und alle `32` Vergleichsreceipts vorhanden sind.
Teilresultate, Retry, Reihenfolgedrift oder nachtraeglich geaenderte
Sollrollen sind methodisch ungueltig.

## Private Grenze

Alle neuen Module beginnen mit Unterstrich und werden weder aus Paketwurzel,
Current API noch Lazy Exports exportiert. Datei-, Snapshot-, Produktions-
und Feldpfade sind ausgeschlossen. Bestehende S1-XC-, S1-XI- und
registrierte Matrixartefakte bleiben unangetastet.

## Entscheidung

Alle `28 von 28` Preflightrollen sind statisch gebunden:

`PASS_PRIVATE_FIXTURE_BASELINE_RECEIPT_RUNNER_PREFLIGHT_BOUND_NO_IMPLEMENTATION_OR_EXECUTION`

Dies ist nur eine Implementierungsvorbereitung. Es besteht kein
Funktionsbefund, keine MCM-spezifische Memory-Mechanik und keine Feldwirkung.
Alle Ausfuehrungszaehler sind null.

Der kanonische Preflightdigest lautet
`1bf316628b75ca6ee11fb05f290713b30b758c7a35b9cb9ede19b3142c577d06`.

## Naechster Schritt

S1-XZ darf ausschliesslich die private unveraenderliche Fixture und ihren
Validator samt synthetischer Vertragstests implementieren. Baseline,
Receipts, Runner, Zustands- und Probenausfuehrung bleiben dabei gesperrt.
