# S1-EB6: Synthetischer siebenarmiger E1-r2/r4/r8-Probeadapter

## Status

Der private siebenarmige Probeadapter fuer S1-EB3-Bildungsergebnisse ist
implementiert und nur mit einer kleinen synthetischen AV-Sequenz und
synthetischen Zwei-Knoten-Feldern abgenommen. Die kanonische Probe wird vor
der Feldkonstruktion abgewiesen. Es wurde keine Entscheidung erzeugt und
keine Datei geschrieben.

## Implementierung

```text
mcm_field_organism/e1_confirmation_seven_arm_probe.py
tests/test_e1_confirmation_seven_arm_probe.py
```

Normalisierter Implementierungsdigest:

```text
0cc32020743830b3daad48716d33ab8aedd386378f03f867e73628a65e372df1
```

## Probegrenze

Der Adapter verlangt gleichzeitig:

- den aktuellen S1-EB-Vertrag;
- genau ein S1-EB3-Bildungsergebnis;
- genau den passenden S1-EB1-Probeplan derselben Verfeinerung;
- eine nichtkanonische audiovisuelle Probequelle;
- sieben frische, wertidentische und objektgetrennte Felder;
- unveraenderte Substrat- und Nachhallkonfiguration.

Der Probeweg verwendet unveraendert:

```text
P0
AB aktiv
BA aktiv
AB Rueckwirkungsablation
BA Rueckwirkungsablation
AB fester Adapter
BA fester Adapter
```

AB und BA bleiben waehrend der gesamten Probe als dieselben E1-
Zustandsobjekte eingefroren. Jeder Support wird genau einmal zugeordnet.

## Synthetische Abnahme

`r2`, `r4` und `r8` wurden jeweils vollstaendig ausgefuehrt. In allen drei
Armen gelten:

```text
Probeablation gegen P0                 = 0.0
Aktiver Arm gegen passenden Adapter    = 0.0
Zustandsdigest vor/nach Probe           = identisch
Supportzuordnung                       = exactly once
```

Synthetische Ergebnisdigests:

```text
r2 e3fd5f2b635c53c32d73bbec43e0a1b8efcd4ee8a495031d8e199b2eed1fa281
r4 892dffd55bdccd770e5344f00e0e5e707267d3f379cf23d94acd7f78d87d9c6f
r8 33333ec7709eba15702e3ad2508611650fa781fd9af0cc7cc48a6049379b6c82
```

Diese Digests binden nur die synthetische Testfixture und sind keine
Forschungsergebnisse.

## Technische Abnahme

```text
8 fokussierte S1-EB6-Tests
464 Tests im vollstaendigen E1-Verbund
OK
```

Die registrierten S1-EB-Ergebnis-, Attempt- und Lockpfade bleiben frei.

## Aussagegrenze

S1-EB6 zeigt nur, dass S1-EB3-Bildungsergebnisse technisch durch den
unveraenderten siebenarmigen Probeweg verarbeitet werden koennen. Es liefert
keinen kanonischen Zustands-, Transfer-, Memory-, Semantik-, Organisations-,
Topologie-, Selbstregulations- oder KI-Befund.

## Anschluss

S1-EB7 hat S1-EB3-Bildung, S1-EB6-Probe und S1-EB5-Entscheidung in einer
privaten synthetischen End-to-End-Kette komponiert. Kanonische Quelle,
Persistenz und S1-EB-Einmallauf blieben gesperrt. Siehe
[S1-EB7 synthetische End-to-End-Komposition](S1EB7_E1_SYNTHETISCHE_R2_R4_R8_END_TO_END_KOMPOSITION.md).
