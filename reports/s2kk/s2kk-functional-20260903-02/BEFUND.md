# S2-KK Funktionsbefund

## Status

`S2KK_LEARNED_VISUAL_CONTEXT_UTILITY_CONFIRMED_DIRECT_ADAPTIVE_FILL_EXPLAINS`

Lauf-ID: `s2kk-functional-20260903-02`

Quellenstand:
`78ff17dfe9e22e031bab218bcd6ba81c442e2e7d`

Der einmalige prospektive Lauf und die eine nachgelagerte read-only
Belegpruefung sind vollstaendig bestanden. Es gab keinen Retry, keine
Parameteraenderung und keine nachtraegliche Korrektur.

## Gebundener Umfang

- 17 atomare Memoryformationen;
- eine strikt spaetere Vollprobe `H_FULL`;
- eine nochmals spaetere maskierte Probe `H_MASKED`;
- alle fuenf Vergleichsarme;
- exakt 161 funktionale Top-Level-Operationen;
- 20 visuelle Rezeptoranalysen und 190 auditive Hop-Aufrufe;
- keine gespeicherten Rohpayloads.

Das korrigierte Startgate bestaetigte vor dem ersten Memoryaufruf fuer alle
63 Distraktorbeziehungen exakt null gemeinsame Fast-Matches. `H_FULL` und
`H_MASKED` kamen in keiner Formation und keinem Baselinetraining vor.

## Memory- und Kontextbefund

Nach den neun Distraktoren galt fuer `H_FULL`:

- kein Treffer in `B4_RECENT`;
- kein Treffer in `TSPM_FAST`;
- visueller Treffer in `B_STABLE`;
- Slow-Support exakt `3`.

Der Kontext wurde ausschliesslich aus dem bereits gebildeten
`B_STABLE_VISUAL`-Kandidaten bereitgestellt. Die Zielwerte wurden erst nach
Abschluss aller Armresultate in der getrennten Auswertung gebunden.

## Vergleichsarme

| Arm | ergaenzte Maskenwerte | Vollvektor-Loss |
| --- | ---: | ---: |
| `CURRENT_PERCEPTION_ONLY` | 0 | `0.8888888888888888` |
| `FROZEN_FIRST_PROTOTYPE` | 0 | `0.8888888888888888` |
| `REPLAY_NEAREST_EXEMPLAR` | 0 | `0.8888888888888888` |
| `ADAPTIVE_B_STABLE_CONTEXT` | 256 | `0.008610662418300614` |
| `DIRECT_ADAPTIVE_MASK_FILL` | 256 | `0.008610662418300614` |

Kontextverbraucher und unabhaengige direkte adaptive Maskenfuellung waren
wert- und positionsgleich. Alle 32 sichtbaren Werte blieben in jedem Arm
unveraendert.

## Read-only Verifikation

Die einmalige reine Ergebnispruefung bestaetigte:

- Ergebnisdigest und Quellenhashes;
- vollstaendige 17er Zustandskette;
- `17/1/1`, `0/63` und das 161er Operationsbudget;
- alle fuenf Armbelege;
- identische Vor-/Nachzustandsdigests fuer Memoryprobe, Kontextprojektion,
  Kontextverbrauch, Baselineproben und Auswertung;
- terminalen Status `RECORDING_COMPLETE`.

Ergebnisdigest:
`63938195a05d8bcc1921c0e5a6a90896c04e8239decb888f81959688e03f37cb`

## Aussagegrenze

Der Lauf bestaetigt, dass ein erfahrungsabhaengig verdichteter und
ausdruecklich bereitgestellter visueller Slow-Kontext eine spaetere
maskierte Wahrnehmung gegenueber Current-only verbessert. Die unabhaengige
Direktbaseline erklaert die konkrete Fuellfunktion vollstaendig.

Nicht nachgewiesen sind automatische Kontextwahl, Maskenerkennung,
Objektbedeutung, Semantik, Feldrueckwirkung oder besondere MCM-Physik. Der
fruehere Lauf `s2kk-functional-20260903-01` bleibt dauerhaft
`NOT_EVALUABLE`.
