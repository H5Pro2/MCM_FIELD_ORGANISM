# S2-MV: Materialisierungs-Typpruefung und fokussierte Qualifikation

## Entscheidung

Die Typpruefung fuer visuelle Teilhinweise wurde eng von
`PARTIAL_VISUAL` auf den vertraglich vorhandenen Ereignistyp
`PARTIAL_VISUAL_CUE` korrigiert.

Die anschliessende Einmalqualifikation unter der ID
`s2mv-neutral-transfer-materialization-20260905-01` ist nicht bestanden.
Der Setup-Pfad stoppte vor dem ersten Testkoerper. Die korrigierte visuelle
Quellenbindung sowie `_geometry` sind durch diesen Lauf daher nicht
qualifiziert. Ein dritter S2-MT-Transferlauf bleibt gesperrt.

## Korrektur

Im privaten S2-MT-Runner wurde ausschliesslich die Ereignistyppruefung in
`_materialize_events` korrigiert:

```python
if spec.event_type != "PARTIAL_VISUAL_CUE":
```

Korpus, Ereignisfolge, Schwellen, Rezeptoren, Runtime, Memory, Feld und
Architektur blieben unveraendert. Der versiegelte Quellenplan behielt den
SHA-256
`ae808ad2a9f206bac45210f5f121e232e72da76b22e0b2bf7c599cc57e479f15`.

## Qualifikationsversuch

Genau ein Testaufruf wurde ausgefuehrt; es gab keinen Retry:

```text
python -m unittest -v tests.test_s2mv_private_transfer_materialization
```

Ergebnis:

- Exit-Code `1`;
- `0` Testkoerper ausgefuehrt;
- `setUpClass` mit einem Fehler abgebrochen;
- keine Memory-, Feld- oder Runtimeausfuehrung;
- kein Hauptlauf.

Die erste deterministisch verletzte Bedingung entstand bereits beim ersten
auditiven Ereignis in `_materialize_events`. Die Umwandlung des realen
Audiorezeptorzustands in `ReceptorContactFrame` wurde mit
`ReceptorContractError` abgewiesen:

```text
receptor values must be non-empty and stay within normalized -1..1 domain
```

Der Abbruch liegt damit vor den vier visuellen Cue-Ereignissen und vor dem
separaten Aufruf von `_geometry`. Er qualifiziert die korrigierte visuelle
Digestbindung nicht und beweist zugleich nicht, dass diese Bindung oder
`_geometry` fehlerhaft waeren.

## Quellbindungen

Produkt- und Testquellhashes waren vor und nach dem einzigen Testaufruf
identisch:

- Runner: `f04bb0e256521d8b2fb46eb1ef8b9ba721378eee8e0bdc0a046727bbf97ed719`
- Test: `3455b249b25ee43e0db805e80754e9522d65cded57acd76f486fbab1bf0fe8a2`

Der historische Lauf `s2mt-presealed-transfer-runtime-20260905-02` bleibt
unveraendert `NOT_EVALUABLE`. Es erfolgte keine fachliche Interpretation und
keine Aenderung am versiegelten Korpus. Die bekannte Bootstrap-Datei bleibt
ausgeschlossen.
