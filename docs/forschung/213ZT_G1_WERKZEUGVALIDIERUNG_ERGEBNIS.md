# 213ZT - Ergebnis der kontrollierten G1-Werkzeugvalidierung

## Einordnung

`213ZT` dokumentiert einen technischen Validierungsschritt und keinen Forschungslauf zur MCM-Felddynamik. Es wurde genau der in `213ZR` gebundene Einzelbefehl einmal ausgefuehrt. Ein Wiederholungsversuch fand nicht statt.

## Forschungsfrage und Auftrag

Besteht das gebundene Werkzeug unter CPython 3.14.4 die kontrollierte Syntaxanalyse und alle 21 synthetischen Validierungsfaelle, ohne die 54 ausgeschlossenen Realpfade oder gesperrte Projektbereiche zu verwenden?

## Tatsaechlich verwendete Quellen

- juengstes Startsignal und bestehender Projektstand
- `docs/forschung/213ZR_G1_CLI_VERTRAG_KORREKTURPAKET.md`
- `docs/forschung/213ZS_G1_213ZR_STATISCHE_ABNAHME.md`
- `reports/213ZR_g1_validation_success/syntax_validation.json`
- `reports/213ZR_g1_validation_success/synthetic_fixture_validation.json`
- `reports/213ZR_g1_validation_success/validation_report.json`
- die sechs unmittelbar vor dem Start erneut geprueften lokalen Dateien

Keine externen Quellen wurden verwendet.

## Verwendete Dateien und Schnittstellen

| Rolle | Bytes | SHA-256 | Unmittelbarer Vorabgleich |
|---|---:|---|---|
| Interpreter | 106328 | `7CA24F26D6E3F463419EE4F537DDD3ACD312C38FE45E678CCE08572F26A8BD1A` | bestanden |
| Controller | 34044 | `433B6EA8695B6C7B6FCC2C583C7125606B00567900802F2871DA305932D1A88D` | bestanden |
| Werkzeug | 42225 | `03162A337473218ADBCAAE577DB1922A3127DD3BCE1AE3B151B0291BDAB4E286` | bestanden |
| Vertrag 213X | 13427 | `48DEB78544B8E1817E33BF01FD484EA7FBA750628CA200FE7BC9BB0147E81D63` | bestanden |
| Vertrag 213Z | 12309 | `6E6A3500295472AD8AD45DDE5A57CCE42C07307EE64D4B1734DACF9D1646E75D` | bestanden |
| Ausschlussartefakt | 6253 | `52DA5D8DD26314BF173367E7F02D1F1B1055077380E83159A0FAE3EB87304ACF` | bestanden |

Die Workspacebindung wurde unmittelbar vor dem Start mit 50 UTF-8-Bytes und SHA-256 `C4DE596ECEDB6CBA69ACCFAAA5FF1A3BEE77899BE6690BC8056B0184F5268493` bestaetigt. Als Ausfuehrungsschnittstelle diente ausschliesslich der exakt in `213ZR` gebundene `C:\Python314\python.exe -B`-Befehl.

## Durchgefuehrte Schritte

1. Sechs Datei-, Groessen- und SHA-256-Bindungen wurden unmittelbar vor dem Start erneut geprueft.
2. Workspacebindung und Nichtvorhandensein aller fuenf Zielpfade wurden unmittelbar erneut geprueft.
3. Der exakt in `213ZR` gebundene Befehl wurde einmal gestartet.
4. Exitcode und Publikationszustand wurden nach Prozessende statisch geprueft.
5. Alle drei publizierten JSON-Dateien wurden mit PowerShell strukturiert gelesen und ausgewertet.
6. Groesse und SHA-256 der drei Ergebnisdateien wurden unabhaengig bestimmt.

## Messergebnisse und Gegenbaselines

### Prozess und Publikation

| Messpunkt | Ergebnis |
|---|---|
| Controllerprozesse | exakt `1` |
| Wiederholungsversuche | `0` |
| Exitcode | `0` |
| Konsolenausgabe | leer |
| Tempordner nach Abschluss | nicht vorhanden |
| Erfolgsordner | vorhanden |
| Fehlerordner | nicht vorhanden |
| Erfolgs-Stagingpfad | nicht vorhanden |
| Fehler-Stagingpfad | nicht vorhanden |
| Erfolgspublikations-Renames | `1` |
| Fehlerpublikations-Renames | `0` |

### Syntax und synthetische Faelle

| Messpunkt | Ergebnis |
|---|---|
| Interpreterversion | `3.14.4 (tags/v3.14.4:23116f9, Apr 7 2026, 14:10:54) [MSC v.1944 64 bit (AMD64)]` |
| Syntaxparse | bestanden |
| Bytecode erzeugt | nein |
| Werkzeugmodul als Zielmodul ausgefuehrt | nein |
| Synthetische Faelle | `21/21` bestanden |
| Fehlgeschlagene synthetische Faelle | `0` |
| Gruppen | Count `4`, Alignment `9`, Error-Context `7`, Routing `1` |

### Ausschluss- und Schreibgrenzen

| Messpunkt | Ergebnis |
|---|---|
| Gebundene ausgeschlossene Pfade | `54` |
| Reale Zielbinaerdatei geoeffnet | nein |
| Projektkontrolle geoeffnet | nein |
| Manifest erzeugt | nein |
| Resolver ausgefuehrt | nein |
| G2 beruehrt | nein |
| Unerwartete Schreibzugriffe | `0` |

### Ergebnisdateibindungen

| Datei | Bytes | SHA-256 |
|---|---:|---|
| `syntax_validation.json` | 779 | `8A80EF10B8DB9BAC8F11347E152AA4DA52C7123E8F6B4CFD0BE01DD91087CEEA` |
| `synthetic_fixture_validation.json` | 24053 | `F0FBE63F23D0DF137D91F01C29084CE0238CFF661927F1723D6137E617C03DC9` |
| `validation_report.json` | 2184 | `EFBB12DAE271DB46D406613A0C99CE5C76DDA57ECC7F820B1D105A62A1AEC65A` |

Gegenbaselines sind der fruehere CLI-Fruehabbruch `213ZQ`, die Fehlerpublikation und unerwartete Schreibzugriffe. Anders als in `213ZQ` wurde diesmal die Syntax- und Fixturephase erreicht; es entstand keine Fehlerpublikation und der Zaehler unerwarteter Schreibzugriffe blieb null.

## Beobachtetes Ergebnis

Die kontrollierte Werkzeugvalidierung ist technisch bestanden. Der gebundene Controller meldete Exitcode `0`, Syntaxparse `parse_ok=true`, und alle 21 synthetischen Faelle tragen `passed=true`. Die Erfolgsausgabe wurde atomar publiziert; temporaere und Stagingpfade blieben nach Abschluss nicht bestehen.

## Technische Interpretation

Unter den gebundenen Dateien und CPython 3.14.4 funktioniert der Validierungsweg fuer die getestete Syntax- und synthetische Fixtureoberflaeche. Der Lauf belegt ausserdem innerhalb der protokollierten Controllergrenzen, dass keine ausgeschlossene reale Zielbinaerdatei oder Projektkontrolle geoeffnet und kein Manifest oder Resolverlauf erzeugt wurde.

## Hypothese

Das Werkzeug ist damit ein technisch geeigneter Kandidat fuer eine spaeter gesondert vorregistrierte reale G1-Pruefung. Diese Hypothese ist nicht getestet, weil Realpfade und nachgelagerte G1-Arbeiten weiterhin ausgeschlossen waren.

## Grenzen und nicht gepruefte Annahmen

- Synthetische Validierung ist keine reale G1-Auswertung und keine Aussage ueber die 54 Realpfade.
- Die Ergebnisse belegen nur die 21 vorgegebenen Faelle und keine vollstaendige Fehlerfreiheit des Werkzeugs.
- Manifest-, Resolver-, G2- und Huerde-G-Arbeiten wurden nicht durchgefuehrt.
- Es entsteht kein Befund zu MCM-Memory, Feldorganisation, Semantik oder KI.
- Die JSON-Inhalte und Dateibindungen muessen noch unabhaengig statisch abgenommen werden.

## Konkrete Schlussfolgerung

Die kontrollierte G1-Werkzeugvalidierung ist fuer die gebundene Syntax- und Fixtureoberflaeche bestanden: CPython 3.14.4, `21/21` Faelle, ein Controllerprozess, keine Fehlerpublikation, keine unerwarteten Schreibzugriffe und keine gesperrten Folgearbeiten. Keine Zielabweichung ist erkennbar.

## Vorschlag fuer den naechsten begrenzten Schritt

Als naechster Schritt ist genau eine unabhaengige statische Abnahme von `213ZT` und den drei gebundenen Ergebnisdateien vorzunehmen. Sie soll Schemas, Bindungen, `21/21` Fallresultate, Publikationszustand und Ausschlusszaehler kontrollieren. Vor dieser Abnahme sind keine Realpfad-, Manifest-, Resolver-, G2- oder Huerde-G-Arbeiten zulaessig.
