# TSPM-1: Implementierungs- und Testbefund

Stand: 28.08.2026. Umfang: drei freigegebene Quelldateien und genau acht
fokussierte Tests. Keine H1-H7-Vergleichszelle, keine Matrixausfuehrung.

## Umsetzung

- Im privaten Vergleichsmodul ist die funktionale Aggregation von der alten
  `_S2EFAttempt`-Abnahme getrennt. Der alte Einstieg bleibt unveraendert gesperrt.
- Der private lokale Runner bildet spaeter die bestehenden Zellen ueber ihre
  echten Owner und Operatoren. Er bindet Quellen, Registry, Start, Owner,
  Ergebnisse und Kosten; seine eigene 56-Zellen-Sperre bleibt ebenfalls geschlossen.
- Dateiablage und lesende Ergebnispruefung unterscheiden vollstaendigen Abschluss
  von fehlenden, beschaedigten oder widerspruechlichen Aufzeichnungen. Kein
  alter Publisher, kein Ersatzattest und keine geschlossene Plattformfunktion
  wurden verwendet. Gleichwertige Funktionsprofile erhalten eine gesonderte
  Engineeringrangfolge nach Schreibarbeit, Speicherbedarf und Ebenenzahl.

Die geprueften Dateien sind
[`_tspm1_s2dr_private_comparison.py`](../../../mcm_field_organism/_tspm1_s2dr_private_comparison.py),
[`_tspm1_functional_study.py`](../../../tools/_tspm1_functional_study.py) und
[`test_tspm1_functional_study.py`](../../../tests/test_tspm1_functional_study.py).
TSPM-1-Grundkern, PPB-1, Parameter, Fixtures, Baselineoperatoren, API,
Snapshot und Feldpfad wurden nicht geaendert.

## Einmaliger Testlauf

Aufruf: `python -B -m tests.test_tspm1_functional_study --record-dir reports/tspm1_functional/qualification-20260828-01`

**8/8 bestanden; Exit-Code 0; terminales OK; 4.872 Sekunden Testsuite.**
Keine Wiederholung. Keine Fehler oder Fehlschlaege der Testsuite.
Erwartete Negativfaelle sind als solche in den Einzelbelegen enthalten.

| Test | Gepruefter Umfang | Ergebnis |
| --- | --- | --- |
| 01 | Zwei echte kleine TSPM-1-Bildungen vor Probe; Zustandskette und Ergebnisablage | PASS |
| 02 | Frischer Anfangszustand, isolierte Wiederaufnahme und unveraenderlicher read-only Abruf | PASS |
| 03 | Neutrale Sollbewertung und einfachere Loesung bei gleichem funktionalem Profil | PASS |
| 04 | Kleine R0-Projektions-Datentraeger: abweichende Bank-, Konfigurations-, Slot- und Beobachtungsidentitaet | PASS |
| 05 | Relationaler Kostenvalidator: 234 Terme akzeptiert, 242 einschliesslich Validierungsarbeit abgewiesen | PASS |
| 06 | Fehlender Abschluss, beschaedigte Datei und eingespeister Flushfehler nicht auswertbar | PASS |
| 07 | Einmalverbrauch, protokollierter Producerfehler und keine Wiederaufnahme | PASS |
| 08 | Beide Einstiegssperren, Plattformisolation sowie unveraenderte bestehende Operatoren und Konstanten | PASS |

Der Budgettest verwendet Registry-Metadaten und synthetische Kostenbelege,
keine ausgefuehrte H1-Zelle und keine gemessenen Modellkosten. Der R0-Test
prueft die Projektionsabnahme, nicht die funktionale Gleichheit aller Geschichten.
Alle acht Tests protokollieren jeweils null Aufrufe der registrierten
Zellowner sowie der drei H1-H7-Initialisierungs-/Bildungs-/Probe-Einstiege.
Die direkten TSPM-1-Aufrufe betreffen ausschliesslich die kleinen Testsequenzen.

## Ergebnisdateien

- [Vollstaendiges Testprotokoll](output.txt)
- [Alle acht Einzelbefunde und Fehlerbelege](result.json)
- [23 gebundene Quelldateien mit Quellbytes sowie Runtime-/Abhaengigkeitsangaben](sources.json)

Die Ergebnisdatei wurde temporaer geschrieben, dateibezogen geflusht und
atomar veroeffentlicht. Anschliessend wurden beide JSON-Siegel, die
Transkriptbindung, alle acht Testeintraege und die 23 aktuellen Quellhashes
mit einem separaten rein lesenden Standardbibliotheksabgleich kontrolliert.
Die Quellbytes blieben seit der Erhebung unveraendert; keine weitere Testausfuehrung.

SHA-256 von `result.json`:
`f14a97a53e5d9751555e95fb17f4a6934c24dc045b8651cf4483fc0ca3f5bab6`

SHA-256 von `output.txt`:
`abee576432b0a8e49f1d67e487af18a1fa021f32f69b6a11657e5e7e8c2505ad`

## Verbleibende Grenze

Im freigegebenen Acht-Test-Umfang ist kein methodischer Widerspruch aufgetreten.
Die vollstaendige Kombination aus 56 echten Zellen, deren Kosten und gemeinsamer
Auswertung ist weiterhin nicht ausgefuehrt oder funktional abgenommen. Die
Miniaturtests ersetzen diesen Vergleich nicht. Auch umfassende Regressionen
und Produktionsgarantien werden aus diesen acht Tests nicht abgeleitet.

Der naechste konkrete Schritt ist die separate Freigabe genau eines
56-Zellen-Funktionsversuchs nach dem dokumentierten, verhaeltnismaessigen Plan.
Nur dafuer waere die neue private Ausfuehrungssperre gezielt zu oeffnen;
S2-FC, der alte Einstieg und der geschlossene Plattformpfad bleiben gesperrt.
Eine weitere allgemeine Vertragsaudit-Kaskade ist nicht vorgesehen.

Die 26 AV-Traegerwerte variieren weiterhin nur in zwei unabhaengigen Werten.
Dieser Testbefund bewertet daher keine reichhaltige Wahrnehmungsrepraesentation.
Nach dem Speichervergleich bleibt gezielt zu entscheiden, welche abgestuften
Merkmale, raeumlichen Beziehungen oder zeitlichen Uebergaenge erhalten werden sollen.

Keine Commits oder Pushes in diesem Arbeitsschritt.
