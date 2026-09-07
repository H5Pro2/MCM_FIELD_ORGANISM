# S2-NP: neutrale rezeptorfreie Quellenqualifikation

Lauf-ID `s2np-source-binding-qualification-20260907-01`, 2026-09-07.
Ausgangsstand `db99d89`. Genau ein Qualifikationsaufruf, kein Retry.

```powershell
& C:/Python314/python.exe -m reports.s2np.qualify_once
```

Arbeitsverzeichnis: `C:/Users/TV/Documents/MCM_FIELD_ORGANISM/workspace`.
Der Aufrufer startete genau einmal `python -m unittest
tests.test_s2np_private_source_binding -v`. Beide Aufrufe Exit-Code 0.
**16/16 bestanden**, Status `S2NP_SOURCE_BINDING_QUALIFIED`.
Testprotokoll: `stderr.txt`; `stdout.txt` ist leer. Keine Tests wiederholt.

Vor dem Testaufruf wurden die 16 vollstaendigen Test-IDs, das Kommando,
Interpreter-/Umgebungsbindungen, Ressourcenlimits und zehn Dateihashes in
`preregistration.json` festgeschrieben. `result.json` bindet identische
Vor-/Nachhashes und die Protokollhashes. Ergebnisdigest:
`659936fc3287422e4f8cf9cf878fb3305d269e46169e4d97975a8af83bae6735`.

## Abgedeckter Umfang

1. Literale Quellen-/Frequenz-/Seedbelegung.
2. Quellenidentitaet, unveraenderliche Spezifikation und Reihenfolge.
3. Exaktkopien mit getrennten Identitaets-/Zeitbindungen, ohne NP-Erzeugung.
4. Native Fenster-/Snapshotformen und Ablehnung falscher Uhr.
5. Partialfolge und unveraenderliche Rezeptform.
6. Ein fremdes neutrales 16-Sample-Rezept gegen direkte Binary64-/Float32-
   Nachrechnung. Keine der zwoelf NP-Quellen; 64 Byte pro Testpayload.
7. Explizite Built-in-math-Herkunft und fehlerhafte Herkunftsbindungen.
8. Drei feste Sichten und Manipulation der verteilten Indexmenge.
9. Alle vier Panels, einschliesslich Leerpanel, und 40 feste Faelle.
10. Getrennte Evaluationswurzel und manipulierte Zielrelation.
11. Digestform und Verknuepfung beider Wurzeln.
12. Reine Original-/Halbprofilmetadaten und Profilmanipulation.
13. Ausgabegrenze und bereits vorhandene Zieldatei.
14. Unveraenderlichkeit der Planpruefung und manipuliertes Payloadbudget.
15. Vollstaendige Erhaltung auch unerwarteter neutraler Hashkollisionen.
16. Geschlossenes Gate, ausgeschlossene Modulimporte/Ausfuehrungsfreigaben.

Die Generatorpruefung verwendet den unveraenderten, per AST ausgewaehlten
`pcm_bytes`-Funktionskoerper. Weder sein historischer Moduleinstieg noch
Rezeptoren, NJ, Vergleichsregeln, Memory, Kontext, Feld oder Runtime wurden
importiert bzw. ausgefuehrt. Die erlaubte neutrale PCM-Erzeugung ist kein
NP-Korpuszugriff. Weitere neutrale Daten sind Planmetadaten und synthetische
Digests, nicht als echte NP-Payloadbindungen ausgegeben.

## Qualifizierte eigene Dateien

| Datei | SHA-256 |
| --- | --- |
| tools/_s2np_private_source_binding.py | 004ea7c8841e5f0b68fe9191604b0a0a7337ac568af2205dca900dd2ae874b12 |
| tools/_s2np_private_preseal_verification.py | f8148f46427ace6081b9baae3673b230e7bb5b15d6ef2f5daed7c84a89d99e24 |
| tests/test_s2np_private_source_binding.py | 606510948f0007e99a62ff77a81f30ac4825c3739abb923e487c98cb7c46c5be |
| reports/s2np/qualify_once.py | 6adaebc7dfd0347c04ad2eb740933fc40723090935f0d8c6720ac19d4eecde7a |
| reports/s2np/preseal_once.py | b92238acdac84f4e695a7efa61c791f57f7d89fd49be0e8ffb06e58f72d63e0e |

Die fuenf weiteren Bindungen betreffen den unveraenderten Plan, den reinen
Generator, die vorhandenen kanonischen/Identitaetshelfer sowie die nur als
Dateien gebundenen Rezeptor-/NJ-Module. Alle zehn Hashes stehen vollstaendig
im Ergebnis. Keine pauschale Freigabe anderer Dateien oder Ausfuehrungen.

Die Qualifikation bestaetigt technische Quellen-/Planbindung, nicht
Rezeptornormalform, spektrale Trennung, Erhaltung oder Abrufnutzen.
Das bestandene Ergebnis erfuellte die vom Benutzer gebundene Voraussetzung
fuer die anschliessende **einmalige rezeptorfreie** Vorversiegelung.
