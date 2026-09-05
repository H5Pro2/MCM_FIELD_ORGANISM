# S2-LZ: Prospektiver Zwei-Blick-Open-Set-Vergleich

## Fragestellung

S2-LZ prueft, ob zeitlich begrenzte, ausschliesslich beobachtete Zwei-Blick-
Evidenz bekannte Varianten zulassen und unbekannte oder unvereinbare Evidenz
zurueckweisen kann. Der Korpus, die zwei disjunkten 96er-Masken und die
Train-/Test-Trennung wurden vor jedem Rezeptoraufruf versiegelt.

Der Korpus enthaelt:

- vier bekannte Modelle mit je vier Referenzquellen;
- acht vollstaendig zurueckgehaltene bekannte Varianten;
- vier unbekannte Formen;
- vier mehrdeutige Zwischenformen;
- vier unvereinbare Blickpaare.

Fuer jedes Modell und jede Reprasentation wird die Zulassungshuelle allein aus
den vier Referenzen gebildet. Ihr Radius ist literal der groesste
Referenzabstand zum eigenen Referenzzentroid. Danach wird nichts anhand der
Testfaelle nachkalibriert. Zugelassen wird nur, wenn exakt ein Modell innerhalb
seiner vorab gebildeten Huelle liegt.

Die 192er-Vereinigung ist nur erlaubt, wenn beide Beobachtungen dieselbe
gebundene Quelle und denselben Payloaddigest besitzen und hoechstens einen Tick
auseinanderliegen. Sie enthaelt ausschliesslich die beiden disjunkten 96er-
Sichten. Fehlende Werte werden nicht ergaenzt.

## Ergebnis

| Arm | Bekannte Treffer | Bekannte Enthaltungen | Open-Set korrekt enthalten | Fehlzulassungen |
| --- | ---: | ---: | ---: | ---: |
| Blick A 96 | `3/8` | `5/8` | `8/8` | `0` |
| Blick B 96 | `2/8` | `6/8` | `8/8` | `0` |
| Zwei-Blick-Konsens | `1/8` | `7/8` | `12/12` | `0` |
| Vereinigung 192 | `7/8` | `1/8` | `12/12` | `0` |
| Vollform-Obergrenze | `8/8` | `0/8` | `12/12` | `0` |

Die Open-Set-Menge umfasst bei den Paararmen vier unbekannte Formen, vier
Zwischenformen und vier unvereinbare Paare. Alle werden enthalten. Es entsteht
keine falsche bekannte Zuordnung und keine Open-Set-Fehlzulassung.

Der Zwei-Blick-Konsens ist erneut zu restriktiv: Nur ein bekannter Holdout wird
von beiden Einzelblicken zugelassen. Die konfliktfreie 192er-Vereinigung
erkennt sieben. Der verbleibende Fall `case-003` liegt ausserhalb aller
vorab gebildeten 192er-Huellen und wird enthalten; die Vollform erkennt ihn
korrekt als `model-02`.

## Technischer Abschluss

- Plan: `36.333` Byte, SHA-256
  `69fec956b6e68bcde41367308fd9a4d785969fdbf1b62ef3eed5641de20b6fe7`;
- Ergebnis: `133.621` Byte, SHA-256
  `d8308a45474f177f26d877b2e9b01f0aa3f23ce02f3793d9eeefc7bd9f0563ab`;
- Vergleichsdigest:
  `efad341b38051730be78d6c44b34dc1bd82dfe207a7553659fc05cf3165a7892`;
- neutrale Qualifikation: `12/12`, Exit-Code `0`, `OK`;
- separate read-only Verifikation: `RECORDING_COMPLETE`;
- 56 visuelle Rezeptoranalysen; Memory-, Kontext- und Feldaufrufe jeweils `0`.

## Aussagegrenze

Der Befund bestaetigt eine kleine prospektive Open-Set-Zulassung fuer diesen
geometrischen Korpus. Die Huelle ist eine transparente, referenzabgeleitete
Engineeringregel und keine gelernte MCM-Memoryfunktion. Paarinkompatibilitaet
wird hier ueber technische Quellen- und Zeitkontinuitaet erkannt, nicht ueber
Semantik oder Objektverfolgung.

Die 192er-Evidenz darf deshalb erst in einem getrennten Schritt als zeitlich
begrenzte interne Wahrnehmungsintegration von `A_RECENT` kontrahiert werden.
Sie ist keine dritte Memoryebene und darf weder Feldkontakte noch beobachtete
Rezeptorwerte ueberschreiben.

Belege:

- `reports/s2lz/s2lz-open-set-corpus-20260905-01/presealed-plan.json`
- `reports/s2lz/s2lz-open-set-two-view-comparison-20260905-01/comparison.json`
- `reports/s2lz/s2lz-open-set-two-view-comparison-20260905-01/verification.json`
- `reports/s2lz/s2lz-open-set-neutral-qualification-20260905-01/qualification.json`
