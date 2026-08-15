# S1-JU: STOPP aeusserer Geometrie- und interner Kantendigest nicht getrennt

## Ergebnis

S1-JU stoppt die Adapterimplementierung vor dem ersten Baselinekern. Die
fokussierte Vorpruefung zeigt, dass der modellseitige S1-JO-Geometriedigest
und der interne MCM-Kanteninventardigest zwei verschiedene, jeweils gueltige
Rollen besitzen. S1-JT hat diese Rollen fuer das B1-Payload noch nicht
eindeutig getrennt.

## Zwei Digestrollen

Der aeussere gemeinsame Geometriedigest stammt aus S1-JG bis S1-JK und wird
in der vierwertigen S1-JO-Modellaufrufhuelle ausgegeben. Er bindet die
registrierte offene Liniengeometrie als gemeinsame Expositionsidentitaet.

Der interne Kanteninventardigest wird direkt aus der vollstaendigen
`MCMNeuronLayer` berechnet. Er bindet Knotenidentitaeten, Positionen,
Samplingoffsets und daraus abgeleitete ungerichtete Kanten. Genau diesen
Digest verlangen `DTS1BackreactionResult`, `MCMSubstrateState` und die F3-
Kernvalidierung.

Die festen Paare lauten:

- Zweiknotenlinie: aussen `5f7bdc4e…810d`, intern `77595b85…6b72`.
- Dreiknotenlinie: aussen `2efcf504…aa49`, intern `2536e5e2…273a`.

Beide Paare sind ungleich. Ein generischer Gleichheitstest lehnt deshalb
jeden ansonsten gueltigen B1-bis-B6-Aufruf vor dem Kern ab.

## Betroffene Bruecken

B1 muss in seinem festen Adapterpayload den internen Digest verwenden, weil
der typisierte Kantenratenrecord ihn verlangt. B3 bis B6 tragen den korrekten
internen Digest bereits im M-Zustand, benoetigen aber weiterhin eine explizite
Pruefung des registrierten aeusseren/inneren Paares. B2 besitzt keinen
Kantendigest im S2-Zustand, muss die Paarzuordnung dennoch als
Geometrieintegritaet pruefen.

Gesperrt sind das Umbenennen bestehender Digests, eine neue Digestfunktion,
das Durchreichen des aeusseren Digests in interne Kernelobjekte sowie das
Weglassen einer der beiden Pruefrollen.

## Entscheidung

`STOPP_OUTER_COMMON_GEOMETRY_AND_INTERNAL_EDGE_INVENTORY_DIGEST_ROLES_NOT_SEPARATED`

Kanonischer Auditdigest:

`77ce8f1e14f6db2bbfa4bfeacaf911a9b20a5b5a59849c1d376649b79ed482c3`

Es wurde kein Adapter akzeptiert, kein Baselinekern aufgerufen und kein
Profilfall ausgefuehrt. Alle bisherigen Zeiten, Digests, Payloadwerte und
Kerne bleiben unveraendert.

## Naechster zulaessiger Schritt

S1-JV darf ausschliesslich fuer beide registrierten Geometrien die endliche
Zuordnung von aeusserem zu internem Digest samt Auswahl durch Feldidentitaet
und Knotenbestand binden. Das B1-Payload muss eindeutig den internen Digest
verwenden; B2 bis B6 muessen beide Rollen pruefen, ohne sie gleichzusetzen.
Noch keine Implementierung, kein Kernaufruf, keine Runtime oder
Forschungsprobe.
