# S1-EC83: Geschlossener r2-Einmallauf-Messvertrag

## Zweck

S1-EC83 bindet den vollstaendigen Ablauf fuer einen moeglichen kuenftigen
Messlauf, ohne ihn freizugeben oder auszufuehren:

1. frischer technischer Preflight;
2. neue ausdrueckliche Besitzerfreigabe;
3. genau ein EC67-Koordinatoraufruf;
4. unmittelbarer EC82-In-Memory-Handoff;
5. genau eine EC80-r2-Skalarquittung;
6. technischer Bericht ohne EC46-Entscheidung.

## Laufgrenze

- vier Formationen und maximal 1.608 Bildungsschritte;
- acht frische Felder;
- acht Proben und maximal 1.600 Probeschritte;
- insgesamt maximal 3.208 Feldschritte;
- hoechstens 900 Sekunden;
- sechs zweikomponentige Skalar-Kontraste als erwartete Messquittung;
- Abbruch bei Ausfuehrungs- oder Handofffehler;
- kein Retry und keine Nachparametrierung.

## Geschlossener Status

Die EC78-Freigabe ist verbraucht. EC83 besitzt keine neue
Besitzerfreigabe: `authorized_execution_count = 0` und
`execution_permitted = False`.

Rohvektoren, Skalar-Dateien und geschuetzte Artefaktaenderungen bleiben
gesperrt. Die Skalarquittung soll lediglich im selben Prozess gemeinsam mit
dem technischen Ergebnis zurueckgegeben werden. `r2` allein erlaubt keine
EC46-Gesamtentscheidung und keinen Memory-, Feldzeit-, Organisations-,
Topologie-, Semantik-, Selbstregulations- oder KI-Claim.

Am besten geht es mit S1-EC84 weiter: einen synthetischen kombinierten
Koordinator-Handoff-Rueckgabewrapper fuer EC83 implementieren. Er muss
beweisen, dass ein Ausfuehrungsergebnis und seine EC80-Skalarquittung
atomar gemeinsam zurueckgegeben werden und bei Handofffehler keine
unvollstaendige technische Erfolgsmeldung entsteht.
