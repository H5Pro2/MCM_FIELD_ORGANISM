# S2-NX: einmaliger gekreuzter Lern-/Transferlauf

Lauf-ID: `s2nx-crossed-learning-20260909-01`.
Technik: **RECORDING_COMPLETE**, **S2NX_LEARNING_VERIFIED**.
Getrennte fachliche Auswertung: **CONFIRMED** im vorgebundenen Umfang.

Genau ein `run_main_once`-Aufruf, danach eine unabhaengige read-only
Verifikation und erst danach eine getrennte Auswertung. Kein Testvorlauf,
keine separate Materialisierung und kein Retry. Qualifizierte Module,
Quellenplan und Versiegelung unveraendert.

## Technischer Abschluss

- 32 Payloads vor Analyse hashgeprueft, 32 direkte Rezeptoranalysen und
  32 NJ-Projektionen. Je 1.536 rohe und gerundete Halbwerte gespeichert.
  Bytegleiche Quellen getrennt verarbeitet, keine Deduplizierung.
- Zwei eigene Lernhistorien, je vier Updates nach Zielbeobachtung und
  Fehlerbindung. Alle aktiven Prognosen einschliesslich Direktrechnung
  zuvor gebunden. Beide Freeze-Bindungen vor der ersten Pruefquelle.
- Zwoelf Pruefstellen mit beiden unveraenderten Lernzustaenden,
  PERSIST, LINEAR und fester 0.5; frisches Praefix je Prueffolge.
  Keine Testupdates, keine Armwahl und keine vorhergesagten Ersatzpraefixe.
- Je Implementierung 92 Prognosevektoren, 4.416 Fehlerterme, 92 MAE-Summen,
  108 Gewinndifferenzen, acht Updates und acht Divisionen. Zusammen
  184 Prognosen und 8.832 Fehlerterme. Alle gebundenen Arbeitsgrenzen
  eingehalten; die Offline-Arbeit wird separat unten ausgewiesen.
- Keine Rohpayloadablage; hoechstens ein 19.200-Byte-PCM-Fenster gleichzeitig.
  Memory-, Feld-, Kontext- und Runtimeaufrufe jeweils 0.
  Beide Lernpaare geschlossen, operative Referenzen verworfen.
- Gesamtbeleg 1.099.358 Byte bei Grenze 2.097.152 Byte;
  Verifikation 1.008 Byte, Auswertung 18.109 Byte, Preregistrierung 5.908 Byte.

Die [Verifikation](verification.json) bestaetigt unabhaengig rekonstruierte
Lernketten, Prognosen, Fehlerterme, Freeze-/Close-Bindungen und Gleichheit
der primaeren und direkten Belege. Quelldateihashes vor/nach dem Lauf
identisch; Ergebnisdateihash vor/nach der Verifikation ebenfalls identisch.
Keine PCM-, Rezeptor- oder NJ-Wiederholung durch die Verifikation.

Offline-Arbeit: 1.536 Halbierungen, je 6.912 Prognosesubtraktionen/-additionen,
4.992 Multiplikationen, 1.920 Kopien, je 1.536 Updateoperationen,
16 Updates/Divisionen, 8.832 Fehlerterme, 184 MAE-Summen und 216
Gewinnpruefungen. Der Offline-Beleg allein beweist keine historische
CPU-Aufrufreihenfolge; diese Absicherung beruht auf dem zuvor qualifizierten,
unveraenderten kausalen Aufrufpfad.

## Getrennter Funktionsbefund

| Block | Ergebnis | Bedeutung |
| --- | --- | --- |
| K01-K06 | 6/6 CONFIRMED | H1 besser als H2 auf s01, H2 besser als H1 auf s02 |
| F01-F06 | 6/6 CONFIRMED | Der jeweils vorab zugeordnete Lerner besser als festes 0.5 |
| B01-B12 | 12/12 CONFIRMED | Zugeordneter Lerner besser als PERSIST und LINEAR auf den Fortsetzungen |
| W01-W04 | 4/4 CONFIRMED | Beide Lerner verlieren gegen PERSIST beim ersten Umkehr-/Gruppenwechselziel |

Kreuzhistorienvorteil und Festfaktorvorteil sind separat bestaetigt. Beide
Fits sind tatsaechlich verschieden, nichtinitial und besitzen n=4 sowie
Sxx>0. Dies sind nachgelagerte Funktionsbefunde, keine Startbedingungen.

**Die vier bestandenen W-Bedingungen sind nachgewiesene Verluste, keine
zusaetzlichen Leistungsgewinne.** Auf s03/p08 und s04/p11 sind beide
Lerner schlechter als PERSIST. Nach dem Gruppenwechsel bleiben beide
auch bei p12 schlechter als PERSIST: MAE 0.0008852589842137442
beziehungsweise 0.0026557769525277167, Persistenzfehler 0.0.
H1 ist dort besser als FIXED_HALF und LINEAR; H2 ist besser als LINEAR,
aber schlechter als FIXED_HALF. Diese Gewinne kompensieren keine Verluste.

Auch die ungeeignete Lerngeschichte bleibt sichtbar: H2 verliert auf allen
drei s01-Zielen gegen PERSIST und FIXED_HALF; H1 verliert auf allen drei
s02-Zielen gegen LINEAR und FIXED_HALF. Es wird kein nachtraeglich bester
Arm als Systemausgabe ausgewaehlt. Gemeinsame Praefixe sind keine
unabhaengigen Replikate.

## Beide Lernketten

Alle folgenden Zahlen stammen aus gespeicherten Zustaenden. Der direkte
Lerner jeder Historie stimmt mit seinem primaeren Gegenstueck ueberein,
wurde aber aus eigenem Nullzustand mit eigenen Updates berechnet.
Die neutralen Beispielkoeffizienten wurden nicht uebernommen.

| Historie | Position | n | Sxx | Sxy | alpha |
| --- | --- | --- | --- | --- | --- |
| H1 | initial | 0 | 0 | 0 | 0 |
| H1 | nach Ziel 2 | 1 | 0.001005281865383363 | 0.0002513204664374563 | 0.25000000009113416 |
| H1 | nach Ziel 3 | 2 | 0.0010681119820156312 | 0.0002670279958207258 | 0.250000000296615 |
| H1 | nach Ziel 4 | 3 | 0.0010720388644177498 | 0.0002680097164438878 | 0.25000000031664 |
| H1 | nach Ziel 5 | 4 | 0.0010722842945791982 | 0.00026807107397324153 | 0.2500000003063012 |
| H1 | frozen | 4 | 0.0010722842945791982 | 0.00026807107397324153 | 0.2500000003063012 |
| H1 | closed | 4 | 0.0010722842945791982 | 0.00026807107397324153 | 0.2500000003063012 |
| H2 | initial | 0 | 0 | 0 | 0 |
| H2 | nach Ziel 2 | 1 | 0.001005281865383363 | 0.0007539614010002165 | 0.7500000019523819 |
| H2 | nach Ziel 3 | 2 | 0.0015707529176055455 | 0.0011780646873554164 | 0.7499999994596587 |
| H2 | nach Ziel 4 | 3 | 0.0018888303802633666 | 0.0014166227853960654 | 0.7500000001051129 |
| H2 | nach Ziel 5 | 4 | 0.0020677489545793152 | 0.0015508117177682622 | 0.7500000008868464 |
| H2 | frozen | 4 | 0.0020677489545793152 | 0.0015508117177682622 | 0.7500000008868464 |
| H2 | closed | 4 | 0.0020677489545793152 | 0.0015508117177682622 | 0.7500000008868464 |

Bei allen acht Updates sind die gespeicherten Subnormal-/Produktunterlauf-
Listen leer, Nullnenner false und Division durchgefuehrt true.
Freeze und Close veraendern keine numerischen Lernparameter.

Historienbindungen:
H1 `f173ce6ed7aabb288c4954af30ea5a8dd970e3cab1d99da5dc1e5b8e09769022`;
H2 `a56060cbbee4b3847cbfb34a87b4a55a58fc8954daec083930a6064e8d71d96c`.
Je sechs Quelldigests und vier Beobachtungsdigests sind vollstaendig in
[result.json](result.json) enthalten. Identische Nullzustandsdigests
bedeuten keine gemeinsamen Owner oder gemeinsame Historienbindung.

| Historie | Schritt | Zustandsdigest | Vorgaengerdigest |
| --- | --- | --- | --- |
| H1 | initial | `c38f6bd280161bdadd08b551c0741ca8fda9148a9d9c35181d01835cdcc0b96f` | null |
| H1 | Update 1 | `9aad7873acf7b38cb582b17c0d955cae12b981989a3aa53307070bacd2ea1ae7` | `c38f6bd280161bdadd08b551c0741ca8fda9148a9d9c35181d01835cdcc0b96f` |
| H1 | Update 2 | `0925c0d58c9d69029a8173f1a81a131a693de9ed40ab3b2e2d55306ce3d72045` | `9aad7873acf7b38cb582b17c0d955cae12b981989a3aa53307070bacd2ea1ae7` |
| H1 | Update 3 | `b67317bbd38fdb691b668afc912a49b660143bdf93f386aee340d648fc62090c` | `0925c0d58c9d69029a8173f1a81a131a693de9ed40ab3b2e2d55306ce3d72045` |
| H1 | Update 4 | `ff1f01947a0b63b7bbdcce6e5cdb9e9e8bbe2894ec4f454d30a8bee6b9b155ec` | `b67317bbd38fdb691b668afc912a49b660143bdf93f386aee340d648fc62090c` |
| H1 | FROZEN | `e2ac7055d38dfbda06dbd0073506df8251e4b8a7fd997e6253f78e3077483e45` | `ff1f01947a0b63b7bbdcce6e5cdb9e9e8bbe2894ec4f454d30a8bee6b9b155ec` |
| H1 | CLOSED | `989b13df4da4a655ca64b51a6af78e9f1d648417c982255c6a518583af802b64` | `e2ac7055d38dfbda06dbd0073506df8251e4b8a7fd997e6253f78e3077483e45` |
| H2 | initial | `c38f6bd280161bdadd08b551c0741ca8fda9148a9d9c35181d01835cdcc0b96f` | null |
| H2 | Update 1 | `fcf4d038e34590c9478a70eee6245debeb802022107a0d840e0d3285114a2cfd` | `c38f6bd280161bdadd08b551c0741ca8fda9148a9d9c35181d01835cdcc0b96f` |
| H2 | Update 2 | `25a00490399c510c49f289e72be47c61b649162e33748bda7775e9fb5cbe44fb` | `fcf4d038e34590c9478a70eee6245debeb802022107a0d840e0d3285114a2cfd` |
| H2 | Update 3 | `9c80eb9f7b1c596d98bbf7baadea877518fde64dec2dcd3150b240a7f0a3259b` | `25a00490399c510c49f289e72be47c61b649162e33748bda7775e9fb5cbe44fb` |
| H2 | Update 4 | `6540899ffbb4f964c095b4cec5462e5c37f6e17127478d5b303dedf00cf4295e` | `9c80eb9f7b1c596d98bbf7baadea877518fde64dec2dcd3150b240a7f0a3259b` |
| H2 | FROZEN | `3ce3c6471d5bd71910cd59ca95e39d7e95de05822ee6a82b6e8236138f190205` | `6540899ffbb4f964c095b4cec5462e5c37f6e17127478d5b303dedf00cf4295e` |
| H2 | CLOSED | `30a3c1072cd56687c6714f92e9d5012ce95d2068097a3e923f9a87a80db7387d` | `3ce3c6471d5bd71910cd59ca95e39d7e95de05822ee6a82b6e8236138f190205` |

## Saemtliche MAE-Einzelwerte

32 Trainings-MAE und 60 Pruef-MAE, keine Mittelung ueber Stellen oder
Verlaufstypen. Die unabhaengige Direktrechnung liefert dieselben 92 Werte.
`-` bezeichnet den im Training nicht aktiven Lerner, nicht einen Nullfehler.
Vollstaendige 48 Einzelterme je MAE stehen im atomaren [Gesamtbeleg](result.json).

### l01: TRAINING_QUARTER_INCREMENT

| Stelle | Ziel k | Phase | MAE H1 | MAE H2 | MAE PERSIST | MAE LINEAR | MAE FIXED_HALF |
| --- | --- | --- | --- | --- | --- | --- | --- |
| t01 | 2 | TRAIN | 0.00028730939862038374 | - | 0.00028730939862038374 | 0.0008619282038161777 | 0.00028730940259971184 |
| t02 | 3 | TRAIN | 1.0784700377394787e-11 | - | 0.00007182735340843406 | 0.00021548204889712397 | 0.00007182735105116046 |
| t03 | 4 | TRAIN | 9.536899148684201e-12 | - | 0.000017956840592686307 | 0.00005387051902082786 | 0.000017956843546420417 |
| t04 | 5 | TRAIN | 8.494046152013715e-12 | - | 0.000004489213114325269 | 0.000013467634975458122 | 0.000004489215937180075 |

### l02: TRAINING_THREE_QUARTER_INCREMENT

| Stelle | Ziel k | Phase | MAE H1 | MAE H2 | MAE PERSIST | MAE LINEAR | MAE FIXED_HALF |
| --- | --- | --- | --- | --- | --- | --- | --- |
| t05 | 2 | TRAIN | - | 0.0008619282112430291 | 0.0008619282112430291 | 0.00028730939311416164 | 0.0002873094100265634 |
| t06 | 3 | TRAIN | - | 2.379619497513987e-11 | 0.0006464461481700931 | 0.0002154820636756014 | 0.00021548204443397348 |
| t07 | 4 | TRAIN | - | 3.024000913461245e-11 | 0.0004848346081273143 | 0.0001616115496494167 | 0.0001616115475343693 |
| t08 | 5 | TRAIN | - | 3.1257685932215514e-11 | 0.00036362596764256846 | 0.00012120865761218451 | 0.00012120866654842885 |

### s01: CONTINUATION_QUARTER

| Stelle | Ziel k | Phase | MAE H1 | MAE H2 | MAE PERSIST | MAE LINEAR | MAE FIXED_HALF |
| --- | --- | --- | --- | --- | --- | --- | --- |
| p01 | 2 | INITIAL_TARGET | 7.606102700451005e-12 | 0.0002843322129474219 | 0.00014216610533315986 | 0.00042649831836852526 | 0.00014216610651768266 |
| p02 | 3 | FIRST_BRANCH | 7.753633520626446e-12 | 0.00007108305562096498 | 0.00003554152584485549 | 0.00010662458166175618 | 0.00003554152932801487 |
| p03 | 4 | FOLLOWUP | 7.316559471742872e-12 | 0.00001777076452932785 | 0.000008885384404325962 | 0.000026656145413517775 | 0.000008885383943054831 |

### s02: CONTINUATION_THREE_QUARTER

| Stelle | Ziel k | Phase | MAE H1 | MAE H2 | MAE PERSIST | MAE LINEAR | MAE FIXED_HALF |
| --- | --- | --- | --- | --- | --- | --- | --- |
| p04 | 2 | INITIAL_TARGET | 0.0002843322087997065 | 1.1523683558149545e-11 | 0.00042649831489931044 | 0.00014216610893168886 | 0.00014216610304846795 |
| p05 | 3 | FIRST_BRANCH | 0.00021324916159002531 | 1.3144245710755763e-11 | 0.00031987374044548995 | 0.00010662457445382049 | 0.00010662458299583471 |
| p06 | 4 | FOLLOWUP | 0.00015993686941889846 | 1.1976132610840191e-11 | 0.00023990530391742446 | 0.00007996843701033524 | 0.00007996843584396299 |

### s03: REVERSAL

| Stelle | Ziel k | Phase | MAE H1 | MAE H2 | MAE PERSIST | MAE LINEAR | MAE FIXED_HALF |
| --- | --- | --- | --- | --- | --- | --- | --- |
| p07 | 2 | INITIAL_TARGET | 7.606102700451005e-12 | 0.0002843322129474219 | 0.00014216610533315986 | 0.00042649831836852526 | 0.00014216610651768266 |
| p08 | 3 | FIRST_BRANCH | 0.00017770763170999552 | 0.00024879068445910916 | 0.00014216610533315986 | 0.0002843322106663197 | 0.00021324915799973977 |
| p09 | 4 | FOLLOWUP | 7.672567245070441e-12 | 0.00007108305475472301 | 0.00003554152575044673 | 0.00010662458091606796 | 0.00003554152837332859 |

### s04: UNEXPECTED_GROUP_CHANGE

| Stelle | Ziel k | Phase | MAE H1 | MAE H2 | MAE PERSIST | MAE LINEAR | MAE FIXED_HALF |
| --- | --- | --- | --- | --- | --- | --- | --- |
| p10 | 2 | INITIAL_TARGET | 0.0002843322087997065 | 1.1523683558149545e-11 | 0.00042649831489931044 | 0.00014216610893168886 | 0.00014216610304846795 |
| p11 | 3 | FIRST_BRANCH | 0.003640331022741163 | 0.003838921205998863 | 0.0035410359325164825 | 0.003938216298590664 | 0.0037396261135341988 |
| p12 | 4 | FOLLOWUP | 0.0008852589842137442 | 0.0026557769525277167 | 0 | 0.0035410359325164825 | 0.0017705179662582413 |

## Gewinne und Verluste je Stelle

Die nachfolgenden Klassen sind unveraendert aus der getrennten
[evaluation.json](evaluation.json) uebernommen. Alle numerischen Gewinne
stehen dort ebenfalls. Kreuzrichtung ist fest `MAE_H2 - MAE_H1`:
WIN bedeutet H1 besser, LOSS H2 besser; keine automatische Historienwahl.
Pro Trainingshistorie/Baseline N=4, pro Prueffolge/Historie/Baseline N=3,
pro Zielphase N=1. Insgesamt 108 Klassifikationen, davon 24 Training.

### l01

| Stelle | Lerner | gegen PERSIST | gegen LINEAR | gegen FIXED_HALF | Kreuz H1 gegen H2 |
| --- | --- | --- | --- | --- | --- |
| t01 | H1 | TIE | WIN | WIN | - |
| t02 | H1 | WIN | WIN | WIN | - |
| t03 | H1 | WIN | WIN | WIN | - |
| t04 | H1 | WIN | WIN | WIN | - |

### l02

| Stelle | Lerner | gegen PERSIST | gegen LINEAR | gegen FIXED_HALF | Kreuz H1 gegen H2 |
| --- | --- | --- | --- | --- | --- |
| t05 | H2 | TIE | LOSS | LOSS | - |
| t06 | H2 | WIN | WIN | WIN | - |
| t07 | H2 | WIN | WIN | WIN | - |
| t08 | H2 | WIN | WIN | WIN | - |

### s01

| Stelle | Lerner | gegen PERSIST | gegen LINEAR | gegen FIXED_HALF | Kreuz H1 gegen H2 |
| --- | --- | --- | --- | --- | --- |
| p01 | H1 | WIN | WIN | WIN | WIN |
| p01 | H2 | LOSS | WIN | LOSS | - |
| p02 | H1 | WIN | WIN | WIN | WIN |
| p02 | H2 | LOSS | WIN | LOSS | - |
| p03 | H1 | WIN | WIN | WIN | WIN |
| p03 | H2 | LOSS | WIN | LOSS | - |

### s02

| Stelle | Lerner | gegen PERSIST | gegen LINEAR | gegen FIXED_HALF | Kreuz H1 gegen H2 |
| --- | --- | --- | --- | --- | --- |
| p04 | H1 | WIN | LOSS | LOSS | LOSS |
| p04 | H2 | WIN | WIN | WIN | - |
| p05 | H1 | WIN | LOSS | LOSS | LOSS |
| p05 | H2 | WIN | WIN | WIN | - |
| p06 | H1 | WIN | LOSS | LOSS | LOSS |
| p06 | H2 | WIN | WIN | WIN | - |

### s03

| Stelle | Lerner | gegen PERSIST | gegen LINEAR | gegen FIXED_HALF | Kreuz H1 gegen H2 |
| --- | --- | --- | --- | --- | --- |
| p07 | H1 | WIN | WIN | WIN | WIN |
| p07 | H2 | LOSS | WIN | LOSS | - |
| p08 | H1 | LOSS | WIN | WIN | WIN |
| p08 | H2 | LOSS | WIN | LOSS | - |
| p09 | H1 | WIN | WIN | WIN | WIN |
| p09 | H2 | LOSS | WIN | LOSS | - |

### s04

| Stelle | Lerner | gegen PERSIST | gegen LINEAR | gegen FIXED_HALF | Kreuz H1 gegen H2 |
| --- | --- | --- | --- | --- | --- |
| p10 | H1 | WIN | LOSS | LOSS | LOSS |
| p10 | H2 | WIN | WIN | WIN | - |
| p11 | H1 | LOSS | WIN | WIN | WIN |
| p11 | H2 | LOSS | WIN | LOSS | - |
| p12 | H1 | LOSS | WIN | WIN | WIN |
| p12 | H2 | LOSS | WIN | LOSS | - |

## Alle 28 vorgebundenen Kriterien

| Kriterium | Stelle | Bedingung | Ergebnis |
| --- | --- | --- | --- |
| K01 | p01 | MAE_H1 < MAE_H2 | CONFIRMED |
| K02 | p02 | MAE_H1 < MAE_H2 | CONFIRMED |
| K03 | p03 | MAE_H1 < MAE_H2 | CONFIRMED |
| K04 | p04 | MAE_H2 < MAE_H1 | CONFIRMED |
| K05 | p05 | MAE_H2 < MAE_H1 | CONFIRMED |
| K06 | p06 | MAE_H2 < MAE_H1 | CONFIRMED |
| F01 | p01 | MAE_H1 < MAE_FIXED_HALF | CONFIRMED |
| F02 | p02 | MAE_H1 < MAE_FIXED_HALF | CONFIRMED |
| F03 | p03 | MAE_H1 < MAE_FIXED_HALF | CONFIRMED |
| F04 | p04 | MAE_H2 < MAE_FIXED_HALF | CONFIRMED |
| F05 | p05 | MAE_H2 < MAE_FIXED_HALF | CONFIRMED |
| F06 | p06 | MAE_H2 < MAE_FIXED_HALF | CONFIRMED |
| B01 | p01 | MAE_H1 < MAE_PERSIST | CONFIRMED |
| B02 | p01 | MAE_H1 < MAE_LINEAR | CONFIRMED |
| B03 | p02 | MAE_H1 < MAE_PERSIST | CONFIRMED |
| B04 | p02 | MAE_H1 < MAE_LINEAR | CONFIRMED |
| B05 | p03 | MAE_H1 < MAE_PERSIST | CONFIRMED |
| B06 | p03 | MAE_H1 < MAE_LINEAR | CONFIRMED |
| B07 | p04 | MAE_H2 < MAE_PERSIST | CONFIRMED |
| B08 | p04 | MAE_H2 < MAE_LINEAR | CONFIRMED |
| B09 | p05 | MAE_H2 < MAE_PERSIST | CONFIRMED |
| B10 | p05 | MAE_H2 < MAE_LINEAR | CONFIRMED |
| B11 | p06 | MAE_H2 < MAE_PERSIST | CONFIRMED |
| B12 | p06 | MAE_H2 < MAE_LINEAR | CONFIRMED |
| W01 | p08 | MAE_H1 > MAE_PERSIST | CONFIRMED |
| W02 | p08 | MAE_H2 > MAE_PERSIST | CONFIRMED |
| W03 | p11 | MAE_H1 > MAE_PERSIST | CONFIRMED |
| W04 | p11 | MAE_H2 > MAE_PERSIST | CONFIRMED |

Gleichstaende wuerden keine strikte Bedingung bestehen. Keine
Trainingsverbesserung, kein Baselineblock und kein Wechselverlustblock
ersetzt K oder F. Kein gepoolter Mittelwert und keine Verlustverrechnung.

## Unveraenderliche Belegbindungen

| Beleg | Digest |
| --- | --- |
| Qualifikation | `95bef00924f51d9cb5924aa9f6ffc3a2cb9e4fb7b8eeb514e06ba30739892d26` |
| Ausfuehrungswurzel | `f52992815d49889334b11f64a13e00879984ce4cabecd3670a0fcf2d7441b80c` |
| Evaluationswurzel | `c755699e69fa38dff0426080ac7d37500e6ba044afd9c53abff4ffe97613847e` |
| Ergebnis | `c8b478c00ce4a83ecd7e8be138a8ba0aada0c52687a4845c7bc086272d71afd4` |
| Verifikation | `4fe83068ab7382a60730f6dfe987fca271c8d64bd98f8bdfa845d9dc0ffabed9` |
| Getrennte Auswertung | `c04ff5a3e3daa232287790e8653e9d0800ed5fb560d54e5ea1744ba20f52e669` |
| Ergebnisfile vor/nach Verifikation | `c8a74fdf39fb64002d2c1d2b60f7e2618edb596e800d6e7d606637e0017ba48c` |

## Aussagegrenze und Stopp

Beobachtet ist auf diesem vorgebundenen kontrollierten Bestand ein
aufgabengerechter Einfluss unterschiedlicher Lernerfahrung bei identischen
aktuellen Pruefeingaben, mit Zusatznutzen gegen die feste Daempfung 0.5.
Die bekannten skalaren Update- und Extrapolationsvorschriften samt
unabhaengigen Direktbaselines erklaeren den Effekt vollstaendig.

Nicht nachgewiesen sind automatische Auswahl der passenden Lerngeschichte,
Quellen-/Objektidentitaet, allgemeines Sequenzlernen oder eine Loesung der
ME/MI-Lernbindung. Die Generatorrollen verbleiben Auswertungsherkunft.
Ein gemeinsames Praefix verraet weiterhin nicht den nachfolgenden Zweig.
Vorhersagefehler sind weder automatisch Quellenwechsel noch Stress.

Kein weiterer NX-Lauf, keine Anpassung, keine Systemintegration.
Alle beteiligten Gates sind nach Abschluss False. ME/MI bleiben gesperrt;
Versiegelung, historische Belege, fremde Aenderungen und Bootstrap unveraendert.

WEITER: Am besten geht es jetzt mit der Analystenbewertung des
Kreuzhistorien- und Festfaktorbefunds samt getrennten Wechselverlusten weiter.
