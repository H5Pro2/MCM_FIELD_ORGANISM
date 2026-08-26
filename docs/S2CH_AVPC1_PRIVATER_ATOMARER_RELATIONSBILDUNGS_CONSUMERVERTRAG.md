# S2-CH: Privater atomarer AVPC-1-Relationsbildungs-Consumer

## Praezisierte Quellen

Das PPB-1-Bildungsergebnis bindet die abgeschlossenen auditiven und visuellen
Bankzustaende. Es enthaelt aber weder die urspruenglichen Frame-Objekte noch
read-only Prototypbefunde. Deshalb reicht das Bildungsergebnis allein fuer eine
quellgebundene AVPC-1-Relationsbildung nicht aus.

Der Consumer muss zusaetzlich den authentischen Bildungsumschlag erhalten. Das
ausgewaehlte auditive und visuelle Frame muessen exakte Bestandteile seiner
beiden Streams sein. Prototyp-IDs oder Paar-IDs duerfen nicht von aussen als
Ersatz eingegeben werden. Die beiden Prototypbefunde werden intern mit der
bereits vorhandenen read-only Probe aus den gebundenen Frames und den
abgeschlossenen Bankzustaenden erzeugt.

## Eigentumsgrenze

Eine private Owner-Instanz autorisiert genau einen begonnenen Versuch. Sie
bindet Bildungsergebnis, Bildungsumschlag, Profil, Zeitaudit,
Relationspartition, beide Frame-Provenienzen und den Relationsvorzustand.
Nach Beginn endet sie entweder `CONSUMED` oder `FAILED`. Ein Retry, eine
Reparatur oder ein Teilcommit ist nicht zulaessig.

Die Garantie gilt pro Owner-Instanz. Eine globale oder persistente
Einmaligkeitsgarantie wird nicht behauptet.

## Verbindliche Reihenfolge

Nach vollstaendiger Quellpruefung ruft der Consumer die vorhandene read-only
Probe genau einmal je Modalitaet auf. Beide Befunde muessen auf die exakten
Frames, Konfigurationen, Bankzustaende und stabilisierten Prototypinventare
zurueckgebunden werden.

Danach wird genau ein vorhandener Ueberlappungsbeleg gebildet und vollstaendig
geprueft. Erst dann darf der bestehende begrenzte Relationskern genau einmal
fortgeschrieben werden. Vor dem Commit werden Ereignis, Vorzustand,
Nachzustand, ausgewaehlter Slot und alle Quelldigests erneut geprueft.

Nur `PAIR_CREATED_PENDING`, `PAIR_CONFIRMED_STABLE` und
`KEY_MARKED_CONFLICTED` koennen ein vollstaendiges Ergebnis bilden. Ein
zustandserhaltendes Ablehnungsereignis, ein Kindfehler oder eine abweichende
Kindausgabe beendet den Owner ohne Ergebnis.

## Grenzen

Der Consumer fuegt keine Speicher-, Distanz-, Kapazitaets-, Support-,
Konflikt- oder Matchregel hinzu. Seine staerkste Gegenbaseline ist dieselbe
atomare Huelle um die bereits bestehende generische Relationstabelle. Der
Vertrag beschreibt daher eine private Engineeringkomponente, keinen neuen
Feldmechanismus und keinen Nachweis einer MCM-spezifischen Memory.

## Naechster Schritt

S2-CI soll ausschliesslich statisch pruefen, ob alle Typen, Quellen,
Rueckbindungen, Kindaufrufe, Owner-Zustaende und synthetischen Testrollen ohne
neue Regel eindeutig materialisierbar sind.

Implementierung, Tests, Zustandsausfuehrung, Abruf, Feldwirkung, Produktion,
Livepfade und oeffentliche API bleiben gesperrt.
