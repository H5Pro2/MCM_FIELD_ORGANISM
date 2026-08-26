# S2-AC: Statischer T0B-Abschluss und Auswahl des kontrollierten Browser-Rezeptor-Gates

## Geschlossener Stand

T0, T0A und T0B sind gruen und werden nicht erneut ausgefuehrt. Damit sind
aktive Oberflaeche, deterministische Rezeptor-Feld-Integration und temporale
Uebergabe als schnelle technische Gates gebunden.

## Naechste aktive Luecke

Der kontrollierte Browserpfad besitzt noch kein eigenes vollstaendiges Gate
fuer seine Randbedingungen. T0 prueft bereits Source und Smoke. T0C ergaenzt
diese Abdeckung ohne Wiederholung um:

- den externen, unveraenderlichen Weltvertrag;
- lokale Runtimeidentitaet und Driftabweisung;
- Finalisierung eines Browser-Payloads als Rezeptorbatch;
- paarweise synthetische Aufnahme und Vergleich am skalaren Feldrand;
- vollstaendigen Ressourcenschluss bei Fehlern.

## Auswahl ohne Wiederholung

Die drei Module fuer Weltvertrag, Runtimebindung und Rezeptorbruecke liefern
13 Tests. Aus dem Timing-Pair-Modul werden 19 von 21 Tests einzeln gebunden.
Die beiden bereits waehrend S1-ZV ausgefuehrten kanonischen Fake-Pair-Tests
sind explizit ausgeschlossen. T0C enthaelt damit genau 32 bislang nicht als
Gate ausgefuehrte Tests.

Der Umfang verwendet temporaere Bindungsdateien, isolierte Python-Importe,
`numpy`, `cv2` und injizierte Browser-Fakes. Ein installiertes
Playwright-Runtimepaket, ein reales Browserbinary, Netzwerk und
Produktionspersistenz sind nicht erforderlich. Rohpayloads werden nicht als
Feldzustand aufbewahrt.

## Ausfuehrungsvertrag

S2-AD darf den exakt gebundenen Befehl einmal ausfuehren. Erfolg verlangt
Exitcode 0 und genau 32 Tests. Bis einschliesslich 15 Sekunden Wandzeit wird
T0C als schnelles aktives Browser-Randgate klassifiziert.

Retry, Reparatur, breite Discovery, Wiederholung frueherer Aktivgates und die
beiden ausgeschlossenen Timing-Tests bleiben gesperrt. S2-AC selbst fuehrt
kein Testmodul, keinen Browserpfad und keine Feldfunktion aus.

## Naechster Schritt

S2-AD fuehrt T0C genau einmal aus, misst die Laufzeit und bindet Ergebnis und
Klasse. Der Befund bleibt eine technische synthetische Browser-Rezeptor-
Regression und kein Wahrnehmungs-, Forschungs- oder Memory-Ergebnis.

Maschinenlesbarer Vertrag:
[S2AC_STATISCHER_T0B_ABSCHLUSS_UND_AUSWAHL_DES_KONTROLLIERTEN_BROWSER_REZEPTOR_GATES_V1.json](S2AC_STATISCHER_T0B_ABSCHLUSS_UND_AUSWAHL_DES_KONTROLLIERTEN_BROWSER_REZEPTOR_GATES_V1.json).
