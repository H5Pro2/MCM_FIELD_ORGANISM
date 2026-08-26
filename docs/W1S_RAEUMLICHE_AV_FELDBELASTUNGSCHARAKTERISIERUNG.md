# W1-S: Raeumliche AV-Feldbelastungscharakterisierung

Stand: 2026-08-09

Entscheidung: `W1S_DISTRIBUTED_LOAD_NEAREST_BOUNDARY_LOCAL_LOAD_SPREADS`

Forschungslauf: nein

Realer Browser gestartet: nein

Adaptive Regulation implementiert: nein

## Auftrag

W1-S trennt im unveraenderten gemeinsamen 26-Neuronen-AV-Feld vier
raeumliche Belastungsformen:

```text
local_auditory       1 auditiver Kontakt
auditory_modality    8 auditive Kontakte
local_visual         1 visueller Kontakt
distributed_av      26 auditive und visuelle Kontakte
```

Alle aktiven Kontakte besitzen den Wert `1.0`. Belastungsdauern sind 0.1,
1.0 und 4.0 s; Nullkontaktfenster sind 0.0, 1.0 und 4.0 s. Jeder der 36 Arme
beginnt mit einem frischen Feld.

## Kontinuierliche Kontaktfolge

Eine einzelne Kontaktunterstuetzung mit Abschluss nur am Fensterende laesst
vor dem Snapshot keine Zeit fuer raeumliche Feldentwicklung. Ein erster
interner Check zeigte ausserhalb des Kontakts deshalb nur numerisches Rauschen
um `1e-15`; dies wurde nicht als Ausbreitung gewertet.

Die gebundene W1-S-Matrix verwendet stattdessen feste 100-ms-Unterstuetzungen.
Zwischen den Kontaktabschluessen entwickelt sich dasselbe lokale Feld weiter.
Es gibt keine Interpolation, Wiederholungsschleife ausserhalb der festen
Matrix oder nachtraegliche Schwellenwahl.

## Vier-Sekunden-Belastung

| Muster | Linf | Grenzabstand | nicht stimuliert Linf | modalitaetsfremd Linf |
|---|---:|---:|---:|---:|
| local_auditory | 0.35727128118469537 | 0.6427287188153046 | 0.09450233518074544 | 0.0842662667771055 |
| auditory_modality | 0.6377225422942969 | 0.3622774577057031 | 0.23099474073429827 | 0.23099474073429827 |
| local_visual | 0.30478396088127424 | 0.6952160391187258 | 0.08426626677710541 | 0.08426626677710541 |
| distributed_av | 0.9816843611112727 | 0.018315638888727337 | 0.0 | nicht getrennt |

Lokale Kontakte bleiben am direkt stimulierten Neuron am staerksten. Die
vorhandene lokale Feldnachbarschaft traegt jedoch einen Teil der Wirkung in
nicht stimulierte und modalitaetsfremde Feldbereiche.

Bei lokaler auditiver Belastung betraegt die modalitaetsfremde Linf-Wirkung
nach 4.0 s rund `0.2358607344471752` des globalen Maximums. Bei lokaler
visueller Belastung sind es rund `0.27647867864651365`. Diese Quotienten sind
Geometrie- und Feldwerte, keine semantische oder sensorische Zuordnung.

## Erholung

Alle vier Muster erholen sich ueber laengere Nullkontaktfenster monoton. Nach
4.0 s Nullkontakt verbleiben fuer die 4.0-s-Belastungen:

| Muster | Erholungs-Linf | Anteil am Belastungsmaximum |
|---|---:|---:|
| local_auditory | 0.000842695549381124 | 0.002358699379885178 |
| auditory_modality | 0.0060523770315332355 | 0.009490611716121802 |
| local_visual | 0.000827767277020551 | 0.002715914822509312 |
| distributed_av | 0.017980176260831926 | 0.018315638888734314 |

Dies bleibt die feste Feldkinetik und keine adaptive Erholung.

## Methodische Grenze

`distributed_av` liegt der normierten Grenze am naechsten, besitzt aber auch
26 aktive Kontakte. `local_auditory` und `local_visual` besitzen jeweils nur
einen, `auditory_modality` acht. W1-S gleicht die gesamte Kontaktmasse daher
nicht an.

Aus dem staerkeren verteilten Arm darf noch nicht gefolgert werden, dass das
Feld eine globale oder multimodale Ueberlastung besitzt. Der Unterschied kann
vollstaendig durch die unterschiedliche Anzahl aktiver Kontakte erklaert
werden. Ebenso begruendet W1-S weder einen lokalen noch einen
modalitaetsweiten Regler.

## Abnahme

Der fokussierte Feldverbund besteht mit `49 passed` und 26 Subtests. W1-R
bleibt nach Auslagerung der gemeinsamen synthetischen Fixture unveraendert
gruen. Geprueft sind Matrixvollstaendigkeit, Kontaktinventare, lokale
Dominanz, Ausbreitung, Grenzabstand, monotone Erholung, fehlende
Rueckschreibung und die zugrunde liegende neutrale/asynchrone Feldintegration.

## Aussagegrenze

W1-S belegt eine technische lokale Feldausbreitung in der gebundenen
Geometrie. Es belegt keine Ueberreizung, Selbstregulation, Wahrnehmung,
Feldzeit, Praegung, Memory, Organisation, Semantik oder KI.

## Bester naechster Schritt

W1-T gleicht die gesamte Kontaktmasse zwischen lokalem, modalitaetsweitem und
vollstaendig verteiltem Kontakt an. Verglichen werden ein Kontakt mit 1.0,
acht auditive Kontakte mit je 0.125, 18 visuelle Kontakte mit je `1/18` und
26 AV-Kontakte mit je `1/26`. Erst diese Gegenbaseline kann trennen, ob
Kontaktanzahl oder Feldgeometrie die Grenzannaeherung bestimmt.
