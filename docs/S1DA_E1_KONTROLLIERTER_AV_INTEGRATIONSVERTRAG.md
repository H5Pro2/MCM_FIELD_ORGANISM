# S1-DA: E1 kontrollierter AV-Integrationsvertrag

## Status

Statischer Integrationsvertrag. Es wurde keine Runtime implementiert, kein
Test ausgefuehrt und kein Ergebnisartefakt erzeugt. S1-DA fuehrt weder den
gestoppten Drei-Knoten-Rekonstruktionszweig fort noch erteilt es einen
Memorybefund.

## Forschungsfrage

Kann die bereits isoliert nachgewiesene E1-Feldplastizitaet ohne neue
Gleichung, neue Parameter oder Musterkodierung an die vorhandene
kontrollierte Audio-/Video-Feldpipeline angeschlossen werden, waehrend
Zeitordnung, lokale Ressourcenbilanz, Modalitaetsgrenzen und Ablation
vollstaendig pruefbar bleiben?

## Vorhandene Anschlussgrenze

Beide zulaessigen Weltquellen liefern bereits dieselbe Form:

```text
synthetische AV-Testwelt oder kontrollierte Browser-Testwelt
-> ReceptorTimeSequence("auditory", ...)
-> ReceptorTimeSequence("visual", ...)
-> handoff_receptor_completion_groups(...)
-> TransientNeuronInputSet je geordnetem Proposal-Batch
-> gemeinsames schnelles S/H-Feld
```

E1 wird erst hinter `TransientNeuronInputSet` angeschlossen. Dadurch kennt
E1 keine Rohbilder, Audiosamples, Dateinamen, Weltidentitaeten, Labels oder
Browserrollen. Seine einzige Ursache bleibt die lokale Aktivierungsdifferenz
auf vorhandenen Feldkanten.

## Technische Integrationsluecke

`advance_e1_coupled_fast_shared_field(...)` unterstuetzt bisher den
synchronen `ReceptorDistribution`-Pfad. Der aktuelle AV-Pfad verwendet
dagegen impulsartige lokale Kontakte in `TransientNeuronInputSet`.

Ein fertiges AV-Endfeld nachtraeglich an E1 zu uebergeben waere unzulaessig:
Die zeitliche Reihenfolge der Weltkontakte ginge verloren. Die erste
Implementierung muss deshalb einen privaten transienten E1/S/H-Schritt
bereitstellen. Sie darf die E1-Gleichung und den Rezeptor-Handoff nicht
veraendern.

## Private Zieloberflaeche

S1-DB darf hoechstens zwei private Rollen implementieren:

```text
advance_e1_coupled_fast_shared_field_transient(
    field,
    e1_state,
    distribution,
    transient_inputs,
    substrate_config,
    afterimage_config,
    dissipation_config=None,
    *,
    backreaction_enabled,
) -> E1CoupledFastFieldStepResult

run_e1_asynchronous_field(
    field,
    e1_state,
    sequences,
    proposal_steps,
    substrate_config,
    afterimage_config,
    dissipation_config=None,
    *,
    backreaction_enabled,
) -> privates unveraenderliches Ergebnis
```

Die Namen duerfen bei der Implementierung dem lokalen Modulstil angepasst
werden. Die Rollen und Eingangsgrenzen bleiben verbindlich. Es gibt keinen
Export aus `__init__.py` oder `current_api.py` und keine Aenderung an
`advance_audio_video_receptor_sequences(...)`.

## Verbindliche Zeitordnung

Der asynchrone Handoff und seine Batches bleiben unveraendert. Innerhalb
jedes Batches werden alle Kontaktabschluesse nach ihrem technischen
`completion_tick` gruppiert. Fuer jedes positive Teilintervall zwischen zwei
Grenzen gilt dieselbe symmetrische E1-Ordnung wie in S1-BT:

```text
1. E1 halbes Teilintervall aus abgeschlossenem S-Anfangszustand
2. internen E1-Adapter fuer dieses Teilintervall bilden
3. S/H bis zur naechsten Abschlussgrenze entwickeln
4. alle dort faelligen lokalen Punktkontakte gemeinsam anwenden
5. E1 halbes Teilintervall aus abgeschlossenem S-Endzustand
```

Gleichzeitige Kontakte werden gemeinsam und nicht in einer
modalitaetsabhaengigen Reihenfolge angewendet. Zwischen zwei Ereignissen
erhaelt E1 keine kuenstlichen Ticks. Ein Abschlusszeitpunkt darf weder
doppelt gezaehlt noch in ein Speicherkommando umgedeutet werden.

## Unveraenderter E1-Vertrag auf AV-Geometrie

Die bestehende E1-Konfiguration bleibt eingefroren:

```text
contract_id                    e1.resource-conserving-local-edge-plasticity.v1
node_capacity                 1.0 je Feldknoten
binding_rate_per_second       1.5
release_rate_per_second       0.25
backreaction_gain             0.5
```

Die Knotenkapazitaet ist lokal. Bei einer groesseren Geometrie waechst nur
die Zahl der lokalen Kapazitaeten und vorhandenen Kanten; kein Parameter
wird durch Neuronenzahl, Modalitaet, Welt oder gewuenschtes Ergebnis
reskaliert. `build_neutral_e1_state(...)` muss das vollstaendige bestehende
Kanteninventar und dessen Digest binden.

## Verbindliche Vergleichsarme

### P0: neutrale AV-Feldpipeline

Der bestehende unveraenderte Pfad ohne E1. Er bleibt die primaere
Runtime-Gegenbaseline.

### A0: E1-Entwicklung mit ablatierter Rueckwirkung

E1 wird entlang derselben Ereigniszeiten entwickelt,
`backreaction_enabled=False`. Das S/H-Ergebnis muss P0 bei identischen
Eingaben bitgenau entsprechen. Dafuer darf A0 intern an den bestehenden
neutralen transienten Feldschritt delegieren; die E1-Beobachtung darf dessen
Feldentwicklung nicht veraendern.

### A1: aktive E1-Rueckwirkung

E1 wird entlang derselben Ereigniszeiten entwickelt und gewichtet nur die
bereits vorhandenen internen Feldkanten. Rezeptoramplituden, Kontaktzeiten,
Docks und H-Nachhall bleiben unveraendert.

### F0: eingefrorener Adapter

Fuer einen spaeteren zweiphasigen Vergleich werden die aus einem
vorab gebundenen E1-Zustand abgeleiteten Kantenraten waehrend der gesamten
identischen Probe eingefroren. F0 prueft, ob eine spaetere Feldabweichung
vollstaendig durch einen statischen raeumlichen Gain erklaert wird. F0 ist
Kontrollobergrenze, kein eigenes Substrat.

S1-DB implementiert zunaechst nur P0, A0 und A1. F0 wird erst vor einer
funktionalen AV-Probe implementiert, damit kein Zielzustand vorweggenommen
wird.

## Modalitaetsarme

Die Geometrie und beide Sequenzrollen bleiben in jedem Arm vollstaendig.
Eine technische Modalitaetsablation ersetzt nur die Werte der betreffenden
Sequenz durch null und erhaelt Zeitfenster, Carrier, Docks und Ereigniszahl:

```text
N0: Audio null, Video null
A:  Audio aktiv, Video null
V:  Audio null, Video aktiv
AV: Audio aktiv, Video aktiv
```

Jeder Modalitaetsarm wird nur zwischen P0, A0 und A1 bei exakt derselben
Quelle verglichen. A, V und AV duerfen nicht direkt als staerker oder
schwaecher interpretiert werden, solange ihre Eingangsmasse nicht
angeglichen ist. Die Ablation ist eine technische Quellenkontrolle und keine
Behauptung organismischer Aufmerksamkeitsregulation.

## Pflichtinvarianten fuer S1-DB

1. Handoff-Digest, Batchreihenfolge und Anzahl eindeutiger Source-Supports
   sind in P0, A0 und A1 identisch.
2. Jedes Ereignis wird genau einmal verarbeitet.
3. A0-S/H ist bei beliebigem gueltigem E1-Zustand bitgenau P0.
4. A1 wird bei `backreaction_gain=0` bitgenau A0.
5. E1-Zustand und Feld besitzen vor und nach jedem Batch denselben
   Kanteninventardigest.
6. Freie und gebundene Ressource bleiben an jedem Knoten nichtnegativ und
   innerhalb der bestehenden Kapazitaetsidentitaet.
7. S und H bleiben endlich und im normierten Bereich.
8. Gleichzeitige Audio-/Videoabschluesse sind gegen Deklarationsreihenfolge
   invariant.
9. Eingabeobjekte bleiben unveraendert; Fehler liefern keinen Teilzustand.
10. P0, die oeffentliche API und neutrale Snapshots bleiben unveraendert.
11. E1 wird nicht in neutrale Runtime-Snapshots aufgenommen.
12. Keine Kamera, kein Live-Mikrofon, kein Browserstart und kein
    Ergebnisreport gehoeren zur S1-DB-Abnahme.

## Abbruchbedingungen

Die Integration wird verworfen, wenn fuer ihren Betrieb mindestens eine der
folgenden Bedingungen noetig wird:

- modalitaets-, welt- oder musterspezifische E1-Parameter;
- ein Label, Reward, Zielmuster oder externer Speicherindex;
- Verlust oder Neusortierung der vorhandenen Ereigniszeiten;
- verdeckte Aenderung von Rezeptoramplituden oder Docks;
- Verletzung der lokalen E1-Ressourcenbilanz;
- eine A0-Feldabweichung gegen P0;
- Aufnahme von E1 in die oeffentliche neutrale Zustandswahrheit.

## Aussagegrenze

Ein Bestehen von S1-DB wuerde nur zeigen, dass E1 technisch und kausal auf
der bestehenden kontrollierten AV-Geometrie mitgefuehrt werden kann. Es
belegt keine Einpraegung, kein Vergessen, keine Rekonstruktion, kein
MCM-Memory, keinen inneren Kontext, keine Semantik, keine Organisation,
keine Topologie, keine Selbstregulation und keine KI.

## Quellen

- `S1CZ_EVIDENZAUDIT_UND_AV_INTEGRATIONSENTSCHEID.md`
- `S1BP_E1_ISOLIERTER_ZUSTANDSCONTAINER_UND_IMPLEMENTIERUNGSGRENZE.md`
- `S1BR_E1_ABLATIERBARER_KANTENRATENADAPTER.md`
- `S1BT_E1_ATOMARER_GEKOPELTER_S_H_SCHRITTVERTRAG.md`
- `S1BD_GEMEINSAME_ZEIT_HANDOFF_UND_FELDGRENZE.md`
- `mcm_field_organism/audio_video_neutral_field_runtime.py`
- `mcm_field_organism/neutral_asynchronous_field_runtime.py`
- `mcm_field_organism/e1_local_edge_plasticity.py`
- `mcm_field_organism/e1_coupled_fast_field.py`

## Bester naechster Schritt

S1-DB implementiert ausschliesslich den privaten transienten E1-Schritt und
den privaten asynchronen Kompositor. Seine Abnahme verwendet synthetische
In-Memory-Sequenzen und prueft P0, A0, A1, Zeitordnung, Ressourcenbilanz und
API-Isolation. Es wird noch kein Forschungs- oder Browserlauf ausgefuehrt.

S1-DB ist inzwischen implementiert und mit 76 relevanten `unittest`-Tests
abgenommen. Der tatsaechliche transiente Ergebniscontainer fuehrt wegen der
asynchronen Zeitordnung einen Adapter je positivem Teilintervall statt eines
einzelnen Endadapters. Siehe
`S1DB_E1_TRANSIENTE_AV_INTEGRATION_UND_ABNAHME.md`.
