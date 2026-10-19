# Architekturklärung: begrenzte zeitliche Erfahrungsspur

**Auftrag:** statische Entscheidungsnotiz vom 19.09.2026.  
**Status:** keine Implementierungs-, Test-, Quellen- oder Medienfreigabe. Alle Gates bleiben `False`.

## Funktionslücke

Der aktive Grundpfad verarbeitet Wahrnehmungen als zeitgebundene Einzelzustände:

- Der Audiorezeptor bildet pro Fenster 48 Bandwerte; Phasen- und Quellenidentität
  sind nicht Teil der Ausgabe ([`log_spectral_receptor.py`](../mcm_field_organism/log_spectral_receptor.py)).
- Der visuelle Pfad bildet pro Frame lokale RGB-Mittelwerte; er liefert keine
  Objekt-, Bewegungs- oder Korrespondenzspur
  ([`finite_video_path.py`](../mcm_field_organism/finite_video_path.py)).
- Das Feld verarbeitet zeitlich aufeinanderfolgende Kontakte, ist aber ein
  unabhängiger Zweig. Der bestehende Memorypfad liest keinen Feldschnappschuss
  als Verlaufsbeleg.
- Fast und PPB schreiben Prototyp, Support, Zeit und Slotgeneration fort. Eine
  geordnete Kante zwischen zwei Wahrnehmungszuständen wird nicht gespeichert.
  Der spätere Teilhinweis scannt daher Kandidaten gegen seinen Einzelzustand;
  die Reihenfolge, in der frühere Zustände entstanden, ist für die A/B-Auflösung
  nicht verfügbar.

Damit ist nicht bewiesen, dass die Rezeptorwerte zeitliche Beziehungen
grundsätzlich nicht tragen. Bewiesen ist nur der Verlust dieser Beziehungen im
heutigen Abrufpfad.

## Vorhandene Evidenz

- **S2-NU:** Zwei Folgen mit bitgleichen Randzuständen und demselben Multiset
  wurden durch die fest gebundene Kennzahl `T` unterschieden. Das belegt eine
  Reihenfolgeempfindlichkeit der Kennzahl, nicht Quellenfortsetzung,
  Objektidentität oder Lernbindung.
- **S2-NW/S2-NX:** Ein aus beobachteten Übergängen gelernter Skalar konnte auf
  gebundenen Fortsetzungen nützen; Wechsel verursachten eigene Verluste. Die
  Befunde belegen begrenzte Vorhersage in einer Dynamikklasse, nicht die
  Auswahl der passenden Erfahrung aus aktueller Wahrnehmung.
- **S2-MI:** Zeitnähe, gemeinsame Datei, Generatorrolle und bestehende
  Zeit-/Feldbindungen sind keine selektive, beobachtbare Erfahrungsbindung.
  Für eine Quellen- oder Objektzuordnung fehlt weiterhin neutrale
  Korrespondenzevidenz.
- **Medien-Erfahrungsvergleich:** Mehr frühere Formationen ergaben keinen
  öffentlichen Abrufvorteil. Zusätzliche Kandidaten können Mehrdeutigkeit
  erhöhen; dies ist kein Hinweis auf eine fehlende oder falsche Identität.

## Technische Bestandsaufnahme

### Vorhandene Eingänge

Der Audioeingang besitzt eine lokale zeitliche Form: Das Standardprofil bindet
48 kHz, 4.800 Samples pro Hann-Fenster, 480-Sample-Hops und 48 logarithmische
Bandwerte. Am Rezeptorausgang bleiben Fensterstart/-ende und Snapshotindex
sowie die 48 Energiebandwerte erhalten
([`log_spectral_receptor.py:15`](../mcm_field_organism/log_spectral_receptor.py:15),
[`log_spectral_receptor.py:128`](../mcm_field_organism/log_spectral_receptor.py:128)).
Die FFT-Phase, das PCM-Fenster und ältere Fensterwerte gehören nicht zur
Rezeptorausgabe.

Der visuelle Eingang besitzt eine lokale räumliche Form: Die Geometrie trägt
12 × 8 Zellen mit je drei RGB-Kanälen sowie einen Frameindex. Der Rezeptor
reduziert ein Bild auf lokale Zellmittelwerte
([`finite_video_path.py:25`](../mcm_field_organism/finite_video_path.py:25),
[`finite_video_path.py:191`](../mcm_field_organism/finite_video_path.py:191)).
Pixel, Kanten, optischer Fluss und eine Zuordnung von Zellen zwischen zwei
Frames werden nicht ausgegeben.

Im vorhandenen Aufruferanschluss werden diese Einzelzustände zusätzlich mit
einem gemeinsamen Feldzeitfenster, einem Ereignisordinal und Quellenbindungen
versehen. Der Adapter prüft getrennte Audio- und Videozeitformen und projiziert
Audio vor dem Kontakt auf das Halbprofil
([`_s2ob_private_caller_binding.py:273`](../tools/_s2ob_private_caller_binding.py:273)).
Die dort sichtbaren Sample- und Frameindizes sind gebundene technische Zeiten.
Ob ein vorgelagerter Decoder darüber hinaus ursprüngliche Medien-PTS vollständig
erhält, ist für den Kern aus diesen Anschlüssen nicht belegt.

### Erreichbarkeit und Verlust

Die vollständige AV-Formation übergibt denselben gebundenen Einzelzustand an
zwei unabhängige Zweige: Feldkontakt und Memoryfortschreibung. Der Aufrufer
initialisiert sie getrennt und der Streamprozessor führt beide nebeneinander
([`_s2ob_private_caller_binding.py:342`](../tools/_s2ob_private_caller_binding.py:342)).
Das Feld erhält fortlaufende Zeitfenster, aber der Memorykern verwendet keinen
Feldschnappschuss als Übergangseingabe.

Memory erhält die aktuellen Audio-/Visualwerte, Prototypen, Support,
Expositions-/Zustandsdigests und Generationen. PPB und Fast aktualisieren bei
Treffern den ausgewählten Prototyp und den gesättigten Support; sie speichern
keine Kante zum vorherigen Rezeptorzustand
([`_ppb1_reference.py:177`](../mcm_field_organism/_ppb1_reference.py:177),
[`_tspm1_private.py:1469`](../mcm_field_organism/_tspm1_private.py:1469)).
Slotgenerationen schützen Ersetzung, bilden aber keine zeitliche Beziehung
zwischen zwei Wahrnehmungen ab.

Beim read-only Abruf liegen dem Scan der aktuelle Cue und die gespeicherten
Kandidatenwerte vor. Die A-Auflösung unterscheidet Mehrfachtreffer und
Konflikte; sie erhält keine Vorgänger-Nachfolger-Daten
([`_s2kz_private_auditory_partial_cue_retrieval_336.py:717`](../tools/_s2kz_private_auditory_partial_cue_retrieval_336.py:717),
[`_s2kz_private_auditory_partial_cue_retrieval_336.py:753`](../tools/_s2kz_private_auditory_partial_cue_retrieval_336.py:753)).

Damit ist technisch belegt verloren: Reihenfolge früherer Einzelzustände,
Richtung und Größe eines Übergangs, visuelle Korrespondenz und die auditive
Phase. Offen bleibt, ob die erhaltenen 48 beziehungsweise 288 Werte für eine
später begründete Variantenbeziehung ausreichen würden.

### Mögliche spätere Anschlussstelle und faire Vergleiche

Ohne Feld, Memorykerne oder historische Profile umzubauen, könnte ein späterer
privater Verlaufsanschluss nur am bereits bestehenden Adapter liegen: nach der
gebundenen Rezeptor-/NJ-Projektion und vor `bind_pair` beziehungsweise der
Formation. Er könnte dann ausschließlich vorhandene Halbprofilwerte,
Visualwerte, Originalindizes, Zeitfenster, Ordinale und Digests lesen. Das ist
eine Anschlussmöglichkeit, keine Freigabe für einen Mechanismus und keine
Bestätigung, dass diese Daten eine Erfahrungsbindung tragen.

Ein fairer Nutzenvergleich müsste denselben Eingang dreifach führen:

1. bestehender Einzelzustands- und direkter Slotscan ohne Verlauf;
2. eine einfache geordnete Referenzfolge mit denselben Zuständen, Zeiten und
   Übergängen;
3. gegebenenfalls der neue Speicheranschluss mit exakt denselben gebundenen
   Eingängen.

Die vorhandene S2-NU-Rechnung (`step`, `T`) ist eine einfache direkte
Ordnungsreferenz, aber keine Abrufregel. PERSIST und LINEAR aus S2-NV sowie die
gefrorenen Lerner aus S2-NW/S2-NX nutzen ebenfalls nur verfügbare
Rezeptorpräfixe; sie sind Vorhersagekontrollen und keine zulässige
Erfahrungszuordnung. Keines dieser Verfahren darf versteckte Generatorrollen,
Quellenlabels oder spätere Zielwerte erhalten.

## SFA: statische Anschlussprüfung

Slow Feature Analysis (SFA) ist hier ausschließlich als möglicher Kandidat für
**Merkmalslernen vor einer möglichen Verlaufsbindung** zu betrachten. Das
Lernprinzip zielt auf Merkmale mit geringer zeitlicher Veränderung; es ist weder
eine gespeicherte Sequenz noch eine Quellen-, Objekt- oder Erfahrungsidentität.
Die Bezugsliteratur ist [Wiskott und Sejnowski (2002)](https://pubmed.ncbi.nlm.nih.gov/11936959/).
Die theoretische Formulierung ergänzt die Langsamkeitsminimierung um Nullmittel,
Einheitsvarianz und Dekorrelation, damit eine konstante Ausgabe keine zulässige
triviale Lösung ist ([Wiskott, 2003](https://www.ini.rub.de/PEOPLE/wiskott/Publications/Wisk2003b-SFATheoryFree-NC.pdf)).
Diese Bedingungen sichern jedoch keine Unterscheidung verschiedener Inhalte.

### Verfügbare geordnete Folge

Der gebundene Sitzungsweg materialisiert und verarbeitet Ereignisse nacheinander
([`_s2ob_private_caller_binding.py:223`](../tools/_s2ob_private_caller_binding.py:223),
[`_s2ob_private_caller_binding.py:363`](../tools/_s2ob_private_caller_binding.py:363)).
Für jedes bereits erreichte Ereignis sind damit Halbprofilwerte, Visualwerte,
Originalindizes, Zeitfenster, Ordinal, Profil- und Quelldigests verfügbar.
Ein späterer Lerner könnte aus diesen bereits erzeugten Zuständen eine geordnete
numerische Lernfolge erhalten.

Das vollständige Manifest enthält allerdings auch Bindungen späterer Ereignisse.
Der heutige Anschluss trennt keinen eigenständigen Lernport von dieser
Verwaltungsstruktur. Ohne einen später ausdrücklich geprüften Port wäre daher
nicht belegt, dass ein Lerner keine Zukunftsdaten, Rollen oder Quellenmetadaten
einsehen kann. Der reine Umstand, dass `process()` zeitlich nacheinander
aufgerufen wird, genügt hierfür nicht.

### Kleinste getrennte Lern-/Prüfgrenze

Ohne Feld oder Memorykerne umzubauen, wäre lediglich eine private,
rezeptornahe Dreiteilung erforderlich:

1. **Lernzufuhr:** nimmt nur den aktuell materialisierten, profilgebundenen
   Vektor und seine gebundene Zeit an; keine künftigen Vektoren,
   Manifestrollen oder Quellennamen.
2. **Einfrieren:** erzeugt nach einer vorab festgelegten Lernfolge einen
   unveränderlichen, profilgebundenen Lernzustand.
3. **Prüfprojektion:** nimmt nur diesen eingefrorenen Zustand und den aktuellen
   Prüfvektor an und gibt eine Merkmalsfolge aus. Sie schreibt weder in Fast,
   PPB noch in das Feld zurück.

Das beschreibt eine Informationsgrenze, keine Schnittstelle mit gewählten
SFA-Parametern oder eine Implementierungsfreigabe. Insbesondere wäre eine
getrennte Testfolge nötig; ihre Werte dürften den Lernzustand nicht verändern.

### Technische Gegenhypothesen und offene Punkte

- Konstante oder nahezu konstante Eingänge können keine informative langsame
  Veränderung von einem trivialen konstanten Merkmal unterscheiden.
- Geringe effektive Variation kann die lernbare Dimension begrenzen. Ob die
  vorhandenen 48 Audio- beziehungsweise 288 Visualwerte dafür auf einem neuen
  Bestand ausreichenden Rang besitzen, ist ungeprüft.
- Der Audioausgang enthält keine Phase; der visuelle Gitterausgang enthält
  räumliche Zellen, aber keine Zellkorrespondenz oder Bewegung. SFA könnte
  deshalb ruhigen Hintergrund stärker abbilden als einen relevanten bewegten
  Inhalt. Diese Gegenhypothese wird nicht durch langsame Werte widerlegt.
- Unterschiedliche Audio- und Videozeitformen bleiben getrennt. Ohne später
  vorab gebundene Kopplungsregel ist keine gemeinsame audiovisuelle SFA-Folge
  begründet.
- Es ist offen, ob eine SFA-Projektion unter Rezeptorvariation mehr trennt als
  sie verwischt. Aus der biologischen Plausibilität folgt hierzu keine
  Architekturentscheidung.

### Fester Prüfentwurf: selektive visuelle Zuordnung

Die fachliche Frage eines späteren Tests wäre: **Werden zurückgehaltene
veränderte visuelle Rezeptorfolgen ihrer passenden Referenz zuverlässiger
zugeordnet, ohne andere Inhalte stärker damit zu verwechseln?** Der Entwurf
prüft nur diese Frage; er ist kein Sequenzgedächtnis und behauptet keinen
Feldbeitrag.

### Fester Bestand und Rollen

Der spätere Bestand umfasst ausschließlich 32 RGB-Frames im vorhandenen Format
`1920 × 1080 × 3`, `uint8`; der Rezeptor bildet unverändert 12 × 8 × 3 Werte.
Jede Folge enthält vier Frames bei lokalen Zeiten `0`, `100`, `200` und
`300 ms`. Sie ist eine eigene zeitliche Episode. Übergänge werden nur innerhalb
einer Episode gebildet, nie über eine Segmentgrenze hinweg.

Jeder Frame entsteht deterministisch aus einem Hintergrund und einem
rechteckigen Vordergrund: Hintergrund zuerst über das gesamte Bild schreiben,
dann ein Rechteck mit Höhe 270, Breite 320 und vertikaler Lage `y=405` ohne
Interpolation überschreiben. Die horizontale Koordinate bezeichnet die linke
Kante. Farben werden als RGB-Bytevektoren verwendet.

| Folge | Anzahl | Hintergrund | Vordergrund | x-Positionen | Rolle außerhalb des Lerners |
| --- | ---: | --- | --- | --- | --- |
| `L1` | 4 | `(24,32,48)` | A: `(224,64,64)` | `160,480,800,1120` | Lernen |
| `L2` | 4 | `(24,32,48)` | B: `(64,224,64)` | `160,480,800,1120` | Lernen |
| `RA` | 4 | `(24,32,48)` | A | `240,560,880,1200` | Referenz A |
| `RB` | 4 | `(24,32,48)` | B | `240,560,880,1200` | Referenz B |
| `QA` | 4 | `(24,32,48)` | A | `320,640,960,1280` | passende Prüfvariante A |
| `QB` | 4 | `(24,32,48)` | B | `320,640,960,1280` | andere bekannte Prüfvariante B |
| `QAB` | 4 | `(96,80,32)` | A | `320,640,960,1280` | Hintergrundwechsel, erwartete Zuordnung A |
| `QC` | 4 | `(24,32,48)` | C: `(64,64,224)` | `320,640,960,1280` | Inhalt ohne Referenz, offene Diagnose |

Die gebundenen Rollen stehen nur in der Evaluationswurzel. Der Lerner erhält
pro Lernframe allein den Rezeptorvektor, eine Segmentgrenze und die lokale
Zeitordnung. Die Segmentgrenze kennzeichnet ausschließlich, dass kein
Übergangspaar über eine tatsächlich getrennte Aufnahmeepisode gebildet werden
darf. Sie ist kein Familien- oder Identitätslabel und kein Nachweis, dass der
Lerner Erfahrungsgrenzen selbstständig ermittelt.

Die Prüfung erwartet für `QA` Referenz A, für `QB` Referenz B und für `QAB`
trotz Hintergrundwechsel Referenz A. Damit ist ausdrücklich gebunden, dass der
Hintergrund als Störfaktor behandelt wird. `QC` hat keine Referenz: Seine
Rangwerte werden nur diagnostisch berichtet. Eine nächstliegende Referenz ist
weder eine positive Zuordnung noch eine Unbekanntheitserkennung.

### Vollständig gebundener linearer SFA-Arm

Es gilt ausschließlich **lineare SFA mit einer Merkmalskomponente** (`J=1`).
Die acht Lernvektoren aus `L1` und `L2` bilden in genau dieser Reihenfolge die
Mittelwert- und Kovarianzstatistik; die sechs innerhalb der beiden Folgen
liegenden Übergänge bilden die Differenzkovarianz. Es gibt keine Übergänge von
`L1` nach `L2` und keine Lernupdates aus Referenz- oder Prüffolgen.

Für Lernvektoren `x` mit Breite 288 gelten, ausschließlich auf diesem
Lernbestand:

```text
μ = mean(x)
C = mean((x - μ) (x - μ)^T)
ε = 2^-40
R = Unterraum der Eigenmoden von C mit λ > ε * λ_max(C)
Δx = x[t+1] - x[t]                              # nur innerhalb L1 oder L2
G = mean(Δx Δx^T)
G w = γ C w, w ∈ R, w^T C w = 1                # kleinster verallgemeinerter Eigenwert γ
y = w^T (x - μ)
```

Wiederholte Eigenwerte von `C` bedeuten nur unterschiedliche Basen desselben
Unterraums `R`; sie machen die Projektion nicht automatisch unbestimmt. Die
SFA-Richtung ist erst dann mehrdeutig, wenn der kleinste verallgemeinerte
Eigenwert `γ₁` nicht von `γ₂` durch mehr als
`ε * max(1, abs(γ₁), abs(γ₂))` getrennt ist. Das Vorzeichen von `w` wird in
den ursprünglichen 288 Rezeptorkoordinaten so gewählt, dass die erste
Komponente mit Betrag mindestens `ε` positiv ist.

Wenn `λ_max(C)` nicht positiv oder nicht endlich ist, wenn `dim(R) < 2`, wenn
`G` oder die verallgemeinerte Eigenzerlegung nicht endlich ist, wenn `γ₁` und
`γ₂` nicht getrennt sind oder wenn die Signregel nicht anwendbar ist, endet der
spätere Versuch als
`SFA_TRAINING_DEGENERATE`. Es gibt keine Ersatzprojektion, keine zusätzliche
Komponente und keine Nachwahl von Lernfolgen.

`μ`, der Unterraum `R`, `w`, `γ₁`, `ε`, der Profil-/Geometriedigest und die
vollständige Segmentordnung bilden den eingefrorenen Lernzustand. `RA`, `RB`,
`QA`, `QB`, `QAB` und `QC` werden nur mit diesem Zustand projiziert.

### Gemeinsame Rangregel und Auswertung

Der Roharm verwendet sämtliche ursprünglichen 288 Rezeptorkoordinaten. Für
jede Koordinate bestimmt er ausschließlich aus den acht Lernwerten den
Mittelwert `μ_i` und die Standardabweichung `s_i`. Bei `s_i > ε` gilt die
eingefrorene Darstellung `(x_i - μ_i) / s_i`; bei `s_i <= ε` bleibt die
Koordinate als begrenzte Rohabweichung `x_i - μ_i` mit fester Skala `1`
erhalten. Konstante Lernkoordinaten werden damit weder nachträglich entfernt
noch durch Testwerte skaliert; ihre Anzahl und Indizes werden getrennt
protokolliert. Der SFA-Arm verwendet den skalaren Wert `y`. Damit werden keine
Roh- und SFA-Distanzen gegeneinander verglichen.

Beide Arme verwenden jedoch dieselbe geordnete Vergleichsform. Für eine
Prüffolge `q`, eine Referenz `r` und die jeweilige Darstellung `a` gilt:

```text
score_a(q, r) = mean_t(mean_i(abs(a(q[t])[i] - a(r[t])[i])))
```

Im Roharm läuft `i` über alle 288 Originalkoordinaten, im SFA-Arm nur über die
eine Merkmalskomponente; beide Mittelungen sind damit auf ihre feste Breite
normiert. Für `QA`, `QB` und `QAB` wird nur zwischen `RA` und `RB` gerankt.
Der passende Score muss strikt kleiner sein. Gleichstand führt zu
`ABSTAIN_TIE`; ein eindeutiger Rang ist nur eine relative Zuordnung und keine
sichere Zulassung.

`step`/`T` wird für Roh- und SFA-Folgen zusätzlich protokolliert, aber nicht zur
Ergebnisentscheidung verwendet. Es misst die vom SFA-Arm mitoptimierte
Langsamkeit und kann daher keinen Nutzen belegen.

Die Bewertung führt getrennt:

- **zusätzliche korrekte Zuordnung:** SFA ordnet `QA`, `QB` oder `QAB` korrekt
  zu, wo der Roharm nicht korrekt zuordnet;
- **Verlust:** der Roharm ordnet einen dieser Fälle korrekt zu, SFA nicht;
- **Verwechslung:** SFA ordnet ihn strikt der jeweils falschen bekannten
  Referenz zu;
- **Enthaltung:** Gleichstand, getrennt von Verlust und Verwechslung;
- **offene Diagnose:** beide Scores von `QC`, ohne Erfolgs- oder Fehlurteil.

Ein begrenzter Merkmalsnutzen dürfte nur behauptet werden, wenn mindestens eine
zusätzliche korrekte Zuordnung vorliegt und gleichzeitig keine Verluste sowie
keine Verwechslungen auftreten. Langsamere Merkmale ohne diesen selektiven
Vorteil oder mit zusätzlichen Verwechslungen verwerfen diese gebundene
Ausführung. Ein negativer Befund verwirft nicht sämtliche SFA-Ansätze; ein
positiver Befund beweist nur eine positionsrobuste Unterscheidung dieser zwei
Farbmuster. Er beweist weder allgemeine Formerkennung, Objektidentität,
Quellenbindung noch allgemeine Variantenrobustheit.

## Kleinster Kandidat

Ein möglicher, **noch nicht freigegebener** Kandidat ist eine
begrenzte **geordnete Übergangsspur** in Betracht. Sie gehört vor einen
eventuellen Memoryanschluss und ist kein zusätzlicher A/B-Slot, kein Cluster und
keine Identitätsbehauptung.

Eine Spur hält höchstens vier aufeinanderfolgende, vom Aufrufer bereits
geordnet gebundene Übergänge fest. Jeder Eintrag enthält ausschließlich:

1. Profil- und Sitzungsbindung,
2. Vorgänger- und Nachfolgerdigest,
3. den vorzeichenbehafteten Rezeptorwertunterschied in Originalindexfolge,
4. native Zeitdifferenz und Ordinalposition.

Die Sitzungsreihenfolge begrenzt nur die Chronologie der Beobachtung. Sie
bedeutet weder, dass beide Zustände dieselbe Quelle darstellen, noch dass ihre
Ähnlichkeit eine zulässige Variation beschreibt. Keine automatische Bindung
allein aus zeitlicher Nähe ist zulässig.

Der Kandidat würde zunächst nur eine **exakte Folgenwiederholung** prüfen:
dieselben gebundenen Rezeptorzustände in derselben gebundenen Ordnung. Das ist
von zwei weitergehenden Fragen zu trennen:

- **Wiedererkennen unter Variation:** Eine veränderte Folge könnte als passend
  behandelt werden, wenn eine vorab begründete beobachtbare Beziehung ihre
  Unterschiede trägt. Variantenrobustheit muss geprüft werden, setzt aber
  nicht bereits bewiesene Objektidentität voraus.
- **Quellen-/Objektidentität:** Die Aussage, dass beide Folgen dieselbe Quelle
  oder dasselbe Objekt betreffen, ist stärker. Sie folgt weder aus exakter
  Wiederholung noch aus einer bestandenen Variantenprüfung.

Die geordnete Spur liefert für diese beiden weitergehenden Fragen noch keine
Beziehung. Sie darf Varianten deshalb nicht stillschweigend als dieselbe
Erfahrung übernehmen, aber ihr strenges Verhalten ist auch kein Beweis, dass
Variantenrobustheit grundsätzlich nur mit schon geklärter Objektidentität
möglich wäre.

## Nutzen- und Widerlegungskriterium

Der Kandidat hätte zunächst nur einen chronologischen Zusatznutzen, wenn ein
späterer, bereits gebundener Präfixzustand eine **geordnete** Fortsetzung von
einer Permutation mit gleichen Einzelzuständen unterscheiden kann, während eine
Einzelzustandsbasislinie dies nicht kann. Das wäre keine Wiedererkennung eines
Objekts oder Klangs.

Eine einfache geordnete Referenzfolge muss dieselbe Zeitinformation erhalten,
wenn später ein Vorteil der vorgeschlagenen Speicherorganisation behauptet
wird. Ein Unterschied gegenüber einer ausschließlich ungeordneten oder
einzelzustandsbasierten Referenz zeigt daher höchstens den Informationsgewinn
der Ordnung, nicht einen besonderen Nutzen dieser Speicherorganisation.

Ein späterer Minimaltest müsste vorab einen neuen Bestand mit folgenden Fällen
festlegen:

- eine Referenzfolge und eine Permutation mit gleichen Randzuständen und
  gleichem Zustandsmultiset,
- eine exakt wiederholte Fortsetzung,
- ein gemeinsames Präfix mit zwei abweichenden Folgezuständen,
- eine numerische Variante und eine unabhängige Kontrolle.

Die Einzelzustandsbasislinie erhält nur den aktuellen Zustand; eine ungeordnete
Kontrolle erhält höchstens das kanonische Multiset. Eine geordnete
Referenzbasislinie erhält dieselben Übergänge wie die Spur. Eine eindeutige
Fortsetzung bei gemeinsamem Präfix und unterschiedlichen gebundenen Nachfolgern
wäre ein Fehler und müsste zur Enthaltung führen.

Der Kandidat ist zu verwerfen, wenn die Spur die vorgebundene
Reihenfolgegegenprobe nicht von den Basislinien trennt, wenn sie einen
gemeinsamen Präfixzweig positiv als eindeutig fortsetzt oder wenn sie ohne
externe Rollen-/Quelleninformation nicht vollständig prüfbar gebunden werden
kann. Auch ein Bestehen würde keine Variantentoleranz, Quellenidentität oder
praktische Videoabrufverbesserung zeigen.

Die entscheidende offene Brücke bleibt damit unbeantwortet: Welche
**beobachtbare** Beziehung könnte eine veränderte Folge mit einer früheren
Erfahrung verbinden, ohne beliebige Ähnlichkeit als Gleichheit oder eine
vorgegebene Identität zu übernehmen? Für diese Beziehung liegt derzeit kein
begründeter Ansatz vor. Sie wird ausdrücklich offengelassen.

## Feld und Ressourcen

Die Spur wäre zunächst rein rezeptorbasiert. Das Feld bleibt unverändert und
liefert weder Eingaben noch Bestätigung für die Spur. Daraus folgt ausdrücklich
keine Feld-Memory-Kopplung und keine Behauptung, dass Feldtrajektorien
Erfahrungsbeziehungen tragen.

Eine spätere, begrenzte Prüfung müsste die Spur auf maximal vier Übergänge und
einen festen audiovisuellen Profilzustand beschränken. Vollständige Werte,
Digests, Zeiten und Ordinale müssten innerhalb der bestehenden
Zustands-/Belegbudgets vorab bilanziert werden. Ohne tragfähige Bilanz bleibt
auch dieser Kandidat gesperrt.

## Empfehlung

Der Übergangsspur-Kandidat wird vorerst nicht weiterverfolgt. S2-NU hat die
engere Frage der Reihenfolgeempfindlichkeit bereits begrenzt beantwortet; sie
ist nicht mit der schwierigen Frage zu verwechseln, wie variierende
Wahrnehmungen als passende frühere Erfahrung nutzbar werden.

Der Video-Abrufzweig bleibt pausiert. Für Variantenrobustheit, Quellen- oder
Objektbindung und eine Auswahl der passenden Erfahrung fehlt weiterhin die in
S2-MI benannte beobachtbare Korrespondenzevidenz. Bis eine fachlich begründete
Brücke vorliegt, ist die Empfehlung: pausieren.
