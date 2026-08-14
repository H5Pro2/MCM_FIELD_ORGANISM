# S1-EC104: Statisches Realresultat-Provenienzgate

## Forschungsfrage

Kann das Projekt allein aus den aktuellen EC67-/EC96-Resultatcontainern
belastbar unterscheiden, ob ein Ergebnis wirklich durch den gebundenen
Koordinatorlauf entstand oder nur synthetisch in derselben Form konstruiert
wurde?

## Befund

Nein. Die aeusseren Resultatvertraege und verschachtelten Quittungen sind
validierbar. Die derzeitigen Realmarker sind jedoch konstruierbare Felder:
`execution_mode`, Schrittzahlen, Autorisierungsdigest,
`authorization_consumed` und `exactly_once_completed`.

EC103 belegt die Luecke kontrolliert: synthetische EC67-/EC96-Container koennen
ihre aktuellen aeusseren Vertraege erfuellen, ohne einen Feldkern oder
Koordinator aufzurufen. Deshalb waere es unzulaessig, allein aus dieser Form
eine reale Ausfuehrungsherkunft abzuleiten.

## Gateentscheidung

`REAL_RESULT_PROVENANCE_NOT_ESTABLISHED_INGRESS_CLOSED`

Das Gate haelt den EC102-Einlass fuer als real deklarierte Ergebnisse
geschlossen. Es startet keinen Lauf, extrahiert keine Resultate, persistiert
nichts und trifft keine EC46- oder Forschungsentscheidung.

## Erforderliche Korrektur

Vor einem realen Einlass braucht es eine atomare Produzentenquittung, die
mindestens bindet:

- Produzentenkennung;
- verbrauchte Einmallaufautorisierung;
- beide Quellresultatdigests;
- alle 24 Probequittungsdigests;
- die gebundene Schrittbilanz;
- die Produzentenreihenfolge;
- einen Gesamtdigest der Attestation.

Auch diese Quittung ist ein technischer Herkunftsvertrag und kein
wissenschaftlicher Ergebnisnachweis.

## Bester naechster Schritt

Am besten geht es mit S1-EC105 weiter: den atomaren
Produzentenquittungsvertrag rein statisch spezifizieren und gegen EC67, EC96
und EC102 binden. Noch keine Koordinatoraenderung, Ausfuehrung oder
Laufautorisierung.
