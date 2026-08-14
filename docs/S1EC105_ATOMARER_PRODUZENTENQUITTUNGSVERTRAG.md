# S1-EC105: Atomarer Produzentenquittungsvertrag

## Zweck

EC105 spezifiziert statisch die Herkunftskette, die vor einem kuenftigen
Realresultat-Einlass fehlt. EC67 und EC96 muessen jeweils eine eigene
Produzentenquittung atomar mit ihrem Resultat liefern. EC102 darf erst aus
beiden validierten Quittungen eine gemeinsame Einlassattestation bilden.

Eine nachtraeglich allein aus bereits vorhandenen Resultatfeldern berechnete
Selbstattestation ist verboten, weil sie die von EC104 gezeigte
Provenienzluecke nur umbenennen wuerde.

## Bindung

Die EC67-r2-Quittung bindet genau ein Resultat, acht Probequittungen, 3.208
abgerechnete Feldschritte und eine neue explizite Einmallaufautorisierung.

Die EC96-r4/r8-Quittung bindet genau ein Resultat, sechzehn Probequittungen,
19.248 abgerechnete Feldschritte und die bereits vorhandene verbrauchte
EC96-Autorisierung.

Die EC102-Einlassattestation bindet beide Produzentenquittungen, beide
Resultatdigests, alle 24 Probequittungsdigests, insgesamt 22.456 Schritte und
die feste Reihenfolge `EC67-r2 -> EC96-r4-r8 -> EC102-ingress`.

## Vertrauensgrenze

Der Vertrag ist eine prozessinterne, digestgebundene Herkunftssicherung. Er
erkennt versehentliche Objekt-, Reihenfolge- oder Digestvertauschungen. Er ist
kein kryptographischer oder externer Beweis, dass physische Rechenarbeit
stattgefunden hat, und kein wissenschaftlicher Ergebnisnachweis.

## Aktueller Status

`ATTESTATION_CONTRACT_SPECIFIED_INTEGRATION_NOT_IMPLEMENTED`

EC67 besitzt noch kein explizites Autorisierungsobjekt und beide Produzenten
geben noch keine atomare Quittung zurueck. EC102 verlangt noch keine gemeinsame
Attestation. Deshalb bleiben Realresultat-Einlass, Ausfuehrung, Persistenz,
Retry, EC46 und Forschungsentscheidung geschlossen.

## Bester naechster Schritt

Am besten geht es mit S1-EC106 weiter: die beiden unveraenderlichen
Quittungsdatentypen und die kombinierte Einlassattestation isoliert
implementieren und rein synthetisch testen. Die Koordinatoren und EC102 bleiben
dabei noch unveraendert; keine reale Ausfuehrung oder Laufautorisierung.
