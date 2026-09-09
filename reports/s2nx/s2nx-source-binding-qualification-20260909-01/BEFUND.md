# S2-NX: neutrale Quellen-/Bindungsqualifikation

Lauf-ID: `s2nx-source-binding-qualification-20260909-01`.
Status: `S2NX_SOURCE_BINDING_QUALIFIED`, **24/24**, Exit-Code `0`.
Genau ein Testaufruf; kein Retry. Inventar, Quellenhashes, Umgebung und
Budgets wurden vor dem Aufruf in [preregistration.json](preregistration.json)
gebunden. Alle 24 Testkoerper wurden laut [Testprotokoll](stderr.txt) erreicht.

## Gepruefter Umfang

- 32 literale Fenster, native Indizes, Reihenfolge und getrennte Identitaeten.
- Expliziter Nenner 1024, Partial-/Phasenfolge mit Nullpositionen, lokale
  Synthesezeit und genau eine Float32-Rundung an sechs neutralen Samples.
- Zwei getrennte Lernhistorien aus Nullzustand, je vier spaetere Updates,
  beide Einfriergrenzen vor der ersten Pruefquelle und kein Testupdate.
- Zwoelf gemeinsame Pruefstellen, feste Kontrolle 0.5 mit Binary64-Hexbindung,
  28 getrennte Bewertungskriterien; keine vorgegebenen Lernkoeffizienten.
- Quellen-/Zeit-/Wurzelmanipulationen, funktionale Metadatenabschottung,
  unveraenderliche Rezepte, Built-in-math und vollstaendige Metadatenhuellen.
- Historischer NW-Nenner bleibt unveraendert; seine Validierung wird nicht
  gelockert. Unterschiedliche Fits bleiben funktional, kein Startgate.

Die Corpusgenerator-Einstiege waren im Test gesperrt. Keine NX-Payloads,
Rezeptor-/NJ-Analysen, Lern-/Prognoseberechnungen oder Systemaufrufe.
Die spaetere kausale Ausfuehrung und wirkliches Einfrieren sind damit noch
nicht qualifiziert; geprueft sind Quellen- und Ablaufmetadaten.

## Bindungen

[result.json](result.json) enthaelt identische Vorher-/Nachher-Quellhashes.

| Bindung | SHA-256 / Digest |
| --- | --- |
| Ergebnisdigest | `0e6ef13f65a8c1f7fd91604e39f831be17a1a00ffb280a4b174657c797291e8a` |
| Quellenmodul | `d5b16c7e8f2a997f63baaf500f53e96c930613e7f653f60ce6b10de97dc7aab3` |
| Unabhaengiger Verifikator | `c4842e603903441e107ef8a69fc71114e46b7264fc9ef1d10b3986fe83dc2bc1` |
| Testdatei | `6a87961f9bdb06f7ecafeaf146c275c64764fa69eb86cb9379423f375ed690d4` |
| Unveraenderter NX-Plan | `e9c156a77f5e22ca2a5765179cf9093b6d7e5c10a38a349c7399a09c0c8fb496` |

Das Bestehen erlaubte ausschliesslich die anschliessende einmalige
[Vorversiegelung](../s2nx-source-preseal-20260909-01/BEFUND.md).
Gates `False`, ME/MI gesperrt. Historische Belege und Bootstrap unveraendert.
