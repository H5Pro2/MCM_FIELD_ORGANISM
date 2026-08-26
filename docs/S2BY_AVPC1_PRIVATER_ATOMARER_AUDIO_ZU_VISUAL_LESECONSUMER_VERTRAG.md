# S2-BY: Vertrag des privaten atomaren AVPC-1-Leseconsumers

## Zweck

S2-BY bindet genau einen privaten Consumer fuer den bereits vorhandenen
AVPC-1-Lesepfad. Der Consumer erfindet keine neue Speicher-, Relations- oder
Matchregel. Er uebernimmt ausschliesslich die atomare Zusammensetzung des
read-only Relations-Lookups und der visuellen Prototypzustandsaufloesung.

Der in S2-BX ausgelassene bestehende auditive Prototypbefund ist korrigiert
und als vierte erforderliche Pfadrolle gebunden: Probehuelle, auditiver
read-only Prototypbefund, Relations-Lookup und visueller Resolver.

## Aufrufregel

Der Consumer muss zuerst alle exakten Eingabetypen, Kennungen und
Quelldigests pruefen. Danach darf er den Relations-Lookup genau einmal mit den
unveraenderten Quellen aufrufen.

Bei `NO_MATCH` oder `NO_MATCH_CONFLICT` wird der visuelle Resolver nicht
aufgerufen. Stattdessen entsteht ein vollstaendiges eingefrorenes negatives
Ergebnis ohne visuellen Prototypzustand.

Nur bei `MATCH` darf der Resolver genau einmal mit demselben Relationszustand,
demselben visuellen Bankzustand und demselben Profil aufgerufen werden. Ziel,
Werte und Quelldigests muessen mit dem Relationsbefund uebereinstimmen. Vor
jeder Rueckgabe werden alle Eingabedigests erneut geprueft.

## Fehlergrenze

Ungueltige Eingaben, Quellabweichungen, Fehler eines Kindaufrufs,
substituierte Ergebnisse oder veraenderte Quellen liefern kein
Consumer-Ergebnis. Es gibt keinen Retry, keine Reparatur, keinen Fallback und
keine Teilausgabe. Negative Relationsbefunde sind dagegen gueltige,
vollstaendige technische Ergebnisse.

## Einordnung

Die staerkste Baseline ist dieselbe sequenzielle Relationspruefung mit
exaktem visuellen Lookup unter identischen eingefrorenen Quellen. Der
Consumer beansprucht keinen funktionalen Vorteil. Sein technischer Beitrag
ist die einzelne atomare Verantwortung fuer Reihenfolge, Quellrechecks,
negative Ergebnisse und das Verbot unvollstaendiger Ausgaben.

S2-BY erlaubt keine Implementierung, Ausfuehrung, Zustandsfortschreibung,
Feldrueckwirkung, oeffentliche API, Produktion, Livepfade oder Semantik.

## Naechster Schritt

S2-BZ soll statisch pruefen, ob alle Typen, Digestregeln, Kindaufrufe,
Fehlerpfade und neun synthetischen Testrollen widerspruchsfrei
materialisierbar sind. Erst ein bestandener Preflight darf eine private
Implementierung separat freigeben.
