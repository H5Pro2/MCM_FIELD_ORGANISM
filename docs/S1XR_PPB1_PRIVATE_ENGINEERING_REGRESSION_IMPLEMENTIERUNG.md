# S1-XR: Private PPB-1-Engineeringregression

## Implementierter Umfang

S1-XR implementiert den in S1-XQ gebundenen privaten Regressionkern:

- S1-XO-Fixture genau einmal bilden;
- je einen neuen auditiven und visuellen PPB-1-Zustand initialisieren;
- beide Zustaende mit je drei Nullkontakten real bilden und stabilisieren;
- zehn Margin-Eingaben read-only gegen die eingefrorenen Zustaende pruefen;
- dieselben Eingaben gegen je einen statischen Nullprototyp pruefen;
- 20 Zellreceipts und ein atomares Engineeringreceipt erzeugen.

Der Kern verwendet keine S1-XC-Registry und keinen S1-XI-Runner.

## Ergebnisgrenze

Der gebundene Erfolgswert lautet
`ENGINEERING_REGRESSION_VALID_EQUIVALENT_TO_STATIC_PROTOTYPE`. Er bedeutet
nur, dass Bildung, read-only Abruf und einfachste Referenz unter der robusten
Fixture konsistent sind. Verhaltensgleichheit ist erwartet und keine
Forschungsneuheit.

Das atomare Regressionreceipt traegt den Digest
`9dd9358c6a7d9bdeb4ecd7d15c090ddd9f2b1bb040db80fb4f2524b8fc48b2a1`.
`12 von 12` fokussierte S1-XR-Tests bestehen.

## Fail-closed-Verhalten

Formation, Slotzahl, Stabilisierung, Support, Prototypwerte, Probeabstand,
Erkennung, Zustandsunveraenderlichkeit, Zellreihenfolge, Baselineidentitaet
und alle Digests werden geprueft. Teilreceipts und manipulierte Rollen
werden abgewiesen.

## Projektgrenze

Das Modul bleibt privat und unexportiert. Registrierte Matrix, Feld, Datei,
Snapshot, API und Produktion werden nicht erreicht. S1-XR begruendet keine
Memory-Faehigkeit oder MCM-spezifische Speicherwirkung.

## Naechster Schritt

S1-XS soll Quelle, Aufrufbudgets, Reihenfolge, Receipts, Ergebnisgrenze,
Privatheit und Trennung rein statisch pruefen. Keine erneute Regression,
keine Zustands- oder Probefunktion und kein Matrix- oder Feldlauf.
