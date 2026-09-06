# S2-NG: lokale Fehlerabbildung und Neuqualifikation bestanden

- Qualifikations-ID: `s2ng-private-runtime-composition-qualification-20260906-02`
- Status: `S2NG_COMPOSITION_QUALIFIED`
- Genau ein vollstaendiger neutraler Testaufruf: **23/23**, Exit-Code `0`, `OK`.
- Keine Wiederholung, S2-MT-Quellenmaterialisierung oder Hauptgeschichte.
- `MAIN_GATE = False`; der reale Vergleich bleibt separat freizugeben.

## Exakte Korrektur

Unmittelbar um die bestehende Zustandsrekonstruktion mittels
`old.decode_state(...)` liegt nun ein einzelner spezifischer Handler:

```python
except run.memory.S2JWCoordinatorError as error:
    raise run.S2NGError("STATE_BINDING_INVALID") from error
```

Keine Aufnahme von `RuntimeError` oder beliebigen Exceptions. Die bestehende
NG-Fehlerweitergabe bleibt unveraendert. Memoryvalidator, Akzeptanzbedingungen,
historische Komponenten, Kompositionsadapter, Auswerter, Regeln, Schwellen
und Ressourcenlimits wurden nicht geaendert.

Die bisherigen 22 Testkoerper bleiben unveraendert. Neben der neuen
Qualifikations-ID kam genau eine Regression hinzu. Sie bestaetigt:

- Ein gueltiger Gesamtbeleg mit gueltigen Zustaenden bleibt verifizierbar.
- Ein manipulierter Zustand wird als `STATE_BINDING_INVALID` abgewiesen.
- `__cause__` ist exakt ein `S2JWCoordinatorError`, mit Code
  `S2JW_PRESTATE_INVALID` und unveraendertem Text
  `S2JW_PRESTATE_INVALID: composite state relation differs`.
- Die explizite Exception-Verkettung bleibt bis zum Aufrufer erhalten.
- Ein bereits vorhandener NG-Fehler bleibt `DIGEST_INVALID` ohne neue Ursache.

## Umfang und Aussagegrenze

Der bisherige neutrale Gesamtumfang bestand einschliesslich Instanzisolation,
Eingabeidentitaet, historischer Arithmetik, unveraendertem Slow-/Visualpfad,
vollstaendigen Scans, Read-only-Hinweisen, Lifecycle und getrennten
Auswertungszaehlern. Auditives `D=0` wird nicht durch visuelle Treffer gefuellt.

Die normale Vier-Ereignis-Fixture pro Arm lieferte `RECORDING_COMPLETE`,
zwoelf Scanbelege, gleiche Feld-/Memory-Geschwisterzustaende und
Baselinegleichheit. Der getrennte neutrale Scanfehlerfall endete absichtlich
`NOT_EVALUABLE`; seine Feldkontakte blieben bestehen. Insgesamt vier neutrale
Formationen und 2.208 Feldkontakte. Keine Rohquellenerzeugung oder Rezeptoranalyse.

Der normale Gesamtbeleg umfasst 242.452 Byte. Maxima seiner Teilbelege:
Eingabe 5.377, Schrittpaar 11.215, Scan 14.643 und Memoryzustand 8.118 Byte.
Alle vorab gebundenen Grenzen bleiben unveraendert. Die zusaetzliche Regression
erhoeht nur die vorab gebundene Anzahl lesender Gesamtpruefungen von 11 auf 14,
nicht Formation, Scan- oder Hauptlaufbudgets.

Das Bestehen qualifiziert die private Vergleichskomposition. Es ist kein
S2-MT-Transferbefund, keine Produktumstellung und kein Nachweis allgemeiner
Erhaltung durch die strengere Regel.

## Aufruf und Bindungen

Caller: `C:/Python314/python.exe -B -m reports.s2ng.qualify_state_binding_once`.
Daraus genau einmal:

```text
C:\Python314\python.exe -m unittest tests.test_s2ng_private_runtime_comparison -v
```

`preregistration.json` bindet vor dem Test alle 23 Test-IDs, Kommando,
Interpreter, Quellen und Grenzen. Der statische Check bestaetigt den lokalen
spezifischen Handler samt Exception-Verkettung und das geschlossene Gate.
`result.json` enthaelt identische Vor-/Nachherhashes aller gebundenen Dateien,
einschliesslich der alten Fehlqualifikation und historischen Komponenten.

| Datei | SHA-256 vor und nach dem Aufruf |
| --- | --- |
| tools/_s2ng_private_comparison_verification.py | 9a7f401849915773f9f054b744236c70c29c83ce419aa3117462261e5dbf7c74 |
| tests/test_s2ng_private_runtime_comparison.py | 29d207ce70bfb03a05361ca1f48da98949a230e3f12211c4263835b2f26216fd |
| tools/_s2ng_private_runtime_comparison.py | 9d62d307a90a94f375d15642612b6538c6370bf345cb22c0e87a68e24016f9d3 |
| tools/_s2ng_private_comparison_evaluation.py | 12cbe8bc0f0feddfc6883239d1f8818609509984c875f36a47cd9dcc40d010ae |

Ergebnisdigest:
`29bb988c8d7068e0a16389b250f4f3f8c9f3ec85de51247d2b6ff14217bd715c`.
Normaler Belegdigest:
`d675bec3e459cba7877c0bdc13f8859593633ca34bb22824d92010a2d08b32e9`.
Normale Verifikation:
`191937a3fcfd831dc0daaad0fa4406f27717b2933b4600500116d39203f6f7d6`.

Protokolle, normaler Beleg, separate Verifikation, neutrale Auswertung und
Scanfehlerbeleg liegen unveraendert im selben Verzeichnis. Die alte
Qualifikation `...-01` bleibt dauerhaft `NOT_QUALIFIED` (21/22).
Fremde Aenderungen und Bootstrap bleiben ausgeschlossen.

RUECKMELDUNG ERFORDERLICH: Analystenpruefung und separate Freigabe des
einmaligen realen Vergleichs. Keine weitere technische Ausfuehrung erfolgt
aus diesem Qualifikationsbefund automatisch.

WEITER: Am besten geht es jetzt mit der Analystenpruefung dieser bestandenen
Neuqualifikation und der Entscheidung ueber den begrenzten Runtimevergleich weiter.
