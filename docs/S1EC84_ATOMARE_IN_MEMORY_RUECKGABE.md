# S1-EC84: Atomare In-Memory-Rueckgabe

## Zweck

S1-EC84 verhindert die in EC78 sichtbar gewordene Auswertungsluecke. Ein
bereits abgeschlossenes EC67-Ergebnis wird erst dann als technischer Erfolg
zurueckgegeben, wenn EC82 und EC80 daraus im selben Prozess erfolgreich eine
`r2`-Skalarquittung erzeugt haben.

Das gemeinsame Rueckgabeobjekt enthaelt:

- den Digest und das In-Memory-Objekt des EC67-Ergebnisses;
- den Digest und das In-Memory-Objekt der EC80-Skalarquittung;
- vier Formationen, acht frische Felder, acht Proben und 3.208 Schritte;
- sechs zweikomponentige Kontraste;
- die explizite Bindung beider Objekte ueber denselben Ergebnis-Digest.

## Atomare Grenze

EC84 konstruiert das Rueckgabeobjekt erst nach erfolgreicher
Skalarreduktion. Bei einem Typ-, Vertrags-, Handoff- oder Reduktionsfehler
wird eine Exception ausgelöst und kein EC84-Erfolg zurueckgegeben. Der
Wrapper selbst startet keinen Koordinator und fuehrt keine weiteren
Feldschritte aus.

## Grenzen

Die Abnahme verwendet nur die synthetische typisierte EC76-Formroute. EC84
persistiert weder Rohvektoren noch Skalare, enthaelt keine Besitzerfreigabe
und trifft keine EC46- oder Forschungsentscheidung. Es gibt keinen Memory-,
Feldzeit-, Organisations-, Topologie-, Semantik-, Selbstregulations- oder
KI-Nachweis.

Am besten geht es mit S1-EC85 weiter: einen statischen Gesamtpreflight fuer
den geschlossenen EC83/EC84-Messpfad erstellen. Er muss aktuelle Ressourcen,
Quellintegritaet, Schutzartefakte, exakt 3.208 Maximalschritte und die
weiterhin fehlende neue Besitzerfreigabe gemeinsam ausweisen.
