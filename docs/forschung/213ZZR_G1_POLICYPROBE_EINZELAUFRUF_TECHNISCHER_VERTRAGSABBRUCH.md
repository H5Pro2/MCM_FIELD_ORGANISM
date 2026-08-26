# 213ZZR - Policy-Probe-Einzelaufruf: technischer Vertragsabbruch

## Einordnung

`213ZZR` dokumentiert den genau einmal freigegebenen `-PolicyProbe`-Einzelaufruf nach `213ZZP`. Der Aufruf ist ein technischer Vertragspruefschritt und kein Forschungslauf; er erhaelt keine Laufnummer. Es gab keinen Retry, keinen Alternativhost, keinen Diagnoseaufruf, keine Produktionsinventur und keine Realpfadabfrage.

## Forschungsfrage und Auftrag

Erfuellt der einmalige, absolut gebundene `-PolicyProbe`-Aufruf alle Vor-, Rohstrom-, Exitcode-, Nach- und Null-Artefakt-Bedingungen von `213ZZP`, sodass `contract_pass=true` zulaessig waere?

## Verwendete Quellen

- aktueller Uebergabe-Eingang;
- `docs/forschung/213ZZP_G1_POLICYPROBE_ROHBYTEBASIERTER_STATISCHER_AUSFUEHRUNGSVERTRAG.md`;
- `docs/forschung/213ZZQ_G1_213ZZP_UNABHAENGIGE_STATISCHE_ABNAHME.md`;
- `tools/run_realpath_metadata_inventory.ps1`;
- das einmalig ausgegebene 25-Felder-Konsolenprotokoll des Beobachters.

Keine externen Quellen wurden verwendet.

## Verwendete Dateien und Schnittstellen

Der Beobachter verwendete `System.Diagnostics.Process` mit `UseShellExecute=false` und genau dem in `213ZZP` gebundenen Host und Argumentstring. `StandardOutput.BaseStream` und `StandardError.BaseStream` wurden parallel und vollstaendig in getrennte `MemoryStream`-Puffer kopiert. Der Beobachter erzeugte keine Datei.

## Durchgefuehrte Schritte

1. Skriptpfad, regulaere Datei, Bytegroesse und SHA-256 vor dem Start geprueft.
2. Host, Argumentstring und Aufruf-ID gegen `213ZZP` geprueft.
3. Final- und Stagingziel vor dem Start auf Nichtvorhandensein geprueft.
4. Genau einen Startversuch fuer den gebundenen Hostprozess ausgefuehrt.
5. Beide Rohstroeme parallel und unveraendert in getrennten In-Memory-Puffern aufgenommen.
6. Bytezahl, Base64 und SHA-256 beider Stroeme bestimmt.
7. Exitcode und beide Ausgabeziele nach Prozessende geprueft.
8. `contract_pass` fail-closed gegen alle Sollwerte entschieden.
9. Das Ergebnis ohne Retry als genau ein 25-Felder-JSON ausgegeben.
10. Standardfehler-Base64 danach statisch zur unabhaengigen Bytezahl- und Hashkontrolle rekonstruiert.

## Vollstaendiges Beobachtungsprotokoll

```json
{"schema_version":"g1-policy-probe-observation-v3","contract_id":"213ZZP","script_path":"C:/Users/TV/Documents/MCM_FIELD_ORGANISM/workspace/tools/run_realpath_metadata_inventory.ps1","script_bytes_before":5085,"script_sha256_before":"8E7AAD2C3FF5E397FE54B81CC6EF1F72CCA82BDF36DD834E6C50D2B232EAF13B","host_path":"C:\\Windows\\System32\\WindowsPowerShell\\v1.0\\powershell.exe","argument_string":"-NoLogo -NoProfile -NonInteractive -File C:\\Users\\TV\\Documents\\MCM_FIELD_ORGANISM\\workspace\\tools\\run_realpath_metadata_inventory.ps1 -PolicyProbe","invocation_id_sha256":"59E703561A02D51F3A23E74D7BC2FB88C2936CD3E529D32EC3D1964F8164658A","pre_final_exists":false,"pre_staging_exists":false,"process_start_attempts":1,"processes_started":1,"retry_count":0,"stdout_bytes":0,"stdout_sha256":"E3B0C44298FC1C149AFBF4C8996FB92427AE41E4649B934CA495991B7852B855","stdout_base64":"","stderr_bytes":460,"stderr_sha256":"C9B3653E516FDE779A6983224B3847E42FDB8D3A7BEE3B4243EC5EA3C8BF4B85","stderr_base64":"RGllIERhdGVpICJDOlxVc2Vyc1xUVlxEb2N1bWVudHNcTUNNX0ZJRUxEX09SR0FOSVNNXHdvcmtzcGFjZVx0b29sc1xydW5fcmVhbHBhdGhfbWV0YWRhdGFfaW52ZW50b3J5LnBzMSIga2FubiBuaWNodCANCmdlbGFkZW4gd2VyZGVuLCBkYSBkaWUgQXVzZoFocnVuZyB2b24gU2tyaXB0cyBhdWYgZGllc2VtIFN5c3RlbSBkZWFrdGl2aWVydCBpc3QuIFdlaXRlcmUgSW5mb3JtYXRpb25lbiBmaW5kZW4gU2llIA0KdW50ZXIgImFib3V0X0V4ZWN1dGlvbl9Qb2xpY2llcyIgKGh0dHBzOi9nby5taWNyb3NvZnQuY29tL2Z3bGluay8/TGlua0lEPTEzNTE3MCkuDQogICAgKyBDYXRlZ29yeUluZm8gICAgICAgICAgOiBTaWNoZXJoZWl0c2ZlaGxlcjogKDopIFtdLCBQYXJlbnRDb250YWluc0Vycm9yUmVjb3JkRXhjZXB0aW9uDQogICAgKyBGdWxseVF1YWxpZmllZEVycm9ySWQgOiBVbmF1dGhvcml6ZWRBY2Nlc3MNCg==","exit_code":1,"post_final_exists":false,"post_staging_exists":false,"observer_artifacts_written":0,"contract_pass":false,"failure_reasons":["stdout_bytes_mismatch","stdout_base64_mismatch","stdout_sha256_mismatch","stderr_not_empty","stderr_base64_mismatch","stderr_sha256_mismatch","exit_code_mismatch"]}
```

## Messergebnisse und Gegenbaselines

- Skriptbytes vor Start: `5085`;
- Skript-SHA-256 vor Start: `8E7AAD2C3FF5E397FE54B81CC6EF1F72CCA82BDF36DD834E6C50D2B232EAF13B`;
- Aufruf-ID: `59E703561A02D51F3A23E74D7BC2FB88C2936CD3E529D32EC3D1964F8164658A`;
- Startversuche: `1`;
- gestartete Probe-Prozesse: `1`;
- Retry: `0`;
- beobachtete Standardausgabe: `0` Bytes;
- erwartete Standardausgabe: `123` Bytes;
- beobachteter Standardausgabe-SHA-256: SHA-256 des leeren Bytearrays;
- beobachteter Standardfehler: `460` Bytes;
- erwarteter Standardfehler: `0` Bytes;
- beobachteter Standardfehler-SHA-256: `C9B3653E516FDE779A6983224B3847E42FDB8D3A7BEE3B4243EC5EA3C8BF4B85`;
- statisch aus Base64 rekonstruierte Standardfehlerbytes: `460`;
- statisch reproduzierter Standardfehler-SHA-256: `C9B3653E516FDE779A6983224B3847E42FDB8D3A7BEE3B4243EC5EA3C8BF4B85`;
- Exitcode beobachtet: `1`;
- Exitcode erwartet: `0`;
- Finalziel vor/nach Aufruf vorhanden: nein/nein;
- Stagingziel vor/nach Aufruf vorhanden: nein/nein;
- Beobachterartefakte: `0`;
- `contract_pass`: `false`.

Die Erfolgsbaseline aus `213ZZP` verlangt 123 exakt gebundene Standardausgabebytes, leeren Standardfehler und Exitcode `0`. Alle drei Bedingungen wurden verfehlt. Die Sicherheitsbaseline wurde eingehalten: genau ein Prozess, kein Retry, keine Artefakte und freie Ziele.

## Beobachtetes Ergebnis

Der gebundene Prozess wurde genau einmal gestartet, gab keine Standardausgabebytes aus, lieferte 460 Standardfehlerbytes und endete mit Exitcode `1`. Der gebundene Fehlerstrom enthaelt die unveraenderten ASCII-Bytefolgen `about_Execution_Policies` und `UnauthorizedAccess`. Final- und Stagingziel blieben frei.

## Technische Interpretation

Der Lauf ist ein technischer Vertragsabbruch. Die gebundenen ASCII-Marker klassifizieren die unmittelbare Ablehnung als mit PowerShell-Ausfuehrungsrichtlinien verknuepften unautorisierten Skriptstart. Nicht bestimmt sind Quelle, Geltungsbereich oder konkrete Konfiguration der Richtlinie. Es wird keine weitergehende Systemursache behauptet.

## Grenzen und nicht gepruefte Annahmen

Der Aufruf pruefte nur den gebundenen Host- und Argumentpfad. Es gab keine Policy-Abfrage, keinen Registry-Zugriff, keinen Alternativhost und keinen Diagnoseprozess. Die nicht-ASCII-Textdekodierung des Fehlerstroms ist nicht Bestandteil der Klassifikation; verwendet wurden die roh gebundenen ASCII-Marker. Der Skriptzweig selbst erzeugte wegen der vorgelagerten Ablehnung keinen beobachtbaren Policy-Probe-Ausgabesatz. Es liegt kein G1- oder MCM-Befund vor.

## Konkrete Schlussfolgerung

Der einmalig freigegebene `-PolicyProbe`-Aufruf hat `213ZZP` fail-closed nicht bestanden. Der Vertrag wurde sicher eingehalten, aber sein Erfolgskriterium wurde wegen leerer Standardausgabe, nichtleerem Standardfehler und Exitcode `1` verfehlt. Der Einzelaufruf ist verbraucht und darf nicht wiederholt werden. Keine Zielabweichung ist erkennbar.

## Naechster begrenzter Schritt

Als naechstes ist ausschliesslich die unabhaengige statische Abnahme und Klassifikation von `213ZZR` zulaessig. Dabei sind das 25-Felder-Protokoll, Rohstrom-Base64, Bytezahlen, Hashwerte, Exitcode, Prozess-/Retry-Zahlen, freie Ziele und die enge Klassifikation anhand der ASCII-Marker zu pruefen. Jeder weitere Aufruf bleibt gesperrt.
