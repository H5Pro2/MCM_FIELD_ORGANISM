# S2-JB Befund

Status:

`QUALIFICATION_FAILED_TEST_FIXTURE_ERROR`

Die private Aggregatcode- und PPB-Herkunftsimplementierung wurde nach einem
bestandenen statischen Codepreflight genau einmal qualifiziert.

Der einzige `unittest`-Aufruf fuehrte alle 50 registrierten Tests aus. 48
Testkoerper bestanden. `test_043` und `test_044` erreichten den vorgesehenen
Mixed-Lineage-Pfad nicht, weil die Testfixture einen bereits erzeugten
`ReceptorContactFrame` vor dem gemeinsamen Hilfsaufruf ein zweites Mal mit
`from_visual_receptor_state` umwandeln wollte. Der nachgelagerte
`tearDownClass`-Fehler ist eine Folge der dadurch nur 212 statt 214 erreichten
PPB-Formationen.

Der Fehler liegt in der Testvorbereitung. Er ist kein negativer Befund zur
Aggregatgleichheit, PPB-Herkunft oder Memory-Funktion. Die Implementierung
ist dennoch nicht qualifiziert, weil zwei der acht Fail-Closed-Faelle nicht
bis zur vorgesehenen Grenze gelangten.

Es gab keinen Retry und keine Korrektur nach dem Lauf. Modul- und Testhashes
blieben waehrend der Ausfuehrung unveraendert. S2-IV bleibt dauerhaft
falsifiziert.

Eine neue Qualifikation erfordert mindestens:

- ausschliesslich die doppelte Fixture-Umwandlung in `test_043` und
  `test_044` entfernen;
- den Produktcode und die uebrigen 48 Testkoerper unveraendert lassen;
- neue Qualifikations-ID;
- erneut genau einen vorab freigegebenen Testaufruf ohne Retry.
