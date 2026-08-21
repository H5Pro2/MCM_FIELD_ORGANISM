# S1-QE: Statischer Feldhandoff-Kompatibilitaetsaudit fuer A0 und A3

## Status und Umfang

S1-QE prueft ausschliesslich, ob die in S1-QD noch offenen Adaptergruppen A0
und A3 mit bereits vorhandenen, unveraenderten Projektpfaden ein
vollstaendiges S1-QA-Feldresultat erzeugen koennen.

Der Audit:

- liest nur vorhandene Quell-, Test- und Vertragsoberflaechen;
- fuehrt keinen Test und keinen Feldlauf aus;
- implementiert keinen Adapter und keine Baseline;
- bindet keine neue Gleichung, Parameter, Werte, Toleranzen oder Fixture;
- wertet keine historischen Ergebniswerte aus;
- trifft keine Kandidaten- oder Funktionsentscheidung.

Auditentscheidung:

```text
A0_EXISTING_STATELESS_COMPLETE_FIELD_PATH_IDENTIFIED
A3_EXISTING_KERNELS_REMAIN_OBSERVER_ONLY_NO_COMPLETE_FIELD_HANDOFF
MANDATORY_BASELINE_PACKAGE_REMAINS_NOT_EXECUTABLE
NO_IMPLEMENTATION_NO_EXECUTION_NO_RESULT_DECISION
```

## Auditkriterien

Ein vorhandener Pfad gilt nur dann als reiner Feldhandoff, wenn er bereits
vor S1-QE gemeinsam alle folgenden Eigenschaften besitzt:

- er akzeptiert den normalen gemeinsamen Rezeptor- und Geometriepfad;
- er erzeugt ein vollstaendiges `SharedMCMField`;
- er setzt S und H ohne neu zu erfindende Regel;
- er liest keinen Kandidatenzustand und keine Orchestrierungsrolle;
- er fuehrt keinen verdeckten Verlauf oder globalen Speicher;
- er ist atomar und fail-closed;
- seine Wiederverwendung erfordert keine Gleichungs- oder
  Rueckwirkungsaenderung.

Eine technisch leicht programmierbare Konvertierung ist noch kein
vorhandener Handoff. Sobald entschieden werden muesste, wie ein lokaler
Output auf S oder H wirkt, liegt eine neue Feldfunktion vor.

## A0-Bestandsoberflaechen

### Lokaler Referenzkern

`mcm_field_organism/carrier_baselines.py` enthaelt
`stateless_baseline(contact)`. Der Kern gibt den aktuellen Kontakt als
Aktivierung und einen gleich grossen Nullnachhall aus. Er speichert keinen
Verlauf, liefert aber nur `CarrierFrame` und kein gemeinsames Feld.

Dieser Kern bleibt eine strukturelle Referenz fuer die A0-Funktionsklasse. Er
muss nicht ueber einen neuen CarrierFrame-zu-Feld-Adapter gezwungen werden,
wenn bereits ein feldnativer funktionsgleicher Pfad existiert.

### Vorhandener feldnativer Pfad

`mcm_field_organism/mcm_neuron_layer.py` enthaelt
`receptor_projection_baseline(drive)`. Die Funktion:

- liest ausschliesslich `drive.perception.receptor_contact`;
- verwendet bei natuerlicher Kontaktabwesenheit den Nullwert;
- setzt die Aktivierung auf den aktuellen Kontakt;
- setzt H ausdruecklich auf null;
- liest weder vorherige Aktivierung noch vorheriges H;
- gibt direkt `MCMNeuronOutput` zurueck.

`SharedMCMField.advance(...)` besitzt bereits die vollstaendige
Feldmaterialisierung fuer diesen Transitionstyp. Der Pfad:

- ordnet alle Kontakte ueber die registrierten Docks zu;
- schreibt jeden Knoten atomar in dieselbe naechste Schicht;
- erhaelt Feld-, Geometrie-, Dock- und Zeitidentitaet;
- gibt ein vollstaendiges `SharedMCMField` zurueck;
- verwirft ungueltige Verteilungen, Zeiten oder Transitionoutputs.

Im Bestand wird genau diese Kombination bereits mehrfach technisch
verwendet. Vorhandene Tests beschreiben unter anderem die atomare Projektion
aller Docks in eine gemeinsame Schicht und die vollstaendige Aktivierungsfolge.
S1-QE fuehrt diese Tests nicht erneut aus und uebernimmt keine Laufwerte.

### Funktionsgleichheit der A0-Rollen

Auf der gemeinsamen normalisierten Kontaktoberflaeche besitzen
`stateless_baseline` und `receptor_projection_baseline` dieselbe technische
Gegenprognose:

```text
Aktivierung = nur aktueller Kontakt
H           = kein Nachhall
Privatcarry = keiner
```

Diese Darstellung ist eine Rollenidentitaet und keine neu gebundene
Gleichung. Der feldnative Pfad ist bereits implementiert.

### A0-Zulassungsgrenze

A0 darf spaeter nur auf einem neutralen Feld ohne Substrat- oder
Entwicklungszustand starten. `SharedMCMField.advance` kann zwar einen bereits
vorhandenen Nullsubstratzustand formal weitertragen; fuer A0 waere selbst
dieser zusaetzliche Carry unnoetig und deshalb unzulaessig.

Die spaetere A0-Huelle darf:

- den bestehenden feldnativen Pfad direkt aufrufen;
- eine Zustandslosmarkierung und S1-QD-Provenienz ergaenzen;
- das vorhandene komplette Feld unveraendert weiterreichen.

Sie darf nicht:

- `CarrierFrame` nachtraeglich in ein Feld umrechnen;
- einen privaten Kontaktverlauf tragen;
- ein Substrat, eine Entwicklung oder einen Nachhall erhalten;
- `receptor_projection_baseline` in die aktive Feld-API hochstufen;
- alte Runner- oder Profilhuellen wiederverwenden.

A0 erhaelt damit den statischen Status:

```text
EXISTING_COMPLETE_STATELESS_FIELD_PATH_PRESENT
NEW_S1PZ_LIFECYCLE_ENVELOPE_ONLY_REQUIRED
```

Dies ist noch keine Implementierungs- oder Ausfuehrungsfreigabe.

## A3-Bestandsoberflaechen

### W7-N-Lokalkerne

`mcm_field_organism/w7n_capacity_function_baselines.py` enthaelt fuer
Saettigung und Normalisierung:

- einen `W7NLocalBaselineState` mit einer latenten Koordinate pro Ort;
- einen `W7NLocalBaselineResult` aus Folgezustand und lokalem Output;
- eine Frischzustandsfabrik;
- eine reine lokale Fortschreibung ueber vorgegebenes Evidence und Dauer.

Diese Kerne geben weder `MCMNeuronOutput` noch `SharedMCMField` aus. Sie
binden insbesondere kein gemeinsames H und keine vollstaendige weitere
S-Fortsetzung.

### Vorhandene Observerpfade

`w7p_measurement_compositor.py` konsumiert die lokalen Outputs nur als
Observertrajektorie und berechnet daraus Diagnosegroessen.
`w7t_observer_continuation.py` kann den privaten W7-N-Zustand kausal ueber
mehrere Observersegmente tragen, bleibt aber ebenfalls auf dieser
Messoberflaeche.

Der bereits vorhandene W7-AU-Bestandsaudit klassifiziert LEAK, SAT und NORM
ausdruecklich als Familie `observer` mit Messoberflaeche
`observer-output`. Keiner dieser Pfade ist dort terminal feldvergleichbar.

### Fehlende Feldentscheidung

Kein vorhandener A3-Pfad entscheidet gleichzeitig:

- ob der lokale Output S ersetzt, S ergaenzt oder nur beobachtet;
- ob H nullgesetzt, erhalten oder neu fortgeschrieben wird;
- wie die Ausgabe in die gemeinsame Feldkopplung gelangt;
- wie eine normalisierte globale Ausgabe kausal auf einzelne Feldorte wirkt;
- wie ein vollstaendiges S1-QA-Feldresultat atomar entsteht.

Jede Wahl in dieser Liste aendert die technische Gegenprognose. Ein Wrapper,
der `MCMNeuronOutput` aus W7-N-Werten baut und anschliessend
`SharedMCMField.advance` aufruft, waere deshalb keine reine Formabbildung,
sondern eine neue explizite Feldfunktion.

### A3-Sperrstatus

Saettigung und Normalisierung erhalten den gemeinsamen Status:

```text
LOCAL_OBSERVER_KERNEL_PRESENT
NO_UNCHANGED_COMPLETE_FIELD_HANDOFF_PRESENT
NEW_FIELD_FUNCTION_CONTRACT_REQUIRED_BEFORE_ANY_IMPLEMENTATION
```

Observerresultate duerfen nicht als S-Fortsetzungen in S1-QA eingesetzt
werden. A3 darf auch nicht still durch B3, B5, B6 oder eine
Observernormalisierung ersetzt werden.

## A0/A3-Gegenueberstellung

| Kriterium | A0 | A3 SAT/NORM |
|---|---|---|
| lokaler Kern vorhanden | ja | ja |
| vollstaendiger Feldtransitionstyp vorhanden | ja | nein |
| S-Rolle bereits eindeutig | aktueller Kontakt | offen |
| H-Rolle bereits eindeutig | null | offen |
| privater Zustand | keiner | lokaler latenter Zustand |
| komplettes Feld bereits erzeugbar | ja | nein |
| nur neue S1-PZ-Huelle erforderlich | ja | nein |

Die asymmetrische Entscheidung verhindert, dass die technische Luecke von A3
als blosse Formatfrage behandelt wird.

## Informations- und API-Grenze

`receptor_projection_baseline` und `stateless_baseline` sind im
Root-Exportbestand als historische Referenzrollen klassifiziert. S1-QE
aendert diese Klassifikation nicht. Eine spaetere Baselinehuelle darf den
vorhandenen A0-Pfad privat und eng begrenzt wiederverwenden; sie darf ihn
nicht zu einer primaeren aktiven Feldoperation machen.

Die W7-N-Kerne bleiben ebenfalls private technische Referenzkerne. Sie werden
nicht in den primaeren MCM-Wahrnehmungsfeldkern eingebaut.

## Paketweite Auswirkung

A0 ist auf Zustands- und Feldoberflaechenebene statisch anschliessbar. A3 ist
es nicht. Weil S1-QA alle Pflichtbaselines fuer das vollstaendige gemeinsame
Feldprofil verlangt, bleibt das gesamte Pflichtbaselinepaket vorerst:

```text
MANDATORY_BASELINE_PACKAGE_NOT_EXECUTABLE
```

Das Fehlen von A3 erzeugt kein positives Residuum und erlaubt weder das
Weglassen der Rolle noch einen Kandidatenlauf.

## Fail-Closed-Regeln

S1-QE wird verletzt, wenn spaeter:

- A0 einen vorherigen Feldwert oder privaten Zustand liest;
- A0 auf einem Feld mit Substrat- oder Entwicklungszustand startet;
- die historische A0-Rolle in die aktive Feld-API verschoben wird;
- ein `CarrierFrame` durch eine neue Rechenregel in ein Feld transformiert
  wird;
- A3-Observeroutput als S1-QA-Feldreadout ausgegeben wird;
- fuer A3 S oder H ohne eigenen vorab gebundenen Funktionsvertrag gesetzt
  werden;
- A3 still entfaellt oder durch eine funktional andere Baseline ersetzt wird;
- ein fehlender Feldhandoff als Kandidatenresiduum gilt.

## Aussagegrenze

S1-QE ist ein statischer Anschlussaudit. Er implementiert und bestaetigt
keine Baselineausfuehrung. Es gibt keine neue Feldgleichung, keine Parameter,
keinen Kandidaten und keinen Befund zu einer hypothetischen MCM-Memory. Der
primaere MCM-Wahrnehmungsfeldkern bleibt unveraendert.

## Genau ein naechster Schritt

Als einziger Anschluss ist zulaessig:

```text
S1-QF - statischer A3-Feldfunktions-, Nichtsubstitutions- und
        Falsifikationsvertrag fuer Saettigung und Normalisierung
```

S1-QF soll vor jeder Gleichung entscheiden, welche eigenstaendige
Feldgegenprognose SAT und NORM jeweils gegen A1, B2/B3, B5/B6, M1 und M5
besitzen muessen, welche S- und H-Ausgaberollen prinzipiell erforderlich sind
und wann eine A3-Unterrolle als redundant verworfen wird. Keine Gleichung,
Parameter, Werte, Implementierung, Fixture, Runtimeaenderung,
Testausfuehrung oder Ergebnisentscheidung.
