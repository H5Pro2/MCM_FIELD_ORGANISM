# Minimal- und Reduzierbarkeitsvertrag fuer ein additives Gegenfeld

## Status

```text
Pruefart:                           statischer Rollen- und Reduzierbarkeitsaudit
lokale Zustandsrollen:              S plus skalares ortsgebundenes L
additive L-zu-S-Wirkung:            physikalisch formulierbar
eigenstaendige neue Naturfunktion:  nicht nachgewiesen
R1-Kandidatenraum:                  geschlossen
konkrete Gleichung:                 nicht zugelassen
Implementierung oder Versuch:       nicht zugelassen
```

## Forschungsfrage

Kann ein begrenztes, skalares und ortsgebundenes L als additives
konstitutives Gegenfeld auf S wirken, ohne vollstaendig auf eine klassische
interne Gegenvariable, dynamische Erholung, glatte Hysterese oder einen
lokalen Oszillator zurueckzufallen?

Die Frage betrifft nur die Mechanikklasse. Sie fragt nicht, ob bekannte
interne Variablen Geschichte tragen koennen. Das koennen sie. Entscheidend
ist, ob die hier geoeffnete Form eine andere, fuer das MCM-Vorhaben
begruendbare Naturfunktion besitzt.

## 1. Minimal zulaessige Rollenform

Das Gegenfeld muesste alle bisherigen R1-Grenzen gleichzeitig einhalten:

- L liegt am selben Feldort wie S;
- nur S traegt den bestehenden raeumlichen Feldfluss;
- L liest keine Rezeptorrohdaten, Labels, IDs oder eigenen Kanten;
- S und L werden atomar aus demselben abgeschlossenen Vorzustand berechnet;
- L wirkt als additiver innerer Beitrag auf S;
- L skaliert weder Eingang noch Feldfluss, Mobilitaet oder Zeitkonstante;
- dieselbe unveraenderte lokale Naturform gilt in jedem Verlauf;
- es gibt keinen Schreib-, Abruf-, Konsolidierungs- oder Loeschmodus.

Abstrakt bleibt damit nur:

```text
S-Fortsetzung = bestehende S-Feldwirkung + lokaler Gegenbeitrag aus S und L
L-Fortsetzung = lokale Entwicklung aus demselben S-L-Vorzustand
```

Dies ist eine Rollenbeschreibung und noch keine Gleichung.

## 2. Was die additive Rolle tatsaechlich leistet

Eine additive L-Wirkung ist gegenueber Gain und Mobilitaet kausal sauber
abgrenzbar. Bei gleichem Rezeptor- und Nachbarschaftsbeitrag kann ein
unterschiedlicher L-Zustand einen unterschiedlichen internen S-Beitrag
verursachen, ohne eine aeussere Wirkung zu multiplizieren.

Diese Abgrenzung begruendet jedoch keine neue Mechanikklasse. In klassischen
konstitutiven Modellen wird genau diese Rolle bereits durch eine interne
Rueckstell- oder Gegenvariable beschrieben. Deren Zustand entwickelt sich
mit der Belastungsgeschichte und traegt additiv zur gegenwaertigen Antwort
bei.

Die physische Rolle ist daher nicht leer, aber bereits bekannt:

```text
additives Gegenfeld
= skalarer interner konstitutiver Zustand mit additivem Antwortbeitrag
```

## 3. Reduktion gegen die engen Pflichtbaselines

### Lineare interne Gegenvariable

Ist Bildung und Rueckwirkung linear oder affin, zerfaellt das gekoppelte
S-L-System in feste Moden. Die Form ist eine Leaky-, viskoelastische oder
gedaempft oszillatorische Baseline.

```text
Entscheidung: kein Rest
```

### Dynamische Erholung

Wird L durch S beziehungsweise lokale Aktivitaet aufgebaut und durch einen
zustandsabhaengigen Ruecklauf abgeschwaecht, entsteht eine klassische interne
Gegenvariable mit dynamischer Erholung. Unterschiedliche Aufbau- und
Entlastungsverlaeufe, Saettigung und richtungsabhaengige Nachwirkung sind
bereits innerhalb dieser Klasse moeglich.

```text
Entscheidung: kein Rest
```

### Glatte Hysterese

Wird L pfad- und richtungsabhaengig fortgesetzt, waehrend sein additiver
Beitrag die S-Antwort veraendert, entsteht eine differentielle
Hystereseklasse. Glatte Formulierungen koennen bereits Asymmetrie,
Degradation, Pinching und unterschiedliche Schleifenformen darstellen.

```text
Entscheidung: komplexe Schleifen oder Pfadabhaengigkeit sind kein Rest
```

### Lokaler Oszillator

Tauschen S und L vorwiegend Phase oder Modenamplitude aus, ist der
Gegenbeitrag eine Rueckstellkraft eines lokalen Oszillators. Dissipation
macht daraus eine gedaempfte Resonanzbaseline; fehlende Dissipation erhaelt
die Mode, loest sie aber nicht funktional um.

```text
Entscheidung: kein Rest
```

## 4. Warum formale Ausschluesse keinen neuen Kandidaten erzeugen

Man koennte die vier Baselines durch zusaetzliche Bedingungen formal
ausschliessen, etwa durch:

- Nichtlinearitaet und Nichtseparierbarkeit;
- Abhaengigkeit von lokaler Verlaufsordnung und Verweildauer;
- fehlende feste Hystereseschleife;
- fehlende autonome periodische Bahn;
- nichtmonotone, aber begrenzte Zustandsentwicklung.

Diese Negativbedingungen benennen jedoch keine unabhaengige physische
Funktion. Nach ihrem Ausschluss bleibt lediglich eine beliebige begrenzte
nichtlineare interne Zustandsdynamik. Sie kann komplexe Transienten erzeugen,
erklaert aber nicht, welches neue lokale Naturprinzip L verkoerpert.

Eine solche Restklasse waere zu breit, um vor einer Gleichungswahl
falsifizierbar zu sein. Die Auswahl einer konkreten Nichtlinearitaet waere
dann nur Funktionssuche, bis ein gewuenschtes Verhalten erscheint.

## 5. Lebenszyklusgrenze

Alle engen Gegenvariablenklassen koennen Teilaspekte des spaeter geforderten
Verlaufs zeigen:

- Aufbau eines geschichtsabhaengigen L-Zustands;
- spaetere additive Wirkung bei gleichem S;
- Abschwaechung oder Ueberschreibung;
- erneute Anregung in eine andere Richtung.

Gerade deshalb duerfen diese Beobachtungen nicht automatisch als organische
Praegung, Loesung oder Wiederpraegung bezeichnet werden. Ohne eine weitere
unabhaengige Naturfunktion beschreiben sie den vorgegebenen Lebenszyklus der
jeweiligen Relaxations- oder Hysteresegleichung.

## 6. Dimensions- und Architekturfolgerung

Die Schliessung beweist nicht, dass ein skalares L mathematisch zu wenig
Zustaende speichern kann. Ein Skalar kann sehr komplexe Geschichte tragen.

Der Mangel ist funktional:

> Fuer den einen zusaetzlichen skalaren Freiheitsgrad wurde keine
> eigenstaendige physische Rolle jenseits bekannter Register-, Gegenvariablen-
> und Hysteresefunktionen begruendet.

Daraus folgt nicht automatisch, dass ein zweiter Skalar, L-Eigenfluss oder
adaptive Kanten eingefuehrt werden duerfen. Vor jeder Erweiterung muss erst
bestimmt werden, welche unabhaengige Kausalrolle im geforderten
Memory-Lebenszyklus tatsaechlich fehlt.

## 7. Stopplinien

Der additive-Gegenfeld-Zweig darf nicht durch folgende Umbenennungen wieder
geoeffnet werden:

1. Backstress oder Rueckstellkraft wird als innerer Kontext bezeichnet.
2. Hystereseschleife wird als Praegung und Loesung bezeichnet.
3. dynamische Erholung wird als organisches Vergessen bezeichnet;
4. Saettigung wird als Feldzeitverdichtung bezeichnet;
5. komplexer Transient wird als entstandene Organisation bezeichnet;
6. eine frei gesuchte Nichtlinearitaet wird nach ihrem Ergebnis ausgewaehlt;
7. ein weiterer Zustand wird ohne eigene physische Kausalrolle hinzugefuegt.

## Forschungsentscheidung

Das begrenzte additive konstitutive Gegenfeld ist als physische Rollenart
formulierbar, aber nicht als eigenstaendige R1-Naturfunktion begruendet. Es
faellt auf bekannte interne Zustandsvariablenklassen zurueck oder wird nach
deren Ausschluss zu einer unbestimmten beliebigen Nichtlinearitaet.

```text
additive L-zu-S-Kausalrolle:         vorhanden
neuer Mechanikrest:                  nein
R1 konkretisieren:                  nein
R1-Gleichung entwickeln:            nein
R1 implementieren oder testen:       nein
R1 als Baselinefamilie behalten:     ja
```

R1 wird damit als primaerer Entwicklungsweg geschlossen. Die bisherigen
R1-Dokumente bleiben als Herleitung und als Baselineordnung erhalten.

## Quellen

- G. M. Eggert und P. R. Dawson,
  [On the use of internal variable constitutive equations in transient forming processes](https://doi.org/10.1016/0020-7403(87)90045-2),
  1987. Belegt die allgemeine konstitutive Rolle interner Zustandsvariablen.
- A. G. C. L. E. Shutov und R. Kreissig,
  [A large deformation theory for rate-dependent elastic-plastic materials with combined isotropic and kinematic hardening](https://www.sciencedirect.com/science/article/abs/pii/S0749641908001757),
  2008. Dient zur Einordnung einer entgegenwirkenden internen Backstress-Rolle
  und ihrer dynamischen Erholung.
- M. Heredia-Perez, D. A. Alvarez und D. Bedoya-Ruiz,
  [A State-of-the-Art Review of the Bouc-Wen Class Model of Hysteresis](https://doi.org/10.1007/s11831-025-10301-z),
  2026. Zeigt die grosse Ausdrucksbreite glatter differentieller
  Hysteresemodelle und dient deshalb als starke Gegenbaseline.

Die Uebertragung dieser Quellen auf die MCM-Rollen ist eine Schlussfolgerung
dieses Audits. Es wird keine Materialgleichung als MCM-Mechanik uebernommen.

## Bester naechster Schritt

Als naechstes wird ein **funktionaler Anforderungsrang-Audit des
Memory-Lebenszyklus** erstellt. Er leitet noch ohne neue Architektur ab:

1. welche voneinander unabhaengigen Kausalwirkungen Bildung, spaetere Wirkung,
   funktionale Loesung und andere Wiederpraegung mindestens benoetigen;
2. welche davon S, H und ein skalares L bereits darstellen koennen;
3. ob der fehlende Rang lokal-dimensional, raeumlich-konservativ oder durch
   eine andere physische Rolle begruendet ist;
4. welche kleinste Architekturfrage danach ueberhaupt wieder geoeffnet werden
   darf.

Erst dieser Audit darf begruenden, ob mehr lokale Dimension, eine begrenzte
Umverteilung oder ein anderer Substrattyp untersucht wird.
