# S2-HP: Statischer Materialisierungs- und Nichtzirkularitaetsaudit

Status: `STATIC_AUDIT_PASS_ROLE_CONSUMER_IMPLEMENTATION_MAY_BE_REQUESTED`

## Gegenstand und Grenze

S2-HP prueft die in S2-HO gebundene Konfliktfixture gegen den vorhandenen
visuellen Rezeptor, die privaten B4-/TSPM-1-Zustaende sowie die S2-GC- und
S2-GI-Projektionen.

Es wurden keine Projektmodule importiert, keine Bilder durch den Rezeptor
ausgefuehrt, keine Speicher- oder Projektionsfunktion aufgerufen und keine
Tests oder Implementierungen angelegt. Bildbytes, Abstaende, Zustandsfolgen
und Digestkanten wurden ausschliesslich statisch hergeleitet.

## 1. Konkrete Bildmaterialisierung

Der reale technische Rezeptorpfad verlangt ein `numpy.ndarray` mit Typ
`uint8` und Form `80 x 120 x 3`. Bei der gebundenen Geometrie mit zwei
Rasterzeilen und drei Rasterspalten wird jeder Rezeptortraeger aus dem Mittel
eines `40 x 40`-Blocks und eines Farbkanals gebildet. Die 18 Ausgabewerte
werden in der Reihenfolge Rasterzeile, Rasterspalte, Kanal abgelegt.

S2-HO bindet fuer jeden der 18 Traeger einen konstanten Block. Der Mittelwert
eines konstanten `uint8`-Blocks ist sein ganzzahliger Blockwert. Nach der
Division durch `255` entstehen daher rechnerisch exakt folgende Werte:

```text
V0 = (1,0,0,1,1,0,0,1,1,0,0,1,1,0,0,1,1,0)

V1 = (1,1,0,0,1,0,0,1,1,0,0,1,1,0,0,1,1,0)

Q0 = (1,127/255,0,128/255,1,0,0,1,1,0,0,1,1,0,0,1,1,0)

Q1 = (1,128/255,0,127/255,1,0,0,1,1,0,0,1,1,0,0,1,1,0)
```

Die statisch gebundenen SHA-256-Digests der jeweils vollstaendig expandierten
`80 x 120 x 3`-Bildbytes lauten:

| Bild | SHA-256 |
|---|---|
| V0 | `36b9c3295ab4130569bf69abe8375c8358c112cf016935478b62a0a81d4f94a9` |
| V1 | `f73995c9ee54c8347d5884e515d1a18b1d418e4440c17c6419e55983a656925e` |
| Q0 | `9d0752305a2c2fc17b81c8df6cfef6ae8043a0fd7739b3876ba0ff5c4451dca0` |
| Q1 | `b748bf97f53f4e45e32a21c6387daea8fc005fbfa830c399095e43523f2817e9` |

V0 und V1 unterscheiden sich ausschliesslich an den maskierten Indizes `1`
und `3`. An allen anderen 16 Positionen sind die Bild- und Rezeptorwerte
identisch. Q0 und Q1 veraendern ebenfalls ausschliesslich diese beiden
maskierten Positionen.

### Fixture-Grenze

Die bestehende private S2-GT-`VisualFixture` akzeptiert nur `[01]{18}` und
der dortige Bildadapter erzeugt nur `0` oder `255`. Er kann Q0 und Q1 daher
nicht darstellen und darf fuer S2-HP nicht stillschweigend erweitert werden.

Die spaetere Umsetzung benoetigt eine getrennte private Byte-Block-Fixture
mit exakt 18 ganzzahligen Werten in `0..255`, fester Geometrie und gebundenem
Rohbilddigest. Das ist materialisierbar, weil der unveraenderte Kernrezeptor
bereits beliebige `uint8`-Bilder akzeptiert. Die alte S2-GT-Registry und ihr
Runner bleiben unveraendert.

## 2. Exakte Distanzpruefung

Mit normalisierter mittlerer L1-Distanz ueber 18 visuelle Werte gilt:

```text
d(V0,V1) = 1/9 = 85/765 = 255/2295

d(Q0,V0) = d(Q1,V1) = 127/2295
d(Q0,V1) = d(Q1,V0) = 128/2295

tau = 44/765 = 132/2295
2*tau = 88/765 = 264/2295
```

Damit ist statisch bestaetigt:

```text
127/2295 <= 132/2295
128/2295 <= 132/2295
132/2295 < 255/2295 <= 264/2295
```

Die beiden Vollproben liegen somit zu beiden Kandidaten innerhalb der
unveraenderten visuellen Funktionsschwelle. Die Kandidaten selbst bleiben
oberhalb dieser Schwelle getrennt. Q0 bevorzugt V0 um genau `1/2295`, Q1
bevorzugt V1 um denselben Betrag. Ueber beide Richtungen ist die
Quantisierung gespiegelt.

Fuer die auditiven Werte gilt unveraendert:

```text
d(M0,M1) = 1/4 > 1/5
d(MQ,M0) = d(MQ,M1) = 1/8 <= 1/5
```

`MQ` ist durch den vorhandenen `ReceptorContactFrame` darstellbar, weil seine
acht Werte endlich sind und im normalisierten Bereich liegen. Es bleibt als
synthetischer auditiver Rezeptorzustand gekennzeichnet und wird nicht als
analysiertes Audiosignal ausgegeben.

## 3. Bildung von B und Aktualitaet von A

Fuer beide spiegelbildlichen Geschichten ergibt die vorhandene TSPM-Logik:

| Schritt | Eingang | Fast-Ereignis | PPB-Schritt je Modalitaet | B-Slow-Support |
|---|---|---|---|---|
| 1 | B | `FAST_CREATED` | 0 | 0 |
| 2 | B | `FAST_UPDATED` | 1, Erzeugung | 1 |
| 3 | B | `FAST_UPDATED` | 1, Aktualisierung | 2 |
| 4 | B | `FAST_UPDATED` | 1, Aktualisierung | 3 stabil |
| 5 | A | `FAST_CREATED` mit partiellem visuellen Konflikt | 0 | 3 unveraendert |

Die visuelle Distanz A gegen B liegt zwar innerhalb der Fast-Schwelle `1/5`.
Die auditive Distanz `1/4` liegt jedoch darueber. Es entsteht deshalb kein
gemeinsamer audiovisueller Fast-Match. A erhaelt einen zweiten Slot und ist
nicht konsolidierungsfaehig.

Nach Schritt 5 gilt:

- B4 enthaelt alle fuenf Bildungen bei Kapazitaet `9`; A besitzt den
  hoechsten Bildungsindex;
- TSPM-Fast enthaelt getrennte B- und A-Slots bei Kapazitaet `3`;
- der B-Slot ist nur einen Schritt alt und kann bei Ablaufgrenze `8` nicht
  verfallen;
- PPB-1 wurde durch A nicht aufgerufen;
- der auditive und visuelle B-Prototyp bleiben bei Support `3` und mit
  unveraendertem Bankzustand erhalten;
- keine Kapazitaetsgrenze kann B ersetzen.

## 4. Gleichzeitige oeffentliche A/B-Verfuegbarkeit

### Geschichte H0

Bei Q0/MQ erfuellen V0/M0 und V1/M1 beide die funktionalen audiovisuellen
Schwellen. B4 waehlt V0/M0, weil dessen visuelle Distanz `127/2295` kleiner
als `128/2295` ist. Der funktionale Fast-Vergleich trifft dieselbe Auswahl.
Der einzige stabile Slow-Kandidat ist V1/M1 und wird funktional erkannt.

S2-GC erzeugt daher gleichzeitig:

```text
B4_RECENT = V0/M0
TSPM_FAST = V0/M0
TSPM_SLOW = V1/M1, stabiler Support 3
```

S2-GI bildet daraus:

```text
A_RECENT.recent_content = V0/M0
A_RECENT.fast_internal = V0/M0
B_STABLE.stable_content = V1/M1
```

### Geschichte H1

Q1/MQ erzeugt die gespiegelte Belegung:

```text
A_RECENT.recent_content = V1/M1
A_RECENT.fast_internal = V1/M1
B_STABLE.stable_content = V0/M0
```

Damit sind in beiden Konfliktrichtungen A und B gleichzeitig oeffentlich
verfuegbar. Die Vollprobe bestimmt nur, welche bereits vorhandenen
Speicherbefunde S2-GC bereitstellt. Sie gelangt nicht als Wertquelle in die
spaetere Maskenfuellung.

## 5. Rollen-, Quellen-, Owner- und Digestgraph

Der zulassbare Graph ist vollstaendig vorwaertsgerichtet:

```text
Byte-Block-Fixture + Rohbilddigest + auditive Fixture
-> Rezeptorframe und Frame-Digest
-> Envelope- und Quellenbindung
-> Formationseingang
-> Formation-Owner(Vorzustand, Eingabe, Konfiguration)
-> atomarer Composite-Nachzustand und Step-Receipt
-> gebundene Vollprobe
-> read-only S2-FS-Finding
-> S2-GC-Bundle
-> S2-GI-Zwei-Bereich-Projektion
-> Rollenverbrauchsbindung(requested_area, Bundle, Probe, Zustaende)
-> Verbraucher- oder unabhaengiges Baselineergebnis
-> getrennte Evaluation
```

Verbindliche Regeln fuer eine spaetere Implementierung:

- jeder Formation-Owner wird vor seinem Schritt an den konkreten Vorzustand
  und Eingang gebunden und genau einmal verbraucht;
- Probe-, Bundle- und Projektionszugriffe muessen identische Vor- und
  Nachzustandsdigests belegen;
- `requested_area` darf erst nach einer validierten S2-GI-Projektion gebunden
  werden und ausschliesslich `A_RECENT` oder `B_STABLE` benennen;
- die Rollenbindung darf keinen Kandidaten berechnen, umsortieren oder
  automatisch auswaehlen;
- `A_RECENT` verwendet nur `recent_content`; `fast_internal` ist keine
  Ersatzquelle;
- Verbraucher und Baseline erhalten dieselbe maskierte Probe, dieselbe
  Projektion, dieselbe Rollenbindung und dasselbe Funktionsbudget;
- Zielbild, Sollausgabe, Fallklasse und Erfolgsentscheidung sind keine Eltern
  eines Speicher-, Projektions-, Verbraucher- oder Baselineartefakts;
- die getrennte Evaluation darf erst aus abgeschlossenen Verbraucher- und
  Baselineergebnissen sowie der unabhaengigen Zielfixture entstehen.

Keine Digestkante verweist auf ein spaeteres Ergebnis oder auf ihren eigenen
Digest. Ziel- und Auswertungsdaten koennen den Funktionspfad daher nicht
zirkulaer beeinflussen.

## 6. Auditentscheidung

| Pruefpunkt | Befund |
|---|---|
| vier konkrete `uint8`-Bilder rechnerisch materialisierbar | bestanden |
| alle 18 Rezeptorwerte eindeutig hergeleitet | bestanden |
| exakte L1-Brueche und unveraenderte Schwelle | bestanden |
| Unterschiede nur an maskierten Positionen 1 und 3 | bestanden |
| Q0 und Q1 gespiegelt und vollstaendig gebunden | bestanden |
| B erreicht vor A Support `3` | bestanden |
| A bleibt aktuell, getrennt und nicht konsolidiert | bestanden |
| B-Zustand bleibt durch A unveraendert | bestanden |
| `A_RECENT` und `B_STABLE` gleichzeitig oeffentlich | bestanden |
| Rollen- und Digestgraph azyklisch | bestanden |
| Ziel- und Auswertungsdaten vom Funktionspfad getrennt | bestanden |

S2-HP ist bestanden. Die Schwelle bleibt `44/765`. Der private
rollenadressierte Verbraucher darf nun in einem getrennten Schritt zur
Implementierung beantragt werden.

Die spaetere Implementierung muss eine neue private Byte-Block-Fixture
verwenden. Eine Erweiterung oder Wiederverwendung der binaeren S2-GT-Fixture
ist durch diesen Audit nicht freigegeben. Tests, Runner und Funktionslauf
bleiben ebenfalls gesperrt.
