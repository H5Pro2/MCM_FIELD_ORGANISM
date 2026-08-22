# S1-VG: MPZ-1 statischer Uebergangsquellen- und Baseline-Nichtduplizierungsaudit

## Freigabe und Grenze

S1-VG prueft ausschliesslich die in S1-VF offengebliebenen Fragen:

- Besitzt jeder MPZ-1-Rollenwechsel eine lokale Ursache und Senke?
- Kann eine Prototypdisposition ohne externen Paarcode und ohne Rohhistorie
  gebildet werden?
- Besitzen Abschwaechung, Aktualisierung, Konflikt und Freigabe verschiedene
  technische Ursachen?
- Verbleibt gegen eine begrenzte konkurrenzfaehige gemeinsame Prototypbank
  eine nicht duplizierte MPZ-1-Prognose?

S1-VG fuehrt keine Gleichung, keinen Parameter, keine Implementierung, keine
Fixture, keine Runtime-, API- oder Snapshotaenderung, keinen Test und keinen
Feldlauf ein.

## Gepruefter Ausgangsstand

S1-VF beschreibt pro vorhandenem Audio-Video-Dockgrenzmotiv eine feste private
Traegermenge mit vier ausschliesslichen Rollen:

- verfuegbar;
- formend;
- stabilisiert;
- loesend.

Ein formender oder stabilisierter Traeger enthaelt eine feste lokale
Prototypdarstellung. S1-VF bindet jedoch bewusst kein Verfahren fuer
Zuordnung, Bildung, Stabilisierung, Aktualisierung, Konflikt, Loesung oder
spaetere Feldrueckwirkung.

Der aktive Feldkern stellt nur lokalen Kontakt, S, H, feste Nachbarschaft und
kausale Feldfortsetzung bereit. Er besitzt keine der genannten
Prototypoperationen.

## Vollstaendiger Uebergangsaudit

### Verfuegbar nach formend

Lokale Feldarbeit allein bestimmt nicht, ob ein neues Grenzmuster einen freien
Traeger beanspruchen oder einem vorhandenen Traeger zugeordnet werden soll.
Dafuer wird mindestens eine der folgenden Zusatzentscheidungen benoetigt:

- Vergleich mit vorhandenen Prototypen;
- Neuheits- oder Distanzentscheidung;
- feste freie-Slot-Auswahl;
- Konkurrenzentscheidung bei mehreren passenden Traegern.

Diese Rollen sind die Aufnahmeoperation einer begrenzten Prototypbank. Ohne
sie bleibt der Wechsel unterbestimmt; mit ihnen ist er bereits durch die
Baseline erklaert.

### Formend nach stabilisiert

Wiederholte aehnliche Exposition verursacht anatomisch noch keine eindeutige
Stabilisierung. Erforderlich waere mindestens:

- Akkumulation einer Haeufigkeit oder eines Vertrauenswerts;
- gleitende Verdichtung des lokalen Musters;
- eine Schwelle oder Rangentscheidung;
- eine feste Anzahl bestaetigender Expositionen.

Jede Variante ist eine Statistik-, Integrator- oder Schwellenoperation der
Prototypbaseline. Der vorhandene Feldkern liefert keine weitere lokale
Stabilisierungsursache.

### Stabilisiert nach stabilisiert mit Aktualisierung

Eine graduelle Aktualisierung verlangt eine Regel, die den bestehenden
Prototyp mit dem neuen lokalen Muster kombiniert. Ohne eine solche Regel gibt
es keine Aktualisierung. Jede fest dimensionierte Kombination ist strukturell
eine gleitende gemeinsame Statistik oder Prototypanpassung.

### Stabilisiert nach loesend

Abschwaechung oder Konflikt loest keinen eindeutigen Rollenwechsel aus, solange
nicht festgelegt wird, ob Zeitablauf, fehlende Bestaetigung, Konkurrenz,
Fehlanpassung oder Kapazitaetsdruck die Loesung auswaehlt. Diese Auswahl ist
eine Zerfalls-, Ersetzungs- oder Verdrangungsregel der Baseline.

### Loesend nach verfuegbar

Die anatomische Bilanz verlangt vollstaendige Freigabe, bestimmt aber nicht
deren Zeitpunkt. Ein Timer, Schwellenwert, vollstaendiges Ueberschreiben oder
explizites Eviction-Ereignis waere erneut eine programmierte
Prototypbankoperation.

### Stabilisierter Traeger zur Feldrueckwirkung

Eine spaetere partielle Probe kann nur dann einen bestimmten Traeger
reaktivieren, wenn Probe und Prototyp verglichen, ein Treffer ausgewaehlt und
das Ergebnis ueber einen Adapter in den Feldschritt eingespeist werden. Genau
diese drei Rollen bilden den Readout einer Prototypbaseline.

Ohne Vergleich und Auswahl existiert keine paarungsspezifische
Wiedererkennungsprognose. Mit Vergleich und Auswahl ist die Prognose nicht
mehr unabhaengig von der gebundenen Gegenbaseline.

## Paarcode- und Lokalitaetspruefung

Ein externer `A1/V1`-Paarcode wird nicht benoetigt, wenn die Prototypbank die
lokalen Werte beider Endpunkte desselben festen Grenzmotivs gemeinsam als
Eingabe liest. Damit ist die Bildung technisch lokal und ohne Semantik
darstellbar.

Dieser Umstand schafft jedoch keine neue Ursache. Er ersetzt nur den externen
Paarcode durch eine fest programmierte gemeinsame Merkmalsdarstellung. Die
Zuordnung zu einem Traeger, ihre Verdichtung und der spaetere Vergleich
bleiben Operationen der gemeinsamen Prototypbaseline.

S/H kann die asynchrone zeitliche Ueberlappung lokal vermitteln. Wird daraus
nur ein gemeinsamer Merkmalswert gebildet, ist auch diese Rolle vollstaendig
durch die Baseline aus aktuellem Feldzustand und Nachhall erklaert.

## Abgleich der vier Funktionsinterventionen

| MPZ-1-Rolle | Vollstaendige Baselineabbildung |
|---|---|
| Stabilisierung durch Wiederholung | Trefferzaehler, gleitende Prototypverdichtung oder Integrator mit Schwelle |
| Abschwaechung | Leaky-Gewicht, Alterswert oder fehlende Bestaetigung |
| Aktualisierung | gemeinsames gleitendes Update des ausgewaehlten Prototyps |
| Konflikt | Konkurrenzscore und Ersetzung des schwaechsten oder unpassendsten Traegers |
| endliche Kapazitaet | feste Anzahl lokaler Prototypslots |
| Freigabe und Wiederverwendung | Eviction und erneute Belegung desselben Slots |
| partielle Wiedererkennung | Aehnlichkeitsvergleich und Winner-Auswahl |
| spaetere Feldwirkung | fester Readoutadapter vom ausgewaehlten Prototyp zum lokalen Feldinput |

Die Baseline benoetigt keine Rohdaten und keine vollstaendige Eingabefolge.
Sie kann dieselbe feste lokale Dimension, dieselbe Traegerzahl, dieselbe
Bilanz und denselben Kandidat-OFF-Pfad verwenden.

## Staerkste Gegenbaseline

Die faire Baseline ist nicht nur ein einzelner gleitender Mittelwert. Sie ist
eine begrenzte lokale gemeinsame Prototypbank mit:

- derselben festen Anzahl lokaler Slots;
- derselben lokalen Audio-Video-Grenzmotifeingabe;
- derselben festen Prototypdimension;
- gemeinsamer Zuordnung und Verdichtung;
- Konkurrenz, Ersetzung und Freigabe;
- demselben spaeteren lokalen Readoutbudget;
- identischem Kandidat-OFF-Pfad.

Diese Baseline ist eine einfachere technische Beschreibung derselben in
S1-VF eingefuehrten Rollen. MPZ-1 besitzt weder einen zusaetzlichen
bilanzierbaren Zustand noch eine andere lokale Ursache, durch die eine
abweichende Prognose entstehen koennte.

## Reduktionsentscheidung

Fuer jede denkbare MPZ-1-Uebergangsrolle gilt eine geschlossene Alternative:

1. Ohne Zuordnungs-, Verdichtungs-, Konkurrenz-, Loesungs- und Readoutregel
   bleibt der Kandidat funktional unvollstaendig.
2. Mit diesen Regeln entspricht der Kandidat strukturell der begrenzten
   konkurrenzfaehigen gemeinsamen Prototypbaseline.

Eine dritte, unabhaengige lokale Uebergangsursache ist im S1-VE-/S1-VF-Vertrag
nicht gebunden. Sie im S1-VG-Audit neu einzufuehren wuerde die
Vorregistrierung nach Kenntnis des Reduktionsbefunds veraendern.

Damit greift die S1-VE-Stoppregel: Die Pflichtbaseline kann Bildung,
Stabilisierung, Aktualisierung, Konflikt, Kapazitaet, Freigabe, partielle
Zuordnung und spaetere Feldrueckwirkung strukturell unter demselben Budget
reproduzieren.

## Verbindliche Entscheidung

```text
S1_VG_LOCAL_PAIR_INPUT_WITHOUT_EXTERNAL_LABEL_IS_POSSIBLE
S1_VG_TRANSITION_SELECTION_NOT_PROVIDED_BY_ACTIVE_FIELD_CORE
S1_VG_FORMATION_REQUIRES_PROTOTYPE_ASSIGNMENT
S1_VG_STABILIZATION_REQUIRES_STATISTIC_OR_THRESHOLD
S1_VG_UPDATE_REQUIRES_MOVING_PROTOTYPE_OPERATION
S1_VG_CONFLICT_AND_RELEASE_REQUIRE_REPLACEMENT_POLICY
S1_VG_LATER_FIELD_EFFECT_REQUIRES_MATCH_AND_READOUT_ADAPTER
S1_VG_BOUNDED_COMPETITIVE_JOINT_PROTOTYPE_BASELINE_COMPLETE
S1_VG_NO_INDEPENDENT_TRANSITION_CAUSE_REMAINS
S1_VG_MPZ1_REDUCED_TO_ENGINEERING_BASELINE
S1_VG_MPZ1_RESEARCH_BRANCH_TERMINALLY_STOPPED
S1_VG_NO_EQUATION_NO_PARAMETER_NO_IMPLEMENTATION_NO_TEST_NO_RUN
S1_VG_NO_MEMORY_FUNCTION_FINDING
```

MPZ-1 wird als eigenstaendiger Forschungskandidat terminal beendet. Die
statische Anatomie aus S1-VF bleibt eine beschreibbare Engineeringbaseline,
aber kein Befund einer neuen MCM-Feldursache.

## Methodischer Erkenntnisgewinn

S1-VG zeigt eine klare Entwicklungsgrenze:

- Technische audiovisuelle Zustandsbildung ist als begrenzte Prototypbank
  konstruierbar und mit dem vorhandenen Rezeptor-/Feldpfad koppelbar.
- Ihre wesentlichen Funktionen muessen jedoch durch Zuordnung, Statistik,
  Konkurrenz und Readout programmiert werden.
- Der bestehende Feldkern erzeugt diese Operationen nicht als eigene lokale
  Ursache.
- Eine solche Engineeringfunktion darf deshalb nicht als neuer
  Kandidatenbefund oder vorhandene MCM-Memory-Funktion bezeichnet werden.

Der negative Kandidatenbefund widerlegt nicht die technische Nutzbarkeit
einer bewusst implementierten perzeptiven Prototypbank. Eine solche
Engineeringentscheidung waere jedoch eine neue ausdrueckliche Richtung mit
eigenem Funktions-, Sicherheits- und Integrationsauftrag.

## Weiteres Vorgehen

Die MPZ-1-Kandidatenforschung pausiert an dieser Stopplinie. Es folgt keine
Gleichung, Parameterwahl, Implementierung, Baselinefixture oder Ausfuehrung.

Ohne neue ausdrueckliche fachliche Entscheidung ist nur die technische Pflege
des bestehenden MCM-Feldkerns zulaessig. Zwei Richtungen duerfen nicht
automatisch aus S1-VG abgeleitet werden:

- eine staerkere Prototypbank unter neuer Kandidatenbezeichnung;
- ein hypothetischer Feldmechanismus, der nur eingefuehrt wird, um die
  Baseline zu uebertreffen.

## Projektgrundlagen

- [S1-VF Anatomie-, Ursachen- und Bilanzvollstaendigkeitsaudit](S1VF_MPZ1_STATISCHER_ANATOMIE_URSACHEN_UND_BILANZVOLLSTAENDIGKEITSAUDIT.md)
- [S1-VE Kandidaten- und Falsifikationsvertrag](S1VE_MPZ1_STATISCHER_KANDIDATEN_UND_FALSIFIKATIONSVERTRAG.md)
- [Aktiver neutraler Feldkern](../mcm_field_organism/neutral_local_field_substrate.py)
- [Aktive Audio-Video-Feldgeometrie](../mcm_field_organism/audio_video_field_geometry.py)
- [Rezeptorenverteiler](../mcm_field_organism/receptor_distributor.py)
- [DTS-1 Ressourcenanatomie-Baseline](S1HI_DTS1_DISKRETE_RESSOURCENANATOMIE_UND_ERHALTUNGSIDENTITAET.md)
- [ACM-1H terminaler Zweigabschluss](S1UL_ACM1H_STATISCHER_ZWEIGABSCHLUSS_UND_KONSOLIDIERUNGSAUDIT.md)
