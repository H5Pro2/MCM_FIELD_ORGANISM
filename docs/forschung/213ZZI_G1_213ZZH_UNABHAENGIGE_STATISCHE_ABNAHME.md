# 213ZZI - Unabhaengige statische Abnahme von 213ZZH

## Einordnung

`213ZZI` ist kein Forschungslauf und erhaelt keine Laufnummer. Geprueft wurde ausschliesslich der statische Ausfuehrungsvertrag `213ZZH`. Weder der dort genannte PowerShell-Host noch das Inventurskript wurden gestartet.

## Forschungsfrage und Auftrag

Bindet `213ZZH` genau einen spaeteren `-PolicyProbe`-Aufruf konsistent an Skriptidentitaet, absolute Aufrufstruktur, Vor- und Nachpruefungen, Abbruchregeln, einzelne JSON-Ausgabe, Exitcode `0`, leeren Standardfehler sowie Null-Artefakt-, Null-Realpfad-, Ein-Prozess- und Kein-Retry-Regel?

## Verwendete Quellen

- aktueller Uebergabe-Eingang;
- `docs/forschung/213ZZH_G1_POLICYPROBE_STATISCHER_AUSFUEHRUNGSVERTRAG.md`;
- `docs/forschung/213ZZG_G1_213ZZF_UNABHAENGIGE_STATISCHE_ABNAHME.md`;
- `tools/run_realpath_metadata_inventory.ps1`.

Keine externen Quellen wurden verwendet.

## Verwendete Dateien und Schnittstellen

Die genannten Dateien wurden nur lesend ausgewertet. Verwendet wurden Dateibytes, `Get-FileHash`, `Test-Path`, regulaere Ausdruecke zur isolierten Auswertung der Markdown-Codebloecke, `System.Management.Automation.Language.Parser`, PowerShell-AST-Knotentypen und `git diff --check`.

## Durchgefuehrte Schritte

1. Bytegroesse und SHA-256 von Vertrag und Skript erneut bestimmt.
2. Den einzigen `text`-Aufrufblock isoliert und Host, absolute Pfade und Argumente geprueft.
3. Anzahl von Aufrufblock und `-PolicyProbe`-Argument bestimmt und `-ExecutionPolicy` im Aufruf ausgeschlossen.
4. Den JSON-Codeblock isoliert und ordinal mit dem AST-Stringliteral des Probe-Zweigs verglichen.
5. Parserfehler, Befehle und Exit-Anweisung im Probe-Zweig geprueft.
6. Alle gebundenen Erwartungen, Vor-/Nachpruefungen und Fail-closed-Abbruchregeln literal nachgewiesen.
7. Final- und Stagingziel auf Nichtvorhandensein geprueft.
8. `git diff --check` ausgefuehrt.

## Messergebnisse und Gegenbaselines

- `213ZZH`-Bytes: `5757`;
- `213ZZH`-SHA-256: `8ACE2CA3E36FCF6CD241B60CBB9FDD44FDE0F5C4531FEFA74E9E207CAEBDEFA8`;
- Skriptbytes: `5085`;
- Skript-SHA-256: `8E7AAD2C3FF5E397FE54B81CC6EF1F72CCA82BDF36DD834E6C50D2B232EAF13B`;
- Aufrufbloecke mit `powershell.exe`: `1`;
- `-PolicyProbe` im Aufrufblock: `1`;
- `-ExecutionPolicy` im Aufrufblock: `0`;
- Hostliteral: `C:\Windows\System32\WindowsPowerShell\v1.0\powershell.exe`;
- Hostargumente: genau `-NoLogo -NoProfile -NonInteractive -File` plus absoluter Skriptpfad und `-PolicyProbe`;
- Parserfehler des Skripts: `0`;
- Befehle im Probe-Zweig: `0`;
- Exit-Anweisungen im Probe-Zweig: `1`;
- Vertrags-JSON gegen AST-Literal: ordinal exakt gleich;
- erwartete Ausgabezeilen: `1`;
- erwarteter Exitcode: `0`;
- erwarteter Standardfehler: `0` Bytes;
- verpflichtende Vertragsmerkmale der Vollstaendigkeitspruefung: `11/11` vorhanden;
- Retry-Konstruktionen im Aufrufblock: `0`;
- finales Ausgabeziel vorhanden: nein;
- Stagingziel vorhanden: nein;
- `git diff --check`: ohne Befund;
- ausgefuehrte Policy-Probes: `0`;
- gestartete Skriptprozesse: `0`;
- Realpfadabfragen: `0/54`;
- erzeugte Inventurartefakte: `0`.

Die Gegenbaseline ist der unveraenderte statische Nullzustand ohne Prozessstart, Skriptausfuehrung, Realpfadabfrage oder Artefakterzeugung.

## Technische Interpretation

Der Vertrag legt einen einzigen, absoluten und nicht durch `-ExecutionPolicy` veraenderten Aufruf fest. Vorbedingungen verhindern einen Start bei abweichender Skriptidentitaet oder belegten Ausgabezielen. Nach dem Prozess sind nur Ausgabe, Standardfehler, Exitcode und die beiden gebundenen Ausgabeziele zu vergleichen. Jede Abweichung beendet den Vorgang ohne Retry, alternative Hostwahl oder erweiterten Diagnoseaufruf. Die erwartete JSON-Zeile entspricht exakt dem statisch geparsten Probe-Literal.

## Grenzen und nicht gepruefte Annahmen

Die Abnahme belegt nur die Konsistenz des Vertrags. Hostexistenz, Execution Policy, Prozessstart, Laufzeitausgabe, Standardfehler, Exitcode und tatsaechliche Nullzugriffswirkung wurden nicht beobachtet. Produktion, Inventur, Realpfadzugriff, Manifest, Resolver, G2 und Huerde G bleiben ausserhalb des Umfangs. Es liegt kein G1- oder MCM-Befund vor.

## Konkrete Schlussfolgerung

Die unabhaengige statische Abnahme von `213ZZH` ist bestanden. Skriptbindung, absolute Aufrufstruktur, Vor-/Nachpruefungen, Abbruchbedingungen, JSON-Ausgabe, Exitcode, leerer Standardfehler sowie Null-Artefakt-, Null-Realpfad-, Ein-Prozess- und Kein-Retry-Regel sind konsistent. Keine Zielabweichung ist erkennbar.

## Naechster begrenzter Schritt

Als naechstes kann ausschliesslich ueber die gesonderte Freigabe genau eines `-PolicyProbe`-Aufrufs nach `213ZZH` entschieden werden. Bei Freigabe darf der Aufruf genau einmal und ohne Retry erfolgen; Produktionsaufruf, Inventur und Realpfadzugriff bleiben weiterhin gesperrt.
