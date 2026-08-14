# 213Q - G1 statische Auswertungswerkzeug-Vorregistrierung

## Einordnung

213Q ist ein statisches Vorregistrierungspaket, kein Forschungslauf, keine
Werkzeugimplementierung und kein Werkzeug- oder Resolverlauf. Es definiert den
Vertrag fuer ein spaeter separat freizugebendes read-only Werkzeug zur
Auswertung von PE-Exporten sowie CPython-Builtin-/Frozen-Tabellen. Es erzeugt
keine Manifeste und veraendert keine bestehende Quelle.

## Forschungsfrage und Auftrag

Welche festen Eingaben, Parserregeln, Ausgaben, Fehlermodi und Stopplinien muss
ein statisches Werkzeug einhalten, damit es

1. die `PyInit_*`-Exporte der in 213P gebundenen `.pyd`-Dateien belegen und
2. die konkreten Builtin-, Frozen- und Frozen-Alias-Eintraege der gebundenen
   CPython-3.14.4-Installation ohne Interpreterstart auswerten kann?

Das Ergebnis soll ausschliesslich Nachweisdaten fuer spaetere, separat
freizugebende Manifestdateien liefern.

## Tatsaechlich verwendete Quellen

- aktueller freigegebener Uebergabe-Eingang;
- `docs/forschung/213P_G1_STATISCHE_MANIFEST_VORREGISTRIERUNG_UND_BINDUNG.md`;
- `docs/forschung/213N_G1_STATISCHE_RESOLVER_VORREGISTRIERUNG.md`;
- `tools/static_g1_resolver.py`;
- `C:/Python314/include/cpython/import.h`;
- `C:/Python314/include/internal/pycore_import.h`.

Keine Webquelle und keine externe MCM-Quelle wurde verwendet.

## Verwendete Dateien und Schnittstellen

Die Quellen wurden nur als Text und Rohbytes gelesen. Es wurden keine Python-,
NumPy- oder Projektmodule importiert, keine PE-Datei geladen, keine Bibliothek
gelinkt, kein Zielprozess gestartet und kein vorhandenes Werkzeug ausgefuehrt.
Ausser diesem Dokument wurde keine Datei veraendert.

## Gebundene Eingangsgrundlage

Das spaetere Werkzeug darf nur diese in 213P bereits gebundenen Eingangsklassen
akzeptieren:

- exakt `C:/Python314/python314.dll`, 6.767.440 Bytes, SHA-256
  `A07F7D09C3121492BB066535C6D0811DF5FBC2090CBCA7031A97BB47CE1480C9`;
- exakt `C:/Python314/include/cpython/import.h`, 929 Bytes, SHA-256
  `65FC03C4074B2834A0FAA06A4347CCA1BB8B320D2DE48EEB75DE951575CD7782`;
- exakt `C:/Python314/include/internal/pycore_import.h`, 4.789 Bytes,
  SHA-256
  `A90DBB06D12E732F2A6138E4521E6B88A8BD6ABF9AD35EFBE1BA7EBD85BB0800`;
- die 34 einzeln in 213P gebundenen `.pyd`-Dateien unter
  `C:/Python314/DLLs`;
- die 19 einzeln in 213P gebundenen NumPy-`.pyd`-Dateien unter
  `.venv/Lib/site-packages/numpy`.

Damit besteht der Native-Eingang aus genau 53 Kandidatendateien und
11.639.184 Bytes. `python3.dll`, `python314.lib`, andere DLLs,
`numpy.libs`, Systemverzeichnisse und Netzwerkquellen sind keine stillen
Ersatzeingaenge.

Vor jeder Auswertung muss das Werkzeug Pfad, regulaeren Dateityp, Groesse und
SHA-256 aller gewaehlten Eingaben gegen eine separat gebundene Steuerdatei
pruefen. Schon eine Abweichung beendet den gesamten Vorgang vor dem Parsen.

## Werkzeuggrenze

Das spaetere Werkzeug ist ein Rohbyte-Parser. Es darf:

- Dateien read-only oeffnen und ihre Bytes lesen;
- SHA-256 und Bytegroessen berechnen;
- PE-/COFF-Header, Section-Tabellen, Data Directories, Exporttabellen und
  Base-Relocation-Informationen statisch dekodieren;
- RVA-Werte nur ueber die im selben PE belegten Section-Bereiche in
  Dateioffsets ueberfuehren;
- gebundene nullterminierte ASCII-Namen und fest definierte Integerfelder
  lesen;
- deterministische JSON-Nachweisdaten und einen menschenlesbaren Bericht in
  einen explizit angegebenen leeren Ausgabeordner schreiben.

Es darf nicht:

- Python oder eine `.pyd`/DLL laden, importieren, ausfuehren oder linken;
- `LoadLibrary`, `GetProcAddress`, `ctypes`, `cffi`, Debugger-, Dump- oder
  Prozessspeicher-APIs verwenden;
- Interpreterfunktionen wie `sys.builtin_module_names` oder `_imp` aufrufen;
- DLL-Abhaengigkeiten rekursiv verfolgen oder G2-Dateien erheben;
- Symbole aus dem Internet, einem Symbolserver oder einer anderen
  CPython-Version beziehen;
- fehlende Namen, Zeiger, Paketflags oder Aliase aus Konventionen ergaenzen;
- Teilmanifeste als bestanden markieren.

## Gemeinsamer PE-Parservertrag

Der Parser muss PE32+ fuer AMD64 explizit verlangen und mindestens folgende
Strukturen mit festen Little-Endian-Feldern validieren:

1. DOS-Header und `e_lfanew` innerhalb der Datei;
2. PE-Signatur, COFF-Header und AMD64-Maschine `0x8664`;
3. PE32+-Optional-Header mit Magic `0x20B`;
4. `SizeOfHeaders`, `SizeOfImage`, ImageBase, SectionAlignment und
   FileAlignment;
5. Anzahl und vollstaendige Grenzen aller Section-Header;
6. Export- und Base-Relocation-Data-Directory;
7. jede verwendete RVA-zu-Dateioffset-Abbildung gegen genau eine Section und
   deren `VirtualAddress`, `VirtualSize`, `SizeOfRawData` und
   `PointerToRawData`;
8. jede Arraylaenge, Multiplikation und Addition vor dem Lesen gegen
   Integerueberlauf und Dateigrenze.

Ueberlappende Sections, mehrdeutige RVA-Abbildungen, Bereiche nur im virtuellen
Nullfuellanteil, abgeschnittene Tabellen oder widerspruechliche Groessen sind
harte Fehler. Der Parser darf keine Windows-Laderreparatur simulieren und keine
ausserhalb der Datei liegenden Daten voraussetzen.

## Teil A: read-only PE-Exportauswertung der `.pyd`-Dateien

### Auswahl

Teil A verarbeitet jede der 53 gebundenen Kandidatendateien einzeln. Die
Verarbeitung aller Kandidaten dient nur der Exportbeweiserhebung. Eine Datei
wird dadurch noch nicht als G1-erreicht klassifiziert.

### Erforderliche Auswertung

Fuer jede Datei muss das Werkzeug die `IMAGE_EXPORT_DIRECTORY` sowie
`AddressOfFunctions`, `AddressOfNames` und `AddressOfNameOrdinals` vollstaendig
und grenzgeprueft lesen. Jeder Name wird als nullterminiertes ASCII mit einer
festen Maximalgrenze von 1.024 Bytes gelesen. Nicht-ASCII, fehlende Terminierung
oder ein Ordinal ausserhalb `NumberOfFunctions` ist ein Fehler.

Ein Init-Kandidat ist ausschliesslich ein exportierter Name mit dem exakten
Praefix `PyInit_` und mindestens einem folgenden ASCII-Zeichen. Dekorierte,
weitergeleitete oder nur aehnliche Exporte werden nicht normalisiert.
Weitergeleitete Exporte werden durch eine Funktions-RVA innerhalb des
Export-Directory-Bereichs erkannt und fuer Init-Symbole als Fehler behandelt.

Das Werkzeug dokumentiert alle Exporte, aber leitet nur aus exakt einem
eindeutigen `PyInit_<leafname>` einen Native-Nachweiskandidaten ab. Null,
mehrere Init-Exporte oder widerspruechliche Ordinal-/Funktionszuordnungen liefern
keinen akzeptierten Eintrag.

### Modulnamensgrenze

Der Export belegt nur den Leaf-Namen. Der vollqualifizierte Modulname darf erst
spaeter aus dem in 213N statisch aufgeloesten Importnamen und dem gebundenen
Paketpfad zugeordnet werden. Das Werkzeug darf aus Verzeichnissen allein keinen
Importnamen behaupten. ABI-Suffixe wie `.cp314-win_amd64` werden nur als
Dateinamensmetadaten ausgegeben, nicht als Namensbeweis.

## Teil B: statische CPython-Builtin-/Frozen-Tabellenbindung

### Durch Header belegte Layouts

`cpython/import.h` bindet fuer diese Installation:

- `_inittab`: Zeiger auf ASCII-Name, Zeiger auf Initfunktion;
- `_frozen`: Zeiger auf ASCII-Name, Zeiger auf Code, `int size`,
  `int is_package`;
- `PyImport_Inittab` und `PyImport_FrozenModules` als exportierte Datenzeiger.

`internal/pycore_import.h` bindet zusaetzlich:

- `_module_alias`: Zeiger auf Aliasname und Originalname;
- `_PyImport_FrozenBootstrap`, `_PyImport_FrozenStdlib` und
  `_PyImport_FrozenTest` als exportierte Datenzeiger;
- `_PyImport_FrozenAliases` als Alias-Tabelle.

Die Header belegen Layout und Symbolrollen, nicht die konkreten Eintraege.

### Zulaessiger Binary-Pfad

Teil B darf konkrete Eintraege nur aus der gebundenen `python314.dll` gewinnen.
Er muss zuerst in deren PE-Exporttabelle die benoetigten Datensymbole exakt
finden. Ein Exportname allein reicht nicht: Die zugeordnete RVA muss als
lesbarer Datenbereich belegt werden.

Fuer exportierte Zeigerslots gilt:

1. Der Slot muss vollstaendig innerhalb eines eindeutig abgebildeten
   Dateibereichs liegen und fuer AMD64 genau 8 Byte liefern.
2. Ein nichtnull Zeigerwert darf nur anhand von ImageBase und belegten
   Base-Relocation-Eintraegen in eine RVA normalisiert werden.
3. Jede verwendete Relocation muss zum Slot passen und den fuer PE32+/AMD64
   erwarteten Typ haben; nicht erkannte Typen sind kein Ersatzpfad.
4. Die normalisierte Ziel-RVA muss wieder eindeutig in dieselbe gebundene Datei
   abbildbar sein.
5. Nicht gebundene Laufzeitadressen oder angenommene Ladebasen sind unzulaessig.

Kann der gespeicherte Zeiger nicht allein aus den gebundenen Rohbytes und deren
Relocations eindeutig normalisiert werden, stoppt Teil B. Ein Scan nach
plausiblen Zeichenketten oder Tabellenmustern ist ausdruecklich verboten.

### Tabellenregeln

- `_inittab` wird in 16-Byte-Schritten gelesen und endet nur bei einem Eintrag
  mit Null-Name und Null-Initfunktion.
- `_frozen` wird mit dem aus den gebundenen Headern und AMD64-Alignment
  vorregistrierten 24-Byte-Layout gelesen und endet nur bei Null-Name,
  Null-Code, Groesse `0` und Paketflag `0`.
- `_module_alias` wird in 16-Byte-Schritten gelesen und endet nur bei zwei
  Nullzeigern.
- Maximal 4.096 Eintraege je Tabelle und maximal 1.024 Bytes je ASCII-Name sind
  zulaessig; ein Erreichen der Grenze ohne Terminator ist ein Fehler.
- Namen muessen nichtleer, nullterminiert und ASCII sein. Doppelte Namen mit
  unterschiedlichen Daten sind ein Fehler.
- Ein Builtin-Eintrag benoetigt nichtnull Name und Initfunktion.
- Ein Frozen-Eintrag benoetigt einen Namen, einen statisch abbildbaren
  Codezeiger und eine konsistente Groesse. Ein negatives `size` darf nicht
  still als Paketkennzeichen interpretiert werden, weil der gebundene
  Python-3.14.4-Header ein separates `is_package`-Feld vorgibt.
- `is_package` muss exakt `0` oder `1` sein.
- Jeder Alias benoetigt existierenden Alias- und Originalnamen. Aliaszyklen,
  Ketten ohne belegtes Original und Konflikte mit eigenstaendigen Eintraegen
  sind Fehler.

Bootstrap-, Stdlib- und Test-Frozen-Tabellen werden getrennt ausgegeben. Eine
Testtabelle darf nicht still in den spaeteren produktiven Manifestumfang
uebernommen werden. `PyImport_FrozenModules` wird als moeglicher Override
separat dokumentiert; ein nichtnull Override darf nicht mit den drei internen
Tabellen zusammengefuehrt werden, solange Prioritaet und Identitaet nicht
statisch eindeutig belegt sind.

## Festes Ausgabeformat

Das Werkzeug erzeugt atomar entweder einen vollstaendigen Nachweisdatensatz
oder nur einen Fehlerbericht. Vorgesehene Dateien:

- `pe_export_evidence.json`;
- `cpython_table_evidence.json`;
- `static_binary_evaluation_report.json`;
- `static_binary_evaluation_errors.json`, nur bei Fehlern.

Keines dieser Dokumente ist bereits das in 213P definierte Resolvermanifest.

### Gemeinsame Pflichtfelder

Jede JSON-Ausgabe enthaelt mindestens:

- `schema` mit festem versionsbezogenem Wert;
- `tool_binding` mit Pfad, Bytes und SHA-256 des spaeter freigegebenen
  Werkzeugs;
- `contract_binding` mit Pfad, Bytes und SHA-256 von 213Q;
- `platform` mit CPython `3.14.4`, Windows und AMD64;
- `input_bindings` fuer jede tatsaechlich gelesene Datei;
- `started_utc` und `finished_utc` nur als Laufmetadaten, nicht als Evidenz;
- `complete`, das nur bei vollstaendiger fehlerfreier Verarbeitung `true` ist;
- sortierte Ergebnisarrays und eine kanonische Sortierregel;
- `errors` und `stops` als Arrays, auch wenn sie leer sind.

`pe_export_evidence.json` enthaelt je `.pyd`: Bindung, PE-Maschine,
Export-Directory-Bindung, alle Exportnamen mit Ordinal und Funktions-RVA,
Weiterleitungsstatus sowie die Liste exakter `PyInit_*`-Kandidaten.

`cpython_table_evidence.json` enthaelt je Datensymbol: Export-RVA,
Zeigerslot, Relocation-Nachweis, normalisierte Ziel-RVA, Tabellenart,
terminierten Eintragsumfang und jeden Eintrag mit Name, Art, Paketflag,
Aliasziel und reproduzierbarem Evidence-Locator. Codebytes werden nicht als
separate Mediendatei oder Nutzlast exportiert; ihre RVA und gebundene Groesse
reichen fuer diesen Strukturbeleg.

Der Bericht enthaelt Zaehler pro Eingangs- und Ergebnisklasse, Bytegesamtsummen,
Fehlerzahl, Stopplinien und die eindeutige Feststellung, dass kein Resolver- oder
Manifestabschluss vorgenommen wurde.

## Determinismus und Atomaritaet

- Eingaben werden nach kanonischem, fallbewusstem Pfad sortiert.
- JSON wird als UTF-8 ohne BOM, mit festem Einzug, sortierten Schluesseln und
  abschliessendem LF geschrieben.
- Ergebnisreihenfolgen folgen `(input_path, export_name, ordinal)` bzw.
  `(table_kind, table_index, entry_index)`.
- Zeitstempel, Hostname und Arbeitsverzeichnis duerfen keine
  Auswertungsentscheidung beeinflussen.
- Ausgaben entstehen zuerst unter temporaeren Namen im expliziten
  Ausgabeordner und werden nur nach vollstaendiger Validierung umbenannt.
- Bei einem Fehler werden keine teilweise als `complete: true` markierten
  Evidenzdateien hinterlassen.
- Bereits vorhandene Ausgabedateien werden nicht ueberschrieben; der Vorgang
  stoppt vor dem ersten Schreibzugriff.

## Fehlermodell

Mindestens diese Fehlerklassen sind getrennt und mit Eingabepfad, Offset/RVA,
Struktur und Detail auszugeben:

- `INPUT_BINDING_MISMATCH`;
- `UNSUPPORTED_PE_FORMAT`;
- `TRUNCATED_STRUCTURE`;
- `INTEGER_OR_FILE_BOUNDS`;
- `AMBIGUOUS_RVA_MAPPING`;
- `MISSING_EXPORT_DIRECTORY`;
- `INVALID_EXPORT_TABLE`;
- `FORWARDED_INIT_EXPORT`;
- `INIT_EXPORT_CARDINALITY`;
- `MISSING_DATA_SYMBOL`;
- `UNSUPPORTED_RELOCATION`;
- `UNRESOLVED_DATA_POINTER`;
- `UNTERMINATED_TABLE`;
- `INVALID_ASCII_NAME`;
- `DUPLICATE_OR_CONFLICTING_ENTRY`;
- `INVALID_PACKAGE_FLAG`;
- `ALIAS_CONFLICT_OR_CYCLE`;
- `OUTPUT_ALREADY_EXISTS`;
- `INTERNAL_INVARIANT_FAILURE`.

Unbekannte oder nicht klassifizierbare Zustaende werden als
`INTERNAL_INVARIANT_FAILURE` behandelt und stoppen. Warnungen duerfen keine
Akzeptanzentscheidung ersetzen.

## Akzeptanzkriterien fuer einen spaeteren Werkzeuglauf

Ein spaeterer Lauf darf nur als vollstaendige Nachweiserhebung gelten, wenn:

1. Werkzeug und 213Q vorab separat bytegebunden und freigegeben sind;
2. alle ausgewaehlten Eingaben ihren 213P-Bindungen entsprechen;
3. alle 53 `.pyd`-Dateien vollstaendig verarbeitet wurden;
4. jede `.pyd` genau eine explizite Exportklassifikation besitzt;
5. alle benoetigten CPython-Datensymbole, Zeiger, Terminatoren und Eintraege
   ohne Heuristik statisch aufgeloest wurden;
6. alle Ergebnisdateien `complete: true`, leere `errors` und leere `stops`
   melden;
7. ein zweiter identischer Lauf auf denselben Bytes abgesehen von den
   nicht-evidentiellen Zeitfeldern byteidentische fachliche Inhalte liefert;
8. keine Laufzeit-, Netzwerk-, G2- oder Sicherheitsgrenze beruehrt wurde.

Diese Kriterien geben weder die Manifestgenerierung noch einen Resolverlauf
frei.

## Stopplinien

Der spaetere Werkzeuglauf stoppt vor einer fachlichen Ausgabe, wenn:

1. eine Eingangsbindung fehlt oder abweicht;
2. PE-Format, Architektur, Section- oder Directory-Grenzen nicht exakt passen;
3. eine RVA, ein Pointer oder eine Relocation nicht eindeutig statisch
   aufloesbar ist;
4. ein Init-Export fehlt, mehrfach, dekoriert, weitergeleitet oder
   widerspruechlich ist;
5. ein Datensymbol, Tabellenende, Name, Paketflag oder Alias nicht eindeutig
   belegt ist;
6. ein Grenzwert erreicht, eine Tabelle abgeschnitten oder ein Integerueberlauf
   moeglich ist;
7. eine nicht gebundene Datei, Laufzeitabfrage, Heuristik oder G2-Aufloesung
   erforderlich waere;
8. der Ausgabeordner nicht leer ist oder atomare Ausgabe nicht garantiert
   werden kann;
9. Werkzeugvertrag und tatsaechliche Implementierung voneinander abweichen.

Es gibt keinen permissiven Modus und keine Option zum Ueberspringen fehlerhafter
Dateien oder Tabellen.

## Messergebnisse und Gegenbaselines

Beobachtet:

- 213P bindet 53 Native-Kandidaten und die konkrete `python314.dll`;
- die gebundenen Header definieren `_inittab`, `_frozen`, `_module_alias` und
  die relevanten Datenzeiger;
- der bestehende Resolver konsumiert nur Manifestdaten und erbringt selbst
  keinen Binary-Nachweis;
- ein Werkzeug mit zwei getrennten Parserteilen ist erforderlich, bevor die
  Manifeste belastbar erzeugt werden koennen.

Gegenbaselines:

- Dateiname oder Paketpfad ohne `PyInit_*`-Export wird nicht als Native-Beleg
  akzeptiert.
- Zeichenketten- oder Mustersuche in `python314.dll` wird nicht als
  Tabellenbeleg akzeptiert.
- Laden der Binary und Abfrage exportierter Zeiger wird nicht als statische
  Auswertung akzeptiert.
- Teilverarbeitung mit Warnungen wird nicht als vollstaendiger Nachweis
  akzeptiert.

## Grenzen und nicht gepruefte Annahmen

- Es wurde nicht geprueft, ob alle benoetigten Datensymbole in der gebundenen
  `python314.dll` tatsaechlich exportiert sind.
- Es wurde nicht geprueft, ob deren Zeigerslots mit den vorhandenen
  Relocation-Daten statisch rekonstruierbar sind.
- PE-Exporte und Tabellen wurden nicht ausgelesen; alle spaeteren
  Ergebniszaehler bleiben offen.
- Das vorregistrierte 24-Byte-`_frozen`-Layout folgt den gebundenen
  Felddeklarationen und AMD64-Alignment; die Implementierung muss dieses Layout
  vor Verwendung gegen den Vertrag pruefen und bei Abweichung stoppen.
- Vollqualifizierte Native-Modulnamen erfordern weiterhin den spaeteren
  Importgraphabgleich.
- DLL-Abhaengigkeiten, `numpy.libs`, G2, Sicherheitszustaende und Huerde G sind
  nicht Gegenstand dieses Pakets.
- Die technische Machbarkeit eines vollstaendig statischen
  Builtin-/Frozen-Tabellenlesers ist noch nicht nachgewiesen.

## Konkrete Schlussfolgerung

Der statische Werkzeugvertrag ist vorregistriert. Er trennt Native-PE-Exporte
von den komplexeren CPython-Datentabellen, bindet beide an vorhandene Rohbytes
und stoppt bei jeder nicht eindeutig aus PE-Strukturen und Relocations
ableitbaren Aussage. Es wurde weder eine Implementierung noch Evidenz erzeugt.
G1 ist weiterhin nicht bestanden, G0 bleibt davon abhaengig und Huerde G bleibt
gesperrt. Eine erkennbare Zielabweichung liegt nicht vor.

## Vorschlag fuer den naechsten begrenzten Forschungs- und Entwicklungsschritt

Als naechstes sollte genau eine statische Implementierung dieses Vertrags
erstellt und selbst bytegenau dokumentiert werden. Sie darf nur Rohbytes parsen
und Nachweis-JSON vorbereiten; sie darf noch nicht gegen `python314.dll` oder
die 53 `.pyd`-Dateien ausgefuehrt, importiert, kompiliert oder getestet werden.
Ein Werkzeuglauf, eine Manifesterzeugung, ein Resolverlauf und G2 bleiben bis
zu einer weiteren Pruefung gesperrt.
