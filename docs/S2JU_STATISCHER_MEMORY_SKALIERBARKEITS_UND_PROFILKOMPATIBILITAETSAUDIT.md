# S2-JU - Statischer Memory-Skalierbarkeits- und Profilkompatibilitaetsaudit

## Status

`S2JU_STATIC_AUDIT_COMPLETE`

Gesamtbefund:

`S2JU_CORES_PROFILE_COMPATIBLE_PRIVATE_BOUNDARIES_REQUIRE_LIMITED_ADAPTATION`

PPB-1 und TSPM-1 sind im Kern dimensionsabgeleitet und koennen das
`default-live`-Profil mit 48 auditiven und 288 visuellen Werten darstellen.
Der bestehende private B4-/TSPM-Koordinator, sein read-only Adapter und sein
Ledger sind dagegen fest an `8 + 18 = 26` Werte gebunden. Sie duerfen fuer
336 Werte nicht wiederverwendet oder nur mit neuen Zahlen gespeist werden.

S2-JU hat keine Module importiert, keine Tests oder Zustandsfunktionen
ausgefuehrt und keinen Memory-, Kontext- oder Feldzustand erzeugt. Die README
bleibt unveraendert.

## Gebundener Quellstand

Basis ist Commit `6363d065e5a4554daa20b35bbd0b726a166085c5`.

| Rolle | Datei | SHA-256 |
| --- | --- | --- |
| atomarer privater Verbund | `tools/_s2fs_b4_tspm1_private_coordinator.py` | `95ee05ccc0eeb14abbcda036971da5c33ac79363dd546789f4878aace5677db0` |
| bisheriger read-only Inhaltsadapter | `tools/_retention_capacity_read_only.py` | `524a42ae8294a14e58adfda29afa8602f3a799e0caaccae9675dc50bf0109ff7` |
| TSPM-1-Kern | `mcm_field_organism/_tspm1_private.py` | `321ce786c42edd217dc6dbf2210c495016b2babaa78d53449a13b0039965d516` |
| PPB-1-Kern | `mcm_field_organism/_ppb1_reference.py` | `15f1fabaa45348f067b7bf466f138d275d74f75a6e98afc05867f7b8c35d46f0` |
| PPB-1-Rezeptorprofile | `mcm_field_organism/_ppb1_receptor_profiles.py` | `28f3ce1de5b0ade465fffaa7dd3064eb51688cfea39ebb6c853cb4328bc0e5e0` |
| bisheriger 26-Werte-Vergleich | `mcm_field_organism/_tspm1_s2dr_private_comparison.py` | `96cdd018be34afe67de0139428fed5254cff945ba74db98163a91273f5d21b2c` |
| kanonische AV-Simulationsgrenze | `tools/_s2jo_private_canonical_av_boundary.py` | `50a39fb3865fbd11b3577f79db2983f9dd3260262dee0f199ae5f884bed4ef71` |
| bestaetigter AV-Feldpfad | `tools/_s2jt_private_timed_field_projection.py` | `91604184325192b6a6291785f713c44fc8fac1d7614234279f635032160c4a4e` |

Der abgeschlossene S2-JT-Ergebnisbeleg hat den SHA-256-Digest
`49f17da19efe1a8fc57346ced5713a409c92cd5f595946239693682c6388613b`.
Er belegt das Default-Live-Rezeptor-/Feldprofil, nicht dessen Memorynutzung.

## Profil- und Kapazitaetsbindung

| Komponente | bisher | Default-Live | Bewertung |
| --- | ---: | ---: | --- |
| auditive Werte | 8 | 48 | Faktor 6 |
| visuelle Werte | 18 | 288 | Faktor 16 |
| gemeinsamer AV-Vektor | 26 | 336 | Faktor `168/13` |
| B4-Slots | 9 | 9 | unveraendert |
| TSPM-Fast-Slots | 3 | 3 | unveraendert |
| PPB-Slow auditiv | 8 | 8 | unveraendert |
| PPB-Slow visuell | 4 | 4 | unveraendert |

`bind_ppb1_receptor_profile("default-live", ...)` erzeugt bereits die
Carrierinventare mit 48 beziehungsweise 288 Positionen. PPB-1 prueft
Vektorlaengen gegen diese Carrierlisten. TSPM-1 leitet Fast- und Slow-
Dimensionen ebenfalls aus derselben Profilbindung ab. In diesen beiden
Kernen existiert deshalb keine technische `8/18`-Dimensionsannahme.

Die Slotzahlen bleiben fachlich unveraendert. Es entsteht keine dritte
Memoryebene:

- `A_RECENT`: B4 mit 9 Eintraegen und TSPM-Fast mit 3 Slots, intern getrennt;
- `B_STABLE`: PPB-1 mit 8 auditiven und 4 visuellen Prototypslots;
- Folgenordnung bleibt ausschliesslich B4-Evidenz.

## Gefundene feste 26-Werte-Grenzen

Der S2-FS-Koordinator ist nicht profilneutral:

- `AUDITORY_DIMENSION = 8`, `VISUAL_DIMENSION = 18` und `AV_DIMENSION = 26`;
- seine Konfiguration akzeptiert ausschliesslich diese Werte;
- Input, Probe und gemeinsame Projektion pruefen dieselben Konstanten;
- die alten Armgrenzen `293` Schreibwoerter und `234` Distanzterme sind
  literal eingebaut.

Der bisherige read-only Adapter ist ebenfalls nicht profilneutral:

- fester Split nach Position 8;
- feste Laengen 8, 18 und 26 fuer B4, Fast und Probe;
- feste B4-Kapazitaet 9;
- funktionale Bewertung mit den bisherigen, fuer 336 Werte nicht
  kalibrierten Schwellen.

Auch der alte S2-DR-Vergleich enthaelt 8/18-Slices und dimensionsbezogene
Schreibbreiten. Er bleibt historische 26-Werte-Infrastruktur und ist kein
Ausgangspunkt fuer den Default-Live-Lauf.

## Digestkompatibilitaet

Die Digestalgorithmen sind dimensionsneutral. Die kanonischen Payloads
binden aber Carrierinventar, Geometrie, Konfiguration und vollstaendige
Wertefolgen. Beim Profilwechsel muessen sich daher mindestens folgende
Digests aendern:

1. auditive und visuelle PPB-Konfiguration;
2. PPB-Profilbindung;
3. TSPM-Konfigurationsbindung;
4. private Koordinatorkonfiguration;
5. alle daraus abgeleiteten Input-, Probe-, Zustands-, Receipt- und
   Ledgerdigests.

Ein 26-Werte-Zustand darf unter einer 336-Werte-Konfiguration weder migriert
noch stillschweigend aufgefuellt werden. Dimensions-, Carrier-, Geometrie-
oder Konfigurationsabweichung stoppt vor dem ersten Armaufruf fail-closed.

## Exakte logische Speichergrenzen

Die folgende Rechnung umfasst die maximal belegbaren numerischen
Memorywerte. Sie umfasst keine Rohbilder, kein PCM, keine Python-
Objektoverheads und keine Ergebnisdateien.

| Zustand | Rechnung | Float64-Werte | Nutzbytes |
| --- | ---: | ---: | ---: |
| B4 | `9 * 336` | 3.024 | 24.192 |
| TSPM-Fast | `3 * 336` | 1.008 | 8.064 |
| PPB-Slow auditiv | `8 * 48` | 384 | 3.072 |
| PPB-Slow visuell | `4 * 288` | 1.152 | 9.216 |
| TSPM gesamt | `1.008 + 384 + 1.152` | 2.544 | 20.352 |
| atomarer B4-/TSPM-Verbund | `3.024 + 2.544` | 5.568 | 44.544 |

Zum Vergleich belegt die 26-Werte-Linie maximal 448 logische Floatwerte
beziehungsweise 3.584 Nutzbytes. Das Default-Live-Profil vergroessert diesen
reinen Wertebestand um den Faktor `87/7`, ohne die Slotzahlen zu erhoehen.

Die exakte physische Prozessspeichergroesse ist aus Python-Quelltext nicht
plattformunabhaengig ableitbar. Sie muss bei einem spaeteren Lauf getrennt
als RSS/Peak-Wert gemessen werden und ist kein Ersatz fuer die oben gebundene
logische Speichergrenze.

## Operations- und Laufzeitarbeit

`normalized_mean_l1_distance` verarbeitet exakt einen Skalarterm pro
Carrier. Unter Beibehaltung der vorhandenen relationalen Nachpruefungen
gelten folgende harte Einzelobergrenzen:

| Operation | skalare L1-Terme maximal |
| --- | ---: |
| eine Formation | `2 * (3 * 336) + 8 * 48 + 4 * 288 = 3.552` |
| eine voll belegte read-only Verbundprobe | `9.120` |

Die Formation enthaelt zwei Fast-Distanzdurchlaeufe, weil der Kandidat nach
seiner Bildung relational neu geprueft wird. Die read-only Grenze enthaelt
B4, den nativen und relational validierten TSPM-Fast-Pfad, den vorhandenen
Inhaltsadapter sowie native und nachgepruefte Slow-Befunde. Hashing,
Serialisierung und skalare Kontrollvergleiche bleiben eigene Ledgerrollen
und duerfen nicht als L1-Terme versteckt werden.

Fuer den unten gebundenen ersten Fall sind die Zaehler exakt:

| Rolle | Anzahl |
| --- | ---: |
| AV-Expositionen | 15 |
| read-only Verbundproben | 3 |
| Top-Level-Memoryoperationen | 72 |
| interne PPB-Formationsaufrufe | 8 |
| interne PPB-/S1WU-Probeaufrufe | 6 |
| Aufrufe von `normalized_mean_l1_distance` | 260 |
| L1-Skalarterme in Formationen | 22.512 |
| L1-Skalarterme in Proben | 21.168 |
| L1-Skalarterme gesamt | 43.680 |
| gemeinsame AV-Projektionsterme | 5.040 |
| neu materialisierte B4-Vektorwerte | 5.040 |
| neu materialisierte Fast-Vektorwerte | 5.040 |
| neu materialisierte Slow-Vektorwerte | 1.344 |
| neu materialisierte Vektorwerte gesamt | 11.424 |

Die 72 Top-Level-Operationen bestehen aus je 15 Quellenprojektionen,
B4-Schritten, TSPM-Schritten und atomaren Verbundvalidierungen sowie je drei
Probeprojektionen, B4-Proben, TSPM-Proben und read-only
Verbundvalidierungen. Interne PPB-Aufrufe werden nicht doppelt als
Top-Level-Operationen gezaehlt.

Damit ist die deterministische Laufzeitarbeit begrenzt. Eine exakte
Wandzeit in Sekunden kann statisch und hardwareunabhaengig nicht berechnet
werden. Ein spaeterer Lauf muss Wandzeit und Peak-RSS separat messen; beide
sind technische Laufdaten, keine funktionalen Erfolgskriterien. Die alten
Ledgerwerte `293/234` sind fuer 336 Werte in jedem Fall ungueltig.

## Erster Funktionsfall

Der erste Funktionsfall prueft ausschliesslich exakte Wiederholung,
begrenzte Erhaltung und Vergessen:

```text
X, X, X, X, Y, Y, D1, D2, D3, D4, D5, D6, D7, D8, D9
```

Gebundene Bedingungen:

- `X` ist viermal bitidentisch; die drei PPB-Aufrufe erzeugen Slow-Support
  `1`, `2`, `3` und damit einen stabilen B-Befund;
- `Y` ist zweimal bitidentisch; genau ein PPB-Aufruf erzeugt Support `1`,
  aber keinen oeffentlichen stabilen B-Befund;
- `D1..D9` sind einmalige, vorab gebundene AV-Rezeptorzustaende;
- alle nichtidentischen Paare liegen in beiden Modalitaeten nachweislich
  ausserhalb der verwendeten nativen Matchbereiche;
- nach `D9` enthaelt B4 exakt das FIFO-Fenster `D1..D9`;
- TSPM-Fast enthaelt weder `X` noch `Y`;
- `X` ist nur als stabiler `B_STABLE`-Inhalt abrufbar;
- `Y` ist funktional vergessen: kein B4-, kein Fast- und kein stabiler
  Slow-Treffer. Sein physisch vorhandener instabiler PPB-Support `1` bleibt
  Diagnoseevidenz und ist keine oeffentliche Memoryebene;
- die drei Abschlussproben sind `D9`, `X` und `Y`; alle sind read-only.

Die Distanzzaehler folgen aus 32 Fast-Slotvergleichen waehrend der Bildung,
deren relationaler Wiederholung, den PPB-Vorbelegungen `0/1/1/1` und den
drei vollstaendigen Abschlussproben. Fixtures muessen diese Belegung vor
einer Ausfuehrung statisch bestaetigen.

## Schwellen- und Aussagegrenze

Die bisherigen Werte `0.2`, `0.02`, `0.01` und `44/765` sind durch S2-JU
nicht fuer das 336-Werte-Profil kalibriert. Sie duerfen weder als
Wahrnehmungsaehnlichkeit noch als generalisierte Abrufqualitaet ausgegeben
werden.

Der erste Fall verwendet deshalb nur:

- Distanz exakt `0` fuer bitidentische Wiederholungen;
- vorab deutlich getrennte Distraktoren fuer Verdrangung und Ablauf;
- direkte Slot-, Support- und Stabilitaetsbefunde.

Er beantwortet keine Frage zu Rauschtoleranz, partieller Aehnlichkeit,
Merkmalsgewichtung oder der Vergleichbarkeit auditiver und visueller
Distanzen. Dafuer ist spaeter eine eigene Kalibrierung erforderlich.

## Gemeinsame Rezeptorquelle ohne Feldrueckweg

Die Memory darf keinen Feldsnapshot lesen. Die zulaessige Verzweigung liegt
unmittelbar hinter den unveraenderten Rezeptoren:

```text
kanonische RGB-/PCM-Quelle
-> unveraenderte Rezeptoren
-> gebundene reduzierte Rezeptorzustaende
   -> S2-JT-Zeitprojektion und Feld
   -> private AV-Expositionsbindung und Memory
```

Beide Zweige muessen dieselben Zustands- und Quelldigests binden. Feldwerte,
Feldtrajektorie und Feldreceipt sind keine Eltern der Memorybildung.

TSPM-1 erwartet pro Formation ein zeitlich ueberlappendes auditives und
visuelles Paar. Die 17 asynchronen S2-JT-Abschluesse sind deshalb nicht
automatisch 17 AV-Memoryformationen. Erforderlich ist eine kleine private,
vorwaertsgerichtete Paarungsgrenze. Sie darf weder den letzten Wert
fortschreiben noch aus einem Feldsnapshot rekonstruieren. Der erste
Funktionsfall verwendet ausschliesslich vorab gebundene, echte gemeinsame
AV-Fenster; die 200-ms-S2-JT-Episode wird nicht umgedeutet.

## Notwendige begrenzte Anpassungen

Vor einem 336-Werte-Funktionslauf sind genau vier private Arbeiten noetig:

1. `default-live`-PPB-/TSPM-Profilbindung mit unveraenderten Slotzahlen und
   neuem Config-Digest;
2. profilabgeleitete B4-/TSPM-Koordinatorgrenze ohne literale 8/18/26-
   Annahmen;
3. profilabgeleitete read-only Inhaltsauswertung ohne Uebernahme der alten
   funktionalen Schwellen;
4. neues dimensions- und pfadbezogenes Ledger fuer Projektion, semantische
   Writes, funktionale und Validierungs-L1-Terme, Digests und Kontrollarbeit.

Diese Arbeiten duerfen die bestehenden qualifizierten 26-Werte-Module nicht
umschreiben. B4-, TSPM-1- und PPB-1-Kerne, Feldpfad, API und Snapshot bleiben
unveraendert.

## Abschlussentscheidung

S2-JU bestaetigt:

- die Kernalgorithmen sind fuer `48 + 288` dimensionskompatibel;
- die Slotarchitektur kann unveraendert bleiben;
- der maximale numerische Verbundzustand ist mit 5.568 Floatwerten endlich;
- L1-Arbeit skaliert linear mit Carrierzahl und belegten Slots;
- der erste bitidentische Verdichtungsfall ist mit 15 Formationen und drei
  Proben endlich materialisierbar.

S2-JU bestaetigt nicht:

- die Eignung bisheriger Schwellen im Default-Live-Profil;
- einen Funktionslauf der 336-Werte-Memory;
- eine Memoryskalierung der asynchronen S2-JT-Episode ohne explizite
  AV-Paarungsregel;
- Kontextnutzung, Feldrueckwirkung oder eine dritte Memoryebene.

Der naechste konkrete Schritt ist damit keine Kernneuentwicklung, sondern
die eng begrenzte private Profil-, Adapter- und Ledgerimplementierung fuer
den oben gebundenen bitidentischen Funktionsfall.
