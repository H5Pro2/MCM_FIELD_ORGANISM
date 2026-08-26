# S2-AP: Statische atomare Besitzerkorrektur

## Ergebnis

S2-AP schliesst die in S2-AO gefundene Einmalverbrauchsluecke auf
Vertragsniveau. Der wertbasierte S2-AN-Funktionseinstieg wird durch einen
privaten In-Memory-Besitzer mit der Methode `consume_once` ersetzt.

Die Garantie gilt bewusst fuer genau eine Besitzerinstanz, eine
vorregistrierte Autorisierung und einen terminalen Versuch. Globale oder
prozessuebergreifende Einmaligkeit wird nicht behauptet. Ein spaeterer
kontrollierter Runner muss genau eine Besitzerinstanz pro registrierter
Autorisierung erzeugen.

## Besitzerzustand

Der Besitzer bindet Owner-, Autorisierungs- und Consumption-ID sowie die
Digests von Huelle, Profil und beiden frischen Bankvorzustaenden. Der initiale
Zustand lautet `AUTHORIZED`, Versuch null, Nutzung null und Generation null.

Stabile Endzustaende sind `CONSUMED` und `FAILED`. `IN_PROGRESS` ist nur ein
interner Zustand waehrend des exklusiven Aufrufs und wird nicht als
abgeschlossener Snapshot ausgegeben. Das Synchronisationsobjekt selbst gehoert
nicht zum kanonischen Zustandsdigest.

## Vorpruefung und Versuchsbeginn

`consume_once` haelt fuer den gesamten Aufruf einen exklusiven,
nicht wiedereintretenden Lock. Vor jedem PPB-1-Schritt werden aktueller
Besitzerzustand, Eingabetypen, alle Autorisierungsdigests, frische
Bankzustaende und der vollstaendige Zeitplan geprueft.

Eine abgewiesene Vorpruefung ruft keinen Lebenszyklusschritt auf und veraendert
den Besitzer nicht. Nur in diesem Fall darf ein korrigierter Aufruf folgen.
Nach bestandener Vorpruefung beginnt genau ein terminaler Versuch.

## Erfolg und Fehler

Bei Erfolg werden das vollstaendige Bildungsergebnis und der Besitzerzustand
`CONSUMED/Versuch 1/Nutzung 1/Generation 1` gemeinsam festgelegt.

Tritt nach Versuchsbeginn ein Fehler auf, wird kein Audio-, Video- oder
Teilergebnis veroeffentlicht. Der Besitzer endet jedoch terminal als
`FAILED/Versuch 1/Nutzung 0/Generation 1` mit Fehlercode und Fehlerdigest.
Diese Regel loest den Widerspruch zwischen unveraendertem Fehlerzustand und
gleichzeitig verbotenem Retry: Nach einem begonnenen Versuch ist jede
Wiederholung gesperrt.

Ein zweiter oder gleichzeitiger Aufruf wartet auf den exklusiven Abschnitt und
wird danach vor jedem Lebenszyklusschritt verworfen, sobald der Besitzer
`CONSUMED` oder `FAILED` ist.

## Grenze und naechster Schritt

S2-AP implementiert und fuehrt nichts aus. Der Besitzer ist keine neue PPB-1-
Speicherregel und kein globaler Ledger. API, Snapshot, Produktion, Live-Pfad,
Feld, Probe und Baselines bleiben unveraendert.

S2-AQ soll die korrigierte Besitzer- und Verbrauchsgrenze statisch auf
Vollstaendigkeit, Konkurrenzverhalten und Materialisierbarkeit pruefen. Erst
danach kann eine private Implementierung erwogen werden.

Maschinenlesbare Vertragskorrektur:
[S2AP_STATISCHE_PRIVATE_ATOMARE_BILDUNGSVERBRAUCHER_BESITZERKORREKTUR_V1.json](S2AP_STATISCHE_PRIVATE_ATOMARE_BILDUNGSVERBRAUCHER_BESITZERKORREKTUR_V1.json).
