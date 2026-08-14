# W7-Q: Vertrag des P0-S-Abschlusszustandsproduzenten

## Entscheidung

`P0_S_COMPLETION_STATE_PRODUCER_BOUND`

W7-Q bindet statisch, wie aus einem eingefrorenen W7-M-Quellsegment genau
eine modellunabhaengige Folge von P0-S-Zustaenden fuer W7-P entstehen darf.
Der Vertrag implementiert und berechnet noch keinen Produzenten.

## 1. Technische Rolle

Der Produzent ist ein passiver Adapter um den vorhandenen exakten neutralen
Fast-Field-Pfad. Er darf:

- einen gebundenen P0-Anfangszustand fortsetzen;
- vollstaendige Rezeptorabschlussgruppen atomar uebergeben;
- S unmittelbar nach jeder atomaren Abschlussgruppe beobachten;
- den exakten S/H-Endzustand fuer eine spaetere P0-Fortsetzung binden;
- S-Abschlusswerte an den W7-P-Kompositor uebergeben.

Er darf keine CAP-, F3-, LIN-, CONST-V-, MOB- oder Interventionsdynamik
ausfuehren. Er ist keine Organismusfunktion und kein Bestandteil des
persistenten Feldzustands.

## 2. Gebundene Eingaben

Jede Produktion erfordert explizit:

1. genau einen `W7MCapacityFunctionMatrixAdapter`;
2. genau ein Quellsegment aus dessen eingefrorenem Digestinventar;
3. die zu diesem Digest gehoerenden beiden `ReceptorTimeSequence`-Folgen;
4. einen expliziten Organismus-Abschlusshorizont
   `(start_tick, end_tick]`;
5. einen P0-Anfangszustand mit S und H in der unveraenderten
   W7-M-Neuronenreihenfolge;
6. `response_time_seconds = 1.0`;
7. `afterimage_time_constant_seconds = 0.5`;
8. `leak_rate_per_second = 0.0`;
9. den W7-M-Takt `organism.mcm_f3_k2b` mit `1_000_000` Ticks pro Sekunde.

Die Parameter stammen aus W7-L und duerfen nicht nach einer spaeteren
Observeranpassung veraendert werden.

## 3. P0-Anfangszustand

Der erste unabhaengige P0-Arm beginnt mit den S- und H-Vektoren der frischen
W7-M-Feldgeometrie. Diese muessen exakt null sein. Eine Fortsetzung beginnt
mit dem zuvor gebundenen exakten P0-Endzustand desselben Quellpfads.

Ein Anfangszustand muss enthalten:

- `matrix_digest`;
- `source_path_id`;
- `clock_id` und Starttick;
- die geordnete Folge der 84 Neuron-IDs;
- den vollstaendigen S-Vektor;
- den vollstaendigen H-Vektor;
- einen kanonischen Zustandsdigest.

Ein Zustand eines gekoppelten Modells oder eines anderen Pfads darf nicht als
P0-Anfangszustand verwendet werden. M wird weder benoetigt noch in die
P0-Bindung aufgenommen. Falls eine bestehende Runtime aus technischen
Gruenden einen Nullarm verlangt, ist dessen M-Zustand inert und darf weder
gemessen noch als Substratrolle ausgegeben werden.

## 4. Vollstaendige Ereignisuebergabe

Fuer das explizite Intervall wird genau ein `MCMFieldStepTime` verwendet.
`handoff_receptor_completion_groups` muss nachweisen:

- keine Abschluesse vor oder am Start;
- keine Abschluesse nach dem Intervallende;
- jedes Ereignis innerhalb des Horizonts genau einmal zugeordnet;
- unveraenderte Modalitaets-, Snapshot- und Zeitidentitaeten.

Danach werden die Gruppen ueber
`map_proposal_batch_to_transient_docks` und
`project_transient_docks_to_neuron_inputs` verlustfrei auf die vorhandene
W7-M-Dockgeometrie abgebildet. Es gibt keine Mittelung zwischen Modalitaeten,
keine Labelbildung und keine inhaltliche Gewichtung.

## 5. Atomare P0-Entwicklung

Der Produzent verwendet direkt
`advance_neutral_fast_shared_field_transient` mit den gebundenen Parametern.
Der allgemeine F3-Wrapper wird nicht erweitert, weil sein P0-Zweig den
vorhandenen privaten Zustandsobserver derzeit nicht weiterreicht.

Zwischen Abschlussgrenzen entwickelt der exakte neutrale Fast-Field-Pfad S
und H. An einer Abschlussgrenze werden alle dort eingetroffenen lokalen
Kontakte aus demselben Vorzustand atomar auf S angewendet. Erst danach darf
genau eine Beobachtung fuer diesen Tick entstehen. Die Reihenfolge
gleichzeitiger Modalitaeten darf das Resultat nicht beeinflussen.

Der Observer muss die uebergebenen Arrays sofort in unveraenderliche Tupel
kopieren und `None` zurueckgeben. Er darf weder Arrays veraendern noch Werte
an Runtime, Rezeptorpfad oder naechste Abschlussgruppe zurueckgeben.

## 6. Abschluss- und Endzustaende

Pro tatsaechlicher Rezeptorabschlussgrenze wird genau ein Datensatz erzeugt:

```text
boundary_kind = EVENT_COMPLETION
completion_tick
ordered_neuron_ids
s_values
```

S wird nach der atomaren Punktaktualisierung beobachtet. H wird intern fuer
die P0-Fortsetzung erhalten, aber nicht an LEAK, SAT oder NORM ausgegeben.

Liegt das Intervallende nach der letzten Ereignisgrenze, wird zusaetzlich ein
exakter Endzustand erzeugt:

```text
boundary_kind = INTERVAL_END
end_tick
ordered_neuron_ids
s_values
h_values
```

Dieser Endzustand dient ausschliesslich als naechster P0-Anfangszustand. Im
W7-P-Treiber darf sein S-Wert nur den terminalen Zustand aktualisieren; er
veraendert kein bereits abgelaufenes linksgehaltenes Segment. Faellt die
letzte Ereignisgrenze mit dem Intervallende zusammen, wird kein doppelter
Tick erzeugt; derselbe exakte Endzustand ergaenzt die vorhandene
Ereignisbeobachtung um H.

## 7. Neuronenordnung und Wertebereich

Die Reihenfolge ist immer exakt
`adapter.initial_field.layer.neurons`. Sie darf nicht sortiert oder aus einer
Map rekonstruiert werden. Jeder S- und H-Vektor besitzt genau 84 endliche
Werte im geschlossenen Bereich `[-1, 1]`.

W7-P uebernimmt nur S und genau diese Reihenfolge. Eine Rezeptorwertfolge,
Dockprojektion oder ein H-Vektor darf nicht als P0-S-Treiber umbenannt werden.

## 8. Digestbindung

Der kanonische Produktionsdigest umfasst mindestens:

- W7-M-Matrix- und Regionsdigest;
- Quellsegmentdigest;
- P0-Anfangszustandsdigest;
- Intervall, Uhr und Tickrate;
- P0-Parameter;
- geordnete Neuron-IDs;
- alle Ereignisgrenzen und S-Abschlussvektoren;
- den vollstaendigen S/H-Endzustand.

Ein W7-P-Treiber muss denselben Matrix- und Quellsegmentdigest tragen. Eine
Fortsetzung muss den vorherigen Produktionsdigest und Endzustandsdigest
referenzieren. Ein anderer Feldmodellarm darf diese Bindung nicht liefern.

## 9. Determinismus- und Gegenkontrollen

Eine spaetere Implementierung muss mindestens pruefen:

- identische Eingaben ergeben bitgleich denselben Zustands- und
  Produktionsdigest;
- Vertauschung gleichzeitiger Modalitaeten aendert keinen S-Zustand;
- geteilte und ungeteilte kontaktfreie Intervalle ergeben denselben
  Endzustand innerhalb des vorhandenen exakten numerischen Bodens;
- keine Eingabe, kein Feld und keine Rezeptorfolge wird mutiert;
- jeder Abschluss erscheint genau einmal;
- Endzustand und anschliessender Anfangszustand sind identisch gebunden;
- alle LEAK-/SAT-/NORM-Arme erhalten denselben W7-P-Treiberdigest;
- `current_api`, Browserpfade und Snapshot-Schemata bleiben unveraendert.

## 10. Harte Stopplinien

Die Implementierung muss stoppen, wenn:

- ein Quellsegmentdigest nicht zu W7-M gehoert;
- Abschlussgruppen fehlen, doppelt sind oder ausserhalb des Intervalls liegen;
- gleichzeitige Ereignisse nacheinander als getrennte S-Zustaende erscheinen;
- eine sortierte statt der originalen Neuronenreihenfolge verwendet wird;
- S direkt aus Rezeptorwerten statt aus dem P0-Fast-Field gelesen wird;
- H, M, CAP-Diagnosen oder Observerausgaenge den Treiber speisen;
- ein aktiver Substrataustausch im P0-Produzenten laeuft;
- ein Endzustand rueckwirkend ein vorheriges Treibersegment veraendert;
- private Beobachtung in die oeffentliche API exportiert wird.

## 11. Aussagegrenze

W7-Q ist nur ein statischer technischer Vertrag. Es wurde kein
P0-Quellsegment ausgefuehrt und kein S-Abschlusszustand erzeugt. Daraus
folgen keine Feldfunktion, kein Memory, keine Ressourcenwiederverwendung,
keine Feldzeit, Organisation, Semantik, Selbstregulation oder KI.

## 12. Verwendete Quellen

- `docs/W7L_VORREGISTRIERUNG_KAPAZITAETSFUNKTION_UND_GEGENBASELINES.md`
- `docs/W7M_IMPLEMENTIERUNG_IN_MEMORY_KAPAZITAETSFUNKTIONSMATRIX_ADAPTER.md`
- `docs/W7O_MESSVERTRAG_FELDKAUSALITAET_UND_OBSERVERBASELINES.md`
- `docs/W7P_IMPLEMENTIERUNG_IN_MEMORY_MESSKOMPOSITOR.md`
- `mcm_field_organism/receptor_proposal_handoff.py`
- `mcm_field_organism/transient_dock_trajectory.py`
- `mcm_field_organism/transient_neuron_input.py`
- `mcm_field_organism/neutral_local_field_substrate.py`
- `mcm_field_organism/mcm_f3_runtime.py`

## 13. Naechster Schritt

W7-R darf den isolierten P0-S-Abschlusszustandsproduzenten und seine
Vertragstests implementieren. Er darf nur einzelne explizit uebergebene
W7-M-Quellsegmente im Arbeitsspeicher verarbeiten. Ein vollstaendiger A/B-
Pfad, eine Hauptmatrix, ein Browserstart, ein Report oder ein Forschungslauf
bleiben gesperrt.
