# W1-R: Synthetische Feldbelastungs- und Erholungscharakterisierung

Stand: 2026-08-08

Entscheidung: `W1R_NORMALIZED_BOUNDARY_NOT_REACHED_IN_BOUND_MATRIX`

Forschungslauf: nein

Realer Browser gestartet: nein

Adaptive Regulation implementiert: nein

## Auftrag

W1-R charakterisiert das unveraenderte gemeinsame audiovisuelle Feld unter
kontrollierten synthetischen Belastungs- und Nullkontaktfenstern. Es wird
keine Empfindlichkeit veraendert, kein Gain zurueckgeschrieben und kein
Regulationskandidat freigegeben.

Die historische `sensory_load_recovery_null_probe` untersucht nur stateless
Rezeptoren. W1-R verwendet stattdessen das heutige neutrale gemeinsame Feld
mit derselben Grundgeometrie wie der aktuelle AV-Pfad:

```text
8 auditive Traeger
18 visuelle Traeger
26 gemeinsame Feldneuronen
orthogonale lokale Nachbarschaft
```

## Gebundene Matrix

Vier getrennte Runtimepfade:

```text
unmodified
fixed_gain_0_5
static_clip_0_5
fixed_leaky_1_0
```

Kontrollachsen:

```text
Eingangsstaerke:     0.25, 0.5, 1.0
Belastungsdauer:     0.1 s, 1.0 s, 4.0 s
Nullkontaktfenster:  0.0 s, 0.1 s, 1.0 s, 4.0 s
```

Das ergibt 144 getrennte Beobachtungen. Jede Beobachtung beginnt mit einem
frischen Feld. Der Maximalwert wird nicht ueber einen nachtraeglichen
Saettigungsschwellwert klassifiziert. Gemessen wird der direkte Abstand zur
normierten Feldgrenze:

```text
normalized_boundary_distance = 1 - activation_linf
```

Nur ein exakter Wert von `1.0` gilt als erreichte normierte Grenze.

## Unveraenderter Feldpfad

Die Linf-Belastungsantwort steigt monoton mit Eingangsstaerke und Dauer:

| Staerke | 0.1 s | 1.0 s | 4.0 s |
|---:|---:|---:|---:|
| 0.25 | 0.02379064549101016 | 0.15803013970713972 | 0.2454210902778169 |
| 0.5 | 0.04758129098202032 | 0.31606027941427944 | 0.4908421805556338 |
| 1.0 | 0.09516258196404064 | 0.6321205588285589 | 0.9816843611112676 |

Der kleinste beobachtete Abstand zur normierten Grenze ist:

```text
0.018315638888732444
```

Die normierte Grenze wurde in der gebundenen Matrix nicht erreicht oder
ueberschritten.

## Erholung bei gemessenem Nullkontakt

Die Aktivierung nimmt fuer jede Staerke und Belastungsdauer monoton mit der
Dauer des Nullkontaktfensters ab. Nach 4.0 Sekunden verbleibt im
unveraenderten Pfad jeweils der Anteil:

```text
recovery_fraction_linf = 0.018315638888735...
```

Beim staerksten und laengsten Belastungsarm sinkt Linf von
`0.9816843611112676` auf `0.017980176260833026`.

Das ist die vorhandene feste Feldkinetik mit Antwortzeit 1.0 s. Es ist keine
adaptive, geschichtsabhaengige oder organismische Selbstregulation.

## Feste Gegenbaselines

Beim Arm Staerke 1.0 und Belastungsdauer 4.0 s ergeben sich:

| Pfad | angewandte Staerke | Belastungs-Linf | Grenzabstand |
|---|---:|---:|---:|
| unmodified | 1.0 | 0.9816843611112676 | 0.018315638888732444 |
| fixed_gain_0_5 | 0.5 | 0.4908421805556338 | 0.5091578194443662 |
| static_clip_0_5 | 0.5 | 0.4908421805556338 | 0.5091578194443662 |
| fixed_leaky_1_0 | 1.0 | 0.49983226868604974 | 0.5001677313139503 |

Diese Pfade sind technische Gegenbaselines. Sie sind keine Kandidaten fuer
organische Regulation. Insbesondere gibt es keinen AGC-, Sollwert- oder
globalen Controllerpfad.

## Abnahme

Der fokussierte Verbund besteht mit `43 passed` und 26 Subtests. Geprueft
sind Matrixvollstaendigkeit, monotone Belastung, monotone Erholung,
Baselineidentitaet, 26-Neuronen-Geometrie, fehlende Rueckschreibung,
unveraenderter E0-Regulationsvertrag sowie die neutrale und asynchrone
Feldintegration.

## Aussagegrenze

W1-R zeigt in der gebundenen verteilten Matrix keine Grenzueberschreitung.
Das widerlegt keine Ueberlastung in anderen lokalen, multimodalen oder
laengeren Weltgeschichten. Der kleinste Grenzabstand zeigt vielmehr, dass
starke lange Belastung den normierten Rand deutlich annaehert.

W1-R belegt keine Selbstregulation, Wahrnehmung, Feldzeit, Praegung, Memory,
Organisation, Semantik oder KI. Aus der vorhandenen festen Erholung darf
kein organisches Vergessen abgeleitet werden.

## Bester naechster Schritt

W1-S trennt unter Fakes vier raeumliche Belastungsformen: lokal auditiv,
auditiv modalitaetsweit, lokal visuell und vollstaendig audiovisuell
verteilt. Gemessen werden lokale und fernliegende Maxima, modalitaetsfremde
Ausbreitung, Grenzabstand und Erholung. Erst wenn daraus ein lokales
Belastungsproblem hervorgeht, darf ein spaeterer Regulationskandidat
begruendet werden.
