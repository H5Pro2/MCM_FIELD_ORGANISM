# URA1-V4: vollständiger Forschungsabschluss

Workflow-Auftrag 9bebcd0c-05ad-46d7-99e1-aa3e6182c55b. Vorstart-SHA deaae277655ecf078de791190e840d42b2f42fb113288fc903b54b49342ccee3.

## Ergebnis

COMPLETE / TERMINAL_COMPLETE. Alle 32 Geschichten und 64 frischen U/R-Arme abgeschlossen, unabhängig geprüft und quittiert. Keine Fehlerursache oder Folgefehler. Genau ein autorisierter Aufruf; Start verbraucht, kein Retry, Resume, Ersatzfall oder nachträgliches Tuning.

Die erfahrungsabhängige Auswahl U erzielt in dieser vorregistrierten synthetischen Testfamilie einen niedrigeren mittleren Q-Prognosefehler als die jüngste passende Originalerfahrung R. U-MAE 0.186279296875, R-MAE 0.222808837890625; U−R = −0.036529541015625. Nominales 95%-Intervall [−0.0430908203125; −0.030029296875], vollständig unter null. Das entspricht deskriptiv etwa 16.40 Prozent weniger Q-MAE relativ zu R. In allen 32 Geschichten ist der mittlere Q-Kontrast negativ. Dies bedeutet keine Verbesserung an jedem einzelnen Ziel.

## Design und Primärnachweis

Ausschließlich 32 neue Geschichten unter MCM-URA1/source/v4, 1024 Frames je Geschichte, 16 je Orientierung. Alle Quellen wurden vor dem ersten Policyarm unabhängig geprüft und gemeinsam versiegelt. Keine historischen V2-/V3-Quellen oder Teilergebnisse einbezogen. Unveränderte U/R-Verfahren, gleiche zugängliche Spuren und gebundene Referenz-/Bestands-/Hypothesen-/Ticket-/Zellprüfungen. Der Vergleich betrifft die Auswahl gegenüber Originalrecency; er isoliert nicht allein eine EMA-Formel.

Primärmaß: pro Geschichte mittlere U−R-MAE über sämtliche 256 Q-Ziele, anschließend Mittel über 32 Geschichten. Keine nachträgliche Entfernung kalter Zustände, fehlender Spuren oder ungünstiger Ziele. Die statistische Einheit ist die Geschichte, nicht jedes der 8192 Q-Ziele als unabhängige Stichprobe.

Weiterrechnung exakt rational aus gespeicherten binary64-Fehlern. 10000 vorab gebundene, nach Orientierung geschichtete Paarziehungen; je Ziehung 16 Geschichten aus jeder Orientierung. Nominales 95%-Perzentilintervall mit h=9999q und linearer Interpolation. Matrix unverändert: 320000 Byte, SHA 0b9fbf483e870adac01ded7d2d0d0a651a11474a4ac2e4fbae1c14e793d7d965. Die unabhängige Statistikreferenz hat den gesamten Ergebnisdatensatz im Lauf bestätigt.

| Primärgröße | Exakter Wert | Dezimalwert |
|---|---:|---:|
| U: Q-MAE | 763/4096 | 0.186279296875 |
| R: Q-MAE | 7301/32768 | 0.222808837890625 |
| U−R | −1197/32768 | −0.036529541015625 |
| 95%-Untergrenze | −353/8192 | −0.0430908203125 |
| 95%-Obergrenze | −123/4096 | −0.030029296875 |

Gebundenes Urteil: FEHLERAUSWAHL_GEGEN_ORIGINALRECENCY_NUETZLICH. Dieses Urteil gilt für diesen Vergleich und diese Quellenfamilie.

## Ergänzende Mittelwerte — ausschließlich deskriptiv

Q: 256 Hauptziele je Geschichte. G_all: alle 511 beobachtbaren Prognoseziele. S: die 255 übrigen Ziele. Q_X/Q_Y: je 128 Q-Ziele. Orientierung 0 entspricht ungeraden, Orientierung 1 geraden Geschichten. Zusätzliche Tabellen begründen keine zusätzlichen Signifikanztests oder nachträgliche Entscheidungsregel.

| Maske | Geschichten | Ziele | U-MAE | R-MAE | U−R |
|---|---|---:|---:|---:|---:|
| Q | alle 32 | 8192 | 0.186279297 | 0.222808838 | -0.036529541 |
| Q | ungerade (16) | 4096 | 0.186523438 | 0.227661133 | -0.041137695 |
| Q | gerade (16) | 4096 | 0.186035156 | 0.217956543 | -0.031921387 |
| G_all | alle 32 | 16352 | 0.311460372 | 0.329760886 | -0.018300514 |
| G_all | ungerade (16) | 8176 | 0.311674413 | 0.332283513 | -0.020609100 |
| G_all | gerade (16) | 8176 | 0.311246331 | 0.327238258 | -0.015991928 |
| S | alle 32 | 8160 | 0.437132353 | 0.437132353 | 0.000000000 |
| S | ungerade (16) | 4080 | 0.437316176 | 0.437316176 | 0.000000000 |
| S | gerade (16) | 4080 | 0.436948529 | 0.436948529 | 0.000000000 |
| Q_X | alle 32 | 4096 | 0.187316895 | 0.225097656 | -0.037780762 |
| Q_X | ungerade (16) | 2048 | 0.187377930 | 0.231811523 | -0.044433594 |
| Q_X | gerade (16) | 2048 | 0.187255859 | 0.218383789 | -0.031127930 |
| Q_Y | alle 32 | 4096 | 0.185241699 | 0.220520020 | -0.035278320 |
| Q_Y | ungerade (16) | 2048 | 0.185668945 | 0.223510742 | -0.037841797 |
| Q_Y | gerade (16) | 2048 | 0.184814453 | 0.217529297 | -0.032714844 |

## Gewinn, Schaden und Grenzen des Gesamtvorteils

Ein Ziel zählt als besser, wenn U−R<0, als schlechter bei U−R>0. Gewinn ist die Summe der Verbesserungsbeträge, Schaden die Summe der Verschlechterungen; Netto = Gewinn−Schaden. Positive Nettowerte begünstigen U und haben damit das umgekehrte Vorzeichen zur aufsummierten U−R-Differenz.

| Maske, alle Geschichten | Besser | Schlechter | Gleich | Gewinn | Schaden | Netto | Maximaler Schaden pro Ziel |
|---|---:|---:|---:|---:|---:|---:|---:|
| Q | 2102 | 1422 | 4668 | 757.000000000 | 457.750000000 | 299.250000000 | 0.500000000 |
| G_all | 2102 | 1422 | 12828 | 757.000000000 | 457.750000000 | 299.250000000 | 0.500000000 |
| S | 0 | 0 | 8160 | 0.000000000 | 0.000000000 | 0.000000000 | 0.000000000 |
| Q_X | 1060 | 714 | 2322 | 381.500000000 | 226.750000000 | 154.750000000 | 0.500000000 |
| Q_Y | 1042 | 708 | 2346 | 375.500000000 | 231.000000000 | 144.500000000 | 0.500000000 |

Auf Q verbessert U 2102 Ziele, verschlechtert 1422 und bleibt auf 4668 gleich. Der maximale zusätzliche Fehler von 0.5 tritt an 409 Q-Zielpositionen auf. Die vollständigen Positionen stehen unter maximum_harm_targets in statistics.json. Die schlechteste ganze Geschichte für den Primärkontrast ist Geschichte 3 mit −0.005859375; auch sie begünstigt U im Q-Mittel. Untergruppen sind nicht durchgehend besser: Der schlechteste Q_X-Geschichtenmittelwert beträgt +0.015625 (Geschichte 3), der schlechteste Q_Y-Mittelwert +0.017578125 (Geschichte 32). Auf S sind alle 8160 beobachteten Fehler gleich.

## Vorab festgelegte Diagnosen — keine Kausalattribution

Die folgenden überlappenden Partitionen beziehen sich auf Q-Ziele und gebundene U-seitige Hypothesen-/Auswahlmerkmale. eligible=2 bedeutet mindestens zwei berechtigte Hypothesen. warm unterscheidet keine, nur kalte, gemischte oder vollständig warme berechtigte Hypothesen. mixed bei choice bedeutet Persistenz in einem Arm und Kontextwahl im anderen. Die Partitionen dürfen nicht über ihre Tabellen hinweg aufsummiert oder als unabhängige Experimente interpretiert werden.

| Partition | Klasse | Ziele | Besser | Schlechter | Gleich | Gewinn | Schaden | Netto |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| eligible | 0 | 439 | 0 | 0 | 439 | 0.000000000 | 0.000000000 | 0.000000000 |
| eligible | 1 | 4849 | 423 | 558 | 3868 | 105.750000000 | 139.500000000 | -33.750000000 |
| eligible | 2 | 2904 | 1679 | 864 | 361 | 651.250000000 | 318.250000000 | 333.000000000 |
| warm | none | 439 | 0 | 0 | 439 | 0.000000000 | 0.000000000 | 0.000000000 |
| warm | cold | 610 | 244 | 366 | 0 | 61.000000000 | 91.500000000 | -30.500000000 |
| warm | mixed | 1054 | 651 | 403 | 0 | 162.750000000 | 100.750000000 | 62.000000000 |
| warm | warm | 6089 | 1207 | 653 | 4229 | 533.250000000 | 265.500000000 | 267.750000000 |
| same_output | False | 3524 | 2102 | 1422 | 0 | 757.000000000 | 457.750000000 | 299.250000000 |
| same_output | True | 4668 | 0 | 0 | 4668 | 0.000000000 | 0.000000000 | 0.000000000 |
| choice | both_persistence | 439 | 0 | 0 | 439 | 0.000000000 | 0.000000000 | 0.000000000 |
| choice | mixed | 2189 | 1176 | 1013 | 0 | 294.000000000 | 253.250000000 | 40.750000000 |
| choice | same_context | 4229 | 0 | 0 | 4229 | 0.000000000 | 0.000000000 | 0.000000000 |
| choice | different_context | 1335 | 926 | 409 | 0 | 463.000000000 | 204.500000000 | 258.500000000 |

Deskriptiv liegt der positive Nettoeffekt vor allem bei mehreren berechtigten Hypothesen (+333). Bei genau einer berechtigten Hypothese ist die Bilanz negativ (−33.75), ebenso in der kalten Klasse (−30.5). Warme und gemischte Klassen sind insgesamt positiv. Diese Befunde begrenzen die Aussage „U ist besser“; sie erklären die Ursache nicht allein und autorisieren kein nachträgliches Tuning.

## Vollständige Primärkontraste je Geschichte

| Geschichte | Q: U−R exakt | Q: U−R dezimal |
|---|---:|---:|
| 1 | -1/64 | -0.015625000 |
| 2 | -5/256 | -0.019531250 |
| 3 | -3/512 | -0.005859375 |
| 4 | -71/1024 | -0.069335938 |
| 5 | -71/1024 | -0.069335938 |
| 6 | -3/64 | -0.046875000 |
| 7 | -55/1024 | -0.053710938 |
| 8 | -5/256 | -0.019531250 |
| 9 | -31/512 | -0.060546875 |
| 10 | -43/1024 | -0.041992188 |
| 11 | -11/512 | -0.021484375 |
| 12 | -1/32 | -0.031250000 |
| 13 | -35/1024 | -0.034179688 |
| 14 | -31/1024 | -0.030273438 |
| 15 | -5/512 | -0.009765625 |
| 16 | -1/64 | -0.015625000 |
| 17 | -21/1024 | -0.020507812 |
| 18 | -11/512 | -0.021484375 |
| 19 | -11/256 | -0.042968750 |
| 20 | -9/256 | -0.035156250 |
| 21 | -83/1024 | -0.081054688 |
| 22 | -5/512 | -0.009765625 |
| 23 | -31/1024 | -0.030273438 |
| 24 | -5/128 | -0.039062500 |
| 25 | -21/512 | -0.041015625 |
| 26 | -1/32 | -0.031250000 |
| 27 | -69/1024 | -0.067382812 |
| 28 | -13/256 | -0.050781250 |
| 29 | -25/512 | -0.048828125 |
| 30 | -17/512 | -0.033203125 |
| 31 | -57/1024 | -0.055664062 |
| 32 | -1/64 | -0.015625000 |

Die unveränderte statistics.json enthält zusätzlich alle kumulativen Kurven (511 beobachtete Ziele je Geschichte), Orientierungstabellen, Schadenspositionen und exakten rationalen Werte. In dieser Übergabe wurden gespeicherte Werte lediglich formatiert, keine Policies, Bootstrapziehungen oder Statistikreferenzen erneut ausgeführt.

## Integritäts- und Vollständigkeitsbelege

START.json bindet den freigegebenen SHA, consumed=true und den Namensraum. sources-manifest.json enthält 32 Quellen mit all_before_policy=true; alle Quellenhashes nach Abschluss erneut verglichen. 32 Archivdateien und 32 Erfassungsmanifeste vorhanden. terminal.json quittiert genau die Fälle 1–32; active_case=null, arms_created=distinct_arms=64, cleanup=CONFIRMED, worker_ended=true und worker_exitcode=0. result.json bestätigt COMPLETE, reference_equal=true und archive_integrity=true.

Jeder Fall wurde im gebundenen Lauf vor seiner Quittung mit dem unabhängigen Decoder gegen die Erfassungsanker geprüft. Zusätzlich wurden nach Ende sämtliche 102 Dateihashes aus closure.json geprüft. Die U/R-Erfassungsanker für äußere und interne Ereignisse stimmen in jeder Geschichte exakt überein. Quellen-, Archiv-, Erfassungs- und rekonstruierte Vollrecordhashes je Fall stehen in verification.json. Die nachträgliche Prüfung las Archive nur für Hashes, Formatgrößen und Metadaten; kein erneuter Decoder-/Policylauf.

| Erfasste Sammlung | U gesamt | R gesamt |
|---|---:|---:|
| Äußere Ereignisse | 98304 | 98304 |
| Interne Ereignisse | 364836 | 364836 |
| Prognosen | 16384 | 16384 |
| Beobachtete Fehlerziele | 16352 | 16352 |

Je Arm und Geschichte: 3072 äußere Ereignisse, 512 Prognosen, 511 beobachtete Ziele. Die letzte Prognose auf Ziel 1025 ist wegen des Endes nach Frame 1024 zensiert, keine nachträgliche Auslassung. Interne Ereignisse je Arm/Geschichte zwischen 11356 und 11436. Insgesamt 8192 Q- und 8160 S-Beobachtungen pro Arm. Die 32 Geschichten wurden vollständig einbezogen.

## Ressourcen und getrennter Cleanup

Startmarker 2026-10-15 10:43:06.942 UTC (12:43:06.942 Europe/Berlin); finaler Terminalbeleg 12:35:14.076 UTC (14:35:14.076 Europe/Berlin). Dateizeiten sind Metadaten; maßgebliche monotone Gesamtdauer im Supervisor: 6727.4106344 s = rund 112.12 Minuten. Der Worker war vorher beendet und liegt damit sicher innerhalb seiner 54000-s-Grenze; eine separate Worker-Wandzeit wurde nicht aufgezeichnet. Gesamtfrist 57600 s eingehalten; keine Forschung in der Abschlussreserve.

Harter gemeinsamer Windows-Job: 536870912 Byte, maximal zwei Prozesse. Gemessener Jobpeak 198234112 Byte, größter Prozesspeak 110362624 Byte. 131620 Worker-Budgetprüfungen mit zusammen 1845.716106 s gemessener Prüfzeit; 268527 Supervisorprüfungen mit 3828.274237 s. Diese Zeiten überlappen und dürfen nicht als zusätzliche serielle Laufzeit addiert werden. Der maximale Worker-Einzelcheck war 0.134949 s; die kurzen Vorbereitungsproben waren keine garantierte Latenzschranke. Die vollständige Serie blieb dennoch deutlich innerhalb des unveränderten Gesamtbudgets.

| Ressource vor dieser Ergebnisdokumentation | Beobachtete Bytes | Grenze |
|---|---:|---:|
| Vorbereitung einschließlich Berechtigung | 2815070 | 8388608 |
| Quellen gesamt | 198711 | 2097152 |
| Archive gesamt | 6035556 | 33554432 |
| Verwaltung | 247849 | 2097152 |
| Abschlusskategorie einschließlich Terminalslot | 28834 | 1048576 |
| Verbliebene temporäre Dateien | 0 | 67108864 |
| Größtes gzip-Fallarchiv | 190794 | 524288 |
| Größtes dekomprimiertes Archivformat | 1116226 | 4194304 |
| Laufverzeichnis | 6510950 | im Gesamtexport enthalten |
| Gesamtexport einschließlich Vorbereitung | 9326020 | 67108864 |

Alle gebundenen Einzelrecord-, Dictionary-, Tabellen- und Referenzgrenzen wurden durch die Lauf-/Decoderprüfungen eingehalten; zusätzliche historische Peakmesswerte dafür werden hier nicht erfunden. verification.json enthält die per Archiv nachgeprüften Formatgrößen. Ergebnisbericht, Verifikation und gesondertes delivery-closure.json zählen ebenfalls zum Export; dessen abschließendes Inventar enthält die finalen Summen einschließlich seiner eigenen Größe. Historische Laufdateien und das reguläre closure.json bleiben unverändert.

Workerende bestätigt; interner Arm-/Store-Cleanup für alle 64 Arme bestätigt; Datei-Cleanup bestätigt, keine Partialdateien. Keine erste Fehlerursache und keine Folgefehler. Die Vorstartbindung wurde nach Abschluss erneut vollständig geprüft.

## Aussagegrenzen und empfohlener nächster Schritt

Positiver Nachweis für die gebundene Auswahlregel gegenüber dieser Originalrecency-Baseline in der festgelegten synthetischen D-Familie. Kein Nachweis allgemeiner Intelligenz, Semantik, feldinterner Memory, realer Audio-/Video-Leistung oder Überlegenheit gegenüber beliebigen Abrufverfahren. Das nominale Bootstrapintervall beschreibt die vorab gewählte Geschichte-/Orientierungsstruktur; es ist keine Garantie für andere Verteilungen. Einzelne Ziele und Untergruppen zeigen Schäden trotz positivem Gesamtbild. Sekundäre Diagnosen bleiben deskriptiv.

Empfehlung: Der Projektleiter nimmt den vollständigen Befund ab und bewertet anhand der bereits gelieferten Diagnosen besonders die Nachteile kalter und Ein-Kandidaten-Zustände. Daraus lässt sich eine konkrete Gegenprognose für einen späteren Transfervergleich formulieren, bevor neue Daten oder Regeländerungen beauftragt werden. Aus diesem Abschluss folgt weder eine weitere Serie noch eine automatische Änderung des MCM-Kerns. Die Einmalfreigabe bleibt verbraucht.

## Belegpfade

Im selben Verzeichnis: START.json, terminal.json (maßgeblicher Supervisorabschluss), worker.json, result.json, closure.json, sources-manifest.json, statistics.json, verification.json sowie case-01 bis case-32 als .delta.json.gz und -capture.json. Die neue delivery-closure.json bindet die Ergebnisübergabe zusätzlich, ohne den Laufabschluss umzuschreiben. Vorbereitung und unveränderte Matrix: reports/s2uc/ura1-v4-preparation-20261015-01.
