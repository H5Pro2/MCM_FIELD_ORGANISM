# W7-R: Implementierung des P0-S-Abschlusszustandsproduzenten

## Entscheidung

`ISOLATED_P0_S_COMPLETION_STATE_PRODUCER_IMPLEMENTED`

W7-R implementiert den in W7-Q gebundenen Produzenten fuer genau ein
explizit uebergebenes W7-M-Quellsegment. Die Implementierung bleibt im
Arbeitsspeicher und startet weder A/B-Hauptpfad noch Forschungsreport.

## Implementierter Umfang

Das Modul
`mcm_field_organism/w7r_p0_s_completion_producer.py` stellt bereit:

- einen exakt null initialisierten, substratfreien P0-Zustand auf der
  W7-M-Feldgeometrie;
- eine vollstaendige P0-Bindung aus S, H, Layerzustand, Organismuszeit und
  Digest;
- verlustfreie Projektion genau eines eingefrorenen Quellsegments;
- atomare S-Beobachtung nach jeder eindeutigen Rezeptorabschlussgrenze;
- einen exakten substratfreien S/H-Endzustand fuer die Fortsetzung;
- einen direkten digestgebundenen Uebergang an den W7-P-Treiber.

Der private P0-Zustand behaelt ein geprueftes `SharedMCMField`, weil S/H
allein Layer-Tick, lokale Wahrnehmung und letzte Organismuszeit nicht
vollstaendig fortsetzen koennen. Dieses Feld besitzt weder M noch einen
Entwicklungszustand und wird nicht exportiert.

## Kausaler Pfad

Die beiden Rezeptorfolgen werden nur nach technischer Modalitaets-ID
kanonisiert. Ihr danach berechneter Digest muss einem W7-M-Quelldigest exakt
entsprechen. Ein `MCMFieldStepTime` umfasst den Korridor `(start, end]`.

`handoff_receptor_completion_groups`,
`map_proposal_batch_to_transient_docks` und
`project_transient_docks_to_neuron_inputs` erhalten alle Ereignisse und ihre
lokale Dockidentitaet. Der vorhandene
`advance_neutral_fast_shared_field_transient` entwickelt S und H exakt. Sein
private Observer kopiert S/H nach jeder atomaren Abschlussgruppe, ohne einen
Wert zurueckzugeben oder den Runtimezustand zu veraendern.

## Zustands- und Digestbindung

Jeder P0-Zustand bindet:

- W7-M-Matrixdigest und technischen Quellpfad;
- Uhr und letzten Endtick;
- originale Neuronenreihenfolge;
- vollstaendige S- und H-Vektoren;
- Layerdigest und letzten Distributionsdigest;
- feste P0-Parameter `1.0`, `0.5` und Leckrate `0.0`.

Der Produktionsdigest bindet zusaetzlich Quelldigest, Intervall, Zahl der
zugeordneten Ereignisse, jeden eindeutigen S-Abschlusszustand sowie Anfangs-
und Endzustandsdigest. Manipulierte Zustands- oder Produktionsdigests werden
abgelehnt.

## W7-P-Uebergabe

Ereigniszustande werden unveraendert in
`W7PCompletedP0SSample` ueberfuehrt. Liegt das Intervallende nach der letzten
Ereignisgrenze, wird der exakte S-Endzustand nur als terminale Probe
ergaenzt. W7-P bildet daraus linksgehaltene Segmente und bindet denselben
Matrix- und Quelldigest.

## Technische Abnahme

Der fokussierte W7-R-Bestand besteht mit:

```text
11 tests, OK
```

Der direkte W7-M/N/P/R-Verbund besteht mit:

```text
37 tests, OK
```

Der erweiterte relevante Verbund aus W7-R, W7-P, W7-N, W7-M,
kapazitaetsbegrenzten Kopplungs- und Runtimepfaden, F3- und
Baselinekopplungen, K2-B-Quellen sowie API-/Architekturverbrauchern besteht
mit:

```text
117 tests, OK
```

Geprueft sind Nullstart, Substratfreiheit, vollstaendige Ereigniszuordnung,
eindeutige atomare Ticks, exakter Endzustand, W7-P-Uebergabe,
Determinismus, vertauschte Modalitaetsreihenfolge, Fortsetzung in das naechste
Quellsegment, Digest- und Intervallsperren, Eingabeunveraenderlichkeit und
fehlender Export aus `current_api`.

## Unveraenderte Grenzen

Unveraendert blieben:

- `mcm_field_organism.__init__` und `current_api`;
- allgemeiner F3-P0-Wrapper und Produktionsruntime;
- Snapshot-Schemata;
- Browser-, Video- und Audiopfade;
- Reports und formale Forschungslaeufe;
- Lauf 197 und der einmalige W6-I-Lauf.

Die Tests verarbeiten kontrollierte W7-M-Quellsegmente ausschliesslich als
technische In-Memory-Abnahme. Daraus folgen keine Feldfunktion, kein Memory,
keine Ressourcenwiederverwendung, keine Feldzeit, Organisation, Semantik,
Selbstregulation oder KI.

## Naechster Schritt

W7-S muss statisch binden, wie die jeweils eigenen LEAK-, SAT- und NORM-
Zustaende ueber mehrere W7-R-/W7-P-Segmente fortgesetzt werden. Kein
Observerzustand darf zwischen Modellen geteilt, an P0 zurueckgegeben oder an
einer Checkpointgrenze stillschweigend auf null gesetzt werden. Noch keine
Implementierung, Hauptmatrix oder Forschungsauswertung.
