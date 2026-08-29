# Technischer Befund: Retention-Runnerqualifikation

## Status

`QUALIFICATION_FAILED`

Die einmalig freigegebene Testausfuehrung wurde genau einmal mit

```text
python -m unittest -v tests.test_retention_capacity_runner_qualification
```

gestartet. Ergebnis: acht Tests, sechs bestanden, zwei technische Fehler,
keine fehlgeschlagene Assertion, Exit-Code 1. Der vollstaendige, ausschliesslich
auf LF-Zeilenenden normalisierte Output liegt in `unittest-output.txt`;
`run-metadata.json` bindet Laufumfang, Exit-Code und SHA-256-Digests.

## Bestandene Teilpruefungen

Die Tests 01 bis 06 bestaetigten innerhalb dieses Qualifikationslaufs:

- `MAIN_EXECUTION_ENABLED` blieb `False` und der Hauptumfang blieb exakt
  `146/170/16/316/1296`;
- ein kleiner echter B4-Weg begann frisch und schrieb genau einen FIFO-Eintrag;
- ein kleiner echter TSPM-1-Weg begann frisch, trennte Fast von auditivem und
  visuellem Slow-Zustand und erzeugte nach zwei passenden Expositionen je einen
  Slow-Support von 1;
- B4- und TSPM-1-Proben blieben nachweislich read-only;
- Start-/Result-Reihenfolge, Digestkette und Ereignisbindungen waren im
  neutralen In-Memory-Belegweg konsistent;
- Versuchslabel und erwartete Befunde wurden nicht als Speicherinput verwendet.

Diese Teilbefunde qualifizieren den Gesamtweg nicht, weil der Lauf insgesamt
nicht bestanden ist.

## Blocker

Die Tests 07 und 08 stoppten beide vor der ersten offiziellen Recorderanlage
an derselben Grenze:

```text
RetentionRecordingError: exact output root and recording plan required
```

`PrivateEvidenceRecorder.__init__` prueft derzeit
`type(output_root) is Path`. Auf Windows liefert `Path(...)` jedoch ein
`WindowsPath`-Objekt. Dadurch weist der Recorder einen regulaeren lokalen
Pfad bereits vor Journalanlage fail-closed ab. Die beabsichtigten Pruefungen
von unvollstaendigem Abschluss, Wiederverwendung, vollstaendiger 1296er
Aufzeichnung, Manipulation und fehlenden Dateien wurden deshalb nicht erreicht.

## Grenze

Es erfolgte keine Korrektur und keine Wiederholung. Die Hauptgeschichten
U/V/C/A/S1/S2 wurden nicht verwendet. Der `146/170/16`-Hauptlauf blieb
gesperrt; B4, TSPM-1, PPB-1, Runner, Recorder, Verifikator, API, Snapshot und
Feldpfad wurden im Qualifikationsschritt nicht geaendert. Die unversionierte
Bootstrap-Datei blieb ausgeschlossen.

Der naechste technische Schritt benoetigt eine gesonderte enge Freigabe fuer
die plattformkorrekte Pfadtyppruefung im Recorder. Erst danach kann eine neue,
ausdruecklich freigegebene Runnerqualifikation mit neuer Laufidentitaet
stattfinden. Der aktuelle Lauf wird nicht fortgesetzt oder umgedeutet.
