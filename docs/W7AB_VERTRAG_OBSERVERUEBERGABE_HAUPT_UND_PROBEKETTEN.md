# W7-AB: Vertrag der Observeruebergabe fuer Haupt- und Probeketten

## Entscheidung

`SEPARATE_MAIN_AND_PROBE_OBSERVER_HANDOFF_CONTRACT_BOUND`

W7-AB bindet statisch, wie W7-AA-Haupt- und Probeproduktionen spaeter an die
vorhandenen W7-P-/W7-T-Observeradapter uebergeben werden duerfen. Der Vertrag
fuehrt noch keinen Observer aus.

## 1. Exklusive Observerrolle

Zulaessig sind genau die externen Baselines:

- `leak`;
- `sat`;
- `norm`.

Sie beobachten ausschliesslich W7-P-Treiber aus bereits abgeschlossenen
W7-AA-P0-Produktionen. Observer duerfen weder P0, S, H, M, Rezeptorfolgen
noch einen gekoppelten Feldzustand veraendern. Sie sind keine
Organismusfunktion.

## 2. Unveraenderliche Eingangsbindung

Eine spaetere Uebergabe bindet vor dem ersten Observerzustand:

- W7-M-Matrix- und Regionsdigest;
- W7-Y-Gesamtplandigest;
- W7-AA-Gesamtverbrauchsdigest;
- genau sieben Pfadergebnisse in kanonischer W7-Y-Reihenfolge;
- genau 32 Hauptproduktionen und 35 Probeproduktionen;
- die W7-M-Spezifikationen fuer LEAK, SAT und NORM;
- Uhr, Tickrate, Neuronenreihenfolge und P0-Parameter.

W7-AA-Ergebnisse, W7-R-Produktionen und W7-Y-Planobjekte bleiben
unveraendert und werden nicht neu berechnet.

## 3. Ein Treiber je P0-Produktion

Jede W7-AA-Haupt- oder Probeproduktion wird genau einmal mit
`compose_w7r_observer_driver` in einen W7-P-Treiber ueberfuehrt. Der Treiber
muss gemeinsam binden:

- W7-R-Produktionsdigest;
- Matrix-, Pfad- und Quelldigest;
- exaktes Intervall;
- originale Neuronenreihenfolge;
- atomare linksgehaltene S-Segmente;
- terminalen S-Zustand;
- kanonischen Treiberdigest.

LEAK, SAT und NORM erhalten fuer dieselbe Produktion exakt dasselbe
unveraenderliche Treiberobjekt oder drei digestgleiche unveraenderliche
Referenzen. Eine modellspezifische Treibervariation ist unzulaessig.

## 4. Observerhauptketten

Jeder der sieben Pfade besitzt drei getrennte Hauptketten, insgesamt 21:

```text
AB, AG, BA, BG, UA, UB, UG
x
LEAK, SAT, NORM
```

Kontaktpfade starten jedes Modell genau einmal bei Tick 0. U-Pfade starten
jedes Modell genau einmal bei Tick 4. Danach verarbeitet jede Modellkette
die geordneten Haupttreiber ihres W7-AA-Pfads genau einmal.

Nach jedem Segment gilt:

- `advance_w7t_observer_continuation` erhaelt den vorherigen Zustand
  derselben Modell- und Pfadkette;
- Produktions-, Treiber-, Intervall-, Pfad- und Matrixbindung stimmen;
- der neue Zustand wird alleiniger Hauptvorgaenger des naechsten Segments;
- kein bereits verarbeiteter Treiberdigest erscheint erneut;
- P0-Produktion und Treiber bleiben unveraendert.

Alle 21 Hauptketten enden bei Tick 8.

## 5. Observercheckpoint

Checkpoint 0 wird nach Praefixbeobachtung oder direkt auf dem U-Nullstart bei
Tick 4 gebunden. Checkpoint 1 bis 4 folgen jeweils dem naechsten
Haupttreiber.

Pro Pfad, Modell und Checkpoint wird
`checkpoint_w7t_observer_state` genau einmal aufgerufen. Die passive
Checkpointreferenz muss Pfad, Modell, Nummer, Tick und Hauptzustandsdigest
tragen. Sie darf den Hauptzustand nicht veraendern.

## 6. Gleichpfadige Probekopie

Die vorhandene `branch_w7t_observer_state`-Funktion ist fuer
Pfadverzweigungen vorgesehen und verbietet die Quellpfad-ID als Ziel. Sie
darf deshalb nicht fuer einen Probeast desselben Pfads missbraucht oder
aufgeweicht werden.

Eine spaetere Implementierung benoetigt eine isolierte technische
Probehuelle. Sie enthaelt mindestens:

- Pfad, Modell, Checkpoint und Probeast-ID;
- Digest des W7-T-Hauptzustands am Kopierpunkt;
- eine objektgetrennte, inhaltlich identische W7-T-Zustandskopie;
- gleichen Zustandsdigest und gleiche vollstaendige Baselinelatenz;
- gleichen Vorgaenger-, Verzweigungs- und Treiberhistorienstand;
- eigenen Huellendigest;
- `returns_to_main = false`.

Die Kopie darf keine neue Pfad-ID, keinen Nullstart und keinen geaenderten
W7-T-Zustandsdigest erfinden.

## 7. Observerprobeaeste

Jede der 35 W7-AA-Probeproduktionen erzeugt fuer jedes Modell einen eigenen
Probeast, insgesamt 105. Der Probeast:

1. beginnt mit der gleichpfadigen Kopie des Hauptobserverzustands am
   Checkpoint;
2. erhaelt den W7-P-Treiber der zugeordneten W7-AA-Probeproduktion;
3. wird genau einmal mit `advance_w7t_observer_continuation` fortgesetzt;
4. bindet Messung, Probeendzustand und Fortsetzungsdigest nur im Probeast.

Probeendzustand, Probeausgabe, Messung und Treiberhistorie duerfen niemals
Hauptkette, andere Modelle, andere Pfade oder andere Proben fortsetzen.

## 8. Modelltrennung und NORM-Grenze

LEAK, SAT und NORM besitzen auch bei digestgleicher Treiberfolge getrennte
Objekte, Zustandsdigests und Fortsetzungsdigests. Ein Modellzustand darf
keinen anderen Modellarm initialisieren oder fortsetzen.

NORM fuehrt ausschliesslich seinen nichtnormalisierten Leaky-Latentzustand
weiter. Seine normalisierte `observer_output_trace` bleibt Ausgabe und darf
weder Haupt- noch Probeendzustand speisen.

Erlaubte Messrollen bleiben ausschliesslich:

- `observer_output_linf`;
- `observer_output_trajectory_l2`;
- `observer_state_linf`;
- `observer_ticks`;
- `observer_output_trace`.

## 9. Rueckwirkungsgegenkontrollen

Eine spaetere Implementierung muss mindestens folgende Kontrollen binden:

1. **Modellreihenfolge:** Verarbeitung in LEAK-SAT-NORM und umgekehrter
   Reihenfolge liefert je Modell dieselben Digests.
2. **Haupt-/Probereihenfolge:** Probe zuerst oder Hauptsegment zuerst liefert
   je Ast denselben Fortsetzungsdigest.
3. **Checkpointpassivitaet:** Checkpointerzeugung vor oder nach der
   Probekopie veraendert den Hauptzustandsdigest nicht.
4. **P0-Unveraenderlichkeit:** Alle W7-AA-Produktions-, Zustands- und
   Gesamtverbrauchsdigests bleiben vor und nach Obserververarbeitung gleich.

Diese Kontrollen pruefen nur technische Unabhaengigkeit. Sie sind keine
Feld- oder Funktionsbefunde.

## 10. Ergebnis- und Digestrollen

Ein spaeteres Observerpfadergebnis bindet mindestens:

- W7-AA-Pfadverbrauchsdigest;
- Modell-ID;
- Anfangszustandsdigest;
- geordnete Haupttreiber- und Hauptfortsetzungsdigests;
- fuenf Hauptcheckpointdigests;
- fuenf Probehuellen-, Probetreiber- und Probefortsetzungsdigests;
- terminalen Hauptzustandsdigest bei Tick 8;
- kanonischen `observer_path_consumption_digest`.

Der globale `observer_seven_path_consumption_digest` bindet die 21
Pfad-/Modellergebnisdigests in Pfad- und Modellreihenfolge sowie die
Gegenkontrolldigests. Er enthaelt keine Pfadbewertung, Rangfolge,
Schwellenentscheidung oder Rueckgabe an P0.

## 11. Pflichtkontrollen

Eine spaetere Implementierung muss mindestens pruefen:

- genau 21 getrennte Observerhauptketten;
- exakt dieselbe Haupttreiberfolge fuer alle drei Modelle eines Pfads;
- einmalige Nullstarts bei Tick 0 oder 4;
- terminalen Haupttick 8;
- 105 objektgetrennte Observerprobeaeste;
- gleiche Zustandsdigests am Kopierpunkt bei verschiedener Objektidentitaet;
- passende W7-AA-Probeproduktion und W7-P-Treiber je Probeast;
- keine Probe-zu-Haupt-, Probe-zu-Probe- oder Modell-zu-Modell-Fortsetzung;
- nichtnormalisierte NORM-Latenz in jeder Fortsetzung;
- alle Gegenkontrollen aus Abschnitt 9;
- deterministische Wiederholung der 21 Ergebnis- und Gesamtdigests;
- unveraenderte W7-M-, W7-Y- und W7-AA-Digests;
- fehlende Exporte aus `current_api`;
- keine Reports, Browserstarts oder Laufmarker.

## 12. Harte Stopplinien

Die Implementierung muss stoppen, wenn:

- ein Observer an einem Checkpoint oder Probeast neu auf null gesetzt wird;
- `branch_w7t_observer_state` fuer denselben Pfad aufgeweicht wird;
- ein Probezustand den Hauptpfad fortsetzt;
- LEAK-, SAT- oder NORM-Zustaende gekreuzt werden;
- Modelle unterschiedliche Treiberdigests fuer dieselbe Produktion erhalten;
- ein Probe- oder Haupttreiber doppelt verarbeitet wird;
- NORM seine normalisierte Ausgabe als Latenz fortsetzt;
- Observerwerte P0, S, H, M oder gekoppelte Modelle beeinflussen;
- Observermessungen zwischen Pfaden gerankt oder interpretiert werden;
- ein Report oder Forschungslauf erzeugt wird.

## 13. Aussagegrenze

W7-AB ist nur ein statischer Observeruebergabevertrag. Es wurde keine
Observerhaupt- oder Probekette ausgefuehrt. Auch eine spaetere korrekte
Ausfuehrung waere eine externe Erklaerungsbaseline. Daraus folgen keine
Feldfunktion, kein Memory, keine Feldzeit, Organisation, Topologie, Semantik,
Selbstregulation oder KI.

## 14. Verwendete Quellen

- `docs/W7S_VERTRAG_SEGMENTUEBERGREIFENDE_OBSERVERFORTSETZUNG.md`
- `docs/W7T_IMPLEMENTIERUNG_SEGMENTUEBERGREIFENDE_OBSERVERFORTSETZUNG.md`
- `docs/W7Y_IMPLEMENTIERUNG_NICHTAUSFUEHRENDER_SIEBENPFAD_PLANADAPTER.md`
- `docs/W7AA_IMPLEMENTIERUNG_P0_ONLY_SIEBENPFAD_VERBRAUCHER.md`
- `mcm_field_organism/w7p_measurement_compositor.py`
- `mcm_field_organism/w7r_p0_s_completion_producer.py`
- `mcm_field_organism/w7t_observer_continuation.py`
- `mcm_field_organism/w7aa_p0_seven_path_consumer.py`

## 15. Naechster Schritt

W7-AC darf den isolierten Obserververbraucher, die gleichpfadige
Probehuelle und ihre Vertragstests implementieren. Er darf ausschliesslich
W7-P/W7-T auf den bereits vorhandenen W7-AA-Produktionen im Arbeitsspeicher
ausfuehren. Keine gekoppelte Matrix, kein Browser, Report oder
Forschungslauf.
