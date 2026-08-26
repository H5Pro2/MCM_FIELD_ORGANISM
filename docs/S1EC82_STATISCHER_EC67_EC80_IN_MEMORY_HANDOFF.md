# S1-EC82: Statischer EC67-zu-EC80-In-Memory-Handoff

## Zweck

S1-EC82 bindet den Zeitpunkt und den Typ der kuenftigen Messwertreduktion.
Nur ein bereits vollstaendig zurueckgegebenes und selbstvalidiertes
EC67-Ergebnisobjekt darf an EC80 uebergeben werden. EC80 reduziert dessen
acht Probequittungen im selben Prozess auf sechs `r2`-Kontraste.

## Bindung

- exakte Quellhashes von EC67 und EC80;
- Ergebnistyp `E1CommonProbeN2R2RealModeCoordinatorResult`;
- exakt acht Probequittungen;
- Quellergebnis-Digest wird in die EC80-Skalarquittung uebernommen;
- Reduktion unmittelbar nach Ergebnisrueckgabe im selben Prozess;
- Rohvektoren verlassen den Prozess nicht.

## Abnahme

Eine typisierte Formabnahme aus der rein synthetischen EC76-Route zeigt,
dass ein vollstaendiges EC67-Ergebnisformat an EC80 uebergeben und dort auf
sechs Skalarpaare reduziert werden kann. Die Abnahme startet keinen
Koordinator und keine Feldmechanik.

## Grenzen

EC82 autorisiert keine Ausfuehrung und enthaelt keine Besitzerfreigabe. Es
persistiert nichts und trifft weder eine EC46- noch eine
Forschungsentscheidung. Die Skalarquittung ist kein Memory-, Feldzeit-,
Organisations-, Topologie-, Semantik-, Selbstregulations- oder KI-Nachweis.

Am besten geht es mit S1-EC83 weiter: den gesamten kuenftigen Ablauf
`autorisierter EC67-Aufruf -> sofortiger EC82-Handoff -> EC80-r2-Quittung`
als nicht ausfuehrenden Einmallaufvertrag festlegen. Dabei muss klar bleiben,
dass `r2` allein keine EC46-Gesamtentscheidung erlaubt.
