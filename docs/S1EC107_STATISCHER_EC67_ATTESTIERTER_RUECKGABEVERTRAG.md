# S1-EC107: Statischer attestierter EC67-Rueckgabevertrag

## Aktuelle Luecke

EC67 akzeptiert derzeit nur `preflight_and_owner_released: bool`. Dieses Signal
ist nicht verbrauchbar und bindet weder Besitzerfreigabe noch Gate, Handoff oder
Schrittbudget in einem Token. EC67 gibt ausserdem nur das nackte Resultat
zurueck.

## Vorgesehene Korrektur

Ein neuer prozessinterner Einmallauftoken muss Besitzerfreigabe, aktuelles
r2-Release-Gate, EC59-Handoff und maximal 3.208 Feldschritte gemeinsam binden.
Er wird unmittelbar vor dem ersten Adapteraufruf genau einmal verbraucht.

Nach erfolgreicher Ausfuehrung validiert EC67 zuerst das vollstaendige Resultat,
erzeugt danach innerhalb desselben Koordinatoraufrufs die r2-
Produzentenquittung und gibt beide Objekte in einer unveraenderlichen Huelle
gemeinsam zurueck. Ein nacktes Resultat oder eine nachtraegliche Quittung sind
danach unzulaessig.

## Fehlersemantik

- Vor Tokenverbrauch: null Adapteraufrufe, Token bleibt frisch, keine Quittung.
- Nach Tokenverbrauch: Versuch ist verbraucht, kein Retry, keine Quittung und
  kein Teilerfolg bei Abbruch.
- Erfolgreich: exakt vier Formationen, acht Proben und 3.208 Schritte; Resultat
  und Quittung werden atomar gebunden zurueckgegeben.

## Status und Grenze

`EC67_ATTESTED_RETURN_INTEGRATION_SPECIFIED_NOT_IMPLEMENTED`

EC107 implementiert weder Token noch Rueckgabehuelle und veraendert EC67 nicht.
Es liegt keine Besitzerfreigabe fuer einen neuen Lauf vor. Realresultat-Einlass,
Ausfuehrung, Persistenz, Retry und Claims bleiben geschlossen.

## Bester naechster Schritt

Am besten geht es mit S1-EC108 weiter: Token und atomare Rueckgabehuelle
isoliert implementieren und mit einem Null-Adapter-/Verbrauchsfixture testen.
EC67 selbst bleibt dabei noch unveraendert; keine reale Ausfuehrung.
