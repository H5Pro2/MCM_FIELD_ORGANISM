# 213ZF - G1 Controller statisches Restkorrekturpaket zu 213ZE

## Einordnung

`213ZF` ist ein statisches Restkorrekturpaket, kein Forschungslauf, kein Test
und keine Ausfuehrungsfreigabe. Eine Laufnummer wird nicht vergeben.

## Forschungsfrage und Auftrag

Auftrag war ausschliesslich die Schliessung der zwei Restbefunde aus `213ZE`:

1. eindeutige Zuordnung jedes negativen PE-Laufzeitfehlers zu seinem
   tatsaechlich fruehen AST-Zweig;
2. phasenabhaengige Freigabe des Fehler-Stagings ausserhalb des Erfolgswegs.

## Tatsaechlich verwendete Quellen

- aktueller freigegebener Uebergabe-Eingang;
- `docs/forschung/213X_G1_WERKZEUGVALIDIERUNG_VORREGISTRIERUNG.md`;
- `docs/forschung/213Z_G1_WERKZEUGVALIDIERUNG_VERTRAGSKORREKTUR.md`;
- `docs/forschung/213ZA_G1_UNABHAENGIGE_STATISCHE_ABNAHME_213Z.md`;
- `docs/forschung/213ZC_G1_UNABHAENGIGE_STATISCHE_ABNAHME_213ZB.md`;
- `docs/forschung/213ZD_G1_CONTROLLER_STATISCHES_KORREKTURPAKET_213ZC.md`;
- `docs/forschung/213ZE_G1_UNABHAENGIGE_STATISCHE_ABNAHME_213ZD.md`;
- `tests/validate_static_binary_evidence.py`;
- `tools/static_binary_evidence.py`, ausschliesslich statisch gelesen.

Keine externe Quelle wurde verwendet.

## Verwendete Dateien und Schnittstellen

Geaendert wurde ausschliesslich:

- `tests/validate_static_binary_evidence.py`.

Neue Bytebindung:

- Groesse: 34.044 Bytes;
- SHA-256:
  `76CF80B8C62EB73DC9702ED54F364D513B171BC7BF3B61642D83C14EE497E784`.

Verwendet wurden nur statisches Textlesen, Textsuche und `apply_patch`. Es
gab keine Syntaxpruefung, keinen Import und keine Ausfuehrung.

## Durchgefuehrte Korrekturen

### 1. Eindeutige PE-Zweigbindung

Die neun PE-Faelle tragen jetzt neben dem erwarteten Ergebnis einen exakten
erwarteten Fehlerdetailtext. Die sieben negativen Faelle sind getrennt:

- `PE-IMAGEBASE-ZERO` erwartet
  `zero PE base, alignment, or image size`;
- die sechs uebrigen negativen Faelle erwarten
  `invalid PE alignment invariants`.

`early_pe_failure_branches` sucht in `PEImage._parse_headers` ausschliesslich
direkte `_fail`-Aufrufe mit konstantem Code `UNSUPPORTED_PE_FORMAT` und
konstantem Detailtext. Fuer jeden gefundenen Detailtext wird gebunden, ob der
Aufruf lexikalisch vor der Data-Directory-Schleife liegt; ausserdem muss die
Directory-Schleife vor der Section-Auswertung liegen.

Ein negativer Fall besteht nur gemeinsam bei:

- exaktem Laufzeitfehlercode;
- exaktem Laufzeitdetailtext;
- vorhandenem AST-Zweig mit demselben Detailtext;
- Position dieses Zweigs vor Directory- und Section-Auswertung.

Damit kann ein spaeterer `UNSUPPORTED_PE_FORMAT` aus der Section-Auswertung
nicht mehr ersatzweise als frueher Alignmentfehler gelten.

### 2. Phasenabhaengiges Fehler-Staging

Der Audit-Waechter wird im normalen Validierungsweg nur mit zwei
Schreibwurzeln installiert:

- Fixture-Temporaerordner;
- Erfolg-Staging.

Das Fehler-Staging ist dort nicht enthalten. Vor Aufbau des Erfolgspakets
wird seine Nichtexistenz erneut geprueft. Erst nach Eintritt in den
Fehlerhandler und nur solange kein Erfolg publiziert wurde, wird der
aufgeloeste Fehler-Stagingpfad an dieselbe vom Audit-Waechter verwendete
Wurzelliste angehaengt. Danach darf genau das feste Fehlerpaket geschrieben
und umbenannt werden.

## Durchgefuehrte Schritte

1. PE-Fallmatrix um feste Detailorakel erweitert.
2. Statische Zweigsammlung auf konstante `_fail`-Identitaet umgestellt.
3. Fehlercode, Detailtext und fruehe AST-Position gemeinsam an die
   Fallakzeptanz gebunden.
4. Audit-Wurzelliste als gemeinsam mutierbaren Phasenzustand gebunden.
5. Fehler-Staging aus dem Erfolgsweg entfernt und erst im Fehlerhandler
   freigegeben.
6. Keine Anweisung ausgefuehrt.

## Messergebnisse und Gegenbaselines

Statisch beobachtet:

- adressierte Restbefunde: `2/2`;
- negative PE-Faelle: `7`;
- unterschiedliche fruehe PE-Detailzweige: `2`;
- Fehler-Staging in initialer Audit-Wurzelliste: `0`;
- Fehler-Staging-Freigaben im Fehlerhandler: `1`;
- direkte `runpy.run_path`-Stellen unveraendert: `1`;
- Gesamtfaelle unveraendert: `21`;
- ausgefuehrte Syntaxpruefungen oder Tests: `0`;
- Realpfadzugriffe: `0`.

Gegenbaselines waren der blosse Fehlercode ohne Zweigidentitaet und eine
globale Schreibfreigabe des Fehler-Stagings. Beide Formen wurden entfernt.

## Grenzen und nicht gepruefte Annahmen

- Die Syntax der Restkorrektur wurde nicht geprueft.
- PE-Fehler und Audit-Phasenwechsel wurden nicht ausgefuehrt.
- Keines der 21 Fixtures wurde erzeugt.
- Keiner der 54 Realpfade wurde beruehrt.
- Praktische Lauf- und Publikationseigenschaften sind noch nicht belegt.
- Die Korrektur ist kein G1- oder MCM-Funktionsnachweis.

## Konkrete Schlussfolgerung

Die zwei Restbefunde aus `213ZE` sind im Controller statisch adressiert. Der
Controller bleibt bis zu einer erneuten unabhaengigen statischen Abnahme
nicht ausfuehrungsreif.

G1 bleibt nicht bestanden, G0 bleibt abhaengig und Huerde G bleibt gesperrt.
Eine Zielabweichung ist nicht erkennbar.

## Vorschlag fuer den naechsten begrenzten Entwicklungsschritt

Als naechstes ist genau eine unabhaengige statische Abnahme des neu gebundenen
Controllers gegen die zwei Restbefunde aus `213ZE` und die fortgeltenden
Vertraege `213X`, `213Z` und `213ZA` erforderlich.

Bis dahin bleiben Syntaxpruefung, Tests, Controller- und Werkzeugausfuehrung,
Realpfade, Manifest, Resolver, G2 und Huerde G gesperrt.
