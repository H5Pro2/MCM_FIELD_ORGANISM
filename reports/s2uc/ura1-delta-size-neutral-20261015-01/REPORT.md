# URA1_STATE_DELTA_V1: Abschluss des einmaligen neutralen Groessenlaufs

Pruefpaket: 238cd874-eaf1-4447-8871-8ecf29997543. Clientdatum: 2026-10-15.

## Ergebnis und Aussagegrenze

**COMPLETE_NEUTRAL_SIZE / PASS_DELTA_INTEGRITY.** Genau ein Start, genau die feste
D_ITEMS-x16-Geschichte mit 1024 Frames je Arm. Vollstaendige Referenzen und
U/R-Gleichheitspruefungen bestanden; unabhaengige Rekonstruktion gegen alle
acht vor Kodierung gespeicherten Erfassungsanker und den Strukturanker bestanden.
Keine Leistungswertung, Forschungsbereitschaft oder Freigabe weiterer Laeufe.
Der Erfolg gilt ausschliesslich fuer diesen periodischen Handfall.

## Vorstartbindung und Einmaligkeit

Vorstart-SHA-256: `d32a621cf372ac09ddaaae115b6121f8251ca458c437e5ebef79069919e872a9`.
271 Dateien gebunden, einschliesslich der unveraenderten 202 Vorgaengerdateien,
der sechs Delta-Dateien, neuer Einstieg/Engine/Tests/Vertrag, Qualifikationsbelege
und alter Ergebnisbelege. Interpreter, DLLs, Runtime, Material und Grenzen sind
in `../ura1-delta-size-preparation-20261015-01/prestart.json` festgehalten.
Exakter Aufruf: `C:\Python314\python.exe -m tools.s2uc_ura1_delta_size_once run C:\Users\TV\Documents\MCM_FIELD_ORGANISM\workspace\reports\s2uc\ura1-delta-size-preparation-20261015-01\prestart.json`.
Material-SHA-256: `c36aaf13ba21830b628ffb98e97400bc4f79090f2415b401429100eb433e11f4`.
Rezept: 16 vorhandene D_ITEMS-Bloecke exakt 16-mal; 256 Bloecke, 1024 Frames.
Die bisherige 128-Frame-Huelle ist unveraendert.

START.json wurde exklusiv reserviert, ist verbraucht und bleibt unveraendert.
Marker-SHA-256: `82463a13d898136d0804f5f517b81d20b3add1cf5c80eaae6d4a67af16fe8608`.
Kein Retry, Resume, zweiter Worker oder Ersatzfall. Die Fortsetzungsnachricht
war keine zusaetzliche Einmalfreigabe. Alter Dictionary-Abbruch samt Marker
und Abschlussdateien sind unveraendert in der neuen Vorstartbindung enthalten.
Alle 271 gebundenen Dateien nach Laufende erneut hashgeprueft.

## Vorbereitung und geaenderte Dateien

S01 Bindung/Material/Runtime/Code/Grenzen, S02 exklusiver Marker,
S03 Kleinfall-End-to-End, S04 manipulierte Encoderwerte/fehlende/vertauschte
Records trotz neuem Envelopehash abgewiesen, S05 Dictionary-Abbruch/Cleanup,
S06 unveraenderte KleinfallhueIle/exaktes Material, S07 Export-/Verwaltungsgrenzen:
**7/7 bestanden**, 5,472 s. Zusaetzliche Startfehler-, Workerfrist- und
Gesamtfristproben bestanden; alle Testprozesse beendet. Testjob-Peak 49.639.424 Byte.
Belege unter `../ura1-delta-size-preparation-20261015-01/qualification/`.
Keine Wiederholung der bereits bestandenen Qualifikation bei Fortsetzung.

Neue Dateien: tools/_s2uc_ura1_delta_size_engine.py,
tools/s2uc_ura1_delta_size_once.py, tests/test_s2uc_ura1_delta_size_once.py,
docs/S2UC_URA1_DELTA_1024_GRENZTEST_VERTRAG_20261015.md und die beiden
separaten Vorbereitungs-/Ergebnisverzeichnisse. README.md,
AKTUELLER_FORSCHUNGSWEG.md und docs/README.md erhalten diese Standseinordnung.
U/R-Kernregeln, unabhaengige Referenzen, Deltaformat und historische Archive
wurden nicht veraendert.

## Vollstaendigkeit und Integritaet

Je Arm: 1024 begonnene und vollstaendig referenzgepruefte Frames,
3072 aeussere Ereignisse, 11276 interne Ereignisse, 512 Prognosen,
511 beobachtete Ziele (3 bis 1023, ungerade); Ziel 1025 bleibt zensiert.
Bestand, Hypothesen, Tickets, Originale, Zellen, Ausgaben und Feedback wurden
gegen die getrennten Referenzen geprueft. Die Paarpruefung bestaetigt die
vorgegebenen gemeinsamen Ereignis-/Zustands- und Metadateninvarianten.
Die policyabhaengigen Ausgaben und Fehler duerfen verschieden sein.

| Folge | Records | Kanonische Byte | SHA-256 |
|---|---:|---:|---|
| /R/events | 3072 | 33368259 | `f59608a254260ad317b53847b0b6a2a2fc5379cbb26ad15110477fa84d6c88e7` |
| /R/forecasts | 512 | 678541 | `424a8ab1ba9ac3be843cc732637dc23a3b9d3034ce34ec819c531cf926e513a8` |
| /R/internal | 11276 | 144932737 | `45aa67703f26a3c9a541b9ee3f8b5d2736348065b220e19881e71010b07c19db` |
| /R/rows | 511 | 40174 | `4cf546eb240db8771c7cf46bffb183c623828ad2417bdae28423269fbe6ea843` |
| /U/events | 3072 | 33368259 | `f59608a254260ad317b53847b0b6a2a2fc5379cbb26ad15110477fa84d6c88e7` |
| /U/forecasts | 512 | 675853 | `a7ad4c7111dbbaac61fa1f924ea522499e7278dc298b16da852ff9e2b373d583` |
| /U/internal | 11276 | 144932737 | `45aa67703f26a3c9a541b9ee3f8b5d2736348065b220e19881e71010b07c19db` |
| /U/rows | 511 | 40238 | `4125a3834a933ae59a0b8a54c12810f745975e6f20b17268d6361b7bf4a01290` |

Strukturanker: `f5a1a229faa1c2d1af62619d1ecaf4335b0b9854d147e7f0e02061de7ce191a2`.
Vollstaendige Rekonstruktion: 358862679 Byte,
SHA-256 `6be2be3dfa6587565552a319d3c65379965d30378133d4d70cdd86402cae2f26`.
Archiv-SHA-256: `d2c8ac7ec1035fde52cc4c20ab83f719860f33fb32229cea6373d923d535666e`.
Decoder importiert weder Encoder noch Policy; Details in Formatvertrag.
Capture- und Decoderfolgen stimmen in Anzahl, Bytezahl und Hash exakt ueberein.

## Gemessene Ressourcen

| Groesse | Messung | Grenze |
|---|---:|---:|
| Dictionary inkl. Werte/Pfade/Deltas | 901970 Byte | 4194304 Byte |
| Dekomprimiertes JSON-Format | 1029374 Byte | 4194304 Byte |
| gzip | 170176 Byte | 524288 Byte |
| Gemeinsamer Kernel-Job-Peak | 146649088 Byte | 536870912 Byte |
| Tabelleneintraege | 16357 | 65536 |
| Referenzkanten | 152878 | 262144 |
| Recordindizes | 30742 | 65536 |
| Collections | 8 | 16 |
| Groesster Einzelrecord | 15198 Byte | 262144 Byte |
| Vorherige Records, kanonischer Peak | 34029 Byte | 16 x 262144 Byte |
| Temporaerer Peak | 170176 Byte | 67108864 Byte |
| Gesamtzeit | 1193.505 s | 3600 s |
| Workerzeit | 1191.638 s | 3540 s |

9414 Wertknoten, 88 Pfade und 6855 Deltas. Keine innere Kompression und kein
Rohspool. Prozessobjekte und Buffer sind im gemeinsamen harten Windows-Job
mitgemessen; beide Prozesse im selben Job verifiziert, Prozesslimit zwei.
Worker-Lifetime-Peak 111333376 Byte. Phasenwerte des Supervisors sind gesampelt;
der gemeinsame Spitzenwert ist kernelgemessen.

| Workerphase | Sekunden | Python-Trace-Peak Byte |
|---|---:|---:|
| capture_references_events_and_anchors | 640.984 | 18975479 |
| envelope_checksum_and_encoding | 220.550 | 15887571 |
| independent_decode | 329.786 | 26480515 |
| cleanup | 0.314 | 23848729 |

Beide Arme geschlossen, Banken nullgesetzt, Originale freigegeben;
Codecstore freigegeben, keine Partialdatei verblieben. Worker Exitcode 0 und
Workerende bestaetigt. Abschluss- und Exportbilanz stehen in closure.json.

Vollstaendige unveraenderte Grenzliste:

- `administration`: 2097152
- `closure`: 1048576
- `collections`: 16
- `dictionary`: 4194304
- `edges`: 262144
- `encoded`: 4194304
- `export`: 67108864
- `gzip`: 524288
- `indices`: 65536
- `job`: 536870912
- `nodes`: 65536
- `preparation`: 8388608
- `record`: 262144
- `source_case`: 32768
- `source_total`: 2097152
- `temp`: 67108864
- `total_seconds`: 3600
- `worker_seconds`: 3540

## Einordnung und naechster Vorschlag

Beobachtet: Dieser eine vollstaendige 1024-Frame-Fall passt in saemtliche
vorgegebenen Grenzen und wird verlustfrei unabhaengig rekonstruiert.
Technische Interpretation: Das Deltaformat beseitigt fuer diesen Fall den
frueher beobachteten Dictionary-Engpass. Die vollstaendige Ausfuehrung dauert
rund 19,9 Minuten; die vorige lineare Kleinfall-Zeitschaetzung war zu niedrig.
Offen: Andere, weniger repetitive Geschichten koennen andere Tabellen- und
Laufzeitprofile haben. Keine allgemeine Skalierungs-, Forschungs- oder
Wirksamkeitsaussage; keine 32-Fall- oder Bootstrapausfuehrung.

Naechster sinnvoller Schritt beim Projektleiter: diesen technischen Nachweis
abnehmen und anhand des bestehenden Forschungsauftrags entscheiden, welches
kleinste noch fehlende Abnahmekriterium vor einer Forschungsfreigabe erforderlich
ist. Kein weiterer gleichartiger Handlauf allein zur Bestaetigung; jede neue
reale Ausfuehrung benoetigt ihren konkreten Auftrag und gegebenenfalls eine
separate Einmalfreigabe. Hier kein technischer Blocker und kein weiterer Start.
