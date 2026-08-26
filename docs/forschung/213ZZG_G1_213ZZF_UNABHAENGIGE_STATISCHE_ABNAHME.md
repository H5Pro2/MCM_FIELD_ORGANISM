# 213ZZG - Unabhaengige statische Abnahme von 213ZZF

## Einordnung

`213ZZG` ist kein Forschungslauf und erhaelt keine Laufnummer. Gegenstand ist ausschliesslich die unabhaengige statische Abnahme der in `213ZZF` gebundenen Implementierung. Das Skript wurde weder ausgefuehrt noch dot-gesourct.

## Forschungsfrage und Auftrag

Erfuellt `tools/run_realpath_metadata_inventory.ps1` statisch die freigegebenen Bindungen zu Dokument, Skriptpfad, Konstanten, `-PolicyProbe`-Kontrollfluss, Produktionsvorbedingungen, einmaliger Metadatenschleife, Staginguebergabe, Fehlervertrag, Ein-Prozess- und Kein-Retry-Regel?

## Verwendete Quellen

- aktueller Uebergabe-Eingang;
- `docs/forschung/213ZZF_G1_REALPFAD_INVENTURSKRIPT_IMPLEMENTIERUNG_UND_STATISCHER_ABNAHMEVORSCHLAG.md`;
- `docs/forschung/213ZZE_G1_213ZZD_UNABHAENGIGE_STATISCHE_ABNAHME.md`;
- `docs/forschung/213ZZD_G1_REALPFAD_INVENTURSKRIPT_MINIMALER_UMSETZUNGSVORSCHLAG.md`;
- `tools/run_realpath_metadata_inventory.ps1`.

Keine externen Quellen wurden verwendet.

## Verwendete Dateien und Schnittstellen

Die Skriptdatei und die Dokumentbindung wurden nur lesend geprueft. Verwendet wurden `System.Management.Automation.Language.Parser`, PowerShell-AST-Knotentypen, `Get-FileHash`, Dateibytes, `Test-Path`, `git diff --check` und `git status --short`. Keine dieser Pruefungen lud oder startete das Inventurskript.

## Durchgefuehrte Schritte

1. Skript und `213ZZF` nach Pfad, Bytegroesse und SHA-256 gebunden.
2. Skript mit dem PowerShell-Parser als Quelltext geparst und AST-Knoten ausgewertet.
3. Parameterzahl, Probe-Zweig, unmittelbaren Probe-Ausstieg und dessen Position vor Produktionskonstanten geprueft.
4. Produktionsliterale und Vorbedingungen gegen `213ZZF` geprueft.
5. Schleifen, Befehle und Mitgliedsaufrufe auf einmalige Metadatenaufnahme, Kindprozesse, Importe, dynamische Ausfuehrung, Netzwerkzugriffe und Retry untersucht.
6. Final- und Stagingziel auf Nichtvorhandensein geprueft.
7. `git diff --check` fuer Skript und Dokumentbindung ausgefuehrt.

## Messergebnisse und Gegenbaselines

- Skriptpfad: `tools/run_realpath_metadata_inventory.ps1`;
- Skriptbytes: `5085`;
- Skript-SHA-256: `8E7AAD2C3FF5E397FE54B81CC6EF1F72CCA82BDF36DD834E6C50D2B232EAF13B`;
- `213ZZF`-Bytes: `4997`;
- `213ZZF`-SHA-256: `70AF36B77EEA08DB3624DACB838E7B23ACEB53900B562787199C2F1A057D295C`;
- Parserfehler: `0`;
- Parameter: genau `PolicyProbe`;
- Probe-Ausgabe: exakt eine feste JSON-Zeile mit `realpath_queries:0` und `artifacts_written:0`;
- Probe-Befehle: `0`; einziger Mitgliedsaufruf ist `[Console]::Out.WriteLine(...)`;
- Probe-Ausstieg: unmittelbar `exit 0`, vor allen Produktionspfaden;
- lineare `foreach`-Schleifen: `2`, davon eine Bindungsvalidierung und eine Metadatenschleife;
- Metadatenschleifen mit `Get-Item`: `1`;
- `Get-Item` in dieser Metadatenschleife: `1`;
- darin verschachtelte Schleifen: `0`;
- Retry-Begriffe oder Warteaufrufe: `0`;
- Kindprozess-, Import-, dynamische Ausfuehrungs- oder Netzwerkbefehle: `0`;
- finales Ausgabeziel vorhanden: nein;
- Stagingziel vorhanden: nein;
- `git diff --check`: ohne Befund;
- Skriptausfuehrungen: `0`;
- Policy-Probes: `0`;
- Realpfadabfragen: `0/54`;
- erzeugte Inventurartefakte: `0`.

Die Gegenbaseline ist der statische Nullzustand: kein Prozessstart, kein Skriptaufruf, keine Realpfadabfrage und keine Ausgabeerzeugung.

## Technische Interpretation

Die Implementierung entspricht statisch dem freigegebenen Entwurf. Der Probe-Zweig ist vor Produktionskonstanten abgeschlossen. Der Produktionszweig bindet Ausschlussmenge, Bytegroesse, SHA-256, Eintragszahl und beide Ausgabeziele fest. Die einzige Metadatenschleife enthaelt genau eine Abfrage je Eintrag; nur `ItemNotFoundException` wird als regulaeres `missing` behandelt, alle anderen Fehler unterliegen dem globalen Abbruchvertrag. Staging wird strukturell rueckvalidiert und erst danach final verschoben.

## Grenzen und nicht gepruefte Annahmen

Die statische Abnahme belegt keine Laufzeitwirkung. Insbesondere wurden weder Policy-Akzeptanz noch exakte Laufzeitausgabe, Dateizugriffsfreiheit des Probe-Zweigs, Produktionsinventur oder Finalisierung praktisch beobachtet. Die 54 Realpfade wurden nicht gelesen. Es folgt daraus keine Freigabe fuer `-PolicyProbe`, Produktion, Manifest, Resolver, G2 oder Huerde G und kein G1- oder MCM-Befund.

## Konkrete Schlussfolgerung

Die unabhaengige statische Abnahme von `213ZZF` ist bestanden. Dokumentbindung, Parser/AST, Pfade, Bytes, SHA-256, Literale, Probe-Kontrollfluss, einmalige Metadatenschleife, Ein-Prozess- und Kein-Retry-Regel sind konsistent. Keine Zielabweichung ist erkennbar.

## Naechster begrenzter Schritt

Als naechstes ist ausschliesslich ein statischer Ausfuehrungsvertrag fuer genau einen spaeteren Aufruf von `tools/run_realpath_metadata_inventory.ps1 -PolicyProbe` vorzuschlagen. Er muss Skriptbytes und SHA-256, exakten Aufruf, erwartete einzelne JSON-Zeile, Exitcode `0`, Nullbindung fuer Realpfadabfragen und Artefakte sowie sofortigen Abbruch bei jeder Abweichung festlegen. Der Probe-Aufruf selbst und jede Produktionsausfuehrung bleiben bis zu einer gesonderten Folgefreigabe gesperrt.
