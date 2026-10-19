# URA1-REV1: vollständiger Forschungsabschluss

Workflow-Auftrag 79d073d9-c0de-4344-9f3d-63649c76b071. Genau ein autorisierter Aufruf; Wiederzustellung als derselbe Auftrag behandelt.
Vorstart-SHA: 3d05e2fc657a704be3fb5901a302c0c81e519aefaa377909529686a6cf7e650d.

## Ergebnis

**COMPLETE / TERMINAL_COMPLETE.** 32 Geschichten, 64 frische U/R-Arme, alle Fallquittungen und unabhängigen Referenz-/Archiv-/Statistikprüfungen bestätigt. Keine Fehlerursache oder Folgefehler. Worker beendet und Cleanup bestätigt. Kein Retry, Resume, Ersatzfall oder Tuning.

Der frühe U/R-Unterschied bleibt nach dem vorab festgelegten Intervallkriterium unentschieden. Das ist kein Gleichwertigkeitsnachweis.

U-MAE 0.191406250000, R-MAE 0.205078125000; U−R -0.013671875000, nominales 95%-Intervall [-0.029541015625; 0.001220703125]. Urteil: INCONCLUSIVE.

## Design und einziger Primärnachweis

32 neue, unabhängig geprüfte Quellen unter MCM-URA1-REV1/source/v1, vollständig vor dem ersten Arm versiegelt. Je 1024 Frames; einmalige Kontingenzumkehr nach Block 128, kein Reset oder zusätzliches Wechselsignal. Unveränderte U/R-Auswahlregeln und identischer zugänglicher Spurenbestand. Frühere V4-Daten sind keine Kontrollgruppe und wurden nicht gepoolt.

Primär: je Geschichte mittlere U−R-MAE über Q129–160, anschließend gleichgewichtetes Mittel über 32 Geschichten. 32 Ziele je Geschichte, 1024 insgesamt. Kalte, leere, Ein-Kandidaten- und schädliche Ziele bleiben eingeschlossen. Statistische Einheit ist die Geschichte. 10000 vorab gebundene Bootstrapziehungen, 16+16 nach Orientierung, nominales zweiseitiges 95%-Perzentilintervall mit linearer Interpolation. Keine neue Matrix oder Seedwahl.

| Größe | Exakt | Dezimal |
|---|---:|---:|
| U-MAE | 49/256 | 0.191406250000 |
| R-MAE | 105/512 | 0.205078125000 |
| U−R | -7/512 | -0.013671875000 |
| 95%-Untergrenze | -121/4096 | -0.029541015625 |
| 95%-Obergrenze | 5/4096 | 0.001220703125 |

## Ergänzende Fenster — ausschließlich deskriptiv

Nur Q129–160 ist primär. Vorphase Q97–128, späte Nachphase Q161–256, gesamte Nachphase Q129–256 sowie Q/G_all/S/Q_X/Q_Y sind deskriptiv. Orientierung 0: ungerade Geschichten; Orientierung 1: gerade. Keine zusätzlichen Signifikanzurteile.

| Maske | Orientierung | Ziele | U-MAE | R-MAE | U−R |
|---|---|---:|---:|---:|---:|
| Q_early_post | alle | 1024 | 0.191406250000 | 0.205078125000 | -0.013671875000 |
| Q_early_post | 0 | 512 | 0.180664062500 | 0.199218750000 | -0.018554687500 |
| Q_early_post | 1 | 512 | 0.202148437500 | 0.210937500000 | -0.008789062500 |
| Q_pre | alle | 1024 | 0.184570312500 | 0.234619140625 | -0.050048828125 |
| Q_pre | 0 | 512 | 0.186035156250 | 0.236816406250 | -0.050781250000 |
| Q_pre | 1 | 512 | 0.183105468750 | 0.232421875000 | -0.049316406250 |
| Q_late_post | alle | 3072 | 0.186523437500 | 0.227213541667 | -0.040690104167 |
| Q_late_post | 0 | 1536 | 0.190104166667 | 0.230468750000 | -0.040364583333 |
| Q_late_post | 1 | 1536 | 0.182942708333 | 0.223958333333 | -0.041015625000 |
| Q_all_post | alle | 4096 | 0.187744140625 | 0.221679687500 | -0.033935546875 |
| Q_all_post | 0 | 2048 | 0.187744140625 | 0.222656250000 | -0.034912109375 |
| Q_all_post | 1 | 2048 | 0.187744140625 | 0.220703125000 | -0.032958984375 |
| Q | alle | 8192 | 0.188964843750 | 0.226226806641 | -0.037261962891 |
| Q | 0 | 4096 | 0.189758300781 | 0.226135253906 | -0.036376953125 |
| Q | 1 | 4096 | 0.188171386719 | 0.226318359375 | -0.038146972656 |
| G_all | alle | 16352 | 0.312805772994 | 0.331473214286 | -0.018667441292 |
| G_all | 0 | 8176 | 0.313203277886 | 0.331427348337 | -0.018224070450 |
| G_all | 1 | 8176 | 0.312408268102 | 0.331519080235 | -0.019110812133 |
| S | alle | 8160 | 0.437132352941 | 0.437132352941 | 0.000000000000 |
| S | 0 | 4080 | 0.437132352941 | 0.437132352941 | 0.000000000000 |
| S | 1 | 4080 | 0.437132352941 | 0.437132352941 | 0.000000000000 |
| Q_X | alle | 4096 | 0.189636230469 | 0.221313476562 | -0.031677246094 |
| Q_X | 0 | 2048 | 0.190795898438 | 0.222412109375 | -0.031616210938 |
| Q_X | 1 | 2048 | 0.188476562500 | 0.220214843750 | -0.031738281250 |
| Q_Y | alle | 4096 | 0.188293457031 | 0.231140136719 | -0.042846679688 |
| Q_Y | 0 | 2048 | 0.188720703125 | 0.229858398438 | -0.041137695312 |
| Q_Y | 1 | 2048 | 0.187866210938 | 0.232421875000 | -0.044555664062 |

## Gewinn und Schaden im Primärfenster

Besser: 222, schlechter: 196, gleich: 606 von 1024 Zielen. Gewinnsumme 303/4, Schadenssumme 247/4, Netto (Gewinn−Schaden) 14. Maximaler zusätzlicher Fehler je Ziel 1/2, an 51 Positionen. Vollständige Positionen stehen in statistics.json.
Schlechtester mittlerer Geschichtenkontrast: 7/128 (0.054687500000), Geschichten [24, 26].

Die folgenden überlappenden Partitionen beziehen sich ausschließlich auf das Primärfenster. eligible=2 bedeutet mindestens zwei berechtigte Hypothesen. Warm-/Auswahlklassen sind U-seitig bestimmt. Netto>0 begünstigt U und hat das umgekehrte Vorzeichen zur U−R-Summe. Keine Kausalattribution aus Untergruppen.

| Partition | Klasse | Ziele | Besser | Schlechter | Gleich | Gewinn | Schaden | Netto |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| eligible | 0 | 40 | 0 | 0 | 40 | 0 | 0 | 0 |
| eligible | 1 | 646 | 66 | 66 | 514 | 33/2 | 33/2 | 0 |
| eligible | 2 | 338 | 156 | 130 | 52 | 237/4 | 181/4 | 14 |
| warm | none | 40 | 0 | 0 | 40 | 0 | 0 | 0 |
| warm | cold | 66 | 26 | 40 | 0 | 13/2 | 10 | -7/2 |
| warm | mixed | 135 | 66 | 69 | 0 | 33/2 | 69/4 | -3/4 |
| warm | warm | 783 | 130 | 87 | 566 | 211/4 | 69/2 | 73/4 |
| same_output | False | 418 | 222 | 196 | 0 | 303/4 | 247/4 | 14 |
| same_output | True | 606 | 0 | 0 | 606 | 0 | 0 | 0 |
| choice | both_persistence | 40 | 0 | 0 | 40 | 0 | 0 | 0 |
| choice | mixed | 286 | 141 | 145 | 0 | 141/4 | 145/4 | -1 |
| choice | same_context | 566 | 0 | 0 | 566 | 0 | 0 | 0 |
| choice | different_context | 132 | 81 | 51 | 0 | 81/2 | 51/2 | 15 |

## Primärkontrast je Geschichte

| Geschichte | U−R exakt | Dezimal |
|---|---:|---:|
| 1 | 5/128 | 0.039062500000 |
| 2 | 5/128 | 0.039062500000 |
| 3 | 0 | 0.000000000000 |
| 4 | 1/128 | 0.007812500000 |
| 5 | -1/128 | -0.007812500000 |
| 6 | -5/128 | -0.039062500000 |
| 7 | -3/128 | -0.023437500000 |
| 8 | 3/64 | 0.046875000000 |
| 9 | 1/128 | 0.007812500000 |
| 10 | 1/128 | 0.007812500000 |
| 11 | -1/128 | -0.007812500000 |
| 12 | -7/128 | -0.054687500000 |
| 13 | -1/32 | -0.031250000000 |
| 14 | -3/128 | -0.023437500000 |
| 15 | 3/128 | 0.023437500000 |
| 16 | -3/128 | -0.023437500000 |
| 17 | 5/128 | 0.039062500000 |
| 18 | -3/128 | -0.023437500000 |
| 19 | -5/128 | -0.039062500000 |
| 20 | 0 | 0.000000000000 |
| 21 | -7/64 | -0.109375000000 |
| 22 | -9/128 | -0.070312500000 |
| 23 | -3/32 | -0.093750000000 |
| 24 | 7/128 | 0.054687500000 |
| 25 | -1/128 | -0.007812500000 |
| 26 | 7/128 | 0.054687500000 |
| 27 | -1/128 | -0.007812500000 |
| 28 | -1/8 | -0.125000000000 |
| 29 | -1/16 | -0.062500000000 |
| 30 | -3/128 | -0.023437500000 |
| 31 | -1/64 | -0.015625000000 |
| 32 | 1/32 | 0.031250000000 |

## Integrität, Ressourcen und Abschluss

939 Vorstart-Dateibindungen unverändert; 32 Quellenhashes und 102 Abschlussdateihashes geprüft. Alle 32 Erfassungsbelege zeigen gleiche U/R-Hashes für äußere und interne Zustandsereignisse. Je Geschichte und Arm 3072 äußere Ereignisse, 512 Prognosen und 511 beobachtete Ziele. Das letzte Ziel 1025 ist zensiert. Die unabhängige Statistikreferenz wurde im autorisierten Lauf vollständig bestätigt. Für diesen Bericht wurden keine Policies oder statistischen Versuche wiederholt.

Gesamtdauer 7148.315 s (119.14 min), innerhalb 57600 s. Jobpeak 206450688 Byte, Prozesspeak 121413632 Byte. Gemeinsamer Job 512 MiB, zwei Prozesse. Workerfrist 54000 s und Abschlussreserve 3600 s innerhalb der Gesamtfrist bleiben durch den gebundenen Einstieg geschützt; ein separater Worker-Walltimewert ist nicht aufgezeichnet.
Workerbilanzierung: 131644 Prüfungen, 1926.089 s; Supervisor: 279984 Prüfungen, 4183.575 s. Zeiten überlappen und werden nicht als Laufdauer addiert.

Worker beendet, interner Cleanup und Datei-Cleanup bestätigt. Keine temporären Teilarchive. Die finale Größen- und Dateibilanz einschließlich dieses Berichts steht in delivery-closure.json; preparation_bytes enthält auch die einmalig erstellte Berechtigung. Alle ursprünglichen Laufartefakte bleiben unverändert.

## Aussagegrenzen und nächster Schritt

Der Befund gilt für diese synthetische Quellenfamilie und das feste frühe Fenster. Er beweist weder eine allgemeine Überlegenheit noch einen kausalen Wechselkosteneffekt ohne stationäre Kontrollbedingung. Ein späteres deskriptives Fenster beweist keine vorübergehende Wirkung. R wählt das neueste verfügbare Original, nicht zwingend die zuletzt beobachtete Fortsetzung. Der frühere binäre U/L-Äquivalenzbefund und die Grenze einer pauschalen EMA-Trägheitserklärung bleiben gültig. Keine Aussage über feldinterne Memory, allgemeine Intelligenz oder reale Audio-/Video-Übertragung.

Empfehlung an den Projektleiter: Intervallbreite, Schadensverteilung und Bestandsdiagnosen fachlich bewerten. Eine Wiederholung oder Vergrößerung benötigt eine neue Begründung und gesonderte Freigabe; kein automatischer Ersatzlauf.

Belege: [START](START.json), [Quellenmanifest](sources-manifest.json), [Statistik](statistics.json), [Worker](worker.json), [Resultat](result.json), [Terminal](terminal.json), [ursprünglicher Abschluss](closure.json), [Nachprüfung](verification.json), [finale Lieferung](delivery-closure.json).
