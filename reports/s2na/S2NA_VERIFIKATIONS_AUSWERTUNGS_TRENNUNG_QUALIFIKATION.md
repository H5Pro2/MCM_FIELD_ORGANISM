# S2-NA: Verifikations-/Auswertungstrennung

## Entscheidung

Die neutrale Qualifikation
`s2na-verification-evaluation-separation-20260906-01` ist bestanden.

Der technische S2-MT-Verifikator akzeptiert nun sowohl eine strukturell
gueltige Hypothese als auch jede der fuenf gueltigen Enthaltungsformen. Die
Vorhersage, ob eine Hypothese erwartet wurde, ist aus dem technischen
Ereignispfad entfernt. Erst `_expected_evaluation` entscheidet weiterhin
unveraendert zwischen `S2MT_TRANSFER_STREAM_CONFIRMED` und
`S2MT_FUNCTION_FALSIFIED`.

Lauf 04 bleibt unveraendert `NOT_EVALUABLE` und wurde weder erneut
verifiziert noch fachlich umgedeutet.

## Korrekturgrenze

Geaendert wurde ausschliesslich der private S2-MT-Verifikator:

- `CONTEXT_CANDIDATE_AVAILABLE` verlangt eine strukturell gueltige
  Hypothese der zum Cue passenden Modalitaet;
- `ABSTAIN_INTERNAL_AMBIGUITY`, `ABSTAIN_INTERNAL_CONFLICT`,
  `ABSTAIN_AMBIGUOUS_CONTEXT`, `ABSTAIN_NO_CONTEXT` und
  `ABSTAIN_NO_APPLICABLE_CONTEXT` verlangen die Abwesenheit einer
  Hypothese;
- `NOT_REQUESTED`, `SCAN_FAILED` und widerspruechliche Kombinationen sind
  im Cue-Pfad unzulaessig;
- der Memoryzustandsdigest muss fuer jeden Cue gegen den unmittelbaren
  Vorzustand unveraendert bleiben;
- Hypothesenmodalitaet, Hypothesendigest, Bereich, Maskenform und
  Wertdimension werden weiterhin technisch geprueft;
- die vorhandene funktionale Auswertung blieb unveraendert.

Quellenplan, Runtime, Memory, Rezeptoren, Schwellen, Ereignisfolge und
Runner wurden nicht geaendert.

## Vor- und Nachbindung

Vor und nach dem einzigen Testaufruf galten:

- S2-MT-Verifikator-SHA-256
  `f8b6a17efc0f580ca7f6ea741137b472255b1f4974d4ed5050f12a3f240ea0de`;
- S2-MT-Runner-SHA-256
  `29f3ef7fa28bfde45236b3cce39febe542f4ab6470a3c0f9b8de7aac7549dcfd`;
- Test-SHA-256
  `a89662d1d1eb5adf0cf6c0dac2d7d80aa19d49de5f64592ac58c88eb1956f0a1`;
- Hauptgate `False`.

Der historische Lauf-04-Beleg blieb bytegleich:

- Dateigroesse `149416` Byte;
- SHA-256
  `a5c16ef89e7059cd358f82fc25422607b5405572d21a86b18b4f80c90d3e11c5`.

## Einziger Qualifikationsaufruf

Aus dem Workspace-Root wurde genau einmal ausgefuehrt:

```text
python -m unittest tests.test_s2na_transfer_verification_evaluation_separation -v
```

Das Ergebnis lautete:

```text
Ran 3 tests in 0.001s
OK
```

Der Prozess endete mit Exit-Code `0`. Es gab keinen Retry.

## Qualifizierte Trennung

Der neutrale Gegenfall band eine fachlich erwartete Hypothese, aber eine
beobachtete gueltige Enthaltung. Die technische Hypothesen-/Statuspruefung
akzeptierte diesen Beleg. Die getrennte unveraenderte Auswertung meldete
daraufhin korrekt `S2MT_FUNCTION_FALSIFIED`.

Zusaetzlich wurden beide gueltigen Hypothesenmodalitaeten, alle fuenf
Enthaltungen sowie isolierte Widersprueche bei Status, Modalitaet und Digest
geprueft. Alle ungueltigen Kombinationen stoppten fail-closed.

Damit ist die bekannte Verifikatorgrenze aus Lauf 04 fuer einen kuenftigen,
separat freizugebenden Transferlauf geschlossen. Es wurde kein Hauptlauf,
keine Memoryformation und keine Runtimeausfuehrung gestartet.
