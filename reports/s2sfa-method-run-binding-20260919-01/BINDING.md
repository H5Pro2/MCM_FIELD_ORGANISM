# S2-SFA: Statische Laufbindung des Methodenversuchs

**Status:** historischer Bindungsstand — durch die vollständige
Quellenquittungsbindung unter
[`s2sfa-method-final-run-binding-20260919-01`](../s2sfa-method-final-run-binding-20260919-01/BINDING.md)
abgelöst.  
**Umfang:** ausschließlich positionsrobuste Zuordnung zweier Farbmuster im
visuellen Rezeptorraum; Feld und Memory bleiben unberührt.

## Aktive Methodendeckung

Die sieben Einzelkontrollen aus
[`s2sfa-method-qualification-20260919-02`](../s2sfa-method-qualification-20260919-02/REPORT.md)
und die zwei Ergänzungskontrollen aus
[`s2sfa-method-qualification-20260919-03`](../s2sfa-method-qualification-20260919-03/REPORT.md)
sind getrennte Befunde, kein nachträglich behaupteter Neun-Test-Lauf.

Nach `20260919-02` wurde ausschließlich `LinearSFALearner` ergänzt. Die
bestehenden Körper von `fit_linear_sfa`, `FrozenLinearSFA`, der Rohbaseline,
der Rangregel und der Gewinn-/Verlustauswertung wurden dabei nicht geändert.
Die Ergänzung kapselt nur die bestehende reine Fitfunktion und wird durch die
zwei neuen Kontrollen auf Einfrieren und Fehlercode geprüft. Daher bleiben die
sieben früheren Einzelbefunde für diese unveränderten Funktionen anwendbar;
sie wurden gemäß Anweisung nicht wiederholt. Das ist eine quellengebundene
Codeabgrenzung, keine neue Ausführung.

| Rolle | Aktueller SHA-256 |
| --- | --- |
| SFA-Methode | `0fe16352a5a15bc0cc73acde7f71a8bdfe57156c022d2b4f87404e76a333793d` |
| frühere neutrale Suite | `4e03a89ef43f08e05a578b8ed6c2990b03cb134263d10f147c8616b066767e6b` |
| fokussierte Ergänzung | `58b70d5bb43694807237adad8a040891a81be09cb919c5e4fe3de2680b48f802` |
| Plan und Rezeptregeln | `5dbe4e446bab5b4fb26ee342a8920ff4704f28dfb1892113dca8f5959b21960f` |

## Fest gebundener Quellen- und Rollenbestand

Die 32 Frames bleiben ausschließlich als Planrezepte in
[`ARCHITEKTURKLAERUNG_ZEITLICHE_ERFAHRUNGSSPUR.md`](../../docs/ARCHITEKTURKLAERUNG_ZEITLICHE_ERFAHRUNGSSPUR.md#fester-bestand-und-rollen)
gebunden. Ihre Rezeptfolge, RGB-Werte, Rechteckgeometrie, Zeiten, Rollen und
die lineare SFA-Regel dürfen nicht bei einem späteren Lauf verändert werden.
Es wurden keine Frames erzeugt, keine Payloadhashes bestimmt und keine
Rezeptorwerte berechnet.

Geplanter späterer Umfang, nicht gemessene Istwerte:

| Phase | Folgen | Frames | Erlaubte Verwendung |
| --- | --- | ---: | --- |
| Lernen | `L1`, `L2` | 8 | Statistik und sechs Intraepisoden-Übergänge |
| Referenz | `RA`, `RB` | 8 | nur eingefrorene Projektion |
| Prüfung | `QA`, `QB`, `QAB`, `QC` | 16 | nur eingefrorene Projektion und Vergleich |
| Gesamt | alle | 32 | ein Frame gleichzeitig, keine Rohframeablage |

## Vorgesehener, aber noch fehlender Einmaleinstieg

Ein späterer repositorygebundener Einstieg muss als private, dateigebundene
Funktion existieren und genau diese Reihenfolge erzwingen:

1. Ausgabeabwesenheit, Plan-/Codebindung und Autorisierung prüfen.
2. Für jeden Frame nur diesen Frame erzeugen, den Hash vor der Analyse prüfen,
   `LocalChannelGridReceptor.analyze()` genau einmal aufrufen und den Rohframe
   danach freigeben.
3. Nach `L1` und `L2` `LinearSFALearner.freeze()` einmal aufrufen. Ein
   `SFA_TRAINING_DEGENERATE` beendet den Lauf regulär mit Phase,
   verarbeitetem Präfix, Teilbeträgen und ohne Ersatzprojektion,
   Parameterwechsel oder Auswertung.
4. `RA`, `RB`, `QA`, `QB`, `QAB` und `QC` nur durch den eingefrorenen Zustand
   führen; keine weitere Lernzufuhr.
5. Einen atomaren Rohbeleg schließen, genau einmal read-only verifizieren und
   erst dann die getrennte Rang-/Gewinn-/Verlustauswertung ausführen.

Dieser Einmaleinstieg, der serialisierte Rohbeleg, der unabhängige Verifikator
und der getrennte Auswerter wurden inzwischen privat ergänzt und neutral
qualifiziert unter
[`s2sfa-run-connection-qualification-20260919-01`](../s2sfa-run-connection-qualification-20260919-01/REPORT.md).
Die Qualifikation verwendete ausschließlich numerische Neutralbeobachtungen;
sie materialisierte keine Planframes.

## Unabhängige Prüfung und Auswertung

Der spätere Verifikator müsste ausschließlich gespeicherte Rezeptorwerte,
Frame-/Quellenhashes, Segmentgrenzen, den eingefrorenen SFA-Zustand und
Rangscores lesen. Er müsste Lernstatistiken, die projizierten Eigenresiduen,
Roh-/Merkmalsprojektionen sowie alle Scores unabhängig nachrechnen. Er darf
weder Frames erneut erzeugen noch den Rezeptor erneut aufrufen. Die Auswertung
erhält erst nach erfolgreicher Verifikation die Rollen `QA→A`, `QB→B` und
`QAB→A`; `QC` bleibt Diagnose ohne Unbekanntheitsurteil.

## Vorläufige Arbeits- und Beleggrenzen

Die folgenden Werte sind Obergrenzen aus dem gebundenen Plan, keine gemessenen
Laufgrößen:

| Klasse | Obergrenze | Begründung |
| --- | ---: | --- |
| Frames insgesamt | 32 | fester Bestand |
| gleichzeitig gehaltene Rohframes | 1 | `1920 × 1080 × 3 = 6.220.800` Byte |
| kumulative erzeugte Eingangsbytes | 199.065.600 | 32 Rohframes, nicht als Ablage zulässig |
| gespeicherte Rezeptorwerte | 73.728 Byte | `32 × 288 × 8` Binary64-Werte |
| Lernframes / Referenzframes / Prüfframes | 8 / 8 / 16 | feste Rollen |
| SFA-Ausgabegröße | eine Komponente | fest gebunden |

Der aktuelle private Laufanschluss erzwingt ein gemeinsames Ledger für
Record, temporäre Veröffentlichung, Verifikation, Auswertung und Fehlerform.
Die lokalen Obergrenzen sind 2 MiB für Record und temporäre Veröffentlichung
bei einer globalen Evidenzgrenze von 8 MiB. Der zugehörige neutrale
Anschlussnachweis steht in
[s2sfa-global-ledger-connection-qualification-20260919-01](../s2sfa-global-ledger-connection-qualification-20260919-01/REPORT.md).
Der frühere Hinweis auf eine 262.144-Byte-Recordgrenze ist damit für den
aktiven privaten Anschluss überholt; historische Befunde bleiben unverändert.

Dieser historische Bindungsstand enthielt noch keine persistierten
Quellenquittungen. Die spätere private Anschlussversion bindet Framehash,
Rezeptbindung, technische Form, Sequenzposition und Beobachtungsdigest vor
der numerischen Verarbeitung im Record. Sie ist separat qualifiziert unter
[`s2sfa-source-receipt-qualification-20260919-02`](../s2sfa-source-receipt-qualification-20260919-02/REPORT.md).

## Entscheidung

Die Methode, der Ledgeranschluss und die Quellenquittung sind neutral
qualifiziert. Der geplante Quellenbestand bleibt jedoch bis zu einer
separaten ausdrücklichen Einmallaufentscheidung **nicht autorisiert**.
