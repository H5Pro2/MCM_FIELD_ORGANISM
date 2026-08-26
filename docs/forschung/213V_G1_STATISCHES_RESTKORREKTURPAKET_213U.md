# 213V - G1 statisches Restkorrekturpaket zu 213U

## Einordnung

213V ist ein statisches Entwicklungspaket, kein Forschungslauf und keine
Lauffreigabe. Es korrigiert ausschliesslich die drei in 213U benannten
Restbefunde in `tools/static_binary_evidence.py`. Das Werkzeug wurde weder
importiert noch kompiliert, getestet oder ausgefuehrt.

## Forschungsfrage und Auftrag

Koennen die in 213U getrennt ausgewiesenen Restluecken bei Tabellenzaehlern,
PE32+/AMD64-Invarianten und Fehlerkontext eng am vorhandenen Werkzeug
geschlossen werden, ohne einen Zielbinary- oder Resolverlauf vorzunehmen?

## Tatsaechlich verwendete Quellen

- aktueller freigegebener Uebergabe-Eingang;
- `docs/forschung/213U_G1_ERNEUTE_UNABHAENGIGE_STATISCHE_ABNAHME_213T.md`;
- `tools/static_binary_evidence.py`.

Keine Webquelle und keine externe MCM-Quelle wurde verwendet.

## Verwendete Dateien und Schnittstellen

Geaendert wurde ausschliesslich:

- `tools/static_binary_evidence.py`.

Neu erstellt wurde ausschliesslich:

- `docs/forschung/213V_G1_STATISCHES_RESTKORREKTURPAKET_213U.md`.

Zur statischen Bearbeitung und Kontrolle wurden Textlesen, Textsuche,
`apply_patch`, Dateigroesse, SHA-256 und `git diff --check` verwendet. Es wurde
keine Python-, Loader-, Import-, Kompilierungs-, Test-, Prozess- oder
Zielbinary-Schnittstelle aufgerufen.

## Durchgefuehrte Schritte

1. Die Tabellenreihenfolge und den separaten Frozen-Override erneut gegen den
   fehlerhaften Summenbereich aus 213U abgeglichen.
2. Die vorhandenen PE32+/AMD64-Headerpruefungen um feste ImageBase-,
   FileAlignment- und SectionAlignment-Invarianten ergaenzt.
3. Einen expliziten Fehlerkontext eingefuehrt und entlang der bereits
   erfolgreich verifizierten Bindungsschritte fortgeschrieben.
4. Den fruehen Fehler beim Parsen des unabhaengigen CLI-Sollankers an denselben
   atomaren Fehlerausgabepfad angeschlossen.
5. Die veraenderten Quellbereiche statisch gelesen und nach gesperrten
   Schnittstellennamen durchsucht.

## Umgesetzte statische Korrekturen

### 1. Getrennte Tabellenzaehler

Der Berichtszaehler `frozen_entries` summiert nur noch die drei festen
Frozen-Tabellen Bootstrap, Stdlib und Test. Der separate Override und die
Alias-Tabelle werden nicht mehr eingemischt, sondern ueber die eigenstaendigen
Felder `frozen_override_entries` und `frozen_alias_entries` ausgewiesen.

Damit bleiben Builtin, feste Frozen-Tabellen, Laufzeit-Override und Aliase als
unterschiedliche Evidenzklassen kontrollierbar.

### 2. PE32+/AMD64-Alignment- und ImageBase-Invarianten

Vor der Verarbeitung von Sections oder Data Directories verlangt der Parser
nun zusaetzlich:

- eine von null verschiedene und auf 64 KiB ausgerichtete `ImageBase`;
- ein potenz-von-zwei `FileAlignment` im festen Bereich 512 bis 65.536 Bytes;
- `SectionAlignment >= FileAlignment`;
- bei `SectionAlignment < 4.096` die Gleichheit von `SectionAlignment` und
  `FileAlignment`.

Die vorhandenen Pruefungen auf potenz-von-zwei, Teilbarkeit von
`SizeOfHeaders` und `SizeOfImage`, Section-Grenzen und Headerueberlappung
bleiben bestehen.

### 3. Schrittweise wahrheitsgemaesser Fehlerkontext

`ErrorContext` beginnt mit Startzeit und gegebenenfalls einer gueltig
geparsten erwarteten Steuerbindung. Erst nach erfolgreicher Bytepruefung werden
folgende Werte eingetragen:

- verifizierte Steuerbindung;
- verifizierte Werkzeugbindung;
- verifizierte Vertragsbindung;
- jede einzeln verifizierte Zielbindung.

Die Fehlerausgabe verwendet ausschliesslich diesen erreichten Stand. Noch
nicht verifizierte Werte bleiben `null` beziehungsweise leer. Eine ungueltige
CLI-Sollbindung wird ebenfalls in das vorregistrierte Fehlerformat ueberfuehrt,
sofern der vorhandene atomare Ausgabepfad einen sicheren leeren Zielordner
anlegen kann.

Die fruehere ersatzweise Neuberechnung einer Werkzeugbindung im Fehlerwriter
wurde entfernt, weil sie keinen bereits erreichten Verifikationsschritt
belegte.

## Messergebnisse und Gegenbaselines

### Beobachtetes statisches Ergebnis

- Die drei Zaehler greifen auf disjunkte Datenklassen zu.
- Die vier in 213U fehlenden Alignmentbeziehungen stehen vor der weiteren
  PE-Strukturverarbeitung.
- Der Fehlerkontext wird unmittelbar nach jedem erfolgreichen Bindungsschritt
  fortgeschrieben.
- Der fruehe CLI-Ankerfehler ruft den Fehlerwriter auf.
- Die statische Suche ergab keine Treffer fuer `subprocess`, `ctypes`,
  `importlib`, NumPy, `exec` oder `eval`.

### Gegenbaselines

- Aliase oder Overrides werden nicht als feste Frozen-Eintraege gezaehlt.
- Potenz-von-zwei allein gilt weiterhin nicht als ausreichende
  Alignmentvalidierung.
- Erwartete Bindungen gelten nicht als verifiziert.
- Eine aus der laufenden Werkzeugdatei neu berechnete Bindung gilt im
  Fehlerfall nicht rueckwirkend als verifizierter Kontext.
- Nicht erreichte Verifikationsschritte werden nicht mit erwarteten Daten
  aufgefuellt.

## Grenzen und nicht gepruefte Annahmen

- Die Syntax und Laufzeitwirkung der Korrektur wurden nicht geprueft.
- Es wurde keine Steuerdatei erzeugt oder gelesen.
- Keine der 54 Zielbinaries wurde geoeffnet oder ausgewertet.
- Der atomare Fehlerausgabepfad wurde nicht ausgefuehrt.
- Reale Tabellen-, Export- und Relocation-Ergebnisse bleiben unbekannt.
- G2, DLL-Abhaengigkeiten, Sicherheitszustand und Huerde G wurden nicht
  bearbeitet.

## Konkrete Schlussfolgerung

Die drei in 213U benannten Restbefunde sind im Quelltext eng und getrennt
adressiert. Dies ist nur ein statisches Implementierungsergebnis. Daraus folgt
weder syntaktische noch funktionale Lauffaehigkeit, solange keine unabhaengige
statische Abnahme und anschliessende ausdrueckliche Lauffreigabe vorliegen.

G1 bleibt nicht bestanden, G0 bleibt abhaengig, G2 und Huerde G bleiben
gesperrt. Eine erkennbare Zielabweichung liegt nicht vor.

## Vorschlag fuer den naechsten begrenzten Schritt

Als naechstes sollte genau eine unabhaengige statische Abnahme von 213V gegen
die drei Befunde aus 213U erfolgen. Sie soll insbesondere die disjunkten
Zaehlerbereiche, die Reihenfolge und Vollstaendigkeit der PE-Invarianten sowie
den tatsaechlich erreichbaren Fehlerkontext jedes Bindungsschritts pruefen.

Noch kein Import, keine Kompilierung, kein Test, kein Werkzeuglauf, keine
Steuerdateierzeugung, keine Manifesterzeugung, kein Resolverlauf, keine
G2-Bearbeitung und keine Oeffnung von Huerde G.
