# W7-D: Statischer Vergleich dreier Substratfamilien

Stand: 2026-08-09

Entscheidung: `NO_NEW_FAMILY_TRANSPORT_BASELINE_REMAINS_ENGINEERING_PATH`

Arbeitsart: statischer Familienvergleich

Runtimeaenderung: nein

## Ausgangspunkt

W7-C bindet den fehlenden Funktionsgrad jenseits der linearen S1-B/B2-Spur:
bilanzierte lokale Verdichtung, funktionale Loesung ohne Reset,
Kapazitaetswiederverwendung und reziproke Wirkung auf spaetere
S-Feldaufnahme. W7-D vergleicht genau die drei dort benannten Familien.

Die Bewertung `ZULASSEN` bedeutet, dass eine Familie einen noch nicht durch
Projektbaselines erklaerten Funktionsgrad besitzt. `BASELINE` bedeutet, dass
die Familie technisch verwendbar, aber bereits durch eine bekannte enge
Mechanikklasse erklaert ist. `STOPP` bedeutet, dass sie den W7-C-Vertrag
strukturell nicht erfuellen kann oder eine gesperrte Architektur voraussetzt.

## Vergleichskriterien

Jede Familie wird gegen dieselben sieben Fragen bewertet:

1. Besitzt sie eine explizite endliche Ressourcenbilanz?
2. Kann lokale Verdichtung ohne Zaehler oder Ergebnisregel entstehen?
3. Kann weitere Feldgeschichte alte Wirkung ohne Reset funktional loesen?
4. Ist frei gewordene Kapazitaet anderswo kausal wiederverwendbar?
5. Entsteht die spaetere Wirkung aus demselben lokalen Substratzustand?
6. Bricht die Familie lineare Superposition aus ihrer Mechanik heraus?
7. Bleibt nach Abgleich mit den vorhandenen Pflichtbaselines ein neuer
   Funktionsgrad uebrig?

## D1: lokal konserviertes Transportmedium

### Technische Rolle

Eine nichtnegative endliche Groesse wird zwischen benachbarten Feldorten
lokal bilanziert verschoben. Lokale Zunahme erzwingt Abnahme innerhalb des
abgeschlossenen Budgets. Dadurch sind Ortskonkurrenz, Freisetzung und
Wiederverwendung technisch direkt darstellbar.

### Projektabgleich

Diese Familie ist nicht ungeprueft:

- T3 und der M-Minimalvertrag haben die konservierte Traegerrolle gebunden;
- K2/F3 hat Transport, Bilanz, Snapshot und S-Rueckwirkung implementiert;
- Lauf 192 hat die beobachtete Wirkung durch eine enge lineare gekoppelte
  Feldbaseline erklaert;
- Lauf 194 hat den alten Wirkungsverlust als passive Entwicklung statt als
  konkurrenzbedingte Verdrangung klassifiziert;
- S1-AB hat ein endliches lokal umverteilbares Kopplungsmedium als adaptive
  Mobilitaet beziehungsweise Standardmaterial eingeordnet.

Eine staerkere nichtlineare Transportregel koennte W7-C-Verhalten technisch
erzeugen. Ohne eine vorab unabhaengig begruendete Bewegungsursache waere sie
aber eine entworfene Materialregel, die gerade auf das gewuenschte Ergebnis
zugeschnitten wird.

### Entscheidung D1

```text
Ressourcenbilanz:                  ja
Loesung und Wiederverwendung:      technisch moeglich
neuer Funktionsgrad gegen K2/F3:   nein
MCM-spezifische Herleitung:        nein
Bewertung:                         BASELINE
```

D1 bleibt die staerkste transparente Engineering-Baseline. Es wird nicht als
neue Substratnatur zugelassen.

## D2: lokal deformierbare Kapazitaet

### Technische Rolle

Jeder Feldort besitzt eine eigene begrenzte Disposition, die durch lokale
Feldteilnahme veraendert wird und spaetere Aufnahme oder Weiterleitung
moduliert.

### Projektabgleich

H1/C1 hat genau diese Grundform bereits technisch getragen und zugleich auf
einen begrenzten lokalen Produktintegrator mit festem Leser reduziert. Eine
konstitutive Gegenvariable erweitert die Ausdrucksform, bleibt aber
Integrator-, Gain-, Hysterese- oder Erholungsbaseline.

Vor allem fehlt D2 als isolierter Familie das W7-C-Ressourcenledger:
Unabhaengige lokale Grenzen belegen weder Freisetzung noch eine kausale
Wiederverwendung derselben Kapazitaet an einem anderen Ort. Fuegt man
zwischenortlichen Austausch hinzu, wird D2 zu D1.

### Entscheidung D2

```text
lokale Begrenzung:                 ja
gemeinsame Ressourcenbilanz:       nein
ortsuebergreifende Wiederverwendung: nein
staerkste Erklaerung:              Integrator / Gain / Hysterese
Bewertung:                         BASELINE
```

D2 wird nicht als eigenstaendiger Kandidat weiterentwickelt.

## D3: verteilte S-vermittelte Substratkopplung

### Technische Rolle

Ortsgebundene langsame Zustaende lesen nur ihr lokales S. Das bestehende
raeumliche S-Feld vermittelt indirekt die Wechselwirkung zwischen diesen
Zustaenden; ein eigener Substrattransport wird nicht eingefuehrt.

### Projektabgleich

Diese Familie entspricht dem geschlossenen R1-/T1-Raum. Verteilte Effekte
sind moeglich, fallen aber auf lokale interne Zustandsdynamik unter einer
Ein-Diffusor-Reaktions-Diffusionsbaseline zurueck. Der S-Fluss transportiert
Feldwirkung, jedoch keine explizit bilanzierte Substratkapazitaet.

Damit kann D3 weder Freisetzung noch Wiederverwendung derselben endlichen
Ressource an einem anderen Ort nachweisen. Ein zusaetzlicher L-Eigenfluss
wuerde die Familie in D1 oder in die bereits geschlossene nichtkonservative
Diffusionsfamilie ueberfuehren.

### Entscheidung D3

```text
verteilte Feldwirkung:             moeglich
explizite Substratbilanz:          nein
Kapazitaetswiederverwendung:       nicht nachweisbar
staerkste Erklaerung:              R1 / Ein-Diffusor-RD
Bewertung:                         BASELINE
```

D3 wird nicht als eigenstaendiger Kandidat weiterentwickelt.

## Gesamtvergleich

| Familie | W7-C-Ressourcenfunktion | staerkste Projektbaseline | Entscheidung |
| --- | --- | --- | --- |
| D1 konserviertes Transportmedium | vollstaendig darstellbar | K2/F3, lineares gekoppeltes Feld, Standardmaterial | `BASELINE` |
| D2 lokal deformierbare Kapazitaet | keine ortsuebergreifende Wiederverwendung | C1/H1, Integrator, Gain, Hysterese | `BASELINE` |
| D3 S-vermittelte Kopplung | keine explizite gemeinsame Kapazitaet | R1/T1, Ein-Diffusor-RD | `BASELINE` |

Keine Familie erhaelt `ZULASSEN`. Das ist kein Nachweis technischer
Unmoeglichkeit. Es bedeutet, dass der aktuelle Projektbestand keine neue
Substratnatur herleitet, die zugleich W7-C erfuellt und von den vorhandenen
engen Baselines getrennt ist.

## Entwicklungsfolgerung

Zwei Ziele muessen ab jetzt sauber getrennt bleiben:

1. **MCM-spezifischer Forschungsbefund:** derzeit kein zugelassener neuer
   Substratkandidat.
2. **Transparente Systementwicklung:** Ein konserviertes Transportmedium kann
   weiterhin als offen konstruierte Engineering-Baseline verwendet werden,
   um die benoetigte Substratfunktion technisch zu untersuchen.

Ein positiver spaeterer Funktionsbefund wuerde dann die gekoppelte
MCM-Materialarchitektur charakterisieren. Er wuerde weder beweisen, dass die
Materialregel aus MCM folgt, noch bereits Memory, Feldzeitverdichtung oder KI
belegen.

## Nicht erneut zu oeffnen

- K2/F3 nur durch staerkere Parameter oder lockere Toleranz retten;
- eine lokale Saettigung als Kapazitaetswiederverwendung bezeichnen;
- S-vermittelte Muster als neue Substratressource interpretieren;
- nichtlineare Transportrichtung nach gewuenschtem Lebenszyklus waehlen;
- Standardmaterial unter einer MCM-spezifischen Bezeichnung erneut
  einreichen.

## Entscheidung

```text
neue zugelassene Substratfamilie:  keine
staerkste technische Familie:      konserviertes Transportmedium
Status dieser Familie:             transparente Engineering-Baseline
konkrete neue Gleichung:           nein
Implementierung:                   nein
Forschungslauf:                    nein
Memory-, Feldzeit- oder KI-Claim:  nein
```

## Verwendete Projektquellen

- [W7-C Funktions- und Ressourcenvertrag](W7C_FUNKTIONS_UND_RESSOURCENVERTRAG_JENSEITS_LINEARER_SPUR.md)
- [H1 Kausalvertrag](H1_LOKAL_DEFORMIERBARE_FELDAUFNAHME_KAUSALVERTRAG.md)
- [H2 Bestandsaudit](H2_BEGRenzTES_UMVERTEILBARES_FELDMEDIUM_BESTANDSAUDIT.md)
- [Vergleich der Traegerfamilien](VERGLEICH_TRAEGERFAMILIEN_VERTEILTE_NICHTSEPARIERBARKEIT.md)
- [R1 Abschlussaudit](MINIMALVERTRAG_ADDITIVES_KONSTITUTIVES_GEGENFELD.md)
- [Lauf 192 Baselinevergleich](forschung/LAUF_192_K2_F3_E3_BASELINEVERGLEICH.md)
- [Lauf 194 Funktionsverlust und Wiederverwendung](forschung/LAUF_194_K2_B_F3_FUNKTIONSVERLUST_UND_WIEDERVERWENDUNG.md)
- [S1-AB Kopplungsmediumaudit](S1AB_AUDIT_ENDLICHES_LOKAL_UMVERTEILBARES_KOPPLUNGSMEDIUM.md)

## Bester naechster Schritt

W7-E bindet einen transparenten Engineering-Entscheid fuer die weitere
Substratentwicklung. Er legt fest, welche bereits bekannte konservierte
Transportbaseline als unveraenderter Ausgangspunkt dient und welche genau
eine neue, ergebnisunabhaengig begruendete Materialeigenschaft vor einer
Gleichung erforderlich waere. W7-E implementiert und testet noch nichts.
