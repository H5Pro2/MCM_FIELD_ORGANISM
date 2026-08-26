# 213Z - G1 Werkzeugvalidierung Vertragskorrektur

## Einordnung und Vorrang

213Z ist ein statisches Vertragskorrekturpaket, kein Forschungslauf, keine
Runnerimplementierung und keine Lauffreigabe. Es korrigiert ausschliesslich die
vier in 213Y festgestellten Vertragsluecken von 213X.

Die unveraenderten Fixturedefinitionen und Orakel aus 213X bleiben bestehen.
Bei Widerspruch haben die in 213Z festgelegten Ausschlussbindungen,
Fallzahlen, Controllerregeln und Begriffsdefinitionen Vorrang.

Es erfolgten keine Syntaxpruefung, keine Python-Ausfuehrung und kein Test.

## Forschungsfrage und Auftrag

Kann der Validierungsvertrag aus 213X so statisch praezisiert werden, dass die
54 ausgeschlossenen Realpfade bytegebunden sind, der fruehe CLI-Fehlerzweig
ein festes Orakel besitzt, genau ein Controller die atomare Publikation
verantwortet und Syntaxanalyse, Modulausfuehrung sowie Importklassen eindeutig
getrennt sind?

## Tatsaechlich verwendete Quellen

- aktueller freigegebener Uebergabe-Eingang;
- `docs/forschung/213Y_G1_UNABHAENGIGE_STATISCHE_PRUEFUNG_213X.md`;
- `docs/forschung/213X_G1_WERKZEUGVALIDIERUNG_VORREGISTRIERUNG.md`;
- `docs/forschung/213P_G1_STATISCHE_MANIFEST_VORREGISTRIERUNG_UND_BINDUNG.md`;
- `tools/static_binary_evidence.py`.

Keine Webquelle und keine externe MCM-Quelle wurde verwendet.

## Verwendete und erzeugte Dateien

Neu erzeugt wurden ausschliesslich:

- `docs/forschung/213Z_G1_REALPFAD_AUSSCHLUSSMENGE.json`;
- `docs/forschung/213Z_G1_WERKZEUGVALIDIERUNG_VERTRAGSKORREKTUR.md`.

213X und `tools/static_binary_evidence.py` blieben unveraendert. Verwendet
wurden Textlesen, strukturierte JSON-Lesung, Textsuche, `apply_patch`,
Dateigroesse, SHA-256 und `git diff --check`. Kein aufgefuehrter Realpfad
wurde geoeffnet, auf Existenz geprueft oder neu gehasht.

## Korrektur 1 - bytegebundene Realpfad-Ausschlussmenge

Die einzige erlaubte Quelle der spaeteren Ausschlussmenge ist:

- Pfad: `docs/forschung/213Z_G1_REALPFAD_AUSSCHLUSSMENGE.json`;
- Schema: `mcm-g1-validation-realpath-exclusion-v1`;
- Groesse: 6.253 Bytes;
- SHA-256:
  `52DA5D8DD26314BF173367E7F02D1F1B1055077380E83159A0FAE3EB87304ACF`.

Das Artefakt bindet seine Herkunft an 213P und enthaelt exakt:

- 1 kanonischen Pfad mit Rolle `cpython-binary`;
- 53 kanonische Pfade mit Rolle `native-candidate`;
- insgesamt 54 eindeutige, auch fallgefaltet eindeutige Pfade;
- keine Dateigroessen oder Binary-Hashes, die ein spaeterer Runner gegen reale
  Dateien nachpruefen muesste.

Der spaetere Controller darf dieses eine JSON zusaetzlich lesen und seine
eigene Bytebindung pruefen. Er darf die darin genannten Pfade nur lexikalisch
kanonisieren und mit Fixture- und Ausgabewegen vergleichen. Verboten bleiben
Existenzabfrage, `stat`, Oeffnen, Lesen, Hashen, Aufloesen von Symlinks oder
anderer Dateisystemzugriff auf einen der 54 Pfade.

Pflichtpruefungen vor Phase A:

1. Artefaktpfad, Groesse und SHA-256 stimmen;
2. Schema stimmt;
3. `expected_counts` ist `1`, `53`, `54`;
4. die Eintragsliste enthaelt exakt dieselben Rollenanzahlen;
5. alle Pfade sind absolute Windows-Pfade mit `/` als Separator;
6. kein Pfad ist leer, doppelt oder fallkollidierend;
7. kein Fixture-, Staging-, Ergebnis- oder Runnerpfad ist lexikalisch gleich
   einem ausgeschlossenen Pfad oder liegt unter einem ausgeschlossenen
   Dateipfad.

Jede Abweichung fuehrt vor der Syntaxanalyse zu
`EXCLUSION_BINDING_MISMATCH`. Die Liste darf nicht ueber CLI-Einzelpfade,
Umgebung, Verzeichnisscan oder andere Projektdateien ergaenzt werden.

## Korrektur 2 - zusaetzlicher AST-Routingfall

Zu den 20 Faellen aus 213X kommt genau ein Fall hinzu:

### R-CLI-EARLY-ERROR

Der bereits fuer Phase A erzeugte AST der gebundenen Werkzeugdatei wird ohne
Zielmodulausfuehrung geprueft. Das feste Orakel verlangt in `main()`:

1. eine Zuweisung `error_context = ErrorContext(started_utc=started)` vor dem
   ersten Sollanker-`try`;
2. im ersten Sollanker-`try` einen Aufruf von `_parse_binding` fuer
   `independent_control_binding`;
3. einen unmittelbar zugeordneten `except EvidenceError as exc`;
4. in diesem Handler einen Aufruf
   `_write_error_only(args.output_dir, exc, context=error_context)` vor dem
   `return 2`;
5. keine Zuweisung an `error_context.expected_control` vor erfolgreicher
   Rueckkehr von `_parse_binding`.

Die Pruefung darf nur feste AST-Knotentypen, Funktions- und Keywordnamen sowie
lexikalische Blockreihenfolge vergleichen. Keine Quelltextregex, kein `eval`,
kein `exec` und kein Aufruf von `main()` sind erlaubt.

Erwartung: alle fuenf Bedingungen sind wahr. Andernfalls ist der Fall
fehlgeschlagen. Dieser Fall belegt nur den statischen Routingvertrag; E-NONE
aus 213X belegt weiterhin die Serialisierung eines leeren Kontextes.

Die feste Fixturezahl lautet damit:

- 4 Zaehlerfaelle;
- 9 Alignmentfaelle;
- 7 Fehlerkontextfaelle;
- 1 AST-Routingfall;
- insgesamt 21 Faelle.

Akzeptanzsumme: Gesamtzahl `21`, bestanden `21`, fehlgeschlagen `0`. Jede
Ausgabe oder Dokumentation mit `20/20` ist nach 213Z ungueltig.

## Korrektur 3 - ein atomarer Controller

Die in 213X genannten zwei getrennten Interpreterstarts werden aufgehoben.
Die spaetere Validierung besitzt genau einen noch nicht implementierten
Controller und genau einen gebundenen CPython-3.14.4-Prozess. Dieser Prozess
fuehrt streng sequenziell aus:

1. eigene Runner-, Werkzeug-, Vertrags-, Ausschluss- und Interpreterbindung
   pruefen;
2. einen neuen Stagingordner neben dem finalen Ergebnisziel anlegen;
3. Ausschlussartefakt strukturell pruefen;
4. Phase A mit `ast.parse` ausfuehren und das Ergebnis nur im Speicher halten;
5. bei erfolgreicher Phase A die 21 Fixturefaelle ausfuehren;
6. alle drei Erfolgsdokumente kanonisch in den Stagingordner schreiben und
   `fsync` ausfuehren;
7. pruefen, dass der finale Ergebnisordner nicht existiert;
8. den Stagingordner durch genau einen Rename als finalen Ergebnisordner
   publizieren.

Kein zweiter Prozess und kein Zwischenartefakt zwischen Phase A und B sind
erlaubt. Der Controller darf keinen Subprozess starten.

### Erfolgspaket

Das atomar publizierte Erfolgspaket enthaelt genau die drei in 213X
vorregistrierten Dateien:

- `syntax_validation.json`;
- `synthetic_fixture_validation.json`;
- `validation_report.json`.

### Fehlerpaket

Jeder Stopp vor vollstaendigem Erfolg verwirft den Erfolgs-Stagingordner. Der
Controller erzeugt danach einen neuen Fehler-Stagingordner und publiziert ihn
durch genau einen Rename unter einem getrennten, vorher nicht existierenden
Fehlerziel. Er enthaelt genau:

- `validation_error.json`.

Pflichtfelder sind Schema `mcm-g1-tool-validation-error-v1`, alle bis zum
Stopp verifizierten Meta-Bindungen, Phase, Fall-ID oder `null`, Fehlercode,
Detail, UTC-Start/Ende sowie die unveraenderten Flags
`project_control_opened=false`, `real_target_binary_opened=false`,
`manifest_generated=false`, `resolver_run=false`, `g2_touched=false`.

Ein Fehlerpaket ist niemals ein bestandenes Teilergebnis. Existiert Erfolgs-
oder Fehlerziel bereits oder schlaegt der Rename fehl, darf kein alternatives
Ziel verwendet werden.

## Korrektur 4 - normative Ausfuehrungs- und Importklassen

Die folgenden Begriffe gelten fuer 213X und 213Z verbindlich:

### Aktueller Vertragskorrekturschritt

213Z fuehrt kein Python aus. Es gibt weder Syntaxanalyse noch Testlauf,
Zielmodulausfuehrung oder Importaktivitaet durch einen Validierungsrunner.

### Phase A: Syntaxanalyse

Der spaetere Controller ist ein Python-Testprozess und darf seine eigene
Standardbibliothek laden. Er liest den gebundenen Werkzeugquelltext und ruft
`ast.parse` auf. Der Werkzeug-Modulrumpf wird in Phase A nicht ausgefuehrt.
`runpy`, Werkzeugklassen und Werkzeugfunktionen werden in dieser Phase nicht
aufgerufen. Es entsteht kein Bytecode.

### Phase B: isolierte Zielmodulausfuehrung

Nach erfolgreicher Phase A fuehrt derselbe Controller die Werkzeugdatei genau
einmal mit
`runpy.run_path(..., run_name="mcm_g1_static_binary_evidence_fixture_target")`
aus. Dies ist eine Zielmodulausfuehrung und ein Testlauf, aber kein Aufruf von
`main()` oder `collect()`.

Dabei duerfen ausschliesslich die im gebundenen Werkzeug statisch vorhandenen
Importe ausgefuehrt werden:

- `__future__`;
- `argparse`;
- `hashlib`;
- `json`;
- `os`;
- `struct`;
- `sys`;
- `dataclasses`;
- `datetime`;
- `pathlib`;
- `typing`.

Der Phase-A-AST muss vor `runpy` bestaetigen, dass die Werkzeugdatei keine
andere Importanweisung besitzt. Ein abweichender Import fuehrt zu
`TARGET_IMPORT_SET_MISMATCH` und verhindert Phase B.

### Verbotene Import- und Loaderklassen

Verboten sind im Runnerquelltext und als direkte Importanweisung des
Werkzeugquelltexts:

- Projektmodule;
- Drittanbieterpakete einschliesslich NumPy;
- `importlib`, `ctypes`, `cffi`, `pickle`;
- direkte Loader-, DLL- oder Extension-Modul-APIs;
- direkter Import der Werkzeugdatei unter ihrem Produktionsnamen;
- direkte Verwendung von `exec`, `eval` oder `compile`.

Die interne Standardbibliotheksimplementierung von `runpy` und des Python-
Importsystems ist kein zusaetzlicher freigegebener Runner- oder
Werkzeugimport. Sie darf nicht durch eigene `importlib`-Aufrufe, Loaderhooks,
`sys.path`-Erweiterung oder Meta-Path-Aenderung gesteuert werden. Vor und nach
Phase B muessen `sys.path` und `sys.meta_path` identisch sein.

`main()`, `collect()`, `_verify_binding` und reale Binarypfade bleiben
ungeachtet dieser Importfreigabe gesperrt.

## Aktualisierte Pflichtausgaben und Akzeptanzkriterien

Alle Pflichtfelder aus 213X bleiben erhalten. Zusaetzlich muss
`validation_report.json` enthalten:

- Bindung des Ausschlussartefakts;
- `excluded_path_count: 54`;
- `controller_process_count: 1`;
- `target_runpy_executions: 1`;
- `fixture_count: 21`;
- Gruppenwerte `4`, `9`, `7`, `1`;
- `success_publication_renames: 1`;
- `error_publication_renames: 0`.

Die Validierung ist nur bestanden, wenn alle urspruenglichen Kriterien aus
213X zusammen mit allen Korrekturen aus 213Z erfuellt sind. Die vier Befunde
aus 213Y dienen als Gegenbaseline. Eine frei gelieferte Ausschlussliste,
20/20 Faelle, zwei Controllerprozesse oder eine globale Behauptung `kein
Import` gelten als Vertragsverletzung.

## Durchgefuehrte Schritte und Messergebnisse

Aus 213P wurden ausschliesslich die dokumentierten Namen und Pfadwurzeln der
1 + 53 Zielbinaries uebernommen. Das neue JSON wurde strukturell gelesen; es
enthaelt beobachtet 1 CPython-Rolle, 53 Native-Rollen, insgesamt 54 Eintraege
und 54 eindeutige Pfade. Kein Zielpfad wurde aufgerufen.

Die drei anderen Korrekturen wurden als statische Vertragsregeln mit festen
Orakeln, Fallzahlen, Prozessgrenzen und Publikationspfaden dokumentiert. Es
liegen keine Syntax- oder Fixture-Messergebnisse vor.

## Grenzen und nicht gepruefte Annahmen

- Der Controller und der Runner existieren noch nicht.
- Die 21 Faelle wurden nicht ausgefuehrt.
- Die synthetischen PE-Fixtures wurden nicht erzeugt.
- Die praktische Atomaritaet und Importmengenkontrolle wurden nicht getestet.
- Die Realpfade stammen aus der gebundenen Dokumentation 213P; ihr aktueller
  Dateisystemzustand wurde absichtlich nicht geprueft.
- Ein spaeteres 21/21-Ergebnis waere Werkzeugvalidierung, kein G1-
  Resolvernachweis und kein MCM-Funktionsnachweis.

## Konkrete Schlussfolgerung

Die vier Vertragsluecken aus 213Y sind statisch adressiert: Die
Ausschlussmenge ist ein fest gebundenes Artefakt, der fruehe CLI-Fehlerzweig
besitzt einen 21. AST-Fall, ein einzelner Controller traegt die atomare
Publikationsverantwortung und die Ausfuehrungs-/Importklassen sind getrennt.
Aktuell ist daraus keine Validierungs- oder Lauffaehigkeit abgeleitet.

G1 bleibt nicht bestanden, G0 bleibt abhaengig, G2 und Huerde G bleiben
gesperrt. Eine erkennbare Zielabweichung liegt nicht vor.

## Vorschlag fuer den naechsten begrenzten Schritt

Als naechstes sollte genau eine unabhaengige statische Abnahme von 213Z gegen
die vier Befunde aus 213Y erfolgen. Zu pruefen sind insbesondere die 54
Artefakteintraege, das AST-Routingorakel, die Einprozess-Atomaritaet und die
Importmengengrenze.

Noch keine Runnerimplementierung, keine Syntaxpruefung, keine Kompilierung,
kein Test, kein Werkzeuglauf, keine Steuerdateierzeugung, kein Oeffnen realer
Zielbinaries, keine Manifesterzeugung, kein Resolverlauf, keine G2-Bearbeitung
und keine Oeffnung von Huerde G.
