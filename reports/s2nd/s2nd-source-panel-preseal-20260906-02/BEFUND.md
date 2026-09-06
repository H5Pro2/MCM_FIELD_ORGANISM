# S2-ND: Rezeptorfreie Vorversiegelung abgeschlossen

Lauf-ID: `s2nd-source-panel-preseal-20260906-02`.
Genau ein neuer Aufruf nach bestandener neutraler Identitaetsqualifikation:

```text
python -m reports.s2nd.seal_inventory
```

Exit-Code `0`, Status `SOURCE_INVENTORY_AND_PANELS_PRESEALED`.
Kein Retry, keine Quellen- oder Parameterkorrektur. Der fruehere Lauf
`s2nd-source-panel-preseal-20260906-01` bleibt unveraendert `NOT_EVALUABLE`.

## Umfang und Herkunft

- 18/18 PCM-Quellen in der gebundenen Reihenfolge erzeugt;
- insgesamt 86.400 Samples und 345.600 PCM-Bytes;
- je Quelle Mono `PCM_F32LE`, 48.000 Hz, 4.800 Samples, 19.200 Bytes;
- vollstaendige Endlichkeits-/Bereichspruefung vor und nach der finalen
  Float32-Rundung, ohne Clipping oder Normalisierung;
- je Quelle Rezeptdigest, PCM-Payloadhash und eigenes Quellzeitfenster;
- zwoelf feste Panels mit expliziten neun B4-/drei Fast-Positionen;
- 48 literal geordnete Faelle je spaeterer Regel;
- 15 verschiedene Payloadhashes, aber weiterhin 18 eigenstaendige Quellen.

Die beabsichtigten Exaktkopien `s001/s007`, `s002/s011` und `s003/s015`
besitzen jeweils denselben Payloadhash und bleiben getrennt mit eigener
Quellen-ID und strikt spaeterem Fenster erhalten. Keine Deduplication.

Die Quellen wurden einzeln erzeugt, gehasht und vor der naechsten Erzeugung
freigegeben. Hoechstens ein 19.200-Byte-PCM-Payload gleichzeitig; keine
Rohbytes in Belegen oder Ergebnisdateien. Diese Speicherdisziplin folgt
aus der unveraenderten Erzeugungs-/Freigabefolge, nicht aus einer neuen
Prozessspeichermessung.

Gebunden ist CPython 3.14.4, Windows x64, mit Interpreterpfad und
Interpreter-SHA-256 sowie Generatorpfad/-hash. `math` ist explizit
`BUILT_IN`, Spec-Origin `built-in`, Built-in-Mitgliedschaft `true`.
Eine separate `math`-Datei oder deren Hash wird nicht behauptet.

## Getrennte Wurzeln

`execution-plan.json` enthaelt nur technische Rezepte, Quellen-, Zeit-,
Profil-, Generator- und Dokumentbindungen, Panelpositionen, Fallfolge,
Beobachtungsbaender, Regeln und Budgets. Keine Sollrelationen,
Variantensubtypen oder Erhaltungsbewertung.

`evaluation-plan.json` bindet nachgeordnet an den Ausfuehrungsdigest die
Sollquellen, Referenzentfernung, Kategorien, Variantensubtypen, Nenner
und D/R/L-Auswertung. Ein leerer Erhaltungsnenner bleibt ausdruecklich
`ERHALTUNG_NICHT_GEPRUEFT`. Gute Exaktkontrollen ersetzen keinen
Variantennachweis. Regeln und Erwartungen wurden nicht ausgefuehrt.

`seal.json` bindet beide Wurzeldigests und Dateihashes, Python-/Generator-
Identitaet, Quellenzaehler, Dokument-/Modulhashes und unveraenderte Nachhashes.
Der Digestgraph fuehrt vom Dokument und den Rezepten zur Ausfuehrungswurzel,
danach zur Evaluationswurzel und abschliessend zum Siegel; keine Rueckkante.

## Bindungsbelege

| Beleg | Kanonische Bytes |
| --- | ---: |
| execution-plan.json | 21.629 |
| evaluation-plan.json | 13.959 |
| seal.json | 2.954 |

Dokument-SHA-256:
`f5241739e3ca18f12f7e104481b820ab13182aee2bea14699c9a8fb8f3891e41`.

Generator-SHA-256:
`9f72d2a9fc9676235cf69b23ea690d25f0a782222c54393ecf5b44107f0ce91c`.

Ausfuehrungsplandigest:
`e29682fe7606f533c068b3a57c5f986a18934cea2b7c0ca977c0c538a6052f22`.

Evaluationsplandigest:
`6f0474cf98ab5cdfa6f3554914b4b0d34c59086198f19c81a11e64381873ecf6`.

Siegeldigest:
`333f15e8ba0a69e50c12481503f089a348a367eec0c8bb2489cc9f184393b61a`.

Datei-SHA-256 von seal.json:
`ba49bcf2eb0a294139b4655d6d532b5a7aa4950f0f63d6b144f03b43d92dc34d`.

## Lesende Abschlusspruefung und Grenze

`postcheck.json` bestaetigt `PRESEAL_BINDINGS_VALID`: Dateihashes,
beide Wurzeldigests, Siegel, 18 Rezeptdigests, Quellenfenster, Fallfolge,
Exaktkopie-Bindungen und fehlende Evaluationsfelder in der Ausfuehrungswurzel
sind konsistent. Dabei wurden keine PCM-Bytes regeneriert. Die elf seit
Qualifikationsbeginn gebundenen Dateien einschliesslich alter Fehlerbelege
blieben bytegleich. Der korrigierte Sealer ersetzt nicht den historischen
Stand unter Commit `db8cfa6`.

Rezeptoranalysen, Distanzberechnungen, Regelvergleiche, Korpusauswertung,
Memory-, Kontext-, Feld- und Runtimeaufrufe: jeweils `0`.
Es liegt noch kein Rezeptor-, Erhaltungs-, Verlust- oder Selektivitaetsbefund
vor. Historische S2-NC-Artefakte und Produktmodule bleiben unveraendert.

WEITER: Am besten geht es jetzt mit der Analystenpruefung dieser
Vorversiegelungsbelege und anschliessend gegebenenfalls der separaten
Freigabe einer einmaligen Rezeptormaterialisierung weiter. Bis dahin
bleiben Rezeptoranalyse und Zwei-Regel-Korpusvergleich geschlossen.
