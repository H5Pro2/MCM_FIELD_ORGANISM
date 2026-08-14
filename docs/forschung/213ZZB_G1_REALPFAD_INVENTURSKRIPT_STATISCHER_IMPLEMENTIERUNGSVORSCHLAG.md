# 213ZZB - Statischer Implementierungsvorschlag fuer das G1-Realpfad-Inventurskript

## Einordnung

`213ZZB` ist kein Forschungslauf und erhaelt keine Laufnummer. Das Dokument ist ausschliesslich ein statischer Implementierungsvorschlag. Es erstellt kein Skript, startet keinen Prozess, fragt keinen der 54 Realpfade ab und erzeugt keine Inventurdatei.

## Forschungsfrage und Auftrag

Wie kann das in `213ZZ` vorgesehene workspace-lokale PowerShell-Skript minimal implementiert und vor einer spaeteren Inventur realpfadfrei auf Policy-Akzeptanz geprueft werden?

## Verwendete Quellen

- aktueller Uebergabe-Eingang;
- `213ZZA` aus dem aktuellen Uebergabeergebnis;
- `docs/forschung/213ZZ_G1_REALPFAD_INVENTUR_KORRIGIERTER_AUSFUEHRUNGSVERTRAG.md`;
- `docs/forschung/213Z_G1_REALPFAD_AUSSCHLUSSMENGE.json`.

Keine externen Quellen wurden verwendet.

## Vorgesehene Datei und Schnittstelle

Spaeterer Skriptpfad:

```text
C:/Users/TV/Documents/MCM_FIELD_ORGANISM/workspace/tools/run_realpath_metadata_inventory.ps1
```

Produktionsaufruf gemaess `213ZZ`:

```text
C:\Windows\System32\WindowsPowerShell\v1.0\powershell.exe -NoLogo -NoProfile -NonInteractive -File C:\Users\TV\Documents\MCM_FIELD_ORGANISM\workspace\tools\run_realpath_metadata_inventory.ps1
```

Realpfadfreier Policy-Pruefaufruf:

```text
C:\Windows\System32\WindowsPowerShell\v1.0\powershell.exe -NoLogo -NoProfile -NonInteractive -File C:\Users\TV\Documents\MCM_FIELD_ORGANISM\workspace\tools\run_realpath_metadata_inventory.ps1 -PolicyProbe
```

Der Parameter `-PolicyProbe` muss als expliziter `switch` implementiert werden. Ohne diesen Parameter gilt der spaetere Aufruf als Produktionspfad. Weitere Parameter, Umgebungsvariablen oder dynamische Pfaduebergaben sind ausgeschlossen.

## Minimaler Implementierungsumfang

Das spaetere Skript darf ausschliesslich folgende fest gebundene Konstanten enthalten:

- Pfad der 54er-Ausschlussmenge;
- deren erwartete Bytegroesse und SHA-256;
- finaler Inventurpfad aus `213ZZ`;
- Stagingpfad aus `213ZZ`;
- Schemawert `g1-realpath-metadata-inventory-v1`;
- erwartete Eintragszahl `54`.

Der Produktionspfad muss in dieser Reihenfolge arbeiten:

1. eigene Ausfuehrungsumgebung und alle fest gebundenen Eingaben pruefen;
2. Ausschlussmengendatei nach Bytes und SHA-256 pruefen;
3. JSON strukturiert laden und exakt 54 eindeutige, nicht leere Pfadbindungen bestaetigen;
4. Nichtvorhandensein von finalem und temporaerem Ausgabepfad bestaetigen;
5. erst danach jeden gebundenen Realpfad genau einmal und in gebundener Reihenfolge auf `exists`, `item_type` und `size_bytes` abfragen;
6. das festgelegte JSON-Schema am Stagingpfad schreiben und strukturell validieren;
7. die vollstaendige Stagingdatei atomar auf den finalen Pfad verschieben;
8. mit Exitcode `0` enden.

Es darf keine Inhalts-, Hash-, Signatur-, Versions-, Import-, Resolver- oder Laufzeitanalyse der 54 Realziele stattfinden.

## Realpfadfreier Policy-Pruefmodus

Bei `-PolicyProbe` muss das Skript unmittelbar nach Parameterbindung exakt folgende JSON-Zeile auf Standardausgabe schreiben und mit Exitcode `0` enden:

```json
{"schema_version":"g1-realpath-inventory-policy-probe-v1","policy_probe":true,"realpath_queries":0,"artifacts_written":0}
```

Im Pruefmodus sind verboten:

- Lesen oder Parsen der Ausschlussmengendatei;
- Existenzpruefungen der 54 Realpfade;
- Pruefung oder Erzeugung der finalen und temporaeren Inventurdatei;
- sonstige Datei-, Registry-, Netzwerk- oder Prozesszugriffe;
- Aufruf des Produktionspfads.

Die Policy-Pruefung weist nur nach, dass der kurze `powershell.exe -File`-Aufruf mit diesem Skript akzeptiert und ausgefuehrt wird. Sie ist kein Inventurversuch und keine Aussage ueber die 54 Realpfade.

## Fehler- und Abbruchvertrag

- Jede verletzte Vorbedingung beendet den Produktionspfad vor der ersten Realpfadabfrage mit einem von `0` verschiedenen Exitcode.
- Nach Beginn der Realpfadabfragen ist keine Wiederholung zulaessig.
- Eine vorhandene finale oder temporaere Ausgabe fuehrt vor Realpfadzugriff zum Abbruch; Ueberschreiben und Anhaengen sind verboten.
- Bei einem Fehler darf keine finale Ausgabe entstehen.
- Ein eventuell verbleibendes Stagingartefakt ist zu dokumentieren; es darf keinen automatischen zweiten Aufruf ausloesen.
- Standardausgabe und Standardfehler duerfen keine Inhalte der Realziele enthalten.

## Spaetere statische Bindung

Nach einer gesondert freigegebenen Implementierung muessen vor jeder Ausfuehrungsfreigabe mindestens festgehalten und unabhaengig geprueft werden:

- exakter Skriptpfad;
- Dateigroesse in Bytes;
- SHA-256 der Skriptbytes;
- PowerShell-Parserbefund ohne Syntaxfehler;
- statischer Nachweis, dass `-PolicyProbe` vor jedem Datei- oder Realpfadzugriff endet;
- statischer Nachweis der fest gebundenen Ein- und Ausgabepfade;
- statischer Nachweis der Ein-Prozess- und Kein-Retry-Regel;
- `git diff --check`.

Die Byte- und SHA-256-Werte koennen in diesem Vorschlag nicht vorweggenommen werden, da noch keine Implementierung existiert. Sie muessen aus den tatsaechlich erzeugten Skriptbytes berechnet werden.

## Getrennte Folgeabnahmen

Die spaetere Entwicklung ist in drei getrennte Entscheidungen aufzuteilen:

1. unabhaengige statische Abnahme dieses Implementierungsvorschlags;
2. gesonderte Freigabe, Implementierung und statische Abnahme des Skripts;
3. erst danach gesonderter Entscheid ueber genau einen realpfadfreien `-PolicyProbe`-Aufruf.

Auch ein bestandener Policy-Pruefaufruf gibt die Inventur nicht automatisch frei. Dafuer bleibt ein weiterer separater Ausfuehrungsentscheid nach erneuter Bindungs- und Zielpfadfrischepruefung erforderlich.

## Ausschluesse

Ausgeschlossen bleiben:

- Skriptimplementierung in diesem Schritt;
- jeder PowerShell-Aufruf in diesem Schritt;
- Inventurausfuehrung und Realpfadabfragen;
- Manifest-, Resolver-, G2- oder Huerde-G-Arbeit;
- Aussagen zu G1, Memory, Feldorganisation, Semantik oder KI.

## Durchgefuehrte Schritte und Messwerte

- statische Produktionsschnittstelle spezifiziert;
- realpfreier Policy-Pruefmodus spezifiziert;
- spaetere Bindungs- und Abnahmekette festgelegt;
- implementierte Skriptdateien: `0`;
- gestartete Prozesse: `0`;
- Realpfadabfragen: `0/54`;
- erzeugte Inventurartefakte: `0`;
- Manifest-, Resolver-, G2- und Huerde-G-Arbeit: jeweils `0`.

Diese Nullwerte bilden die Gegenbaseline des reinen Vorschlags.

## Grenzen und nicht gepruefte Annahmen

Die technische Umsetzbarkeit und Policy-Akzeptanz des vorgeschlagenen Skripts sind noch nicht beobachtet. Es existiert noch keine Skript-Bytebindung. Der Vorschlag prueft weder die 54 Realpfade noch die spaetere atomare Dateierzeugung praktisch. Kein G1- oder MCM-Forschungsbefund.

## Konkrete Schlussfolgerung

Der minimale Implementierungsumfang ist statisch und eng begrenzt beschrieben. Der realpfadfreie `-PolicyProbe` trennt die Policy-Pruefung methodisch von der spaeteren Inventur. Keine Zielabweichung ist erkennbar.

## Naechster begrenzter Schritt

Als naechstes ist ausschliesslich eine unabhaengige statische Abnahme von `213ZZB` vorzunehmen. Zu pruefen sind insbesondere die strikte Trennung von `-PolicyProbe` und Produktionspfad, Nullzugriffsanforderungen, spaetere Byte-/SHA-256-Bindung, Abbruchregeln, gestufte Folgefreigaben und Ausschluesse. Eine Skriptimplementierung oder Ausfuehrung bleibt bis zu deren ausdruecklicher Freigabe ausgeschlossen.
