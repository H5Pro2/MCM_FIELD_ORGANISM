# 213ZZP - Rohbytebasierter statischer Ausfuehrungsvertrag fuer einen Policy-Probe-Einzelaufruf

## Einordnung

`213ZZP` ist kein Forschungslauf und erhaelt keine Laufnummer. Das Dokument ist ausschliesslich ein statischer Ausfuehrungsvertrag fuer genau einen eventuell spaeter separat freizugebenden `-PolicyProbe`-Einzelaufruf. Es wurde kein Host, Skript, Probe-, Diagnose- oder Produktionsprozess gestartet und keine Ausfuehrungsfreigabe erzeugt.

## Forschungsfrage und Auftrag

Kann genau ein spaeterer `-PolicyProbe`-Aufruf so fest gebunden werden, dass Identitaet, Aufruf, Rohstrombeobachtung, Vor- und Nachzustand sowie jeder Erfolg oder Abbruch aus einem einzigen 25-Felder-Konsolenprotokoll reproduzierbar und fail-closed entschieden werden koennen?

## Verwendete Quellen

- aktueller Uebergabe-Eingang;
- `docs/forschung/213ZZN_G1_POLICYPROBE_ROHBYTEBASIERTER_STATISCHER_BEOBACHTUNGSVERTRAG.md`;
- `docs/forschung/213ZZO_G1_213ZZN_UNABHAENGIGE_STATISCHE_ABNAHME.md`;
- `tools/run_realpath_metadata_inventory.ps1`.

Keine externen Quellen wurden verwendet.

## Verwendete Dateien und Schnittstellen

Die Quellen wurden ausschliesslich statisch gelesen. Ein eventuell spaeter separat freizugebender Beobachter darf nur `System.Diagnostics.Process` mit `UseShellExecute=false`, umgeleiteter Standardausgabe und umgeleitetem Standardfehler verwenden. Beide `BaseStream`-Schnittstellen muessen parallel und vollstaendig in zwei getrennte `System.IO.MemoryStream`-Puffer kopiert werden. Der Beobachter darf keine lokale Protokoll-, Umleitungs-, Fehler- oder Temporaerdatei erzeugen.

## Unveraenderte Vorbindungen

- Vertrags-ID: `213ZZP`;
- Beobachtungsschema: `g1-policy-probe-observation-v3`;
- Skriptpfad: `C:/Users/TV/Documents/MCM_FIELD_ORGANISM/workspace/tools/run_realpath_metadata_inventory.ps1`;
- Skriptbytes: `5085`;
- Skript-SHA-256: `8E7AAD2C3FF5E397FE54B81CC6EF1F72CCA82BDF36DD834E6C50D2B232EAF13B`;
- einziger Host: `C:\Windows\System32\WindowsPowerShell\v1.0\powershell.exe`;
- einziger Argumentstring: `-NoLogo -NoProfile -NonInteractive -File C:\Users\TV\Documents\MCM_FIELD_ORGANISM\workspace\tools\run_realpath_metadata_inventory.ps1 -PolicyProbe`;
- Aufruf-ID-Bildung: SHA-256 ueber UTF-8 ohne BOM der ordinalen Verkettung `Host + U+0000 + Argumentstring`;
- Aufruf-ID-SHA-256: `59E703561A02D51F3A23E74D7BC2FB88C2936CD3E529D32EC3D1964F8164658A`;
- finales Ausgabeziel: `C:/Users/TV/Documents/MCM_FIELD_ORGANISM/workspace/reports/213ZZ_g1_realpath_inventory.json`;
- Stagingziel: `C:/Users/TV/Documents/MCM_FIELD_ORGANISM/workspace/reports/.213ZZ_g1_realpath_inventory.json.staging`.

Relative Pfade, ein anderer Host, zusaetzliche Argumente, geaenderte Argumentreihenfolge, Shellvermittlung, Produktionsmodus und jeder Aufruf ohne `-PolicyProbe` sind ausgeschlossen.

## Unveraenderte Rohbyte-Sollwerte

Die erwartete Standardausgabe besteht aus UTF-8 ohne BOM des ordinalen ASCII-Literals

`{"schema_version":"g1-realpath-inventory-policy-probe-v1","policy_probe":true,"realpath_queries":0,"artifacts_written":0}`

unmittelbar gefolgt von exakt `0D 0A` und keinen weiteren Bytes.

- erwartete Standardausgabebytes: `123`;
- erwartetes Standardausgabe-Base64: `eyJzY2hlbWFfdmVyc2lvbiI6ImcxLXJlYWxwYXRoLWludmVudG9yeS1wb2xpY3ktcHJvYmUtdjEiLCJwb2xpY3lfcHJvYmUiOnRydWUsInJlYWxwYXRoX3F1ZXJpZXMiOjAsImFydGlmYWN0c193cml0dGVuIjowfQ0K`;
- erwarteter Standardausgabe-SHA-256: `8FB301FE4D2E5D5208CC0DA2682FF5E49661155BB58CC9E1DF158727F4C7E877`;
- erwartete Standardfehlerbytes: `0`;
- erwartetes Standardfehler-Base64: leere Zeichenfolge;
- erwarteter Standardfehler-SHA-256: `E3B0C44298FC1C149AFBF4C8996FB92427AE41E4649B934CA495991B7852B855`;
- erwarteter Exitcode: `0`.

Fuer die Erfolgsentscheidung ist jede Textdekodierung, Normalisierung, Trimmung, zeilenweise Erfassung oder Rekodierung der beobachteten Stroeme ausgeschlossen.

## Verbindliche Vorpruefungen

Vor jedem Startversuch muss der Beobachter in dieser Reihenfolge pruefen:

1. Skriptpfad stimmt ordinal mit der Bindung ueberein.
2. Skript ist eine regulaere vorhandene Datei.
3. Skriptgroesse ist exakt `5085` Bytes.
4. Skript-SHA-256 stimmt exakt mit der Bindung ueberein.
5. Hostpfad und Argumentstring stimmen ordinal mit den Bindungen ueberein.
6. Reproduzierte Aufruf-ID stimmt exakt mit der Bindung ueberein.
7. Finalziel existiert nicht.
8. Stagingziel existiert nicht.

Scheitert eine Vorpruefung, sind `process_start_attempts=0`, `processes_started=0`, `retry_count=0` und `contract_pass=false` zu protokollieren. Danach endet der Vertrag ohne Prozessstart.

## Einziger zulaessiger Start

Nur wenn alle Vorpruefungen bestanden sind und eine spaetere separate Ausfuehrungsfreigabe genau diesen Vertrag nennt, darf der Beobachter genau einmal `System.Diagnostics.Process.Start()` fuer den gebundenen Host und den gebundenen Argumentstring aufrufen.

- `process_start_attempts` darf nie groesser als `1` werden;
- `processes_started` darf nur `0` oder `1` sein;
- `retry_count` bleibt immer `0`;
- ein Startfehler fuehrt unmittelbar zu `contract_pass=false`;
- ein Startfehler darf keinen zweiten Versuch oder Alternativhost ausloesen;
- der Beobachter darf keinen weiteren Kindprozess absichtlich starten.

## Verbindliche Rohstromaufnahme

Nach erfolgreichem Start muessen `StandardOutput.BaseStream` und `StandardError.BaseStream` unmittelbar parallel bis zum jeweiligen Streamende in getrennte `MemoryStream`-Puffer kopiert werden. Erst nach Abschluss beider Kopieroperationen und des Prozesses duerfen Bytearrays, Exitcode und Nachzustand ausgewertet werden.

Aus jedem unveraenderten Bytearray werden ausschliesslich folgende Werte gebildet:

- Bytezahl;
- Base64;
- SHA-256.

Die Bytezahl muss der Laenge des aus Base64 rekonstruierten Bytearrays entsprechen. Dessen SHA-256 muss mit dem Stromhash uebereinstimmen. Jede Inkonsistenz ist fail-closed.

## Verbindliche Nachpruefungen

Nach Prozessende muss der Beobachter genau einmal pruefen:

1. Standardausgabe stimmt byteweise mit allen drei Sollbindungen ueberein.
2. Standardfehler stimmt als leeres Bytearray mit allen drei Sollbindungen ueberein.
3. Exitcode ist exakt `0`.
4. Finalziel existiert weiterhin nicht.
5. Stagingziel existiert weiterhin nicht.
6. Der Beobachter hat `0` Artefakte geschrieben.
7. Prozess- und Retry-Zahlen entsprechen dem Vertrag.

Eine Abweichung erzeugt ausschliesslich ein fail-closed Protokollergebnis. Es folgen keine Ursachenanalyse und kein weiterer Aufruf.

## Verbindliches 25-Felder-Protokoll

Der Beobachter gibt abschliessend genau ein JSON-Objekt auf seiner Standardausgabe aus. Es enthaelt genau diese 25 Felder:

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

`failure_reasons` ist eine geordnete Liste ausschliesslich technischer Vertragsabweichungen. Kann ein Wert wegen eines Vorabbruchs oder Startfehlers nicht beobachtet werden, muss das zugehoerige Feld als JSON `null` erscheinen und der technische Grund in `failure_reasons` stehen. Das Protokoll selbst wird nicht lokal persistiert.

## Contract-pass-Entscheidung

`contract_pass=true` ist nur zulaessig, wenn gleichzeitig gilt:

- alle Vorpruefungen bestanden;
- `process_start_attempts=1`;
- `processes_started=1`;
- `retry_count=0`;
- alle Standardausgabe-Rohbytebindungen stimmen;
- alle Standardfehler-Rohbytebindungen stimmen;
- `exit_code=0`;
- Final- und Stagingziel waren vor und nach dem Aufruf frei;
- `observer_artifacts_written=0`;
- `failure_reasons` ist leer;
- alle 25 Protokollfelder sind vorhanden und intern konsistent.

Jede einzelne Abweichung setzt `contract_pass=false`. Ein fehlgeschlagener Vertrag ist verbraucht und darf nicht wiederholt werden.

## Abbruch- und Ausschlussregeln

Der Vertrag verbietet ausdruecklich:

- Retry oder Wiederholungsaufruf;
- Alternativhost oder geaenderte Argumente;
- Diagnose-, Produktions- oder Inventuraufruf;
- Realpfadabfrage;
- lokale Beobachtungs- oder Umleitungsartefakte;
- Manifest-, Resolver-, G2- oder Huerde-G-Arbeit;
- Ursachenbehauptungen aus einem technischen Fehler;
- G1- oder MCM-Befundbehauptungen.

## Durchgefuehrte Schritte

1. Identitaeten und Hashwerte aus `213ZZN` und `213ZZO` statisch abgeglichen.
2. Rohbyte-Sollwerte unveraendert uebernommen.
3. Alle 25 Protokollfelder unveraendert uebernommen.
4. Vorpruefungen, einziger Startversuch, parallele Rohstromaufnahme und Nachpruefungen verbindlich geordnet.
5. Vorabbruch, Startfehler und Nachabweichung jeweils fail-closed definiert.
6. Null-Artefakt-, Kein-Retry- und Ausschlussregeln gebunden.

## Messergebnisse und Gegenbaselines

- Skriptbytes statisch gemessen: `5085`;
- Skript-SHA-256 statisch gemessen: `8E7AAD2C3FF5E397FE54B81CC6EF1F72CCA82BDF36DD834E6C50D2B232EAF13B`;
- `213ZZN`-Bytes: `9957`;
- `213ZZN`-SHA-256: `8B472C8231996383682E03586A99CB73FDB2D22C3E2082570458D5A3B57F2671`;
- `213ZZO`-Bytes: `6002`;
- `213ZZO`-SHA-256: `B8D2332B7C04BF35644D272CF5E5B86B3348A899AAA2AC8D1D515CA7C555CC30`;
- Protokollfelder: `25`;
- erwartete Standardausgabebytes: `123`;
- erwartete Standardfehlerbytes: `0`;
- in diesem Vertrag gestartete Prozesse: `0`;
- Probe-, Diagnose-, Produktions- oder Inventuraufrufe: `0`;
- Realpfadabfragen: `0`;
- erzeugte Laufartefakte: `0`;
- Finalziel vorhanden: nein;
- Stagingziel vorhanden: nein.

Die Gegenbaseline ist ein nicht gebundener Aufruf oder ein Vertrag mit textdekodierungsabhaengiger Erfolgsentscheidung. Beides wird ausgeschlossen. Gegenueber `213ZZN` wird keine Beobachtungsmechanik geaendert; `213ZZP` ordnet sie ausschliesslich als einmaligen, weiterhin nicht freigegebenen Ausfuehrungsvertrag.

## Grenzen und nicht gepruefte Annahmen

Der Vertrag wurde nicht ausgefuehrt. Prozessstart, Streamparallelitaet, tatsaechliche Rohbytes, Exitcode und Nachzustand wurden nicht praktisch beobachtet. Es wird nicht angenommen, dass ein spaeterer Aufruf erfolgreich ist. Die Ursache eines frueheren technischen Abbruchs bleibt offen. Es liegt kein G1- oder MCM-Befund vor.

## Konkrete Schlussfolgerung

`213ZZP` bindet genau einen eventuell spaeter separat freizugebenden `-PolicyProbe`-Einzelaufruf an die in `213ZZN` und `213ZZO` abgenommenen Identitaeten, Rohbyte-Sollwerte, 25 Protokollfelder und Sicherheitsregeln. Der Vertrag ist statisch und erzeugt keine Ausfuehrungsfreigabe. Keine Zielabweichung ist erkennbar.

## Naechster begrenzter Schritt

Als naechstes ist ausschliesslich die unabhaengige statische Abnahme von `213ZZP` vorzunehmen. Zu pruefen sind unveraenderte Identitaeten und Rohbytewerte, absolute Aufrufstruktur, Vor- und Nachpruefungen, 25 Protokollfelder, Nullbehandlung bei Vorabbruch, `BaseStream`-Parallelitaet, Ein-Prozess-, Kein-Retry-, Null-Artefakt- und Fail-closed-Regeln. Jeder tatsaechliche Aufruf bleibt gesperrt.
