# F3: Existenz- und Reduzierbarkeitsaudit

## Status

```text
Auditart:                         statisch / mathematisch
Passivitaet plus Nichtkontraktion: moeglich
minimale Zustandsdimension:        bereits skalar moeglich
eigenstaendiger F3-Mechanismus:    nicht nachgewiesen
Rest ausserhalb fester Rekurrenz:  unter aktueller Definition leer
F3 als eigene Mechanik:            geschlossen
Runtime-Aenderung:                 nein
```

## Prueffrage

Der F3-Minimalvertrag fragt, ob es eine lokale reziproke, passive und
zeitweilig inkrementell nichtkontraktive S-L-Dynamik gibt, deren funktionale
Klasse nicht vollstaendig auf nichtnormale Rekurrenz, Oszillation, Hysterese,
Gain oder Mobilitaet reduziert werden kann.

Der Audit trennt zwei Fragen:

1. Sind Passivitaet und zeitweilige Nichtkontraktivitaet mathematisch
   miteinander vereinbar?
2. Entsteht dadurch eine eigenstaendige digitale Mechanik ausserhalb einer
   festen Zustandsrekurrenz?

Die erste Frage ist positiv, die zweite unter der gegenwaertigen breiten
Baseline-Definition negativ zu beantworten.

## 1. Begriffsgrenze

### Passivitaet

Passivitaet beziehungsweise Dissipativitaet beschraenkt eine Speicher- oder
Bilanzgroesse entlang eines einzelnen Verlaufs. Sie sagt nicht automatisch,
dass zwei verschiedene Verlaeufe unter gleicher weiterer Anregung aufeinander
zulaufen.

### Inkrementelle Kontraktion

Kontraktion ist eine Eigenschaft von Abstaenden zwischen benachbarten
Verlaeufen in einer festgelegten Metrik. Sie ist damit staerker und anders
gerichtet als eine reine Energie- oder Passivitaetsaussage.

Die Literatur trennt klassische Dissipativitaet von differentieller
Dissipativitaet und verbindet letztere mit inkrementeller Stabilitaet. Diese
Trennung bestaetigt, dass passive Einzeldynamik nicht automatisch
inkrementell kontraktiv sein muss.

## 2. Existenz bereits im skalaren Fall

Ein skalarer passiver Zerfall kann in einem Bereich zeitweilig
nichtkontraktiv sein. Als reine Gegenkonstruktion, nicht als MCM-Kandidat,
genuegt beispielsweise:

```text
dx/dt = -x / (1 + x^2)
```

Mit der Speichergroesse

```text
V(x) = x^2 / 2
```

gilt ohne Zufuhr:

```text
dV/dt = -x^2 / (1 + x^2) <= 0
```

Der Verlauf ist damit begrenzt und dissipativ. Die lokale Steigung des
Vektorfelds lautet jedoch:

```text
df/dx = (x^2 - 1) / (1 + x^2)^2
```

Fuer `|x| > 1` ist sie positiv. Nahe skalare Verlaeufe koennen dort
zeitweilig auseinanderlaufen, obwohl jeder einzelne Verlauf Energie abbaut.

### Reduktion

Dieselbe Form ist exakt schreibbar als:

```text
dx/dt = -m(x) * x
m(x)  = 1 / (1 + x^2)
```

Sie ist damit eine zustandsabhaengige Mobilitaet beziehungsweise variable
Relaxationsrate. Der kleinste Existenzbeleg faellt direkt auf die bereits
geschlossene Familie F2 zurueck.

### Folgerung zur Dimension

Eine Dimension genuegt fuer die formale Vereinbarkeit von Passivitaet und
zeitweiliger Nichtkontraktivitaet. Eine reziproke S-L-Rollenverteilung
benoetigt zwar mindestens zwei funktionale Komponenten, schafft dadurch aber
noch keine neue mathematische Klasse.

## 3. Zweidimensionale Minimalfaelle

### Nichtnormale lineare Dynamik

Eine stabile lineare Dynamik mit nichtorthogonalen Moden kann in einer
gewaehlten euklidischen Norm starke transiente Verstaerkung zeigen, obwohl
alle Eigenmoden asymptotisch zerfallen.

Fuer eine Hurwitz-stabile lineare Matrix existiert zugleich eine positive
quadratische Lyapunov-Metrik, in der der Verlauf kontraktiv beschrieben
werden kann. Die beobachtete Nichtkontraktivitaet kann daher von der
Metrikwahl abhaengen.

Unabhaengig von der Metrik bleibt dieser Fall eine feste lineare Rekurrenz und
damit die bereits ausgeschlossene C1-Baseline.

### Reziproker Oszillator

Zwei gekoppelte Rollen koennen eine konservative oder schwach dissipative
Schwingung tragen. Abstand, Phase oder Richtung bleiben erhalten oder bauen
sich langsam ab.

Das erzeugt innere Zeitordnung und Nachwirkung, aber keine eigenstaendige
strukturveraendernde Klasse. Der Fall ist die C3-Oszillator- und
Viskoelastikbaseline.

### Mehrere Ruhelagen

Mehrere stabile oder metastabile Lagen koennen Geschichte langfristig
unterscheiden. Die moeglichen Lagen und ihre Trennbereiche liegen dann jedoch
im festen Vektorfeld. Der Fall reduziert auf Attraktor oder Hysterese und
damit auf F1.

## 4. Hoehere und nichtlineare Zustaende

Mit weiteren lokalen Freiheitsgraden sind komplexere transiente
Verstaerkung, nichtnormale Richtungswechsel, chaotische Abschnitte und
zustandsabhaengige lokale Geometrien moeglich.

Keine dieser Eigenschaften hebt jedoch allein die Reduktion auf:

- gespeicherte lokale Skalierung ist Gain oder Mobilitaet;
- gespeicherte Richtung ist Metrik, Routing oder adaptive Kante;
- mehrere bestandsfaehige Bereiche sind Attraktor oder Hysterese;
- konservierte Richtungen sind Oszillator- oder Phasenmoden;
- komplexe begrenzte Transienten sind nichtlineare feste Rekurrenz;
- Chaos ist weder Memory noch entwickelte Organisation.

Eine hoehere Dimension vergroessert den darstellbaren Dynamikraum, liefert
aber kein unabhaengiges Entstehungsprinzip.

## 5. Allgemeiner Reduktionssatz fuer die Projektgrenze

Jede endliche deterministische digitale lokale Naturform besitzt nach
Aufnahme aller internen Variablen in den Gesamtzustand die Form:

```text
X_(n+1) = F(X_n, U_n, dt_n)
```

Dabei enthaelt `X` schnelle und langsame lokale Rollen, `U` den zulaessigen
lokalen Welt- und Feldkontakt und `F` die unveraenderte lokale Updateform.

Auch wenn sich aus Teilsicht die effektive Antwort, Landschaft oder
Kopplungsform veraendert, bleibt das Gesamtsystem eine feste Rekurrenz ueber
dem erweiterten Zustand.

Das ist keine Besonderheit klassischer KI und kein Mangel der MCM. Es ist die
notwendige Form jeder endlichen deterministischen digitalen Physik.

### Konsequenz

Wenn `feste Rekurrenz` als Baseline jede feste endliche Zustandsfortschreibung
umfasst, kann keine digitale F3-Hypothese ausserhalb dieser Baseline liegen.
Eine gleich budgetierte Baseline mit derselben Zustandsdimension und einer
beliebigen Updatefunktion kann den Kandidaten definitionsgemaess identisch
abbilden.

Der verlangte nichtreduzierbare Rest ist unter dieser Definition leer.

## 6. Ergebnis der vier Auditfragen

| Frage | Ergebnis | Begruendung |
|---|---|---|
| minimale Dimension | skalar fuer formale Vereinbarkeit; mindestens zwei Rollen fuer S-L | Skalarfall reduziert auf Mobilitaet |
| Passivitaet plus Nichtkontraktion | ja | Einzelverlaufsbilanz und Verlaufsabstand sind verschiedene Eigenschaften |
| kleinste Formen jenseits der Baselines | nein | Mobilitaet, nichtnormale Rekurrenz, Oszillator oder Attraktor decken sie ab |
| eigenstaendiger F3-Raum | nein unter aktueller Rekurrenzdefinition | jede endliche feste Digitalphysik ist eine Zustandsrekurrenz |

## 7. Forschungsentscheidung

F3 wird als eigenstaendige strukturveraendernde Mechanik geschlossen. Die
Eigenschaft `zeitweilig inkrementell nichtkontraktiv` bleibt als spaeteres
Analysekriterium zulaessig, begruendet aber keine eigene Naturklasse.

```text
F3-Existenz als Dynamikeigenschaft: ja
F3 als neue Mechanikklasse:        nein
F3-Gleichung entwickeln:           nein
F3 implementieren:                 nein
```

Diese Schliessung bedeutet nicht, dass das MCM-Vorhaben unmoeglich ist. Sie
zeigt eine unbrauchbar breite Verbotsdefinition im bisherigen
Forschungsrahmen.

## 8. Notwendige methodische Korrektur

Die Projektgrenze muss zwei Bedeutungen von Rekurrenz unterscheiden.

### Unvermeidbare digitale Naturrekurrenz

Zulaessig sein muss eine feste, lokale, symmetrische und inhaltsfreie
Updateform. Ohne sie kann keine digitale MCM-Physik existieren.

Fest sein darf die allgemeine Naturgesetzlichkeit. Entstehen muessen die
konkrete Zustandsbelegung, Feldform, Lebensdauer, spaetere Wirkung und
Umbildung unter Weltgeschichte.

### Verbotene vorprogrammierte Organismusfunktion

Verboten bleiben Rekurrenzen, deren Variablen oder Updatezweige bereits die
gesuchte Funktion kodieren, insbesondere:

- Objekt-, Episoden-, Partner- oder Clusteridentitaeten;
- Zielantwort, Reward, Loss oder Solltopologie;
- gespeicherte Vorlage mit festem Leser;
- besondere Schreib-, Konsolidierungs- oder Loeschphase;
- Wiederholungszaehler, Ablaufzeit oder Bindungsschwelle;
- fest zugewiesene Memory-Slots oder adaptive Beziehungen.

### Sinnvolle Pflichtbaselines

Pflichtbaselines duerfen nicht `jede beliebige feste Rekurrenz` sein. Sie
muessen konkrete einfachere Funktionsklassen bezeichnen:

- lineare und nichtnormale lineare Dynamik;
- Leaky-Spuren und Integratoren;
- Oszillatoren und feste Resonanzmoden;
- feste Hysterese und Attraktorlandschaften;
- adaptive Gains und Mobilitaeten;
- gleich dimensionierte, aber strukturell reduzierte Ablationen.

Nur gegen solche vorregistrierten, engeren Klassen ist ein Kandidat
wissenschaftlich unterscheidbar.

## 9. Reichweite der Korrektur

Die Korrektur lockert keine Verbote fuer Labels, Ziele, Memory-Inhalte oder
Lebenszyklusregeln. Sie entfernt nur die logisch unmoegliche Forderung, eine
endliche digitale Naturphysik duerfe keine feste Gesamtzustandsrekurrenz
sein.

Danach kann erneut untersucht werden, ob eine inhaltsfreie lokale
MCM-Naturform konkrete Organisation aus Weltkontakt entstehen laesst. Der
positive Befund waere die nicht durch einfachere Baselines erklaerte
Trajektorie und ihr kontrollierter Lebenszyklus, nicht die Abwesenheit einer
Updategleichung.

## Quellen

- W. Lohmiller und J.-J. E. Slotine,
  [On Contraction Analysis for Non-linear Systems](https://doi.org/10.1016/S0005-1098(98)00019-3),
  Automatica 34(6), 1998. Grundlage fuer die differentielle Betrachtung der
  Konvergenz benachbarter Verlaeufe.
- F. Forni und R. Sepulchre,
  [On differentially dissipative dynamical systems](https://arxiv.org/abs/1305.3456),
  2013. Trennt klassische Dissipativitaet von differentieller beziehungsweise
  inkrementeller Dissipativitaet.
- L. N. Trefethen, A. E. Trefethen, S. C. Reddy und T. A. Driscoll,
  [Hydrodynamic Stability Without Eigenvalues](https://people.maths.ox.ac.uk/trefethen/publication/PDF/1993_57.pdf),
  Science 261, 1993. Zeigt transiente lineare Verstaerkung durch
  Nichtnormalitaet trotz asymptotisch stabiler Eigenmoden.

Die konkrete skalare Gegenkonstruktion und der allgemeine digitale
Reduktionsschluss sind Ableitungen dieses Audits, keine aus den Quellen
uebernommenen MCM-Behauptungen.

## Bester naechster Schritt

Als naechstes wird ein **Korrekturvertrag zur digitalen Naturrekurrenz**
erstellt. Er muss projektweit verbindlich trennen:

1. unvermeidbare und zulaessige feste lokale Naturgesetzlichkeit;
2. verbotene vorprogrammierte Organismusfunktion;
3. enge, falsifizierbare Pflichtbaselineklassen;
4. Eigenschaften, die ausschliesslich aus Weltgeschichte entstehen muessen.

Erst danach darf ein neuer konstitutiver Kandidatenraum geoeffnet werden.
