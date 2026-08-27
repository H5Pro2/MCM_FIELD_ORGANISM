# S2-EG: Statischer Implementierungs- und Testaudit

## Entscheidung

**Nicht bestanden.**
`STATIC_IMPLEMENTATION_AUDIT_BLOCKED_MATRIX_LOCKED`.

Gepruefter Commit: `1ca652531f3aff61007997d575b8561bd9c50eaa`.
Geprueft wurde ausschliesslich die private S2-EF-Umsetzung gegen S2-EE und
die zugehoerigen statischen Belege. Es bestehen zwei konkrete
Implementierungsblocker sowie eine gesonderte Testkompatibilitaetsluecke.
Es wurden keine Korrekturen vorgenommen.

## EG-B01: Gueltige Generator-Aufrufstellen werden verworfen

Prioritaet: hoch. Betroffen: Operationszaehlung und Quellbindung.

Quellen:
- `_tspm1_s2dr_private_comparison.py:308`: Aufzeichnung von
  `caller.f_code.co_name` und `caller.f_lineno`.
- `_ppb1_s1wu_read_only_perceptual_probe.py:209`: Der L1-Aufruf steht in
  einem Generatorausdruck zur Bildung der Kandidatenliste.
- `_tspm1_s2dr_private_comparison.py:2073`: Der Validator akzeptiert nur
  `FunctionDef`/`AsyncFunctionDef` mit demselben Namen.

Der kompilierte, aber nicht ausgefuehrte S1-WU-Quelltext weist fuer diese
Aufrufstelle den Codeobjektnamen `<genexpr>` aus. Es gibt keinen entsprechenden
AST-Funktionsknoten. Sobald ein stabiler PPB-Prototyp fuer eine Probe zulaessig
ist, zeichnet der Zaehler daher einen Beleg auf, den sein eigener Validator
mit `S2DR_RESULT_RELATION_MISMATCH` verwerfen muss.

Dies betrifft beispielsweise die registrierte H2-Probe nach vier AX-Eingaben:
Die unveraenderte PPB-Stabilisierung ist dann erreichbar. Es handelt sich um
eine statisch hergeleitete Erreichbarkeit, nicht um ein ausgefuehrtes Zellresultat.
Die Luecke darf weder als fehlende Wiedererkennung noch als Budgetueberschreitung
gewertet werden. Erforderlich ist eine eindeutige Quellzuordnung auch fuer
gebundene Generator-Codeobjekte, ohne unbekannte Aufrufstellen pauschal zuzulassen.

## EG-B02: Lesbare Datei ersetzt im Fehlerpfad die Dauerhaftigkeitsbestaetigung

Prioritaet: hoch. Betroffen: atomarer und dauerhafter Abschluss.

Quellen:
- `_tspm1_s2dr_private_comparison.py:2831`: `publish` fuehrt die Umbenennung
  und anschliessend `flush` aus.
- `_tspm1_s2dr_private_comparison.py:2996`: Aufruf der Veroeffentlichung.
- `_tspm1_s2dr_private_comparison.py:3000`: Allgemeiner Ausnahmezweig.
- `_tspm1_s2dr_private_comparison.py:3021`: `_verify_artifact` prueft Inhalt
  und Digests, aber keinen erfolgreich abgeschlossenen Dauerhaftigkeitsschritt.

Statischer Fehlerpfad: Die atomare Umbenennung gelingt, der folgende
Volume-Flush meldet einen Fehler. Die finale Datei kann trotzdem lesbar sein.
Der Ausnahmezweig prueft dann nur ihre Bytes und setzt den Versuch bei
passendem Inhalt auf `COMPLETED`. Die Ausnahme wird zwar weitergereicht,
die interne Einordnung behauptet jedoch einen abgeschlossenen Versuch.

S2-EE fordert eine bestaetigte Plattform-Dauerhaftigkeit, nicht lediglich
eine lesbare Finaldatei. Das im JSON bereits enthaltene `status=COMPLETED`
wurde vor dem fehlgeschlagenen Schritt erstellt und belegt diesen nicht.
No-Replace und die verbrauchte Reservierung bleiben richtig; sie ersetzen
die fehlende Abschlussbestaetigung nicht.

Die spaetere Korrektur muss einen bestaetigten dauerhaften Abschluss von
einem nur sichtbaren beziehungsweise ungewissen Abschluss unterscheiden.
Ein bestaetigter Abschluss darf nicht widerspruechlich nachtraeglich scheitern;
ein ungewisser Abschluss darf weder als bestaetigt gelten noch einen Retry,
eine erneute Veroeffentlichung oder einen neuen Matrixversuch erlauben.
Dieser Fehlerpfad wurde ausschliesslich gelesen, nicht injiziert oder ausgefuehrt.

## EG-T01: Historische Tests sind nicht die Abnahme der neuen Schnittstelle

Die 51 Definitionen sind unveraendert; das entsprach der S2-EF-Grenze.
Sie koennen aber nicht unveraendert zur Freigabe der neuen Umsetzung dienen:

- T01 (`tests/test_tspm1_s2dr_private_comparison_contract.py:257`) erwartet
  genau drei Quellhashes; die neue Inventarisierung umfasst den transitiven Importbestand.
- T34 (`:371`) uebergibt die fuenf neuen Pflichtfelder von
  `S2DRComparisonResult` nicht: `evaluation_id`, `per_arm_metrics`,
  `all_arm_ranking`, `simple_baseline_ranking`,
  `ordered_cell_evidence_digests`. Der neu gebundene Evaluations-/Registryinhalt
  ist zusaetzlich fachlich anzupassen.
- T35-T39 und T51 verwenden `synthetic_comparison` (`:248`) ohne die nun
  zwingende Attestation. Sie erreichen die beabsichtigte Comparatorlogik nicht.
- T46 (`:450`) erwartet einen Duplikatfehler, wird aber ebenfalls vorher
  durch die fehlende Attestation abgewiesen.
- T37 behandelt einen technischen Armfehler noch als
  `TSPM1_FUNCTION_NOT_VALID`; S2-EE verlangt dafuer `METHOD_INVALID`.

Eine neue Testbindung muss die geaenderten Schnittstellen und Fehlerprioritaeten
sowie Generatorzaehlung und Veroeffentlichungsfehler abdecken. Sie darf zur
Herstellung gueltiger Testeingaben nicht stillschweigend die reale
56-Zellen-Matrix ausfuehren. Es wird hier weder ein Testbudget festgelegt noch
eine Testimplementierung oder Ausfuehrung freigegeben.

## Abgleich der fuenf Korrekturen

| Bereich | Statischer Befund |
| --- | --- |
| Neutrale Erfolgskriterien | Die 18 Sollproben und P1-P5 entsprechen S2-EE. Native ausgewaehlte Werte, getrennte Zielabweichung und numerische AX-Erhaltung ersetzen architekturspezifische Erfolgskriterien. |
| Operationszaehler | Funktionale und validierende L1-Arbeit werden addiert; Wortbreiten und alleiniger relationaler Ueberschreitungsort bleiben gebunden. EG-B01 blockiert die Abnahme. |
| Tie- und Entscheidungslogik | Methodik vor Funktion; danach einfache Baseline oder begrenzter Engineeringvorteil. Fehler, Latenz, Schreibaufwand und ASCII-Gleichstand sind gebunden. R0 bleibt zwingend. |
| Quellen, Owner, Receipts | Manifest, Registry, Autorisierung, Reservierung, Zellstart, Owner, Originalresultat und Wertkopien sind verknuepft. Zehn literale Record-Konstruktorstellen stimmen feldgenau mit S2-EE ueberein. Keine Gesamtfreigabe wegen der genannten Beleg- und Abschlussluecken. |
| Einmaligkeit und Veroeffentlichung | Exklusive feste Reservierung, serielle Starts, No-Replace und geschlossenes Freigabegate sind vorhanden. EG-B02 verhindert den vollstaendigen dauerhaften Abschlussnachweis. |

## Statischer Budgetabgleich

Es wird kein Messergebnis angegeben. Aus den festen H1-H7-Literalen und den
gelesenen Schleifen lassen sich konservative Arbeitsgrenzen ableiten:

| Arm | L1-Terme Bildung / Probe, hoechstens | Schreibwoerter Bildung, hoechstens |
| --- | --- | --- |
| TSPM1 | 208 / 208 | 160 |
| R0 | 130 / 104 | 160 |
| B0 | 0 / 0 | 0 |
| B1_DIRECT, B1_BUDGET_MATCHED | 136 / 136 | 36 |
| B2 | 234 / 234 | 291 |
| B3 | 0 / 26 | 29 |
| B4 | 0 / 234 | 29 |

Begruendung: TSPM1 vergleicht bis zu drei Fast-Slots je einmal funktional und
einmal in der relationalen Validierung. In diesen Literalen koennen nur AX
und das zweimalige P2 zur Konsolidierung gelangen; nur AX erreicht drei
Slow-Belege. Deshalb entstehen bis zu 52 weitere Bildungsterme beziehungsweise
zweimal 26 Slow-Probetterme. R0 hat einen Fast-Vergleichsdurchgang und einen
Slow-Probedurchgang. Andere Einzelpaare erhalten keine zweite gemeinsame
Fast-Bestaetigung. Die PPB-Ablaufgrenzen 64/256 werden in keiner endlichen
Geschichte erreicht. B2 und B4 besitzen neun AV-Plaetze, die direkten PPB-Arme
acht auditive und vier visuelle Plaetze. Die Schreibgrenzen summieren die
festen Aktionsbreiten konservativ, einschliesslich moeglicher Fast-/B2-Resets.

Alle so abgeleiteten Grenzen liegen innerhalb der unveraenderten 234
Distanzterme und 293 Schreibwoerter. Das ist kein Beleg fuer einen fehlerfreien
Zaehler und keine Erlaubnis, EG-B01 zu umgehen. Probe-Schreibbudget bleibt null;
der getrennte gemeinsame Evaluator verwendet hoechstens 26 Zielterme pro Probe.

## Syntax-, Symbol- und Hashbelege

AST, Compile-only und globale Symbolauflosung sind nachvollziehbar.
Kein kompiliertes Projektcodeobjekt wurde ausgewertet. Die kanonischen
S2-EE-, S2-ED-Wiederholungs- und S2-EF-Digests stimmen. Der Implementierungsblob
`379bf9c160cc59ce33f9d39a369098a5b3417961` und der dokumentierte Rohbytehash
stimmen. Alle sechs in S2-EF gebundenen geschuetzten Dateihashes stimmen ebenfalls.
Die Literale ergeben weiterhin sieben Geschichten, acht Arme, 42 Bildungseingaben
und 18 Proben je Arm. Das auf `False` gesetzte Freigabegate bleibt geschlossen.

Diese Belege sichern Quellstand und Syntax; sie beweisen keine Laufzeitkorrektheit.
Die Dateisystemfaehigkeit und die benoetigten Volume-Flush-Rechte wurden nicht
ausprobiert. Ein unabhaengiger Absturz- oder Laufzeitbeleg liegt nicht vor.

## Grenze und naechster Schritt

Angelegt werden ausschliesslich die zwei S2-EG-Auditdokumente. Null Code- oder
Testaenderungen, Projektimporte, Registry-, Zustands-, Probe-, Comparator-,
Dateisystem-Versuchs- und Matrixaufrufe. Keine Test-Collection oder Testausfuehrung.
API, Snapshot und Feldpfad bleiben unveraendert. Die strukturelle
Wahrnehmungsrepraesentation bleibt unentschieden.

Naechster sinnvoller Schritt ist **S2-EH als enger statischer Korrekturvertrag**
fuer EG-B01 und EG-B02 einschliesslich der notwendigen Testkompatibilitaetsbindung
EG-T01. Erst danach sind gesondert freizugebende Korrekturen und ein erneuter
S2-EG-Audit sinnvoll. Die 56-Zellen-Matrix bleibt gesperrt.
