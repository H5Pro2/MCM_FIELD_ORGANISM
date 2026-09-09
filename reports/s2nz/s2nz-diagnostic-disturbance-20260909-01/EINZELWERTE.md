# S2-NZ: vollstaendige diagnostische Einzelwerte

ID `s2nz-diagnostic-disturbance-20260909-01`.
Aus der einmalig nach erfolgreicher Verifikation erzeugten
[evaluation.json](evaluation.json) uebertragen. Keine erneute Prognose-,
MAE- oder Gewinndifferenzberechnung fuer diese Tabellen.
Dezimale Roundtrip-Darstellung gespeicherter Binary64-Werte; keine Toleranz.

s01/s02: H1-Fortsetzung sauber/gestoert. s03/s04: H2-Fortsetzung sauber/gestoert.
s05/s06: Gruppenwechsel sauber/gestoert, erstes Wechselziel k3,
Folgefenster k4. k2 hat noch keine Empfehlung und keine LOCAL-Schaetzung.
Die Kategorien dienen ausschliesslich der Evaluation.

## Alle 66 Arm-MAE

MAE bezieht sich immer auf den tatsaechlich beobachteten naechsten Halbvektor
derselben Folge, auch gestoert. Kein sauberes Rekonstruktionsziel.
Die Empfehlung waehlt den bezeichneten bereits berechneten H1-/H2-MAE;
bei Enthaltung ist ihr MAE null/fehlend, nicht numerisch null.
`-` bedeutet nicht verfuegbar. NEXT_BEST ist nur der Vergleich mit der
anderen gespeicherten Historie, kein Urteil gegen LOCAL oder PERSIST.

| Stelle | Folge/Ziel | H1 MAE | H2 MAE | LOCAL MAE | PERSIST MAE | Empfehlung | Naechster Historienvergleich |
| --- | --- | ---: | ---: | ---: | ---: | --- | --- |
| p01 | s01/k2 | 8.196341579208739E-12 | 0.00042081024705607523 | - | 0.00021040512375393892 | Enthaltung: Praefix | - |
| p02 | s01/k3 | 7.870064375865504E-12 | 0.00010520256310068923 | 8.026922659392257E-12 | 5.2601280679769994E-05 | H1 | NEXT_BEST |
| p03 | s01/k4 | 8.391391530222832E-12 | 2.630063953742575E-05 | 8.726335067596528E-12 | 1.3150325362131344E-05 | H1 | NEXT_BEST |
| p04 | s02/k2 | 6.9639460981488394E-06 | 0.0004273259242719922 | - | 0.0002150703110885289 | Enthaltung: Praefix | - |
| p05 | s02/k3 | 6.698412863899002E-06 | 0.00011321358761374832 | 6.696069968526233E-06 | 5.7831906749587743E-05 | H1 | NEXT_BEST |
| p06 | s02/k4 | 6.601882585813799E-06 | 3.386082924743215E-05 | 6.6027196024974685E-06 | 1.80540354288046E-05 | H1 | NEXT_BEST |
| p07 | s03/k2 | 0.00042081025443583766 | 1.7135197033974432E-11 | - | 0.0006312153779223047 | Enthaltung: Praefix | - |
| p08 | s03/k3 | 0.0003156076909997134 | 1.8678301284539253E-11 | 2.345411889738565E-11 | 0.00047341153567363167 | H2 | NEXT_BEST |
| p09 | s03/k4 | 0.0002367057611838664 | 1.941795995237172E-11 | 1.9049422618752066E-11 | 0.00035505864172618267 | H2 | NEXT_BEST |
| p10 | s04/k2 | 0.00042599012451432247 | 8.167048810000397E-06 | - | 0.000635812614670089 | Enthaltung: Praefix | - |
| p11 | s04/k3 | 0.00032299717273822124 | 9.214864460992774E-06 | 9.584611210964812E-06 | 0.00047997173148481054 | H2 | NEXT_BEST |
| p12 | s04/k4 | 0.00024269534790832757 | 1.0407291467035624E-05 | 1.0735936800816341E-05 | 0.000359884067852536 | H2 | NEXT_BEST |
| p13 | s05/k2 | 0.00042081025443583766 | 1.7135197033974432E-11 | - | 0.0006312153779223047 | Enthaltung: Praefix | - |
| p14 | s05/k3 | 0.004260611865571825 | 0.004576218097529568 | 0.0045762181023053855 | 0.004102808751252962 | H2 | NEXT_WRONG |
| p15 | s05/k4 | 0.0010257021890699356 | 0.003077106567078283 | 0.013220135146633434 | 0 | H1 | NEXT_BEST |
| p16 | s06/k2 | 0.0004264294632886949 | 8.36758018392599E-06 | - | 0.000636027443387459 | Enthaltung: Praefix | - |
| p17 | s06/k3 | 0.004251355320261391 | 0.004568116194779856 | 0.004567858228216437 | 0.004093060318919926 | H2 | NEXT_WRONG |
| p18 | s06/k4 | 0.0010262498040200126 | 0.0030723466667329723 | 0.013159416355125348 | 4.590523277203951E-06 | H1 | NEXT_BEST |

## Absolute Gewinne und Verluste

Je Vergleich `MAE(Kontrolle) - MAE(Arm)`: positiv WIN, negativ LOSS,
numerisch null TIE. `R` bezeichnet ausschliesslich die ausgegebene Empfehlung.
Keine Bestarmwahl im Bericht. Fehlende Empfehlung bleibt `-`, kein Nullgewinn.
Saemtliche zusaetzlich gespeicherten NY-Empfehlungsvergleiche mit H1/H2
stehen unveraendert in evaluation.json; hier sind die verlangten
LOCAL-/PERSIST-Beziehungen vollstaendig ausgewiesen.

| Stelle | H1 vs LOCAL | H2 vs LOCAL | R vs LOCAL | H1 vs PERSIST | H2 vs PERSIST | LOCAL vs PERSIST | R vs PERSIST |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| p01 | - | - | - | 0.00021040511555759733 | -0.0002104051233021363 | - | - |
| p02 | 1.5685828352675306E-13 | -0.00010520255507376657 | 1.5685828352675306E-13 | 5.260127280970562E-05 | -5.260128242091924E-05 | 5.2601272652847335E-05 | 5.260127280970562E-05 |
| p03 | 3.3494353737369643E-13 | -2.6300630811090682E-05 | 3.3494353737369643E-13 | 1.3150316970739814E-05 | -1.3150314175294405E-05 | 1.3150316635796277E-05 | 1.3150316970739814E-05 |
| p04 | - | - | - | 0.00020810636499038004 | -0.00021225561318346332 | - | - |
| p05 | -2.3428953727684264E-09 | -0.0001065175176452221 | -2.3428953727684264E-09 | 5.113349388568874E-05 | -5.538168086416058E-05 | 5.113583678106151E-05 | 5.113349388568874E-05 |
| p06 | 8.370166836695951E-10 | -2.7258109644934685E-05 | 8.370166836695951E-10 | 1.1452152842990802E-05 | -1.5806793818627552E-05 | 1.1451315826307133E-05 | 1.1452152842990802E-05 |
| p07 | - | - | - | 0.00021040512348646708 | 0.0006312153607871077 | - | - |
| p08 | -0.0003156076675455945 | 4.775817612846397E-12 | 4.775817612846397E-12 | 0.00015780384467391825 | 0.00047341151699533036 | 0.00047341151221951276 | 0.00047341151699533036 |
| p09 | -0.00023670574213444377 | -3.685373336196542E-13 | -3.685373336196542E-13 | 0.00011835288054231626 | 0.0003550586223082227 | 0.00035505862267676004 | 0.0003550586223082227 |
| p10 | - | - | - | 0.00020982249015576648 | 0.0006276455658600885 | - | - |
| p11 | -0.00031341256152725644 | 3.697467499720382E-07 | 3.697467499720382E-07 | 0.0001569745587465893 | 0.0004707568670238178 | 0.00047038712027384574 | 0.0004707568670238178 |
| p12 | -0.00023195941110751124 | 3.286453337807176E-07 | 3.286453337807176E-07 | 0.00011718871994420845 | 0.0003494767763855004 | 0.0003491481310517197 | 0.0003494767763855004 |
| p13 | - | - | - | 0.00021040512348646708 | 0.0006312153607871077 | - | - |
| p14 | 0.00031560623673356023 | 4.775817762092682E-12 | 4.775817762092682E-12 | -0.00015780311431886317 | -0.00047340934627660564 | -0.0004734093510524234 | -0.00047340934627660564 |
| p15 | 0.012194432957563499 | 0.01014302857955515 | 0.012194432957563499 | -0.0010257021890699356 | -0.003077106567078283 | -0.013220135146633434 | -0.0010257021890699356 |
| p16 | - | - | - | 0.0002095979800987641 | 0.000627659863203533 | - | - |
| p17 | 0.00031650290795504597 | -2.579665634187475E-07 | -2.579665634187475E-07 | -0.00015829500134146527 | -0.00047505587585993 | -0.00047479790929651124 | -0.00047505587585993 |
| p18 | 0.012133166551105336 | 0.010087069688392375 | 0.012133166551105336 | -0.0010216592807428086 | -0.0030677561434557686 | -0.013154825831848144 | -0.0010216592807428086 |

## Abdeckung und getrennte Verlaufsergebnisse

Je Folge N=3 Prognosestellen, davon zwoelf insgesamt mit ausreichendem
Praefix. Empfehlungen insgesamt D=12/18, bei ausreichendem Praefix 12/12.
Sechs ABSTAIN_INSUFFICIENT_PREFIX, keine ABSTAIN_TIE. Unter den zwoelf
Empfehlungen 10 NEXT_BEST, 2 NEXT_WRONG, 0 NEXT_TIE.
Die folgenden Zaehler sind WIN/TIE/LOSS, keine kompensierte Gesamtsumme.

| Folge | Kategorie | N / Empfehlungs-D | H1 vs LOCAL (D=2) | H2 vs LOCAL (D=2) | R vs LOCAL (D=2) | R vs PERSIST (D=2) |
| --- | --- | --- | --- | --- | --- | --- |
| s01 | H1 sauber | 3 / 2 | 2/0/0 | 0/0/2 | 2/0/0 | 2/0/0 |
| s02 | H1 gestoert | 3 / 2 | 1/0/1 | 0/0/2 | 1/0/1 | 2/0/0 |
| s03 | H2 sauber | 3 / 2 | 0/0/2 | 1/0/1 | 1/0/1 | 2/0/0 |
| s04 | H2 gestoert | 3 / 2 | 0/0/2 | 2/0/0 | 2/0/0 | 2/0/0 |
| s05 | Wechsel sauber | 3 / 2 | 2/0/0 | 2/0/0 | 2/0/0 | 0/0/2 |
| s06 | Wechsel gestoert | 3 / 2 | 2/0/0 | 1/0/1 | 1/0/1 | 0/0/2 |

Der Schwerpunkt p05/p06/p11/p12 bleibt vollstaendig: N=4, D=4.
H1 vs LOCAL: 1/0/3; H2 vs LOCAL: 2/0/2; Empfehlung vs LOCAL: 3/0/1.
H1 vs PERSIST: 4/0/0; H2 vs PERSIST: 2/0/2; Empfehlung vs PERSIST: 4/0/0.
Die Empfehlung ist nicht identisch mit einem einzelnen festen Historienarm.

Am ersten Wechselziel p14/p17: jeweils H2 empfohlen, jeweils NEXT_WRONG;
beide Empfehlungen verlieren gegen PERSIST. Im Folgefenster p15/p18:
jeweils H1 empfohlen und NEXT_BEST, aber ebenfalls Verlust gegen PERSIST.
Diese Verluste werden durch LOCAL-Gewinne nicht aufgehoben.
