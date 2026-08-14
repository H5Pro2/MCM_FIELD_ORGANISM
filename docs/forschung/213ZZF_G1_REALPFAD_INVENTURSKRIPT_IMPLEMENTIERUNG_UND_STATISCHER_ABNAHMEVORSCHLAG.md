# 213ZZF - Inventurskriptimplementierung und statischer Abnahmevorschlag

## Einordnung

`213ZZF` ist kein Forschungslauf und erhaelt keine Laufnummer. Implementiert wurde ausschliesslich die in `213ZZE` freigegebene Datei. Das Skript wurde nicht ausgefuehrt. Die hier festgehaltene statische Eigenpruefung ersetzt keine unabhaengige Abnahme.

## Forschungsfrage und Auftrag

Kann `tools/run_realpath_metadata_inventory.ps1` gemaess `213ZZD` implementiert und ohne Skriptausfuehrung nach AST, Parser, Pfad, Bytes, SHA-256, Literalbindungen, Probe-Kontrollfluss, Ein-Prozess- und Kein-Retry-Regel fuer eine unabhaengige statische Abnahme gebunden werden?

## Verwendete Quellen

- aktueller Uebergabe-Eingang;
- `docs/forschung/213ZZE_G1_213ZZD_UNABHAENGIGE_STATISCHE_ABNAHME.md`;
- `docs/forschung/213ZZD_G1_REALPFAD_INVENTURSKRIPT_MINIMALER_UMSETZUNGSVORSCHLAG.md`;
- `docs/forschung/213ZZB_G1_REALPFAD_INVENTURSKRIPT_STATISCHER_IMPLEMENTIERUNGSVORSCHLAG.md`;
- `docs/forschung/213ZZ_G1_REALPFAD_INVENTUR_KORRIGIERTER_AUSFUEHRUNGSVERTRAG.md`;
- `docs/forschung/213Z_G1_REALPFAD_AUSSCHLUSSMENGE.json`.

Keine externen Quellen wurden verwendet.

## Verwendete Dateien und Schnittstellen

Neu erstellt wurde ausschliesslich:

```text
tools/run_realpath_metadata_inventory.ps1
```

Zur statischen Eigenpruefung wurden die PowerShell-Klassen `System.Management.Automation.Language.Parser` und AST-Knotentypen verwendet. Die Datei wurde dabei nur geparst, nicht als Skript geladen, dot-gesourct oder ausgefuehrt.

## Durchgefuehrte Schritte

1. Den einzigen Parameter `[switch]$PolicyProbe` implementiert.
2. Strikten Fehlermodus gesetzt und den Probe-Zweig vor allen Produktionskonstanten angeordnet.
3. Im Probe-Zweig ausschliesslich die gebundene JSON-Zeile und unmittelbares `exit 0` implementiert.
4. Ausschlussmenge, Bytegroesse, SHA-256, Ausgabewege, Schema und Eintragszahl als feste Literale gebunden.
5. Produktionsvorbedingungen und strukturierte Validierung der 54er-Ausschlussmenge implementiert.
6. Eine lineare Metadatenabfrage pro Eintrag mit gezielter Behandlung eines regulaer fehlenden Pfades implementiert.
7. Stagingerzeugung, strukturelle Rueckvalidierung und nicht ueberschreibende Finalisierung implementiert.
8. Parser- und AST-Eigenpruefung ohne Skriptausfuehrung vorgenommen.

## Implementierungsbindung

- Pfad: `C:/Users/TV/Documents/MCM_FIELD_ORGANISM/workspace/tools/run_realpath_metadata_inventory.ps1`;
- Bytegroesse: `5085`;
- SHA-256: `8E7AAD2C3FF5E397FE54B81CC6EF1F72CCA82BDF36DD834E6C50D2B232EAF13B`.

## Statische Messergebnisse und Gegenbaseline

- Parserfehler: `0`;
- Parameter: genau `PolicyProbe`;
- Probe-Zweig vor Produktionskonstanten: ja;
- verbotene Befehle aus der Pruefmenge: `0`;
- `Start-Process`, `Invoke-Expression`, `Import-Module`, `Add-Type`, Webaufrufe und `Remove-Item`: nicht vorhanden;
- `for`-Schleifen: `0`;
- `while`-Schleifen: `0`;
- `do`-Schleifen: `0`;
- lineare `foreach`-Schleifen: eine fuer Bindungsvalidierung, eine fuer genau eine Metadatenaufnahme je gebundenem Eintrag;
- Skriptausfuehrungen: `0`;
- Policy-Probes: `0`;
- Realpfadabfragen: `0/54`;
- finale Ausgabe vorhanden: nein;
- Stagingausgabe vorhanden: nein;
- Wiederholungsaufrufe: `0`;
- Manifest-, Resolver-, G2- und Huerde-G-Arbeit: jeweils `0`.

Die Nullwerte bilden die Gegenbaseline der nicht ausgefuehrten Implementierung.

## Geplanter Umfang der unabhaengigen statischen Abnahme

Die Folgeabnahme muss mindestens unabhaengig bestaetigen:

- Pfad, Bytegroesse und SHA-256 der Skriptdatei;
- Parserbefund und AST-Struktur;
- exakt einen Schalterparameter;
- Probe-Kontrollfluss mit Ende vor jedem Datei-, Registry-, Netzwerk-, Prozess- oder Realpfadzugriff;
- vollstaendige und richtige Literalbindungen;
- genau eine Metadatenaufnahme je Eintrag im Produktionspfad;
- korrekte Behandlung von `missing` ohne zweite Abfrage;
- Stagingvalidierung und Finalisierung ohne Ueberschreiben;
- Fehlen von Kindprozessen, Importen, dynamischer Konfiguration, Retry und Alternativpfaden;
- weiterhin unverbrauchte Ausgabeziele;
- `git diff --check`.

Die Folgeabnahme darf das Skript nicht ausfuehren.

## Grenzen und nicht gepruefte Annahmen

Der Parserbefund weist nur syntaktische Gueltigkeit nach. Die Laufzeitwirkung beider Zweige, Policy-Akzeptanz, tatsaechliche Metadatenaufnahme, JSON-Erzeugung und atomare Finalisierung wurden nicht beobachtet. Die 54 Realpfade wurden nicht abgefragt. Es liegt kein G1- oder MCM-Forschungsbefund vor.

## Konkrete Schlussfolgerung

Die eine freigegebene Skriptdatei ist implementiert und statisch gebunden. Die vorlaeufige Eigenpruefung zeigt keine Syntax-, Prozess-, Retry- oder Pfaderweiterung. Eine Ausfuehrungsfreigabe folgt daraus nicht. Keine Zielabweichung ist erkennbar.

## Naechster begrenzter Schritt

Als naechstes ist ausschliesslich die unabhaengige statische Abnahme der gebundenen Skriptimplementierung und von `213ZZF` vorzunehmen. `-PolicyProbe`, Produktionsaufruf, Inventur und Realpfadzugriff bleiben gesperrt.
