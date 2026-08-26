# W7-Z: Vertrag fuer den P0-only-Siebenpfad-Planverbrauch

## Entscheidung

`P0_ONLY_SEVEN_PATH_PLAN_CONSUMPTION_CONTRACT_BOUND`

W7-Z bindet statisch, wie der nicht ausfuehrende W7-Y-Plan spaeter mit dem
vorhandenen W7-R-P0-S/H-Produzenten verbraucht werden darf. Der Vertrag
fuehrt noch keinen Pfad und keine Probe aus.

## 1. Exklusive Modellgrenze

Der spaetere Verbraucher darf ausschliesslich den substratfreien P0-Arm
verwenden:

- S/H-Fast-Field mit W7-R-Parametern `1.0`, `0.5` und Leckrate `0.0`;
- kein M-Substrat;
- kein Entwicklungszustand;
- keine CAP-, F3-, LIN-, CONST-V-, MOB- oder Interventionsdynamik;
- keine LEAK-, SAT- oder NORM-Observerfortsetzung;
- keine W7-P-Messkomposition;
- keine Ergebnisbewertung oder Pfadentscheidung.

P0 ist eine technische rezeptorgetriebene Gegenbaseline. Sein Verlauf ist
keine MCM-Memory-, Feldzeit- oder Organismusfunktion.

## 2. Unveraenderliche Eingangsbindung

Jeder Verbrauch bindet vor dem ersten Zustand:

- genau einen W7-M-Adapter;
- genau eine passende W7-W-Quellenfamilie und Autorisierung;
- genau einen W7-Y-Plan;
- W7-M-Matrix- und Regionsdigest;
- Basis-, Symmetrie-, Autorisierungs- und Gesamtplandigest;
- Uhr `organism.mcm_f3_k2b` und Tickrate `1_000_000`;
- kanonische Pfadreihenfolge `AB`, `AG`, `BA`, `BG`, `UA`, `UB`, `UG`.

Keine Bindung darf nach einem P0-Ergebnis erneuert, angepasst oder ersetzt
werden.

## 3. P0-Startrollen

### 3.1 Kontaktpfade

AB, AG, BA und BG erhalten je eine eigene P0-Hauptkette. Fuer jeden Pfad
wird `build_initial_w7r_p0_state` mit Starttick 0 aufgerufen. Der gebundene
Praefix wird anschliessend genau einmal ueber
`produce_w7r_p0_s_completion_states` bis Tick 4 verarbeitet.

Gemeinsame A- oder B-Quellen erlauben keine gemeinsame veraenderbare
P0-Instanz. Jeder Pfad besitzt sein eigenes Anfangs- und Endzustandsobjekt.

### 3.2 U-Pfade

UA, UB und UG beginnen je mit einem eigenen
`build_initial_w7r_p0_state` bei Tick 4. S und H sind exakt null. Es wird
kein Praefix und keine kuenstliche Null-, Gap- oder Uniformsequenz erzeugt.

Das U bezeichnet im P0-only-Arm nur: keine vorherige Rezeptorexposition in
dieser technischen Fast-State-Kette. P0 besitzt kein M. Daher ist dieser
Nullstart weder ein uebernommener uniformer M-Zustand noch eine Aussage ueber
einen Organismuszustand.

## 4. Hauptfortsetzung

Nach Checkpoint 0 verarbeitet jeder Pfad genau die vier in W7-Y gebundenen
Hauptsegmente:

```text
4-5 -> 5-6 -> 6-7 -> 7-8
```

Fuer jedes Segment gelten gemeinsam:

- Anfangszustand ist exakt der vorherige Hauptendzustand desselben Pfads;
- Starttick entspricht exakt dessen Endtick;
- Pfad-, Matrix-, Uhr- und Neuronenbindung bleiben gleich;
- Quelldigest, Sequenzen, Intervall und additive Autorisierung stammen
  unveraendert aus dem W7-Y-Segment;
- W7-R verarbeitet das Segment genau einmal;
- Produktions- und Endzustandsdigest werden in derselben Hauptkette gebunden.

Ein Probeendzustand oder Zustand eines anderen Pfads ist niemals als
Hauptanfangszustand zulaessig.

## 5. P0-Checkpoints

Checkpoint 0 wird auf dem P0-Zustand bei Tick 4 gebunden. Checkpoint 1 bis 4
folgen jeweils dem zugeordneten Hauptsegment bei Tick 5 bis 8.

Ein P0-Checkpointresultat enthaelt mindestens:

- W7-Y-Checkpoint- und Pfadplandigest;
- Pfad, Checkpointnummer und Tick;
- vorherigen Hauptproduktionsdigest oder Uniformstartdigest;
- unveraenderten Hauptzustandsdigest;
- Digest der fuer die Probe erzeugten P0-Zustandskopie;
- zugeordneten W7-Y-Probesegmentdigest;
- kanonischen Checkpointresultatdigest.

Der Checkpoint selbst fuehrt keine Zeitentwicklung und keinen Reset aus.

## 6. Isolierte Probeaeste

Vor P0 bis P4 wird der vollstaendige P0-Hauptzustand des Checkpoints in ein
eigenstaendiges Probeobjekt kopiert. Erforderlich sind:

- gleicher Matrix-, Pfad-, Uhr-, Tick- und Zustandsdigest am Kopierpunkt;
- gleiche Neuronenreihenfolge sowie bitgleiche S- und H-Werte;
- getrennte Python-Objektidentitaet fuer Zustand und privates P0-Feld;
- keine gemeinsam veraenderbaren Arrays oder Container;
- unveraenderter Hauptzustand vor und nach der Probe.

Die Probe verarbeitet ausschliesslich das im W7-Y-Checkpoint gebundene
Probesegment. Ihr Anfangstick ist der Checkpointtick, ihr Endtick liegt genau
eine Sekunde spaeter. Probeproduktions- und Probeendzustandsdigest werden nur
im Probeast gebunden.

Die Probe darf ihren Endzustand weder in die Hauptkette noch in einen
anderen Probeast zurueckgeben. P0 bis P3 und das zeitgleich folgende
Hauptsegment muessen aus getrennten Kopien desselben Checkpointzustands
starten.

## 7. Reihenfolge-Gegenkontrolle

Die technische Unabhaengigkeit von Haupt- und Probeast muss mindestens an
einem repraesentativen Checkpoint durch zwei Ausfuehrungsordnungen geprueft
werden:

1. Probe zuerst, danach Hauptfortsetzung;
2. Hauptfortsetzung zuerst, danach Probe.

Hauptendzustand, Probeendzustand und ihre Produktionsdigests muessen je Rolle
zwischen beiden Ordnungen exakt gleich bleiben. Diese Gegenkontrolle belegt
nur fehlende technische Rueckwirkung in der Implementierung.

## 8. Ergebnis- und Digestrollen

Ein spaeteres P0-Pfadergebnis bindet mindestens:

- W7-Y-Pfadplandigest;
- P0-Anfangszustandsdigest;
- geordnete Hauptproduktionsdigests;
- Checkpointresultatdigests 0 bis 4;
- Probeproduktions- und Probeendzustandsdigests 0 bis 4;
- terminalen Hauptzustandsdigest bei Tick 8;
- kanonischen `p0_path_consumption_digest`.

Der globale `p0_seven_path_consumption_digest` bindet die sieben
Pfadergebnisdigests in W7-Y-Reihenfolge. Der zusammengesetzte Digest darf die
bereits in W7-R gebundenen S/H-Werte nur transitiv ueber Zustands- und
Produktionsdigests referenzieren. Er enthaelt keine Interpretation,
Schwellenentscheidung oder Rangfolge.

## 9. Pflichtkontrollen

Eine spaetere Implementierung muss mindestens pruefen:

- genau sieben getrennte P0-Hauptketten;
- Kontaktstart bei Tick 0 und U-Start bei Tick 4;
- null initialisierte, substrat- und entwicklungsfreie P0-Zustaende;
- exakt vier Hauptfortsetzungen und fuenf Checkpoints je Pfad;
- lueckenlose Anfangs-/Endzustandsbindung;
- passende W7-W-Autorisierung fuer additive Segmente;
- genau fuenf getrennte Probeobjekte und Probeproduktionen je Pfad;
- Digestgleichheit und Objekttrennung am Kopierpunkt;
- unveraenderte Hauptzustaende waehrend jeder Probe;
- keine Probe-zu-Haupt- oder Probe-zu-Probe-Fortsetzung;
- Reihenfolge-Gegenkontrolle gemaess Abschnitt 7;
- deterministische Wiederholung aller Pfad- und Gesamtverbrauchsdigests;
- unveraenderte W7-M-, W7-W- und W7-Y-Digests;
- fehlende Exporte aus `current_api`;
- keine Reports, Browserstarts oder Laufmarker.

## 10. Harte Stopplinien

Die Implementierung muss stoppen, wenn:

- ein P0-Zustand ein Substrat oder einen Entwicklungszustand besitzt;
- ein Pfad oder Segment neu auf null gesetzt wird;
- U durch eine Rezeptorsequenz ersetzt wird;
- ein Hauptsegment aus einem Probeendzustand startet;
- Haupt- und Probeast dasselbe private P0-Feldobjekt teilen;
- ein Probeast einen anderen Probeast fortsetzt;
- Quell-, Intervall-, Pfad- oder Autorisierungsbindung von W7-Y abweicht;
- ein Haupt- oder Probesegment doppelt verarbeitet wird;
- Observer-, Mess- oder gekoppelte Modellwerte in P0 zurueckgegeben werden;
- Pfadergebnisse verglichen, gerankt oder als Funktionsbefund interpretiert
  werden;
- ein Report oder Forschungslauf erzeugt wird.

## 11. Aussagegrenze

W7-Z ist nur ein statischer P0-Verbrauchsvertrag. Es wurde kein P0-Pfad und
kein Probeast ausgefuehrt. Auch eine spaetere korrekte P0-Ausfuehrung waere
nur eine technische Fast-State-Gegenbaseline. Daraus folgen keine
Feldfunktion, kein Memory, keine Feldzeit, Organisation, Topologie, Semantik,
Selbstregulation oder KI.

## 12. Verwendete Quellen

- `docs/W7Q_VERTRAG_P0_S_ABSCHLUSSZUSTANDSPRODUZENT.md`
- `docs/W7R_IMPLEMENTIERUNG_P0_S_ABSCHLUSSZUSTANDSPRODUZENT.md`
- `docs/W7X_VERTRAG_SIEBENPFAD_QUELLPLAN_UND_CHECKPOINTKOPIEN.md`
- `docs/W7Y_IMPLEMENTIERUNG_NICHTAUSFUEHRENDER_SIEBENPFAD_PLANADAPTER.md`
- `mcm_field_organism/w7r_p0_s_completion_producer.py`
- `mcm_field_organism/w7w_symmetric_source_family.py`
- `mcm_field_organism/w7y_seven_path_source_plan.py`

## 13. Naechster Schritt

W7-AA darf den isolierten P0-only-Siebenpfad-Verbraucher und seine
Vertragstests implementieren. Er darf ausschliesslich W7-R auf den von W7-Y
gebundenen Haupt- und Probesegmenten im Arbeitsspeicher ausfuehren. Keine
Observer, gekoppelte Matrix, kein Browser, Report oder Forschungslauf.
