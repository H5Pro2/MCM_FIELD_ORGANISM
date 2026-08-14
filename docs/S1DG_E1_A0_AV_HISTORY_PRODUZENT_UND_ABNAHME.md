# S1-DG: E1-A0-AV-History-Produzent und Abnahme

## Status

Der in S1-DF gebundene private History-Produzent ist implementiert und mit
kleinen synthetischen In-Memory-Sequenzen abgenommen. Die kanonischen
S1-DE-Historien wurden nicht durch E1 ausgefuehrt. Es gab keinen Browserstart,
keine Probe und keinen Forschungsrunner.

## Implementierung

```text
mcm_field_organism/e1_a0_av_history_producer.py
tests/test_e1_a0_av_history_producer.py
```

Das Modul bleibt privat und ist weder aus `__init__.py` noch aus
`current_api.py` exportiert.

## Zwei Ausfuehrungsgrenzen

Der Produzent besitzt einen kleinen privaten Kern fuer bereits vorgepruefte
AB-/BA-Sequenzen und einen kanonischen Einstieg fuer S1-DE.

Der Kern erzeugt intern vier vollstaendig getrennte Arme:

```text
AB-P0  AB-A0  BA-P0  BA-A0
```

Alle vier Felder werden vor der Ausfuehrung als objektgetrennte Kopien eines
frischen Feldes erzeugt. Beide A0-Arme erhalten getrennte Kopien eines
neutralen E1-Zustands. E1-Rueckwirkung ist fest deaktiviert.

Der kanonische Einstieg akzeptiert ausschliesslich die drei in S1-DE
gebundenen Digests, 200 auditive und 20 visuelle Frames, 12 auditive und 72
visuelle Carrier sowie die daraus gebaute 84-Knoten-Geometrie. Laufhorizont,
S/H-Konfiguration und E1-Vertrag sind nicht parametrierbar.

## Frischfelddigest statt Runtime-Snapshot

Die erste synthetische Abnahme hat eine bestehende korrekte API-Grenze
sichtbar gemacht: `SharedMCMField.snapshot()` ist erst nach einem
abgeschlossenen Rezeptorkontakt zulaessig. Ein frisch gebautes Feld besitzt
noch keinen abgeschlossenen rezeptorgetriebenen Zustand.

S1-DG bindet die vier Startfelder deshalb mit einem expliziten strukturellen
Frischfelddigest aus Layerdigest, Dockinventar, leerer
`last_distribution` sowie fehlendem M- und L-Zustand. Endfelder werden
weiterhin ueber den vorhandenen Runtime-Snapshot verglichen. Die
Snapshot-Semantik wurde nicht aufgeweicht.

## Ausgabegrenze

Nach vollstaendiger interner Validierung verlassen nur folgende Rollen den
Produzenten:

- `b_ab` und `b_ba` als objektgetrennte E1-Endzustaende;
- unveraenderte S1-DE-Quell- und Permutationsdigests;
- Geometrie- und Frischfelddigest;
- paarweise P0-/A0-Endfelddigests;
- Handoff-, Ereignis- und Ressourcenaudits;
- ein Produktionsdigest.

Historische Feldobjekte, letzte Rezeptorverteilungen, Restore-Snapshots,
Adapter und Probeobjekte sind nicht Teil des Ergebniscontainers.

## Synthetische Abnahme

Sieben fokussierte Tests bestaetigen:

1. AB-A0 ist bitgenau AB-P0 und BA-A0 bitgenau BA-P0.
2. Je synthetischem Arm werden alle vier Source-Supports genau einmal
   verarbeitet.
3. Beide E1-Endzustaende bleiben objektgetrennt.
4. Historische Feld- und Proberollen fehlen im Ergebniscontainer.
5. Initialfeld und neutraler E1-Start bleiben unveraendert.
6. Nichtneutraler E1-Start und geaenderte H-Konfiguration brechen ab.
7. Wiederholte synthetische Produktion ist digest- und zustandsidentisch.
8. Der kanonische Einstieg baut 84 Knoten und uebergibt nur die fest
   gebundene Laufkonfiguration an einen ersetzten, nicht ausgefuehrten Kern.
9. Ein geaenderter kanonischer Digest wird vor einer Ausfuehrung abgewiesen.
10. Paket- und `current_api`-Grenze bleiben geschlossen.

Der fokussierte Lauf besteht mit:

```text
7 tests
OK
```

Der relevante AV-/E1-Verbund besteht mit:

```text
114 tests
OK
```

## Begrenzter Befund

```text
E1_A0_AV_HISTORY_PRODUCER_READY
```

Dieser Befund bedeutet nur, dass der private Produzent technisch bereit ist
und seine Kontrollgrenzen in kleinen synthetischen Laeufen bestehen.

## Aussagegrenze

Die kanonischen E1-Endzustaende `b_AB` und `b_BA` existieren noch nicht. Es
gibt deshalb keinen Befund ueber eine AB-/BA-Zustandsdifferenz und keinen
AV-history-spezifischen E1-Effekt. S1-DG belegt weder Einpraegung, Vergessen,
Rekonstruktion, MCM-Memory, inneren Kontext, Semantik, Organisation,
Topologie, Selbstregulation noch KI.

## Bester naechster Schritt

S1-DH registriert statisch genau eine kanonische AB/BA-History-Produktion.
Vorab werden Quell-, Implementierungs- und Konfigurationsdigests, ein neues
noch nicht vorhandenes Ergebnisziel, die erlaubten Rohmetriken `D_state` und
`D_total_binding`, Abbruchnachweis und Wiederholungsverbot gebunden. S1-DH
fuehrt den Produzenten noch nicht aus und bildet keine Probe.

S1-DH ist inzwischen statisch registriert und mit 8 fokussierten sowie 122
relevanten `unittest`-Tests abgenommen. Kein Zielpfad wurde angelegt und der
Produzent wurde nicht aufgerufen. Siehe
`S1DH_E1_A0_AV_HISTORY_STATISCHER_EINMALLAUFVERTRAG.md`.
