# 213ZS - Unabhaengige statische Abnahme von 213ZR

## Einordnung

`213ZS` ist eine statische Abnahme und kein Forschungslauf. Python, Controller und Werkzeug wurden nicht ausgefuehrt.

## Forschungsfrage und Auftrag

Ist das CLI-Vertragskorrekturpaket `213ZR` parserkonform, vollstaendig gebunden und auf genau einen spaeteren Controllerprozess mit fuenf frischen Zielpfaden begrenzt?

## Tatsaechlich verwendete Quellen

- juengstes Startsignal und bestehender Projektstand
- `docs/forschung/213ZR_G1_CLI_VERTRAG_KORREKTURPAKET.md`
- statisch gelesene Parserdefinition in `tests/validate_static_binary_evidence.py`
- die sechs in `213ZR` gebundenen lokalen Dateien

Keine externen Quellen wurden verwendet.

## Verwendete Dateien und Schnittstellen

Die Abnahme erfolgte ausschliesslich mit lesenden PowerShell-Datei-, Hash-, String- und Statuspruefungen. Die vorregistrierte Python-Schnittstelle wurde nicht aufgerufen.

| Rolle | Bytes | SHA-256 | Abgleich |
|---|---:|---|---|
| Interpreter | 106328 | `7CA24F26D6E3F463419EE4F537DDD3ACD312C38FE45E678CCE08572F26A8BD1A` | bestanden |
| Controller | 34044 | `433B6EA8695B6C7B6FCC2C583C7125606B00567900802F2871DA305932D1A88D` | bestanden |
| Werkzeug | 42225 | `03162A337473218ADBCAAE577DB1922A3127DD3BCE1AE3B151B0291BDAB4E286` | bestanden |
| Vertrag 213X | 13427 | `48DEB78544B8E1817E33BF01FD484EA7FBA750628CA200FE7BC9BB0147E81D63` | bestanden |
| Vertrag 213Z | 12309 | `6E6A3500295472AD8AD45DDE5A57CCE42C07307EE64D4B1734DACF9D1646E75D` | bestanden |
| Ausschlussartefakt | 6253 | `52DA5D8DD26314BF173367E7F02D1F1B1055077380E83159A0FAE3EB87304ACF` | bestanden |

## Durchgefuehrte Schritte

1. Groesse und SHA-256 aller sechs Dateibindungen wurden unabhaengig neu bestimmt.
2. Workspace- und Zielpfadstrings wurden unabhaengig als UTF-8-Bytefolgen gehasht.
3. Workspaceexistenz und Frische aller fuenf Zielpfade wurden geprueft.
4. Der einzelne Befehlsblock wurde isoliert und gegen alle 22 Pflichtoptionen der Parserdefinition abgeglichen.
5. Alte `--python-*`-Optionen und fruehere Verwendung der `213ZR`-Zielnamen wurden als Gegenbaselines gesucht.
6. Einprozessgrenze und Ausfuehrungssperre wurden geprueft.

## Messergebnisse und Gegenbaselines

| Pruefpunkt | Ergebnis |
|---|---|
| Dateibindungen | `6/6` korrekt |
| Workspacebindung | 50 UTF-8-Bytes, SHA-256 `C4DE596ECEDB6CBA69ACCFAAA5FF1A3BEE77899BE6690BC8056B0184F5268493` |
| Workspaceordner | vorhanden |
| Zielpfadbindungen | `5/5` stimmen in Laenge und SHA-256 |
| Frische Zielpfade | `5/5` nicht vorhanden |
| Pflichtoptionen des Controllers | `22/22` jeweils exakt einmal vorhanden |
| Alte `--python-exe`, `--python-size`, `--python-sha256` | `0` Treffer im Befehlsblock |
| Vorregistrierte `python.exe -B`-Befehle | exakt `1` |
| Vorgesehene Controllerprozesse | exakt `1` |
| Verwendung der `213ZR`-Zielnamen in aelteren Forschungsdokumenten | `0` Treffer |
| Ausfuehrungen | `0` |

Die unabhaengig bestaetigten Zielpfadbindungen sind:

| Ziel | UTF-8-Bytes | SHA-256 |
|---|---:|---|
| `reports/213ZR_g1_validation_temp` | 83 | `5CB3E0BE7A3872B1569D763488982171C18792D4A64DD99CA61F97AD2A05D330` |
| `reports/213ZR_g1_validation_success` | 86 | `9782E379DBEDFFD62774CA0A5A8DD9414262194A1F459109F796E7B4DA680B49` |
| `reports/213ZR_g1_validation_error` | 84 | `C3E2F092CA709B8579F9940DE95AB4F61168632E887615980D607FEBEBF1FD26` |
| `reports/.213ZR_g1_validation_success.staging` | 95 | `0BC4B0916E1E49473700C879954228F5B56A3FA8AF592B75849DA4E699551E95` |
| `reports/.213ZR_g1_validation_error.staging` | 93 | `E3E487830B765EEF60997F57F7EBCD0E07FF22AA3A8F04DE3345FCB6C1D929E1` |

## Beobachtetes Ergebnis

Alle statischen Abnahmekriterien sind erfuellt. Es wurde kein Widerspruch zwischen Parserdefinition, korrigiertem Befehlsblock, Datei- und Pfadbindungen oder aktuellem Zielstatus gefunden.

## Technische Interpretation

`213ZR` ist als korrigierte statische Ausfuehrungsvorregistrierung konsistent. Dies beseitigt den in `213ZQ` beobachteten CLI-Vertragsfehler auf Dokumentebene, belegt aber noch keinen erfolgreichen Controller- oder Werkzeuglauf.

## Grenzen und nicht gepruefte Annahmen

- Die CPython-Version wurde nicht durch Start des Interpreters geprueft.
- Syntaxanalyse und 21 synthetische Faelle wurden nicht ausgefuehrt.
- Zielpfadfrische ist eine Momentaufnahme und muss unmittelbar vor jeder spaeter freigegebenen Ausfuehrung erneut geprueft werden.
- Die 54 Realpfade wurden nicht gelesen.
- Manifest-, Resolver-, G2- und Huerde-G-Arbeiten wurden nicht durchgefuehrt.
- Es entsteht kein Befund zu Memory, Feldorganisation oder KI.

## Konkrete Schlussfolgerung

Die unabhaengige statische Abnahme von `213ZR` ist bestanden. Parserkonformitaet, Workspacebindung, unveraenderte Dateibindungen, fuenf frische neue Ziele, Nichtwiederverwendung, Einzelbefehl und Einprozessgrenze sind nachgewiesen. Keine Zielabweichung ist erkennbar.

## Vorschlag fuer den naechsten begrenzten Schritt

Als naechster Schritt kann genau eine kontrollierte Werkzeugvalidierung mit dem exakt in `213ZR` gebundenen Einzelbefehl vorgeschlagen werden. Unmittelbar vorher sind alle sechs Dateibindungen, die Workspacebindung und alle fuenf Zielstatus erneut zu pruefen. Danach darf genau ein Controllerprozess ohne Wiederholungsversuch gestartet werden; das Ergebnis ist anschliessend unabhaengig statisch zu pruefen.
