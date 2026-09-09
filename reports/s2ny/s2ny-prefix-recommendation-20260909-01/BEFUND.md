# S2-NY: realer praefixgebundener Empfehlungs-/LOCAL-Vergleich

## Technischer Abschluss

Lauf-ID `s2ny-prefix-recommendation-20260909-01`, neues Ergebnisverzeichnis.
Genau ein `run_main_once`, anschliessend genau ein `verify_file_once`, erst
nach dessen Bestehen genau ein `evaluate_file_once`. Exit-Code 0, kein Retry.
Keine Produkt-, Quellen-, Parameter- oder Grenzaenderung und kein Vorlauf.

**RECORDING_COMPLETE**, **S2NY_PREDICTION_VERIFIED**, danach
**FUNCTIONALLY_EVALUATED**. Technisch gueltiger, fachlich begrenzter Befund
mit Fortsetzungsgewinnen und eigenstaendigen Fehl- und Wechselbefunden.

| Beleg | Kanonischer Digest |
| --- | --- |
| [Gesamtbeleg](result.json) | `3a0ba3cd84f117fd2d6300ad44d0da80d3ba9ba13c9b58b20aff560c33f7a788` |
| [Read-only-Verifikation](verification.json) | `64f535bbb32efa91a4c8f17b49fc3a736095078de7b052190fbf76c34d0f278d` |
| [Getrennte Auswertung](evaluation.json) | `30b552b1390a465258e948f36cb0aa4ebf458a8798fec33c01dbfef02de1d020` |

[Vorregistrierung](preregistration.json) bindet Quellen, Versionen und Budgets.
Die 43 qualifizierten Datei-SHA-256 wurden vor Materialisierung und nach Lauf
identisch gebunden. Das historische Siegel und die NX-Belege sind unveraendert.
Ergebnisdatei vor/nach Verifikation SHA-256
`328fe99e50ee2eb1d4b9069796f47427dbdec9bb351b9e132fd291799f11d0d0`.

## Kausalitaet und Ressourcen

30 PCM-Fenster einzeln erzeugt, 30 Payloadhashes vor Analyse bestaetigt,
30 direkte Rezeptoranalysen, 30 NJ-Projektionen, 30 abgeschlossene Fenster.
Keine Deduplizierung, rollende Pipeline oder separate Vorabmaterialisierung.
Je 1.440 Roh-/Halbwerte gespeichert, keine PCM-Rohpayloads; ein Fenster
mit 19.200 Byte gleichzeitig. Sechs getrennte Fuenferfolgen ordnungsgemaess
geschlossen, Praefix und Fehlerhistorie jeweils zurueckgesetzt.

18 Stellen je Rechenarm, davon zwoelf mit frischer LOCAL-Schaetzung.
Alle Prognosen, LOCAL und Empfehlung wurden ueber den qualifizierten
Praefixpfad vor dem naechsten Ziel-Reader gebunden. Die Empfehlung verwendet
nur die belegten H1-/H2-Fehler der unmittelbar vorherigen Stelle derselben
Folge; keine nachtraegliche Armwahl. An k=2 keine Empfehlung/LOCAL; bei
Gleichstand keine Ersatzprognose. Enthaltungs-MAE bleiben null.

NX-Freeze-Import unveraendert:
`a897b32ef204947af6e08ef5770e23c921b422da73b06b92d9bf08189c77c07f`.
H1 alpha `0.2500000003063012` (`0x1.0000000543208p-2`),
H2 alpha `0.7500000008868464` (`0x1.800000079e322p-1`).
Keine Lernkettenwiederholung, Owneroeffnung oder Updates.

Je Implementierung: 66 Prognosevektoren, je 2.304 Prognosesubtraktionen,
-multiplikationen und -additionen, 864 Persistenzkopien; je 1.152 lokale
Differenzen/Produkte/Additionen, 12 Fits mit 10 Divisionen; 3.168 Fehlerterme,
66 MAE und 88 von hoechstens 96 Gewinndifferenzen. Primaer und Direkt gleich.
Die zwei Nullnenner an s04/k3,k4 sind regulaere LOCAL-Faelle.

Die einmalige Offline-Pruefung verwendete getrennt 1.440 Halbierungen,
je 4.608 Prognoseoperationen, 1.728 Kopien, je 2.304 lokale Operationen,
24 Fitpruefungen/20 Divisionen, 6.336 Fehlerterme, 132 MAE,
36 Empfehlungspruefungen und 176 Gewinnpruefungen. Keine Rezeptor-/NJ-
Wiederholung. Gesamtdatei 818.036/2.097.152 Byte; Verifikation 994/262.144,
Auswertung 15.299/262.144 Byte. Alle gebundenen Grenzen eingehalten.

## Abdeckung und getrennte Kontrollen

Empfehlungen **10/18 insgesamt**, **10/12 bei ausreichendem Praefix**.
Sechs `ABSTAIN_INSUFFICIENT_PREFIX`, zwei `ABSTAIN_TIE`.
Unter den zehn Empfehlungen: **9/10 NEXT_BEST, 1/10 NEXT_WRONG,
0/10 NEXT_TIE**. Kein Empfehlungsfehler oder -gewinn fuer Enthaltungen.

| Folge | N / ausreichend / D | NEXT_BEST / WRONG / TIE | Empfehlung gegen PERSIST W/T/L | gegen LOCAL W/T/L |
| --- | --- | --- | --- | --- |
| s01 Fortsetzung H1 | 3 / 2 / 2 | 2 / 0 / 0 | 2 / 0 / 0 | 2 / 0 / 0 |
| s02 Fortsetzung H2 | 3 / 2 / 2 | 2 / 0 / 0 | 2 / 0 / 0 | 2 / 0 / 0 |
| s03 beschleunigt/unpassend | 3 / 2 / 2 | 2 / 0 / 0 | 2 / 0 / 0 | 0 / 0 / 2 |
| s04 Stillstand | 3 / 2 / 0 | 0 / 0 / 0 | ungeprueft | ungeprueft |
| s05 Umkehr | 3 / 2 / 2 | 2 / 0 / 0 | 1 / 0 / 1 | 2 / 0 / 0 |
| s06 Gruppenwechsel | 3 / 2 / 2 | 1 / 1 / 0 | 0 / 0 / 2 | 2 / 0 / 0 |

s04: D=0 bedeutet `NUTZEN_NICHT_GEPRUEFT`, nicht erfolgreichen
Empfehlungsnutzen. Die vier Kontrollen haben dort Nullfehler, aber es gibt
keine ausgegebene Empfehlung. Die Kategorien bleiben Evaluationsrollen.

## Alle 20 vorgebundenen Kriterien

| Kriterium | Stelle | Bedingung bei ausgegebener Empfehlung | Ergebnis |
| --- | --- | --- | --- |
| R01 | p02 | NEXT_BEST | CONFIRMED |
| R02 | p03 | NEXT_BEST | CONFIRMED |
| R03 | p05 | NEXT_BEST | CONFIRMED |
| R04 | p06 | NEXT_BEST | CONFIRMED |
| L01 | p02 | MAE < LOCAL | CONFIRMED |
| L02 | p03 | MAE < LOCAL | CONFIRMED |
| L03 | p05 | MAE < LOCAL | CONFIRMED |
| L04 | p06 | MAE < LOCAL | CONFIRMED |
| P01 | p02 | MAE < PERSIST | CONFIRMED |
| P02 | p03 | MAE < PERSIST | CONFIRMED |
| P03 | p05 | MAE < PERSIST | CONFIRMED |
| P04 | p06 | MAE < PERSIST | CONFIRMED |
| W01 | p14 | MAE > PERSIST | CONFIRMED |
| W02 | p14 | MAE > LOCAL | FALSIFIED |
| W03 | p15 | MAE > PERSIST | FALSIFIED |
| W04 | p15 | MAE > LOCAL | FALSIFIED |
| W05 | p17 | MAE > PERSIST | CONFIRMED |
| W06 | p17 | MAE > LOCAL | FALSIFIED |
| W07 | p18 | MAE > PERSIST | CONFIRMED |
| W08 | p18 | MAE > LOCAL | FALSIFIED |

R 4/4, L 4/4, P 4/4. W 3/8: fuenf vorgebundene Verlustprognosen treten
nicht ein; das ist ein regulaerer Funktionsbefund, kein technischer Fehler.
Keine Gesamtpunktzahl verrechnet Fortsetzungsgewinne und Wechselverluste.

## Absoluter Nutzen und eigenstaendige Verluste

Alle 66 MAE-Einzelwerte, 88 absoluten Gewinndifferenzen und 18 Urteile sind
in [EINZELWERTE.md](EINZELWERTE.md) sowie unverkuerzt im Auswertungs-JSON
ausgewiesen. Positiver Gewinn bedeutet Kontroll-MAE minus Empfehlungs-MAE.

Die vier Fortsetzungsgewinne gegen LOCAL betragen nur
`1.3269196726676544e-13`, `4.607284183561149e-14`,
`1.3465600875849741e-12`, `2.4857686571392354e-12`.
Die zugehoerigen Empfehlungs-MAE liegen zwischen etwa 9.58e-12 und 2.17e-11.
Damit besteht das strikte vorgebundene L-Kriterium; diese kleine absolute
Differenz begruendet keine allgemeine Robustheit oder bevorzugte Systemregel.

s03: Die Empfehlung ist zweimal die bessere der beiden Historien, verliert
aber gegen LOCAL: Gewinne `-0.000702783863265659` (p08) und
`-0.000281113556103299` (p09). NEXT_BEST bedeutet nur besser als die andere
eingefrorene Historie, nicht insgesamt passend oder besser als lokale Evidenz.

s05: Am Umkehrziel p14 NEXT_BEST und minimal besser als LOCAL, aber Verlust
gegen PERSIST `-0.00005270879147458051`. Im Folgefenster p15 gewinnt H1
gegen beide Kontrollen. Dieser Folgegewinn hebt den Wechselverlust nicht auf.

s06: Am Gruppenwechsel p17 wird H2 empfohlen, obwohl H1 danach besser ist:
NEXT_WRONG. Gegen PERSIST Verlust `-0.00047437480367466117`; der winzige
LOCAL-Vorteil `1.3465556794600708e-12` korrigiert diese Fehlentscheidung nicht.
Im Folgefenster p18 H1/NEXT_BEST, aber erneut Verlust gegen PERSIST
`-0.001026584284749542`; PERSIST hat dort Nullfehler. LOCAL ist noch schlechter.
Vergangene bessere Fehler garantieren damit weder die bessere Historie nach
einem unangekuendigten Wechsel noch eine bessere Prognose als Persistenz.

## Aussagegrenze und Ende des freigegebenen Laufs

Beobachtet ist begrenzte praefixgebundene Historienempfehlung mit einem
sehr kleinen Fortsetzungsvorteil gegen LOCAL auf diesem Bestand. Gemeinsame
Praefixe sind keine unabhaengigen Replikate. Kein Nachweis von Quellenidentitaet,
sicherer Wechselerkennung, allgemeiner Anwendbarkeit oder neuem Lernen in NY.
Kein bevorzugter Arm wurde nachtraeglich ausgewaehlt.

Offline-Pruefung: numerische gespeicherte Halbierungen und Rechnungen plus
Bindungen; keine historische CPU-Aufrufordnung allein aus Digests beweisbar.
Die kausale Grenze beruht auf dem zuvor neutral qualifizierten Aufrufpfad.

Gates nach Hauptaufruf und Verifikation `False`; keine Memory-, Feld-,
Kontext- oder Runtimeaufrufe. ME/MI und Systemintegration bleiben gesperrt.
Versiegelung, historische Belege, fremde Aenderungen und Bootstrap unveraendert.

WEITER: Am besten geht es jetzt mit der Analystenbewertung des getrennten
Historien-, LOCAL- und Wechselbefunds weiter, ohne erneuten NY-Lauf.
