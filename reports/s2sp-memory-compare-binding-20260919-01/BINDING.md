# S2-SP-Memoryvergleich: Bindung

Auftragskennung: `S2SP-MEMORY-COMPARE-20260919-01`  
Geplante Lauf-ID: `s2sp-memory-compare-real-20260919-01`

## Unveränderte Mechanik

Der Vergleich verwendet die private S2-JW-Formation unverändert. Jede
Formation erzeugt atomar einen B4-, Fast- und gegebenenfalls visuellen
PPB-Übergang. Die Auswertung liest ausschließlich die danach tatsächlich
belegten visuellen Werte der drei Banken. Sie ruft keine öffentliche
Teilhinweisfunktion und keine Hypothesenanwendung auf.

Die historische Exaktbaseline der ersten 32 Werte und der private S2-SP-
Versatzhinweis (`-1`, `0`, `+1`; vollständige sichtbare Überlappung) prüfen je
Bank exakt denselben Kandidatenbestand. Es gibt weder Rangordnung noch
Kandidatenauswahl über Auswertungsrollen.

## Gebundene Folge

| Ereignisse | Inhalt | Verarbeitung |
| --- | --- | --- |
| e01 | A0 | Formation |
| e02 | A0 | read-only Referenzhinweis |
| e03-e05 | A0 | drei Formationen |
| e06 | A0 | read-only Stabilisierungshinweis |
| e07 | A1 | read-only verschobener Hinweis |
| e08-e16 | B1 | neun Formationen als A-Druck und Ersetzungstest |
| e17 | A0 | read-only Verfügbarkeitshinweis |
| e18 | A1 | read-only verschobener Hinweis unter Konkurrenz |
| e19 | B1 | read-only Konkurrenzhinweis |

`A0` ist die Referenz, `A1` ihre Ein-Zell-Verschiebung und `B1` eine
Innenabweichung. Diese Rollen liegen ausschließlich in der Auswertung. Die
Laufmechanik erhält nur die gebundenen RGB- und PCM-Werte. Die ursprüngliche
B4-Generation aus e01 wird nach e16 gegen den tatsächlichen finalen
B4-Bestand geprüft; ein historischer Herkunftsnachweis ersetzt keine aktuelle
Verfügbarkeit.

## Ressourcen

- 19 Ereignisse: 13 Formationen und sechs read-only Hinweise;
- 13 Audioanalysen, 19 Visualanalysen, 130 Audiohops;
- keine Feldkontakte, keine öffentliche Hypothese, keine Memoryänderung durch
  Hinweise;
- höchstens ein PCM-Fenster und ein RGB-Frame zur selben Zeit;
- maximal 16 visuelle Kandidaten pro Hinweis und Bank;
- späterer veröffentlichter Gesamtnachweis maximal 524.288 Byte.

## Neutrale Qualifikation

Ein einmaliger fokussierter Testlauf prüft echte atomare Formation mit
read-only Hinweis, die Abweisung einer Innenabweichung und die Nichtverfügung
der ursprünglichen B4-Kandidatenbindung nach Ersetzung. Der Test verwendet
neutrale Rezeptoren und keine gebundene S2-SP-Hauptfolge.

| Datei | SHA-256 |
| --- | --- |
| `tools/_s2sp_private_memory_compare.py` | `9c79df376483727371451fbb7b8b1f830e4e6ffd1a04cd12ba689467585f58d2` |
| `tests/test_s2sp_private_memory_compare.py` | `078f4a4a6b26d6a976bfd794c7337a8f93753adcd077ce2c6f79c8a6bdcc4141` |
| `tools/_s2sp_private_shift_hint.py` | `cc16661dc16f75e5e59e077a739c7b7a608168d68aafe1cdb31071f04532ed36` |
| `tools/_s2jw_profiled_memory_coordinator.py` | `4a737735abe8324755f0c9e585b95351bf9533251b50aed4b40fc319d9ad640e` |

## Anschlussqualifikation und Einmalrunner

Die korrigierte vollständige Qualifikation
`S2SP-MEMORY-COMPARE-QUAL-20260919-02` erreichte `3/3`. Sie prüfte die
unveränderte Übernahme nativer visueller Rezeptorwerte, den read-only
Versatzhinweis, die Abweisung einer Innenabweichung und die B4-Ersetzung.
Der frühere Befund `…-01` bleibt `NOT_QUALIFIED`.

Der gebundene Einmalrunner ist
`reports/run_s2sp_memory_compare_once.py`, SHA-256
`7ac8e239c898391ea9373921e1886193871d98598e6b0446fbc2a058f8846545`.
Er veröffentlicht nur Zustands-, Herkunfts- und die für die private
Teilstrukturverifikation benötigten sichtbaren Kandidatenwerte. Der
Verifikator führt keine Rezeptoranalyse oder Formation erneut aus.
