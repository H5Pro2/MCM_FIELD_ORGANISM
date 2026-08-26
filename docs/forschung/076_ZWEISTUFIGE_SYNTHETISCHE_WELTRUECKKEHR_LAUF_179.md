# Lauf 179: Zweistufige synthetische Weltrueckkehr

## Forschungsfrage und Auftrag

Geprueft wurde, ob eine regulaere, unterbrochene oder fest vertauschte erste
Rueckkehr die Aufnahme desselben zweiten regulaeren Weltkontakts veraendert
und ob etwaige Unterschiede vollstaendig durch den bestehenden linearen
Zustand und `afterimage` erklaert werden.

## Verwendete Quellen

Tatsaechlich verwendet wurden:

- aktueller Uebergabeeingang und Lauf 178;
- `AGENTS.md`;
- `docs/forschung/075_SYNTHETISCHE_WELTRUECKKEHR_KAUSALBASELINES_LAUF_178.md`;
- `docs/architektur/018_MINIMALER_SIMULIERTER_EFFEKTORVERTRAG.md`;
- `mcm_field_organism/simulated_return_causal_probe.py`;
- `mcm_field_organism/simulated_effector_world.py`;
- `mcm_field_organism/simulated_world_mcm_path.py`;
- `mcm_field_organism/mcm_neuron_layer.py`;
- `mcm_field_organism/sensor_mcm_field.py`;
- zugehoerige Tests und der vorhandene JSON-Runner.

Externe Quellen wurden nicht verwendet.

## Verwendete Dateien und Schnittstellen

Erweitert wurden:

- `mcm_field_organism/simulated_return_causal_probe.py`;
- `tests/test_simulated_return_causal_probe.py`;
- `tools/run_simulated_return_causal_probe.py`.

Verwendet wurden dieselben Welt-, Rezeptor- und Feldschnittstellen wie in
Lauf 178 sowie der bestehende synchrone zweite Aufruf von
`SensorMCMField.advance` mit `receptor_projection_baseline`.

## Durchgefuehrte Schritte

Fuer sieben Startpositionen und beide aeusseren ersten Interventionen `-1`
und `+1` wurden drei frische Arme ausgefuehrt:

1. regulaere erste Rueckkehr;
2. erste Rueckkehr als Nullkontakt unterbrochen;
3. erste Rezeptorkanaele fest durch `i -> 6-i` vertauscht.

Anschliessend erhielt jeder Arm dieselbe zweite aeussere Intervention `0`
auf demselben Weltzustand und damit denselben regulaeren zweiten
Rezeptorkontakt. Es entstanden 14 Faelle und 42 Beobachtungen.

Gemessen wurden beide Welt-Digests, erster Fast State, zweiter
Rezeptorkontakt, zweite Aktivierung, zweites `afterimage`, Layer-Digest und
die lokalen Samples im zweiten Layer. Der Lauf wurde vollstaendig wiederholt.

## Messergebnisse und Gegenbaselines

```text
Fokussierte Tests:                              5 passed in 1.30s
Faelle:                                         14
Beobachtungen:                                  42
Identische zweite Welt in allen drei Armen:     14 / 14
Gleiche zweite Fast States, paarweise:          28 / 28
Zweite Aktivierung entspricht Rezeptorkontakt:  42 / 42
Zweites afterimage vollstaendig null:           42 / 42
Layer-Digest anders nach Unterbrechung:          14 / 14
Layer-Digest anders nach Kanaltausch:            12 / 14
Lokale Samples aus erstem Zustand vorhersagbar: 42 / 42
Deterministische Wiederholung:                  ja
Feld-zu-Effektor-Anschluss:                     nein
```

Die zwei gleichen Layer-Digests beim Kanaltausch entsprechen erneut dem
Fixkanal 3 der Spiegelung. Alle anderen Layer-Digest-Unterschiede lagen in
den lokalen Sample-Payloads der ersten Aktivierung. Die verwendete
Projektionsbaseline las diese Samples nicht und setzte die zweite Aktivierung
ausschliesslich aus dem aktuellen Rezeptorkontakt sowie `afterimage = 0`.

## Einordnung

**Beobachtet:** Derselbe zweite Weltkontakt erzeugte in allen Armen denselben
zweiten Aktivierungs- und `afterimage`-Vektor.

**Beobachtet:** Die Layer-Digests unterschieden sich weiterhin, wenn die
erste Aktivierung unterschiedlich gewesen war.

**Technische Interpretation:** Diese Digest-Unterschiede dokumentieren den
vorherigen Zustand in den unveraenderlichen Wahrnehmungs-Samples. Sie
veraendern unter `receptor_projection_baseline` nicht die spaetere
Feldaufnahme und sind damit kein funktionaler Memorybefund.

**Nullbefund:** Fuer eine durch die erste Rueckkehr veraenderte zweite
Fast-State-Aufnahme wurde kein Hinweis gefunden.

## Grenzen und nicht gepruefte Annahmen

- Der Lauf war vollstaendig synthetisch und testtreibergesteuert.
- Es bestand keine MCM-zu-Effektor-Verbindung.
- Die zweite Intervention war fuer alle Arme fest `0` und keine Handlung.
- Die historische separate Sensorfeldbaseline ist nicht die aktive
  Organismus-Gesamtarchitektur.
- Nur zwei abgeschlossene Zeitstufen wurden untersucht.
- Die Projektionsbaseline ignoriert lokale Samples definitionsgemaess.
- Eine andere, bereits vorhandene Transition wurde nicht verglichen.
- Es wurde keine neue Transition, Memoryvariable oder Topologie eingefuehrt.
- Reale physische Weltwirkung, Semantik, Agency und Organisation wurden nicht
  untersucht.

## Konkrete Schlussfolgerung

Die erste synthetische Rueckkehr hinterlaesst technische Sample-Payloads im
zweiten Layer-Digest, veraendert aber bei identischem zweiten Weltkontakt
weder Aktivierung noch `afterimage`. Der gesamte Befund ist durch die
vorhandene synchrone Samplebildung und die zustandslose lineare
Rezeptorprojektion erklaert.

Damit gilt die Stopplinie: Aus diesem Pfad darf keine Memoryfunktion
abgeleitet und keine Memoryvariable ergaenzt werden. Eine Zielabweichung ist
nicht erkennbar.

## Naechster begrenzter Forschungslauf

Als Lauf 180 sollte geprueft werden, ob im aktiven `SharedMCMField` mit
derselben zweistufigen Kontaktfamilie derselbe Nullbefund gilt. Dabei sind
ausschliesslich vorhandene Docks, `ReceptorDistributor`,
`SharedMCMField.advance` und `receptor_projection_baseline` zu verwenden.
Zu vergleichen sind Fast State, `afterimage`, Layer-Payload und Snapshot-
Digest. Neue Feld-, Memory- oder Effektorregeln bleiben ausgeschlossen.
