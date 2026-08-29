# Technischer Befund: zweite Retention-Runnerqualifikation

## Status

`QUALIFICATION_VALID`

Die neu freigegebene Qualifikation wurde mit der Lauf-ID
`retention-runner-qualification-20260829-02` genau einmal ausgefuehrt:

```text
python -m unittest -v tests.test_retention_capacity_runner_qualification
```

Ergebnis: `8/8`, Exit-Code 0, terminal `OK`. Es gab keine Korrektur,
Wiederholung oder Teilfortsetzung. Der vollstaendige, ausschliesslich auf
LF-Zeilenenden normalisierte Output liegt in `unittest-output.txt`;
`run-metadata.json` bindet Exit-Code und Quelldigests.

## Qualifizierter technischer Umfang

Die unveraenderten acht Tests bestaetigten:

- den geschlossenen Hauptschalter und die unveraenderten Hauptbudgets
  `146/170/16/316/1296`;
- je einen kleinen echten, frischen B4- und TSPM-1-Zustandsweg ohne Nutzung
  der Hauptgeschichten;
- getrennte Fast-, auditive Slow- und visuelle Slow-Zustaende;
- nachweislich unveraenderliche B4- und TSPM-1-read-only Proben;
- Ereignisreihenfolge, Digestverkettung und Start-/Result-Bindungen;
- Ausschluss von Labeln und Sollbefunden aus dem Speicherinput;
- fail-closed Verhalten bei unvollstaendigem Abschluss und Verzeichnisreuse;
- eine vollstaendige neutrale Aufzeichnung mit den weiterhin festen 1296
  Ereignissen sowie erfolgreiche read-only Verifikation;
- Erkennung manipulierter Ergebnisse und fehlender Abschlussdateien.

## Abgrenzung

Der erste Lauf `retention-runner-qualification-20260829-01` bleibt dauerhaft
`QUALIFICATION_FAILED`. Die zweite Qualifikation ersetzt oder repariert ihn
nicht; sie prueft denselben unveraenderten Testsatz nach der separat
versionierten Zwei-Stellen-Pfadkorrektur.

Der Befund qualifiziert ausschliesslich Runner, Recorder und Verifikator fuer
eine spaetere gesondert freizugebende Hauptausfuehrung. Er ist kein Befund zu
Erhaltung, Verdichtung, Vergessen, Folgenordnung oder einer Memory-Funktion.
Die Hauptgeschichten und der `146/170/16`-Lauf wurden nicht ausgefuehrt.
`MAIN_EXECUTION_ENABLED` bleibt `False`; Bootstrap-Datei, API, Snapshot und
Feldpfad blieben unberuehrt.
