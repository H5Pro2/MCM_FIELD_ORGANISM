# W7-C: Funktions- und Ressourcenvertrag jenseits der linearen Spur

Stand: 2026-08-09

Entscheidung: `FUNCTIONAL_RESOURCE_GAP_BOUND`

Arbeitsart: statischer Architektur- und Zulassungsvertrag

Runtimeaenderung: nein

## Ausgangspunkt

W7-B hat den vorhandenen S1-B-Pfad als lineare reziproke B2-Referenz
bestimmt. Der R8/C8-Unterschied ist technisch real, wird aber vollstaendig
durch diese lineare Zweizeitendynamik erklaert. Weitere Auswertung derselben
Spur kann den fehlenden Freiheitsgrad nicht erzeugen.

W7-C bindet deshalb vor jeder neuen Gleichung den kleinsten funktionalen und
ressourcenbezogenen Abstand zur Referenz. Es behauptet weder, dass ein
solcher Kandidat bereits existiert, noch dass seine spaetere Wirkung Memory
waere.

## Forschungsfrage

Welche minimale, lokale und homogene Substratfunktion fehlt S1-B/B2, damit
wiederholte Feldteilnahme eine begrenzte lokale Disposition veraendern,
weitere Feldgeschichte diese Wirkung wieder funktional loesen und die dabei
frei werdende Kapazitaet an anderer Stelle erneut beansprucht werden kann?

## Gebundener Funktionsunterschied

Ein spaeterer Kandidat muss alle folgenden Eigenschaften gemeinsam tragen:

1. **Nichtlineare Geschichtsabhaengigkeit:** Die Antwort auf zusammengesetzte
   Kontakte darf nicht als Summe oder feste Faltung der Einzelantworten
   darstellbar sein.
2. **Lokale Verdichtung als Messbegriff:** Wiederholte lokale Feldteilnahme
   muss die Verteilung einer endlichen technischen Substratkapazitaet lokal
   veraendern. `Verdichtung` bezeichnet nur diese messbare Konzentration,
   keine Cluster-, Bedeutungs- oder Memoryeinheit.
3. **Begrenzung aus Bilanz:** Lokale Zunahme muss durch lokale Abgabe,
   bilanzierten Transport oder sinkende freie Kapazitaet begrenzt sein. Reset,
   Clipping und globale nachtraegliche Normierung sind unzulaessig.
4. **Funktionale Loesung:** Weitere neutrale oder konkurrierende
   Feldgeschichte muss eine fruehere Wirkung ohne Loeschsignal, feste
   Ablaufzeit oder Sonderphase abschwaechen oder funktionslos machen koennen.
5. **Kapazitaetswiederverwendung:** Eine nachweislich frei gewordene
   Kapazitaet muss unter derselben Mechanik an einem anderen lokalen
   Feldabschnitt erneut wirksam werden koennen.
6. **Reziproke Feldwirkung:** Nur der tatsaechliche lokale Substratzustand
   darf eine spaetere schnelle S-Feldaufnahme veraendern. Bildung und Lesen
   bleiben Teile derselben lokalen Wechselwirkung.
7. **Ein homogenes Regelwerk:** Bildung, Begrenzung, Loesung und erneute
   Beanspruchung verwenden an allen gleichartigen Feldorten dieselben
   inhaltsfreien Regeln und Parameter.

Diese Liste ist ein Funktionsvertrag. Sie legt weder Stoffart, Transportart,
Zahl zusaetzlicher Variablen noch eine Gleichung fest.

## Ressourcenvertrag

Ein Kandidat benoetigt ein explizites technisches Ressourcenledger. Vor der
Implementierung muessen mindestens angegeben werden:

- welche nichtnegative Groesse bilanziert wird;
- ob ihre Gesamtmenge lokal, nachbarschaftlich oder global abgeschlossen ist;
- welche lokalen Fluesse jede Zu- und Abnahme erklaeren;
- wie Neutralzustand und exakter Nullpfad definiert sind;
- wie Bilanzfehler, Negativitaet und unerlaubte Erzeugung gemessen werden;
- wie frei gewordene Kapazitaet von bloss abgeklungener Ausgangswirkung
  unterschieden wird.

Eine unabhaengige Saettigungsgrenze pro Ort erfuellt diesen Vertrag nicht,
wenn keine Kapazitaet freigesetzt und anderswo bilanziert wiederverwendet
werden kann. Eine global berechnete Gewinnerverteilung ist ebenfalls kein
lokaler Substratfluss.

## Kausal- und Darstellungsgrenze

Zulaessig sind nur lokale abgeschlossene Vorzustaende der bestehenden
MCM-Feldorte, lokale S-Feldgroessen und ein spaeter explizit begruendeter
Substratzustand. Weltkontakt erreicht das Substrat ausschliesslich ueber den
normalen Rezeptor- und S-Feldpfad.

Unzulaessig bleiben:

- Wiederholungs-, Episoden-, Objekt-, Quellen- oder Phasenzaehler;
- Labels, Reward, Loss, Sollantworten oder Zieltopologien;
- gespeicherte Rohbilder, Audiodaten, Merkmalsvektoren oder Embeddings;
- Cluster-IDs, Aehnlichkeitsschwellen oder externe Zuordnungslogik;
- verschiedene Regeln fuer Bildung, Loesung und Wiederbeanspruchung;
- Observerwerte als Ursache der Organismusentwicklung.

## Pflichtbaselines

Jeder spaetere Kandidat muss bei identischem Zustands-, Parameter-,
Praezisions- und Rechenbudget mindestens gegen folgende Klassen bestehen:

| Kennung | Gegenbaseline | Ausschlussgrund |
| --- | --- | --- |
| B0 | schneller MCM-Pfad ohne Substrat | prueft den exakten Nullpfad |
| B1 | einseitige lineare Leaky-Spur | prueft feste Faltung ohne Rueckwirkung |
| B2 | S1-B lineare reziproke Spur | prueft lineare Zweizeitenkopplung |
| B3 | begrenzter lokaler Integrator | prueft Saettigung ohne Ressourcenfluss |
| B4 | zustandsabhaengige Mobilitaet oder Gain | prueft nichtlineare Geschwindigkeit auf derselben Zustandsbahn |
| F3 | konservierter Traeger oder adaptive Leitfaehigkeit | prueft, ob nur bekanntes Materialverhalten neu benannt wurde |
| R0 | globale Normalisierung oder Gewinnerverteilung | prueft eine externe Kapazitaetssteuerung |

Baselinegleichheit ist ein gueltiges Negativergebnis. Sie verbietet nur den
Anspruch auf den hier gesuchten zusaetzlichen Funktionsgrad.

## Minimale spaetere Pruefstruktur

W7-C fuehrt keinen Lauf aus. Eine spaetere Vorregistrierung muss jedoch
mindestens vier getrennte Phasen mit kontrollierten Audio-, Video- oder
Browser-Testwelten binden:

1. gleich budgetierte wiederholte und kontinuierliche Bildungsgeschichte;
2. identische neutrale Probe nach externem S/H-Abgleich;
3. neutrale oder konkurrierende Geschichte ohne Reset;
4. erneute Beanspruchung eines anderen lokalen Feldabschnitts bei
   unveraendertem Gesamtbudget.

Erforderlich sind direkte Substratintervention, S-nach-Substrat-Ablation,
Substrat-nach-S-Ablation, Bilanzkontrolle und ein Tausch der lokalen
Testwelten. Ein spaeterer S-Unterschied allein genuegt nicht.

## Statische Stopplinien

Eine Kandidatenfamilie erhaelt vor Implementierung `STOPP`, wenn mindestens
eines gilt:

- sie variiert nur Relaxationsrate, Zeitkonstante oder Gain von S1-B/B2;
- ihre Nichtlinearitaet besteht nur aus lokaler Saettigung;
- sie setzt eine bevorzugte Bewegungsrichtung allein wegen des erwarteten
  Ergebnisses;
- sie benoetigt eine fest programmierte Potentialmulde, Attraktorkarte,
  Hysteresekurve oder Loeschphase;
- lokale Kapazitaet entsteht oder verschwindet ohne bilanzierte Ursache;
- Wiederverwendung wird nur aus sinkender S-Ausgabe abgeleitet;
- der Funktionsunterschied ist erst nach einer Memory-Interpretation
  sichtbar.

## Abgrenzung zu frueheren Zweigen

W7-C oeffnet H2 oder S1-AB nicht erneut. Deren Negativbefund bleibt gueltig:
Ein endliches umverteilbares Medium ist technisch moeglich, folgt aber nicht
eindeutig aus der bestehenden MCM-Mechanik und ist als adaptive Mobilitaet
oder Standardmaterial darstellbar.

Neu gebunden wird nur die fehlende Funktion gegen den inzwischen empirisch
sauber bestimmten W7-B-Nullpunkt. Eine spaetere Materialphysik darf offen als
Engineeringannahme gesetzt werden, muss dann aber ihre Bewegungsursache,
Bilanz und Gegenprognosen unabhaengig von einem gewuenschten Memoryergebnis
begruenden. Der Projektweg sucht keine verborgene Neuphysik.

## Entscheidung

```text
lineare Referenzgrenze:             durch W7-B bestimmt
minimaler Funktionsunterschied:     gebunden
Ressourcenledger:                   verpflichtend
Pflichtbaselines:                   gebunden
konkrete Substratnatur:             offen
konkrete Gleichung:                 nicht ausgewaehlt
Implementierung:                    nein
Forschungslauf:                     nein
Memory- oder Feldzeitbefund:        nein
```

`FUNCTIONAL_RESOURCE_GAP_BOUND` bedeutet: Das Projekt kennt nun die
kleinste nachzuweisende Funktion jenseits der linearen Spur. Es kennt noch
nicht die Mechanik, welche diese Funktion ohne einprogrammiertes Ergebnis
erzeugt.

## Bester naechster Schritt

W7-D vergleicht statisch genau drei deklarierte Kandidatenfamilien gegen
diesen Vertrag: ein lokal konserviertes Transportmedium, eine lokal
deformierbare Kapazitaet und eine verteilte S-vermittelte Substratkopplung.
Die Bewertung endet pro Familie mit `ZULASSEN`, `BASELINE` oder `STOPP`.
W7-D waehlt hoechstens eine Familie fuer eine spaetere Gleichungsarbeit und
implementiert noch nichts.
