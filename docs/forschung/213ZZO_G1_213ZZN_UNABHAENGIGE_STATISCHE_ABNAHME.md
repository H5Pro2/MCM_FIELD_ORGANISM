# 213ZZO - Unabhaengige statische Abnahme von 213ZZN

## Einordnung

`213ZZO` ist kein Forschungslauf und erhaelt keine Laufnummer. Gegenstand ist ausschliesslich die unabhaengige statische Abnahme des rohbytebasierten Beobachtungsvertrags `213ZZN`. Es wurde kein Host, Skript, Probe-, Diagnose- oder Produktionsprozess gestartet.

## Forschungsfrage und Auftrag

Sind die Rohbytekonstanten, 25 Protokollfelder, Aufruf-ID, Skript-, Host- und Argumentbindung, `BaseStream`-Erfassung sowie Ein-Prozess-, Kein-Retry-, Null-Artefakt-, freie-Ziele- und Fail-closed-Regeln in `213ZZN` statisch konsistent und ohne Textdekodierung reproduzierbar entscheidbar?

## Verwendete Quellen

- aktueller Uebergabe-Eingang;
- `docs/forschung/213ZZN_G1_POLICYPROBE_ROHBYTEBASIERTER_STATISCHER_BEOBACHTUNGSVERTRAG.md`;
- `docs/forschung/213ZZM_G1_213ZZL_UNABHAENGIGE_STATISCHE_ABNAHME.md`;
- `tools/run_realpath_metadata_inventory.ps1`.

Keine externen Quellen wurden verwendet.

## Verwendete Dateien und Schnittstellen

Die Dateien wurden ausschliesslich lesend und statisch geprueft. Verwendet wurden Dateibytes, SHA-256, UTF-8 ohne BOM fuer die statische Sollwertberechnung, Base64, ordinaler Stringvergleich und `Test-Path`. Die vorgesehenen Schnittstellen `StandardOutput.BaseStream`, `StandardError.BaseStream` und zwei getrennte `MemoryStream`-Puffer wurden nur im Vertrag geprueft, nicht ausgefuehrt.

## Durchgefuehrte Schritte

1. Bytegroesse und SHA-256 von `213ZZN` und dem gebundenen Skript bestimmt.
2. Das unveraenderte ASCII-Ausgabeliteral im `-PolicyProbe`-Zweig statisch mit der Vertragsbindung verglichen.
3. UTF-8-ohne-BOM-Bytes des Literals mit exakt angehaengtem `0D 0A` unabhaengig gebildet.
4. Bytezahl, Base64 und SHA-256 der erwarteten Standardausgabe reproduziert.
5. Bytezahl, Base64 und SHA-256 des leeren Standardfehlers reproduziert.
6. Aufruf-ID aus `Host + U+0000 + Argumentstring` unabhaengig reproduziert.
7. Anzahl und Eindeutigkeit der 25 Protokollfelder geprueft.
8. Beide `BaseStream`-Bindungen, getrennte Speicherpuffer und parallele Vollstaendigkeitsanforderung geprueft.
9. Erfolgs-, Vorabbruch- und Nachabbruchregeln auf Ein-Prozess, Kein-Retry, Null-Artefakt und fail-closed geprueft.
10. Final- und Stagingziel auf Nichtvorhandensein geprueft.

## Messergebnisse und Gegenbaselines

- `213ZZN`-Bytes: `9957`;
- `213ZZN`-SHA-256: `8B472C8231996383682E03586A99CB73FDB2D22C3E2082570458D5A3B57F2671`;
- Skriptbytes: `5085`;
- Skript-SHA-256: `8E7AAD2C3FF5E397FE54B81CC6EF1F72CCA82BDF36DD834E6C50D2B232EAF13B`;
- Protokollfelder vorhanden: `25/25`;
- eindeutige Protokollfelder: `25/25`;
- reproduzierte Standardausgabebytes: `123`;
- reproduziertes Standardausgabe-Base64: `eyJzY2hlbWFfdmVyc2lvbiI6ImcxLXJlYWxwYXRoLWludmVudG9yeS1wb2xpY3ktcHJvYmUtdjEiLCJwb2xpY3lfcHJvYmUiOnRydWUsInJlYWxwYXRoX3F1ZXJpZXMiOjAsImFydGlmYWN0c193cml0dGVuIjowfQ0K`;
- reproduzierter Standardausgabe-SHA-256: `8FB301FE4D2E5D5208CC0DA2682FF5E49661155BB58CC9E1DF158727F4C7E877`;
- reproduzierte Standardfehlerbytes: `0`;
- reproduziertes Standardfehler-Base64: leere Zeichenfolge;
- reproduzierter Standardfehler-SHA-256: `E3B0C44298FC1C149AFBF4C8996FB92427AE41E4649B934CA495991B7852B855`;
- reproduzierte Aufruf-ID: `59E703561A02D51F3A23E74D7BC2FB88C2936CD3E529D32EC3D1964F8164658A`;
- `StandardOutput.BaseStream` gebunden: ja;
- `StandardError.BaseStream` gebunden: ja;
- zwei getrennte `MemoryStream`-Puffer gebunden: ja;
- textdekodierungsabhaengige Erfolgskriterien: `0`;
- finales Ausgabeziel vorhanden: nein;
- Stagingziel vorhanden: nein;
- gestartete gebundene Prozesse: `0`;
- Realpfadabfragen: `0`;
- erzeugte Laufartefakte: `0`.

Die Gegenbaseline ist `213ZZL`, dessen `contract_pass` wegen einer nicht gebundenen Textdekodierung nicht vollstaendig reproduzierbar war. Diese Unterbestimmung liegt in `213ZZN` nicht mehr vor: Alle Stromkriterien werden anhand unveraenderter Rohbytes entschieden.

## Beobachtetes Ergebnis

Alle freigegebenen statischen Pruefpunkte stimmen. Die erwartete Standardausgabe reproduziert sich als exakt 123 Bytes mit den gebundenen Base64- und SHA-256-Werten. Der leere Standardfehler und die Aufruf-ID reproduzieren sich ebenfalls exakt. Die 25 Protokollfelder sind vollstaendig und eindeutig. Prozess-, Retry-, Artefakt-, Zielpfad- und Abbruchregeln sind statisch vorhanden und widerspruchsfrei.

## Technische Interpretation

`contract_pass` ist aus dem feststehenden Vertrag und einem spaeteren vollstaendigen 25-Felder-Protokoll ohne Textdekodierung unabhaengig reproduzierbar. Eine abweichende Plattformausgabe, ein anderer Zeilenabschluss oder irgendeine weitere Byteabweichung kann nicht unbemerkt als Erfolg gelten, sondern fuehrt fail-closed zu `contract_pass=false`.

## Grenzen und nicht gepruefte Annahmen

Die Abnahme ist rein statisch. Nicht praktisch geprueft wurden Prozessstart, parallele Rohstromaufnahme, tatsaechliche Ausgabe, Exitcode oder Nachzustand. Die Abnahme behauptet nicht, dass ein spaeterer Prozess die Sollbytes erzeugt. Die Ursache des frueheren technischen Abbruchs bleibt offen. Es liegt weder ein G1- noch ein MCM-Befund vor.

## Konkrete Schlussfolgerung

`213ZZN` besteht die unabhaengige statische Abnahme. Rohbytekonstanten, Protokollstruktur, Aufruf- und Skriptbindung sowie alle geforderten Sicherheitsregeln sind statisch konsistent. Die Kodierungsunterbestimmung aus `213ZZM` ist im Vertrag behoben. Diese Abnahme erzeugt keine Ausfuehrungsfreigabe. Keine Zielabweichung ist erkennbar.

## Naechster begrenzter Forschungsschritt

Als naechstes sollte ausschliesslich ein statischer Ausfuehrungsvertrag fuer genau einen eventuell spaeter separat freizugebenden `-PolicyProbe`-Einzelaufruf auf Basis von `213ZZN` formuliert werden. Er muss die hier abgenommenen Identitaeten, Rohbyte-Sollwerte, 25 Protokollfelder, Vor- und Nachpruefungen sowie Ein-Prozess-, Kein-Retry-, Null-Artefakt- und Fail-closed-Regeln unveraendert uebernehmen. Ein tatsaechlicher Aufruf bleibt bis zu einer ausdruecklichen Folgefreigabe gesperrt.
