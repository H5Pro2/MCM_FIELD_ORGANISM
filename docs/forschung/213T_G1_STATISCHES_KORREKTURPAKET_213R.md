# 213T - G1 statisches Korrekturpaket fuer 213R

## Einordnung

213T ist genau ein statisches Korrektur- und Bindungspaket fuer die drei in
213S benannten Vertragsluecken. Es ist kein Forschungslauf, kein Test und kein
Werkzeuglauf. Es wurden keine Zielbinaries gelesen und keine Nachweis-JSONs,
Manifeste oder Resolverergebnisse erzeugt.

## Forschungsfrage und Auftrag

Koennen die drei abnahmehemmenden Befunde aus 213S eng begrenzt korrigiert
werden, ohne den Forschungsumfang zu erweitern?

Konkret zu korrigieren waren:

1. unabhaengiger Bytebindungsanker fuer Steuerdatei und konkrete
   `1 + 53 = 54` Zielbinaries;
2. Header-RVA-, Section-Table-, `SizeOfHeaders`- und `SizeOfImage`-Invarianten;
3. Export-Directory-, Relocation- und Fehlerausgabe-Pflichtfelder.

## Tatsaechlich verwendete Quellen

- aktueller freigegebener Uebergabe-Eingang;
- `docs/forschung/213S_G1_UNABHAENGIGE_STATISCHE_CODEPRUEFUNG_213R.md`;
- `docs/forschung/213Q_G1_STATISCHE_AUSWERTUNGSWERKZEUG_VORREGISTRIERUNG.md`;
- `docs/forschung/213P_G1_STATISCHE_MANIFEST_VORREGISTRIERUNG_UND_BINDUNG.md`;
- `tools/static_binary_evidence.py` in der durch 213R gebundenen Fassung.

Keine Webquelle und keine externe MCM-Quelle wurde verwendet.

## Verwendete Dateien und Schnittstellen

Geaendert:

- `tools/static_binary_evidence.py`.

Neu erstellt:

- dieses Dokument.

Die Pruefung erfolgte nur durch Textsuche, Textlesen, Dateigroesse, SHA-256 und
`git diff --check`. Das Werkzeug wurde nicht importiert, kompiliert, getestet
oder ausgefuehrt. Keine weitere Projektdatei wurde veraendert.

## Durchgefuehrte Korrekturen

### 1. Unabhaengiger Steuerdateianker und 54-Dateien-Identitaet

Die Kommandozeile verlangt nun neben `--control` zwingend:

- `--control-size`;
- `--control-sha256`.

Diese Sollwerte werden vor dem Lesen des Steuerinhalts als eigener
`Binding`-Datensatz geprueft. Erst wenn kanonischer Pfad, regulaerer Dateityp,
Bytegroesse und SHA-256 der Steuerdatei passen, darf deren Inhalt die
Werkzeug-, Vertrags- und Zielbindungen liefern.

Die unabhaengig freizugebende Steuerdateibindung ist damit der externe
Vertrauensanker. Ihre gebundenen Bytes enthalten anschließend die konkrete
Liste der Zielbindungen. Der bereits vorhandene Rollenabschluss bleibt
zusaetzlich bestehen:

- genau `1` Eintrag `cpython-binary`;
- genau `53` Eintraege `native-candidate`;
- keine andere Rolle;
- keine doppelten oder fallkollidierenden Pfade.

Damit reicht eine frei formulierte, nicht passend gebundene Steuerdatei nicht
mehr aus, um andere 54 Dateien selbst zu autorisieren. Die konkrete
Steuerdatei wurde in diesem Paket noch nicht erzeugt; sie muss spaeter separat
statisch erstellt und vor einem Lauf bytegenau freigegeben werden.

### 2. PE-Header- und RVA-Invarianten

Ergaenzt wurden harte Stopps fuer:

- `SizeOfHeaders` kleiner als das Ende der Section-Tabelle;
- `SizeOfHeaders` groesser als Datei oder `SizeOfImage`;
- nicht potenz-von-zwei ausgerichtete Section-/File-Alignments;
- nicht an FileAlignment ausgerichtete `SizeOfHeaders` und Raw-Offsets;
- nicht an SectionAlignment ausgerichtete `SizeOfImage` und Section-RVAs;
- Raw-Sectionbereiche, die den Headerbereich ueberlappen;
- Sections ausserhalb `SizeOfImage`;
- einen Header-RVA-Lesebereich, dessen Ende `SizeOfHeaders` ueberschreitet.

Die bisherige Datei- und Section-Ueberlappungspruefung bleibt bestehen. Eine
RVA kann damit nicht mehr im Header beginnen und ausserhalb seines deklarierten
Bereichs weiterlesen.

### 3. Pflichtfelder fuer Evidenz und Fehler

Die Native-Evidenz enthaelt nun je Datei die Export-Directory-Bindung mit:

- RVA;
- Bytegroesse;
- Dateioffset.

Relocation-Datensaetze enthalten nun:

- Typ;
- RVA des Relocation-Ziels;
- Page-RVA des Blocks;
- Dateioffset des Relocation-Eintrags.

Diese Datensaetze werden fuer exportierte Tabellenzeigerslots sowie fuer
Name-, Initfunktion-, Code- und Aliaszeiger in den CPython-Tabellen ausgegeben.
Die Tabellenobjekte enthalten `export_rva` ausdruecklich neben `slot_rva`.

Die Fehlerausgabe enthaelt nun auch bei `complete: false` die gemeinsamen
Felder:

- `tool_binding` oder explizit `null`, wenn nicht erhebbar;
- `contract_binding: null`, solange der Fehlerpfad keine verifizierte Bindung
  uebergeben kann;
- erwartete und verifizierte Steuerbindung getrennt;
- `input_bindings`, gegebenenfalls als leeres Array;
- `started_utc` und `finished_utc`;
- Plattform, Fehler und Stopps.

Nicht verfuegbare Bindungen werden damit offen als `null` beziehungsweise leer
dokumentiert und nicht erfunden.

## Statische Kontrollmessungen

Beobachtet:

- die CLI besitzt genau die drei Steuerparameter `--control`,
  `--control-size` und `--control-sha256`;
- die Steuerbindung wird vor `_load_control` verifiziert;
- die Rollenpruefung verlangt weiterhin `1 + 53 = 54` Zielbinaries;
- die neue Headergrenze prueft das Ende jedes Headerlesebereichs gegen
  `SizeOfHeaders`;
- Export-Directory- und Relocation-Felder sind in den aufgebauten
  Evidenzobjekten vorhanden;
- Fehlerobjekte enthalten die gemeinsamen Pflichtfeldnamen;
- die Importsuche zeigt weiterhin ausschließlich Python-Standardbibliothek;
- die statische Suche fand keine Binary-Lade-, Projekt-, NumPy-, Prozess-,
  `ctypes`-, `subprocess`-, `importlib`-, `exec`- oder `eval`-Schnittstelle;
- `git diff --check` ist fuer die geaenderten Dateien sauber.

Diese Messungen sind reine Text- und Bytebefunde, kein Syntax- oder
Funktionsnachweis.

## Gegenbaselines

- Ein Rollenzaehler ohne vorgelagerte Steuerdateibindung wird nicht mehr als
  Identitaetsabschluss akzeptiert.
- Ein Dateibounds-Check ohne `SizeOfHeaders`-Endgrenze wird nicht mehr als
  gueltige Header-RVA-Pruefung behandelt.
- Implizite Relocation-Nutzung ohne ausgegebenen Fundort gilt nicht mehr als
  vollstaendiger Evidenzdatensatz.
- Fehlende Fehlerkontextfelder werden nicht durch angenommene Werte ersetzt.

## Grenzen und nicht gepruefte Annahmen

- Die korrigierte Implementierung wurde nicht importiert, kompiliert, getestet
  oder ausgefuehrt.
- Eine konkrete Steuerdatei und deren unabhaengige Sollbindung existieren noch
  nicht.
- Die Identitaet der 54 spaeteren Ziele ist erst dann technisch erzwungen,
  wenn genau diese separat gepruefte Steuerdatei samt Sollgroesse und Sollhash
  an den Werkzeugaufruf gebunden wird.
- Reale PE-Strukturen, Exporte, Relocations und Tabellen wurden nicht gelesen.
- Ob alle statischen Invarianten mit den gebundenen CPython-/NumPy-Binaries
  vereinbar sind, ist offen.
- Fehlerkontext dokumentiert nicht verifizierbare Bindungen bewusst als
  `null`; er ist kein Erfolgsnachweis.
- G2, DLL-Abhaengigkeiten, `numpy.libs`, Sicherheitszustand und Huerde G wurden
  nicht bearbeitet.

## Konkrete Schlussfolgerung

Die drei in 213S benannten Vertragsluecken wurden im statischen Quelltext eng
begrenzt adressiert. Der externe Steuerdateianker ist nun technisch
verpflichtend, die PE-Headergrenzen sind verschaerft und die fehlenden
Evidenzfelder werden aufgebaut. Daraus folgt noch keine technische
Funktionsfaehigkeit oder Lauffreigabe.

G1 bleibt nicht bestanden, G0 bleibt abhaengig und Huerde G bleibt gesperrt.
Eine erkennbare Zielabweichung liegt nicht vor.

## Vorschlag fuer den naechsten begrenzten Schritt

Als naechstes sollte ausschließlich eine erneute unabhaengige statische
Abnahme der korrigierten Werkzeugdatei gegen 213S und 213Q erfolgen. Dabei sind
der externe Steueranker, alle neuen PE-Invarianten und die JSON-Pflichtfelder
zeilenbezogen zu kontrollieren. Noch kein Import, keine Kompilierung, kein Test,
kein Werkzeuglauf, keine Steuerdateierzeugung, keine Manifesterzeugung, kein
Resolverlauf und keine G2-Bearbeitung.
