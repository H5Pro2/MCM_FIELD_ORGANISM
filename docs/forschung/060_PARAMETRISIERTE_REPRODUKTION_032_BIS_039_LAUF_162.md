# Lauf 162: Parametrisierte Reproduktion von Forschung 032 bis 039

## Forschungsfrage und Auftrag

Der vom Forschungspruefer freigegebene Auftrag war, Forschung 032 bis 039
mit frisch initialisierten synthetischen Zustaenden, messbaren Nullbaselines
und einem gemeinsamen parametrisierten Runner zu reproduzieren. Geprueft
wurden Aktivierung, `afterimage`, Layer-Digest und Snapshot-Digest.

Es wurden keine neue Feldmechanik, keine Geraete und keine Medienpfade
verwendet. Memory, Bedeutung und Topologie waren nicht Gegenstand des Laufs.

## Verwendete Quellen

Tatsaechlich verwendet wurden ausschliesslich:

- aktueller freigegebener Uebergabeeingang;
- `AGENTS.md`;
- `docs/forschung/032_*.md` bis `docs/forschung/039_*.md`;
- `mcm_field_organism/shared_mcm_field.py`;
- `mcm_field_organism/mcm_neuron_layer.py`;
- `mcm_field_organism/receptor_contract.py`;
- `mcm_field_organism/receptor_distributor.py`;
- `mcm_field_organism/current_field_history_null_probe.py` und zugehoeriger
  Test als bestehendes Muster.

Externe Quellen und Projektdatenbanken wurden nicht verwendet.

## Verwendete Dateien und Schnittstellen

Neu angelegt wurden:

- `mcm_field_organism/contact_reproduction_probe.py`;
- `tests/test_contact_reproduction_probe.py`;
- `tools/run_contact_reproduction_probe.py`;
- dieser Ergebnisbericht.

Der Messpfad verwendet ausschliesslich `ReceptorContactFrame`,
`CommonFieldTime`, `ReceptorDistributor`, `ReceptorDock`,
`build_shared_mcm_field`, `SharedMCMField.advance` und
`receptor_projection_baseline`. Die vier vorhandenen Kernkomponenten wurden
nicht veraendert.

## Durchgefuehrte Schritte

1. Versuchsarme und Zeitstrukturen aus 032 bis 039 rekonstruiert.
2. Jeden Arm und jede Nullbaseline frisch initialisiert.
3. Alle Varianten zweimal deterministisch ausgefuehrt.
4. Aktivierung, `afterimage`, Layer- und Snapshot-Digest verglichen.
5. Den parametrisierten Test und danach den gemeinsamen JSON-Runner gestartet.

## Messergebnisse und Gegenbaselines

Der Test ergab `8 passed`. Der Runner lieferte:

```text
Forschung  Kombinationen  activation  afterimage  ungleiche Layer  ungleiche Snapshots
032         5              0.0         0.0          0                 4
033        25              0.0         0.0          4                20
034        11              0.0         0.0          0                10
035        75              0.0         0.0         12                70
036        70              0.0         0.0         11                65
037        70              0.0         0.0         11                65
038       220              0.0         0.0         37               215
039       370              0.0         0.0         49               365
```

Beobachtet wurde:

- Jede spaetere Probe hatte exakt den dokumentierten Aktivierungsvektor.
- Jedes `afterimage` war exakt null.
- Beide Ausfuehrungen jeder Variante waren vollstaendig deterministisch.
- Snapshot-Differenzen folgten den armbezogenen technischen `snapshot_id`.
- Die Layer-Differenzen lagen ausschliesslich in Armen mit Abstand `0`.
  Aktivierung und `afterimage` waren dort trotzdem gleich zur Nullbaseline.

Die Dokumente 038 und 039 enthalten interne Zaehlwidersprueche. Die
aufgelisteten Arme ergeben fuer 038 `44 * 5 = 220`, nicht 215, und fuer 039
`74 * 5 = 370`, nicht 365. Kein aufgelisteter Arm wurde entfernt, um die
berichtete kleinere Zahl zu erzwingen.

## Interpretation

**Beobachtetes Ergebnis:** Der schnelle Nullbefund fuer Aktivierung und
`afterimage` ist fuer alle aufgelisteten Varianten reproduziert.

**Technische Interpretation:** Bei Abstand `0` traegt der vollstaendige
Layer-Digest noch Felder des unmittelbaren Vorzustands, obwohl die schnellen
Ausgabevektoren bereits gleich sind. Ab einem neutralen Abstandsschritt ist
dieser Unterschied im hier ausgefuehrten Pfad nicht vorhanden.

**Nicht reproduziert:** Die Altberichte 033 sowie 035 bis 039 behaupten
Layer-Digest-Gleichheit auch fuer Abstand `0`. Diese Aussage wird durch Lauf
162 widerlegt. Die Mengenangaben 038 und 039 sind ebenfalls nicht
reproduzierbar, wenn alle dort aufgelisteten Arme ausgefuehrt werden.

## Grenzen und nicht gepruefte Annahmen

- Der Lauf ist synthetisch und prueft keine Kamera-, Mikrofon- oder
  Weltkontinuitaet.
- Snapshot-Differenzen wurden als Metadatenwirkung beobachtet; es wurde kein
  alternativer Snapshot ohne Metadaten eingefuehrt.
- Der Layer-Digest zeigt Zustandsverschiedenheit, aber keine eigenstaendige
  Feldfunktion und kein Memory.
- Keine Aussage wurde ueber Semantik, Organisation oder Topologie geprueft.
- Die widerspruechliche Formulierung zu den 14 Armen in 036/037 wurde
  wortgetreu als kanonischer `A-B-A`-Arm plus drei aufgezaehlte eindeutige
  Permutationsarme umgesetzt; dadurch bleibt die berichtete Gesamtzahl 14.

Eine Zielabweichung ist nicht erkennbar.

## Konkrete Schlussfolgerung

Forschung 032 und 034 sind auf den geprueften Messgroessen reproduziert.
Forschung 033 und 035 bis 039 sind nur hinsichtlich Aktivierung,
`afterimage` und Determinismus reproduziert. Ihre pauschale Aussage gleicher
vollstaendiger Layer-Digests bei Abstand `0` ist nicht belastbar. Forschung
038 und 039 enthalten zusaetzlich je einen dokumentarischen Zaehlfehler.

Der Befund rechtfertigt keine neue Feld- oder Memory-Mechanik.

## Vorschlag fuer den naechsten begrenzten Forschungslauf

Als naechster Lauf sollte ausschliesslich die Abstand-`0`-Abweichung
zerlegt werden: Fuer je einen minimalen Arm aus 033, 035, 036, 037, 038 und
039 die kanonischen Layer-Payloads feldweise gegen die jeweilige Nullbaseline
vergleichen, danach denselben Vergleich bei Abstand `1` wiederholen. Ziel ist
nur die genaue technische Zuordnung der Digest-Differenz; neue Mechanik,
Memory-Auswertung, Geraete und Medien bleiben ausgeschlossen.
