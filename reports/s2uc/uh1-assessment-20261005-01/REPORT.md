# UH1 Ergebnis auf bekannten HX1 Quellen

Technischer Abschluss COMPLETE; Archivprüfung PASS. Primärurteil **H_ERWARTUNG_WIDERLEGT_U_VORTEIL**.

**Untersuchung auf bekannten Quellen.** Vergleich zweier Gesamtverfahren mit unterschiedlicher Speicherrepräsentation und unterschiedlichem Informationszugang. H kennt die Vierframephase und hält zwei vollständige Hinweisschlüssel mit Mittelwerten. U behält reguläre Originalspuren. Keine isolierte Kausalzuordnung zu Speicherumfang oder Mittelwertbildung. Keine unabhängige Replikation.


U erreicht in D einen mittleren Q-MAE von **0,186340332031**, H von
**0,190531240114**. Das vollständig negative Primärintervall belegt nach der
vorab festgelegten Entscheidungsregel einen begrenzten Vorteil von U gegenüber H.
Die Erwartung eines H-Vorteils ist widerlegt. Der Mittelwertvergleich war keine
MAE-optimale Referenz; das Ergebnis erlaubt keine Aussage über alle einfachen
hinweisabhängigen Verfahren.

In D stehen U-Gewinnen von 588,467059523 MAE-Summeneinheiten Schäden von
554,135140510 gegenüber, netto +34,331919013. In N beträgt der Nettowert
−13,929426042. N bleibt ergänzend; daraus wird kein Gleichwertigkeitsurteil abgeleitet.
H hatte je Bedingung 64 unbekannte und 8.128 bekannte Q-Ziele, ohne Slotersetzung.
U hatte weiterhin reguläre Verfügbarkeitsverluste. Diese Unterschiede sind
Bestandteile des Gesamtvergleichs und werden nicht als isolierte Ursachen ausgegeben.

## Einziger Primärkontrast

D:U−H auf allen Q-Zielen; positive Werte sprechen für H. 32 Paarwerte, 10.000 nach Orientierung geschichtete Clusterbootstrap-Ziehungen. Nominales approximatives 95%-Intervall; Urteile aus exakten rationalen Werten.

Mittel **-0.004190908083**, Intervall **[-0.007614034809; -0.000909328372]**, Urteil **H_ERWARTUNG_WIDERLEGT_U_VORTEIL**.

## Vollständige ergänzende Bilanzen

Alle Zahlen gerundet. Netto = Gewinn_U − Schaden_U. Explorative 95%-Intervalle; keine zusätzlichen bestätigenden Regeln. Masken überlappen und werden nicht addiert.

| C | Maske | o | n | U-MAE | H-MAE | U−H | 95%-Intervall | besser/schlechter/gleich | Gewinn U | Schaden U | Netto | Max. Schaden | Schlechtester Geschichtenkontrast |
| --- | --- | --- | ---: | ---: | ---: | ---: | --- | --- | ---: | ---: | ---: | ---: | ---: |
| D | Q | alle | 8192 | 0.186340332031 | 0.190531240114 | -0.004190908083 | [-0.007614034809; -0.000909328372] | 4411/3587/194 | 588.467059523023 | 554.135140509994 | 34.331919013030 | 0.421052631579 | 0.014953967304 |
| D | Q | 0 | 4096 | 0.184936523438 | 0.189577575635 | -0.004641052197 | [-0.010321670200; 0.000794005646] | 2224/1777/95 | 297.077688639309 | 278.067938840350 | 19.009749798959 | 0.421052631579 | 0.014953967304 |
| D | Q | 1 | 4096 | 0.187744140625 | 0.191484904593 | -0.003740763968 | [-0.007312272970; 0.000109658331] | 2187/1810/99 | 291.389370883715 | 276.067201669644 | 15.322169214071 | 0.414893617021 | 0.014094164349 |
| D | G_all | alle | 16352 | 0.311949608611 | 0.314049163345 | -0.002099554734 | [-0.003814467536; -0.000455553940] | 4411/3587/8354 | 588.467059523023 | 554.135140509994 | 34.331919013030 | 0.421052631579 | 0.007491615714 |
| D | G_all | 0 | 8176 | 0.311338062622 | 0.313663129868 | -0.002325067245 | [-0.005170934581; 0.000397779737] | 2224/1777/4175 | 297.077688639309 | 278.067938840350 | 19.009749798959 | 0.421052631579 | 0.007491615714 |
| D | G_all | 1 | 8176 | 0.312561154599 | 0.314435196822 | -0.001874042223 | [-0.003663291351; 0.000054936463] | 2187/1810/4179 | 291.389370883715 | 276.067201669644 | 15.322169214071 | 0.414893617021 | 0.007060872942 |
| D | S | alle | 8160 | 0.438051470588 | 0.438051470588 | 0.000000000000 | [0.000000000000; 0.000000000000] | 0/0/8160 | 0.000000000000 | 0.000000000000 | 0.000000000000 | 0.000000000000 | 0.000000000000 |
| D | S | 0 | 4080 | 0.438235294118 | 0.438235294118 | 0.000000000000 | [0.000000000000; 0.000000000000] | 0/0/4080 | 0.000000000000 | 0.000000000000 | 0.000000000000 | 0.000000000000 | 0.000000000000 |
| D | S | 1 | 4080 | 0.437867647059 | 0.437867647059 | 0.000000000000 | [0.000000000000; 0.000000000000] | 0/0/4080 | 0.000000000000 | 0.000000000000 | 0.000000000000 | 0.000000000000 | 0.000000000000 |
| D | Q_X | alle | 4096 | 0.187438964844 | 0.190652089503 | -0.003213124659 | [-0.007807841793; 0.001306612621] | 2211/1794/91 | 291.935970950144 | 278.775012345261 | 13.160958604883 | 0.421052631579 | 0.023792988304 |
| D | Q_X | 0 | 2048 | 0.186889648438 | 0.190384029242 | -0.003494380805 | [-0.011294542150; 0.004137953373] | 1116/891/41 | 147.833530601612 | 140.677038713818 | 7.156491887795 | 0.421052631579 | 0.023792988304 |
| D | Q_X | 1 | 2048 | 0.187988281250 | 0.190920149764 | -0.002931868514 | [-0.007665768164; 0.002007566393] | 1095/903/50 | 144.102440348532 | 138.097973631443 | 6.004466717089 | 0.400000000000 | 0.013172433064 |
| D | Q_Y | alle | 4096 | 0.185241699219 | 0.190410390725 | -0.005168691506 | [-0.011157028300; 0.000445434594] | 2200/1793/103 | 296.531088572879 | 275.360128164733 | 21.170960408146 | 0.414893617021 | 0.023227913053 |
| D | Q_Y | 0 | 2048 | 0.182983398438 | 0.188771122027 | -0.005787723589 | [-0.013572516421; 0.001609222360] | 1108/886/54 | 149.244158037697 | 137.390900126532 | 11.853257911164 | 0.412280701754 | 0.019789402301 |
| D | Q_Y | 1 | 2048 | 0.187500000000 | 0.192049659422 | -0.004549659422 | [-0.013605271178; 0.004115991047] | 1092/907/49 | 147.286930535183 | 137.969228038201 | 9.317702496982 | 0.414893617021 | 0.023227913053 |
| N | Q | alle | 8192 | 0.252716064453 | 0.251015695063 | 0.001700369390 | [-0.002033013776; 0.005587049008] | 3953/3941/298 | 601.578150872249 | 615.507576914087 | -13.929426041838 | 0.357142857143 | 0.030955395857 |
| N | Q | 0 | 4096 | 0.251647949219 | 0.251209119916 | 0.000438829303 | [-0.005298848911; 0.006822407384] | 1989/1965/142 | 304.591599399949 | 306.389044223984 | -1.797444824035 | 0.357142857143 | 0.030955395857 |
| N | Q | 1 | 4096 | 0.253784179688 | 0.250822270210 | 0.002961909477 | [-0.001844840698; 0.007673032086] | 1964/1976/156 | 296.986551472300 | 309.118532690103 | -12.131981217803 | 0.350000000000 | 0.017212746311 |
| N | G_all | alle | 16352 | 0.345018957926 | 0.344167109464 | 0.000851848461 | [-0.001018496138; 0.002798991284] | 3953/3941/8458 | 601.578150872249 | 615.507576914087 | -13.929426041838 | 0.357142857143 | 0.015507986965 |
| N | G_all | 0 | 8176 | 0.344483855186 | 0.344264011152 | 0.000219844034 | [-0.002654609239; 0.003417879237] | 1989/1965/4222 | 304.591599399949 | 306.389044223984 | -1.797444824035 | 0.357142857143 | 0.015507986965 |
| N | G_all | 1 | 8176 | 0.345554060665 | 0.344070207777 | 0.001483852889 | [-0.000924225477; 0.003844023902] | 1964/1976/4236 | 296.986551472300 | 309.118532690103 | -12.131981217803 | 0.350000000000 | 0.008623215373 |
| N | S | alle | 8160 | 0.437683823529 | 0.437683823529 | 0.000000000000 | [0.000000000000; 0.000000000000] | 0/0/8160 | 0.000000000000 | 0.000000000000 | 0.000000000000 | 0.000000000000 | 0.000000000000 |
| N | S | 0 | 4080 | 0.437683823529 | 0.437683823529 | 0.000000000000 | [0.000000000000; 0.000000000000] | 0/0/4080 | 0.000000000000 | 0.000000000000 | 0.000000000000 | 0.000000000000 | 0.000000000000 |
| N | S | 1 | 4080 | 0.437683823529 | 0.437683823529 | 0.000000000000 | [0.000000000000; 0.000000000000] | 0/0/4080 | 0.000000000000 | 0.000000000000 | 0.000000000000 | 0.000000000000 | 0.000000000000 |
| N | Q_X | alle | 4096 | 0.251037597656 | 0.251451260149 | -0.000413662492 | [-0.004580391903; 0.004082166315] | 1980/1948/168 | 305.454683427651 | 303.760321859277 | 1.694361568374 | 0.357142857143 | 0.026978475721 |
| N | Q_X | 0 | 2048 | 0.251098632812 | 0.251779529238 | -0.000680896425 | [-0.007196442052; 0.006483876735] | 993/978/77 | 153.107651159522 | 151.713175281093 | 1.394475878429 | 0.357142857143 | 0.026978475721 |
| N | Q_X | 1 | 2048 | 0.250976562500 | 0.251122991060 | -0.000146428560 | [-0.005287638766; 0.005245418746] | 987/970/91 | 152.347032268129 | 152.047146578184 | 0.299885689945 | 0.350000000000 | 0.023904031659 |
| N | Q_Y | alle | 4096 | 0.254394531250 | 0.250580129978 | 0.003814401272 | [-0.002209386628; 0.010047099636] | 1973/1993/130 | 296.123467444599 | 311.747255054810 | -15.623787610212 | 0.350000000000 | 0.043228601968 |
| N | Q_Y | 0 | 2048 | 0.252197265625 | 0.250638710595 | 0.001558555030 | [-0.007194861367; 0.010938747735] | 996/987/65 | 151.483948240427 | 154.675868942891 | -3.191920702464 | 0.338235294118 | 0.043228601968 |
| N | Q_Y | 1 | 2048 | 0.256591796875 | 0.250521549361 | 0.006070247514 | [-0.002228837602; 0.014267888483] | 977/1006/65 | 144.639519204172 | 157.071386111919 | -12.431866907748 | 0.350000000000 | 0.035616174364 |

Explorative Q-Interaktion D−N: -0.005891277473, 95%-Intervall [-0.010204426285; -0.001559239091].

## Verfügbarkeit und vollständige Beiträge auf Q

U-V0 keine passende Spur, V1 nur kalte Zellen, V2 warme Zellen/Persistenz, V3 warme Zellen/Kontextausgabe. H_known: bekannte Prognose vor Zielbeobachtung. H_replaced: regulärer Slotersatz beim Feedback. Jede Partition separat vollständig; Partitionen nicht miteinander addieren.

| C | Partition | Klasse | n | Gewinn U | Schaden U | Netto |
| --- | --- | --- | ---: | ---: | ---: | ---: |
| D | class | V0 | 437 | 13.637879841979 | 38.078213233197 | -24.440333391218 |
| D | class | V1 | 575 | 19.689525666306 | 54.248155271440 | -34.558629605135 |
| D | class | V2 | 1608 | 48.143613553167 | 140.788345527683 | -92.644731974517 |
| D | class | V3 | 5572 | 506.996040461572 | 321.020426477673 | 185.975613983899 |
| D | H_known | False | 64 | 0.000000000000 | 0.000000000000 | 0.000000000000 |
| D | H_known | True | 8128 | 588.467059523023 | 554.135140509994 | 34.331919013030 |
| D | H_replaced | False | 8192 | 588.467059523023 | 554.135140509994 | 34.331919013030 |
| D | H_replaced | True | 0 | 0.000000000000 | 0.000000000000 | 0.000000000000 |
| N | class | V0 | 576 | 9.525724946202 | 10.155643072655 | -0.629918126453 |
| N | class | V1 | 976 | 20.628379458973 | 18.363158101165 | 2.265221357807 |
| N | class | V2 | 1961 | 25.831962562836 | 25.655543093603 | 0.176419469233 |
| N | class | V3 | 4679 | 545.592083904239 | 561.333232646665 | -15.741148742425 |
| N | H_known | False | 64 | 0.000000000000 | 0.000000000000 | 0.000000000000 |
| N | H_known | True | 8128 | 601.578150872249 | 615.507576914087 | -13.929426041838 |
| N | H_replaced | False | 8192 | 601.578150872249 | 615.507576914087 | -13.929426041838 |
| N | H_replaced | True | 0 | 0.000000000000 | 0.000000000000 | 0.000000000000 |

## Alle Primärpaarwerte

| r | U−H in D |
| ---: | ---: |
| 1 | -0.025274521193 |
| 2 | 0.002139992335 |
| 3 | -0.021051739619 |
| 4 | 0.007301818206 |
| 5 | 0.010904483719 |
| 6 | -0.009376480545 |
| 7 | 0.002636791109 |
| 8 | -0.004982427951 |
| 9 | -0.014142746600 |
| 10 | 0.001896440871 |
| 11 | 0.004808797722 |
| 12 | 0.014094164349 |
| 13 | -0.001212828423 |
| 14 | -0.004495437691 |
| 15 | -0.009322035100 |
| 16 | -0.004653111949 |
| 17 | -0.000136299810 |
| 18 | -0.010557757109 |
| 19 | -0.009320973028 |
| 20 | 0.002632895722 |
| 21 | -0.018671550621 |
| 22 | -0.013508499482 |
| 23 | 0.008909398766 |
| 24 | -0.006759036677 |
| 25 | -0.010112895269 |
| 26 | -0.014394360008 |
| 27 | -0.000025972735 |
| 28 | -0.000085319398 |
| 29 | -0.007198711376 |
| 30 | -0.008406891826 |
| 31 | 0.014953967304 |
| 32 | -0.010698212340 |

## Ressourcen und Vollständigkeit

- 64 unveränderte Archivquellen, 128 frische Armläufe, 131,072 Frame-Verarbeitungen und ebenso viele unabhängige Referenzfortschritte. Keine Quellenneugenerierung.
- Worker 452.442988 s; Supervisor 457.089727 s; Grenzen 3.540/3.600 s. Worker beendet, Exitcode 0.
- Gemeinsamer Job-Peak 116,539,392 Byte unter 536.870.912 Byte.
- U-Zusatzheap 5,332 Byte unter 16.384; H-eigener Heap 3,959 Byte unter 32.768. Unterschiedliche Messgrenzen, keine Ressourcengleichheit.
- U-Bank 416 Byte; H-Bank 3.520 Byte, konservative Numerik 3.928 unter 4.096 Byte. U konservativ Original/Kombination 16/18; Ausgabeslots U/H 2/1.
- U Receipt 782 Byte, UTF-8-Obergrenze 1564 Byte. H Receipt 0, geliehener aktueller Frame 384 Rohbytes/1584 Objektbytes.
- Vorbereitung und Archivquellen belastet: 8,200,240 Byte; Export 15,379,474; zusammen 23,579,714 unter 67.108.864 Byte.
- Fallarchive gesamt 15,194,358 unter 33.554.432 Byte; Verwaltung 176,459 unter 2.097.152; Abschluss 8,657 unter 1.048.576 Byte.
- Größter Fall komprimiert 253,320 unter 524.288 Byte; expandiert 1,692,906 unter 4.194.304 Byte.
- Rohressourcenwerte original_frames_peak/combined_peak=0 bedeuten deaktiviertes Rohframe-Tracing, nicht Nullbelegung. Konservative Belegung und externe Grenzstelleninventare separat in verification.json.
- 69 Abschlussdateien hashgeprüft. 65.536 H-Zustände dekodiert, 32.704 H-Ausgaben aus dem Archiv erneut bewertet; 32.704 U-Fehler stimmen mit HX1 überein. U wurde im neuen Lauf frisch ausgeführt.
- Primärintervall und alle 30 ergänzenden Intervalle, Interaktion, 512 Diagnosezeilen, Gewinn-/Schadenssummen und kumulierte Zielverläufe aus archivierten Werten nachgeprüft. Keine Policy während dieser Prüfung ausgeführt.

## Grenzen und Belege

HX1 bleibt abgenommen. UH1 prüft einen weiteren Leistungsvergleich; weder Semantik noch Feld-Memory oder allgemeine Überlegenheit werden behauptet. Der Mittelwert ist unter MAE nicht allgemein optimal. Nichtnachweis ist kein Gleichwertigkeitsnachweis. Eine Übernahme von H ist nicht beauftragt und wurde nicht vorgenommen.

[Exakte Auswertung mit allen Maximalschadenspositionen und Geschichtenwerten](../uh1-comparison-20261004-01/assessment.json), [terminaler Laufabschluss](../uh1-comparison-20261004-01/closure.json), [Prüfbilanz und vollständige Ressourcenmaxima](verification.json). Vollständige U-Lebenszyklen, H-Zustandsdeltas und Zielverläufe verbleiben in den 64 ursprünglichen Fallarchiven.

Einmalfreigabe VERBRAUCHT. Die Autorisierungsdatei bleibt als historischer Beleg AUTHORIZED_ONCE; der exklusive Zielordner sperrt Wiederverwendung. Kein weiterer Lauf, keine Ersatzquelle oder Fallkürzung.

## Nächster vorgeschlagener Schritt

Projektleiter: den begrenzten U-Vorteil auf bekannten Quellen fachlich abnehmen.
Als nächste konzeptionelle Aufgabe ein getrenntes, bislang ungesehenes Prüfmaterial
und eine vorab festgelegte Übertragbarkeitsfrage für die unveränderten Verfahren
spezifizieren. Damit würde die derzeitige Aussagegrenze bekannter Quellen adressiert.
Keine neue Quelle, Implementierung oder Ausführung ist dadurch freigegeben.
U bleibt unverändert, A1/K1 deaktiviert; H wurde nicht übernommen.
