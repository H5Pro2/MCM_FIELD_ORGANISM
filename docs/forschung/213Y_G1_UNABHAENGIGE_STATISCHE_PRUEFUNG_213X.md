# 213Y - G1 unabhaengige statische Pruefung von 213X

## Einordnung

213Y ist ein statisches Pruef- und Befundpaket, kein Forschungslauf, keine
Korrektur von 213X, keine Runnerimplementierung und keine Lauffreigabe. Der
vorregistrierte Validierungsvertrag wurde auf Fixture-Abdeckung, Orakel,
Fallzahl, Ausschlussregeln sowie die Grenzen zwischen `ast.parse`,
`runpy.run_path`, Import und Testlauf geprueft.

Es erfolgten keine Syntaxpruefung, keine Modulausfuehrung und kein Test.

## Forschungsfrage und Auftrag

Ist 213X als spaeter ausfuehrbarer Validierungsvertrag vollstaendig und
widerspruchsfrei, insbesondere hinsichtlich der 20 festen Fixtures, des
realen Ausschlusskorpus, der atomaren Pflichtausgaben und der unterschiedlichen
Bedeutung von Syntaxlesen und Modulausfuehrung?

## Tatsaechlich verwendete Quellen

- aktueller freigegebener Uebergabe-Eingang;
- `docs/forschung/213X_G1_WERKZEUGVALIDIERUNG_VORREGISTRIERUNG.md`;
- `tools/static_binary_evidence.py`.

Keine Webquelle und keine externe MCM-Quelle wurde verwendet.

## Verwendete Dateien und Schnittstellen

Die beiden Dateien wurden ausschliesslich als Text und Rohbytes gelesen.
Verwendet wurden PowerShell-Textausgabe, Textsuche, Dateigroesse, SHA-256 und
`git diff --check`. Nur dieses Dokument wurde neu erstellt. Weder 213X noch
die Werkzeugdatei wurden veraendert.

Gepruefte Bindungen:

- `docs/forschung/213X_G1_WERKZEUGVALIDIERUNG_VORREGISTRIERUNG.md`:
  13.427 Bytes, SHA-256
  `48DEB78544B8E1817E33BF01FD484EA7FBA750628CA200FE7BC9BB0147E81D63`;
- `tools/static_binary_evidence.py`: 42.225 Bytes, SHA-256
  `03162A337473218ADBCAAE577DB1922A3127DD3BCE1AE3B151B0291BDAB4E286`.

## Durchgefuehrte statische Pruefschritte

1. Alle Falltabellen ausgezaehlt und mit den Gruppen- und Gesamtzaehlern
   abgeglichen.
2. Fuer jeden in 213W abgenommenen Korrekturbereich geprueft, ob mindestens ein
   positiver und ein isolierter negativer Fall existiert.
3. Die sieben Fehlerkontextfixtures bis zu den tatsaechlich aufgerufenen
   Werkzeugfunktionen verfolgt.
4. Herkunft, Format und Bindung der geforderten Realpfad-Ausschlussliste
   gesucht.
5. Schreibverantwortung fuer die drei Pflichtausgaben ueber beide
   Interpreterstarts verfolgt.
6. `ast.parse` als reine Quelltextanalyse von `runpy.run_path` als
   Modulausfuehrung getrennt und gegen alle Importaussagen abgeglichen.
7. Stopplinien darauf geprueft, ob ein Fehlerzustand noch dokumentierbar ist,
   ohne die Atomaritaetsregel zu verletzen.

## Messergebnisse und Gegenbaselines

### Bestaetigte Teile

- Die dokumentierte Fallzahl ist rechnerisch konsistent: 4 Zaehlerfaelle, 9
  Alignmentfaelle und 7 Fehlerkontextfaelle ergeben 20.
- Die Zaehlerorakel trennen feste Frozen-Eintraege, Override und Aliase.
- Die Alignmentfixtures decken beide gueltigen Betriebsarten sowie ImageBase,
  FileAlignment-Grenzen, Potenz-von-zwei, Section-vs-File und Low-Alignment-
  Gleichheit ab.
- Die sieben direkten Fehlerwriter-Faelle bilden leeren und schrittweise
  gefuellten Kontext mit eindeutigen JSON-Orakeln ab.
- Phase A beschreibt `ast.parse` korrekt als Quelltextanalyse ohne Ausfuehrung
  des Zielmoduls.
- Phase B benennt `runpy.run_path` und einen Nicht-`__main__`-Namen; `main()`
  und `collect()` bleiben ausdruecklich gesperrt.
- Reale CPython- und `.pyd`-Binaries sowie die Projektsteuerdatei sind als
  verbotene Eingaben benannt.

Gegenbaseline war jeweils ein Vertrag, der nicht nur die beabsichtigte
Sicherheitswirkung beschreibt, sondern alle benoetigten Eingaben, Ausgaben und
Abbruchpfade so bindet, dass ein spaeterer Runner keine eigene Auslegung
erfinden muss.

## Abnahmehemmende Befunde

### Befund 1 - Realpfad-Ausschlussliste ist weder Quelle noch Artefaktbindung

Schwere: hoch.

213X fordert vor Phase B eine Liste der 54 ausgeschlossenen Realpfade und den
Stopp `EXCLUSION_SET_MISSING`. Es legt jedoch weder Pfad, Schema, Anzahl,
Rollenzuordnung, Groesse, SHA-256 noch eine erlaubte Quelle dieser Liste fest.
Gleichzeitig darf der Runner keine andere Projektdatei lesen.

Damit kann ein spaeterer Implementierer die Ausschlussmenge nicht
reproduzierbar beziehen. Eine leere, frei eingegebene oder aus einem anderen
Workspacezustand stammende Liste koennte formal als vorhanden gelten, ohne die
tatsaechlichen 1 + 53 Zielpfade abzudecken.

Erforderliche Korrektur: Genau ein statisches Ausschlussartefakt oder eine
vollstaendig vorgebundene Launcher-Eingabe mit Schema, exakt 54 eindeutigen
kanonischen Pfaden, Rollenabschluss 1 + 53, Groesse und SHA-256 festlegen. Nur
dieses Artefakt darf als zusaetzliche Lesedatei zugelassen werden. Es darf
keine Binary-Inhalte oder Binary-Hashes durch den Runner neu ermitteln.

### Befund 2 - frueher CLI-Ankerpfad ist in den 20 Faellen nicht abgedeckt

Schwere: hoch.

Die Fehlerkontextfixtures B3 konstruieren `ErrorContext` direkt und rufen nur
`_write_error_only` auf. `main()`, `collect()` und `_verify_binding` sind
gesperrt. E-NONE zeigt daher zwar, dass ein leerer Kontext serialisiert werden
kann, prueft aber nicht den in 213V korrigierten Kontrollfluss: Fehler von
`_parse_binding` muss in `main()` den Fehlerwriter erreichen.

Der Vertrag behauptet damit Fixture-Abdeckung des Fehlerkontextpfads, ohne den
fruehen Routingpunkt zu beobachten. Ein spaeterer Verlust des
`_write_error_only`-Aufrufs im ersten `except EvidenceError` bliebe bei 20/20
unentdeckt.

Erforderliche Korrektur: Einen eigenen, rein AST-strukturellen Routingfall mit
festem Orakel ergaenzen oder E-NONE entsprechend erweitern. Das Orakel muss den
ersten `_parse_binding`-Fehlerzweig in `main()` eindeutig dem Aufruf
`_write_error_only(args.output_dir, exc, context=error_context)` zuordnen,
ohne `main()` auszufuehren. Fallzahl und Akzeptanzsumme sind danach eindeutig
neu festzulegen.

### Befund 3 - atomare Ausgabe ist ueber zwei Interpreterstarts nicht zugeordnet

Schwere: mittel bis hoch.

213X erlaubt genau einen Interpreterstart fuer Phase A und einen fuer Phase B.
Phase A soll bereits `syntax_validation.json` schreiben. Gleichzeitig soll der
Ergebnisordner atomar neu entstehen und am Ende genau drei Dateien enthalten.
Es ist nicht festgelegt, welcher Prozess den Stagingordner besitzt, wie Phase
B das Ergebnis von Phase A bezieht und welcher Prozess den einzigen finalen
Rename ausfuehrt.

Ohne diese Zuordnung muesste entweder Phase A den finalen Ordner vorzeitig
erzeugen oder Phase B einen bereits nichtleeren Ausgabeordner uebernehmen.
Beides widerspricht der beschriebenen einmaligen atomaren Gesamtausgabe.
Auch der dokumentierte Fehlerfall bei Syntaxfehler hat kein eindeutiges
atomar publizierbares Ergebnisformat.

Erforderliche Korrektur: Einen einzigen Laufcontroller und ein festes
Stagingprotokoll definieren. Phase A darf nur ein gebundenes Zwischenartefakt
im Stagingbereich erzeugen; Phase B beziehungsweise der Controller muss nach
vollstaendiger Validierung genau einen finalen Rename vornehmen. Fuer Stopps
muss ein separates, ebenfalls atomares Fehlerpaket mit festen Dateien
vorregistriert werden.

### Befund 4 - Import- und Ausfuehrungsbegriffe sind noch nicht normativ getrennt

Schwere: mittel.

Phase A sagt korrekt, dass das Modul nicht importiert wird. Phase B fuehrt mit
`runpy.run_path` jedoch den Modulrumpf aus; dabei werden auch die im Werkzeug
stehenden Standardbibliothek-Importanweisungen ausgefuehrt. Das ist kein
Projektimport und kein Aufruf von `main()`, aber sehr wohl Modulausfuehrung und
Standardbibliothek-Importaktivitaet.

Die Formulierungen `kein Import`, `keine Modulausfuehrung` und `kein Testlauf`
sind deshalb nur fuer den aktuellen Vorregistrierungsschritt und Phase A
wahr. Sie koennen nicht als globale Eigenschaft der spaeteren Phase B gelten.

Erforderliche Korrektur: Vier Begriffe verbindlich definieren:

- aktueller Schritt: keinerlei Python-Ausfuehrung;
- Phase A: Interpreterlauf mit `ast.parse`, aber keine Zielmodulausfuehrung;
- Phase B: genau eine Zielmodulausfuehrung via `runpy.run_path`, einschliesslich
  der statisch vorhandenen Standardbibliothekimporte;
- weiterhin verboten: Projekt-/Drittanbieterimporte, `importlib`, direkter
  Import unter dem Produktionsnamen, `main()` und `collect()`.

Der spaetere Fixture-Runner ist ein Testlauf. Nur die aktuelle Erstellung oder
Pruefung des Vertrags darf als `kein Testlauf` bezeichnet werden.

## Grenzen und nicht gepruefte Annahmen

- Es wurde kein Runner implementiert oder ausgefuehrt.
- Die Syntax von Werkzeug und kuenftigem Runner blieb ungeprueft.
- Keine synthetische PE-Datei und kein Ergebnisordner wurde erzeugt.
- Es wurde nicht praktisch geprueft, ob `runpy.run_path` ohne Seiteneffekt
  ausserhalb der erlaubten Ordner bleibt.
- Keine Projektsteuerdatei und keines der 54 realen Zielbinaries wurde
  geoeffnet.
- Die vier Befunde sind Vertragsbefunde, keine beobachteten Laufzeitfehler.

## Konkrete Schlussfolgerung

213X enthaelt eine sinnvolle, rechnerisch konsistente Fixturebasis. Als
ausfuehrbarer Vorregistrierungsvertrag ist es wegen der ungebundenen
Ausschlussmenge, der fehlenden CLI-Routingabdeckung, der unklaren atomaren
Mehrprozessausgabe und der begrifflichen Importgrenze noch nicht
abnahmefaehig.

G1 bleibt nicht bestanden, G0 bleibt abhaengig, G2 und Huerde G bleiben
gesperrt. Eine erkennbare Zielabweichung liegt nicht vor.

## Vorschlag fuer den naechsten begrenzten Schritt

Als naechstes sollte genau ein statisches Vertragskorrekturpaket fuer 213X
erstellt werden, das ausschliesslich:

1. die 54 Realpfade ueber ein bytegebundenes Ausschlussartefakt festlegt;
2. einen AST-Routingfall fuer den fruehen CLI-Ankerfehler ergaenzt und die
   feste Fallzahl anpasst;
3. einen einzigen atomaren Staging- und Publikationscontroller samt
   Fehlerpaket definiert;
4. `ast.parse`, `runpy`-Modulausfuehrung, erlaubte Standardbibliothekimporte
   und verbotene Importklassen normativ trennt;
5. Korrekturdokument und gegebenenfalls Ausschlussartefakt bytegenau bindet.

Noch keine Runnerimplementierung, keine Syntaxpruefung, keine Kompilierung,
kein Test, kein Werkzeuglauf, keine Steuerdateierzeugung, kein Oeffnen realer
Zielbinaries, keine Manifesterzeugung, kein Resolverlauf, keine G2-Bearbeitung
und keine Oeffnung von Huerde G.
