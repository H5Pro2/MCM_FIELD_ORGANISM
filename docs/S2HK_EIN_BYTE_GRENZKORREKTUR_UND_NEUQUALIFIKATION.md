# S2-HK: Ein-Byte-Grenzkorrektur und Neuqualifikation

Status: `S2HK_COMPACT_PROJECTION_QUALIFICATION_VALID`

## Anlass

Der erweiterte 60-Huellen-Audit hat fuer die gueltige S2-GI-Worst-Case-Form
mit einer 96 Zeichen langen Owner-ID eine kanonische Huellengroesse von
2.978 Byte bestimmt. Die bisherige Maschinenbindung von 2.977 Byte war damit
um genau ein Byte zu klein. Die zuvor untersuchte 3.236-Byte-Form bleibt
vertragswidrig, weil sie Sequenzevidenz mit dem Status `NOT_REQUESTED`
vermischt.

## Korrekturgrenze

- `COMPACT_S2GI_MAX_ARTIFACT_BYTES` wird im privaten Runner und im
  unabhaengigen Verifikator von `2_977` auf `2_978` gesetzt.
- `COMPACT_FORMATION_MAX_ARTIFACT_BYTES = 2_801` bleibt unveraendert.
- `COMPACT_S2GC_MAX_ARTIFACT_BYTES = 3_174` bleibt unveraendert.
- Die Registrygrenze von 4.096 Byte und die Gesamtbudgets
  `2.009.088 / 2.045.952` Byte bleiben unveraendert.
- `NOT_REQUESTED` ist nur mit leerer Referenzmenge zulaessig. Jede zusaetzliche
  Sequenzreferenz wird fail-closed abgewiesen.

## Neue neutrale Qualifikation

Die Qualifikations-ID lautet
`s2hk-compact-projection-qualification-20260831-01`.

Die Fixture verwendet:

- einen aus den gebundenen Quellen materialisierten `ExecutionPlan`;
- eine kanonisch gueltige Owner-ID mit exakt 96 Zeichen;
- einen typisierten `NOT_REQUESTED`-Abwesenheitsbeleg ohne Sequenzreferenzen;
- dieselben zwoelf Testziele der vorherigen Qualifikation.

Vor dem einmaligen Lauf werden die Quellhashes gebunden. Nach dem Lauf werden
dieselben Quellen erneut gehasht. Es gibt keinen Retry und keine Korrektur
innerhalb dieser Qualifikations-ID.

## Ausfuehrungsbefund

Der genau einmal ausgefuehrte Qualifikationslauf endete mit:

- `12/12` bestandenen Tests;
- Exit-Code `0`;
- terminalem `OK`;
- identischen Quellhashes vor und nach der Ausfuehrung.

Die 60 kanonisch materialisierten Huellen ergaben:

| Rolle | Anzahl | Minimum | Maximum | Bindung |
|---|---:|---:|---:|---:|
| Formation | 52 | 2.786 | 2.799 | 2.801 |
| S2-GC | 4 | 2.645 | 3.165 | 3.174 |
| S2-GI | 4 | 2.511 | 2.978 | 2.978 |

Die S2-GI-Worst-Case-Huelle erreicht damit exakt die korrigierte Grenze. Die
4.096-Byte-Registrygrenze und die Gesamtbudgets wurden nicht veraendert.

## Fortbestehende Grenzen

S2-HC bleibt dauerhaft `NOT_EVALUABLE`. Der Kontextfunktionslauf bleibt
gesperrt. Diese Korrektur betrifft ausschliesslich die gueltige kanonische
Aufzeichnungshuelle und erzeugt keinen neuen Funktions- oder Memory-Befund.
