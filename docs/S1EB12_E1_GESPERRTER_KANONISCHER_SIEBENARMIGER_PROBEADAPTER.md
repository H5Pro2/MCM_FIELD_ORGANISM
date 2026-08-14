# S1-EB12: Gesperrter kanonischer siebenarmiger Probeadapter

## Status

S1-EB12 implementiert einen privaten siebenarmigen Probeadapter hinter der
statischen S1-EB11-Uebergabe. Der kanonische Inputresolver bindet
Probequelle, `r2/r4/r8`-Plaene, Geometrie und frische Probefelder. Der
gemeinsame Rechenkern wurde ausschliesslich mit einer kleinen synthetischen
Audio-/Video-Probe und synthetisch gebildeten E1-Zustaenden ausgefuehrt.

Der kanonische Einstieg prueft S1-EB9, S1-EB10 und S1-EB11, stoppt danach
aber vor der kanonischen Inputaufloesung, weil die Probeausfuehrung weiterhin
gesperrt ist.

## Implementierung

```text
mcm_field_organism/e1_confirmation_canonical_probe_adapter.py
tests/test_e1_confirmation_canonical_probe_adapter.py
```

Normalisierter Implementierungsdigest:

```text
14ca32466f45dea0aafcd9fdb6da76888e0d89c7f49256859f6abb2f907687f9
```

Synthetische Rechenkern-Ergebnisdigests fuer `r2/r4/r8`:

```text
r2 e3fd5f2b635c53c32d73bbec43e0a1b8efcd4ee8a495031d8e199b2eed1fa281
r4 892dffd55bdccd770e5344f00e0e5e707267d3f379cf23d94acd7f78d87d9c6f
r8 33333ec7709eba15702e3ad2508611650fa781fd9af0cc7cc48a6049379b6c82
```

Diese Digests gehoeren nur zur synthetischen Fixture. Sie sind keine
kanonischen Probe- oder Forschungsbefunde.

## Sieben kontrollierte Arme

```text
P0
AB aktiv
BA aktiv
AB Probeablation
BA Probeablation
AB Fixed Adapter
BA Fixed Adapter
```

Alle sieben Felder starten wertidentisch und objektgetrennt. Die AB-/BA-
E1-Zustaende bleiben waehrend der Probe eingefroren. Jeder Support wird
genau einmal zugeordnet. Probeablation gegen P0 und aktiver Pfad gegen den
zugehoerigen Fixed Adapter bleiben in der synthetischen Abnahme bitgenau.

## Geschlossene Ausfuehrungsgrenze

Der reservierte Einstieg
`run_e1_confirmation_canonical_seven_arm_probe(...)` lehnt den aktuellen
S1-EB11-Handoff ab, weil dessen `probe_execution_permitted=false` ist. Diese
Ablehnung erfolgt vor `_canonical_probe_inputs(...)` und damit vor jeder
kanonischen Feldkonstruktion oder Probe.

Es existiert kein Entscheidungs- oder Persistenzpfad in diesem Adapter.

## Technische Abnahme

```text
8 fokussierte S1-EB12-Tests
504 Tests im vollstaendigen E1-Verbund
OK
```

Geprueft wurden kanonische Inputbindung ohne Probe, der siebenarmige Kern auf
synthetischen Inputs, Wiederholbarkeit, Quellbindung vor Feldkonstruktion,
eingefrorene E1-Zustaende, exakte Ablationen, fruehe Sperre des kanonischen
Einstiegs, ungueltige Handoffs, private API und freie Exactly-once-Pfade.

Der S1-EA6-Bericht blieb unter
`adf8b2b6c1b9fdda48062dbb1cd9149fcde462a3dc77a348aa2dfb0cb1fcaa47`
unveraendert. Ergebnis-, Attempt- und Lockpfad von S1-EB bleiben frei.

## Aussagegrenze

S1-EB12 ist eine technische Adapter- und Sicherheitsstufe. Es gibt keinen
neuen kanonischen Feld-, Zustands-, Transfer-, Memory-, Semantik-,
Organisations-, Topologie-, Selbstregulations- oder KI-Befund.

## Bester naechster Schritt

S1-EB13 bindet die spaetere Uebergabe der drei Proberesultate an den
vorhandenen Ergebnis- und Entscheidungskern statisch. Die Komposition wird
nur mit synthetischen Ersatzresultaten geprueft; kanonische Probe,
Entscheidung und Persistenz bleiben gesperrt.
