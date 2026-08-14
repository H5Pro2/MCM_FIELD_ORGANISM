# S1-FD: Synthetischer E1-Bildungszustands-Konvergenzauswerter

## Umsetzung

S1-FD implementiert den in S1-FC gebundenen Auswerter ohne Feld- oder
Probeausfuehrung. Eingabe ist genau ein atomarer Satz aus 15 synthetischen,
digestgebundenen Kantenbelegungsvektoren fuer r2/r4/r8 und die fuenf
festgelegten Bildungsrollen. Unvollstaendige Inventare, abweichende
Kantenreihenfolgen und veraenderte Zustandsdigests schliessen die Auswertung.

## Entscheidungsgang

Die Auswertung trennt drei Konvergenzkomponenten:

- aktives AB;
- aktives BA;
- aktives AB minus aktives BA als Ordnungszustand.

Fuer jede Komponente werden r2/r4- und r4/r8-L-infinity-Abstand sowie der
relative r4/r8-Abstand zum r8-Zustand bestimmt. Die vor S1-FD gebundenen
Grenzen `1e-12` und `0.01` bleiben unveraendert. Die Entscheidung erfolgt
fail-closed: Kontrollfehler vor fehlendem Ordnungszustand, fehlender
Ordnungszustand vor Nichtkonvergenz und erst danach ein rein diagnostischer
Konvergenzausgang.

## Synthetische Abnahme

Die Tests decken kontrolliert ab:

- eine konvergierende Reihe mit unterscheidbarem AB/BA-Ordnungszustand;
- eine nicht konvergierende Reihe;
- eine Identitaetskontrollverletzung;
- eine Reihe ohne unterscheidbaren Ordnungszustand;
- fehlende Vektoren, falsche Kantenordnung und Digestveraenderung.

Der positive synthetische Ausgang lautet
`FORMATION_STATE_CONVERGED_DIAGNOSTIC_ONLY`. Er zeigt nur, dass der Auswerter
seinen Vertrag korrekt anwendet. Er ist kein empirischer E1-Befund.

## Grenzen

S1-FD erzeugt keine realen E1-Zustaende, fuehrt kein Feld und keine Probe aus,
schreibt keine Ergebnisartefakte und veraendert EC46 nicht. Es folgt kein
Nachweis von Memory, Feldzeit, Organisation, Semantik, Selbstregulation oder
KI.

## Bester naechster Schritt

Am besten geht es mit S1-FE weiter: statisch einen einmaligen
Bildungszustands-Capturevertrag entwerfen, der die bereits vorhandene
Formation genau an ihrem Endpunkt und vor jeder Probe an die 15
S1-FD-Vektoren bindet. Noch keine Ausfuehrung oder Autorisierung.
