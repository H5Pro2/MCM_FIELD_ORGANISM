# S2-GL: Rezeptorrealistische Fixture- und Laufmaterialisierung

## Auftrag und Grenze

S2-GL korrigiert ausschliesslich die noch nicht materialisierbaren Teile des
S2-GJ-Vertrags. Die private S2-GK-Implementierung bleibt unveraendert und
qualifiziert.

Der Vertrag bindet erzeugbare Bildquellen, vier endliche Bildungsgeschichten,
Quellen- und Digestrollen sowie vollstaendige Laufbudgets. Er erlaubt keine
Fixture-, Runner- oder Recorderimplementierung und keine Ausfuehrung.

Die in S2-GJ genannten konstanten D-Vektoren von `-1.0` bis `1.0` werden fuer
eine spaetere Ausfuehrung verworfen. Sie sind nicht vollstaendig durch den
bestehenden visuellen Rezeptor erzeugbar und duerfen nicht hinter dem Rezeptor
eingesetzt werden.

## Gebundener technischer Ausgangsstand

`LocalChannelGridReceptor` akzeptiert ausschliesslich `uint8`-Bilder mit der
gebundenen Form `(80, 120, 3)`. Die Konfiguration lautet:

```text
VisualGridConfig(120, 80, 3, 2, 30.0)
geometry_id = visual.grid3x2.channels3.source120x80.v1
carrier_count = 18
```

Jede der sechs Zellen ist `40 x 40` Pixel gross. Der Rezeptor bildet pro Zelle
und Kanal den Mittelwert und teilt ihn durch `255`. Seine Ausgabewerte liegen
daher zwingend in `0.0 .. 1.0`.

Gebundene Quellbelege:

| Rolle | SHA-256 |
| --- | --- |
| visueller Rezeptor | `d09cb6ba35fd061e4a243b7ed2112597a194e75abd026d7cc3ab7aa89922c07a` |
| privater B4-/TSPM-Koordinator | `95ee05ccc0eeb14abbcda036971da5c33ac79363dd546789f4878aace5677db0` |
| S2-GC-Bundleprojektion | `0fba7b0323fe772c481eb5261b9640e4a5b00d7da3ceb1a7e0f81c6d9f54bf49` |
| S2-GI-A/B-Projektion | `21bc206dc37f8a9f477c02eac7d14ff22e6924bbdb54eb5153122ec296cdd587` |
| S2-GK-Verbraucher | `29c16372184bec0092fadf777adc7b7e1c9a5ba0529711c46ca75c92c4769832` |
| S2-GK-Direktbaseline | `43ac94ca59a1157893cdc96cd4b980a0fb348130bc670596bbd3d65e112d7958` |
| S2-GK-Auswerter | `ac33ed97b670681250cb709b40332024ab107365836cd5641d27e34ee85e5cf5` |
| TSPM-1-Kern | `321ce786c42edd217dc6dbf2210c495016b2babaa78d53449a13b0039965d516` |
| PPB-1-Kern | `15f1fabaa45348f067b7bf466f138d275d74f75a6e98afc05867f7b8c35d46f0` |

Eine spaetere Implementierung muss diese Belege neu gegen die tatsaechlichen
Quellbytes binden. Eine Abweichung ist kein Funktionsbefund, sondern stoppt
vor dem ersten Rezeptoraufruf.

## Kanonische Bilderzeugung

Jedes Bild wird durch genau 18 Bits beschrieben. Die Reihenfolge ist:

```text
row 0, column 0, channel 0..2,
row 0, column 1, channel 0..2,
row 0, column 2, channel 0..2,
row 1, column 0, channel 0..2,
row 1, column 1, channel 0..2,
row 1, column 2, channel 0..2
```

Ein Bit `0` erzeugt in dem gesamten Zellkanal den Wert `0`, ein Bit `1` den
Wert `255`. Das resultierende Bild ist ein unveraendertes
`uint8[80,120,3]`. Der Rezeptorausgang ist dadurch exakt derselbe 18-Werte-
Vektor mit den Werten `0.0` und `1.0`. Es gibt keinen nachtraeglich
eingesetzten Rezeptorwert.

### Ziel- und Kontrollbilder

| ID | 18 Bits | SHA-256 der 28.800 Rohbytes |
| --- | --- | --- |
| `J1-T` | `100110011001100110` | `36b9c3295ab4130569bf69abe8375c8358c112cf016935478b62a0a81d4f94a9` |
| `J1-F` | `110011001100110011` | `8b06a64ad2b4c589a0eb32ce90bb2546ce06ea5cab00db4cc377210568e0db7e` |
| `J1-C` | `000110011001100110` | `c4c7ba6d0da052425937c0888b7b2c222abf04f051073bd600782329fb5fa01e` |

`J1-T` und `J1-F` bleiben an allen sichtbaren Positionen gleich und an allen
maskierten Positionen verschieden. `J1-C` widerspricht weiterhin nur an der
sichtbaren Position `0`.

### Neun Distraktoren fuer die drei stabilen Kontexte

| ID | 18 Bits | SHA-256 der Rohbytes |
| --- | --- | --- |
| `D1` | `111111100000000000` | `acbf5d3052e7bdd25027cddd46d11991e42e585e1599ed58628f5dcabb15fb16` |
| `D2` | `111100011100000000` | `162f321fe3aeaa2b9a20aaf36ca46197361987df1552b9acfeb972b79e9ee9e8` |
| `D3` | `111100000011100000` | `79d82f14640e3a78b0ee8d1fc73d7516d07befd8c73cdbf5e8daa1a6d4479053` |
| `D4` | `111100000000011100` | `4c4809a51aba4bdc718c73e8f9e8b01ba69ee9426497912088b97e201111722c` |
| `D5` | `111010010010010000` | `2c26c0f64bb0d0b7018328d8273b4bea46c8d616bc26e129267093d0328afd21` |
| `D6` | `111010001001001000` | `f668dcc5677dd625e2acc2a72cb00c71e432489ef1ae8492ceb491d31597c8c0` |
| `D7` | `111010000100100100` | `92ded1eb1875494e94256cc633fbc543e0ba921d8699792903b52f740315eeea` |
| `D8` | `111001010001000100` | `115596e84cba8d0d5ffeb018aa45b0eeb3460d1e38d84610e3b3fe237c2ec6b0` |
| `D9` | `111001001010000010` | `52354f306a7010fe295fc3f4d02dae3e464c070b481a9f2ccd3c87bfc18f247b` |

### Dreizehn einmalige Quellen fuer `K_ABSENT`

| ID | 18 Bits | SHA-256 der Rohbytes |
| --- | --- | --- |
| `A1` | `111001000100010001` | `75b780558aea7c28a595d6ecbfb524f582cb50e408c6df340e4a8f6d41d1ad03` |
| `A2` | `111000110000101000` | `06862a7ef902262606f27ec27b8ad83c984dfbdc49fe4fb78b3b63a5a2a2cde5` |
| `A3` | `111000101000000101` | `31799ae00e8a698b3b7611aedfd26134d698ac9123a7cb9167ea9f27eb9ee301` |
| `A4` | `111000100101000010` | `84f7d6ae1b5664ad249b4e5675922661e95dc32b5e6b8741c13dc048a2a1dc46` |
| `A5` | `110110010001000001` | `1b2eefbc9bfd21520b6bb0b5454905e78bfa87eec6548cfec7a5fc15c7b26090` |
| `A6` | `110110001010000100` | `220babcdacc05a1c8faad77042cb96c9ab68da0b1c2127bdb96d97ff839e2b74` |
| `A7` | `110110000100010010` | `ced8867f594bbad2e915372b8ea49ccb9be1dcbb99b3167440fda6e3d6be7478` |
| `A8` | `110101010010001000` | `aa180051bec55126a890742b05f25b263795f99a5294ba9795837606a5cf7647` |
| `A9` | `110101001001010000` | `34c497af454e7113c4e5a3e30d3e8821a6c4a1703f866937fd0e859cc9cd4ee2` |
| `A10` | `110101000000100110` | `c3f0e1c3ede5264caeecc4f5a2c24cc2a22c25dfc8c3802839eb570c297ad446` |
| `A11` | `110100101000001010` | `c4af8113278e754be39bbfd86c60ce8501ff61b5f5897fef674798672ca0f2c1` |
| `A12` | `110100100110000001` | `6363776eb2805268e0f32d780a766e258fcc6d5ffd78489c963a37b16b555fd8` |
| `A13` | `110011011000100000` | `1664ac5850c81a523c2ecfd7d6b8785d7a4968de11ca1352dfff69cfcbd3c715` |

Der kanonische Fixture-Set-Digest ueber Schema, Geometrie, IDs, Bits und
Rohbytedigests lautet:

`0e9f26180b1f392a10fa727a5f320d2a2f2be1da8dc686cc4f82534a56d3a789`

## Abstandsbindung

Es gilt die normalisierte L1-Distanz ueber 18 visuelle Werte.

| Menge | kleinster Hammingabstand | normalisierte L1-Distanz |
| --- | ---: | ---: |
| `D1..D9` untereinander | `6` | `6/18 = 1/3` |
| `A1..A13` untereinander | `6` | `6/18 = 1/3` |
| alle 22 Distraktoren untereinander | `6` | `6/18 = 1/3` |
| jeder Distraktor gegen `J1-T/F/C` | `5` | `5/18` |

Damit liegen alle Distraktorabstaende strikt ueber:

- der nativen visuellen TSPM-/PPB-Grenze `1/5 = 0.2`;
- der funktionalen B4-Grenze `44/765`.

`J1-T` gegen `J1-C` bleibt absichtlich `1/18`: Der spaetere S2-GK-
Verbraucher erkennt den sichtbaren Konflikt durch exakten Vergleich, nicht
durch eine neue Matchschwelle.

## Auditive Bindung

Auditive Werte bleiben synthetische Rezeptorzustaende und werden nicht als
analysiertes Audiosignal bezeichnet. Jede Maske besitzt vier Einsen:

```text
Q0  = 11110000
Q1  = 11101000   Q2  = 11100100   Q3  = 11100010
Q4  = 11100001   Q5  = 11011000   Q6  = 11010100
Q7  = 11010010   Q8  = 11010001   Q9  = 11001100
Q10 = 11001010   Q11 = 11001001   Q12 = 11000110
Q13 = 11000101
```

Verschiedene Masken besitzen mindestens `2/8 = 0.25` Abstand und liegen
damit ebenfalls ueber `0.2`.

In den drei stabilen Kontexten verwenden die vier J-Expositionen `Q0`, die
neun D-Expositionen `Q1..Q9`. In `K_ABSENT` werden `Q1..Q13` jeweils genau
einmal verwendet. Dadurch hat `K_ABSENT` weder eine wiederholte auditive noch
eine wiederholte visuelle Fast-Quelle und kann keinen Slow-Prototyp bilden.

## Vier vollstaendige Bildungsgeschichten

Jede Geschichte beginnt mit einem frischen Composite-Zustand. Fuer Schritt
`n` gilt exakt das Fenster `[n-1, n]`, `n = 1..13`.

| Schritt | `K_CORRECT` | `K_FOREIGN` | `K_CONFLICT` | `K_ABSENT` | Audio stabil/D | Audio absent |
| ---: | --- | --- | --- | --- | --- | --- |
| 1 | `J1-T` | `J1-F` | `J1-C` | `A1` | `Q0` | `Q1` |
| 2 | `J1-T` | `J1-F` | `J1-C` | `A2` | `Q0` | `Q2` |
| 3 | `J1-T` | `J1-F` | `J1-C` | `A3` | `Q0` | `Q3` |
| 4 | `J1-T` | `J1-F` | `J1-C` | `A4` | `Q0` | `Q4` |
| 5 | `D1` | `D1` | `D1` | `A5` | `Q1` | `Q5` |
| 6 | `D2` | `D2` | `D2` | `A6` | `Q2` | `Q6` |
| 7 | `D3` | `D3` | `D3` | `A7` | `Q3` | `Q7` |
| 8 | `D4` | `D4` | `D4` | `A8` | `Q4` | `Q8` |
| 9 | `D5` | `D5` | `D5` | `A9` | `Q5` | `Q9` |
| 10 | `D6` | `D6` | `D6` | `A10` | `Q6` | `Q10` |
| 11 | `D7` | `D7` | `D7` | `A11` | `Q7` | `Q11` |
| 12 | `D8` | `D8` | `D8` | `A12` | `Q8` | `Q12` |
| 13 | `D9` | `D9` | `D9` | `A13` | `Q9` | `Q13` |

Die Quellen-ID lautet kanonisch
`s2gl.<context>.formation.<nn>`. Sie bindet Kontext, Schritt, Fenster,
Bild-ID, Rohbytedigest, auditive Maske, Konfiguration und Fixture-Set-Digest.
Sie ist niemals ein Match-, Ziel- oder Auswahlmerkmal.

Nach Schritt 13 erhaelt jeder Kontext genau eine volle read-only Probe mit
dem real analysierten Bild `J1-T`, `Q0` und dem Fenster `[13,14]`. Die
kanonische ID lautet `s2gl.<context>.probe.full.01`.

Erwartete, noch nicht ausgefuehrte Endanatomie:

- `K_CORRECT`, `K_FOREIGN`, `K_CONFLICT`: B4 und Fast enthalten den
  wiederholten J-Zustand nicht mehr; Slow enthaelt den jeweiligen stabilen
  auditiven und visuellen Kandidaten mit Support `3`;
- `K_ABSENT`: B4 und Fast liefern fuer `J1-T/Q0` keinen Treffer, beide
  Slow-Baenke bleiben ohne stabilen Kandidaten;
- eine Abweichung ist ein spaeteres fachliches Ergebnis, keine Erlaubnis zur
  Aenderung von Bildern oder Schwellen.

## Maskierte Probe und Digestrollen

Die spaetere Teilprobe wird aus der bereits real analysierten vollen
`J1-T`-Probe des `K_CORRECT`-Probevorgangs abgeleitet:

```text
VISIBLE = (0, 2, 4, 6, 8, 10, 12, 14, 16)
MASKED  = (1, 3, 5, 7, 9, 11, 13, 15, 17)
Marker  = None
```

Der Marker ist ausschliesslich private Probeanatomie. Er wird weder an den
visuellen Rezeptor noch an einen Speicheroperator uebergeben. Es gibt genau
56 reale visuelle Analysen: 52 Bildungseingaben und vier volle
Kontextproben. Die Maskierung erzeugt keine 57. Rezeptoranalyse.

Der kanonische Digest der Teilprobenquelle ueber Fixture-Set, `J1-T`-
Rohbytedigest, Maske, sichtbare Werte und Markerrolle lautet:

`4ba6dbcb31eea7ddb198a442e699aa7f73ee8785c494cbede92a2526b9385f81`

Eine spaetere Materialisierung muss folgende Digestkette ohne Abkuerzung
erzeugen und pruefen:

```text
Bildbytes -> Bild-SHA-256 -> Rezeptorzustandsdigest
-> zeitgebundener Quelldigest -> Composite-Schritt-Receipt
-> Composite-Endzustandsdigest -> read-only Findingdigest
-> S2-GC-Bundledigest -> S2-GI-Bundledigest
-> S2-GK-Bindingdigest -> Armresultatdigest -> Auswertungsdigest
```

Laufzeitabhaengige Zustands-, Bundle- und Resultatdigests werden nicht
vorweggenommen. Sie muessen aus den tatsaechlich gebildeten Artefakten
stammen. Fremde, vertauschte oder aus einer anderen Geschichte stammende
Digests stoppen vor dem Verbraucher.

## Exakter spaeterer Operationsumfang

Die vier Geschichten und sieben S2-GJ-Faelle ergeben genau:

| Operation | Anzahl |
| --- | ---: |
| reale visuelle Rezeptoranalysen | `56` |
| atomare Composite-Bildungen | `52` |
| native Composite-read-only Proben | `4` |
| S2-GC-Projektionen | `4` |
| S2-GI-Projektionen | `4` |
| `CURRENT_PERCEPTION_ONLY` | `1` |
| S2-GK-Kontextverbraeuche | `4` |
| direkte Maskenfuellbaselines | `2` |
| reine Fallauswertungen | `4` |
| **gesamt** | **`131`** |

Eine spaetere append-only Aufzeichnung besitzt damit genau `262`
verkettete `START`-/`RESULT`-Ereignisse. Die sieben Armresultate bleiben
`GJ-01..GJ-07`; die vier Auswertungen sind `CORRECT`, `FOREIGN`, `ABSENT`
und `CONFLICT`.

## Ressourcen-, Speicher- und Vergleichsbudget

### Rezeptor und Quellen

- ein Bild: `80 * 120 * 3 = 28.800` Rohbytes;
- 25 eindeutige gebundene Bilder: `720.000` Rohbytes, falls gemeinsam
  materialisiert;
- spaeter analysierter Bilddurchsatz: `56 * 28.800 = 1.612.800` Rohbytes;
- maximal ein Bild muss gleichzeitig als Rohbild gehalten werden;
- Rohbilder werden nicht in B4, TSPM-1, Bundle oder Resultat gespeichert;
- 56 AV-Rezeptorzustaende enthalten jeweils `8 + 18 = 26` Werte.

### Composite-Bildung und read-only Speicherprobe

Die unveraenderten S2-FS-Ledger ergeben:

| Rolle | Anzahl | Write-Woerter | Distanzterme | Kontrollterme |
| --- | ---: | ---: | ---: | ---: |
| Formation je Schritt | `52` | `32.084` | `24.336` | `2.808` |
| read-only je Kontext | `4` | `56` | `1.872` | `192` |
| **gesamt** | **`56`** | **`32.140`** | **`26.208`** | **`3.000`** |

Grundlage je Formation ist `617/468/54`, je read-only Probe `14/468/48`.
Das sind vertragliche Funktionszaehler, keine Messung von Prozess-RAM oder
Laufzeit.

### S2-GC- und S2-GI-Projektion

Kurzfolge ist fuer diese Aufgabe `NOT_REQUESTED` und besitzt null
Sequenzreferenzen.

| Projektion | Evidence | validierte Digests | Kandidaten | Komponenten | Werte | Digestoperationen |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| drei stabile Kontexte zusammen, S2-GC | `39` | `30` | `3` | `6` | `78` | `27` |
| `K_ABSENT`, S2-GC | `11` | `8` | `0` | `0` | `0` | `6` |
| alle vier, S2-GI | `4` Bundles | `12` Rollen | `3` | `6` | `78` | `16` |

Jeder tatsaechliche Projektionsledger muss diese Werte bestaetigen. Eine
abweichende reale Zustandsanatomie macht den Lauf `NOT_EVALUABLE`; sie darf
nicht durch Sollwerte erzwungen werden.

### Sieben S2-GJ-Armresultate

Die unveraenderten Verbraucher- und Baselineledger summieren sich zu:

| Zaehler | Gesamt |
| --- | ---: |
| Maskenvalidierungen | `126` |
| sichtbare Wertevergleiche | `45` |
| Maskenuebernahmen | `36` |
| Bereichszugriffe | `6` |
| Kandidatenreferenzen | `5` |
| Wertereferenzen | `99` |
| Digestoperationen | `14` |

Der reine Auswerter fuehrt genau vier Fallauswertungen, `36` sichtbare
Zielwertpruefungen, `54` absolute Fehlerterme fuer die zwei vollstaendig
gefuellten Faelle, `36` Wertgleichheitspruefungen zwischen Verbraucher und
Direktbaseline sowie `14` Ledgergleichheitspruefungen aus. Zielwerte werden
erst in diesen vier Auswertungsoperationen sichtbar.

## Fail-Closed- und Falsifikationsregeln

`NOT_EVALUABLE` gilt insbesondere bei:

- einem Wert ausserhalb `0.0..1.0` am visuellen Rezeptorausgang;
- einem abweichenden Bild-, Quellen-, Konfigurations- oder Zustandsdigest;
- einem Distraktorabstand von hoechstens `0.2`;
- einer Wiederholung oder Slow-Stabilisierung in `K_ABSENT`;
- fehlenden 13 Schritten, vertauschten Ticks oder nicht frischen Zustaenden;
- Maskenmarkern im Rezeptor- oder Speichereingang;
- abweichenden Operations-, Ereignis- oder Ressourcenledgern;
- Teilaufzeichnung, Wiederverwendung oder nachtraeglicher Rekonstruktion.

Fachlich falsche, aber vollstaendig und methodisch korrekt gebildete Abrufe
bleiben Ergebnisse. Sie stoppen nicht technisch und duerfen nicht durch eine
nachtraegliche Fixture-, Schwellen- oder Bewertungsanpassung korrigiert
werden.

## Nicht freigegeben

S2-GL erlaubt nicht:

- Fixture-, Runner-, Recorder- oder Verifikatorcode;
- Tests oder Projektfunktionsaufrufe;
- Rezeptor-, Speicher-, Kontext- oder Feldausfuehrung;
- Aenderungen an S2-GK, B4, TSPM-1, PPB-1, API, Snapshot oder Feldpfad;
- einen Funktions-, Memory- oder Feldwirkungsbefund.

## Statische Entscheidung

Die vier Geschichten sind mit dem bestehenden visuellen Rezeptor und den
nativen Matchgrenzen widerspruchsfrei materialisierbar. Die zuvor ungueltigen
negativen D-Werte sind durch konkrete, digestgebundene `uint8`-Bildquellen
ersetzt. `K_ABSENT` besitzt eine vollstaendige budgetgleiche Geschichte ohne
wiederholte AV-Quelle.

Status:

`PASS_S2GL_STATIC_RECEPTOR_REALISTIC_MATERIALIZATION_CONTRACT_BOUND`

Vor jeder Implementierung ist ein enger statischer Materialisierungs- und
Nichtzirkularitaetsaudit dieses Vertrags erforderlich. Runner und sieben
GJ-Faelle bleiben bis zu einer neuen ausdruecklichen Freigabe gesperrt.
