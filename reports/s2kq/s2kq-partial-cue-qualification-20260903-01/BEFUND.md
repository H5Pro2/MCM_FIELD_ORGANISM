# S2-KQ - Private Teilhinweisabruf-Qualifikation

## Status

`S2KQ_PRIVATE_READ_ONLY_PARTIAL_CUE_RETRIEVAL_336_VALID`

Qualifikations-ID:
`s2kq-partial-cue-qualification-20260903-01`

Der private read-only Slotscan und die unabhaengige Direktbaseline sind fuer
die neutrale 336-Werte-Vertragsgrenze qualifiziert. Dies ist noch kein realer
Teilhinweisabruf aus einer gebildeten Memorygeschichte.

## Einmalige Ausfuehrung

Kommando:

```text
python -m unittest tests.test_s2kq_private_partial_cue_retrieval_336
```

Ergebnis:

```text
S2KQ_MAX_NEUTRAL_OUTPUT_BYTES=17205
............
----------------------------------------------------------------------
Ran 12 tests in 0.557s

OK
```

Exit-Code: `0`

Es gab keinen Retry und keine Korrektur nach dem Testaufruf.

## Qualifizierte Grenzen

- exakt neun B4-, drei Fast- und vier visuelle Slow-Slots werden erfasst;
- alle drei Bankscans werden vor jeder Entscheidung vollstaendig beendet;
- eindeutiges A, eindeutiges B, A/B-Mehrdeutigkeit, Bankmehrdeutigkeit,
  B4/Fast-Konflikt, Abwesenheit und sichtbare Unvereinbarkeit sind getrennt;
- B4 und Fast bleiben interne Herkunftsrollen von `A_RECENT`;
- oeffentlich entstehen hoechstens `A_RECENT` und `B_STABLE`;
- mehrere passende Slots oder Bereiche fuehren ohne Rangfolge zur
  Enthaltung;
- die Hypothese enthaelt genau 256 maskierte Vorschlagswerte und keine
  beobachteten Werte oder Feldkontakte;
- Funktion und unabhaengige Direktbaseline stimmen in allen gueltigen
  Testfaellen fachlich ueberein;
- manipulierte Zustands-, Masken-, Dimensions- und Zeitbelege stoppen
  fail-closed;
- Eingabeprobe und Memoryzustand bleiben unveraendert.

Der materialisierte Worst Case enthaelt alle 16 Slotbelege, 800
Wertvergleiche und eine 256-Werte-Hypothese. Seine groessere der beiden
kanonischen Arm-Ausgaben betraegt `17.205` Byte und liegt unter der harten
Grenze von `32.768` Byte.

## Quellbindung

Die Vorher- und Nachher-Hashes sind identisch:

| Quelle | SHA-256 |
| --- | --- |
| `tools/_s2kq_private_partial_cue_retrieval_336.py` | `6abe7f915861446574c72dbe8da1a3368f9cd9009b1ab398407bfa968bd9fb67` |
| `tools/_s2kq_private_direct_slot_scan_baseline.py` | `5bd3bb6596071d38965f6036ab4dbd0b96249bc631109b89585078657723b71c` |
| `tests/test_s2kq_private_partial_cue_retrieval_336.py` | `48187107a1203468ba498f1bc97c49ef50724d5ed522a6731aadc16323dad81c` |

Die maschinenlesbaren Vorher-/Nachherlisten, das Kommando, die vollstaendige
Testausgabe und der Exit-Code liegen im selben Qualifikationsverzeichnis.

## Aussagegrenze

Qualifiziert ist nur die sichere read-only Slotscan-, A-Projektions- und
Zulassungslogik mit neutral konstruierten gueltigen Zustaenden. Es wurden
keine realen Bildungsgeschichten, Rezeptoren, Memoryformationen,
Vollproben, Kontextverbraucher oder Feldfunktionen ausgefuehrt.

Ein realer Teilhinweisabruf aus frisch gebildeten 336-Werte-Zustaenden
benoetigt eine separate Freigabe.
