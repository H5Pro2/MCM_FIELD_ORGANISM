# S1-EC108: Isolierter r2-Token und Rueckgabehuelle

## Umsetzung

EC108 implementiert einen prozessinternen Einmallauftoken und eine
unveraenderliche attestierte r2-Rueckgabehuelle isoliert vom EC67-Koordinator.
Der Token bindet Autorisierungsdigest, Gate-Digest, EC59-Handoff, maximal 3.208
Schritte, keine Persistenz und keinen Retry.

EC108 erzeugt ausschliesslich Token mit dem Scope `synthetic-fixture`. Ein
solcher Token ist keine Besitzerfreigabe und kann spaeter nicht als produktiver
EC67-Token akzeptiert werden.

Die Rueckgabehuelle verlangt einen bereits verbrauchten Token, ein typisiertes
r2-Resultat und dessen EC106-Produzentenquittung. Autorisierungs-, Resultat- und
Quittungsdigests sowie die Objektidentitaet des Resultats muessen durchgaengig
uebereinstimmen.

## Null-Adapter-Fixture

Die drei Phasen sind getrennt abgenommen:

- Abbruch vor Verbrauch: Token frisch, null Adapter, keine Huelle;
- Abbruch nach Verbrauch: Token verbraucht, kein Retry, keine Huelle;
- synthetischer Erfolg: Token verbraucht, Resultat und Quittung gebunden, null
  Adapteraufrufe und keine Ausfuehrungsfreigabe.

## Aussagegrenze

EC108 ruft EC67 und seine Adapter nicht auf, veraendert keinen Produktionscode,
persistiert nichts und oeffnet den EC104-Einlass nicht. Die synthetische Huelle
ist kein Nachweis eines Feldlaufs.

## Bester naechster Schritt

Am besten geht es mit S1-EC109 weiter: ein statisches Integrationsgate erstellen,
das die EC108-Typen gegen den konkreten EC67-Kontrollfluss und alle betroffenen
Rueckgabetyp-Verbraucher prueft. Noch keine EC67-Aenderung oder Ausfuehrung.
