# S2-BT: Privater read-only Resolververtrag

## Zweck

S2-BT bindet den kleinsten fehlenden Consumerbaustein nach dem positiven
AVPC-1-Relationsbefund. Der Resolver soll einen bereits gebundenen visuellen
Prototypdigest gegen genau einen stabilisierten Slot derselben eingefrorenen
visuellen PPB-1-Bank aufloesen.

Der Resolver bildet keinen neuen Zustand und veraendert keine Bank. Er stellt
nur einen bereits vorhandenen verdichteten Prototypzustand mit vollstaendiger
Quellbindung read-only bereit.

## Eingaben und Ausgabe

Die spaetere Funktion erhaelt eine technische Resolver-ID, einen positiven
`AVPC1ReadOnlyRelationFinding`, den exakten `AVPC1BoundedRelationState`, das
exakte `PPB1ReceptorProfileBinding` und den exakten visuellen
`PPB1BankState`.

Die Ausgabe `AVPC1ReadOnlyVisualPrototypeState` darf ausschliesslich enthalten:

- Digests von Relationsbefund, Relationszustand, Profil, visueller
  Konfiguration und visueller Bank;
- Relations- und Prototypslotidentitaet;
- visuellen Prototypdigest;
- Modalitaet, Geometrie und Carrieridentitaeten;
- die bereits vorhandenen normalisierten Prototypwerte und ihren Support;
- einen Digest des vollstaendigen Ausgabezustands.

## Aufloesungsregel

Es ist nur ein exakter SHA-256-Identitaetsvergleich mit der vorhandenen
`_prototype_digest`-Regel zulaessig. Genau ein belegter Slot mit mindestens
`stable_after` Support muss den Zieldigest besitzen. Distanzsuche,
Gleichstandsregel, Fallback, Aktualisierung, Wertkonvertierung oder
Carrierumsortierung sind ausgeschlossen.

Der im Relationsbefund benannte Relationsslot muss im gebundenen
Relationszustand stabil sein und denselben visuellen Zieldigest tragen.

## Fail-Closed-Grenze

Negative oder konfliktbehaftete Relationsbefunde erzeugen keine leere
Ersatzausgabe, sondern werden abgewiesen. Dasselbe gilt fuer abweichende
Quellen, einen instabilen, fehlenden oder mehrfach vorkommenden Zieldigest und
jede Aenderung eines Eingabedigest waehrend der Aufloesung.

## Einordnung und naechster Schritt

Die staerkste Baseline ist derselbe exakte Digestzugriff auf dieselbe
eingefrorene Bank. Der Resolver beansprucht keinen funktionalen Vorteil; seine
Rolle sind Provenienzpruefung, atomare Ausgabe und Fail-Closed-Verhalten.

S2-BU soll statisch pruefen, ob alle Typen, Digestregeln und synthetischen
Testfaelle widerspruchsfrei materialisierbar sind. Implementierung,
Ausfuehrung, oeffentliche API und Feld- oder Produktionspfade bleiben bis
dahin gesperrt.
