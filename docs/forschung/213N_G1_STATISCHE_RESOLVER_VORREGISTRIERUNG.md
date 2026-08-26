# 213N - G1 statische Resolver-Vorregistrierung

## Einordnung

213N ist ein statisches Entscheidungs- und Vorregistrierungspaket, kein
Forschungslauf und keine Resolverimplementierung. Es fuehrt keine Python-, NumPy-
oder Projektimporte aus, startet keine Tests oder Prozesse und bearbeitet G2 oder
Windows-Sicherheitszustand nicht.

## Forschungsfrage und Auftrag

Welche festen Regeln muss ein spaeter separat freizugebender statischer Resolver
einhalten, damit aus dem in 213M dokumentierten Mindestbefund ein begruendeter,
reproduzierbarer Python-/NumPy-Datei- und Elternverzeichnisabschluss fuer G1
entstehen kann?

Festzulegen sind Syntaxabdeckung, Windows-/Python-3.14.4-Konstanten, bedingte
Imports, `ImportError`-Zweige, Sternimporte, native Module, Paketdaten,
Elternverzeichnisse und Stopplinien. Dieses Dokument erhebt keine neuen
Laufzeitdaten.

## Tatsaechlich verwendete Quellen

- aktueller freigegebener Uebergabe-Eingang;
- `docs/forschung/213M_G1_STATISCHER_PYTHON_NUMPY_DATEIABSCHLUSS.md`;
- `docs/forschung/213F_STATISCHER_NACHWEISKATALOG_VOR_HUERDE_G_ENTSCHEIDUNG.md`;
- `docs/forschung/213A_STATISCHE_LOKALE_PYTHON_KORRIDOR_DATEI_UND_IMPORTKARTE.md`;
- `.venv/pyvenv.cfg`;
- `.venv/Lib/site-packages/numpy/__init__.py`;
- `.venv/Lib/site-packages/numpy/_core/__init__.py`.

Keine Webquelle und keine externe MCM-Quelle wurde verwendet.

## Verwendete Dateien und Schnittstellen

Die Quellen wurden ausschliesslich als Text und Rohbytes gelesen. Es wurden keine
Module importiert, kein Python-Interpreter, Test, Runner oder Zielprozess gestartet
und keine Datei ausser diesem Dokument veraendert.

## Gebundener Eingang

Ein spaeterer Resolverlauf darf nur von folgendem Eingang ausgehen:

- privater Einstieg:
  `mcm_field_organism/_runtime_fixation_single_use_path.py`;
- der in 213A gebundene relative private Projektgraph;
- dessen 13 nichtrelative Wurzeln:
  `__future__`, `dataclasses`, `enum`, `hashlib`, `hmac`, `json`, `math`, `numpy`,
  `pathlib`, `queue`, `re`, `time`, `typing`;
- Python-Basis: `C:/Python314`;
- Standardbibliothek: `C:/Python314/Lib`;
- native Python-Erweiterungen: `C:/Python314/DLLs` und die bereits in 213E
  gebundenen nativen Pfade;
- lokale Drittanbieterwurzel:
  `.venv/Lib/site-packages`;
- `.venv/pyvenv.cfg` mit Python `3.14.4` und
  `include-system-site-packages = false`;
- G1-Mindestbefund aus 213M: `17/17` Dateien, `467.482` Bytes.

Andere Arbeitsordner, Benutzer-Site-Packages, globale Site-Packages, Umgebungs-
Overrides und Netzwerkquellen sind keine stillen Ersatzwurzeln.

## Festgeschriebene Plattformkonstanten

Fuer einen spaeteren statischen Resolverlauf gelten genau diese Konstanten:

| Ausdrucksklasse | Vorregistrierter Wert |
|---|---|
| Betriebssystemfamilie | Windows |
| `os.name` | `nt` |
| `sys.platform` | `win32` |
| Python-Version | `3.14.4` |
| Implementierung | CPython |
| Architektur | AMD64 / 64 Bit |
| Byte-Reihenfolge | `little` |
| venv aktiv | ja, anhand `pyvenv.cfg` gebunden |
| System-Site-Packages | nein |
| NumPy-Paketwurzel | lokale venv unter `.venv/Lib/site-packages/numpy` |
| Typpruefmodus | `typing.TYPE_CHECKING = false` |
| NumPy-Setupmodus | `__NUMPY_SETUP__ = false`, soweit der Quellzweig diesen lokal setzt |
| Optimierungsmodus | nicht angenommen; kein Zweig darf daraus entfernt werden |
| Umgebungsvariablen | unbekannt, sofern nicht spaeter separat bytegenau gebunden |

Nur Bedingungen, die sich aus diesen Konstanten und literalen, lokal im selben
Kontrollfluss gesetzten Werten eindeutig entscheiden lassen, duerfen statisch auf
einen Zweig reduziert werden.

## Erforderliche Syntaxabdeckung

Ein spaeterer Resolver darf nicht zeilenbasiert arbeiten. Er muss mindestens den
vollstaendigen Python-3.14-Syntaxbaum der gebundenen `.py`-Dateien lesen und diese
Konstrukte klassifizieren:

1. `import a`, Aliasimporte und kommaseparierte Importe;
2. `from a import b`, Aliasnamen und geklammerte Mehrzeilenformen;
3. relative Importe jeder Punktebene;
4. `from a import *`;
5. Importe in Funktionen, Klassen, Schleifen und Kontextmanagern;
6. Importe unter `if`/`elif`/`else`, einschliesslich boolescher Ausdruecke,
   Vergleiche und Membership-Pruefungen;
7. Importe in `try`/`except`/`else`/`finally`, insbesondere
   `ImportError` und `ModuleNotFoundError`;
8. literale Aufrufe von `importlib.import_module` und `__import__`;
9. dynamische Importaufrufe mit nichtliteralem Modulnamen;
10. `exec`, `eval` und erzeugten Quelltext;
11. literale Datei- und Ressourcenaufrufe, darunter `open`, `Path`,
    `read_text`, `read_bytes`, `importlib.resources` und `pkgutil.get_data`;
12. Pfadbildung aus `__file__`, Elternpfaden und literalen Segmenten;
13. Manipulationen von `sys.path`, `os.add_dll_directory` und vergleichbaren
    Suchpfad-Schnittstellen;
14. Namespacepakete sowie Pakete mit und ohne `__init__.py`;
15. Syntaxfehler, unbekannte Kodierungen und nicht lesbare Dateien.

Jede erkannte Kante muss Quellpfad, Quellposition, syntaktische Klasse,
Bedingungskontext, Zielname und Aufloesungsergebnis tragen.

## Modul- und Paketaufloesung

Die statische Aufloesung erfolgt deterministisch und ohne Ausfuehrung:

1. Relative Projektimporte werden nur innerhalb `mcm_field_organism` aufgeloest.
2. Nichtrelative Namen werden zuerst gegen die vorregistrierte Builtin-/Frozen-
   Namenstabelle fuer exakt CPython 3.14.4 klassifiziert. Diese Tabelle muss vor
   einem Resolverlauf separat aus vorhandenen Installationsmetadaten oder
   dokumentierten Binärdaten gebunden sein; sie darf nicht durch Interpreterstart
   erzeugt werden.
3. Danach werden konkrete native Module aus den bereits statisch gebundenen
   Python-/NumPy-Pfaden geprueft.
4. Danach werden lokale venv-Pakete unter `.venv/Lib/site-packages` geprueft.
5. Danach wird `C:/Python314/Lib` geprueft.
6. Ein Dateimodul bindet die konkrete `.py`-Datei. Ein regulaeres Paket bindet
   zusaetzlich jedes auf dem Zielpfad erforderliche `__init__.py`.
7. Bei mehreren Kandidaten darf keine Prioritaet aus Plausibilitaet angenommen
   werden. Die Kollision wird ausgegeben und der Abschluss stoppt, sofern die
   Suchprioritaet nicht bereits statisch gebunden ist.
8. Benutzer-Site, Registry, `.pth`, Zipimport, Side-by-Side und Loader-Sonderpfade
   werden in G1 nicht still aufgeloest. Jeder Fund wird als G2-Abhaengigkeit
   ausgegeben und stoppt den G1-Abschluss bis zur getrennten Klaerung.

## Bedingte Importe

Jeder Import erhaelt eine der Klassen `required`, `excluded`, `alternative` oder
`unresolved`:

- `required`: Der umgebende Kontrollfluss ist unter den festgeschriebenen
  Konstanten eindeutig erreichbar.
- `excluded`: Der Kontrollfluss ist unter denselben Konstanten eindeutig nicht
  erreichbar; Ausdruck und Auswertung werden dokumentiert.
- `alternative`: Die Bedingung ist statisch nicht entscheidbar. Alle moeglichen
  Zielkanten werden getrennt erhalten, aber nicht als gleichzeitig benoetigt
  behauptet.
- `unresolved`: Syntax, Wertfluss oder externe Zustandseingabe verhindert eine
  belastbare Bedingungsbewertung.

Eine `alternative`- oder `unresolved`-Kante darf nicht still in eine Freigabeliste
umgewandelt werden. Sie erzeugt einen offenen Nachweis und damit G1-STOPP.

## `ImportError`- und Fallback-Zweige

Fuer `try`-Importe mit `except ImportError` oder `ModuleNotFoundError` gilt:

1. Der Primaername und jeder Fallbackname werden separat aufgeloest.
2. Nur wenn die Primaeraufloesung unter den gebundenen Suchwurzeln eindeutig ist
   und keine importzeitige Ausnahme jenseits reiner Namensabwesenheit relevant sein
   kann, darf der Fallback als `excluded` klassifiziert werden.
3. Weil ein vorhandenes Modul beim spaeteren Ausfuehren intern dennoch
   `ImportError` ausloesen kann, ist diese Ausnahme ohne Ausfuehrung grundsaetzlich
   nicht vollstaendig entscheidbar. Solche Faelle bleiben `alternative`, sofern der
   Quelltext die Ausnahme nicht nachweisbar auf einen bestimmten fehlenden Namen
   begrenzt.
4. Breite `except Exception`- oder bare `except`-Fallbacks bleiben offen.

## Sternimporte

`from paket import *` wird nur dann geschlossen, wenn:

- das Zielmodul eindeutig aufgeloest ist;
- ein statisch literales `__all__` vollstaendig bestimmt werden kann;
- jede daraus referenzierte Untermodulkante separat aufgeloest wird;
- keine Mutation, Konkatenation mit unbekannten Werten oder dynamische
  `__getattr__`-/Lazy-Importlogik die Exportmenge veraendert.

Ohne diese Bedingungen bleibt die Sternimportkante `unresolved` und G1 stoppt. Das
blosse Lesen aller Dateien eines Pakets ist kein zulaessiger Ersatz.

## Native und eingebaute Module

Jeder nicht als `.py` aufgeloeste Name muss genau einer Klasse zugeordnet werden:

- CPython Builtin;
- Frozen-Modul;
- konkrete `.pyd`-Datei;
- konkrete `.dll`-Folgekante aus dem gebundenen PE-Abschluss;
- API-Set-/Extension-Set-Vertrag aus 213E;
- fehlend;
- offen.

Fuer konkrete Dateien werden Pfad, Existenz, Groesse und SHA-256 ausgegeben. Bereits
in G0/213E gebundene Dateien werden referenziert und dedupliziert, nicht doppelt zur
Bytesumme addiert. Ein Name ohne gebundene Klassifikation stoppt G1. Reale
Loaderreihenfolge, `os.add_dll_directory`, Delay-Load und `LoadLibrary` bleiben G2.

## Paketdaten und Dateiverweise

Ein Paketdatenobjekt wird nur aufgenommen, wenn ein statischer Dateiverweis aus
einer als `required` klassifizierten Quelldatei besteht. Der Resolver muss ausgeben:

- Quellpfad und Quellposition;
- verwendete Datei-API;
- literalen oder statisch zusammensetzbaren relativen Zielpfad;
- aufgeloesten absoluten Pfad;
- Existenz, Dateityp, Groesse und SHA-256;
- bei Verzeichnissen die konkrete, begruendete Auswahlregel.

Nichtliterale Ressourcenamen, Glob-Muster, Verzeichnisiteration, Metadatenabfragen
und Pluginentdeckung bleiben offen. Ein gesamter Datenbaum darf nicht pauschal
gebunden werden. `.pyc` wird nur aufgenommen, wenn ein spaeter gebundener
Startvertrag genau dessen Nutzung statt der `.py`-Quelle statisch festlegt; eine
moegliche Cacheerzeugung ist zusaetzlich G10-relevant.

## Elternverzeichnisabschluss

Fuer jede gebundene Datei muss die deduplizierte Elternkette bis zu genau einer
vorregistrierten Wurzel ausgegeben werden:

- Projektworkspace;
- `C:/Python314`;
- `.venv`;
- eine bereits in 213E gebundene Systemwurzel.

Je Verzeichnis sind absoluter normalisierter Pfad, Existenz, Reparse-Status und
Ziel, falls vorhanden, auszugeben. Die Auflistung ist noch keine ACL- oder
Traverse-Freigabe; Sicherheitsdeskriptoren gehoeren zu G3/G4. Ein nicht existentes,
nicht lesbares oder nicht eindeutig normalisierbares Elternverzeichnis stoppt G1.

## Deterministische Arbeitswarteschlange

Der spaetere Resolver muss eine sortierte, deduplizierte Warteschlange verwenden.
Der Schluessel besteht aus normalisiertem Zielnamen, absolutem Zielpfad und
Bedingungsklasse. Jede Datei wird hoechstens einmal syntaktisch gelesen; mehrere
Kanten bleiben als Provenienz erhalten. Zyklen werden als Kanten dokumentiert, aber
erzeugen keine erneute Verarbeitung. Gross-/Kleinschreibung wird fuer Windows-Pfade
vergleichend normalisiert, der beobachtete Pfadstring bleibt erhalten.

## Pflichtausgabe eines spaeteren Resolverlaufs

Ein Ergebnis muss mindestens enthalten:

1. Hash und Groesse aller Resolvereingaben und der Vorregistrierung;
2. alle verwendeten Konstanten;
3. vollstaendige Kantenliste mit Provenienz und Bedingungsklasse;
4. eindeutige Python-Dateiliste mit Pfad, Groesse und SHA-256;
5. native/Builtin/Frozen-Klassifikation aller nicht-Python-Namen;
6. konkrete Paketdatenliste;
7. deduplizierte Elternverzeichnisliste;
8. Kollisionen, Alternativen, unaufgeloeste Namen und G2-Verweise;
9. getrennte Summen fuer neue G1-Dateien und bereits in G0 deduplizierte Dateien;
10. Gegenbaselines gegen den 17-Dateien-Mindestbefund, die 465-Dateien-
    Ueberapproximation und den 4.831-Dateien-Installationsbaum;
11. eindeutige Entscheidung `G1 bestanden` oder `G1 nicht bestanden`.

## Vorregistrierte Akzeptanzkriterien

G1 darf nur als bestanden ausgegeben werden, wenn gleichzeitig:

- alle erforderlichen Quelldateien syntaktisch lesbar sind;
- jede Importkante klassifiziert ist;
- `alternative = 0` und `unresolved = 0` gelten;
- jeder erforderliche Python-, native oder Datenpfad eindeutig existiert;
- jede konkrete Datei Groesse und SHA-256 besitzt;
- alle erforderlichen Paketinitialisierungen enthalten sind;
- die Elternverzeichnisliste vollstaendig und dedupliziert ist;
- keine unbegruendete Freigabe eines gesamten installierten Baums erfolgt;
- G2-relevante Funde nur als offene Abhaengigkeit ausgewiesen und nicht als in G1
  geschlossen behauptet werden;
- die neue G1-Menge gegen G0 bytegenau dedupliziert werden kann;
- eine unabhaengige statische Reproduktion dieselben Zaehler und Digests ergibt.

Bereits ein verletztes Kriterium bedeutet `G1 nicht bestanden`.

## Stopplinien

Der Resolverlauf muss ohne Ersatzannahme stoppen bei:

- Syntaxfehler oder nicht unterstuetzter Python-3.14-Syntax;
- nicht lesbarer oder waehrend der Erhebung veraenderter Datei;
- Digestabweichung einer Eingangsdatei;
- dynamischem Modul- oder Ressourcennamen;
- nicht entscheidbarer Bedingung;
- offenem Sternimport;
- uneindeutigem Modulpfad oder Namenskollision;
- unklassifiziertem Builtin-, Frozen- oder nativen Namen;
- `.pth`, Registry, Zipimport, Namespace- oder Loader-Sonderpfad ohne getrennte
  statische Bindung;
- offenem Paketdatenzugriff;
- fehlendem oder uneindeutigem Elternverzeichnis;
- Versuch, Tests, Imports oder Prozesse zur Aufloesung zu starten.

Ein Stopp ist ein methodischer G1-Befund und darf nicht durch Aufnahme des gesamten
Installationsbaums umgangen werden.

## Durchgefuehrte Schritte

1. G1-Mindestkriterium und den Zwischenbefund 213M gelesen.
2. Eingangsdateien, Suchwurzeln und Plattformkonstanten festgeschrieben.
3. Erforderliche Syntax- und Kontrollflussklassen definiert.
4. Regeln fuer Paket-, native, Builtin-, Daten- und Elternpfadauflösung festgelegt.
5. Pflichtausgaben, Akzeptanzkriterien und Stopplinien vorregistriert.
6. Keine Resolverimplementierung und keinen Resolverlauf durchgefuehrt.

## Messergebnisse und Gegenbaselines

Dieses Paket erzeugt keine neue Dateiauswahl und keine dynamischen Messwerte.

- gebundene Ausgangswurzeln: `13`;
- vorregistrierte Plattformkonfigurationen: `1`;
- Bedingungsklassen: `4`;
- Pflichtausgabeklassen: `11`;
- neue Resolverimplementierungen: `0`;
- Imports, Tests, Prozesse, G2- und Sicherheitsaktionen: jeweils `0`;
- G1-Stand vor und nach dieser Vorregistrierung: `nicht bestanden`.

Gegenbaselines bleiben:

| Gegenbaseline | Rolle |
|---|---|
| 17 Dateien / 467.482 Bytes | bytegenauer Mindestbefund, kein Abschluss |
| 465 Dateien / 11.131.140 Bytes | zeilenbasierte Ueberapproximation, nicht trennscharf |
| 4.831 Dateien / 134.440.989 Bytes | installierter Gesamtbaum, keine Startauswahl |

## Grenzen und nicht gepruefte Annahmen

- **Beobachtetes Ergebnis:** Der Resolververtrag ist statisch formuliert; ein
  Resolverlauf liegt nicht vor.
- **Technische Interpretation:** Die Regeln adressieren die in 213M beobachtete
  Unter- und Ueberapproximation, beweisen aber noch keinen konkreten Abschluss.
- **Hypothese:** Ein spaeter regelkonformer statischer Resolver koennte die offene
  G1-Menge weiter eingrenzen. Ob er `alternative = 0` und `unresolved = 0` erreicht,
  ist offen.
- **Offene Frage:** Ob Python-/NumPy-Quelllogik ohne Ausfuehrung alle importzeitigen
  Fallbackentscheidungen eindeutig aufloesen laesst, ist nicht geprueft.
- **Nicht gepruefte Annahme:** Die vorregistrierten statischen Regeln werden nicht
  als Ersatz fuer reale Loader-, Dateizugriffs- oder Artefaktbeobachtung behandelt.
- G2, G3, G4 und alle spaeteren Gates bleiben unberuehrt.
- Es gibt keinen Befund zu Feldwirkung, Memory, Organisation, Topologie, Semantik,
  Selbstregulation oder KI.

## Konkrete Schlussfolgerung

Der G1-Resolver ist als statischer Vertrag vorregistriert. G1 bleibt **nicht
bestanden**, weil weder eine Implementierung noch ein regelkonformer statischer Lauf
vorliegt. Die Vorregistrierung erteilt keine Implementierungs-, Import-, Test- oder
Ausfuehrungsfreigabe. G0 bleibt vom offenen G1-Umfang abhaengig, G2 bleibt offen und
Huerde G bleibt gesperrt. Eine erkennbare Zielabweichung liegt nicht vor.

## Vorschlag fuer den naechsten begrenzten Schritt

Als naechster Schritt ist ausschliesslich die unabhaengige statische Pruefung dieses
Vorregistrierungspakets zweckmaessig. Zu pruefen sind Vollstaendigkeit und
Widerspruchsfreiheit der Syntax-, Bedingungs-, Aufloesungs-, Daten-, Elternpfad-,
Akzeptanz- und Stopplinienregeln. Eine Resolverimplementierung oder ein technischer
Lauf darf erst durch einen separaten Auftrag freigegeben werden.
