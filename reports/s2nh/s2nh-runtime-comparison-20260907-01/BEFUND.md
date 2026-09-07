# S2-NH: einmaliger Runtimevergleich technisch abgebrochen

Lauf-ID: `s2nh-runtime-comparison-20260907-01`.
Quellenstand: `cd8d4efd65d691ac2ed2d71f94362b99d2a74e86`.
Status: **NOT_EVALUABLE**. Kein NH-Funktions- oder Erhaltungsbefund.

## Ausfuehrung und Stopp

Genau ein Aufruf aus dem Workspace:

```text
C:/Python314/python.exe -B -m reports.s2nh.run_runtime_comparison_once
```

Der archivierte Einmalaufrufer delegierte genau einmal an den unveraenderten
`run_main_once`. Neue ID und vorher nicht vorhandenes Ergebnisverzeichnis;
keine vorgeschaltete Rezeptormessreihe oder weitere Tests. Prozess-Exit-Code
1. Danach genau eine unabhaengige read-only Verifikation, keine Auswertung.

Der atomare Beleg lokalisiert den Abbruch:

| Bindung | Beobachtet |
| --- | --- |
| Technische Phase | `RECEPTOR_ANALYSIS` |
| Ereignisordinal | 2 (`e02`) |
| Quellen-ID | `nh-a01` |
| Ausnahmeklasse | `ReceptorContractError` |
| Gespeicherter Fehlercode | `NH_TECHNICAL_ERROR` |
| Materialisierungsaufrufe | 1 |
| Abgeschlossene Ereignismaterialisate | 1 |
| Verarbeitete Audiofenster | 2 |
| Audiohops | 20 |
| Rollende Audioabschluesse | 11 |
| Visuelle Analysen | 1 |

Die Zaehler bedeuten nicht, dass das zweite Audioereignis gueltig gebunden
werden konnte. Die Phase umfasst im qualifizierten Materialisierer auch
die Uebernahme des Audiorezeptorzustands in den Rezeptorkontaktvertrag.
Der Beleg enthaelt keinen konkreten verletzten Wertebereich oder Bandindex;
eine bestimmte numerische Ursache wird deshalb hier nicht behauptet.
Keine erneute Analyse zur nachtraeglichen Ursachenbestimmung.

Die gesamte gemeinsame Materialisierung wurde nicht abgeschlossen. Sie ist
Voraussetzung fuer die Runtimeinitialisierung. Somit wurden **keine Runtime-
instanzen erzeugt, keine Memoryformationen, Feldkontakte oder Scanaufrufe
ausgefuehrt**. Es gibt keine zu schliessenden Runtimeinstanzen. Beide
Hauptgates sind nach dem Aufruf nachweislich `False`.

Die noch nicht verarbeiteten Quellen wurden nicht ersatzweise erzeugt.
Kein Retry, Clipping, Nachskalieren, Seed-, Quellen- oder Parameterwechsel.
Die Teilmaterialisate und Rohpayloads wurden nicht als Ergebnis gespeichert.
`comparison` und `materialization` bleiben im Fehlerbeleg `null`; allein die
technischen Fortschrittszaehler stehen unter `failure.metrics`.

## Bindungen und einmalige Belegpruefung

Die Versiegelung und alle 104 qualifizierten Datei-/Quellenbindungen wurden
vor dem Lauf gelesen und geprueft. Die Payloadhashpruefung liegt jeweils
vor dem Rezeptoraufruf. Der erste vollstaendige AV-Payloadsatz und der
zweite Audiopayload erreichten ihre Analyse; kein Payloadhashfehler wurde
gemeldet. Keine Behauptung ueber ungeoeffnete spaetere Payloads.

Die unabhaengige Verifikation bestaetigt `evidence_valid = true`,
`read_only = true`, `file_unchanged = true`, `verification_calls = 1`.
Das bestaetigt nur die technische Gueltigkeit des **Abbruchbelegs**,
nicht eine abgeschlossene NH-Ausfuehrung.

- Ausfuehrungsplandigest unveraendert:
  `47ac97a175e37d45f576479ba82c906e4b36c47ae3708fca7d8e6ced885298a4`.
- Ergebnisdigest:
  `d4de5edc4e0b79630f4076e37a93104a39010710c4970d7472dcef6716fbe1a0`.
- SHA-256 von `recording.json`:
  `20f1096586590aa6492836f9d3ad9beb3f51d4fe4e49d32fa17e6757c0dda9ee`.
- Dateiverifikationsdigest:
  `bfcc1b3e6d0ecaea1661d7afe3deb59b9928630e16898e2fd193acf270a28e5f`.
- Einmalaufrufer SHA-256 vor/nach:
  `4f5abde3eeade18e53a38916fa95b796d8f4970a955b900d581c53066f5a0e5e`.

`call.json` bestaetigt unveraenderte Quellhashes und geschlossene Gates.
Die qualifizierten Module, Quellenversiegelung, Regeln, Schwellen, Kerne,
historischen Belege und fremden Arbeitsbaumaenderungen bleiben unveraendert.

## Aussagegrenze

N/D/R/L, Gewinne, Verluste, Fehlzulassungen, Zielverwerfungen, Konkurrenz,
Stabilisierung, Vermischung und Verdraengung sind **nicht ausgewertet**.
Sie werden nicht als Nullergebnis ausgegeben. Der technische Abbruch ist
keine Falsifikation der NH-Funktionsvorhersagen oder der Runtime.
Die neutrale 20/20-Anbindungsqualifikation bleibt historisch unveraendert.

STOPP: Dieser Einmallauf ist abgeschlossen; keine Wiederholung oder
Reparatur in derselben Freigabe.

RUECKMELDUNG ERFORDERLICH: Jede weitere Untersuchung benoetigt einen neuen,
eng begrenzten Auftrag. Es wurde keine Quellenanpassung vorbereitet.

WEITER: Am besten geht es jetzt mit der Analystenpruefung des lokalisierten
Abbruchbelegs und einer gegebenenfalls freigegebenen rein statischen
Klaerung der Rezeptorvertragsgrenze bei e02 weiter.
