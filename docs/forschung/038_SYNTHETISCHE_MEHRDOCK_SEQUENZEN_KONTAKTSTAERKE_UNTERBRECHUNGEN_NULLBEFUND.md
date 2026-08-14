# Forschung 038: Mehrdock-Sequenzen, Kontaktstaerke und Unterbrechungen

## Auftrag und Grenze

Geprueft wurde, ob der stabile Nullbefund aus Forschung 032 bis 037 erhalten
bleibt, wenn Dock-Wechsel, unterschiedliche Kontaktstaerken und neutrale
Unterbrechungen in kurzen synthetischen Sequenzen kombiniert werden.
Verwendet wurden ausschliesslich vorhandene synthetische Docks sowie die
bestehenden Rezeptor-, Verteiler-, `SharedMCMField`-, Neuron-Layer- und
Projektionsschnittstellen.

Schnellnachhall, Browser, Medienpfade, Download, lokale Medienkopie,
Installation, Transcode und dateibasierte Auswertung blieben ausgeschlossen.
Code, Runtime und Architektur wurden nicht geaendert.

## Kontrollierter Aufbau

Die Kontakte lagen auf den drei getrennten technischen Docks `A`, `B` und
`C`. Verwendet wurden die Kontaktstaerken:

```text
schwach: 0.2
mittel:  0.5
stark:   0.9
```

Jeder Arm hatte exakt fuenf Sequenzfenster. Kontakte lagen in den Fenstern
`0`, `2` und `4`; die Fenster `1` und `3` waren neutrale kontaktfreie
Feldschritte. Verglichen wurden 43 frisch initialisierte Arme:

- ein Nullkontaktarm;
- drei Einzelkontaktarme, je einer pro Kontaktstaerke;
- drei identische Wiederholungsarme, je einer pro Kontaktstaerke;
- 36 Mehrdock-Arme aus allen sechs Dock-Reihenfolgen kombiniert mit allen
  sechs Reihenfolgen der drei Kontaktstaerken;
- eine getrennte frische Reproduktion der kanonischen Folge
  `A(0.2)-neutral-B(0.5)-neutral-C(0.9)`.

Nach den gleich langen Sequenzen folgten die neutralen Abstandsstufen `0`,
`1`, `2`, `4` und `8`. Alle Arme endeten mit derselben aktuellen Probe am
Dock `A` mit der Staerke `0.6`.

## Ergebnis

In jeder Abstandsstufe und jedem Arm ergab die spaetere Probe:

```text
activation = (0.6, 0.0, 0.0)
afterimage  = (0.0, 0.0, 0.0)
```

Fuer alle 215 Kombinationen aus 43 Armen und 5 Abstandsstufen galt:

```text
maximaler activation-Fehler gegen Nullkontakt: 0.0
maximaler afterimage-Fehler gegen Nullkontakt:  0.0
Layer-Digest gegen Nullkontakt:                 gleich
frische kanonische Reproduktion:                gleich
```

Die vollstaendigen Snapshot-Digests unterschieden sich aufgrund der
arm-spezifischen `snapshot_id` der aktuellen Probe. Diese technische
Metadatenabweichung war nicht in Aktivierung, `afterimage` oder Layer-Digest
vorhanden.

## Technische Nullerklaerung

Gesamtfensterlaenge, Feldschrittzahl und Layer-Tickzahl waren in allen Armen
identisch. Dock-Auswahl, Dock-Reihenfolge und Kontaktstaerke wurden
vollstaendig gegeneinander permutiert. Die neutralen Unterbrechungen liefen
als regulaere kontaktfreie Verteilungen auf derselben Organismuszeitachse.

Die spaetere Aktivierung entspricht ausschliesslich der aktuellen Projektion
der identischen Probe. Lokale Ein-Schritt-Wirkung, vorherige Dock-Auswahl,
vorherige Kontaktstaerke, Sequenzreihenfolge, neutrale Unterbrechungen,
Snapshotmetadaten und Numerik hinterliessen keinen zusaetzlichen kausalen
Rest im spaeteren Layerzustand.

## Befund und Stopplinie

Der Nullbefund bleibt unter der kombinierten Variation von drei Docks, drei
Kontaktstaerken, allen Reihenfolgen, neutralen Unterbrechungen und allen
geprueften nachgelagerten Abstandsstufen stabil. Es wurde keine veraenderte
spaetere lokale Feldaufnahme festgestellt.

Das Ergebnis begruendet keine Programmerweiterung und keine Aussage ueber
Memory, Bedeutung, Reward, Materialrollen, Organisation oder Topologie.

## Tatsaechlich verwendete Quellen

- aktuelle Uebergabe des MCM-Forschungsleiters;
- `docs/forschung/037_SYNTHETISCHE_KONTAKTSEQUENZEN_MIT_NEUTRALEN_UNTERBRECHUNGEN_NULLBEFUND.md`;
- `mcm_field_organism/receptor_contract.py`;
- `mcm_field_organism/receptor_distributor.py`;
- `mcm_field_organism/shared_mcm_field.py`;
- `mcm_field_organism/mcm_neuron_layer.py`.

Externe Quellen und MINI_DIO wurden nicht verwendet.
