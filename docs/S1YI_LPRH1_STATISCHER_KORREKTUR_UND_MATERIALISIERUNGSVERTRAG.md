# S1-YI: Statischer LPRH-1-Korrektur- und Materialisierungsvertrag

## Zweck und Grenze

S1-YI schliesst ausschliesslich die sieben S1-YH-Blocker. Der Vertrag legt
die spaetere private Datenanatomie so fest, dass bei einer Implementierung
keine Identitaets-, Ordnungs-, Zeit-, Fehler- oder Budgetregel nachtraeglich
erfunden werden darf.

Es werden keine Projektmodule importiert und keine Handoff-, Probe-,
Zustands- oder Feldfunktion implementiert oder ausgefuehrt.

## Atomare Eingabe

Die spaetere reine Funktion erhaelt genau neun Rollen: Ausfuehrungsidentitaet,
PPB-1-Konfiguration, unveraenderlichen Bankzustand, S1-WU-Befund, genau einen
`OrganismTimedReceptorFrame`, Ziel-Feldschritt, `SharedFieldDock`, aktuellen
`TransientNeuronInputSet` und die sortierte Menge bereits verbrauchter
Handoff-IDs.

Der getaktete Rezeptorframe bindet Originalframe und Organismuszeit atomar.
Der Zielschritt muss auf derselben Organismusuhr unmittelbar nach dem
Probeintervall beginnen. Der Rezeptoreingang muss exakt denselben Zielschritt
tragen.

## Kanonische Digests

Alle Digests verwenden kanonisches UTF-8-JSON mit verbotenen Nichtzahlen,
sortierten Schluesseln und SHA-256. Feldlisten sind exakt gebunden fuer:

- Probeinput;
- Prototypwerte;
- getakteten Probeinput;
- Zielschritt;
- Shared Dock;
- transienten Rezeptoreingang;
- jeden darin enthaltenen lokalen Kontakt.

Damit koennen vorhandener Probeinput- und Prototypdigest rekonstruiert werden,
ohne die Probe erneut aufzurufen.

## Exakte private Ergebnisanatomie

Sechs spaetere unveraenderliche Typen sind feldweise gebunden:

1. lokaler Neuronenkontext je Traeger;
2. transienter lokaler Prototypkontext;
3. ausdrueckliches No-Context-Receipt;
4. dualer Eingangs-Envelope;
5. Handoff-Receipt mit Aufruf- und Einmaligkeitsbilanz;
6. atomares Handoff-Ergebnis mit Envelope, Receipt und fortgeschriebener
   Einmaligkeitsmenge.

Der Envelope enthaelt exakt einen unveraenderten Rezeptoreingang und entweder
genau einen Kontext oder genau ein No-Context-Receipt. Beide gleichzeitig
oder beide abwesend sind ungueltig.

## Lokale Ordnung

Die `carrier_ids` der PPB-1-Konfiguration bestimmen die einzige gueltige
Reihenfolge. Der `SharedFieldDock` muss Modalitaet, Geometrie und genau
dieselbe Traegermenge besitzen. Fuer jeden Traeger wird in dieser Reihenfolge
genau ein lokaler Kontext mit Dock-, Traeger- und Neuronenidentitaet sowie dem
unveraenderten Prototypwert gebildet. Fusion, Skalierung und Umordnung sind
verboten.

## Einmaligkeit und Fehlerbudget

Handoff- und Receipt-ID werden deterministisch aus den gebundenen
Quelldigests, Zielschritt, Rezeptoreingang und Ausfuehrungsidentitaet
abgeleitet. Eine bereits verbrauchte Handoff-ID bricht vor jeder Ausgabe ab.
Nach einem gueltigen positiven oder negativen Ergebnis wird sie atomar in die
sortierte unveraenderliche Einmaligkeitsmenge aufgenommen.

Acht endliche Fehlercodes sind gebunden. Pro gueltiger Anfrage gibt es genau
einen Funktionsaufruf und einen Extraktionsversuch, keine Probe- oder
Zustandsfunktion, keinen Feldaufruf, keine Dateioperation, keinen Retry und
keine Teilausgabe. Jeder Fehler laesst auch die Einmaligkeitsmenge
unveraendert.

## Entscheidung

Alle sieben S1-YH-Blocker sind vertraglich geschlossen. Alle `26 von 26`
Materialisierungsrollen bestehen:

`PASS_LPRH1_SEVEN_MATERIALIZATION_BINDINGS_CLOSED_NO_IMPLEMENTATION_OR_EXECUTION`

Dies ist weiterhin nur eine private Engineeringvorbereitung. Es besteht kein
implementierter Handoff, keine Feldwirkung und kein Nachweis einer besonderen
Memory- oder Wahrnehmungsfunktion.

Der kanonische Vertragsdigest lautet
`8de3ed1392f1038bc6dcfd63287bf6f8e452aa1771fab1836d4230e6da0c7bd9`.

## Naechster Schritt

S1-YJ darf ausschliesslich statisch Vollstaendigkeit und interne
Widerspruchsfreiheit der sieben Korrekturen sowie die spaetere private
Implementierungsanatomie pruefen. Keine Implementierung oder Ausfuehrung.
