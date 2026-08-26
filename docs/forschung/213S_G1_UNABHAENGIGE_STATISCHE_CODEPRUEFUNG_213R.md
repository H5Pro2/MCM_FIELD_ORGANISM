# 213S - G1 unabhaengige statische Codepruefung von 213R

## Einordnung

213S ist ein statisches Pruef- und Befundpaket, kein Forschungslauf, kein
Werkzeuglauf und keine Codekorrektur. Geprueft wurde die Implementierung aus
213R gegen den Vertrag aus 213Q. Das Werkzeug wurde nicht importiert,
kompiliert, getestet oder ausgefuehrt. Keine Zielbinary wurde gelesen.

## Forschungsfrage und Auftrag

Entspricht `tools/static_binary_evidence.py` statisch dem Vertrag aus 213Q,
insbesondere bei Exportfeldindizes, RVA-Grenzen, Relocation-Normalisierung,
Tabellenlayouts, Aliasvalidierung, Atomaritaet, Stopplinien und dem expliziten
Umfang von 53 `.pyd`-Dateien plus `python314.dll`?

## Tatsaechlich verwendete Quellen

- aktueller freigegebener Uebergabe-Eingang;
- `tools/static_binary_evidence.py`;
- `docs/forschung/213Q_G1_STATISCHE_AUSWERTUNGSWERKZEUG_VORREGISTRIERUNG.md`;
- `docs/forschung/213R_G1_STATISCHE_AUSWERTUNGSWERKZEUG_IMPLEMENTIERUNG.md`;
- `docs/forschung/213P_G1_STATISCHE_MANIFEST_VORREGISTRIERUNG_UND_BINDUNG.md`.

Keine Webquelle und keine externe MCM-Quelle wurde verwendet.

## Verwendete Dateien und Schnittstellen

Die Dateien wurden ausschließlich als Text und Rohbytes gelesen. Verwendet
wurden PowerShell-Textausgabe, Textsuche, Dateigroesse, SHA-256 und
`git diff --check`. Es gab keinen Python-, Import-, Kompilierungs-, Test-,
Werkzeug-, Resolver- oder Zielprozessstart. Es wurde nur dieses Dokument neu
erstellt.

Gepruefte Implementierungsbindung:

- `tools/static_binary_evidence.py`;
- 35.080 Bytes;
- SHA-256
  `2B47B0C4045F288B4CE27228B086A73A270D698122A9664EB1052D14B34ECAF2`.

## Durchgefuehrte statische Pruefschritte

1. PE-Header- und Exportfeldindizes gegen die in 213Q festgelegten Strukturen
   abgeglichen.
2. Datei- und RVA-Grenzpruefungen entlang aller Leserpfade verfolgt.
3. Datenzeiger- und Tabellenzeiger-Normalisierung gegen ImageBase und
   `DIR64`-Relocations verfolgt.
4. `_inittab`, `_frozen` und `_module_alias` sowie Terminatoren und Limits
   abgeglichen.
5. Aliaszyklus-, Aliasziel- und Namenskonfliktpruefung verfolgt.
6. Staging- und Verzeichnisumbenennung fuer Erfolgs- und Fehlerausgaben
   betrachtet.
7. Steuerdatei, Bindungsrollen und Umfangszaehler verfolgt.
8. Ausgabeobjekte gegen die in 213Q geforderten Pflichtfelder abgeglichen.
9. Gesperrte Imports und APIs erneut statisch gesucht.

## Messergebnisse und Gegenbaselines

### Beobachtete passende Punkte

- Die `IMAGE_EXPORT_DIRECTORY`-Indizes fuer Base, Funktionszahl, Namenszahl,
  Funktions-RVA, Namens-RVA und Ordinal-RVA sind statisch passend zugeordnet.
- PE32+/AMD64, Exportverzeichnis und Relocationverzeichnis werden getrennt und
  fail-closed behandelt.
- Nichtnull Tabellen- und Eintragszeiger verlangen `DIR64` und werden gegen
  ImageBase sowie `SizeOfImage` normalisiert.
- Die Layouts 16 Byte fuer `_inittab`, 24 Byte fuer `_frozen` und 16 Byte fuer
  `_module_alias` entsprechen 213Q.
- Paketflag, Terminatoren, Eintragslimit, Aliaszyklen, Aliasziele und
  Namenskonflikte werden statisch geprueft.
- Die Erfolgsdateien werden in einem Geschwister-Stagingordner vorbereitet und
  mit einer abschliessenden Verzeichnisumbenennung veroeffentlicht.
- Es gibt keine Projekt-, NumPy-, Binary-Lade-, Prozess-, `ctypes`-,
  `subprocess`-, `importlib`-, `exec`- oder `eval`-Schnittstelle.
- Der Umfangszaehler verlangt genau eine Rolle `cpython-binary` und genau 53
  Rollen `native-candidate`. Damit ist die Anzahl explizit `54` Zielbinaries.

### Gegenbaselines

- Eine reine Importsuche wurde nicht als vollstaendige Codepruefung behandelt.
- Der Zaehler `1 + 53` wurde nicht als Identitaetsnachweis fuer die in 213P
  gebundenen 54 Dateien behandelt.
- Fail-closed Verhalten wurde nicht automatisch mit vollstaendiger
  Vertragserfuellung gleichgesetzt.
- Dokumentierte Ausgabeabsicht wurde gegen die tatsaechlich aufgebauten
  JSON-Objekte geprueft.

## Abnahmehemmende Befunde

### Befund 1 - Steuerdatei ist eine ungebundene Vertrauenswurzel

Schwere: hoch.

In `tools/static_binary_evidence.py:722-752` liest das Werkzeug die erwarteten
Werkzeug-, Vertrags- und Zielbindungen ausschließlich aus der per CLI
uebergebenen Steuerdatei. Die Steuerdatei selbst besitzt weder eine
vorregistrierte Pfad-/Groessen-/SHA-256-Bindung noch feste Sollwerte fuer
213Q, `python314.dll` oder die 53 konkreten `.pyd`-Dateien. Der Code prueft nur,
ob die aktuell gelesenen Dateien zu den Behauptungen derselben Steuerdatei
passen.

Beobachtete Folge: Eine beliebige andere Datei kann in einer neu formulierten
Steuerdatei als `cpython-binary` oder `native-candidate` selbst autorisiert
werden, solange die Rollenzaehler `1` und `53` stimmen. Auch
`contract_binding` kann auf ein anderes Dokument zeigen. Damit erzwingt die
Implementierung den in 213Q und 213P fest gebundenen 54-Dateien-Umfang nur
numerisch, nicht identitaetsbezogen.

Erforderliche Korrekturgrenze: Vor einem Lauf muss eine außerhalb ihrer selbst
autorisierte, bytegebundene Steuerdatei existieren und das Werkzeug muss deren
Sollbindung ueber einen unabhaengigen, vorregistrierten Vertrauensanker
erhalten. Alternativ muessen die freigegebenen Sollbindungen unveraenderlich in
einem separat geprueften Bindungsartefakt liegen. Eine Steuerdatei darf ihre
eigene Autoritaet nicht allein begruenden.

### Befund 2 - Header-RVA kann `SizeOfHeaders` ueberschreiten

Schwere: hoch.

In `tools/static_binary_evidence.py:299-302` wird jede RVA kleiner als
`SizeOfHeaders` direkt als Dateioffset akzeptiert. Geprueft wird nur, ob
`rva + size` innerhalb der Gesamtdatei liegt. Es fehlt die Bedingung
`rva + size <= SizeOfHeaders`.

Beobachtete Folge: Eine Struktur kann im Header beginnen und ueber die
deklarierte Headergrenze hinausreichen, ohne einer einzelnen Section zugeordnet
zu sein. Das widerspricht der 213Q-Regel, dass jeder verwendete Bereich
vollstaendig und eindeutig in genau einem belegten Bereich liegen muss.

Zusaetzlich werden `SizeOfHeaders` und `SizeOfImage` beim Einlesen nicht auf
plausible Beziehung zur Datei, zur Section-Tabelle und zu den Section-RVAs
geprueft. Der bestehende Dateibounds-Check ersetzt diese PE-Strukturinvarianten
nicht.

Erforderliche Korrekturgrenze: Headerbereiche muessen vollstaendig innerhalb
`[0, SizeOfHeaders)` liegen. `SizeOfHeaders`, Section-Tabelle,
`SizeOfImage` und Section-Grenzen muessen vor RVA-Nutzung konsistent validiert
werden.

### Befund 3 - 213Q-Pflichtfelder fehlen in Evidenzausgaben

Schwere: mittel bis hoch.

213Q verlangt fuer die PE-Evidenz eine Bindung des Export-Directory und fuer
CPython-Datensymbole unter anderem Export-RVA, Zeigerslot und expliziten
Relocation-Nachweis. In `tools/static_binary_evidence.py:484-502` werden bei
Native-Dateien Bindung, Exporte, Init-Kandidaten und Maschine ausgegeben, aber
keine Export-Directory-RVA/-Groesse/-Dateioffset-Bindung. In den
Tabellenausgaben werden Slot- und Ziel-RVAs dokumentiert, der verwendete
Relocation-Typ und dessen Fundort jedoch nicht als eigener Nachweisdatensatz.

Die Fehlerausgabe in `tools/static_binary_evidence.py:794-802` enthaelt
ausserdem weder `tool_binding`, `contract_binding`, `input_bindings` noch
`started_utc`/`finished_utc`. 213Q fordert diese gemeinsamen Pflichtfelder fuer
jede JSON-Ausgabe. Bei einem fruehen Bindungsfehler koennen einzelne Werte
unverifiziert sein; dann muessen erwartete und bereits verifizierte Werte
getrennt oder explizit als nicht verfuegbar dokumentiert werden, statt die
Felder wegzulassen.

Erforderliche Korrekturgrenze: Die fehlenden Strukturnachweise und gemeinsamen
Fehlerfelder muessen ohne Bedeutungsableitung ergaenzt werden. Das
Ausgabeformat bleibt Evidenz, nicht Manifest.

## Weitere statische Grenzen

- Die technische Syntax wurde wegen der Auftragssperre nicht kompiliert oder
  geparst.
- Kein reales PE-Layout wurde gegen den Parser gehalten.
- Ob `python314.dll` alle erwarteten Datensymbole exportiert, bleibt offen.
- Die Forderung nach exakt einem `PyInit_*`-Export je `.pyd` wurde nicht an
  realen Kandidaten geprueft.
- Dateisystematomaritaet der Verzeichnisumbenennung wurde nicht technisch
  erprobt.
- G2, DLL-Abhaengigkeiten, `numpy.libs`, Sicherheitszustand und Huerde G wurden
  nicht bearbeitet.

## Konkrete Schlussfolgerung

Die Kernrichtung von 213R ist statisch nachvollziehbar: Parserfelder,
Relocation-Grundmodell, Tabellenlayouts, Aliaspruefung und numerischer Umfang
von 54 Zielbinaries sind vorhanden. Die drei beschriebenen Vertragsluecken
verhindern jedoch eine statische Abnahme fuer einen spaeteren Werkzeuglauf.

Die Implementierung ist damit noch nicht lauffreigabefaehig. Dies ist kein
Nachweis eines Laufzeitfehlers, weil keinerlei Ausfuehrung stattfand. G1 bleibt
nicht bestanden, G0 bleibt abhaengig und Huerde G bleibt gesperrt. Eine
erkennbare Zielabweichung liegt nicht vor.

## Vorschlag fuer den naechsten begrenzten Forschungs- und Entwicklungsschritt

Als naechstes sollte genau ein statisches Korrekturpaket fuer 213R erstellt
werden. Es soll ausschließlich:

1. einen unabhaengig bytegebundenen Vertrauensanker fuer die Steuerdatei und
   die konkrete 54-Dateien-Identitaet einfuehren;
2. Header-RVA- und PE-Header-/Image-Invarianten vervollstaendigen;
3. Export-Directory-, Relocation- und Fehlerausgabe-Pflichtfelder aus 213Q
   ergaenzen;
4. die geaenderte Werkzeugdatei erneut bytegenau dokumentieren.

Noch kein Import, keine Kompilierung, kein Test, kein Werkzeuglauf, keine
Manifesterzeugung, kein Resolverlauf und keine G2-Bearbeitung.
