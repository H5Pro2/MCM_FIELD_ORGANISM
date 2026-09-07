# S2-NM: gebundene Subnormal-Konfliktpruefung

Einmalige neutrale Qualifikation: `s2nm-subnormal-a-conflict-qualification-20260907-01`.
Kein Hauptlauf, keine Produktkorrektur und keine Wiederholung der 29 S2-NL-Tests.

## Inventar und Eingaben

Genau drei Testkoerper in `tests/test_s2nm_subnormal_a_conflict.py`:

1. `test_01_smallest_subnormal_zero`: `(s, 0)`.
2. `test_02_three_four_subnormal`: `(3*s, 4*s)`.
3. `test_03_normal_boundary`: `(m, nextafter(m, 0))`.

`s` ist das kleinste positive Binary64-Subnormal, `m` das kleinste
positive normale Binary64. Ausschliesslich die in S2-NL gebundenen Hexwerte
werden uebernommen; Abgleich mit den historischen `subnormal.0..2`-Belegen.
Keine neuen Zahlenpaare, Quellen oder Suchfaelle. Positionen 0..46 sind null,
die unterschiedliche Position ist 47. Die unveraenderte NJ-Projektion halbiert
jedes der sechs synthetischen Ausgangsvektorexemplare genau einmal.

Je Paar ein neutraler B4-Kandidat und ein neutraler Fast-Kandidat, jeweils
Support/Generation 1, restliche Slots frei und beide Slow-Banken leer.
Explizite synthetische Datentypfixtures, kein Anspruch einer realen
Formationsgeschichte. Altes und neues Configdigest muessen S2-NL entsprechen.
Audiozustand endet bei 4800; Cuefenster [4800,9600] derselben nativen
`audio.sample`-Uhr schreitet fort. Cuewerte 0..23 sind null; 24..47 unbekannt.
Die technischen Cue-Quelldigests bezeichnen neutrale Belege, keine erzeugten PCM.

## Umfang und Budgets

- 3 Paare x 2 Profile x 2 Regeln = 12 Primaerentscheidungen.
- Dazu 12 unabhaengige Direktbaselineentscheidungen, insgesamt 24 Abrufbelege.
- Historisches `sum(...)/24` und `ALL_BANDS_24`; Slow unveraendert.
- Jeder Arm scannt vollstaendig 9/3/8 Slots, maximal 528 Wertvergleiche.
- In dieser Belegung 48 beobachtete Differenzen plus 48 interne
  Gleichheitspositionen je Arm: 2304 budgetierte Wertvergleiche insgesamt.
  Die lesende Belegverifikation ist gesondert und kein erneuter Abruf.
- Je Abrufbeleg strikt weniger als 32768 Byte, Gesamt-JSON maximal 1048576 Byte.
- Ein Testaufruf, maximal 120 Sekunden, failfast, kein Retry.
- Null Formationen, PPB-Updates, Rezeptoranalysen, PCM-Generierungen,
  Feld-, Runtime- oder NH-Aufrufe. Keine Hypothesenanwendung.

## Getrennte Ergebnisse

Vollvektorgleichheit und Wertedigests, beide Banktreffer, A-Aufloesung und
endgueltige Hypothese/Enthaltung werden getrennt aufgezeichnet. Technische
Qualifikation verlangt vollstaendige Scans, Baselinegleichheit, read-only
Zustaende und gueltige Belege. Die aus dem bekannten Gleichheitsverlust
abgeleitete Kontrollprognose ist Konflikt im Altprofil und A-Zulassung im
Halbprofil. Ihr Eintreten ist eine **semantische Abweichung**, keine Erhaltung.
Es wird weder numerische Toleranz noch eine Ersatzdarstellung eingefuehrt.

Der Qualifikationsaufruf bindet vor Testbeginn Inventar, Interpreter,
Quellhashes und historische Paarbelege. Danach werden dieselben Hashes und
die geschlossenen NG-/NH-/NL-Gates lesend kontrolliert. Bei Fehlern Stopp.
Kein universeller Gleitkommabeweis und keine Integrationsfreigabe.
