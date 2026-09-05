# S2-MS: Reproduktion der S2-LN-Folge ueber den minimalen Runtime

## Ergebnis

Status: `S2MS_MINIMAL_RUNTIME_S2LN_REPRODUCTION_CONFIRMED`

Die unveraenderte S2-LN-Ereignisfolge wurde genau einmal ueber eine einzige
Instanz von `MinimalMCMRuntime336` verarbeitet. Alle Ereignisfortschreibungen
liefen ausschliesslich ueber deren oeffentliche Methoden `process_once`,
`snapshot` und `close`.

## Laufbindung

- Lauf-ID: `s2ms-minimal-runtime-s2ln-20260905-01`;
- Ereignisbudget: `18`;
- vollstaendige AV-Formationen: `16`;
- spaetere Teilhinweise: ein auditiver und ein visueller;
- Feldkontakte: `5.712`;
- Hauptaufrufe: genau einer;
- Retries: keine;
- read-only Verifikationen: genau eine.

## Technischer Abschluss

- Aufzeichnung: `RECORDING_COMPLETE`;
- Verifikation: `RECORDING_COMPLETE`;
- Record-Digest:
  `412e2565a7129054ae24e0e716a166515d87a3a7b013eb7f16cf38308c01cf27`;
- Verification-Digest:
  `827991aafa8f87fff6c91f00bf5681d006987bface0af82313bf882336dc6f5c`;
- Ergebnisdatei: `82.943` Byte;
- Ergebnisdatei-SHA-256:
  `e90c7c08461dcf4895e529aaf4cfd54638e4610276a897864373301baac289cd`;
- Hauptgate nach dem Lauf: `False`.

## Funktionale Projektion

- `18` Feldversuche und `18` gueltige Feldkontakte;
- `16` atomare Memoryformationen;
- `4` Scans, je Produktions- und Direktbaseline fuer beide Modalitaeten;
- finaler B4-Bestand aus den Formationen `8...16`;
- Ziel vollstaendig aus `A_RECENT` entfernt;
- auditory `B_STABLE` mit Support `3`;
- visual `B_STABLE` mit Support `3`;
- auditiver Hinweis liefert eine getrennte Hypothese aus
  `B_STABLE_AUDITORY`;
- visueller Hinweis liefert eine getrennte Hypothese aus `B_STABLE`;
- Memorydigest bleibt waehrend beider Hinweise unveraendert;
- keine Hypothese wurde angewendet oder zur Vervollstaendigung verwendet.

Die funktionale Projektion stimmt vollstaendig mit dem gebundenen,
verifizierten S2-LN-Referenzbefund ueberein. Runtime-, Owner-, Schritt- und
sonstige laufabhaengige Digests mussten und sollten dabei nicht identisch
sein.

## Abschlusszustand

Vor `close()`:

- Status `OPEN`;
- naechste Ordinalzahl `19`;
- `18/18/16/4` fuer Ereignisse, Feld, Formationen und Scans.

Nach `close()`:

- Status `CLOSED`;
- Feld-, Memory- und S2-LM-Stromdigest unveraendert;
- nur der Runtime-Snapshotdigest aendert sich durch die gebundene Phase.

## Quellhashes vor und nach dem Lauf

| Datei | SHA-256 |
| --- | --- |
| `tools/_s2ms_private_minimal_runtime_reproduction.py` | `d128e4af568a5cf2f120b533793a27c4f2dfee45a328da4674a9b214beed7a48` |
| `tools/_s2ms_private_minimal_runtime_verifier.py` | `ff5791b875ecc22243a21000f51026b4bfbef099f69c327e58b9ba374299ab9c` |
| `tools/_s2mr_private_minimal_mcm_runtime.py` | `da7699b6ef2a17c3b241f257a8aa9c954439e8a2b5cc37dab2a372a7691cf49f` |

Alle drei Hashes blieben unveraendert.

## Aussagegrenze

S2-MS bestaetigt, dass Feldkontakt, atomare Zwei-Bereich-Memorybildung,
zeitlich verteilte Verdichtung, Verlust aus `A_RECENT` und spaeterer
read-only Teilhinweisabruf gemeinsam ueber eine minimale zustandstragende
Runtimeoberflaeche arbeiten.

Nicht bestaetigt sind Hypothesenanwendung, automatische Vervollstaendigung,
Kontextwahl, Livequellen, Semantik, Feldrueckwirkung oder dauerhafte
Wiederanlaufpersistenz.
