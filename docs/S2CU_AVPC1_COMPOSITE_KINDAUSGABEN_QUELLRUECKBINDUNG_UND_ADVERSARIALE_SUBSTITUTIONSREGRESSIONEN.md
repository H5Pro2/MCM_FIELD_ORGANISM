# S2-CU: Composite-Quellrueckbindung und Substitutionsregressionen

## Korrektur

S2-CU schliesst ausschliesslich die drei in S2-CT gefundenen
Quellenrueckbindungsblocker des privaten AVPC-1-End-to-End-Evaluators.

Das Formationsergebnis muss jetzt Consumption-ID, beide autorisierten
Frischzustandsdigests sowie Owner-, Authorization- und Consumption-ID des
vollstaendig verbrauchten Formation-Owners zurueckbinden.

Jeder Relationsbildungsbefund muss jetzt Formation, Bildungsumschlag,
spaeteren Expositionsumschlag, Profil, Relationspartition, beide exakten
Frameprovenienzen, Relationsvorzustandsidentitaet und -digest sowie alle
Owner-, Probe-, Expositions- und Transitions-IDs des konkreten Schritts
zurueckbinden.

Jeder atomare Abrufbefund muss jetzt Consumer-ID, Audio-only-Umschlag,
auditiven Finding-Digest, Relationsidentitaet und -zustand, Profil,
visuellen Bankzustand, Relationsprobe und visuellen Resolver zurueckbinden.

## Adversariale Regressionen

Drei neue Tests liefern jeweils einen intern gueltigen und digestkonsistenten,
aber fuer den Composite fremden Kindbefund:

1. Ein Formationsergebnis eines anderen vollstaendig verbrauchten Owners mit
   denselben Formationseingaben wird vor der ersten Spur verworfen.
2. Der erste Relationsschritt erhaelt einen gueltigen Befund fuer das spaetere
   gleichartige dritte Paar desselben Umschlags. Die andere Frameprovenienz
   wird vor jedem Abruf verworfen.
3. Der erste Abruf erhaelt einen gueltigen Befund eines anderen Probe-,
   Consumer- und Resolveraufrufs mit demselben visuellen Ziel. Die fremde
   Probe wird vor der Ergebnisveroeffentlichung verworfen.

Alle drei Composite-Owner enden `FAILED`; kein Gesamtresultat wird
veroeffentlicht.

## Testevidenz

Der neue S2-CS/S2-CU-Fokusumfang besteht mit `14/14` Tests. Der abschliessende
direkte Integrationslauf fuer Relationskern, atomaren Leseconsumer,
Relationsbildungs-Consumer und End-to-End-Evaluator besteht mit `47/47` Tests
in `1.096 s`.

Der gueltige kanonische Aufrufumfang und die Entscheidung
`FUNCTION_VALID_BASELINE_EXPLAINS` bleiben unveraendert.

## Grenze und naechster Schritt

S2-CU fuegt keine Fixturewerte, Parameter, Mechanik, Vergleichsprojektion oder
oeffentliche Schnittstelle hinzu. Feldkern, Snapshot, Produktion, Livepfade
und Semantik bleiben unberuehrt. Der Befund bleibt eine generisch erklaerte
assoziative Engineeringfunktion.

S2-CV soll die korrigierte Composite-Grenze rein statisch abschliessend
pruefen. Der Testlauf wird dabei nicht wiederholt.
