# S2-TY-Gesamtqualifikation: Vorstartfehler

Auftragskennung: `s2ty-neutral-overall-qualification-20260920-01`.

Der einmalig vorgesehene Qualifikationsstarter wurde aufgerufen, erreichte
aber keinen `unittest`-Aufruf und erzeugte keine Qualifikationsablage. Beim
Start von `reports/s2ty/qualify_s2ty_neutral_once.py` schlug der Import fehl:

```text
ModuleNotFoundError: No module named 'tools'
```

Ursache: Beim direkten Start liegt das Skriptverzeichnis, nicht die
Arbeitswurzel, auf `sys.path`. Damit ist der formale Testbestand nicht
gestartet und keine der 49 neutralen Prüfungen erneut ausgeführt worden.

Status: `NOT_QUALIFIED_PRESTART`. Die vorgesehene Ergebnisablage
`reports/s2ty/s2ty-neutral-overall-qualification-20260920-01/` ist weiterhin
nicht vorhanden. Es erfolgte kein Payloadzugriff, keine Rezeptor- oder
NJ-Ausführung und kein Hauptlauf.

Kleinste Korrekturrichtung: Den Starter vor seinen Projektimporten explizit
an die Arbeitswurzel binden, etwa durch Einfügen der aufgelösten Wurzel in
`sys.path`. Danach erfordert der formale Testaufruf eine neue ausdrückliche
Freigabe; dieser Vorstartfehler wird nicht als ausgeführte Qualifikation
ausgegeben.
