# Z1: Vorregistrierung des Feldtrajektorien-Kovarianzaudits

Stand: 2026-08-06

Status:

- statisch vorregistriert;
- Quellenarme, Digests, passiver Observer und reine Pfadmetrik technisch
  implementiert und getestet;
- gebundener F3/B3-Mehrarmrunner technisch implementiert und mit einem
  kontrollierten Ersatz-Executor geprueft;
- reine Entscheidungslogik, JSON-Projektion und one-shot Laufweg synthetisch
  geprueft;
- einmalig als Lauf 195 ausgefuehrt; Entscheidung
  `TECHNICALLY_UNDECIDABLE` wegen gescheiterter Teilungsnullkontrolle;
- keine neue Zeitvariable und kein Feldzeit-, Memory- oder KI-Claim.

## 1. Forschungsfrage

Traegt die bestehende gemeinsame MCM-Feldruntime unter kontrollierter
audiovisueller Anregung eine Feldtrajektorie, die

1. gegen rein technische Integrations- und Ereignisteilung invariant ist,
2. bei gleichfoermiger Dehnung oder Kompression der Weltzeit dieselbe
   geometrische Zustandsbahn nur anders parametrisiert durchlaeuft und
3. zugleich auf eine Aenderung der kausalen Quellenreihenfolge reagiert?

Z1 prueft nur eine beobachtbare Eigenschaft vorhandener S-, H- und
M-Trajektorien. Es prueft noch keine lokale feldinterne Zeitbildung und keine
kausale Rueckwirkung eines Zeitkontexts.

## 2. Unveraenderte Mechaniken

Verglichen werden genau zwei bereits vorhandene Mechaniken:

```text
Kandidat: bestehende aktive F3-Runtime
Baseline: lineare gekoppelte Feldform B3 aus Lauf 192

response_time_seconds:    1.0
afterimage_time_constant: 0.5
lambda_sm_per_second:     1.0
kappa:                    0.5
eta:                      1.0
refinement:               n, 2n und 4n; Hauptauswertung 4n
```

Es werden keine Parameter an die Ergebnisse angepasst. P0 darf nur als
technische Kontrolle der S/H-Grundruntime mitgefuehrt werden.

## 3. Gebundene Testwelt

Die Quelle wird aus der vorhandenen kontrollierten gemeinsamen
Audio-/Video-Welt `world.asynchronous.wav` abgeleitet:

```text
Dauer Referenz:       1.0 s
Audio:                320 Hz, Amplitude 0.25
Video:                vorhandenes festes Rechteckmuster
Audio-Ereignisrate:   100 Hz
Video-Ereignisrate:   10 Hz
Organismusclock:      eine gemeinsame feste Clock
```

Der feste Audiohop erzeugt nach dem technischen Anlauf des Spektralrezeptors
91 reduzierte Audioabschluesse; die Videoquelle erzeugt 10 reduzierte
Abschluesse. Z1 bindet diese reduzierte Ereignismenge und nicht die Zahl der
eingespeisten Rohhops.

Die Implementierung muss vor der ersten Ausfuehrung den vollstaendigen
reduzierten Referenzquellendigest und die Digests aller Transformationen
festschreiben. Eine Aenderung der Quelle nach Einsicht in Messwerte ist
untersagt.

### Festgeschriebene Quellen- und Ausfuehrungsdigests

| Arm | Sequenzdigest | Ausfuehrungsdigest | Schritte | Horizonttick |
| --- | --- | --- | ---: | ---: |
| `A.reference` | `5e0afdb8a1861edd7732cb50a5f5c66a44a4bae96a6a177f2f9b28f49e259bb8` | `23901add0b257a699b47acc9921d53c6865cbafa68fd5d583fbaa0bb033347d8` | 91 | 1000000 |
| `A.partitioned` | `5e0afdb8a1861edd7732cb50a5f5c66a44a4bae96a6a177f2f9b28f49e259bb8` | `7c1b4270b193ccebd2693f6efb808039c10fa5d5af9c4484a4b9787b1d253129` | 182 | 1000000 |
| `A.stretched` | `4e17e0ebef71eb084cdd57cc37148d6033cf1e35cae54ec52446b72d0d4c1859` | `b187ba724fa8f18617dd5ffda320c626821792410c76d3a36bd42624e278752c` | 91 | 2000000 |
| `A.compressed` | `c3bf0c167acd64ddd602937c78b8f552183d51acf6aa46c36115f46c975055e2` | `75991c488630bd5ce077b324b461deff9da2817037a962e1a402926171954a49` | 91 | 500000 |
| `A.reversed` | `6261285e07b55a2f47742d7848821e783eb46ec6b0b4be8559ed76f6873e09b0` | `808a53aa2c889262197c50e2136aaf66a66e38e2d3e662f530e0955474c3a774` | 91 | 1000000 |
| `A.permuted` | `1bb5806990d68873631a283da859d2bc48f450b3fecef8576af20bc3d1864247` | `a765cc542ae0a871a5cc77b8f395cc443d3912ce5763365866dfa2ace3d84d8d` | 91 | 1000000 |
| `B.independent` | `bc1cd6b64b84f1e6496f1e78d87528a46274fc170ede7ca8d93e019280ed826a` | `bd582ba84c0b72270c201e0c593c74165cbce47ff03990e615b8bff1ba13ffb0` | 91 | 1000000 |

Jeder Arm enthaelt 101 reduzierte Ereignisse in 91 gemeinsamen
Abschlussgruppen. Der Ausfuehrungsdigest bindet Sequenzdigest und technische
Vorschlagsschritte gemeinsam.

## 4. Sieben feste Arme

1. `A.reference`: unveraenderte Quelle und verlustfreie Teilung an allen
   Rezeptorabschlusszeitpunkten.
2. `A.partitioned`: identische Rezeptorwerte, Abschlusszeitpunkte und
   Reihenfolge; nur jeder Integrationsabschnitt wird deterministisch in zwei
   gleich lange Teilschritte zerlegt. Es entstehen keine neuen
   Rezeptorereignisse.
3. `A.stretched`: identische geordnete Rezeptorwerte; alle Zeitpunkte und
   Dauern werden relativ zum Start exakt mit Faktor `2` skaliert.
4. `A.compressed`: identische geordnete Rezeptorwerte; alle Zeitpunkte und
   Dauern werden relativ zum Start exakt mit Faktor `0.5` skaliert.
5. `A.reversed`: die reduzierten Frames werden innerhalb jeder Modalitaet in
   umgekehrter Reihenfolge auf die unveraenderten Zeitfenster dieser
   Modalitaet gelegt. Das gemeinsame Abschlussraster selbst bleibt erhalten;
   gleichzeitig liegende Zielabschluesse bleiben gleichzeitig.
6. `A.permuted`: feste Permutation der Binnenreihenfolge in vier gleich
   langen, zeitlich aufeinanderfolgenden Quellbloecken `0, 3, 2, 1`.
   Damit werden bei 91 reduzierten Audio- und 10 Videoabschluessen nur die
   Bloecke 1 und 3 mit gleichem Modalitaetsinventar vertauscht. Das Zeitraster
   bleibt unveraendert und gleichzeitig liegende Zielabschluesse bleiben
   gleichzeitig.
7. `B.independent`: vorhandene kontrollierte unabhaengige AV-Kontrollquelle
   mit gleicher Dauer, Ereigniszahl und demselben Zeitraster.

Das Vertauschen der Deklarationsreihenfolge gleichzeitig abgeschlossener
Modalitaeten ist nur eine technische Ordnungsnullkontrolle und kein eigener
kausaler Arm.

## 5. Start- und Beobachtungsbedingungen

Jeder Arm startet aus demselben bitgleichen neutralen Schema-2-Snapshot.
Keine Geschichte wird vorgelegt. Der passive Observer liest nach jedem
vollstaendigen Rezeptorabschluss sowie am Ende jedes zusaetzlichen
Integrationsabschnitts:

```text
S = vollstaendiger Aktivierungsvektor
H = vollstaendiger Nachhallvektor
M = vollstaendiger Substratvektor
technischer Weltzeitpunkt
```

Der Observer berechnet keine Eingabe fuer die Runtime und schreibt kein
Ergebnis zurueck. Rohes Audio oder Video wird nicht als Organismuszustand
gespeichert.

## 6. Vorregistrierte Pfadmetrik

Fuer jede Komponente `X in {S, H, M}` und jeden Arm wird aus den beobachteten
Vektoren `X_j` die kumulative euklidische Pfadlaenge gebildet:

```text
l_0 = 0
l_j = l_(j-1) + ||X_j - X_(j-1)||_2
q_j = l_j / l_final
```

Bei `l_final = 0` ist die Komponente technisch unentscheidbar. Sonst wird die
polygonale Zustandsbahn linear auf dem festen Raster
`q = 0.00, 0.01, ..., 1.00` abgetastet. Fuer Referenz `R` und Arm `Y` gilt:

```text
scale_X = max_q ||R_X(q) - R_X(0)||_inf
D_X(Y)  = max_q ||Y_X(q) - R_X(q)||_inf / scale_X
```

Damit wird nur die geometrische Zustandsbahn verglichen. Weltsekunden,
Tickzahl und Anzahl der Observerpunkte werden nicht als Feldzeitmessung
verwendet. S, H und M bleiben getrennt; sie werden nicht durch frei gewaehlte
Gewichte zu einem Score vermischt.

## 7. Numerische Kontrollgrenze

Fuer jeden Mechanismus und Arm werden n, 2n und 4n verglichen. Die numerische
Huelle je Komponente ist vor der Sachentscheidung:

```text
E_X = max(1e-12, 4 * D_X(2n gegen 4n))
```

Bei einem Sachvergleich zwischen Referenz `R` und Arm `Y` gilt
komponentenweise die gemeinsame Huelle

```text
E_X(R,Y) = max(E_X(R), E_X(Y))
```

Damit kann weder ein numerisch ruhiger Referenzarm noch ein numerisch
unruhiger Vergleichsarm die Toleranz einseitig bestimmen.

Erforderliche technische Kontrollen:

- frische 4n-Reproduktion ist bitgleich;
- Quellwerte und Abschlussgruppen entsprechen ihrer Armdefinition;
- `A.partitioned` besitzt keine zusaetzlichen Rezeptorereignisse;
- Gesamt-M bleibt innerhalb der vorhandenen Invariantengrenze erhalten;
- alle S-, H- und M-Werte sind endlich und innerhalb der Runtimegrenzen;
- der 2n-zu-4n-Abstand ist nicht groesser als der n-zu-2n-Abstand.

Eine Verletzung ergibt `TECHNICALLY_UNDECIDABLE`.

## 8. Vorregistrierte Entscheidungen

### Technische Teilungsinvarianz

`TECHNICAL_PARTITION_INVARIANT` gilt fuer einen Mechanismus nur, wenn fuer
S, H und M jeweils gilt:

```text
D_X(A.partitioned) <= E_X
```

Scheitert diese Bedingung, lautet die Modellentscheidung
`TECHNICALLY_UNDECIDABLE`. Zeit-Reparametrisierung und Ordnungssensitivitaet
werden dann zwar als Rohdistanzen dokumentiert, aber nicht als Entscheidung
freigegeben.

### Zeit-Reparametrisierung

`TIME_REPARAMETERIZATION_COVARIANT` gilt nur, wenn sowohl `A.stretched` als
auch `A.compressed` fuer S, H und M jeweils

```text
D_X <= max(0.05, E_X)
```

erfuellen. Andernfalls lautet die Einordnung
`WORLD_TIME_BOUND_FIELD_PATH`.

### Ordnungssensitivitaet

`ORDER_SENSITIVE_FIELD_PATH` gilt nur, wenn `A.reversed` und `A.permuted` in
mindestens einer der Komponenten S, H oder M jeweils

```text
D_X > max(0.05, 4 * E_X)
```

erreichen und `B.independent` ebenfalls ausserhalb dieser Grenze liegt.

Alle Einzelwerte werden berichtet. Eine Gesamtentscheidung darf nicht aus
einem gemittelten Score gebildet werden.

## 9. Pflichtvergleich mit B3

Alle Entscheidungen werden fuer F3 und B3 getrennt berechnet. Zeigt B3
dieselbe Klassifikation und liegen die vollstaendigen F3-Pfade innerhalb der
bereits gebundenen E3-Grenze von `5 %` zu B3, gilt Z1 als durch die lineare
gekoppelte Feldbaseline erklaert.

Ein Unterschied zu B3 waere nur ein offener Residualbefund. Er berechtigt
nicht zu einem Feldzeitclaim und muesste vor jeder neuen Mechanik gegen
weitere enge dynamische Baselines geprueft werden.

## 10. Aussage- und Stopplinien

Nicht zulaessig sind aus Z1 Claims zu relativer Feldzeit, Memory,
Feldzeitverdichtung, innerem Kontext, Organisation, Topologie, Semantik,
Selbstregulation oder KI.

Insbesondere gilt:

- Teilungsinvarianz allein ist nur numerische beziehungsweise technische
  Robustheit.
- Zeitkovarianz allein ist nur eine observerseitige Trajektorieneigenschaft.
- Ordnungssensitivitaet allein ist nur kausale Verlaufsabhaengigkeit.
- Weltzeitbindung widerlegt nicht die MCM-Feldmechanik; sie schliesst nur
  diese Runtime als Beleg relativer Feldzeit in Z1.
- Kein Ergebnis darf durch nachtraeglich geaenderte Pfadmetrik, Toleranz,
  Quelltransformation oder Komponentengewichtung gerettet werden.

## 11. Laufnummer

Der letzte ausgefuehrte Forschungsdurchlauf bleibt Lauf 194. Implementierung
und technische Tests erhalten keine Laufnummer. Erst die einmalige
Ausfuehrung des unveraenderten Z1-Vertrags wuerde Lauf 195 erzeugen.

## 12. Bester naechster Schritt

Den unveraenderten one-shot Laufweg genau einmal als Lauf 195 aufrufen. Ein
separater Vollmatrix-Preflight ist nicht zulaessig, weil er dieselben
Forschungsdaten vorwegnehmen wuerde.
