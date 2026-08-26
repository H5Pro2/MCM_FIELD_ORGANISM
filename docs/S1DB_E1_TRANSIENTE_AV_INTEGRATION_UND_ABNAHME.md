# S1-DB: E1 transiente AV-Integration und Abnahme

## Status

Die in S1-DA gebundene private Integrationsscheibe ist implementiert und
synthetisch abgenommen. Es wurde kein Browser gestartet, kein
Forschungsrunner ausgefuehrt und kein Ergebnisreport erzeugt.

## Implementierte Module

```text
mcm_field_organism/e1_transient_coupled_field.py
mcm_field_organism/e1_asynchronous_field_runtime.py
```

Beide Module bleiben privat. Es gibt keine Exporte aus `__init__.py` oder
`current_api.py`. Der bestehende neutrale AV-Pfad wurde nicht veraendert.

## Transienter E1/S/H-Schritt

`advance_e1_coupled_fast_shared_field_transient(...)` verarbeitet genau die
vorhandenen `TransientNeuronInputSet`-Ereignisse. Kontaktabschluesse werden
nach `completion_tick` gruppiert. Fuer jedes positive Teilintervall wird E1
symmetrisch vor und nach der S/H-Entwicklung fortgeschrieben. Gleichzeitige
Audio- und Videoabschluesse werden gemeinsam angewendet.

Das Ergebnis fuehrt fuer jedes positive Teilintervall den tatsaechlich
angewendeten E1-Adapter und dessen Endtick. Dadurch wird nicht nur ein
einzelner Endadapter stellvertretend fuer den gesamten asynchronen Verlauf
ausgegeben.

## Asynchroner Kompositor

`run_e1_asynchronous_field(...)` verwendet unveraendert:

```text
handoff_receptor_completion_groups
-> map_proposal_batch_to_transient_docks
-> project_transient_docks_to_neuron_inputs
-> transienter E1/S/H-Schritt
```

Eindeutige Source-Supports, Handoff, Batchreihenfolge und die genau einmalige
Ereigniszuordnung bleiben Pflichtgrenzen. Feld und E1-Zustand werden als
getrennte private Rollen ausgegeben. E1 wird nicht in den neutralen Snapshot
geschrieben.

## P0, A0 und A1

### A0

Bei deaktivierter Rueckwirkung delegiert die Feldentwicklung vollstaendig an
`advance_neutral_fast_shared_field_transient(...)`. Dessen abgeschlossene
Ereignisgrenzen werden nur fuer die getrennte E1-Entwicklung beobachtet.
Damit ist das A0-S/H-Feld bitgenau P0, obwohl sich der private E1-Zustand
entwickeln kann.

### A1

Bei aktiver Rueckwirkung wird pro positivem Ereignisintervall der vorhandene
E1-Kantenadapter gebildet. Er gewichtet ausschliesslich interne bestehende
Feldkanten. Punktkontakte, Rezeptorwerte, Docks und Abschlusszeiten bleiben
unveraendert.

### Nullgain

Auch ein aktiv aufgerufener Arm mit `backreaction_gain=0` delegiert die
Feldentwicklung an den neutralen Pfad. A1 ist in diesem Fall bitgenau A0;
der angewendete Adapter bleibt dennoch als aktiv markierter Nullgainarm
nachvollziehbar.

## Technische Abnahme

Sieben fokussierte S1-DB-Tests bestehen:

1. A0-S/H ist bitgenau P0, waehrend E1 sich getrennt entwickelt.
2. A1 veraendert die spaetere Feldlage gegen A0 technisch.
3. Freie und gebundene lokale E1-Ressource bleiben bilanziert.
4. Nullgain-A1 ist bitgenau A0.
5. Alle fuenf synthetischen AV-Source-Supports werden genau einmal
   verarbeitet.
6. Die Intervallenden `2, 4, 5, 9, 12` bleiben vollstaendig erhalten.
7. Gleichzeitige Audio-/Videoabschluesse sind gegen
   Deklarationsreihenfolge invariant.
8. Ungueltige Schalter und Ereignisse ausserhalb des Horizonts brechen ab.
9. Die neuen Rollen bleiben aus Paket- und `current_api` ausgeschlossen.

Der relevante Verbund besteht mit:

```text
50 Tests: E1, gewichteter Adapter, synchrone und transiente Kopplung,
          neutral-asynchroner Feldpfad und schneller Nachhall
26 Tests: AV-Runtime, kontrollierte AV-Testwelt, Current-API-Consumer und
          aktive Feldzustandsgrenze
76 relevante Tests insgesamt
```

`pytest` war in der verwendeten Python-Installation nicht vorhanden. Die
Abnahme erfolgte deshalb ueber den im Projekt vorhandenen
`python -m unittest`-Pfad.

## Begrenzter Befund

```text
E1_TRANSIENT_AV_INTEGRATION_READY
```

Dieser Befund bedeutet ausschliesslich:

- E1 kann auf derselben technischen Zeitordnung wie kontrollierte Audio- und
  Video-Rezeptorereignisse mitgefuehrt werden;
- Ablation bleibt bitgenau gegen den neutralen Feldpfad kontrollierbar;
- aktive E1-Rueckwirkung ist auf der transienten Feldstrecke technisch
  vorhanden;
- lokale E1-Ressourcenbilanz und private API-Grenze bleiben erhalten.

## Aussagegrenze

S1-DB belegt keine Einpraegung, kein Vergessen, keine Rekonstruktion, kein
MCM-Memory, keinen inneren Kontext, keine Semantik, keine Organisation,
keine Topologie, keine Selbstregulation und keine KI. Die aktive Abweichung
ist aufgrund der implementierten E1-Gleichung zu erwarten und allein kein
Forschungsdurchbruch.

## Bester naechster Schritt

S1-DC bindet vor jeder weiteren Ausfuehrung einen kleinen zweiphasigen
AV-Pruefvertrag: kontrollierter Weltkontakt, anschliessende angeglichene
S/H-Probegrenze und identische spaetere AV-Probe. P0, A0, A1 und ein aus dem
vorab gebundenen E1-Zustand eingefrorener F0-Adapter bleiben Pflichtarme.
Zuerst nur statisch; noch kein Browser- oder Forschungsrunner.
