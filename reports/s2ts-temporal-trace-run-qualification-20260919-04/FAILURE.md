# S2-TS: vollständige kanonische Beleggrenze

Qualifikations-ID: `S2TS-TEMPORAL-TRACE-RUN-QUAL-20260919-04`  
Status: `NOT_QUALIFIED`

Der Aufruf begann am vollständigen JSON-Rundlauf, erreichte aber noch nicht
die unabhängigen Spur- und Baselineprüfungen. `record["binding"]` enthält
nach dem zulässigen JSON-Schreib-/Leseweg Ereignislisten; `run.binding()`
liefert intern Ereignistupel. Der Verifikator vergleicht beide noch direkt und
bricht daher mit `BINDING_INVALID` ab.

Das ist ein weiterer unbehandelter Teil derselben Serialisierungsgrenze.
Keine NU-Payload, Rezeptor-/NJ-, Feld-/Memoryverarbeitung oder Hauptlauf
wurde ausgeführt. Kein Retry erfolgte.
