# 213ZO - Neue statische G1-Ausfuehrungsvorregistrierung

## Einordnung

`213ZO` ist eine statische Ausfuehrungsvorregistrierung und kein Forschungslauf. Dieses Dokument fuehrt weder den Controller noch das Werkzeug aus und nimmt keine Syntaxanalyse oder synthetische Fallpruefung vor.

## Forschungsfrage und Auftrag

Kann eine neue, eindeutig gebundene Einzel-Ausfuehrung fuer die Werkzeugvalidierung vorregistriert werden, nachdem die Zweischluesselkorrektur des Controllers in `213ZN` statisch abgenommen wurde, ohne bisherige Zielnamen wiederzuverwenden?

Der Auftrag ist auf die Bindung der unveraenderten Eingaben, der korrigierten Controllerdatei und fuenf vollstaendig neuer Ausgabeziele begrenzt.

## Tatsaechlich verwendete Quellen

- aktueller Uebergabe-Eingang mit der Freigabe fuer genau eine neue statische Ausfuehrungsvorregistrierung
- `docs/forschung/213ZN_G1_ZWEISCHLUESSELKORREKTUR_STATISCHE_ABNAHME.md`
- `docs/forschung/213ZM_G1_CONTROLLER_ZWEISCHLUESSELKORREKTUR.md`
- `docs/forschung/213ZL_G1_WERKZEUGVALIDIERUNG_ERGEBNIS.md`
- die nachfolgend direkt bytegebundenen lokalen Dateien

Keine externen Quellen wurden verwendet.

## Verwendete Dateien und Schnittstellen

| Rolle | Pfad | Groesse in Bytes | SHA-256 |
|---|---|---:|---|
| CPython-Interpreter | `C:\Python314\python.exe` | 106328 | `7CA24F26D6E3F463419EE4F537DDD3ACD312C38FE45E678CCE08572F26A8BD1A` |
| Controller | `tests/validate_static_binary_evidence.py` | 34044 | `433B6EA8695B6C7B6FCC2C583C7125606B00567900802F2871DA305932D1A88D` |
| Werkzeug | `tools/static_binary_evidence.py` | 42225 | `03162A337473218ADBCAAE577DB1922A3127DD3BCE1AE3B151B0291BDAB4E286` |
| Vertrag 213X | `docs/forschung/213X_G1_WERKZEUGVALIDIERUNG_VORREGISTRIERUNG.md` | 13427 | `48DEB78544B8E1817E33BF01FD484EA7FBA750628CA200FE7BC9BB0147E81D63` |
| Vertrag 213Z | `docs/forschung/213Z_G1_WERKZEUGVALIDIERUNG_VERTRAGSKORREKTUR.md` | 12309 | `6E6A3500295472AD8AD45DDE5A57CCE42C07307EE64D4B1734DACF9D1646E75D` |
| Ausschlussartefakt | `docs/forschung/213Z_G1_REALPFAD_AUSSCHLUSSMENGE.json` | 6253 | `52DA5D8DD26314BF173367E7F02D1F1B1055077380E83159A0FAE3EB87304ACF` |

Die einzige vorregistrierte Ausfuehrungsschnittstelle ist der unten festgeschriebene Aufruf von `python.exe -B`. Es ist genau ein Controllerprozess vorgesehen. Syntaxanalyse und die 21 synthetischen Faelle duerfen nur innerhalb dieses Prozesses stattfinden.

## Neue Zielpfadbindungen

Die Hashwerte binden jeweils exakt den dargestellten kanonischen Pfadstring als UTF-8-Bytefolge. Alle fuenf Ziele waren bei der statischen Vorpruefung nicht vorhanden. Der gemeinsame Elternordner `C:/Users/TV/Documents/MCM_FIELD_ORGANISM/workspace/reports` war vorhanden.

| Zweck | Kanonischer Pfadstring | UTF-8-Bytes | SHA-256 des Pfadstrings | Status |
|---|---|---:|---|---|
| Tempordner | `C:/Users/TV/Documents/MCM_FIELD_ORGANISM/workspace/reports/213ZO_g1_validation_temp` | 83 | `01CA6A09A710BC4036EB5B4E2A102D161537DDD54D37E7DCC5F425BA949E7A8A` | nicht vorhanden |
| Erfolgsordner | `C:/Users/TV/Documents/MCM_FIELD_ORGANISM/workspace/reports/213ZO_g1_validation_success` | 86 | `7E82A94123F628877A358B83A4DB34C69346AB02BC0AA7E88808EA70FC61A8F2` | nicht vorhanden |
| Fehlerordner | `C:/Users/TV/Documents/MCM_FIELD_ORGANISM/workspace/reports/213ZO_g1_validation_error` | 84 | `65FF75C3122D4C1D4F0FE93F6EE9116D024751FAEE120C250CE293AC4B4F1870` | nicht vorhanden |
| Erfolgs-Stagingpfad | `C:/Users/TV/Documents/MCM_FIELD_ORGANISM/workspace/reports/.213ZO_g1_validation_success.staging` | 95 | `5B45363273AD5966AE9C36F267CB806B9B74E8A0A5967FE565E977ACF517C060` | nicht vorhanden |
| Fehler-Stagingpfad | `C:/Users/TV/Documents/MCM_FIELD_ORGANISM/workspace/reports/.213ZO_g1_validation_error.staging` | 93 | `6013F2A8E5AD39CB38B7E35F712A782389B4403589DC5B365AEE2B964F2EB44A` | nicht vorhanden |

Der bestehende fruehere Fehlerordner `reports/213ZH_g1_validation_error` bleibt vorhanden und unveraendert. Kein Zielname aus einer frueheren Vorregistrierung wird wiederverwendet.

## Exakt ein spaeterer CLI-Befehl

Der folgende Befehl ist der einzige vorregistrierte spaetere Aufruf. Er wurde in `213ZO` nicht ausgefuehrt:

```powershell
& 'C:\Python314\python.exe' -B 'C:\Users\TV\Documents\MCM_FIELD_ORGANISM\workspace\tests\validate_static_binary_evidence.py' --python-exe 'C:\Python314\python.exe' --python-size 106328 --python-sha256 7CA24F26D6E3F463419EE4F537DDD3ACD312C38FE45E678CCE08572F26A8BD1A --runner 'C:\Users\TV\Documents\MCM_FIELD_ORGANISM\workspace\tests\validate_static_binary_evidence.py' --runner-size 34044 --runner-sha256 433B6EA8695B6C7B6FCC2C583C7125606B00567900802F2871DA305932D1A88D --tool 'C:\Users\TV\Documents\MCM_FIELD_ORGANISM\workspace\tools\static_binary_evidence.py' --tool-size 42225 --tool-sha256 03162A337473218ADBCAAE577DB1922A3127DD3BCE1AE3B151B0291BDAB4E286 --contract-x 'C:\Users\TV\Documents\MCM_FIELD_ORGANISM\workspace\docs\forschung\213X_G1_WERKZEUGVALIDIERUNG_VORREGISTRIERUNG.md' --contract-x-size 13427 --contract-x-sha256 48DEB78544B8E1817E33BF01FD484EA7FBA750628CA200FE7BC9BB0147E81D63 --contract-z 'C:\Users\TV\Documents\MCM_FIELD_ORGANISM\workspace\docs\forschung\213Z_G1_WERKZEUGVALIDIERUNG_VERTRAGSKORREKTUR.md' --contract-z-size 12309 --contract-z-sha256 6E6A3500295472AD8AD45DDE5A57CCE42C07307EE64D4B1734DACF9D1646E75D --exclusion 'C:\Users\TV\Documents\MCM_FIELD_ORGANISM\workspace\docs\forschung\213Z_G1_REALPFAD_AUSSCHLUSSMENGE.json' --exclusion-size 6253 --exclusion-sha256 52DA5D8DD26314BF173367E7F02D1F1B1055077380E83159A0FAE3EB87304ACF --temp-dir 'C:\Users\TV\Documents\MCM_FIELD_ORGANISM\workspace\reports\213ZO_g1_validation_temp' --success-dir 'C:\Users\TV\Documents\MCM_FIELD_ORGANISM\workspace\reports\213ZO_g1_validation_success' --error-dir 'C:\Users\TV\Documents\MCM_FIELD_ORGANISM\workspace\reports\213ZO_g1_validation_error'
```

Die beiden Stagingpfade werden vom gebundenen Controller aus den Erfolgs- und Fehlerpfaden abgeleitet. Es ist kein vorbereitender oder nachgelagerter CLI-Befehl vorregistriert.

## Durchgefuehrte Schritte

1. Die in `213ZN` abgenommene Controllerbindung wurde uebernommen.
2. Interpreter, Controller, Werkzeug, Vertraege und Ausschlussartefakt wurden statisch bytegebunden.
3. Fuenf neue Zielpfade unter dem vorhandenen `reports`-Elternordner wurden festgelegt.
4. UTF-8-Laenge, SHA-256 und Nichtvorhandensein jedes Zielpfadstrings wurden gebunden.
5. Genau ein spaeterer Einprozessaufruf wurde dokumentiert.

## Messergebnisse und Gegenbaselines

- Neue Zielpfade: `5/5` bei der Vorpruefung nicht vorhanden.
- Vorhandener Elternordner: `1/1` vorhanden.
- Vorregistrierte spaetere CLI-Aufrufe: exakt `1`.
- Vorgesehene Controllerprozesse: exakt `1`.
- Wiederverwendete fruehere Zielnamen: `0`.
- Controller-SHA-256 entspricht der in `213ZN` abgenommenen Korrekturbindung: ja.
- Gegenbaseline frueherer Fehlerordner: `reports/213ZH_g1_validation_error` ist weiterhin vorhanden und wird weder als Eingabe noch als Ziel verwendet.
- Realpfadzugriffe, Syntaxanalyse, synthetische Faelle und Werkzeugausfuehrungen in `213ZO`: jeweils `0`.

## Grenzen und nicht gepruefte Annahmen

- Diese Vorregistrierung belegt nicht, dass der Controller oder das Werkzeug erfolgreich laeuft.
- Die CPython-Versionsannahme und die semantische Eignung der gebundenen Dateien werden hier nicht durch Ausfuehrung geprueft.
- Die 54 Realpfade wurden nicht gelesen und sind keine Eingaben dieses Schritts.
- Manifest-, Resolver-, G2- und Huerde-G-Arbeiten wurden nicht durchgefuehrt.
- Die spaetere Frische der Zielpfade muss unmittelbar vor einer etwaigen Ausfuehrung erneut geprueft werden.

## Konkrete Schlussfolgerung

Die korrigierte Controllerdatei und fuenf neue, aktuell frische Zielpfade sind fuer genau einen moeglichen spaeteren Controlleraufruf statisch vorregistriert. Daraus folgt keine Ausfuehrungsfreigabe und kein Forschungsbefund. Eine Zielabweichung ist nicht erkennbar.

## Vorschlag fuer den naechsten begrenzten Schritt

Als naechster Schritt ist genau eine unabhaengige statische Abnahme von `213ZO` vorzunehmen. Sie soll die Datei- und Pfadbindungen, die Frische aller fuenf Ziele, die Einprozessgrenze und den exakt einen CLI-Befehl pruefen. Bis zu einer bestandenen Abnahme darf die Werkzeugvalidierung nicht wiederholt werden.
