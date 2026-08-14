# 213ZB - G1 Einprozess-Controller Implementierung

## Einordnung

`213ZB` ist eine statische Implementierung, kein Forschungslauf und keine
Ausfuehrungsfreigabe. Eine Laufnummer wird deshalb nicht vergeben.

## Forschungsfrage und Auftrag

Auftrag war genau eine statische Implementierung des in `213X` und `213Z`
vorregistrierten Einprozess-Controllers. Der Controller muss die spaetere
Syntaxanalyse und 21 synthetischen Faelle in einem Prozess ausfuehren und das
Gesamtergebnis atomar publizieren, ohne reale Zielpfade zu verwenden.

## Tatsaechlich verwendete Quellen

- aktueller freigegebener Uebergabe-Eingang;
- `docs/forschung/213X_G1_WERKZEUGVALIDIERUNG_VORREGISTRIERUNG.md`;
- `docs/forschung/213Y_G1_UNABHAENGIGE_STATISCHE_PRUEFUNG_213X.md`;
- `docs/forschung/213Z_G1_REALPFAD_AUSSCHLUSSMENGE.json`;
- `docs/forschung/213Z_G1_WERKZEUGVALIDIERUNG_VERTRAGSKORREKTUR.md`;
- `docs/forschung/213ZA_G1_UNABHAENGIGE_STATISCHE_ABNAHME_213Z.md`;
- `tools/static_binary_evidence.py`, nur statisch gelesen.

Keine externen Quellen wurden verwendet.

## Verwendete Dateien und Schnittstellen

Neu erstellt wurde:

- `tests/validate_static_binary_evidence.py`.

Bytebindung der statisch implementierten Controllerdatei:

- Groesse: 25.727 Bytes;
- SHA-256:
  `50AD8FC8B08946B2BC584913F208C45592F9568A8DE9B8C00BF8B04FD6ABB3CD`.

Verwendet wurden ausschliesslich statisches Textlesen, Textsuche und
`apply_patch`. Der neue Controller und das Zielwerkzeug wurden nicht
ausgefuehrt oder importiert. Es gab keine Syntaxpruefung und keinen Test.

## Implementierte Vertragsbestandteile

Der Controller besitzt:

1. explizite CLI-Bindungen fuer Runner, Werkzeug, `213X`, `213Z`,
   Ausschlussartefakt und CPython-Interpreter;
2. Bindungspruefungen vor Syntaxanalyse und Fixtures;
3. strukturelle Pruefung der 54er-Ausschlussmenge ohne Zugriff auf die darin
   genannten Realpfade;
4. Phase A ueber `ast.parse` und eine exakte Positivliste direkter
   Werkzeugimporte;
5. Phase B ueber genau einen statisch sichtbaren `runpy.run_path`-Aufruf mit
   dem vorregistrierten Nicht-`__main__`-Namen;
6. vier Zaehler-, neun PE-Alignment-, sieben Fehlerkontext- und einen
   AST-Routingfall;
7. feste Akzeptanz `21/21`;
8. einen Erfolg-Stagingbaum mit genau drei Dokumenten und genau einem finalen
   Rename;
9. einen getrennten Fehler-Stagingbaum mit genau einem Fehlerdokument und
   genau einem Rename;
10. unveraenderte Sperrflags fuer Steuerdatei, Realbinaries, Manifest,
    Resolver und G2.

Der Controller enthaelt keine Projektimporte, Drittanbieterimporte,
`subprocess`, Netzwerkzugriffe, `ctypes`, `importlib`, `exec`, `eval` oder
`compile`. `main`, `collect` und `_verify_binding` des Zielwerkzeugs werden
nicht aufgerufen.

## Durchgefuehrte Schritte

1. Die Vertragsstellen und tatsaechlichen Werkzeugstrukturen wurden statisch
   gelesen.
2. Die CLI- und Bindungsgrenze wurde festgelegt.
3. Die vier Fixturegruppen wurden mit festen IDs und Orakeln implementiert.
4. Erfolg- und Fehlerpublikation wurden getrennt und jeweils als einzelner
   Verzeichnis-Rename umgesetzt.
5. Die Ausfuehrung wurde an keiner Stelle gestartet.

## Messergebnisse und Gegenbaselines

Beobachtete statische Implementierungswerte:

- Controllerdateien: `1`;
- vorgesehene Controllerprozesse: `1`;
- statisch vorgesehene `runpy.run_path`-Aufrufe: `1`;
- Fallgruppen: `4 + 9 + 7 + 1`;
- Gesamtfaelle: `21`;
- Erfolgspaketdateien: `3`;
- Fehlerpaketdateien: `1`;
- Zugriffe auf die 54 Realpfade: `0` in diesem Implementierungsschritt;
- ausgefuehrte Syntaxpruefungen oder Tests: `0`.

Gegenbaselines sind die in `213Y` verworfenen Formen: freie
Ausschlusslisten, nur 20 Faelle, zwei Controllerprozesse und eine globale
Behauptung ohne Importaktivitaet. Keine dieser Formen wurde implementiert.

## Grenzen und nicht gepruefte Annahmen

- Die Syntax des Controllers ist absichtlich noch ungeprueft.
- Kein Fixture wurde erzeugt oder ausgefuehrt.
- Die AST-Orakel, PE-Rohbytes, Fehlerkontexte und Publikationspfade sind nur
  implementiert, nicht praktisch bestaetigt.
- Der Controller ist noch nicht unabhaengig statisch abgenommen und darf vor
  dieser Abnahme nicht ausgefuehrt werden.
- Keine Steuerdatei und keines der 54 realen Zielbinaries wurde geoeffnet.
- Es folgt keine Aussage ueber G1-Evidenz oder eine MCM-Funktion.

## Konkrete Schlussfolgerung

Der vorregistrierte Einprozess-Controller liegt als statische Implementierung
vor. Daraus folgt noch keine Syntax- oder Lauffaehigkeit. G1 bleibt nicht
bestanden, G0 bleibt abhaengig und Huerde G bleibt gesperrt. Eine
Zielabweichung ist nicht erkennbar.

## Vorschlag fuer den naechsten begrenzten Entwicklungsschritt

Als naechstes ist zwingend genau eine unabhaengige statische Abnahme von
`tests/validate_static_binary_evidence.py` gegen `213X`, `213Z` und `213ZA`
erforderlich. Fokus: Bindungsreihenfolge, Verbot von Realpfadzugaengen,
vollstaendige 21 Orakel, genau eine Zielmodulausfuehrung, Einprozessgrenze und
atomare Erfolg-/Fehlerpublikation.

Bis zu dieser Abnahme bleiben Syntaxpruefung, Kompilierung, Tests,
Controller- und Werkzeugausfuehrung, Steuerdatei, Realbinaries, Manifest,
Resolver, G2 und Huerde G gesperrt.
