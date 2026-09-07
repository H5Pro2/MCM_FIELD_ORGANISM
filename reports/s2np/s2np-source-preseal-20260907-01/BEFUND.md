# S2-NP: einmalige rezeptorfreie Vorversiegelung

Lauf-ID `s2np-source-preseal-20260907-01`, 2026-09-07.
Nach bestandener neutraler Qualifikation 16/16 genau ein Vorversiegelungs-
aufruf und anschliessend genau eine unabhaengige read-only Bindungspruefung.
Kein Retry, keine Quellenkorrektur und keine Rezeptorvorpruefung.

```powershell
& C:/Python314/python.exe -m reports.s2np.preseal_once
```

Arbeitsverzeichnis: `C:/Users/TV/Documents/MCM_FIELD_ORGANISM/workspace`.
Exit-Code 0. Siegelstatus `S2NP_SOURCES_PRESEALED`;
Pruefstatus `S2NP_PRESEAL_BINDINGS_VALID`.

## Tatsaechlicher Umfang

- 12 versuchte und 12 abgeschlossene PCM-Erzeugungen in versiegelter Folge
  np-a01..np-a12; 57.600 Samples, insgesamt 230.400 erzeugte PCM-Bytes.
- Je Quelle 4.800 Samples / 19.200 Byte; immer nur ein vollstaendiger
  PCM-Bytepuffer. Hash vor Freigabe des Puffers, kein PCM-Rohdatenartefakt.
- Zwoelf eigenstaendige Quellenidentitaeten und native Fenster 0..57.600,
  Uhr `audio.sample`, Snapshotindices in 10er-Schritten 0..110.
- Drei feste Sichten, vier Panels, 40 literale Hinweis-/Panel-Faelle und
  drei bestehende Bedingungen sind als **Metadaten** gebunden, nicht ausgewertet.
- Rezeptor, NJ, Distanzen, Regelvergleich, Memory, Kontext, Feld und Runtime:
  jeweils **0 Aufrufe**. Alle Hauptgates bleiben `False`.

Die Erzeugung verwendet ausschliesslich den unveraenderten reinen
`pcm_bytes`-Koerper aus dem historischen NC-Modul. Auswahl und AST-Digest
sind im Plan gebunden; der historische Moduleinstieg wurde nicht ausgefuehrt.
Keine Eingangsabschwachung, Float32-Zwischenrundung, Normalisierung oder
Anpassung an Filterbankzentren bzw. Messergebnisse.

## Quellenidentitaet und Kollisionen

| Quelle(n) | PCM-SHA-256 |
| --- | --- |
| np-a01, np-a03 | 2e7f681c7300b310640fe4ffa2d0754fced00d3822a2a5ed6483f1ba63d0dc84 |
| np-a02, np-a07 | 80b97d6323c3890a52c31cfc1866fe26e94961fc1a033ae82f990a0eb1f74595 |
| np-a04 | 6573c7f4701af0f49937b00e345ae501c0aeda44e50f771033203fefefd0736c |
| np-a05 | 9c71a0cad8482fff457c5cb487f1da9aa90b6e618f17b0971e923368bb1fa2e8 |
| np-a06 | 9ace77d668677abec33701cc7f5a73b835fe43b44d462e430d6e930270345b6c |
| np-a08 | ea569310c6e274f2b6d1f2a150356480ea36eeb3c6cce216cbc563f1ec95e8f2 |
| np-a09 | ada1012529e7111ff8b0073d478167f65e9b1eab0526d88814a2b19b6f673bbb |
| np-a10 | aaf44bba580170685afe18d95265480a1cc48c59d3232a9a2c5e881822dd7734 |
| np-a11 | ae870428d5d34c0a02eddddbdcf09b9b56b8d4f2aaf56c650653c0856485fcda |
| np-a12 | 6e9522a915dcb8e8487f7f0dbc9e5daa02b1e586861fa380a6b07fd2a04e7581 |

Genau die beiden beabsichtigten Exaktpaare sind bytegleich. Ihre
Quellen-/Zeitdigests bleiben verschieden. Keine weiteren Payloadhash-
kollisionen; keine Deduplication oder Entfernung von Quellen. Vollstaendige
Rezept-, Payload-, Quellen- und Zeitbindungen stehen in `execution-plan.json`.
Zielrelationen und Subtypen stehen ausschliesslich in `evaluation-plan.json`.

## Profil, Umgebung und Belegbindungen

CPython 3.14.4, Build `23116f9`, MSC v.1944, AMD64, Binary64 nearest-even.
Interpreter `C:/Python314/python.exe`, SHA-256
`7ca24f26d6e3f463419ee4f537ddd3acd312c38fe45e678cce08572f26a8bd1a`.
Python-DLLs sind separat gebunden. `math` ist nachweislich Built-in:
`__spec__.origin == "built-in"` und Mitglied von `sys.builtin_module_names`.
Keine erfundene math-Datei. NumPy 2.4.4 wurde ueber Distributionsmetadaten,
Paketpfad, Initialisierungsdatei, Pyd-Binaerdateien und Bibliotheks-DLLs
gebunden, nicht importiert oder numerisch verwendet.

Originalprofil-Digest:
`5c6b2b19281a44023497b435a96b1051905af4bbac493cae7e699ea1320392c7`.
Halbprofil-Digest:
`4a56de2f630055816533ecb45cdef5662157993bc1192023d01cf29e92247c9f`.
Beides ist hier reine Profilmetadatenbindung; NJ wurde nicht ausgefuehrt.

| Beleg | Wurzeldigest | Dateigroesse |
| --- | --- | --- |
| execution-plan.json | bae2b0ef565a5117c28984d40753da39cc1ca82b576e59864c72d57212254664 | 20.382 Byte |
| evaluation-plan.json | 0d2849710a4d321cc63ae42b024f46e0ead3579f0d4dfce9dd4139243e4cd96d | 1.316 Byte |
| seal.json | a72aa07c9dc153f29a187470bce76fb918ce8cbbaeb4f2666c700fb719bf307b | 3.426 Byte |
| verification.json | 1de2a65b9fd918ebf95af524b877cec627a40de89695707aa258aa276ff1a7f7 | 1.450 Byte |

`preregistration.json` hat 14.141 Byte und wurde vor der ersten Quelle
geschrieben. Alle einzelnen Metadatenartefakte bleiben unter 65.536 Byte.
Kein behaupteter Prozesspeaknachweis. Dateihashes der beiden Planwurzeln:
`3e7814f75d5c8d05b24290a04509d1d3eb85cb6aec2b1d3afa1d948b8b19b4f0`
(Ausfuehrung) und
`57fd3d1359df8adff639091b1e2cfd90115b32bd0279affca6a391ece961383d`
(Evaluation). Plan-Dokumenthash unveraendert:
`484f592257fa9cfb245e84aff72ab3c9d2fff92501be0576353dfeaff9d26953`.

## Einmalige unabhaengige lesende Pruefung

Die Pruefung las beide Wurzeln, Siegel und Vorregistrierung. Sie kontrollierte
kanonische Digests/Dateihashes, Quellformen, Rezept-/Zeitbindungen, Sichten,
vollstaendige Panels/Faelle, Profilmetadaten, Rollenabtrennung, Kollisionen,
Zaehler, Ressourcenlimits sowie identische Code-/Umgebungsbindungen.
Alle zehn beobachteten Quelldateihashes blieben gegenueber Qualifikation und
Vorversiegelungsbeginn unveraendert. Auch die vier gelesenen Artefakte blieben
bytegleich; der separate Pruefbeleg bindet deren Vor-/Nachhashes.

**Pruefgrenze:** Die Verifikation erzeugte keinen PCM-Payload erneut. Sie
bestaetigt die Bindung der aufgezeichneten Payloadhashes, nicht durch eine
zweite Erzeugung deren numerischen Inhalt. Der geladene reine Generator-
Funktionskoerper wurde zur Identitaetspruefung nicht aufgerufen. Keine
Rezeptor-, NJ- oder Distanznachrechnung ist Teil dieser Pruefung.

## Ergebnis und naechste Grenze

Die rezeptorfreie Quellenvorversiegelung ist bestanden. Eine gueltige
Rezeptornormalform, veraenderte Rezeptorwerte, Trennleistung, Beziehungserhaltung
oder ein Abrufnutzen wurden **noch nicht** gemessen. Exaktkopien auf Byteebene
ersetzen keinen spaeteren Variantenbefund. Es gibt kein positives Distanzgate.

Historische Belege und Komponenten sowie der NP-Plan blieben unveraendert.
Fremde Aenderungen und Bootstrap werden nicht in die eigene Versionierung
aufgenommen. Keine automatische Freigabe der nachfolgenden Materialisierung.

WEITER: Am besten geht es jetzt mit der Analystenpruefung dieser Quellenbindung
und der separaten Freigabe einer einmaligen Rezeptor-/NJ-Materialisierung
weiter. Vergleichsauswertung und Systemintegration bleiben geschlossen.
