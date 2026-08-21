# S1-SJ: Implementierung des atomaren Vier-Knoten-Einzelzellen-Lebenszyklus

## Status

S1-SJ setzt ausschliesslich den in S1-SI gebundenen technischen
Einzelzellenvertrag um. Es wurde keine Matrixzelle ausgefuehrt und kein
Feld- oder Forschungsergebnis gebildet.

## Implementierte Oberflaechen

`four_node_model_invocation.py` stellt nun die drei gebundenen schmalen
Rollen bereit:

```text
four_node_model_field_digest
four_node_model_private_state_digest
rebind_four_node_model_carry_field
```

Die Digestrollen delegieren die bereits verwendete Kanonisierung. Die
Rebindrolle akzeptiert nur die festgelegte zeitlose Nullrahmenprojektion.
Sie prueft den eingehenden Carrydigest, Feld- und Geometrieidentitaeten,
Layertick, Docks, Knotenrollen, lokale Samples sowie Substrat- und
Entwicklungsreferenzen. Der private Objektverweis und alle Konfigurations-
und Abhaengigkeitsrollen bleiben erhalten; Feld- und Carrydigest werden neu
gebildet.

## Atomare Zellhuelle

`four_node_cell_lifecycle.py` implementiert genau eine isolierte
Modellrollen-/Expositionsplanzelle. Die Huelle:

- baut fuer jede Zelle ein eigenes Frischbundle und genau eine Assembly;
- uebergibt dem Modell nur Assembly oder Carry, Fixturedistribution,
  Fixturestepzeit und den rollenfesten Refinementwert;
- verwendet fuer B3 bis B6 durchgehend `refinement=2`, sonst `None`;
- verlangt pro Intervall genau einen vollstaendigen Modellschritt;
- materialisiert Align ohne Modellaufruf oder Zeitfortschritt;
- bindet den Vor-Align-Distributionsdigest im Alignreceipt;
- erfasst Checkpoints passiv mit vier vorzeichenbehafteten Feldvektoren;
- verkettet Intervall-, Align- und Checkpointreceipts;
- publiziert Carry und Checkpoints erst nach vollstaendigem Zellerfolg.

Jeder Fehler liefert ausschliesslich `NOT_COMPUTABLE`, Fehlercode und
Fehlerreceipt. Ein Zwischen-Carry, Teilfeld, interner Checkpoint oder
terminaler Kettendigest wird im Fehlerfall nicht publiziert. Es gibt keinen
Retry und keinen Ersatzpfad.

## Definierte Tests

`tests/test_four_node_cell_lifecycle.py` enthaelt 14 fokussierte Tests fuer:

- gemeinsame Digestdefinition;
- private und technische Identitaeten ueber Carry-Rebinding;
- gueltige zeitlose Alignprojektion und Ablehnung abweichender Projektionen;
- atomaren Erfolg mit geordneten Checkpoints;
- feste Refinementbindung fuer F3- und Nicht-F3-Rollen;
- exakt einen Modellaufruf pro Intervall, jedoch keinen fuer Align oder
  Checkpoint;
- vierdimensionale vorzeichenbehaftete Checkpointvektoren;
- Checkpoint- und Alignreceiptordnung;
- atomare Fehlerausgabe nach bereits intern erfasstem Checkpoint;
- Ablehnung manipulierter Fixtures und ungueltiger Planpositionen;
- deterministische Zell- und Ereignisketten-Digestkodierung.

Die letzte Bezeichnung meint ausschliesslich technische Digestbildung. Sie
ist keine funktionale Interpretation.

## Statische Kontrolle

Die drei geaenderten beziehungsweise neuen Python-Dateien wurden nur auf
Syntax und Importierbarkeit kontrolliert. Die Testdatei enthaelt exakt 14
Testmethoden. `git diff --check` meldet keine Inhaltsfehler.

Keine der 14 Testmethoden wurde ausgefuehrt. Es gab keinen Modellaufruf,
keine Matrixzelle, keinen Feldlauf und keine Ergebnisentscheidung.

## Entscheidung und Grenze

```text
ATOMIC_FOUR_NODE_CELL_LIFECYCLE_IMPLEMENTED_FOURTEEN_TESTS_DEFINED_NOT_RUN
```

S1-SJ ist damit als Implementierung abgeschlossen, aber noch nicht
technisch abgenommen. Der einzige naechste Schritt ist S1-SK: genau ein
unveraenderter fokussierter Lauf von
`tests/test_four_node_cell_lifecycle.py`. Bei einem Fehler wird gestoppt;
es folgen weder Reparatur und Wiederholung im selben Schritt noch eine
Matrixausfuehrung.
