# S2-TS: Quellen- und Verifikationsqualifikation

Qualifikations-ID: `S2TS-TEMPORAL-TRACE-RUN-QUAL-20260919-02`  
Status: `NOT_QUALIFIED`

Der einmalige neue Aufruf erreichte die Quellenplanauflösung, die synthetische
18-Endpunkt-Hülle und die unabhängige Verifikationsrechnung. Er endete bei
deren Vergleich der Spurentscheidungen mit `TRACE_DECISIONS_INVALID`.

Konkrete Ursache: Die produktive Spur liefert `offsets` intern als Tupel,
während die unabhängige Verifikation ihre kanonische Belegform als Liste
bildet. Beide Formen bezeichnen dieselben Offsets, sind aber vor der
kanonischen Serialisierung nicht gleich. Der Verifikator muss die Belegform
vor dem Vergleich ausdrücklich kanonisieren; die Entscheidung selbst wurde
nicht als fachlich falsch nachgewiesen.

Es wurden keine NU-Payloads materialisiert, keine Rezeptoren/NJ ausgeführt,
keine Feld- oder Memoryfunktion aufgerufen und kein S2-TS-Hauptlauf gestartet.
Kein Retry erfolgte. Die frühere `1/1`-Ereignisqualifikation und der
Spurzustandsbefund `3/3` bleiben historische Teilbelege, ersetzen diese
fehlgeschlagene Gesamtqualifikation nicht.
