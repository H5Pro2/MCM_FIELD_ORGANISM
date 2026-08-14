# S1-DF: E1-A0-AV-History-Produktionsvertrag

## Status

Statischer Implementierungs- und Abnahmevertrag. S1-DF implementiert und
erzeugt noch keine E1-Historie, fuehrt keinen Feldlauf aus, startet keinen
Browser und bildet keine Probe oder Forschungsentscheidung.

## Technische Frage

Wie muessen die in S1-DE gebundenen reduzierten AB- und BA-Sequenzen durch
den vorhandenen S1-DB-Kompositor gefuehrt werden, damit zwei getrennte
E1-Endzustaende entstehen koennen, ohne dass E1 auf die jeweilige
Geschichte zurueckwirkt und ohne dass ein historischer S/H-Zustand in die
spaetere Probe gelangt?

S1-DF beantwortet nur die Schnittstellen- und Kontrollfrage. Ob `b_AB` und
`b_BA` verschieden ausfallen, wird weder vorausgesetzt noch in dieser Stufe
ermittelt.

## Gebundene Quelle

Einziger zulaessiger Eingang ist
`build_e1_av_history_permutation()` aus S1-DE. Vor jeder spaeteren
Ausfuehrung muessen exakt gelten:

```text
AB-Digest          a48d3d1620afa82d12dda855bb2ec03de3a57e7a69488d46edba6ec99cbef6d6
BA-Digest          bb1d887f1ff5809964ae8175c7fa661430e8fbc8502f0522a7003d6c6fc3c011
Permutationsdigest ad509ef23a9394009baddc8185edc5a13f76882ee79e7c31d3b0ec111bfbcc78
Organismusuhr      organism.e1.av-history
Historiengrenze    [0, 2000000]
Ticks je Sekunde   1000000.0
```

Jeder Arm enthaelt 200 auditive und 20 visuelle Frames. Die vorhandenen
S1-DE-Audits fuer Payload, Source-Supports, Organismus-Zeitslots, Masse und
Energie sind Pflichtvorbedingungen. Die Quelle darf im Produzenten nicht
neu reduziert, permutiert, skaliert oder vervollstaendigt werden.

## Fest gebundene Feldgeometrie

Das Feld wird ausschliesslich aus den ersten vorhandenen auditiven und
visuellen Referenzframes sowie der bestehenden allgemeinen AV-Anatomie
gebaut:

```text
auditive Carrier        12
visuelles Raster        6 x 4
visuelle Kanaele        3
visuelle Carrier        72
Feldknoten gesamt       84
Nachbarschaft           ORTHOGONAL_FIELD_SAMPLE_OFFSETS
```

Die Knotenzahl wird aus der Quelle validiert und nicht als freier
Versuchsparameter verwendet. Es gibt keine ergebnisbezogene Skalierung von
Geometrie, Knotenkapazitaet oder E1-Raten.

## Eingefrorene Konfiguration

Der spaetere Produzent verwendet ausschliesslich bereits implementierte
Rollen und folgende feste Konfiguration:

```text
NeutralLocalFieldSubstrateConfig.response_time_seconds  1.0
NeutralFastAfterimageConfig.time_constant_seconds       0.5
NeutralFieldDissipationConfig                            None

E1 contract_id                    e1.resource-conserving-local-edge-plasticity.v1
E1 node_capacity                  1.0 je Feldknoten
E1 binding_rate_per_second        1.5
E1 release_rate_per_second        0.25
E1 backreaction_gain              0.5
History backreaction_enabled      False
```

Die einzige Proposal-Grenze ist:

```text
MCMFieldStepTime("organism.e1.av-history", 0, 2000000, 1000000.0)
```

Es duerfen keine zusaetzlichen Ticks, Pausen, Wiederholungen oder
modalitaetsabhaengigen Parametersaetze eingefuehrt werden.

## Vier interne Pflichtarme

```text
AB-P0: frisches Feld, H-AB, neutraler asynchroner Feldpfad ohne E1
AB-A0: frisches Feld, H-AB, neutraler E1-Start, Rueckwirkung aus
BA-P0: frisches Feld, H-BA, neutraler asynchroner Feldpfad ohne E1
BA-A0: frisches Feld, H-BA, neutraler E1-Start, Rueckwirkung aus
```

`AB-P0` und `BA-P0` sind getrennte technische Ablationsbaselines. Ihre
Endfelder muessen nicht untereinander gleich sein, weil die zeitliche
Quellenordnung verschieden ist. Verbindlich sind nur die paarweisen
Identitaeten:

```text
Endfeld(AB-A0) == Endfeld(AB-P0) bitgenau
Endfeld(BA-A0) == Endfeld(BA-P0) bitgenau
```

Ein direkter Vergleich `Endfeld(AB-P0)` gegen `Endfeld(BA-P0)` ist keine
E1-Metrik und darf keine Entscheidung ausloesen.

## Frische- und Objektgrenzen

Alle vier Arme beginnen mit objektgetrennten Feldern. Deren strukturelle
Frischfeld-, Layer-, Dock-, Neuronen-, Kanten- und Geometriedigests muessen
wertidentisch sein. Ein Runtime-Snapshot ist vor dem ersten abgeschlossenen
Rezeptorkontakt nicht zulaessig. Es ist verboten, einen Arm aus dem Endfeld eines
anderen Arms, aus einem neutralen Snapshot mit E1-Zusatz oder aus einem
frueheren Lauf wiederherzustellen.

`AB-A0` und `BA-A0` erhalten je einen neu gebauten neutralen E1-Zustand.
Beide Zustaende muessen wertidentisch, objektgetrennt, vollstaendig neutral
und an denselben Kanteninventardigest gebunden sein. Auch die beiden P0-Arme
teilen keine veraenderlichen Feldobjekte.

Die Eingabesequenzen und ihre Frames bleiben unveraendert. Dass S1-DE beim
Blocktausch dieselben unveraenderlichen Frameobjekte wiederverwendet, ist
zulaessig; Feld-, Handoff-, E1- und Ergebnisobjekte duerfen dagegen nicht
zwischen Armen geteilt werden.

## Private Zieloberflaeche fuer S1-DG

Die naechste Implementierung darf genau einen privaten Produzenten und
einen unveraenderlichen Ergebniscontainer hinzufuegen. Sinngemaess:

```text
produce_e1_a0_av_histories(source) -> E1A0AVHistoryProduction
```

Der Ergebniscontainer darf nach vollstaendiger interner Validierung nur
folgende Rollen tragen:

```text
b_ab                              E1-Endzustand aus AB-A0
b_ba                              E1-Endzustand aus BA-A0
source/permutation digests        unveraenderte S1-DE-Bindung
initial geometry/fresh-field digest gemeinsame Frischebindung
AB- und BA-P0/A0-Endfelddigests    paarweise Ablationskontrolle
Handoff- und Ereignisaudits        Vollstaendigkeit je Arm
E1-Ressourcenaudits                Bilanz je E1-Endzustand
production digest                  vollstaendige technische Bindung
```

Historische `SharedMCMField`-Objekte, letzte Rezeptorverteilungen,
Snapshots als Restore-Objekte, aktive Adapter oder Probeobjekte duerfen
nicht Teil der rueckgegebenen Oberflaeche sein. Der Produzent bleibt aus
`__init__.py` und `current_api.py` ausgeschlossen und darf bei Import oder
Objektaufbau nichts ausfuehren.

## Pflichtinvarianten

1. Alle S1-DE-Quellenidentitaeten und Digests stimmen vor dem ersten Arm.
2. Jeder der vier Arme startet aus einem frischen, wertidentischen Feld.
3. Beide E1-Arme starten aus objektgetrennten neutralen E1-Zustaenden.
4. `backreaction_enabled` ist in beiden E1-Armen exakt `False`.
5. A0 ist in AB und BA jeweils bitgenau der zugehoerige P0-Feldarm.
6. Alle 220 eindeutigen Source-Supports werden je Arm genau einmal
   zugeordnet; kein Ereignis liegt vor Start oder nach dem Horizont.
7. Handoff-, Batch- und Abschlusszeitordnung bleibt innerhalb jedes
   Quellenarms unveraendert.
8. E1-Zustand und Feld besitzen jederzeit denselben Kanteninventardigest.
9. Freie und gebundene lokale E1-Ressourcen bleiben endlich, nichtnegativ
   und innerhalb der Kapazitaetsidentitaet.
10. Alle aufgerufenen E1-Adapter sind als ablatierte Rueckwirkung markiert.
11. Eingabequelle, Felder und neutrale E1-Startzustaende bleiben
    unveraendert; ein Fehler liefert keinen Teilcontainer.
12. Nur `b_ab` und `b_ba` duerfen spaeter eine Probegrenze ueberqueren.

S1-DG darf synthetisch ausserdem beweisen, dass vertauschte
Modalitaetsdeklarationsreihenfolge bei gleichen Abschlusszeiten dasselbe
Ergebnis liefert und dass ein fremder Quell-, Geometrie-, Uhr- oder
Konfigurationsdigest hart abgewiesen wird.

## Abbruchbedingungen

Der Produzent muss ohne Teilergebnis abbrechen, wenn mindestens eine der
folgenden Bedingungen eintritt:

- eine S1-DE-Identitaet oder ein gebundener Digest weicht ab;
- Geometrie oder Carrierinventar passt nicht zur Quelle;
- ein Startfeld oder E1-Zustand wurde zwischen Armen wiederverwendet;
- ein E1-Startzustand ist nicht neutral;
- A0 weicht vom jeweils zugeordneten P0-Feld ab;
- ein Source-Support fehlt, doppelt ist oder ausserhalb des Horizonts liegt;
- eine Ressource, ein Feldwert oder ein Nachhallwert ist nicht endlich oder
  verlaesst seine bestehende gueltige Grenze;
- historische S/H- oder Restore-Rollen gelangen in den Ausgabecontainer;
- fuer ein gewuenschtes Ergebnis muessten Parameter, Quelle oder Reihenfolge
  nachtraeglich veraendert werden.

## Zulaessiger spaeterer Befund

Nach Implementierung und synthetischer Abnahme darf S1-DG hoechstens melden:

```text
E1_A0_AV_HISTORY_PRODUCER_READY
```

Dieser Befund bedeutet nur, dass der Produzent technisch kontrolliert und
ausfuehrbar ist. Er sagt nicht, dass `b_AB` und `b_BA` verschieden sind.

## Aussagegrenze

S1-DF erzeugt keine Geschichte und keinen empirischen Befund. Auch eine
spaetere unterschiedliche E1-Endlage waere zunaechst nur eine technisch
history-spezifische Zustandsdifferenz. Weder S1-DF noch der
Bereitschaftsbefund aus S1-DG belegen Einpraegung, Vergessen,
Rekonstruktion, MCM-Memory, inneren Kontext, Semantik, Organisation,
Topologie, Selbstregulation oder KI.

## Quellen

- `S1DA_E1_KONTROLLIERTER_AV_INTEGRATIONSVERTRAG.md`
- `S1DB_E1_TRANSIENTE_AV_INTEGRATION_UND_ABNAHME.md`
- `S1DC_E1_ZWEIPHASIGER_AV_HISTORY_PROBEVERTRAG.md`
- `S1DD_E1_EINGEFRORENER_TRANSIENTER_PROBEOPERATOR.md`
- `S1DE_E1_REDUZIERTE_AV_HISTORY_PERMUTATION.md`
- `mcm_field_organism/e1_asynchronous_field_runtime.py`
- `mcm_field_organism/e1_av_history_permutation.py`
- `mcm_field_organism/e1_local_edge_plasticity.py`
- `mcm_field_organism/neutral_asynchronous_field_runtime.py`
- `mcm_field_organism/audio_video_field_geometry.py`
- `mcm_field_organism/shared_mcm_field.py`

## Bester naechster Schritt

S1-DG implementiert den privaten Produzenten und nimmt ihn zuerst mit kleinen
synthetischen In-Memory-Sequenzen ab. Geprueft werden Frische, P0/A0-
Identitaet, Handoff-Vollstaendigkeit, Ressourcenbilanz, Fehlerfaelle und
API-Isolation. Die kanonischen S1-DE-Historien werden dabei noch nicht durch
E1 ausgefuehrt; eine reale AB/BA-History-Produktion bleibt bis zu einer
separaten finalen Vorpruefung gesperrt.

S1-DG ist inzwischen privat implementiert und mit 7 fokussierten sowie 114
relevanten `unittest`-Tests synthetisch abgenommen. Die kanonischen
S1-DE-Historien wurden nicht durch E1 ausgefuehrt. Siehe
`S1DG_E1_A0_AV_HISTORY_PRODUZENT_UND_ABNAHME.md`.
