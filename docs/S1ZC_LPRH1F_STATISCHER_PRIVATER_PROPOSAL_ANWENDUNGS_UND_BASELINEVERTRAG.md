# S1-ZC: Statischer privater Proposal-Anwendungs- und Baselinevertrag

## Technische Funktion

S1-ZC bindet eine moegliche private Ein-Schritt-Anwendung eines vollstaendigen
LPRH-1F-Proposal-Satzes. Ein spaeterer Adapter darf genau einmal
`MCMNeuronLayer.advance` aufrufen. Jeder dort neu erzeugte Drive muss
digestgenau dem vorbereiteten Drive entsprechen; erst dann darf der Adapter
die gebundene Proposal-Ausgabe fuer dieses Neuron zurueckgeben.

Ein eigener Layer-Anwendungs-Identifier und ein getrenntes Ledger verhindern
Wiederverwendung. Jeder Fehler vor oder waehrend der Anwendung liefert keinen
Folgelayer, kein Receipt und keine Ledgeraenderung.

## Staerkste Gegenbaseline

Kandidat und wertgleiche generische Baseline muessen dasselbe Layerobjekt,
denselben vorbereiteten Drive-Satz, dieselben Rezeptorkontakte und dieselben
lokalen Werte erhalten. Ihre numerischen Proposal-Ausgaben muessen bereits
vor der Anwendung identisch sein. Deshalb muessen auch numerischer Folgelayer
und Layerdigest exakt gleich sein.

Eine Abweichung waere kein Kandidatenvorteil, sondern ein Provenienzleck,
Implementierungsfehler oder methodisch ungueltiger Vergleich. Ein Gleichstand
bestaetigt nur die erwartete generische Reduzierbarkeit.

## Grenze

S1-ZC implementiert und fuehrt nichts aus. API, `SharedMCMField`, Kernklassen,
Snapshot, Produktion und reale Eingaben bleiben gesperrt. S1-ZD muss zuerst
statisch pruefen, ob der Vertrag ohne neue Kernentscheidung eindeutig
materialisierbar ist.

Maschinenlesbarer Vertrag:
[S1ZC_LPRH1F_STATISCHER_PRIVATER_PROPOSAL_ANWENDUNGS_UND_BASELINEVERTRAG_V1.json](S1ZC_LPRH1F_STATISCHER_PRIVATER_PROPOSAL_ANWENDUNGS_UND_BASELINEVERTRAG_V1.json).
