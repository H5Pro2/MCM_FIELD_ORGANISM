# S2-NS: rezeptorfreie Vorversiegelung

Status: `S2NS_SOURCES_PRESEALED`; unabhaengige read-only Bindungspruefung:
`S2NS_PRESEAL_BINDINGS_VALID`.
ID: `s2ns-source-preseal-20260908-01`, Exit-Code `0`.

Nach bestandener neutraler 14/14-Qualifikation genau ein Aufruf:

```powershell
C:/Python314/python.exe -m reports.s2ns.preseal_once
```

Der Einstieg erzeugte einmal die Quellen und rief danach genau einmal den
separaten Offline-Verifikator auf. Kein Retry, keine Ersatzquelle und keine
historische Sealer-Hauptfunktion. Die qualifizierten eigenen und historischen
Quellhashes blieben vor und nach der Versiegelung identisch.

## Beobachteter Umfang

| Bindung | Ergebnis |
| --- | --- |
| PCM-Quellen | 7/7, je 4800 Samples, 48000 Hz, PCM_F32LE |
| RGB-Quellen | 11/11, je 1920x1080 RGB8 |
| Vollstaendige Quellen | 18/18 Versuche abgeschlossen |
| Ereignismetadaten | 31, davon 16 Formationen und 15 Hinweise; nicht ausgefuehrt |
| Geschichten | 3, mit getrennten Startbindungen und literaler Fortsetzung |
| Sichten | LOWER_24 = 0..23, UPPER_24 = 24..47; komplementaer |
| Generierte PCM-Bytes | 134400, maximal ein Fenster mit 19200 Byte gleichzeitig |
| Generierte RGB-Bytes | 68428800, maximal ein Frame mit 6220800 Byte gleichzeitig |
| Persistierte Rohpayloads | 0 |
| Rezeptor / NJ / Distanz / Memory / Feld / Kontext / Runtime | jeweils 0 |
| Hauptgate nach Abschluss | False |

`ns-a01` und `ns-a03` besitzen den identischen Payloadhash
`8b1bdc97e23c97cd974d442e45ee57e3fd855d1ce43b42689917c74a771a49d5`,
bleiben aber getrennte Quellen mit unterschiedlichen Zeit-/Ereignisbindungen
und unterschiedlichen Quellen-Digests (kanonisches Feld `source_digest`):

- a01: `e78ef4a9d192649168bfe9229b7560f71c504ac82bb20ce6cde427c844965dcb`.
- a03: `dfe81ec5be2ae10299a0d39de61d2e95703a4b1e27e14520e2449a20a1900db6`.

Weitere Payloadkollisionen wurden nicht festgestellt. Die a06-Rezeptbindung
enthaelt unveraendert beide Gruppen und alle sechs Partialpositionen,
einschliesslich der Nullamplituden. Ihr Payloadhash lautet
`45867eeffcbfde86c6f1dde3652ed118da8fffd986214b6524dfa1aa75ee5422`.
Keine Quelle wurde anhand von Rezeptorwerten oder Treffern ausgewaehlt.

## Versiegelte Wurzeln

| Beleg | Kanonischer Digest |
| --- | --- |
| execution-plan.json | `bd21e9e5f564e3a11dc2bb0a3dcb40d92a6a5336e863fa10a57c2eb86aa92816` |
| evaluation-plan.json | `bcb99bcf6936d2e361950cf6ea5e615d612ae178d8da919d8e875f6b89680b8c` |
| seal.json | `80de4e919a4aa99f4fdaab01378299a0c83eb9863cab2359c245040c2b9171f8` |
| verification.json | `80d67f262bb316df25dc61058347de513d516e6c78a19da84e8518c0e30b1857` |

Dokument-SHA-256 des unveraenderten NS-Plans:
`a305a9588d164e90ffb19918fbefc561d745b643b768785d3cd057445e65153a`.

Die Ausfuehrungswurzel bindet Rezepte, Payloadhashes, Quellenidentitaeten,
Originalindizes, native Audio-/Videozeiten, gemeinsame Zeitprojektionen,
Profilmetadaten, Generatoren, Code und Umgebung. Nur die getrennte
Evaluationswurzel enthaelt Zielzuordnung, Variantengruppen und Vorhersagen.
Eine Zielstabilisierung oder guenstige Geometrie wurde nicht vorausgesetzt.

Umgebung: CPython 3.14.4, 64 Bit, NumPy 2.4.4 nur fuer RGB-Generierung.
`math` ist mit Spec-Herkunft `built-in` und bestaetigter Mitgliedschaft im
Built-in-Inventar gebunden; keine erfundene Moduldatei. Interpreterdatei,
Python-DLLs, NumPy-Dateien und reine Generatoridentitaeten sind vollstaendig
in der Ausfuehrungswurzel und Vorregistrierung festgehalten.

Ausfuehrungsplan: 44966 Byte; Evaluationsplan: 2768 Byte;
Vorregistrierung: 31532 Byte; Siegel: 7070 Byte. Jede dieser Metadatenformen
liegt unter 65536 Byte; die Beleggruppe liegt unter 4194304 Byte.

## Pruefgrenze

Die einmalige Offline-Pruefung bestaetigt Quellen-/Rezeptformen, Ereignisse,
Zeiten, komplementaere Sichten, Profil-/Code-/Umgebungsbindungen, getrennte
Planwurzeln, Digestverknuepfungen, Zaehler und Kollisionsangaben. Die vier
geprueften Dateien blieben bytegleich. Vollstaendige Datei-SHA-256 stehen
getrennt von kanonischen Wurzeldigests in `verification.json`.

Payloadhashes wurden bei der einmaligen Erzeugung gebildet; die lesende
Pruefung erzeugte keine Payloads erneut. Sie ist daher keine unabhaengige
numerische Reproduktion der PCM-/RGB-Bytes. Rezeptorgueltigkeit, NJ-Ausgaenge,
Memoryerreichbarkeit und Zwei-Sichten-Nutzen bleiben ungeprueft.

Die Zwei-Sichten-Implementierung und der Funktionslauf bleiben gesperrt.
Historische Belege und Bootstrap wurden nicht veraendert; fremde Aenderungen
werden nicht Bestandteil dieser Versionierung.

WEITER: Am besten geht es jetzt mit der Analystenpruefung dieser Quellen-,
Ereignis- und Wurzelbindungen und der separaten Entscheidung ueber den
naechsten begrenzten NS-Schritt weiter.
