# S2-TW-Ergebnis 20260919-01

Status: `RECORDING_COMPLETE`, unabhängig `VERIFIED`.

S2-TW verglich den unveränderten S2-TU-Aufbewahrungsarm mit einer privaten
Bestätigung, die nur nach vollständiger Gleichheit aller vier geordneten
Halbprofilzustände greift. Feld, A/B-Memory und Hypothesen waren nicht
beteiligt.

## Technischer Abschluss

* 26 Ereignisse: 22 materialisierte Audioendpunkte und vier Segmentabschlüsse.
* 22 PCM-Hashprüfungen, direkte Audioanalysen und NJ-Projektionen.
* 16 Formationen, sechs Hintframes, drei Entscheidungen je Arm.
* Zwei getrennte Owner-Abschlüsse nach dem letzten Ereignis.
* Der unabhängige Verifikator rekonstruiert Werte, Vollgleichheit,
  Übernahmen, Inventare, FIFO-Verdrängungen und Hintentscheidungen aus dem
  gespeicherten Record ohne Materialisierung oder Rezeptoraufruf.

`record.json` misst `34580` Byte, `verification.json` `126` Byte. Beide
liegen innerhalb der unveränderten gemeinsamen Zusatzgrenze von `262144`
Byte. Die gebundene konservative Vektor-Spitze beider Stores beträgt `10752`
Byte und bleibt getrennt von der serialisierten Beleggröße.

## Vergleichsbefund

| Abschluss oder Hint | S2-TU unverändert | S2-TW Bestätigung |
| --- | --- | --- |
| e10, exakte zweite Folge | Generation 2 zusätzlich übernommen; Inventar `1,2` | `TRACE_CONFIRMED` für Generation 1; Inventar bleibt `1` |
| e12, Hint `b,c` | `ABSTAIN_AMBIGUOUS_RETAINED_TRACE`, Generationen 1/2 | `TRACE_MATCH`, Generation 1, Offset 1 |
| e17, umgekehrte Folge | Generation 3, FIFO verdrängt 1 | Generation 2, kein FIFO-Verlust |
| e19, Hint `d,c` | `TRACE_MATCH`, Generation 3 | `TRACE_MATCH`, Generation 2 |
| e24, teilweise gleiche Folge | Generation 4 verdrängt 2; Inventar `3,4` | Generation 3 verdrängt die bestätigte Generation 1; Inventar `2,3` |
| e26, Hint `d,a` | `ABSTAIN_NO_RETAINED_TRACE` | `ABSTAIN_NO_RETAINED_TRACE` |

Die Verdrängung der bestätigten Generation ist durch den nativen
Bestätigungsarm-Receipt bei e24 (`evicted: 1`) und das Inventar `2,3`
belegt. H3 ist nur eine Negativkontrolle: Das Paar `d,a` lag auch vorher in
keiner Spur benachbart vor und dient nicht als Verdrängungsnachweis.

P3 wurde vollständig in umgekehrter Reihenfolge gespeichert. P4 wurde nicht
bestätigt und regulär übernommen. Der reale Record belegt damit nur fehlende
Vollgleichheit von P4; die neutral geprüfte Einzelkomponentenabweichung wird
nicht auf diese Rezeptorwerte übertragen.

## Aussagegrenze

Der Versuch belegt das Vermeiden einer exakten Doppelbelegung und die daraus
folgende begrenzte Abrufwirkung. Die Bestätigung erneuert weder Generation
noch FIFO-Alter und ist keine Variantenbindung, Stabilisierung durch Support
oder semantische Verdichtung.

Quellenwurzel: `6e64fbd5b7e86f16156b6d68bd5f7dbda3fefa8f223b2a31114bf3293eaa5f10`.
Neutralqualifikation: `reports/s2tw-exact-confirmation-qualification-20260919-01/REPORT.md`.
