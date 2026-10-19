# S2-TU-Ergebnis 20260919-01

Status: `RECORDING_COMPLETE`, unabhängig `VERIFIED`.

S2-TU prüfte ausschließlich die ownergebundene Aufbewahrung abgeschlossener
exakter Vierertraces. Es gab keine Feldkontakte, keine A/B-Auflösung und
keine Hypothesenanwendung.

## Technischer Abschluss

* 23 Ereignisse: 12 Formationen, acht Hintframes und drei Segmentabschlüsse.
* 20 PCM-Prüfungen, 20 direkte Rezeptoranalysen und 20 NJ-Projektionen.
* Ein separater finaler Owner-Abschluss nach dem letzten Ereignis.
* Der Verifikator rekonstruierte aus dem gespeicherten Beleg Quellen-,
  Zeit-, Frame-, Übergangs- und Entscheidungsbindung ohne Materialisierung
  oder erneuten Rezeptoraufruf.

Die Vektor-Spitze beträgt wie gebunden `5376` Byte: zwei gehaltene
Vierertraces, ein aktiver Viererformationspuffer und ein Zweierhintpuffer.
Sie ist getrennt von der serialisierten Beleggröße. `record.json` misst
`33519` Byte, `verification.json` `97` Byte; beide liegen innerhalb der
gemeinsamen Beleggrenze von `262144` Byte.

## Fachliche Befunde

| Entscheidung | Ergebnis |
| --- | --- |
| e12, H1 `b,c` | `TRACE_MATCH`, Generation 1, Offset 1 |
| e14, H1 `c,b` | `TRACE_MATCH`, Generation 2, Offset 0 |
| e21, H2 `b,c` | `ABSTAIN_NO_RETAINED_TRACE` |
| e23, H2 `c,b` | `ABSTAIN_AMBIGUOUS_RETAINED_TRACE`, Generationen 2/3, Offsets 0/1 |

Der dritte Segmentabschluss hielt Generation 3 und ersetzte Generation 1
FIFO. Vor dem separaten Owner-Abschluss waren exakt die Generationen `2,3`
gebunden; danach ist kein weiterer Zugriff zulässig. Die Mehrdeutigkeit von
H2 `c,b` ist daher keine technische Störung, sondern folgt aus den zwei
tatsächlich gehaltenen Spuren.

## Grenzen

Der Befund belegt begrenzte ownergebundene Aufbewahrung, FIFO-Ersetzung und
read-only Hintentscheidungen in diesem Vierertrace-Modell. Er belegt weder
eine semantische Zuordnung noch Feld-, A/B- oder Hypothesenverhalten.

Quellenwurzel: `6e64fbd5b7e86f16156b6d68bd5f7dbda3fefa8f223b2a31114bf3293eaa5f10`.
Neutralqualifikation: `reports/s2tu-retention-qualification-20260919-01/REPORT.md`.
