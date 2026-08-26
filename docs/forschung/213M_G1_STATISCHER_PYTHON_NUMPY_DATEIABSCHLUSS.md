# 213M - G1 statischer Python-/NumPy-Dateiabschluss

## Einordnung

213M ist eine statische Read-only-Erhebung und kein Forschungslauf. Es werden keine
Module importiert, Tests oder Zielprozesse gestartet und keine Sicherheits- oder
Systemaenderungen vorgenommen.

## Forschungsfrage und Auftrag

Welche konkreten Python-Standardbibliotheks- und NumPy-Pythondateien lassen sich fuer
den in 213A gebundenen privaten Einstieg allein aus vorhandenen statischen Quellen
begruendet binden, welche Auswahlregeln gelten und welche Grenzen verhindern derzeit
einen abgeschlossenen G1-Nachweis?

G1 fordert nach 213F eine exakte Datei- und Elternverzeichnisliste fuer benoetigte
Standardbibliotheks-, NumPy-Python- und Datendateien einschliesslich
Paketinitialisierung. Eine pauschale Freigabe des gesamten installierten Baums ist
ausgeschlossen.

## Tatsaechlich verwendete Quellen

- aktueller freigegebener Uebergabe-Eingang;
- `docs/forschung/213F_STATISCHER_NACHWEISKATALOG_VOR_HUERDE_G_ENTSCHEIDUNG.md`;
- `docs/forschung/213A_STATISCHE_LOKALE_PYTHON_KORRIDOR_DATEI_UND_IMPORTKARTE.md`;
- `docs/forschung/213E_STATISCHE_LOADER_STDLIB_NUMPY_SYSTEM_DLL_PFADBAUM_ISTAUFNAHME.md`;
- `.venv/pyvenv.cfg`;
- die unten einzeln gebundenen lokalen Python-Dateien.

Keine Webquelle und keine externe MCM-Quelle wurde verwendet.

## Verwendete Dateien und Schnittstellen

Verwendet wurden ausschliesslich read-only Dateisystemzugriffe, statische Textsuche,
Dateigroessen und SHA-256-Berechnung. Der Textresolver wurde nur im Arbeitsspeicher
ausgefuehrt. Python, NumPy und Projektmodule wurden nicht importiert oder gestartet.

## Ausgangslage und Auswahlregeln

213A belegt fuer die 20 privaten Projektmodule diese 13 nichtrelativen
Importwurzeln:

`__future__`, `dataclasses`, `enum`, `hashlib`, `hmac`, `json`, `math`, `numpy`,
`pathlib`, `queue`, `re`, `time`, `typing`.

Fuer diese G1-Erhebung gelten folgende Regeln:

1. Ausgangspunkte sind ausschliesslich die 13 in 213A belegten Wurzeln.
2. Ein reines Modul wird als gleichnamige `.py`-Datei gebunden.
3. Ein Paket wird zuerst durch sein `__init__.py` gebunden; fuer NumPy werden die
   dort eindeutig und unbedingt bezeichneten initialen Unterdateien aufgenommen.
4. `math` und `time` werden nicht als Python-Dateien erfunden. 213E ordnet sie dem
   Interpreter beziehungsweise nativen Abschluss zu; ihre konkrete native
   Zuordnung bleibt ausserhalb dieses G1-Python-Teilbefunds.
5. `.pyc`, `.pyi`, Tests, Beispiele, Builddateien und Paketdaten werden nicht
   pauschal aufgenommen. Sie duerfen nur durch eine konkrete statische Kante oder
   einen konkreten Dateiverweis gebunden werden.
6. Bedingte, dynamische, plattformabhaengige und aus `from ... import *` entstehende
   Kanten werden nicht als sicher benoetigt behauptet.
7. `include-system-site-packages = false` aus `.venv/pyvenv.cfg` begrenzt die
   Drittanbieterwurzel auf die lokale venv; es beweist keine reale Suchreihenfolge.

## Direkt belegte Standardbibliotheksdateien

| Importwurzel | Pfad | Bytes | SHA-256 |
|---|---|---:|---|
| `__future__` | `C:/Python314/Lib/__future__.py` | 5.365 | `bf11d13b6c9b2b8706be425addf399965738622bb4cc553217be16399c51d51a` |
| `dataclasses` | `C:/Python314/Lib/dataclasses.py` | 73.162 | `9e247c9f3b6f09c9f4684368487f54efbe573da8779da601a169ec8989bfc9e1` |
| `enum` | `C:/Python314/Lib/enum.py` | 87.610 | `81866aafa2a0a4ef1f542ce0b9aa26c8779086924704269e5df8c2676554741b` |
| `hashlib` | `C:/Python314/Lib/hashlib.py` | 9.714 | `271b00a30d27c3cdd99b7f70962680f8455d3057b3c103f028e2da31141b91ee` |
| `hmac` | `C:/Python314/Lib/hmac.py` | 9.858 | `d61c744b17d6a07e5b2e7b952de0b42053871f3fac6599910c30eb666fe2394e` |
| `json` | `C:/Python314/Lib/json/__init__.py` | 14.431 | `0439e6546415d4147396afac324beadb7a8dc2c1e2391dcb541fb34c83986d8f` |
| `pathlib` | `C:/Python314/Lib/pathlib/__init__.py` | 48.114 | `208546aa566ca8df4b8e1259f30209c0f803c3f920e6d080ae1b10d53d05bd72` |
| `queue` | `C:/Python314/Lib/queue.py` | 13.838 | `6034bec6d992edef9753ff7022ff5c6dfc252fed0339315dfaa47bdae6b99546` |
| `re` | `C:/Python314/Lib/re/__init__.py` | 18.304 | `5e285750c13fdf690a100379ec133d2038bb0f6c6e1b51206caf94e41288440b` |
| `typing` | `C:/Python314/Lib/typing.py` | 139.132 | `78437f3e0ddb98907d7ca5ded507767103a5352dddec1513dcc8d737f2ecbb84` |
| **Summe** | **10 Dateien** | **419.528** | |

Alle zehn Dateien sind vorhanden. `pathlib.py` existiert in dieser Python-3.14.4-
Installation nicht; die Wurzel wird durch `pathlib/__init__.py` realisiert.

## Direkt belegte NumPy-Initialisierungsdateien

Der direkte Import `numpy` bindet zuerst `numpy/__init__.py`. Dessen statischer
Initialisierungspfad bezeichnet vor dem breiteren `_core`-Import die Versions-,
Attribut-, Global-, Distributor- und Konfigurationsdateien sowie
`numpy/_core/__init__.py`.

| Rolle | Relativer Pfad unter `.venv/Lib/site-packages/` | Bytes | SHA-256 |
|---|---|---:|---|
| Paketinitialisierung | `numpy/__init__.py` | 26.470 | `a6958cb364663b7acce81ccfd58eeb65a2b34d5376157f924777b97211a73be4` |
| Version | `numpy/version.py` | 304 | `3318dccdcc15ce17bafd08756a01a5bf55e24c0f33b15eb690959011f913a70e` |
| abgelaufene Attribute | `numpy/_expired_attrs_2_0.py` | 3.853 | `7fba906bc3cd76d97be7f446ce120379a98e925458465aa5caf65a988b4e513b` |
| globale Objekte | `numpy/_globals.py` | 4.277 | `22fb9c5a81e206f4e592b5fefd6d90c38be2ade565381de6b3d502b00f5a1cf` |
| Distributorinitialisierung | `numpy/_distributor_init.py` | 436 | `879fc2abb22d0ebb75259a00874e1a3b9e195ec5d1464c86a0d1451fd4fed3c5` |
| Konfiguration | `numpy/__config__.py` | 5.749 | `5dca7e6e901bdcd783c9e9cb01aa8b186f463cc951d4e17e69d471cc73f2f040` |
| Core-Paketinitialisierung | `numpy/_core/__init__.py` | 6.865 | `73c57a7f3a54e33399ddb9b142eb27ed3aae2bf4be2f4c159396788e16b620e5` |
| **Summe** | **7 Dateien** | **47.954** | |

Alle sieben Dateien sind vorhanden. `numpy/__init__.py` bezeichnet ausserdem den
Nachbarpfad `numpy.libs` und fuegt ihn bei vorhandener Verzeichnisstruktur ueber
`os.add_dll_directory` hinzu. Die zwei dort vorhandenen DLLs sind bereits in 213E
und G0 gebunden; diese Beobachtung ist zugleich eine offene G2-Sonderpfadkante und
wird hier nicht als G2-Abschluss bewertet.

## Statischer Mindestbefund

| Klasse | Dateien | Vorhanden | Fehlend | Bytes |
|---|---:|---:|---:|---:|
| direkte Standardbibliotheksanker | 10 | 10 | 0 | 419.528 |
| direkte NumPy-Initialisierungsanker | 7 | 7 | 0 | 47.954 |
| **Summe** | **17** | **17** | **0** | **467.482** |

Die 17 Dateien sind ein reproduzierbarer Mindestbefund. Sie sind ausdruecklich
kein abgeschlossener Laufzeitkorpus.

## Rekursive Gegenbaseline

Ein konservativer zeilenbasierter Textresolver wurde ab den 13 Wurzeln rekursiv
ueber lokal aufloesbare `import`- und `from`-Zeilen gefuehrt. Er ergab:

| Klasse | Dateien | Bytes |
|---|---:|---:|
| Dateien unter `C:/Python314/Lib` | 253 | 6.514.964 |
| Dateien unter `.venv/Lib/site-packages` | 212 | 4.616.176 |
| **Summe** | **465** | **11.131.140** |

Zusaetzlich blieben 115 Namen im verwendeten Dateiresolver unaufgeloest. Darunter
sind eingebaute und native Module, Plattformalternativen, optionale Drittanbieter,
Testabhaengigkeiten und syntaktische Fehlgriffe des Zeilenresolvers. Der Abschluss
zog beispielsweise Plattform-, Test- und optionale Paketzweige ein. Deshalb ist
die 465-Dateien-Menge eine Ueberapproximations-Gegenbaseline und keine begruendete
Freigabeliste.

## Durchgefuehrte Schritte

1. G1-Mindestkriterium aus 213F gelesen.
2. Die 13 nichtrelativen Importwurzeln aus 213A uebernommen.
3. Direkte Modul- und Paketinitialisierungsdateien gegen Python 3.14.4 und die venv
   statisch aufgeloest.
4. Existenz, Groesse und SHA-256 der 17 belastbaren Ankerdateien erhoben.
5. NumPy-Initialisierung und deren direkte Dateiverweise statisch gelesen.
6. Einen konservativen rekursiven Textabschluss als Gegenbaseline erhoben.
7. Mindestbefund, Ueberapproximation und offene Auswahlgrenzen getrennt bewertet.

## Messergebnisse und Gegenbaselines

- direkt belegte Python-Dateien: `17/17`, `0` fehlend, `467.482` Bytes;
- Standardbibliotheksanker: `10`, `419.528` Bytes;
- NumPy-Initialisierungsanker: `7`, `47.954` Bytes;
- breit installierte Baumgegenbaseline aus 213E: `4.831` Dateien,
  `134.440.989` Bytes;
- rekursive Textresolver-Gegenbaseline: `465` Dateien, `11.131.140` Bytes;
- im Textresolver unaufgeloeste Namen: `115`;
- neu pauschal freigegebene installierte Dateien: `0`;
- Imports, Tests, Prozesse und Sicherheitsaktionen: jeweils `0`.

| Gegenbaseline | Bewertung |
|---|---|
| nur 13 Namen ohne Paketinitialisierung | zu schmal; Paket-`__init__.py` und direkt bezeichnete NumPy-Dateien fehlen |
| 17 direkte Anker als vollstaendiger Startabschluss | unzulaessig; transitive und bedingte Kanten sind nicht geschlossen |
| 465 Textresolver-Dateien | zu breit und nicht trennscharf; enthaelt optionale, Plattform- und Testzweige |
| alle 4.831 Dateien aus 213E | installierter Baum, aber keine konkrete Startauswahl |
| `.pyc` statt `.py` pauschal voraussetzen | nicht belegt; Cachewahl und Schreibunterdrueckung sind nicht ausgefuehrt |

## Grenzen und nicht gepruefte Annahmen

- **Beobachtet:** 17 direkt begruendete Python-Dateien sind vorhanden und bytegenau
  gebunden. Die breite statische Rekursion ist nicht trennscharf.
- **Technische Interpretation:** Der Mindestbefund schliesst die unmittelbaren
  Wurzeln, aber nicht den transitiven Python-/NumPy-Startkorpus.
- **Hypothese:** Ein enger Abschluss koennte durch einen vorregistrierten Resolver
  entstehen, der bedingte Imports fuer exakt Windows, Python 3.14.4 und die
  vorgesehene NumPy-Konfiguration statisch auswertet. Dies wurde nicht geprueft.
- **Offene Frage:** Welche Zweige aus `numpy/_core/__init__.py`, Sternimporten,
  optionalen Importen und nativen Modulbindungen fuer den vorgesehenen Start
  tatsaechlich erforderlich sind, ist nicht abgeschlossen.
- **Nicht gepruefte Annahme:** Es wird nicht angenommen, dass fehlende literale
  Datenverweise in den 17 Ankern beweisen, dass keine tieferen NumPy-Datendateien
  benoetigt werden.
- Elternverzeichnisse sind durch die Dateipfade ableitbar, aber noch nicht als
  deduplizierte vollstaendige Traverse-Liste gebunden.
- Dynamische Importe, `import *`, optionale Fehlerpfade, Bytecodewahl, Encoding-
  Initialisierung und reale Importreihenfolge wurden nicht vollstaendig aufgeloest.
- Die `numpy.libs`-Verzeichniskante gehoert zusaetzlich zu G2 und bleibt dort offen.
- G2, SID, Profil, ACL, SACL, Tests und Ausfuehrung wurden nicht bearbeitet.

## Konkrete Schlussfolgerung

G1 ist **nicht bestanden**. Es liegt ein bytegenauer Mindestbefund von `17/17`
direkten Python-Dateien mit `467.482` Bytes vor. Weder die 17-Dateien-Menge noch die
465-Dateien-Ueberapproximation erfuellt jedoch das G1-Mindestkriterium einer exakten,
begruendeten Datei- und Elternverzeichnisliste. Der gesamte installierte Baum wird
nicht freigegeben. G0 bleibt vom offenen G1-Umfang abhaengig und Huerde G bleibt
gesperrt.

Es gibt keinen Befund zu Feldwirkung, Memory, Organisation, Topologie, Semantik,
Selbstregulation oder KI. Eine erkennbare Zielabweichung liegt nicht vor.

## Vorschlag fuer den naechsten begrenzten Schritt

Als naechster Schritt ist ein rein statisches G1-Resolver-Vorregistrierungspaket
zweckmaessig. Es soll Syntaxabdeckung, Plattformkonstanten fuer Windows/Python 3.14.4,
Behandlung von `try/except ImportError`, Sternimporten, eingebauten und nativen
Modulen, Paketdaten, Elternverzeichnissen und Stopplinien exakt festlegen. Noch keine
Implementierung, kein Import, kein Test, kein Prozessstart und keine G2-Bearbeitung.
