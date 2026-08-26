# W7-S: Vertrag der segmentuebergreifenden Observerfortsetzung

## Entscheidung

`SEPARATE_OBSERVER_STATE_CONTINUATIONS_BOUND`

W7-S bindet statisch, wie LEAK, SAT und NORM ueber mehrere W7-R-/W7-P-
Segmente fortgesetzt werden duerfen. Der Vertrag implementiert und berechnet
noch keine Observerkette und startet keine Hauptmatrix.

## 1. Gemeinsamer Eingang, getrennte Zustaende

Alle drei Observer erhalten pro Quellsegment exakt denselben digestgebundenen
W7-P-P0-S-Treiber. Gemeinsam sind nur:

- Matrix- und Quelldigest;
- Quellpfad und Organismusintervall;
- Neuronenreihenfolge;
- Treibersegmente und ihre Abschlussgrenzen.

Nicht gemeinsam sind die latenten Zustaende. LEAK, SAT und NORM besitzen je
Pfad genau eine eigene `W7NLocalBaselineState`-Kette. Ein Zustand darf weder
zwischen Modellen ausgetauscht noch zu einem gemeinsamen Observerzustand
gemittelt werden.

## 2. Einmaliger Nullstart

Ein Observerpfad darf genau einmal mit
`build_zero_w7n_local_baseline` beginnen. Der Nullstart ist nur zulaessig,
wenn:

- noch kein Vorgaengerzustand fuer Modell und Pfad existiert;
- der Starttick dem gebundenen Anfang des P0-Pfads entspricht;
- die Zahl der latenten Werte der W7-M-Neuronenanzahl entspricht;
- Modellgleichung und Parameter exakt aus W7-M stammen.

An einer Segment-, Ereignis-, Probe- oder Checkpointgrenze ist kein erneuter
Nullstart zulaessig. Ein Reset waere eine technische Intervention und duerfte
nur als separat vorregistrierte Gegenkontrolle auftreten, nicht als normale
Observerfortsetzung.

## 3. Fortsetzungszustand

Jeder gebundene Observerzustand muss mindestens enthalten:

- `matrix_digest`;
- `source_path_id`;
- `model_id`;
- `equation_id` und Digest der Parameterbindung;
- `clock_id` und `end_tick`;
- originale geordnete Neuron-IDs;
- vollstaendigen latenten W7-N-Zustand;
- Vorgaenger-Zustandsdigest oder expliziten Nullstartmarker;
- zuletzt verarbeiteten W7-P-Treiberdigest;
- kanonischen Zustandsdigest.

Der Zustand ist Observertechnik. Er darf nicht S, H, M, Feldzustand,
Organismuszustand oder Memory genannt werden.

## 4. Segmentfortsetzung

Ein Segment darf nur fortgesetzt werden, wenn:

- sein Starttick exakt dem Endtick des Vorgaengerzustands entspricht;
- Matrix, Pfad, Modell, Gleichung, Parameter und Neuronenreihenfolge gleich
  bleiben;
- der W7-P-Treiber zum W7-R-Produktionsdigest desselben Pfads gehoert;
- Treibersegmente lueckenlos und streng geordnet sind;
- kein Treiberdigest bereits in derselben Kette verarbeitet wurde.

Fuer jedes Treibersegment wird
`advance_w7n_local_baseline` genau einmal mit dessen konstanter S-Evidenz und
exakter Dauer aufgerufen. Der resultierende Zustand ist der Eingang des
naechsten Segments. Nur der letzte Zustand des Quellsegments wird als
Fortsetzungszustand gebunden.

## 5. Ausgaben und NORM-Grenze

Pro Segment duerfen weiterhin nur `observer_`-Rollen ausgegeben werden:

- `observer_output_linf`;
- `observer_output_trajectory_l2`;
- `observer_state_linf`;
- `observer_ticks`;
- `observer_output_trace`.

LEAK gibt seinen latenten Zustand als Ausgang aus. SAT wendet `tanh` nur auf
den aktuellen latenten Zustand an. NORM fuehrt denselben fortgesetzten
Leaky-Latentzustand weiter und normalisiert nur die jeweilige externe
Ausgabe. Die normalisierte NORM-Ausgabe darf niemals als naechster latenter
Zustand verwendet werden.

## 6. Pfadverzweigungen

Die W7-M-Pfade besitzen gemeinsame Praefixe. An einer vorregistrierten
Verzweigungsgrenze wird der vollstaendige Observerzustand jedes Modells
unveraendert in getrennte Pfadbindungen kopiert.

Beispiele:

- der gemeinsame A-Praefix darf je Modell identische Startkopien fuer `AB`
  und `AG` liefern;
- der uniforme Praefix darf je Modell identische Startkopien fuer `UB` und
  `UG` liefern;
- die gespiegelte B-A-Linie verwendet eigene Pfadbindungen und darf nicht mit
  A-B-Zustaenden gekreuzt werden.

Nach der Verzweigung besitzt jede Kopie eine eigene Digestkette. Eine
spaetere Aenderung eines Pfads kann keine andere Kopie veraendern. Das Klonen
ist keine Organismusfunktion, sondern eine externe kontrollierte
Vergleichsoperation.

## 7. Checkpoints und Messungen

Checkpoint 0 bis 4 sind passive Beobachtungsgrenzen. Sie duerfen:

- den aktuellen Observerzustandsdigest festhalten;
- die bis dahin erzeugten `observer_`-Messungen binden;
- dimensionslose Profile gemaess W7-O/W7-P vorbereiten.

Sie duerfen den Zustand nicht veraendern, normalisieren, abschwaechen,
verstaerken oder auf null setzen. Messungen zwischen Pfaden sind nur bei
identischem Checkpoint, Zeitintervall, Treibersupport und Modell zulaessig.

## 8. Digestkette

Der kanonische Fortsetzungsdigest umfasst mindestens:

- Vorgaenger-Zustandsdigest;
- W7-R-Produktionsdigest und W7-P-Treiberdigest;
- Matrix-, Quell- und Pfadbindung;
- Modell-, Gleichungs- und Parameterbindung;
- Start- und Endtick;
- geordnete Neuron-IDs;
- vollstaendigen latenten Endzustand;
- `observer_`-Messrollen des Segments.

Eine Pfadkopie bindet zusaetzlich den Digest der Verzweigungsquelle und eine
neue Zielpfad-ID. Digestketten verschiedener Modelle oder Pfade duerfen nicht
zusammengefuehrt werden.

## 9. Pflichtkontrollen

Eine spaetere Implementierung muss mindestens pruefen:

- segmentierte und als ein Treiber zusammengesetzte Fortsetzung ergeben
  innerhalb des exakten W7-N-Kerns denselben Endzustand;
- identische Ketten sind deterministisch und digestgleich;
- LEAK, SAT und NORM erhalten dieselbe Treiberdigestfolge;
- ihre latenten Zustandsobjekte und Digests bleiben verschieden gebunden;
- NORM setzt mit latentem, nicht normalisiertem Zustand fort;
- Pfadkopien sind am Verzweigungspunkt gleich und danach unabhaengig;
- kein Checkpoint veraendert einen Zustand;
- Eingaben, Treiber, W7-R-Produktion und Vorgaengerzustand bleiben
  unveraendert;
- `current_api`, Runtime, Snapshot-Schema und Reports bleiben unveraendert.

## 10. Harte Stopplinien

Die Implementierung muss stoppen, wenn:

- ein bestehender Pfad an einer Checkpointgrenze neu auf null gesetzt wird;
- Modell-ID, Gleichung oder Parameter zwischen Segmenten wechseln;
- ein SAT-, LEAK- oder NORM-Zustand in ein anderes Modell uebergeht;
- die NORM-Ausgabe als latenter Fortsetzungszustand dient;
- Treiberdigests zwischen Observern abweichen;
- Intervalle ueberlappen, eine Luecke besitzen oder rueckwaerts laufen;
- derselbe Treiber zweimal in einer Kette verarbeitet wird;
- Pfadzustaende nach einer Verzweigung dasselbe veraenderbare Objekt teilen;
- Observerwerte P0, S, H, M oder ein gekoppeltes Feldmodell beeinflussen;
- Observerzustaende als Memory-, Feldzeit- oder Organismuszustand ausgegeben
  werden.

## 11. Aussagegrenze

W7-S ist nur ein statischer Fortsetzungsvertrag. Es wurde keine
Observerkette ausgefuehrt und keine Hauptmatrix berechnet. Selbst eine
spaetere technisch korrekte Observerfortsetzung waere nur eine externe
Erklaerungsbaseline. Daraus folgen keine Feldfunktion, kein Memory, keine
Ressourcenwiederverwendung, keine Feldzeit, Organisation, Semantik,
Selbstregulation oder KI.

## 12. Verwendete Quellen

- `docs/W7N_IMPLEMENTIERUNG_REINER_KAPAZITAETSFUNKTIONS_BASELINEKERNE.md`
- `docs/W7O_MESSVERTRAG_FELDKAUSALITAET_UND_OBSERVERBASELINES.md`
- `docs/W7P_IMPLEMENTIERUNG_IN_MEMORY_MESSKOMPOSITOR.md`
- `docs/W7Q_VERTRAG_P0_S_ABSCHLUSSZUSTANDSPRODUZENT.md`
- `docs/W7R_IMPLEMENTIERUNG_P0_S_ABSCHLUSSZUSTANDSPRODUZENT.md`
- `mcm_field_organism/w7n_capacity_function_baselines.py`
- `mcm_field_organism/w7p_measurement_compositor.py`
- `mcm_field_organism/w7r_p0_s_completion_producer.py`

## 13. Naechster Schritt

W7-T darf einen isolierten Observerfortsetzungsadapter und seine
Vertragstests implementieren. Er darf nur explizit uebergebene W7-P-Treiber
und vorhandene Observerzustaende im Arbeitsspeicher verarbeiten. Keine
vollstaendige Pfadmatrix, kein Browser, Report oder Forschungslauf.
