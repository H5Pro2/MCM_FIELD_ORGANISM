# 213ZG - Unabhaengige statische Abnahme von 213ZF

## Einordnung

`213ZG` ist eine statische Abnahme und kein Forschungslauf. Gegenstand ist ausschliesslich der durch `213ZF` neu gebundene Einprozess-Controller. Es wurden weder Syntaxpruefung noch Test, Controller- oder Werkzeugausfuehrung durchgefuehrt. Die 54 gebundenen Realpfade wurden nicht geoeffnet.

## Forschungsfrage und Auftrag

Schliesst der neu gebundene Controller die zwei Restbefunde aus `213ZE` und bleibt er zugleich mit den fortgeltenden Vertraegen aus `213X`, `213Z` und `213ZA` vereinbar?

Besonders zu pruefen waren:

1. sieben negative PE-Faelle mit zwei fruehen Detailzweigen, darunter ein eigener Zweig fuer `PE-IMAGEBASE-ZERO`,
2. eindeutige Bindung von Fehlercode, Detailtext, AST-Zweig und Position vor Directory- und Section-Auswertung,
3. fehlende initiale Schreibfreigabe fuer das Fehler-Staging,
4. Freigabe des Fehler-Stagings ausschliesslich im Fehlerhandler,
5. Ausschluss einer Fehlerpublikation nach erfolgreicher Publikation.

## Tatsaechlich verwendete Quellen

- aktueller Uebergabe-Eingang mit der Freigabe zur statischen Abnahme,
- `docs/forschung/213ZE_G1_UNABHAENGIGE_STATISCHE_ABNAHME_213ZD.md`,
- `docs/forschung/213ZF_G1_CONTROLLER_STATISCHES_RESTKORREKTURPAKET_213ZE.md`,
- `docs/forschung/213X_G1_WERKZEUGVALIDIERUNG_VORREGISTRIERUNG.md`,
- `docs/forschung/213Z_G1_WERKZEUGVALIDIERUNG_VERTRAGSKORREKTUR.md`,
- `docs/forschung/213ZA_G1_UNABHAENGIGE_STATISCHE_ABNAHME_213Z.md`,
- `tests/validate_static_binary_evidence.py`,
- `tools/static_binary_evidence.py`.

Keine externen Quellen wurden verwendet.

## Verwendete Dateien und Schnittstellen

| Datei | Bytes | SHA-256 |
|---|---:|---|
| `tests/validate_static_binary_evidence.py` | 34.044 | `76CF80B8C62EB73DC9702ED54F364D513B171BC7BF3B61642D83C14EE497E784` |
| `docs/forschung/213ZF_G1_CONTROLLER_STATISCHES_RESTKORREKTURPAKET_213ZE.md` | 5.339 | `D65E093F2EFDD02A8FD275D7B02D89CECB941A5181354C65F883C29DB687C3B1` |
| `docs/forschung/213ZE_G1_UNABHAENGIGE_STATISCHE_ABNAHME_213ZD.md` | 7.871 | `AF7FB8B8AB60C0059EFDE128AD682520EED3A938B16B6D619832AB453ED64497` |
| `docs/forschung/213X_G1_WERKZEUGVALIDIERUNG_VORREGISTRIERUNG.md` | 13.427 | `48DEB78544B8E1817E33BF01FD484EA7FBA750628CA200FE7BC9BB0147E81D63` |
| `docs/forschung/213Z_G1_WERKZEUGVALIDIERUNG_VERTRAGSKORREKTUR.md` | 12.309 | `6E6A3500295472AD8AD45DDE5A57CCE42C07307EE64D4B1734DACF9D1646E75D` |
| `tools/static_binary_evidence.py` | 42.225 | `03162A337473218ADBCAAE577DB1922A3127DD3BCE1AE3B151B0291BDAB4E286` |

Untersucht wurden nur statisch sichtbare Python-Quelltext- und Dokumentvertraege. Es wurde keine Laufzeitschnittstelle aufgerufen.

## Durchgefuehrte Schritte

1. Die Bytebindungen des Controllers und der Vertragsdokumente wurden gegen `213ZF` und die fortgeltenden Bindungen abgeglichen.
2. Die sieben negativen PE-Fallbeschreibungen wurden mit dem geschlossenen AST-Auswerter und den Fehlerzweigen in `PEImage._parse_headers` verglichen.
3. Fehlercode, exakter Detailtext und Quellposition jedes erwarteten Zweigs wurden gegen die Positionen der Directory-Schleife und der Section-Auswertung geprueft.
4. Der Schreibwaechter, seine mutable Freigabeliste sowie Erfolgs- und Fehlerpfad wurden statisch verfolgt.
5. Die fortgeltenden Kontrollen zu Fallzahl, Routing, Einprozess-Controller, Importgrenze und Realpfadsperre wurden erneut auf erkennbare Regressionen geprueft.

## Messergebnisse und Gegenbaselines

| Pruefpunkt | Soll | Beobachtet | Ergebnis |
|---|---|---|---|
| Negative PE-Faelle | 7 | 7 | bestanden |
| Fruehe PE-Detailzweige | 2 | 2: `zero PE base, alignment, or image size`; `invalid PE alignment invariants` | bestanden |
| `PE-IMAGEBASE-ZERO` | eigener frueher Zweig | eigener exakter Detailzweig vor Directory- und Section-Auswertung | bestanden |
| Uebrige PE-Negativfaelle | Alignment-Zweig | 6 Faelle an den exakten Alignment-Detailzweig gebunden | bestanden |
| Fehlercode | `UNSUPPORTED_PE_FORMAT` | in beiden fruehen Zweigen konstant gebunden | bestanden |
| Fehler-Staging initial | nicht freigegeben | initiale Waechterliste enthaelt nur Temp- und Erfolgs-Staging | bestanden |
| Fehler-Staging im Fehlerpfad | erst dort freigegeben | Aufloesung und Anhaengen erfolgen im Ausnahmehandler | bestanden |
| Fehlerpublikation nach Erfolg | ausgeschlossen | Erfolg prueft fehlendes Fehler-Staging, publiziert atomar, setzt Erfolgsflag und kehrt unmittelbar zurueck; Fehlerhandler publiziert nur bei nicht gesetztem Erfolgsflag | bestanden |
| Vertragsfaelle | 21 = 4 + 9 + 7 + 1 | 21 = 4 + 9 + 7 + 1 | bestanden |
| Werkzeugrouting | genau eine `runpy.run_path`-Stelle | genau eine statisch sichtbare Stelle | bestanden |

Gegenbaseline fuer den PE-Punkt waren die falschen beziehungsweise unzureichenden Bindungen aus `213ZE`: ein gemeinsamer Detailzweig fuer alle negativen PE-Faelle oder ein Zweig erst nach Directory-/Section-Auswertung waere nicht akzeptiert worden. Beides liegt im neu gebundenen Controller nicht vor.

Gegenbaseline fuer das Staging war eine initiale Schreibfreigabe des Fehler-Stagings oder eine nach Erfolg noch erreichbare Fehlerpublikation. Auch diese beiden Zustaende sind im statisch sichtbaren Kontrollfluss nicht vorhanden.

Gesamtergebnis der beauftragten Restabnahme: **2/2 Restbefunde geschlossen**. Bei der begrenzten Regressionseinordnung wurde kein neuer abnahmehemmender statischer Befund erkannt.

## Grenzen und nicht gepruefte Annahmen

- Die Python-Syntax wurde absichtlich nicht geprueft.
- Der Controller und das Werkzeug wurden nicht importiert oder ausgefuehrt.
- Es wurden keine Tests und keine Laufzeit-Gegenbaselines ausgefuehrt.
- Die tatsaechliche Wirksamkeit des Schreibwaechters, der AST-Orakel und der atomaren Publikation ist daher noch nicht empirisch belegt.
- Die 54 Realpfade und ihre Zielbinaries wurden nicht geoeffnet oder aufgeloest.
- Es wurde kein Manifest erzeugt und keine G2- oder Huerde-G-Arbeit vorgenommen.
- Aus dieser statischen Abnahme folgt kein Nachweis von MCM-Memory, Feldorganisation, Semantik, KI oder einer anderen Organismusfunktion.

## Konkrete Schlussfolgerung

Der durch `213ZF` gebundene Controller schliesst die zwei Restbefunde aus `213ZE` statisch. Die sieben negativen PE-Faelle sind eindeutig auf zwei fruehe Fehlerzweige verteilt; `PE-IMAGEBASE-ZERO` besitzt den geforderten eigenen Zweig. Das Fehler-Staging ist im Erfolgsweg nicht freigegeben und wird ausschliesslich im Fehlerhandler beschreibbar. Eine Fehlerpublikation nach erfolgreicher Publikation ist im sichtbaren Kontrollfluss ausgeschlossen.

Damit ist die statische Abnahme des Controllercodes gegen die vorliegenden Vertraege bestanden. Dies ist noch keine Syntax-, Test- oder Ausfuehrungsfreigabe. G1 bleibt ohne kontrollierten Werkzeuglauf nicht bestanden, G0 bleibt davon abhaengig und Huerde G bleibt gesperrt. Eine Zielabweichung ist nicht erkennbar.

## Vorschlag fuer den naechsten begrenzten Entwicklungsstand

Als naechster Schritt sollte genau eine statische Ausfuehrungsvorregistrierung erstellt werden. Sie bindet bytegenau den freigegebenen CPython-3.14.4-Interpreter, den Controller, das Werkzeug, das Ausschlussartefakt und alle Vertragsdateien sowie genau einen frischen Satz aus Temp-, Erfolgs- und Fehlerziel und genau einen spaeter auszufuehrenden CLI-Befehl. In diesem Schritt duerfen weiterhin weder Syntaxpruefung noch Test, Controller- oder Werkzeugausfuehrung, Realpfadzugriff, Manifest-, Resolver-, G2- oder Huerde-G-Arbeit stattfinden. Erst die unabhaengige statische Abnahme dieser Vorregistrierung kann eine getrennte Entscheidung ueber einen ersten kontrollierten Werkzeuglauf vorbereiten.
