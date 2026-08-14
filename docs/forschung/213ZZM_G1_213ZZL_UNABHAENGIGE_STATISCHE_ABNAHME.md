# 213ZZM - Unabhaengige statische Abnahme von 213ZZL

## Einordnung

`213ZZM` ist kein Forschungslauf und erhaelt keine Laufnummer. Gegenstand ist ausschliesslich die unabhaengige statische Abnahme des Beobachtungsvertrags `213ZZL`. Es wurde kein Host, Skript oder Diagnoseprozess gestartet.

## Forschungsfrage und Auftrag

Sind Skript-, Host-, Argument- und Aufruf-ID-Bindung, 25 Protokollfelder, parallele Rohstromaufnahme, Base64-/Bytezahl-/SHA-256-Konsistenz sowie Ein-Prozess-, Kein-Retry-, Null-Artefakt- und Fail-closed-Regeln in `213ZZL` vollstaendig und aus dem vorgesehenen Protokoll reproduzierbar entscheidbar?

## Verwendete Quellen

- aktueller Uebergabe-Eingang;
- `docs/forschung/213ZZL_G1_POLICYPROBE_KORRIGIERTER_STATISCHER_BEOBACHTUNGSVERTRAG.md`;
- `docs/forschung/213ZZK_G1_213ZZJ_UNABHAENGIGE_STATISCHE_ABNAHME.md`;
- `tools/run_realpath_metadata_inventory.ps1`.

Keine externen Quellen wurden verwendet.

## Verwendete Dateien und Schnittstellen

Die Dateien wurden nur lesend geprueft. Verwendet wurden Dateibytes, `Get-FileHash`, ordinaler Stringvergleich, statische Reproduktion der Aufruf-ID mit SHA-256 ueber UTF-8-Bytes, `Test-Path` und `git diff --check`. Es wurde kein Prozess gestartet.

## Durchgefuehrte Schritte

1. Bytegroesse und SHA-256 von `213ZZL` und Skript bestimmt.
2. Host- und Argumentliteral ordinal geprueft.
3. Aufruf-ID unabhaengig aus `Host + U+0000 + Argumentstring` reproduziert.
4. Alle 25 vorgegebenen Protokollfelder nachgewiesen.
5. `BaseStream`-, `MemoryStream`- und Parallelitaetsvorgaben geprueft.
6. Base64-, Bytezahl- und SHA-256-Konsistenzregeln fuer beide Rohstroeme geprueft.
7. Prozess-, Retry-, Artefakt-, Ausgabeziel- und Fail-closed-Regeln geprueft.
8. Fuer jedes Erfolgskriterium geprueft, ob es aus den 25 Protokollfeldern reproduzierbar entscheidbar ist.
9. Final- und Stagingziel sowie `git diff --check` geprueft.

## Messergebnisse und Gegenbaselines

- `213ZZL`-Bytes: `7956`;
- `213ZZL`-SHA-256: `7318706D6EC5C1F5F3DBD47664F6530843042CA45871980E9721C55CF2A7777D`;
- Skriptbytes: `5085`;
- Skript-SHA-256: `8E7AAD2C3FF5E397FE54B81CC6EF1F72CCA82BDF36DD834E6C50D2B232EAF13B`;
- Protokollfelder vorhanden: `25/25`;
- reproduzierte Aufruf-ID: `59E703561A02D51F3A23E74D7BC2FB88C2936CD3E529D32EC3D1964F8164658A`;
- Aufruf-ID stimmt: ja;
- `BaseStream`-Bindungen: `2`;
- `MemoryStream`-Bindungen: `2`;
- parallele Aufnahme explizit gefordert: ja;
- Base64-/Bytezahl-/SHA-256-Regel fuer beide Stroeme: vorhanden;
- Ein-Prozess-, Kein-Retry-, Null-Artefakt- und Fail-closed-Regel: vorhanden;
- Erfolgskriterium mit „vom Prozess gemeldeter Ausgabekodierung“: vorhanden;
- Protokollfelder fuer Ausgabekodierung: `0`;
- definierter belastbarer Meldepfad der Prozesskodierung: `0`;
- finales Ausgabeziel vorhanden: nein;
- Stagingziel vorhanden: nein;
- in dieser Abnahme gestartete Prozesse: `0`;
- `git diff --check`: ohne Befund.

Die Gegenbaseline ist ein Vertrag, dessen `contract_pass` ausschliesslich aus dem vollstaendigen Beobachtungsobjekt unabhaengig reproduziert werden kann. Diese Baseline wird wegen der fehlenden Kodierungsbindung nicht vollstaendig erreicht.

## Beobachtetes Ergebnis

Alle geforderten Identitaets-, Rohstrom-, Prozess-, Retry-, Artefakt- und Ausgabezielbindungen sind statisch vorhanden. Ein einzelnes Erfolgskriterium ist jedoch unterbestimmt: Die Standardausgabe soll unter einer vom Prozess gemeldeten Ausgabekodierung dekodiert werden, waehrend das Protokoll keine Kodierung enthaelt und der Vertrag keine Quelle fuer eine solche Meldung festlegt.

## Technische Interpretation

Base64, Bytezahl und SHA-256 sichern die Rohbytes verlustfrei, bestimmen aber keine Textkodierung. Zwei unabhaengige Pruefer koennen deshalb aus demselben 25-Felder-Protokoll nicht zwingend dieselbe Textdekodierung und damit denselben Wert fuer `contract_pass` ableiten. Das ist ein statischer Vertragsfehler, keine Aussage ueber die Ursache von `213ZZJ`.

## Grenzen und nicht gepruefte Annahmen

Es wurde nicht geprueft, welche Kodierung ein spaeterer Host tatsaechlich verwendet. Es wird weder UTF-8 noch eine Execution-Policy-Ursache angenommen. `213ZZL` wurde nicht ausgefuehrt. Es liegt kein G1- oder MCM-Befund vor.

## Konkrete Schlussfolgerung

Die unabhaengige statische Abnahme von `213ZZL` ist nicht bestanden. Der Vertrag ist bis auf die Kodierungsentscheidung konsistent, aber `contract_pass` ist aus den definierten 25 Protokollfeldern nicht vollstaendig reproduzierbar. Der Befund erfordert eine enge statische Korrektur und erzeugt keine Ausfuehrungsfreigabe. Keine Zielabweichung ist erkennbar.

## Naechster begrenzter Schritt

Als naechstes ist ausschliesslich eine korrigierte statische Revision des Beobachtungsvertrags vorzuschlagen. Sie muss entweder eine belastbar erfasste Kodierung mit eindeutigem Erfassungsweg in das Protokoll aufnehmen oder die Erfolgskontrolle vollstaendig auf fest gebundene erwartete Rohbytes, Bytezahl und SHA-256 umstellen. Ein tatsaechlicher Aufruf bleibt gesperrt.
