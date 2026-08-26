# S1-XQ: Statischer privater PPB-1-Engineering-Regressionvertrag

## Zweck und Grenze

S1-XQ bindet eine kleine technische Regression fuer den erhaltenen privaten
PPB-1-Baustein. Der Vertrag implementiert und startet nichts. Er erzeugt
keine Forschungs- oder Memory-Funktionsentscheidung.

## Gebundener Ablauf

Fuer auditive und visuelle Modalitaet gilt jeweils:

1. S1-XO-Margin-Fixture aus derselben Bundleidentitaet verwenden.
2. Eine neue private PPB-1-Konfiguration erzeugen, ohne S1-XC-Identitaet.
3. Aus leerem Zustand drei Nullprototyp-Kontakte ausfuehren.
4. `CREATED`, `MATCHED`, `MATCHED`, einen belegten stabilisierten Slot und
   Supportzahl drei pruefen.
5. Alle fuenf Margin-Proben read-only gegen denselben eingefrorenen Zustand
   auswerten.
6. Dieselben fuenf Eingaben gegen genau einen statischen Nullprototyp mit
   derselben L1-Metrik und Schwelle auswerten.
7. Kandidat und Baseline vollstaendig vergleichen und ein einziges privates
   Engineeringreceipt zurueckgeben.

Die sechs getrennten S1-XO-Schwellenoperatorfaelle sind nicht Bestandteil
dieser Regression.

## Endliches Budget

```text
Fixturebildung:              1
Initialzustaende:            2
PPB-1-Bildungsschritte:      6
read-only Kandidatenproben: 10
statische Baselinedistanzen:10
Engineeringzellen gesamt:   20
Retries:                     0
```

## Erwartete Gleichheit

Die statische Nullprototypbaseline ist absichtlich verhaltensgleich. Ein
gueltiger technischer Erfolg lautet:

`ENGINEERING_REGRESSION_VALID_EQUIVALENT_TO_STATIC_PROTOTYPE`

Diese Gleichheit bestaetigt nur, dass Zustandsbildung und read-only Abruf
unter der robusten Fixture konsistent arbeiten. Sie ist weder ein Fehler
noch Forschungsneuheit oder MCM-spezifische Wirkung.

## Fail-closed-Grenzen

Digestdrift, injizierter statt gebildeter Zustand, abweichende Formation,
nicht spaetere Probe, Zustands- oder Identitaetsaenderung, fehlende,
doppelte oder wiederholte Zelle, Teilreceipt sowie jeder Zugriff auf S1-XC,
S1-XI, Matrix, Feld, API, Snapshot, Datei oder Produktion machen den Ablauf
methodisch ungueltig.

## Entscheidung

`PASS_PRIVATE_PPB1_ENGINEERING_REGRESSION_CONTRACT_BOUND`

## Naechster Schritt

S1-XR darf den privaten reinen Regressionkern und synthetische Vertragstests
implementieren. Der Lauf darf nur in diesen Tests stattfinden. Matrix,
Feldwirkung, oeffentliche Integration und Forschungsclaims bleiben
ausgeschlossen.
