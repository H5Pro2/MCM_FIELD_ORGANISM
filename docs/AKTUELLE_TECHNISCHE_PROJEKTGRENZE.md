# Aktuelle technische Projektgrenze

## Vorrangige Grenze: S2-FT statisch blockiert

Der [S2-FT-Plan](S2FT_STATISCHER_FUNKTIONS_UND_AUSWERTUNGSPLAN_ATOMARER_B4_TSPM1_VERBUND.md)
hat die freigegebene 17-Schritt-Geschichte vollstaendig gegen die
unveraenderten Regeln materialisiert. Die positive Slow-Prognose ist dabei
nicht erreichbar: Fast-Kapazitaet 3 verdraengt P1 bei Schritt 4. Nach seiner
Neuanlage bei Schritt 5 folgen nur zwei passende Aktualisierungen, also
PPB-1-Support 2 statt des stabilen Supports 3.

Die fruehe B4-Folge und der spaetere B4-/Fast-Verlust waeren darstellbar;
P1 waere final jedoch nicht stabil aus `TSPM_SLOW` abrufbar. Deshalb lautet
der Status `BLOCKED_STATIC_SEQUENCE_DOES_NOT_REACH_SLOW_SUPPORT_3`. Es wurden
keine Fixtures, Tests, Funktionen oder Laeufe angelegt beziehungsweise
ausgefuehrt. Die kleinste dokumentierte Korrektur fuegt nach der Fast-Neuanlage
einen fuenften P1-Auftritt ein und erfordert eine neue ausdrueckliche
Entscheidung.

## Vorrangige Grenze: privater atomarer Koordinator qualifiziert

S2-FS hat den in S2-FR gebundenen privaten B4-/TSPM-1-Koordinator in genau
einem neuen Modul umgesetzt. Eine gemeinsame Rezeptorquelle wird vor beiden
Armaufrufen vollstaendig validiert. B4- und TSPM-Kandidaten bleiben lokal;
nur ein vollstaendig validierter Composite-Nachzustand wird zurueckgegeben.
Fehler setzen den Owner auf `FAILED`, Erfolg auf `CONSUMED`, und jeder Owner
ist terminal nur einmal verwendbar.

Die neutrale Testsuite wurde nach statischer Pruefung genau einmal ausgefuehrt
und bestand `12/12`, Exit-Code 0. Der read-only Pfad liefert nur
`B4_RECENT`, `TSPM_FAST` und `TSPM_SLOW`. Es gibt keinen dritten Speicher,
keine Gesamtentscheidung und keinen oeffentlichen Export. Das
Formationsledger zaehlt 617 funktionale Schreibwoerter, 468 Distanzterme und
54 Kontrollterme. Die bestehenden B4-, TSPM-1-, PPB-1-, API-, Snapshot- und
Feldquellen blieben unveraendert.

Der gueltige Befund ist ausschliesslich
`PRIVATE_ATOMIC_COORDINATOR_CONTRACT_VALID`. Ein funktionaler Verbundnachweis,
Runner, Hauptgeschichte und Feldintegration bleiben gesperrt. Der naechste
Schritt ist nach gesonderter Freigabe ein kleiner, vorab gebundener
Funktionsnachweis der drei getrennten Sichten, keine weitere allgemeine
Auditkaskade.

## Vorrangige Grenze: begrenzter Erhaltungsbefund abgeschlossen

Der separat freigegebene Hauptlauf
`retention-capacity-main-20260829-01` wurde genau einmal mit dem gebundenen
Umfang `146/170/16/316/1296` ausgefuehrt. Der anschliessend genau einmal
aufgerufene read-only Verifikator bestaetigt `RECORDING_COMPLETE`, 1296
Ereignisse und keine Beanstandung. Das Lauf-Gate ist wieder geschlossen.

Der [Befund](../reports/tspm1_functional/retention-capacity-main-20260829-01-evaluation/BEFUND.md)
belegt fuer die synthetischen Geschichten U, V, C, A, S1 und S2:

- vier statt zwei passende Expositionen stabilisieren N1 bis Support 3;
- der Slow-Zustand erhaelt N1 nach belegtem Fast-Ablauf;
- endlicher Slow-Kapazitaetsdruck ersetzt N1 durch D1 und N2 durch D2;
- B4 erhaelt die explizite Reihenfolge nur, solange alle benoetigten
  FIFO-Inhalte vorhanden sind;
- TSPM-1 bleibt beim Folgenbefund korrekt auf Inhaltserhaltung begrenzt.

Dieser Abschluss ist eine begrenzte technische Memory-Funktion und keine
allgemeine oder langfristige MCM-Memory, keine Semantik und keine Feldwirkung.
B4, TSPM-1, PPB-1, API, Snapshot und Feldpfad bleiben unveraendert. Alte
Einstiege, S2-FC und der geschlossene Plattformpfad bleiben gesperrt.

Der Architekturentscheid ist jetzt im
[S2-FR-Vertrag](S2FR_STATISCHER_ARCHITEKTUR_UND_FALSIFIKATIONSVERTRAG_ATOMARER_B4_TSPM1_VERBUND.md)
statisch gebunden. B4 und TSPM-1 werden nicht verschmolzen. Ein spaeterer
privater Koordinator darf beiden genau dieselbe Rezeptorexposition geben und
nur gemeinsam einen B4- und TSPM-Nachzustand veroeffentlichen. Der Abruf
bleibt in `B4_RECENT`, `TSPM_FAST` und `TSPM_SLOW` getrennt; eine automatische
Gesamtauswahl ist ausgeschlossen. Folgenordnung stammt ausschliesslich aus
B4. Das gemeinsame Ressourcenledger muss beide Arme und den Koordinator
vollstaendig addieren.

Die dort noch offene Koordinatorimplementierung und ihre neutralen Tests sind
mit S2-FS inzwischen abgeschlossen. Fixtures, Funktionsrunner, weitere
Hauptausfuehrung, Feldintegration und neue Speichermechanik bleiben gesperrt.

## Vorherige Grenze: Runner implementiert, Ausfuehrung gesperrt

Der [Reihenfolge-Pruefplan](VISUELLE_REIHENFOLGE_AUFGABEN_UND_PRUEFPLAN.md)
war die dokumentarische Grundlage. Vier Bilder innerhalb der B4-Kapazitaet,
zwei Folgen, feste Zeitabstaende und eingefrorene L1-KAL-Grenzen;
keine neue Speichermechanik. Bildungsindizes muessen aus der tatsaechlichen
Zustandsfortsetzung stammen. Der private read-only Sequenzpruefer ist
implementiert, wegen des nachfolgenden Fehlabschlusses aber nicht funktional
abgenommen. Keine weitere Ausfuehrung, Feldintegration oder Wiedereroeffnung
alter Einstiege. G1 bleibt eine dokumentierte Grenze ohne zusaetzliche Mechanik.

Die danach gesondert freigegebene private Umsetzung liegt vor und acht Tests
bestanden. Die einmalige Hauptuntersuchung ist wegen eines Fehlers im
Abschlussvalidator [nicht auswertbar](../reports/tspm1_functional/sequence-20260829-01/BEFUND.md).
Vollstaendige deskriptive Ereignisse ersetzen den fehlenden regulaeren
Abschluss nicht. Der Validatorverweis ist korrigiert, aber nicht erneut
getestet oder ausgefuehrt; der Einstieg ist gesperrt. Keine Wiederholung,
Teilfortsetzung oder funktionale Ergebnisinterpretation ist freigegeben.

Die naechste Richtung wurde zunaechst als
[unabhaengiger Bestaetigungsplan](VISUELLE_REIHENFOLGE_UNABHAENGIGE_BESTAETIGUNGSPLAN.md)
gebunden: vier neue deterministisch ausgewaehlte Bilder, unveraenderte
Folgenfunktion und Schwelle, ein kleiner vollstaendiger Validatorabschluss
und danach eine neue Einmalgrenze. Der alte Fehlversuch bleibt unangetastet.
Die begrenzte Refaktorierung und genau ein
[Validator-Korrekturtest](../reports/tspm1_functional/sequence-confirmation-validator-20260829-01/BEFUND.md)
sind abgeschlossen: vollstaendiger Mini-Abschluss `COMPLETE`, 1/1 Test,
Exit-Code 0 und null fachliche Operatoraufrufe.

Der anschliessend separat freigegebene
[Hauptlauf](../reports/tspm1_functional/sequence-confirmation-20260829-01/BEFUND.md)
wurde genau einmal vollstaendig ausgefuehrt: 56 Bildanalysen, acht B4-Bildungen,
zwoelf Folgeproben, 24 read-only Entscheidungen und 152 Ereignisse. GEORDNET
trennte Original- und Gegenfolge in allen zwoelf Faellen korrekt;
REIHENFOLGEBLIND bestaetigte diagnostisch die Inhaltsgleichheit. Die reine
Belegpruefung rechnete 192 Paarabstaende ohne Projektmodulaufruf nach. Damit
ist nur ein begrenzter technischer Kurzzeit-Sequenzabruf ueber explizite
Bildungsindizes bestaetigt. B4, TSPM-1, PPB-1, API, Snapshot und Feldpfad
bleiben unveraendert; der Lauf-Gate und alle alten Einstiege sind gesperrt.

Als naechste Grenze ist ausschliesslich der
[statische Zwischenreiz-/Kapazitaetsplan](FOLGENERHALTUNG_ZWISCHENREIZE_KAPAZITAETSDRUCK_PRUEFPLAN.md)
gebunden. Er untersucht Inhaltserhaltung bei B4 und TSPM-1 sowie Folgenordnung
nur dort, wo der gespeicherte Zustand sie repraesentiert. TSPM-1 bekommt keine
Folgenkennung, keinen Uebergangstraeger und keine Recorderhistorie. Sein Fast-
und Slow-Inhaltsbefund ist getrennt zu berichten; fehlende volle Folgenordnung
ist kein negativer Memory-Gesamtbefund. Der Slow-Vergleich setzt jetzt korrekt
vier passende Expositionen bis PPB-Support 3 voraus und trennt unverdichtetes
N1, verdichtetes N1, Fast-Ablauf sowie Slow-Kapazitaetsdruck. Implementiert und
statisch geprueft sind die privaten Geschichten-Fixtures und die
zustandsunveraenderliche Fast-/Slow-Inhaltsauswertung. Die einmalig
freigegebenen acht synthetischen Adaptertests sind mit `8/8` abgeschlossen;
der private Runner, die exklusive Hashkettenaufzeichnung und der getrennte
read-only Ergebnisverifikator sind inzwischen implementiert. Ihr Umfang ist
statisch auf `146/170/16/316/1296` gebunden. Der Runner besitzt keinen offenen
CLI-Einstieg und `MAIN_EXECUTION_ENABLED` bleibt `False`. Die neuen Module
wurden nur per AST, Quellenvergleich und Grenzpruefung kontrolliert; keine
Speicherfunktion und kein Test wurde dabei aufgerufen. Als naechster Schritt
war nur eine gesondert freizugebende technische Qualifikation mit kleinen
neutralen Fixtures zulaessig. Diese wurde genau einmal ausgefuehrt: sechs von
acht Tests bestanden, zwei stoppten wegen der Windows-unzulaessigen exakten
Recorder-Pfadtyppruefung vor der Ergebnisanlage. Gesamtstatus:
`QUALIFICATION_FAILED`, Exit-Code 1. Keine Korrektur und keine Wiederholung.
Die getrennt freigegebene Zwei-Stellen-Korrektur wurde statisch abgenommen.
Der anschliessende neue Einmallauf
`retention-runner-qualification-20260829-02` bestand alle acht unveraenderten
Tests, Exit-Code 0. Ein statischer Abschlussaudit bestaetigt Quelldigests,
Einmaligkeit, Hauptbudgets und den weiterhin geschlossenen Schalter. Damit
sind nur Runner, Recorder und Verifikator technisch qualifiziert.
Hauptausfuehrung und alte Einstiege bleiben gesperrt.

## Abgeschlossener Umfang: einmalige L1-Bestaetigung

Der [Kalibrierungs- und Bestaetigungsplan](VISUELLE_L1_KALIBRIERUNG_UND_BESTAETIGUNGSPLAN.md)
bindet die einfache aufgabenspezifische Schwellenwahl, Mindestunterscheidbarkeit
und prospektiv neue Bildpaare. Die nachfolgend gesondert freigegebene private
Umsetzung und einmalige Ausfuehrung sind abgeschlossen: acht bestandene Tests,
56 Bildanalysen, acht Bildungen, 48 Probeinputs und 96 Abrufe.
Der [Befund](../reports/tspm1_functional/calibration-20260828-01/BEFUND.md)
bestaetigt L1-KAL fuer alle 36 Pflichtentscheidungen; G1 bleibt getrennte
Grenzdiagnose mit sechs gleichgesetzten Tauschen je Regel. Die Schwelle
ist technisch vorgegeben, nicht erlernt. Keine nachtraegliche Kalibrierung.
Die Freigabe ist verbraucht, der private Einstieg wieder gesperrt. Weitere
Bildanalysen, Bildungen, Proben, Tests oder Integration sind nicht freigegeben.
Die bisherigen A/B/C-Befunde bleiben unveraendert und sind Entwicklungsdaten,
kein unabhaengiger Bestaetigungssatz. Rezeptor, Speicher und gespeicherte
Werte bleiben unveraendert; keine neue Memory-Mechanik oder Feldintegration.

Der [Ortsstrukturplan](VISUELLE_ORTSSTRUKTUR_AUFGABEN_UND_PRUEFPLAN.md)
war die dokumentarische Folgeaufgabe des akzeptierten Funktionsvergleichs.
B4 ist bevorzugte Arbeitsreferenz fuer dessen Aufgaben;
TSPM-1 und PPB-1 bleiben unveraendert erhalten. Die neue Frage betrifft feste
visuelle Zellwerte bei gleicher globaler Verteilung. Die anschliessend separat
freigegebene private Umsetzung ist mit 11/11 fokussierten Tests und genau
einem Versuch mit 28 Bildanalysen, acht Bildungen und 48 Proben abgeschlossen.
Der [Befund](../reports/tspm1_functional/spatial-20260828-01/BEFUND.md) trennt
erhaltene Rezeptor-/Speicherwerte von sechs Fehlgleichsetzungen des kleinen
Ortstauschs durch die bestehende Abrufregel. Keine Parameteranpassung und
keine zusaetzliche Speichermechanik. Eine andere Abrufbewertung bedarf einer
getrennten Entscheidung. Alle verbrauchten Versuchseinstiege sowie S2-FC
bleiben gesperrt; keine Wiederholung, automatische Ersetzung oder Feldintegration.

Die [einmalige Bestandskonsolidierung](BESTANDSKONSOLIDIERUNG_NACH_PLATTFORMSTOPP.md)
erhaelt Feldkern, private PPB-1-/TSPM-1-Komponenten, Vergleichsinfrastruktur
und historische Belege. Sie ist von dem anschliessend separat freigegebenen
und tatsaechlich ausgefuehrten TSPM-1-Funktionsvergleich zu unterscheiden.

Der konkrete Supervisor-/Child-Plattformpfad ist geschlossen. Nicht
abgenommene Infrastruktur bleibt erhalten, aber nicht zur Ausfuehrung
freigegeben. S2-FC und der alte Matrixeinstieg bleiben gesperrt.

Das fachliche Ziel ist die Pruefung von Aufnahme, Erhaltung, Konsolidierung
und Abruf der vorhandenen technischen Memory-Architektur. Ein bekanntes
Speicherverfahren darf dabei brauchbar sein, ohne eine neue MCM-Feldursache
darzustellen. Geschlossene Feldursachen-Kandidaten werden dadurch nicht
wiedereroeffnet; Feldintegration, API und Snapshot bleiben unveraendert.

Die ausdruecklich freigegebene Strategieaenderung ist im
[begrenzten Funktionspruefplan](TSPM1_VERHAELTNISMAESSIGER_FUNKTIONSPRUEFPLAN.md)
dokumentiert. Er benennt die ersetzten Plattformanforderungen, unveraenderte
H1-H7-Geschichten und Budgets sowie eine lokale, vollstaendige Ergebnisaufzeichnung.
Die Aenderung ist keine Abnahme alter Plattformbelege und keine Umgehung durch
einen neuen Matrixnamen. Fehlende Aufzeichnung bedeutet nicht auswertbar,
keinen negativen Memory-Befund und keine automatische Wiederholungsfreigabe.

Die drei Dateiarbeiten und acht fokussierten Tests wurden separat freigegeben
und abgeschlossen. Anschliessend wurde genau ein 56-Zellen-Vergleich ueber
den neuen privaten Einstieg ausdruecklich freigegeben und vollstaendig
ausgefuehrt: 336 Bildungsangebote, 144 Proben, Exit-Code 0. Der
[Befund](../reports/tspm1_functional/functional-20260828-01/BEFUND.md)
trennt Abrufqualitaet, Ressourcen und die weiterhin offene Repraesentationsfrage.
TSPM1, R0 und B4 erreichen dasselbe gebundene Funktionsprofil; B4 ist dafuer
die einfachere ausreichende Engineeringloesung. Das ist keine allgemeine
Aussage ueber beliebige Wahrnehmungssequenzen oder eine eigene MCM-Feldursache.

Die einmalige Ausfuehrung ist verbraucht. Der neue private Einstieg wurde
nach der Belegpruefung wieder gesperrt; keine Wiederholung oder Teilfortsetzung
ist freigegeben. TSPM-1-Grundkern, PPB-1, Baselines, Fixtures, Parameter, API,
Snapshot und Feldpfad bleiben unveraendert. Reichhaltigere Repraesentationen,
Semantik, innerer Kontext und Feldrueckwirkung bleiben getrennte spaetere
Entwicklungsstufen. Die nachfolgenden Abschnitte bleiben historische Protokolle;
ihre Fortsetzungsanweisungen besitzen keinen Vorrang vor dieser Grenze.

## Vorrangige Projektgrenze nach S1-UN

S1-UM ist fachlich akzeptiert. Die Kandidatenforschung pausiert, und nur die
technische Konsolidierung des bestehenden primaeren Feldkerns ist zulaessig.
Neue Gleichungen, Kandidatenruntimes sowie Feld- und Matrixausfuehrungen sind
gesperrt.

Eine Wiederaufnahme erfordert einen vollstaendigen statischen Vertrag fuer
genau einen neuen Kandidaten mit lokaler Ursache, Bilanz, erreichbarer
Feldgeschichte, eigener Feldprognose, staerkster Gegenbaseline und
eindeutiger Stoppbedingung. Details:
[`S1-UN`](S1UN_TECHNISCHER_KONSOLIDIERUNGSAUFTRAG_UND_WIEDEROEFFNUNGSTOR.md).

## Vorrangige Forschungsgrenze nach S1-UM

Der primaere MCM-Feldkern bleibt aktiv, stabil und unveraendert. RFM-1,
ACM-1H und alle zuvor geschlossenen Kandidatenzweige bleiben ausserhalb der
aktiven Oberflaeche. Es ist keine neue lokale Ursache mit eigener Bilanz und
nicht baseline-reduzierbarer Gegenprognose vorhanden.

Die Kandidatenforschung pausiert bis zu einer ausdruecklichen fachlichen
Richtungsentscheidung. Ohne sie sind keine neue Mechanik, Gleichung,
Parameter, Implementierung oder Ausfuehrung zulaessig. Details:
[`S1-UM`](S1UM_STATISCHER_RUECKKEHR_UND_LUECKENAUDIT_PRIMAERER_MCM_FELDKERN.md).

## Vorrangige Forschungsgrenze nach S1-SO

Kanonische carryfreie Matrixserialisierung, transitive lokale
Quellinventare, feste Laufpfade, Versuchsschutz, Wiederholungssperre und
atomare Same-Directory-Publikation sind statisch gebunden.

Als genau ein Anschluss ist S1-SP fuer Matrixresultatvalidator,
Artefaktmodul, Einmalpublisher und hoechstens 20 noch nicht ausgefuehrte
synthetische Tests zulaessig. Modellkerne und Matrixproducer bleiben
unveraendert; keine reale Zelle, Matrix oder Ergebnisentscheidung. Details:
[`S1-SO`](S1SO_STATISCHER_REALPFAD_SERIALISIERUNGS_ARTEFAKT_QUELLBELEG_UND_EINMALLAUFVERTRAG.md).

## Vorrangige Forschungsgrenze nach S1-SN

Die atomare Matrixhuelle ist mit 17 von 17 bestandenen synthetischen Tests
im ersten unveraenderten Lauf technisch abgenommen. Kein realer
Modellkernaufruf, keine reale Zelle und kein Matrixoutput wurden erzeugt.

Als genau ein Anschluss ist S1-SO fuer einen statischen Realpfad- und
Artefaktvertrag zulaessig. Er muss kanonische carryfreie Serialisierung,
Quell- und Budgetbelege, atomare Dateipublikation und Einmallauf ohne Retry
binden. Keine Implementierung, kein Test und keine Ausfuehrung. Details:
[`S1-SN`](S1SN_FOKUSSIERTER_SYNTHETISCHER_TESTLAUF_UND_TECHNISCHE_ABNAHME_ATOMARER_MATRIXHUELLE.md).

## Vorrangige Forschungsgrenze nach S1-SM

Einzelzellenresultat-Validierung, planweise/rollenweise Matrixordnung,
Summaryledger, Checkpointledger, Matrixdigestkette und atomare
Fehlerpublikation sind implementiert. Finale Carryobjekte verlassen die
Zellvalidierung nicht.

17 fokussierte Tests mit synthetischen Zellresultaten sind nur definiert.
Als genau ein Anschluss ist S1-SN fuer einen unveraenderten Lauf dieser
einen Testdatei zulaessig. Auch bei Erfolg bleiben reale Zellen,
238-Zellen-Matrix, Comparatoren und Ergebnisentscheidung gesperrt. Details:
[`S1-SM`](S1SM_IMPLEMENTIERUNG_ATOMARE_ENDLICHE_VIER_KNOTEN_MATRIXHUELLE_UND_SYNTHETISCHE_TESTDEFINITION.md).

## Vorrangige Forschungsgrenze nach S1-SL

Die spaetere 238-Zellen-Matrix besitzt nun eine feste planweise/rollenweise
Ordnung, getrennte Frischstarts, ein endliches 1.778/238/560-Budget, ein
privatdatenfreies Summaryledger und eine atomare Publikationsgrenze.

Eine fehlgeschlagene Zelle stoppt ohne Retry und ohne Teilpublikation. Als
genau ein Anschluss ist S1-SM fuer die neue Matrixhuelle, eine reine
Einzelzellenresultatvalidierung und hoechstens 18 noch nicht ausgefuehrte
Tests zulaessig. Modellkerne, Fixture und Comparatoren bleiben unveraendert;
keine Zelle oder Matrix darf ausgefuehrt werden. Details:
[`S1-SL`](S1SL_STATISCHER_ENDLICHER_VIER_KNOTEN_MATRIX_AUSFUEHRUNGS_LEDGER_UND_PUBLIKATIONSVERTRAG.md).

## Vorrangige Forschungsgrenze nach S1-SK

Die atomare Einzelzellenoberflaeche ist mit 14 von 14 bestandenen Tests im
ersten unveraenderten Lauf technisch abgenommen. Der Testlauf erzeugte
isolierte Testinstanzen, aber keine vollstaendige Matrix, keinen
Matrixoutput und keine Ergebnisentscheidung.

Als genau ein Anschluss ist S1-SL fuer einen statischen endlichen
Matrixvertrag zulaessig. Er darf die 238 Frischzellen, 1778 Intervalle, 238
zeitlosen Alignoperationen, 560 Pflichtcheckpoints, Fehlerabbruch und
atomare Publikation binden. Keine Runnerimplementierung und keine
Ausfuehrung. Details: [`S1-SK`](S1SK_FOKUSSIERTER_TESTLAUF_UND_TECHNISCHE_ABNAHME_ATOMARER_EINZELZELLEN_LEBENSZYKLUS.md).

## Vorrangige Forschungsgrenze nach S1-SJ

Carry-Neubindung, zeitlose Alignprojektion, passive Checkpoints,
Ereigniskette und atomare Einzelzellenausgabe sind implementiert. Die
Modellkerne und das kanonische 17-Plan-Fixture wurden nicht veraendert.

14 fokussierte Tests sind nur definiert. Als genau ein Anschluss ist S1-SK
fuer einen unveraenderten Lauf dieser einen Testdatei zulaessig. Bei einem
Fehler wird ohne Wiederholung gestoppt. Keine Matrixzelle, kein Gesamtpaket,
kein Forschungslauf und keine funktionale Interpretation. Details:
[`S1-SJ`](S1SJ_IMPLEMENTIERUNG_ATOMARER_VIER_KNOTEN_EINZELZELLEN_LEBENSZYKLUS.md).

## Vorrangige Forschungsgrenze nach S1-SI

Alignprojektion, Carry-Neubindung, passive Checkpoints, Ereigniskette und
atomare Einzelzellenausgabe sind statisch gebunden. Der bisherige
`last_distribution`-Digest bleibt im Alignreceipt; das neue Feld erhaelt
eine passende zeitlose Nullframe-Projektionsdistribution.

Als genau ein Anschluss ist S1-SJ fuer die Implementierung und hoechstens
16 noch nicht ausgefuehrte fokussierte Tests zulaessig. Keine Matrixzelle,
kein Gesamtpaket und kein Forschungslauf. Details:
[`S1-SI`](S1SI_STATISCHER_VIER_KNOTEN_ALIGN_CHECKPOINT_CARRY_UND_ATOMARER_EINZELZELLEN_LEBENSZYKLUSVERTRAG.md).

## Vorrangige Forschungsgrenze nach S1-SH

Das 17-Plan-Expositionsfixture ist mit 13 von 13 bestandenen fokussierten
Tests technisch abgenommen. Kein Alignziel wurde auf ein Feld angewandt und
kein Modellintervall ausgefuehrt.

Als genau ein Anschluss ist S1-SI fuer einen statischen Align-, passiven
Checkpoint- und atomaren Einzelzellen-Lebenszyklusvertrag zulaessig. Keine
Implementierung, kein Test, keine Matrixzelle und kein Forschungslauf.
Details: [`S1-SH`](S1SH_FOKUSSIERTER_TESTLAUF_UND_TECHNISCHE_ABNAHME_VIER_KNOTEN_EXPOSITIONSFIXTURE.md).

## Vorrangige Forschungsgrenze nach S1-SG

Das kanonische 17-Plan-Fixture, sein Digest und sein Fail-Closed-Validator
sind implementiert. 13 fokussierte Tests sind definiert. Weder Align noch
ein Modellintervall wurde ausgefuehrt.

Als genau ein Anschluss ist S1-SH fuer den einmaligen unveraenderten Lauf
von `tests/test_four_node_exposure_fixture.py` zulaessig. Keine Korrektur im
Laufschritt, keine Alignanwendung, kein Modellaufruf, keine Matrixzelle und
kein Forschungslauf. Details:
[`S1-SG`](S1SG_IMPLEMENTIERUNG_KANONISCHES_VIER_KNOTEN_EXPOSITIONSFIXTURE_UND_FAIL_CLOSED_VALIDATOR.md).

## Vorrangige Forschungsgrenze nach S1-SF

Das gemeinsame synchrone Segmentalphabet, Alignziel und alle 17 konkreten
Planfolgen sind gebunden. Die Topologie umfasst pro Modellrolle 127
modellwirksame Intervalle, 17 Alignoperationen und 40 passive
Pflichtbeobachtungen. Diese Zahlen sind keine Ausfuehrungsfreigabe.

Als genau ein Anschluss ist S1-SG fuer ein kanonisches Planfixture,
Fail-Closed-Validierung und noch nicht ausgefuehrte fokussierte Tests
zulaessig. Keine Modellanpassung, keine Matrixzelle und kein Forschungslauf.
Details: [`S1-SF`](S1SF_STATISCHER_GEMEINSAMER_SYNCHRONER_VIER_KNOTEN_EXPOSITIONSSEGMENT_EREIGNISPLAN_UND_17_REPLIKEN_FIXTUREVERTRAG.md).

## Vorrangige Forschungsgrenze nach S1-SE

Die Frischmatrixregistrierung ist mit 11 von 11 bestandenen fokussierten
Tests technisch abgenommen. Die getrennten U-Frischkontrollen und die
238-/560-Vollstaendigkeitszahlen sind eindeutig mit dem unveraenderten
v1-Frischmanifest verbunden.

Als genau ein Anschluss ist S1-SF fuer einen statischen gemeinsamen
synchronen 17-Repliken-Segment-, Ereignisplan- und Fixturevertrag
zulaessig. Keine Implementierung, kein Test, keine Matrixzelle und kein
Forschungslauf. Details:
[`S1-SE`](S1SE_FOKUSSIERTER_TESTLAUF_UND_TECHNISCHE_ABNAHME_VIER_KNOTEN_FRISCHMATRIXREGISTRIERUNG.md).

## Vorrangige Forschungsgrenze nach S1-SD

Die neue Matrixregistrierung, ihr strikter Consumer und elf fokussierte
Tests sind implementiert. Der Registrierungsdigest reproduziert sich im
statischen Audit. Das v1-Manifest und sein Consumer sind unveraendert.

Als genau ein Anschluss ist S1-SE fuer den einmaligen unveraenderten Lauf
von `tests/test_four_node_fresh_matrix_registration.py` zulaessig. Keine
Korrektur im Laufschritt, kein allgemeiner Testbestand, kein Fixture, keine
Matrixzelle und kein Forschungslauf. Details:
[`S1-SD`](S1SD_MATERIALISIERUNG_UND_IMPLEMENTIERUNG_VIER_KNOTEN_FRISCHMATRIXREGISTRIERUNG.md).

## Vorrangige Forschungsgrenze nach S1-SC

Das abgenommene v1-Frischmanifest bleibt unveraendert. S1-SC bindet eine
getrennte versionierte Matrixregistrierung, welche die identischen
Frischwerte mit 17 Repliken, 238 Zellen und 560 Pflichtrecords verbindet.

Als genau ein Anschluss ist S1-SD fuer genau eine neue Reportdatei, einen
strikten Consumer und eine fokussierte Testdatei zulaessig. Die Tests werden
noch nicht ausgefuehrt. Keine v1-Aenderung, kein Frischbau, kein Fixture,
keine Matrixzelle und kein Forschungslauf. Details:
[`S1-SC`](S1SC_STATISCHER_VERSIONIERTER_FRISCHMANIFEST_MATRIXREGISTRIERUNGS_MIGRATIONS_UND_ABNAHMEBUDGETVERTRAG.md).

## Vorrangige Forschungsgrenze nach S1-SB

Die korrigierte statische Achse besitzt 17 Repliken, darunter getrennte
fruehe und spaete U-Frischkontrollen. Daraus folgen 238 Matrixzellen und 560
passive Pflichtrecords. Werte, Dauern und Fixtures bleiben offen.

Das abgenommene Frischmanifest v1 traegt weiterhin seine historische
224-Zellen-Aussage und darf nicht in-place geaendert werden. Als genau ein
Anschluss ist S1-SC fuer den statischen Vertrag einer versionierten
Manifestmigration zulaessig. Keine Materialisierung, keine
Consumer-Aenderung, kein Test und kein Forschungslauf. Details:
[`S1-SB`](S1SB_STATISCHE_KORREKTUR_17_REPLIKEN_ACHSE_UND_ZWEI_ZEITANGEPASSTE_U_FRISCHKONTROLLEN.md).

## Vorrangige Forschungsgrenze nach S1-SA

Der statische 16-Repliken-Fixturevertrag ist nicht bindbar: Der einzige
`U_FRESH_B`-Nullvorlauf kann nicht gleichzeitig an die zwei verschiedenen
B-Startzeiten nach `GAP_EARLY` und `GAP_LATE` angepasst werden. Werte,
Dauern und Digests wurden deshalb nicht gewaehlt.

Vor einem weiteren technischen Schritt ist die fachliche Wahl zwischen 17
Repliken mit zwei getrennten U-Frischkontrollen und einem reduzierten
16-Repliken-U-Vergleich erforderlich. Keine Implementierung, kein Test,
keine Matrixzelle und kein Forschungslauf. Details:
[`S1-SA`](S1SA_STOPP_WIDERSPRUCH_16_REPLIKEN_FIXTURE_UND_U_FRISCHKONTROLLE.md).

## Vorrangige Forschungsgrenze nach S1-RZ

Die Vier-Knoten-Modellaufrufoberflaeche ist mit 11 von 11 bestandenen Tests
technisch abgenommen. Alle 14 synchronen Rollenpfade sind verfuegbar; elf
transiente Rollenpfade und die drei synchron-only Gates bestehen ebenfalls.
Noch wurde keine Expositionsreplik oder Matrixzelle ausgefuehrt.

Als genau ein Anschluss ist S1-SA fuer einen statischen gemeinsamen
synchronen Vier-Knoten-Expositionssegment-, Ereignisplan- und
16-Repliken-Fixturevertrag zulaessig. Keine Implementierung, kein Test,
keine Matrixzelle und kein Forschungslauf. Details:
[`S1-RZ`](S1RZ_FOKUSSIERTER_TESTLAUF_UND_TECHNISCHE_ABNAHME_VIER_KNOTEN_MODELLAUFRUF.md).

## Vorrangige Forschungsgrenze nach S1-RY

Die gemeinsame atomare Aufrufoberflaeche fuer alle 14 Rollen und elf
fokussierte Tests sind implementiert. Kein Modellkern wurde in S1-RY
ausgefuehrt. Die Huelle trennt synchrone und transiente Faehigkeit, bindet
vollstaendige Carries und verwirft Fehler ohne Teilresultat.

Als genau ein Anschluss ist S1-RZ fuer den einmaligen unveraenderten Lauf
von `tests/test_four_node_model_invocation.py` zulaessig. Keine Korrektur im
Laufschritt, keine Matrixzelle und kein Forschungslauf. Details:
[`S1-RY`](S1RY_IMPLEMENTIERUNG_GEMEINSAME_VIER_KNOTEN_MODELLAUFRUF_UND_ATOMARE_ERGEBNISOBERFLAECHE.md).

## Vorrangige Forschungsgrenze nach S1-RX

Die statische Aufruf-, Intervall-, Konfigurations-, Carry- und
Ergebnisgrenze ist fuer alle 14 Vier-Knoten-Rollen gebunden. B1, B2 und M4
sind nur synchron anschliessbar. Jede unzulaessige Intervallform und jedes
Teilresultat bleiben fail-closed. Bestehende Konfigurationen werden nur
typisiert materialisiert und nicht neu gewaehlt.

Als genau ein Anschluss ist S1-RY fuer die gemeinsame Vier-Knoten-
Modellaufruf- und atomare Ergebnisoberflaeche sowie ihre noch nicht
ausgefuehrten Tests zulaessig. Keine Matrix, kein Comparator und kein
Forschungslauf. Details:
[`S1-RX`](S1RX_STATISCHER_ROLLENWEISER_MODELLAUFRUF_INTERVALL_KONFIGURATION_FOLGEZUSTAND_UND_ERGEBNISVERTRAG.md).

## Vorrangige Forschungsgrenze nach S1-RW

Die reine Vier-Knoten-Modelleingangsmontage ist mit 15 von 15 bestandenen
unveraenderten Tests technisch abgenommen. Die konstruktive Kette vom
validierten Manifest bis zum rollenrichtigen Modelleingangsrecord ist fuer
alle 14 Rollen verfuegbar. Kein Modellkern wurde dabei aufgerufen.

Als genau ein Anschluss ist S1-RX fuer einen statischen rollenweisen
Modellaufruf-, Intervall-, Konfigurations-, Folgezustands- und atomaren
Ergebnisvertrag zulaessig. Keine Implementierung, kein weiterer Test, kein
Adapter, keine Matrixzelle und kein Feldlauf. Details:
[`S1-RW`](S1RW_FOKUSSIERTER_TESTLAUF_UND_TECHNISCHE_ABNAHME_MODELLEINGANGSMONTAGE.md).

## Vorrangige Forschungsgrenze nach S1-RV

Die reine Modelleingangsmontage und 15 fokussierte Tests sind innerhalb des
S1-RU-Budgets implementiert. Nur B3-B6 erhalten eine neue Feldhuelle mit
nativer M-Einbettung; alle anderen Modellfelder bleiben identisch zum
oeffentlichen Frischfeld. Kein Modellkern oder historischer Orchestrator ist
angeschlossen.

Die Tests wurden noch nicht ausgefuehrt. Als genau ein Anschluss ist S1-RW
fuer den einmaligen unveraenderten Lauf von
`tests/test_four_node_model_input_assembly.py` zulaessig. Keine Korrektur im
Laufschritt, kein Adapter, kein Intervall und kein Feldlauf. Details:
[`S1-RV`](S1RV_IMPLEMENTIERUNG_REINE_VIER_KNOTEN_MODELLEINGANGSMONTAGE.md).

## Vorrangige Forschungsgrenze nach S1-RU

S1-RU bindet die Modelleingangsmontage fuer alle 14 abgenommenen
Vier-Knoten-Frischbundle. Das oeffentliche Frischfeld bleibt unveraendert;
nur B3-B6 duerfen ihren nativen M-Zustand in eine neue Feldinstanz
einbetten. Alle anderen privaten Rollen bleiben getrennt. Historische
S1-JN/S1-JW-Kontexte, alte Frischbuilder und der alte Ein-Replik-
Orchestrator sind fuer diesen Anschluss gesperrt.

Noch existiert keine Montageimplementierung und kein Adapteranschluss wurde
ausgefuehrt. Als genau ein Anschluss ist S1-RV fuer eine reine
Vier-Knoten-Montagefunktion und ihre noch nicht ausgefuehrten fokussierten
Tests zulaessig. Kein Modellkern, kein Intervall, keine Matrixzelle und kein
Feldlauf. Details:
[`S1-RU`](S1RU_STATISCHER_ROLLENWEISER_ADAPTERANSCHLUSS_MODELLEINGANGSMONTAGE_UND_INTEGRITAETSVERTRAG.md).

## Vorrangige Forschungsgrenze nach S1-RT

Die Vier-Knoten-Frischfabrik ist nach 16 von 16 bestandenen unveraenderten
Fabriktests fuer alle 14 Rollen technisch abgenommen. Die Abnahme umfasst
Frischzustand, Digestbruecken, registrierte Roundtrips und Objekttrennung,
nicht aber Modellanschluss oder Ausfuehrung.

Als genau ein Anschluss ist S1-RU fuer den statischen rollenweisen
Modelleingangs- und Adapteranschlussvertrag zulaessig. Implementierung,
weitere Tests, Matrix und Feldlauf bleiben gesperrt. Siehe
[`S1-RT`](S1RT_UNVERAENDERTER_WIEDERHOLUNGSLAUF_UND_TECHNISCHE_ABNAHME_ROLLENFABRIK.md).

Die nachfolgenden aelteren Grenzen bleiben chronologischer Nachweisbestand.
Ihre Weiterfreigaben sind operativ ueberholt.

## Vorrangige Forschungsgrenze nach S1-RS

Die reversible B3-B6-Massenabbildung ist an den zwei zugelassenen lokalen
Fabrikstellen implementiert. Manifest, native Substratklassen, Tests, Werte,
Digests und andere Rollen bleiben unveraendert.

Die Korrektur ist noch nicht technisch abgenommen. Als genau ein Anschluss
ist S1-RT fuer die unveraenderte Wiederholung der 16 Fabriktests zulaessig.
Codeaenderung, Consumer-Gesamtlauf, Adapter, Matrix und Feldlauf bleiben
gesperrt. Siehe
[`S1-RS`](S1RS_IMPLEMENTIERUNG_REVERSIBLE_B3_B6_MASSENIDENTITAETSABBILDUNG.md).

Die nachfolgenden aelteren Grenzen bleiben chronologischer Nachweisbestand.
Ihre Weiterfreigaben sind operativ ueberholt.

## Vorrangige Forschungsgrenze nach S1-RR

Die einzige zulaessige Korrektur ist als reversible lokale Abbildung
`node_id -> neuron_id -> node_id` gebunden. Sie betrifft ausschliesslich die
B3-B6-Massenkonstruktion und deren registrierte Rueckprojektion.

Manifest, native Klassen, Werte, Digests, andere Rollen und Tests bleiben
unveraendert. Als genau ein Anschluss ist S1-RS fuer die begrenzte
Implementierung zulaessig. Testausfuehrung, Adapter, Matrix und Feldlauf
bleiben gesperrt. Siehe
[`S1-RR`](S1RR_STATISCHER_KORREKTURVERTRAG_B3_B6_MASSENIDENTITAETSABBILDUNG.md).

Die nachfolgenden aelteren Grenzen bleiben chronologischer Nachweisbestand.
Ihre Weiterfreigaben sind operativ ueberholt.

## Vorrangige Forschungsgrenze nach S1-RQ

Die Rollenfabrik ist nach dem fokussierten Lauf noch nicht technisch
abgenommen. 13 Testmethoden bestanden; drei Methoden scheiterten an der
fehlenden lokalen Uebersetzung vom registrierten Massenfeld `node_id` zum
nativen Feld `neuron_id`.

Als genau ein Anschluss ist S1-RR fuer den statischen reversiblen
Korrekturvertrag zulaessig. Manifest, native Substratklasse, andere Rollen,
Adapter, Matrix und Feldlauf bleiben unveraendert beziehungsweise gesperrt.
Siehe
[`S1-RQ`](S1RQ_FOKUSSIERTER_FABRIKTESTLAUF_NICHT_ABGENOMMEN.md).

Die nachfolgenden aelteren Grenzen bleiben chronologischer Nachweisbestand.
Ihre Weiterfreigaben sind operativ ueberholt.

## Vorrangige Forschungsgrenze nach S1-RP

Die bestehende Frischfabrik implementiert jetzt alle 14 Rollenbundle, die
getrennten Kanten- und M2-Geometriedigestpfade sowie den registrierten
Privatpayload-Roundtrip. Sie besitzt keine Advance- oder Adapterfunktion.

Die 16 Fabriktests sind definiert, aber noch nicht ausgefuehrt. Als genau ein
Anschluss ist S1-RQ fuer diesen fokussierten Testlauf zulaessig. Consumer-
Gesamtlauf, allgemeine Tests, Adapter, Matrix und Feldlauf bleiben gesperrt.
Siehe
[`S1-RP`](S1RP_IMPLEMENTIERUNG_ROLLENBUNDLE_UND_DIGESTBRUECKEN.md).

Die nachfolgenden aelteren Grenzen bleiben chronologischer Nachweisbestand.
Ihre Weiterfreigaben sind operativ ueberholt.

## Vorrangige Forschungsgrenze nach S1-RO

Alle 14 registrierten Frischrollen besitzen eine statisch gebundene
Zielrealisierung. Alte S1-JZ-Privatzustaende bleiben ausgeschlossen. Die
Kantenkanonisierungen fuer B3-B6/M4 und die M2-Geometriekanonisierung werden
nur ueber vollstaendige strukturelle Identitaet verbunden und bleiben als
Digestrollen getrennt.

Rollenfabrik und zugehoerige Tests sind noch nicht implementiert. Als genau
ein Anschluss ist S1-RP innerhalb der beiden bereits angelegten Fabrikdateien
zulaessig. Testausfuehrung, Adapter, Matrix und Feldlauf bleiben gesperrt.
Siehe
[`S1-RO`](S1RO_STATISCHER_ROLLENWEISER_REALISIERUNGS_TYPBINDUNGS_UND_DIGESTBRUECKENVERTRAG.md).

Die nachfolgenden aelteren Grenzen bleiben chronologischer Nachweisbestand.
Ihre Weiterfreigaben sind operativ ueberholt.

## Vorrangige Forschungsgrenze nach S1-RN

Manifestconsumer und gemeinsame Vier-Knoten-Nullfeldfabrik sind nach 16 von
16 bestandenen fokussierten Tests technisch abgenommen. Die Abnahme umfasst
nur strikte Manifestvalidierung und Konstruktion des gemeinsamen Feldes bei
Takt null.

Private Rollenstatus, native Typuebersetzungen und Kanten-Digestbruecke sind
noch nicht implementiert oder getestet. Als genau ein Anschluss ist S1-RO
fuer ihren statischen Realisierungsvertrag zulaessig. Adapter, Matrix und
Feldlauf bleiben gesperrt. Siehe
[`S1-RN`](S1RN_FOKUSSIERTER_TESTLAUF_UND_TECHNISCHE_ABNAHME_MANIFESTCONSUMER_NULLFELDFABRIK.md).

Die nachfolgenden aelteren Grenzen bleiben chronologischer Nachweisbestand.
Ihre Weiterfreigaben sind operativ ueberholt.

## Vorrangige Forschungsgrenze nach S1-RM

Der unveraenderliche Manifestconsumer und die gemeinsame technische
Vier-Knoten-Nullfeldfabrik sind implementiert. Die Implementierung besitzt
keinen rollenprivaten Baupfad und fuehrt keine Feldgleichung aus. Die beiden
gebundenen Testmodule enthalten zusammen 16 noch nicht ausgefuehrte Tests.

Als genau ein Anschluss ist S1-RN fuer den fokussierten technischen Testlauf
dieser beiden Module zulaessig. Allgemeiner Testbestand, Rollenfabriken,
Adapteranschluss, Matrixzellen und Feldlauf bleiben gesperrt. Siehe
[`S1-RM`](S1RM_IMPLEMENTIERUNG_MANIFESTCONSUMER_UND_VIER_KNOTEN_NULLFELDFABRIK.md).

Die nachfolgenden aelteren Grenzen bleiben chronologischer Nachweisbestand.
Ihre Weiterfreigaben sind operativ ueberholt.

## Vorrangige Forschungsgrenze nach S1-RL

S1-RL bindet nur den technischen Einfuegepunkt fuer den unveraenderten
S1-RK-Manifestbestand. Zulaessig sind spaeter genau zwei neue
Produktionsmodule und zwei fokussierte Testmodule. Gemeinsames Nullfeld,
rollenprivate Frischformen und beide Kanten-Digestrollen bleiben strikt
getrennt.

Noch sind weder Consumer noch Fabriken implementiert. Registrierung,
Adapteranschluss, Testausfuehrung, Matrix und Feldlauf bleiben gesperrt. Als
genau ein Anschluss ist S1-RM fuer Manifestconsumer und gemeinsame
Vier-Knoten-Nullfeldfabrik zulaessig. Siehe
[`S1-RL`](S1RL_STATISCHER_REGISTRIERUNGS_FRISCHFABRIK_MANIFESTCONSUMER_UND_ABNAHMEBUDGETVERTRAG.md).

Die nachfolgenden aelteren Grenzen bleiben chronologischer Nachweisbestand.
Ihre Weiterfreigaben sind operativ ueberholt.

## Vorrangige Forschungsgrenze nach S1-RK

Das kanonische Vier-Knoten-Frischmanifest besitzt reproduzierbare Digests
und bestandene Queridentitaeten. Dieser Stand ist ausschliesslich statische
Registrierungsgrundlage; er ist noch kein ausfuehrbarer Feld- oder
Baselinebestand.

Als genau ein Anschluss ist S1-RL fuer den statischen Einfuegepunkt-,
Manifestconsumer- und Abnahmebudgetvertrag zulaessig. Siehe
[`S1-RK`](S1RK_STATISCHER_MATERIALISIERUNGS_DIGESTBERECHNUNGS_UND_QUERIDENTITAETSAUDIT_S1RJ_FRISCHMANIFEST.md).

Die nachfolgenden aelteren Grenzen bleiben chronologischer Nachweisbestand.
Ihre Weiterfreigaben sind operativ ueberholt.

## Vorrangige Forschungsgrenze nach S1-RJ

Die Vier-Knoten-Frischformen sind kanonisch als getrennte Praeimages
gebunden. Aeussere A/B/C/D-Rollen bleiben ausserhalb des Modellkerns; der
oeffentliche Frischpayload bleibt fuer alle 224 Pflichtzellen gleich;
rollenprivate Zustaende bleiben vollstaendig getrennt.

Noch existieren weder Digestmanifest noch registrierte Geometrie oder
Frischfabriken. Als genau ein Anschluss ist S1-RK fuer die statische
Materialisierung und Queridentitaetspruefung zulaessig. Siehe
[`S1-RJ`](S1RJ_STATISCHER_KANONISCHER_PAYLOAD_UND_DIGESTPRAEIMAGEVERTRAG_VIER_KNOTEN_FRISCHFORMEN.md).

Die nachfolgenden aelteren Grenzen bleiben chronologischer Nachweisbestand.
Ihre Weiterfreigaben sind operativ ueberholt.

## Vorrangige Forschungsgrenze nach S1-RI

Der primaere B1/M4-Drei-Kanten-Ausgangsbestand ist numerisch gebunden: M4
traegt pro Kante `0.2` leitend und `0.1` refraktaer; B1 projiziert daraus pro
Kante die feste Rate `1.1`. Lokale und globale Erhaltungswerte sind
vollstaendig abgeleitet.

Die Auswahl gilt nur fuer die Vier-Knoten-Offenlinie. Alternative globale
Teilung und Nullinitialisierung erhalten keine Pflichtmatrixrolle. Digests,
Registrierung, Implementierung und Ausfuehrung bleiben gesperrt.

Als genau ein Anschluss ist S1-RJ fuer den statischen kanonischen Payload-
und Digestpraeimagevertrag zulaessig. Siehe
[`S1-RI`](S1RI_STATISCHER_AUSWAHL_UND_EXAKTER_WERTABLEITUNGSVERTRAG_LOKALE_B1_M4_KANTENWERTTREUE.md).

Die nachfolgenden aelteren Grenzen bleiben chronologischer Nachweisbestand.
Ihre Weiterfreigaben sind operativ ueberholt.

## Vorrangige Forschungsgrenze nach S1-RH

Lokale Kantenwerttreue ist nach dem statischen Vergleich die einzige noch
primaer geeignete B1/M4-Erweiterungsinvariante. Globale Budgetteilung
veraendert die lokale Feldkopplung; Nullinitialisierung bleibt eine
Negativkontrolle ohne Fixed-Adapter-Aufschlag.

MINI_DIO begruendet nur die Pflicht, Geometrie und lokale Kopplung als
getrennte Ursachen zu kontrollieren. Seine Gewichte, Observer und Befunde
werden nicht uebertragen. Die lokale Option ist noch nicht formal
ausgewaehlt; Digests, Registrierung, Implementierung und Ausfuehrung bleiben
gesperrt.

Als genau ein Anschluss ist S1-RI fuer den statischen Auswahl- und exakten
Wertableitungsvertrag zulaessig. Siehe
[`S1-RH`](S1RH_STATISCHER_GEOMETRIEERWEITERUNGSINVARIANTENVERGLEICH_B1_M4_DREI_KANTEN_AUSGANGSBESTAND.md).

Die nachfolgenden aelteren Grenzen bleiben chronologischer Nachweisbestand.
Ihre Weiterfreigaben sind operativ ueberholt.

## Vorrangige Forschungsgrenze nach S1-RG

B3-B6-Viertelmassen sowie M4-Knotenkapazitaet und -Dynamikraten sind aus
akzeptierten Quellen eindeutig ableitbar. Der initiale Drei-Kanten-Bestand
von M4 und die daraus folgenden B1-Raten sind nicht eindeutig bestimmt.

Historische Profilwerte duerfen nicht als allgemeine Vier-Knoten-Regel
kopiert werden. B1 und M4 duerfen keine getrennten Ausgangsquellen erhalten.
Registrierung, Digests, Implementierung und Ausfuehrung bleiben gesperrt.

Als genau ein Anschluss ist S1-RH fuer den statischen Vergleich gemeinsamer
Geometrieerweiterungsinvarianten zulaessig. Siehe
[`S1-RG`](S1RG_STATISCHER_WERTQUELLEN_UND_EINDEUTIGER_ABLEITBARKEITSAUDIT_VIER_KNOTEN_FRISCHPAYLOADS.md).

Die nachfolgenden aelteren Grenzen bleiben chronologischer Nachweisbestand.
Ihre Weiterfreigaben sind operativ ueberholt.

## Vorrangige Forschungsgrenze nach S1-RF

Die Vier-Knoten-Identitaet, Rollenabbildung, Spiegelung, Dock- und
Carrierordnung sowie alle oeffentlichen und privaten Frischzustandsformen
sind statisch gebunden. Modellkerne duerfen den getrennten A/B/C/D-
Rollenmappingdigest nicht erhalten.

Noch nicht gebunden sind B1-Drei-Kanten-Raten, B3-B6-M-Frischmassen und die
numerischen M4-Kapazitaets- und Kantenressourcen. Freie Auswahl, Retuning,
Digestberechnung, Implementierung und Ausfuehrung bleiben gesperrt.

Als genau ein Anschluss ist S1-RG fuer den statischen Wertquellen- und
eindeutigen Ableitbarkeitsaudit zulaessig. Siehe
[`S1-RF`](S1RF_STATISCHER_VIER_KNOTEN_IDENTITAETS_ROLLEN_DOCK_FRISCHZUSTANDS_UND_A2_M4_ERWEITERUNGSPFLICHTENVERTRAG.md).

Die nachfolgenden aelteren Grenzen bleiben chronologischer Nachweisbestand.
Ihre Weiterfreigaben sind operativ ueberholt.

## Vorrangige Forschungsgrenze nach S1-RE

Als minimale gemeinsame S1-PZ-Klasse ist ausschliesslich die offene
Vier-Knoten-Linie `B_LOCAL - A_FOCAL - D_CONTROL - C_REMOTE` ausgewaehlt.
Sie trennt lokale und entfernte Geschichte bei geometrisch gleichen B/C-
Endpunkten. D bleibt technischer Kontrollort ohne eigene Expositionsrolle.

Die Auswahl ist noch keine Registrierung. A2 darf nicht mit den heutigen
S1-JV-Zeilen oder dem Drei-Knoten-B1-Payload auf vier Knoten erweitert
werden. M4 darf keine historische Anatomie uebernehmen. Neue Gleichungen,
Konfigurationsaenderungen, Implementierungen und Ausfuehrungen bleiben
gesperrt.

Als genau ein Anschluss ist S1-RF fuer den statischen Vier-Knoten-
Identitaets-, Rollen-, Dock-, Frischzustands- und A2/M4-
Erweiterungspflichtenvertrag zulaessig. Siehe
[`S1-RE`](S1RE_STATISCHER_MINIMALGEOMETRIEKLASSEN_UND_A2_M4_MAPPINGFOLGENAUDIT.md).

Die nachfolgenden aelteren Grenzen bleiben chronologischer Nachweisbestand.
Ihre Weiterfreigaben sind operativ ueberholt.

## Vorrangige Forschungsgrenze nach S1-RD

Die vorhandene S1-JV-Drei-Knoten-Offenlinie darf nicht fuer die gemeinsame
S1-PZ-Matrix registriert werden. Keine A/B/C-Zuordnung bietet gleichzeitig
direkte A-B-Nachbarschaft, nichtdirekte A-C-Trennung und geometrisch
angepasste B/C-Orte.

Getrennte Carrier erlauben zwar wert- und zeitgleiche B/C-Inputs. Die
oeffentliche Nullfrischprojektion ist ebenfalls fuer alle 14 Modellrollen
kompatibel. Beides kompensiert keine unterschiedliche Grad- oder Randlage
waehrend der getragenen Geschichte.

Mit der aktuellen Geometriemappingmenge bleiben A2, M4 und die gesamte
S1-RA-Matrix gesperrt. Als genau ein Anschluss ist S1-RE fuer den statischen
Minimalgeometrieklassen- und A2/M4-Mappingfolgenaudit zulaessig. Siehe
[`S1-RD`](S1RD_STATISCHER_DREI_KNOTEN_ABC_GEOMETRIE_LASTANPASSUNGS_UND_FRISCHPROJEKTIONS_KOMPATIBILITAETSAUDIT.md).

Die nachfolgenden aelteren Grenzen bleiben chronologischer Nachweisbestand.
Ihre Weiterfreigaben sind operativ ueberholt.

## Vorrangige Forschungsgrenze nach S1-RC

Eine Mehrkanten-T1-Laufzeitprojektion ist fuer M4 gesperrt. DTS-1 fuehrt
Kapazitaet pro Knoten und Kantenressourcen ohne eigene Kantenkapazitaet; eine
T1-Kopie je Kante waere daher nicht eindeutig und koennte freie Ressource
doppelt zaehlen.

Als passive M4-Erhaltungspruefung gelten ausschliesslich die vorhandenen
DTS-1-Knotenledger mit halben Kantenanteilen und das globale Ledger mit jeder
Kante genau einmal. T1 bleibt externe eingefrorene Ein-Kanten-Gegenbaseline
und Testfixture. Es wird nicht als zweiter M4-Zustand, Matrixarm oder
Checkpoint verwendet.

Es gibt keine Bruecken-, Geometrie-, Implementierungs- oder
Ausfuehrungsfreigabe. Als genau ein Anschluss ist S1-RD fuer den statischen
Drei-Knoten-A/B/C-Geometrie-, Lastanpassungs- und
Frischprojektions-Kompatibilitaetsaudit zulaessig. Siehe
[`S1-RC`](S1RC_STATISCHER_M4_T1_STRUKTURPROJEKTIONS_ERHALTUNGS_UND_NICHTDOPPELZAEHLUNGSVERTRAG.md).

Die nachfolgenden aelteren Grenzen bleiben chronologischer Nachweisbestand.
Ihre Weiterfreigaben sind operativ ueberholt.

## Vorrangige Forschungsgrenze nach S1-RB

A2/B1-B6 besitzt profilblinde Intervallkerne mit vollstaendigen Ausgaben,
aber noch keine S1-QZ-neutrale Frisch-, Invocation-, Receipt- und
Fehlerhuelle. Die vorhandenen S1-JO-/S1-JZ-/S1-K*-Aussenpfade bleiben wegen
ihrer historischen Profilbindung ausgeschlossen.

M4 kann im gekoppelten DTS-1-Kern normale Kontakt- und Nullkontaktintervalle
mit derselben festen Dynamik tragen. Recovery-on/off-Sidecars sind dafuer
nicht zulaessig oder erforderlich. Die allgemeine T1-Strukturvalidierung ist
jedoch offen, weil der Bestand nur eine lokale Ein-Kanten-Projektion besitzt
und eine naive Mehrkantenabbildung freie Knotenkapazitaet doppelt zaehlen
koennte.

Es gibt keine Bruecken-, Matrix-, Test- oder Ausfuehrungsfreigabe. Als genau
ein Anschluss ist S1-RC fuer den statischen M4-T1-Strukturprojektions-,
Erhaltungs- und Nichtdoppelzaehlungsvertrag zulaessig. Siehe
[`S1-RB`](S1RB_STATISCHER_A2_B1_B6_UND_M4_BRUECKENKOMPATIBILITAETSAUDIT_GEGEN_S1QZ_S1RA.md).

Die nachfolgenden aelteren Grenzen bleiben chronologischer Nachweisbestand.
Ihre Weiterfreigaben sind operativ ueberholt.

## Vorrangige Forschungsgrenze nach S1-RA

S1-RA bindet eine statische Matrix aus 14 Baseline-Modellrollen und 16
getrennten Expositionsrepliken. Die daraus abgeleiteten 224 Zellen und 532
passiven Beobachtungsrecords sind Vollstaendigkeitsrollen, keine
Ausfuehrungsfreigabe und kein Feldschrittbudget.

Jede Zelle besitzt einen eigenen Frischzustand und eine lueckenlose
Carrykette. Oeffentliche Ereignisprovenienz ist modelluebergreifend gleich;
private Zustaende bleiben rollengetrennt. Das Paket publiziert nur ein
vollstaendiges Gesamtresultat oder `BASELINE_PACKAGE_NOT_COMPUTABLE`, niemals
Teilkontraste.

Konkrete Inputs, Geometrie, Zeiten, Parameter, Comparator, Implementierung
und Lauf bleiben gesperrt. Als genau ein Anschluss ist S1-RB fuer den
statischen A2/B1-B6- und M4-Brueckenkompatibilitaetsaudit zulaessig. Siehe
[`S1-RA`](S1RA_STATISCHER_PFLICHTBASELINEPAKET_ARM_FAMILIEN_CHECKPOINTMATRIX_UND_ATOMARER_GESAMTRESULTATBUENDELVERTRAG.md).

Die nachfolgenden aelteren Grenzen bleiben chronologischer Nachweisbestand.
Ihre Weiterfreigaben sind operativ ueberholt.

## Vorrangige Forschungsgrenze nach S1-QZ

S1-QZ bindet ausschliesslich die gemeinsame aeussere Baselinehuelle. Die
Modellrollen, Expositionsrepliken, Frischzustaende, Felder und privaten
Carries bleiben getrennt. Ein Baselinekern sieht nur technische
Intervallinputs; S1-PZ-Rollen verbleiben in der Orchestrierung.

Ein erfolgreicher Intervallschritt muss Folgefeld und Privatcarry atomar
liefern. Align verbraucht keine Feldzeit und erhaelt Privatstatus bitgenau;
Observe schreibt nichts fort. A2 und M4 duerfen nur bei exakter
Bestandskompatibilitaet ueber neutrale Bruecken angeschlossen werden.

Es gibt keine Geometrie-, Parameter-, Matrix-, Comparator-, Implementierungs-
oder Ausfuehrungsfreigabe. Als genau ein Anschluss ist S1-RA fuer den
statischen Arm-/Familien-/Checkpointmatrix- und atomaren
Gesamtresultatbuendelvertrag zulaessig. Siehe
[`S1-QZ`](S1QZ_STATISCHER_GEMEINSAMER_BASELINEARM_CARRY_UND_S1PZ_LEBENSZYKLUS_HUELLENVERTRAG.md).

Die nachfolgenden aelteren Grenzen bleiben chronologischer Nachweisbestand.
Ihre Weiterfreigaben sind operativ ueberholt.

## Vorrangige Forschungsgrenze nach S1-QY

S1-QY aendert keinen Feldkern und keine Runtime. Der Audit klassifiziert nur
die Anschlusslage des Pflichtbaselinepakets. A0, A1, A3-NORM, M1, M2 und M5
besitzen wiederverwendbare Feldpfade; A2/B1-B6 und M4 duerfen nur ueber neue
modellneutrale Bruecken an S1-PZ angeschlossen werden.

Ein gemeinsames Arm-/Carryprotokoll, die ausfuehrbare S1-PZ-Huelle, eine
aktuelle atomare Matrix, das M3-Reduktionsschema und der passive
S1-QA-Comparator fehlen. Alte DTS-1-Profilorchestratoren, Sidecars und die
historische 24-Fall-Matrix bleiben ausgeschlossen. Daher gibt es keine
Implementierungs-, Test-, Lauf- oder Ergebnisfreigabe.

Als genau ein Anschluss ist S1-QZ fuer den statischen gemeinsamen
Baselinearm-, Carry- und S1-PZ-Lebenszyklus-Huellenvertrag zulaessig. Siehe
[`S1-QY`](S1QY_STATISCHER_PFLICHTBASELINEPAKET_LEBENSZYKLUS_MATRIX_COMPARATOR_BESTANDS_ANSCHLUSS_UND_LUECKENAUDIT.md).

Die nachfolgenden aelteren Grenzen bleiben chronologischer Nachweisbestand.
Ihre Weiterfreigaben sind operativ ueberholt.

## Vorrangige Forschungsgrenze nach S1-QX

Der private M2-Pufferkompositor ist in genau einem neuen Produktionsmodul
umgesetzt. Zwei neue Testdateien binden die kanonischen Fixtures, 25
Testmethoden und 18 kontrollierte Fehlermutationen.

Der einmalige kombinierte Abnahmelauf bestand 124 Tests in 40,158 Sekunden.
DELAY und REPLAY verwenden dieselbe Kapazitaet zwei, dieselbe aktuelle
A1-S-Evidence und getrennte private Frischzustaende. Die registrierte
Quellfolge ist bis `P3` identisch und trennt sich erstmals an `P4`. Finales H,
Perzeption und Feldzeit bleiben in jedem Intervall am aktuellen einmaligen
A1-Vorschlag. Fehler liefern weder Feld noch Pufferfolgezustand als
Teiloutput.

Aktive API, primaerer Feldkern, Runtime, Runner und Orchestrator bleiben
unveraendert. M2 ist technische Baselineinfrastruktur und kein
Kandidatenbefund. Als genau ein Anschluss ist S1-QY fuer einen statischen
Bestands-, Anschluss- und Lueckenaudit der gemeinsamen
Pflichtbaselinepaket-Lebenszyklus-, Matrix- und Comparatoroberflaeche
zulaessig. Keine Implementierung oder Ausfuehrung.

Die nachfolgenden aelteren Grenzen bleiben chronologischer Nachweisbestand.
Ihre Weiterfreigaben sind operativ ueberholt.

## Vorrangige Forschungsgrenze nach S1-QW

S1-QW autorisiert noch keine Umsetzung, bindet aber deren vollstaendige
Grenze. S1-QX darf genau ein privates M2-Kompositormodul und zwei zugehoerige
Testdateien neu anlegen. Alle vorhandenen Produktions-, API-, Runtime-,
Runner-, Root- und Kandidatendateien bleiben unveraendert.

Der Kompositor muss exakt die S1-QV-Registrierung, zwei getrennte
Moduskonfigurationen, kanonische A1-S-Records, den begrenzten Puffer,
positionsgebundene Auswahl, vollstaendige S-Ersetzung, aktuelles A1-H und
genau eine Feldzeitfortschreibung pro Intervall belegen. Fehler sperren Feld
und gesamten M2-Folgezustand atomar.

Gebunden sind 18 Fehlercodes und Mutationsklassen, 25 neue Tests und genau ein
kombinierter Testprozess. Als genau ein Anschluss ist S1-QX fuer die
begrenzte Implementierung und technische Einmalabnahme zulaessig. Siehe
[`S1-QW`](S1QW_STATISCHER_M2_ZUSTANDS_KOMPOSITOR_FEHLERCODE_UND_TESTBUDGETVERTRAG.md).

Die nachfolgenden aelteren Grenzen bleiben chronologischer Nachweisbestand.
Ihre Weiterfreigaben sind operativ ueberholt.

## Vorrangige Forschungsgrenze nach S1-QV

Beide M2-Modi muessen exakt `K = 2` Records tragen. Die einzige registrierte
Minimalachse lautet `P0..P4` mit den aktuellen Records `A..E`. Bis
einschliesslich `P3` sind die Ausgabequellen beider Modi identisch. Die erste
zulaessige Divergenz liegt an `P4`: Delay selektiert Record `C`, Replay ist
erschoepft und verwendet aktuelles `E`.

Recorddigests muessen paarweise verschieden sein; `S_A != S_B` prueft die
Prefixordnung und `S_C != S_E` die sichtbare Divergenz. Die kanonische
Registrierung traegt den Digest
`6abe7781ffd1d1b238b5e3302960b41d8e98dc880432869187f8eafdb8b95810`.

Es gibt keine Implementierungs- oder Ausfuehrungsfreigabe. Als genau ein
Anschluss ist S1-QW fuer den statischen M2-Zustands-, Kompositor-,
Fehlercode- und Testbudgetvertrag zulaessig. Siehe
[`S1-QV`](S1QV_STATISCHER_M2_KAPAZITAETS_POSITIONS_UND_DIVERGENZREGISTRIERUNGSVERTRAG.md).

Die nachfolgenden aelteren Grenzen bleiben chronologischer Nachweisbestand.
Ihre Weiterfreigaben sind operativ ueberholt.

## Vorrangige Forschungsgrenze nach S1-QU

M2 ist auf `DELAY` und einmaliges `REPLAY` mit einer gemeinsamen positiven,
endlichen und noch unregistrierten Recordkapazitaet `K` begrenzt. Der
Pufferrecord enthaelt nur kanonische A1-S-Evidence und Quelldigests. Rohdaten,
vollstaendige Felder, H, Kandidaten-, Observer- und Orchestrierungsdaten sind
im M2-Zustand gesperrt.

`DELAY` bleibt rollend. `REPLAY` darf ausschliesslich die positionsbestimmten
Phasen `CAPTURE`, `EMIT` und `EXHAUSTED` einmal durchlaufen. Aktuelles A1-S
ist der einzige Warm-up- und Erschoepfungsfallback. Finales H, Perzeption und
Feldzeit bleiben am genau einmal fortgeschriebenen aktuellen A1-Vorschlag.

Es gibt keine Implementierungs- oder Ausfuehrungsfreigabe. Als genau ein
Anschluss ist S1-QV fuer die statische Registrierung von `K`, einer kleinsten
endlichen Recordfolge und der positionsgebundenen Modusdivergenz zulaessig.
Scheitert diese Trennung, wird `REPLAY` gestoppt. Siehe
[`S1-QU`](S1QU_STATISCHER_M2_MODUSFAMILIEN_EINGABERECORD_PUFFERANATOMIE_UND_FALSIFIKATIONSVERTRAG.md).

Die nachfolgenden aelteren Grenzen bleiben chronologischer Nachweisbestand.
Ihre Weiterfreigaben sind operativ ueberholt.

## Vorrangige Forschungsgrenze nach S1-QT

Im Projektbestand existiert kein zulaessiger vollstaendiger M2-Delay- oder
Replaypuffer. Vorhandene Eingabe- und Feldkompositionsprimitive duerfen
spaeter nur unter einer neuen privaten, endlichen und atomaren M2-Huelle
wiederverwendet werden. Rezeptor- oder Medienrohdaten, bestehende
Feldzustaende und historische Replaypfade werden nicht als Pufferkern
uebernommen.

Ein fester rollender Delay besitzt eine eigenstaendige technische
Gegenprognose. Prefix-Replay bleibt nur unter der fail-closed-Bedingung
separat, dass Aufnahmegrenze, Ausgabestart, feste Ordnung und Erschoepfung
rein kausal vorregistriert werden. Andernfalls ist es keine zweite Rolle.

M2 bleibt private Gegenbaseline; Feldkern, API, Runtime, Runner und
Orchestrator bleiben unveraendert. Als genau ein Anschluss ist S1-QU fuer
einen statischen M2-Modusfamilien-, Eingaberecord-, Pufferanatomie- und
Falsifikationsvertrag zulaessig. Keine Gleichung, Parameterwahl,
Implementierung oder Ausfuehrung. Siehe
[`S1-QT`](S1QT_STATISCHER_M2_DELAY_REPLAYPUFFER_BESTANDS_NICHTDUPLIZIERUNGS_UND_FALSIFIKATIONSAUDIT.md).

Die nachfolgenden aelteren Grenzen bleiben chronologischer Nachweisbestand.
Ihre Weiterfreigaben sind operativ ueberholt.

## Vorrangige Forschungsgrenze nach S1-QS

Der private M1-Zweispurkompositor ist in genau einem neuen Produktionsmodul
umgesetzt. Zwei neue Testdateien binden die kanonischen Fixtures, 20
Testmethoden und 16 kontrollierte Fehlermutationen.

Der einmalige kombinierte Abnahmelauf bestand 99 Tests in 50,161 Sekunden.
FAST und SLOW verwenden getrennte W7-N-`LEAK`-Zustaende, dieselbe A1-S-
Evidence und denselben Intervallwert. Finales S ist exakt ihr lokaler
gleichgewichteter Mittelwert; H und Feldzeit bleiben am einmaligen
A1-Vorschlag. Fehler liefern weder Feld noch Bankfolgezustand als Teiloutput.

Aktive API, primaerer Feldkern, Runtime, Runner und Orchestrator bleiben
unveraendert. M1 ist technische Baselineinfrastruktur und kein
Kandidatenbefund. Als genau ein Anschluss ist S1-QT fuer einen statischen
M2-Delay-/Replaypuffer-Bestands-, Nichtduplizierungs- und
Falsifikationsaudit zulaessig. Keine Implementierung oder Ausfuehrung.

Die nachfolgenden aelteren Grenzen bleiben chronologischer Nachweisbestand.
Ihre Weiterfreigaben sind operativ ueberholt.

## Vorrangige Forschungsgrenze nach S1-QR

S1-QR autorisiert noch keine Umsetzung, bindet aber deren vollstaendige
Grenze. S1-QS darf genau ein privates M1-Kompositormodul und zwei zugehoerige
Testdateien neu anlegen. Alle vorhandenen Produktions-, API-, Runtime-,
Runner-, Root- und Kandidatendateien bleiben unveraendert.

Der Kompositor muss exakt die S1-QQ-Konfiguration, zwei getrennte
W7-N-`LEAK`-Zustaende, denselben A1-S-Eingang, den gleichgewichteten lokalen
Mittelwert, vollstaendige S-Ersetzung, unveraendertes H und genau eine
Feldzeitfortschreibung belegen. Fehler sperren Feld und gesamten
Bankfolgezustand atomar.

Gebunden sind sechzehn Fehlercodes, sechzehn Mutationsklassen, zwanzig neue
Tests und genau ein kombinierter Testprozess. Als genau ein Anschluss ist
S1-QS fuer die begrenzte Implementierung und technische Einmalabnahme
zulaessig. Siehe
[`S1-QR`](S1QR_STATISCHER_M1_ZUSTANDS_KOMPOSITOR_FEHLERCODE_UND_TESTBUDGETVERTRAG.md).

Die nachfolgenden aelteren Grenzen bleiben chronologischer Nachweisbestand.
Ihre Weiterfreigaben sind operativ ueberholt.

## Vorrangige Forschungsgrenze nach S1-QQ

Die M1-Zeitrollen sind auf `FAST = 1,0 s` und `SLOW = 4,0 s` festgelegt. Die
einzige zulaessige kumulative Gap-Achse lautet `G1 = 1,0 s`, `G4 = 4,0 s`,
`G8 = 8,0 s` und muss als ein lueckenloser Carry ausgefuehrt werden.

Der kanonische Registrierungsdigest ist
`141b552532f0f43449e2d92c2d09274eae6acb66b224cd287b12b3a6d8d63f3b`.
Historische E1-Zustaende, Mechaniken, Profile und Ergebnisse sind weiterhin
gesperrt; nur die vorhandenen technischen Zeitwerte wurden wiederverwendet.

Die analytische Drei-Punkt-Referenz ist strukturell von einer einzelnen
festen Exponentialspur unterscheidbar. Sie ist kein Feldbefund. Es gibt noch
keine M1-Implementierungs- oder Ausfuehrungsfreigabe. Als genau ein Anschluss
ist S1-QR fuer den statischen M1-Zustands-, Kompositor-, Fehlercode- und
Testbudgetvertrag zulaessig. Siehe
[`S1-QQ`](S1QQ_STATISCHER_M1_ZEITROLLENREGISTRIERUNGS_UND_GAP_IDENTIFIZIERBARKEITSVERTRAG.md).

Die nachfolgenden aelteren Grenzen bleiben chronologischer Nachweisbestand.
Ihre Weiterfreigaben sind operativ ueberholt.

## Vorrangige Forschungsgrenze nach S1-QP

M1 ist auf genau zwei unabhaengige W7-N-`LEAK`-Spuren begrenzt. Ihre feste
Ordnung ist `(FAST, SLOW)`, beide sehen dieselbe A1-S-Evidence und es muss
`0 < tau_FAST < tau_SLOW` gelten. Die konkrete Zeitwertregistrierung fehlt
noch.

Der einzige zulaessige Readout ist der punktweise gleichgewichtete Mittelwert
beider direkten Spurausgaben. Er ersetzt finales S; H und Feldzeit bleiben am
einmaligen A1-Vorschlag. Andere Gewichte, Kopplung, globale Normierung,
Ressourcenrollen, Puffer, Delay und Replay sind gesperrt.

Es gibt keine M1-Implementierungs- oder Ausfuehrungsfreigabe. Als genau ein
Anschluss ist S1-QQ fuer einen statischen M1-Zeitrollenregistrierungs- und
Gap-Identifizierbarkeitsvertrag zulaessig. Sind zwei Rollen auf der
vorhandenen Zeitachse nicht unterscheidbar, wird M1 gestoppt. Siehe
[`S1-QP`](S1QP_STATISCHER_M1_MINIMALFAMILIEN_SPURANATOMIE_READOUT_UND_FALSIFIKATIONSVERTRAG.md).

Die nachfolgenden aelteren Grenzen bleiben chronologischer Nachweisbestand.
Ihre Weiterfreigaben sind operativ ueberholt.

## Vorrangige Forschungsgrenze nach S1-QO

M1 bleibt als feste parallele Mehrzeitskalen-Gegenbaseline strukturell
eigenstaendig. Zulaessig sind nur unabhaengige passive Spuren, die denselben
lokalen Eingang sehen, keine Ressourcen teilen und mit einer ueber alle Arme
festen Bank- und Readoutkonfiguration getragen werden.

Vorhandene Einzel-Leaky-Kerne duerfen spaeter als Primitive geprueft werden,
sind aber noch kein M1. Der geschlossene lokale Zwei-Zeitskalen-Kandidat,
gekoppelte Stufen, Stabilisierung, Kapazitaetsbudget, globale Normierung,
Delay und Replay sind fuer M1 gesperrt.

Es gibt keine M1-Implementierungs- oder Ausfuehrungsfreigabe. Als genau ein
Anschluss ist S1-QP fuer einen statischen M1-Minimalfamilien-, Spuranatomie-,
Readout- und Falsifikationsvertrag zulaessig. Bleibt dabei keine kleinste
endliche nichtduplizierte Familie uebrig, wird M1 gestoppt. Siehe
[`S1-QO`](S1QO_STATISCHER_M1_MEHRZEITSKALENBANK_BESTANDS_NICHTDUPLIZIERUNGS_UND_FALSIFIKATIONSAUDIT.md).

Die nachfolgenden aelteren Grenzen bleiben chronologischer Nachweisbestand.
Ihre Weiterfreigaben sind operativ ueberholt.

## Vorrangige Forschungsgrenze nach S1-QN

Der private M5_DIRECT-`REPLACE_S`-Kompositor und der modellneutrale
A1/`REPLACE_S`-Hilfskern sind technisch umgesetzt. M5_DIRECT darf
ausschliesslich die registrierte W7-N-`LEAK`-Spezifikation, einen lokalen
Zustand pro Feldort und dessen direkten signed Output verwenden. Nur S wird
ersetzt; H und Feldzeit bleiben vollstaendig an A1 gebunden.

Der einmalige kombinierte Abnahmelauf bestand 79 Tests in 40,017 Sekunden.
Genau 18 davon pruefen M5_DIRECT einschliesslich aller 14 gebundenen
Fehlermutationsklassen. Fehler liefern weder ein Feld noch einen
M5-Folgezustand als Teilergebnis. Die A3-Oberflaeche und die einbezogenen
Feldkerne blieben regressionsfrei.

Aktive API, primaerer Feldkern, Runtime, Runner und Orchestrator bleiben
unveraendert. M5_DIRECT ist technische Baselineinfrastruktur und kein
Kandidatenbefund. Das Pflichtbaselinepaket darf noch nicht ausgefuehrt
werden. Als genau ein Anschluss ist S1-QO fuer einen statischen
M1-Mehrzeitskalenbank-Bestands-, Nichtduplizierungs- und
Falsifikationsaudit zulaessig. S1-QO bindet keine Gleichung, Parameter,
Implementierung oder Ausfuehrung.

Die nachfolgenden aelteren Grenzen bleiben chronologischer Nachweisbestand.
Ihre Weiterfreigaben sind operativ ueberholt.

## Vorrangige Forschungsgrenze nach S1-QM

S1-QM begrenzt die spaetere M5_DIRECT-Umsetzung auf die registrierte
W7-N-`LEAK`-Spezifikation, genau einen lokalen Zustand pro Feldort und den
direkten signed Output als finales S. H und Feldzeit bleiben am einmaligen
A1-Fast-Vorschlag.

Ein privater modellneutraler A1/REPLACE_S-Hilfskern darf extrahiert werden,
aber keine NORM-, M5-, Receipt- oder Fehlersemantik enthalten. Die bestehende
A3-NORM-Oberflaeche und alle Digests muessen unveraendert bleiben.

Vierzehn Fehlercodes, vierzehn Mutationsklassen, achtzehn neue Tests und
genau ein kombinierter Testprozess sind statisch gebunden. Es gibt noch keine
Implementierung oder Ausfuehrung. Als genau ein Anschluss ist S1-QN fuer die
begrenzte Implementierung und technische Einmalabnahme zulaessig. Siehe
[`S1-QM`](S1QM_STATISCHER_M5_DIRECT_ZUSTANDS_KOMPOSITOR_FEHLERCODE_UND_TESTBUDGETVERTRAG.md).

Die nachfolgenden aelteren Grenzen bleiben chronologischer Nachweisbestand.
Ihre Weiterfreigaben sind operativ ueberholt.

## Vorrangige Forschungsgrenze nach S1-QL

S1-QL bindet `M5_DIRECT_LOCAL_STATE` als einzigen endlichen ausfuehrbaren
M5-Vertreter. Zulaessig sind nur der vorhandene W7-N-`LEAK`-Frischzustand,
seine lokale Fortschreibung und sein direkter signed Output. Finales S wird
funktional durch diesen Output ersetzt; H bleibt unveraendert aus A1.

SAT bleibt Observerdiagnostik, NORM bleibt global getrennt, und M5 darf keine
M1-Mehrspur, M4-Ressourcenrollen, M-/Edge-Zustaende, Puffer oder Replay lesen.
Die spaetere Aussage ist auf direkte lokale Einzustandsretention begrenzt.

Es gibt noch keine M5-Implementierungs- oder Ausfuehrungsfreigabe. Als genau
ein Anschluss ist S1-QM fuer den statischen M5_DIRECT-Zustands-, Kompositor-,
Fehlercode- und Testbudgetvertrag zulaessig. Siehe
[`S1-QL`](S1QL_STATISCHER_M5_READOUTFAMILIEN_NICHTDUPLIZIERUNGS_UND_FALSIFIKATIONSVERTRAG.md).

Die nachfolgenden aelteren Grenzen bleiben chronologischer Nachweisbestand.
Ihre Weiterfreigaben sind operativ ueberholt.

## Vorrangige Forschungsgrenze nach S1-QK

S1-QK klassifiziert W7-N `LEAK` als direkten M5-kompatiblen Unterfall. Seine
lokale A1-S-Zustandsrolle ist jedoch noch gegen die passiven H- und
M/F3-gebundenen B3-Leaky-Rollen abzugrenzen. W7-N `SAT` bleibt gestoppte
M5-Unterklasse; NORM bleibt wegen seiner globalen Outputkopplung
ausdruecklich getrennt.

Carrier-, F3- und G2/D3-Retention sind keine unveraenderten M5-Feldpfade.
Eine endliche nichtduplizierte M5-Readoutfamilie ist noch nicht gebunden.
Deshalb gibt es keine M5-Implementierungs- oder Ausfuehrungsfreigabe und das
Pflichtbaselinepaket bleibt nicht ausfuehrbar.

Als genau ein Anschluss ist S1-QL fuer den statischen
M5-Readoutfamilien-, Nichtduplizierungs- und Falsifikationsvertrag zulaessig.
Siehe
[`S1-QK`](S1QK_STATISCHER_M5_BESTANDS_NICHTDUPLIZIERUNGS_UND_FELDROLLENKOMPATIBILITAETSAUDIT.md).

Die nachfolgenden aelteren Grenzen bleiben chronologischer Nachweisbestand.
Ihre Weiterfreigaben sind operativ ueberholt.

## Vorrangige Forschungsgrenze nach S1-QJ

Der private A3-NORM-`REPLACE_S`-Kompositor ist in genau einem neuen
Produktionsmodul umgesetzt. Zwei neue Testdateien binden kanonische
In-memory-Fixtures, 18 Testmethoden und 14 kontrollierte Fehlermutationen.

Der einmalige kombinierte Abnahmelauf bestand 61 Tests in 20,080 Sekunden.
Finales S stammt vollstaendig aus dem signed NORM-Output; H und alle anderen
Feldrollen bleiben am einmal fortgeschriebenen A1-Vorschlag. Fehler liefern
weder Feld noch NORM-Folgezustand als Teilergebnis.

Aktive API, primaerer Feldkern, Runtime, Runner und Orchestrator bleiben
unveraendert. Das Pflichtbaselinepaket ist weiterhin nicht ausfuehrbar. Als
genau ein Anschluss ist S1-QK fuer den statischen M5-Bestands-,
Nichtduplizierungs- und Feldrollenkompatibilitaetsaudit zulaessig.

Die nachfolgenden aelteren Grenzen bleiben chronologischer Nachweisbestand.
Ihre Weiterfreigaben sind operativ ueberholt.

## Vorrangige Forschungsgrenze nach S1-QI

S1-QI begrenzt die spaetere A3-NORM-`REPLACE_S`-Umsetzung auf ein neues
privates Produktionsmodul und zwei fokussierte Testdateien. Die Komponente
darf nur vorhandene A1- und W7-N-Kerne verbinden, synchrone und transiente
Intervalle typisiert unterscheiden und genau ein atomar vollstaendiges Feld
plus NORM-Folgezustand liefern.

Vierzehn Fehlercodes, vierzehn isolierte Mutationsklassen und achtzehn neue
Testmethoden sind statisch gebunden. Es gibt keine Implementierung,
Ausfuehrung, API-Freigabe oder Runtimeintegration.

Als genau ein Anschluss ist S1-QJ fuer die begrenzte Implementierung und
einmalige technische Komponentenabnahme zulaessig. Siehe
[`S1-QI`](S1QI_STATISCHER_A3_NORM_REPLACE_S_KOMPOSITOR_FEHLERCODE_UND_TESTBUDGETVERTRAG.md).

Die nachfolgenden aelteren Grenzen bleiben chronologischer Nachweisbestand.
Ihre Weiterfreigaben sind operativ ueberholt.

## Vorrangige Forschungsgrenze nach S1-QH

S1-QH bindet `REPLACE_S` als einzige NORM-Feldkompositionsfamilie. Ein
interner A1-Fast-Vorschlag liefert S-Evidence und H; der danach gebildete
signed NORM-Output ersetzt ausschliesslich finales S. Dieses S wird erst im
naechsten Intervall wieder Eingabe. Es gibt genau eine Feldzeitfortschreibung
und kein aktuelles Rueckkopplungsproblem.

`SCALE_S` und `SOURCE_S` sind gestoppt. Sie wuerden neue Feldtransformation,
Kopplung, Zeitregel oder zweite Integration erfordern.

Es gibt keine neue Gleichung, Parameter, Implementierung oder Ausfuehrung.
Das Pflichtbaselinepaket bleibt nicht ausfuehrbar. Als genau ein Anschluss ist
S1-QI fuer den statischen REPLACE_S-Kompositor-, Fehlercode- und
Testbudgetvertrag vorgesehen. Siehe
[`S1-QH`](S1QH_STATISCHER_NORM_FELDKOMPOSITIONSFAMILIEN_UND_NICHTZIRKULARITAETSAUDIT.md).

Die nachfolgenden aelteren Grenzen bleiben chronologischer Nachweisbestand.
Ihre Weiterfreigaben sind operativ ueberholt.

## Vorrangige Forschungsgrenze nach S1-QG

S1-QG bindet fuer NORM genau einen lokalen Zustand pro vollstaendigem
Feldknoten. Die globale Skalierungsgrundlage und der signed Outputvektor sind
temporaere atomare Outputs, keine zusaetzlichen Carryzustaende.

NORM darf nur S beeinflussen; H bleibt die unveraenderte schnelle A1-Rolle.
Der vorhandene W7-N-Kern liefert Zustand und normalisierten Output, aber noch
keinen vollstaendigen Feldoutput. Offen sind die drei Kompositionsfamilien
`REPLACE_S`, `SCALE_S` und `SOURCE_S`.

Es gibt keine neue Gleichung, Parameter, Implementierung oder Ausfuehrung.
Das Pflichtbaselinepaket bleibt nicht ausfuehrbar. Als genau ein Anschluss ist
S1-QH fuer den statischen Feldkompositionsfamilien- und
Nichtzirkularitaetsaudit vorgesehen. Siehe
[`S1-QG`](S1QG_STATISCHER_A3_NORM_ZUSTANDSINVENTAR_NENNERPROVENIENZ_UND_FELDOUTPUTROLLENVERTRAG.md).

Die nachfolgenden aelteren Grenzen bleiben chronologischer Nachweisbestand.
Ihre Weiterfreigaben sind operativ ueberholt.

## Vorrangige Forschungsgrenze nach S1-QF

S1-QF stoppt SAT als eigenen A3-Feldarm, weil seine lokale
Einzustands-Saettigung vollstaendig in der allgemeinen M5-Retentionsklasse
liegt. Der vorhandene SAT-Kern bleibt unveraenderte Observerdiagnostik.

Als einzige A3-Feldrolle bleibt NORM. NORM prueft globale Outputskalierung
ohne lokalen Ressourcentransfer, Edge-Ledger oder zusaetzlichen globalen
Zustand. M5 bleibt ortsseparabel; NORM darf nur die S-Beitragsrolle betreffen
und keine eigene H-Dynamik einfuehren.

Es gibt keine neue Gleichung, Parameter, Implementierung oder Ausfuehrung.
Das Pflichtbaselinepaket bleibt nicht ausfuehrbar. Als genau ein Anschluss ist
S1-QG fuer den statischen A3-NORM-Zustandsinventar-, Nennerprovenienz- und
Feldoutputrollenvertrag vorgesehen. Siehe
[`S1-QF`](S1QF_STATISCHER_A3_FELDFUNKTIONS_NICHTSUBSTITUTIONS_UND_FALSIFIKATIONSVERTRAG.md).

Die nachfolgenden aelteren Grenzen bleiben chronologischer Nachweisbestand.
Ihre Weiterfreigaben sind operativ ueberholt.

## Vorrangige Forschungsgrenze nach S1-QE

S1-QE identifiziert fuer A0 einen vorhandenen, vollstaendigen und
zustandslosen Feldpfad. `receptor_projection_baseline` liest nur den aktuellen
Dockkontakt und setzt H auf null; `SharedMCMField.advance` materialisiert das
gemeinsame Feld atomar. Der Pfad bleibt eine private Gegenbaseline und wird
nicht Teil der aktiven Feld-API.

Fuer A3 existiert kein entsprechender Handoff. Die vorhandenen
Saettigungs- und Normalisierungskerne enden auf einer Observeroberflaeche.
Eine Feldabbildung muesste S- und H-Wirkung neu definieren und ist deshalb
keine reine Adapterarbeit. A3 sowie das gesamte Pflichtbaselinepaket bleiben
vorerst nicht ausfuehrbar.

Es gibt keine neue Gleichung, Parameter, Implementierung oder Ausfuehrung.
Als genau ein Anschluss ist S1-QF fuer den statischen A3-Feldfunktions-,
Nichtsubstitutions- und Falsifikationsvertrag vorgesehen. Siehe
[`S1-QE`](S1QE_STATISCHER_FELDHANDOFF_KOMPATIBILITAETSAUDIT_A0_A3.md).

Die nachfolgenden aelteren Grenzen bleiben chronologischer Nachweisbestand.
Ihre Weiterfreigaben sind operativ ueberholt.

## Vorrangige Forschungsgrenze nach S1-QD

S1-QD bindet fuer jede Pflichtbaselinerolle genau die kleinste private
Zustandsverantwortung, den unabhaengigen Frischstart, den lueckenlosen Carry
und eine atomare Ausgabegrenze. Familien-, Arm-, Ziel- und Ergebniswissen
bleibt ausserhalb der Modelle.

A0 und M3 sind zustandslos; M3 bleibt zudem ohne Feldarm. A1, A2, A3 sowie
M1, M2, M4 und M5 duerfen nur ihren jeweils registrierten vollstaendigen
Zustand tragen. Ein Adapter darf niemals eine neue Dynamik oder Rueckwirkung
als Formabbildung verbergen.

Deshalb bleiben A0 und A3 technisch offen: Ihre vorhandenen lokalen Outputs
sind noch keine vollstaendigen S1-QA-Feldresultate. Es gibt keine neue
Gleichung, Parameter, Implementierung oder Ausfuehrung. Als genau ein
Anschluss ist S1-QE fuer den statischen Feldhandoff-Kompatibilitaetsaudit von
A0 und A3 vorgesehen. Siehe
[`S1-QD`](S1QD_STATISCHER_ZUSTANDS_HANDOFF_UND_AUSGABEVERTRAG_PFLICHTBASELINEPAKET.md).

Die nachfolgenden aelteren Grenzen bleiben chronologischer Nachweisbestand.
Ihre Weiterfreigaben sind operativ ueberholt.

## Vorrangige Forschungsgrenze nach S1-QC

S1-QC bindet vier Adaptergruppen fuer vorhandene Kerne und fuenf getrennte
Abschlussrollen: Mehrzeitskalen, begrenzter Delay-/Replay-Puffer, passiver
Capacity-Clamp-Audit, eingefrorenes DTS-1/T1 und allgemeine
Einzustandsretention.

Fixed Adapter umfasst Frozen-E1, permanentes Gewicht und statische Kopplung.
G2/D3 wird nicht erneut ausgefuehrt, sondern bleibt strukturelle
Reduktionskontrolle gegen Retention, DTS und Clamp. Der Replaypuffer ist nur
eine private negative Gegenbaseline und bleibt als Kandidaten- oder
Feldkernfunktion gesperrt.

Es gibt keine neue Gleichung, Baseline, Kandidatenmechanik, Runtimeaenderung
oder Ausfuehrung. Als genau ein Anschluss ist S1-QD fuer den statischen
Zustands-, Handoff- und Ausgabevertrag des Baselinepakets vorgesehen. Siehe
[`S1-QC`](S1QC_STATISCHER_FUNKTIONS_NICHTDUPLIZIERUNGS_UND_FALSIFIKATIONSVERTRAG_PFLICHTBASELINEPAKET.md).

Die nachfolgenden aelteren Grenzen bleiben chronologischer Nachweisbestand.
Ihre Weiterfreigaben sind operativ ueberholt.

## Vorrangige Forschungsgrenze nach S1-QB

S1-QB klassifiziert die vorhandenen Pflichtbaselineoberflaechen. Der schnelle
H-Feldkern und B1 bis B6 besitzen vollstaendige Feldintervallkerne, brauchen
aber eine neue S1-PZ-Huellenbindung. Stateless, Saettigung und Normalisierung
haben noch keinen zulaessigen S1-QA-Feldhandoff.

Mehrzeitskalen, feste Verzoegerung, statische Rekurrenz, Replay und minimaler
Capacity-Clamp besitzen keinen direkt zulaessigen Lebenszykluskern. DTS-1/T1,
Retention und G2/D3 bleiben eingefrorene geschlossene Spezialkontrollen und
duerfen nicht direkt in den neuen Vergleich uebernommen werden.

Es gibt keine neue Baseline, keinen Kandidaten, keine Gleichung, Parameter,
Runtimeaenderung oder Ausfuehrung. Als genau ein Anschluss ist S1-QC fuer den
statischen Vertrag des kleinsten fehlenden Pflichtbaselinepakets vorgesehen.
Siehe
[`S1-QB`](S1QB_STATISCHER_PFLICHTBASELINE_OBERFLAECHEN_UND_INFORMATIONSAUDIT.md).

Die nachfolgenden aelteren Grenzen bleiben chronologischer Nachweisbestand.
Ihre Weiterfreigaben sind operativ ueberholt.

## Vorrangige Forschungsgrenze nach S1-QA

S1-QA bindet ausschliesslich die spaeteren passiven Beobachtungs-, Bilanz-,
Kontrast- und Comparatorrollen. Der Hauptreadout ist die vollstaendige signed
S-Fortsetzung. S/H-Angleichung, private Zustandsprovenienz, Kandidatenbilanz,
Diagnostik und Feldwirkung bleiben getrennte Evidenzrollen.

Die F/T/I/C/R/U-Gruppen werden nur als vollstaendiger Lebenszyklus und in
fester Fail-Closed-Reihenfolge bewertet. Eine Pflichtbaseline muss alle
Geschichten unter einer unveraenderten Konfiguration erhalten. Eine
unvollstaendige oder inkompatible Baseline macht den Vergleich ungueltig und
erzeugt kein positives Residuum.

Es gibt keinen Kandidaten, keine Bilanzanatomie, Gleichung, Werte,
Comparatorimplementierung, Runtimeaenderung oder Ausfuehrung. Als genau ein
Anschluss ist S1-QB fuer den statischen Pflichtbaseline-Oberflaechen- und
Informationsaudit vorgesehen. Siehe
[`S1-QA`](S1QA_STATISCHER_BEOBACHTUNGS_BILANZ_UND_LEBENSZYKLUS_COMPARATORROLLENVERTRAG.md).

Die nachfolgenden aelteren Grenzen bleiben chronologischer Nachweisbestand.
Ihre Weiterfreigaben sind operativ ueberholt.

## Vorrangige Forschungsgrenze nach S1-PZ

S1-PZ bindet ausschliesslich die modellneutrale Kausalordnung der spaeteren
S1-PX-Expositionen. A ist fokal, B lokal konkurrierend und C eine gleich
belastete nichtlokale Kontrolle. Getrennte Rollenfamilien erfassen Bildung,
Wiederholung, Interferenz, Kapazitaet, normalen kontaktfreien
Funktionsverlust und andere Wiederverwendung.

S und H werden innerhalb normaler Geschichte kausal getragen. Eine
gemeinsame Angleichung von aktuellem Eingang, S und H ist nur unmittelbar vor
einem vergleichenden Readout zulaessig und muss private Modellzustaende
bitgenau erhalten. Alle zustandsbehafteten Baselines muessen dieselbe
relevante Geschichte erhalten.

Es gibt keinen Kandidaten, keine Zustandsanatomie, Werte, Gleichung,
Parameter, Runtimeaenderung und keinen Lauf. Als genau ein Anschluss ist
S1-QA fuer den statischen Beobachtungs-, Bilanz- und
Lebenszyklus-Comparatorrollenvertrag vorgesehen. Siehe
[`S1-PZ`](S1PZ_STATISCHER_MODELLNEUTRALER_EXPOSITIONSROLLENVERTRAG_S1PX_LEBENSZYKLUS.md).

Die nachfolgenden aelteren Grenzen bleiben chronologischer Nachweisbestand.
Ihre Weiterfreigaben sind operativ ueberholt.

## Vorrangige Forschungsgrenze nach S1-PY

S1-PY ordnet das vorhandene technische Geruest als teilweise
wiederverwendbar ein. Gemeinsame S/H-Grenzen, Intervallmaterialisierung,
getrennte Expositions- und Vorzustandsrollen, sechs Baselineadapter,
Frischstarts und atomare Outputs koennen nach neuer Vertragsbindung genutzt
werden.

Nicht freigegeben sind alte DTS- oder G2-Sidecars, alte Ergebnisvektoren und
die Fortsetzung der unvollstaendigen 24-Fall-Matrix. Fuer S1-PX fehlen noch
eine vollstaendige modellneutrale Lebenszyklusexposition, mehrere
Pflichtbaseline-Bruecken und ein gemeinsamer passiver Comparator.

Es gibt weiterhin keinen Kandidaten, keine Gleichung, keine Parameter,
keine Runtimeaenderung und keinen Lauf. Als genau ein Anschluss ist S1-PZ
fuer den statischen modellneutralen Expositionsrollenvertrag vorgesehen.
Siehe
[`S1-PY`](S1PY_STATISCHER_WIEDERVERWENDBARKEITS_UND_LUECKENAUDIT_EXPOSITION_BASELINES_COMPARATOREN.md).

Die nachfolgenden aelteren Grenzen bleiben chronologischer Nachweisbestand.
Ihre Weiterfreigaben sind operativ ueberholt.

## Vorrangige Forschungsgrenze nach S1-PX

S1-PX oeffnet eine neue hypothetische MCM-Memory-Entwicklungsrichtung, ohne
eine vorhandene Faehigkeit zu behaupten. Vor jeder Kandidatenanatomie oder
Gleichung ist jetzt eine gemeinsame technische Gegenprognose gebunden:
endogene lokale Bildung, verbleibende Feldwirkung nach Eingangs- und
S/H-Angleichung, Abschwaechung, spezifische Interferenz, endliche lokale
Kapazitaet, funktionale Freigabe und andere Wiederverwendung.

Der gesamte Verlauf muss mit fairer kausaler Exposition gegen Fixed Adapter,
Frozen-E1, Leaky, Integrator, schnellen Nachhall, Replay, Normalisierung,
Capacity-Clamp, DTS-1/T1, Retentionsbaseline und G2/D3 bestehen. Die
geschlossenen Zweige werden dadurch nicht wieder geoeffnet.

Es gibt noch keinen Kandidaten, keine Gleichung, keine Parameter, keine
Runtimeaenderung und keinen Lauf. Als genau ein Anschluss ist S1-PY fuer den
statischen Wiederverwendbarkeits- und Lueckenaudit der vorhandenen
Expositions-, Baseline- und Comparatorinfrastruktur vorgesehen. Siehe
[`S1-PX`](S1PX_STATISCHER_FUNKTIONS_UND_FALSIFIKATIONSVERTRAG_HYPOTHETISCHE_MCM_MEMORY.md).

Die nachfolgenden aelteren Grenzen bleiben als chronologischer
Nachweisbestand erhalten. Ihre damaligen Pausen- und Weiterfreigaben sind
durch S1-PX operativ ueberholt.

## Vorrangiger Abschlussstand nach S1-PW

S1-PW findet unter 305 Root-Verbraucherdateien keine ungedeckte
Lazy-Verhaltensklasse. Kein internes Paketmodul konsumiert die Root-API. Ein
weiterer Regressionstest ist nicht erforderlich und nicht freigegeben.

Die technische Aktivkern-, Root- und Archivgrenzenkonsolidierung ist
abgeschlossen. Die Substratforschung bleibt mangels eigener falsifizierbarer
Gegenprognose pausiert. Ein neuer Abschnitt benoetigt eine konkrete neue
Engineeringanforderung oder eine ausdrueckliche fachliche Richtungsentscheidung.
`ok weiter` allein reicht an dieser Grenze nicht aus. Siehe
[`S1-PW`](S1PW_STATISCHER_ABDECKUNGSAUDIT_ROOT_IMPORTVERBRAUCHER.md).

## Vorrangige Paketgrenze nach S1-PV

Die breite Root-API ist als generierte Lazy-Fassade umgesetzt. Alle 1.267
Namen und ihre Ursprungsidentitaeten bleiben erhalten; reiner Paketimport und
`current_api`-Import sind von nicht angeforderten Root-Modulen getrennt.

Der einmalige 41-Methoden-Verbund bestand vollstaendig. Als genau ein
Anschluss ist `S1-PW` fuer den statischen Abdeckungsaudit weiterer
Root-Importverbraucher vorgesehen. Keine weitere Ausfuehrung oder
Importaenderung. Siehe
[`S1-PV`](S1PV_IMPLEMENTIERUNG_UND_41_METHODEN_ABNAHME_LAZY_ROOT.md).

Die pausierte Substratforschung bleibt geschlossen.

## Vorrangige Abnahmegrenze nach S1-PU

S1-PU bindet die spaetere Lazy-Root-Migration auf zwei Laufzeitdateien, einen
statischen Generator und zwei neue Testdateien. `current_api` und saemtliche
Feld-, Referenz-, Kandidaten-, Runner- und Sensormodule bleiben unveraendert.

Das endliche Gate umfasst genau 41 Methoden in einem einzigen Lauf. S1-PU
selbst enthaelt keine Implementierung und keine Ausfuehrung. Als genau ein
Anschluss ist `S1-PV` fuer die einmalige Implementierung und Abnahme
vorgesehen. Siehe
[`S1-PU`](S1PU_STATISCHER_IMPLEMENTIERUNGS_UND_ABNAHMEVERTRAG_LAZY_ROOT.md).

Die pausierte Substratforschung bleibt geschlossen.

## Vorrangige Inventargrenze nach S1-PT

S1-PT bindet alle 1.267 Root-Namen statisch und eindeutig an 156
Ursprungsmodule. Die kanonische `__all__`-Liste und die sortierte
Name-Ursprung-Klasse-Abbildung besitzen getrennte Digests. Es gibt keine
Dubletten, Mehrdeutigkeiten oder fehlenden Urspruenge.

Die Root-Datei und die Runtime sind unveraendert. Als genau ein Anschluss ist
`S1-PU` fuer den statischen Implementierungs- und Abnahmevertrag der
Lazy-Root-Migration vorgesehen. Keine Implementierung und keine Tests. Siehe
[`S1-PT`](S1PT_STATISCHER_ROOT_EXPORTINVENTAR_UND_EINDEUTIGKEITSAUDIT.md).

Die pausierte Substratforschung bleibt geschlossen.

## Vorrangige Importgrenze nach S1-PS

S1-PS bindet ausschliesslich den statischen Migrationsvertrag fuer die breite
Root-Oberflaeche. Eine spaetere Lazy-Aufloesung muss alle bestehenden Namen,
Objektidentitaeten, `__all__`-Eigenschaften und direkten Modulimporte
kompatibel erhalten. Nicht angeforderte geschlossene, historische und
inaktive Module sollen beim Aktivkernimport nicht geladen werden.

Der Importcode ist unveraendert. Als genau ein Anschluss ist `S1-PT` fuer
die statische, digestgebundene Root-Exportabbildung vorgesehen. Keine
Implementierung und keine Ausfuehrung. Siehe
[`S1-PS`](S1PS_STATISCHER_VERTRAG_KOMPATIBLE_SCHLANKE_PAKETINITIALISIERUNG.md).

Die pausierte Substratforschung bleibt geschlossen.

## Vorrangige Architekturgrenze nach S1-PR

Der aktive technische Einstieg ist `mcm_field_organism.current_api`. Seine
129 Feldkernrollen sind von 57 Referenzrollen getrennt. Geschlossene
Kandidaten, historische Runner und inaktive Sensorpfade bleiben Archiv- oder
Kompatibilitaetsbestand und sind keine aktive Architektur.

Die Paket-Root-API bleibt derzeit breit und wird bei einem Python-Import vor
dem Untermodul initialisiert. Deshalb ist die aktive Namensgrenze sauber,
waehrend die physische Paketinitialisierung noch nicht auf den Feldkern
begrenzt ist. S1-PR veraendert daran keinen Code.

Als genau ein technischer Anschluss ist `S1-PS` fuer den statischen Vertrag
einer kompatiblen schlanken Paketinitialisierung vorgesehen. Die pausierte
Substratforschung bleibt geschlossen. Siehe
[`S1-PR`](S1PR_STATISCHE_AKTIVKERN_ISOLATION_UND_ARCHIVGRENZENKONSOLIDIERUNG.md).

## Verbindlicher Projektgegenstand

Das Projekt entwickelt und prueft ein technikbasiertes MCM-Wahrnehmungsfeld.
Sein primaerer Kern ist:

```text
kontrollierte Audio-/Video-Testwelt
-> zeitlich geordnete Rezeptorfolgen
-> gemeinsames lokales MCM-Feld
-> schneller technischer S/H-Zustand
-> passive Messung, Baselines und Reproduzierbarkeitspruefung
```

Das Feld verarbeitet kontrollierte Eingangsfolgen in einer gemeinsamen lokalen
Feldgeometrie. Snapshot und Restore sind Runtime-Serialisierung. Nachhall H ist
eine schnelle passive Zustandsrolle. Diese technischen Funktionen begruenden
keine weitergehende Faehigkeit.

Der Repository- und Paketname `MCM_FIELD_ORGANISM` bleibt aus Gruenden der
Kompatibilitaet und Nachvollziehbarkeit bestehen. Er ist keine fachliche
Behauptung ueber die Eigenschaften des Systems.

## Vorrangige Forschungsgrenze nach S1-PQ

Der statische S1-PQ-Audit bestaetigt den oben beschriebenen Feldkern als
aktive technische Architektur. Er findet keine bereits gebundene
eigenstaendige Gegenprognose, die einen neuen Substrat- oder technischen
Memory-Funktionszweig zulaesst. Diese Forschung bleibt pausiert.

Geschlossene Kandidaten, technische Baselines, historische Runner und
inaktive Sensoradapter duerfen im Repository verbleiben, gehoeren dadurch
aber nicht zum aktiven Feldkern. Als genau ein naechster Anschluss ist
`S1-PR` zur statischen Aktivkern-Isolation und
Archivgrenzenkonsolidierung vorgeschlagen. Bis zu einer ausdruecklichen
Freigabe erfolgen keine Kandidatenwahl, Gleichung, Runtimeaenderung oder
Ausfuehrung. Siehe
[`S1-PQ`](S1PQ_STATISCHER_BESTANDS_UND_LUECKENAUDIT_PRIMAERES_MCM_WAHRNEHMUNGSFELD.md).

Die nachfolgende Chronologie bleibt als technischer Nachweisbestand erhalten.
Ihre frueheren Weiterfreigaben sind nicht mehr operativ.

## Aktueller Evidenzstand

- Lauf 198 ist ausschliesslich eine reale Fixed-Adapter-Gegenbaseline. Seine
  kleine, nichtnullige und ueber r2/r4/r8 konvergierende AB/BA-Wirkung ist kein
  Nachweis einer Speicher- oder Lernfunktion.
- S1-LM ist die statische C10-Fallauswahl abgeschlossen. S1-LN bindet aktuell
  die lokale C10-Anatomie fuer `B3/P_IH_ATTENUATION` inkl. Rollenledger,
  Konservationsidentitaet und expliziten Baseline-/Struktursperren ohne
  Equation, Parameter, Dynamik oder Ausfuehrung.
- S1-LO implementiert diese Auswahl als technisch vollständige dreifach
  ausgefuehrte `r2/r4/r8`-Sequenz mit exakt neun Intervallaufrufen und
  bestätigter Fail-Closed-Rahmung. Auch hier keine Feldkopplung oder
  dynamische Aussage.
- S1-LP bildet den vollständigen Case-Output fuer diese drei Refinements
  (Replica/Komponenten/Digests), inklusive Vergleichsmessung und Primärbezug,
  und bleibt rein statisch. Kein Feldlauf, keine Baselineentscheidung und kein
  Kandidatenvergleich.
- S1-LQ bindet C01 bis C10 als abgeschlossen, mit den zugehoerigen
  Vertrags- und Falloutput-Digests, und nennt als naechsten Fall ausschliesslich
  `C11 / B3 / B3_F3_LOCAL_LEAKY / P_IK_INTERFERENCE`.
- S1-LR bindet C11 statisch als B3/P_IK-Auswahl. S1-LS fuehrt exakt diese
  drei Refinements isoliert aus: `r2/r4/r8`, zwei P_IK-Sequenzen pro
  Replikat, 24 Intervallaufrufe und sechs technische signed Komponenten pro
  Refinement. Der C11-Falloutput, Matrixpublikation, Baseline- oder
  Kandidatenurteil und Runtime-Integration bleiben gesperrt.
- S1-LT bindet den vollstaendigen technischen C11-Falloutput aus den bereits
  vorhandenen S1-LS-Ausgaben. Enthalten sind Provenienz-, Vergleichs- und
  Checkpoint-Digests, `r4` als Primaerrefinement und zwei gerichtete
  Residualbloecke. Matrixpublikation, Baseline- oder Kandidatenurteil und
  Runtime-Integration bleiben weiterhin gesperrt.
- S1-LU bindet C01 bis C11 als abgeschlossen. Damit liegen elf von 24
  Profilfaellen beziehungsweise 33 von 72 Refinement-Ausgaben vor. C12 bis
  C24 fehlen weiterhin; als naechster einzelner Fall ist nur
  `C12 / B3 / B3_F3_LOCAL_LEAKY / P_IN_RELEASE_REUSE` freigegeben. Keine
  Matrixkomposition, keine Matrixpublikation und kein Urteil.
- S1-LV bindet C12 statisch als B3/P_IN-Auswahl mit zwei getrennten
  Recovery-Sequenzen, drei Refinements und vollstaendigem B3-Frischzustand.
  Es gibt keine Implementierung, keine Ausfuehrung, keinen C12-Falloutput,
  keine Matrixkomposition, keine Matrixpublikation und kein Urteil.
- S1-LW implementiert und fuehrt genau diese C12-Auswahl isoliert aus. Die
  Recovery-on/off-Terminals sind innerhalb jedes Refinements bitidentisch und
  alle sechs signed Komponenten sind null. Das ist kein Release-/Reuse-,
  Baseline- oder Kandidatenurteil; C12-Falloutput, Matrixkomposition und
  Matrixpublikation bleiben gesperrt.
- S1-LX bindet den vollstaendigen technischen C12-Falloutput aus den bereits
  vorhandenen S1-LW-Ausgaben. Enthalten sind Provenienz-, Vergleichs- und
  Checkpoint-Digests, `r4` als Primaerrefinement, sechs Nullkomponenten und
  zwei gerichtete Null-Residualbloecke. Matrixpublikation, Baseline- oder
  Kandidatenurteil und Runtime-Integration bleiben weiterhin gesperrt.
- S1-LY bindet C01 bis C12 als abgeschlossen. Damit liegen zwoelf von 24
  Profilfaellen beziehungsweise 36 von 72 Refinement-Ausgaben vor. C13 bis
  C24 fehlen weiterhin; als naechster einzelner Fall ist nur
  `C13 / B4 / B4_F3_LINEAR_COUPLED / P_IE_CAUSAL_TWO_SUBSTEP` freigegeben.
  Keine Matrixkomposition, keine Matrixpublikation und kein Urteil.
- S1-LZ bindet C13 statisch als B4/P_IE-Auswahl mit zwei getrennten
  P_IE-Sequenzen, drei Refinements und vollstaendigem B4-Frischzustand samt
  linear gekoppeltem M-Arm. Es gibt keine Implementierung, keine Ausfuehrung,
  keinen C13-Falloutput, keine Matrixkomposition, keine Matrixpublikation und
  kein Urteil.
- S1-MA implementiert und fuehrt genau diese C13-Auswahl isoliert aus. Alle
  acht signed Komponenten sind null; Provenienz-, Vergleichs- und
  Checkpointdigests bleiben refinementabhaengig. Das ist kein Baseline- oder
  Kandidatenurteil; C13-Falloutput, Matrixkomposition und Matrixpublikation
  bleiben gesperrt.
- S1-MB bindet den vollstaendigen technischen C13-Falloutput aus den bereits
  vorhandenen S1-MA-Ausgaben. Enthalten sind Provenienz-, Vergleichs- und
  Checkpoint-Digests, `r4` als Primaerrefinement, acht Nullkomponenten und
  zwei gerichtete Null-Residualbloecke. Matrixpublikation, Baseline- oder
  Kandidatenurteil und Runtime-Integration bleiben weiterhin gesperrt.
- S1-MC bindet C01 bis C13 als abgeschlossen. Damit liegen dreizehn von 24
  Profilfaellen beziehungsweise 39 von 72 Refinement-Ausgaben vor. C14 bis
  C24 fehlen weiterhin; als naechster einzelner Fall ist nur
  `C14 / B4 / B4_F3_LINEAR_COUPLED / P_IH_ATTENUATION` freigegeben. Keine
  Matrixkomposition, keine Matrixpublikation und kein Urteil.
- S1-MD bindet C14 statisch als B4/P_IH-Auswahl mit einer P_IH-Sequenz, drei
  Refinements und vollstaendigem B4-Frischzustand samt linear gekoppeltem
  M-Arm. Es gibt keine Implementierung, keine Ausfuehrung, keinen
  C14-Falloutput, keine Matrixkomposition, keine Matrixpublikation und kein
  Urteil.
- S1-ME implementiert und fuehrt genau diese C14-Auswahl isoliert aus:
  `r2/r4/r8`, eine P_IH-Sequenz pro Replikat, neun Intervallaufrufe und acht
  technische signed Komponenten pro Refinement. Das ist kein Memory-Nachweis,
  keine vorhandene Memory-Faehigkeit, kein Baseline- oder Kandidatenurteil und
  kein Systemfaehigkeits-Claim; C14-Falloutput, Matrixkomposition und
  Matrixpublikation bleiben gesperrt.
- S1-MF bindet den vollstaendigen technischen C14-Falloutput aus den bereits
  vorhandenen S1-ME-Ausgaben. Enthalten sind Provenienz-, Vergleichs- und
  Checkpoint-Digests, `r4` als Primaerrefinement, acht nichtnullige
  Komponenten und zwei gerichtete nichtnullige Residualbloecke.
  Matrixpublikation, Baseline- oder Kandidatenurteil, Memory-Faehigkeit und
  Runtime-Integration bleiben weiterhin gesperrt.
- S1-MG bindet C01 bis C14 als abgeschlossen. Damit liegen vierzehn von 24
  Profilfaellen beziehungsweise 42 von 72 Refinement-Ausgaben vor. C15 bis
  C24 fehlen weiterhin; als naechster einzelner Fall ist nur
  `C15 / B4 / B4_F3_LINEAR_COUPLED / P_IK_INTERFERENCE` freigegeben. Keine
  Matrixkomposition, keine Matrixpublikation und kein Urteil.
- S1-MH bindet C15 statisch als B4/P_IK-Auswahl mit zwei getrennten
  P_IK-Sequenzen, drei Refinements und vollstaendigem B4-Dreiknoten-
  Frischzustand samt linear gekoppeltem M-Arm. Es gibt keine Implementierung,
  keine Ausfuehrung, keinen C15-Falloutput, keine Matrixkomposition, keine
  Matrixpublikation und kein Urteil.
- S1-MI implementiert und fuehrt genau diese C15-Auswahl isoliert aus:
  `r2/r4/r8`, zwei P_IK-Sequenzen pro Replikat, 24 Intervallaufrufe und sechs
  technische signed Komponenten pro Refinement. Das ist kein Interferenz-,
  Baseline- oder Kandidatenurteil, keine Memory-Faehigkeit und kein
  Systemfaehigkeits-Claim; C15-Falloutput, Matrixkomposition und Matrixpublikation
  bleiben gesperrt.
- S1-MJ bindet den vollstaendigen technischen C15-Falloutput aus den bereits
  vorhandenen S1-MI-Ausgaben. Enthalten sind Provenienz-, Vergleichs- und
  Checkpoint-Digests, `r4` als Primaerrefinement, sechs nichtnullige
  Komponenten und zwei gerichtete nichtnullige Residualbloecke.
  Matrixpublikation, Baseline- oder Kandidatenurteil, Memory-Faehigkeit und
  Runtime-Integration bleiben weiterhin gesperrt.
- S1-MK bindet C01 bis C15 als abgeschlossen. Damit liegen fuenfzehn von 24
  Profilfaellen beziehungsweise 45 von 72 Refinement-Ausgaben vor. C16 bis
  C24 fehlen weiterhin; als naechster einzelner Fall ist nur
  `C16 / B4 / B4_F3_LINEAR_COUPLED / P_IN_RELEASE_REUSE` freigegeben. Keine
  Matrixkomposition, keine Matrixpublikation und kein Urteil.
- S1-ML bindet C16 statisch als B4/P_IN-Auswahl mit zwei getrennten
  P_IN-Sequenzen, drei Refinements und vollstaendigem B4-Dreiknoten-
  Frischzustand samt linear gekoppeltem M-Arm. Es gibt keine Implementierung,
  keine Ausfuehrung, keinen C16-Falloutput, keine Matrixkomposition, keine
  Matrixpublikation und kein Urteil.
- S1-MM implementiert und fuehrt ausschliesslich die drei C16-Replikate
  `B4:P_IN_RELEASE_REUSE:r2/r4/r8` isoliert aus. Es gibt gebundene Output-,
  Vergleichs- und Checkpoint-Digests aus 24 Intervallaufrufen, aber keinen
  C16-Falloutput, keine Matrixkomposition, keine Matrixpublikation und kein
  Urteil.
- S1-MN setzt den technischen C16-Falloutput ausschliesslich aus den S1-MM-
  Ausgaben zusammen. Primaerkomponenten und Residuen sind exakt null; daraus
  folgt kein Release-/Reuse-Urteil, kein Baselineabschluss und kein
  Kandidatenvergleich.
- S1-MO bindet C01 bis C16 als vollstaendige technische Falloutputs mit 48 von
  72 Refinement-Ausgaben. C17 bis C24 fehlen weiterhin; als naechster einzelner
  Fall ist nur `C17 / B5 / B5_F3_FULL / P_IE_CAUSAL_TWO_SUBSTEP` freigegeben.
  Keine Matrixkomposition, keine Matrixpublikation und kein Urteil.
- S1-MP bindet C17 statisch als B5/P_IE-Auswahl mit zwei P_IE-Sequenzen, drei
  Refinements und vollstaendigem B5-Zweiknoten-Frischzustand samt vollem B5-
  Arm. Es gibt keine Implementierung, keine Ausfuehrung, keinen C17-Falloutput,
  keine Matrixkomposition, keine Matrixpublikation und kein Urteil.
- S1-MQ implementiert und fuehrt ausschliesslich die drei C17-Replikate
  `B5:P_IE_CAUSAL_TWO_SUBSTEP:r2/r4/r8` isoliert aus. Es gibt gebundene
  Output-, Vergleichs- und Checkpoint-Digests aus 12 Intervallaufrufen, aber
  keinen C17-Falloutput, keine Matrixkomposition, keine Matrixpublikation und
  kein Urteil.
- S1-MR setzt den technischen C17-Falloutput ausschliesslich aus den S1-MQ-
  Ausgaben zusammen. Primaerkomponenten und Residuen sind exakt null; daraus
  folgt kein Baselineabschluss und kein Kandidatenvergleich.
- S1-MS bindet C01 bis C17 als vollstaendige technische Falloutputs mit 51 von
  72 Refinement-Ausgaben. C18 bis C24 fehlen weiterhin; als naechster einzelner
  Fall ist nur `C18 / B5 / B5_F3_FULL / P_IH_ATTENUATION` freigegeben. Keine
  Matrixkomposition, keine Matrixpublikation und kein Urteil.
- S1-MT bindet C18 statisch als B5/P_IH-Auswahl mit einer P_IH-Sequenz, drei
  Refinements und vollstaendigem B5-Zweiknoten-Frischzustand samt vollem B5-
  Arm. Es gibt keine Implementierung, keine Ausfuehrung, keinen C18-Falloutput,
  keine Matrixkomposition, keine Matrixpublikation und kein Urteil.
- S1-MU bindet ausschliesslich den Kohaerenzvertrag fuer geschlossene
  Feldkopplung. Kohaerenz ist ein technischer Messrahmen, keine
  Projektfaehigkeit. Stoerung, lokale Ressource, Spaetaufnahme,
  Abschwaechung, Interferenz, Freigabe, Gegenbaselines und
  Verwerfungsbedingungen muessen vor jeder Kandidatengleichung feststehen.
  Es gibt keine Gleichung, keine Parameter, keine Runtime, keinen Feldlauf und
  keinen Memory- oder Systemfaehigkeitsclaim.
- S1-MV waehlt statisch `KFS-1` als einzigen weiterverfolgbaren
  Kandidatenraum fuer diese Kohaerenzrolle. KFS-1 ist ein lokales
  ressourcenbegrenztes Feld-Substrat mit Kohaerenzbelastung und spaeterer
  Aufnahmeaenderung. Reward, Replay, feste Kanten, globale Normalisierung,
  reiner Leaky-Nachhall, reiner Integrator, Fixed Adapter und
  Readout-Klassifikatoren sind als primaere Kandidaten gesperrt. Es gibt keine
  Gleichung, keine Parameter, keine Runtime, keinen Feldlauf und keinen
  Memory- oder Systemfaehigkeitsclaim.
- S1-MW bindet fuer KFS-1 ausschliesslich Funktionsprognose,
  Falsifikationskriterien und Claim-Sperren. Lokale Stoerungsaufnahme,
  Ressourcenbelastung, Spaetaufnahme, Abschwaechung, Interferenz, Freigabe und
  Wiederbindung muessen getrennt messbar sein. Gegenbaselines bleiben Fixed
  Adapter, Leaky-Nachhall, Integrator, Replay, globale Normalisierung, feste
  Kanten, Readout-Klassifikator und F3/CONST-V. Es gibt keine Gleichung, keine
  Parameter, keine Runtime, keinen Feldlauf und keinen Memory- oder
  Systemfaehigkeitsclaim.
- S1-MX bindet fuer KFS-1 ausschliesslich statische Anatomie und Messrollen:
  lokale Traeger- und Kantenidentitaet, read-only S/H-Feldbezug, ein
  endliches `free/bound/blocked`-Ressourcenledger pro Kante, lokale
  Erhaltungsidentitaet, passive Messrollen, verbotene Zustaende,
  Baselineabgrenzung und Fail-Closed-Anatomietests. Es gibt keine Gleichung,
  keine Parameter, keine Runtime, keinen Feldlauf, keinen Funktionsnachweis
  und keinen Memory- oder Systemfaehigkeitsclaim.
- S1-MY bindet fuer KFS-1 ausschliesslich das statische Schema- und
  Digestmodell. Kanonische IDs und getrennte Digests halten Geometrie,
  Feldreferenz, Ressourcenledger, Expositionshistorie und Messrollen
  reproduzierbar auseinander. Ungueltige oder kausal nicht vergleichbare
  Records scheitern fail-closed. Digests sind Identitaetsnachweise und keine
  Funktionsbefunde; Gleichung, Parameter, Runtime, Feldlauf und
  Funktionsentscheidung bleiben gesperrt.
- S1-MZ bindet ausschliesslich den zugehoerigen statischen Validator- und
  Fixturevertrag. Unveraenderte Eingabebytes, Validierungsbeleg und
  Record-Digests bleiben getrennt. Gueltige Minimalfixtures und eindeutig
  mutierte Fehlerfixtures pruefen Schema, Anatomie, lokale Bilanz, faire
  Vorgeschichte, passive Messrollen und deterministische Ablehnung. Es gibt
  keine Kandidatengleichung, keine Dynamikparameter, keine Runtimeintegration,
  keinen Feldlauf und keine Funktionsentscheidung.
- S1-NA bindet ausschliesslich die isolierte Implementierungsgrenze dieses
  Validators. Ein Produktionsmodul, ein testseitiger Fixturekatalog und eine
  fokussierte Testdatei duerfen spaeter Schema, Digests, Anatomie, Bilanz und
  kausale Vergleichbarkeit pruefen. Das endliche Budget erlaubt hoechstens 64
  Validatoraufrufe und genau null MCM-Feldschritte, Runner-, Medien-, Browser-,
  Netzwerk- oder Reportaufrufe. Kandidatendynamik und Funktionsentscheidung
  bleiben gesperrt.
- S1-NB implementiert ausschliesslich diesen statischen Validator und nimmt
  ihn einmal fokussiert ab. Alle 12 Testgruppen mit insgesamt 23 Fixtures
  bestehen bei 27 Validatoraufrufen und genau null MCM-Feldschritten.
  Ungueltige Records werden nicht repariert; ihre Eingabebytes bleiben
  digestgebunden. Das ist ein Validatorbefund und keine KFS-1-Wirkung,
  Runtimeintegration oder Funktionsentscheidung.
- S1-NC bindet ausschliesslich das lokale KFS-1-Uebergangsalphabet. Vier
  ressourcenerhaltende Wechsel und drei Stillstandsrollen sind strukturell
  zugelassen; uebersprungene Rollen, Wechsel zwischen Kanten, globale
  Bilanzkorrektur und Readout-gesteuerte Ereignisse sind fail-closed
  gesperrt. Jeder spaetere Wechsel benoetigt dieselbe lokale Kantenidentitaet,
  geordnete Feldfolge und eine vorangehende Ausloeserbeobachtung. Gleichung,
  Rate, Parameter, Runtime und Funktionsentscheidung bleiben gesperrt.
- S1-ND bindet ausschliesslich Schema, Digests und Fehlergrenze lokaler
  Uebergangsrecords. Vollstaendige Vor-/Nachledger, Bilanzwert, Rollenpaar,
  Ausloeserreferenz, Feldordnung und Vorgaengerverkettung muessen gemeinsam
  gueltig sein. Sieben Alphabetfaelle und achtzehn Fail-Closed-Codes sind
  festgelegt. Die isolierte Validatorerweiterung ist freigegeben; Gleichung,
  Rate, Dynamikparameter, Runtime, Feldlauf und Funktionsentscheidung bleiben
  gesperrt.
- S1-NE implementiert ausschliesslich die isolierte Einzelrecord- und
  Vorgaengerpruefung. Alle sieben Alphabetrecords, achtzehn isolierten
  Fehlerfaelle sowie gueltige und gebrochene Zweierkette werden in 12
  Testgruppen korrekt behandelt. Es gab 29 Uebergangsvalidatoraufrufe und
  genau null MCM-Feldschritte. Der Befund betrifft nur Schema, Bilanz und
  Kettenintegritaet; er ist keine KFS-1-Wirkung oder Funktionsentscheidung.
- S1-NF waehlt ausschliesslich `KFS1-T1_LOCAL_TARGET_REFRACTORY` als erste
  konkrete lokale Regel. Zielbelegung ist `C*p` mit der bestehenden
  symmetrischen Kantenbeteiligung. Positiver Kontakt bindet oder blockiert;
  nur exakter Nullkontakt gibt vorbestehende blockierte Ressource frei. Die
  Regel besitzt keine freie Rate, Schwelle oder Parametersuche und noch keine
  Runtime- oder Feldrueckwirkung. DTS-1 bleibt verpflichtende strukturelle
  Gegenbaseline; ein Funktionsbefund liegt nicht vor.
- S1-NG implementiert und prueft ausschliesslich diese lokale T1-Regel fuer
  eine Kante. Die einmalige fokussierte Abnahme besteht mit 12 Tests, elf
  Uebergaengen und null Feldschritten. Die acht Ledgerprognosen, lokale
  Erhaltung und technische Isolation sind erfuellt. Das ist keine
  Feldwirkung, keine Baselineentscheidung und kein Befund zur hypothetischen
  MCM-Memory. Vor weiterer Ausfuehrung muss S1-NH die endliche Sequenz und
  die faire DTS-1-Gegenbaseline statisch binden.
- S1-NH bindet die endliche lokale Vergleichsfolge und schliesst die
  Profilmenge vor jeder Ausfuehrung. T1 und DTS-1 sehen dieselben sieben
  Beteiligungsereignisse und dieselbe Gesamtressource. DTS-1 darf nur das
  registrierte Profil `0.4/0.3/0.2` in `r1/r2/r4/r8` sowie die statische
  Nullratenkontrolle verwenden. Es gibt noch keine Ausfuehrung,
  Redundanzentscheidung oder Feldwirkung.
- S1-NI fuehrt den gebundenen lokalen Vergleich genau einmal aus. Acht Tests
  bestehen bei sieben T1-Uebergaengen, 112 DTS-1-Subschritten und null
  Feldschritten. Die festen DTS-1-Arme reproduzieren T1 nicht vollstaendig;
  T1 ist jedoch exakt als ereignisgeschaltete DTS-1-Dreirollenabbildung
  darstellbar. T1 bleibt deshalb nur als diskrete DTS-1-Gegenbaseline und
  wird nicht als unabhaengiger Substratkandidat an das Feld gekoppelt.
- S1-NJ schliesst T1 formal als unabhaengigen Kandidaten. Eine spaetere
  KFS-1-Regel muss zusaetzlich zum bestehenden Funktionsvertrag ein
  Nicht-DTS-Gate erfuellen: anderes atomares Transfernetz, zusaetzliche
  endliche nicht rekonstruierbare lokale Zustandskoordinate oder nicht auf
  DTS-1 faktorisierbare lokale Ressourcenverteilung. Eine kontrollierte
  Zustandsinterventionsprognose ist vor jeder Gleichung verpflichtend.
- S1-NK auditiert G1 bis G3 und fuehrt nur G2 als darstellungsoffene Klasse
  eines endlichen lokalen Konfigurationszustands weiter. G1 traegt allein
  keine eigene Zustandsintervention; G3 ist entweder im DTS-1-Kantenledger
  enthalten oder benoetigt selbst eine zusaetzliche G2-Rolle. Es sind noch
  keine Variable, Anatomie, Gleichung, Runtime oder Feldwirkung gewaehlt.
- S1-NL bindet fuer G2 direkte Zustandsintervention und spaetere endogene
  Bildung als getrennte Falsifikationsstufen. Bei bitgleichem Feld-,
  Ressourcen- und Baselinevorzustand darf nur G2 C0/C1 unterscheiden.
  Leaky-/Integratorgegenprognosen, reine G2-Ablation, Abschwaechung,
  Interferenz, Loesung und erneute Bildung bleiben verpflichtend. Eine
  Darstellung, Gleichung oder Feldwirkung ist weiterhin nicht gewaehlt.
- S1-NM bindet zwei direkte F1-Arme mit bitgleichem Feld-, Ressourcen- und
  Baselinevorzustand. Nur C0/C1 unterscheidet sich. Primaer gemessen wird die
  obere lokale Zulassungsgrenze fuer `free -> bound`; fuer C1 ist eine
  geringere Zulassung vorregistriert, waehrend alle Baselines und die
  G2-Ablation exakt null zwischen den Armen vorhersagen. Noch keine
  Zustandsdarstellung, Ausfuehrung oder Feldwirkung.
- S1-NN waehlt nach einem Vierklassen-Audit ausschliesslich die konservative
  Unterteilung `bound_unconfigured + bound_configured = bound`. Sie fuegt
  keine Gesamtressource hinzu und bleibt fuer DTS-1/T1 bei Aggregation
  unsichtbar. Binaerflag, unabhaengiger Skalar und Mehrkantenrelation sind
  fuer F1 gestoppt. Eine Dynamik, Funktion oder Feldwirkung ist nicht
  gebunden.
- S1-NO bindet die D3-Unterteilung als statische Einkantenanatomie mit vier
  disjunkten Rollen und exakter Erhaltung. C0 und C1 projizieren bitgleich
  auf `(free,bound,blocked)=(0.5,0.5,0.0)`. Die reine Ablation bildet C1 auf
  C0 ab, ohne Kapazitaet oder Aggregat zu veraendern. Keine Dynamik,
  Admissibilitaetsfunktion, Ausfuehrung oder Feldwirkung ist gebunden.
- S1-NP bindet additiv ein eigenes D3-Anatomieschema mit getrennten Digests
  fuer Vierrollenressource, Dreirollenprojektion und Gesamtrecord. Spaetere
  reine Einzel- und Paarvalidatoren duerfen nur Anatomie, Erhaltung,
  C0/C1-Aggregation und Ablation pruefen. Das bestehende KFS-1-Schema bleibt
  unveraendert; Implementierung, Dynamik und Feldwirkung sind gesperrt.
- S1-NQ bindet die isolierte Implementierung mit drei neuen Dateien,
  bytefesten C0/C1/MIXED-Fixtures, 18 Einzel- und sechs Paarmutationen,
  zwoelf Testgruppen und einem endlichen Einmalausfuehrungsbudget. C0 und C1
  besitzen bitgleich denselben Dreirollen-Projektionsdigest. Noch gibt es
  keine Validatorausfuehrung, Admissibilitaetsfunktion oder Feldwirkung.
- S1-NR implementiert die drei Dateien. Die einmalige fokussierte Abnahme
  scheiterte an genau einem abgeleiteten Folgefehler fuer ein fehlendes
  Klassenfeld. Die korrigierte Implementierung ist noch nicht erneut
  ausgefuehrt und deshalb nicht abgenommen. Bis zu einem separat gebundenen
  Wiederabnahmeschritt bleiben alle G2-Funktions- und Feldpfade gesperrt.
- S1-NS bindet fuer die bitgleich festgelegte korrigierte Fassung genau eine
  Wiederabnahme nach read-only Digestpreflight. Der Schritt selbst fuehrt
  nichts aus. Nur `10 tests, OK` darf den statischen Validator akzeptieren;
  jede Abweichung haelt alle G2-Funktions- und Feldpfade geschlossen.
- S1-NT bestaetigt den Preflight bitgleich und akzeptiert den statischen
  D3-Validator mit genau einem fokussierten Lauf und `10 tests, OK`.
  Akzeptiert sind nur Anatomie-, Bilanz-, Digest-, Projektions- und
  Ablationspruefungen; Admissibilitaet, Dynamik und Feldwirkung bleiben offen.
- S1-NU bindet fuer die direkte F1-Messung nur die parameterfreie reine
  Restzulassung `max(0.0,free-bound_configured)`. Sie liest zwei validierte
  D3-Rollen, mutiert nichts und wird nicht auf aggregierte Baselinerecords
  angewendet. Implementierung, Transfer, Bildung und Feldwirkung bleiben
  gesperrt.
- S1-NV bindet die isolierte O3-Implementierung mit genau zwei neuen Dateien,
  validierungsgebundener API, unveraenderlichem Beleg, bestehenden bytefesten
  Fixtures und endlichem Einmaltestbudget. Der Schritt fuehrt nichts aus;
  Transfer, Bildung, Dynamik und Feldwirkung bleiben gesperrt.
- S1-NW implementiert und akzeptiert den reinen O3-Begrenzer mit genau einem
  fokussierten Lauf und `10 tests, OK`. Der direkte C0/C1-Unterschied ist
  konstruktiv durch die statische Formel erzeugt und noch kein Befund einer
  endogenen Bildung oder Feldwirkung. Diese Pfade bleiben gesperrt.
- S1-NX bindet F2 als drei endliche, dosis- und kontaktmengengleiche lokale
  Geschichten mit unterschiedlicher Ordnung. Nur die D3-Unterteilung darf
  nach gemeinsamer schneller Feld- und Aggregatangleichung verschieden
  bleiben. Bildungsgleichung, Parameter, Runtime und Feldwirkung bleiben
  gesperrt.
- S1-NY fuehrt nur die Klasse einer transienten lokalen
  Fortsetzungspruefung weiter. Sie darf am atomaren Zweiintervallrand eine
  konservative D3-Umordnung zulassen, aber keinen Kontakt, Zaehler oder
  Sequenzzustand persistieren. Betrag, Rate, Gleichung und Feldwirkung bleiben
  gesperrt.
- S1-NZ bindet die transiente Zweiintervallanatomie, drei Ereignisrollen und
  eine atomare Commitgrenze. Nur eine konservative Umordnung innerhalb von
  `bound` ist als spaetere Zielprojektion zulaessig. Nach Commit darf keine
  Kontakt-, Intervall- oder Ereignisrolle im Kandidaten- oder Feldzustand
  verbleiben; Betrag und Gleichung sind weiter gesperrt.
- S1-OA bindet das additive transiente Grenzschema, getrennte Kontakt- und
  Recorddigests, D3-Quellvalidierung und einen ausschliesslich passiven
  Einzelgrenzenbeleg. Ereignisvorgabe, Persistenz oder Rueckfuehrung des
  Belegs sind fail-closed verboten. Implementierung und Bildung bleiben
  gesperrt.
- S1-OB bindet die isolierte Grenzvalidatorimplementierung mit drei neuen
  Dateien, kanonischer Fixture-Fabrik, byte- und digestfesten Tabellen- und
  Verlaufsfaellen, 17 Fehlermutationen und endlichem Einmaltestbudget. Der
  Schritt fuehrt nichts aus; Umordnung, Bildung und Feldwirkung bleiben
  gesperrt.
- S1-OC implementiert genau diese drei Dateien und akzeptiert den passiven
  Grenzvalidator im einzigen Lauf mit `12 tests, OK`. Die vorab gebundenen
  Ereignisrollen und alle 17 Fail-Closed-Mutationen werden exakt bestaetigt.
  Der Validator veraendert keinen D3- oder Feldzustand und belegt weder eine
  Bildung noch eine Funktion der hypothetischen MCM-Memory. S1-OD darf als
  Naechstes nur einen statischen Betrags-Funktionsvertrag binden; Gleichung,
  Parameter, Umordnung und Feldwirkung bleiben gesperrt.
- S1-OD bindet den statischen Betrags-Funktions- und
  Falsifikationsvertrag. Nullfaelle, positive F2-Fortsetzung,
  Spiegelgleichheit, lokale Restressourcengrenze und Trennung von Betrag und
  Commit stehen damit vor jeder Formel fest. S1-OE darf nur minimale
  Betragsfamilien auditieren; Parameter, Implementierung, Umordnung und
  Feldwirkung bleiben gesperrt.
- S1-OE verwirft Nullfamilie, festes Quantum und Vollumordnung. Nur eine
  strikt innere restressourcenbezogene Familie wird ohne Formel oder
  Zahlenparameter weitergefuehrt. Ihre moegliche Leaky- oder
  Adapterreduzierbarkeit bleibt ausdruecklich offen und muss durch eine
  angepasste Gegenbaseline geprueft werden. S1-OF darf nur den statischen
  mathematischen und numerischen Vertrag binden.
- S1-OF bindet die konstruierte Halbierungsform `m=U/2`, Faktor `1/2`, eine
  exakte dyadische Operationsdomaene und rationale Bilanzpruefung. Ausserhalb
  der Domaene entsteht fail-closed kein Zielwert. Die F2-Zielwerte H0 `0.0`
  und H1/H1M `0.375` sind Vertragserwartungen, keine Messergebnisse. Die
  angepasste Leaky-/Adapterbaseline bleibt zwingend. S1-OG darf nur Schema,
  Digests und einen passiven Belegvertrag binden.
- S1-OG bindet eine reine API, Registry, neun Phasen, fuenf Fehlercodes und
  einen passiven Halbierungsbetragsbeleg. Die Quelle wird innerhalb desselben
  Aufrufs validiert; Zielwerte bleiben verworfene Previewwerte. D3-Nachzustand,
  Commit, O3 und Feldwirkung bleiben gesperrt. S1-OH darf nur den statischen
  Implementierungs-, Fixture- und Testbudgetvertrag binden.
- S1-OH bindet genau drei S1-OI-Dateien, neun gueltige Kontrollen, fuenf
  einzeln gegatete Fehlerfixtures, zwoelf Testgruppen und maximal 36
  Operatoraufrufe fuer genau einen Testlauf. Noch ist kein Betragsoperator
  implementiert. Zielzustand, Commit, O3 und Feldwirkung bleiben gesperrt.
- S1-OI implementiert und akzeptiert die reine Halbierungsbetragsermittlung
  im einzigen Lauf mit `12 tests, OK`. Sie liefert fuer gueltige erste
  Fortsetzungen `0.25` und bleibt fuer alle gebundenen Nullpfade null. Der
  Beleg ist passiv; D3-Zielzustand, Commit, O3 und Feldwirkung bleiben
  gesperrt. S1-OJ darf nur deren statischen Funktions- und
  Falsifikationsvertrag binden.
- S1-OJ bindet reine Zielprojektion und atomare Commitgrenze getrennt. Nur
  `bound_unconfigured` und `bound_configured` duerfen sich gegensinnig
  aendern; Nullpfade bleiben byteidentisch. Positive Zielbytes muessen
  kanonisch neu digestiert, D3-validiert und vor Uebergabe gegen die aktuelle
  Quelldigestidentitaet geprueft werden. Implementierung, Runtimecommit, O3
  und Feldwirkung bleiben gesperrt.
- S1-OK bindet die getrennten Schema-, Digest- und Fail-Closed-Oberflaechen.
  Projektions- und Betragsbelege sind passive Dokumentation und keine
  Commit-Eingaben. Die Commitseite rekonstruiert die erwartete Projektion aus
  Originalbytes und sperrt ungueltige Vorschlaege sowie stale Quellen ohne
  Zustandsbytes. Implementierung, Runtimecommit, O3 und Feldwirkung bleiben
  gesperrt.
- S1-OL begrenzt die naechste Implementierung auf die reine Zielprojektion:
  drei neue Dateien, zehn gueltige Kontrollen, fuenf unveraenderte
  Eingabefehler und ein einmaliger Testlauf mit maximal 40
  Projektionsaufrufen. Die atomare Commitseite bleibt separat gesperrt.
- S1-OM implementiert und akzeptiert diese reine Zielprojektion im einzigen
  Lauf mit `12 tests, OK`. Nullpfade bleiben objektidentisch; positive erste
  und zweite Fortsetzungen erzeugen die exakt gebundenen konservativen
  D3-Zielbytes. Es gibt keine Commitfunktion, Runtimepublikation, O3- oder
  Feldwirkung. S1-ON darf nur den statischen Implementierungs-, Fixture- und
  Testbudgetvertrag fuer die getrennte atomare Commitauswahl binden.
- S1-ON bindet diese Commitauswahl mit fuenf gueltigen Kontrollen, neun
  getrennten Fehlerfaellen und maximal 45 Aufrufen in einem einzigen
  spaeteren Test. Erwartetes Ziel, vorgeschlagener Zustand und aktueller
  Zustand bleiben unabhaengige Pruefrollen. Runtimepublikation, O3 und
  Feldwirkung bleiben gesperrt.
- S1-OO implementiert und akzeptiert die reine atomare Commitauswahl im
  einzigen Lauf mit `14 tests, OK`. Erwartete Projektion, Vorschlag, aktueller
  Zustand und Stale-Gate bleiben getrennt; Fehler liefern keine Zustandsbytes.
  Die Auswahl existiert nur im Rueckgabeobjekt. Runtimepublikation, O3 und
  Feldwirkung bleiben gesperrt.
- S1-OP bindet ausschliesslich Funktion und Falsifikation einer reinen
  Zweischrittkomposition. Der zweite Schritt darf erst aus vollstaendigen
  ersten Commitbytes beginnen; seine Grenze muss Kontaktordinale `1/2`, den
  vorherigen Kontakt und den Mixed-Anatomierecord als Quelle binden. Belege,
  Teilzustaende, Runtimepublikation, O3 und Feldwirkung bleiben gesperrt.
- S1-OQ bindet die Sequenzoberflaeche mit zwei exakten Chainrecords,
  Vertragsdigest, dreizehn Phasen, elf Einzelcodes und passivem Beleg. Zweite
  Grenzvalidierung, D3-Quellbindung und Kontaktverknuepfung bleiben getrennte
  Gates vor dem zweiten Projektionsaufruf. Implementierung,
  Runtimepublikation, O3 und Feldwirkung bleiben gesperrt.
- S1-OR begrenzt die naechste Implementierung auf drei neue Dateien, zwei
  gueltige Chains, sieben externe Fehlermutationen und einen einmaligen
  Testlauf. Sechs defensive Invariantencodes werden ohne Fake-Resultate oder
  Dependency-Ersatz nur statisch gegatet. Runtimepublikation, O3 und
  Feldwirkung bleiben gesperrt.
- S1-OS implementiert und akzeptiert die reine Zweischrittkomposition im
  einzigen Lauf mit `14 tests, OK`. Beide Orientierungsrollen erzeugen
  dieselben konservativen Zwischen- und Endbytes; alle externen Kausalfehler
  bleiben ohne finale Bytes. O3, Feldwirkung und Runtimepublikation bleiben
  gesperrt.
- S1-OT bindet drei read-only O3-Checkpoints an validiertes C0, ersten
  Mixed-Commit und finalen Second-Commit. Die Werte `0.5/0.25/0.125` sind
  konstruktive Operatorprognosen und keine Funktionsabgrenzung. Beleginput,
  Fixturelookup, Feldwirkung und Runtimepublikation bleiben gesperrt; eine
  angepasste zustandsbehaftete Gegenbaseline bleibt zwingend.
- S1-OU bindet einen gemeinsamen privaten Zweischrittexecutor und eine neue
  Checkpointoberflaeche. Die bestehende S1-OS-Komposition muss bitidentisch
  bleiben. Der Messpfad darf den Executor einmal und O3 dreimal aufrufen;
  private Checkpointbytes bleiben unpubliziert. Feldwirkung und
  Runtimepublikation bleiben gesperrt.
- S1-OV bindet die Dateigrenze, den mechanischen Refaktor, zwei gueltige
  Chains, sieben reale Sequenzfehler, sechs defensive Gates und einen
  kombinierten Einmallauf mit exakt 30 Tests. S1-OS-Fixture, S1-OS-Test und
  O3-Operator bleiben byteidentisch. Implementiert oder ausgefuehrt wurde
  noch nichts.
- S1-OW implementiert den gemeinsamen privaten Executor und den isolierten
  Drei-O3-Checkpointpfad. Der einzige kombinierte Lauf bestand exakt 30
  Tests. Es werden nur Werte, Komponenten und passive Digests publiziert;
  Checkpointbytes, Feldwirkung und Runtimepublikation bleiben gesperrt. Die
  konstruktive Folge ist noch keine Funktionsabgrenzung gegen eine
  zustandsbehaftete Gegenbaseline.
- S1-OX bindet eine einzelne skalare Retentionsbaseline als faire
  zustandsbehaftete Gegenprognose. Sie sieht dieselben zwei modellneutralen
  Fortsetzungsereignisse, traegt ihren Zustand ohne Reset ueber drei
  Checkpoints und verwendet fuer XXX und YYY genau eine Konfiguration.
  Kandidatenbytes, Ressourcenrollen, erwartete Werte und Belege als
  Folgeeingang bleiben gesperrt. Es gibt noch keine Gleichung, keinen
  Parameter und keinen Vergleichslauf.
- S1-OY bindet genau einen nichtnegativen skalaren Baselinezustand, einen
  byteidentischen modellneutralen Fortsetzungstoken, 14 Phasen und elf
  Fail-Closed-Codes. Schrittposition und Kettenprovenienz erreichen den
  Updatekern nicht. Private Zustandsrecords werden nicht publiziert;
  Kandidat und Baseline bleiben bis zum passiven Vergleich getrennt.
  Startwert, Retentionsfraktion, Gleichung, Implementierung und Lauf bleiben
  offen.
- S1-OZ bindet `q_0 = 0.5`, eine stationaere Retentionsfraktion `0.5` und
  exakt zwei Updates. Werte, Komponenten, Konfigurations-/Zustandsdigests
  und Nullresiduen sind ohne Toleranz vorregistriert. Die atomare Prognose
  lautet `BASELINE_CLOSED_CURRENT_CHECKPOINT_VECTOR`. Noch gibt es keinen
  Baselineoperator, Comparator, Test oder Lauf.
- S1-PA bindet vier neue Dateien, die strikte Trennung von Baselineoperator
  und Comparator, fuenf externe Baselinefehler, drei externe
  Comparatorfehlerrollen, defensive Gates und genau einen kombinierten Lauf
  mit 48 Tests. Bestehende S1-OS-/S1-OW-Dateien bleiben byteidentisch.
  Implementiert oder ausgefuehrt wurde noch nichts.
- S1-PB implementiert die enge Retentionsbaseline und den passiven
  Comparator. Der einzige kombinierte Lauf bestand exakt 48 Tests. XXX und
  YYY liefern `BASELINE_CLOSED_CURRENT_CHECKPOINT_VECTOR` mit Nullresiduen.
  Der aktuelle Halbierungsvektor ist damit keine eigenstaendige
  Kandidatenfunktion und kein Befund zu einer hypothetischen
  MCM-Memory-Funktion. D3-Anatomie und technischer MCM-Feldkern bleiben
  unveraendert bestehen.
- S1-PC schliesst den Halbierungszweig und waehlt als einzige neue Richtung
  eine lokale `free`/`blocked`-Intervention bei gleicher Gesamtressource und
  gleicher leitender Bindung. Die Funktionsfrage betrifft ausschliesslich die
  tatsaechliche naechste Bindung nach einem identischen frischen Ereignis.
  Eine unmittelbare O3-Differenz gilt nur als Manipulationskontrolle und ist
  keine eigenstaendige Funktionsevidenz. Werte, Gleichung, Implementierung
  und Lauf bleiben gesperrt.
- S1-PD bindet die `free`/`blocked`-Umbuchung ausschliesslich als
  vorregistrierte externe Zweiarm-Testintervention aus demselben gueltigen
  D3-Vorzustand. Die gleich grossen entgegengesetzten Umbuchungen duerfen
  keine weitere Ressourcen- oder Strukturrolle veraendern und werden nur als
  vollstaendiges gueltiges Paar angenommen. Es gibt noch keine
  Kandidatenwirkung, Wirkungsgleichung, Implementierung oder Ausfuehrung.
- S1-PE bindet die statische Zweiarm-Fixture mit exakt dyadischen
  Ressourcenwerten und einem Umbuchungsbetrag von `0.125`. Drei kanonische
  D3-Records, die inhaltsfreie gemeinsame Ereignisidentitaet, ein externer
  Fixturemanifest und ihre SHA-256-Digests sind festgelegt. Der vorhandene
  F1-Paarvalidator bleibt wegen seiner engeren C0/C1-Bindung ausgeschlossen.
  Es gibt weiterhin keine Bindungsdynamik, Implementierung oder Ausfuehrung.
- S1-PF begrenzt die spaetere Fixtureabnahme auf ein neues passives
  Interventionsvalidatormodul, zwei Testdateien, 17 kontrollierte
  Fehlermutationen und genau einen Lauf mit 25 Testmethoden. Der bestehende
  D3-Einzelvalidator wird unveraendert wiederverwendet; vier Grundlagen sind
  digestfixiert. Kandidatenintegration, Bindungsdynamik und Feldpfad bleiben
  geschlossen.
- S1-PG implementiert ausschliesslich diesen passiven Validator und die zwei
  gebundenen Testdateien. Der einzige Lauf bestand mit exakt 25 Testmethoden;
  alle 17 kontrollierten semantischen Mutationen liefern ihren einzelnen
  erwarteten Fehlercode. Der Receipt enthaelt keine Zustandsbytes und das
  Modul besitzt keinen Teilcommit-, O3-, Feld- oder Runtimepfad. Dies ist nur
  eine technische Fixtureabnahme, keine Kandidatenwirkung.
- S1-PH bindet statisch das fuer Kandidatenarme und Baselinereplikate
  byteidentische frische Bindungsangebot. Primaere Messgroesse ist nur die
  direkte gueltige Ledgerumbuchung von `free` nach `bound_unconfigured`;
  O3 bleibt Manipulationskontrolle. Ein positiver Kandidatenkontrast bei
  nullwertigem Baselinekontrast waere lediglich eine kontrollierte
  Ressourcenreaktion. Zahlenwert, Wirkungsgleichung, Implementierung und
  Ausfuehrung bleiben offen beziehungsweise gesperrt.
- S1-PI bindet `offer_amount=0.375`, kanonische Expositions- und
  Ereignisbytes sowie zwei extern getrennte Baselinereplikate mit exakt
  gleichem Ursprungsdigest. Kandidatenzustands- und O3-Exposition sind
  gesperrt. Der Baseline-Ereignisadapter ist ausdruecklich `UNBOUND`; damit
  bleiben Nachzustaende, Baselineantwort, Implementierung und Ausfuehrung
  geschlossen.
- S1-PJ bindet die lokale konservative Bindungsgleichung, zwei exakte
  Kandidatennachrecords und einen statischen Ereignisadapter zur vorhandenen
  Retentionsbaseline. Prognostiziert sind Kandidatenkontrast `0.125` und
  Baselinekontrast `0.0`; nur der erste Baselineschritt darf verglichen
  werden. Dies ist ein analytischer Vertrag, keine ausgefuehrte
  Kandidatenwirkung. Implementierung, Feldintegration und Lauf bleiben
  gesperrt.
- S1-PK bindet nur die spaetere Dateigrenze, passive Informationsfluesse, 18
  Fehlermutationen und ein einmaliges 63-Testbudget. Kandidatenoperator,
  Adapter und Comparator bleiben getrennt; insbesondere startet der
  Comparator nichts und verwendet keinen zweiten Baselinecheckpoint.
  Implementierung, Feldintegration und Ausfuehrung bleiben gesperrt.
- S1-PL haelt die Dateigrenze und alle 13 eingefrorenen Digests ein. Der
  einmalige kombinierte Lauf erreichte 62 erfolgreiche Methoden und einen
  Testfehler: Test 19 verwendete `contract_digest`, waehrend das passive
  Comparator-Receipt `comparison_contract_digest` definiert. Der Lauf ist
  damit fail-closed beendet und S1-PL nicht abgenommen. Ein zweiter Lauf fand
  nicht statt.
- S1-PM darf als naechstes nur einen statischen Reparaturvertrag fuer diesen
  Testschluessel und ein neues endliches Einmallaufbudget festlegen. Bis zu
  dessen Abschluss bleiben Testwiederholung, Feldintegration und Aussagen
  ueber eine Kandidatenwirkung gesperrt.
- S1-PM bindet die Reparatur auf genau ein Schluesselfeld in Test 19. Die
  Produktionsmodule, Fixtures und S1-PK-Grundlagen bleiben unveraendert.
  S1-PN darf die eine vorregistrierte Ersetzung ausfuehren und bei exakten
  Digests genau einen neuen 63-Methoden-Verbundlauf starten. S1-PM selbst
  enthaelt keine Codeaenderung und keine Testausfuehrung.
- S1-PN hielt diese Grenze ein. Alle 18 statischen Digests stimmten und der
  einmalige Verbundlauf bestand mit exakt 63 Methoden
  (`Ran 63 tests in 0.138s`, `OK`). Abgenommen sind ausschliesslich der
  konstruktive lokale Ressourcenoperator, der statische Ereignisadapter und
  der passive Comparator. Feld-, Runtime-, O3- und Medienintegration bleiben
  gesperrt.
- S1-PO darf als naechstes nur statisch untersuchen, ob der beobachtete
  Kandidatenkontrast bereits vollstaendig durch eine minimale lokale
  Kapazitaets-Clamp-Baseline erklaert wird. Ohne eine danach verbleibende
  eigene Gegenprognose wird keine Kandidatenfunktion weiterverfolgt.
- S1-PO schliesst den statischen Einzelcommit als eigene Funktionsevidenz:
  `min(offer, free)` reproduziert beide Commits und den Kontrast `0.125`
  exakt. Die Retentionsbaseline mit Kontrast `0.0` war gegen diese Erklaerung
  nicht kausal gleich exponiert. Technische Implementierungsabnahme,
  D3-Anatomie und MCM-Feldkern bleiben bestehen.
- S1-PP darf nur eine kausal erzeugte Belastungs-, Freigabe- und
  Wiederbeanspruchungstrajektorie vertraglich binden. Alle zustandsbehafteten
  Gegenbaselines muessen dieselbe relevante Ereignisgeschichte sehen.
  Gleichung, Implementierung, Feldintegration und Lauf bleiben gesperrt.
- S1-PP hebt diese Weiterfreigabe auf. Free/Blocked und der Dreirollenzyklus
  bleiben DTS-1/T1-Baseline. Die einzige vorregistrierte endogene
  G2/D3-Bildungsklasse erzeugte den durch die Retentionsbaseline exakt
  geschlossenen Halbierungsvektor; die Free/Blocked-Ausweichrichtung ist
  Capacity-Clamp-reduzierbar. Es verbleibt keine registrierte nicht-DTS- und
  nicht-Clamp-reduzierbare endogene G2-Gegenprognose.
- Der G2-Zweig ist als eigenstaendige Kandidatenentwicklung gestoppt. Seine
  technischen Artefakte bleiben Regression, Infrastruktur und Baseline.
  Eine neue Substratrichtung benoetigt eine ausdrueckliche fachliche
  Entscheidung; Feldintegration und weitergehende G2-Aussagen bleiben
  gesperrt. Der MCM-Wahrnehmungsfeldkern bleibt aktiv.
- Der S1-PP-Abschluss ist ausdruecklich angenommen. G2/D3 bleibt nur
  technische Infrastruktur: Schema, Validatoren, Operatoren,
  Ressourcenledger, Comparatoren und Baselineadapter bleiben erhalten, sind
  aber keine Kandidatenevidenz. Weitere G2-Gleichungen, G2-Runtime,
  G2-Feldlaeufe und G2-Funktionsentscheidungen sind gesperrt. Ein neuer
  Forschungsabschnitt beginnt erst nach einer neuen ausdruecklichen
  fachlichen Richtungsentscheidung.
- S1-HG beendet den Frozen-E1-Probezweig. Frozen-E1 berechnet aus demselben
  unveraenderten Zustand denselben Adapter und verwendet denselben Integrator
  wie die Fixed-Adapter-Baseline. Der geplante 45-Arm-Lauf wird nicht
  ausgefuehrt.
- Das MCM-Wahrnehmungsfeld und seine kontrollierte Testinfrastruktur bleiben
  der belastbare technische Kern.

## Offene Substrathypothese

Der folgende DTS-1-Abschnitt dokumentiert die historische Herkunft der
technischen Dreirollenbaseline. DTS-1/T1 und daraus abgeleitete
Free/Blocked-Trajektorien sind keine aktive Kandidatenentwicklung. Die
S1-PP-Abschlussannahme oeffnet diesen Zweig nicht erneut.

S1-HH bindet genau einen moeglichen lokalen, ressourcenbegrenzten und nicht auf
einen vor der Probe fixierten Adapter reduzierbaren Kandidaten. DTS-1 besitzt die
drei Ressourcenrollen frei, leitend gebunden und voruebergehend refraktaer.

S1-LN uebernimmt diese Strukturbindung fuer `B3/P_IH_ATTENUATION` als
statische C10-Konzervierung von Rollenledger, lokaler und globaler Identitaet,
bevor eine dynamische Ausfuehrungsrunde freigegeben wird.

DTS-1 ist bisher nur ein Funktions- und Falsifikationsvertrag. Es gibt keine
ausgewaehlte Gleichung, keine Parameter, keine Runtime und keinen Lauf. Vor
jeder mathematischen Festlegung muessen gebunden bleiben:

- eine eigene technische Funktionsprognose;
- Verwerfungsbedingungen;
- Fixed Adapter, Leaky/Integrator, zweistufiges E1, F3/CONST-V und schneller
  Nachhall als Gegenbaselines;
- direkte Messungen von Abschwaechung und Interferenz;
- ein exaktes endliches Ressourcenledger;
- Freigabe und erneute Beanspruchung lokaler Kapazitaet.

Kann der Kandidat keine eigene Gegenprognose tragen oder wird sein Verlauf von
einer registrierten Baseline vollstaendig erklaert, wird der Kandidat gestoppt.

## Begriffs- und Aussagegrenze

Begriffe wie Gefuehl, Bewusstsein, Erleben, Verstehen, Feldintelligenz, KI und
organische Entwicklung sind keine aktuellen Projektmerkmale und keine
Bezeichnungen fuer technische Messergebnisse. Hypothetische MCM-Memory
bezeichnet ausschliesslich eine offene Entwicklungsrichtung fuer spaetere
MCM-faehige Memory. Eine vorhandene Memory-Faehigkeit oder ein Memory-Nachweis
wird nicht behauptet.

Messbare Zustandsdifferenz, Nachhall, Persistenz, Snapshot, Wiederholbarkeit,
Adapterwirkung oder Substratbilanz duerfen nicht sprachlich zu einer groesseren
Faehigkeit aufgewertet werden. Jede Ergebnisdarstellung trennt:

1. direkte Messung;
2. begrenzte technische Interpretation;
3. offene Hypothese;
4. Nichtnachweis und gesperrte Aussage.

## Forschungsregel

Vor jeder neuen Gleichung stehen Funktionsprognose, Falsifikation,
Gegenbaselines und direkte Ressourcenmessung. Eine neue Richtung benoetigt eine
eigene technische Gegenprognose. Fehlt sie, endet der Zweig mit `STOPP`.

Historische Plaene und Forschungsprotokolle bleiben fuer Reproduzierbarkeit
erhalten. Sie beschreiben fruehere Fragestellungen und sind keine aktuellen
Projektclaims. Fuer neue Arbeit haben diese Dokumente Vorrang:

1. `docs/AKTUELLE_TECHNISCHE_PROJEKTGRENZE.md`;
2. `AKTUELLER_FORSCHUNGSWEG.md`;
3. `docs/S1HH_DYNAMISCHER_SUBSTRAT_FUNKTIONS_UND_FALSIFIKATIONSVERTRAG.md`;
4. `docs/S1LN_B3_PIH_C10_ANATOMY_UND_KONSERVATION_VERTRAG.md`.
