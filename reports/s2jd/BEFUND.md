# S2-JD Befund

S2-JD integriert die qualifizierte Rezeptor-Aggregatgleichheit prospektiv in
den privaten Zwei-Bereich-Kontextsignalgeber und seine unabhaengige
Direktbaseline.

Die Integration veraendert weder `A_RECENT` noch `B_STABLE`. Aggregatecodes
bleiben eine temporaere, read-only Herkunfts- und Gleichheitsevidenz. Der neue
Einstieg besitzt keinen Float-Rundungspfad, keinen Rueckfall auf exakte
Floatgleichheit und keine neue Schwelle. Eine vorhandene B-Evidenz wird nur
angenommen, wenn ihre vollstaendige PPB-Formationskette denselben homogenen
Aggregatecodebestand belegt.

Die fokussierte Qualifikation bestaetigt:

- `c01`: derselbe prospektiv gebundene Rezeptorzustand bleibt trotz
  PPB-Floatdrift `CONSISTENT`;
- `c05`: der stabile B-Kontext bleibt `SINGLE_SOURCE`;
- `c07` und `c08`: reale Ein-Stufen-Abweichungen bleiben
  `NO_APPLICABLE_CONTEXT`;
- direkt benachbarte Aggregatsummen bleiben verschieden;
- fehlende oder gemischte B-Herkunft stoppt fail-closed;
- Signalgeber und Direktbaseline stimmen ueberein;
- Eingaben und Memory-/Bundlezustaende bleiben unveraendert.

Qualifikationshistorie:

- `s2jd-aggregate-context-integration-20260901-01`: fehlgeschlagen; die
  maskierten Ergaenzungssaetze wurden noch mit exakter Floatgleichheit
  verglichen.
- `s2jd-aggregate-context-integration-20260901-02`: fehlgeschlagen; statischer
  Einfuegefehler machte den Area-Rueckgabeblock unerreichbar.
- `s2jd-aggregate-context-integration-20260901-03`: `8/8`, Exit-Code `0`,
  terminal `OK`, Quellhashes vor und nach dem Lauf identisch.

Status:

`S2JD_PRIVATE_AGGREGATE_CONTEXT_SIGNAL_INTEGRATION_QUALIFIED`

S2-IV bleibt unveraendert fachlich falsifiziert. Es wurde kein Hauptlauf,
keine automatische Kontextwahl, keine neue Memory-Ebene und keine
Feldintegration ausgefuehrt oder eingefuehrt.
