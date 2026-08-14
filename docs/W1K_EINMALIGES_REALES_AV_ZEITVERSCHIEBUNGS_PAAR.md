# W1-K: Einmaliges reales AV-Zeitverschiebungs-Paar

Stand: 2026-08-07

Entscheidung: `W1K_REAL_TIMING_PAIR_REJECTED_INPUT_INVARIANT`

Forschungslauf: nein

Laufnummer: keine

Reale Paarausfuehrungen: genau eine

Automatische Wiederholung: nein

## Auftrag

W1-K bindet das in W1-J implementierte A0/C0-Paar an die bereits in W1-H
bestaetigte lokale Playwright-/Chromium-Runtime und fuehrt es genau einmal
als technischen Realpaar-Smoke aus.

Der Lauf darf nur einen positiven Receipt liefern, wenn beide Arme ihre
Payload-, Rezeptor-, Energie-, Feld- und Lifecycle-Invarianten vollstaendig
erfuellen.

## Einmalwerkzeug

`tools/run_browser_payload_timing_pair.py`:

- bindet die lokale Playwright-1.62.0-/Chromium-151-Runtime;
- verwendet ausschliesslich die kontrollierten lokalen W1-Assets;
- uebergibt `sync_playwright` ausdruecklich an den W1-J-Paarlauf;
- ruft den Paarlauf genau einmal auf;
- enthaelt keine Schleife und keine Wiederholungslogik;
- gibt nur bei einem gueltigen Paar eine sortierte skalare ASCII-JSON-
  Projektion aus;
- schreibt keine Report-, Payload- oder Forschungslaufdatei.

Der direkte Werkzeugeinstieg wurde vor dem realen Start ausserhalb des
Workspace importiert, ohne `main()` und ohne Browserstart auszufuehren.

## Statische Vorpruefung

Vor der realen Ausfuehrung bestanden:

```text
playwright:               1.62.0
chromium:                 151.0.7922.34
browser_revision:         1234
browser_started:          false
fokussierte Tests:        19 passed
```

Runtime-, Manifest-, Requirements-, Binary- und Assetbindung blieben auf dem
in W1-F bis W1-J dokumentierten Stand.

## Reales Ergebnis

Das Werkzeug startete genau ein A0/C0-Paar. Beide Arme erreichten den
Paar-Comparator. Dort wurde das Paar verworfen:

```text
BrowserPayloadTimingPairError:
timing pair input invariants failed
```

Es entstand kein positiver `BrowserPayloadTimingPairReceipt` und keine JSON-
Ergebnisausgabe. Deshalb duerfen aus diesem Paar weder Feldabstand noch
Zeitkopplungswirkung abgeleitet werden.

Die zum Ausfuehrungszeitpunkt vorhandene Fehlermeldung fasste alle
Eingangsinvarianten zusammen. Sie serialisierte die intern bereits
berechneten Einzelwerte nicht und benennt rueckwirkend nicht eindeutig, ob
die Abweichung aus visueller Sequenzgleichheit, Audioenergie oder einer
anderen Paarinvariante stammt. Eine Festlegung auf Audioenergie waere daher
nur eine Vermutung und ist kein Befund.

## Nachtraegliche Diagnosehaertung

Nach dem beendeten Einmalpaar wurde der Comparator ohne reale Wiederholung so
gehaertet, dass ein zukuenftiger Fehler eine oder mehrere technische Rollen
nennt:

```text
visual_sequence
audio_total_energy
auditory_inventory
visual_inventory
event_inventory
afterimage_inactive
```

Die Energieabweichungs-Fake-Abnahme bestaetigt nun explizit
`audio_total_energy` als Diagnose. Der fokussierte Verbund besteht nach der
Aenderung weiterhin mit `19 passed`.

Diese Haertung lokalisiert das bereits beendete W1-K-Paar nicht rueckwirkend.
Sie rechtfertigt insbesondere keine zweite reale Ausfuehrung unter derselben
W1-K-Entscheidung.

## Prozess- und Dateinachzustand

Nach dem Abbruch:

```text
W1-Headless-Browserprozess:      keiner
neue Reportdatei:               nein
Rohpayloaddatei:                nein
Forschungslaufdatei:            nein
Lauf-197-Artefakte:             weiterhin nicht vorhanden
```

Die beiden Arm-Lifecycles liegen vor dem Paar-Comparator. Der Fehler trat
erst beim Erzeugen des Paar-Receipts auf; alle Browserressourcen waren zu
diesem Zeitpunkt bereits geschlossen.

## Aussagegrenze

W1-K belegt:

- das Realpaar kann bis zum Invariantenvergleich ausgefuehrt werden;
- die vorab gebundene Kontrolle hat eine Abweichung erkannt und das Paar
  korrekt nicht als positives Ergebnis ausgegeben;
- Prozess- und Dateigrenzen wurden eingehalten.

W1-K belegt nicht:

- welche einzelne Eingangsinvariante real abwich;
- eine reale Feldwirkung der Zeitverschiebung;
- Wahrnehmung, Nachhall, Feldzeit, Praegung, Memory, Organisation, Semantik,
  Selbstregulation oder KI.

## W1-K-Entscheidung

```text
Einmalwerkzeug:                  implementiert
statische Vorpruefung:           bestanden
reale Paarausfuehrung:           genau eine
positive Paarabnahme:            nein
Abbruchgrund:                    Eingangsinvariante, nicht einzeln lokalisiert
automatische Wiederholung:       nein
Prozessschluss:                  bestanden
Artefaktfreiheit:                bestanden
Forschungslauf:                  nein
```

## Bester naechster Schritt

W1-L untersucht statisch und unter Fakes die moeglichen realen
Invariantenabweichungen. Schwerpunkt sind Web-Audio-Grenzsample,
Float64-Energiesummierung, zeitverschobene Oszillatorphase und die exakte
visuelle Sequenzprojektion. W1-L darf keinen realen Browser starten und W1-K
nicht wiederholen. Erst ein vorab dokumentierter Ursachenbefund kann einen
neuen, separat benannten Realpaar-Smoke begruenden.
