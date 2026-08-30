# S2-GK: Private Kontextverwendung und neutrale Qualifikation

## Auftrag und Grenze

S2-GK implementiert die private technische Grenze fuer die in S2-GJ
gebundene maskierte visuelle Kontextaufgabe. Umgesetzt wurden genau:

1. ein read-only Kontextverbraucher;
2. eine unabhaengige direkte Maskenfuellbaseline;
3. ein getrennter reiner Auswerter;
4. eine Testdatei mit exakt 16 neutralen Vertragstests.

Die 13-Schritt-Bildungsgeschichten und die sieben GJ-Faelle wurden nicht
ausgefuehrt.

Qualifikations-ID:

`s2gk-private-context-use-qualification-20260830-01`

Technischer Ausgangsstand:

`a599df0e00df25cef3a71c58ef0b5c5f7318becf`

## Implementierte Rollen

### Read-only Kontextverbraucher

Der Verbraucher akzeptiert:

- eine maskierte visuelle Probe mit exakt 18 Positionen;
- neun feste sichtbare und neun feste maskierte Positionen;
- ein validiertes S2-GI-Zwei-Bereich-Bundle;
- eine explizite Rollenbindung auf `B_STABLE`.

`CURRENT_PERCEPTION_ONLY` meldet `INSUFFICIENT_INFORMATION` und fuellt keinen
Wert. `CURRENT_PERCEPTION_PLUS_TWO_AREA_CONTEXT` prueft zuerst alle sichtbaren
Positionen und uebernimmt nur bei Widerspruchsfreiheit die neun maskierten
Werte aus der stabilen visuellen B-Komponente.

Ein fehlender visueller B-Kandidat ergibt `CONTEXT_ABSENT`. Ein sichtbarer
Widerspruch ergibt `CONTEXT_CONFLICT`. Beide Ausgaenge erzeugen keine
Teilfuellung.

Die aktuelle maskierte Probe und der historische Kontextbeleg besitzen
getrennte Probedigests. Ihre Beziehung wird durch einen neuen read-only
Aufrufbeleg gebunden; es wird keine rueckwirkende Probeidentitaet behauptet.

### Unabhaengige direkte Baseline

`DIRECT_B_STABLE_MASK_FILL` besitzt einen eigenen Validierungs-, Vergleichs-,
Kopier-, Ledger- und Ergebnisweg. Die Baseline ruft weder den
Kontextverbraucher noch dessen Ergebnisfunktion auf. Sie verwendet nur die
gemeinsam gebundenen unveraenderlichen Eingabedatentypen.

### Reiner Auswerter

Nur der Auswerter akzeptiert einen vollstaendigen 18-Werte-Zielzustand. Er
wird erst nach Verbraucher und Baseline aufgerufen und unterscheidet:

- `S2GJ_FUNCTION_VALID_DIRECT_MASK_FILL_EXPLAINS`;
- `S2GJ_FOREIGN_CONTEXT_LIMIT_OBSERVED`;
- `S2GJ_CONTROL_VALID`;
- `S2GJ_FUNCTION_FALSIFIED`;
- `S2GJ_NOT_EVALUABLE`.

Verbraucher und Baseline importieren keinen Zielwerttyp und erhalten weder
Sollklassen noch Falllabels.

## Statischer Vorlauf

Vor der Ausfuehrung wurden bestaetigt:

- alle vier neuen Dateien sind syntaktisch gueltig;
- die Testdatei enthaelt exakt 16 geordnete Tests;
- Verbraucher, Baseline und Auswerter importieren keine Speicher-, Rezeptor-,
  Koordinator- oder Feldmodule;
- die Baseline besitzt keinen Consumer-Aufruf und keinen Consumer-Ergebnistyp;
- Zielwerttypen existieren nur im Auswerter;
- S2-GC- und S2-GI-Quellen blieben unveraendert.

Quellbindungen:

| Quelle | SHA-256 |
| --- | --- |
| `tools/_s2gk_private_masked_visual_context_consumer.py` | `29c16372184bec0092fadf777adc7b7e1c9a5ba0529711c46ca75c92c4769832` |
| `tools/_s2gk_private_direct_mask_fill_baseline.py` | `43ac94ca59a1157893cdc96cd4b980a0fb348130bc670596bbd3d65e112d7958` |
| `tools/_s2gk_private_masked_visual_completion_evaluator.py` | `ac33ed97b670681250cb709b40332024ab107365836cd5641d27e34ee85e5cf5` |
| `tests/test_s2gk_private_masked_visual_context.py` | `f6044b01a5984ff6bdc47155e4811efa22d83cd30f24611241c4a56254472499` |

## Einmalige neutrale Qualifikation

Es erfolgte genau ein Aufruf:

```text
python -m unittest tests.test_s2gk_private_masked_visual_context -v
```

Vollstaendiger Abschluss:

```text
Ran 16 tests in 0.047s

OK
EXIT_CODE=0
```

Die Tests bestaetigen neutral:

- keine Schaetzung im Current-only-Arm;
- korrekte B-Vervollstaendigung;
- funktionale Gleichheit der direkten Baseline;
- vollstaendige Fremdvervollstaendigung und ihre Grenzklassifikation;
- gueltige Abwesenheit und sichtbaren Konflikt ohne Teilfuellung;
- Unabhaengigkeit von interferierendem A-Inhalt;
- unveraenderte sichtbare Werte und genau neun Maskenuebernahmen;
- explizite B-Rollenbindung ohne Auswahl;
- Fail-Closed-Verhalten bei Masken-, Dimensions-, Marker-, Herkunfts-,
  Probe-, Bundle-, Zustandsdigest- und Ressourcenfehlern;
- Unveraenderlichkeit aller Eingaben und Ergebnisse;
- Zielwerttrennung;
- Trennung von funktionaler Falsifikation und `NOT_EVALUABLE`.

## Statischer Abschlussaudit

Der Abschlussaudit bestaetigt:

- genau drei private Implementierungsmodule und eine Testdatei;
- keine nachtraegliche Aenderung an S2-GC, S2-GI, B4, TSPM-1 oder PPB-1;
- keine Speicher-, Rezeptor-, Koordinator- oder Feldfunktion im Testlauf;
- keine automatische Kontextwahl, Lernoperation oder Feldintegration;
- keine Ausfuehrung einer gebundenen 13-Schritt-Geschichte oder eines
  GJ-Hauptfalls.

Technischer Status:

`PRIVATE_READ_ONLY_MASKED_VISUAL_CONTEXT_USE_VALID`

Der Status qualifiziert Verbraucher, Baseline und Auswerter. Er ist noch kein
Funktionsbefund aus tatsaechlich gebildeten Kontextgeschichten.
