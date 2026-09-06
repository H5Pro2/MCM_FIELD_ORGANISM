# S2-NF: Rezeptorfreie Quellenvorversiegelung

Status: `S2NF_SOURCES_PRESEALED` und
`S2NF_PRESEAL_BINDINGS_VERIFIED`. Ausgangscommit `bbeb856`.
Lauf-ID: `s2nf-source-preseal-20260906-01`.

Genau ein Vorversiegelungsaufruf nach bestandener neutraler `10/10`-
Qualifikation, anschliessend genau eine unabhaengige lesende Bindungspruefung.
Kein Retry, keine Quellensubstitution oder Parameteranpassung.

```text
C:\Python314\python.exe -m reports.s2nf.preseal_once
```

Workspace-Root als Arbeitsverzeichnis, Exit-Code `0`.
Der Aufrufer erzeugte das zuvor nicht vorhandene Ergebnisverzeichnis
exklusiv. `preregistration.json` bindet vor der ersten PCM-Erzeugung alle
Rezepte, Quellenfenster, Code- und Qualifikationshashes.

## Beobachteter Umfang

- Sieben einzelne Generatoraufrufe, sieben abgeschlossene PCM-Quellen.
- Jeweils Mono PCM_F32LE, 48.000 Hz, 4.800 Samples / 19.200 kanonische Bytes.
- Insgesamt 33.600 Samples / 134.400 erzeugte kanonische Bytes.
- Maximal ein vollstaendiges Quellenfenster gleichzeitig; danach freigegeben.
- Keine Rohpayloadablage, keine Deduplizierung.
- Alle sechs historischen Payloadbindungen stimmen exakt ueberein.
- nf-a01 und nf-a03 besitzen denselben Payloadhash, aber unterschiedliche
  Quellen-IDs, Zeitfenster und Quelldigests.

| Quelle | PCM-SHA-256 |
| --- | --- |
| nf-a01 | 4a2651fb420154c6dbd8604ebbd898da637c5e05c2fe8c7230e60df2bcfd1cdd |
| nf-a02 | 97a11dfcb89615b257d430ab718505b2ec207b8b8684c012ec5bdc6adcea4f5b |
| nf-a03 | 4a2651fb420154c6dbd8604ebbd898da637c5e05c2fe8c7230e60df2bcfd1cdd |
| nf-a04 | 64cf87cb39efc6b235b2484ef8b3356ae89ece84d5b467c0302bd148a4180d2f |
| nf-a05 | b97943fadd28774e36aa4f1eb1f0819a59215816e5cb96bfd8f4ece712a667f6 |
| nf-a06 | 2984a92493a24d8b673bd620ec0e5a3925672f4272b5abfbdab55d8d84385efc |
| nf-a07 | 1b281f3e23cc23f320917094f75c69d195c390cc0bb0aaa7f089b776412b46d7 |

nf-a07 behaelt Seed und die ersten drei Partiale des Grundrezepts;
120 Hz mit Amplitude 3/10 steht unveraendert an vierter Stelle.
Die einmalige Float32-Rundung erfolgt erst nach der Binary64-Summe.
Keine nachgelagerte Addition auf bereits gerundete Samples.

## Identitaet und Ressourcen

CPython 3.14.4, MSC v.1944, AMD64, 64 Bit;
`C:\Python314\python.exe`, Interpreter-SHA-256:
`7ca24f26d6e3f463419ee4f537ddd3acd312c38fe45e678cce08572f26a8bd1a`.
`math` ist nach `__spec__.origin == "built-in"` UND Zugehoerigkeit zu
`sys.builtin_module_names` gebunden. Es wird keine math-Datei erfunden.

Harmonische Quellen verwenden unveraendert die reine `pcm_payload`-Funktion
aus `reports/s2nd/seal_inventory.py`, niemals deren Sealer-Einstieg.
Fuer nf-a02 werden ausschliesslich `S2LBMaterializationError`, `_f32` und
`_materialize_pcm` als unveraenderte AST-Koerper aus dem gebundenen S2-LB-
Quelltext geladen. Dessen Modulimporte und Materialisierung bleiben unaufgerufen.
Datei- und AST-Digests stehen in `generator_identity`.

Der Chirpgenerator liefert sein vorhandenes einzelnes Python-Samplefenster;
dessen Hash entsteht aus skalaren Little-Endian-Float32-Fragmenten ohne
zweite vollstaendige PCM-Bytekopie. 19.200 Bytes bezeichnen die kanonische
Payloadgroesse, NICHT einen gemessenen Python-Prozesspeak. Python-Objekt-
und Verwaltungsaufwand wird damit nicht als null behauptet.

## Versiegelte Wurzeln

Ausfuehrungswurzel: sieben Audiorezepte/Hashes, historische visuelle
Begleitbindungen ohne neue RGB-Erzeugung, Profil `48000/4800/480/50/18000/48`,
native Quellenzeit und die unveraenderten 13 zukuenftigen Ereignisse.
Das sind Planpositionen fuer drei Formationen und zehn Hinweise, keine
ausgefuehrten Memoryereignisse. Haupt-/Rezeptor-/Regelgates bleiben geschlossen.
Zielzuordnung, Variantensubtypen, Sollrelationen und N/D/R/L befinden sich
ausschliesslich in der getrennten Evaluationswurzel.

| Bindung | Kanonischer Digest |
| --- | --- |
| execution_digest | 83da38c8ba7dfb7b2eb6c615d9f646a89eda60a83e3898a177fd08fe632d8cbe |
| evaluation_digest | 253438d0cd4b703a4b6bf2719f94f8aa48b7e01787c10c184c409838502783b9 |
| seal_digest | 5bf3d5465ef2cc57f8183de657ca6bfce223fc397cdf6bcba68932aa50f7cfbd |
| verification_digest | 370a0907ece7012c154cd6ae6df6880f84e24f2dedf0f8ae7ce8973a02d8cbd7 |

Dokumenthash unveraendert:
`d652db5fb9b0ad07ae09ae572235d563d38a37caa99184ee0c4ed05b31f0e16b`.
Dateihashes sind von diesen inneren kanonischen Digests getrennt im Siegel
und im Pruefbeleg gebunden. execution-plan.json: 20.293 Bytes;
evaluation-plan.json: 2.835 Bytes; seal.json: 12.265 Bytes.

## Unabhaengige lesende Pruefung und Grenzen

`verification.json` bestaetigt alle sieben Quellen, getrennte Exaktidentitaet,
Rezept-/Zeit-/Profil-/Generatorbindungen, literale Folge, Budgets und
Evaluationswurzel. Die 47 gebundenen Quell-/Dokumentdateien und die vier
gelesenen Eingabebelege waren vor/nach der Pruefung bytegleich.
Kein erneuter Generatoraufruf. Historische Quellen und S2-NE blieben unveraendert.

Rezeptor-, Distanz-, Regel-, Memory-, Kontext-, Feld- und Runtimeaufrufe:
jeweils **0**. Visuelle Quellen wurden nur aus historischen Literalbindungen
uebernommen; keine neue Analyse. Bootstrap bleibt ausgeschlossen.

Dies ist ausschliesslich ein technischer Quellenbindungsbefund.
Gueltige PCM-Samples garantieren keine spaetere Rezeptornormalform,
keinen positiven Erhaltungsnenner und keinen Selektivitaetsgewinn.
Kein Regelvergleich und keine Erhaltungs- oder Verlustbewertung erfolgt.
Eine zusaetzliche Rezeptorvorpruefung wurde weder eingefuehrt noch ausgefuehrt.

WEITER: Am besten geht es jetzt mit der Analystenpruefung dieser versiegelten
Quellenbindungen und der gesonderten Freigabe des naechsten begrenzten
S2-NF-Schritts weiter.
