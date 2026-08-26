# 213ZA - G1: Unabhaengige statische Abnahme von 213Z

## Einordnung

`213ZA` ist eine statische Abnahme und kein Forschungslauf. Es wurde keine
Laufnummer vergeben. Gegenstand ist ausschliesslich die in `213Y` geforderte
Pruefung der Vertragskorrektur `213Z`.

## Forschungsfrage und Auftrag

Schliesst `213Z` die vier abnahmehemmenden Vertragsbefunde aus `213Y`
statisch und widerspruchsfrei?

Geprueft wurden ausschliesslich:

1. die gebundene Ausschlussmenge der 54 realen Zielpfade;
2. das AST-Routingorakel fuer den fruehen `_parse_binding`-Fehler in `main()`;
3. die Einprozess-Atomaritaet des spaeteren Validierungscontrollers;
4. die normative Grenze zwischen `ast.parse`, `runpy.run_path`, erlaubten
   Standardbibliothekimporten und verbotenen Importen.

## Verwendete Quellen

Tatsaechlich verwendet wurden:

- der aktuelle Uebergabe-Eingang mit der Freigabe fuer genau diese statische
  Abnahme;
- `docs/forschung/213Y_G1_UNABHAENGIGE_STATISCHE_PRUEFUNG_213X.md`;
- `docs/forschung/213X_G1_WERKZEUGVALIDIERUNG_VORREGISTRIERUNG.md`;
- `docs/forschung/213Z_G1_REALPFAD_AUSSCHLUSSMENGE.json`;
- `docs/forschung/213Z_G1_WERKZEUGVALIDIERUNG_VERTRAGSKORREKTUR.md`;
- `tools/static_binary_evidence.py`, ausschliesslich als Textdatei zur
  statischen Bestimmung seiner Importanweisungen.

Externe Projekt- oder Internetquellen waren fuer diese Vertragsabnahme nicht
erforderlich und wurden nicht verwendet.

## Verwendete Dateien und Schnittstellen

Verwendet wurden nur lesende Dateisystemzugriffe, Textsuche, kryptographische
Dateibindung und strukturelles JSON-Lesen. Es wurde keine Python-Schnittstelle
des Werkzeugs aufgerufen.

Bestand vor der Abnahme:

| Datei | Bytes | SHA-256 |
|---|---:|---|
| `213Y_G1_UNABHAENGIGE_STATISCHE_PRUEFUNG_213X.md` | 10.179 | `8D4FFADFFA161F607E6E86E4F5CD519F0711094478594FA2C3BA0AF372CA789F` |
| `213X_G1_WERKZEUGVALIDIERUNG_VORREGISTRIERUNG.md` | 13.427 | `48DEB78544B8E1817E33BF01FD484EA7FBA750628CA200FE7BC9BB0147E81D63` |
| `213Z_G1_REALPFAD_AUSSCHLUSSMENGE.json` | 6.253 | `52DA5D8DD26314BF173367E7F02D1F1B1055077380E83159A0FAE3EB87304ACF` |
| `213Z_G1_WERKZEUGVALIDIERUNG_VERTRAGSKORREKTUR.md` | 12.309 | `6E6A3500295472AD8AD45DDE5A57CCE42C07307EE64D4B1734DACF9D1646E75D` |
| `tools/static_binary_evidence.py` | 42.225 | `03162A337473218ADBCAAE577DB1922A3127DD3BCE1AE3B151B0291BDAB4E286` |

## Durchgefuehrte Schritte

1. Die Bindungen der beiden `213Z`-Artefakte wurden gegen Dateigroesse und
   SHA-256 kontrolliert.
2. Das JSON-Artefakt wurde strukturell gelesen. Schema, Rollen, Pfadanzahl,
   exakte Eindeutigkeit, gross-/kleinschreibungsunabhaengige Eindeutigkeit und
   lexikalische Pfadform wurden geprueft.
3. Das AST-Orakel `R-CLI-EARLY-ERROR` wurde gegen den in `213Y` benannten
   fehlenden fruehen Routingzweig und gegen die korrigierte Gesamtfallzahl
   geprueft.
4. Der Publikationsvertrag wurde auf Prozesszahl, Phasenfolge, Staging,
   Synchronisierung, einzelnen Rename und getrennte Fehlerpublikation geprueft.
5. Die Importregeln wurden mit den statisch sichtbaren Importanweisungen von
   `tools/static_binary_evidence.py` verglichen.
6. Ausschlussregeln und Stopplinien wurden auf Widersprueche kontrolliert.

## Messergebnisse und Gegenbaselines

### 1. Ausschlussmenge der Realpfade

Beobachtet:

- Schema: `mcm-g1-validation-realpath-exclusion-v1`;
- Eintraege gesamt: `54`;
- Rolle `cpython-binary`: `1`;
- Rolle `native-candidate`: `53`;
- exakt eindeutige Pfade: `54`;
- casefold-eindeutige Pfade: `54`;
- ungueltige lexikalische Pfadformen: `0`;
- alle Eintraege verwenden eine absolute Windows-Laufwerksform mit `/`;
- das Ausschlussartefakt ist im Vertrag mit Pfad, `6.253` Bytes und SHA-256
  gebunden.

Gegenbaseline aus `213Y`: Zuvor war die Ausschlussliste nur narrativ und nicht
als festes Artefakt gebunden. `213Z` stellt nun eine maschinenlesbare,
bytegebundene Menge mit fester Kardinalitaet bereit.

Die spaetere Kontrolle dieser Menge ist ausdruecklich lexikalisch. Fuer die 54
Realpfade sind `stat`, `open`, Hashbildung und `resolve` untersagt. Damit
erzeugt die Kontrollregel keinen verdeckten Zugriff auf das reale G1-Korpus.

### 2. AST-Routingorakel

Beobachtet: `R-CLI-EARLY-ERROR` fordert gemeinsam, dass

- `error_context` vor dem relevanten `try` erzeugt wird;
- `_parse_binding` fuer die unabhaengige Steuerbindung im `try` liegt;
- ein passendes `except EvidenceError as exc` existiert;
- darin `_write_error_only(args.output_dir, exc, context=error_context)` vor
  `return 2` erreicht wird;
- `expected_control` erst nach erfolgreichem Parsen gesetzt wird.

Die normative Fallrechnung lautet `4 + 9 + 7 + 1 = 21`; akzeptiert wird nur
`21/21`.

Gegenbaseline aus `213Y`: Der fruehe `_parse_binding`-Fehlerzweig war nicht
durch einen eigenen Routingfall abgedeckt. `213Z` schliesst genau diese Luecke
und passt Fallzahl sowie Akzeptanzsumme konsistent an.

### 3. Einprozess-Atomaritaet

Beobachtet:

- Der fruehere Vertrag mit zwei Interpreterstarts wird ausdruecklich ersetzt.
- Genau ein Controller in genau einem CPython-Prozess fuehrt Bindungspruefung,
  Ausschlusspruefung, AST-Pruefung, synthetische Fixtures und Publikation
  sequentiell aus.
- Das Erfolgspaket besteht aus genau drei Dateien im Staging-Baum.
- Nach Schreiben und Synchronisieren erfolgt genau ein Rename des gesamten
  Erfolgspakets auf ein zuvor nicht existentes Ziel.
- Bei Fehler wird das Erfolgs-Staging verworfen; ein getrenntes Paket mit genau
  einer Fehlerdatei wird ebenfalls atomar publiziert.
- Ein zweiter Prozess, `subprocess`, ein Fallback-Ziel und Teilpublikationen
  sind normativ ausgeschlossen.

Gegenbaseline aus `213Y`: Die vorherige Zweiprozessform konnte keine gemeinsame
Atomaritaet aller Phasen garantieren. Der einzelne Controller beseitigt diesen
Vertragswiderspruch statisch.

### 4. Importmengengrenze

Beobachtet:

- In Phase A wird nur Quelltext gelesen und mit `ast.parse` in einen AST
  ueberfuehrt; das Zielmodul wird weder importiert noch ausgefuehrt und es darf
  kein Bytecode entstehen.
- In Phase B erfolgt genau eine Ausfuehrung ueber `runpy.run_path` unter einem
  Namen ungleich `__main__`. Dabei wird das Zielmodul ausgefuehrt und seine
  erlaubte Standardbibliothek darf importiert werden; dies wird nicht
  faelschlich als "kein Import" bezeichnet.
- Die statisch sichtbare Importmenge von `tools/static_binary_evidence.py`
  entspricht der normativen Positivliste: `__future__.annotations`,
  `argparse`, `hashlib`, `json`, `os`, `struct`, `sys`, `dataclasses`,
  `datetime`, `pathlib` und `typing`.
- Projektimporte, Drittanbieterimporte, `importlib`, `ctypes`, NumPy,
  Loaderimporte, direkter Produktionsimport sowie `exec`, `eval` und
  `compile` bleiben ausgeschlossen.
- `main`, `collect` und `_verify_binding` duerfen nicht aufgerufen werden;
  `sys.path` und `sys.meta_path` duerfen nicht veraendert werden.

Gegenbaseline aus `213Y`: Die Begriffe Ausfuehrung, Import und "kein Import"
waren zuvor nicht hinreichend getrennt. `213Z` definiert fuer beide Phasen nun
eindeutige, pruefbare Grenzen.

## Grenzen und nicht gepruefte Annahmen

- Dies ist ausschliesslich eine statische Vertragsabnahme. Die spaetere
  Implementierung und die Erreichbarkeit der Orakel wurden nicht ausgefuehrt.
- Es erfolgten keine Syntaxpruefung, Kompilierung, Tests und kein Werkzeuglauf.
- Weder Steuerdatei noch eines der 54 realen Zielbinaries wurden erzeugt,
  geoeffnet, aufgeloest, gehasht oder anderweitig inspiziert.
- Die Herkunft der 54 Pfade aus dem frueher gebundenen Bestand wird innerhalb
  dieser Abnahme nicht durch Dateisystemzugriff nachgeprueft; das ist eine
  ausdrueckliche Schutzgrenze des Vertrags.
- Die Atomaritaet ist normativ vollstaendig beschrieben, aber noch nicht durch
  eine Implementierung oder einen Fehlerinduktionslauf belegt.
- Aus dieser technischen Abnahme folgt keine Aussage ueber MCM-Memory,
  Feldorganisation, Topologie, Semantik, Selbstregulation oder KI.

## Konkrete Schlussfolgerung

Die vier Befunde aus `213Y` sind in `213Z` statisch geschlossen. Es wurden
keine neuen abnahmehemmenden Widersprueche in den vier freigegebenen
Pruefbereichen festgestellt.

`213Z` ist damit als korrigierter statischer Validierungsvertrag abnahmefaehig.
Dies bedeutet noch nicht, dass G1 bestanden ist oder dass der Vertrag
ausfuehrbar validiert wurde. G1 bleibt nicht bestanden, G0 bleibt davon
abhaengig und Huerde G bleibt gesperrt.

Eine Zielabweichung ist nicht erkennbar.

## Vorschlag fuer den naechsten begrenzten Entwicklungsschritt

Als naechster Schritt sollte genau eine statische Implementierung des in
`213X` und `213Z` festgelegten Einprozess-Controllers erstellt werden. Dieser
Schritt darf nur Runnercode und eine bytegenaue Implementierungsdokumentation
erzeugen. Noch nicht enthalten sein duerfen Syntaxpruefung, Kompilierung,
Tests, Runner- oder Werkzeugausfuehrung, Steuerdateierzeugung, Zugriff auf die
54 Realpfade, Manifest- oder Resolverarbeit, G2 oder eine Oeffnung von Huerde G.

Nach dieser Implementierung ist vor jeder Ausfuehrung genau eine unabhaengige
statische Abnahme des Runnercodes gegen den hier abgenommenen Vertrag
erforderlich.
