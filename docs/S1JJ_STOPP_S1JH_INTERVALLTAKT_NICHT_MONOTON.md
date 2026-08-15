# S1-JJ: STOPP wegen nicht monotonem S1-JH-Intervalltakt

## Ergebnis

S1-JJ stoppt vor dem korrigierten Materialisierungsschemavertrag. Der in
S1-JH fuer alle 23 Hüllen wiederholte Zeitwert `0..1` bei `2 ticks/s` ist mit
einem innerhalb einer Sequenz getragenen `SharedMCMField` nicht vereinbar.

## Bestehende Zeitinvariante

Nach einem abgeschlossenen Feldintervall traegt `SharedMCMField` die letzte
`ReceptorDistribution`. Die bestehenden Zwei- und Dreiknotengrenzoperatoren
ersetzen nur S/H und erhalten diese Distribution als identisches Objekt.

Fuer das folgende Intervall verlangt der Feldkern:

- denselben gemeinsamen Feldtakt,
- einen strikt groesseren `window_end_tick`,
- exakte Uebereinstimmung von `MCMFieldStepTime` und Distributionsfenster.

Nach dem ersten S1-JH-Intervall endet das getragene Feld bei Tick 1. Das
zweite Intervall bietet erneut `0..1`; sein Endtick ist nicht groesser als 1.
Der Feldkern bricht daher vor einer gueltigen zweiten Transition ab. Ein
S/H-Grenzreset darf diese Zeithistorie nicht entfernen oder umschreiben.

## Betroffener Umfang

Alle sieben Sequenzen besitzen mindestens zwei Intervalle. Von 23 Hüllen pro
Modell und Refinement sind 16 Folgehuellen mit dem getragenen Feldtakt
unvereinbar:

- P_IE: je ein Folgeintervall in F_HIGH und R_HIGH,
- P_IH: zwei Folgeintervalle,
- P_IK: je drei Folgeintervalle in beiden Sequenzen,
- P_IN: je drei Folgeintervalle in beiden Sequenzen.

Alle 24 Baseline-Rollen-Block-Faelle bleiben blockiert.

## Erhaltene und zu ersetzende Bindungen

Erhalten bleiben Geometrien, Knotenordnungen, alle S/H-Werte,
geometriebreiten Nullkontakte, Kontaktidentitaeten, Kandidatensidecars,
Refinements, Budgets, Quarantaeneregeln und die gemeinsame
Informationsgrenze.

Zu ersetzen sind nur der wiederholte S1-JH-Zeitwert, alle davon abhaengigen
Sequenz- und Intervalldigests sowie die Aussage, dieser Zeitplan sei bereits
materialisierbar.

## Korrekturgrenze

Eine korrigierte Sequenz verwendet bei `2 ticks/s` ordinalabhaengig die
zusammenhaengenden Fenster `0..1`, `1..2`, `2..3` und bei vier Intervallen
zusaetzlich `3..4`. Nur beim Start einer neuen unabhaengigen Sequenz mit neuem
Modellzustand beginnt der relative Takt erneut bei 0. DTS-1 und B1 bis B6
erhalten fuer dasselbe Ordinal dasselbe Fenster; ein separates Ordinallabel
bleibt ausgeschlossen.

## Entscheidung

`STOPP_S1JH_REPEATED_INTERVAL_CLOCK_INCOMPATIBLE_WITH_CARRIED_FIELD_TIME`

Kanonischer Auditdigest:

`8436374fc2d4674d425b3441d23ca2fe5f2ec470037c797ceaffca59da10b603`

Es wurde kein Hüllen-, Adapter- oder Modellcode implementiert und kein
Feldschritt ausgefuehrt. Der STOPP ist kein Funktionsbefund. Baselinepassung,
Kandidatenueberlegenheit sowie Speicher-, Lern- und KI-Claims bleiben
gesperrt.

## Naechster zulaessiger Schritt

S1-JK darf ausschliesslich einen korrigierten endlichen monotonen
Intervalltaktvertrag binden und alle zeitabhaengigen Sequenz- und
Intervalldigests neu registrieren. Noch keine Materialisierung, kein Adapter-
oder Modellaufruf, keine Runtime und keine Forschungsprobe.
