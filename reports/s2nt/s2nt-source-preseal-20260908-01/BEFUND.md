# S2-NT: rezeptorfreie Vorversiegelung

Lauf-ID `s2nt-source-preseal-20260908-01`, Datum 2026-09-08.
Ergebnis: `S2NT_SOURCES_PRESEALED`, anschliessend genau einmal unabhaengig
read-only geprueft: `S2NT_PRESEAL_VERIFIED`. Exit-Code `0`, kein Retry.
Voraussetzung war die unveraenderte neutrale **16/16**-Qualifikation unter
`s2nt-source-binding-qualification-20260908-01`; ihre Quellhashes sind auch
an diesen Lauf gebunden.

## Quellen und Ausfuehrungsgrenze

Genau 14 PCM_F32LE-Fenster in der geplanten Reihenfolge erzeugt, je
4800 Samples bei 48000 Hz und 19200 Byte; insgesamt 268800 generierte Bytes.
Maximal ein vollstaendiger PCM-Payload gleichzeitig, nach Hashbildung
freigegeben, keine Rohpayloadablage. Keine Ersatzquelle, Phasenverschiebung,
Auslassung von Nullpartialen, Skalierung, Normalisierung oder Clipping.

| Quelle | Fenster audio.sample | Nativer Snapshotindex | PCM-SHA-256 |
| --- | --- | ---: | --- |
| nt-a01 | [0,4800) | 0 | 5711dc0929d6b5fbc1516758016d16f6093f413ef16a5c2c420cca156b8fd760 |
| nt-a02 | [4800,9600) | 10 | 056e27be93baed7fad9a53eb2b8b86f94d1775caf33af03b7e7698ca13a48aed |
| nt-a03 | [9600,14400) | 20 | 5711dc0929d6b5fbc1516758016d16f6093f413ef16a5c2c420cca156b8fd760 |
| nt-a04 | [14400,19200) | 30 | e8d4331a78509a7b283e8dc9d6116591c50895e390b23845f3cdc984f816abf7 |
| nt-a05 | [19200,24000) | 40 | ee3ad8307018a5d31614e2a04f904a7a0a421e6732422f321e2c6395c82a0ea2 |
| nt-a06 | [24000,28800) | 50 | 4f55ea340de98103903185e57a0043a89f35e5876765c592b0fbf5d3cefa94cd |
| nt-a07 | [28800,33600) | 60 | 40a8007bd07e7b03e2601984c67d84723de112b94ed624eb427581a6b30c424a |
| nt-a08 | [33600,38400) | 70 | 056e27be93baed7fad9a53eb2b8b86f94d1775caf33af03b7e7698ca13a48aed |
| nt-a09 | [38400,43200) | 80 | c48414b62674242313b310171bddfa94fe54113797d17ed3bf021c7fb6df9065 |
| nt-a10 | [43200,48000) | 90 | d2dc7cce4bd6195b73150340706f989ec21547c77dec5b26d532b209b0065de2 |
| nt-a11 | [48000,52800) | 100 | 3bcc870d6d8b89207d79a50d6ef17500d75ae92f7e2020567bd2e32f9d538acf |
| nt-a12 | [52800,57600) | 110 | a91160beef0d4256ac95731a610d07d60bc4224118fbf05f14e16b6e0771f7a8 |
| nt-a13 | [57600,62400) | 120 | 6bc4ca4f4baaa492ac870c46440a9e7705fdf1d8e541cb9dc7eb132f1c676d27 |
| nt-a14 | [62400,67200) | 130 | 136e3e98de1fa7430130be0264d0afefe79eb7b57bdf42540b72fc0341774a49 |

Beabsichtigte Bytegleichheit `nt-a01/nt-a03` und `nt-a02/nt-a08` bestaetigt.
Beide Paare haben getrennte Quellen-/Zeit-/Digestbindungen; keine
Deduplizierung. **Keine weiteren Payloadkollisionen** gefunden. Das ist keine
Aussage ueber spaetere Rezeptor- oder Halbwertgleichheit.

`execution-plan.json` bindet alle vollstaendigen Rezepte und Rezeptdigests,
Quellen-/Payload-/Zeitbindungen, die 25 neutralen Vergleichspaare,
diagnostische 48er-Indexfolge, Rechenfolge, Profile und Budgets.
`evaluation-plan.json` bindet getrennt die Zuordnungen, Variantentypen,
Additions-/Ersetzungskontrollen und alle 24 strikten Ordnungsbedingungen:
acht primaere, vier Referenzzuordnungen und zwoelf Kontrollbedingungen.
Keine Bedingung wurde numerisch ausgewertet. Die Metadatenpruefung berechnet
keine Audiodistanz und waehlt keine Quelle nach spaeterer Trennleistung aus.

## Wurzel- und Umgebungsbindungen

| Bindung | Digest |
| --- | --- |
| NT-Dokument SHA-256 | 917483459ad77f4f2bcba4a578cf4b813d78f6a1afaf9acb4cfaede5ef5a35ea |
| Ausfuehrungswurzel | 512cab06237f98ca0481f6b16764e30bdd99bb18841f0fb204c5e4700ae8673d |
| Evaluationswurzel | 822f9e3ff6292160ba6b417c188aab2fb44f4b068fb9e0a093562b4e2f6bed7d |
| Siegel | ab2f64627d3385592281b6b0b312968bd4ff6397dcc46ec72fafd5779dad676a |
| Read-only Verifikation | 0b1ed1b7755ddd532d6af0c181a3abe1d8893e7c1fb8d9f3efa7a1a4817b229c |
| Rohprofil | 5c6b2b19281a44023497b435a96b1051905af4bbac493cae7e699ea1320392c7 |
| Halbprofil | 4a56de2f630055816533ecb45cdef5662157993bc1192023d01cf29e92247c9f |

CPython 3.14.4, MSC v.1944, AMD64, `C:/Python314/python.exe`;
Interpreter-SHA-256:
`7ca24f26d6e3f463419ee4f537ddd3acd312c38fe45e678cce08572f26a8bd1a`.
`math` ist bestaetigt eingebaut (`origin=built-in`, Built-in-Mitgliedschaft);
keine separate math-Datei behauptet. Python-DLLs, Binary64-Umgebung und
vorhandene NumPy-Dateiidentitaeten sind mitgebunden; NumPy wurde nicht importiert.

Verwendet wurde ausschliesslich die reine `pcm_bytes`-Funktion aus
`reports/s2nc/seal_inventory.py`, isoliert aus dem gebundenen AST, nicht dessen
historischer Einstieg. Datei-SHA-256:
`7709beaa1aede2393d27fa133cb67fa77d3200182d8e10ea7e125c6abd202618`;
Funktions-AST-Digest:
`7cb5396b9047d22872083c210d8f198d5fc9322f74c4469423cc431580c94ebe`.
Die vorhandenen reinen Hilfen fuer Kanonisierung, Dateiablage, Umgebungs- und
literale Profilmetadaten wurden wiederverwendet. Keine historischen
Sealer-/Materialisierungshaupteinstiege ausgefuehrt oder veraendert.

## Pruefgrenze und Ressourcen

Die unabhaengige Pruefung verwendet eine eigene Transkription der
Quellenrezepte, Zeiten, Paarbelegung und Ordnungsmetadaten. Sie kontrolliert
beide Wurzeln, Siegel, Qualifikations-, Generator-, Umgebungs- und
Quellhashbindungen sowie die Exakt-/Kollisionsgruppen. Alle gebundenen
Quellhashes sind vor/nach Qualifikation und Vorversiegelung unveraendert.

**Keine erneute PCM-Erzeugung:** Payloadhashes stammen aus dem einen
Generatorlauf. Die Offline-Pruefung bestaetigt ihre gespeicherte Bindung,
nicht die Bytes durch eine zweite unabhengige Generierung.

Ausfuehrungswurzel 21348 Byte, Evaluationswurzel 3033 Byte,
Vorregistrierung 19971 Byte, Siegel 3859 Byte: jeweils unter 65536 Byte.
Verifikationsbeleg 903 Byte, unter 262144 Byte. Keine Rohdateien gespeichert.
Spaetere Vergleichsgrenzen bleiben unveraendert, sind noch nicht ausgefuehrt.

Rezeptor-, NJ-, Distanz-, Memory-, Feld-, Kontext- und Runtimeaufrufe jeweils
**0**. Gates `False`. NS, historische Belege und Versiegelungen, fremde
Aenderungen und Bootstrap bleiben unveraendert.

Bestaetigt ist ausschliesslich die Quellen- und Bewertungsbindung.
Rezeptorgueltigkeit, tatsaechliche Variation, Ordnungsseparation und
Bestandteilserkennung sind noch nicht untersucht.

WEITER: Am besten geht es jetzt mit der Analystenpruefung dieser
Vorversiegelung und der separaten Entscheidung ueber die einmalige
Rezeptor-/NJ-Materialisierung weiter; noch kein Distanzvergleich.
