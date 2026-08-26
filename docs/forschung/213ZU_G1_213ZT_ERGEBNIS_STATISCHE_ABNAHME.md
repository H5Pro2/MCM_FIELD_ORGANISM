# 213ZU - Unabhaengige statische Abnahme von 213ZT

## Einordnung

`213ZU` ist eine unabhaengige statische Ergebnisabnahme und kein Forschungslauf. Controller und Werkzeug wurden nicht erneut ausgefuehrt. Die drei bereits publizierten JSON-Artefakte wurden ausschliesslich lesend geprueft.

## Forschungsfrage und Auftrag

Sind der Ergebnisbericht `213ZT` und die drei publizierten Validierungsartefakte bytegebunden, intern konsistent und mit einem erfolgreichen technischen Syntax- und Fixturelauf innerhalb aller Ausschlussgrenzen vereinbar?

## Tatsaechlich verwendete Quellen

- aktueller Uebergabe-Eingang
- `docs/forschung/213ZT_G1_WERKZEUGVALIDIERUNG_ERGEBNIS.md`
- `reports/213ZR_g1_validation_success/syntax_validation.json`
- `reports/213ZR_g1_validation_success/synthetic_fixture_validation.json`
- `reports/213ZR_g1_validation_success/validation_report.json`
- die in den JSON-Artefakten gebundenen lokalen Interpreter-, Controller-, Werkzeug-, Vertrags- und Ausschlussdateien

Keine externen Quellen wurden verwendet.

## Verwendete Dateien und Schnittstellen

Die Abnahme nutzte ausschliesslich lesende PowerShell-Hash-, JSON- und Dateistatuspruefungen. Keine Python-Schnittstelle wurde gestartet.

| Ergebnisdatei | Bytes | SHA-256 | Abgleich mit 213ZT |
|---|---:|---|---|
| `syntax_validation.json` | 779 | `8A80EF10B8DB9BAC8F11347E152AA4DA52C7123E8F6B4CFD0BE01DD91087CEEA` | bestanden |
| `synthetic_fixture_validation.json` | 24053 | `F0FBE63F23D0DF137D91F01C29084CE0238CFF661927F1723D6137E617C03DC9` | bestanden |
| `validation_report.json` | 2184 | `EFBB12DAE271DB46D406613A0C99CE5C76DDA57ECC7F820B1D105A62A1AEC65A` | bestanden |

## Durchgefuehrte Schritte

1. Groesse und SHA-256 der drei Ergebnisdateien wurden unabhaengig neu bestimmt.
2. Alle drei Dateien wurden mit einem strukturierten JSON-Parser gelesen.
3. Schemas, Syntaxstatus, Interpreterversion und Fixturezaehler wurden kontrolliert.
4. Alle 21 Fallobjekte wurden auf `passed=true` und eindeutige IDs geprueft.
5. Prozess-, Publikations-, Ausschluss- und Schreibzaehler wurden kontrolliert.
6. Publikationsordner, Temp-, Fehler- und Stagingpfade wurden im Dateisystem geprueft.
7. Eingebettete Bindungen wurden gegen die aktuellen lokalen Dateien gegengehasht.
8. Zeitintervalle und Summe der Fixturegruppen wurden auf interne Konsistenz geprueft.

## Messergebnisse und Gegenbaselines

### Bindungen und Schemas

| Pruefpunkt | Ergebnis |
|---|---|
| Ergebnisdateibindungen | `3/3` korrekt |
| Syntaxschema | `mcm-g1-static-binary-syntax-validation-v1` |
| Fixtureschema | `mcm-g1-static-binary-synthetic-fixtures-v1` |
| Berichtschema | `mcm-g1-static-binary-validation-report-v1` |
| Eingebettete Interpreterbindungen | korrekt |
| Eingebettete Runnerbindung | korrekt |
| Eingebettete Werkzeugbindungen | korrekt |
| Eingebettete Vertragsbindungen | `2/2` korrekt |
| Eingebettete Ausschlussbindung | korrekt |

### Syntax und Fixtures

| Pruefpunkt | Ergebnis |
|---|---|
| CPython-Version | `3.14.4` |
| `parse_ok` | `true` |
| `bytecode_generated` | `false` |
| `module_executed` | `false` |
| Deklarierte Faelle | `21` |
| Vorhandene Fallobjekte | `21` |
| Bestandene Faelle | `21` |
| Fehlgeschlagene Faelle | `0` |
| Nicht bestandene Fallobjekte | `0` |
| Doppelte Fall-IDs | `0` |
| Summe der Fixturegruppen | `21` |

### Prozess-, Publikations- und Ausschlussgrenzen

| Pruefpunkt | Ergebnis |
|---|---|
| Controllerprozesse | `1` |
| Erfolgspublikations-Renames | `1` |
| Fehlerpublikations-Renames | `0` |
| Unerwartete Schreibzugriffe | `0` |
| Ausgeschlossene Pfade | `54` |
| Reale Zielbinaerdatei geoeffnet | `false` |
| Projektkontrolle geoeffnet | `false` |
| Manifest erzeugt | `false` |
| Resolver ausgefuehrt | `false` |
| G2 beruehrt | `false` |

### Dateisystemzustand

| Pfadklasse | Ergebnis |
|---|---|
| Erfolgsordner | vorhanden, exakt drei Dateien |
| Tempordner | nicht vorhanden |
| Fehlerordner | nicht vorhanden |
| Erfolgs-Stagingpfad | nicht vorhanden |
| Fehler-Stagingpfad | nicht vorhanden |

Die Startzeit in Syntax- und Gesamtbericht ist identisch. Beide Zeitintervalle sind aufsteigend, und das Syntaxintervall liegt vollstaendig innerhalb des Gesamtintervalls.

Gegenbaselines waren nicht bestandene oder doppelte Fixturefaelle, Fehlerpublikation, verbliebene temporaere Pfade, unerwartete Schreibzugriffe und gesetzte Sperrindikatoren. Alle diese Gegenbaselines blieben bei null oder `false`.

## Beobachtetes Ergebnis

Die in `213ZT` berichteten technischen Ergebnisse sind durch die drei unveraenderten Artefakte bestaetigt. Syntaxparse und `21/21` synthetische Faelle sind bestanden. Publikation und Ausschlussgrenzen sind intern sowie mit dem aktuellen Dateisystemzustand konsistent.

## Technische Interpretation

Die Werkzeugvalidierung ist fuer die gebundene Syntax- und synthetische Fixtureoberflaeche unabhaengig statisch abgenommen. Dieser Befund qualifiziert das Werkzeug als technisch geprueften Kandidaten fuer einen spaeter gesondert freizugebenden G1-Schritt, nicht als bereits real validiertes Werkzeug fuer die 54 Pfade.

## Grenzen und nicht gepruefte Annahmen

- Die Abnahme reproduziert den Controllerlauf nicht, sondern prueft dessen gebundene Ergebnisartefakte.
- Die 54 Realpfade wurden nicht gelesen oder analysiert.
- Es erfolgten keine Manifest-, Resolver-, G2- oder Huerde-G-Arbeiten.
- Die 21 synthetischen Faelle decken nicht jede moegliche Werkzeugabweichung ab.
- Es gibt keine Aussage zu MCM-Memory, Feldorganisation, Semantik oder KI.

## Konkrete Schlussfolgerung

Die unabhaengige statische Abnahme von `213ZT` und den drei Ergebnisdateien ist bestanden. Bindungen, Schemas, `21/21` Faelle, Publikationszustand und Ausschlusszaehler sind konsistent. Die Aussage bleibt strikt auf die technische Werkzeugvalidierung begrenzt. Keine Zielabweichung ist erkennbar.

## Vorschlag fuer den naechsten begrenzten Schritt

Als naechster Schritt ist ein rein statischer, gesonderter Freigabevorschlag fuer die naechste G1-Stufe zu erstellen. Er muss den jetzt abgenommenen Werkzeugstand binden und klar festlegen, welche Realpfad-, Manifest- oder Resolverhandlung gegebenenfalls spaeter einzeln beantragt wird. Bis zu einer ausdruecklichen Freigabe dieses neuen Auftrags bleiben alle 54 Realpfade sowie Manifest-, Resolver-, G2- und Huerde-G-Arbeiten gesperrt.
