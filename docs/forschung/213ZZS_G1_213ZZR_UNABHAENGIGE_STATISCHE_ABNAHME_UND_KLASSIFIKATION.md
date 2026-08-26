# 213ZZS - Unabhaengige statische Abnahme und Klassifikation von 213ZZR

## Einordnung

`213ZZS` ist kein Forschungslauf und erhaelt keine Laufnummer. Gegenstand ist ausschliesslich die unabhaengige statische Abnahme des in `213ZZR` dokumentierten einmaligen `-PolicyProbe`-Vertragspruefschritts. Es wurde kein weiterer Prozess oder Aufruf gestartet.

## Forschungsfrage und Auftrag

Ist das in `213ZZR` eingebettete 25-Felder-Protokoll intern konsistent, stimmen Base64, Bytezahlen und SHA-256 beider Rohstroeme, wurden Prozess-, Retry-, Ziel- und Null-Artefakt-Regeln eingehalten, und ist die enge Klassifikation anhand der ASCII-Marker methodisch gedeckt?

## Verwendete Quellen

- aktueller Uebergabe-Eingang;
- `docs/forschung/213ZZR_G1_POLICYPROBE_EINZELAUFRUF_TECHNISCHER_VERTRAGSABBRUCH.md`;
- `docs/forschung/213ZZP_G1_POLICYPROBE_ROHBYTEBASIERTER_STATISCHER_AUSFUEHRUNGSVERTRAG.md`;
- `docs/forschung/213ZZQ_G1_213ZZP_UNABHAENGIGE_STATISCHE_ABNAHME.md`.

Keine externen Quellen wurden verwendet.

## Verwendete Dateien und Schnittstellen

Die Dokumente wurden ausschliesslich statisch gelesen. Das eingebettete JSON wurde strukturell geparst. Standardausgabe und Standardfehler wurden aus ihren Base64-Feldern in Bytearrays rekonstruiert; Bytezahl, SHA-256 und ASCII-Teilfolgen wurden unabhaengig geprueft. Es wurde keine Textkodierung fuer nicht-ASCII-Inhalte angenommen.

## Durchgefuehrte Schritte

1. Bytegroesse und SHA-256 von `213ZZR` bestimmt.
2. Das eingebettete JSON geparst und die Anzahl seiner Felder geprueft.
3. Standardausgabe aus Base64 rekonstruiert und Bytezahl sowie SHA-256 reproduziert.
4. Standardfehler aus Base64 rekonstruiert und Bytezahl sowie SHA-256 reproduziert.
5. Fehlergruende ordinal gegen alle beobachteten Sollabweichungen verglichen.
6. Exitcode, `contract_pass`, Startversuche, Prozesszahl und Retry-Zahl geprueft.
7. Vor- und Nachzustand von Final- und Stagingziel geprueft.
8. Null-Artefakt-Regel geprueft.
9. Rohbytes des Standardfehlers auf die ASCII-Teilfolgen `about_Execution_Policies` und `UnauthorizedAccess` geprueft.
10. Klassifikation gegen die methodische Grenze zu ungepruefter Quelle, Scope und Konfiguration geprueft.

## Messergebnisse und Gegenbaselines

- `213ZZR`-Bytes: `7398`;
- `213ZZR`-SHA-256: `1AA843D50A5C72DF621ABF70B6B64E7592A6705F88914A3115720D707DA8A05F`;
- JSON-Protokollfelder: `25/25`;
- rekonstruierte Standardausgabebytes: `0`;
- protokollierte Standardausgabebytes: `0`;
- reproduzierter Standardausgabe-SHA-256: `E3B0C44298FC1C149AFBF4C8996FB92427AE41E4649B934CA495991B7852B855`;
- Standardausgabe-Bytezahl und Hash konsistent: ja;
- rekonstruierte Standardfehlerbytes: `460`;
- protokollierte Standardfehlerbytes: `460`;
- reproduzierter Standardfehler-SHA-256: `C9B3653E516FDE779A6983224B3847E42FDB8D3A7BEE3B4243EC5EA3C8BF4B85`;
- Standardfehler-Bytezahl und Hash konsistent: ja;
- ASCII-Marker `about_Execution_Policies`: vorhanden;
- ASCII-Marker `UnauthorizedAccess`: vorhanden;
- Fehlergruende vollstaendig und ordinal konsistent: ja;
- Exitcode: `1`;
- `contract_pass`: `false`;
- Startversuche: `1`;
- gestartete Prozesse: `1`;
- Retry: `0`;
- Beobachterartefakte: `0`;
- Finalziel vor/nach Aufruf vorhanden: nein/nein;
- Stagingziel vor/nach Aufruf vorhanden: nein/nein;
- Finalziel bei Abnahme vorhanden: nein;
- Stagingziel bei Abnahme vorhanden: nein;
- weitere Aufrufe in dieser Abnahme: `0`;
- Realpfadabfragen: `0`.

Die Erfolgsbaseline aus `213ZZP` verlangt 123 gebundene Standardausgabebytes, leeren Standardfehler und Exitcode `0`. Beobachtet wurden 0 Standardausgabebytes, 460 Standardfehlerbytes und Exitcode `1`. Die Sicherheitsbaseline verlangt genau einen Prozess, keinen Retry, keine Artefakte und freie Ziele; sie wurde vollstaendig eingehalten.

## Beobachtetes Ergebnis

Das 25-Felder-Protokoll ist intern konsistent. Beide aus Base64 rekonstruierten Rohstroeme stimmen in Bytezahl und SHA-256 mit dem Protokoll ueberein. Alle sieben protokollierten Fehlergruende entsprechen den Abweichungen von den Sollwerten. Prozess-, Retry-, Artefakt- und Zielzustandsfelder belegen die Einhaltung der Sicherheitsgrenzen.

## Technische Interpretation

`contract_pass=false` ist korrekt. Der Vorgang ist als technischer, fail-closed Vertragsabbruch zu klassifizieren. Die Rohbytes tragen beide gebundenen ASCII-Marker und stuetzen deshalb die enge Einordnung als mit PowerShell-Ausfuehrungsrichtlinien verknuepfte unautorisierte Ablehnung des Skriptstarts.

## Grenzen und nicht gepruefte Annahmen

Nicht bestimmt wurden Quelle, Geltungsbereich, Prioritaet oder konkrete Konfiguration einer Richtlinie. Es erfolgten keine Policy-Abfrage, kein Registry-Zugriff, kein Diagnoseprozess und keine nicht-ASCII-Textinterpretation. Aus dem technischen Abbruch folgt kein G1- oder MCM-Befund.

## Konkrete Schlussfolgerung

`213ZZR` besteht die unabhaengige statische Abnahme und Klassifikation. Dokumentation, Rohstrombindungen, Fehlergruende und Sicherheitszaehler sind konsistent; der Aufruf selbst bleibt ein nicht bestandener, verbrauchter Einzelvertrag. Die enge Marker-basierte Klassifikation ist zulaessig, weitergehende Ursachenbehauptungen sind nicht gedeckt. Keine Zielabweichung ist erkennbar.

## Naechster begrenzter Schritt

Ein weiterer Aufruf ist nicht zulaessig. Als naechstes kann ausschliesslich ein enger statischer Vorschlag zur methodischen Behandlung der nachgewiesenen technischen Ausfuehrungsgrenze formuliert werden, ohne Policy-Abfrage, Registry-Zugriff, Alternativhost, Retry oder Aenderung der Systemkonfiguration. Jede praktische Diagnose oder Ausfuehrung benoetigt eine neue ausdrueckliche Freigabe.
