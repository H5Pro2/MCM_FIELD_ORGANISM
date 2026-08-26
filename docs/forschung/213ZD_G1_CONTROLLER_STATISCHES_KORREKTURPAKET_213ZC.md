# 213ZD - G1 Controller statisches Korrekturpaket zu 213ZC

## Einordnung

`213ZD` ist ein statisches Korrekturpaket, kein Forschungslauf, kein Test und
keine Ausfuehrungsfreigabe. Eine Laufnummer wird nicht vergeben.

## Forschungsfrage und Auftrag

Auftrag war, ausschliesslich die sechs Befunde aus `213ZC` im bestehenden
Einprozess-Controller zu schliessen:

1. Erfolg und Fehler gegenseitig ausschliessen;
2. unerwartete Dateien und `__pycache__` kontrollieren;
3. Zaehler ueber einen geschlossenen AST-Auswerter messen;
4. Fehlerkontextfelder vollstaendig vergleichen;
5. fruehen PE-Alignmentabbruch binden;
6. Realpfade auch gegen lexikalische Unterpfade sperren.

## Tatsaechlich verwendete Quellen

- aktueller freigegebener Uebergabe-Eingang;
- `docs/forschung/213X_G1_WERKZEUGVALIDIERUNG_VORREGISTRIERUNG.md`;
- `docs/forschung/213Z_G1_REALPFAD_AUSSCHLUSSMENGE.json`;
- `docs/forschung/213Z_G1_WERKZEUGVALIDIERUNG_VERTRAGSKORREKTUR.md`;
- `docs/forschung/213ZA_G1_UNABHAENGIGE_STATISCHE_ABNAHME_213Z.md`;
- `docs/forschung/213ZB_G1_EINPROZESS_CONTROLLER_IMPLEMENTIERUNG.md`;
- `docs/forschung/213ZC_G1_UNABHAENGIGE_STATISCHE_ABNAHME_213ZB.md`;
- `tests/validate_static_binary_evidence.py`;
- `tools/static_binary_evidence.py`, ausschliesslich statisch gelesen.

Keine externe Quelle wurde verwendet.

## Verwendete Dateien und Schnittstellen

Geaendert wurde ausschliesslich:

- `tests/validate_static_binary_evidence.py`.

Neue Bytebindung des Controllers:

- Groesse: 33.100 Bytes;
- SHA-256:
  `18446459E4F3445BDEF7B613DCB604215113BB7DF3A29D89D0B5697360EBC663`.

Verwendet wurden nur statisches Textlesen, Textsuche und `apply_patch`.
Controller und Werkzeug wurden nicht importiert, geparst oder ausgefuehrt.

## Durchgefuehrte Korrekturen

### 1. Gegenseitiger Ausschluss der Publikationen

Die Temporaerbereinigung liegt jetzt vor Aufbau und Publikation des
Erfolgspakets. Nach `publish_directory` folgt nur noch die nicht
fehlerwerfende Zustandszuweisung `success_published = True` und `return 0`.
Der Fehlerhandler darf `publish_error` ausschliesslich ausfuehren, solange
`success_published` falsch ist.

### 2. Dateiseiteneffekte und Bytecode

Vor Phase B werden die bekannten `__pycache__`-Bereiche von Runner und
Werkzeug inventarisiert. Ein Audit-Waechter erlaubt Schreibereignisse nur
unter Fixture-Temporaerordner, Erfolg-Staging oder Fehler-Staging. Fuer die
einmalige Zielmodulausfuehrung wird `sys.dont_write_bytecode` gesetzt und
anschliessend wiederhergestellt. Eine veraenderte Cache-Inventur stoppt mit
`UNEXPECTED_FILE_CREATED`.

### 3. Geschlossener AST-Zaehlerauswerter

Die vier Faelle erzeugen nun `table_result` und `export_results` in der
vorregistrierten Form. `evaluate_count_expression` akzeptiert nur:

- gebundene Namen;
- feste String- und Integerkonstanten;
- Dictionary-/Listenindexe;
- exakt den Slice `1:4`;
- `len` mit einem Argument;
- `sum` ueber genau einen synchronen Generator ohne Filter.

Jede andere AST-Form stoppt mit `AST_ORACLE_MISMATCH`. Die sechs beobachteten
Werte stammen damit aus den konkreten Werkzeugausdruecken und nicht aus einer
parallelen testseitigen Formel.

### 4. Vollstaendige Fehlerkontextorakel

Fuer jeden der sieben Faelle werden die erwarteten Werte von
`control_binding_expected`, `control_binding_verified`, `tool_binding`,
`contract_binding` und der geordneten `input_bindings` vollstaendig erzeugt.
Das Ergebnis-JSON muss diesem gesamten Bindungsbild einschliesslich aller
`null`-Zustaende exakt entsprechen.

### 5. Frueher PE-Alignmentabbruch

Das Negativorakel bindet die Laufzeitbeobachtung des exakten Fehlercodes an
eine AST-Strukturpruefung von `PEImage._parse_headers`. Der Alignment-
Fehlerblock muss lexikalisch vor der Data-Directory-Schleife und diese vor der
Section-Auswertung liegen. Nur Fehlercode und bestaetigte fruehe Position
gemeinsam koennen einen negativen PE-Fall bestehen lassen.

### 6. Lexikalische Unterpfadsperre

Geschuetzte Runner-, Fixture-, Staging- und Ergebniswege werden rein
lexikalisch absolut und fallgefaltet verglichen. Neben exakter Gleichheit
wird mit separatorgebundenem Praefix geprueft, ob ein geschuetzter Pfad unter
einem ausgeschlossenen Realpfad liegt. Die 54 ausgeschlossenen Pfade werden
dabei nicht aufgeloest, auf Existenz geprueft, geoeffnet oder gehasht.

## Messergebnisse und Gegenbaselines

Statisch beobachtet:

- korrigierte Befundbereiche: `6/6`;
- Controllerprozesse im Vertrag: `1`;
- direkte `runpy.run_path`-Stellen: `1`;
- Fallzahl unveraendert: `21`;
- Fallverteilung unveraendert: `4 + 9 + 7 + 1`;
- Erfolgspaketdateien: `3`;
- Fehlerpaketdateien: `1`;
- ausgefuehrte Syntaxpruefungen: `0`;
- ausgefuehrte Tests oder Controllerlaeufe: `0`;
- Zugriffe auf die 54 Realpfade: `0`.

Gegenbaselines sind die sechs konkreten Fehlformen aus `213ZC`: doppeltes
Publizieren nach Erfolg, unbelegtes Bytecodeflag, parallele Zaehlerformel,
unvollstaendiger Kontextvergleich, blosser PE-Fehlercode und reiner
Gleichheitsvergleich. Diese Formen wurden jeweils eng korrigiert.

## Grenzen und nicht gepruefte Annahmen

- Die Syntax des korrigierten Controllers ist noch ungeprueft.
- Audit-Waechter, AST-Auswerter, Cache-Inventur und Orakel wurden nicht
  ausgefuehrt.
- Die 21 Faelle und ihre synthetischen Dateien wurden nicht erzeugt.
- Praktische Atomaritaet und Fehlerinduktion sind nicht belegt.
- Keiner der 54 Realpfade wurde beruehrt.
- Ein statisch geschlossenes Korrekturpaket ist kein G1-Nachweis und keine
  Aussage ueber eine MCM-Funktion.

## Konkrete Schlussfolgerung

Die sechs Befunde aus `213ZC` sind im Controller statisch adressiert. Daraus
folgt noch keine Ausfuehrungsreife, weil die korrigierte Datei zuerst erneut
unabhaengig statisch abgenommen werden muss.

G1 bleibt nicht bestanden, G0 bleibt abhaengig und Huerde G bleibt gesperrt.
Eine Zielabweichung ist nicht erkennbar.

## Vorschlag fuer den naechsten begrenzten Entwicklungsschritt

Als naechstes ist genau eine unabhaengige statische Abnahme des neu gebundenen
Controllers gegen die sechs Befunde aus `213ZC` sowie `213X`, `213Z` und
`213ZA` erforderlich.

Bis dahin bleiben Syntaxpruefung, Tests, Controller- und Werkzeugausfuehrung,
Zugriff auf die 54 Realpfade, Manifest, Resolver, G2 und Huerde G gesperrt.
