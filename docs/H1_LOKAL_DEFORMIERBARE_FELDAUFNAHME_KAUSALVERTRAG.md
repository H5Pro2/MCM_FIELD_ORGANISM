# H1: lokal deformierbare Feldaufnahme - Kausalvertrag und Kollisionsentscheidung

## Status

```text
Vertragstyp:                         statische Funktionspruefung
einfache lokale Feldempfaenglichkeit: bereits als C1 geprueft
technische Spaetwirkung:              getragen
Nichtredundanz gegen Integrator:      nicht getragen
Memory-Lebenszyklus:                  nicht getragen
H1 als Einzelspur:                    geschlossen
Runtime-Aenderung:                    nein
```

## Forschungsfrage

H1 fragte, ob lokale Feldbeanspruchung die spaetere Aufnahme derselben
Feldregion veraendern kann, nachdem Aktivierung und schneller Nachhall
angeglichen wurden.

Diese Frage ist nicht neu. Der passive C1-Versuch pruefte bereits:

```text
lokaler Weltkontakt
+ lokaler Feldunterschied
-> begrenzter lokaler Empfaenglichkeitszustand
-> angeglichene schnelle Feldrollen
-> identische spaetere Feldprobe
-> veraenderte lokale Weiterleitung
```

Nullsetzung, Zustandstausch, Spiegelung, Zeitteilung und Snapshot wurden
bestanden. Der Befund trug eine technische lokale Spaetwirkung.

## Entscheidende Kollision mit C1

Die C1-Bildung war exakt umformbar zu:

```text
z_i = tanh(Integral[c_i * L_i(x) dt])
```

Eine faire Baseline aus begrenztem lokalem Produktintegrator und festem
symmetrischem Leser reproduzierte Bildung und spaetere Feldantwort exakt.

Damit ist folgende H1-Form bereits geschlossen:

```text
unabhaengige lokale Spur
+ feste Modulation spaeterer Aufnahme oder Weiterleitung
```

Eine andere Benennung als Deformation, Empfaenglichkeit, Praegung oder
Substratwirkung aendert diese Klassifikation nicht.

## Was H1 zusaetzlich leisten muesste

Ein neuer H1-Kandidat waere nur dann funktional verschieden, wenn seine
eigentliche Wirkung bereits waehrend einer zweiten realen Feldgeschichte
entsteht und nicht erst beim spaeteren Leser.

Erforderlich waere:

```text
gleiche schnelle Feldlage
+ identische neue Geschichte B
+ unterschiedliche fruehere Geschichte A
-> unterschiedliche lokale Substratentwicklung waehrend B
-> spaetere Feldwirkung
```

Die fruehere A-Geschichte muesste somit die weitere **Aenderbarkeit** der
lokalen Aufnahme veraendern. Ein unveraenderter A-Wert, den ein fester Leser
mit B kombiniert, reicht nicht.

## Verbindlicher Lebenszyklus

Ein zulaessiger staerkerer Kandidat muesste mit derselben lokalen
Naturbedingung alle folgenden Stufen tragen:

1. **Bildung:** Reale lokale Feldwirkung erzeugt vor jedem Observer einen
   Substratunterschied.
2. **Mitentwicklung:** Identische neue B-Evidenz entwickelt das Substrat je
   nach realer A-Vorgeschichte verschieden weiter.
3. **Feldwirkung:** Diese unterschiedliche Entwicklung veraendert die
   vollstaendige spaetere Feldantwort.
4. **Tausch:** Die Wirkung wandert mit dem vollstaendigen Substratzustand.
5. **Neutralisierung:** Ohne Substratwirkung verschwindet der Zusatzbefund.
6. **Loesung:** Gewoehnliche weitere Feldgeschichte kann die alte Wirkung
   vollstaendig funktionslos machen.
7. **Wiederpraegung:** Dieselbe lokale Kapazitaet kann danach eine andere
   Geschichte tragen.

Keine Stufe darf eine Phasenkennung, einen Loeschbefehl oder eine andere Regel
als die uebrigen Stufen verwenden.

## Kausale Interventionen

Ein spaeterer Kandidat muesste mindestens folgende Zweige besitzen:

| Zweig | Intervention | Erforderliche Aussage |
|---|---|---|
| `A0-B` | keine A-Geschichte, dann B | Grundentwicklung unter B |
| `A1-B` | A-Geschichte, dann identisches B | A beeinflusst Aenderbarkeit waehrend B |
| `U-B` | budgetgleiche, nicht ueberlappende Geschichte, dann B | lokale Spezifitaet statt Gesamtenergie |
| `swap` | Substrat vor B zwischen A0 und A1 tauschen | B-Entwicklung wandert mit Substrat |
| `zero` | Substratwirkung vor B neutralisieren | Zusatzwirkung verschwindet |
| `path-block` | realen lokalen Feldweg waehrend A blockieren | keine Bildung ohne lokale Ursache |
| `solve` | konkurrierende Geschichte ohne Reset | alte Wirkung wird funktionslos |
| `rebind` | andere Geschichte nach Loesung | dieselbe Kapazitaet traegt neue Wirkung |

Aktivierung, Nachhall, aktueller Rezeptorzustand und spaetere Probe muessen an
den jeweiligen Isolationsgrenzen identisch sein.

## Pflichtbaselines mit fairem Budget

Kandidat und Baselines muessen dasselbe Budget erhalten fuer persistente
Werte, Praezision, Parameterzahl, lokalen Radius, Zeitpraefix, Snapshot und
Leseroperationen.

Pflicht sind:

- heutige neutrale Feldruntime;
- eine und mehrere lineare Leaky-Spuren;
- lokale Produktintegratoren bis zum zweiten Grad;
- begrenzte unabhaengige Nichtlinearitaeten;
- fester lokaler multiplikativer Leser;
- feste lokale Rekurrenz;
- feste lokale Normalisierung;
- permanenter adaptiver Gain als unzulaessige starke Gegenkontrolle;
- passive Relaxation mit festem Zerfall.

Reproduziert eine dieser Klassen Bildung, B-Mitentwicklung, Loesung und
Wiederpraegung vollstaendig, ist kein eigenstaendiger H1-Befund vorhanden.

## Unzulaessige Rettungen

H1 darf nicht durch folgende Erweiterungen nachtraeglich gerettet werden:

- weitere unabhaengige Zeitspuren;
- eine speziell gewaehlte Produkt- oder Momentenfunktion;
- eine feste Aktivitaets-zu-Gain-Abbildung;
- unterschiedliche Gleichungen fuer Bildung, Ruhe, Loesung oder Probe;
- eine Schwelle, die nach dem beobachteten Ergebnis festgelegt wird;
- globale Rang- oder Gewinnerauswahl;
- gespeicherte Rangzyklen aus MINI_DIO;
- Partner-, Objekt-, Phasen- oder Episodenkennungen;
- Reward oder gewuenschte Zielantwort.

## Entscheidung

H1 beschreibt als einfache lokal deformierbare Feldaufnahme keine neue offene
Forschungsfamilie. Diese Funktion wurde durch C1 technisch getragen und
zugleich vollstaendig als Produktintegrator mit festem Leser klassifiziert.

Offen bleibt nur eine staerkere gekoppelte Funktion:

> Frühere Feldgeschichte veraendert nicht nur einen spaeter gelesenen Wert,
> sondern die weitere lokale Substratentwicklung unter neuer realer
> Feldgeschichte; dieselbe Dynamik ermoeglicht vollstaendige Funktionslosigkeit
> und andere Wiederpraegung.

Diese offene Funktion ist nicht mehr sinnvoll als isolierte
`Feldempfaenglichkeit` zu behandeln. Sie benoetigt eine gemeinsame begrenzte
Substrat- oder Ressourcenphysik und fuehrt damit sachlich zu H2.

## Bester naechster Schritt

H1 wird nicht implementiert und nicht erneut ausgefuehrt. Als naechstes wird
H2, das begrenzte lokal umverteilbare Feldmedium, statisch auf seine kleinste
nicht willkuerliche Ressourcenbilanz untersucht.

Dabei muss zuerst geklaert werden:

1. Was wird lokal erhalten oder umverteilt?
2. Welche bereits vorhandene Feldwirkung darf die Bewegung verursachen?
3. Wie veraendert die Verteilung spaetere Feldaufnahme oder Weiterleitung?
4. Wie entstehen Loesung und Wiederpraegung ohne Reset oder feste Ablaufzeit?
5. Kann dieselbe Funktion durch Diffusion, Leaky-Spuren oder adaptive Gains
   gleichwertig erklaert werden?

Erst wenn diese Fragen ohne vorgegebene Richtung, Zieltopologie oder
Partnerliste beantwortbar sind, darf eine konkrete H2-Naturhypothese
formuliert werden.
