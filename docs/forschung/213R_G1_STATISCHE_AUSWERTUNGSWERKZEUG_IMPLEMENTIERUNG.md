# 213R - G1 statische Auswertungswerkzeug-Implementierung

## Einordnung

213R ist ein statisches Implementierungs- und Bindungspaket, kein
Forschungslauf und kein Werkzeuglauf. Es setzt den in 213Q freigegebenen
Rohbyte-Parservertrag in genau einer neuen Werkzeugdatei um. Das Werkzeug wurde
nicht ausgefuehrt, importiert, kompiliert oder getestet. Es wurden keine
Nachweis-JSONs oder Manifeste erzeugt.

## Forschungsfrage und Auftrag

Kann der Vertrag aus 213Q als eng begrenztes fail-closed Werkzeug implementiert
werden, das ausschließlich gebundene Rohbytes liest, PE-Exporte und
CPython-Datentabellen dekodiert und atomare Nachweis-JSONs vorbereitet, ohne
Zielbinaries zu laden oder G1 vorzeitig als bestanden zu behandeln?

## Tatsaechlich verwendete Quellen

- aktueller freigegebener Uebergabe-Eingang;
- `docs/forschung/213Q_G1_STATISCHE_AUSWERTUNGSWERKZEUG_VORREGISTRIERUNG.md`;
- `docs/forschung/213P_G1_STATISCHE_MANIFEST_VORREGISTRIERUNG_UND_BINDUNG.md`;
- `C:/Python314/include/cpython/import.h`;
- `C:/Python314/include/internal/pycore_import.h`;
- bestehender lokaler Stil in `tools/static_g1_resolver.py`.

Keine Webquelle und keine externe MCM-Quelle wurde verwendet.

## Verwendete Dateien und Schnittstellen

Neu erstellt:

- `tools/static_binary_evidence.py`;
- dieses Dokument.

Die Implementierung verwendet im Quelltext nur Python-Standardbibliotheks-
Schnittstellen fuer Argumente, JSON, SHA-256, Rohbytes, `struct`, Pfade,
Zeitmetadaten und atomare Dateiausgabe. Sie enthaelt keine Projekt- oder
NumPy-Importanweisung und keine Schnittstelle zu `LoadLibrary`,
`GetProcAddress`, `ctypes`, `cffi`, Debugger- oder Prozessspeicher-APIs.

Im Rahmen dieses Auftrags wurde keine dieser Schnittstellen ausgefuehrt.

## Implementierter Umfang

### Eingangsbindung

- versioniertes Steuerformat `mcm-g1-static-binary-control-v1`;
- Pflichtbindungen fuer Werkzeug, Vertrag und Eingangsdateien;
- kanonischer Pfad, regulaere Datei, Bytegroesse und SHA-256;
- genau eine Rolle `cpython-binary` und genau 53 Rollen
  `native-candidate`;
- Stopp bei Doppelpfad oder Fallkollision.

Die spaetere Steuerdatei ist noch nicht erzeugt. Ihre Bytebindung ist ein
separater Schritt vor einem Werkzeuglauf.

### PE-Rohbyteparser

- DOS- und PE-Signatur;
- COFF AMD64 `0x8664`;
- PE32+ Magic `0x20B`;
- Optional Header, Data Directories und Section-Tabelle;
- Datei- und virtuelle Bereichsueberlappung;
- eindeutige RVA-zu-Dateioffset-Abbildung;
- Export- und Base-Relocation-Directory;
- grenzgepruefte Little-Endian-Dekodierung;
- ASCII-Namen bis maximal 1.024 Bytes.

### Native-Exportnachweis

- vollstaendige Named-Exportauswertung jeder Kandidatendatei;
- Ordinal- und Function-RVA-Zuordnung;
- Erkennung weitergeleiteter Exporte;
- exakt ein nicht weitergeleiteter `PyInit_*`-Export pro akzeptiertem
  Kandidaten;
- keine Ableitung vollqualifizierter Modulnamen aus dem Dateipfad.

### Builtin-/Frozen-Nachweis

- exakte exportierte Datensymbole;
- AMD64-DIR64-Relocation am Zeigerslot;
- Normalisierung bevorzugter virtueller Adresse gegen ImageBase;
- `_inittab` mit 16-Byte-Eintraegen;
- `_frozen` mit 24-Byte-Eintraegen und separatem Paketflag;
- `_module_alias` mit 16-Byte-Eintraegen;
- Nullterminatoren, Grenze von 4.096 Eintraegen und Aliaszykluspruefung;
- getrennte Bootstrap-, Stdlib-, Test- und Override-Tabellen.

### Ausgaben

Bei vollstaendiger Verarbeitung sind ausschließlich vorgesehen:

- `pe_export_evidence.json`;
- `cpython_table_evidence.json`;
- `static_binary_evaluation_report.json`.

Bei einem Fehler ist ausschließlich
`static_binary_evaluation_errors.json` vorgesehen. Ausgaben werden kanonisch
als UTF-8/ASCII-kompatibles JSON in einem Geschwister-Stagingordner vorbereitet.
Erst der vollstaendige Ordner wird abschliessend mit einer einzelnen
Verzeichnisumbenennung veroeffentlicht. Ein nichtleerer Ausgabeordner oder ein
vorhandener Stagingordner stoppt.

## Statische Vertragspruefung

Die Datei wurde ausschließlich als Text gegen 213Q gelesen. Beobachtet wurden:

- keine Importanweisung fuer Projektmodule oder NumPy;
- keine Binary-Lade-, Link-, Prozess- oder Debugger-API;
- keine Stringscan-Fallbacklogik fuer CPython-Tabellen;
- keine Dateinamenheuristik als Native-Namensbeweis;
- keine G2-Aufloesung;
- `manifest_generated` und `resolver_run` werden nur als `false`
  dokumentiert;
- Fehler fuehren zu `complete: false` und einem Stopcode;
- die fachlichen Evidenzdateien werden nur nach vollstaendiger Verarbeitung
  vorbereitet.

Diese statische Inspektion ist kein Syntax-, Import-, Kompilierungs- oder
Funktionstest.

## Messergebnisse und Gegenbaselines

Beobachtet:

- genau eine neue Werkzeugimplementierung wurde erstellt;
- der vorregistrierte Eingang bleibt auf eine CPython-Binary und 53
  Native-Kandidaten beschraenkt;
- es wurden `0` Zielbinaries ausgewertet;
- es wurden `0` Nachweisdateien und `0` Manifeste erzeugt;
- es wurde `0` Resolverlauf durchgefuehrt.

Gegenbaselines:

- keine Nutzung von `pefile`, Systemtools oder Laufzeitloadern;
- keine Ableitung aus Dateinamen oder Strings;
- keine Teilakzeptanz bei einzelnen Parserfehlern;
- keine automatische Weiterleitung der Evidenz in Resolvermanifeste.

## Grenzen und nicht gepruefte Annahmen

- Syntax und Laufzeitverhalten der Implementierung wurden nicht getestet.
- Die tatsächlichen PE-Strukturen der 54 Zielbinaries wurden nicht gelesen.
- Ob alle CPython-Datensymbole exportiert und ihre Zeiger per DIR64-Relocation
  statisch aufloesbar sind, bleibt offen.
- Der Vertrag verlangt exakt einen `PyInit_*`-Export je Kandidat; ob Test- oder
  Mehrphasenmodule davon abweichen, ist noch nicht beobachtet.
- Das Werkzeug erzeugt Nachweise, aber keine vollqualifizierte
  Importgraphzuordnung und keine Manifeste.
- G2, DLL-Abhaengigkeiten, `numpy.libs`, Sicherheitszustand und Huerde G wurden
  nicht bearbeitet.

## Stopplinien

- Keine Ausfuehrung oder technische Erprobung vor separater Freigabe.
- Keine Aenderung der Parserregeln aufgrund spaeterer Zielbytes ohne neue
  statische Pruefung.
- Keine Akzeptanz, wenn Eingangsbindung, PE-Struktur, Export, Relocation,
  Tabellenende, Paketflag oder Alias nicht eindeutig ist.
- Keine Manifesterzeugung oder Resolverausfuehrung aus diesem Paket.
- Kein Uebergang zu G2 oder Huerde G.

## Konkrete Schlussfolgerung

Der Vertrag aus 213Q ist als eigenstaendiger Rohbyte-Parser implementiert und
statisch dokumentiert. Die Implementierung behauptet noch weder technische
Funktionsfaehigkeit noch einen Binary-, Manifest- oder G1-Abschluss. G1 ist
weiterhin nicht bestanden, G0 bleibt abhaengig und Huerde G bleibt gesperrt.
Eine erkennbare Zielabweichung liegt nicht vor.

## Vorschlag fuer den naechsten begrenzten Forschungs- und Entwicklungsschritt

Als naechstes sollte die Implementierung ausschließlich statisch gegen 213Q
und ihre eigene Bytebindung geprueft werden. Dabei sind insbesondere
RVA-Grenzen, Exportfeldindizes, Relocation-Normalisierung, Tabellenlayouts,
Atomaritaet und die Abwesenheit gesperrter APIs zu kontrollieren. Noch kein
Import, keine Kompilierung, kein Test, kein Werkzeuglauf gegen Zielbinaries,
keine Manifesterzeugung, kein Resolverlauf und keine G2-Bearbeitung.
