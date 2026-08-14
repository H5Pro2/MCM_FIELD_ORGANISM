# 213ZI - Unabhaengige statische Abnahme von 213ZH

## Einordnung

`213ZI` ist eine statische Abnahme und kein Forschungslauf. Geprueft wurde ausschliesslich die Ausfuehrungsvorregistrierung `213ZH` gegen ihre Bytebindungen, die statisch sichtbare Controller-CLI und die freigegebenen Ausschlussgrenzen.

Es erfolgten keine Syntaxpruefung, kein Test, keine Controller- oder Werkzeugausfuehrung und kein Zugriff auf einen der 54 Realpfade. Es wurden keine Ziel-, Staging-, Fixture-, Manifest- oder Resolverdateien erzeugt.

## Forschungsfrage und Auftrag

Ist `213ZH` byte-, versions-, befehls- und pfadseitig eindeutig genug gebunden, um nach einer gesonderten Freigabe genau einen kontrollierten `python.exe -B`-Controllerprozess zu starten, ohne Realpfade als Eingaben oder unbeabsichtigte Ausgabeziele zu verwenden?

## Tatsaechlich verwendete Quellen

- aktueller freigegebener Uebergabe-Eingang,
- `docs/forschung/213ZH_G1_STATISCHE_AUSFUEHRUNGSVORREGISTRIERUNG.md`,
- `docs/forschung/213X_G1_WERKZEUGVALIDIERUNG_VORREGISTRIERUNG.md`,
- `docs/forschung/213Z_G1_WERKZEUGVALIDIERUNG_VERTRAGSKORREKTUR.md`,
- `docs/forschung/213ZA_G1_UNABHAENGIGE_STATISCHE_ABNAHME_213Z.md`,
- `docs/forschung/213ZG_G1_UNABHAENGIGE_STATISCHE_ABNAHME_213ZF.md`,
- `docs/forschung/213Z_G1_REALPFAD_AUSSCHLUSSMENGE.json`,
- `tests/validate_static_binary_evidence.py`,
- `tools/static_binary_evidence.py`,
- `C:/Python314/python.exe` nur fuer Dateibindung und statische Windows-Versionsmetadaten, ohne Ausfuehrung.

Keine externe Quelle wurde verwendet.

## Verwendete Dateien und Schnittstellen

| Datei | Bytes | SHA-256 |
|---|---:|---|
| `docs/forschung/213ZH_G1_STATISCHE_AUSFUEHRUNGSVORREGISTRIERUNG.md` | 10.284 | `6AE7A4F4AAC2F9C605A92D4E605531B8A23ECF4A1E1BC1AAF4A08D1959665127` |
| `C:/Python314/python.exe` | 106.328 | `7CA24F26D6E3F463419EE4F537DDD3ACD312C38FE45E678CCE08572F26A8BD1A` |
| `tests/validate_static_binary_evidence.py` | 34.044 | `76CF80B8C62EB73DC9702ED54F364D513B171BC7BF3B61642D83C14EE497E784` |
| `tools/static_binary_evidence.py` | 42.225 | `03162A337473218ADBCAAE577DB1922A3127DD3BCE1AE3B151B0291BDAB4E286` |
| `docs/forschung/213Z_G1_REALPFAD_AUSSCHLUSSMENGE.json` | 6.253 | `52DA5D8DD26314BF173367E7F02D1F1B1055077380E83159A0FAE3EB87304ACF` |
| `docs/forschung/213X_G1_WERKZEUGVALIDIERUNG_VORREGISTRIERUNG.md` | 13.427 | `48DEB78544B8E1817E33BF01FD484EA7FBA750628CA200FE7BC9BB0147E81D63` |
| `docs/forschung/213Z_G1_WERKZEUGVALIDIERUNG_VERTRAGSKORREKTUR.md` | 12.309 | `6E6A3500295472AD8AD45DDE5A57CCE42C07307EE64D4B1734DACF9D1646E75D` |
| `docs/forschung/213ZA_G1_UNABHAENGIGE_STATISCHE_ABNAHME_213Z.md` | 9.113 | `00001F7A663EAE6F339643E893B16A5298D97E371ED5D287C84418CD8601EC61` |
| `docs/forschung/213ZG_G1_UNABHAENGIGE_STATISCHE_ABNAHME_213ZF.md` | 7.631 | `2B0BC0783BEFC2B670E47E3D25A7FC06D09F6A80909C6F352444D8726147994C` |

Verwendete statische Schnittstellen waren Dateigroesse, SHA-256, Windows-Dateiversionsmetadaten, Pfadexistenz und Quelltextvergleich. Keine Python- oder Projektlaufzeitschnittstelle wurde aufgerufen.

## Durchgefuehrte Schritte

1. Alle in `213ZH` genannten Bytebindungen wurden gegen die aktuellen Dateien verglichen.
2. Die Windows-Metadaten von `C:/Python314/python.exe` wurden ohne Start des Interpreters gelesen.
3. Anzahl und Inhalt der vorregistrierten Prozessaufrufe wurden mit der Controller-CLI verglichen.
4. Die fuenf in `213ZH` behaupteten frischen Pfade wurden auf Nichtexistenz geprueft.
5. Die im Controller tatsaechlich abgeleiteten Stagingpfade und die Erzeugungsart der Zielordner wurden statisch nachverfolgt.
6. CLI-Eingaben wurden lexikalisch gegen Rollen und Pfadklassen der 54er-Ausschlussmenge abgegrenzt.
7. Einprozess-, `-B`- und Nichtausfuehrungsgrenzen wurden gegen `213ZH` geprueft.

## Messergebnisse und Gegenbaselines

| Pruefpunkt | Soll | Beobachtet | Ergebnis |
|---|---|---|---|
| Direkte Bytebindungen | 6 unveraendert | 6/6 stimmen | bestanden |
| Fortgeltende Abnahmebindungen | 2 unveraendert | 2/2 stimmen | bestanden |
| Interpreter-Metadaten | CPython 3.14.4-Kandidat | `FileVersion=3.14.4`, `ProductVersion=3.14.4`, `OriginalFilename=python.exe` | statisch gestuetzt |
| Runtime-Version | erst im Controller messbar | nicht ausgefuehrt | offen, korrekt als Annahme markiert |
| CLI-Aufrufe | exakt 1 | 1 PowerShell-Aufruf von `python.exe -B` | bestanden |
| Prozessgrenze | 1 CPython-Prozess | genau 1 vorregistriert | bestanden |
| Genannte frische Pfade | 5 nicht vorhanden | 5/5 nicht vorhanden | bestanden |
| Realpfade als CLI-Eingaben | 0 | 0; `python.exe` ist weder `python314.dll` noch einer der 53 `.pyd`-Pfade | bestanden |
| Syntax/Test/Ausfuehrung in `213ZH` | 0 | 0 | bestanden |
| Temp-Elternpfad | vor Aufruf vorhanden | `.tmp` ist nicht vorhanden | **nicht bestanden** |
| Tatsaechliche Stagingpfade | mit Controllerableitung identisch | `213ZH` nennt Namen ohne fuehrenden Punkt; Controller erzeugt `.213ZH_g1_validation_success.staging` und `.213ZH_g1_validation_error.staging` | **nicht bestanden** |

### Befund 1 - nicht erzeugbarer Temporaerordner

Der CLI-Befehl bindet `--temp-dir` an:

`C:/Users/TV/Documents/MCM_FIELD_ORGANISM/workspace/.tmp/213ZH_g1_validation_temp`

Der Elternpfad `.tmp` ist statisch beobachtet nicht vorhanden. Der Controller verwendet fuer den Temporaerordner `mkdir(parents=False, exist_ok=False)`. Damit kann dieser vorregistrierte Pfad ohne eine nicht vorregistrierte vorgelagerte Verzeichniserzeugung nicht angelegt werden. Ein spontanes Anlegen von `.tmp` waere ein zusaetzlicher, nicht gebundener Vorbereitungsschritt und widerspraeche dem exakt einen vorregistrierten Prozessaufruf.

### Befund 2 - falsch bezeichnete Stagingpfade

`213ZH` bindet und prueft als Stagingziele:

- `reports/213ZH_g1_validation_success.staging`,
- `reports/213ZH_g1_validation_error.staging`.

Der Controller leitet stattdessen aus den finalen Namen ab:

- `reports/.213ZH_g1_validation_success.staging`,
- `reports/.213ZH_g1_validation_error.staging`.

Der fuehrende Punkt ist Bestandteil beider tatsaechlichen Dateinamen. Deshalb prueft die Vorregistrierung nicht die Pfade, die der Controller spaeter auf Vorhandensein prueft und beschreibt. Die behauptete Fuenfermenge frischer Zielpfade ist somit nicht die tatsaechliche Fuenfermenge des Controllers.

Gegenbaseline ist eine Vorregistrierung, deren Temp-, Final- und abgeleitete Stagingpfade ohne Zusatzhandlung exakt mit dem Controller uebereinstimmen. `213ZH` verfehlt diese Gegenbaseline in zwei Punkten.

## Grenzen und nicht gepruefte Annahmen

- Die Runtime-Identitaet CPython 3.14.4 bleibt trotz passender Dateimetadaten bis zu einem getrennt freigegebenen Controllerlauf ungeprueft.
- Python-Syntax und CLI-Parser wurden nicht ausgefuehrt.
- Es wurden keine Fixtures und keine Ergebnis- oder Fehlerpublikation erzeugt.
- Die 54 Realpfade wurden nicht auf Existenz geprueft, geoeffnet, gelesen oder gehasht.
- Aus der statischen Abnahme folgt kein Messergebnis zu den 21 Faellen und kein G1-, Resolver- oder MCM-Funktionsnachweis.

## Konkrete Schlussfolgerung

Die Bytebindungen, Versionsannahme, Einprozessgrenze, CLI-Eindeutigkeit und Realpfadsperre von `213ZH` sind statisch stimmig. Die Ausfuehrungsvorregistrierung ist dennoch **nicht abnahmefaehig**, weil der Temp-Elternpfad fehlt und die zwei dokumentierten Stagingpfade nicht den vom Controller tatsaechlich abgeleiteten Pfaden entsprechen.

Eine Ausfuehrung darf auf Basis von `213ZH` nicht freigegeben werden. G1 bleibt nicht bestanden, G0 bleibt abhaengig und Huerde G bleibt gesperrt. Eine Zielabweichung ist nicht erkennbar.

## Vorschlag fuer den naechsten begrenzten Schritt

Als naechstes sollte genau ein statisches Korrekturpaket fuer `213ZH` erstellt werden:

1. `--temp-dir` wird auf einen neuen, nicht vorhandenen Unterpfad eines bereits vorhandenen Workspace-Elternordners gebunden, vorzugsweise `reports/213ZH_g1_validation_temp`.
2. Die beiden Stagingpfade werden exakt mit fuehrendem Punkt dokumentiert und auf Nichtexistenz gebunden: `reports/.213ZH_g1_validation_success.staging` und `reports/.213ZH_g1_validation_error.staging`.
3. Der einzige CLI-Befehl und alle betroffenen Pfadtabellen werden gemeinsam korrigiert; alle Bytebindungen bleiben unveraendert.

Danach ist erneut genau eine unabhaengige statische Abnahme erforderlich. Weiterhin nicht freigegeben sind Syntaxpruefung, Tests, Controller- oder Werkzeugausfuehrung, Zugriff auf die 54 Realpfade, Manifest-, Resolver-, G2- und Huerde-G-Arbeit.
