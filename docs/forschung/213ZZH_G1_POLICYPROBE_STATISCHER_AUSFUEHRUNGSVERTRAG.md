# 213ZZH - Statischer Ausfuehrungsvertrag fuer eine Policy-Probe

## Einordnung

`213ZZH` ist kein Forschungslauf und erhaelt keine Laufnummer. Dieses Dokument beschreibt ausschliesslich einen spaeteren, einmaligen Aufruf des bereits statisch abgenommenen Probe-Zweigs. Es erteilt keine Ausfuehrungsfreigabe. Bei Erstellung dieses Vertrags wurde das Skript nicht ausgefuehrt.

## Forschungsfrage und Auftrag

Kann genau ein spaeterer Aufruf von `tools/run_realpath_metadata_inventory.ps1 -PolicyProbe` so vorgebunden werden, dass Skriptidentitaet, Prozesszahl, Ausgabe, Exitcode, Null-Realpfadzugriff, Null-Artefakte und Abbruchbedingungen eindeutig pruefbar sind?

## Verwendete Quellen

- aktueller Start- und Uebergabekontext;
- `docs/forschung/213ZZG_G1_213ZZF_UNABHAENGIGE_STATISCHE_ABNAHME.md`;
- `docs/forschung/213ZZF_G1_REALPFAD_INVENTURSKRIPT_IMPLEMENTIERUNG_UND_STATISCHER_ABNAHMEVORSCHLAG.md`;
- `tools/run_realpath_metadata_inventory.ps1`.

Keine externen Quellen wurden verwendet.

## Verwendete Dateien und Schnittstellen

Statisch gelesen wurden das Skript und `213ZZG`. Zur erneuten Bindung wurden Dateibytes, `Get-FileHash` und `Test-Path` verwendet. Weder der PowerShell-Skripthost noch das Inventurskript wurden gestartet.

## Vorbindungen

- Skriptpfad: `C:/Users/TV/Documents/MCM_FIELD_ORGANISM/workspace/tools/run_realpath_metadata_inventory.ps1`;
- Skriptbytes: `5085`;
- Skript-SHA-256: `8E7AAD2C3FF5E397FE54B81CC6EF1F72CCA82BDF36DD834E6C50D2B232EAF13B`;
- finales Ausgabeziel: `C:/Users/TV/Documents/MCM_FIELD_ORGANISM/workspace/reports/213ZZ_g1_realpath_inventory.json`;
- Stagingziel: `C:/Users/TV/Documents/MCM_FIELD_ORGANISM/workspace/reports/.213ZZ_g1_realpath_inventory.json.staging`;
- beide Ausgabeziele muessen unmittelbar vor dem Aufruf fehlen.

Jede Abweichung von Pfad, Bytegroesse, SHA-256 oder Ausgabezielzustand beendet den geplanten Vorgang vor einem Prozessstart.

## Exakter spaeterer Aufruf

Zulaessig ist genau ein neuer Prozess mit genau dieser Argumentstruktur:

```text
C:\Windows\System32\WindowsPowerShell\v1.0\powershell.exe -NoLogo -NoProfile -NonInteractive -File C:\Users\TV\Documents\MCM_FIELD_ORGANISM\workspace\tools\run_realpath_metadata_inventory.ps1 -PolicyProbe
```

Der Aufruf erfolgt ohne `-ExecutionPolicy`, ohne dot-sourcing, ohne Wrapper-Skript, ohne Pipeline in das Skript, ohne weitere Skriptparameter und ohne Umgebungs- oder Konfigurationsinjektion. Standardausgabe, Standardfehler und Exitcode duerfen durch den bereits laufenden Beobachter nur aufgezeichnet, nicht transformiert werden.

## Erwartungsvertrag

Standardausgabe muss aus exakt einer ASCII-kompatiblen JSON-Zeile bestehen, abgeschlossen durch genau den von `Console.Out.WriteLine` erzeugten plattformspezifischen Zeilenumbruch:

```json
{"schema_version":"g1-realpath-inventory-policy-probe-v1","policy_probe":true,"realpath_queries":0,"artifacts_written":0}
```

Weiterhin gilt:

- Exitcode: exakt `0`;
- Standardfehler: `0` Bytes;
- gestartete Kindprozesse: `0`;
- Realpfadabfragen: `0`;
- finale Inventurartefakte: `0`;
- Stagingartefakte: `0`;
- Wiederholungsaufrufe: `0`;
- zulaessige Gesamtzahl gestarteter Probe-Prozesse: `1`.

## Beobachtung und Abbruchregeln

1. Vor dem einzigen Prozessstart Skriptbytes und SHA-256 erneut vergleichen und beide Ausgabeziele auf Nichtvorhandensein pruefen.
2. Bei bestandener Vorpruefung genau den gebundenen Prozess einmal starten.
3. Standardausgabe, Standardfehler und Exitcode unveraendert erfassen.
4. Nach Prozessende ausschliesslich beide gebundenen Ausgabeziele erneut auf Nichtvorhandensein pruefen.
5. Keine Wiederholung, Reparatur, alternative Hostwahl oder erweiterte Diagnose im selben Vorgang durchfuehren.

Als fehlgeschlagen und sofort beendet gilt der Vorgang bei jeder Vorbindungsabweichung, Prozessstartfehlermeldung, zusaetzlichen oder abweichenden Ausgabe, Standardfehlerausgabe, anderem Exitcode, entstandenem Ausgabeziel oder Hinweis auf einen Realpfadzugriff. Ein Fehlschlag erzeugt keine Freigabe fuer einen zweiten Versuch.

## Messergebnisse und Gegenbaseline

- Skriptbytes erneut statisch gemessen: `5085`;
- Skript-SHA-256 erneut statisch gemessen: `8E7AAD2C3FF5E397FE54B81CC6EF1F72CCA82BDF36DD834E6C50D2B232EAF13B`;
- `213ZZG`-Bytes: `5144`;
- `213ZZG`-SHA-256: `D70F32DB3EC5FD629987F39DCF2DAADD1D1B222E7E8A3829EA240CC3D8A19FCC`;
- finales Ausgabeziel vorhanden: nein;
- Stagingziel vorhanden: nein;
- ausgefuehrte Policy-Probes: `0`;
- gestartete Skriptprozesse: `0`;
- Realpfadabfragen: `0/54`;
- erzeugte Inventurartefakte: `0`.

Die Gegenbaseline ist der unveraenderte statische Nullzustand vor jeder Probe-Ausfuehrung.

## Grenzen und nicht gepruefte Annahmen

Nicht geprueft wurden die Existenz oder Startfaehigkeit des festgelegten Skripthosts, die lokale Execution Policy, die Laufzeitausgabe und der tatsaechliche Verzicht auf Dateizugriffe im Probe-Zweig. Der Vertrag ist keine Beobachtung und keine Policy-Freigabe. Produktion, Realpfadinventur, Manifest, Resolver, G2 und Huerde G bleiben ausserhalb des Umfangs. Es liegt kein G1- oder MCM-Befund vor.

## Konkrete Schlussfolgerung

Ein einzelner spaeterer Policy-Probe-Aufruf ist statisch eindeutig und fail-closed vorgebunden. Der Vertrag wahrt Ein-Prozess-, Kein-Retry-, Null-Realpfad- und Null-Artefakt-Regel. Keine Zielabweichung ist erkennbar.

## Naechster begrenzter Schritt

Als naechstes ist ausschliesslich die unabhaengige statische Abnahme dieses Vertrags vorzunehmen. Zu pruefen sind Dokument- und Skriptbindung, Host- und Argumentliteral, fehlendes `-ExecutionPolicy`, exakte Ausgabe, Exitcode, Vor-/Nachpruefungen, Ein-Prozess- und Kein-Retry-Regel sowie alle Abbruchbedingungen. Der `-PolicyProbe`-Aufruf selbst bleibt bis zu einer gesonderten Folgefreigabe gesperrt.
