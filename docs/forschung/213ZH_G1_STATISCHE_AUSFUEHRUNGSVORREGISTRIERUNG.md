# 213ZH - Statische Ausfuehrungsvorregistrierung

## Einordnung

`213ZH` ist eine statische Vorregistrierung und kein Forschungslauf. Sie bindet genau einen moeglichen spaeteren Validierungsaufruf des durch `213ZG` statisch abgenommenen Einprozess-Controllers. Dieser Aufruf wird in `213ZH` nicht ausgefuehrt und durch dieses Dokument nicht freigegeben.

Es erfolgten keine Syntaxpruefung, kein Test, keine Controller- oder Werkzeugausfuehrung und kein Zugriff auf einen der 54 Realpfade. Es wurden keine Ausgabeordner, Fixtures, Manifeste oder Resolverdaten erzeugt.

## Forschungsfrage und Auftrag

Kann ein einzelner spaeterer Controlleraufruf so bytegenau und pfadgenau vorregistriert werden, dass Interpreter, Controller, Zielwerkzeug, Ausschlussartefakt, fortgeltende Vertraege und frische Ausgabeziele vor jeder Ausfuehrungsentscheidung eindeutig feststehen?

## Tatsaechlich verwendete Quellen

- aktueller freigegebener Uebergabe-Eingang,
- `docs/forschung/213X_G1_WERKZEUGVALIDIERUNG_VORREGISTRIERUNG.md`,
- `docs/forschung/213Z_G1_WERKZEUGVALIDIERUNG_VERTRAGSKORREKTUR.md`,
- `docs/forschung/213ZA_G1_UNABHAENGIGE_STATISCHE_ABNAHME_213Z.md`,
- `docs/forschung/213ZG_G1_UNABHAENGIGE_STATISCHE_ABNAHME_213ZF.md`,
- `docs/forschung/213Z_G1_REALPFAD_AUSSCHLUSSMENGE.json`,
- `tests/validate_static_binary_evidence.py`,
- `tools/static_binary_evidence.py`,
- `C:/Python314/python.exe` ausschliesslich fuer Pfad-, Groessen- und SHA-256-Bindung, ohne Ausfuehrung.

Keine externe Quelle wurde verwendet.

## Bytebindungen

### Spaeter direkt durch den Controller zu pruefende Bindungen

| Rolle | Pfad | Bytes | SHA-256 |
|---|---|---:|---|
| CPython-3.14.4-Interpreterkandidat | `C:/Python314/python.exe` | 106.328 | `7CA24F26D6E3F463419EE4F537DDD3ACD312C38FE45E678CCE08572F26A8BD1A` |
| Controller/Runner | `tests/validate_static_binary_evidence.py` | 34.044 | `76CF80B8C62EB73DC9702ED54F364D513B171BC7BF3B61642D83C14EE497E784` |
| Zielwerkzeug | `tools/static_binary_evidence.py` | 42.225 | `03162A337473218ADBCAAE577DB1922A3127DD3BCE1AE3B151B0291BDAB4E286` |
| Vertrag X | `docs/forschung/213X_G1_WERKZEUGVALIDIERUNG_VORREGISTRIERUNG.md` | 13.427 | `48DEB78544B8E1817E33BF01FD484EA7FBA750628CA200FE7BC9BB0147E81D63` |
| Vertrag Z | `docs/forschung/213Z_G1_WERKZEUGVALIDIERUNG_VERTRAGSKORREKTUR.md` | 12.309 | `6E6A3500295472AD8AD45DDE5A57CCE42C07307EE64D4B1734DACF9D1646E75D` |
| Ausschlussartefakt | `docs/forschung/213Z_G1_REALPFAD_AUSSCHLUSSMENGE.json` | 6.253 | `52DA5D8DD26314BF173367E7F02D1F1B1055077380E83159A0FAE3EB87304ACF` |

Die Bezeichnung CPython 3.14.4 ist bis zur Ausfuehrung eine Vertragsbindung. Beobachtet wurden in `213ZH` nur Pfad, Dateigroesse und Hash des Interpreters; seine Versionsmeldung wurde nicht ausgefuehrt. Der Controller muss bei einem spaeter getrennt freigegebenen Lauf zusaetzlich `sys.implementation.name == "cpython"` und `sys.version_info[:3] == (3, 14, 4)` pruefen.

### Fortgeltende statische Abnahmebindungen

| Rolle | Pfad | Bytes | SHA-256 |
|---|---|---:|---|
| Statische Vertragsabnahme | `docs/forschung/213ZA_G1_UNABHAENGIGE_STATISCHE_ABNAHME_213Z.md` | 9.113 | `00001F7A663EAE6F339643E893B16A5298D97E371ED5D287C84418CD8601EC61` |
| Statische Controllerabnahme | `docs/forschung/213ZG_G1_UNABHAENGIGE_STATISCHE_ABNAHME_213ZF.md` | 7.631 | `2B0BC0783BEFC2B670E47E3D25A7FC06D09F6A80909C6F352444D8726147994C` |

Diese beiden Abnahmen gelten als Vorbedingung der spaeteren Ausfuehrungsentscheidung. Sie sind keine zusaetzlichen Controllerargumente, weil die statisch abgenommene CLI ausschliesslich `contract-x` und `contract-z` vorsieht. Eine Abweichung ihrer Bindung macht diese Vorregistrierung ungueltig und verlangt eine neue statische Pruefung vor jeder Ausfuehrung.

## Frische Ausgabeziele

Workspace-Bindung:

`C:/Users/TV/Documents/MCM_FIELD_ORGANISM/workspace`

Genau dieser spaetere Zielsatz ist vorregistriert:

| Rolle | Absoluter Pfad | Zustand bei Vorregistrierung |
|---|---|---|
| Temporaerordner | `C:/Users/TV/Documents/MCM_FIELD_ORGANISM/workspace/.tmp/213ZH_g1_validation_temp` | nicht vorhanden |
| Erfolgsordner | `C:/Users/TV/Documents/MCM_FIELD_ORGANISM/workspace/reports/213ZH_g1_validation_success` | nicht vorhanden |
| Fehlerordner | `C:/Users/TV/Documents/MCM_FIELD_ORGANISM/workspace/reports/213ZH_g1_validation_error` | nicht vorhanden |
| Erfolgs-Staging | `C:/Users/TV/Documents/MCM_FIELD_ORGANISM/workspace/reports/213ZH_g1_validation_success.staging` | nicht vorhanden |
| Fehler-Staging | `C:/Users/TV/Documents/MCM_FIELD_ORGANISM/workspace/reports/213ZH_g1_validation_error.staging` | nicht vorhanden |

Alle fuenf Pfade muessen unmittelbar vor einem spaeteren Aufruf weiterhin fehlen. Bereits vorhandene Pfade duerfen weder geloescht, geleert, umbenannt noch wiederverwendet werden; der Lauf ist dann vor dem Python-Aufruf neu zu planen.

## Exakt ein spaeterer CLI-Befehl

Der einzige vorregistrierte Prozessaufruf lautet:

```powershell
& 'C:\Python314\python.exe' -B 'C:\Users\TV\Documents\MCM_FIELD_ORGANISM\workspace\tests\validate_static_binary_evidence.py' --runner 'C:\Users\TV\Documents\MCM_FIELD_ORGANISM\workspace\tests\validate_static_binary_evidence.py' --runner-size 34044 --runner-sha256 76CF80B8C62EB73DC9702ED54F364D513B171BC7BF3B61642D83C14EE497E784 --tool 'C:\Users\TV\Documents\MCM_FIELD_ORGANISM\workspace\tools\static_binary_evidence.py' --tool-size 42225 --tool-sha256 03162A337473218ADBCAAE577DB1922A3127DD3BCE1AE3B151B0291BDAB4E286 --contract-x 'C:\Users\TV\Documents\MCM_FIELD_ORGANISM\workspace\docs\forschung\213X_G1_WERKZEUGVALIDIERUNG_VORREGISTRIERUNG.md' --contract-x-size 13427 --contract-x-sha256 48DEB78544B8E1817E33BF01FD484EA7FBA750628CA200FE7BC9BB0147E81D63 --contract-z 'C:\Users\TV\Documents\MCM_FIELD_ORGANISM\workspace\docs\forschung\213Z_G1_WERKZEUGVALIDIERUNG_VERTRAGSKORREKTUR.md' --contract-z-size 12309 --contract-z-sha256 6E6A3500295472AD8AD45DDE5A57CCE42C07307EE64D4B1734DACF9D1646E75D --exclusion 'C:\Users\TV\Documents\MCM_FIELD_ORGANISM\workspace\docs\forschung\213Z_G1_REALPFAD_AUSSCHLUSSMENGE.json' --exclusion-size 6253 --exclusion-sha256 52DA5D8DD26314BF173367E7F02D1F1B1055077380E83159A0FAE3EB87304ACF --interpreter 'C:\Python314\python.exe' --interpreter-size 106328 --interpreter-sha256 7CA24F26D6E3F463419EE4F537DDD3ACD312C38FE45E678CCE08572F26A8BD1A --workspace 'C:\Users\TV\Documents\MCM_FIELD_ORGANISM\workspace' --temp-dir 'C:\Users\TV\Documents\MCM_FIELD_ORGANISM\workspace\.tmp\213ZH_g1_validation_temp' --success-dir 'C:\Users\TV\Documents\MCM_FIELD_ORGANISM\workspace\reports\213ZH_g1_validation_success' --error-dir 'C:\Users\TV\Documents\MCM_FIELD_ORGANISM\workspace\reports\213ZH_g1_validation_error'
```

Der Schalter `-B` untersagt Bytecode-Schreiben auf Interpreterebene. Es sind kein vorgelagerter Syntaxbefehl, kein zweiter Python-Prozess, keine Shell-Pipeline und kein Nachbearbeitungsbefehl vorregistriert.

## Vorbedingungen und Stopplinien

Vor einer spaeteren Ausfuehrung muessen durch eine getrennte statische Abnahme bestaetigt werden:

1. alle oben genannten Bytebindungen sind unveraendert,
2. der CLI-Befehl stimmt byte- und argumentgenau mit dieser Vorregistrierung ueberein,
3. alle fuenf Ausgabe- und Stagingpfade fehlen,
4. die Ausschlussmenge bleibt bei 54 lexikalisch gebundenen Pfaden,
5. es ist genau ein CPython-Prozess und genau eine `runpy.run_path`-Ausfuehrung vorgesehen,
6. weder Projektsteuerdatei noch einer der 54 Realpfade ist CLI-Eingabe,
7. es gibt keine Manifest-, Resolver-, G2- oder Huerde-G-Handlung.

Bei jeder Abweichung ist vor dem Python-Aufruf zu stoppen. Die Vorregistrierung darf nicht durch spontane Pfad-, Hash-, Befehls- oder Ausgabeanpassung repariert werden.

## Durchgefuehrte Schritte und Messergebnisse

1. Die statisch abgenommene Controller-CLI wurde gelesen.
2. Interpreter, Controller, Werkzeug, Ausschlussartefakt und Vertragsdateien wurden ueber Pfad, Dateigroesse und SHA-256 gebunden.
3. Ein neuer Zielsatz wurde lexikalisch festgelegt und auf gegenwaertige Nichtexistenz geprueft.
4. Genau ein spaeterer CPython-Aufruf wurde vollstaendig aus den Bindungen zusammengesetzt.

Beobachtetes Ergebnis ist ausschliesslich die vollstaendige Vorregistrierung von sechs direkten Controllerbindungen, zwei fortgeltenden statischen Abnahmebindungen, fuenf frischen Zielpfaden und einem spaeteren Prozessaufruf. Es existiert kein Syntax-, Fixture- oder Werkzeugmessergebnis.

Gegenbaseline sind ein ungebundener Interpreter, veraenderbare CLI-Argumente, mehrere Python-Aufrufe, wiederverwendete Ausgabeziele oder ein Realpfad als Eingabe. Keiner dieser Zustaende ist vorregistriert.

## Grenzen und nicht gepruefte Annahmen

- Die behauptete CPython-Version 3.14.4 wurde nicht durch Ausfuehrung gemessen.
- Die Python-Syntax von Controller und Werkzeug wurde nicht geprueft.
- Die CLI wurde nicht durch einen Parserlauf validiert.
- Keine Bindung wurde durch den Controller selbst geprueft.
- Atomaritaet, Schreibwaechter, AST-Orakel, 21 Fixturefaelle und Fehlerpublikation wurden nicht ausgefuehrt.
- Die 54 Realpfade wurden weder geoeffnet noch auf Existenz geprueft.
- Die aktuelle Nichtexistenz der Zielpfade ist nur eine statische Vorbedingung und muss unmittelbar vor einem spaeteren Lauf erneut bestaetigt werden.
- Ein spaeteres `21/21` waere nur eine Werkzeugvalidierung, kein G1-Resolvernachweis und kein Nachweis einer MCM-Funktion.

## Konkrete Schlussfolgerung

Der spaetere Validierungsschritt ist nun pfad-, byte-, ziel- und befehlsgenau vorregistriert. `213ZH` erteilt keine Ausfuehrungsfreigabe. G1 bleibt nicht bestanden, G0 bleibt abhaengig und Huerde G bleibt gesperrt. Eine Zielabweichung ist nicht erkennbar.

## Vorschlag fuer den naechsten begrenzten Schritt

Als naechstes ist genau eine unabhaengige statische Abnahme von `213ZH` vorzunehmen. Sie soll alle Bytebindungen, die Versionsannahme, die Vollstaendigkeit und Eindeutigkeit des einzelnen CLI-Befehls, die fuenf frischen Zielpfade, die Einprozessgrenze sowie den Ausschluss der 54 Realpfade pruefen. Weiterhin nicht freigegeben sind Syntaxpruefung, Tests, Controller- oder Werkzeugausfuehrung, Realpfadzugriff, Manifest-, Resolver-, G2- und Huerde-G-Arbeit. Erst das Ergebnis dieser Abnahme darf einen getrennten Vorschlag fuer oder gegen den kontrollierten Validierungsaufruf enthalten.
