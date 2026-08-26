# S1-JV: Endliche Geometriedigest-Zuordnung

## Zweck

S1-JV behebt ausschliesslich den in S1-JU festgestellten Rollenkonflikt. Der
aeussere gemeinsame Geometriedigest und der interne Kanteninventardigest
bleiben verschieden. Fuer jede der beiden registrierten Geometrien wird
genau ein festes Paar gebunden.

## Endliche Zuordnung

Die Auswahl erfolgt ausschliesslich durch die vollstaendige Feldidentitaet
und den geordneten Knotenbestand:

- `mcm.s1jn.field.2n`, `node-a@(0), node-b@(1)`: aussen
  `5f7bdc4e...810d`, intern `77595b85...6b72`.
- `mcm.s1jn.field.3n`, `node-a@(0), node-b@(1), node-c@(2)`: aussen
  `2efcf504...aa49`, intern `2536e5e2...273a`.

Feld-, Layer- und Geometrieidentitaet sowie Knotenreihenfolge muessen im
selben Record uebereinstimmen. Unbekannte, partielle, umgeordnete oder ueber
die beiden Records gekreuzte Identitaeten werden vor jedem Adapterobjekt
abgelehnt. Modellrolle, Profil, Kontrolllabel, Refinement und Ergebnis duerfen
die Auswahl nicht beeinflussen.

## Rollenbindung

B1 validiert den aeusseren Digest an der Modellaufrufhuelle. Sein
`edge_inventory_digest` im festen Adapterpayload ist dagegen ausschliesslich
der interne Digest des ausgewaehlten Records.

B2 validiert den aeusseren Digest und den internen Layerbestand getrennt. In
den `S2ReferenceState` wird kein neues Digestfeld eingefuegt. B3 bis B6
validieren den aeusseren Digest an der Aufrufhuelle und den internen Digest im
eingebetteten M-Zustand.

Die Rollen werden nie gleichgesetzt. Vertauschen, Weglassen, Neuberechnen,
Umbenennen, Reparieren oder aus Kontroll- beziehungsweise Ergebnisdaten
Ableiten ist fail-closed gesperrt.

S1-JT bleibt als historischer Quellvertrag unveraendert. S1-JV ersetzt nur
dessen mehrdeutige B1-Digestrollenbeschreibung; Raten, Payloadformen,
Runtimewerte, Diagnostik, Ausgabe und Fehlergrenze bleiben bitgleich.

## Entscheidung

`FINITE_OUTER_TO_INTERNAL_GEOMETRY_DIGEST_MAPPING_BOUND_NO_IMPLEMENTATION_OR_EXECUTION`

Kanonischer Vertragsdigest:

`8878cc42b423cfed7721e39dc56181f870a0c76832cccee48aac592f5390fd30`

Es wurde kein Adapter implementiert oder konstruiert, kein Baselinekern
aufgerufen, kein Profilfall ausgefuehrt und keine Runtime angebunden.

## Naechster zulaessiger Schritt

S1-JW darf ausschliesslich die privaten Adapterrecords und sechs Bruecken
gemaess S1-JP, S1-JR, S1-JT und S1-JV implementieren und gegen technische
synthetische Einzelintervalle pruefen. Vor jedem Kern muss die vollstaendige
zweifache Digestrollenpruefung fehlschliessen koennen. Noch kein Fall der
24-Fall-Matrix, kein gemeinsamer Profilvergleich, keine Runtime und keine
Forschungsprobe.
