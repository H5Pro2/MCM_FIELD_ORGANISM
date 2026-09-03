# S2-KO - Statischer Erreichbarkeitsaudit der realen 336-Werte-Kontextzulassung

## Status und Grenze

`S2KO_STATIC_REAL_336_CONTEXT_ADMISSION_REACHABILITY_CONFIRMED`

S2-KO prueft rein statisch, ob die sechs fachlich gebundenen
Zulassungszustaende aus echten, durch die unveraenderten Rezeptoren gebildeten
336-Werte-Memorygeschichten erreichbar sind. Der Audit fuehrt keine
Rezeptor-, Memory-, Kontextverbraucher- oder Feldfunktion aus. Er erzeugt
keinen Runner, Recorder und keinen neuen Funktionsbefund.

Die bestehende S2-KN-Zulassungslogik bleibt unveraendert. B4 und Fast sind
interne Evidenzrollen von `A_RECENT`; oeffentlich existieren weiterhin exakt
`A_RECENT` und `B_STABLE`.

## Gebundener Ausgangsstand

Technischer Ausgangsstand ist Commit
`989ba278ba7d50433ef491c5a12d3ad98093a9f9`.

| Rolle | Quelle | SHA-256 |
| --- | --- | --- |
| qualifizierte Zwei-Bereich-Zulassung | `tools/_s2kn_private_two_area_context_admission_336.py` | `15ccfa47195887a590b0609fbad9def93c5cd48222254a7a688fb173b14930eb` |
| unabhaengige Direktbaseline | `tools/_s2kn_private_direct_two_area_admission_baseline.py` | `6071a5390ecf9200f472c0ab4e444e2acf2f1e54f8ac52fca078dbfd6c3d7939` |
| qualifizierte neutrale Tests | `tests/test_s2kn_private_two_area_context_admission_336.py` | `15f88c9a99dc8490ab81500e572543fa125bcc877a58e88f6b92bff39a1102b8` |
| Default-Live-Profil | `tools/_s2jw_default_live_profile.py` | `ad5c8f607bc375daa8a6ed70134f6ed716780658a2a5e88bddb77a980da1af6f` |
| atomarer 336-Werte-Koordinator | `tools/_s2jw_profiled_memory_coordinator.py` | `c9676ea9a740bfb82d66a91c00c559d1ff4d3759bd7bfed12c55afb9820dea81` |
| read-only 336-Werte-Auswertung | `tools/_s2jw_profiled_memory_read_only.py` | `efd3dad03810811acc3fc124543bf8aa524ad1de4585210f2852f7048dbf93e7` |
| TSPM-1-Kern | `mcm_field_organism/_tspm1_private.py` | `321ce786c42edd217dc6dbf2210c495016b2babaa78d53449a13b0039965d516` |
| B4-Referenzschritt | `mcm_field_organism/_tspm1_s2dr_private_comparison.py` | `96cdd018be34afe67de0139428fed5254cff945ba74db98163a91273f5d21b2c` |
| PPB-1-Kern | `mcm_field_organism/_ppb1_reference.py` | `15f1fabaa45348f067b7bf466f138d275d74f75a6e98afc05867f7b8c35d46f0` |
| gebundene reale S2-JX-Fixtures | `tools/_s2jx_default_live_memory_fixtures.py` | `5313888d81b946c7ca87f6cf140a04d7810fdb0ecd1eaa0650e9fc1bb1854936` |
| bestaetigter S2-JX-Lauf | `reports/s2jx_default_live_memory/s2jx-default-live-memory-20260902-01/result.json` | `0ed7b62c873603feefde3e5cf4ed949cfc1323ff36e0adc22d58a4ccc8a92547` |

## Unveraenderte mechanische Regeln

Der Audit verwendet ausschliesslich die vorhandenen Regeln:

- B4 speichert jeden akzeptierten AV-Zustand unveraendert mit seinem
  `formation_index` und behaelt die neun juengsten Eintraege.
- TSPM-Fast akzeptiert einen gemeinsamen Treffer nur bei auditiver Distanz
  `<= 0.2` und visueller Distanz `<= 0.2`.
- Ein neuer Fast-Slot enthaelt die unveraenderten Eingangswerte und Support
  `1`.
- Ein Fast-Treffer wird mit Faktor `0.5` aktualisiert. Ab Support `2` wird
  genau ein PPB-Schritt ausgeloest.
- Ein Fast-Slot laeuft vor einer Formation ab, sobald
  `step - last_selected_step >= 8` gilt.
- Visuelles PPB-Matching verwendet unveraendert `0.01`; ein Slow-Prototyp
  ist ab Support `3` stabil.
- Alle Proben sind read-only. Kandidaten werden nur aus belegten Slots und
  deren gespeicherten Werten gebunden.

Die S2-KN-Sichtbarkeitspruefung und ihre feste unabhaengige Maske bleiben
unveraendert. Keine neue Schwelle oder Gleichheitsregel wird eingefuehrt.

## Bereits real erzeugte Referenzzustaende

Der vollstaendig verifizierte S2-JX-Lauf bildet die Geschichte

```text
X X X X Y Y D1 D2 D3 D4 D5 D6 D7 D8 D9
```

aus realen `1920 x 1080 RGB8`-Bildern und echten `PCM_F32LE`-Fenstern durch
die unveraenderten Default-Live-Rezeptoren. Sein finaler Zustandsdigest ist
`1e62a53b6a6721af59f554428ed72154292769c87380fb6970f5718c759a766e`.

Die gespeicherten read-only Befunde belegen:

| Vollprobe | B4 | Fast | stabiles visuelles Slow |
| --- | --- | --- | --- |
| `D9` | Treffer, Formation 15, Distanz 0 | Treffer, Support 1, Distanz 0 | abwesend |
| `X` | abwesend | abwesend | Treffer, Support 3, Distanz 0 |
| `Y` | abwesend | abwesend | kein stabiler Treffer; interne Spur Support 1 |

Bei `D9` stammen B4 und Fast aus derselben unmatched Formation. B4 legt den
Eingangstupel unveraendert ab; `FAST_CREATED` beziehungsweise
`FAST_REPLACED` legt denselben auditiven und visuellen Eingangstupel
unveraendert ab. Der spaetere Distanz-0-Doppeltreffer ist deshalb ein
erreichbarer wertgleicher A-Befund mit zwei getrennten Herkunftsbelegen.

Damit sind drei der sechs S2-KO-Faelle bereits durch einen abgeschlossenen
realen Lauf belegt. Der Audit repariert oder erweitert dessen Ergebnisdatei
nicht.

## Prospektive reale Minimalfixtures

Die drei noch fehlenden Zustaende werden nicht als Kandidatenvektoren hinter
dem Rezeptor eingesetzt. Sie werden durch konkrete erzeugbare Quellen und
echte Formation histories gebunden.

Alle neuen visuellen Quellen sind `1920 x 1080 x 3`-`uint8`-Bilder im
Default-Live-Raster. Jeder der 288 Kanalbloecke ist `160 x 135` Bytes gross
und blockkonstant. Der unveraenderte visuelle Rezeptor liefert daher fuer
einen Blockbytewert `k` exakt `k/255`.

Die festen visuellen Zustandsrollen lauten:

| Zustand | Blockwerte der 288 visuellen Carrier |
| --- | --- |
| `B0` | alle Carrier `0` |
| `A0` | wie `B0`, nur Carrier 32 ist `1` |
| `C0` | identisch zu `B0` |
| `C1` | wie `C0`, nur Carrier 32 ist `2` |

Alle vier Rollen verwenden echte, strikt fortgeschriebene 100-ms-
`PCM_F32LE`-Fenster nach der bereits gebundenen S2-JV-X-Rezeptur. Gleicher
Inhalt darf erneut auftreten; Blockindex, Samplefenster, Frameindex,
Zeitbindung und Quelldigest bleiben pro Exposition neu und eindeutig. Die
neun Druckzustaende verwenden die unveraenderten realen S2-JX-Fixtures
`D1..D9`.

Fuer die Zulassungsprobe bleiben die 32 visuellen Positionen `0..31`
beobachtet; die Positionen `32..287` sind durch den unabhaengigen Maskenbeleg
maskiert. Die Maske wird nicht aus Werten abgeleitet.

### Exakte relevante Distanzen

```text
d_visual(B0, A0) = 1 / (288 * 255) = 1/73440
d_visual(C0, C1) = 2 / (288 * 255) = 1/36720
Fast(C0 -> C1), Carrier 32 = 0.5 * 0 + 0.5 * (2/255) = 1/255
d_visual(Fast-Mittel, C1) = 1/73440
```

Alle Werte liegen unter Fast `0.2`; `B0/A0` liegt auch unter visuell Slow
`0.01`. Die Unterschiede liegen ausschliesslich auf der maskierten Position
32. Die neun S2-JX-Druckbilder besitzen gegen ein Nullbild mindestens 130
aktive von 288 Carriern. Selbst bei der einen abweichenden A0-Position bleibt
ihre visuelle Distanz groesser als `0.45` und damit sicher oberhalb der
Fast-Grenze `0.2`. Untereinander liegen die gebundenen S2-JX-Distanzen bei
`13/24` bis `79/144`.

Diese Beziehungen folgen vollstaendig aus ganzzahligen Blockbytes und der
Rezeptorformel. Sie sind keine handgeschriebenen Memorywerte und keine neue
Wahrnehmungskalibrierung.

## Sechs erreichbare Zulassungsfaelle

### R1 - nur A anwendbar, B4 und Fast wertgleich

Gebundene reale Geschichte und Zustand: finaler S2-JX-Zustand, Vollprobe
`D9`, danach eine strikt spaetere maskierte D9-Probe.

- B4 und Fast waehlen den unveraendert gespeicherten D9-Zustand.
- Beide internen A-Rollen sind wertgleich und auf allen sichtbaren Positionen
  anwendbar.
- Es existiert kein stabiler visueller B-Treffer.
- Oeffentlich entsteht genau ein `A_RECENT`-Kandidat mit zwei
  Herkunftsbelegen.
- Erwartete Entscheidung: `ADMIT_SINGLE_CONTEXT`, Hypothesenquelle
  `A_RECENT`.

### R2 - nur B anwendbar

Gebundene reale Geschichte und Zustand: finaler S2-JX-Zustand, Vollprobe
`X`, danach eine strikt spaetere maskierte X-Probe.

- B4 und Fast sind abwesend.
- Der visuelle Slow-Prototyp trifft mit Support `3` und Distanz 0.
- Erwartete Entscheidung: `ADMIT_SINGLE_CONTEXT`, Hypothesenquelle
  `B_STABLE`.

### R3 - A und B anwendbar

Prospektive reale Geschichte:

```text
B0 B0 B0 B0 D1 D2 D3 D4 D5 D6 D7 D8 D9 A0
```

- B0 erzeugt nach vier identischen Expositionen einen stabilen visuellen
  Slow-Prototyp mit Support `3`.
- Der B0-Fast-Slot laeuft vor Schritt 12 ab; nach neun Druckzustaenden ist B0
  auch aus dem B4-FIFO entfernt.
- A0 passt wegen der visuellen Distanz groesser `0.45` zu keinem verbliebenen
  D-Slot und wird in B4 und Fast unveraendert neu angelegt.
- A0 erzeugt keinen weiteren PPB-Schritt; der B0-Prototyp bleibt unveraendert.
- Die A0-Vollprobe liefert wertgleiche B4-/Fast-Evidenz und den bestehenden
  B0-Slow-Kandidaten. Auf den sichtbaren Positionen `0..31` sind beide
  Bereichskandidaten identisch; ihre einzige Abweichung liegt maskiert auf
  Position 32.
- Erwartete Entscheidung: `ABSTAIN_AMBIGUOUS_CONTEXT`.

### R4 - interner A-Konflikt

Prospektive reale Geschichte:

```text
C0 C1
```

- B4 speichert C1 exakt mit Carrier 32 gleich `2/255`.
- Fast aktualisiert den C0-Slot mit Faktor `0.5` auf Carrier 32 gleich
  `1/255`.
- Beide internen Rollen treffen die C1-Vollprobe mechanisch und sind auf den
  sichtbaren Positionen `0..31` anwendbar.
- Ihre 288-Werte-Tupel sind verschieden. Der erste PPB-Schritt besitzt nur
  Support `1` und erzeugt keinen oeffentlichen B-Kandidaten.
- Erwarteter A-Befund: `A_RECENT_INTERNAL_CONFLICT`.
- Erwartete Entscheidung: `ABSTAIN_A_RECENT_INTERNAL_CONFLICT`.

Dieser Fall belegt insbesondere, dass ein realer Fast-Updatepfad und das
exakte B4-FIFO verschiedene, gleichzeitig anwendbare interne A-Werte erzeugen
koennen. Der Konflikt wird weder aus Labels konstruiert noch durch
Listenreihenfolge entschieden.

### R5 - kein vorhandener Kontext

Gebundene reale Geschichte und Zustand: finaler S2-JX-Zustand, Vollprobe
`Y`, danach eine strikt spaetere maskierte Y-Probe.

- B4 und Fast sind abwesend.
- Die vorhandene Slow-Spur besitzt nur Support `1` und ist nicht oeffentlich
  stabil.
- Gueltige oeffentliche Abwesenheit ist kein Evidenzfehler.
- Erwartete Entscheidung: `ABSTAIN_NO_CONTEXT`.

### R6 - vorhanden, aber sichtbar unpassend

Gebundene reale Geschichte und Zustand: finaler S2-JX-Zustand mit den
vorhandenen wertgleichen D9-B4-/Fast-Kandidaten.

Die strikt spaetere Probe ist ein echtes D9-Blockbild, bei dem nur der
beobachtete Carrier 0 von Byte `0` auf Byte `255` geaendert wird. Die
Positionen `0..31` bleiben beobachtet, `32..287` maskiert. Audio, Profil und
AV-Zeitbindung bleiben gueltig und strikt spaeter.

- Beide vorhandenen internen A-Kandidaten widersprechen der Probe an der
  sichtbaren Position 0.
- Es existiert kein anwendbarer B-Kandidat.
- A wird `A_RECENT_NOT_APPLICABLE`, nicht abwesend und nicht beschaedigt.
- Erwartete Entscheidung: `ABSTAIN_NO_APPLICABLE_CONTEXT`.

## Erreichbarkeitsmatrix

| Fall | reale Basis | oeffentlich A | oeffentlich B | erwarteter Ausgang |
| --- | --- | --- | --- | --- |
| R1 | ausgefuehrter S2-JX-D9-Zustand | ein Kandidat, B4/Fast gleich | keiner | `A_RECENT` zugelassen |
| R2 | ausgefuehrter S2-JX-X-Zustand | keiner | ein stabiler Kandidat | `B_STABLE` zugelassen |
| R3 | prospektive B0/D/A0-Geschichte | ein Kandidat | ein Kandidat | mehrdeutig, Enthaltung |
| R4 | prospektive C0/C1-Geschichte | interner Konflikt | keiner | interner Konflikt, Enthaltung |
| R5 | ausgefuehrter S2-JX-Y-Zustand | keiner | keiner | kein Kontext |
| R6 | ausgefuehrter S2-JX-D9-Zustand | vorhanden, unpassend | keiner | kein anwendbarer Kontext |

"Prospektiv" bedeutet hier nur, dass die konkrete Geschichte noch nicht
ausgefuehrt wurde. Ihre Kandidaten duerfen in einem spaeteren Funktionslauf
ausschliesslich durch die genannten echten RGB-/PCM-Quellen, unveraenderte
Rezeptoren und unveraenderte Memorykerne entstehen. Eine direkte
Kandidatenfixture waere vertragswidrig.

## Nichtzirkularitaet und spaetere Auswertung

Eine spaetere Laufplanung muss Formation und Auswertung trennen:

- Labels `R1..R6`, erwartete Entscheidungen und Sollbereiche sind nur
  Auswertungsmetadaten.
- Memoryeingaben enthalten ausschliesslich gebundene AV-Rezeptorzustaende,
  Zeit und technische Provenienz.
- Die Vollprobe erzeugt die read-only Memoryfindings. Die danach gebildete
  maskierte Zulassungsprobe ist eine eigene, strikt spaetere Quelle.
- Der Zulassungsfunktion werden weder Geschichte noch Sollstatus noch
  Zielwerte uebergeben.
- B4-/Fast-Wertgleichheit wird aus den tatsaechlich gebundenen Slotwerten und
  Digests nachgewiesen; der interne Konflikt aus den tatsaechlich
  verschiedenen Slotwerten.
- Pre- und Postdigests jeder Probe und Zulassung muessen identisch sein.

## Ergebnis und naechste Grenze

Alle sechs geforderten fachlichen Zustaende sind unter den bestehenden
Rezeptor-, B4-, Fast-, PPB- und S2-KN-Regeln erreichbar. Insbesondere sind
sowohl wertgleiche B4-/Fast-Evidenz als auch ein echter interner A-Konflikt
aus konkreten Formation histories ableitbar.

S2-KO bestaetigt nur die statische Erreichbarkeit. Es bestaetigt keinen neuen
realen Zulassungslauf. Fuer einen spaeteren kleinen Funktionslauf sind keine
neuen Schwellen, keine Feldwirkung und keine neue Runner-/Recorderarchitektur
begruendet; zu implementieren waeren hoechstens die prospektiven Rohfixtures
und eine minimale Wiederverwendung des vorhandenen privaten Ausfuehrungswegs.
