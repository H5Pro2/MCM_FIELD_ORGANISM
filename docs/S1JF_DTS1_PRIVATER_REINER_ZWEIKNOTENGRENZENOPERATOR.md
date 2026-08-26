# S1-JF: Privater reiner P_IH-Zweiknotengrenzenoperator

## Ergebnis

S1-JF implementiert die in S1-JE registrierte Zweiknotenfixture und genau
einen privaten reinen Operator:

`apply_dts1_common_sh_boundary_2n(field, boundary_role)`

Die Umsetzung liegt in einem separaten privaten Modul. Der abgeschlossene
S1-IZ-Dreiknotenoperator und sein Receipt bleiben unveraendert.

## Eingabegrenze

Zulaessig ist ausschliesslich ein vollstaendiges `SharedMCMField` mit zwei
eindimensional benachbarten Knoten und genau einer offenen Kante. Die Knoten
werden nach ihrer Position kanonisch geordnet. Als Rolle ist nur
`A_BOUNDARY_2N` erlaubt.

Andere Rollen, Knotenzahlen, Positionsluecken oder Kanteninventuren brechen
vor einer Ausgabe ab.

## Reine Transformation

Der Operator ersetzt pro Knoten nur:

- S als `activation` mit `(-0.5,0.5)`,
- H als `afterimage` mit `(0,0)`.

Neuron- und Feldidentitaeten, Modalitaet, Geometrie, Position,
Wahrnehmungsobjekt und Tick bleiben unveraendert. Docks, Distribution und
Layergeometrie bleiben wertgleich. Vorhandene L- oder M-Zustaende werden als
dasselbe unveraenderte Objekt uebernommen.

DTS-1-Anatomie und fester B1-Adapter sind keine Eingaben und daher fuer den
Operator unerreichbar. Das Modul importiert keinen Modell-, Ressourcen-,
Backreaction-, Baseline- oder Runtimekern. Der Operator ist weder im Paket
noch in `current_api` exportiert.

## Technische Abnahme

Elf Matrixfaelle pruefen:

- exakte unveraenderliche Fixturewerte,
- exakte S/H-Anwendung,
- unveraenderte Eingabe und Nicht-S/H-Neuronenrollen,
- identische Erhaltung vorhandener M- und L-Zustaende,
- unveraenderte Feldhuelle und Zeit,
- Fail-Closed-Verhalten fuer Rollen und Geometrien,
- Determinismus und Unabhaengigkeit von der Deklarationsreihenfolge,
- fehlende Modell-, Ressourcen-, Runtime- und Exportpfade,
- statischen Abschluss ohne Feldschritt.

Die Abnahme ist eine reine technische Zustandstransformation. Sie fuehrt kein
Intervall und keinen Modellkern aus.

## Entscheidung

`PRIVATE_PURE_TWO_NODE_COMMON_SH_BOUNDARY_IMPLEMENTED_TECHNICALLY_ACCEPTED`

Kanonischer Receipt-Digest:

`ce0d17c185f08327bf81ea50b936fdc54992968980c56b385fd9629658236277`

S1-JF zeigt keine funktionale Wirkung, Baselinepassung oder
Kandidatenueberlegenheit. Speicher-, Lern- und KI-Claims bleiben gesperrt.

## Naechster zulaessiger Schritt

S1-JG darf ausschliesslich den statischen Vertrag fuer die gemeinsame
unveraenderliche Intervallhuelle ueber P_IE, korrigiertes P_IH sowie
korrigiertes P_IK/P_IN binden. Noch keine Huelleimplementierung, kein
Adapter- oder Modellaufruf, keine Runtime und keine Forschungsprobe.
