# S1-ZY: Statischer T0-Abschluss und Auswahl des aktiven Rezeptor-Feld-Integrationsgates

## T0-Abschluss

Das gruene S1-ZX-Ergebnis mit 46 von 46 Tests ist technisch geschlossen und
wird nicht erneut ausgefuehrt. Es bestaetigt den kleinen aktiven
Architektur-, API- und Smoke-Guard, deckt aber noch nicht die vollstaendige
deterministische Rezeptor-zu-Feld-Kette ab.

## Ausgewaehlter Umfang

Als genau eine naechste aktive Regression wird
`T0A_ACTIVE_DETERMINISTIC_RECEPTOR_TO_FIELD_INTEGRATION` gebunden. Der Umfang
enthaelt neun vorhandene Module mit insgesamt 66 Tests. Gemeinsam pruefen sie:

- feste Audio-/Video-Feldgeometrie;
- Rezeptorverteilung in das gemeinsame Feld;
- transiente Docktrajektorie und lokale Neuroneneingabe;
- neutralen lokalen und asynchronen Feldschritt;
- Sitzungs- und Snapshotfortsetzung;
- einen endlichen synthetischen Audio-/Video-Pfad in genau ein gemeinsames Feld.

Die Auswahl schliesst damit eine reale Abdeckungsluecke zwischen dem bereits
gruenen T0-Oberflaechengate und dem aktiven In-Memory-Integrationspfad.

## Abgrenzung

Der Umfang verwendet nur synthetische Eingaben. Zwei kleine Sleeps modellieren
ueberlappende Rezeptoraufnahme; sie sind endlich und an Testdaten gebunden.
Es gibt keine Hardware, keinen realen Browser, kein Netzwerk und keine
Dateipersistenz.

Technische Substratrollen werden nur als Nullzustands-, Schema- und
Fail-Closed-Grenzen geprueft. Ein aktiver Substratanhang wird abgewiesen. Damit
reaktiviert T0A keinen geschlossenen Forschungskandidaten und prueft keine
Memory-Komponente.

Live-Audio/Video, Charakterisierungsreihen, optionale Abhaengigkeiten sowie
geschlossene und private Kandidatentests bleiben ausgeschlossen.

## Laufzeit- und Ausfuehrungsvertrag

S1-ZZ darf den exakt gebundenen 66-Test-Befehl einmal ausfuehren. Bis
einschliesslich 15 Sekunden Wandzeit wird der Umfang als aktives schnelles
Integrationsgate klassifiziert; oberhalb davon bleibt er eine aktive langsame
Integration. Die Klassifikation veraendert das Testergebnis nicht.

Erfolg verlangt Exitcode 0 und genau 66 Tests. Im selben Schritt sind Retry,
Reparatur, T0-Wiederholung und breite Discovery gesperrt. S1-ZY selbst hat
kein Testmodul und keine Feldfunktion ausgefuehrt.

## Naechster Schritt

S1-ZZ fuehrt T0A genau einmal aus, misst die Wandzeit und bindet Ergebnis und
Laufzeitklasse. Der Befund bleibt eine technische Regression und kein
Forschungs- oder Memory-Ergebnis.

Maschinenlesbarer Vertrag:
[S1ZY_STATISCHER_T0_ABSCHLUSS_UND_AUSWAHL_DES_AKTIVEN_REZEPTOR_FELD_INTEGRATIONSGATES_V1.json](S1ZY_STATISCHER_T0_ABSCHLUSS_UND_AUSWAHL_DES_AKTIVEN_REZEPTOR_FELD_INTEGRATIONSGATES_V1.json).
