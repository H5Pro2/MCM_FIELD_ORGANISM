# Forschung 034: Dock-uebergreifende synthetische Kontaktvariation

## Auftrag und Grenze

Geprueft wurde, ob der Nullbefund aus Forschung 032 und 033 bei kontrollierter
Variation der zuvor kontaktierten Dock-Kombinationen stabil bleibt. Der Lauf
verwendete ausschliesslich vorhandene synthetische Rezeptor-, Verteiler-,
`SharedMCMField`- und Projektionsschnittstellen.

Schnellnachhall, Browser, Medieninput, Download, lokale Medienkopie,
Installation, Transcode und dateibasierte Auswertung blieben ausgeschlossen.
Code, Runtime und Architektur wurden nicht geaendert.

## Festgelegter Aufbau

Vier synthetische Rezeptoren waren fest den Docks `dock.0` bis `dock.3`
zugeordnet. Jeder Arm bestand aus zwei Vorgeschichtsschritten, einem
vollstaendig kontaktlosen Abstandsschritt und derselben spaeteren Probe:

```text
Probe = (0.6, 0.4, 0.2, 0.1)
```

Die frisch initialisierten Vorgeschichten waren:

- Nullkontakt: `(0,0,0,0)` -> `(0,0,0,0)`;
- Einzelkontakt: `(0,0,0,0)` -> `(0.8,0,0,0)`;
- gleiche Docks / Wiederholung: `(0.8,0,0,0)` -> `(0.8,0,0,0)`;
- wechselnde Docks: `(0.8,0,0,0)` -> `(0,0.8,0,0)`;
- ueberlappende Dock-Mengen: `(0.4,0.4,0,0)` -> `(0,0.4,0.4,0)`;
- disjunkte Dock-Mengen: `(0.4,0.4,0,0)` -> `(0,0,0.4,0.4)`.

Jeder nichttriviale Arm wurde zusaetzlich frisch mit umgekehrter Dock- und
Frame-Deklarationsreihenfolge ausgefuehrt.

## Ergebnis

Nach dem kontaktlosen Abstand galt in allen Armen:

```text
activation = (0.0, 0.0, 0.0, 0.0)
afterimage  = (0.0, 0.0, 0.0, 0.0)
```

Bei der identischen spaeteren Probe lieferten alle Arme:

```text
activation = (0.6, 0.4, 0.2, 0.1)
afterimage  = (0.0, 0.0, 0.0, 0.0)
```

Fuer Einzelkontakt, gleiche, wechselnde, ueberlappende und disjunkte Docks
galt jeweils gegen den Nullarm:

```text
activation max error: 0.0
afterimage max error:  0.0
Layer-Digest:           gleich
```

Fuer jede umgekehrte Dock- und Frame-Reihenfolge galt:

```text
activation max error: 0.0
afterimage max error:  0.0
Layer-Digest:           gleich
```

## Technische Nullerklaerung

Die spaetere Aktivierung ist vollstaendig die aktuelle Projektion der
identischen Probe. Der kontaktlose Abstand gleicht die bekannte lokale
Ein-Schritt-Wirkung an. `afterimage` ist in diesem ausgefuehrten
Projektionspfad durchgehend null. Dock-Auswahl und Deklarationsreihenfolge
lassen keinen numerischen oder kausalen Feldrest zurueck.

Die vollstaendigen Snapshot-Digests getrennter Arme unterscheiden sich durch
die absichtlich arm-spezifischen technischen `snapshot_id`-Werte in der
serialisierten letzten Rezeptorverteilung. Aktivierung, `afterimage` und
Layer-Digest sind davon unberuehrt. Es wurde kein Cachezustand und kein
Observer-Writeback verwendet.

## Befund und Stopplinie

Der Nullbefund bleibt bei gleichen, wechselnden, ueberlappenden und disjunkten
Dock-Kombinationen stabil. Die vorhandene Projektionsruntime zeigt keine
veraenderte spaetere lokale Feldaufnahme, die ueber aktuelle Projektion,
lokale Ein-Schritt-Wirkung und technische Snapshotmetadaten hinausgeht.

Das Ergebnis begruendet keine Programmerweiterung und keine Aussage ueber
Memory, Bedeutung, Reward, Materialrollen, Organisation oder Topologie.

## Tatsaechlich verwendete Quellen

- aktuelle Uebergabe des MCM-Forschungsleiters;
- `docs/forschung/033_ABSTANDSSTABILITAET_SYNTHETISCHER_WELTKONTAKT_NULLBEFUND.md`;
- `mcm_field_organism/receptor_contract.py`;
- `mcm_field_organism/receptor_distributor.py`;
- `mcm_field_organism/shared_mcm_field.py`;
- `mcm_field_organism/mcm_neuron_layer.py`.

Externe Quellen und MINI_DIO wurden nicht verwendet.
