# Lauf 163: Technische Zerlegung der Abstand-0-Layer-Abweichung

## Forschungsfrage und Auftrag

Zu pruefen war, welche vorhandenen Felder des kanonischen Layer-Payloads die
in Lauf 162 beobachtete Digest-Abweichung bei neutralem Abstand `0` tragen
und warum sie nach einem neutralen Schritt verschwindet. Untersucht wurde je
ein dokumentierter Arm aus Forschung 033, 035, 036, 037, 038 und 039 gegen
eine frisch initialisierte Nullbaseline bei Abstand `0` und `1`.

## Verwendete Quellen

Tatsaechlich verwendet wurden ausschliesslich:

- aktueller freigegebener Uebergabeeingang;
- `AGENTS.md`;
- `docs/forschung/060_PARAMETRISIERTE_REPRODUKTION_032_BIS_039_LAUF_162.md`;
- `mcm_field_organism/contact_reproduction_probe.py`;
- `mcm_field_organism/shared_mcm_field.py`;
- `mcm_field_organism/mcm_neuron_layer.py`;
- `mcm_field_organism/receptor_contract.py`;
- `mcm_field_organism/receptor_distributor.py`.

Externe Quellen und Projektdatenbanken wurden nicht verwendet.

## Verwendete Dateien und Schnittstellen

Neu angelegt wurden:

- `mcm_field_organism/layer_payload_difference_probe.py`;
- `tests/test_layer_payload_difference_probe.py`;
- `tools/run_layer_payload_difference_probe.py`;
- dieser Bericht.

`contact_reproduction_probe.py` wurde nur so erweitert, dass ein frisch
ausgefuehrter Arm seinen bereits vorhandenen `SharedMCMFieldSnapshot`
zurueckgeben kann. Die Feld-, Neuron-, Rezeptor- und Verteilungsmechanik
wurde nicht geaendert.

## Durchgefuehrte Schritte

1. Je Forschungsvariante einen Arm mit letztem Kontaktimpuls unmittelbar vor
   der Probe ausgewaehlt.
2. Jeweils Null- und Kontaktarm frisch bei Abstand `0` ausgefuehrt.
3. Denselben Vergleich mit genau einem neutralen Abstandsschritt wiederholt.
4. Kanonische Layer-Payloads rekursiv und feldweise verglichen.
5. Aktivierung, `afterimage`, Layer-Digest und Snapshot-Digest kontrolliert.
6. Parametrisierten Test und JSON-Runner ausgefuehrt.

## Messergebnisse und Gegenbaselines

Es wurden `12` Vergleiche ausgefuehrt: sechs Forschungsvarianten mal zwei
Abstandsstufen.

```text
Forschung  Arm                            Diff-Felder Abstand 0  Abstand 1
033        single                         2                      0
035        s0.2.g0.single                 2                      0
036        g0.aba.canonical               1                      0
037        g0.aba.canonical               1                      0
038        g0.mixed.(0,1,2).(0.2,0.5,0.9) 1                      0
039        g0.canonical.0                  1                      0
```

Saemtliche Abstand-`0`-Unterschiede lagen ausschliesslich auf drei
kanonischen Pfadformen:

```text
layer.neurons[0].perception.local_samples[0].activation
layer.neurons[1].perception.local_samples[0].activation
layer.neurons[1].perception.local_samples[1].activation
```

Die abweichenden Werte entsprachen den Aktivierungen des unmittelbar
vorherigen Sequenzfensters: `0.2`, `0.3`, `0.5`, `0.8`, `0.9` oder `-0.9`
gegen jeweils `0.0` in der Nullbaseline.

Fuer alle zwoelf Vergleiche galt:

```text
aktuelle activation gleich:  ja
aktuelles afterimage gleich: ja
Snapshot-Digest gleich:      nein
```

Bei Abstand `0` waren alle sechs Layer-Digests verschieden. Bei Abstand `1`
waren alle sechs Layer-Digests und die vollstaendigen Layer-Payloads gleich.
Die Snapshot-Digests blieben wegen getrennter armspezifischer
`snapshot_id`-Metadaten verschieden.

## Einordnung

**Beobachtetes Ergebnis:** Der Digest-Unterschied ist vollstaendig auf
`perception.local_samples[*].activation` begrenzt. Andere Layer-Felder
unterschieden sich nicht.

**Technische Interpretation:** Beim aktuellen Probenschritt enthalten die
lokalen Samples die Aktivierung der direkten Quellneuronen aus dem
vorherigen Layer-Tick. Ein neutraler Abstandsschritt setzt diese
Quellaktivierungen im Projektionspfad auf null. Im folgenden Probenschritt
werden daher auf beiden Armen identische lokale Samples gebildet.

**Nicht beobachtet:** Es wurde keine ueber einen neutralen Schritt tragende
Layer-Differenz und keine Wirkung auf aktuelle Aktivierung oder `afterimage`
beobachtet.

## Grenzen und nicht gepruefte Annahmen

- Untersucht wurde je Variante ein gezielt offengelegter Arm mit letztem
  Impuls unmittelbar vor der Probe, nicht erneut die gesamte Armmenge.
- Der Befund gilt fuer `receptor_projection_baseline` und die vorhandene
  lokale Ein-Schritt-Abtastung.
- Snapshot-Metadaten wurden nicht entfernt oder normalisiert.
- Keine Geraete, Medien, Browser oder Streams wurden verwendet.
- Lokale Samples sind vorhandener technischer Layerzustand; sie wurden nicht
  als Memory, Semantik, Organisation oder Organismusfunktion interpretiert.

Eine Zielabweichung ist nicht erkennbar.

## Konkrete Schlussfolgerung

Die Abstand-`0`-Layer-Abweichung ist kein unerklaerter Persistenzrest. Sie
ist die dokumentierte lokale Ein-Schritt-Abtastung der Aktivierung des
unmittelbar vorherigen Layer-Ticks. Ein neutraler Schritt setzt die
Quellaktivierungen auf null; danach sind die Layer-Payloads vollständig
gleich. Dieser Befund gibt keine neue Feld- oder Memory-Mechanik frei.

## Vorschlag fuer den naechsten begrenzten Forschungslauf

Der synthetische Persistenzzweig 032 bis 039 ist damit technisch erklaert.
Als naechster begrenzter Lauf sollte die bereits benannte asynchrone
Audio-Video-Luecke aus Forschung 030 untersucht werden: mit rein
synthetischen Ereignissen unterschiedliche Audio-/Videoraten,
Zeitteilungen und Reihenfolgen gegen zeitlich aequivalente Gegenbaselines
vergleichen. Dabei darf keine neue Mechanik und kein Geraetezugriff
eingefuehrt werden.
