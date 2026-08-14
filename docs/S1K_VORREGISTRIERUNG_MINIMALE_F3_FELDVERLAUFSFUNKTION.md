# S1-K: Vorregistrierung minimale F3-Feldverlaufsfunktion

Stand: 2026-08-09

Vertragsstatus: `PREREGISTERED_NOT_IMPLEMENTED_NOT_EXECUTED`

Runtimeaenderung: nein

Forschungslauf: nein

## Forschungsfrage

Traegt die unveraenderte F3-Referenz auf der aktuellen gemeinsamen
26-Neuronen-AV-Geometrie nach zwei kontrollierten, massen- und
amplitudenangeglichenen Feldkontaktverlaeufen eine reproduzierbare
unterschiedliche Wirkung auf denselben spaeteren AV-Kontakt, wenn S und H vor
diesem Kontakt exakt angeglichen werden?

Zusaetzlich wird getrennt gefragt:

1. Wird die spaetere Wirkung durch die lineare gekoppelte F3-Baseline
   technisch erklaert?
2. Verschwindet sie nach externer uniformer M-Neutralisierung?
3. Kann nach dieser technischen Neutralisierung derselbe M-Zustandsraum einen
   neuen kontrollierten Verlauf wieder tragen?

Die Frage betrifft nur eine transparente Feldverlaufsfunktion. Sie setzt
kein Lernen, Memory, Vergessen oder innere Wahrnehmung voraus.

## Abgrenzung zum historischen Zweig

S1-K wiederholt Lauf 189, 192 oder 194 nicht. Insbesondere wird nicht erneut
geprueft, ob weitere normale B-Weltgeschichte eine alte A-Wirkung
konkurrierend verdraengt. Lauf 194 bleibt als Befund passiver Abnahme und
Wiederverwendung unveraendert geschlossen.

Der neue Vertrag unterscheidet sich durch:

- die aktuelle synthetische 8+18-AV-Geometrie aus S1-J;
- zwei neue ortsverschobene, aber wertemultimengleiche Kontaktverlaeufe;
- eine einmalige gemeinsame spaetere Probe nach exakter S/H-Angleichung;
- P0 und `eta=0` als exakte Wirkungsnullkontrollen;
- uniforme M-Neutralisierung nur als externe Kausalkontrolle;
- eine Engineeringklassifikation, nicht die Suche nach irreduzibler Physik.

Die Zweige 213ZZR bis 213ZZU, Z4 und Lauf 197 bleiben unberuehrt.

## Unveraenderte technische Mechanik

```text
Feldneuronen:                  26
auditive Feldneuronen:          8
visuelle Feldneuronen:         18
response_time_seconds:        1.0
afterimage_time_constant:     0.5
lambda_sm_per_second:         1.0
kappa:                        0.5
eta aktiver Arm:              1.0
initial_total_mass:           1.0
dissipation:                  keine
Integrationsverfeinerungen:   1, 2, 4
```

F3-Gleichung, lineare Baseline, Feldgeometrie und Rezeptorprojektion werden
nicht veraendert. Es gibt keine adaptive Kante, keine variable Topologie,
keinen Gainregler und keinen Ergebnisrueckkanal.

## Kontrollierte Quellen

Alle Quellen werden erst in S1-L aus der bestehenden synthetischen AV-Fixture
erzeugt. Ein Support dauert 0.1 Sekunden. Die Quellen enthalten keine
Objektklasse oder Bedeutung.

### Verlauf A

Vier gleiche Supports:

```text
auditory[0] = 0.8
visual[5]   = 0.6
alle anderen Werte = 0.0
```

### Verlauf B

Vier gleiche Supports mit derselben Wertemultimenge an anderen Feldorten:

```text
auditory[7] = 0.8
visual[12]  = 0.6
alle anderen Werte = 0.0
```

A und B besitzen damit exakt gleiche Dauer, Ereigniszahl, Wertemultimenge,
L1-Amplitude und L2-Amplitude. Nur die raeumliche Zuordnung im bestehenden
Feld unterscheidet sich.

### Nullkontakt und gemeinsame Probe P

Nach A oder B folgen zwei Nullsupports. Danach werden S und H extern exakt
auf denselben Nullzustand angeglichen, ohne M zu veraendern.

Die gemeinsame Probe besitzt einen Kontakt- und einen Nullsupport:

```text
auditory[3] = 0.4
visual[8]   = 0.4
alle anderen Werte = 0.0
```

Die Probe ist fuer alle Verlaufs- und Modellarme bitgleich. Sie ist nur eine
technische spaetere Eingabe, kein Abfrage-, Lese- oder Erinnerungsbefehl.

## Zeitrollen

```text
0.0 .. 0.4 s   Verlauf A oder B
0.4 .. 0.6 s   Nullkontakt
bei 0.6 s      externe exakte S/H-Angleichung
0.6 .. 0.7 s   identischer Probe-P-Kontakt
0.7 .. 0.8 s   identischer Nullsupport
```

M wird auf den Hauptarmen weder an der Angleichungsgrenze noch waehrend P
zurueckgesetzt. Alle Messungen erfolgen passiv nach abgeschlossenen
Ereignis- oder Feldgrenzen.

## Modell- und Kontrollarme

Jeder A/B-Pfad wird mit identischem Quellen-, Zustands-, Geometrie- und
Zeitbudget ausgefuehrt:

| Modellarm | M-Dynamik | Rueckwirkung auf S | Rolle |
|---|---|---|---|
| F3 | unveraendert | `eta=1` | technische Feldverlaufs-Referenz |
| lineare gekoppelte Baseline | feste lineare Form | `eta=1` | engste Mechanikbaseline |
| `eta=0` | unveraenderte F3-M-Dynamik | keine | exakte Leserablation |
| P0 | keine M-Dynamik | keine | exakter Fast-Field-Nullarm |
| F3 M-neutral | M nach A/B extern uniformisiert | `eta=1` | kausale M-Neutralisierung |

Die uniforme M-Neutralisierung ist keine Organismusfunktion und kein
natuerliches Vergessen. Sie ist eine einmalige externe Intervention in einer
getrennten Kontrollkopie.

## Messrollen

An jeder Beobachtungsgrenze von Probe P werden nur fluechtige technische
Vektoren fuer S, H und M verglichen. Rohbild- oder Audiodaten werden nicht im
Ergebnis gehalten.

Fuer Modell `X` und Beobachtungsgrenze `t` gilt:

```text
E_X(t) = max(
  Linf(S_X,A(t) - S_X,B(t)),
  Linf(H_X,A(t) - H_X,B(t))
)
```

Gebundene Messungen:

- maximales `E_X` ueber Probe P;
- M-Linf zwischen A und B unmittelbar vor P;
- maximale Massenbilanzabweichung von 1.0;
- minimale lokale M-Masse;
- F3-Effektvektor gegen den Effektvektor der linearen Baseline;
- Verfeinerungsabweichung 2 gegen 4;
- exakte Wiederholung derselben technischen Komposition;
- Neutralisierungseffekt;
- erneute Bindbarkeit nach technischer Neutralisierung.

Der relative lineare Baselinefehler ist:

```text
R_linear = Linf(effect_F3 - effect_linear)
           / max(Linf(effect_F3), detection_floor)
```

## Numerische und kausale Pflichtkontrollen

Der Nachweisboden wird nicht aus einem positiven Ergebnis nachtraeglich
gewaehlt:

```text
absolute_floor = 1e-12
convergence_floor = 8 * Linf(effect_refinement_4 - effect_refinement_2)
detection_floor = max(absolute_floor, convergence_floor)
linear_equivalence_limit = 0.05
mass_tolerance = 1e-12
```

Pflichtkontrollen:

1. A und B besitzen die vorregistrierten gleichen Marginalinvarianten.
2. S und H sind vor P exakt gleich.
3. P0-A und P0-B bleiben waehrend P exakt gleich.
4. `eta=0`-A und `eta=0`-B bleiben in S und H waehrend P exakt gleich, auch
   wenn ihre M-Zustaende verschieden sind.
5. Nach uniformer M-Neutralisierung bleiben F3-A und F3-B waehrend P exakt
   gleich.
6. Gesamtmasse bleibt innerhalb `1e-12` bei 1.0 und alle M-Werte bleiben
   nichtnegativ.
7. Wiederholte technische Ausfuehrungen liefern dieselben skalaren Werte und
   Zustandsdigests.
8. Kein Observerwert steuert Quelle, Angleichung, Arm oder Runtime.

Verletzt ein Pflichtpunkt die Grenze, ist die gesamte Funktionsentscheidung
`TECHNICALLY_INVALID`.

## Erneute Bindbarkeit

In einer getrennten Kontrollkopie wird nach Verlauf A:

1. S/H exakt angeglichen;
2. M extern uniformisiert;
3. Verlauf B mit denselben vier Supports neu zugefuehrt;
4. erneut S/H angeglichen;
5. Probe P zugefuehrt.

Der resultierende technische B-Effekt wird mit einem frischen, zeitlich
gleich gebundenen B-Referenzpfad verglichen. Gleichheit innerhalb des
Verfeinerungsbodens bedeutet nur `TECHNICAL_REBINDABILITY_CONFIRMED`.
Abweichung bedeutet `REBINDABILITY_NOT_CONFIRMED`.

Diese Kontrolle belegt keine natuerliche Loesung, kein Vergessen und keine
Wiederpraegung, weil die uniforme Neutralisierung extern vorgenommen wird.

## Vorregistrierte Entscheidungen

Nach bestandenen Pflichtkontrollen wird genau eine Hauptentscheidung
ausgegeben:

1. `NO_TECHNICAL_HISTORY_EFFECT`, wenn der maximale F3-Effekt den
   `detection_floor` nicht ueberschreitet.
2. `TRANSPARENT_HISTORY_EFFECT_LINEARLY_EXPLAINED`, wenn ein F3-Effekt ueber
   dem Nachweisboden besteht und `R_linear <= 0.05` gilt.
3. `TRANSPARENT_HISTORY_EFFECT_BASELINE_DIFFERENT`, wenn ein F3-Effekt ueber
   dem Nachweisboden besteht und `R_linear > 0.05` gilt.
4. `TECHNICALLY_INVALID`, sobald eine Quellen-, Kausal-, Null-, Massen-,
   Wiederholungs- oder Konvergenzkontrolle verletzt ist.

Neutralisierung und erneute Bindbarkeit werden daneben getrennt als
`CONFIRMED` oder `NOT_CONFIRMED` ausgewiesen. Sie veraendern die
Hauptentscheidung nicht und duerfen nicht zu einem Memoryclaim
zusammengezogen werden.

`TRANSPARENT_HISTORY_EFFECT_BASELINE_DIFFERENT` waere insbesondere kein
Nachweis neuer Physik. Dafuer waeren unabhaengige Replikation, weitere enge
Baselines und eine eigene neue Naturursache erforderlich.

## Aussagegrenze

S1-K ist nur eine Vorregistrierung. Es wurde nichts implementiert und nichts
ausgefuehrt. Kein moeglicher Ausgang dieses Vertrags belegt:

- Lernen, Praegung, Vergessen oder Rekonstruktion;
- MCM-Memory oder organisches Memory;
- relative Feldzeit oder Feldzeitverdichtung;
- inneren Kontext, Bedeutung oder Semantik;
- Organisation, Topologie oder Selbstregulation;
- feldbasierte KI oder neue Feldphysik.

Es bleiben ausschliesslich synthetische Audio-/Video-Fakes erlaubt. Browser,
Kamera, Mikrofon, reale Sensorik, Forschungsrunner, Ergebnisreport und neue
Laufnummer bleiben in S1-K gesperrt.

## Verwendete Quellen

- S1-H: Nullausgang fuer eine neue Substratnatur.
- S1-I: Trennung von Neuphysik- und Engineeringlinie.
- S1-J: technische Kompatibilitaet auf der aktuellen 26-Neuronen-Geometrie.
- Lauf 192: lineare gekoppelte F3-Baseline als enge Erklaerung.
- Lauf 194: passive Abnahme und Wiederverwendung ohne konkurrierende
  Reorganisation.
- vorhandene F3-Kopplung, transiente Runtime, S/H-Angleichung und uniforme
  M-Neutralisierung als transparente technische Bestandsfunktionen.

## Bester naechster Schritt

S1-L implementiert ausschliesslich den in-memory Pruefadapter und technische
Vertragstests fuer Quelleninvarianten, Armgleichheit, Angleichung,
Neutralisierung, Verfeinerung und passive Skalarmessung. S1-L erzeugt noch
keinen Forschungsrunner, keinen Report und keine Laufnummer.

## Spaeterer Umsetzungsstand S1-L

S1-L ist inzwischen im
[`In-Memory-F3-Feldverlaufspruefadapter`](S1L_IMPLEMENTIERUNG_IN_MEMORY_F3_FELDVERLAUFSPRUEFADAPTER.md)
umgesetzt. Quellen, Arme, Nullkontrollen, Verfeinerungen, Wiederholung und
externe Wiederbindung bestehen technisch mit `65 passed` und 24 Subtests.
Die S1-K-Hauptentscheidung wurde noch nicht berechnet. Naechster Schritt ist
der reine passive S1-M-Evaluator.

## Spaetere technische Klassifikation S1-M

Der passive S1-M-Evaluator hat alle Pflichtkontrollen bestanden. Die
vorregistrierte Klassifikation lautet
`TRANSPARENT_HISTORY_EFFECT_LINEARLY_EXPLAINED`: Der F3-Effekt liegt ueber
dem Konvergenzboden, der vollstaendige lineare Effektvektor bleibt mit
1.842 Prozent relativem Rest innerhalb der festen 5-Prozent-Grenze. Dies ist
eine technische Engineeringklassifikation ohne Memory- oder Neuphysikclaim.
