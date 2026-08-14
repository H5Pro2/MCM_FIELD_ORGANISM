# 213W - G1 unabhaengige statische Abnahme von 213V

## Einordnung

213W ist ein statisches Pruef- und Befundpaket, kein Forschungslauf, keine
Codekorrektur und keine Lauffreigabe. Geprueft wurde das Restkorrekturpaket
213V ausschliesslich gegen die drei Restbefunde aus 213U. Es erfolgten kein
Import, keine Kompilierung, kein Test und kein Werkzeuglauf.

## Forschungsfrage und Auftrag

Sind die in 213U festgestellten Restluecken bei disjunkten Tabellenzaehlern,
PE32+/AMD64-Invarianten und dem erreichbaren Fehlerkontext in der durch 213V
gebundenen Werkzeugdatei statisch vollstaendig und widerspruchsfrei
geschlossen?

## Tatsaechlich verwendete Quellen

- aktueller freigegebener Uebergabe-Eingang;
- `tools/static_binary_evidence.py`;
- `docs/forschung/213V_G1_STATISCHES_RESTKORREKTURPAKET_213U.md`;
- `docs/forschung/213U_G1_ERNEUTE_UNABHAENGIGE_STATISCHE_ABNAHME_213T.md`.

Keine Webquelle und keine externe MCM-Quelle wurde verwendet.

## Verwendete Dateien und Schnittstellen

Die drei genannten Dateien wurden ausschliesslich als Text beziehungsweise
Rohbytes gelesen. Verwendet wurden PowerShell-Textausgabe, Textsuche,
Dateigroesse, SHA-256 und `git diff --check`. Nur dieses Dokument wurde neu
erstellt. `tools/static_binary_evidence.py` blieb unveraendert.

Gepruefte Werkzeugbindung:

- `tools/static_binary_evidence.py`;
- 42.225 Bytes;
- SHA-256
  `03162A337473218ADBCAAE577DB1922A3127DD3BCE1AE3B151B0291BDAB4E286`.

## Durchgefuehrte statische Pruefschritte

1. Die konkrete Reihenfolge der Tabellenliste bis zu jedem Berichtszaehler
   verfolgt und die Indexbereiche paarweise abgeglichen.
2. ImageBase-, FileAlignment- und SectionAlignment-Bedingungen sowohl fuer den
   normalen PE-Fall als auch fuer SectionAlignment unterhalb 4 KiB verfolgt.
3. Die Position der neuen Invarianten vor Data-Directory- und
   Section-Verarbeitung bestaetigt.
4. Jeden Fortschreibungspunkt des Fehlerkontexts gegen den unmittelbar
   vorhergehenden Byteverifikationsschritt abgeglichen.
5. Fehler vor Sollankerabschluss, bei Steuerbindung, Werkzeugbindung,
   Vertragsbindung und innerhalb der 54 Zielbindungen statisch verfolgt.
6. Erfolgs- und Fehlerausgabe auf eine rueckwirkende Erzeugung angeblich
   verifizierter Bindungen geprueft.
7. Gesperrte Import-, Lade-, Prozess- und Auswertungsschnittstellen statisch
   gesucht.

## Messergebnisse und Gegenbaselines

### Befund 1 - Tabellenzaehler

Beobachtet:

- Builtins stammen ausschliesslich aus `tables[0]`.
- `frozen_entries` summiert ausschliesslich `tables[1:4]`, also Bootstrap,
  Stdlib und Test.
- `frozen_override_entries` stammt ausschliesslich aus dem separaten Objekt
  `override`.
- `frozen_alias_entries` stammt ausschliesslich aus `tables[4]`.

Die vier Klassen sind damit im Bericht disjunkt. Aliase und Override koennen
nicht mehr in `frozen_entries` eingehen. Der erste Restbefund aus 213U ist
statisch geschlossen.

Gegenbaseline: Die fruehere Summe ueber `tables[1:]` haette die Alias-Tabelle
eingeschlossen und den separaten Override ausgelassen. Dieses Muster liegt
nicht mehr vor.

### Befund 2 - PE32+/AMD64-Invarianten

Beobachtet:

- ImageBase muss ungleich null und durch 65.536 teilbar sein.
- SectionAlignment und FileAlignment muessen ungleich null und jeweils eine
  Potenz von zwei sein.
- FileAlignment muss im Bereich 512 bis 65.536 liegen.
- SectionAlignment darf FileAlignment nicht unterschreiten.
- Unterhalb 4.096 muss SectionAlignment genau FileAlignment entsprechen.
- SizeOfHeaders und SizeOfImage bleiben an FileAlignment beziehungsweise
  SectionAlignment gebunden.
- Alle Bedingungen werden vor Data Directories und Sections ausgewertet.

Der normale Fall und der Low-Alignment-Sonderfall sind damit fail-closed
abgedeckt. Der zweite Restbefund aus 213U ist statisch geschlossen.

Gegenbaselines: Nichtnull oder Potenz-von-zwei allein wurden nicht als
ausreichend akzeptiert. Ebenfalls nicht akzeptiert waere ein niedrigeres
SectionAlignment mit abweichendem FileAlignment.

### Befund 3 - erreichbarer Fehlerkontext

Beobachtet:

- Vor erfolgreichem Parsen des unabhaengigen Sollankers bleibt
  `expected_control` leer; der Fehlerwriter wird dennoch versucht.
- Nach erfolgreichem Sollankerparsen wird nur die erwartete Steuerbindung
  gesetzt.
- `control_binding`, `tool_binding` und `contract_binding` werden jeweils erst
  nach erfolgreicher `_verify_binding`-Rueckkehr gesetzt.
- Zielbindungen werden einzeln erst nach erfolgreicher Bytepruefung in den
  Fehlerkontext aufgenommen.
- Der Fehlerwriter berechnet keine Bindung neu und ersetzt nicht erreichte
  Schritte durch `null` beziehungsweise eine leere Liste.
- Der bestehende atomare Ausgabepfad verwirft weiterhin nichtleere
  Ausgabeziele und kann deshalb auch beim fruehen Ankerfehler nur in einen
  sicheren leeren Zielpfad schreiben.

Der Fehlerkontext bildet den statisch erreichbaren Verifikationsfortschritt
wahrheitsgemaess ab. Der dritte Restbefund aus 213U ist statisch geschlossen.

Gegenbaseline: Erwartete Bindungen, noch nicht gepruefte Zielbindungen und eine
ad hoc neu berechnete Werkzeugbindung wurden nicht als verifizierter Kontext
gewertet.

### Schnittstellenkontrolle

Die statische Suche fand keine Verwendung von `subprocess`, `ctypes`,
`importlib`, NumPy, `exec` oder `eval`. Die vorhandenen Standardbibliothek-
Dateizugriffe wurden nicht ausgefuehrt.

## Grenzen und nicht gepruefte Annahmen

- Die Python-Syntax wurde nicht kompiliert oder anderweitig ausgefuehrt.
- Kein Erfolgs- oder Fehlerpfad wurde durch einen Test aufgerufen.
- Es wurde keine Steuerdatei erzeugt oder gelesen.
- Keine der 54 Zielbinaries wurde geoeffnet oder ausgewertet.
- Die atomare Ausgabe und reale JSON-Serialisierung bleiben praktisch
  ungeprueft.
- Export-, Relocation- und CPython-Tabellenergebnisse bleiben unbekannt.
- G2, DLL-Abhaengigkeiten, Sicherheitszustand und Huerde G wurden nicht
  bearbeitet.

## Konkrete Schlussfolgerung

Die unabhaengige statische Abnahme findet innerhalb der drei freigegebenen
Prueffelder keinen verbleibenden abnahmehemmenden Widerspruch. 213V ist gegen
die Restbefunde aus 213U statisch abgenommen. Dies ist keine Aussage ueber
Syntax- oder Laufzeitfunktion und keine Freigabe zur Auswertung der gebundenen
CPython- oder `.pyd`-Binaries.

G1 bleibt nicht bestanden, G0 bleibt abhaengig, G2 und Huerde G bleiben
gesperrt. Eine erkennbare Zielabweichung liegt nicht vor.

## Vorschlag fuer den naechsten begrenzten Schritt

Als naechstes sollte genau ein rein statisches Vorregistrierungspaket fuer
eine spaetere Werkzeugvalidierung erstellt werden. Es soll Syntaxpruefung und
synthetische, lokal erzeugte Minimalfixtures fuer Zaehler-, Alignment- und
Fehlerkontextpfade festlegen, feste Eingaben und erwartete Ausgaben binden und
strikt ausschliessen, die Steuerdatei oder eines der 54 realen Zielbinaries zu
oeffnen. Erst nach gesonderter Abnahme dieser Vorregistrierung duerfen
Kompilierung oder Tests vorgeschlagen werden.

Noch kein Import, keine Kompilierung, kein Test, kein Werkzeuglauf, keine
Steuerdateierzeugung, keine Manifesterzeugung, kein Resolverlauf, keine
G2-Bearbeitung und keine Oeffnung von Huerde G.
