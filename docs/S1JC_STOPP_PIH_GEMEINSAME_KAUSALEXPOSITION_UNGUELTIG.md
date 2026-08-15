# S1-JC: STOPP der bisherigen P_IH-Expositionsannahme

## Ergebnis

S1-JC stoppt die vorgesehene Bindung der gemeinsamen Intervallhuelle, weil
die bisher als gueltig uebernommene P_IH-Exposition bei Quellpruefung nicht
modellneutral ist.

P_IE traegt tatsaechlich ein gemeinsames vollstaendiges S/H-Feld und den
jeweiligen Modellzustand durch zwei gekoppelte Intervalle. Dieser Block bleibt
gueltig. P_IH besitzt dagegen eine andere technische Struktur.

## Quellbefund P_IH

Im aktiven P_IH-Ablauf wird die DTS-1-Anatomie dreimal mit
`compute_dts1_closed_prestate_step` fortgefuehrt. Nach jedem dieser
ressourcen-only-Schritte wird ein Feldcheckpoint separat erzeugt:

- Jeder Feldaufruf startet aus einem neu konstruierten Feld mit denselben
  S/H-Werten.
- Der Feldaufruf liest die jeweilige DTS-1-Anatomie vor dem Kontakt.
- Die vom gekoppelten Feldaufruf zurueckgegebene Anatomie wird verworfen.
- Nur die direkte Ressourcenfolge traegt die Geschichte zwischen den drei
  Checkpoints.

Damit sehen die P_IH-Feldvektoren eine getragene DTS-1-Anatomiegeschichte,
aber keine aequivalente gemeinsame Vorgeschichte fuer zustandsbehaftete
Baselines. DTS-1-Beteiligung, Anatomie und Ressourcenledger sind fuer B1 bis
B6 zu Recht gesperrt. Frische Feldreadouts allein ersetzen diese Exposition
nicht.

## Folgen

Die bisherigen P_IH-Feldvektoren werden nur fuer den gemeinsamen
Baselinevergleich quarantinisiert. Die direkten P_IH-Ledger, Receipts und die
synthetisch festgestellte Abschwaechungsrichtung bleiben gueltig.

P_IE bleibt als gemeinsamer Expositionsblock erhalten. Die korrigierten
P_IK-/P_IN-Grenzvertraege S1-IX bis S1-IZ bleiben ebenfalls erhalten. Alle
sieben S1-JA-Konfigurationen, Digests und Refinementstufen sowie alle 24
Fallidentitaeten bleiben gebunden. Die 24 Faelle bleiben blockiert.

Es wurde kein Adapter oder Modell ausgefuehrt und kein technischer oder
Forschungsfeldschritt erzeugt.

## Erforderliche Korrektur

Vor einer gemeinsamen Intervallhuelle muss P_IH neu gebunden werden:

1. Eine modellneutrale Zweiknoten-A-Grenze erzeugt positive
   S1-HK-Beteiligung.
2. DTS-1 und B1 bis B6 erhalten drei identische positive A-Aktivintervalle.
3. Vor jedem Intervall wird nur S/H ersetzt; der jeweilige modellinterne
   Zustand bleibt erhalten.
4. Kontakt und Dauer sind fuer alle Modelle identisch.
5. Nach jedem Intervall liegt ein gemeinsamer Checkpoint.
6. DTS-1 leitet seine Beteiligung erst nach der jeweiligen Grenze ab.
7. Alte P_IH-Feldzahlen werden bei der Neuregistrierung nicht uebernommen.

## Entscheidung

`STOPP_P_IH_RETAINED_COMMON_CAUSAL_EXPOSURE_ASSUMPTION_INVALID`

Kanonischer Audit-Digest:

`f1bb190007697aa29ff0e35e6532d3855ad67f5ab1cfe45d6e4b6cf14fd0783e`

Der Befund ist keine Kernelinkompatibilitaet, keine Baselineablehnung und kein
Kandidatenvorteil. Speicher-, Lern- und KI-Claims bleiben gesperrt.

## Naechster zulaessiger Schritt

S1-JD darf ausschliesslich den korrigierten statischen P_IH-
Kausalexpositionsvertrag binden. Zweiknoten-A-Grenze, drei identische
Intervalle, S/H-Reset, Tragen modelleigener Zustaende und Checkpointordnung
muessen vor jeder Wertwahl feststehen. Noch keine Werte, Intervallhuelle,
Adapterimplementierung, Modellausfuehrung oder Forschungsprobe.
