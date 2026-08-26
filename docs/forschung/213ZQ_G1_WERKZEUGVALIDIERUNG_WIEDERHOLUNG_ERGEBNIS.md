# 213ZQ - Ergebnis der kontrollierten G1-Werkzeugvalidierungswiederholung

## Einordnung

`213ZQ` dokumentiert einen technischen Validierungsschritt und keinen Forschungslauf zur MCM-Felddynamik. Es wurde genau ein vorregistrierter Controllerprozess gestartet. Ein Wiederholungsversuch fand nicht statt.

## Forschungsfrage und Auftrag

Kann der in `213ZO` exakt gebundene Einzelbefehl nach bestandener statischer Abnahme `213ZP` die kontrollierte Werkzeugvalidierung mit Syntaxanalyse und 21 synthetischen Faellen durchfuehren?

## Tatsaechlich verwendete Quellen

- aktueller Uebergabe-Eingang
- `docs/forschung/213ZO_G1_NEUE_STATISCHE_AUSFUEHRUNGSVORREGISTRIERUNG.md`
- `docs/forschung/213ZP_G1_213ZO_STATISCHE_ABNAHME.md`
- `tests/validate_static_binary_evidence.py`
- Prozessausgabe des exakt einmal gestarteten, in `213ZO` gebundenen CLI-Befehls

Keine externen Quellen wurden verwendet.

## Verwendete Dateien und Schnittstellen

Unmittelbar vor dem Start wurden folgende sechs Bindungen erneut geprueft:

| Rolle | Bytes | SHA-256 | Ergebnis |
|---|---:|---|---|
| CPython-Interpreter | 106328 | `7CA24F26D6E3F463419EE4F537DDD3ACD312C38FE45E678CCE08572F26A8BD1A` | stimmt |
| Controller | 34044 | `433B6EA8695B6C7B6FCC2C583C7125606B00567900802F2871DA305932D1A88D` | stimmt |
| Werkzeug | 42225 | `03162A337473218ADBCAAE577DB1922A3127DD3BCE1AE3B151B0291BDAB4E286` | stimmt |
| Vertrag 213X | 13427 | `48DEB78544B8E1817E33BF01FD484EA7FBA750628CA200FE7BC9BB0147E81D63` | stimmt |
| Vertrag 213Z | 12309 | `6E6A3500295472AD8AD45DDE5A57CCE42C07307EE64D4B1734DACF9D1646E75D` | stimmt |
| Ausschlussartefakt | 6253 | `52DA5D8DD26314BF173367E7F02D1F1B1055077380E83159A0FAE3EB87304ACF` | stimmt |

Als Ausfuehrungsschnittstelle wurde ausschliesslich der in `213ZO` dokumentierte einzelne `C:\Python314\python.exe -B`-Aufruf verwendet. Seine Argumente wurden nicht veraendert.

## Durchgefuehrte Schritte

1. Alle sechs Datei-, Groessen- und SHA-256-Bindungen wurden unmittelbar erneut geprueft.
2. Das Nichtvorhandensein aller fuenf in `213ZO` gebundenen Ziele wurde unmittelbar erneut geprueft.
3. Der exakt in `213ZO` gebundene Befehl wurde einmal gestartet.
4. Nach seinem Ende wurden Exitcode, Fehlermeldung und Status aller fuenf Zielpfade statisch geprueft.
5. Die CLI-Definition des gebundenen Controllers wurde anschliessend nur lesend abgeglichen.

## Messergebnisse und Gegenbaselines

| Messpunkt | Ergebnis |
|---|---|
| Dateibindungen unmittelbar vor Start | `6/6` korrekt |
| Frische Zielpfade unmittelbar vor Start | `5/5` nicht vorhanden |
| Gestartete Controllerprozesse | exakt `1` |
| Wiederholungsversuche | `0` |
| Prozess-Exitcode | `1` |
| Erreichte Phase | CLI-Argumentpruefung von `argparse` |
| Syntaxanalyse | nicht erreicht |
| Synthetische Faelle | `0/21` ausgefuehrt |
| Nach Prozessende vorhandene Zielpfade | `0/5` |
| Realpfadzugriffe | `0` nach beobachtbarer Phasengrenze |
| Manifest-, Resolver-, G2- oder Huerde-G-Arbeit | `0` |

Beobachtete Fehlermeldung:

```text
validate_static_binary_evidence.py: error: the following arguments are required: --interpreter, --interpreter-size, --interpreter-sha256, --workspace
```

Statische Gegenpruefung des Controllers:

- Die Parserdefinition erzeugt fuer die Rolle `interpreter` die drei Pflichtargumente `--interpreter`, `--interpreter-size` und `--interpreter-sha256`.
- `--workspace` ist ein weiteres Pflichtargument.
- `213ZO` bindet stattdessen `--python-exe`, `--python-size` und `--python-sha256` und enthaelt kein `--workspace`.
- Der Abbruch ist damit vollstaendig durch die Differenz zwischen vorregistrierter CLI und gebundener Parserdefinition erklaert.

## Beobachtetes Ergebnis

Die Werkzeugvalidierung ist nicht bestanden. Der einzige freigegebene Prozess stoppte kontrolliert in der Argumentpruefung, bevor Controllerlogik, Syntaxanalyse, Fixturephase oder Publikation erreicht wurden. Es entstanden keine Temp-, Erfolgs-, Fehler- oder Stagingartefakte.

## Technische Interpretation

Der Befund betrifft die statische Ausfuehrungsvorregistrierung, nicht die zuvor korrigierten `expected_counts`-Schluessel und nicht die Funktionsfaehigkeit des Werkzeugs. `213ZP` bestaetigte die interne Konsistenz der in `213ZO` dokumentierten Bindungen, pruefte jedoch nicht die Uebereinstimmung aller CLI-Optionsnamen mit dem Parservertrag.

## Hypothese

Nach einer eng begrenzten Korrektur der drei Interpreter-Optionsnamen und dem Hinzufuegen des gebundenen Workspacearguments koennte der Controller die eigentliche Bindungsphase erreichen. Dies ist nicht geprueft und keine Erfolgsbehauptung.

## Grenzen und nicht gepruefte Annahmen

- Controller- und Werkzeugsyntax wurden nicht analysiert.
- Kein synthetischer Fall wurde ausgefuehrt.
- Die Werkzeugvalidierung liefert daher keine Aussage zur Eignung des Werkzeugs.
- Der fehlende `--workspace`-Wert muss in einem neuen statischen Korrekturpaket kanonisch festgelegt und gebunden werden.
- Fuer jede spaetere Ausfuehrung sind vollstaendig neue Temp-, Erfolgs-, Fehler- und Stagingnamen erforderlich, obwohl `213ZO` keine Zielartefakte erzeugte.
- Es gibt keinen Befund zu Memory, Feldorganisation, Semantik oder KI.

## Konkrete Schlussfolgerung

Die kontrollierte Wiederholung endete mit einem reproduzierbar erklaerten CLI-Fruehabbruch. Die Ausfuehrungsgrenzen wurden eingehalten, aber die Werkzeugvalidierung ist nicht bestanden. Eine Zielabweichung ist nicht erkennbar.

## Vorschlag fuer den naechsten begrenzten Schritt

Als naechster Schritt ist genau ein statisches Korrekturpaket fuer die Ausfuehrungsvorregistrierung vorzuschlagen:

- `--python-exe` durch `--interpreter` ersetzen,
- `--python-size` durch `--interpreter-size` ersetzen,
- `--python-sha256` durch `--interpreter-sha256` ersetzen,
- `--workspace` mit dem kanonischen Projekt-Workspace ergaenzen und als UTF-8-Pfadstring binden,
- vollstaendig neue Temp-, Erfolgs-, Fehler- und Stagingpfade verwenden.

Danach ist zwingend eine neue unabhaengige statische Abnahme erforderlich. Eine weitere Ausfuehrung ist bis dahin nicht zulaessig.
