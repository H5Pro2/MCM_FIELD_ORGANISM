# 213ZZD - Minimaler Umsetzungsvorschlag fuer das G1-Realpfad-Inventurskript

## Einordnung

`213ZZD` ist kein Forschungslauf und erhaelt keine Laufnummer. Dieses Dokument ist ausschliesslich der separate Umsetzungsvorschlag nach der statischen Abnahme `213ZZC`. Es erzeugt kein Skript, startet keinen Prozess, fuehrt keinen Policy-Probe aus, fragt keinen Realpfad ab und schreibt keine Inventurdatei.

## Forschungsfrage und Auftrag

Wie ist die in `213ZZB` abgenommene Minimalimplementierung als eng begrenzter Entwicklungsschritt umzusetzen und danach statisch zu binden, ohne bereits eine Ausfuehrung freizugeben?

## Verwendete Quellen

- aktuelles Startsignal und juengste Benutzeranweisung;
- `docs/forschung/213ZZC_G1_213ZZB_UNABHAENGIGE_STATISCHE_ABNAHME.md`;
- `docs/forschung/213ZZB_G1_REALPFAD_INVENTURSKRIPT_STATISCHER_IMPLEMENTIERUNGSVORSCHLAG.md`;
- `docs/forschung/213ZZ_G1_REALPFAD_INVENTUR_KORRIGIERTER_AUSFUEHRUNGSVERTRAG.md`;
- `docs/forschung/213Z_G1_REALPFAD_AUSSCHLUSSMENGE.json`.

Keine externen Quellen wurden verwendet.

## Vorgesehene Datei und unveraenderte Schnittstelle

Einzige spaeter zu erzeugende Datei:

```text
C:/Users/TV/Documents/MCM_FIELD_ORGANISM/workspace/tools/run_realpath_metadata_inventory.ps1
```

Zulaessige Parameteroberflaeche:

```powershell
param([switch]$PolicyProbe)
```

Weitere Parameter, dynamische Pfade, Umgebungsvariablen als Konfiguration, Dot-Sourcing, Modulimporte und Kindprozesse sind ausgeschlossen.

## Fest zu kodierende Konstanten

Die spaetere Implementierung muss genau folgende Vertragswerte als Literale enthalten:

- Ausschlussmenge: `C:/Users/TV/Documents/MCM_FIELD_ORGANISM/workspace/docs/forschung/213Z_G1_REALPFAD_AUSSCHLUSSMENGE.json`;
- erwartete Ausschlussmengengroesse: `6253` Bytes;
- erwarteter SHA-256: `52DA5D8DD26314BF173367E7F02D1F1B1055077380E83159A0FAE3EB87304ACF`;
- finale Ausgabe: `C:/Users/TV/Documents/MCM_FIELD_ORGANISM/workspace/reports/213ZZ_g1_realpath_inventory.json`;
- Stagingausgabe: `C:/Users/TV/Documents/MCM_FIELD_ORGANISM/workspace/reports/.213ZZ_g1_realpath_inventory.json.staging`;
- Schema: `g1-realpath-metadata-inventory-v1`;
- erwartete Eintragszahl: `54`.

## Vorgesehener Quellaufbau

Die spaetere Datei soll in dieser Reihenfolge aufgebaut werden:

1. Parameterblock mit ausschliesslich `[switch]$PolicyProbe`.
2. Strikter Fehlermodus: neueste lokal verfuegbare Sprachstufe, `Set-StrictMode -Version Latest` und `$ErrorActionPreference = 'Stop'`.
3. Sofortiger `if ($PolicyProbe)`-Block als erste operative Verzweigung.
4. Im Probe-Block exakt eine feste JSON-Zeile ueber die Konsolenschnittstelle ausgeben und unmittelbar mit Exitcode `0` enden.
5. Erst nach diesem Ende die Produktionskonstanten deklarieren.
6. Produktionsvorbedingungen pruefen.
7. Ausschlussmenge strukturiert laden und validieren.
8. Genau eine lineare Schleife ueber die 54 gebundenen Eintraege ausfuehren.
9. Ausgabe am Stagingpfad erzeugen und strukturell validieren.
10. Stagingdatei ohne Ueberschreiben auf den finalen Pfad verschieben.
11. Mit Exitcode `0` enden; jeder Fehler endet einmalig mit einem von `0` verschiedenen Exitcode.

## Isolierter Policy-Probe-Zweig

Der Probe-Zweig darf ausschliesslich die bereits in `213ZZB` gebundene Zeile ausgeben:

```json
{"schema_version":"g1-realpath-inventory-policy-probe-v1","policy_probe":true,"realpath_queries":0,"artifacts_written":0}
```

Vor dem anschliessenden Prozessende duerfen keine Produktionskonstante ausgewertet, keine .NET-Dateisystemklasse aufgerufen, kein Cmdlet mit externem Zustand verwendet und kein weiterer Prozess erzeugt werden. Die spaetere statische Abnahme muss bestaetigen, dass dieser Zweig syntaktisch und kontrollflussseitig vor jedem Zugriff endet.

## Produktionsvorbedingungen

Vor der ersten Realpfadabfrage muss die spaetere Implementierung in fester Reihenfolge bestaetigen:

1. Der Skriptstand ist der separat gebundene und abgenommene Stand.
2. Die Ausschlussmengendatei besitzt exakt die festgelegte Bytegroesse und SHA-256.
3. Das JSON besitzt das erwartete Schema und genau 54 gueltige, eindeutige, nicht leere Bindungen.
4. Finale Ausgabe und Stagingausgabe existieren nicht.
5. Es wurde keine zusaetzliche Konfiguration eingebracht.

Die Skriptbindung selbst wird vor Prozessstart extern geprueft; das Skript darf weder sich selbst noch Forschungsdokumente dynamisch aufloesen.

## Minimaler Produktionspfad

Fuer jeden gebundenen Eintrag ist genau eine Metadatenaufnahme erlaubt:

- `exists`;
- `item_type` mit `file`, `directory`, `other` oder `missing`;
- `size_bytes` nur fuer Dateien, sonst `null`.

Verboten bleiben Inhaltslesen, Hashen eines Realziels, Versions- oder Signaturabfrage, Import- oder Resolveranalyse, Rekursion in Verzeichnisse sowie jede fachliche Interpretation. Die Schleife darf keinen Retry- oder Fehlerwiederholungszweig besitzen.

## Ausgabe- und Fehlervertrag

- Die JSON-Struktur folgt unveraendert `213ZZ`.
- Die vollstaendige Ausgabe entsteht zuerst am Stagingpfad.
- Vor dem Verschieben wird sie erneut strukturiert geladen und auf Schema sowie 54 Ergebnisse geprueft.
- Das Verschieben darf keine vorhandene Zieldatei ersetzen.
- Bei einem Fehler entsteht keine finale Datei.
- Ein verbleibendes Stagingartefakt wird nicht automatisch entfernt und loest keinen zweiten Aufruf aus.
- Fehlerausgaben duerfen keine Inhalte der Realziele enthalten.
- Es gibt keinen zweiten Prozess, keinen Retry und keinen alternativen Ausgabeweg.

## Umsetzung und nachfolgende statische Abnahme

Nach gesonderter Freigabe darf genau die eine `.ps1`-Datei erzeugt werden. Unmittelbar danach und weiterhin ohne Skriptausfuehrung sind zu dokumentieren:

- Skriptpfad;
- Bytegroesse;
- SHA-256 der Skriptbytes;
- PowerShell-Parserbefund;
- statischer Kontrollfluss des Probe-Zweigs;
- alle fest kodierten Konstanten;
- Fehlen von Kindprozess-, Netzwerk-, Registry-, Modulimport-, Retry- und alternativen Pfadoperationen;
- unverbrauchter Zustand beider Ausgabeziele;
- `git diff --check`.

Parserpruefung und statische Text-/AST-Pruefung sind Teil der spaeteren Implementierungsabnahme, aber keine Freigabe zum Aufruf der Skriptdatei.

## Durchgefuehrte Schritte und Gegenbaseline

- separaten minimalen Quellaufbau festgelegt;
- Literalbindungen und Kontrollfluss spezifiziert;
- spaetere Abnahmekriterien festgelegt;
- erzeugte Skriptdateien: `0`;
- gestartete Prozesse: `0`;
- Policy-Probes: `0`;
- Realpfadabfragen: `0/54`;
- erzeugte Inventurartefakte: `0`;
- Wiederholungsaufrufe: `0`;
- Manifest-, Resolver-, G2- und Huerde-G-Arbeit: jeweils `0`.

Diese Nullwerte bilden die Gegenbaseline dieses Umsetzungsvorschlags.

## Grenzen und nicht gepruefte Annahmen

Es existiert noch kein umgesetzter Quelltext. Parsergueltigkeit, tatsaechliche Bytebindung, Policy-Akzeptanz, Metadatenaufnahme und atomare Ausgabe wurden nicht beobachtet. Die 54 Realziele wurden nicht abgefragt. Dieses Dokument liefert keinen G1- oder MCM-Forschungsbefund.

## Konkrete Schlussfolgerung

Der spaetere Implementierungsschritt ist auf eine Datei, zwei strikt getrennte Kontrollpfade und fest gebundene Literale begrenzt. Die vorgeschlagene Umsetzung erweitert weder Inventurumfang noch Forschungsziel. Keine Zielabweichung ist erkennbar.

## Naechster begrenzter Schritt

Als naechstes ist ausschliesslich die unabhaengige statische Abnahme von `213ZZD` vorzunehmen. Erst nach deren Bestehen darf die eine Skriptdatei in einem gesondert freigegebenen Entwicklungsschritt implementiert werden. Policy-Probe und Inventurausfuehrung bleiben gesperrt.
