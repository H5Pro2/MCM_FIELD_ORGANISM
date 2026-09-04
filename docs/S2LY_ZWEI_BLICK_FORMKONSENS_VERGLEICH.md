# S2-LY: Zwei-Blick-Formkonsens

## Fragestellung

S2-LY prueft prospektiv, ob zwei zeitlich aufeinanderfolgende, raeumlich
verteilte 96-Werte-Sichten Unsicherheit besser begrenzen als ein einzelner
Teilhinweis. Kontext wird nur zugelassen, wenn beide Sichten unabhaengig
denselben eindeutigen Kandidaten bestimmen. Es gibt keine Rangfolge,
Imputation, Schwelle, Memory- oder Feldintegration.

Vor jeder Rezeptoranalyse wurde ein neuer Korpus versiegelt:

- vier neutrale Formkandidaten und 28 spaetere Varianten;
- 32 eindeutige kanonische RGB8-Quellen;
- zwei disjunkte, koordinaten- und seedgebundene 96er-Masken;
- 56 Beobachtungen in fester Reihenfolge: Blick A vor Blick B;
- Familienrollen nur in der getrennten Auswertungswurzel.

Beide Masken decken alle acht Rasterzeilen, zwoelf Spalten und drei Kanaele
ab. Ihre Vereinigung enthaelt exakt 192 unterschiedliche Rezeptorwerte. Die
fehlenden Werte sind in den maskenkonditionierten Formprojektionen nicht
vorhanden und werden nicht ergaenzt.

## Ergebnis

| Arm | Korrekt | Fehlzulassung | Enthaltung | Korrekte Abdeckung |
| --- | ---: | ---: | ---: | ---: |
| Blick A, Form 96 | `26/28` | `2` | `0` | `92,86 %` |
| Blick B, Form 96 | `24/28` | `4` | `0` | `85,71 %` |
| Zwei-Blick-Konsens | `23/28` | `1` | `4` | `82,14 %` |
| Vereinigte Form 192 | `28/28` | `0` | `0` | `100 %` |
| Vollvektor 288 | `16/28` | `10` | `2` | `57,14 %` |
| Vollform-Obergrenze | `28/28` | `0` | `0` | `100 %` |

Der Konsens wandelt vier voneinander abweichende Einzelblickentscheidungen in
kontrollierte Enthaltung um und reduziert Fehlzulassungen gegenueber beiden
Einzelblicken. Er ist jedoch kein Vollstaendigkeitsbeweis: Bei `source-010`
waehlen beide Teilansichten systematisch denselben falschen Kandidaten. Diese
gemeinsame Fehlzulassung bleibt sichtbar und wird nicht nachtraeglich
umklassifiziert.

Die 192er-Vereinigung erreicht auf diesem Korpus dieselben `28/28` wie die
Vollform. Der rohe 288-Werte-Vektor ist mit `16/28` deutlich schwaecher. Der
Befund stuetzt damit weitere zeitliche Sichtbarkeit plus Formnormalisierung,
nicht eine neue globale Distanzgrenze.

## Technischer Abschluss

- Plan: `35.268` Byte, SHA-256
  `9c8d3e5f9aba866481e638a3354bb741d73b40c178d2342d0387a6f965c34348`;
- Ergebnis: `174.259` Byte, SHA-256
  `bb3aad06e0344f9b772deae2f8305aecacb6b6763a9ff838b3f9adc59bbeb06d`;
- Vergleichsdigest:
  `bee0c4f0924f6a231d4eafe676440824764a391029fb818e60da17d624a0667c`;
- 60 Rezeptoranalysen, Memory-, Kontext- und Feldaufrufe jeweils `0`;
- zweite neutrale Qualifikation: `12/12`, Exit-Code `0`, `OK`;
- separate read-only Verifikation: `RECORDING_COMPLETE`.

Die erste Qualifikation bleibt mit `11/12` als nicht qualifizierend erhalten.
Sie scheiterte an einer Reihenfolgeannahme des Verifikators fuer kanonisch
sortierte JSON-Objektschluessel, nicht an der Zwei-Blick-Funktion.

## Entscheidung

Zwei unabhaengige Blicke verbessern die Sicherheit durch Enthaltung, verlieren
aber Abdeckung und koennen eine gemeinsame systematische Verwechslung nicht
erkennen. Die disjunkte 192er-Vereinigung loest den konkreten Korpus dagegen
vollstaendig. Vor einem Memoryanschluss ist daher eher eine gebundene
zeitliche Evidenzvereinigung zu pruefen als eine neue Schwelle oder weitere
Imputation.

Belege:

- `reports/s2ly/s2ly-two-view-corpus-20260905-01/presealed-plan.json`
- `reports/s2ly/s2ly-two-view-consensus-comparison-20260905-01/comparison.json`
- `reports/s2ly/s2ly-two-view-consensus-comparison-20260905-01/verification.json`
- `reports/s2ly/s2ly-two-view-neutral-qualification-20260905-01/qualification.json`
- `reports/s2ly/s2ly-two-view-neutral-qualification-20260905-02/qualification.json`
