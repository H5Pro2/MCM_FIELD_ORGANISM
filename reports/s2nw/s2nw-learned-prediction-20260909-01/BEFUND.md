# S2-NW: einmaliger realer Lern-/Transferlauf

Lauf-ID: `s2nw-learned-prediction-20260909-01`.
Technik: **RECORDING_COMPLETE**, einmal **S2NW_LEARNING_VERIFIED**,
anschliessend einmal getrennt **FUNCTIONALLY_EVALUATED**.
Primaere Fortsetzungsprognose: **CONFIRMED**, sechs von sechs Bedingungen.
Getrennte Wechselverlustprognosen: drei von drei bestaetigt. Diese Verluste
sind keine Gewinne und kompensieren keinen anderen Befund.

## Ausfuehrung und Beleggrenzen

Genau ein `run_main_once`-Aufruf auf der unveraenderten Vorversiegelung,
keine zusaetzliche Qualifikation, separate Vorabmaterialisierung oder
Wiederholung. Gate nur im Prozess fuer diesen Aufruf geoeffnet, danach im
`finally` geschlossen; NW-, Quellen- und NV-Gate abschliessend `False`.
Qualifizierte Quelldateien blieben unveraendert.

- 26 getrennte PCM-Erzeugungen, 26 Hashpruefungen vor Analyse, 26 direkte
  Rezeptoranalysen und 26 NJ-Projektionen. Keine Deduplizierung.
- Je 1.248 gespeicherte Roh-/Halbwerte, keine PCM-Rohpayloadablage,
  hoechstens ein PCM-Fenster zugleich; keine rollenden Hops.
- Vier Lernprognosen, jeweils Bindung aller drei Arme und Direktnachrechnung
  vor Zielerzeugung, danach Beobachtung, Fehlerbindung und erst dann Update.
- Vier Updates je unabhaengigem Lerner, danach Freeze. Zwoelf Pruefprognosen
  mit identischer Freeze-Bindung; frischer Praefix pro Folge, keine Testupdates.
- Beide Implementierungen: insgesamt 96 Prognosevektoren, 4.608 Fehlerterme,
  96 MAE-Summen und 64 Gewinne. Die vier Updates je Implementierung verwenden
  je 384 Differenzen, Produkte und Akkumulatoradditionen sowie vier Divisionen.
- Zusaetzliche einmalige Offline-Pruefung: 1.248 Halbierungen, 3.072
  Prognosesubtraktionen/-additionen je Art, 1.536 Multiplikationen/Kopien
  je Art, 768 Updatedifferenzen/-produkte/-additionen je Art, acht
  Updates/Divisionen und weitere 4.608 Fehlerterme, 96 Summen, 64 Gewinne.
- Gesamtbeleg 656.904 / 2.097.152 Byte; Pruefung 1.001 / 262.144 Byte;
  Auswertung 7.593 / 262.144 Byte; Preregistrierung 5.362 / 65.536 Byte.
- Keine Memory-, Feld-, Kontext- oder Runtimeaufrufe. ME/MI bleiben gesperrt.

[Preregistrierung](preregistration.json), [Gesamtbeleg](result.json),
[unabhaengige Verifikation](verification.json), [getrennte Auswertung](evaluation.json).
Exklusive Verifikations-/Auswertungsclaims sind gespeichert. Die Direkt-
Lernzustandsketten, Prognosen und Fehler sind exakt baselinegleich.

| Bindung | Digest |
| --- | --- |
| Ausfuehrungsplan | `96b902af68ffb2662aaa6995756b1ca6c435b157012b17cb1065b18c7d5a4a7c` |
| Historische Versiegelung | `9df2bc5147c6e85f51eb1a628bf2f0fffcf851e6037c74f52cfc2b5ef4fe4a65` |
| Gesamtbeleg | `cfd29880d965138f753db703eba316b767b4f6cb6f4d1b17a39580e736f4431a` |
| Verifikation | `435cd9776dd32ac708cb5e1a97a93b69729c127cd6c65626bbc5fcddd739b8a1` |
| Auswertung | `54c3502103b5447a6d4029f3d3dd9780d90860b48b0b7e77314eaf02198f9e70` |
| Ergebnisdatei vor/nach Verifikation | `0f69762916632c89d5343fa0790a921356cba320b047cb98288dc6d34ea04cea` |

## Tatsaechlicher Lernzustand

Primaer- und Direktlerner beginnen unabhaengig mit positiven Binary64-
Nullwerten. Die folgenden Werte sind aus den gespeicherten realen Belegen
uebernommen, keine Nachrechnung oder Uebernahme des neutralen Beispiel-Fits.
Jede Zeile zeigt den Zustand **nach** dem zugehoerigen Update; die Prognose
dieser Stelle verwendete noch den vorherigen Koeffizienten.

| Zustand | n | Sxx | Sxy | alpha |
| --- | --- | --- | --- | --- |
| Initial | 0 | 0.0 | 0.0 | 0.0 |
| nach t01 | 1 | 0.0008590188243815615 | 0.000429509408668601 | 0.4999999958997641 |
| nach t02 | 2 | 0.0010737735269547722 | 0.0005368867610489296 | 0.4999999977383904 |
| nach t03 | 3 | 0.0011274622036917985 | 0.0005637310996491045 | 0.499999998051558 |
| nach t04 / Freeze / Close | 4 | 0.001140884373107718 | 0.000570442184412696 | 0.49999999812324286 |

Alle vier Updatebelege melden `zero_denominator=False`,
`division_performed=True` und leere Subnormal-/Produktunterlauf-Indizes.
Primaer und Direkt stimmen in jeder Zustandsbindung ueberein.
Der tatsaechliche Koeffizient ist nicht bitgleich mit dem neutralen `.5`.
Freeze-Digest: `96191b933af1129cd8bb50e7caa735093e236a645b8bb84dc59e47be5520f576`.
Close-Digest: `852ded4f1fb23cfe0ad170c9e0d2cde707f1cf400306a8218126024c4f020b79`.
Die unterschiedlichen Phasen-/Kettendigests aendern keine numerischen Werte.
Alle Vorgaenger- und Beobachtungsdigests stehen vollstaendig in `result.json`.

## Alle MAE-Einzelwerte

L = LEARNED_DELTA, P = PERSIST, X = LINEAR. Zahlen unverkuerzt aus der
gespeicherten Auswertung; keine erneute Prognose-/Fehlerberechnung.
Die Trainingsstellen verwenden nacheinander alpha `0.0`,
`0.4999999958997641`, `0.4999999977383904`, `0.499999998051558`.
Alle Pruefstellen verwenden `0.49999999812324286`.

| Stelle | Folge / Ziel k | MAE L | MAE P | MAE X |
| --- | --- | --- | --- | --- |
| t01 | l01 / 2 | 0.000567862409885515 | 0.000567862409885515 | 0.0005678624226605305 |
| t02 | l01 / 3 | 1.8867213920342846e-11 | 0.000283931206654612 | 0.000283931203937455 |
| t03 | l01 / 4 | 1.4878726544136683e-11 | 0.00014196560142985012 | 0.00014196561009092236 |
| t04 | l01 / 5 | 1.3275733233977538e-11 | 7.098280672483683e-05 | 7.098280494646958e-05 |
| p01 | s01 / 2 | 1.2512427812977601e-11 | 0.0002816626028334812 | 0.0002816626155555724 |
| p02 | s01 / 3 | 1.532407656321822e-11 | 0.00014083131167448123 | 0.00014083129830987152 |
| p03 | s01 / 4 | 1.4340890123922901e-11 | 7.04156540830176e-05 | 7.041566364076861e-05 |
| p04 | s02 / 2 | 1.2512427812977601e-11 | 0.0002816626028334812 | 0.0002816626155555724 |
| p05 | s02 / 3 | 0.00042249390372160945 | 0.0002816626028334812 | 0.0005633252056669623 |
| p06 | s02 / 4 | 1.6853530386829357e-11 | 0.00014083130931753408 | 0.00014083129873024137 |
| p07 | s03 / 2 | 1.2512427812977601e-11 | 0.0002816626028334812 | 0.0002816626155555724 |
| p08 | s03 / 3 | 0.0001408313008881283 | 0.0 | 0.0002816626028334812 |
| p09 | s03 / 4 | 0.0 | 0.0 | 0.0 |
| p10 | s04 / 2 | 1.2512427812977601e-11 | 0.0002816626028334812 | 0.0002816626155555724 |
| p11 | s04 / 3 | 0.004563949745057889 | 0.004423119180911094 | 0.004704780310530317 |
| p12 | s04 / 4 | 0.0022115595821544268 | 0.0 | 0.004423119180911094 |

## Gewinne und Verluste getrennt

Gewinn ist der gespeicherte Wert `MAE_Baseline - MAE_L`. Kein Gesamtmittel,
keine Verrechnung negativer Werte mit positiven. WIN/TIE/LOSS aus Sicht L.

| Stelle | Gewinn gegen P | Urteil P | Gewinn gegen X | Urteil X |
| --- | --- | --- | --- | --- |
| t01 | 0.0 | TIE | 1.2775015528938838e-11 | WIN |
| t02 | 0.00028393118778739806 | WIN | 0.00028393118507024105 | WIN |
| t03 | 0.0001419655865511236 | WIN | 0.00014196559521219583 | WIN |
| t04 | 7.09827934491036e-05 | WIN | 7.098279167073635e-05 | WIN |
| p01 | 0.00028166259032105334 | WIN | 0.00028166260304314457 | WIN |
| p02 | 0.00014083129635040467 | WIN | 0.00014083128298579496 | WIN |
| p03 | 7.041563974212747e-05 | WIN | 7.041564929987848e-05 | WIN |
| p04 | 0.00028166259032105334 | WIN | 0.00028166260304314457 | WIN |
| p05 | -0.00014083130088812828 | LOSS | 0.0001408313019453529 | WIN |
| p06 | 0.00014083129246400368 | WIN | 0.00014083128187671097 | WIN |
| p07 | 0.00028166259032105334 | WIN | 0.00028166260304314457 | WIN |
| p08 | -0.0001408313008881283 | LOSS | 0.00014083130194535287 | WIN |
| p09 | 0.0 | TIE | 0.0 | TIE |
| p10 | 0.00028166259032105334 | WIN | 0.00028166260304314457 | WIN |
| p11 | -0.00014083056414679503 | LOSS | 0.0001408305654724282 | WIN |
| p12 | -0.0022115595821544268 | LOSS | 0.002211559598756667 | WIN |

| Folge | Phase / Nenner je Baseline | gegen P: WIN/TIE/LOSS | gegen X: WIN/TIE/LOSS |
| --- | --- | --- | --- |
| l01 | Training, N=4 | 3/1/0 | 4/0/0 |
| s01 | Fortsetzung, N=3 | 3/0/0 | 3/0/0 |
| s02 | Umkehr, N=3 | 2/0/1 | 3/0/0 |
| s03 | Stillstand, N=3 | 1/1/1 | 2/1/0 |
| s04 | unangekuendigter Gruppenwechsel, N=3 | 1/0/2 | 3/0/0 |

In jeder Prueffolge ist k=2 der gemeinsame Anstieg, k=3 das erste
Zweigziel und k=4 das Folgefenster, jeweils N=1 pro Baseline.
Nach Umkehr gewinnt L im Folgefenster wieder gegen beide Baselines;
nach Stillstand herrscht Gleichstand; nach Gruppenwechsel bleibt ein
weiterer Verlust gegen Persistenz. Der Gewinn gegen LINEAR beseitigt
diesen Persistenzverlust nicht. Trainingsgewinne zaehlen nicht als Transfer.

## Neun vorgebundene Bedingungen

| ID | Stelle | Strikte Bedingung | Ergebnis |
| --- | --- | --- | --- |
| o01 | p01 | MAE L < MAE P | bestanden |
| o02 | p01 | MAE L < MAE X | bestanden |
| o03 | p02 | MAE L < MAE P | bestanden |
| o04 | p02 | MAE L < MAE X | bestanden |
| o05 | p03 | MAE L < MAE P | bestanden |
| o06 | p03 | MAE L < MAE X | bestanden |
| o07 | p05 | MAE L > MAE P | Wechselverlust bestaetigt |
| o08 | p08 | MAE L > MAE P | Wechselverlust bestaetigt |
| o09 | p11 | MAE L > MAE P | Wechselverlust bestaetigt |

Die Primaerbewertung verlangt zusaetzlich einen aus vier Updates belegten,
nichtinitialen Freeze-Zustand mit `Sxx>0`; dies ist erfuellt. Keine Schwelle
oder Toleranz wurde aus den Ergebnissen abgeleitet. Der sehr kleine t01-
Gewinn gegen LINEAR bleibt die tatsaechliche strikte Binary64-Entscheidung,
kein zusaetzlicher belastbarer Transfernachweis.

## Interpretation und Nichtnachweise

Belegt ist ein aus real beobachteten Uebergaengen geschaetzter Koeffizient,
der nach Einfrieren innerhalb der gebundenen Dynamikklasse auf einem anderen
Ton-/Phasenbestand Fortsetzungen besser vorhersagt als beide festen
Baselines. Es handelt sich um die vorgegebene skalare Anpassung, keine
Algorithmuswahl oder besondere Memorymechanik. Die Direktbaseline erklaert
den Effekt vollstaendig.

Bei unangekuendigter Umkehr, Stillstand und Gruppenwechsel verursacht die
gelernte Fortsetzungsannahme gegenueber Persistenz zusaetzliche Fehler.
Identische Praefixe enthalten keine Information ueber ihren spaeteren Zweig;
die mehrfachen gemeinsamen Anstiege sind keine unabhaengigen Replikate.
Der Verlauf wurde nicht als Objekt-, Quellen- oder zulaessige Variantenbindung
gelernt. Vorhersagefehler bedeuten weder Quellenwechselnachweis noch Stress.

Die Offline-Pruefung bestaetigt gespeicherte Zahlen und Ketten, aber allein
keine historische CPU-Reihenfolge. Die kausale Grenze beruht auf dem
unveraenderten qualifizierten Aufrufpfad. Keine allgemeine Generalisierung,
kein allgemeines Sequenzlernen, keine Integration und keine Entsperrung von
ME/MI. Historische Versiegelung und fruehere Befunde bleiben unveraendert.

WEITER: Am besten geht es jetzt mit der Analystenbewertung dieses begrenzten
eingefrorenen Transfernutzens und seiner getrennten Wechselverluste weiter.
