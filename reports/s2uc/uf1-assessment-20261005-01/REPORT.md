# UF1 Abschluss und unabhängige Archivprüfung

Berichts- und Prüfdatum: 2026-10-14. Forschungsversuch: 2026-10-05. Autor: MCM-KI-Entwickler; Empfänger: MCM KI Projektleiter.

**Abschluss: PASS_ARCHIVE_VERIFICATION; F_VORTEIL_BELEGT unabhängig bestätigt.** Genau ein vorhandener Forschungsversuch COMPLETE, 32 neue D/N-Paare, 64 Geschichten und 128 Armläufe. Die UF1-Einmalbeauftragung ist VERBRAUCHT. Dieser Abschluss erzeugt keine neue Laufnummer oder Forschungsfreigabe.

Einziger Primärkontrast D, U−F auf allen Q-Zielen: **0.057098388672**, nominales 95%-Intervall **[0.054504394531; 0.059814453125]**. Exakt: 1871/32768, [893/16384; 245/4096]. Das gesamte Intervall ist positiv: F hat in dieser Aufgabenfamilie weniger Fehler als U.

## Fehlerwerte und ergänzende Befunde

| Bedingung | U mittlere MAE | F mittlere MAE | U−F | 95%-Intervall | Einordnung |
| --- | --- | --- | --- | --- | --- |
| D | 0.186218261719 | 0.129119873047 | 0.057098388672 | [0.054504394531; 0.059814453125] | einziger Primärvergleich |
| N | 0.246673583984 | 0.257720947266 | -0.011047363281 | [-0.017975616455; -0.003936767578] | ergänzend, kein zweiter Primärtest |

Alle 32 D-Paarkontraste sind positiv. In N ist der ergänzende mittlere Kontrast negativ: U hat dort weniger Fehler als F. Die 30 Nebenintervalle und die Interaktion sind nominal und nicht für Mehrfachvergleiche korrigiert; daraus entsteht kein zusätzlicher konfirmatorischer Gesamtsieg.
Explorative Interaktion (D:U−F)−(N:U−F): 0.068145751953, 95%-Intervall [0.060882568359; 0.075531005859].

## Bedeutung für den Erfahrungsmechanismus

**Beobachtung:** U bildet und nutzt begrenzte Verlaufsspuren mit rückgemeldeten Fehlerwerten; die archivierten Ausgaben und Fehlerupdates sind konsistent. In D gewinnt U an 832 Q-Zielen gegen F, verliert an 2323 und ist an 5037 gleich. Seine Gewinnsumme 238,5 wird durch die Schadenssumme 706,25 übertroffen. In N gewinnt U an 2643 Q-Zielen, verliert an 2406 und ist an 3143 gleich; Gewinn 884,25, Schaden 793,75. Technische Funktion und zusätzlicher Vorhersagenutzen sind damit getrennte Aussagen.

**Technische Interpretation:** Auf der stabilen hinweisabhängigen Zweiwerteaufgabe nutzt die einfache Häufigkeitsregel die bisher beobachteten Alternativen wirksamer als U als Gesamtverfahren. U erreicht hier keinen Vorteil gegenüber dieser passenden Baseline. In D ist die Nettobilanz gegenüber F in jeder U-Verfügbarkeitsklasse negativ, auch bei warmem Kontextabruf V3. Der Abstand lässt sich daher deskriptiv nicht ausschließlich auf fehlende oder kalte Spuren reduzieren. Das ist keine kausale Zerlegung der Fehlerursache.

**Hypothese:** Die Speicherung alternativer Fortsetzungen samt ihrer empirischen Häufigkeiten und die zur absoluten Fehlerbewertung passende Mehrheitswahl können den D-Vorteil erklären. UF1 isoliert diese Erklärung nicht: F besitzt explizites Vierframe-Phasenwissen, zwei exakte Zweiframe-Hinweisschlüssel und eine andere Speicherrepräsentation. U hält zwei Retained-Vierframespuren und einen Kandidaten mit Fehlerbewertung. Ein Gleichbudget- oder Gleichinformationsvergleich liegt nicht vor. Insbesondere sind U-Zusatzheap und F-Eigenheap keine direkt vergleichbaren Gesamtgrößen; U-Bank allein gegen F-Bank zu stellen wäre irreführend.

**Grenzen und Nichtnachweis:** F kann je Hinweis nur zwei verschiedene Fortsetzungswerte aufnehmen; ein dritter Wert wäre terminal. In diesen Quellen gibt es nur zwei Hinweise, daher keine F-Hinweisverdrängung. Kein Nachweis für variierende Aufgaben, Audio/Video, allgemeine Kognition, Semantik, Clusterbildung oder feldinterne Memory. Der ergänzende U-Vorteil in N belegt ebenfalls keine allgemeine Überlegenheit. Die Ergebnisse von UH1/UHR1 bleiben eigenständige Befunde mit anderen Quellen und Vergleichsarm H; sie werden weder gepoolt noch kausal mit UF1 verrechnet.

## Unabhängige Prüfungen und Aussagegrenzen des Audits

Das nachgelagerte Skript importiert ausschließlich die Python-Standardbibliothek. Es führt keine Policy, keinen Produktions- oder Referenzprädiktor und keinen Quellengenerator aus. Die Auswertung verwendet nur vorhandene UF1-Archive sowie die vorab gebundenen Dateien.

| Prüfung | Ergebnis |
| --- | --- |
| Bindungen | PASS: exakter Vorstart-SHA, operative Code-/Vorstartdateien, Vertrags-SHA, Autorisierungsvorlage plus AUTHORIZED_ONCE, archivierter Planhash und 4.690.185 Vorbereitungsbytes |
| Archivvollständigkeit | PASS: exakt 133 im Versuchsabschluss gebundene Dateien plus closure.json; alle Dateilängen und SHA256; 64 Quellen und 64 Fallarchive |
| Quellen | PASS: kanonische Bytes, IDs/r/C/o, Katalog, 1024 Frames, Phasen, D-Quoten, N-Randquoten, identische D/N-Fortsetzungsfolgen je Paar, Ziehungszähler und Quellenhashes |
| F | PASS: 65.536 vollständige Bankzustände aus XOR/zlib-Deltas dekodiert; Schlüssel, Wertebits, Häufigkeiten gegen ausschließlich vergangenes Feedback, Reihenfolge, Stempel, Puffer, Tickets, Ausgabe und Phasen geprüft |
| F-Fehler | PASS: 32.704 eingefrorene Ausgaben aus Vorzustand gegen archivierte Ziele mit sequenziellem binary64-MAE nachgerechnet; F0/F1/F2 und Zählerdiagnosen geprüft |
| U | PASS: 32.704 Ausgaben anhand ursprünglicher Frameindices neu bewertet; archivierte Auswahl anhand Fehlerzellen, EC/EP-Updates und Feedbackhistorie rekonstruiert; Profil und Zeitfenster geprüft |
| Statistik | PASS: alle 320.000 Bootstrapindices gegen SHA-Rezept, 640 Armmittelwerte, 32 Primärpaare, Primärintervall, 30 Nebenbilanzen/-intervalle, 704 Falldiagnosen und explorative Interaktion exakt rational nachgerechnet |
| Ressourcen | PASS: archivierte Laufzeit-/Speicher-/Exportmessungen und sämtliche Kategoriegrenzen; zusätzlicher Abschluss im Exportbudget |
| Cleanup | COMPLETE, Workerexit 0, Worker beendet, Cleanup-Marker je Fall, Ziel 1025 rechtszensiert, Resume verboten |

Die Vollständigkeitsprüfung des vorbereiteten Skripts führte zu Ergänzungen ausschließlich an verify_archive.py: vollständige F-Zustandsprüfung gegen Präfixhäufigkeiten, U-Zell-/Auswahl-/Feedbackprüfung, unabhängige Bootstrapindexprüfung, eindeutige Nebenbilanz-/Diagnoseabdeckung, fehlende Primär-/Interaktionsmittelwerte, Fallidentitäten, Plan-/Vorbereitungsbindung und Ressourcenteilgrenzen. Während der Entwicklung wurde der Zugriff auf im Kompaktarchiv nicht enthaltene prior_feedback-Felder durch Rekonstruktion aus Updates und ursprünglichen Frameindices ersetzt; ein Syntaxfehler wurde vor der erfolgreichen Auswertung korrigiert. Diese Prüfskriptkorrekturen veränderten keine gebundenen Versuchsdaten oder Verfahren.

Auditgrenze: Die ursprüngliche Quellenrezeptprüfung und die kausale Versiegelung vor dem ersten Policy-Aufruf sind durch den gebundenen Starter und das Manifest belegt; das Audit prüft deren Bindung und die archivierten Quellen, erzeugt aber das Forschungsrezept nicht erneut. Die damals unabhängige U-Lebenszyklusreferenz und der Cleanup sind im gebundenen Lauf belegt; das Audit führt keine zweite U-Zustandsmaschine aus. Prozesspeaks sind archivierte Windows-Job-Messungen, keine heute erneut gemessenen Laufwerte. Die 3600-s-Frist betrifft den damaligen Versuch, nicht die am 14.10. erfolgende nachgelagerte Dokumentation.

## Vollständige ergänzende Vergleiche

Orientierung 0: ungerade Paare; 1: gerade Paare; alle: 32 Paare. Q hat 256, G_all 511, S 255 und Q_X/Q_Y jeweils 128 Ziele je Geschichte. Positive U−F-Werte bedeuten F-Vorteil. Alle Q-Ziele einschließlich Kaltstart zählen. S ist in beiden Armen identisch.

| C | Maske | Orientierung | U | F | U−F | 95%-Intervall |
| --- | --- | --- | --- | --- | --- | --- |
| D | Q | alle | 0.186218261719 | 0.129119873047 | 0.057098388672 | [0.054504394531; 0.059814453125] |
| D | Q | 0 | 0.187255859375 | 0.128906250000 | 0.058349609375 | [0.054321289062; 0.062622070312] |
| D | Q | 1 | 0.185180664062 | 0.129333496094 | 0.055847167969 | [0.052612304688; 0.059020996094] |
| D | G_all | alle | 0.311704990215 | 0.283099926614 | 0.028605063601 | [0.027305528376; 0.029965753425] |
| D | G_all | 0 | 0.312224804305 | 0.282992906067 | 0.029231898239 | [0.027213796477; 0.031372309198] |
| D | G_all | 1 | 0.311185176125 | 0.283206947162 | 0.027978228963 | [0.026357632094; 0.029568248532] |
| D | S | alle | 0.437683823529 | 0.437683823529 | 0.000000000000 | [0.000000000000; 0.000000000000] |
| D | S | 0 | 0.437683823529 | 0.437683823529 | 0.000000000000 | [0.000000000000; 0.000000000000] |
| D | S | 1 | 0.437683823529 | 0.437683823529 | 0.000000000000 | [0.000000000000; 0.000000000000] |
| D | Q_X | alle | 0.188110351562 | 0.128967285156 | 0.059143066406 | [0.055297851562; 0.063110351562] |
| D | Q_X | 0 | 0.188598632812 | 0.128540039062 | 0.060058593750 | [0.055175781250; 0.065185546875] |
| D | Q_X | 1 | 0.187622070312 | 0.129394531250 | 0.058227539062 | [0.052124023438; 0.064086914062] |
| D | Q_Y | alle | 0.184326171875 | 0.129272460938 | 0.055053710938 | [0.050842285156; 0.058959960938] |
| D | Q_Y | 0 | 0.185913085938 | 0.129272460938 | 0.056640625000 | [0.049438476562; 0.062988281250] |
| D | Q_Y | 1 | 0.182739257812 | 0.129272460938 | 0.053466796875 | [0.049072265625; 0.057617187500] |
| N | Q | alle | 0.246673583984 | 0.257720947266 | -0.011047363281 | [-0.017975616455; -0.003936767578] |
| N | Q | 0 | 0.244079589844 | 0.254516601562 | -0.010437011719 | [-0.019226074219; -0.001036071777] |
| N | Q | 1 | 0.249267578125 | 0.260925292969 | -0.011657714844 | [-0.022033691406; -0.001342773438] |
| N | G_all | alle | 0.341854207436 | 0.347388698630 | -0.005534491194 | [-0.009005396893; -0.001972235812] |
| N | G_all | 0 | 0.340508806262 | 0.345737524462 | -0.005228718200 | [-0.009631849315; -0.000519049658] |
| N | G_all | 1 | 0.343199608611 | 0.349039872798 | -0.005840264188 | [-0.011038405088; -0.000672700587] |
| N | S | alle | 0.437408088235 | 0.437408088235 | 0.000000000000 | [0.000000000000; 0.000000000000] |
| N | S | 0 | 0.437316176471 | 0.437316176471 | 0.000000000000 | [0.000000000000; 0.000000000000] |
| N | S | 1 | 0.437500000000 | 0.437500000000 | 0.000000000000 | [0.000000000000; 0.000000000000] |
| N | Q_X | alle | 0.248901367188 | 0.256286621094 | -0.007385253906 | [-0.015136718750; 0.000732421875] |
| N | Q_X | 0 | 0.245971679688 | 0.257934570312 | -0.011962890625 | [-0.020751953125; -0.001342773438] |
| N | Q_X | 1 | 0.251831054688 | 0.254638671875 | -0.002807617188 | [-0.014892578125; 0.009399414062] |
| N | Q_Y | alle | 0.244445800781 | 0.259155273438 | -0.014709472656 | [-0.023681640625; -0.005981445312] |
| N | Q_Y | 0 | 0.242187500000 | 0.251098632812 | -0.008911132812 | [-0.022097778320; 0.003417968750] |
| N | Q_Y | 1 | 0.246704101562 | 0.267211914062 | -0.020507812500 | [-0.033081054688; -0.008056640625] |

## Gewinne und Schäden

Perspektive U gegen F: Gewinn=sum(max(F−U,0)), Schaden=sum(max(U−F,0)), Netto=Gewinn−Schaden. Diese Ziel-Summen sind keine Geschichtenmittelwerte. Besser/schlechter/gleich zählen Ziele. Schlechtestes Paar ist der größte Geschichtenmittelwert U−F.

| C/Maske/o | Ziele | Gewinn | Schaden | Netto | besser/schlechter/gleich | max. Schaden | schlechtestes Paarmittel |
| --- | --- | --- | --- | --- | --- | --- | --- |
| D/Q/alle | 8192 | 238.500000000000 | 706.250000000000 | -467.750000000000 | 832/2323/5037 | 0.500000000000 | 0.075195312500 |
| D/Q/0 | 4096 | 119.750000000000 | 358.750000000000 | -239.000000000000 | 415/1177/2504 | 0.500000000000 | 0.075195312500 |
| D/Q/1 | 4096 | 118.750000000000 | 347.500000000000 | -228.750000000000 | 417/1146/2533 | 0.500000000000 | 0.066406250000 |
| D/G_all/alle | 16352 | 238.500000000000 | 706.250000000000 | -467.750000000000 | 832/2323/13197 | 0.500000000000 | 0.037671232877 |
| D/G_all/0 | 8176 | 119.750000000000 | 358.750000000000 | -239.000000000000 | 415/1177/6584 | 0.500000000000 | 0.037671232877 |
| D/G_all/1 | 8176 | 118.750000000000 | 347.500000000000 | -228.750000000000 | 417/1146/6613 | 0.500000000000 | 0.033268101761 |
| D/S/alle | 8160 | 0.000000000000 | 0.000000000000 | 0.000000000000 | 0/0/8160 | 0.000000000000 | 0.000000000000 |
| D/S/0 | 4080 | 0.000000000000 | 0.000000000000 | 0.000000000000 | 0/0/4080 | 0.000000000000 | 0.000000000000 |
| D/S/1 | 4080 | 0.000000000000 | 0.000000000000 | 0.000000000000 | 0/0/4080 | 0.000000000000 | 0.000000000000 |
| D/Q_X/alle | 4096 | 116.250000000000 | 358.500000000000 | -242.250000000000 | 402/1182/2512 | 0.500000000000 | 0.080078125000 |
| D/Q_X/0 | 2048 | 58.250000000000 | 181.250000000000 | -123.000000000000 | 201/594/1253 | 0.500000000000 | 0.080078125000 |
| D/Q_X/1 | 2048 | 58.000000000000 | 177.250000000000 | -119.250000000000 | 201/588/1259 | 0.500000000000 | 0.078125000000 |
| D/Q_Y/alle | 4096 | 122.250000000000 | 347.750000000000 | -225.500000000000 | 430/1141/2525 | 0.500000000000 | 0.074218750000 |
| D/Q_Y/0 | 2048 | 61.500000000000 | 177.500000000000 | -116.000000000000 | 214/583/1251 | 0.500000000000 | 0.074218750000 |
| D/Q_Y/1 | 2048 | 60.750000000000 | 170.250000000000 | -109.500000000000 | 216/558/1274 | 0.500000000000 | 0.066406250000 |
| N/Q/alle | 8192 | 884.250000000000 | 793.750000000000 | 90.500000000000 | 2643/2406/3143 | 0.500000000000 | 0.039062500000 |
| N/Q/0 | 4096 | 446.250000000000 | 403.500000000000 | 42.750000000000 | 1327/1202/1567 | 0.500000000000 | 0.039062500000 |
| N/Q/1 | 4096 | 438.000000000000 | 390.250000000000 | 47.750000000000 | 1316/1204/1576 | 0.500000000000 | 0.039062500000 |
| N/G_all/alle | 16352 | 884.250000000000 | 793.750000000000 | 90.500000000000 | 2643/2406/11303 | 0.500000000000 | 0.019569471624 |
| N/G_all/0 | 8176 | 446.250000000000 | 403.500000000000 | 42.750000000000 | 1327/1202/5647 | 0.500000000000 | 0.019569471624 |
| N/G_all/1 | 8176 | 438.000000000000 | 390.250000000000 | 47.750000000000 | 1316/1204/5656 | 0.500000000000 | 0.019569471624 |
| N/S/alle | 8160 | 0.000000000000 | 0.000000000000 | 0.000000000000 | 0/0/8160 | 0.000000000000 | 0.000000000000 |
| N/S/0 | 4080 | 0.000000000000 | 0.000000000000 | 0.000000000000 | 0/0/4080 | 0.000000000000 | 0.000000000000 |
| N/S/1 | 4080 | 0.000000000000 | 0.000000000000 | 0.000000000000 | 0/0/4080 | 0.000000000000 | 0.000000000000 |
| N/Q_X/alle | 4096 | 435.500000000000 | 405.250000000000 | 30.250000000000 | 1287/1222/1587 | 0.500000000000 | 0.048828125000 |
| N/Q_X/0 | 2048 | 216.750000000000 | 192.250000000000 | 24.500000000000 | 648/582/818 | 0.500000000000 | 0.046875000000 |
| N/Q_X/1 | 2048 | 218.750000000000 | 213.000000000000 | 5.750000000000 | 639/640/769 | 0.500000000000 | 0.048828125000 |
| N/Q_Y/alle | 4096 | 448.750000000000 | 388.500000000000 | 60.250000000000 | 1356/1184/1556 | 0.500000000000 | 0.031250000000 |
| N/Q_Y/0 | 2048 | 229.500000000000 | 211.250000000000 | 18.250000000000 | 679/620/749 | 0.500000000000 | 0.031250000000 |
| N/Q_Y/1 | 2048 | 219.250000000000 | 177.250000000000 | 42.000000000000 | 677/564/807 | 0.500000000000 | 0.029296875000 |

Alle Positionen maximalen Schadens stehen verlustfrei in [assessment.json](../uf1-comparison-20261005-01/assessment.json) unter secondary[].maximum_harm_targets als [Paar,Ziel]. Sämtliche 30 Paarlisten, 704 Falldiagnosen und 640 Armmittelwerte bleiben dort vollständig erhalten; die 640 Armmittelwerte stehen zusätzlich in [verification.json](verification.json). Die Positionen wurden unabhängig gegen alle archivierten Ziele geprüft.

## Diagnosen auf allen Q-Zielen

V0: keine passende Spur; V1: nur kalte Zellen; V2: warm/Persistenz; V3: warm/Kontext. F0: unbekannt; F1: Gleichstand; F2: strikte Mehrheit. Partitionen überlappen und werden nicht addiert. Leere Gruppen haben keine definierte mittlere Leistung; ihre Summen sind null.

| C | Partition | Label | Anzahl | Gewinn | Schaden | Netto | besser/schlechter/gleich | max. Schaden |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| D | class | V0 | 437 | 25.250000000000 | 64.000000000000 | -38.750000000000 | 101/256/80 | 0.250000000000 |
| D | class | V1 | 623 | 40.750000000000 | 109.000000000000 | -68.250000000000 | 163/436/24 | 0.250000000000 |
| D | class | V2 | 1572 | 109.750000000000 | 279.750000000000 | -170.000000000000 | 439/1119/14 | 0.250000000000 |
| D | class | V3 | 5560 | 62.750000000000 | 253.500000000000 | -190.750000000000 | 129/512/4919 | 0.500000000000 |
| D | F_class | F0 | 64 | 0.000000000000 | 0.000000000000 | 0.000000000000 | 0/0/64 | 0.000000000000 |
| D | F_class | F1 | 71 | 1.750000000000 | 2.500000000000 | -0.750000000000 | 7/10/54 | 0.250000000000 |
| D | F_class | F2 | 8057 | 236.750000000000 | 703.750000000000 | -467.000000000000 | 825/2313/4919 | 0.500000000000 |
| D | F_known | False | 64 | 0.000000000000 | 0.000000000000 | 0.000000000000 | 0/0/64 | 0.000000000000 |
| D | F_known | True | 8128 | 238.500000000000 | 706.250000000000 | -467.750000000000 | 832/2323/4973 | 0.500000000000 |
| D | F_replaced | False | 8192 | 238.500000000000 | 706.250000000000 | -467.750000000000 | 832/2323/5037 | 0.500000000000 |
| D | F_replaced | True | 0 | 0.000000000000 | 0.000000000000 | 0.000000000000 | 0/0/0 | nicht definiert |
| N | class | V0 | 567 | 59.250000000000 | 52.750000000000 | 6.500000000000 | 237/211/119 | 0.250000000000 |
| N | class | V1 | 959 | 107.500000000000 | 106.750000000000 | 0.750000000000 | 430/427/102 | 0.250000000000 |
| N | class | V2 | 1905 | 228.000000000000 | 211.250000000000 | 16.750000000000 | 912/845/148 | 0.250000000000 |
| N | class | V3 | 4761 | 489.500000000000 | 423.000000000000 | 66.500000000000 | 1064/923/2774 | 0.500000000000 |
| N | F_class | F0 | 64 | 0.000000000000 | 0.000000000000 | 0.000000000000 | 0/0/64 | 0.000000000000 |
| N | F_class | F1 | 629 | 42.500000000000 | 38.500000000000 | 4.000000000000 | 170/154/305 | 0.250000000000 |
| N | F_class | F2 | 7499 | 841.750000000000 | 755.250000000000 | 86.500000000000 | 2473/2252/2774 | 0.500000000000 |
| N | F_known | False | 64 | 0.000000000000 | 0.000000000000 | 0.000000000000 | 0/0/64 | 0.000000000000 |
| N | F_known | True | 8128 | 884.250000000000 | 793.750000000000 | 90.500000000000 | 2643/2406/3079 | 0.500000000000 |
| N | F_replaced | False | 8192 | 884.250000000000 | 793.750000000000 | 90.500000000000 | 2643/2406/3143 | 0.500000000000 |
| N | F_replaced | True | 0 | 0.000000000000 | 0.000000000000 | 0.000000000000 | 0/0/0 | nicht definiert |

## Alle Primärpaare

| Paar | Orientierung | D: U−F exakt | D: U−F dezimal |
| --- | --- | --- | --- |
| 1 | 0 | 53/1024 | 0.051757812500 |
| 2 | 1 | 57/1024 | 0.055664062500 |
| 3 | 0 | 15/256 | 0.058593750000 |
| 4 | 1 | 61/1024 | 0.059570312500 |
| 5 | 0 | 77/1024 | 0.075195312500 |
| 6 | 1 | 63/1024 | 0.061523437500 |
| 7 | 0 | 77/1024 | 0.075195312500 |
| 8 | 1 | 51/1024 | 0.049804687500 |
| 9 | 0 | 55/1024 | 0.053710937500 |
| 10 | 1 | 3/64 | 0.046875000000 |
| 11 | 0 | 7/128 | 0.054687500000 |
| 12 | 1 | 53/1024 | 0.051757812500 |
| 13 | 0 | 67/1024 | 0.065429687500 |
| 14 | 1 | 31/512 | 0.060546875000 |
| 15 | 0 | 27/512 | 0.052734375000 |
| 16 | 1 | 43/1024 | 0.041992187500 |
| 17 | 0 | 15/256 | 0.058593750000 |
| 18 | 1 | 49/1024 | 0.047851562500 |
| 19 | 0 | 31/512 | 0.060546875000 |
| 20 | 1 | 59/1024 | 0.057617187500 |
| 21 | 0 | 55/1024 | 0.053710937500 |
| 22 | 1 | 33/512 | 0.064453125000 |
| 23 | 0 | 29/512 | 0.056640625000 |
| 24 | 1 | 61/1024 | 0.059570312500 |
| 25 | 0 | 41/1024 | 0.040039062500 |
| 26 | 1 | 7/128 | 0.054687500000 |
| 27 | 0 | 1/16 | 0.062500000000 |
| 28 | 1 | 17/256 | 0.066406250000 |
| 29 | 0 | 31/512 | 0.060546875000 |
| 30 | 1 | 55/1024 | 0.053710937500 |
| 31 | 0 | 55/1024 | 0.053710937500 |
| 32 | 1 | 63/1024 | 0.061523437500 |

## Quellenkontingenzen

D je ungeradem Paar XA/XB/YA/YB=96/32/32/96, je geradem Paar 32/96/96/32. N hat die folgenden tatsächlichen Kontingenzen, ohne erzwungene 64er-Balance. Die vollständigen 64 Quellenhashes und Ziehungszähler stehen in verification.json unter source_tables und im [Manifest](../uf1-comparison-20261005-01/manifest.json).

| Paar | Orientierung | N: XA/XB/YA/YB |
| --- | --- | --- |
| 1 | 0 | 56/72/72/56 |
| 2 | 1 | 54/74/74/54 |
| 3 | 0 | 69/59/59/69 |
| 4 | 1 | 63/65/65/63 |
| 5 | 0 | 64/64/64/64 |
| 6 | 1 | 65/63/63/65 |
| 7 | 0 | 62/66/66/62 |
| 8 | 1 | 65/63/63/65 |
| 9 | 0 | 68/60/60/68 |
| 10 | 1 | 64/64/64/64 |
| 11 | 0 | 70/58/58/70 |
| 12 | 1 | 58/70/70/58 |
| 13 | 0 | 69/59/59/69 |
| 14 | 1 | 59/69/69/59 |
| 15 | 0 | 65/63/63/65 |
| 16 | 1 | 62/66/66/62 |
| 17 | 0 | 58/70/70/58 |
| 18 | 1 | 71/57/57/71 |
| 19 | 0 | 64/64/64/64 |
| 20 | 1 | 63/65/65/63 |
| 21 | 0 | 56/72/72/56 |
| 22 | 1 | 63/65/65/63 |
| 23 | 0 | 66/62/62/66 |
| 24 | 1 | 53/75/75/53 |
| 25 | 0 | 61/67/67/61 |
| 26 | 1 | 65/63/63/65 |
| 27 | 0 | 60/68/68/60 |
| 28 | 1 | 62/66/66/62 |
| 29 | 0 | 64/64/64/64 |
| 30 | 1 | 67/61/61/67 |
| 31 | 0 | 68/60/60/68 |
| 32 | 1 | 64/64/64/64 |

## Ressourcen und Export

| Messgröße | Wert | Grenze |
| --- | --- | --- |
| Workerzeit (s) | 461.8608642000472 | 3540 |
| Supervisor bis Abschlusswrite (s) | 465.8609131 | 3600 |
| Job Private Commit (Byte) | 204697600 | 536870912 |
| Prozesspeak (Byte) | 176828416 | im gemeinsamen Job |
| U Zusatzheap (Byte) | 5359 | 16384 |
| F Eigenheap (Byte) | 5847 | 32768 |
| F Bank / konservative Numerik (Byte) | 4304 / 4712 | 5120 |
| U Originalframes / kombinierte Obergrenze | 16 / 18 | 18 / 20 |
| U Receipt / UTF-8-Obergrenze (Byte) | 778 / 1556 | 16384 / 32768 |
| Vorbereitung (Byte) | 4690185 | 8388608 |
| Quellen gesamt (Byte) | 396416 | 2097152 |
| Fallarchive gesamt (Byte) | 9801582 | 33554432 |
| Größtes gzip / expandiert (Byte) | 159520 / 1652521 | 524288 / 4194304 |
| Laufverwaltung (Byte) | 262749 | 2097152 |
| Versuchsabschluss (Byte) | 15955 | 1048576 |
| Laufexport (Byte) | 10476702 | Teil der Gesamtsumme |
| Vorbereitung plus Laufexport (Byte) | 15166887 | 67108864 |

F besitzt einen Ausgabeslot, keine Receipts und höchstens 384 Byte geliehene Eingangsrohdaten (Objektgraph 1584 Byte). U besitzt bis zu zwei Ausgabeslots. U-Grenzstellenmaxima: 15 Originale, 5760 Originalrohbytes, 15907 Originalobjektbytes, 17183 Basisarmbytes und 20871 insgesamt erreichbare Bytes; Zusatzheap wird separat gemessen. Nullwerte deaktivierter Rohtrace-Spitzen bedeuten nicht Nullspeicher. F konservative Numerik ist eine gebundene Entwurfsobergrenze, kein neu erhobener numerischer Peak.

Externe Beobachtermaxima: U-Belege 11021954 Byte, F-Trace 601440 Byte, Eingangsobjekte 458136 Byte, F-Referenzgrenzstelle 798 Byte. Diese Größen gehören zum gemeinsamen Prozessbudget, nicht zur Arm-Memory. Vollständige Phasenspitzen stehen in verification.json/maxima.

Die nachgelagerten Prüf-/Berichtsdateien sowie die neu eingefügten Übersichtstexte werden zusätzlich belastet. [export-accounting.json](export-accounting.json) enthält die abschließende Bytebilanz samt 16-KiB-Reserve für Bilanz und Abschluss; die bereits vorhandenen historischen Übersichtstexte werden nicht als neue Kopie belastet. Verwaltungsgrenze 2 MiB und Gesamtgrenze 64 MiB bleiben verbindlich.

## Bindungen und Artefakte

| Artefakt | SHA256 |
| --- | --- |
| Vorstart | 1a2c3bcab967eeed4d6fa422693216f8ba2853bac7aaab389ecc54aa606eb6d7 |
| Codebindung | 32a61bfa36d3cfaa400154c9ad839ea5f3a6fffcb83d5a6404c2508c7b388f06 |
| Autorisierung | c07f558f9c6d39c3800187db6f4d42115d5e0e1883073710e5929e0d8f040a53 |
| Quellenmanifest | c82e867bf5403c605be518afe6ffa0ad18eaf716ba588794875b61cbb0faa68c |
| Versuchsabschluss | c45ae3b7908cec60ccfa34d125e258776ec4394b9e5f48391a56550eed556489 |
| Vorhandene Auswertung | 36fa1143c6bb2eb7bc625c9b61ca99a81854258b2fcdb58650380d7bc06fb23a |
| Prüfskript | b818b5698c58f602ca0b7d5644267fa866092cb35c741ff735d943dd07def216 |
| Unabhängige Prüfung | 33a2fefabb51232cdcc4c5745c88175deebb123012b90fb347d1a4a66b586618 |

Forschungsarchiv: reports/s2uc/uf1-comparison-20261005-01. Abschlussordner: reports/s2uc/uf1-assessment-20261005-01. [Prüfskript](verify_archive.py), [Prüfergebnis](verification.json), [Abschlussbindung](closure.json). Gebundener Code, Quellen, Matrix, Autorisierung und Versuchsabschluss bleiben unverändert. AUTHORIZED_ONCE in der historischen Autorisierungsdatei wird nicht umgeschrieben: Der vorhandene Versuchsmarker und Abschluss belegen den Verbrauch. Kein Retry, Resume, Ersatzmaterial oder Pooling.

## Begründeter nächster fachlicher Schritt

Vorschlag an den Projektleiter: zunächst einen eng begrenzten Konzeptvertrag für einen Vergleich unter angeglichenem Informationszugang und nachvollziehbar abgeglichenem Gesamtbudget festlegen. Er soll genau die offene Frage trennen, ob U gegenüber der Häufigkeitsspeicherung einen eigenständigen Nutzen aus Verlaufserfahrung gewinnt oder ob der jetzige Abstand durch Aufgabenpassung, Phasenwissen und Speicherung der Alternativen erklärt wird. Die notwendige Angleichung muss vor jeder Implementierung festlegen, welches Phasenwissen beide Verfahren erhalten, welche Originaldaten und Zusatzspeicher zählen und welcher einzelne Kontrast die Erklärung falsifizieren würde. Ist das ohne eine andere Forschungsfrage nicht sinnvoll möglich, soll der Projektleiter die Grenze ausdrücklich festhalten und den nächsten Aufgabenstrukturwechsel begründen.

Begründung: Die vorliegende stabile Zweiwerteaufgabe zeigt einen klaren D-Vorteil der einfachen Baseline und einen ergänzenden N-Vorteil von U. Ein weiteres unverändertes Wiederholen liefert keine neue mechanistische Gegenprognose. Deshalb jetzt keine U-Änderung, keine neue Laufserie und kein vorweggenommener Architekturwechsel. Der Folgeauftrag ist in diesem Abschluss ausschließlich vorgeschlagen und wurde nicht ausgeführt.
