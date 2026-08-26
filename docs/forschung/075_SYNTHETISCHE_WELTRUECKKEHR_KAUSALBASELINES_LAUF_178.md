# Lauf 178: Synthetische Weltrueckkehr-Kausalbaselines

## Forschungsfrage und Auftrag

Untersucht wurde, ob die vorhandene testtreibergesteuerte simulierte Welt-
Rezeptor-MCM-Strecke vier technische Rueckkehrarme deterministisch und kausal
unterscheidbar abbildet: regulaere Rueckkehr, neutrale aeussere Intervention,
unterbrochene Rueckkehr und fest vertauschte Rezeptorkanaele.

Der Lauf fuehrt keine MCM-zu-Effektor-Regel ein.

## Verwendete Quellen

Tatsaechlich verwendet wurden:

- aktueller Uebergabeeingang mit Lauf 177;
- `AGENTS.md`;
- `docs/architektur/018_MINIMALER_SIMULIERTER_EFFEKTORVERTRAG.md`;
- `docs/architektur/103_GRUNDLAGENENTSCHEIDUNG_FELDGEBUNDENE_WELTWIRKUNG.md`;
- `docs/architektur/104_TECHNISCHER_VERTRAG_VISUELLE_MCM_EFFEKTORFLAECHE.md`;
- `docs/architektur/105_KAUSALVERTRAG_GETRENNTE_VISUELLE_WELTWIRKUNG.md`;
- `mcm_field_organism/simulated_effector_world.py`;
- `mcm_field_organism/simulated_world_mcm_path.py`;
- `mcm_field_organism/sensor_mcm_field.py`;
- bestehende zugehoerige Tests und Runnerstile.

Externe Quellen wurden nicht verwendet.

## Verwendete Dateien und Schnittstellen

Neu ergaenzt wurden:

- `mcm_field_organism/simulated_return_causal_probe.py`;
- `tests/test_simulated_return_causal_probe.py`;
- `tools/run_simulated_return_causal_probe.py`.

Verwendete Schnittstellen waren `SimulatedWorldState`, `WorldIntervention`,
`advance_simulated_world`, `receptor_frame_from_world`,
`simulated_world_receptor_to_contact_frame`, `ReceptorContactFrame`,
`CommonFieldTime`, `build_receptor_aligned_mcm_field` und
`receptor_projection_baseline`.

## Versuchsaufbau

Aus sieben frischen Startpositionen wurden jeweils die aeusseren
Testinterventionen `-1` und `+1` angewendet. Fuer jeden der 14 Ausgangsfaelle
wurden vier frische Arme erzeugt:

1. `original`: regulaere Welttransition und regulaere Rezeptorrueckkehr;
2. `neutral`: am selben Startzustand aeussere Intervention `0`;
3. `interrupted`: originale Welttransition, aber Nullvektor an der
   Rezeptoruebergabe;
4. `swapped`: originale Welttransition, aber feste Umkehr der sieben
   Rezeptorkanaele.

Alle Arme verwendeten dasselbe abgeschlossene Feldzeitfenster. Gemessen wurden
Weltposition und Welt-Digest, Rezeptorwerte, Aktivierung, `afterimage` und
Feldfenster-Digest. Der gesamte Lauf wurde intern wiederholt.

## Messergebnisse und Gegenbaselines

```text
Fokussierte Tests:                              3 passed in 1.19s
Ausgangsfaelle:                                 14
Beobachtungen:                                  56
Neutralarm mit anderer Welt als Original:       14 / 14
Unterbrechung mit gleicher Welt wie Original:   14 / 14
Unterbrechung mit anderem Feldfenster:           14 / 14
Kanaltausch mit gleicher Welt wie Original:     14 / 14
Kanaltausch mit anderem Rezeptorvektor:          12 / 14
Kanaltausch mit anderem Feldfenster:             12 / 14
Alle afterimage-Vektoren null:                  ja
Deterministische Gesamtreproduktion:            ja
Feld-zu-Effektor-Anschluss:                     nein
```

Die zwei beim Kanaltausch unveraenderten Faelle endeten beide am mittleren
Kanal 3. Dieser Kanal ist der einzige Fixpunkt der festen Umkehrabbildung
`i -> 6-i`. Der erste Testlauf hatte hier irrtuemlich zehn Unterschiede
erwartet; beobachtet wurden zwoelf. Die Testannahme wurde an die tatsaechliche
Geometrie korrigiert, ohne die Probe zu aendern.

## Einordnung

**Beobachtet:** Bei identischer Welttransition entfernte die unterbrochene
Rueckkehr in allen 14 Faellen die one-hot Feldaktivierung. Der Welt-Digest
blieb jeweils identisch.

**Technische Interpretation:** Die simulierte Weltwirkung erreicht das Feld
in dieser Probe ausschliesslich ueber die Rezeptoruebergabe.

**Beobachtet:** Die feste Kanalumkehr verschob Rezeptor- und Feldaktivierung
in 12 Faellen gleichartig. Zwei mittlere Fixpunktfaelle blieben unveraendert.

**Technische Interpretation:** Die Feldlage folgt der technisch uebergebenen
Kanalordnung. Das belegt keine entstandene Topologie.

**Beobachtet:** Die neutrale aeussere Intervention erzeugte in allen 14
Vergleichen einen anderen Weltzustand als die jeweilige Bewegung.

## Grenzen und nicht gepruefte Annahmen

- Der Lauf war vollstaendig synthetisch.
- Alle Interventionen stammten vom Testtreiber, nicht vom MCM-Feld.
- `InterventionCause.EFFECTOR` wurde nicht als Kausalbeweis verwendet.
- Die Unterbrechung wurde technisch durch einen Null-Kontaktvektor modelliert.
- Der Kanaltausch war eine feste Spiegelung und keine physische Vertauschung.
- Der verwendete separate Sensorfeldpfad ist eine historische
  Reproduktionsbaseline, nicht die aktive Organismus-Gesamtarchitektur.
- Es wurde keine zeitliche Rueckkopplung ueber mehrere Welt-Feld-Zyklen
  untersucht.
- Memory, Semantik, Agency, Organisation und entstandene Topologie wurden
  weder untersucht noch behauptet.
- Eine reale physische Feld-Welt-Feld-Schleife wurde nicht geprueft.

## Konkrete Schlussfolgerung

Die bestehende synthetische Welt-Rezeptor-Feld-Strecke reagiert
deterministisch auf Rueckkehrunterbrechung und feste Kanalvertauschung. Die
Unterschiede sind vollstaendig durch die vorgegebene Welttransition, die
technische Rezeptoruebergabe und die lineare Projektion erklaert. Der Lauf
zeigt damit eine kontrollierbare technische Kausalkette, aber keine
eigenstaendige Feldorganisation und keinen geschlossenen Effektorpfad.

Eine Zielabweichung ist nicht erkennbar.

## Naechster begrenzter Forschungslauf

Als Lauf 179 sollte dieselbe synthetische Kausalprobe auf zwei abgeschlossene
Zeitstufen erweitert werden. Nach einer ersten regulären, unterbrochenen oder
vertauschten Rueckkehr erhalten alle Arme denselben zweiten regulaeren
Weltkontakt. Zu messen ist ausschliesslich, ob Unterschiede der zweiten
Feldaufnahme vollstaendig durch den bestehenden linearen Zustand und
`afterimage` erklaert werden. Eine neue Memoryvariable oder Effektorregel ist
nicht zulaessig.
