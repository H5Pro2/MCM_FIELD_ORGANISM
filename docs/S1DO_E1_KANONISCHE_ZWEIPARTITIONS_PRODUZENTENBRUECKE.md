# S1-DO: E1 kanonische Zwei-Partitions-Produzentenbruecke

## Status

Die kanonische Produzentenbruecke fuer den in S1-DM registrierten
Zustandstransfer ist privat implementiert und statisch abgenommen. Nur ihr
nichtausfuehrender Preflight wurde aufgerufen. Die Funktion
`produce_e1_frozen_state_transfer(...)` wurde nicht aufgerufen und alle drei
S1-DN-Projektpfade bleiben unbenutzt.

## Implementierung

```text
mcm_field_organism/e1_frozen_state_transfer_canonical_producer.py
tests/test_e1_frozen_state_transfer_canonical_producer.py
```

Produzentendigest:

```text
d6dea39041b8f2b967f81a5c5c248c05d67566256d798808ed014e7221af6f75
```

Alle Rollen bleiben privat und fehlen in Paket- und Current-API.

## Kanonischer Preflight

Der Preflight bindet ohne Feldfortschreibung:

```text
Probequellendigest  c0a9a59fb93996bdfd95247a1f6feec19723aeb36c84bd8bc8a423e677fbea7d
Geometriedigest     6cc885c3b6cb41efcdb48cea0aecb02f980f582115e505534679beb3c427b8e6
Frischfelddigest    26a53d5a379ecefb7d707df0336c0f7da1b70d0cd8484e7b6221add9a65b4ce1
Supports            110
Feldknoten          84
E1-Kanten           145
Ausfuehrungsfreigabe false
```

Die beiden veroeffentlichten E1-Zustaende werden typisiert geladen und
gegen dieselbe Feldgeometrie validiert. Die Probe besteht aus 100 auditiven
und 10 visuellen Frames des bereits in S1-DK gebundenen reduzierten
A-Blocks.

## Zwei Partitionen

Die Bruecke fuehrt bei einem spaeter freigegebenen Aufruf dieselben 110
Supports durch:

```text
coarse  (0, 1_000_000)
split   (0, 500_000, 1_000_000)
```

Alle Supports muessen pro Partition genau einmal zugeordnet sein. Beide
Partitionen verwenden dieselben Quellobjekte, Carrier, Werte und
Feldgeometrien.

## Siebenarmige Fortsetzung

Pro Partition werden sieben frische, wertidentische und objektseitig
getrennte 84-Knoten-Felder gebildet:

```text
p0, ab0, ba0, ab1, ba1, abf, baf
```

Jeder Handoff-Batch wird auf allen Armen in derselben Reihenfolge
fortgeschrieben. `b_AB` und `b_BA` bleiben exakt dieselben eingefrorenen
Objekte. Die festen Adapterarme verwenden die in demselben Batch aus dem
jeweiligen eingefrorenen Zustand berechneten Adapter.

## Metrikaggregation

Die aktive S/H-Distanz wird aus der geteilten Partition berichtet. Der
eigene Probe-Numerikrest ist der maximale S/H-Abstand jedes gleichnamigen
Arms zwischen grober und geteilter Partition. Ablations- und
Festadapterresiduen werden ueber beide Partitionen maximiert.

Der technische Status wird anschliessend vom bereits synthetisch
abgenommenen S1-DN-Ergebniscontainer validiert. Die Bruecke besitzt keine
eigene freie Interpretationsrolle.

## Technische Abnahme

```text
7 fokussierte Tests
169 relevante Verbundtests
OK
```

Geprueft sind Evidenz- und Probequellendigest, Zustands-/Geometrie-
Kompatibilitaet, Frame-, Support-, Knoten- und Kanteninventar,
Ausfuehrungssperre, exakte und zusammenhaengende Partitionen,
Statusgrenze, statische Produzentenverdrahtung und private API-Grenze.

## Aussagegrenze

S1-DO ist eine Implementierungs- und Preflightabnahme. Es existiert noch
kein kanonisches Transferergebnis. Insbesondere folgt kein Befund ueber
History-Ursache, Memory, Semantik, Organisation, Topologie,
Selbstregulation oder KI. Der volle S1-DC-Zweig bleibt gestoppt.

## Bester naechster Schritt

S1-DP bildet ein letztes statisches Freigabetor. Es bindet mindestens den
S1-DM-Vertragsdigest, den S1-DO-Produzentendigest
`d6dea390...1af6f75`, den S1-DN-Executordigest
`de9b98a1...22915d`, die unveraenderte Evidenz und die drei weiterhin
unbenutzten Projektpfade. S1-DP fuehrt Produzent und Executor noch nicht aus.

## Anschlussstatus

S1-DP hat Produzenten- und Executordigest, Evidenz und freie Projektpfade in
einem vollstaendig neu aufbaubaren finalen Gate gebunden. Produzent und
Executor blieben unaufgerufen. S1-DQ ist der naechste genau einmalige
kanonische Ausfuehrungsschritt.
