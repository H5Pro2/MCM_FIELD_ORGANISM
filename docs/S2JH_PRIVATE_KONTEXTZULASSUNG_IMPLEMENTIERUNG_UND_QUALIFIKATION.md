# S2-JH - Private Kontextzulassung und neutrale Qualifikation

## Implementierungsstand

Die private S2-JG-Zulassungsschicht ist implementiert:

- unveraenderliche Eingabe-, Owner-, Ledger-, Ergebnis- und Receiptformen;
- reine Entscheidung `ALLOW_CONTEXT` oder `PROCEED_WITHOUT_CONTEXT` fuer alle
  fuenf bestaetigten S2-IC-Statuswerte;
- `SINGLE_SOURCE` bindet nur die einzige anwendbare Rolle;
- `CONSISTENT` bindet ausschliesslich einen ungeordneten
  A/B-Aequivalenzset-Digest und den gemeinsamen Ergaenzungsdigest;
- `CONFLICT`, `NO_CONTEXT` und `NO_APPLICABLE_CONTEXT` geben keine
  Kontextreferenz aus;
- atomarer Einmal-Owner mit `CONSUMED` oder `FAILED`;
- unabhaengige direkte Entscheidungstabellen-Baseline;
- keine Memory-, Rezeptor-, Runner-, Datei- oder Feldfunktion.

Gebundene Grenzen:

```text
logische Operationen pro Erfolg = 4
maximale Erfolgsartefaktbytes    = 11264
Einzelgrenzen:
  input   2304
  owner   1536
  ledger  1280
  result  2560
  receipt 2048
Memory-/Rezeptor-/Feldaufrufe   = 0
```

## Erster Qualifikationslauf

Ausgefuehrt wurde genau einmal:

```text
python -m unittest -v tests.test_s2jh_private_controlled_context_admission
```

Ergebnis:

```text
12 Tests gestartet
11 bestanden
1 fehlgeschlagen
Exit-Code 1
FAILED
```

Status:

`QUALIFICATION_FAILED_TEST_EVIDENCE_MISMATCH`

Der Fehler lag in Test 1: Zulassungsfunktion und Direktbaseline erhielten zwei
getrennt erzeugte neutrale Signalbelege. Der Test verglich danach
quellenabhaengige Aequivalenzdigests, die bei verschiedenen Belegen
notwendigerweise verschieden sind. Das verletzt die S2-JG-Vorgabe identischer
Baselineeingaben und ist kein Produkt- oder Funktionsfehler.

## Enge Testkorrektur

Ausschliesslich die Testvorbereitung wurde anschliessend statisch korrigiert:
Zulassungsfunktion und Direktbaseline erhalten nun denselben einmal erzeugten
S2-IC-Signalbeleg und getrennte S2-JH-Owner. Produktcode,
Entscheidungstabellen, Grenzen und die zwoelf Testdefinitionen blieben
unveraendert.

Die korrigierte Suite wurde in diesem ersten Schritt nicht erneut ausgefuehrt.
S2-JH war zu diesem Zeitpunkt noch nicht neutral qualifiziert. Der erste
Fehlbefund bleibt unveraendert erhalten.

## Quellbindungen nach der Korrektur

| Rolle | Quelle | SHA-256 |
| --- | --- | --- |
| Zulassungsfunktion und Datentypen | `tools/_s2jh_private_controlled_context_admission.py` | `191c9216703885c24397fabd13dd15d359531445b0b9d4dce70cfda2126258bc` |
| Unabhaengige Tabellenbaseline | `tools/_s2jh_private_direct_admission_baseline.py` | `e151b195d7aa7bda1e4edeee44eb25e83a273f615244409779e5fe525911e340` |
| Korrigierte neutrale Tests | `tests/test_s2jh_private_controlled_context_admission.py` | `b63b9c5dc93bd475d816cc222158d800ce6463d2f850ea9df62262f3c7fe6bce` |

Die offene spaetere Wahrnehmungsgrenze fuer austauschbare Browser-, Desktop-,
Video-, Simulations- und Kameraquellen wird durch S2-JH weder geschlossen noch
umgangen. DOM, URL und sonstige Metadaten sind kein Eingang der
Zulassungsfunktion.

## Neue Einmalqualifikation

Qualifikations-ID:

`s2jh-controlled-context-admission-qualification-20260901-02`

Unter dieser neuen ID wurde die korrigierte Suite genau einmal ausgefuehrt:

```text
python -m unittest -v tests.test_s2jh_private_controlled_context_admission
```

Ergebnis:

```text
12 Tests gestartet
12 bestanden
Exit-Code 0
OK
```

Die vor und nach dem Lauf erhobenen SHA-256-Digests waren jeweils identisch:

| Rolle | SHA-256 vor und nach dem Lauf |
| --- | --- |
| Zulassungsfunktion und Datentypen | `191c9216703885c24397fabd13dd15d359531445b0b9d4dce70cfda2126258bc` |
| Unabhaengige Tabellenbaseline | `e151b195d7aa7bda1e4edeee44eb25e83a273f615244409779e5fe525911e340` |
| Korrigierte neutrale Tests | `b63b9c5dc93bd475d816cc222158d800ce6463d2f850ea9df62262f3c7fe6bce` |

Damit ist der freigegebene Status gesetzt:

`PRIVATE_CONTROLLED_CONTEXT_ADMISSION_VALID`

Die Qualifikation bestaetigt ausschliesslich die private read-only
Zulassungsfunktion, ihre unabhaengige Entscheidungstabellen-Baseline,
Owner-Einmaligkeit, Fail-Closed-Grenzen sowie Zustandsunveraenderlichkeit. Es
fand kein realer Kontextzulassungs- oder Kontextverbrauchslauf statt.
