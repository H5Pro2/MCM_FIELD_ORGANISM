# S1-EC111: Statische externe Besitzerfreigabebruecke

## Zweck

EC111 trennt Workflow-Fortsetzung von einer echten Lauffreigabe. Nachrichten
wie `ok weiter`, `weiter`, `fahre fort` oder `entwickle weiter` erlauben nur die
Fortsetzung geschlossener Forschung, Dokumentation und Implementierung. Sie
autorisieren keinen Token und keinen Feldlauf.

## Explizite Lauffreigabe

Ein kuenftiger Freigabekandidat muss in einer neuen Besitzerbotschaft
gleichzeitig enthalten:

- exakte Laufkennung EC67-r2;
- genau einen Lauf;
- maximal 3.208 Feldschritte;
- Nichtpersistenz;
- kein Retry;
- aktuelles Release-Gate und EC59-Handoff;
- ausdrueckliche Absicht, reale Ausfuehrung zu autorisieren;
- Thread- oder Sitzungsbindung.

Fehlt ein Bestandteil oder ist die Formulierung mehrdeutig, bleibt die Bruecke
geschlossen. Alte Freigaben werden nicht uebernommen. Der Assistent darf keinen
Besitzerfreigabetext selbst erzeugen und als Eingabe verwenden.

## Status

`CONTINUATION_BOUND_RELEASE_BRIDGE_SPECIFIED_NOT_IMPLEMENTED`

Die Bruecke ist nur statisch spezifiziert. Es wird kein Freigabeartefakt und
kein Token erzeugt; EC67 und der Realresultat-Einlass bleiben geschlossen.

## Bester naechster Schritt

Am besten geht es mit S1-EC112 weiter: einen reinen, nicht ausfuehrenden
Nachrichtenklassifikator implementieren, der Fortsetzung, Frage, Stopp und
vollstaendigen Freigabekandidaten trennt und bei jeder Mehrdeutigkeit
fail-closed bleibt. Noch keine Tokenausgabe.
