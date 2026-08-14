# S1-EC110: Geschlossene Besitzer-Scope-Token-Factory

## Grenze

Die Fortsetzungsnachricht `ok weiter` ist keine neue ausdrueckliche Freigabe
eines realen EC67-Laufs. Deshalb darf EC110 keinen Besitzer-Token erzeugen und
enthaelt bewusst keinen vorgegebenen Freigabetext.

## Vertrag

Ein kuenftiger Besitzer-Token muss eine extern attestierte neue
Besitzerfreigabe, Thread- oder Sitzungsbindung, aktuelles Gate, EC59-Handoff,
maximal 3.208 Schritte, Nichtpersistenz und Retry-Verbot gemeinsam binden. Ein
synthetischer Scope darf niemals als Besitzerfreigabe akzeptiert werden.

Die externe Freigabe darf nicht im Forschungsmodul selbst konstruiert werden.
Sie muss nach einer neuen exakten Besitzerbotschaft durch eine getrennte
Vertrauensbruecke erzeugt werden.

## Umsetzung

Die Factory-Schnittstelle ist vorhanden, lehnt aber derzeit jede Anfrage
fail-closed ab. Es gibt weder einen Defaulttext noch eine Fallbackfreigabe oder
eine Umdeutung von `ok weiter`.

Entscheidung:
`OWNER_SCOPE_TOKEN_FACTORY_CLOSED_NO_NEW_EXPLICIT_RELEASE`.

## Aussagegrenze

EC110 erzeugt keinen Token, veraendert EC67 nicht, fuehrt nichts aus,
persistiert nichts und oeffnet weder Realresultat-Einlass noch Claims.

## Bester naechster Schritt

Am besten geht es mit S1-EC111 weiter: die externe Besitzerfreigabebruecke nur
statisch spezifizieren, einschliesslich exakter Abgrenzung zwischen
Fortsetzungsbefehl und Lauffreigabe. Noch keine Tokenausgabe oder Ausfuehrung.
