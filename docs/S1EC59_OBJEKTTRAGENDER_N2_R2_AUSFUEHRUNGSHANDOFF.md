# S1-EC59: Objekttragender n2/r2-Ausfuehrungshandoff

## Zweck

S1-EC59 schliesst die in EC58 lokalisierte Implementierungsluecke zwischen
der typisierten EC57-Rollenmatrix und den privaten EC54-Real-Wrappern. Der
Handoff behaelt die konkreten Plan-, Sequenz-, Feld- und Zustandsobjekte, ohne
einen Feldkern aufzurufen.

## Umsetzung

`mcm_field_organism/e1_common_probe_n2_r2_object_handoff.py` bindet:

- exakt `n2/r2`;
- alle acht EC45-Common-Probe-Rollen in ihrer festgelegten Reihenfolge;
- vier eindeutige Bildungsrouten: aktiv AB/BA und bildungsablatiert AB/BA;
- den realen EC27-Wiederholungsplansatz;
- die feste Common-Probe-Quelle und ihren realen Verfeinerungsplansatz;
- das konkrete neutrale Ausgangsfeld und den konkreten neutralen
  E1-Ausgangszustand.

Alle acht Slots werden durch den vorhandenen EC54-Resolver aufgeloest. Die
vier spaeter benoetigten Bildungszustaende werden jeweils genau einer
aufgeloesten Route zugeordnet. Die Objekte bleiben im Handoff erhalten und
werden nicht vorzeitig auf Digests oder Tokens reduziert.

## Abnahme

- acht aufgeloeste Probenslots
- vier eindeutige Bildungsrouten
- null Feldschritte
- keine Fresh-Field-Kopie
- kein Bildungs- oder Probekernaufruf
- keine Persistenz
- keine Forschungsentscheidung
- kein Memory-Claim
- 14 fokussierte Tests bestanden

Handoff-Digest:

`5acf624ffaa209e058b74134a069946e21eb2db6609ad7db8301c2c122bca3cb`

## Bewertung

Die in EC58 festgestellte Objekttransportluecke ist damit geschlossen. Das
ist eine technische Pfadabnahme und keine Evidenz fuer zustandsabhaengige
Feldaufnahme oder Memory. EC60 hat zusaetzlich klargestellt, dass fuer eine
ausfuehrbare Gesamtfixture noch der enge Vier-Bildungs-/Acht-Proben-
Koordinator fehlt. Der reale 3.208-Schritte-Lauf bleibt gesperrt.

Am besten geht es mit S1-EC60 weiter: EC58 als neuen statischen Preflight mit
dem EC59-Handoff wiederholen. Geprueft werden muessen Handoff-Digest,
Objektrouten, Ressourcen, geschuetzte Artefakte und das Fehlen einer neuen
Einmallauffreigabe. Dabei werden weiterhin keine Feldschritte ausgefuehrt.
