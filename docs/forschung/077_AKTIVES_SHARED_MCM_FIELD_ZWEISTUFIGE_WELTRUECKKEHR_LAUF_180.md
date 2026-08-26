# Lauf 180: Zweistufige Weltrueckkehr im aktiven SharedMCMField

## Forschungsfrage und Auftrag

Geprueft wurde, ob eine regulare, unterbrochene oder fest vertauschte erste
Rueckkehr die Aufnahme desselben zweiten Weltkontakts im aktiven
`SharedMCMField` veraendert. Zulassig waren nur vorhandene Docks,
`ReceptorDistributor`, `SharedMCMField.advance` und
`receptor_projection_baseline`. Neue Feld-, Memory- oder Effektorregeln wurden
nicht ergaenzt.

## Verwendete Quellen

Tatsaechlich verwendet wurden:

- aktueller Uebergabeeingang und Lauf 179
- `AGENTS.md`
- `docs/forschung/076_ZWEISTUFIGE_SYNTHETISCHE_WELTRUECKKEHR_LAUF_179.md`
- `docs/architektur/018_MINIMALER_SIMULIERTER_EFFEKTORVERTRAG.md`
- vorhandene Shared-Field-, Rezeptorverteiler-, Welt- und Adaptermodule
- zugehoerige Tests und Runnerstile

Externe Quellen wurden nicht verwendet.

## Dateien und Schnittstellen

Neu ergaenzt wurden:

- `mcm_field_organism/shared_return_causal_probe.py`
- `tests/test_shared_return_causal_probe.py`
- `tools/run_shared_return_causal_probe.py`
- dieses Forschungsdokument

Verwendete Schnittstellen:

- `SimulatedWorldState`, `WorldIntervention`, `advance_simulated_world`
- `receptor_frame_from_world`
- `simulated_world_receptor_to_contact_frame`
- `ReceptorContactFrame`, `CommonFieldTime`
- `ReceptorDock`, `ReceptorDistributor`
- `ReceptorDockAnatomy`, `build_shared_mcm_field`
- `SharedMCMField.advance`, `SharedMCMField.snapshot`
- `receptor_projection_baseline`

## Durchgefuehrte Schritte

Fuer sieben Startpositionen und die ersten aeusseren Interventionen `-1` und
`+1` wurden drei frische Arme aufgebaut: regulaere Rueckkehr, Nullkontakt als
technische Unterbrechung und feste Kanalumkehr. Danach erhielten alle drei Arme
dieselbe neutrale Welttransition und denselben regulaeren zweiten Kontakt.

Die sieben Rezeptorwerte wurden ueber sieben bestehende Ein-Kontakt-Docks in
ein gemeinsames zweidimensionales Shared-Feld verteilt. Gemessen wurden Fast
State, `afterimage`, lokale Sample-Payloads, Layer-Digest und vollstaendiger
Snapshot-Digest.

Ein erster fokussierter Test deckte auf, dass der simulierte Rezeptorframe nicht
direkt das gemeinsame `values`-Format besitzt. Die Probe wurde ueber den bereits
vorhandenen Adapter gefuehrt. Danach wurde eine armabhaengige technische
`snapshot_id` entfernt, weil sie den Snapshot-Vergleich unabhaengig vom
Feldzustand verfremdet hatte. Die fachliche Mechanik blieb unveraendert.

## Messergebnisse und Gegenbaselines

```text
Faelle:                                           14
Beobachtungen:                                   42
Identische zweite Welt in allen Armen:           14 / 14
Gleiche zweite Fast States, paarweise:           28 / 28
Zweite Aktivierung entspricht Kontakt:           42 / 42
Zweites afterimage vollstaendig null:             42 / 42
Layer-Digest anders nach Unterbrechung:           14 / 14
Layer-Digest anders nach Kanaltausch:             12 / 14
Snapshot-Digest anders nach Unterbrechung:        14 / 14
Snapshot-Digest anders nach Kanaltausch:          12 / 14
Sample-Payload aus erstem Zustand vorhersagbar:  42 / 42
Deterministische Wiederholung:                   ja
Feld-zu-Effektor-Anschluss:                      nein
```

Die zwei unveraenderten Kanaltauschfaelle liegen auf Kanal 3, dem Fixpunkt der
siebenstelligen Umkehrung.

Verifikation:

```text
Fokussierte Tests:          3 passed in 1.37s
Direkt abhaengige Tests:   42 passed in 11.42s
git diff --check:          ohne Befund
```

## Einordnung

**Beobachtet:** Derselbe zweite Weltkontakt erzeugte in allen Armen identische
Aktivierung und identisches `afterimage`.

**Beobachtet:** Layer- und Snapshot-Digests unterschieden sich genau dort, wo
die erste Aktivierung durch Unterbrechung oder Kanaltausch unterschiedlich war.

**Technische Interpretation:** Die Digest-Unterschiede werden vollstaendig durch
die lokalen Samples des ersten abgeschlossenen Layers erklaert. Die zustandslose
lineare Rezeptorprojektion setzt die zweiten Fast States ausschliesslich aus dem
aktuellen Kontakt.

**Nullbefund:** Auch im aktiven Shared-Feld wurde keine durch die erste Rueckkehr
veraenderte zweite Fast-State-Aufnahme beobachtet.

## Grenzen und nicht gepruefte Annahmen

- Der Lauf war vollstaendig synthetisch und testtreibergesteuert.
- Die Unterbrechung war ein digitaler Nullkontakt, keine physische Blockade.
- Der Kanaltausch war eine feste technische Umkehrung.
- Die Weltinterventionen waren aeusserlich vorgegeben.
- Es bestand keine MCM-zu-Effektor-Verbindung.
- Nur zwei Zeitstufen und die lineare Rezeptorbaseline wurden untersucht.
- Die Sample-Payloads sind technischer Laufzeitzustand, kein Nachweis organischen
  Memorys.
- Reale Weltwirkung, Memory, Semantik, Agency und eigenstaendige Organisation
  wurden nicht nachgewiesen.
- Der System-Python enthielt kein `pytest`; verifiziert wurde in der vorhandenen
  Projektumgebung `.venv`.
- Bestehende fremde Workspace-Aenderungen blieben unangetastet.

## Konkrete Schlussfolgerung

Der Nullbefund aus Lauf 179 reproduziert sich im aktiven `SharedMCMField`.
Fruehere Rueckkehrvarianten bleiben zwar als exakt erklaerbare lokale Samples im
Layer erhalten, veraendern aber die Fast-State-Aufnahme eines identischen
zweiten Kontakts nicht. Layer- und Snapshot-Unterschiede belegen daher keine
Memoryfunktion oder unabhaengige Feldorganisation.

Die Stopplinie gilt weiterhin: Es darf keine Memoryvariable ergaenzt werden.
Eine Zielabweichung ist nicht erkennbar.

## Vorschlag fuer den naechsten begrenzten Forschungslauf

Als Lauf 181 sollte die synthetische Persistenzlinie beendet und die bereits
implementierte asynchrone Audio-Video-Runtime in der vorhandenen
Projektumgebung erneut vollstaendig verifiziert werden. Zu pruefen sind
insbesondere die Lauf-164/165-Proben und ihre direkt abhaengigen Runtime-Tests,
ohne neue Mechanik und ohne Memory-Auswertung.

Ziel ist eine belastbare technische Grundlage fuer den anschliessenden
laengeren gemeinsamen Kamera-Mikrofon-Betrieb. Falls dafuer reale Geraete oder
eine physische Handlung erforderlich werden, ist dies separat als technische
Grenze auszuweisen.
