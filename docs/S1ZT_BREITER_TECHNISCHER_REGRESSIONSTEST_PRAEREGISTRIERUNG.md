# S1-ZT: Praeregistrierung des breiten technischen Regressionstests

## Zweck

S1-ZT prueft nach dem geschlossenen W1-F-EOL-Rest genau einmal den breiten
technischen Testbestand. Der Lauf soll weitere unabhaengige Fehler sichtbar
machen. Er ist kein Forschungs- oder Feldlauf.

## Gebundener Aufruf

```text
Arbeitsverzeichnis: Repositorywurzel
PYTHONDONTWRITEBYTECODE=1
python -m unittest discover -s tests -p test_*.py
Fail-Fast: nein
Wiederholung im selben Schritt: nein
```

Der Preflight zaehlt 914 passende Testmodule. In den Tests gibt es keinen
direkten `sync_playwright`-Aufruf. Browserrollen verwenden injizierte Fakes
oder stoppen vor der Factory. Ein installiertes Browserbinary und reale
Audio-/Videoquellen bleiben ausgeschlossen.

Synthetische Unit- und Integrationstests duerfen bestehende Feldfunktionen im
Testzustand aufrufen. Nicht zulaessig sind reale oder registrierte Feldlaeufe,
Produktionsausfuehrungen und neue Ergebnisdateien im Repository.

## Entscheidungsregel

- Bei vollstaendigem Bestehen wird nur der technische Regressionsteststatus
  dokumentiert.
- Bei Fehlern werden alle vom einmaligen Lauf gemeldeten Fehler nach
  Erstursache und Projektbereich klassifiziert.
- Im selben Schritt wird kein Fehler repariert und kein Test wiederholt.
- Ein Fehler ist kein Forschungsbefund und darf geschlossene Kandidaten nicht
  reaktivieren.

Maschinenlesbare Praeregistrierung:
[S1ZT_BREITER_TECHNISCHER_REGRESSIONSTEST_PRAEREGISTRIERUNG_V1.json](S1ZT_BREITER_TECHNISCHER_REGRESSIONSTEST_PRAEREGISTRIERUNG_V1.json).

