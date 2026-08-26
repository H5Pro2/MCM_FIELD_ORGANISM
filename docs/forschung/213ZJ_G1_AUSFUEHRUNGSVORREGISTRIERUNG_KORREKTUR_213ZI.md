# 213ZJ - Korrektur der Ausfuehrungsvorregistrierung

## Einordnung und Vorrang

`213ZJ` ist ein statisches Korrekturpaket und kein Forschungslauf. Es korrigiert ausschliesslich die zwei Pfadbefunde aus `213ZI` an der Ausfuehrungsvorregistrierung `213ZH`.

Die unveraenderten Bytebindungen, Ausschlussregeln, Stopplinien und Grenzen aus `213ZH` gelten fort. Bei Widerspruch haben ausschliesslich die in `213ZJ` neu gebundenen Zielpfade und der korrigierte CLI-Befehl Vorrang.

Es erfolgten keine Syntaxpruefung, kein Test, keine Controller- oder Werkzeugausfuehrung und kein Zugriff auf einen der 54 Realpfade. Es wurden keine Ziel- oder Stagingordner erzeugt.

## Forschungsfrage und Auftrag

Kann `213ZH` so eng korrigiert werden, dass der Temporaerordner einen vorhandenen Elternordner besitzt, die beiden Stagingpfade exakt der Controllerableitung entsprechen und weiterhin genau ein spaeterer CLI-Befehl vorregistriert bleibt?

## Tatsaechlich verwendete Quellen

- aktueller freigegebener Uebergabe-Eingang,
- `docs/forschung/213ZH_G1_STATISCHE_AUSFUEHRUNGSVORREGISTRIERUNG.md`,
- `docs/forschung/213ZI_G1_UNABHAENGIGE_STATISCHE_ABNAHME_213ZH.md`,
- `tests/validate_static_binary_evidence.py` ausschliesslich statisch,
- der vorhandene Workspace-Elternordner `reports` und die fuenf korrigierten Zielpfade ausschliesslich fuer Pfadstatuspruefungen.

Keine externe Quelle wurde verwendet.

## Unveraenderte Bindungen

Die folgenden direkten Bindungen aus `213ZH` bleiben unveraendert:

| Rolle | Bytes | SHA-256 |
|---|---:|---|
| `C:/Python314/python.exe` | 106.328 | `7CA24F26D6E3F463419EE4F537DDD3ACD312C38FE45E678CCE08572F26A8BD1A` |
| `tests/validate_static_binary_evidence.py` | 34.044 | `76CF80B8C62EB73DC9702ED54F364D513B171BC7BF3B61642D83C14EE497E784` |
| `tools/static_binary_evidence.py` | 42.225 | `03162A337473218ADBCAAE577DB1922A3127DD3BCE1AE3B151B0291BDAB4E286` |
| `docs/forschung/213X_G1_WERKZEUGVALIDIERUNG_VORREGISTRIERUNG.md` | 13.427 | `48DEB78544B8E1817E33BF01FD484EA7FBA750628CA200FE7BC9BB0147E81D63` |
| `docs/forschung/213Z_G1_WERKZEUGVALIDIERUNG_VERTRAGSKORREKTUR.md` | 12.309 | `6E6A3500295472AD8AD45DDE5A57CCE42C07307EE64D4B1734DACF9D1646E75D` |
| `docs/forschung/213Z_G1_REALPFAD_AUSSCHLUSSMENGE.json` | 6.253 | `52DA5D8DD26314BF173367E7F02D1F1B1055077380E83159A0FAE3EB87304ACF` |

Auch die fortgeltenden Abnahmebindungen `213ZA` und `213ZG` bleiben unveraendert. `213ZH` ist gebunden an 10.284 Bytes und SHA-256 `6AE7A4F4AAC2F9C605A92D4E605531B8A23ECF4A1E1BC1AAF4A08D1959665127`; der festgestellte Korrekturbedarf ist gebunden durch `213ZI` mit 8.473 Bytes und SHA-256 `0877D57308F1EF2BD6051A91F57ADAE3DC807982ECD5219ABBC9FE74F90FAD5A`.

## Korrigierte Zielpfadbindung

Kodierungsregel: Jeder kanonische Pfadstring wird exakt wie in der Tabelle, mit `/` als Separator, ohne Anfuehrungszeichen und ohne abschliessenden Zeilenumbruch in UTF-8 kodiert. `UTF-8 Bytes` und SHA-256 binden diese Stringdarstellung, nicht den Inhalt einer Zieldatei. Die Ziele existieren bei dieser Vorregistrierung noch nicht und besitzen daher keine Dateibytes.

Der gemeinsame Elternordner

`C:/Users/TV/Documents/MCM_FIELD_ORGANISM/workspace/reports`

ist beobachtet vorhanden und ein Verzeichnis.

| Rolle | Kanonischer Pfadstring | UTF-8 Bytes | SHA-256 des Pfadstrings | Status |
|---|---|---:|---|---|
| Temporaerordner | `C:/Users/TV/Documents/MCM_FIELD_ORGANISM/workspace/reports/213ZH_g1_validation_temp` | 83 | `EB69B89B1A8A92ECD00169D89602A73974BC70174D71724A169F6FF676607EE4` | nicht vorhanden |
| Erfolgsordner | `C:/Users/TV/Documents/MCM_FIELD_ORGANISM/workspace/reports/213ZH_g1_validation_success` | 86 | `7B8E72C48D50A293806967E669B8BDBE6A1AE66E28325DE25673B9027FA91A4E` | nicht vorhanden |
| Fehlerordner | `C:/Users/TV/Documents/MCM_FIELD_ORGANISM/workspace/reports/213ZH_g1_validation_error` | 84 | `824A57B5C5C3C8AEEE6A428D4918629ECE1069621C7AAF15FAC49FC990FFEF86` | nicht vorhanden |
| Erfolgs-Staging | `C:/Users/TV/Documents/MCM_FIELD_ORGANISM/workspace/reports/.213ZH_g1_validation_success.staging` | 95 | `091CECC6A4C7F74354539DB64DF5470867265F1D7E1F42938E9B2557A94D5B7A` | nicht vorhanden |
| Fehler-Staging | `C:/Users/TV/Documents/MCM_FIELD_ORGANISM/workspace/reports/.213ZH_g1_validation_error.staging` | 93 | `EEDECCF7ACAACFA17295E711E1CBEECAB6D2424E056996CF7A20EA200C856B0A` | nicht vorhanden |

Die beiden Stagingnamen folgen exakt der statisch sichtbaren Controllerableitung aus dem Elternordner des Finalziels und `f".{name}.staging"`. Alle fuenf Pfade muessen unmittelbar vor einem spaeteren Lauf weiterhin fehlen. Der Elternordner `reports` muss weiterhin als Verzeichnis vorhanden sein.

## Korrigierter einzelner CLI-Befehl

Der in `213ZH` vorregistrierte CLI-Befehl wird vollstaendig durch genau diesen einen Befehl ersetzt:

```powershell
& 'C:\Python314\python.exe' -B 'C:\Users\TV\Documents\MCM_FIELD_ORGANISM\workspace\tests\validate_static_binary_evidence.py' --runner 'C:\Users\TV\Documents\MCM_FIELD_ORGANISM\workspace\tests\validate_static_binary_evidence.py' --runner-size 34044 --runner-sha256 76CF80B8C62EB73DC9702ED54F364D513B171BC7BF3B61642D83C14EE497E784 --tool 'C:\Users\TV\Documents\MCM_FIELD_ORGANISM\workspace\tools\static_binary_evidence.py' --tool-size 42225 --tool-sha256 03162A337473218ADBCAAE577DB1922A3127DD3BCE1AE3B151B0291BDAB4E286 --contract-x 'C:\Users\TV\Documents\MCM_FIELD_ORGANISM\workspace\docs\forschung\213X_G1_WERKZEUGVALIDIERUNG_VORREGISTRIERUNG.md' --contract-x-size 13427 --contract-x-sha256 48DEB78544B8E1817E33BF01FD484EA7FBA750628CA200FE7BC9BB0147E81D63 --contract-z 'C:\Users\TV\Documents\MCM_FIELD_ORGANISM\workspace\docs\forschung\213Z_G1_WERKZEUGVALIDIERUNG_VERTRAGSKORREKTUR.md' --contract-z-size 12309 --contract-z-sha256 6E6A3500295472AD8AD45DDE5A57CCE42C07307EE64D4B1734DACF9D1646E75D --exclusion 'C:\Users\TV\Documents\MCM_FIELD_ORGANISM\workspace\docs\forschung\213Z_G1_REALPFAD_AUSSCHLUSSMENGE.json' --exclusion-size 6253 --exclusion-sha256 52DA5D8DD26314BF173367E7F02D1F1B1055077380E83159A0FAE3EB87304ACF --interpreter 'C:\Python314\python.exe' --interpreter-size 106328 --interpreter-sha256 7CA24F26D6E3F463419EE4F537DDD3ACD312C38FE45E678CCE08572F26A8BD1A --workspace 'C:\Users\TV\Documents\MCM_FIELD_ORGANISM\workspace' --temp-dir 'C:\Users\TV\Documents\MCM_FIELD_ORGANISM\workspace\reports\213ZH_g1_validation_temp' --success-dir 'C:\Users\TV\Documents\MCM_FIELD_ORGANISM\workspace\reports\213ZH_g1_validation_success' --error-dir 'C:\Users\TV\Documents\MCM_FIELD_ORGANISM\workspace\reports\213ZH_g1_validation_error'
```

Die Stagingpfade sind keine CLI-Argumente. Sie werden deterministisch aus `--success-dir` und `--error-dir` abgeleitet und sind deshalb separat in der Fuenfermenge gebunden. Es gibt keinen zweiten Python-Aufruf, keinen vorgelagerten Verzeichniserzeugungsbefehl und keinen Nachbearbeitungsbefehl.

## Durchgefuehrte Schritte und Messergebnisse

1. Der vorhandene Elternordner `reports` wurde als Verzeichnis bestaetigt.
2. Ein neuer Temporaerpfad direkt unter `reports` wurde festgelegt.
3. Die zwei Stagingnamen wurden mit dem fuehrenden Punkt an die Controllerableitung angeglichen.
4. Alle fuenf kanonischen Pfadstrings wurden ueber UTF-8-Laenge und SHA-256 gebunden und auf Nichtexistenz geprueft.
5. Im einzigen spaeteren CLI-Befehl wurde ausschliesslich `--temp-dir` korrigiert; Erfolgs- und Fehlerfinalziel sowie alle Dateibindungen blieben unveraendert.

Beobachtetes Ergebnis: Der Elternordner ist vorhanden; die korrigierte Fuenfermenge ist `5/5` nicht vorhanden. Der Befehlssatz enthaelt genau einen spaeteren `python.exe -B`-Aufruf.

Gegenbaseline sind der nicht erzeugbare `.tmp`-Pfad und die zwei Stagingnamen ohne fuehrenden Punkt aus `213ZH`. Keiner dieser drei fehlerhaften Strings gilt unter `213ZJ` fort.

## Grenzen und nicht gepruefte Annahmen

- Python-Syntax, CLI-Parser und Interpreterversion wurden nicht ausgefuehrt.
- Controller, Werkzeug und 21 Fixturefaelle wurden nicht ausgefuehrt.
- Der Status der fuenf Zielpfade kann sich nach der Dokumentation aendern und muss vor einem spaeteren Lauf erneut statisch geprueft werden.
- Die 54 Realpfade wurden nicht geoeffnet oder auf Existenz geprueft.
- Es erfolgte keine Manifest-, Resolver-, G2- oder Huerde-G-Arbeit.
- Aus dieser Korrektur folgt kein Validierungsergebnis und kein Nachweis einer MCM-Funktion.

## Konkrete Schlussfolgerung

Die zwei Pfadbefunde aus `213ZI` sind im statischen Vertragsstand korrigiert. `213ZJ` ist weiterhin keine Ausfuehrungsfreigabe. G1 bleibt nicht bestanden, G0 bleibt abhaengig und Huerde G bleibt gesperrt. Eine Zielabweichung ist nicht erkennbar.

## Vorschlag fuer den naechsten begrenzten Schritt

Als naechstes ist genau eine unabhaengige statische Abnahme von `213ZJ` zusammen mit den fortgeltenden Teilen aus `213ZH` vorzunehmen. Besonders zu pruefen sind der vorhandene `reports`-Elternordner, die Nichtexistenz aller fuenf korrigierten Pfade, die beiden Stagingnamen mit fuehrendem Punkt, die unveraenderten Dateibindungen und genau ein korrigierter CLI-Befehl. Weiterhin nicht freigegeben sind Syntaxpruefung, Tests, Controller- oder Werkzeugausfuehrung, Zugriff auf die 54 Realpfade, Manifest-, Resolver-, G2- und Huerde-G-Arbeit.
