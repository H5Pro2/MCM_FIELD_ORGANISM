# S1-JD: Korrigierter P_IH-Kausalexpositionsvertrag

## Zweck

S1-JD ersetzt fuer den spaeteren gemeinsamen Baselinevergleich ausschliesslich
den in S1-JC gestoppten P_IH-Feldpfad. Der Zustand bindet noch keine
Grenzwerte, Dauer, Toleranz, Implementierung oder Ausfuehrung.

## Gemeinsame Folge

P_IH besteht aus genau drei gleich aufgebauten Ereignissen:

1. `A_BOUNDARY_2N`,
2. `A_ACTIVE_2N`,
3. vollstaendiger S/H-Checkpoint.

Die Folge wird dreimal in fester Reihenfolge ausgefuehrt. Die Zweiknoten-
A-Grenze muss eine strikt positive S1-HK-Beteiligung erzeugen. Vor jedem
Aktivintervall erhalten DTS-1 und B1 bis B6 denselben vollstaendigen
S/H-Grenzzustand.

Der zeitlose Grenzoperator ersetzt nur S/H. DTS-1-Anatomie, fester
B1-Adapter, B2-L und B3- bis B6-M bleiben erhalten. Grenzwerte duerfen nicht
von Modell, Checkpoint, Ergebnis, verborgenem oder zukuenftigem Zustand
abhaengen.

## Aktivintervalle

Nach jeder Grenze leitet DTS-1 seine Beteiligung und seinen aktuellen Adapter
aus genau einem abgeschlossenen Vorzustand ab. Alle sieben Modelle erhalten
denselben Nullkontakt an beiden Knoten und dieselbe positive Dauer. Jedes
Modell entwickelt nur seinen eigenen registrierten Zustand und traegt den
vollstaendigen Postzustand zum naechsten Ereignis.

Private Refinementsubschritte duerfen keine weitere S/H-Grenze anwenden. Nach
jedem Gesamtintervall wird ein vollstaendiger S/H-Checkpoint in kanonischer
Knotenreihenfolge ausgegeben.

## Modellgrenzen

- DTS-1 traegt nur seine vollstaendige Ressourcenanatomie.
- B1 verwendet unveraendert einen festen Vor-Divergenz-Adapter und besitzt
  keinen sich entwickelnden verborgenen Zustand.
- B2 traegt nur sein baselineeigenes L.
- B3 bis B6 tragen nur ihr jeweiliges baselineeigenes M.
- Kein Modell erhaelt Zustand, Beteiligung, Transferledger oder Rollenlabel
  eines anderen Modells.

Die Fixed-Adapter-Gegenprognose ist damit klar: Nach identischen Grenzen muss
B1 bitidentische vollstaendige Checkpoints liefern. Zustandsbehaftete
Baselines werden erst spaeter ausgefuehrt und bewertet.

## Profil und erhaltene Evidenz

Das P_IH-Profil bleibt acht Komponenten breit:

- Checkpoint 2 minus Checkpoint 1,
- danach Checkpoint 3 minus Checkpoint 1,
- pro Differenz zuerst beide S-, danach beide H-Werte.

Alle Komponenten bleiben vorzeichenbehaftet. Absolutbetrag, Skalierung,
Checkpointfit oder reine Endpunktmessung sind gesperrt.

Der alte ressourcen-only-plus-frisches-Feld-Pfad und seine Feldvektoren sind
fuer den gemeinsamen Vergleich ersetzt beziehungsweise quarantinisiert. Die
direkten P_IH-Ressourcenledger, Receipts und die festgestellte
Abschwaechungsrichtung bleiben als getrennte harte Evidenz erhalten.

## Entscheidung

`CORRECTED_COMMON_P_IH_THREE_INTERVAL_EXPOSURE_CONTRACT_BOUND_NO_VALUES_OR_EXECUTION`

Kanonischer Vertragsdigest:

`273d2272ad660bc60a8a089c3910488b3a8375cb4c7742fed0040102dcb1ee3e`

S1-JD zeigt keine Baselinepassung oder Kandidatenueberlegenheit. Speicher-,
Lern- und KI-Claims bleiben gesperrt.

## Naechster zulaessiger Schritt

S1-JE darf ausschliesslich einen endlichen statischen Fixturevertrag fuer die
Zweiknoten-A-Grenze binden. Exakte S/H-Werte, positive Dauer, strukturelle
Toleranzen und maximales technisches Aufrufbudget muessen vor jeder
Implementierung feststehen. Noch kein Grenzoperator, keine Intervallhuelle,
kein Adapter- oder Modelllauf und keine Forschungsprobe.
