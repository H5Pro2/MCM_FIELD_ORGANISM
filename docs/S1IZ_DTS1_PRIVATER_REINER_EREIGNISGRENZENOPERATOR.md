# S1-IZ: Privater reiner DTS-1-Ereignisgrenzenoperator

## Ergebnis

S1-IZ implementiert die vier in S1-IY registrierten Fixtureobjekte und genau
einen privaten reinen Operator:

`apply_dts1_common_sh_boundary(field, boundary_role)`

Der Operator ist nicht im Paket- oder `current_api`-Export enthalten. Er ist
keine Runtimefunktion und fuehrt kein Modellintervall aus.

## Technische Grenze

Als Eingabe ist genau ein vollstaendiges `SharedMCMField` mit drei
eindimensional zusammenhaengenden Knoten und den beiden Kanten der offenen
Linie zulaessig. Die Knoten werden nach ihrer Position kanonisch geordnet.
Unbekannte Rollen, andere Knotenzahlen, Luecken oder eine abweichende
Kanteninventur brechen vor einer Ausgabe ab.

Der Operator ersetzt pro Knoten ausschliesslich:

- `activation` als S,
- `afterimage` als H.

Neuronidentitaet, Feldidentitaet, Modalitaet, Geometrie, Position,
Wahrnehmungsobjekt und Tick bleiben unveraendert. Ebenso bleiben Docks,
letzte Distribution und Layergeometrie wertgleich. Ein vorhandener L- oder
M-Zustand wird als dasselbe unveraenderte Objekt uebernommen.

DTS-1-Anatomie und der feste B1-Adapter sind keine Operatorargumente und fuer
den Operator nicht erreichbar. Der Operator kann sie daher weder lesen noch
veraendern. Er importiert keinen Ressourcen-, Backreaction-, Baseline- oder
Runtimekern.

## Technische Abnahme

Die 14 registrierten Matrixfaelle pruefen:

- Konstruktion der vier unveraenderlichen kanonischen Fixtures,
- exakte Anwendung jeder A/B/Gap/Probe-S/H-Grenze,
- Unveraendertheit der Eingabe und aller Nicht-S/H-Neuronenfelder,
- identische Erhaltung vorhandener M- und L-Zustaende,
- unveraenderte Feldhuelle und Zeit,
- Fail-Closed-Verhalten fuer Rollen und Geometrien,
- Determinismus und Unabhaengigkeit von der Deklarationsreihenfolge,
- fehlende Modell-, Ressourcen-, Runtime- und oeffentliche Exportpfade,
- statischen Abschluss ohne Feldschritt.

Die Abnahme ruft den Grenzoperator nur als reine technische
Zustandstransformation auf. Sie fuehrt keinen Zeitschritt, kein
Modellintervall und keine Forschungsprobe aus.

## Entscheidung

`PRIVATE_PURE_COMMON_SH_BOUNDARY_IMPLEMENTED_TECHNICALLY_ACCEPTED`

Kanonischer Receipt-Digest:

`346f4778686642b0fa907c7ee1a5c95b2b8968172efc7a4f1cf0340de0e77828`

S1-IZ zeigt keine funktionale Wirkung, keinen Baselineabschluss und keinen
Kandidatenvorteil. Speicher-, Lern- und KI-Claims bleiben gesperrt.

## Naechster zulaessiger Schritt

S1-JA darf ausschliesslich den endlichen statischen Konfigurations- und
Fallmatrixvertrag fuer DTS-1 und B1 bis B6 binden. Vor jeder
Adapterimplementierung muessen Quellenidentitaeten, exakte Werte, Digests,
Refinementregeln und die 24 Rollen-Block-Faelle geschlossen sein. Noch keine
Adapterimplementierung, kein Modelllauf, keine Runtime und keine
Forschungsprobe.
