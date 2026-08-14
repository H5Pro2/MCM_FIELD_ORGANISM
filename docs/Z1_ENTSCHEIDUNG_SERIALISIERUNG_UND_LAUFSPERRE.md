# Z1: Entscheidung, Serialisierung und Lauf-195-Sperre

Stand: 2026-08-06

## Status

Die reine Z1-Entscheidungslogik, die JSON-Projektion und der einmalige
Lauf-195-Einstieg wurden vor der Ausfuehrung implementiert und ausschliesslich
mit synthetischen Paketen getestet. Der reale one-shot Lauf ist inzwischen
[`TECHNICALLY_UNDECIDABLE`](forschung/LAUF_195_Z1_FELDTRAJEKTORIEN_KOVARIANZAUDIT.md)
abgeschlossen; das Ergebnis liegt in
`reports/mcm_f3_z1_lauf_195.json`.

## Festgelegte Auswertungsreihenfolge

1. Alle technischen Paketkontrollen muessen bestehen.
2. Fuer jeden Mechanismus und Arm werden n-zu-2n-, 2n-zu-4n-Abstand und
   numerische Huelle getrennt fuer S, H und M berechnet.
3. Bei Armvergleichen gilt komponentenweise das Maximum der numerischen
   Huellen von Referenz und Vergleichsarm.
4. Scheitert `A.partitioned`, bleibt das Modell
   `TECHNICALLY_UNDECIDABLE`; Zeit- und Ordnungsentscheidungen werden nicht
   freigegeben.
5. Dehnung und Kompression entscheiden gemeinsam zwischen
   `TIME_REPARAMETERIZATION_COVARIANT` und
   `WORLD_TIME_BOUND_FIELD_PATH`.
6. Umkehrung, Blockpermutation und unabhaengige Quelle muessen jeweils die
   vorregistrierte Ordnungsgrenze ueberschreiten, bevor
   `ORDER_SENSITIVE_FIELD_PATH` gilt.
7. F3 und B3 werden mit derselben Logik getrennt klassifiziert.
8. B3 erklaert F3 in Z1 nur, wenn beide Klassifikationen uebereinstimmen und
   alle sieben vollstaendigen 4n-Pfade komponentenweise innerhalb 5 Prozent
   liegen.

## Fehler- und Stopplogik

Fehlgeschlagene Reproduktion, Handoff-, Massen-, Werte- oder
Konvergenzkontrollen ergeben unmittelbar `TECHNICALLY_UNDECIDABLE`. Dasselbe
gilt, wenn eine Komponente keine messbare Pfadlaenge besitzt oder die feste
Pfadmetrik nicht berechnet werden kann.

Ein technisch unentscheidbares Ergebnis wird nicht nachtraeglich durch eine
andere Metrik, Toleranz oder Teilmenge gerettet.

## Ergebnisprojektion

`mcm_field_organism/mcm_f3_z1_evaluation.py` gibt nur skalare Distanzen,
Huellen, Klassifikationen, Kontrollen und die B3-Einordnung aus. Vollstaendige
S/H/M-Trajektorien werden nicht in das Ergebnis-JSON uebernommen.

Das Schema lautet:

```text
mcm.f3.z1.run.v1
```

Alle Memory-, Organisations-, Topologie-, Semantik- und KI-Claimflags bleiben
fest `false`.

## Einmaliger Laufweg

`mcm_field_organism/mcm_f3_z1_run.py` verbindet genau einmal:

```text
reale technische Vollmatrix
-> unveraenderte reine Z1-Auswertung
-> Lauf-ID lauf-195
-> JSON-Projektion ohne Rohtrajektorien
```

`tools/run_mcm_f3_z1.py` schreibt ausschliesslich
`reports/mcm_f3_z1_lauf_195.json` und bricht ab, falls diese Datei bereits
existiert.

## Technische Pruefung

Synthetisch bestaetigt sind:

- kovariante identische Pfadgeometrie bei anderen Ticks;
- getrennte B3-Erklaerung;
- unmittelbarer Stopp bei fehlgeschlagener Paketkontrolle;
- unmittelbare Unentscheidbarkeit bei verletzter Teilungsinvarianz;
- endliches JSON ohne Rohtrajektorien;
- feste Lauf-ID und festes Ergebnisschema;
- kein Aufruf der realen Vollmatrix in Tests.

Insgesamt bestehen 44 fokussierte Z1/F3-Tests.

## Aussagegrenze

Die fertige Auswertung war vor ihrem realen Aufruf noch kein
Forschungsergebnis. Lauf 195 hat inzwischen ausschliesslich technische
Unentscheidbarkeit ergeben. Insbesondere sind weder relative Feldzeit noch
Memory, Organisation, Topologie, Semantik, Selbstregulation oder KI
nachgewiesen.

## Bester naechster Schritt

Den unveraenderten one-shot Einstieg `tools/run_mcm_f3_z1.py` genau einmal
ausfuehren. Ein technischer Abbruch wird als solcher dokumentiert und nur mit
eng begrenztem Korrekturvertrag fortgesetzt; ein erfolgreicher Lauf wird ohne
Schwellen- oder Metrikaenderung als Lauf 195 ausgewertet.
