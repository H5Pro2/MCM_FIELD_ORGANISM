# S2-MT: Vorversiegelter Transferstrom

## Entscheidung

Der einmalige Lauf `s2mt-presealed-transfer-runtime-20260905-01` ist
`NOT_EVALUABLE`.

Es liegt weder eine Bestaetigung noch eine fachliche Falsifikation der
Transferfrage vor. Der Ergebnisbeleg enthaelt keine Ausfuehrungs- oder
Auswertungsprojektion. Ein Befund zu A/B-Stabilisierung, C-Instabilitaet,
Verdraengung oder Teilhinweisabruf ist deshalb unzulaessig.

## Gebundener Umfang

- neue, vor der Rezeptoranalyse digestgebundene RGB-/PCM-Quellen;
- 28 neutrale Ereignisspezifikationen;
- 20 vorgesehene Formationen und acht Teilhinweise;
- 8.064 vorgesehene Feldkontakte;
- unveraenderte oeffentliche S2-MR-Runtime;
- keine Kontextanwendung oder Vervollstaendigung.

Der statische Preflight bestaetigte vor dem Lauf eindeutige Ereignis-IDs,
Zaehler, geschlossenes Gate, ein nicht vorhandenes Ergebnisverzeichnis und
identische Standszeiger fuer `main` und `origin/main` auf
`c040493dc47d778f2e2fd2297e1dc82604f080ec`.

## Einmalausfuehrung

Der Hauptaufruf wurde genau einmal ausgefuehrt. Der Aufruf endete mit
Exit-Code `0`, verbrauchte die Einmalmarke und setzte das Gate im
`finally`-Pfad wieder auf `False`.

Der atomare Ergebnisbeleg enthaelt:

- `technical_status = NOT_EVALUABLE`;
- `failure_code = S2MT_EXECUTION_FAILED`;
- `execution = null`;
- `evaluation = null`;
- 1.844 Byte kanonische Ergebnisdatei;
- Datei-SHA-256
  `9a027627e4e65e4b6c4719d1ff95e1afc32e65c25ea8a5f2bc9b275f09f2270b`;
- Record-Digest
  `db3f8cd99c059741ab5120b201b347c8baa4dd612a8156e7616e15d8d7292531`.

Die generische Fail-Closed-Form bindet keine Abbruchphase. Eine konkrete
Ursache kann daher aus dem abgeschlossenen Beleg nicht rekonstruiert werden.
Der Lauf wird nicht wiederholt oder nachtraeglich ergaenzt.

## Unabhaengige Verifikation

Genau eine read-only Verifikation wurde ausgefuehrt. Sie bestaetigte die
kanonische Serialisierung, den Record-Digest, die gebundenen Quellenhashes,
die Lauf-ID und die exklusive `NOT_EVALUABLE`-Form.

- Verifikationsstatus: `NOT_EVALUABLE`
- Read-only: `true`
- Verifikationsdigest:
  `9672045d03b7f5d4f08074acd247e0e1ffaaf9c1228496f22ca65ca3d704baf5`

Die drei neuen S2-MT-Quellen waren vor und nach dem Lauf bytegleich:

- Quellenplan: `ae808ad2a9f206bac45210f5f121e232e72da76b22e0b2bf7c599cc57e479f15`
- Runner: `4f7beb059a966c3fb343262a9930b13246ee584c1bc6453c6df08899c0fcaa1a`
- Verifikator: `acb1c9b6f519e15b290cf6138a642e8decc40f8e6a1d7c608426eb5131c8952a`

S2-MS und alle frueheren bestaetigten Befunde bleiben unveraendert. Die
bekannte Bootstrap-Datei ist weiterhin ausgeschlossen.
