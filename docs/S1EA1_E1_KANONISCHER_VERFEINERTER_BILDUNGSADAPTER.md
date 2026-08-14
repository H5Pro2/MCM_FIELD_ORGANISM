# S1-EA1: E1 kanonischer verfeinerter Bildungsadapter

## Status

Der private kanonische Bildungsadapter ist implementiert, aber nicht mit den
kanonischen 84-Knoten-Eingaben aufgerufen. Sein Fuenfarm-Kern wurde mit
vollstaendig ersetzten synthetischen Eingaben ausgefuehrt und abgenommen.
Der S1-DY-Einstieg und alle S1-EA-Dateipfade bleiben gesperrt.

## Implementierung

```text
mcm_field_organism/e1_canonical_refined_formation_adapter.py
tests/test_e1_canonical_refined_formation_adapter.py
```

Normalisierter Implementierungsdigest:

```text
df7f5bb04a60a180ed24ecec5244e5130cb5b3275e0d3b745850c7c2fbfd2c62
```

## Kanonische Bindung

`produce_e1_canonical_refined_formation(...)` akzeptiert nur die private
S1-DY-Bindung. Bei einem spaeter freigegebenen Aufruf rekonstruiert sie:

- die digestgebundenen S1-DU-Quellen AB und BA;
- die completion-aligned Plaene `r1/r2/r4`;
- ein frisches Feld aus der gebundenen AV-Geometrie;
- einen neutralen 145-Kanten-E1-Anfang;
- die unveraenderten neutralen S/H- und Nachhallkonfigurationen.

Quelle, Permutation, beide Plaene, Anfangsfeld und Anfangszustand muessen den
S1-DY-Digests entsprechen, bevor ein Bildungsarm erreichbar ist.

## Fuenf Bildungsarme

Pro Verfeinerung sind getrennt verdrahtet:

```text
AB aktiv
BA aktiv
AB Identitaetswiederholung
AB Bildungsablation
BA Bildungsablation
```

Jeder Arm erhaelt eine tiefe Kopie von Feld und E1-Anfang. Historische
Rueckwirkung auf das laufende S/H-Feld bleibt deaktiviert. Nur die fuenf
E1-Endzustaende und ihre Audits verlassen den Adapter; historische Felder
werden nicht an die spaetere Probe uebergeben.

## Synthetische Abnahme

Der Kern wurde durch Ersetzen des kanonischen Eingabebauers mit einer kleinen
synthetischen AV-Geometrie ausgefuehrt. Dabei entstanden geordnet
`r1/r2/r4`, die AB-Wiederholung blieb bitgenau und beide Bildungsablationsarme
blieben neutral. Dieser Test ist keine kanonische Ausfuehrung.

```text
6 fokussierte Tests
381 Tests im vollstaendigen E1-Verbund
OK
```

## Aussagegrenze

S1-EA1 liefert keine kanonischen Zustandswerte und keinen Bildungs-,
Transfer-, Memory-, Semantik-, Organisations-, Topologie-,
Selbstregulations- oder KI-Befund.

## Anschluss

S1-EA2 bindet nun Bildungsadapter, 110-Support-Probe und S1-DZ-Komposition
zu einem privaten Gesamtproduzenten. Der kanonische Aufruf bleibt gesperrt.
