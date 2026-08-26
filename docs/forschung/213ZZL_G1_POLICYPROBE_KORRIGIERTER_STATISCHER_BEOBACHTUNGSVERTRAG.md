# 213ZZL - Korrigierter statischer Beobachtungsvertrag fuer Policy-Probe

## Einordnung

`213ZZL` ist kein Forschungslauf und erhaelt keine Laufnummer. Dieses Dokument ist ausschliesslich ein statischer Vorschlag fuer die Beobachtung eines eventuell spaeter separat freizugebenden Einzelaufrufs. Es wurde kein Host, Skript oder Diagnoseprozess gestartet.

## Forschungsfrage und Auftrag

Kann ein spaeterer einzelner `-PolicyProbe`-Aufruf so beobachtet werden, dass Standardausgabe und Standardfehler vollstaendig als Rohbytes im Arbeitsspeicher erhalten und gemeinsam mit Exitcode, Skriptidentitaet, Aufrufidentitaet, Prozesszahl, Retry-Zahl und Ausgabezielzustand in genau einem ausgegebenen JSON-Protokoll gebunden werden?

## Verwendete Quellen

- aktueller Uebergabe-Eingang;
- `docs/forschung/213ZZK_G1_213ZZJ_UNABHAENGIGE_STATISCHE_ABNAHME.md`;
- `docs/forschung/213ZZJ_G1_POLICYPROBE_EINMALAUF_TECHNISCHER_ABBRUCH.md`;
- `docs/forschung/213ZZH_G1_POLICYPROBE_STATISCHER_AUSFUEHRUNGSVERTRAG.md`;
- `tools/run_realpath_metadata_inventory.ps1`.

Keine externen Quellen wurden verwendet.

## Verwendete Dateien und Schnittstellen

Statisch gelesen wurden das Skript und die genannten Dokumente. Fuer einen spaeteren, noch nicht freigegebenen Aufruf ist ausschliesslich `System.Diagnostics.Process` mit `UseShellExecute=false`, umgeleiteten Rohstroemen und zwei getrennten `System.IO.MemoryStream`-Puffern vorgesehen. Lokale Beobachtungs-, Fehler- oder Umleitungsdateien sind ausgeschlossen.

## Feste Vorbindungen

- Skriptpfad: `C:/Users/TV/Documents/MCM_FIELD_ORGANISM/workspace/tools/run_realpath_metadata_inventory.ps1`;
- Skriptbytes: `5085`;
- Skript-SHA-256: `8E7AAD2C3FF5E397FE54B81CC6EF1F72CCA82BDF36DD834E6C50D2B232EAF13B`;
- Host: `C:\Windows\System32\WindowsPowerShell\v1.0\powershell.exe`;
- Argumentstring: `-NoLogo -NoProfile -NonInteractive -File C:\Users\TV\Documents\MCM_FIELD_ORGANISM\workspace\tools\run_realpath_metadata_inventory.ps1 -PolicyProbe`;
- Aufruf-ID: SHA-256 ueber die UTF-8-Bytes der ordinalen Verkettung `Host + U+0000 + Argumentstring`;
- Aufruf-ID-SHA-256: `59E703561A02D51F3A23E74D7BC2FB88C2936CD3E529D32EC3D1964F8164658A`;
- finales Ausgabeziel: `C:/Users/TV/Documents/MCM_FIELD_ORGANISM/workspace/reports/213ZZ_g1_realpath_inventory.json`;
- Stagingziel: `C:/Users/TV/Documents/MCM_FIELD_ORGANISM/workspace/reports/.213ZZ_g1_realpath_inventory.json.staging`.

Der konkrete Wert wurde rein statisch ohne Prozessstart berechnet. Eine Folgeabnahme muss ihn unabhaengig reproduzieren.

## Vorgesehener Beobachtungsablauf

1. Skriptpfad, Bytegroesse und SHA-256 statisch vergleichen.
2. Final- und Stagingziel auf Nichtvorhandensein pruefen.
3. Bei jeder Abweichung vor Prozessstart genau ein Abbruchprotokoll ausgeben.
4. Bei bestandenen Vorbedingungen genau einen gebundenen Hostprozess starten.
5. `StandardOutput.BaseStream` und `StandardError.BaseStream` unmittelbar und parallel jeweils vollstaendig in einen eigenen `MemoryStream` kopieren, um Stream-Deadlocks und Textdekodierungsverlust zu vermeiden.
6. Auf beide Kopieroperationen und das Prozessende warten.
7. Rohbytes beider Puffer ohne Normalisierung, Trimmen, Zeilenumbruchaenderung oder Textrekodierung auslesen.
8. Exitcode und Nachzustand beider Ausgabeziele bestimmen.
9. Genau ein Beobachtungsobjekt auf Standardausgabe des Beobachters schreiben.
10. Keine lokale Protokolldatei, kein Retry, kein Alternativhost und kein weiterer Diagnoseprozess.

## Vollstaendiges In-Memory-Protokoll

Das eine ausgegebene JSON-Objekt muss mindestens genau diese Felder enthalten:

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

Feste Protokollwerte:

- `schema_version`: `g1-policy-probe-observation-v2`;
- `contract_id`: `213ZZL`;
- `process_start_attempts`: hoechstens `1`;
- `processes_started`: `0` oder `1`;
- `retry_count`: immer `0`;
- `observer_artifacts_written`: immer `0`;
- `stdout_base64` und `stderr_base64`: Base64 der jeweiligen unveraenderten Rohbytes, bei leerem Strom die leere Zeichenfolge;
- `stdout_sha256` und `stderr_sha256`: SHA-256 der jeweiligen Rohbytes, einschliesslich des definierten SHA-256-Werts des leeren Bytearrays;
- `failure_reasons`: geordnete Liste rein technischer Vertragsabweichungen, ohne Ursacheninterpretation.

Die Bytezahl muss jeweils der Laenge des aus Base64 rueckgewonnenen Bytearrays entsprechen. Dessen SHA-256 muss jeweils dem gebundenen Stromhash entsprechen. Dadurch bleiben auch nichtleere Fehlerstroeme vollstaendig nachpruefbar, ohne eine lokale Datei zu erzeugen.

## Erfolgskriterien

`contract_pass=true` ist nur zulaessig, wenn alle Bedingungen gleichzeitig gelten:

- alle Vorbindungen stimmen;
- beide Ausgabeziele waren vor dem Start frei;
- genau ein Prozess wurde bei genau einem Startversuch gestartet;
- `retry_count=0`;
- Standardausgabe dekodiert unter der vom Prozess gemeldeten Ausgabekodierung zu genau der erwarteten JSON-Zeile plus genau einem Zeilenumbruch;
- Standardfehler hat `0` Rohbytes;
- Exitcode ist `0`;
- Final- und Stagingziel fehlen nach Prozessende;
- `observer_artifacts_written=0`;
- Base64-, Bytezahl- und SHA-256-Bindungen beider Stroeme sind intern konsistent.

Jede einzelne Abweichung setzt `contract_pass=false`. Ein fehlgeschlagener Vertrag darf keine zweite Ausfuehrung ausloesen.

## Abbruchregeln

Vor Prozessstart wird bei abweichender Skriptidentitaet oder belegtem Ausgabeziel kein Prozess gestartet. Nach einem Start werden auch bei leerer Ausgabe, nichtleerem Standardfehler, Exitcode ungleich `0`, Artefaktentstehung oder Protokollinkonsistenz nur die beobachteten Rohdaten ausgegeben. Es folgen weder Retry noch Ursachenanalyse, Alternativhost, Policy-Abfrage, Registry-Zugriff oder Produktionspfad.

## Messergebnisse und Gegenbaseline

- Skriptbytes statisch gemessen: `5085`;
- Skript-SHA-256 statisch gemessen: `8E7AAD2C3FF5E397FE54B81CC6EF1F72CCA82BDF36DD834E6C50D2B232EAF13B`;
- `213ZZK`-Bytes: `4852`;
- `213ZZK`-SHA-256: `BE9D9B6415E47973F57F416B873840D997B9B755A0A70EA9167A84DDC4CA59A7`;
- finales Ausgabeziel vorhanden: nein;
- Stagingziel vorhanden: nein;
- in diesem Vorschlag gestartete Prozesse: `0`;
- neue Probe-Aufrufe: `0`;
- Realpfadabfragen: `0`;
- erzeugte Beobachtungsartefakte: `0`.

Die Gegenbaseline ist der statische Nullzustand. Gegenueber `213ZZJ` korrigiert der Vorschlag ausschliesslich die unvollstaendige Ausgabe des Beobachters: Beide Rohstroeme muessen vollstaendig im einen Konsolenprotokoll enthalten sein.

## Grenzen und nicht gepruefte Annahmen

Der Vorschlag wurde nicht ausgefuehrt. Parallelitaet, Encoding-Metadaten, Streamabschluss, JSON-Ausgabe und Hashkonsistenz wurden nicht praktisch beobachtet. Die konkrete Ursache von `213ZZJ` bleibt offen. Der Vertrag erlaubt keine Ursachenbehauptung und keine Aussage ueber G1 oder MCM.

## Konkrete Schlussfolgerung

Der korrigierte statische Beobachtungsvertrag beseitigt konzeptionell die in `213ZZJ` entstandene Belegluecke, indem er Standardausgabe und Standardfehler verlustfrei als Rohbytes, Base64, Bytezahl und SHA-256 in einem In-Memory-Konsolenprotokoll bindet. Ein-Prozess-, Kein-Retry-, Null-Artefakt- und fail-closed-Regel bleiben erhalten. Keine Zielabweichung ist erkennbar.

## Naechster begrenzter Schritt

Als naechstes ist ausschliesslich die unabhaengige statische Abnahme von `213ZZL` vorzunehmen. Zu pruefen sind Rohstromvollstaendigkeit, parallele In-Memory-Aufnahme, Protokollfelder, Base64-/Byte-/SHA-256-Konsistenz, Skript- und Aufrufbindung, freie Ausgabeziele, Ein-Prozess-, Kein-Retry-, Null-Artefakt- und Abbruchregeln. Jeder tatsaechliche Aufruf bleibt gesperrt.
