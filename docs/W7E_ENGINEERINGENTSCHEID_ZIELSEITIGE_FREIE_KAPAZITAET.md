# W7-E: Engineeringentscheid fuer zielseitige freie Kapazitaet

Stand: 2026-08-09

Entscheidung: `DESTINATION_AVAILABILITY_SELECTED_AS_TRANSPARENT_ENGINEERING_PROPERTY`

Arbeitsart: statischer Engineering- und Zulassungsentscheid

Runtimeaenderung: nein

## Ausgangspunkt

W7-D hat keine neue MCM-spezifische Substratfamilie zugelassen. Das lokal
konservierte Transportmedium D1 bleibt jedoch der technisch vollstaendigste
Traeger fuer Bilanz, Ortskonkurrenz und Kapazitaetswiederverwendung. W7-E
entscheidet, ob und wie dieser bekannte Materialpfad transparent fortgesetzt
werden darf.

Der bestehende K2/F3-Pfad ist quellenbegrenzt:

```text
gerichtete Abgabe haengt von der am Quellort vorhandenen M-Menge ab
```

Er bewahrt Nichtnegativitaet und Gesamtmasse. Seine lokale Obergrenze folgt
aber nur aus `M_i <= M_total`. Die freie Aufnahmekapazitaet des Zielortes ist
keine Ursache der Kantenrate. Dadurch bleibt der Transport im untersuchten
Korridor eine enge lineare gekoppelte Feldbaseline.

## Genau eine neue Engineering-Eigenschaft

W7-E bindet ausschliesslich:

> **Zielseitige Verfuegbarkeit:** Materieller Zufluss zu einem Feldort ist
> nur moeglich, soweit dieser Ort noch freie lokale Substratkapazitaet besitzt.

Jeder gleichartige Feldort erhaelt dieselbe feste, positive technische
Kapazitaet `C_site`. Fuer den vorhandenen lokalen Zustand `M_i` ist

```text
freie Kapazitaet V_i = C_site - M_i
```

`V_i` ist eine abgeleitete Groesse und kein zweiter gespeicherter Zustand.
W7-E fuehrt weder Slots, Partikelidentitaeten, Belegungslisten noch eine neue
Memoryschicht ein.

## Warum diese Eigenschaft sachlich zulaessig ist

Die Eigenschaft ist unabhaengig von einem spaeteren Memoryergebnis
formulierbar. Sie beschreibt endliche lokale Aufnahme eines technischen
Mediums:

- vorhandene Quellmenge begrenzt Abgabe;
- freie Zielkapazitaet begrenzt Aufnahme;
- eine lokale Zunahme bleibt kantenweise durch gleiche Abnahme bilanziert;
- vollstaendige Belegung sperrt weiteren Zufluss, ohne Clipping oder Reset;
- Abfluss erzeugt am selben Ort wieder freie Aufnahmekapazitaet.

Diese Regeln gelten auch dann, wenn niemals Praegung, funktionale Loesung
oder Memory beobachtet wird. Sie sind bekannte Ausschluss- beziehungsweise
Belegungsphysik und werden nicht als aus MCM hergeleitete Naturform
ausgegeben.

## Gebundene Kapazitaetsgrenze

W7-E waehlt noch keinen Zahlenwert. Eine spaetere mathematische Form muss
jedoch konstruktiv sichern:

```text
0 <= M_i <= C_site
Summe_i M_i = M_total
Anzahl_Orte * C_site > M_total
```

Die letzte Ungleichung stellt sicher, dass der homogene Ausgangszustand
freie Kapazitaet besitzt. `C_site` ist global, zeitlich konstant,
inhaltsfrei und an allen gleichartigen Feldorten identisch. Sie darf nicht
nach Weltquelle, Modalitaet, Phase oder Ergebnis angepasst werden.

## Direkte Gegenprognosen vor jedem Funktionsversuch

Die Eigenschaft ist nur dann technisch vorhanden, wenn eine spaetere
Gleichung bereits ohne Memoryauswertung folgende Unterschiede erzwingt:

1. Bei identischem Quellzustand und identischer S-Felddifferenz ist der
   Zufluss zu einem staerker belegten Ziel kleiner als zu einem freieren Ziel.
2. Bei `M_j = C_site` ist weiterer gerichteter Zufluss nach j exakt null.
3. Abfluss aus j vergroessert dessen spaetere Aufnahmefaehigkeit exakt um die
   bilanzierte abgegebene Menge.
4. Jeder gerichtete Kantenaustausch bleibt antisymmetrisch; Zielbegrenzung
   darf keine Masse vernichten oder nachtraeglich umverteilen.
5. Im Grenzbereich sehr geringer Belegung muss die neue Form auf den
   quellenbegrenzten K2/F3-Transport oder dessen konstant skalierte Form
   zurueckfallen.

Wenn diese Prognosen erst durch Observer, Clipping, Normalisierung oder eine
Phasenregel entstehen, gilt die Eigenschaft als nicht umgesetzt.

## Erwarteter funktionaler Unterschied

Zielseitige Verfuegbarkeit fuegt dem Transport eine gemeinsame Abhaengigkeit
von Quellmenge und Zielbelegung hinzu. Damit ist die Transportdynamik nicht
mehr generell eine lineare Funktion des M-Vektors. Lokale Verdichtung kann
den weiteren Zufluss selbst begrenzen; Abfluss kann dieselbe Kapazitaet
wieder oeffnen.

Das ermoeglicht den W7-C-Lebenszyklus nur. Es beweist ihn nicht. Insbesondere
muss ein spaeterer kontrollierter Vergleich erst zeigen, ob konkurrierende
Feldgeschichte eine alte Wirkung staerker verdraengt als eine gleich lange
passive Unterbrechung. Lauf 194 bleibt dafuer die negative K2/F3-Referenz.

## Pflichtbaselines

Eine spaetere Form muss bei gleichem Zustands-, Parameter-, Praezisions- und
Zeitbudget mindestens gegen folgende Arme bestehen:

| Kennung | Rolle |
| --- | --- |
| P0 | heutiger neutraler S/H-Pfad ohne aktiven Substrataustausch |
| K2/F3 | vorhandener quellenbegrenzter Transport |
| LIN | enge lineare gekoppelte Feldbaseline aus Lauf 192 |
| B3 | lokaler begrenzter Integrator ohne konservierten Transport |
| CONST-V | konstante statt zustandsabhaengige Zielverfuegbarkeit |
| ETA0 | gleicher Transport ohne M-nach-S-Rueckwirkung |
| SIGN | invertierte S-Transportrichtung |

`CONST-V` ist entscheidend: Falls eine konstante Skalierung des bisherigen
K2/F3-Pfads alle Effekte erklaert, wurde kein neuer Kapazitaetseffekt
isoliert.

## Harte Stopplinien

W7-E erteilt vor einer mathematischen Zulassungspruefung keine
Implementierungsfreigabe. Eine spaetere Form erhaelt `STOPP`, wenn:

- `C_site` nur als Clippinggrenze verwendet wird;
- M nach einem Schritt normalisiert oder auf freie Plaetze verteilt wird;
- Zielverfuegbarkeit aus Wiederholungszahl, Phase oder Ergebnis entsteht;
- getrennte Regeln fuer Bildung, Loesung und Wiederbeanspruchung gelten;
- eine volle Stelle trotz nichtnegativer gerichteter Zuflussrate weiter M
  aufnimmt;
- Masse, Nichtnegativitaet oder lokale Obergrenze nicht aus der Flussform
  selbst folgen;
- die Form algebraisch nur K2/F3 mit anderer konstanter Rate ist;
- der einzige Unterschied erst durch eine Memoryinterpretation entsteht.

## Abgrenzung zu S1-AB und H2

W7-E hebt deren Negativentscheid nicht auf. Zielseitige Verfuegbarkeit ist
weiterhin Standardmaterial- beziehungsweise Ausschlussphysik. Der neue Schritt
ist eine bewusst deklarierte Engineeringentscheidung, weil das Projekt ein
technisches Substrat aufbauen und pruefen will. Ein spaeterer positiver Befund
gilt nur fuer diese konstruierte gekoppelte Architektur.

## Entscheidung

```text
Ausgangstraeger:                    D1 / K2-F3-Engineeringbaseline
neue Eigenschaft:                  zielseitige freie Kapazitaet
zusaetzlicher gespeicherter State: nein
neue MCM-Substratnatur:            nein
konkreter Kapazitaetswert:         offen
konkrete Flussgleichung:           offen
Implementierung:                   nein
Forschungslauf:                    nein
Memory-, Feldzeit- oder KI-Claim:  nein
```

## Verwendete Projektquellen

- [W7-C Funktions- und Ressourcenvertrag](W7C_FUNKTIONS_UND_RESSOURCENVERTRAG_JENSEITS_LINEARER_SPUR.md)
- [W7-D Familienvergleich](W7D_STATISCHER_VERGLEICH_DREIER_SUBSTRATFAMILIEN.md)
- [Minimalvertrag der konservierten Feldgroesse M](MINIMALVERTRAG_KONSERVIERTE_BEGRENZTE_FELDGROESSE_M.md)
- [K2/F3 mathematischer Minimalvertrag](K2_MATHEMATISCHER_F3_MINIMALVERTRAG.md)
- [K2/F3 C/R-Implementierungsvertrag](K2_F3_SCHEIBE_B_CR_IMPLEMENTIERUNGSVERTRAG.md)
- [Lauf 192 Baselinevergleich](forschung/LAUF_192_K2_F3_E3_BASELINEVERGLEICH.md)
- [Lauf 194 Funktionsverlust und Wiederverwendung](forschung/LAUF_194_K2_B_F3_FUNKTIONSVERLUST_UND_WIEDERVERWENDUNG.md)
- [S1-AB Kopplungsmediumaudit](S1AB_AUDIT_ENDLICHES_LOKAL_UMVERTEILBARES_KOPPLUNGSMEDIUM.md)

## Bester naechster Schritt

W7-F formuliert den mathematischen Minimalvertrag fuer einen
kapazitaetsbegrenzten gerichteten Kantenaustausch. Er muss die fuenf direkten
Gegenprognosen, Massenbilanz, Invarianz von `0 <= M_i <= C_site`, den exakten
P0-Nullpfad und die Reduktion auf K2/F3 im Niedrigbelegungsgrenzfall statisch
beweisen. W7-F implementiert und testet noch nichts.
