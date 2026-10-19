# MCM-KI: nichtpersistenter XYX-Vergleich abgeschlossen

2026-10-03. Genau einmal,Exit0:48 Quellpositionen,240 Arm-Aufnahmen plus240 interne Referenzfortschreibungen.
**AUSWAHL_X_Y_X: BELEGT. Nettonutzen auf H: BELEGT. Gesamtnutzen auf G: BELEGT.**
Alle Befunde gelten fuer den festgelegten Entwicklungskontrast. Unabhaengiger Evaluationsnutzen NICHT_GEPRUEFT; Defaults deaktiviert.
Keine technischen Fehler,keine Abweichungen der Entscheidungen oder Fehlerpaare von den statischen Erwartungen. Keine Wiederholung,Ersatzfolge,Parameter- oder Policyaenderung.
64 gebundene Dateien,Plan,Vertrag und Laufzeit unveraendert. Autorisierung ausschliesslich im Status geaendert; Einmalfreigabe verbraucht. Endziel49 zensiert,Ausgaben freigegeben.

## Alle sieben Zielmengen

Je Feld Fehlersumme / MAE; keine fehlenden Ziele. H/N partitionieren G; S/F/A_W/A_R bleiben getrennte,ueberlappende Diagnosen. Kontextabdeckung aller Arme je Ziel in all-target-sets.json.

| Menge | Ziele | U | M | E | K | P |
|---|---|---:|---:|---:|---:|---:|
| G | 3,5,7,9,11,13,15,17,19,21,23,25,27,29,31,33,35,37,39,41,43,45,47 | 10.0 / 0.43478260869565216 | 12.25 / 0.532608695652174 | 12.75 / 0.5543478260869565 | 11.75 / 0.5108695652173914 | 13.25 / 0.5760869565217391 |
| H | 7,11,15,19,23,27,31,35,39,43,47 | 1.25 / 0.11363636363636363 | 3.5 / 0.3181818181818182 | 4.0 / 0.36363636363636365 | 3.0 / 0.2727272727272727 | 4.5 / 0.4090909090909091 |
| N | 3,5,9,13,17,21,25,29,33,37,41,45 | 8.75 / 0.7291666666666666 | 8.75 / 0.7291666666666666 | 8.75 / 0.7291666666666666 | 8.75 / 0.7291666666666666 | 8.75 / 0.7291666666666666 |
| S | 11,15 | 0.0 / 0.0 | 0.0 / 0.0 | 0.5 / 0.25 | 0.0 / 0.0 | 1.0 / 0.5 |
| F | 19,35 | 0.5 / 0.25 | 0.75 / 0.375 | 0.75 / 0.375 | 0.75 / 0.375 | 0.75 / 0.375 |
| A_W | 23,27,31 | 0.25 / 0.08333333333333333 | 0.75 / 0.25 | 0.75 / 0.25 | 0.75 / 0.25 | 0.75 / 0.25 |
| A_R | 39,43,47 | 0.0 / 0.0 | 1.5 / 0.5 | 1.5 / 0.5 | 1.5 / 0.5 | 1.5 / 0.5 |

## Identitaet und kausale Auswahl

X: Originalframes1..4,Nachfolgerordinal3 mit Wert13/16; nach Promotion retained-Key(Rolle0,Generation1,Offset0,EXACT).
Y: Originalframes17..20,Nachfolgerordinal19 mit Wert9/16; zuerst candidate-Key(1,2,0,EXACT),ab Promotion24 retained-Key(0,2,0,EXACT). Persistenz ist5/16.
Keys,Originalordinalen,Hintwerte,Zeitgrenzen,Read-Revision und vollstaendige Treffer wurden gegen eingefrorene Receipts,Feedbackbelege und normale Bestandsereignisse geprueft. Keine Identifikation ueber feste Ticketnummern.
11/15: warme X-Auswahl aus Feedback7 bzw.7/11; direkte Promotion bei8 erhaelt diese Erfahrung.
19: erster Wechsel,X gewaehlt,Fehler1/4. Danach X=(1/8,3/8),d=-1/4; Y noch nicht gespeichert.
23: Y ist vorhanden,aber kalt. U waehlt weiterhin warmes X,Fehler1/4. Dieser erwartete Verzoegerungsverlust bleibt enthalten. Feedback23 aktualisiert X zu(3/16,5/16) und das NICHT ausgewaehlte Y zu(0,1/4).
24: Y:c2->r2 erhaelt sein Fehlerpaar und seine Originalframes. Keine Ticketumleitung oder zusaetzliche Beobachtung.
27: beide Kontextfortsetzungen warm und besser als P; d_X=-1/8,d_Y=-1/4. U waehlt tatsaechlich Y mit Nachfolgerordinal19,Fehler0. An31 bleibt Y gewaehlt. Vorangehendes Y-Feedback:23 bzw.23/27.
35: erste Rueckkehr,Y gewaehlt,Fehler1/4. Feedback35 bewertet auch das NICHT ausgewaehlte X: X=(15/128,49/128),Y=(1/8,3/8).
39: d_X=-17/64<d_Y=-1/4; U waehlt tatsaechlich X mit Nachfolgerordinal3. Feedback35 ist der neue Rueckkehrbeleg. X bleibt an43/47 gewaehlt,je Fehler0. Die Frist43 ist bereits an39 erfuellt.
Keine dieser gewerteten Kontextentscheidungen ist P,Kaltwahl oder Gleichstand. Die Herkunft bleibt bei Konkurrenz mehrdeutig.
Wichtig: Y an35 ist trotz0.25 Vorteil gegen jede Baseline weiterhin eine falsche Fortsetzung und zaehlt nicht als gelungene Rueckkehr. Die Wahl an23 ist ebenfalls kein Erfolg.

## Saemtliche eingefrorenen Entscheidungen und Einzelfehler

| Ziel | U | Grund U | Fehler U/M/E/K/P | U-M / U-E / U-K / U-P |
|---:|---|---|---|---|
| 3 | P | NO_ELIGIBLE_CONTEXT | 0.5 / 0.5 / 0.5 / 0.5 / 0.5 | 0.0 / 0.0 / 0.0 / 0.0 |
| 5 | P | NO_ELIGIBLE_CONTEXT | 0.75 / 0.75 / 0.75 / 0.75 / 0.75 | 0.0 / 0.0 / 0.0 / 0.0 |
| 7 | P | COLD_ONLY | 0.5 / 0.5 / 0.5 / 0.0 / 0.5 | 0.0 / 0.0 / 0.5 / 0.0 |
| 9 | P | NO_ELIGIBLE_CONTEXT | 0.75 / 0.75 / 0.75 / 0.75 / 0.75 | 0.0 / 0.0 / 0.0 / 0.0 |
| 11 | X | SELECTED_BY_ERROR | 0.0 / 0.0 / 0.5 / 0.0 / 0.5 | 0.0 / -0.5 / 0.0 / -0.5 |
| 13 | P | NO_ELIGIBLE_CONTEXT | 0.75 / 0.75 / 0.75 / 0.75 / 0.75 | 0.0 / 0.0 / 0.0 / 0.0 |
| 15 | X | SELECTED_BY_ERROR | 0.0 / 0.0 / 0.0 / 0.0 / 0.5 | 0.0 / 0.0 / 0.0 / -0.5 |
| 17 | P | NO_ELIGIBLE_CONTEXT | 0.75 / 0.75 / 0.75 / 0.75 / 0.75 | 0.0 / 0.0 / 0.0 / 0.0 |
| 19 | X | SELECTED_BY_ERROR | 0.25 / 0.25 / 0.25 / 0.25 / 0.25 | 0.0 / 0.0 / 0.0 / 0.0 |
| 21 | P | NO_ELIGIBLE_CONTEXT | 0.75 / 0.75 / 0.75 / 0.75 / 0.75 | 0.0 / 0.0 / 0.0 / 0.0 |
| 23 | X | SELECTED_BY_ERROR | 0.25 / 0.25 / 0.25 / 0.25 / 0.25 | 0.0 / 0.0 / 0.0 / 0.0 |
| 25 | P | NO_ELIGIBLE_CONTEXT | 0.75 / 0.75 / 0.75 / 0.75 / 0.75 | 0.0 / 0.0 / 0.0 / 0.0 |
| 27 | Y | SELECTED_BY_ERROR | 0.0 / 0.25 / 0.25 / 0.25 / 0.25 | -0.25 / -0.25 / -0.25 / -0.25 |
| 29 | P | NO_ELIGIBLE_CONTEXT | 0.75 / 0.75 / 0.75 / 0.75 / 0.75 | 0.0 / 0.0 / 0.0 / 0.0 |
| 31 | Y | SELECTED_BY_ERROR | 0.0 / 0.25 / 0.25 / 0.25 / 0.25 | -0.25 / -0.25 / -0.25 / -0.25 |
| 33 | P | NO_ELIGIBLE_CONTEXT | 0.75 / 0.75 / 0.75 / 0.75 / 0.75 | 0.0 / 0.0 / 0.0 / 0.0 |
| 35 | Y | SELECTED_BY_ERROR | 0.25 / 0.5 / 0.5 / 0.5 / 0.5 | -0.25 / -0.25 / -0.25 / -0.25 |
| 37 | P | NO_ELIGIBLE_CONTEXT | 0.75 / 0.75 / 0.75 / 0.75 / 0.75 | 0.0 / 0.0 / 0.0 / 0.0 |
| 39 | X | SELECTED_BY_ERROR | 0.0 / 0.5 / 0.5 / 0.5 / 0.5 | -0.5 / -0.5 / -0.5 / -0.5 |
| 41 | P | NO_ELIGIBLE_CONTEXT | 0.75 / 0.75 / 0.75 / 0.75 / 0.75 | 0.0 / 0.0 / 0.0 / 0.0 |
| 43 | X | SELECTED_BY_ERROR | 0.0 / 0.5 / 0.5 / 0.5 / 0.5 | -0.5 / -0.5 / -0.5 / -0.5 |
| 45 | P | NO_ELIGIBLE_CONTEXT | 0.75 / 0.75 / 0.75 / 0.75 / 0.75 | 0.0 / 0.0 / 0.0 / 0.0 |
| 47 | X | SELECTED_BY_ERROR | 0.0 / 0.5 / 0.5 / 0.5 / 0.5 | -0.5 / -0.5 / -0.5 / -0.5 |

## Alle Hypothesenbewertungen vor/nach Feedback

Paare=(EC,EP). Rohfehler und gesamte Vorgeschichte stehen zusaetzlich im JSON. KALT ist keine Nullbewertung.
| Ziel | Hypothese / Key | Nachfolgerordinal | Vorher | Rohfehler | Nachher | Fruehere Feedbackziele |
|---:|---|---:|---|---|---|---|
| 7 | X [1, 1, 0] | 3 | KALT | [0.0, 0.5] | [0.0, 0.5] |  |
| 11 | X [0, 1, 0] | 3 | [0.0, 0.5] | [0.0, 0.5] | [0.0, 0.5] | 7 |
| 15 | X [0, 1, 0] | 3 | [0.0, 0.5] | [0.0, 0.5] | [0.0, 0.5] | 7,11 |
| 19 | X [0, 1, 0] | 3 | [0.0, 0.5] | [0.25, 0.25] | [0.125, 0.375] | 7,11,15 |
| 23 | X [0, 1, 0] | 3 | [0.125, 0.375] | [0.25, 0.25] | [0.1875, 0.3125] | 7,11,15,19 |
| 23 | Y [1, 2, 0] | 19 | KALT | [0.0, 0.25] | [0.0, 0.25] |  |
| 27 | X [0, 1, 0] | 3 | [0.1875, 0.3125] | [0.25, 0.25] | [0.21875, 0.28125] | 7,11,15,19,23 |
| 27 | Y [0, 2, 0] | 19 | [0.0, 0.25] | [0.0, 0.25] | [0.0, 0.25] | 23 |
| 31 | X [0, 1, 0] | 3 | [0.21875, 0.28125] | [0.25, 0.25] | [0.234375, 0.265625] | 7,11,15,19,23,27 |
| 31 | Y [0, 2, 0] | 19 | [0.0, 0.25] | [0.0, 0.25] | [0.0, 0.25] | 23,27 |
| 35 | X [0, 1, 0] | 3 | [0.234375, 0.265625] | [0.0, 0.5] | [0.1171875, 0.3828125] | 7,11,15,19,23,27,31 |
| 35 | Y [0, 2, 0] | 19 | [0.0, 0.25] | [0.25, 0.5] | [0.125, 0.375] | 23,27,31 |
| 39 | Y [0, 2, 0] | 19 | [0.125, 0.375] | [0.25, 0.5] | [0.1875, 0.4375] | 23,27,31,35 |
| 39 | X [0, 1, 0] | 3 | [0.1171875, 0.3828125] | [0.0, 0.5] | [0.05859375, 0.44140625] | 7,11,15,19,23,27,31,35 |
| 43 | Y [0, 2, 0] | 19 | [0.1875, 0.4375] | [0.25, 0.5] | [0.21875, 0.46875] | 23,27,31,35,39 |
| 43 | X [0, 1, 0] | 3 | [0.05859375, 0.44140625] | [0.0, 0.5] | [0.029296875, 0.470703125] | 7,11,15,19,23,27,31,35,39 |
| 47 | Y [0, 2, 0] | 19 | [0.21875, 0.46875] | [0.25, 0.5] | [0.234375, 0.484375] | 23,27,31,35,39,43 |
| 47 | X [0, 1, 0] | 3 | [0.029296875, 0.470703125] | [0.0, 0.5] | [0.0146484375, 0.4853515625] | 7,11,15,19,23,27,31,35,39,43 |

## Gewinne und Schaeden gegen jede Baseline

- Gegen M: Gewinne [{"target": 27, "magnitude": 0.25, "U_minus": -0.25}, {"target": 31, "magnitude": 0.25, "U_minus": -0.25}, {"target": 35, "magnitude": 0.25, "U_minus": -0.25}, {"target": 39, "magnitude": 0.5, "U_minus": -0.5}, {"target": 43, "magnitude": 0.5, "U_minus": -0.5}, {"target": 47, "magnitude": 0.5, "U_minus": -0.5}]; Schaeden [].
- Gegen E: Gewinne [{"target": 11, "magnitude": 0.5, "U_minus": -0.5}, {"target": 27, "magnitude": 0.25, "U_minus": -0.25}, {"target": 31, "magnitude": 0.25, "U_minus": -0.25}, {"target": 35, "magnitude": 0.25, "U_minus": -0.25}, {"target": 39, "magnitude": 0.5, "U_minus": -0.5}, {"target": 43, "magnitude": 0.5, "U_minus": -0.5}, {"target": 47, "magnitude": 0.5, "U_minus": -0.5}]; Schaeden [].
- Gegen K: Gewinne [{"target": 27, "magnitude": 0.25, "U_minus": -0.25}, {"target": 31, "magnitude": 0.25, "U_minus": -0.25}, {"target": 35, "magnitude": 0.25, "U_minus": -0.25}, {"target": 39, "magnitude": 0.5, "U_minus": -0.5}, {"target": 43, "magnitude": 0.5, "U_minus": -0.5}, {"target": 47, "magnitude": 0.5, "U_minus": -0.5}]; Schaeden [{"target": 7, "magnitude": 0.5, "U_minus": 0.5}].
- Gegen P: Gewinne [{"target": 11, "magnitude": 0.5, "U_minus": -0.5}, {"target": 15, "magnitude": 0.5, "U_minus": -0.5}, {"target": 27, "magnitude": 0.25, "U_minus": -0.25}, {"target": 31, "magnitude": 0.25, "U_minus": -0.25}, {"target": 35, "magnitude": 0.25, "U_minus": -0.25}, {"target": 39, "magnitude": 0.5, "U_minus": -0.5}, {"target": 43, "magnitude": 0.5, "U_minus": -0.5}, {"target": 47, "magnitude": 0.5, "U_minus": -0.5}]; Schaeden [].
Alle anderen Differenzen sind0; genaue Gleichstandsziele in all-gains-and-harms.json.
Der einzige Mehrfehler gegen die Baselines liegt an7 gegen K:0.5 kalte Anfangskosten. Die eigenen Fehler19/23/35 bleiben unabhaengig von Differenzen vollstaendig ausgewiesen.
Auswahlfaehigkeit,H-Nettonutzen und G-Gesamtnutzen sind getrennte,jeweils erfuellte Kriterien. Kein Weglassen der Neben-/Anfangsziele; N bleibt bei allen Armen gleich.

## Ressourcen und gemeinsame Exportbilanz

| Arm | Python-Zusatzpeak Bytes | Frameangabe | Gemeinsam | Receipt / UTF8-Obergrenze Bytes |
|---|---:|---|---|---|
| U | 5146 | 12 kontrollierte Obergrenze | 14 Obergrenze | 720 / 1440 |
| M | 4180 | 12 beobachteter Peak | 13 beobachteter Peak | 453 / 906 |
| E | 2481 | 12 beobachteter Peak | 13 beobachteter Peak | 453 / 906 |
| K | 1282 | 12 beobachteter Peak | 13 beobachteter Peak | 453 / 906 |
| P | 1498 | 12 beobachteter Peak | 13 beobachteter Peak | 453 / 906 |

U verwendet416 gepackte Bytes inkl.Ticket/Staging,maximal2 Ausgabeplaetze.12 ist die kontrollierte Frameobergrenze,KEIN gemessener U-Framepeak; unbefuellte Tracingpeaks bleiben ohne Verbrauchsaussage.
Der alte Exporter traegt packed_bytes=416 auch fuer K/P als konstante Grenze ein; deren Fehlergedaechtnis ist deaktiviert. Daraus keine gemessene416-Byte-Allokation dieser Arme ableiten.
Wiederverwendete Policyqualifikation:9897/16384 Zusatzbyte,18/18 Originalframes,2/2 Ausgabeplaetze,20/20 gemeinsam,Receipt2012,UTF8-Obergrenze4024 Byte. Kein Gesamtprozess-RAM-Beleg.
Policyqualifikation549025 Byte + separate Vorbereitung49280 Byte + Originalvergleich306045 Byte = 904350 Byte vor dieser Nachauswertung. Endsumme inklusive Bericht in closure.json; gemeinsame Grenze4194304 Byte,Reserve262144 Byte.
Alle Originalexporte bleiben versiegelt. Berichtsauswertung ausschliesslich gespeicherter Daten,keine weiteren Replays.

## Genau eine naechste Forschungsentscheidung

Empfehlung: einen unabhaengigen Evaluationsvertrag fuer die eingefrorene Policy konzipieren. Die Auswertungsquelle soll getrennt bereitgestellt und vor Ausfuehrung gebunden werden; Baselines,Ressourcen und Fehlerkriterien stehen vorher fest. Die jetzige offengelegte,algebraisch vorhergesagte Folge belegt Entwicklungsauswahl,keine unabhaengige Generalisierung.
Heute keine neue Quelle,keine Policyanpassung und keine weitere Ausfuehrungsfreigabe.
