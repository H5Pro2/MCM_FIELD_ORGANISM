# 213U - G1 erneute unabhaengige statische Abnahme von 213T

## Einordnung

213U ist ein statisches Pruef- und Befundpaket, kein Forschungslauf, keine
Codekorrektur und keine Lauffreigabe. Geprueft wurde die durch 213T korrigierte
Werkzeugdatei gegen 213S und 213Q. Es erfolgten kein Import, keine
Kompilierung, kein Test und kein Werkzeuglauf.

## Forschungsfrage und Auftrag

Sind der externe Steueranker, die neuen PE-Invarianten sowie die Erfolgs- und
Fehlerausgaben in `tools/static_binary_evidence.py` nach 213T statisch
vollstaendig und widerspruchsfrei umgesetzt?

## Tatsaechlich verwendete Quellen

- aktueller freigegebener Uebergabe-Eingang;
- `tools/static_binary_evidence.py`;
- `docs/forschung/213T_G1_STATISCHES_KORREKTURPAKET_213R.md`;
- `docs/forschung/213S_G1_UNABHAENGIGE_STATISCHE_CODEPRUEFUNG_213R.md`;
- `docs/forschung/213Q_G1_STATISCHE_AUSWERTUNGSWERKZEUG_VORREGISTRIERUNG.md`.

Keine Webquelle und keine externe MCM-Quelle wurde verwendet.

## Verwendete Dateien und Schnittstellen

Die Dateien wurden ausschließlich als Text und Rohbytes gelesen. Verwendet
wurden PowerShell-Textausgabe, Textsuche, Dateigroesse, SHA-256 und
`git diff --check`. Nur dieses Dokument wurde neu erstellt.

Gepruefte Werkzeugbindung:

- `tools/static_binary_evidence.py`;
- 40.760 Bytes;
- SHA-256
  `FC18A144CF5CC1B3A123DA4ECDDE941DE764E56ADD2488D2ABE80AF234BFE82E`.

## Durchgefuehrte statische Pruefschritte

1. Reihenfolge von unabhaengiger Steuerbindung, Steuerdateilesung und
   54-Dateien-Rollenabschluss verfolgt.
2. `SizeOfHeaders`, Section-Tabelle, Section-RVAs, Raw-Bereiche,
   `SizeOfImage`, FileAlignment und SectionAlignment geprueft.
3. Export-Directory- und Relocation-Nachweisfelder bis in die aufgebauten
   JSON-Objekte verfolgt.
4. Erfolgs- und Fehlerpfade gegen die gemeinsamen Pflichtfelder aus 213Q
   abgeglichen.
5. Berichtssummen gegen die konkrete Struktur der CPython-Tabellenliste und
   des separaten Overrides abgeglichen.
6. Gesperrte Imports und APIs erneut statisch gesucht.

## Messergebnisse und Gegenbaselines

### Bestaetigte Korrekturen aus 213T

- `--control-size` und `--control-sha256` sind verpflichtend.
- `_verify_binding(expected_control)` liegt vor `_load_control`.
- Erst der Inhalt der extern bytegebundenen Steuerdatei liefert Werkzeug-,
  Vertrags- und Zielbindungen.
- Der Rollenabschluss verlangt weiterhin exakt eine CPython-Binary und 53
  Native-Kandidaten, also 54 Zielbinaries.
- Ein Header-RVA-Bereich darf `SizeOfHeaders` nicht mehr ueberschreiten.
- Die Section-Tabelle muss vollstaendig in `SizeOfHeaders` liegen.
- Sections werden gegen Raw-Headerueberlappung und `SizeOfImage` geprueft.
- Export-Directory-RVA, -Groesse und -Dateioffset werden ausgegeben.
- Relocation-Typ, Ziel-RVA, Page-RVA und Eintragsoffset werden fuer Tabellen-
  und Eintragszeiger ausgegeben.
- Fehlerobjekte besitzen die geforderten Feldnamen fuer Bindungen, Zeit,
  Plattform, Fehler und Stopps.
- Die statische Suche fand weiterhin keine gesperrte Lade-, Prozess-, Projekt-
  oder NumPy-Schnittstelle.

### Gegenbaselines

- Vorhandene Feldnamen wurden nicht automatisch als korrekter Feldinhalt
  gewertet.
- Eine Berichtssumme wurde nicht ohne Abgleich ihrer konkreten Tabellenindizes
  akzeptiert.
- Potenz-von-zwei-Pruefung allein wurde nicht als vollstaendige PE-Alignment-
  Validierung behandelt.
- Ein `null`-Feld wurde nicht als wahrheitsgemaesser Nachweis angesehen, wenn
  die zugehoerige Bindung im vorherigen Schritt bereits erfolgreich geprueft
  worden sein kann.

## Abnahmehemmende Restbefunde

### Befund 1 - Frozen-Berichtszaehler vermischt Alias-Eintraege und Override

Schwere: hoch.

Die Tabellenliste wird in `tools/static_binary_evidence.py:746-752` in dieser
Reihenfolge aufgebaut: Builtin, Frozen-Bootstrap, Frozen-Stdlib, Frozen-Test,
Aliases. Der Override liegt separat in `table_result["override"]`.

Der Bericht berechnet in `tools/static_binary_evidence.py:883-887`
`frozen_entries` jedoch ueber `table_result["tables"][1:]`. Dadurch werden
alle Alias-Eintraege als Frozen-Eintraege mitgezaehlt, waehrend Eintraege des
separaten Overrides nicht eingehen.

Folge: Ein spaeterer erfolgreicher Bericht koennte eine sachlich falsche
Frozen-Gesamtzahl ausgeben, obwohl die einzelnen Evidenzobjekte korrekt
vorliegen. Die Zaehler sind damit nicht als kontrollierbare Zusammenfassung
geeignet.

Erforderliche Korrektur: Frozen-Zaehler ausschließlich aus Bootstrap, Stdlib
und Test bilden und Override separat zaehlen. Alias-Eintraege erhalten einen
eigenen Zaehler. Keine Zusammenfuehrung der Klassen.

### Befund 2 - PE-Alignment- und ImageBase-Invarianten bleiben unvollstaendig

Schwere: mittel bis hoch.

`tools/static_binary_evidence.py:248-262` liest ImageBase, SectionAlignment und
FileAlignment. Geprueft werden Nichtnullwerte, Potenz-von-zwei sowie die
Teilbarkeit von `SizeOfHeaders` und `SizeOfImage`.

Nicht geprueft werden jedoch:

- Nichtnullwert und 64-KiB-Ausrichtung der ImageBase fuer PE32+/AMD64;
- der zulaessige Wertebereich von FileAlignment;
- die Beziehung `SectionAlignment >= FileAlignment` im normalen PE-Fall;
- die PE-Sonderregel, dass bei SectionAlignment unterhalb der Seitengroesse
  FileAlignment demselben Wert entsprechen muss.

Folge: Strukturell unzulaessige Alignmentkombinationen koennen die vorhandenen
Teilpruefungen passieren. Das widerspricht der in 213Q vorregistrierten
Validierung von ImageBase, SectionAlignment und FileAlignment.

Erforderliche Korrektur: Die festen PE32+/AMD64-Regeln explizit und fail-closed
validieren, bevor Sections oder Data Directories verarbeitet werden.

### Befund 3 - Fehlerkontext verliert bereits erreichten Verifikationsstand

Schwere: mittel.

`tools/static_binary_evidence.py:837-864` kann die Steuerdatei, das Werkzeug,
den Vertrag und mehrere Zielbindungen bereits erfolgreich geprueft haben,
bevor spaeter ein Parserfehler entsteht. Der Fehlerpfad
`tools/static_binary_evidence.py:902-927` erhaelt jedoch nur die erwartete
Steuerbindung und den Startzeitpunkt. Er schreibt deshalb ausnahmslos:

- `control_binding_verified: null`;
- `contract_binding: null`;
- `input_bindings: []`.

Folge: Bei einem spaeten Fehler wird ein tatsaechlich bereits erreichter und
fuer die Fehlerreproduktion relevanter Verifikationsstand verworfen. Das Feld
ist zwar vorhanden, sein Inhalt bildet den Ablauf aber nicht wahrheitsgemaess
ab. Umgekehrt erzeugt ein Fehler bereits beim Parsen der unabhaengigen
CLI-Sollbindung in `tools/static_binary_evidence.py:938-950` ueberhaupt keine
JSON-Fehlerdatei, sondern nur Standardfehlerausgabe.

Erforderliche Korrektur: Einen expliziten, schrittweise gefuellten
Fehlerkontext fuehren. Er darf nur bereits verifizierte Bindungen enthalten und
muss fruehe noch nicht verifizierbare Werte als `null` oder leer kennzeichnen.
Auch ein formal ungueltiger CLI-Sollanker muss, soweit ein sicherer leerer
Ausgabeordner angegeben ist, in das vorregistrierte Fehlerformat ueberfuehrt
werden.

## Grenzen und nicht gepruefte Annahmen

- Die Werkzeugsyntax und jeder Laufzeitpfad blieben ungetestet.
- Es wurde keine Steuerdatei erzeugt oder gelesen.
- Keine der 54 Zielbinaries wurde geoeffnet oder ausgewertet.
- Reale Export-, Relocation- und Tabellenzaehler bleiben unbekannt.
- Die technische Atomaritaet wurde nicht erprobt.
- G2, DLL-Abhaengigkeiten, `numpy.libs`, Sicherheitszustand und Huerde G wurden
  nicht bearbeitet.

## Konkrete Schlussfolgerung

Die drei urspruenglichen Befunde aus 213S sind im vorgesehenen Hauptpfad
weitgehend adressiert. Die erneute statische Abnahme zeigt jedoch einen
falschen Berichtzaehler sowie zwei noch unvollstaendige Vertragsbereiche. Das
Werkzeug ist deshalb weiterhin nicht lauffreigabefaehig. Dies ist kein
beobachteter Laufzeitfehler, weil kein Code ausgefuehrt wurde.

G1 bleibt nicht bestanden, G0 bleibt abhaengig und Huerde G bleibt gesperrt.
Eine erkennbare Zielabweichung liegt nicht vor.

## Vorschlag fuer den naechsten begrenzten Schritt

Als naechstes sollte genau ein statisches Restkorrekturpaket erstellt werden,
das ausschließlich:

1. Frozen-, Override- und Aliaszaehler trennt;
2. die fehlenden festen PE32+/AMD64-Alignment- und ImageBase-Regeln ergaenzt;
3. einen schrittweise wahrheitsgemaessen Fehlerkontext einschliesslich des
   fruehen CLI-Ankerfehlers implementiert;
4. Werkzeug und Korrekturdokument neu bytegenau bindet.

Noch kein Import, keine Kompilierung, kein Test, kein Werkzeuglauf, keine
Steuerdateierzeugung, keine Manifesterzeugung, kein Resolverlauf und keine
G2-Bearbeitung.
