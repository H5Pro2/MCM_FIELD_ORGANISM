# S2-NT: neutrale Quellenbindungsqualifikation

Lauf-ID `s2nt-source-binding-qualification-20260908-01`.
Ergebnis: `S2NT_SOURCE_BINDING_QUALIFIED`, **16/16**, Exit-Code `0`.
Genau ein vorab gebundener Unittest-Aufruf; kein Retry.

Das Inventar in `preregistration.json` wurde mit Befehl, Quellhashes,
Interpreterumgebung und Budgets vor dem Test gespeichert. Alle 16 Testkoerper
wurden erreicht; `stderr.txt` dokumentiert `Ran 16 tests` und `OK`.
Resultdigest:
`cfa5460ba5852b4801da39273226a3534b228c79623e0a3d71088e7d87cee347`.

Geprueft sind literale Metadaten fuer 14 Quellen, unveraenderliche Rezeptform,
getrennte Exaktquellenidentitaeten, Gruppenreihenfolge, erhaltene
Nullpartialpositionen, Phasenseeds, native Fenster und Snapshotindizes
einschliesslich e01/e02 beziehungsweise spaeter Fenster und Fehlbindungen.
25 Vergleichspaare und 24 strikte Ordnungskontrollen, getrennte Planwurzeln,
Quellenmanipulationen, Profile, Budgets und Publikationskonflikte sind abgedeckt.
Die unabhengige Verifikation akzeptiert gueltige synthetische Metadaten und
weist manipulierte Quellen, Zeiten, Paare und Bewertungen typisiert ab.

Einziger PCM-Test war eine fremde neutrale Zwei-Sample-Fixture mit zwei
Gruppen, je drei Partialpositionen, acht Payloadbytes und zwoelf
Generator-Sinusaufrufen. Zwoelf weitere Sinusauswertungen dienten nur der
neutralen Referenz. Phasen-/Winkelreihenfolge und abschliessende Float32-Bytes
stimmen exakt; keine NT-Payloads wurden erzeugt.

Das lokal geladene `math` ist durch `__spec__.origin == 'built-in'` und
Zugehoerigkeit zu `sys.builtin_module_names` gebunden. Keine erfundene
Moduldatei; die bestehende dateibasierte Alternativbindung bleibt erhalten.
Kein Rezeptor- oder NJ-Import, keine Analyse, Distanz- oder Systemausfuehrung.
Alle vor/nach dem Test gebundenen Quellhashes sind identisch; Gate `False`.

Der Befund qualifiziert ausschliesslich Quellen- und Metadatenbindung.
Er bestaetigt weder NT-Rezeptorgueltigkeit noch Trennleistung. Die nach diesem
Bestehen separat einmal ausgefuehrte Vorversiegelung besitzt ihren eigenen
Befund und ihre eigene Lauf-ID.
