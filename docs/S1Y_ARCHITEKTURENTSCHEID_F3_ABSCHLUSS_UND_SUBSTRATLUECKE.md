# S1-Y: Architekturentscheid zum F3-Abschluss und zur Substratluecke

Stand: 2026-08-09

Entscheidung: `F3_HISTORY_CARRIER_CONFIRMED_MEMORY_SUBSTRATE_GAP_REMAINS`

Formaler Forschungslauf: nein

## Forschungsfrage

Erzeugt der in S1-X replizierte nichtlineare Komponentenrest eine neue
funktionale Rolle gegenueber den bekannten F3- und linearen Mechaniken, oder
bleibt fuer den geforderten Lebenszyklus aus Bildung, Erhaltung, Wirkung,
Loesung und anderer Wiederpraegung eine Architekturluecke bestehen?

## Verwendete Projektquellen

- [Funktionaler Anforderungsrang des Memory-Lebenszyklus](FUNKTIONALER_ANFORDERUNGSRANG_MEMORY_LEBENSZYKLUS.md)
- [Richtungsentscheid Substrat vor Memorybefund](RICHTUNGSENTSCHEID_SUBSTRAT_VOR_MEMORYBEFUND.md)
- [S1-H Ursachenentscheid fuer eine neue Substratnatur](S1H_URSACHENENTSCHEID_NEUE_SUBSTRATNATUR.md)
- [S1-T statische F3-Beitragszerlegung](S1T_STATISCHE_F3_BEITRAGSZERLEGUNG_UND_OBSERVERVERTRAG.md)
- [S1-W passive Vollmatrixauswertung](S1W_PASSIVE_VOLLMATRIXAUSWERTUNG_F3_KOMPONENTENLEDGER.md)
- [S1-X gezielte Komponentenrest-Replikation](S1X_GEZIELTE_KOMPONENTENREST_REPLIKATION.md)

S1-Y verwendet ausschliesslich diese vorhandene Projektevidenz. Es gab keine
Ausfuehrung, keine Tests, keinen Browserstart und keine neue Datengewinnung.

## Funktionsbilanz des vorhandenen F3-Pfads

| Rolle | F3-Stand | Begrenzung |
|---|---|---|
| R1: weltbedingte Erreichbarkeit | technisch vorhanden | Weltkontakt veraendert M ueber das gemeinsame S-Feld. |
| R2: geschichtliche Unterscheidbarkeit | technisch vorhanden | Ein M-Unterschied kann nach schneller S/H-Angleichung verbleiben. |
| R3: spaetere Feldwirkung | technisch vorhanden | M wirkt ueber die feste reziproke Kopplung auf die weitere S-Trajektorie. |
| R4: Funktionsverlust und andere Wiederpraegung derselben Kapazitaet | nicht nachgewiesen | Passive Relaxation und erneute Wirkung sind kein kontrollierter vollstaendiger Austausch einer alten Wirkung durch eine andere. |

F3 ist damit ein transparenter, rueckwirkender Feld-Geschichtstraeger und eine
wertvolle Engineeringreferenz. Diese Einordnung ist enger als ein
Memorybefund.

## Einordnung des replizierten Komponentenrests

S1-X lokalisiert den Rest vollstaendig im bekannten Aktivierungsantrieb:

```text
A_i = -lambda * kappa
      * sum_j ((M_i + M_j) * (S_j - S_i))
```

Die Abweichung von der linearen Baseline entsteht aus der festen lokalen
Massengewichtung `(M_i + M_j)` statt `2*M_0`. Sie ist numerisch robust, fuegt
aber keine neue Zustandsrolle, keinen veraenderlichen Kopplungstyp und keine
neue Rueckwirkung hinzu. Die zusammengesetzte M-/Probeantwort blieb zuvor
linear erklaert.

Daraus folgt kein separates funktionales Kriterium. Weitere Aufloesung,
weitere Dosisstufen oder weitere Zerlegung derselben F3-Gleichung wuerden die
offene Architekturfrage nicht beantworten. Die Mikrolinie S1-I bis S1-X ist
damit abgeschlossen.

## Praezise verbleibende Architekturluecke

Es fehlt nicht einfach mehr Nichtlinearitaet, eine langsamere Uhr, ein
Wiederholungszaehler oder eine groessere M-Masse. Es fehlt eine begruendete
Moeglichkeit, dass lokale Feldteilnahme die **spaetere Umformbarkeit des
begrenzten Substrats selbst** veraendert.

Als noch darstellungsoffene Funktionsanforderung gilt:

> Eine lokale, endliche Substratkonfiguration muss durch normale
> Feldteilnahme so veraenderbar sein, dass sich ihre spaetere Aufnahme,
> Umlagerung oder Freigabe ebenfalls geschichtlich veraendert. Konkurrierende
> Weltgeschichte muss eine alte kausale Wirkung vollstaendig irrelevant
> machen und dieselbe begrenzte Faehigkeit fuer eine anders wirkende
> Konfiguration wieder verfuegbar machen koennen.

Diese Anforderung wird vorlaeufig **lokal mitentwickelte Umformbarkeit**
genannt. Der Name bezeichnet eine offene Funktion, keine fertige Mechanik.

F3 besitzt zwar eine zustandsabhaengige Massengewichtung. Seine
Konstitutivform, seine Kopplungsstaerke und seine zulaessigen Uebergaenge
bleiben jedoch unveraendert vorgegeben. Geschichte veraendert M, aber nicht
die Art, wie das Substrat spaeter durch Feldteilnahme umgeformt werden kann.

## Was daraus nicht folgt

Aus der Funktionsluecke folgt derzeit weder:

- eine zweite lokale Skalarvariable;
- eine adaptive Kante oder Zieltopologie;
- ein Schwellenwert, Slot, Zaehler oder Phasenautomat;
- ein eigener Zerfallstimer;
- eine konkrete Erhaltungs- oder Dissipationsgleichung;
- Memory, Lernen, Praegung, Vergessen oder Feldzeit als Befund.

Zuerst muss geprueft werden, ob bereits vorhandene Projektkandidaten diese
Funktionsrolle mit eigener lokaler Ursache und ohne vorprogrammierten
Lebenszyklus ueberhaupt darstellen koennen. Erst danach darf eine minimale
Zustandsdarstellung diskutiert werden.

## Zulassungstor fuer einen spaeteren Kandidaten

Ein Kandidat darf erst mechanisch formuliert werden, wenn statisch alle
folgenden Fragen beantwortet sind:

1. Welche lokale, inhaltsfreie Ursache veraendert seine spaetere
   Umformbarkeit?
2. Welche endliche Ressource oder Bilanz begrenzt diese Aenderung?
3. Wie wirkt die veraenderte Umformbarkeit ueber denselben normalen Feldpfad
   zurueck?
4. Wie kann konkurrierende normale Weltgeschichte die alte Wirkung ohne Reset
   funktionslos machen?
5. Warum erklaeren F3, lineare Kopplung, Leaky-Spur, lokale Hysterese und feste
   Reaktions-Diffusionsdynamik dieselbe Wirkung nicht gleichwertig?
6. Welche verteilte Intervention trennt den Kandidaten von einer Summe
   unabhaengiger lokaler Spuren?

Fehlt eine Antwort, wird keine Gleichung und keine Runtime-Erweiterung
zugelassen.

## Aussage- und Stopplinie

- F3 bleibt als Engineeringreferenz und Pflichtbaseline erhalten.
- Die F3-Komponentenverfeinerung wird nicht fortgesetzt.
- S1-Y oeffnet keine neue Physik und waehlt keine Architektur.
- R1 bis R3 werden nur als technische Kausalrollen des F3-Pfads bezeichnet.
- R4 und der gesamte Memory-Lebenszyklus bleiben offen.
- Feldzeit, innerer Kontext, Organisation, Semantik, Selbstregulation und KI
  bleiben unbelegt.
- Lauf 197 bleibt reserviert und unberuehrt.

## Bester naechster Schritt

S1-Z fuehrt eine rein statische Bestandssichtung vorhandener
Substratkandidaten und geschlossener Baselines gegen genau die hier definierte
lokal mitentwickelte Umformbarkeit durch. Ziel ist keine Formel, sondern eine
kleine Entscheidungsmatrix:

```text
vorhandener Kandidat
-> eigene lokale Ursache vorhanden?
-> endliche Ressource vorhanden?
-> veraendert er spaetere Umformbarkeit statt nur Zustand?
-> R4 prinzipiell pruefbar?
-> durch geschlossene Baseline bereits erklaert oder widerlegt?
```

Nur falls genau eine bereits begruendete Rolle dieses Tor besteht, darf danach
ein minimaler Mechanikvertrag vorbereitet werden. Andernfalls bleibt die
Substratimplementierung pausiert und die fehlende Naturursache wird offen
ausgewiesen.
