# 213ZP - Unabhaengige statische Abnahme von 213ZO

## Einordnung

`213ZP` ist eine unabhaengige statische Abnahme und kein Forschungslauf. Weder Python noch Controller oder Werkzeug wurden ausgefuehrt. Es gab keine Syntaxanalyse und keinen Zugriff auf die 54 Realpfade.

## Forschungsfrage und Auftrag

Ist die Ausfuehrungsvorregistrierung `213ZO` intern konsistent, vollstaendig byte- und pfadgebunden und auf genau einen spaeteren Controllerprozess mit fuenf frischen Zielpfaden begrenzt?

## Tatsaechlich verwendete Quellen

- aktueller Uebergabe-Eingang
- `docs/forschung/213ZO_G1_NEUE_STATISCHE_AUSFUEHRUNGSVORREGISTRIERUNG.md`
- `docs/forschung/213ZN_G1_ZWEISCHLUESSELKORREKTUR_STATISCHE_ABNAHME.md`
- die sechs in `213ZO` gebundenen lokalen Dateien
- statisch gelesene Stagingableitung in `tests/validate_static_binary_evidence.py`

Keine externen Quellen wurden verwendet.

## Verwendete Dateien und Schnittstellen

Die Abnahme verwendete ausschliesslich lokale, lesende PowerShell-Datei- und Stringpruefungen. Die vorregistrierte Python-Schnittstelle wurde nicht aufgerufen.

| Rolle | Beobachtete Bytes | Beobachtete SHA-256 | Abgleich mit 213ZO |
|---|---:|---|---|
| `C:\Python314\python.exe` | 106328 | `7CA24F26D6E3F463419EE4F537DDD3ACD312C38FE45E678CCE08572F26A8BD1A` | bestanden |
| `tests/validate_static_binary_evidence.py` | 34044 | `433B6EA8695B6C7B6FCC2C583C7125606B00567900802F2871DA305932D1A88D` | bestanden |
| `tools/static_binary_evidence.py` | 42225 | `03162A337473218ADBCAAE577DB1922A3127DD3BCE1AE3B151B0291BDAB4E286` | bestanden |
| Vertrag `213X` | 13427 | `48DEB78544B8E1817E33BF01FD484EA7FBA750628CA200FE7BC9BB0147E81D63` | bestanden |
| Vertrag `213Z` | 12309 | `6E6A3500295472AD8AD45DDE5A57CCE42C07307EE64D4B1734DACF9D1646E75D` | bestanden |
| Realpfad-Ausschlussartefakt | 6253 | `52DA5D8DD26314BF173367E7F02D1F1B1055077380E83159A0FAE3EB87304ACF` | bestanden |

## Durchgefuehrte Schritte

1. `213ZO` wurde vollstaendig statisch gelesen.
2. Groesse und SHA-256 aller sechs gebundenen Dateien wurden unabhaengig neu bestimmt.
3. UTF-8-Laenge und SHA-256 aller fuenf kanonischen Zielpfadstrings wurden unabhaengig neu bestimmt.
4. Das aktuelle Nichtvorhandensein aller fuenf Ziele und das Vorhandensein des `reports`-Elternordners wurden geprueft.
5. Aeltere Forschungsdokumente wurden nach den neuen `213ZO`-Zielnamen durchsucht.
6. Die Stagingableitung des Controllers wurde statisch an den Zeilen mit `f".{args.success_dir.name}.staging"` und `f".{args.error_dir.name}.staging"` kontrolliert.
7. Anzahl und Struktur des vorregistrierten CLI-Befehls sowie die Einprozessgrenze wurden geprueft.

## Messergebnisse und Gegenbaselines

| Pruefpunkt | Ergebnis |
|---|---|
| Dateibindungen | `6/6` stimmen in Groesse und SHA-256 |
| Controllerbindung | `433B6EA8695B6C7B6FCC2C583C7125606B00567900802F2871DA305932D1A88D`, bestanden |
| Zielpfadstring-Bindungen | `5/5` stimmen in UTF-8-Laenge und SHA-256 |
| Frische Zielpfade | `5/5` nicht vorhanden |
| `reports`-Elternordner | vorhanden |
| Treffer der neuen Zielnamen in aelteren Forschungsdokumenten | `0` |
| Vorregistrierte `python.exe -B`-Befehle | exakt `1` |
| `--runner`, `--temp-dir`, `--success-dir`, `--error-dir` | jeweils exakt `1` im Befehlsblock |
| Vorgesehene Controllerprozesse | exakt `1` |
| Stagingnamen | beide mit fuehrendem Punkt korrekt aus den Endpfaden abgeleitet |
| Frueherer Fehlerordner `reports/213ZH_g1_validation_error` | vorhanden, weder Eingabe noch Ziel |
| Python-, Controller- oder Werkzeugausfuehrungen | `0` |
| Realpfadzugriffe | `0` |

Die unabhaengig berechneten Pfadbindungen lauten:

| Zweck | UTF-8-Bytes | SHA-256 |
|---|---:|---|
| `reports/213ZO_g1_validation_temp` | 83 | `01CA6A09A710BC4036EB5B4E2A102D161537DDD54D37E7DCC5F425BA949E7A8A` |
| `reports/213ZO_g1_validation_success` | 86 | `7E82A94123F628877A358B83A4DB34C69346AB02BC0AA7E88808EA70FC61A8F2` |
| `reports/213ZO_g1_validation_error` | 84 | `65FF75C3122D4C1D4F0FE93F6EE9116D024751FAEE120C250CE293AC4B4F1870` |
| `reports/.213ZO_g1_validation_success.staging` | 95 | `5B45363273AD5966AE9C36F267CB806B9B74E8A0A5967FE565E977ACF517C060` |
| `reports/.213ZO_g1_validation_error.staging` | 93 | `6013F2A8E5AD39CB38B7E35F712A782389B4403589DC5B365AEE2B964F2EB44A` |

## Beobachtetes Ergebnis

Alle freigegebenen statischen Abnahmekriterien sind erfuellt. Es wurde kein abnahmehemmender Widerspruch zwischen Dokument, lokalen Dateien, Controller-Stagingableitung und aktuellem Dateisystemstatus gefunden.

## Technische Interpretation

`213ZO` ist als statische Vorregistrierung konsistent und aus technischer Sicht fuer eine gesonderte Entscheidung ueber genau eine kontrollierte Wiederholung der Werkzeugvalidierung geeignet. Diese Interpretation ist kein Nachweis, dass die Validierung erfolgreich sein wird.

## Grenzen und nicht gepruefte Annahmen

- Die CPython-Versionsannahme wurde nicht durch Start des Interpreters geprueft.
- Controller- und Werkzeugsyntax sowie die 21 synthetischen Faelle wurden nicht ausgefuehrt.
- Die Zielpfadfrische ist eine Momentaufnahme und muss unmittelbar vor einer spaeter freigegebenen Ausfuehrung erneut geprueft werden.
- Die 54 Realpfade wurden nicht gelesen.
- Manifest-, Resolver-, G2- und Huerde-G-Arbeiten waren nicht Bestandteil der Abnahme.
- Es entsteht kein Forschungsbefund zu Memory, Feldorganisation oder KI.

## Konkrete Schlussfolgerung

Die unabhaengige statische Abnahme von `213ZO` ist bestanden. Die Controller-SHA, alle weiteren Dateibindungen, alle fuenf Pfadbindungen, deren Frische, die Nichtwiederverwendung, der vorhandene Elternordner, der Einzelbefehl und die Einprozessgrenze sind konsistent. Keine Zielabweichung ist erkennbar.

## Vorschlag fuer den naechsten begrenzten Schritt

Als naechster Schritt kann genau eine kontrollierte Wiederholung der Werkzeugvalidierung vorgeschlagen werden. Vor dem Start sind die sechs Dateibindungen und alle fuenf Zielstatus unmittelbar erneut zu pruefen; danach darf ausschliesslich der exakt in `213ZO` gebundene einzelne `python.exe -B`-Befehl in genau einem Controllerprozess ausgefuehrt werden. Das Ergebnis ist anschliessend unabhaengig statisch zu pruefen.
