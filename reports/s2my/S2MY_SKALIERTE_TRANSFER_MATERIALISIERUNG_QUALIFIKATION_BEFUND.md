# S2-MY: Skalierte S2-MT-Materialisierungsqualifikation

## Entscheidung

Die Einmalqualifikation unter der ID
`s2my-scaled-transfer-materialization-20260906-01` ist nicht vollstaendig
bestanden.

Die enge Produktkorrektur des Fast-Konfigurationszugriffs ist technisch
durchgelaufen. Vollstaendige Materialisierung, Geometrie, visuelle
Cue-Digestbindungen und Cue-Treffermengen wurden bestaetigt. Zwei zusaetzliche
Testkoerper fuer die 78 auditiven Paardistanzen stoppten jedoch an einer
falschen Feldnamenannahme in der neuen Testdatei. Es gab keinen Retry. Der
dritte S2-MT-Transferlauf bleibt gesperrt.

## Produktkorrektur

Im privaten S2-MT-Geometriepfad wurden ausschliesslich die beiden
freigegebenen Zugriffe korrigiert:

```text
config.tspm_config.fast_config.auditory_match_threshold
config.tspm_config.fast_config.visual_match_threshold
```

Quellen, Skalierungsfaktor, Schwellen, Rezeptoren, Memory, Feld und Runtime
blieben unveraendert.

## Statischer Preflight

Vor dem Testaufruf wurden folgende SHA-256-Quellhashes gebunden:

- S2-MT-Runner:
  `e2e5a2f0d7b1bff4231c4e88daf1fbac1431e19ed5e9ad34b97b8cb8dc5f9ec4`;
- skalierter Quellenplan:
  `56ac39b47e9df7cab424943a66636de80200c925035d4328521c90500dd92674`;
- Qualifikation:
  `061ed77e4c8e16d56f9e0d27a45ef111e5a6973e283918933e2005056aafff7a`;
- unveraenderter S2-MW-Ergebnisbeleg:
  `b1ca1ad9d11e29c6d5b547d166741f1afbf40fb3e8f240ea6eb07d3f4e7d87ef`.

Der Test enthielt keinen Haupt-, Memoryformations-, Feldschritt- oder
Runtimeaufruf.

## Einmalqualifikation

Genau ein Testaufruf wurde ausgefuehrt:

```text
python -m unittest -v tests.test_s2my_private_scaled_transfer_materialization
```

Ergebnis:

- `7/9` Tests bestanden;
- Exit-Code `1`;
- terminales `FAILED (errors=2)`;
- kein Retry;
- keine Memoryformation, kein Feldschritt und keine Runtimeausfuehrung.

Bestanden sind:

1. neuer prospektiver Plan und unveraenderte Ereignisfolge;
2. exakt 28 skalierte Materialisate;
3. alle vier visuellen Cue-Quelldigestbindungen;
4. alle acht erwarteten Cue-Treffermengen;
5. unveraenderte Fast- und Slow-Schwellen;
6. `S2MT_GEOMETRY_MATERIALIZED` mit 66 AV-Formationspaaren;
7. kanonischer Geometriedigest und geschlossenes Hauptgate.

## Testfixturefehler

Die beiden nicht bestandenen Testkoerper wollten auditive Rezeptorwerte aus
dem bereits materialisierten Feldinput lesen. Sie verwendeten dabei:

```text
item.field_input.frames
```

Der qualifizierte unveraenderliche Typ `S2LOFieldInputV1` besitzt
stattdessen die Rolle:

```text
item.field_input.timed_frames
```

Beide Fehler sind deshalb identisch:

```text
AttributeError: 'S2LOFieldInputV1' object has no attribute 'frames'
```

Die 78 auditiven Paarabstaende wurden in dieser Qualifikation nicht erneut
verglichen. Ihr unveraenderter S2-MW-Beleg bleibt bestehen, qualifiziert aber
nicht allein den aktuellen Materialisierungspfad.

## Aussagegrenze

Der Lauf bestaetigt die korrigierte private Geometrieprojektion sowie die
vollstaendige 28-Ereignis-Materialisierung und alle vier visuellen
Cue-Digestbindungen. Wegen der zwei Testfixturefehler ist die geforderte
Gesamtqualifikation einschliesslich aller 78 auditiven Paardistanzen nicht
abgeschlossen.

Nach dem Einmalaufruf wurde weder die Testdatei korrigiert noch ein weiterer
Test gestartet. Ein dritter Transferlauf ist nicht freigegeben.
