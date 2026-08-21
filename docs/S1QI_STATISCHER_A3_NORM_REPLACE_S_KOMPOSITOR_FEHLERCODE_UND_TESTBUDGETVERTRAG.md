# S1-QI: Statischer A3-NORM-REPLACE_S-Kompositor-, Fehlercode- und Testbudgetvertrag

## Status und Umfang

S1-QI bindet ausschliesslich die spaetere begrenzte Implementierung des in
S1-QH gewaehlten `REPLACE_S`-Feldhandoffs. Der Vertrag legt fest:

- eine private Modul- und Importgrenze;
- eine diskriminierte synchrone oder transiente Intervalloberflaeche;
- die atomare A1-NORM-REPLACE_S-Reihenfolge;
- vollstaendige Eingabe-, Receipt- und Resultatrollen;
- ein endliches, deterministisches Fehlervokabular;
- ein kleines einmaliges technisches Testbudget.

S1-QI enthaelt keine neue Feld- oder NORM-Gleichung, keine Parameterwerte,
keine Fixturewerte, keine Implementierung, keine Runtimeintegration und keine
Ausfuehrung. Es wird kein Feldlauf und keine Ergebnisentscheidung freigegeben.

Verbindliche Entscheidung:

```text
PRIVATE_A3_NORM_REPLACE_S_COMPOSITOR_SURFACE_BOUND
SYNC_OR_TRANSIENT_SINGLE_INTERVAL_DISCRIMINATOR_BOUND
ATOMIC_RESULT_FAILURE_CODES_AND_SINGLE_TEST_BUDGET_BOUND
NO_EQUATIONS_NO_VALUES_NO_IMPLEMENTATION_NO_EXECUTION
```

## Gebundene Implementierungsgrenze

Ein spaeterer S1-QJ-Schritt darf genau drei neue Dateien anlegen:

| Datei | Aufgabe |
|---|---|
| `mcm_field_organism/a3_norm_replace_s_compositor.py` | privater atomarer Intervallkompositor samt Resultat und Receipt |
| `tests/a3_norm_replace_s_s1qj_fixtures.py` | kleine kanonische Gueltig- und Fehlermutationsfixtures |
| `tests/test_a3_norm_replace_s_s1qj_compositor.py` | fokussierte technische Abnahme |

Bestehende Produktions-, Runner-, Feldkern-, W7-N- und API-Dateien bleiben
unveraendert. Die drei vorrangigen Statusdokumente duerfen nach der einmaligen
Abnahme nur um das tatsaechliche Ergebnis ergaenzt werden.

Insbesondere bleiben gesperrt:

- `mcm_field_organism/current_api.py` und alle Root-Exports;
- Orchestrator-, Runner-, Medien- und Lebenszyklusmodule;
- der primaere `SharedMCMField`- und A1-Fast-Kern;
- der vorhandene W7-N-Lokalkern;
- alle Kandidaten-, Substrat- und Entwicklungsmodule.

Der Kompositor bleibt eine private technische Gegenbaseline.

## Erlaubte Abhaengigkeiten

Das neue Produktionsmodul darf ausser der Python-Standardbibliothek nur die
vorhandenen Typen und Funktionen aus folgenden Modulen importieren:

```text
mcm_field_organism.shared_mcm_field
mcm_field_organism.field_step_time
mcm_field_organism.transient_neuron_input
mcm_field_organism.receptor_distributor
mcm_field_organism.neutral_local_field_substrate
mcm_field_organism.w7m_capacity_function_matrix
mcm_field_organism.w7n_capacity_function_baselines
```

Es darf keine alternative A1- oder NORM-Rechnung nachbilden. Fuer den
A1-Vorschlag ist je nach Intervallform genau eine der vorhandenen Funktionen
aufzurufen:

```text
advance_neutral_fast_shared_field
advance_neutral_fast_shared_field_transient
```

Fuer NORM sind ausschliesslich `W7NLocalBaselineState` und
`advance_w7n_local_baseline` zulaessig. Eine eigene Normalisierung, ein
zweiter Integrator oder eine nachtraegliche Feldreparatur ist verboten.

## Private Aufrufoberflaeche

S1-QJ darf genau eine ausfuehrende Funktion bereitstellen:

```text
advance_a3_norm_replace_s(
    field,
    distribution,
    interval_input,
    neutral_substrate_config,
    fast_afterimage_config,
    norm_spec,
    norm_prestate,
    dissipation_config=None,
) -> A3NormReplaceSResult
```

`interval_input` ist exakt eine der beiden vorhandenen Rollen:

```text
MCMFieldStepTime | TransientNeuronInputSet
```

Der konkrete Typ bestimmt ausschliesslich, welcher vorhandene A1-Fast-Pfad
verwendet wird. Arm-, Familien-, Checkpoint- oder Ergebnislabels duerfen
diese Auswahl nicht beeinflussen. Andere Typen, eine Doppelbelegung oder
eine implizite Konvertierung sind unzulaessig.

Die Funktion wird weder in die aktive API exportiert noch von einem Runner
aufgerufen. Die spaetere S1-QJ-Abnahme darf sie nur direkt als isolierte
Komponente testen.

## Eingabegrenze

Ein gueltiger Aufruf bindet gemeinsam:

- ein vollstaendiges neutrales `SharedMCMField` ohne Substrat oder
  Entwicklungszustand;
- genau eine aktuelle `ReceptorDistribution`;
- genau eine dazu passende technische Intervallform;
- unveraenderte A1-Konfigurationen;
- eine unveraenderte W7-M-Spezifikation mit Modellrolle `norm`;
- einen vollstaendigen NORM-Vorzustand derselben Geometrie und Knotenanzahl.

Die kanonische NORM-Ortsordnung ist exakt die Reihenfolge der Neuronen im
vollstaendigen Feld. Die API akzeptiert keine getrennte Ortsliste, keine
Teilmenge und keine nachtraegliche Sortieranweisung.

Nicht zulaessig sind:

- Kandidaten-, Substrat-, Entwicklungs- oder Ressourcenpayloads;
- Expositionsfamilie, Armname, Zielrichtung oder Comparatorresultat;
- vorheriger NORM-Output oder Skalierungsrecord als Eingabe;
- historische Observertraces, Replayfolgen oder Profilzustaende;
- ein extern erzeugter A1-Vorschlag oder NORM-Folgezustand;
- ein zweiter Feldzeit-, Integrations- oder Reparaturauftrag.

## Gebundene Phasenordnung

Jeder fachlich erreichbare Aufruf folgt exakt dieser logischen Reihenfolge:

```text
1. api_intake
2. common_identity_validation
3. interval_discrimination
4. a1_fast_proposal
5. a1_proposal_validation
6. norm_advance
7. norm_output_validation
8. replace_s_materialization
9. final_field_validation
10. atomic_receipt
```

Der erste Fehler beendet alle nachfolgenden Phasen. Keine Fehlerphase darf
Sachwerte reparieren, normalisieren, neu ordnen oder mit einem zweiten
Rechenversuch ersetzen.

## Atomare Kompositionspflicht

Der Kompositor muss intern genau folgende Kausalordnung einhalten:

```text
gueltige Eingaben
    -> genau ein vollstaendiger A1-Fast-Vorschlag
    -> dessen vollstaendiges S als NORM-Evidence
    -> genau ein vollstaendiges W7-N-NORM-Resultat
    -> finales Feld durch vollstaendige S-Ersetzung
    -> genau ein atomarer Resultatabschluss
```

Beim finalen Feld darf ausschliesslich jede Aktivierung `S` durch den
zugeordneten signed NORM-Output ersetzt werden. Gegen den internen
A1-Vorschlag muessen bitgleich bleiben:

- Feld-, Schicht-, Geometrie- und Knotenidentitaeten;
- Knotenpositionen, Dockrollen und Perzeptionen;
- vollstaendiges H jedes Knotens;
- Tick, abgeschlossene Rezeptorverteilung und Feldzeitbezug;
- die Abwesenheit von Substrat- und Entwicklungszustand.

Das finale Feld wird konstruiert, aber nicht erneut fortgeschrieben. Der
interne A1-Vorschlag wird nicht publiziert, gespeichert oder als separates
Feldresultat zurueckgegeben.

## Resultat- und Receiptrollen

`A3NormReplaceSResult` enthaelt genau:

```text
field: SharedMCMField | NOT_COMPUTABLE
next_norm_state: W7NLocalBaselineState | NOT_COMPUTABLE
receipt: A3NormReplaceSReceipt
```

Ein gueltiger Receipt bindet mindestens:

- Vertrags- und Konfigurationsidentitaeten;
- Intervallform und Eingabeprovenienz;
- Feldvorzustands-, NORM-Vorzustands- und Geometriedigest;
- internen A1-Vorschlagsdigest;
- NORM-Folgezustandsdigest;
- Digest des vollstaendigen signed NORM-Outputs;
- Skalierungsprovenienz aus allen lokalen Folgezustaenden;
- finalen Felddigest;
- Beleg der vollstaendigen S-Ersetzung und H-Identitaet;
- Beleg genau einer Feldzeitfortschreibung;
- abgeschlossene Phasen, Status, Fehlercodes und Receiptdigest.

Der Receipt darf den A1-Vorschlag und den signed Output nur kanonisch
belegen, nicht als zweites Feld oder zusaetzlichen Carryzustand ausgeben.

Es gibt genau zwei Abschlussstatus:

```text
COMPLETED
NOT_COMPUTABLE
```

Bei `NOT_COMPUTABLE` sind `field` und `next_norm_state` gemeinsam
`NOT_COMPUTABLE`. Ein Feld ohne Folgezustand oder ein Folgezustand ohne Feld
ist unzulaessig.

## Kanonische Digests

Alle Digests werden aus typisierten kanonischen Payloads mit fest
sortierten Objektschluesseln und erhaltener Knotenreihenfolge gebildet.
Flieszahlen werden aus ihrer bereits validierten technischen Darstellung
uebernommen und nicht gerundet oder textuell nachnormalisiert.

Der Gesamtdigest bindet mindestens:

```text
contract -> inputs -> A1 proposal -> NORM state/output -> final field
         -> phases -> status -> failure codes
```

Ein Digest darf keine Python-Objektadresse, Prozesszeit, Dateiposition oder
Orchestrierungsrolle enthalten. Derselbe gueltige Aufruf muss denselben
Receipt erzeugen.

## Endliches Fehlervokabular

S1-QJ bindet exakt diese vierzehn Fehlercodes:

```text
QI_INPUT_TYPE_INVALID
QI_FIELD_ROLE_INVALID
QI_DISTRIBUTION_OR_INTERVAL_INVALID
QI_CONFIGURATION_INVALID
QI_NORM_PRESTATE_INVALID
QI_GEOMETRY_OR_ORDER_MISMATCH
QI_A1_ADVANCE_FAILED
QI_A1_PROPOSAL_INVALID
QI_NORM_ADVANCE_FAILED
QI_NORM_OUTPUT_INVALID
QI_S_REPLACEMENT_FAILED
QI_H_OR_PROVENANCE_CHANGED
QI_FIELD_TIME_CARDINALITY_FAILED
QI_ATOMIC_OUTPUT_FAILED
```

Fehlercodes sind eindeutig, in Phasenreihenfolge sortiert und
deterministisch. Ein Aufruf darf mehrere bereits in derselben abgeschlossenen
Validierungsphase festgestellte Codes tragen, aber keine Codes aus einer
nicht erreichten Phase. Unbekannte Ausnahmen werden nicht in einen
scheinbaren Sachfehler uminterpretiert; sie verhindern jede Publikation.

## Kontrollierte Fehlermutationen

Die spaetere Fixturedatei bindet genau vierzehn isolierte Mutationsklassen:

1. falscher Typ an einer Pflichtgrenze;
2. Feld mit Substrat- oder Entwicklungszustand;
3. unpassende Distribution oder Intervallform;
4. nicht-NORM oder veraenderte Konfiguration;
5. falscher oder unvollstaendiger NORM-Vorzustand;
6. abweichende Knotenanzahl oder Knotenordnung;
7. kontrolliertes Scheitern des vorhandenen A1-Aufrufs;
8. ungueltiger oder zeitlich abweichender A1-Vorschlag;
9. kontrolliertes Scheitern des vorhandenen NORM-Aufrufs;
10. unvollstaendiger, nicht endlicher oder falsch geordneter NORM-Output;
11. partielle oder falsche S-Ersetzung;
12. veraendertes H oder veraenderte Feldprovenienz;
13. zweiter Tick oder abweichendes Zeitfenster;
14. simuliertes Scheitern vor atomarer Resultatpublikation.

Jede Mutation muss ohne Sachoutput mit ihrem vorab zugeordneten Fehlercode
enden. Es gibt keine Reparaturfixture und keinen Retry.

## Genau achtzehn neue Testmethoden

Das einmalige S1-QJ-Testbudget umfasst genau:

1. Modul-, Typ-, Status- und Fehlercodeoberflaeche;
2. deterministische kanonische Frischfixtures;
3. gueltiger synchroner REPLACE_S-Schritt;
4. gueltiger transienter REPLACE_S-Schritt;
5. exakte vollstaendige S-Ersetzung und signed Ortsordnung;
6. bitgleiche H-, Perzeptions-, Dock- und Identitaetsrollen;
7. genau eine Feldzeitfortschreibung in beiden Intervallformen;
8. korrekter gemeinsamer Carry aus finalem Feld und NORM-Folgezustand;
9. deterministische Resultat- und Receiptdigests;
10. Nullzustands- und Nulloutputstruktur;
11. gemeinsame Geometriepermutation ohne Positionssemantik;
12. globale NORM-Kopplung ohne Edge-Transfer;
13. keine Veroeffentlichung des internen A1-Vorschlags;
14. keine verbotenen Imports, Exporte oder Seiteneffekte;
15. Mutationsklassen 1 bis 5 und ihre exakten Fehlercodes;
16. Mutationsklassen 6 bis 10 und ihre exakten Fehlercodes;
17. Mutationsklassen 11 bis 14 und ihre exakten Fehlercodes;
18. atomare `NOT_COMPUTABLE`-Paarung ohne Teiloutput.

Die Tests 10 bis 12 sind strukturelle technische Gegenprognosen, keine
Feldstudie. Sie verwenden nur kleine synthetische In-memory-Fixtures.

## Einmalige Ausfuehrungsgrenze

S1-QJ darf nach Implementierung genau einen kombinierten Testaufruf fuer die
neue Testdatei und die direkt beruehrten bestehenden A1-, W7-N-, transienten
Eingabe- und Shared-Field-Regressionen ausfuehren:

```powershell
.\.venv\Scripts\python.exe -m unittest tests.test_a3_norm_replace_s_s1qj_compositor tests.test_neutral_local_field_substrate tests.test_w7n_capacity_function_baselines tests.test_transient_neuron_input tests.test_receptor_distributor_and_shared_field
```

Dieser eine Prozess ist das vollstaendige S1-QJ-Ausfuehrungsbudget.

Nicht freigegeben sind:

- die gesamte Testsuite;
- ein Orchestrator-, Runner- oder Feldlauf;
- reale Medien- oder Sensorinputs;
- Profil-, Parameter- oder Wiederholungssuchen;
- ein Vergleich mit einem Kandidaten;
- eine funktionale Ergebnisentscheidung.

Ein fehlgeschlagener Einmallauf darf analysiert werden. Eine Codekorrektur
oder Wiederholung benoetigt einen neuen statischen Reparaturvertrag und darf
nicht still innerhalb von S1-QJ erfolgen.

## Abnahmekriterien

S1-QJ ist nur technisch abgeschlossen, wenn gemeinsam gilt:

```text
PRIVATE_COMPONENT_ONLY
EXISTING_A1_AND_NORM_KERNELS_REUSED
SYNC_AND_TRANSIENT_INTERVALS_DISCRIMINATED
EXACT_REPLACE_S_AND_H_IDENTITY_CONFIRMED
ONE_FIELD_TIME_ADVANCE_CONFIRMED
ATOMIC_FAIL_CLOSED_CONFIRMED
NO_RUNNER_OR_ACTIVE_API_INTEGRATION
```

Auch eine vollstaendige technische Abnahme macht das Pflichtbaselinepaket
noch nicht ausfuehrbar. Dafuer fehlen weiterhin die gemeinsamen
Lebenszyklushuellen, registrierten Konfigurationen, Fallmatrix und
Comparatorbindung.

## Aussagegrenze

S1-QI spezifiziert nur eine technische Gegenbaseline. Es gibt keine neue
Kandidatenmechanik, keinen Feldlauf und keinen Befund zu einer hypothetischen
MCM-Memory. Der primaere MCM-Wahrnehmungsfeldkern bleibt unveraendert.

## Genau ein naechster Schritt

Als einziger Anschluss ist zulaessig:

```text
S1-QJ - begrenzte Implementierung und einmalige technische Abnahme des
        privaten A3-NORM-REPLACE_S-Kompositors
```

S1-QJ darf ausschliesslich die drei gebundenen Dateien erstellen und den
einmaligen fokussierten Testaufruf ausfuehren. Keine API- oder
Runtimeintegration, kein Orchestrator, kein Feldlauf, keine Fallmatrix und
keine Ergebnisentscheidung.
