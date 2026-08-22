# S1-US: Lokaler Kausal- und Lebenszyklusvertrag fuer LRD-E1

> **Abschlussstatus nach S1-UW:** Historische Vertragsstufe. Die diskrete
> K1/K2/K3-Fassung wurde bereits in S1-UT gestoppt; der gesamte LRD-E1-Zweig
> wurde anschliessend in S1-UV geschlossen und in S1-UW konsolidiert.

## Auftrag und Grenze

S1-US bindet ausschliesslich die lokale Ursache, Gegenwirkung,
Abschwaechung, Interferenz, Wiederbeanspruchung und den LRD-OFF-Nullfall des
in S1-UR ausgewaehlten Engineeringreferenzmodells LRD-E1.

Es werden keine Gleichung, Parameter, Intervallgrenzen, Implementierung,
Runtime, Matrix oder Feldlaeufe eingefuehrt.

## Kausaler Grundsatz

LRD-E1 darf nicht aus einem interpretierten Erfolg oder einer benannten
Rueckkehr lernen. Seine Disposition darf sich nur aus der lokal beobachtbaren
Fortsetzung des bestehenden Feldes entwickeln.

Die zulaessige Kausalkette lautet:

```text
reduzierter lokaler Weltkontakt
-> vorhandene lokale S/H-Feldlage
-> kontaktfreie lokale Feldfortsetzung
-> lokal beobachtbare Einpendel- oder Ueberschwingbewegung
-> spaetere Aenderung der privaten Rueckfuehrungsdisposition
-> Wirkung erst auf einen folgenden Feldschritt
```

Versuchsarm, Phase, Wiederholungszahl und spaetere Probe kommen in dieser
Kette nicht vor.

## Abgeschlossene lokale Eingangsrollen

Eine spaetere LRD-E1-Fortschreibung darf nur folgende abgeschlossene Rollen
lesen:

1. lokale `S`-Lage vor dem betrachteten Feldschritt;
2. lokale `S`-Lage nach dessen normaler Fortschreibung;
3. zugehoerigen lokalen `H`-Vorzustand nur als Pflichtkontrolle;
4. Anwesenheit oder Abwesenheit aktuellen lokalen Rezeptorkontakts;
5. feste Neutralreferenz und lokale Feldgeometrie;
6. abgeschlossenen privaten LRD-E1-Vorzustand;
7. reale Dauer des betrachteten Feldschritts.

Nachbarwerte sind nur zulaessig, soweit sie bereits an der normalen lokalen
Feldtransition beteiligt sind. Globale Normen, Armstatistiken, Observerwerte
und zukuenftige Feldlagen bleiben verboten.

## Drei inhaltsfreie lokale Ursachenklassen

### K1: Einpendelnde Rueckfuehrung

K1 liegt nur bei fehlendem lokalem Rezeptorkontakt vor, wenn die normale
Feldfortsetzung die lokale Auslenkung in Richtung der Neutralreferenz
verringert, ohne die Neutralreferenz im selben Schritt zu ueberschreiten.

K1 darf die spaetere lokale Rueckfuehrungsdisposition in Richtung staerkerer
Rueckwirkung verschieben. Die konkrete Staerke dieser Verschiebung bleibt
ungebunden.

K1 bezeichnet keinen Erfolg. Es ist nur eine lokale geometrische Beziehung
zwischen zwei abgeschlossenen Feldlagen.

### K2: Ueberschwingende Gegenwirkung

K2 liegt nur bei fehlendem lokalem Rezeptorkontakt vor, wenn die normale
Feldfortsetzung die Neutralreferenz ueberschreitet und die lokale Auslenkung
auf der Gegenseite fortsetzt oder vergroessert.

K2 muss einer zuvor verstaerkten Rueckfuehrungsdisposition entgegenwirken.
Damit kann dieselbe unveraenderte Naturform zu staerkerer oder schwaecherer
spaeterer Rueckwirkung fuehren, ohne einen Sollwert aus einer Auswertung zu
lesen.

Die spaetere mathematische Form muss numerisches Ueberschwingen von einer
tragenden Feldbewegung trennen. Gelingt diese Trennung nicht, ist K2 als
Ursache unzulaessig.

### K3: Feldnahe Ruhe

K3 liegt bei fehlendem lokalem Rezeptorkontakt und ausbleibender tragender K1-
oder K2-Wirkung vor. In K3 muss die lokale Disposition dissipativ in Richtung
ihrer Neutralreferenz zurueckkehren.

K3 ist keine Loeschphase. Dieselbe Dissipation gilt in jedem normalen
Feldschritt, in dem keine staerkere lokale Ursache entgegenwirkt.

## Verhalten bei aktuellem Rezeptorkontakt

Direkter Rezeptorkontakt darf die LRD-E1-Disposition nicht selbst
konfigurieren. Waehrend eines lokalen Kontakts:

- wirkt der bestehende Rezeptor- und Feldpfad unveraendert;
- wird kein K1- oder K2-Ereignis aus der erzwungenen Feldbewegung abgeleitet;
- darf nur die allgemeine, spaeter mathematisch gebundene Dissipation wirken,
  sofern dadurch der LRD-OFF-Nullfall nicht verletzt wird.

Damit bleibt LRD-E1 eine Disposition aus feldinterner Rueckfuehrung und wird
nicht zu einem Rezeptorintegrator.

## Atomare Kausalordnung

Ein Feldschritt darf keinen algebraischen Sofortruecklauf zwischen Feld und
Disposition enthalten. Die spaetere technische Reihenfolge muss sein:

```text
abgeschlossener Feld- und LRD-Vorzustand
-> normaler Feldfolgezustand unter der bisherigen Disposition
-> passive lokale Klassifikation K1, K2 oder K3
-> neuer privater LRD-Zustand
-> dessen Wirkung fruehestens im naechsten Feldschritt
```

Die Klassifikation ist Teil der lokalen Naturform und darf nicht aus
Observer- oder Ergebniscode stammen.

## Technischer Lebenszyklus

### Bildung

Wiederholte kausal erreichte K1-Fortsetzungen duerfen die lokale Disposition
begrenzt von ihrer Neutralreferenz wegbewegen. Kontaktinventar allein genuegt
nicht; entscheidend ist die anschliessende feldinterne Rueckfuehrung.

### Spaetere Feldwirkung

Die abgeschlossene Disposition muss bei einer spaeteren identischen
Fortsetzung die lokale `S`-Transition selbst beeinflussen. Eine Wirkung nur
auf Diagnose, Probe oder Ausgabe ist unzulaessig.

### Funktionale Abschwaechung

Unter K3-Fortsetzung muss die Disposition schrittweise zur Neutralreferenz
zurueckkehren. Die Abschwaechung darf keinen Timer, keine feste Loeschdauer
und keine Versuchsphasenkennung verwenden.

### Interferenz

Eine spaetere lokal erreichbare K2-Geschichte muss einer zuvor durch K1
gebildeten Disposition entgegenwirken. Interferenz bedeutet bei LRD-E1 nicht
die Konkurrenz gespeicherter Inhalte, sondern die Konkurrenz zweier
Feldgeschichten um denselben skalaren Rueckfuehrungsfaktor.

### Kapazitaetsfreigabe

LRD-E1 besitzt kein separates Ressourcenledger. Seine technische
Wiederverfuegbarkeit ist der dissipativ wiederhergestellte Abstand zur
endlichen Zustandsgrenze. Rueckkehr zur Neutralreferenz stellt den
unbelasteten lokalen Engineeringzustand wieder her.

### Wiederbeanspruchung

Nach Rueckkehr zur Neutralreferenz muss eine neue K1-Geschichte denselben
lokalen Zustand erneut veraendern koennen. Es darf kein Reset und kein neuer
Slot erzeugt werden.

## Reichweitengrenze

LRD-E1 besitzt genau einen skalaren Zustand pro teilnehmendem Feldort. Daraus
folgt eine bewusste Funktionsgrenze:

- gleichzeitig verschiedene Inhalte oder Pfade koennen nicht getrennt
  getragen werden;
- Interferenz ist nur als Veraenderung desselben lokalen Faktors darstellbar;
- raeumliche Differenzierung entsteht nur durch verschiedene Feldorte, nicht
  durch Objekt- oder Episodenadressen;
- eine spaetere breitere Memory-Funktion kann aus LRD-E1 nicht vorausgesetzt
  werden.

Diese Grenze verhindert, dass ein einfacher Gaintraeger nachtraeglich als
allgemeines Memorysystem interpretiert wird.

## Exakter LRD-OFF-Nullfall

`LRD-OFF` muss den heutigen produktiven Feldkern byte- und
fortschreibungsidentisch erhalten:

1. kein LRD-Zustand wird angelegt oder gelesen;
2. keine K1/K2/K3-Klassifikation wird ausgefuehrt;
3. keine Feldrate, kein Integratorschritt und kein Rezeptorpfad wird
   veraendert;
4. kein bestehendes Snapshot- oder `current_api`-Schema wird erweitert;
5. bestehende Digests und Regressionsergebnisse bleiben unveraendert;
6. ein privater spaeterer Adapter muss bei OFF direkt den bestehenden
   Feldschritt verwenden.

Ein neutral initialisiertes `LRD-ON` ist nicht mit `LRD-OFF` gleichzusetzen,
weil es waehrend der Geschichte eine Disposition entwickeln darf.

## Fail-closed-Regeln

Eine spaetere LRD-E1-Fortschreibung muss abbrechen, wenn:

- Vor- und Folgezustand nicht demselben Feldort und Feldschritt angehoeren;
- Rezeptorkontakt oder dessen Abwesenheit nicht eindeutig gebunden ist;
- Zeitordnung, Dauer oder Neutralreferenz ungueltig sind;
- die Disposition ausserhalb ihres spaeter gebundenen Bereichs liegt;
- K1 und K2 gleichzeitig klassifiziert werden;
- numerische Nichtendlichkeit oder ungebundene Bereichsprojektion auftritt;
- Diagnose- oder Observerdaten als Ursache angeboten werden.

Der Abbruch darf keinen Ersatzwert in Feld oder Disposition schreiben.

## Gegenbaselines und Abnahmen

Der Lebenszyklus muss spaeter mindestens gegen folgende Erklaerungen getrennt
werden:

- unveraendertes `S/H`-Feld bei LRD-OFF;
- Fixed Adapter mit staerkerer Rueckfuehrung;
- Rezeptorintegrator;
- eine Leaky-Spur aus lokaler `S`-Auslenkung;
- eine Leaky-Spur aus kontaktfreier Rueckfuehrungsbewegung;
- zustandsabhaengige Mobilitaet ohne K1/K2-Unterscheidung;
- F3 beziehungsweise eine gleich budgetierte Zweizustandsrekurrenz.

Da LRD-E1 offen zur Mobilitaets-/Gainklasse gehoert, pruefen diese Vergleiche
technischen Mehrwert, Stabilitaet und Kausalbindung, nicht eine bereits
behauptete neue Mechanikklasse.

## Stoppbedingungen

Die Linie wird vor Mathematik gestoppt, wenn:

1. K1, K2 und K3 nicht ausschliesslich aus zulaessigen lokalen Rollen
   entscheidbar sind;
2. K2 in normalen kontrollierten Feldgeschichten prinzipiell nicht erreichbar
   ist;
3. Abschwaechung und K1-Bildung nur durch getrennte Sonderphasen formulierbar
   sind;
4. die atomare Ein-Schritt-Verzoegerung die S1-UQ-Funktion unmoeglich macht;
5. ein LRD-OFF-Pfad nicht exakt auf den bestehenden Feldschritt reduziert;
6. die spaetere Gleichung Clipping als normale Begrenzungsdynamik benoetigt;
7. eine einzelne engere Leaky-Baseline denselben technischen Nutzen mit
   geringerem Zustand und gleicher Kausalgeschichte vollstaendig liefert.

## Claim-Sperren

S1-US bindet einen technischen Lebenszyklus eines adaptiven lokalen
Rueckfuehrungsfaktors. Daraus folgen keine Aussagen ueber eine vorhandene
technische MCM-Memory, Lernen, Wiedererkennen, Bedeutung, Wahrnehmung,
Selbstregulation, Bewusstsein oder KI.

## Verbindliche Entscheidung

```text
S1_US_LRD_E1_LOCAL_CAUSAL_LIFECYCLE_BOUND
S1_US_SETTLING_SUPPORT_OVERSHOOT_OPPOSITION_AND_QUIESCENT_DECAY_BOUND
S1_US_NO_DIRECT_RECEPTOR_CONFIGURATION
S1_US_ONE_STEP_CAUSAL_DELAY_REQUIRED
S1_US_LRD_OFF_EXACT_PRIMARY_FIELD_NULL_BOUND
S1_US_SCALAR_INTERFERENCE_AND_REUSE_LIMITS_EXPLICIT
S1_US_NO_EQUATION_NO_PARAMETERS_NO_RUNTIME_NO_EXECUTION
```

## Bester naechster Schritt

S1-UT darf ausschliesslich statisch pruefen, ob K1, K2 und K3 mit den
vorhandenen atomaren `SharedMCMField`-Schrittgrenzen, Rezeptorkontaktrollen und
lokalen `S/H`-Zustaenden ohne neue oeffentliche API und ohne Snapshotumbau
eindeutig berechenbar waeren. Noch keine Gleichung, Parameter,
Implementierung oder Ausfuehrung.

## Projektgrundlagen

- [S1-UR Anatomie- und Baselinekollisionsaudit](S1UR_LRD1_ANATOMIE_BEGRENZUNGS_UND_BASELINEKOLLISIONSAUDIT.md)
- [S1-UQ Funktions- und Falsifikationsvertrag](S1UQ_FUNKTIONS_UND_FALSIFIKATIONSVERTRAG_LOKALE_RUECKFUEHRUNGSDISPOSITION.md)
- [Funktionaler Anforderungsrang des technischen Memory-Lebenszyklus](FUNKTIONALER_ANFORDERUNGSRANG_MEMORY_LEBENSZYKLUS.md)
- [Korrekturvertrag zur digitalen Naturrekurrenz](KORREKTURVERTRAG_DIGITALE_NATURREKURRENZ.md)
