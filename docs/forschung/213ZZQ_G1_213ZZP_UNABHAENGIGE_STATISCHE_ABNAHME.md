# 213ZZQ - Unabhaengige statische Abnahme von 213ZZP

## Einordnung

`213ZZQ` ist kein Forschungslauf und erhaelt keine Laufnummer. Gegenstand ist ausschliesslich die unabhaengige statische Abnahme des Policy-Probe-Ausfuehrungsvertrags `213ZZP`. Es wurde kein Host, Skript, Probe-, Diagnose-, Produktions- oder Inventurprozess gestartet.

## Forschungsfrage und Auftrag

Sind in `213ZZP` die abgenommenen Identitaeten und Rohbytewerte, die absolute Aufrufstruktur, Vor- und Nachpruefungen, 25 Protokollfelder, Nullbehandlung, parallele `BaseStream`-Erfassung sowie Ein-Prozess-, Kein-Retry-, Null-Artefakt- und Fail-closed-Regeln vollstaendig und widerspruchsfrei gebunden?

## Verwendete Quellen

- aktueller Uebergabe-Eingang;
- `docs/forschung/213ZZP_G1_POLICYPROBE_ROHBYTEBASIERTER_STATISCHER_AUSFUEHRUNGSVERTRAG.md`;
- `docs/forschung/213ZZN_G1_POLICYPROBE_ROHBYTEBASIERTER_STATISCHER_BEOBACHTUNGSVERTRAG.md`;
- `docs/forschung/213ZZO_G1_213ZZN_UNABHAENGIGE_STATISCHE_ABNAHME.md`;
- `tools/run_realpath_metadata_inventory.ps1`.

Keine externen Quellen wurden verwendet.

## Verwendete Dateien und Schnittstellen

Die Dateien wurden ausschliesslich statisch und lesend geprueft. Verwendet wurden Dateibytes, SHA-256, UTF-8 ohne BOM, Base64, ordinaler Vergleich und `Test-Path`. Die vorgesehenen Schnittstellen `System.Diagnostics.Process.Start()`, `StandardOutput.BaseStream`, `StandardError.BaseStream` und zwei getrennte `MemoryStream`-Puffer wurden nur auf ihre Vertragsbindung geprueft und nicht ausgefuehrt.

## Durchgefuehrte Schritte

1. Bytegroesse und SHA-256 von `213ZZP` sowie dem gebundenen Skript bestimmt.
2. Skriptpfad, Hostpfad und Argumentstring ordinal gegen `213ZZN` und `213ZZO` verglichen.
3. Aufruf-ID unabhaengig aus `Host + U+0000 + Argumentstring` reproduziert.
4. Erwartetes Skriptliteral als UTF-8 ohne BOM mit exakt `0D 0A` gebildet.
5. Bytezahl, Base64 und SHA-256 der erwarteten Standardausgabe unabhaengig reproduziert.
6. Bytezahl, Base64 und SHA-256 des leeren Standardfehlers unabhaengig reproduziert.
7. Anzahl und Eindeutigkeit der 25 Protokollfelder geprueft.
8. Acht Vorpruefungen und sieben Nachpruefungen nachgewiesen.
9. Nullbehandlung bei nicht beobachtbaren Werten und technische `failure_reasons` geprueft.
10. Direkten Einzelstart, parallele getrennte Rohstromaufnahme, Prozessgrenzen und Retry-Verbot geprueft.
11. Null-Artefakt-, freie-Ziele-, Ausschluss- und Fail-closed-Regeln geprueft.
12. Final- und Stagingziel auf Nichtvorhandensein geprueft.

## Messergebnisse und Gegenbaselines

- `213ZZP`-Bytes: `11057`;
- `213ZZP`-SHA-256: `759B7205BD8DFF40B080A4761851AF74B4BC681EB4957971455B19396FE3E3EC`;
- Skriptbytes: `5085`;
- Skript-SHA-256: `8E7AAD2C3FF5E397FE54B81CC6EF1F72CCA82BDF36DD834E6C50D2B232EAF13B`;
- Protokollfelder vorhanden: `25/25`;
- eindeutige Protokollfelder: `25/25`;
- Vorpruefungen: `8`;
- Nachpruefungen: `7`;
- reproduzierte Standardausgabebytes: `123`;
- reproduziertes Standardausgabe-Base64: `eyJzY2hlbWFfdmVyc2lvbiI6ImcxLXJlYWxwYXRoLWludmVudG9yeS1wb2xpY3ktcHJvYmUtdjEiLCJwb2xpY3lfcHJvYmUiOnRydWUsInJlYWxwYXRoX3F1ZXJpZXMiOjAsImFydGlmYWN0c193cml0dGVuIjowfQ0K`;
- reproduzierter Standardausgabe-SHA-256: `8FB301FE4D2E5D5208CC0DA2682FF5E49661155BB58CC9E1DF158727F4C7E877`;
- reproduzierte Standardfehlerbytes: `0`;
- reproduziertes Standardfehler-Base64: leere Zeichenfolge;
- reproduzierter Standardfehler-SHA-256: `E3B0C44298FC1C149AFBF4C8996FB92427AE41E4649B934CA495991B7852B855`;
- reproduzierte Aufruf-ID: `59E703561A02D51F3A23E74D7BC2FB88C2936CD3E529D32EC3D1964F8164658A`;
- absolut gebundener Host und absolut gebundener `-File`-Pfad: vorhanden;
- direkte `System.Diagnostics.Process.Start()`-Bindung: vorhanden;
- `BaseStream`-Bindungen: `2`;
- getrennte `MemoryStream`-Puffer: `2`;
- JSON-`null`-Regel bei nicht beobachtbaren Werten: vorhanden;
- maximaler Startversuch: `1`;
- Retry-Zahl: immer `0`;
- finales Ausgabeziel vorhanden: nein;
- Stagingziel vorhanden: nein;
- gestartete gebundene Prozesse: `0`;
- Realpfadabfragen: `0`;
- erzeugte Laufartefakte: `0`.

Die Gegenbaseline ist ein Vertrag, der relative oder veraenderbare Aufrufe, Textdekodierung, fehlende Rohstroeme, Wiederholungsaufrufe oder lokale Beobachtungsartefakte zulaesst. `213ZZP` schliesst diese Alternativen explizit aus.

## Beobachtetes Ergebnis

Alle freigegebenen statischen Pruefpunkte stimmen. Identitaeten, Aufruf-ID und Rohbyte-Sollwerte wurden unveraendert aus den abgenommenen Vorstufen uebernommen und unabhaengig reproduziert. Die Vor-, Start-, Strom-, Nach- und Abbruchbedingungen ergeben eine geschlossene fail-closed Entscheidung mit genau einem maximalen Startversuch und ohne Retry.

## Technische Interpretation

Ein spaeteres 25-Felder-Protokoll waere anhand von `213ZZP` auch bei Vorabbruch oder Startfehler auswertbar: Nicht beobachtbare Werte werden als JSON `null` kenntlich gemacht, waehrend Prozesszaehler und technische Fehlergruende den Abbruch belegen. Nur der vollstaendig bestandene Einzelaufruf kann `contract_pass=true` ergeben.

## Grenzen und nicht gepruefte Annahmen

Die Abnahme ist rein statisch. Nicht praktisch geprueft wurden Prozessstart, Streamparallelitaet, Rohbytes, Exitcode, JSON-Ausgabe oder Nachzustand. Die Beschreibung eines Beobachters ist kein ausgefuehrtes Beobachterprogramm. Es wird weder ein spaeterer Erfolg noch eine Ursache fuer einen frueheren technischen Abbruch angenommen. Es liegt kein G1- oder MCM-Befund vor.

## Konkrete Schlussfolgerung

`213ZZP` besteht die unabhaengige statische Abnahme. Absolute Aufrufstruktur, Identitaeten, Rohbytewerte, 25-Felder-Protokoll, Nullbehandlung und alle geforderten Sicherheitsregeln sind statisch konsistent. Diese Abnahme erzeugt keine Ausfuehrungsfreigabe. Keine Zielabweichung ist erkennbar.

## Naechster begrenzter Schritt

Als naechstes kann ausschliesslich die separate Entscheidung geprueft werden, ob genau ein `-PolicyProbe`-Einzelaufruf gemaess `213ZZP` freigegeben werden darf. Ohne eine solche ausdrueckliche Folgefreigabe bleibt jeder Aufruf gesperrt. Produktionsinventur, Diagnose, Alternativhost, Retry, Realpfadzugriff sowie G1- und MCM-Befundarbeit bleiben ausgeschlossen.
