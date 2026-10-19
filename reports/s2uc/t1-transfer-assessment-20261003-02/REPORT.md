# T1-Transferprüfung: vollständiger Abschluss

Der neue Einmallauf am Ziel t1-transfer-20261003-02 ist COMPLETE. Alle16 Fälle,
1.280 Quellpositionen,80 Arme U/M/E/K/P,6.400 Arm-Aufnahmen und6.400 separat
bilanzierte Referenzfortschreibungen sind vollständig. Kein technischer Abbruch,
keine Fallersetzung, Reparatur, Fortsetzung oder Wiederholung. Die Einmalfreigabe
ist verbraucht. Die erste fehlgeschlagene Startausführung bleibt unverändert
separat geschlossen und NOT_EVALUABLE.

## Getrennte fachliche Urteile

| Kriterium | Ergebnis | Beleg |
| --- | --- | --- |
| Wiedererkennung | BELEGT | 11/16 Fälle, alle4 Herkunftsgruppen; Schwelle4 Fälle/2 Gruppen |
| Verfügbarkeit | Vollständig erfasst, stark begrenzt | 528/624 Ziele ohne berechtigten Kontext;7 tatsächliche Nachfolger fehlen trotz Kandidaten;9 kalt;80 warm |
| Erfahrungsabhängige Anpassung | NICHT_NACHGEWIESEN | 0/52 Übergänge; jede Gruppe0/13; gefordert26/52 und4/13 je Gruppe |
| G-Gesamtnutzen | NICHT_NACHGEWIESEN | U gleich M/E/P, geringfügig schlechter als K |
| Stabilität/Schadensgrenze | BELEGT | Festes G_w bei allen Armen gleich; größter schlechterer G-Fallabstand0,00006155274872 <1/32 |

Dies ist ein technisch vollständiger negativer Transferbefund für Anpassung
und Nutzen im festgelegten synthetischen T1-Vertrag, kein NOT_EVALUABLE wegen
fehlender Treffer. Wiedererkennung allein hat keinen nutzbaren Anpassungsvorteil
bewiesen. Keine Behauptung allgemeiner Transferunfähigkeit außerhalb dieses Vertrags.

G-Fallmittel: U/M/E/P jeweils0,05347585104979002; K0,05347200400299496.
G_w-Fallmittel bei allen fünf Armen0,030894060929616295. Das Fenster besteht
weiterhin aus den festen späten Zielen11,13,...,79 der vier S0-Fälle; seine
Gleichheit ist kein Nachweis warmer Verfügbarkeit. Alle624 G-Ziele sind vorhanden.
Die abschließende Prognose für Ziel81 ist zensiert und wird nicht gewertet.

U hat an keinem gewerteten Ziel einen Kontext gewählt. Entscheidungen:
528 NO_ELIGIBLE_CONTEXT,12 COLD_ONLY,84 NO_ESTIMATED_IMPROVEMENT.
Die Verfügbarkeitskategorien betrachten den tatsächlich realisierten Nachfolger,
die Entscheidungsgründe dagegen die gesamten Kandidaten; deshalb unterscheiden
sich9 tatsächliche kalte Nachfolger von12 Entscheidungen mit nur kalten Kandidaten.
72 der80 warm verfügbaren tatsächlichen Nachfolger stammen aus den zwei
konstanten S0-Haltefällen; diese liefern keinen geschätzten Vorteil gegenüber
Persistenz. Fünf Fälle zeigen überhaupt keinen berechtigten Kontext:
T1-0-3,T1-0-4,T1-2-1,T1-2-2,T1-2-4.

## Übergänge, Kontrollen und Schäden

Alle52 Übergänge einschließlich kurzer Phasen und leerer Zielmengen bleiben
im Nenner. Die20 negativen Kontrollen werden zusätzlich getrennt ausgewiesen:
I12 mit0 bestandenen Warmwahlkriterien; H8 mit0 bestandenen Warmwahlkriterien.
Über die tatsächlichen G-Ziele dieser Kontrollphasen: I48 Ziele, Fehlersumme
3,5978591442108154 bei jedem Arm; H32 Ziele, Fehlersumme0 bei jedem Arm.
Damit bedeutet ein gescheitertes Warmwahlkriterium gerade nicht automatisch
Vorhersagefehler oder unangemessene Enthaltung. Die Kontrollphasen-Zielzählung
enthält auch reale G-Ziele außerhalb der engeren mechanistischen Übergangsmaske.
Modale Fortsetzung und realisierte Prognosefehler bleiben getrennt gespeichert.

Gegen M/E/P gibt es kein schlechteres Ziel und keinen schlechteren Fallmittelwert.
Gegen K gibt es genau ein schlechteres Ziel: T1-1-3,Ziel7,
U-Fehler0,08912928899129231 gegenüber K0,08672873179117839;
Differenz0,002400557200113923. Der zugehörige G-Fallmittelabstand beträgt
0,00006155274872086627. Das liegt unter1/32, ist aber keine Schadensfreiheit.
Alle Zielvergleiche und Übergangsdetails bleiben in den ursprünglichen
Fallberichten und assessment.json des Laufordners erhalten.

## Herkunft, Bindung und Nachprüfung

Alle16 Quellen, Herkunftsdaten und Masken wurden vor dem ersten Policyaufruf
im Manifest versiegelt. Alle80 Startbelege verweisen auf denselben Manifesthash.
Der erneute reine Datei-/Hashabgleich bestätigt Quellen und Provenienz.
Keine vollständige Quellenüberschneidung und keine gemeinsamen Einzelvektoren,
Paare oder Viererfenster mit dem gebundenen Herkunftsindex einschließlich neutralem
Ergänzungsindex. Diese Aussage gilt für den dokumentierten Archivsuchumfang,
nicht für alle denkbaren externen Versuche oder eine unabhängige Population.

Die operative Datei entstand durch ausschließlich status=AUTHORIZED_ONCE aus der
START-V3-Vorlage. Verwendet wurde direkt:
C:/Python314/python.exe -m tools.s2uc_t1_start_v3 run --authorization docs/S2UC_T1_START_V3_AUTORISIERUNG_20261003.json
Kein zusätzlicher Wrapper, keine neuen Claimfelder, keine Vorbereitungs- oder
Qualifikationswiederholung. Claim155 Byte. Policy, Defaults und Kriterien unverändert.

Nach Abschluss wurden die16 Fallauswertungen und die Gesamtaggregation aus den
gespeicherten Quellen und Armbelegen erneut berechnet und mit den gespeicherten
JSON-Ergebnissen abgeglichen. Python-Tupel wurden dabei ausschließlich für den
Vergleich in ihre JSON-Listendarstellung normalisiert. Keine Policy-Replays und
keine Änderung an Quelldaten oder Ergebnisdateien. Alle80 Ressourcen-/Cleanup-
Belege bestanden den Abgleich. Bindungen und erster Fehlversuch blieben unverändert.

## Ressourcen und Zeit

Maximaler Zusatzheap: U6.033,M4.364,E2.457,K1.498,P1.498 Byte,
jeweils unter16.384. Gepackter Bestand416/416 Byte. Die detaillierten80
Ressourcenbelege stehen in facts.json. U verwendet seine geprüften Obergrenzen;
mit0 gespeicherte Trace-Peaks bedeuten keine Messung von null Speicherverbrauch.
Baseline-Zusatzheap umfasst die isolierte Aufnahme ohne Beobachtertrace.
Diese Messungen sind keine Gesamtprozess-RAM-Messung.

Worker beendet mit Exit0, worker_alive=false. Supervisorabschluss bis unmittelbar
vor seinem eigenen Schreibvorgang535,9044721s, deutlich unter3.600s; der CLI-Aufruf
endete erfolgreich. Reine Engine533,8120842s, Quellenverarbeitung4,5681957s,
Fallauswertung8,7682847s und Armexport0,2642997s. Die Kategorien sind Teile der
Engine, nicht zusätzlich zu ihr zu summieren. Die vorausgeplanten2.066,196404s
waren eine Hochrechnung; hier liegen tatsächliche Laufmessungen vor.
Der vollständige externe Abschlusszeitpunkt ist separat in closure.json erfasst.

Laufdateien7.263.101 Byte. Vorbelastung einschließlich Autorisierung und reserviertem
externem Bericht7.190.465 Byte. Konservative Gesamtbilanz inklusive dieser
Berichtsreserve14.453.566/67.108.864 Byte. Die frühere administrative Übergabe
und dieses neue Abschlussdossier teilen sich die vorab reservierten524.288 Byte;
ihre tatsächliche Summe und die bereinigte Gesamtbilanz stehen in closure.json.
Alle Datei- und Systemgrenzen eingehalten;1MiB Laufabschlussreserve war vorgesehen.

## Begründete Anschlussentscheidung

Empfehlung an den Projektleiter: T1 als vollständig ausgewerteten Gegenbefund
für den beanspruchten Anpassungs- und Nutzenübertrag abschließen. Keine
Policyfreigabe oder Generalisierungsbehauptung daraus ableiten; Defaults bleiben aus.

Als nächster begrenzter Forschungsschritt eignet sich eine ausschließlich lesende
Ursachenanalyse der bereits gespeicherten Belege: für die32 nichtnegativen
Übergänge die Kette Matchverfügbarkeit → lebender Schlüssel → vorzielliches
Feedback → strikter Vorteil gegenüber Persistenz aufschlüsseln. So lässt sich
trennen, ob die begrenzte exakte Wiederkehr, die Bestandsdauer oder die fehlende
Fehlerdifferenz den Mechanismus verhindert. Die vorhandene Bilanz legt vor allem
fehlende Verfügbarkeit und fehlenden geschätzten Vorteil nahe; sie beweist keine
isolierte Ursache. Erst aus dieser Analyse wäre eine neue falsifizierbare
Forschungsfrage abzuleiten. Kein erneutes T1-Tuning und keine nachträglichen
Schwellen- oder Quellenänderungen. Dieser Vorschlag ist kein neuer Versuchsstart.

Aussagegrenze: synthetischer Transfer ab der48-Vektor-Grenze. Kein Audio-/Video-
Kettentransfer und keine allgemeine Invarianz. Alter Raster32-Lauf bleibt separat
NOT_EVALUABLE; bekannte technische Wiederholungsbefunde bleiben historisch getrennt.
