# Vorregistrierung des einmaligen Bindungs-Preflights ueber stdin

## 1. Forschungsfrage und Auftrag

Kann ein neuer einmaliger Bindungs-Preflight so vollstaendig vorregistriert
werden, dass Nutzlast, Transport, Ausgabe und Abbruch vor einer separaten
Ausfuehrungsfreigabe unveraenderlich pruefbar sind?

Der Auftrag ist ausschliesslich statisch. Dieses Dokument und die gebundene
Nutzlast werden nicht ausgefuehrt. Runtime-Fixierung, Vertragskonstruktion,
Feldkonstruktion, Hook-Ausfuehrung und Effektmessung bleiben gesperrt.

## 2. Verwendete Quellen und Dateien

- `AGENTS.md`
- `AKTUELLER_FORSCHUNGSWEG.md`
- aktueller Korrektur-Eingang des Forschungshelfers
- `docs/forschung/214_STATISCHE_VORREGISTRIERUNG_STDIN_TRANSPORT_BINDUNGS_PREFLIGHT.md`
- `mcm_field_organism/_previous_state_integration_contract.py`
- `mcm_field_organism/_previous_state_minimal_runner.py`
- `mcm_field_organism/_runtime_fixation_binding.py`
- `mcm_field_organism/_runtime_fixation_handoff.py`
- `tests/test_previous_state_integration_contract.py`

Keine externe Quelle wurde verwendet. Die Python-Dateien wurden nur statisch
gelesen und weder importiert noch ausgefuehrt.

## 3. Final fixierte stdin-Nutzlast

Die vollstaendige Nutzlast liegt ausschliesslich als Byteartefakt vor:

```text
docs/forschung/215_BINDUNGS_PREFLIGHT_STDIN_NUTZLAST.txt
```

Ihre verbindliche Bytebindung lautet:

```text
Kodierung: ASCII, zugleich gueltiges UTF-8
BOM: nein
Zeilenenden: LF
abschliessendes LF: ja
Byteumfang: 1806
SHA-256: d86be4be95ed54ea461aea4c538639cec179726ccca30b14dd762a605351b393
```

Eine Abweichung auch nur eines Bytes sperrt den Preflight. Eine Darstellung
der Nutzlast in einer Shellzeichenkette oder eine nachtraegliche
Rekonstruktion aus diesem Dokument ist unzulaessig.

## 4. Festgeschriebener Prozess- und Transportvertrag

Ein spaeterer, separat freizugebender Preflight darf genau einen Prozess im
Workspace-Stamm starten. Anwendung und Argumentvektor sind exakt:

```text
.venv\Scripts\python.exe -B -I -
```

Vor dem Prozessstart muss der Supervisor Digest und Byteumfang des
Nutzlastartefakts gegen Abschnitt 3 pruefen. Danach darf er genau die 1806
gebundenen Bytes in genau einer Schreiboperation an `stdin` uebergeben und die
Pipe unmittelbar schliessen. Verboten sind `-c`, temporaere Python-Dateien,
interaktive Eingabe, zweite Schreiboperation, Retry, Parallelitaet,
Kindprozess und automatische Fortsetzung.

Der feste absolute Workspace-Eintrag in der Nutzlast kompensiert den durch
`-I` isolierten Importpfad. Die Nutzlast veraendert weder Arbeitsverzeichnis
noch Umgebung.

## 5. Fixierte Preflight-Funktion

Nur fuer einen spaeter separat freigegebenen Einmalaufruf enthaelt die
Nutzlast exakt folgende einmalige Reihenfolge:

```python
binding = _build_private_fixation_binding()
bundle = _execute_private_runtime_fixation(binding)
manifest = build_locked_previous_state_minimal_manifest()
contract = _build_private_integration_contract(bundle, manifest)
```

Danach wird ausschliesslich `asdict(contract)` mit sortierten Schluesseln,
kompakten JSON-Trennzeichen und ASCII-Escaping kanonisiert. Der
`contract_digest` ist SHA-256 dieser UTF-8-Bytes. Rohbundle, Einzeldigests,
Kontakte, Feldwerte und Zwischenobjekte duerfen den Prozess nicht verlassen.

## 6. Ausgabegrenze

Im Erfolgsfall ist genau eine kompakte, schluesselsortierte ASCII-JSON-Zeile
mit abschliessendem LF zulaessig. Sie enthaelt ausschliesslich:

```text
contract_digest
execution_locked
field_execution_allowed
hook_execution_allowed
effect_measurement_allowed
```

Die maximale Gesamtausgabe auf `stdout` betraegt 4096 Byte und wird bereits
vor dem Schreiben in der Nutzlast geprueft. Jede weitere Ausgabe, jeder
Zwischenwert und jede Ausgabe ueber 4096 Byte sind unzulaessig. Im Fehlerfall
ist keine Nutzlastausgabe vorgesehen; der Prozess endet mit Exitcode 1 ohne
Traceback. Unerwartete Ausgabe auf `stderr` sperrt das Ergebnis ebenfalls.

## 7. Abbruchkriterien

Der spaetere Preflight muss ohne Teilresultat, Retry oder Fortsetzung
abbrechen, wenn mindestens eines der folgenden Ereignisse eintritt:

1. Nutzlastdatei fehlt oder Digest, Byteumfang, BOM, LF-Form oder Schluss-LF
   weichen ab;
2. Interpreterpfad, Argumentfolge oder Arbeitsordner weichen ab;
3. stdin wird nicht vollstaendig, nicht einmalig oder nicht geschlossen
   uebergeben;
4. Import, Parser, Bindung, Runtime-Fixierung, Manifest- oder
   Vertragskonstruktion schlagen fehl;
5. die Ausgabe ist nicht genau eine zulaessige JSON-Zeile, enthaelt andere
   Schluessel, ueberschreitet 4096 Byte oder `contract_digest` ist kein
   kleingeschriebener SHA-256-Hexdigest;
6. die vier Sperrwerte sind nicht exakt `execution_locked == true`,
   `field_execution_allowed == false`, `hook_execution_allowed == false` und
   `effect_measurement_allowed == false`;
7. `stderr` ist nicht leer, der Exitcode ist nicht eindeutig oder eine
   Laufzeitgrenze wird ueberschritten;
8. Datei-, Metadaten-, Prozess-, Thread-, Netzwerk-, Geraete-, Cache-,
   Bytecode- oder sonstige nicht vorregistrierte Seiteneffekte werden
   beobachtet.

Jeder Abbruch ist ausschliesslich ein technischer Preflight-Abbruch und kein
fachlicher Befund.

## 8. Unveraenderte Sperren

Diese Vorregistrierung setzt kein Freigabefeld. Insbesondere bleiben
gesperrt:

- die Ausfuehrung dieser Preflight-Nutzlast;
- jede weitere oder wiederholte Runtime-Fixierung;
- Feld- und Rezeptorkonstruktion;
- Integrator-, Runner-, Executor- und Hook-Ausfuehrung;
- Effektmessung und wissenschaftliche Interpretation;
- Public-AV, Live-Sensorik und physischer Weltkontakt;
- persistente Zustands- oder Memory-Artefakte;
- automatische Fortsetzung und Produktionsanbindung.

## 9. Durchgefuehrte Schritte und Ergebnis

- Die verbindlichen Projektdokumente wurden erneut gelesen.
- Die beteiligten privaten Schnittstellen wurden statisch abgeglichen.
- Die finale Nutzlast wurde als ASCII/LF-Byteartefakt erstellt.
- SHA-256, Byteumfang, BOM-Freiheit, LF-Form und Schluss-LF wurden statisch mit
  Dateibyte-APIs bestimmt.
- Die Nutzlast und keine Projektfunktion wurden ausgefuehrt.

Beobachtete Messung: nur Dateiumfang 1806 Byte und der in Abschnitt 3 genannte
SHA-256-Digest. Gegenbaselines wurden nicht ausgefuehrt. Diese Arbeit erhaelt
keine Laufnummer.

## 10. Grenzen, Nichtnachweis und offene Annahmen

Nicht geprueft sind Parserfaehigkeit unter dem fixierten Aufruf, tatsaechliche
stdin-Uebergabe, Imports im isolierten Prozess, Runtime-Fixierung,
Vertragskonstruktion, resultierender Vertragsdigest, Ausgabe und
Seiteneffektfreiheit. Die Bindbarkeit des realen `_FixedDigestBundle` bleibt
offen.

Es gibt keinen Befund zu Vorzustandswirkung, Feldwirkung, Memory,
Organisation, Topologie, Bedeutung, Semantik, Selbstregulation oder KI.

## 11. Schlussfolgerung und naechster Schritt

Der einmalige Bindungs-Preflight ist nun mit finaler stdin-Nutzlast, festem
SHA-256-Digest, festem Byteumfang, exaktem Interpreteraufruf, Ausgabegrenze,
Abbruchkriterien und unveraenderten Sperren ausfuehrungspruefbar
vorregistriert. Eine Zielabweichung ist nicht erkennbar.

Kleinster naechster Schritt ist die unabhaengige statische Pruefung der
Dokumente 215 und 216. Erst eine ausdrueckliche spaetere Freigabe darf genau
diese gebundene Nutzlast einmal ausfuehren.
