# 213ZL - Kontrollierte Werkzeugvalidierung

## Einordnung

`213ZL` ist ein technischer Werkzeugvalidierungsschritt und kein Forschungslauf. Ausgefuehrt wurde genau der durch `213ZJ` vorregistrierte und durch `213ZK` statisch abgenommene Einzelbefehl.

Vor dem Aufruf wurden alle sechs direkten Dateibindungen, der vorhandene `reports`-Elternordner und die Nichtexistenz aller fuenf Zielpfade geprueft. Danach wurde genau ein CPython-Controllerprozess gestartet. Es gab keinen zweiten Python-Aufruf und keinen Wiederholungsversuch.

## Forschungsfrage und Auftrag

Kann der gebundene Einprozess-Controller die Syntaxanalyse und alle 21 synthetischen Werkzeugfaelle unter den Ausschluss-, Einprozess- und atomaren Publikationsregeln vollstaendig ausfuehren?

## Tatsaechlich verwendete Quellen

- aktueller freigegebener Uebergabe-Eingang,
- `docs/forschung/213ZJ_G1_AUSFUEHRUNGSVORREGISTRIERUNG_KORREKTUR_213ZI.md`,
- `docs/forschung/213ZK_G1_UNABHAENGIGE_STATISCHE_ABNAHME_213ZJ.md`,
- die sechs in `213ZJ` gebundenen Dateien,
- `reports/213ZH_g1_validation_error/validation_error.json`,
- `tests/validate_static_binary_evidence.py` nach dem Lauf ausschliesslich fuer die statische Zuordnung des gemeldeten Fehlers.

Keine externe Quelle wurde verwendet.

## Verwendete Dateien und Schnittstellen

Unmittelbar vor dem Controllerstart bestaetigte Bindungen:

| Rolle | Bytes | SHA-256 | Vorpruefung |
|---|---:|---|---|
| Interpreter `C:/Python314/python.exe` | 106.328 | `7CA24F26D6E3F463419EE4F537DDD3ACD312C38FE45E678CCE08572F26A8BD1A` | bestanden |
| Controller | 34.044 | `76CF80B8C62EB73DC9702ED54F364D513B171BC7BF3B61642D83C14EE497E784` | bestanden |
| Zielwerkzeug | 42.225 | `03162A337473218ADBCAAE577DB1922A3127DD3BCE1AE3B151B0291BDAB4E286` | bestanden |
| Vertrag X | 13.427 | `48DEB78544B8E1817E33BF01FD484EA7FBA750628CA200FE7BC9BB0147E81D63` | bestanden |
| Vertrag Z | 12.309 | `6E6A3500295472AD8AD45DDE5A57CCE42C07307EE64D4B1734DACF9D1646E75D` | bestanden |
| Ausschlussartefakt | 6.253 | `52DA5D8DD26314BF173367E7F02D1F1B1055077380E83159A0FAE3EB87304ACF` | bestanden |

Verwendete Laufzeitschnittstelle war genau ein Aufruf von `C:/Python314/python.exe -B` mit den in `213ZJ` gebundenen Controllerargumenten. Nach dem kontrollierten Ende wurden nur die Zielpfadstatus und die publizierte Fehler-JSON mit PowerShell gelesen.

## Durchgefuehrte Schritte

1. `6/6` direkte Dateibindungen wurden unmittelbar vor dem Aufruf bestaetigt.
2. `reports` wurde als vorhandener Elternordner bestaetigt.
3. Temp-, Erfolgs-, Fehler- und beide Stagingpfade wurden als `5/5` nicht vorhanden bestaetigt.
4. Genau der einzelne in `213ZJ` gebundene `python.exe -B`-Befehl wurde einmal gestartet.
5. Der Controller endete mit Prozesscode `1` und Meldung `EXCLUSION_BINDING_MISMATCH: unexpected exclusion counts`.
6. Es wurde kein zweiter Controllerprozess gestartet.
7. Die atomar publizierte Fehlerausgabe und die fuenf Zielpfadstatus wurden gelesen.
8. Der gemeldete Fehler wurde statisch dem Controllervergleich in `verify_exclusion` zugeordnet.

## Messergebnisse und Gegenbaselines

### Laufresultat

| Messwert | Erwartung | Beobachtet | Ergebnis |
|---|---|---|---|
| Controllerprozesse | 1 | 1 | bestanden |
| Prozesscode | 0 bei Gesamterfolg | 1 | nicht bestanden |
| Fehlercode | keiner | `EXCLUSION_BINDING_MISMATCH` | kontrollierter Stopp |
| Fehlerphase | keine | `exclusion` | vor Syntaxanalyse |
| Syntaxanalyse | `parse_ok=true` | nicht erreicht | 0 Ergebnisse |
| Synthetische Faelle | 21/21 | 0/21 erreicht | nicht bestanden |
| Erfolgsordner | atomar bei Erfolg | nicht vorhanden | konsistent mit Stopp |
| Fehlerordner | atomar bei Fehler | vorhanden | bestanden |
| Temporaerordner nach Ende | entfernt | nicht vorhanden | bestanden |
| Erfolgs-Staging nach Ende | nicht vorhanden | nicht vorhanden | bestanden |
| Fehler-Staging nach Ende | nicht vorhanden | nicht vorhanden | bestanden |

Die publizierte Fehlerdatei:

- Pfad: `reports/213ZH_g1_validation_error/validation_error.json`,
- Groesse: 2.024 Bytes,
- SHA-256: `3D053843BD60CC1F5094D11ADE2F6B1D0B5FC2E1A3778B0324E76B6DFF07939B`,
- Schema: `mcm-g1-tool-validation-error-v1`,
- Fehlercode: `EXCLUSION_BINDING_MISMATCH`,
- Detail: `unexpected exclusion counts`,
- Phase: `exclusion`,
- `case_id: null`.

Die Fehlerausgabe enthaelt alle sechs erwarteten Metabindungen. Sie meldet ausserdem:

- `project_control_opened: false`,
- `real_target_binary_opened: false`,
- `manifest_generated: false`,
- `resolver_run: false`,
- `g2_touched: false`.

Diese Flags sind Beobachtungen der Controller-Ausgabe und kein unabhaengiges Betriebssystem-Audit der Dateizugriffe.

### Technische Fehlerzuordnung

Das gebundene Ausschlussartefakt verwendet unter `expected_counts`:

- `cpython_binary: 1`,
- `native_candidate: 53`,
- `total: 54`.

Der Controller fragt in `verify_exclusion` stattdessen ab:

- `counts.get("cpython-binary")`,
- `counts.get("native-candidate")`,
- `counts.get("total")`.

Die Rollenwerte der Eintraege verwenden korrekt Bindestriche; nur die Schluessel von `expected_counts` verwenden laut gebundenem Schema Unterstriche. Der Controller vermischt diese beiden Namensraeume. Dadurch entsteht beobachtet `(None, None, 54)` statt `(1, 53, 54)`, und der Controller stoppt vertragsgemaess vor Syntaxanalyse und Fixturephase.

Gegenbaseline war ein vollstaendiger Lauf mit `parse_ok=true`, `21/21` bestandenen Faellen und atomarer Erfolgspublikation. Diese Gegenbaseline wurde nicht erreicht. Der kontrollierte fruehe Stopp darf nicht als Teilerfolg oder kleinere Fallzahl umgedeutet werden.

## Grenzen und nicht gepruefte Annahmen

- Syntax und Importmenge des Zielwerkzeugs wurden im Lauf nicht erreicht.
- Keiner der 21 synthetischen Faelle wurde ausgefuehrt.
- Zaehler-, PE-, Fehlerkontext- und Routingorakel besitzen aus `213ZL` keine Laufzeitmessung.
- Die Flags zu Realpfaden und ausgeschlossenen Arbeiten stammen aus der Controllerausgabe; ein separates Dateisystem-Tracing war nicht vorregistriert.
- Es wurde kein Wiederholungsversuch vorgenommen.
- Der Fehlerordner ist nun belegt und darf fuer einen spaeteren Lauf nicht wiederverwendet, geloescht oder ueberschrieben werden.
- Es erfolgte keine Manifest-, Resolver-, G2- oder Huerde-G-Arbeit.
- Aus diesem Werkzeugstopp folgt keine Aussage ueber G1, MCM-Memory, Feldorganisation, Semantik oder KI.

## Konkrete Schlussfolgerung

Der kontrollierte Werkzeugvalidierungsschritt ist **nicht bestanden**. Der Einprozess- und Fehlerpublikationspfad funktionierte bis zum fruehen Ausschlussstopp, aber Syntaxanalyse und alle 21 synthetischen Faelle blieben unerreicht.

Die Ursache ist ein eng lokalisierter statischer Controllerfehler: `expected_counts` wird mit Bindestrichschluesseln gelesen, obwohl das gebundene Ausschlussartefakt dort Unterstrichschluessel definiert. Das Ausschlussartefakt selbst stimmt weiterhin mit seiner Bytebindung ueberein und darf nicht an den fehlerhaften Controller angepasst werden.

G1 bleibt nicht bestanden, G0 bleibt abhaengig und Huerde G bleibt gesperrt. Eine Zielabweichung ist nicht erkennbar.

## Vorschlag fuer den naechsten begrenzten Schritt

Als naechstes sollte genau ein statisches Controllerkorrekturpaket erstellt werden, ausschliesslich fuer die zwei Zugriffe in `verify_exclusion`:

- `counts.get("cpython-binary")` zu `counts.get("cpython_binary")`,
- `counts.get("native-candidate")` zu `counts.get("native_candidate")`.

Danach sind eine neue Bytebindung des Controllers, eine unabhaengige statische Abnahme dieser Zweischluesselkorrektur und neue, bisher nicht verwendete Temp-, Erfolgs-, Fehler- und Stagingpfade erforderlich. Bis zu gesonderten Freigaben sind Wiederholung, Syntaxpruefung, Tests, Controller- oder Werkzeugausfuehrung, Zugriff auf die 54 Realpfade, Manifest-, Resolver-, G2- und Huerde-G-Arbeit gesperrt.
