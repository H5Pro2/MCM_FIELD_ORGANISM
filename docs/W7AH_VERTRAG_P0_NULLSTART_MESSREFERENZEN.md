# W7-AH: Vertrag fuer P0-Nullstartmessreferenzen

## Entscheidung

`P0_ZERO_START_MEASUREMENT_REFERENCE_CONTRACT_BOUND`

W7-AH bindet statisch, wie zu den 35 W7-AG-CAP-Messrollen spaeter
substratfreie P0-Messreferenzen mit identischem S/H-Nullstart entstehen
duerfen. Der Vertrag fuehrt noch keine P0-Probe aus und vergleicht keine
Messwerte.

## 1. Technische Ausgangslage

W7-R stellt bereits bereit:

- `build_initial_w7r_p0_state` fuer jeden der sieben Pfade und jeden
  nichtnegativen Starttick;
- exakt S = H = 0 auf der unveraenderten W7-M-Neuronenreihenfolge;
- ein substrat- und entwicklungsfreies privates `SharedMCMField`;
- P0-Parameter `response_time = 1.0`, `afterimage_time = 0.5` und Leckrate
  `0.0`;
- `produce_w7r_p0_s_completion_states` mit exaktem S/H-Endzustand.

Die W7-R-Ereignisobjekte speichern an Zwischenabschluessen absichtlich nur
S. H ist nur im vollstaendigen Endzustand gebunden. Deshalb kann
`probe_H_linf` oder `probe_SH_trajectory_l2` nicht nachtraeglich aus den
vorhandenen W7-R-Ereignisobjekten rekonstruiert werden.

W7-R, W7-AA und ihre Digests bleiben unveraendert. W7-AH erlaubt keine
Schemaerweiterung ihrer vorhandenen Zustands- oder Produktionsobjekte.

## 2. Unveraenderliche Eingangsbindung

Eine spaetere P0-Messreferenzuebergabe bindet:

- W7-M-Matrixdigest und Neuronenreihenfolge;
- W7-Y-Gesamtplan-, Pfad-, Checkpoint- und Probesegmentdigests;
- W7-AA-P0-, W7-AC-Observer-, W7-AE-CAP- und W7-AG-
  Messuebergabegesamtdigests;
- Uhr `organism.mcm_f3_k2b` und Tickrate `1_000_000`;
- genau die Rollen `AB`, `AG`, `BA`, `BG`, `UA`, `UB`, `UG`;
- genau die Checkpoints 0 bis 4 und ihre Ticks 4 bis 8;
- je Rolle exakt die vorhandene W7-Y-Probe P0 bis P4.

Keine Quelle, Zeitgrenze oder P0-Parameterbindung darf nach einem Messwert
veraendert werden.

## 3. Genau 35 frische P0-Messstarts

Fuer jede Kombination aus Pfad und Checkpoint wird genau ein eigener
Messanfangszustand erzeugt:

```text
start_tick = checkpoint_tick
S = 0
H = 0
M = nicht vorhanden
development = nicht vorhanden
last_distribution = nicht vorhanden
```

Der Zustand wird mit `build_initial_w7r_p0_state` erzeugt. Er uebernimmt
weder den W7-AA-Hauptzustand noch dessen technische Probe. Pfad und Tick sind
Bindungsrollen; sie duerfen keine modellspezifische Eingangsaenderung
bewirken.

Alle sieben Pfade desselben Checkpoints starten inhaltlich gleich, besitzen
aber getrennte Zustands- und Feldobjekte. Keine P0-Messreferenz darf einen
anderen Pfad oder Checkpoint fortsetzen.

## 4. Separate passive P0-Messausfuehrung

W7-AI darf fuer jeden Nullstart einen eigenen Messproduzenten implementieren.
Er muss dieselbe vorhandene technische Kette wie W7-R verwenden:

1. zwei W7-Y-Rezeptorsequenzen kanonisch nach Modalitaet ordnen;
2. Quell- und Sequenzdigest erneut pruefen;
3. Completion-Handoff fuer exakt das Probeintervall bilden;
4. transiente Docks und Neuroneneingaben erzeugen;
5. `advance_neutral_fast_shared_field_transient` mit den festen P0-
   Parametern ausfuehren;
6. S und H passiv an den tatsaechlichen Abschlussgrenzen beobachten;
7. den exakten substratfreien Endzustand binden.

Die Messausfuehrung ist eine getrennte technische Referenz. Sie darf weder
W7-AA fortsetzen noch CAP-, M- oder Observerzustand lesen.

## 5. Passive S/H-Samples

Pro tatsaechlicher Rezeptorabschlussgrenze wird genau ein Sample gebunden:

- Abschlussgrenzentick;
- unveraenderte Neuronenreihenfolge;
- vollstaendiger S-Vektor;
- vollstaendiger H-Vektor;
- kanonischer Sampledigest.

Der Segmentendtick muss enthalten sein. Doppelte Ticks, Interpolation,
Nachabtastung und aus Anfang/Ende geschaetzte Zwischenwerte sind verboten.
Samples bleiben externe Messdaten und werden nicht als naechster P0-Zustand
verwendet.

## 6. W7-R-Endzustandsaequivalenz

Fuer dieselbe Nullstartkopie, dieselbe W7-Y-Probe und dasselbe Intervall wird
zusaetzlich der unveraenderte W7-R-Produzent auf einer getrennten Kopie
ausgefuehrt.

Messproduzent und W7-R-Referenz muessen uebereinstimmen in:

- zugewiesener Ereignisanzahl;
- geordneten Ereignisabschlussgrenzen;
- S-Werten an jeder W7-R-Ereignisgrenze;
- vollstaendigem S/H-Endvektor;
- privatem Endfelddigest und letztem Distributionsdigest;
- Endtick und Neuronenreihenfolge.

Der Messproduzent besitzt einen eigenen Digest, weil er zusaetzlich H-Samples
bindet. Digestungleichheit zwischen den beiden Produktionsformaten ist daher
kein Zustandsunterschied.

## 7. P0-Feldmessrollen

Aus den gebundenen Samples wird genau eine
`W7PFieldMeasurement(model_id = "p0")` pro Pfad und Checkpoint erzeugt:

- `probe_S_linf` als groesste absolute S-Komponente;
- `probe_H_linf` als groesste absolute H-Komponente;
- `probe_SH_trajectory_l2` als diskrete gemeinsame S/H-L2-Norm;
- `probe_observation_ticks` als streng geordnete Abschlussgrenzen.

Die Definitionen muessen exakt den W7-AG-CAP-Messdefinitionen entsprechen.
P0 erhaelt keine M-, Kapazitaets-, Regions- oder Bilanzrolle.

## 8. Vergleichsbereitschaft ohne Vergleich

Erst wenn alle 35 P0-Messreferenzen vollstaendig und gegen W7-R aequivalent
sind, darf die technische Rolle
`p0_absolute_comparison_ready = true` gesetzt werden.

Dieses Kennzeichen bedeutet nur:

- CAP und P0 starten fuer die jeweilige Probe mit S = H = 0;
- Geometrie, Uhr, Tick, Probequelle und Messnorm sind gleich gebunden;
- CAP besitzt zusaetzlich sein unveraendertes checkpointabhaengiges M;
- beide Messseiten sind technisch vergleichbar materialisiert.

Es ist kein Vergleichsergebnis und keine Feldfunktionsentscheidung.

## 9. Ergebnis- und Digestrollen

Ein P0-Messreferenzresultat bindet mindestens:

- Pfad, Checkpoint und Tick;
- W7-Y-Checkpoint- und Probesegmentdigest;
- P0-Nullstartzustandsdigest;
- geordnete S/H-Sampledigests;
- Messproduktions- und Endzustandsdigest;
- W7-R-Referenzproduktions- und Endzustandsdigest;
- Aequivalenzkontrolldigest;
- W7-P-Feldmessung;
- Kennzeichen `substrate_present = false`;
- Kennzeichen `returns_to_p0_main = false`;
- kanonischen Messreferenzdigest.

Der globale `p0_zero_start_measurement_reference_digest` bindet genau 35
Resultate in W7-Y-Reihenfolge, die Reihenfolge-Gegenkontrolle und die
unveraenderten W7-AA-/AC-/AE-/AG-Gesamtdigests. Er enthaelt keine CAP/P0-
Abstaende, Pfadkontraste oder Entscheidung.

## 10. Gegenkontrollen

W7-AI muss mindestens pruefen:

1. **Modalitaetsreihenfolge:** kanonische und vertauschte Eingabereihenfolge
   liefern dieselben Mess- und Endzustandsdigests.
2. **Rollenreihenfolge:** kanonische und umgekehrte Verarbeitung der 35
   Rollen liefert je Rolle denselben Digest.
3. **W7-R-Aequivalenz:** Abschnitt 6 gilt fuer jede Rolle.
4. **Nullstartgleichheit:** alle sieben Startvektoren desselben Checkpoints
   sind wertgleich, aber objektgetrennt.
5. **Eingangspassivitaet:** W7-AA, W7-AC, W7-AE und W7-AG bleiben
   unveraendert.

## 11. Noch gesperrte Auswertung

Auch nach W7-AI bleiben bis zu einem weiteren statischen Auswertungsvertrag
gesperrt:

- absolute CAP/P0-Differenzen;
- Pfad- und Checkpointkontraste;
- Lebenszyklusprofile;
- numerische Bodenentscheidungen;
- Ressourcenfreisetzungs- oder Wiederverwendungsentscheidungen;
- Interventionen und weitere Modellarme;
- Forschungsclaims jeder Art.

## 12. Pflichtkontrollen

Eine spaetere Implementierung muss mindestens pruefen:

- genau 35 substratfreie P0-Nullstarts und Messresultate;
- S = H = 0 an jedem Start;
- exakte Pfad-, Checkpoint-, Tick- und Probequellenbindung;
- vollstaendige, streng geordnete S/H-Samples;
- identische W7-P-Normdefinitionen wie W7-AG;
- vollstaendige W7-R-Endzustandsaequivalenz;
- keine M- oder Kapazitaetsrolle;
- alle Gegenkontrollen aus Abschnitt 10;
- deterministischen Gesamtmessreferenzdigest;
- fehlende Exporte aus Paketwurzel und `current_api`;
- keine Reports, Browserstarts oder Laufmarker.

## 13. Harte Stopplinien

Die Implementierung muss stoppen, wenn:

- ein W7-AA-Haupt- oder Probezustand als Messnullstart verwendet wird;
- ein CAP-, M- oder Observerwert in P0 einfliesst;
- H-Zwischenwerte aus W7-R-S-Endpunkten geschaetzt werden;
- Mess- und W7-R-Endzustand voneinander abweichen;
- Pfade desselben Checkpoints unterschiedliche Startwerte erhalten;
- P0 eine Ressourcenrolle erhaelt;
- Vergleichsbereitschaft vor 35 vollstaendigen Aequivalenznachweisen gesetzt
  wird;
- Messwerte bereits verglichen oder interpretiert werden;
- ein Report oder Forschungslauf erzeugt wird.

## 14. Aussagegrenze

W7-AH ist ausschliesslich ein statischer P0-Messreferenzvertrag. Es wurde
keine P0-Probe ausgefuehrt und kein CAP/P0-Wert verglichen. Daraus folgen
keine Feldfunktion, kein Memory, keine Feldzeit, Organisation, Topologie,
Semantik, Selbstregulation oder KI.

## 15. Verwendete Quellen

- `docs/W7Q_VERTRAG_P0_S_ABSCHLUSSZUSTANDSPRODUZENT.md`
- `docs/W7R_IMPLEMENTIERUNG_P0_S_ABSCHLUSSZUSTANDSPRODUZENT.md`
- `docs/W7AF_VERTRAG_PASSIVE_CAP_MESSUEBERGABE.md`
- `docs/W7AG_IMPLEMENTIERUNG_PASSIVE_CAP_MESSUEBERGABE.md`
- `mcm_field_organism/neutral_local_field_substrate.py`
- `mcm_field_organism/w7r_p0_s_completion_producer.py`
- `mcm_field_organism/w7p_measurement_compositor.py`
- `mcm_field_organism/w7y_seven_path_source_plan.py`
- `mcm_field_organism/w7ag_passive_cap_measurement_handoff.py`

## 16. Naechster Schritt

W7-AI darf den isolierten P0-Nullstartmessproduzenten, 35 Messreferenzen und
ihre Vertragstests implementieren. W7-R, W7-AA und W7-AG muessen
unveraendert bleiben. Erst bei vollstaendiger W7-R-Aequivalenz darf das
technische Bereitschaftskennzeichen gesetzt werden. Keine CAP/P0-Auswertung,
Intervention, kein Browser, Report oder Forschungslauf.
