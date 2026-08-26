# 213ZZN - Rohbytebasierter statischer Beobachtungsvertrag fuer Policy-Probe

## Einordnung

`213ZZN` ist kein Forschungslauf und erhaelt keine Laufnummer. Das Dokument revidiert ausschliesslich den statischen Beobachtungsvertrag `213ZZL`. Es wurde kein Host, Skript oder Diagnoseprozess gestartet und keine Ausfuehrungsfreigabe erzeugt.

## Forschungsfrage und Auftrag

Kann die Erfolgsentscheidung eines eventuell spaeter separat freizugebenden einzelnen `-PolicyProbe`-Aufrufs vollstaendig aus gebundenen Rohbytes reproduziert werden, ohne eine Textdekodierung oder eine nicht protokollierte Ausgabekodierung zu verwenden?

## Verwendete Quellen

- aktueller Uebergabe-Eingang;
- `docs/forschung/213ZZM_G1_213ZZL_UNABHAENGIGE_STATISCHE_ABNAHME.md`;
- `docs/forschung/213ZZL_G1_POLICYPROBE_KORRIGIERTER_STATISCHER_BEOBACHTUNGSVERTRAG.md`;
- `tools/run_realpath_metadata_inventory.ps1`.

Keine externen Quellen wurden verwendet.

## Verwendete Dateien und Schnittstellen

Die genannten Dateien wurden ausschliesslich statisch gelesen. Fuer einen spaeteren, weiterhin gesperrten Aufruf ist nur `System.Diagnostics.Process` mit `UseShellExecute=false`, `StandardOutput.BaseStream`, `StandardError.BaseStream` und zwei getrennten `System.IO.MemoryStream`-Puffern vorgesehen. Es gibt keine Beobachtungs-, Fehler- oder Umleitungsdatei.

## Feste Identitaets- und Aufrufbindungen

- Skriptpfad: `C:/Users/TV/Documents/MCM_FIELD_ORGANISM/workspace/tools/run_realpath_metadata_inventory.ps1`;
- Skriptbytes: `5085`;
- Skript-SHA-256: `8E7AAD2C3FF5E397FE54B81CC6EF1F72CCA82BDF36DD834E6C50D2B232EAF13B`;
- Host: `C:\Windows\System32\WindowsPowerShell\v1.0\powershell.exe`;
- Argumentstring: `-NoLogo -NoProfile -NonInteractive -File C:\Users\TV\Documents\MCM_FIELD_ORGANISM\workspace\tools\run_realpath_metadata_inventory.ps1 -PolicyProbe`;
- Aufruf-ID-Bildung: SHA-256 ueber UTF-8 ohne BOM der ordinalen Verkettung `Host + U+0000 + Argumentstring`;
- Aufruf-ID-SHA-256: `59E703561A02D51F3A23E74D7BC2FB88C2936CD3E529D32EC3D1964F8164658A`;
- finales Ausgabeziel: `C:/Users/TV/Documents/MCM_FIELD_ORGANISM/workspace/reports/213ZZ_g1_realpath_inventory.json`;
- Stagingziel: `C:/Users/TV/Documents/MCM_FIELD_ORGANISM/workspace/reports/.213ZZ_g1_realpath_inventory.json.staging`.

## Feste Rohbyte-Erwartung

Die erwartete Standardausgabe ist statisch als folgende Bytefolge definiert:

1. UTF-8 ohne BOM des ordinal unveraenderten ASCII-Literals `{"schema_version":"g1-realpath-inventory-policy-probe-v1","policy_probe":true,"realpath_queries":0,"artifacts_written":0}`;
2. unmittelbar gefolgt von genau den Bytes `0D 0A` (CRLF);
3. keine weiteren Bytes.

Verbindliche Sollwerte:

- `expected_stdout_bytes`: `123`;
- `expected_stdout_base64`: `eyJzY2hlbWFfdmVyc2lvbiI6ImcxLXJlYWxwYXRoLWludmVudG9yeS1wb2xpY3ktcHJvYmUtdjEiLCJwb2xpY3lfcHJvYmUiOnRydWUsInJlYWxwYXRoX3F1ZXJpZXMiOjAsImFydGlmYWN0c193cml0dGVuIjowfQ0K`;
- `expected_stdout_sha256`: `8FB301FE4D2E5D5208CC0DA2682FF5E49661155BB58CC9E1DF158727F4C7E877`;
- `expected_stderr_bytes`: `0`;
- `expected_stderr_base64`: leere Zeichenfolge;
- `expected_stderr_sha256`: `E3B0C44298FC1C149AFBF4C8996FB92427AE41E4649B934CA495991B7852B855`.

Diese Definition bindet die Byteerwartung, nicht die Dekodierung eines beobachteten Stroms. Beobachtete Rohbytes duerfen fuer `contract_pass` weder als Text dekodiert noch normalisiert, getrimmt, zeilenweise gelesen oder rekodiert werden. Ein Kodierungsfeld ist deshalb fuer die Erfolgsentscheidung weder erforderlich noch zulaessiger Ersatz fuer den Rohbytevergleich.

## Vorgesehener Beobachtungsablauf

1. Skriptpfad, Bytegroesse und SHA-256 statisch mit den Vorbindungen vergleichen.
2. Final- und Stagingziel auf Nichtvorhandensein pruefen.
3. Bei jeder Vorabweichung ohne Prozessstart genau ein fail-closed Beobachtungsobjekt ausgeben.
4. Nur nach einer separaten spaeteren Freigabe genau einen gebundenen Hostprozess starten.
5. `StandardOutput.BaseStream` und `StandardError.BaseStream` unmittelbar und parallel vollstaendig in getrennte `MemoryStream`-Puffer kopieren.
6. Auf beide Kopieroperationen und das Prozessende warten.
7. Beide Rohbytearrays ohne Dekodierung oder Veraenderung erfassen und daraus Bytezahl, Base64 und SHA-256 bilden.
8. Exitcode sowie den Nachzustand von Final- und Stagingziel erfassen.
9. Genau ein JSON-Beobachtungsobjekt auf der Standardausgabe des Beobachters ausgeben.
10. Keine Datei erzeugen, keinen Retry, keinen Alternativhost und keinen Diagnoseprozess starten.

## Vollstaendiges In-Memory-Protokoll

Das eine Beobachtungsobjekt enthaelt genau die bereits in `213ZZL` gebundenen 25 Felder:

```text
schema_version
contract_id
script_path
script_bytes_before
script_sha256_before
host_path
argument_string
invocation_id_sha256
pre_final_exists
pre_staging_exists
process_start_attempts
processes_started
retry_count
stdout_bytes
stdout_sha256
stdout_base64
stderr_bytes
stderr_sha256
stderr_base64
exit_code
post_final_exists
post_staging_exists
observer_artifacts_written
contract_pass
failure_reasons
```

Feste Protokollwerte sind `schema_version=g1-policy-probe-observation-v3`, `contract_id=213ZZN`, `process_start_attempts<=1`, `processes_started` gleich `0` oder `1`, `retry_count=0` und `observer_artifacts_written=0`. `failure_reasons` ist eine geordnete Liste ausschliesslich technischer Vertragsabweichungen.

Fuer jeden Strom muss die protokollierte Bytezahl gleich der Laenge des aus dem protokollierten Base64-Wert rekonstruierten Bytearrays sein. Dessen SHA-256 muss dem protokollierten Stromhash entsprechen. Der leere Fehlerstrom wird durch Bytezahl `0`, leeres Base64 und den gebundenen SHA-256 des leeren Bytearrays gemeinsam nachgewiesen.

## Rohbytebasierte Erfolgskriterien

`contract_pass=true` ist genau dann zulaessig, wenn alle folgenden Bedingungen gleichzeitig aus dem 25-Felder-Protokoll und den festen Sollwerten reproduzierbar erfuellt sind:

- alle Skript-, Host-, Argument- und Aufruf-ID-Bindungen stimmen ordinal;
- `pre_final_exists=false` und `pre_staging_exists=false`;
- `process_start_attempts=1`, `processes_started=1` und `retry_count=0`;
- `stdout_bytes=123`;
- `stdout_base64` stimmt ordinal mit `expected_stdout_base64` ueberein;
- `stdout_sha256` stimmt ordinal mit `expected_stdout_sha256` ueberein;
- das aus `stdout_base64` rekonstruierte Bytearray hat 123 Bytes, seinen gebundenen SHA-256 und ist byteweise identisch mit der festen erwarteten Bytefolge;
- `stderr_bytes=0`, `stderr_base64` ist leer und `stderr_sha256` entspricht dem gebundenen Hash des leeren Bytearrays;
- `exit_code=0`;
- `post_final_exists=false` und `post_staging_exists=false`;
- `observer_artifacts_written=0`;
- `failure_reasons` ist leer.

Jede Abweichung setzt `contract_pass=false`. Die Entscheidung verwendet keine Textdekodierung und keine Laufzeitannahme ueber eine Ausgabekodierung.

## Abbruchbedingungen und Sicherheitsgrenzen

Bei abweichender Skriptidentitaet oder belegtem Ziel wird kein Prozess gestartet. Nach einem Start fuehren abweichende Rohbytes, nichtleerer Standardfehler, Exitcode ungleich `0`, Artefaktentstehung oder Protokollinkonsistenz ausschliesslich zum fail-closed Ergebnis. Es folgen kein zweiter Startversuch, keine Ursachenanalyse, keine Policy-Abfrage, kein Registry-Zugriff, kein Alternativhost und kein Produktionspfad. Der Beobachter darf weder Final-/Stagingdateien noch temporaere Protokolldateien erzeugen.

## Durchgefuehrte Schritte

1. Den Kodierungsfehler aus `213ZZM` gegen `213ZZL` abgegrenzt.
2. Das Skriptliteral des `-PolicyProbe`-Zweigs statisch gelesen.
3. Erwartete Standardausgabe als UTF-8-ohne-BOM-Rohbytes plus CRLF festgelegt.
4. Bytezahl, Base64 und SHA-256 der erwarteten Standardausgabe statisch gebunden.
5. Leeren Standardfehler mit Bytezahl, Base64 und SHA-256 gebunden.
6. Die 25 Protokollfelder und bisherigen Prozess-, Retry-, Artefakt- und Abbruchregeln beibehalten.
7. Jede textdekodierungsabhaengige Erfolgsbedingung entfernt.

## Messergebnisse und Gegenbaselines

- Skriptbytes: `5085`;
- Skript-SHA-256: `8E7AAD2C3FF5E397FE54B81CC6EF1F72CCA82BDF36DD834E6C50D2B232EAF13B`;
- Protokollfelder: `25`;
- erwartete Standardausgabe: `123` Rohbytes;
- erwarteter Standardfehler: `0` Rohbytes;
- benoetigte Dekodierung beobachteter Stroeme: `0`;
- in dieser Revision gestartete Prozesse: `0`;
- Probe-, Diagnose- oder Produktionsaufrufe: `0`;
- Realpfadabfragen: `0`;
- erzeugte Laufartefakte: `0`.

Die Gegenbaseline ist `213ZZL`: Dort war die Rohstromaufnahme gebunden, die Erfolgsentscheidung aber wegen einer nicht gebundenen Textdekodierung unterbestimmt. `213ZZN` ersetzt nur dieses Kriterium durch einen vollstaendigen Rohbytevergleich.

## Grenzen und nicht gepruefte Annahmen

Der Vertrag wurde nicht ausgefuehrt. Nicht praktisch geprueft wurden Prozessstart, parallele Streamaufnahme, tatsaechliche Ausgabe, Exitcode und Nachzustand. Die festgelegte Sollbytefolge folgt statisch aus dem gebundenen Skriptzweig und der expliziten CRLF-Vertragsanforderung; ob ein spaeterer Prozess diese Folge liefert, bleibt offen. Die Ursache des frueheren Abbruchs bleibt offen. Es gibt keinen G1- oder MCM-Befund.

## Konkrete Schlussfolgerung

`213ZZN` beseitigt die in `213ZZM` festgestellte Unterbestimmung: `contract_pass` ist ohne Dekodierung allein aus festen erwarteten Rohbytes und den protokollierten Bytezahl-, Base64- und SHA-256-Werten reproduzierbar. Ein-Prozess-, Kein-Retry-, Null-Artefakt-, freie-Ziele- und Fail-closed-Regeln bleiben erhalten. Eine Ausfuehrungsfreigabe entsteht nicht. Keine Zielabweichung ist erkennbar.

## Naechster begrenzter Schritt

Als naechstes ist ausschliesslich die unabhaengige statische Abnahme von `213ZZN` vorzunehmen. Zu pruefen sind die feste Rohbytefolge, Bytezahl, Base64, SHA-256, die 25 Protokollfelder, Skript-, Host-, Argument- und Aufruf-ID-Bindung, `BaseStream`-Erfassung, Ein-Prozess-, Kein-Retry-, Null-Artefakt-, freie-Ziele- und Fail-closed-Regeln. Jeder tatsaechliche Aufruf bleibt gesperrt.
