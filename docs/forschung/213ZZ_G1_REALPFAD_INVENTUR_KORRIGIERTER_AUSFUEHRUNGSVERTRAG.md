# 213ZZ - Korrigierter statischer Ausfuehrungsvertrag fuer die G1-Realpfad-Metadateninventur

## Einordnung

`213ZZ` ist kein Forschungslauf und erhaelt keine Laufnummer. Das Dokument definiert ausschliesslich einen statischen Vertrag fuer genau einen spaeteren read-only Inventurversuch. Es implementiert kein Werkzeug und fuehrt weder die Inventur noch einen Zugriff auf einen der 54 gebundenen Realpfade aus.

## Forschungsfrage und Auftrag

Kann der nach `213ZX` technisch abgebrochene Inventurversuch durch eine kurze, dateibasierte PowerShell-Schnittstelle methodisch neu gebunden werden, ohne den Umfang aus `213ZV` zu erweitern oder bereits einen G1-Befund vorwegzunehmen?

Der Auftrag ist auf die Festlegung dieses Ausfuehrungsvertrags begrenzt. Die spaetere Skriptimplementierung, deren statische Abnahme und der Inventurversuch sind getrennte Folgeschritte.

## Verwendete Quellen

- aktueller Uebergabe-Eingang;
- `docs/forschung/213ZY_G1_213ZX_UNABHAENGIGE_STATISCHE_ABNAHME.md`;
- `docs/forschung/213ZX_G1_REALPFAD_INVENTUR_TECHNISCHER_VORLAUFABBRUCH.md`;
- `docs/forschung/213ZV_G1_REALPFAD_INVENTUR_FREIGABEVORSCHLAG.md`;
- `docs/forschung/213Z_G1_REALPFAD_AUSSCHLUSSMENGE.json`.

Keine externen Quellen wurden verwendet.

## Gebundene Ausgangsbasis

| Objekt | Bytes | SHA-256 |
|---|---:|---|
| `213ZY_G1_213ZX_UNABHAENGIGE_STATISCHE_ABNAHME.md` | 3558 | `6E56186FA8C2120F4C445493748E236AF1A3D226023ECF773B20D3A9B288687B` |
| `213ZX_G1_REALPFAD_INVENTUR_TECHNISCHER_VORLAUFABBRUCH.md` | 2830 | `B8DACAAAADA07C1DABF7FB66703D573621E33106EAE8228D7D74181B6E977D86` |
| `213ZV_G1_REALPFAD_INVENTUR_FREIGABEVORSCHLAG.md` | 8538 | `245743D80ECF4B2D71E815CB92C5823C0DE847B992F6DCEF181E2131C91173E6` |
| `213Z_G1_REALPFAD_AUSSCHLUSSMENGE.json` | 6253 | `52DA5D8DD26314BF173367E7F02D1F1B1055077380E83159A0FAE3EB87304ACF` |

Die Ausschlussmenge muss unmittelbar vor einem spaeteren Versuch erneut exakt 54 Eintraege enthalten: eine CPython-Rolle und 53 native Rollen, keine leeren Pfade und keine nach ordinalem Case-Folding doppelten Pfade.

## Korrigierte Schnittstelle

Der in `213ZX` dokumentierte lange Inline-Befehl bleibt ausgeschlossen. Der neue Vertrag sieht eine kurze, dateibasierte Prozessschnittstelle vor:

```text
C:\Windows\System32\WindowsPowerShell\v1.0\powershell.exe -NoLogo -NoProfile -NonInteractive -File C:\Users\TV\Documents\MCM_FIELD_ORGANISM\workspace\tools\run_realpath_metadata_inventory.ps1
```

Gebundener Skriptpfad:

```text
C:/Users/TV/Documents/MCM_FIELD_ORGANISM/workspace/tools/run_realpath_metadata_inventory.ps1
```

- UTF-8-Laenge des Pfadstrings: `92` Bytes
- SHA-256 des Pfadstrings: `E3667A1D02783E5FBC39DBF3D5499C548F9352E0900A3806CAB5BA4F398B5E37`
- gegenwaertiger Zustand: Datei nicht vorhanden

Die Schnittstelle gilt erst dann als ausfuehrbar, wenn das Skript in einem getrennten, eng begrenzten Entwicklungsschritt erstellt, nach Bytes und SHA-256 gebunden und unabhaengig statisch abgenommen wurde. Diese Abnahme muss insbesondere bestaetigen, dass der exakte kurze Aufruf von der geltenden Ausfuehrungspolicy akzeptiert wird, ohne einen Realpfad abzufragen oder eine Inventurausgabe zu erzeugen. Bis dahin ist die Schnittstelle nur ein statischer Vertragsentwurf.

## Neue Ausgabebindung

Finaler Pfad:

```text
C:/Users/TV/Documents/MCM_FIELD_ORGANISM/workspace/reports/213ZZ_g1_realpath_inventory.json
```

- UTF-8-Laenge des Pfadstrings: `91` Bytes
- SHA-256 des Pfadstrings: `94ED5C2D03E4EDE789A56B102E197E45532C7A91A6D18179F0C8B5A1F331E4AF`
- gegenwaertiger Zustand: nicht vorhanden

Stagingpfad:

```text
C:/Users/TV/Documents/MCM_FIELD_ORGANISM/workspace/reports/.213ZZ_g1_realpath_inventory.json.staging
```

- UTF-8-Laenge des Pfadstrings: `100` Bytes
- SHA-256 des Pfadstrings: `BF6CB48921A022B21CA74FB0E4E4FEF6D8B775FB107D92D6BA267C014C385BA8`
- gegenwaertiger Zustand: nicht vorhanden

Existiert unmittelbar vor dem spaeteren Prozessstart einer der beiden Pfade, muss der Versuch vor der ersten Realpfadabfrage abbrechen. Ueberschreiben, Anhaengen und automatische Wiederholung sind ausgeschlossen.

## Erlaubte Handlung

Nach allen Vorbedingungen darf genau ein PowerShell-Prozess gestartet werden. Dieser darf die 54 bereits gebundenen Realpfade genau einmal in ihrer gebundenen Reihenfolge ausschliesslich auf folgende Dateisystemmetadaten abfragen:

- `exists`: Existenz des gebundenen Pfades;
- `item_type`: `file`, `directory`, `other` oder `missing`;
- `size_bytes`: Dateigroesse fuer Dateien, sonst `null`.

Dateiinhalte, Dateihashes, Versionsinformationen, Signaturen, Importtabellen, Abhaengigkeiten, Laufzeitverhalten und fachliche Interpretation sind nicht Bestandteil der Inventur.

## Ausgabeschema

Die finale JSON-Datei muss genau ein Objekt mit diesen Feldern enthalten:

```json
{
  "schema_version": "g1-realpath-metadata-inventory-v1",
  "source_exclusion_set_sha256": "52DA5D8DD26314BF173367E7F02D1F1B1055077380E83159A0FAE3EB87304ACF",
  "entry_count": 54,
  "entries": [
    {
      "ordinal": 1,
      "role": "bound role from exclusion set",
      "path": "bound real path",
      "exists": true,
      "item_type": "file",
      "size_bytes": 123
    }
  ]
}
```

Die Ausgabe wird zuerst vollstaendig am Stagingpfad erzeugt, strukturell validiert und danach atomar auf den finalen Pfad verschoben. Bei Fehlern darf keine finale Datei entstehen. Ein verbleibendes Stagingartefakt ist als technischer Fehler zu dokumentieren und darf nicht durch einen zweiten Inventuraufruf behandelt werden.

## Zwingende Vorbedingungen und Abbruchbedingungen

Vor dem spaeteren Prozessstart muessen alle folgenden Bedingungen erfuellt sein:

1. Die vier gebundenen Ausgangsdokumente stimmen in Dateigroesse und SHA-256 ueberein.
2. Das spaeter implementierte Skript stimmt mit seiner separat abgenommenen Byte- und SHA-256-Bindung ueberein.
3. Die Ausschlussmenge besteht weiterhin aus genau 54 gueltigen und eindeutigen Bindungen.
4. Finaler Ausgabe- und Stagingpfad sind nicht vorhanden.
5. Die unabhaengige statische Abnahme dieses Vertrags sowie die separate statische Abnahme der Skriptimplementierung liegen vor.
6. Der exakte kurze Prozessaufruf wurde ohne Realpfadzugriff und ohne Zielartefakt als policy-akzeptiert bestaetigt.

Ist eine Bedingung nicht erfuellt, muss vor Prozessstart abgebrochen werden. Nach Prozessstart fuehrt jede Schemaabweichung, unerwartete Ausnahme, zusaetzliche Pfadabfrage oder zusaetzliche Ausgabe zum Abbruch ohne Wiederholung.

## Ausschluesse

Ausdruecklich ausgeschlossen bleiben:

- ein zweiter oder automatischer Inventurversuch;
- Aenderungen an den 54 Realzielen;
- Inhaltsanalyse oder Ausfuehrung der gebundenen Realziele;
- Manifest- oder Resolver-Arbeit;
- G2-Arbeit und Huerde-G-Arbeit;
- Kamera, Mikrofon, reale Sensorik, Marker oder physische Rueckkopplung;
- Aussagen zu G1, MCM-Memory, Organisation, Topologie, Semantik oder KI.

## Durchgefuehrte Schritte und Messwerte

- Dokument- und Pfadbindungen statisch festgelegt;
- kurze dateibasierte Schnittstelle definiert;
- neues finales Ziel und neuer Stagingpfad festgelegt;
- gestartete Inventurprozesse: `0`;
- abgefragte Realpfade: `0/54`;
- erzeugte Inventurartefakte: `0`;
- Skriptimplementierungen: `0`;
- Manifest-, Resolver-, G2- und Huerde-G-Arbeit: jeweils `0`.

Die Nullwerte sind die Gegenbaseline fuer diesen reinen Vertragschritt.

## Grenzen und nicht gepruefte Annahmen

Die Policy-Akzeptanz des kurzen Aufrufs ist noch nicht beobachtet. Das Skript existiert noch nicht und besitzt daher noch keine Bytebindung. Existenz, Typ und Groesse der 54 Realziele sind weiterhin ungeprueft. Der Vertrag liefert keinen G1- oder MCM-Forschungsbefund.

## Konkrete Schlussfolgerung

Ein korrigierter, eng begrenzter Ausfuehrungsvertrag ist statisch formuliert. Er beseitigt die bekannte Abhaengigkeit von einem langen Inline-Befehl, behauptet jedoch keine bereits nachgewiesene Policy-Akzeptanz. Ohne getrennte Abnahme dieses Vertrags und einer spaeteren minimalen Skriptimplementierung bleibt jeder Inventurversuch gesperrt. Eine Zielabweichung ist nicht erkennbar.

## Naechster begrenzter Schritt

Als naechstes ist ausschliesslich eine unabhaengige statische Abnahme von `213ZZ` vorzunehmen. Geprueft werden muessen Dokumentbindungen, neue Pfade, Ausgabeschema, Ein-Prozess-/Kein-Retry-Regel, Policy-Akzeptanz-Gate, Abbruchbedingungen und Ausschluesse. Erst nach bestandener Abnahme darf ein separater Vorschlag fuer die minimale Skriptimplementierung und deren statische Validierung vorgelegt werden; die Inventur selbst bleibt dabei weiterhin ausgeschlossen.
