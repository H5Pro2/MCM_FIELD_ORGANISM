# 213ZR - Statisches G1-CLI-Vertragskorrekturpaket

## Einordnung

`213ZR` ist ein statisches Korrekturpaket und kein Forschungslauf. Es korrigiert ausschliesslich den in `213ZO` falsch vorregistrierten CLI-Vertrag. Python, Controller und Werkzeug wurden nicht gestartet.

## Forschungsfrage und Auftrag

Kann der in `213ZQ` belegte CLI-Vertragsfehler eng begrenzt korrigiert werden, indem die drei Interpreteroptionen an die Parserdefinition angepasst, der Workspace kanonisch gebunden und vollstaendig neue Zielpfade verwendet werden?

## Tatsaechlich verwendete Quellen

- aktueller Uebergabe-Eingang
- `docs/forschung/213ZO_G1_NEUE_STATISCHE_AUSFUEHRUNGSVORREGISTRIERUNG.md`
- `docs/forschung/213ZP_G1_213ZO_STATISCHE_ABNAHME.md`
- `docs/forschung/213ZQ_G1_WERKZEUGVALIDIERUNG_WIEDERHOLUNG_ERGEBNIS.md`
- statisch gelesene Parserdefinition in `tests/validate_static_binary_evidence.py`
- die nachfolgend direkt bytegebundenen lokalen Dateien

Keine externen Quellen wurden verwendet.

## Verwendete Dateien und Schnittstellen

| Rolle | Pfad | Bytes | SHA-256 |
|---|---|---:|---|
| Interpreter | `C:\Python314\python.exe` | 106328 | `7CA24F26D6E3F463419EE4F537DDD3ACD312C38FE45E678CCE08572F26A8BD1A` |
| Controller | `tests/validate_static_binary_evidence.py` | 34044 | `433B6EA8695B6C7B6FCC2C583C7125606B00567900802F2871DA305932D1A88D` |
| Werkzeug | `tools/static_binary_evidence.py` | 42225 | `03162A337473218ADBCAAE577DB1922A3127DD3BCE1AE3B151B0291BDAB4E286` |
| Vertrag 213X | `docs/forschung/213X_G1_WERKZEUGVALIDIERUNG_VORREGISTRIERUNG.md` | 13427 | `48DEB78544B8E1817E33BF01FD484EA7FBA750628CA200FE7BC9BB0147E81D63` |
| Vertrag 213Z | `docs/forschung/213Z_G1_WERKZEUGVALIDIERUNG_VERTRAGSKORREKTUR.md` | 12309 | `6E6A3500295472AD8AD45DDE5A57CCE42C07307EE64D4B1734DACF9D1646E75D` |
| Ausschlussartefakt | `docs/forschung/213Z_G1_REALPFAD_AUSSCHLUSSMENGE.json` | 6253 | `52DA5D8DD26314BF173367E7F02D1F1B1055077380E83159A0FAE3EB87304ACF` |

Die Parserdefinition fordert fuer die Interpreterrolle `--interpreter`, `--interpreter-size` und `--interpreter-sha256`. Sie fordert ausserdem `--workspace`. Diese vier Optionsnamen werden im korrigierten Einzelbefehl exakt verwendet.

## Kanonische Workspacebindung

Gebunden wird exakt der folgende kanonische Pfadstring als UTF-8-Bytefolge:

| Pfadstring | UTF-8-Bytes | SHA-256 des Pfadstrings | Status |
|---|---:|---|---|
| `C:/Users/TV/Documents/MCM_FIELD_ORGANISM/workspace` | 50 | `C4DE596ECEDB6CBA69ACCFAAA5FF1A3BEE77899BE6690BC8056B0184F5268493` | vorhandener Ordner |

Der CLI-Wert verwendet den dazu aequivalenten nativen Windows-Pfad `C:\Users\TV\Documents\MCM_FIELD_ORGANISM\workspace`.

## Vollstaendig neue Zielpfadbindungen

Alle Hashwerte binden exakt den dargestellten kanonischen Pfadstring als UTF-8-Bytefolge. Der gemeinsame `reports`-Elternordner ist vorhanden. Alle fuenf Ziele waren bei Erstellung von `213ZR` nicht vorhanden.

| Zweck | Kanonischer Pfadstring | UTF-8-Bytes | SHA-256 des Pfadstrings | Status |
|---|---|---:|---|---|
| Tempordner | `C:/Users/TV/Documents/MCM_FIELD_ORGANISM/workspace/reports/213ZR_g1_validation_temp` | 83 | `5CB3E0BE7A3872B1569D763488982171C18792D4A64DD99CA61F97AD2A05D330` | nicht vorhanden |
| Erfolgsordner | `C:/Users/TV/Documents/MCM_FIELD_ORGANISM/workspace/reports/213ZR_g1_validation_success` | 86 | `9782E379DBEDFFD62774CA0A5A8DD9414262194A1F459109F796E7B4DA680B49` | nicht vorhanden |
| Fehlerordner | `C:/Users/TV/Documents/MCM_FIELD_ORGANISM/workspace/reports/213ZR_g1_validation_error` | 84 | `C3E2F092CA709B8579F9940DE95AB4F61168632E887615980D607FEBEBF1FD26` | nicht vorhanden |
| Erfolgs-Stagingpfad | `C:/Users/TV/Documents/MCM_FIELD_ORGANISM/workspace/reports/.213ZR_g1_validation_success.staging` | 95 | `0BC4B0916E1E49473700C879954228F5B56A3FA8AF592B75849DA4E699551E95` | nicht vorhanden |
| Fehler-Stagingpfad | `C:/Users/TV/Documents/MCM_FIELD_ORGANISM/workspace/reports/.213ZR_g1_validation_error.staging` | 93 | `E3E487830B765EEF60997F57F7EBCD0E07FF22AA3A8F04DE3345FCB6C1D929E1` | nicht vorhanden |

Kein `213ZO`-Ziel und kein sonstiger frueherer Zielname wird wiederverwendet.

## Exakt ein korrigierter spaeterer CLI-Befehl

Der folgende Befehl ist die einzige korrigierte Vorregistrierung. Er wurde in `213ZR` nicht ausgefuehrt und darf erst nach einer unabhaengigen statischen Abnahme ausgefuehrt werden:

```powershell
& 'C:\Python314\python.exe' -B 'C:\Users\TV\Documents\MCM_FIELD_ORGANISM\workspace\tests\validate_static_binary_evidence.py' --interpreter 'C:\Python314\python.exe' --interpreter-size 106328 --interpreter-sha256 7CA24F26D6E3F463419EE4F537DDD3ACD312C38FE45E678CCE08572F26A8BD1A --runner 'C:\Users\TV\Documents\MCM_FIELD_ORGANISM\workspace\tests\validate_static_binary_evidence.py' --runner-size 34044 --runner-sha256 433B6EA8695B6C7B6FCC2C583C7125606B00567900802F2871DA305932D1A88D --tool 'C:\Users\TV\Documents\MCM_FIELD_ORGANISM\workspace\tools\static_binary_evidence.py' --tool-size 42225 --tool-sha256 03162A337473218ADBCAAE577DB1922A3127DD3BCE1AE3B151B0291BDAB4E286 --contract-x 'C:\Users\TV\Documents\MCM_FIELD_ORGANISM\workspace\docs\forschung\213X_G1_WERKZEUGVALIDIERUNG_VORREGISTRIERUNG.md' --contract-x-size 13427 --contract-x-sha256 48DEB78544B8E1817E33BF01FD484EA7FBA750628CA200FE7BC9BB0147E81D63 --contract-z 'C:\Users\TV\Documents\MCM_FIELD_ORGANISM\workspace\docs\forschung\213Z_G1_WERKZEUGVALIDIERUNG_VERTRAGSKORREKTUR.md' --contract-z-size 12309 --contract-z-sha256 6E6A3500295472AD8AD45DDE5A57CCE42C07307EE64D4B1734DACF9D1646E75D --exclusion 'C:\Users\TV\Documents\MCM_FIELD_ORGANISM\workspace\docs\forschung\213Z_G1_REALPFAD_AUSSCHLUSSMENGE.json' --exclusion-size 6253 --exclusion-sha256 52DA5D8DD26314BF173367E7F02D1F1B1055077380E83159A0FAE3EB87304ACF --workspace 'C:\Users\TV\Documents\MCM_FIELD_ORGANISM\workspace' --temp-dir 'C:\Users\TV\Documents\MCM_FIELD_ORGANISM\workspace\reports\213ZR_g1_validation_temp' --success-dir 'C:\Users\TV\Documents\MCM_FIELD_ORGANISM\workspace\reports\213ZR_g1_validation_success' --error-dir 'C:\Users\TV\Documents\MCM_FIELD_ORGANISM\workspace\reports\213ZR_g1_validation_error'
```

Die beiden Stagingpfade werden vom gebundenen Controller aus den Endpfaden mit fuehrendem Punkt abgeleitet. Es ist kein weiterer Vor- oder Nachbereitungsbefehl vorgesehen. Genau ein Controllerprozess ist gebunden.

## Durchgefuehrte Schritte

1. Die CLI-Pflichtargumente wurden statisch aus der gebundenen Parserdefinition gelesen.
2. Die drei falschen `--python-*`-Optionsnamen wurden ausschliesslich im neu vorregistrierten Befehl durch die geforderten `--interpreter*`-Namen ersetzt.
3. `--workspace` wurde kanonisch pfadgebunden ergaenzt.
4. Fuenf neue `213ZR`-Ziele wurden einschliesslich Stringlaenge, SHA-256 und Status gebunden.
5. Genau ein korrigierter spaeterer Einzelbefehl wurde dokumentiert.

## Messergebnisse und Gegenbaselines

- Unveraenderte Dateibindungen: `6/6` stimmen.
- Geforderte Interpreteroptionen im korrigierten Befehl: `3/3` vorhanden.
- Alte `--python-exe`, `--python-size`, `--python-sha256` im korrigierten Befehl: `0/3` vorhanden.
- `--workspace`: exakt einmal vorhanden und kanonisch gebunden.
- Neue Zielpfade: `5/5` nicht vorhanden.
- Treffer der `213ZR`-Zielnamen in aelteren Forschungsdokumenten: `0`.
- Vorregistrierte spaetere `python.exe -B`-Befehle: exakt `1`.
- Vorgesehene Controllerprozesse: exakt `1`.
- Ausfuehrungen, Syntaxanalysen und synthetische Faelle in `213ZR`: jeweils `0`.

Gegenbaseline ist der fehlerhafte `213ZO`-Befehl: Dort standen drei `--python-*`-Optionen, und `--workspace` fehlte. Diese vier CLI-Vertragsabweichungen sind im neuen Befehl korrigiert; sonstige Dateirollen und Bindungswerte bleiben unveraendert.

## Grenzen und nicht gepruefte Annahmen

- Dieses statische Paket belegt nicht, dass Controller oder Werkzeug erfolgreich laufen.
- Die CPython-Version wurde nicht durch Ausfuehrung geprueft.
- Die Zielpfadfrische ist vor einer spaeteren Ausfuehrung erneut zu pruefen.
- Die 54 Realpfade wurden nicht gelesen und sind keine Eingaben dieses Schritts.
- Manifest-, Resolver-, G2- und Huerde-G-Arbeiten wurden nicht durchgefuehrt.
- Es entsteht kein Befund zu Memory, Feldorganisation oder KI.

## Konkrete Schlussfolgerung

Der in `213ZQ` belegte CLI-Vertragsfehler ist im statischen Korrekturpaket eng begrenzt adressiert. Der korrigierte Einzelbefehl verwendet die vier vom Controller geforderten Bindungen und vollstaendig neue Zielpfade. Daraus folgt noch keine Ausfuehrungsfreigabe. Keine Zielabweichung ist erkennbar.

## Vorschlag fuer den naechsten begrenzten Schritt

Als naechster Schritt ist genau eine unabhaengige statische Abnahme von `213ZR` vorzunehmen. Sie soll insbesondere die Parserkonformitaet aller Optionsnamen, die Workspacebindung, die unveraenderten Dateibindungen, `5/5` frische Ziele, die Nichtwiederverwendung und exakt einen Einprozessbefehl pruefen. Bis zu einer bestandenen Abnahme darf keine weitere Werkzeugvalidierung gestartet werden.
