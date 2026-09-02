# S2-JW - Private Default-Live-Memoryadapter: Implementierung und Qualifikation

## Status

`S2JW_PRIVATE_DEFAULT_LIVE_MEMORY_ADAPTERS_QUALIFIED`

Die eng begrenzte private Adapterlinie fuer `48 + 288 = 336` echte
Default-Live-Rezeptorwerte ist implementiert und fokussiert qualifiziert.
Der gebundene Verlauf mit 15 Formationen und drei Proben wurde nicht
ausgefuehrt. Dieser Befund ist daher noch kein Memory-Funktionsbefund fuer X,
Y oder D9.

## Implementierter Umfang

- `tools/_s2jw_default_live_profile.py`: digestgebundene Default-Live-Profil-
  und TSPM-Konfiguration;
- `tools/_s2jw_default_live_av_pairing.py`: source-neutrale Paarung eines
  echten auditiven und visuellen Rezeptorabschlusses mit positiver
  Feldzeitueberlappung;
- `tools/_s2jw_profiled_memory_coordinator.py`: profilabgeleiteter atomarer
  B4-/TSPM-Verbund mit einmaligem Owner;
- `tools/_s2jw_profiled_memory_read_only.py`: getrennte read-only Befunde fuer
  B4, Fast sowie auditive und visuelle Slow-Bank;
- `tools/_s2jw_profiled_memory_ledger.py`: aus Profil, Carrierzahlen und
  Slotkapazitaeten abgeleitete Grenzen;
- `tests/test_s2jw_default_live_memory_adapters.py`: 14 neutrale
  Qualifikationstests.

Die private `PPB1ActiveReceptorBatchEnvelope` akzeptiert zusaetzlich das
vorhandene Profil `default-live`. Der bestehende
`bind_ppb1_active_receptor_batch` bleibt weiterhin literal browserexklusiv.
Eine Browser-Umetikettierung findet nicht statt.

PPB-1, TSPM-1 und der dimensionsneutrale B4-Operator blieben unveraendert.
Ihre SHA-256-Digests sind:

| Kern | SHA-256 |
| --- | --- |
| PPB-1 | `15f1fabaa45348f067b7bf466f138d275d74f75a6e98afc05867f7b8c35d46f0` |
| TSPM-1 | `321ce786c42edd217dc6dbf2210c495016b2babaa78d53449a13b0039965d516` |
| B4-Vergleichsoperator | `96cdd018be34afe67de0139428fed5254cff945ba74db98163a91273f5d21b2c` |

## Qualifikationsumfang

Die neutrale Fixture verwendete drei kurze, real erzeugte
Default-Live-AV-Fenster. Visuelle Werte entstanden mit
`LocalChannelGridReceptor(VisualGridConfig())`; auditive Werte mit einem
frischen `BroadbandHearingPath(LogSpectralReceptor(LogSpectralConfig()))`.
Kein Test verwendete X, Y, D1 bis D9 oder den vollstaendigen S2-JV-Verlauf.

Geprueft wurden:

1. exakte Profil-, Dimensions- und Digestbindung;
2. `default-live` ohne Browser-Umetikettierung;
3. echte 336-Werte-Paarung mit 10-ms-Ueberlappung;
4. Fail-Closed bei Profil- oder Zeitmanipulation;
5. initiale B4-/TSPM-Invarianten;
6. atomarer realer Doppelschritt;
7. Generationsgleichheit ueber zwei neutrale Schritte;
8. Stopp vor beiden Armen bei ungueltigem Vorzustand;
9. kein sichtbarer B4-Teilzustand bei injiziertem TSPM-Fehler;
10. Owner-Einmaligkeit;
11. getrennte read-only Befunde und Zustandsunveraenderlichkeit;
12. vollstaendige B4-FIFO-Anatomie;
13. profilabgeleitete Ledger- und S2-JV-Plangrenzen;
14. unveraenderte Kernhashes, private Exportgrenze und Rohdatenausschluss.

Ausgefuehrter Einzelaufruf:

```text
python -m unittest tests.test_s2jw_default_live_memory_adapters -v
```

Ergebnis:

```text
Ran 14 tests in 0.345s

OK
Exit-Code: 0
```

## Gebundene Grenzen

Die Qualifikation bestaetigte:

- Dimensionen `48/288/336` und unveraenderte Slotzahlen `9/3/8/4`;
- maximale L1-Grenzen `3.552` je Formation und `9.120` je voll belegter
  read-only Probe;
- maximal 5.568 numerische Zustandswerte beziehungsweise 44.544 logische
  Float64-Bytes;
- den weiterhin gebundenen Hauptumfang `15/3/72/43.680`;
- keine RGB-/PCM-Bytes in Memoryzustand, Formationreceipt oder read-only
  Finding;
- keine Kompression auf 26 Werte, keine dritte Memoryebene, keine
  Kontextauswahl und keinen Feldrueckweg.

## Quellhashes nach Qualifikation

| Quelle | SHA-256 |
| --- | --- |
| aktive private Envelopebindung | `0a1b6ddf13f13773a68914a6e42c7bdfb582dd8b07dc2ea2e44cf2a8e67de32f` |
| Profiladapter | `ad5c8f607bc375daa8a6ed70134f6ed716780658a2a5e88bddb77a980da1af6f` |
| AV-Paarung | `4ec7d8660bb2269f858db8a025749764b193cd3511934b9ae143bb07359958db` |
| Ledgeradapter | `995c064e32dba313d6d8329ed9c661402ce77185143f2d62b95380b777da2f80` |
| atomarer Koordinator | `c9676ea9a740bfb82d66a91c00c559d1ff4d3759bd7bfed12c55afb9820dea81` |
| read-only Adapter | `efd3dad03810811acc3fc124543bf8aa524ad1de4585210f2852f7048dbf93e7` |
| Qualifikationstest | `1eb243f01877b5916ca1433574291a88b9a83c0b1328649b72cd90e7e1cb9767` |

README, API, Snapshot, Feldpfad, Kontextmodule und die unversionierte
Bootstrap-Datei wurden nicht veraendert.

## Naechste Entscheidung

Die privaten Adapter sind fuer den einmaligen S2-JV-Funktionslauf technisch
qualifiziert. Separat freizugeben bleibt genau die gebundene Frage, ob D9 als
juengster Inhalt, X als stabil verdichteter Inhalt und Y als kontrolliert
vergessener Inhalt aus dem real erzeugten 336-Werte-Profil hervorgehen.
