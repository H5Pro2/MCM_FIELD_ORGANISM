# S1-DX: E1 verfeinerter Kettenergebniskern und synthetischer Einmalexecutor

## Status

Der private Ergebniscontainer und die atomare Einmal-Persistenz fuer die
verfeinerte Bildungs- und Transferkette sind implementiert. Die heutige
Executoroberflaeche ist absichtlich nur synthetisch aufrufbar und verweigert
den registrierten kanonischen Projektordner. Es wurde kein kanonischer
Produzent, keine Bildung und keine Probe ausgefuehrt.

## Implementierung

```text
mcm_field_organism/e1_refined_chain_one_shot_execution.py
tests/test_e1_refined_chain_one_shot_execution.py
```

Normalisierter Implementierungsdigest:

```text
a9621b561e7aa02fd18f3f43ffdd9c02c36efb4737745906a729ce8275277c7b
```

## Ergebniscontainer

Jede Verfeinerung `r1/r2/r4` muss geordnet enthalten:

- fuenf E1-Zustandsdigests fuer AB, BA, AB-Identitaet und beide
  Bildungsablationsarme;
- sieben Feldendigests fuer P0, aktive AB/BA-Probe, Probeablationen und
  feste Adapter;
- rohe nichtnegative Werte fuer Zustandsabstand, Gesamtbindungsabstand und
  beide S/H-Probenabstaende.

Der Gesamtergebniscontainer bindet alle 13 S1-DS-Metriken, elf boolesche
Pflichtkontrollen und genau eine der vier vorregistrierten Entscheidungen.
Die feinen Hauptmetriken muessen den `r4`-Werten entsprechen.

Exakte Identitaets-, Bildungsablations-, Probeablations- und Fixed-Adapter-
Kontrollen duerfen keinem von null verschiedenen Rest widersprechen. Der
Ressourcenbilanzfehler darf `1e-12` nicht uebersteigen.

## Deterministische Entscheidung

Die S1-DS-Reihenfolge ist direkt umgesetzt:

1. Mindestens eine fehlgeschlagene Pflichtkontrolle ergibt
   `TECHNICALLY_INVALID`.
2. Sind Zustands- und beide Probensignale in `r1/r2/r4` exakt null, ergibt
   sich `NO_REFINED_WORLD_FORMATION_EFFECT`.
3. Sind feiner Zustands- und beide feinen Probeneffekte jeweils groesser als
   das Achtfache ihres passenden feinen Restes und werden die Reste nicht
   groesser, ergibt sich `REFINED_WORLD_FORMATION_AND_TRANSFER_EFFECT`.
4. Jeder andere technisch gueltige Ausgang ist `NUMERICALLY_UNDECIDABLE`.

Eine abweichend deklarierte Entscheidung wird abgewiesen.

## Synthetische Einmalgrenze

`execute_synthetic_e1_refined_chain_one_shot(...)` verlangt den aktuellen
S1-DW-Vertrag, aber schreibt ausschliesslich in einen explizit getrennten
synthetischen Zielordner. Der kanonische `reports`-Ordner wird abgewiesen.

Die synthetische Persistenz prueft:

- nicht aufrufbare Produzenten vor Versuchsbeginn;
- exklusiven Sperr- und Versuchsmarker;
- Beibehaltung des Versuchsmarkers nach gestartetem Fehler;
- Sperrung jeder Wiederholung;
- kanonisches Ergebnis-JSON und Ergebnisdigest;
- atomare Veroeffentlichung ueber einen exklusiven Dateilink;
- Entfernung von Versuch und Sperre nur nach Erfolg.

## Kanonische Pfade

Die registrierten S1-EA-Pfade bleiben unbenutzt:

```text
reports/e1_refined_formation_transfer_s1ea_once_v1.json
reports/e1_refined_formation_transfer_s1ea_once_v1.attempt.json
reports/e1_refined_formation_transfer_s1ea_once_v1.lock
```

## Technische Abnahme

```text
8 fokussierte Tests
359 Tests im vollstaendigen E1-Verbund
OK
```

## Aussagegrenze

Alle in S1-DX verwendeten Zahlen, Digests und Entscheidungen sind
synthetische Testfixtures. Sie sind kein Ergebnis der kanonischen AV-Welt
und begruenden keinen Zustandsbildungs-, Transfer-, Memory- oder KI-Befund.

## Anschluss

S1-DY bindet nun Quellen, Plaene, Probe, frisches Feld, neutralen E1-Anfang,
Rollen und den privaten kanonischen Einstieg. Der Preflight ist
nichtausfuehrend; die numerische Produzentenkomposition folgt getrennt in
S1-DZ.
