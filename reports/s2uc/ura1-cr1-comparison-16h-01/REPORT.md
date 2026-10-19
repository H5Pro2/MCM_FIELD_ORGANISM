# URA1-CR1: vollständiger Forschungsabschluss

Workflow-Auftrag 09fde789-5ec0-4a2f-9d30-516d4906d587. Genau ein autorisierter Aufruf; Wiederzustellung als derselbe Auftrag behandelt.
Vorstart-SHA: 336f44aa79d8091991cfdc292e550c01e952e4faf5247e2c1b8613fb858ac1f3.

## Ergebnis

**COMPLETE / TERMINAL_COMPLETE.** 32 Geschichten, 64 frische C/U-Arme, alle Fallquittungen und unabhängigen Referenz-/Archiv-/Statistikprüfungen bestätigt. Keine Fehlerursache oder Folgefehler. Worker beendet und Cleanup bestätigt. Kein Retry, Resume, Ersatzfall oder Tuning.

C erzielt im vorab festgelegten frühen Nachwechselfenster einen niedrigeren mittleren Fehler als U. Das vollständig negative Intervall unterstützt die feste kalte Auswahlregel in dieser Quellenfamilie.

C-MAE 0.205322265625, U-MAE 0.210449218750; C−U -0.005126953125, nominales 95%-Intervall [-0.008300781250; -0.001708984375]. Urteil: C_EARLY_POST_BETTER.

## Design und einziger Primärnachweis

32 neue, unabhängig geprüfte Quellen unter MCM-URA1-CR1/source/v1, vollständig vor dem ersten Arm versiegelt. Je 1024 Frames; einmalige Kontingenzumkehr nach Block 128, kein Reset oder zusätzliches Wechselsignal. C weicht ausschließlich bei nicht leerem, vollständig kaltem H durch Originalrecency von U ab. Gemeinsamer zugänglicher Bestand, Rückmeldungen und warme Auswahl bleiben identisch. Historische Daten wurden nicht gepoolt. Die Variantenwahl ist ausdrücklich durch die frühere REV1-Diagnose motiviert; jene Daten dienen der Hypothesenbildung, nicht als unabhängiger C-Beleg.

Primär: je Geschichte mittlere C−U-MAE über Q129–160, anschließend gleichgewichtetes Mittel über 32 Geschichten. 32 Ziele je Geschichte, 1024 insgesamt. Kalte, leere, Ein-Kandidaten- und schädliche Ziele bleiben eingeschlossen. Statistische Einheit ist die Geschichte. 10000 vorab gebundene Bootstrapziehungen, 16+16 nach Orientierung, nominales zweiseitiges 95%-Perzentilintervall mit linearer Interpolation. Keine neue Matrix oder Seedwahl.

| Größe | Exakt | Dezimal |
|---|---:|---:|
| C-MAE | 841/4096 | 0.205322265625 |
| U-MAE | 431/2048 | 0.210449218750 |
| C−U | -21/4096 | -0.005126953125 |
| 95%-Untergrenze | -17/2048 | -0.008300781250 |
| 95%-Obergrenze | -7/4096 | -0.001708984375 |

## Ergänzende Fenster — ausschließlich deskriptiv

Nur Q129–160 ist primär. Vorphase Q97–128, späte Nachphase Q161–256, gesamte Nachphase Q129–256 sowie Q/G_all/S/Q_X/Q_Y sind deskriptiv. Orientierung 0: ungerade Geschichten; Orientierung 1: gerade. Keine zusätzlichen Signifikanzurteile.

| Maske | Orientierung | Ziele | C-MAE | U-MAE | C−U |
|---|---|---:|---:|---:|---:|
| Q_early_post | alle | 1024 | 0.205322265625 | 0.210449218750 | -0.005126953125 |
| Q_early_post | 0 | 512 | 0.204589843750 | 0.208984375000 | -0.004394531250 |
| Q_early_post | 1 | 512 | 0.206054687500 | 0.211914062500 | -0.005859375000 |
| Q_pre | alle | 1024 | 0.182128906250 | 0.183349609375 | -0.001220703125 |
| Q_pre | 0 | 512 | 0.172363281250 | 0.173828125000 | -0.001464843750 |
| Q_pre | 1 | 512 | 0.191894531250 | 0.192871093750 | -0.000976562500 |
| Q_late_post | alle | 3072 | 0.184733072917 | 0.186523437500 | -0.001790364583 |
| Q_late_post | 0 | 1536 | 0.189453125000 | 0.191243489583 | -0.001790364583 |
| Q_late_post | 1 | 1536 | 0.180013020833 | 0.181803385417 | -0.001790364583 |
| Q_all_post | alle | 4096 | 0.189880371094 | 0.192504882812 | -0.002624511719 |
| Q_all_post | 0 | 2048 | 0.193237304688 | 0.195678710938 | -0.002441406250 |
| Q_all_post | 1 | 2048 | 0.186523437500 | 0.189331054688 | -0.002807617188 |
| Q | alle | 8192 | 0.185974121094 | 0.188385009766 | -0.002410888672 |
| Q | 0 | 4096 | 0.187561035156 | 0.189147949219 | -0.001586914062 |
| Q | 1 | 4096 | 0.184387207031 | 0.187622070312 | -0.003234863281 |
| G_all | alle | 16352 | 0.311399217221 | 0.312607020548 | -0.001207803327 |
| G_all | 0 | 8176 | 0.312285958904 | 0.313080968689 | -0.000795009785 |
| G_all | 1 | 8176 | 0.310512475538 | 0.312133072407 | -0.001620596869 |
| S | alle | 8160 | 0.437316176471 | 0.437316176471 | 0.000000000000 |
| S | 0 | 4080 | 0.437500000000 | 0.437500000000 | 0.000000000000 |
| S | 1 | 4080 | 0.437132352941 | 0.437132352941 | 0.000000000000 |
| Q_X | alle | 4096 | 0.187866210938 | 0.190917968750 | -0.003051757812 |
| Q_X | 0 | 2048 | 0.187866210938 | 0.190429687500 | -0.002563476562 |
| Q_X | 1 | 2048 | 0.187866210938 | 0.191406250000 | -0.003540039062 |
| Q_Y | alle | 4096 | 0.184082031250 | 0.185852050781 | -0.001770019531 |
| Q_Y | 0 | 2048 | 0.187255859375 | 0.187866210938 | -0.000610351562 |
| Q_Y | 1 | 2048 | 0.180908203125 | 0.183837890625 | -0.002929687500 |

## Gewinn und Schaden im Primärfenster

Besser: 48, schlechter: 27, gleich: 949 von 1024 Zielen. Gewinnsumme 12, Schadenssumme 27/4, Netto (Gewinn−Schaden) 21/4. Maximaler zusätzlicher Fehler je Ziel 1/4, an 27 Positionen. Vollständige Positionen stehen in statistics.json.
Schlechtester mittlerer Geschichtenkontrast: 1/64 (0.015625000000), Geschichten [16, 31].

Alle 75 unterschiedlichen Primärausgaben gehören zur vollständig kalten Klasse mit genau einer berechtigten Hypothese. 949 Ausgaben sind identisch. Damit ist in diesem Primärfenster die kalte Originalausgabe gegenüber Persistenz verglichen; ein spezifischer Vorteil der Recency-Rangfolge zwischen mehreren kalten Originalen ist nicht nachgewiesen. Diese Einordnung ist deskriptiv und ändert das vorab festgelegte Primärurteil nicht.

Die folgenden überlappenden Partitionen beziehen sich ausschließlich auf das Primärfenster. eligible=2 bedeutet mindestens zwei berechtigte Hypothesen. Warm-/Auswahlklassen sind U-seitig bestimmt. Netto>0 begünstigt C und hat das umgekehrte Vorzeichen zur C−U-Summe. Keine Kausalattribution aus Untergruppen.

| Partition | Klasse | Ziele | Besser | Schlechter | Gleich | Gewinn | Schaden | Netto |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| eligible | 0 | 50 | 0 | 0 | 50 | 0 | 0 | 0 |
| eligible | 1 | 619 | 48 | 27 | 544 | 12 | 27/4 | 21/4 |
| eligible | 2 | 355 | 0 | 0 | 355 | 0 | 0 | 0 |
| warm | none | 50 | 0 | 0 | 50 | 0 | 0 | 0 |
| warm | cold | 75 | 48 | 27 | 0 | 12 | 27/4 | 21/4 |
| warm | mixed | 156 | 0 | 0 | 156 | 0 | 0 | 0 |
| warm | warm | 743 | 0 | 0 | 743 | 0 | 0 | 0 |
| same_output | False | 75 | 48 | 27 | 0 | 12 | 27/4 | 21/4 |
| same_output | True | 949 | 0 | 0 | 949 | 0 | 0 | 0 |
| choice | both_persistence | 277 | 0 | 0 | 277 | 0 | 0 | 0 |
| choice | mixed | 75 | 48 | 27 | 0 | 12 | 27/4 | 21/4 |
| choice | same_context | 672 | 0 | 0 | 672 | 0 | 0 | 0 |
| choice | different_context | 0 | 0 | 0 | 0 | 0 | 0 | 0 |

Die leere Klasse different_context hat Anzahl 0 und mean_delta=null in statistics.json; kein definierter Teilgruppenmittelwert. Geschichten mit Primärkontrast 0 bleiben vollständig im Mittel und Bootstrap enthalten.


## Primärkontrast je Geschichte

| Geschichte | C−U exakt | Dezimal |
|---|---:|---:|
| 1 | 0 | 0.000000000000 |
| 2 | 0 | 0.000000000000 |
| 3 | -1/128 | -0.007812500000 |
| 4 | -1/64 | -0.015625000000 |
| 5 | 0 | 0.000000000000 |
| 6 | -1/64 | -0.015625000000 |
| 7 | -1/128 | -0.007812500000 |
| 8 | -1/128 | -0.007812500000 |
| 9 | -1/128 | -0.007812500000 |
| 10 | -3/128 | -0.023437500000 |
| 11 | -1/128 | -0.007812500000 |
| 12 | 1/128 | 0.007812500000 |
| 13 | 0 | 0.000000000000 |
| 14 | -1/128 | -0.007812500000 |
| 15 | -1/64 | -0.015625000000 |
| 16 | 1/64 | 0.015625000000 |
| 17 | 1/128 | 0.007812500000 |
| 18 | -1/128 | -0.007812500000 |
| 19 | -1/64 | -0.015625000000 |
| 20 | -1/64 | -0.015625000000 |
| 21 | 0 | 0.000000000000 |
| 22 | 0 | 0.000000000000 |
| 23 | 0 | 0.000000000000 |
| 24 | 0 | 0.000000000000 |
| 25 | -1/64 | -0.015625000000 |
| 26 | -1/64 | -0.015625000000 |
| 27 | -1/128 | -0.007812500000 |
| 28 | 1/128 | 0.007812500000 |
| 29 | -1/128 | -0.007812500000 |
| 30 | 0 | 0.000000000000 |
| 31 | 1/64 | 0.015625000000 |
| 32 | -1/64 | -0.015625000000 |

## Integrität, Ressourcen und Abschluss

987 Vorstart-Dateibindungen unverändert; 32 Quellenhashes und 102 Abschlussdateihashes geprüft. Alle 32 Erfassungsbelege zeigen gleiche C/U-Hashes für äußere und interne Zustandsereignisse. Je Geschichte und Arm 3072 äußere Ereignisse, 512 Prognosen und 511 beobachtete Ziele. Das letzte Ziel 1025 ist zensiert. Die unabhängige Statistikreferenz wurde im autorisierten Lauf vollständig bestätigt. Für diesen Bericht wurden keine Policies oder statistischen Versuche wiederholt.

Gesamtdauer 7919.528 s (131.99 min), innerhalb 57600 s. Jobpeak 188317696 Byte, Prozesspeak 100208640 Byte. Gemeinsamer Job 512 MiB, zwei Prozesse. Workerfrist 54000 s und Abschlussreserve 3600 s innerhalb der Gesamtfrist bleiben durch den gebundenen Einstieg geschützt; ein separater Worker-Walltimewert ist nicht aufgezeichnet.
Workerbilanzierung: 131644 Prüfungen, 1893.067 s; Supervisor: 316770 Prüfungen, 4599.040 s. Zeiten überlappen und werden nicht als Laufdauer addiert.

Worker beendet, interner Cleanup und Datei-Cleanup bestätigt. Keine temporären Teilarchive. Die finale Größen- und Dateibilanz einschließlich dieses Berichts steht in delivery-closure.json; preparation_bytes enthält auch die einmalig erstellte Berechtigung. Alle ursprünglichen Laufartefakte bleiben unverändert.

## Aussagegrenzen und nächster Schritt

Der Befund gilt ausschließlich für die feste diagnosemotivierte Kaltauswahl, diese synthetische Quellenfamilie und das vorab festgelegte Fenster. Ein möglicher Ausgabevorteil beweist keine verbesserte Erfahrungsbildung: Gemeinsame Fehlerzustände und Erfahrungsaufnahme bleiben gerade unverändert. Keine allgemeine Überlegenheit, neue Memory-Organisation oder Übertragung auf reale Audio-/Video-Wahrnehmung nachgewiesen. Neueste Originalfortsetzung bedeutet nicht zwingend zuletzt beobachtete Fortsetzung. Deskriptive Untergruppen und weitere Fenster erhalten kein zusätzliches Signifikanzurteil.

Empfehlung an den Projektleiter: C als begrenzt belegte Ausgabevariante dieser Testfamilie einordnen. Alle 75 abweichenden Primärziele hatten genau eine kalte Hypothese: Der Befund trägt kalte Originalausgabe gegenüber Persistenz, keinen Vergleich mehrerer kalter Originale. Diese Grenze zuerst abnehmen und danach eine eigene mechanistische Gegenprognose zur Erfahrungsbildung formulieren; kein automatischer weiterer C/U-Lauf oder Tuning.

Belege: [START](START.json), [Quellenmanifest](sources-manifest.json), [Statistik](statistics.json), [Worker](worker.json), [Resultat](result.json), [Terminal](terminal.json), [ursprünglicher Abschluss](closure.json), [Nachprüfung](verification.json), [finale Lieferung](delivery-closure.json).
