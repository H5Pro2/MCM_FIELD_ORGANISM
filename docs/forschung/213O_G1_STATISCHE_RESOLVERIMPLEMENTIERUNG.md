# 213O - G1 statische Resolverimplementierung

## Einordnung

213O dokumentiert die gemaess 213N erstellte statische Resolverimplementierung.
Dies ist kein Forschungslauf und kein G1-Resolverlauf. Die Implementierung wurde
nicht importiert, gestartet oder getestet.

## Forschungsfrage und Auftrag

Kann genau eine eigenstaendige statische Resolverimplementierung erstellt werden,
die den Vertrag aus 213N technisch abbildet, Projekt- und NumPy-Quellen nur als
Daten behandelt und bei offenen Alternativen, Ressourcen oder G2-Kanten konservativ
stoppt?

Freigegeben war nur die Implementierung mit anschliessender statischer
Dokumentation. Nicht freigegeben waren Resolverlauf, Projektimporte, Tests,
Zielprozessstarts, G2, SID, Profil, ACL, SACL oder Huerde G.

## Tatsaechlich verwendete Quellen

- aktueller freigegebener Uebergabe-Eingang;
- `docs/forschung/213N_G1_STATISCHE_RESOLVER_VORREGISTRIERUNG.md`;
- vorhandene Werkzeugkonventionen unter `tools/`;
- neu erstellte Datei `tools/static_g1_resolver.py`.

Keine Webquelle und keine externe MCM-Quelle wurde verwendet.

## Verwendete Dateien und Schnittstellen

Die Implementierung verwendet bei einem spaeter separat freizugebenden Lauf nur
Python-Standardbibliotheksschnittstellen:

- `ast` fuer Python-3.14-Syntaxbaeume;
- `pathlib` fuer normalisierte Dateipfade;
- `hashlib` fuer SHA-256;
- `json` fuer gebundene Manifeste und Ergebnisausgabe;
- `argparse` fuer explizite Eingaben;
- `dataclasses` und `typing` fuer strukturierte interne Datensaetze.

Es existiert keine Importanweisung fuer `mcm_field_organism`, NumPy oder ein anderes
Drittanbieterpaket. Zielquellen werden ausschliesslich als Bytes und Text gelesen.

## Implementierte Eingangsbindung

Der Resolver verlangt explizit:

- `--workspace`;
- `--python-root`;
- `--venv-root`;
- `--builtin-manifest`;
- `--native-manifest`;
- `--specification`;
- optional `--output`.

Vorregistrierung, Builtinmanifest, Nativmanifest und `pyvenv.cfg` werden als
Eingangsdateien mit Pfad, Groesse und SHA-256 gebunden. Die Implementierung besitzt
keinen stillen Standardpfad fuer Benutzer-Site-Packages, Registry oder Netzwerk.

Builtin-/Frozen-Namen muessen aus einem vorab gebundenen JSON-Manifest stammen.
Native Namen muessen Pfad, Groesse und SHA-256 im Nativmanifest besitzen; eine
Abweichung erzeugt einen Stopp. Diese beiden Manifeste wurden in diesem Auftrag
nicht erstellt.

## Implementierte Plattformbindung

Fest kodiert sind die in 213N vorregistrierten statischen Konstanten:

- `os.name = nt`;
- `sys.platform = win32`;
- `sys.byteorder = little`;
- `sys.version_info = (3, 14, 4)`;
- `sys.implementation.name = cpython`;
- `typing.TYPE_CHECKING = false`;
- `__NUMPY_SETUP__ = false`.

Der Bedingungsauswerter unterstuetzt Konstanten, Negation, boolesche Verknuepfung,
einfache und verkettete Vergleiche, Membership sowie literale Sequenzen. Nicht
auswertbare Bedingungen werden nicht geraten.

## Implementierte Syntax- und Kantenabdeckung

Die Implementierung verarbeitet ueber den Syntaxbaum:

- einfache, aliasierte und mehrteilige `import`-Anweisungen;
- absolute und relative `from`-Importe;
- aufloesbare importierte Untermodule;
- Sternimporte mit statisch literalem `__all__`;
- literale dynamische Importe;
- nichtliterale dynamische Importe als Stopp;
- `if`-/`elif`-/`else`-Zweige;
- `try`-/`except`-/`else`-/`finally` und `try*`;
- Importe in Funktionen als nicht statisch aufgerufene Alternativen;
- `for`, `async for`, `while` und `match` als konservative Alternativen;
- bekannte Datei-/Ressourcen-APIs;
- bekannte Suchpfad- und `os.add_dll_directory`-Aufrufe als G2-Verweise.

Jede Importkante traegt Quelle, Zeile, Spalte, Syntaxklasse, Zielname,
Bedingungsklasse, Aufloesungsklasse, Zielpfade und Detailtext. Die vier
Bedingungsklassen lauten `required`, `excluded`, `alternative` und `unresolved`.

## Implementierte Modulaufloesung

Die Aufloesung trennt:

- private Projektmodule unter dem Workspace;
- Builtin- und Frozen-Module aus dem Eingangsmanifest;
- native Module aus dem Eingangsmanifest;
- lokale venv-Pakete;
- Python-Standardbibliothek;
- konkrete Python-Module und regulaere Pakete;
- fehlende, kollidierende, offene und G2-relevante Ziele.

Elternpaket-`__init__.py`-Dateien werden in die sortierte Warteschlange aufgenommen.
Mehrere Kandidaten werden nicht priorisiert, sondern als Kollision gestoppt. Die
Warteschlange ist sortiert und dedupliziert; Zyklen werden nicht erneut verarbeitet.

## Implementierte Datei-, Ressourcen- und Elternbindung

Jede gebundene konkrete Datei erhaelt absoluten Pfad, Klasse, Groesse und SHA-256.
Ressourcenaufrufe werden mit API, Ausdruck, Bedingung und Quellposition erfasst.
Nicht vollstaendig aufgeloeste Ressourcen fuehren in der Abschlussbewertung zum
Stopp; sie werden nicht still ignoriert.

Fuer jede konkrete Datei wird die deduplizierte Elternkette bis zur engsten
registrierten Wurzel aufgebaut. Ausgegeben werden Existenz, Symlinkstatus,
aufgeloester Pfad und zugehoerige Wurzel. Fehlende Eltern oder Dateien ausserhalb
der Wurzeln stoppen den Abschluss.

## Implementierte Stopplinie und Ausgabe

Der Resolver gibt ein deterministisch sortiertes JSON-Dokument mit Eingangsbindungen,
Dateien, Importkanten, Ressourcen, Elternverzeichnissen, G2-Verweisen, Stopps,
Zaehlern und `g1_passed` aus.

`g1_passed` kann nur wahr werden, wenn gleichzeitig:

- keine Stopps bestehen;
- `alternative = 0`;
- `unresolved = 0`;
- keine G2-Verweise bestehen;
- alle Elternverzeichnisse vorhanden sind.

Ein nicht bestandenes Ergebnis liefert Rueckgabecode `1`, ein bestandenes Ergebnis
Rueckgabecode `0`. Diese Logik wurde nur statisch gelesen, nicht ausgefuehrt.

## Durchgefuehrte Schritte

1. Werkzeugstruktur und lokale Konventionen read-only untersucht.
2. Den Resolver als eine neue, vom Projektpaket getrennte Werkzeugdatei erstellt.
3. Strukturierte Datensaetze fuer Dateien, Kanten, Ressourcen und Eltern angelegt.
4. Syntaxbaum-, Bedingungs-, Modul-, Manifest-, Ressourcen- und Elternlogik
   implementiert.
5. Warteschlange, Deduplikation, Pflichtzaehler und Stopplinie implementiert.
6. Quelltext statisch auf Standardbibliotheks- und verbotene Projektimporte geprueft.
7. Dateigroesse und SHA-256 der Implementierung erhoben.
8. Keinen Resolverlauf, Import, Test oder Zielprozess ausgefuehrt.

## Messergebnisse und Gegenbaselines

Statische Kennwerte der Implementierung:

| Kennwert | Ergebnis |
|---|---:|
| Implementierungsdateien | 1 |
| Bytes | 30.616 |
| Zeilen | 769 |
| Klassen | 11 |
| Funktionen und Methoden | 46 |
| Projekt-/NumPy-Importanweisungen | 0 |
| Resolverlaeufe | 0 |
| Tests | 0 |
| Zielprozessstarts | 0 |

Dateibindung:

| Pfad | Bytes | SHA-256 |
|---|---:|---|
| `tools/static_g1_resolver.py` | 30.616 | `edf16697ca8a7bd5b8443a75691ca48f3c9f6067f738c0e540b2c4df54daf7ca` |

Gegenbaselines:

| Gegenbaseline | Abgrenzung |
|---|---|
| zeilenbasierter Resolver aus 213M | ersetzt durch Syntaxbaumanalyse |
| Projekt- oder NumPy-Import zur Aufloesung | nicht vorhanden und nicht erforderlich |
| still erzeugte Builtin-/Native-Liste | ausgeschlossen; beide Manifeste sind Pflichtinput |
| offene Ressource als bestanden behandeln | ausgeschlossen; erzeugt Stopp |
| G2-Kante innerhalb G1 schliessen | ausgeschlossen; G2-Verweis verhindert `g1_passed` |
| gesamte Installation bei Unsicherheit aufnehmen | nicht implementiert |

## Grenzen und nicht gepruefte Annahmen

- **Beobachtetes Ergebnis:** Eine statisch prüfbare Resolverimplementierung liegt
  als einzelne Werkzeugdatei vor. Sie wurde nicht ausgefuehrt.
- **Technische Interpretation:** Die Implementierung bildet die wesentlichen
  Eingangs-, Syntax-, Kanten-, Manifest-, Ressourcen-, Eltern- und Stopplinienregeln
  aus 213N ab.
- **Hypothese:** Ein spaeterer Lauf wird wegen konservativer Alternativ- und
  Ressourcenklassifikation zunaechst wahrscheinlich mit `G1 nicht bestanden`
  stoppen. Dies ist nicht geprueft.
- **Offene Frage:** Ob die statische Kontrollflussabdeckung fuer alle konkret
  erreichten Python-3.14.4-/NumPy-Quellen ausreicht, kann erst nach separater
  Freigabe eines Resolverlaufs beurteilt werden.
- **Nicht gepruefte Annahme:** Syntaxgueltigkeit, Laufzeitfehlerfreiheit und
  Ergebniszaehler werden nicht behauptet, weil Imports, Kompilierung und Tests
  ausdruecklich gesperrt waren.
- Builtin- und Nativmanifeste fehlen noch als gebundene Eingaben.
- Literale Ressourcen werden erfasst, aber nicht ohne eindeutig gebundene
  Wurzelrelation als konkrete Datei freigegeben.
- G2, SID, Profil, ACL, SACL und Huerde G wurden nicht bearbeitet.
- Es gibt keinen Befund zu Feldwirkung, Memory, Organisation, Topologie, Semantik,
  Selbstregulation oder KI.

## Konkrete Schlussfolgerung

Die genau eine freigegebene statische Resolverimplementierung ist erstellt und
statisch dokumentiert. Sie importiert weder Projektcode noch NumPy und wurde nicht
ausgefuehrt. G1 bleibt **nicht bestanden**, weil noch kein gepruefter Resolverlauf
und noch keine freigegebenen Builtin-/Nativmanifeste vorliegen. G0 bleibt abhaengig,
G2 und Huerde G bleiben gesperrt. Eine erkennbare Zielabweichung liegt nicht vor.

## Vorschlag fuer den naechsten begrenzten Schritt

Als naechster Schritt ist ausschliesslich eine unabhaengige statische Codepruefung
von `tools/static_g1_resolver.py` gegen 213N zweckmaessig. Zu pruefen sind insbesondere
fehlende Syntaxklassen, falsche Zustandsreduktionen, Suchprioritaet,
Manifestvalidierung, Sternimport-, Ressourcen-, Elternpfad- und Stopplinienlogik.
Noch kein Resolverlauf, kein Import, kein Test und keine G2-Bearbeitung.
