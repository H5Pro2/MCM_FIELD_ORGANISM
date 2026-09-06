# S2-NC: Einmalige Rezeptormaterialisierung

## Technischer Abschluss

Lauf-ID: `s2nc-receptor-materialization-20260906-01`.
Status: `RECEPTOR_MATERIALIZATION_COMPLETE`, Exit-Code `0`.
Die anschliessende einmalige read-only Belegpruefung bestand mit
`MATERIALIZATION_EVIDENCE_VALID`, Exit-Code `0`.

Genau 23 versiegelte Quellen wurden in ihrer literalen Reihenfolge s001
bis s023 regeneriert und jeweils einmal unmittelbar mit
`LogSpectralReceptor.analyze` analysiert. Alle 23 Aufrufe kehrten zurueck;
alle 1.104 Werte waren endlich und innerhalb der gebundenen Normalform
`0..1`. Es gab keinen technischen Abbruch, Retry oder Parameterwechsel.

Dies ist ausschliesslich ein Quellen-/Rezeptormaterialisierungsbefund.
Eine Selektivitaet, Anwendbarkeit oder fachliche Vorhersage wurde nicht
ausgewertet. Insbesondere wurden keine Distanzen und weder `MEAN_L1_24`
noch `ALL_BANDS_24` berechnet.

## Uebernahme der Vorversiegelung

Die vorhandenen Wurzeln wurden vor jeder Regeneration read-only geprueft:

- Ausfuehrungsdigest:
  `00a0f5d177d11702b6ac08056d08b0501f125cefa8f0c0f1e3b651b894c67ae2`;
- Auswertungsdigest:
  `5f81b3e4c2e1f746659a9ef529ad6af91dbe0e890c4043edbd99ebf1ea36e641`;
- Siegeldigest:
  `ac2ec3e0441fb463c2a1a80d8cb296bbc4934f7555899c5750aa32a0ea56679b`.

Alle sieben gebundenen Dokument-/Quellhashes und der Skripthash von
`seal_inventory.py` stimmten. Rezeptdigests, Reihenfolge, Zeitfenster,
Profil, Referenz-/Hinweistrennung und Panelstruktur waren konsistent.
Die Pruefung erzeugte keine PCM-Payloads und rief keinen Rezeptor auf.
Ihre Ausgabe ist unveraendert in `preseal-check.json` enthalten.

Vorhandenes Quelleninventar, Vorversiegelungsartefakte und die ausdruecklich
beauftragte Rollentrennung in `AGENTS.md` wurden unveraendert mit Commit
`45ee5c5` gesichert und vor der Materialisierung nach `origin/main` gepusht.
Das Vorversiegelungsskript wurde nicht erneut ausgefuehrt oder importiert.
Es wurde kein neues Korpus erzeugt oder neu versiegelt.

## Kleine Materialisierungsroutine

Die private Routine liegt in
`tools/_s2nc_private_receptor_materialization.py`.
Quellcommit vor dem Lauf:
`c9af1babc91f667d4d77827b97c83eb385d14314`.
Routine-SHA-256 vor und nach der Ausfuehrung:
`8a2898d9e6bf6a3d0ca5da527008bb8fe361f37fba892631857b34185e491d14`.

Der statische Codecheck bestaetigte Syntax, genau eine Analyze-Aufrufstelle
und AST-Identitaet der uebernommenen reinen `pcm_bytes`-Funktion mit der
bereits versiegelten Generatorfunktion. Inventarbildung, Panels und
Auswertungsfunktionen des Vorversiegelungsskripts wurden nicht uebernommen.
Die Routine regeneriert ausschliesslich die Rezepte des Ausfuehrungsplans.

Die einzige Projektimportgrenze der Routine ist der unveraenderte
`LogSpectralReceptor` mit `LogSpectralConfig`. Es wird ein Rezeptor fuer
alle 23 direkten Fensteranalysen verwendet, keine rollende Audiopipeline.
Python `3.14.4`, Windows x64; NumPy `2.4.4`.
Das Profil bleibt `48000/4800/480/50/18000/48`.

Der Auswertungsplan wird waehrend der Materialisierung ausschliesslich als
Bytehash gebunden, nicht als Rollen- oder Sollrelation geparst. Die Routine
benutzt keine Regeln, Konkurrenzpanels oder Fallbewertungen des Plans.

Die neue Lauf-ID wird durch exklusive Verzeichnisanlage verbraucht. Ein
technischer Fehler erhaelt Quellen-ID, Ordinalzahl, Phase, Zahl der
vollstaendig validierten Analysen sowie getrennte Aufruf-/Rueckkehrzaehler.
Es gibt keine Fehlerwiederholung. Dieser Abbruchpfad wurde statisch geprueft;
es wurde kein zusaetzlicher Fehlerlauf ausgefuehrt.

## Einziger Aufruf und Wertebindung

Aus dem Workspace-Root:

```text
python -m tools._s2nc_private_receptor_materialization
```

Vor jedem Analyze-Aufruf wurden genau 19.200 PCM-Bytes gegen den jeweiligen
versiegelten SHA-256 geprueft. Die Samples blieben Mono-F32LE bei 48.000 Hz,
jeweils 4.800 Samples innerhalb `[-1,1]`. Es gab kein Clipping, keine
Nachnormalisierung und keine Aenderung der Erzeugungsreihenfolge.
Nach jedem Aufruf wurden PCM-Payload und Sampleansicht verworfen.

Die Quellenfenster liegen auf `s2nc-source-sample-clock` bei
`[(n-1)*4800, n*4800)`. Das sind deklarierte PCM-Quellzeiten; die Routine
gibt sie nicht als native Zeitstempel einer rollenden Rezeptorpipeline aus.

Jeder reduzierte Beleg bindet Quelle, Rezept, PCM-Hash, Ordinalzahl,
Quellfenster, Ausfuehrungsdigest, Profil, 48 Werte, kanonischen Wertdigest
und Binary64-Little-Endian-Bytedigest. `materialized_state_digest` bezeichnet
den Digest dieses privaten reduzierten Belegs, keinen Memoryzustand.
Der Profilbeleg enthaelt die unveraenderte Konfiguration, alle 48
Kanalrollen und ihre Frequenzgeometrie. Profilbelegdigest:
`ee29cafe6b5b9f1e5bc632897f9a5c48c74f32d0b839d1f69cf7da3ef304c196`.

Die atomare Ergebnisdatei `result.json` besitzt 54.086 Bytes:

- Record-Digest:
  `b335416ea03284e59c2eda83586d19081eaeef4885644e2c12ff97e2ab6ad236`;
- Datei-SHA-256:
  `f58aa66491371687e626fcaf939857e22ae8fdb54186df387cd6243ceb3c038f`.

`call.txt` haelt Kommando, Exit-Code und Prozessausgabe fest.
Rohbytes, Distanzen, Regeln, Zielwerte und Kontextkandidaten sind nicht
Teil der Ergebnisdatei. Saemtliche Quellenbindungen blieben unveraendert.

## Einmalige unabhaengige Belegpruefung

Die Abschlusspruefung lief in einem getrennten Python-Prozess nur mit der
Standardbibliothek. Ihre unveraenderte, nachtraeglich abgelegte Quelle ist
`integrity_check.py`; sie wurde danach nicht erneut ausgefuehrt.

Geprueft wurden kanonische Datei-/Recordformen, alle Quellenhashes,
23 Reihenfolge- und Zeitbindungen, Profil und Kanalrollen, 48 Werte je
Quelle, beide Wertdigests sowie alle reduzierten Belegdigests und Zaehler.
Die feste Zustandsfeldmenge schliesst zusaetzliche Rohpayloadfelder aus.
Die Pruefung berechnete weder PCM noch Rezeptorwerte oder Distanzen neu.
Der Ergebnisdateihash blieb vor und nach ihr identisch.

`verification.json` bindet den Verifikationsdigest
`bbfc80e099f7ef47c54bfd839e04af214fd047e1cd1462c67f4c5a006322d761`.

## Rueckmeldung an den Analysten

Die versiegelten Quellen sind jetzt vollstaendig und technisch gueltig als
23 reduzierte Rezeptorbelege verfuegbar. Abbruchstelle: keine.
Memory-, Kontext-, Feld-, Runtime-, Regel- und Distanzaufrufe: jeweils `0`.
Historische Quellen und Ergebnisbelege bleiben unveraendert; S2-MT Lauf 05
bleibt falsifiziert. Die Bootstrap-Datei bleibt ausgeschlossen.

WEITER: Am besten geht es jetzt mit der Pruefung dieses
Materialisierungsbefunds durch den Analysten und danach mit einem eng freizugebenden
Zwei-Regel-Vergleich auf exakt diesen Werten weiter. Ein solcher Vergleich
wurde weder begonnen noch durch diesen Befund automatisch freigegeben.
