# Lauf 176: Frische Verifikation der parametrisierten Reproduktion 032 bis 039

## Forschungsfrage und Auftrag

Der freigegebene Auftrag war, Forschung 032 bis 039 in einem gemeinsamen
parametrisierten Lauf aus frisch initialisierten synthetischen Zustaenden gegen
Nullbaselines zu reproduzieren. Geprueft wurden Aktivierung, `afterimage`,
Layer-Digest, Snapshot-Digest und deterministische Wiederholung.

## Verwendete Quellen

Tatsaechlich verwendet wurden:

- der aktuelle freigegebene Uebergabeeingang zu Lauf 161;
- `AGENTS.md`;
- `docs/forschung/032_*.md` bis `docs/forschung/039_*.md` mittelbar ueber die
  bereits dokumentierte Parametrisierung;
- `docs/forschung/060_PARAMETRISIERTE_REPRODUKTION_032_BIS_039_LAUF_162.md`;
- `mcm_field_organism/contact_reproduction_probe.py`;
- `tests/test_contact_reproduction_probe.py`;
- `tools/run_contact_reproduction_probe.py`;
- die von der Probe verwendeten bestehenden Schnittstellen in
  `shared_mcm_field.py`, `mcm_neuron_layer.py`, `receptor_contract.py` und
  `receptor_distributor.py`.

Externe Quellen und Projektdatenbanken wurden nicht verwendet.

## Verwendete Dateien und Schnittstellen

Der vorhandene Runner deckt Nullkontakt, Einzelkontakt, Wiederholung,
Reproduktion, Abstandsstufen, Dockkombinationen, Kontaktstaerken, Sequenzen,
neutrale Unterbrechungen, Mehrdock- und Kontrastfolgen ab. Jeder Arm baut ein
frisches gemeinsames Feld auf und verwendet `ReceptorContactFrame`,
`CommonFieldTime`, `ReceptorDistributor`, `ReceptorDock`,
`build_shared_mcm_field`, `SharedMCMField.advance` und
`receptor_projection_baseline`.

In Lauf 176 wurde keine Feld- oder Rezeptormechanik veraendert. Neu ist nur
dieser Ergebnisbericht.

## Durchgefuehrte Schritte

1. Vorhandene Parametrisierung und Testabdeckung gegen den Auftrag geprueft.
2. Den fokussierten parametrisierten Test frisch gestartet.
3. Den gemeinsamen JSON-Runner unabhaengig davon frisch gestartet.
4. Alle acht Forschungsvarianten gegen ihre Nullbaselines ausgewertet.

Aufrufe:

```powershell
.\.venv\Scripts\python.exe -m pytest -q tests\test_contact_reproduction_probe.py
.\.venv\Scripts\python.exe tools\run_contact_reproduction_probe.py
```

## Messergebnisse und Gegenbaselines

Der Test ergab:

```text
8 passed in 8.57s
```

Der Runner ergab:

```text
Forschung  Kombinationen  Nullbaselines  activation  afterimage  ungleiche Layer  ungleiche Snapshots
032         5              1              0.0         0.0          0                 4
033        25              5              0.0         0.0          4                20
034        11              1              0.0         0.0          0                10
035        75              5              0.0         0.0         12                70
036        70              5              0.0         0.0         11                65
037        70              5              0.0         0.0         11                65
038       220              5              0.0         0.0         37               215
039       370              5              0.0         0.0         49               365
```

Fuer alle acht Varianten waren die erwarteten Probeaktivierungen exakt, alle
`afterimage`-Vektoren exakt null und die vollstaendige zweite Ausfuehrung
deterministisch gleich. Die Layer-Digest-Abweichungen entsprechen erneut den
Armen mit Abstand 0. Snapshot-Digests unterscheiden sich aufgrund der
armbezogenen technischen Snapshot-Identitaet.

## Einordnung

**Beobachtetes Ergebnis:** Die Messwerte aus Lauf 162 wurden frisch und ohne
Abweichung reproduziert.

**Technische Interpretation:** Die schnelle Feldantwort traegt in diesen
synthetischen Armen keine messbare historische Wirkung in Aktivierung oder
`afterimage`. Der vollstaendige Layerzustand kann bei Abstand 0 dennoch vom
Nullarm verschieden sein.

**Nicht beobachtet:** Es wurde keine unabhaengige Feldfunktion, kein Memory,
keine Bedeutung und keine Topologie nachgewiesen.

## Grenzen und nicht gepruefte Annahmen

- Der Lauf verwendet ausschliesslich synthetische Kontakte.
- Kamera, Mikrofon, Browser, Streams und physische Aufbauten wurden nicht
  angesprochen.
- Die Abstand-0-Layerdifferenz wurde in diesem Lauf nicht erneut feldweise
  zerlegt; diese Zerlegung liegt bereits in Lauf 163 vor.
- Snapshot-Differenz bedeutet keine funktionale Feldwirkung.
- Der vorhandene unversionierte und teilweise veraenderte Workspace wurde
  nicht bereinigt, committed oder zurueckgesetzt.

Eine Zielabweichung ist nicht erkennbar.

## Konkrete Schlussfolgerung

Der freigegebene Reproduktionsauftrag ist im aktuellen Workspace technisch
umgesetzt und durch Lauf 176 frisch bestaetigt. Forschung 032 bis 039 ist fuer
Aktivierung, `afterimage` und Determinismus reproduzierbar. Pauschale
Layer-Digest-Gleichheit bei Abstand 0 bleibt widerlegt. Der Befund rechtfertigt
keine neue Feld- oder Memory-Mechanik.

## Vorschlag fuer den naechsten begrenzten Forschungslauf

Da Reproduktion und Abstand-0-Zerlegung bereits abgeschlossen sind, sollte der
naechste Lauf keine weitere synthetische Persistenzwiederholung sein. Unter der
aktuellen Benutzergrenze sollte als naechster begrenzter Entwicklungszweig der
vorhandene simulierte Effektor-Welt-Vertrag inventarisiert und gegen vier
technische Kausalbaselines geprueft werden: Originalrueckkehr, neutrale
Effektorausgabe, unterbrochene Rueckkehr und vertauschte Kanaluebergabe. Dabei
duerfen keine reale physische Wirkung und keine Memoryfunktion behauptet werden.
