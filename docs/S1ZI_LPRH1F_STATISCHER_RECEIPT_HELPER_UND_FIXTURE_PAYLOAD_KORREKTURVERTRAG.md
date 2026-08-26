# S1-ZI: Statischer Receipt-, Helper- und Fixture-Payload-Korrekturvertrag

## Ergebnis

S1-ZI schliesst die drei S1-ZH-Luecken statisch. Der Ableitungs-Receipt ist nun
als eigenes unveraenderliches Objekt im abgeleiteten Drive-Satz verschachtelt.
Seine Felder und sein Digest muessen exakt mit dem Drive-Satz uebereinstimmen.
Das fruehere unverbundene Receipt-ID-Feld wird dadurch eindeutig ersetzt.

Der Ableitungshelper erhaelt acht eigene Fehlercodes. Layer, Zielschritt,
Kontaktmapping und Transientmapping werden vor und nach der Ableitung kanonisch
gebunden. Jede Aenderung stoppt ohne Teilergebnis.

## Endliche Fixture

Die vier Handoff-Arme binden nun konkrete PPB-1-Konfigurationen, Zustaende,
Proben, Findings, Zeitfenster, Dock- und Rezeptorpayloads. Die vier anderen
Arme binden ihre generischen Quellen und lokalen Werte direkt. Fuer alle acht
Arme ist der vollstaendige erwartete Folgelayer-Payload festgelegt, nicht nur
ein Aktivierungswert oder eine paarweise Relation.

## Grenze

S1-ZI ist weiterhin nur ein Vertrag. S1-ZJ muss Receiptkette, Fehlerordnung,
Quellenregister und Folgelayer-Payloads statisch abnehmen. Helper, Adapter,
Fixture und Layerlauf bleiben gesperrt. LPRH-1F bleibt generisch reduzierbares
Engineering ohne Feldwirkungs-, Memory- oder MCM-spezifischen Befund.

Maschinenlesbarer Vertrag:
[S1ZI_LPRH1F_STATISCHER_RECEIPT_HELPER_UND_FIXTURE_PAYLOAD_KORREKTURVERTRAG_V1.json](S1ZI_LPRH1F_STATISCHER_RECEIPT_HELPER_UND_FIXTURE_PAYLOAD_KORREKTURVERTRAG_V1.json).
