# AS480 – archivbasierte Diagnose

Auftrag 60d11630-4c59-4467-99c5-1d5fa8c1e3d0. 2026-10-19.

**A480 scheitert an der festen Distanzschranke:** Offset0 hat relative Paar-L1=0.035964472284790765, größer als τ=0.03125. Alle drei Offsets liegen über τ. Signalzulassung besteht; kein Exaktmatch. Mehrdeutigkeit und fehlender Nachfolger sind nicht der Auslöser.

## Ablehnungskette und Gegenfälle

ε=3.3647428814553505e-05; τ=0.03125. Beide Werte unverändert. Signalbedingung: jeder der zwei Hinweise und jeweils beide gespeicherten Frames haben mittlere Absolutaktivität strikt über ε. Exaktprüfung testet die vorhandenen Faktoren0,5/1/2 ohne Toleranz.

| Fall | Offset | Hinweisamplituden | Speicheramplituden | L1 Frame0 / Frame1 | Paar-L1 | ≤τ | Exaktfaktoren | Nachfolger |
|---|---:|---|---|---|---:|---|---|---|
| A0 | 0 | 0.00163922979277 / 0.00160489001558 | 0.00163922979277 / 0.00160489001558 | 0 / 0 | 0 | True | [1.0] | 3 |
| A0 | 1 | 0.00163922979277 / 0.00160489001558 | 0.00160489001558 / 0.00161266274881 | 1.97903871677 / 1.749721416 | 1.86978599198 | False | [] | 4 |
| A0 | 2 | 0.00163922979277 / 0.00160489001558 | 0.00161266274881 / 0.0015982322655 | 1.98379073302 / 1.99584956116 | 1.98975632431 | False | [] | None |
| A480 | 0 | 0.00170491434669 / 0.00165913129207 | 0.00163922979277 / 0.00160489001558 | 0.0390213104461 / 0.0328232819151 | 0.0359644722848 | False | [] | 3 |
| A480 | 1 | 0.00170491434669 / 0.00165913129207 | 0.00160489001558 / 0.00161266274881 | 1.90390094398 / 1.69841459947 | 1.80255605724 | False | [] | 4 |
| A480 | 2 | 0.00170491434669 / 0.00165913129207 | 0.00161266274881 / 0.0015982322655 | 1.92779159695 / 1.93985943475 | 1.9337433971 | False | [] | None |
| B0 | 0 | 0.00163464699278 / 0.00161854145155 | 0.00163922979277 / 0.00160489001558 | 0.775978466834 / 0.42371877442 | 0.60181371448 | False | [] | 3 |
| B0 | 1 | 0.00163464699278 / 0.00161854145155 | 0.00160489001558 / 0.00161266274881 | 1.98177619868 / 1.7379352378 | 1.86045930926 | False | [] | 4 |
| B0 | 2 | 0.00163464699278 / 0.00161854145155 | 0.00161266274881 / 0.0015982322655 | 1.98654873676 / 1.98745007011 | 1.98699717232 | False | [] | None |
| B480 | 0 | 0.00170437870787 / 0.0016965281746 | 0.00163922979277 / 0.00160489001558 | 0.781476849085 / 0.449590245051 | 0.615916604722 | False | [] | 3 |
| B480 | 1 | 0.00170437870787 / 0.0016965281746 | 0.00160489001558 / 0.00161266274881 | 1.90298709245 / 1.67584848848 | 1.78967994983 | False | [] | 4 |
| B480 | 2 | 0.00170437870787 / 0.0016965281746 | 0.00161266274881 / 0.0015982322655 | 1.92590592077 / 1.92520618174 | 1.92555685888 | False | [] | None |

Die Frame-L1-Werte sind separat normierte Diagnosegrößen. Die produktive Schranke gilt ausschließlich für Paar-L1; keine zusätzliche Frame-Schwelle. Nenner, unnormierte Frame-MAE und additive Framebeiträge sind vollständig in distances.json enthalten.
A0 verwendet Exaktpriorität; seine hier daneben berechneten Näherungsdistanzen wurden im ursprünglichen Abruf nicht benötigt. A480/B0/B480 haben null zulässige Näherungsoffsets; daher keine Mehrdeutigkeit und ABSTAIN_NO_APPROX_CONTEXT.
Offset0 hätte Original3 als Nachfolger, Offset1 Original4; Offset2 hat keinen Nachfolger. Da A480 schon die Distanzprüfung verfehlt, erklärt die Nachfolgerprüfung seine Enthaltung nicht.

## Offset0 nach Kanälen

Jeder Beitrag ist |Hinweis−Original|/(96×Paarnenner). Aufgeführt sind die acht größten Kanalbeiträge über beide Hinweise; die vollständigen96 Beiträge pro Fall liegen in channel-contributions.json. Kanalindizes sind nullbasiert.

| Fall | Kanal | Träger | Beitrag | Anteil am Paarabstand |
|---|---:|---|---:|---:|
| A0 | 0 | auditory.log_hz.50.000000 | 0 | 0.000000% |
| A0 | 1 | auditory.log_hz.56.670810 | 0 | 0.000000% |
| A0 | 2 | auditory.log_hz.64.231614 | 0 | 0.000000% |
| A0 | 3 | auditory.log_hz.72.801152 | 0 | 0.000000% |
| A0 | 4 | auditory.log_hz.82.514004 | 0 | 0.000000% |
| A0 | 5 | auditory.log_hz.93.522709 | 0 | 0.000000% |
| A0 | 6 | auditory.log_hz.106.000153 | 0 | 0.000000% |
| A0 | 7 | auditory.log_hz.120.142291 | 0 | 0.000000% |
| A480 | 29 | auditory.log_hz.1889.135185 | 0.0039843258359 | 11.078505% |
| A480 | 26 | auditory.log_hz.1297.462433 | 0.00334643699723 | 9.304841% |
| A480 | 25 | auditory.log_hz.1144.736095 | 0.00302785373903 | 8.419013% |
| A480 | 21 | auditory.log_hz.693.661702 | 0.00290332962697 | 8.072771% |
| A480 | 24 | auditory.log_hz.1009.987415 | 0.00211243193207 | 5.873663% |
| A480 | 23 | auditory.log_hz.891.100213 | 0.00180556848146 | 5.020423% |
| A480 | 28 | auditory.log_hz.1666.762120 | 0.00165645770271 | 4.605817% |
| A480 | 22 | auditory.log_hz.786.207409 | 0.00149525652168 | 4.157593% |
| B0 | 20 | auditory.log_hz.612.009696 | 0.101149605358 | 16.807461% |
| B0 | 19 | auditory.log_hz.539.969075 | 0.0989441270921 | 16.440989% |
| B0 | 16 | auditory.log_hz.370.852015 | 0.0953094193229 | 15.837030% |
| B0 | 17 | auditory.log_hz.420.329681 | 0.0936456475182 | 15.560571% |
| B0 | 22 | auditory.log_hz.786.207409 | 0.0526893546848 | 8.755094% |
| B0 | 21 | auditory.log_hz.693.661702 | 0.0522627257475 | 8.684203% |
| B0 | 25 | auditory.log_hz.1144.736095 | 0.0513646409235 | 8.534973% |
| B0 | 24 | auditory.log_hz.1009.987415 | 0.0510457210177 | 8.481980% |
| B480 | 20 | auditory.log_hz.612.009696 | 0.0978830354557 | 15.892255% |
| B480 | 19 | auditory.log_hz.539.969075 | 0.0953431132635 | 15.479874% |
| B480 | 16 | auditory.log_hz.370.852015 | 0.0914619843628 | 14.849735% |
| B480 | 17 | auditory.log_hz.420.329681 | 0.0900000723273 | 14.612380% |
| B480 | 21 | auditory.log_hz.693.661702 | 0.0529618424648 | 8.598866% |
| B480 | 25 | auditory.log_hz.1144.736095 | 0.0521987285576 | 8.474967% |
| B480 | 22 | auditory.log_hz.786.207409 | 0.0521842522255 | 8.472617% |
| B480 | 24 | auditory.log_hz.1009.987415 | 0.0503564128005 | 8.175849% |

Für A480 tragen insbesondere folgende Änderungen bei (größte einzelne Frame/Kanal-Beiträge):

| Hinweis | Kanal | NJ Original → Hinweis | Rohwert Original → Hinweis | Beitrag |
|---:|---:|---|---|---:|
| 1 | 29 | 5.55231175823e-09 → 0.000614514325015 | 1.11046235165e-08 → 0.00122902865003 | 0.00380561605659 |
| 0 | 25 | 8.06835491768e-09 → 0.000484700667737 | 1.61367098354e-08 → 0.000969401335474 | 0.00300167226353 |
| 0 | 21 | 1.45358770338e-07 → 0.000467431304759 | 2.90717540676e-07 → 0.000934862609518 | 0.0028938739007 |
| 1 | 26 | 1.0784939263e-07 → 0.000377257312535 | 2.1569878526e-07 → 0.000754514625069 | 0.00233566405627 |
| 0 | 24 | 1.28499773573e-08 → 0.000338527734777 | 2.56999547146e-08 → 0.000677055469554 | 0.00209640242453 |
| 0 | 22 | 4.55130963994e-08 → 0.000240401473835 | 9.10261927989e-08 → 0.000480802947669 | 0.00148851008173 |
| 1 | 28 | 1.0042025912e-08 → 0.000224525117638 | 2.0084051824e-08 → 0.000449050235277 | 0.00139040842808 |
| 0 | 14 | 1.45849977275e-07 → 0.000180014546905 | 2.9169995455e-07 → 0.000360029093809 | 0.00111391607657 |
| 1 | 30 | 3.40627326602e-09 → 0.000177154086229 | 6.81254653203e-09 → 0.000354308172458 | 0.00109708356011 |
| 1 | 20 | 1.24207458348e-07 → 0.00017711463902 | 2.48414916696e-07 → 0.00035422927804 | 0.00109609115139 |

Die Rohrezeptorvektoren waren nicht separat gespeichert. Sie wurden ausschließlich durch inverse Zweierskalierung aus den archivierten NJ-Werten rekonstruiert; jeder rekonstruierte Vektor stimmt mit dem archivierten source_values_digest überein. Keine Rezeptor- oder NJ-Funktion wurde ausgeführt.
Die NJ-Halbierung verändert die hier betrachtete relative L1 nicht: Zähler und Nenner skalieren gleich. Die festgestellten Kanalverschiebungen stammen bereits aus den gebundenen Rezeptorwerten; daraus folgt keine isolierte physikalische Ursachenbestimmung.

## Fensterzusammensetzung und Aussagegrenze

A480-Hinweis0 umfasst4320 Samples aus Abschnitt0 (380Hz plus1,5-fache Komponente) und480 Samples aus Abschnitt1 (740Hz); Hinweis1 entsprechend4320 Samples aus Abschnitt1 und480 aus Abschnitt2 (1260Hz). A0 umfasst jeweils einen vollständigen4800-Sample-Abschnitt. B verwendet die festgelegten400/760/2140/2380Hz mit denselben Schnittregeln.
Nach unverändertem Rezeptorcode werden4800 Samples mit symmetrischem Hann gewichtet, FFT-Beträge gebildet und48 überlappende logarithmische Bänder quadratisch reduziert. Verschobener Abschnittsinhalt, Phase und Fenstergewichtung wirken gemeinsam. Die Archivdiagnose isoliert diese Einflüsse nicht; die10%-Beimischung ist keine10%-Energieaussage.
Der bestehende Abruf verlangt komponentennahe Zwei-Frame-Verläufe. Er besitzt in dieser Gegenprobe keine ausreichende Invarianz gegen den festgelegten480-Sample-Fensterversatz. Das Vierfallurteil NO_ADDITIONAL_BENEFIT bleibt unverändert. Keine alternative Schwelle berechnet oder empfohlen.

## Durchführung und Anschluss

Acht kleine künstliche Fixtures prüfen ausschließlich die neue Diagnoserechnung. Ausgewertet wurden vier archivierte Hauptentscheidungen, zwölf Offsetdistanzen,36 Exaktfaktorprüfungen und384 Kanalbeiträge. Archivierte Status-/Exaktzähler werden wiederverwendet; nicht gespeicherte Distanzen werden als neue Archivberechnungen ausgewiesen.
Null neue PCM-Daten, Rezeptor-/NJ-Aufrufe, Policy-Läufe oder Referenzwiederholungen. Historische Artefakte bleiben unverändert; die drei Übersichtsvorgänger werden verlustfrei komprimiert gesichert. Diese Diagnose hat ihre eigene Ressourcenbilanz und gehört nicht zur früheren300-Sekunden-Laufzeit.
Vorschlag: den unveränderten AS480-Zweig abschließen und fachlich entscheiden, ob zeitliche Ausrichtung vor dem Abruf als eigener konzeptioneller Ansatz sinnvoll ist. Zunächst einen falsifizierbaren Vertrag für Eigen-/Fremdverlaufstrennung formulieren; keine automatische Implementierung, Kalibration oder neue Messung.
