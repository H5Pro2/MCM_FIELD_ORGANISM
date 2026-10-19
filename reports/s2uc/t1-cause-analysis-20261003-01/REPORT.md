# T1-Ursachenanalyse aus gespeicherten Belegen

Alle32 Übergänge außerhalb der I/H-Negativkontrollen sind als **potenziell
prüfbare Übergänge** untersucht. Ihr Erfolg wird nicht vorausgesetzt. Sie enthalten
324 vertragliche Prüfziele; die übrigen T1-Ziele bleiben außerhalb dieses primären
Diagnosenenners. Keine neuen Quellen, Policy-Replays, Parameter- oder Architektur-
änderungen. T1 ist abgeschlossen und jetzt bekanntes Entwicklungsmaterial.

## Vorrangiges Hindernis: verfügbare Originalspuren vor der Fehlerauswahl

Die Kette bricht überwiegend vor einer möglichen erfahrungsabhängigen Auswahl.
201/324 Ziele besitzen einen früheren exakten Zweierhinweis im bereits aufgenommenen
Verlauf. Nur3/324 besitzen einen entsprechenden Treffer im damals lebenden Bestand,
nur2 einen berechtigten Nachfolger. Beide Schlüssel sind kalt, ohne vorzielliches
Feedback. Kein Prüfziel besitzt einen lebenden modalen Nachfolger. Ein strikter
geschätzter Vorteil kann deshalb in diesem Teilkorpus nicht zur Auswahl führen.

| Erste beobachtete Unterbrechung | Ziele |
| --- | ---: |
| Kein früheres exaktes Paar, auch nicht überlappend mit aktuellem Hinweis | 110 |
| Früheres Paar nur überlappend mit aktuellem Hinweis, noch nicht vollständig aufgenommen | 13 |
| Früheres aufgenommenes Paar vorhanden, aber kein lebender Match | 198 |
| Lebender Match, aber Nachfolger außerhalb der Originalspur | 1 |
| Berechtigter Nachfolger, aber kein vorzielliches Feedback | 2 |
| Summe | 324 |

Diese erste Unterbrechung dient der vollständigen Zuordnung. Sie ist keine
isolierte Ursachenbehauptung. Weitere gleichzeitig vorhandene Hindernisse stehen
je Ziel und je historischem Vorkommen in targets.json und target-map.csv.

Bei135 Zielen war früher bereits eine segmentintern vollständige Originalspur
mit passendem Hinweis und berechtigtem Nachfolger entstanden. Bei133 davon zeigen
die gespeicherten Vor-/Nachbestände die spätere Kandidatenersetzung vor dem jetzigen
Abruf; bei2 lebt die Spur noch. Bei108 der133 Ziele stimmt der damals gespeicherte
Nachfolger zudem mit dem jetzt modalen Nachfolger überein. Das ist ein konkreter
Nachweis eines Verlusts durch Bestandswechsel, nicht bloß fehlender Wiederkehr.
Die historischen Spuren sind jedoch keine damals verfügbaren Systemhypothesen.
Auch ein historisch modaler Nachfolger garantiert weder warmes Feedback noch Nutzen.

## Segmentierung, Ersetzung, Promotion und Verdrängung getrennt

Überlappende Diagnosemerkmale auf Zielebene: Kandidatenersetzung bei177 Zielen
für mindestens ein passendes historisches Vorkommen; Paar über Segmentgrenze bei80;
Nachfolger außerhalb der Viererspur/Offset2 bei86; noch nicht abgeschlossene
Segmentbildung bei7; frühere, aber mit aktuellem Hinweis überlappende Paare bei17.
Diese Zahlen dürfen nicht addiert werden.177 umfasst auch Vorkommen ohne
segmentinternen Nachfolger; die engere Zahl133 verlangt eine wirklich früher
gebildete berechtigte Originalspur. Mehrere Vorkommen eines Ziels können an
unterschiedlichen Grenzen scheitern.

In den vollständigen Bestandsprotokollen der12 betroffenen Fälle sind216
Kandidatenersetzungen und4 Promotionen sichtbar. Das sind Ereigniszahlen über
die ganzen Fälle, nicht324 unabhängige Ursachen. Bei den4 Promotionen bleiben
die Originalordinalen erhalten und der Schlüssel wechselt von candidate zu retained.
Sie liegen in H-Phasen. Beispiel T1-3-1: Original9–12 wird bei Aufnahme16 promoviert;
der Prognoseschlüssel für Ziel17 ist danach nicht mehr lebend, die promovierte
Originalspur bleibt für Ziel19 vorhanden. Dies ist keine Vernichtung der Spur.
Keine Verdrängung einer bestätigten Spur ist in diesen12 Fallprotokollen belegt.
In den beiden berechtigten Hypothesen der324 Prüfziele findet zwischen Prognose
und Feedback weder Promotion noch Verlust statt. Promotion ist damit für diese
primären Abrufausfälle nicht als erste Verluststelle belegt.

## Zeitgrenze, Modalität und Lerngelegenheiten

Für Ziel t stammt der Hinweis aus t−2,t−1. Der für diese Prognose abgefragte
Bestand liegt vor deren Aufnahme und enthält höchstens die Positionen bis t−3.
Der aktuelle Hinweis selbst zählt nie als historische Wiederkehr. Frühere
überlappende Paare werden separat ausgewiesen und nicht als aufgenommene Hypothesen
behandelt. Historische Nachfolger werden nur bei Position<=t−3 als bereits
aufgenommen beurteilt. Ein Match benötigt den Nachfolger innerhalb seiner
Originalviererspur; Offset2 liefert ihn nicht, selbst wenn spätere Rohdaten
außerhalb dieser Spur existieren.

Bei72/324 Prüfzielen unterscheiden sich modaler Nachfolger und realisiertes Ziel.
165 Ziele besitzen irgendein früheres aufgenommenes Rohdaten-Dreierstück mit
passendem modalem Nachfolger; nur108 besitzen dafür eine segmentintern vollständige,
früher tatsächlich gespeicherte Originalspur, und diese ist jeweils ersetzt.
Keine dieser historischen Möglichkeiten wird als aktuelle Policyhypothese gewertet.

Vier kurze R-Phasen, T1-2-1 bis T1-2-4, jeweils Phase3/Position41–44, enthalten
nur Prüfziel43. Es gibt damit keine Folge aus zwei vollständig in dieser Phase
liegenden Hinweis-Prüfzielen zum erstmaligen Lernen und anschließenden Nutzen.
Es gab allerdings bereits G-Feedbackziel41 aus einem Hinweis der vorherigen Phase.
Der Vertrag erlaubt solches Feedback zeitlich; daher wird keine absolute
Lernunmöglichkeit allein aus der Phasenlänge behauptet. Tatsächlich besitzt Ziel43
in keinem der vier Fälle einen lebenden Match; in Replikat1/3 fehlt frühere
aufgenommene Wiederkehr, in2/4 besteht historisches Vorkommen ohne lebenden Match.
Frühere G- und engere T-Ziele sind je Prüfziel separat dokumentiert.

Die beiden berechtigten Schlüssel haben keinerlei früheres Feedback, auch nicht
aus einer vorherigen Phase. Bei keinem der324 Prüfziele liegt eine warme berechtigte
Hypothese vor. Dies grenzt den aktuellen Engpass vor der Fehlergewichtung ein;
es testet nicht, ob eine andere Fehlergewichtung bei ausreichender Verfügbarkeit
hilfreich wäre. Keine alternative Policy wurde berechnet.

## Nachvollziehbare Beispiele

1. **T1-1-1/Ziel19:** Hinweis17–18 wiederholt Original5–6. Die Spur5–8 entstand
   bei Aufnahme8; ihr Nachfolger7 entspricht der modalen Fortsetzung für19.
   Aufnahme12 ersetzte Kandidatengeneration2. Beim Abruf steht nur Kandidat13–16
   zur Verfügung. Das realisierte Ziel19 weicht zugleich vom Modalwert ab.
   Belege: Quelle; M.admissions[8,12,17]; U.forecasts[input_indices=17,18].
2. **T1-1-2/Ziel19:** Historischer Hinweis4–5 mit Nachfolger6 passt sogar zu Modalwert
   und realisiertem Ziel. Das Paar liegt jedoch über der Grenze1–4/5–8 und war
   nie innerhalb einer solchen Originalspur abrufbar. Die Entfernung der Spur1–4
   allein erklärt hier nicht das Scheitern; die Segmentgrenze besteht bereits davor.
3. **T1-2-3/Ziel55:** Kandidat49–52 ist lebend; Hinweis53–54 trifft Original51–52
   an Offset2. In der Spur existiert kein Nachfolger. Rohdatenposition53 außerhalb
   der Spur darf nicht nachträglich als Systemhypothese ergänzt werden.
4. **T1-2-3/Ziel27:** Kandidat21–24 liefert für Hinweis25–26 den berechtigten
   Nachfolger24. Er entspricht dem realisierten Ziel27, aber nicht der modalen
   Fortsetzung. Schlüssel[1,6,1] ist kalt; Feedback27 ergibt ec=ep=0. Auch richtige
   Nachfolgeridentität bedeutet hier keinen geschätzten Vorteil gegenüber Persistenz.
5. **T1-1-3/Ziel7:** Kandidat1–4 liefert Schlüssel[1,1,0], aber ohne vorheriges
   Feedback und mit einem nichtmodalen Nachfolger. Erst Feedback7 ergibt ec<ep.
   Die Originalspur wird bei Aufnahme8 ersetzt. Der neu entstandene günstige
   Fehlerwert war deshalb weder bei Ziel7 vorziellich verfügbar noch später unter
   diesem Schlüssel erhalten. Belege: U.updates[target=7], M.admissions[frame=8].

## Belegabdeckung und Grenzen

324 eindeutige Fall-/Phasen-/Zielzuordnungen,32 Übergänge vollständig. Die
historischen Rohdatenpaare wurden unabhängig nochmals aufgezählt; lebende Matches
und Berechtigung stimmen mit den gespeicherten U-Belegen überein. Der M-Bestand
wird nur verwendet, weil die gespeicherten U/M-Zustandshashes übereinstimmen.
D01–D06 in verification.json sind reine Konsistenzprüfungen der Diagnose.
Die versiegelten Laufdateien und der frühere Fehlversuch bleiben bytegleich.

Für die angeforderten Ziel-/Bestands-/Feedbackdaten fehlen keine Pflichtbelege.
Nicht als eigenständiges Ereignislabel gespeichert sind die damaligen Aktionen
„Kandidatenersetzung“ und „Promotion“: diese Bezeichnungen werden nachvollziehbar
anhand der Vor-/Nachbestände und unveränderten Originalordinalen rekonstruiert.
Das vollständige Verhalten einer alternativen Speicherorganisation, deren Budget,
Feedbackverlauf oder Vorhersagen ist nicht belegt. Auch die erreichbare Qualität
unter anderer Segmentierung wird aus historischen Rohdaten nicht als Ergebnis
behauptet. Häufigkeiten allein isolieren keine Ursache.

Die Priorität liegt deshalb auf der Lebensdauer berechtigter Kandidatenspuren
bis zu ihrer Wiederkehr, bei zugleich sichtbaren Segmentierungs- und
Wiederkehrgrenzen. Diese Priorisierung stützt sich auf die133 dokumentierten
Entfernungen vorher wirklich gebildeter Spuren, nicht nur auf fehlende Matches.
Eine erfolgreiche Architekturänderung oder spätere Anpassung folgt daraus nicht.

## Genau eine neue falsifizierbare Forschungsfrage

Erhöht eine budgetneutrale längere Erhaltung bereits gebildeter Kandidatenspuren gegenüber der bisherigen Ersetzung den Anteil potenziell prüfbarer Ziele mit einem lebenden modalen Nachfolger und vorziellichem Feedback, wenn Segmentierung, Abruf und Auswahlregel unverändert bleiben?

Die prüfbare Erwartung wäre ein höherer Anteil solcher Ziele als unter der
bisherigen Ersetzung, unter demselben vorab festgelegten Ressourcenrahmen.
Kein Anstieg würde diese Erwartung im jeweiligen Vergleich widerlegen.
Dies ist ausschließlich die nächste Forschungsfrage: kein Implementierungsauftrag,
kein festgelegtes neues Speicherverfahren und keine neue Versuchsfreigabe.
Ein künftiger Vergleich müsste vorab festgelegt werden. T1 darf dabei höchstens
als bekanntes Entwicklungsmaterial dienen; nach einer Änderung wäre für einen
unberührten Transfernachweis neues getrenntes Material erforderlich.

## Vollständige Übergangszuordnung

Die maschinenlesbare Zuordnung aller324 Ziele steht in target-map.csv und targets.json;
letztere enthält jede historische Fundstelle, lebenden Bestand, Schlüssel,
Feedbackkette, gleichzeitig bestehende Hindernisse und konkrete Quelldateireferenzen.
NO_PRIOR_ADMITTED_EXACT_PAIR umfasst110 echte Nichtwiederkehrziele plus13 Ziele
mit ausschließlich noch nicht aufgenommenen Überlappungen.

| Fall | Phase | Positionen | Prüfziele | Erste Unterbrechungen |
| --- | ---: | --- | --- | --- |
| T1-1-1 | 1 | 4–20 | 7,9,11,13,15,17,19 | NO_PRIOR_ADMITTED_EXACT_PAIR:5, NO_LIVE_MATCH:2 |
| T1-1-1 | 3 | 23–45 | 25,27,29,31,33,35,37,39,41,43,45 | NO_PRIOR_ADMITTED_EXACT_PAIR:6, NO_LIVE_MATCH:5 |
| T1-1-1 | 5 | 51–80 | 53,55,57,59,61,63,65,67,69,71,73,75,77,79 | NO_LIVE_MATCH:13, NO_PRIOR_ADMITTED_EXACT_PAIR:1 |
| T1-1-2 | 1 | 4–20 | 7,9,11,13,15,17,19 | NO_PRIOR_ADMITTED_EXACT_PAIR:5, NO_LIVE_MATCH:2 |
| T1-1-2 | 3 | 23–45 | 25,27,29,31,33,35,37,39,41,43,45 | NO_PRIOR_ADMITTED_EXACT_PAIR:5, NO_LIVE_MATCH:6 |
| T1-1-2 | 5 | 51–80 | 53,55,57,59,61,63,65,67,69,71,73,75,77,79 | NO_LIVE_MATCH:13, NO_PRIOR_ADMITTED_EXACT_PAIR:1 |
| T1-1-3 | 1 | 4–20 | 7,9,11,13,15,17,19 | NO_PRIOR_FEEDBACK:1, NO_PRIOR_ADMITTED_EXACT_PAIR:4, NO_LIVE_MATCH:2 |
| T1-1-3 | 3 | 23–45 | 25,27,29,31,33,35,37,39,41,43,45 | NO_PRIOR_ADMITTED_EXACT_PAIR:7, NO_LIVE_MATCH:4 |
| T1-1-3 | 5 | 51–80 | 53,55,57,59,61,63,65,67,69,71,73,75,77,79 | NO_LIVE_MATCH:12, NO_PRIOR_ADMITTED_EXACT_PAIR:2 |
| T1-1-4 | 1 | 4–20 | 7,9,11,13,15,17,19 | NO_PRIOR_ADMITTED_EXACT_PAIR:5, NO_LIVE_MATCH:2 |
| T1-1-4 | 3 | 23–45 | 25,27,29,31,33,35,37,39,41,43,45 | NO_PRIOR_ADMITTED_EXACT_PAIR:6, NO_LIVE_MATCH:5 |
| T1-1-4 | 5 | 51–80 | 53,55,57,59,61,63,65,67,69,71,73,75,77,79 | NO_LIVE_MATCH:12, NO_PRIOR_ADMITTED_EXACT_PAIR:2 |
| T1-2-1 | 2 | 12–40 | 15,17,19,21,23,25,27,29,31,33,35,37,39 | NO_PRIOR_ADMITTED_EXACT_PAIR:5, NO_LIVE_MATCH:8 |
| T1-2-1 | 3 | 41–44 | 43 | NO_PRIOR_ADMITTED_EXACT_PAIR:1 |
| T1-2-1 | 4 | 45–80 | 47,49,51,53,55,57,59,61,63,65,67,69,71,73,75,77,79 | NO_PRIOR_ADMITTED_EXACT_PAIR:9, NO_LIVE_MATCH:8 |
| T1-2-2 | 2 | 12–40 | 15,17,19,21,23,25,27,29,31,33,35,37,39 | NO_PRIOR_ADMITTED_EXACT_PAIR:5, NO_LIVE_MATCH:8 |
| T1-2-2 | 3 | 41–44 | 43 | NO_LIVE_MATCH:1 |
| T1-2-2 | 4 | 45–80 | 47,49,51,53,55,57,59,61,63,65,67,69,71,73,75,77,79 | NO_PRIOR_ADMITTED_EXACT_PAIR:5, NO_LIVE_MATCH:12 |
| T1-2-3 | 2 | 12–40 | 15,17,19,21,23,25,27,29,31,33,35,37,39 | NO_PRIOR_ADMITTED_EXACT_PAIR:8, NO_LIVE_MATCH:4, NO_PRIOR_FEEDBACK:1 |
| T1-2-3 | 3 | 41–44 | 43 | NO_PRIOR_ADMITTED_EXACT_PAIR:1 |
| T1-2-3 | 4 | 45–80 | 47,49,51,53,55,57,59,61,63,65,67,69,71,73,75,77,79 | NO_PRIOR_ADMITTED_EXACT_PAIR:6, NO_ELIGIBLE_SUCCESSOR:1, NO_LIVE_MATCH:10 |
| T1-2-4 | 2 | 12–40 | 15,17,19,21,23,25,27,29,31,33,35,37,39 | NO_PRIOR_ADMITTED_EXACT_PAIR:5, NO_LIVE_MATCH:8 |
| T1-2-4 | 3 | 41–44 | 43 | NO_LIVE_MATCH:1 |
| T1-2-4 | 4 | 45–80 | 47,49,51,53,55,57,59,61,63,65,67,69,71,73,75,77,79 | NO_PRIOR_ADMITTED_EXACT_PAIR:8, NO_LIVE_MATCH:9 |
| T1-3-1 | 2 | 21–26 | 23,25 | NO_PRIOR_ADMITTED_EXACT_PAIR:2 |
| T1-3-1 | 4 | 46–80 | 49,51,53,55,57,59,61,63,65,67,69,71,73,75,77,79 | NO_PRIOR_ADMITTED_EXACT_PAIR:5, NO_LIVE_MATCH:11 |
| T1-3-2 | 2 | 21–26 | 23,25 | NO_PRIOR_ADMITTED_EXACT_PAIR:2 |
| T1-3-2 | 4 | 46–80 | 49,51,53,55,57,59,61,63,65,67,69,71,73,75,77,79 | NO_LIVE_MATCH:14, NO_PRIOR_ADMITTED_EXACT_PAIR:2 |
| T1-3-3 | 2 | 21–26 | 23,25 | NO_PRIOR_ADMITTED_EXACT_PAIR:2 |
| T1-3-3 | 4 | 46–80 | 49,51,53,55,57,59,61,63,65,67,69,71,73,75,77,79 | NO_LIVE_MATCH:13, NO_PRIOR_ADMITTED_EXACT_PAIR:3 |
| T1-3-4 | 2 | 21–26 | 23,25 | NO_PRIOR_ADMITTED_EXACT_PAIR:2 |
| T1-3-4 | 4 | 46–80 | 49,51,53,55,57,59,61,63,65,67,69,71,73,75,77,79 | NO_PRIOR_ADMITTED_EXACT_PAIR:3, NO_LIVE_MATCH:13 |
