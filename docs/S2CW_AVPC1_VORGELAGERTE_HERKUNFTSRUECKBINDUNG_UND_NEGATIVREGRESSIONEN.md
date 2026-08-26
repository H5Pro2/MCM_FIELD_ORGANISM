# S2-CW: Vorgelagerte Herkunftsrueckbindung und Negativregressionen

## Ergebnis

S2-CW schliesst ausschliesslich die drei in S2-CV gefundenen vorgelagerten
Herkunftsgrenzen des privaten AVPC-1-End-to-End-Evaluators.

Der initiale Relationszustand wird jetzt vor dem ersten Relationsschritt an
die erwartete Tabellen-ID, das Profil, beide Bankzustaende und Inventare, die
Relationspartition, den leeren Verbrauch und die beiden freien Slots
zurueckgebunden.

Jede auditive Probenhuelle wird vor der read-only Probe an ihre Binding-ID,
Quellbindung, Sequenz, Profil- und Bankidentitaet, Relationspartition,
Zeitfenster, Eingabeprojektion sowie genau einen auditiven und null visuelle
Eingaenge zurueckgebunden.

Jeder auditive read-only Befund wird vor dem atomaren Endabruf an die konkrete
Probe-ID, auditive Bank und Konfiguration, den beobachteten Bankzustand und die
exakte Eingabeprojektion zurueckgebunden.

## Drei Negativregressionen

Genau drei neue Tests ersetzen jeweils eine intern gueltige Ausgabe durch
eine gueltige, aber fuer den beabsichtigten Aufruf fremde Ausgabe:

1. Ein Initialzustand mit fremder Tabellen-ID wird vor dem ersten
   Relations-Consumer verworfen.
2. Eine Audio-only-Huelle mit fremder Binding-ID wird vor der read-only Probe
   verworfen.
3. Ein auditiver Finding mit fremder Probe-ID wird vor dem atomaren Endabruf
   verworfen.

Alle drei Composite-Owner enden `FAILED`. Kein Gesamtresultat und keine
Teilausgabe werden als gueltiges Ergebnis veroeffentlicht.

## Testevidenz

Der gebundene fokussierte Integrationsumfang fuer Relationskern, atomaren
Leseconsumer, Relationsbildungs-Consumer und End-to-End-Evaluator besteht mit
`50/50` Tests in `1.239 s`.

Der erste Versuch mit dem System-Python ueber `pytest` war nicht ausfuehrbar,
weil dort das optionale Paket `pytest` fehlt. Der im Projekt fuer diesen
Umfang gebundene `unittest`-Befehl wurde danach unveraendert ausgefuehrt.

## Einordnung

S2-CW veraendert keine Mechanik, Parameter, Fixturewerte oder Comparatoren.
Oeffentliche API, Snapshot, Produktions-, Feld-, Live- und Semantikpfade
bleiben unberuehrt.

Die technische Beweiskette besteht im fokussierten Umfang. Die
Funktionsentscheidung bleibt unveraendert
`FUNCTION_VALID_BASELINE_EXPLAINS`: AVPC-1 bleibt eine durch die generische
Vergleichsbasis erklaerte Engineeringfunktion und kein MCM-spezifischer
Memory-Befund.

## Naechster Schritt

S2-CX soll die korrigierte Composite-Quellkette rein statisch abschliessend
pruefen. Dabei werden keine Tests oder Zustandsfunktionen erneut ausgefuehrt
und keine neue Funktion freigegeben.
