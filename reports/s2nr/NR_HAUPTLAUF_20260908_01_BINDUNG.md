# S2-NR: freigegebener einmaliger Hauptlauf

Lauf-ID: `s2nr-mask-runtime-transfer-20260908-01`.
Ausgangscommit: `57c93b95`. Das gebundene Ergebnisverzeichnis
`reports/s2nr/s2nr-mask-runtime-transfer-20260908-01` existiert vor dem Aufruf nicht.
Diese Datei dokumentiert die Benutzerfreigabe, keine weitere Qualifikation.

Genau ein Aufruf von `tools._s2nr_private_run.run_main_once`, unveraenderte
qualifizierte Quellen. Nur das prozesslokale `MAIN_GATE` des Einmaleinstiegs
wird fuer diesen Aufruf geoeffnet; alle beteiligten Hauptgates werden im
abschliessenden `finally` auf `False` gesetzt. Kein Retry.

Vor Materialisierung prueft der Haupteinstieg den vollstaendigen
Qualifikationsverbund und den neuen Anschlussbeleg sowie die unveraenderte
Quellenversiegelung, Generator-, Umgebungs-, Profil- und Codebindungen.
Keine zusaetzlichen Tests, Rezeptorvorlaeufe oder Payloadgenerierungen.

- Gemeinsame Materialisierung: 18 Audiofenster, 180 Hops, 171 rollende
  Abschluesse, 18 einmalige NJ-Endpunktprojektionen und 14 visuelle Analysen.
- Zwei feste Masken, getrennte frische Runtimeinstanzen und Owner.
- Je Arm 18 Ereignisse und 14 Formationen, insgesamt 9792 Feldkontakte
  und 16 Abrufbelege einschliesslich unabhaengiger Direktbaselines.
- Unveraenderte Regeln, Grenzen, Zeitfenster, Masken und endliche Budgets.
- Ein atomarer `recording.json`-Gesamtbeleg, anschliessend genau ein
  `verify_file_once` aus dem unabhaengigen NR-Verifikator.
- Nur bei technisch gueltigem `RECORDING_COMPLETE` genau einmal
  `evaluate_file_once` aus dem getrennten NR-Auswerter.

Gueltige Enthaltungen, unerwartete Supports oder fehlende Zielstabilisierung
sind keine technischen Fehler fuer sich. Auswertung trennt A-/B-Erhaltung,
Gewinne, Verluste, Fehlzulassungen, Mehrdeutigkeit, Rezeptorvariation und
Cue-/Kandidatenabweichung. Fehlende Referenzen bleiben null; D=0 bleibt
ERHALTUNG_NICHT_GEPRUEFT. Keine Hypothesenanwendung.

Technische Fehler werden phasengebunden gesichert, ohne Funktionsinterpretation.
Keine Reparatur oder nachtraegliche Quellen-/Parameteraenderung in diesem Lauf.
Historische Belege, Versiegelung, fremde Aenderungen und Bootstrap bleiben
unveraendert. Die Offline-Pruefung rekonstruiert keine ungespeicherten
Rohspektren aus den gerundeten NJ-Werten.
