# W7-BH: Vertrag fuer CONST-V-AB/BA-R2 und rohe D12-Vorbereitung

## Zweck

W7-BH registriert die naechste Aufloesungsstufe fuer beide bereits technisch
gebundenen Richtungen. Zuerst werden AB und BA bei R2 exakt wiederholt. Nur
nach bestandener Wiederholung darf eine rohe D12-Datenstruktur aus R1 und R2
vorbereitet werden.

## Gebundene Grundlage

- W7-BF-Digest: `e7d819ad...40d0`
- W7-BG-Digest: `3d2abeda...1927`
- W7-BD-Adapterdigest: `496a7955...58db`
- W7-Y-Plan: `c771a3c...5b32`
- Modell: `const-v`
- Aufloesung: R2

Die Rollen bleiben `AB` und `BA`. Jede Rolle besitzt fuenf
Hauptproduktionen, fuenf isolierte Checkpointproben und je 91 erwartete rohe
S/H/Skalar-Samples pro Probe. Die Checkpointregel bleibt unveraendert:
Tiefenkopie, `S=H=0`, technischer Skalar erhalten, keine Rueckkehr in die
Hauptkette.

## Wiederholungsgrenze

Die AB/R2-Wiederholung muss die R1-konsistenten Struktur- und Diagnosesurfaces
exakt reproduzieren. Bei Abweichung endet der Vorgang vor BA/R2.

## D12-Grenze

Nach erfolgreicher R2-Wiederholung darf fuer dieselbe Rolle die rohe R1/R2-
Trajektorienstruktur vorbereitet werden. Die Struktur wird nicht bewertet:
keine Distanzzahl, kein Epsilon, kein Effektboden und kein Profilvergleich.
Eine Konvergenzentscheidung bleibt bis R4 gesperrt.

## Naechster Anschluss

W7-BI implementiert den privaten AB/BA-R2-Executor und die wertfreie rohe
D12-Vorbereitung. W7-BI ist mit terminalem D12-Digest
`b4daf8e5...cbf77` technisch abgeschlossen. W7-BJ folgt als R4-Vertrag.
