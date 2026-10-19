# UHR1 Ergebnis: U-Vorteil auf neuen Folgen derselben Aufgabenfamilie repliziert

Stand 2026-10-05. Genau ein autorisierter Forschungsversuch; technischer Abschluss **COMPLETE**, unabhängige Archivprüfung **PASS_ARCHIVE_VERIFICATION**. Primärurteil **U_VORTEIL_REPLIZIERT**. Die Einmalbeauftragung ist verbraucht.

## Einziger Primärkontrast

U−H in D auf sämtlichen 256 Q-Zielen je Geschichte, 32 neue Paare; keine Aufwärmphase oder Ausschlüsse. Negative Werte sprechen für U. 10.000 nach Orientierung geschichtete Paarbootstrap-Ziehungen, nominales approximatives 95%-Intervall. Urteile aus den ungerundeten rationalen Werten.

**Mittlere Fehlerdifferenz -0.005799488143; 95%-Intervall [-0.009360747140; -0.002299448369].** Das gesamte Intervall liegt unter null; die vorregistrierte Replikationsregel ist erfüllt.

D: U-MAE 0.185607910156, H-MAE 0.191407398300. Keine zusätzliche konfirmatorische Regel und kein Pooling mit UH1.

## Vollständige ergänzende Bilanz

Alle 30 Kombinationen aus Bedingung, Maske und Orientierung. Zahlen gerundet; exakte Brüche, alle Maximalschadenspositionen und Geschichtenkontraste stehen in assessment.json. Masken überlappen und werden nicht addiert. Ergänzende Intervalle sind explorativ.

| C | Maske | o | n | U-MAE | H-MAE | U−H | 95%-Intervall | besser/schlechter/gleich | Gewinn U | Schaden U | Netto | Max. Schaden | Schlechtester Geschichtenkontrast |
| --- | --- | --- | ---: | ---: | ---: | ---: | --- | --- | ---: | ---: | ---: | ---: | ---: |
| D | Q | alle | 8192 | 0.185607910156 | 0.191407398300 | -0.005799488143 | [-0.009360747140; -0.002299448369] | 4412/3572/208 | 595.004019077417 | 547.494612206384 | 47.509406871033 | 0.428571428571 | 0.011292746102 |
| D | Q | 0 | 4096 | 0.185546875000 | 0.192011009403 | -0.006464134403 | [-0.010886415356; -0.002224946021] | 2222/1778/96 | 301.683361455094 | 275.206266938392 | 26.477094516703 | 0.406250000000 | 0.009122586153 |
| D | Q | 1 | 4096 | 0.185668945312 | 0.190803787196 | -0.005134841883 | [-0.010767801143; 0.000372643839] | 2190/1794/112 | 293.320657622323 | 272.288345267992 | 21.032312354331 | 0.428571428571 | 0.011292746102 |
| D | G_all | alle | 16352 | 0.311261619374 | 0.314167038091 | -0.002905418718 | [-0.004689532814; -0.001151974134] | 4412/3572/8368 | 595.004019077417 | 547.494612206384 | 47.509406871033 | 0.428571428571 | 0.005657422705 |
| D | G_all | 0 | 8176 | 0.311185176125 | 0.314423568312 | -0.003238392186 | [-0.005453859748; -0.001114650062] | 2222/1778/4176 | 301.683361455094 | 275.206266938392 | 26.477094516703 | 0.406250000000 | 0.004570219286 |
| D | G_all | 1 | 8176 | 0.311338062622 | 0.313910507871 | -0.002572445249 | [-0.005394436580; 0.000186686542] | 2190/1794/4192 | 293.320657622323 | 272.288345267992 | 21.032312354331 | 0.428571428571 | 0.005657422705 |
| D | S | alle | 8160 | 0.437408088235 | 0.437408088235 | 0.000000000000 | [0.000000000000; 0.000000000000] | 0/0/8160 | 0.000000000000 | 0.000000000000 | 0.000000000000 | 0.000000000000 | 0.000000000000 |
| D | S | 0 | 4080 | 0.437316176471 | 0.437316176471 | 0.000000000000 | [0.000000000000; 0.000000000000] | 0/0/4080 | 0.000000000000 | 0.000000000000 | 0.000000000000 | 0.000000000000 | 0.000000000000 |
| D | S | 1 | 4080 | 0.437500000000 | 0.437500000000 | 0.000000000000 | [0.000000000000; 0.000000000000] | 0/0/4080 | 0.000000000000 | 0.000000000000 | 0.000000000000 | 0.000000000000 | 0.000000000000 |
| D | Q_X | alle | 4096 | 0.185546875000 | 0.190177310306 | -0.004630435306 | [-0.009905232643; 0.000913913966] | 2203/1786/107 | 294.576135596768 | 275.609872583543 | 18.966263013225 | 0.428571428571 | 0.024633987585 |
| D | Q_X | 0 | 2048 | 0.188232421875 | 0.190505908208 | -0.002273486333 | [-0.010388014129; 0.005850794250] | 1095/902/51 | 146.257628953875 | 141.601528944464 | 4.656100009411 | 0.406250000000 | 0.024633987585 |
| D | Q_X | 1 | 2048 | 0.182861328125 | 0.189848712404 | -0.006987384279 | [-0.014317440456; 0.000282792312] | 1108/884/56 | 148.318506642893 | 134.008343639079 | 14.310163003814 | 0.428571428571 | 0.016569610249 |
| D | Q_Y | alle | 4096 | 0.185668945312 | 0.192637486293 | -0.006968540981 | [-0.011770067912; -0.002058758803] | 2209/1786/101 | 300.427883480649 | 271.884739622841 | 28.543143857808 | 0.397435897436 | 0.027208355575 |
| D | Q_Y | 0 | 2048 | 0.182861328125 | 0.193516110599 | -0.010654782474 | [-0.016926320813; -0.004555693297] | 1127/876/45 | 155.425732501219 | 133.604737993928 | 21.820994507291 | 0.397435897436 | 0.010556942272 |
| D | Q_Y | 1 | 2048 | 0.188476562500 | 0.191758861988 | -0.003282299488 | [-0.010410120795; 0.004364457394] | 1082/910/56 | 145.002150979430 | 138.280001628913 | 6.722149350517 | 0.392307692308 | 0.027208355575 |
| N | Q | alle | 8192 | 0.252380371094 | 0.250726131377 | 0.001654239717 | [-0.002803427166; 0.005751717156] | 3982/3894/316 | 599.887921368767 | 613.439453129405 | -13.551531760639 | 0.375000000000 | 0.021227795012 |
| N | Q | 0 | 4096 | 0.247741699219 | 0.250066500612 | -0.002324801394 | [-0.009025306744; 0.003741108479] | 2042/1912/142 | 312.141323432535 | 302.618936924024 | 9.522386508511 | 0.357142857143 | 0.021227795012 |
| N | Q | 1 | 4096 | 0.257019042969 | 0.251385762141 | 0.005633280827 | [-0.000462398452; 0.010981729226] | 1940/1982/174 | 287.746597936231 | 310.820516205381 | -23.073918269150 | 0.375000000000 | 0.020530486499 |
| N | G_all | alle | 16352 | 0.344667318982 | 0.343838580494 | 0.000828738488 | [-0.001404456663; 0.002881486481] | 3982/3894/8476 | 599.887921368767 | 613.439453129405 | -13.551531760639 | 0.375000000000 | 0.010634668343 |
| N | G_all | 0 | 8176 | 0.342435176125 | 0.343599851579 | -0.001164675454 | [-0.004521484396; 0.001874214815] | 2042/1912/4222 | 312.141323432535 | 302.618936924024 | 9.522386508511 | 0.357142857143 | 0.010634668343 |
| N | G_all | 1 | 8176 | 0.346899461840 | 0.344077309409 | 0.002822152430 | [-0.000231651671; 0.005501609945] | 1940/1982/4254 | 287.746597936231 | 310.820516205381 | -23.073918269150 | 0.375000000000 | 0.010285331788 |
| N | S | alle | 8160 | 0.437316176471 | 0.437316176471 | 0.000000000000 | [0.000000000000; 0.000000000000] | 0/0/8160 | 0.000000000000 | 0.000000000000 | 0.000000000000 | 0.000000000000 | 0.000000000000 |
| N | S | 0 | 4080 | 0.437500000000 | 0.437500000000 | 0.000000000000 | [0.000000000000; 0.000000000000] | 0/0/4080 | 0.000000000000 | 0.000000000000 | 0.000000000000 | 0.000000000000 | 0.000000000000 |
| N | S | 1 | 4080 | 0.437132352941 | 0.437132352941 | 0.000000000000 | [0.000000000000; 0.000000000000] | 0/0/4080 | 0.000000000000 | 0.000000000000 | 0.000000000000 | 0.000000000000 | 0.000000000000 |
| N | Q_X | alle | 4096 | 0.250976562500 | 0.250940880288 | 0.000035682212 | [-0.005148664227; 0.004933522207] | 2012/1922/162 | 304.931775312549 | 305.077929651811 | -0.146154339262 | 0.375000000000 | 0.025363739793 |
| N | Q_X | 0 | 2048 | 0.246582031250 | 0.250028580802 | -0.003446549552 | [-0.010692038322; 0.003101870861] | 1032/942/74 | 156.948448014739 | 149.889914532637 | 7.058533482102 | 0.357142857143 | 0.014203465217 |
| N | Q_X | 1 | 2048 | 0.255371093750 | 0.251853179775 | 0.003517913975 | [-0.004342160748; 0.010528306334] | 980/980/88 | 147.983327297810 | 155.188015119174 | -7.204687821364 | 0.375000000000 | 0.025363739793 |
| N | Q_Y | alle | 4096 | 0.253784179688 | 0.250511382465 | 0.003272797222 | [-0.003567908033; 0.010198972911] | 1970/1972/154 | 294.956146056218 | 308.361523477594 | -13.405377421377 | 0.346153846154 | 0.048494072372 |
| N | Q_Y | 0 | 2048 | 0.248901367188 | 0.250104420423 | -0.001203053236 | [-0.011848393638; 0.009534860227] | 1010/970/68 | 155.192875417796 | 152.729022391387 | 2.463853026409 | 0.346153846154 | 0.048494072372 |
| N | Q_Y | 1 | 2048 | 0.258666992188 | 0.250918344508 | 0.007748647680 | [-0.000788910244; 0.016550864624] | 960/1002/86 | 139.763270638422 | 155.632501086207 | -15.869230447786 | 0.346153846154 | 0.040816091705 |

Explorative Q-Interaktion D−N: -0.007453727860, 95%-Intervall [-0.012578937441; -0.001803387268].

N auf Q: U−H 0.001654239717, 95%-Intervall [-0.002803427166; 0.005751717156]. Dieses Intervall enthält null; daraus folgt keine Gleichwertigkeit. Die N-Bilanz ändert die einzige primäre Erfolgsregel nicht.

## Verfügbarkeit und Beiträge auf Q

U-V0 keine passende Spur, V1 nur kalte Zellen, V2 warme Zellen/Persistenz, V3 warme Zellen/Kontext. H_known wird vor Zielbeobachtung bestimmt. Jede Partition separat vollständig, Partitionen nicht addieren. Nullbelegungen werden als solche berichtet.

| C | Partition | Klasse | n | Gewinn U | Schaden U | Netto |
| --- | --- | --- | ---: | ---: | ---: | ---: |
| D | class | V0 | 448 | 13.612160560512 | 34.473751902780 | -20.861591342268 |
| D | class | V1 | 627 | 22.532709865566 | 56.209111461463 | -33.676401595897 |
| D | class | V2 | 1571 | 46.523155142827 | 138.693060454629 | -92.169905311802 |
| D | class | V3 | 5546 | 512.335993508513 | 318.118688387512 | 194.217305121000 |
| D | H_known | False | 64 | 0.000000000000 | 0.000000000000 | 0.000000000000 |
| D | H_known | True | 8128 | 595.004019077417 | 547.494612206384 | 47.509406871033 |
| D | H_replaced | False | 8192 | 595.004019077417 | 547.494612206384 | 47.509406871033 |
| D | H_replaced | True | 0 | 0.000000000000 | 0.000000000000 | 0.000000000000 |
| N | class | V0 | 597 | 12.166977252725 | 11.509178720947 | 0.657798531778 |
| N | class | V1 | 1060 | 19.061631110375 | 19.003000676587 | 0.058630433788 |
| N | class | V2 | 1869 | 25.028906096236 | 22.647382466728 | 2.381523629508 |
| N | class | V3 | 4666 | 543.630406909430 | 560.279891265143 | -16.649484355712 |
| N | H_known | False | 64 | 0.000000000000 | 0.000000000000 | 0.000000000000 |
| N | H_known | True | 8128 | 599.887921368767 | 613.439453129405 | -13.551531760639 |
| N | H_replaced | False | 8192 | 599.887921368767 | 613.439453129405 | -13.551531760639 |
| N | H_replaced | True | 0 | 0.000000000000 | 0.000000000000 | 0.000000000000 |

H-Slotersetzungen gesamt: 0. Je D/N 8.128 bekannte und 64 unbekannte H-Hinweise. H besitzt Phasenwissen; seine Schlüsselverfügbarkeit ist keine mit U gleichgesetzte Ressource.

## Alle 32 Primärpaarwerte

| r | U−H in D |
| ---: | ---: |
| 1 | -0.008136449137 |
| 2 | -0.017772062123 |
| 3 | 0.009122586153 |
| 4 | -0.002547538562 |
| 5 | -0.020682601275 |
| 6 | -0.004888299063 |
| 7 | -0.024760857382 |
| 8 | 0.000046422768 |
| 9 | -0.018219552015 |
| 10 | 0.009313830604 |
| 11 | -0.008578494459 |
| 12 | -0.001752104657 |
| 13 | -0.005109665836 |
| 14 | 0.007168867098 |
| 15 | -0.000280440369 |
| 16 | 0.011292746102 |
| 17 | -0.011104051441 |
| 18 | -0.004287762881 |
| 19 | 0.004089062966 |
| 20 | -0.004073123572 |
| 21 | -0.003479989408 |
| 22 | 0.004341814520 |
| 23 | -0.006290348523 |
| 24 | -0.023212682984 |
| 25 | -0.003424841934 |
| 26 | -0.024739018813 |
| 27 | 0.006540016266 |
| 28 | -0.022907615962 |
| 29 | -0.009713720230 |
| 30 | -0.011555872543 |
| 31 | -0.003396803832 |
| 32 | 0.003414929931 |

Alle 640 armweisen Geschichtenmittelwerte für D/N und Q/G_all/S/Q_X/Q_Y sind zusätzlich in verification.json unter story_means archiviert. Vollständige Zielreihen, kumulierte Differenzen für G_all/Q, Zellalter und Feedbackpositionen liegen in den 64 Fallarchiven. Die 512 Geschichten-/Verfügbarkeitspartitionen bleiben vollständig in assessment.json erhalten.

## Quellen und vollständiger Ablauf

64 neue Quellen aus MCM-UHR1/source/v1, 32 D/N-Paare, je 1.024 Frames. Sämtliche Quellen wurden innerhalb des autorisierten Workers erzeugt, unabhängig gegen das Rezept geprüft und vor dem ersten U/H-Aufruf im Manifest versiegelt. Vor jedem Replay erneute Byte-/Hashprüfung. Kein Ersatzmaterial, keine Auswahl oder nachträgliche Änderung der N-Kontingenzen.
32 Quellenpaare, 16 je Orientierung; D/N teilen jeweils dieselbe Fortsetzungsfolge. Alle Längen, Katalogwerte, Phasen und Quoten wurden auch im Archiv unabhängig geprüft. Die nachstehenden N-Tabellen sind beobachtete Kontingenzen, keine nachträglich angepassten Quoten.

| r | Orientierung | N: XA | N: XB | N: YA | N: YB |
| ---: | ---: | ---: | ---: | ---: | ---: |
| 1 | 0 | 69 | 59 | 59 | 69 |
| 2 | 1 | 61 | 67 | 67 | 61 |
| 3 | 0 | 62 | 66 | 66 | 62 |
| 4 | 1 | 64 | 64 | 64 | 64 |
| 5 | 0 | 66 | 62 | 62 | 66 |
| 6 | 1 | 62 | 66 | 66 | 62 |
| 7 | 0 | 63 | 65 | 65 | 63 |
| 8 | 1 | 65 | 63 | 63 | 65 |
| 9 | 0 | 65 | 63 | 63 | 65 |
| 10 | 1 | 63 | 65 | 65 | 63 |
| 11 | 0 | 61 | 67 | 67 | 61 |
| 12 | 1 | 69 | 59 | 59 | 69 |
| 13 | 0 | 60 | 68 | 68 | 60 |
| 14 | 1 | 55 | 73 | 73 | 55 |
| 15 | 0 | 65 | 63 | 63 | 65 |
| 16 | 1 | 70 | 58 | 58 | 70 |
| 17 | 0 | 60 | 68 | 68 | 60 |
| 18 | 1 | 66 | 62 | 62 | 66 |
| 19 | 0 | 67 | 61 | 61 | 67 |
| 20 | 1 | 67 | 61 | 61 | 67 |
| 21 | 0 | 65 | 63 | 63 | 65 |
| 22 | 1 | 65 | 63 | 63 | 65 |
| 23 | 0 | 64 | 64 | 64 | 64 |
| 24 | 1 | 63 | 65 | 65 | 63 |
| 25 | 0 | 63 | 65 | 65 | 63 |
| 26 | 1 | 67 | 61 | 61 | 67 |
| 27 | 0 | 66 | 62 | 62 | 66 |
| 28 | 1 | 63 | 65 | 65 | 63 |
| 29 | 0 | 64 | 64 | 64 | 64 |
| 30 | 1 | 63 | 65 | 65 | 63 |
| 31 | 0 | 56 | 72 | 72 | 56 |
| 32 | 1 | 63 | 65 | 65 | 63 |

128 frische U/H-Armläufe, 65.536 Quellframes, 131.072 Armverarbeitungen und ebenso viele unabhängige Referenzfortschritte. Je Arm 32.704 beobachtete Ziele, davon 16.384 Q-Ziele. Alle 64 Geschichten vollständig; rechtszensierte letzte Prognosen ohne erfundenes Feedback. Worker beendet, Exitcode 0, kein Resume.

## Ressourcen

| Größe | Beobachtet | Grenze |
| --- | ---: | ---: |
| Workerzeit | 462.016625 s | 3.540 s |
| Supervisorzeit einschließlich Vorbereitung im Versuch | 466.731947 s | 3.600 s |
| Gemeinsamer privater Job-Peak | 117858304 Byte | 536870912 Byte |
| U-Zusatzheap | 5308 Byte | 16384 Byte |
| H-Eigenheap | 5063 Byte | 32768 Byte |
| H konservative Numerik | 3928 Byte | 4096 Byte |
| Vorbereitungsbytes einschließlich Autorisierung | 8212164 Byte | 8388608 Byte |
| Quellen gesamt | 396416 Byte | 2097152 Byte |
| Fallarchive gesamt | 15213920 Byte | 33554432 Byte |
| Größter Fall gzip / expandiert | 252283 / 1687220 Byte | 524288 / 4194304 Byte |
| Verwaltung im Versuch | 190616 Byte | 2097152 Byte |
| Terminaler Abschluss | 16082 Byte | 1048576 Byte |
| Vorbereitung plus gesamter Versuchsexport | 24029198 Byte | 67108864 Byte |

U-Bank 416 Byte; H-Bank 3520 Byte. Konservative U-Original-/Kombinationsgrenze beobachtet 16/18 unter 18/20; Ausgabeslots U/H 2/1. U-Receipt 776 Byte, UTF-8-Obergrenze 1552 Byte. H-Receipt 0, geliehener Frame 384 Rohbytes/1584 Objektbytes.
Beobachter-/Referenzspeicher zählt zum gemeinsamen Prozesslimit und ist für die Arme unerreichbar. U-Zusatzheap und H-Eigenheap sind unterschiedliche Messgrenzen. Rohframe-Traces mit Wert 0 sind deaktiviert und kein Nullbelegungsnachweis. Die zusätzliche Berichtsausgabe wird in export-accounting.json separat und im Gesamtbudget nachgerechnet.

## Unabhängige Archivprüfung und Bindungen

133 Abschlussdateien vollständig hash- und längengeprüft; 65.536 H-Zustände aus XOR/zlib rekonstruiert. Je 32.704 H-Ausgaben aus eingefrorenen Zuständen und U-Ausgaben aus archivierten Original-/Persistenzzuordnungen unabhängig bewertet. Primärintervall, alle 30 ergänzenden Intervalle, Interaktion, Gewinn-/Schadenssummen, Maximalpositionen, Verfügbarkeitsbeiträge und kumulierte Zielverläufe nachgerechnet. Keine Policy und kein Quellgenerator während dieser Nachprüfung ausgeführt.

Vorstart-SHA256: `91a770a4b5ba5e442807abc50bd458c194e57c6c8cebfc135102bbca304c6355`.
Autorisierungs-SHA256: `79840b0848cd538677ad75c25f1e84d29591495f656f71c0085c4edf024fdaf6`.
Manifest-SHA256: `b38d6e0883b87b83d98b7170107687a7d213f09818fb942095d830c1ae71bbbf`.
Laufabschluss-SHA256: `e9c5ddce5469e0c2591e138e7798dd9a382a5e2f291a87585bf19f21d9cf696c`.

[Exakte Auswertung und Maximalschadenspositionen](../uhr1-comparison-20261005-01/assessment.json), [Manifest](../uhr1-comparison-20261005-01/manifest.json), [terminaler Laufabschluss](../uhr1-comparison-20261005-01/closure.json), [unabhängige Prüfbilanz mit Geschichtenmittelwerten und Ressourcen](verification.json), [prüfbares Auditprogramm](verify_archive.py).

## Einordnung und nächster Vorschlag

Beobachteter Befund: Der zuvor auf bekannten Folgen gefundene U-Vorteil gegenüber H ist auf den 32 neuen Paaren dieser Aufgabenfamilie nach der vorregistrierten Regel repliziert. UH1 und UHR1 bleiben getrennte Auswertungen; kein gemeinsames Intervall und keine zusammengezogene Stichprobe.
Technische Interpretation: Der Vorteil betrifft genau diese beiden unveränderten Gesamtverfahren, dieses Quellenrezept und diese Grenzen. H besitzt zwei dauerhaft verfügbare Hinweisschlüssel und Phasenwissen; U speichert reguläre Originalspuren. Speicherumfang, Informationszugang und Mittelwertbildung sind nicht isoliert kausal geprüft. Der Mittelwert ist unter MAE nicht allgemein optimal.
Aussagegrenze: Kein Nachweis für andere Aufgabenstrukturen, Audio/Video, Semantik, allgemeine Kognition, Cluster oder feldinterne Memory. Die neue Quelle ist eine pseudorandomisierte Folge desselben festen Alphabets und derselben Quoten, keine neue Aufgabenfamilie.
Empfohlener nächster Schritt an den Projektleiter: diesen Replikationsbefund abnehmen und anschließend konzeptionell genau eine gezielt veränderte Aufgabenstruktur für eine Übertragbarkeitsprüfung festlegen. U zunächst unverändert halten, eine passende einfache Baseline und die Erfolgsregel vorab bestimmen. Das ist ein Vorschlag für einen neuen begrenzten Konzeptauftrag, keine Implementierungs- oder Versuchsfreigabe. Eine weitere Wiederholung desselben Rezepts wird nicht automatisch gestartet.

Einmalbeauftragung VERBRAUCHT. Die Autorisierungsdatei bleibt als historischer Beleg AUTHORIZED_ONCE; Marker und exklusiver Zielordner verhindern Wiederverwendung. Kein Retry, Resume, Ersatzmaterial oder erneuter neutraler Größenablauf.
