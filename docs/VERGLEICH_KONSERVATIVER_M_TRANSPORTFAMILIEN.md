# Vergleich konservativer M-Transportfamilien

## Status

```text
Pruefart:                           statischer Familien- und Reduktionsaudit
F1 passiver M-Eigenpotentialfluss: geschlossen
F2 S-Drift plus separater Leser:   geschlossen
F3 konjugierte S-M-Kreuzwirkung:   bedingt offen
konkrete Gleichung:                 nicht gewaehlt
Implementierung oder Versuch:       nicht zugelassen
```

## Forschungsfrage

Welche kleinste konservative Transportfamilie verbindet eine endliche
M-Umverteilung mit einer kausalen S-Rueckwirkung, ohne lediglich Diffusion,
Chemotaxisdrift, Cross-Diffusionsmuster, adaptiven Gain oder einen
gespeicherten Patternzustand mit festem Leser zu realisieren?

M bleibt die einzige langsame Feldkomponente. Jede Familie muss den
[Minimalvertrag fuer M](MINIMALVERTRAG_KONSERVIERTE_BEGRENZTE_FELDGROESSE_M.md)
vollstaendig einhalten.

## Gemeinsame konservative Grenze

Fuer jede Familie gilt:

- `M_i` ist nichtnegativ und endlich;
- `M_total` bleibt je verbundener Geometriekomponente konstant;
- M-Aenderungen entstehen nur durch antisymmetrisch bilanzierte lokale
  Nachbarschaftsfluesse;
- die gleichfoermige M-Verteilung ist funktional neutral;
- Weltkontakt erreicht M nur ueber S;
- alle Vorschlaege lesen denselben abgeschlossenen S-H-M-Vorzustand;
- keine globale Normierung korrigiert die Bilanz nachtraeglich;
- keine Familie erhaelt Ziele, Labels, Schwellen oder Lebenszyklusphasen.

## F1: passiver M-Eigenpotentialfluss

### Familienidee

M bewegt sich ausschliesslich aufgrund eigener lokaler Mengen- oder
Potentialunterschiede. S bestimmt weder Richtung noch Staerke des
M-Transports.

### Dynamische Konsequenz

Bei konvexem lokalem Potential und positiver Mobilitaet wird eine
Inhomogenitaet geglaettet. Bei nichtkonvexer freier Energie koennen
Phasentrennung, Grenzflaechen und Koarsening entstehen.

Aus dem neutralen gleichfoermigen M-Zustand kann normale S-Weltgeschichte
jedoch keine geschichtsspezifische M-Verteilung erzeugen, solange S den
Transport nicht mitbestimmt.

Fuegt man eine S-abhaengige lokale Energie hinzu, ist die Familie nicht mehr
reiner Eigenpotentialfluss. Die eigentliche Naturannahme verschiebt sich dann
in die gewaehlte S-M-Kopplung.

### Reduktion

```text
konvexes Potential:      positive Diffusion / Homogenisierung
nichtkonvexes Potential: Cahn-Hilliard / vorgegebene Phasenlandschaft
keine S-Kopplung:         kein weltbedingter langsamer Traeger
```

### Entscheidung

```text
F1: geschlossen als primaerer MCM-Traeger
Grund: traegt keine S-bedingte Bildung oder faellt auf konservierte
       Diffusions- und Phasenfeldbaselines
```

F1 bleibt Pflichtbaseline und kann als dissipativer M-Eigenanteil einer
spaeteren Familie auftreten. Es ist nicht deren unabhaengige Funktion.

## F2: S-gradientengetriebener M-Drift mit separatem Leser

### Familienidee

Lokale S-Unterschiede bestimmen einen gerichteten konservativen M-Fluss.
Eine davon getrennte Funktion liest die entstandene M-Verteilung spaeter als
additiven S-Beitrag.

```text
S-Gradient -> M-Drift -> M-Muster
M-Muster -> fester S-Leser
```

### Physische Einordnung

Der Transport entspricht einer Drift- beziehungsweise chemotaxisnahen
Familie: Eine konservierte Menge bewegt sich entlang eines Signalfeldes. Je
nach Vorzeichen entsteht Bewegung mit oder gegen den lokalen S-Gradienten.

Die Bewegungsrichtung muss als Naturparameter gesetzt werden und kann
Aggregation, Polarisation oder Entleerung erzeugen. Diese Effekte werden
bereits von Keller-Segel-artigen und verwandten Driftmodellen getragen.

### Projektkollision

Die spaetere Wirkung liegt nicht in derselben Wechselwirkung wie die Bildung.
M speichert ein raeumliches Pattern, das ein fester Leser an S zurueckgibt.
Damit entstehen genau die zwei getrennten Funktionen, die der Minimalvertrag
ausschliesst:

- eine Transportregel schreibt;
- eine Leserregel ruft ab.

Auch ein rein additiver Leser loest diese Trennung nicht. Er ersetzt nur Gain
durch ein fest gelesenes Biaspattern.

### Entscheidung

```text
F2: geschlossen
Grund: Keller-Segel-/Driftbaseline plus separater Pattern-Leser
```

F2 bleibt starke Gegenbaseline fuer weltgetriebene konservative
Musterbildung.

## F3: unteilbare lokal konjugierte S-M-Kreuzwirkung

### Familienidee

Dieselbe lokale Nachbarschaftswechselwirkung besitzt zwei untrennbare
Kausalseiten:

```text
eine S-M-Konjugation verschiebt M konservativ zwischen Nachbarorten
und
dieselbe Konjugation leistet einen additiven internen Gegenbeitrag zur
S-Fortsetzung
```

Es gibt keinen zeitlich oder funktional getrennten M-Leser. Die konkrete
M-Verteilung veraendert die spaetere gemeinsame Wechselwirkung, weil sie
deren gegenwaertiger Materialzustand ist.

### Eigenstaendige physische Rollenart

Die offene Rollenart lautet:

> konservativer konjugierter Feld-Material-Austausch

`Konjugiert` bedeutet nur, dass Fluss und Rueckwirkung als zwei Seiten
derselben lokalen Prozessgroesse bilanziert werden muessen. Der Begriff
behauptet weder thermodynamisches Gleichgewicht noch Onsager-Reziprozitaet.

Im Unterschied zu F2 ist M kein zuerst geschriebenes und danach gelesenes
Pattern. Im Unterschied zu F1 wird die Materialbewegung durch die gemeinsame
S-M-Lage mitbestimmt.

### Bekannte Reduktionsrisiken

Die Familie ist noch sehr nahe an bekannten Klassen:

- konstante lineare Kreuzkoeffizienten koennen auf feste gekoppelte
  Eigenmoden oder lineare Cross-Diffusion fallen;
- ein M-abhaengiger Transportfaktor ist zustandsabhaengige Mobilitaet;
- ein S-gradientenabhaengiger Fluss kann Keller-Segel-Drift bleiben;
- eine nichtkonvexe Potentialkopplung kann Cahn-Hilliard-artige
  Phasentrennung programmieren;
- ein additiver S-Gegenbeitrag kann bei Trennbarkeit erneut Pattern-Leser
  sein;
- Instabilitaet, Wellen oder Polarisation koennen reine
  Cross-Diffusionsmuster sein.

Diese Kollisionen schliessen nicht die gesamte Familie als Universalbaseline.
`Beliebige Cross-Diffusion` waere zu breit und koennte den Kandidaten selbst
enthalten. Vor einer Gleichung muessen deshalb wenige enge Schliessungsformen
verglichen werden.

### Kausale Mindestbedingungen

Eine spaetere F3-Schliessung muss mindestens zeigen:

1. Ohne lokale S-M-Konjugation gibt es weder weltbedingten M-Fluss noch
   M-vermittelten S-Gegenbeitrag.
2. Ein vollstaendiger M-Tausch verschiebt sowohl Flussfortsetzung als auch
   spaetere S-Zusatzwirkung.
3. Das Entfernen nur einer Kreuzrichtung erzeugt eine vorregistrierte
   Ablationsbaseline, nicht eine alternative Runtimefunktion.
4. Die M-Gesamtmenge bleibt bei jeder Kreuzwirkung exakt erhalten.
5. Der gleichfoermige M-Zustand erzeugt keine S-Zusatzwirkung.
6. Spiegelung und Kantenumkehr spiegeln den gesamten gekoppelten Prozess.
7. Keine getrennte Funktion kann erst M bilden und spaeter unveraendert
   auslesen.

### Entscheidung

```text
F3-Rollenart:                       physikalisch formulierbar
konkrete nichtreduzierte Form:      noch nicht nachgewiesen
F3 fuer Schliessungsformen-Audit:   bedingt offen
F3-Gleichung oder Implementierung:  nicht zugelassen
```

## Gesamtvergleich

| Familie | Weltbedingte M-Verteilung | unteilbare Rueckwirkung | staerkste Baseline | Entscheidung |
|---|---:|---:|---|---|
| F1 Eigenpotentialfluss | nein | nein | Diffusion / Cahn-Hilliard | geschlossen |
| F2 S-Drift plus Leser | ja | nein | Keller-Segel plus Pattern-Leser | geschlossen |
| F3 konjugierter Austausch | ja | prinzipiell ja | Cross-Diffusion / Mobilitaet / Eigenmoden | bedingt offen |

## Abgrenzung zur frueher geschlossenen R3-Familie

Der fruehere raeumliche R3-Audit schloss reziproken Kreuzfluss als ersten
Kandidaten, weil weder eine Stoffrolle noch eine MCM-spezifische
Transportursache begruendet war. Dieser Befund bleibt gueltig.

Neu hinzugekommen sind:

- eine explizite endliche konservierte Stoffrolle;
- ein neutraler endlicher Gleichzustand;
- eine lokale Mengenbilanz;
- der Evidenzvertrag fuer verteilte Nichtseparierbarkeit;
- konservative Tausch-, Permutations- und Neutralisierungsinterventionen.

Dadurch darf F3 erneut genau auf Schliessungsformen geprueft werden. Keine
alte Kreuzflussgleichung oder zustandsabhaengige Mobilitaet wird automatisch
wieder zugelassen.

## Stopplinien fuer den naechsten Audit

Eine F3-Schliessungsform wird sofort geschlossen, wenn:

1. sie nur positive Diffusion oder S-Gradientendrift ist;
2. M durch Clipping oder globale Normierung konserviert wird;
3. M nur Gain, Mobilitaet, Zeitkonstante oder Kante skaliert;
4. ein separater fester Leser die M-Verteilung auf S abbildet;
5. eine freie Energie Zielphasen, Wellenlaenge oder Polaritaet vorgibt;
6. konstante lineare Kreuzkopplung nur feste Eigenmoden erzeugt;
7. funktionale Loesung nur Diffusion, Leaky-Zerfall oder Reset ist;
8. die Richtung nach einem gewuenschten Muster gewaehlt wird;
9. nur Instabilitaet oder geometrische Nichtseparierbarkeit gezeigt wird;
10. der gesamte Evidenzvertrag nicht mit einem Parametersatz pruefbar ist.

## Quellen

- E. F. Keller und L. A. Segel,
  [Initiation of slime mold aggregation viewed as an instability](https://doi.org/10.1016/0022-5193(70)90092-5),
  1970. Dient als Drift- und Aggregationsbaseline.
- L. Onsager,
  [Reciprocal Relations in Irreversible Processes II](https://doi.org/10.1103/PhysRev.38.2265),
  1931. Belegt nur die physikalische Moeglichkeit gekoppelter Fluesse und
  Kraefte unter passenden Voraussetzungen.
- V. K. Vanag und I. R. Epstein,
  [Cross-diffusion and pattern formation in reaction-diffusion systems](https://doi.org/10.1039/B813825G),
  2009. Dient als Grenze gegen die Interpretation von Cross-Diffusionsmustern
  als neuer MCM-Funktion.

## Bester naechster Schritt

Als naechstes wird ein **F3-Schliessungsformen-Audit fuer konservativen
konjugierten S-M-Austausch** durchgefuehrt. Er vergleicht hoechstens drei
kleinste Formen:

1. konstante lineare reziproke Kreuzkopplung mit konservativem M-Fluss;
2. begrenzte massenabhaengige Kreuzmobilitaet ohne freie Energielandschaft;
3. lokale bilineare S-M-Kraft-Fluss-Kopplung mit antisymmetrischem M-Transport
   und gebundenem additivem S-Gegenbeitrag.

Der Audit muss algebraisch gegen Eigenmoden, Keller-Segel-Drift,
zustandsabhaengige Mobilitaet, Cross-Diffusion und Pattern-Leser reduzieren.
Danach darf hoechstens eine Form fuer einen mathematischen Minimalvertrag
offen bleiben.
