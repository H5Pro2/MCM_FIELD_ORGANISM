# 213ZZJ - Policy-Probe-Einmallauf mit technischem Abbruch

## Einordnung

`213ZZJ` ist kein Forschungslauf und erhaelt keine Laufnummer. Ausgefuehrt wurde ausschliesslich der in `213ZZH` gebundene und nach `213ZZI` einmalig freigegebene `-PolicyProbe`-Aufruf. Es gab keinen Retry und keinen Produktionsaufruf.

## Forschungsfrage und Auftrag

Erzeugt genau ein gebundener `-PolicyProbe`-Aufruf die erwartete einzelne JSON-Zeile mit Exitcode `0`, leerem Standardfehler, ohne Inventurartefakte und ohne Wiederholung?

## Verwendete Quellen

- aktueller Uebergabe-Eingang;
- `docs/forschung/213ZZH_G1_POLICYPROBE_STATISCHER_AUSFUEHRUNGSVERTRAG.md`;
- `docs/forschung/213ZZI_G1_213ZZH_UNABHAENGIGE_STATISCHE_ABNAHME.md`;
- `tools/run_realpath_metadata_inventory.ps1`.

Keine externen Quellen wurden verwendet.

## Verwendete Dateien und Schnittstellen

Vor dem Start wurden Skriptbytes, SHA-256 sowie Final- und Stagingziel geprueft. Der gebundene Host `C:\Windows\System32\WindowsPowerShell\v1.0\powershell.exe` wurde ueber `System.Diagnostics.Process` genau einmal mit getrennt im Speicher erfasster Standardausgabe und Standardfehler gestartet. Danach wurden ausschliesslich die beiden gebundenen Ausgabeziele und die Skriptidentitaet erneut statisch geprueft.

## Durchgefuehrte Schritte

1. Skriptpfad, Bytegroesse und SHA-256 erfolgreich gegen `213ZZH` geprueft.
2. Nichtvorhandensein von Final- und Stagingziel erfolgreich geprueft.
3. Genau einen Prozess mit den Argumenten `-NoLogo -NoProfile -NonInteractive -File <absoluter Skriptpfad> -PolicyProbe` gestartet.
4. Standardausgabe, Standardfehler und Exitcode getrennt im Speicher erfasst.
5. Ergebnis gegen die Vertragswerte verglichen.
6. Final- und Stagingziel nach Prozessende erneut geprueft.
7. Keinen Retry, Alternativhost oder Diagnoseaufruf gestartet.
8. Skriptbytes und SHA-256 nach dem Abbruch erneut geprueft.

## Beobachtete Messergebnisse und Gegenbaseline

- Vorbedingung Skriptbytes: `5085`, bestanden;
- Vorbedingung Skript-SHA-256: `8E7AAD2C3FF5E397FE54B81CC6EF1F72CCA82BDF36DD834E6C50D2B232EAF13B`, bestanden;
- gestartete Probe-Prozesse: `1`;
- Standardausgabezeilen: `0`;
- erwartete JSON-Zeile exakt erhalten: nein;
- Standardfehler leer: nein;
- Standardfehlerlaenge nach Dekodierung und UTF-8-Neukodierung: `462` Bytes;
- Exitcode: `1` statt erwartet `0`;
- finales Ausgabeziel nach Prozessende vorhanden: nein;
- Stagingziel nach Prozessende vorhanden: nein;
- Retry: `0`;
- Produktionsaufrufe: `0`;
- Skriptbytes nach Prozessende: `5085`;
- Skript-SHA-256 nach Prozessende: unveraendert;
- erzeugte Inventurartefakte: `0`.

Die Gegenbaseline aus `213ZZH` war eine JSON-Ausgabezeile, leerer Standardfehler und Exitcode `0`. Diese Baseline wurde bei Ausgabe und Exitcode nicht erreicht. Null-Artefakt- und Kein-Retry-Regel wurden eingehalten.

## Technische Interpretation

Der Probe-Vertrag ist fail-closed fehlgeschlagen. Der Prozess wurde gestartet, lieferte jedoch keine Standardausgabe, nichtleeren Standardfehler und Exitcode `1`. Daher ist keine Policy-Akzeptanz nachgewiesen und es entsteht keine Freigabe fuer Produktion oder Inventur.

## Offene Frage

Die konkrete Fehlerursache ist aus der persistierten Beobachtung nicht bestimmbar, weil der Standardfehlerinhalt nach dem abgeschlossenen Prozess nicht in das ausgegebene Beobachtungsprotokoll aufgenommen wurde; erhalten blieb nur seine Nichtleere und Laengenmessung. Eine Execution-Policy-Ursache waere eine Hypothese, kein beobachteter Befund.

## Grenzen und nicht gepruefte Annahmen

Es wurde keine unabhaengige Systemaufruf-Instrumentierung fuer Realpfadzugriffe eingesetzt. Da keine JSON-Zeile vorliegt, existiert auch kein Laufzeit-Selbstbericht `realpath_queries:0`; ein tatsaechlicher Wert darf deshalb nicht behauptet werden. Es wurden keine der 54 gebundenen Inventurpfade absichtlich abgefragt und keine Artefakte erzeugt. Der Standardfehlerinhalt wird nicht rekonstruiert oder geraten. Es liegt kein G1- oder MCM-Befund vor.

## Konkrete Schlussfolgerung

Der genau einmal freigegebene `-PolicyProbe`-Aufruf endete als technischer Vertragsabbruch. Ein-Prozess-, Kein-Retry- und Null-Artefakt-Regel wurden eingehalten; Ausgabe- und Exitcodevertrag wurden nicht erfuellt. Das Skript blieb unveraendert. Keine Zielabweichung ist erkennbar.

## Naechster begrenzter Schritt

Als naechstes ist ausschliesslich die unabhaengige statische Abnahme von `213ZZJ` und die Klassifikation des dokumentierten technischen Abbruchs vorzunehmen. Ein weiterer `-PolicyProbe`-Aufruf, Diagnoseprozess, Produktionsaufruf, Inventur oder Realpfadzugriff bleibt gesperrt. Erst eine neue statische Ursachenpruefung und ein neuer, unabhaengig abgenommener Vertrag koennten einen spaeteren Folgeaufruf begruenden.
