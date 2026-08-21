# S1-QA: Statischer Beobachtungs-, Bilanz- und Lebenszyklus-Comparatorrollenvertrag

## Status und Umfang

S1-QA bindet ausschliesslich die passiven Beobachtungsrollen, die spaeteren
Bilanzpflichten, die vollstaendigen Kontrastgruppen und die atomare
Entscheidungsordnung fuer die S1-PZ-Expositionsfamilien F, T, I, C, R und U.

S1-QA enthaelt:

- keinen Kandidaten und keine Zustandsanatomie;
- keine Gleichung, Parameter oder Konfigurationswerte;
- keine numerischen Schwellen oder Toleranzen;
- keine konkreten Payloads, Digests oder Fixture;
- keine Comparatorimplementierung;
- keine Runtimeaenderung, keinen Test und keinen Feldlauf;
- keine Ergebnisentscheidung.

Verbindliche Entscheidung:

```text
PASSIVE_S1PX_LIFECYCLE_OBSERVATION_BALANCE_AND_COMPARATOR_ROLES_BOUND
ATOMIC_GATE_ORDER_BOUND_NO_PARTIAL_FUNCTION_DECISION
NO_VALUES_NO_CANDIDATE_NO_IMPLEMENTATION_NO_EXECUTION
```

## Grundregel der Beobachtung

Jede Beobachtung ist passiv. Sie darf weder Feld noch privaten Modellzustand
fortschreiben, keine Gleichung aufrufen, keinen Parameter waehlen und kein
spaeteres Ereignis beeinflussen.

Ein Checkpoint wird erst nach einem vollstaendig abgeschlossenen Intervall
oder nach der registrierten Readoutprobe aufgenommen. Zwischenzustandslesen
waehrend eines atomaren Modellschritts ist unzulaessig.

Der spaetere Comparator erhaelt nur bereits vollstaendige, unveraenderliche
Resultatbuendel. Er darf Kandidat, Baseline, Orchestrator oder Feldkern nicht
starten und keine fehlende Beobachtung nachberechnen.

## Fuenf getrennte Beobachtungsebenen

### O1 - Gemeinsame Expositionsprovenienz

Jeder Checkpoint muss spaeter binden:

- Expositionsfamilie und Arm ausschliesslich als Orchestrierungsmetadatum;
- vollstaendige geordnete Historienprovenienz;
- Geometrie- und Knotenreihenfolge;
- Rezeptor- und Kontaktprovenienz;
- vollstaendige Zeit- und Intervallreihenfolge;
- Frischzustands- und Carryprovenienz;
- Angleichungs- und Probenprovenienz;
- Modellrolle und unveraenderten Konfigurationsdigest;
- atomaren Abschlussstatus.

Diese Metadaten duerfen waehrend der Ausfuehrung nicht in eine Modellgleichung
gelangen.

### O2 - Gemeinsamer Feldzustand

Vor und nach jeder vergleichenden Probe werden spaeter in kanonischer
Knotenreihenfolge vollstaendig beobachtet:

- aktueller Rezeptorkontakt;
- S;
- H;
- Feldtakt und Geometrieidentitaet;
- der vollstaendige Feldzustandsdigest;
- die vollstaendige weitere S-Fortsetzung nach der Probe.

Der S1-PX-Hauptreadout ist die vollstaendige vorzeichenbehaftete
S-Fortsetzung. Ein Betrag, eine Norm, ein einzelner ausgewaehlter Knoten oder
ein nachtraeglich gewaehlter Skalar darf sie nicht ersetzen. Abgeleitete
Skalare duerfen spaeter nur zusaetzliche Diagnostik sein.

H bleibt Beobachtung und Angleichungskontrolle. Eine verbleibende
H-Differenz macht den betreffenden Vergleich ungueltig; sie ist kein
Kandidatenresiduum.

### O3 - Privater Modellzustand

Jedes zustandsbehaftete Modell muss seinen vollstaendigen privaten Zustand an
allen registrierten Checkpoints durch einen kanonischen Zustandsdigest
binden. Der Comparator prueft Vollstaendigkeit, Carry und Konfigurationsbezug,
interpretiert Baselinezustaende aber nicht kandidatenartig.

Private Zustaende verschiedener Modelle muessen weder gleich aussehen noch
gleiche Digests besitzen. Entscheidend ist, dass jedes Modell seinen eigenen
Zustand vollstaendig und ohne verdeckten globalen Zustand traegt.

### O4 - Kandidateninterne Bilanz

Ein spaeterer Kandidat muss vor seiner Gleichung eine vollstaendige lokale und
globale Bilanzoberflaeche deklarieren. S1-QA waehlt deren Zustandsrollen noch
nicht aus.

Die spaetere Bilanzbeobachtung muss mindestens enthalten:

- alle kandidateninternen Zustandskoordinaten des registrierten Ortes;
- ihre vollstaendige lokale Summe oder explizite Dissipationsbuchung;
- die globale Summe ueber die endliche Testgeometrie;
- jeden Transfer zwischen spaeter deklarierten Rollen;
- jeden zulaessigen Zu- oder Abfluss mit derselben Kausalquelle;
- Vor- und Nachzustand jedes Bildungs-, Konkurrenz-, Gap-, Freigabe- und
  Wiederverwendungsintervalls;
- einen Bilanzrest und einen vollstaendigen Zustandsdigest.

Clipping, Nachnormierung, stilles Nullsetzen, nicht beobachteter globaler
Speicher und Observer-only-Zaehler sind verboten. Eine Bilanz darf keine
fehlende Feldwirkung ersetzen.

Baselines erhalten die Kandidatenbilanz nicht als Eingabe. Sie tragen und
belegen ausschliesslich ihren eigenen privaten Zustand.

### O5 - Technische Diagnostik

Numerik-, Endlichkeits-, Determinismus-, Nullpfad-, Ablations- und
Fehlerdiagnostik bleibt getrennt von Feldreadout und Bilanz. Diagnostik darf
keinen ausgefallenen Funktionskontrast in einen positiven Befund umdeuten.

## Vollstaendiges Resultatbuendel

Ein spaeteres Kandidaten- oder Baslineresultat ist nur vergleichbar, wenn es
atomar fuer alle registrierten Expositionsarme vorliegt. Das Buendel muss
mindestens binden:

- Schema- und Vertragsidentitaeten;
- Modellklasse und Konfigurationsidentitaet;
- vollstaendige Expositions- und Frischzustandsprovenienz;
- alle O1- bis O3-Beobachtungen;
- bei einem Kandidaten zusaetzlich alle O4-Beobachtungen;
- alle technischen O5-Gates;
- Ablations- und Vollpfadkontrollen, soweit fuer die Modellrolle anwendbar;
- eine kanonische Komponentenordnung;
- einen Eigendigest und genau einen Abschlussstatus.

Fehlt ein Arm oder Checkpoint, bleibt das gesamte Lebenszyklusresultat
`not_computable`. Teilergebnisse werden nicht verglichen.

## Kontrastgruppe F - Bildung und spaetere Feldwirkung

Die F-Gruppe vergleicht die vollstaendigen A-Probenfortsetzungen aus:

1. fokaler A-Geschichte;
2. belastungsangepasster entfernter C-Geschichte;
3. reiner Gap-Geschichte.

Vor dem Vergleich muessen aktueller Kontakt, S und H nachweislich angeglichen
sein. Die drei vollstaendigen signed Feldvektoren bleiben gemeinsam erhalten.

Eine spaetere Kandidatenzulassung verlangt:

- einen vorregistrierten A-gegen-C-Kontrast;
- einen vorregistrierten A-gegen-Gap-Kontrast;
- keinen unzulaessigen Rest im Angleichungsgate;
- eine passende Readoutablation, die den kandidatengetragenen Anteil unter
  ansonsten identischer Probe beseitigt.

S1-QA legt noch keine Richtung, Mindestgroesse oder Toleranz fest.

## Kontrastgruppe T - Wiederholung und Abschwaechung

Die T-Gruppe bindet die vollstaendigen A-Probenfortsetzungen nach dem kurzen
und dem laengeren A-Geschichtspraefix. Beide Praefixe bleiben als getrennte
Frischreplikate erhalten.

Spaeter muessen gemeinsam ausgewertet werden:

- Feldfortsetzung am fruehen Readout;
- Feldfortsetzung am spaeteren Readout;
- vollstaendige Kandidatenbilanz an beiden Punkten;
- passende Leaky-, Integrator-, Saettigungs- und Clampbaselineverlaeufe.

Ein kleinerer spaeterer Readout allein ist keine gueltige Abschwaechung. Die
Bilanz- und Baselinegates muessen denselben Verlauf erklaerungsoffen
mitfuehren.

## Kontrastgruppe I - Spezifische lokale Interferenz

Die I-Gruppe haelt drei vollstaendige A-Readouts zusammen:

- lokale B-Konkurrenz;
- gleich belastete nichtlokale C-Kontrolle;
- zeitangepasste Gap-Kontrolle.

Der Comparator muss alle drei Paarrollen in fester Reihenfolge fuehren:

1. lokal gegen nichtlokal;
2. lokal gegen Gap;
3. nichtlokal gegen Gap.

Nur die gemeinsame Dreierstruktur kann spaeter lokale Interferenz von
allgemeiner Last und reinem Zeitverlauf trennen. Ein einzelner Paarvergleich
darf keine Interferenzentscheidung erzeugen.

## Kontrastgruppe C - Endliche lokale Kapazitaet

Die C-Gruppe bindet vor und nach der lokalen, entfernten oder Gap-Mittelphase:

- vollstaendigen Feldzustand;
- vollstaendigen privaten Kandidatenzustand;
- lokale und globale Bilanz;
- spaetere A-Probenfortsetzung.

Ein spaeterer Kapazitaetsbefund benoetigt gemeinsam:

- eine vorab deklarierte endliche lokale Obergrenze;
- direkte lokale Beanspruchung im B-Arm;
- keine entsprechende lokale Beanspruchung im gleich belasteten C-Arm;
- keine Erklaerung allein durch aktuelle freie Menge oder Capacity-Clamp;
- eine erhaltene oder explizit dissipative Gesamtbilanz.

Die konkrete Ressourcenanatomie und Obergrenze bleiben in S1-QA offen.

## Kontrastgruppe R - Funktionsverlust und Freigabe

Die R-Gruppe vergleicht A-Readouts nach fruehem und spaeterem Praefix derselben
normalen Gap-Fortsetzung. Sie bindet gleichzeitig die Kandidatenbilanz vor und
nach jedem Gap.

Funktionale Freigabe darf spaeter nur registriert werden, wenn gemeinsam gilt:

- die alte A-Wirkung ist am spaeten Readout nach vorab gebundener
  Aequivalenzregel funktionslos;
- S/H-Angleichung und aktueller Eingang sind gueltig;
- die Kandidatenbilanz zeigt direkt erneut nutzbare lokale Kapazitaet;
- kein Recoveryschalter, Reset, Clipping oder Neustart wurde verwendet;
- Gap-, Leaky-, Retentions- und Mehrzeitskalenbaselines bleiben im Vergleich.

S1-QA bindet noch keine Aequivalenzschwelle und entscheidet keine Freigabe.

## Kontrastgruppe U - Andere Wiederverwendung

Die U-Gruppe fuehrt die vollstaendigen B-Readouts aus:

- B-Bildung nach spaeter A-Freigaberolle;
- B-Bildung nach frueher, noch nicht freigegebener A-Rolle;
- B-Bildung aus zeitangepasster Frischkontrolle.

Eine spaetere Wiederverwendungsentscheidung verlangt gemeinsam:

- zuvor bestandenen A-Funktionsverlust aus R;
- direkte Bilanzfreigabe vor der B-Geschichte;
- erneute lokale Beanspruchung waehrend der identischen B-Geschichte;
- B-Feldwirkung unter identischer B-Probe;
- vorregistrierte Vergleichbarkeit mit der frischen B-Kontrolle;
- Trennung von Retention, Clamp, globaler Normalisierung und staerkerem
  aktuellem B-Eingang.

Ohne bestandenes R-Gate ist U nicht auswertbar.

## Ablations- und Nullpfadgates

Die Readoutablation prueft nur Kausalitaet der spaeteren Kandidatenwirkung.
Sie darf die vorausgehende Geschichte, den aktuellen Eingang, S, H, die
Geometrie oder eine Baseline nicht veraendern.

Der vollstaendig deaktivierte Kandidatenpfad muss spaeter ueber alle
Expositionsfamilien den vorregistrierten Feldkern-Nullpfad erhalten. Eine
Abweichung stoppt vor jeder Funktionsauswertung.

Eine erfolgreiche Ablation allein ist kein Funktionsbefund. Sie ist ein
Pflichtgate innerhalb des vollstaendigen Lebenszyklus.

## Gemeinsamer Baselinevergleich

Jede Pflichtbaseline liefert dasselbe vollstaendige F/T/I/C/R/U-Buendel mit
derselben aeusseren Geschichte und genau einer Konfigurationsidentitaet.

Der Baselinevergleich verwendet:

- alle vollstaendigen signed Feldfortsetzungen;
- dieselbe Komponentenordnung;
- alle gemeinsamen technischen Checkpoints;
- einen einzigen unveraenderten Parametersatz pro Baseline;
- keine armweise Skalierung, Nachpassung oder Komponentenauswahl.

Kandidateninterne Bilanzwerte gehoeren zu den harten Kandidatengates, aber
nicht zum Feldprofilfit einer Baseline. Kann eine Baseline das vollstaendige
Feldprofil aller Familien reproduzieren, bleibt der Kandidat trotz eigener
interner Bilanz baseline-reduziert.

Eine technisch inkompatible oder fehlende Pflichtbaseline macht den
Gesamtvergleich ungueltig. Sie erzeugt kein positives Residuum.

## Atomare Gateordnung

Ein spaeterer Comparator muss exakt in folgender logischer Reihenfolge
entscheiden:

1. Schema- und Vertragsidentitaet;
2. Vollstaendigkeit aller Modelle, Familien, Arme und Checkpoints;
3. Expositions-, Geometrie-, Zeit- und Rezeptorprovenienz;
4. Frischzustands-, Carry- und Konfigurationsidentitaet;
5. B/C-Belastungsanpassung und Gap-Zeitkontrolle;
6. Eingangs- und S/H-Angleichung vor jedem Readout;
7. Endlichkeit, Determinismus, Bilanz- und Zustandsvollstaendigkeit;
8. Vollpfad-Nullkontrolle;
9. endogene F-Bildung und Readoutablation;
10. T-Abschwaechungsgruppe;
11. I-Dreifachinterferenzgruppe;
12. C-Kapazitaetsgruppe;
13. R-Funktionsverlust und Freigabe;
14. U-andere Wiederverwendung;
15. Vollstaendigkeit und Fairness aller Pflichtbaselines;
16. gemeinsame Baslinereduktion ueber das vollstaendige Feldprofil;
17. atomarer Abschlussstatus.

Ein Fehler in den Stufen 1 bis 8 liefert ausschliesslich
`AUDIT_INVALID_NOT_COMPUTABLE`. Ein gueltiger technischer Verlauf, der eines
der Kandidatengates 9 bis 14 nicht erfuellt, liefert ausschliesslich
`S1PX_FUNCTION_GATE_NOT_SUPPORTED_STOP`. Reproduziert eine Pflichtbaseline
den Gesamtverlauf, lautet der Status ausschliesslich
`S1PX_BASELINE_REDUCED_STOP`.

Nur wenn alle vorherigen Gates gueltig und nicht geschlossen sind, darf der
rein technische Status
`S1PX_JOINT_FIELD_RESIDUAL_PRESENT_REQUIRES_SEPARATE_EVIDENCE_DECISION`
entstehen. Dieser Status ist kein Nachweis einer hypothetischen MCM-Memory.

Teilstatus, Mehrfachfehler, nachtraeglich reparierte Ergebnisse und ein
Best-of-Arms-Urteil sind verboten.

## Comparator-Informationsgrenze

Der spaetere Comparator darf importieren oder erhalten:

- unveraenderliche oeffentliche Resultat- und Receipttypen;
- statische Vertrags- und Schemaidentitaeten;
- reine kanonische Digest- und Endlichkeitshelfer.

Er darf nicht importieren oder aufrufen:

- Kandidaten- oder Baselinegleichungen;
- Runner, Orchestrator oder Feldruntime;
- private Zustandsparser eines Modells;
- Fixturegeneratoren oder Parameterquellen;
- Reparatur-, Retry-, Fit- oder Optimierungslogik.

Der Comparator veroeffentlicht keine privaten Rohzustaende. Er darf nur
kanonische Beobachtungen, Bilanzrecords, Residuen, Gatebelege und seinen
atomaren Abschlussstatus weitergeben.

## Fail-Closed-Verwerfung

S1-QA wird fuer eine spaetere Umsetzung verletzt, wenn:

- ein Checkpoint ein Modell fortschreibt;
- nur ausgewaehlte Knoten, Betraege oder Normen statt voller signed Vektoren
  verglichen werden;
- Kandidatenbilanz oder Armwissen eine Baseline steuert;
- ein Funktionsgate ohne alle zugehoerigen Kontrollen bewertet wird;
- R ohne direkte Bilanzfreigabe oder U ohne bestandenes R-Gate gilt;
- eine Baseline fehlt, inkompatibel ist oder nur einen Teil der Geschichte
  sieht;
- verschiedene Arme verschiedene Konfigurationen verwenden;
- ein Teilresultat trotz ungueltigem Vorgate veroeffentlicht wird;
- Schwellen, Komponenten oder Status nach Kenntnis eines Ergebnisses
  veraendert werden.

## Aussagegrenze

S1-QA legt nur fest, wie ein spaeteres Ergebnis beobachtet und fail-closed
bewertet werden muesste. Es existiert weiterhin kein Kandidat, keine
Zustandsanatomie, keine Gleichung, keine Runtime und kein Funktionsbefund.
Geschlossene Zweige und der primaere MCM-Wahrnehmungsfeldkern bleiben
unveraendert.

## Genau ein naechster Schritt

Als einziger Anschluss ist zulaessig:

```text
S1-QB - statischer Pflichtbaseline-Oberflaechen- und Informationsaudit
```

S1-QB soll fuer jede in S1-PX geforderte Baseline ausschliesslich pruefen,
ob ein vorhandener unveraenderter Kern die S1-PZ-Geschichten und
S1-QA-Beobachtungsrollen aufnehmen kann, welcher reine private Formadapter
fehlt und welche Informationssperren gelten muessen. Keine
Adapterimplementierung, keine neue Baselinegleichung, keine Parameter,
Werte, Fixture, Runtimeaenderung, Testausfuehrung oder Ergebnisentscheidung.
