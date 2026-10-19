# ULZ1: einmaliger Forschungsdurchlauf, 2026-10-04

**COMPLETE – alle 64 Forschungsquellen und 128 Arme vollständig ausgeführt.**
Einmalfreigabe verbraucht. Kein Neustart, keine Fall-/Seed-Auswahl, keine Regeländerung.
U bleibt unverändert; L wurde nicht als neuer Standard übernommen. A1/K1 aus.

## Zwei vorab festgelegte Primärfragen

D=MAE(U)−MAE(L), gepaarte Mittelwerte aus je32 Wiederholungen. Negative Werte
bedeuten geringeren U-Fehler. Vorab bestimmte10.000 Clusterbootstrap-Ziehungen;
zweiseitige97,5%-Intervalle mit Bonferroni-Aufteilung für genau zwei Fragen.

| Frage | U-MAE | L-MAE | U−L | 97,5%-Intervall | erwartete Richtung | Urteil |
| --- | ---: | ---: | ---: | --- | --- | --- |
| Stabil: S, Y33–128 | 0.191121419 | 0.196004232 | -0.004882812 | [-0.006591797; -0.003214010] | U besser | BELEGT |
| Früher Wechsel: W, Y129–160 | 0.206787109 | 0.209716797 | -0.002929688 | [-0.006713867; 0.000976562] | L besser | NICHT_NACHGEWIESEN |

**Erwartete Abwägung: NICHT_NACHGEWIESEN.** Sie gilt nur bei Bestätigung beider Richtungen.
Primärzielzahlen je Arm:3.072 im stabilen und1.024 im frühen Wechselkontrast.
Ein Null einschließendes Intervall ist kein Gleichwertigkeitsnachweis.
Sekundäre Vorteile ersetzen keinen fehlenden Primärnachweis.

## Vollständige Masken und sekundäre Unsicherheit

Die beiden Primärzeilen sind oben verbindlich beurteilt. Alle anderen Zeilen
und Orientierungsaufteilungen sind explorativ. Vollständige32 Wiederholungswerte
und alle Orientierungsintervalle: [Kontraste](contrasts.csv).

| Bedingung | Maske | U | L | U−L | Intervall | Niveau |
| --- | --- | ---: | ---: | ---: | --- | --- |
| S | G | 0.098770171 | 0.101035645 | -0.002265474 | [-0.002935332; -0.001625723] | 0.95 |
| S | G_Y | 0.195358276 | 0.199951172 | -0.004592896 | [-0.005950928; -0.003295898] | 0.95 |
| S | G_init | 0.178571429 | 0.178571429 | 0.000000000 | [0.000000000; 0.000000000] | 0.95 |
| S | G_post | 0.097679138 | 0.099975586 | -0.002296448 | [-0.002975464; -0.001647949] | 0.95 |
| S | G_skeleton | 0.000000000 | 0.000000000 | 0.000000000 | [0.000000000; 0.000000000] | 0.95 |
| S | Y_129_160 | 0.203002930 | 0.206054688 | -0.003051758 | [-0.005981445; -0.000122070] | 0.95 |
| S | Y_161_256 | 0.194824219 | 0.199625651 | -0.004801432 | [-0.006958008; -0.002644857] | 0.95 |
| S | Y_1_32 | 0.202026367 | 0.206665039 | -0.004638672 | [-0.008178711; -0.000854492] | 0.95 |
| S | Y_33_128 | 0.191121419 | 0.196004232 | -0.004882812 | [-0.006591797; -0.003214010] | 0.975 |
| W | G | 0.098679853 | 0.100712006 | -0.002032153 | [-0.002461163; -0.001625723] | 0.95 |
| W | G_Y | 0.195175171 | 0.199295044 | -0.004119873 | [-0.004989624; -0.003295898] | 0.95 |
| W | G_init | 0.178571429 | 0.178571429 | 0.000000000 | [0.000000000; 0.000000000] | 0.95 |
| W | G_post | 0.097587585 | 0.099647522 | -0.002059937 | [-0.002494812; -0.001647949] | 0.95 |
| W | G_skeleton | 0.000000000 | 0.000000000 | 0.000000000 | [0.000000000; 0.000000000] | 0.95 |
| W | Y_129_160 | 0.206787109 | 0.209716797 | -0.002929688 | [-0.006713867; 0.000976562] | 0.975 |
| W | Y_161_256 | 0.193074544 | 0.196655273 | -0.003580729 | [-0.005494181; -0.001708984] | 0.95 |
| W | Y_1_32 | 0.202026367 | 0.206665039 | -0.004638672 | [-0.008178711; -0.000854492] | 0.95 |
| W | Y_33_128 | 0.191121419 | 0.196004232 | -0.004882812 | [-0.006388346; -0.003417969] | 0.95 |

Alle519 Ziele je Armgeschichte einschließlich Präfix und Gerüst bleiben enthalten.
[Vollständiger Zielverlauf](targets.csv) enthält U/L-Fehler, Einzeldifferenz,
kumulierte Differenz, Ausgabeoriginal, Wahlgrund und Z-Zustand. Keine Auswahl nur
warmer/erfolgreicher Ziele. [Fallmittel](case-mask-means.csv) enthalten sämtliche Masken.

## Gewinne und Schäden

| Bedingung | Maske | U besser | U schlechter | gleich | Gewinnsumme | Schadenssumme | maximaler Schaden | schlechtester Fallmittelwert U−L |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| S | G | 362 | 202 | 16044 | 78.875000000 | 41.250000000 | 0.250000000 | 0.000963391 |
| S | G_Y | 362 | 202 | 7628 | 78.875000000 | 41.250000000 | 0.250000000 | 0.001953125 |
| S | G_init | 0 | 0 | 224 | 0.000000000 | 0.000000000 | 0.000000000 | 0.000000000 |
| S | G_post | 362 | 202 | 15820 | 78.875000000 | 41.250000000 | 0.250000000 | 0.000976562 |
| S | G_skeleton | 0 | 0 | 8192 | 0.000000000 | 0.000000000 | 0.000000000 | 0.000000000 |
| S | Y_129_160 | 40 | 29 | 955 | 8.875000000 | 5.750000000 | 0.250000000 | 0.015625000 |
| S | Y_161_256 | 134 | 72 | 2866 | 29.625000000 | 14.875000000 | 0.250000000 | 0.005208333 |
| S | Y_1_32 | 46 | 25 | 953 | 10.000000000 | 5.250000000 | 0.250000000 | 0.027343750 |
| S | Y_33_128 | 142 | 76 | 2854 | 30.375000000 | 15.375000000 | 0.250000000 | 0.003906250 |
| W | G | 346 | 196 | 16066 | 74.375000000 | 40.625000000 | 0.250000000 | 0.000000000 |
| W | G_Y | 346 | 196 | 7650 | 74.375000000 | 40.625000000 | 0.250000000 | 0.000000000 |
| W | G_init | 0 | 0 | 224 | 0.000000000 | 0.000000000 | 0.000000000 | 0.000000000 |
| W | G_post | 346 | 196 | 15842 | 74.375000000 | 40.625000000 | 0.250000000 | 0.000000000 |
| W | G_skeleton | 0 | 0 | 8192 | 0.000000000 | 0.000000000 | 0.000000000 | 0.000000000 |
| W | Y_129_160 | 43 | 27 | 954 | 9.000000000 | 6.000000000 | 0.250000000 | 0.019531250 |
| W | Y_161_256 | 115 | 68 | 2889 | 25.000000000 | 14.000000000 | 0.250000000 | 0.006510417 |
| W | Y_1_32 | 46 | 25 | 953 | 10.000000000 | 5.250000000 | 0.250000000 | 0.027343750 |
| W | Y_33_128 | 142 | 76 | 2854 | 30.375000000 | 15.375000000 | 0.250000000 | 0.003906250 |

Überlappende Masken nicht addieren. Keine Schadensfreiheitsbehauptung und keine
nachträglich übertragene A1-Schadensschwelle. [Vollständige Schadensbilanz](harms.csv).

## Regulärer Z-Lebenszyklus

| Bedingung | Z-Kandidat erzeugt | Z-Kandidat ersetzt | Z promoviert | Z aus Retained verdrängt | alle Promotionen | alle Verdrängungen |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| S | 395 | 0 | 382 | 367 | 1015 | 951 |
| W | 384 | 0 | 374 | 356 | 981 | 917 |

| Bedingung | Arm | Y-Ziele | Z berechtigt | Z kalt | Z warm | Z als Kandidat | Z als Retained | Z ausgewählt | Persistenz ausgewählt | gültiges Z-Feedback |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| S | U | 8192 | 6096 | 392 | 5704 | 1925 | 4171 | 1506 | 840 | 6096 |
| S | L | 8192 | 6096 | 392 | 5704 | 1925 | 4171 | 1491 | 690 | 6096 |
| W | U | 8192 | 6190 | 383 | 5807 | 1879 | 4311 | 1496 | 830 | 6190 |
| W | L | 8192 | 6190 | 383 | 5807 | 1879 | 4311 | 1490 | 670 | 6190 |

Bestand, Berechtigung, Kalt/Warm-Belegung und Feedbackgelegenheiten sind
ereignisweise innerhalb jedes U/L-Paars gleich. Die jeweiligen Fehlerwerte,
Ausgaben und EP-Historien dürfen verschieden sein. Z wurde nicht ausgeblendet
oder geschützt. [Alle Fall-Lebenszyklen](cycles.json) dokumentieren Originale,
Promotionen, Verluste, Kandidatenersetzungen und Bestätigungen. Die vollständigen
Feedback-/Zellketten beider Arme liegen im hashgeprüften Laufarchiv. Im L-Export
verweist shared_stock_with_U auf den nachweislich gleichen U-Bestand; L-Zellwerte
und Ausgaben sind separat gespeichert. Kein Beobachterverlauf wurde L zugeführt.

## Integrität und Ressourcen

133 im Abschluss aufgeführte Dateien auf Länge und SHA256 geprüft.
64 Fälle,128 Arme,66.560 Quellenframes,133.120 Produktionsaufnahmen und ebenso
viele separat gezählte unabhängige Referenzfortschreibungen.33.216 gepaarte Ziele,
davon16.384 Y-Ziele; vollständige Bereinigung, Ziel1041 je Armgeschichte zensiert.
Alle Quellen vor erster Policy versiegelt. Keine technische Abweichung und kein
Budgetabbruch; Worker beendet.

| Ressource | U | L |
| --- | ---: | ---: |
| zusätzlicher Python-Peak (Byte) | 6260 | 5976 |
| Bank (Byte) | 416 | 416 |
| Originale an Operationsgrenzen | 15 | 15 |
| konservative Originalobergrenze | 16 | 16 |
| konservative kombinierte Obergrenze | 18 | 18 |
| gültige Zellen, Maximum | 3 | 3 |
| Ausgabeslots | 2 | 2 |
| gesamte erreichbare Systemobjekte an Operationsgrenzen (Byte) | 19994 | 19872 |
| Basisarm an Operationsgrenzen (Byte) | 16027 | 16011 |
| neue Ausgabepayloads | 0 | 0 |
| Receipt (Byte) | 1064 | 937 |
| UTF-8-Obergrenze (Byte) | 2128 | 1874 |

Gleiche tatsächliche Original-/Zellbelegung wurde pro Ereignis kontrolliert.
Die übrige Python-Nutzung wird nicht als identisch behauptet oder künstlich
angeglichen. Ganze Systemobjekte sind Grenzstellenzählungen, keine Messung des
ganzen Prozesspeaks. Zusatzheap enthält Operationstransienten. Überlappende
Kategorien nicht addieren; Frame-Tracing-Zähler0 sind keine Nullbelegung.
Eingang und externe Beobachterdaten sind im Laufexport separat ausgewiesen.

Worker: 667.362s; Supervisor vor terminalem Schreiben: 673.455s.
Vorbereitung: 4635399Byte; Laufexport einschließlich Abschluss: 8419051Byte.
Maximaler Fall: 2254124Byte expandiert, 128249Byte gzip.
Alle gebundenen Grenzen eingehalten. Die zusätzliche Archivauswertung verändert
keine versiegelte Laufdatei und enthält keinen weiteren Replay.

Vorstart-SHA256: `58f6009f7b5609e3993983bafe554f9029bdca31f82addf9c79fa5eec2120537`.
Autorisierungs-SHA256: `716d2b15bc2565bde2d5439dc720d6823b93a344d2acbe33f92da152d38359c1`.
Laufabschluss-SHA256: `df4bb51d44eb4e188e4c7a41e30c4d80d56daac1758d5ec41a75df3ae9da036e`.
[Prüfbilanz](verification.json), [versiegelter Laufabschluss](../ulz1-comparison-20261004-01/closure.json).

Die operative Autorisierung bleibt als historischer Startbeleg unverändert.
Vorhandener Zielordner, resume_permitted=false und Abschluss dokumentieren
den Verbrauch. Keine Wiederholung aus erneuter Zustellung dieser Freigabe.

## Aussagegrenze

Untersucht wurde zeitliche Fehlerglättung in dieser synthetischen A/B/Z-Familie
unter gemeinsamem regulären Speicherlebenszyklus und gleichen Budgets.
Kein allgemeiner MCM-Mehrwert, Transfer oder feldinterne Memory nachgewiesen.
Historische LZ1-/T1-/F-Urteile bleiben bestehen. Keine Übernahme von L und
keine weitere Regeländerung durch diesen Lauf.

## Fachliche Einordnung und nächster sinnvoller Schritt

Im stabilen Primärfenster beträgt die Fehlerreduktion durch U gegenüber L
0,0048828125 MAE. Dieser begrenzte Nutzen zeitlicher Glättung ist unter dem
geprüften gemeinsamen Speicherlebenszyklus belegt. Er geht mit einzelnen
Schäden einher:142 bessere und76 schlechtere Ziele in diesem Fenster.

Im frühen Wechselfenster liegt der Punktwert ebenfalls zugunsten von U,
aber das97,5%-Intervall schließt null ein. Weder der erwartete L-Vorteil noch
ein gegenläufiger U-Vorteil ist dort nachgewiesen. Insbesondere keine Aussage,
U passe sich nach Wechsel sicher schneller an. Die erwartete gemeinsame
Stabilitäts-/Wechselabwägung bleibt NICHT_NACHGEWIESEN.

Sekundär ist U auf dem vollständigen G_Y-Verlauf in S und W im Mittel besser.
Das ersetzt die offene frühe Wechselkomponente nicht. Gleiches Gerüst und
Präfix tragen keinen U/L-Vorteil bei. Die gezählte Z-Konkurrenz, Promotion
und Verdrängung sind reguläre Teile dieses begrenzten Vergleichs.

Empfehlung an den Projektleiter: den nachgewiesenen Stabilitätsnutzen und die
nicht nachgewiesene Wechselabwägung getrennt abnehmen; U unverändert belassen.
Vor einem weiteren Entwicklungsversuch wäre als kleinster sinnvoller Schritt
anhand des vorhandenen Archivs einzuordnen, wie Gewinne und Einzelschäden mit
Z-Auswahl, Persistenzwahl und Verdrängungsereignissen zusammenhängen. Das wäre
eine Diagnose vorhandener Belege, keine neue Parameter- oder Quellenwahl.
Hier wurde keine solche Folgeuntersuchung gestartet und keine Umstellung auf L
vorgenommen.
