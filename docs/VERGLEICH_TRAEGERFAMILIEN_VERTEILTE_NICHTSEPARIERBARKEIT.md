# Vergleich von Traegerfamilien fuer verteilte Nichtseparierbarkeit

## Status

```text
Pruefart:                           statischer Rollen- und Familienvergleich
T1 nur S-vermittelte Ortszustaende: geschlossen
T2 nichtkonservativer L-Eigenfluss: geschlossen
T3 konservative L-Umverteilung:    bedingt offen
T4 variable Beziehungen/Topologie: verboten
konkrete Gleichung:                 nicht zugelassen
Implementierung oder Versuch:       nicht zugelassen
```

## Forschungsfrage

Welche kleinste Traegerfamilie besitzt eine eigene physische Rolle fuer eine
spaeter pruefbare verteilte kausale Nichtseparierbarkeit, ohne lediglich die
bereits geschlossenen lokalen Register, Reaktions-Diffusionsmuster oder
adaptive Beziehungen erneut zu benennen?

Der Vergleich waehlt keine Memory-Mechanik. Er entscheidet nur, ob eine
Traegerrolle einen weiteren statischen Vertrag rechtfertigt.

## Gemeinsame Grenze

Alle zulaessigen Familien muessen:

- im einen gemeinsamen MCM-Feld liegen;
- die bestehende feste Feldgeometrie verwenden;
- nur abgeschlossene lokale Vorzustaende und Feldproben lesen;
- Weltkontakt ausschliesslich ueber den normalen S-Pfad erhalten;
- dieselbe inhaltsfreie Naturform an gleichartigen Orten verwenden;
- ohne Labels, Reward, Ziele, Partner-IDs und Lebenszyklusphasen auskommen;
- durch eine vorab feste Kopplungsablation exakt die heutige S-H-Runtime
  erhalten;
- durch den Evidenzvertrag kausal tausch-, ablations- und
  permutationspruefbar sein.

## T1: nur S-vermittelte ortsgebundene Zustaende

### Traegeridee

Jeder Feldort besitzt einen langsamen lokalen Zustand. Zwischen langsamen
Zustaenden gibt es keinen direkten Fluss. Die raeumliche Kopplung erfolgt nur
ueber das bestehende schnelle S-Feld:

```text
L_i <-> S_i <-> S-Nachbarschaft <-> S_j <-> L_j
```

### Abgleich mit dem Projektstand

Dies ist exakt die Familie R1. Ihre lokalen dissipativen,
nichtgradientigen und additiven Schliessungsformen wurden gegen Leaky-Spur,
interne Gegenvariable, Hysterese und Oszillator reduziert. Nach Ausschluss
dieser Klassen blieb keine begruendete lokale Naturfunktion.

Kollektive Effekte koennen dennoch entstehen, werden aber primaer durch eine
Ein-Diffusor-Reaktions-Diffusionsbaseline erklaert. Der neue Evidenzvertrag
liefert keinen neuen lokalen Traeger fuer T1.

### Entscheidung

```text
T1: geschlossen
Grund: identisch mit abgeschlossenem R1-Raum; verteilte Effekte besitzen
       weiterhin die Ein-Diffusor- und lokale Hysteresebaseline
```

T1 bleibt Pflichtbaseline.

## T2: nichtkonservativer L-Eigenfluss

### Traegeridee

L besitzt auf der vorhandenen Geometrie einen eigenen Nachbarschaftsfluss.
Lokale L-Menge darf durch Reaktion beziehungsweise Relaxation entstehen oder
verschwinden. Der Gesamtwert von L ist nicht erhalten.

### Physische Einordnung

Ein nichtkonservativer Ordnungsparameter mit raeumlicher Glattung liegt in
der Naehe von Allen-Cahn-artiger Phasenrelaxation. Zusammen mit lokaler S-L-
Reaktion entsteht eine klassische Zwei-Komponenten-Reaktions-Diffusionsform.

Die Familie kann:

- lokale Unterschiede verbreiten und glaetten;
- Grenzflaechen bewegen;
- Wellen, Flecken und Koarsening erzeugen;
- durch lokale Reaktion Werte auf- und abbauen.

Keine dieser Eigenschaften definiert eine eigenstaendige begrenzte
Traegerressource. Loesung kann lokal durch dieselbe Reaktion vorgegeben sein,
ohne dass eine frei gewordene Kapazitaet an anderer Stelle kausal nachweisbar
wird.

### Baselinekollision

Ohne weitere Physik ist T2:

- positive L-Diffusion plus lokaler Registerzustand;
- nichtkonservative Phasenrelaxation;
- klassische Zwei-Komponenten-Reaktions-Diffusion;
- Muster- oder Attraktorkinetik bei nichtkonvexer lokaler Form.

### Entscheidung

```text
T2: geschlossen
Grund: eigener L-Fluss fuegt Transport und Musterbildung hinzu, aber keine
       unabhaengige begrenzte Traegerrolle
```

T2 bleibt Diffusions-, Phasenrelaxations- und Musterbaseline.

## T3: konservative Umverteilung einer begrenzten Feldgroesse

### Traegeridee

Eine nichtnegative endliche Feldgroesse M liegt verteilt auf den bestehenden
Feldorten. Die lokale Menge kann sich durch Fluss zwischen benachbarten Orten
veraendern, wird innerhalb des geschlossenen Feldes aber weder erzeugt noch
vernichtet.

```text
M_i nimmt zu
<=> bilanziell entsprechende M-Menge verlaesst andere verbundene Orte
```

M ist vorlaeufig eine Stoff- oder Kapazitaetsrolle, kein gespeicherter Inhalt.

### Eigenstaendige physische Rolle

T3 fuegt gegenueber T1 und T2 eine neue, kausal pruefbare Bedingung hinzu:

> Lokale Veraenderung ist zugleich eine raeumliche Ressourcenverschiebung.

Dadurch sind lokale Bildung und lokale Loesung nicht unabhaengig. Eine
staerkere Belegung an einem Ort beschraenkt unter derselben Gesamtmenge die
moegliche Belegung an anderen Orten. Funktionsverlust kann mit einer
nachweisbaren raeumlichen Freigabe derselben Groesse verbunden werden.

Diese Rolle ist nicht automatisch Memory. Sie begruendet aber eine
verteilte Konkurrenz, die unabhaengige lokale Hystereseelemente ohne
gemeinsame Bilanz nicht besitzen.

### Warum die Familie nur bedingt offen bleibt

Erhaltung waehlt noch keine Bewegungsursache. Unbeantwortet bleiben:

- welche lokale Feldgroesse mit M konjugiert ist;
- wodurch Richtung und Vorzeichen des Flusses entstehen;
- ob reine Diffusion nur homogenisiert;
- wie M auf S wirkt, ohne Gain oder Kantengewicht zu sein;
- wie der gleichfoermige Materialzustand ohne Weltkraft stationaer bleibt und
  der getrennte Nullparameterarm die heutige Runtime exakt erhaelt;
- ob funktionale Rekonfiguration mehr ist als Phasentrennung oder
  Wave-Pinning.

Konservative Reaktions-Diffusions- und Cahn-Hilliard-artige Systeme koennen
bereits Polarisation, Grenzflaechen und Muster erzeugen. Diese Effekte bleiben
starke Baselines und duerfen nicht als MCM-Organisation interpretiert werden.

### Abgrenzung vom alten H2-Zweig

T3 nimmt keine fruehere H2-Gleichung wieder auf. Geschlossen bleiben:

- frei zugeordnete radiale Materialbewegung;
- positive Diffusion als Memory-Erklaerung;
- vorgegebene freie Energielandschaft mit Zielphasen;
- Oberflaechenmaterial als direktes Richtungsgewicht;
- memristive Kennlinie und feste Hystereseschleife;
- getrennte Bildungs-, Loesch- und Wiederbindungsregeln.

Neu ist nur die durch den Evidenzvertrag praezisierte Prueffrage, ob eine
gemeinsame konservierte Bilanz fuer verteilte Nichtseparierbarkeit eine
unabhaengige Traegerrolle bildet.

### Entscheidung

```text
T3-Rollenart:                      physikalisch eigenstaendig
konkrete MCM-Bewegungsursache:     fehlt
konkrete Feldrueckwirkung:         fehlt
T3 fuer einen Minimalvertrag:      bedingt offen
T3-Gleichung oder Implementierung: nicht zugelassen
```

## T4: variable Beziehungen oder Topologie

### Traegeridee

Langsame Geschichte veraendert Nachbarschaften, Kanten, Partnerzuordnungen,
Routing oder die Menge aktiver Feldorte.

### Projektkollision

Diese Familie kann verteilte Nichtseparierbarkeit unmittelbar erzeugen, weil
die relationale Anatomie selbst Geschichte traegt. Sie programmiert aber
genau die derzeit gesperrte Organisations- und Topologierolle:

- adaptive Kanten sind gespeicherte Beziehungen;
- Partner- oder Slot-IDs sind explizite Bindungen;
- Routing und Gewinnerlogik legen Auslesepfade fest;
- Entstehung und Loesung von Kanten benoetigen eine noch unbegruendete
  Lebenszyklusregel.

### Entscheidung

```text
T4: verboten
Grund: traegt gewuenschte Beziehung oder Topologie direkt in der Anatomie
```

T4 dient nur als Negativkontrolle.

## Gesamtvergleich

| Familie | eigene Traegerrolle | staerkste enge Baseline | Entscheidung |
|---|---|---|---|
| T1 S-vermittelte Ortszustaende | nein nach R1-Audit | lokale Hysterese plus Ein-Diffusor-RD | geschlossen |
| T2 nichtkonservativer L-Fluss | Transport ohne gemeinsame Ressource | Allen-Cahn / Zwei-Komponenten-RD | geschlossen |
| T3 konservative Umverteilung | endliche gemeinsame Menge und Ortskonkurrenz | Cahn-Hilliard / massenerhaltende RD | bedingt offen |
| T4 variable Beziehungen | explizite relationale Anatomie | adaptive Kanten/Topologie | verboten |

## Falsifikationsgrenze fuer T3

T3 wird bereits vor einer Gleichung geschlossen, wenn der naechste
Minimalvertrag keine Antworten auf diese Punkte geben kann:

1. Was ist die erhaltene dimensionslose Feldgroesse physikalisch?
2. Welche lokale Bilanz gilt auf der vorhandenen periodischen oder offenen
   MCM-Geometrie?
3. Welcher gleichfoermige Zustand ist funktional neutral?
4. Wie erreicht Weltgeschichte die Groesse nur ueber S, ohne sie zu erzeugen?
5. Welche inhaltsfreie lokale Konjugation kann Flussrichtung begruenden?
6. Wie wirkt die Verteilung additiv auf S statt als Gain oder Kante?
7. Welche Beobachtung unterscheidet Ressourcenverschiebung von Diffusion,
   Phasentrennung und Wave-Pinning?
8. Wie werden Erhaltung und Nichtnegativitaet bei Snapshot, Tausch,
   Permutation und Forschungsablation ausgewiesen?

Die Antwort `weil damit Memory entsteht` fuehrt zum sofortigen STOPP.

## Quellen

- S. M. Allen und J. W. Cahn,
  [A microscopic theory for antiphase boundary motion and its application to antiphase domain coarsening](https://doi.org/10.1016/0001-6160(79)90196-2),
  1979. Dient als physische Grenze fuer nichtkonservative
  Grenzflaechenbewegung und Phasenrelaxation.
- J. W. Cahn und J. E. Hilliard,
  [Free Energy of a Nonuniform System I](https://doi.org/10.1063/1.1744102),
  1958. Dient als konservierte Phasenfeld- und Energielandschaftsbaseline.
- Y. Mori, A. Jilkine und L. Edelstein-Keshet,
  [Wave-Pinning and Cell Polarity from a Bistable Reaction-Diffusion System](https://pmc.ncbi.nlm.nih.gov/articles/PMC2292363/),
  2008. Zeigt, dass Massenerhaltung, Bistabilitaet und unterschiedliche
  Diffusion bereits stabile verteilte Polarisation tragen koennen.

Die Auswahl von T3 fuer genau einen weiteren statischen Vertrag ist eine
Projektentscheidung. Die Quellen belegen kein MCM-Memory und keine
organische Feldorganisation.

## Bester naechster Schritt

Als naechstes wird ein **Minimalvertrag fuer eine konservierte begrenzte
Feldgroesse M** formuliert. Er muss ohne Bewegungs- oder Rueckwirkungsgleichung
festlegen:

1. Stoffrolle, Wertebereich, Gesamtbilanz und neutralen Gleichzustand;
2. zulaessige lokale S-M-Konjugation und verbotene Richtungszuweisungen;
3. additive M-zu-S-Kausalrolle ohne Gain, Kante oder Zielzustand;
4. korrekte konservative Tausch-, Permutations- und
   Neutralisierungsinterventionen;
5. Reduktion gegen Diffusion, Cahn-Hilliard, Wave-Pinning und globale
   Normierung.

Nur wenn dieser Vertrag nichtleer bleibt, darf danach eine kleine Zahl
konkreter konservativer Flussfamilien statisch verglichen werden.
